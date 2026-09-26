"""Typed owner-decision application and stale-decision falsifiers."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import apply_owner_decisions  # noqa: E402


class OwnerDecisionApplication(unittest.TestCase):
    CURRENT = REPO / "Requests/relative-motion-six-core.ncert-current.plan-request.json"

    def request(self):
        return json.loads(self.CURRENT.read_text(encoding="utf-8"))

    def artifact(self, request):
        return apply_owner_decisions.template(request)["artifact"]

    def test_keep_drifted_source_then_agent_authors_uncovered_practice(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["decisions"]["SOURCE_BASIS_DRIFT_DECISION"] = {
            "action": "KEEP_SUPPLIED_DESPITE_DRIFT"
        }
        report = apply_owner_decisions.apply(request, artifact)
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(
            report["request_after"]["source_basis_drift_acknowledgement"],
            "KEEP_SUPPLIED_DESPITE_DRIFT",
        )
        self.assertNotIn("SOURCE_BASIS_DRIFT_DECISION", report["remaining_overridable"])
        self.assertIn("AUTHOR_SUPPLEMENTAL_PRACTICE", report["agent_actions"])
        core2 = next(row for row in report["plan_after"]["products"]
                     if row["core"] == "CORE2")
        self.assertEqual(core2["state"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(core2["duty"]["duty"], "ACQUIRE_SOURCE")

    def test_change_source_basis_clears_stale_receipt_and_policy(self):
        request = self.request()
        request["supplemental_question_policy"] = "SOURCE_ONLY"
        # The current plan would not normally ask supplement policy while drift is open,
        # so remove it before pinning and then prove replacement clears it if present.
        request.pop("supplemental_question_policy")
        artifact = self.artifact(request)
        artifact["decisions"]["SOURCE_BASIS_DRIFT_DECISION"] = {
            "action": "CHANGE_SOURCE_BASIS",
            "replacement_source_basis": [
                "https://ncert.nic.in/textbook/pdf/keph102.pdf"
            ],
        }
        report = apply_owner_decisions.apply(request, artifact)
        self.assertTrue(report["passed"], report["findings"])
        after = report["request_after"]
        self.assertEqual(
            after["source_basis"],
            ["https://ncert.nic.in/textbook/pdf/keph102.pdf"],
        )
        self.assertNotIn("source_receipt_ref", after)
        self.assertNotIn("source_basis_drift_acknowledgement", after)
        self.assertNotIn("supplemental_question_policy", after)
        self.assertIn("INSPECT_AND_INGEST_SOURCE_BASIS", report["agent_actions"])
        self.assertNotIn("SOURCE_BASIS_DRIFT_DECISION", report["remaining_overridable"])
        for core in ("CORE2", "CORE2A", "CORE2B"):
            product = next(row for row in report["plan_after"]["products"]
                           if row["core"] == core)
            self.assertEqual(product["state"], "RESEARCH_AND_AUTHOR")
            self.assertEqual(product["duty"]["duty"], "ACQUIRE_SOURCE")

    def test_unoffered_replacement_is_rejected(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["decisions"]["SOURCE_BASIS_DRIFT_DECISION"] = {
            "action": "CHANGE_SOURCE_BASIS",
            "replacement_source_basis": ["https://example.invalid/not-offered.pdf"],
        }
        report = apply_owner_decisions.apply(request, artifact)
        self.assertFalse(report["passed"])
        self.assertIn("OWNER_SOURCE_REPLACEMENT_NOT_OFFERED",
                      [row["point"] for row in report["findings"]])

    def test_unsolicited_decision_is_rejected(self):
        request = self.request()
        artifact = self.artifact(request)
        # The request already names its source basis, so there is nothing to override.
        artifact["decisions"]["SOURCE_BASIS"] = ["https://example.invalid/other.pdf"]
        report = apply_owner_decisions.apply(request, artifact)
        self.assertFalse(report["passed"])
        self.assertIn("OWNER_DECISION_UNSOLICITED",
                      [row["point"] for row in report["findings"]])

    def test_request_change_makes_decision_artifact_stale(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["decisions"]["SOURCE_BASIS_DRIFT_DECISION"] = {
            "action": "KEEP_SUPPLIED_DESPITE_DRIFT"
        }
        changed = copy.deepcopy(request)
        changed["requested_cores"] = ["CORE1", "CORE2"]
        report = apply_owner_decisions.apply(changed, artifact)
        self.assertFalse(report["passed"])
        self.assertIn("OWNER_DECISIONS_REQUEST_STALE",
                      [row["point"] for row in report["findings"]])

    def test_plan_change_makes_decision_artifact_stale(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["plan_digest"] = "0" * 64
        artifact["decisions"]["SOURCE_BASIS_DRIFT_DECISION"] = {
            "action": "KEEP_SUPPLIED_DESPITE_DRIFT"
        }
        report = apply_owner_decisions.apply(request, artifact)
        self.assertFalse(report["passed"])
        self.assertIn("OWNER_DECISIONS_PLAN_STALE",
                      [row["point"] for row in report["findings"]])

    def test_explicit_unknown_learner_takes_the_default_median(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["decisions"]["LEARNER_ENTRY"] = {
            "kind": "unknown",
            "instruction": "No learner evidence is available for this run.",
        }
        report = apply_owner_decisions.apply(request, artifact)
        self.assertTrue(report["passed"], report["findings"])
        route = report["plan_after"]["learner_route"]
        self.assertNotEqual(route["state"], "BLOCKED")
        learner = next(row for row in report["plan_after"]["defaults_applied"]
                       if row["field"] == "learner")
        self.assertEqual(learner["basis"], "DEFAULT_MEDIAN")

    def test_partial_decisions_are_legal(self):
        request = self.request()
        artifact = self.artifact(request)
        artifact["decisions"]["CORE2A_PURPOSE"] = "PRACTICE"
        report = apply_owner_decisions.apply(request, artifact)
        self.assertTrue(report["passed"], report["findings"])
        self.assertNotIn("CORE2A_PURPOSE", report["remaining_overridable"])
        self.assertIn("CORE2B_PURPOSE", report["remaining_overridable"])
        self.assertIn("SOURCE_BASIS_DRIFT_DECISION", report["remaining_overridable"])

    def test_audit_supports_every_planner_owner_input(self):
        report = apply_owner_decisions.audit()
        self.assertTrue(report["passed"], report["findings"])
        self.assertGreater(report["plan_fixtures"], 0)


if __name__ == "__main__":
    unittest.main()
