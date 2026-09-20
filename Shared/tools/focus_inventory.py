#!/usr/bin/env python3
"""Rank existing canonical inventory for validated diagnostic focus.

Precision comes only from explicit canonical bindings. Question text is never parsed to
infer diagnostic stage or repair-step ownership.
"""
from __future__ import annotations

import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load  # noqa: E402
from Shared.library.practice_inventory import bucket_questions  # noqa: E402
from Shared.library.resolve import build_index, load_packages  # noqa: E402


def _records(subject: str, repo: Path = REPO) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def _exposed(question: dict, core: str) -> bool:
    return any(item.get("core") == core for item in question.get("exposure", []))


def _question_rows(records: dict, bucket_id: str, core: str,
                   target: dict) -> list[dict]:
    capability = target.get("capability_ref")
    repair_ref = target.get("repair_ref")
    rows = [
        row for row in bucket_questions(records, bucket_id)
        if row.get("primary_capability_ref") == capability and _exposed(row, core)
    ]
    out = []
    for row in rows:
        bound = row.get("repair_ref")
        if repair_ref:
            if bound == repair_ref:
                precision = "EXACT_REPAIR_REF"
            elif not bound:
                precision = "CAPABILITY_LEVEL"
            else:
                continue
        else:
            precision = "CAPABILITY_LEVEL"
        out.append({
            "id": row["id"],
            "kind": "QUESTION",
            "precision": precision,
            "primary_capability_ref": row.get("primary_capability_ref"),
            "repair_ref": bound,
            "family_ref": row.get("family_ref"),
            "origin": row.get("origin"),
            "stage_binding": "NOT_ENCODED_IN_CANONICAL_ITEM",
        })
    return sorted(out, key=lambda x: (
        0 if x["precision"] == "EXACT_REPAIR_REF" else 1,
        x["id"],
    ))


def _activity_rows(records: dict, target: dict) -> list[dict]:
    capability = target.get("capability_ref")
    repair_ref = target.get("repair_ref")
    out = []
    for row in records.values():
        if row.get("_collection") != "resources" or "ACTIVITY" not in row.get("role", []):
            continue
        if capability not in row.get("supports_claims", []):
            continue
        atlas = (row.get("extensions") or {}).get("topic_atlas", {})
        step_refs = list(atlas.get("teaching_step_refs") or [])
        if repair_ref:
            if repair_ref in step_refs:
                precision = "EXACT_REPAIR_REF"
            elif not step_refs:
                precision = "CAPABILITY_LEVEL"
            else:
                continue
        else:
            precision = "CAPABILITY_LEVEL"
        out.append({
            "id": row["id"],
            "kind": "ACTIVITY",
            "precision": precision,
            "supports_claims": list(row.get("supports_claims") or []),
            "teaching_step_refs": step_refs,
            "locator": row.get("locator"),
            "stage_binding": "NOT_ENCODED_IN_CANONICAL_ITEM",
        })
    return sorted(out, key=lambda x: (
        0 if x["precision"] == "EXACT_REPAIR_REF" else 1,
        x["id"],
    ))


def for_core(subject: str, bucket_id: str, core: str,
             targets: list[dict] | None, repo: Path = REPO) -> dict:
    records = _records(subject, repo)
    groups = []
    for target in targets or []:
        groups.append({
            "address": target.get("address"),
            "capability_ref": target.get("capability_ref"),
            "repair_ref": target.get("repair_ref"),
            "error_stage": target.get("error_stage"),
            "questions": _question_rows(records, bucket_id, core, target),
            "activities": _activity_rows(records, target),
        })
    return {
        "core": core,
        "targets": groups,
        "rule": (
            "exact means an explicit repair_ref/teaching_step_refs binding; otherwise the "
            "match is capability-level. Diagnostic stage is never inferred from free-form text."
        ),
    }


def for_cores(subject: str, bucket_id: str, cores: list[str],
              targets: list[dict] | None, repo: Path = REPO) -> dict[str, dict]:
    return {
        core: for_core(subject, bucket_id, core, targets, repo)
        for core in cores
    }
