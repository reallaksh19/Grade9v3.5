#!/usr/bin/env python3
"""Validate external answer-sheet gaps against canonical matrix semantics.

This module is deliberately transient. A diagnostic gap can narrow a canonical
capability to an existing teaching step and diagnostic stage, but it never creates
new rungs, capabilities, mastery state, prerequisite clearance, or evidence from
absence. Invalid narrow precision degrades only to the valid capability-level gap.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402

FORMAT = "GRADE9V3_EXTERNAL_DIAGNOSTIC_GAP_ENVELOPE"
VERSION = "0.1.0"
GAP_RESULTS = ("MISSING", "UNCERTAIN")
DIAGNOSTIC_STAGES = ("CONCEPT", "SETUP", "EXECUTION", "CARELESS", "UNKNOWN")
DIMENSION_INDEX = {
    "CONCEPT": 0,
    "SETUP": 1,
    "EXECUTION": 2,
    "CARELESS": 3,
    "UNKNOWN": 99,
}


def _records(subject: str, repo: Path = REPO) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _board(subject: str, matrix_id: str, repo: Path = REPO) -> dict | None:
    for path in sorted((repo / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        if board.get("matrix_id") == matrix_id:
            return {**board, "_path": str(path.relative_to(repo))}
    return None


def derive_address(rung: str, step_index: int, stage: str) -> str:
    """Presentation address only; canonical matrix identity remains rung/capability/step."""
    if step_index == 99:
        return f"{rung}.99"
    dim = DIMENSION_INDEX.get(stage, 99)
    return f"{rung}.{step_index}.{dim if dim != 99 else 99}"


def _top_level_errors(payload: object) -> list[str]:
    if not isinstance(payload, dict):
        return ["diagnostic envelope must be an object"]
    errors = []
    expected = {
        "format": FORMAT,
        "version": VERSION,
        "provenance": "HISTORICAL_IMPORT",
        "evidence_kind": "PRIOR_DIAGNOSTIC",
    }
    for key, value in expected.items():
        if payload.get(key) != value:
            errors.append(f"{key} must equal {value}")
    for key in ("diagnostic_id", "matrix_id", "subject", "when"):
        if not isinstance(payload.get(key), str) or not payload[key].strip():
            errors.append(f"{key} is required and must be non-empty text")
    if not isinstance(payload.get("rows"), list):
        errors.append("rows must be a list")
    return errors


def _capability_rows(board: dict, records: dict) -> dict[str, list[dict]]:
    found: dict[str, list[dict]] = {}
    for row in board.get("rungs", []):
        micro = records.get(row.get("microtopic_ref"), {})
        capability = micro.get("primary_capability_ref")
        if capability:
            found.setdefault(capability, []).append({
                "rung": row,
                "microtopic": micro,
                "capability": records.get(capability, {}),
            })
    return found


def _resolve_row(row: object, index: int, cap_rows: dict[str, list[dict]]) -> tuple[dict | None, str | None, str | None]:
    if not isinstance(row, dict):
        return None, f"row {index + 1} must be an object", None

    cap_ref = row.get("capability_ref")
    if not isinstance(cap_ref, str) or not cap_ref.strip():
        return None, f"row {index + 1} requires capability_ref; no fuzzy mapping is allowed", None

    matches = cap_rows.get(cap_ref, [])
    if not matches:
        return None, f"row {index + 1} capability_ref {cap_ref} is not on this matrix", None
    if len(matches) != 1:
        return None, f"row {index + 1} capability_ref {cap_ref} is ambiguous on this matrix", None

    context = matches[0]
    rung = context["rung"]
    micro = context["microtopic"]

    rung_ref = row.get("rung_ref")
    if rung_ref is not None:
        if not isinstance(rung_ref, str) or not rung_ref.strip():
            return None, f"row {index + 1} rung_ref must be non-empty text when supplied", None
        if rung_ref != rung.get("rung"):
            return None, (
                f"row {index + 1} rung_ref {rung_ref} conflicts with capability_ref "
                f"{cap_ref} ({rung.get('rung')})"
            ), None

    result = row.get("result")
    if result not in GAP_RESULTS:
        return None, f"row {index + 1} result must be MISSING or UNCERTAIN", None

    stage = row.get("error_stage", "UNKNOWN")
    if not isinstance(stage, str):
        return None, f"row {index + 1} error_stage must be text", None
    stage = stage.upper()
    if stage not in DIAGNOSTIC_STAGES:
        return None, (
            f"row {index + 1} error_stage {row.get('error_stage')} is not in the "
            "diagnostic vocabulary"
        ), None

    score = row.get("score")
    if score is not None:
        if isinstance(score, bool) or not isinstance(score, (int, float)) or not 0 <= score <= 100:
            return None, f"row {index + 1} score must be a number from 0 to 100 when supplied", None

    observed = row.get("observed")
    if not isinstance(observed, str) or not observed.strip():
        return None, f"row {index + 1} requires non-empty observed answer-sheet evidence", None

    question_ref = row.get("question_ref")
    if question_ref is not None and (not isinstance(question_ref, str) or not question_ref.strip()):
        return None, f"row {index + 1} question_ref must be non-empty text or null", None

    tpath = list(micro.get("teaching_path") or [])
    repair_ref = row.get("repair_ref")
    warning = None
    step_index = 99
    step = None
    if repair_ref is not None:
        if not isinstance(repair_ref, str) or not repair_ref.strip():
            return None, f"row {index + 1} repair_ref must be non-empty text or null", None
        step_index = next((i for i, item in enumerate(tpath) if item.get("id") == repair_ref), -1)
        if step_index >= 0:
            step = tpath[step_index]
        else:
            warning = (
                f"row {index + 1} repair_ref {repair_ref} is not a canonical step on "
                f"{rung.get('rung')}; discarded only the unsupported narrow target"
            )
            repair_ref = None
            step_index = 99

    fallback = "EXACT_LEAF_DIMENSION"
    if step_index == 99:
        fallback = "CAPABILITY_ONLY_FALLBACK"
    elif stage == "UNKNOWN":
        fallback = "LEAF_UNKNOWN_DIMENSION_FALLBACK"

    target = {
        "address": derive_address(rung["rung"], step_index, stage),
        "rung": rung["rung"],
        "capability_ref": cap_ref,
        "microtopic_ref": micro.get("id"),
        "repair_ref": repair_ref,
        "error_stage": stage,
        "score": score,
        "observed": observed.strip(),
        "result": result,
        "question_ref": question_ref,
        "fallback_level": fallback,
        "step_action": step.get("action") if step else None,
    }
    return target, None, warning


def resolve(payload: dict, repo: Path = REPO, *,
            expected_subject: str | None = None,
            expected_matrix_id: str | None = None) -> dict:
    """Return validated focus targets without changing learner placement or readiness."""
    errors = _top_level_errors(payload)
    if errors:
        return {
            "state": "REJECTED",
            "passed": False,
            "matrix_id": payload.get("matrix_id") if isinstance(payload, dict) else None,
            "subject": payload.get("subject") if isinstance(payload, dict) else None,
            "targets": [],
            "rejected": [],
            "warnings": [],
            "errors": errors,
            "rule": "invalid diagnostic input is isolated; it does not become learner evidence or planner authority",
        }

    subject = payload["subject"]
    matrix_id = payload["matrix_id"]
    if expected_subject and subject != expected_subject:
        errors.append(f"diagnostic subject {subject} does not match request subject {expected_subject}")
    if expected_matrix_id and matrix_id != expected_matrix_id:
        errors.append(
            f"diagnostic matrix_id {matrix_id} does not match request matrix {expected_matrix_id}"
        )
    board = _board(subject, matrix_id, repo)
    if board is None:
        errors.append(f"no canonical matrix {matrix_id} exists under subject {subject}")
    elif payload.get("subtopic") and payload.get("subtopic") != board.get("subtopic"):
        errors.append(
            f"diagnostic subtopic {payload.get('subtopic')} does not match canonical "
            f"{board.get('subtopic')}"
        )

    if errors or board is None:
        return {
            "state": "REJECTED",
            "passed": False,
            "matrix_id": matrix_id,
            "subject": subject,
            "targets": [],
            "rejected": [],
            "warnings": [],
            "errors": errors,
            "rule": "matrix/subject identity is exact; no cross-topic or fuzzy diagnostic mapping is allowed",
        }

    records = _records(subject, repo)
    cap_rows = _capability_rows(board, records)
    targets = []
    rejected = []
    warnings = []
    for index, row in enumerate(payload.get("rows", [])):
        target, error, warning = _resolve_row(row, index, cap_rows)
        if error:
            rejected.append({"index": index, "error": error})
            continue
        targets.append(target)
        if warning:
            warnings.append({"index": index, "warning": warning})

    state = "VALID"
    if rejected and targets:
        state = "PARTIAL"
    elif rejected and not targets:
        state = "REJECTED"
    elif not targets:
        state = "EMPTY"

    return {
        "state": state,
        "passed": not rejected,
        "diagnostic_id": payload.get("diagnostic_id"),
        "matrix_id": matrix_id,
        "subject": subject,
        "bucket_id": board.get("bucket_id"),
        "subtopic": board.get("subtopic"),
        "when": payload.get("when"),
        "targets": targets,
        "rejected": rejected,
        "warnings": warnings,
        "errors": [],
        "rule": (
            "targets are transient focus only; absence is not DEMONSTRATED, scores are not "
            "mastery thresholds, and repair_ref precision comes only from canonical steps"
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--expected-subject")
    parser.add_argument("--expected-matrix")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = resolve(
        load(args.input),
        expected_subject=args.expected_subject,
        expected_matrix_id=args.expected_matrix,
    )
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
