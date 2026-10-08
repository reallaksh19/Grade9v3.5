#!/usr/bin/env python3
"""Render the TEST-only Question Bank for parked source-verified intake questions.

This is deliberately not the production Question Bank projection. Every intake record remains
academically UNVALIDATED until a separate validation/admission workflow promotes that individual
record. Source-verification and academic-validation are displayed as independent states.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry, test_source_custody  # noqa: E402

SCHEMA = test_intake_registry.SCHEMA
UNVALIDATED = "UNVALIDATED"
VALIDATION_SCHEMA = "grade9v3-test-question-validation-v1"
BANNER = "TEST sandbox · drafts only · not reviewed, not accepted, not curriculum"


# Capture-era version guard for the 60 existing academic receipts.
# These snapshots prevent options-only or coordinated source/receipt edits from
# reusing an old academic PASS. They are NOT independent academic verification
# or NCERT custody evidence. Extending this scope requires explicit review.
HISTORICAL_ACADEMIC_CAPTURE_SCOPE = {
    "ncert-exemplar-g9-math-u01-q01": (["(A) a natural number","(B) an integer","(C) a real number","(D) a whole number"], "(C) a real number", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q1", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q02": (["(A) there is no rational number","(B) there is exactly one rational number","(C) there are infinitely many rational numbers","(D) there are only rational numbers and no irrational numbers"], "(C) there are infinitely many rational numbers", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q2", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q03": (["(A) terminating","(B) non-terminating","(C) non-terminating repeating","(D) non-terminating non-repeating"], "(D) non-terminating non-repeating", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q3", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q04": (["(A) always an irrational number","(B) always a rational number","(C) always an integer","(D) sometimes rational, sometimes irrational"], "(D) sometimes rational, sometimes irrational", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q4", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q05": (["(A) a finite decimal","(B) 1.41421","(C) non-terminating recurring","(D) non-terminating non-recurring"], "(D) non-terminating non-recurring", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q5", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q06": (["(A) √(4/9)","(B) √12/√3","(C) √7","(D) √81"], "(C) √7", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q6", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q07": (["(A) 0.14","(B) 0.1416 (with bar over 16)","(C) 0.1416 (with bar over 1416)","(D) 0.4014001400014..."], "(D) 0.4014001400014...", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q7", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q08": (["(A) (√2 + √3)/2","(B) (√2 · √3)/2","(C) 1.5","(D) 1.8"], "(C) 1.5", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q8", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q09": (["(A) 19/10","(B) 1999/1000","(C) 2","(D) 1/9"], "(C) 2", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q9", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q10": (["(A) 2√6","(B) 6","(C) 3√3","(D) 4√6"], "(C) 3√3", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q10", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q11": (["(A) 6√5","(B) 5√6","(C) √25","(D) 10√5"], "(B) 5√6", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q11", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q12": (["(A) (√7 + 2)/3","(B) (√7 - 2)/3","(C) (√7 + 2)/5","(D) (√7 + 2)/45"], "(A) (√7 + 2)/3", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q12", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q13": (["(A) (1/2)(3 - 2√2)","(B) 1/(3 + 2√2)","(C) 3 - 2√2","(D) 3 + 2√2"], "(D) 3 + 2√2", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q13", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q14": (["(A) 13","(B) 19","(C) 5","(D) 35"], "(B) 19", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q14", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q15": (["(A) √2","(B) 2","(C) 4","(D) 8"], "(B) 2", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q15", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q16": (["(A) 2.4142","(B) 5.8282","(C) 0.4142","(D) 0.1718"], "(C) 0.4142", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q16", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q17": (["(A) 2^(-1/6)","(B) 2^(-6)","(C) 2^(1/6)","(D) 2^6"], "(C) 2^(1/6)", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q17", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q18": (["(A) √2","(B) 2","(C) ¹²√2","(D) ¹²√32"], "(B) 2", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q18", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q19": (["(A) 1/9","(B) 1/3","(C) 9","(D) 1/81"], "(A) 1/9", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q19", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q20": (["(A) 4","(B) 16","(C) 64","(D) 256.25"], "(A) 4", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q20", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q21": (["(A) x^(12/7) - x^(5/7)","(B) ¹²√(x⁴)^(1/3)","(C) (√(x³))^(2/3)","(D) x^(12/7) × x^(7/12)"], "(C) (√(x³))^(2/3)", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.1 Q21", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u01-q22": (None, "Yes. Let x = 21, y = √2 be a rational number and irrational number respectively. Now x + y = 21 + √2 = 22.4142... which is non-terminating and non-recurring. Hence x + y is irrational.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q1", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u01-q23": (None, "No. 0 × √2 = 0 which is not irrational.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q2", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u01-q24": (["True","False"], "False. Although √2/3 is of the form p/q, here p = √2 is not an integer.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q3(i)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u01-q25": (["True","False"], "False. Between any two integers there is only a finite number of integers.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q3(ii)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u01-q26": (["True","False"], "False. For example (∜2)² = √2 which is not rational.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q3(v)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u01-q27": (["True","False"], "False, because √12/√3 = √(12/3) = √4 = 2, which is a rational number.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.2 Q3(vi)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u01-q28": (None, "Rational, as √196 = 14", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.3 Q1(i)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u01-q29": (None, "Irrational, as 3√18 = 9√2, which is the product of a rational and an irrational number and so an irrational number.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.3 Q1(ii)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u01-q30": (None, "Irrational, as √(9/27) = 1/√3, which is the quotient of a rational and an irrational number and so an irrational number.", "NCERT Exemplar Class IX Mathematics, Answers Unit 1, Ex 1.3 Q1(iii)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q01": (["(A) x²/2 - 2/x²","(B) √(2x) - 1","(C) x² + 3x^(3/2)/√x","(D) (x - 1)/(x + 1)"], "(C) x² + 3x^(3/2)/√x", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q1", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q02": (["(A) 2","(B) 0","(C) 1","(D) 1/2"], "(B) 0", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q2", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q03": (["(A) 4","(B) 5","(C) 3","(D) 7"], "(A) 4", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q3", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q04": (["(A) 0","(B) 1","(C) Any natural number","(D) Not defined"], "(D) Not defined", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q4", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q05": (["(A) 0","(B) 1","(C) 4√2","(D) 8√2 + 1"], "(B) 1", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q5", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q06": (["(A) -6","(B) 6","(C) 2","(D) -2"], "(A) -6", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q6", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q07": (["(A) 3","(B) 2x","(C) 0","(D) 6"], "(D) 6", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q7", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q08": (["(A) 0","(B) 1","(C) Any real number","(D) Not defined"], "(C) Any real number", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q8", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q09": (["(A) -2/5","(B) -5/2","(C) 2/5","(D) 5/2"], "(B) -5/2", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q9", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q10": (["(A) 2","(B) 1/2","(C) -1/2","(D) -2"], "(B) 1/2", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q10", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q11": (["(A) 0","(B) 1","(C) 49","(D) 50"], "(D) 50", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q11", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q12": (["(A) -3","(B) 4","(C) 2","(D) -2"], "(C) 2", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q12", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q13": (["(A) x³ + x² - x + 1","(B) x³ + x² + x + 1","(C) x⁴ + x³ + x² + 1","(D) x⁴ + 3x³ + 3x² + x + 1"], "(B) x³ + x² + x + 1", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q13", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q14": (["(A) 5 + x","(B) 5 - x","(C) 5x - 1","(D) 10x"], "(D) 10x", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q14", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q15": (["(A) 1²","(B) 477","(C) 487","(D) 497"], "(D) 497", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q15", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q16": (["(A) (x + 1) (x + 3)","(B) (2x + 1) (2x + 3)","(C) (2x + 2) (2x + 5)","(D) (2x - 1) (2x - 3)"], "(B) (2x + 1) (2x + 3)", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q16", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q17": (["(A) x² + y² + 2xy","(B) x² + y² - xy","(C) xy²","(D) 3xy"], "(D) 3xy", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q17", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q18": (["(A) 1","(B) 9","(C) 18","(D) 27"], "(D) 27", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q18", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q19": (["(A) 1","(B) -1","(C) 0","(D) 1/2"], "(C) 0", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q19", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q20": (["(A) 0","(B) 1/√2","(C) 1/4","(D) 1/2"], "(C) 1/4", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q20", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q21": (["(A) 0","(B) abc","(C) 3abc","(D) 2abc"], "(C) 3abc", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.1 Q21", "MULTIPLE_CHOICE"),
    "ncert-exemplar-g9-math-u02-q22": (None, "Polynomials: (iii) and (iv) because the exponent of the variable after simplification in each of these is a whole number.", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.2 Q1", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q23": (["True","False"], "False, because a binomial has exactly two terms.", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.2 Q2(i)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u02-q24": (["True","False"], "False, x³ + x + 1 is a polynomial but not a binomial.", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.2 Q2(ii)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u02-q25": (["True","False"], "False, a quadratic polynomial can have up to two zeroes.", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.2 Q2(iv)", "TRUE_FALSE"),
    "ncert-exemplar-g9-math-u02-q26": (None, "5", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.3 Q1(i)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q27": (None, "8", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.3 Q1(ii)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q28": (None, "0", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.3 Q1(iii)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q29": (None, "1", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.3 Q2(i)", "SHORT_ANSWER"),
    "ncert-exemplar-g9-math-u02-q30": (None, "-1", "NCERT Exemplar Class IX Mathematics, Answers Unit 2, Ex 2.3 Q2(ii)", "SHORT_ANSWER"),
}


def intake_banks(repo: Path) -> list[dict]:
    """Only validated, unique flat-identity source banks enter the TEST projection."""
    return test_intake_registry.load_intake_banks(repo)


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
            value = {"status": projected, "receipt": path.relative_to(repo).as_posix(),
                     "stem_sha256": row.get("stem_sha256"),
                     "original_identifier": row.get("original_identifier"),
                     "official_answer_text": row.get("official_answer_text"),
                     "official_answer_locator": row.get("official_answer_locator")}
            if source_id in rows and rows[source_id] != value:
                raise ValueError(f"conflicting TEST question validation receipts for {source_id}")
            rows[source_id] = value
    return rows


def payload(repo: Path) -> dict:
    validations = validation_index(repo)
    custody = test_source_custody.reconcile(repo)
    source_evidence = {row["intake_question_ref"]: row for row in custody["handoff"]}
    source_holds = set(custody["hold_ids"])
    banks = json.loads(json.dumps(intake_banks(repo)))
    counts: dict[str, int] = {}
    custody_counts = {"INDEPENDENTLY_EVIDENCED": 0, "EVIDENCE_PENDING": 0, "SOURCE_TEXT_HOLD": 0}
    for bank in banks:
        for question in bank.get("questions") or []:
            row = validations.get(question.get("id")) or {"status": UNVALIDATED, "receipt": None}
            # A PASS receipt for a superseded source digest is historical evidence,
            # never approval of the corrected wording. Preserve receipts unchanged.
            source_id = question.get("id")
            matches_source = (
                row.get("stem_sha256") == question.get("stem_sha256")
                and row.get("original_identifier") == question.get("original_identifier")
                and row.get("official_answer_text") == question.get("official_answer_text")
                and row.get("official_answer_locator") == question.get("answer_key_locator")
                and source_id in HISTORICAL_ACADEMIC_CAPTURE_SCOPE
                and (question.get("options"), question.get("official_answer_text"),
                     question.get("answer_key_locator"), question.get("question_type"))
                    == HISTORICAL_ACADEMIC_CAPTURE_SCOPE[source_id]
            )
            academic_status = row["status"] if matches_source else UNVALIDATED
            question["academic_validation_status"] = academic_status
            question["academic_validation_receipt"] = row["receipt"] if matches_source else None
            counts[academic_status] = counts.get(academic_status, 0) + 1
            evidence = source_evidence.get(question["id"])
            state = ("INDEPENDENTLY_EVIDENCED" if evidence else
                     "SOURCE_TEXT_HOLD" if question["id"] in source_holds else "EVIDENCE_PENDING")
            custody_counts[state] += 1
            question["custody_evidence_status"] = state
            question["custody_evidence_ref"] = evidence["verification_evidence_ref"] if evidence else None
            question["custody_source_locator"] = evidence["source_locator"] if evidence else None
            question["custody_question_source_url"] = (
                evidence["source_identity"]["document_url"] if evidence else question["source_url"]
            )
            verified_key = evidence["official_answer_key_ref"] if evidence else None
            question["custody_answer_source_url"] = verified_key["document_url"] if verified_key else None
    return {
        "schema_version": "grade9v3-test-question-bank-projection-v1",
        "academic_validation_status": "PER_QUESTION",
        "validation_counts": dict(sorted(counts.items())),
        "custody_evidence_counts": dict(sorted(custody_counts.items())),
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
.tqb-shell{max-width:1220px;margin:0 auto;padding:24px}.tqb-intro{background:#fff7ed;border:1px solid #fdba74;border-radius:12px;padding:16px;margin:0 0 18px}.tqb-intro strong{color:#9a3412}.tqb-stats{display:flex;gap:8px;flex-wrap:wrap;margin:12px 0}.tqb-stat,.tqb-badge{display:inline-flex;align-items:center;border-radius:999px;padding:5px 9px;font:700 12px/1.2 system-ui,sans-serif}.tqb-stat{background:#e2e8f0;color:#0f172a}.tqb-controls{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,200px),1fr));gap:10px;align-items:end;position:sticky;top:0;z-index:3;background:var(--bg,#f8fafc);padding:10px 0 14px}.tqb-controls>*{min-width:0}.tqb-controls label{display:grid;min-width:0;gap:4px;font:700 12px/1.2 system-ui,sans-serif}.tqb-controls input,.tqb-controls select,.tqb-controls button{width:100%;max-width:100%;min-width:0;min-height:48px;box-sizing:border-box;border:1px solid #cbd5e1;border-radius:8px;padding:8px 10px;background:white;color:#0f172a}.tqb-controls button{cursor:pointer;font-weight:700}.tqb-result-count{margin:4px 0 12px;font-weight:700}.tqb-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:14px}.tqb-card{border:1px solid #cbd5e1;border-radius:12px;background:#fff;padding:16px;min-width:0}.tqb-card[hidden]{display:none}.tqb-card h2{font-size:18px;margin:10px 0 4px}.tqb-badges{display:flex;gap:6px;flex-wrap:wrap}.tqb-badge-source{background:#dcfce7;color:#166534}.tqb-badge-unvalidated{background:#fef3c7;color:#92400e;border:1px solid #f59e0b}.tqb-badge-validated{background:#dbeafe;color:#1e40af;border:1px solid #60a5fa}.tqb-badge-review{background:#fee2e2;color:#991b1b}.tqb-badge-custody{background:#dcfce7;color:#166534}.tqb-badge-pending{background:#fff7ed;color:#9a3412;border:1px solid #fdba74}.tqb-meta,.tqb-muted{color:#64748b;font-size:13px;overflow-wrap:anywhere}.tqb-stem{font-size:17px;line-height:1.55;margin:14px 0}.tqb-options{margin:8px 0 12px;padding-left:24px}.tqb-options li{margin:5px 0}.tqb-answer{border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px}.tqb-answer summary{cursor:pointer;font-weight:700;min-height:48px;display:flex;align-items:center}.tqb-warning{background:#fffbeb;border-left:4px solid #f59e0b;padding:8px 10px;font-size:13px}.tqb-card-footer{display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap;border-top:1px solid #e2e8f0;margin-top:12px;padding-top:10px;color:#64748b;font-size:12px}.tqb-card-footer a{display:inline-flex;min-height:48px;align-items:center;color:#1d4ed8;text-decoration:underline}.tqb-empty{padding:32px;text-align:center;border:1px dashed #94a3b8;border-radius:12px}.tqb-test-nav{display:flex;flex-wrap:wrap;gap:4px;margin:0;padding:0 14px;background:#7c2d12}.tqb-test-nav a{display:inline-flex;min-height:48px;align-items:center;padding:0 10px;color:#fde68a;font-weight:700;text-decoration:none}.tqb-test-banner{background:#7c2d12;color:white;padding:8px 14px;font:600 14px/1.4 system-ui,sans-serif}
@media(max-width:800px){.tqb-controls{grid-template-columns:1fr;position:static}.tqb-grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<div class="tqb-test-banner" data-g9-test-banner role="note">TEST sandbox · drafts only · not reviewed, not accepted, not curriculum</div>
<nav class="tqb-test-nav" aria-label="TEST"><a href="../../index.html">Portal</a><a href="../index.html">TEST</a><a href="index.html" aria-current="page">Question Bank</a><a href="../atlas/index.html">Atlas</a><a href="../rungs/index.html">Rungs</a><a href="../deployments/index.html">Deployments</a></nav>
<main class="tqb-shell">
<h1>TEST Question Bank</h1>
<section class="tqb-intro"><strong>Academic validation boundary.</strong> These questions are parked for review. An intake text-verification claim, independent official-source custody evidence, and Grade9V3 academic validation are three separate states. Only records with independent evidence can be READY_FOR_BLUEPRINT; the other records remain evidence-pending regardless of their historical workflow label. A question remains <strong>UNVALIDATED</strong> until a source-bound validation receipt marks it PASS and admission-eligible; validated questions show <strong>VALIDATED</strong>. Production admission is governed separately.</section>
<div class="tqb-stats" id="tqbStats"></div>
<section class="tqb-controls" aria-label="Question filters">
<label>Search<input id="tqbSearch" type="search" placeholder="Question, topic, id…" autocomplete="off"></label>
<label>Unit<select id="tqbUnit"><option value="">All units</option></select></label>
<label>Type<select id="tqbType"><option value="">All types</option></select></label>
<label>Subject<select id="tqbSubject"><option value="">All subjects</option></select></label>
<label>Grade<select id="tqbGrade"><option value="">All grades</option></select></label>
<label>Authority<select id="tqbAuthority"><option value="">All authorities</option></select></label>
<label>Source kind<select id="tqbKind"><option value="">All source kinds</option></select></label>
<label>Topic<select id="tqbTopic"><option value="">All topics</option></select></label>
<label>Subtopic<select id="tqbSubtopic"><option value="">All subtopics</option></select></label>
<label>Intake state<select id="tqbIntake"><option value="">All intake states</option></select></label>
<label>Blueprint readiness<select id="tqbBlueprint"><option value="">All readiness states</option></select></label>
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
  const sourceFilename = q => String(q.custody_question_source_url || q.source_url || '').split('/').pop();
  const custodyStatus = q => q.custody_evidence_status || 'EVIDENCE_PENDING';
  const sourceVerified = q => q.text_verification_status === 'TEXT_VERIFIED_AGAINST_OFFICIAL';
  // Never use the historical workflow/status label as an authority for READY.
  const blueprintState = q => custodyStatus(q) === 'INDEPENDENTLY_EVIDENCED'
    ? 'READY_FOR_BLUEPRINT' : custodyStatus(q) === 'SOURCE_TEXT_HOLD'
    ? 'SOURCE_TEXT_HOLD' : 'EVIDENCE_PENDING';
  const intakeState = q => custodyStatus(q) === 'SOURCE_TEXT_HOLD' ? 'SOURCE_TEXT_HOLD' : 'TEST_VISIBLE';
  const facets = [
    ['tqbSubject', q => q.subject || 'Unknown'],
    ['tqbGrade', q => String(q.grade ?? 'Unknown')],
    ['tqbAuthority', q => q.source_authority || 'Unknown'],
    ['tqbKind', q => q.source_kind || 'Unknown'],
    ['tqbTopic', q => q.topic_label || 'Unknown'],
    ['tqbSubtopic', q => q.subtopic_label || 'Not labelled'],
    ['tqbIntake', intakeState],
    ['tqbBlueprint', blueprintState],
  ].map(([id, get]) => ({ id, get, control: document.getElementById(id) }));
  for (const {get, control} of facets) {
    const counts = new Map();
    questions.forEach(q => counts.set(get(q), (counts.get(get(q)) || 0) + 1));
    for (const [value, total] of [...counts].sort(([a],[b]) => a.localeCompare(b))) {
      const option = document.createElement('option');
      option.value = value;
      option.textContent = label(value) + ' (' + total + ')';
      control.append(option);
    }
  }
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
  const evidenceCount = questions.filter(q => custodyStatus(q) === 'INDEPENDENTLY_EVIDENCED').length;
  const holdCount = questions.filter(q => custodyStatus(q) === 'SOURCE_TEXT_HOLD').length;
  const pendingCount = questions.length - evidenceCount - holdCount;
  const validatedCount = questions.filter(q => validationStatus(q) === 'VALIDATED').length;
  const unvalidatedCount = questions.filter(q => validationStatus(q) === 'UNVALIDATED').length;
  const duplicateCount = questions.filter(q => q.workflow_status === 'DUPLICATE_REVIEW').length;
  stats.innerHTML = '<span class="tqb-stat">'+questions.length+' questions</span>'
    + '<span class="tqb-stat">'+verifiedCount+' legacy text-verification labels</span>'
    + '<span class="tqb-stat">'+evidenceCount+' independent source evidence</span>'
    + '<span class="tqb-stat">'+holdCount+' source-text hold</span>'
    + '<span class="tqb-stat">'+pendingCount+' evidence pending</span>'
    + '<span class="tqb-stat">'+validatedCount+' academically validated</span>'
    + '<span class="tqb-stat">'+unvalidatedCount+' academically unvalidated</span>'
    + '<span class="tqb-stat">'+duplicateCount+' duplicate review</span>'
    + '<span class="tqb-stat">'+units.size+' units</span>';

  function renderCard(q) {
    const options = (q.options || []).length
      ? '<ol class="tqb-options">'+q.options.map(option => '<li>'+esc(option)+'</li>').join('')+'</ol>' : '';
    const academic = validationStatus(q);
    const independentlyEvidenced = custodyStatus(q) === 'INDEPENDENTLY_EVIDENCED';
    const sourceHold = custodyStatus(q) === 'SOURCE_TEXT_HOLD';
    const answerNote = sourceHold
      ? 'SOURCE-TEXT HOLD: official NCERT wording differs from this recorded stem; source custody and READY are withheld pending review.'
      : !q.custody_answer_source_url
      ? 'This answer is recorded in intake, but its official answer-document custody has not been independently reconciled.'
      : academic === 'VALIDATED'
        ? 'Independent official-answer custody and Grade9V3 academic validation are separately evidenced.'
        : 'Official-answer custody is independently evidenced. Grade9V3 academic validation is still pending.';
    const answer = q.official_answer_text
      ? '<details class="tqb-answer"><summary>'+(q.custody_answer_source_url ? 'Evidenced official answer' : 'Recorded answer — official key custody pending')+'</summary><p><strong>'+esc(q.official_answer_text)+'</strong></p>'
        + '<p class="tqb-muted">'+esc(q.answer_key_locator || '')+'</p>'
        + '<p class="tqb-warning">'+esc(answerNote)+'</p></details>'
      : '<p class="tqb-warning">No source answer is recorded. Academic validation remains pending.</p>';
    const text = [q.id,q.original_identifier,q.stem,q.chapter_or_unit,q.exercise_or_section,q.topic_label,q.subtopic_label,q.question_type].join(' ').toLowerCase();
    const article = document.createElement('article');
    article.className = 'tqb-card';
    article.id = q.id;
    article.dataset.g9TestQuestion = q.id;
    article.dataset.g9Validation = academic;
    article.dataset.g9Custody = custodyStatus(q);
    article.dataset.g9SourceVerification = independentlyEvidenced ? 'SOURCE VERIFIED'
      : sourceHold ? 'SOURCE TEXT HOLD' : 'SOURCE EVIDENCE PENDING';
    article.dataset.g9LegacyTextStatus = sourceVerified(q) ? 'HISTORICAL_TEXT_VERIFIED_LABEL'
      : (q.text_verification_status || 'HISTORICAL_STATUS_UNKNOWN');
    article.dataset.g9Review = q.workflow_status || '';
    article.dataset.unit = q.chapter_or_unit || '';
    article.dataset.type = q.question_type || '';
    facets.forEach(({id,get}) => { article.dataset[id] = get(q); });
    article.dataset.search = text;
    article.innerHTML = '<div class="tqb-badges">'
      + '<span class="tqb-badge '+(independentlyEvidenced ? 'tqb-badge-custody' : 'tqb-badge-pending')+'">'+(independentlyEvidenced ? 'SOURCE EVIDENCED' : sourceHold ? 'SOURCE TEXT HOLD' : 'EVIDENCE PENDING')+'</span>'
      + '<span class="tqb-badge tqb-stat">'+esc(q.subject || '')+' · Grade '+esc(q.grade)+'</span>'
      + '<span class="tqb-badge tqb-stat">'+esc(label(q.source_authority))+' · '+esc(label(q.source_kind))+'</span>'
      + '<span class="tqb-badge tqb-stat">Intake: '+esc(label(intakeState(q)))+'</span>'
      + '<span class="tqb-badge '+(independentlyEvidenced ? 'tqb-badge-custody' : 'tqb-badge-pending')+'">Blueprint: '+esc(label(blueprintState(q)))+'</span>'
      + '<span class="tqb-badge '+(academic === 'VALIDATED' ? 'tqb-badge-validated' : 'tqb-badge-unvalidated')+'">Academic: '+esc(academic)+'</span>'+reviewBadge(q)+'</div>'
      + '<h2>'+esc(q.original_identifier || q.id)+'</h2>'
      + '<p class="tqb-meta"><code>'+esc(q.id)+'</code> · '+esc(q.chapter_or_unit || '')+' · '+esc(q.exercise_or_section || '')+' · '+esc(label(q.question_type || ''))+'</p>'
      + '<p class="tqb-meta">'+esc(q.topic_label || '')+(q.subtopic_label ? ' · '+esc(q.subtopic_label) : '')+'</p>'
      + '<div class="tqb-stem">'+esc(q.stem || '')+'</div>'+options+answer
      + '<footer class="tqb-card-footer"><span>'+esc(q.wording_custody || '')+' · '+esc(q.capture_method || '')+'</span>'
      + '<span>Source: <a href="'+esc(q.custody_question_source_url || q.source_url || '')+'" target="_blank" rel="noopener noreferrer">'+esc(sourceFilename(q))+'</a>'
      + ' · '+esc(q.exercise_or_section || '')+' Q'+esc(q.question_number || '')
      + (independentlyEvidenced ? ' · printed page '+esc(q.custody_source_locator.printed_page)+' / PDF index '+esc(q.custody_source_locator.pdf_page_index) : ' · independent locator pending')
      + '</span></footer>';
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
        && (!type.value || card.dataset.type === type.value)
        && facets.every(({id,control}) => !control.value || card.dataset[id] === control.value);
      card.hidden = !matches;
      if (matches) visible += 1;
    });
    count.textContent = visible + ' of ' + cards.length + ' questions shown';
    empty.hidden = visible !== 0;
  }
  [search, unit, type, ...facets.map(({control}) => control)].forEach(control => control.addEventListener('input', apply));
  reset.addEventListener('click', () => {
    [search, unit, type, ...facets.map(({control}) => control)].forEach(control => { control.value = ''; });
    apply(); search.focus();
  });
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
