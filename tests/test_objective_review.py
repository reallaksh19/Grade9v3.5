from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools import objective_review as review  # noqa: E402


class ObjectiveReviewMatrix(unittest.TestCase):
    def test_matrix_is_exactly_four_by_seven(self):
        self.assertEqual(review.problems(), [])
        rows = review.load(review.MATRIX_FILE)["cells"]
        self.assertEqual(len(rows), 28)
        self.assertEqual(
            {(row["difficulty_band"], row["demand_family"]) for row in rows},
            {(band, demand) for band in review.BANDS for demand in review.DEMANDS},
        )

    def test_every_cell_resolves_to_agent_ready_hspm_policy(self):
        for band in review.BANDS:
            for demand in review.DEMANDS:
                policy = review.resolve(band, demand)
                self.assertEqual(policy["template_id"], f"QRT-{band}-{demand}")
                self.assertEqual(set(policy["slots"]), {"X", "Y", "Z", "W"})
                self.assertEqual(policy["attempt_first"]["protected_slot"], "W")
                self.assertEqual(policy["hint_objectives"]["REPRESENTATION"]["review_id"], "H1")
                self.assertEqual(policy["hint_objectives"]["KEY_CONCEPT"]["review_id"], "H2")
                self.assertEqual(policy["hint_objectives"]["CRUX"]["review_id"], "H3")
                self.assertEqual(set(policy["figure_policy"]["stage_objectives"]), {"S1", "S2", "S3"})
                self.assertEqual(set(policy["helper_policy"]), {"P1", "P2", "P3"})
                self.assertTrue(all(key in policy["misconception_policy"] for key in ("M1", "M2", "M3")))

    def test_difficulty_changes_posture_not_demand_identity(self):
        direct = review.resolve("D1", "MOD")
        transfer = review.resolve("D4", "MOD")
        self.assertEqual(direct["objective"], transfer["objective"])
        self.assertNotEqual(direct["difficulty_character"], transfer["difficulty_character"])
        self.assertNotEqual(direct["slots"]["W"], transfer["slots"]["W"])

    def test_demand_changes_cognitive_job_at_same_band(self):
        model = review.resolve("D3", "MOD")
        proof = review.resolve("D3", "PRF")
        self.assertNotEqual(model["objective"], proof["objective"])
        self.assertNotEqual(model["hint_objectives"]["CRUX"]["objective"], proof["hint_objectives"]["CRUX"]["objective"])


if __name__ == "__main__":
    unittest.main()
