#!/usr/bin/env python3
"""Render the TEST-only Question Bank for parked source-verified intake questions.

This is deliberately not the production Question Bank projection. Every intake record remains
academically UNVALIDATED until a separate validation/admission workflow promotes that individual
record. Source-verification and academic-validation are displayed as independent states.
"""
from __future__ import annotations

import html
import json
from collections import Counter
from pathlib import Path

SCHEMA = "grade9v3-test-source-question-intake-v1"
UNVALIDATED = "UNVALIDATED"
BANNER = "TEST sandbox · drafts only · not reviewed, not accepted, not curriculum"


def esc(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def intake_banks(repo: Path) -> list[dict]:
    root = repo / "TEST" / "question-bank" / "intake"
    if not root.is_dir():
        return []
    banks: list[dict] = []
    for path in sorted(root.glob("*.json")):
        if path.name.endswith(".blueprint-handoff.json"):
            continue
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict) and data.get("schema_version") == SCHEMA:
            banks.append(data)
    return banks


def _source_label(question: dict) -> str:
    status = str(question.get("text_verification_status") or "")
    if status == "TEXT_VERIFIED_AGAINST_OFFICIAL":
        return "SOURCE VERIFIED"
    return status.replace("_", " ") or "SOURCE STATUS UNKNOWN"


def _review_label(question: dict) -> str | None:
    status = str(question.get("workflow_status") or "")
    return "DUPLICATE REVIEW" if status == "DUPLICATE_REVIEW" else None


def _source_filename(question: dict) -> str:
    source = str(question.get("source_url") or "")
    return source.rsplit("/", 1)[-1] if source else ""


def _card(question: dict) -> str:
    qid = str(question.get("id") or "")
    unit = str(question.get("chapter_or_unit") or "")
    qtype = str(question.get("question_type") or "")
    review = str(question.get("workflow_status") or "")
    source_label = _source_label(question)
    review_label = _review_label(question)
    options = question.get("options") or []
    option_html = ""
    if options:
        option_html = '<ol class="tqb-options">' + "".join(f"<li>{esc(option)}</li>" for option in options) + "</ol>"

    answer = str(question.get("official_answer_text") or "")
    answer_block = (
        '<details class="tqb-answer"><summary>Official source answer</summary>'
        f'<p><strong>{esc(answer)}</strong></p>'
        f'<p class="tqb-muted">{esc(question.get("answer_key_locator") or "")}</p>'
        '<p class="tqb-warning">This is the answer recorded from the official source. '
        'Grade9V3 academic validation is still pending.</p></details>'
        if answer else
        '<p class="tqb-warning">No source answer is recorded. Academic validation remains pending.</p>'
    )
    duplicate = (
        '<span class="tqb-badge tqb-badge-review" data-g9-review-badge>DUPLICATE REVIEW</span>'
        if review_label else ""
    )
    search_text = " ".join(str(question.get(key) or "") for key in (
        "id", "original_identifier", "stem", "chapter_or_unit", "exercise_or_section",
        "topic_label", "subtopic_label", "question_type",
    )).lower()
    return (
        f'<article class="tqb-card" id="{esc(qid)}" data-g9-test-question="{esc(qid)}" '
        f'data-g9-validation="{UNVALIDATED}" data-g9-source-verification="{esc(source_label)}" '
        f'data-g9-review="{esc(review)}" data-unit="{esc(unit)}" data-type="{esc(qtype)}" '
        f'data-search="{esc(search_text)}">'
        '<div class="tqb-badges">'
        '<span class="tqb-badge tqb-badge-source">SOURCE VERIFIED</span>'
        '<span class="tqb-badge tqb-badge-unvalidated">UNVALIDATED</span>'
        f'{duplicate}</div>'
        f'<h2>{esc(question.get("original_identifier") or qid)}</h2>'
        f'<p class="tqb-meta"><code>{esc(qid)}</code> · {esc(unit)} · '
        f'{esc(question.get("exercise_or_section") or "")} · {esc(question.get("question_type") or "")}</p>'
        f'<p class="tqb-meta">{esc(question.get("topic_label") or "")}'
        f'{(" · " + esc(question.get("subtopic_label"))) if question.get("subtopic_label") else ""}</p>'
        f'<div class="tqb-stem">{esc(question.get("stem") or "")}</div>'
        f'{option_html}{answer_block}'
        '<footer class="tqb-card-footer">'
        f'<span>{esc(question.get("wording_custody") or "")} · {esc(question.get("capture_method") or "")}</span>'
        f'<span>Source: {esc(_source_filename(question))}</span>'
        '</footer></article>'
    )


