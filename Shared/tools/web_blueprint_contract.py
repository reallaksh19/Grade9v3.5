#!/usr/bin/env python3
"""Resolve and audit subject-neutral Interactive Page Blueprints."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
SCHEMA_PATH = REPO / "Shared" / "web" / "interactive-page-blueprint.schema.json"
REGISTRY_PATH = REPO / "Shared" / "web" / "interactive-page-blueprints.v1.json"
CORE_ROLES = {"CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"}
PACKAGING_MODES = {"PUBLIC", "PAGES", "OFFLINE_DIRECTORY", "SINGLE_FILE", "EMBED"}


class WebBlueprintContractError(ValueError):
    """Raised when a blueprint reference cannot be resolved safely."""


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise WebBlueprintContractError(f"WEB_BLUEPRINT_REGISTRY_LOAD_FAILED: {exc}") from exc
    if not isinstance(data, dict):
        raise WebBlueprintContractError("WEB_BLUEPRINT_REGISTRY_INVALID")
    return data


def blueprint_ref(row: dict[str, Any]) -> str:
    return f"{row.get('id', '')}@{row.get('version', '')}"


def split_ref(ref: str) -> tuple[str, str]:
    if not isinstance(ref, str) or "@" not in ref:
        raise WebBlueprintContractError("WEB_BLUEPRINT_REF_INVALID")
    blueprint_id, version = ref.rsplit("@", 1)
    if not blueprint_id or not version:
        raise WebBlueprintContractError("WEB_BLUEPRINT_REF_INVALID")
    return blueprint_id, version


def resolve_blueprint(ref: str, registry: dict[str, Any] | None = None) -> dict[str, Any]:
    blueprint_id, version = split_ref(ref)
    registry = registry or load_registry()
    rows = registry.get("blueprints")
    if not isinstance(rows, list):
        raise WebBlueprintContractError("WEB_BLUEPRINT_REGISTRY_ROWS_INVALID")
    same_id = [row for row in rows if isinstance(row, dict) and row.get("id") == blueprint_id]
    exact = [row for row in same_id if row.get("version") == version]
    if not same_id:
        raise WebBlueprintContractError(f"WEB_BLUEPRINT_UNKNOWN: {ref}")
    if not exact:
        raise WebBlueprintContractError(f"WEB_BLUEPRINT_VERSION_UNSUPPORTED: {ref}")
    if len(exact) != 1:
        raise WebBlueprintContractError(f"WEB_BLUEPRINT_DUPLICATE: {ref}")
    row = copy.deepcopy(exact[0])
    if row.get("status") != "ACTIVE":
        raise WebBlueprintContractError(f"WEB_BLUEPRINT_NOT_ACTIVE: {ref}")
    row["ref"] = ref
    return row


def _finding(point: str, *, ref: str = "", detail: str = "") -> dict[str, str]:
    return {"point": point, "ref": ref, "detail": detail}


def audit_registry(registry: dict[str, Any] | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    try:
        registry = registry or load_registry()
    except WebBlueprintContractError as exc:
        return {"passed": False, "blueprints_checked": 0, "findings": [_finding("WEB_BLUEPRINT_REGISTRY_LOAD_FAILED", detail=str(exc))]}

    if registry.get("schema_version") != "1.0":
        findings.append(_finding("WEB_BLUEPRINT_SCHEMA_VERSION_UNSUPPORTED", detail=str(registry.get("schema_version"))))
    shell = registry.get("shell")
    shell_id = shell.get("id") if isinstance(shell, dict) else None
    if not isinstance(shell_id, str) or not shell_id:
        findings.append(_finding("WEB_BLUEPRINT_SHELL_INVALID"))
    rows = registry.get("blueprints")
    if not isinstance(rows, list):
        return {"passed": False, "blueprints_checked": 0, "findings": findings + [_finding("WEB_BLUEPRINT_REGISTRY_ROWS_INVALID")]}

    seen_refs: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            findings.append(_finding("WEB_BLUEPRINT_ROW_INVALID"))
            continue
        ref = blueprint_ref(row)
        if ref in seen_refs:
            findings.append(_finding("WEB_BLUEPRINT_DUPLICATE", ref=ref))
        seen_refs.add(ref)
        if not row.get("id") or not row.get("version"):
            findings.append(_finding("WEB_BLUEPRINT_ID_VERSION_REQUIRED", ref=ref))
        roles = row.get("core_roles")
        if not isinstance(roles, list) or not roles or len(roles) != len(set(roles)) or any(role not in CORE_ROLES for role in roles):
            findings.append(_finding("WEB_BLUEPRINT_CORE_ROLES_INVALID", ref=ref))
        if not shell_id or row.get("shell_ref") != shell_id:
            findings.append(_finding("WEB_BLUEPRINT_SHELL_REF_INVALID", ref=ref))

        slots = row.get("slots")
        if not isinstance(slots, list) or not slots:
            findings.append(_finding("WEB_BLUEPRINT_SLOTS_INVALID", ref=ref))
            continue
        slot_ids: set[str] = set()
        mapped_blocks: set[str] = set()
        for slot in slots:
            if not isinstance(slot, dict) or not isinstance(slot.get("id"), str) or not slot["id"]:
                findings.append(_finding("WEB_BLUEPRINT_SLOT_INVALID", ref=ref))
                continue
            if slot["id"] in slot_ids:
                findings.append(_finding("WEB_BLUEPRINT_SLOT_DUPLICATE", ref=ref, detail=slot["id"]))
            slot_ids.add(slot["id"])
            blocks = slot.get("accepts_blocks")
            if not isinstance(blocks, list) or not blocks or any(not isinstance(block, str) or not block for block in blocks):
                findings.append(_finding("WEB_BLUEPRINT_SLOT_BLOCKS_INVALID", ref=ref, detail=slot["id"]))
                continue
            for block in blocks:
                if block in mapped_blocks:
                    findings.append(_finding("WEB_BLUEPRINT_BLOCK_AMBIGUOUS", ref=ref, detail=block))
                mapped_blocks.add(block)

        touch = row.get("touch_policy") or {}
        if not isinstance(touch.get("minimum_target_css_px"), int) or touch.get("minimum_target_css_px", 0) < 48:
            findings.append(_finding("WEB_BLUEPRINT_TOUCH_TARGET_TOO_SMALL", ref=ref))
        if not isinstance(touch.get("minimum_control_gap_css_px"), int) or touch.get("minimum_control_gap_css_px", 0) < 8:
            findings.append(_finding("WEB_BLUEPRINT_TOUCH_GAP_TOO_SMALL", ref=ref))
        packaging = row.get("packaging_modes")
        if not isinstance(packaging, list) or set(packaging) != PACKAGING_MODES:
            findings.append(_finding("WEB_BLUEPRINT_PACKAGING_MODES_INVALID", ref=ref))
        responsive = row.get("responsive_policy") or {}
        primary = responsive.get("primary_fraction")
        support = responsive.get("support_fraction")
        if not isinstance(primary, (int, float)) or not isinstance(support, (int, float)) or abs((primary + support) - 1.0) > 1e-9:
            findings.append(_finding("WEB_BLUEPRINT_RESPONSIVE_FRACTIONS_INVALID", ref=ref))
        representation = row.get("representation_policy") or {}
        if representation.get("legacy_iframe") != "MIGRATION_ONLY":
            findings.append(_finding("WEB_BLUEPRINT_LEGACY_IFRAME_POLICY_INVALID", ref=ref))

    return {
        "schema_version": registry.get("schema_version"),
        "registry_version": registry.get("registry_version"),
        "blueprints_checked": sum(1 for row in rows if isinstance(row, dict)),
        "passed": not findings,
        "findings": findings,
    }


def validate_role_binding(
    role_name: str,
    role: dict[str, Any],
    registry: dict[str, Any] | None = None,
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    ref = role.get("web_blueprint_ref")
    if not isinstance(ref, str) or not ref:
        return [_finding("WEB_BLUEPRINT_REF_MISSING", detail=role_name)]
    try:
        blueprint = resolve_blueprint(ref, registry)
    except WebBlueprintContractError as exc:
        message = str(exc)
        point = message.split(":", 1)[0]
        return [_finding(point, ref=ref, detail=role_name)]

    if role_name not in (blueprint.get("core_roles") or []):
        findings.append(_finding("WEB_BLUEPRINT_CORE_INCOMPATIBLE", ref=ref, detail=role_name))

    ordered = [
        block.get("id")
        for block in role.get("ordered_blocks") or []
        if isinstance(block, dict) and isinstance(block.get("id"), str)
    ]
    accepted = {
        block
        for slot in blueprint.get("slots") or []
        if isinstance(slot, dict)
        for block in slot.get("accepts_blocks") or []
        if isinstance(block, str)
    }
    for block in ordered:
        if block not in accepted:
            findings.append(_finding("WEB_BLUEPRINT_BLOCK_UNMAPPED", ref=ref, detail=f"{role_name}:{block}"))

    needs_attempt_boundary = bool(role.get("withheld_pre_attempt")) or any(
        block.get("visibility") == "ATTEMPT_FIRST"
        for block in role.get("ordered_blocks") or []
        if isinstance(block, dict)
    )
    attempt_policy = (blueprint.get("interaction_policy") or {}).get("attempt_before_reveal")
    if needs_attempt_boundary and attempt_policy == "NEVER":
        findings.append(_finding("WEB_BLUEPRINT_REVEAL_CONFLICT", ref=ref, detail=role_name))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit_registry()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
