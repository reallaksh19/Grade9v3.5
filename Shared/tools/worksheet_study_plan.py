#!/usr/bin/env python3
"""Compile one learner-facing worksheet -> study plan from existing core layers.

This is an orchestration/view layer, not a new learning architecture. It composes:

    worksheet map
    -> canonical question/capability locations
    -> prerequisite-ordered study route
    -> optional local owner-estimate start hints
    -> optional learner evidence overlay

The output deliberately keeps question demand, canonical teaching truth, owner estimates
and learner evidence separate. Owner estimates never become mastery evidence, and learner
state never enters matrices or capabilities.
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
from Shared.library.resolve import build_index, load_packages  # noqa: E402
from Shared.tools import (  # noqa: E402
    capability_delivery,
    learner_evidence,
    learning_router,
    study_map,
    study_start,
)

STATE_PRIORITY = {
    "MISSING": 40,
    "UNCERTAIN": 30,
    "UNOBSERVED": 20,
    "DEMONSTRATED": 10,
}


def _lesson(location: dict, index: dict) -> dict:
    microtopic_ref = location.get("microtopic_ref")
    microtopic = index["microtopics"].get(microtopic_ref, {})
    title = microtopic.get("title")
    label_base = (
        location.get("subtopic")
        or location.get("topic")
        or location.get("matrix_id")
        or "unknown matrix"
    )
    rung = location.get("rung")
    label = f"{label_base} / {rung}" if rung else str(label_base)
    return {
        "matrix_id": location.get("matrix_id"),
        "bucket_id": location.get("bucket_id"),
        "rung": rung,
        "ladder_position": location.get("ladder_position"),
        "microtopic_ref": microtopic_ref,
        "microtopic_title": title,
        "intrinsic_difficulty": microtopic.get("intrinsic_badge"),
        "difficulty_reason": microtopic.get("badge_reason"),
        "label": label,
    }


def _matrix_views(subject: str, index: dict, matrix_ids: list[str],
                  start_decisions: list[dict], repo: Path) -> list[dict]:
    """Project canonical matrices into the view without copying them into learner state."""
    wanted = set(matrix_ids)
    decisions = {row["matrix_id"]: row for row in start_decisions}
    boards: dict[str, dict] = {}
    root = repo / subject / "matrices"
    if root.is_dir():
        for path in sorted(root.glob("*.rungs.json")):
            board = load(path)
            matrix_id = board.get("matrix_id")
            if matrix_id in wanted:
                boards[matrix_id] = board

    views = []
    for matrix_id in matrix_ids:
        board = boards.get(matrix_id)
        if board is None:
            continue
        rungs = []
        for rung in sorted(
            board.get("rungs", []),
            key=lambda row: (
                int(row.get("ladder_position") or 0),
                str(row.get("rung") or ""),
            ),
        ):
            microtopic_ref = rung.get("microtopic_ref")
            microtopic = index["microtopics"].get(microtopic_ref, {})
            capability_ref = microtopic.get("primary_capability_ref")
            capability = index["capabilities"].get(capability_ref, {})
            rungs.append({
                "rung": rung.get("rung"),
                "ladder_position": rung.get("ladder_position"),
                "capability_ref": capability_ref,
                "microtopic_ref": microtopic_ref,
                "what_the_learner_owns": microtopic.get("title"),
                "intrinsic_difficulty": microtopic.get("intrinsic_badge"),
                "difficulty_reason": microtopic.get("badge_reason"),
                "prerequisite_refs": list(capability.get("prerequisite_refs") or []),
                "default_entry_eligible": rung.get("default_entry_eligible", True),
            })
        views.append({
            "matrix_id": matrix_id,
            "bucket_id": board.get("bucket_id"),
            "topic": board.get("topic"),
            "subtopic": board.get("subtopic"),
            "axis_note": board.get("axis_note"),
            "family_invariant": (board.get("family") or {}).get("invariant_demand"),
            "owner_start_decision": decisions.get(matrix_id),
            "rungs": rungs,
        })
    return views


def _profile_state(profile: dict | None, capability_ref: str,
                   repo: Path) -> dict:
    if profile is None:
        return {
            "state": "UNOBSERVED",
            "source": "NO_PROFILE",
            "observation_ref": None,
            "when": None,
            "help": None,
            "error_stage": None,
        }
    return learner_evidence.effective_state(profile, capability_ref, repo)


def _observation_lookup(profile: dict | None, repo: Path) -> dict[str, dict]:
    if profile is None:
        return {}
    all_observations = learner_evidence.load_observations(repo)
    return {
        ref: all_observations[ref]
        for ref in profile.get("observation_refs", [])
        if ref in all_observations
    }


def _attention_for(capabilities: list[dict], observations: dict[str, dict]) -> tuple[str, str]:
    """Return question-level learner state and an evidence-grounded attention note."""
    if not capabilities:
        return "UNOBSERVED", "No mapped capability is available to diagnose."

    worst = max(
        capabilities,
        key=lambda row: STATE_PRIORITY.get(row["learner_state"]["state"], 0),
    )
    state = worst["learner_state"]["state"]
    evidence = worst["learner_state"]
    observation_ref = evidence.get("observation_ref")
    observation = observations.get(observation_ref or "")

    if observation:
        observed = observation.get("observed", "").strip()
        stage = observation.get("error_stage")
        prefix = f"{stage.title()} — " if stage and stage != "UNKNOWN" else ""
        if observed:
            return state, f"{prefix}{observed}"
    capability = worst.get("capability_ref")
    if state == "MISSING":
        return state, f"{capability} is currently marked missing; teach before retry."
    if state == "UNCERTAIN":
        return state, f"{capability} is currently uncertain; repair then retry independently."
    if state == "DEMONSTRATED":
        return state, "Mapped capability is already demonstrated; use this mainly as consolidation."
    return state, "No learner evidence yet; use the first attempt as the diagnostic."


def _route_action(row: dict, learner_state: dict) -> tuple[str, str]:
    """Let evidence resolve bridge need before falling back to local start hints."""
    state = learner_state["state"]
    scope = row.get("scope")
    delivery = row.get("delivery_state")

    if delivery == capability_delivery.EXTERNAL_BRIDGE:
        provider = row.get("provider") or "declared provider"
        if state == "DEMONSTRATED":
            if scope in {"QUESTION_ONLY", "QUESTION_AND_SYLLABUS"}:
                return (
                    "QUICK_CHECK",
                    f"Already demonstrated; confirm briefly on the worksheet demand before "
                    f"invoking the {provider} bridge.",
                )
            return (
                "SKIP",
                f"Prerequisite is already demonstrated; the {provider} bridge is not needed.",
            )
        if state == "UNCERTAIN":
            return (
                "BRIDGE",
                f"Current learner evidence says UNCERTAIN; use the {provider} bridge to repair.",
            )
        if state == "MISSING":
            return (
                "BRIDGE",
                f"Current learner evidence says MISSING; use the {provider} bridge to teach it.",
            )
        return (
            "BRIDGE",
            f"No learner evidence yet; the {provider} bridge should verify the capability "
            "before teaching more than necessary.",
        )

    if row.get("state") != "RESOLVED":
        return "UNRESOLVED", "Canonical capability delivery is unresolved."

    if state == "MISSING":
        return "TEACH", "Current learner evidence says MISSING."
    if state == "UNCERTAIN":
        return "REPAIR", "Current learner evidence says UNCERTAIN."
    if state == "DEMONSTRATED":
        if scope in {"QUESTION_ONLY", "QUESTION_AND_SYLLABUS"}:
            return "QUICK_CHECK", "Already demonstrated; confirm briefly on the worksheet demand."
        return "SKIP", "Prerequisite is already demonstrated; no study detour is needed."

    estimate = row.get("estimate_basis")
    if estimate:
        action = row.get("learner_action") or "STUDY"
        return (
            action,
            f'Owner estimate {estimate["knowledge_percentage"]}% selected '
            f'{estimate["selected_rung"]}; this is a routing hint, not evidence.',
        )
    return row.get("learner_action") or "STUDY", (
        "No learner evidence or owner estimate is available; follow the canonical route."
    )


def _active_question_families(mapping: dict, required_by: list[str],
                              records: dict) -> list[str]:
    """Resolve worksheet question demand to canonical question-family refs when possible."""
    declared = {row.get("question_id"): row for row in mapping.get("questions", [])}
    families = []
    for question_id in required_by:
        row = declared.get(question_id) or {}
        canonical_ref = row.get("canonical_question_ref") or question_id
        question = records.get(canonical_ref)
        if not question or question.get("_collection") != "questions":
            continue
        family_ref = question.get("family_ref")
        if family_ref and family_ref not in families:
            families.append(family_ref)
    return families


def resolve(mapping: dict, owner_estimates: list[dict] | None = None,
            profile: dict | None = None, repo: Path = REPO) -> dict:
    """Compile a learner-facing question map plus an ordered study route."""
    started = study_start.resolve(mapping, owner_estimates or [], repo, profile=profile)
    subject = mapping.get("subject")
    index = study_map.subject_index(subject, repo)
    resolved_map = study_map.resolve(mapping, repo)
    observations = _observation_lookup(profile, repo)
    canonical_records = build_index(
        load_packages(sorted((repo / subject / "library").glob("*.json")))
    )

    if profile is not None and profile.get("provenance") == "SYNTHETIC_TEST":
        findings = list(started.get("findings", []))
        findings.append({
            "point": "WORKSHEET_STUDY_PLAN_SYNTHETIC_PROFILE_REFUSED",
            "profile_id": profile.get("profile_id"),
            "detail": "a synthetic test profile may not be used for learner routing",
        })
        return {
            "worksheet_id": mapping.get("worksheet_id"),
            "subject": subject,
            "profile_id": profile.get("profile_id"),
            "canonical_matrices": [],
            "questions": [],
            "route": [],
            "start_decisions": started.get("start_decisions", []),
            "findings": findings,
            "warnings": list(started.get("warnings", [])),
            "execution_disposition": started.get("execution_disposition"),
            "blockers": list(started.get("blockers", [])),
            "valid": False,
            "ready": False,
            "passed": False,
        }

    resolved_questions = {
        row["question_id"]: row
        for row in resolved_map.get("questions", [])
    }
    question_rows = []
    for declared in mapping.get("questions", []):
        qid = declared["question_id"]
        mapped = resolved_questions.get(qid, {})
        capability_rows = []
        for cap in mapped.get("capabilities", []):
            capability_ref = cap["capability_ref"]
            state = _profile_state(profile, capability_ref, repo)
            lessons = [_lesson(loc, index) for loc in cap.get("locations", [])]
            capability_rows.append({
                "role": cap.get("role"),
                "capability_ref": capability_ref,
                "action": cap.get("action"),
                "success_criterion": cap.get("success_criterion"),
                "delivery_state": cap.get("delivery_state"),
                "provider": cap.get("provider"),
                "external_provider": cap.get("external_provider") or cap.get("provider"),
                "acceptance_status": cap.get("acceptance_status"),
                "learner_state": state,
                "lessons": lessons,
            })

        primary = next(
            (row for row in capability_rows if row.get("role") == "PRIMARY"),
            capability_rows[0] if capability_rows else None,
        )
        primary_lesson = (
            primary["lessons"][0]["microtopic_title"]
            if primary and primary.get("lessons")
            and primary["lessons"][0].get("microtopic_title")
            else (primary.get("action") if primary else "Unmapped capability")
        )
        primary_difficulty = (
            primary["lessons"][0].get("intrinsic_difficulty")
            if primary and primary.get("lessons")
            else None
        )
        difficulty_source = (
            primary["lessons"][0].get("microtopic_ref")
            if primary and primary.get("lessons")
            else None
        )
        lesson_labels = [
            lesson["label"]
            for cap in capability_rows
            for lesson in cap.get("lessons", [])
        ]
        if (
            not lesson_labels
            and primary
            and primary.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE
        ):
            lesson_labels = [f'External bridge: {primary.get("provider") or "external provider"}']
        question_state, attention = _attention_for(capability_rows, observations)
        question_rows.append({
            "question_id": qid,
            "mapping_state": mapped.get("state"),
            "primary_capability_ref": declared.get("primary_capability_ref"),
            "secondary_capability_refs": list(declared.get("secondary_capability_refs") or []),
            "core_lesson": " + ".join(lesson_labels) if lesson_labels else "UNRESOLVED",
            "what_is_being_learned": primary_lesson,
            "intrinsic_difficulty": primary_difficulty,
            "difficulty_source": difficulty_source,
            "learner_state": question_state,
            "why_extra_attention": attention,
            "capabilities": capability_rows,
        })

    route_rows = []
    routing_by_capability = {}
    for row in started.get("route", []):
        capability_ref = row["capability_ref"]
        state = _profile_state(profile, capability_ref, repo)
        action, reason = _route_action(row, state)
        locations = [_lesson(loc, index) for loc in row.get("locations", [])]
        dependencies = list(row.get("depends_on") or [])
        prerequisites_ready = all(
            routing_by_capability.get(ref, {}).get("routing_posture") == learning_router.READY
            for ref in dependencies
        )
        evidence_history = (
            learner_evidence.evidence_for_capability(profile, capability_ref, repo)
            if profile is not None else []
        )
        active_question_families = _active_question_families(
            mapping, list(row.get("required_by_questions") or []), canonical_records
        )
        routing = learning_router.route_decision(
            state,
            capability_ref=capability_ref,
            microtopic_refs=[
                location["microtopic_ref"]
                for location in locations
                if location.get("microtopic_ref")
            ],
            records=canonical_records,
            prerequisites_ready=prerequisites_ready,
            evidence_history=evidence_history,
            active_question_families=active_question_families,
            repo=repo,
        )
        routing_by_capability[capability_ref] = routing
        route_rows.append({
            **row,
            "learner_state": state,
            "recommended_action": action,
            "action_reason": reason,
            "lessons": locations,
            "routing_posture": routing["routing_posture"],
            "starting_support": routing["starting_support"],
            "initial_visual": routing["initial_visual"],
            "presentation": routing["presentation"],
            "recommended_explorer_ref": routing["recommended_explorer_ref"],
            "exercise_demand": routing["exercise_demand"],
            "exercise_question_ref": routing["exercise_question_ref"],
            "exercise_reason": routing["exercise_reason"],
            "exercise_family_ref": routing.get("exercise_family_ref"),
            "transfer_eligible": routing.get("transfer_eligible", False),
            "transfer_dimension": routing.get("transfer_dimension"),
            "transfer_evidence": routing.get("transfer_evidence", []),
            "routing_findings": routing["routing_findings"],
            "routing_persistence": routing["persistence"],
        })

    relevant_matrix_ids = []
    for question in question_rows:
        for capability in question.get("capabilities", []):
            for lesson in capability.get("lessons", []):
                matrix_id = lesson.get("matrix_id")
                if matrix_id and matrix_id not in relevant_matrix_ids:
                    relevant_matrix_ids.append(matrix_id)
    for row in route_rows:
        for lesson in row.get("lessons", []):
            matrix_id = lesson.get("matrix_id")
            if matrix_id and matrix_id not in relevant_matrix_ids:
                relevant_matrix_ids.append(matrix_id)
    canonical_matrices = _matrix_views(
        subject,
        index,
        relevant_matrix_ids,
        started.get("start_decisions", []),
        repo,
    )

    findings = list(started.get("findings", []))
    warnings = list(started.get("warnings", []))
    blockers = []
    for row in route_rows:
        if row.get("delivery_state") != capability_delivery.EXTERNAL_BRIDGE:
            continue
        if row["learner_state"]["state"] == "DEMONSTRATED":
            continue
        blockers.append({
            "point": "WORKSHEET_STUDY_PLAN_EXTERNAL_BRIDGE_REQUIRED",
            "capability": row["capability_ref"],
            "provider": row.get("provider"),
            "acceptance_status": row.get("acceptance_status"),
            "detail": (
                "learner evidence does not yet satisfy this externally provided capability; "
                "verify or repair it through the declared provider boundary"
            ),
        })
    valid = not findings
    return {
        "worksheet_id": mapping.get("worksheet_id"),
        "subject": subject,
        "profile_id": profile.get("profile_id") if profile else None,
        "canonical_matrices": canonical_matrices,
        "questions": question_rows,
        "route": route_rows,
        "start_decisions": started.get("start_decisions", []),
        "findings": findings,
        "warnings": warnings,
        "execution_disposition": started.get("execution_disposition"),
        "blockers": blockers,
        "valid": valid,
        "ready": valid and not blockers,
        "passed": valid,
        "rules": [
            "Worksheet mappings describe demand; canonical subject records remain academic truth.",
            "Within a matrix, learner-facing order comes from ladder_position; rung identifiers are labels.",
            "Cross-matrix study order comes only from capability prerequisites.",
            "Intrinsic difficulty is read from the canonical microtopic and is not a learner score.",
            "Owner estimates choose a local starting attempt and never create mastery evidence.",
            "Observed learner state overrides owner estimates but never mutates subject content.",
            "External-provider prerequisites remain explicit bridge actions; they are not "
            "misreported as missing local teaching.",
        ],
    }


def _md(value) -> str:
    return str(value if value is not None else "").replace("|", "\\|").replace("\n", " ")


def readable(report: dict) -> str:
    out = [
        f'# Worksheet study plan — {report.get("worksheet_id")}',
        "",
        f'  subject: {report.get("subject")}',
        f'  profile: {report.get("profile_id") or "none"}',
        "",
    ]

    if report.get("start_decisions"):
        out += ["## Rough starting estimates", ""]
        for row in report["start_decisions"]:
            out += [
                f'- **{_md(row.get("subtopic") or row.get("matrix_id"))}: '
                f'{_md(row.get("knowledge_percentage"))}%** — starting-point routing only; '
                f'selected {_md(row.get("selected_rung"))} at position '
                f'{_md(row.get("selected_position"))}. This does not create DEMONSTRATED.'
            ]
        out += [""]

    for matrix in report.get("canonical_matrices", []):
        out += [
            f'## Canonical matrix — {_md(matrix.get("subtopic") or matrix.get("matrix_id"))}',
            "",
        ]
        if matrix.get("family_invariant"):
            out += [
                f'**Family invariant:** {_md(matrix["family_invariant"])}',
                "",
            ]
        out += [
            "Order is the existing ladder_position; rung identifiers are labels, not sequence numbers.",
            "",
            "| Rung | Position | Existing capability | What the learner owns | Difficulty (source) | Prerequisites | Default? |",
            "|---|---:|---|---|---|---|---|",
        ]
        for rung in matrix.get("rungs", []):
            prerequisites = ", ".join(rung.get("prerequisite_refs") or []) or "—"
            difficulty = rung.get("intrinsic_difficulty") or "UNSPECIFIED"
            if rung.get("microtopic_ref"):
                difficulty += f' — {rung["microtopic_ref"]}'
            out.append(
                "| " + " | ".join([
                    _md(rung.get("rung")),
                    _md(rung.get("ladder_position")),
                    _md(rung.get("capability_ref") or "UNRESOLVED"),
                    _md(rung.get("what_the_learner_owns") or "UNRESOLVED"),
                    _md(difficulty),
                    _md(prerequisites),
                    "Yes" if rung.get("default_entry_eligible", True) else "No",
                ]) + " |"
            )
        out += [""]

    out += [
        "## Question -> study map",
        "",
        "| Question | Core lesson | What is being learned | Difficulty (source) | Learner state | Why extra attention? |",
        "|---|---|---|---|---|---|",
    ]
    for row in report.get("questions", []):
        out.append(
            "| " + " | ".join([
                _md(row["question_id"]),
                _md(row["core_lesson"]),
                _md(row["what_is_being_learned"]),
                _md(
                    (row.get("intrinsic_difficulty") or "UNSPECIFIED")
                    + (
                        f' — {row["difficulty_source"]}'
                        if row.get("difficulty_source") else ""
                    )
                ),
                _md(row["learner_state"]),
                _md(row["why_extra_attention"]),
            ]) + " |"
        )

    out += [
        "",
        "## Learner route — Ordered study route",
        "",
        "| # | Action | Capability | Lesson | State | Why |",
        "|---:|---|---|---|---|---|",
    ]
    for row in report.get("route", []):
        lesson = " + ".join(item["label"] for item in row.get("lessons", []))
        if not lesson and row.get("delivery_state") == capability_delivery.EXTERNAL_BRIDGE:
            lesson = f'External bridge: {row.get("provider") or "external provider"}'
        out.append(
            "| " + " | ".join([
                _md(row.get("order")),
                _md(row.get("recommended_action")),
                _md(row.get("capability_ref")),
                _md(lesson or "UNRESOLVED"),
                _md(row.get("learner_state", {}).get("state")),
                _md(row.get("action_reason")),
            ]) + " |"
        )

    if report.get("blockers"):
        out += ["", "## Bridge blockers", ""]
        for blocker in report["blockers"]:
            out.append(
                f'- {_md(blocker.get("point"))}: {_md(blocker.get("capability"))} '
                f'via {_md(blocker.get("provider"))}'
            )

    if report.get("warnings"):
        out += ["", "## Fallback warnings", ""]
        for warning in report["warnings"]:
            out.append(
                f'- {_md(warning.get("point"))}: {_md(warning.get("detail", ""))}'
            )

    if report.get("findings"):
        out += ["", "## Findings", ""]
        for finding in report["findings"]:
            out.append(
                f'- {_md(finding.get("point"))}: {_md(finding.get("detail", ""))}'
            )
    return "\n".join(out)


def _estimates(raw_values: list[str], parser: argparse.ArgumentParser) -> list[dict]:
    rows = []
    for raw in raw_values:
        if "=" not in raw:
            parser.error("--estimate must be MATRIX_ID=PERCENT")
        matrix_id, percentage = raw.split("=", 1)
        try:
            number = float(percentage)
        except ValueError:
            parser.error(f"invalid percentage in --estimate {raw}")
        rows.append({
            "matrix_id": matrix_id,
            "knowledge_percentage": number,
        })
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--map", type=Path, required=True, help="worksheet capability map JSON")
    parser.add_argument("--profile", type=Path, help="optional learner profile JSON")
    parser.add_argument(
        "--estimate",
        action="append",
        default=[],
        metavar="MATRIX_ID=PERCENT",
        help="optional rough owner estimate for one local matrix; may be repeated",
    )
    parser.add_argument("--readable", action="store_true")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    mapping = load(args.map)
    profile = load(args.profile) if args.profile else None
    report = resolve(mapping, _estimates(args.estimate, parser), profile)
    print(readable(report) if args.readable
          else json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
