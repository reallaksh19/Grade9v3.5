#!/usr/bin/env python3
"""Resolve an arbitrary worksheet's question-to-capability map against canonical teaching.

A worksheet is a transient demand overlay. It does not become curriculum authority merely
because somebody mapped its questions. This tool therefore reads existing capability,
microtopic and matrix records and reports where each declared capability is taught. It
never invents a capability, prerequisite, matrix rung or source claim.

Prerequisite closure and cross-matrix ordering belong to the next layer (study_route.py).
This module answers only: "what does the worksheet say this question needs, and where does
the repository currently teach that capability?"
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
from Shared.tools import capability_delivery, capability_graph  # noqa: E402

SCHEMA = REPO / "Shared/library/worksheet-map.schema.json"

UNKNOWN_CAPABILITY = "WORKSHEET_CAPABILITY_UNKNOWN"
NO_TEACHING_LOCATION = "WORKSHEET_CAPABILITY_HAS_NO_TEACHING_LOCATION"
AMBIGUOUS_LOCATION = "WORKSHEET_CAPABILITY_AMBIGUOUS_LOCATION"


def _schema_findings(mapping: dict, repo: Path = REPO) -> list[dict]:
    """Return structural findings when jsonschema is available."""
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    schema = load(repo / "Shared/library/worksheet-map.schema.json")
    validator = jsonschema.Draft202012Validator(schema)
    return [{
        "point": "WORKSHEET_MAP_STRUCTURE",
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(mapping)]


def _canonical_questions(subject: str, repo: Path = REPO) -> dict[str, dict]:
    found: dict[str, dict] = {}
    for path in sorted((repo / subject / "library").rglob("*.json")):
        package = load(path)
        for question in package.get("questions", []):
            found[question["id"]] = question
    return found


def capability_locations(subject: str, repo: Path = REPO) -> dict[str, list[dict]]:
    """Map capability ids to matrix/rung locations through canonical microtopics."""
    caps, mics = capability_graph.subject_graph(subject, repo)
    locations: dict[str, list[dict]] = {cap: [] for cap in caps}
    matrices = repo / subject / "matrices"
    if not matrices.is_dir():
        return locations

    for path in sorted(matrices.glob("*.rungs.json")):
        board = load(path)
        for row in board.get("rungs", []):
            mic_ref = row.get("microtopic_ref")
            mic = mics.get(mic_ref) if mic_ref else None
            capability = mic.get("primary_capability_ref") if mic else None
            if not capability:
                continue
            locations.setdefault(capability, []).append({
                "matrix_id": board.get("matrix_id"),
                "bucket_id": board.get("bucket_id"),
                "topic": board.get("topic"),
                "subtopic": board.get("subtopic"),
                "rung": row.get("rung"),
                "ladder_position": row.get("ladder_position"),
                "default_entry_eligible": row.get("default_entry_eligible", True),
                "microtopic_ref": mic_ref,
                "matrix_path": str(path.relative_to(repo)),
            })

    for rows in locations.values():
        rows.sort(key=lambda row: (
            str(row.get("matrix_id") or ""),
            int(row.get("ladder_position") or 0),
            str(row.get("rung") or ""),
        ))
    return locations


def subject_index(subject: str, repo: Path = REPO) -> dict:
    """Build the canonical lookup surface used by worksheet resolution."""
    caps, mics = capability_graph.subject_graph(subject, repo)
    by_capability: dict[str, list[str]] = {}
    for mic in mics.values():
        cap = mic.get("primary_capability_ref")
        if cap:
            by_capability.setdefault(cap, []).append(mic["id"])
    for refs in by_capability.values():
        refs.sort()
    return {
        "subject": subject,
        "capabilities": caps,
        "microtopics": mics,
        "microtopics_by_capability": by_capability,
        "locations": capability_locations(subject, repo),
        "canonical_questions": _canonical_questions(subject, repo),
    }


def _capability_row(capability_ref: str, role: str, index: dict) -> tuple[dict, list[dict]]:
    """Resolve one declared capability and return its row plus findings."""
    cap = index["capabilities"].get(capability_ref)
    if cap is None:
        return ({
            "role": role,
            "capability_ref": capability_ref,
            "state": "UNKNOWN",
            "locations": [],
        }, [{
            "point": UNKNOWN_CAPABILITY,
            "capability": capability_ref,
            "detail": "no canonical capability with this id exists in the subject library",
        }])

    locations = list(index["locations"].get(capability_ref, []))
    delivery = capability_delivery.resolve(cap, locations)
    row = {
        "role": role,
        "capability_ref": capability_ref,
        "state": capability_delivery.legacy_state(delivery),
        "delivery_state": delivery["state"],
        "provider": delivery["provider"],
        "external_provider": delivery["provider"],
        "acceptance_status": delivery["acceptance_status"],
        "action": cap.get("action"),
        "success_criterion": cap.get("success_criterion"),
        "microtopic_refs": list(index["microtopics_by_capability"].get(capability_ref, [])),
        "locations": locations,
    }
    findings = []
    if delivery["state"] == capability_delivery.UNRESOLVED:
        findings.append({
            "point": NO_TEACHING_LOCATION,
            "capability": capability_ref,
            "detail": (
                "the capability exists but has neither a local matrix/rung teaching "
                "location nor a declared external provider"
            ),
        })
    elif delivery["state"] == capability_delivery.AMBIGUOUS:
        findings.append({
            "point": AMBIGUOUS_LOCATION,
            "capability": capability_ref,
            "detail": "the same capability is taught from more than one matrix/rung location",
            "locations": locations,
        })
    return row, findings


def resolve_question(question: dict, index: dict) -> tuple[dict, list[dict]]:
    """Resolve a worksheet question without computing prerequisite closure."""
    qid = question.get("question_id")
    primary = question.get("primary_capability_ref")
    secondary = list(question.get("secondary_capability_refs") or [])
    findings: list[dict] = []

    rows = []
    if primary:
        row, found = _capability_row(primary, "PRIMARY", index)
        rows.append(row)
        findings += [{**f, "where": qid} for f in found]
    for capability in secondary:
        row, found = _capability_row(capability, "SECONDARY", index)
        rows.append(row)
        findings += [{**f, "where": qid} for f in found]

    if primary and primary in secondary:
        findings.append({
            "point": "WORKSHEET_PRIMARY_REPEATED_AS_SECONDARY",
            "where": qid,
            "capability": primary,
            "detail": "the primary capability may not be repeated as a secondary capability",
        })

    basis = question.get("mapping_basis")
    canonical_ref = question.get("canonical_question_ref")
    if basis == "CANONICAL_QUESTION":
        canonical = index["canonical_questions"].get(canonical_ref or "")
        if not canonical_ref:
            findings.append({
                "point": "WORKSHEET_CANONICAL_MAPPING_WITHOUT_QUESTION_REF",
                "where": qid,
                "detail": "CANONICAL_QUESTION mapping_basis requires canonical_question_ref",
            })
        elif canonical is None:
            findings.append({
                "point": "WORKSHEET_CANONICAL_QUESTION_UNKNOWN",
                "where": qid,
                "detail": f"{canonical_ref} does not exist in the subject library",
            })
        else:
            expected_primary = canonical.get("primary_capability_ref")
            expected_secondary = set(canonical.get("secondary_capability_refs") or [])
            if expected_primary != primary or expected_secondary != set(secondary):
                findings.append({
                    "point": "WORKSHEET_CANONICAL_MAPPING_DRIFT",
                    "where": qid,
                    "detail": (
                        "declared mapping does not match the canonical question's current "
                        "primary/secondary capability refs"
                    ),
                    "canonical_question_ref": canonical_ref,
                })

    state = "RESOLVED" if not findings else "HAS_FINDINGS"
    return ({
        "question_id": qid,
        "mapping_basis": basis,
        "canonical_question_ref": canonical_ref,
        "primary_capability_ref": primary,
        "secondary_capability_refs": secondary,
        "capabilities": rows,
        "state": state,
    }, findings)


def validate_mapping(mapping: dict, repo: Path = REPO) -> list[dict]:
    """Validate structure and semantic references, without guessing missing mappings."""
    structural = _schema_findings(mapping, repo)
    if structural:
        return structural

    findings: list[dict] = []
    seen: set[str] = set()
    for question in mapping.get("questions", []):
        qid = question["question_id"]
        if qid in seen:
            findings.append({
                "point": "WORKSHEET_QUESTION_ID_DUPLICATE",
                "where": qid,
                "detail": "question_id must be unique within one worksheet map",
            })
        seen.add(qid)

    index = subject_index(mapping["subject"], repo)
    for question in mapping.get("questions", []):
        _, found = resolve_question(question, index)
        findings += found
    return findings


def resolve(mapping: dict, repo: Path = REPO) -> dict:
    """Resolve a complete worksheet map to canonical teaching locations."""
    structural = _schema_findings(mapping, repo)
    if structural:
        return {
            "worksheet_id": mapping.get("worksheet_id"),
            "subject": mapping.get("subject"),
            "questions": [],
            "findings": structural,
            "passed": False,
        }

    index = subject_index(mapping["subject"], repo)
    rows, findings = [], []
    seen: set[str] = set()
    for question in mapping.get("questions", []):
        qid = question["question_id"]
        if qid in seen:
            findings.append({
                "point": "WORKSHEET_QUESTION_ID_DUPLICATE",
                "where": qid,
                "detail": "question_id must be unique within one worksheet map",
            })
        seen.add(qid)
        row, found = resolve_question(question, index)
        rows.append(row)
        findings += found

    return {
        "worksheet_id": mapping["worksheet_id"],
        "subject": mapping["subject"],
        "source_note": mapping.get("source_note"),
        "questions": rows,
        "findings": findings,
        "passed": not findings,
        "rule": (
            "Worksheet mappings describe demand; canonical capabilities/microtopics/matrices "
            "remain academic authority. Prerequisite ordering is not computed in this layer."
        ),
    }


def readable(report: dict) -> str:
    out = [
        f'# Study map -- {report.get("worksheet_id")}',
        "",
        f'  subject  {report.get("subject")}',
        "",
    ]
    for question in report.get("questions", []):
        out += [f'## {question["question_id"]} -- {question["state"]}', ""]
        for cap in question.get("capabilities", []):
            out += [f'  {cap["role"]:9} {cap["capability_ref"]} -- {cap["state"]}']
            if cap.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE:
                out += [
                    f'            bridge: {cap.get("provider")} '
                    f'({cap.get("acceptance_status") or "UNSPECIFIED"})'
                ]
            for loc in cap.get("locations", []):
                out += [
                    f'            {loc["matrix_id"]} / {loc["rung"]} '
                    f'({loc["microtopic_ref"]})'
                ]
        out += [""]
    if report.get("findings"):
        out += ["## Findings", ""]
        for finding in report["findings"]:
            out += [
                f'  {finding["point"]:48} {finding.get("where", "")} '
                f'{finding.get("capability", "")}'
            ]
        out += [""]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--map", type=Path, required=True, help="worksheet map JSON")
    parser.add_argument("--readable", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    report = resolve(load(args.map))
    print(readable(report) if args.readable
          else json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
