"""Fail-closed R4 page-observation reconciliation; never source READY authority.

U01/U02 Exemplar Q11-Q12 are compared with official rendered PDFs.
No official PDF bytes were retrieved; visual review is not an authenticated
independent custody overlay or a reusable academic PASS receipt.
"""
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

FILE = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q11-q12.observation.v1.json"
BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
Q1 = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
Q2 = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf"
KEY = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"
SCHEMA = "grade9v3-test-primary-source-page-observation-v1"
METHOD = "DIRECT_NCERT_PRIMARY_PDF_RENDERED_PAGE_VISUAL_REVIEW"
MATCH = "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION"

# Frozen, literal page/key observations from 2026-10-08. These are independent
# of the mutable bank AND the mutable ledger; nevertheless they are NOT an
# authenticated official-PDF byte snapshot or custody certificate.
FROZEN = json.loads(r'''{"ncert-exemplar-g9-math-u01-q11":{"original_identifier":"Unit 1 Ex 1.1 Q11","captured_stem":"√10 × √15 is equal to","stem_sha256":"sha256:ffb8ba0ffe7ccce391022848b2bd1454dde1417114a7184eaafee1538cb32f5f","captured_options":["(A) 6√5","(B) 5√6","(C) √25","(D) 10√5"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","source_locator":{"chapter_or_unit":"Unit 1: Number Systems","exercise_or_section":"Exercise 1.1","question_number":"11","printed_page":4,"pdf_page_index":3},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":0,"official_answer_key":"(B)","captured_answer":"(B) 5√6","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"Printed radical multiplication and radical options linearised as Unicode surds; no conflicting symbols observed."},"ncert-exemplar-g9-math-u01-q12":{"original_identifier":"Unit 1 Ex 1.1 Q12","captured_stem":"The number obtained on rationalising the denominator of 1/(√7 - 2) is","stem_sha256":"sha256:905d8811c353324f74c3c955303079f0d0d8327cbb332da3dc43718fbdf78e0a","captured_options":["(A) (√7 + 2)/3","(B) (√7 - 2)/3","(C) (√7 + 2)/5","(D) (√7 + 2)/45"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf","source_locator":{"chapter_or_unit":"Unit 1: Number Systems","exercise_or_section":"Exercise 1.1","question_number":"12","printed_page":4,"pdf_page_index":3},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":0,"official_answer_key":"(A)","captured_answer":"(A) (√7 + 2)/3","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"Printed fraction with irrational denominator and rationalised fractional answer options linearised with parentheses."},"ncert-exemplar-g9-math-u02-q11":{"original_identifier":"Unit 2 Ex 2.1 Q11","captured_stem":"If x⁵¹ + 51 is divided by x + 1, the remainder is","stem_sha256":"sha256:73b99fb47b34f998a0ce47f48cab49607bb081b0eb4d882f18933d95480e65f1","captured_options":["(A) 0","(B) 1","(C) 49","(D) 50"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf","source_locator":{"chapter_or_unit":"Unit 2: Polynomials","exercise_or_section":"Exercise 2.1","question_number":"11","printed_page":15,"pdf_page_index":2},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":3,"official_answer_key":"(D)","captured_answer":"(D) 50","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"Printed polynomial power x^51 is represented with Unicode superscript; remainder options visually match."},"ncert-exemplar-g9-math-u02-q12":{"original_identifier":"Unit 2 Ex 2.1 Q12","captured_stem":"If x + 1 is a factor of the polynomial 2x² + kx, then the value of k is","stem_sha256":"sha256:11f4bebaa831493642170a8326e5561dda775dcc7ed45ebab4e3d63aa04b9f5b","captured_options":["(A) -3","(B) 4","(C) 2","(D) -2"],"official_question_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf","source_locator":{"chapter_or_unit":"Unit 2: Polynomials","exercise_or_section":"Exercise 2.1","question_number":"12","printed_page":15,"pdf_page_index":2},"official_answer_document_url":"https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf","official_answer_pdf_page_index":3,"official_answer_key":"(C)","captured_answer":"(C) 2","comparison_status":"VISUAL_MATCH_WITH_NOTATION_NORMALIZATION","comparison_note":"Printed polynomial exponent x^2 is represented with Unicode superscript; factor theorem option labels match."}}''')
ROOT_FIELDS = {
    "schema_version", "scope", "checked_on", "source_bank_ref",
    "question_documents", "answer_document", "verification_method",
    "witness_limit", "official_pdf_bytes_available", "official_pdf_sha256",
    "independent_custody_witness_authenticated", "source_custody_promoted",
    "academic_status_promoted", "publication_authorized", "records",
}
ROW_FIELDS = {
    "source_id", *next(iter(FROZEN.values())).keys(),
    "observation_method", "projection_disposition", "source_custody_promoted",
    "academic_status_promoted", "publication_authorized",
}


def require(ok: bool, where: str, issue: str) -> None:
    if not ok:
        raise ValueError(f"{where}: {issue}")


