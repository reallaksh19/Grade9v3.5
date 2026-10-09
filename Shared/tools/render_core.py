#!/usr/bin/env python3
"""The one renderer for learner Core pages.

Renders the selected Core roles of a product from library records (schema 0.2.0) and a product
manifest; legacy manifests default to all six roles. It renders only through the role's blueprint slots
(Shared/web/interactive-page-blueprints.v1.json) and inside the tablet shell
(docs/specs/TABLET-SHELL-AND-NAVIGATION.md). Every block, figure stage, reveal, attempt
control and hint rung is marked with a data-g9-* attribute for advisory observation.

The renderer never writes academic text of its own. Everything the learner reads comes from a
record, and a missing required field is recorded as an advisory gap. Draft marking
describes the build; only the Owner decides whether an exact render is published.

Attempt controls ask an honest self-learner for a commitment before seeing a result.
They neither grade correctness nor prevent a determined reader from inspecting source.

Figures are mounted from authored SVG assets (representation.rendered_asset_refs). Each
reveal stage is a <g data-g9-stage-id="…">. There is no generated stand-in figure.

Usage:
    render_core.py build --manifest M.json --out DIR [--mode PAGES|EMBED|SINGLE_FILE] [--draft]
    render_core.py gaps --manifest M.json
"""
from __future__ import annotations

import argparse
import hashlib
import html
from html.parser import HTMLParser
import json
import re
import sys
import subprocess
from functools import lru_cache
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from urllib.parse import urlsplit, urljoin
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import core2_v2, learner_metadata, owner_bank, product_coverage, product_manifest, toughest_concept, learning_repair  # noqa: E402
from Shared.tools import web_blueprint_contract as blueprints_api  # noqa: E402

BLUEPRINTS = REPO / "Shared/web/interactive-page-blueprints.v1.json"
CONTRACT = REPO / "Shared/quality/learner-quality.v1.json"
TABLET_CSS = REPO / "public/css/tablet-12-7.css"
PACKAGE_SCHEMA = REPO / "Shared/library/package.schema.json"
BANK_SCHEMA = REPO / "Shared/library/competitive-exam-bank.schema.json"
CORE2_V2_SOURCE = Path(core2_v2.__file__).resolve()
LEARNER_METADATA_SOURCE = Path(learner_metadata.__file__).resolve()
LEARNER_METADATA_VOCABULARY = learner_metadata.VOCABULARY
PRODUCT_MANIFEST_SOURCE = Path(product_manifest.__file__).resolve()
ROLES = ["CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"]
ROLE_FILE = {r: r.lower() + ".html" for r in ROLES}
ROLE_TITLE = {"CORE1": "Orientation map", "CORE1A": "Construction", "CORE1B": "Reconstruction",
              "CORE2": "Source questions", "CORE2A": "Supported practice", "CORE2B": "Transfer"}
MODES = ("PAGES", "EMBED", "SINGLE_FILE")
RENDERER_VERSION = "render_core/2"
PROTECTION = {
    "PAGES": "inert-template-until-commitment",
    "EMBED": "inert-template-until-commitment",
    "SINGLE_FILE": "inert-template-until-commitment",
    "LEARNER_PDF": "protected-bytes-absent",
    "KEY_PDF": "all-payloads-materialised",
}


class RenderGapError(Exception):
    """Raised in strict mode when the product cannot be rendered without gaps."""


@dataclass
class Ctx:
    manifest: dict
    packages: list[dict]
    bank: list[dict]
    blueprints: dict
    selection_rows: dict[str, list[dict]] = field(default_factory=dict)
    authority_hashes: list[tuple[str, str]] = field(default_factory=list)
    gaps: list[dict] = field(default_factory=list)
    advisories: list[dict] = field(default_factory=list)
    waived: list[dict] = field(default_factory=list)
    held_to: str = "FLOOR"      # FLOOR: judge at each component's floor; REFERENCE: new authoring, judged at the reference depth
    figure_instances: dict[str, int] = field(default_factory=dict)
    source_items: dict[str, dict] = field(default_factory=dict)
    source_checks: dict[str, dict] = field(default_factory=dict)
    _toughest: list = field(default_factory=list, repr=False)

    def toughest(self) -> dict | None:
        """The toughest concept of the selected questions (see Shared/tools/toughest_concept.py), worked out once."""
        if not self._toughest:
            self._toughest.append(toughest_concept.derive(self.selection_rows.get("core2", []),
                                                          self.selection_rows.get("microtopics", [])))
        return self._toughest[0]

    def gap(self, duty: str, record: str, detail: str, role: str, component: str | None = None) -> None:
        row = {"duty": duty, "record": record, "detail": detail, "core": role,
               "product": self.manifest["product_id"]}
        if component:
            row["component"] = component
        self.gaps.append(row)

    def waive(self, component: str, record: str, reason: str, role: str) -> None:
        """An EXPECTED component its author declared not applicable, with the reason (kept; never silent)."""
        self.waived.append({"component": component, "record": record, "reason": reason, "core": role,
                            "product": self.manifest["product_id"]})

    def advise(self, component: str, record: str, detail: str, role: str) -> None:
        """What the blueprint expects a learner to see and the record does not supply: said, never a failure."""
        self.advisories.append({"component": component, "record": record, "detail": detail, "core": role,
                                "product": self.manifest["product_id"]})

    # record lookup across the manifest's packages
    def index(self, kind: str) -> dict:
        out = {}
        for p in self.packages:
            for r in p.get(kind, []):
                out[r["id"]] = r
        return out


def esc(value) -> str:
    return html.escape(str(value), quote=True)


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ figures

def asset_svg(ref: str) -> str | None:
    path = REPO / ref
    if not ref.endswith(".svg") or not path.is_file():
        return None
    text = path.read_text(encoding="utf-8")
    return text[text.find("<svg"):] if "<svg" in text else None


def _scope_svg_ids(svg: str, scope: str) -> str:
    """Namespace one inline SVG instance so repeated authored assets keep valid DOM identity."""
    id_attr = re.compile(r'(?<![-:\\w])id="([^"]+)"')
    ids = id_attr.findall(svg)
    if not ids:
        return svg
    mapping = {old: f"{scope}--{old}" for old in ids}
    out = svg
    for old, new in mapping.items():
        out = re.sub(
            rf'(?<![-:\\w])id="{re.escape(old)}"',
            f'id="{new}"',
            out,
        )
        out = out.replace(f'url(#{old})', f'url(#{new})')
        out = out.replace(f'href="#{old}"', f'href="#{new}"')
        out = out.replace(f"xlink:href=\"#{old}\"", f"xlink:href=\"#{new}\"")
    for attr in ("aria-labelledby", "aria-describedby"):
        pattern = re.compile(rf'{attr}="([^"]+)"')
        out = pattern.sub(
            lambda m: f'{attr}="' + " ".join(mapping.get(token, token) for token in m.group(1).split()) + '"',
            out,
        )
    return out


def _parsed_svg_stage_ids(svg: str) -> list[str]:
    """Validate a staged SVG and read its stage groups irrespective of attribute quoting.

    Refuse malformed markup, non-<g> stage markers and duplicate stage IDs.
    Rendering must never fall back to mounting an entire staged asset when a
    protected stage cannot be identified.
    """
    root = ET.fromstring(svg)
    if root.tag.rsplit("}", 1)[-1] != "svg":
        raise ValueError("staged asset root must be <svg>")
    ids: list[str] = []
    for element in root.iter():
        if "data-g9-stage-id" not in element.attrib:
            continue
        if element.tag.rsplit("}", 1)[-1] != "g":
            raise ValueError("stage marker must belong to a <g> group")
        stage_id = element.attrib["data-g9-stage-id"]
        if not stage_id or stage_id in ids:
            raise ValueError("empty or duplicated SVG stage ID")
        ids.append(stage_id)
    return ids


def _number(value: str | None, default: float | None = None) -> float | None:
    found = re.match(r"\s*(-?\d+(?:\.\d+)?)", value or "")
    return float(found.group(1)) if found else default


def _figure_text_findings(svg: str, column_px: float, minimum_px: float) -> list[str]:
    """What would make an authored figure's labels unreadable on the reference tablet.

    The figure fills its column, so its scale is the column's width over the viewBox's width; a label of `size` units renders at
    size x scale CSS pixels. A label whose estimated extent leaves the viewBox is cut off at the figure's edge."""
    head = re.search(r"<svg\b[^>]*>", svg, re.I)
    box = re.search(r'viewBox\s*=\s*"([^"]+)"', head.group(0)) if head else None
    numbers = re.findall(r"-?\d+(?:\.\d+)?", box.group(1)) if box else []
    if len(numbers) != 4 or float(numbers[2]) <= 0:
        return []
    left, width = float(numbers[0]), float(numbers[2])
    scale = column_px / width
    root_size = _number(re.search(r'font-size\s*=\s*"([^"]+)"', head.group(0)).group(1) if re.search(r'font-size\s*=\s*"([^"]+)"', head.group(0)) else None, 16.0)
    smallest: tuple[float, str] | None = None
    outside: list[str] = []
    for found in re.finditer(r"<text\b([^>]*)>(.*?)</text>", svg, re.S | re.I):
        attrs, inner = found.group(1), re.sub(r"<[^>]+>", "", found.group(2)).strip()
        if not inner:
            continue
        size_text = (re.search(r'font-size\s*=\s*"([^"]+)"', attrs) or re.search(r"font-size\s*:\s*([^;\"]+)", attrs))
        size = _number(size_text.group(1) if size_text else None, root_size)
        if size and (smallest is None or size < smallest[0]):
            smallest = (size, inner)
        x = _number((re.search(r'\sx\s*=\s*"([^"]+)"', attrs) or [None, None])[1])
        if x is None or not size:
            continue
        bold = bool(re.search(r'font-weight\s*[=:]\s*"?(bold|[6-9]00)', attrs, re.I))
        extent = len(inner) * size * (0.58 if bold else 0.52)
        anchor = (re.search(r'text-anchor\s*[=:]\s*"?(\w+)', attrs) or [None, "start"])[1]
        low = x - (extent if anchor == "end" else extent / 2 if anchor == "middle" else 0)
        high = low + extent
        if low < left - 4 or high > left + width + 4:
            outside.append(inner[:28])
    out: list[str] = []
    if smallest and smallest[0] * scale < minimum_px - 0.05:
        need = minimum_px / scale
        out.append(f"the smallest label ({smallest[1][:24]!r}, {smallest[0]:g} units) renders at {smallest[0] * scale:.1f} px on a "
                   f"12.7-inch tablet, under the {minimum_px:g} px floor: draw labels at least {need:.0f} units high in a viewBox "
                   f"no wider than {column_px / minimum_px * min(smallest[0], 99):.0f} units, or both")
    if outside:
        out.append(f"label(s) run outside the viewBox and are cut off at the figure's edge: {', '.join(repr(t) for t in outside[:3])}")
    return out


def _figure_column_px(ctx: Ctx, role: str) -> tuple[float, float] | None:
    """(the support column's usable width, the label floor) in CSS px on the blueprint's reference tablet, if it declares one."""
    bp = blueprint_of(ctx, role)
    policy = ((bp or {}).get("responsive_policy") or {})
    tablet = policy.get("tablet_12_7")
    if not tablet or not policy.get("support_fraction"):
        return None
    reference = tablet["reference_viewport"]["width"]
    inner = min(reference, 1380) - 108 - 22        # main and article padding, and the gap between the columns
    return policy["support_fraction"] * inner - 26, float(tablet["figure_min_text_css_px"])


def figure(ctx: Ctx, rep_id: str | None, stage: str, role: str, record: str, first_stage_only: bool = False,
           allowed: list[str] | None = None, instance_ref: str | None = None,
           owner_ref: str | None = None) -> str:
    """Mount a representation's authored SVG, or record the gap (never a stand-in)."""
    if not rep_id:
        return ""
    # An explicit empty list means no pre-solution stages are authorized.
    # Do not reinterpret it as the legacy "first stage" default.
    if allowed is not None and not allowed:
        return ""
    rep = ctx.index("representations").get(rep_id)
    source_resource = None
    if rep is None:
        source_resource = ctx.index("resources").get(rep_id)
        if source_resource:
            snapshot = source_resource.get("snapshot_ref")
            path = REPO / snapshot if snapshot else None
            expected = str(source_resource.get("snapshot_digest") or "").removeprefix("sha256:")
            if not path or not path.is_file() or not expected or _file_sha256(path) != expected:
                ctx.gap("MOUNT_REPRESENTATION", record, f"{rep_id}: source figure snapshot missing or digest differs", role)
                return ""
            rep = {"rendered_asset_refs": [snapshot], "kind": "SOURCE_FIGURE",
                   "purpose": source_resource.get("caption", "")}
    if rep is None:
        ctx.gap("MOUNT_REPRESENTATION", record, f"{rep_id} is not a representation in the product's packages", role)
        return ""
    case = None
    if instance_ref is not None:
        case = next((item for item in rep.get("scene_instances", []) if item["id"] == instance_ref), None)
        if (source_resource or rep.get("kind") == "SOURCE_FIGURE" or not case
                or case.get("question_ref") != (owner_ref or record)
                or role not in case.get("cores", []) or not case.get("asset_ref")):
            ctx.gap("MOUNT_REPRESENTATION", record, "selected case must bind this question, role and authored asset", role)
            return ""
        if not case.get("datum_refs") or any(ref not in ctx.index("data") for ref in case["datum_refs"]):
            ctx.gap("BUILD_SCENE", record, "selected case refers to absent data records", role)
            return ""
    assets = [case["asset_ref"]] if case else rep.get("rendered_asset_refs") or []
    svg = next((s for s in (asset_svg(a) for a in assets) if s), None)
    if svg is None:
        ctx.gap("BUILD_SCENE", rep_id, "no authored SVG asset (rendered_asset_refs) to mount", role)
        return ""
    opener = re.search(r"<svg\b[^>]*>", svg, re.I)
    named = bool(opener and re.search(r"\baria-(?:label|labelledby)=['\"][^'\"]+['\"]", opener.group(0), re.I))
    described = bool(re.search(r"<title\b[^>]*>.*?</title>", svg, re.I | re.S) and re.search(r"<desc\b[^>]*>.*?</desc>", svg, re.I | re.S))
    if not (named and described):
        ctx.gap("BUILD_SCENE", rep_id, "authored SVG lacks an accessible name and title/description pair", role)
        return ""
    column = _figure_column_px(ctx, role) if ctx.held_to == "REFERENCE" else None
    if column:
        for detail in _figure_text_findings(svg, *column):
            ctx.gap("AUTHOR_FIGURE_TEXT", rep_id, detail, role,
                    component="STAGED_VISUAL" if role == "CORE1A" else "REPRESENTATION")
    instance_base = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{role}-{record}-{rep_id}").strip("-")
    instance_no = ctx.figure_instances.get(instance_base, 0) + 1
    ctx.figure_instances[instance_base] = instance_no
    svg = _scope_svg_ids(svg, f"g9fig-{instance_base}-{instance_no}")
    # An SVG that actually declares stage markers is an access-control
    # boundary. Catalogue reveal_stages may include labels for different scene
    # assets or legacy unstaged figures; metadata alone must not reinterpret
    # a fully visible historical figure as an invalid staged asset.
    # Parse marked SVG as XML before deciding which stages exist.
    if stage == "PRE_ATTEMPT" and "data-g9-stage-id" in svg:
        try:
            stage_ids = _parsed_svg_stage_ids(svg)
        except (ET.ParseError, ValueError) as exc:
            ctx.gap("BUILD_SCENE", record, f"{rep_id}: unsafe staged SVG ({exc})", role)
            return ""
        # A representation's catalogued reveal stages can span multiple bound
        # scene assets; only the selected asset and explicit allowed IDs govern
        # this attempt. Never assume every catalogue stage is on every asset.
        if not stage_ids:
            ctx.gap("BUILD_SCENE", record, f"{rep_id}: staged asset has no parseable stage groups", role)
            return ""
    else:
        stage_ids = re.findall(r'data-g9-stage-id="([^"]+)"', svg)
    if allowed is not None and any(sid not in stage_ids for sid in allowed):
        ctx.gap("BUILD_SCENE", record, "authorized visual stage is absent from asset", role)
        return ""
    # Before an attempt only permitted stages show: the record's stage_refs, else the first stage.
    if stage == "PRE_ATTEMPT" and not allowed:
        first_stage_only = True
    shown = [s for s in stage_ids if s in allowed] if allowed else (stage_ids[:1] if first_stage_only else stage_ids)
    kind = rep.get("kind")
    controls = ""
    withheld = [s for s in stage_ids if s not in shown]
    labels = {st.get("id"): st.get("label") for st in rep.get("reveal_stages") or []}
    purposes = {st.get("id"): st.get("purpose") for st in rep.get("reveal_stages") or []}
    if len(shown) > 1:
        # Named chips jump to a stage and say what it adds (the stage's purpose, once the figure is no longer a pre-attempt one);
        # previous and next stay for keyboard and screen-reader use.
        chips = "".join(
            f'<button type="button" class="g9-stage-chip" data-g9-stage-goto="{n}"'
            + (f' data-g9-stage-desc="{esc(purposes[sid])}"' if stage != "PRE_ATTEMPT" and purposes.get(sid) else "")
            + f'>{n + 1}: {esc(labels.get(sid) or "Stage " + str(n + 1))}</button>'
            for n, sid in enumerate(shown))
        controls = ('<div class="g9-stage-controls"><div class="g9-stage-chips" role="group" aria-label="Stages">'
                    f'{chips}</div><p class="g9-stage-desc" data-g9-stage-desc-text></p>'
                    '<div class="g9-stage-stepper"><button type="button" data-g9-stage-step="prev">Previous stage</button>'
                    '<span data-g9-stage-label></span>'
                    '<button type="button" data-g9-stage-step="next">Next stage</button></div></div>')
    if stage == "PRE_ATTEMPT":
        # `purpose` is the illustrator's design note and often names the result ("so the double count is
        # diagnosed"). Before the attempt the caption is only the labels of the stages actually shown.
        caption = (f'<figcaption data-g9-block="stage_caption" data-g9-caption="stages">'
                   f'{esc("; ".join(labels[s] for s in shown if labels.get(s)))}</figcaption>')
    else:
        caption = (f'<figcaption data-g9-block="representation_bridge" data-g9-caption="purpose">'
                   f'{esc(case["scene"]["caption"] if case else rep.get("purpose", ""))}</figcaption>')
    if source_resource:
        caption = f'<figcaption data-g9-source-caption>{esc(source_resource.get("caption", ""))}</figcaption>'
    if withheld or (stage == "PRE_ATTEMPT" and stage_ids):
        # Even a single permitted stage can carry an answer-bearing root SVG
        # aria-label/title/desc. Scrub staged pre-attempt metadata whether or
        # not there are any groups to withhold.
        # A withheld stage is not in the page at all (hiding it with CSS still hands it to the DOM,
        # the hover tooltip and screen readers). The asset's own <title>/<desc> describe the whole
        # figure, so they go too; the accessible name is the shown stages' labels from the record.
        redacted = _without_stages(svg, set(withheld))
        if stage == "PRE_ATTEMPT":
            try:
                remaining = _parsed_svg_stage_ids(redacted)
            except (ET.ParseError, ValueError) as exc:
                ctx.gap("BUILD_SCENE", record, f"{rep_id}: stage redaction failed ({exc})", role)
                return ""
            if remaining != shown:
                ctx.gap("BUILD_SCENE", record, f"{rep_id}: protected SVG stage survived redaction", role)
                return ""
        svg = redacted
        svg = re.sub(r"<(title|desc)\b[^>]*>.*?</\1>", "", svg, flags=re.S)
        head = re.search(r"<svg\b[^>]*>", svg)
        if head:                                       # the name comes from the shown stages below
            clean = re.sub(
                r"""\s(?:role|aria-label|aria-labelledby|aria-describedby)\s*=\s*(["']).*?\1""",
                "", head.group(0), flags=re.I | re.S,
            )
            svg = svg[:head.start()] + clean + svg[head.end():]
        visible_name = "; ".join(labels[s] for s in shown if labels.get(s))
        # An author purpose may disclose the protected result (W). Never use it as
        # the pre-attempt accessible fallback, even after SVG title/desc removal.
        name = visible_name or ("Diagram showing the available stage" if stage == "PRE_ATTEMPT"
                                else rep.get("purpose", ""))
        svg = re.sub(r"<svg\b", f'<svg role="img" aria-label="{esc(name)}"', svg, count=1)
    stage_mode = str((rep.get("extensions") or {}).get("grade9v3:stage_mode") or "CUMULATIVE").upper()
    if stage_mode not in {"CUMULATIVE", "REPLACE"}:
        ctx.gap("AUTHOR_STAGE_MODE", rep_id,
                f"unsupported grade9v3:stage_mode {stage_mode!r}; use CUMULATIVE or REPLACE",
                role, component="STAGED_VISUAL" if role == "CORE1A" else "REPRESENTATION")
        stage_mode = "CUMULATIVE"
    mode_attr = f' data-g9-stage-mode="{stage_mode.lower()}"' if len(stage_ids) > 1 else ""
    bp = blueprint_of(ctx, role) or {}
    text_floor = ((bp.get('responsive_policy') or {}).get('tablet_12_7') or {}).get('figure_min_text_css_px',
                  ((ctx.blueprints.get('shell') or {}).get('typography_policy') or {}).get('minimum_learner_text_css_px',14))
    case_attrs = (f' data-g9-case-instance="{esc(case["id"])}"'
                  f' data-g9-case-owner="{esc(case["question_ref"])}"'
                  f' data-g9-case-data="{esc(" ".join(case["datum_refs"]))}"') if case else ""
    return (f'<figure data-g9-figure data-g9-fig="{esc(record)}-{esc(rep_id)}" data-g9-stage="{stage}"{case_attrs} '
            f'data-g9-representation="{esc(rep_id)}" data-g9-kind="{esc(kind)}" data-g9-min-figure-text="{esc(text_floor)}" data-reveal-stages="{max(len(shown), 1)}" '
            f'data-g9-stages-total="{max(len(stage_ids), 1)}" data-g9-stages="{esc(" ".join(shown))}"{mode_attr}>'
            f'<div class="g9-diagram-scroll" tabindex="0" role="region" aria-label="Diagram; scroll horizontally when enlarged">{svg}</div>{controls}{caption}</figure>')


def _without_stages(svg: str, withheld: set[str]) -> str:
    """Remove withheld <g> subtrees without serializing or changing other SVG bytes.

    The caller validates well-formed XML first and re-parses the result to
    confirm that exactly the authorized stage IDs remain. The tag scanner
    accepts either XML attribute quote style and nested <g> elements.
    """
    g_tag = re.compile(r"""</?g\b(?:[^'">]|"[^"]*"|'[^']*')*>""", re.I | re.S)
    stage_attribute = re.compile(r""" \bdata-g9-stage-id\s*=\s*(["'])(.*?)\1""".strip(), re.I | re.S)
    output: list[str] = []
    cursor = 0
    skip_depth = 0
    for match in g_tag.finditer(svg):
        tag = match.group(0)
        closing = tag.startswith("</")
        self_closing = tag.rstrip().endswith("/>")
        if skip_depth:
            if closing:
                skip_depth -= 1
            elif not self_closing:
                skip_depth += 1
            if skip_depth == 0:
                cursor = match.end()
            continue
        if closing:
            continue
        marker = stage_attribute.search(tag)
        if marker and html.unescape(marker.group(2)) in withheld:
            output.append(svg[cursor:match.start()])
            if self_closing:
                cursor = match.end()
            else:
                skip_depth = 1
    if skip_depth:
        return ""  # malformed containment; caller records a BUILD_SCENE gap
    output.append(svg[cursor:])
    return "".join(output)


# ------------------------------------------------------------------ small html helpers

def block(name: str, body: str, tag: str = "div", title: str | None = None) -> str:
    if not body:
        return ""
    head = f"<h4>{esc(title)}</h4>" if title else ""
    return f'<{tag} class="g9-block" data-g9-block="{name}">{head}{body}</{tag}>'


def para(text) -> str:
    return f"<p>{esc(text)}</p>" if text else ""


def secondary_disclosure(summary: str, body: str, kind: str) -> str:
    """Progressive disclosure for useful-but-secondary learner material; closed by default."""
    if not body:
        return ""
    return (f'<details class="g9-secondary-disclosure" data-g9-secondary="{esc(kind)}">'
            f'<summary>{esc(summary)}</summary><div class="g9-secondary-body">{body}</div></details>')


@lru_cache(maxsize=1024)
def _typed_math(tex: str, display: bool) -> str:
    """Use the pinned local KaTeX compiler to emit native, offline MathML.

    No browser CDN or inference from prose; stdin carries the declared data, not code.
    """
    script = ('const fs=require("fs");const k=require(process.argv[1]);'
              'const v=JSON.parse(fs.readFileSync(0,"utf8"));'
              'process.stdout.write(k.renderToString(v.tex,{displayMode:v.display,output:"mathml",'
              'throwOnError:true,trust:false,maxExpand:1000}));')
    result = subprocess.run(["node", "-e", script, str(REPO / "public/vendor/katex/0.16.8/katex.min.js")],
                            input=json.dumps({"tex": tex, "display": display}), text=True,
                            capture_output=True, encoding="utf-8", timeout=15)
    if result.returncode:
        raise ValueError("declared TeX could not be typeset")
    return result.stdout


def question_text(ctx: Ctx, q: dict, target: str, value, role="CORE2") -> str:
    text = str(value or "")
    spans = [s for s in (q.get("extensions") or {}).get("grade9v3:math_spans", []) if s["target"] == target]
    parts = []; cursor = 0
    # Positions are found in the source text, never in generated HTML.
    located = []
    for span in spans:
        literal = span["literal"]
        if literal not in text:
            if target == "conditions" and any(literal in c for c in q.get("conditions") or []):
                continue
            ctx.gap("AUTHOR_TYPED_MATH", q["id"], f"{target}: declared literal missing", role)
            continue
        located.extend((match.start(), span) for match in re.finditer(re.escape(literal), text))
    # Prefer a whole declared expression to a contained declared symbol (e.g.
    # sqrt(a^2-x^2) and x^2); both commonly occur in the same source sentence.
    located = [(start, span) for start, span in located if not any(
        other <= start and other + len(parent["literal"]) >= start + len(span["literal"])
        and len(parent["literal"]) > len(span["literal"]) for other, parent in located)]
    for start, span in sorted(located, key=lambda pair: pair[0]):
        if start < cursor:
            ctx.gap("AUTHOR_TYPED_MATH", q["id"], f"{target}: overlapping literals", role)
            continue
        parts.append(esc(text[cursor:start]))
        try:
            parts.append(_typed_math(span["tex"], span["display"]))
        except (ValueError, OSError, subprocess.TimeoutExpired):
            ctx.gap("AUTHOR_TYPED_MATH", q["id"], f"{target}: local typesetting unavailable or invalid", role)
            parts.append(esc(span["literal"]))
        cursor = start + len(span["literal"])
    parts.append(esc(text[cursor:]))
    return "".join(parts)


def items(values, ordered=False) -> str:
    values = [v for v in values or [] if v]
    if not values:
        return ""
    t = "ol" if ordered else "ul"
    return f"<{t}>" + "".join(f"<li>{esc(v)}</li>" for v in values) + f"</{t}>"


def slot(name: str, body: str, required: bool) -> str:
    return (f'<section class="blueprint-slot slot-{name}" data-blueprint-slot="{name}" '
            f'data-required="{"true" if required else "false"}">{body}</section>')


