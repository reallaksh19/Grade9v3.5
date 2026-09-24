#!/usr/bin/env python3
"""Inventory Core2B transfer integrity and prevent new legacy transfer debt.

Core2B is a changed-demand claim relative to prior exposure. Existing items may remain
unchanged while they migrate, but a new or materially revised transfer item must close
its machine-checkable debt: concrete lineage, established capabilities, structured
protected decision, specific repair, and rubric closure.

This tool does not decide whether a transfer statement is pedagogically profound. It
makes the pairwise evidence visible and blocks claims that are mechanically false.
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

DEFAULT_BASELINE = REPO / "docs/core2b-legacy-transfer-baseline.json"
TRANSFER_DIMENSIONS = {
    "model_choice", "representation_translation", "reasoning_steps", "novelty"
}

SEMANTIC_FIELDS = (
    "stem", "subparts", "options", "conditions", "figure_refs",
    "primary_capability_ref", "secondary_capability_refs", "family_ref",
    "hints", "scaffolds", "exposure", "transfer", "repair_ref", "adaptation",
)


def subjects(repo: Path = REPO) -> list[Path]:
    return sorted(path.parent.parent for path in repo.glob("*/adapter/CoreContracts.json"))


def package_paths(subject: Path) -> list[Path]:
    return sorted(path for path in (subject / "library").rglob("*.json")
                  if not path.name.endswith(".schema.json"))


def _core2b(question: dict) -> bool:
    return any(
        isinstance(row, dict) and row.get("core") == "CORE2B"
        for row in question.get("exposure", [])
    )


def _core2a(question: dict) -> bool:
    return any(
        isinstance(row, dict) and row.get("core") == "CORE2A"
        for row in question.get("exposure", [])
    )


def _semantic_digest(question: dict) -> str:
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    payload = {field: question.get(field) for field in SEMANTIC_FIELDS}
    payload["answer"] = {
        field: answer.get(field)
        for field in (
            "kind", "summary", "reasoning", "reasoning_route", "crux_move_ref",
            "difficult_move", "check", "subpart_answers", "rubric",
        )
    }
    return digest(payload)


def _subject_records(subject: Path) -> dict:
    records: dict[str, dict] = {}
    for path in package_paths(subject):
        try:
            package = load(path)
        except Exception:
            continue
        if not isinstance(package, dict):
            continue
        package_id = package.get("package_id") or package.get("manifest_id") or str(path)
        for collection in ("questions", "microtopics", "capabilities"):
            for row in package.get(collection, []) or []:
                if not isinstance(row, dict) or not row.get("id"):
                    continue
                records[row["id"]] = {
                    **row,
                    "_collection": collection,
                    "_package": package_id,
                    "_path": str(path.relative_to(subject.parent)),
                }
    return records


def _step_ids(records: dict) -> set[str]:
    return {
        step.get("id")
        for row in records.values()
        if row.get("_collection") == "microtopics"
        for step in row.get("teaching_path", []) or []
        if isinstance(step, dict) and step.get("id")
    }


def _capability_closure(records: dict, refs: set[str]) -> set[str]:
    found = set(refs)
    pending = list(refs)
    while pending:
        ref = pending.pop()
        row = records.get(ref)
        if not row or row.get("_collection") != "capabilities":
            continue
        for parent in row.get("prerequisite_refs", []) or []:
            if parent not in found:
                found.add(parent)
                pending.append(parent)
    return found


def _capabilities_from_ref(records: dict, ref: str) -> set[str]:
    row = records.get(ref)
    if not row:
        return set()
    if row.get("_collection") == "questions":
        refs = {
            row.get("primary_capability_ref"),
            *(row.get("secondary_capability_refs") or []),
        }
        refs.discard(None)
        return _capability_closure(records, refs)
    if row.get("_collection") == "microtopics":
        ref = row.get("primary_capability_ref")
        return _capability_closure(records, {ref} if ref else set())
    if row.get("_collection") == "capabilities":
        return _capability_closure(records, {row["id"]})
    return set()


def _repair_state(records: dict, step_ids: set[str], repair_ref: str | None) -> str:
    if not repair_ref:
        return "MISSING"
    if repair_ref in step_ids:
        return "SPECIFIC_TEACHING_STEP"
    row = records.get(repair_ref)
    if not row:
        return "UNRESOLVED"
    return f'DECLARED_{str(row.get("_collection") or "RECORD").upper()}_NOT_STEP'


def classify(question: dict, records: dict, step_ids: set[str]) -> dict:
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    transfer = question.get("transfer") if isinstance(question.get("transfer"), dict) else {}
    route = answer.get("reasoning_route")
    route = route if isinstance(route, list) else []
    moves = {
        move.get("id"): move
        for move in route
        if isinstance(move, dict) and move.get("id")
    }
    protected = transfer.get("protected_move_ref")
    protected_move = moves.get(protected)

    if route and protected and protected_move and protected_move.get("kind") == "DECIDE":
        protection_state = "STRUCTURED_PROTECTED"
    elif not route and not protected:
        protection_state = "LEGACY_TRANSFER_PROTECTION_REQUIRED"
    elif protected and protected not in moves:
        protection_state = "INVALID_PROTECTED_MOVE_DANGLING"
    elif protected_move and protected_move.get("kind") != "DECIDE":
        protection_state = "INVALID_PROTECTED_MOVE_NOT_DECIDE"
    else:
        protection_state = "INVALID_PARTIAL_TRANSFER_PROTECTION"

    lineage = list(transfer.get("builds_on") or [])
    unresolved = [ref for ref in lineage if ref not in records]
    adaptation = question.get("adaptation") if isinstance(question.get("adaptation"), dict) else {}
    parent_ref = adaptation.get("parent_ref")
    parent = records.get(parent_ref) if parent_ref else None

    question_anchor = None
    anchor_kind = None
    if parent and parent.get("_collection") == "questions":
        question_anchor = parent
        anchor_kind = "ADAPTATION_PARENT"
    else:
        for ref in lineage:
            candidate = records.get(ref)
            if candidate and candidate.get("_collection") == "questions":
                question_anchor = candidate
                anchor_kind = "QUESTION_LINEAGE"
                break

    microtopic_anchor = None
    if question_anchor is None:
        for ref in lineage:
            candidate = records.get(ref)
            if candidate and candidate.get("_collection") == "microtopics":
                microtopic_anchor = candidate
                anchor_kind = "MICROTOPIC_LINEAGE"
                break

    anchor = question_anchor or microtopic_anchor
    anchor_ref = anchor.get("id") if anchor else None

    established: set[str] = set()
    for ref in lineage:
        established |= _capabilities_from_ref(records, ref)

    required = {
        question.get("primary_capability_ref"),
        *(question.get("secondary_capability_refs") or []),
    }
    required.discard(None)
    missing_capabilities = sorted(required - established)

    repair_state = _repair_state(records, step_ids, question.get("repair_ref"))
    rubric = answer.get("rubric")
    rubric_present = bool(
        isinstance(rubric, list)
        and rubric
        and all(
            isinstance(row, dict)
            and str(row.get("criterion") or "").strip()
            and str(row.get("evidence_of") or "").strip()
            for row in rubric
        )
    )

    debt: list[str] = []
    if protection_state != "STRUCTURED_PROTECTED":
        debt.append("PROTECTED_DECISION_MIGRATION_REQUIRED")
    if not lineage:
        debt.append("TRANSFER_LINEAGE_MISSING")
    if unresolved:
        debt.append("TRANSFER_LINEAGE_UNRESOLVED")
    if parent_ref and parent_ref not in lineage:
        debt.append("ADAPTATION_PARENT_NOT_IN_LINEAGE")
    if question_anchor and not _core2a(question_anchor):
        debt.append("QUESTION_ANCHOR_NOT_FAMILIAR_CORE2A")
    if missing_capabilities:
        debt.append("TRANSFER_REQUIRES_UNESTABLISHED_CAPABILITY")
    if repair_state != "SPECIFIC_TEACHING_STEP":
        debt.append("REPAIR_NOT_SPECIFIC_TEACHING_STEP")
    if not rubric_present:
        debt.append("TRANSFER_RUBRIC_INCOMPLETE")

    return {
        "protection_state": protection_state,
        "reasoning_moves": len(route),
        "protected_move_ref": protected,
        "protected_move_kind": protected_move.get("kind") if protected_move else None,
        "dimension": transfer.get("dimension"),
        "statement_present": bool(str(transfer.get("statement") or "").strip()),
        "lineage": lineage,
        "lineage_unresolved": unresolved,
        "anchor_ref": anchor_ref,
        "anchor_kind": anchor_kind,
        "anchor_is_core2a": bool(question_anchor and _core2a(question_anchor)),
        "anchor_family_ref": question_anchor.get("family_ref") if question_anchor else None,
        "anchor_primary_capability_ref": (
            question_anchor.get("primary_capability_ref") if question_anchor
            else microtopic_anchor.get("primary_capability_ref") if microtopic_anchor else None
        ),
        "same_family_as_question_anchor": (
            question_anchor.get("family_ref") == question.get("family_ref")
            if question_anchor else None
        ),
        "same_primary_as_question_anchor": (
            question_anchor.get("primary_capability_ref") == question.get("primary_capability_ref")
            if question_anchor else None
        ),
        "adaptation_parent_ref": parent_ref,
        "adaptation_changed_fields": list(adaptation.get("changed_fields") or []),
        "required_capabilities": sorted(required),
        "established_capabilities": sorted(established),
        "missing_capabilities": missing_capabilities,
        "repair_ref": question.get("repair_ref"),
        "repair_state": repair_state,
        "rubric_present": rubric_present,
        "hint_reveal_depths": [
            row.get("reveals") for row in question.get("hints", [])
            if isinstance(row, dict)
        ],
        "scaffold_count": len(question.get("scaffolds") or []),
        "debt_reasons": debt,
        "debt_count": len(debt),
    }


def inventory(repo: Path = REPO) -> dict:
    rows: list[dict] = []
    parse_findings: list[dict] = []

    for subject in subjects(repo):
        records = _subject_records(subject)
        step_ids = _step_ids(records)
        for qid, question in sorted(records.items()):
            if question.get("_collection") != "questions" or not _core2b(question):
                continue
            transfer = question.get("transfer") if isinstance(question.get("transfer"), dict) else {}
            if transfer.get("dimension") not in TRANSFER_DIMENSIONS:
                parse_findings.append({
                    "point": "CORE2B_TRANSFER_DIMENSION_INVALID",
                    "where": qid,
                    "detail": str(transfer.get("dimension")),
                })
            rows.append({
                "subject": subject.name,
                "package_path": question.get("_path"),
                "question_id": qid,
                "question_status": question.get("status"),
                "family_ref": question.get("family_ref"),
                "primary_capability_ref": question.get("primary_capability_ref"),
                "semantic_digest": _semantic_digest(question),
                **classify(question, records, step_ids),
            })

    states = Counter(row["protection_state"] for row in rows)
    dimensions = Counter(row["dimension"] for row in rows)
    debt_reasons = Counter(reason for row in rows for reason in row["debt_reasons"])
    subjects_summary = {}
    for subject in sorted({row["subject"] for row in rows}):
        subset = [row for row in rows if row["subject"] == subject]
        subjects_summary[subject] = {
            "core2b_questions": len(subset),
            "structured_protected": sum(
                row["protection_state"] == "STRUCTURED_PROTECTED" for row in subset
            ),
            "debt_items": sum(bool(row["debt_reasons"]) for row in subset),
        }

    return {
        "schema_version": "1.0.0",
        "summary": {
            "core2b_questions": len(rows),
            "structured_protected": states.get("STRUCTURED_PROTECTED", 0),
            "debt_items": sum(bool(row["debt_reasons"]) for row in rows),
            "protection_states": dict(sorted(states.items())),
            "dimensions": dict(sorted((str(k), v) for k, v in dimensions.items())),
            "debt_reasons": dict(sorted(debt_reasons.items())),
            "subjects": subjects_summary,
        },
        "rows": rows,
        "findings": parse_findings,
    }


def baseline_document(report: dict) -> dict:
    items = [{
        "subject": row["subject"],
        "package_path": row["package_path"],
        "question_id": row["question_id"],
        "semantic_digest": row["semantic_digest"],
        "debt_reasons": row["debt_reasons"],
    } for row in report["rows"] if row["debt_reasons"]]
    return {
        "schema_version": "1.0.0",
        "policy": (
            "Existing Core2B debt may remain unchanged while it migrates; new or materially "
            "revised transfer items must close all machine-checkable debt."
        ),
        "generated_by": "Shared/tools/core2b_inventory.py --write-baseline",
        "items": items,
    }


def _key(row: dict) -> tuple[str, str, str]:
    return (
        str(row.get("subject") or ""),
        str(row.get("package_path") or ""),
        str(row.get("question_id") or ""),
    )


def forward_findings(report: dict, baseline: dict) -> list[dict]:
    prior = {_key(row): row for row in baseline.get("items", []) if isinstance(row, dict)}
    found = list(report.get("findings", []))
    for row in report.get("rows", []):
        if not row.get("debt_reasons"):
            continue
        key = _key(row)
        before = prior.get(key)
        where = ":".join(key)
        if before is None:
            found.append({
                "point": "CORE2B_NEW_TRANSFER_DEBT",
                "where": where,
                "detail": ", ".join(row["debt_reasons"]),
            })
        elif before.get("semantic_digest") != row.get("semantic_digest"):
            found.append({
                "point": "CORE2B_MATERIAL_EDIT_WITH_TRANSFER_DEBT",
                "where": where,
                "detail": (
                    "materially edited Core2B item still carries: "
                    + ", ".join(row["debt_reasons"])
                ),
            })
    return found


def audit(repo: Path = REPO, baseline_path: Path | None = None) -> dict:
    report = inventory(repo)
    baseline_path = baseline_path or (repo / DEFAULT_BASELINE.relative_to(REPO))
    if not baseline_path.is_file():
        found = [{
            "point": "CORE2B_LEGACY_BASELINE_MISSING",
            "where": str(baseline_path),
            "detail": "generate the deterministic Core2B debt baseline",
        }]
        return {**report, "forward_findings": found, "passed_forward": False}
    baseline = load(baseline_path)
    found = forward_findings(report, baseline)
    return {**report, "forward_findings": found, "passed_forward": not found}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--baseline", type=Path, default=DEFAULT_BASELINE)
    parser.add_argument("--write-baseline", action="store_true")
    parser.add_argument("--enforce-forward", action="store_true")
    args = parser.parse_args()

    report = inventory(REPO)
    if args.write_baseline:
        args.baseline.parent.mkdir(parents=True, exist_ok=True)
        args.baseline.write_text(
            json.dumps(baseline_document(report), indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    if args.enforce_forward:
        audited = audit(REPO, args.baseline)
        print(json.dumps(audited, indent=2, ensure_ascii=False))
        return 1 if not audited["passed_forward"] else 0
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