def validate(repo: Path = REPO) -> dict:
    path = repo / FILE
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError(f"{path}: missing or unreadable four-row observation: {exc}") from exc
    where = str(path)
    require(isinstance(doc, dict) and set(doc) == ROOT_FIELDS, where,
            "observation root shape or injected authority field")
    require(doc.get("schema_version") == SCHEMA
            and doc.get("checked_on") == "2026-10-08"
            and doc.get("source_bank_ref") == BANK
            and doc.get("scope") == (
                "R4 FOLLOWUP multi-topic U01/U02 Q11-Q12 rendered-page observation; "
                "explicitly NOT independent verified source custody"
            ), where, "fixed observation scope changed")
    require(doc.get("question_documents") == [Q1, Q2]
            and doc.get("answer_document") == KEY,
            where, "official question/answer source URLs changed")
    require(doc.get("verification_method") == (
                "Directly inspected rendered official NCERT question PDF pages and the "
                "separate NCERT answer-key PDF; recorded print/PDF coordinates. "
                "No official PDF bytes retrieved."
            ) and isinstance(doc.get("witness_limit"), str)
            and "NOT a reproducible cryptographic PDF byte snapshot" in doc["witness_limit"],
            where, "visual-only observation limitations omitted")
    require(doc.get("official_pdf_bytes_available") is False
            and doc.get("official_pdf_sha256") is None
            and doc.get("independent_custody_witness_authenticated") is False
            and all(doc.get(k) is False for k in
                    ("source_custody_promoted", "academic_status_promoted",
                     "publication_authorized")),
            where, "visual observation cannot assert PDF bytes/custody/academic/publication")

    banks = test_intake_registry.load_intake_banks(repo)
    questions = {q["id"]: q for b in banks for q in b["questions"]}
    require(len(questions) == 210, where, "original intake denominator changed")
    rows = doc.get("records")
    require(isinstance(rows, list) and len(rows) == len(FROZEN), where,
            "four immutable source IDs are required")
    seen = set()
    for r in rows:
        require(isinstance(r, dict) and set(r) == ROW_FIELDS, where,
                "observation record shape or injected authority field")
        qid = r.get("source_id")
        require(qid in FROZEN and qid not in seen, where,
                f"unexpected or duplicate observed source {qid!r}")
        seen.add(qid)
        q = questions.get(qid)
        require(q is not None, where, f"observed source missing in intake: {qid}")
        require(all(r.get(k) == v for k, v in FROZEN[qid].items()), where,
                f"frozen rendered-page observation changed: {qid}")
        require(r.get("observation_method") == METHOD
                and r.get("comparison_status") == MATCH
                and r.get("projection_disposition") == "EVIDENCE_PENDING"
                and all(r.get(k) is False for k in
                        ("source_custody_promoted", "academic_status_promoted",
                         "publication_authorized")),
                where, f"visual observation cannot promote {qid}")
        require(q.get("id") == qid
                and q.get("original_identifier") == r["original_identifier"]
                and q.get("stem") == r["captured_stem"]
                and q.get("stem_sha256") == r["stem_sha256"]
                and q.get("stem_sha256") == "sha256:" +
                    hashlib.sha256(q["stem"].encode("utf-8")).hexdigest()
                and q.get("options") == r["captured_options"],
                where, f"source bank stem/options/digest scope changed: {qid}")
        loc = r["source_locator"]
        require(all(loc.get(k) == q.get(k) for k in (
                    "chapter_or_unit", "exercise_or_section", "question_number"))
                and r["official_question_document_url"] == q.get("source_url")
                and q.get("source_authority") == "NCERT_OFFICIAL"
                and q.get("source_kind") == "EXEMPLAR",
                where, f"official document or source locator changed: {qid}")
        require(r["official_answer_document_url"] == KEY
                and r["official_answer_key"] == q["official_answer_text"].split()[0]
                and r["captured_answer"] == q["official_answer_text"]
                and r["captured_answer"] in q["options"],
                where, f"official answer key/option changed: {qid}")
        require(q.get("workflow_status") == "EVIDENCE_PENDING"
                and q.get("text_verification_status") == "CAPTURED_UNVERIFIED"
                and q.get("wording_custody") == "CAPTURED_UNVERIFIED",
                where, f"raw intake must not inherit new visual-source authority: {qid}")
    require(seen == set(FROZEN), where, "missing frozen source ID")
    custody = test_source_custody.reconcile(repo)
    return {
        "reviewed": len(seen), "review_ids": sorted(seen),
        "ready_granted": 0,
        "separately_ready": sorted(seen & set(custody["ready_ids"])),
        "official_pdf_bytes_available": False,
        "source_pending": sorted(seen - set(custody["ready_ids"])),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args(argv)
    try:
        report = validate(args.repo)
    except ValueError as exc:
        print(f"TEST source page observation rejected: {exc}", file=sys.stderr)
        return 1
    print(f"R4 rendered NCERT page observations: {report['reviewed']} across 2 topics; "
          "0 READY granted; official PDF bytes/digest unavailable")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
