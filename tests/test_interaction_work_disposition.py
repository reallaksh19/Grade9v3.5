from __future__ import annotations

import unittest

from Shared.tools import interaction_work_disposition, web_resolver


MOTION = "MATRIX-PHY-KIN-2D-MOTION"
MATH = "MATRIX-MATH-LINEAR-EQUATIONS"


def request(subject, target, *, interaction="REQUIRED"):
    return {
        "schema_version": "1.0.0",
        "request_id": f"TEST-WORK-{subject}",
        "subject": subject,
        "target": dict(target),
        "experience_segments": [{
            "mode": "EXPLORE",
            "interaction_requirement": interaction,
        }],
        "packaging_mode": "PUBLIC",
    }


class InteractionWorkDispositionTests(unittest.TestCase):
    def test_missing_required_interaction_becomes_local_build_work_not_agent_hold(self):
        plan = web_resolver.resolve(request(
            "Mathematics", {"matrix_ref": MATH, "rung": "R1"},
        ))
        # Merged-#284 delivery truth still says the requested interactive artifact is not ready.
        self.assertEqual(plan["request_satisfaction"], "RESEARCH_AND_AUTHOR")
        self.assertTrue(any(
            row["code"] == "WEB_REQUIRED_INTERACTION_UNAVAILABLE"
            for row in plan["findings"]
        ))

        disposition = interaction_work_disposition.classify(plan)
        self.assertTrue(disposition["research_may_continue"])
        self.assertEqual(disposition["action"], "BUILD_LOCAL_OR_REUSABLE")
        self.assertEqual(
            disposition["learner_completion_state"],
            "ENGINEERING_IMPLEMENTATION_REQUIRED",
        )
        self.assertEqual(disposition["academic_findings"], [])
        self.assertTrue(disposition["engineering_findings"])
        self.assertIn("deterministic governed", disposition["runtime_invariant"])

    def test_existing_governed_interaction_uses_resolved_delivery(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        disposition = interaction_work_disposition.classify(plan)
        self.assertEqual(disposition["action"], "USE_RESOLVED_DELIVERY")
        self.assertEqual(disposition["learner_completion_state"], "DELIVERY_RESOLVED")

    def test_unresolved_academic_identity_limits_learner_completion_but_not_research(self):
        plan = web_resolver.resolve(request(
            "Mathematics", {"exact_ref": "MIC-DOES-NOT-EXIST"},
        ))
        disposition = interaction_work_disposition.classify(plan)
        self.assertTrue(disposition["research_may_continue"])
        self.assertEqual(disposition["action"], "RESEARCH_ACADEMIC_GAP_AND_PROTOTYPE")
        self.assertEqual(
            disposition["learner_completion_state"],
            "ACADEMICALLY_UNRESOLVED",
        )
        self.assertTrue(any(
            row["code"] == "WEB_CANONICAL_REF_INVALID"
            for row in disposition["academic_findings"]
        ))

    def test_stale_interaction_brief_is_academic_handoff_debt_not_research_permission(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
        ))
        disposition = interaction_work_disposition.classify(
            plan,
            brief_freshness={"status": "STALE", "brief_id": "IBR-TEST"},
        )
        self.assertTrue(disposition["research_may_continue"])
        self.assertEqual(disposition["action"], "RESEARCH_ACADEMIC_GAP_AND_PROTOTYPE")
        self.assertTrue(any(
            row["code"] == "INTERACTION_BRIEF_NOT_CURRENT"
            for row in disposition["academic_findings"]
        ))

    def test_missing_reuse_metadata_is_explicitly_reconstruction_debt(self):
        plan = web_resolver.resolve(request(
            "Mathematics", {"matrix_ref": MATH, "rung": "R1"},
        ))
        disposition = interaction_work_disposition.classify(plan)
        self.assertIn("reconstruction debt", disposition["evidence_note"])
        self.assertNotIn("permission", disposition["evidence_note"].lower())


if __name__ == "__main__":
    unittest.main()
