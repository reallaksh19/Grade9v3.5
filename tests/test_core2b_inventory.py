"""Core2B transfer inventory and forward-only integrity gate falsifiers."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import core2b_inventory


def move(mid: str, kind: str) -> dict:
    return {
        "id": mid,
        "kind": kind,
        "action": "Choose the applicable relation.",
        "why_valid": "The stated condition determines whether the relation applies.",
        "inputs": ["condition"],
        "output": "selected relation",
    }


def parent_question() -> dict:
    return {
        "id": "Q-A",
        "status": "CANDIDATE",
        "stem": "Use the familiar relation.",
        "subparts": [], "options": [], "conditions": [], "figure_refs": [],
        "primary_capability_ref": "CAP-A",
        "secondary_capability_refs": [],
        "family_ref": "FAM-A",
        "hints": [],
        "scaffolds": [],
        "exposure": [{"core": "CORE2A", "role": "PRACTICE", "artifact_ref": None}],
        "answer": {
            "kind": "MODEL_RESPONSE",
            "summary": "Familiar solution.",
            "reasoning": ["Use the relation."],
            "check": "Substitute into the original condition.",
            "subpart_answers": [],
            "rubric": [],
        },
        "adaptation": None,
        "repair_ref": "STEP-A",
    }


def transfer_question(*, protected=True, rubric=True, repair="STEP-A",
                      add_capability=False, parent_in_lineage=True) -> dict:
    route = [move("M-DECIDE", "DECIDE")] if protected else []
    answer = {
        "kind": "MODEL_RESPONSE",
        "summary": "Transfer solution.",
        "reasoning": ["Decide whether the familiar relation applies."],
        "reasoning_route": route,
        "crux_move_ref": "M-DECIDE" if protected else None,
        "check": "Substitute into the original condition.",
        "subpart_answers": [],
        "rubric": (
            [{"criterion": "Selects the relation conditionally.",
              "evidence_of": "Explains why the condition permits the model."}]
            if rubric else []
        ),
    }
    if not protected:
        answer.pop("reasoning_route")
        answer.pop("crux_move_ref")
    return {
        "id": "Q-B",
        "status": "CANDIDATE",
        "stem": "Decide whether the familiar relation still applies.",
        "subparts": [], "options": [], "conditions": [], "figure_refs": [],
        "primary_capability_ref": "CAP-A",
        "secondary_capability_refs": ["CAP-B"] if add_capability else [],
        "family_ref": "FAM-A",
        "hints": [{"text": "Inspect the condition.", "reveals": "CONCEPT"}],
        "scaffolds": [],
        "exposure": [{"core": "CORE2B", "role": "NEW_TRANSFER", "artifact_ref": None}],
        "answer": answer,
        "transfer": {
            "dimension": "model_choice",
            "statement": "The learner must decide whether the familiar relation applies.",
            "builds_on": ["Q-A"] if parent_in_lineage else ["MIC-A"],
            "protected_move_ref": "M-DECIDE" if protected else None,
        },
        "adaptation": {
            "parent_ref": "Q-A",
            "changed_fields": ["stem", "answer"],
            "reason": "Changes from told relation to model choice.",
        },
        "repair_ref": repair,
    }


def write_repo(root: Path, transfer: dict) -> None:
    (root / "Example/adapter").mkdir(parents=True, exist_ok=True)
    (root / "Example/library").mkdir(parents=True, exist_ok=True)
    (root / "Example/adapter/CoreContracts.json").write_text("{}\n", encoding="utf-8")
    package = {
        "package_id": "PKG",
        "capabilities": [
            {"id": "CAP-A", "prerequisite_refs": []},
            {"id": "CAP-B", "prerequisite_refs": []},
        ],
        "microtopics": [{
            "id": "MIC-A",
            "primary_capability_ref": "CAP-A",
            "teaching_path": [{
                "id": "STEP-A", "action": "Teach A.", "why_valid": "A is established.",
                "inputs": [], "output": "A",
            }],
        }],
        "questions": [parent_question(), transfer],
    }
    (root / "Example/library/p.json").write_text(
        json.dumps(package, indent=2) + "\n", encoding="utf-8"
    )


class Core2BInventory(unittest.TestCase):
    def test_current_tree_is_nonvacuous_and_exposes_legacy_protection_debt(self):
        report = core2b_inventory.inventory()
        self.assertGreater(report["summary"]["core2b_questions"], 0)
        self.assertGreater(report["summary"]["debt_items"], 0)
        self.assertGreater(report["summary"]["structured_protected"], 0)

    def test_mature_transfer_has_no_machine_checkable_debt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question())
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertEqual(row["protection_state"], "STRUCTURED_PROTECTED")
        self.assertTrue(row["anchor_is_core2a"])
        self.assertEqual(row["missing_capabilities"], [])
        self.assertEqual(row["repair_state"], "SPECIFIC_TEACHING_STEP")
        self.assertEqual(row["debt_reasons"], [])

    def test_unprotected_transfer_is_named_as_migration_debt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(protected=False))
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertIn("PROTECTED_DECISION_MIGRATION_REQUIRED", row["debt_reasons"])

    def test_parent_must_be_in_lineage(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(parent_in_lineage=False))
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertIn("ADAPTATION_PARENT_NOT_IN_LINEAGE", row["debt_reasons"])

    def test_new_capability_is_not_silently_called_transfer(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(add_capability=True))
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertIn("CAP-B", row["missing_capabilities"])
        self.assertIn("TRANSFER_REQUIRES_UNESTABLISHED_CAPABILITY", row["debt_reasons"])

    def test_repair_must_point_to_specific_teaching_step(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(repair="MIC-A"))
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertIn("REPAIR_NOT_SPECIFIC_TEACHING_STEP", row["debt_reasons"])

    def test_rubric_is_forward_transfer_closure(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(rubric=False))
            row = core2b_inventory.inventory(root)["rows"][0]
        self.assertIn("TRANSFER_RUBRIC_INCOMPLETE", row["debt_reasons"])

    def test_unchanged_legacy_debt_is_allowed_but_new_debt_is_not(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, transfer_question(protected=False))
            report = core2b_inventory.inventory(root)
            baseline = core2b_inventory.baseline_document(report)
            self.assertEqual(core2b_inventory.forward_findings(report, baseline), [])

            q = transfer_question(protected=False)
            q["id"] = "Q-C"
            q["adaptation"]["parent_ref"] = "Q-A"
            write_repo(root, q)
            points = [
                row["point"]
                for row in core2b_inventory.forward_findings(
                    core2b_inventory.inventory(root), baseline
                )
            ]
        self.assertIn("CORE2B_NEW_TRANSFER_DEBT", points)


if __name__ == "__main__":
    unittest.main()
