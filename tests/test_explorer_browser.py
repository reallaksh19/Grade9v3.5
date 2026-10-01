"""The explorer in a real browser at the 12.7-inch viewports: gating, the drawing as the model, the route to its end, and the layout the blueprint promises."""
from __future__ import annotations

import json
import subprocess
import tempfile
import unittest
from pathlib import Path

from Shared.tools import build_test_site, deploy_test
from Shared.tools import explorer_build as eb
from Shared.tools import explorer_model as em
from tests.test_explorer_build import QUESTION, SPEC, brief
from tests.test_tablet_audit import _browser_available

REPO = Path(__file__).resolve().parents[1]
VIEWPORTS = {"landscape": (1366, 854), "landscape-large": (1440, 900), "portrait": (854, 1366), "portrait-large": (900, 1440)}
EXPECTED_EVIDENCE = ["INITIAL_PREDICTION", "MANIPULATION_COMPLETED", "MISCONCEPTION_SIGNATURE", "CONTRADICTION_UNDERSTOOD", "CAUSAL_CHAIN_RECONSTRUCTED",
                     "EQUATION_TESTED", "INVARIANT_RECONSTRUCTED", "BOUNDARY_TEST_RESULT", "SCAFFOLD_FADE_RESULT", "FRESH_TRANSFER_RESULT"]


def run_browser(page: Path, width: int, height: int) -> dict:
    run = subprocess.run(["node", str(REPO / "tests/explorer_browser.cjs"), str(page), str(width), str(height)], capture_output=True, text=True,
                         cwd=REPO, timeout=300)
    if run.returncode:
        raise AssertionError(run.stderr[-2500:])
    return json.loads(run.stdout)


