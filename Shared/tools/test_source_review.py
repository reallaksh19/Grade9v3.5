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

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry, test_source_custody  # noqa: E402

SCHEMA = "grade9v3-test-primary-source-review-v1"
ROOT = "TEST/evidence/source-intake"
STATES = {"VISUAL_MATCH", "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "SOURCE_NOTATION_DISCREPANCY"}
ANSWER_DOCUMENT = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"

# Frozen *observations* from the eight-row R4 review, not independent custody.
# Prevent plausible numeric page/key or verdict rewrites from reusing that record.
# Changing an observation requires a deliberate, reviewable source-scope update.
FROZEN_R4_PRIMARY_OBSERVATIONS = {
    "ncert-exemplar-g9-math-u01-q07": ("Unit 1 Ex 1.1 Q7", "sha256:ca54af54c150e14888774feabed443bc1268dd4ffc24c58935994ef023b17e10", ("(A) 0.14", "(B) 0.1416 (with bar over 16)", "(C) 0.1416 (with bar over 1416)", "(D) 0.4014001400014..."), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf", 3, 2, 0, "SOURCE_NOTATION_DISCREPANCY", "(D)"),
    "ncert-exemplar-g9-math-u01-q08": ("Unit 1 Ex 1.1 Q8", "sha256:6b129d19cb6843884e9b3ece342b35792f0b5b2d6e68c5b5f711cd8efb3b4555", ("(A) (√2 + √3)/2", "(B) (√2 · √3)/2", "(C) 1.5", "(D) 1.8"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf", 3, 2, 0, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(C)"),
    "ncert-exemplar-g9-math-u01-q09": ("Unit 1 Ex 1.1 Q9", "sha256:95983b6a230f17147913be88b58362c7bbe0e63229f937cf44e94c88e3dfdc90", ("(A) 19/10", "(B) 1999/1000", "(C) 2", "(D) 1/9"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf", 4, 3, 0, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(C)"),
    "ncert-exemplar-g9-math-u01-q10": ("Unit 1 Ex 1.1 Q10", "sha256:d537ab861909252a8d6bb2b9ab4d11005a57e5cca8bd206e3354ce1d1211d044", ("(A) 2√6", "(B) 6", "(C) 3√3", "(D) 4√6"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf", 4, 3, 0, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(C)"),
    "ncert-exemplar-g9-math-u02-q07": ("Unit 2 Ex 2.1 Q7", "sha256:a086cd2210982163be7dfbdad7fc9cfa1c9ce00ff867163a6b315519ea65bb9a", ("(A) 3", "(B) 2x", "(C) 0", "(D) 6"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf", 15, 2, 3, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(D)"),
    "ncert-exemplar-g9-math-u02-q08": ("Unit 2 Ex 2.1 Q8", "sha256:b5938b0629df8a8997e888b2d33677048dd9800d29fe6b23b2b93ccc41637dbc", ("(A) 0", "(B) 1", "(C) Any real number", "(D) Not defined"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf", 15, 2, 3, "VISUAL_MATCH", "(C)"),
    "ncert-exemplar-g9-math-u02-q09": ("Unit 2 Ex 2.1 Q9", "sha256:a14fd2d6137b869c653f9eeb158eb14a41b894a6e1b113918623aab13326efc9", ("(A) -2/5", "(B) -5/2", "(C) 2/5", "(D) 5/2"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf", 15, 2, 3, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(B)"),
    "ncert-exemplar-g9-math-u02-q10": ("Unit 2 Ex 2.1 Q10", "sha256:f7f2590fcb64a90fe599a3c5112137d435e48036f44a182efd1ead40197640f4", ("(A) 2", "(B) 1/2", "(C) -1/2", "(D) -2"), "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep202.pdf", 15, 2, 3, "VISUAL_MATCH_WITH_NOTATION_NORMALIZATION", "(B)"),
}


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
            # This file is an immutable earlier observation. A later, independently
            # authenticated custody overlay may promote a previously reviewed ID,
            # but this historical review still must not do the promoting.
            if (record.get("projection_disposition") != "EVIDENCE_PENDING"
                    or record.get("source_custody_promoted") is not False):
                raise ValueError(f"{where}: review cannot grant source readiness for {qid}")
            if record.get("comparison_status") not in STATES:
                raise ValueError(f"{where}: unknown review comparison result for {qid}")
            if (qid == "ncert-exemplar-g9-math-u01-q07"
                    and record["comparison_status"] != "SOURCE_NOTATION_DISCREPANCY"):
                raise ValueError(f"{where}: known overbar transcription discrepancy cannot be silently cleared")
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
            # Existing observations are source-located snapshots, not editable
            # declarations. Numeric coordinates must match the inspected record.
            observed = FROZEN_R4_PRIMARY_OBSERVATIONS.get(qid)
            reported = (record["original_identifier"], digest,
                        tuple(record["captured_options"]), url,
                        loc["printed_page"], loc["pdf_page_index"],
                        record["official_answer_pdf_page_index"],
                        record["comparison_status"], key)
            if observed is None or reported != observed:
                raise ValueError(f"{where}: frozen primary-source observation scope mismatch for {qid}")
            reviewed[qid] = record
    return {"reviewed": len(reviewed), "review_ids": sorted(reviewed),
            "notation_discrepancies": sorted(qid for qid, r in reviewed.items()
                                            if r["comparison_status"] == "SOURCE_NOTATION_DISCREPANCY"),
            "custody_promotions": 0,
            "separately_custody_ready": sorted(set(reviewed) & current_ready)}


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
