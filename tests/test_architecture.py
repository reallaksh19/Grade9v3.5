"""Architecture acceptance tests for cold-agent planning and learner reachability."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.library import practice_inventory  # noqa: E402
from Shared.tools import (academic_readiness, capability_graph, plan_request,  # noqa: E402
                          research_first_policy, resolve_request)


class CapabilityTopology(unittest.TestCase):
    def nlm(self):
        return json.loads((REPO / "Physics/matrices/phy-nlm-first-law.rungs.json")
                          .read_text(encoding="utf-8"))

    def test_a_dependant_cannot_be_placed_before_its_prerequisite(self):
        board = self.nlm()
        # Plant the exact failure class: friction (R5) is made to occur before FBD
        # body ownership (R3), although friction genuinely depends on that capability.
        board["rungs"][3]["ladder_position"] = 60
        caps, mics = capability_graph.subject_graph("Physics")
        points = [f["point"] for f in capability_graph.topology_findings(board, caps, mics)]
        self.assertIn(capability_graph.VIOLATION, points)

    def test_entry_backtracks_and_keeps_external_bridges(self):
        board = json.loads((REPO / "Physics/matrices/relative-motion.rungs.json")
                           .read_text(encoding="utf-8"))
        caps, mics = capability_graph.subject_graph("Physics")
        route = capability_graph.resolve_entry(
            board["rungs"], "R4", {}, caps, mics)
        self.assertEqual(route["rung"], "R3")
        self.assertEqual(route["reason"], "PREREQUISITE_BACKTRACK")
        self.assertIn("CAP-SIGNED-PAIR", route["bridges"])


class PracticeOwnership(unittest.TestCase):
    def test_a_prerequisite_question_does_not_make_the_downstream_bucket_ready(self):
        records = {
            "BUCKET-A": {"id": "BUCKET-A", "_collection": "buckets"},
            "BUCKET-B": {"id": "BUCKET-B", "_collection": "buckets",
                         "prerequisite_refs": ["BUCKET-A"]},
            "CAP-A": {"id": "CAP-A", "_collection": "capabilities"},
            "CAP-B": {"id": "CAP-B", "_collection": "capabilities",
                      "prerequisite_refs": ["CAP-A"]},
            "MIC-A": {"id": "MIC-A", "_collection": "microtopics",
                      "bucket_id": "BUCKET-A", "primary_capability_ref": "CAP-A"},
            "MIC-B": {"id": "MIC-B", "_collection": "microtopics",
                      "bucket_id": "BUCKET-B", "primary_capability_ref": "CAP-B"},
            "Q-A": {"id": "Q-A", "_collection": "questions",
                    "primary_capability_ref": "CAP-A",
                    "exposure": [{"core": "CORE2A"}]},
        }
        self.assertEqual(practice_inventory.questions_for_core(
            records, "BUCKET-B", "CORE2A"), [])
        self.assertEqual(
            [q["id"] for q in practice_inventory.questions_for_core(
                records, "BUCKET-A", "CORE2A")],
            ["Q-A"],
        )

    def test_strict_resolver_agrees_relative_motion_has_no_core2b_asset(self):
        request = json.loads((REPO / "Requests/relative-motion-g9.request.json")
                             .read_text(encoding="utf-8"))
        report = resolve_request.plan(request)
        core = next(row for row in report["cores"] if row["core"] == "CORE2B")
        self.assertEqual(core["state"], "BLOCKED")
        self.assertIn("bucket-owned question", core["reason"])


class ThirdAgentGoldenPath(unittest.TestCase):
    FIXTURE = REPO / "Requests/relative-motion-six-core.plan-request.json"

    def report(self):
        return plan_request.plan(json.loads(self.FIXTURE.read_text(encoding="utf-8")))

    def test_three_line_request_resolves_without_authoring_content(self):
        report = self.report()
        self.assertEqual(report["bucket"], "BUCKET-RELATIVE-MOTION")
        self.assertTrue(report["canonical_rungs"])
        self.assertTrue(report["no_content_authored"])
        self.assertEqual(report["findings"], [])

    def duties(self, report):
        return {row["core"]: row["duty"]["duty"] for row in report["products"] if row.get("duty")}

    def test_missing_owner_inputs_take_defaults_instead_of_waiting(self):
        report = self.report()
        self.assertEqual(report["required_owner_inputs"], [])
        self.assertEqual(
            [row["field"] for row in report["defaults_applied"]],
            ["learner", "practice.CORE2A.purpose", "practice.CORE2B.purpose",
             "supplemental_question_policy"],
        )
        learner = report["defaults_applied"][0]
        self.assertEqual(learner["basis"], "DEFAULT_MEDIAN")
        self.assertEqual(learner["value"], {"owner_estimate": {"knowledge_percentage": 50}})
        self.assertEqual(
            [row["id"] for row in report["agent_actions"]],
            ["INSPECT_AND_INGEST_SOURCE_BASIS"],
        )

    def test_verified_receipt_gap_becomes_authored_practice_duty(self):
        request = json.loads(self.FIXTURE.read_text(encoding="utf-8"))
        request["source_receipt_ref"] = "SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY"
        report = plan_request.plan(request)
        actions = [row["id"] for row in report["agent_actions"]]
        self.assertIn("AUTHOR_SUPPLEMENTAL_PRACTICE", actions)
        self.assertNotIn("INSPECT_AND_INGEST_SOURCE_BASIS", actions)
        self.assertEqual(self.duties(report)["CORE2A"], "AUTHOR_PRACTICE")

    def test_verified_source_drift_is_researched_by_the_agent(self):
        request = json.loads(
            (REPO / "Requests/relative-motion-six-core.ncert-current.plan-request.json")
            .read_text(encoding="utf-8")
        )
        report = plan_request.plan(request)
        self.assertEqual(report["required_owner_inputs"], [])
        self.assertIn("RESOLVE_SOURCE_BASIS_DRIFT", [row["id"] for row in report["agent_actions"]])
        self.assertEqual(report["source"]["basis_assessment"]["status"], "DRIFT")
        for core in ("CORE2", "CORE2A", "CORE2B"):
            product = next(row for row in report["products"] if row["core"] == core)
            self.assertEqual(product["state"], "RESEARCH_AND_AUTHOR")
            self.assertEqual(product["duty"]["duty"], "ACQUIRE_SOURCE")

    def test_acknowledged_source_drift_then_authors_uncovered_practice(self):
        request = json.loads(
            (REPO / "Requests/relative-motion-six-core.ncert-current.plan-request.json")
            .read_text(encoding="utf-8")
        )
        request["source_basis_drift_acknowledgement"] = "KEEP_SUPPLIED_DESPITE_DRIFT"
        report = plan_request.plan(request)
        actions = [row["id"] for row in report["agent_actions"]]
        self.assertNotIn("RESOLVE_SOURCE_BASIS_DRIFT", actions)
        self.assertIn("AUTHOR_SUPPLEMENTAL_PRACTICE", actions)
        self.assertEqual(self.duties(report)["CORE2"], "ACQUIRE_SOURCE")

    def test_buildability_reachability_and_review_are_separate_axes(self):
        report = self.report()
        self.assertEqual(report["invariant"], "READY_TO_BUILD != REACHABLE_TO_LEARN")
        self.assertEqual(report["readiness"]["REACHABLE_TO_LEARN"], "READY")
        self.assertEqual(report["readiness"]["ACADEMIC_REVIEW"], "NOT_REVIEWED")
        self.assertEqual(report["readiness"]["CONTENT_EXPANSION"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(report["execution"]["state"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(report["lifecycle"]["RELEASE"]["state"], "OWNER_REVIEW")

    def test_no_product_state_is_an_escape_state(self):
        report = self.report()
        self.assertEqual(research_first_policy.escape_states(
            [row["state"] for row in report["products"]]
            + [report["lifecycle"][k]["state"] for k in ("AUTHORING", "BUILD", "RELEASE")]
            + list(report["readiness"].values())), [])

    def test_provenance_is_not_collapsed_into_existence_or_review(self):
        rung = self.report()["canonical_rungs"][0]
        self.assertEqual(rung["existence"], "PRESENT")
        self.assertIn("matrix_provenance", rung)
        self.assertIn("library_record_status", rung)
        self.assertIn("source_refs", rung)

    def test_six_core_relationships_are_explicit(self):
        rel = self.report()["core_relationships"]
        self.assertIn("same canonical rung segment", rel["CORE1A_CORE1B"])
        self.assertIn("support", rel["CORE2A"])
        self.assertIn("decision structure", rel["CORE2B"])


class AcademicReviewBoundary(unittest.TestCase):
    def test_relative_motion_names_its_academic_review_gap_without_faking_approval(self):
        board = json.loads((REPO / "Physics/matrices/relative-motion.rungs.json")
                           .read_text(encoding="utf-8"))
        report = academic_readiness.board_report(board, "Physics")
        self.assertEqual(
            [(row["point"], row["where"]) for row in report["mechanical_findings"]],
            [("VOCABULARY_CEILING_MISSING", "R5")],
        )
        self.assertFalse(report["mechanically_reviewable"])
        self.assertEqual(report["human_review"]["state"], "NOT_REVIEWED")
        self.assertFalse(report["learner_release_ready"])


if __name__ == "__main__":
    unittest.main()
