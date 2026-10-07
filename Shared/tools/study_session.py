#!/usr/bin/env python3
"""Thin practical runner for one self-study worksheet session.

This file deliberately composes existing core contracts instead of inventing another
learning model:

    worksheet map
    -> session readiness
    -> learner-facing study plan
    -> attempt feedback
    -> observation draft + review date

It does not author curriculum, grade free-form work, mutate learner profiles, or persist
observations silently. The caller still supplies the evaluated attempt outcome.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.contracts import load  # noqa: E402
from Shared.tools import (  # noqa: E402
    capability_delivery,
    capability_graph,
    feedback,
    session_readiness,
    study_map,
    worksheet_study_plan,
)

READY = session_readiness.READY
READY_WITH_BRIDGE = session_readiness.READY_WITH_BRIDGE
PILOT_READY = session_readiness.PILOT_READY
NOT_READY = session_readiness.NOT_READY

EXECUTE_WITH_FALLBACK = "EXECUTE_WITH_FALLBACK"
OWNER_DECISION = "OWNER_DECISION"

OWNER_LOCATION = "LOCATION"
OWNER_EXTERNAL = "EXTERNAL"

NONEXECUTABLE_RUNG_POINTS = {
    "READINESS_MICROTOPIC_MISSING",
    "READINESS_CAPABILITY_MISSING",
    "READINESS_TEACHING_PATH_MISSING",
}

HARD_PLAN_FINDINGS = {
    "WORKSHEET_MAP_STRUCTURE",
    "WORKSHEET_QUESTION_ID_DUPLICATE",
    "WORKSHEET_STUDY_PLAN_SYNTHETIC_PROFILE_REFUSED",
    "STUDY_ROUTE_PREREQUISITE_UNKNOWN",
    "STUDY_ROUTE_PREREQUISITE_CYCLE",
}


def _matrices(subject: str, repo: Path = REPO) -> list[dict]:
    root = repo / subject / "matrices"
    if not root.is_dir():
        return []
    return [load(path) for path in sorted(root.glob("*.rungs.json"))]


def resolve_estimates(subject: str, raw_values: list[str],
                      repo: Path = REPO) -> tuple[list[dict], list[dict]]:
    """Resolve human-friendly TARGET=PERCENT estimates to canonical matrix ids.

    TARGET may be an exact matrix id, bucket id, or subtopic name. Subtopic matching is
    case-insensitive but otherwise exact; fuzzy topic guessing would be unsafe here.
    """
    boards = _matrices(subject, repo)
    estimates: list[dict] = []
    findings: list[dict] = []

    for raw in raw_values:
        if "=" not in raw:
            findings.append({
                "point": "STUDY_SESSION_ESTIMATE_FORMAT",
                "detail": f"{raw!r} must be TARGET=PERCENT",
            })
            continue

        target, percent_text = raw.rsplit("=", 1)
        target = target.strip()
        try:
            percentage = float(percent_text.strip())
        except ValueError:
            findings.append({
                "point": "STUDY_SESSION_ESTIMATE_PERCENT_INVALID",
                "target": target,
                "detail": f"{percent_text!r} is not a number",
            })
            continue

        if percentage < 0 or percentage > 100:
            findings.append({
                "point": "STUDY_SESSION_ESTIMATE_PERCENT_OUT_OF_RANGE",
                "target": target,
                "detail": "percentage must be between 0 and 100",
            })
            continue

        matches = [
            board for board in boards
            if target == board.get("matrix_id")
            or target == board.get("bucket_id")
            or target.casefold() == str(board.get("subtopic") or "").casefold()
        ]
        if not matches:
            findings.append({
                "point": "STUDY_SESSION_ESTIMATE_TARGET_UNKNOWN",
                "target": target,
                "detail": "target does not match a matrix id, bucket id, or exact subtopic",
            })
            continue
        if len(matches) > 1:
            findings.append({
                "point": "STUDY_SESSION_ESTIMATE_TARGET_AMBIGUOUS",
                "target": target,
                "matrices": sorted(board["matrix_id"] for board in matches),
                "detail": "target matches more than one matrix; use matrix_id",
            })
            continue

        board = matches[0]
        estimates.append({
            "matrix_id": board["matrix_id"],
            "knowledge_percentage": percentage,
            "input_target": target,
        })

    return estimates, findings


def resolve_owner_choices(raw_values: list[str]) -> tuple[dict[str, dict], list[dict]]:
    """Parse session-only owner resolutions without changing canonical records."""
    choices: dict[str, dict] = {}
    warnings: list[dict] = []
    for raw in raw_values:
        if "=" not in raw:
            warnings.append({
                "point": "STUDY_SESSION_OWNER_CHOICE_FORMAT",
                "detail": f"{raw!r} must name a capability and a resolution",
            })
            continue
        capability, payload = raw.split("=", 1)
        capability = capability.strip()
        payload = payload.strip()
        if not capability or ":" not in payload:
            warnings.append({
                "point": "STUDY_SESSION_OWNER_CHOICE_FORMAT",
                "capability_ref": capability or None,
                "detail": "owner choice is missing a capability or resolution payload",
            })
            continue
        if capability in choices:
            warnings.append({
                "point": "STUDY_SESSION_OWNER_CHOICE_DUPLICATE",
                "capability_ref": capability,
                "detail": "only the first session owner choice for a capability is used",
            })
            continue

        kind, rest = payload.split(":", 1)
        kind = kind.strip().upper()
        if kind == OWNER_EXTERNAL:
            provider = rest.strip()
            if not provider:
                warnings.append({
                    "point": "STUDY_SESSION_OWNER_CHOICE_FORMAT",
                    "capability_ref": capability,
                    "detail": "EXTERNAL choice requires a provider label",
                })
                continue
            choices[capability] = {
                "kind": OWNER_EXTERNAL,
                "provider": provider,
                "scope": "SESSION_ONLY",
            }
            continue

        if kind == OWNER_LOCATION:
            parts = rest.split(":", 1)
            if len(parts) != 2 or not all(part.strip() for part in parts):
                warnings.append({
                    "point": "STUDY_SESSION_OWNER_CHOICE_FORMAT",
                    "capability_ref": capability,
                    "detail": "LOCATION choice requires MATRIX_ID:RUNG",
                })
                continue
            choices[capability] = {
                "kind": OWNER_LOCATION,
                "matrix_id": parts[0].strip(),
                "rung": parts[1].strip(),
                "scope": "SESSION_ONLY",
            }
            continue

        warnings.append({
            "point": "STUDY_SESSION_OWNER_CHOICE_KIND_UNKNOWN",
            "capability_ref": capability,
            "detail": f"{kind!r} is not a supported session owner resolution",
        })
    return choices, warnings


def _touched_matrix_ids(study_plan: dict) -> list[str]:
    found = []
    for row in study_plan.get("route", []):
        for location in row.get("locations", []):
            matrix_id = location.get("matrix_id")
            if matrix_id and matrix_id not in found:
                found.append(matrix_id)
    return found


def _session_status(readiness_rows: list[dict], study_plan: dict) -> str:
    """Keep matrix readiness truthful; execution fallback is decided separately."""
    statuses = {row.get("status") for row in readiness_rows}
    if NOT_READY in statuses:
        return NOT_READY
    if PILOT_READY in statuses:
        return PILOT_READY
    if READY_WITH_BRIDGE in statuses:
        return READY_WITH_BRIDGE
    return READY


def _rung_detail(readiness: dict | None, rung: str | None) -> dict | None:
    if readiness is None or not rung:
        return None
    for row in readiness.get("rungs", []):
        if row.get("rung") == rung:
            return row
    return None


def _rung_state(readiness: dict | None, rung: str | None) -> str | None:
    detail = _rung_detail(readiness, rung)
    return detail.get("state") if detail else None


def _rung_execution_blockers(readiness: dict | None, rung: str | None) -> list[dict]:
    if readiness is None or not rung:
        return []
    return [
        row for row in readiness.get("blocking_findings", [])
        if row.get("where") == rung
        and row.get("point") in NONEXECUTABLE_RUNG_POINTS
    ]


def _route_execution(
    study_plan: dict,
    readiness_rows: list[dict],
    warnings: list[dict],
    owner_choices: dict[str, dict] | None = None,
):
    """Annotate exceptional execution states and apply session-only owner choices."""
    by_matrix = {row.get("matrix_id"): row for row in readiness_rows}
    choices = owner_choices or {}
    route = []
    owner_decisions = []
    fallback_reasons = []
    applied_owner_choices = []
    choice_warnings = []
    executable = 0
    owner_required: set[str] = set()
    route_capabilities = {
        row.get("capability_ref")
        for row in study_plan.get("route", [])
        if row.get("capability_ref")
    }

    def bridge(item: dict, capability: str, choice: dict) -> None:
        provider = choice["provider"]
        item["recommended_action"] = "BRIDGE"
        item["action_reason"] = (
            f"Session-only owner bridge via {provider}; canonical delivery is unchanged."
        )
        item["external_provider"] = provider
        item["provider"] = provider
        item["acceptance_status"] = "SESSION_OWNER_CHOICE"
        item["locations"] = []
        item["lessons"] = []
        item["owner_choice"] = dict(choice)
        item["execution_disposition"] = EXECUTE_WITH_FALLBACK
        applied_owner_choices.append({"capability_ref": capability, **choice})
        fallback_reasons.append({
            "capability_ref": capability,
            "reason": "session-only owner bridge; canonical teaching truth is unchanged",
        })

    for row in study_plan.get("route", []):
        item = dict(row)
        capability = item.get("capability_ref")
        choice = choices.get(capability)
        action = item.get("recommended_action")
        disposition = None

        if action == "SKIP":
            item["execution_disposition"] = None
            route.append(item)
            continue

        blocked_dependencies = [
            ref for ref in item.get("depends_on", [])
            if ref in owner_required
        ]
        if blocked_dependencies:
            disposition = OWNER_DECISION
            owner_required.add(capability)
            owner_decisions.append({
                "capability_ref": capability,
                "depends_on": blocked_dependencies,
                "reason": (
                    "a prerequisite requires an owner decision; dependent study cannot "
                    "safely leap over that prerequisite"
                ),
            })
            item["execution_disposition"] = disposition
            route.append(item)
            continue

        if item.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE:
            executable += 1
            item["execution_disposition"] = None
            route.append(item)
            continue

        locations = list(item.get("locations") or [])
        owner_selected_location = False
        if choice and choice.get("kind") == OWNER_LOCATION:
            matches = [
                location for location in locations
                if location.get("matrix_id") == choice.get("matrix_id")
                and location.get("rung") == choice.get("rung")
            ]
            if len(matches) == 1 and (
                item.get("state") != "RESOLVED" or len(locations) != 1
            ):
                selected = matches[0]
                locations = [selected]
                item["locations"] = [selected]
                item["lessons"] = [
                    lesson for lesson in item.get("lessons", [])
                    if lesson.get("matrix_id") == selected.get("matrix_id")
                    and lesson.get("rung") == selected.get("rung")
                ]
                item["owner_choice"] = dict(choice)
                owner_selected_location = True
                applied_owner_choices.append({"capability_ref": capability, **choice})

        unresolved = (
            item.get("state") != "RESOLVED" or len(locations) != 1
        ) and not owner_selected_location

        if unresolved:
            if choice and choice.get("kind") == OWNER_EXTERNAL:
                bridge(item, capability, choice)
                executable += 1
                route.append(item)
                continue
            disposition = OWNER_DECISION
            owner_required.add(capability)
            owner_decisions.append({
                "capability_ref": capability,
                "reason": (
                    "supplied location is not one of the offered canonical locations"
                    if choice and choice.get("kind") == OWNER_LOCATION
                    else "canonical teaching delivery is unresolved or ambiguous"
                ),
            })
        else:
            location = locations[0]
            readiness = by_matrix.get(location.get("matrix_id"))
            rung_state = _rung_state(readiness, location.get("rung"))
            rung_blockers = _rung_execution_blockers(readiness, location.get("rung"))
            if rung_state in {None, "BLOCKED"} or rung_blockers:
                if choice and choice.get("kind") == OWNER_EXTERNAL:
                    bridge(item, capability, choice)
                    executable += 1
                    route.append(item)
                    continue
                disposition = OWNER_DECISION
                owner_required.add(capability)
                owner_decisions.append({
                    "capability_ref": capability,
                    "matrix_id": location.get("matrix_id"),
                    "rung": location.get("rung"),
                    "blocking_points": [row.get("point") for row in rung_blockers],
                    "reason": (
                        "the demanded rung has no safe teaching path; use an owner external "
                        "bridge or repair the canonical content"
                    ),
                })
            else:
                executable += 1
                if owner_selected_location:
                    disposition = EXECUTE_WITH_FALLBACK
                    fallback_reasons.append({
                        "capability_ref": capability,
                        "matrix_id": location.get("matrix_id"),
                        "rung": location.get("rung"),
                        "reason": (
                            "owner selected one offered canonical location for this session; "
                            "canonical ambiguity remains visible"
                        ),
                    })
                elif (
                    rung_state == "NEEDS_SUPPORT"
                    or readiness.get("status") in {PILOT_READY, NOT_READY}
                ):
                    disposition = EXECUTE_WITH_FALLBACK
                    fallback_reasons.append({
                        "capability_ref": capability,
                        "matrix_id": location.get("matrix_id"),
                        "rung": location.get("rung"),
                        "reason": (
                            "the demanded rung is usable, but surrounding support/content "
                            "gaps remain visible"
                        ),
                    })

        item["execution_disposition"] = disposition
        route.append(item)

    applied_caps = {row["capability_ref"] for row in applied_owner_choices}
    for capability in choices:
        if capability in applied_caps:
            continue
        if capability not in route_capabilities:
            choice_warnings.append({
                "point": "STUDY_SESSION_OWNER_CHOICE_TARGET_UNKNOWN",
                "capability_ref": capability,
                "detail": "owner choice names no capability in the current route",
            })
        elif capability not in owner_required:
            choice_warnings.append({
                "point": "STUDY_SESSION_OWNER_CHOICE_NOT_REQUIRED",
                "capability_ref": capability,
                "detail": "canonical route is already executable; owner choice was ignored",
            })

    if executable:
        overall = (
            EXECUTE_WITH_FALLBACK
            if warnings or fallback_reasons or owner_decisions
            else None
        )
    elif owner_decisions:
        overall = OWNER_DECISION
    else:
        overall = None

    return (
        route,
        owner_decisions,
        fallback_reasons,
        executable,
        overall,
        applied_owner_choices,
        choice_warnings,
    )

def _question_execution(questions: list[dict], route: list[dict]) -> tuple[list[dict], list[str], list[str]]:
    """Project route-level fallback onto worksheet questions without inventing new states."""
    by_capability = {
        row.get("capability_ref"): row
        for row in route
        if row.get("capability_ref")
    }

    def closure(capability_ref: str, seen: set[str] | None = None) -> list[dict]:
        seen = set() if seen is None else seen
        if capability_ref in seen:
            return []
        seen.add(capability_ref)
        row = by_capability.get(capability_ref)
        if row is None:
            return []
        out = [row]
        for dependency in row.get("depends_on", []):
            out.extend(closure(dependency, seen))
        return out

    annotated = []
    executable_questions = []
    owner_questions = []
    for question in questions:
        item = dict(question)
        roots = [
            question.get("primary_capability_ref"),
            *list(question.get("secondary_capability_refs") or []),
        ]
        rows = []
        seen_caps: set[str] = set()
        for root in roots:
            if not root:
                continue
            for row in closure(root):
                capability = row.get("capability_ref")
                if capability in seen_caps:
                    continue
                seen_caps.add(capability)
                rows.append(row)

        owner_caps = [
            row.get("capability_ref")
            for row in rows
            if row.get("execution_disposition") == OWNER_DECISION
        ]
        fallback_caps = [
            row.get("capability_ref")
            for row in rows
            if row.get("execution_disposition") == EXECUTE_WITH_FALLBACK
        ]

        if owner_caps:
            item["execution_disposition"] = OWNER_DECISION
            item["owner_decision_capabilities"] = owner_caps
            owner_questions.append(item.get("question_id"))
        elif fallback_caps:
            item["execution_disposition"] = EXECUTE_WITH_FALLBACK
            item["fallback_capabilities"] = fallback_caps
            executable_questions.append(item.get("question_id"))
        else:
            item["execution_disposition"] = None
            executable_questions.append(item.get("question_id"))
        annotated.append(item)

    return annotated, executable_questions, owner_questions


def _next_step(study_plan: dict) -> dict | None:
    for row in study_plan.get("route", []):
        if row.get("recommended_action") == "SKIP":
            continue
        if row.get("execution_disposition") == OWNER_DECISION:
            continue
        lessons = row.get("lessons", [])
        lesson = lessons[0] if lessons else None
        return {
            "order": row.get("order"),
            "action": row.get("recommended_action"),
            "capability_ref": row.get("capability_ref"),
            "lesson": lesson,
            "reason": row.get("action_reason"),
            "external_provider": row.get("external_provider"),
            "acceptance_status": row.get("acceptance_status"),
            "routing_posture": row.get("routing_posture"),
            "starting_support": row.get("starting_support"),
            "initial_visual": row.get("initial_visual"),
            "presentation": row.get("presentation"),
            "recommended_explorer_ref": row.get("recommended_explorer_ref"),
            "exercise_demand": row.get("exercise_demand"),
            "exercise_question_ref": row.get("exercise_question_ref"),
            "exercise_reason": row.get("exercise_reason"),
            "exercise_family_ref": row.get("exercise_family_ref"),
            "transfer_eligible": row.get("transfer_eligible", False),
            "transfer_dimension": row.get("transfer_dimension"),
            "transfer_evidence": row.get("transfer_evidence", []),
            "routing_persistence": row.get("routing_persistence"),
        }
    return None


def plan(mapping: dict, estimate_specs: list[str] | None = None,
         profile: dict | None = None, repo: Path = REPO, *,
         owner_choice_specs: list[str] | None = None) -> dict:
    """Compile a readiness-gated, learner-facing session plan."""
    subject = mapping.get("subject")
    estimates, estimate_findings = resolve_estimates(
        subject, estimate_specs or [], repo
    )
    owner_choices, owner_choice_parse_warnings = resolve_owner_choices(
        owner_choice_specs or []
    )
    study_plan = worksheet_study_plan.resolve(
        mapping,
        owner_estimates=estimates,
        profile=profile,
        repo=repo,
    )

    readiness_rows = [
        session_readiness.audit(subject, matrix_id=matrix_id, repo=repo)
        for matrix_id in _touched_matrix_ids(study_plan)
    ]
    status = _session_status(readiness_rows, study_plan)
    plan_findings = list(study_plan.get("findings", []))
    hard_findings = [
        row for row in plan_findings
        if row.get("point") in HARD_PLAN_FINDINGS
    ]
    decision_findings = [
        row for row in plan_findings
        if row.get("point") not in HARD_PLAN_FINDINGS
    ]
    warnings = [
        *estimate_findings,
        *list(study_plan.get("warnings", [])),
    ]

    (
        route,
        owner_decisions,
        fallback_reasons,
        executable_count,
        disposition,
        applied_owner_choices,
        owner_choice_warnings,
    ) = _route_execution(
        study_plan,
        readiness_rows,
        warnings,
        owner_choices,
    )
    applied_caps = {row["capability_ref"] for row in applied_owner_choices}
    owner_resolved_findings = []
    for finding in decision_findings:
        if finding.get("capability") in applied_caps:
            owner_resolved_findings.append(finding)
            continue
        owner_decisions.append({
            "point": finding.get("point"),
            "target": finding.get("where") or finding.get("capability"),
            "reason": finding.get("detail", ""),
        })
    if decision_findings and executable_count:
        disposition = EXECUTE_WITH_FALLBACK
    elif decision_findings and not executable_count:
        disposition = OWNER_DECISION

    questions, executable_question_ids, owner_decision_question_ids = _question_execution(
        list(study_plan.get("questions", [])),
        route,
    )

    academic_warnings = [
        {
            "matrix_id": row.get("matrix_id"),
            "subtopic": row.get("subtopic"),
            **warning,
        }
        for row in readiness_rows
        for warning in row.get("academic_warnings", [])
    ]

    valid = not hard_findings
    ready = (
        valid
        and executable_count > 0
        and disposition is None
        and status not in {PILOT_READY, NOT_READY}
        and study_plan.get("ready", True)
    )
    return {
        "worksheet_id": mapping.get("worksheet_id"),
        "subject": subject,
        "status": status,
        "valid": valid,
        "ready": ready,
        "profile_id": study_plan.get("profile_id"),
        "owner_estimates": estimates,
        "owner_choices": owner_choices,
        "applied_owner_choices": applied_owner_choices,
        "owner_choice_warnings": [
            *owner_choice_parse_warnings,
            *owner_choice_warnings,
        ],
        "owner_resolved_findings": owner_resolved_findings,
        "execution_disposition": disposition,
        "owner_decisions": owner_decisions,
        "fallback_reasons": fallback_reasons,
        "warnings": warnings,
        "readiness": [{
            "matrix_id": row.get("matrix_id"),
            "subtopic": row.get("subtopic"),
            "status": row.get("status"),
            "external_bridges": row.get("external_bridges", []),
            "support_findings": row.get("support_findings", []),
        } for row in readiness_rows],
        "next_step": _next_step({"route": route}) if valid and executable_count else None,
        "questions": questions,
        "executable_question_ids": executable_question_ids,
        "owner_decision_question_ids": owner_decision_question_ids,
        "route": route,
        "academic_warnings": academic_warnings,
        "findings": hard_findings,
        "blockers": list(study_plan.get("blockers", [])),
        "passed": valid,
        "rules": [
            "Matrix readiness remains truthful; execution may fall back only on demanded usable rungs.",
            "An unresolved prerequisite propagates OWNER_DECISION to its dependent route; the runner never leaps over an unresolved dependency.",
            "Session owner choices may select an offered canonical location or supply an external bridge, but never mutate canonical truth.",
            "Only EXECUTE_WITH_FALLBACK and OWNER_DECISION are added as exceptional execution dispositions.",
            "Owner percentages choose a local starting attempt; they are not mastery evidence.",
            "Worksheet questions remain transient demand unless separately promoted.",
            "Attempt evaluation is supplied by the caller; the runner does not pretend to grade free-form work.",
            "Observation drafts are returned explicitly and are never persisted silently.",
        ],
    }


def _question_readiness(
    mapping: dict,
    question: dict,
    repo: Path,
    *,
    result: str | None = None,
    failed_capability_ref: str | None = None,
) -> tuple[list[dict], list[dict], list[dict]]:
    """Return local readiness, blockers and explicit external bridges for one question.

    An external secondary capability should not prevent a local repair when the caller has
    already attributed the failure to a different locally taught capability. It *must*
    still block when the external capability itself is the failed capability, or when an
    incorrect/undecidable attempt has not been attributed and the external dependency could
    be the actual failure.
    """
    subject = mapping.get("subject")
    mapped = [
        question.get("primary_capability_ref"),
        *list(question.get("secondary_capability_refs") or []),
    ]

    # Direct question mappings stay sparse. A prerequisite is considered here only when
    # reviewed work explicitly attributes the failure to it; we do not copy prerequisite
    # closure into worksheet secondary capability mappings.
    caps, _ = capability_graph.subject_graph(subject, repo)
    prerequisite_refs = set(
        capability_graph.prerequisite_closure_many(
            [capability for capability in mapped if capability],
            caps,
        )
    )
    checked_capabilities = list(mapped)
    if (
        failed_capability_ref
        and failed_capability_ref in prerequisite_refs
        and failed_capability_ref not in checked_capabilities
    ):
        checked_capabilities.append(failed_capability_ref)

    from Shared.tools import study_map  # local import avoids a wider public surface

    index = study_map.subject_index(subject, repo)
    matrix_ids = []
    blockers = []
    external_bridges = []
    local_locations = []

    for capability in checked_capabilities:
        locations = list(index.get("locations", {}).get(capability, []))
        cap_record = index.get("capabilities", {}).get(capability, {})
        if not cap_record:
            blockers.append({
                "point": "STUDY_SESSION_QUESTION_CAPABILITY_UNKNOWN",
                "capability_ref": capability,
                "detail": "mapped question capability is not canonical in the selected subject",
            })
            continue

        delivery = capability_delivery.resolve(cap_record, locations)
        if delivery["state"] == capability_delivery.EXTERNAL_BRIDGE:
            bridge = {
                "capability_ref": capability,
                "external_provider": delivery["provider"],
                "acceptance_status": delivery.get("acceptance_status"),
            }
            external_bridges.append(bridge)
            bridge_can_be_failure = (
                result in {"INCORRECT", "UNDECIDABLE"}
                and (
                    failed_capability_ref is None
                    or failed_capability_ref == capability
                )
            )
            if bridge_can_be_failure:
                blockers.append({
                    "point": "STUDY_SESSION_QUESTION_EXTERNAL_ONLY",
                    **bridge,
                    "detail": (
                        "the attempt cannot be repaired locally because the failed "
                        "capability is external, or the failure is not yet attributed "
                        "well enough to exclude the external dependency"
                    ),
                })
            continue
        if delivery["state"] == capability_delivery.UNRESOLVED:
            blockers.append({
                "point": "STUDY_SESSION_QUESTION_DELIVERY_UNRESOLVED",
                "capability_ref": capability,
                "detail": "mapped question capability has no resolvable teaching delivery",
            })
            continue
        if delivery["state"] == capability_delivery.AMBIGUOUS:
            blockers.append({
                "point": "STUDY_SESSION_QUESTION_DELIVERY_AMBIGUOUS",
                "capability_ref": capability,
                "detail": "mapped question capability has more than one teaching location",
            })
            continue

        for location in delivery["locations"]:
            local_locations.append((capability, location))
            matrix_id = location.get("matrix_id")
            if matrix_id and matrix_id not in matrix_ids:
                matrix_ids.append(matrix_id)

    readiness_rows = [
        session_readiness.audit(subject, matrix_id=matrix_id, repo=repo)
        for matrix_id in matrix_ids
    ]
    readiness_by_matrix = {
        row.get("matrix_id"): row for row in readiness_rows
    }
    for capability, location in local_locations:
        if result not in {"INCORRECT", "UNDECIDABLE"}:
            continue
        if failed_capability_ref is not None and failed_capability_ref != capability:
            continue
        readiness = readiness_by_matrix.get(location.get("matrix_id"))
        rung_state = _rung_state(readiness, location.get("rung"))
        if rung_state in {None, "BLOCKED"}:
            blockers.append({
                "point": "STUDY_SESSION_QUESTION_RUNG_NOT_EXECUTABLE",
                "capability_ref": capability,
                "matrix_id": location.get("matrix_id"),
                "rung": location.get("rung"),
                "detail": (
                    "the failed capability cannot be repaired from the demanded rung "
                    "without an explicit owner decision"
                ),
            })

    return readiness_rows, blockers, external_bridges


def _primary_verification_supported(
    mapping: dict,
    question: dict,
    readiness_rows: list[dict],
    repo: Path = REPO,
) -> bool:
    """Whether canonical support can independently verify the question's primary capability."""
    primary = question.get("primary_capability_ref")
    if not primary:
        return False
    index = study_map.subject_index(mapping.get("subject"), repo)
    locations = list(index.get("locations", {}).get(primary, []))
    if len(locations) != 1:
        return False
    location = locations[0]
    readiness = next(
        (
            row for row in readiness_rows
            if row.get("matrix_id") == location.get("matrix_id")
        ),
        None,
    )
    detail = _rung_detail(readiness, location.get("rung"))
    return bool(detail and detail.get("verification"))


