#!/usr/bin/env python3
"""Record what a delivered learner product shows, as a learner observation.

The quality contract (Shared/tools/quality_contract.py) judges observations, never the files
directly. This module turns delivered files into observations
(Shared/quality/learner-observation.schema.json).

Extractors, one per page family:
- `motion2d-generator-html`: the six Core pages of calibration specimen S1. Full unit extraction.
- `pdf-print`: a print product such as S2, with its figure count and producer.
- `markdown-prototype`, `research-first-preview`, `research-first-render`: specimens S3–S5.
  Product-level facts only (escape states, provenance, roles, Atlas).
- `question-bank-reference`: the owner's tablet question bank (reference R2).

These legacy extractors exist for calibration. The Phase 3 renderer marks every block, figure
stage and reveal with data-g9-* attributes, and needs a single extractor.

Usage:
    quality_observe.py specimen S1 [--out obs.json]
    quality_observe.py reference R2 [--out obs.json]
"""
from __future__ import annotations

import argparse
import html
import json
import re
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CORPUS = REPO / "benchmarks/quality-calibration"
CONTRACT = REPO / "Shared/quality/learner-quality.v1.json"
VOID = {"br", "img", "meta", "link", "input", "hr", "source", "col", "area", "base", "wbr", "path", "line",
        "circle", "rect", "polygon", "polyline", "ellipse", "use", "stop"}


# ------------------------------------------------------------------ tiny DOM

class Node:
    __slots__ = ("tag", "attrs", "children", "parent", "text")

    def __init__(self, tag, attrs=None, parent=None, text=None):
        self.tag, self.attrs, self.children, self.parent, self.text = tag, dict(attrs or {}), [], parent, text

    def iter(self):
        yield self
        for c in self.children:
            yield from c.iter()

    def find_all(self, tag=None, cls=None, attr=None):
        for n in self.iter():
            if n.tag is None:
                continue
            if tag and n.tag != tag:
                continue
            if cls and cls not in (n.attrs.get("class") or "").split():
                continue
            if attr and attr not in n.attrs:
                continue
            yield n

    def first(self, tag=None, cls=None, attr=None):
        return next(self.find_all(tag, cls, attr), None)

    def content(self) -> str:
        parts = [n.text for n in self.iter() if n.tag is None and not _inside(n, "style", "script")]
        return re.sub(r"\s+", " ", html.unescape(" ".join(parts))).strip()

    def ancestors(self):
        n = self.parent
        while n is not None:
            yield n
            n = n.parent


def _inside(node, *tags):
    return any(a.tag in tags for a in node.ancestors())


class _Builder(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=False)
        self.root = Node("#root")
        self.cur = self.root

    def handle_starttag(self, tag, attrs):
        node = Node(tag, attrs, self.cur)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.cur.children.append(Node(tag, attrs, self.cur))

    def handle_endtag(self, tag):
        n = self.cur
        while n is not None and n.tag != tag:
            n = n.parent
        if n is not None and n.parent is not None:
            self.cur = n.parent

    def handle_data(self, data):
        self.cur.children.append(Node(None, parent=self.cur, text=data))

    def handle_entityref(self, name):
        self.handle_data(f"&{name};")

    def handle_charref(self, name):
        self.handle_data(f"&#{name};")


def parse(text: str) -> Node:
    b = _Builder()
    b.feed(text)
    return b.root


# ------------------------------------------------------------------ shared helpers

def thresholds() -> dict:
    return json.loads(CONTRACT.read_text(encoding="utf-8"))["thresholds"]


def placeholders_in(text: str) -> list[str]:
    found = []
    for pat in thresholds()["placeholder_patterns"]:
        for m in re.finditer(pat, text, re.IGNORECASE):
            found.append(text[max(0, m.start() - 30): m.end() + 10].strip())
    return found


def escape_states_in(text: str) -> list[str]:
    tokens = thresholds()["escape_state_tokens"]
    hits = re.findall(r"(?<![A-Za-z_])(" + "|".join(sorted(tokens, key=len, reverse=True)) + r")(?![A-Za-z_])", text)
    return sorted(set(hits))


