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
