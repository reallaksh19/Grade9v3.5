#!/usr/bin/env python3
"""Reconcile independent Stage-1 source custody evidence onto existing TEST IDs.

This is source custody only. It never establishes academic validation,
canonical admission, curriculum acceptance, or a publication decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry  # noqa: E402

SCHEMA = "grade9v3-test-source-custody-overlay-v1"
def _require(condition: bool, where: str, reason: str) -> None:
    if not condition:
        raise ValueError(f"{where}: {reason}")


def _evidence_ref(value: object) -> bool:
    # A durable pointer shape, not proof that GitHub has verified the claim.
    return isinstance(value, str) and re.fullmatch(
        r"github:reallaksh19/Grade9v3\.5#[1-9][0-9]*:[1-9][0-9]*", value
    ) is not None


def reconcile(repo: Path) -> dict:
    """Return a fail-closed, deterministic evidence view; never mutate intake records."""
    banks = test_intake_registry.load_intake_banks(repo)
    by_id = {q["id"]: (bank, q) for bank in banks for q in bank["questions"]}
    reconciled: dict[str, dict] = {}
    source_holds: dict[str, dict] = {}
    evidence_dir = repo / "TEST/evidence/source-intake"
    for path in sorted(evidence_dir.glob("*.custody.v1.json")):
        try:
            overlay = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError, json.JSONDecodeError) as exc:
            raise ValueError(f"{path}: invalid custody evidence: {exc}") from exc
        where = str(path)
        _require(isinstance(overlay, dict) and overlay.get("schema_version") == SCHEMA,
                 where, "unsupported custody evidence schema")
        _require(isinstance(overlay.get("source_bank_ref"), str), where, "missing bank reference")
        _require(isinstance(overlay.get("documents"), list), where, "documents must be a list")
        _require(isinstance(overlay.get("records"), list), where, "records must be a list")
        documents: dict[str, dict] = {}
        for document in overlay["documents"]:
            _require(isinstance(document, dict), where, "invalid document")
            name = document.get("id")
            _require(isinstance(name, str) and name and name not in documents,
                     where, "missing or duplicate document id")
            authority = document.get("authority")
            _require(test_intake_registry.official_source_url(document.get("url"), authority), where, "unofficial document URL")
            _require(document.get("role") in {"QUESTION_SOURCE", "ANSWER_KEY"}, where, "invalid document role")
            _require(_evidence_ref(document.get("verification_evidence_ref")), where, "missing source document witness")
            documents[name] = document
        for record in overlay["records"]:
            _require(isinstance(record, dict), where, "invalid evidence record")
            qid = record.get("id")
            _require(isinstance(qid, str) and qid in by_id, where, f"orphan source identity {qid!r}")
            _require(qid not in reconciled, where, f"duplicate custody evidence for {qid}")
            bank, source = by_id[qid]
            _require(overlay["source_bank_ref"] == f"TEST/question-bank/intake/{bank['bank_id']}.json",
                     where, f"bank identity mismatch for {qid}")
            origin = documents.get(record.get("source_document_ref"))
            _require(origin is not None and origin["role"] == "QUESTION_SOURCE",
                     where, f"missing question-source document for {qid}")
            _require(origin["authority"] == source["source_authority"]
                     and origin["kind"] == source["source_kind"]
                     and origin["url"] == source["source_url"],
                     where, f"official source identity mismatch for {qid}")
            digest = "sha256:" + hashlib.sha256(source["stem"].encode("utf-8")).hexdigest()
            _require(record.get("stem_sha256") == source["stem_sha256"] == digest,
                     where, f"stem digest mismatch for {qid}")
            _require(record.get("original_identifier") == source["original_identifier"]
                     and record.get("options") == source.get("options", []),
                     where, f"question identifier/options mismatch for {qid}")
            locator = record.get("source_locator") or {}
            _require(isinstance(locator, dict), where, f"invalid locator for {qid}")
            _require(all(locator.get(key) == source[key] for key in
                         ("chapter_or_unit", "exercise_or_section", "question_number")),
                     where, f"source exercise/number mismatch for {qid}")
            _require(type(locator.get("printed_page")) is int
                     and locator["printed_page"] > 0
                     and type(locator.get("pdf_page_index")) is int
                     and locator["pdf_page_index"] >= 0,
                     where, f"missing independently checked PDF/printed page for {qid}")
            _require(record.get("source_verification_status") == "SOURCE_VERIFIED_OFFICIAL"
                     and record.get("text_verification_status") == "TEXT_VERIFIED_AGAINST_OFFICIAL"
                     and _evidence_ref(record.get("verification_evidence_ref")),
                     where, f"independent source/text evidence missing for {qid}")
            _require(record.get("workflow_status") == "READY_FOR_BLUEPRINT",
                     where, f"unsupported READY claim for {qid}")
            key = record.get("official_answer") or {}
            _require(isinstance(key, dict), where, f"invalid answer custody for {qid}")
            key_doc = documents.get(key.get("document_ref"))
            _require(key_doc is not None and key_doc["role"] == "ANSWER_KEY"
                     and key_doc["authority"] == origin["authority"]
                     and key_doc["url"] != origin["url"]
                     and _evidence_ref(key.get("verification_evidence_ref")),
                     where, f"missing independent official answer-key witness for {qid}")
            _require(key.get("exercise_or_section") == source["exercise_or_section"]
                     and key.get("question_number") == source["question_number"],
                     where, f"answer-key locator mismatch for {qid}")
            answer_key = key.get("answer_key")
            _require(source.get("official_answer_available") is True
                     and isinstance(answer_key, str) and bool(answer_key.strip())
                     and source.get("official_answer_text", "").startswith(answer_key),
                     where, f"official answer differs from source record for {qid}")
            if source.get("question_type") == "MULTIPLE_CHOICE":
                _require(bool(re.fullmatch(r"\([A-Za-z]\)", answer_key))
                         and any(isinstance(option, str) and option.startswith(answer_key)
                                 for option in source.get("options", [])),
                         where, f"official answer differs from source record for {qid}")
            reconciled[qid] = {
                "intake_question_ref": qid,
                "source_identity": {"authority": origin["authority"], "kind": origin["kind"],
                                    "document_url": origin["url"], "document_title": origin["title"]},
                "source_locator": locator,
                "stem": source["stem"],
                "stem_sha256": digest,
                "options": source.get("options", []),
                "subject": source["subject"], "grade": source["grade"],
                "topic_label": source["topic_label"], "subtopic_label": source.get("subtopic_label"),
                "question_type": source["question_type"],
                "official_answer_key_ref": {"document_url": key_doc["url"],
                                            "exercise_or_section": key["exercise_or_section"],
                                            "question_number": key["question_number"],
                                            "answer_key": key["answer_key"]},
                "verification_evidence_ref": record["verification_evidence_ref"],
                "intake_status": "READY_FOR_BLUEPRINT",
            }
        hold_rows = overlay.get("holds", [])
        _require(isinstance(hold_rows, list), where, "source-text holds must be a list")
        for hold in hold_rows:
            _require(isinstance(hold, dict), where, "invalid source-text hold")
            qid = hold.get("id")
            _require(isinstance(qid, str) and qid in by_id, where, f"orphan source-text hold {qid!r}")
            _require(qid not in reconciled and qid not in source_holds, where, f"duplicate or READY source-text hold {qid}")
            bank, source = by_id[qid]
            _require(overlay["source_bank_ref"] == f"TEST/question-bank/intake/{bank['bank_id']}.json",
                     where, f"bank identity mismatch for held {qid}")
            origin = documents.get(hold.get("source_document_ref"))
            _require(origin is not None and origin["role"] == "QUESTION_SOURCE"
                     and origin["authority"] == source["source_authority"]
                     and origin["kind"] == source["source_kind"]
                     and origin["url"] == source["source_url"], where, f"held official source mismatch for {qid}")
            loc = hold.get("source_locator")
            _require(isinstance(loc, dict)
                     and all(loc.get(k) == source[k] for k in
                             ("chapter_or_unit", "exercise_or_section", "question_number"))
                     and type(loc.get("printed_page")) is int and loc["printed_page"] > 0
                     and type(loc.get("pdf_page_index")) is int and loc["pdf_page_index"] >= 0,
                     where, f"invalid held source locator for {qid}")
            _require(hold.get("disposition") == "SOURCE_TEXT_HOLD"
                     and hold.get("reason_code") == "VERBATIM_SOURCE_TEXT_MISMATCH"
                     and hold.get("captured_stem") == source["stem"]
                     and hold.get("captured_stem_sha256") == source["stem_sha256"]
                     and isinstance(hold.get("official_stem"), str)
                     and bool(hold["official_stem"].strip()) and hold["official_stem"] != source["stem"]
                     and _evidence_ref(hold.get("verification_evidence_ref")),
                     where, f"invalid disputed official wording for {qid}")
            source_holds[qid] = {"id": qid, "reason": hold["reason_code"],
                                 "official_stem": hold["official_stem"],
                                 "verification_evidence_ref": hold["verification_evidence_ref"]}
    return {
        "schema_version": "grade9v3-test-source-custody-reconciliation-v1",
        "total_intake": len(by_id),
        "ready_for_blueprint": len(reconciled),
        "evidence_pending": len(by_id) - len(reconciled) - len(source_holds),
        "source_text_hold": len(source_holds),
        "ready_ids": sorted(reconciled),
        "hold_ids": sorted(source_holds),
        "held": [source_holds[qid] for qid in sorted(source_holds)],
        "pending_ids": sorted(set(by_id) - set(reconciled) - set(source_holds)),
        "handoff": [reconciled[qid] for qid in sorted(reconciled)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[2])
    parser.add_argument("--handoff", action="store_true", help="print machine-readable verified-only handoff")
    args = parser.parse_args(argv)
    result = reconcile(args.repo)
    if args.handoff:
        print(json.dumps(result["handoff"], sort_keys=True, ensure_ascii=False, indent=2))
    else:
        print(f"Stage-1 custody: {result['ready_for_blueprint']} READY_FOR_BLUEPRINT; "
              f"{result['source_text_hold']} SOURCE_TEXT_HOLD; "
          f"{result['evidence_pending']} EVIDENCE_PENDING; "
              "no academic, production or owner acceptance implied")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