def render_page(repo: Path) -> str:
    banks = intake_banks(repo)
    questions = [question for bank in banks for question in (bank.get("questions") or [])]
    units = Counter(str(q.get("chapter_or_unit") or "Unknown") for q in questions)
    types = Counter(str(q.get("question_type") or "Unknown") for q in questions)
    duplicate_count = sum(1 for q in questions if q.get("workflow_status") == "DUPLICATE_REVIEW")
    source_verified = sum(1 for q in questions if q.get("text_verification_status") == "TEXT_VERIFIED_AGAINST_OFFICIAL")

    unit_options = "".join(
        f'<option value="{esc(unit)}">{esc(unit)} ({count})</option>'
        for unit, count in sorted(units.items())
    )
    type_options = "".join(
        f'<option value="{esc(kind)}">{esc(kind.replace("_", " ").title())} ({count})</option>'
        for kind, count in sorted(types.items())
    )
    cards = "".join(_card(question) for question in questions)

    styles = """
<style>
.tqb-shell{max-width:1220px;margin:0 auto;padding:24px}.tqb-intro{background:#fff7ed;border:1px solid #fdba74;border-radius:12px;padding:16px;margin:0 0 18px}.tqb-intro strong{color:#9a3412}.tqb-stats{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.tqb-stat,.tqb-badge{display:inline-flex;align-items:center;border-radius:999px;padding:5px 9px;font:700 12px/1.2 system-ui,sans-serif}.tqb-stat{background:#e2e8f0;color:#0f172a}.tqb-controls{display:grid;grid-template-columns:minmax(220px,2fr) minmax(180px,1fr) minmax(160px,1fr) auto;gap:10px;align-items:end;position:sticky;top:0;z-index:3;background:var(--bg,#f8fafc);padding:10px 0 14px}.tqb-controls label{display:grid;gap:4px;font:700 12px/1.2 system-ui,sans-serif}.tqb-controls input,.tqb-controls select,.tqb-controls button{min-height:48px;border:1px solid #cbd5e1;border-radius:8px;padding:8px 10px;background:white;color:#0f172a}.tqb-controls button{cursor:pointer;font-weight:700}.tqb-result-count{margin:4px 0 12px;font-weight:700}.tqb-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:14px}.tqb-card{border:1px solid #cbd5e1;border-radius:12px;background:#fff;padding:16px;min-width:0}.tqb-card[hidden]{display:none}.tqb-card h2{font-size:18px;margin:10px 0 4px}.tqb-badges{display:flex;gap:6px;flex-wrap:wrap}.tqb-badge-source{background:#dcfce7;color:#166534}.tqb-badge-unvalidated{background:#fef3c7;color:#92400e;border:1px solid #f59e0b}.tqb-badge-review{background:#fee2e2;color:#991b1b}.tqb-meta,.tqb-muted{color:#64748b;font-size:13px;overflow-wrap:anywhere}.tqb-stem{font-size:17px;line-height:1.55;margin:14px 0}.tqb-options{margin:8px 0 12px;padding-left:24px}.tqb-options li{margin:5px 0}.tqb-answer{border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px}.tqb-answer summary{cursor:pointer;font-weight:700;min-height:44px;display:flex;align-items:center}.tqb-warning{background:#fffbeb;border-left:4px solid #f59e0b;padding:8px 10px;font-size:13px}.tqb-card-footer{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px;color:#64748b;font-size:12px}.tqb-empty{padding:32px;text-align:center;border:1px dashed #94a3b8;border-radius:12px}.tqb-test-nav{display:flex;flex-wrap:wrap;gap:4px;margin:0;padding:0 14px;background:#7c2d12}.tqb-test-nav a{display:inline-flex;min-height:48px;align-items:center;padding:0 10px;color:#fde68a;font-weight:700;text-decoration:none}.tqb-test-banner{background:#7c2d12;color:white;padding:8px 14px;font:600 14px/1.4 system-ui,sans-serif}
@media(max-width:800px){.tqb-controls{grid-template-columns:1fr;position:static}.tqb-grid{grid-template-columns:1fr}}
</style>
"""
    script = """
<script>
(() => {
  const search = document.getElementById('tqbSearch');
  const unit = document.getElementById('tqbUnit');
  const type = document.getElementById('tqbType');
  const reset = document.getElementById('tqbReset');
  const count = document.getElementById('tqbCount');
  const cards = Array.from(document.querySelectorAll('[data-g9-test-question]'));
  function apply() {
    const query = (search.value || '').trim().toLowerCase();
    let visible = 0;
    cards.forEach(card => {
      const matches = (!query || card.dataset.search.includes(query))
        && (!unit.value || card.dataset.unit === unit.value)
        && (!type.value || card.dataset.type === type.value);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = visible + ' of ' + cards.length + ' questions shown';
    document.getElementById('tqbEmpty').hidden = visible !== 0;
  }
  [search, unit, type].forEach(control => control.addEventListener('input', apply));
  reset.addEventListener('click', () => {
    search.value = ''; unit.value = ''; type.value = ''; apply(); search.focus();
  });
  apply();
})();
</script>
"""
    return (
        '<!doctype html>\n<html lang="en" data-g9-shell data-g9-role="TEST" '
        'data-g9-test="sandbox-draft"><head><meta charset="utf-8">'
        '<meta name="viewport" content="width=device-width,initial-scale=1">'
        '<title>Question Bank · TEST · Grade9V3</title>'
        '<link rel="stylesheet" href="../../css/tablet-12-7.css">'
        f'{styles}</head><body>'
        f'<div class="tqb-test-banner" data-g9-test-banner role="note">{esc(BANNER)}</div>'
        '<nav class="tqb-test-nav" aria-label="TEST">'
        '<a href="../../index.html">Portal</a><a href="../index.html">TEST</a>'
        '<a href="index.html" aria-current="page">Question Bank</a>'
        '<a href="../atlas/index.html">Atlas</a><a href="../rungs/index.html">Rungs</a>'
        '<a href="../deployments/index.html">Deployments</a></nav>'
        '<main class="tqb-shell"><h1>TEST Question Bank</h1>'
        '<section class="tqb-intro"><strong>Academic validation boundary.</strong> '
        'These questions are parked for review. Source wording and source answers may be verified against official NCERT material, '
        'but every record remains <strong>UNVALIDATED</strong> for Grade9V3 academic admission until that question is separately reviewed. '
        'Nothing on this page is in the production Question Bank.</section>'
        '<div class="tqb-stats">'
        f'<span class="tqb-stat">{len(questions)} questions</span>'
        f'<span class="tqb-stat">{source_verified} source verified</span>'
        f'<span class="tqb-stat">{len(questions)} academically unvalidated</span>'
        f'<span class="tqb-stat">{duplicate_count} duplicate review</span>'
        f'<span class="tqb-stat">{len(units)} units</span></div>'
        '<section class="tqb-controls" aria-label="Question filters">'
        '<label>Search<input id="tqbSearch" type="search" placeholder="Question, topic, id…" autocomplete="off"></label>'
        f'<label>Unit<select id="tqbUnit"><option value="">All units ({len(questions)})</option>{unit_options}</select></label>'
        f'<label>Type<select id="tqbType"><option value="">All types</option>{type_options}</select></label>'
        '<button id="tqbReset" type="button">Clear filters</button></section>'
        f'<p class="tqb-result-count" id="tqbCount">{len(questions)} of {len(questions)} questions shown</p>'
        f'<section class="tqb-grid" id="tqbGrid">{cards}</section>'
        '<p class="tqb-empty" id="tqbEmpty" hidden>No questions match these filters.</p>'
        '</main><footer style="padding:20px;text-align:center;color:#64748b">TEST Question Bank · sandbox projection only · not accepted</footer>'
        f'{script}</body></html>\n'
    )


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[2]
    print(render_page(repo), end="")
