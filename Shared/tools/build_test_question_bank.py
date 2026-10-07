#!/usr/bin/env python3
"""Render the TEST-only Question Bank for parked source-verified intake questions.

This is deliberately not the production Question Bank projection. Every intake record remains
academically UNVALIDATED until a separate validation/admission workflow promotes that individual
record. Source-verification and academic-validation are displayed as independent states.
"""
from __future__ import annotations

import json
from pathlib import Path

SCHEMA = "grade9v3-test-source-question-intake-v1"
UNVALIDATED = "UNVALIDATED"
VALIDATION_SCHEMA = "grade9v3-test-question-validation-v1"
BANNER = "TEST sandbox · drafts only · not reviewed, not accepted, not curriculum"


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


def validation_index(repo: Path) -> dict[str, dict]:
    """Latest repository validation truth by parked source id.

    Validation receipts are evidence, not admission. A PASS row is shown as VALIDATED only when
    the receipt also says it is admission-eligible; HOLD/FAIL remain visibly non-admitted states.
    Conflicting receipts fail loudly rather than silently choosing one.
    """
    rows: dict[str, dict] = {}
    for path in sorted((repo / "TEST" / "candidates").glob("*.validation.json")):
        try:
            receipt = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if not isinstance(receipt, dict) or receipt.get("schema_version") != VALIDATION_SCHEMA:
            continue
        for row in receipt.get("records") or []:
            source_id = row.get("source_id")
            academic = row.get("academic_validation") or {}
            if not isinstance(source_id, str) or not source_id:
                continue
            status = academic.get("status")
            if status == "PASS" and academic.get("admission_eligible") is True:
                projected = "VALIDATED"
            elif status == "HOLD":
                projected = "HOLD"
            elif status == "FAIL":
                projected = "FAILED"
            else:
                projected = UNVALIDATED
            value = {"status": projected, "receipt": path.relative_to(repo).as_posix()}
            if source_id in rows and rows[source_id] != value:
                raise ValueError(f"conflicting TEST question validation receipts for {source_id}")
            rows[source_id] = value
    return rows


def payload(repo: Path) -> dict:
    validations = validation_index(repo)
    banks = json.loads(json.dumps(intake_banks(repo)))
    counts: dict[str, int] = {}
    for bank in banks:
        for question in bank.get("questions") or []:
            row = validations.get(question.get("id")) or {"status": UNVALIDATED, "receipt": None}
            question["academic_validation_status"] = row["status"]
            question["academic_validation_receipt"] = row["receipt"]
            counts[row["status"]] = counts.get(row["status"], 0) + 1
    return {
        "schema_version": "grade9v3-test-question-bank-projection-v1",
        "academic_validation_status": "PER_QUESTION",
        "validation_counts": dict(sorted(counts.items())),
        "banks": banks,
    }


