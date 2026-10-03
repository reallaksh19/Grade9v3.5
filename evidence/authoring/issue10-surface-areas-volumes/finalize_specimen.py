#!/usr/bin/env python3
"""Add contract-required derived metadata to the generated Issue #10 specimen.

The cold-run keeps the owner stems immutable. This finalizer only projects
agent-owned audit evidence into the generated owner-bank metadata.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
GENERATED = HERE / "generated"

qrt = json.loads((HERE / "qrt-review.v1.json").read_text(encoding="utf-8"))
bank_path = GENERATED / "owner.bank.json"
bank = json.loads(bank_path.read_text(encoding="utf-8"))
by_qid = {row["question_id"]: row for row in qrt["items"]}

for question in bank["questions"]:
    qid = question["original_identifier"]
    review = by_qid[qid]
    analysis = question.setdefault("extensions", {}).setdefault("grade9v3:analysis", {})
    difficulty = analysis.setdefault("difficulty", {})
    difficulty["basis"] = (
        f"{review['X']} The decisive learner move is: {review['Z']} "
        f"Repository five-component evidence totals {review['difficulty']['score']}, "
        f"which resolves to {review['difficulty']['band']}."
    )

bank_path.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("finalized owner-bank difficulty basis")
