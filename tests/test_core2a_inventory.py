"""Core2A reasoning-migration inventory and forward-only gate falsifiers."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import core2a_inventory

REPO = Path(__file__).resolve().parents[1]


def question(qid: str, *, structured: bool = False) -> dict:
    answer = {
        "kind": "MODEL_RESPONSE",
        "summary": "A result.",
        "reasoning": ["Represent the state.", "Connect it to the relation."],
        "check": "Substitute the result into the original condition.",
        "subpart_answers": [],
    }
    if structured:
        answer["reasoning_route"] = [
            {
                "id": "M-REP",
                "kind": "REPRESENT",
                "action": "Represent the known state.",
                "why_valid": "The relation uses these declared quantities.",
                "inputs": ["knowns"],
                "output": "represented state",
            },
            {
                "id": "M-CONNECT",
                "kind": "CONNECT",
                "action": "Connect the represented state to the governing relation.",
                "why_valid": "Its conditions are satisfied.",
                "inputs": ["represented state"],
                "output": "solvable relation",
            },
        ]
        answer["crux_move_ref"] = "M-REP"
    return {
        "id": qid,
        "status": "CANDIDATE",
        "stem": "Use the familiar relation to find the requested quantity.",
        "subparts": [],
        "options": [],
        "conditions": [],
        "figure_refs": [],
        "primary_capability_ref": "CAP-X",
        "secondary_capability_refs": [],
        "family_ref": "FAM-X",
        "answer": answer,
        "hints": [],
        "exposure": [{"core": "CORE2A", "role": "PRACTICE", "artifact_ref": None}],
    }


def write_repo(root: Path, questions: list[dict]) -> None:
    (root / "Example/adapter").mkdir(parents=True, exist_ok=True)
    (root / "Example/library").mkdir(parents=True, exist_ok=True)
    (root / "Example/adapter/CoreContracts.json").write_text("{}\n", encoding="utf-8")
    package = {"package_id": "PKG-X", "questions": questions}
    (root / "Example/library/example.json").write_text(
        json.dumps(package, indent=2) + "\n", encoding="utf-8"
    )


class Core2AInventory(unittest.TestCase):
    def test_current_tree_proves_inventory_is_nonvacuous_and_mixed(self):
        report = core2a_inventory.inventory(REPO)
        self.assertGreater(report["summary"]["core2a_questions"], 0)
        self.assertGreater(report["summary"]["structured"], 0)
        self.assertGreater(report["summary"]["migration_required"], 0)

    def test_structured_represent_crux_is_mature_core2a(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, [question("Q-1", structured=True)])
            row = core2a_inventory.inventory(root)["rows"][0]
        self.assertEqual(row["state"], "STRUCTURED")
        self.assertEqual(row["crux_kind"], "REPRESENT")
        self.assertFalse(row["migration_required"])

    def test_legacy_reasoning_is_named_not_silently_accepted_as_migrated(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, [question("Q-1")])
            row = core2a_inventory.inventory(root)["rows"][0]
        self.assertEqual(row["state"], "LEGACY_REASONING_MIGRATION_REQUIRED")
        self.assertTrue(row["migration_required"])

    def test_unchanged_legacy_debt_is_allowed_by_forward_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, [question("Q-1")])
            report = core2a_inventory.inventory(root)
            baseline = core2a_inventory.baseline_document(report)
            self.assertEqual(core2a_inventory.forward_findings(report, baseline), [])

    def test_new_legacy_core2a_question_fails_forward_gate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, [question("Q-1")])
            before = core2a_inventory.inventory(root)
            baseline = core2a_inventory.baseline_document(before)
            write_repo(root, [question("Q-1"), question("Q-2")])
            after = core2a_inventory.inventory(root)
            points = [row["point"] for row in core2a_inventory.forward_findings(after, baseline)]
        self.assertIn("CORE2A_NEW_LEGACY_REASONING", points)

    def test_materially_edited_legacy_question_must_migrate(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            original = question("Q-1")
            write_repo(root, [original])
            baseline = core2a_inventory.baseline_document(core2a_inventory.inventory(root))
            changed = question("Q-1")
            changed["answer"]["reasoning"].append("A newly authored teaching move.")
            write_repo(root, [changed])
            points = [
                row["point"]
                for row in core2a_inventory.forward_findings(
                    core2a_inventory.inventory(root), baseline
                )
            ]
        self.assertIn("CORE2A_LEGACY_MATERIAL_EDIT_WITHOUT_STRUCTURED_ROUTE", points)

    def test_migrating_an_existing_legacy_question_clears_debt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write_repo(root, [question("Q-1")])
            baseline = core2a_inventory.baseline_document(core2a_inventory.inventory(root))
            write_repo(root, [question("Q-1", structured=True)])
            report = core2a_inventory.inventory(root)
            self.assertEqual(core2a_inventory.forward_findings(report, baseline), [])
            self.assertEqual(report["summary"]["migration_required"], 0)

    def test_why_valid_cannot_merely_repeat_the_action(self):
        q = question("Q-1", structured=True)
        q["answer"]["reasoning_route"][0]["why_valid"] = (
            q["answer"]["reasoning_route"][0]["action"]
        )
        points = [row["point"] for row in core2a_inventory.quality_findings(q)]
        self.assertIn("CORE2A_REASONING_JUSTIFICATION_REPEATS_ACTION", points)

    def test_duplicate_reasoning_moves_are_obvious_quality_defects(self):
        q = question("Q-1", structured=True)
        duplicate = dict(q["answer"]["reasoning_route"][0])
        duplicate["id"] = "M-DUP"
        q["answer"]["reasoning_route"].append(duplicate)
        points = [row["point"] for row in core2a_inventory.quality_findings(q)]
        self.assertIn("CORE2A_REASONING_MOVE_DUPLICATE", points)

    def test_generic_check_is_rejected_but_meaningful_unclassified_check_is_not(self):
        q = question("Q-1", structured=True)
        q["answer"]["check"] = "Check your answer."
        self.assertEqual(
            core2a_inventory.check_quality(q["answer"])["state"],
            "GENERIC_NON_EXECUTABLE",
        )
        points = [row["point"] for row in core2a_inventory.quality_findings(q)]
        self.assertIn("CORE2A_LEARNER_CHECK_GENERIC", points)

        q["answer"]["check"] = (
            "Compare the final state with the declared conservation constraint."
        )
        self.assertEqual(
            core2a_inventory.check_quality(q["answer"])["state"],
            "EXECUTABLE_UNCLASSIFIED",
        )
        self.assertNotIn(
            "CORE2A_LEARNER_CHECK_GENERIC",
            [row["point"] for row in core2a_inventory.quality_findings(q)],
        )

    def test_known_check_kinds_are_reported_without_becoming_a_subject_oracle(self):
        examples = {
            "SUBSTITUTE_ORIGINAL_CONDITION":
                "Substitute the result back into the original equation.",
            "DIMENSION_OR_UNIT":
                "Check that every term has the same unit.",
            "SIGN_DIRECTION_BOUND":
                "Check that the sign and direction match the declared axis.",
            "REPRESENTATION_CROSSCHECK":
                "Cross-check the result against the vector diagram.",
        }
        for expected, text in examples.items():
            with self.subTest(expected=expected):
                self.assertEqual(
                    core2a_inventory.check_quality({"check": text})["class"],
                    expected,
                )

    def test_forward_gate_rejects_obvious_quality_defect_even_when_structured(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            q = question("Q-1", structured=True)
            q["answer"]["check"] = "Check your answer."
            write_repo(root, [q])
            report = core2a_inventory.inventory(root)
            points = [
                row["point"]
                for row in core2a_inventory.forward_findings(report, {"items": []})
            ]
        self.assertIn("CORE2A_LEARNER_CHECK_GENERIC", points)


if __name__ == "__main__":
    unittest.main()
