#!/usr/bin/env python3
"""The toughest concept in a question set: the one a concept book and an interactive page must be built for.

A Core1A page that names the hard concept and teaches only the easy ones, or an interactive page that plays with the
easiest relation in the set, is a page built for the page's sake. The page's job is the question a learner is most
likely to fail, and the idea that question turns on. This module says which that is, from the records alone, so that the
author, the renderer and the checks all point at the same question.

The rule (written once here, quoted wherever it is applied):

    the question whose difficulty is most *conceptual* (concept_model_selection + trap_exception_sensitivity, each 0 to 2),
    then the higher total score, then the heavier representation_translation, then the longer reasoning chain,
    then the one that comes first in the bank.

Conceptual difficulty comes first on purpose: a question that is hard because of its algebra is practice, not a concept.
The estimates are the author's (the owner bank records each question's five components and says they are an estimate), so
the Owner can overrule the choice by changing them; nothing here guesses.

    python3 Shared/tools/toughest_concept.py TEST/products/SLUG.manifest.json [--json]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import core2_v2  # noqa: E402

ANALYSIS_KEY = "grade9v3:analysis"
CONCEPTUAL_PARTS = ("concept_model_selection", "trap_exception_sensitivity")
BAND_ORDER = {"D1": 1, "D2": 2, "D3": 3, "D4": 4}
RULE = ("the question whose difficulty is most conceptual (concept_model_selection + trap_exception_sensitivity), then the higher "
        "total score, then representation_translation, then reasoning_chain_length, then the first in the bank")


def _difficulty(question: dict) -> dict | None:
    analysis = (question.get("extensions") or {}).get(ANALYSIS_KEY) or {}
    difficulty = analysis.get("difficulty")
    if not isinstance(difficulty, dict) or not isinstance(difficulty.get("components"), dict):
        return None
    if not isinstance(difficulty.get("score"), int) or difficulty.get("band") not in BAND_ORDER:
        return None
    return difficulty


def rank(question: dict) -> tuple[int, int, int, int] | None:
    """The sort key, larger is tougher; None when the question carries no complete difficulty estimate."""
    difficulty = _difficulty(question)
    if difficulty is None:
        return None
    parts = difficulty["components"]
    count = lambda name: parts.get(name) if isinstance(parts.get(name), int) else 0  # noqa: E731
    return (sum(count(name) for name in CONCEPTUAL_PARTS), difficulty["score"],
            count("representation_translation"), count("reasoning_chain_length"))


def crux_move(question: dict) -> dict | None:
    """The move the question's author says a learner is most likely to miss."""
    answer = question.get("answer") if isinstance(question.get("answer"), dict) else {}
    for move in answer.get("reasoning_route") or []:
        if isinstance(move, dict) and move.get("id") == answer.get("crux_move_ref"):
            return {key: move.get(key) for key in ("id", "kind", "action", "why_valid", "output")}
    return None


def label_of(question: dict) -> str:
    """The Owner's own number for the question where there is one (Q8), else its id."""
    return str(question.get("original_identifier") or question.get("id") or "")


def derive(questions: list[dict], microtopics: list[dict]) -> dict[str, Any] | None:
    """The brief for the toughest question of `questions` (selected bank records) against the package's `microtopics`.

    None when no question carries a complete difficulty estimate: nothing is chosen on a guess."""
    ranked = [(rank(question), -index, question) for index, question in enumerate(questions) if isinstance(question, dict)]
    ranked = [row for row in ranked if row[0] is not None]
    if not ranked:
        return None
    ranked.sort(key=lambda row: (row[0], row[1]), reverse=True)
    key, _, question = ranked[0]
    difficulty = _difficulty(question)
    try:
        join = core2_v2.concept_question_join(microtopics, questions)
    except core2_v2.Core2ConceptJoinError:
        join = {"question_to_microtopics": {}}
    owners = join["question_to_microtopics"].get(question["id"]) or []
    owner = next((m for m in microtopics if m.get("id") == (owners[0] if owners else None)), None)
    analysis = (question.get("extensions") or {}).get(ANALYSIS_KEY) or {}
    runner_up = ranked[1][2] if len(ranked) > 1 else None
    return {
        "rule": RULE,
        "question_ref": question["id"],
        "label": label_of(question),
        "stem": question.get("stem") or "",
        "band": difficulty["band"],
        "score": difficulty["score"],
        "conceptual": key[0],
        "components": dict(difficulty["components"]),
        "capability_ref": question.get("primary_capability_ref"),
        "microtopic_ref": owner["id"] if owner else None,
        "microtopic_title": (owner or {}).get("title"),
        "relation_refs": list((owner or {}).get("relation_refs") or []),
        "crux_move": crux_move(question),
        "wrong_route": analysis.get("common_wrong_route") or None,
        "related_question_refs": [row[2]["id"] for row in ranked[1:]
                                  if row[2].get("primary_capability_ref") == question.get("primary_capability_ref")],
        "runner_up": ({"question_ref": runner_up["id"], "label": label_of(runner_up), "conceptual": ranked[1][0][0],
                       "score": ranked[1][0][1]} if runner_up else None),
    }


def crux_band(unit: dict, questions: list[dict]) -> str | None:
    """The hardest band among the questions whose crux a construction unit says it builds; None when it builds none."""
    wanted = set(unit.get("crux_question_refs") or [])
    bands = [(_difficulty(question) or {}).get("band") for question in questions if question.get("id") in wanted]
    bands = [band for band in bands if band in BAND_ORDER]
    return max(bands, key=BAND_ORDER.get) if bands else None


def describe(brief: dict | None) -> list[str]:
    """What the author and the Owner are told: which question, why, and what it turns on."""
    if not brief:
        return ["toughest concept: not chosen (no question carries a complete difficulty estimate)"]
    lines = [f"toughest concept: {brief['label']} ({brief['question_ref']}), {brief['band']}, {brief['score']}/10, "
             f"{brief['conceptual']}/4 conceptual"
             + (f"; the concept is {brief['microtopic_title']} ({brief['microtopic_ref']})" if brief.get("microtopic_ref")
                else "; no microtopic of the package owns its capability")]
    if brief.get("crux_move"):
        move = brief["crux_move"]
        lines.append(f"  the move a learner misses: {move.get('action')} ({move.get('id')})")
    if brief.get("wrong_route"):
        lines.append(f"  the tempting wrong route: {brief['wrong_route']}")
    lines.append(f"  chosen by: {brief['rule']}")
    return lines


def for_manifest(manifest_path: Path) -> dict[str, Any] | None:
    from Shared.tools import render_core  # noqa: PLC0415  (render_core imports this module)
    ctx = render_core.context(Path(manifest_path))
    return derive(ctx.selection_rows.get("core2", []), ctx.selection_rows.get("microtopics", []))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("manifest", help="a product manifest (TEST/products/SLUG.manifest.json)")
    parser.add_argument("--json", action="store_true", help="print the brief as JSON")
    args = parser.parse_args(argv)
    brief = for_manifest(Path(args.manifest))
    print(json.dumps(brief, indent=2, ensure_ascii=False) if args.json else "\n".join(describe(brief)))
    return 0 if brief else 1


if __name__ == "__main__":
    raise SystemExit(main())
