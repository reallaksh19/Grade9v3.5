#!/usr/bin/env python3
"""Parse and validate the six-Core learner-product template contract.

The role specifications remain authoritative for learner-product meaning. This module
checks only the presentation contract carried by the role-directory template spec:
role presence, block ordering, reveal-state vocabulary and a small set of anti-collapse
invariants that are safe to test mechanically.

It deliberately does not attempt to prove pedagogical quality or academic correctness.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

try:
    from Shared.tools import web_blueprint_contract
except ModuleNotFoundError:  # direct script execution from Shared/tools
    import web_blueprint_contract

REPO = Path(__file__).resolve().parents[2]
ROLE_DIR = REPO / "Shared" / "roles"
ROLE_ORDER = ("CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B")
BLOCK = re.compile(r"^\`\`\`core-templates\s*$\n(.*?)^\`\`\`\s*$", re.MULTILINE | re.DOTALL)
ALLOWED_VISIBILITY = {"IMMEDIATE", "ATTEMPT_FIRST", "POST_ATTEMPT", "ON_REVEAL", "AUTHOR_ONLY"}

REQUIRED_BLOCKS = {
    "CORE1": (
        "identity_scope",
        "objects_conventions",
        "canonical_representation",
        "governing_relations",
        "hard_transition_map",
        "exclusions_extensions",
        "orientation_closure",
    ),
    "CORE1A": (
        "identity_entry_assumptions",
        "inferential_jump",
        "completed_construction",
        "representation_bridge",
        "worked_conceptual_anchor",
        "diagnose",
        "repair",
        "independent_checks",
        "exit_task_closure",
    ),
    "CORE1B": (
        "predict",
        "attempt",
        "reconstruct",
        "diagnose",
        "repair",
        "boundary_test",
        "model_response_or_rubric",
        "rejoin_inferential_jump",
    ),
    "CORE2": (
        "source_identity_provenance",
        "source_question",
        "source_hint_ladder",
        "source_answer_rubric",
        "custody_status",
    ),
    "CORE2A": (
        "family_identity_provenance",
        "question",
        "pedagogical_scaffolds",
        "reasoning_route",
        "application_crux",
        "complete_solution",
        "independent_check",
        "failure_signal_repair",
    ),
    "CORE2B": (
        "question_prior_exposure",
        "safe_pre_attempt_support",
        "attempt_commitment",
        "post_attempt_support",
        "full_answer_rubric",
        "changed_demand_review",
        "repair_route",
        "lineage_continuity_check",
    ),
}


class CoreTemplateContractError(ValueError):
    """Raised when the durable template contract is malformed."""


def discover_template_spec(role_dir: Path = ROLE_DIR) -> Path:
    """Find the one role document that carries the machine-readable template block."""
    matches = []
    for path in sorted(role_dir.glob("*.md")):
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if BLOCK.search(text):
            matches.append(path)
    if len(matches) != 1:
        raise CoreTemplateContractError(
            f"CORE_TEMPLATE_SPEC_DISCOVERY_FAILED: expected 1 fenced contract, found {len(matches)}"
        )
    return matches[0]


def load_contract(path: Path | None = None) -> dict[str, Any]:
    path = path or discover_template_spec()
    text = path.read_text(encoding="utf-8")
    match = BLOCK.search(text)
    if not match:
        raise CoreTemplateContractError("CORE_TEMPLATE_BLOCK_MISSING")
    try:
        contract = json.loads(match.group(1))
    except json.JSONDecodeError as exc:
        raise CoreTemplateContractError(f"CORE_TEMPLATE_JSON_INVALID: {exc}") from exc
    if not isinstance(contract, dict):
        raise CoreTemplateContractError("CORE_TEMPLATE_ROOT_NOT_OBJECT")
    return contract


def _finding(point: str, role: str = "", detail: str = "") -> dict[str, str]:
    return {"point": point, "role": role, "detail": detail}


def _block_ids(role: dict[str, Any]) -> list[str]:
    return [
        block.get("id")
        for block in role.get("ordered_blocks") or []
        if isinstance(block, dict) and isinstance(block.get("id"), str)
    ]


def _index(ids: list[str], block_id: str) -> int:
    try:
        return ids.index(block_id)
    except ValueError:
        return -1


def audit(path: Path | None = None) -> dict[str, Any]:
    findings: list[dict[str, str]] = []
    try:
        contract = load_contract(path)
    except (OSError, CoreTemplateContractError) as exc:
        return {
            "roles_checked": 0,
            "passed": False,
            "findings": [_finding("CORE_TEMPLATE_LOAD_FAILED", detail=str(exc))],
        }

    roles = contract.get("roles")
    if not isinstance(roles, dict):
        return {
            "roles_checked": 0,
            "passed": False,
            "findings": [_finding("CORE_TEMPLATE_ROLES_MISSING")],
        }

    actual = set(roles)
    expected = set(ROLE_ORDER)
    for missing in sorted(expected - actual):
        findings.append(_finding("CORE_TEMPLATE_ROLE_MISSING", missing))
    for extra in sorted(actual - expected):
        findings.append(_finding("CORE_TEMPLATE_ROLE_UNKNOWN", extra))

    for role_name in ROLE_ORDER:
        role = roles.get(role_name)
        if not isinstance(role, dict):
            continue

        learner_job = role.get("learner_job")
        if not isinstance(learner_job, str) or not learner_job.strip():
            findings.append(_finding("CORE_TEMPLATE_LEARNER_JOB_MISSING", role_name))

        findings.extend(
            _finding(row["point"], role_name, row.get("detail") or row.get("ref") or "")
            for row in web_blueprint_contract.validate_role_binding(role_name, role)
        )

        blocks = role.get("ordered_blocks")
        if not isinstance(blocks, list) or not blocks:
            findings.append(_finding("CORE_TEMPLATE_BLOCKS_MISSING", role_name))
            continue

        ids = _block_ids(role)
        if len(ids) != len(blocks):
            findings.append(_finding("CORE_TEMPLATE_BLOCK_ID_INVALID", role_name))
        if len(ids) != len(set(ids)):
            findings.append(_finding("CORE_TEMPLATE_BLOCK_ID_DUPLICATE", role_name))

        for block in blocks:
            if not isinstance(block, dict):
                findings.append(_finding("CORE_TEMPLATE_BLOCK_INVALID", role_name))
                continue
            visibility = block.get("visibility")
            if visibility not in ALLOWED_VISIBILITY:
                findings.append(
                    _finding(
                        "CORE_TEMPLATE_VISIBILITY_INVALID",
                        role_name,
                        f"{block.get('id')}: {visibility!r}",
                    )
                )

        for required in REQUIRED_BLOCKS[role_name]:
            if required not in ids:
                findings.append(
                    _finding("CORE_TEMPLATE_REQUIRED_BLOCK_MISSING", role_name, required)
                )

        required_inputs = role.get("required_inputs")
        if not isinstance(required_inputs, list) or not all(
            isinstance(item, str) and item.strip() for item in required_inputs
        ):
            findings.append(_finding("CORE_TEMPLATE_REQUIRED_INPUTS_INVALID", role_name))

        for key in ("withheld_pre_attempt", "forbidden"):
            values = role.get(key)
            if not isinstance(values, list) or not all(
                isinstance(item, str) and item.strip() for item in values
            ):
                findings.append(_finding(f"CORE_TEMPLATE_{key.upper()}_INVALID", role_name))

    # Anti-collapse invariants safe enough to enforce mechanically.
    core1 = roles.get("CORE1") or {}
    if "FULL_INFERENTIAL_CONSTRUCTION" not in (core1.get("forbidden") or []):
        findings.append(_finding("CORE1_ORIENTATION_BOUNDARY_UNPROTECTED", "CORE1"))

    core1a_ids = _block_ids(roles.get("CORE1A") or {})
    if "completed_construction" not in core1a_ids:
        findings.append(_finding("CORE1A_CONSTRUCTION_NOT_EXPLICIT", "CORE1A"))

    core1b = roles.get("CORE1B") or {}
    core1b_ids = _block_ids(core1b)
    if _index(core1b_ids, "attempt") < 0 or _index(core1b_ids, "reconstruct") < 0:
        findings.append(_finding("CORE1B_ATTEMPT_RECONSTRUCT_MISSING", "CORE1B"))
    elif _index(core1b_ids, "attempt") >= _index(core1b_ids, "reconstruct"):
        findings.append(_finding("CORE1B_REVEAL_PRECEDES_ATTEMPT", "CORE1B"))
    if "ANSWER_BEFORE_ATTEMPT" not in (core1b.get("forbidden") or []):
        findings.append(_finding("CORE1B_ATTEMPT_BOUNDARY_UNPROTECTED", "CORE1B"))

    core2 = roles.get("CORE2") or {}
    if "AUTHORED_SCAFFOLD_PRESENTED_AS_SOURCE_HINT" not in (core2.get("forbidden") or []):
        findings.append(_finding("CORE2_CUSTODY_SCAFFOLD_BOUNDARY_UNPROTECTED", "CORE2"))

    core2a_ids = _block_ids(roles.get("CORE2A") or {})
    if "application_crux" not in core2a_ids:
        findings.append(_finding("CORE2A_CRUX_NOT_EXPLICIT", "CORE2A"))

    core2b = roles.get("CORE2B") or {}
    core2b_ids = _block_ids(core2b)
    attempt_i = _index(core2b_ids, "attempt_commitment")
    changed_i = _index(core2b_ids, "changed_demand_review")
    if attempt_i < 0 or changed_i < 0 or changed_i <= attempt_i:
        findings.append(_finding("CORE2B_CHANGED_DEMAND_PRECEDES_ATTEMPT", "CORE2B"))
    if "PROTECTED_MOVE" not in (core2b.get("withheld_pre_attempt") or []):
        findings.append(_finding("CORE2B_PROTECTED_MOVE_NOT_WITHHELD", "CORE2B"))
    if "PROTECTED_MOVE_DISCLOSED_PRE_ATTEMPT" not in (core2b.get("forbidden") or []):
        findings.append(_finding("CORE2B_PROTECTED_MOVE_BOUNDARY_UNPROTECTED", "CORE2B"))

    # A role template should not accidentally collapse to the exact same ordered anatomy
    # as another role.
    signatures: dict[tuple[str, ...], str] = {}
    for role_name in ROLE_ORDER:
        signature = tuple(_block_ids(roles.get(role_name) or {}))
        if not signature:
            continue
        previous = signatures.get(signature)
        if previous:
            findings.append(
                _finding(
                    "CORE_TEMPLATE_ANATOMY_COLLAPSE",
                    role_name,
                    f"same ordered blocks as {previous}",
                )
            )
        else:
            signatures[signature] = role_name

    registry_report = web_blueprint_contract.audit_registry()
    for row in registry_report["findings"]:
        findings.append(_finding(row["point"], detail=row.get("detail") or row.get("ref") or ""))

    return {
        "contract_version": contract.get("version"),
        "roles_checked": sum(1 for role in ROLE_ORDER if role in roles),
        "blueprint_refs": {
            role: (roles.get(role) or {}).get("web_blueprint_ref")
            for role in ROLE_ORDER
        },
        "passed": not findings,
        "findings": findings,
    }


def resolve_web_blueprint_for_core(core: str, path: Path | None = None) -> dict[str, Any]:
    """Resolve the exact versioned web blueprint declared by the Core template contract."""
    if core not in ROLE_ORDER:
        raise CoreTemplateContractError(f"CORE_TEMPLATE_ROLE_UNKNOWN: {core}")
    contract = load_contract(path)
    role = (contract.get("roles") or {}).get(core)
    if not isinstance(role, dict):
        raise CoreTemplateContractError(f"CORE_TEMPLATE_ROLE_MISSING: {core}")
    ref = role.get("web_blueprint_ref")
    if not isinstance(ref, str) or not ref:
        raise CoreTemplateContractError(f"WEB_BLUEPRINT_REF_MISSING: {core}")
    try:
        return web_blueprint_contract.resolve_blueprint(ref)
    except web_blueprint_contract.WebBlueprintContractError as exc:
        raise CoreTemplateContractError(str(exc)) from exc


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--enforce",
        action="store_true",
        help="exit non-zero when the template contract is structurally invalid",
    )
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
