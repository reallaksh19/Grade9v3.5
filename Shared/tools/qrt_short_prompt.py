#!/usr/bin/env python3
"""Plan QRT authoring from a short owner prompt normalized to a small JSON request."""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
WORKFLOW_PATH = REPO / "Shared" / "workflows" / "qrt-short-prompt.v1.json"

SUBJECTS = ("Physics", "Chemistry", "Mathematics")
OUTPUTS = ("LEARNER_HTML", "QRT_EVIDENCE")
PROVENANCE = ("OWNER_SUPPLIED", "AUTHORED_PRACTICE", "EXTERNAL_SOURCE", "ADAPTED")
INTENTS = ("PRESERVE_OWNER_QUESTIONS", "AUTHORED_PRACTICE")
STATUSES = ("DEMONSTRATED", "UNCERTAIN", "MISSING")


class ShortPromptError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ShortPromptError(f"{path}: expected object")
    return data


def normalize_request(raw: dict[str, Any]) -> dict[str, Any]:
    if raw.get("schema") != "qrt-short-prompt-request/v1":
        raise ShortPromptError("schema must be qrt-short-prompt-request/v1")
    subject = raw.get("subject")
    if subject not in SUBJECTS:
        raise ShortPromptError(f"unsupported subject: {subject!r}")
    topic = str(raw.get("topic") or "").strip()
    if not topic:
        raise ShortPromptError("topic is required")
    questions = raw.get("questions")
    if not isinstance(questions, list) or not questions:
        raise ShortPromptError("at least one question is required")

    seen: set[str] = set()
    normalized_questions = []
    for index, row in enumerate(questions, 1):
        if not isinstance(row, dict):
            raise ShortPromptError(f"questions[{index-1}] must be an object")
        text = " ".join(str(row.get("text") or "").split())
        if len(text.split()) < 3:
            raise ShortPromptError(f"questions[{index-1}].text is too short")
        qid = str(row.get("id") or f"Q{index}").strip()
        if not qid or qid in seen:
            raise ShortPromptError(f"question id missing or duplicate: {qid!r}")
        seen.add(qid)
        normalized_questions.append({"id": qid, "text": text})

    outputs = raw.get("requested_outputs") or list(OUTPUTS)
    if not isinstance(outputs, list) or not outputs:
        raise ShortPromptError("requested_outputs must be a non-empty list")
    if any(item not in OUTPUTS for item in outputs):
        raise ShortPromptError("requested_outputs may contain only LEARNER_HTML and QRT_EVIDENCE")
    outputs = list(dict.fromkeys(outputs))
    for required in OUTPUTS:
        if required not in outputs:
            outputs.append(required)

    learner = copy.deepcopy(raw.get("learner_input"))
    if learner is not None:
        if not isinstance(learner, dict) or learner.get("mode") not in ("PROFILE", "USE_DEFAULT_GENERIC"):
            raise ShortPromptError("learner_input.mode must be PROFILE or USE_DEFAULT_GENERIC")
        if learner["mode"] == "PROFILE":
            ideas = learner.get("ideas")
            if not isinstance(ideas, list) or not ideas:
                raise ShortPromptError("PROFILE learner_input requires ideas[]")
            for item in ideas:
                if not isinstance(item, dict) or not str(item.get("idea") or "").strip() or item.get("status") not in STATUSES:
                    raise ShortPromptError("learner ideas require idea + DEMONSTRATED/UNCERTAIN/MISSING")

    provenance = copy.deepcopy(raw.get("provenance"))
    if provenance is not None:
        if not isinstance(provenance, dict) or provenance.get("kind") not in PROVENANCE:
            raise ShortPromptError("provenance.kind is invalid")

    intent = raw.get("product_intent")
    if intent is not None and intent not in INTENTS:
        raise ShortPromptError("product_intent is invalid")

    return {
        "schema": "qrt-short-prompt-request/v1",
        "subject": subject,
        "grade": raw.get("grade"),
        "topic": topic,
        "questions": normalized_questions,
        "requested_outputs": outputs,
        "learner_input": learner,
        "provenance": provenance,
        "product_intent": intent,
    }


