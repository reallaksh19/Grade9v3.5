from __future__ import annotations

from pathlib import Path
import unittest

from Shared.tools import core2_v2, render_core


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
WITNESS_ID = "PYQ-PHY-IITJEE-2011-P2-Q33"


class Core2V2Motion2DIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = render_core.context(MANIFEST)
        cls.questions = {q["id"]: q for q in cls.ctx.selection_rows["core2"]}
        cls.microtopics = {m["id"]: m for m in cls.ctx.selection_rows["microtopics"]}
        cls.question = cls.questions[WITNESS_ID]

    def test_manifest_selects_expected_real_product_shape(self):
        self.assertEqual(self.ctx.manifest["product_id"], "PRODUCT-PHY-KIN-2D-MOTION")
        self.assertEqual(len(self.ctx.selection_rows["microtopics"]), 3)
        self.assertEqual(len(self.ctx.selection_rows["core2"]), 15)
        self.assertIn(WITNESS_ID, self.questions)

    def test_witness_uses_existing_authored_scaffolds_without_reclassifying_them_as_source_hints(self):
        source, authored = core2_v2.split_pre_solution_support(self.question)
        self.assertGreaterEqual(len(authored), 1)
        self.assertTrue(all(row["provenance"] == core2_v2.AUTHORED_CORE2_SUPPORT for row in authored))
        self.assertTrue(all(row["source"].startswith("scaffolds[") for row in authored))
        self.assertTrue(all(row["provenance"] == core2_v2.SOURCE_HINT for row in source))

    def test_witness_has_structured_solution_with_resolved_crux(self):
        rows = core2_v2.project_solution(self.question["answer"])
        self.assertGreaterEqual(len(rows), 1)
        self.assertEqual(sum(1 for row in rows if row["is_crux"]), 1)
        self.assertTrue(all(row["move_id"] for row in rows))
        self.assertTrue(all(row["stage"] in core2_v2.SOLUTION_STAGES for row in rows))

    def test_witness_joins_to_selected_core1a_concept_from_canonical_capability_refs(self):
        join = core2_v2.concept_question_join(
            self.ctx.selection_rows["microtopics"],
            self.ctx.selection_rows["core2"],
        )
        owners = join["question_to_microtopics"][WITNESS_ID]
        self.assertGreaterEqual(len(owners), 1)
        self.assertTrue(all(owner in self.microtopics for owner in owners))
        for owner in owners:
            self.assertIn(WITNESS_ID, join["microtopic_to_questions"][owner])

    def test_canonical_renderer_projects_support_solution_and_exact_concept_link_for_witness(self):
        rendered = render_core.core2(self.ctx, self.question)
        self.assertIn(f'data-g9-question-ref="{WITNESS_ID}"', rendered)
        self.assertIn('data-g9-block="authored_core2_support"', rendered)
        self.assertIn('data-g9-support-provenance="AUTHORED_CORE2_PROMPT_REVEAL"', rendered)
        self.assertIn('data-g9-block="structured_working"', rendered)
        self.assertIn('data-g9-block="concept_navigation"', rendered)
        self.assertNotIn('data-g9-support-reveals="ANSWER"', rendered)

    def test_full_pages_build_contains_witness_and_preserves_exact_cross_core_anchors(self):
        pages, gaps, digest = render_core.build(MANIFEST, "PAGES")
        self.assertEqual(gaps, [])
        self.assertEqual(len(digest), 16)
        core2 = pages["core2.html"]
        core1a = pages["core1a.html"]
        self.assertIn(f'id="{WITNESS_ID}"', core2)
        self.assertIn(f'data-g9-question-ref="{WITNESS_ID}"', core2)
        self.assertIn(f'href="core2.html#{WITNESS_ID}"', core1a)


if __name__ == "__main__":
    unittest.main()
