#!/usr/bin/env python3
"""Derive session-only learner routing posture from existing evidence.

This module does not own learner truth. learner_evidence.effective_state remains the
state owner and returns DEMONSTRATED / UNCERTAIN / MISSING / UNOBSERVED. The values here
are disposable next-action annotations: they may choose how much support to start with,
but they are never persisted as mastery evidence.

READY is deliberately strict: only evidence whose current effective projection explicitly
proves an independent attempt may route READY. A bare DEMONSTRATED label is not enough.

Starting support is a two-stage decision. Posture requests a level; the active matrix
family's support_ladder decides whether that level actually exists. Missing, ambiguous or
undeclared family support is withheld and reported rather than guessed.
"""
from __future__ import annotations

from pathlib import Path

from Shared.contracts import load

REPO = Path(__file__).resolve().parents[2]

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


def _independence_proven(learner_state: dict) -> bool:
    """Accept explicit derived proof, or the equivalent explicit legacy provenance pair."""
    if "independence_proven" in learner_state:
        return learner_state.get("independence_proven") is True
    return (
        learner_state.get("source") == "DIRECT_ATTEMPT"
        and learner_state.get("help") == "NONE"
    )


def posture_for(learner_state: dict) -> str:
    """Return the Owner-defined, non-persisted routing posture for one capability."""
    state = learner_state.get("state", "UNOBSERVED")
    error_stage = learner_state.get("error_stage")

    if state == "DEMONSTRATED":
        return READY if _independence_proven(learner_state) else REINFORCE
    if state == "MISSING":
        if error_stage in PROCEDURAL_ERROR_STAGES:
            return REINFORCE
        return REBUILD
    return REINFORCE


def requested_support(posture: str) -> str:
    """Return the pre-attempt support level requested by posture, not availability."""
    return POSTURE_SUPPORT.get(posture, MEDIUM)


def family_support_context(
    microtopic_refs: list[str],
    repo: Path = REPO,
) -> dict:
    """Resolve the one matrix family governing the active route, or fail closed."""
    wanted = {ref for ref in microtopic_refs if ref}
    matches = []
    if wanted:
        for path in sorted(repo.glob("*/matrices/*.rungs.json")):
            board = load(path)
            board_microtopics = {
                rung.get("microtopic_ref")
                for rung in board.get("rungs", []) or []
                if rung.get("microtopic_ref")
            }
            if wanted & board_microtopics:
                matches.append({
                    "family_ref": board.get("matrix_id"),
                    "source": str(path.relative_to(repo)),
                    "support_ladder": list((board.get("family") or {}).get("support_ladder") or []),
                })

    if not matches:
        return {
            "status": "MISSING",
            "family_ref": None,
            "source": None,
            "support_ladder": [],
            "candidates": [],
        }
    if len(matches) != 1:
        return {
            "status": "AMBIGUOUS",
            "family_ref": None,
            "source": None,
            "support_ladder": [],
            "candidates": [row.get("family_ref") for row in matches],
        }
    return {"status": "RESOLVED", **matches[0], "candidates": [matches[0].get("family_ref")]}


def resolve_support(requested: str, family_context: dict) -> dict:
    """Resolve requested support only against declared active-family availability."""
    status = family_context.get("status")
    if status != "RESOLVED":
        point = (
            "LEARNING_ROUTER_SUPPORT_FAMILY_AMBIGUOUS"
            if status == "AMBIGUOUS"
            else "LEARNING_ROUTER_SUPPORT_FAMILY_MISSING"
        )
        return {
            "requested_support": requested,
            "starting_support": None,
            "support_status": "WITHHELD",
            "finding": {
                "point": point,
                "detail": (
                    "active family support authority is ambiguous; support is withheld"
                    if status == "AMBIGUOUS"
                    else "active family support authority is missing; support is withheld"
                ),
                "candidates": list(family_context.get("candidates") or []),
            },
        }

    declared = [
        row.get("level")
        for row in family_context.get("support_ladder", []) or []
        if isinstance(row, dict) and isinstance(row.get("level"), str)
    ]
    if requested not in declared:
        return {
            "requested_support": requested,
            "starting_support": None,
            "support_status": "WITHHELD",
            "finding": {
                "point": "LEARNING_ROUTER_SUPPORT_UNDECLARED",
                "detail": (
                    f"{family_context.get('family_ref')} does not declare requested "
                    f"support level {requested}; support is withheld"
                ),
                "family_ref": family_context.get("family_ref"),
                "requested_support": requested,
                "declared_levels": declared,
            },
        }

    return {
        "requested_support": requested,
        "starting_support": requested,
        "support_status": "RESOLVED",
        "finding": None,
    }


def decision(learner_state: dict) -> dict:
    """Project evidence into posture and a requested, not yet authorized, support level."""
    posture = posture_for(learner_state)
    return {
        "routing_posture": posture,
        "requested_support": requested_support(posture),
        "starting_support": None,
        "support_status": "UNRESOLVED",
        "evidence_basis": {
            "state": learner_state.get("state", "UNOBSERVED"),
            "source": learner_state.get("source"),
            "observation_ref": learner_state.get("observation_ref"),
            "when": learner_state.get("when"),
            "help": learner_state.get("help"),
            "error_stage": learner_state.get("error_stage"),
            "independence_proven": _independence_proven(learner_state),
            "independence_basis": (
                learner_state.get("independence_basis")
                or (
                    "DIRECT_ATTEMPT_WITH_NO_HELP"
                    if _independence_proven(learner_state)
                    else "NOT_PROVEN"
                )
            ),
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


def visual_decision(records: dict, microtopic_refs: list[str], support: str | None) -> dict:
    """Resolve one canonical representation, its initial stage and existing explorers.

    Zero representations is a valid no-visual result. More than one is deliberately not
    guessed. If starting support is withheld, the representation may still resolve but
    no initial support stage is selected.
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

    explorers = []
    for resource_ref in representation.get("interactive_resource_refs", []) or []:
        resource = records.get(resource_ref)
        if resource and resource.get("_collection") == "resources" and "ACTIVITY" in (resource.get("role") or []):
            explorers.append(resource_ref)

    if support is None:
        return {
            "representation_ref": rep_ref,
            "visual_stage_ref": None,
            "interactive_resource_refs": explorers,
            "finding": None,
        }

    stage_ref = next(
        (
            row.get("visual_stage_ref")
            for row in representation.get("support_stage_map", []) or []
            if row.get("support_level") == support
        ),
        None,
    )
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
    repo: Path = REPO,
) -> dict:
    """Combine evidence, family-authorized support, visuals and exercise demand."""
    routed = decision(learner_state)
    family_context = family_support_context(microtopic_refs, repo)
    support = resolve_support(routed["requested_support"], family_context)
    visual = visual_decision(records, microtopic_refs, support["starting_support"])
    exercise = exercise_decision(
        routed["routing_posture"],
        capability_ref,
        records,
        prerequisites_ready=prerequisites_ready,
    )
    explorers = list(visual.get("interactive_resource_refs") or [])
    findings = []
    if support.get("finding"):
        findings.append(support["finding"])
    if visual.get("finding"):
        findings.append(visual["finding"])
    return {
        **routed,
        "starting_support": support["starting_support"],
        "support_status": support["support_status"],
        "support_family_ref": family_context.get("family_ref"),
        "support_family_source": family_context.get("source"),
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
        "routing_findings": findings,
    }
