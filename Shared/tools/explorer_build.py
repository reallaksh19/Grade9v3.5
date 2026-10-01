#!/usr/bin/env python3
"""Make a guided explorer for the toughest concept of a question set, from a spec, through the blueprint BP-EXPLORER-GCDR.

An explorer is not a sandbox. It is the route the repo's own standard asks for (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md):
the learner predicts before any control moves, manipulates toward goals, judges what was seen, imposes the tempting model and sees
it fail, watches the hidden mechanism appear cause by cause, rebuilds the mathematics from it, tries to break what survives, finds
where the shortcut stops, answers with the supports taken away, and does a fresh task with the explorer closed. The author writes
the content of each step as data; this tool writes the page, and Shared/tools/explorer_model.py checks every number in it.

    python3 Shared/tools/explorer_build.py new   TEST/products/SLUG.manifest.json     # scaffold TEST/interactive/SLUG/explorer.json
    python3 Shared/tools/explorer_build.py check TEST/interactive/SLUG                # the findings, with how to author each
    python3 Shared/tools/explorer_build.py build TEST/interactive/SLUG --out DIR      # the page, as a preview (deploy_test.py does the rest)
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import explorer_expr as expr  # noqa: E402
from Shared.tools import explorer_model as em  # noqa: E402
from Shared.tools import render_core, toughest_concept  # noqa: E402
from Shared.tools import web_blueprint_contract as blueprints  # noqa: E402

BUILDER = "explorer_build/1"
MODEL_JS = REPO / "Shared/web/explorer-model.js"
RUNTIME_JS = REPO / "Shared/web/explorer-runtime.js"
INTERACTIVE_ROOT = REPO / "TEST" / "interactive"
EXAMPLE_SPEC = REPO / "tests" / "fixtures" / "explorer" / "projectile-range.explorer.json"      # the worked example of the format, for another concept
SPEC_FILE = "explorer.json"
TITLES = {"CONTEXT": "Context", "PREDICT": "Predict", "MANIPULATE": "Try it", "OBSERVE": "Notice", "CONTRADICT": "Test the tempting model",
          "DECONSTRUCT": "See why", "RECONSTRUCT": "Build the maths", "INVARIANT": "Try to break it", "BOUNDARY": "Where it stops",
          "FADE": "With less help", "TRANSFER": "A fresh task"}
SHORT = {"CONTEXT": "Context", "PREDICT": "Predict", "MANIPULATE": "Try it", "OBSERVE": "Notice", "CONTRADICT": "Tempting model",
         "DECONSTRUCT": "Why", "RECONSTRUCT": "Maths", "INVARIANT": "Break it", "BOUNDARY": "Limits", "FADE": "Less help", "TRANSFER": "Fresh task"}
CONTINUE = {"CONTEXT": "Make my prediction", "PREDICT": "Lock in my prediction", "MANIPULATE": "I have seen what happens", "OBSERVE": "Continue",
            "CONTRADICT": "Show me why", "DECONSTRUCT": "Build the maths from it", "RECONSTRUCT": "Continue", "INVARIANT": "Continue",
            "BOUNDARY": "Continue", "FADE": "Continue", "TRANSFER": "Finish"}
# What each level of the fade takes away (the blueprint says three: numbers, then the relation, then everything but the scene).
FADE_LEVELS = [
    {"label": "the numbers on the picture are hidden.", "values": True},
    {"label": "the mechanism, the graph and the equation are hidden too: you supply the relation.", "values": True, "mechanism": True, "graph": True},
    {"label": "the physical scene only.", "values": True, "mechanism": True, "graph": True, "labels": True, "result": True},
]
SPEC_ORDER = ["schema", "slug", "title", "product", "blueprint_ref", "target", "context", "parameters", "quantities", "scene", "second_view",
              "predict", "manipulate", "observe", "contradict", "deconstruct", "reconstruct", "invariants", "oracles", "boundary", "fade", "transfer"]
ROLES = ["object", "given", "result", "wrong", "helper", "frame"]


def esc(value) -> str:
    return html.escape(str(value), quote=True)


# ------------------------------------------------------------------ what the page is built for

class Brief:
    """The toughest concept of the product, the owner's question for it, and where the product's pages are."""

    def __init__(self, manifest_path: Path) -> None:
        self.manifest_path = Path(manifest_path)
        self.ctx = render_core.context(self.manifest_path)
        self.brief = toughest_concept.derive(self.ctx.selection_rows.get("core2", []), self.ctx.selection_rows.get("microtopics", []))
        self.product = str(self.ctx.manifest.get("product_id") or self.manifest_path.name.split(".")[0])
        self.question = next((q for q in self.ctx.selection_rows.get("core2", []) if self.brief and q.get("id") == self.brief["question_ref"]), None)

    @classmethod
    def from_parts(cls, brief: dict | None, question: dict | None, product: str) -> "Brief":
        """A brief that is not read from a product (for tests, and for previewing a spec before a product exists)."""
        self = cls.__new__(cls)
        self.manifest_path, self.ctx, self.brief, self.question, self.product = None, None, brief, question, product
        return self

    def links(self) -> dict[str, str | None]:
        """Where the learner rejoins the question and the concept book, when the product's pages are deployed."""
        base = REPO / "public" / "test" / "products" / self.product
        out: dict[str, str | None] = {"question": None, "concept": None}
        if not self.brief:
            return out
        if (base / "core2.html").is_file():
            out["question"] = f"../../products/{self.product}/core2.html#{self.brief['question_ref']}"
        if (base / "core1a.html").is_file() and self.brief.get("microtopic_ref"):
            out["concept"] = f"../../products/{self.product}/core1a.html#{self.brief['microtopic_ref']}"
        return out


# ------------------------------------------------------------------ scaffold

def scaffold(manifest_path: Path, slug: str | None = None) -> dict:
    """An empty spec for the product's toughest concept: every field the blueprint lists, and what the records already say filled in."""
    brief = Brief(manifest_path)
    if not brief.brief:
        raise ValueError("the toughest concept is not chosen: no selected question carries a complete difficulty estimate")
    bp = em.blueprint()
    spec = copy.deepcopy(blueprints.skeleton(bp))
    slug = slug or brief.product
    rel = brief.manifest_path.resolve().relative_to(REPO).as_posix()
    spec.update({"schema": em.SPEC_VERSION, "slug": slug, "title": "", "product": rel, "blueprint_ref": f"{bp['id']}@{bp['version']}"})
    spec["target"]["question_ref"] = brief.brief["question_ref"]
    spec["target"]["failure"] = brief.brief.get("wrong_route") or ""
    spec["target"]["operation"] = (brief.brief.get("crux_move") or {}).get("action") or ""
    spec["title"] = ""
    return {key: spec[key] for key in SPEC_ORDER if key in spec}


def hints(bp: dict, components: list[str] | None = None) -> list[str]:
    out = []
    for cid, level, hint in blueprints.authoring_hints(bp):
        if components is None or cid in components:
            out.append(f"  {cid}: {hint}")
    return out


# ------------------------------------------------------------------ markup

