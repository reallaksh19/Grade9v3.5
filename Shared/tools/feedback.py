#!/usr/bin/env python3
"""Progressive self-study feedback over existing question and microtopic records.

This module deliberately does not pretend to be a universal grader. The caller supplies
an evaluated outcome (CORRECT / INCORRECT / UNDECIDABLE) and, when known, the failed
capability or misconception. This module owns the safer next-step policy:

  independent attempt -> small hint -> retry -> repair -> fresh verification

It never emits an ANSWER-revealing hint, never guesses which capability failed when a
multi-capability question is ambiguous, and never writes learner state silently. Instead
it returns an observation draft that the caller may persist explicitly.

A real school worksheet question does not have to be promoted into the canonical question
library. For such questions the caller supplies the already-resolved worksheet mapping
(primary + meaningful secondary capability refs). Because that transient row has no
canonical hint ladder, the runtime diagnoses/repairs from existing microtopic content
rather than inventing a hint.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.tools import capability_graph, review_schedule  # noqa: E402

RESULTS = {"CORRECT", "INCORRECT", "UNDECIDABLE"}
ERROR_STAGES = {"CONCEPT", "SETUP", "EXECUTION", "CARELESS", "UNKNOWN"}
HELP_LEVELS = {"NONE", "HINT", "WORKED_EXAMPLE", "SOLUTION", "UNKNOWN"}
INDEPENDENT_HELP = {"NONE"}
DIAGNOSIS_STATES = {"CONFIRMED", "REFUTED", "INDETERMINATE"}


def subject_records(subject: str, repo: Path = REPO) -> dict:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths))


def question_record(records: dict, question_ref: str) -> dict | None:
    record = records.get(question_ref)
    if record and record.get("_collection") == "questions":
        return record
    return None


def resolve_question_input(request: dict, records: dict) -> tuple[dict | None, str | None, list[dict]]:
    """Resolve either a canonical question or one transient worksheet-mapping row.

    Canonical records win when the id exists because they carry governed hints, transfer
    metadata and repair refs. Otherwise a worksheet question may supply only the mapping
    already established by study_map.py. This function validates that those capability
    refs are canonical; it does not create content for the worksheet.
    """
    question_ref = request.get("question_ref")
    canonical = question_record(records, question_ref)
    supplied = request.get("worksheet_question")
    findings: list[dict] = []

    if canonical is not None:
        if supplied:
            supplied_id = supplied.get("question_id")
            if supplied_id and supplied_id != question_ref:
                findings.append({
                    "point": "FEEDBACK_WORKSHEET_QUESTION_ID_MISMATCH",
                    "detail": (
                        f"worksheet_question.question_id {supplied_id} does not match "
                        f"question_ref {question_ref}"
                    ),
                })
            supplied_primary = supplied.get("primary_capability_ref")
            supplied_secondary = set(supplied.get("secondary_capability_refs") or [])
            if (
                supplied_primary
                and (
                    supplied_primary != canonical.get("primary_capability_ref")
                    or supplied_secondary
                    != set(canonical.get("secondary_capability_refs") or [])
                )
            ):
                findings.append({
                    "point": "FEEDBACK_CANONICAL_MAPPING_DRIFT",
                    "detail": (
                        "worksheet_question mapping conflicts with the canonical question; "
                        "canonical capability ownership is authoritative"
                    ),
                })
        return canonical, "CANONICAL_QUESTION", findings

    if not supplied:
        return None, None, [{
            "point": "FEEDBACK_QUESTION_UNKNOWN",
            "detail": (
                f"{question_ref} is not a canonical question and no worksheet_question "
                "mapping was supplied"
            ),
        }]

    supplied_id = supplied.get("question_id") or question_ref
    if supplied_id != question_ref:
        findings.append({
            "point": "FEEDBACK_WORKSHEET_QUESTION_ID_MISMATCH",
            "detail": (
                f"worksheet_question.question_id {supplied_id} does not match "
                f"question_ref {question_ref}"
            ),
        })

    primary = supplied.get("primary_capability_ref")
    secondary = list(supplied.get("secondary_capability_refs") or [])
    if not primary:
        findings.append({
            "point": "FEEDBACK_WORKSHEET_PRIMARY_CAPABILITY_MISSING",
            "detail": "worksheet_question requires primary_capability_ref",
        })

    for capability in [primary, *secondary]:
        if not capability:
            continue
        record = records.get(capability)
        if record is None or record.get("_collection") != "capabilities":
            findings.append({
                "point": "FEEDBACK_WORKSHEET_CAPABILITY_UNKNOWN",
                "capability_ref": capability,
                "detail": "worksheet mapping names no canonical capability in this subject",
            })

    if findings:
        return None, "WORKSHEET_MAPPING", findings

    return {
        "id": question_ref,
        "primary_capability_ref": primary,
        "secondary_capability_refs": secondary,
        "hints": [],
        "_worksheet_mapping": True,
        "_mapping_basis": supplied.get("mapping_basis"),
    }, "WORKSHEET_MAPPING", []


def required_capabilities(question: dict) -> list[str]:
    return [
        question["primary_capability_ref"],
        *list(question.get("secondary_capability_refs") or []),
    ]


def prerequisite_capabilities(records: dict, capability_refs: list[str]) -> list[str]:
    """Canonical prerequisite closure that may be explicitly attributed by reviewed work."""
    caps = {
        record_id: record
        for record_id, record in records.items()
        if record.get("_collection") == "capabilities"
    }
    return capability_graph.prerequisite_closure_many(capability_refs, caps)


def microtopics_for_capability(records: dict, capability_ref: str) -> list[dict]:
    rows = [
        record for record in records.values()
        if record.get("_collection") == "microtopics"
        and record.get("primary_capability_ref") == capability_ref
    ]
    return sorted(rows, key=lambda row: row["id"])


def diagnostic_options(records: dict, capability_refs: list[str]) -> list[dict]:
    """Concrete prompts a caller may use to distinguish an ambiguous failure."""
    options = []
    for capability in capability_refs:
        for microtopic in microtopics_for_capability(records, capability):
            prompts = [
                {
                    "index": index,
                    "wrong_idea": misconception["wrong_idea"],
                    "diagnostic_prompt": misconception["diagnostic_prompt"],
                }
                for index, misconception in enumerate(microtopic.get("misconceptions", []))
            ]
            options.append({
                "capability_ref": capability,
                "microtopic_ref": microtopic["id"],
                "title": microtopic.get("title"),
                "diagnostics": prompts,
            })
    return options


def _step_repair(records: dict, repair_ref: str) -> dict | None:
    for microtopic in (
        record for record in records.values()
        if record.get("_collection") == "microtopics"
    ):
        for step in microtopic.get("teaching_path", []):
            if step.get("id") == repair_ref:
                return {
                    "kind": "TEACHING_STEP",
                    "repair_ref": repair_ref,
                    "microtopic_ref": microtopic["id"],
                    "action": step.get("action"),
                    "why_valid": step.get("why_valid"),
                    "route": "CORE1B_THEN_CORE1A",
                }
    return None


def diagnostic_evidence_for(records: dict, failed_capability_ref: str | None,
                            misconception_index: int, observed_response: str,
                            diagnosis: str, basis: str) -> tuple[dict | None, str | None]:
    """Build evidence against the canonical diagnostic prompt; never infer the diagnosis."""
    if not failed_capability_ref:
        return None, "DIAGNOSTIC_EVIDENCE_FAILED_CAPABILITY_REQUIRED"
    microtopics = microtopics_for_capability(records, failed_capability_ref)
    if len(microtopics) != 1:
        return None, "DIAGNOSTIC_EVIDENCE_MICROTOPIC_AMBIGUOUS"
    misconceptions = list(microtopics[0].get("misconceptions", []))
    if not isinstance(misconception_index, int) or not 0 <= misconception_index < len(misconceptions):
        return None, "DIAGNOSTIC_EVIDENCE_MISCONCEPTION_INVALID"
    if diagnosis not in DIAGNOSIS_STATES:
        return None, "DIAGNOSTIC_EVIDENCE_DIAGNOSIS_INVALID"
    if not isinstance(observed_response, str) or not observed_response.strip():
        return None, "DIAGNOSTIC_EVIDENCE_RESPONSE_MISSING"
    if not isinstance(basis, str) or not basis.strip():
        return None, "DIAGNOSTIC_EVIDENCE_BASIS_MISSING"
    probe = misconceptions[misconception_index].get("diagnostic_prompt")
    if not isinstance(probe, str) or not probe.strip():
        return None, "DIAGNOSTIC_EVIDENCE_PROBE_MISSING"
    return {
        "misconception_index": misconception_index,
        "probe": probe,
        "observed_response": observed_response.strip(),
        "diagnosis": diagnosis,
        "basis": basis.strip(),
    }, None


def _validate_diagnostic_evidence(records: dict, failed_capability_ref: str | None,
                                  raw: object) -> tuple[dict | None, list[dict]]:
    if raw is None:
        return None, []
    if not isinstance(raw, dict):
        return None, [{
            "point": "DIAGNOSTIC_EVIDENCE_INVALID",
            "detail": "evaluation.diagnostic_evidence must be an object",
        }]
    index = raw.get("misconception_index")
    evidence, error = diagnostic_evidence_for(
        records,
        failed_capability_ref,
        index,
        raw.get("observed_response"),
        raw.get("diagnosis"),
        raw.get("basis"),
    )
    if error:
        return None, [{"point": error, "detail": "diagnostic evidence does not satisfy the confirmation contract"}]
    if raw.get("probe") != evidence["probe"]:
        return None, [{
            "point": "DIAGNOSTIC_EVIDENCE_PROBE_MISMATCH",
            "detail": "diagnostic evidence must bind to the exact canonical diagnostic_prompt",
        }]
    unknown = set(raw) - {"misconception_index", "probe", "observed_response", "diagnosis", "basis"}
    if unknown:
        return None, [{
            "point": "DIAGNOSTIC_EVIDENCE_UNKNOWN_FIELD",
            "detail": f"unexpected diagnostic evidence fields: {', '.join(sorted(unknown))}",
        }]
    return evidence, []


def repair_for(records: dict, question: dict, failed_capability_ref: str | None,
               misconception_index: int | None = None) -> dict | None:
    """Resolve the narrowest repair already present in canonical content."""
    repair_ref = question.get("repair_ref")
    if repair_ref:
        exact = _step_repair(records, repair_ref)
        if exact:
            return exact

    if not failed_capability_ref:
        return None

    microtopics = microtopics_for_capability(records, failed_capability_ref)
    if len(microtopics) != 1:
        return None

    microtopic = microtopics[0]
    misconceptions = list(microtopic.get("misconceptions", []))
    if misconception_index is not None:
        if 0 <= misconception_index < len(misconceptions):
            misconception = misconceptions[misconception_index]
            return {
                "kind": "MISCONCEPTION_REPAIR",
                "microtopic_ref": microtopic["id"],
                "misconception_index": misconception_index,
                "wrong_idea": misconception["wrong_idea"],
                "diagnostic_prompt": misconception["diagnostic_prompt"],
                "repair": misconception["repair"],
                "route": "CORE1B_THEN_CORE1A",
            }
        return None

    return {
        "kind": "MICROTOPIC_REPAIR",
        "microtopic_ref": microtopic["id"],
        "title": microtopic.get("title"),
        "diagnostic_prompts": [
            row["diagnostic_prompt"] for row in misconceptions
        ],
        "route": "CORE1B_THEN_CORE1A",
    }


def pre_attempt_safe_hint(question: dict, shown_hint_indices: list[int]) -> dict | None:
    """Return only support safe to expose before a Core2B attempt.

    Hints remain canonical custody data. Learner-time disclosure is stricter: any
    transfer task gets concept-only support before commitment. METHOD/ANSWER hints may
    still participate in graduated help after an attempt through next_safe_hint().
    """
    shown = set(shown_hint_indices)
    is_transfer = isinstance(question.get("transfer"), dict) and bool(question.get("transfer"))
    for index, hint in enumerate(question.get("hints", [])):
        if index in shown:
            continue
        reveals = hint.get("reveals")
        if reveals == "ANSWER":
            continue
        if is_transfer and reveals != "CONCEPT":
            continue
        return {"index": index, **hint}
    return None


def next_safe_hint(question: dict, shown_hint_indices: list[int]) -> dict | None:
    """Return the next post-attempt non-answer hint that preserves decision demand."""
    shown = set(shown_hint_indices)
    transfer = question.get("transfer") or {}
    model_choice_transfer = transfer.get("dimension") == "model_choice"

    for index, hint in enumerate(question.get("hints", [])):
        if index in shown:
            continue
        reveals = hint.get("reveals")
        if reveals == "ANSWER":
            continue
        if model_choice_transfer and reveals != "CONCEPT":
            # In a model-choice transfer task, a METHOD hint can hand over the very
            # decision the task is supposed to assess.
            continue
        return {"index": index, **hint}
    return None


def verification_candidate(records: dict, question: dict,
                           attempted_question_refs: list[str]) -> dict | None:
    """Prefer a fresh same-capability question; otherwise use the microtopic exit task."""
    attempted = set(attempted_question_refs) | {question["id"]}
    primary = question["primary_capability_ref"]
    alternatives = sorted(
        (
            record for record in records.values()
            if record.get("_collection") == "questions"
            and record.get("primary_capability_ref") == primary
            and record.get("id") not in attempted
            # A Core1A worked anchor is shown with its full solution, so it cannot verify.
            and {e.get("core") for e in record.get("exposure", [])} != {"CORE1A"}
        ),
        key=lambda row: row["id"],
    )
    if alternatives:
        chosen = alternatives[0]
        return {
            "kind": "QUESTION",
            "question_ref": chosen["id"],
            "stem": chosen.get("stem"),
            "status": chosen.get("status"),
        }

    microtopics = microtopics_for_capability(records, primary)
    for microtopic in microtopics:
        exit_task = microtopic.get("exit_task")
        if exit_task:
            return {
                "kind": "EXIT_TASK",
                "verification_ref": f'{microtopic["id"]}:exit_task',
                "microtopic_ref": microtopic["id"],
                "prompt": exit_task.get("prompt"),
                "source_ref": exit_task.get("source_ref"),
                "status": microtopic.get("status"),
            }
    return None


def _effective_help(request: dict) -> str:
    declared = request.get("help_used", "NONE")
    if declared not in HELP_LEVELS:
        return "UNKNOWN"
    if request.get("shown_hint_indices") and declared == "NONE":
        return "HINT"
    return declared


def observation_draft(request: dict, question: dict,
                      failed_capability_ref: str | None) -> dict | None:
    """Draft one capability observation when the attempt supports a clear attribution."""
    when = request.get("when")
    if not when:
        return None
    evaluation = request["evaluation"]
    result = evaluation["result"]
    error_stage = evaluation.get("error_stage", "UNKNOWN")
    help_used = _effective_help(request)

    if result == "CORRECT":
        capability = question["primary_capability_ref"]
        state = "DEMONSTRATED" if help_used in INDEPENDENT_HELP else "UNCERTAIN"
    elif result == "INCORRECT" and failed_capability_ref:
        capability = failed_capability_ref
        state = "MISSING" if error_stage in {"CONCEPT", "SETUP"} else "UNCERTAIN"
    else:
        return None

    response = request.get("response_summary") or request.get("response") or result
    return {
        "observation_id": request.get("observation_id")
        or f'OBS-{question["id"]}-ATTEMPT-{request.get("attempt_number", 1)}',
        "capability_ref": capability,
        "method": f'question attempt {question["id"]}',
        "evidence_kind": "DIRECT_ATTEMPT",
        "provenance": "UNREVIEWED_SESSION_DRAFT",
        "question_ref": question["id"],
        **({"session_ref": request["session_ref"]} if request.get("session_ref") else {}),
        "observed": str(response),
        "result": state,
        "when": when,
        "help": help_used,
        "error_stage": error_stage,
    }


def run(request: dict, repo: Path = REPO) -> dict:
    """Return the next safe learner action and an optional observation draft."""
    subject = request.get("subject")
    question_ref = request.get("question_ref")
    evaluation = request.get("evaluation") or {}
    result = evaluation.get("result")
    findings = []

    if result not in RESULTS:
        return {
            "question_ref": question_ref,
            "next_action": "STOP",
            "findings": [{
                "point": "FEEDBACK_RESULT_INVALID",
                "detail": f"evaluation.result must be one of {', '.join(sorted(RESULTS))}",
            }],
            "passed": False,
        }

    if evaluation.get("error_stage", "UNKNOWN") not in ERROR_STAGES:
        findings.append({
            "point": "FEEDBACK_ERROR_STAGE_INVALID",
            "detail": "evaluation.error_stage is outside the small feedback vocabulary",
        })

    records = subject_records(subject, repo)
    question, question_origin, question_findings = resolve_question_input(request, records)
    findings.extend(question_findings)
    if question is None:
        return {
            "question_ref": question_ref,
            "next_action": "STOP",
            "findings": findings,
            "passed": False,
        }

    candidates = required_capabilities(question)
    prerequisites = prerequisite_capabilities(records, candidates)
    attributable = [*candidates, *prerequisites]
    failed = evaluation.get("failed_capability_ref")
    if failed and failed not in attributable:
        findings.append({
            "point": "FEEDBACK_FAILED_CAPABILITY_NOT_REQUIRED",
            "capability_ref": failed,
            "detail": (
                "failed_capability_ref is neither direct question demand nor a canonical "
                "prerequisite of that demand"
            ),
        })
        failed = None
    if result == "INCORRECT" and not failed and len(candidates) == 1:
        failed = candidates[0]

    diagnostic_evidence, diagnostic_findings = _validate_diagnostic_evidence(
        records, failed, evaluation.get("diagnostic_evidence")
    )
    findings.extend(diagnostic_findings)
    if evaluation.get("misconception_index") is not None and diagnostic_evidence is None:
        findings.append({
            "point": "DIAGNOSTIC_EVIDENCE_REQUIRED",
            "detail": (
                "misconception_index is only a hypothesis selector; misconception-specific "
                "repair requires canonical probe/response evidence and an explicit diagnosis"
            ),
        })

    observation = observation_draft(request, question, failed)
    review = (
        review_schedule.schedule(observation, transfer=bool(question.get("transfer")))
        if observation is not None else None
    )
    base = {
        "question_ref": question["id"],
        "question_origin": question_origin,
        "result": result,
        "failed_capability_ref": failed,
        "candidate_capabilities": candidates,
        "observation_draft": observation,
        "review": review,
        "diagnostic_evidence": diagnostic_evidence,
        "findings": findings,
    }

    if result == "UNDECIDABLE":
        return {
            **base,
            "next_action": "DIAGNOSE",
            "diagnostic_options": diagnostic_options(records, candidates),
            "passed": not findings,
        }

    if result == "CORRECT":
        help_used = _effective_help(request)
        if help_used == "NONE":
            return {
                **base,
                "next_action": "CONTINUE",
                "passed": not findings,
            }
        verification = verification_candidate(
            records, question, request.get("attempted_question_refs", [])
        )
        return {
            **base,
            "next_action": "VERIFY" if verification else "VERIFICATION_ITEM_REQUIRED",
            "verification": verification,
            "passed": not findings,
        }

    # Incorrect multi-capability work must be diagnosed before routing a repair. Guessing
    # the failed capability would turn one wrong final answer into a false learner model.
    if not failed:
        return {
            **base,
            "next_action": "DIAGNOSE",
            "diagnostic_options": diagnostic_options(records, candidates),
            "passed": not findings,
        }

    attempt_number = max(1, int(request.get("attempt_number", 1)))
    if attempt_number <= 2:
        hint = next_safe_hint(question, request.get("shown_hint_indices", []))
        if hint is not None:
            return {
                **base,
                "next_action": "RETRY",
                "hint": hint,
                "passed": not findings,
            }
        if question.get("_worksheet_mapping") and (
            diagnostic_evidence is None or diagnostic_evidence["diagnosis"] != "CONFIRMED"
        ):
            # The transient worksheet row truthfully carries no canonical hint ladder.
            # Diagnose from governed misconception prompts rather than fabricating a hint
            # just to keep the retry cadence symmetrical with canonical questions.
            return {
                **base,
                "next_action": "DIAGNOSE",
                "diagnostic_options": diagnostic_options(records, [failed]),
                "passed": not findings,
            }

    diagnostic_claim_present = (
        evaluation.get("diagnostic_evidence") is not None
        or evaluation.get("misconception_index") is not None
    )
    if diagnostic_claim_present and (
        diagnostic_evidence is None or diagnostic_evidence["diagnosis"] != "CONFIRMED"
    ):
        return {
            **base,
            "next_action": "DIAGNOSE",
            "diagnostic_options": diagnostic_options(records, [failed]),
            "passed": not findings,
        }

    repair = repair_for(
        records,
        question,
        failed,
        (
            diagnostic_evidence["misconception_index"]
            if diagnostic_evidence is not None
            else None
        ),
    )
    if repair is None:
        return {
            **base,
            "next_action": "DIAGNOSE",
            "diagnostic_options": diagnostic_options(records, [failed]),
            "passed": not findings,
        }

    verification = verification_candidate(
        records, question, request.get("attempted_question_refs", [])
    )
    return {
        **base,
        "next_action": "REPAIR",
        "repair": repair,
        "after_repair": (
            {"next_action": "VERIFY", "verification": verification}
            if verification else {"next_action": "VERIFICATION_ITEM_REQUIRED"}
        ),
        "passed": not findings,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    request = json.loads(args.input.read_text(encoding="utf-8"))
    report = run(request)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