def shell_facts(root: Node, raw: str) -> dict:
    home = False
    for a in root.find_all("a"):
        href = a.attrs.get("href", "")
        if re.fullmatch(r"(\.\./)+(index\.html)?|/|/Grade9V3/?", href) or a.content().strip().lower() in {"home", "app home"}:
            home = True
    home = home or root.first("a", attr="data-g9-home") is not None
    return {"home_link": home,
            "shell_header": root.first(attr="data-g9-shell-header") is not None,
            "slot_markers": sum(1 for _ in root.find_all(attr="data-blueprint-slot")),
            "print_css": "@media print" in raw}


def figure_of(svg: Node, stage: str) -> dict:
    titled = svg.first("title") is not None or bool(svg.attrs.get("aria-label") or svg.attrs.get("aria-labelledby"))
    fig = next((a for a in svg.ancestors() if a.tag == "figure"), None)
    stages = int(fig.attrs.get("data-reveal-stages", 1)) if fig is not None else 1
    return {"stage": stage, "titled": titled, "kind": None, "reveal_stages": stages}


# ------------------------------------------------------------------ S1: motion2d generator pages

LABELS = {
    "CORE1": {"hard transition": "hard_transition", "exit": "exit_prompt", "representation": "_reps"},
    "CORE1A": {"entry assumptions": "entry_assumptions", "inferential jump": "inferential_jump",
               "stepwise construction": "construction", "representation bridge": "representation_bridge",
               "worked conceptual anchor": "worked_anchor", "plausible wrong path": "wrong_path",
               "diagnostic": "diagnose", "repair": "repair", "independent checks and limits": "independent_check",
               "exit task": "exit_task", "model answer": "exit_answer"},
    "CORE1B": {"predict": "predict", "attempt": "attempt_prompt", "reconstruct · open after your attempt": "reconstruct",
               "diagnose → repair": ("diagnose", "repair"), "model response / rubric": "model_response",
               "rejoin the inferential jump": "rejoin_jump", "boundary test": "boundary_test",
               "boundary answer": "boundary_answer"},
    "CORE2": {"governed faithful restatement": "stem", "subparts": "stem", "conditions": "conditions",
              "options": "options", "figures and captions": "_figures", "source hints only": "source_hints",
              "source-answer custody": ("answer", "working")},
    "CORE2A": {"conditions": "conditions", "optional authored support": "_support",
               "your independent attempt": "_attempt", "reasoning route and full solution": ("reasoning_route", "solution"),
               "crux move": "reasoning_route", "answer": "answer", "independent check": "independent_check",
               "failure signal": "failure_signal", "repair pointer": "repair"},
    "CORE2B": {"prior-exposure lineage": "lineage", "conditions": "conditions", "safe pre-attempt support": "safe_support",
               "commit before support": "commitment", "post-attempt review and solution": "_post",
               "changed demand": "changed_demand", "protected decide move": "protected_move",
               "complete reasoning route": "reasoning_route", "answer": "answer", "justification rubric": "rubric",
               "independent check": "independent_check", "repair route": "repair", "accessible element list": "_a11y"},
}
QUESTION_ROLES = {"CORE2", "CORE2A", "CORE2B"}


def _label_of(node: Node) -> str | None:
    if node.tag in {"h3", "summary"}:
        return node.content()
    if node.tag == "strong":
        t = node.content()
        return t[:-1].strip() if t.endswith(":") else None
    return None


