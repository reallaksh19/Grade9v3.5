#!/usr/bin/env python3
"""Add contract-required derived metadata to the generated Issue #18 specimen.

The cold-run keeps the owner stems immutable. This finalizer projects
agent-owned audit evidence into generated metadata, applies explicit semantic
component waivers, and normalizes authored teaching/derivation step semantics
into the canonical package vocabulary.
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
    waivers = microtopic.setdefault("extensions", {}).setdefault("grade9v3:component_waivers", {})
    if microtopic.get("id") == "MIC-MAT-SAV-VOLUME-STRUCTURE":
        waivers["STAGED_VISUAL"] = (
            "The decisive construction is symbolic/contextual: distinguish capacity, conserved volume and a shared "
            "formula factor. A decorative solid drawing adds no semantic bridge for this competition learner."
        )
    if microtopic.get("id") == "MIC-MAT-SAV-SURFACE-INVENTORY":
        waivers["EQUATIONS"] = (
            "The hidden-joint construction is a physical exposure decision; its useful bridge is the staged joint "
            "diagram and touch/paint test, not another equation card."
        )
for relation in package.get("relations", []):
    for derivation_step in relation.get("derivation", []):
        derivation_step["role"] = role_map.get(derivation_step.get("role"), derivation_step.get("role"))

package_path.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("normalized package teaching/derivation-step roles and semantic waivers")

manifest_path = GENERATED / "product.manifest.json"
manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
manifest["output_roles"] = ["CORE1A", "CORE2"]
manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("scoped rendered product to Issue #18 deliverables: CORE1A + CORE2")
