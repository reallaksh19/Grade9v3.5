"""Validate primary-source observation ledgers without granting source custody.

Review notes are *not* independently authenticated custody overlays. A matched
NCERT page observed during review still needs a separately reconciled source/text
witness before READY_FOR_BLUEPRINT may be projected to TEST.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

from Shared.tools import test_intake_registry, test_source_custody

SCHEMA = "grade9v3-test-primary-source-review-v1"
ROOT = "TEST/evidence/source-intake"
STATES = {"VISUAL_MATCH", "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "SOURCE_NOTATION_DISCREPANCY"}
ANSWER_DOCUMENT = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"


def validate(repo: Path) -> dict:
    """Fail on malformed, stale, duplicated or falsely promoted review claims."""
    questions = {q["id"]: q for bank in test_intake_registry.load_intake_banks(repo)
                 for q in bank["questions"]}
    custody = test_source_custody.reconcile(repo)
    current_ready = set(custody["ready_ids"])
    reviewed: dict[str, dict] = {}
    paths = sorted((repo / ROOT).glob("*.review.v1.json"))
    for path in paths:
        try:
            ledger = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: invalid primary-source review: {exc}") from exc
        where = str(path)
        if not isinstance(ledger, dict) or ledger.get("schema_version") != SCHEMA:
            raise ValueError(f"{where}: invalid review schema")
        if ledger.get("source_bank_ref") != "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json":
            raise ValueError(f"{where}: review source bank does not match")
        if ledger.get("answer_document") != ANSWER_DOCUMENT:
            raise ValueError(f"{where}: unrecognized official answer document")
        documents = ledger.get("question_documents")
        if (not isinstance(documents, list) or len(documents) == 0
                or len(set(documents)) != len(documents)
                or not all(test_intake_registry.official_source_url(s, "NCERT_OFFICIAL") for s in documents)):
            raise ValueError(f"{where}: invalid official question document list")
        records = ledger.get("records")
        if not isinstance(records, list) or not records:
            raise ValueError(f"{where}: review must have source-bound records")
        for record in records:
            if not isinstance(record, dict):
                raise ValueError(f"{where}: invalid record")
            qid = record.get("source_id")
            question = questions.get(qid)
            if question is None or qid in reviewed:
                raise ValueError(f"{where}: unknown or duplicate review source id {qid!r}")
            if qid in current_ready:
                raise ValueError(f"{where}: already custody READY; review-only record would misstate live custody")
            if (record.get("projection_disposition") != "EVIDENCE_PENDING"
                    or record.get("source_custody_promoted") is not False):
                raise ValueError(f"{where}: review cannot grant source readiness for {qid}")
            if record.get("comparison_status") not in STATES:
                raise ValueError(f"{where}: unknown review comparison result for {qid}")
            if record.get("reviewer_observation") != "DIRECT_NCERT_PRIMARY_PDF_VISUAL_REVIEW":
                raise ValueError(f"{where}: missing explicitly described review method for {qid}")
            stem = record.get("captured_stem")
            digest = record.get("stem_sha256")
            if (not isinstance(stem, str) or stem != question["stem"]
                    or digest != question["stem_sha256"]
                    or digest != "sha256:" + hashlib.sha256(stem.encode("utf-8")).hexdigest()):
                raise ValueError(f"{where}: review source stem digest/wording mismatch for {qid}")
            if (record.get("original_identifier") != question["original_identifier"]
                    or record.get("captured_options") != question.get("options", [])):
                raise ValueError(f"{where}: review source identifier/options mismatch for {qid}")
            url = record.get("official_question_document_url")
            if (url not in documents or url != question["source_url"]
                    or not test_intake_registry.official_source_url(url, question["source_authority"])):
                raise ValueError(f"{where}: review official source document mismatch for {qid}")
            loc = record.get("source_locator")
            if (not isinstance(loc, dict)
                    or any(loc.get(f) != question[f] for f in
                           ("chapter_or_unit", "exercise_or_section", "question_number"))
                    or type(loc.get("printed_page")) is not int or loc["printed_page"] < 1
                    or type(loc.get("pdf_page_index")) is not int or loc["pdf_page_index"] < 0):
                raise ValueError(f"{where}: invalid reported review locator for {qid}")
            if (record.get("official_answer_document_url") != ANSWER_DOCUMENT
                    or type(record.get("official_answer_pdf_page_index")) is not int
                    or record["official_answer_pdf_page_index"] < 0):
                raise ValueError(f"{where}: review answer document locator mismatch for {qid}")
            answer = record.get("captured_answer")
            key = record.get("official_answer_key")
            if (not isinstance(answer, str) or answer != question.get("official_answer_text")
                    or not isinstance(key, str) or not answer.startswith(key)
                    or not any(isinstance(option, str) and option == answer
                               for option in question.get("options", []))):
                raise ValueError(f"{where}: review answer/captured option mismatch for {qid}")
            if (not isinstance(record.get("comparison_note"), str)
                    or not record["comparison_note"].strip()):
                raise ValueError(f"{where}: comparison needs explicit source-note for {qid}")
            reviewed[qid] = record
    return {"reviewed": len(reviewed), "review_ids": sorted(reviewed),
            "notation_discrepancies": sorted(qid for qid, r in reviewed.items()
                                            if r["comparison_status"] == "SOURCE_NOTATION_DISCREPANCY"),
            "custody_promotions": 0}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args(argv)
    try:
        result = validate(args.repo)
    except ValueError as exc:
        print(f"TEST source review rejected: {exc}", file=sys.stderr)
        return 1
    print(f"TEST source review: {result['reviewed']} reviewed; "
          f"{len(result['notation_discrepancies'])} notation discrepancy; "
          "0 READY promoted by review alone")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
