#!/usr/bin/env python3
"""Compile a bank + learner profile into deterministic QRT pedagogy records.

This stage sits before rendering. It does not write HTML and does not make post-render
YES/PARTLY/NO judgements.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from Shared.tools import question_review_matrix as qrt

REPO = Path(__file__).resolve().parents[2]


class BatchAuthoringError(ValueError):
    pass


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise BatchAuthoringError(f"{path}: expected object")
    return value


def compile_batch(
    bank: dict[str, Any],
    profile: dict[str, Any],
    subject: str,
    authority_record: str,
) -> dict[str, Any]:
    if subject not in ("Physics", "Chemistry", "Mathematics"):
        raise BatchAuthoringError(f"unsupported subject: {subject}")
    questions = bank.get("questions") or []
    if not questions:
        raise BatchAuthoringError("bank has no questions")

    matrix = qrt.load(qrt.MATRIX_PATH)
    vocab = qrt.load(qrt.VOCAB_PATH)
    adapter = qrt.load(REPO / subject / "adapter" / "DemandReview.json")

    items = []
    unresolved_y = False
    for question in questions:
        resolution = qrt.specialize_resolution(
            qrt.resolve_review(question, profile, matrix, vocab),
            adapter,
        )
        demand = resolution["classification"]["demand"]
        analysis = ((question.get("extensions") or {}).get("grade9v3:analysis") or {})
        slots = {}
        for key in ("X", "Y", "Z", "W"):
            row = resolution["slots"][key]
            unresolved = key == "Y" and row["text"].startswith("UNRESOLVED:")
            unresolved_y = unresolved_y or unresolved
            slots[key] = {
                "text": row["text"],
                "basis": list(row.get("basis") or []),
                "state": "UNRESOLVED_OWNER_INPUT" if unresolved else "RESOLVED",
            }

        guidance = resolution["subject_adapter"]["guidance"]
        rep_kinds = ", ".join(guidance.get("representation_kinds") or []) or "none specified"
        check_types = ", ".join(guidance.get("check_types") or []) or "none specified"
        items.append({
            "question_ref": question["id"],
            "template_id": resolution["template_id"],
            "classification": {
                "primary_demand": demand["primary"],
                "band": resolution["classification"]["band"],
                "basis": demand["basis"],
            },
            "slots": slots,
            "authoring": {
                "hint_objectives": [
                    resolution["review"]["H1"]["objective"],
                    resolution["review"]["H2"]["objective"],
                    resolution["review"]["H3"]["objective"],
                ],
                "figure_policy": (
                    f"{guidance['review_focus']} Candidate representation kinds: {rep_kinds}. "
                    "Any pre-attempt visual must preserve W; a correctly-not-applicable visual needs a reason."
                ),
                "misconception_model": str(analysis.get("common_wrong_route") or ""),
                "solution_architecture": [
                    move["id"] for move in ((question.get("answer") or {}).get("reasoning_route") or [])
                    if isinstance(move, dict) and move.get("id")
                ],
            },
        })

    return {
        "schema": "question-pedagogy-batch/v1",
        "product_id": bank.get("product_id") or "PRODUCT-MAT-G9-SAV",
        "authority_record": authority_record,
        "profile_ref": str(profile.get("profile_id") or ""),
        "matrix_ref": qrt.MATRIX_PATH.relative_to(REPO).as_posix(),
        "status": "PENDING_OWNER_PROFILE" if unresolved_y else "READY_FOR_RENDER",
        "items": items,
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--bank", type=Path, required=True)
    parser.add_argument("--profile", type=Path, required=True)
    parser.add_argument("--subject", required=True)
    parser.add_argument("--authority-record", required=True)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args(argv)
    result = compile_batch(
        load(args.bank),
        load(args.profile),
        args.subject,
        args.authority_record,
    )
    payload = json.dumps(result, indent=2, ensure_ascii=False) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
