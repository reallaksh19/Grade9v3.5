"""The blueprint is the page's source: its components, columns and depths decide what the renderer builds, what the
gate fails and what an author is scaffolded and asked for. Each test changes or reads the blueprint, not a copy of it."""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import blueprint_spec, explorer_build, explorer_model, owner_bank, quality_contract, render_core
from Shared.tools import web_blueprint_contract as blueprints

REPO = Path(__file__).resolve().parents[1]
REGISTRY = json.loads((REPO / "Shared/web/interactive-page-blueprints.v1.json").read_text(encoding="utf-8"))
MOTION_2D = REPO / "products/physics/phy-kin-2d-motion.manifest.json"


def ctx_with(blueprint_registry: dict) -> render_core.Ctx:
    return render_core.Ctx(manifest={"product_id": "P"}, packages=[], bank=[], blueprints=blueprint_registry)


class Registry(unittest.TestCase):
    def test_the_registry_is_valid_against_its_schema_and_audit(self):
        import jsonschema
        schema = json.loads((REPO / "Shared/web/interactive-page-blueprint.schema.json").read_text(encoding="utf-8"))
        self.assertEqual([e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(REGISTRY)], [])
        self.assertEqual(blueprints.audit_registry(REGISTRY)["findings"], [])

    def test_the_audit_names_a_component_in_no_slot_a_duplicate_and_a_slot_with_nothing_in_it(self):
        broken = copy.deepcopy(REGISTRY)
        core2 = next(b for b in broken["blueprints"] if b["id"] == "BP-CORE2-SOURCE-QUESTION")
        core2["components"][0]["slot"] = "nowhere"
        core2["components"].append(dict(core2["components"][1]))
        core2["components"] = [c for c in core2["components"] if c["slot"] != "representation"]
        points = {f["point"] for f in blueprints.audit_registry(broken)["findings"]}
        self.assertTrue({"WEB_BLUEPRINT_COMPONENT_SLOT_UNKNOWN", "WEB_BLUEPRINT_COMPONENT_DUPLICATE",
                         "WEB_BLUEPRINT_SLOT_WITHOUT_COMPONENT"} <= points, points)

    def test_every_presentation_the_schema_allows_has_its_own_css(self):
        # The Core pages are styled by the renderer; the explorer's own presentations by the explorer builder, which writes the same class names.
        rules = render_core.COMPONENT_CSS + explorer_build.explorer_css(explorer_model.blueprint(REGISTRY))
        for name in sorted(blueprints.presentations()):
            cls = "g9-c-" + name.lower().replace("_", "-")
            self.assertTrue(re.search(r"\." + re.escape(cls) + r"(?![\w-])", rules), f"{name} has no .{cls} rule")

    def test_learner_text_in_components_never_drops_below_the_blueprint_floor(self):
        floor = REGISTRY["shell"]["typography_policy"]["minimum_learner_text_css_px"]
        base = REGISTRY["shell"]["typography_policy"]["base_text_css_px"]
        for size in re.findall(r"font-size:([0-9.]+)rem", render_core.COMPONENT_CSS):
            self.assertGreaterEqual(float(size) * base, floor, size)
        for size in re.findall(r"font-size:([0-9.]+)px", render_core.COMPONENT_CSS):
            self.assertGreaterEqual(float(size), floor, size)

    def test_a_toggle_that_holds_a_badge_and_a_label_wraps_instead_of_overflowing_a_320px_screen(self):
        rule = re.search(r"\.g9-why-toggle\{([^}]*)\}", render_core.CSS + render_core.COMPONENT_CSS).group(1)
        self.assertIn("flex-wrap:wrap", rule)
        self.assertIn("max-width:100%", rule)

    def test_the_written_specification_is_current(self):
        self.assertEqual(blueprint_spec.OUT.read_text(encoding="utf-8"), blueprint_spec.render())


