"""Thin study-session runner composes readiness, routing and feedback without new truth."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import session_readiness, study_session  # noqa: E402


class StudySessionRunner(unittest.TestCase):
    FIXTURE = REPO / "tests/fixtures/study_session/relative-motion.worksheet.json"

    def mapping(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def nlm_fbd_mapping(self):
        return {
            "worksheet_id": "WS-NLM-FBD-ROUTER",
            "subject": "Physics",
            "questions": [{
                "question_id": "Q-PHY-NLM-2A-COV-03",
                "primary_capability_ref": "CAP-NLM-FBD-BODY-OWNERSHIP",
                "secondary_capability_refs": [],
                "mapping_basis": "CANONICAL_QUESTION",
                "canonical_question_ref": "Q-PHY-NLM-2A-COV-03",
            }],
        }

    def nlm_friction_mapping(self):
        return {
            "worksheet_id": "WS-NLM-FRICTION-ROUTER",
            "subject": "Physics",
            "questions": [{
                "question_id": "Q-PHY-NLM-2A-FRICTION-STATIC-09",
                "primary_capability_ref": "CAP-NLM-FRICTION-QUANT",
                "secondary_capability_refs": ["CAP-NLM-SECOND-LAW"],
                "mapping_basis": "CANONICAL_QUESTION",
                "canonical_question_ref": "Q-PHY-NLM-2A-FRICTION-STATIC-09",
            }],
        }

    def test_human_subtopic_estimate_resolves_to_canonical_matrix(self):
        estimates, findings = study_session.resolve_estimates(
            "Physics",
            ["relative motion=60"],
        )
        self.assertEqual(findings, [])
        self.assertEqual(len(estimates), 1)
        self.assertEqual(estimates[0]["matrix_id"], "MATRIX-PHY-RELATIVE-MOTION")
        self.assertEqual(estimates[0]["knowledge_percentage"], 60)
        self.assertEqual(estimates[0]["input_target"], "relative motion")

    def test_relative_motion_plan_is_ready_with_bridge_and_starts_from_estimate(self):
        report = study_session.plan(
            self.mapping(),
            ["Relative motion=60"],
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertTrue(report["valid"])
        self.assertFalse(report["ready"])
        self.assertEqual(report["status"], session_readiness.READY_WITH_BRIDGE)
        self.assertEqual(len(report["readiness"]), 1)
        self.assertEqual(
            report["readiness"][0]["matrix_id"],
            "MATRIX-PHY-RELATIVE-MOTION",
        )
        self.assertEqual(
            report["readiness"][0]["status"],
            session_readiness.READY_WITH_BRIDGE,
        )

        route = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(route["CAP-SIGNED-PAIR"]["recommended_action"], "BRIDGE")
        self.assertEqual(route["CAP-SAME-TIME"]["recommended_action"], "START_HERE")
        self.assertEqual(route["CAP-RELATIVE-V"]["recommended_action"], "STUDY")
        self.assertEqual(route["CAP-VECTOR-CHECK"]["recommended_action"], "STUDY")

        self.assertEqual(report["next_step"]["action"], "BRIDGE")
        self.assertEqual(
            report["next_step"]["external_provider"],
            "Mathematics",
        )

    def test_demonstrated_external_prerequisite_clears_execution_blocker(self):
        profile = {
            "profile_id": "PROFILE-SESSION-BRIDGE",
            "provenance": "UNKNOWN",
            "held": {"CAP-SIGNED-PAIR": "DEMONSTRATED"},
            "observation_refs": [],
        }
        report = study_session.plan(
            self.mapping(),
            ["Relative motion=60"],
            profile=profile,
        )
        self.assertTrue(report["valid"], report["findings"])
        self.assertTrue(report["ready"], report["blockers"])
        self.assertEqual(report["blockers"], [])
        self.assertEqual(report["status"], session_readiness.READY_WITH_BRIDGE)
        self.assertEqual(report["next_step"]["action"], "START_HERE")
        self.assertEqual(
            report["next_step"]["capability_ref"],
            "CAP-SAME-TIME",
        )
        route = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(route["CAP-SIGNED-PAIR"]["recommended_action"], "SKIP")

    def test_invalid_optional_estimate_warns_and_keeps_neutral_session(self):
        report = study_session.plan(self.mapping(), ["not-a-subtopic=60"])
        self.assertTrue(report["passed"], report["findings"])
        self.assertTrue(report["valid"])
        self.assertEqual(
            report["execution_disposition"],
            study_session.EXECUTE_WITH_FALLBACK,
        )
        self.assertIn(
            "STUDY_SESSION_ESTIMATE_TARGET_UNKNOWN",
            [row["point"] for row in report["warnings"]],
        )
        self.assertIsNotNone(report["next_step"])

    def test_plan_keeps_academic_warnings_visible_without_blocking_family_pilot(self):
        report = study_session.plan(self.mapping(), ["Relative motion=60"])
        points = {row["point"] for row in report["academic_warnings"]}
        self.assertIn("READINESS_ACADEMIC_REVIEW_PENDING", points)
        self.assertIn("READINESS_SOURCE_QUESTION_COVERAGE_ABSENT", points)
        self.assertTrue(report["passed"])
        self.assertTrue(report["valid"])
        self.assertFalse(report["ready"])

    def test_not_ready_matrix_can_execute_usable_demanded_rungs_with_fallback(self):
        partial = {
            "subject": "Physics",
            "matrix_id": "MATRIX-PHY-RELATIVE-MOTION",
            "subtopic": "Relative motion",
            "status": session_readiness.NOT_READY,
            "external_bridges": [],
            "support_findings": [],
            "academic_warnings": [],
            "rungs": [
                {"rung": "R3", "state": "READY"},
                {"rung": "R4", "state": "READY"},
                {"rung": "R5", "state": "READY"},
                {"rung": "R99", "state": "BLOCKED"},
            ],
            "passed": False,
        }
        with patch.object(
            study_session.session_readiness,
            "audit",
            return_value=partial,
        ):
            report = study_session.plan(self.mapping(), ["Relative motion=60"])

        self.assertTrue(report["passed"], report["findings"])
        self.assertTrue(report["valid"])
        self.assertFalse(report["ready"])
        self.assertEqual(report["status"], session_readiness.NOT_READY)
        self.assertEqual(
            report["execution_disposition"],
            study_session.EXECUTE_WITH_FALLBACK,
        )
        self.assertIsNotNone(report["next_step"])
        self.assertTrue(report["fallback_reasons"])

    def test_missing_teaching_path_requires_owner_decision_even_when_rung_is_needs_support(self):
        partial = {
            "subject": "Physics",
            "matrix_id": "MATRIX-PHY-RELATIVE-MOTION",
            "subtopic": "Relative motion",
            "status": session_readiness.NOT_READY,
            "external_bridges": [],
            "support_findings": [],
            "academic_warnings": [],
            "blocking_findings": [{
                "point": "READINESS_TEACHING_PATH_MISSING",
                "where": "R3",
                "detail": "teaching path is absent",
            }],
            "rungs": [
                {"rung": "R3", "state": "NEEDS_SUPPORT", "teaching": False, "verification": True},
                {"rung": "R4", "state": "READY", "teaching": True, "verification": True},
                {"rung": "R5", "state": "READY", "teaching": True, "verification": True},
            ],
            "passed": False,
        }
        profile = {
            "profile_id": "PROFILE-TEACHING-GAP",
            "provenance": "UNKNOWN",
            "held": {"CAP-SIGNED-PAIR": "DEMONSTRATED"},
            "observation_refs": [],
        }
        with patch.object(
            study_session.session_readiness,
            "audit",
            return_value=partial,
        ):
            report = study_session.plan(
                self.mapping(),
                ["Relative motion=60"],
                profile=profile,
            )

        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(
            report["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertIsNone(report["next_step"])
        points = {
            point
            for row in report["owner_decisions"]
            for point in row.get("blocking_points", [])
        }
        self.assertIn("READINESS_TEACHING_PATH_MISSING", points)

    def test_blocked_demanded_rungs_require_owner_decision_not_global_failure(self):
        blocked = {
            "subject": "Physics",
            "matrix_id": "MATRIX-PHY-RELATIVE-MOTION",
            "subtopic": "Relative motion",
            "status": session_readiness.NOT_READY,
            "external_bridges": [],
            "support_findings": [],
            "academic_warnings": [],
            "rungs": [
                {"rung": "R3", "state": "BLOCKED"},
                {"rung": "R4", "state": "BLOCKED"},
                {"rung": "R5", "state": "BLOCKED"},
            ],
            "passed": False,
        }
        profile = {
            "profile_id": "PROFILE-OWNER-DECISION",
            "provenance": "UNKNOWN",
            "held": {"CAP-SIGNED-PAIR": "DEMONSTRATED"},
            "observation_refs": [],
        }
        with patch.object(
            study_session.session_readiness,
            "audit",
            return_value=blocked,
        ):
            report = study_session.plan(
                self.mapping(),
                ["Relative motion=60"],
                profile=profile,
            )

        self.assertTrue(report["passed"], report["findings"])
        self.assertTrue(report["valid"])
        self.assertFalse(report["ready"])
        self.assertEqual(
            report["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertIsNone(report["next_step"])
        self.assertTrue(report["owner_decisions"])

    def test_owner_decision_propagates_to_dependents_but_not_unrelated_branch(self):
        synthetic_plan = {
            "worksheet_id": "SYNTHETIC-FALLBACK",
            "subject": "Physics",
            "profile_id": None,
            "findings": [],
            "warnings": [],
            "blockers": [],
            "valid": True,
            "ready": True,
            "questions": [
                {
                    "question_id": "Q-BLOCKED-BRANCH",
                    "primary_capability_ref": "CAP-B",
                    "secondary_capability_refs": [],
                },
                {
                    "question_id": "Q-INDEPENDENT",
                    "primary_capability_ref": "CAP-C",
                    "secondary_capability_refs": [],
                },
            ],
            "route": [
                {
                    "order": 1,
                    "capability_ref": "CAP-A",
                    "depends_on": [],
                    "state": "RESOLVED",
                    "delivery_state": "LOCAL",
                    "recommended_action": "STUDY",
                    "action_reason": "prerequisite",
                    "locations": [{"matrix_id": "M-A", "rung": "R1"}],
                    "lessons": [],
                },
                {
                    "order": 2,
                    "capability_ref": "CAP-B",
                    "depends_on": ["CAP-A"],
                    "state": "RESOLVED",
                    "delivery_state": "LOCAL",
                    "recommended_action": "STUDY",
                    "action_reason": "question demand",
                    "locations": [{"matrix_id": "M-B", "rung": "R1"}],
                    "lessons": [],
                },
                {
                    "order": 3,
                    "capability_ref": "CAP-C",
                    "depends_on": [],
                    "state": "RESOLVED",
                    "delivery_state": "LOCAL",
                    "recommended_action": "STUDY",
                    "action_reason": "independent question demand",
                    "locations": [{"matrix_id": "M-C", "rung": "R1"}],
                    "lessons": [],
                },
            ],
        }

        readiness = {
            "M-A": {
                "matrix_id": "M-A",
                "subtopic": "A",
                "status": session_readiness.NOT_READY,
                "rungs": [{"rung": "R1", "state": "BLOCKED"}],
                "external_bridges": [],
                "support_findings": [],
                "academic_warnings": [],
            },
            "M-B": {
                "matrix_id": "M-B",
                "subtopic": "B",
                "status": session_readiness.READY,
                "rungs": [{"rung": "R1", "state": "READY"}],
                "external_bridges": [],
                "support_findings": [],
                "academic_warnings": [],
            },
            "M-C": {
                "matrix_id": "M-C",
                "subtopic": "C",
                "status": session_readiness.READY,
                "rungs": [{"rung": "R1", "state": "READY"}],
                "external_bridges": [],
                "support_findings": [],
                "academic_warnings": [],
            },
        }

        def audit(_subject, matrix_id=None, **_kwargs):
            return readiness[matrix_id]

        with patch.object(
            study_session.worksheet_study_plan,
            "resolve",
            return_value=synthetic_plan,
        ), patch.object(
            study_session.session_readiness,
            "audit",
            side_effect=audit,
        ):
            report = study_session.plan(self.mapping())

        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(
            report["execution_disposition"],
            study_session.EXECUTE_WITH_FALLBACK,
        )
        route = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(
            route["CAP-A"]["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertEqual(
            route["CAP-B"]["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertIsNone(route["CAP-C"]["execution_disposition"])
        self.assertEqual(report["next_step"]["capability_ref"], "CAP-C")
        self.assertEqual(report["executable_question_ids"], ["Q-INDEPENDENT"])
        self.assertEqual(
            report["owner_decision_question_ids"],
            ["Q-BLOCKED-BRANCH"],
        )

    def test_owner_can_supply_session_external_bridge_without_mutating_canonical_route(self):
        synthetic_plan = {
            "worksheet_id": "SYNTHETIC-OWNER-BRIDGE",
            "subject": "Physics",
            "profile_id": None,
            "findings": [{
                "point": "STUDY_ROUTE_CAPABILITY_HAS_NO_TEACHING_LOCATION",
                "capability": "CAP-A",
                "detail": "no canonical delivery",
            }],
            "warnings": [],
            "blockers": [],
            "valid": False,
            "ready": False,
            "questions": [{
                "question_id": "Q-B",
                "primary_capability_ref": "CAP-B",
                "secondary_capability_refs": [],
            }],
            "route": [
                {
                    "order": 1,
                    "capability_ref": "CAP-A",
                    "depends_on": [],
                    "state": "UNRESOLVED",
                    "delivery_state": "UNRESOLVED",
                    "recommended_action": "UNRESOLVED",
                    "action_reason": "no canonical delivery",
                    "locations": [],
                    "lessons": [],
                },
                {
                    "order": 2,
                    "capability_ref": "CAP-B",
                    "depends_on": ["CAP-A"],
                    "state": "RESOLVED",
                    "delivery_state": "LOCAL",
                    "recommended_action": "STUDY",
                    "action_reason": "question demand",
                    "locations": [{"matrix_id": "M-B", "rung": "R1"}],
                    "lessons": [{"matrix_id": "M-B", "rung": "R1", "label": "B / R1"}],
                },
            ],
        }
        ready = {
            "matrix_id": "M-B",
            "subtopic": "B",
            "status": session_readiness.READY,
            "rungs": [{"rung": "R1", "state": "READY", "teaching": True, "verification": True}],
            "blocking_findings": [],
            "external_bridges": [],
            "support_findings": [],
            "academic_warnings": [],
        }
        with patch.object(
            study_session.worksheet_study_plan,
            "resolve",
            return_value=synthetic_plan,
        ), patch.object(
            study_session.session_readiness,
            "audit",
            return_value=ready,
        ):
            report = study_session.plan(
                self.mapping(),
                owner_choice_specs=["CAP-A=EXTERNAL:Owner-selected tutor"],
            )

        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["owner_decisions"], [])
        self.assertEqual(
            report["execution_disposition"],
            study_session.EXECUTE_WITH_FALLBACK,
        )
        self.assertEqual(report["next_step"]["action"], "BRIDGE")
        self.assertEqual(
            report["next_step"]["external_provider"],
            "Owner-selected tutor",
        )
        self.assertEqual(report["executable_question_ids"], ["Q-B"])
        self.assertEqual(report["owner_decision_question_ids"], [])
        self.assertEqual(len(report["applied_owner_choices"]), 1)
        self.assertEqual(len(report["owner_resolved_findings"]), 1)
        self.assertEqual(
            report["route"][0]["owner_choice"]["scope"],
            "SESSION_ONLY",
        )

    def test_owner_can_select_one_offered_location_for_session_only(self):
        synthetic_plan = {
            "worksheet_id": "SYNTHETIC-OWNER-LOCATION",
            "subject": "Physics",
            "profile_id": None,
            "findings": [{
                "point": "STUDY_ROUTE_CAPABILITY_AMBIGUOUS_LOCATION",
                "capability": "CAP-A",
                "detail": "two canonical locations exist",
            }],
            "warnings": [],
            "blockers": [],
            "valid": False,
            "ready": False,
            "questions": [{
                "question_id": "Q-A",
                "primary_capability_ref": "CAP-A",
                "secondary_capability_refs": [],
            }],
            "route": [{
                "order": 1,
                "capability_ref": "CAP-A",
                "depends_on": [],
                "state": "AMBIGUOUS",
                "delivery_state": "AMBIGUOUS",
                "recommended_action": "UNRESOLVED",
                "action_reason": "ambiguous delivery",
                "locations": [
                    {"matrix_id": "M-A", "rung": "R1"},
                    {"matrix_id": "M-X", "rung": "R2"},
                ],
                "lessons": [
                    {"matrix_id": "M-A", "rung": "R1", "label": "A / R1"},
                    {"matrix_id": "M-X", "rung": "R2", "label": "X / R2"},
                ],
            }],
        }
        readiness = {
            "M-A": {
                "matrix_id": "M-A",
                "subtopic": "A",
                "status": session_readiness.READY,
                "rungs": [{"rung": "R1", "state": "READY", "teaching": True, "verification": True}],
                "blocking_findings": [],
                "external_bridges": [],
                "support_findings": [],
                "academic_warnings": [],
            },
            "M-X": {
                "matrix_id": "M-X",
                "subtopic": "X",
                "status": session_readiness.READY,
                "rungs": [{"rung": "R2", "state": "READY", "teaching": True, "verification": True}],
                "blocking_findings": [],
                "external_bridges": [],
                "support_findings": [],
                "academic_warnings": [],
            },
        }

        def audit(_subject, matrix_id=None, **_kwargs):
            return readiness[matrix_id]

        with patch.object(
            study_session.worksheet_study_plan,
            "resolve",
            return_value=synthetic_plan,
        ), patch.object(
            study_session.session_readiness,
            "audit",
            side_effect=audit,
        ):
            report = study_session.plan(
                self.mapping(),
                owner_choice_specs=["CAP-A=LOCATION:M-X:R2"],
            )

        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["owner_decisions"], [])
        self.assertEqual(
            report["execution_disposition"],
            study_session.EXECUTE_WITH_FALLBACK,
        )
        self.assertEqual(report["route"][0]["locations"], [{"matrix_id": "M-X", "rung": "R2"}])
        self.assertEqual(report["next_step"]["lesson"]["matrix_id"], "M-X")
        self.assertEqual(report["next_step"]["lesson"]["rung"], "R2")
        self.assertEqual(
            report["route"][0]["owner_choice"]["scope"],
            "SESSION_ONLY",
        )

    def test_wrong_external_question_diagnoses_without_inventing_a_hint(self):
        report = study_session.attempt(
            self.mapping(),
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            response_summary="Subtracted the speeds as scalars and ignored direction.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("hint", report)
        self.assertEqual(report["observation_draft"]["result"], "MISSING")
        self.assertEqual(report["observation_draft"]["question_ref"], "SCHOOL-REL-Q1")
        self.assertEqual(report["review"]["next_review"], "2026-09-19")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")
        prompts = [
            diagnostic["diagnostic_prompt"]
            for option in report["diagnostic_options"]
            for diagnostic in option["diagnostics"]
        ]
        self.assertTrue(prompts)

    def test_local_failure_can_be_repaired_when_an_unfailed_secondary_is_external(self):
        mapping = self.mapping()
        mapping["questions"][0]["secondary_capability_refs"].append(
            "CAP-RIGHT-TRIANGLE"
        )
        report = study_session.attempt(
            mapping,
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            response_summary="Relative-velocity setup failed before the magnitude step.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertEqual(
            [row["capability_ref"] for row in report["external_bridges"]],
            ["CAP-RIGHT-TRIANGLE"],
        )

    def test_explicit_failure_on_external_secondary_still_blocks_local_repair(self):
        mapping = self.mapping()
        mapping["questions"][0]["secondary_capability_refs"].append(
            "CAP-RIGHT-TRIANGLE"
        )
        report = study_session.attempt(
            mapping,
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RIGHT-TRIANGLE",
            error_stage="EXECUTION",
            response_summary="Relative velocity was set up, but the right-triangle magnitude failed.",
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["next_action"], study_session.OWNER_DECISION)
        self.assertEqual(
            report["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertIn(
            "STUDY_SESSION_QUESTION_EXTERNAL_ONLY",
            [row["point"] for row in report["findings"]],
        )

    def test_unattributed_wrong_attempt_with_external_secondary_requires_attribution(self):
        mapping = self.mapping()
        mapping["questions"][0]["secondary_capability_refs"].append(
            "CAP-RIGHT-TRIANGLE"
        )
        report = study_session.attempt(
            mapping,
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            error_stage="UNKNOWN",
            response_summary="Final answer was wrong; failure point is not yet known.",
        )
        self.assertTrue(report["passed"])
        self.assertEqual(report["next_action"], study_session.OWNER_DECISION)
        self.assertEqual(
            report["execution_disposition"],
            study_session.OWNER_DECISION,
        )
        self.assertIn(
            "STUDY_SESSION_QUESTION_EXTERNAL_ONLY",
            [row["point"] for row in report["findings"]],
        )

    def test_confirmed_misconception_repairs_then_uses_fresh_canonical_check(self):
        report = study_session.attempt(
            self.mapping(),
            "SCHOOL-REL-Q1",
            result="INCORRECT",
            when="2026-09-18",
            failed_capability_ref="CAP-RELATIVE-V",
            error_stage="CONCEPT",
            misconception_index=0,
            response_summary="Used scalar speed difference.",
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")
        self.assertEqual(report["repair"]["microtopic_ref"], "MIC-COMMON-INTERVAL")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        verification = report["after_repair"]["verification"]
        self.assertEqual(verification["kind"], "QUESTION")
        self.assertEqual(verification["question_ref"], "Q-AUTHOR-REL-01")
        self.assertNotEqual(verification["question_ref"], "SCHOOL-REL-Q1")

    def test_independent_correct_attempt_without_verification_stays_uncertain(self):
        limited = {
            "subject": "Physics",
            "matrix_id": "MATRIX-PHY-RELATIVE-MOTION",
            "subtopic": "Relative motion",
            "status": session_readiness.NOT_READY,
            "external_bridges": [],
            "support_findings": [],
            "academic_warnings": [],
            "blocking_findings": [{
                "point": "READINESS_VERIFICATION_MISSING",
                "where": "R4",
                "detail": "no canonical fresh verification path",
            }],
            "rungs": [
                {"rung": "R3", "state": "READY", "teaching": True, "verification": True},
                {"rung": "R4", "state": "NEEDS_SUPPORT", "teaching": True, "verification": False},
                {"rung": "R5", "state": "READY", "teaching": True, "verification": True},
            ],
            "passed": False,
        }
        with patch.object(
            study_session.session_readiness,
            "audit",
            return_value=limited,
        ):
            report = study_session.attempt(
                self.mapping(),
                "SCHOOL-REL-Q1",
                result="CORRECT",
                when="2026-09-18",
                error_stage="UNKNOWN",
                help_used="NONE",
                response_summary="Solved independently.",
            )

        self.assertTrue(report["passed"], report.get("findings"))
        self.assertEqual(report["observation_draft"]["help"], "NONE")
        self.assertEqual(report["observation_draft"]["result"], "UNCERTAIN")
        self.assertEqual(
            report["evidence_limited"]["point"],
            "STUDY_SESSION_VERIFICATION_UNAVAILABLE",
        )

    def test_independent_correct_attempt_drafts_evidence_and_review_without_writing(self):
        report = study_session.attempt(
            self.mapping(),
            "SCHOOL-REL-Q1",
            result="CORRECT",
            when="2026-09-18",
            error_stage="UNKNOWN",
            help_used="NONE",
            response_summary="Set observer order, subtracted vectors, checked reversal.",
        )
        self.assertEqual(report["next_action"], "CONTINUE")
        self.assertEqual(report["observation_draft"]["result"], "DEMONSTRATED")
        self.assertEqual(report["observation_draft"]["capability_ref"], "CAP-RELATIVE-V")
        self.assertEqual(report["review"]["next_review"], "2026-09-25")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")

    def test_session_next_step_surfaces_router_without_persisting_it(self):
        independent = {
            "state": "DEMONSTRATED",
            "source": "DIRECT_ATTEMPT",
            "observation_ref": "OBS-INDEPENDENT",
            "when": "2026-09-20T12:00:00Z",
            "help": "NONE",
            "error_stage": None,
        }
        with patch.object(
            study_session.worksheet_study_plan,
            "_profile_state",
            return_value=independent,
        ):
            report = study_session.plan(self.nlm_fbd_mapping())

        self.assertTrue(report["passed"], report["findings"])
        step = report["next_step"]
        self.assertEqual(step["capability_ref"], "CAP-NLM-FBD-BODY-OWNERSHIP")
        self.assertEqual(step["routing_posture"], "READY")
        self.assertEqual(step["starting_support"], "low")
        self.assertEqual(step["exercise_demand"], "PRACTICE")
        self.assertFalse(step["transfer_eligible"])
        self.assertEqual(
            step["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FBD-V0",
        )
        self.assertEqual(step["routing_persistence"], "NOT_WRITTEN")

    def test_starting_visual_does_not_consume_hint_ladder_and_repair_rejoins_verification(self):
        mapping = self.nlm_friction_mapping()
        plan = study_session.plan(mapping)
        route = {row["capability_ref"]: row for row in plan["route"]}
        friction = route["CAP-NLM-FRICTION-QUANT"]
        self.assertEqual(friction["routing_posture"], "REINFORCE")
        self.assertEqual(friction["starting_support"], "medium")
        self.assertEqual(
            friction["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FRICTION-V1",
        )

        first = study_session.attempt(
            mapping,
            "Q-PHY-NLM-2A-FRICTION-STATIC-09",
            result="INCORRECT",
            when="2026-09-20",
            failed_capability_ref="CAP-NLM-FRICTION-QUANT",
            error_stage="CONCEPT",
            attempt_number=1,
            shown_hint_indices=[],
            response_summary="Used mu_s N immediately instead of finding required static friction.",
        )
        self.assertEqual(first["next_action"], "RETRY")
        self.assertEqual(first["hint"]["index"], 0)
        self.assertEqual(first["hint"]["visual_stage_ref"], "VIS-NLM-FRICTION-V2")
        self.assertEqual(first["review"]["next_review"], "2026-09-21")

        second = study_session.attempt(
            mapping,
            "Q-PHY-NLM-2A-FRICTION-STATIC-09",
            result="INCORRECT",
            when="2026-09-20",
            failed_capability_ref="CAP-NLM-FRICTION-QUANT",
            error_stage="CONCEPT",
            attempt_number=2,
            shown_hint_indices=[0],
            response_summary="Still treated the limiting value as the actual friction.",
        )
        self.assertEqual(second["next_action"], "RETRY")
        self.assertEqual(second["hint"]["index"], 1)
        self.assertEqual(second["hint"]["visual_stage_ref"], "VIS-NLM-FRICTION-V3")

        repaired = study_session.attempt(
            mapping,
            "Q-PHY-NLM-2A-FRICTION-STATIC-09",
            result="INCORRECT",
            when="2026-09-20",
            failed_capability_ref="CAP-NLM-FRICTION-QUANT",
            error_stage="CONCEPT",
            attempt_number=3,
            shown_hint_indices=[0, 1],
            attempted_question_refs=["Q-PHY-NLM-2A-FRICTION-STATIC-09"],
            response_summary="Needs reconstruction of the static-friction condition.",
        )
        self.assertEqual(repaired["next_action"], "REPAIR")
        self.assertEqual(repaired["repair"]["repair_ref"], "NLM8-2")
        self.assertEqual(repaired["after_repair"]["next_action"], "VERIFY")
        self.assertNotEqual(
            repaired["after_repair"]["verification"]["question_ref"],
            "Q-PHY-NLM-2A-FRICTION-STATIC-09",
        )
        self.assertEqual(repaired["review"]["next_review"], "2026-09-21")


    def test_question_not_in_supplied_worksheet_is_refused(self):
        report = study_session.attempt(
            self.mapping(),
            "NOT-IN-WORKSHEET",
            result="INCORRECT",
            when="2026-09-18",
        )
        self.assertFalse(report["passed"])
        self.assertEqual(report["next_action"], "STOP")
        self.assertEqual(
            report["findings"][0]["point"],
            "STUDY_SESSION_QUESTION_NOT_IN_WORKSHEET",
        )

    def test_readable_plan_is_parent_oriented_not_raw_json(self):
        report = study_session.plan(self.mapping(), ["Relative motion=60"])
        rendered = study_session.readable_plan(report)
        self.assertIn("Study session", rendered)
        self.assertIn("Subtopic readiness", rendered)
        self.assertIn("Start now", rendered)
        self.assertIn("Ordered study route", rendered)
        self.assertIn("Worksheet questions", rendered)
        self.assertIn("Parent warnings", rendered)
        self.assertIn("External bridge: Mathematics", rendered)


if __name__ == "__main__":
    unittest.main()
