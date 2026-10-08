"""Fail-closed pre-attempt SVG disclosure: protect the learner's decisive move (W)."""
from __future__ import annotations

import unittest
from unittest.mock import patch

from Shared.tools import render_core


class StagedSvgDisclosure(unittest.TestCase):
    @staticmethod
    def _render(svg: str, *, allowed=None, stages=None):
        rep = {
            "id": "REP-W",
            "kind": "DIAGRAM",
            "purpose": "Protected result W = 42",
            "rendered_asset_refs": ["fixture.svg"],
            "reveal_stages": stages if stages is not None else [
                {"id": "S1", "label": "Given"},
                {"id": "S2", "label": "Solution"},
            ],
        }
        ctx = render_core.Ctx(
            manifest={"product_id": "SVG-NEGATIVE-FIXTURE"},
            packages=[{"representations": [rep]}],
            bank=[],
            blueprints={},
        )
        with patch.object(render_core, "asset_svg", return_value=svg):
            rendered = render_core.figure(
                ctx, "REP-W", "PRE_ATTEMPT", "CORE2", "Q-W",
                first_stage_only=True, allowed=allowed,
            )
        return rendered, ctx.gaps

    @staticmethod
    def _svg(first: str, second: str, *, nested=False, quote="'"):
        visible = f"<g data-g9-stage-id={quote}S1{quote}><text>Given setup</text>"
        secret = f"<g data-g9-stage-id={second}S2{second}><text>W = 42</text></g>"
        if nested:
            groups = visible + secret + "</g>"
        else:
            groups = visible + "</g>" + secret
        return (
            "<svg xmlns='http://www.w3.org/2000/svg' aria-label='W = 42'>"
            "<title>W = 42</title><desc>Protected W = 42</desc>"
            + groups + "</svg>"
        )

    def test_double_single_and_mixed_quoted_stage_attributes_remove_secret_bytes(self):
        for first_quote, second_quote in [('"', '"'), ("'", "'"), ('"', "'"), ("'", '"')]:
            with self.subTest(first=first_quote, second=second_quote):
                svg = self._svg(first_quote, second_quote)
                rendered, gaps = self._render(svg)
                self.assertEqual(gaps, [])
                self.assertIn("Given setup", rendered)
                self.assertNotIn("W = 42", rendered)
                self.assertNotIn("data-g9-stage-id=" + second_quote + "S2", rendered)
                self.assertEqual(rendered.count('data-g9-stage-id='), 1)

    def test_nested_withheld_stage_and_descendants_are_removed(self):
        svg = (
            "<svg aria-label='Teaching diagram'><title>Title</title><desc>Full figure</desc>"
            "<g data-g9-stage-id='S1'><text>Given setup</text>"
            "<g data-g9-stage-id='S2'><g><text>W = 42</text></g></g>"
            "</g></svg>"
        )
        rendered, gaps = self._render(svg)
        self.assertEqual(gaps, [])
        self.assertIn("Given setup", rendered)
        self.assertNotIn("W = 42", rendered)
        self.assertNotIn("data-g9-stage-id='S2'", rendered)

    def test_malformed_staged_svg_fails_closed(self):
        svg = (
            "<svg aria-label='Figure'><title>Figure</title><desc>Figure stages</desc>"
            "<g data-g9-stage-id='S1'>Given</g>"
            "<g data-g9-stage-id='S2'><text>W = 42</text>"
            "</svg>"
        )
        rendered, gaps = self._render(svg)
        self.assertEqual(rendered, "")
        self.assertTrue(any(gap["duty"] == "BUILD_SCENE" for gap in gaps), gaps)

    def test_stage_marker_on_non_group_fails_closed(self):
        svg = (
            "<svg aria-label='Figure'><title>Figure</title><desc>Figure stages</desc>"
            "<g data-g9-stage-id='S1'><text>Given</text></g>"
            "<text data-g9-stage-id='S2'>W = 42</text></svg>"
        )
        rendered, gaps = self._render(svg)
        self.assertEqual(rendered, "")
        self.assertTrue(gaps)

    def test_requested_stage_missing_from_selected_asset_fails_closed(self):
        svg = (
            "<svg aria-label='Figure'><title>Figure</title><desc>Figure stages</desc>"
            "<g data-g9-stage-id='S1'><text>Given</text></g></svg>"
        )
        rendered, gaps = self._render(svg, allowed=["S2"])
        self.assertEqual(rendered, "")
        self.assertTrue(gaps)

    def test_catalogue_may_describe_stages_not_present_in_selected_scene(self):
        # One representation may have several question-specific assets.
        # Catalogued labels are not permission to display missing/other stages.
        svg = (
            "<svg aria-label='Figure'><title>Figure</title><desc>Figure stages</desc>"
            "<g data-g9-stage-id='S1'><text>Given</text></g></svg>"
        )
        rendered, gaps = self._render(svg, allowed=["S1"])
        self.assertEqual(gaps, [])
        self.assertIn("Given", rendered)
        self.assertNotIn("W = 42", rendered)

    def test_explicit_empty_allowlist_shows_no_figure(self):
        svg = self._svg('"', '"')
        rendered, gaps = self._render(svg, allowed=[])
        self.assertEqual(rendered, "")
        self.assertEqual(gaps, [])


if __name__ == "__main__":
    unittest.main()