def _lines(text: str) -> str:
    rows = [line.strip() for line in str(text or "").splitlines() if line.strip()]
    return "".join(f"<p>{esc(line)}</p>" for line in rows)


def _math(expression: str) -> str:
    return f'<span class="gx-math" data-g9-math="mathml">{expr.to_mathml(expression)}</span>'


def _card(cid: str, number: int, body: str) -> str:
    """One step of the route. The first is shown as it is; the page's script opens the others one at a time, as each is earned."""
    first = number == 1
    return (f'<section class="gx-card g9-c-route-step" id="gx-card-{cid}" data-gx-step="{cid}" data-g9-component="{cid}" '
            f'data-state="{"current" if first else "locked"}"{"" if first else " hidden"} aria-labelledby="gx-h-{cid}"><div class="gx-card-head"><h2 id="gx-h-{cid}"><span class="gx-n" aria-hidden="true">{number}</span>'
            f'<span class="gx-t">{esc(TITLES[cid])}</span></h2><p class="gx-sum" data-gx-summary></p></div>'
            f'<div class="gx-card-body">{body}'
            f'<div class="gx-actions"><button type="button" class="gx-primary" data-gx-continue disabled>{esc(CONTINUE[cid])}</button></div></div></section>')


def _goals(goals: list[dict]) -> str:
    rows = "".join(
        f'<li data-gx-goal="{i}" data-met="false"><span class="gx-check" aria-hidden="true"></span><div class="gx-goal-body">'
        f'<span class="gx-goal-text">{esc(g["prompt"])}</span> <span class="gx-goal-state sr-only">not yet</span>'
        f'<div class="gx-row"><button type="button" class="gx-mini" data-gx-hint aria-expanded="false">Hint</button>'
        f'<button type="button" class="gx-mini" data-gx-show>Show me</button></div><p class="gx-hint" hidden>{esc(g["hint"])}</p></div></li>'
        for i, g in enumerate(goals))
    return f'<ol class="gx-goals">{rows}</ol>'


def _tasks(tasks: list[dict]) -> str:
    rows = ""
    for i, task in enumerate(tasks):
        unit = f'<span class="gx-unit">{esc(task["unit"])}</span>' if task.get("unit") else ""
        rows += (f'<li data-gx-task="{i}" hidden><p class="gx-prompt">{esc(task["prompt"])}</p>'
                 f'<div class="gx-answer"><label>Your answer <input type="text" inputmode="decimal" autocomplete="off" data-gx-answer aria-label="Your answer"></label>{unit}'
                 f'<button type="button" class="gx-secondary" data-gx-check>Check</button></div>'
                 f'<div class="gx-feedback" hidden aria-live="polite"></div></li>')
    return f'<ol class="gx-tasks">{rows}</ol>'


def render_cards(spec: dict, brief: Brief) -> str:
    q = brief.question or {}
    label = toughest_concept.label_of(q) if q else spec["target"]["question_ref"]
    target = spec["target"]
    bodies: dict[str, str] = {}
    bodies["CONTEXT"] = (
        f'<blockquote class="gx-source" data-g9-component="SOURCE"><p class="gx-cite"><strong>{esc(label)}</strong> · the question this page is built for</p>'
        f'<div class="gx-stem">{_lines(q.get("stem", ""))}</div></blockquote>'
        f'<p class="gx-situation">{esc(spec["context"]["situation"])}</p>'
        f'<div class="gx-target" data-g9-component="TARGET"><p><span class="gx-tag">Most learners think</span> {esc(target["failure"])}</p>'
        f'<p><span class="gx-tag">The move to learn</span> {esc(target["operation"])}</p></div>')
    options = "".join(f'<label class="gx-option"><input type="radio" name="gx-predict" value="{i}"><span>{esc(o["text"])}</span></label>'
                      for i, o in enumerate(spec["predict"]["options"]))
    bodies["PREDICT"] = (f'<p class="gx-prompt">{esc(spec["predict"]["prompt"])}</p>'
                         f'<fieldset class="gx-options"><legend class="sr-only">Your prediction</legend>{options}</fieldset>'
                         '<p class="gx-note">Choose one. Your prediction is kept: the sliders unlock when you lock it in, and the page comes back to it.</p>')
    bodies["MANIPULATE"] = '<p class="gx-prompt">Use the sliders to reach each goal.</p>' + _goals(spec["manipulate"]["goals"])
    stmts = "".join(
        f'<li data-gx-statement="{i}"><p class="gx-stmt-text">{esc(s["text"])}</p>'
        f'<div class="gx-choice" role="group" aria-label="Agree or disagree"><button type="button" data-gx-agree aria-pressed="false">Agree</button>'
        f'<button type="button" data-gx-disagree aria-pressed="false">Disagree</button></div>'
        f'<div class="gx-feedback" hidden aria-live="polite"><p data-gx-verdict></p><p>{esc(s["why"])}</p>'
        f'<button type="button" class="gx-mini" data-gx-witness hidden>Show me where it fails</button></div></li>'
        for i, s in enumerate(spec["observe"]["statements"]))
    bodies["OBSERVE"] = ('<p class="gx-prompt">Do you agree? Test each statement on the sliders if you like.</p>'
                         f'<ul class="gx-statements">{stmts}</ul>'
                         '<div class="gx-recall" data-gx-recall hidden><p data-gx-recall-text></p>'
                         '<button type="button" class="gx-mini" data-gx-recall-show>Show me</button></div>')
    c = spec["contradict"]
    bodies["CONTRADICT"] = (
        f'<p class="gx-prompt">{esc(c["imposes"])}</p>'
        f'<button type="button" class="gx-toggle" data-gx-impose aria-pressed="false">Impose the tempting model: {esc(c["wrong_model"]["label"])}</button>'
        '<p class="gx-compare" data-gx-wrong-compare hidden>The tempting model says <output data-gx-wrong></output>; the real model says <output data-gx-true></output>.</p>'
        + _goals([c["goal"]])
        + f'<div class="gx-why" data-gx-why hidden><p><strong>Why the tempting model cannot be right.</strong> {esc(c["why_wrong"])}</p>'
          f'<p><strong>Why the real model works.</strong> {esc(c["why_correct"])}</p></div>')
    steps = ""
    for i, step in enumerate(spec["deconstruct"]["steps"]):
        ask = ""
        if step.get("ask"):
            a = step["ask"]
            opts = "".join(f'<button type="button" data-gx-ask-opt="{k}" aria-pressed="false">{esc(o)}</button>' for k, o in enumerate(a["options"]))
            ask = (f'<div class="gx-ask"><p class="gx-prompt">{esc(a["prompt"])}</p><div class="gx-choice" role="group" aria-label="Your answer">{opts}</div>'
                   '<p class="gx-feedback" hidden aria-live="polite"></p></div>')
        steps += f'<li data-gx-dstep="{i}" hidden><p>{esc(step["text"])}</p>{ask}</li>'
    bodies["DECONSTRUCT"] = (f'<ol class="gx-steps">{steps}</ol>'
                             '<button type="button" class="gx-secondary" data-gx-more>Show the next cause</button>')
    quantities = {row["id"]: row for row in spec["quantities"]}
    rsteps = ""
    for i, step in enumerate(spec["reconstruct"]["steps"]):
        row = quantities[step["quantity"]]
        unit = f' <span class="gx-unit">{esc(row.get("unit", ""))}</span>' if row.get("unit") else ""
        formula = _math(row["id"] + " == " + row["expr"])
        rsteps += (f'<li data-gx-rstep="{i}" hidden><p>{esc(step["text"])}</p><div class="gx-eq">{formula}'
                   f'<span class="gx-val">now <output data-gx-val>—</output>{unit}</span></div></li>')
    equation = spec["reconstruct"]["equation"]
    closed_form = _math(spec["target"]["quantity"] + " == " + equation["expr"])
    bodies["RECONSTRUCT"] = (
        f'<ol class="gx-derive">{rsteps}</ol>'
        '<button type="button" class="gx-secondary" data-gx-more>Show the next step</button>'
        f'<div class="gx-equation" data-gx-equation hidden><p>{esc(equation["text"])}</p><div class="gx-eq gx-eq-final">{closed_form}</div>'
        '<p class="gx-compare">The equation gives <output data-gx-eq-value></output>; the picture measures <output data-gx-eq-measured></output> <strong data-gx-eq-ok></strong></p>'
        '<p class="gx-note">Move the sliders to test it at two more positions: <output data-gx-eq-count>0</output> of 2.</p></div>')
    signs = {"==": "=", "<=": "≤", ">=": "≥"}
    invs = "".join(
        f'<li data-gx-inv="{i}"><p class="gx-inv-text">{esc(inv["text"])}</p><div class="gx-eq">{_math(inv["lhs"] + " " + inv["rel"] + " " + inv["rhs"])}</div>'
        f'<p class="gx-inv-live">Here: <output data-gx-inv-lhs></output> {signs[inv["rel"]]} <output data-gx-inv-rhs></output> <strong data-gx-inv-ok></strong></p>'
        f'<p class="gx-try">{esc(inv["try"])}</p>'
        '<p class="gx-note">Positions tried: <output data-gx-inv-count>0</output> of 5. Try five different ones; if it breaks anywhere, you will see it.</p></li>'
        for i, inv in enumerate(spec["invariants"]))
    bodies["INVARIANT"] = f'<p class="gx-prompt">What survives every position of the sliders?</p><ul class="gx-invs">{invs}</ul>'
    cases = "".join(
        f'<li data-gx-case="{i}"><p>{esc(cs["text"])}</p><button type="button" class="gx-mini" data-gx-go>Set the sliders here</button>'
        f'<p class="gx-compare" hidden>{esc(cs["shortcut_label"])} gives <output data-gx-sc></output>; the true value is <output data-gx-true></output>.</p>'
        '<div class="gx-choice" role="group" aria-label="Does the shortcut give the true value here?"><button type="button" data-gx-yes aria-pressed="false">It holds</button>'
        '<button type="button" data-gx-no aria-pressed="false">It fails</button></div><p class="gx-feedback" hidden aria-live="polite"></p></li>'
        for i, cs in enumerate(spec["boundary"]["cases"]))
    bodies["BOUNDARY"] = (f'<p class="gx-prompt">{esc(spec["boundary"]["assumption"])}</p><ol class="gx-cases">{cases}</ol>'
                          f'<div class="gx-takeaway" hidden><strong>Take away.</strong> {esc(spec["boundary"]["learner_must_identify"])}</div>')
    bodies["FADE"] = '<p class="gx-level" data-gx-level></p>' + _tasks(spec["fade"])
    bodies["TRANSFER"] = '<p class="gx-note">The explorer is closed for these. Work it out, then check.</p>' + _tasks(spec["transfer"])
    return "".join(_card(cid, i, bodies[cid]) for i, cid in enumerate(em.stages(em.blueprint()), 1))


