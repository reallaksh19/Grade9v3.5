from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import interaction_local_runtime, interaction_reuse_binding

REPO = Path(__file__).resolve().parents[1]
LOCAL_SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.local.json"
CONSUMER_SOURCE = REPO / "Mathematics/interactions/linear-equations-two-variables.test-pairs.reuse-consumer.json"


class InteractionReuseBindingTests(unittest.TestCase):
    def test_real_canonical_question_consumes_same_runtime_package_unchanged(self):
        local = interaction_local_runtime.compile_source(LOCAL_SOURCE)
        reused = interaction_reuse_binding.compile_source(CONSUMER_SOURCE)

        self.assertEqual(reused["status"], "CURRENT")
        self.assertEqual(reused["consumer_ref"], "Q-MAT-LEQ-04-1A-TEST-PAIRS")
        self.assertEqual(
            reused["consumer_primary_capability_ref"],
            "CAP-MAT-LEQ-04-TWO-VARIABLE-SOLUTIONS",
        )
        self.assertEqual(reused["runtime"], local["runtime"])
        self.assertEqual(
            reused["reuse_evidence"]["runtime_binding_ref"],
            local["runtime"]["binding_ref"],
        )
        decision = reused["reuse_evidence"]["decisions"][0]
        self.assertEqual(decision["mode"], "R1")
        self.assertEqual(decision["relation"], "CONSUMES")
        self.assertEqual(decision["implementation_ref"], local["runtime"]["activity_ref"])
        self.assertEqual(decision["evidence_ref"], local["runtime"]["package_ref"])
        self.assertEqual(reused["reuse_analysis"]["maturity"], "REUSED")
        self.assertEqual(
            reused["reuse_analysis"]["consumer_interaction_refs"],
            ["Q-MAT-LEQ-04-1A-TEST-PAIRS"],
        )
        self.assertFalse(reused["reuse_analysis"]["subject_neutral_shared_claim_proven"])
        self.assertEqual(reused["reuse_analysis"]["shared_owner_refs"], [])

    def test_consumer_with_mismatched_primary_capability_fails_closed(self):
        source = json.loads(CONSUMER_SOURCE.read_text(encoding="utf-8"))
        source["consumer_ref"] = "Q-MATH-CONSTRAINT-1A"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "mismatch.reuse-consumer.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            with self.assertRaisesRegex(
                interaction_reuse_binding.InteractionReuseBindingError,
                "CONSUMER_CAPABILITY_MISMATCH",
            ):
                interaction_reuse_binding.compile_source(path)

    def test_binding_is_deterministic_and_freshness_detects_source_drift(self):
        first = interaction_reuse_binding.compile_source(CONSUMER_SOURCE)
        second = interaction_reuse_binding.compile_source(CONSUMER_SOURCE)
        self.assertEqual(first, second)
        self.assertEqual(
            interaction_reuse_binding.freshness(first, CONSUMER_SOURCE)["status"],
            "CURRENT",
        )

        source = json.loads(CONSUMER_SOURCE.read_text(encoding="utf-8"))
        source["slice_ref"] = "changed-slice"
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "changed.reuse-consumer.json"
            path.write_text(json.dumps(source), encoding="utf-8")
            self.assertEqual(
                interaction_reuse_binding.freshness(first, path)["status"],
                "STALE",
            )


if __name__ == "__main__":
    unittest.main()
