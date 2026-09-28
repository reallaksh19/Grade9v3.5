from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import product_manifest, render_core

REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "products/physics/phy-nlm-first-law.manifest.json"
PACKAGE = REPO / "Physics/library/phy-nlm-first-law.v1.json"
BANK = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"


class NlmSelectionContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.bank_questions = cls.bank["questions"]

    def validate(self, manifest: dict) -> dict[str, list[dict]]:
        return product_manifest.validate_selection(
            manifest,
            [self.package],
            self.bank_questions,
        )

    def test_current_nlm_selection_is_exactly_resolved_in_role_authority(self):
        selection = self.manifest["selection"]
        self.assertEqual(
            {key: len(value) for key, value in selection.items()},
            {"microtopics": 11, "core2": 13, "core2a": 22, "core2b": 16},
        )
        self.assertTrue(all(len(values) == len(set(values)) for values in selection.values()))

        resolved = self.validate(self.manifest)
        self.assertEqual(
            {key: len(value) for key, value in resolved.items()},
            {"microtopics": 11, "core2": 13, "core2a": 22, "core2b": 16},
        )

        package_question_ids = {row["id"] for row in self.package["questions"]}
        bank_question_ids = {row["id"] for row in self.bank_questions}
        self.assertTrue(set(selection["core2"]) <= bank_question_ids)
        self.assertTrue(set(selection["core2"]).isdisjoint(package_question_ids))
        self.assertTrue(set(selection["core2a"]) <= package_question_ids)
        self.assertTrue(set(selection["core2b"]) <= package_question_ids)
        self.assertTrue(set(selection["core2a"]).isdisjoint(bank_question_ids))
        self.assertTrue(set(selection["core2b"]).isdisjoint(bank_question_ids))

    def test_selected_authored_assessments_have_explicit_normalized_metadata(self):
        selected = self.manifest["selection"]["core2a"] + self.manifest["selection"]["core2b"]
        package_questions = {q["id"]: q for q in self.package["questions"]}
        self.assertEqual(len(selected), 38)
        rows = [package_questions[record_id] for record_id in selected]
        self.assertTrue(all(row.get("learner_question_type") == "constructed_response" for row in rows))
        self.assertTrue(all(isinstance(row.get("difficulty"), dict) for row in rows))
        self.assertGreaterEqual(len({package_questions[i]["difficulty"]["band"] for i in self.manifest["selection"]["core2a"]}), 3)
        self.assertGreaterEqual(len({package_questions[i]["difficulty"]["band"] for i in self.manifest["selection"]["core2b"]}), 2)
        for row in rows:
            difficulty = row["difficulty"]
            self.assertEqual(difficulty["score"], sum(difficulty["components"].values()))
            self.assertTrue(difficulty["basis"])

    def test_missing_selected_id_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["selection"]["core2"][0] = "Q-DOES-NOT-EXIST"
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            r"PRODUCT_SELECTION_UNRESOLVED: core2:Q-DOES-NOT-EXIST:expected=BANK",
        ):
            self.validate(manifest)

    def test_duplicate_selected_id_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        duplicate = manifest["selection"]["core2"][0]
        manifest["selection"]["core2"].append(duplicate)
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            rf"PRODUCT_SELECTION_DUPLICATE_ID: core2:{duplicate}",
        ):
            self.validate(manifest)

    def test_wrong_authority_fails_closed(self):
        manifest = copy.deepcopy(self.manifest)
        package_question = manifest["selection"]["core2a"][0]
        manifest["selection"]["core2"][0] = package_question
        with self.assertRaisesRegex(
            product_manifest.ProductSelectionError,
            rf"PRODUCT_SELECTION_WRONG_AUTHORITY: core2:{package_question}:expected=BANK",
        ):
            self.validate(manifest)

    def test_renderer_context_uses_the_same_fail_closed_selection_contract(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["selection"]["core2b"][0] = "Q-DOES-NOT-EXIST"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "manifest.json"
            path.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(
                product_manifest.ProductSelectionError,
                r"PRODUCT_SELECTION_UNRESOLVED: core2b:Q-DOES-NOT-EXIST:expected=PACKAGE",
            ):
                render_core.context(path)


if __name__ == "__main__":
    unittest.main()
