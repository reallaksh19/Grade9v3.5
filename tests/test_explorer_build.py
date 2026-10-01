"""The explorer page is generated from a spec through the blueprint: its route, its numbers, its layout, and what it will not carry."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import sys
import unittest
import xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import explorer_build as eb  # noqa: E402
from Shared.tools import explorer_model as em  # noqa: E402
from tests.test_test_area import Fixture  # noqa: E402

FIXTURE = REPO / "tests/fixtures/explorer/projectile-range.explorer.json"
SPEC = json.loads(FIXTURE.read_text(encoding="utf-8"))
QUESTION = {"id": "Q-PROJ-8", "original_identifier": "Q8", "stem": "A ball is launched from level ground at 20 m/s.\n(a) At what angle does it land farthest?\n(b) Explain."}
BRIEF = {"question_ref": "Q-PROJ-8", "label": "Q8", "rule": "the most conceptual question first"}
MATHML = {"math", "mrow", "mi", "mn", "mo", "msub", "msup", "mfrac", "mtext", "msqrt"}


def brief(links: dict | None = None) -> eb.Brief:
    return eb.Brief.from_parts(BRIEF, QUESTION, "projectile-range")


def build_page(spec: dict | None = None, links: dict | None = None) -> str:
    html, _ = eb.page(copy.deepcopy(spec or SPEC), brief(), links or {"question": None, "concept": None})
    return html


class Scaffold(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.cleanup)

    def test_the_scaffold_has_every_key_in_the_order_of_the_spec_and_the_depth_of_the_reference_page(self):
        spec = eb.scaffold(self.fixture.manifest)
        self.assertEqual(list(spec), eb.SPEC_ORDER)
        bp = em.blueprint()
        floors = em.minima(bp)
        self.assertEqual(len(spec["predict"]["options"]), floors["PREDICT"][1])
        self.assertEqual(len(spec["manipulate"]["goals"]), floors["MANIPULATE"][1])
        self.assertEqual(len(spec["observe"]["statements"]), floors["OBSERVE"][1])
        self.assertEqual(len(spec["deconstruct"]["steps"]), floors["DECONSTRUCT"][1])
        self.assertEqual(len(spec["reconstruct"]["steps"]), floors["RECONSTRUCT"][1])
        self.assertEqual(len(spec["invariants"]), floors["INVARIANT"][1])
        self.assertEqual(len(spec["boundary"]["cases"]), floors["BOUNDARY"][1])
        self.assertEqual(len(spec["fade"]), 3)
        self.assertEqual(len(spec["transfer"]), floors["TRANSFER"][1])
        self.assertEqual(len(spec["quantities"]), floors["QUANTITIES"][1])

    def test_it_fills_in_what_the_records_already_say_about_the_toughest_concept(self):
        spec = eb.scaffold(self.fixture.manifest)
        brief = eb.Brief(self.fixture.manifest).brief
        self.assertEqual(spec["target"]["question_ref"], brief["question_ref"])
        self.assertEqual(spec["target"]["failure"], brief["wrong_route"])
        self.assertEqual(spec["target"]["operation"], brief["crux_move"]["action"])
        self.assertEqual(spec["slug"], self.fixture.slug)
        self.assertEqual(spec["blueprint_ref"], "BP-EXPLORER-GCDR@1.0.0")
        self.assertTrue(spec["product"].endswith("product.manifest.json"))
        self.assertEqual(spec["schema"], em.SPEC_VERSION)

    def test_the_scaffold_fails_the_check_and_each_flagged_component_comes_with_the_blueprints_own_words(self):
        spec = eb.scaffold(self.fixture.manifest)
        folder = eb.INTERACTIVE_ROOT / self.fixture.slug
        folder.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, folder, True)
        (folder / eb.SPEC_FILE).write_text(json.dumps(spec), encoding="utf-8")
        _, _, report = eb.check_source(folder)
        self.assertTrue(report.errors)
        self.assertTrue({"TARGET", "PREDICT", "SCENE", "TRANSFER"} <= {f.component for f in report.errors})
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            eb.print_findings(report, em.blueprint())
        text = out.getvalue()
        self.assertIn("how to author what is flagged", text)
        self.assertIn("PREDICT: predict.prompt, predict.options (three)", text)
        self.assertIn("TARGET: target:", text)

    def test_new_writes_the_spec_once_and_never_over_a_spec_that_is_there(self):
        folder = eb.INTERACTIVE_ROOT / self.fixture.slug
        self.addCleanup(shutil.rmtree, folder, True)
        rel = self.fixture.manifest.relative_to(REPO).as_posix()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(eb.main(["new", rel]), 0)
        self.assertTrue((folder / eb.SPEC_FILE).is_file())
        self.assertIn("toughest concept: Q1", out.getvalue())
        self.assertIn("every field of the blueprint BP-EXPLORER-GCDR@1.0.0", out.getvalue())
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            self.assertEqual(eb.main(["new", rel]), 1)
        self.assertIn("not overwritten", err.getvalue())


class FromAProduct(unittest.TestCase):
    """A spec for the product's own toughest concept builds; one for any other question is refused."""

    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.cleanup)
        self.brief = eb.Brief(self.fixture.manifest)
        self.folder = eb.INTERACTIVE_ROOT / self.fixture.slug
        self.folder.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.folder, True)

    def write(self, **changes) -> Path:
        spec = copy.deepcopy(SPEC)
        spec.update(slug=self.fixture.slug, product=self.fixture.manifest.relative_to(REPO).as_posix())
        spec["target"]["question_ref"] = self.brief.brief["question_ref"]
        for key, value in changes.items():
            spec[key] = value
        (self.folder / eb.SPEC_FILE).write_text(json.dumps(spec), encoding="utf-8")
        return self.folder

    def test_a_spec_for_the_toughest_concept_builds_a_page_that_shows_the_owners_question_word_for_word(self):
        html, compiled, spec, report, brief = eb.build(self.write())
        self.assertEqual(report.errors, [])
        self.assertIn(self.brief.question["stem"].splitlines()[0], html.replace("&#x27;", "'"))
        self.assertIn(f"<strong>Q1</strong> · the question this page is built for", html)
        self.assertEqual(compiled["view_box"], [440, 220])

    def test_a_spec_for_another_question_than_the_toughest_is_refused_and_no_page_is_made(self):
        folder = self.write()
        spec = json.loads((folder / eb.SPEC_FILE).read_text(encoding="utf-8"))
        spec["target"]["question_ref"] = "Q-OWNER-FX-02"
        (folder / eb.SPEC_FILE).write_text(json.dumps(spec), encoding="utf-8")
        html, _, _, report, _ = eb.build(folder)
        self.assertEqual(html, "")
        self.assertTrue(any("is not the toughest concept of the set" in f.detail for f in report.errors), report.errors)

    def test_the_slug_is_the_name_of_the_folder(self):
        folder = self.write(slug="somewhere-else")
        _, _, report = eb.check_source(folder)
        self.assertTrue(any(f.where == "slug" for f in report.errors), report.errors)

    def test_a_product_that_is_not_there_is_said_in_one_line(self):
        folder = self.write(product="TEST/_nowhere/none.manifest.json")
        with self.assertRaisesRegex(ValueError, "'product' must name an existing product manifest"):
            eb.check_source(folder)

    def test_the_command_line_exits_with_the_checks_verdict(self):
        folder = self.write()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(eb.main(["check", str(folder)]), 0)
        self.assertIn("no findings", out.getvalue())
        self.assertIn("evidence:", out.getvalue())
        bad = self.write(blueprint_ref="BP-EXPLORER-GCDR@0.1.0")
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(eb.main(["check", str(bad)]), 1)


