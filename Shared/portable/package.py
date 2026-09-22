"""Versioned, data-only portable workbench package contract."""
from __future__ import annotations

from copy import deepcopy
from typing import Any

PACKAGE_SCHEMA = "portable-workbench-package"
PACKAGE_VERSION = "1.0.0"
COMPONENT_API_VERSION = "0.1.0"
TRANSFORMATION_IR_VERSION = "0.1.0"
ADAPTER_API_VERSION = "0.1.0"
SCENE_PACKAGE_VERSION = "1.0.0"
DECLARATIVE_ADAPTER_ID = "declarative-transfer-v1"

_EXECUTABLE_KEYS = {
    "script", "javascript", "eval", "function", "handler",
    "onclick", "onload", "onerror", "sourcecode", "executable",
}
_PIXEL_KEYS = {"x", "y", "left", "top", "width", "height"}


class PortablePackageError(ValueError):
    def __init__(self, code: str, detail: str = ""):
        super().__init__(f"{code}: {detail}" if detail else code)
        self.code = code
        self.detail = detail


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise PortablePackageError(code, detail)


def _text(value: Any, code: str, detail: str = "") -> str:
    _require(isinstance(value, str) and value.strip(), code, detail)
    return value


def _string_list(value: Any, code: str, *, allow_empty: bool = True) -> list[str]:
    _require(isinstance(value, list), code)
    if not allow_empty:
        _require(bool(value), code)
    for item in value:
        _text(item, code)
    _require(len(value) == len(set(value)), code)
    return list(value)