# ------------------------------------------------------------------ blueprint components
# A blueprint (Shared/web/interactive-page-blueprints.v1.json) names the components of a page, the slot each
# belongs to, how much it matters (REQUIRED, EXPECTED, OPTIONAL) and the column of each slot. The renderer
# realises exactly that: it wraps what it built as the component, reports a REQUIRED component that is absent or
# short as a gap that names the record to author, and reports an EXPECTED one as an advisory. It never
# writes the missing text itself.

_COMPONENT_NOUN = {"HINT_LADDER": "rungs", "SOLUTION_STEPS": "moves", "REPRESENTATION": "figures",
                   "CONSTRUCTION_STEPS": "steps", "STAGED_VISUAL": "stages", "TRAP_REPAIR": "wrong paths",
                   "QUICK_CHECK": "checks"}


def blueprint_of(ctx: Ctx, role: str) -> dict | None:
    return blueprints_api.blueprint_for_role(ctx.blueprints, role) if ctx.blueprints else None


def component(ctx: Ctx, role: str, cid: str, body: str, record: str, items: int | None = None,
              unit: str | None = None, band: str | None = None, waivers: dict | None = None) -> str:
    """Wrap `body` as the blueprint's component `cid`; with a blueprint that declares components, report its absence.

    `band` is the record's difficulty band, for components whose reference depth depends on it; `waivers` is what the
    record's author declared not applicable ({component id: reason}). Held to the FLOOR, a REQUIRED component below its
    floor is a gap and anything else short of the reference is an advisory; held to the REFERENCE (new authoring), every
    shortfall against the reference depth, and an EXPECTED component neither present nor waived, is a gap."""
    bp = blueprint_of(ctx, role)
    if bp is None or not bp.get("components"):
        return body
    spec = next((c for c in blueprints_api.components(bp) if c["id"] == cid), None)
    if spec is None:
        raise KeyError(f"{role}: {cid} is not a component of {bp['id']}")
    present = bool(body and body.strip())
    minimum = spec.get("min_items")
    target = blueprints_api.target_for(spec, band)
    noun = _COMPONENT_NOUN.get(cid, "items")
    count = items if items is not None else (1 if present else 0)
    strict = ctx.held_to == "REFERENCE"
    reason = (waivers or {}).get(cid)
    if not present and spec["level"] == "EXPECTED" and reason:
        ctx.waive(cid, record, reason, role)
        return (f'<span hidden data-g9-component-waiver="{cid}" data-g9-waiver-reason="{esc(reason)}"'
                + (f' data-g9-component-unit="{esc(unit)}"' if unit else "") + '></span>')
    below_floor = not present or (minimum is not None and count < minimum)
    below_reference = present and target is not None and items is not None and count < target
    if below_floor or below_reference:
        if below_floor:
            detail = f"{cid} is absent" if not present else f"{cid} has {count} of the {minimum} {noun} it needs"
        else:
            detail = f"{cid} has {count} of the {target} {noun} the reference page has" + (f" for a {band} question" if band else "")
        if spec["level"] == "REQUIRED" and below_floor or (strict and spec["level"] in {"REQUIRED", "EXPECTED"}):
            duty = spec.get("duty")
            if not (duty and any(g["duty"] == duty and g["record"] == record for g in ctx.gaps)):
                ctx.gap(duty or "AUTHOR_COMPONENT", record, detail, role, component=cid)
        elif spec["level"] in {"REQUIRED", "EXPECTED"}:
            ctx.advise(cid, record, detail, role)
    if not present:
        return ""
    attrs = (f'data-g9-component="{cid}" data-g9-level="{spec["level"]}" '
             f'data-g9-presentation="{spec["presentation"]}"')
    if items is not None:
        attrs += f' data-g9-component-items="{items}"'
    if unit:
        attrs += f' data-g9-component-unit="{esc(unit)}"'
    return f'<div class="g9-component g9-c-{spec["presentation"].lower().replace("_", "-")}" {attrs}>{body}</div>'


def component_body(ctx: Ctx, role: str, parts: dict[str, str], slot_id: str | None = None,
                   parent: str | None = None) -> str:
    """Component bodies in the order the blueprint lists them (`parts` keys are component ids)."""
    bp = blueprint_of(ctx, role)
    if bp is None or not bp.get("components"):
        return "".join(parts.values())
    order = [c["id"] for c in blueprints_api.components(bp)
             if c.get("parent") == parent and (slot_id is None or c["slot"] == slot_id)]
    unknown = sorted(set(parts) - set(order))
    if unknown:
        raise KeyError(f"{role}: {', '.join(unknown)} not declared in {slot_id or parent} of {bp['id']}")
    return "".join(parts.get(cid, "") for cid in order)


def compose(ctx: Ctx, role: str, bodies: dict[str, str]) -> str:
    """Slot sections in blueprint order, grouped by column.

    A FULL slot is a band across the page. PRIMARY and SUPPORT slots between two bands share one split: the
    primary column and the support column. Compact and medium widths stack them, primary first, in the same DOM.
    """
    bp = blueprint_of(ctx, role)
    if bp is None:
        return "".join(slot(name, body, True) for name, body in bodies.items())
    out: list[str] = []
    primary: list[str] = []
    support: list[str] = []
    support_filled = False

    def flush() -> None:
        nonlocal support_filled
        if primary or support:
            solo = "" if support_filled else " g9-split-primary-only"
            solo = solo if primary else " g9-split-support-only"
            cols = (f'<div class="g9-col g9-col-primary">{"".join(primary)}</div>' if primary else "")
            cols += (f'<div class="g9-col g9-col-support">{"".join(support)}</div>' if support else "")
            out.append(f'<div class="g9-split{solo}">{cols}</div>')
        primary.clear()
        support.clear()
        support_filled = False

    for row in bp["slots"]:
        if row["id"] not in bodies:
            continue
        section = slot(row["id"], bodies[row["id"]], bool(row["required"]))
        column = row.get("column") or "FULL"
        if column == "FULL":
            flush()
            out.append(section)
        elif column == "PRIMARY":
            primary.append(section)
        else:
            support.append(section)
            support_filled = support_filled or bool(bodies[row["id"]].strip())
    flush()
    return "".join(out)


def metadata_strip(ctx: Ctx, role: str, record: dict) -> str:
    """Render the safe projection, or turn incomplete canonical metadata into an explicit draft gap."""
    try:
        projection = learner_metadata.project(role, record, ctx.packages)
    except learner_metadata.LearnerMetadataError as exc:
        ctx.gap("AUTHOR_LEARNER_METADATA", record["id"], str(exc), role)
        return (
            f'<div data-g9-meta-strip data-g9-meta-role="{esc(role)}" '
            f'data-g9-meta-record="{esc(record["id"])}" data-g9-meta-incomplete="true"></div>'
        )
    field_labels = projection["field_labels"]
    chips = "".join(
        f'<span data-g9-meta-item data-g9-meta-kind="{esc(item["kind"])}" '
        f'data-g9-meta-ref="{esc(item["ref"])}" data-g9-meta-value="{esc(item["value"])}">'
        f'<strong>{esc(field_labels[item["kind"]])}:</strong> '
        f'<span data-g9-meta-label>{esc(item["label"])}</span></span>'
        for item in projection["items"]
    )
    return (
        f'<div data-g9-meta-strip data-g9-meta-role="{esc(role)}" '
        f'data-g9-meta-record="{esc(record["id"])}" data-g9-search-safe>{chips}</div>'
    )


def metadata_search_text(ctx: Ctx, role: str, record: dict) -> str:
    """Build the page-search corpus from the same explicit learner-safe metadata projection."""
    try:
        projection = learner_metadata.project(role, record, ctx.packages)
    except learner_metadata.LearnerMetadataError:
        return record.get("stem") or record.get("title") or ""
    return learner_metadata.safe_search_text(projection, record, role)


def reveal(summary: str, body: str, gated: bool = True, ref: str | None = None) -> str:
    if not body:
        return ""
    if not gated:
        return f'<details data-g9-reveal><summary>{esc(summary)}</summary>{body}</details>'
    payload_ref = ref or hashlib.sha256((summary + "\0" + body).encode("utf-8")).hexdigest()[:16]
    return (f'<details data-g9-reveal data-requires-attempt data-g9-payload-ref="{esc(payload_ref)}">'
            f'<summary>{esc(summary)}</summary><div data-g9-payload-slot></div></details>'
            f'<template data-g9-payload="{esc(payload_ref)}">{body}</template>')


RESPONSE_FROM_FORMAT = {
    "SINGLE_CORRECT": "single_choice", "MULTIPLE_CORRECT": "multiple_choice",
    "TRUE_FALSE": "true_false", "NUMERIC": "numeric", "SHORT": "short_text",
    "FILL_BLANK": "short_text", "LONG": "free_response", "HOTS": "free_response",
    "MATCH": "match", "ASSERTION_REASON": "single_choice",
    "COMPREHENSION": "free_response", "OTHER": "free_response",
}


def response_for(question: dict) -> dict:
    """Choose a commitment control from authored response or source format, without grading."""
    if question.get("response"):
        return question["response"]
    ext = question.get("extensions") or {}
    source_format = question.get("format") or ext.get("grade9v3:source_format")
    if source_format in RESPONSE_FROM_FORMAT:
        return {"type": RESPONSE_FROM_FORMAT[source_format]}
    if question.get("options") and (question.get("answer") or {}).get("kind") == "EXACT":
        return {"type": "single_choice"}
    if question.get("subparts"):
        return {"type": "multipart", "parts": question["subparts"]}
    if (question.get("answer") or {}).get("numeric"):
        return {"type": "numeric"}
    return {"type": "free_response"}


def source_projection(ctx: Ctx, question: dict) -> dict:
    """Project the pinned inventory and current independent check into Core2.

    The inventory describes the source item; a verified result supplies printed-key
    wording and its relation to the independently solved result. Neither changes
    the authored mathematical answer.
    """
    ref = (question.get("extensions") or {}).get("grade9v3:inventory_item")
    item = ctx.source_items.get(ref)
    if not item:
        return question
    projected = dict(question)
    projected["format"] = item["format"]
    answer = dict(question.get("answer") or {})
    key = dict(answer.get("source_key") or {})
    key.update({"state": item["key"]["state"]})
    if item["key"].get("card"):
        key["card"] = item["key"]["card"]
    else:
        key.pop("card", None)
        key.pop("value", None)
    check = ctx.source_checks.get(item["question_card"])
    if check and key["state"] == "PRESENT":
        key["value"] = check["official_answer"]
        answer["_independent_result"] = check["independent_answer"]
        answer["key_relation"] = "MATCHES_KEY" if check["agrees"] else "CONFLICTS_WITH_KEY"
    elif key["state"] != "PRESENT":
        answer["key_relation"] = "NO_KEY"
    else:
        answer.pop("key_relation", None)
    answer["source_key"] = key
    projected["answer"] = answer
    return projected


def attempt_box(label: str, response: dict | None = None, options: list | None = None,
                record: str = "", option_html: list[str] | None = None) -> str:
    """Ask an honest self-learner for a typed commitment, not a marked answer."""
    response = response or {"type": "free_response"}
    kind = response["type"]
    group = "g9-" + re.sub(r"[^A-Za-z0-9_-]+", "-", record or label)
    if kind in {"single_choice", "multiple_choice", "true_false"}:
        choices = list(options or (["True", "False"] if kind == "true_false" else []))
        input_type = "checkbox" if kind == "multiple_choice" else "radio"
        controls = "".join(
            f'<label class="g9-answer-option"><input data-g9-choice type="{input_type}" '
            f'name="{esc(group)}" value="{i}"><span>{option_html[i] if option_html is not None else esc(choice)}</span></label>'
            for i, choice in enumerate(choices)
        )
        controls = f'<div class="g9-answer-options" data-g9-block="options">{controls}</div>'
    elif kind == "numeric":
        controls = ('<label>Number<input data-g9-attempt data-g9-number type="text" inputmode="decimal" '
                    'autocomplete="off"></label><label>Unit<input data-g9-unit-input type="text" autocomplete="off"></label>')
    elif kind == "short_text":
        controls = f'<label>{esc(label)}<input data-g9-attempt type="text" autocomplete="off"></label>'
    elif kind == "multipart":
        parts = response.get("parts") or []
        controls = "".join(
            f'<fieldset data-g9-part><legend>{esc(part.get("label", f"Part {i + 1}") if isinstance(part, dict) else part)}</legend>'
            f'<input data-g9-attempt data-g9-part-input data-g9-part-type="{esc(part.get("type", "short_text") if isinstance(part, dict) else "short_text")}" '
            f'type="text" autocomplete="off"></fieldset>'
            for i, part in enumerate(parts)
        )
    elif kind == "match":
        right = response.get("match_right") or []
        controls = "".join(
            f'<label class="g9-match">{esc(left)}<select data-g9-match><option value="">Choose</option>'
            + "".join(f'<option value="{i}">{esc(value)}</option>' for i, value in enumerate(right))
            + '</select></label>'
            for left in response.get("match_left") or []
        )
    else:
        controls = f'<label>{esc(label)}<textarea data-g9-attempt rows="4"></textarea></label>'
    if kind in {"free_response", "multipart"} and response.get("paper_ok", True):
        controls += '<label class="g9-paper"><input data-g9-paper type="checkbox">I worked this on paper</label>'
    return (f'<div class="g9-attempt" data-g9-attempt-box data-g9-response-type="{esc(kind)}">{controls}'
            '<button type="button" data-g9-commit>I have attempted this</button></div>')


_MATHML_NS = "http://www.w3.org/1998/Math/MathML"
_MATHML_TAGS = {"math", "mrow", "mi", "mn", "mo", "msub", "msup", "mfrac", "mtext", "msqrt"}
_MATHML_ATTRS = {"display", "mathvariant"}
ET.register_namespace("", _MATHML_NS)


def _safe_mathml(value: str | None) -> str | None:
    """Return canonical restricted presentation MathML, or None if it is unsafe/malformed."""
    if not value:
        return None
    try:
        root = ET.fromstring(value)
    except ET.ParseError:
        return None
    for node in root.iter():
        if node.tag.startswith("{") and not node.tag.startswith("{" + _MATHML_NS + "}"):
            return None
        local = node.tag.split("}", 1)[-1]
        if local not in _MATHML_TAGS:
            return None
        node.tag = "{" + _MATHML_NS + "}" + local
        for attr in node.attrib:
            if attr.split("}", 1)[-1] not in _MATHML_ATTRS:
                return None
    if root.tag != "{" + _MATHML_NS + "}math":
        return None
    return ET.tostring(root, encoding="unicode", short_empty_elements=True)


def _relation_expression(ctx: Ctx, relation: dict, record: str, role: str = "CORE1") -> str:
    if relation.get("mathml"):
        mathml = _safe_mathml(relation["mathml"])
        if mathml is None:
            ctx.gap("AUTHOR_GOVERNING_RELATION", relation["id"],
                    "relation.mathml is malformed or outside the restricted presentation-MathML subset",
                    role)
        else:
            return f'<div class="g9-math" data-g9-math="mathml">{mathml}</div>'
    else:
        _typeset_finding(ctx, relation, role)
    return f'<p class="g9-expr">{esc(relation["expression"])}</p>'


def _typeset_finding(ctx: Ctx, relation: dict, role: str) -> None:
    """The blueprint's typeset rule: an equation a learner reads is presentation MathML; an expression alone is shown as plain text, and the build says so
    (an advisory at the floor, a gap at the reference)."""
    policy = ((ctx.blueprints or {}).get("component_policy") or {}).get("typeset")
    if not policy:
        return
    detail = (f"{relation['id']} has no presentation MathML (relation.mathml), so its equation is shown as plain text: "
              f"{str(relation.get('expression', ''))[:60]}")
    if policy["held_to"][ctx.held_to] == "GAP":
        ctx.gap(policy["duty"], relation["id"], detail, role, component=policy["component"])
    else:
        ctx.advise(policy["component"], relation["id"], detail, role)


def _coverage_findings(ctx: Ctx, roles: list[str]) -> None:
    """The blueprint's coverage rule (Shared/tools/product_coverage.py): what the library holds for the package is selected or omitted with a reason,
    and the hardest question is selected. An advisory at the floor, a gap at the reference."""
    policy = ((ctx.blueprints or {}).get("component_policy") or {}).get("coverage")
    if not policy:
        return
    for finding in product_coverage.findings(product_coverage.report(ctx.manifest, ctx.packages, ctx.bank), roles):
        if policy["held_to"][ctx.held_to] == "GAP":
            ctx.gap(policy["duty"], finding["record"], finding["detail"], finding["core"], component=policy["component"])
        else:
            ctx.advise(policy["component"], finding["record"], finding["detail"], finding["core"])


PURPOSE_DELIVERY_KEY = "grade9v3:purpose_delivery"


def _purpose_delivery_spec(ctx: Ctx) -> tuple[str, list[dict]]:
    """Return the manifest-selected purpose and authored delivery specs from package extensions."""
    purpose = str(ctx.manifest.get("purpose") or "").upper()
    if purpose not in {"REVISION", "COMPETITION"}:
        return purpose, []
    specs: list[dict] = []
    for package in ctx.packages:
        delivery = ((package.get("extensions") or {}).get(PURPOSE_DELIVERY_KEY) or {})
        spec = delivery.get(purpose)
        if isinstance(spec, dict):
            specs.append(spec)
    return purpose, specs


def _purpose_extension(ctx: Ctx, role: str, record_id: str) -> str:
    """Project a purpose-specific challenge beside the exact concept/question it extends."""
    purpose, specs = _purpose_delivery_spec(ctx)
    if not specs:
        return ""
    ref_key = "concept_refs" if role == "CORE1A" else "question_refs" if role == "CORE2" else None
    if ref_key is None:
        return ""
    rendered: list[str] = []
    for spec in specs:
        section_title = str(spec.get("section_title") or ("Next-level revision" if purpose == "REVISION" else "Competition transfer"))
        for item in spec.get("items") or []:
            if not isinstance(item, dict) or role not in (item.get("roles") or []):
                continue
            if record_id not in (item.get(ref_key) or []):
                continue
            item_id = str(item.get("id") or "")
            prompt = str(item.get("prompt") or "")
            if not item_id or not prompt:
                continue
            source_kind = str(item.get("source_kind") or "")
            source_label = str(item.get("source_label") or "")
            if source_kind == "AUTHOR_CREATED_COMPETITION_STYLE":
                provenance = source_label or "Original competition-style transfer; not a past-paper claim."
            elif source_kind == "VERIFIED_COMPETITIVE_SOURCE":
                provenance = source_label or "Verified competitive source"
            else:
                provenance = source_label or "Authored transfer"
            answer = item.get("answer") or {}
            answer_body = para(answer.get("summary")) + items(answer.get("reasoning"), True)
            response = item.get("response") if isinstance(item.get("response"), dict) else {"type": "free_response", "paper_ok": True}
            rendered.append(
                f'<section class="g9-purpose-extension" data-g9-purpose-delivery="{esc(purpose)}" '
                f'data-g9-purpose-item="{esc(item_id)}" data-g9-purpose-role="{esc(role)}">'
                f'<div class="g9-eyebrow">{esc(section_title)}</div>'
                f'<h3>{esc(item.get("title") or section_title)}</h3>'
                f'<p class="g9-purpose-source">{esc(provenance)}</p>'
                f'<div class="g9-purpose-prompt">{para(prompt)}</div>'
                + attempt_box("Your attempt", response, record=item_id)
                + reveal("Check your reasoning", answer_body, ref=f"PURPOSE-{item_id}-{role}")
                + '</section>'
            )
    return "".join(rendered)


# ------------------------------------------------------------------ roles

def _relations(ctx: Ctx, m: dict) -> list[dict]:
    rel = ctx.index("relations")
    return [rel[r] for r in m.get("relation_refs", []) if r in rel]


def _misconceptions(m: dict, unit: dict | None) -> list[dict]:
    rows = m.get("misconceptions") or []
    idx = (unit or {}).get("misconception_indexes")
    return [rows[i] for i in idx if i < len(rows)] if idx is not None else rows


_TEACHERS: dict | None = None


def teachers() -> dict:
    """capability id -> (subject, package path, microtopic id) across every library package."""
    global _TEACHERS
    if _TEACHERS is None:
        from Shared.tools.package_migrate import package_paths  # noqa: PLC0415
        _TEACHERS = {}
        for path in package_paths():
            pkg = load_json(path)
            mics = {x["primary_capability_ref"]: x["id"] for x in pkg.get("microtopics", [])}
            titles = {x["primary_capability_ref"]: x["title"] for x in pkg.get("microtopics", [])}
            for c in pkg.get("capabilities", []):
                row = (pkg["subject"], path.relative_to(REPO).as_posix(), mics.get(c["id"]), titles.get(c["id"]) or c.get("action"))
                _TEACHERS[c["id"]] = row
                _TEACHERS[f"{pkg['subject']}:{c['id']}"] = row
    return _TEACHERS



_BUCKETS: dict | None = None


def library_buckets() -> dict:
    """bucket id -> (subject, title) across canonical library packages."""
    global _BUCKETS
    if _BUCKETS is None:
        from Shared.tools.package_migrate import package_paths  # noqa: PLC0415
        _BUCKETS = {}
        for path in package_paths():
            pkg = load_json(path)
            for bucket in pkg.get("buckets", []):
                title = bucket.get("title") or bucket.get("topic")
                if title:
                    _BUCKETS[bucket["id"]] = (pkg["subject"], title)
    return _BUCKETS


def _core1a_route(ctx: Ctx) -> list[dict]:
    """Flatten selected canonical construction units into one deterministic Concept Book route."""
    route: list[dict] = []
    for microtopic in ctx.selection_rows.get("microtopics", []):
        units = microtopic.get("construction_units") or []
        if units:
            for index, unit in enumerate(units, 1):
                route.append({
                    "microtopic_id": microtopic["id"],
                    "microtopic_title": microtopic["title"],
                    "unit_id": unit["id"],
                    "label": unit.get("decision") or f"Construction {index}",
                })
        elif microtopic.get("teaching_path"):
            # Older canonical packages may own a complete teaching path without construction_units.
            # The concept id is already the stable canonical fragment; do not manufacture section identity.
            route.append({
                "microtopic_id": microtopic["id"],
                "microtopic_title": microtopic["title"],
                "unit_id": microtopic["id"],
                "label": microtopic["title"],
            })
    return route


def _core1a_foundation_route(ctx: Ctx, bucket: dict) -> str:
    """Render bucket prerequisites as orientation only; absence never blocks entry."""
    links = ctx.manifest.get("prerequisite_links", {})
    local = ctx.index("buckets")
    global_index = library_buckets()
    rows = []
    for ref in bucket.get("prerequisite_refs", []):
        title = None
        subject = None
        if ref in local:
            row = local[ref]
            title = row.get("title") or row.get("topic")
            subject = ctx.manifest.get("subject")
        elif ref in global_index:
            subject, title = global_index[ref]
        if not title:
            continue
        href = links.get(ref)
        label = f"{title} ({subject})" if subject and subject != ctx.manifest.get("subject") else title
        availability = "linked" if href else "unlinked"
        rows.append(
            f'<li data-g9-foundation-ref="{esc(ref)}" data-g9-availability="{availability}">'
            + (f'<a href="{esc(href)}">{esc(label)}</a>' if href
               else f'{esc(label)} <span class="g9-availability-note">— direct route unavailable in this product</span>')
            + "</li>"
        )
    return "<ul>" + "".join(rows) + "</ul>" if rows else ""


def _core1a_concept_route(microtopics: list[dict]) -> str:
    rows = []
    for microtopic in microtopics:
        units = microtopic.get("construction_units") or []
        sections = "".join(
            f'<li><a href="#{esc(unit["id"])}">{esc(unit.get("decision") or f"Construction {index}")}</a></li>'
            for index, unit in enumerate(units, 1)
        )
        nested = f"<ol>{sections}</ol>" if sections else ""
        rows.append(
            f'<li data-g9-concept-ref="{esc(microtopic["id"])}">'
            f'<a href="#{esc(microtopic["id"])}">{esc(microtopic["title"])}</a>{nested}</li>'
        )
    return "<ol>" + "".join(rows) + "</ol>" if rows else ""


def _core1a_bucket_orientation(ctx: Ctx) -> str:
    """Compose compact bucket orientation only from canonical bucket + selected concept records."""
    selected = ctx.selection_rows.get("microtopics", [])
    if not selected:
        return ""
    bucket_index = ctx.index("buckets")
    groups: dict[str, list[dict]] = {}
    for microtopic in selected:
        bucket_ref = microtopic.get("bucket_id")
        if bucket_ref and bucket_ref in bucket_index:
            groups.setdefault(bucket_ref, []).append(microtopic)

    rendered = []
    for bucket_ref, microtopics in groups.items():
        bucket = bucket_index[bucket_ref]
        scope = bucket.get("scope") or {}
        covers = scope.get("covers")
        promise = items(covers) if isinstance(covers, list) else para(covers)
        conventions = [
            row.get("statement") for row in bucket.get("conventions", [])
            if isinstance(row, dict) and row.get("statement")
        ]
        primary = (
            block("learning_promise", promise, title="Learning promise")
            + f'<nav class="g9-block" data-g9-block="concept_route" data-g9-concept-route '
              f'aria-label="Concept Book route"><h4>Concept route</h4>{_core1a_concept_route(microtopics)}</nav>'
        )
        exclusions = scope.get("excluded") or []
        companion = (
            block("foundation_route", _core1a_foundation_route(ctx, bucket), title="Foundation route")
            + block("model_contract", items(conventions), title="Model contract")
            + block("scope_boundary", items(exclusions), title="Outside this book")
        )
        rendered.append(
            f'<section class="g9-core1a-book" data-g9-bucket-orientation '
            f'data-g9-bucket-ref="{esc(bucket_ref)}">'
            f'<p class="g9-prov">Concept Book</p><h2>{esc(bucket.get("title") or bucket.get("topic") or "")}</h2>'
            f'<div class="g9-bucket-orientation-grid"><div>{primary}</div><aside>{companion}</aside></div>'
            f'</section>'
        )
    return secondary_disclosure("Contents and concept route", "".join(rendered), "core1a-contents")


def _core1a_section_route(m: dict) -> str:
    units = m.get("construction_units") or []
    if len(units) < 2:
        return ""          # one section has nowhere to route to: its own title is already the heading below
    links = "".join(
        f'<li><a href="#{esc(unit["id"])}">{esc(unit.get("decision") or f"Construction {index}")}</a></li>'
        for index, unit in enumerate(units, 1)
    )
    return f'<nav data-g9-section-route aria-label="Sections in this concept"><ol>{links}</ol></nav>'


def _core1a_unit_navigation(ctx: Ctx, unit_id: str) -> str:
    route = _core1a_route(ctx)
    index = next((i for i, row in enumerate(route) if row["unit_id"] == unit_id), None)
    if index is None:
        return ""
    previous = route[index - 1] if index > 0 else None
    following = route[index + 1] if index + 1 < len(route) else None
    links = []
    if previous:
        links.append(
            f'<a data-g9-prev-section href="#{esc(previous["unit_id"])}" '
            f'aria-label="Previous section: {esc(previous["label"])}">← Previous</a>'
        )
    if following:
        links.append(
            f'<a data-g9-next-section href="#{esc(following["unit_id"])}" '
            f'aria-label="Next section: {esc(following["label"])}">Next →</a>'
        )
    return (
        f'<nav class="g9-cu-nav" data-g9-unit-navigation aria-label="Concept Book section navigation">'
        f'<span data-g9-route-position>Section {index + 1} of {len(route)}</span>'
        f'<span class="g9-cu-nav-links">{"".join(links)}</span></nav>'
    )


