#!/usr/bin/env python3
"""Stage-1 NCERT/CBSE official source question intake tool (GitHub Issue #68).

Manages official question intake for Grade 9 Mathematics (and other sandbox subjects)
under schema 'grade9v3-test-source-question-intake-v1'.

Enforces Stage-1 rules:
- Verifies exact stem digests (sha256);
- Rejects any fabricated difficulty, cognitive demand, QRT cells, or authored worked solutions;
- Preserves official source custody and locators;
- Emits deterministic reports, projection data for TEST UI, and blueprint handoffs.
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

SCHEMA_VERSION = "grade9v3-test-source-question-intake-v1"
SCHEMA_PATH = REPO / "Shared" / "library" / "test-source-question-intake.schema.json"

FORBIDDEN_DEFERRED_FIELDS = (
    "difficulty",
    "band",
    "d_band",
    "derived_d_band",
    "score",
    "qrt_cell",
    "primary_demand",
    "secondary_demand",
    "cognitive_demand",
    "reasoning_route",
    "crux_move",
    "crux_move_ref",
    "scaffolds",
    "hint_ladder",
    "primary_capability_ref",
    "family_ref",
    "misconception",
    "worked_solution",
    "support_eligibility",
)

PERMITTED_AUTHORITIES = {"NCERT_OFFICIAL", "CBSE_OFFICIAL"}
PERMITTED_STATUSES = {
    "CAPTURED", "SOURCE_VERIFIED", "TEXT_VERIFIED", "LABELLED",
    "TEST_VISIBLE", "READY_FOR_BLUEPRINT", "SOURCE_HOLD",
    "TEXT_HOLD", "IDENTITY_HOLD", "DUPLICATE_REVIEW", "TOPIC_HOLD"
}


def text_digest(text: str) -> str:
    """Return the sha256 text digest in canonical format."""
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def load_json(path: Path | str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_schema() -> dict:
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def check(bank_data: dict | Path | str) -> list[str]:
    """Validate a Stage-1 intake bank. Returns list of problem strings."""
    if isinstance(bank_data, (str, Path)):
        bank_path = Path(bank_data)
        if not bank_path.is_file():
            return [f"File not found: {bank_path}"]
        try:
            bank = load_json(bank_path)
        except Exception as exc:
            return [f"Invalid JSON in {bank_path}: {exc}"]
    else:
        bank = bank_data

    problems: list[str] = []

    # 1. Basic schema checks
    if bank.get("schema_version") != SCHEMA_VERSION:
        problems.append(
            f"Expected schema_version {SCHEMA_VERSION!r}, got {bank.get('schema_version')!r}"
        )

    bank_id = bank.get("bank_id", "")
    if not re.match(r"^[a-z0-9][a-z0-9-]{0,63}$", bank_id):
        problems.append(f"Invalid bank_id {bank_id!r}")

    source_scope = set(bank.get("source_scope") or [])
    if not source_scope.issubset(PERMITTED_AUTHORITIES):
        problems.append(f"source_scope contains non-official authority: {source_scope - PERMITTED_AUTHORITIES}")

    questions = bank.get("questions")
    if not isinstance(questions, list):
        return problems + ["questions must be an array"]

    # 2. Try JSON Schema validation if jsonschema is available
    try:
        from jsonschema import Draft202012Validator
        schema = load_schema()
        validator = Draft202012Validator(schema)
        for err in validator.iter_errors(bank):
            problems.append(f"schema: {'/'.join(str(p) for p in err.path)}: {err.message}")
    except ImportError:
        pass

    # 3. Semantic & Custody checks per question
    seen_ids: set[str] = set()
    seen_stems: dict[str, str] = {}
    seen_locators: dict[tuple, str] = {}

    for idx, q in enumerate(questions):
        qid = q.get("id", f"questions[{idx}]")

        # ID uniqueness
        if qid in seen_ids:
            problems.append(f"{qid}: duplicate question ID")
        seen_ids.add(qid)

        # Forbidden academic fields guardrail
        for forbidden in FORBIDDEN_DEFERRED_FIELDS:
            if forbidden in q:
                problems.append(
                    f"{qid}: deferred academic field {forbidden!r} is FORBIDDEN at Stage 1"
                )

        # Stem digest verification
        stem = q.get("stem", "")
        if not stem.strip():
            problems.append(f"{qid}: stem is empty or blank")
        else:
            expected_sha = text_digest(stem)
            actual_sha = q.get("stem_sha256", "")
            if actual_sha != expected_sha:
                problems.append(
                    f"{qid}: stem_sha256 mismatch (recorded: {actual_sha}, computed: {expected_sha})"
                )

        # Duplicate stem check
        stem_hash = q.get("stem_sha256")
        if stem_hash in seen_stems:
            if q.get("workflow_status") != "DUPLICATE_REVIEW":
                problems.append(
                    f"{qid}: duplicate stem matches {seen_stems[stem_hash]} (flag for DUPLICATE_REVIEW)"
                )
        else:
            seen_stems[stem_hash] = qid

        # Duplicate locator check
        locator_key = (
            q.get("source_authority"),
            q.get("source_kind"),
            q.get("document_title"),
            q.get("chapter_or_unit"),
            q.get("exercise_or_section"),
            q.get("question_number")
        )
        if locator_key in seen_locators:
            problems.append(
                f"{qid}: duplicate source locator matches {seen_locators[locator_key]}"
            )
        else:
            seen_locators[locator_key] = qid

        # Source authority in declared scope
        auth = q.get("source_authority")
        if auth and auth not in source_scope:
            problems.append(f"{qid}: source_authority {auth!r} not in declared bank source_scope")

        # Ready for blueprint criteria
        wf_status = q.get("workflow_status")
        text_status = q.get("text_verification_status")
        if wf_status == "READY_FOR_BLUEPRINT":
            if text_status != "TEXT_VERIFIED_AGAINST_OFFICIAL":
                problems.append(
                    f"{qid}: READY_FOR_BLUEPRINT requires text_verification_status "
                    f"'TEXT_VERIFIED_AGAINST_OFFICIAL', got {text_status!r}"
                )
            if not q.get("source_url"):
                problems.append(f"{qid}: READY_FOR_BLUEPRINT requires source_url")

    return problems


def report(bank: dict) -> dict:
    """Generate statistical summary by topic, authority, kind, and status."""
    questions = bank.get("questions", [])
    topics: dict[str, int] = {}
    authorities: dict[str, int] = {}
    kinds: dict[str, int] = {}
    workflow_statuses: dict[str, int] = {}
    text_statuses: dict[str, int] = {}

    for q in questions:
        t = q.get("topic_label", "Unknown")
        topics[t] = topics.get(t, 0) + 1

        a = q.get("source_authority", "Unknown")
        authorities[a] = authorities.get(a, 0) + 1

        k = q.get("source_kind", "Unknown")
        kinds[k] = kinds.get(k, 0) + 1

        ws = q.get("workflow_status", "Unknown")
        workflow_statuses[ws] = workflow_statuses.get(ws, 0) + 1

        ts = q.get("text_verification_status", "Unknown")
        text_statuses[ts] = text_statuses.get(ts, 0) + 1

    return {
        "bank_id": bank.get("bank_id"),
        "total_questions": len(questions),
        "by_topic": topics,
        "by_authority": authorities,
        "by_kind": kinds,
        "by_workflow_status": workflow_statuses,
        "by_text_verification_status": text_statuses,
    }


def handoff(bank: dict) -> list[dict]:
    """Generate minimal immutable handoff list for READY_FOR_BLUEPRINT items."""
    result: list[dict] = []
    for q in bank.get("questions", []):
        if q.get("workflow_status") != "READY_FOR_BLUEPRINT":
            continue
        result.append({
            "intake_question_ref": q["id"],
            "original_identifier": q["original_identifier"],
            "source_identity": {
                "source_authority": q["source_authority"],
                "source_kind": q["source_kind"],
                "document_title": q["document_title"],
                "edition_or_year": q.get("edition_or_year"),
                "source_url": q["source_url"],
                "chapter_or_unit": q["chapter_or_unit"],
                "exercise_or_section": q["exercise_or_section"],
                "question_number": q["question_number"],
                "page": q.get("page"),
            },
            "stem": q["stem"],
            "stem_sha256": q["stem_sha256"],
            "options": q.get("options", []),
            "subparts": q.get("subparts", []),
            "subject": q["subject"],
            "grade": q["grade"],
            "topic_label": q["topic_label"],
            "subtopic_label": q.get("subtopic_label"),
            "question_type": q["question_type"],
            "official_answer_available": q["official_answer_available"],
            "official_answer_key_ref": q.get("answer_key_locator"),
            "official_answer_text": q.get("official_answer_text"),
            "workflow_status": q["workflow_status"],
            "text_verification_status": q["text_verification_status"],
        })
    return result


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Stage-1 NCERT/CBSE question intake tool")
    subparsers = parser.add_subparsers(dest="cmd", required=True)

    check_parser = subparsers.add_parser("check", help="Verify intake bank")
    check_parser.add_argument("bank", type=Path, help="Path to intake JSON bank")

    report_parser = subparsers.add_parser("report", help="Generate summary report")
    report_parser.add_argument("bank", type=Path, help="Path to intake JSON bank")

    handoff_parser = subparsers.add_parser("handoff", help="Export blueprint handoff list")
    handoff_parser.add_argument("bank", type=Path, help="Path to intake JSON bank")
    handoff_parser.add_argument("--out", type=Path, required=True, help="Output JSON path")

    args = parser.parse_args(argv)

    if args.cmd == "check":
        problems = check(args.bank)
        if problems:
            print(f"FAILED with {len(problems)} problem(s):")
            for p in problems:
                print(f"  - {p}")
            return 1
        print("OK: Stage-1 intake bank passes all verification rules.")
        return 0

    if args.cmd == "report":
        data = load_json(args.bank)
        rep = report(data)
        print(f"Bank ID: {rep['bank_id']}")
        print(f"Total questions: {rep['total_questions']}")
        print("\nBy Topic:")
        for t, c in sorted(rep["by_topic"].items()):
            print(f"  - {t}: {c}")
        print("\nBy Authority:")
        for a, c in rep["by_authority"].items():
            print(f"  - {a}: {c}")
        print("\nBy Source Kind:")
        for k, c in rep["by_kind"].items():
            print(f"  - {k}: {c}")
        print("\nBy Workflow Status:")
        for ws, c in rep["by_workflow_status"].items():
            print(f"  - {ws}: {c}")
        print("\nBy Text Verification Status:")
        for ts, c in rep["by_text_verification_status"].items():
            print(f"  - {ts}: {c}")
        return 0

    if args.cmd == "handoff":
        data = load_json(args.bank)
        items = handoff(data)
        args.out.write_text(json.dumps(items, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {len(items)} handoff record(s) to {args.out}")
        return 0

    return 0


if __name__ == "__main__":
    sys.exit(main())
