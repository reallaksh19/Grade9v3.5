"""The explorer in a real browser at the 12.7-inch viewports: gating, the drawing as the model, the route to its end, and the layout the blueprint promises."""
from __future__ import annotations

import json
import os
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


def run_browser(page: Path, width: int, height: int, env: dict | None = None) -> dict:
    run = subprocess.run(["node", str(REPO / "tests/explorer_browser.cjs"), str(page), str(width), str(height)], capture_output=True, text=True,
                         cwd=REPO, timeout=300, env={**os.environ, **(env or {})})
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

    def test_every_control_and_picture_has_a_name_and_the_numbers_do_not_talk_over_a_reader(self):
        for name, report in self.each():
            a11y = report["a11y"]
            self.assertEqual(a11y["unnamed"], [], name)
            self.assertEqual(a11y["liveOutputs"], 0, f"{name}: a readout that is a live region speaks at every slider move")
            self.assertEqual(a11y["lang"], "en", name)
            self.assertEqual((a11y["headings"], a11y["landmarks"]), (1, [1, 1, 1]), name)
            self.assertTrue(all(p["role"] == "img" and p["named"] and p["described"] for p in a11y["pictures"]), name)

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


def every_kind(spec: dict) -> dict:
    """The reference spec with one element of each kind the vocabulary has, a vertical guide and a reversed arc added to it."""
    spec["scene"]["elements"] += [
        {"id": "wedge", "kind": "polygon", "role": "helper", "points": [["0", "0"], ["vx/2", "0"], ["vx/2", "vy/2"]], "label": "wedge", "reveal": "deconstruct"},
        {"id": "ring", "kind": "circle", "role": "frame", "center": ["R/2", "H"], "r": 1.5, "label": "peak"},
        {"id": "note", "kind": "text", "role": "result", "at": [30, 19], "text": "range {R:1} m", "anchor": "end", "reveal": "manipulate"},
        {"id": "back", "kind": "arc", "role": "given", "center": [0, 0], "r": 9, "from_deg": "theta", "to_deg": 0, "label": "back"},
        {"id": "rim", "kind": "curve", "role": "helper", "param": "u", "t_min": 0, "t_max": 6.2832, "steps": 24, "x": "40 + 1.5*cos(u)", "y": "17 + 1.5*sin(u)", "label": "rim"},
    ]
    spec["deconstruct"]["steps"][0]["reveals"].append("wedge")
    spec["second_view"]["guides"].append({"expr": "45", "label": "best at {theta:0}", "orient": "v"})
    spec["second_view"]["guides"].append({"expr": "Rmax/2", "label": "half of {Rmax:0} m", "orient": "h"})
    return spec


def two_sliders(spec: dict) -> dict:
    """The reference spec with the launch speed a slider as well: two parameters move, so the states are a grid and the picture must hold for all of them."""
    spec["parameters"][0] = {"id": "v", "label": "launch speed", "unit": "m/s", "min": 10, "max": 30, "step": 2, "value": 20}
    spec["scene"]["world"] = {"x": [-2, 94], "y": [-3, 47]}
    spec["scene"]["elements"][0]["to"] = ["94", "0"]
    for element in spec["scene"]["elements"]:
        if element["id"] == "angleArc":
            element["r"] = "10"
    return spec


