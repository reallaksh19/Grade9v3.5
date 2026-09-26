#!/usr/bin/env python3
"""Apply typed owner decisions to an authoring request and immediately re-plan it."""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import digest, load  # noqa: E402
from Shared.tools import plan_request  # noqa: E402

SCHEMA = REPO / "Shared/library/owner-decisions.schema.json"


def _schema_findings(value: dict, repo: Path = REPO) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(load(repo / "Shared/library/owner-decisions.schema.json"))
    return [{
        "point": "OWNER_DECISIONS_STRUCTURE",
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(value)]


def plan_digest(plan: dict) -> str:
    """Digest the planner result that defines which owner decisions are currently legal."""
    return digest(plan)


DEFAULT_FIELDS = {
    "learner": "LEARNER_ENTRY",
    "practice.CORE2A.purpose": "CORE2A_PURPOSE",
    "practice.CORE2B.purpose": "CORE2B_PURPOSE",
    "supplemental_question_policy": "SUPPLEMENTAL_QUESTION_POLICY",
}
ACTION_DECISIONS = {
    "RESEARCH_SOURCE_BASIS": "SOURCE_BASIS",
    "RESOLVE_SOURCE_BASIS_DRIFT": "SOURCE_BASIS_DRIFT_DECISION",
}


def overridable(plan: dict) -> list[str]:
    """Owner decisions that may override what the planner defaulted or assigned to the agent.

    The planner never waits for these: it applies a default or gives the agent a research
    duty. The owner may still override either, and only those.
    """
    ids = {DEFAULT_FIELDS[row["field"]] for row in plan.get("defaults_applied", [])
           if row["field"] in DEFAULT_FIELDS}
    ids |= {ACTION_DECISIONS[row["id"]] for row in plan.get("agent_actions", [])
            if row["id"] in ACTION_DECISIONS}
    return sorted(ids)


def template(request: dict, repo: Path = REPO) -> dict:
    plan = plan_request.plan(request, repo)
    artifact = {
        "decision_id": f'DEC-{request.get("request_id", "UNNAMED")}',
        "version": "1.0.0",
        "request_id": request.get("request_id"),
        "request_digest": digest(request),
        "plan_digest": plan_digest(plan),
        "decisions": {},
    }
    return {
        "artifact": artifact,
        "overridable_decisions": overridable(plan),
    }


def _learner_value(value: dict) -> dict:
    kind = value["kind"]
    if kind == "profile_ref":
        return {"profile_ref": value["profile_ref"]}
    if kind == "owner_entry":
        return {"owner_entry": {
            "rung": value["rung"],
            "by": "owner",
            **({"instruction": value["instruction"]} if value.get("instruction") else {}),
        }}
    if kind == "owner_estimate":
        return {"owner_estimate": {
            "knowledge_percentage": value["knowledge_percentage"],
            "by": "owner",
            **({"instruction": value["instruction"]} if value.get("instruction") else {}),
        }}
    return {"unknown": {
        "by": "owner",
        **({"instruction": value["instruction"]} if value.get("instruction") else {}),
    }}


def _request_schema_findings(request: dict, repo: Path = REPO) -> list[dict]:
    try:
        import jsonschema
    except ModuleNotFoundError:
        return []
    validator = jsonschema.Draft202012Validator(
        load(repo / "Shared/library/authoring-request.schema.json"))
    return [{
        "point": "OWNER_DECISION_RESULT_REQUEST_STRUCTURE",
        "where": "/".join(str(part) for part in error.path),
        "detail": error.message,
    } for error in validator.iter_errors(request)]


def apply(request: dict, decisions: dict, repo: Path = REPO) -> dict:
    found = _schema_findings(decisions, repo)

    def fail(point: str, where: str, detail: str) -> None:
        found.append({"point": point, "where": where, "detail": detail})

    current_plan = plan_request.plan(request, repo)
    if decisions.get("request_id") != request.get("request_id"):
        fail("OWNER_DECISIONS_REQUEST_ID_MISMATCH", decisions.get("request_id", ""),
             "decision artifact does not name this request")
    if decisions.get("request_digest") != digest(request):
        fail("OWNER_DECISIONS_REQUEST_STALE", request.get("request_id", ""),
             "request changed after these decisions were prepared")
    if decisions.get("plan_digest") != plan_digest(current_plan):
        fail("OWNER_DECISIONS_PLAN_STALE", request.get("request_id", ""),
             "planner output changed after these decisions were prepared")

    legal = set(overridable(current_plan))
    supplied = decisions.get("decisions", {})
    for decision_id in supplied:
        if decision_id not in legal:
            fail("OWNER_DECISION_UNSOLICITED", decision_id,
                 "the pinned plan neither defaulted this input nor assigned it to the agent")

    patched = copy.deepcopy(request)
    if found:
        return {
            "passed": False,
            "findings": found,
            "request_before": request,
            "request_after": None,
            "plan_before": current_plan,
            "plan_after": None,
        }

    for decision_id, value in supplied.items():
        if decision_id == "LEARNER_ENTRY":
            patched["learner"] = _learner_value(value)

        elif decision_id == "CORE2A_PURPOSE":
            patched.setdefault("practice", {}).setdefault("CORE2A", {})["purpose"] = value

        elif decision_id == "CORE2B_PURPOSE":
            patched.setdefault("practice", {}).setdefault("CORE2B", {})["purpose"] = value

        elif decision_id == "SOURCE_BASIS":
            patched["source_basis"] = list(value)
            patched.pop("source_receipt_ref", None)
            patched.pop("source_basis_drift_acknowledgement", None)
            patched.pop("supplemental_question_policy", None)

        elif decision_id == "SOURCE_BASIS_DRIFT_DECISION":
            action = value["action"]
            if action == "KEEP_SUPPLIED_DESPITE_DRIFT":
                patched["source_basis_drift_acknowledgement"] = action
            else:
                candidates = set(
                    ((current_plan.get("source") or {}).get("basis_assessment") or {})
                    .get("replacement_candidates") or []
                )
                replacement = list(value["replacement_source_basis"])
                if not replacement or any(locator not in candidates for locator in replacement):
                    fail("OWNER_SOURCE_REPLACEMENT_NOT_OFFERED",
                         ",".join(replacement),
                         "replacement source basis must be one of the planner's receipt-backed candidates")
                    continue
                patched["source_basis"] = replacement
                patched.pop("source_receipt_ref", None)
                patched.pop("source_basis_drift_acknowledgement", None)
                # A policy chosen against the old source gap is stale after replacement.
                patched.pop("supplemental_question_policy", None)

        elif decision_id == "SUPPLEMENTAL_QUESTION_POLICY":
            patched["supplemental_question_policy"] = value

    if found:
        return {
            "passed": False,
            "findings": found,
            "request_before": request,
            "request_after": None,
            "plan_before": current_plan,
            "plan_after": None,
        }

    found.extend(_request_schema_findings(patched, repo))
    if found:
        return {
            "passed": False,
            "findings": found,
            "request_before": request,
            "request_after": None,
            "plan_before": current_plan,
            "plan_after": None,
        }

    after = plan_request.plan(patched, repo)
    return {
        "passed": True,
        "findings": [],
        "decision_id": decisions.get("decision_id"),
        "request_id": request.get("request_id"),
        "request_digest_before": digest(request),
        "request_digest_after": digest(patched),
        "plan_digest_before": plan_digest(current_plan),
        "plan_digest_after": plan_digest(after),
        "applied_decisions": sorted(supplied),
        "request_after": patched,
        "plan_after": after,
        "remaining_overridable": overridable(after),
        "agent_actions": [row["id"] for row in after.get("agent_actions", [])],
    }


def audit(repo: Path = REPO) -> dict:
    """Prove every owner override the planner offers has a typed application path."""
    schema = load(repo / "Shared/library/owner-decisions.schema.json")
    supported = set(
        schema["properties"]["decisions"]["properties"]
    )
    rows, findings = [], []
    for path in sorted((repo / "Requests").glob("*.plan-request.json")):
        request = load(path)
        plan = plan_request.plan(request, repo)
        offered = overridable(plan)
        unsupported = sorted(set(offered) - supported)
        row_findings = [{
            "point": "OWNER_DECISION_APPLICATION_UNSUPPORTED",
            "where": decision_id,
            "detail": "planner offers an owner override with no typed application contract",
        } for decision_id in unsupported]
        if plan.get("required_owner_inputs"):
            row_findings.append({"point": "PLANNER_WAITS_ON_OWNER", "where": str(path.relative_to(repo)),
                                 "detail": "the planner must default or research, never wait"})
        rows.append({
            "path": str(path.relative_to(repo)),
            "overridable_decisions": offered,
            "supported": not unsupported,
            "findings": row_findings,
        })
        findings.extend(row_findings)
    return {
        "plan_fixtures": len(rows),
        "supported_decision_ids": sorted(supported),
        "rows": rows,
        "findings": findings,
        "passed": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--request", type=Path)
    parser.add_argument("--decisions", type=Path)
    parser.add_argument("--template", action="store_true")
    parser.add_argument("--audit", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    if args.audit:
        report = audit()
    elif args.template:
        if not args.request:
            parser.error("--template requires --request")
        report = template(load(args.request))
    else:
        if not args.request or not args.decisions:
            parser.error("apply requires --request and --decisions")
        report = apply(load(args.request), load(args.decisions))

    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report.get("passed", True) else 0


if __name__ == "__main__":
    raise SystemExit(main())
