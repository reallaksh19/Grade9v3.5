from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence/architectural-recovery/ISS69/phase-d-d06-freeze-handoff.v1.json"


class PhaseDFreezeHandoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_exact_child_pr_inventory_is_complete_and_shared_neutral(self):
        rows = self.record["child_prs"]
        self.assertEqual([row["pr"] for row in rows], [119, 124, 120, 121, 126])
        for row in rows:
            with self.subTest(pr=row["pr"]):
                self.assertRegex(row["head_sha"], r"^[0-9a-f]{40}$")
                self.assertEqual(
                    row["base_sha"],
                    "59751b52e4911a132abb8c3956583a75b3cbcab7",
                )
                self.assertTrue(row["files"])
                self.assertFalse(
                    [path for path in row["files"] if path.startswith("Shared/")],
                    row["files"],
                )
        self.assertEqual(self.record["shared_production_files_changed"], [])

    def test_current_render_receipts_distinguish_retained_and_ephemeral_bytes(self):
        receipts = {row["phase"]: row for row in self.record["render_receipts"]}
        self.assertEqual(set(receipts), {"D01", "D02", "D03"})

        physics = receipts["D01"]
        self.assertEqual(
            physics["binding"],
            "CURRENT_EPHEMERAL_BROWSER_RUN_NO_RETAINED_REVIEW_BUNDLE",
        )
        self.assertIsNone(physics["artifact_sha256"])

        for phase in ("D02", "D03"):
            row = receipts[phase]
            with self.subTest(phase=phase):
                self.assertEqual(row["binding"], "CURRENT_RETAINED_CI_ARTIFACT")
                self.assertRegex(row["artifact_sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(row["artifact_id"], 0)
                self.assertGreater(row["workflow_run_id"], 0)
                self.assertGreater(row["job_id"], 0)

    def test_broad_guardrail_deltas_add_no_phase_d_failure_signatures(self):
        deltas = self.record["broad_guardrail_deltas"]
        self.assertEqual({row["phase"] for row in deltas}, {"D01", "D02", "D03", "D04", "D05"})
        for row in deltas:
            with self.subTest(phase=row["phase"]):
                self.assertEqual(row["base_unique_failure_or_error_tests"], 112)
                self.assertEqual(row["head_unique_failure_or_error_tests"], 112)
                self.assertEqual(row["added"], [])
                self.assertEqual(row["removed"], [])
                self.assertTrue(row["signature_identical"])

    def test_acceptance_summary_imports_d05_without_promoting_any_cell(self):
        acceptance = self.record["acceptance_summary"]
        self.assertEqual(acceptance["source_issue"], 113)
        self.assertEqual(acceptance["source_pr"], 126)
        self.assertEqual(acceptance["accepted_row_count"], 0)
        self.assertEqual(acceptance["accepted_cell_count"], 0)
        self.assertEqual(acceptance["unsupported_cell_count"], 28)
        self.assertFalse(acceptance["independent_acceptance_granted"])
        self.assertFalse(acceptance["merge_or_publication_granted"])

    def test_returned_findings_are_explicit_and_not_silently_closed(self):
        rows = {row["id"]: row for row in self.record["returned_findings"]}
        expected = {
            "ISS108_GENERATED_ARTIFACT_DRIFT",
            "D01_RENDER_BYTES_NOT_RETAINED",
            "D03_CORE1A_MIN_TEXT_11PX",
            "D05_INDEPENDENT_REVIEW_MISSING",
            "APPENDIX_A_PROMOTION_AUTHORITY_SEPARATE",
        }
        self.assertTrue(expected <= set(rows))
        self.assertEqual(rows["ISS108_GENERATED_ARTIFACT_DRIFT"]["status"], "OPEN_BLOCKS_PHASE_E_FINAL")
        self.assertEqual(rows["D03_CORE1A_MIN_TEXT_11PX"]["status"], "REVIEW_REQUIRED")
        self.assertEqual(rows["APPENDIX_A_PROMOTION_AUTHORITY_SEPARATE"]["status"], "TECHNICAL_BROWSER_COMPLETE_PROMOTION_SEPARATE")

    def test_phase_e_handoff_preserves_non_grants_and_real_blocker(self):
        handoff = self.record["phase_e_handoff"]
        self.assertEqual(handoff["issue"], 75)
        self.assertIn(108, handoff["blocking_issues"])
        self.assertFalse(handoff["merge_to_main_granted"])
        self.assertFalse(handoff["golden_promotion_granted"])
        self.assertFalse(handoff["learner_publication_granted"])
        self.assertFalse(handoff["learning_effectiveness_claimed"])

        result = self.record["task_result"]
        self.assertEqual(result["RESULT_SCOPE"], "RESPONSIBILITY")
        self.assertEqual(result["COVERAGE"], "architectural recovery programme #69 / Phase D")
        self.assertEqual(result["RESPONSIBILITY_COMPLETE"], "YES")


if __name__ == "__main__":
    unittest.main()
