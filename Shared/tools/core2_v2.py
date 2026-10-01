"""Typed Core2-v2 learner projections.

Core2 keeps source hints (question.hints) and authored pedagogy
(question.scaffolds) distinct. This module orders both support lanes without
changing their provenance, marks answer-revealing rows as unavailable before
the solution stage, projects structured reasoning moves into learner-facing
solution stages without inventing or collapsing authored intermediate steps,
and derives the Core1A↔Core2 concept/question join from canonical capability
references rather than persisted reciprocal link lists.
"""
from __future__ import annotations

import re

SOURCE_HINT = "SOURCE_HINT"
AUTHORED_CORE2_SUPPORT = "AUTHORED_CORE2_PROMPT_REVEAL"
LEARNER_STAGES = {"KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "CRUX", "FORMAL_MODEL", "CHECKPOINT", "OTHER"}
_REVEAL_ORDER = {"CONCEPT": 0, "METHOD": 1, "ANSWER": 2}
_REF = re.compile(r"^(hints|scaffolds)\[(\d+)\]$")

# The Core2-v2 amendment names these as the preferred learner progression.
# Existing canonical reasoning_move.kind remains the authoring authority; this
# mapping is structural and never infers a stage from prose.
SOLUTION_STAGE_BY_KIND = {
    "DECIDE": "UNDERSTAND",
    "REPRESENT": "REPRESENT",
    "CONNECT": "CONNECT",
    "TRANSFORM": "CALCULATE",
    "VERIFY": "INTERPRET",
}
SOLUTION_STAGES = tuple(dict.fromkeys(SOLUTION_STAGE_BY_KIND.values()))


class Core2SupportProjectionError(ValueError):
    pass


class Core2SolutionProjectionError(ValueError):
    pass


class Core2ConceptJoinError(ValueError):
    pass


def _rows(question: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i, hint in enumerate(question.get("hints") or []):
        if isinstance(hint, str) and hint.strip():
            # The competitive-exam bank stores a source hint as bare text; a package stores
            # {text, reveals}. Both are the same lane, and a bare hint declares no reveal depth.
            hint = {"text": hint}
        if not isinstance(hint, dict) or not hint.get("text"):
            raise Core2SupportProjectionError(f"hints[{i}] is not a typed hint")
        ref = f"hints[{i}]"
        out[ref] = {
            "source": ref,
            "provenance": SOURCE_HINT,
            "text": hint["text"],
            "prompt": None,
            "learner_stage": None,
            "support_kind": None,
            "reveals": hint.get("reveals", "METHOD"),
            "supports_move_ref": None,
            "visual_ref": hint.get("visual_ref"),
            "visual_stage_ref": hint.get("visual_stage_ref"),
        }
    for i, scaffold in enumerate(question.get("scaffolds") or []):
        if not isinstance(scaffold, dict) or not scaffold.get("text"):
            raise Core2SupportProjectionError(f"scaffolds[{i}] is not a typed scaffold")
        stage = scaffold.get("learner_stage")
        if stage is not None and stage not in LEARNER_STAGES:
            raise Core2SupportProjectionError(f"invalid learner stage {stage!r}")
        ref = f"scaffolds[{i}]"
        out[ref] = {
            "source": ref,
            "provenance": AUTHORED_CORE2_SUPPORT,
            "text": scaffold["text"],
            "prompt": scaffold.get("prompt"),
            "learner_stage": stage,
            "support_kind": scaffold.get("support_kind"),
            "reveals": scaffold.get("reveals", "METHOD"),
            "supports_move_ref": scaffold.get("supports_move_ref"),
            "visual_ref": scaffold.get("visual_ref"),
            "visual_stage_ref": scaffold.get("visual_stage_ref"),
        }
    return out


_INLINE_PROVENANCE = {
    "SOURCE_HINT": SOURCE_HINT,
    "AUTHORED_HINT": AUTHORED_CORE2_SUPPORT,
    "AUTHORED_SCAFFOLD": AUTHORED_CORE2_SUPPORT,
}
_INLINE_REVEALS = {"ORIENT": "CONCEPT", "ANSWER": "ANSWER"}


def _inline_rows(question: dict) -> dict[str, dict]:
    """Ladder rungs that carry their own text (`hint_rung` allows `text` instead of `from`).

    Provenance is read from the rung's declared `provenance`, never inferred from the text.
    """
    out: dict[str, dict] = {}
    for i, rung in enumerate(question.get("hint_ladder") or []):
        if not isinstance(rung, dict) or rung.get("from") or not rung.get("text"):
            continue
        provenance = _INLINE_PROVENANCE.get(rung.get("provenance"))
        if provenance is None:
            raise Core2SupportProjectionError(
                f"hint_ladder[{i}] has inline text but no declared provenance")
        ref = f"hint_ladder[{i}]"
        out[ref] = {
            "source": ref,
            "provenance": provenance,
            "text": rung["text"],
            "prompt": None,
            "learner_stage": None,
            "support_kind": None,
            "reveals": _INLINE_REVEALS.get(rung.get("purpose"), "METHOD"),
            "supports_move_ref": rung.get("supports_move_ref"),
            "visual_ref": None,
            "visual_stage_ref": rung.get("visual_stage_ref"),
        }
    return out


def _fallback_order(rows: dict[str, dict]) -> list[str]:
    keyed = []
    for ref, row in rows.items():
        if not _REF.match(ref):
            continue  # inline rungs are reached only through the ladder that carries them
        lane, index = _REF.match(ref).groups()
        keyed.append((_REVEAL_ORDER.get(row["reveals"], 1), 0 if lane == "hints" else 1, int(index), ref))
    return [entry[3] for entry in sorted(keyed)]


def _order(question: dict, rows: dict[str, dict]) -> list[str]:
    ladder = question.get("hint_ladder") or []
    if not ladder:
        return _fallback_order(rows)
    ordered, seen = [], set()
    positions = {id(rung): position for position, rung in enumerate(ladder)}
    for rung in sorted(ladder, key=lambda value: value.get("order", 0)):
        ref = rung.get("from") or (f"hint_ladder[{positions[id(rung)]}]" if rung.get("text") else None)
        if not ref or ref not in rows or ref in seen:
            raise Core2SupportProjectionError(f"invalid hint_ladder reference {ref!r}")
        ordered.append(ref)
        seen.add(ref)
    ordered.extend(ref for ref in _fallback_order(rows) if ref not in seen)
    return ordered


def project_support(question: dict) -> list[dict]:
    rows = _rows(question)
    rows.update(_inline_rows(question))
    projected = []
    for order, ref in enumerate(_order(question, rows), 1):
        row = dict(rows[ref])
        row["order"] = order
        row["eligible_pre_solution"] = row["reveals"] != "ANSWER"
        projected.append(row)
    return projected


def pre_solution_support(question: dict) -> list[dict]:
    return [row for row in project_support(question) if row["eligible_pre_solution"]]


def split_pre_solution_support(question: dict) -> tuple[list[dict], list[dict]]:
    rows = pre_solution_support(question)
    return (
        [row for row in rows if row["provenance"] == SOURCE_HINT],
        [row for row in rows if row["provenance"] == AUTHORED_CORE2_SUPPORT],
    )


def project_solution(answer: dict) -> list[dict]:
    """Project canonical reasoning moves into Core2 learner solution stages.

    One output row is retained for every authored reasoning move. The preferred
    UNDERSTAND → REPRESENT → CONNECT → CALCULATE → INTERPRET vocabulary is a
    rendering classification, not a quota: missing stages are not fabricated and
    repeated stages remain repeated when the authored reasoning needs them.

    An empty list means the record has only legacy ``reasoning[]`` and the
    renderer must use that as the backward-compatible fallback.
    """
    route = answer.get("reasoning_route") or []
    if not route:
        return []
    crux_ref = answer.get("crux_move_ref")
    ids: set[str] = set()
    projected: list[dict] = []
    for index, move in enumerate(route, 1):
        if not isinstance(move, dict) or not move.get("id"):
            raise Core2SolutionProjectionError(f"reasoning_route[{index - 1}] is not a typed reasoning move")
        move_id = move["id"]
        if move_id in ids:
            raise Core2SolutionProjectionError(f"duplicate reasoning move id {move_id!r}")
        ids.add(move_id)
        kind = move.get("kind")
        stage = SOLUTION_STAGE_BY_KIND.get(kind)
        if stage is None:
            raise Core2SolutionProjectionError(f"reasoning move {move_id!r} has unsupported kind {kind!r}")
        for required in ("action", "why_valid", "output"):
            if not move.get(required):
                raise Core2SolutionProjectionError(f"reasoning move {move_id!r} is missing {required}")
        projected.append({
            "order": index,
            "move_id": move_id,
            "kind": kind,
            "stage": stage,
            "action": move["action"],
            "why_valid": move["why_valid"],
            "inputs": list(move.get("inputs") or []),
            "output": move["output"],
            "representation_ref": move.get("representation_ref"),
            "visual_stage_ref": move.get("visual_stage_ref"),
            "source_ref": move.get("source_ref"),
            "is_crux": move_id == crux_ref,
        })
    if crux_ref and crux_ref not in ids:
        raise Core2SolutionProjectionError(f"crux_move_ref {crux_ref!r} does not resolve inside reasoning_route")
    return projected


def concept_question_join(microtopics: list[dict], questions: list[dict]) -> dict[str, dict[str, list[str]]]:
    """Derive the selected Core1A↔Core2 join from canonical capability refs.

    A selected Core1A microtopic owns its ``primary_capability_ref``. Selected
    Core2 questions point to that same authority through their primary and
    secondary capability refs. Both directions are generated in memory from
    those records; no reciprocal academic/link list is persisted.
    """
    owner_by_capability: dict[str, str] = {}
    microtopic_to_questions: dict[str, list[str]] = {}
    for index, microtopic in enumerate(microtopics):
        if not isinstance(microtopic, dict) or not microtopic.get("id"):
            raise Core2ConceptJoinError(f"microtopics[{index}] has no id")
        microtopic_id = microtopic["id"]
        capability = microtopic.get("primary_capability_ref")
        if not capability:
            raise Core2ConceptJoinError(f"microtopic {microtopic_id!r} has no primary_capability_ref")
        previous = owner_by_capability.get(capability)
        if previous and previous != microtopic_id:
            raise Core2ConceptJoinError(
                f"selected capability {capability!r} is owned by both {previous!r} and {microtopic_id!r}"
            )
        owner_by_capability[capability] = microtopic_id
        microtopic_to_questions.setdefault(microtopic_id, [])

    question_to_microtopics: dict[str, list[str]] = {}
    seen_questions: set[str] = set()
    for index, question in enumerate(questions):
        if not isinstance(question, dict) or not question.get("id"):
            raise Core2ConceptJoinError(f"questions[{index}] has no id")
        question_id = question["id"]
        if question_id in seen_questions:
            raise Core2ConceptJoinError(f"duplicate selected Core2 question id {question_id!r}")
        seen_questions.add(question_id)

        refs = [question.get("primary_capability_ref"), *(question.get("secondary_capability_refs") or [])]
        matched: list[str] = []
        seen_refs: set[str] = set()
        for capability in refs:
            if not capability or capability in seen_refs:
                continue
            seen_refs.add(capability)
            microtopic_id = owner_by_capability.get(capability)
            if microtopic_id and microtopic_id not in matched:
                matched.append(microtopic_id)
                microtopic_to_questions[microtopic_id].append(question_id)
        question_to_microtopics[question_id] = matched

    return {
        "question_to_microtopics": question_to_microtopics,
        "microtopic_to_questions": microtopic_to_questions,
    }
