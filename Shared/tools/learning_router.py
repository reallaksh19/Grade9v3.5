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
                matched_rungs = [
                    rung.get("rung")
                    for rung in board.get("rungs", []) or []
                    if rung.get("microtopic_ref") in wanted and rung.get("rung")
                ]
                transfer_dimensions = []
                for transfer in board.get("transfer", []) or []:
                    if transfer.get("repair_to") in matched_rungs and transfer.get("dimension"):
                        dimension = transfer["dimension"]
                        if dimension not in transfer_dimensions:
                            transfer_dimensions.append(dimension)
                matches.append({
                    "family_ref": board.get("matrix_id"),
                    "source": str(path.relative_to(repo)),
                    "support_ladder": list((board.get("family") or {}).get("support_ladder") or []),
                    "matched_rungs": matched_rungs,
                    "transfer_dimensions": transfer_dimensions,
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


def _question_candidates(records: dict, capability_ref: str, core: str,
                         *, family_ref: str | None = None,
                         transfer_dimensions: list[str] | None = None) -> list[dict]:
    """Canonical candidates filtered by capability, family and declared demand."""
    dimensions = set(transfer_dimensions or [])
    rows = []
    for row in records.values():
        if row.get("_collection") != "questions":
            continue
        if row.get("primary_capability_ref") != capability_ref:
            continue
        if not any(exposure.get("core") == core for exposure in row.get("exposure", [])):
            continue
        if family_ref is not None and row.get("family_ref") != family_ref:
            continue
        if core == "CORE2B" and dimensions:
            if (row.get("transfer") or {}).get("dimension") not in dimensions:
                continue
        rows.append(row)

    dimension_order = {value: index for index, value in enumerate(transfer_dimensions or [])}
    return sorted(
        rows,
        key=lambda row: (
            dimension_order.get((row.get("transfer") or {}).get("dimension"), 999),
            int((row.get("answer") or {}).get("difficult_move") or 0),
            str(row.get("id") or ""),
        ),
    )


def _stable_independent_family(evidence_history: list[dict], records: dict,
                               capability_ref: str,
                               allowed_families: list[str]) -> dict:
    """Require two distinct independent canonical questions in one family."""
    grouped: dict[str, dict[str, str]] = {}
    for observation in evidence_history or []:
        if observation.get("evidence_kind") != "DIRECT_ATTEMPT":
            continue
        if observation.get("result") != "DEMONSTRATED" or observation.get("help") != "NONE":
            continue
        question_ref = observation.get("question_ref")
        question = records.get(question_ref)
        if not question or question.get("_collection") != "questions":
            continue
        if question.get("primary_capability_ref") != capability_ref:
            continue
        family_ref = question.get("family_ref")
        if not family_ref:
            continue
        if allowed_families and family_ref not in allowed_families:
            continue
        grouped.setdefault(family_ref, {})[question_ref] = observation.get("observation_id") or question_ref

    stable = [family for family, questions in grouped.items() if len(questions) >= 2]
    if len(stable) != 1:
        return {
            "eligible": False,
            "family_ref": None,
            "independent_question_refs": [],
            "reason": (
                "stable independent same-family evidence is ambiguous"
                if len(stable) > 1
                else "fewer than two distinct independent same-family canonical questions are demonstrated"
            ),
        }
    family_ref = stable[0]
    return {
        "eligible": True,
        "family_ref": family_ref,
        "independent_question_refs": sorted(grouped[family_ref]),
        "reason": "two or more distinct independent canonical questions are demonstrated in one family",
    }


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
    evidence_history: list[dict] | None = None,
    active_question_families: list[str] | None = None,
    transfer_dimensions: list[str] | None = None,
) -> dict:
    """Choose demand from canonical family/demand authority; READY alone never transfers."""
    if posture == REBUILD:
        return {
            "demand": GUIDED_RECONSTRUCTION,
            "question_ref": None,
            "family_ref": None,
            "transfer_dimension": None,
            "transfer_eligible": False,
            "reason": "concept/setup evidence requires reconstruction before independent practice",
            "finding": None,
        }

    explicit_families = list(dict.fromkeys(active_question_families or []))
    stability = _stable_independent_family(
        evidence_history or [], records, capability_ref, explicit_families
    )
    family_ref = explicit_families[0] if len(explicit_families) == 1 else stability.get("family_ref")

    if len(explicit_families) > 1:
        family_finding = {
            "point": "LEARNING_ROUTER_EXERCISE_FAMILY_AMBIGUOUS",
            "detail": "worksheet demand resolves to more than one canonical question family; no question is guessed",
            "candidates": explicit_families,
        }
    else:
        family_finding = None

    practice = _question_candidates(
        records, capability_ref, "CORE2A", family_ref=family_ref
    ) if family_ref else []
    transfer = _question_candidates(
        records,
        capability_ref,
        "CORE2B",
        family_ref=family_ref,
        transfer_dimensions=transfer_dimensions,
    ) if family_ref and transfer_dimensions else []

    transfer_eligible = bool(
        posture == READY
        and prerequisites_ready
        and stability.get("eligible")
        and stability.get("family_ref") == family_ref
        and transfer
    )
    if transfer_eligible:
        chosen = transfer[0]
        return {
            "demand": TRANSFER,
            "question_ref": chosen["id"],
            "family_ref": family_ref,
            "transfer_dimension": (chosen.get("transfer") or {}).get("dimension"),
            "transfer_eligible": True,
            "transfer_evidence": stability.get("independent_question_refs"),
            "reason": "stable independent same-family evidence, prerequisites and canonical transfer demand all agree",
            "finding": family_finding,
        }

    if family_ref is None and not family_finding:
        candidate_families = sorted({
            row.get("family_ref")
            for row in _question_candidates(records, capability_ref, "CORE2A")
            if row.get("family_ref")
        })
        if len(candidate_families) == 1:
            family_ref = candidate_families[0]
            practice = _question_candidates(records, capability_ref, "CORE2A", family_ref=family_ref)
        elif candidate_families:
            family_finding = {
                "point": "LEARNING_ROUTER_EXERCISE_FAMILY_UNRESOLVED",
                "detail": "multiple canonical practice families exist and the active worksheet does not choose one",
                "candidates": candidate_families,
            }

    return {
        "demand": PRACTICE,
        "question_ref": practice[0]["id"] if practice else None,
        "family_ref": family_ref,
        "transfer_dimension": None,
        "transfer_eligible": False,
        "transfer_evidence": stability.get("independent_question_refs") or [],
        "reason": (
            stability.get("reason")
            if posture == READY and prerequisites_ready
            else "transfer prerequisites are not yet satisfied; retain family-compatible practice"
        ),
        "finding": family_finding,
    }


def route_decision(
    learner_state: dict,
    *,
    capability_ref: str,
    microtopic_refs: list[str],
    records: dict,
    prerequisites_ready: bool,
    evidence_history: list[dict] | None = None,
    active_question_families: list[str] | None = None,
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
        evidence_history=evidence_history,
        active_question_families=active_question_families,
        transfer_dimensions=family_context.get("transfer_dimensions") or [],
    )
    explorers = list(visual.get("interactive_resource_refs") or [])
    findings = []
    if support.get("finding"):
        findings.append(support["finding"])
    if visual.get("finding"):
        findings.append(visual["finding"])
    if exercise.get("finding"):
        findings.append(exercise["finding"])
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
        "exercise_family_ref": exercise.get("family_ref"),
        "transfer_eligible": exercise.get("transfer_eligible", False),
        "transfer_dimension": exercise.get("transfer_dimension"),
        "transfer_evidence": exercise.get("transfer_evidence", []),
        "routing_findings": findings,
    }