def _scan_data(value: Any, path: str = "package") -> None:
    _require(not callable(value), "PORTABLE_EXECUTABLE_VALUE_FORBIDDEN", path)
    if isinstance(value, dict):
        for key, child in value.items():
            _text(key, "PORTABLE_FIELD_NAME_INVALID", path)
            _require(
                key.lower() not in _EXECUTABLE_KEYS,
                "PORTABLE_EXECUTABLE_FIELD_FORBIDDEN",
                f"{path}.{key}",
            )
            if key == "placement" and isinstance(child, dict):
                for pixel in _PIXEL_KEYS:
                    _require(
                        pixel not in child,
                        "PORTABLE_PIXEL_COORDINATE_FORBIDDEN",
                        f"{path}.{key}.{pixel}",
                    )
            _scan_data(child, f"{path}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _scan_data(child, f"{path}[{index}]")
    else:
        _require(
            value is None or isinstance(value, (str, int, float, bool)),
            "PORTABLE_DATA_TYPE_UNSUPPORTED",
            path,
        )


def _validate_scene(scene: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(scene, dict), "PORTABLE_SCENE_REQUIRED")
    _require(
        scene.get("apiVersion") == COMPONENT_API_VERSION,
        "PORTABLE_COMPONENT_API_VERSION_MISMATCH",
        str(scene.get("apiVersion")),
    )
    _text(scene.get("sceneVersion"), "PORTABLE_SCENE_VERSION_REQUIRED")
    _text(scene.get("id"), "PORTABLE_SCENE_ID_REQUIRED")
    grids = scene.get("grids")
    _require(isinstance(grids, list) and grids, "PORTABLE_SCENE_GRIDS_REQUIRED")
    grid_index: dict[str, dict[str, Any]] = {}
    for grid in grids:
        grid_id = _text(grid.get("id"), "PORTABLE_SCENE_GRID_ID_REQUIRED")
        _require(grid_id not in grid_index, "PORTABLE_SCENE_GRID_ID_DUPLICATE", grid_id)
        rows = _string_list(grid.get("rows"), "PORTABLE_SCENE_GRID_ROWS_INVALID", allow_empty=False)
        columns = _string_list(grid.get("columns"), "PORTABLE_SCENE_GRID_COLUMNS_INVALID", allow_empty=False)
        grid_index[grid_id] = {"rows": rows, "columns": columns}

    def validate_placement(row: dict[str, Any], owner: str) -> None:
        placement = row.get("placement")
        _require(isinstance(placement, dict), "PORTABLE_PLACEMENT_REQUIRED", owner)
        _require(set(placement) == {"grid", "row", "column"}, "PORTABLE_PLACEMENT_FIELDS_INVALID", owner)
        grid = grid_index.get(placement.get("grid"))
        _require(grid is not None, "PORTABLE_PLACEMENT_GRID_UNKNOWN", owner)
        _require(placement.get("row") in grid["rows"], "PORTABLE_PLACEMENT_ROW_UNKNOWN", owner)
        _require(placement.get("column") in grid["columns"], "PORTABLE_PLACEMENT_COLUMN_UNKNOWN", owner)

    entities = scene.get("entities") or []
    projections = scene.get("projections") or []
    targets = scene.get("targets") or []
    transforms = scene.get("canonicalTransformations") or []
    for rows, code in [
        (entities, "PORTABLE_SCENE_ENTITIES_INVALID"),
        (projections, "PORTABLE_SCENE_PROJECTIONS_INVALID"),
        (targets, "PORTABLE_SCENE_TARGETS_INVALID"),
        (transforms, "PORTABLE_SCENE_TRANSFORMATIONS_INVALID"),
    ]:
        _require(isinstance(rows, list), code)
        ids = [_text(row.get("id"), code) for row in rows]
        _require(len(ids) == len(set(ids)), code)

    entity_ids = {row["id"] for row in entities}
    target_ids = {row["id"] for row in targets}
    for projection in projections:
        _require(projection.get("entityRef") in entity_ids, "PORTABLE_PROJECTION_ENTITY_UNKNOWN", projection.get("id", ""))
        validate_placement(projection, projection["id"])
    for target in targets:
        _text(target.get("operation"), "PORTABLE_TARGET_OPERATION_REQUIRED", target["id"])
        validate_placement(target, target["id"])
    for transform in transforms:
        sources = _string_list(transform.get("sourceEntityRefs"), "PORTABLE_TRANSFORMATION_SOURCES_INVALID", allow_empty=False)
        for source in sources:
            _require(source in entity_ids, "PORTABLE_TRANSFORMATION_SOURCE_UNKNOWN", source)
        _require(transform.get("targetRef") in target_ids, "PORTABLE_TRANSFORMATION_TARGET_UNKNOWN", transform.get("id", ""))
    return deepcopy(scene)


def _validate_adapter(adapter: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(adapter, dict), "PORTABLE_ADAPTER_REQUIRED")
    _require(adapter.get("id") == DECLARATIVE_ADAPTER_ID, "PORTABLE_ADAPTER_ID_UNSUPPORTED", str(adapter.get("id")))
    _require(adapter.get("apiVersion") == ADAPTER_API_VERSION, "PORTABLE_ADAPTER_API_VERSION_MISMATCH", str(adapter.get("apiVersion")))
    rules = adapter.get("rules")
    _require(isinstance(rules, list) and rules, "PORTABLE_ADAPTER_RULES_REQUIRED")
    transforms = {row["id"]: row for row in scene.get("canonicalTransformations") or []}
    targets = {row["id"]: row for row in scene.get("targets") or []}
    seen: set[str] = set()
    for rule in rules:
        rule_id = _text(rule.get("id"), "PORTABLE_ADAPTER_RULE_ID_REQUIRED")
        _require(rule_id not in seen, "PORTABLE_ADAPTER_RULE_ID_DUPLICATE", rule_id)
        seen.add(rule_id)
        ref = _text(rule.get("transformationRef"), "PORTABLE_ADAPTER_TRANSFORMATION_REQUIRED", rule_id)
        transform = transforms.get(ref)
        _require(transform is not None, "PORTABLE_ADAPTER_TRANSFORMATION_UNKNOWN", ref)
        source = _text(rule.get("sourceEntityRef"), "PORTABLE_ADAPTER_SOURCE_REQUIRED", rule_id)
        _require(source in transform["sourceEntityRefs"], "PORTABLE_ADAPTER_SOURCE_MISMATCH", rule_id)
        target = _text(rule.get("targetRef"), "PORTABLE_ADAPTER_TARGET_REQUIRED", rule_id)
        _require(target == transform["targetRef"], "PORTABLE_ADAPTER_TARGET_MISMATCH", rule_id)
        _require(rule.get("operation") == targets[target]["operation"], "PORTABLE_ADAPTER_OPERATION_MISMATCH", rule_id)
        patch = rule.get("patch")
        _require(isinstance(patch, dict), "PORTABLE_ADAPTER_PATCH_REQUIRED", rule_id)
        _require(set(patch) <= {"addEntities", "addProjections"}, "PORTABLE_ADAPTER_PATCH_FIELD_UNSUPPORTED", rule_id)
        _require(isinstance(patch.get("addEntities", []), list), "PORTABLE_ADAPTER_PATCH_ENTITIES_INVALID", rule_id)
        _require(isinstance(patch.get("addProjections", []), list), "PORTABLE_ADAPTER_PATCH_PROJECTIONS_INVALID", rule_id)
        _require(bool(patch.get("addEntities") or patch.get("addProjections")), "PORTABLE_ADAPTER_PATCH_EMPTY", rule_id)
    return deepcopy(adapter)


def validate_package(package: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(package, dict), "PORTABLE_PACKAGE_REQUIRED")
    _scan_data(package)
    expected = {
        "schemaVersion": PACKAGE_SCHEMA,
        "packageVersion": PACKAGE_VERSION,
        "componentApiVersion": COMPONENT_API_VERSION,
        "transformationIrVersion": TRANSFORMATION_IR_VERSION,
        "adapterApiVersion": ADAPTER_API_VERSION,
        "scenePackageVersion": SCENE_PACKAGE_VERSION,
    }
    for key, value in expected.items():
        _require(package.get(key) == value, f"PORTABLE_{key.upper()}_MISMATCH", str(package.get(key)))
    _text(package.get("id"), "PORTABLE_PACKAGE_ID_REQUIRED")
    _text(package.get("title"), "PORTABLE_PACKAGE_TITLE_REQUIRED")
    for field in ("sourceRefs", "sceneRefs", "representationRefs", "assetRefs", "accessibilityRefs"):
        _string_list(package.get(field), f"PORTABLE_{field.upper()}_INVALID")
    _require(isinstance(package.get("questionBindings"), list), "PORTABLE_QUESTION_BINDINGS_INVALID")
    provenance = package.get("provenance")
    _require(isinstance(provenance, dict), "PORTABLE_PROVENANCE_REQUIRED")
    _require(provenance.get("authority") == "NON_CANONICAL_COMPILED_PROOF", "PORTABLE_PROVENANCE_AUTHORITY_INVALID")
    scene = _validate_scene(package.get("scene"))
    _require(package["sceneRefs"] == [scene["id"]], "PORTABLE_SCENE_REFS_MISMATCH")
    _validate_adapter(package.get("adapter"), scene)
    _require(isinstance(package.get("injections"), list), "PORTABLE_INJECTIONS_INVALID")
    return deepcopy(package)


def build_package(source: dict[str, Any], scene: dict[str, Any]) -> dict[str, Any]:
    package = {
        "schemaVersion": PACKAGE_SCHEMA,
        "packageVersion": PACKAGE_VERSION,
        "componentApiVersion": COMPONENT_API_VERSION,
        "transformationIrVersion": TRANSFORMATION_IR_VERSION,
        "adapterApiVersion": ADAPTER_API_VERSION,
        "scenePackageVersion": SCENE_PACKAGE_VERSION,
        "id": source["id"],
        "title": source["title"],
        "sourceRefs": list(source.get("sourceRefs") or []),
        "sceneRefs": [scene["id"]],
        "representationRefs": list(source.get("representationRefs") or []),
        "assetRefs": list(source.get("assetRefs") or []),
        "accessibilityRefs": list(source.get("accessibilityRefs") or []),
        "questionBindings": deepcopy(source.get("questionBindings") or []),
        "provenance": {
            "authority": "NON_CANONICAL_COMPILED_PROOF",
            "sourceKind": source.get("sourceKind", "COMPILED_PROOF_FIXTURE"),
            "sourceRefs": list(source.get("sourceRefs") or []),
        },
        "scene": deepcopy(scene),
        "adapter": {
            "id": DECLARATIVE_ADAPTER_ID,
            "apiVersion": ADAPTER_API_VERSION,
            "rules": deepcopy(source["adapterRules"]),
        },
        "injections": deepcopy(source.get("injections") or []),
    }
    return validate_package(package)
