#!/usr/bin/env python3
"""Subject-neutral canonical Atlas reference index for Issue #212.

This module is a derived read model only. It never authors curriculum relationships:
every emitted edge comes from an explicit matrix/library/Core field, and every broken
declared edge remains visible as a finding rather than being repaired by similarity.
"""
from __future__ import annotations

from collections import Counter, defaultdict
from typing import Iterable

CONTRACT_VERSION = "2.0"
READY = "READY"
UNAVAILABLE = "UNAVAILABLE"
INVALID = "INVALID"


def _finding(code: str, ref: str | None, detail: str) -> dict:
    return {"code": code, "ref": ref, "detail": detail}


def _ordered_unique(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        if value and value not in seen:
            seen.add(value)
            out.append(value)
    return out


def _record_is(records: dict, ref: str, collection: str) -> bool:
    row = records.get(ref)
    return isinstance(row, dict) and row.get("_collection") == collection


def _core_maps(core_payload: dict, subject: str) -> tuple[dict, dict, dict]:
    availability = {
        row["bucket_ref"]: row
        for row in core_payload.get("bucket_availability", [])
        if row.get("subject") == subject
    }
    by_id = {
        row["id"]: row
        for row in core_payload.get("core_projections", [])
        if row.get("subject") == subject and row.get("id")
    }
    by_microtopic: dict[str, list[str]] = defaultdict(list)
    for ref, row in by_id.items():
        projection = row.get("projection") or {}
        concept = projection.get("concept") or {}
        microtopic_ref = concept.get("microtopic_ref")
        if microtopic_ref:
            by_microtopic[microtopic_ref].append(ref)
    for refs in by_microtopic.values():
        refs.sort()
    return availability, by_id, by_microtopic


def _representation_activity_refs(
    representation_refs: list[str],
    records: dict,
) -> tuple[list[str], list[dict]]:
    refs: list[str] = []
    provenance: list[dict] = []
    for representation_ref in representation_refs:
        representation = records.get(representation_ref)
        if not isinstance(representation, dict):
            continue
        for resource_ref in representation.get("interactive_resource_refs", []):
            refs.append(resource_ref)
            provenance.append({
                "resource_ref": resource_ref,
                "asserted_by": {
                    "record_ref": representation_ref,
                    "field": "interactive_resource_refs",
                },
            })
    return _ordered_unique(refs), provenance


def _capability_activity_refs(capability_ref: str | None, records: dict) -> tuple[list[str], list[dict]]:
    if not capability_ref:
        return [], []
    refs = sorted(
        row["id"]
        for row in records.values()
        if isinstance(row, dict)
        and row.get("_collection") == "resources"
        and "ACTIVITY" in row.get("role", [])
        and capability_ref in row.get("supports_claims", [])
    )
    return refs, [
        {
            "resource_ref": ref,
            "asserted_by": {
                "record_ref": ref,
                "field": "supports_claims",
                "value": capability_ref,
            },
        }
        for ref in refs
    ]


def _delivery_profile(resource: dict | None) -> str | None:
    if not isinstance(resource, dict):
        return None
    topic_atlas = resource.get("extensions", {}).get("topic_atlas", {})
    gcdr = topic_atlas.get("gcdr_contract", {})
    return gcdr.get("delivery_profile", {}).get("profile")


def _visual_targets(records: dict) -> dict[str, dict]:
    representation_sources: dict[str, list[str]] = defaultdict(list)
    for row in records.values():
        if not isinstance(row, dict) or row.get("_collection") != "representations":
            continue
        for resource_ref in row.get("interactive_resource_refs", []):
            representation_sources[resource_ref].append(row["id"])

    activity_refs = {
        row["id"]
        for row in records.values()
        if isinstance(row, dict)
        and row.get("_collection") == "resources"
        and "ACTIVITY" in row.get("role", [])
    }
    activity_refs.update(representation_sources)

    targets: dict[str, dict] = {}
    for resource_ref in sorted(activity_refs):
        resource = records.get(resource_ref)
        valid_resource = (
            isinstance(resource, dict)
            and resource.get("_collection") == "resources"
            and "ACTIVITY" in resource.get("role", [])
        )
        locator = resource.get("locator") if valid_resource else None
        profile = _delivery_profile(resource if valid_resource else None)
        targets[resource_ref] = {
            "resource_ref": resource_ref,
            "representation_refs": sorted(set(representation_sources.get(resource_ref, []))),
            "locator": locator,
            "delivery_kind": "EXISTING_ACTIVITY",
            "delivery_profile": profile,
            "portable_package_ref": None,
            "availability": {
                "resource": READY if valid_resource else INVALID,
                "locator": READY if valid_resource and locator else (INVALID if not valid_resource else UNAVAILABLE),
                "portable_package": UNAVAILABLE,
                "standalone": READY if profile == "SINGLE_FILE_OFFLINE" else UNAVAILABLE,
            },
            "provenance": {
                "representation_ref_sources": sorted(set(representation_sources.get(resource_ref, []))),
                "capability_ref_sources": sorted(
                    ref
                    for ref in (resource.get("supports_claims", []) if valid_resource else [])
                    if _record_is(records, ref, "capabilities")
                ),
            },
        }
    return targets


def _availability_counts(rows: list[dict], dimensions: tuple[str, ...]) -> dict:
    return {
        dimension: dict(sorted(Counter(
            row["availability"][dimension] for row in rows
        ).items()))
        for dimension in dimensions
    }


def _coverage(rows: list[dict]) -> dict:
    dimensions = (
        "mapping",
        "core",
        "representation",
        "activity",
        "locator",
        "portable_package",
        "standalone",
    )
    by_matrix: list[dict] = []
    matrix_order = _ordered_unique(row["matrix_id"] for row in rows)
    for matrix_id in matrix_order:
        matrix_rows = [row for row in rows if row["matrix_id"] == matrix_id]
        by_matrix.append({
            "matrix_id": matrix_id,
            "rung_count": len(matrix_rows),
            "availability": _availability_counts(matrix_rows, dimensions),
            "finding_counts": dict(sorted(Counter(
                finding["code"]
                for row in matrix_rows
                for finding in row["findings"]
            ).items())),
        })
    return {
        "rung_count": len(rows),
        "availability": _availability_counts(rows, dimensions),
        "finding_counts": dict(sorted(Counter(
            finding["code"]
            for row in rows
            for finding in row["findings"]
        ).items())),
        "matrices": by_matrix,
    }


def build_subject_index(
    subject: str,
    boards: list[dict],
    records: dict,
    core_payload: dict,
) -> dict:
    """Build a deterministic Atlas index from explicit canonical relationships."""
    core_availability, core_by_id, core_by_microtopic = _core_maps(core_payload, subject)
    teaching_step_ids = {
        step.get("id")
        for record in records.values()
        if isinstance(record, dict) and record.get("_collection") == "microtopics"
        for step in record.get("teaching_path", [])
        if isinstance(step, dict) and step.get("id")
    }
    key_counts = Counter(
        (board.get("matrix_id"), rung.get("rung"))
        for board in boards
        for rung in board.get("rungs", [])
    )

    rows: list[dict] = []
    global_findings: list[dict] = []

    for board in boards:
        matrix_id = board.get("matrix_id")
        bucket_id = board.get("bucket_id")
        for source_rung in board.get("rungs", []):
            rung_label = source_rung.get("rung")
            key = (matrix_id, rung_label)
            findings: list[dict] = []
            mapping_invalid = False

            if key_counts[key] > 1:
                finding = _finding(
                    "ATLAS_DUPLICATE_KEY",
                    f"{matrix_id}/{rung_label}",
                    "Composite (matrix_id, rung) appears more than once; no first-wins resolution is allowed.",
                )
                findings.append(finding)
                global_findings.append(finding)
                mapping_invalid = True

            microtopic_ref = source_rung.get("microtopic_ref")
            mapping_unavailable = not microtopic_ref
            microtopic = records.get(microtopic_ref) if microtopic_ref else None
            if mapping_unavailable:
                findings.append(_finding(
                    "MICROTOPIC_REF_UNAVAILABLE",
                    None,
                    "Matrix rung has no authored microtopic_ref; the mapping is honestly unavailable.",
                ))
            elif not (
                isinstance(microtopic, dict)
                and microtopic.get("_collection") == "microtopics"
            ):
                findings.append(_finding(
                    "MICROTOPIC_REF_UNRESOLVED",
                    microtopic_ref,
                    "Matrix declares a microtopic_ref that does not resolve to a canonical microtopic.",
                ))
                microtopic = None
                mapping_invalid = True

            capability_ref = microtopic.get("primary_capability_ref") if microtopic else None
            capability = records.get(capability_ref) if capability_ref else None
            if microtopic and not (
                isinstance(capability, dict)
                and capability.get("_collection") == "capabilities"
            ):
                findings.append(_finding(
                    "CAPABILITY_REF_UNRESOLVED",
                    capability_ref,
                    "Microtopic primary_capability_ref does not resolve to a canonical capability.",
                ))
                capability = None
                mapping_invalid = True

            teaching_step_refs = [
                step.get("id")
                for step in (microtopic.get("teaching_path", []) if microtopic else [])
                if step.get("id")
            ]
            microtopic_prerequisite_refs = (
                list(microtopic.get("prerequisite_refs", [])) if microtopic else []
            )
            capability_prerequisite_refs = (
                list(capability.get("prerequisite_refs", [])) if capability else []
            )

            for source_name, refs in (
                ("microtopic.prerequisite_refs", microtopic_prerequisite_refs),
                ("capability.prerequisite_refs", capability_prerequisite_refs),
            ):
                for ref in refs:
                    if ref not in records:
                        findings.append(_finding(
                            "PREREQUISITE_REF_UNRESOLVED",
                            ref,
                            f"{source_name} declares a prerequisite that does not resolve.",
                        ))
                        mapping_invalid = True

            representation_refs = (
                list(microtopic.get("representation_refs", [])) if microtopic else []
            )
            representation_invalid = False
            for ref in representation_refs:
                if not _record_is(records, ref, "representations"):
                    findings.append(_finding(
                        "REPRESENTATION_REF_UNRESOLVED",
                        ref,
                        "Microtopic representation_ref does not resolve to a canonical representation.",
                    ))
                    representation_invalid = True
                    mapping_invalid = True

            representation_activity_refs, rep_activity_provenance = _representation_activity_refs(
                representation_refs,
                records,
            )
            capability_activity_refs, capability_activity_provenance = _capability_activity_refs(
                capability_ref,
                records,
            )
            activity_refs = _ordered_unique(
                [*representation_activity_refs, *capability_activity_refs]
            )
            activity_invalid = False
            for ref in activity_refs:
                if not (
                    _record_is(records, ref, "resources")
                    and "ACTIVITY" in records[ref].get("role", [])
                ):
                    findings.append(_finding(
                        "ACTIVITY_REF_UNRESOLVED",
                        ref,
                        "Declared Atlas activity/resource ref does not resolve to an ACTIVITY resource.",
                    ))
                    activity_invalid = True
                    mapping_invalid = True
                    continue

                atlas_extension = records[ref].get("extensions", {}).get("topic_atlas", {})
                for step_ref in atlas_extension.get("teaching_step_refs", []):
                    if step_ref not in teaching_step_ids:
                        findings.append(_finding(
                            "ACTIVITY_TEACHING_STEP_REF_UNRESOLVED",
                            step_ref,
                            f"ACTIVITY {ref} declares a teaching_step_ref that does not resolve.",
                        ))
                        activity_invalid = True
                        mapping_invalid = True

            core_projection_refs: list[str] = []
            bucket_core = core_availability.get(bucket_id)
            if mapping_invalid:
                core_status = INVALID
                findings.append(_finding(
                    "CORE_PROJECTION_UNAVAILABLE",
                    None,
                    "Cannot resolve rung-level Core projections while its microtopic mapping is invalid.",
                ))
            elif microtopic is None:
                core_status = UNAVAILABLE
                findings.append(_finding(
                    "CORE_PROJECTION_UNAVAILABLE",
                    None,
                    "No Core projection can be bound because this rung has no authored microtopic_ref.",
                ))
            elif bucket_core is None:
                core_status = INVALID
                findings.append(_finding(
                    "CORE_PROJECTION_UNAVAILABLE",
                    bucket_id,
                    "No Issue #211 bucket availability record exists for the matrix bucket.",
                ))
            elif bucket_core.get("status") == "UNSUPPORTED":
                core_status = UNAVAILABLE
                findings.append(_finding(
                    "CORE_PROJECTION_UNAVAILABLE",
                    bucket_id,
                    f"{bucket_core.get('code')}: {bucket_core.get('detail')}",
                ))
            else:
                core_projection_refs = list(core_by_microtopic.get(microtopic_ref, []))
                declared_bucket_refs = set(bucket_core.get("projection_refs", []))
                broken_core = [
                    ref
                    for ref in core_projection_refs
                    if ref not in core_by_id or ref not in declared_bucket_refs
                ]
                if broken_core:
                    core_status = INVALID
                    for ref in broken_core:
                        findings.append(_finding(
                            "CORE_PROJECTION_REF_CONFLICT",
                            ref,
                            "Rung projection exists but conflicts with Issue #211 bucket availability.",
                        ))
                elif core_projection_refs:
                    core_status = READY
                else:
                    core_status = UNAVAILABLE
                    findings.append(_finding(
                        "CORE_PROJECTION_UNAVAILABLE",
                        microtopic_ref,
                        "Issue #211 bucket is available but no Core projection is explicitly bound to this microtopic.",
                    ))

            representation_status = (
                INVALID if representation_invalid
                else READY if representation_refs
                else UNAVAILABLE
            )
            activity_status = (
                INVALID if activity_invalid
                else READY if activity_refs
                else UNAVAILABLE
            )
            if not activity_refs:
                locator_status = UNAVAILABLE
            elif activity_invalid:
                locator_status = INVALID
            else:
                missing_locator = [
                    ref for ref in activity_refs if not records[ref].get("locator")
                ]
                locator_status = INVALID if missing_locator else READY
                for ref in missing_locator:
                    findings.append(_finding(
                        "ACTIVITY_LOCATOR_UNAVAILABLE",
                        ref,
                        "ACTIVITY resource has no browser/repository locator.",
                    ))

            portable_status = UNAVAILABLE
            profiles = [
                _delivery_profile(records.get(ref))
                for ref in activity_refs
                if _record_is(records, ref, "resources")
            ]
            standalone_status = READY if "SINGLE_FILE_OFFLINE" in profiles else UNAVAILABLE

            if representation_status == UNAVAILABLE and activity_status == UNAVAILABLE:
                findings.append(_finding(
                    "VISUAL_REF_UNAVAILABLE",
                    None,
                    "No canonical representation or activity/resource link is authored for this rung.",
                ))

            row = {
                "matrix_id": matrix_id,
                "rung": rung_label,
                "ladder_position": source_rung.get("ladder_position"),
                "default_entry_eligible": source_rung.get("default_entry_eligible", True),
                "microtopic_ref": microtopic_ref,
                "capability_ref": capability_ref,
                "teaching_step_refs": teaching_step_refs,
                "microtopic_prerequisite_refs": microtopic_prerequisite_refs,
                "capability_prerequisite_refs": capability_prerequisite_refs,
                "representation_refs": representation_refs,
                "activity_refs": activity_refs,
                "core_projection_refs": core_projection_refs,
                "core_availability": {
                    "status": bucket_core.get("status") if bucket_core else "UNKNOWN",
                    "code": bucket_core.get("code") if bucket_core else None,
                    "detail": bucket_core.get("detail") if bucket_core else None,
                },
                "availability": {
                    "mapping": (
                        INVALID if mapping_invalid
                        else UNAVAILABLE if mapping_unavailable
                        else READY
                    ),
                    "core": core_status,
                    "representation": representation_status,
                    "activity": activity_status,
                    "locator": locator_status,
                    "portable_package": portable_status,
                    "standalone": standalone_status,
                },
                "provenance": {
                    "microtopic_ref": {
                        "record_ref": f"{matrix_id}/{rung_label}",
                        "field": "microtopic_ref",
                    },
                    "capability_ref": {
                        "record_ref": microtopic_ref,
                        "field": "primary_capability_ref",
                    } if microtopic_ref else None,
                    "microtopic_prerequisite_refs": {
                        "record_ref": microtopic_ref,
                        "field": "prerequisite_refs",
                    } if microtopic_ref else None,
                    "capability_prerequisite_refs": {
                        "record_ref": capability_ref,
                        "field": "prerequisite_refs",
                    } if capability_ref else None,
                    "representation_refs": {
                        "record_ref": microtopic_ref,
                        "field": "representation_refs",
                    } if microtopic_ref else None,
                    "activity_refs": [
                        *rep_activity_provenance,
                        *capability_activity_provenance,
                    ],
                },
                "findings": findings,
            }
            rows.append(row)
            global_findings.extend(findings)

    # Keep global findings deterministic and avoid repeated summaries.
    deduped_global: list[dict] = []
    seen_global: set[tuple] = set()
    for finding in global_findings:
        key = (finding["code"], finding["ref"], finding["detail"])
        if key not in seen_global:
            seen_global.add(key)
            deduped_global.append(finding)

    return {
        "atlas_index_contract_version": CONTRACT_VERSION,
        "atlas_index": rows,
        "visual_targets": _visual_targets(records),
        "findings": deduped_global,
        "coverage": _coverage(rows),
    }
