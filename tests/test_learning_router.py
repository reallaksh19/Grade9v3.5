"""Falsifiers for the session-only evidence -> posture -> support policy."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from Shared.tools import learner_evidence, learning_router


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


if __name__ == "__main__":
    unittest.main()