def _unit_href(ctx: Ctx, role: str, record_id: str) -> str | None:
    """Link only to a unit actually projected into this packet."""
    key = "microtopics" if role in ("CORE1", "CORE1A", "CORE1B") else role.lower()
    if role in product_manifest.selected_output_roles(ctx.manifest) and record_id in (ctx.manifest.get("selection", {}).get(key) or []):
        return f"{ROLE_FILE[role]}#{record_id}"
    return None


def _prereqs(ctx: Ctx, m: dict) -> str:
    own = {x["primary_capability_ref"]: x["id"] for p in ctx.packages for x in p.get("microtopics", [])}
    own_titles = {x["primary_capability_ref"]: x["title"] for p in ctx.packages for x in p.get("microtopics", [])}
    links = ctx.manifest.get("prerequisite_links", {})
    rows = []
    for ref in m.get("prerequisite_refs", []):
        bare = ref.split(":", 1)[-1]
        taught = teachers().get(ref) or teachers().get(bare)
        caps = {c["id"]: c for p in ctx.packages for c in p.get("capabilities", [])}
        if bare in own:
            label = (caps.get(bare) or {}).get("action") or own_titles.get(bare, "")
            href = _unit_href(ctx, "CORE1A", own[bare])
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="true">'
                        + (f'<a href="{esc(href)}">{esc(label)}</a>' if href else esc(label)) + "</li>")
        elif taught:
            href = links.get(ref) or links.get(bare)
            label = f"{taught[3]} ({taught[0]})" if len(taught) > 3 and taught[3] else f"Taught in {taught[0]}"
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="true">'
                        + (f'<a href="{esc(href)}">{esc(label)}</a>' if href else esc(label)) + "</li>")
        else:
            ctx.gap("TEACH_PREREQUISITE_BRIDGE", m["id"], f"prerequisite {ref} is taught by no library", "CORE1A")
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="false">{esc(ref)}</li>')
    return "<ul>" + "".join(rows) + "</ul>" if rows else ""


def _concept_join(ctx: Ctx, role: str) -> dict[str, dict[str, list[str]]]:
    """Derive the selected Core1A↔Core2 graph; malformed authority fails as a typed render gap."""
    try:
        return core2_v2.concept_question_join(
            ctx.selection_rows.get("microtopics", []),
            ctx.selection_rows.get("core2", []),
        )
    except core2_v2.Core2ConceptJoinError as exc:
        ctx.gap("RESOLVE_CORE2_CONCEPT_JOIN", ctx.manifest["product_id"], str(exc), role)
        return {"question_to_microtopics": {}, "microtopic_to_questions": {}}


def _core1a_practice_navigation(ctx: Ctx, m: dict) -> str:
    """Generate exact Core2 practice links from the selected canonical capability graph."""
    join = _concept_join(ctx, "CORE1A")
    ids = join["microtopic_to_questions"].get(m["id"], [])
    if not ids:
        return ""
    questions = {q["id"]: q for q in ctx.selection_rows.get("core2", [])}
    rows = []
    for question_id in ids:
        question = questions.get(question_id)
        if not question:
            continue
        label = _identity(question) or question_id
        rows.append(
            f'<li><a data-g9-practice-link data-g9-question-ref="{esc(question_id)}" '
            f'data-g9-concept-ref="{esc(m["id"])}" href="core2.html#{esc(question_id)}">{esc(label)}</a></li>'
        )
    return block("practice_navigation", "<ul>" + "".join(rows) + "</ul>" if rows else "",
                 title="Practice this concept in Core2")


def _core1a_interactive_bridge(ctx: Ctx, m: dict) -> str:
    """Conditionally render contextual interactive bridge if an eligible explorer is registered for this concept."""
    concept_id = m.get("id")
    portal_root = _portal_root(ctx.manifest, "PAGES")
    if not concept_id or not portal_root:
        return ""
    try:
        from Shared.tools.resolve_concept_bundle import resolve_bundle
        registry_path = REPO / "public" / "data" / "resource-registry.v1.json"
        if not registry_path.exists():
            return ""
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)
        bundle = resolve_bundle(concept_id, registry)
        interactives = bundle.get("interactive", [])
        if not interactives:
            return ""
        cards = []
        for it in interactives:
            ep = it.get("entrypoint", "")
            title = it.get("title", "Interactive Explorer")
            rel_href = _portal_href(portal_root, ep)
            cards.append(
                f'<aside class="g9-interactive-bridge" data-g9-interactive-bridge>'
                f'<span class="g9-pill g9-pill-interactive">Try Visually</span>'
                f'<h3 class="g9-interactive-title">{esc(title)}</h3>'
                f'<p class="g9-interactive-desc">Explore this concept with interactive controls and real-time visual response.</p>'
                f'<a class="g9-bridge-link g9-action-interactive" data-g9-interactive-link href="{esc(rel_href)}" target="_blank" rel="noopener">'
                f'Try it visually &rarr;</a>'
                f'</aside>'
            )
        return "".join(cards)
    except Exception:
        return ""


def _core1a_learning_transitions(ctx: Ctx, m: dict) -> str:
    """Render derived transitions connecting Learn to Practice, Interactive, and Question Bank."""
    concept_id = m.get("id")
    portal_root = _portal_root(ctx.manifest, "PAGES")
    if not concept_id or not portal_root:
        return ""
    chips = []
    if "CORE2" in product_manifest.selected_output_roles(ctx.manifest):
        chips.append(
            f'<a class="g9-transition-chip g9-chip-practice" data-g9-transition="PRACTICE" href="core2.html">'
            f'Practice this concept &rarr;</a>'
        )
    qb_url = f"../../../question-bank/index.html?capability={esc(concept_id)}"
    chips.append(
        f'<a class="g9-transition-chip g9-chip-qb" data-g9-transition="QUESTION_BANK" href="{esc(qb_url)}">'
        f'All questions in Question Bank &rarr;</a>'
    )
    return block("learning_transitions", f'<div class="g9-transitions-row" data-g9-transitions>{"".join(chips)}</div>', title="Next steps")


def core1(ctx: Ctx, m: dict) -> str:
    rels = _relations(ctx, m)
    if not rels:
        ctx.gap("AUTHOR_GOVERNING_RELATION", m["id"], "no governing relation", "CORE1")
    anchor = m.get("compact_anchor")
    if not anchor:
        ctx.gap("AUTHOR_COMPACT_ANCHOR", m["id"], "no compact anchor", "CORE1")
    rel_html = "".join(f'<div class="g9-relation">{_relation_expression(ctx, r, m["id"])}{para(r.get("meaning"))}'
                       f'{items(r.get("conditions"))}</div>' for r in rels)
    # The compact anchor's own figure; the microtopic's first representation is often shared across the map.
    rep = (anchor or {}).get("representation_ref") or (m.get("representation_refs") or [None])[0]
    return compose(ctx, "CORE1", {
        "identity": block("scope", f"<h2>{esc(m['title'])}</h2>") + metadata_strip(ctx, "CORE1", m),
        "orientation": (block("hard_transition", para(m["inferential_jump"]), title="Hard transition")
                        + figure(ctx, rep, "TEACHING", "CORE1", m["id"])
                        + block("governing_relation", rel_html, title="Governing relation")
                        + block("compact_anchor", (para(anchor["prompt"]) + para(anchor["result"])) if anchor else "", title="Compact anchor")
                        + block("exit_prompt", para((m.get("exit_task") or {}).get("prompt")), title="Before you go on")),
    })


def _core1a_worked_anchor(question: dict, ctx: Ctx | None = None, owner: bool = False) -> str:
    """Render WATCH ONE from governed answer structure without inventing missing explanation.

    `owner` is a question of the product's bank worked through as the unit's example: it is shown as its owner wrote it,
    under its own identity and custody line."""
    answer = question.get("answer") or {}
    route = answer.get("reasoning_route") or []
    if route:
        steps = "".join(
            f'<li data-g9-watch-step data-g9-move-ref="{esc(row.get("id", index))}">'
            f'<div class="g9-worked-step-body"><strong>{esc(row.get("action", ""))}</strong>'
            f'{para("Why valid: " + row["why_valid"]) if row.get("why_valid") else ""}'
            f'{para("Result: " + row["output"]) if row.get("output") else ""}</div></li>'
            for index, row in enumerate(route, 1)
        )
        working = ('<p class="g9-worked-instruction">Follow the operation, its justification and its result.</p>'
                   f'<ol class="g9-watch-steps">{steps}</ol>')
    else:
        legacy = [str(step) for step in answer.get("reasoning") or [] if str(step).strip()]
        if legacy:
            steps = "".join(
                f'<li data-g9-watch-step>'
                f'<div class="g9-worked-step-body">{para(step)}</div></li>'
                for index, step in enumerate(legacy, 1)
            )
            working = ('<p class="g9-worked-instruction">Follow the operation, its justification and its result.</p>'
                       f'<ol class="g9-watch-steps">{steps}</ol>')
        else:
            working = ""
    stem = question.get("stem")
    head = (f'<p class="g9-prov" data-g9-anchor-source>{esc(_identity(question))} · {esc(_custody(question))}</p>'
            if owner else "")
    return (
        head
        + (f'<p class="g9-lines">{question_text(ctx, question, "stem", stem, "CORE1A")}</p>' if ctx and stem else para(stem))
        + working
        + block("worked_result", para(answer.get("summary")), title="Result")
        + block("worked_check", para(answer.get("check")), title="Check")
    )


def _core1a_question_bridge(ctx: Ctx, unit: dict, questions: list[dict], toughest: dict | None) -> str:
    """Say which source question a unit builds toward, and the move learners most often miss in it."""
    if not questions:
        return ""
    selected = "CORE2" in product_manifest.selected_output_roles(ctx.manifest)
    rows = []
    for question in questions:
        difficulty = (((question.get("extensions") or {}).get(toughest_concept.ANALYSIS_KEY) or {}).get("difficulty") or {})
        move = toughest_concept.crux_move(question) or {}
        hardest = bool(toughest and toughest["question_ref"] == question["id"])
        link = (f' <a class="g9-bridge-link" data-g9-practice-link data-g9-question-ref="{esc(question["id"])}" href="core2.html#{esc(question["id"])}">'
                f'Try it in Core2</a>') if selected else ""
        rows.append(
            f'<li data-g9-bridge-question="{esc(question["id"])}"><strong>{esc(toughest_concept.label_of(question))}</strong>'
            f'{" · " + esc(difficulty["band"]) if difficulty.get("band") else ""}'
            f'{" · the hardest question in this set" if hardest else ""}'
            f'{"<br>The move learners miss: " + esc(move["action"]) if move.get("action") else ""}{link}</li>')
    return block("question_bridge", "<ul>" + "".join(rows) + "</ul>", title="This unit builds toward")


def _core1a_relation_matrix(ctx: Ctx, m: dict, refs: list[str] | None = None) -> str:
    """Preserve governed equation/meaning/validity data as a semantic comparison table.

    `refs` limits it to the relations one construction unit names; without it, all the microtopic's relations."""
    relations = [r for r in _relations(ctx, m) if refs is None or r["id"] in refs]
    if not relations:
        return ""
    rows = []
    for relation in relations:
        validity = items(relation.get("conditions"))
        rows.append(
            f'<tr data-g9-relation-ref="{esc(relation["id"])}">'
            f'<td>{_relation_expression(ctx, relation, m["id"], "CORE1A")}</td>'
            f'<td>{para(relation.get("meaning"))}</td>'
            f'<td>{validity}</td></tr>'
        )
    return (
        '<div class="g9-table-scroll" data-g9-equation-matrix>'
        '<table><thead><tr><th scope="col">Equation</th>'
        '<th scope="col">What it tells you</th><th scope="col">When you can use it</th>'
        f'</tr></thead><tbody>{"".join(rows)}</tbody></table></div>'
    )


def _core1a_path_bridge(ctx: Ctx, m: dict, steps: dict[str, dict]) -> tuple[str, str]:
    """Render canonical teaching_path when no construction-unit wrapper exists.

    This is a presentation fallback over existing academic records, not a synthetic
    construction-unit or a new academic taxonomy.
    """
    ordered = [step for step in m.get("teaching_path", []) if step.get("id") in steps]
    if not ordered:
        return "", ""
    transform_count = sum(1 for step in ordered if step.get("role") == "TRANSFORM")
    derivation = transform_count >= 2 and bool(m.get("relation_refs"))
    attrs = (' data-g9-derivation-bridge="true"' if derivation else ' data-g9-path-construction="true"')
    rep = (m.get("representation_refs") or [None])[0]
    step_html = "".join(
        f'<li data-g9-step="{esc(step["id"])}">'
        f'<strong>{esc(step["action"])}</strong>'
        f'<br><em>Why valid:</em> {esc(step["why_valid"])}'
        f'<br><em>Result:</em> {esc(step["output"])}</li>'
        for step in ordered
    )
    primary = (
        f'<section class="g9-cu g9-path-bridge"{attrs}>'
        + _core1a_unit_navigation(ctx, m["id"])
        + block("construction", f"<ol>{step_html}</ol>")
        + figure(ctx, rep, "TEACHING", "CORE1A", m["id"])
        + block("equation_matrix", _core1a_relation_matrix(ctx, m), title="Equations and validity")
        + "</section>"
    )
    wrong = _misconceptions(m, None)
    trap = (
        block("wrong_path", items(row["wrong_idea"] for row in wrong), title="A tempting wrong path")
        + block("diagnose", items(row["diagnostic_prompt"] for row in wrong), title="Diagnose")
        + block("repair", items(row["repair"] for row in wrong), title="Repair")
    )
    trap_component = component(
        ctx, "CORE1A", "TRAP_REPAIR",
        secondary_disclosure("Mistake clinic · diagnose and repair", trap, "core1a-trap-repair"),
        m["id"], items=len(wrong), waivers=blueprints_api.waivers_of(m),
    )
    support = (
        f'<section class="g9-cu-support" data-g9-support-for="{esc(m["id"])}">'
        f'<h3>{esc(m["title"])}</h3>{trap_component}</section>'
        if trap_component else ""
    )
    return primary, support


_TRIAD_ROLE = {"CHECK": "Check", "APPLY": "Apply", "CONNECT": "Connect"}


def _quick_check(checks: list[dict]) -> str:
    """Render whichever intermediate checks are actually authored; role labels are optional metadata."""
    rows = "".join(
        f'<li data-g9-triad-role="{esc(c.get("role") or "")}"><span class="g9-triad-head">'
        f'{n} · {esc(_TRIAD_ROLE.get(c.get("role") or "", "Check"))}</span>'
        f'<span class="g9-triad-text">{esc(c["statement"])}</span></li>'
        for n, c in enumerate(checks, 1)
    )
    # Keep the legacy CSS hook for compatible styling; it no longer implies three items.
    return block("independent_check", f'<ol class="g9-triad">{rows}</ol>' if rows else "", title="Quick check")


def _stages_of(figure_html: str) -> int:
    found = re.search(r'data-g9-stages-total="(\d+)"', figure_html)
    return int(found.group(1)) if found else 0


def _draft_concept_checkpoint(ctx: Ctx, m: dict) -> str:
    """Optional neutral Core1A check for wholly authored TEST candidates only.

    This client-side formative check selects a concept *before* guided work.
    Its text match is not evidence of comprehension or independent mastery.
    """
    spec = (m.get("extensions") or {}).get("grade9v3:concept_checkpoint")
    if not spec:
        return ""
    if (ctx.manifest.get("subject") != "TEST" or spec.get("scope") != "TEST_AUTHORED_CORE1A_ONLY"
            or m.get("status") != "CANDIDATE"
            or spec.get("status") != "LOCAL_TEACHING_FORMAT_CHECK_NOT_INDEPENDENT_MASTERY"):
        ctx.gap("AUTHOR_CONCEPT_CHECKPOINT", m["id"],
                "neutral concept checkpoint is restricted to unadmitted TEST authoring", "CORE1A")
        return ""
    options = spec.get("choices") or []
    if (len(options) != 2 or {c.get("value") for c in options} != {"FACTOR", "ADD"}
            or spec.get("correct_value") != "FACTOR"):
        ctx.gap("AUTHOR_CONCEPT_CHECKPOINT", m["id"], "bad check choices", "CORE1A")
        return ""
    labels = "".join(
        f'<label><input type="radio" name="{esc(m["id"])}-concept" '
        f'data-g9-concept-option value="{esc(choice["value"])}"> '
        f'{esc(choice["label"])}</label> '
        for choice in options
    )
    return (
        f'<section class="g9-concept-first" data-g9-concept-check '
        f'data-g9-concept-ref="{esc(m["id"])}" '
        f'data-g9-concept-correct="{esc(spec["correct_value"])}" '
        f'data-g9-reason-words="{esc(",".join(spec["reason_contains_any"]))}" '
        f'data-g9-rule-words="{esc(",".join(spec["reason_contains_any_rule"]))}" '
        f'data-g9-feedback-choice="{esc(spec["on_wrong_choice"])}" '
        f'data-g9-feedback-explain="{esc(spec["on_wrong_explanation"])}" '
        f'data-g9-feedback-passed="{esc(spec["on_form_check"])}">'
        '<h4>Concept first · before the worked equation</h4>'
        f'<p>{esc(spec["neutral_demo"])}</p>'
        f'<fieldset><legend>{esc(spec["prompt"])}</legend>{labels}</fieldset>'
        '<label for="g9-concept-reason">Explain why in your own words</label>'
        '<textarea id="g9-concept-reason" data-g9-concept-reason rows="3" '
        'placeholder="Describe the index law and why it multiplies."></textarea>'
        '<button type="button" data-g9-concept-commit>Check concept, then see guided work</button>'
        '<p data-g9-concept-feedback role="status" aria-live="polite">'
        'Choose a relationship and explain the exponent rule before continuing.</p>'
        '<p>Formative teaching self-check only; this is not independent mastery evidence.</p>'
        '</section>'
    )