def render_stage(spec: dict, compiled: dict) -> str:
    scene, view = spec["scene"], spec["second_view"]
    vw, vh = compiled["view_box"]
    markers = "".join(f'<marker id="gx-ah-{role}" viewBox="0 0 10 10" refX="8.5" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
                      f'<path d="M0 0L10 5L0 10z" class="gx-ah gx-r-{role}"/></marker>' for role in ROLES)
    sliders = ""
    for p in spec["parameters"]:
        if p.get("fixed"):
            continue
        unit = f'<span class="gx-unit">{esc(p.get("unit", ""))}</span>' if p.get("unit") else ""
        sliders += (f'<div class="gx-ctl" data-gx-param="{esc(p["id"])}"><label for="gx-p-{esc(p["id"])}"><span class="gx-ctl-name">{esc(p["label"])}</span> '
                    f'<span class="gx-ctl-val"><output data-gx-out="{esc(p["id"])}"></output>{unit}</span></label>'
                    f'<input type="range" id="gx-p-{esc(p["id"])}" min="{p["min"]}" max="{p["max"]}" step="{p["step"]}" value="{p["value"]}" disabled></div>')
    wrong = spec["contradict"]["wrong_model"]["quantity"]
    rows = ""
    for p in spec["parameters"]:
        if p.get("fixed"):
            unit = f' <span class="gx-unit">{esc(p.get("unit", ""))}</span>' if p.get("unit") else ""
            rows += (f'<div class="gx-ro" data-gx-reveal="start"><span class="gx-ro-l">{esc(p["label"])} (given)</span>'
                     f'<span class="gx-ro-v"><output data-gx-q="{esc(p["id"])}"></output>{unit}</span></div>')
    for row in spec["quantities"]:
        if row.get("show", True) is False and row["id"] != wrong:
            continue
        reveal = "contradict" if row["id"] == wrong else "manipulate"
        unit = f' <span class="gx-unit">{esc(row.get("unit", ""))}</span>' if row.get("unit") else ""
        cls = " gx-ro-target" if row["id"] == spec["target"]["quantity"] else ""
        rows += (f'<div class="gx-ro{cls}" data-gx-reveal="{reveal}" hidden><span class="gx-ro-l">{esc(row["label"])}</span>'
                 f'<span class="gx-ro-v"><output data-gx-q="{esc(row["id"])}"></output>{unit}</span></div>')
    return (
        '<section class="gx-stage" aria-label="The explorer">'
        '<div class="gx-views">'
        f'<figure class="gx-view g9-c-stage-view" data-gx-view="scene" data-g9-component="SCENE"><svg id="gx-scene-svg" class="gx-svg" viewBox="0 0 {vw} {vh}" role="img" '
        f'aria-labelledby="gx-scene-t gx-scene-d"><title id="gx-scene-t">{esc(scene["title"])}</title><desc id="gx-scene-d">{esc(scene["description"])}</desc><defs>{markers}</defs></svg>'
        f'<figcaption>{esc(scene["title"])}</figcaption></figure>'
        f'<figure class="gx-view g9-c-stage-view" data-gx-view="graph" data-g9-component="SECOND_VIEW"><svg id="gx-graph-svg" class="gx-svg" viewBox="0 0 440 330" role="img" '
        f'aria-labelledby="gx-graph-t gx-graph-d"><title id="gx-graph-t">{esc(view["title"])}</title><desc id="gx-graph-d">{esc(view["description"])}</desc></svg>'
        f'<figcaption>{esc(view["title"])}</figcaption></figure></div>'
        '<p class="gx-closed-note" hidden>The explorer is closed for the fresh tasks.</p>'
        '<div class="gx-panel"><div class="gx-controls g9-c-control-panel" data-g9-component="PARAMETERS">'
        f'{sliders}<p class="gx-note" data-gx-lock-note></p><button type="button" class="gx-secondary" data-gx-reset>Reset sliders</button></div>'
        f'<div class="gx-readouts g9-c-control-panel" data-g9-component="QUANTITIES" role="group" aria-label="Readouts">{rows}</div></div>'
        '<p class="sr-only" id="gx-state-summary"></p></section>')


