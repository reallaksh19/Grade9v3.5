#!/usr/bin/env python3
"""Add contract-required derived metadata to the generated Issue #10 specimen.

The cold-run keeps the owner stems immutable. This finalizer only projects
agent-owned audit evidence into generated metadata and normalizes authored
teaching/derivation step semantics into the canonical package vocabulary.
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

package_path = GENERATED / "package.v1.json"
package = json.loads(package_path.read_text(encoding="utf-8"))
role_map = {
    "DECIDE": "DECLARE",
    "REPRESENT": "TRANSFORM",
}
for microtopic in package.get("microtopics", []):
    for teaching_step in microtopic.get("teaching_path", []):
        teaching_step["role"] = role_map.get(teaching_step.get("role"), teaching_step.get("role"))
for relation in package.get("relations", []):
    for derivation_step in relation.get("derivation", []):
        derivation_step["role"] = role_map.get(derivation_step.get("role"), derivation_step.get("role"))

package_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("normalized package teaching/derivation-step roles")
