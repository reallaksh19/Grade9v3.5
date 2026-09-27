#!/usr/bin/env python3
"""The one renderer for learner Core pages.

Renders the six Core roles of a product from library records (schema 0.2.0) and a product
manifest. It renders only through the role's blueprint slots
(Shared/web/interactive-page-blueprints.v1.json) and inside the tablet shell
(docs/specs/TABLET-SHELL-AND-NAVIGATION.md). Every block, figure stage, reveal, attempt
control and hint rung is marked with a data-g9-* attribute, so the rendered quality gate
(Shared/tools/quality_gate.py) judges exactly what the learner receives.

The renderer never writes academic text of its own. Everything the learner reads comes from a
record, and a required record field that is missing is a *gap*: a typed duty
(RENDERER/AUTHOR/RESEARCHER). A product with gaps is written only as a draft, marked
data-g9-draft, which the gate refuses and navigation never links.

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
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

BLUEPRINTS = REPO / "Shared/web/interactive-page-blueprints.v1.json"
CONTRACT = REPO / "Shared/quality/learner-quality.v1.json"
ROLES = ["CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"]
ROLE_FILE = {r: r.lower() + ".html" for r in ROLES}
ROLE_TITLE = {"CORE1": "Orientation map", "CORE1A": "Construction", "CORE1B": "Reconstruction",
              "CORE2": "Source questions", "CORE2A": "Supported practice", "CORE2B": "Transfer"}
MODES = ("PAGES", "EMBED", "SINGLE_FILE")
RENDERER_VERSION = "render_core/1"


class RenderGapError(Exception):
    """Raised in strict mode when the product cannot be rendered without gaps."""


@dataclass
class Ctx:
    manifest: dict
    packages: list[dict]
    bank: list[dict]
    blueprints: dict
    gaps: list[dict] = field(default_factory=list)

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


def reveal(summary: str, body: str, gated: bool = True) -> str:
    if not body:
        return ""
    return (f'<details data-g9-reveal{" data-requires-attempt" if gated else ""}>'
            f'<summary>{esc(summary)}</summary>{body}</details>')


def attempt_box(label: str) -> str:
    return (f'<div class="g9-attempt"><label>{esc(label)}<textarea data-g9-attempt rows="4"></textarea></label>'
            f'<button type="button" data-g9-commit>I have attempted this</button></div>')


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
                row = (pkg["subject"], str(path.relative_to(REPO)), mics.get(c["id"]), titles.get(c["id"]) or c.get("action"))
                _TEACHERS[c["id"]] = row
                _TEACHERS[f"{pkg['subject']}:{c['id']}"] = row
    return _TEACHERS


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
    rel_html = "".join(f'<div class="g9-relation"><p class="g9-expr">{esc(r["expression"])}</p>{para(r.get("meaning"))}'
                       f'{items(r.get("conditions"))}</div>' for r in rels)
    # The compact anchor's own figure; the microtopic's first representation is often shared across the map.
    rep = (anchor or {}).get("representation_ref") or (m.get("representation_refs") or [None])[0]
    body = (slot("identity", block("scope", f"<h2>{esc(m['title'])}</h2>"), True)
            + slot("orientation",
                   block("hard_transition", para(m["inferential_jump"]), title="Hard transition")
                   + figure(ctx, rep, "TEACHING", "CORE1", m["id"])
                   + block("governing_relation", rel_html, title="Governing relation")
                   + block("compact_anchor", (para(anchor["prompt"]) + para(anchor["result"])) if anchor else "", title="Compact anchor")
                   + block("exit_prompt", para((m.get("exit_task") or {}).get("prompt")), title="Before you go on"), True))
    return body


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
        anchor_html = ""
        if anchor_q:
            ans = anchor_q["answer"]
            anchor_html = para(anchor_q["stem"]) + items(ans.get("reasoning"), True) + para(ans.get("summary"))
        checks = [c["statement"] for c in u.get("independent_checks") or []]
        if not checks:
            ctx.gap("AUTHOR_INDEPENDENT_CHECK", u["id"], "no independent check", "CORE1A")
        wrong = _misconceptions(m, u)
        heading = f"<h3>{esc(decision)}</h3>" if decision else (f"<h3>Construction step {n + 1} of {len(units)}</h3>" if len(units) > 1 else "")
        unit_html += (f'<section class="g9-cu" data-g9-cu="{esc(u["id"])}">{heading}'
                      + block("construction", f"<ol>{step_html}</ol>")
                      + figure(ctx, u.get("representation_ref"), "TEACHING", "CORE1A", u["id"])
                      + block("worked_anchor", anchor_html, title="Worked example")
                      + block("wrong_path", items(w["wrong_idea"] for w in wrong), title="A tempting wrong path")
                      + block("diagnose", items(w["diagnostic_prompt"] for w in wrong), title="Diagnose")
                      + block("repair", items(w["repair"] for w in wrong), title="Repair")
                      + block("independent_check", items(checks), title="Check it independently")
                      + "</section>")
    exit_task = m.get("exit_task") or {}
    return (slot("identity", f"<h2>{esc(m['title'])}</h2>"
                 + block("entry_assumptions", items(m.get("entry_assumptions")) + _prereqs(ctx, m), title="You need")
                 , True)
            + slot("construction", block("inferential_jump", para(m["inferential_jump"]), title="The key step") + unit_html, True)
            + slot("repair_closure",
                   block("exit_task", para(exit_task.get("prompt")), title="Exit task")
                   + attempt_box("Your answer")
                   + reveal("Model answer", block("exit_answer", para((exit_task.get("answer") or {}).get("summary"))
                                                  + items((exit_task.get("answer") or {}).get("reasoning"), True))), True))


def core1b(ctx: Ctx, m: dict) -> str:
    e = m.get("elicitation")
    if not e:
        ctx.gap("AUTHOR_ELICITATION", m["id"], "no predict/attempt/reconstruct/boundary cycle", "CORE1B")
        return slot("identity", f"<h2>{esc(m['title'])}</h2>", True)
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
    return (slot("identity", f"<h2>{esc(m['title'])}</h2>", True)
            + slot("attempt",
                   block("predict", para((e.get("predict") or {}).get("prompt")), title="Predict")
                   + figure(ctx, task_rep, "PRE_ATTEMPT", "CORE1B", m["id"], first_stage_only=True,
                            allowed=(task or {}).get("stage_refs") or None)
                   + block("attempt_prompt", (para(task["prompt"]) + items(task.get("givens")) + (
                       f'<p class="g9-prov">Your answer should contain: {esc(att["produces"])}</p>' if att.get("produces") else ""))
                       if task else "", title="Attempt")
                   + attempt_box("Your attempt"), True)
            + slot("reconstruction",
                   reveal("Reconstruct", block("reconstruct", items((r["ask"] for r in rec.get("route") or []), True))
                          + block("diagnose", items(w["diagnostic_prompt"] for w in wrong), title="Diagnose")
                          + block("repair", items(w["repair"] for w in wrong), title="Repair")
                          + block("model_response", para(model) + items(att.get("accepted")), title="What a complete answer does")
                          + block("rejoin_jump", para(m["inferential_jump"]), title="The step you rebuilt")
                          + figure(ctx, task_rep, "POST_ATTEMPT", "CORE1B", m["id"] + "-full"))
                   + block("boundary_test", para(bt.get("prompt")), title="Boundary test")
                   + reveal("Boundary answer", block("boundary_answer", para(bt.get("answer")) + para(bt.get("confirms")))), True))


def _identity(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    parts = [cust.get("exam"), cust.get("year"), cust.get("paper"), f"Q{cust['question_number']}" if cust.get("question_number") else None]
    return " · ".join(str(p) for p in parts if p) or q.get("original_identifier", "")


def _custody(q: dict) -> str:
    cust = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
    wording = {"FAITHFUL_NON_VERBATIM_RESTATEMENT": "faithful restatement of the original"}.get(cust.get("wording_custody"), "")
    return "Official past paper" + (f", {wording}" if wording else "")


def core2(ctx: Ctx, q: dict) -> str:
    ans = q["answer"]
    # A source option keeps its own label ("(A)", "(1)") because the key refers to it; unlabelled ones get a letter.
    labelled = re.compile(r"\s*\(?[A-Za-z0-9]{1,2}[).]\s")
    stem = q["stem"] + ((" " + " ".join(str(o) if labelled.match(str(o)) else f"({chr(97 + i)}) {o}"
                                          for i, o in enumerate(q["options"]))) if q.get("options") else "")
    return (slot("identity", block("source_identity", f"<h2>{esc(_identity(q))}</h2><p class=\"g9-prov\">{esc(_custody(q))}</p>"), True)
            + slot("attempt", block("stem", para(stem)) + block("conditions", items(q.get("conditions")), title="Conditions")
                   + attempt_box("Your answer"), True)
            + slot("solution", reveal("Answer and working", block("answer", para(ans.get("summary")))
                                      + block("working", items(ans.get("reasoning"), True))), True))


def _ladder(ctx: Ctx, q: dict, role: str) -> str:
    rungs = sorted(q.get("hint_ladder") or [], key=lambda r: r["order"])
    texts = []
    for r in rungs:
        if r.get("text"):
            texts.append(r["text"])
        elif r.get("from"):
            kind, i = re.match(r"(hints|scaffolds)\[(\d+)\]", r["from"]).groups()
            texts.append((q.get(kind) or [])[int(i)]["text"])
    if len(texts) < 3:
        ctx.gap("AUTHOR_HINT_LADDER", q["id"], f"{len(texts)} rung(s); need 3", role)
    if not texts:
        return ""
    lis = "".join(f'<li data-g9-rung="{n + 1}"{"" if n == 0 else " hidden"}>{esc(t)}</li>' for n, t in enumerate(texts))
    return (f'<div class="g9-ladder"><ol data-g9-ladder>{lis}</ol>'
            f'<button type="button" data-g9-next-rung>Next hint</button></div>')


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
                 + block("family_identity", para(_family_title(ctx, fam.get("family_ref") or q.get("family_ref")))), True)
            + slot("attempt", block("stem", f"<h2>{esc(q['stem'])}</h2>")
                   + block("conditions", items(q.get("conditions")), title="Conditions")
                   + figure(ctx, roles.get("initial_ref"), "PRE_ATTEMPT", "CORE2A", q["id"], allowed=roles.get("stage_refs"))
                   + attempt_box("Your attempt"), True)
            + slot("support", _ladder(ctx, q, "CORE2A"), False)
            + slot("reasoning", reveal("Reasoning route and full solution",
                                       block("reasoning_route", f"<ol>{route}</ol>" if route else "")
                                       + figure(ctx, roles.get("bound_ref"), "POST_ATTEMPT", "CORE2A", q["id"] + "-bound")
                                       + block("solution", items(ans.get("reasoning"), True))
                                       + block("answer", para(ans.get("summary")), title="Answer")
                                       + block("independent_check", para(check), title="Independent check")
                                       + block("failure_signal", para(q.get("failure_signal")), title="If you went wrong")
                                       + block("repair", _repair(ctx, q.get("repair_ref")), title="Repair")
                                       + block("exposure_closure", para(fam.get("closure")), title="What this establishes")), True))


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
                 + block("stem", f"<h2>{esc(q['stem'])}</h2>")
                 + block("lineage", f"<ul>{lineage}</ul>" if lineage else "", title="Builds on"), True)
            + slot("attempt", block("conditions", items(q.get("conditions")), title="Conditions")
                   + figure(ctx, roles.get("safe_ref"), "PRE_ATTEMPT", "CORE2B", q["id"], allowed=roles.get("stage_refs"))
                   + block("safe_support", para(rung_text), title="Where to start")
                   + attempt_box("Your commitment: the model or representation you choose, and your first relation"), True)
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
                            + block("repair", _repair(ctx, q.get("repair_ref")), title="Repair")), True))


RENDER = {"CORE1": core1, "CORE1A": core1a, "CORE1B": core1b, "CORE2": core2, "CORE2A": core2a, "CORE2B": core2b}


# ------------------------------------------------------------------ selection

def units_for(ctx: Ctx, role: str) -> list[dict]:
    mics = ctx.index("microtopics")
    sel = ctx.manifest["selection"]
    if role in {"CORE1", "CORE1A", "CORE1B"}:
        return [mics[i] for i in sel["microtopics"] if i in mics]
    qs = {**ctx.index("questions"), **{q["id"]: q for q in ctx.bank}}
    rows = [qs[i] for i in sel.get(role.lower(), []) if i in qs]
    if not rows:
        ctx.gap("ACQUIRE_SOURCE" if role == "CORE2" else "AUTHOR_PRACTICE", ctx.manifest["product_id"],
                f"no {role} items selected", role)
    return rows


# ------------------------------------------------------------------ page

CSS = """
:root{--g9-zoom:1;--bg:#f6f7fb;--fg:#172033;--card:#fff;--line:#d5dce6;--accent:#1f5fae;--muted:#52627a}
:root[data-theme=dark]{--bg:#0f1520;--fg:#e8edf5;--card:#18212f;--line:#2c394d;--accent:#8ab4f8;--muted:#a3b1c6}
html{font-size:calc(17px * var(--g9-zoom))}body{margin:0;background:var(--bg);color:var(--fg);font:1rem/1.6 system-ui,sans-serif}
header[data-g9-shell-header]{position:sticky;top:0;z-index:5;display:flex;flex-wrap:wrap;gap:8px;align-items:center;padding:8px 16px;background:var(--card);border-bottom:1px solid var(--line)}
header a,header button,button,summary,nav a{min-height:48px;min-width:48px;padding:10px 14px;box-sizing:border-box;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg);font:inherit;text-decoration:none;display:inline-flex;align-items:center;cursor:pointer}
nav[data-g9-breadcrumb]{display:flex;gap:8px;flex-wrap:wrap;padding:8px 16px}
main{max-width:1180px;margin:0 auto;padding:16px}
article[data-g9-unit]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px;margin:18px 0}
@media (min-width:1100px){article[data-g9-unit].g9-stage-support{display:grid;grid-template-columns:.68fr .32fr;gap:20px}
article.g9-stage-support>.slot-identity,article.g9-stage-support>.slot-attempt,article.g9-stage-support>.slot-construction,article.g9-stage-support>.slot-reconstruction,article.g9-stage-support>.slot-reasoning,article.g9-stage-support>.slot-post_attempt,article.g9-stage-support>.slot-solution{grid-column:1}
article.g9-stage-support>.slot-support,article.g9-stage-support>.slot-repair_closure{grid-column:2}}
textarea{width:100%;min-height:96px;font:inherit;border:1px solid var(--line);border-radius:10px;padding:10px;box-sizing:border-box;background:var(--card);color:var(--fg)}
details{border:1px solid var(--line);border-radius:10px;margin:12px 0;padding:0 12px}details[data-locked] summary{opacity:.55;cursor:not-allowed}
figure{margin:14px 0}figure svg{width:100%;height:auto;max-width:720px}figcaption{color:var(--muted)}
.g9-prov{color:var(--muted);font-size:.95rem}.g9-expr{font-family:ui-monospace,monospace;font-size:1.05rem}
h4{margin:.8em 0 .3em}:focus-visible{outline:3px solid var(--accent);outline-offset:2px}
footer{padding:24px 16px;color:var(--muted)}
@media print{header[data-g9-shell-header],nav[data-g9-breadcrumb],.g9-attempt,button,[data-g9-display-panel]{display:none!important}
details>*{display:block!important}details{border:none}article[data-g9-unit]{break-inside:avoid-page;border:none}
[data-g9-stage-id]{display:inline!important}body{background:#fff;color:#000}}
"""

JS = """
(()=>{const q=(s,r=document)=>[...r.querySelectorAll(s)];
const store={get:k=>{try{return localStorage.getItem('g9-'+k)}catch(e){return null}},set:(k,v)=>{try{localStorage.setItem('g9-'+k,v)}catch(e){}}};
const root=document.documentElement;const apply=()=>{root.dataset.theme=store.get('theme')||root.dataset.theme||'light';root.style.setProperty('--g9-zoom',store.get('zoom')||'1');};apply();
q('[data-g9-theme]').forEach(b=>b.onclick=()=>{store.set('theme',b.dataset.g9Theme);apply()});
q('[data-g9-zoom]').forEach(b=>b.onclick=()=>{let z=parseFloat(store.get('zoom')||'1');z=b.dataset.g9Zoom==='inc'?Math.min(1.6,z+0.1):b.dataset.g9Zoom==='dec'?Math.max(0.8,z-0.1):1;store.set('zoom',z.toFixed(1));apply()});
q('[data-g9-font]').forEach(b=>b.onclick=()=>q('[data-g9-zoom="'+b.dataset.g9Font+'"]')[0]?.click());
q('article[data-g9-unit]').forEach(a=>{const lock=()=>q('details[data-requires-attempt]',a).forEach(d=>{if(!a.dataset.attempted){d.dataset.locked='';d.open=false}else delete d.dataset.locked});lock();
q('details[data-requires-attempt] summary',a).forEach(s=>s.addEventListener('click',e=>{if(!a.dataset.attempted){e.preventDefault();q('[data-g9-attempt]',a)[0]?.focus()}}));
q('[data-g9-commit]',a).forEach(b=>b.onclick=()=>{const t=q('[data-g9-attempt]',a)[0];if(t&&t.value.trim().length<3){t.focus();return}a.dataset.attempted='1';lock()});
q('[data-g9-next-rung]',a).forEach(b=>b.onclick=()=>{const h=q('[data-g9-rung][hidden]',a)[0];if(h)h.hidden=false;if(!q('[data-g9-rung][hidden]',a).length)b.disabled=true});});
q('figure[data-g9-figure]').forEach(f=>{const ids=(f.dataset.g9Stages||'').split(' ').filter(Boolean);if(ids.length<2)return;let i=0;
const show=()=>{ids.forEach((id,n)=>q('[data-g9-stage-id="'+id+'"]',f).forEach(g=>g.style.display=n<=i?'':'none'));const l=q('[data-g9-stage-label]',f)[0];if(l)l.textContent='Stage '+(i+1)+' of '+ids.length};show();
q('[data-g9-stage-step]',f).forEach(b=>b.onclick=()=>{i=Math.max(0,Math.min(ids.length-1,i+(b.dataset.g9StageStep==='next'?1:-1)));show()})});
const input=q('[data-g9-search-input]')[0];if(input)input.oninput=()=>{const v=input.value.trim().toLowerCase();q('article[data-g9-unit]').forEach(a=>a.hidden=!!v&&!a.textContent.toLowerCase().includes(v))};
q('[data-g9-action="search"]').forEach(b=>b.onclick=()=>{const p=q('[data-g9-search-panel]')[0];p.hidden=!p.hidden;if(!p.hidden)input.focus()});
q('[data-g9-action="display"]').forEach(b=>b.onclick=()=>{const p=q('[data-g9-display-panel]')[0];p.hidden=!p.hidden});
})();
"""


def shell(ctx: Ctx, role: str, mode: str) -> tuple[str, str]:
    m = ctx.manifest
    if mode == "EMBED":
        return "", ""
    nav_links = "".join(f'<a href="{ROLE_FILE[r]}"{" aria-current=page" if r == role else ""}>{esc(r)}</a>' for r in ROLES)
    header = (f'<header data-g9-shell-header><a data-g9-home href="{esc(m["home_href"])}">Home</a>'
              f'<button type="button" onclick="history.back()">Back</button>'
              f'<a href="{esc(m.get("question_bank_href", m["home_href"]))}">Question bank</a>'
              f'<button type="button" data-g9-action="search">Search</button>'
              f'<button type="button" data-g9-action="display">Display</button>'
              f'<div data-g9-search-panel hidden><input data-g9-search-input type="search" aria-label="Search this page"></div>'
              f'<div data-g9-display-panel hidden><button type="button" data-g9-font="dec">A−</button><button type="button" data-g9-font="reset">A</button>'
              f'<button type="button" data-g9-font="inc">A+</button><button type="button" data-g9-theme="light">Light</button>'
              f'<button type="button" data-g9-theme="dark">Dark</button><button type="button" data-g9-zoom="dec">Zoom −</button>'
              f'<button type="button" data-g9-zoom="reset">100%</button><button type="button" data-g9-zoom="inc">Zoom +</button></div></header>')
    crumbs = (f'<nav data-g9-breadcrumb aria-label="Breadcrumb"><a href="{esc(m["home_href"])}">Home</a>'
              f'<a href="index.html">{esc(m["title"])}</a>{nav_links}</nav>')
    return header, crumbs


def render_digest(ctx: Ctx) -> str:
    h = hashlib.sha256()
    h.update(json.dumps(ctx.manifest, sort_keys=True).encode())
    for p in ctx.packages:
        h.update(json.dumps(p, sort_keys=True).encode())
    h.update(load_json(CONTRACT)["version"].encode())
    return h.hexdigest()[:16]


def page(ctx: Ctx, role: str, mode: str, digest: str) -> str:
    bp = next(b for b in ctx.blueprints["blueprints"] if role in b["core_roles"])
    stage_support = bp["responsive_policy"].get("expanded") == "STAGE_SUPPORT"
    articles = ""
    klass = ' class="g9-stage-support"' if stage_support else ""
    for rec in units_for(ctx, role):
        kind = "CONCEPT" if role in {"CORE1", "CORE1A", "CORE1B"} else "QUESTION"
        articles += (f'<article id="{esc(rec["id"])}" data-g9-unit="{esc(rec["id"])}" data-g9-kind="{kind}"'
                     f'{klass}>{RENDER[role](ctx, rec)}</article>')
    header, crumbs = shell(ctx, role, mode)
    m = ctx.manifest
    return ("<!doctype html>\n"
            f'<html lang="en" data-g9-shell data-g9-role="{role}" data-g9-mode="{mode}">'
            '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="g9-render" content="{RENDERER_VERSION} {digest}">'
            f'<title>{esc(ROLE_TITLE[role])} · {esc(m["title"])}</title><style>{CSS}</style></head>'
            f'<body data-core="{role}" data-blueprint-ref="{esc(bp["id"])}@{esc(bp["version"])}">'
            f'{header}{crumbs}<main><h1>{esc(m["title"])}: {esc(ROLE_TITLE[role])}</h1>{articles}</main>'
            f'<footer data-g9-footer>{esc(m["subject"])} · {esc(m["product_id"])}</footer>'
            f"<script>{JS}</script></body></html>\n")


def index_page(ctx: Ctx, digest: str) -> str:
    m = ctx.manifest
    header, crumbs = shell(ctx, "CORE1", "PAGES")
    links = "".join(f'<li><a href="{ROLE_FILE[r]}">{esc(r)}: {esc(ROLE_TITLE[r])}</a></li>' for r in ROLES)
    qs = {**ctx.index("questions"), **{q["id"]: q for q in ctx.bank}}
    diag_ids = m.get("diagnostic", [])
    if len(diag_ids) < m.get("diagnostic_min", 0):
        ctx.gap("AUTHOR_DIAGNOSTIC", m["product_id"], f"{len(diag_ids)} diagnostic item(s); need {m['diagnostic_min']}", "INDEX")
    diag = "".join(f'<article data-g9-diagnostic="{esc(i)}"><p>{esc(qs[i]["stem"])}</p>{attempt_box("Your answer")}'
                   f'{reveal("Check", para(qs[i]["answer"].get("summary")))}</article>' for i in diag_ids if i in qs)
    diag_html = f'<section data-g9-diagnostic-set><h2>Start here</h2>{diag}</section>' if diag else ""
    return ("<!doctype html>\n"
            f'<html lang="en" data-g9-shell data-g9-role="INDEX"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<meta name="g9-render" content="{RENDERER_VERSION} {digest}"><title>{esc(m["title"])}</title><style>{CSS}</style></head>'
            f'<body>{header}{crumbs}<main><h1>{esc(m["title"])}</h1>{diag_html}<ol>{links}</ol></main><script>{JS}</script></body></html>\n')


# ------------------------------------------------------------------ entry points

def context(manifest_path: Path) -> Ctx:
    manifest = load_json(manifest_path)
    packages = [load_json(REPO / p) for p in manifest["package_refs"]]
    bank = [q for b in manifest.get("bank_refs", []) for q in load_json(REPO / b).get("questions", [])]
    return Ctx(manifest, packages, bank, load_json(BLUEPRINTS))


def build(manifest_path: Path, mode: str = "PAGES") -> tuple[dict[str, str], list[dict], str]:
    ctx = context(manifest_path)
    digest = render_digest(ctx)
    pages = {ROLE_FILE[r]: page(ctx, r, mode, digest) for r in ROLES}
    index = index_page(ctx, digest)
    if mode != "EMBED":
        pages["index.html"] = index
    if mode == "SINGLE_FILE":
        bodies = "".join(f'<section data-g9-role-section="{r}">{re.search(r"<main>(.*)</main>", pages[ROLE_FILE[r]], re.S).group(1)}</section>'
                         for r in ROLES)
        pages = {"product.html": pages[ROLE_FILE["CORE1"]].replace(
            re.search(r"<main>(.*)</main>", pages[ROLE_FILE["CORE1"]], re.S).group(1), bodies)}
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
        print(f"{len(gaps)} gap(s)")
        return 1 if gaps else 0
    if gaps and not args.draft:
        print(f"{len(gaps)} gap(s): nothing written. Run `render_core.py gaps` or `--draft`.", file=sys.stderr)
        return 2
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    for name, text in pages.items():
        if gaps:
            text = text.replace("<html ", '<html data-g9-draft="%d" ' % len(gaps), 1)
        (out / name).write_text(text, encoding="utf-8")
    (out / "render-receipt.json").write_text(json.dumps({
        "renderer": RENDERER_VERSION, "digest": digest, "manifest": args.manifest, "mode": args.mode,
        "draft": bool(gaps), "gaps": gaps, "pages": sorted(pages),
        "ledger": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("ledger", []),
        "diagnostic_min": json.loads(Path(args.manifest).read_text(encoding="utf-8")).get("diagnostic_min", 0)},
        indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(pages)} page(s) to {out}" + (f" as DRAFT with {len(gaps)} gap(s)" if gaps else ""))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
