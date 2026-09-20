#!/usr/bin/env python3
"""Overlay rough subtopic-wise owner estimates onto a canonical study route.

The generic study route stays learner-independent. This module adds the practical input a
parent can usually provide at the beginning: "she is roughly 70% on this subtopic."

An estimate chooses where to *try first* inside that matrix. Earlier routed capabilities
become QUICK_CHECK, never DEMONSTRATED. A failed quick check simply sends the learner into
normal study/feedback for that capability.

This is intentionally small. It is not a mastery model and it never compares ladder
positions across matrices.
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
from Shared.tools import capability_delivery, learner_evidence, study_map, study_route  # noqa: E402


def _boards(subject: str, repo: Path = REPO) -> dict[str, dict]:
    found = {}
    root = repo / subject / "matrices"
    if not root.is_dir():
        return found
    for path in sorted(root.glob("*.rungs.json")):
        board = load(path)
        found[board["matrix_id"]] = board
    return found


def _teaching_positions(index: dict,
                        explicit_nondefault: set[str] | None = None) -> dict[str, list[dict]]:
    """Existing teaching locations by matrix; record-less rungs are not start points.

    Non-default rungs are excluded from generic estimate coordinates unless this worksheet
    explicitly demands that capability as a question target or declared extension.
    """
    found: dict[str, list[dict]] = {}
    seen = set()
    explicit_nondefault = explicit_nondefault or set()
    for capability_ref, rows in index["locations"].items():
        for row in rows:
            if (
                row.get("default_entry_eligible", True) is False
                and capability_ref not in explicit_nondefault
            ):
                continue
            key = (
                row.get("matrix_id"),
                row.get("rung"),
                row.get("ladder_position"),
            )
            if key in seen:
                continue
            seen.add(key)
            found.setdefault(row["matrix_id"], []).append({
                "matrix_id": row["matrix_id"],
                "bucket_id": row.get("bucket_id"),
                "rung": row.get("rung"),
                "ladder_position": row.get("ladder_position"),
            })
    for rows in found.values():
        rows.sort(key=lambda row: (
            int(row.get("ladder_position") or 0),
            str(row.get("rung") or ""),
        ))
    return found


def _resolve_estimate_target(estimate: dict, boards: dict[str, dict]) -> tuple[str | None, dict | None]:
    matrix_id = estimate.get("matrix_id")
    bucket_id = estimate.get("bucket_id")

    if bool(matrix_id) == bool(bucket_id):
        return None, {
            "point": "STUDY_START_ESTIMATE_TARGET_INVALID",
            "detail": "each estimate must name exactly one of matrix_id or bucket_id",
        }
    if matrix_id:
        if matrix_id not in boards:
            return None, {
                "point": "STUDY_START_MATRIX_UNKNOWN",
                "matrix_id": matrix_id,
                "detail": "no matrix with this id exists for the worksheet subject",
            }
        return matrix_id, None

    matches = [
        mid for mid, board in boards.items()
        if board.get("bucket_id") == bucket_id
    ]
    if not matches:
        return None, {
            "point": "STUDY_START_BUCKET_UNKNOWN",
            "bucket_id": bucket_id,
            "detail": "no matrix declares this bucket for the worksheet subject",
        }
    if len(matches) > 1:
        return None, {
            "point": "STUDY_START_BUCKET_AMBIGUOUS",
            "bucket_id": bucket_id,
            "detail": "more than one matrix declares this bucket; supply matrix_id",
            "matrices": sorted(matches),
        }
    return matches[0], None


def _select_start(rows: list[dict], percentage: float) -> dict | None:
    if not rows:
        return None
    eligible = [
        row for row in rows
        if float(row.get("ladder_position") or 0) <= percentage
    ]
    return eligible[-1] if eligible else rows[0]


GATEWAY_CHECKS_PER_MATRIX = 1


def _gateway_representatives(route_rows: list[dict], profile: dict | None,
                             repo: Path) -> dict[str, list[str]]:
    """Choose a bounded local quick-check sample without manufacturing evidence."""
    by_matrix: dict[str, list[tuple[float, str]]] = {}
    for row in route_rows:
        locations = row.get("locations") or []
        if row.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE:
            continue
        if row.get("state") != "RESOLVED" or len(locations) != 1:
            continue
        capability_ref = row.get("capability_ref")
        state = (
            learner_evidence.effective_state(profile, capability_ref, repo)["state"]
            if profile is not None
            else "UNOBSERVED"
        )
        if state not in {"UNOBSERVED", "UNCERTAIN"}:
            continue
        location = locations[0]
        matrix_id = location.get("matrix_id")
        if not matrix_id:
            continue
        by_matrix.setdefault(matrix_id, []).append((
            float(location.get("ladder_position") or 0),
            capability_ref,
        ))

    selected = {}
    for matrix_id, rows in by_matrix.items():
        ordered = sorted(rows, key=lambda item: (item[0], item[1]))
        selected[matrix_id] = [
            capability for _, capability in ordered[:GATEWAY_CHECKS_PER_MATRIX]
        ]
    return selected


def resolve(mapping: dict, owner_estimates: list[dict] | None = None,
            repo: Path = REPO, *, profile: dict | None = None) -> dict:
    """Return the generic route plus a per-capability learner start action."""
    route = study_route.resolve(mapping, repo)
    findings = list(route.get("findings", []))
    warnings: list[dict] = []
    subject = mapping.get("subject")
    index = study_map.subject_index(subject, repo)
    boards = _boards(subject, repo)
    explicit_nondefault = {
        row["capability_ref"]
        for row in route.get("route", [])
        if {"QUESTION_DEMAND", "DECLARED_EXTENSION"} & set(row.get("reasons", []))
    }
    positions = _teaching_positions(index, explicit_nondefault)

    decisions: dict[str, dict] = {}
    for estimate in owner_estimates or []:
        matrix_id, finding = _resolve_estimate_target(estimate, boards)
        if finding:
            warnings.append(finding)
            continue

        percentage = estimate.get("knowledge_percentage")
        if not isinstance(percentage, (int, float)) or isinstance(percentage, bool):
            warnings.append({
                "point": "STUDY_START_ESTIMATE_INVALID",
                "matrix_id": matrix_id,
                "detail": "knowledge_percentage must be a number from 0 to 100",
            })
            continue
        if percentage < 0 or percentage > 100:
            warnings.append({
                "point": "STUDY_START_ESTIMATE_OUT_OF_RANGE",
                "matrix_id": matrix_id,
                "detail": "knowledge_percentage must be between 0 and 100",
            })
            continue
        if matrix_id in decisions:
            warnings.append({
                "point": "STUDY_START_ESTIMATE_DUPLICATE",
                "matrix_id": matrix_id,
                "detail": "only one rough owner estimate may be supplied per matrix",
            })
            continue

        selected = _select_start(positions.get(matrix_id, []), percentage)
        if selected is None:
            warnings.append({
                "point": "STUDY_START_MATRIX_HAS_NO_TEACHING_LOCATION",
                "matrix_id": matrix_id,
                "detail": "the matrix has no canonical teaching location to start from",
            })
            continue

        board = boards[matrix_id]
        decisions[matrix_id] = {
            "matrix_id": matrix_id,
            "bucket_id": board.get("bucket_id"),
            "topic": board.get("topic"),
            "subtopic": board.get("subtopic"),
            "knowledge_percentage": percentage,
            "selected_rung": selected["rung"],
            "selected_position": selected["ladder_position"],
            "provenance": "OWNER_ESTIMATE",
            "rule": (
                "routing hint only; capabilities below this point require a quick check "
                "and are not marked demonstrated"
            ),
        }

    gateway = _gateway_representatives(route.get("route", []), profile, repo)
    learner_route = []
    for row in route.get("route", []):
        item = dict(row)
        locations = row.get("locations") or []
        if row.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE:
            item["learner_action"] = "BRIDGE"
            item["estimate_basis"] = None
            item["gateway_basis"] = None
            learner_route.append(item)
            continue
        if row.get("state") != "RESOLVED" or len(locations) != 1:
            item["learner_action"] = "UNRESOLVED"
            item["estimate_basis"] = None
            item["gateway_basis"] = None
            learner_route.append(item)
            continue

        location = locations[0]
        decision = decisions.get(location["matrix_id"])
        if decision is None:
            selected = row.get("capability_ref") in gateway.get(location["matrix_id"], [])
            item["learner_action"] = "QUICK_CHECK" if selected else "STUDY"
            item["estimate_basis"] = None
            item["gateway_basis"] = (
                {
                    "matrix_id": location["matrix_id"],
                    "reason": "bounded representative check over uncertain/unobserved local capability",
                    "not_evidence": True,
                }
                if selected else None
            )
        else:
            position = float(location.get("ladder_position") or 0)
            start = float(decision["selected_position"])
            if position < start:
                item["learner_action"] = "QUICK_CHECK"
            elif position == start:
                item["learner_action"] = "START_HERE"
            else:
                item["learner_action"] = "STUDY"
            item["gateway_basis"] = None
            item["estimate_basis"] = {
                "matrix_id": decision["matrix_id"],
                "knowledge_percentage": decision["knowledge_percentage"],
                "selected_rung": decision["selected_rung"],
                "selected_position": decision["selected_position"],
                "not_evidence": True,
            }
        learner_route.append(item)

    blockers = list(route.get("blockers", []))
    valid = not findings
    return {
        "worksheet_id": route.get("worksheet_id"),
        "subject": route.get("subject"),
        "start_decisions": [
            decisions[mid] for mid in sorted(decisions)
        ],
        "gateway_decisions": [
            {
                "matrix_id": matrix_id,
                "capability_refs": list(gateway[matrix_id]),
                "max_checks": GATEWAY_CHECKS_PER_MATRIX,
                "not_evidence": True,
            }
            for matrix_id in sorted(gateway)
            if matrix_id not in decisions and gateway[matrix_id]
        ],
        "route": learner_route,
        "findings": findings,
        "warnings": warnings,
        "execution_disposition": "EXECUTE_WITH_FALLBACK" if warnings and valid else None,
        "blockers": blockers,
        "valid": valid,
        "ready": valid and not blockers,
        "passed": valid,
        "rule": (
            "Subtopic estimates choose local starting attempts only. Without an estimate, "
            "each matrix gets at most one representative uncertain/unobserved QUICK_CHECK. "
            "QUICK_CHECK is not mastery evidence; cross-matrix order still comes only from prerequisites."
        ),
    }


def readable(report: dict) -> str:
    out = [
        f'# Learner start -- {report.get("worksheet_id")}',
        "",
        f'  subject  {report.get("subject")}',
        "",
    ]
    if report.get("start_decisions"):
        out += ["## Owner estimates", ""]
        for row in report["start_decisions"]:
            out += [
                f'  {row["matrix_id"]}: {row["knowledge_percentage"]}% '
                f'-> {row["selected_rung"]} ({row["selected_position"]})'
            ]
        out += [""]

    out += ["## Route", ""]
    for row in report.get("route", []):
        out += [
            f'{row["order"]:>2}. {row["learner_action"]:11} '
            f'{row["capability_ref"]} [{row["scope"]}]'
        ]
    if report.get("warnings"):
        out += ["", "## Fallback warnings", ""]
        out += [
            f'  {warning["point"]}: {warning.get("detail", "")}'
            for warning in report["warnings"]
        ]
    if report.get("findings"):
        out += ["", "## Findings", ""]
        out += [
            f'  {finding["point"]}: {finding.get("detail", "")}'
            for finding in report["findings"]
        ]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--map", type=Path, required=True)
    parser.add_argument(
        "--estimate",
        action="append",
        default=[],
        metavar="MATRIX_ID=PERCENT",
        help="rough owner estimate for one local matrix; may be repeated",
    )
    parser.add_argument("--readable", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    estimates = []
    for raw in args.estimate:
        if "=" not in raw:
            parser.error("--estimate must be MATRIX_ID=PERCENT")
        matrix_id, percentage = raw.split("=", 1)
        try:
            number = float(percentage)
        except ValueError:
            parser.error(f"invalid percentage in --estimate {raw}")
        estimates.append({
            "matrix_id": matrix_id,
            "knowledge_percentage": number,
        })

    report = resolve(load(args.map), estimates)
    print(readable(report) if args.readable
          else json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