def core1a(ctx: Ctx, m: dict) -> str:
    units = m.get("construction_units") or []
    if not units:
        ctx.gap("AUTHOR_CONSTRUCTION_UNITS", m["id"], "no construction units", "CORE1A")
    steps = {s["id"]: s for s in m.get("teaching_path", [])}
    questions = ctx.index("questions")
    exit_task = m.get("exit_task") or {}

    waivers = blueprints_api.waivers_of(m)
    toughest = ctx.toughest() if ctx.held_to == "REFERENCE" else None

    def part(cid: str, body: str, record: str = m["id"], items: int | None = None, unit: str | None = None) -> str:
        return component(ctx, "CORE1A", cid, body, record, items=items, unit=unit, waivers=waivers)

    identity = component_body(ctx, "CORE1A", {
        "CONCEPT_HEADER": part("CONCEPT_HEADER", f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1A", m)),
        "SECTION_ROUTE": part("SECTION_ROUTE", secondary_disclosure("Sections", _core1a_section_route(m), "core1a-section-route")),
    }, "identity")

    def opening() -> dict[str, str]:
        """Current conditions precede construction; its key insight follows the visual."""
        return {
            "KEY_STEP": part("KEY_STEP", block("inferential_jump", para(m["inferential_jump"]), title="The key step")),
            "MODEL_CONTRACT": part("MODEL_CONTRACT",
                block("entry_assumptions", items(m.get("entry_assumptions")), title="Conditions for this construction")
                + secondary_disclosure("Prerequisite reference", _prereqs(ctx, m), "core1a-prerequisites")),
        }
    closure = component_body(ctx, "CORE1A", {
        "EXIT_RECALL": part("EXIT_RECALL", (
            block("exit_task", para(exit_task.get("prompt")), title="Now you do one")
            + attempt_box("Your answer", record=m["id"])
            + reveal("Model answer",
                     block("exit_answer",
                           para((exit_task.get("answer") or {}).get("summary"))
                           + items((exit_task.get("answer") or {}).get("reasoning"), True)),
                     ref=f'CORE1A-{m["id"]}-exit'))),
        "PRACTICE_LINKS": part("PRACTICE_LINKS", _core1a_practice_navigation(ctx, m)),
        "INTERACTIVE_BRIDGE": part("INTERACTIVE_BRIDGE", _core1a_interactive_bridge(ctx, m)),
        "LEARNING_TRANSITIONS": part("LEARNING_TRANSITIONS", _core1a_learning_transitions(ctx, m)),
    }, "repair_closure")
    closing = compose(ctx, "CORE1A", {"repair_closure": closure})
    head = compose(ctx, "CORE1A", {"identity": identity})

    if not units:
        if toughest and m["id"] == toughest["microtopic_ref"]:
            _toughest_unit_gaps(ctx, m, units, toughest)
        primary, support = _core1a_path_bridge(ctx, m, steps)
        opened = opening()
        return (head + compose(ctx, "CORE1A", {
            "construction": opened["KEY_STEP"] + opened["MODEL_CONTRACT"] + primary,
            "repair_closure": support + closure,
        }) + _purpose_extension(ctx, "CORE1A", m["id"]))

    rows = ""
    bank_questions = [q for q in ctx.bank if isinstance(q, dict) and q.get("id")]
    bank_by_id = {q["id"]: q for q in bank_questions}
    try:       # the concept's difficulty, as the metadata strip already projects it
        concept_difficulty = next(item["label"] for item in learner_metadata.project("CORE1A", m, ctx.packages)["items"]
                                  if item["kind"] == "concept-difficulty")
    except (learner_metadata.LearnerMetadataError, StopIteration):
        concept_difficulty = ""
    difficulty_pill = f'<span class="g9-pill g9-pill-concept">{esc(concept_difficulty)}</span>' if concept_difficulty else ""
    for n, u in enumerate(units):
        decision = "" if u.get("decision_from") == "inferential_jump" else u.get("decision", "")
        step_items = [steps[sid] for sid in u["step_refs"] if sid in steps]
        crux_step = u.get("crux_step_ref") if u.get("crux_question_refs") else None
        step_html = "".join(
            f'<li data-g9-step="{esc(step["id"])}"{" data-g9-crux-step" if step["id"] == crux_step else ""}>'
            + ('<span class="g9-crux-tag">The step the hard question turns on</span>' if step["id"] == crux_step else "")
            + f'<strong>{esc(step["action"])}</strong>'
            f'<br><em>Why valid:</em> {esc(step["why_valid"])}'
            f'<br><em>Result:</em> {esc(step["output"])}</li>'
            for step in step_items
        )
        novel_anchor = ((m.get("extensions") or {}).get("grade9v3:lesson_anchors") or {}).get(u["id"])
        bank_ref = u.get("bank_anchor_ref")
        if novel_anchor is not None:
            errors = learning_repair.anchor_problems(novel_anchor, bank_by_id, u['id'])
            for error in errors:
                ctx.gap('AUTHOR_WORKED_ANCHOR', u['id'], error, 'CORE1A', component='WORKED_EXAMPLE')
            anchor_html = _core1a_worked_anchor(novel_anchor) if not errors else ''
        elif bank_ref:
            anchor_q = bank_by_id.get(bank_ref)
            if not anchor_q:
                ctx.gap("AUTHOR_WORKED_ANCHOR", u["id"], f"bank_anchor_ref {bank_ref} is not a question of this product's bank "
                        f"({', '.join(sorted(bank_by_id)[:4])}...)", "CORE1A", component="WORKED_EXAMPLE")
            anchor_html = _core1a_worked_anchor(anchor_q, ctx, owner=True) if anchor_q else ""
        else:
            worked_ref = u.get("worked_anchor_ref")
            anchor_q = questions.get(worked_ref) if worked_ref else None
            if worked_ref and not anchor_q:
                ctx.gap(
                    "AUTHOR_WORKED_ANCHOR", u["id"],
                    f"worked_anchor_ref {worked_ref} does not resolve to a question",
                    "CORE1A", component="WORKED_EXAMPLE",
                )
            anchor_html = _core1a_worked_anchor(anchor_q) if anchor_q else ""
        crux_refs = [ref for ref in u.get("crux_question_refs") or [] if isinstance(ref, str)]
        crux_questions = [bank_by_id[ref] for ref in crux_refs if ref in bank_by_id]
        for ref in crux_refs:
            if ref not in bank_by_id:
                ctx.gap("AUTHOR_QUESTION_BRIDGE", u["id"], f"crux_question_refs names {ref}, which is not a question of this "
                        "product's bank", "CORE1A", component="QUESTION_BRIDGE")
        unit_band = toughest_concept.crux_band(u, crux_questions)   # the reference depth of the hardest question it builds toward
        if crux_questions and u.get("crux_step_ref") not in (u.get("step_refs") or []):
            ctx.gap("AUTHOR_QUESTION_BRIDGE", u["id"],
                    "this unit builds toward " + ", ".join(toughest_concept.label_of(q) for q in crux_questions)
                    + ": set crux_step_ref to the one of its step_refs that builds the move the question turns on", "CORE1A",
                    component="QUESTION_BRIDGE")
        check_rows = [c for c in u.get("independent_checks") or [] if c.get("statement")]
        checks = [c["statement"] for c in check_rows]
        wrong = _misconceptions(m, u)
        title = decision or (f"Construction step {n + 1} of {len(units)}" if len(units) > 1 else "Construction")
        unit_head = (f'<div class="g9-unit-head"><span class="g9-unit-no" aria-hidden="true">{n + 1}</span>'
                     f'<h3>{esc(title)}</h3>{difficulty_pill}</div>'
                     + _core1a_unit_navigation(ctx, u["id"]))
        # A unit that names its relations shows its own equation card; otherwise only the first unit shows the microtopic's.
        unit_relations = u.get("relation_refs")
        relation_matrix = (_core1a_relation_matrix(ctx, m, unit_relations) if unit_relations is not None
                           else (_core1a_relation_matrix(ctx, m) if n == 0 else ""))

        unit_waivers = {**waivers, **blueprints_api.waivers_of(u)}

        def unit_part(cid: str, body: str, items: int | None = None, band: str | None = None) -> str:
            return component(
                ctx, "CORE1A", cid, body, u["id"], items=items, unit=u["id"],
                band=band, waivers=unit_waivers,
            )

        figure_html = figure(ctx, u.get("representation_ref"), "TEACHING", "CORE1A", u["id"])
        probes = [r for r in (m.get('extensions') or {}).get('grade9v3:question_repairs', [])
                  if r.get('construction_ref') == u['id'] and r.get('interaction') == 'MODEL_SCOPE_PROBE']
        primary_probe = ''
        if probes:
            row = next((r for r in probes if novel_anchor and r['question_ref'] == novel_anchor.get('target_question_ref')), probes[0])
            question = bank_by_id.get(row.get('question_ref')) or (
                questions.get(row.get('question_ref'))
                if u.get('worked_anchor_ref') == row.get('question_ref') else None)
            valid = question and row == (question.get('extensions') or {}).get(learning_repair.KEY) and not learning_repair.problems(question, {u['id']})
            if valid:
                primary_probe = learning_repair.alignment_probe('construction-' + u['id'])
            else:
                ctx.gap('AUTHOR_LEARNING_REPAIR', u['id'], 'construction probe does not bind this question and crux', 'CORE1A')

        # Construction, its adjacent visual and then the insight follow the active blueprint order.
        card_parts = {
            "UNIT_HEADER": unit_part("UNIT_HEADER", unit_head),
            **(opening() if n == 0 else {}),
            "QUESTION_BRIDGE": unit_part("QUESTION_BRIDGE", secondary_disclosure(
                "Why this section matters for the question set",
                _core1a_question_bridge(ctx, u, crux_questions, ctx.toughest()),
                "core1a-question-bridge",
            )),
            "CONSTRUCTION_STEPS": unit_part("CONSTRUCTION_STEPS",
                                            block("construction", f"<ol>{step_html}</ol>" if step_html else ""),
                                            items=len(step_items), band=unit_band),
            "EQUATIONS": unit_part("EQUATIONS", secondary_disclosure(
                "Formula reference · meaning and conditions",
                block("equation_matrix", relation_matrix, title="Equations and validity"),
                "core1a-equations",
            )),
            "STAGED_VISUAL": unit_part("STAGED_VISUAL", figure_html, items=_stages_of(figure_html), band=unit_band),
            "MODEL_SCOPE_PROBE": unit_part("MODEL_SCOPE_PROBE", primary_probe),
            "WORKED_EXAMPLE": unit_part("WORKED_EXAMPLE", block("worked_anchor", anchor_html, title="Worked explanation")),
        }
        card = component_body(ctx, "CORE1A", card_parts, "construction")
        checkpoint = _draft_concept_checkpoint(ctx, m) if n == 0 else ""
        construction = (f'<section id="{esc(u["id"])}" class="g9-cu" data-g9-cu="{esc(u["id"])}">'
                        + checkpoint
                        + (f'<div data-g9-concept-target hidden>{card}</div>' if checkpoint else card)
                        + '</section>')
        support_label = decision or f"Construction {n + 1}"
        trap = (block("wrong_path", items(row["wrong_idea"] for row in wrong), title="A tempting wrong path")
                + block("diagnose", items(row["diagnostic_prompt"] for row in wrong), title="Diagnose")
                + block("repair", items(row["repair"] for row in wrong), title="Repair"))
        support_body = component_body(ctx, "CORE1A", {
            "TRAP_REPAIR": unit_part("TRAP_REPAIR", secondary_disclosure(
                "Mistake clinic · diagnose and repair",
                trap,
                "core1a-trap-repair",
            ), items=len(wrong)),
            "QUICK_CHECK": unit_part("QUICK_CHECK", _quick_check(check_rows), items=len(checks)),
        }, "repair_closure")
        support = (
            f'<section class="g9-cu-support" data-g9-support-for="{esc(u["id"])}">'
            f"<h3>{esc(support_label)}</h3>{support_body}</section>"
            if support_body else ""
        )
        rows += compose(ctx, "CORE1A", {
            "construction": construction,
            **({"repair_closure": (f'<div data-g9-concept-target hidden>{support}</div>'
                                    if checkpoint else support)} if support else {}),
        })

    if toughest and m["id"] == toughest["microtopic_ref"]:
        _toughest_unit_gaps(ctx, m, units, toughest)
    repair_rows = (m.get("extensions") or {}).get("grade9v3:question_repairs") or []
    return_hrefs = {}
    for repair_row in repair_rows:
        ref = repair_row['question_ref']
        href = next((_unit_href(ctx, role, ref) for role in ('CORE2', 'CORE2A', 'CORE2B')
                     if _unit_href(ctx, role, ref)), None)
        return_hrefs[ref] = href or ('#' + repair_row['construction_ref'])
    clinics = secondary_disclosure("Question-specific diagnosis and repair", learning_repair.clinic(repair_rows, return_hrefs), "core1a-question-repair") if repair_rows else ""
    if _draft_concept_checkpoint(ctx, m):
        clinics = f'<div data-g9-concept-target hidden>{clinics}</div>'
        closing = f'<div data-g9-concept-target hidden>{closing}</div>'
    return head + rows + clinics + _purpose_extension(ctx, "CORE1A", m["id"]) + closing


def _toughest_unit_gaps(ctx: Ctx, m: dict, units: list[dict], toughest: dict) -> None:
    """Require the toughest target to bind to the construction that teaches its decisive move.

    The source question itself does not have to become the worked example. The ordinary
    Core1A unit validation separately checks that a bound crux_step_ref belongs to the
    unit's teaching path.
    """
    ref, label = toughest["question_ref"], toughest["label"]
    move = (toughest.get("crux_move") or {}).get("action")
    why = (
        f"{label} is the toughest question in this set ({toughest['band']}, {toughest['score']}/10, "
        f"{toughest['conceptual']}/4 conceptual) and belongs to this concept"
    )
    builders = [u for u in units if ref in (u.get("crux_question_refs") or [])]
    if not builders:
        ctx.gap(
            "AUTHOR_TOUGHEST_CONCEPT", m["id"],
            f"{why}, but no construction unit builds toward it: name {ref} in crux_question_refs on the unit whose steps lead to "
            + (f"the move a learner misses ({move!r})" if move else "the move the question turns on"),
            "CORE1A", component="QUESTION_BRIDGE",
        )
        return

    # The extra worked-target admission is a REFERENCE authoring obligation,
    # not a new FLOOR rule for already governed canonical products. The
    # blueprint itself keeps WORKED_EXAMPLE EXPECTED, never unwaivably REQUIRED.
    if ctx.held_to != "REFERENCE":
        return

    authored = ((m.get("extensions") or {}).get("grade9v3:lesson_anchors") or {})
    bank_by_id = {q["id"]: q for q in ctx.bank if isinstance(q, dict) and q.get("id")}
    for unit in builders:
        novel_anchor = authored.get(unit["id"])
        # An author may explicitly waive an inapplicable worked panel at the
        # recovered blueprint's EXPECTED level; a bare missing panel is not a
        # waiver. An actual authored anchor still needs its exact crux binding.
        if (novel_anchor is None and not unit.get("bank_anchor_ref")
                and not unit.get("worked_anchor_ref")
                and blueprints_api.waivers_of(unit).get("WORKED_EXAMPLE")):
            continue
        if novel_anchor is not None:
            problems = learning_repair.anchor_problems(
                novel_anchor, bank_by_id, unit["id"], expected_ref=ref)
            answer = novel_anchor.get("answer") if isinstance(novel_anchor, dict) else {}
            answer = answer if isinstance(answer, dict) else {}
            reasoning = answer.get("reasoning_route") or answer.get("reasoning") or []
            if not isinstance(reasoning, list) or not any(
                    (isinstance(step, str) and step.strip())
                    or (isinstance(step, dict) and step.get("action") and step.get("why_valid"))
                    for step in reasoning):
                problems.append("lesson anchor has no worked reasoning with a justified move")
            if problems:
                ctx.gap("AUTHOR_TOUGHEST_CONCEPT", unit["id"],
                        f"{why}, but the separate worked example is not bound to the real target crux: "
                        + "; ".join(problems), "CORE1A", component="WORKED_EXAMPLE")
        elif unit.get("bank_anchor_ref") == ref:
            continue  # The traditional question-as-worked-example path.
        elif unit.get("bank_anchor_ref") or unit.get("worked_anchor_ref"):
            ctx.gap("AUTHOR_TOUGHEST_CONCEPT", unit["id"],
                    f"{why}, but the different worked example has no explicit target-crux binding: "
                    "author grade9v3:lesson_anchors with target_question_ref, target_crux_move_ref "
                    "and construction_ref", "CORE1A", component="WORKED_EXAMPLE")
        else:
            ctx.gap("AUTHOR_TOUGHEST_CONCEPT", unit["id"],
                    f"{why}, but its crux_question_refs are only a label: a worked teaching example "
                    "bound to the target question and crux is absent", "CORE1A", component="WORKED_EXAMPLE")


def core1b(ctx: Ctx, m: dict) -> str:
    e = m.get("elicitation")
    if not e:
        ctx.gap("AUTHOR_ELICITATION", m["id"], "no predict/attempt/reconstruct/boundary cycle", "CORE1B")
        return compose(ctx, "CORE1B", {"identity": f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1B", m)})
    unit = (m.get("construction_units") or [{}])[0]
    wrong = _misconceptions(m, unit if unit else None)
    rec = e.get("reconstruct") or {}
    att = e.get("attempt") or {}
    bt = e.get("boundary_test") or {}
    model = att.get("model_response") or "; ".join(r.get("criterion", "") for r in att.get("rubric") or [])
    task = att.get("task")
    # The attempt's own figure; the Core1A unit's figure depicts the worked anchor, not this task.
    task_rep = (task or {}).get("representation_ref") or unit.get("representation_ref")
    if not task:
        # `produces` describes the expected answer; it is not a task the learner can act on.
        ctx.gap("AUTHOR_RECONSTRUCTION_TASK", m["id"], "no concrete Core1B task (elicitation.attempt.task)", "CORE1B")
    return compose(ctx, "CORE1B", {
        "identity": f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1B", m),
        "attempt": (block("predict", para((e.get("predict") or {}).get("prompt")), title="Predict")
                    + figure(ctx, task_rep, "PRE_ATTEMPT", "CORE1B", m["id"], first_stage_only=True,
                             allowed=(task or {}).get("stage_refs") or None)
                    + block("attempt_prompt", (para(task["prompt"]) + items(task.get("givens"))) if task else "",
                            title="Attempt")
                    + attempt_box("Your attempt", (task or {}).get("response"), record=m["id"])),
        "reconstruction": (
            reveal("Reconstruct", block("reconstruct", items((r["ask"] for r in rec.get("route") or []), True))
                   + block("diagnose", items(w["diagnostic_prompt"] for w in wrong), title="Diagnose")
                   + block("repair", items(w["repair"] for w in wrong), title="Repair")
                   + block("success_criteria", para(att.get("produces")), title="What your answer should contain")
                   + block("model_response", para(model) + items(att.get("accepted")), title="What a complete answer does")
                   + block("rejoin_jump", para(m["inferential_jump"]), title="The step you rebuilt")
                   + figure(ctx, task_rep, "POST_ATTEMPT", "CORE1B", m["id"] + "-full"),
                   ref=f'CORE1B-{m["id"]}-reconstruct')
            + block("boundary_test", para(bt.get("prompt")), title="Boundary test")
            + reveal("Boundary answer", block("boundary_answer", para(bt.get("answer")) + para(bt.get("confirms"))),
                     ref=f'CORE1B-{m["id"]}-boundary')),
    })


def _identity(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    parts = [cust.get("exam"), cust.get("year"), cust.get("paper"), f"Q{cust['question_number']}" if cust.get("question_number") else None]
    return " · ".join(str(p) for p in parts if p) or q.get("original_identifier", "")


def _custody(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    if cust.get("authority_class") == "OWNER_SUPPLIED_RAW_INPUT":
        # CORE2.md: a question the owner supplied is custody in its own right and is shown as supplied, with no exam identity.
        line = "Owner-supplied question" + (", verbatim" if cust.get("wording_custody") == "VERBATIM" else "")
        authorship = (q.get("extensions") or {}).get("grade9v3:authorship") or {}
        return line + (" · coordinator/AI-drafted benchmark" if authorship.get("kind") == "COORDINATOR_AI_DRAFTED" else "")
    if (cust.get("authority_class") == "CURRICULAR_STANDARD"
            and cust.get("source_status") == "NCERT_AUTHENTIC"):
        wording = {
            "FAITHFUL_NCERT": "faithful NCERT wording",
            "VERBATIM": "verbatim",
        }.get(cust.get("wording_custody"), "")
        return "Verified curricular source" + (f", {wording}" if wording else "")
    if (cust.get("authority_class") != "OFFICIAL_EXAM_ORGANIZER_ARCHIVE"
            or cust.get("source_status") != "PYQ_VERIFIED_PARENT"
            or not cust.get("paper_url")):
        return "Source unverified"
    wording = {"FAITHFUL_NON_VERBATIM_RESTATEMENT": "faithful restatement of the original"}.get(cust.get("wording_custody"), "")
    return "Official past paper" + (f", {wording}" if wording else "")


def _source_pdf(q: dict) -> str:
    """The original past paper as a PDF, for a question whose source custody is a verified official exam organizer archive.

    Only an https link to a PDF is ever offered (never a script, a plain-http link or a page that is not a PDF), and only where the custody is
    verified; an owner-supplied question has no source file, and nothing is invented to make the icon appear."""
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    url = cust.get("paper_url")
    if (cust.get("authority_class") != "OFFICIAL_EXAM_ORGANIZER_ARCHIVE" or cust.get("source_status") != "PYQ_VERIFIED_PARENT"
            or not isinstance(url, str) or not re.fullmatch(r"[^\s<>\"'`]+", url.strip())):
        return ""
    parts = urlsplit(url.strip())
    if parts.scheme != "https" or not parts.netloc or not parts.path.lower().endswith(".pdf"):
        return ""
    return block("source_pdf", f'<a class="g9-pdf-link g9-source-pdf" data-g9-source-pdf href="{esc(url.strip())}" target="_blank" rel="noopener noreferrer" '
                 f'type="application/pdf" aria-label="{esc(SOURCE_PDF_ACCESSIBLE_NAME)}">{PDF_ICON}<span>Source paper (PDF)</span></a>')


def _core2_concept_navigation(ctx: Ctx, q: dict) -> str:
    """Link one selected source question back to its exact selected Core1A concept owners."""
    if "CORE1A" not in product_manifest.selected_output_roles(ctx.manifest):
        return ""   # a link to a page this product does not have would be a dead link
    join = _concept_join(ctx, "CORE2")
    ids = join["question_to_microtopics"].get(q["id"], [])
    if not ids:
        return ""
    microtopics = {m["id"]: m for m in ctx.selection_rows.get("microtopics", [])}
    repair = (q.get("extensions") or {}).get(learning_repair.KEY) or {}
    target = repair.get("construction_ref")
    unit_ids = {u["id"] for m in microtopics.values() for u in m.get("construction_units", [])}
    if target and target not in unit_ids:
        ctx.gap("AUTHOR_CONCEPT_TARGET", q["id"], "construction target does not resolve", "CORE2")
        return ""
    rows = []
    for microtopic_id in ids:
        microtopic = microtopics.get(microtopic_id)
        if not microtopic:
            continue
        rows.append(
            f'<li><a data-g9-concept-link data-g9-question-ref="{esc(q["id"])}" '
            f'data-g9-concept-ref="{esc(microtopic_id)}" '
            f'href="core1a.html?g9-return={esc(q["id"])}&amp;g9-concept={esc(microtopic_id)}#{esc(target or microtopic_id)}">'
            f'{esc(((q.get("extensions") or {}).get("grade9v3:attempt_labels") or {}).get("concept") or microtopic.get("title") or microtopic_id)}</a></li>'
        )
    return block("concept_navigation", "<ul>" + "".join(rows) + "</ul>" if rows else "",
                 title="Need the concept again?")


def _source_solution(answer: dict) -> str:
    key = answer.get("source_key") or {}
    verified = answer.get("_independent_result") or answer.get("summary")
    relation = answer.get("key_relation") or ("UNVERIFIED_KEY" if key.get("state") == "PRESENT" else "NO_KEY")
    if relation == "CONFLICTS_WITH_KEY":
        return (block("printed_key", para(key.get("value")), title="Printed book key")
                + block("verified_result", para(verified), title="Mathematically verified result")
                + block("key_conflict", para(answer.get("key_conflict_explanation")), title="Why they differ"))
    note_text = ("The printed key is ambiguous." if key.get("state") == "AMBIGUOUS"
                 else "No printed key accompanies this source item.")
    if relation == "NO_KEY":
        return block("answer", para(f'{note_text} {answer.get("summary", "")}'))
    if relation == "UNVERIFIED_KEY":
        return (block("printed_key", para(key.get("value") or "Printed key value awaits independent readback."),
                      title="Printed book key")
                + block("verified_result", para(answer.get("summary")), title="Worked result"))
    if key.get("value"):
        return (block("printed_key", para(key["value"]), title="Printed book key")
                + block("verified_result", para(verified), title="Mathematically verified result"))
    return block("answer", para(answer.get("summary")))


_CORE2_STAGE_LABEL = {
    "KEY_CONCEPT": "Key concept",
    "REPRESENTATION": "Representation",
    "FIRST_MOVE": "First move",
    "CRUX": "Crux",
    "FORMAL_MODEL": "Equation / formal model",
    "CHECKPOINT": "Assembly checkpoint",
    "OTHER": "Support",
}


def _core2_support_target(source: str) -> str:
    """The typed-math target a support row's text is declared under in the record."""
    found = re.match(r"(hints|scaffolds)\[(\d+)\]", source)
    if not found:
        return ""  # a ladder rung that carries its own text declares no typed-math span
    lane, index = found.groups()
    return f'{"source_hint" if lane == "hints" else "scaffold"}:{index}'


def _core2_rung_pill(provenance: str) -> str:
    source = provenance == core2_v2.SOURCE_HINT
    return f'<span class="g9-pill g9-pill-{"source" if source else "guided"}">{"Source" if source else "Guided"}</span>'


_CORE2_KIND_LABEL = {"REPRESENT": "Represent", "CONNECT": "Connect", "EXECUTE": "Carry out"}


def _core2_rung_head(number: int, stage: str | None, provenance: str, kind: str | None = None) -> str:
    """H0, H1, ...: which rung, what it is for, and whose words it carries."""
    label = (_CORE2_STAGE_LABEL[stage] if stage in _CORE2_STAGE_LABEL and stage != "OTHER"
             else _CORE2_KIND_LABEL.get(kind or "", "Support"))
    return (f'<div class="g9-rung-head"><span class="g9-rung-no">H{number - 1}</span>'
            f'<span class="g9-rung-label" data-g9-support-stage-label>{esc(label)}</span>'
            f'{_core2_rung_pill(provenance)}</div>')


def _core2_support_rung(ctx: Ctx, q: dict, row: dict, number: int, post_solution: bool = False) -> str:
    """Render one provenance-explicit support rung without manufacturing academic content."""
    attrs = [
        f'data-g9-rung="{number}"',
        f'data-g9-support-provenance="{esc(row["provenance"])}"',
        f'data-g9-support-source="{esc(row["source"])}"',
        f'data-g9-support-reveals="{esc(row["reveals"])}"',
    ]
    for attr, key in (
        ("data-g9-support-stage", "learner_stage"),
        ("data-g9-support-kind", "support_kind"),
        ("data-g9-supports-move", "supports_move_ref"),
    ):
        if row.get(key):
            attrs.append(f'{attr}="{esc(row[key])}"')
    stage = row.get("learner_stage")
    stage_badge = _core2_rung_head(number, stage, row["provenance"], row.get("support_kind"))
    allowed = [row["visual_stage_ref"]] if row.get("visual_stage_ref") else None
    instance_ref = None
    if row.get("visual_ref"):
        binding = core2_v2.visual_support(q, row["visual_ref"])
        if binding:
            instance_ref = binding["instance_ref"]
            if not post_solution:
                allowed = ([ref for ref in allowed if ref in binding["pre_attempt_stage_refs"]]
                           if allowed else binding["pre_attempt_stage_refs"])
    visual = ("" if instance_ref and allowed == [] and not post_solution else
              figure(ctx, row.get("visual_ref"), "POST_ATTEMPT" if post_solution else "PRE_ATTEMPT",
                     "CORE2", f'{q["id"]}-support-{number}', allowed=allowed,
                     instance_ref=instance_ref, owner_ref=q["id"]))
    reveal_body = f'<p>{question_text(ctx, q, _core2_support_target(row["source"]), row["text"])}</p>' + visual
    if row.get("prompt"):
        content = (stage_badge
                   + f'<p data-g9-support-prompt>{esc(row["prompt"])}</p>'
                   + f'<details data-g9-support-reveal><summary>Reveal support</summary>{reveal_body}</details>')
    else:
        content = stage_badge + f'<div data-g9-support-reveal>{reveal_body}</div>'
    return f'<li {" ".join(attrs)}>{content}</li>'


def _core2_support_ladder(ctx: Ctx, q: dict, rows: list[dict], provenance: str) -> str:
    """Keep every Core2 support rung collapsed until the learner requests it."""
    if not rows:
        return ""
    ref = f'CORE2-{q["id"]}-{provenance}'
    payloads = "".join(
        f'<template data-g9-rung-payload="{esc(ref)}-{number}">'
        f'{_core2_support_rung(ctx, q, row, number)}</template>'
        for number, row in enumerate(rows, 1)
    )
    label = "Show source hint" if provenance == core2_v2.SOURCE_HINT else "Show guided support"
    # The rungs still to come are listed by number, purpose and provenance only, so the learner sees the shape of
    # the ladder; each rung's words stay out of the page until it is asked for.
    ahead = "".join(f'<li data-g9-rung-ghost>{_core2_rung_head(number, row.get("learner_stage"), row["provenance"], row.get("support_kind"))}</li>'
                    for number, row in enumerate(rows, 1))
    return (f'<div class="g9-ladder" data-g9-ladder-ref="{esc(ref)}" '
            f'data-g9-support-group="{esc(provenance)}"><ol data-g9-ladder></ol>'
            f'<ol class="g9-rung-map" aria-label="Rungs still to come">{ahead}</ol>'
            f'{payloads}<button type="button" data-g9-next-rung>{esc(label)}</button></div>')


def _core2_support_rungs(q: dict) -> int:
    """How many rungs the learner can ask for before the solution (0 when the support does not project)."""
    try:
        source_rows, authored_rows = core2_v2.split_pre_solution_support(q)
    except core2_v2.Core2SupportProjectionError:
        return 0
    return len(source_rows) + len(authored_rows)


def _core2_support(ctx: Ctx, q: dict) -> str:
    """Project source and authored Core2 support into distinct, fail-closed learner lanes."""
    try:
        source_rows, authored_rows = core2_v2.split_pre_solution_support(q)
    except core2_v2.Core2SupportProjectionError as exc:
        ctx.gap("AUTHOR_CORE2_SUPPORT", q["id"], str(exc), "CORE2")
        return ""
    lanes = (block("source_hints",
                   _core2_support_ladder(ctx, q, source_rows, core2_v2.SOURCE_HINT),
                   title="Source support")
             + block("authored_core2_support",
                     _core2_support_ladder(ctx, q, authored_rows, core2_v2.AUTHORED_CORE2_SUPPORT),
                     title="Guided support"))
    return (secondary_disclosure(
        "Need a hint? · guided support",
        '<div class="g9-eyebrow">Hint ladder · reveal only what you need</div>' + lanes,
        "core2-hints",
    ) if lanes else "")


def _core2_solution_moves(answer: dict) -> int:
    """How many steps the learner is shown as the working (route moves, else the legacy reasoning lines)."""
    try:
        rows = core2_v2.project_solution(answer)
    except core2_v2.Core2SolutionProjectionError:
        return 0
    return len(rows) if rows else sum(1 for step in answer.get("reasoning") or [] if step)


def _core2_solution(ctx: Ctx, q: dict, answer: dict) -> str:
    """Render structured Core2 solution moves, with legacy prose only when no route exists."""
    try:
        rows = core2_v2.project_solution(answer)
    except core2_v2.Core2SolutionProjectionError as exc:
        ctx.gap("AUTHOR_CORE2_SOLUTION", q["id"], str(exc), "CORE2")
        return ""
    if not rows:
        steps = "".join(f'<li>{question_text(ctx, q, f"answer_reasoning:{i}", step)}</li>'
                        for i, step in enumerate(answer.get("reasoning") or []) if step)
        return block("working", f"<ol>{steps}</ol>" if steps else "")

    rendered = []
    for row in rows:
        attrs = [
            f'data-g9-solution-order="{row["order"]}"',
            f'data-g9-solution-move="{esc(row["move_id"])}"',
            f'data-g9-solution-kind="{esc(row["kind"])}"',
            f'data-g9-solution-stage="{esc(row["stage"])}"',
            f'data-g9-solution-crux="{"true" if row["is_crux"] else "false"}"',
        ]
        if row.get("source_ref"):
            attrs.append(f'data-g9-solution-source="{esc(row["source_ref"])}"')
        allowed = [row["visual_stage_ref"]] if row.get("visual_stage_ref") else None
        visual = figure(ctx, row.get("representation_ref"), "POST_ATTEMPT", "CORE2",
                        f'{q["id"]}-solution-{row["order"]}', allowed=allowed)
        crux = '<p class="g9-prov" data-g9-crux-label>Key move</p>' if row["is_crux"] else ""
        uses = block("solution_inputs", items(row.get("inputs")), title="Uses")
        rendered.append(
            f'<section class="g9-solution-move" {" ".join(attrs)}>'
            f'<div class="g9-step-no" aria-hidden="true">{row["order"]}</div>'
            f'<div class="g9-step-body"><h4 data-g9-solution-stage-label>{esc(row["stage"].title())}</h4>'
            f'{crux}<p data-g9-solution-action>{esc(row["action"])}</p>{uses}'
            f'<p data-g9-solution-why><em>Why valid:</em> {esc(row["why_valid"])}</p>'
            f'<p data-g9-solution-output><strong>Result:</strong> {esc(row["output"])}</p>'
            f'{visual}</div></section>'
        )
    return block("structured_working", "".join(rendered), title="Reasoning route")


_DIFFICULTY_PART = {
    "concept_model_selection": "Choosing the model",
    "representation_translation": "Representation",
    "reasoning_chain_length": "Reasoning chain",
    "algebra_computational_load": "Algebra and numbers",
    "trap_exception_sensitivity": "Traps and exceptions",
}


def _difficulty_why(rid: str, analysis: dict) -> str:
    """The band, its score and the five parts behind it, from the record's own difficulty estimate."""
    d = analysis.get("difficulty")
    if not isinstance(d, dict) or not d.get("band"):
        return ""
    parts = d.get("components") if isinstance(d.get("components"), dict) else {}
    cells = "".join(f'<div class="g9-dcell"><span>{esc(label)}</span><b>{parts[key]}/2</b></div>'
                    for key, label in _DIFFICULTY_PART.items() if isinstance(parts.get(key), int))
    score = f' · {d["score"]}/10' if isinstance(d.get("score"), int) else ""
    seconds = analysis.get("expected_time_seconds")
    if isinstance(seconds, int) and seconds > 0:
        minutes = round(seconds / 60)
        score += f' · about {minutes} min' if minutes >= 1 else f' · about {seconds} s'
    target = f"g9-why-{re.sub(r'[^A-Za-z0-9_-]+', '-', rid)}"
    return (f'<button type="button" class="g9-why-toggle" data-g9-toggle aria-expanded="false" aria-controls="{target}">'
            f'<span class="g9-pill g9-pill-band" data-g9-band="{esc(d["band"])}">{esc(d["band"])}{score}</span>'
            f'<span>Why this difficulty?</span></button>'
            f'<div id="{target}" class="g9-why" hidden>'
            '<p>This author estimate combines the five parts below. The detailed rationale is available with the answer and working after your attempt.</p>'
            f'{f"<div class=g9-dgrid>{cells}</div>" if cells else ""}</div>')


def _core2_question_figures(ctx: Ctx, q: dict, stage: str = "PRE_ATTEMPT") -> str:
    """Use explicitly reviewed authored support without replacing a source figure.

    Frozen question figure_refs remain custody data. A correction may supersede
    an authored representation, but not an authentic source snapshot/resource.
    """
    refs = q.get("figure_refs") or []
    review = (q.get("extensions") or {}).get("grade9v3:core2_visual_review")
    if review is not None:
        authored = review.get("authored_figure_refs") if isinstance(review, dict) else None
        valid = (isinstance(review, dict) and review.get("question_ref") == q["id"]
                 and review.get("replaces_authored_figure_refs") == refs
                 and isinstance(review.get("rationale"), str) and bool(review["rationale"].strip())
                 and isinstance(authored, list) and bool(authored)
                 and all(isinstance(ref, str) for ref in authored))
        representations = ctx.index("representations")
        if valid:
            valid = all(ref in representations and representations[ref].get("kind") != "SOURCE_FIGURE"
                        for ref in refs + authored)
            valid = valid and all((representations[ref].get("extensions") or {}).get("grade9v3:authored_question_ref") == q["id"]
                                  for ref in authored)
        if not valid:
            ctx.gap("AUTHOR_CORE2_VISUAL_REVIEW", q["id"],
                    "review must bind this question and its frozen authored refs; source figure snapshots cannot be replaced", "CORE2")
        else:
            refs = authored
    return _core2_bound_figures(ctx, q, refs, stage)


def _core2_bound_figures(ctx: Ctx, q: dict, refs: list[str], stage: str) -> str:
    output = []
    try:
        plan = core2_v2.support_plan(q)
        if any(item["representation_ref"] not in refs for item in plan.get("visuals", [])):
            raise core2_v2.Core2SupportProjectionError("a bound visual must belong to this question's figure references")
        for ref in refs:
            binding = core2_v2.visual_support(q, ref)
            if not binding:
                if stage == "PRE_ATTEMPT":
                    output.append(figure(ctx, ref, stage, "CORE2", q["id"], first_stage_only=True))
                continue
            if stage == "PRE_ATTEMPT":
                allowed = binding["pre_attempt_stage_refs"]
                render_stage = "PRE_ATTEMPT"
            elif stage == "AFTER_ATTEMPT":
                allowed = binding["after_attempt_stage_refs"]
                render_stage = "POST_ATTEMPT"
            else:
                allowed = binding["post_solution_stage_refs"]
                render_stage = "POST_ATTEMPT"
            if not allowed:
                continue
            output.append(figure(ctx, ref, render_stage, "CORE2", q["id"], allowed=allowed,
                                 instance_ref=binding["instance_ref"], owner_ref=q["id"]))
    except core2_v2.Core2SupportProjectionError as exc:
        ctx.gap("AUTHOR_CORE2_SUPPORT", q["id"], str(exc), "CORE2")
    return "".join(output)


def _core2_after_attempt_support(ctx: Ctx, q: dict) -> str:
    """Support unlocked by commitment without bundling it into the full solution."""
    if core2_v2.SUPPORT_PLAN_KEY not in (q.get("extensions") or {}):
        return ""
    try:
        rows = core2_v2.after_attempt_support(q)
        text = "".join(_core2_support_rung(ctx, q, row, number, post_solution=True)
                       for number, row in enumerate(rows, 1))
        figures = _core2_question_figures(ctx, q, "AFTER_ATTEMPT")
    except core2_v2.Core2SupportProjectionError as exc:
        ctx.gap("AUTHOR_CORE2_SUPPORT", q["id"], str(exc), "CORE2")
        return ""
    body = block("after_attempt_support", (f"<ol>{text}</ol>" if text else "") + figures,
                 title="Support after your attempt") if text or figures else ""
    return reveal("More support after your attempt", body, ref=f'CORE2-{q["id"]}-after-attempt') if body else ""


def _core2_completed_support(ctx: Ctx, q: dict) -> str:
    """Keep solution-only support inside the existing attempted-solution payload."""
    if core2_v2.SUPPORT_PLAN_KEY not in (q.get("extensions") or {}):
        return ""
    try:
        rows = core2_v2.post_solution_support(q)
        text = "".join(_core2_support_rung(ctx, q, row, number, post_solution=True)
                       for number, row in enumerate(rows, 1))
        figures = _core2_question_figures(ctx, q, "POST_SOLUTION")
    except core2_v2.Core2SupportProjectionError as exc:
        ctx.gap("AUTHOR_CORE2_SUPPORT", q["id"], str(exc), "CORE2")
        return ""
    return block("completed_support", (f"<ol>{text}</ol>" if text else "") + figures,
                 title="Further support") if text or figures else ""


def core2(ctx: Ctx, q: dict) -> str:
    q = source_projection(ctx, q)
    ans = q["answer"]
    if ans.get("_independent_result") and ans["_independent_result"] != ans.get("summary"):
        ctx.gap("AUTHOR_SOURCE_RESULT_DIFFERS", q["id"], "authored summary differs from current independent result", "CORE2")
    rid = q["id"]
    analysis = (q.get("extensions") or {}).get(owner_bank.ANALYSIS_KEY) or {}
    figures = _core2_question_figures(ctx, q)
    roles = q.get("representation_roles") or {}
    teaching_figure = figure(ctx, roles.get("bound_ref"), "POST_ATTEMPT", "CORE2", rid + "-bound")
    conditions = "".join(f'<li>{question_text(ctx, q, "conditions", c)}</li>' for c in q.get("conditions") or [])
    options = [question_text(ctx, q, f"option:{i}", opt) for i, opt in enumerate(q.get("options") or [])]
    solution = _source_solution(ans)
    if not ans.get("source_key"):
        solution = block("answer", '<p>' + question_text(ctx, q, "answer_summary", ans.get("summary")) + '</p>')
    wrong_route = analysis.get("common_wrong_route")

    band = ((analysis.get("difficulty") or {}).get("band")) if isinstance(analysis.get("difficulty"), dict) else None
    waivers = blueprints_api.waivers_of(q)

    # A newly authored Owner-bank question is held to the complete Core2
    # reasoning contract in a REFERENCE deployment. Legacy prose is still
    # renderable for FLOOR products, but it is not a substitute for the
    # move-typed solution that an Owner must finish before acceptance.
    custody = (q.get("extensions") or {}).get(owner_bank.CUSTODY_KEY) or {}
    if (ctx.held_to == "REFERENCE"
            and custody.get("authority_class") == owner_bank.CUSTODY_CLASS
            and not ans.get("reasoning_route")):
        ctx.gap("AUTHOR_COMPONENT", rid,
                "SOLUTION_STEPS is absent: answer.reasoning_route must teach the authored inferential moves",
                "CORE2", component="SOLUTION_STEPS")

    def part(cid: str, body: str, items: int | None = None) -> str:
        return component(ctx, "CORE2", cid, body, rid, items=items, band=band, waivers=waivers)

    repair = (q.get("extensions") or {}).get(learning_repair.KEY)
    unit_ids = {u["id"] for m in ctx.selection_rows.get("microtopics", []) for u in m.get("construction_units", [])}
    repair_errors = learning_repair.problems(q, unit_ids) if repair is not None else []
    for error in repair_errors:
        ctx.gap("AUTHOR_LEARNING_REPAIR", rid, error, "CORE2")
    repair_html = learning_repair.card(repair, rid) if repair and not repair_errors else ""
    detailed_labels = ""
    if (q.get("extensions") or {}).get("grade9v3:attempt_labels"):
        concept = learner_metadata.resolve_concept(ctx.packages, q.get("primary_capability_ref"))
        family = learner_metadata.resolve_family(ctx.packages, q.get("family_ref"))
        detailed_labels = block("detailed_concept_labels", para(concept["concept"] + " · " + family["family"]),
                                title="Concept and question family")
    worked = component_body(ctx, "CORE2", {
        "DIAGNOSTIC_REPAIR": part("DIAGNOSTIC_REPAIR", repair_html),
        "SOLUTION_STEPS": part("SOLUTION_STEPS", _core2_solution(ctx, q, ans), items=_core2_solution_moves(ans)),
        "ANSWER": part("ANSWER", solution),
        "CHECK": part("CHECK", block("independent_check", '<p>' + question_text(ctx, q, "answer_check", ans["check"]) + '</p>'
                                     if ans.get("check") else "", title="Independent check")),
    }, parent="SOLUTION")
    rendered = compose(ctx, "CORE2", {
        "identity": component_body(ctx, "CORE2", {
            "IDENTITY": part("IDENTITY", block("source_identity", f"<h2>{esc(_identity(q))}</h2><p class=\"g9-prov\">{esc(_custody(q))}</p>")
                             + metadata_strip(ctx, "CORE2", q)),
            "SOURCE_PDF": part("SOURCE_PDF", _source_pdf(q)),
            "DIFFICULTY_WHY": part("DIFFICULTY_WHY", _difficulty_why(rid, analysis)),
        }, "identity"),
        "attempt": component_body(ctx, "CORE2", {
            "STEM": part("STEM", '<div class="g9-eyebrow">Attempt first</div>'
                         + block("stem", '<p>' + question_text(ctx, q, "stem", q["stem"]) + '</p>')),
            "CONDITIONS": part("CONDITIONS", block("conditions", f'<ul>{conditions}</ul>' if conditions else "", title="Conditions")),
            "ATTEMPT": part("ATTEMPT", attempt_box("Your answer", response_for(q), q.get("options"), rid,
                                                   option_html=options if options else None)),
        }, "attempt"),
        "representation": component_body(ctx, "CORE2", {
            "REPRESENTATION": part("REPRESENTATION",
                                   ('<div class="g9-card-head"><strong>Representation</strong></div>' + figures) if figures else "",
                                   items=figures.count("<figure ")),
        }, "representation"),
        "support": component_body(ctx, "CORE2", {
            "TRAP": part("TRAP", reveal(
                "Common wrong route · after your attempt",
                block("common_wrong_route", '<p>' + question_text(ctx, q, "common_wrong_route", wrong_route) + '</p>'
                      if isinstance(wrong_route, str) and wrong_route.strip() else "", title="Common wrong route"),
                ref=f"CORE2-{rid}-wrong-route",
            )),
            "HINT_LADDER": part("HINT_LADDER", _core2_support(ctx, q) + _core2_after_attempt_support(ctx, q),
                                items=_core2_support_rungs(q)),
            "CONCEPT_NAV": part("CONCEPT_NAV", _core2_concept_navigation(ctx, q)),
        }, "support"),
        "solution": component_body(ctx, "CORE2", {
            "SOLUTION": part("SOLUTION", reveal("Answer and working", worked + teaching_figure + detailed_labels
                             + _core2_completed_support(ctx, q)
                             + block("difficulty_basis", para((analysis.get("difficulty") or {}).get("basis")),
                                     title="Author's difficulty rationale"), ref=f'CORE2-{rid}-solution')),
        }, "solution"),
    })
    return rendered + _purpose_extension(ctx, "CORE2", rid)


def _ladder(ctx: Ctx, q: dict, role: str, source: bool = False) -> str:
    rungs = sorted(q.get("hint_ladder") or [], key=lambda r: r["order"])
    texts = []
    visuals = []
    targets = []
    if source:
        texts = [h["text"] if isinstance(h, dict) else str(h) for h in q.get("hints") or []]
        targets = [f"source_hint:{i}" for i in range(len(texts))]
    else:
        for r in rungs:
            if r.get("text"):
                texts.append(r["text"])
                visuals.append("")
                targets.append("")
            elif r.get("from"):
                kind, i = re.match(r"(hints|scaffolds)\[(\d+)\]", r["from"]).groups()
                if role == "CORE2" and kind == "hints":
                    continue  # source hints must never count as authored teaching
                support = (q.get(kind) or [])[int(i)]
                texts.append(support["text"])
                targets.append(f'{"source_hint" if kind == "hints" else "scaffold"}:{i}')
                visuals.append(figure(ctx, support.get("visual_ref"), "POST_ATTEMPT", role,
                                      f'{q["id"]}-hint-{len(texts)}', allowed=[support["visual_stage_ref"]]
                                      if support.get("visual_stage_ref") else None))
        if role == "CORE2" and not rungs:
            texts = [s["text"] for s in q.get("scaffolds") or []]
            targets = [f"scaffold:{i}" for i in range(len(texts))]
            visuals = [figure(ctx, s.get("visual_ref"), "POST_ATTEMPT", role,
                              f'{q["id"]}-hint-{n}', allowed=[s["visual_stage_ref"]]
                              if s.get("visual_stage_ref") else None)
                       for n, s in enumerate(q.get("scaffolds") or [], 1)]
    if not source and role != "CORE2" and len(texts) < 3:
        ctx.gap("AUTHOR_HINT_LADDER", q["id"], f"{len(texts)} rung(s); need 3", role)
    if not texts:
        return ""
    ref = f'{role}-{q["id"]}' + ("-source" if source else "-authored")
    payloads = [question_text(ctx, q, targets[i] if i < len(targets) else "", t, role)
                + (visuals[i] if i < len(visuals) else "") for i, t in enumerate(texts)]
    # Core2A's first hint is *optional*, not disclosed on page load.
    # Every rung opened through the button is recorded as assisted locally.
    optional = role == "CORE2A"
    start = 0 if optional else 1
    later = "".join(f'<template data-g9-rung-payload="{esc(ref)}-{n}">'
                    f'<li data-g9-rung="{n}">{t}</li></template>'
                    for n, t in enumerate(payloads[start:], start + 1))
    initial = "" if optional else f'<li data-g9-rung="1">{payloads[0]}</li>'
    notice = ('<p data-g9-assistance-status role="status" aria-live="polite" hidden>'
              'Hints viewed: assisted practice, not independent mastery.</p>' if optional else "")
    return (f'<div class="g9-ladder" data-g9-ladder-ref="{esc(ref)}">'
            f'<ol data-g9-ladder>{initial}</ol>'
            f'{later}<button type="button" data-g9-next-rung'
            f'{" disabled" if not later else ""}>'
            f'{"Show hint 1" if optional else "Next hint"}</button>{notice}</div>')


def _family_title(ctx: Ctx, ref: str | None) -> str:
    fam = ctx.index("question_families").get(ref or "")
    return fam.get("title", "") if fam else ""


def _repair(ctx: Ctx, ref: str | None) -> str:
    """Link a canonical repair step to its exact Core1A construction location when one exists."""
    if not ref:
        return ""
    for p in ctx.packages:
        for m in p.get("microtopics", []):
            for s in m.get("teaching_path", []):
                if s["id"] != ref:
                    continue
                unit = next(
                    (row for row in m.get("construction_units") or [] if ref in (row.get("step_refs") or [])),
                    None,
                )
                target = unit["id"] if unit else m["id"]
                label = f'Revisit: {esc(s["action"])}'
                # Link to the exact owning construction unit, but only when Core1A is part of this packet.
                if _unit_href(ctx, "CORE1A", m["id"]):
                    return (
                        f'<p><a data-g9-repair-ref="{esc(ref)}" data-g9-concept-ref="{esc(m["id"])}" '
                        f'data-g9-repair-target="{esc(target)}" href="core1a.html#{esc(target)}">{label}</a></p>'
                    )
                return f"<p>{label}</p>"
    return ""


def core2a(ctx: Ctx, q: dict) -> str:
    ans = q["answer"]
    roles = q.get("representation_roles") or {}
    if not roles.get("initial_ref"):
        ctx.gap("AUTHOR_QUESTION_REPRESENTATION", q["id"], "no representation shown with the stem", "CORE2A")
    if not q.get("failure_signal"):
        ctx.gap("AUTHOR_FAILURE_SIGNAL", q["id"], "no item-specific failure signal", "CORE2A")
    fam = q.get("family_exposure") or {}
    if not fam.get("closure"):
        ctx.gap("AUTHOR_FAMILY_EXPOSURE", q["id"], "no family/exposure closure", "CORE2A")
    check = (q.get("independent_check") or {}).get("statement") or ans.get("check")
    route = "".join(f'<li><strong>{esc(s["kind"])}</strong> {esc(s["action"])}<br><em>Why valid:</em> {esc(s["why_valid"])}</li>'
                    for s in ans.get("reasoning_route") or [])
    return compose(ctx, "CORE2A", {
        "identity": (block("provenance", f'<p class="g9-prov">{esc(q.get("origin"))} practice</p>')
                     + metadata_strip(ctx, "CORE2A", q)
                     + block("family_identity", para(_family_title(ctx, fam.get("family_ref") or q.get("family_ref"))))),
        "attempt": (block("stem", f"<h2>{esc(q['stem'])}</h2>")
                    + block("conditions", items(q.get("conditions")), title="Conditions")
                    + figure(ctx, roles.get("initial_ref"), "PRE_ATTEMPT", "CORE2A", q["id"], allowed=roles.get("stage_refs"))
                    + attempt_box("Your attempt", response_for(q), q.get("options"), q["id"])),
        "support": _ladder(ctx, q, "CORE2A"),
        "reasoning": reveal("Reasoning route and full solution",
                            block("reasoning_route", f"<ol>{route}</ol>" if route else "")
                            + figure(ctx, roles.get("bound_ref"), "POST_ATTEMPT", "CORE2A", q["id"] + "-bound")
                            + block("solution", items(ans.get("reasoning"), True))
                            + block("answer", para(ans.get("summary")), title="Answer")
                            + block("independent_check", para(check), title="Independent check")
                            + block("failure_signal", para(q.get("failure_signal")), title="If you went wrong")
                            + block("repair", _repair(ctx, q.get("repair_ref")), title="Repair")
                            + block("exposure_closure", para(fam.get("closure")), title="What this establishes"),
                            ref=f'CORE2A-{q["id"]}-reasoning'),
    })


def core2b(ctx: Ctx, q: dict) -> str:
    ans = q["answer"]
    roles = q.get("representation_roles") or {}
    tr = q.get("transfer") or {}
    if not roles.get("safe_ref"):
        ctx.gap("AUTHOR_SAFE_REPRESENTATION", q["id"], "no safe pre-commitment representation", "CORE2B")
    if not tr.get("invariant"):
        ctx.gap("AUTHOR_LINEAGE_CHECK", q["id"], "no invariant-versus-changed statement", "CORE2B")
    novelty = tr.get("novelty") or {}
    if not (novelty.get("checked_against") and novelty.get("why_new")):
        ctx.gap("AUTHOR_TRANSFER_NOVELTY", q["id"],
                "no record of which earlier items (Core1A anchors, Core1B boundary tests, Core2A items) this "
                "task was checked against and why its decision is new", "CORE2B")
    qs = ctx.index("questions")

    def _short(text: str) -> str:
        return text if len(text) <= 90 else text[:87].rsplit(" ", 1)[0] + "…"
    sel = ctx.manifest.get("selection") or {}

    def _where(b: str) -> str | None:
        """The page and unit where the earlier item is rendered: its Core2A article, or the Core1A
        microtopic that uses it as a worked anchor. None when this product does not show it."""
        href = _unit_href(ctx, "CORE2A", b)
        if href:
            return href
        for m in ctx.index("microtopics").values():
            if m["id"] in (sel.get("microtopics") or []) and any(
                    u.get("worked_anchor_ref") == b for u in m.get("construction_units") or []):
                return _unit_href(ctx, "CORE1A", m["id"])
        return None

    def _earlier(b: str) -> str:
        label = esc(_short(qs[b]["stem"]) if b in qs else "Earlier practice item")
        href = _where(b)
        return f'<li><a data-g9-lineage href="{esc(href)}">{label}</a></li>' if href else f"<li>{label}</li>"
    lineage = "".join(_earlier(b) for b in tr.get("builds_on") or [])
    check = (q.get("independent_check") or {}).get("statement") or ans.get("check")
    protected = next((s for s in ans.get("reasoning_route") or [] if s.get("id") == tr.get("protected_move_ref")), None)
    # Safe pre-attempt support is the item's own first rung (orientation), never a generic sentence.
    rung = next((r for r in sorted(q.get("hint_ladder") or [], key=lambda r: r["order"]) if r.get("purpose") == "ORIENT"), None)
    rung_text = (rung.get("text") or "") if rung else ""
    if rung and not rung_text and rung.get("from"):
        kind, i = re.match(r"(hints|scaffolds)\[(\d+)\]", rung["from"]).groups()
        rung_text = (q.get(kind) or [])[int(i)]["text"]
    return compose(ctx, "CORE2B", {
        "identity": (block("provenance", f'<p class="g9-prov">{esc(q.get("origin"))} transfer</p>')
                     + metadata_strip(ctx, "CORE2B", q)
                     + block("stem", f"<h2>{esc(q['stem'])}</h2>")
                     + block("lineage", f"<ul>{lineage}</ul>" if lineage else "", title="Builds on")),
        "attempt": (block("conditions", items(q.get("conditions")), title="Conditions")
                    + figure(ctx, roles.get("safe_ref"), "PRE_ATTEMPT", "CORE2B", q["id"], allowed=roles.get("stage_refs"))
                    + block("safe_support", para(rung_text), title="Where to start")
                    + attempt_box("Your commitment: the model or representation you choose, and your first relation",
                                  response_for(q), q.get("options"), q["id"])),
        "post_attempt": (
            block("lineage_check", para("Before you open the solution: what from the earlier item still holds here, "
                                        "and what is different?") if tr.get("invariant") else "", title="Lineage check")
            + reveal("Review and solution",
                     block("invariant_changed", para(tr.get("invariant")), title="What stayed valid")
                     + block("changed_demand", para(tr.get("statement")), title="What changed")
                     + block("protected_move", para(protected["action"]) if protected else "", title="The deciding move")
                     + figure(ctx, roles.get("bound_ref"), "POST_ATTEMPT", "CORE2B", q["id"] + "-bound")
                     + block("answer", para(ans.get("summary")) + items(ans.get("reasoning"), True), title="Answer")
                     + block("rubric", items(r.get("criterion") for r in ans.get("rubric") or []), title="Rubric")
                     + block("independent_check", para(check), title="Independent check")
                     + block("repair", _repair(ctx, q.get("repair_ref")), title="Repair"),
                     ref=f'CORE2B-{q["id"]}-review')),
    })


RENDER = {"CORE1": core1, "CORE1A": core1a, "CORE1B": core1b, "CORE2": core2, "CORE2A": core2a, "CORE2B": core2b}


# ------------------------------------------------------------------ selection

def units_for(ctx: Ctx, role: str) -> list[dict]:
    key = "microtopics" if role in {"CORE1", "CORE1A", "CORE1B"} else role.lower()
    rows = ctx.selection_rows[key]
    if role not in {"CORE1", "CORE1A", "CORE1B"} and not rows:
        ctx.gap("ACQUIRE_SOURCE" if role == "CORE2" else "AUTHOR_PRACTICE", ctx.manifest["product_id"],
                f"no {role} items selected", role)
    return rows


# ------------------------------------------------------------------ page

CSS = """
[hidden]{display:none!important}
:root{--g9-zoom:1;--g9-content-max:1380px;--g9-touch-min:48px;--g9-space:clamp(16px,2vw,28px);--g9-type-body:17px;--bg:#f6f7fb;--fg:#172033;--card:#fff;--line:#d5dce6;--accent:#1f5fae;--muted:#52627a;
--soft:#fbfdff;--pill-bg:#eef2ff;--pill-fg:#4338ca;--src-bg:#ecfdf5;--src-fg:#047857;--info-bg:#f8fbff;--info-line:#93c5fd;--info-fg:#455d72;--warn-bg:#fff7f8;--warn-line:#ffc9d3;--warn-fg:#8a2942;--ok-bg:#f0fdf7;--ok-line:#bbf7d0;--ok-fg:#14532d}
:root[data-theme=dark]{--bg:#0f1520;--fg:#e8edf5;--card:#18212f;--line:#2c394d;--accent:#8ab4f8;--muted:#a3b1c6;
--soft:#141c29;--pill-bg:#262f5a;--pill-fg:#c3c9ff;--src-bg:#12301f;--src-fg:#6ee7b7;--info-bg:#14263d;--info-line:#3b6db3;--info-fg:#b8c9de;--warn-bg:#2b1620;--warn-line:#6b3045;--warn-fg:#f3b6c4;--ok-bg:#10281d;--ok-line:#1f6b44;--ok-fg:#b7efcf}
html{font-size:calc(var(--g9-type-body) * var(--g9-zoom))}body{margin:0;background:var(--bg);color:var(--fg);font:1rem/1.6 system-ui,sans-serif;overflow-wrap:break-word}
header[data-g9-shell-header]{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px var(--g9-space);background:var(--card);border-bottom:1px solid var(--line)}
.g9-header-inner{width:100%;min-width:0;box-sizing:border-box;padding:0;gap:12px}
.g9-brand{min-width:0;max-width:100%;flex-wrap:wrap;justify-content:flex-start;overflow-wrap:anywhere}
.g9-header-nav,.g9-header-actions{min-width:0;max-width:100%;flex-wrap:wrap;gap:8px}
.g9-header-nav a,.g9-header-actions>*{max-width:100%;white-space:normal;overflow-wrap:anywhere}
a{color:var(--accent)}
header a,header button,button,summary,nav a{min-height:var(--g9-touch-min);min-width:var(--g9-touch-min);padding:10px 14px;box-sizing:border-box;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg);font:inherit;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;touch-action:manipulation}
nav[data-g9-breadcrumb]{display:flex;gap:8px;flex-wrap:wrap;padding:8px var(--g9-space)}
.g9-breadcrumb-bar{display:none!important}
.g9-triad-context{font-size:max(.85rem,14px);opacity:.7;margin-bottom:4px;display:block}
.g9-triad-context a{color:inherit;text-decoration:none;min-height:var(--g9-touch-min);min-width:var(--g9-touch-min);padding:0 8px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;touch-action:manipulation}
.g9-triad-context a:hover{text-decoration:underline}
.g9-triad-actions a{min-height:var(--g9-touch-min);min-width:var(--g9-touch-min);padding:10px 14px;box-sizing:border-box;display:inline-flex;align-items:center;justify-content:center;touch-action:manipulation}
main{width:100%;min-width:0;max-width:var(--g9-content-max);margin:0 auto;padding:var(--g9-space);box-sizing:border-box;overflow-wrap:anywhere}
main>*{min-width:0}article[data-g9-unit]{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:var(--g9-space);margin:18px 0;min-width:0}
article[data-g9-unit]>*{min-width:0}
.blueprint-slot,.g9-component,.g9-cu,.g9-cu-support,[data-g9-block],details,fieldset{min-width:0;max-width:100%;box-sizing:border-box}
fieldset{min-inline-size:0}
h1,h2,h3,h4,p,li,label,summary{overflow-wrap:anywhere}
article[id],section[id]{scroll-margin-top:var(--g9-header-offset,96px)}
.g9-core1a-book{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:clamp(16px,2vw,24px);margin:0 0 18px;min-width:0}
.g9-core1a-book>h2{margin:.15em 0 .6em}
.g9-bucket-orientation-grid{display:block;min-width:0}.g9-bucket-orientation-grid>*{min-width:0}
[data-g9-concept-route] ol,[data-g9-section-route] ol{padding-left:1.4rem;margin:.5rem 0;box-sizing:border-box;max-width:100%;min-width:0}
[data-g9-concept-route] li,[data-g9-section-route] li{margin:.35rem 0;max-width:100%;min-width:0}
[data-g9-concept-route] a,[data-g9-section-route] a{display:flex;width:100%;max-width:100%;min-width:0;justify-content:flex-start;text-align:left;white-space:normal;overflow-wrap:anywhere}
.g9-cu{padding-top:8px;border-top:1px solid var(--line)}
.g9-cu:first-child{border-top:0}
.g9-path-bridge[data-g9-derivation-bridge] [data-g9-block=construction] ol{list-style:none;padding-left:0;counter-reset:g9-derive}
.g9-path-bridge[data-g9-derivation-bridge] [data-g9-block=construction] li{counter-increment:g9-derive;margin:0 0 12px;padding:12px 14px;border-left:3px solid var(--accent);background:var(--bg)}
.g9-path-bridge[data-g9-derivation-bridge] [data-g9-block=construction] li::before{content:"Step " counter(g9-derive);display:block;color:var(--muted);font-size:max(.85rem,14px);font-weight:700;text-transform:uppercase;letter-spacing:.03em}
.g9-cu-nav{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:.35rem 0 .8rem}
.g9-cu-nav-links{display:flex;gap:8px;flex-wrap:wrap}
.g9-stage-controls{display:grid;gap:8px;max-width:100%}
.g9-stage-chips{display:flex;flex-wrap:wrap;gap:8px}
.g9-stage-chip{border-radius:999px;padding:6px 14px;font-size:.9rem}.g9-stage-chip[aria-pressed=true]{background:var(--accent);color:var(--card);border-color:var(--accent);font-weight:700}
.g9-stage-desc{margin:0;color:var(--muted);font-size:.92rem;min-height:1.4em}
.g9-stage-stepper{display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.g9-stage-stepper>[data-g9-stage-label]{color:var(--muted);flex:0 1 auto}
.g9-table-scroll{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.g9-table-scroll table{width:100%;min-width:680px;border-collapse:collapse}
.g9-table-scroll th,.g9-table-scroll td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
.g9-table-scroll th{background:var(--bg)}
.g9-table-scroll td>.g9-math,.g9-table-scroll td>.g9-expr{margin:.15rem 0}
[data-g9-block=worked_anchor]{border-left:4px solid var(--accent);padding-left:14px}
.g9-watch-steps>li{margin:.8rem 0}.g9-watch-steps p{margin:.2rem 0}
[data-g9-block=wrong_path],[data-g9-block=repair]{border-left:3px solid var(--line);padding-left:12px}
[data-g9-block=scope_boundary]{color:var(--muted);font-size:.92rem}
[data-g9-block=scope_boundary] ul{margin:.35rem 0;padding-left:1.2rem}
.g9-availability-note{color:var(--muted);font-size:.9rem}
.g9-cu-support{padding:0 0 16px;margin:0 0 16px;border-bottom:1px solid var(--line)}
.g9-cu-support:last-of-type{border-bottom:0}.g9-cu-support>h3{font-size:1rem;line-height:1.35;margin:.3rem 0 .7rem;color:var(--muted)}
@media (min-width:1100px){.g9-bucket-orientation-grid{display:grid;grid-template-columns:.68fr .32fr;gap:20px}}
textarea{width:100%;min-height:120px;font:inherit;border:1px solid var(--line);border-radius:10px;padding:14px 16px;box-sizing:border-box;background:var(--card);color:var(--fg)}
details{border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:0 12px}details[data-locked] summary{opacity:.55;cursor:not-allowed}
figure{margin:14px 0;max-width:100%;overflow-x:auto}figure svg{width:100%;height:auto;max-width:720px}figcaption{color:var(--muted)}
.g9-prov{color:var(--muted);font-size:.95rem}.g9-expr{font-family:ui-monospace,monospace;font-size:1.05rem}
[data-g9-meta-strip]{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}
[data-g9-meta-item]{display:inline-flex;flex-wrap:wrap;gap:4px;align-items:baseline;padding:5px 9px;border:1px solid var(--line);border-radius:999px;background:var(--bg);font-size:.9rem;max-width:100%;min-width:0;box-sizing:border-box}
[data-g9-meta-item] strong{font-weight:700;flex:0 0 auto}
[data-g9-meta-label]{min-width:0;overflow-wrap:anywhere}
h4{margin:.8em 0 .3em}:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
input:focus-visible,textarea:focus-visible,select:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
.g9-shell-header .g9-header-btn:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation:none!important;transition:none!important;scroll-behavior:auto!important}}
footer{padding:24px 16px;color:var(--muted)}
@media print{:root,:root[data-theme=dark]{--bg:#fff;--fg:#000;--card:#fff;--line:#bbb;--accent:#1f5fae;--muted:#333;--soft:#fff;--pill-bg:#eee;--pill-fg:#222;--src-bg:#eee;--src-fg:#222;--info-bg:#fff;--info-line:#888;--info-fg:#222;--warn-bg:#fff;--warn-line:#888;--warn-fg:#222;--ok-bg:#fff;--ok-line:#888;--ok-fg:#222}
header[data-g9-shell-header],nav[data-g9-breadcrumb],.g9-attempt,button,[data-g9-display-panel],[data-g9-source-pdf]{display:none!important}
.g9-attempt:has(.g9-answer-options){display:block!important}
.g9-attempt>:not(.g9-answer-options),.g9-answer-option input{display:none!important}
details[data-requires-attempt]:not([open]){display:none!important}
details{border:none}article[data-g9-unit]{break-inside:auto;border:none}
h1,h2,h3,h4{break-after:avoid-page}footer{padding:0;break-before:avoid-page}
body{background:#fff;color:#000}}
.g9-attempt input[type=text],.g9-attempt select,.g9-attempt textarea{min-height:48px;box-sizing:border-box}
.g9-answer-option,.g9-paper,.g9-match{display:flex;align-items:center;gap:.5rem;min-height:48px}
.g9-answer-option input,.g9-paper input{min-width:48px;min-height:48px}
.g9-attempt fieldset{min-height:48px}
.g9-math,pre,table{max-width:100%;overflow-x:auto}
input,select{font-size:max(16px,1rem)}
@media (max-width:899px){header[data-g9-shell-header]{position:relative}article[data-g9-unit]{padding:16px}nav[data-g9-breadcrumb]{font-size:.95rem}}
"""

# Presentation of the blueprint's components. One rule set per presentation archetype the schema allows
# (Shared/web/interactive-page-blueprint.schema.json, $defs/presentation); a test keeps the two lists equal.
# Text is never below .85rem (14.45px at the base size), the blueprint's learner-text floor.
COMPONENT_CSS = """
.g9-split{display:block;min-width:0}.g9-col{min-width:0}
.g9-component{min-width:0;margin:14px 0}.g9-component:first-child{margin-top:0}
.g9-eyebrow{font-size:max(.85rem,14px);font-weight:800;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);margin:0 0 6px}
.g9-pill{display:inline-flex;align-items:center;font-size:max(.85rem,14px);font-weight:800;line-height:1.2;padding:3px 10px;border-radius:999px;background:var(--pill-bg);color:var(--pill-fg);white-space:nowrap}
.g9-pill-source{background:var(--src-bg);color:var(--src-fg)}
.g9-purpose-extension{margin:18px 0;padding:16px;border:2px solid var(--accent);border-radius:16px;background:var(--soft)}
.g9-purpose-extension h3{margin:.1rem 0 .35rem}.g9-purpose-source{margin:.15rem 0 .7rem;color:var(--muted);font-size:.9rem}
.g9-purpose-prompt p{font-size:1.05rem;line-height:1.55;white-space:pre-line}
.g9-secondary-disclosure{border:1px solid var(--line);border-radius:12px;background:var(--card);overflow:hidden}
.g9-secondary-disclosure{min-width:0;max-width:100%}
.g9-c-disclosure-tile,.g9-c-disclosure-info,.g9-c-disclosure-equation-card,.g9-c-disclosure-trap-card,.g9-c-predict-reveal-worked-card{min-width:0;max-width:100%;overflow-wrap:anywhere}
.g9-c-disclosure-tile>.g9-secondary-disclosure{background:var(--soft)}
.g9-c-disclosure-info>.g9-secondary-disclosure{background:var(--info-bg);border-color:var(--info-line)}
.g9-c-disclosure-equation-card>.g9-secondary-disclosure{background:var(--soft)}
.g9-c-disclosure-trap-card>.g9-secondary-disclosure{background:var(--warn-bg);border-color:var(--warn-line);color:var(--warn-fg)}
.g9-c-predict-reveal-worked-card>.g9-secondary-disclosure{border-left:4px solid var(--accent)}
.g9-c-disclosure-tile .g9-secondary-disclosure>summary,.g9-c-disclosure-info .g9-secondary-disclosure>summary,.g9-c-disclosure-equation-card .g9-secondary-disclosure>summary,.g9-c-disclosure-trap-card .g9-secondary-disclosure>summary,.g9-c-predict-reveal-worked-card .g9-secondary-disclosure>summary{min-height:var(--g9-touch-min);overflow-wrap:anywhere}
.g9-secondary-disclosure>summary{min-height:var(--g9-touch-min);min-width:0;display:flex;align-items:center;flex-wrap:wrap;overflow-wrap:anywhere;padding:10px 12px;font-weight:800;cursor:pointer}
.g9-secondary-disclosure>summary::after{content:"+";margin-left:auto;font-size:1.2em}.g9-secondary-disclosure[open]>summary::after{content:"−"}
.g9-secondary-body{padding:0 12px 12px}
.g9-worked-instruction{margin:.35rem 0 .6rem;color:var(--muted);font-weight:650}
.g9-watch-steps{padding-left:1.35rem}.g9-watch-steps>li{margin:.65rem 0}
.g9-worked-step{border:1px solid var(--line);border-radius:10px;background:var(--card);overflow:hidden}
.g9-worked-step>summary{min-height:var(--g9-touch-min);display:flex;align-items:center;padding:9px 11px;font-weight:750;cursor:pointer}
.g9-worked-step-body{padding:0 11px 11px}.g9-worked-step-body p{margin:.3rem 0}
article[data-g9-unit]>.slot-identity{padding:0 0 12px;margin-bottom:16px;border-bottom:1px solid var(--line)}
.g9-c-header h2,.g9-c-concept-header h2{font-size:1.2rem;line-height:1.3;margin:0;letter-spacing:-.01em}
.g9-c-header .g9-prov{margin:2px 0 0}
.g9-c-disclosure-grid{margin-top:0}
.g9-c-unit-header{margin-top:0}
.g9-why-toggle{margin-top:10px;gap:4px 10px;flex-wrap:wrap;max-width:100%;text-align:left;justify-content:flex-start;border:0;background:transparent;padding:6px 0;font-weight:700;color:var(--muted)}
.g9-pill-band{background:#fff7ed;color:#9a3412}.g9-pill-band[data-g9-band=D1]{background:#ecfdf5;color:#047857}.g9-pill-band[data-g9-band=D2]{background:#eff6ff;color:#1d4ed8}.g9-pill-band[data-g9-band=D4]{background:#fdf2f8;color:#be185d}
:root[data-theme=dark] .g9-pill-band{background:#3a2a14;color:#fdba74}:root[data-theme=dark] .g9-pill-band[data-g9-band=D1]{background:#12301f;color:#6ee7b7}:root[data-theme=dark] .g9-pill-band[data-g9-band=D2]{background:#172a4d;color:#9ec5ff}:root[data-theme=dark] .g9-pill-band[data-g9-band=D4]{background:#3a1830;color:#f9a8d4}
.g9-why{margin-top:6px}.g9-why p{margin:.2rem 0 .6rem;color:var(--muted)}
.g9-dgrid{display:grid;grid-template-columns:repeat(5,minmax(0,1fr));gap:8px}
.g9-dcell{background:var(--soft);border:1px solid var(--line);border-radius:10px;padding:8px 10px;font-size:max(.85rem,14px);color:var(--muted)}.g9-dcell b{display:block;color:var(--fg);font-size:1rem}
.g9-c-stem [data-g9-block=stem] p{margin:.1rem 0;font-size:1.12rem;line-height:1.58;font-weight:560;white-space:pre-line}
.g9-c-callout-info{border-left:4px solid var(--info-line);background:var(--info-bg);padding:10px 14px;border-radius:0 12px 12px 0;color:var(--info-fg)}
.g9-c-callout-warn{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:12px;padding:10px 14px;color:var(--warn-fg)}
.g9-c-callout-info h4,.g9-c-callout-warn h4{margin:0 0 .2rem;font-size:1rem}.g9-c-callout-warn h4{color:var(--warn-fg)}
.g9-c-callout-info ul{margin:.2rem 0;padding-left:1.2rem}.g9-c-callout-info p,.g9-c-callout-warn p{margin:.1rem 0}
.g9-bridge-link{color:var(--accent);font-weight:700;text-decoration:underline;text-underline-offset:3px;white-space:normal;overflow-wrap:anywhere;max-width:100%;min-width:0}
.g9-crux-tag{display:inline-block;margin:0 0 4px;padding:1px 10px;border-radius:999px;background:var(--pill-bg);color:var(--pill-fg);font-size:max(.85rem,14px);font-weight:800}
.g9-c-step-cards [data-g9-block=construction] ol>li[data-g9-crux-step]{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}
.g9-lines{white-space:pre-line}
.g9-cu-support>h3{position:absolute;width:1px;height:1px;margin:-1px;padding:0;overflow:hidden;clip:rect(0 0 0 0);white-space:normal;overflow-wrap:anywhere}
.g9-c-attempt .g9-attempt{border:1px solid var(--line);border-radius:14px;padding:12px 14px;background:var(--soft)}
.g9-answer-options{display:grid;gap:8px;counter-reset:g9opt}
.g9-answer-option{border:1px solid var(--line);background:var(--card);border-radius:12px;padding:6px 12px}
.g9-answer-option::before{counter-increment:g9opt;content:"(" counter(g9opt,upper-alpha) ")";font-weight:850;color:var(--accent);order:1;min-width:2.2rem}
.g9-answer-option input{order:0}.g9-answer-option>span{order:2}
.g9-c-visual-card,.g9-c-staged-visual{border:1px solid var(--line);border-radius:16px;background:var(--soft);padding:10px 12px 12px}
.g9-card-head{display:flex;justify-content:space-between;gap:10px;align-items:center;margin-bottom:6px}.g9-card-head strong{font-size:.9rem}
.g9-c-visual-card figure,.g9-c-staged-visual figure{margin:0}
.g9-c-visual-card figure svg,.g9-c-staged-visual figure svg{display:block;width:100%;height:auto;max-width:100%}
.g9-c-visual-card figure svg{max-height:min(48vh,440px)}.g9-c-staged-visual figure svg{max-height:min(42vh,360px)}
.g9-diagram-scroll{width:100%;max-width:100%;min-width:0;min-height:48px;box-sizing:border-box;overflow-x:auto}
.g9-diagram-scroll svg{display:block;max-height:none!important;max-width:none!important}
.g9-c-ladder .g9-block>h4{margin:.9rem 0 .2rem;font-size:max(.85rem,14px);color:var(--muted)}
.g9-rung-map,.g9-c-ladder [data-g9-ladder]{list-style:none;margin:8px 0 0;padding:0;display:grid;gap:8px}
.g9-rung-map>li{border:1px dashed var(--line);border-radius:12px;padding:9px 13px;color:var(--muted)}
.g9-c-ladder [data-g9-ladder]>li{border:1px solid var(--line);border-radius:12px;background:var(--card);padding:10px 13px}
.g9-rung-head{display:flex;gap:10px;align-items:center;flex-wrap:wrap;font-weight:800}
.g9-rung-no{display:inline-grid;place-items:center;min-width:2.3em;height:2.1em;border-radius:8px;background:var(--pill-bg);color:var(--pill-fg);font-size:max(.85rem,14px)}
.g9-c-ladder details[data-g9-support-reveal]{border:0;padding:0;margin:.5rem 0}
.g9-c-ladder details[data-g9-support-reveal]>summary{width:100%;justify-content:space-between;font-weight:700}
.g9-c-ladder [data-g9-support-prompt]{margin:.5rem 0}.g9-c-ladder .g9-ladder>button{margin-top:10px}
.g9-pdf-link{gap:6px;font-weight:700}.g9-pdf-icon{flex:none;width:24px;height:24px}.g9-pdf-link span{white-space:nowrap}header .g9-pdf-link{color:var(--accent)}.g9-c-link-list .g9-source-pdf{border-radius:12px}
.g9-c-link-list h4{margin:.9rem 0 .3rem;font-size:max(.85rem,14px);color:var(--muted)}
.g9-c-link-list ul{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:.2rem 0;padding:0}
.g9-c-link-list li{margin:0;min-width:0;max-width:100%}.g9-c-link-list a{display:inline-flex;align-items:center;min-height:48px;max-width:100%;min-width:0;box-sizing:border-box;padding:6px 14px;border:1px solid var(--line);border-radius:999px;background:var(--card);color:var(--fg);text-decoration:none;white-space:normal;overflow-wrap:anywhere}
.g9-c-disclosure>details{border:1px solid var(--line);border-radius:14px;background:var(--soft);padding:0;overflow:hidden;margin:0}
.g9-c-disclosure>details>summary{list-style:none;display:flex;width:100%;justify-content:space-between;border:0;border-radius:0;background:transparent;padding:13px 15px;font-weight:850;min-height:48px}
.g9-c-disclosure>details>summary::-webkit-details-marker{display:none}
.g9-c-disclosure>details>summary::after{content:"Show";font-size:max(.85rem,14px);background:var(--pill-bg);color:var(--pill-fg);padding:4px 10px;border-radius:999px}
.g9-c-disclosure>details[open]>summary::after{content:"Hide"}.g9-c-disclosure>details[data-locked]>summary::after{content:"After you attempt"}
.g9-c-disclosure>details[open]>summary{border-bottom:1px solid var(--line);background:var(--card)}
.g9-c-disclosure [data-g9-payload-slot]{padding:6px 16px 16px}
.g9-solution-move{display:grid;grid-template-columns:42px minmax(0,1fr);gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
.g9-solution-move:last-child{border-bottom:0}
.g9-step-no{font-weight:850;font-size:.9rem;color:var(--pill-fg);background:var(--pill-bg);border-radius:8px;padding:5px 6px;text-align:center;height:max-content}
.g9-step-body [data-g9-block=solution_inputs]{display:flex;flex-wrap:wrap;gap:.4rem;align-items:baseline;color:var(--muted)}
.g9-step-body [data-g9-block=solution_inputs] h4{margin:0}
.g9-step-body [data-g9-block=solution_inputs] ul{display:flex;flex-wrap:wrap;gap:.4rem;list-style:none;margin:0;padding:0}
.g9-step-body [data-g9-block=solution_inputs] li{border:1px solid var(--line);border-radius:999px;padding:1px 10px;font-size:max(.85rem,14px)}
.g9-step-body p{margin:.25rem 0}.g9-step-body h4{margin:0;font-size:max(.85rem,14px);color:var(--muted)}
.g9-solution-move[data-g9-solution-crux=true]{background:var(--info-bg);border-radius:10px;padding-left:8px;padding-right:8px}
.g9-c-step-list [data-g9-block=working] ol{list-style:none;padding:0;margin:0;counter-reset:g9s}
.g9-c-step-list [data-g9-block=working] ol>li{counter-increment:g9s;display:grid;grid-template-columns:42px minmax(0,1fr);gap:12px;padding:10px 0;border-bottom:1px solid var(--line)}
.g9-c-step-list [data-g9-block=working] ol>li::before{content:counter(g9s);font-weight:850;font-size:.9rem;color:var(--pill-fg);background:var(--pill-bg);border-radius:8px;padding:5px 6px;text-align:center;height:max-content}
.g9-c-answer-box{background:var(--ok-bg);border:1px solid var(--ok-line);border-radius:12px;padding:10px 14px;color:var(--ok-fg)}
.g9-c-answer-box p{margin:.15rem 0}.g9-c-answer-box h4{margin:0 0 .2rem;font-size:max(.85rem,14px)}
.g9-c-check-box{border-left:4px solid var(--ok-line);padding:4px 14px;color:var(--ok-fg)}.g9-c-check-box h4{margin:0;font-size:max(.85rem,14px)}.g9-c-check-box p{margin:.15rem 0}
.g9-c-tile,.g9-c-recall-card{border:1px solid var(--line);border-radius:14px;background:var(--soft);padding:12px 16px}
.g9-c-tile h4,.g9-c-recall-card h4{margin:0 0 .3rem}.g9-c-tile ul{margin:.2rem 0;padding-left:1.2rem}
.g9-c-banner{border-left:5px solid var(--accent);background:var(--info-bg);padding:12px 16px;border-radius:0 14px 14px 0}.g9-c-banner h4{margin:0 0 .2rem;color:var(--accent)}.g9-c-banner p{margin:.1rem 0}
.g9-unit-head{display:flex;gap:12px;align-items:center;flex-wrap:wrap}
.g9-unit-no{display:inline-grid;place-items:center;width:2.3em;height:2.3em;border-radius:50%;background:var(--accent);color:var(--card);font-weight:850}
.g9-unit-head h3{margin:0;flex:1 1 12rem;font-size:1.12rem;line-height:1.35}.g9-pill-concept{background:var(--info-bg);color:var(--info-fg);border:1px solid var(--info-line)}
.g9-concept-first{border:2px solid var(--accent);border-radius:14px;padding:14px 18px;margin:12px 0;background:var(--soft);line-height:1.65}
.g9-concept-first fieldset{border:1px solid var(--line);border-radius:9px;padding:10px;margin:12px 0}
.g9-concept-first fieldset label{display:inline-flex;align-items:center;gap:8px;padding:8px 12px;min-height:44px}
.g9-concept-first textarea{display:block;width:100%;max-width:64ch;min-height:84px;margin:6px 0 12px}
.g9-concept-first button{min-height:44px;padding:8px 14px;border-radius:8px}
[data-g9-concept-target][hidden],[data-g9-assistance-status][hidden]{display:none!important}
@media print{[data-g9-concept-target][hidden]{display:block!important}}
.g9-c-step-cards [data-g9-block=construction] ol{list-style:none;margin:0;padding:0;counter-reset:g9c;display:grid;grid-template-columns:minmax(0,1fr);gap:10px}
.g9-c-step-cards [data-g9-block=construction] ol>li{counter-increment:g9c;position:relative;border:1px solid var(--line);border-radius:14px;background:var(--card);padding:12px 14px 12px 54px;min-width:0;overflow-wrap:anywhere}
.g9-c-step-cards [data-g9-block=construction] ol>li::before{content:counter(g9c);position:absolute;left:14px;top:12px;display:grid;place-items:center;width:1.9em;height:1.9em;border-radius:50%;background:var(--pill-bg);color:var(--pill-fg);font-weight:850;font-size:.9rem}
.g9-c-step-cards li em{display:inline-block;min-width:5.6rem;color:var(--muted);font-style:normal;font-weight:700}
.g9-c-step-cards li br{display:block;content:"";margin-top:.3rem}
.g9-c-equation-card,.g9-c-worked-card{border:1px solid var(--line);border-radius:14px;background:var(--soft);padding:10px 14px}
.g9-c-worked-card{border-left:4px solid var(--accent)}.g9-c-worked-card [data-g9-block=worked_anchor]{border-left:0;padding-left:0}
.g9-c-trap-card{background:var(--warn-bg);border:1px solid var(--warn-line);border-radius:14px;padding:10px 14px;color:var(--warn-fg)}
.g9-c-trap-card [data-g9-block]{border-left:0;padding-left:0}.g9-c-trap-card h4{margin:.5rem 0 .1rem;font-size:max(.85rem,14px)}
.g9-c-trap-card ul{margin:.1rem 0;padding-left:1.2rem}
.g9-c-triad{border:1px solid var(--line);border-radius:14px;background:var(--soft);padding:10px 14px}
.g9-c-triad h4{margin:0 0 .4rem;font-size:max(.85rem,14px);text-transform:uppercase;letter-spacing:.05em;color:var(--muted)}
.g9-triad{list-style:none;margin:0;padding:0;display:grid;gap:8px}
.g9-triad>li{display:grid;gap:2px;border-left:4px solid var(--line);padding:2px 0 2px 10px}
.g9-triad>li[data-g9-triad-role=CHECK]{border-color:var(--info-line)}.g9-triad>li[data-g9-triad-role=APPLY]{border-color:var(--ok-line)}.g9-triad>li[data-g9-triad-role=CONNECT]{border-color:var(--pill-fg)}
.g9-triad-head{font-size:max(.85rem,14px);font-weight:800;letter-spacing:.04em;text-transform:uppercase;color:var(--muted)}
.g9-c-chips ul,.g9-c-chips ol{display:flex;flex-wrap:wrap;gap:8px;list-style:none;margin:.3rem 0;padding:0}
.g9-c-chips li{margin:0}
.g9-c-chips a{border:1px solid var(--line);border-radius:999px;background:var(--card);padding:6px 14px;min-height:48px;display:inline-flex;align-items:center;text-decoration:none;color:var(--fg)}
/* 12.7-inch tablet: the identity block is a title row and a chip row, so the first screen shows the work and not the labels */
article[data-g9-role=CORE2]>.slot-identity,article[data-g9-role=CORE1A]>.slot-identity{display:flex;flex-wrap:wrap;align-items:center;gap:4px 16px;padding:0 0 8px;margin-bottom:12px}
article[data-g9-role=CORE2]>.slot-identity>.g9-component,article[data-g9-role=CORE1A]>.slot-identity>.g9-component{display:contents}
article[data-g9-role=CORE2]>.slot-identity [data-g9-block=source_identity]{order:1;flex:1 1 16rem;display:flex;align-items:baseline;flex-wrap:wrap;gap:0 14px;min-width:0}
article[data-g9-role=CORE2]>.slot-identity [data-g9-block=source_identity] h2,article[data-g9-role=CORE1A]>.slot-identity h2{margin:0}
article[data-g9-role=CORE2]>.slot-identity [data-g9-block=source_identity] .g9-prov{margin:0}
article[data-g9-role=CORE2]>.slot-identity .g9-why-toggle{order:2;margin:0;padding:2px 0;min-height:var(--g9-touch-min)}
article[data-g9-role=CORE2]>.slot-identity [data-g9-meta-strip],article[data-g9-role=CORE1A]>.slot-identity [data-g9-meta-strip]{order:3;flex:1 0 100%;margin:0;gap:6px}
article[data-g9-role=CORE2]>.slot-identity .g9-why{order:4;flex:1 0 100%}
article[data-g9-role=CORE1A]>.slot-identity h2{order:1;flex:1 1 auto}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-block=section_route]{order:4;flex:1 0 100%;display:flex;align-items:center;gap:6px 12px;flex-wrap:wrap}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-block=section_route] h4{margin:0;white-space:nowrap}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-section-route] ol{display:flex;flex-wrap:wrap;gap:6px;margin:0;padding:0;list-style:none}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-section-route] li{margin:0}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-section-route] a{display:inline-block;width:auto;max-width:24rem;padding:4px 14px;border-radius:999px;line-height:38px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-component=SECTION_ROUTE]{flex:1 1 100%;width:100%;min-width:0}
article[data-g9-role=CORE1A]>.slot-identity [data-g9-section-route] a{max-width:100%;white-space:normal;overflow-wrap:anywhere}
article[data-g9-role=CORE2]>.slot-identity [data-g9-meta-item],article[data-g9-role=CORE1A]>.slot-identity [data-g9-meta-item]{padding:2px 10px;line-height:1.35}
.g9-interactive-bridge{border:2px solid var(--accent);border-radius:16px;background:var(--card);padding:16px 20px;margin:18px 0}
.g9-interactive-bridge h3{margin:8px 0 4px;font-size:1.15rem;color:var(--fg)}
.g9-interactive-desc{color:var(--muted);font-size:.92rem;margin:0 0 12px}
.g9-action-interactive{display:inline-flex;align-items:center;min-height:var(--g9-touch-min);padding:8px 16px;border-radius:10px;background:var(--accent);color:#fff;text-decoration:none;font-weight:700}
.g9-action-interactive:hover{opacity:.95}
.g9-transitions-row{display:flex;flex-wrap:wrap;gap:12px;margin:10px 0}
.g9-transition-chip{display:inline-flex;align-items:center;min-height:var(--g9-touch-min);padding:8px 16px;border:1px solid var(--line);border-radius:12px;background:var(--card);color:var(--accent);font-weight:700;text-decoration:none}
.g9-transition-chip:hover{background:var(--soft);border-color:var(--accent)}
"""


def layout_css(registry: dict) -> str:
    """The layout of every blueprint, written from the blueprint's own columns, fractions and component order.

    Expanded: the primary and support columns side by side (the support column pinned, and scrolling inside itself when it is
    taller than the screen, where the blueprint says so). Narrower: one column in the blueprint's compact order, whichever
    column each component sits in, so a picture follows the question it belongs to and the ladder follows the attempt."""
    out = []
    for bp in registry.get("blueprints") or []:
        rp = bp.get("responsive_policy") or {}
        if rp.get("expanded") != "STAGE_SUPPORT" or not rp.get("support_fraction"):
            continue
        role = bp["core_roles"][0]
        if role not in ROLES:
            continue                 # the explorer lays itself out from the same blueprint fields (Shared/tools/explorer_build.py)
        scope = f'article[data-g9-role="{role}"]'
        columns = f'minmax(0,{rp["primary_fraction"] * 100:g}fr) minmax(0,{rp["support_fraction"] * 100:g}fr)'
        wide = (f'{scope} .g9-split{{display:grid;grid-template-columns:{columns};gap:22px;align-items:start}}'
                f'{scope} .g9-split-primary-only,{scope} .g9-split-support-only{{grid-template-columns:minmax(0,1fr)}}')
        if rp.get("support_sticky"):
            pinned = "position:sticky;top:80px"
            if (rp.get("tablet_12_7") or {}).get("support_scrolls_inside"):
                pinned += ";max-height:calc(100vh - 96px);overflow-y:auto;overscroll-behavior:contain"
            wide += f'{scope} .g9-split:not(.g9-split-support-only)>.g9-col-support{{{pinned}}}'
        expanded_min = rp.get("expanded_min_px", 1100)
        out.append(f'@media (min-width:{expanded_min}px){{{wide}}}')
        order = [(c["id"], c["compact_order"]) for c in blueprints_api.components(bp) if isinstance(c.get("compact_order"), int)]
        if order:
            flat = (f'{scope} .g9-split{{display:flex;flex-direction:column}}'
                    f'{scope} .g9-split .g9-col,{scope} .g9-split .blueprint-slot,{scope} .g9-split .g9-cu,'
                    f'{scope} .g9-split .g9-cu-support{{display:contents}}')
            flat += "".join(f'{scope} [data-g9-component="{cid}"]{{order:{n}}}' for cid, n in order)
            out.append(f'@media (max-width:{expanded_min - 1}px){{{flat}}}')
        out.append(f'@media print{{{scope} .g9-split{{display:grid;grid-template-columns:{columns};gap:12px}}}}')
    return "".join(out)


JS = r"""
(()=>{const q=(s,r=document)=>[...r.querySelectorAll(s)];
const store={get:k=>{try{return localStorage.getItem('g9-'+k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem('g9-'+k,v);return true}catch(e){return false}},remove:k=>{try{localStorage.removeItem('g9-'+k);return true}catch(e){return false}}};
const root=document.documentElement;const scope=root.dataset.g9Product&&root.dataset.g9RenderDigest?root.dataset.g9Product+':'+root.dataset.g9RenderDigest:'';
const shell=document.querySelector('.g9-shell-header');if(shell){const offset=()=>root.style.setProperty('--g9-header-offset',(shell.getBoundingClientRect().height+16)+'px');new ResizeObserver(offset).observe(shell);offset();}
const apply=()=>{root.dataset.theme=store.get('theme')||root.dataset.theme||'light';root.style.setProperty('--g9-zoom',store.get('zoom')||'1');};apply();
q('[data-g9-theme]').forEach(b=>b.onclick=()=>{store.set('theme',b.dataset.g9Theme);apply()});
q('[data-g9-zoom]').forEach(b=>b.onclick=()=>{let z=parseFloat(store.get('zoom')||'1');z=b.dataset.g9Zoom==='inc'?Math.min(1.6,z+0.1):b.dataset.g9Zoom==='dec'?Math.max(0.8,z-0.1):1;store.set('zoom',z.toFixed(1));apply()});
q('[data-g9-font]').forEach(b=>b.onclick=()=>q('[data-g9-zoom="'+b.dataset.g9Font+'"]')[0]?.click());
function fitFigure(f){const svg=q('svg',f)[0];if(!svg||!svg.isConnected)return;const groups=q('[data-g9-stage-id]',svg).filter(g=>getComputedStyle(g).display!=='none');if(groups.length){const boxes=groups.map(g=>g.getBBox()).filter(b=>b.width>0&&b.height>0);if(boxes.length){const x=Math.min(...boxes.map(b=>b.x))-12,y=Math.min(...boxes.map(b=>b.y))-12,r=Math.max(...boxes.map(b=>b.x+b.width))+12,b=Math.max(...boxes.map(b=>b.y+b.height))+12;svg.setAttribute('viewBox',[x,y,r-x,b-y].join(' '));}}
const host=svg.parentElement;const labels=q('text',svg).filter(t=>t.checkVisibility({visibilityProperty:true}));const min=labels.reduce((v,t)=>Math.min(v,parseFloat(getComputedStyle(t).fontSize)||Infinity),Infinity);const box=svg.viewBox.baseVal;const floor=Number(f.dataset.g9MinFigureText)||14;const needed=Number.isFinite(min)&&min>0?Math.ceil(box.width*floor/min):0;svg.style.width=Math.max(host.clientWidth,needed)+'px';}
function initFigure(f){if(f.dataset.g9Init)return;f.dataset.g9Init='1';const ids=(f.dataset.g9Stages||'').split(' ').filter(Boolean);fitFigure(f);const host=q('.g9-diagram-scroll',f)[0];if(host){let width=host.clientWidth;new ResizeObserver(()=>{const next=host.clientWidth;if(next!==width){width=next;fitFigure(f)}}).observe(host)}if(ids.length<2)return;let i=0;
const chips=q('[data-g9-stage-goto]',f);const desc=q('[data-g9-stage-desc-text]',f)[0];
const stageMode=f.dataset.g9StageMode||'cumulative';const cumulative=stageMode!=='replace';
ids.forEach(id=>q('[data-g9-stage-id="'+id+'"]',f).forEach(g=>g.style.display='none'));
const show=()=>{ids.forEach((id,n)=>q('[data-g9-stage-id="'+id+'"]',f).forEach(g=>g.style.display=(cumulative?n<=i:n===i)?'':'none'));fitFigure(f);const l=q('[data-g9-stage-label]',f)[0];if(l)l.textContent='Stage '+(i+1)+' of '+ids.length;chips.forEach((c,n)=>c.setAttribute('aria-pressed',String(n===i)));if(desc)desc.textContent=(chips[i]&&chips[i].dataset.g9StageDesc)||''};show();chips.forEach((c,n)=>c.onclick=()=>{i=n;show()});
q('[data-g9-stage-step]',f).forEach(b=>b.onclick=()=>{i=Math.max(0,Math.min(ids.length-1,i+(b.dataset.g9StageStep==='next'?1:-1)));show()})}
function nextRung(l){const t=q('template[data-g9-rung-payload]',l)[0];if(!t)return false;const payload=t.content.cloneNode(true);q('[data-g9-rung-ghost]',l)[0]?.remove();q('[data-g9-ladder]',l)[0].append(payload);q('figure[data-g9-figure]',l).forEach(initFigure);t.remove();const b=q('[data-g9-next-rung]',l)[0];if(b){if(!q('template[data-g9-rung-payload]',l).length)b.disabled=true;else b.textContent='Show next support'}return true}
function materialise(a){q('details[data-g9-payload-ref]',a).forEach(d=>{const slot=q('[data-g9-payload-slot]',d)[0];if(!slot||slot.dataset.g9Filled)return;const t=q('template[data-g9-payload]',a).find(x=>x.dataset.g9Payload===d.dataset.g9PayloadRef);if(!t)return;slot.replaceChildren(t.content.cloneNode(true));slot.dataset.g9Filled='1';q('figure[data-g9-figure]',slot).forEach(initFigure)})}
const number=t=>{const v=t.trim();if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?(?:\s*\/\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)?$/i.test(v))return false;const p=v.split('/').map(x=>Number(x.trim()));return p.every(Number.isFinite)&&(p.length===1||p[1]!==0)};
function validAttempt(box){const type=box.dataset.g9ResponseType;if(type==='single_choice'||type==='multiple_choice'||type==='true_false')return q('[data-g9-choice]:checked',box).length>0;
if(type==='numeric')return number(q('[data-g9-number]',box)[0]?.value||'');if(type==='short_text')return !!q('[data-g9-attempt]',box)[0]?.value.trim();
if(type==='match'){const fields=q('[data-g9-match]',box);return fields.length>0&&fields.every(x=>x.value!=='')}
if(q('[data-g9-paper]:checked',box).length)return true;if(type==='multipart'){const fields=q('[data-g9-part-input]',box);return fields.length>0&&fields.every(x=>x.value.trim()&&(!x.dataset.g9PartType||x.dataset.g9PartType!=='numeric'||number(x.value)))}
return !!q('[data-g9-attempt]',box)[0]?.value.trim()}
const stateKey=a=>scope&&a?.dataset.g9Unit?'state:'+scope+':'+a.dataset.g9Unit:null;const returnKey=concept=>scope&&concept?'return:'+scope+':'+concept:null;
function readState(key){if(!key)return null;const raw=store.get(key);if(!raw)return null;try{const state=JSON.parse(raw);return state&&typeof state==='object'?state:null}catch(e){return null}}
const attemptFields=a=>q('[data-g9-attempt-box] input,[data-g9-attempt-box] textarea,[data-g9-attempt-box] select',a);const rungCount=l=>{const list=q('[data-g9-ladder]',l)[0];return list?q('[data-g9-rung]',list).length:0};
const assistanceOf=a=>(a.dataset.g9Assistance||'').split(',').filter(Boolean);
function assistanceLabel(a){q('[data-g9-assistance-status]',a).forEach(el=>el.hidden=!a.dataset.g9Assisted)}
function markAssistance(a,kind){if(!['CORE2','CORE2A'].includes(a.dataset.g9Role)||!kind)return;const kinds=new Set(assistanceOf(a));kinds.add(kind);a.dataset.g9Assistance=Array.from(kinds).join(',');a.dataset.g9Assisted='1';assistanceLabel(a)}
function saveCore2State(a){if(!['CORE2','CORE2A'].includes(a.dataset.g9Role))return;const key=stateKey(a);if(!key)return;const fields=attemptFields(a).map(el=>({value:el.value,checked:!!el.checked}));const ladders={};q('.g9-ladder[data-g9-ladder-ref]',a).forEach(l=>ladders[l.dataset.g9LadderRef]=rungCount(l));const reveals=q('details[data-g9-support-reveal]',a).map(d=>!!d.open);const assistance=assistanceOf(a);store.set(key,JSON.stringify({attempted:!!a.dataset.attempted,assisted:!!a.dataset.g9Assisted,assistance,fields,ladders,reveals}))}
function bindSupportRevealState(a){q('details[data-g9-support-reveal]',a).forEach(d=>{if(d.dataset.g9StateBound)return;d.dataset.g9StateBound='1';d.addEventListener('toggle',()=>saveCore2State(a))})}
function restoreCore2State(a,lock){if(!['CORE2','CORE2A'].includes(a.dataset.g9Role))return;const state=readState(stateKey(a));if(!state)return;const fields=attemptFields(a);(state.fields||[]).forEach((saved,i)=>{const el=fields[i];if(!el||!saved||typeof saved!=='object')return;if(Object.prototype.hasOwnProperty.call(saved,'value'))el.value=saved.value??'';if(el.type==='checkbox'||el.type==='radio')el.checked=!!saved.checked});Object.entries(state.ladders||{}).forEach(([ref,count])=>{const l=q('.g9-ladder[data-g9-ladder-ref]',a).find(x=>x.dataset.g9LadderRef===ref);if(!l||!Number.isInteger(count)||count<0)return;while(rungCount(l)<count&&nextRung(l)){};});bindSupportRevealState(a);q('details[data-g9-support-reveal]',a).forEach((d,i)=>d.open=!!(state.reveals||[])[i]);if(state.assisted){a.dataset.g9Assisted='1';a.dataset.g9Assistance=(Array.isArray(state.assistance)?state.assistance:[]).filter(v=>typeof v==='string').join(',')}if(state.attempted){a.dataset.attempted='1';materialise(a)}assistanceLabel(a);lock()}
const articles=q('article[data-g9-unit],article[data-g9-diagnostic],[data-g9-purpose-item]');
articles.forEach(a=>{const lock=()=>q('details[data-requires-attempt]',a).forEach(d=>{if(!a.dataset.attempted){d.dataset.locked='';d.open=false}else delete d.dataset.locked});lock();restoreCore2State(a,lock);
q('details[data-requires-attempt] summary',a).forEach(s=>s.addEventListener('click',e=>{if(!a.dataset.attempted){e.preventDefault();q('[data-g9-attempt-box] input,[data-g9-attempt-box] textarea,[data-g9-attempt-box] select',a)[0]?.focus()}}));
q('[data-g9-commit]',a).forEach(b=>b.onclick=()=>{const box=b.closest('[data-g9-attempt-box]');if(!box||!validAttempt(box)){q('input,textarea,select',box||a)[0]?.focus();return}a.dataset.attempted='1';lock();materialise(a);saveCore2State(a)});
a.addEventListener('click',e=>{const b=e.target.closest('[data-g9-next-rung]');if(b&&a.contains(b)){markAssistance(a,'HINT_LADDER');nextRung(b.closest('.g9-ladder'));bindSupportRevealState(a);saveCore2State(a)}});attemptFields(a).forEach(el=>{el.addEventListener('input',()=>saveCore2State(a));el.addEventListener('change',()=>saveCore2State(a))});
q('details[data-g9-payload-ref$="-wrong-route"]',a).forEach(d=>d.addEventListener('toggle',()=>{if(d.open){markAssistance(a,'WRONG_ROUTE');saveCore2State(a)}}));
q('[data-g9-concept-link]',a).forEach(link=>link.addEventListener('click',()=>{markAssistance(a,'CONCEPT_NAV');saveCore2State(a);const key=returnKey(link.dataset.g9ConceptRef);if(key)store.set(key,link.dataset.g9QuestionRef||a.dataset.g9Unit);refreshReturnLinks()}))});
// An opt-in, TEST-only formative concept checkpoint: verify a choice and
// a minimal rule-oriented rationale before showing the guided lesson.
// A keyword/radio check is NOT a knowledge score, mastery or secure receipt.
q('[data-g9-concept-check]').forEach(c=>{
  const article=c.closest('article[data-g9-role="CORE1A"]');
  const b=q('[data-g9-concept-commit]',c)[0];
  const feedback=q('[data-g9-concept-feedback]',c)[0];
  if(!article||!b||!feedback)return;
  b.addEventListener('click',()=>{
    const choice=q('[data-g9-concept-option]:checked',c)[0]?.value||'';
    const reason=(q('[data-g9-concept-reason]',c)[0]?.value||'').trim().toLowerCase();
    const match=(s)=>s.split(',').some(w=>w&&reason.includes(w));
    if(choice!==c.dataset.g9ConceptCorrect){feedback.textContent=c.dataset.g9FeedbackChoice;return}
    if(reason.length<15||!match(c.dataset.g9ReasonWords||'')||!match(c.dataset.g9RuleWords||'')){
      feedback.textContent=c.dataset.g9FeedbackExplain;return
    }
    article.dataset.g9ConceptCheckCompleted='formative_only';
    q('[data-g9-concept-target]',article).forEach(el=>{el.hidden=false});
    feedback.textContent=c.dataset.g9FeedbackPassed;
    q('figure[data-g9-figure]',article).forEach(fitFigure);
    q('[data-g9-concept-target] h3,[data-g9-concept-target] h4',article)[0]?.setAttribute('tabindex','-1');
    q('[data-g9-concept-target] h3,[data-g9-concept-target] h4',article)[0]?.focus();
  })
});
const practiceLinks=q('[data-g9-practice-link]');const practiceLabels=new Map(practiceLinks.map(link=>[link,link.textContent]));const navParams=new URLSearchParams(location.search);const navReturn=navParams.get('g9-return');const navConcept=navParams.get('g9-concept');
function refreshReturnLinks(){practiceLinks.forEach(link=>{const key=returnKey(link.dataset.g9ConceptRef);const stored=!!key&&store.get(key)===link.dataset.g9QuestionRef;const routed=navReturn===link.dataset.g9QuestionRef&&navConcept===link.dataset.g9ConceptRef;const active=stored||routed;if(active){link.dataset.g9ReturnLink='';link.textContent='Return to question · '+practiceLabels.get(link)}else{delete link.dataset.g9ReturnLink;link.textContent=practiceLabels.get(link)}})}
practiceLinks.forEach(link=>link.addEventListener('click',()=>{const key=returnKey(link.dataset.g9ConceptRef);if(key&&store.get(key)===link.dataset.g9QuestionRef)store.remove(key);refreshReturnLinks()}));refreshReturnLinks();
window.g9MaterialiseAll=()=>{q('[data-g9-concept-target]').forEach(el=>el.hidden=false);articles.forEach(a=>{a.dataset.attempted='1';q('details[data-requires-attempt]',a).forEach(d=>delete d.dataset.locked);materialise(a);q('.g9-ladder',a).forEach(l=>{while(nextRung(l)){};});q('details[data-g9-support-reveal]',a).forEach(d=>d.open=true)})};
q('figure[data-g9-figure]').forEach(initFigure);
q('[data-g9-toggle]').forEach(b=>b.onclick=()=>{const t=document.getElementById(b.getAttribute('aria-controls'));if(!t)return;const open=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',String(!open));t.hidden=open});
const input=q('[data-g9-search-input]')[0];if(input)input.oninput=()=>{const v=input.value.trim().toLowerCase();articles.forEach(a=>{a.hidden=!!v&&!(a.dataset.g9SearchText||'').toLowerCase().includes(v)})};
q('[data-g9-action="search"]').forEach(b=>b.onclick=()=>{const p=q('[data-g9-search-panel]')[0];p.hidden=!p.hidden;if(!p.hidden)input.focus()});
q('[data-g9-action="display"]').forEach(b=>b.onclick=()=>{const p=q('[data-g9-display-panel]')[0];p.hidden=!p.hidden});
})();
"""


def _mode_href(href: str, mode: str) -> str:
    """Rebase public-root-relative links for the governed standalone publication path."""
    if mode == "SINGLE_FILE" and href.startswith("../../../"):
        return "../../../public/" + href[len("../../../"):]
    return href


# A page of a document: the corner folded, three lines of text. Decorative; the word "PDF" beside it is what says what the control is.
PDF_ICON = ('<svg class="g9-pdf-icon" aria-hidden="true" focusable="false" viewBox="0 0 24 24" width="24" height="24">'
            '<path d="M6 2.5h8l4.5 4.5v14.5H6z" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linejoin="round"/>'
            '<path d="M14 2.5V7h4.5M9 12h6.5M9 15.5h6.5M9 19h4" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/></svg>')
PDF_ACCESSIBLE_NAME = "Open the PDF of this page to print it"
SOURCE_PDF_ACCESSIBLE_NAME = "Open the original past paper as a PDF to print it"


def pdf_control(href: str, accessible_name: str = PDF_ACCESSIBLE_NAME) -> str:
    """The shell's PRINT_PDF control (Shared/web/interactive-page-blueprints.v1.json, shell.print_policy): the PDF printed from this page."""
    return (f'<a data-g9-action="pdf" class="g9-pdf-link" href="{esc(href)}" target="_blank" rel="noopener" type="application/pdf" '
            f'aria-label="{esc(accessible_name)}">{PDF_ICON}<span>PDF</span></a>')


def shell_header(home_href: str, question_bank_href: str, pdf_href: str | None = None, pdf_name: str = PDF_ACCESSIBLE_NAME, portal_root: str | None = None) -> str:
    """The shared tablet-shell header. Used by every rendered page."""
    pdf_btn = f'<a class="g9-header-btn g9-pdf-link" data-g9-action="pdf" data-g9-pdf-link aria-label="{esc(pdf_name)}" href="{esc(pdf_href)}" title="{esc(pdf_name)}">PDF</a>' if pdf_href else ""
    subjects = ''.join(f'<a href="{esc(_portal_href(portal_root, name.lower()+"/index.html"))}">{name}</a>'
                       for name in ('Physics','Chemistry','Mathematics')) if portal_root else ''
    qb_link = f'<a href="{esc(question_bank_href)}">Question Bank</a>' if question_bank_href != home_href else ''
    return (f'<header class="g9-shell-header" data-g9-shell-header><div class="g9-header-inner">'
            f'<a href="{esc(home_href)}" class="g9-brand"><span class="logo-icon">⚡</span><span class="brand-title">Grade9V3.5</span><span class="g9-brand-badge">Learner Platform</span></a>'
            f'<nav class="g9-header-nav" aria-label="Portal Navigation">'
            f'<a data-g9-home href="{esc(home_href)}">Home</a>'
            f'{subjects}{qb_link}'
            f'</nav>'
            f'<div class="g9-header-actions">'
            f'<button type="button" class="g9-header-btn g9-search-btn" data-g9-action="search" title="Search Grade9V3 (Ctrl/⌘ K)" aria-label="Search"><span class="g9-btn-icon">🔍</span><span class="g9-btn-text">Search</span></button>'
            f'<button type="button" class="g9-header-btn g9-display-btn" data-g9-action="display" title="Display & Theme Settings" aria-label="Display & Theme"><span class="g9-btn-icon">🌙 / ☀️</span><span class="g9-btn-text">Display</span></button>'
            f'{pdf_btn}'
            f'</div></div>'
            f'<div data-g9-search-panel hidden><input data-g9-search-input type="search" aria-label="Search this page"></div>'
            f'<div data-g9-display-panel hidden><button type="button" data-g9-font="dec">A-</button><button type="button" data-g9-font="reset">A</button>'
            f'<button type="button" data-g9-font="inc">A+</button><button type="button" data-g9-theme="light">Light</button>'
            f'<button type="button" data-g9-theme="dark">Dark</button><button type="button" data-g9-zoom="dec">Zoom -</button>'
            f'<button type="button" data-g9-zoom="reset">100%</button><button type="button" data-g9-zoom="inc">Zoom +</button></div>'
            f'</header>')


def _pdf_target(ctx: Ctx, role: str, mode: str) -> tuple[str | None, str]:
    """Where the PRINT_PDF control of this page points, and what it is called, as the registry's shell.print_policy says; None where the page has no PDF beside it."""
    policy = ((ctx.blueprints or {}).get("shell") or {}).get("print_policy")
    if not policy or role not in policy.get("applies_to_roles", []) or mode != "PAGES":
        return None, PDF_ACCESSIBLE_NAME
    stem = ROLE_FILE[role].removesuffix(".html")
    return policy["target_pattern"].format(page_stem=stem), policy["accessible_name"]


def _portal_root(manifest: dict, mode: str) -> str | None:
    """A declared portal home supplies its base; a standalone product index does not."""
    home = _mode_href(manifest["home_href"], mode)
    parent = home.rsplit('/', 1)[0]+'/' if '/' in home else None
    return parent

def _portal_href(portal_root: str | None, target: str) -> str | None:
    """Resolve a site-root-relative target without urljoin collapsing ../../../ prefixes."""
    if not portal_root:
        return None
    if target.startswith(("http://", "https://", "//", "#")):
        return target
    return f"{portal_root}{target.lstrip('/')}"


def shell(ctx: Ctx, role: str, mode: str, pdf: bool = True) -> tuple[str, str]:
    m = ctx.manifest
    if mode == "EMBED":
        return "", ""
    
    MODERN_ROLE = {"CORE1A": "Learn", "CORE2": "Practice"}
    current_role = MODERN_ROLE.get(role, role)
    
    home_href = _mode_href(m["home_href"], mode)
    qb_href = _mode_href(m.get("question_bank_href", m["home_href"]), mode)
    pdf_href, pdf_name = _pdf_target(ctx, role, mode) if pdf else (None, PDF_ACCESSIBLE_NAME)
    
    portal_root = _portal_root(m, mode)
    header = shell_header(home_href, qb_href, pdf_href, pdf_name, portal_root)
    subject = m.get("subject", "")
    subject_href = _portal_href(portal_root, subject.lower()+"/index.html") if portal_root else None
    concept = next(iter(ctx.selection_rows.get("microtopics", [])), {})
    selected_questions = ctx.selection_rows.get("core2", [])
    cap_ref = concept.get("primary_capability_ref") or (selected_questions[0].get("primary_capability_ref") if selected_questions else None)
    explore_btn = ""
    topic_href = None
    if portal_root and cap_ref:
        from Shared.tools.resolve_concept_bundle import resolve_bundle
        registry_path = REPO / "public/data/resource-registry.v1.json"
        bundle = resolve_bundle(cap_ref, load_json(registry_path)) if registry_path.exists() else {}
        if bundle.get("interactive"):
            entry = bundle["interactive"][0].get("entrypoint")
            if entry:
                explore_btn = f'<a class="g9-triad-btn g9-btn-explore" href="{esc(_portal_href(portal_root, entry))}">⚡ Try visually</a>'
        topic_ref = bundle.get("topic_ref")
        if topic_ref:
            topic_href = _portal_href(portal_root, "topics/"+topic_ref.split(".")[-1]+"/index.html")
    subject_label = f'<a href="{esc(subject_href)}">{esc(subject)}</a>' if subject_href else esc(subject)
    topic_label = f'<a href="{esc(topic_href)}">{esc(m.get("title", ""))}</a>' if topic_href else esc(m.get("title", ""))
    triad_context = f'<div class="g9-triad-context">{subject_label} / {topic_label} / <span aria-current="page">{esc(current_role)}</span></div>'
    actions = []
    selected_roles = product_manifest.selected_output_roles(m)
    for target,label in (("CORE1","Orientation"),("CORE1A","📖 Learn"),("CORE1B","Recall"),
                         ("CORE2","✍️ Practice"),("CORE2A","Apply"),("CORE2B","Transfer")):
        if target in selected_roles:
            active = ' active' if role == target else ''
            href = '#g9-role-'+target if mode == 'SINGLE_FILE' else ROLE_FILE[target]
            actions.append(f'<a class="g9-triad-btn{active}" href="{esc(href)}">{label}</a>')
    actions.append(explore_btn)
    if qb_href != home_href:
        actions.append(f'<a class="g9-triad-btn g9-btn-qb" href="{esc(qb_href)}">All questions in QB &rarr;</a>')
    triad = (f'<div class="g9-concept-triad-bar"><div class="g9-triad-inner">{triad_context}'
             f'<span class="g9-triad-concept-title">Concept: {esc(m.get("title", ""))}</span>'
             f'<div class="g9-triad-actions">{"".join(actions)}</div></div></div>')

    return header, triad


DIGEST_SLOT = "g9-digest-pending"


def render_digest(ctx: Ctx) -> str:
    """Fingerprint the exact authority-file bytes that can change rendered learner output."""
    h = hashlib.sha256()
    if ctx.authority_hashes:
        for label, digest in ctx.authority_hashes:
            h.update(label.encode("utf-8"))
            h.update(b"\0")
            h.update(digest.encode("ascii"))
            h.update(b"\n")
        return h.hexdigest()[:16]

    # Compatibility fallback for explicitly constructed contexts. Production context()
    # always records file-byte authority hashes.
    h.update(json.dumps(ctx.manifest, sort_keys=True).encode())
    for p in ctx.packages:
        h.update(json.dumps(p, sort_keys=True).encode())
    h.update(json.dumps(ctx.bank, sort_keys=True).encode())
    h.update(json.dumps(ctx.blueprints, sort_keys=True).encode())
    h.update(load_json(CONTRACT)["version"].encode())
    return h.hexdigest()[:16]


def _asset_root(ctx: Ctx) -> str:
    """Return the site-root prefix declared by the product manifest."""
    home = str(ctx.manifest.get("home_href") or "index.html")
    return home[:-len("index.html")] if home.endswith("index.html") else ""


def _shared_head_assets(ctx: Ctx, mode: str) -> str:
    """Renderer-owned tablet shell asset; SINGLE_FILE embeds it and PAGES links it."""
    if mode == "EMBED":
        return ""
    if mode == "SINGLE_FILE":
        return ('<style data-g9-modern-shell>' + (REPO / 'public/css/modern-learner.css').read_text(encoding="utf-8")
                + '</style><style data-g9-tablet-shell>' + TABLET_CSS.read_text(encoding="utf-8") + '</style>')
    root = _asset_root(ctx)
    return f'<link rel="stylesheet" href="{esc(root)}css/modern-learner.css"><link rel="stylesheet" href="{esc(root)}css/tablet-12-7.css">'


def _shared_script_assets(ctx: Ctx, mode: str) -> str:
    if mode == "EMBED":
        return ""
    paths = ("js/display-controls.js", "js/site-header.js")
    if mode == "SINGLE_FILE":
        return ''.join('<script>' + (REPO / 'public' / path).read_text(encoding='utf-8') + '</script>' for path in paths)
    return ''.join(f'<script src="{esc(_asset_root(ctx))}{path}"></script>' for path in paths)


def page(ctx: Ctx, role: str, mode: str, digest: str) -> str:
    bp = next(b for b in ctx.blueprints["blueprints"] if role in b["core_roles"])
    stage_support = bp["responsive_policy"].get("expanded") == "STAGE_SUPPORT"
    articles = ""
    klass = ' class="g9-stage-support"' if stage_support else ""
    for rec in units_for(ctx, role):
        kind = "CONCEPT" if role in {"CORE1", "CORE1A", "CORE1B"} else "QUESTION"
        search_text = metadata_search_text(ctx, role, rec)
        articles += (f'<article id="{esc(rec["id"])}" data-g9-unit="{esc(rec["id"])}" data-g9-kind="{kind}"'
                     f' data-g9-role="{esc(role)}" data-g9-search-text="{esc(search_text)}"{klass}>{RENDER[role](ctx, rec)}</article>')
    header, crumbs = shell(ctx, role, mode)
    m = ctx.manifest
    # The blueprint says which theme its page opens in (the Core1A benchmark opens dark); a learner's own choice still wins.
    theme = (bp.get("presentation_policy") or {}).get("default_theme")
    theme_attr = f' data-theme="{esc(theme)}"' if theme in {"light", "dark"} else ""
    return ("<!doctype html>\n"
            f'<html lang="en"{theme_attr} data-g9-shell data-g9-role="{role}" data-g9-mode="{mode}" '
            f'data-g9-product="{esc(m["product_id"])}" data-g9-render-digest="{esc(digest)}">'
            '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="g9-render" content="{RENDERER_VERSION} {digest}">'
            f'{_shared_head_assets(ctx, mode)}'
            f'<title>{esc(ROLE_TITLE[role])} · {esc(m["title"])}</title><style>{CSS}{COMPONENT_CSS}{learning_repair.CSS}{layout_css(ctx.blueprints)}</style></head>'
            f'<body data-core="{role}" data-blueprint-ref="{esc(bp["id"])}@{esc(bp["version"])}">'
            f'{header}{crumbs}<noscript>Answers open after you attempt; this page needs JavaScript.</noscript>'
            f'<main><h1>{esc(m["title"])}: {esc(ROLE_TITLE[role])}</h1>'
            f'{_core1a_bucket_orientation(ctx) if role == "CORE1A" else ""}{articles}</main>'
            f'<footer data-g9-footer>{esc(m["subject"])} · {esc(m["title"])}</footer>'
            f"<script>{JS}{learning_repair.JS}</script>{_shared_script_assets(ctx, mode)}</body></html>\n")


def index_page(ctx: Ctx, digest: str) -> str:
    m = ctx.manifest
    output_roles = product_manifest.selected_output_roles(m)
    header, crumbs = shell(ctx, output_roles[0], "PAGES", pdf=False)   # the index is not printed: it has no PDF beside it
    links = "".join(f'<li><a href="{ROLE_FILE[r]}">{esc(r)}: {esc(ROLE_TITLE[r])}</a></li>' for r in output_roles)
    qs = {**ctx.index("questions"), **{q["id"]: q for q in ctx.bank}}
    diag_ids = m.get("diagnostic", [])
    if len(diag_ids) < m.get("diagnostic_min", 0):
        ctx.gap("AUTHOR_DIAGNOSTIC", m["product_id"], f"{len(diag_ids)} diagnostic item(s); need {m['diagnostic_min']}", "INDEX")
    diag = "".join(f'<article data-g9-diagnostic="{esc(i)}"><p>{esc(qs[i]["stem"])}</p>'
                   f'{attempt_box("Your answer", response_for(qs[i]), qs[i].get("options"), i)}'
                   f'{reveal("Check", para(qs[i]["answer"].get("summary")), ref=f"INDEX-{i}-check")}</article>'
                   for i in diag_ids if i in qs)
    diag_html = f'<section data-g9-diagnostic-set><h2>Start here</h2>{diag}</section>' if diag else ""
    return ("<!doctype html>\n"
            f'<html lang="en" data-g9-shell data-g9-role="INDEX" data-g9-product="{esc(m["product_id"])}" '
            f'data-g9-render-digest="{esc(digest)}"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="g9-render" content="{RENDERER_VERSION} {digest}">{_shared_head_assets(ctx, "PAGES")}<title>{esc(m["title"])}</title><style>{CSS}</style></head>'
            f'<body>{header}{crumbs}<noscript>Answers open after you attempt; this page needs JavaScript.</noscript>'
            f'<main><h1>{esc(m["title"])}</h1>{diag_html}<ol>{links}</ol></main><script>{JS}</script></body></html>\n')


# ------------------------------------------------------------------ entry points

def _file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def context(manifest_path: Path) -> Ctx:
    manifest = load_json(manifest_path)
    package_paths = [REPO / p for p in manifest["package_refs"]]
    bank_paths = [REPO / b for b in manifest.get("bank_refs", [])]
    packages = [load_json(p) for p in package_paths]
    try:
        from jsonschema import Draft202012Validator
    except ModuleNotFoundError as exc:
        raise RuntimeError("jsonschema is required for product structure validation") from exc
    for paths, records, schema_path in (
        (package_paths, packages, PACKAGE_SCHEMA),
        (bank_paths, [load_json(p) for p in bank_paths], BANK_SCHEMA),
    ):
        validator = Draft202012Validator(load_json(schema_path))
        for path, record in zip(paths, records):
            if schema_path == BANK_SCHEMA and owner_bank.is_owner_bank(record):
                if path.parent.name == "exam-bank":
                    raise ValueError(f"PRODUCT_STRUCTURE_INVALID: {path}: an owner-supplied bank may not live in exam-bank/")
                problems = owner_bank.check(record, str(path), complete=False)
                if problems:
                    raise ValueError("PRODUCT_STRUCTURE_INVALID: " + problems[0]
                                     + (f" (+{len(problems) - 1} more)" if len(problems) > 1 else ""))
                continue
            if schema_path == BANK_SCHEMA and path.parent.name != "exam-bank":
                # Fixture and exemplar banks are not canonical bank publications.
                continue
            errors = sorted(validator.iter_errors(record), key=lambda error: tuple(str(x) for x in error.absolute_path))
            if errors:
                # Name the first several together: fixing them one deploy at a time costs a cold-start author a round each.
                shown = "; ".join(f'{"/".join(str(x) for x in error.absolute_path) or "<root>"}: {error.message}'
                                  for error in errors[:6])
                raise ValueError(f"PRODUCT_STRUCTURE_INVALID: {path}: {shown}"
                                 + (f" (+{len(errors) - 6} more)" if len(errors) > 6 else ""))
    manifest["title"] = (next((p.get("title") for p in packages if p.get("title")), None)
                         or next((b.get("title") for p in packages for b in p.get("buckets", []) if b.get("title")), None)
                         or manifest["product_id"].replace("-", " ").title())
    bank = [q for p in bank_paths for q in load_json(p).get("questions", [])]
    selection_rows = product_manifest.validate_selection(manifest, packages, bank)
    product_coverage.validate(manifest, product_manifest.derivable(packages, bank))
    from Shared.tools import evidence_check, library_board  # local import keeps renderer usable with explicit Ctx fixtures
    source_items = {ref: item for ref, (_inventory, item) in
                    evidence_check.inventory_index(manifest["subject"]).items()}
    source_checks = {}
    for package in packages:
        for question in package.get("questions", []):
            ref = (question.get("extensions") or {}).get("grade9v3:inventory_item")
            item = source_items.get(ref)
            node = (question.get("extensions") or {}).get(library_board.NODE_KEY)
            if not item or not node:
                continue
            path = library_board.verification_path(manifest["subject"], node)
            if not path.is_file():
                continue
            verification = load_json(path)
            records = [row for p in packages for collection in
                       ("capabilities", "microtopics", "relations", "representations", "question_families", "questions")
                       for row in p.get(collection, [])
                       if (row.get("extensions") or {}).get(library_board.NODE_KEY) == node]
            if verification.get("inputs_digest") != library_board.inputs_digest(manifest["subject"], node, records):
                continue
            author = (question.get("extensions") or {}).get("grade9v3:authored_by")
            reader = verification.get("verified_by")
            if not reader or reader == author:
                continue
            required = {ref, item["question_card"]}
            if item["key"].get("card"):
                required.add(item["key"]["card"])
            readback = {row.get("ref") for row in verification.get("readback", [])
                        if row.get("reader") == reader and row.get("reader") != author
                        and row.get("state") in {"AGREED", "CORRECTED"}}
            if ref not in readback and not required - {ref} <= readback:
                continue
            for check in verification.get("questions", []):
                if check.get("card_ref") == item["question_card"]:
                    source_checks[item["question_card"]] = check
    asset_refs = sorted({
        ref
        for package in packages
        for representation in package.get("representations", [])
        for ref in representation.get("rendered_asset_refs", [])
        if isinstance(ref, str)
    } | {scene["asset_ref"] for p in packages for rep in p.get("representations", [])
         for scene in rep.get("scene_instances", []) if scene.get("asset_ref")}
      | {r["snapshot_ref"] for p in packages for r in p.get("resources", []) if r.get("snapshot_ref")})
    own_capabilities = {
        capability["id"]
        for package in packages
        for capability in package.get("capabilities", [])
    }
    teacher_refs: set[str] = set()
    teacher_index = teachers()
    for package in packages:
        for microtopic in package.get("microtopics", []):
            for prerequisite in microtopic.get("prerequisite_refs", []):
                bare = prerequisite.split(":", 1)[-1]
                if bare in own_capabilities:
                    continue
                taught = teacher_index.get(prerequisite) or teacher_index.get(bare)
                if taught:
                    teacher_refs.add(taught[1])
    authority_hashes = [
        ("renderer-source", _file_sha256(Path(__file__))),
        ("core2-v2-source", _file_sha256(CORE2_V2_SOURCE)),
        ("product-manifest-source", _file_sha256(PRODUCT_MANIFEST_SOURCE)),
        ("toughest-concept-source", _file_sha256(Path(toughest_concept.__file__))),
        ("learner-metadata-source", _file_sha256(LEARNER_METADATA_SOURCE)),
        ("learner-metadata-vocabulary", _file_sha256(LEARNER_METADATA_VOCABULARY)),
        ("package-schema", _file_sha256(PACKAGE_SCHEMA)),
        ("competitive-bank-schema", _file_sha256(BANK_SCHEMA)),
        ("manifest", _file_sha256(manifest_path)),
        *[(f"package:{p}", _file_sha256(path)) for p, path in zip(manifest["package_refs"], package_paths)],
        *[(f"bank:{p}", _file_sha256(path)) for p, path in zip(manifest.get("bank_refs", []), bank_paths)],
        ("blueprints", _file_sha256(BLUEPRINTS)),
        ("quality-contract", _file_sha256(CONTRACT)),
        ("tablet-css", _file_sha256(TABLET_CSS)),
        ("typed-math-compiler", _file_sha256(REPO / "public/vendor/katex/0.16.8/katex.min.js")),
        *[
            (f"teacher-package:{ref}", _file_sha256(REPO / ref))
            for ref in sorted(teacher_refs)
            if (REPO / ref).is_file()
        ],
        *[
            (f"asset:{ref}", _file_sha256(REPO / ref))
            for ref in asset_refs
            if (REPO / ref).is_file()
        ],
    ]
    return Ctx(manifest=manifest, packages=packages, bank=bank, blueprints=load_json(BLUEPRINTS),
               selection_rows=selection_rows, authority_hashes=authority_hashes,
               source_items=source_items, source_checks=source_checks)


def subject_authority_findings(manifest_path: Path, repo: Path = REPO) -> list[dict]:
    """Report package relations that lack their subject gate authority."""
    from Shared.library import authority

    manifest = load_json(manifest_path)
    gates = authority.gate_relations(repo / manifest["subject"])
    return [
        {"package": ref, **finding}
        for ref in manifest["package_refs"]
        for finding in authority.findings(load_json(repo / ref), gates)
    ]


def _single_file_fragment(page_html: str, role: str) -> str:
    """Scope role-level unit anchors and convert cross-Core links for one-document packaging."""
    match = re.search(r"<main>(.*)</main>", page_html, re.S)
    if not match:
        raise ValueError(f"{role}: rendered page has no main")
    fragment = match.group(1)
    article_ids = re.findall(r'<article\b[^>]*\bid="([^"]+)"', fragment)
    section_ids = re.findall(r'<section\b[^>]*\bid="([^"]+)"', fragment)
    local_anchor_ids = list(dict.fromkeys(article_ids + section_ids))
    for old in local_anchor_ids:
        fragment = fragment.replace(f'id="{old}"', f'id="g9-{role}--{old}"', 1)
    file_to_role = {ROLE_FILE[r]: r for r in ROLES}
    def cross_link(m: re.Match[str]) -> str:
        target_role = file_to_role.get(m.group(1))
        return f'href="#g9-{target_role}--{m.group(2)}"' if target_role else m.group(0)
    fragment = re.sub(r'href="(core\w+\.html)(?:\?[^"#]*)?#([^"]+)"', cross_link, fragment)
    for old in local_anchor_ids:
        fragment = fragment.replace(f'href="#{old}"', f'href="#g9-{role}--{old}"')
    fragment = re.sub(
        r'href="\.\./\.\./\.\./([^"]+)"',
        lambda m: f'href="../../../public/{m.group(1)}"',
        fragment,
    )
    return fragment


class _SemanticMetadataParser(HTMLParser):
    """Extract mode-neutral learner metadata/search semantics from generated HTML."""

    def __init__(self, role: str | None = None):
        super().__init__(convert_charrefs=True)
        self.role = role
        self.section_depth = 0
        self._role_sections: list[tuple[int, str | None]] = []
        self.current_unit: dict | None = None
        self.current_meta: dict | None = None
        self.units: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = {key: value or "" for key, value in attrs}
        if tag == "section":
            self.section_depth += 1
            if values.get("data-g9-role-section"):
                self._role_sections.append((self.section_depth, self.role))
                self.role = values["data-g9-role-section"]
        if tag == "article" and values.get("data-g9-unit"):
            self.current_unit = {
                "role": self.role,
                "unit": values["data-g9-unit"],
                "search": values.get("data-g9-search-text", ""),
                "metadata": [],
            }
        if self.current_unit is not None and values.get("data-g9-meta-kind"):
            self.current_meta = {
                "kind": values["data-g9-meta-kind"],
                "ref": values.get("data-g9-meta-ref", ""),
                "value": values.get("data-g9-meta-value", ""),
                "label": "",
            }

    def handle_data(self, data: str) -> None:
        if self.current_meta is not None:
            self.current_meta["label"] += data

    def handle_endtag(self, tag: str) -> None:
        if tag == "span" and self.current_meta is not None and self.current_unit is not None:
            self.current_meta["label"] = " ".join(self.current_meta["label"].split())
            self.current_unit["metadata"].append(self.current_meta)
            self.current_meta = None
        if tag == "article" and self.current_unit is not None:
            self.units.append(self.current_unit)
            self.current_unit = None
            self.current_meta = None
        if tag == "section":
            if self._role_sections and self._role_sections[-1][0] == self.section_depth:
                _depth, previous = self._role_sections.pop()
                self.role = previous
            self.section_depth = max(0, self.section_depth - 1)


def semantic_metadata_snapshot(pages: dict[str, str], mode: str) -> list[dict]:
    """Return the mode-neutral learner metadata/search contract actually present in HTML."""
    units: list[dict] = []
    if mode == "SINGLE_FILE":
        parser = _SemanticMetadataParser()
        parser.feed(pages["product.html"])
        units.extend(parser.units)
    else:
        for role in ROLES:
            name = ROLE_FILE[role]
            if name not in pages:
                continue
            parser = _SemanticMetadataParser(role)
            parser.feed(pages[name])
            units.extend(parser.units)
    order = {role: index for index, role in enumerate(ROLES)}
    return sorted(units, key=lambda row: (order.get(row["role"], len(ROLES)), row["unit"]))


def semantic_metadata_digest(pages: dict[str, str], mode: str) -> str:
    payload = json.dumps(
        semantic_metadata_snapshot(pages, mode),
        sort_keys=True,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode()
    return hashlib.sha256(payload).hexdigest()[:16]


def _artifact_digest(pages: dict[str, str]) -> str:
    h = hashlib.sha256()
    for name in sorted(pages):
        h.update(name.encode() + b"\0" + pages[name].encode())
    return h.hexdigest()[:16]


def build(manifest_path: Path, mode: str = "PAGES") -> tuple[dict[str, str], list[dict], str]:
    pages, gaps, digest, _advisories, _waived = build_report(manifest_path, mode)
    return pages, gaps, digest


def _toughest_host_gap(ctx: Ctx) -> None:
    """The toughest question's concept must be one of the concept books this product has."""
    toughest = ctx.toughest()
    if not toughest or toughest["microtopic_ref"] in {m["id"] for m in ctx.selection_rows.get("microtopics", [])}:
        return
    capability = toughest.get("capability_ref")
    ctx.gap("AUTHOR_TOUGHEST_CONCEPT", toughest["question_ref"],
            f"{toughest['label']} is the toughest question in this set, but no concept book of this product owns its capability "
            f"({capability}): write the microtopic whose primary_capability_ref is {capability}, with a construction unit that "
            f"builds toward {toughest['label']}", "CORE1A", component="QUESTION_BRIDGE")


def build_report(manifest_path: Path, mode: str = "PAGES", held_to: str = "FLOOR"
                 ) -> tuple[dict[str, str], list[dict], str, list[dict], list[dict]]:
    """build(), and the advisories and waivers too.

    Advisories are what the blueprint expects a learner to see and the records do not supply; waivers are the
    components an author declared not applicable, with the reason. `held_to="REFERENCE"` judges new authoring at the
    reference depth instead of each component's floor (see component())."""
    ctx = context(manifest_path)
    ctx.held_to = held_to
    output_roles = product_manifest.selected_output_roles(ctx.manifest)
    role_pages = {ROLE_FILE[r]: page(ctx, r, mode, DIGEST_SLOT) for r in output_roles}
    if held_to == "REFERENCE" and "CORE1A" in output_roles:
        _toughest_host_gap(ctx)
    _coverage_findings(ctx, output_roles)
    if mode == "SINGLE_FILE":
        bodies = "".join(
            f'<section id="g9-role-{r}" data-g9-role-section="{r}">'
            f'{_single_file_fragment(role_pages[ROLE_FILE[r]], r)}</section>'
            for r in output_roles
        )
        base_role = output_roles[0]
        product = role_pages[ROLE_FILE[base_role]].replace(
            re.search(r"<main>(.*)</main>", role_pages[ROLE_FILE[base_role]], re.S).group(1),
            bodies,
        )
        pages = {"product.html": product}
    else:
        pages = dict(role_pages)
        if mode != "EMBED":
            pages["index.html"] = index_page(ctx, DIGEST_SLOT)

    # Exact artifact identity is mode-specific by design. PAGES review binds to PAGES bytes;
    # SINGLE_FILE has its own exact identity. Cross-mode equivalence is checked separately
    # through semantic_metadata_digest().
    digest = _artifact_digest(pages)
    pages = {name: page_html.replace(DIGEST_SLOT, digest) for name, page_html in pages.items()}

    # the same gap can be met on several pages; two components of one record are two gaps, though they share a duty
    seen, gaps = set(), []
    for g in ctx.gaps:
        key = (g["duty"], g["record"], g.get("component"))
        if key not in seen:
            seen.add(key)
            gaps.append(g)
    advised, advisories = set(), []
    for a in ctx.advisories:
        key = (a["component"], a["record"])
        if key not in advised:
            advised.add(key)
            advisories.append(a)
    waived, seen_waived = [], set()
    for w in ctx.waived:
        key = (w["component"], w["record"])
        if key not in seen_waived:
            seen_waived.add(key)
            waived.append(w)
    return pages, gaps, digest, advisories, waived



def pdf_publication_problems(folder: Path) -> list[str]:
    """What stands between a rendered product folder and publishing its learner PDFs beside its pages (empty: nothing).

    A page that links its PDF (the shell's PRINT_PDF control) is only as good as the file behind the link. Every such link must name a plain
    learner PDF in the folder, and print-receipt.json (mode LEARNER_PDF) must say that exact PDF was printed from that exact page: same bytes
    of the page, same bytes of the PDF. A key PDF is never a target and never published (it holds the answers). A PDF in the folder that the
    receipt does not vouch for is a problem too: the folder would carry bytes nobody can trace to a page."""
    problems: list[str] = []
    receipt_path = folder / "print-receipt.json"
    receipt = None
    if receipt_path.is_file():
        try:
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
        except ValueError:
            problems.append("print-receipt.json is not valid JSON")
    printed = {}
    if isinstance(receipt, dict):
        if receipt.get("mode") != "LEARNER_PDF":
            problems.append(f"print-receipt.json is a {receipt.get('mode')!r} receipt, not a LEARNER_PDF one")
        else:
            printed = {row.get("pdf"): row for row in receipt.get("pages", []) if isinstance(row, dict)}

    def digest(data: bytes) -> str:
        return "sha256:" + hashlib.sha256(data).hexdigest()

    linked: set[str] = set()
    for page in sorted(folder.glob("*.html")):
        text = page.read_text(encoding="utf-8")
        for anchor in re.findall(r'<a\b[^>]*\bdata-g9-action="pdf"[^>]*>', text):
            target_attr = re.search(r'\bhref="([^"]*)"', anchor)
            href = target_attr.group(1) if target_attr else ""
            if not re.fullmatch(r"[a-z0-9]+\.pdf", href):
                problems.append(f"{page.name}: the PDF link {href!r} is not a learner PDF beside the page")
                continue
            linked.add(href)
            target = folder / href
            row = printed.get(href)
            if not target.is_file():
                problems.append(f"{page.name}: links {href}, which is not there (print the pages: node tools/print/print-product.mjs {folder.name})")
            elif row is None:
                problems.append(f"{page.name}: {href} is not in print-receipt.json")
            elif row.get("page") != page.name:
                problems.append(f"{page.name}: {href} was printed from {row.get('page')}, not from this page")
            elif row.get("page_digest") != digest(page.read_bytes()):
                problems.append(f"{page.name}: changed after {href} was printed from it")
            elif row.get("pdf_digest") != digest(target.read_bytes()):
                problems.append(f"{href}: its bytes differ from the print receipt")
    for pdf in sorted(folder.glob("*.pdf")):
        if pdf.name.endswith(".key.pdf"):
            problems.append(f"{pdf.name}: a key PDF holds the answers and is never published")
        elif pdf.name not in printed:
            problems.append(f"{pdf.name}: not in print-receipt.json")
    return problems


def _retire_previous_outputs(out: Path, pages: dict[str, str]) -> None:
    """Retire receipt-owned files, never arbitrary files in the output directory.

    PDFs must be regenerated after every render, even when the HTML names stay the same.
    A fixed basename allowlist also prevents a malformed receipt escaping this directory.
    """
    receipt = out / "render-receipt.json"
    if not receipt.is_file():
        return
    try:
        previous = json.loads(receipt.read_text(encoding="utf-8")).get("pages", [])
    except (ValueError, AttributeError):
        return
    if not isinstance(previous, list):
        return
    managed = set(ROLE_FILE.values()) | {"index.html", "product.html"}
    previous = {name for name in previous if isinstance(name, str) and name in managed}
    obsolete = previous - set(pages)
    for name in previous - {"index.html"}:
        obsolete.update((name.removesuffix(".html") + ".pdf", name.removesuffix(".html") + ".key.pdf"))
    if previous:
        obsolete.update(("print-receipt.json", "print-key-receipt.json"))
    for name in obsolete:
        target = out / name
        if target.is_file() and not target.is_symlink() and target.resolve().parent == out.resolve():
            target.unlink()


_ROLE_SELECTION_KEY = {"CORE1": "microtopics", "CORE1A": "microtopics", "CORE1B": "microtopics",
                       "CORE2": "core2", "CORE2A": "core2a", "CORE2B": "core2b"}


def empty_roles(manifest: dict) -> list[str]:
    """Roles the product includes whose selection is empty: their pages render with no items, and a draft
    build still succeeds, so the build says so instead of leaving it to be noticed in the page."""
    selection = manifest.get("selection") or {}
    return [role for role in product_manifest.selected_output_roles(manifest)
            if not selection.get(_ROLE_SELECTION_KEY[role])]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--manifest", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--mode", choices=MODES, default="PAGES")
    b.add_argument("--draft", action="store_true", help="write a draft even when gaps remain (never published)")
    b.add_argument("--reference", action="store_true", help="judge authored depth against the blueprint reference bar")
    g = sub.add_parser("gaps")
    g.add_argument("--manifest", required=True)
    g.add_argument("--reference", action="store_true", help="judge authored depth against the blueprint reference bar")
    args = parser.parse_args(argv)
    held_to = "REFERENCE" if getattr(args, "reference", False) else "FLOOR"
    try:
        pages, gaps, digest, _advisories, _waived = build_report(
            Path(args.manifest), getattr(args, "mode", "PAGES"), held_to=held_to
        )
    except product_manifest.ProductSelectionError as caught:
        print(f"selection rejected: {caught}", file=sys.stderr)  # an input problem, not a crash
        return 1
    if args.cmd == "gaps":
        for gap in gaps:
            print(f"{gap['core']:7s} {gap['duty']:32s} {gap['record']:44s} {gap['detail']}")
        authority_findings = subject_authority_findings(Path(args.manifest))
        for finding in authority_findings:
            print(f"AUTHORITY {finding['point']:28s} {finding['record']:44s} {finding['detail']}")
        print(f"{len(gaps)} depth gap(s); {len(authority_findings)} subject-authority finding(s)")
        return 1 if gaps or authority_findings else 0
    if gaps and not args.draft:
        # A strict CI failure must identify its real authoring defects. This
        # remains fail-closed: no output is written and the exit code is 2.
        for gap in gaps:
            print(f"{gap['core']:7s} {gap['duty']:32s} {gap['record']:44s} {gap['detail']}", file=sys.stderr)
        print(f"{len(gaps)} gap(s): nothing written. Run `render_core.py gaps` or `--draft`.", file=sys.stderr)
        return 2
    out = Path(args.out)
    if out.resolve().is_relative_to((REPO / "public").resolve()):
        raise ValueError("render_core cannot write to public; use Owner acceptance of a staged render")
    out.mkdir(parents=True, exist_ok=True)
    _retire_previous_outputs(out, pages)
    for name, text in pages.items():
        if gaps:
            text = text.replace("<html ", '<html data-g9-draft="%d" ' % len(gaps), 1)
        (out / name).write_bytes(text.encode("utf-8"))
    manifest_path = Path(args.manifest).resolve()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    try:
        manifest_ref = manifest_path.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        manifest_ref = manifest_path.as_posix()
    (out / "render-receipt.json").write_text(json.dumps({
        "renderer": RENDERER_VERSION, "digest": digest,
        "semantic_digest": semantic_metadata_digest(pages, args.mode),
        "manifest": manifest_ref, "mode": args.mode, "held_to": held_to,
        "draft": bool(gaps), "gaps": gaps, "pages": sorted(pages),
        "output_roles": product_manifest.selected_output_roles(manifest),
        "ledger": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("ledger", []),
        "diagnostic_min": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("diagnostic_min", 0)},
        indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(pages)} page(s) to {out}" + (f" as DRAFT with {len(gaps)} gap(s)" if gaps else ""))
    print("selected records: " + " ".join(f"{key}={len(manifest.get('selection', {}).get(key) or [])}"
                                          for key in product_manifest.SELECTION_KEYS))
    for role in empty_roles(manifest):
        print(f"WARNING: {role} is part of this product but selects no records, so its page has no items.", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
