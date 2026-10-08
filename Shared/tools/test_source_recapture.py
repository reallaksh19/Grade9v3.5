"""Validate a NON-AUTHORITATIVE NCERT Q7 math-notation recapture proposal.

The historical eight-row R4 observation stays immutable. This proposal may inform
a later independent custody decision but cannot edit the 210-source bank, reuse the
old academic PASS, or supply READY_FOR_BLUEPRINT authority.
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

from Shared.tools import test_intake_registry, test_source_review, test_source_custody  # noqa: E402

QID = "ncert-exemplar-g9-math-u01-q07"
PROPOSAL = "TEST/evidence/source-intake/ncert-exemplar-g9-u01-q07.recapture-proposal.v1.json"
REVIEW = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q07-q10.review.v1.json"
QUESTION_PDF = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep201.pdf"
ANSWER_PDF = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/ieep2an.pdf"
# These strings transcribe *only* the mathematical overbar shapes seen in the
# official printed NCERT page. They are not themselves a new custody witness.
SOURCE_FAITHFUL_TEX_PROPOSAL = (
    "(A) 0.14",
    "(B) 0.14\\overline{16}",
    "(C) 0.\\overline{1416}",
    "(D) 0.4014001400014...",
)


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError("NCERT Q7 recapture proposal: " + message)


def validate(repo: Path = REPO) -> dict:
    proposal = json.loads((repo / PROPOSAL).read_text(encoding="utf-8"))
    review_result = test_source_review.validate(repo)
    historical = json.loads((repo / REVIEW).read_text(encoding="utf-8"))
    prior = next((r for r in historical["records"] if r["source_id"] == QID), None)
    rows = [q for bank in test_intake_registry.load_intake_banks(repo)
            for q in bank["questions"] if q["id"] == QID]
    _require(len(rows) == 1 and prior is not None, "original source/review identity missing")
    source = rows[0]
    _require(review_result["reviewed"] == 8 and
             QID in review_result["notation_discrepancies"],
             "historical eight-row official review or notation discrepancy was rewritten")
    _require(proposal.get("schema_version") == "grade9v3-test-source-recapture-proposal-v1"
             and proposal.get("authority") == "DRAFT_RECAPTURE_PROPOSAL_ONLY",
             "wrong proposal schema or authority")
    _require(proposal.get("source_question_ref") == QID
             and proposal.get("original_identifier") == source["original_identifier"]
             and proposal.get("original_stem") == source["stem"]
             and proposal.get("source_stem_sha256") == source["stem_sha256"]
             and proposal["source_stem_sha256"] == "sha256:" +
                 hashlib.sha256(source["stem"].encode("utf-8")).hexdigest(),
             "unbound source identity, stem or digest")
    _require(proposal.get("original_captured_options") == source["options"]
             == prior["captured_options"],
             "historical captured options were modified or not bound")
    _require(tuple(proposal.get("proposed_tex_options") or ()) == SOURCE_FAITHFUL_TEX_PROPOSAL,
             "proposed overbar notation differs from source-located transcription")
    _require(proposal.get("representation") == "EXPLICIT_LATEX_OVERLINE_NOT_YET_IN_LIVE_BANK"
             and proposal.get("proposed_tex_options") != source["options"],
             "proposed math notation falsely treated as an applied source capture")
    _require(proposal.get("official_question_pdf") == QUESTION_PDF == source["source_url"]
             and proposal.get("source_locator") == prior["source_locator"]
             and proposal.get("official_answer_pdf") == ANSWER_PDF == prior["official_answer_document_url"]
             and proposal.get("official_answer_pdf_page_index") == 0
             and prior["official_answer_pdf_page_index"] == 0,
             "official NCERT question/answer PDF or printed/PDF locator mismatch")
    _require(proposal.get("official_answer_key") == "(D)"
             == prior["official_answer_key"]
             and source["official_answer_text"] == SOURCE_FAITHFUL_TEX_PROPOSAL[3],
             "original answer key/captured option mismatch")
    _require(proposal.get("historical_review_ref") == REVIEW
             and proposal.get("historical_review_status") == "SOURCE_NOTATION_DISCREPANCY",
             "historical non-authoritative review reference changed")
    _require(all(proposal.get(field) is False for field in
                 ("proposed_record_change_applied", "source_custody_promoted",
                  "academic_status_promoted", "publication_authorized")),
             "proposal cannot claim applied source correction, custody or acceptance")
    _require(source["workflow_status"] == "EVIDENCE_PENDING"
             and source["text_verification_status"] == "CAPTURED_UNVERIFIED",
             "live Q7 intake must remain capture-only pending independent verification")
    custody = test_source_custody.reconcile(repo)
    _require(QID not in custody["ready_ids"],
             "draft recapture proposal must be explicitly superseded before READY")
    return {"source_id": QID, "recapture_proposals": 1, "ready_granted": 0,
            "historical_review_rows": review_result["reviewed"],
            "original_stem_sha256": source["stem_sha256"],
            "official_answer_key": "(D)"}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args(argv)
    report = validate(args.repo)
    print("NCERT Q7 notation recapture proposal PASS: 1 source-bound candidate; "
          f"{report['historical_review_rows']} historical review rows intact; "
          "0 custody/academic/promotional authority granted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
