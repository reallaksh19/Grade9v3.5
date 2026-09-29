from __future__ import annotations

import unittest

from Shared.tools import interaction_reuse


class InteractionReuseTests(unittest.TestCase):
    def evidence(
        self,
        interaction_ref,
        subject_ref,
        binding_ref,
        decisions,
        *,
        mechanics=("MECH-DRAG",),
        shared_binding=None,
    ):
        return interaction_reuse.build_evidence(
            interaction_ref=interaction_ref,
            subject_ref=subject_ref,
            runtime_binding_ref=binding_ref,
            mechanic_refs=list(mechanics),
            decisions=decisions,
            shared_binding=shared_binding,
        )

    def test_one_interaction_can_have_mixed_r1_r2_r3_r4_paths(self):
        record = self.evidence(
            "INTERACTION-MIXED",
            "SUBJECT-A",
            "BINDING-MIXED",
            [
                {"slice_ref": "S1", "mode": "R1", "relation": "CONSUMES", "implementation_ref": "IMPL-PICK", "evidence_ref": "ART-PICK"},
                {"slice_ref": "S2", "mode": "R2", "relation": "COMPOSES", "implementation_ref": "IMPL-KEYBOARD", "evidence_ref": "ART-KEYBOARD"},
                {"slice_ref": "S3", "mode": "R3", "relation": "EXTENDS", "implementation_ref": "IMPL-ADAPTER", "evidence_ref": "ART-ADAPTER"},
                {"slice_ref": "S4", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-LOCAL-SCENE", "evidence_ref": None},
            ],
        )
        summary = interaction_reuse.interaction_summary(record)
        self.assertEqual(summary["modes_present"], ["R1", "R2", "R3", "R4"])
        self.assertTrue(summary["mixed_path"])
        self.assertEqual(len(summary["decisions"]), 4)

    def test_new_real_implementation_is_local_without_promotion_requirement(self):
        created = self.evidence(
            "INTERACTION-A",
            "SUBJECT-A",
            "BINDING-A",
            [{"slice_ref": "SCENE", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        result = interaction_reuse.analyse_implementation([created], "IMPL-A")
        self.assertEqual(result["maturity"], "LOCAL")
        self.assertEqual(result["maturity_status"], "OBSERVED")
        self.assertEqual(result["creator_interaction_refs"], ["INTERACTION-A"])
        self.assertEqual(result["consumer_interaction_refs"], [])
        self.assertFalse(result["subject_neutral_shared_claim_proven"])

    def test_later_real_consumer_makes_lineage_reused(self):
        created = self.evidence(
            "INTERACTION-A",
            "SUBJECT-A",
            "BINDING-A",
            [{"slice_ref": "SCENE", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        consumer = self.evidence(
            "INTERACTION-B",
            "SUBJECT-A",
            "BINDING-B",
            [{"slice_ref": "MECHANIC", "mode": "R3", "relation": "EXTENDS", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        result = interaction_reuse.analyse_implementation([created, consumer], "IMPL-A")
        self.assertEqual(result["maturity"], "REUSED")
        self.assertEqual(result["consumer_interaction_refs"], ["INTERACTION-B"])

    def test_two_similar_independent_creations_are_duplication_not_reuse(self):
        first = self.evidence(
            "INTERACTION-A",
            "SUBJECT-A",
            "BINDING-A",
            [{"slice_ref": "SCENE", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        second = self.evidence(
            "INTERACTION-B",
            "SUBJECT-B",
            "BINDING-B",
            [{"slice_ref": "SCENE", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-B", "evidence_ref": "ART-B"}],
        )
        self.assertEqual(interaction_reuse.analyse_implementation([first, second], "IMPL-A")["maturity"], "LOCAL")
        self.assertEqual(interaction_reuse.analyse_implementation([first, second], "IMPL-B")["maturity"], "LOCAL")
        opportunities = interaction_reuse.duplication_opportunities([first, second])
        self.assertEqual(len(opportunities), 1)
        self.assertEqual(opportunities[0]["disposition"], "DUPLICATION_OPPORTUNITY_ONLY")
        self.assertEqual(opportunities[0]["maturity_effect"], "NONE_WITHOUT_LINEAGE")

    def test_shared_claim_requires_owner_two_consumers_and_cross_subject_evidence(self):
        created = self.evidence(
            "INTERACTION-A",
            "SUBJECT-A",
            "BINDING-A",
            [{"slice_ref": "BASE", "mode": "R4", "relation": "CREATES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        consumer_one = self.evidence(
            "INTERACTION-B",
            "SUBJECT-A",
            "BINDING-B",
            [{"slice_ref": "USE", "mode": "R1", "relation": "CONSUMES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
        )
        consumer_two_same_subject = self.evidence(
            "INTERACTION-C",
            "SUBJECT-A",
            "BINDING-C",
            [{"slice_ref": "USE", "mode": "R2", "relation": "COMPOSES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
            shared_binding={"implementation_ref": "IMPL-A", "owner_ref": "SHARED-OWNER"},
        )
        same_subject = interaction_reuse.analyse_implementation(
            [created, consumer_one, consumer_two_same_subject], "IMPL-A"
        )
        self.assertEqual(same_subject["maturity"], "REUSED")
        self.assertFalse(same_subject["subject_neutral_shared_claim_proven"])

        consumer_two_other_subject = self.evidence(
            "INTERACTION-C",
            "SUBJECT-B",
            "BINDING-C",
            [{"slice_ref": "USE", "mode": "R2", "relation": "COMPOSES", "implementation_ref": "IMPL-A", "evidence_ref": "ART-A"}],
            shared_binding={"implementation_ref": "IMPL-A", "owner_ref": "SHARED-OWNER"},
        )
        cross_subject = interaction_reuse.analyse_implementation(
            [created, consumer_one, consumer_two_other_subject], "IMPL-A"
        )
        self.assertEqual(cross_subject["maturity"], "SHARED")
        self.assertTrue(cross_subject["subject_neutral_shared_claim_proven"])
        self.assertEqual(cross_subject["shared_owner_refs"], ["SHARED-OWNER"])

    def test_missing_lineage_is_unobserved_reconstruction_debt_not_local_claim(self):
        result = interaction_reuse.analyse_implementation([], "IMPL-UNKNOWN")
        self.assertIsNone(result["maturity"])
        self.assertEqual(result["maturity_status"], "UNOBSERVED")
        self.assertEqual(result["reconstruction_debt"], ["NO_IMPLEMENTATION_LINEAGE_EVIDENCE"])
        self.assertIn("local itself requires evidence", result["claim_note"].lower())

    def test_mode_relation_mismatch_is_rejected(self):
        with self.assertRaisesRegex(interaction_reuse.InteractionReuseError, "MODE_RELATION_INVALID"):
            self.evidence(
                "INTERACTION-BAD",
                "SUBJECT-A",
                "BINDING-BAD",
                [{"slice_ref": "BAD", "mode": "R4", "relation": "CONSUMES", "implementation_ref": "IMPL-A", "evidence_ref": None}],
            )


if __name__ == "__main__":
    unittest.main()
