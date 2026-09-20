#!/usr/bin/env python3
"""Project validated diagnostic targets into Core-specific emphasis.

This is an emphasis overlay only. It cannot make a Core READY, clear prerequisites,
change a teaching segment, alter practice purpose/support, or invent a new Core type.
"""
from __future__ import annotations

ALL_CORES = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")

DIMENSION_EMPHASIS = {
    "CONCEPT": "CONCEPT_FOCUS",
    "SETUP": "SETUP_FOCUS",
    "EXECUTION": "EXECUTION_FOCUS",
    "CARELESS": "CARELESS_CHECK_FOCUS",
    "UNKNOWN": "UNSPECIFIED_DIAGNOSTIC_FOCUS",
}


def for_core(core: str, targets: list[dict] | None) -> dict:
    if core not in ALL_CORES:
        raise ValueError(f"unknown Core {core}")
    projected = []
    for target in targets or []:
        projected.append({
            "address": target.get("address"),
            "capability_ref": target.get("capability_ref"),
            "repair_ref": target.get("repair_ref"),
            "error_stage": target.get("error_stage"),
            "dimension_emphasis": DIMENSION_EMPHASIS.get(
                target.get("error_stage"), "UNSPECIFIED_DIAGNOSTIC_FOCUS"
            ),
            "fallback_level": target.get("fallback_level"),
            "result": target.get("result"),
            "score": target.get("score"),
        })
    return {
        "core": core,
        "targets": projected,
        "policy": (
            "diagnostic focus changes emphasis only; existing Core role, purpose/support, "
            "canonical coverage, readiness, prerequisite and source-custody rules remain authoritative"
        ),
    }


def for_cores(cores: list[str], targets: list[dict] | None) -> dict[str, dict]:
    return {core: for_core(core, targets) for core in cores}
