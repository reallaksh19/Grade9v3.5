"""Selected Physics Core2 figure references must resolve to governed product assets."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
MOTION_MANIFEST = "products/physics/phy-kin-2d-motion.manifest.json"


class Motion2DSourceFigureResolution(unittest.TestCase):
    def test_selected_core2_figures_are_real_product_representations(self):
        manifest = json.loads((REPO / MOTION_MANIFEST).read_text(encoding="utf-8"))
        questions = {}
        for ref in manifest["bank_refs"]:
            bank = json.loads((REPO / ref).read_text(encoding="utf-8"))
            for question in bank["questions"]:
                self.assertNotIn(question["id"], questions, "ambiguous bank question identity")
                questions[question["id"]] = question

        authored = set()
        for ref in manifest["package_refs"]:
            package = json.loads((REPO / ref).read_text(encoding="utf-8"))
            for kind in ("representations", "resources"):
                authored.update(row["id"] for row in package.get(kind, []))

        selected = manifest["selection"]["core2"]
        self.assertTrue(selected, "Motion-in-2D must select genuine source questions")
        self.assertEqual(len(selected), len(set(selected)), "duplicate Core2 selection")
        self.assertFalse(set(selected) - questions.keys(), "selected source question is missing")
        unresolved = {
            question_id: [ref for ref in questions[question_id].get("figure_refs", [])
                          if ref not in authored]
            for question_id in selected
        }
        self.assertFalse(
            {key: refs for key, refs in unresolved.items() if refs},
            "A source figure must be authored and resolvable; never render a phantom ref",
        )


if __name__ == "__main__":
    unittest.main()
