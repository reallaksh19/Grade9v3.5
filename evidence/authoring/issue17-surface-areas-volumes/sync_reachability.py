#!/usr/bin/env python3
"""Reconcile the Issue #17 QRT graph with the actual Core2 learner surface.

The exact-render audit showed that difficulty/trap panels are pre-attempt resources and that
Core1A navigation must be post-attempt because the linked construction page can expose protected
question work.  This projection keeps the machine graph aligned with the rendered product.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

CONDITION_QUESTIONS = {"Q3", "Q4", "Q6", "Q7", "Q8", "Q9", "Q10"}


def graph_for(question: dict) -> dict:
    qid = question["id"]
    protected = question["slots"]["W"]["protected_move_ref"]
    root_id = f"{qid}-ROOT"
    links: list[str] = []
    nodes: list[dict] = [{
        "id": root_id,
        "phase": "PRE_ATTEMPT",
        "resource_kind": "QUESTION",
        "move_refs": [],
        "links": links,
    }]

    def pre(suffix: str, kind: str) -> None:
        nid = f"{qid}-{suffix}"
        links.append(nid)
        nodes.append({"id": nid, "phase": "PRE_ATTEMPT", "resource_kind": kind, "move_refs": [], "links": []})

    pre("DIFFICULTY", "DIFFICULTY_PANEL")
    if qid in CONDITION_QUESTIONS:
        pre("CONDITIONS", "CONDITIONS")
    pre("TRAP", "TRAP_PANEL")
    for hint in question.get("hints") or []:
        nid = hint["id"]
        links.append(nid)
        nodes.append({"id": nid, "phase": "PRE_ATTEMPT", "resource_kind": "HINT", "move_refs": [], "links": []})
    if (question.get("representation") or {}).get("applicability") != "NOT_APPLICABLE":
        pre("REP", "REPRESENTATION")

    post_solution = f"{qid}-POST-SOLUTION"
    post_core1a = f"{qid}-POST-CORE1A"
    links.append(post_solution)
    nodes.append({
        "id": post_solution,
        "phase": "POST_ATTEMPT",
        "resource_kind": "SOLUTION",
        "move_refs": [protected],
        "links": [post_core1a],
    })
    nodes.append({
        "id": post_core1a,
        "phase": "POST_ATTEMPT",
        "resource_kind": "CORE1A_LINK",
        "move_refs": [],
        "links": [],
    })
    return {"question_ref": qid, "root": root_id, "nodes": nodes}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run", type=Path)
    args = parser.parse_args()
    data = json.loads(args.run.read_text(encoding="utf-8"))
    data["pre_attempt_graphs"] = [graph_for(q) for q in data.get("questions") or []]
    args.run.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"reachability: reconciled {len(data['pre_attempt_graphs'])} question graph(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
