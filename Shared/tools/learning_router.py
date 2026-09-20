#!/usr/bin/env python3
"""Derive session-only learner routing posture from existing evidence.

This module does not own learner truth. learner_evidence.effective_state remains the
state owner and returns DEMONSTRATED / UNCERTAIN / MISSING / UNOBSERVED. The values here
are disposable next-action annotations: they may choose how much support to start with,
but they are never persisted as mastery evidence.

The deliberate asymmetry for MISSING protects against over-remediation. A conceptual or
setup failure (or an unattributed missing state) may justify rebuilding. A failure whose
recorded stage is EXECUTION or CARELESS is reinforced without declaring the underlying
concept missing.
"""
from __future__ import annotations

READY = "READY"
REINFORCE = "REINFORCE"
REBUILD = "REBUILD"

LOW = "low"
MEDIUM = "medium"
HIGH = "high"

GUIDED_RECONSTRUCTION = "GUIDED_RECONSTRUCTION"
PRACTICE = "PRACTICE"
TRANSFER = "TRANSFER"

POSTURE_SUPPORT = {
    READY: LOW,
    REINFORCE: MEDIUM,
    REBUILD: HIGH,
}

PROCEDURAL_ERROR_STAGES = {"EXECUTION", "CARELESS"}


def posture_for(learner_state: dict) -> str:
    """Return the Owner-defined, non-persisted routing posture for one capability."""
    state = learner_state.get("state", "UNOBSERVED")
    error_stage = learner_state.get("error_stage")

    if state == "DEMONSTRATED":
        return READY
    if state == "MISSING":
        if error_stage in PROCEDURAL_ERROR_STAGES:
            return REINFORCE
        return REBUILD
    return REINFORCE


def starting_support(posture: str) -> str:
    """Map a routing posture to pre-attempt support without touching the hint ladder."""
    return POSTURE_SUPPORT.get(posture, MEDIUM)


def decision(learner_state: dict) -> dict:
    """Project evidence into one inspectable session routing decision."""
    posture = posture_for(learner_state)
    return {
        "routing_posture": posture,
        "starting_support": starting_support(posture),
        "evidence_basis": {
            "state": learner_state.get("state", "UNOBSERVED"),
            "source": learner_state.get("source"),
            "observation_ref": learner_state.get("observation_ref"),
            "when": learner_state.get("when"),
            "help": learner_state.get("help"),
            "error_stage": learner_state.get("error_stage"),
        },
        "persistence": "NOT_WRITTEN",
    }


def _question_candidates(records: dict, capability_ref: str, core: str) -> list[dict]:
    """Canonical questions for one primary capability and one Core product."""
    return sorted(
        (
            row for row in records.values()
            if row.get("_collection") == "questions"
            and row.get("primary_capability_ref") == capability_ref
            and any(exposure.get("core") == core for exposure in row.get("exposure", []))
        ),
        key=lambda row: str(row.get("id") or ""),
    )


def visual_decision(records: dict, microtopic_refs: list[str], support: str) -> dict:
    """Resolve one canonical representation, its initial stage and existing explorers.

    Zero representations is a valid no-visual result. More than one is deliberately not
    guessed: the caller gets a finding instead of an arbitrary visual choice.
    """
    representation_refs = []
    for ref in microtopic_refs:
        microtopic = records.get(ref, {})
        for rep_ref in microtopic.get("representation_refs", []) or []:
            if rep_ref not in representation_refs:
                representation_refs.append(rep_ref)

    if not representation_refs:
        return {
            "representation_ref": None,
            "visual_stage_ref": None,
            "interactive_resource_refs": [],
            "finding": None,
        }
    if len(representation_refs) != 1:
        return {
            "representation_ref": None,
            "visual_stage_ref": None,
            "interactive_resource_refs": [],
            "finding": {
                "point": "LEARNING_ROUTER_VISUAL_AMBIGUOUS",
                "detail": (
                    "more than one canonical representation is available; "
                    "the runtime will not choose between academic representations"
                ),
                "candidates": representation_refs,
            },
        }

    rep_ref = representation_refs[0]
    representation = records.get(rep_ref)
    if not representation or representation.get("_collection") != "representations":
        return {
            "representation_ref": None,
            "visual_stage_ref": None,
            "interactive_resource_refs": [],
            "finding": {
                "point": "LEARNING_ROUTER_VISUAL_UNRESOLVED",
                "detail": f"{rep_ref} does not resolve to a canonical representation",
            },
        }

    stage_ref = next(
        (
            row.get("visual_stage_ref")
            for row in representation.get("support_stage_map", []) or []
            if row.get("support_level") == support
        ),
        None,
    )
    explorers = []
    for resource_ref in representation.get("interactive_resource_refs", []) or []:
        resource = records.get(resource_ref)
        if resource and resource.get("_collection") == "resources" and "ACTIVITY" in (resource.get("role") or []):
            explorers.append(resource_ref)

    return {
        "representation_ref": rep_ref,
        "visual_stage_ref": stage_ref,
        "interactive_resource_refs": explorers,
        "finding": (
            None if stage_ref else {
                "point": "LEARNING_ROUTER_VISUAL_STAGE_UNRESOLVED",
                "detail": (
                    f"{rep_ref} has no support-stage mapping for {support}; "
                    "the runtime will not invent an initial visual state"
                ),
            }
        ),
    }


def exercise_decision(
    posture: str,
    capability_ref: str,
    records: dict,
    *,
    prerequisites_ready: bool,
) -> dict:
    """Choose only an exercise-demand preference; canonical questions stay authoritative."""
    if posture == REBUILD:
        return {
            "demand": GUIDED_RECONSTRUCTION,
            "question_ref": None,
            "reason": "concept/setup evidence requires reconstruction before independent practice",
        }

    practice = _question_candidates(records, capability_ref, "CORE2A")
    transfer = _question_candidates(records, capability_ref, "CORE2B")
    if posture == READY and prerequisites_ready and transfer:
        return {
            "demand": TRANSFER,
            "question_ref": transfer[0]["id"],
            "reason": "independent evidence and prerequisite readiness permit changed-demand transfer",
        }

    return {
        "demand": PRACTICE,
        "question_ref": practice[0]["id"] if practice else None,
        "reason": (
            "reinforce with same-family practice"
            if posture == REINFORCE
            else "transfer is not yet safe or available; retain supported practice"
        ),
    }


def route_decision(
    learner_state: dict,
    *,
    capability_ref: str,
    microtopic_refs: list[str],
    records: dict,
    prerequisites_ready: bool,
) -> dict:
    """Combine evidence, canonical visuals and exercise demand into one disposable route."""
    routed = decision(learner_state)
    visual = visual_decision(records, microtopic_refs, routed["starting_support"])
    exercise = exercise_decision(
        routed["routing_posture"],
        capability_ref,
        records,
        prerequisites_ready=prerequisites_ready,
    )
    explorers = list(visual.get("interactive_resource_refs") or [])
    return {
        **routed,
        "initial_visual": {
            "representation_ref": visual.get("representation_ref"),
            "visual_stage_ref": visual.get("visual_stage_ref"),
            "interactive_resource_refs": explorers,
        },
        "recommended_explorer_ref": (
            explorers[0]
            if routed["routing_posture"] == REBUILD and len(explorers) == 1
            else None
        ),
        "exercise_demand": exercise["demand"],
        "exercise_question_ref": exercise["question_ref"],
        "exercise_reason": exercise["reason"],
        "routing_findings": [visual["finding"]] if visual.get("finding") else [],
    }