def render_head(spec: dict, brief: Brief) -> str:
    rail = "".join(f'<li data-gx-rail="{cid}" data-gx-title="{esc(SHORT[cid])}" data-state="todo"><span class="gx-n" aria-hidden="true">{i}</span>'
                   f'<span class="gx-lab">{esc(SHORT[cid])}</span></li>' for i, cid in enumerate(em.stages(em.blueprint()), 1))
    return (f'<header class="gx-head g9-c-route-rail" data-g9-component="ROUTE_RAIL"><h1>{esc(spec["title"])}</h1>'
            f'<ol class="gx-rail" aria-label="The route, eleven steps">{rail}</ol>'
            '<button type="button" class="gx-secondary" data-gx-theme aria-pressed="true">Theme</button>'
            '<button type="button" class="gx-secondary" data-gx-restart>Start over</button></header>')


def render_done(spec: dict, links: dict) -> str:
    buttons = ""
    if links.get("question"):
        buttons += f'<a class="gx-primary-link" href="{esc(links["question"])}">Back to the question</a>'
    if links.get("concept"):
        buttons += f'<a class="gx-secondary-link" href="{esc(links["concept"])}">The concept book for it</a>'
    note = "" if buttons else '<p class="gx-note">The product pages for this question are not deployed yet, so there is nothing to link back to.</p>'
    return ('<section class="gx-card gx-done" id="gx-done" data-state="current" hidden><div class="gx-card-head"><h2 tabindex="-1"><span class="gx-n" aria-hidden="true">✓</span>'
            '<span class="gx-t">You have finished the route</span></h2></div><div class="gx-card-body">'
            '<ul data-gx-summary-list></ul>'
            f'<p class="gx-prompt">Now return to the question this page was built for, and answer it yourself.</p><div class="gx-actions gx-links">{buttons}</div>{note}</div></section>')


# ------------------------------------------------------------------ css

