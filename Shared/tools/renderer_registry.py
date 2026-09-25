#!/usr/bin/env python3
"""Subject-neutral renderer capability registry derived from declared subject contracts."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CONTRACT_VERSION = "1.0.0"


def _load(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def manifests(subject: str, repo: Path = REPO) -> list[dict[str, Any]]:
    path = repo / subject / "adapter" / "CoreContracts.json"
    if not path.is_file():
        return []
    contract = _load(path)
    rows = []
    for kind in contract.get("representation_kinds", []):
        kind_id = kind.get("id")
        status = kind.get("status")
        if not isinstance(kind_id, str) or not kind_id:
            continue
        rows.append({
            "renderer_id": f"STATIC-{kind_id}@1.0.0",
            "version": "1.0.0",
            "subject": subject,
            "accepted_representation_kinds": [kind_id],
            "required_elements": list(kind.get("requires") or []),
            "supported_interactions": [],
            "input_contract": "CANONICAL_REPRESENTATION",
            "output_contract": "STATIC_SEMANTIC_RENDERING",
            "accessibility_capabilities": [
                "TEXTUAL_LABELS_REQUIRED",
                "NO_COLOUR_ONLY_ESSENTIAL_MEANING",
            ],
            "static_fallback": status == "IMPLEMENTED",
            "status": "READY" if status == "IMPLEMENTED" else "UNAVAILABLE",
            "basis": {
                "path": str(path.relative_to(repo)),
                "representation_kind_status": status,
            },
        })
    return rows


def resolve(
    subject: str,
    representation_kind: str | None,
    *,
    interaction_requirement: str = "OPTIONAL",
    repo: Path = REPO,
) -> dict[str, Any]:
    if not representation_kind:
        return {
            "status": "NOT_REQUIRED",
            "renderer": None,
            "interaction_satisfied": interaction_requirement != "REQUIRED",
        }
    matches = [
        row for row in manifests(subject, repo)
        if representation_kind in row["accepted_representation_kinds"]
    ]
    if not matches:
        return {
            "status": "UNAVAILABLE",
            "renderer": None,
            "interaction_satisfied": False if interaction_requirement == "REQUIRED" else True,
        }
    row = matches[0]
    if row["status"] != "READY":
        return {
            "status": "UNAVAILABLE",
            "renderer": row,
            "interaction_satisfied": False if interaction_requirement == "REQUIRED" else True,
        }
    interactive = bool(row["supported_interactions"])
    return {
        "status": "READY",
        "renderer": row,
        "interaction_satisfied": interaction_requirement != "REQUIRED" or interactive,
    }


def build(repo: Path = REPO) -> dict[str, Any]:
    subjects = sorted(
        path.parent.parent.name
        for path in repo.glob("*/adapter/CoreContracts.json")
    )
    rows = [row for subject in subjects for row in manifests(subject, repo)]
    return {
        "contract_version": CONTRACT_VERSION,
        "renderers": sorted(rows, key=lambda row: (row["subject"], row["renderer_id"])),
    }