def _limit_demonstration_without_verification(
    report: dict,
    *,
    verification_supported: bool,
) -> dict:
    """Keep learning evidence conservative when no canonical fresh verification path exists."""
    observation = report.get("observation_draft")
    if (
        verification_supported
        or not observation
        or observation.get("result") != "DEMONSTRATED"
    ):
        return report

    limited = dict(report)
    limited_observation = dict(observation)
    limited_observation["result"] = "UNCERTAIN"
    limited_observation["independence"] = (
        "Independent correctness was observed, but the canonical capability has no "
        "fresh verification path; do not promote this draft to DEMONSTRATED yet."
    )
    limited["observation_draft"] = limited_observation
    limited["evidence_limited"] = {
        "point": "STUDY_SESSION_VERIFICATION_UNAVAILABLE",
        "detail": (
            "teaching/attempt may continue, but independent mastery evidence is held at "
            "UNCERTAIN until a fresh verification path exists"
        ),
    }
    return limited


def attempt(mapping: dict, question_id: str, *, result: str,
            when: str, failed_capability_ref: str | None = None,
            error_stage: str = "UNKNOWN", help_used: str = "NONE",
            attempt_number: int = 1, shown_hint_indices: list[int] | None = None,
            attempted_question_refs: list[str] | None = None,
            misconception_index: int | None = None,
            diagnostic_response: str | None = None,
            diagnosis: str | None = None,
            diagnostic_basis: str | None = None,
            response_summary: str | None = None,
            session_ref: str | None = None,
            repo: Path = REPO) -> dict:
    """Run feedback for one mapped worksheet question without persisting learner state."""
    question = next(
        (row for row in mapping.get("questions", []) if row.get("question_id") == question_id),
        None,
    )
    if question is None:
        return {
            "question_ref": question_id,
            "next_action": "STOP",
            "findings": [{
                "point": "STUDY_SESSION_QUESTION_NOT_IN_WORKSHEET",
                "detail": "question id is not present in the supplied worksheet map",
            }],
            "passed": False,
        }

    readiness_rows, blockers, external_bridges = _question_readiness(
        mapping,
        question,
        repo,
        result=result,
        failed_capability_ref=failed_capability_ref,
    )
    if blockers:
        return {
            "question_ref": question_id,
            "next_action": OWNER_DECISION,
            "execution_disposition": OWNER_DECISION,
            "readiness": readiness_rows,
            "external_bridges": external_bridges,
            "findings": blockers,
            "passed": True,
        }

    evaluation = {
        "result": result,
        "error_stage": error_stage,
    }
    if failed_capability_ref:
        evaluation["failed_capability_ref"] = failed_capability_ref
    if misconception_index is not None:
        evaluation["misconception_index"] = misconception_index
        if diagnostic_response is not None or diagnosis is not None or diagnostic_basis is not None:
            records = feedback.subject_records(mapping.get("subject"), repo)
            evidence, evidence_error = feedback.diagnostic_evidence_for(
                records,
                failed_capability_ref,
                misconception_index,
                diagnostic_response,
                diagnosis,
                diagnostic_basis,
            )
            if evidence is not None:
                evaluation["diagnostic_evidence"] = evidence
            else:
                evaluation["diagnostic_evidence"] = {
                    "misconception_index": misconception_index,
                    "probe": "",
                    "observed_response": diagnostic_response or "",
                    "diagnosis": diagnosis or "",
                    "basis": diagnostic_basis or "",
                    "_input_error": evidence_error,
                }

    request = {
        "subject": mapping.get("subject"),
        "question_ref": question_id,
        "worksheet_question": question,
        "attempt_number": attempt_number,
        "shown_hint_indices": shown_hint_indices or [],
        "attempted_question_refs": attempted_question_refs or [question_id],
        "help_used": help_used,
        "when": when,
        "session_ref": session_ref or mapping.get("worksheet_id"),
        "evaluation": evaluation,
    }
    if response_summary:
        request["response_summary"] = response_summary

    report = feedback.run(request, repo)
    if result == "CORRECT":
        report = _limit_demonstration_without_verification(
            report,
            verification_supported=_primary_verification_supported(
                mapping,
                question,
                readiness_rows,
                repo,
            ),
        )
    return {
        **report,
        "readiness": readiness_rows,
        "external_bridges": external_bridges,
        "persistence": "NOT_WRITTEN",
    }


