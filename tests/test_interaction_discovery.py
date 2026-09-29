from __future__ import annotations

import unittest
from pathlib import Path

from Shared.tools import (
    interaction_discovery,
    interaction_local_runtime,
    interaction_reuse,
    interaction_reuse_binding,
)

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.local.json"
CONSUMER_SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.test-pairs.reuse-consumer.json"


class InteractionDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = interaction_local_runtime.compile_source(SOURCE)
        cls.consumer = interaction_reuse_binding.compile_source(CONSUMER_SOURCE)
        cls.implementation_ref = cls.local["runtime"]["activity_ref"]

    def test_repository_index_discovers_real_reused_witness(self):
        index = interaction_discovery.build()
        self.assertEqual(index["authority"], "DERIVED_INTERACTION_DISCOVERY_ONLY")
        policy = index["execution_policy"]
        self.assertTrue(policy["advisory_only"])
        self.assertTrue(policy["research_may_continue"])
        self.assertTrue(policy["unindexed_build_allowed"])
        self.assertTrue(policy["promotion_not_required"])
        self.assertTrue(policy["similarity_is_not_reuse_evidence"])

        rows = interaction_discovery.search(
            index,
            implementation_ref=self.implementation_ref,
        )
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["maturity"], "REUSED")
        self.assertEqual(row["maturity_status"], "OBSERVED")
        self.assertEqual(row["subject_refs"], ["Mathematics"])
        self.assertIn("residual-feedback", row["mechanic_refs"])
        self.assertEqual(row["package_refs"], [self.local["runtime"]["package_ref"]])
        self.assertEqual(
            row["source_paths"],
            ["Mathematics/interactions/linear-equations-two-variables.local.json"],
        )
        self.assertEqual(
            row["consumer_interaction_refs"],
            ["Q-MAT-LEQ-04-1A-TEST-PAIRS"],
        )
        self.assertEqual(row["consumer_subject_refs"], ["Mathematics"])
        self.assertFalse(row["subject_neutral_shared_claim_proven"])
        self.assertEqual(row["shared_owner_refs"], [])
        self.assertIn(
            "Mathematics/interactions/linear-equations-two-variables.test-pairs.reuse-consumer.json",
            index["source_inventory"]["reuse_consumer_source_paths"],
        )

    def test_real_consumer_keeps_same_runtime_identity(self):
        self.assertEqual(self.consumer["runtime"], self.local["runtime"])
        self.assertEqual(
            self.consumer["reuse_evidence"]["runtime_binding_ref"],
            self.local["runtime"]["binding_ref"],
        )
        decision = self.consumer["reuse_evidence"]["decisions"][0]
        self.assertEqual(decision["implementation_ref"], self.implementation_ref)
        self.assertEqual(decision["evidence_ref"], self.local["runtime"]["package_ref"])

    def test_exact_mechanic_search_finds_precedent_without_ranking(self):
        index = interaction_discovery.build()
        rows = interaction_discovery.search(
            index,
            mechanic_refs=["residual-feedback", "accepted-pair-accumulation"],
        )
        self.assertEqual([row["implementation_ref"] for row in rows], [self.implementation_ref])
        self.assertEqual(rows[0]["maturity"], "REUSED")
        self.assertEqual(
            interaction_discovery.search(index, mechanic_refs=["not-recorded-mechanic"]),
            [],
        )
        self.assertTrue(index["execution_policy"]["unindexed_build_allowed"])

    def test_concrete_additional_consumer_remains_reused_without_promotion_gate(self):
        additional_consumer = interaction_reuse.build_evidence(
            interaction_ref="interaction-consumer-two",
            subject_ref="Mathematics",
            runtime_binding_ref=self.local["runtime"]["binding_ref"],
            mechanic_refs=["residual-feedback"],
            decisions=[{
                "slice_ref": "residual-check",
                "mode": "R1",
                "relation": "CONSUMES",
                "implementation_ref": self.implementation_ref,
                "evidence_ref": self.local["runtime"]["package_ref"],
            }],
        )
        index = interaction_discovery.build_from_records(
            [self.local],
            [self.consumer["reuse_evidence"], additional_consumer],
        )
        row = interaction_discovery.search(
            index, implementation_ref=self.implementation_ref,
        )[0]
        self.assertEqual(row["maturity"], "REUSED")
        self.assertEqual(
            row["consumer_interaction_refs"],
            ["Q-MAT-LEQ-04-1A-TEST-PAIRS", "interaction-consumer-two"],
        )
        self.assertTrue(index["execution_policy"]["promotion_not_required"])
        self.assertEqual(row["shared_owner_refs"], [])
        self.assertFalse(row["subject_neutral_shared_claim_proven"])

    def test_independent_lookalikes_remain_duplication_opportunity_not_reuse(self):
        first = interaction_reuse.build_evidence(
            interaction_ref="interaction-a",
            subject_ref="subject-a",
            runtime_binding_ref="binding-a",
            mechanic_refs=["candidate-mechanic"],
            decisions=[{
                "slice_ref": "whole",
                "mode": "R4",
                "relation": "CREATES",
                "implementation_ref": "implementation-a",
                "evidence_ref": "artifact-a",
            }],
        )
        second = interaction_reuse.build_evidence(
            interaction_ref="interaction-b",
            subject_ref="subject-b",
            runtime_binding_ref="binding-b",
            mechanic_refs=["candidate-mechanic"],
            decisions=[{
                "slice_ref": "whole",
                "mode": "R4",
                "relation": "CREATES",
                "implementation_ref": "implementation-b",
                "evidence_ref": "artifact-b",
            }],
        )
        index = interaction_discovery.build_from_records([], [first, second])
        self.assertEqual(len(index["duplication_opportunities"]), 1)
        opportunity = index["duplication_opportunities"][0]
        self.assertEqual(opportunity["disposition"], "DUPLICATION_OPPORTUNITY_ONLY")
        self.assertEqual(opportunity["maturity_effect"], "NONE_WITHOUT_LINEAGE")
        maturities = {
            row["implementation_ref"]: row["maturity"]
            for row in index["implementations"]
        }
        self.assertEqual(maturities, {
            "implementation-a": "LOCAL",
            "implementation-b": "LOCAL",
        })

    def test_index_digest_is_deterministic(self):
        first = interaction_discovery.build()
        second = interaction_discovery.build()
        self.assertEqual(first["index_digest"], second["index_digest"])
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
