"""Real-question pilot for the owner-supplied ExamSIDE Motion in a Plane bank."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import feedback, study_session, worksheet_study_plan  # noqa: E402


class ExamSideMotionInPlanePilot(unittest.TestCase):
    FIXTURE = REPO / "tests/fixtures/real_pilots/examside-motion-in-plane.worksheet.json"
    LIVE_FIXTURE = REPO / "docs/pilots/relative-motion-live-01.worksheet.json"

    def mapping(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def live_mapping(self):
        return json.loads(self.LIVE_FIXTURE.read_text(encoding="utf-8"))

    def relative_only(self):
        mapping = self.mapping()
        mapping["worksheet_id"] = "EXAMSIDE-RELATIVE-MOTION-SESSION"
        mapping["questions"] = mapping["questions"][:2]
        return mapping

    def test_live_pilot_packet_stops_at_real_bridge_without_invented_evidence(self):
        report = study_session.plan(self.live_mapping())
        self.assertTrue(report["valid"], report["findings"])
        self.assertFalse(report["ready"])
        self.assertEqual(report["status"], "SESSION_READY_WITH_BRIDGE")
        self.assertEqual(report["next_step"]["action"], "BRIDGE")
        self.assertEqual(
            report["next_step"]["capability_ref"],
            "CAP-SIGNED-PAIR",
        )

    def test_live_pilot_packet_becomes_ready_with_real_bridge_evidence(self):
        profile = {
            "profile_id": "PROFILE-LIVE-PILOT",
            "provenance": "UNKNOWN",
            "held": {"CAP-SIGNED-PAIR": "DEMONSTRATED"},
            "observation_refs": [],
        }
        report = study_session.plan(self.live_mapping(), profile=profile)
        self.assertTrue(report["valid"], report["findings"])
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(
            {row["question_id"] for row in report["questions"]},
            {
                "EXAMSIDE-MIP-2026-01-21-RIVER",
                "EXAMSIDE-MIP-2022-06-27-RAIN",
            },
        )

    def test_real_relative_motion_slice_runs_through_the_practical_session_runner(self):
        report = study_session.plan(
            self.relative_only(),
            ["Relative motion=60"],
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["status"], "SESSION_READY_WITH_BRIDGE")
        self.assertEqual(
            [row["matrix_id"] for row in report["readiness"]],
            ["MATRIX-PHY-RELATIVE-MOTION"],
        )
        route = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(route["CAP-SIGNED-PAIR"]["recommended_action"], "BRIDGE")
        self.assertEqual(route["CAP-SAME-TIME"]["recommended_action"], "START_HERE")
        self.assertEqual(route["CAP-RELATIVE-V"]["recommended_action"], "STUDY")
        self.assertEqual(report["next_step"]["external_provider"], "Mathematics")

    def test_real_relative_motion_attempt_runs_through_session_runner_without_persisting(self):
        mapping = self.relative_only()
        row = mapping["questions"][0]
        report = study_session.attempt(
            mapping,
            row["question_id"],
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            response_summary="Subtracted the speeds as scalars and ignored direction.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertEqual(report["observation_draft"]["result"], "MISSING")
        self.assertEqual(report["review"]["next_review"], "2026-09-19")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")

    def test_real_question_slice_maps_without_promoting_questions_to_canonical_truth(self):
        mapping = self.mapping()
        report = worksheet_study_plan.resolve(mapping)
        self.assertEqual(len(report["questions"]), 3)

        for source_row, resolved in zip(mapping["questions"], report["questions"]):
            self.assertEqual(source_row["mapping_basis"], "AGENT_PROPOSAL")
            self.assertNotIn("canonical_question_ref", source_row)
            self.assertNotEqual(resolved["core_lesson"], "UNRESOLVED")
            self.assertEqual(resolved["learner_state"], "UNOBSERVED")

    def test_real_slice_exercises_more_than_one_canonical_matrix(self):
        report = worksheet_study_plan.resolve(self.mapping())
        matrices = {
            lesson["matrix_id"]
            for row in report["route"]
            for lesson in row.get("lessons", [])
        }
        self.assertIn("MATRIX-PHY-RELATIVE-MOTION", matrices)
        self.assertIn("MATRIX-PHY-NLM-FIRST-LAW", matrices)

    def test_real_slice_routes_declared_external_prerequisite_as_explicit_bridge(self):
        report = worksheet_study_plan.resolve(self.mapping())
        self.assertTrue(report["passed"], report["findings"])
        by_cap = {row["capability_ref"]: row for row in report["route"]}
        bridge = by_cap["CAP-SIGNED-PAIR"]
        self.assertEqual(bridge["state"], "EXTERNAL_BRIDGE")
        self.assertEqual(bridge["recommended_action"], "BRIDGE")
        self.assertEqual(bridge["external_provider"], "Mathematics")
        self.assertEqual(
            bridge["acceptance_status"],
            "PROVIDER_REVIEW_REQUIRED",
        )
        self.assertFalse(any(
            row.get("point") == "STUDY_ROUTE_CAPABILITY_HAS_NO_TEACHING_LOCATION"
            and row.get("capability") == "CAP-SIGNED-PAIR"
            for row in report["findings"]
        ))

    def test_relative_motion_demand_keeps_reference_frame_support_explicit(self):
        report = worksheet_study_plan.resolve(self.mapping())
        by_cap = {row["capability_ref"]: row for row in report["route"]}
        self.assertIn("CAP-RELATIVE-V", by_cap)
        self.assertIn("CAP-VECTOR-CHECK", by_cap)
        self.assertIn("CAP-NLM-FRAME-CHOICE", by_cap)
        self.assertIn("CAP-NLM-FBD-BODY-OWNERSHIP", by_cap)
        self.assertLess(
            by_cap["CAP-NLM-FBD-BODY-OWNERSHIP"]["order"],
            by_cap["CAP-NLM-FRAME-CHOICE"]["order"],
        )

    def test_real_external_question_enters_feedback_without_becoming_canonical(self):
        mapping = self.mapping()
        row = mapping["questions"][0]
        report = feedback.run({
            "subject": mapping["subject"],
            "question_ref": row["question_id"],
            "worksheet_question": row,
            "attempt_number": 1,
            "attempted_question_refs": [row["question_id"]],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": mapping["worksheet_id"],
            "response_summary": "Subtracted the two speeds and ignored direction.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-RELATIVE-V",
                "error_stage": "CONCEPT",
            },
        })
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertEqual(report["observation_draft"]["result"], "MISSING")
        self.assertEqual(report["review"]["next_review"], "2026-09-19")
        prompts = [
            diagnostic["diagnostic_prompt"]
            for option in report["diagnostic_options"]
            for diagnostic in option["diagnostics"]
        ]
        self.assertTrue(any("directions" in prompt for prompt in prompts))

    def test_diagnosed_real_question_repairs_then_uses_fresh_canonical_check(self):
        mapping = self.mapping()
        row = mapping["questions"][0]
        report = feedback.run({
            "subject": mapping["subject"],
            "question_ref": row["question_id"],
            "worksheet_question": row,
            "attempt_number": 1,
            "attempted_question_refs": [row["question_id"]],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": mapping["worksheet_id"],
            "response_summary": "Subtracted the speeds as scalars.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-RELATIVE-V",
                "error_stage": "CONCEPT",
                "misconception_index": 0,
            },
        })
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")
        self.assertEqual(report["repair"]["microtopic_ref"], "MIC-COMMON-INTERVAL")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        verification = report["after_repair"]["verification"]
        self.assertEqual(verification["kind"], "QUESTION")
        self.assertEqual(verification["question_ref"], "Q-AUTHOR-REL-01")
        self.assertNotEqual(verification["question_ref"], row["question_id"])

    def test_first_use_is_diagnostic_without_inventing_weakness(self):
        report = worksheet_study_plan.resolve(self.mapping())
        self.assertEqual(
            {row["learner_state"] for row in report["questions"]},
            {"UNOBSERVED"},
        )
        self.assertTrue(all(
            "first attempt" in row["why_extra_attention"]
            for row in report["questions"]
        ))


if __name__ == "__main__":
    unittest.main()
