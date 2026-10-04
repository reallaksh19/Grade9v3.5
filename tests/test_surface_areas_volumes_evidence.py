from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence" / "reviews" / "surface-areas-and-volumes"


class SurfaceAreasVolumesEvidenceSeparationTests(unittest.TestCase):
    def test_authoring_record_is_not_presented_as_render_review(self):
        authoring = json.loads((EVIDENCE / "question-pedagogy.v1.json").read_text(encoding="utf-8"))
        review = json.loads((EVIDENCE / "qrt-review-evidence.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(authoring["schema"], "question-pedagogy-batch/v1")
        self.assertEqual(authoring["status"], "PENDING_OWNER_PROFILE")
        self.assertEqual(review["schema"], "qrt-render-review-batch/v1")
        self.assertEqual(review["status"], "PENDING_EXACT_RENDER")
        self.assertIsNone(review["render_basis"]["core2_html_sha256"])
        self.assertIsNone(review["render_basis"]["core1a_html_sha256"])
        self.assertEqual(review["product_review_projection"]["status"], "NOT_EMITTED")

    def test_all_y_slots_are_unresolved_until_owner_profile_exists(self):
        authoring = json.loads((EVIDENCE / "question-pedagogy.v1.json").read_text(encoding="utf-8"))
        self.assertEqual(len(authoring["items"]), 10)
        for item in authoring["items"]:
            self.assertEqual(item["slots"]["Y"]["state"], "UNRESOLVED_OWNER_INPUT")
            self.assertNotEqual(item["slots"]["Z"]["text"], item["slots"]["W"]["text"])

    def test_review_has_no_fake_acceptance_or_verdicts_before_exact_render(self):
        review = json.loads((EVIDENCE / "qrt-review-evidence.v1.json").read_text(encoding="utf-8"))
        text = json.dumps(review).lower()
        self.assertNotIn("accept_with_notes", text)
        self.assertNotIn('"overall"', text)
        self.assertTrue(all(item["verdicts"] == {} for item in review["items"]))


if __name__ == "__main__":
    unittest.main()