class TwoSliders(unittest.TestCase):
    """Two sliders: the claims are checked over a grid of positions, and the page is driven through its route by moving either."""

    @classmethod
    def setUpClass(cls):
        why_not = _browser_available()
        if why_not:
            raise unittest.SkipTest(why_not)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.spec = two_sliders(json.loads(json.dumps(SPEC)))
        cls.check = em.check(cls.spec, {"question_ref": "Q-PROJ-8", "label": "Q8", "rule": "x"})
        html, _ = eb.page(em.normalize(cls.spec), brief(), {"question": None, "concept": None})
        cls.page = Path(cls.tmp.name) / "index.html"
        cls.page.write_text(html, encoding="utf-8")
        cls.report = run_browser(cls.page, 1366, 854)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_claims_hold_over_the_grid_of_both_sliders(self):
        self.assertEqual([f.line() for f in self.check.errors], [])
        self.assertEqual(self.check.evidence["states_checked"], 81 * 11)
        self.assertEqual(self.check.evidence["observations"], ["sometimes", "always", "always", "never"])

    def test_the_route_is_driven_to_its_end_with_no_script_error_and_the_drawing_is_the_model(self):
        self.assertEqual(self.report["consoleErrors"], [])
        self.assertTrue(self.report["done"]["visible"])
        self.assertLess(self.report["geometry"]["worstPixelError"], 0.2)
        self.assertLess(self.report["geometry"]["worstOracleError"], 1e-9)

    def test_two_sliders_still_leave_the_primary_button_in_reach_and_the_controls_big_enough(self):
        for step in self.report["steps"]:
            if step["label"] not in {"done", "transfer"}:
                self.assertTrue(step["continueVisible"], step["label"])
            self.assertGreaterEqual(step["smallestTarget"], 47.5, step["label"])

    def test_a_picture_that_cannot_hold_the_faster_throws_is_an_error_naming_the_element_and_the_position(self):
        spec = two_sliders(json.loads(json.dumps(SPEC)))
        spec["scene"]["world"] = {"x": [-2, 44], "y": [-3, 47]}
        found = [f.line() for f in em.check(spec, {"question_ref": "Q-PROJ-8", "label": "Q8", "rule": "x"}).errors]
        self.assertTrue(any(line.startswith("SCENE element landing: reaches (") and "right of the picture" in line and "v = " in line for line in found), found)


class EveryKind(unittest.TestCase):
    """Each element kind and each guide the vocabulary has, drawn and driven in a browser: nothing breaks and the drawing is the model."""

    @classmethod
    def setUpClass(cls):
        why_not = _browser_available()
        if why_not:
            raise unittest.SkipTest(why_not)
        cls.tmp = tempfile.TemporaryDirectory()
        cls.spec = every_kind(json.loads(json.dumps(SPEC)))
        report = em.check(cls.spec, {"question_ref": "Q-PROJ-8", "label": "Q8", "rule": "x"})
        cls.findings = [f.line() for f in report.errors]
        html, _ = eb.page(em.normalize(cls.spec), brief(), {"question": None, "concept": None})
        cls.page = Path(cls.tmp.name) / "index.html"
        cls.page.write_text(html, encoding="utf-8")
        cls.report = run_browser(cls.page, 1366, 854)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_the_spec_with_every_kind_has_no_error(self):
        self.assertEqual(self.findings, [])

    def test_every_kind_is_drawn_without_a_script_error_and_the_route_reaches_its_end(self):
        self.assertEqual(self.report["consoleErrors"], [])
        self.assertTrue(self.report["done"]["visible"])

    def test_the_drawing_is_still_the_model(self):
        self.assertLess(self.report["geometry"]["worstPixelError"], 0.2)

    def test_no_label_of_any_kind_is_below_the_floor_or_off_the_screen(self):
        for step in self.report["steps"]:
            if step["smallestText"] is not None:
                self.assertGreaterEqual(step["smallestText"], 14, step["label"])
            self.assertEqual(step["overflow"], 0, step["label"])


if __name__ == "__main__":
    unittest.main()


class CollinearLabels(unittest.TestCase):
    """A sum of two vectors drawn along one line (an explorer a Sonnet-low agent wrote for the toughest vectors question): at 0 and 180 degrees
    the labels of five arrows fall in one row; at no position of the slider may two labels sit on one another."""

    @classmethod
    def setUpClass(cls):
        why_not = _browser_available()
        if why_not:
            raise unittest.SkipTest(why_not)
        cls.tmp = tempfile.TemporaryDirectory()
        spec = json.loads((REPO / "tests/fixtures/explorer/vectors-sum.explorer.json").read_text(encoding="utf-8"))
        html, _ = eb.page(em.normalize(spec), brief(), {"question": None, "concept": None})
        cls.page = Path(cls.tmp.name) / "index.html"
        cls.page.write_text(html, encoding="utf-8")
        cls.reports = {name: run_browser(cls.page, *size) for name, size in {"landscape": (1366, 854), "portrait": (854, 1366)}.items()}

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_no_two_labels_sit_on_one_another_at_any_position(self):
        for name, report in self.reports.items():
            self.assertGreaterEqual(report["labels"]["positions"], 30, name)
            self.assertEqual(report["labels"]["worstOverlap"], 0, (name, report["labels"]["worst"]))

    def test_the_route_still_runs_to_its_end(self):
        for name, report in self.reports.items():
            self.assertEqual(report["consoleErrors"], [], name)
            self.assertTrue(report["done"]["visible"], name)