def _lesson_label(step: dict | None) -> str:
    if not step:
        return ""
    lesson = step.get("lesson") or {}
    if lesson:
        return lesson.get("microtopic_title") or lesson.get("label") or ""
    if step.get("external_provider"):
        return f'External bridge: {step["external_provider"]}'
    return ""


def readable_plan(report: dict) -> str:
    out = [
        f'# Study session — {report.get("worksheet_id")}',
        "",
        f'  subject: {report.get("subject")}',
        f'  status:  {report.get("status")}',
        f'  execution: {report.get("execution_disposition") or "NORMAL"}',
        "",
    ]

    if report.get("applied_owner_choices"):
        out += ["## Applied session owner choices", ""]
        for choice in report["applied_owner_choices"]:
            if choice.get("kind") == OWNER_EXTERNAL:
                detail = f'External bridge: {choice.get("provider")}'
            else:
                detail = f'{choice.get("matrix_id")} / {choice.get("rung")}'
            out.append(f'- {choice.get("capability_ref")}: {detail}')
        out += [""]

    if report.get("owner_choice_warnings"):
        out += ["## Owner-choice warnings", ""]
        for warning in report["owner_choice_warnings"]:
            out.append(f'- {warning.get("point")}: {warning.get("detail", "")}')
        out += [""]

    if report.get("owner_estimates"):
        out += ["## Rough starting estimates", ""]
        for estimate in report["owner_estimates"]:
            out.append(
                f'- {estimate.get("input_target")}: '
                f'{estimate["knowledge_percentage"]:g}% -> {estimate["matrix_id"]}'
            )
        out += [""]

    out += ["## Subtopic readiness", ""]
    if not report.get("readiness"):
        out.append("- No local teaching matrix is required.")
    for row in report.get("readiness", []):
        out.append(
            f'- {row.get("subtopic") or row.get("matrix_id")}: {row.get("status")}'
        )
        for bridge in row.get("external_bridges", []):
            out.append(
                f'  - bridge: {bridge["capability_ref"]} -> '
                f'{bridge["external_provider"]}'
            )

    if report.get("next_step"):
        step = report["next_step"]
        out += ["", "## Start now", ""]
        out.append(
            f'1. {step.get("action")} — '
            f'{_lesson_label(step) or step.get("capability_ref")}'
        )
        if step.get("reason"):
            out.append(f'   {step["reason"]}')
        if step.get("routing_posture"):
            out.append(
                f'   route: {step["routing_posture"]} / '
                f'support {step.get("starting_support") or "unspecified"} / '
                f'demand {step.get("exercise_demand") or "unspecified"}'
            )
        presentation = step.get("presentation") or {}
        if presentation.get("checkpoint_prompt"):
            out.append(f'   checkpoint: {presentation["checkpoint_prompt"]}')
        visual = step.get("initial_visual") or {}
        if visual.get("representation_ref"):
            out.append(
                f'   visual: {visual.get("representation_ref")} -> '
                f'{visual.get("visual_stage_ref") or "no initial stage"}'
            )
        if step.get("recommended_explorer_ref"):
            out.append(f'   explorer: {step["recommended_explorer_ref"]}')
        if step.get("exercise_question_ref"):
            out.append(f'   exercise: {step["exercise_question_ref"]}')

    out += ["", "## Ordered study route", ""]
    for row in report.get("route", []):
        lessons = ", ".join(
            lesson.get("microtopic_title") or lesson.get("label") or ""
            for lesson in row.get("lessons", [])
        )
        if not lessons and row.get("recommended_action") == "BRIDGE":
            lessons = f'External bridge: {row.get("external_provider")}'
        out.append(
            f'{row.get("order", "-")}. {row.get("recommended_action")} — '
            f'{lessons or row.get("capability_ref")}'
        )

    out += ["", "## Worksheet questions", ""]
    for row in report.get("questions", []):
        execution = row.get("execution_disposition")
        suffix = f' / {execution}' if execution else ''
        out.append(
            f'- {row.get("question_id")}: {row.get("what_is_being_learned")} '
            f'[{row.get("learner_state")}{suffix}]'
        )
        out.append(f'  {row.get("why_extra_attention")}')

    if report.get("warnings"):
        out += ["", "## Fallback warnings", ""]
        for warning in report["warnings"]:
            out.append(f'- {warning.get("point")}: {warning.get("detail", "")}')

    if report.get("owner_decisions"):
        out += ["", "## Owner decisions", ""]
        for decision in report["owner_decisions"]:
            target = decision.get("target") or decision.get("capability_ref") or decision.get("matrix_id")
            out.append(f'- {target}: {decision.get("reason", "")}')

    if report.get("academic_warnings"):
        out += ["", "## Parent warnings", ""]
        seen = set()
        for warning in report["academic_warnings"]:
            key = (warning.get("matrix_id"), warning.get("point"))
            if key in seen:
                continue
            seen.add(key)
            out.append(
                f'- {warning.get("subtopic") or warning.get("matrix_id")}: '
                f'{warning.get("detail")}'
            )

    if report.get("findings"):
        out += ["", "## Blocking/input findings", ""]
        for finding in report["findings"]:
            out.append(
                f'- {finding.get("point")}: {finding.get("detail", "")}'
            )
    return "\n".join(out)