class Realisation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = render_core.context(MOTION_2D)
        cls.digest = render_core.render_digest(cls.ctx)
        cls.html = {role: render_core.page(cls.ctx, role, "PAGES", cls.digest) for role in ("CORE2", "CORE1A")}

    def marked(self, role: str) -> set[str]:
        body = re.sub(r"<style\b.*?</style>", "", self.html[role], flags=re.S)       # the layout CSS names components too
        return set(re.findall(r'data-g9-component="([A-Z_]+)"', body))

    def test_every_marker_on_a_page_is_a_component_its_blueprint_declares(self):
        for role in ("CORE2", "CORE1A"):
            declared = {c["id"] for c in blueprints.components(blueprints.blueprint_for_role(REGISTRY, role))}
            self.assertLessEqual(self.marked(role), declared, role)

    def test_a_fully_authored_product_shows_every_required_component(self):
        for role in ("CORE2", "CORE1A"):
            required = {c["id"] for c in blueprints.required_components(blueprints.blueprint_for_role(REGISTRY, role))}
            self.assertLessEqual(required, self.marked(role), (role, required - self.marked(role)))

    def test_the_layout_is_one_split_per_row_with_the_blueprints_columns(self):
        article = re.search(r"<article .*?</article>", self.html["CORE2"], re.S).group(0)
        self.assertEqual(article.count('class="g9-split'), 1)
        primary = article[article.index("g9-col-primary"):article.index("g9-col-support")]
        self.assertIn('data-g9-component="STEM"', primary)
        self.assertIn('data-g9-component="ATTEMPT"', primary)
        self.assertNotIn('data-g9-component="HINT_LADDER"', primary)
        self.assertIn('data-g9-component="HINT_LADDER"', article[article.index("g9-col-support"):])

    def test_the_hint_ladder_shows_its_rungs_before_their_words(self):
        article = re.search(r"<article .*?</article>", self.html["CORE2"], re.S).group(0)
        ghosts = article.count("data-g9-rung-ghost")
        self.assertGreaterEqual(ghosts, 2)
        shown = re.search(r"<ol data-g9-ladder>(.*?)</ol>", article, re.S).group(1)
        self.assertEqual(shown, "", "no rung's words are in the page before the learner asks for it")

    def test_guided_support_is_collapsed_by_default(self):
        article = re.search(r"<article .*?</article>", self.html["CORE2"], re.S).group(0)
        disclosure = re.search(r'<details class="g9-secondary-disclosure" data-g9-secondary="core2-hints"[^>]*>', article)
        self.assertIsNotNone(disclosure)
        self.assertNotIn(" open", disclosure.group(0))
        self.assertIn("Need a hint? · guided support", article)