def _unit_s1(article: Node, role: str) -> dict:
    labels = LABELS[role]
    blocks: dict[str, list[str]] = {}
    order: list[str] = []
    reveals: dict[int, set] = {}
    current: tuple = ()
    figures, support = [], []
    question = role in QUESTION_ROLES

    def reveal_of(n):
        for a in n.ancestors():
            if a is article:
                return None
            if a.tag == "details" and not _inside(a, "figure"):
                return id(a)
        return None

    eyebrow = article.first(cls="eyebrow")
    if eyebrow is not None and role in {"CORE2A", "CORE2B"} and re.search(r"AUTHORED|SOURCE", eyebrow.content()):
        blocks["provenance"] = [eyebrow.content()]
        order.append("provenance")
    for n in article.iter():
        if n.tag == "div" and n is eyebrow:
            continue
        if eyebrow is not None and any(a is eyebrow for a in n.ancestors()):
            continue
        if n.tag == "h2":
            current = ("source_identity",) if role == "CORE2" else (("stem",) if question else ("_title",))
            continue
        label = _label_of(n) if n.tag else None
        if label is not None:
            key = label.lower().strip()
            if key in labels:
                mapped = labels[key]
                current = mapped if isinstance(mapped, tuple) else (mapped,)
            continue
        if n.tag == "svg":
            r = reveal_of(n)
            stage = "POST_ATTEMPT" if r is not None else ("PRE_ATTEMPT" if question else "TEACHING")
            figures.append(figure_of(n, stage))
            continue
        if n.tag is not None or not n.text.strip() or _inside(n, "svg", "style", "summary", "h3"):
            continue
        if n.parent.tag == "strong" and (n.text.strip().endswith(":")):
            continue
        text = html.unescape(n.text).strip()
        m = re.match(r"([A-Z][A-Za-z -]{2,40}):\s*(.*)", text)
        if m and m.group(1).lower() in labels:
            mapped = labels[m.group(1).lower()]
            current = mapped if isinstance(mapped, tuple) else (mapped,)
            text = m.group(2)
        for b in current:
            if b.startswith("_"):
                continue
            blocks.setdefault(b, []).append(text)
            if b not in order:
                order.append(b)
            r = reveal_of(n)
            if r is not None:
                reveals.setdefault(r, set()).add(b)
    details = [d for d in article.find_all("details") if not _inside(d, "figure")]
    scaffold = next((d for d in details if d.attrs.get("data-role") == "scaffold"), None)
    if scaffold is not None:
        support = [li.content() for li in scaffold.find_all("li")]
    reveal_rows = []
    for d in details:
        if d is scaffold:
            continue
        gated = "data-requires-attempt" in d.attrs
        reveal_rows.append({"blocks": sorted(reveals.get(id(d), set())), "gated": gated})
    text_all = article.content()
    unit = {
        "id": article.attrs.get("id", "?"),
        "kind": "QUESTION" if question else "CONCEPT",
        "concept_ref": article.attrs.get("id") if not question else None,
        "family_ref": None,
        "blocks": {k: " ".join(v).strip() for k, v in blocks.items() if " ".join(v).strip()},
        "block_order": order,
        "placeholders": placeholders_in(text_all),
        "figures": figures,
        "representation_refs_unmounted": re.findall(r"Canonical representation:\s*(REP-[A-Z0-9-]+)", text_all),
        "attempt": article.first("textarea") is not None,
        "reveals": reveal_rows,
        "support_levels": support,
        "lineage_refs": [],
    }
    if role == "CORE1A":
        unit["decisions"] = text_all.count("Why valid")
        unit["worked_anchors"] = sum(1 for h in article.find_all("h3") if h.content().lower() == "worked conceptual anchor")
        entry = _section_after(article, "Entry assumptions")
        unit["prerequisites_assumed"] = [li.content() for li in entry] if entry else []
        unit["prerequisites_bridged"] = [li.content() for li in (entry or []) if li.first("a") is not None]
    if role == "CORE2B":
        lineage = _section_after(article, "Prior-exposure lineage") or []
        unit["lineage_refs"] = [a.attrs.get("href") for li in lineage for a in li.find_all("a")] or \
            re.findall(r"core\w+\.html#[A-Z0-9-]+", " ".join(li.content() for li in lineage))
    return unit


def _section_after(article: Node, heading: str) -> list[Node] | None:
    """List items between the h3 `heading` and the next h3 (document order)."""
    seen, items = False, []
    for n in article.iter():
        if n.tag == "h3":
            if seen:
                break
            seen = n.content().lower() == heading.lower()
        elif seen and n.tag == "li":
            items.append(n)
    return items if seen else None