def explorer_css(bp: dict) -> str:
    rp = bp["responsive_policy"]
    columns = f'minmax(0,{rp["primary_fraction"] * 100:g}fr) minmax(0,{rp["support_fraction"] * 100:g}fr)'
    wide = rp.get("expanded_min_px", 1100)
    return f"""
:root{{--gx-object:#8ab4f8;--gx-given:#fbbf24;--gx-result:#34d399;--gx-wrong:#fb7185;--gx-helper:#c4b5fd;--gx-frame:#8190a5;--gx-grid:rgba(148,163,184,.25);--gx-plot:rgba(148,163,184,.07)}}
:root[data-theme=light]{{--gx-object:#1f5fae;--gx-given:#b45309;--gx-result:#047857;--gx-wrong:#be123c;--gx-helper:#6d28d9;--gx-frame:#64748b;--gx-grid:rgba(100,116,139,.28);--gx-plot:rgba(100,116,139,.06)}}
.sr-only{{position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);white-space:nowrap}}
.gx-skip{{position:absolute;left:8px;top:-60px;z-index:20;background:var(--card);padding:0 14px;border-radius:8px;min-height:48px;box-sizing:border-box;display:inline-flex;align-items:center}}.gx-skip:focus{{top:8px}}
.g9-c-route-rail{{position:sticky;top:0;z-index:6;display:flex;align-items:center;gap:10px;padding:6px 16px;background:var(--card);border-bottom:1px solid var(--line);min-height:60px;box-sizing:border-box}}
.gx-head h1{{font-size:1.05rem;line-height:1.2;margin:0;flex:0 1 27%;min-width:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.gx-rail{{display:flex;gap:6px;list-style:none;margin:0;padding:0;flex:1 1 auto;min-width:0;overflow-x:auto;justify-content:center;scrollbar-width:none}}
.gx-rail li{{display:inline-flex;align-items:center;gap:6px;border:1px solid var(--line);border-radius:999px;padding:3px 10px 3px 3px;min-height:36px;box-sizing:border-box;color:var(--muted);font-size:.9rem;white-space:nowrap}}
.gx-rail li .gx-lab{{display:none}}.gx-rail li[data-state=current]{{border-color:var(--accent);color:var(--fg);font-weight:700}}.gx-rail li[data-state=current] .gx-lab{{display:inline}}
.gx-rail li[data-state=done]{{color:var(--fg)}}.gx-rail li[data-state=done] .gx-n{{background:var(--ok-bg);color:var(--ok-fg);border:1px solid var(--ok-line)}}
.gx-n{{display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;background:var(--pill-bg);color:var(--pill-fg);font-size:.85rem;font-weight:700;flex:0 0 auto}}
.gx-head>button{{min-height:48px;padding:6px 12px}}
.gx-main{{max-width:var(--g9-content-max);margin:0 auto;padding:12px 16px 28px;box-sizing:border-box}}
.gx-stage{{display:grid;gap:12px;min-width:0}}
.gx-views{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;align-items:stretch}}
.g9-c-stage-view{{margin:0;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 8px 4px;overflow:visible;min-width:0;display:flex;flex-direction:column}}
.g9-c-stage-view svg{{display:block;width:100%;height:auto;max-width:none;max-height:min(52vh,420px);flex:1 1 auto;min-height:0}}
.g9-c-stage-view figcaption{{font-size:.9rem;color:var(--muted);padding:2px 6px 4px}}
.gx-closed-note{{margin:0;padding:14px;border:1px dashed var(--line);border-radius:12px;color:var(--muted)}}
.gx-panel{{display:grid;grid-template-columns:minmax(0,1.25fr) minmax(0,1fr);gap:12px 18px;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px}}
.gx-controls{{display:grid;gap:4px;align-content:start}}
.gx-ctl label{{display:flex;justify-content:space-between;gap:8px;font-weight:600}}.gx-ctl-val{{font-variant-numeric:tabular-nums}}
.gx-ctl input[type=range]{{width:100%;margin:2px 0 0}}
.gx-readouts{{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:6px 14px;align-content:start}}
.gx-ro{{display:flex;flex-direction:column;min-width:0}}.gx-ro-l{{font-size:.9rem;color:var(--muted)}}.gx-ro-v{{font-weight:700;font-size:1.15rem;font-variant-numeric:tabular-nums}}
.gx-ro-target .gx-ro-v{{color:var(--gx-result)}}
.gx-unit{{color:var(--muted);font-weight:500;font-size:.92rem}}
.gx-route{{min-width:0}}
.gx-card,.g9-c-route-step{{background:var(--card);border:1px solid var(--line);border-radius:14px;margin:0 0 10px;min-width:0}}
.g9-c-control-panel{{min-width:0}}
.gx-card[data-state=current]{{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}}
.gx-card-head{{display:flex;align-items:center;gap:10px;padding:10px 14px;flex-wrap:wrap}}.gx-card[data-state=done] .gx-card-head{{cursor:pointer}}
.gx-card h2{{font-size:1.08rem;margin:0;display:flex;align-items:center;gap:8px}}
.gx-card[data-state=current] .gx-n{{background:var(--accent);color:var(--card)}}
.gx-sum{{margin:0;color:var(--muted);font-size:.92rem;flex:1 1 12rem;min-width:0;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}}
.gx-card-body{{padding:0 14px 14px}}.gx-card[data-state=done] .gx-card-body{{display:none}}.gx-card[data-state=done][data-open] .gx-card-body{{display:block}}
.gx-card[data-state=current] .gx-sum{{display:none}}
.gx-prompt{{margin:.2rem 0 .6rem;font-weight:600}}.gx-situation{{margin:.5rem 0}}
.gx-source{{margin:0 0 .6rem;padding:10px 14px;border-left:4px solid var(--accent);background:var(--bg);border-radius:0 10px 10px 0}}
.gx-source p{{margin:.25rem 0}}.gx-cite{{color:var(--muted);font-size:.92rem}}
.gx-target{{background:var(--info-bg);border:1px solid var(--info-line);border-radius:10px;padding:8px 14px;color:var(--info-fg)}}.gx-target p{{margin:.35rem 0}}
.gx-tag{{display:inline-block;font-size:.85rem;font-weight:700;text-transform:uppercase;letter-spacing:.03em;color:var(--accent);margin-right:6px}}
.gx-options{{border:0;margin:0;padding:0}}
.gx-option{{display:flex;gap:10px;align-items:flex-start;padding:10px 12px;border:1px solid var(--line);border-radius:10px;margin:8px 0;min-height:48px;box-sizing:border-box;cursor:pointer;background:var(--bg)}}
.gx-option:has(input:checked){{border-color:var(--accent);box-shadow:0 0 0 1px var(--accent)}}
.gx-option input{{width:24px;height:24px;margin:2px 0 0;flex:0 0 auto}}
.gx-note{{color:var(--muted);font-size:.92rem;margin:.5rem 0}}
.gx-goals,.gx-cases,.gx-statements,.gx-invs,.gx-steps,.gx-derive,.gx-tasks{{list-style:none;padding:0;margin:.5rem 0}}
.gx-goals>li,.gx-cases>li,.gx-statements>li,.gx-invs>li,.gx-steps>li,.gx-derive>li,.gx-tasks>li{{margin:0 0 10px;padding:10px 12px;border:1px solid var(--line);border-radius:10px;background:var(--bg)}}
.gx-goals>li{{display:flex;gap:10px;align-items:flex-start}}.gx-goal-body{{flex:1 1 auto;min-width:0}}
.gx-check{{flex:0 0 auto;display:inline-grid;place-items:center;width:28px;height:28px;border-radius:50%;border:2px solid var(--line);font-weight:800;color:var(--ok-fg)}}
.gx-goals>li[data-met=true]{{border-color:var(--ok-line);background:var(--ok-bg)}}.gx-goals>li[data-met=true] .gx-check{{border-color:var(--ok-line)}}
.gx-row{{display:flex;gap:8px;flex-wrap:wrap;margin-top:6px}}
.gx-mini,.gx-secondary,.gx-toggle{{min-height:48px;padding:8px 14px}}
.gx-primary,.gx-primary-link{{background:var(--accent);color:var(--card);border-color:var(--accent);font-weight:700;min-height:48px;padding:10px 18px}}
.gx-primary:disabled{{opacity:.4;cursor:not-allowed}}
.gx-primary-link,.gx-secondary-link{{display:inline-flex;align-items:center;border-radius:10px;border:1px solid var(--accent);text-decoration:none;min-height:48px;padding:10px 18px;box-sizing:border-box}}
.gx-secondary-link{{color:var(--accent);background:var(--card)}}
.gx-toggle[aria-pressed=true],.gx-choice button[aria-pressed=true]{{background:var(--accent);color:var(--card);border-color:var(--accent);font-weight:700}}
.gx-actions{{display:flex;gap:10px;justify-content:flex-end;flex-wrap:wrap;margin-top:12px}}
.gx-card[data-state=current] .gx-actions{{position:sticky;bottom:0;z-index:2;margin:12px -14px -14px;padding:10px 14px;background:var(--card);border-top:1px solid var(--line);border-radius:0 0 14px 14px}}
.gx-choice{{display:flex;gap:8px;flex-wrap:wrap;margin:.4rem 0}}
.gx-feedback{{margin:.5rem 0 0;padding:8px 12px;border-left:3px solid var(--accent);background:var(--card);border-radius:0 8px 8px 0}}.gx-feedback p{{margin:.25rem 0}}
.gx-why{{margin-top:10px;padding:8px 14px;border:1px solid var(--ok-line);background:var(--ok-bg);color:var(--ok-fg);border-radius:10px}}
.gx-compare{{margin:.5rem 0;padding:6px 10px;background:var(--card);border-radius:8px;font-variant-numeric:tabular-nums}}
.gx-takeaway,.gx-recall{{margin:.5rem 0;padding:8px 14px;border:1px solid var(--info-line);background:var(--info-bg);color:var(--info-fg);border-radius:10px}}
.gx-eq{{display:flex;gap:14px;align-items:center;flex-wrap:wrap;margin:.35rem 0;font-size:1.12rem}}.gx-math math{{font-size:1.15em}}.gx-val{{color:var(--muted);font-size:.95rem}}
.gx-eq-final{{padding:6px 12px;border:1px solid var(--accent);border-radius:10px;background:var(--card)}}
.gx-level{{margin:.2rem 0 .6rem;color:var(--muted)}}
.gx-answer{{display:flex;gap:10px;align-items:center;flex-wrap:wrap}}.gx-answer input{{width:9rem;min-height:48px;box-sizing:border-box;border:1px solid var(--line);border-radius:10px;background:var(--card);color:var(--fg);padding:6px 12px}}
.gx-done .gx-links{{justify-content:flex-start}}
/* the pictures */
.gx-svg text{{font:600 16px system-ui,sans-serif;fill:currentColor}}
.gx-lab{{paint-order:stroke;stroke:var(--card);stroke-width:5px;stroke-linejoin:round}}
.gx-stroke{{fill:none;stroke:currentColor;stroke-width:3;stroke-linecap:round;stroke-linejoin:round}}
.gx-fill{{fill:currentColor;stroke:var(--card);stroke-width:2}}
.gx-nofill{{fill:none}}.gx-soft{{fill:currentColor;fill-opacity:.16}}
.gx-r-object{{color:var(--gx-object)}}.gx-r-given{{color:var(--gx-given)}}.gx-r-result{{color:var(--gx-result)}}.gx-r-wrong{{color:var(--gx-wrong)}}.gx-r-helper{{color:var(--gx-helper)}}.gx-r-frame{{color:var(--gx-frame)}}
.gx-ah{{fill:currentColor}}
.gx-r-wrong .gx-stroke{{stroke-dasharray:8 5}}.gx-r-helper .gx-stroke{{stroke-width:2.6}}.gx-r-frame .gx-stroke{{stroke-width:1.8}}.gx-r-frame .gx-lab{{fill:var(--muted)}}
.gx-plot{{fill:var(--gx-plot);stroke:var(--line)}}.gx-grid{{stroke:var(--gx-grid);stroke-width:1}}
.gx-tick,.gx-axis-label{{fill:var(--muted)!important;font-weight:500!important}}
.gx-curve{{stroke-width:3.5}}.gx-drop{{stroke-dasharray:3 4;stroke-width:1.6;color:var(--muted)}}.gx-guide .gx-stroke{{stroke-dasharray:6 5;stroke-width:1.8}}
.gx-svg *{{vector-effect:none}}
.g9-c-stage-view{{position:relative}}.gx-faded svg{{visibility:hidden}}.gx-faded::after{{content:'Hidden at this level';position:absolute;inset:0;display:grid;place-items:center;color:var(--muted);font-weight:600}}
.gx-latest{{border-color:var(--accent)!important}}
/* layout: from the blueprint's own fractions; the route stays in view and scrolls inside itself */
@media (min-width:{wide}px){{
.gx-main{{display:grid;grid-template-columns:{columns};gap:16px;align-items:start}}
.gx-route{{position:sticky;top:76px;max-height:calc(100vh - 92px);overflow-y:auto;overscroll-behavior:contain;padding-right:2px}}
}}
@media (max-width:{wide - 1}px){{
.g9-c-route-rail{{position:static;flex-wrap:wrap;row-gap:6px;padding:8px 16px}}
.gx-head h1{{flex:1 1 40%;-webkit-line-clamp:3}}.gx-head>button{{white-space:nowrap}}
.gx-rail{{order:3;flex:1 1 100%;justify-content:flex-start}}
.gx-main{{display:block;padding-top:8px}}
.gx-stage,.gx-panel{{display:contents}}
.gx-views{{position:sticky;top:0;z-index:4;background:var(--bg);padding:6px 0 8px;margin:0}}
.gx-controls{{position:sticky;top:var(--gx-views-h,340px);z-index:4;background:var(--card);border:1px solid var(--line);border-radius:12px;padding:8px 14px;margin:0 0 8px}}
.gx-readouts{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:10px 14px;margin:0 0 10px}}
.gx-closed-note{{margin:0 0 8px}}
.gx-route{{margin-top:6px}}
}}
@media (max-width:699px){{
.gx-views{{grid-template-columns:minmax(0,1fr);position:static}}.gx-controls{{position:static}}
.gx-readouts{{grid-template-columns:repeat(2,minmax(0,1fr))}}
}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
body.gx-closed .gx-stage{{display:none}}
@media (min-width:{wide}px){{body.gx-closed .gx-main{{grid-template-columns:minmax(0,1fr)}}body.gx-closed .gx-route{{max-width:760px;margin:0 auto}}}}
"""


