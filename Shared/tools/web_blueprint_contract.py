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
CORE_ROLES = {"CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B", "EXPLORER"}   # EXPLORER is a page the Cores lead to, not a Core
PACKAGING_MODES = {"PUBLIC", "PAGES", "OFFLINE_DIRECTORY", "SINGLE_FILE", "EMBED"}
COLUMNS = {"FULL", "PRIMARY", "SUPPORT"}
BANDS = ("D1", "D2", "D3", "D4")
WAIVER_KEY = "grade9v3:component_waivers"
LEVELS = ("REQUIRED", "EXPECTED", "OPTIONAL")


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


def presentations(schema_path: Path = SCHEMA_PATH) -> set[str]:
    """The presentation archetypes a blueprint may name (the schema's closed list)."""
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return set(schema["$defs"]["presentation"]["enum"])


def blueprint_for_role(registry: dict[str, Any], role: str) -> dict[str, Any] | None:
    """The one active blueprint a Core role renders through, or None when the registry has none."""
    rows = [row for row in registry.get("blueprints") or []
            if isinstance(row, dict) and row.get("status") == "ACTIVE" and role in (row.get("core_roles") or [])]
    return rows[0] if len(rows) == 1 else None


def components(blueprint: dict[str, Any]) -> list[dict[str, Any]]:
    """The components a blueprint declares, in the order they appear on the page."""
    return [c for c in blueprint.get("components") or [] if isinstance(c, dict)]


def slot_column(blueprint: dict[str, Any], slot_id: str) -> str:
    """Where a slot sits in the expanded layout (FULL, PRIMARY or SUPPORT)."""
    for slot in blueprint.get("slots") or []:
        if isinstance(slot, dict) and slot.get("id") == slot_id:
            return slot.get("column") or "FULL"
    return "FULL"


def required_components(blueprint: dict[str, Any], level: str = "REQUIRED") -> list[dict[str, Any]]:
    return [c for c in components(blueprint) if c.get("level") == level]


def skeleton(blueprint: dict[str, Any]) -> dict[str, Any]:
    """The empty record fields the blueprint's components ask an author to fill, merged into one object."""
    out: dict[str, Any] = {}

    def merge(into: dict, add: dict) -> None:
        for key, value in add.items():
            if isinstance(value, dict) and isinstance(into.get(key), dict):
                merge(into[key], value)
            else:
                into[key] = copy.deepcopy(value)

    for component in components(blueprint):
        merge(out, (component.get("authoring") or {}).get("skeleton") or {})
    return out


def _walk(record: Any, path: str) -> Any:
    for part in path.split("."):
        if not isinstance(record, dict):
            return None
        record = record.get(part)
    return record


def record_items(component: dict[str, Any], record: dict[str, Any]) -> int:
    """How much a record supplies to a component. A component with a depth (min_items) is counted by the length of
    the first non-empty list among its source fields; any other is 1 when a source field holds something, else 0."""
    values = [_walk(record, path) for path in component.get("source") or []]
    for value in values:
        if isinstance(value, list) and value:
            return len(value)
    if component.get("min_items"):
        return 0
    return 1 if any(value not in (None, "", [], {}) for value in values) else 0


def band_of(component: dict[str, Any], record: dict[str, Any]) -> str | None:
    """The difficulty band the record declares where the component says to look, if it is one of D1 to D4."""
    path = component.get("band_source")
    band = _walk(record, path) if path else None
    return band if band in BANDS else None


def target_for(component: dict[str, Any], band: str | None = None) -> int | None:
    """The reference depth of a component for a record of this band (the flat target when the band is unknown)."""
    by_band = component.get("target_items_by_band") or {}
    if band in by_band:
        return by_band[band]
    if by_band and component.get("target_items") is None:
        return max(by_band.values())      # a band that is not declared is held to the deepest reference
    return component.get("target_items")


def waivers_of(record: dict[str, Any]) -> dict[str, str]:
    """{component id: reason} the record's author declared not applicable (reasons that are blank do not count)."""
    found = (record.get("extensions") or {}).get(WAIVER_KEY)
    if not isinstance(found, dict):
        return {}
    return {key: reason.strip() for key, reason in found.items() if isinstance(reason, str) and reason.strip()}


