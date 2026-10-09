#!/usr/bin/env python3
"""#132: read-only source-record-to-canonical Q1 migration assessment.

Produces an audit/decision *candidate*, never an acceptance receipt or a
canonical Question Bank, Atlas, search or Pages publication.
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

SCHEMA = "grade9v3-test-canonical-q1-handoff-dry-run-v1"
SOURCE_ID = "ncert-exemplar-g9-math-u02-q01"
CANONICAL_ID = "Q-MAT-POLY-NCERT9-EX21-Q01"
BANK = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
RECEIPT = "TEST/candidates/ncert-exemplar-g9-math-u02-q01-q10.validation.json"
PACKAGE = "Mathematics/library/polynomials.v1.json"
DISPOSITIONS = frozenset({"ACCEPTED", "DEFERRED", "REJECTED"})

# An ordered plan for a *separately authorised* future scratch run; no stage
# invokes any of these producers. Source-to-canonical mapping is not an HTML copy.
PRODUCER_SEQUENCE = (
    "Shared/tools/build_question_bank_web.py",
    "Shared/tools/build_question_bank_platform.py",
    "Shared/tools/build_web_data.py",
    "Shared/tools/build_learner_search_index.py",
    "Shared/tools/build_pages_site.py",
)


def _require(ok: bool, message: str) -> None:
    if not ok:
        raise ValueError(message)


def _load(repo: Path, relative: str) -> dict:
    path = repo / relative
    result = json.loads(path.read_text(encoding="utf-8"))
    _require(isinstance(result, dict), f"{relative}: expected JSON object")
    return result


def _one(rows: list[dict], ident: str, key: str, description: str) -> dict:
    matches = [row for row in rows if isinstance(row, dict) and row.get(key) == ident]
    _require(len(matches) == 1, f"{description}: expected exactly one {ident}, found {len(matches)}")
    return matches[0]


def _text_digest(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def _candidate_digest(fields: dict) -> str:
    encoded = json.dumps(fields, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    return "sha256:" + hashlib.sha256(encoded.encode("utf-8")).hexdigest()


def assess(repo: Path = REPO) -> dict:
    """Reconcile immutable source/receipt versions. Never create or modify files."""
    banks = test_intake_registry.load_intake_banks(repo)
    _require(len(banks) == 1 and banks[0]["bank_id"] == Path(BANK).stem,
             "ambiguous or missing official source bank")
    source = _one(banks[0]["questions"], SOURCE_ID, "id", "official source")
    custody = test_source_custody.reconcile(repo)
    ready = _one(custody["handoff"], SOURCE_ID, "intake_question_ref", "source custody")
    _require(SOURCE_ID not in custody["hold_ids"], "Q1 still held")
    _require(ready["intake_status"] == "READY_FOR_BLUEPRINT"
             and ready["stem_sha256"] == source["stem_sha256"]
             and ready["stem"] == source["stem"]
             and _text_digest(source["stem"]) == source["stem_sha256"],
             "official source stem/verified digest mismatch")
    _require(ready["official_answer_custody"] == "INDEPENDENTLY_EVIDENCED"
             and ready["official_answer_key_ref"]["answer_key"] == "(C)"
             and source["official_answer_text"].startswith("(C)")
             and ready["source_locator"]["printed_page"] == 14
             and ready["source_locator"]["pdf_page_index"] == 1,
             "Q1 official source, locator or answer custody missing")

    receipt = _one(_load(repo, RECEIPT)["records"], SOURCE_ID, "source_id",
                   "historical academic receipt")
    package = _load(repo, PACKAGE)
    canonical = _one(package["questions"], CANONICAL_ID, "id", "canonical record")
    extensions = canonical.get("extensions") or {}
    lineage = extensions.get("grade9v3:lineage") or {}
    provenance = extensions.get("grade9v3:source_custody") or {}
    canonical_digest = _text_digest(canonical["stem"])
    previous_digest = receipt.get("stem_sha256")
    _require(lineage.get("source_question_id") == SOURCE_ID
             and lineage.get("source_bank_ref") == BANK
             and lineage.get("validation_ref") == RECEIPT
             and lineage.get("source_text_sha256") == previous_digest
             and provenance.get("text_sha256") == previous_digest
             and previous_digest == canonical_digest,
             "historical canonical/academic lineage digest does not reconcile")
    _require(receipt["original_identifier"] == source["original_identifier"]
             and canonical["original_identifier"] == source["original_identifier"]
             and canonical["options"] == source["options"]
             and canonical["answer"]["summary"] == source["official_answer_text"],
             "source-to-canonical identifier/options/answer conflict")
    _require(receipt["academic_validation"]["status"] == "PASS"
             and receipt["academic_validation"]["admission_eligible"] is True
             and canonical["status"] == "REVIEWED"
             and extensions.get("grade9v3:question_bank", {}).get("include") is True,
             "historical admission state inconsistent")
    _require(previous_digest != source["stem_sha256"],
             "Q1 is no longer the disputed source-version migration; reassess scope")

    candidate = {
        "canonical_question_id": CANONICAL_ID,
        "original_identifier": source["original_identifier"],
        "stem": source["stem"],
        "options": source["options"],
        "official_answer_summary": source["official_answer_text"],
        "question_source_url": ready["source_identity"]["document_url"],
        "answer_source_url": ready["official_answer_key_ref"]["document_url"],
    }
    _require(all("public/test/" not in str(value) and "docs/test/" not in str(value)
                 for value in candidate.values()), "TEST-rendered artifact leaked into mapping")
    return {
        "schema_version": SCHEMA,
        "scope": "NCERT_POLYNOMIALS_EX21_Q1_SOURCE_VERSION_ONLY",
        "disposition": "DEFERRED",
        "reason_codes": [
            "CURRENT_ACADEMIC_RECEIPT_ABSENT",
            "CANONICAL_RECORD_BINDS_SUPERSEDED_SOURCE_DIGEST",
            "OWNER_CANONICAL_DECISION_ABSENT",
        ],
        "source": {
            "source_id": SOURCE_ID,
            "source_digest": source["stem_sha256"],
            "verification_witness": ready["verification_evidence_ref"],
            "source_readiness": ready["intake_status"],
            "academic_receipt_for_current_digest": None,
        },
        "historical_canonical": {
            "id": CANONICAL_ID,
            "stem_sha256": canonical_digest,
            "historical_receipt_digest": previous_digest,
            "already_included_in_production": True,
            "currently_aligned_to_official_source": False,
        },
        "candidate": candidate,
        "candidate_digest": _candidate_digest(candidate),
        "authority": {
            "technical_source_custody": "SOURCE_EVIDENCED",
            "independent_academic_review_for_candidate": "MISSING",
            "owner_promotion_authorization": "ABSENT",
        },
        "regeneration": {
            "mode": "PLAN_ONLY_NOT_EXECUTED",
            "producer_sequence": list(PRODUCER_SEQUENCE),
            "scratch_confirmation": "NOT_RUN",
            "canonical_writes": False,
            "test_html_as_input": False,
        },
        "effects": {"files_written": [], "published": False, "accepted": False},
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    args = parser.parse_args(argv)
    try:
        result = assess(args.repo)
    except (OSError, UnicodeError, ValueError, TypeError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({
            "schema_version": SCHEMA, "disposition": "REJECTED",
            "reason": str(exc), "effects": {"files_written": [], "published": False, "accepted": False},
        }, ensure_ascii=False, sort_keys=True))
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
