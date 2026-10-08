"""Immutable U01/U02 Q13-Q14 rendered-page observations; NOT an NCERT custody oracle."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry, test_source_custody  # noqa: E402

LEDGER = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q13-q14.observation.v1.json"
BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
FROZEN_ROOT = json.loads(r'''{"schema_version":"grade9v3-test-primary-source-page-observation-v1","scope":"R4 NEXT multi-topic U01/U02 Q13-Q14 official rendered-page observation; NOT authenticated source custody","checked_on":"2026-10-08","source_bank_ref":"TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json","question_documents":["https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf"],"answer_document":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","verification_method":"Direct visual comparison of official NCERT Unit 1/Unit 2 rendered PDF pages and separate answer-key rendered pages; no source PDF bytes or edition-authenticated digest available.","witness_limit":"Visual page inspection only; NOT an independently authenticated PDF byte snapshot or READY-for-blueprint source custody witness. Do not reuse academic PASS, apply canonical changes or authorize publication.","official_pdf_bytes_available":false,"official_pdf_sha256":null,"independent_custody_witness_authenticated":false,"source_custody_promoted":false,"academic_status_promoted":false,"publication_authorized":false}''')
FROZEN_ROWS = json.loads(r'''{"ncert-exemplar-g9-math-u01-q13":{"source_id":"ncert-exemplar-g9-math-u01-q13","original_identifier":"Unit 1 Ex 1.1 Q13","captured_stem":"1/(√9 - √8) is equal to","stem_sha256":"sha256:68dd99035094965dfffc7f590939885de8f7a79abf42652e8a380fe3762e100f","captured_options":["(A) (1/2)(3 - 2√2)","(B) 1/(3 + 2√2)","(C) 3 - 2√2","(D) 3 + 2√2"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","source_locator":{"chapter_or_unit":"Unit 1: Number Systems","exercise_or_section":"Exercise 1.1","question_number":"13","printed_page":4,"pdf_page_index":3},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":0,"official_answer_key":"(D)","captured_answer":"(D) 3 + 2√2","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"The displayed radical denominator sqrt(9)-sqrt(8), the 1/2 and reciprocal choices, and the conjugate radical choices correspond to the Unicode linearisation.","observation_method":"DIRECT_NCERT_PRIMARY_PDF_RENDERED_PAGE_VISUAL_REVIEW","projection_disposition":"EVIDENCE_PENDING","source_custody_promoted":false,"academic_status_promoted":false,"publication_authorized":false},"ncert-exemplar-g9-math-u01-q14":{"source_id":"ncert-exemplar-g9-math-u01-q14","original_identifier":"Unit 1 Ex 1.1 Q14","captured_stem":"After rationalising the denominator of 7/(3√3 - 2√2), we get the denominator as","stem_sha256":"sha256:95d25533fea0dcc9eb50988ea5cc43ada64846d10ee81ae284015a640ad5f300","captured_options":["(A) 13","(B) 19","(C) 5","(D) 35"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","source_locator":{"chapter_or_unit":"Unit 1: Number Systems","exercise_or_section":"Exercise 1.1","question_number":"14","printed_page":4,"pdf_page_index":3},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":0,"official_answer_key":"(B)","captured_answer":"(B) 19","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"The displayed 7/(3sqrt(3)-2sqrt(2)) fraction and numerical denominator options correspond; NCERT key selects 19.","observation_method":"DIRECT_NCERT_PRIMARY_PDF_RENDERED_PAGE_VISUAL_REVIEW","projection_disposition":"EVIDENCE_PENDING","source_custody_promoted":false,"academic_status_promoted":false,"publication_authorized":false},"ncert-exemplar-g9-math-u02-q13":{"source_id":"ncert-exemplar-g9-math-u02-q13","original_identifier":"Unit 2 Ex 2.1 Q13","captured_stem":"x + 1 is a factor of the polynomial","stem_sha256":"sha256:abeca57b608b4bc073ec9a5ed39a7b52f75aba48ce41c07730a8178cd8cbd0ad","captured_options":["(A) x³ + x² - x + 1","(B) x³ + x² + x + 1","(C) x⁴ + x³ + x² + 1","(D) x⁴ + 3x³ + 3x² + x + 1"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf","source_locator":{"chapter_or_unit":"Unit 2: Polynomials","exercise_or_section":"Exercise 2.1","question_number":"13","printed_page":15,"pdf_page_index":2},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":3,"official_answer_key":"(B)","captured_answer":"(B) x³ + x² + x + 1","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"The four polynomial options with x squared/cubed/fourth powers correspond to the Unicode superscript capture.","observation_method":"DIRECT_NCERT_PRIMARY_PDF_RENDERED_PAGE_VISUAL_REVIEW","projection_disposition":"EVIDENCE_PENDING","source_custody_promoted":false,"academic_status_promoted":false,"publication_authorized":false},"ncert-exemplar-g9-math-u02-q14":{"source_id":"ncert-exemplar-g9-math-u02-q14","original_identifier":"Unit 2 Ex 2.1 Q14","captured_stem":"One of the factors of (25x² - 1) + (1 + 5x)² is","stem_sha256":"sha256:f4baf8c2a268fcc4e39b925bb35c4486db2c85b9eb717d0a4fc775fd2462ffb1","captured_options":["(A) 5 + x","(B) 5 - x","(C) 5x - 1","(D) 10x"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf","source_locator":{"chapter_or_unit":"Unit 2: Polynomials","exercise_or_section":"Exercise 2.1","question_number":"14","printed_page":15,"pdf_page_index":2},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":3,"official_answer_key":"(D)","captured_answer":"(D) 10x","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"The official polynomial (25x^2-1)+(1+5x)^2 and four factor choices correspond to the source capture.","observation_method":"DIRECT_NCERT_PRIMARY_PDF_RENDERED_PAGE_VISUAL_REVIEW","projection_disposition":"EVIDENCE_PENDING","source_custody_promoted":false,"academic_status_promoted":false,"publication_authorized":false}}''')


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("R4 Q13-Q14 visual-only source observation: " + message)


def validate(repo: Path = REPO) -> dict:
    try:
        doc = json.loads((repo / LEDGER).read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("R4 Q13-Q14 visual-only source observation: missing/invalid ledger") from exc
    _require(isinstance(doc, dict), "ledger must be an object")
    rows = doc.get("records")
    root = dict(doc)
    root.pop("records", None)
    _require(root == FROZEN_ROOT, "frozen root scope, provenance, or authority rewritten")
    _require(isinstance(rows, list) and len(rows) == len(FROZEN_ROWS),
             "exact four independently scoped rows required")

    questions = {q["id"]: q for b in test_intake_registry.load_intake_banks(repo)
                 for q in b["questions"]}
    _require(len(questions) == 210, "must preserve 210 original unique source IDs")
    seen: set[str] = set()
    for r in rows:
        _require(isinstance(r, dict), "each record must be an object")
        qid = r.get("source_id")
        _require(isinstance(qid, str) and qid in FROZEN_ROWS and qid not in seen,
                 "unexpected, duplicated or substituted source ID")
        seen.add(qid)
        _require(r == FROZEN_ROWS[qid],
                 f"frozen options, locators, key, source observation, or authority rewritten: {qid}")
        q = questions.get(qid)
        _require(q is not None, f"source missing from intake: {qid}")
        _require((q["original_identifier"], q["stem"], q["stem_sha256"], q["options"],
                  q["source_url"], q["chapter_or_unit"], q["exercise_or_section"],
                  q["question_number"], q["official_answer_text"]) ==
                 (r["original_identifier"], r["captured_stem"], r["stem_sha256"],
                  r["captured_options"], r["official_question_document_url"],
                  r["source_locator"]["chapter_or_unit"],
                  r["source_locator"]["exercise_or_section"],
                  r["source_locator"]["question_number"], r["captured_answer"]),
                 f"immutable bank-versus-observation text/locator/answer mismatch: {qid}")
        _require(q["stem_sha256"] ==
                 "sha256:" + hashlib.sha256(q["stem"].encode("utf-8")).hexdigest(),
                 f"raw source stem digest mismatch: {qid}")
        _require(r["captured_answer"] in q["options"]
                 and r["captured_answer"].startswith(r["official_answer_key"]),
                 f"captured answer not in four options: {qid}")
        _require(q["source_authority"] == "NCERT_OFFICIAL"
                 and q["source_kind"] == "EXEMPLAR"
                 and q["workflow_status"] == "EVIDENCE_PENDING"
                 and q["wording_custody"] == "CAPTURED_UNVERIFIED"
                 and q["text_verification_status"] == "CAPTURED_UNVERIFIED",
                 f"visual observation cannot promote intake authority: {qid}")
        _require(r["source_custody_promoted"] is False
                 and r["academic_status_promoted"] is False
                 and r["publication_authorized"] is False
                 and r["projection_disposition"] == "EVIDENCE_PENDING",
                 f"historical visual review cannot grant READY: {qid}")
    _require(seen == set(FROZEN_ROWS), "some frozen IDs missing")
    custody = test_source_custody.reconcile(repo)
    _require(not set(seen) & set(custody["ready_ids"]),
             "visual-only observation must not be promoted to READY via this review")
    return {"reviewed": len(seen), "source_ids": sorted(seen),
            "ready_granted": 0, "official_pdf_bytes_authenticated": False,
            "evidence_pending": len(seen)}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args(argv)
    try:
        report = validate(args.repo)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"R4 U01/U02 Q13–Q14: {report['reviewed']} visual-only observations; "
          "0 source READY; no authenticated PDF bytes")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
