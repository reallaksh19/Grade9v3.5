#!/usr/bin/env python3
"""Apply the research-first workflow policy: defaults instead of owner waits, duties instead of holds.

Every agent job ends in a delivered product. Conditions that older planners reported as
HOLD, BLOCKED or WAITING are translated here into the duty the agent must carry out inside
the same job (research a source, author a bridge, apply the default learner, ...). The
duties and defaults are governed data in Shared/workflows/research-first.v1.json; this
module only reads them, so no subject or topic appears here.
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO / "Shared" / "workflows" / "research-first.v1.json"

RESEARCH_AND_AUTHOR = "RESEARCH_AND_AUTHOR"

# Former planner/composer states -> duty family in escape_state_duties.
STATE_FAMILY = {
    "IDENTITY_HOLD": "IDENTITY",
    "UNMAPPED_HOLD": "MAPPING",
    "AGENT_PROPOSAL_PENDING_REVIEW": "MAPPING",
    "MIXED_SUBTOPIC_HOLD": "SCOPE",
    "WAITING_FOR_LEARNER_ENTRY": "LEARNER_ENTRY",
    "BLOCKED_PREREQUISITE": "PREREQUISITE",
    "BLOCKED_TOPOLOGY": "TOPOLOGY",
    "WAITING_FOR_SOURCE_RECEIPT": "SOURCE_CUSTODY",
    "BLOCKED_SOURCE_RECEIPT": "SOURCE_CUSTODY",
    "WAITING_FOR_SOURCE_BASIS_DECISION": "SOURCE_CUSTODY",
    "BLOCKED_SOURCE_CUSTODY": "SOURCE_CUSTODY",
    "SOURCE_CUSTODY_HOLD": "SOURCE_CUSTODY",
    "WAITING_FOR_SUPPLEMENT_POLICY": "SOURCE_COVERAGE",
    "BLOCKED_SOURCE_COVERAGE": "SOURCE_COVERAGE",
    "BLOCKED_ASSET": "ASSET",
    "VISUAL_HOLD": "ASSET",
    "HOLD_WORKED_ANCHOR": "ASSET",
    "WAITING_FOR_PURPOSE": "PURPOSE",
    "WITHHELD": "TRANSFER_EXPOSURE",
    "LEARNER_ELIGIBILITY_HOLD": "LEARNER_ENTRY",
    "UNTAUGHT_CAPABILITY_GAP": "UNTAUGHT_CAPABILITY",
}


def load_workflow(path: Path = WORKFLOW_PATH) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def duty_for(state: str, workflow: dict | None = None) -> dict:
    """Return the duty an agent must perform for a former escape state."""
    workflow = workflow or load_workflow()
    duties = workflow["escape_state_duties"]
    family = STATE_FAMILY.get(state, "GATE_FINDING")
    return {"family": family, "replaces": state, **duties[family]}


def default_learner(workflow: dict | None = None) -> dict:
    workflow = workflow or load_workflow()
    return {**copy.deepcopy(workflow["default_learner_start"]), "blocking": False}


def apply_request_defaults(request: dict, workflow: dict | None = None) -> tuple[dict, list[dict]]:
    """Fill every owner input the planner could wait on. Returns (request, defaults_applied)."""
    workflow = workflow or load_workflow()
    defaults = workflow["default_request_values"]
    out = copy.deepcopy(request)
    applied: list[dict] = []
    learner = out.get("learner")
    if not learner or "unknown" in learner:
        out["learner"] = {"owner_estimate": copy.deepcopy(defaults["learner"]["owner_estimate"])}
        applied.append({"field": "learner", "value": out["learner"], "basis": defaults["learner"]["basis"]})
    requested = set(out.get("requested_cores", []))
    practice = out.setdefault("practice", {})
    for core, value in defaults["practice"].items():
        if core in requested and not (practice.get(core) or {}).get("purpose"):
            practice[core] = {**(practice.get(core) or {}), **value}
            applied.append({"field": f"practice.{core}.purpose", "value": value["purpose"], "basis": "DEFAULT"})
    if not out.get("supplemental_question_policy"):
        out["supplemental_question_policy"] = defaults["supplemental_question_policy"]
        applied.append({"field": "supplemental_question_policy",
                        "value": defaults["supplemental_question_policy"], "basis": "DEFAULT"})
    return out, applied


def _state_pattern(workflow: dict) -> re.Pattern:
    words = "|".join(sorted(map(re.escape, workflow["forbidden_outcome_states"]), key=len, reverse=True))
    # An outcome token: the bare word, or an UPPER_SNAKE state containing it (IDENTITY_HOLD, BLOCKED_ASSET).
    return re.compile(rf"\b(?:[A-Z0-9]+_)*(?:{words})(?:_[A-Z0-9]+)*\b")


def escape_states(value: object, workflow: dict | None = None) -> list[str]:
    """Every forbidden outcome state appearing as a state token in a value (recursively)."""
    workflow = workflow or load_workflow()
    pattern = _state_pattern(workflow)
    found: list[str] = []

    def walk(item: object) -> None:
        if isinstance(item, str):
            found.extend(pattern.findall(item))
        elif isinstance(item, dict):
            for key, child in item.items():
                walk(key)
                walk(child)
        elif isinstance(item, (list, tuple)):
            for child in item:
                walk(child)

    walk(value)
    return sorted(set(found))
