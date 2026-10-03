from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.tools import question_review_matrix as qrt


REPO = Path(__file__).resolve().parents[1]


class QuestionReviewMatrixTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.vocab = qrt.load(qrt.VOCAB_PATH)
        cls.matrix = qrt.load(qrt.MATRIX_PATH)
        cls.templates = qrt.compile_templates(cls.matrix, cls.vocab)

    def test_vocabulary_has_exactly_seven_subject_neutral_demands(self):
        self.assertEqual(tuple(self.vocab["demands"]), qrt.DEMANDS)
        text = json.dumps(self.vocab)
        self.assertNotIn("Physics", text)
        self.assertNotIn("Chemistry", text)
        self.assertNotIn("Mathematics", text)

    def test_source_contract_is_valid_and_projection_is_current(self):
        self.assertEqual(qrt.validate_contract(self.matrix, self.vocab), [])
        self.assertEqual(qrt.check_paths(), [])

    def test_compiler_emits_exactly_twenty_eight_unique_cells(self):
        self.assertEqual(len(self.templates), 28)
        ids = [row["template_id"] for row in self.templates]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(
            set(ids),
            {f"QRT-{demand}-{band}" for demand in qrt.DEMANDS for band in qrt.BANDS},
        )

    def test_every_cell_has_twelve_semantic_asks_and_protects_w(self):
        for row in self.templates:
            with self.subTest(row["template_id"]):
                self.assertEqual(tuple(row["review"]), qrt.ASKS)
                self.assertIn("Band protection:", row["slots"]["W"])
                self.assertIn(row["band_policy"]["protected_work"], row["slots"]["W"])
                base_w = row["slots"]["W"].split(". Band protection:", 1)[0]
                self.assertIn(base_w, row["review"]["H3"]["question"])
                self.assertIn(row["band_policy"]["protected_work"], row["review"]["P1"]["question"])

    def test_cells_are_semantically_distinct_without_using_ids_as_the_difference(self):
        signatures = [qrt.normalized_signature(row) for row in self.templates]
        self.assertEqual(len(signatures), len(set(signatures)))

    def test_no_numeric_quality_score_contract_exists(self):
        self.assertEqual(qrt.forbidden_score_keys(self.matrix), [])
        for row in self.templates:
            self.assertEqual(qrt.forbidden_score_keys(row), [], row["template_id"])

    def test_missing_demand_and_scoring_mutations_are_refused(self):
        missing = copy.deepcopy(self.matrix)
        del missing["demands"]["JUSTIFY"]
        self.assertTrue(any("matrix demands" in p for p in qrt.validate_contract(missing, self.vocab)))

        scored = copy.deepcopy(self.matrix)
        scored["band_policies"]["D4"]["weight"] = 4
        self.assertTrue(any("numeric-quality scoring" in p for p in qrt.validate_contract(scored, self.vocab)))

    def test_primary_demand_and_band_are_orthogonal_axes(self):
        by_demand = {d: {row["band"] for row in self.templates if row["demand"] == d} for d in qrt.DEMANDS}
        self.assertTrue(all(bands == set(qrt.BANDS) for bands in by_demand.values()))
        by_band = {b: {row["demand"] for row in self.templates if row["band"] == b} for b in qrt.BANDS}
        self.assertTrue(all(demands == set(qrt.DEMANDS) for demands in by_band.values()))

    def test_generated_projection_is_exact_compiler_output(self):
        committed = json.loads(qrt.GENERATED_PATH.read_text(encoding="utf-8"))
        self.assertEqual(committed, qrt.generated_payload(self.matrix, self.vocab))


if __name__ == "__main__":
    unittest.main()