def readable_attempt(report: dict) -> str:
    out = [
        f'# Attempt feedback — {report.get("question_ref")}',
        "",
        f'  next: {report.get("next_action")}',
        "",
    ]
    hint = report.get("hint")
    if hint:
        out += ["## Hint", "", hint.get("text", ""), ""]

    if report.get("diagnostic_options"):
        out += ["## Diagnose", ""]
        for option in report["diagnostic_options"]:
            for diagnostic in option.get("diagnostics", []):
                out.append(f'- {diagnostic.get("diagnostic_prompt")}')

    repair = report.get("repair")
    if repair:
        out += ["", "## Repair", ""]
        if repair.get("repair"):
            out.append(repair["repair"])
        elif repair.get("action"):
            out.append(repair["action"])
        elif repair.get("title"):
            out.append(f'Review: {repair["title"]}')

    after = report.get("after_repair") or {}
    verification = after.get("verification") or report.get("verification")
    if verification:
        out += ["", "## Fresh verification", ""]
        prompt = verification.get("stem") or verification.get("prompt")
        out.append(str(prompt or verification.get("question_ref") or verification.get("verification_ref")))

    observation = report.get("observation_draft")
    if observation:
        out += ["", "## Observation draft", ""]
        out.append(
            f'{observation.get("capability_ref")}: {observation.get("result")} '
            f'({observation.get("help")})'
        )

    review = report.get("review")
    if review:
        out += ["", f'Next review: {review.get("next_review")}']

    if report.get("evidence_limited"):
        out += ["", "## Evidence limit", ""]
        out.append(report["evidence_limited"].get("detail", ""))

    if report.get("findings"):
        out += ["", "## Findings", ""]
        for finding in report["findings"]:
            out.append(f'- {finding.get("point")}: {finding.get("detail", "")}')

    out += ["", "Learner state was not written automatically."]
    return "\n".join(out)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="command", required=True)

    p_plan = sub.add_parser("plan", help="compile the start-of-session study plan")
    p_plan.add_argument("--map", type=Path, required=True)
    p_plan.add_argument("--profile", type=Path)
    p_plan.add_argument(
        "--estimate",
        action="append",
        default=[],
        metavar="TARGET=PERCENT",
        help="TARGET is matrix id, bucket id, or exact subtopic name; may repeat",
    )
    p_plan.add_argument(
        "--owner-choice",
        action="append",
        default=[],
        metavar="CAPABILITY=LOCATION:MATRIX:RUNG|EXTERNAL:PROVIDER",
        help="session-only owner resolution; may repeat",
    )
    p_plan.add_argument("--readable", action="store_true")
    p_plan.add_argument("--enforce", action="store_true")

    p_attempt = sub.add_parser("attempt", help="run feedback for one mapped question")
    p_attempt.add_argument("--map", type=Path, required=True)
    p_attempt.add_argument("--question", required=True)
    p_attempt.add_argument("--result", choices=sorted(feedback.RESULTS), required=True)
    p_attempt.add_argument("--when", required=True, help="ISO date/timestamp")
    p_attempt.add_argument("--failed-capability")
    p_attempt.add_argument(
        "--error-stage", choices=sorted(feedback.ERROR_STAGES), default="UNKNOWN"
    )
    p_attempt.add_argument(
        "--help-used", choices=sorted(feedback.HELP_LEVELS), default="NONE"
    )
    p_attempt.add_argument("--attempt-number", type=int, default=1)
    p_attempt.add_argument("--shown-hint", action="append", type=int, default=[])
    p_attempt.add_argument("--attempted-question", action="append", default=[])
    p_attempt.add_argument("--misconception-index", type=int)
    p_attempt.add_argument("--diagnostic-response")
    p_attempt.add_argument("--diagnosis", choices=sorted(feedback.DIAGNOSIS_STATES))
    p_attempt.add_argument("--diagnostic-basis")
    p_attempt.add_argument("--response-summary")
    p_attempt.add_argument("--session-ref")
    p_attempt.add_argument("--readable", action="store_true")
    p_attempt.add_argument("--enforce", action="store_true")

    args = parser.parse_args()
    mapping = load(args.map)

    if args.command == "plan":
        profile = load(args.profile) if args.profile else None
        report = plan(
            mapping,
            args.estimate,
            profile,
            owner_choice_specs=args.owner_choice,
        )
        print(readable_plan(report) if args.readable
              else json.dumps(report, indent=2, ensure_ascii=False))
        return 1 if args.enforce and not report["passed"] else 0

    report = attempt(
        mapping,
        args.question,
        result=args.result,
        when=args.when,
        failed_capability_ref=args.failed_capability,
        error_stage=args.error_stage,
        help_used=args.help_used,
        attempt_number=args.attempt_number,
        shown_hint_indices=args.shown_hint,
        attempted_question_refs=args.attempted_question,
        misconception_index=args.misconception_index,
        diagnostic_response=args.diagnostic_response,
        diagnosis=args.diagnosis,
        diagnostic_basis=args.diagnostic_basis,
        response_summary=args.response_summary,
        session_ref=args.session_ref,
    )
    print(readable_attempt(report) if args.readable
          else json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