class Reporting(unittest.TestCase):
    def test_a_required_component_that_is_absent_or_below_its_floor_is_a_gap_that_names_it(self):
        ctx = ctx_with(REGISTRY)
        self.assertEqual(render_core.component(ctx, "CORE2", "HINT_LADDER", "", "Q1", items=0), "")
        render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q2", items=1)
        self.assertEqual([(g["duty"], g["record"], g["component"]) for g in ctx.gaps],
                         [("AUTHOR_COMPONENT", "Q1", "HINT_LADDER"), ("AUTHOR_COMPONENT", "Q2", "HINT_LADDER")])
        self.assertIn("1 of the 2 rungs", ctx.gaps[1]["detail"])

    def test_between_the_floor_and_the_reference_depth_is_an_advisory_not_a_gap(self):
        ctx = ctx_with(REGISTRY)
        marked = render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q", items=2)
        self.assertIn('data-g9-component="HINT_LADDER"', marked)
        self.assertEqual(ctx.gaps, [])
        self.assertEqual([a["component"] for a in ctx.advisories], ["HINT_LADDER"])

    def test_an_expected_component_that_is_absent_is_an_advisory_and_an_optional_one_is_silent(self):
        ctx = ctx_with(REGISTRY)
        render_core.component(ctx, "CORE2", "REPRESENTATION", "", "Q", items=0)
        render_core.component(ctx, "CORE2", "CONCEPT_NAV", "", "Q")
        self.assertEqual(ctx.gaps, [])
        self.assertEqual([a["component"] for a in ctx.advisories], ["REPRESENTATION"])

    def test_a_duty_that_already_reports_the_absence_is_not_reported_twice(self):
        ctx = ctx_with(REGISTRY)
        ctx.gap("AUTHOR_WORKED_ANCHOR", "CU-1", "no worked anchor", "CORE1A")
        render_core.component(ctx, "CORE1A", "WORKED_EXAMPLE", "", "CU-1")
        self.assertEqual(len(ctx.gaps), 1)

    def test_without_a_blueprint_the_renderer_neither_wraps_nor_reports(self):
        ctx = ctx_with({})
        self.assertEqual(render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q", items=0), "<p>x</p>")
        self.assertEqual((ctx.gaps, ctx.advisories), ([], []))

    def test_the_order_inside_a_slot_is_the_blueprints_and_an_undeclared_part_is_refused(self):
        ctx = ctx_with(REGISTRY)
        body = render_core.component_body(ctx, "CORE2", {"CONDITIONS": "c", "STEM": "s", "ATTEMPT": "a", "TRAP": "t"}, "attempt")
        self.assertEqual(body, "scta")      # STEM, CONDITIONS, TRAP, ATTEMPT: the order the blueprint lists them in
        with self.assertRaises(KeyError):
            render_core.component_body(ctx, "CORE2", {"NOT_A_COMPONENT": "x"}, "attempt")

    def test_the_gate_rule_reads_the_registry_not_a_copy_of_it(self):
        page = {"role": "CORE2", "blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.5.0",
                "units": [{"id": "Q", "components": [{"id": "STEM", "items": None, "unit": None},
                                                     {"id": "HINT_LADDER", "items": 1, "unit": None}]}]}
        problems = quality_contract.OPS["blueprint_components"](page, {"level": "REQUIRED"}, {})
        self.assertIn("Q: HINT_LADDER has 1 of the 2 it needs", problems)
        self.assertIn("Q: ATTEMPT is absent", problems)
        self.assertFalse([p for p in problems if "STEM" in p])
        raised = copy.deepcopy(REGISTRY)
        next(c for b in raised["blueprints"] if b["id"] == "BP-CORE2-SOURCE-QUESTION"
             for c in b["components"] if c["id"] == "HINT_LADDER")["min_items"] = 1
        with patch.object(blueprints, "load_registry", return_value=raised):
            self.assertNotIn("Q: HINT_LADDER has 1 of the 2 it needs",
                             quality_contract.OPS["blueprint_components"](page, {"level": "REQUIRED"}, {}))

    def test_a_per_unit_component_is_expected_once_for_each_construction_unit(self):
        page = {"role": "CORE1A", "blueprint_ref": "BP-CORE1A-CONSTRUCTION@1.4.0",
                "units": [{"id": "MIC", "construction_units": ["CU-1", "CU-2"],
                           "components": [{"id": "STAGED_VISUAL", "items": 3, "unit": "CU-1"}]}]}
        problems = quality_contract.OPS["blueprint_components"](page, {"level": "REQUIRED"}, {})
        self.assertIn("MIC / CU-2: STAGED_VISUAL is absent", problems)
        self.assertNotIn("MIC / CU-1: STAGED_VISUAL is absent", problems)


class ReferenceDepth(unittest.TestCase):
    """New authoring is held to the benchmark, by difficulty band; official products stay at their floor."""

    @staticmethod
    def ctx(held_to: str) -> render_core.Ctx:
        ctx = ctx_with(REGISTRY)
        ctx.held_to = held_to
        return ctx

    def test_the_depth_a_ladder_is_held_to_follows_the_questions_band(self):
        ctx = self.ctx("REFERENCE")
        render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q-EASY", items=3, band="D1")
        render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q-HARD", items=3, band="D3")
        self.assertEqual([(g["record"], g["component"]) for g in ctx.gaps], [("Q-HARD", "HINT_LADDER")])
        self.assertIn("3 of the 5 rungs the reference page has for a D3 question", ctx.gaps[0]["detail"])

    def test_the_same_shortfall_is_only_an_advisory_for_an_official_product(self):
        ctx = self.ctx("FLOOR")
        render_core.component(ctx, "CORE2", "HINT_LADDER", "<p>x</p>", "Q-HARD", items=3, band="D3")
        self.assertEqual(ctx.gaps, [])
        self.assertEqual([a["record"] for a in ctx.advisories], ["Q-HARD"])

    def test_an_expected_component_is_a_gap_for_new_authoring_until_the_record_waives_it_with_a_reason(self):
        ctx = self.ctx("REFERENCE")
        render_core.component(ctx, "CORE2", "TRAP", "", "Q1")
        self.assertEqual([(g["record"], g["component"]) for g in ctx.gaps], [("Q1", "TRAP")])
        marked = render_core.component(ctx, "CORE2", "TRAP", "", "Q2", waivers={"TRAP": "no tempting route"})
        self.assertEqual(len(ctx.gaps), 1, "a waiver is not a gap")
        self.assertIn('data-g9-component-waiver="TRAP"', marked)
        self.assertIn("no tempting route", marked)
        self.assertEqual([(w["record"], w["component"], w["reason"]) for w in ctx.waived], [("Q2", "TRAP", "no tempting route")])

    def test_a_required_component_cannot_be_waived(self):
        ctx = self.ctx("REFERENCE")
        render_core.component(ctx, "CORE2", "ATTEMPT", "", "Q", waivers={"ATTEMPT": "not needed"})
        self.assertEqual([g["component"] for g in ctx.gaps], ["ATTEMPT"])
        self.assertEqual(ctx.waived, [])

    def test_the_gate_holds_a_deep_question_to_its_band_and_skips_what_the_record_waived(self):
        page = {"role": "CORE2", "blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.5.0",
                "units": [{"id": "Q", "metadata": [{"kind": "question-difficulty", "ref": "D3", "value": "D3",
                                                   "display_name": "Difficulty", "label": "D3"}],
                           "components": [{"id": "HINT_LADDER", "items": 3, "unit": None}],
                           "waived": {"TRAP": "no tempting route"}}]}
        depth = quality_contract.OPS["blueprint_components"](page, {"level": "DEPTH"}, {})
        self.assertTrue([p for p in depth if "HINT_LADDER" in p], depth)
        expected = quality_contract.OPS["blueprint_components"](page, {"level": "EXPECTED"}, {})
        self.assertFalse([p for p in expected if "TRAP" in p], expected)


class Core1aBenchmark(unittest.TestCase):
    """What the Core1A benchmark page has per concept, read off the product the renderer builds from the blueprint."""

    @classmethod
    def setUpClass(cls):
        ctx = render_core.context(MOTION_2D)
        digest = render_core.render_digest(ctx)
        cls.html = render_core.page(ctx, "CORE1A", "PAGES", digest)
        cls.blueprint = blueprints.blueprint_for_role(REGISTRY, "CORE1A")

    def test_the_page_opens_in_the_blueprints_theme_and_the_learner_can_switch(self):
        self.assertEqual(self.blueprint["presentation_policy"]["default_theme"], "dark")
        self.assertRegex(self.html, r"<html[^>]*data-theme=\"dark\"")
        self.assertIn('data-g9-theme="light"', self.html)
        self.assertIn('data-g9-theme="dark"', self.html)

    def test_secondary_reference_is_collapsed_but_the_crux_and_practice_path_stay_visible(self):
        for kind in ("core1a-prerequisites", "core1a-question-bridge", "core1a-equations", "core1a-trap-repair"):
            matches = re.findall(rf'<details class="g9-secondary-disclosure" data-g9-secondary="{kind}"[^>]*>', self.html)
            self.assertTrue(matches, kind)
            self.assertTrue(all(" open" not in tag for tag in matches), kind)
        self.assertIn('data-g9-component="KEY_STEP"', self.html)
        self.assertIn('data-g9-component="CONSTRUCTION_STEPS"', self.html)
        self.assertIn('data-g9-component="QUICK_CHECK"', self.html)
        self.assertIn("Now you do one", self.html)

    def test_worked_examples_require_prediction_before_each_step_is_revealed(self):
        self.assertIn("Before opening each step, say what you would do next.", self.html)
        worked = re.findall(r'<details class="g9-worked-step" data-g9-worked-predict[^>]*>', self.html)
        self.assertTrue(worked)
        self.assertTrue(all(" open" not in tag for tag in worked))
        self.assertRegex(self.html, r"Predict step 1, then reveal")
        self.assertIn('data-g9-secondary="worked-result"', self.html)

    def test_the_independent_checks_are_a_numbered_triad_that_names_each_items_job(self):
        triad = render_core._quick_check([{"statement": "Substitute back", "role": "CHECK"},
                                          {"statement": "Use it on new numbers", "role": "APPLY"},
                                          {"statement": "Tie it to the next idea", "role": "CONNECT"}])
        self.assertEqual(re.findall(r'data-g9-triad-role="(\w+)"', triad), ["CHECK", "APPLY", "CONNECT"])
        self.assertEqual(re.findall(r'g9-triad-head">(\d) · (\w+)', triad), [("1", "Check"), ("2", "Apply"), ("3", "Connect")])
        self.assertIn(".g9-triad{", render_core.COMPONENT_CSS)
        self.assertTrue(re.search(r'<ol class="g9-triad">', self.html), "the unit's checks are a triad even where a package declares no job")

    def test_revision_and_competition_project_distinct_authored_transfer_sections(self):
        revision_package = {
            "extensions": {
                "grade9v3:purpose_delivery": {
                    "REVISION": {
                        "section_title": "Next-level revision",
                        "support_policy": "REDUCED_SUPPORT",
                        "items": [{
                            "id": "REV-1",
                            "roles": ["CORE1A", "CORE2"],
                            "concept_refs": ["MIC-X"],
                            "question_refs": ["Q-X"],
                            "title": "One step harder",
                            "prompt": "Apply the same idea with one added modelling decision.",
                            "source_kind": "AUTHOR_CREATED_REVISION_TRANSFER",
                            "source_label": "Original next-level revision transfer.",
                            "answer": {"summary": "Model answer", "reasoning": ["Check the added decision."]},
                        }],
                    }
                }
            }
        }
        competition_package = {
            "extensions": {
                "grade9v3:purpose_delivery": {
                    "COMPETITION": {
                        "section_title": "Competition transfer",
                        "support_policy": "NO_MID_TASK_BRIDGING",
                        "items": [{
                            "id": "COMP-1",
                            "roles": ["CORE1A", "CORE2"],
                            "concept_refs": ["MIC-X"],
                            "question_refs": ["Q-X"],
                            "title": "Mixed transfer",
                            "prompt": "Solve the mixed transfer without a labelled route.",
                            "source_kind": "AUTHOR_CREATED_COMPETITION_STYLE",
                            "source_label": "Original competition-style transfer; not a past-paper claim.",
                            "answer": {"summary": "Model answer", "reasoning": ["Identify the hidden structure."]},
                        }],
                    }
                }
            }
        }
        revision = render_core.Ctx(manifest={"product_id": "P", "purpose": "REVISION"}, packages=[revision_package], bank=[], blueprints={})
        competition = render_core.Ctx(manifest={"product_id": "P", "purpose": "COMPETITION"}, packages=[competition_package], bank=[], blueprints={})
        rev_html = render_core._purpose_extension(revision, "CORE1A", "MIC-X")
        comp_html = render_core._purpose_extension(competition, "CORE1A", "MIC-X")
        self.assertIn('data-g9-purpose-delivery="REVISION"', rev_html)
        self.assertIn("Next-level revision", rev_html)
        self.assertIn('data-g9-purpose-delivery="COMPETITION"', comp_html)
        self.assertIn("Competition transfer", comp_html)
        self.assertNotEqual(rev_html, comp_html)

    def test_staged_figures_reveal_cumulatively_unless_the_author_explicitly_requests_replacement(self):
        self.assertIn('data-g9-stage-mode="cumulative"', self.html)
        self.assertNotIn("g9StageSequence", render_core.JS)
        self.assertIn("stageMode=f.dataset.g9StageMode||'cumulative'", render_core.JS)
        self.assertIn("cumulative?n<=i:n===i", render_core.JS)

        asset = REPO / "tests/fixtures/_stage-mode.svg"
        asset.write_text(
            '<svg viewBox="0 0 200 100" role="img" aria-label="stages">'
            '<title>stages</title><desc>two stages</desc>'
            '<g data-g9-stage-id="A"><path d="M10 90 L100 10"/></g>'
            '<g data-g9-stage-id="B"><text x="100" y="50">label</text></g></svg>',
            encoding="utf-8",
        )
        self.addCleanup(lambda: asset.unlink(missing_ok=True))
        rep = {
            "id": "REP-STAGE",
            "kind": "GEOMETRIC_CONSTRUCTION",
            "purpose": "test",
            "rendered_asset_refs": ["tests/fixtures/_stage-mode.svg"],
            "reveal_stages": [
                {"id": "A", "label": "Geometry", "purpose": "show structure"},
                {"id": "B", "label": "Label", "purpose": "annotate structure"},
            ],
            "extensions": {"grade9v3:stage_mode": "REPLACE"},
        }
        ctx = render_core.Ctx(
            manifest={"product_id": "P"},
            packages=[{"representations": [rep]}],
            bank=[],
            blueprints={},
        )
        html = render_core.figure(ctx, "REP-STAGE", "TEACHING", "CORE1A", "CU")
        self.assertIn('data-g9-stage-mode="replace"', html)

    def test_each_equation_card_belongs_to_a_construction_unit_and_every_stage_has_a_named_button(self):
        units = set(re.findall(r'data-g9-component="CONSTRUCTION_STEPS"[^>]*data-g9-component-unit="([^"]+)"', self.html))
        cards = re.findall(r'data-g9-component="EQUATIONS"[^>]*data-g9-component-unit="([^"]+)"', self.html)
        self.assertTrue(cards)
        self.assertLessEqual(set(cards), units, "an equation card is per construction unit, never per page")
        self.assertEqual(len(cards), len(set(cards)))
        stages = [int(n) for n in re.findall(r'data-g9-stages-total="(\d+)"', self.html)]
        described = re.findall(r'class="g9-stage-chip"[^>]*data-g9-stage-desc="[^"]+"', self.html)
        self.assertTrue(stages)
        self.assertEqual(len(described), sum(stages), "every stage of every figure is a button with its own description")

    def test_the_blueprint_asks_for_three_steps_and_three_stages_as_the_reference_has(self):
        by_id = {c["id"]: c for c in blueprints.components(self.blueprint)}
        self.assertEqual((by_id["CONSTRUCTION_STEPS"]["target_items"], by_id["STAGED_VISUAL"]["target_items"]), (3, 3))
        self.assertEqual(by_id["QUICK_CHECK"]["presentation"], "TRIAD")
        self.assertEqual(by_id["EQUATIONS"]["level"], "EXPECTED")
        self.assertTrue(self.blueprint["interaction_policy"]["progressive_support"])
        self.assertEqual(self.blueprint["interaction_policy"]["secondary_reference_default"], "COLLAPSED")
        self.assertEqual(self.blueprint["interaction_policy"]["worked_example_step_policy"], "PREDICT_THEN_REVEAL")
        self.assertEqual(by_id["WORKED_EXAMPLE"]["presentation"], "PREDICT_REVEAL_WORKED_CARD")


class Tablet(unittest.TestCase):
    """The 12.7-inch tablet is the design target: what the blueprint promises there is read by the renderer and the audit."""

    @classmethod
    def setUpClass(cls):
        cls.ctx = render_core.context(MOTION_2D)
        cls.digest = render_core.render_digest(cls.ctx)
        cls.core1a = render_core.page(cls.ctx, "CORE1A", "PAGES", cls.digest)

    def test_both_question_and_concept_pages_declare_the_tablet_promises(self):
        for role in ("CORE2", "CORE1A"):
            promise = blueprints.blueprint_for_role(REGISTRY, role)["responsive_policy"]["tablet_12_7"]
            self.assertEqual(promise["reference_viewport"], {"width": 1366, "height": 854})
            self.assertGreaterEqual(promise["figure_min_text_css_px"], 14)
            self.assertLessEqual(promise["identity_max_px"], 200)

    def test_the_key_step_and_what_the_learner_needs_open_the_first_unit_beside_the_figure_not_above_it(self):
        article = re.search(r"<article .*?</article>", self.core1a, re.S).group(0)
        split = article.index("g9-split")
        for marker in ('data-g9-component="KEY_STEP"', 'data-g9-component="MODEL_CONTRACT"'):
            self.assertGreater(article.index(marker), split, marker)
        self.assertEqual(article.count('data-g9-component="KEY_STEP"'), 1)
        self.assertLess(article.index('data-g9-component="UNIT_HEADER"'), article.index('data-g9-component="KEY_STEP"'))
        self.assertLess(article.index('data-g9-component="KEY_STEP"'), article.index('data-g9-component="MODEL_CONTRACT"'))

    def test_a_concept_with_one_section_has_no_route_to_itself(self):
        one = {"construction_units": [{"id": "CU-A", "decision": "Only"}]}
        two = {"construction_units": [{"id": "CU-A", "decision": "First"}, {"id": "CU-B", "decision": "Second"}]}
        self.assertEqual(render_core._core1a_section_route(one), "")
        self.assertIn("data-g9-section-route", render_core._core1a_section_route(two))

    def test_an_authored_figure_is_held_to_the_labels_a_tablet_can_read_and_none_cut_off(self):
        def figure(size, width, x=60, anchor="start", text="magnitude 5"):
            return (f'<svg viewBox="0 0 {width} 300" role="img" aria-label="a"><title>t</title><desc>d</desc>'
                    f'<text x="{x}" y="40" font-size="{size}" text-anchor="{anchor}">{text}</text></svg>')
        column = 468.0
        self.assertEqual(render_core._figure_text_findings(figure(14, 440), column, 14.0), [])
        small = render_core._figure_text_findings(figure(14, 520), column, 14.0)
        self.assertEqual(len(small), 1)
        self.assertIn("12.6 px", small[0])
        self.assertIn("at least 16 units high", small[0])
        cut = render_core._figure_text_findings(figure(16, 440, x=4, anchor="end"), column, 14.0)
        self.assertTrue(any("cut off" in line for line in cut), cut)
        self.assertEqual(render_core._figure_text_findings("<svg><text>no viewBox</text></svg>", column, 14.0), [])

    def test_only_new_authoring_is_asked_for_legible_figures(self):
        figure = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 640 300" role="img" aria-label="a"><title>t</title><desc>d</desc>'
                  '<text x="20" y="40" font-size="12">small label</text></svg>')
        package = {"representations": [{"id": "REP-X", "rendered_asset_refs": ["tests/fixtures/_tablet_figure.svg"]}]}
        path = REPO / "tests/fixtures/_tablet_figure.svg"
        path.write_text(figure, encoding="utf-8")
        self.addCleanup(lambda: path.unlink(missing_ok=True))
        for held_to, expected in (("FLOOR", 0), ("REFERENCE", 1)):
            ctx = render_core.Ctx(manifest={"product_id": "P"}, packages=[package], bank=[], blueprints=REGISTRY, held_to=held_to)
            html = render_core.figure(ctx, "REP-X", "TEACHING", "CORE2", "Q")
            self.assertIn("<figure", html)
            self.assertEqual(len([g for g in ctx.gaps if g["duty"] == "AUTHOR_FIGURE_TEXT"]), expected, held_to)

    def test_links_inside_the_page_use_the_themes_accent_so_they_read_on_dark(self):
        self.assertIn("a{color:var(--accent)}", render_core.CSS)