class Explorer(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        why_not = _browser_available()
        if why_not:
            raise unittest.SkipTest(why_not)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.page = Path(cls.tmp.name) / "index.html"
        html, _ = eb.page(json.loads(json.dumps(SPEC)), brief(), {"question": None, "concept": None})
        # as it is deployed: under the TEST header, which pushes the whole page down
        cls.page.write_text(deploy_test._stamp(html, build_test_site.sandbox_bar("../../../")), encoding="utf-8")
        cls.reports = {name: run_browser(cls.page, *size) for name, size in VIEWPORTS.items()}
        cls.floor = em.blueprint()["responsive_policy"]["tablet_12_7"]["figure_min_text_css_px"]

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def each(self):
        for name, report in self.reports.items():
            yield name, report

    def test_the_page_runs_without_an_error_at_every_size(self):
        for name, report in self.each():
            self.assertEqual(report["consoleErrors"], [], name)

    def test_nothing_is_there_to_play_with_before_the_prediction_and_the_controls_unlock_with_it(self):
        for name, report in self.each():
            before, after, gates = report["before"], report["after"], report["gates"]
            self.assertEqual(before["stage"], "CONTEXT", name)
            self.assertTrue(before["slidersDisabled"] and before["lockNote"], name)
            self.assertEqual((before["manipulateElementsShown"], before["contradictElementsShown"], before["deconstructElementsShown"]), (0, 0, 0), name)
            self.assertEqual(before["readoutsShown"], 2, f"{name}: only the givens of the question are shown before anything is predicted")
            self.assertFalse(before["curveDrawn"], name)
            self.assertEqual(before["routeCardsShown"], 1, name)
            self.assertTrue(gates["predictNeedsAChoice"] and gates["predictAfterChoice"], name)
            self.assertTrue(after["slidersEnabled"], name)
            self.assertGreaterEqual(after["manipulateElementsShown"], 1, name)
            self.assertGreater(after["readoutsShown"], before["readoutsShown"], name)
            self.assertFalse(after["curveDrawn"], f"{name}: the whole curve is for the learner to find, not to be shown while manipulating")
            self.assertGreater(after["trailDots"], 0, f"{name}: the graph keeps the positions the learner has visited")

    def test_each_step_waits_for_the_work_it_asks_and_help_comes_after_a_hint(self):
        for name, report in self.each():
            gates = report["gates"]
            self.assertTrue(gates["manipulateNeedsGoals"], name)
            self.assertTrue(gates["showMeNeedsTheHint"] and gates["showMeAfterHint"], name)
            self.assertTrue(gates["reconstructNeedsTesting"], name)
            self.assertTrue(gates["deconstructWaitsForTheQuestion"], name)

    def test_the_drawing_is_the_model_at_every_position_tried(self):
        for name, report in self.each():
            self.assertLess(report["geometry"]["worstPixelError"], 0.2, name)
            self.assertLess(report["geometry"]["worstOracleError"], 1e-9, name)

    def test_the_tempting_model_and_the_mechanism_appear_only_when_asked_for_and_in_the_order_written(self):
        for name, report in self.each():
            self.assertFalse(report["contradict"]["shownBefore"], name)
            self.assertTrue(report["contradict"]["shownAfter"] and report["contradict"]["ghostDrawn"], name)
            order = [set(step) for step in report["deconstruct"]["revealedAfterEachStep"]]
            self.assertEqual(order[0], {"velocity"}, name)
            self.assertTrue(all(a <= b for a, b in zip(order, order[1:])), name)
            self.assertEqual(order[-1], {"velocity", "vxArrow", "vyArrow", "peak"}, name)

    def test_the_equation_the_learner_builds_is_the_measured_value_and_every_invariant_holds_where_tried(self):
        for name, report in self.each():
            self.assertTrue(report["reconstruct"]["equationShown"], name)
            self.assertIn("equal", report["reconstruct"]["verdict"], name)
            self.assertTrue(all("holds" in v for v in report["invariant"]["verdicts"]), name)
            self.assertTrue(report["recall"] and report["boundary"]["takeaway"], name)

    def test_the_supports_come_away_in_three_levels(self):
        for name, report in self.each():
            one, two, three = report["fade"]["levels"]
            self.assertTrue(one["numbersHidden"] and one["mechanismShown"] == 4 and not one["graphHidden"], name)
            self.assertTrue(two["numbersHidden"] and two["mechanismShown"] == 0 and two["graphHidden"] and two["resultShown"] == 1, name)
            self.assertTrue(three["numbersHidden"] and three["graphHidden"] and three["resultShown"] == 0 and three["labelsShown"] == 0, name)
            self.assertTrue(all(level["slidersDisabled"] for level in report["fade"]["levels"]), name)
            self.assertIn("Type a number", report["fade"]["asksForANumber"], name)

    def test_the_fresh_task_is_done_with_the_explorer_closed_and_two_wrong_answers_show_the_working(self):
        for name, report in self.each():
            self.assertTrue(report["transfer"]["stageHidden"] and report["transfer"]["revealedAfterTwoWrong"], name)
            self.assertEqual(report["transferResults"], [False, True, True], name)
            self.assertEqual(report["fadeResults"], [True, True, True], name)
            self.assertTrue(report["done"]["visible"] and report["done"]["stageBack"], name)
            self.assertEqual(len(report["done"]["summary"]), 4, name)

    def test_the_route_leaves_its_evidence_in_the_order_the_standard_asks(self):
        for name, report in self.each():
            kinds = [e for e in report["evidence"] if e in EXPECTED_EVIDENCE]
            self.assertEqual(kinds, EXPECTED_EVIDENCE, name)

    def test_nothing_overflows_the_screen_and_no_learner_text_is_below_the_floor(self):
        for name, report in self.each():
            for step in report["steps"]:
                self.assertEqual(step["overflow"], 0, f"{name} at {step['label']}")
                if step["smallestText"] is not None:
                    self.assertGreaterEqual(step["smallestText"], self.floor, f"{name} at {step['label']}")

    def test_every_control_is_a_touch_target(self):
        for name, report in self.each():
            for step in report["steps"]:
                self.assertGreaterEqual(step["smallestTarget"], 47.5, f"{name} at {step['label']}: {step['smallestTargetIs']}")

    def test_the_head_block_is_short_and_the_button_that_goes_on_is_always_in_reach(self):
        limit = em.blueprint()["responsive_policy"]["tablet_12_7"]["identity_max_px"]
        for name, report in self.each():
            if name.startswith("landscape"):
                self.assertLessEqual(report["layout"]["headHeight"], limit, name)
            for step in report["steps"]:
                if step["label"] in {"done", "transfer"}:
                    continue
                self.assertTrue(step["continueVisible"], f"{name} at {step['label']}: the primary button is out of reach")

    def test_landscape_has_the_route_beside_the_stage_pinned_and_scrolling_inside(self):
        for name in ("landscape", "landscape-large"):
            layout = self.reports[name]["layout"]
            self.assertEqual((layout["mainDisplay"], layout["routePosition"], layout["routeOverflowY"]), ("grid", "sticky", "auto"), name)

    def test_portrait_keeps_the_pictures_and_the_sliders_in_view_while_the_route_scrolls(self):
        for name in ("portrait", "portrait-large"):
            pinned = self.reports[name]["pinned"]
            self.assertGreater(pinned["scrolled"], 0, name)
            self.assertLessEqual(abs(pinned["viewsTop"]), 1, f"{name}: the pictures leave the screen")
            self.assertLessEqual(abs(pinned["controlsTop"] - pinned["viewsBottom"]), 2, f"{name}: the sliders are not under the pictures")
            self.assertEqual(self.reports[name]["layout"]["mainDisplay"], "block", name)


if __name__ == "__main__":
    unittest.main()