def observe_motion2d_pages(folder: Path, product_id: str, rendered: dict | None = None) -> dict:
    pages, roles, escape = [], [], set()
    for path in sorted(folder.glob("core*.html")):
        raw = path.read_text(encoding="utf-8")
        root = parse(raw)
        body = root.first("body")
        role = body.attrs.get("data-core")
        roles.append(role)
        escape |= set(escape_states_in(body.content()))
        units = [_unit_s1(a, role) for a in body.find_all("article")]
        r = (rendered or {}).get(path.name)
        pages.append({
            "role": role, "path": path.name, "blueprint_ref": body.attrs.get("data-blueprint-ref"),
            "shell": shell_facts(root, raw),
            "rendered": None if r is None else {
                "small_targets": r["viewports"]["android-landscape"]["smallTargets"],
                "stage_support_layout": r["viewports"]["android-landscape"]["stageSupportLayout"],
                "min_font_px": r["viewports"]["android-landscape"]["minFontPx"]},
            "figures": [], "units": units})
    return {"schema": "learner-observation/v1", "product_id": product_id, "subject": "Physics",
            "observed_by": "motion2d-generator-html",
            "provenance": {"render_stamp": None, "hand_authored": False},
            "escape_states": sorted(escape), "roles_rendered": sorted(set(roles)),
            "atlas": None, "print": None, "pages": pages}


# ------------------------------------------------------------------ S2: print product

def observe_pdf_print(folder: Path, product_id: str, web_figures: int) -> dict:
    from pypdf import PdfReader  # noqa: PLC0415
    figures, producers = 0, set()
    for pdf in sorted(folder.glob("*.pdf")):
        reader = PdfReader(str(pdf))
        producers.add(str((reader.metadata or {}).get("/Producer", "")))
        for page in reader.pages:
            figures += len(page.images)
            data = page.get_contents().get_data() if page.get_contents() else b""
            # A drawn figure shows up as path construction followed by a stroke or fill.
            paths = len(re.findall(rb"(?:^|\s)(?:re|c|v|y)\s", data))
            figures += 1 if paths >= 12 else 0
    from_page = any(re.search(r"Skia|Chrom|WebKit|Gecko", p) for p in producers)
    return {"schema": "learner-observation/v1", "product_id": product_id, "subject": "Physics",
            "observed_by": "pdf-print", "provenance": {"render_stamp": None, "hand_authored": False},
            "escape_states": [], "atlas": None,
            "print": {"present": True, "from_page": from_page, "figures": figures, "web_figures": web_figures},
            "pages": []}


# ------------------------------------------------------------------ S3–S5: product-level facts

def observe_markdown_prototype(folder: Path, product_id: str) -> dict:
    text = " ".join(p.read_text(encoding="utf-8") for p in sorted(folder.glob("CORE*.md")))
    holds = json.loads((folder / "hold-register.json").read_text(encoding="utf-8")) if (folder / "hold-register.json").is_file() else {}
    escape = set(escape_states_in(text)) | {h.get("status", "") for h in holds.get("holds", []) if h.get("status")}
    roles = sorted({m.upper() for m in re.findall(r"^CORE[12][AB]?", " ".join(p.stem for p in folder.glob("CORE*.md")), re.M)} |
                   {p.stem.upper() for p in folder.glob("CORE*.md")})
    return {"schema": "learner-observation/v1", "product_id": product_id, "subject": "Physics",
            "observed_by": "markdown-prototype", "provenance": {"render_stamp": None, "hand_authored": True},
            "escape_states": sorted(e for e in escape if e), "roles_rendered": roles,
            "atlas": None, "print": None, "pages": []}


def observe_research_first(folder: Path, product_id: str) -> dict:
    files = sorted(folder.rglob("*.html"))
    text = " ".join(parse(p.read_text(encoding="utf-8")).content() for p in files)
    roles = sorted({m for p in files for m in re.findall(r'data-core="(CORE[12][AB]?)"', p.read_text(encoding="utf-8"))})
    atlas_file = folder / "atlas" / "index.html"
    atlas = None
    if atlas_file.is_file():
        raw = atlas_file.read_text(encoding="utf-8")
        atlas = {"present": True, "shared_runtime": "topic-atlas.js" in raw or "data-g9-atlas" in raw}
    obs = {"schema": "learner-observation/v1", "product_id": product_id, "subject": "Physics",
           "observed_by": "research-first-render" if (folder / "pages").is_dir() else "research-first-preview",
           "provenance": {"render_stamp": None, "hand_authored": False},
           "escape_states": escape_states_in(text), "atlas": atlas, "print": None, "pages": []}
    if (folder / "pages").is_dir():
        obs["roles_rendered"] = roles
    return obs


