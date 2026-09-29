#!/usr/bin/env python3
"""Classify WebResolutionPlan findings into academic truth gaps vs engineering work.

This module is deliberately downstream of the merged #284 resolver. A WebResolutionPlan may
truthfully say that the requested learner artifact is not release-ready. That must not be
misread as permission logic for the Interactive Agent. Engineering-only gaps produce useful
work (`BUILD_LOCAL_OR_REUSABLE`); unresolved academic truth limits learner-complete claims but
still permits research/prototyping.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load


ACADEMIC_EXACT_CODES = {
    "WEB_REQUEST_STRUCTURE",
    "WEB_SUBJECT_UNAVAILABLE",
    "WEB_TARGET_UNRESOLVED",
    "WEB_TARGET_AMBIGUOUS",
    "WEB_CANONICAL_REF_INVALID",
    "WEB_ATLAS_CANONICAL_DIVERGENCE",
    "WEB_CORE_SEMANTICS_UNAVAILABLE",
    "WEB_TARGET_NOT_PREPARED",
    "WEB_TARGET_COVERAGE_INCOMPLETE",
    "WEB_TARGET_AUTHORIZATION_MISSING",
}
ACADEMIC_PREFIXES = (
    "WEB_TARGET_ROUTE_",
)
ENGINEERING_EXACT_CODES = {
    "WEB_REQUIRED_INTERACTION_UNAVAILABLE",
    "WEB_RENDERER_UNAVAILABLE",
    "WEB_ACTIVITY_BINDING_INVALID",
}


def _code(row: dict) -> str:
    value = row.get("code")
    return value if isinstance(value, str) else "WEB_UNKNOWN_FINDING"


def _is_academic_finding(row: dict) -> bool:
    code = _code(row)
    return code in ACADEMIC_EXACT_CODES or code.startswith(ACADEMIC_PREFIXES)


def _is_engineering_finding(row: dict) -> bool:
    return _code(row) in ENGINEERING_EXACT_CODES


def _required_unready(plan: dict, dimension: str) -> bool:
    row = (plan.get("availability") or {}).get(dimension) or {}
    return row.get("requirement") == "REQUIRED" and row.get("status") not in {"READY", "NOT_REQUIRED"}


def _interaction_required(plan: dict) -> bool:
    return any(
        segment.get("interaction_requirement") == "REQUIRED"
        for segment in plan.get("experience_segments") or []
    )


def classify(
    plan: dict,
    *,
    brief_freshness: dict | None = None,
) -> dict[str, Any]:
    """Return an advisory engineering continuation disposition, never a permission gate."""
    findings = [row for row in plan.get("findings") or [] if isinstance(row, dict)]
    academic = [row for row in findings if _is_academic_finding(row)]
    engineering = [row for row in findings if _is_engineering_finding(row)]
    other = [
        row for row in findings
        if row not in academic and row not in engineering
    ]

    # Required canonical representation/Core semantics are academic-completion inputs.
    # A missing activity/renderer is engineering work once those truth-bearing inputs exist.
    if _required_unready(plan, "core"):
        academic.append({
            "code": "INTERACTION_ACADEMIC_CORE_UNRESOLVED",
            "detail": "Required Core semantics are not resolved for learner-complete delivery.",
        })
    if _required_unready(plan, "mapping"):
        academic.append({
            "code": "INTERACTION_ACADEMIC_MAPPING_UNRESOLVED",
            "detail": "Canonical target mapping is not resolved for learner-complete delivery.",
        })
    if _required_unready(plan, "representation"):
        academic.append({
            "code": "INTERACTION_ACADEMIC_REPRESENTATION_UNRESOLVED",
            "detail": "A required truth-bearing representation is not resolved.",
        })

    if brief_freshness is not None and brief_freshness.get("status") != "CURRENT":
        academic.append({
            "code": "INTERACTION_BRIEF_NOT_CURRENT",
            "detail": (
                "The derived Interaction Brief no longer matches its canonical academic basis; "
                "research/prototyping may continue, but learner-complete claims must use current truth."
            ),
            "brief_status": brief_freshness.get("status"),
        })

    needs_interaction_engineering = (
        _interaction_required(plan)
        and not academic
        and _required_unready(plan, "activity")
    )
    if needs_interaction_engineering and not any(
        _code(row) == "WEB_REQUIRED_INTERACTION_UNAVAILABLE" for row in engineering
    ):
        engineering.append({
            "code": "INTERACTION_LOCAL_IMPLEMENTATION_REQUIRED",
            "detail": (
                "Academic truth is sufficient but no governed required interaction binding is ready; "
                "build or bind a LOCAL/reusable implementation through the existing runtime/package path."
            ),
        })

    if academic:
        action = "RESEARCH_ACADEMIC_GAP_AND_PROTOTYPE"
        learner_completion = "ACADEMICALLY_UNRESOLVED"
    elif needs_interaction_engineering or engineering:
        action = "BUILD_LOCAL_OR_REUSABLE"
        learner_completion = "ENGINEERING_IMPLEMENTATION_REQUIRED"
    elif plan.get("request_satisfaction") in {"FULL", "DEGRADED_ACCEPTABLE"}:
        action = "USE_RESOLVED_DELIVERY"
        learner_completion = "DELIVERY_RESOLVED"
    else:
        # Unknown non-academic findings are still reported; they do not create an agent permission state.
        action = "RESEARCH_AND_IMPLEMENT_BEST_TRUTHFUL_PATH"
        learner_completion = "UNRESOLVED_FINDINGS"

    return {
        "schema_version": "1.0.0",
        "authority": "DERIVED_ENGINEERING_CONTINUATION_ONLY",
        "request_id": plan.get("request_id"),
        "subject": plan.get("subject"),
        "research_may_continue": True,
        "action": action,
        "learner_completion_state": learner_completion,
        "release_ready_from_source_plan": (
            plan.get("artifact_buildable") is True
            and plan.get("request_satisfaction") in {"FULL", "DEGRADED_ACCEPTABLE"}
        ),
        "academic_findings": academic,
        "engineering_findings": engineering,
        "other_findings": other,
        "runtime_invariant": (
            "LOCAL means not promoted to shared reuse architecture; learner delivery still requires "
            "deterministic governed scene/adapter/activity/package identity."
        ),
        "evidence_note": (
            "Missing reuse metadata is reconstruction debt. Concrete lineage evidence is required "
            "only when claiming REUSED or SHARED maturity."
        ),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--brief-freshness", type=Path)
    args = parser.parse_args()
    result = classify(
        load(args.plan),
        brief_freshness=load(args.brief_freshness) if args.brief_freshness else None,
    )
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
