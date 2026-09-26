#!/usr/bin/env python3
"""Resolve a webpage request from exact canonical identity, AtlasIndex 2.0, and provider-owned delivery contracts."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
REQUEST_SCHEMA = REPO / "Shared/library/web-request.schema.json"
PLAN_SCHEMA = REPO / "Shared/library/web-resolution-plan.schema.json"
EXPLORER_REGISTRY = REPO / "Shared/web/explorer-profiles.v1.json"
TARGET_ROUTING_CONTRACT_VERSION = "1.1.0"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load
from Shared.library.resolve import build_index, load_packages
from Shared.tools import (build_core_learning_data, build_web_data, derived_artifact_registry,
                          renderer_registry, target_demand_routing_contract)


READY = "READY"
UNAVAILABLE = "UNAVAILABLE"
INVALID = "INVALID"
RESEARCH_AND_AUTHOR = "RESEARCH_AND_AUTHOR"


class WebResolutionError(ValueError):
    pass


def _finding(code: str, detail: str, ref: str | None = None) -> dict[str, Any]:
    row: dict[str, Any] = {"code": code, "detail": detail}
    if ref:
        row["ref"] = ref
    return row


def _schema_findings(value: dict, path: Path, code: str) -> list[dict[str, Any]]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(path)
    return [
        _finding(code, error.message, "/".join(str(part) for part in error.path))
        for error in jsonschema.Draft202012Validator(schema).iter_errors(value)
    ]


def _subject_records(subject: str, repo: Path) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    if not paths:
        return {}
    return build_index(load_packages(paths))


def _matrix_rows(entry: dict, matrix_id: str) -> list[dict]:
    return [
        row for row in entry.get("atlas_index", [])
        if row.get("matrix_id") == matrix_id
    ]


def _matrix_bucket(entry: dict, matrix_id: str) -> str | None:
    matches = [
        row.get("bucket_id")
        for row in entry.get("matrices", [])
        if row.get("matrix_id") == matrix_id
    ]
    unique = {value for value in matches if isinstance(value, str) and value}
    return next(iter(unique)) if len(unique) == 1 else None


def _question_rows(entry: dict, question_ref: str) -> list[dict]:
    keys = []
    for matrix in entry.get("matrices", []):
        for rung in matrix.get("rungs", []):
            if any(q.get("id") == question_ref for q in rung.get("questions", [])):
                keys.append((matrix.get("matrix_id"), rung.get("rung")))
    return [
        row for row in entry.get("atlas_index", [])
        if (row.get("matrix_id"), row.get("rung")) in keys
    ]


def _direct_exact_rows(entry: dict, exact_ref: str) -> list[dict]:
    rows = []
    for row in entry.get("atlas_index", []):
        refs = {
            row.get("microtopic_ref"),
            row.get("capability_ref"),
            *(row.get("representation_refs") or []),
            *(row.get("activity_refs") or []),
            *(row.get("core_projection_refs") or []),
        }
        if exact_ref in refs:
            rows.append(row)
    rows.extend(_question_rows(entry, exact_ref))
    unique = {}
    for row in rows:
        unique[(row.get("matrix_id"), row.get("rung"))] = row
    return list(unique.values())


def _aggregate_status(rows: list[dict], dimension: str) -> str:
    states = [
        (row.get("availability") or {}).get(dimension)
        for row in rows
        if (row.get("availability") or {}).get(dimension)
    ]
    if INVALID in states:
        return INVALID
    if READY in states:
        return READY
    if states:
        return UNAVAILABLE
    return UNAVAILABLE


def _add_unique(target: list[str], values: list[str] | tuple[str, ...]) -> None:
    for value in values:
        if isinstance(value, str) and value and value not in target:
            target.append(value)


def _resolved_refs(
    *,
    entry: dict,
    records: dict[str, dict],
    rows: list[dict],
    exact_ref: str | None,
) -> dict[str, list[str]]:
    refs = {
        "bucket_refs": [],
        "microtopic_refs": [],
        "capability_refs": [],
        "question_refs": [],
        "family_refs": [],
        "representation_refs": [],
        "activity_refs": [],
        "core_projection_refs": [],
        "microtopic_prerequisite_refs": [],
        "capability_prerequisite_refs": [],
    }
    for row in rows:
        bucket = _matrix_bucket(entry, row.get("matrix_id"))
        _add_unique(refs["bucket_refs"], [bucket] if bucket else [])
        _add_unique(refs["microtopic_refs"], [row.get("microtopic_ref")])
        _add_unique(refs["capability_refs"], [row.get("capability_ref")])
        _add_unique(refs["representation_refs"], row.get("representation_refs") or [])
        _add_unique(refs["activity_refs"], row.get("activity_refs") or [])
        _add_unique(refs["core_projection_refs"], row.get("core_projection_refs") or [])
        _add_unique(refs["microtopic_prerequisite_refs"], row.get("microtopic_prerequisite_refs") or [])
        _add_unique(refs["capability_prerequisite_refs"], row.get("capability_prerequisite_refs") or [])

    direct = records.get(exact_ref) if exact_ref else None
    if isinstance(direct, dict):
        collection = direct.get("_collection")
        if collection == "questions":
            _add_unique(refs["question_refs"], [direct.get("id")])
            _add_unique(refs["family_refs"], [direct.get("family_ref")])
            _add_unique(refs["capability_refs"], [
                direct.get("primary_capability_ref"),
                *(direct.get("secondary_capability_refs") or []),
            ])
            _add_unique(refs["representation_refs"], [
                move.get("representation_ref")
                for move in (direct.get("answer") or {}).get("reasoning_route", [])
                if isinstance(move, dict)
            ])
            _add_unique(refs["representation_refs"], [
                item.get("visual_ref")
                for item in (direct.get("scaffolds") or [])
                if isinstance(item, dict)
            ])
        elif collection == "microtopics":
            _add_unique(refs["microtopic_refs"], [direct.get("id")])
            _add_unique(refs["capability_refs"], [direct.get("primary_capability_ref")])
            _add_unique(refs["representation_refs"], direct.get("representation_refs") or [])
        elif collection == "capabilities":
            _add_unique(refs["capability_refs"], [direct.get("id")])
        elif collection == "representations":
            _add_unique(refs["representation_refs"], [direct.get("id")])
            _add_unique(refs["activity_refs"], direct.get("interactive_resource_refs") or [])
        elif collection == "resources" and "ACTIVITY" in (direct.get("role") or []):
            _add_unique(refs["activity_refs"], [direct.get("id")])
            for record in records.values():
                if (
                    isinstance(record, dict)
                    and record.get("_collection") == "representations"
                    and direct.get("id") in (record.get("interactive_resource_refs") or [])
                ):
                    _add_unique(refs["representation_refs"], [record.get("id")])
        elif collection == "buckets":
            _add_unique(refs["bucket_refs"], [direct.get("id")])

    for representation_ref in list(refs["representation_refs"]):
        representation = records.get(representation_ref) or {}
        _add_unique(refs["activity_refs"], representation.get("interactive_resource_refs") or [])
    return refs


def _target_resolution(
    request: dict,
    entry: dict,
    records: dict[str, dict],
) -> tuple[dict, list[dict], list[dict]]:
    target = request["target"]
    findings: list[dict] = []
    if "exact_ref" in target:
        exact_ref = target["exact_ref"]
        direct = records.get(exact_ref)
        rows = _direct_exact_rows(entry, exact_ref)
        if direct is None:
            findings.append(_finding(
                "WEB_CANONICAL_REF_INVALID",
                "Exact ref does not resolve in canonical subject records.",
                exact_ref,
            ))
        collection = direct.get("_collection") if isinstance(direct, dict) else None
        resolved = {
            "entry_kind": "EXACT_REF",
            "exact_ref": exact_ref,
            "matrix_ref": rows[0].get("matrix_id") if len(rows) == 1 else None,
            "rung": rows[0].get("rung") if len(rows) == 1 else None,
            "canonical_collection": collection,
        }
    else:
        matrix_ref = target["matrix_ref"]
        rung = target["rung"]
        rows = [
            row for row in _matrix_rows(entry, matrix_ref)
            if row.get("rung") == rung
        ]
        if len(rows) != 1:
            findings.append(_finding(
                "WEB_TARGET_UNRESOLVED" if not rows else "WEB_TARGET_AMBIGUOUS",
                "Atlas composite identity must resolve exactly once.",
                f"{matrix_ref}/{rung}",
            ))
        resolved = {
            "entry_kind": "ATLAS_SELECTION",
            "exact_ref": None,
            "matrix_ref": matrix_ref,
            "rung": rung,
            "canonical_collection": None,
        }
    resolved["resolved_refs"] = _resolved_refs(
        entry=entry,
        records=records,
        rows=rows,
        exact_ref=resolved["exact_ref"],
    )
    return resolved, rows, findings


def _route_receipt(
    request: dict,
    route_artifact: dict | None,
    target: dict,
    repo: Path,
) -> tuple[dict | None, list[dict]]:
    if not request["target"].get("preparation_request", False):
        return None, []
    if not isinstance(route_artifact, dict):
        return None, [_finding(
            "WEB_TARGET_ROUTE_REQUIRED",
            "Target-preparation requests require the upstream Target Demand Route artifact.",
        )]
    validation = target_demand_routing_contract.validate_route_artifact(route_artifact, repo=repo)
    if validation:
        return None, [_finding(
            "WEB_TARGET_ROUTE_INVALID",
            "Target Demand Route failed schema/semantic validation: " + "; ".join(validation[:8]),
        )]
    findings = []
    if route_artifact.get("schema_version") != TARGET_ROUTING_CONTRACT_VERSION:
        findings.append(_finding(
            "WEB_TARGET_ROUTE_VERSION_UNSUPPORTED",
            f"Expected Target Demand Route {TARGET_ROUTING_CONTRACT_VERSION}.",
        ))
    if route_artifact.get("subject") != request.get("subject"):
        findings.append(_finding(
            "WEB_TARGET_ROUTE_SUBJECT_MISMATCH",
            "Target Demand Route subject differs from the web request.",
        ))
    exact_ref = target.get("exact_ref")
    candidates = []
    for row in route_artifact.get("targets", []):
        identity = row.get("identity") or {}
        if exact_ref and exact_ref in {
            row.get("target_id"), row.get("owner_ref"), identity.get("exact_ref")
        }:
            candidates.append(row)
    if len(candidates) != 1:
        findings.append(_finding(
            "WEB_TARGET_ROUTE_TARGET_UNRESOLVED",
            "The Target Demand Route must contain exactly one matching requested target.",
            exact_ref,
        ))
        return None, findings
    row = candidates[0]
    identity = row.get("identity") or {}
    if exact_ref and identity.get("exact_ref") != exact_ref:
        findings.append(_finding(
            "WEB_TARGET_ROUTE_IDENTITY_MISMATCH",
            "The route identity must name the requested exact canonical ref.",
            exact_ref,
        ))
    if not any(
        node.get("kind") == "TARGET"
        and node.get("ref") in {row.get("target_id"), exact_ref}
        for node in row.get("target_route") or []
    ):
        findings.append(_finding(
            "WEB_TARGET_ROUTE_TERMINAL_MISSING",
            "A prepared target requires an explicit matching TARGET step.",
            exact_ref,
        ))
    requested_cores = {
        segment.get("core") for segment in request["experience_segments"]
        if segment.get("core")
    }
    route_cores = {
        node.get("kind") for node in row.get("target_route") or []
    }
    if requested_cores - route_cores:
        findings.append(_finding(
            "WEB_TARGET_ROUTE_CORE_MISMATCH",
            "The requested Core must be a step in the reviewed target route.",
            exact_ref,
        ))
    if row.get("preparation_state") != "PREPARED":
        findings.append(_finding(
            "WEB_TARGET_NOT_PREPARED",
            "Blocked or partial Target Demand routes cannot satisfy fixed-target webpage preparation.",
            row.get("target_id"),
        ))
    if row.get("coverage_state") != "INDEPENDENT_EVIDENCE_COMPLETE":
        findings.append(_finding(
            "WEB_TARGET_COVERAGE_INCOMPLETE",
            "Target preparation lacks independent evidence coverage.",
            row.get("target_id"),
        ))
    if row.get("authorization_state") != "READY":
        findings.append(_finding(
            "WEB_TARGET_AUTHORIZATION_MISSING",
            "Target preparation is not yet academically authorized; complete and record the authorization evidence.",
            row.get("target_id"),
        ))
    return {
        "route_bundle_id": route_artifact.get("route_bundle_id"),
        "target_id": row.get("target_id"),
        "coverage_state": row.get("coverage_state"),
        "authorization_state": row.get("authorization_state"),
        "preparation_state": row.get("preparation_state"),
        "demand_move_refs": [move["move_id"] for move in row.get("demand_moves") or []],
        "route_steps": row.get("target_route") or [],
        "contract_path": "Shared/library/target-demand-route.schema.json",
        "contract_version": TARGET_ROUTING_CONTRACT_VERSION,
    }, findings


def _dimension(requirement: str, status: str, refs: list[str], detail: str | None = None) -> dict:
    return {
        "requirement": requirement,
        "status": status if requirement != "NOT_REQUIRED" else "NOT_REQUIRED",
        "refs": refs,
        "detail": detail,
    }


def _representation_kind(records: dict[str, dict], refs: list[str]) -> str | None:
    kinds = {
        records.get(ref, {}).get("kind")
        for ref in refs
        if (records.get(ref) or {}).get("_collection") == "representations"
    }
    kinds.discard(None)
    return next(iter(kinds)) if len(kinds) == 1 else None


def _activity_delivery(entry: dict, refs: list[str], packaging_mode: str) -> tuple[bool, bool]:
    targets = entry.get("visual_targets") or {}
    ready = [
        targets.get(ref) or {}
        for ref in refs
        if (targets.get(ref) or {}).get("availability", {}).get("resource") == READY
    ]
    locator_ready = any(row.get("availability", {}).get("locator") == READY for row in ready)
    portable_ready = any(row.get("availability", {}).get("portable_package") == READY for row in ready)
    if packaging_mode in {"OFFLINE_DIRECTORY", "SINGLE_FILE"}:
        return portable_ready, portable_ready
    return locator_ready or portable_ready, True


def _core_segment(
    *,
    segment: dict,
    request: dict,
    target: dict,
    core_payload: dict,
) -> tuple[dict, list[dict]]:
    refs = []
    for values in target["resolved_refs"].values():
        _add_unique(refs, values)
    if target.get("exact_ref"):
        _add_unique(refs, [target["exact_ref"]])
    remembered = []
    for ref in refs:
        remembered = derived_artifact_registry.search(
            subject=request["subject"],
            core=segment["core"],
            artifact_type="CORE_PROJECTION",
            exact_ref=ref,
        )
        remembered = [item for item in remembered if item.get("reuse") == "DIRECT"]
        if remembered:
            break
    preflight = build_core_learning_data.preflight_projection(
        subject=request["subject"],
        core=segment["core"],
        target_refs=refs,
        payload=core_payload,
    )
    row = {
        **segment,
        "provider_status": preflight["status"],
        "projection_ref": preflight.get("projection_ref"),
        "remembered_artifact_ref": remembered[0]["artifact_ref"] if remembered else None,
        "remembered_reuse": remembered[0]["reuse"] if remembered else None,
    }
    findings = []
    if preflight["status"] != "READY_EXISTING":
        findings.append(_finding(
            "WEB_CORE_SEMANTICS_UNAVAILABLE",
            preflight.get("detail") or "Core provider did not authorize a projection.",
            segment["core"],
        ))
    return row, findings


def resolve(
    request: dict,
    *,
    route_artifact: dict | None = None,
    repo: Path = REPO,
) -> dict:
    input_findings = _schema_findings(request, repo / REQUEST_SCHEMA.relative_to(REPO), "WEB_REQUEST_STRUCTURE")
    if input_findings:
        return {
            "schema_version": "1.0.0",
            "request_id": request.get("request_id", "INVALID"),
            "subject": request.get("subject", ""),
            "target": {
                "entry_kind": "EXACT_REF",
                "exact_ref": None, "matrix_ref": None, "rung": None,
                "canonical_collection": None, "resolved_refs": {},
            },
            "experience_segments": [],
            "availability": {
                key: _dimension("NOT_REQUIRED", "NOT_REQUIRED", [])
                for key in ("mapping","core","representation","activity","locator","portable_package","standalone","renderer")
            },
            "artifact_buildable": False,
            "request_satisfaction": "RESEARCH_AND_AUTHOR",
            "build_action": "AUTHOR_MISSING_INPUTS",
            "pins": {
                "atlas_index_contract_version": "2.0",
                "core_provider_contract_version": "1.1",
                "target_routing_contract_version": None,
                "explorer_profile_registry_version": "1.0.0",
                "renderer_registry_version": renderer_registry.CONTRACT_VERSION,
            },
            "target_route": None,
            "packaging_mode": request.get("packaging_mode", "PUBLIC"),
            "fallback_used": [],
            "findings": input_findings,
        }

    subject = request["subject"]
    records = _subject_records(subject, repo)
    web_payload = build_web_data.build()
    entry = (web_payload.get("subjects") or {}).get(subject)
    findings: list[dict] = []
    if not records or not isinstance(entry, dict):
        findings.append(_finding(
            "WEB_SUBJECT_UNAVAILABLE",
            "Subject has no canonical library/web-data projection.",
            subject,
        ))
        entry = {"atlas_index": [], "matrices": [], "visual_targets": {}}

    target, atlas_rows, target_findings = _target_resolution(request, entry, records)
    findings.extend(target_findings)
    route_receipt, route_findings = _route_receipt(request, route_artifact, target, repo)
    findings.extend(route_findings)

    refs = target["resolved_refs"]
    core_payload = build_core_learning_data.build()
    resolved_segments = []
    core_findings = []
    for segment in request["experience_segments"]:
        if segment["mode"] == "EXPLORE":
            resolved_segments.append({**segment, "profile_ref": next((row.get("ref") for row in load(repo / EXPLORER_REGISTRY.relative_to(REPO)).get("profiles", []) if row.get("profile_kind") == "EXPLORE"), None)})
        else:
            resolved, segment_findings = _core_segment(
                segment=segment,
                request=request,
                target=target,
                core_payload=core_payload,
            )
            resolved_segments.append(resolved)
            core_findings.extend(segment_findings)
    findings.extend(core_findings)

    has_core = any(row["mode"] != "EXPLORE" for row in resolved_segments)
    has_explore = any(row["mode"] == "EXPLORE" for row in resolved_segments)
    interaction_requirement = max(
        (row["interaction_requirement"] for row in resolved_segments),
        key={"OPTIONAL": 0, "PREFERRED": 1, "REQUIRED": 2}.get,
    )

    mapping_status = _aggregate_status(atlas_rows, "mapping") if atlas_rows else (
        READY if target.get("canonical_collection") else UNAVAILABLE
    )
    representation_status = _aggregate_status(atlas_rows, "representation") if atlas_rows else (
        READY if refs["representation_refs"] else UNAVAILABLE
    )
    activity_status = _aggregate_status(atlas_rows, "activity") if atlas_rows else (
        READY if refs["activity_refs"] else UNAVAILABLE
    )
    locator_status = _aggregate_status(atlas_rows, "locator") if atlas_rows else UNAVAILABLE
    portable_status = _aggregate_status(atlas_rows, "portable_package") if atlas_rows else UNAVAILABLE
    standalone_status = _aggregate_status(atlas_rows, "standalone") if atlas_rows else UNAVAILABLE

    activity_usable, activity_package_ok = _activity_delivery(
        entry, refs["activity_refs"], request["packaging_mode"]
    )
    representation_kind = _representation_kind(records, refs["representation_refs"])
    renderer = renderer_registry.resolve(
        subject,
        representation_kind,
        interaction_requirement=interaction_requirement,
        repo=repo,
    )
    renderer_status = renderer["status"]

    core_ready = all(
        row.get("provider_status") == "READY_EXISTING"
        for row in resolved_segments
        if row["mode"] != "EXPLORE"
    )
    core_requirement = "REQUIRED" if has_core else "NOT_REQUIRED"

    explicit_visual_required = False
    for segment in resolved_segments:
        if segment.get("projection_ref"):
            provider_row = next(
                (row for row in core_payload["core_projections"] if row["id"] == segment["projection_ref"]),
                None,
            )
            projection = (provider_row or {}).get("projection") or {}
            concept = projection.get("concept") or {}
            presentation = projection.get("presentation") or {}
            if presentation.get("initial_visual_ref") or concept.get("representation_refs"):
                explicit_visual_required = True

    if has_explore:
        representation_requirement = "OPTIONAL" if activity_usable else "REQUIRED"
        activity_requirement = "REQUIRED" if interaction_requirement == "REQUIRED" else "OPTIONAL"
    else:
        representation_requirement = "REQUIRED" if explicit_visual_required else "OPTIONAL"
        activity_requirement = "OPTIONAL" if interaction_requirement != "REQUIRED" else "REQUIRED"

    if not refs["representation_refs"] and representation_requirement == "OPTIONAL":
        representation_requirement = "NOT_REQUIRED"
    if not refs["activity_refs"] and activity_requirement == "OPTIONAL":
        activity_requirement = "NOT_REQUIRED"

    interactive_ready = activity_usable
    static_ready = representation_status == READY and renderer_status == READY
    core_buildable = (not has_core) or core_ready
    explore_buildable = (not has_explore) or activity_usable or static_ready
    canonical_refs_valid = all(
        (records.get(ref) or {}).get("_collection") == collection
        for key, collection in (
            ("microtopic_refs", "microtopics"),
            ("capability_refs", "capabilities"),
            ("representation_refs", "representations"),
            ("activity_refs", "resources"),
        )
        for ref in refs[key]
    )
    if mapping_status != READY:
        findings.append(_finding(
            "WEB_ATLAS_CANONICAL_DIVERGENCE",
            "Selected Atlas mapping is not canonically verified as READY.",
        ))
    if not canonical_refs_valid:
        findings.append(_finding(
            "WEB_CANONICAL_REF_INVALID",
            "One or more Atlas references cannot be verified in canonical subject records.",
        ))
    artifact_buildable = (
        not findings
        and core_buildable
        and explore_buildable
    )

    fallback_used: list[str] = []
    if has_explore and not activity_usable and static_ready:
        fallback_used.append("STATIC_RENDERER_INSTEAD_OF_INTERACTIVE_ACTIVITY")

    if any(row["code"].startswith("WEB_TARGET_ROUTE") or row["code"].startswith("WEB_TARGET_") and row["code"] in {
        "WEB_TARGET_NOT_PREPARED","WEB_TARGET_COVERAGE_INCOMPLETE","WEB_TARGET_AUTHORIZATION_MISSING"
    } for row in findings):
        satisfaction = RESEARCH_AND_AUTHOR
    elif interaction_requirement == "REQUIRED" and not interactive_ready:
        satisfaction = RESEARCH_AND_AUTHOR
        findings.append(_finding(
            "WEB_REQUIRED_INTERACTION_UNAVAILABLE",
            "The requested interaction is REQUIRED and not yet authored; author the interactive activity, then resolve again.",
        ))
    elif interaction_requirement == "PREFERRED" and not interactive_ready and artifact_buildable:
        # Build the static page now; authoring the preferred interaction is the next duty.
        satisfaction = "DEGRADED_ACCEPTABLE"
    elif fallback_used:
        satisfaction = "DEGRADED_ACCEPTABLE"
    elif artifact_buildable:
        satisfaction = "FULL"
    else:
        satisfaction = RESEARCH_AND_AUTHOR

    if not artifact_buildable:
        satisfaction = RESEARCH_AND_AUTHOR

    if satisfaction == RESEARCH_AND_AUTHOR:
        # The findings name what to research or author before the page can be built.
        build_action = "AUTHOR_MISSING_INPUTS"
    elif len(resolved_segments) > 1:
        build_action = "COMPOSE_SEGMENTS"
    elif has_explore:
        build_action = "EXPLORE_PAGE_ADAPTER"
    else:
        build_action = "CORE_PAGE_ADAPTER"

    availability = {
        "mapping": _dimension("REQUIRED", mapping_status, []),
        "core": _dimension(
            core_requirement,
            READY if core_ready and has_core else UNAVAILABLE,
            [row.get("projection_ref") for row in resolved_segments if row.get("projection_ref")],
        ),
        "representation": _dimension(
            representation_requirement,
            representation_status,
            refs["representation_refs"],
        ),
        "activity": _dimension(
            activity_requirement,
            READY if activity_usable else activity_status,
            refs["activity_refs"],
            None if activity_package_ok else "Requested packaging requires a released portable activity package.",
        ),
        "locator": _dimension(
            "OPTIONAL" if refs["activity_refs"] else "NOT_REQUIRED",
            locator_status,
            refs["activity_refs"],
        ),
        "portable_package": _dimension(
            "REQUIRED" if request["packaging_mode"] in {"OFFLINE_DIRECTORY","SINGLE_FILE"} and interaction_requirement == "REQUIRED" else "OPTIONAL",
            portable_status,
            refs["activity_refs"],
        ),
        "standalone": _dimension(
            "OPTIONAL" if refs["activity_refs"] else "NOT_REQUIRED",
            standalone_status,
            refs["activity_refs"],
        ),
        "renderer": _dimension(
            "OPTIONAL" if refs["representation_refs"] else "NOT_REQUIRED",
            renderer_status,
            [renderer["renderer"]["renderer_id"]] if renderer.get("renderer") else [],
        ),
    }

    registry = load(repo / EXPLORER_REGISTRY.relative_to(REPO))
    plan = {
        "schema_version": "1.0.0",
        "request_id": request["request_id"],
        "subject": subject,
        "target": target,
        "experience_segments": resolved_segments,
        "availability": availability,
        "artifact_buildable": artifact_buildable,
        "request_satisfaction": satisfaction,
        "build_action": build_action,
        "pins": {
            "atlas_index_contract_version": (
                (entry.get("atlas_index_contract_version") or "2.0")
            ),
            "core_provider_contract_version": (
                (core_payload.get("provider") or {}).get("contract_version") or "1.1"
            ),
            "target_routing_contract_version": (
                TARGET_ROUTING_CONTRACT_VERSION if request["target"].get("preparation_request") else None
            ),
            "explorer_profile_registry_version": registry.get("registry_version") or "1.0.0",
            "renderer_registry_version": renderer_registry.CONTRACT_VERSION,
        },
        "target_route": route_receipt,
        "packaging_mode": request["packaging_mode"],
        "fallback_used": fallback_used,
        "findings": findings,
    }
    plan_findings = _schema_findings(
        plan,
        repo / PLAN_SCHEMA.relative_to(REPO),
        "WEB_RESOLUTION_PLAN_STRUCTURE",
    )
    if plan_findings:
        plan["findings"].extend(plan_findings)
        plan["artifact_buildable"] = False
        plan["request_satisfaction"] = RESEARCH_AND_AUTHOR
        plan["build_action"] = "AUTHOR_MISSING_INPUTS"
    return plan


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path, required=True)
    parser.add_argument("--route-artifact", type=Path)
    parser.add_argument("--out", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    request = load(args.request)
    route = load(args.route_artifact) if args.route_artifact else None
    plan = resolve(request, route_artifact=route)
    body = json.dumps(plan, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(body, encoding="utf-8")
    else:
        print(body, end="")
    return 1 if args.enforce and plan["request_satisfaction"] == RESEARCH_AND_AUTHOR else 0


if __name__ == "__main__":
    raise SystemExit(main())