class Links(unittest.TestCase):
    def test_a_core2_page_links_to_concepts_only_when_the_product_has_a_core1a_page(self):
        ctx = render_core.context(MOTION_2D)
        question = ctx.selection_rows["core2"][0]
        self.assertIn('href="core1a.html#', render_core._core2_concept_navigation(ctx, question))
        ctx.manifest["output_roles"] = ["CORE2"]
        self.assertEqual(render_core._core2_concept_navigation(ctx, question), "")


class Authoring(unittest.TestCase):
    INTAKE = {"status": "OK", "inputs": {"questions": [{"id": "q1", "label": "1", "text": "Find 3 + 4."}]}, "intake_digest": "d"}

    def test_a_new_owner_question_is_scaffolded_with_exactly_what_the_blueprint_lists(self):
        question = owner_bank.new(self.INTAKE, "demo")["questions"][0]
        wanted = json.loads(json.dumps(blueprints.skeleton(owner_bank.core2_blueprint())).replace("{qid}", question["id"]))
        self.assertEqual(question["scaffolds"], wanted["scaffolds"])
        self.assertEqual(question["answer"]["reasoning_route"], wanted["answer"]["reasoning_route"])
        self.assertEqual(question["extensions"]["grade9v3:analysis"]["common_wrong_route"], "")

    def test_the_depth_an_owner_bank_is_held_to_is_the_blueprints_target_for_its_band_not_a_number_in_the_tool(self):
        bank = owner_bank.new(self.INTAKE, "demo")
        bank["questions"][0]["extensions"]["grade9v3:analysis"]["difficulty"]["band"] = "D1"
        raised = copy.deepcopy(REGISTRY)
        next(c for b in raised["blueprints"] if b["id"] == "BP-CORE2-SOURCE-QUESTION"
             for c in b["components"] if c["id"] == "HINT_LADDER")["target_items_by_band"]["D1"] = 6
        with patch.object(blueprints, "load_registry", return_value=raised):
            self.assertIn("HINT_LADDER needs 6, the record supplies 5", " ".join(owner_bank.check(bank)))
        self.assertNotIn("HINT_LADDER needs", " ".join(owner_bank.check(bank)), "five rungs meet the blueprint's three for a D1 question")


