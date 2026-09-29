from __future__ import annotations

import unittest
from pathlib import Path

from Shared.tools import interaction_discovery, interaction_local_runtime, interaction_reuse

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.local.json"


class InteractionDiscoveryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.local = interaction_local_runtime.compile_source(SOURCE)
        cls.implementation_ref = cls.local["runtime"]["activity_ref"]

    def test_repository_index_discovers_real_local_witness(self):
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
        self.assertEqual(row["maturity"], "LOCAL")
        self.assertEqual(row["maturity_status"], "OBSERVED")
        self.assertEqual(row["subject_refs"], ["Mathematics"])
        self.assertIn("residual-feedback", row["mechanic_refs"])
        self.assertEqual(row["package_refs"], [self.local["runtime"]["package_ref"]])
        self.assertEqual(
            row["source_paths"],
            ["Mathematics/interactions/linear-equations-two-variables.local.json"],
        )
        self.assertFalse(row["subject_neutral_shared_claim_proven"])

    def test_exact_mechanic_search_finds_precedent_without_ranking(self):
        index = interaction_discovery.build()
        rows = interaction_discovery.search(
            index,
            mechanic_refs=["residual-feedback", "accepted-pair-accumulation"],
        )
        self.assertEqual([row["implementation_ref"] for row in rows], [self.implementation_ref])
        self.assertEqual(
            interaction_discovery.search(index, mechanic_refs=["not-recorded-mechanic"]),
            [],
        )
        self.assertTrue(index["execution_policy"]["unindexed_build_allowed"])

    def test_concrete_consumer_upgrades_index_to_reused_without_promotion_gate(self):
        consumer = interaction_reuse.build_evidence(
            interaction_ref="interaction-consumer",
            subject_ref="Mathematics",
            runtime_binding_ref="binding-consumer",
            mechanic_refs=["residual-feedback"],
            decisions=[{
                "slice_ref": "residual-check",
                "mode": "R1",
                "relation": "CONSUMES",
                "implementation_ref": self.implementation_ref,
                "evidence_ref": "artifact-consumer",
            }],
        )
        index = interaction_discovery.build_from_records([self.local], [consumer])
        row = interaction_discovery.search(
            index, implementation_ref=self.implementation_ref,
        )[0]
        self.assertEqual(row["maturity"], "REUSED")
        self.assertEqual(row["consumer_interaction_refs"], ["interaction-consumer"])
        self.assertTrue(index["execution_policy"]["promotion_not_required"])
        self.assertEqual(row["shared_owner_refs"], [])

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
