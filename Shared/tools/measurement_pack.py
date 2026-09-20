#!/usr/bin/env python3
"""Export canonical scanner instructions for one Grade9V3 matrix.

The pack separates what an external evaluator may measure from Grade9V3-only routing
context. It never asks the scanner to redefine difficulty, prerequisites, ladder
coordinates, or mastery thresholds.
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
from Shared.tools.atlas_need import DIAGNOSTIC_STAGES, GAP_RESULTS  # noqa: E402

FORMAT = "GRADE9V3_TOPIC_ATLAS_MEASUREMENT_PACK"
VERSION = "1.0.0"


def _records(subject: str, repo: Path = REPO) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _board(subject: str, matrix_id: str, repo: Path = REPO) -> dict:
    for path in sorted((repo / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        if board.get("matrix_id") == matrix_id:
            return {**board, "_path": str(path.relative_to(repo))}
    raise ValueError(f"no matrix {matrix_id} exists under subject {subject}")


def _questions(records: dict, capability_ref: str) -> list[dict]:
    rows = []
    for row in records.values():
        if row.get("_collection") != "questions":
            continue
        if row.get("primary_capability_ref") != capability_ref:
            continue
        rows.append({
            "id": row["id"],
            "family_ref": row.get("family_ref"),
            "repair_ref": row.get("repair_ref"),
            "stem": row.get("stem"),
            "exposure": [item.get("core") for item in row.get("exposure", []) if item.get("core")],
        })
    return sorted(rows, key=lambda x: x["id"])


def build(subject: str, matrix_id: str, repo: Path = REPO) -> dict:
    board = _board(subject, matrix_id, repo)
    records = _records(subject, repo)
    targets = []

    for rung in board.get("rungs", []):
        micro = records.get(rung.get("microtopic_ref"), {})
        capability_ref = micro.get("primary_capability_ref")
        capability = records.get(capability_ref, {}) if capability_ref else {}
        targets.append({
            "measurement": {
                "capability_ref": capability_ref,
                "capability_action": capability.get("action"),
                "success_criterion": capability.get("success_criterion"),
                "microtopic_ref": micro.get("id"),
                "microtopic_title": micro.get("title"),
                "semantic_actions": [
                    {
                        "id": step.get("id"),
                        "role": step.get("role"),
                        "action": step.get("action"),
                        "why_valid": step.get("why_valid"),
                    }
                    for step in micro.get("teaching_path", [])
                ],
                "misconceptions": [
                    {
                        "wrong_idea": item.get("wrong_idea"),
                        "diagnostic_prompt": item.get("diagnostic_prompt"),
                        "repair": item.get("repair"),
                    }
                    for item in micro.get("misconceptions", [])
                ],
                "questions": _questions(records, capability_ref) if capability_ref else [],
            },
            "routing_context": {
                "rung": rung.get("rung"),
                "ladder_position": rung.get("ladder_position"),
                "default_entry_eligible": rung.get("default_entry_eligible", True),
                "prerequisites": list(capability.get("prerequisite_refs") or []),
                "intrinsic_difficulty": micro.get("intrinsic_badge"),
                "difficulty_reason": micro.get("badge_reason"),
            },
        })

    return {
        "format": FORMAT,
        "version": VERSION,
        "authority_note": (
            "Generated from canonical Grade9V3 package and matrix records. External "
            "evaluation may report only observed gaps against supplied targets; routing "
            "context remains Grade9V3 authority."
        ),
        "generator": "Shared/tools/measurement_pack.py",
        "matrix_id": board["matrix_id"],
        "subject": board.get("subject", subject),
        "topic": board.get("topic"),
        "subtopic": board.get("subtopic"),
        "bucket_id": board.get("bucket_id"),
        "diagnostic_contract": {
            "result_values": list(GAP_RESULTS),
            "error_stage_values": list(DIAGNOSTIC_STAGES),
            "score": {
                "optional": True,
                "minimum": 0,
                "maximum": 100,
                "rule": (
                    "Target-local display/evidence score only. Grade9V3 defines no automatic "
                    "mastery threshold and never averages stage scores into rung mastery."
                ),
            },
            "rules": [
                "Report only gaps supported by written answer-sheet evidence.",
                "Absence from the gap list is not DEMONSTRATED.",
                "Use capability_ref exactly as supplied; do not fuzzy-map.",
                "Use repair_ref only when the supplied stable semantic action supports that precision.",
                "Do not recalculate canonical difficulty, prerequisites, or ladder position.",
            ],
        },
        "targets": targets,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--subject", required=True)
    parser.add_argument("--matrix", required=True)
    args = parser.parse_args()
    print(json.dumps(build(args.subject, args.matrix), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
