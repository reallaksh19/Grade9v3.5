from __future__ import annotations

import json
from pathlib import Path
import unittest
from unittest.mock import patch

from Shared.tools import render_core


REPO = Path(__file__).resolve().parents[1]


class Core2V2TabletRailContract(unittest.TestCase):
    """The Core2 layout is the blueprint's: its columns, fractions and breakpoint become CSS, its slots become columns."""

    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((REPO / "Shared/web/interactive-page-blueprints.v1.json").read_text(encoding="utf-8"))
        cls.css = render_core.layout_css(cls.registry)
        cls.blueprint = next(bp for bp in cls.registry["blueprints"] if "CORE2" in bp["core_roles"])

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

    def test_expanded_core2_layout_is_written_from_the_blueprint(self):
        policy = self.blueprint["responsive_policy"]
        self.assertEqual((policy["primary_fraction"], policy["support_fraction"]), (0.42, 0.58))
        self.assertIn(f'@media (min-width:{policy["expanded_min_px"]}px)', self.css)
        self.assertIn('article[data-g9-role="CORE2"] .g9-split{display:grid;'
                      'grid-template-columns:minmax(0,42fr) minmax(0,58fr)', self.css)

    def test_core1a_layout_is_its_own_blueprints_with_a_sticky_support_column(self):
        core1a = next(bp for bp in self.registry["blueprints"] if "CORE1A" in bp["core_roles"])
        self.assertTrue(core1a["responsive_policy"]["support_sticky"])
        self.assertIn('article[data-g9-role="CORE1A"] .g9-split{display:grid;'
                      'grid-template-columns:minmax(0,68fr) minmax(0,32fr)', self.css)
        self.assertIn('article[data-g9-role="CORE1A"] .g9-split:not(.g9-split-support-only)>.g9-col-support{position:sticky', self.css)

    def test_every_blueprint_slot_has_a_column_and_below_the_breakpoint_nothing_is_a_grid(self):
        for bp in self.registry["blueprints"]:
            for slot in bp["slots"]:
                self.assertIn(slot.get("column"), {"FULL", "PRIMARY", "SUPPORT"}, (bp["id"], slot["id"]))
        for rule in self.css.split("@media"):
            if "grid-template-columns" in rule and "print" not in rule.split("{")[0]:
                self.assertIn("(min-width:", rule.split("{")[0])

    def test_source_representation_and_requested_support_share_the_support_column(self):
        columns = {slot["id"]: slot["column"] for slot in self.blueprint["slots"]}
        self.assertEqual(columns, {"identity": "FULL", "attempt": "PRIMARY", "representation": "SUPPORT",
                                   "support": "SUPPORT", "solution": "FULL"})

    def test_renderer_emits_one_representation_in_the_support_column(self):
        ctx = self._ctx()
        ctx.blueprints = self.registry
        question = ctx.selection_rows["core2"][0]

        def fake_figure(_ctx, rep_id, *_args, **_kwargs):
            if not rep_id:
                return ""
            return f'<figure data-g9-figure data-g9-representation="{rep_id}"></figure>'

        with patch.object(render_core, "figure", side_effect=fake_figure):
            rendered = render_core.core2(ctx, question)
        self.assertEqual(rendered.count('data-g9-representation="REP-RAIL"'), 1)
        primary = rendered[rendered.index('g9-col-primary'):rendered.index('g9-col-support')]
        support = rendered[rendered.index('g9-col-support'):]
        self.assertIn('data-g9-block="stem"', primary)
        self.assertIn('data-g9-attempt-box', primary)
        self.assertIn('data-g9-representation="REP-RAIL"', support)
        self.assertIn('data-g9-component="HINT_LADDER"', support)
        self.assertLess(support.index('data-g9-component="REPRESENTATION"'), support.index('data-g9-component="HINT_LADDER"'))
        self.assertIn('data-blueprint-slot="support"', rendered)

    def test_without_a_blueprint_the_slots_still_render_in_one_flow(self):
        ctx = self._ctx()
        rendered = render_core.core2(ctx, ctx.selection_rows["core2"][0])
        self.assertNotIn("g9-split", rendered)
        self.assertIn('data-blueprint-slot="attempt"', rendered)

    def test_support_rail_is_contextual_not_preexpanded(self):
        ctx = self._ctx()
        question = ctx.selection_rows["core2"][0]
        rendered = render_core._core2_support(ctx, question)
        self.assertEqual(rendered.count('<ol data-g9-ladder></ol>'), 2)
        self.assertIn('<template data-g9-rung-payload=', rendered)
        self.assertNotIn('<ol data-g9-ladder><li', rendered)


if __name__ == "__main__":
    unittest.main()
