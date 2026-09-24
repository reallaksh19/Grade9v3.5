#!/usr/bin/env python3
"""Audit Core2 -> Core2A -> Core2B progression at question-family level.

The three products have different ownership:
- Core2 proves source assessment demand.
- Core2A teaches a familiar application and may be AUTHORED.
- Core2B changes the demand relative to a familiar exposure.

This module joins those facts for review. It never copies competitive-bank questions into
ordinary library packages and never treats renderability as academic/progression acceptance.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.library import source_custody  # noqa: E402
from Shared.tools import core2a_inventory, core2b_inventory  # noqa: E402

BANK_ACCEPTED = {"PYQ_VERIFIED", "PYQ_ADAPTED"}
DEFAULT_REPORT = REPO / "docs/core-progression-report.json"


def subjects(repo: Path = REPO) -> list[Path]:
    return sorted(path.parent.parent for path in repo.glob("*/adapter/CoreContracts.json"))


def ordinary_package_paths(subject: Path) -> list[Path]:
    return sorted((subject / "library").glob("*.json"))


def ordinary_records(subject: Path) -> dict:
    paths = ordinary_package_paths(subject)
    return build_index(load_packages(paths)) if paths else {}


def bank_paths(subject: Path) -> list[Path]:
    return sorted((subject / "library" / "exam-bank").glob("*.json"))


def bank_anchors(subject: Path) -> list[dict]:
    rows = []
    for path in bank_paths(subject):
        try:
            bank = load(path)
        except Exception:
            continue
        if not isinstance(bank, dict):
            continue
        bank_id = bank.get("bank_id") or str(path.relative_to(subject.parent))
        for question in bank.get("questions", []) or []:
            if not isinstance(question, dict):
                continue
            provenance = question.get("provenance_status")
            family_ref = question.get("family_ref")
            if provenance not in BANK_ACCEPTED or not family_ref:
                continue
            rows.append({
                "kind": "COMPETITIVE_BANK_VERIFIED_DEMAND",
                "subject": subject.name,
                "family_ref": family_ref,
                "question_id": question.get("id"),
                "bank_id": bank_id,
                "bank_status": bank.get("status"),
                "provenance_status": provenance,
                "primary_capability_ref": question.get("primary_capability_ref"),
                "concept_bucket": question.get("concept_bucket"),
                "package_path": str(path.relative_to(subject.parent)),
            })
    return rows


def _has_core(question: dict, core: str) -> bool:
    return any(
        isinstance(row, dict) and row.get("core") == core
        for row in question.get("exposure", [])
    )


def _ordinary_core2_anchors(records: dict) -> list[dict]:
    rows = []
    for question in records.values():
        if question.get("_collection") != "questions":
            continue
        family_ref = question.get("family_ref")
        if not family_ref:
            continue
        if question.get("status") not in {"REVIEWED", "CURATED"}:
            continue
        if not source_custody.valid_for_core2(question, records):
            continue
        rows.append({
            "kind": "ORDINARY_CORE2_CUSTODY",
            "family_ref": family_ref,
            "question_id": question.get("id"),
            "question_status": question.get("status"),
            "primary_capability_ref": question.get("primary_capability_ref"),
        })
    return rows


def _practice_questions(records: dict) -> list[dict]:
    return sorted(
        [
            row for row in records.values()
            if row.get("_collection") == "questions"
            and (_has_core(row, "CORE2A") or _has_core(row, "CORE2B"))
        ],
        key=lambda row: row["id"],
    )


def _family_ids(records: dict) -> set[str]:
    return {
        q.get("family_ref")
        for q in _practice_questions(records)
        if q.get("family_ref")
    }


def _b_pair_findings(question: dict, records: dict) -> list[dict]:
    found = []
    qid = question.get("id", "")
    adaptation = question.get("adaptation")
    adaptation = adaptation if isinstance(adaptation, dict) else {}
    parent_ref = adaptation.get("parent_ref")
    parent = records.get(parent_ref) if parent_ref else None

    def fail(point: str, detail: str) -> None:
        found.append({"point": point, "where": qid, "detail": detail})

    if not parent or parent.get("_collection") != "questions":
        fail(
            "CORE_PROGRESSION_TRANSFER_PARENT_MISSING",
            "Core2B question has no concrete canonical question parent",
        )
        return found
    if not _has_core(parent, "CORE2A"):
        fail(
            "CORE_PROGRESSION_TRANSFER_PARENT_NOT_CORE2A",
            f"{parent_ref} is not a familiar Core2A exposure",
        )
    if parent.get("family_ref") != question.get("family_ref"):
        fail(
            "CORE_PROGRESSION_TRANSFER_FAMILY_CHANGED",
            f"{parent_ref} family {parent.get('family_ref')} != {question.get('family_ref')}",
        )
    # Whether the adaptation parent is also named in transfer.builds_on is owned by the
    # Phase-3 transfer-migration audit. Existing Phase-3 debt remains a visible family
    # gap below; Phase 4 hard-fails only a broken familiar parent or family identity.
    return found


def family_rows(subject: Path, records: dict, banks: list[dict]) -> tuple[list[dict], list[dict]]:
    step_ids = core2b_inventory._step_ids(records)
    ordinary_source = _ordinary_core2_anchors(records)
    findings: list[dict] = []
    rows = []

    questions = _practice_questions(records)
    for question in questions:
        if _has_core(question, "CORE2B"):
            findings.extend(_b_pair_findings(question, records))

    for family_ref in sorted(_family_ids(records)):
        a = [q for q in questions if q.get("family_ref") == family_ref and _has_core(q, "CORE2A")]
        b = [q for q in questions if q.get("family_ref") == family_ref and _has_core(q, "CORE2B")]
        ordinary = [x for x in ordinary_source if x["family_ref"] == family_ref]
        bank = [x for x in banks if x["family_ref"] == family_ref]

        a_structured = [
            q["id"] for q in a if core2a_inventory.classify(q)["state"] == "STRUCTURED"
        ]
        b_maturity = {
            q["id"]: core2b_inventory.classify(q, records, step_ids)
            for q in b
        }
        b_protected = [
            qid for qid, maturity in b_maturity.items()
            if maturity["protection_state"] == "STRUCTURED_PROTECTED"
        ]

        source_anchors = ordinary + bank
        if ordinary:
            evidence_state = "ORDINARY_CORE2_CUSTODY"
        elif bank:
            evidence_state = "COMPETITIVE_BANK_VERIFIED_DEMAND"
        else:
            evidence_state = "SOURCE_DEMAND_NOT_YET_EVIDENCED"

        gaps = []
        if not source_anchors:
            gaps.append("SOURCE_DEMAND_NOT_YET_EVIDENCED")
        if not a:
            gaps.append("CORE2A_FAMILIAR_MISSING")
        elif len(a_structured) < len(a):
            gaps.append("CORE2A_STRUCTURED_MIGRATION")
        if b and len(b_protected) < len(b):
            gaps.append("CORE2B_PROTECTED_MIGRATION")
        if any(
            "ADAPTATION_PARENT_NOT_IN_LINEAGE" in maturity["debt_reasons"]
            for maturity in b_maturity.values()
        ):
            gaps.append("CORE2B_PARENT_LINEAGE_MIGRATION")
        if any(
            "TRANSFER_REQUIRES_UNESTABLISHED_CAPABILITY" in maturity["debt_reasons"]
            for maturity in b_maturity.values()
        ):
            gaps.append("CORE2B_CAPABILITY_CONTINUITY_MIGRATION")

        rows.append({
            "subject": subject.name,
            "family_ref": family_ref,
            "source_demand_state": evidence_state,
            "source_demand_evidenced": bool(source_anchors),
            "source_anchors": source_anchors,
            "core2a_question_refs": [q["id"] for q in a],
            "core2a_structured_refs": a_structured,
            "core2b_question_refs": [q["id"] for q in b],
            "core2b_protected_refs": b_protected,
            "gaps": gaps,
        })
    return rows, findings


def audit(repo: Path = REPO) -> dict:
    rows = []
    findings = []
    bank_anchor_count = 0
    ordinary_anchor_count = 0

    for subject in subjects(repo):
        try:
            records = ordinary_records(subject)
        except Exception as exc:
            findings.append({
                "point": "CORE_PROGRESSION_LIBRARY_UNREADABLE",
                "where": subject.name,
                "detail": str(exc),
            })
            continue
        banks = bank_anchors(subject)
        bank_anchor_count += len(banks)
        family, subject_findings = family_rows(subject, records, banks)
        rows.extend(family)
        findings.extend(subject_findings)
        ordinary_anchor_count += sum(
            1
            for row in family
            for anchor in row["source_anchors"]
            if anchor["kind"] == "ORDINARY_CORE2_CUSTODY"
        )

    source_states = Counter(row["source_demand_state"] for row in rows)
    return {
        "schema_version": "1.0.0",
        "summary": {
            "practice_families": len(rows),
            "source_demand_evidenced_families": sum(
                row["source_demand_evidenced"] for row in rows
            ),
            "source_demand_states": dict(sorted(source_states.items())),
            "ordinary_core2_anchors": ordinary_anchor_count,
            "competitive_bank_accepted_anchors_scanned": bank_anchor_count,
            "core2a_questions": sum(len(row["core2a_question_refs"]) for row in rows),
            "core2a_structured": sum(len(row["core2a_structured_refs"]) for row in rows),
            "core2b_questions": sum(len(row["core2b_question_refs"]) for row in rows),
            "core2b_protected": sum(len(row["core2b_protected_refs"]) for row in rows),
        },
        "families": rows,
        "findings": findings,
        "passed": not findings,
        "semantics": {
            "renderability_is_readiness": False,
            "competitive_bank_evidence_is_ordinary_core2_custody": False,
            "source_demand_evidence_statement": (
                "A verified/adapted bank item can evidence real assessment demand for a "
                "family without becoming an ordinary-library Core2 question."
            ),
        },
    }


def report_document(repo: Path = REPO) -> dict:
    """The committed reviewer artifact; identical to the live audit output."""
    return audit(repo)


def report_drift(repo: Path = REPO, path: Path | None = None) -> list[dict]:
    target = path or (repo / DEFAULT_REPORT.relative_to(REPO))
    if not target.is_file():
        return [{
            "point": "CORE_PROGRESSION_REPORT_MISSING",
            "where": str(target),
            "detail": "generate the deterministic family progression report",
        }]
    current = report_document(repo)
    stored = load(target)
    if digest(stored) == digest(current):
        return []
    return [{
        "point": "CORE_PROGRESSION_REPORT_STALE",
        "where": str(target),
        "detail": "committed family progression report differs from the live canonical graph",
    }]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--report", type=Path, default=DEFAULT_REPORT)
    args = parser.parse_args()
    report = report_document(REPO)
    if args.write_report:
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.report.write_text(
            json.dumps(report, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
            newline="\n",
        )
    drift = [] if args.write_report else report_drift(REPO, args.report)
    if args.enforce and drift:
        report = {**report, "findings": report["findings"] + drift, "passed": False}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
