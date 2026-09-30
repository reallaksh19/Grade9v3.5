from __future__ import annotations

from pathlib import Path
import unittest
from unittest.mock import patch

from Shared.tools import render_core


REPO = Path(__file__).resolve().parents[1]
TABLET_CSS = REPO / "public/css/tablet-12-7.css"


class Core2V2TabletRailContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.css = TABLET_CSS.read_text(encoding="utf-8")

    @staticmethod
    def _ctx() -> render_core.Ctx:
        microtopic = {"id": "MIC-A", "title": "Concept A", "primary_capability_ref": "CAP-A"}
        question = {
            "id": "Q-RAIL",
            "original_identifier": "Exam|2026|Paper 1|Physics|Q7",
            "primary_capability_ref": "CAP-A",
            "secondary_capability_refs": [],
            "stem": "Find the requested quantity.",
            "conditions": ["Use the stated model."],
            "figure_refs": ["REP-RAIL"],
            "answer": {"summary": "Verified result", "reasoning": ["Reasoning step"]},
            "response": {"type": "short_text"},
            "hints": [{"text": "Source support", "reveals": "CONCEPT"}],
            "scaffolds": [
                {
                    "text": "Choose the useful representation.",
                    "prompt": "Which representation separates the knowns?",
                    "learner_stage": "REPRESENTATION",
                    "support_kind": "REPRESENT",
                    "reveals": "METHOD",
                    "supports_move_ref": "MOVE-1",
                }
            ],
            "hint_ladder": [
                {"order": 1, "from": "hints[0]"},
                {"order": 2, "from": "scaffolds[0]"},
            ],
        }
        return render_core.Ctx(
            manifest={"product_id": "test-product"},
            packages=[],
            bank=[],
            blueprints={},
            selection_rows={"microtopics": [microtopic], "core2": [question]},
        )

    def test_expanded_core2_uses_bounded_68_32_grid(self):
        self.assertIn('@media (min-width: 1100px)', self.css)
        self.assertIn('article[data-g9-role="CORE2"].g9-stage-support', self.css)
        self.assertIn('grid-template-columns: minmax(0, 2.125fr) minmax(280px, 1fr) !important;', self.css)
        self.assertIn('grid-auto-flow: dense;', self.css)

    def test_source_representation_and_requested_support_share_the_rail(self):
        self.assertIn('> .slot-attempt > figure[data-g9-figure],', self.css)
        self.assertIn('> .slot-support {', self.css)
        self.assertIn('grid-column: 2;', self.css)
        self.assertIn('> .slot-attempt {\n    display: contents;', self.css)

    def test_primary_question_work_and_solution_remain_in_primary_column(self):
        for selector in (
            '[data-g9-block="stem"]',
            '[data-g9-block="conditions"]',
            '> .slot-attempt > .g9-attempt',
            '> .slot-identity',
            '> .slot-solution',
        ):
            self.assertIn(selector, self.css)
        self.assertIn('grid-column: 1;', self.css)

    def test_portrait_and_medium_widths_cancel_two_column_compression(self):
        self.assertIn('@media (max-width: 1099px)', self.css)
        self.assertIn('display: block !important;', self.css)
        self.assertIn('overflow-x: clip;', self.css)
        self.assertIn('max-width: 100%;', self.css)
        self.assertIn('min-width: 0;', self.css)

    def test_renderer_emits_one_representation_not_a_rail_clone(self):
        ctx = self._ctx()
        question = ctx.selection_rows["core2"][0]
        with patch.object(
            render_core,
            "figure",
            return_value='<figure data-g9-figure data-g9-representation="REP-RAIL"></figure>',
        ):
            rendered = render_core.core2(ctx, question)
        self.assertEqual(rendered.count('data-g9-representation="REP-RAIL"'), 1)
        self.assertLess(rendered.index('data-g9-block="stem"'), rendered.index('data-g9-representation="REP-RAIL"'))
        self.assertLess(rendered.index('data-g9-representation="REP-RAIL"'), rendered.index('data-g9-attempt-box'))
        self.assertIn('data-blueprint-slot="support"', rendered)

    def test_support_rail_is_contextual_not_preexpanded(self):
        ctx = self._ctx()
        question = ctx.selection_rows["core2"][0]
        rendered = render_core._core2_support(ctx, question)
        self.assertEqual(rendered.count('<ol data-g9-ladder></ol>'), 2)
        self.assertIn('<template data-g9-rung-payload=', rendered)
        self.assertNotIn('<ol data-g9-ladder><li', rendered)


if __name__ == "__main__":
    unittest.main()
