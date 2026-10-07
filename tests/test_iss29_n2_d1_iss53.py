from __future__ import annotations

import hashlib
import json
from pathlib import Path
import subprocess
import sys
import unittest

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
ISS53 = REPO / "evidence" / "benchmark" / "ISS53"
GENERATED = ISS53 / "generated"
SCHEMA = json.loads((REPO / "Shared" / "library" / "package.schema.json").read_text(encoding="utf-8"))

from Shared.tools import owner_bank, question_difficulty  # noqa: E402


EXPECTED = {
    "Q1": ("D1", "EXPLAIN", "QRT-EXPLAIN-D1"),
    "Q2": ("D2", "RETRIEVE", "QRT-RETRIEVE-D2"),
    "Q3": ("D1", "APPLY", "QRT-APPLY-D1"),
    "Q4": ("D1", "APPLY", "QRT-APPLY-D1"),
    "Q5": ("D2", "REPRESENT", "QRT-REPRESENT-D2"),
    "Q6": ("D2", "EXPLAIN", "QRT-EXPLAIN-D2"),
    "Q7": ("D2", "MODEL", "QRT-MODEL-D2"),
    "Q8": ("D2", "APPLY", "QRT-APPLY-D2"),
    "Q9": ("D2", "JUSTIFY", "QRT-JUSTIFY-D2"),
    "Q10": ("D2", "SYNTHESIZE", "QRT-SYNTHESIZE-D2"),
}


class Issue29N2D1ISS53(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        subprocess.run([sys.executable, str(ISS53 / "build_specimen.py")], cwd=REPO, check=True)
        cls.package = json.loads((GENERATED / "package.v1.json").read_text(encoding="utf-8"))
        cls.bank = json.loads((GENERATED / "owner.bank.json").read_text(encoding="utf-8"))
        cls.reanalysis = json.loads((ISS53 / "academic-reanalysis.v1.json").read_text(encoding="utf-8"))

    def test_frozen_owner_prompt_digest_is_unchanged(self) -> None:
        digest = hashlib.sha256((ISS53 / "owner-core-prompt.md").read_bytes()).hexdigest()
        self.assertEqual(digest, "c2cca6e6b92997c30d2f3a7eab91577bc8463ec9ce44ca90b9be728f3d1d46b8")

    def test_generated_package_conforms_to_current_schema(self) -> None:
        errors = sorted(
            Draft202012Validator(SCHEMA).iter_errors(self.package),
            key=lambda e: tuple(str(x) for x in e.absolute_path),
        )
        self.assertEqual([f"{list(e.absolute_path)}: {e.message}" for e in errors], [])

    def test_owner_bank_meets_current_core2_contract(self) -> None:
        self.assertEqual(owner_bank.check(self.bank, "ISS53", complete=True), [])

    def test_requested_d1_is_separate_from_derived_difficulty(self) -> None:
        rows = {row["q"]: row for row in self.reanalysis["rows"]}
        bank = {q["original_identifier"]: q for q in self.bank["questions"]}
        self.assertEqual(set(rows), set(EXPECTED))
        self.assertEqual(set(bank), set(EXPECTED))
        for qid, (band, demand, template) in EXPECTED.items():
            row = rows[qid]
            self.assertEqual(row["difficulty"]["band"], band)
            self.assertEqual(row["demand"]["primary"], demand)
            self.assertEqual(row["demand"]["template_id"], template)
            analysis = bank[qid]["extensions"]["grade9v3:analysis"]
            derived = question_difficulty.derive(analysis["difficulty"], question_ref=qid)
            self.assertEqual(derived["requested_band"], "D1")
            self.assertEqual(derived["band"], band)
            self.assertEqual(analysis["cognitive_demand"], demand)

    def test_core2_attempt_has_no_authored_figure_and_declares_protected_move(self) -> None:
        for question in self.bank["questions"]:
            self.assertEqual(question["figure_refs"], [], question["id"])
            plan = question["extensions"]["grade9v3:core2_support_plan"]
            self.assertEqual(plan["protected_move_refs"], [question["answer"]["crux_move_ref"]])
            waiver = question["extensions"]["grade9v3:component_waivers"]["TRAP"]
            self.assertIn("not pre-authorized", waiver)
            self.assertNotIn("taught directly", waiver)

    def test_authored_practice_has_separate_provenance(self) -> None:
        resources = {row["id"]: row for row in self.package["resources"]}
        practice = resources["SRC-AUTHORED-ISS29-N2-D1-PRACTICE"]
        self.assertEqual(practice["origin"], "AUTHORED")
        self.assertIn("not CBSE/NCERT/PYQ", practice["rights_status"])
        for microtopic in self.package["microtopics"]:
            self.assertEqual(microtopic["exit_task"]["source_ref"], practice["id"])

    def test_core1a_uses_changed_anchors_not_source_question_worked_examples(self) -> None:
        all_units = [
            unit
            for microtopic in self.package["microtopics"]
            for unit in microtopic.get("construction_units", [])
        ]
        self.assertTrue(all_units)
        self.assertTrue(all(unit.get("bank_anchor_ref") is None for unit in all_units))
        ids = {unit["id"] for unit in all_units}
        self.assertTrue({
            "CU-MATH-POLY-SQUARE-CROSS-TERMS",
            "CU-MATH-POLY-DIFF-SQUARES",
            "CU-MATH-POLY-RECTANGLE-MODEL",
            "CU-MATH-POLY-UNIVERSAL-IDENTITY",
            "CU-MATH-POLY-LINEAR-CONSTRAINTS",
        }.issubset(ids))

    def test_changed_visuals_do_not_replay_protected_source_cases(self) -> None:
        coeff = (ISS53 / "assets" / "poly-coeff-table.svg").read_text(encoding="utf-8")
        exponent = (ISS53 / "assets" / "poly-exponent-classification.svg").read_text(encoding="utf-8")
        square = (ISS53 / "assets" / "poly-area-model.svg").read_text(encoding="utf-8")
        linear = (ISS53 / "assets" / "poly-linear-zero.svg").read_text(encoding="utf-8")
        self.assertNotIn("5x³", coeff)
        self.assertNotIn("4x³", coeff)
        self.assertNotIn("3x² − 2x + 1", exponent)
        self.assertNotIn("(x + 3)", square)
        self.assertNotIn("(0, 2)", linear)
        self.assertNotIn("(1, 0)", linear)

    def test_historical_acceptance_is_not_carried_forward(self) -> None:
        for row in self.reanalysis["rows"]:
            self.assertEqual(row["acceptance_state"], "AUTHOR_DERIVED_PENDING_INDEPENDENT_RENDERED_REVIEW")


if __name__ == "__main__":
    unittest.main()
