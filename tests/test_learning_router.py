"""Falsifiers for the session-only evidence -> posture -> declared-support policy."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.library.resolve import build_index, load_packages
from Shared.tools import learner_evidence, learning_router, worksheet_study_plan

REPO = Path(__file__).resolve().parents[1]


class LearningRouterTest(unittest.TestCase):
    def test_frozen_evidence_to_posture_truth_table(self):
        cases = [
            ({"state": "DEMONSTRATED", "independence_proven": True}, "READY", "low"),
            ({"state": "DEMONSTRATED"}, "REINFORCE", "medium"),
            ({"state": "UNCERTAIN", "error_stage": "CONCEPT"}, "REINFORCE", "medium"),
            ({"state": "UNOBSERVED", "error_stage": None}, "REINFORCE", "medium"),
            ({"state": "MISSING", "error_stage": "CONCEPT"}, "REBUILD", "high"),
            ({"state": "MISSING", "error_stage": "SETUP"}, "REBUILD", "high"),
            ({"state": "MISSING", "error_stage": "EXECUTION"}, "REINFORCE", "medium"),
            ({"state": "MISSING", "error_stage": "CARELESS"}, "REINFORCE", "medium"),
        ]
        for evidence, posture, requested in cases:
            with self.subTest(evidence=evidence):
                routed = learning_router.decision(evidence)
                self.assertEqual(routed["routing_posture"], posture)
                self.assertEqual(routed["requested_support"], requested)
                self.assertIsNone(routed["starting_support"])
                self.assertEqual(routed["support_status"], "UNRESOLVED")
                self.assertEqual(routed["persistence"], "NOT_WRITTEN")

    def test_unattributed_missing_remains_conservative_rebuild(self):
        routed = learning_router.decision({"state": "MISSING", "error_stage": None})
        self.assertEqual(routed["routing_posture"], "REBUILD")
        self.assertEqual(routed["requested_support"], "high")

    def test_effective_state_marks_only_explicit_no_help_direct_attempt_independent(self):
        independent = {
            "observation_id": "OBS-ROUTER-INDEPENDENT",
            "capability_ref": "CAP-X",
            "evidence_kind": "DIRECT_ATTEMPT",
            "result": "DEMONSTRATED",
            "help": "NONE",
            "error_stage": "UNKNOWN",
            "when": "2026-09-20T12:00:00Z",
        }
        unknown_help = {**independent, "observation_id": "OBS-ROUTER-UNKNOWN", "help": "UNKNOWN"}
        profile = {"profile_id": "PROFILE-X", "held": {}, "observation_refs": []}

        with patch.object(learner_evidence, "evidence_for_capability", return_value=[independent]):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertTrue(state["independence_proven"])
        self.assertEqual(state["independence_basis"], "DIRECT_ATTEMPT_WITH_NO_HELP")
        self.assertEqual(learning_router.posture_for(state), "READY")

        with patch.object(learner_evidence, "evidence_for_capability", return_value=[unknown_help]):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertFalse(state["independence_proven"])
        self.assertEqual(state["independence_basis"], "NOT_PROVEN")
        self.assertEqual(learning_router.posture_for(state), "REINFORCE")

    def test_effective_state_exposes_chosen_observation_error_stage(self):
        observation = {
            "observation_id": "OBS-ROUTER-1",
            "capability_ref": "CAP-X",
            "evidence_kind": "DIRECT_ATTEMPT",
            "result": "MISSING",
            "help": "NONE",
            "error_stage": "EXECUTION",
            "when": "2026-09-20T12:00:00Z",
        }
        profile = {"profile_id": "PROFILE-X", "held": {}, "observation_refs": []}
        with patch.object(learner_evidence, "evidence_for_capability", return_value=[observation]):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertEqual(state["state"], "MISSING")
        self.assertEqual(state["error_stage"], "EXECUTION")
        self.assertTrue(state["independence_proven"])
        self.assertEqual(learning_router.posture_for(state), "REINFORCE")

    def test_profile_snapshot_demonstration_cannot_become_ready(self):
        routed = learning_router.decision({
            "state": "DEMONSTRATED",
            "source": "PROFILE_DIAGNOSTIC",
            "help": None,
            "error_stage": None,
            "independence_proven": False,
        })
        self.assertEqual(routed["routing_posture"], "REINFORCE")
        self.assertEqual(routed["requested_support"], "medium")

    def test_hinted_demonstration_cannot_become_ready(self):
        observation = {
            "observation_id": "OBS-ROUTER-2",
            "capability_ref": "CAP-X",
            "evidence_kind": "DIRECT_ATTEMPT",
            "result": "DEMONSTRATED",
            "help": "HINT",
            "error_stage": "UNKNOWN",
            "when": "2026-09-20T12:00:00Z",
        }
        profile = {"profile_id": "PROFILE-X", "held": {}, "observation_refs": []}
        with patch.object(learner_evidence, "evidence_for_capability", return_value=[observation]):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertEqual(state["state"], "UNCERTAIN")
        self.assertFalse(state["independence_proven"])
        self.assertEqual(learning_router.posture_for(state), "REINFORCE")

    def test_nlm_family_support_ladder_is_the_availability_authority(self):
        context = learning_router.family_support_context(
            ["MIC-PHY-NLM-FRICTION-QUANT"],
            REPO,
        )
        self.assertEqual(context["status"], "RESOLVED")
        self.assertEqual(context["family_ref"], "MATRIX-PHY-NLM-FIRST-LAW")

        low = learning_router.resolve_support("low", context)
        self.assertEqual(low["starting_support"], "low")
        self.assertEqual(low["support_status"], "RESOLVED")
        self.assertIsNone(low["finding"])

        minimum = learning_router.resolve_support("minimum", context)
        self.assertIsNone(minimum["starting_support"])
        self.assertEqual(minimum["support_status"], "WITHHELD")
        self.assertEqual(
            minimum["finding"]["point"],
            "LEARNING_ROUTER_SUPPORT_UNDECLARED",
        )
        self.assertEqual(
            minimum["finding"]["declared_levels"],
            ["high", "medium", "low"],
        )

    def test_missing_or_ambiguous_family_support_fails_closed(self):
        missing = learning_router.resolve_support(
            "medium",
            {"status": "MISSING", "candidates": []},
        )
        self.assertIsNone(missing["starting_support"])
        self.assertEqual(
            missing["finding"]["point"],
            "LEARNING_ROUTER_SUPPORT_FAMILY_MISSING",
        )

        ambiguous = learning_router.resolve_support(
            "medium",
            {"status": "AMBIGUOUS", "candidates": ["MATRIX-A", "MATRIX-B"]},
        )
        self.assertIsNone(ambiguous["starting_support"])
        self.assertEqual(
            ambiguous["finding"]["point"],
            "LEARNING_ROUTER_SUPPORT_FAMILY_AMBIGUOUS",
        )

    def test_nlm_friction_visual_and_exercise_routing_is_canonical(self):
        records = build_index(load_packages([
            REPO / "Physics/library/phy-nlm-first-law.v1.json"
        ]))
        rebuild = learning_router.route_decision(
            {"state": "MISSING", "error_stage": "CONCEPT"},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=False,
            repo=REPO,
        )
        self.assertEqual(rebuild["requested_support"], "high")
        self.assertEqual(rebuild["starting_support"], "high")
        self.assertEqual(rebuild["support_status"], "RESOLVED")
        self.assertEqual(
            rebuild["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FRICTION-V2",
        )
        self.assertEqual(
            rebuild["recommended_explorer_ref"],
            "ACT-NLM-FRICTION-THRESHOLD",
        )
        self.assertEqual(
            rebuild["exercise_demand"],
            learning_router.GUIDED_RECONSTRUCTION,
        )

        ready = learning_router.route_decision(
            {"state": "DEMONSTRATED", "independence_proven": True, "error_stage": None},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=True,
            repo=REPO,
        )
        self.assertEqual(ready["requested_support"], "low")
        self.assertEqual(ready["starting_support"], "low")
        self.assertEqual(
            ready["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FRICTION-V0",
        )
        self.assertEqual(ready["exercise_demand"], learning_router.TRANSFER)
        self.assertTrue(ready["exercise_question_ref"].startswith("Q-PHY-NLM-"))

        gated = learning_router.route_decision(
            {"state": "DEMONSTRATED", "independence_proven": True, "error_stage": None},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=False,
            repo=REPO,
        )
        self.assertEqual(gated["exercise_demand"], learning_router.PRACTICE)

    def test_routing_does_not_consume_question_hints(self):
        records = build_index(load_packages([
            REPO / "Physics/library/phy-nlm-first-law.v1.json"
        ]))
        question = records["Q-PHY-NLM-2A-FRICTION-STATIC-09"]
        before_hints = [dict(row) for row in question.get("hints", [])]
        before_shown = list(question.get("shown_hint_indices", []) or [])
        learning_router.route_decision(
            {"state": "UNOBSERVED", "independence_proven": False},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=False,
            repo=REPO,
        )
        self.assertEqual(question.get("hints", []), before_hints)
        self.assertEqual(list(question.get("shown_hint_indices", []) or []), before_shown)

    def test_worksheet_route_receives_session_only_router_annotations(self):
        mapping = {
            "worksheet_id": "WS-NLM-ROUTER",
            "subject": "Physics",
            "questions": [{
                "question_id": "Q-PHY-NLM-2A-FRICTION-STATIC-09",
                "primary_capability_ref": "CAP-NLM-FRICTION-QUANT",
                "secondary_capability_refs": ["CAP-NLM-SECOND-LAW"],
                "mapping_basis": "CANONICAL_QUESTION",
                "canonical_question_ref": "Q-PHY-NLM-2A-FRICTION-STATIC-09",
            }],
        }
        report = worksheet_study_plan.resolve(mapping, repo=REPO)
        self.assertTrue(report["passed"], report["findings"])
        route = {row["capability_ref"]: row for row in report["route"]}
        friction = route["CAP-NLM-FRICTION-QUANT"]
        self.assertEqual(friction["routing_posture"], "REINFORCE")
        self.assertEqual(friction["starting_support"], "medium")
        self.assertEqual(
            friction["initial_visual"]["representation_ref"],
            "REP-NLM-FRICTION-THRESHOLD",
        )
        self.assertEqual(
            friction["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FRICTION-V1",
        )
        self.assertEqual(friction["exercise_demand"], learning_router.PRACTICE)
        self.assertEqual(friction["routing_persistence"], "NOT_WRITTEN")


if __name__ == "__main__":
    unittest.main()