# ------------------------------------------------------------------ the page

def page(spec: dict, brief: Brief, links: dict) -> tuple[str, dict]:
    bp = em.blueprint()
    compiled = em.compile_page_model(spec)
    route = em.stages(bp)
    payload = {"spec": spec, "compiled": compiled, "route": route, "fade_levels": FADE_LEVELS, "links": links}
    data = json.dumps(payload, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")
    model_js = MODEL_JS.read_text(encoding="utf-8")
    runtime_js = RUNTIME_JS.read_text(encoding="utf-8")
    css = render_core.CSS + explorer_css(bp)
    digest = hashlib.sha256((json.dumps(spec, sort_keys=True) + model_js + runtime_js + css + bp["version"]).encode("utf-8")).hexdigest()[:16]
    document = (
        "<!doctype html>\n"
        f'<html lang="en" data-theme="dark" data-g9-role="EXPLORER" data-g9-blueprint="{esc(bp["id"])}@{esc(bp["version"])}" data-g9-render-digest="{digest}">'
        '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        f'<meta name="g9-render" content="{BUILDER} {digest}"><title>{esc(spec["title"])}</title>'
        f'<style data-g9-tablet-shell>{render_core.TABLET_CSS.read_text(encoding="utf-8")}</style><style>{css}</style></head>'
        f'<body data-core="EXPLORER" data-blueprint-ref="{esc(bp["id"])}@{esc(bp["version"])}">'
        '<a class="gx-skip" href="#g9-route">Skip to the route</a>'
        f'{render_head(spec, brief)}'
        '<noscript><p class="gx-note" style="padding:16px">This explorer needs JavaScript: it computes every number it shows.</p></noscript>'
        f'<main class="gx-main">{render_stage(spec, compiled)}'
        f'<aside class="gx-route" id="g9-route" aria-label="The route">{render_cards(spec, brief)}{render_done(spec, links)}</aside></main>'
        '<div class="sr-only" id="gx-live" aria-live="polite" role="status"></div>'
        f'<script type="application/json" id="gx-data">{data}</script>'
        f'<script>{model_js}</script><script>{runtime_js}</script></body></html>\n')
    return document, compiled


# ------------------------------------------------------------------ the contract the standard asks every explorer to carry

CONTRACT_SCHEMA = REPO / "Shared/library/explorer_design_contract.schema.json"
CONTRACT_EVENTS = ["INITIAL_PREDICTION", "MISCONCEPTION_SIGNATURE", "MANIPULATION_COMPLETED", "CONTRADICTION_UNDERSTOOD", "CAUSAL_CHAIN_RECONSTRUCTED",
                   "INVARIANT_RECONSTRUCTED", "BOUNDARY_TEST_RESULT", "FRESH_TRANSFER_RESULT"]
CONTRACT_SEQUENCE = {"CONTEXT": "CONTEXT", "PREDICT": "PREDICT", "MANIPULATE": "MANIPULATE", "OBSERVE": "OBSERVE", "CONTRADICT": "CONTRADICT",
                     "DECONSTRUCT": "GRAPHICAL_DECONSTRUCTION", "RECONSTRUCT": "MATHEMATICAL_RECONSTRUCTION", "INVARIANT": "INVARIANT_DISCOVERY",
                     "BOUNDARY": "BOUNDARY_STRESS", "FADE": "SCAFFOLD_FADE", "TRANSFER": "FRESH_TRANSFER"}


def _sentence(text: str, minimum: int = 10) -> str:
    text = str(text).strip()
    return text if len(text) >= minimum else (text + " " * minimum)[:minimum].replace(" ", ".")


def contract(spec: dict, brief: Brief, locator: str) -> dict:
    """The machine-bound design contract of Shared/library/explorer_design_contract.schema.json, written from the spec.

    It says what the page was built to do and states, in the audit block, that no audit has been run: a generated page is
    IMPLEMENTATION_PARTIAL until a person or a run of the checklist says otherwise, and a TEST page is never certified."""
    target, scene, view = spec["target"], spec["scene"], spec["second_view"]
    free = [p for p in spec["parameters"] if not p.get("fixed")]
    steps = [step["text"] for step in spec["deconstruct"]["steps"]]
    chain = (steps + [step["text"] for step in spec["reconstruct"]["steps"]])[:max(len(steps), 3)]
    holds = [c["text"] for c in spec["boundary"]["cases"] if c["expect"] == "fails"] or [c["text"] for c in spec["boundary"]["cases"]]
    capability = (brief.brief or {}).get("capability_ref")
    units = sorted({p.get("unit", "") for p in spec["parameters"] if p.get("unit")} | {q.get("unit", "") for q in spec["quantities"] if q.get("unit")})
    invariants = [{"id": f"RI-ORACLE-{i}", "views": ["scene geometry", "computed quantities"], "relation": _sentence(o["text"], 8), "tolerance": 1e-6,
                   "evidence_method": "ANALYTIC_ORACLE", "evidence_ref": f"explorer-evidence.json#oracles/{i}"} for i, o in enumerate(spec["oracles"], 1)]
    invariants.append({"id": "RI-EQUATION", "views": ["mechanism steps", "closed-form equation"], "relation": _sentence(spec["reconstruct"]["equation"]["text"], 8),
                       "tolerance": 1e-6, "evidence_method": "PROPERTY_TEST", "evidence_ref": "explorer-evidence.json#equation"})
    pending = "PENDING"
    return {
        "schema_version": "1.3.0",
        "conformance_status": "IMPLEMENTATION_PARTIAL",
        "cognitive_target": {"target_failure": _sentence(target["failure"]), "target_operation": _sentence(target["operation"]),
                             "core_invariant": _sentence(target["invariant"], 5), "boundary": _sentence(target["boundary"])},
        "route_policy": {"recommended_when": ["INTRINSIC_HARD", "COUNTERINTUITIVE"], "learner_evidence_triggers": ["MISCONCEPTION_DETECTED", "REPEATED_FAILURE"],
                         "prerequisite_policy": "DIVERT_IF_PREREQUISITE_MISSING", "auto_route_policy": "RECOMMEND_ONLY"},
        "interaction_sequence": [CONTRACT_SEQUENCE[cid] for cid in em.stages(em.blueprint())],
        "graphical_contract": {
            "phenomenon_view": _sentence(scene["job"]),
            "mechanism_view": _sentence("; ".join(steps)),
            "mathematical_structure_view": _sentence(spec["reconstruct"]["equation"]["text"]),
            "direct_manipulation": _sentence(", ".join(f"the {p['label']} slider" for p in free), 5),
            "synchronized_representations": [scene["title"], view["title"], "the readouts of every quantity", "the equation with live values"],
            "causal_chain": chain,
            "progressive_disclosure": "The situation first, then a locked-in prediction, then the result, the pattern, the tempting model, the mechanism one cause at a time, the equation, the invariants and the boundary.",
            "counterfactual_model": _sentence(spec["contradict"]["imposes"])},
        "boundary_contract": {"assumption_held": _sentence(spec["boundary"]["assumption"], 5), "stress_action": "Set the sliders to each boundary case and judge whether the shortcut holds there.",
                              "expected_break": _sentence("; ".join(holds), 5), "learner_must_identify": _sentence(spec["boundary"]["learner_must_identify"], 5)},
        "exit_evidence": {"reconstruction_required": True, "boundary_test_required": True, "fresh_transfer_required": True,
                          "rejoin_step_ref": target["question_ref"], "evidence_events": CONTRACT_EVENTS},
        "implementation_evidence": {key: True for key in (
            "prediction_before_reveal", "meaningful_direct_manipulation", "synchronized_representations", "physical_contradiction", "explicit_causal_chain",
            "mathematics_from_visual_mechanism", "invariant_discovery", "boundary_stress", "scaffold_fade", "fresh_transfer_without_scaffold")},
        "state_fidelity_contract": {
            "source_of_truth": _sentence("The slider positions (" + ", ".join(p["id"] for p in free) + "): every quantity, element and readout is computed from them by the spec's expressions."),
            "external_state_mapping": "NOT_APPLICABLE", "missing_parameter_policy": "NEVER_INVENT_AS_EXACT", "fidelity_labels": ["EXACT", "CONSTRAINT_FAITHFUL", "CONCEPT_ONLY", "UNAVAILABLE"],
            "unit_constant_policy": _sentence("Every quantity is shown in its declared unit (" + (", ".join(units) or "none") + "); the page applies no other conversion."),
            "reset_policy": "Reset sliders returns every slider to its starting position and Start over reloads the route from the first step.",
            "external_state_bindings": [], "exactness_rule": "ALL_REQUIRED_BINDINGS_PRESENT"},
        "quality_audit": {
            "checklist_version": "1.2.0", "audit_status": "NOT_RUN", "last_audited": None,
            "audit_provenance": {"mode": "NOT_RUN", "auditor": None, "version": None},
            "audit_1_canonical_truth_scope": {k: pending for k in ("canonical_binding", "assumptions_and_conventions", "derivation_or_model_check", "units_constants_parameters",
                                                                  "boundary_limit_cases", "source_claim_fidelity", "corpus_snapshot_provenance", "instructional_depth_scope")},
            "audit_2_graphical_state_fidelity": {k: pending for k in ("single_state_source", "representation_synchronization", "direct_manipulation_is_causal", "counterfactual_is_honest",
                                                                     "progressive_disclosure", "control_state_mapping", "no_invented_exact_parameters", "interaction_fidelity_disclosed",
                                                                     "representation_equivalence", "rendered_geometry_truth")},
            "audit_3_reconstruction_teaching_transfer": {k: pending for k in ("answer_or_disposition_specific", "derivation_specific", "independent_check", "misconception_trap_specific",
                                                                             "transfer_takeaway_specific", "boundary_recognition", "scaffold_fade", "fresh_transfer", "helper_activation")},
            "audit_4_runtime_release_integrity": {k: pending for k in ("implementation_locator", "static_syntax", "handler_and_control_integrity", "identifier_integrity",
                                                                      "no_placeholder_or_undefined_output", "deterministic_reset", "runtime_smoke", "accessibility_baseline",
                                                                      "delivery_profile_integrity")},
            "audit_receipts": [], "unresolved_findings": [], "waivers": {}},
        "scope_contract": {"canonical_binding_status": "BOUND" if capability else "UNBOUND_EXTENSION", "canonical_capability_refs": [capability] if capability else [],
                           "instructional_depth": "SCHOOL_CORE", "extension_reason": "none: built for the toughest question of the owner's own set",
                           "certification_scope": "TEST sandbox draft: not eligible for canonical GCDR certification"},
        "representation_invariants": invariants,
        "geometry_truth_contract": {"verification_status": "DECLARED", "oracle_method": "ANALYTIC_ORACLE",
                                    "governed_geometry": [e["id"] for e in scene["elements"]] or ["scene"], "evidence_ref": "explorer-evidence.json#oracles"},
        "delivery_profile": {"profile": "SINGLE_FILE_OFFLINE", "artifact_locator": locator, "remote_dependencies_declared": []},
    }


def contract_findings(document: dict) -> list[str]:
    """What is wrong with a contract against its schema, one line each (empty when it is valid)."""
    import jsonschema  # noqa: PLC0415
    schema = json.loads(CONTRACT_SCHEMA.read_text(encoding="utf-8"))
    return [f"{'.'.join(str(p) for p in e.absolute_path) or 'contract'}: {e.message}"
            for e in jsonschema.Draft202012Validator(schema).iter_errors(document)]


def evidence_record(spec: dict, report: em.Report, page_sha256: str) -> dict:
    """What the build computed, kept beside the page: the numbers behind every claim in it."""
    return {
        "schema": "grade9v3-explorer-evidence-v1",
        "builder": BUILDER,
        "blueprint_ref": spec["blueprint_ref"],
        "spec_sha256": hashlib.sha256(json.dumps(spec, sort_keys=True).encode("utf-8")).hexdigest(),
        "page_sha256": page_sha256,
        "checked_by": "Shared/tools/explorer_model.py at every position the sliders can reach (see states_checked)",
        **report.evidence,
        "oracles": [{"text": o["text"], "left": o["left"], "right": o["right"]} for o in spec["oracles"]],
        "not_checked_here": ["whether the teaching is sound", "the behaviours in a browser (tests/test_explorer_browser.py runs them on a reference page)",
                             "the audit of the standard's checklist: it is NOT_RUN in the contract"],
    }


# ------------------------------------------------------------------ the whole build

def load_spec(source: Path) -> tuple[dict, Path]:
    source = Path(source)
    spec_path = source / SPEC_FILE if source.is_dir() else source
    if not spec_path.is_file():
        raise ValueError(f"no {SPEC_FILE} in {source}")
    return json.loads(spec_path.read_text(encoding="utf-8")), spec_path


def _sentences(node, found: list[str] | None = None) -> list[str]:
    found = [] if found is None else found
    if isinstance(node, str):
        if len(node) >= 30 and " " in node:
            found.append(node)
    elif isinstance(node, dict):
        for value in node.values():
            _sentences(value, found)
    elif isinstance(node, list):
        for value in node:
            _sentences(value, found)
    return found


def copied_from_example(spec: dict) -> list[str]:
    """Sentences of the spec that are word for word the worked example's. Two is not a coincidence."""
    if not EXAMPLE_SPEC.is_file():
        return []
    example = json.loads(EXAMPLE_SPEC.read_text(encoding="utf-8"))
    if example == spec:
        return []
    mine, theirs = _sentences(spec), set(_sentences(example))
    matches = [text for text in mine if text in theirs]
    return matches if len(matches) >= 2 else []


def check_source(source: Path) -> tuple[dict, Brief, em.Report]:
    spec, spec_path = load_spec(source)
    spec = em.normalize(spec)
    if isinstance(spec, dict) and "product" in spec and (REPO / str(spec["product"])).is_file():
        brief = Brief(REPO / spec["product"])
    else:
        raise ValueError(f"{SPEC_FILE}: 'product' must name an existing product manifest (TEST/products/SLUG.manifest.json)")
    report = em.check(spec, brief.brief)
    if not report.errors and spec_path.parent.name != spec["slug"] and spec_path.parent.parent == INTERACTIVE_ROOT:
        report.error("SPEC", "slug", f"{spec['slug']!r} must equal the directory name {spec_path.parent.name!r}")
    copied = copied_from_example(spec)
    if copied:
        report.error("SPEC", "text", f"{len(copied)} sentences are the worked example's own, written for a different concept (for example {copied[0]!r}); the "
                     f"example ({EXAMPLE_SPEC.relative_to(REPO).as_posix()}) shows the format, not what to write. Write the sentences for this concept")
    return spec, brief, report


def print_findings(report: em.Report, bp: dict, limit: int = 40) -> None:
    shown = report.findings[:limit]
    for finding in shown:
        print(f"  {finding.kind:5s} {finding.line()}")
    if len(report.findings) > limit:
        print(f"  ... {len(report.findings) - limit} more")
    components = sorted({f.component for f in report.findings})
    advice = hints(bp, components)
    if advice:
        print("how to author what is flagged (the blueprint's own words):")
        print("\n".join(advice))


def build(source: Path) -> tuple[str, dict, dict, em.Report, Brief]:
    """(page, compiled model, spec, report, brief) for a source folder; the page only when the report has no error."""
    spec, brief, report = check_source(source)
    if report.errors:
        return "", {}, spec, report, brief
    document, compiled = page(spec, brief, brief.links())
    return document, compiled, spec, report, brief


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("new")
    p.add_argument("manifest")
    p.add_argument("--slug")
    p = sub.add_parser("check")
    p.add_argument("source")
    p = sub.add_parser("build")
    p.add_argument("source")
    p.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    try:
        bp = em.blueprint()
        if args.cmd == "new":
            spec = scaffold(Path(args.manifest), args.slug)
            out = INTERACTIVE_ROOT / spec["slug"] / SPEC_FILE
            if out.exists():
                print(f"explorer_build: {out.relative_to(REPO)} exists; not overwritten", file=sys.stderr)
                return 1
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            brief = Brief(Path(args.manifest))
            print(f"wrote {out.relative_to(REPO)} for the toughest concept of the set:")
            print("\n".join(toughest_concept.describe(brief.brief)))
            print(f"every field of the blueprint {bp['id']}@{bp['version']} is in it; fill each one (python3 Shared/tools/explorer_build.py check {out.parent.relative_to(REPO)} says what is missing or wrong):")
            print("\n".join(hints(bp)))
            return 0
        if args.cmd == "check":
            spec, brief, report = check_source(Path(args.source))
            print("\n".join(toughest_concept.describe(brief.brief)))
            if report.findings:
                print(f"{len(report.errors)} error(s), {len(report.gaps)} gap(s):")
                print_findings(report, bp)
            else:
                print("no findings: the numbers are checked at every position of the sliders (that is not a review)")
            print("evidence: " + json.dumps(report.evidence, ensure_ascii=False))
            return 1 if report.errors else 0
        document, compiled, spec, report, brief = build(Path(args.source))
        if report.errors:
            print(f"explorer_build: {len(report.errors)} error(s); no page written")
            print_findings(report, bp)
            return 1
        out = Path(args.out)
        out.mkdir(parents=True, exist_ok=True)
        (out / "index.html").write_text(document, encoding="utf-8")
        print(f"wrote {out / 'index.html'} ({len(document) // 1024} KB); {len(report.gaps)} gap(s)")
        return 0
    except (ValueError, json.JSONDecodeError, blueprints.WebBlueprintContractError) as caught:
        print(f"explorer_build: {caught}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
