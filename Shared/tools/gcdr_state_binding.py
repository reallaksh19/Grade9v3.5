#!/usr/bin/env python3
"""Resolve an external task payload into governed GCDR activity state.

The resolver is deliberately fail-closed:
- it never invents missing values;
- it never upgrades a partial mapping to EXACT;
- CUSTOM_DECLARED transforms require a subject adapter rather than hidden defaults.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


class BindingError(ValueError):
    pass


_MISSING = object()


def resolve_pointer(document: Any, pointer: str) -> Any:
    if not pointer.startswith("/"):
        raise BindingError(f"not an absolute JSON pointer: {pointer!r}")
    current = document
    for raw in pointer[1:].split("/"):
        token = raw.replace("~1", "/").replace("~0", "~")
        if isinstance(current, list):
            try:
                current = current[int(token)]
            except (ValueError, IndexError) as exc:
                raise KeyError(pointer) from exc
        elif isinstance(current, dict) and token in current:
            current = current[token]
        else:
            raise KeyError(pointer)
    return current


def _units_safe(binding: dict) -> bool:
    source = binding.get("source_unit")
    target = binding.get("target_unit")
    transform = binding["transform"]
    if source is None or target is None or source == target:
        return True
    if transform == "DEGREES_TO_RADIANS":
        return source in {"deg", "degree", "degrees"} and target in {"rad", "radian", "radians"}
    if transform == "RADIANS_TO_DEGREES":
        return source in {"rad", "radian", "radians"} and target in {"deg", "degree", "degrees"}
    return transform == "CUSTOM_DECLARED"


def apply_transform(value: Any, binding: dict) -> Any:
    transform = binding["transform"]
    if not _units_safe(binding):
        raise BindingError(
            f"{binding['id']}: unit change {binding.get('source_unit')}→"
            f"{binding.get('target_unit')} requires an explicit transform"
        )
    if transform == "IDENTITY":
        return value
    if transform == "DEGREES_TO_RADIANS":
        return math.radians(float(value))
    if transform == "RADIANS_TO_DEGREES":
        return math.degrees(float(value))
    if transform == "CUSTOM_DECLARED":
        raise BindingError(f"{binding['id']}: CUSTOM_DECLARED requires a subject adapter")
    raise BindingError(f"{binding['id']}: unsupported transform {transform!r}")


def resolve_external_state(state_fidelity_contract: dict, payload: Any) -> dict:
    policy = state_fidelity_contract["external_state_mapping"]
    bindings = state_fidelity_contract["external_state_bindings"]

    if policy == "NOT_APPLICABLE":
        return {
            "fidelity": "UNAVAILABLE",
            "loaded_state": {},
            "applied_bindings": [],
            "missing_bindings": [],
            "reasons": ["external state mapping is not applicable to this activity"],
        }

    loaded: dict[str, Any] = {}
    applied: list[str] = []
    missing: list[str] = []
    reasons: list[str] = []
    required_ids = {row["id"] for row in bindings if row["required_for_exact"]}
    resolved_required: set[str] = set()

    for binding in bindings:
        try:
            value = resolve_pointer(payload, binding["source_pointer"])
        except KeyError:
            missing.append(binding["id"])
            reasons.append(
                f"{binding['id']}: source value missing at {binding['source_pointer']}"
            )
            continue

        try:
            mapped = apply_transform(value, binding)
        except (BindingError, TypeError, ValueError) as exc:
            missing.append(binding["id"])
            reasons.append(str(exc))
            continue

        loaded[binding["target_state_path"]] = mapped
        applied.append(binding["id"])
        if binding["required_for_exact"]:
            resolved_required.add(binding["id"])

    exact = bool(bindings) and resolved_required == required_ids
    if exact:
        fidelity = "EXACT"
    elif policy == "EXACT_REQUIRED":
        fidelity = "UNAVAILABLE"
        loaded = {}
        applied = []
        reasons.append("EXACT_REQUIRED cannot be satisfied without every required binding")
    elif applied:
        fidelity = "CONSTRAINT_FAITHFUL"
    elif policy == "CONCEPT_MAPPING_ALLOWED":
        fidelity = "CONCEPT_ONLY"
    else:
        fidelity = "UNAVAILABLE"

    return {
        "fidelity": fidelity,
        "loaded_state": loaded,
        "applied_bindings": applied,
        "missing_bindings": missing,
        "reasons": reasons,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("contract", type=Path, help="JSON file containing state_fidelity_contract")
    parser.add_argument("payload", type=Path, help="external task/question JSON payload")
    args = parser.parse_args()

    contract_doc = json.loads(args.contract.read_text(encoding="utf-8"))
    contract = contract_doc.get("state_fidelity_contract", contract_doc)
    payload = json.loads(args.payload.read_text(encoding="utf-8"))
    print(json.dumps(resolve_external_state(contract, payload), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
