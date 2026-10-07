from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from Shared.tools import question_difficulty
from Shared.tools import question_review_matrix as qrt


REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence/architectural-recovery/ISS69/phase-d-d05-acceptance-synthesis.v1.json"


class PhaseDAcceptanceSynthesis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.record = json.loads(EVIDENCE.read_text(encoding="utf-8"))

    def test_matrix_is_exact_canonical_four_by_seven(self):
        matrix = self.record["matrix"]
        self.assertEqual(tuple(matrix["bands"]), qrt.BANDS)
        self.assertEqual(tuple(matrix["demands"]), qrt.DEMANDS)
        self.assertEqual(matrix["total_cells"], len(qrt.BANDS) * len(qrt.DEMANDS))
        self.assertEqual(matrix["total_cells"], 28)

    def test_every_candidate_difficulty_is_mechanically_derived(self):
        for row in self.record["candidates"]:
            with self.subTest(subject=row["subject"]):
                difficulty = row["difficulty"]
                derived = question_difficulty.derive(
                    {
                        "band": difficulty["band"],
                        "score": difficulty["score"],
                        "components": difficulty["components"],
                    },
                    question_ref=row["question_ref"],
                )
                self.assertEqual(derived["score"], difficulty["score"])
                self.assertEqual(derived["band"], difficulty["band"])

    def test_only_fresh_normalized_rows_may_even_enter_primary_classification_admission(self):
        fresh = [
            row for row in self.record["candidates"]
            if row["primary_classification"]["status"] == "FRESH_NORMALIZED_CANDIDATE"
        ]
        self.assertEqual(
            [(row["subject"], row["question_ref"]) for row in fresh],
            [("Mathematics", "Q-MAT-LEQ-04-EXEMPLAR9-4-3-Q7")],
        )
        classification = fresh[0]["primary_classification"]
        self.assertEqual(classification["demand"], "MODEL")
        self.assertEqual(classification["qrt_template"], "QRT-MODEL-D2")
        self.assertEqual(classification["crux_move_ref"], "Q37-DEC")

    def test_retained_render_artifacts_have_exact_current_identity(self):
        retained = [
            row for row in self.record["candidates"]
            if row["rendered_binding"]["retained_artifact_id"] is not None
        ]
        self.assertEqual({row["subject"] for row in retained}, {"Mathematics", "Chemistry"})
        for row in retained:
            with self.subTest(subject=row["subject"]):
                binding = row["rendered_binding"]
                self.assertRegex(binding["head_sha"], r"^[0-9a-f]{40}$")
                self.assertIsInstance(binding["run_id"], int)
                self.assertGreater(binding["run_id"], 0)
                self.assertIsInstance(binding["job_id"], int)
                self.assertGreater(binding["job_id"], 0)
                self.assertRegex(binding["retained_artifact_sha256"], r"^[0-9a-f]{64}$")
                self.assertGreater(binding["retained_artifact_id"], 0)

        physics = next(row for row in self.record["candidates"] if row["subject"] == "Physics")
        self.assertEqual(
            physics["rendered_binding"]["status"],
            "CURRENT_EPHEMERAL_BROWSER_RUN_NO_RETAINED_REVIEW_BUNDLE",
        )
        self.assertIsNone(physics["rendered_binding"]["retained_artifact_sha256"])

    def test_missing_independent_reviewer_cannot_be_upgraded_to_acceptance(self):
        for row in self.record["candidates"]:
            with self.subTest(subject=row["subject"]):
                review = row["independent_review"]
                self.assertEqual(review["status"], "MISSING")
                self.assertIsNone(review["reviewer_ref"])
                self.assertFalse(row["accepted"])
                self.assertIn("INDEPENDENT_RENDERED_REVIEW_MISSING", row["rejection_reasons"])

        self.assertEqual(self.record["accepted_rows"], [])
        self.assertFalse(self.record["release_boundary"]["independent_acceptance_granted"])
        self.assertFalse(self.record["release_boundary"]["merge_or_publication_granted"])

    def test_coverage_is_computed_only_from_accepted_rows_and_all_unsupported_cells_are_explicit(self):
        accepted = self.record["accepted_rows"]
        accepted_cells = {
            (row["difficulty"]["band"], row["primary_classification"]["demand"])
            for row in accepted
        }
        all_cells = {(band, demand) for band in qrt.BANDS for demand in qrt.DEMANDS}
        unsupported = {
            (row["band"], row["demand"])
            for row in self.record["coverage"]["unsupported_cells"]
        }
        self.assertEqual(accepted_cells, set())
        self.assertEqual(unsupported, all_cells - accepted_cells)
        self.assertEqual(self.record["coverage"]["accepted_row_count"], 0)
        self.assertEqual(self.record["coverage"]["accepted_cell_count"], 0)
        self.assertEqual(self.record["coverage"]["unsupported_cell_count"], 28)

    def test_historical_replays_contribute_zero_accepted_rows(self):
        excluded = self.record["historical_exclusions"]
        self.assertEqual(excluded["accepted_rows_contributed"], 0)
        self.assertEqual(excluded["status"], "EXCLUDED_FROM_ACCEPTED_COVERAGE")
        self.assertTrue({49, 50, 51, 52, 53, 54, 55, 56} <= set(excluded["issues"]))


if __name__ == "__main__":
    unittest.main()
