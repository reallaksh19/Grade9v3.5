#!/usr/bin/env python3
"""Turn a minimal owner prompt into a clarification packet or learner profile.

This tool deliberately separates:
- owner-owned facts that must be asked for when materially missing; and
- agent-owned academic/pedagogical decisions that must never be pushed back to the owner.

It does not classify D-band, cognitive demand, QRT template, X/Z/W, hints,
figures, misconceptions or solutions. Those remain agent/QRT responsibilities.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
POLICY_PATH = REPO / "Shared/quality/minimal-authoring-intake.v1.json"
SCHEMA_PATH = REPO / "Shared/quality/minimal-authoring-intake.schema.json"
PURPOSES = ("STARTER", "PRACTICE", "REVISION", "COMPETITION")
KNOWLEDGE = ("DEMONSTRATED", "UNCERTAIN", "MISSING")


class IntakeError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise IntakeError(f"{path}: expected JSON object")
    return value


def validate_intake_shape(value: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    if value.get("schema") != "minimal-authoring-intake/v1":
        problems.append("schema must be minimal-authoring-intake/v1")
    if value.get("subject") not in ("Physics", "Chemistry", "Mathematics"):
        problems.append("subject must be Physics, Chemistry or Mathematics")
    if value.get("grade") not in (9, 10, 11):
        problems.append("grade must be 9, 10 or 11")
    if not isinstance(value.get("topic"), str) or not value["topic"].strip():
        problems.append("topic is required")
    questions = value.get("questions")
    if not isinstance(questions, list) or not questions:
        problems.append("at least one question is required")
    else:
        ids: list[str] = []
        for index, row in enumerate(questions):
            if not isinstance(row, dict):
                problems.append(f"questions[{index}] must be an object")
                continue
            qid, stem = row.get("id"), row.get("stem")
            if not isinstance(qid, str) or not qid.strip():
                problems.append(f"questions[{index}].id is required")
            else:
                ids.append(qid)
            if not isinstance(stem, str) or not stem.strip():
                problems.append(f"questions[{index}].stem is required")
        if len(ids) != len(set(ids)):
            problems.append("question ids must be unique")
    purpose = value.get("purpose")
    if purpose is not None and purpose not in PURPOSES:
        problems.append(f"purpose must be one of {list(PURPOSES)}")
    learner = value.get("learner")
    if learner is not None:
        if not isinstance(learner, dict):
            problems.append("learner must be an object")
        else:
            held = learner.get("knowledge")
            if held is not None:
                if not isinstance(held, dict):
                    problems.append("learner.knowledge must be an object")
                else:
                    for key, state in held.items():
                        if state not in KNOWLEDGE:
                            problems.append(f"learner.knowledge.{key} must be one of {list(KNOWLEDGE)}")
    return problems


def normalize_capabilities(value: dict[str, Any]) -> list[dict[str, str]]:
    rows = value.get("capabilities")
    if not isinstance(rows, list) or not rows:
        raise IntakeError("capability scan must contain non-empty capabilities[]")
    out: list[dict[str, str]] = []
    seen: set[str] = set()
    for index, row in enumerate(rows):
        if not isinstance(row, dict):
            raise IntakeError(f"capabilities[{index}] must be an object")
        cid = row.get("id")
        label = row.get("label")
        reason = row.get("reason")
        if not isinstance(cid, str) or not cid.strip():
            raise IntakeError(f"capabilities[{index}].id is required")
        if cid in seen:
            raise IntakeError(f"duplicate capability id {cid}")
        seen.add(cid)
        if not isinstance(label, str) or not label.strip():
            label = cid
        if not isinstance(reason, str) or not reason.strip():
            reason = "Needed as a prerequisite or bridge for one or more supplied questions."
        out.append({"id": cid, "label": label, "reason": reason})
    return out


def clarification_plan(intake: dict[str, Any], capability_scan: dict[str, Any] | None) -> dict[str, Any]:
    problems = validate_intake_shape(intake)
    if problems:
        return {
            "status": "INTAKE_INVALID",
            "problems": problems,
            "owner_questions": [],
            "agent_actions": [],
        }

    owner_questions: list[dict[str, Any]] = []
    agent_actions: list[dict[str, str]] = []

    if intake.get("purpose") is None:
        owner_questions.append({
            "id": "PURPOSE",
            "question": "What is the purpose for this learner: STARTER, PRACTICE, REVISION, or COMPETITION?",
            "why_needed": "Purpose affects support posture and how much of the decisive work should remain unsupported.",
            "allowed": list(PURPOSES),
        })

    if capability_scan is None:
        agent_actions.append({
            "id": "SCAN_RELEVANT_LEARNER_CAPABILITIES",
            "instruction": "Independently inspect the supplied questions and canonical topic truth, then identify only the prerequisite/bridge capabilities whose learner state would materially change X, Y, W, support posture or Core1A routing. Do not ask the owner to perform this scan.",
        })
    else:
        capabilities = normalize_capabilities(capability_scan)
        held = ((intake.get("learner") or {}).get("knowledge") or {})
        missing = [row for row in capabilities if row["id"] not in held]
        if missing:
            owner_questions.append({
                "id": "LEARNER_KNOWLEDGE",
                "question": "For each item below, tell me whether the learner has DEMONSTRATED it, is UNCERTAIN, or is MISSING it.",
                "why_needed": "The QRT bridge Y and learner-relative X/W cannot be honestly resolved without idea-level learner evidence.",
                "allowed": list(KNOWLEDGE),
                "items": missing,
            })

    # These are explicitly agent-owned and are emitted as work, never questions to the owner.
    agent_actions.extend([
        {"id": "VERIFY_ACADEMICS", "instruction": "Solve and independently verify each supplied question and preserve owner-supplied source custody without inventing provenance."},
        {"id": "CLASSIFY_DIFFICULTY", "instruction": "Author the five-component difficulty evidence and resolve D1-D4."},
        {"id": "CLASSIFY_DEMAND", "instruction": "Author primary/secondary cognitive demand and basis; never infer it from question type or keywords."},
        {"id": "RESOLVE_QRT", "instruction": "Resolve the one QRT cell and subject adapter, then author/review support against H1-M3."},
        {"id": "AUTHOR_HTML", "instruction": "Project through the active Blueprint/render path; do not invent a parallel HTML shell."},
    ])

    if owner_questions:
        status = "CLARIFICATION_REQUIRED"
    elif capability_scan is None:
        status = "AGENT_ANALYSIS_REQUIRED"
    else:
        status = "READY_FOR_PERSONALIZED_QRT"

    return {
        "schema": "authoring-intake-plan/v1",
        "status": status,
        "subject": intake["subject"],
        "grade": intake["grade"],
        "topic": intake["topic"],
        "question_count": len(intake["questions"]),
        "owner_questions": owner_questions,
        "agent_actions": agent_actions,
        "source_default": "OWNER_SUPPLIED",
        "do_not_ask_owner_for": [
            "D1-D4",
            "cognitive demand",
            "QRT template",
            "X/Y/Z/W wording",
            "hint ladder",
            "figure/SVG design",
            "misconception repair",
            "worked solution",
            "Core1A concept structure",
        ],
    }


def materialize_profile(intake: dict[str, Any], capability_scan: dict[str, Any]) -> dict[str, Any]:
    plan = clarification_plan(intake, capability_scan)
    if plan["status"] != "READY_FOR_PERSONALIZED_QRT":
        raise IntakeError(f"PROFILE_NOT_READY: {plan['status']}")
    capabilities = normalize_capabilities(capability_scan)
    held = ((intake.get("learner") or {}).get("knowledge") or {})
    selected = {row["id"]: held[row["id"]] for row in capabilities}
    learner = intake.get("learner") or {}
    profile_id = learner.get("profile_ref") or "OWNER-ESTIMATE-AUTHORING-SESSION"
    profile: dict[str, Any] = {
        "profile_id": profile_id,
        "provenance": "OWNER_ESTIMATE",
        "held": selected,
        "knowledge_percentage": None,
        "measured_fit_claim": False,
    }
    if learner.get("support_posture"):
        profile["support_posture"] = learner["support_posture"]
    return profile


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    check = sub.add_parser("check", help="validate the policy file and basic invariants")
    plan = sub.add_parser("plan", help="produce missing-input clarification / agent work plan")
    plan.add_argument("--intake", type=Path, required=True)
    plan.add_argument("--capabilities", type=Path)
    profile = sub.add_parser("profile", help="materialize an OWNER_ESTIMATE learner profile after clarification")
    profile.add_argument("--intake", type=Path, required=True)
    profile.add_argument("--capabilities", type=Path, required=True)
    args = parser.parse_args(argv)

    if args.command == "check":
        policy = load(POLICY_PATH)
        problems: list[str] = []
        if policy.get("schema") != "minimal-authoring-intake-policy/v1":
            problems.append("policy schema mismatch")
        forbidden = " ".join(policy.get("forbidden_clarification_requests") or [])
        for phrase in ("D1-D4", "cognitive demand", "QRT template", "X, Y, Z or W"):
            if phrase not in forbidden:
                problems.append(f"policy must forbid delegating {phrase} to owner")
        learner_rule = ((policy.get("owner_owned_inputs") or {}).get("learner_knowledge") or {})
        if not learner_rule.get("clarify_when_missing"):
            problems.append("learner knowledge must be clarified when materially missing")
        if problems:
            print("\n".join(problems))
            return 1
        print("ok: minimal-prompt intake policy")
        return 0

    intake = load(args.intake)
    capabilities = load(args.capabilities) if getattr(args, "capabilities", None) else None
    try:
        if args.command == "plan":
            result = clarification_plan(intake, capabilities)
        else:
            result = materialize_profile(intake, capabilities)
    except IntakeError as exc:
        print(str(exc))
        return 1
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
