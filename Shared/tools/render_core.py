#!/usr/bin/env python3
"""The one renderer for learner Core pages.

Renders the six Core roles of a product from library records (schema 0.2.0) and a product
manifest. It renders only through the role's blueprint slots
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
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import learner_metadata, product_manifest  # noqa: E402

BLUEPRINTS = REPO / "Shared/web/interactive-page-blueprints.v1.json"
CONTRACT = REPO / "Shared/quality/learner-quality.v1.json"
TABLET_CSS = REPO / "public/css/tablet-12-7.css"
PACKAGE_SCHEMA = REPO / "Shared/library/package.schema.json"
BANK_SCHEMA = REPO / "Shared/library/competitive-exam-bank.schema.json"
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
    figure_instances: dict[str, int] = field(default_factory=dict)
    source_items: dict[str, dict] = field(default_factory=dict)
    source_checks: dict[str, dict] = field(default_factory=dict)

    def gap(self, duty: str, record: str, detail: str, role: str) -> None:
        self.gaps.append({"duty": duty, "record": record, "detail": detail, "core": role,
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


def figure(ctx: Ctx, rep_id: str | None, stage: str, role: str, record: str, first_stage_only: bool = False,
           allowed: list[str] | None = None) -> str:
    """Mount a representation's authored SVG, or record the gap (never a stand-in)."""
    if not rep_id:
        return ""
    rep = ctx.index("representations").get(rep_id)
    if rep is None:
        ctx.gap("MOUNT_REPRESENTATION", record, f"{rep_id} is not a representation in the product's packages", role)
        return ""
    svg = next((s for s in (asset_svg(a) for a in rep.get("rendered_asset_refs") or []) if s), None)
    if svg is None:
        ctx.gap("BUILD_SCENE", rep_id, "no authored SVG asset (rendered_asset_refs) to mount", role)
        return ""
    opener = re.search(r"<svg\b[^>]*>", svg, re.I)
    named = bool(opener and re.search(r"\baria-(?:label|labelledby)=['\"][^'\"]+['\"]", opener.group(0), re.I))
    described = bool(re.search(r"<title\b[^>]*>.*?</title>", svg, re.I | re.S) and re.search(r"<desc\b[^>]*>.*?</desc>", svg, re.I | re.S))
    if not (named and described):
        ctx.gap("BUILD_SCENE", rep_id, "authored SVG lacks an accessible name and title/description pair", role)
        return ""
    instance_base = re.sub(r"[^A-Za-z0-9_-]+", "-", f"{role}-{record}-{rep_id}").strip("-")
    instance_no = ctx.figure_instances.get(instance_base, 0) + 1
    ctx.figure_instances[instance_base] = instance_no
    svg = _scope_svg_ids(svg, f"g9fig-{instance_base}-{instance_no}")
    stage_ids = re.findall(r'data-g9-stage-id="([^"]+)"', svg)
    # Before an attempt only permitted stages show: the record's stage_refs, else the first stage.
    if stage == "PRE_ATTEMPT" and not allowed:
        first_stage_only = True
    shown = [s for s in stage_ids if s in allowed] if allowed else (stage_ids[:1] if first_stage_only else stage_ids)
    kind = rep.get("kind")
    controls = ""
    if len(shown) > 1:
        controls = ('<div class="g9-stage-controls"><button type="button" data-g9-stage-step="prev">Previous stage</button>'
                    '<span data-g9-stage-label></span>'
                    '<button type="button" data-g9-stage-step="next">Next stage</button></div>')
    withheld = [s for s in stage_ids if s not in shown]
    labels = {st.get("id"): st.get("label") for st in rep.get("reveal_stages") or []}
    if stage == "PRE_ATTEMPT":
        # `purpose` is the illustrator's design note and often names the result ("so the double count is
        # diagnosed"). Before the attempt the caption is only the labels of the stages actually shown.
        caption = (f'<figcaption data-g9-block="stage_caption" data-g9-caption="stages">'
                   f'{esc("; ".join(labels[s] for s in shown if labels.get(s)))}</figcaption>')
    else:
        caption = (f'<figcaption data-g9-block="representation_bridge" data-g9-caption="purpose">'
                   f'{esc(rep.get("purpose", ""))}</figcaption>')
    if withheld:
        # A withheld stage is not in the page at all (hiding it with CSS still hands it to the DOM,
        # the hover tooltip and screen readers). The asset's own <title>/<desc> describe the whole
        # figure, so they go too; the accessible name is the shown stages' labels from the record.
        svg = _without_stages(svg, set(withheld))
        svg = re.sub(r"<(title|desc)\b[^>]*>.*?</\1>", "", svg, flags=re.S)
        head = re.search(r"<svg\b[^>]*>", svg)
        if head:                                       # the name comes from the shown stages below
            clean = re.sub(r'\s(role|aria-label|aria-labelledby|aria-describedby)="[^"]*"', "", head.group(0))
            svg = svg[:head.start()] + clean + svg[head.end():]
        name = "; ".join(labels[s] for s in shown if labels.get(s)) or rep.get("purpose", "")
        svg = re.sub(r"<svg\b", f'<svg role="img" aria-label="{esc(name)}"', svg, count=1)
    return (f'<figure data-g9-figure data-g9-fig="{esc(record)}-{esc(rep_id)}" data-g9-stage="{stage}" '
            f'data-g9-representation="{esc(rep_id)}" data-g9-kind="{esc(kind)}" data-reveal-stages="{max(len(shown), 1)}" '
            f'data-g9-stages-total="{max(len(stage_ids), 1)}" data-g9-stages="{esc(" ".join(shown))}">'
            f'{svg}{controls}{caption}</figure>')