class Persistence(unittest.TestCase):
    """The route survives a reload: what the learner did is done again, quietly, so the page comes back where it was; Start over forgets it."""

    @classmethod
    def setUpClass(cls):
        why_not = _browser_available()
        if why_not:
            raise unittest.SkipTest(why_not)
        cls.tmp = tempfile.TemporaryDirectory()
        root = Path(cls.tmp.name)
        links = {"question": None, "concept": None}
        html, _ = eb.page(json.loads(json.dumps(SPEC)), brief(), links)
        rebuilt = json.loads(json.dumps(SPEC))
        rebuilt["title"] += " (rebuilt)"
        (root / "a.html").write_text(html, encoding="utf-8")
        (root / "b.html").write_text(eb.page(rebuilt, brief(), links)[0], encoding="utf-8")
        cls.reload_run = run_browser(root / "a.html", 1366, 854, {"GX_PERSIST": "1"})
        cls.no_storage = run_browser(root / "a.html", 1366, 854, {"GX_NOSTORE": "1"})
        run = subprocess.run(["node", str(REPO / "tests/explorer_persist.cjs"), str(root / "a.html"), str(root / "b.html")], capture_output=True, text=True,
                             cwd=REPO, timeout=300)
        if run.returncode:
            raise AssertionError(run.stderr[-2500:])
        cls.scenes = json.loads(run.stdout)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_after_every_step_a_reload_brings_back_the_same_page(self):
        rows = self.reload_run["persist"]
        self.assertEqual(len(rows), 12, "one reload after each of the eleven steps and one in the middle of the fresh tasks")
        for row in rows:
            self.assertTrue(row["same"], (row["label"], row["differs"]))
            self.assertEqual(row["restored"], row["kept"], row["label"])
            self.assertGreater(row["kept"], 0, row["label"])
        self.assertEqual(self.reload_run["consoleErrors"], [])
        self.assertTrue(self.reload_run["done"]["visible"])

    def test_the_page_comes_back_quietly_and_the_host_is_not_told_twice(self):
        back = self.scenes["back"]
        self.assertEqual((back["stage"], self.scenes["before"]["stage"]), ("MANIPULATE", "MANIPULATE"))
        self.assertEqual(back["host"], [], "what the host heard before the reload it does not hear again")
        self.assertTrue(all(replayed for _, replayed in back["evidence"]), back["evidence"])
        self.assertEqual([name for name, _ in back["evidence"]], self.scenes["before"]["host"])
        self.assertEqual(back["slider"], back["expectedSlider"])
        self.assertTrue(back["unlocked"])
        self.assertGreater(back["restored"], 0)

    def test_start_over_forgets_what_was_kept(self):
        self.assertEqual(self.scenes["startOver"], {"stage": "CONTEXT", "kept": None, "restored": 0})

    def test_a_page_rebuilt_from_another_spec_starts_fresh(self):
        self.assertEqual((self.scenes["beforeRebuild"]["stage"], self.scenes["beforeRebuild"]["kept"]), ("MANIPULATE", True))
        self.assertEqual(self.scenes["rebuilt"], {"stage": "CONTEXT", "restored": 0})

    def test_a_kept_list_that_does_not_fit_is_dropped_without_a_loop(self):
        self.assertEqual(self.scenes["mismatchAtOnce"], {"stage": "CONTEXT", "restored": 0, "kept": None, "loads": 1})
        self.assertEqual(self.scenes["mismatchAfterSome"], {"stage": "CONTEXT", "restored": 0, "kept": None, "loads": 2})
        self.assertEqual(self.scenes["consoleErrors"], [])

    def test_where_the_browser_keeps_nothing_the_page_still_runs_to_its_end(self):
        self.assertEqual(self.no_storage["consoleErrors"], [])
        self.assertTrue(self.no_storage["done"]["visible"])
        self.assertEqual(self.no_storage["evidence"][-1], "FRESH_TRANSFER_RESULT")