# ------------------------------------------------------------------ R2: question-bank reference

def observe_question_bank(raw: str, product_id: str) -> list[dict]:
    root = parse(raw)
    by_subject: dict[str, list] = {}
    for sheet in root.find_all("section", cls="sheet"):
        if sheet.first(cls="hint-ladder-wrap") is None:
            continue
        domain = ""
        title = sheet.first(cls="chalkboard-title")
        if title is not None:
            spans = list(title.find_all("span"))
            domain = spans[-1].content() if spans else ""
        subject = "Chemistry" if domain.startswith(("REDOX", "MOLE")) else "Physics"
        blocks, order = {}, []

        def put(block, node):
            if node is not None and node.content():
                blocks[block] = (blocks.get(block, "") + " " + node.content()).strip()
                if block not in order:
                    order.append(block)
        footer = sheet.first(cls="page-footer")
        if footer is not None and "source identity" in footer.content():
            blocks["provenance"] = footer.content()
            order.append("provenance")
        put("stem", sheet.first(cls="stem-text"))
        put("conditions", sheet.first(cls="conditions-box"))
        put("reasoning_route", sheet.first(cls="first-move-card"))
        put("failure_signal", sheet.first(cls="trap-card"))
        put("solution", sheet.first(cls="stepwise-card"))
        answer = sheet.first(cls="answer-card")
        paras = list(answer.find_all("p")) if answer is not None else []
        if paras:
            put("answer", paras[0])
            for p in paras[1:]:
                put("independent_check", p)
        rungs = list(sheet.find_all("details", cls="hint-rung"))
        support = [f"{r.first(cls='hint-prompt').content()} {r.first(cls='hint-reveal').content()}".strip()
                   for r in rungs if r.first(cls="hint-prompt") is not None]
        figures = [figure_of(svg, "PRE_ATTEMPT") for svg in sheet.find_all("svg")
                   if any(a.attrs.get("class") == "chalkboard-svg-wrap" for a in svg.ancestors())]
        qid = sheet.first(cls="q-id")
        unit = {"id": (footer.content().split("|")[0].strip() if footer is not None else qid.content()),
                "kind": "QUESTION", "concept_ref": None, "family_ref": domain or None,
                "blocks": blocks, "block_order": order, "placeholders": placeholders_in(sheet.content()),
                "figures": figures, "attempt": False,
                "reveals": [{"blocks": [], "gated": "open" not in r.attrs} for r in rungs],
                "support_levels": support,
                "check_types": [t.content() for t in sheet.find_all(cls="audit-method-tag")]}
        by_subject.setdefault(subject, []).append(unit)
    return [{"schema": "learner-observation/v1", "product_id": f"{product_id}:{subject}", "subject": subject,
             "observed_by": "question-bank-reference",
             "provenance": {"render_stamp": None, "hand_authored": False}, "escape_states": [],
             "atlas": None, "print": None,
             "pages": [{"role": "CORE2A", "path": "canonical_question_bank_10inch_tablet.html", "blueprint_ref": None,
                        "shell": None, "rendered": None, "figures": [], "units": units}]}
            for subject, units in sorted(by_subject.items())]


# ------------------------------------------------------------------ render_core output

