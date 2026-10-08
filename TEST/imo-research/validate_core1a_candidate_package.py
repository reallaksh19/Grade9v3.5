#!/usr/bin/env python3
"""Check the isolated TEST IMO Core1A candidate without admitting product authority."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.library.resolve import validate_library  # noqa: E402

ROOT = REPO / "TEST" / "imo-research"
PACKAGE = REPO / "TEST" / "library" / "imo-g9-divisibility-core1a.v1.json"
SCHEMA = REPO / "Shared" / "library" / "package.schema.json"
PACKAGE_ID = "TEST-IMO-G9-CORE1A-NS-DIVISIBILITY-PILOT"
S = "SRC-TEST-IMO-G9-NS-AUTHORED"
B = "BUCKET-TEST-IMO-G9-NS-DIVISIBILITY"
C = "CAP-TEST-IMO-G9-UNIVERSAL-DIVISIBILITY"
M = "MIC-TEST-IMO-G9-CONSECUTIVE-FACTOR-INVARIANTS"
R = "REL-TEST-IMO-G9-THREE-CONSECUTIVE-FACTORS"
P = "REP-TEST-IMO-G9-RESIDUE-TABLE"
F = "FAM-TEST-IMO-G9-AUTHORED-CONSECUTIVE-PRODUCT"
T = "ROUTE-TEST-IMO-G9-CORE1A-CONSTRUCTION"


class IMOCore1ACandidateError(ValueError):
    pass


def ensure(ok: bool, why: str) -> None:
    if not ok:
        raise IMOCore1ACandidateError(why)


def read(path: Path) -> dict:
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise IMOCore1ACandidateError(f"unreadable research package: {path}: {exc}") from exc
    ensure(isinstance(obj, dict), "package must be an object")
    return obj


def validate_package(package: Path = PACKAGE) -> dict:
    d = read(package)
    expected = {
        "resources": (S,), "buckets": (B,), "capabilities": (C,),
        "microtopics": (M,), "relations": (R,), "representations": (P,),
        "question_families": (F,), "teaching_routes": (T,),
        "questions": (), "practice_profiles": (), "evidence": (),
        "known_issues": (), "data": ()
    }
    ensure(d.get("schema_version") == "0.2.0"
           and d.get("package_id") == PACKAGE_ID
           and d.get("version") == "0.1.0"
           and d.get("status") == "CANDIDATE"
           and d.get("subject") == "TEST"
           and d.get("curriculum_mappings") == []
           and d.get("scope_summary") ==
           "Isolated authored mathematical Core1A candidate; no official SOF source questions, QRT admission, licensed figures, public learner delivery or curriculum approval.",
           "research-only TEST canonical scope or status altered")
    ensure(d.get("extensions") == {
        "grade9v3:imo_provenance": "ISSUE_296_AUTHORED_CORE1A_CANDIDATE_NO_SOFT_CORE2",
        "grade9v3:qrt_admitted": False,
        "grade9v3:core2_source_custody_granted": False,
        "grade9v3:learner_published": False
    }, "invented SOF source, QRT, Core2 or publication")
    for coll, ids in expected.items():
        values = d.get(coll)
        ensure(isinstance(values, list) and tuple(
            r.get("id") if isinstance(r, dict) else None for r in values
        ) == ids, f"{coll}: expected exact canonical candidate records")
    src, bucket, cap, micro, rel, rep, family, route = (
        d[name][0] for name in (
            "resources","buckets","capabilities","microtopics",
            "relations","representations","question_families","teaching_routes"
        )
    )
    ensure(src.get("origin") == "AUTHORED"
           and src.get("role") == ["AUTHOR_CREATED"]
           and src.get("status") == "CANDIDATE"
           and src.get("snapshot_digest") is None
           and src.get("snapshot_ref") is None
           and src.get("locator") ==
           "https://github.com/reallaksh19/Grade9v3.5/issues/296",
           "source must be authored math not falsely cited SOF PDF")
    ensure(cap.get("acceptance_status") == "CANDIDATE"
           and cap.get("curriculum_mappings") == []
           and cap.get("prerequisite_refs") == [],
           "capability may not claim academic curriculum acceptance")
    ensure(bucket.get("primary_representation_ref") == P
           and bucket.get("intrinsic_badge") == "HARD"
           and len(bucket.get("conventions", [])) == 4,
           "missing critical domain conventions")
    ensure(micro.get("bucket_id") == B
           and micro.get("primary_capability_ref") == C
           and micro.get("relation_refs") == [R]
           and micro.get("representation_refs") == [P]
           and micro.get("question_family_refs") == [F]
           and micro.get("intrinsic_badge") == "HARD"
           and len(micro.get("entry_assumptions", [])) == 4,
           "microtopic premise/canonical join incomplete")
    jump = micro.get("inferential_jump")
    ensure(isinstance(jump, str) and len(jump) >= 165
           and all(term in jump for term in ("universal", "coprimality", "factor of 2", "factor of 3")),
           "universal divisibility inference removed")
    steps = micro.get("teaching_path")
    ensure(isinstance(steps, list)
           and [r.get("id") for r in steps] == ["TC-01","TC-02","TC-03","TC-04"],
           "exact four inferential steps required")
    for step in steps:
        ensure(step.get("source_ref") == S
               and step.get("role") in {"DECLARE","TRANSFORM","VERIFY"}
               and len(step.get("why_valid","")) >= 78
               and len(step.get("action","")) >= 65,
               "complete reasoning and why-valid explanations required")
    ensure(len(micro.get("misconceptions",[])) == 1
           and "few starting integers" in micro["misconceptions"][0].get("wrong_idea",""),
           "finite-example reasoning misconception must be explicitly repaired")
    exit_task = micro.get("exit_task", {})
    answer = exit_task.get("answer",{})
    ensure("divisible by 24" in exit_task.get("prompt","")
           and answer.get("verification_status") == "CHECKED_BY_AUTHOR"
           and answer.get("kind") == "MODEL_RESPONSE"
           and "divisible by 8" in " ".join(answer.get("reasoning", []))
           and "divisible by 3" in " ".join(answer.get("reasoning", []))
           and "24" in answer.get("check","")
           and exit_task.get("source_ref") == S
           and exit_task.get("oracle",{}).get("verification",{}).get("validator_id") ==
           "TEST/imo-research/validate_core1a_candidate_package.py",
           "exit task must have an authored full 24-divisibility closure and oracle")
    units = micro.get("construction_units")
    ensure(isinstance(units,list) and len(units) == 1
           and units[0].get("step_refs") == [s["id"] for s in steps]
           and units[0].get("representation_ref") == P
           and units[0].get("misconception_indexes") == [0],
           "construction unit cannot omit decisive step or repair")
    ensure(rel.get("source_refs") == [S]
           and rel.get("gate_relation_ref") is None
           and "mod 6" in rel.get("expression","")
           and len(rel.get("derivation",[])) == 3,
           "source-independent relation and derivation required")
    ensure(rep.get("kind") == "TABLE_OF_VALUES"
           and rep.get("source_refs") == [S]
           and rep.get("relation_refs") == [R]
           and len(rep.get("required_elements",[])) == 5
           and len(rep.get("correspondence",[])) == 2
           and rep.get("scene_instances") == []
           and rep.get("rendered_asset_refs") == [],
           "only the proposed verbal/symbolic representation exists; no live figure claim")
    ensure(family.get("capability_refs") == [C] and
           family.get("item_refs") == [],
           "authored conceptual family may not claim reviewed source questions")
    ensure(route.get("cores") == ["CORE1A"]
           and route.get("microtopic_refs") == [M]
           and route.get("practice_profile_ref") is None
           and len(route.get("source_preferences",[])) == 1
           and route["source_preferences"][0]["resource_ref"] == S,
           "Core1A only, not invented source Core2 route")
    # Exhaustive modular reasoning checks every integer congruence class,
    # rather than sampling positive starting values in a finite interval.
    ensure(all(n*(n+1)*(n+2) % 6 == 0 for n in range(6)),
           "divisibility-by-six proof contradicted by exhaustive residues")
    ensure(all(n*(n+1)*(n+2)*(n+3) % 24 == 0 for n in range(24)),
           "independent exit proof contradicted by exhaustive residues")
    try:
        outcome = validate_library([d])
    except Exception as exc:
        raise IMOCore1ACandidateError(
            f"canonical package unresolved/collision/cycle: {exc}"
        ) from exc
    ensure(outcome.get("unresolved_references") == 0,
           "candidate canonical references unresolved")
    return {
      "result": "AUTHORED_TEST_CORE1A_PACKAGE_CANDIDATE_ONLY",
      "package": PACKAGE_ID, "capabilities": 1, "microtopics": 1,
      "complete_teaching_steps": 4, "figure_assets_rendered": 0,
      "schema_validated_by_jsonschema": False,
      "mathematics_exhaustive_residue_checks": "MOD6_AND_MOD24_PASS",
      "official_source_core2": 0, "canonical_acceptance": 0,
      "qrt_acceptance": 0, "learner_published": 0,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--package",type=Path,default=PACKAGE)
    args = parser.parse_args()
    try:
        print(json.dumps(validate_package(args.package),sort_keys=True))
    except IMOCore1ACandidateError as exc:
        parser.exit(1, f"IMO_TEST_CORE1A_CANDIDATE_INVALID: {exc}\n")


if __name__ == "__main__":
    main()
