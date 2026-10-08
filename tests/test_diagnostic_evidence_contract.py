from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools import feedback, study_session


REPO = Path(__file__).resolve().parents[1]


class DiagnosticEvidenceContractTests(unittest.TestCase):
    def request(self) -> dict:
        return {
            "subject": "Mathematics",
            "question_ref": "Q-MATH-LINEAR-01",
            "attempt_number": 3,
            "shown_hint_indices": [0, 1],
            "attempted_question_refs": ["Q-MATH-LINEAR-01"],
            "help_used": "HINT",
            "when": "2026-10-06",
            "session_ref": "ISS66-U07",
            "response_summary": "Could not isolate x.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-MATH-ISOLATE",
                "error_stage": "SETUP",
            },
        }

    def evidence(self, diagnosis: str = "CONFIRMED") -> dict:
        records = feedback.subject_records("Mathematics")
        evidence, error = feedback.diagnostic_evidence_for(
            records,
            "CAP-MATH-ISOLATE",
            0,
            "Learner says the same operation may be applied to only one side.",
            diagnosis,
            "The response to the canonical probe directly states whether equivalence must be preserved.",
        )
        self.assertIsNone(error)
        self.assertIsNotNone(evidence)
        return evidence

    def test_schema_requires_probe_response_diagnosis_and_basis(self):
        schema = json.loads(
            (REPO / "Shared/quality/diagnostic-evidence.schema.json").read_text(encoding="utf-8")
        )
        check = Draft202012Validator(schema)
        good = self.evidence()
        self.assertEqual(list(check.iter_errors(good)), [])
        for key in ("probe", "observed_response", "diagnosis", "basis"):
            with self.subTest(key=key):
                broken = copy.deepcopy(good)
                del broken[key]
                self.assertTrue(list(check.iter_errors(broken)))

    def test_bare_misconception_index_never_confirms_or_repairs(self):
        request = self.request()
        request["evaluation"]["misconception_index"] = 0
        report = feedback.run(request)
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("repair", report)
        self.assertIsNone(report["diagnostic_evidence"])
        self.assertIn(
            "DIAGNOSTIC_EVIDENCE_REQUIRED",
            [row["point"] for row in report["findings"]],
        )
        self.assertFalse(report["passed"])

    def test_indeterminate_evidence_stays_in_diagnose(self):
        request = self.request()
        request["evaluation"]["diagnostic_evidence"] = self.evidence("INDETERMINATE")
        report = feedback.run(request)
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("repair", report)
        self.assertEqual(report["diagnostic_evidence"]["diagnosis"], "INDETERMINATE")
        self.assertTrue(report["passed"], report["findings"])

    def test_refuted_evidence_does_not_select_that_repair(self):
        request = self.request()
        request["evaluation"]["diagnostic_evidence"] = self.evidence("REFUTED")
        report = feedback.run(request)
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("repair", report)
        self.assertEqual(report["diagnostic_evidence"]["diagnosis"], "REFUTED")

    def test_confirmed_evidence_routes_to_repair_then_fresh_verification(self):
        request = self.request()
        request["evaluation"]["diagnostic_evidence"] = self.evidence("CONFIRMED")
        report = feedback.run(request)
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")
        self.assertEqual(report["diagnostic_evidence"]["diagnosis"], "CONFIRMED")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        self.assertNotEqual(
            report["after_repair"]["verification"].get("question_ref"),
            request["question_ref"],
        )

    def test_probe_mismatch_is_rejected(self):
        request = self.request()
        bad = self.evidence("CONFIRMED")
        bad["probe"] = "A different, non-canonical prompt."
        request["evaluation"]["diagnostic_evidence"] = bad
        report = feedback.run(request)
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("repair", report)
        self.assertIn(
            "DIAGNOSTIC_EVIDENCE_PROBE_MISMATCH",
            [row["point"] for row in report["findings"]],
        )
        self.assertFalse(report["passed"])

    def test_session_runner_builds_canonical_probe_evidence_before_repair(self):
        mapping = json.loads(
            (REPO / "tests/fixtures/study_session/relative-motion.worksheet.json").read_text(
                encoding="utf-8"
            )
        )
        report = study_session.attempt(
            mapping,
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-10-06",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            attempt_number=3,
            misconception_index=0,
            diagnostic_response="I subtracted speeds without preserving the directed observer-to-object relation.",
            diagnosis="CONFIRMED",
            diagnostic_basis="The learner repeated the targeted scalar/order error on the canonical probe.",
            response_summary="Used scalar speed difference.",
        )
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")
        self.assertEqual(report["diagnostic_evidence"]["diagnosis"], "CONFIRMED")
        self.assertTrue(report["diagnostic_evidence"]["probe"].strip())
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")


if __name__ == "__main__":
    unittest.main()