def _render_core_unit(article: Node) -> dict:
    blocks: dict[str, str] = {}
    order: list[str] = []
    for n in article.find_all(attr="data-g9-block"):
        name = n.attrs["data-g9-block"]
        blocks[name] = (blocks.get(name, "") + " " + n.content()).strip()
        if name not in order:
            order.append(name)
    figures = []
    for f in article.find_all("figure", attr="data-g9-figure"):
        svg = f.first("svg")
        figures.append({"stage": f.attrs.get("data-g9-stage", "TEACHING"),
                        "titled": svg is not None and (svg.first("title") is not None or bool(svg.attrs.get("aria-label"))),
                        "kind": f.attrs.get("data-g9-kind") or None,
                        "reveal_stages": int(f.attrs.get("data-reveal-stages", "1") or 1),
                        "stages_total": int(f.attrs.get("data-g9-stages-total") or 0)
                        or max(1, sum(1 for n in f.iter() if n.tag and "data-g9-stage-id" in n.attrs)),
                        "stages_in_dom": sum(1 for n in f.iter() if n.tag and "data-g9-stage-id" in n.attrs),
                        "asset_text": svg is not None and (svg.first("title") is not None or svg.first("desc") is not None),
                        "caption_source": (f.first("figcaption").attrs.get("data-g9-caption") if f.first("figcaption") else None),
                        "representation_ref": f.attrs.get("data-g9-representation"),
                        "mount": next((a.attrs["data-g9-cu"] for a in f.ancestors() if a.tag and "data-g9-cu" in a.attrs),
                                      article.attrs["data-g9-unit"])})
    payloads = {t.attrs["data-g9-payload"]: t for t in article.find_all("template", attr="data-g9-payload")}
    reveals = []
    for d in article.find_all("details", attr="data-g9-reveal"):
        ref = d.attrs.get("data-g9-payload-ref")
        content = payloads.get(ref, d) if ref else d
        inside = sorted({n.attrs["data-g9-block"] for n in content.find_all(attr="data-g9-block")})
        reveals.append({"blocks": inside, "gated": "data-requires-attempt" in d.attrs})
    prereqs = list(article.find_all("li", attr="data-g9-prereq"))
    metadata = []
    for node in article.find_all(attr="data-g9-meta-item"):
        strong = node.first("strong")
        display_name = strong.content().rstrip(":").strip() if strong is not None else ""
        text = node.content()
        prefix = f"{display_name}:" if display_name else ""
        label = text[len(prefix):].strip() if prefix and text.startswith(prefix) else text
        metadata.append({
            "kind": node.attrs.get("data-g9-meta-kind"),
            "ref": node.attrs.get("data-g9-meta-ref"),
            "value": node.attrs.get("data-g9-meta-value"),
            "display_name": display_name,
            "label": label,
        })
    return {
        "id": article.attrs["data-g9-unit"], "kind": article.attrs.get("data-g9-kind", "CONCEPT"),
        "concept_ref": article.attrs["data-g9-unit"] if article.attrs.get("data-g9-kind") == "CONCEPT" else None,
        "family_ref": None, "blocks": blocks, "block_order": order,
        "placeholders": placeholders_in(article.content()), "figures": figures,
        "representation_refs_unmounted": [],
        "attempt": article.first(attr="data-g9-attempt-box") is not None,
        "reveals": reveals,
        "support_levels": [li.content() for li in article.find_all("li", attr="data-g9-rung")],
        "decisions": sum(1 for _ in article.find_all("li", attr="data-g9-step")),
        "worked_anchors": sum(1 for n in article.find_all(attr="data-g9-block") if n.attrs["data-g9-block"] == "worked_anchor"),
        "prerequisites_assumed": [li.attrs["data-g9-prereq"] for li in prereqs],
        "prerequisites_bridged": [li.attrs["data-g9-prereq"] for li in prereqs if li.attrs.get("data-bridged") == "true"],
        "lineage_refs": [a.attrs.get("href") for a in article.find_all("a", attr="data-g9-lineage")],
        "metadata": metadata,
    }


