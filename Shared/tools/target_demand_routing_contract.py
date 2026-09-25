#!/usr/bin/env python3
"""Validate the Target Demand Routing blueprint contract and route artifacts."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
ROLE_DIR = REPO / "Shared" / "roles"
SCHEMA_PATH = REPO / "Shared" / "library" / "target-demand-route.schema.json"
BLOCK = re.compile(r"^```target-demand-routing\s*$\n(.*?)^```\s*$", re.MULTILINE | re.DOTALL)

REQUIRED_INVARIANTS = {
    "every_fixed_target_requires_route_or_terminal_block",
    "whole_question_hold_cannot_hide_partial_capability_closure",
    "every_move_requires_coverage_ledger",
    "generic_practice_does_not_close_target",
    "target_authority_is_independent_of_direct_source_use",
    "direct_source_use_is_independent_of_instructional_demand_use",
    "instructional_demand_use_is_independent_of_assessment_claim",
    "identity_is_independent_of_source_custody",
    "semantic_identity_requires_documented_candidate_review",
    "owner_waiver_is_not_mastery_evidence",
    "owner_waiver_cannot_bypass_capability_gap",
    "owner_waiver_cannot_bypass_academic_review",
    "core1_family_scope_remains_canonical",
    "demand_influence_must_name_move_and_observable_change",
    "core2a_target_use_requires_capability_closure",
    "core2b_target_use_requires_capability_closure_and_prior_exposure",
    "extension_candidate_is_not_canonical_until_admitted",
    "blocked_target_cannot_pass_preparation_acceptance",
    "prepared_requires_independent_evidence_and_authorization",
    "learner_product_quality_is_separate_from_route_validity",
}

EXPECTED_CLOSURES = {
    "ESTABLISHED_CURRENT_SCOPE",
    "ESTABLISHED_CANONICAL_PREREQUISITE",
    "AUTHORABLE_EXTENSION",
    "UNRESOLVED_GAP",
    "IDENTITY_BLOCKED",
}
EXPECTED_MOVE_COVERAGE = {
    "UNTAUGHT",
    "TAUGHT_NO_EVIDENCE",
    "SUPPORTED_EVIDENCE",
    "INDEPENDENT_EVIDENCE",
}
EXPECTED_TARGET_COVERAGE = {
    "INCOMPLETE",
    "SUPPORTED_ONLY",
    "INDEPENDENT_EVIDENCE_COMPLETE",
}
EXPECTED_TARGET_AUTH = {
    "READY",
    "ACADEMIC_REVIEW_HOLD",
    "INSTRUCTIONAL_USE_HOLD",
    "IDENTITY_HOLD",
}
EXPECTED_TARGET_PREPARATION = {"PREPARED", "PARTIALLY_PREPARED", "BLOCKED"}


def discover_contract(role_dir: Path = ROLE_DIR) -> Path:
    matches = []
    for path in sorted(role_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if BLOCK.search(text):
            matches.append(path)
    if len(matches) != 1:
        raise ValueError(f"TARGET_DEMAND_ROUTING_DISCOVERY_FAILED:{len(matches)}")
    return matches[0]


def load_contract(path: Path | None = None) -> dict[str, Any]:
    path = path or discover_contract()
    text = path.read_text(encoding="utf-8")
    match = BLOCK.search(text)
    if not match:
        raise ValueError("TARGET_DEMAND_ROUTING_BLOCK_MISSING")
    value = json.loads(match.group(1))
    if not isinstance(value, dict):
        raise ValueError("TARGET_DEMAND_ROUTING_ROOT_NOT_OBJECT")
    return value


def audit_contract(path: Path | None = None) -> dict[str, Any]:
    findings: list[str] = []
    try:
        contract = load_contract(path)
    except Exception as exc:
        return {"passed": False, "findings": [str(exc)]}

    if contract.get("is_core_role") is not False:
        findings.append("TARGET_ROUTING_BECAME_CORE_ROLE")
    checks = [
        ("TARGET_ROUTING_CAPABILITY_CLOSURES_DRIFT", "capability_closure_states", EXPECTED_CLOSURES),
        ("TARGET_ROUTING_MOVE_COVERAGE_DRIFT", "move_coverage_states", EXPECTED_MOVE_COVERAGE),
        ("TARGET_ROUTING_TARGET_COVERAGE_DRIFT", "target_coverage_states", EXPECTED_TARGET_COVERAGE),
        ("TARGET_ROUTING_TARGET_AUTH_DRIFT", "target_authorization_states", EXPECTED_TARGET_AUTH),
        ("TARGET_ROUTING_TARGET_PREPARATION_DRIFT", "target_preparation_states", EXPECTED_TARGET_PREPARATION),
    ]
    for finding, key, expected in checks:
        if set(contract.get(key) or []) != expected:
            findings.append(finding)

    invariants = contract.get("invariants") or {}
    for name in sorted(REQUIRED_INVARIANTS):
        if invariants.get(name) is not True:
            findings.append(f"TARGET_ROUTING_INVARIANT_NOT_TRUE:{name}")

    required_bridge = {
        "bridge_id","target_refs","teaching_goal","prerequisite_refs",
        "mathematical_prerequisite_refs","required_new_capabilities",
        "grade_scope_decision","construction","representation_requirements",
        "worked_anchor","worked_solution_check","misconceptions","independent_check",
        "exit_task","independent_transfer_ref","authority_state","academic_review",
    }
    if set(contract.get("bridge_candidate_required_fields") or []) != required_bridge:
        findings.append("TARGET_ROUTING_BRIDGE_REQUIRED_FIELDS_DRIFT")
    return {
        "passed": not findings,
        "contract_version": contract.get("version"),
        "findings": findings,
    }


def _identity_findings(target: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    target_id = target.get("target_id")
    identity = target.get("identity") or {}
    state = identity.get("state")
    if state == "SEMANTIC_MATCH_RESOLVED":
        required_nonempty = [
            "candidate_set_provenance",
            "discriminating_features",
            "rejected_candidates",
            "resolution_decision",
            "resolution_reviewer",
        ]
        for key in required_nonempty:
            value = identity.get(key)
            if value in (None, "", []):
                findings.append(f"SEMANTIC_IDENTITY_MISSING_EVIDENCE:{target_id}:{key}")
        if identity.get("identity_confidence") not in {"HIGH", "MEDIUM"}:
            findings.append(f"SEMANTIC_IDENTITY_CONFIDENCE_TOO_LOW:{target_id}")
        exact_ref = identity.get("exact_ref")
        if not exact_ref:
            findings.append(f"SEMANTIC_IDENTITY_WITHOUT_EXACT_REF:{target_id}")
        rejected = {row.get("ref") for row in identity.get("rejected_candidates") or []}
        candidates = set(identity.get("candidate_refs") or [])
        if rejected - candidates:
            findings.append(f"SEMANTIC_IDENTITY_REJECTED_OUTSIDE_CANDIDATES:{target_id}")
    return findings


def _coverage_findings(target: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    target_id = target.get("target_id")
    moves = target.get("demand_moves") or []
    move_states = []
    for move in moves:
        move_id = move.get("move_id")
        coverage = move.get("coverage") or {}
        state = coverage.get("coverage_state")
        move_states.append(state)
        if coverage.get("target_use_ref") != target_id:
            findings.append(f"MOVE_TARGET_USE_MISMATCH:{target_id}:{move_id}")
        if state in {"TAUGHT_NO_EVIDENCE", "SUPPORTED_EVIDENCE", "INDEPENDENT_EVIDENCE"} and not coverage.get("teaching_refs"):
            findings.append(f"MOVE_TAUGHT_WITHOUT_TEACHING_REF:{target_id}:{move_id}")
        if state in {"SUPPORTED_EVIDENCE", "INDEPENDENT_EVIDENCE"} and not coverage.get("supported_attempt_refs"):
            findings.append(f"MOVE_SUPPORTED_WITHOUT_GUIDED_EVIDENCE:{target_id}:{move_id}")
        if state == "INDEPENDENT_EVIDENCE" and not coverage.get("independent_evidence_refs"):
            findings.append(f"MOVE_INDEPENDENT_WITHOUT_EVIDENCE:{target_id}:{move_id}")

    target_coverage = target.get("coverage_state")
    if moves and all(state == "INDEPENDENT_EVIDENCE" for state in move_states):
        expected = "INDEPENDENT_EVIDENCE_COMPLETE"
    elif moves and all(state in {"SUPPORTED_EVIDENCE", "INDEPENDENT_EVIDENCE"} for state in move_states):
        expected = "SUPPORTED_ONLY"
    else:
        expected = "INCOMPLETE"
    if target_coverage != expected:
        findings.append(f"TARGET_COVERAGE_STATE_MISMATCH:{target_id}:{target_coverage}:{expected}")
    return findings


def validate_route_artifact(value: dict[str, Any], repo: Path = REPO) -> list[str]:
    findings: list[str] = []
    try:
        import jsonschema
    except ModuleNotFoundError:
        return ["JSONSCHEMA_UNAVAILABLE"]

    schema = json.loads((repo / SCHEMA_PATH.relative_to(REPO)).read_text(encoding="utf-8"))
    validator = jsonschema.Draft202012Validator(schema)
    for error in validator.iter_errors(value):
        where = "/".join(str(x) for x in error.path)
        findings.append(f"SCHEMA:{where}:{error.message}")

    targets = [row for row in value.get("targets", []) if isinstance(row, dict)]
    target_ids = {row.get("target_id") for row in targets}
    bridge_rows = [row for row in value.get("bridge_candidates", []) if isinstance(row, dict)]
    bridge_by_id = {row.get("bridge_id"): row for row in bridge_rows}

    for target in targets:
        target_id = target.get("target_id")
        findings.extend(_identity_findings(target))
        findings.extend(_coverage_findings(target))

        moves = target.get("demand_moves") or []
        move_ids = {m.get("move_id") for m in moves if isinstance(m, dict)}
        route = target.get("target_route") or []
        terminal = target.get("terminal_block")
        preparation = target.get("preparation_state")
        coverage_state = target.get("coverage_state")
        authorization = target.get("authorization_state")

        if preparation == "BLOCKED" and not terminal:
            findings.append(f"TARGET_BLOCKED_WITHOUT_TERMINAL:{target_id}")
        if preparation != "BLOCKED" and not route:
            findings.append(f"TARGET_ACTIVE_WITHOUT_ROUTE:{target_id}")
        if preparation == "PREPARED":
            if coverage_state != "INDEPENDENT_EVIDENCE_COMPLETE":
                findings.append(f"PREPARED_WITHOUT_INDEPENDENT_COVERAGE:{target_id}")
            if authorization != "READY":
                findings.append(f"PREPARED_WITHOUT_AUTHORIZATION:{target_id}")
            if terminal:
                findings.append(f"PREPARED_WITH_TERMINAL_BLOCK:{target_id}")

        route_move_refs: set[str] = set()
        for node in route:
            refs = set(node.get("prepares_move_refs") or [])
            route_move_refs.update(refs)
            unknown = refs - move_ids
            if unknown:
                findings.append(f"ROUTE_UNKNOWN_MOVE:{target_id}:{','.join(sorted(unknown))}")
        missing_route_moves = move_ids - route_move_refs
        if route and missing_route_moves:
            findings.append(f"ROUTE_DOES_NOT_COVER_ALL_MOVES:{target_id}:{','.join(sorted(missing_route_moves))}")

        for move in moves:
            move_id = move.get("move_id")
            closure = (move or {}).get("closure") or {}
            state = closure.get("state")
            bridge_ref = closure.get("bridge_candidate_ref")
            if state == "AUTHORABLE_EXTENSION":
                bridge = bridge_by_id.get(bridge_ref)
                if not bridge:
                    findings.append(f"AUTHORABLE_EXTENSION_WITHOUT_BRIDGE:{target_id}:{move_id}")
                elif bridge.get("authority_state") != "ADMITTED":
                    if authorization == "READY":
                        findings.append(f"READY_WITH_UNADMITTED_EXTENSION:{target_id}:{move_id}")
            elif bridge_ref:
                findings.append(f"BRIDGE_REF_ON_NON_EXTENSION:{target_id}:{move_id}")
            if state in {"UNRESOLVED_GAP", "IDENTITY_BLOCKED"} and preparation == "PREPARED":
                findings.append(f"PREPARED_WITH_UNRESOLVED_MOVE:{target_id}:{move_id}")

        authority = target.get("authority") or {}
        if authority.get("instructional_demand_use") == "HOLD" and authorization == "READY":
            findings.append(f"READY_WHILE_INSTRUCTIONAL_USE_HELD:{target_id}")

    for bridge in bridge_rows:
        bridge_id = bridge.get("bridge_id")
        unknown_targets = set(bridge.get("target_refs") or []) - target_ids
        if unknown_targets:
            findings.append(f"BRIDGE_UNKNOWN_TARGET:{bridge_id}:{','.join(sorted(unknown_targets))}")
        review = bridge.get("academic_review") or {}
        state = bridge.get("authority_state")
        decision = review.get("decision")
        if state == "ADMITTED":
            if decision != "APPROVED" or not review.get("reviewer") or not review.get("evidence"):
                findings.append(f"ADMITTED_BRIDGE_WITHOUT_APPROVED_REVIEW:{bridge_id}")
        if state == "CANDIDATE" and decision == "APPROVED":
            findings.append(f"CANDIDATE_BRIDGE_CANNOT_CLAIM_APPROVED:{bridge_id}")
        if state == "REJECTED" and decision != "REJECTED":
            findings.append(f"REJECTED_BRIDGE_REVIEW_MISMATCH:{bridge_id}")

    moves_by_target = {
        target.get("target_id"): {m.get("move_id") for m in target.get("demand_moves") or []}
        for target in targets
    }
    for influence_row in value.get("core_demand_influences", []):
        for influence in influence_row.get("demand_influence_refs") or []:
            target_ref = influence.get("target_ref")
            move_ref = influence.get("move_ref")
            if target_ref not in target_ids:
                findings.append(f"INFLUENCE_UNKNOWN_TARGET:{target_ref}")
            elif move_ref not in moves_by_target.get(target_ref, set()):
                findings.append(f"INFLUENCE_UNKNOWN_MOVE:{target_ref}:{move_ref}")

    validation = value.get("validation") or {}
    acceptance = validation.get("fixed_target_preparation_acceptance")
    all_prepared = bool(targets) and all(t.get("preparation_state") == "PREPARED" for t in targets)
    if acceptance == "PASS" and not all_prepared:
        findings.append("PREPARATION_ACCEPTANCE_PASS_WITH_NONPREPARED_TARGET")
    if any(t.get("preparation_state") == "BLOCKED" for t in targets) and acceptance == "PASS":
        findings.append("BLOCKED_TARGET_COUNTED_AS_PREPARED")
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--artifact", type=Path)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit_contract()
    if args.artifact:
        value = json.loads(args.artifact.read_text(encoding="utf-8"))
        route_findings = validate_route_artifact(value)
        report["route_findings"] = route_findings
        report["passed"] = report["passed"] and not route_findings
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
