"""Typed Core2-v2 learner projections.

Core2 keeps source hints (question.hints) and authored pedagogy
(question.scaffolds) distinct. This module orders both support lanes without
changing their provenance, marks answer-revealing rows as unavailable before
the solution stage, and projects structured reasoning moves into learner-facing
solution stages without inventing or collapsing authored intermediate steps.
"""
from __future__ import annotations

import re

SOURCE_HINT = "SOURCE_HINT"
AUTHORED_CORE2_SUPPORT = "AUTHORED_CORE2_PROMPT_REVEAL"
LEARNER_STAGES = {"KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "OTHER"}
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


def _rows(question: dict) -> dict[str, dict]:
    out: dict[str, dict] = {}
    for i, hint in enumerate(question.get("hints") or []):
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


def _fallback_order(rows: dict[str, dict]) -> list[str]:
    keyed = []
    for ref, row in rows.items():
        lane, index = _REF.match(ref).groups()
        keyed.append((_REVEAL_ORDER.get(row["reveals"], 1), 0 if lane == "hints" else 1, int(index), ref))
    return [entry[3] for entry in sorted(keyed)]


def _order(question: dict, rows: dict[str, dict]) -> list[str]:
    ladder = question.get("hint_ladder") or []
    if not ladder:
        return _fallback_order(rows)
    ordered, seen = [], set()
    for rung in sorted(ladder, key=lambda value: value.get("order", 0)):
        ref = rung.get("from")
        if not ref or not _REF.match(ref) or ref not in rows or ref in seen:
            raise Core2SupportProjectionError(f"invalid hint_ladder reference {ref!r}")
        ordered.append(ref)
        seen.add(ref)
    ordered.extend(ref for ref in _fallback_order(rows) if ref not in seen)
    return ordered


def project_support(question: dict) -> list[dict]:
    rows = _rows(question)
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