def _without_stages(svg: str, withheld: set[str]) -> str:
    """Remove each <g data-g9-stage-id="…"> element whose stage is withheld, with everything inside it."""
    out, i = [], 0
    opener = re.compile(r'<g\b[^>]*\bdata-g9-stage-id="([^"]+)"[^>]*>')
    while True:
        m = opener.search(svg, i)
        if not m:
            out.append(svg[i:])
            return "".join(out)
        if m.group(1) not in withheld:
            out.append(svg[i:m.end()])
            i = m.end()
            continue
        out.append(svg[i:m.start()])
        if m.group(0).endswith("/>"):                  # an empty withheld group
            i = m.end()
            continue
        depth, j = 1, m.end()
        tags = re.compile(r"<g\b[^>]*?(/?)>|</g\s*>")
        while depth:
            t = tags.search(svg, j)
            if t is None:                      # malformed asset: drop the rest rather than leak it
                return "".join(out)
            if t.group(0).startswith("</"):
                depth -= 1
            elif not t.group(1):
                depth += 1
            j = t.end()
        i = j


# ------------------------------------------------------------------ small html helpers

def block(name: str, body: str, tag: str = "div", title: str | None = None) -> str:
    if not body:
        return ""
    head = f"<h4>{esc(title)}</h4>" if title else ""
    return f'<{tag} class="g9-block" data-g9-block="{name}">{head}{body}</{tag}>'


def para(text) -> str:
    return f"<p>{esc(text)}</p>" if text else ""


def items(values, ordered=False) -> str:
    values = [v for v in values or [] if v]
    if not values:
        return ""
    t = "ol" if ordered else "ul"
    return f"<{t}>" + "".join(f"<li>{esc(v)}</li>" for v in values) + f"</{t}>"


