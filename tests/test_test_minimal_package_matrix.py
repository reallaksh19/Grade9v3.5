from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.library import resolve
from Shared.tools import matrix_conformance


REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "TEST/library/number-systems-rational-q1.v1.json"
MATRIX = REPO / "TEST/matrices/number-systems-rational.rungs.json"


class TestMinimalTestPackageMatrix(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))

    def test_fixed_cardinality_and_schema(self):
        self.assertEqual(resolve.schema_problems(self.package), [])
        expected = {
            "resources": 1, "buckets": 1, "capabilities": 1, "microtopics": 1,
            "relations": 0, "representations": 0, "question_families": 1, "questions": 1,
        }
        for key, count in expected.items():
            self.assertEqual(len(self.package[key]), count, key)
        self.assertEqual(len(self.package["microtopics"][0]["construction_units"]), 1)

    def test_package_references_resolve_without_claiming_bank_authority(self):
        report = resolve.validate_library([self.package])
        self.assertEqual(report["unresolved_references"], 0)
        question = self.package["questions"][0]
        self.assertEqual(question["origin"], "AUTHORED")
        self.assertEqual(question["extensions"]["authority"], "AGENT_AUTHORED_SANDBOX")
        unit = self.package["microtopics"][0]["construction_units"][0]
        self.assertEqual(unit["worked_anchor_ref"], question["id"])
        self.assertEqual(unit["bank_anchor_ref"], "Q-TEST-NCERT-NS-Q1")
        self.assertEqual(unit["crux_question_refs"], ["Q-TEST-NCERT-NS-Q1"])

    def test_three_rung_matrix_conforms_to_test_library(self):
        self.assertEqual([r["ladder_position"] for r in self.matrix["rungs"]], [20, 60, 100])
        self.assertEqual({r["provenance"] for r in self.matrix["rungs"]}, {"AUTHORED"})
        mics, dimensions = matrix_conformance.library("TEST")
        self.assertEqual(matrix_conformance.board_findings(self.matrix), [])
        self.assertIn("MIC-TEST-MATH-NS-RATIONAL-INCLUSION", mics)
        self.assertEqual(set(self.package["question_families"][0]["demand_dimensions"]), dimensions)


if __name__ == "__main__":
    unittest.main()
