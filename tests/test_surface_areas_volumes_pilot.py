from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
ASSET_DIR = REPO / "Mathematics" / "assets" / "representations"


class SurfaceAreasVolumesPilotSafetyTests(unittest.TestCase):
    def test_core1a_teaching_assets_do_not_embed_owner_question_answers(self):
        forbidden = (
            "294 cm", "880 cm", "946 cm", "550 m", "89.83", "214.5 cm",
            "27 small spheres", "2700", "308 cm",
        )
        for path in sorted(ASSET_DIR.glob("REP-MAT-SAV-*.svg")):
            text = path.read_text(encoding="utf-8")
            with self.subTest(path=path.name):
                for token in forbidden:
                    self.assertNotIn(token, text)

    def test_q5_hemisphere_construction_is_surface_area_not_volume(self):
        package = json.loads(
            (REPO / "Mathematics" / "library" / "surface-areas-and-volumes.v1.json").read_text(encoding="utf-8")
        )
        m = next(row for row in package["microtopics"] if row["id"] == "MIC-MAT-SAV-SPHERE-HEMISPHERE")
        text = json.dumps(m)
        self.assertIn("Curved Inner Surface", m["title"])
        self.assertNotIn("(2/3)", text)
        self.assertNotIn("capacity", text.lower())
        self.assertIn("opening", text.lower())

    def test_issue13_question_bank_declares_explicit_review_bottleneck_route_and_protected_work(self):
        bank = json.loads(
            (REPO / "Mathematics" / "question-bank" / "surface-areas-and-volumes.owner-bank.v1.json")
            .read_text(encoding="utf-8")
        )
        for q in bank["questions"]:
            with self.subTest(question=q["id"]):
                analysis = q["extensions"]["grade9v3:analysis"]
                self.assertTrue(analysis["review_bottleneck"])
                self.assertTrue(analysis["review_route_to_crux"])
                self.assertTrue(analysis["protected_work"])
                self.assertNotEqual(analysis["review_route_to_crux"], analysis["protected_work"])
                self.assertNotIn(q["answer"]["summary"], analysis["review_bottleneck"])


if __name__ == "__main__":
    unittest.main()