class Page(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.html = build_page()

    def test_the_route_is_the_blueprints_eleven_steps_in_order_and_only_the_first_is_open(self):
        steps = re.findall(r'<section class="gx-card g9-c-route-step"[^>]*data-gx-step="([A-Z]+)"', self.html)
        self.assertEqual(steps, em.stages(em.blueprint()))
        self.assertEqual(len(re.findall(r'data-gx-rail="', self.html)), 11)
        opened = re.findall(r'data-gx-step="([A-Z]+)"[^>]*data-state="current"', self.html)
        self.assertEqual(opened, ["CONTEXT"])
        self.assertEqual(self.html.count('data-state="locked" hidden'), 10)

    def test_every_component_of_the_blueprint_that_the_page_shows_is_marked_for_the_audits(self):
        for cid in ["ROUTE_RAIL", "SCENE", "SECOND_VIEW", "PARAMETERS", "QUANTITIES", "TARGET", "SOURCE"] + em.stages(em.blueprint()):
            self.assertIn(f'data-g9-component="{cid}"', self.html, cid)

    def test_the_page_says_what_it_is_in_the_markup_and_opens_dark(self):
        self.assertIn('data-g9-role="EXPLORER"', self.html)
        self.assertIn('data-g9-blueprint="BP-EXPLORER-GCDR@1.0.0"', self.html)
        self.assertIn('<html lang="en" data-theme="dark"', self.html)
        self.assertRegex(self.html, r'<meta name="viewport" content="width=device-width,initial-scale=1">')
        self.assertRegex(self.html, r'<meta name="g9-render" content="explorer_build/1 [0-9a-f]{16}">')

    def test_the_page_is_one_file_that_loads_nothing_from_another_host(self):
        for url in re.findall(r'(?:src|href)=["\']([^"\']+)', self.html):
            self.assertTrue(url.startswith("#"), url)
        self.assertNotRegex(self.html, r"@import|url\(\s*[\"']?https?:")
        hosts = set(re.findall(r"https?://[^\"'\s<>)]+", self.html))
        self.assertLessEqual({h.rstrip("/") for h in hosts}, {"http://www.w3.org/2000/svg", "http://www.w3.org/1998/Math/MathML"}, hosts)

    def test_the_equations_are_restricted_presentation_mathml_built_from_the_spec_not_typed(self):
        maths = re.findall(r"<math .*?</math>", self.html)
        self.assertGreaterEqual(len(maths), 6)
        for math_tree in maths:
            tags = {node.tag.split("}", 1)[-1] for node in ET.fromstring(math_tree).iter()}
            self.assertLessEqual(tags, MATHML)
        self.assertIn("<msqrt>", "".join(maths) + "<msqrt>")

    def test_the_picture_and_the_graph_have_a_name_and_a_description_for_a_reader_who_cannot_see_them(self):
        for ident in ("gx-scene", "gx-graph"):
            self.assertIn(f'aria-labelledby="{ident}-t {ident}-d"', self.html)
            self.assertIn(f'<title id="{ident}-t">', self.html)
            self.assertIn(f'<desc id="{ident}-d">', self.html)
        self.assertIn('id="gx-live"', self.html)
        self.assertIn('aria-live="polite"', self.html)
        self.assertIn('href="#g9-route"', self.html)

    def test_each_slider_is_a_range_input_with_its_label_and_starts_locked_until_the_prediction(self):
        self.assertRegex(self.html, r'<label for="gx-p-theta">.*?</label><input type="range" id="gx-p-theta" min="5" max="85" step="1" value="30" disabled>')
        self.assertNotIn('id="gx-p-v"', self.html, "a fixed parameter is a given, not a slider")
        self.assertIn("launch speed (given)", self.html)

    def test_the_tempting_models_number_is_shown_only_when_the_model_is_imposed(self):
        self.assertRegex(self.html, r'data-gx-reveal="contradict" hidden><span class="gx-ro-l">range if steeper meant farther</span>')

    def test_a_number_the_spec_does_not_show_never_reaches_the_page_as_text_the_page_computes_them(self):
        steps = re.search(r'<ol class="gx-derive">(.*?)</ol>', self.html, re.S).group(1)
        self.assertNotRegex(steps, r"\d+\.\d+")
        self.assertEqual(steps.count("<output data-gx-val>"), 4)

    def test_the_same_spec_is_the_same_page_and_a_changed_spec_is_a_different_one(self):
        self.assertEqual(build_page(), self.html)
        changed = copy.deepcopy(SPEC)
        changed["context"]["situation"] += " It is a warm day."
        self.assertNotEqual(build_page(changed), self.html)

    def test_the_spec_travels_in_the_page_as_json_and_nothing_in_it_can_close_the_script(self):
        hostile = copy.deepcopy(SPEC)
        hostile["title"] = "</title><script>alert(1)</script>"
        hostile["context"]["situation"] = "<img src=x onerror=alert(1)> -->"
        page = build_page(hostile)

        class Elements(HTMLParser):
            def __init__(self):
                super().__init__()
                self.scripts, self.images, self.handlers = 0, 0, 0

            def handle_starttag(self, tag, attrs):
                self.scripts += tag == "script"
                self.images += tag == "img"
                self.handlers += sum(1 for name, _ in attrs if name.startswith("on"))

        parsed = Elements()
        parsed.feed(page)
        self.assertEqual((parsed.scripts, parsed.images, parsed.handlers), (3, 0, 0), "the data, the model and the runtime; nothing the spec wrote")
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        data = re.search(r'<script type="application/json" id="gx-data">(.*?)</script>', page, re.S).group(1)
        self.assertNotIn("</", data)
        self.assertEqual(json.loads(data)["spec"]["title"], hostile["title"])

    def test_the_data_in_the_page_is_the_spec_and_the_model_the_checks_ran_on(self):
        data = json.loads(re.search(r'<script type="application/json" id="gx-data">(.*?)</script>', self.html, re.S).group(1))
        self.assertEqual(data["spec"], SPEC)
        self.assertEqual(data["compiled"], em.compile_page_model(copy.deepcopy(SPEC)))
        self.assertEqual(data["route"], em.stages(em.blueprint()))

    def test_the_script_never_turns_text_into_markup(self):
        runtime = (REPO / "Shared/web/explorer-runtime.js").read_text(encoding="utf-8")
        for forbidden in ("innerHTML", "outerHTML", "insertAdjacentHTML", "document.write", "eval(", "new Function"):
            self.assertNotIn(forbidden, runtime)

    def test_the_end_of_the_route_links_back_to_the_question_when_the_product_is_there_and_says_so_when_it_is_not(self):
        with_links = build_page(links={"question": "../../products/projectile-range/core2.html#Q-PROJ-8", "concept": "../../products/projectile-range/core1a.html#MIC-X"})
        self.assertIn('<a class="gx-primary-link" href="../../products/projectile-range/core2.html#Q-PROJ-8">Back to the question</a>', with_links)
        self.assertIn('<a class="gx-secondary-link" href="../../products/projectile-range/core1a.html#MIC-X">The concept book for it</a>', with_links)
        self.assertIn("not deployed yet", self.html)
        self.assertNotIn("Back to the question", self.html)


class Layout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bp = em.blueprint()
        cls.css = eb.explorer_css(cls.bp)

    def test_the_columns_are_the_blueprints_own_fractions_from_its_own_breakpoint(self):
        rp = self.bp["responsive_policy"]
        self.assertEqual((rp["primary_fraction"], rp["support_fraction"], rp["expanded_min_px"]), (0.66, 0.34, 1100))
        self.assertIn("@media (min-width:1100px){\n.gx-main{display:grid;grid-template-columns:minmax(0,66fr) minmax(0,34fr)", self.css)

    def test_the_route_stays_in_view_and_scrolls_inside_itself_where_the_blueprint_says_so(self):
        self.assertTrue(self.bp["responsive_policy"]["support_sticky"] and self.bp["responsive_policy"]["tablet_12_7"]["support_scrolls_inside"])
        self.assertRegex(self.css, r"\.gx-route\{position:sticky;top:\d+px;max-height:calc\(100vh - \d+px\);overflow-y:auto;overscroll-behavior:contain")

    def test_narrower_than_the_breakpoint_the_pictures_stay_in_view_and_the_sliders_stay_under_them(self):
        narrow = self.css.split("@media (max-width:1099px){")[1].split("@media (max-width:699px)")[0]
        self.assertIn(".gx-views{position:sticky;top:0", narrow)
        self.assertIn(".gx-controls{position:sticky;top:var(--gx-views-h", narrow)
        self.assertIn(".gx-stage,.gx-panel{display:contents}", narrow)

    def test_the_current_steps_buttons_stay_reachable_when_the_step_is_taller_than_the_panel(self):
        self.assertRegex(self.css, r"\.gx-card\[data-state=current\] \.gx-actions\{position:sticky;bottom:0")

    def test_learner_text_never_drops_below_the_floor_and_every_control_is_a_touch_target(self):
        floor = self.bp["responsive_policy"]["tablet_12_7"]["figure_min_text_css_px"]
        self.assertEqual(floor, 14)
        self.assertIn(".gx-svg text{font:600 16px", self.css, "labels are 16 units on a 440-unit picture, 14.9 px at the reference width")
        for size in re.findall(r"font-size:([0-9.]+)rem", self.css):
            self.assertGreaterEqual(float(size) * 17, 14.4, size)
        for rule in re.findall(r"\.(?:gx-mini|gx-secondary|gx-toggle|gx-primary)[^{]*\{[^}]*min-height:(\d+)px", self.css):
            self.assertGreaterEqual(int(rule), 48)

    def test_the_roles_are_told_apart_by_shape_as_well_as_by_colour(self):
        self.assertIn(".gx-r-wrong .gx-stroke{stroke-dasharray", self.css)
        self.assertIn(".gx-r-helper .gx-stroke{stroke-width", self.css)
        for role in ("object", "given", "result", "wrong", "helper", "frame"):
            self.assertIn(f".gx-r-{role}{{color:var(--gx-{role})}}", self.css)
            self.assertIn(f"--gx-{role}:", self.css)

    def test_both_themes_define_every_role_colour(self):
        dark = self.css.split(":root[data-theme=light]")[0]
        light = self.css.split(":root[data-theme=light]")[1].split("}")[0]
        for role in ("object", "given", "result", "wrong", "helper", "frame"):
            self.assertIn(f"--gx-{role}:", dark)
            self.assertIn(f"--gx-{role}:", light)


if __name__ == "__main__":
    unittest.main()