def observe_render_core(folder: Path, product_id: str | None = None, subject: str | None = None,
                        rendered: dict | None = None) -> dict:
    """Observation of a render_core product directory (core*.html, optional print receipt)."""
    pages, roles, escape, stamp, draft = [], [], set(), None, False
    web_figures = 0
    for path in sorted(folder.glob("core*.html")):
        raw = path.read_text(encoding="utf-8")
        root = parse(raw)
        html_el = root.first("html")
        role = html_el.attrs.get("data-g9-role")
        draft = draft or "data-g9-draft" in html_el.attrs
        meta = next((m for m in root.find_all("meta") if m.attrs.get("name") == "g9-render"), None)
        stamp = stamp or (meta.attrs.get("content") if meta is not None else None)
        body = root.first("body")
        roles.append(role)
        escape |= set(escape_states_in(body.content()))
        units = [_render_core_unit(a) for a in body.find_all("article", attr="data-g9-unit")]
        web_figures += sum(len(u["figures"]) for u in units)
        r = (rendered or {}).get(path.name)
        pages.append({"role": role, "path": path.name, "blueprint_ref": body.attrs.get("data-blueprint-ref"),
                      "shell": shell_facts(root, raw),
                      "rendered": None if r is None else {
                          "small_targets": r["viewports"]["android-landscape"]["smallTargets"],
                          "stage_support_layout": r["viewports"]["android-landscape"]["stageSupportLayout"],
                          "min_font_px": r["viewports"]["android-landscape"]["minFontPx"],
                          "metadata_missing_units": r["viewports"]["android-landscape"]["metadataMissingUnits"],
                          "search_corpus_missing_units": r["viewports"]["android-landscape"]["searchCorpusMissingUnits"],
                          "protected_search_matches": r["viewports"]["android-landscape"]["protectedSearchMatches"],
                          "gated_open_before_attempt": r["viewports"]["android-landscape"]["gatedOpenBeforeAttempt"]},
                      "figures": [], "units": units})
    receipt = folder / "print-receipt.json"
    print_obs = None
    if receipt.is_file():
        rec = json.loads(receipt.read_text(encoding="utf-8"))
        print_obs = {"present": True, "from_page": rec.get("tool", "").startswith("print-product/"),
                     "figures": sum(p.get("figures", 0) for p in rec["pages"]), "web_figures": web_figures}
    render_receipt = folder / "render-receipt.json"
    meta = json.loads(render_receipt.read_text(encoding="utf-8")) if render_receipt.is_file() else {}
    return {"schema": "learner-observation/v1", "product_id": product_id or meta.get("manifest", folder.name),
            "subject": subject or "Physics", "observed_by": "render-core-html",
            "provenance": {"render_stamp": None if draft else stamp, "hand_authored": False},
            "escape_states": sorted(escape), "roles_rendered": sorted(set(roles)),
            "atlas": None, "print": print_obs, "pages": pages}


# ------------------------------------------------------------------ corpus entry points

def observe_specimen(spec: dict, repo: Path = REPO) -> dict:
    folder = repo / "benchmarks/quality-calibration" / spec["dir"]
    kind = spec.get("observe", {}).get("extractor")
    if kind == "motion2d-generator-html":
        rendered_path = spec["observe"].get("rendered_measurements")
        rendered = json.loads((repo / rendered_path).read_text(encoding="utf-8")) if rendered_path else None
        return observe_motion2d_pages(folder, spec["id"], rendered)
    if kind == "pdf-print":
        pair = spec["observe"]["print_of"]
        manifest = json.loads((repo / "benchmarks/quality-calibration/manifest.v1.json").read_text(encoding="utf-8"))
        web = observe_specimen(next(s for s in manifest["specimens"] if s["id"] == pair), repo)
        web_figures = sum(len(u["figures"]) for p in web["pages"] for u in p["units"])
        return observe_pdf_print(folder, spec["id"], web_figures)
    if kind == "markdown-prototype":
        return observe_markdown_prototype(folder, spec["id"])
    if kind in {"research-first-preview", "research-first-render"}:
        return observe_research_first(folder, spec["id"])
    raise SystemExit(f"specimen {spec['id']} has no known extractor ({kind})")


def observe_reference(ref: dict, repo: Path = REPO) -> list[dict]:
    src = ref["source"]
    path = next(f["path"] for f in src["files"] if f["path"].endswith(".html"))
    got = subprocess.run(["git", "-C", str(repo), "show", f"{src['commit']}:{path}"], capture_output=True)
    if got.returncode:
        raise SystemExit(f"reference {ref['id']} unreachable; run: git fetch origin {src['branch']}")
    return observe_question_bank(got.stdout.decode("utf-8"), ref["id"])


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("what", choices=["specimen", "reference"])
    parser.add_argument("id")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    manifest = json.loads((CORPUS / "manifest.v1.json").read_text(encoding="utf-8"))
    if args.what == "specimen":
        obs = observe_specimen(next(s for s in manifest["specimens"] if s["id"] == args.id))
    else:
        obs = observe_reference(next(r for r in manifest["references"] if r["id"] == args.id))
    text = json.dumps(obs, indent=2, ensure_ascii=False)
    if args.out:
        Path(args.out).write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