def slot(name: str, body: str, required: bool) -> str:
    return (f'<section class="blueprint-slot slot-{name}" data-blueprint-slot="{name}" '
            f'data-required="{"true" if required else "false"}">{body}</section>')


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
        f'<strong>{esc(field_labels[item["kind"]])}:</strong> {esc(item["label"])}</span>'
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
                record: str = "") -> str:
    """Ask an honest self-learner for a typed commitment, not a marked answer."""
    response = response or {"type": "free_response"}
    kind = response["type"]
    group = "g9-" + re.sub(r"[^A-Za-z0-9_-]+", "-", record or label)
    if kind in {"single_choice", "multiple_choice", "true_false"}:
        choices = list(options or (["True", "False"] if kind == "true_false" else []))
        input_type = "checkbox" if kind == "multiple_choice" else "radio"
        controls = "".join(
            f'<label class="g9-answer-option"><input data-g9-choice type="{input_type}" '
            f'name="{esc(group)}" value="{i}"><span>{esc(choice)}</span></label>'
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
    return f'<p class="g9-expr">{esc(relation["expression"])}</p>'


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
        for index, unit in enumerate(units, 1):
            route.append({
                "microtopic_id": microtopic["id"],
                "microtopic_title": microtopic["title"],
                "unit_id": unit["id"],
                "label": unit.get("decision") or f"Construction {index}",
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
        rows.append(f'<li data-g9-foundation-ref="{esc(ref)}">'
                    + (f'<a href="{esc(href)}">{esc(label)}</a>' if href else esc(label))
                    + "</li>")
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
        companion = (
            block("foundation_route", _core1a_foundation_route(ctx, bucket), title="Foundation route")
            + block("model_contract", items(conventions), title="Model contract")
        )
        rendered.append(
            f'<section class="g9-core1a-book" data-g9-bucket-orientation '
            f'data-g9-bucket-ref="{esc(bucket_ref)}">'
            f'<p class="g9-prov">Concept Book</p><h2>{esc(bucket.get("title") or bucket.get("topic") or "")}</h2>'
            f'<div class="g9-bucket-orientation-grid"><div>{primary}</div><aside>{companion}</aside></div>'
            f'</section>'
        )
    return "".join(rendered)


def _core1a_section_route(m: dict) -> str:
    units = m.get("construction_units") or []
    if not units:
        return ""
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
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="true"><a href="core1a.html#{esc(own[bare])}">{esc(label)}</a></li>')
        elif taught:
            href = links.get(ref) or links.get(bare)
            label = f"{taught[3]} ({taught[0]})" if len(taught) > 3 and taught[3] else f"Taught in {taught[0]}"
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="true">'
                        + (f'<a href="{esc(href)}">{esc(label)}</a>' if href else esc(label)) + "</li>")
        else:
            ctx.gap("TEACH_PREREQUISITE_BRIDGE", m["id"], f"prerequisite {ref} is taught by no library", "CORE1A")
            rows.append(f'<li data-g9-prereq="{esc(ref)}" data-bridged="false">{esc(ref)}</li>')
    return "<ul>" + "".join(rows) + "</ul>" if rows else ""


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
    body = (slot("identity", block("scope", f"<h2>{esc(m['title'])}</h2>") + metadata_strip(ctx, "CORE1", m), True)
            + slot("orientation",
                   block("hard_transition", para(m["inferential_jump"]), title="Hard transition")
                   + figure(ctx, rep, "TEACHING", "CORE1", m["id"])
                   + block("governing_relation", rel_html, title="Governing relation")
                   + block("compact_anchor", (para(anchor["prompt"]) + para(anchor["result"])) if anchor else "", title="Compact anchor")
                   + block("exit_prompt", para((m.get("exit_task") or {}).get("prompt")), title="Before you go on"), True))
    return body


def _core1a_worked_anchor(question: dict) -> str:
    """Render WATCH ONE from governed answer structure without inventing missing explanation."""
    answer = question.get("answer") or {}
    route = answer.get("reasoning_route") or []
    if route:
        steps = "".join(
            f'<li data-g9-watch-step data-g9-move-ref="{esc(row.get("id", index))}">'
            f'<strong>{esc(row.get("action", ""))}</strong>'
            f'{para("Why valid: " + row["why_valid"]) if row.get("why_valid") else ""}'
            f'{para("Result: " + row["output"]) if row.get("output") else ""}</li>'
            for index, row in enumerate(route, 1)
        )
        working = f'<ol class="g9-watch-steps">{steps}</ol>'
    else:
        working = items(answer.get("reasoning"), True)
    return (
        para(question.get("stem"))
        + working
        + block("worked_result", para(answer.get("summary")), title="Result")
        + block("worked_check", para(answer.get("check")), title="Check")
    )


def _core1a_relation_matrix(ctx: Ctx, m: dict) -> str:
    """Preserve governed equation/meaning/validity data as a semantic comparison table."""
    relations = _relations(ctx, m)
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


def core1a(ctx: Ctx, m: dict) -> str:
    units = m.get("construction_units") or []
    if not units:
        ctx.gap("AUTHOR_CONSTRUCTION_UNITS", m["id"], "no construction units", "CORE1A")
    steps = {s["id"]: s for s in m.get("teaching_path", [])}
    questions = ctx.index("questions")
    unit_html = ""
    for n, u in enumerate(units):
        decision = "" if u.get("decision_from") == "inferential_jump" else u.get("decision", "")
        step_html = "".join(f'<li data-g9-step="{esc(sid)}"><strong>{esc(steps[sid]["action"])}</strong>'
                            f'<br><em>Why valid:</em> {esc(steps[sid]["why_valid"])}'
                            f'<br><em>Result:</em> {esc(steps[sid]["output"])}</li>'
                            for sid in u["step_refs"] if sid in steps)
        anchor_q = questions.get(u.get("worked_anchor_ref") or "")
        if not anchor_q:
            ctx.gap("AUTHOR_WORKED_ANCHOR", u["id"], "no worked anchor", "CORE1A")
        anchor_html = _core1a_worked_anchor(anchor_q) if anchor_q else ""
        checks = [c["statement"] for c in u.get("independent_checks") or []]
        if not checks:
            ctx.gap("AUTHOR_INDEPENDENT_CHECK", u["id"], "no independent check", "CORE1A")
        wrong = _misconceptions(m, u)
        heading = f"<h3>{esc(decision)}</h3>" if decision else (f"<h3>Construction step {n + 1} of {len(units)}</h3>" if len(units) > 1 else "")
        relation_matrix = _core1a_relation_matrix(ctx, m) if n == 0 else ""
        unit_html += (f'<section id="{esc(u["id"])}" class="g9-cu" data-g9-cu="{esc(u["id"])}">{heading}'
                      + _core1a_unit_navigation(ctx, u["id"])
                      + block("construction", f"<ol>{step_html}</ol>")
                      + figure(ctx, u.get("representation_ref"), "TEACHING", "CORE1A", u["id"])
                      + block("equation_matrix", relation_matrix, title="Equations and validity")
                      + block("worked_anchor", anchor_html, title="Watch one")
                      + block("wrong_path", items(w["wrong_idea"] for w in wrong), title="A tempting wrong path")
                      + block("diagnose", items(w["diagnostic_prompt"] for w in wrong), title="Diagnose")
                      + block("repair", items(w["repair"] for w in wrong), title="Repair")
                      + block("independent_check", items(checks), title="Check it independently")
                      + "</section>")
    exit_task = m.get("exit_task") or {}
    return (slot("identity", f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1A", m)
                 + block("entry_assumptions", items(m.get("entry_assumptions")) + _prereqs(ctx, m), title="You need")
                 + block("section_route", _core1a_section_route(m), title="Sections")
                 , True)
            + slot("construction", block("inferential_jump", para(m["inferential_jump"]), title="The key step") + unit_html, True)
            + slot("repair_closure",
                   block("exit_task", para(exit_task.get("prompt")), title="Exit task")
                   + attempt_box("Your answer", record=m["id"])
                   + reveal("Model answer", block("exit_answer", para((exit_task.get("answer") or {}).get("summary"))
                                                  + items((exit_task.get("answer") or {}).get("reasoning"), True)),
                            ref=f'CORE1A-{m["id"]}-exit'), True))


def core1b(ctx: Ctx, m: dict) -> str:
    e = m.get("elicitation")
    if not e:
        ctx.gap("AUTHOR_ELICITATION", m["id"], "no predict/attempt/reconstruct/boundary cycle", "CORE1B")
        return slot("identity", f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1B", m), True)
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
    return (slot("identity", f"<h2>{esc(m['title'])}</h2>" + metadata_strip(ctx, "CORE1B", m), True)
            + slot("attempt",
                   block("predict", para((e.get("predict") or {}).get("prompt")), title="Predict")
                   + figure(ctx, task_rep, "PRE_ATTEMPT", "CORE1B", m["id"], first_stage_only=True,
                            allowed=(task or {}).get("stage_refs") or None)
                   + block("attempt_prompt", (para(task["prompt"]) + items(task.get("givens"))) if task else "",
                           title="Attempt")
                   + attempt_box("Your attempt", (task or {}).get("response"), record=m["id"]), True)
            + slot("reconstruction",
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
                            ref=f'CORE1B-{m["id"]}-boundary'), True))


def _identity(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    parts = [cust.get("exam"), cust.get("year"), cust.get("paper"), f"Q{cust['question_number']}" if cust.get("question_number") else None]
    return " · ".join(str(p) for p in parts if p) or q.get("original_identifier", "")


def _custody(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    if (cust.get("authority_class") != "OFFICIAL_EXAM_ORGANIZER_ARCHIVE"
            or cust.get("source_status") != "PYQ_VERIFIED_PARENT"
            or not cust.get("paper_url")):
        return "Source unverified"
    wording = {"FAITHFUL_NON_VERBATIM_RESTATEMENT": "faithful restatement of the original"}.get(cust.get("wording_custody"), "")
    return "Official past paper" + (f", {wording}" if wording else "")


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


def core2(ctx: Ctx, q: dict) -> str:
    q = source_projection(ctx, q)
    ans = q["answer"]
    if ans.get("_independent_result") and ans["_independent_result"] != ans.get("summary"):
        ctx.gap("AUTHOR_SOURCE_RESULT_DIFFERS", q["id"], "authored summary differs from current independent result", "CORE2")
    figures = "".join(figure(ctx, ref, "PRE_ATTEMPT", "CORE2", q["id"], first_stage_only=True)
                      for ref in q.get("figure_refs") or [])
    return (slot("identity", block("source_identity", f"<h2>{esc(_identity(q))}</h2><p class=\"g9-prov\">{esc(_custody(q))}</p>") + metadata_strip(ctx, "CORE2", q), True)
            + slot("attempt", block("stem", para(q["stem"])) + block("conditions", items(q.get("conditions")), title="Conditions")
                   + figures + attempt_box("Your answer", response_for(q), q.get("options"), q["id"]), True)
            + slot("support", block("source_hints", _ladder(ctx, q, "CORE2", source=True)), False)
            + slot("solution", reveal("Answer and working", _source_solution(ans)
                                      + block("working", items(ans.get("reasoning"), True)),
                                      ref=f'CORE2-{q["id"]}-solution'), True))


def _ladder(ctx: Ctx, q: dict, role: str, source: bool = False) -> str:
    rungs = sorted(q.get("hint_ladder") or [], key=lambda r: r["order"])
    texts = []
    if source:
        texts = [h["text"] if isinstance(h, dict) else str(h) for h in q.get("hints") or []]
    else:
        for r in rungs:
            if r.get("text"):
                texts.append(r["text"])
            elif r.get("from"):
                kind, i = re.match(r"(hints|scaffolds)\[(\d+)\]", r["from"]).groups()
                texts.append((q.get(kind) or [])[int(i)]["text"])
    if not source and len(texts) < 3:
        ctx.gap("AUTHOR_HINT_LADDER", q["id"], f"{len(texts)} rung(s); need 3", role)
    if not texts:
        return ""
    ref = f'{role}-{q["id"]}'
    later = "".join(f'<template data-g9-rung-payload="{esc(ref)}-{n}">'
                    f'<li data-g9-rung="{n}">{esc(t)}</li></template>'
                    for n, t in enumerate(texts[1:], 2))
    return (f'<div class="g9-ladder" data-g9-ladder-ref="{esc(ref)}">'
            f'<ol data-g9-ladder><li data-g9-rung="1">{esc(texts[0])}</li></ol>'
            f'{later}<button type="button" data-g9-next-rung{" disabled" if len(texts) == 1 else ""}>'
            'Next hint</button></div>')


def _family_title(ctx: Ctx, ref: str | None) -> str:
    fam = ctx.index("question_families").get(ref or "")
    return fam.get("title", "") if fam else ""


def _repair(ctx: Ctx, ref: str | None) -> str:
    """A repair pointer as the learner needs it: the step's own action, linked to Core1A."""
    if not ref:
        return ""
    for p in ctx.packages:
        for m in p.get("microtopics", []):
            for s in m.get("teaching_path", []):
                if s["id"] == ref:
                    return f'<p><a href="core1a.html#{esc(m["id"])}">Revisit: {esc(s["action"])}</a></p>'
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
    return (slot("identity", block("provenance", f'<p class="g9-prov">{esc(q.get("origin"))} practice</p>')
                 + metadata_strip(ctx, "CORE2A", q)
                 + block("family_identity", para(_family_title(ctx, fam.get("family_ref") or q.get("family_ref")))), True)
            + slot("attempt", block("stem", f"<h2>{esc(q['stem'])}</h2>")
                   + block("conditions", items(q.get("conditions")), title="Conditions")
                   + figure(ctx, roles.get("initial_ref"), "PRE_ATTEMPT", "CORE2A", q["id"], allowed=roles.get("stage_refs"))
                   + attempt_box("Your attempt", response_for(q), q.get("options"), q["id"]), True)
            + slot("support", _ladder(ctx, q, "CORE2A"), False)
            + slot("reasoning", reveal("Reasoning route and full solution",
                                       block("reasoning_route", f"<ol>{route}</ol>" if route else "")
                                       + figure(ctx, roles.get("bound_ref"), "POST_ATTEMPT", "CORE2A", q["id"] + "-bound")
                                       + block("solution", items(ans.get("reasoning"), True))
                                       + block("answer", para(ans.get("summary")), title="Answer")
                                       + block("independent_check", para(check), title="Independent check")
                                       + block("failure_signal", para(q.get("failure_signal")), title="If you went wrong")
                                       + block("repair", _repair(ctx, q.get("repair_ref")), title="Repair")
                                       + block("exposure_closure", para(fam.get("closure")), title="What this establishes"),
                                       ref=f'CORE2A-{q["id"]}-reasoning'), True))


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
        if b in (sel.get("core2a") or []):
            return f"core2a.html#{b}"
        for m in ctx.index("microtopics").values():
            if m["id"] in (sel.get("microtopics") or []) and any(
                    u.get("worked_anchor_ref") == b for u in m.get("construction_units") or []):
                return f"core1a.html#{m['id']}"
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
    return (slot("identity", block("provenance", f'<p class="g9-prov">{esc(q.get("origin"))} transfer</p>')
                 + metadata_strip(ctx, "CORE2B", q)
                 + block("stem", f"<h2>{esc(q['stem'])}</h2>")
                 + block("lineage", f"<ul>{lineage}</ul>" if lineage else "", title="Builds on"), True)
            + slot("attempt", block("conditions", items(q.get("conditions")), title="Conditions")
                   + figure(ctx, roles.get("safe_ref"), "PRE_ATTEMPT", "CORE2B", q["id"], allowed=roles.get("stage_refs"))
                   + block("safe_support", para(rung_text), title="Where to start")
                   + attempt_box("Your commitment: the model or representation you choose, and your first relation",
                                 response_for(q), q.get("options"), q["id"]), True)
            + slot("post_attempt",
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
                            ref=f'CORE2B-{q["id"]}-review'), True))


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
:root{--g9-zoom:1;--g9-content-max:1380px;--g9-touch-min:48px;--g9-space:clamp(16px,2vw,28px);--g9-type-body:17px;--bg:#f6f7fb;--fg:#172033;--card:#fff;--line:#d5dce6;--accent:#1f5fae;--muted:#52627a}
:root[data-theme=dark]{--bg:#0f1520;--fg:#e8edf5;--card:#18212f;--line:#2c394d;--accent:#8ab4f8;--muted:#a3b1c6}
html{font-size:calc(var(--g9-type-body) * var(--g9-zoom))}body{margin:0;background:var(--bg);color:var(--fg);font:1rem/1.6 system-ui,sans-serif;overflow-wrap:break-word}
header[data-g9-shell-header]{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px var(--g9-space);background:var(--card);border-bottom:1px solid var(--line)}
header a,header button,button,summary,nav a{min-height:var(--g9-touch-min);min-width:var(--g9-touch-min);padding:10px 14px;box-sizing:border-box;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg);font:inherit;text-decoration:none;display:inline-flex;align-items:center;justify-content:center;cursor:pointer;touch-action:manipulation}
nav[data-g9-breadcrumb]{display:flex;gap:8px;flex-wrap:wrap;padding:8px var(--g9-space)}
main{max-width:var(--g9-content-max);margin:0 auto;padding:var(--g9-space);box-sizing:border-box}
main>*{min-width:0}article[data-g9-unit]{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:var(--g9-space);margin:18px 0;min-width:0}
article[data-g9-unit]>*{min-width:0}
article[id],section[id]{scroll-margin-top:96px}
.g9-core1a-book{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:clamp(16px,2vw,24px);margin:0 0 18px;min-width:0}
.g9-core1a-book>h2{margin:.15em 0 .6em}
.g9-bucket-orientation-grid{display:block;min-width:0}.g9-bucket-orientation-grid>*{min-width:0}
[data-g9-concept-route] ol,[data-g9-section-route] ol{padding-left:1.4rem;margin:.5rem 0}
[data-g9-concept-route] li,[data-g9-section-route] li{margin:.35rem 0}
.g9-cu{padding-top:8px;border-top:1px solid var(--line)}
.g9-cu:first-child{border-top:0}
.g9-cu-nav{display:flex;align-items:center;justify-content:space-between;gap:8px;flex-wrap:wrap;margin:.35rem 0 .8rem}
.g9-cu-nav-links{display:flex;gap:8px;flex-wrap:wrap}
.g9-table-scroll{max-width:100%;overflow-x:auto;-webkit-overflow-scrolling:touch}
.g9-table-scroll table{width:100%;min-width:680px;border-collapse:collapse}
.g9-table-scroll th,.g9-table-scroll td{border:1px solid var(--line);padding:10px 12px;text-align:left;vertical-align:top}
.g9-table-scroll th{background:var(--bg)}
.g9-table-scroll td>.g9-math,.g9-table-scroll td>.g9-expr{margin:.15rem 0}
[data-g9-block=worked_anchor]{border-left:4px solid var(--accent);padding-left:14px}
.g9-watch-steps>li{margin:.8rem 0}.g9-watch-steps p{margin:.2rem 0}
[data-g9-block=wrong_path],[data-g9-block=repair]{border-left:3px solid var(--line);padding-left:12px}
@media (min-width:1100px){.g9-bucket-orientation-grid{display:grid;grid-template-columns:.68fr .32fr;gap:20px}
article[data-g9-unit].g9-stage-support{display:grid;grid-template-columns:.68fr .32fr;gap:20px}
article.g9-stage-support>.slot-identity,article.g9-stage-support>.slot-attempt,article.g9-stage-support>.slot-construction,article.g9-stage-support>.slot-reconstruction,article.g9-stage-support>.slot-reasoning,article.g9-stage-support>.slot-post_attempt,article.g9-stage-support>.slot-solution{grid-column:1}
article.g9-stage-support>.slot-support,article.g9-stage-support>.slot-repair_closure{grid-column:2}}
textarea{width:100%;min-height:120px;font:inherit;border:1px solid var(--line);border-radius:10px;padding:14px 16px;box-sizing:border-box;background:var(--card);color:var(--fg)}
details{border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:0 12px}details[data-locked] summary{opacity:.55;cursor:not-allowed}
figure{margin:14px 0;max-width:100%;overflow-x:auto}figure svg{width:100%;height:auto;max-width:720px}figcaption{color:var(--muted)}
.g9-prov{color:var(--muted);font-size:.95rem}.g9-expr{font-family:ui-monospace,monospace;font-size:1.05rem}
[data-g9-meta-strip]{display:flex;flex-wrap:wrap;gap:8px;margin:10px 0 4px}
[data-g9-meta-item]{display:inline-flex;gap:4px;align-items:baseline;padding:5px 9px;border:1px solid var(--line);border-radius:999px;background:var(--bg);font-size:.9rem}
[data-g9-meta-item] strong{font-weight:700}
h4{margin:.8em 0 .3em}:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
footer{padding:24px 16px;color:var(--muted)}
@media print{header[data-g9-shell-header],nav[data-g9-breadcrumb],.g9-attempt,button,[data-g9-display-panel]{display:none!important}
details{border:none}article[data-g9-unit]{break-inside:avoid-page;border:none}body{background:#fff;color:#000}}
.g9-attempt input[type=text],.g9-attempt select,.g9-attempt textarea{min-height:48px;box-sizing:border-box}
.g9-answer-option,.g9-paper,.g9-match{display:flex;align-items:center;gap:.5rem;min-height:48px}
.g9-answer-option input,.g9-paper input{min-width:48px;min-height:48px}
.g9-attempt fieldset{min-height:48px}
.g9-math,pre,table{max-width:100%;overflow-x:auto}
input,select{font-size:max(16px,1rem)}
@media (max-width:899px){header[data-g9-shell-header]{position:relative}article[data-g9-unit]{padding:16px}nav[data-g9-breadcrumb]{font-size:.95rem}}
"""

JS = r"""
(()=>{const q=(s,r=document)=>[...r.querySelectorAll(s)];
const store={get:k=>{try{return localStorage.getItem('g9-'+k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem('g9-'+k,v)}catch(e){}}};
const root=document.documentElement;const apply=()=>{root.dataset.theme=store.get('theme')||root.dataset.theme||'light';root.style.setProperty('--g9-zoom',store.get('zoom')||'1');};apply();
q('[data-g9-theme]').forEach(b=>b.onclick=()=>{store.set('theme',b.dataset.g9Theme);apply()});
q('[data-g9-zoom]').forEach(b=>b.onclick=()=>{let z=parseFloat(store.get('zoom')||'1');z=b.dataset.g9Zoom==='inc'?Math.min(1.6,z+0.1):b.dataset.g9Zoom==='dec'?Math.max(0.8,z-0.1):1;store.set('zoom',z.toFixed(1));apply()});
q('[data-g9-font]').forEach(b=>b.onclick=()=>q('[data-g9-zoom="'+b.dataset.g9Font+'"]')[0]?.click());
function initFigure(f){if(f.dataset.g9Init)return;f.dataset.g9Init='1';const ids=(f.dataset.g9Stages||'').split(' ').filter(Boolean);if(ids.length<2)return;let i=0;
const show=()=>{ids.forEach((id,n)=>q('[data-g9-stage-id="'+id+'"]',f).forEach(g=>g.style.display=n<=i?'':'none'));const l=q('[data-g9-stage-label]',f)[0];if(l)l.textContent='Stage '+(i+1)+' of '+ids.length};show();
q('[data-g9-stage-step]',f).forEach(b=>b.onclick=()=>{i=Math.max(0,Math.min(ids.length-1,i+(b.dataset.g9StageStep==='next'?1:-1)));show()})}
function nextRung(l){const t=q('template[data-g9-rung-payload]',l)[0];if(!t)return false;q('[data-g9-ladder]',l)[0].append(t.content.cloneNode(true));t.remove();const b=q('[data-g9-next-rung]',l)[0];if(b&&!q('template[data-g9-rung-payload]',l).length)b.disabled=true;return true}
function materialise(a){q('details[data-g9-payload-ref]',a).forEach(d=>{const slot=q('[data-g9-payload-slot]',d)[0];if(!slot||slot.dataset.g9Filled)return;const t=q('template[data-g9-payload]',a).find(x=>x.dataset.g9Payload===d.dataset.g9PayloadRef);if(!t)return;slot.replaceChildren(t.content.cloneNode(true));slot.dataset.g9Filled='1';q('figure[data-g9-figure]',slot).forEach(initFigure)})}
const number=t=>{const v=t.trim();if(!/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?(?:\s*\/\s*[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:e[+-]?\d+)?)?$/i.test(v))return false;const p=v.split('/').map(x=>Number(x.trim()));return p.every(Number.isFinite)&&(p.length===1||p[1]!==0)};
function validAttempt(box){const type=box.dataset.g9ResponseType;if(type==='single_choice'||type==='multiple_choice'||type==='true_false')return q('[data-g9-choice]:checked',box).length>0;
if(type==='numeric')return number(q('[data-g9-number]',box)[0]?.value||'');if(type==='short_text')return !!q('[data-g9-attempt]',box)[0]?.value.trim();
if(type==='match'){const fields=q('[data-g9-match]',box);return fields.length>0&&fields.every(x=>x.value!=='')}
if(q('[data-g9-paper]:checked',box).length)return true;if(type==='multipart'){const fields=q('[data-g9-part-input]',box);return fields.length>0&&fields.every(x=>x.value.trim()&&(!x.dataset.g9PartType||x.dataset.g9PartType!=='numeric'||number(x.value)))}
return !!q('[data-g9-attempt]',box)[0]?.value.trim()}
const articles=q('article[data-g9-unit],article[data-g9-diagnostic]');
articles.forEach(a=>{const lock=()=>q('details[data-requires-attempt]',a).forEach(d=>{if(!a.dataset.attempted){d.dataset.locked='';d.open=false}else delete d.dataset.locked});lock();
q('details[data-requires-attempt] summary',a).forEach(s=>s.addEventListener('click',e=>{if(!a.dataset.attempted){e.preventDefault();q('[data-g9-attempt-box] input,[data-g9-attempt-box] textarea,[data-g9-attempt-box] select',a)[0]?.focus()}}));
q('[data-g9-commit]',a).forEach(b=>b.onclick=()=>{const box=b.closest('[data-g9-attempt-box]');if(!box||!validAttempt(box)){q('input,textarea,select',box||a)[0]?.focus();return}a.dataset.attempted='1';lock();materialise(a)});
q('[data-g9-next-rung]',a).forEach(b=>b.onclick=()=>nextRung(b.closest('.g9-ladder')))});
window.g9MaterialiseAll=()=>articles.forEach(a=>{a.dataset.attempted='1';q('details[data-requires-attempt]',a).forEach(d=>delete d.dataset.locked);materialise(a);q('.g9-ladder',a).forEach(l=>{while(nextRung(l)){};})});
q('figure[data-g9-figure]').forEach(initFigure);
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


def shell(ctx: Ctx, role: str, mode: str) -> tuple[str, str]:
    m = ctx.manifest
    if mode == "EMBED":
        return "", ""
    nav_links = "".join(
        f'<a href="{"#g9-role-" + r if mode == "SINGLE_FILE" else ROLE_FILE[r]}"'
        f'{" aria-current=page" if mode != "SINGLE_FILE" and r == role else ""}>{esc(r)}</a>'
        for r in ROLES
    )
    home_href = _mode_href(m["home_href"], mode)
    question_bank_href = _mode_href(m.get("question_bank_href", m["home_href"]), mode)
    header = (f'<header data-g9-shell-header><a data-g9-home href="{esc(home_href)}">Home</a>'
              f'<button type="button" onclick="history.back()">Back</button>'
              f'<a href="{esc(question_bank_href)}">Question bank</a>'
              f'<button type="button" data-g9-action="search">Search</button>'
              f'<button type="button" data-g9-action="display">Display</button>'
              f'<div data-g9-search-panel hidden><input data-g9-search-input type="search" aria-label="Search this page"></div>'
              f'<div data-g9-display-panel hidden><button type="button" data-g9-font="dec">A−</button><button type="button" data-g9-font="reset">A</button>'
              f'<button type="button" data-g9-font="inc">A+</button><button type="button" data-g9-theme="light">Light</button>'
              f'<button type="button" data-g9-theme="dark">Dark</button><button type="button" data-g9-zoom="dec">Zoom −</button>'
              f'<button type="button" data-g9-zoom="reset">100%</button><button type="button" data-g9-zoom="inc">Zoom +</button></div></header>')
    product_href = "#g9-role-CORE1" if mode == "SINGLE_FILE" else "index.html"
    crumbs = (f'<nav data-g9-breadcrumb aria-label="Breadcrumb"><a href="{esc(home_href)}">Home</a>'
              f'<a href="{product_href}">{esc(m["title"])}</a>{nav_links}</nav>')
    return header, crumbs


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
        return '<style data-g9-tablet-shell>' + TABLET_CSS.read_text(encoding="utf-8") + '</style>'
    root = _asset_root(ctx)
    return f'<link rel="stylesheet" href="{esc(root)}css/tablet-12-7.css">'


def page(ctx: Ctx, role: str, mode: str, digest: str) -> str:
    bp = next(b for b in ctx.blueprints["blueprints"] if role in b["core_roles"])
    stage_support = bp["responsive_policy"].get("expanded") == "STAGE_SUPPORT"
    articles = ""
    klass = ' class="g9-stage-support"' if stage_support else ""
    for rec in units_for(ctx, role):
        kind = "CONCEPT" if role in {"CORE1", "CORE1A", "CORE1B"} else "QUESTION"
        search_text = metadata_search_text(ctx, role, rec)
        articles += (f'<article id="{esc(rec["id"])}" data-g9-unit="{esc(rec["id"])}" data-g9-kind="{kind}"'
                     f' data-g9-search-text="{esc(search_text)}"{klass}>{RENDER[role](ctx, rec)}</article>')
    header, crumbs = shell(ctx, role, mode)
    m = ctx.manifest
    return ("<!doctype html>\n"
            f'<html lang="en" data-g9-shell data-g9-role="{role}" data-g9-mode="{mode}">'
            '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="g9-render" content="{RENDERER_VERSION} {digest}">'
            f'{_shared_head_assets(ctx, mode)}'
            f'<title>{esc(ROLE_TITLE[role])} · {esc(m["title"])}</title><style>{CSS}</style></head>'
            f'<body data-core="{role}" data-blueprint-ref="{esc(bp["id"])}@{esc(bp["version"])}">'
            f'{header}{crumbs}<noscript>Answers open after you attempt; this page needs JavaScript.</noscript>'
            f'<main><h1>{esc(m["title"])}: {esc(ROLE_TITLE[role])}</h1>'
            f'{_core1a_bucket_orientation(ctx) if role == "CORE1A" else ""}{articles}</main>'
            f'<footer data-g9-footer>{esc(m["subject"])} · {esc(m["title"])}</footer>'
            f"<script>{JS}</script></body></html>\n")


def index_page(ctx: Ctx, digest: str) -> str:
    m = ctx.manifest
    header, crumbs = shell(ctx, "CORE1", "PAGES")
    links = "".join(f'<li><a href="{ROLE_FILE[r]}">{esc(r)}: {esc(ROLE_TITLE[r])}</a></li>' for r in ROLES)
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
            f'<html lang="en" data-g9-shell data-g9-role="INDEX"><head><meta charset="utf-8">'
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
            if schema_path == BANK_SCHEMA and path.parent.name != "exam-bank":
                # Fixture and exemplar banks are not canonical bank publications.
                continue
            errors = sorted(validator.iter_errors(record), key=lambda error: tuple(str(x) for x in error.absolute_path))
            if errors:
                error = errors[0]
                location = "/".join(str(x) for x in error.absolute_path) or "<root>"
                raise ValueError(f"PRODUCT_STRUCTURE_INVALID: {path}: {location}: {error.message}")
    manifest["title"] = (next((p.get("title") for p in packages if p.get("title")), None)
                         or next((b.get("title") for p in packages for b in p.get("buckets", []) if b.get("title")), None)
                         or manifest["product_id"].replace("-", " ").title())
    bank = [q for p in bank_paths for q in load_json(p).get("questions", [])]
    selection_rows = product_manifest.validate_selection(manifest, packages, bank)
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
    })
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
        ("product-manifest-source", _file_sha256(PRODUCT_MANIFEST_SOURCE)),
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
    for old in article_ids:
        fragment = fragment.replace(f'id="{old}"', f'id="g9-{role}--{old}"', 1)
    file_to_role = {ROLE_FILE[r]: r for r in ROLES}
    def cross_link(m: re.Match[str]) -> str:
        target_role = file_to_role.get(m.group(1))
        return f'href="#g9-{target_role}--{m.group(2)}"' if target_role else m.group(0)
    fragment = re.sub(r'href="(core\w+\.html)#([^"]+)"', cross_link, fragment)
    for old in article_ids:
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
    ctx = context(manifest_path)
    role_pages = {ROLE_FILE[r]: page(ctx, r, mode, DIGEST_SLOT) for r in ROLES}
    if mode == "SINGLE_FILE":
        bodies = "".join(
            f'<section id="g9-role-{r}" data-g9-role-section="{r}">'
            f'{_single_file_fragment(role_pages[ROLE_FILE[r]], r)}</section>'
            for r in ROLES
        )
        product = role_pages[ROLE_FILE["CORE1"]].replace(
            re.search(r"<main>(.*)</main>", role_pages[ROLE_FILE["CORE1"]], re.S).group(1),
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

    # the same gap can be met on several pages
    seen, gaps = set(), []
    for g in ctx.gaps:
        key = (g["duty"], g["record"])
        if key not in seen:
            seen.add(key)
            gaps.append(g)
    return pages, gaps, digest



def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--manifest", required=True)
    b.add_argument("--out", required=True)
    b.add_argument("--mode", choices=MODES, default="PAGES")
    b.add_argument("--draft", action="store_true", help="write a draft even when gaps remain (never published)")
    g = sub.add_parser("gaps")
    g.add_argument("--manifest", required=True)
    args = parser.parse_args(argv)
    pages, gaps, digest = build(Path(args.manifest), getattr(args, "mode", "PAGES"))
    if args.cmd == "gaps":
        for gap in gaps:
            print(f"{gap['core']:7s} {gap['duty']:32s} {gap['record']:44s} {gap['detail']}")
        authority_findings = subject_authority_findings(Path(args.manifest))
        for finding in authority_findings:
            print(f"AUTHORITY {finding['point']:28s} {finding['record']:44s} {finding['detail']}")
        print(f"{len(gaps)} depth gap(s); {len(authority_findings)} subject-authority finding(s)")
        return 1 if gaps or authority_findings else 0
    if gaps and not args.draft:
        print(f"{len(gaps)} gap(s): nothing written. Run `render_core.py gaps` or `--draft`.", file=sys.stderr)
        return 2
    out = Path(args.out)
    if out.resolve().is_relative_to((REPO / "public").resolve()):
        raise ValueError("render_core cannot write to public; use Owner acceptance of a staged render")
    out.mkdir(parents=True, exist_ok=True)
    for name, text in pages.items():
        if gaps:
            text = text.replace("<html ", '<html data-g9-draft="%d" ' % len(gaps), 1)
        (out / name).write_bytes(text.encode("utf-8"))
    manifest_path = Path(args.manifest).resolve()
    try:
        manifest_ref = manifest_path.relative_to(REPO.resolve()).as_posix()
    except ValueError:
        manifest_ref = manifest_path.as_posix()
    (out / "render-receipt.json").write_text(json.dumps({
        "renderer": RENDERER_VERSION, "digest": digest,
        "semantic_digest": semantic_metadata_digest(pages, args.mode),
        "manifest": manifest_ref, "mode": args.mode,
        "draft": bool(gaps), "gaps": gaps, "pages": sorted(pages),
        "ledger": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("ledger", []),
        "diagnostic_min": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("diagnostic_min", 0)},
        indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(pages)} page(s) to {out}" + (f" as DRAFT with {len(gaps)} gap(s)" if gaps else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
