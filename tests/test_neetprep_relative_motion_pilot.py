"""Real-source pilot for the owner-supplied NEETPrep Relative Motion mini bank."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import study_map, study_session  # noqa: E402


class NeetprepRelativeMotionPilot(unittest.TestCase):
    FIXTURE = (
        REPO
        / "tests/fixtures/real_pilots/neetprep-relative-motion.worksheet.json"
    )

    def mapping(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def test_routable_slice_is_real_external_demand_not_canonical_questions(self):
        mapping = self.mapping()
        report = study_map.resolve(mapping)
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(len(report["questions"]), 6)

        index = study_map.subject_index("Physics")
        canonical = index["canonical_questions"]
        for row in mapping["questions"]:
            with self.subTest(question=row["question_id"]):
                self.assertEqual(row["mapping_basis"], "AGENT_PROPOSAL")
                self.assertNotIn(row["question_id"], canonical)

    def test_routable_questions_use_existing_relative_motion_or_vector_foundation_capabilities(self):
        mapping = self.mapping()
        expected = {
            "NEETPREP-MQB-REL-Q1": (
                "CAP-RELATIVE-V",
                {"CAP-VECTOR-CHECK", "CAP-RIGHT-TRIANGLE"},
            ),
            "NEETPREP-MQB-REL-Q2": (
                "CAP-RELATIVE-V",
                {"CAP-VECTOR-CHECK"},
            ),
            "NEETPREP-MQB-REL-Q3": (
                "CAP-RELATIVE-V",
                {"CAP-VECTOR-CHECK", "CAP-RIGHT-TRIANGLE"},
            ),
            "NEETPREP-MQB-REL-Q4": (
                "CAP-VEC-RESULTANT-CONSTRAINT",
                {"CAP-RELATIVE-V"},
            ),
            "NEETPREP-MQB-REL-Q5": (
                "CAP-VEC-RESULTANT-CONSTRAINT",
                {"CAP-RELATIVE-V", "CAP-RIGHT-TRIANGLE"},
            ),
            "NEETPREP-MQB-REL-Q7": (
                "CAP-RELATIVE-V",
                {"CAP-VECTOR-CHECK", "CAP-RIGHT-TRIANGLE"},
            ),
        }
        for row in mapping["questions"]:
            with self.subTest(question=row["question_id"]):
                primary, secondary = expected[row["question_id"]]
                self.assertEqual(row["primary_capability_ref"], primary)
                self.assertEqual(set(row["secondary_capability_refs"]), secondary)

    def test_session_plan_is_valid_but_keeps_provider_bridges_visible(self):
        report = study_session.plan(self.mapping())
        self.assertTrue(report["valid"], report["findings"])
        self.assertEqual(report["status"], "SESSION_READY_WITH_BRIDGE")

        route = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(route["CAP-SIGNED-PAIR"]["recommended_action"], "BRIDGE")
        self.assertEqual(route["CAP-RIGHT-TRIANGLE"]["recommended_action"], "BRIDGE")
        self.assertEqual(
            route["CAP-SIGNED-PAIR"]["external_provider"],
            "Mathematics",
        )
        self.assertEqual(
            route["CAP-RIGHT-TRIANGLE"]["external_provider"],
            "Mathematics",
        )

    def test_no_owner_percentage_is_invented_for_the_real_source(self):
        report = study_session.plan(self.mapping())
        self.assertEqual(report["owner_estimates"], [])

    def test_wrong_rain_question_routes_to_existing_relative_velocity_diagnosis(self):
        report = study_session.attempt(
            self.mapping(),
            "NEETPREP-MQB-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            response_summary="Combined only the speed magnitudes.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertEqual(report["observation_draft"]["result"], "MISSING")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")
        prompts = [
            diagnostic["diagnostic_prompt"]
            for option in report["diagnostic_options"]
            for diagnostic in option["diagnostics"]
        ]
        self.assertTrue(prompts)

    def test_confirmed_error_repairs_then_uses_fresh_canonical_verification(self):
        report = study_session.attempt(
            self.mapping(),
            "NEETPREP-MQB-REL-Q2",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            misconception_index=0,
            diagnostic_response="I reversed the relative-velocity subtraction because I treated the order as interchangeable.",
            diagnosis="CONFIRMED",
            diagnostic_basis="The canonical probe response explicitly repeats the targeted relative-velocity order error.",
            response_summary="Used the wrong relative-velocity subtraction order.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["microtopic_ref"], "MIC-COMMON-INTERVAL")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        verification = report["after_repair"]["verification"]
        self.assertEqual(verification["kind"], "QUESTION")
        self.assertEqual(verification["question_ref"], "Q-AUTHOR-REL-01")

    def test_figure_dependent_source_items_are_not_smuggled_into_the_executable_fixture(self):
        ids = {row["question_id"] for row in self.mapping()["questions"]}
        self.assertIn("NEETPREP-MQB-REL-Q4", ids)
        self.assertIn("NEETPREP-MQB-REL-Q5", ids)
        self.assertNotIn("NEETPREP-MQB-REL-Q6", ids)
        self.assertNotIn("NEETPREP-MQB-REL-Q8", ids)


class RelativeMotionQ4DryRun(unittest.TestCase):
    """Synthetic dry run of the Q4 learner loop; never empirical learner evidence."""

    FIXTURE = (
        REPO
        / "tests/fixtures/real_pilots/neetprep-relative-motion.worksheet.json"
    )
    Q4 = "NEETPREP-MQB-REL-Q4"
    SESSION = "SESSION-DRY-PHY-REL-Q4-01"

    def mapping(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def attempt(self, **kwargs):
        defaults = {
            "result": "INCORRECT",
            "when": "2026-09-18",
            "session_ref": self.SESSION,
        }
        defaults.update(kwargs)
        return study_session.attempt(self.mapping(), self.Q4, **defaults)

    def test_independent_correct_is_only_an_unreviewed_draft(self):
        report = self.attempt(result="CORRECT", help_used="NONE")
        self.assertEqual(report["next_action"], "CONTINUE")
        self.assertEqual(report["observation_draft"]["result"], "DEMONSTRATED")
        self.assertEqual(
            report["observation_draft"]["provenance"],
            "UNREVIEWED_SESSION_DRAFT",
        )
        self.assertEqual(report["persistence"], "NOT_WRITTEN")

    def test_helped_correct_requests_fresh_exit_verification(self):
        report = self.attempt(result="CORRECT", help_used="HINT")
        self.assertEqual(report["observation_draft"]["result"], "UNCERTAIN")
        self.assertEqual(report["next_action"], "VERIFY")
        self.assertEqual(report["verification"]["kind"], "EXIT_TASK")
        self.assertEqual(
            report["verification"]["microtopic_ref"],
            "MIC-PHY-VEC-RESULTANT-CONSTRAINT",
        )

    def test_ambiguous_failure_diagnoses_without_guessing(self):
        report = self.attempt(result="UNDECIDABLE")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertIsNone(report["failed_capability_ref"])
        self.assertIsNone(report["observation_draft"])
        self.assertTrue(report["diagnostic_options"])

    def test_clear_resultant_constraint_failure_repairs_then_verifies(self):
        report = self.attempt(
            failed_capability_ref="CAP-VEC-RESULTANT-CONSTRAINT",
            error_stage="CONCEPT",
            misconception_index=0,
            diagnostic_response=(
                "I applied the directly-opposite condition to the swimmer vector "
                "instead of the ground-relative resultant."
            ),
            diagnosis="CONFIRMED",
            diagnostic_basis=(
                "The canonical diagnostic response places the opposite-direction constraint "
                "on the wrong vector, matching the authored misconception."
            ),
            response_summary=(
                "Applied the directly-opposite condition to the swimmer vector "
                "instead of the ground-relative resultant."
            ),
        )
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(
            report["repair"]["microtopic_ref"],
            "MIC-PHY-VEC-RESULTANT-CONSTRAINT",
        )
        self.assertEqual(report["observation_draft"]["result"], "MISSING")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        self.assertEqual(
            report["after_repair"]["verification"]["kind"],
            "EXIT_TASK",
        )

    def test_execution_slip_stays_uncertain(self):
        report = self.attempt(
            failed_capability_ref="CAP-VEC-RESULTANT-CONSTRAINT",
            error_stage="EXECUTION",
            response_summary="Set up the resultant constraint but made an arithmetic slip.",
        )
        self.assertEqual(report["observation_draft"]["result"], "UNCERTAIN")
        self.assertEqual(report["next_action"], "DIAGNOSE")

    def test_explicit_local_prerequisite_failure_can_be_attributed(self):
        for capability in (
            "CAP-VECTOR-SIGNED-COMPONENT",
            "CAP-VEC-COMPONENT-SUM",
        ):
            with self.subTest(capability=capability):
                report = self.attempt(
                    failed_capability_ref=capability,
                    error_stage="CONCEPT",
                    response_summary=f"Dry-run evidence explicitly supports {capability}.",
                )
                self.assertNotEqual(report["next_action"], study_session.OWNER_DECISION)
                self.assertEqual(report["failed_capability_ref"], capability)
                self.assertEqual(report["observation_draft"]["capability_ref"], capability)
                self.assertEqual(report["observation_draft"]["result"], "MISSING")
                self.assertNotIn(
                    "FEEDBACK_FAILED_CAPABILITY_NOT_REQUIRED",
                    [row["point"] for row in report["findings"]],
                )

    def test_explicit_external_prerequisite_failure_requires_owner_decision(self):
        report = self.attempt(
            failed_capability_ref="CAP-SIGNED-PAIR-BRIDGE",
            error_stage="CONCEPT",
            response_summary="Dry-run evidence explicitly isolates signed-coordinate handling.",
        )
        self.assertEqual(report["next_action"], study_session.OWNER_DECISION)
        self.assertEqual(report["execution_disposition"], study_session.OWNER_DECISION)
        self.assertIn(
            "STUDY_SESSION_QUESTION_EXTERNAL_ONLY",
            [row["point"] for row in report["findings"]],
        )


if __name__ == "__main__":
    unittest.main()
