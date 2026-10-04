from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import question_content_audit as audit

REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "Mathematics" / "question-bank" / "surface-areas-and-volumes.owner-bank.v1.json"


class QuestionContentAuditTests(unittest.TestCase):
    def test_surface_areas_volumes_bank_passes_content_self_audit(self):
        report = audit.audit_bank(json.loads(BANK.read_text(encoding="utf-8")))
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["items"]), 10)
        for item in report["items"]:
            self.assertEqual(item["hint_audit"]["verdict"], "PASS")
            self.assertEqual(item["solution_audit"]["verdict"], "PASS")
            self.assertEqual(item["calculation_audit"]["verdict"], "PASS")
            self.assertEqual(item["failure_count"], 0)

    def test_calculations_are_independently_re_evaluated(self):
        self.assertEqual(audit.safe_number("2 * (22/7) * 7 * 20"), 880)
        self.assertAlmostEqual(audit.safe_number("(3.5**2 + 12**2)**0.5"), 12.5)

    def test_hint_leaking_a_protected_result_fails(self):
        bank = json.loads(BANK.read_text(encoding="utf-8"))
        question = bank["questions"][0]
        question["scaffolds"][0]["text"] += " The answer is 294 cm²."
        self.assertEqual(audit.audit_question(question)["hint_audit"]["verdict"], "FAIL")

    def test_unknown_or_unsafe_calculation_expression_is_rejected(self):
        with self.assertRaises(audit.AuditError):
            audit.safe_number("__import__('os').system('echo no')")


if __name__ == "__main__":
    unittest.main()