def owner_questions(request: dict[str, Any], workflow: dict[str, Any]) -> list[dict[str, Any]]:
    wanted: list[str] = []
    if request.get("learner_input") is None:
        wanted.append("LEARNER_PROFILE")
    provenance = request.get("provenance")
    if provenance is None:
        wanted.append("QUESTION_PROVENANCE")
    elif provenance.get("kind") in ("EXTERNAL_SOURCE", "ADAPTED") and not str(provenance.get("source_note") or "").strip():
        wanted.append("SOURCE_DETAILS")
    if request.get("product_intent") is None:
        wanted.append("PRODUCT_INTENT")
    catalogue = {row["id"]: row for row in workflow["clarification_policy"]["owner_questions"]}
    return [copy.deepcopy(catalogue[key]) for key in wanted]


def _role(request: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
    intent = request.get("product_intent")
    if intent == "PRESERVE_OWNER_QUESTIONS" and (request.get("provenance") or {}).get("kind") == "AUTHORED_PRACTICE":
        raise ShortPromptError("AUTHORED_PRACTICE provenance cannot be promoted to preserved Core2 source custody")
    row = next((r for r in workflow["role_routing"] if r["product_intent"] == intent), None)
    if row is None:
        raise ShortPromptError("cannot route without product_intent")
    return copy.deepcopy(row)


def plan(raw: dict[str, Any], workflow: dict[str, Any]) -> dict[str, Any]:
    request = normalize_request(raw)
    questions = owner_questions(request, workflow)
    base = {
        "schema": "qrt-short-prompt-plan/v1",
        "request": request,
        "owner_questions": questions,
        "never_ask_owner_for": copy.deepcopy(workflow["never_ask_owner_for"]),
        "requested_outputs": copy.deepcopy(request["requested_outputs"]),
    }
    if questions:
        return {
            **base,
            "state": "OWNER_INPUT_REQUIRED",
            "next_action": "Ask only the listed owner questions, merge the answers into the normalized request, then run plan again.",
            "agent_duties_pending": copy.deepcopy(workflow["agent_duties"]),
        }

    route = _role(request, workflow)
    duties = list(workflow["agent_duties"])
    provenance = request["provenance"]
    if provenance["kind"] in ("EXTERNAL_SOURCE", "ADAPTED"):
        duties.insert(0, "ACQUIRE_AND_VERIFY_SOURCE_CUSTODY")
    if request["learner_input"]["mode"] == "USE_DEFAULT_GENERIC":
        duties.insert(0, "RUN_SHORT_DIAGNOSTIC_BEFORE_MAKING_PERSONALISED_XY_CLAIMS")

    return {
        **base,
        "state": "READY_TO_AUTHOR",
        "role": route["role"],
        "blueprint_ref": route["blueprint_ref"],
        "role_rule": route["rule"],
        "learner_mode": "PERSONALISED" if request["learner_input"]["mode"] == "PROFILE" else "DEFAULT_GENERIC",
        "provenance_rule": (
            "Owner/source wording and identity must remain explicit; do not invent exam identity."
            if route["role"] == "CORE2"
            else "Output practice is AUTHORED_PRACTICE and must not be presented as source-backed Core2."
        ),
        "agent_duties": duties,
        "agent_derived_fields": [
            "canonical topic/package/microtopic/capability mapping",
            "five-component difficulty + D1-D4 band + basis",
            "primary/secondary cognitive demand + basis",
            "verified answer reasoning route + crux move + independent check",
            "X/Y/Z/W",
            "resolved QRT template id",
            "subject-adapter specialization",
            "hints/representations/helpers/misconception repair",
            "governed product manifest and render path",
        ],
        "output_contract": copy.deepcopy(workflow["output_contract"]),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("plan", help="normalize a short-prompt request and produce clarification questions or an authoring work order")
    p.add_argument("--request", type=Path, required=True)
    args = parser.parse_args(argv)

    workflow = load(WORKFLOW_PATH)
    if args.cmd == "plan":
        print(json.dumps(plan(load(args.request), workflow), indent=2, ensure_ascii=False))
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
