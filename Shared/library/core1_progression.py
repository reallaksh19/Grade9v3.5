"""Phase-4 cross-Core1 conceptual-progression inventory and forward gate.

This audit composes the Phase-1/2/3 evidence without collapsing their responsibilities:
Core1 maps the bucket, Core1A constructs the canonical inferential jump, and Core1B
elicits reconstruction of that same jump. Local construction debt remains local debt;
cross-Core findings are reserved for progression/ownership failures.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from Shared.library import (
    core1_orientation,
    core1a_construction,
    core1b_reconstruction,
)


def _finding(code: str, detail: str, ref: str | None = None) -> dict:
    row = {"code": code, "detail": detail}
    if ref:
        row["ref"] = ref
    return row


def _canonical_microtopics(repo: Path) -> tuple[dict[str, dict], dict[str, str], list[dict]]:
    microtopics: dict[str, dict] = {}
    subjects: dict[str, str] = {}
    route_rows: list[dict] = []
    for subject, path, package in core1_orientation.subject_packages(repo):
        for row in package.get("microtopics", []) or []:
            if not isinstance(row, dict) or not isinstance(row.get("id"), str):
                continue
            microtopics[row["id"]] = row
            subjects[row["id"]] = subject
        for route in package.get("teaching_routes", []) or []:
            if isinstance(route, dict):
                route_rows.append({
                    "subject": subject,
                    "package_path": str(path.relative_to(repo)),
                    "id": route.get("id"),
                    "cores": list(route.get("cores") or []),
                    "microtopic_refs": list(route.get("microtopic_refs") or []),
                })
    return microtopics, subjects, route_rows


def progression_row(
    microtopic: dict,
    *,
    subject: str,
    orientation: dict | None,
    construction: dict | None,
    reconstruction: dict | None,
) -> dict:
    ref = microtopic.get("id")
    findings: list[dict] = []
    routing_state = (
        reconstruction.get("routing_state")
        if isinstance(reconstruction, dict)
        else "UNOBSERVED"
    )

    if routing_state == "UNROUTED":
        findings.append(_finding(
            "CROSS_CORE_ROUTING_UNRESOLVED",
            "The canonical concept is claimed by neither Core1A nor Core1B teaching routes.",
            ref,
        ))
    elif routing_state in {"CORE1A_ONLY", "CORE1B_ONLY"}:
        findings.append(_finding(
            "CROSS_CORE_ROUTE_COVERAGE_MISMATCH",
            "Core1A and Core1B do not claim the same canonical concept coverage.",
            ref,
        ))

    if routing_state not in {"UNROUTED", "UNOBSERVED"}:
        if not isinstance(orientation, dict) or not orientation.get("core1_compilable"):
            findings.append(_finding(
                "CORE1_ORIENTATION_UNAVAILABLE_FOR_STUDY",
                "A concept is routed through Core1A/Core1B but its bucket has no compilable Core1 map.",
                microtopic.get("bucket_id"),
            ))

    jump = microtopic.get("inferential_jump")
    if not isinstance(jump, str) or not jump.strip():
        findings.append(_finding(
            "CANONICAL_INFERENTIAL_JUMP_MISSING",
            "The study progression has no single canonical inferential jump to share.",
            ref,
        ))

    hard_transition_refs = {
        row.get("microtopic_ref")
        for row in (orientation or {}).get("hard_transitions", [])
        if isinstance(row, dict)
    }
    if microtopic.get("intrinsic_badge") in {"MEDIUM", "HARD"}:
        if ref not in hard_transition_refs:
            findings.append(_finding(
                "CORE1_HARD_POINTER_MISSING",
                "A MEDIUM/HARD concept is not named in Core1's hard-transition orientation.",
                ref,
            ))

    canonical_representation_refs = sorted({
        item
        for item in (microtopic.get("representation_refs") or [])
        if isinstance(item, str) and item
    })

    phase1_debt = list((orientation or {}).get("finding_codes") or [])
    phase2_debt = list((construction or {}).get("finding_codes") or [])
    phase3_debt = list((reconstruction or {}).get("finding_codes") or [])

    return {
        "subject": subject,
        "bucket_ref": microtopic.get("bucket_id"),
        "microtopic_ref": ref,
        "inferential_jump": jump,
        "intrinsic_badge": microtopic.get("intrinsic_badge"),
        "depth_authority": "CANONICAL_MICROTOPIC",
        "core1_orientation_available": bool((orientation or {}).get("core1_compilable")),
        "core1_orientation_surfaces": list((orientation or {}).get("orientation_surfaces") or []),
        "core1a_route_refs": list((reconstruction or {}).get("core1a_route_refs") or []),
        "core1b_route_refs": list((reconstruction or {}).get("core1b_route_refs") or []),
        "routing_state": routing_state,
        "canonical_representation_refs": canonical_representation_refs,
        "representation_authority": "SHARED_CANONICAL_MICROTOPIC_REFS",
        "phase1_orientation_debt": phase1_debt,
        "phase2_construction_debt": phase2_debt,
        "phase3_reconstruction_debt": phase3_debt,
        "cross_progression_findings": findings,
        "cross_progression_codes": sorted({row["code"] for row in findings}),
        "cross_progression_coherent": not findings,
        "manual_review_obligations": [
            "CORE1_ORIENTS_WITHOUT_PRETENDING_TO_TEACH",
            "CORE1A_GENUINELY_CONSTRUCTS_CANONICAL_INFERENCE",
            "CORE1B_GENUINELY_RECONSTRUCTS_SAME_INFERENCE",
            "REPRESENTATION_MEANING_REMAINS_CANONICAL_ACROSS_PRODUCTS",
        ],
    }


def audit(repo: Path) -> dict:
    orientation_report = core1_orientation.audit(repo)
    construction_report = core1a_construction.audit(repo)
    reconstruction_report = core1b_reconstruction.audit(repo)

    orientation_by_bucket = {
        row["bucket_ref"]: row
        for row in orientation_report["buckets"]
    }
    construction_by_microtopic = {
        row["microtopic_ref"]: row
        for row in construction_report["microtopics"]
    }
    reconstruction_by_microtopic = {
        row["microtopic_ref"]: row
        for row in reconstruction_report["microtopics"]
    }
    microtopics, subjects, routes = _canonical_microtopics(repo)

    route_findings: list[dict] = []
    for route in routes:
        for ref in route["microtopic_refs"]:
            if ref not in microtopics:
                route_findings.append(_finding(
                    "TEACHING_ROUTE_MICROTOPIC_UNRESOLVED",
                    f'{route.get("id")} references no canonical microtopic.',
                    str(ref),
                ))

    rows = [
        progression_row(
            microtopic,
            subject=subjects.get(ref, "UNKNOWN"),
            orientation=orientation_by_bucket.get(microtopic.get("bucket_id")),
            construction=construction_by_microtopic.get(ref),
            reconstruction=reconstruction_by_microtopic.get(ref),
        )
        for ref, microtopic in microtopics.items()
    ]
    rows.sort(key=lambda row: (row["subject"], row["bucket_ref"] or "", row["microtopic_ref"] or ""))

    buckets = []
    for bucket_ref, orientation in sorted(orientation_by_bucket.items()):
        members = [row for row in rows if row["bucket_ref"] == bucket_ref]
        buckets.append({
            "subject": orientation["subject"],
            "bucket_ref": bucket_ref,
            "core1_orientation_available": orientation["core1_compilable"],
            "core1_orientation_surfaces": orientation.get("orientation_surfaces") or [],
            "microtopic_count": len(members),
            "routed_study_microtopics": sum(
                1 for row in members
                if row["routing_state"] not in {"UNROUTED", "UNOBSERVED"}
            ),
            "cross_progression_gap_count": sum(
                1 for row in members if row["cross_progression_findings"]
            ),
            "phase1_orientation_debt": orientation.get("finding_codes") or [],
        })

    cross_counts: dict[str, int] = {}
    for row in rows:
        for code in row["cross_progression_codes"]:
            cross_counts[code] = cross_counts.get(code, 0) + 1
    for finding in route_findings:
        cross_counts[finding["code"]] = cross_counts.get(finding["code"], 0) + 1

    return {
        "schema_version": "1.0.0",
        "audit": "CORE1_CROSS_PROGRESSION",
        "semantics": {
            "progression": "Core1 map -> Core1A construction -> Core1B reconstruction",
            "canonical_crux": "microtopic.inferential_jump",
            "depth_authority": "microtopic.intrinsic_badge",
            "local_debt_is_not_cross_drift": True,
            "manual_review_required": True,
        },
        "summary": {
            "bucket_count": len(buckets),
            "core1_orientable_buckets": sum(
                1 for row in buckets if row["core1_orientation_available"]
            ),
            "microtopic_count": len(rows),
            "cross_progression_coherent_microtopics": sum(
                1 for row in rows if row["cross_progression_coherent"]
            ),
            "cross_progression_gap_microtopics": sum(
                1 for row in rows if not row["cross_progression_coherent"]
            ),
            "unrouted_microtopics": sum(
                1 for row in rows if row["routing_state"] == "UNROUTED"
            ),
            "phase1_local_debt_buckets": sum(
                1 for row in buckets if row["phase1_orientation_debt"]
            ),
            "phase2_local_debt_microtopics": sum(
                1 for row in rows if row["phase2_construction_debt"]
            ),
            "phase3_local_debt_microtopics": sum(
                1 for row in rows if row["phase3_reconstruction_debt"]
            ),
            "route_reference_findings": len(route_findings),
            "cross_finding_counts": dict(sorted(cross_counts.items())),
        },
        "route_findings": route_findings,
        "buckets": buckets,
        "microtopics": rows,
    }


def baseline(report: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "audit": report["audit"],
        "basis": "legacy cross-Core1 progression debt; local Phase-1/2/3 debt remains owned by its phase",
        "route_findings": sorted({
            (row["code"], row.get("ref", ""))
            for row in report.get("route_findings", [])
        }),
        "microtopics": {
            row["microtopic_ref"]: row["cross_progression_codes"]
            for row in report["microtopics"]
        },
    }


def forward_findings(report: dict, baseline_doc: dict) -> list[dict]:
    previous = baseline_doc.get("microtopics") or {}
    out: list[dict] = []
    for row in report["microtopics"]:
        current = set(row["cross_progression_codes"])
        allowed = set(previous.get(row["microtopic_ref"], []))
        for code in sorted(current - allowed):
            out.append({
                "microtopic_ref": row["microtopic_ref"],
                "subject": row["subject"],
                "code": code,
                "detail": "new cross-Core1 progression debt relative to committed baseline",
            })

    previous_routes = {
        tuple(row)
        for row in baseline_doc.get("route_findings", [])
        if isinstance(row, list) and len(row) == 2
    }
    for finding in report.get("route_findings", []):
        key = (finding["code"], finding.get("ref", ""))
        if key not in previous_routes:
            out.append({
                "microtopic_ref": finding.get("ref"),
                "subject": "UNKNOWN",
                "code": finding["code"],
                "detail": "new unresolved teaching-route reference relative to committed baseline",
            })
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--write-report")
    parser.add_argument("--write-baseline")
    parser.add_argument("--check-baseline")
    args = parser.parse_args()
    report = audit(Path(args.repo).resolve())

    if args.write_report:
        Path(args.write_report).write_text(
            json.dumps(report, indent=2) + "\n",
            encoding="utf-8",
        )
    if args.write_baseline:
        Path(args.write_baseline).write_text(
            json.dumps(baseline(report), indent=2) + "\n",
            encoding="utf-8",
        )
    if args.check_baseline:
        base = json.loads(Path(args.check_baseline).read_text(encoding="utf-8"))
        findings = forward_findings(report, base)
        print(json.dumps({"passed": not findings, "findings": findings}, indent=2))
        return 1 if findings else 0

    if not (args.write_report or args.write_baseline):
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
