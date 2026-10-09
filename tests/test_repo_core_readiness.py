"""The repository-wide readout must not invent six-Core or QRT acceptance."""
from __future__ import annotations

import unittest

from Shared.tools.repo_core_readiness import project


def fixtures():
    qrt = [
        {"template_id": f"QRT-{demand}-{band}"}
        for demand in ("RETRIEVE", "EXPLAIN", "APPLY", "MODEL", "REPRESENT", "SYNTHESIZE", "JUSTIFY")
        for band in ("D1", "D2", "D3", "D4")
    ]
    c1 = {
        "summary": {
            "bucket_count": 21, "core1_orientable_buckets": 21,
            "microtopic_count": 91, "cross_progression_coherent_microtopics": 90,
            "cross_progression_gap_microtopics": 1, "unrouted_microtopics": 1,
            "phase2_local_debt_microtopics": 89,
        },
        "microtopics": [
            {"microtopic_ref": "MIC-HOLD", "cross_progression_codes": ["CROSS_CORE_ROUTING_UNRESOLVED"]},
            {"microtopic_ref": "MIC-OK", "cross_progression_codes": []},
        ],
    }
    c1b = {"summary": {
        "routed_microtopics": 90, "structured_routed_microtopics": 90,
        "coverage_mismatches": 0,
    }}
    c2 = {
        "summary": {
            "practice_families": 25, "source_demand_evidenced_families": 3,
            "ordinary_core2_anchors": 0, "competitive_bank_accepted_anchors_scanned": 77,
        },
        "findings": [{"point": "CORE_PROGRESSION_TRANSFER_PARENT_MISSING", "where": "Q-HOLD"}],
    }
    c2a = {"summary": {"core2a_questions": 84, "structured": 20, "migration_required": 64}}
    c2b = {"summary": {
        "core2b_questions": 47, "structured_protected": 30,
        "debt_items": 32, "debt_reasons": {"PROTECTED_DECISION_MIGRATION_REQUIRED": 32},
    }}
    return [qrt, [], c1, c1b, c2, c2a, c2b]


class SixCoreReadinessTests(unittest.TestCase):
    def test_exact_28_cell_12_ask_projection_does_not_claim_academic_acceptance(self):
        report = project(*fixtures(), head="abcdef0")
        self.assertEqual(report["qrt"]["base_template_count"], 28)
        self.assertEqual(len(report["qrt"]["semantic_ask_ids"]), 12)
        self.assertTrue(report["qrt"]["mechanical_contract_valid"])
        self.assertEqual(report["qrt"]["accepted_cells"], "NOT_EVALUATED")
        self.assertEqual(report["qrt"]["independent_exact_render_reviews"], "NOT_EVALUATED")
        self.assertEqual(report["release"]["integrated_six_role_journey"], "NOT_EVALUATED")

    def test_debt_source_and_transfer_are_not_renamed_success(self):
        report = project(*fixtures(), head=None)
        self.assertEqual(report["core1_continuity"]["cross_progression_gap"], 1)
        self.assertEqual(report["core1_continuity"]["core1a_local_construction_debt"], 89)
        self.assertEqual(report["core2_progression"]["ordinary_core2_custody_anchors"], 0)
        self.assertEqual(report["core2_progression"]["core2b_current_debt_items"], 32)
        self.assertFalse(report["gate_semantics"]["competitive_bank_evidence_is_ordinary_core2_custody"])
        self.assertFalse(report["gate_semantics"]["core2b_label_is_proof_of_changed_decision"])
        self.assertEqual(report["core2_progression"]["cross_findings"][0]["where"], "Q-HOLD")

    def test_bad_qrt_does_not_hide_but_preserves_inventory(self):
        args = fixtures()
        args[1] = ["QRT projection not fresh"]
        report = project(*args, head="sha")
        self.assertFalse(report["qrt"]["mechanical_contract_valid"])
        self.assertEqual(report["qrt"]["contract_problems"], ["QRT projection not fresh"])
        self.assertEqual(report["core2_progression"]["core2a_structured"], 20)


if __name__ == "__main__":
    unittest.main()
