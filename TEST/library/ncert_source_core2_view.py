#!/usr/bin/env python3
"""Fail-closed NCERT Q1 -> TEST-only Core2 *render view*; not another intake bank.

Use this source-derived adapter before render_core/deploy_test. The source
question, options, original identifier and digest always come from the
authoritative 210-record intake. Candidate educational content is separate.
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import test_intake_registry, test_source_custody  # noqa: E402

AUTHOR = "TEST/library/ncert-u01-q01.core2-authoring.v1.json"
OUTPUT = "TEST/library/ncert-u01-q01.core2-source-view.v1.json"
SOURCE = "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
SCHEMA = "grade9v3-test-core2-source-view-v1"


def build(repo: Path) -> dict:
    authored = json.loads((repo / AUTHOR).read_text(encoding="utf-8"))
    if authored.get("schema_version") != "grade9v3-test-core2-authored-spec-v1":
        raise ValueError("NCERT Q1 authoring spec schema mismatch")
    qid = authored["source_question_ref"]
    banks = test_intake_registry.load_intake_banks(repo)
    matches = [(bank, row) for bank in banks for row in bank["questions"] if row["id"] == qid]
    if len(matches) != 1:
        raise ValueError("NCERT Q1 source ID missing or duplicated")
    bank, source = matches[0]
    if bank["bank_id"] != "ncert-cbse-math-g9-pilot":
        raise ValueError("NCERT Q1 moved outside approved 210-record bank")
    if (source["stem_sha256"] != authored["expected_stem_sha256"]
            or source["id"] != "ncert-exemplar-g9-math-u01-q01"):
        raise ValueError("NCERT Q1 source stem digest changed; authoring requires revalidation")

    custody = test_source_custody.reconcile(repo)
    evidenced = {row["intake_question_ref"]: row for row in custody["handoff"]}
    ready = evidenced.get(qid)
    if qid not in custody["ready_ids"] or ready is None:
        raise ValueError("NCERT Q1 not independently custody READY: refuse product view")
    locator = ready["source_locator"]
    key = ready.get("official_answer_key_ref")
    if not key or key.get("answer_key") != "(C)":
        raise ValueError("NCERT Q1 official answer key not independently evidenced")
    if ready["source_identity"]["document_url"] != source["source_url"]:
        raise ValueError("NCERT source document identity mismatch")

    candidate = copy.deepcopy(authored["render_record_template"])
    if candidate.get("status") != "CANDIDATE":
        raise ValueError("NCERT candidate answer cannot assert publication acceptance")
    answer = candidate.get("answer") or {}
    if (answer.get("verification_status") != "CHECKED_BY_AUTHOR"
            or (answer.get("source_key") or {}).get("value") != source.get("official_answer_text")
            or (answer.get("source_key") or {}).get("value", "")[:3] != key["answer_key"]):
        raise ValueError("NCERT candidate authoring does not match separately witnessed official key")
    if (candidate.get("primary_capability_ref") != "CAP-TEST-NCERT-U01-RATIONAL-REAL-INCLUSION"
            or candidate.get("family_ref") != "FAM-TEST-NCERT-U01-SET-INCLUSION"):
        raise ValueError("NCERT source view references unrelated concept authority")

    candidate["id"] = source["id"]
    candidate["original_identifier"] = source["original_identifier"]
    candidate["stem"] = source["stem"]
    candidate["options"] = copy.deepcopy(source.get("options") or [])
    ext = candidate.setdefault("extensions", {})
    ext["grade9v3:ncert_source_lineage"] = {
        "source_id": source["id"],
        "stem_sha256": source["stem_sha256"],
        "original_identifier": source["original_identifier"],
        "source_url": source["source_url"],
        "source_authority": source["source_authority"],
        "source_document_role": source["source_kind"],
        "verified_printed_page": locator["printed_page"],
        "verified_pdf_page_index": locator["pdf_page_index"],
        "source_custody_status": "READY_FOR_BLUEPRINT",
        "separate_official_answer_key": key["answer_key"],
        "answer_source_url": key["document_url"],
        "academic_status_not_granted_by_view": True,
    }
    # The existing renderer's legacy PYQ-only badge does NOT understand NCERT
    # custody yet. Keep the NCERT authority class explicit; never forge PYQ.
    ext["grade9v3:source_custody"] = {
        "authority_class": "NCERT_OFFICIAL_EXEMPLAR",
        "intake_ref": source["id"],
        "wording_custody": "TEXT_VERIFIED_AGAINST_OFFICIAL",
        "text_sha256": source["stem_sha256"],
        "source_status": "READY_FOR_BLUEPRINT",
        "paper_url": source["source_url"],
    }
    # Preserve source-lineage disclosures before authored topic classification.
    candidate["extensions"] = {
        "grade9v3:ncert_source_lineage": ext["grade9v3:ncert_source_lineage"],
        "grade9v3:source_custody": ext["grade9v3:source_custody"],
        **{k: v for k, v in ext.items()
           if k not in {"grade9v3:ncert_source_lineage", "grade9v3:source_custody"}},
    }
    return {
        "schema_version": SCHEMA,
        "authority_note": ("TEST-only derived product view, never a source intake bank or "
                           "curriculum/canonical acceptance. Rebuild using "
                           "TEST/library/ncert_source_core2_view.py --check."),
        "source_bank_ref": SOURCE,
        "source_question_ref": source["id"],
        "source_stem_sha256": source["stem_sha256"],
        "questions": [candidate],
    }


def generated_bytes(repo: Path) -> str:
    return json.dumps(build(repo), indent=2, ensure_ascii=False) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    expected = generated_bytes(args.repo)
    path = args.repo / OUTPUT
    if args.check:
        if not path.is_file() or path.read_text(encoding="utf-8") != expected:
            print(f"STALE NCERT Core2 view: {path}", file=sys.stderr)
            return 1
        print("PASS: source-bound NCERT Q1 Core2 product view is fresh and nonaccepted")
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(expected, encoding="utf-8")
        print(f"Rebuilt {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
