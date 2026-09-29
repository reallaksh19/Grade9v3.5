from __future__ import annotations

import unittest
from pathlib import Path

from Shared.tools import (
    interaction_local_runtime,
    interaction_reuse,
    interaction_shared_claim,
)

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.local.json"


class InteractionSharedClaimTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = interaction_local_runtime.compile_source(SOURCE)
        cls.implementation_ref = cls.local["runtime"]["activity_ref"]

    def evidence(
        self,
        interaction_ref,
        subject_ref,
        binding_ref,
        relation,
        *,
        mode,
        owner_ref=None,
    ):
        shared_binding = None
        if owner_ref:
            shared_binding = {
                "implementation_ref": self.implementation_ref,
                "owner_ref": owner_ref,
            }
        return interaction_reuse.build_evidence(
            interaction_ref=interaction_ref,
            subject_ref=subject_ref,
            runtime_binding_ref=binding_ref,
            mechanic_refs=["residual-feedback"],
            decisions=[{
                "slice_ref": "whole",
                "mode": mode,
                "relation": relation,
                "implementation_ref": self.implementation_ref,
                "evidence_ref": "artifact-shared-claim-test",
            }],
            shared_binding=shared_binding,
        )

    def test_repository_real_evidence_keeps_reused_and_shared_false(self):
        assessment = interaction_shared_claim.assess_repository(self.implementation_ref)
        self.assertEqual(assessment["observed_maturity"], "REUSED")
        self.assertEqual(assessment["decision"], "KEEP_REUSED")
        self.assertFalse(assessment["shared_claim_proven"])
        self.assertIn("MULTIPLE_REAL_CONSUMER_EVIDENCE", assessment["missing_claim_evidence"])
        self.assertIn("CROSS_SUBJECT_CONSUMER_EVIDENCE", assessment["missing_claim_evidence"])
        self.assertIn("JUSTIFIED_SHARED_OWNER", assessment["missing_claim_evidence"])
        policy = assessment["execution_policy"]
        self.assertTrue(policy["advisory_only"])
        self.assertTrue(policy["research_may_continue"])
        self.assertTrue(policy["local_or_reused_delivery_not_blocked"])
        self.assertFalse(policy["promotion_required"])

    def test_current_reused_evidence_cannot_assert_shared(self):
        assessment = interaction_shared_claim.assess_repository(self.implementation_ref)
        with self.assertRaisesRegex(
            interaction_shared_claim.InteractionSharedClaimError,
            "INTERACTION_SHARED_CLAIM_UNPROVEN",
        ):
            interaction_shared_claim.assert_shared(assessment)

    def test_cross_subject_consumers_plus_one_owner_prove_shared_claim(self):
        creator = self.local["reuse_evidence"]
        consumer_a = self.evidence(
            "interaction-a",
            "Mathematics",
            "binding-a",
            "CONSUMES",
            mode="R1",
            owner_ref="Shared/interaction/example-owner",
        )
        consumer_b = self.evidence(
            "interaction-b",
            "Physics",
            "binding-b",
            "COMPOSES",
            mode="R2",
            owner_ref="Shared/interaction/example-owner",
        )
        assessment = interaction_shared_claim.assess_records(
            [creator, consumer_a, consumer_b], self.implementation_ref
        )
        self.assertEqual(assessment["observed_maturity"], "SHARED")
        self.assertEqual(assessment["decision"], "SHARED_CLAIM_PROVEN")
        self.assertTrue(assessment["shared_claim_proven"])
        self.assertEqual(assessment["missing_claim_evidence"], [])
        interaction_shared_claim.assert_shared(assessment)

    def test_cross_subject_lineage_with_ambiguous_owners_does_not_prove_claim(self):
        creator = self.local["reuse_evidence"]
        consumer_a = self.evidence(
            "interaction-a",
            "Mathematics",
            "binding-a",
            "CONSUMES",
            mode="R1",
            owner_ref="Shared/interaction/owner-a",
        )
        consumer_b = self.evidence(
            "interaction-b",
            "Physics",
            "binding-b",
            "COMPOSES",
            mode="R2",
            owner_ref="Shared/interaction/owner-b",
        )
        assessment = interaction_shared_claim.assess_records(
            [creator, consumer_a, consumer_b], self.implementation_ref
        )
        self.assertEqual(assessment["observed_maturity"], "SHARED")
        self.assertEqual(assessment["decision"], "SHARED_CLAIM_UNPROVEN")
        self.assertFalse(assessment["shared_claim_proven"])
        self.assertIn("UNAMBIGUOUS_SHARED_OWNER", assessment["missing_claim_evidence"])

    def test_cross_subject_consumers_without_creator_do_not_prove_claim(self):
        consumer_a = self.evidence(
            "interaction-a",
            "Mathematics",
            "binding-a",
            "CONSUMES",
            mode="R1",
            owner_ref="Shared/interaction/example-owner",
        )
        consumer_b = self.evidence(
            "interaction-b",
            "Physics",
            "binding-b",
            "COMPOSES",
            mode="R2",
            owner_ref="Shared/interaction/example-owner",
        )
        assessment = interaction_shared_claim.assess_records(
            [consumer_a, consumer_b], self.implementation_ref
        )
        self.assertEqual(assessment["observed_maturity"], "SHARED")
        self.assertEqual(assessment["decision"], "SHARED_CLAIM_UNPROVEN")
        self.assertIn("CONCRETE_CREATOR_EVIDENCE", assessment["missing_claim_evidence"])
        self.assertFalse(assessment["shared_claim_proven"])


if __name__ == "__main__":
    unittest.main()