if __name__ == "__main__":
    unittest.main()


class PrintPdf(unittest.TestCase):
    """A PDF icon in the header opens the PDF printed from the page; a verified past paper is linked as its own PDF; the key is never linked."""

    @classmethod
    def setUpClass(cls):
        cls.pages, cls.gaps, _ = render_core.build(MOTION_2D)
        cls.policy = REGISTRY["shell"]["print_policy"]

    def link(self, html: str) -> str:
        found = re.findall(r'<a data-g9-action="pdf"[^>]*>.*?</a>', html)
        self.assertLessEqual(len(found), 1)
        return found[0] if found else ""

    def test_the_registry_says_what_the_icon_is_where_it_goes_and_what_it_never_opens(self):
        self.assertIn("PRINT_PDF", REGISTRY["shell"]["controls"])
        self.assertEqual((self.policy["target"], self.policy["never_linked"], self.policy["in_print"]), ("GENERATED_LEARNER_PDF", ["KEY_PDF"], "HIDDEN"))
        self.assertGreaterEqual(self.policy["target_css_px_min"], 48)

    def test_each_role_page_links_the_pdf_printed_from_itself_and_the_index_links_none(self):
        for role in self.policy["applies_to_roles"]:
            name = render_core.ROLE_FILE[role]
            html = self.pages[name]
            link = self.link(html)
            self.assertIn(f'href="{name.removesuffix(".html")}.pdf"', link, name)
            self.assertIn('target="_blank"', link)
            self.assertIn('rel="noopener"', link)
            self.assertIn('type="application/pdf"', link)
            self.assertIn(f'aria-label="{self.policy["accessible_name"]}"', link)
            self.assertIn("<span>PDF</span>", link, "the icon is never the only thing that says what it is")
            self.assertIn("aria-hidden=\"true\"", link)
            self.assertNotIn(".key.pdf", html)
        self.assertEqual(self.link(self.pages["index.html"]), "")

    def test_the_icon_sits_in_the_fixed_header_among_the_other_controls(self):
        header = re.search(r"<header data-g9-shell-header>.*?</header>", self.pages["core2.html"]).group(0)
        self.assertIn('data-g9-action="pdf"', header)
        self.assertLess(header.index("Question bank"), header.index('data-g9-action="pdf"'))
        self.assertLess(header.index('data-g9-action="pdf"'), header.index('data-g9-action="search"'))

    def test_the_icon_is_a_touch_target_and_is_not_printed(self):
        css = render_core.CSS + render_core.COMPONENT_CSS
        self.assertRegex(css, r"header a,header button[^{]*\{[^}]*min-height:var\(--g9-touch-min\)")
        self.assertRegex(render_core.CSS, r"@media print\{[^@]*header\[data-g9-shell-header\][^{]*\{display:none!important\}")

    def test_a_single_file_page_has_no_icon_because_it_has_no_file_beside_it(self):
        pages, _, _ = render_core.build(MOTION_2D, mode="SINGLE_FILE")
        self.assertEqual(self.link(pages["product.html"]), "")

    def test_a_header_made_without_a_pdf_has_no_icon(self):
        self.assertNotIn('data-g9-action="pdf"', render_core.shell_header("../index.html", "../qb.html"))
        self.assertIn('data-g9-action="pdf"', render_core.shell_header("../index.html", "../qb.html", pdf_href="core2.pdf"))

    def test_a_verified_past_paper_is_linked_as_a_pdf_and_an_owner_supplied_question_is_not(self):
        verified = {"extensions": {"grade9v3:source_custody": {"authority_class": "OFFICIAL_EXAM_ORGANIZER_ARCHIVE", "source_status": "PYQ_VERIFIED_PARENT",
                                                                  "paper_url": "https://jeeadv.ac.in/past_qps/2007_1.pdf"}}}
        html = render_core._source_pdf(verified)
        self.assertIn('href="https://jeeadv.ac.in/past_qps/2007_1.pdf"', html)
        self.assertIn('rel="noopener noreferrer"', html)
        self.assertIn('target="_blank"', html)
        self.assertIn("Source paper", html)
        self.assertIn("(PDF)", html)
        owner = {"extensions": {"grade9v3:source_custody": {"authority_class": "OWNER_SUPPLIED_RAW_INPUT", "wording_custody": "VERBATIM"}}}
        self.assertEqual(render_core._source_pdf(owner), "")

    def test_only_an_https_link_to_a_verified_pdf_is_ever_linked(self):
        base = {"authority_class": "OFFICIAL_EXAM_ORGANIZER_ARCHIVE", "source_status": "PYQ_VERIFIED_PARENT"}
        def link(**more):
            return render_core._source_pdf({"extensions": {"grade9v3:source_custody": {**base, **more}}})
        self.assertEqual(link(paper_url="http://jeeadv.ac.in/past_qps/2007_1.pdf"), "", "not https")
        self.assertEqual(link(paper_url="https://jeeadv.ac.in/past_qps/index.html"), "", "not a pdf")
        self.assertEqual(link(paper_url="javascript:alert(1).pdf"), "")
        self.assertEqual(link(paper_url=""), "")
        self.assertEqual(render_core._source_pdf({"extensions": {"grade9v3:source_custody": {**base, "source_status": "UNVERIFIED", "paper_url": "https://x.org/a.pdf"}}}), "",
                         "an unverified source is not offered")
        self.assertIn('href="https://x.org/a.pdf?download=1"', link(paper_url="https://x.org/a.pdf?download=1"))
        self.assertNotIn("<script", link(paper_url='https://x.org/"><script>.pdf'))

    def test_the_source_pdf_is_a_component_of_the_core2_blueprint_in_the_identity_slot_and_is_optional(self):
        core2 = next(b for b in REGISTRY["blueprints"] if b["id"] == "BP-CORE2-SOURCE-QUESTION")
        row = next(c for c in core2["components"] if c["id"] == "SOURCE_PDF")
        self.assertEqual((row["slot"], row["level"], row["presentation"]), ("identity", "OPTIONAL", "LINK_LIST"))