def record_problems(blueprint: dict[str, Any], record: dict[str, Any], label: str, explained: set[str] | None = None) -> list[str]:
    """Where a record falls short of what its blueprint asks of new authoring.

    Held to the reference page: every REQUIRED component that has a depth is measured against its target for the
    record's band, and every EXPECTED component must be present or waived by the record with a reason. With
    `explained`, a component's authoring instruction is given at its first shortfall and left out of later ones."""
    out = []
    waivers = waivers_of(record)

    def say(component: dict[str, Any], message: str) -> str:
        hint = (component.get("authoring") or {}).get("hint", "")
        if not hint or (explained is not None and component["id"] in explained):
            return f"{label}: {message}"
        if explained is not None:
            explained.add(component["id"])
        return f"{label}: {message} {hint}"

    for component in components(blueprint):
        level = component.get("level")
        if level == "REQUIRED" and (component.get("min_items") or component.get("target_items")
                                    or component.get("target_items_by_band")):
            needed = target_for(component, band_of(component, record)) or component.get("min_items")
            if not needed:
                continue
            found = record_items(component, record)
            if found < needed:
                out.append(say(component, f"{component['id']} needs {needed}, the record supplies {found}."))
        elif level == "EXPECTED" and not component.get("repeat") and component["id"] not in waivers:
            if record_items(component, record) == 0:
                out.append(say(component, f"{component['id']} is absent: supply it, or waive it in "
                                          f"extensions['{WAIVER_KEY}'] with the reason."))
    return out


def authoring_hints(blueprint: dict[str, Any]) -> list[tuple[str, str, str]]:
    """(component id, level, hint) for every component that tells an author what to write."""
    return [(c["id"], c["level"], c["authoring"]["hint"]) for c in components(blueprint)
            if (c.get("authoring") or {}).get("hint")]


def _finding(point: str, *, ref: str = "", detail: str = "") -> dict[str, str]:
    return {"point": point, "ref": ref, "detail": detail}


def _audit_components(row: dict[str, Any], ref: str, slot_ids: set[str]) -> list[dict[str, str]]:
    """A blueprint that declares components declares them completely: each in a real slot, each presentable."""
    declared = row.get("components")
    if declared is None:
        return []
    if not isinstance(declared, list) or not declared:
        return [_finding("WEB_BLUEPRINT_COMPONENTS_INVALID", ref=ref)]
    findings: list[dict[str, str]] = []
    try:
        known = presentations()
    except (OSError, KeyError, json.JSONDecodeError):
        known = set()
    by_id: dict[str, dict[str, Any]] = {}
    for component in declared:
        if not isinstance(component, dict) or not isinstance(component.get("id"), str):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_INVALID", ref=ref))
            continue
        cid = component["id"]
        if cid in by_id:
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_DUPLICATE", ref=ref, detail=cid))
        by_id[cid] = component
        if component.get("slot") not in slot_ids:
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_SLOT_UNKNOWN", ref=ref, detail=cid))
        if component.get("level") not in LEVELS:
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_LEVEL_INVALID", ref=ref, detail=cid))
        if known and component.get("presentation") not in known:
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_PRESENTATION_UNKNOWN", ref=ref, detail=cid))
        if not component.get("purpose") or not component.get("benchmark"):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_UNEXPLAINED", ref=ref, detail=cid))
        minimum = component.get("min_items")
        if minimum is not None and (not isinstance(minimum, int) or minimum < 1):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_MIN_ITEMS_INVALID", ref=ref, detail=cid))
        target = component.get("target_items")
        if target is not None and (not isinstance(target, int) or target < (minimum or 1)):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_TARGET_INVALID", ref=ref, detail=cid))
        by_band = component.get("target_items_by_band")
        if by_band is not None:
            if not component.get("band_source") or not isinstance(by_band, dict) \
                    or any(k not in BANDS or not isinstance(v, int) or v < (minimum or 1) for k, v in by_band.items()):
                findings.append(_finding("WEB_BLUEPRINT_COMPONENT_BAND_TARGETS_INVALID", ref=ref, detail=cid))
        if component.get("level") == "REQUIRED" and not (component.get("authoring") or {}).get("hint") \
                and not component.get("duty") and (minimum or component.get("repeat")):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_NO_AUTHORING_HINT", ref=ref, detail=cid))
    for cid, component in by_id.items():
        parent = component.get("parent")
        if parent is not None and (parent not in by_id or by_id[parent].get("slot") != component.get("slot")
                                   or by_id[parent].get("parent")):
            findings.append(_finding("WEB_BLUEPRINT_COMPONENT_PARENT_INVALID", ref=ref, detail=cid))
    unused = slot_ids - {c.get("slot") for c in by_id.values()}
    for slot_id in sorted(unused):
        findings.append(_finding("WEB_BLUEPRINT_SLOT_WITHOUT_COMPONENT", ref=ref, detail=slot_id))
    return findings


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

        for slot in slots:
            if isinstance(slot, dict) and slot.get("column") not in COLUMNS:
                findings.append(_finding("WEB_BLUEPRINT_SLOT_COLUMN_INVALID", ref=ref, detail=str(slot.get("id"))))
        findings.extend(_audit_components(row, ref, slot_ids))

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
