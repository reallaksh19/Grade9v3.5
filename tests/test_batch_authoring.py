from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import batch_authoring

REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "Mathematics" / "question-bank" / "surface-areas-and-volumes.owner-bank.v1.json"
PROFILE = REPO / "evidence" / "reviews" / "surface-areas-and-volumes" / "learner-profile.v1.json"


class BatchAuthoringTests(unittest.TestCase):
    def test_surface_areas_volumes_compiles_all_ten_qrts_before_render(self):
        result = batch_authoring.compile_batch(
            json.loads(BANK.read_text(encoding="utf-8")),
            json.loads(PROFILE.read_text(encoding="utf-8")),
            "Mathematics",
            "PRODUCT-MAT-G9-SAV",
            "https://github.com/reallaksh19/Grade9v3.5/issues/13",
        )
        self.assertEqual(result["schema"], "question-pedagogy-batch/v1")
        self.assertEqual(result["status"], "PENDING_OWNER_PROFILE")
        self.assertEqual(len(result["items"]), 10)
        self.assertEqual({row["question_ref"] for row in result["items"]}, {f"Q{i}" for i in range(1, 11)})
        for item in result["items"]:
            self.assertTrue(item["template_id"].startswith("QRT-"))
            self.assertEqual(item["slots"]["Y"]["state"], "UNRESOLVED_OWNER_INPUT")
            self.assertEqual(item["slots"]["X"]["state"], "RESOLVED")
            self.assertEqual(item["slots"]["Z"]["state"], "RESOLVED")
            self.assertEqual(item["slots"]["W"]["state"], "RESOLVED")
            self.assertNotEqual(item["slots"]["Z"]["text"], item["slots"]["W"]["text"])
            self.assertEqual(len(item["authoring"]["hint_objectives"]), 3)
            self.assertTrue(item["authoring"]["solution_architecture"])

    def test_product_id_is_an_explicit_orchestration_input(self):
        result = batch_authoring.compile_batch(
            json.loads(BANK.read_text(encoding="utf-8")),
            json.loads(PROFILE.read_text(encoding="utf-8")),
            "Mathematics",
            "PRODUCT-OTHER",
            "issue:test",
        )
        self.assertEqual(result["product_id"], "PRODUCT-OTHER")


if __name__ == "__main__":
    unittest.main()
