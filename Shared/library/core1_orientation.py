"""Phase-1 Core1 semantic-orientation inventory and forward gate.

The auditor enforces only structural claims that can be falsified from canonical data.
It deliberately does not score prose length, keywords, or stylistic similarity as a
proxy for conceptual quality. The reviewer-owned distinction "Core1 is a map, not the
teaching construction" remains an explicit manual-review obligation in the report.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Iterable

STRUCTURAL_FINDINGS = {
    "RELATION_REF_UNRESOLVED",
    "RELATION_MEANING_MISSING",
    "RELATION_CONDITIONS_MISSING",
    "CONVENTION_STATEMENT_MISSING",
    "HARD_TRANSITION_BADGE_REASON_MISSING",
    "CURRICULUM_MAPPING_STATUS_MISSING",
    "PRIMARY_REPRESENTATION_UNRESOLVED",
    "PRIMARY_REPRESENTATION_CORE1_SCENE_MISSING",
    "SCOPE_DECLARATION_EMPTY",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def subject_packages(repo: Path) -> Iterable[tuple[str, Path, dict]]:
    """Yield ordinary canonical subject-library packages.

    Exam banks live under library/exam-bank and are intentionally outside the concept
    orientation audit. Shared/docs/tests are excluded because they are not subject
    libraries.
    """
    for subject_dir in sorted(path for path in repo.iterdir() if path.is_dir()):
        library = subject_dir / "library"
        if not library.is_dir():
            continue
        for path in sorted(library.glob("*.json")):
            try:
                package = load(path)
            except Exception:
                continue
            if not isinstance(package, dict) or not isinstance(package.get("buckets"), list):
                continue
            yield subject_dir.name, path, package


def _index(package: dict, key: str) -> dict[str, dict]:
    return {
        row["id"]: row
        for row in package.get(key, []) or []
        if isinstance(row, dict) and isinstance(row.get("id"), str)
    }


def _finding(code: str, *, detail: str, ref: str | None = None) -> dict:
    row = {"code": code, "detail": detail}
    if ref:
        row["ref"] = ref
    return row


def orientation_surfaces(
    bucket: dict,
    microtopics: list[dict],
    relation_refs: set[str] | list[str],
    *,
    representation_index: dict[str, dict] | None = None,
) -> list[str]:
    """Canonical content that can legitimately form the compact Core1 map.

    Equation presence is one orientation surface, not the definition of orientation.
    Core1 may also map declared conventions/scope, point at intrinsically difficult
    transitions, or show a declared primary representation that actually has a Core1
    scene. The helper names only content the compiler can emit without inventing prose.
    """
    surfaces: list[str] = []
    if relation_refs:
        surfaces.append("GOVERNING_RELATIONS")

    conventions = bucket.get("conventions") or []
    if any(
        isinstance(row, dict)
        and isinstance(row.get("statement"), str)
        and row["statement"].strip()
        for row in conventions
    ):
        surfaces.append("DECLARED_CONVENTIONS")

    scope = bucket.get("scope") or {}
    if (
        isinstance(scope, dict)
        and (
            (isinstance(scope.get("covers"), str) and scope["covers"].strip())
            or bool(scope.get("excluded"))
        )
    ):
        surfaces.append("DECLARED_SCOPE")

    if any(
        isinstance(row, dict) and row.get("intrinsic_badge") in {"MEDIUM", "HARD"}
        for row in microtopics
    ):
        surfaces.append("HARD_TRANSITION_POINTERS")

    primary = bucket.get("primary_representation_ref")
    if isinstance(primary, str) and primary and representation_index:
        representation = representation_index.get(primary)
        if isinstance(representation, dict) and any(
            isinstance(scene, dict) and "CORE1" in (scene.get("cores") or [])
            for scene in (representation.get("scene_instances") or [])
        ):
            surfaces.append("PRIMARY_REPRESENTATION")

    return surfaces


def audit_bucket(
    subject: str,
    package_path: str,
    package: dict,
    bucket: dict,
    *,
    relation_index: dict[str, dict] | None = None,
    representation_index: dict[str, dict] | None = None,
    microtopics_override: list[dict] | None = None,
) -> dict:
    relations = relation_index or _index(package, "relations")
    representations = representation_index or _index(package, "representations")
    microtopics = (
        list(microtopics_override)
        if microtopics_override is not None
        else [
            row for row in package.get("microtopics", []) or []
            if isinstance(row, dict) and row.get("bucket_id") == bucket.get("id")
        ]
    )

    findings: list[dict] = []
    relation_refs = sorted({
        ref
        for microtopic in microtopics
        for ref in (microtopic.get("relation_refs") or [])
        if isinstance(ref, str)
    })
    relation_rows = []
    for ref in relation_refs:
        relation = relations.get(ref)
        if relation is None:
            findings.append(_finding(
                "RELATION_REF_UNRESOLVED",
                detail="Core1 relation reference does not resolve in the canonical package.",
                ref=ref,
            ))
            continue
        meaning = relation.get("meaning")
        conditions = relation.get("conditions")
        if not isinstance(meaning, str) or not meaning.strip():
            findings.append(_finding(
                "RELATION_MEANING_MISSING",
                detail="A governing relation used by this bucket has no learner-readable meaning.",
                ref=ref,
            ))
        if not isinstance(conditions, list) or not conditions:
            findings.append(_finding(
                "RELATION_CONDITIONS_MISSING",
                detail="A governing relation used by this bucket declares no applicability conditions.",
                ref=ref,
            ))
        relation_rows.append({
            "id": ref,
            "has_meaning": isinstance(meaning, str) and bool(meaning.strip()),
            "condition_count": len(conditions) if isinstance(conditions, list) else 0,
        })

    conventions = bucket.get("conventions") or []
    if isinstance(conventions, list):
        for row in conventions:
            if not isinstance(row, dict) or not isinstance(row.get("statement"), str) or not row["statement"].strip():
                findings.append(_finding(
                    "CONVENTION_STATEMENT_MISSING",
                    detail="An authored convention row has no usable statement.",
                    ref=row.get("id") if isinstance(row, dict) else None,
                ))

    scope = bucket.get("scope")
    scope_state = "NOT_AUTHORED"
    if isinstance(scope, dict):
        covers = scope.get("covers")
        excluded = scope.get("excluded") or []
        extensions = scope.get("extension_refs") or []
        scope_state = "AUTHORED"
        if not (isinstance(covers, str) and covers.strip()) and not excluded and not extensions:
            findings.append(_finding(
                "SCOPE_DECLARATION_EMPTY",
                detail="The bucket declares scope but provides no covers/excluded/extension content.",
            ))

    hard_transitions = []
    for microtopic in microtopics:
        badge = microtopic.get("intrinsic_badge")
        if badge not in {"MEDIUM", "HARD"}:
            continue
        reason = microtopic.get("badge_reason")
        if not isinstance(reason, str) or not reason.strip():
            findings.append(_finding(
                "HARD_TRANSITION_BADGE_REASON_MISSING",
                detail="A MEDIUM/HARD conceptual transition has no reason for Core1 to point forward to.",
                ref=microtopic.get("id"),
            ))
        hard_transitions.append({
            "microtopic_ref": microtopic.get("id"),
            "title": microtopic.get("title"),
            "intrinsic_badge": badge,
            "badge_reason": reason,
        })

    mappings = bucket.get("curriculum_mappings") or []
    if isinstance(mappings, list):
        for index, mapping in enumerate(mappings):
            if not isinstance(mapping, dict) or not isinstance(mapping.get("mapping_status"), str) or not mapping["mapping_status"].strip():
                findings.append(_finding(
                    "CURRICULUM_MAPPING_STATUS_MISSING",
                    detail="A bucket curriculum mapping lacks explicit mapping_status, so authority cannot be represented honestly.",
                    ref=f"{bucket.get('id')}:mapping:{index}",
                ))

    primary = bucket.get("primary_representation_ref")
    representation_state = "NOT_AUTHORED"
    if isinstance(primary, str) and primary:
        representation_state = "RESOLVED"
        representation = representations.get(primary)
        if representation is None:
            representation_state = "UNRESOLVED"
            findings.append(_finding(
                "PRIMARY_REPRESENTATION_UNRESOLVED",
                detail="The bucket's declared primary representation does not resolve.",
                ref=primary,
            ))
        else:
            core1_scenes = [
                scene for scene in representation.get("scene_instances", []) or []
                if isinstance(scene, dict) and "CORE1" in (scene.get("cores") or [])
            ]
            if not core1_scenes:
                representation_state = "NO_CORE1_SCENE"
                findings.append(_finding(
                    "PRIMARY_REPRESENTATION_CORE1_SCENE_MISSING",
                    detail="The declared primary representation has no scene instance bound to Core1.",
                    ref=primary,
                ))

    finding_codes = sorted({row["code"] for row in findings})
    surfaces = orientation_surfaces(
        bucket,
        microtopics,
        set(relation_refs),
        representation_index=representations,
    )
    return {
        "subject": subject,
        "package_path": package_path,
        "bucket_ref": bucket.get("id"),
        "title": bucket.get("title"),
        "core1_compilable": bool(surfaces),
        "core1_compilability_reason": (
            "ORIENTABLE_CANONICAL_CONTENT_PRESENT"
            if surfaces
            else "NO_ORIENTABLE_CANONICAL_CONTENT"
        ),
        "orientation_surfaces": surfaces,
        "conventions_state": "AUTHORED" if conventions else "NOT_AUTHORED",
        "convention_count": len(conventions) if isinstance(conventions, list) else 0,
        "scope_state": scope_state,
        "primary_representation_state": representation_state,
        "primary_representation_ref": primary,
        "relations": relation_rows,
        "hard_transitions": hard_transitions,
        "curriculum_mapping_count": len(mappings) if isinstance(mappings, list) else 0,
        "findings": findings,
        "finding_codes": finding_codes,
        "manual_review_obligations": [
            "CORE1_IS_MAP_NOT_TEACHING_CONSTRUCTION",
            "ORIENTATION_WORDING_IS_CONCISE_WITHOUT_ERASING_CONDITIONS",
        ],
    }


def audit(repo: Path) -> dict:
    rows = []
    packages = list(subject_packages(repo))
    by_subject: dict[str, list[tuple[Path, dict]]] = {}
    for subject, path, package in packages:
        by_subject.setdefault(subject, []).append((path, package))

    for subject, subject_rows in sorted(by_subject.items()):
        relations: dict[str, dict] = {}
        representations: dict[str, dict] = {}
        microtopics_by_bucket: dict[str, list[dict]] = {}
        for _, package in subject_rows:
            relations.update(_index(package, "relations"))
            representations.update(_index(package, "representations"))
            for microtopic in package.get("microtopics", []) or []:
                if not isinstance(microtopic, dict):
                    continue
                bucket_ref = microtopic.get("bucket_id")
                if isinstance(bucket_ref, str):
                    microtopics_by_bucket.setdefault(bucket_ref, []).append(microtopic)
        for path, package in subject_rows:
            rel = str(path.relative_to(repo))
            for bucket in package.get("buckets", []) or []:
                if isinstance(bucket, dict):
                    rows.append(audit_bucket(
                        subject,
                        rel,
                        package,
                        bucket,
                        relation_index=relations,
                        representation_index=representations,
                        microtopics_override=microtopics_by_bucket.get(bucket.get("id"), []),
                    ))
    rows.sort(key=lambda row: (row["subject"], row["bucket_ref"] or ""))
    counts: dict[str, int] = {}
    for row in rows:
        for code in row["finding_codes"]:
            counts[code] = counts.get(code, 0) + 1
    return {
        "schema_version": "1.0.0",
        "audit": "CORE1_SEMANTIC_ORIENTATION",
        "semantics": {
            "core1": "compact semantic orientation; map, not teaching construction",
            "structural_gate_only": True,
            "manual_review_required": True,
        },
        "summary": {
            "bucket_count": len(rows),
            "core1_compilable_buckets": sum(1 for row in rows if row["core1_compilable"]),
            "buckets_with_structural_findings": sum(1 for row in rows if row["findings"]),
            "finding_counts": dict(sorted(counts.items())),
        },
        "buckets": rows,
    }


def baseline(report: dict) -> dict:
    return {
        "schema_version": "1.0.0",
        "audit": report["audit"],
        "basis": "legacy structural debt accepted only as forward-migration baseline",
        "buckets": {
            row["bucket_ref"]: row["finding_codes"]
            for row in report["buckets"]
        },
    }


def forward_findings(report: dict, baseline_doc: dict) -> list[dict]:
    previous = baseline_doc.get("buckets") or {}
    result = []
    for row in report["buckets"]:
        current = set(row["finding_codes"])
        allowed = set(previous.get(row["bucket_ref"], []))
        for code in sorted(current - allowed):
            result.append({
                "bucket_ref": row["bucket_ref"],
                "subject": row["subject"],
                "code": code,
                "detail": "new structural Core1 orientation debt relative to the committed baseline",
            })
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=str(Path(__file__).resolve().parents[2]))
    parser.add_argument("--write-report")
    parser.add_argument("--write-baseline")
    parser.add_argument("--check-baseline")
    args = parser.parse_args()

    repo = Path(args.repo).resolve()
    report = audit(repo)

    if args.write_report:
        Path(args.write_report).write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    if args.write_baseline:
        Path(args.write_baseline).write_text(json.dumps(baseline(report), indent=2) + "\n", encoding="utf-8")
    if args.check_baseline:
        base = load(Path(args.check_baseline))
        findings = forward_findings(report, base)
        if findings:
            print(json.dumps({"passed": False, "findings": findings}, indent=2))
            return 1
        print(json.dumps({"passed": True, "findings": []}, indent=2))
        return 0

    if not (args.write_report or args.write_baseline):
        print(json.dumps(report, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
