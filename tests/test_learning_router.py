"""Falsifiers for the session-only evidence -> posture -> support policy."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.library.resolve import build_index, load_packages
from Shared.tools import learner_evidence, learning_router, worksheet_study_plan

REPO = Path(__file__).resolve().parents[1]


class LearningRouterTest(unittest.TestCase):
    def test_frozen_evidence_to_posture_and_support_truth_table(self):
        cases = [
            ({"state": "DEMONSTRATED", "error_stage": None}, "READY", "low"),
            ({"state": "UNCERTAIN", "error_stage": "CONCEPT"}, "REINFORCE", "medium"),
            ({"state": "UNOBSERVED", "error_stage": None}, "REINFORCE", "medium"),
            ({"state": "MISSING", "error_stage": "CONCEPT"}, "REBUILD", "high"),
            ({"state": "MISSING", "error_stage": "SETUP"}, "REBUILD", "high"),
            ({"state": "MISSING", "error_stage": "EXECUTION"}, "REINFORCE", "medium"),
            ({"state": "MISSING", "error_stage": "CARELESS"}, "REINFORCE", "medium"),
        ]
        for evidence, posture, support in cases:
            with self.subTest(evidence=evidence):
                routed = learning_router.decision(evidence)
                self.assertEqual(routed["routing_posture"], posture)
                self.assertEqual(routed["starting_support"], support)
                self.assertEqual(routed["persistence"], "NOT_WRITTEN")

    def test_unattributed_missing_remains_conservative_rebuild(self):
        routed = learning_router.decision({"state": "MISSING", "error_stage": None})
        self.assertEqual(routed["routing_posture"], "REBUILD")
        self.assertEqual(routed["starting_support"], "high")

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
        with patch.object(
            learner_evidence,
            "evidence_for_capability",
            return_value=[observation],
        ):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertEqual(state["state"], "MISSING")
        self.assertEqual(state["error_stage"], "EXECUTION")
        self.assertEqual(learning_router.posture_for(state), "REINFORCE")

    def test_profile_snapshot_demonstration_cannot_become_ready(self):
        routed = learning_router.decision({
            "state": "DEMONSTRATED",
            "source": "PROFILE_DIAGNOSTIC",
            "help": None,
            "error_stage": None,
        })
        self.assertEqual(routed["routing_posture"], "REINFORCE")
        self.assertEqual(routed["starting_support"], "medium")

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
        with patch.object(
            learner_evidence,
            "evidence_for_capability",
            return_value=[observation],
        ):
            state = learner_evidence.effective_state(profile, "CAP-X")
        self.assertEqual(state["state"], "UNCERTAIN")
        self.assertEqual(learning_router.posture_for(state), "REINFORCE")

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
        )
        self.assertEqual(rebuild["starting_support"], "high")
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
            {"state": "DEMONSTRATED", "error_stage": None},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=True,
        )
        self.assertEqual(ready["starting_support"], "low")
        self.assertEqual(
            ready["initial_visual"]["visual_stage_ref"],
            "VIS-NLM-FRICTION-V0",
        )
        self.assertEqual(ready["exercise_demand"], learning_router.TRANSFER)
        self.assertTrue(ready["exercise_question_ref"].startswith("Q-PHY-NLM-"))

        gated = learning_router.route_decision(
            {"state": "DEMONSTRATED", "error_stage": None},
            capability_ref="CAP-NLM-FRICTION-QUANT",
            microtopic_refs=["MIC-PHY-NLM-FRICTION-QUANT"],
            records=records,
            prerequisites_ready=False,
        )
        self.assertEqual(gated["exercise_demand"], learning_router.PRACTICE)

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
