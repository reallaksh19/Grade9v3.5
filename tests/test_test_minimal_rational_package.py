from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.library import resolve
from Shared.tools import learner_metadata


REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "TEST/library/number-systems-rational-q1.v1.json"


class TestMinimalRationalPackage(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))

    def test_schema_resolver_and_fixed_cardinality(self):
        self.assertEqual(resolve.schema_problems(self.package), [])
        report = resolve.validate_library([self.package])
        self.assertEqual(report["unresolved_references"], 0)
        expected = {
            "resources": 1, "buckets": 1, "capabilities": 1, "microtopics": 1,
            "relations": 0, "representations": 0, "question_families": 1, "questions": 1,
        }
        for key, count in expected.items():
            self.assertEqual(len(self.package[key]), count, key)
        self.assertEqual(len(self.package["microtopics"][0]["construction_units"]), 1)

    def test_authored_anchor_stays_separate_from_verified_bank_question(self):
        question = self.package["questions"][0]
        self.assertEqual(question["id"], "Q-TEST-AUTHORED-NS-RATIONAL-BOUNDARY-01")
        self.assertEqual(question["origin"], "AUTHORED")
        self.assertEqual(question["extensions"]["authority"], "AGENT_AUTHORED_SANDBOX")
        projected = learner_metadata.project("CORE1A", question, [self.package])
        self.assertEqual(projected["record_ref"], question["id"])
        unit = self.package["microtopics"][0]["construction_units"][0]
        self.assertEqual(unit["worked_anchor_ref"], question["id"])
        self.assertEqual(unit["bank_anchor_ref"], "Q-TEST-NCERT-NS-Q1")
        self.assertEqual(unit["crux_question_refs"], ["Q-TEST-NCERT-NS-Q1"])


if __name__ == "__main__":
    unittest.main()