def render_data(repo: Path) -> str:
    text = json.dumps(payload(repo), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f"window.G9_TEST_QUESTION_BANK={text};\n"


PAGE = """<!doctype html>
<html lang="en" data-g9-shell data-g9-role="TEST" data-g9-test="sandbox-draft">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Question Bank · TEST · Grade9V3</title>
<link rel="stylesheet" href="../../css/tablet-12-7.css">
<style>
.tqb-shell{max-width:1220px;margin:0 auto;padding:24px}.tqb-intro{background:#fff7ed;border:1px solid #fdba74;border-radius:12px;padding:16px;margin:0 0 18px}.tqb-intro strong{color:#9a3412}.tqb-stats{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.tqb-stat,.tqb-badge{display:inline-flex;align-items:center;border-radius:999px;padding:5px 9px;font:700 12px/1.2 system-ui,sans-serif}.tqb-stat{background:#e2e8f0;color:#0f172a}.tqb-controls{display:grid;grid-template-columns:minmax(220px,2fr) minmax(180px,1fr) minmax(160px,1fr) auto;gap:10px;align-items:end;position:sticky;top:0;z-index:3;background:var(--bg,#f8fafc);padding:10px 0 14px}.tqb-controls>*{min-width:0}.tqb-controls label{display:grid;min-width:0;gap:4px;font:700 12px/1.2 system-ui,sans-serif}.tqb-controls input,.tqb-controls select,.tqb-controls button{width:100%;max-width:100%;min-width:0;min-height:48px;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:8px;padding:8px 10px;background:white;color:#0f172a}.tqb-controls button{cursor:pointer;font-weight:700}.tqb-result-count{margin:4px 0 12px;font-weight:700}.tqb-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:14px}.tqb-card{border:1px solid #cbd5e1;border-radius:12px;background:#fff;padding:16px;min-width:0}.tqb-card[hidden]{display:none}.tqb-card h2{font-size:18px;margin:10px 0 4px}.tqb-badges{display:flex;gap:6px;flex-wrap:wrap}.tqb-badge-source{background:#dcfce7;color:#166534}.tqb-badge-unvalidated{background:#fef3c7;color:#92400e;border:1px solid #f59e0b}.tqb-badge-validated{background:#dbeafe;color:#1e40af;border:1px solid #60a5fa}.tqb-badge-review{background:#fee2e2;color:#991b1b}.tqb-meta,.tqb-muted{color:#64748b;font-size:13px;overflow-wrap:anywhere}.tqb-stem{font-size:17px;line-height:1.55;margin:14px 0}.tqb-options{margin:8px 0 12px;padding-left:24px}.tqb-options li{margin:5px 0}.tqb-answer{border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px}.tqb-answer summary{cursor:pointer;font-weight:700;min-height:48px;display:flex;align-items:center}.tqb-warning{background:#fffbeb;border-left:4px solid #f59e0b;padding:8px 10px;font-size:13px}.tqb-card-footer{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px;color:#64748b;font-size:12px}.tqb-empty{padding:32px;text-align:center;border:1px dashed #94a3b8;border-radius:12px}.tqb-test-nav{display:flex;flex-wrap:wrap;gap:4px;margin:0;padding:0 14px;background:#7c2d12}.tqb-test-nav a{display:inline-flex;min-height:48px;align-items:center;padding:0 10px;color:#fde68a;font-weight:700;text-decoration:none}.tqb-test-banner{background:#7c2d12;color:white;padding:8px 14px;font:600 14px/1.4 system-ui,sans-serif}
@media(max-width:800px){.tqb-controls{grid-template-columns:1fr;position:static}.tqb-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="tqb-test-banner" data-g9-test-banner role="note">TEST sandbox · drafts only · not reviewed, not accepted, not curriculum</div>
<nav class="tqb-test-nav" aria-label="TEST"><a href="../../index.html">Portal</a><a href="../index.html">TEST</a><a href="index.html" aria-current="page">Question Bank</a><a href="../atlas/index.html">Atlas</a><a href="../rungs/index.html">Rungs</a><a href="../deployments/index.html">Deployments</a></nav>
<main class="tqb-shell">
<h1>TEST Question Bank</h1>
<section class="tqb-intro"><strong>Academic validation boundary.</strong> These questions are parked for review. Source verification and Grade9V3 academic validation are separate states. A question remains <strong>UNVALIDATED</strong> until a source-bound validation receipt marks it PASS and admission-eligible; validated questions show <strong>VALIDATED</strong>. Production admission is governed separately.</section>
<div class="tqb-stats" id="tqbStats"></div>
<section class="tqb-controls" aria-label="Question filters">
<label>Search<input id="tqbSearch" type="search" placeholder="Question, topic, id…" autocomplete="off"></label>
<label>Unit<select id="tqbUnit"><option value="">All units</option></select></label>
<label>Type<select id="tqbType"><option value="">All types</option></select></label>
<button id="tqbReset" type="button">Clear filters</button>
</section>
<p class="tqb-result-count" id="tqbCount" aria-live="polite"></p>
<section class="tqb-grid" id="tqbGrid"></section>
<p class="tqb-empty" id="tqbEmpty" hidden>No questions match these filters.</p>
</main>
<footer style="padding:20px;text-align:center;color:#64748b">TEST Question Bank · sandbox projection only · not accepted</footer>
<script src="questions.js"></script>
<script>
(() => {
  const projection = window.G9_TEST_QUESTION_BANK || {banks:[]};
  const questions = projection.banks.flatMap(bank => bank.questions || []);
  const search = document.getElementById('tqbSearch');
  const unit = document.getElementById('tqbUnit');
  const type = document.getElementById('tqbType');
  const reset = document.getElementById('tqbReset');
  const count = document.getElementById('tqbCount');
  const grid = document.getElementById('tqbGrid');
  const empty = document.getElementById('tqbEmpty');
  const stats = document.getElementById('tqbStats');
  const esc = value => String(value ?? '').replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const label = value => String(value || '').replaceAll('_',' ');
  const sourceFilename = q => String(q.source_url || '').split('/').pop();
  const sourceVerified = q => q.text_verification_status === 'TEXT_VERIFIED_AGAINST_OFFICIAL';
  const validationStatus = q => q.academic_validation_status || 'UNVALIDATED';
  const reviewBadge = q => q.workflow_status === 'DUPLICATE_REVIEW'
    ? '<span class="tqb-badge tqb-badge-review" data-g9-review-badge>DUPLICATE REVIEW</span>' : '';

  const units = new Map();
  const types = new Map();
  questions.forEach(q => {
    units.set(q.chapter_or_unit || 'Unknown', (units.get(q.chapter_or_unit || 'Unknown') || 0) + 1);
    types.set(q.question_type || 'Unknown', (types.get(q.question_type || 'Unknown') || 0) + 1);
  });
  [...units].sort().forEach(([name,n]) => unit.insertAdjacentHTML('beforeend', '<option value="'+esc(name)+'">'+esc(name)+' ('+n+')</option>'));
  [...types].sort().forEach(([name,n]) => type.insertAdjacentHTML('beforeend', '<option value="'+esc(name)+'">'+esc(label(name))+' ('+n+')</option>'));

  const verifiedCount = questions.filter(sourceVerified).length;
  const validatedCount = questions.filter(q => validationStatus(q) === 'VALIDATED').length;
  const unvalidatedCount = questions.filter(q => validationStatus(q) === 'UNVALIDATED').length;
  const duplicateCount = questions.filter(q => q.workflow_status === 'DUPLICATE_REVIEW').length;
  stats.innerHTML = '<span class="tqb-stat">'+questions.length+' questions</span>'
    + '<span class="tqb-stat">'+verifiedCount+' source verified</span>'
    + '<span class="tqb-stat">'+validatedCount+' academically validated</span>'
    + '<span class="tqb-stat">'+unvalidatedCount+' academically unvalidated</span>'
    + '<span class="tqb-stat">'+duplicateCount+' duplicate review</span>'
    + '<span class="tqb-stat">'+units.size+' units</span>';

  function renderCard(q) {
    const options = (q.options || []).length
      ? '<ol class="tqb-options">'+q.options.map(option => '<li>'+esc(option)+'</li>').join('')+'</ol>' : '';
    const academic = validationStatus(q);
    const answerNote = academic === 'VALIDATED'
      ? 'This source answer has a matching Grade9V3 PASS validation receipt.'
      : 'This is the answer recorded from the official source. Grade9V3 academic validation is still pending.';
    const answer = q.official_answer_text
      ? '<details class="tqb-answer"><summary>Official source answer</summary><p><strong>'+esc(q.official_answer_text)+'</strong></p>'
        + '<p class="tqb-muted">'+esc(q.answer_key_locator || '')+'</p>'
        + '<p class="tqb-warning">'+esc(answerNote)+'</p></details>'
      : '<p class="tqb-warning">No source answer is recorded. Academic validation remains pending.</p>';
    const text = [q.id,q.original_identifier,q.stem,q.chapter_or_unit,q.exercise_or_section,q.topic_label,q.subtopic_label,q.question_type].join(' ').toLowerCase();
    const article = document.createElement('article');
    article.className = 'tqb-card';
    article.id = q.id;
    article.dataset.g9TestQuestion = q.id;
    article.dataset.g9Validation = academic;
    article.dataset.g9SourceVerification = sourceVerified(q) ? 'SOURCE VERIFIED' : (q.text_verification_status || 'SOURCE STATUS UNKNOWN');
    article.dataset.g9Review = q.workflow_status || '';
    article.dataset.unit = q.chapter_or_unit || '';
    article.dataset.type = q.question_type || '';
    article.dataset.search = text;
    article.innerHTML = '<div class="tqb-badges">'
      + '<span class="tqb-badge tqb-badge-source">'+(sourceVerified(q) ? 'SOURCE VERIFIED' : esc(label(q.text_verification_status || 'SOURCE STATUS UNKNOWN')))+'</span>'
      + '<span class="tqb-badge '+(academic === 'VALIDATED' ? 'tqb-badge-validated' : 'tqb-badge-unvalidated')+'">'+esc(academic)+'</span>'+reviewBadge(q)+'</div>'
      + '<h2>'+esc(q.original_identifier || q.id)+'</h2>'
      + '<p class="tqb-meta"><code>'+esc(q.id)+'</code> · '+esc(q.chapter_or_unit || '')+' · '+esc(q.exercise_or_section || '')+' · '+esc(label(q.question_type || ''))+'</p>'
      + '<p class="tqb-meta">'+esc(q.topic_label || '')+(q.subtopic_label ? ' · '+esc(q.subtopic_label) : '')+'</p>'
      + '<div class="tqb-stem">'+esc(q.stem || '')+'</div>'+options+answer
      + '<footer class="tqb-card-footer"><span>'+esc(q.wording_custody || '')+' · '+esc(q.capture_method || '')+'</span><span>Source: '+esc(sourceFilename(q))+'</span></footer>';
    return article;
  }

  questions.forEach(q => grid.append(renderCard(q)));
  const cards = Array.from(grid.children);
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
    empty.hidden = visible !== 0;
  }
  [search, unit, type].forEach(control => control.addEventListener('input', apply));
  reset.addEventListener('click', () => { search.value=''; unit.value=''; type.value=''; apply(); search.focus(); });
  apply();
})();
</script>
</body>
</html>
"""


def render_page(_repo: Path) -> str:
    return PAGE


if __name__ == "__main__":
    repo = Path(__file__).resolve().parents[2]
    print(render_page(repo), end="")
