"""The blueprint is the page's source: its components, columns and depths decide what the renderer builds, what the
gate fails and what an author is scaffolded and asked for. Each test changes or reads the blueprint, not a copy of it."""
from __future__ import annotations

import copy
import json
import re
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import blueprint_spec, owner_bank, quality_contract, render_core
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
        for name in sorted(blueprints.presentations()):
            cls = "g9-c-" + name.lower().replace("_", "-")
            self.assertTrue(re.search(r"\." + re.escape(cls) + r"(?![\w-])", render_core.COMPONENT_CSS), f"{name} has no .{cls} rule")

    def test_learner_text_in_components_never_drops_below_the_blueprint_floor(self):
        floor = REGISTRY["shell"]["typography_policy"]["minimum_learner_text_css_px"]
        base = REGISTRY["shell"]["typography_policy"]["base_text_css_px"]
        for size in re.findall(r"font-size:([0-9.]+)rem", render_core.COMPONENT_CSS):
            self.assertGreaterEqual(float(size) * base, floor, size)
        for size in re.findall(r"font-size:([0-9.]+)px", render_core.COMPONENT_CSS):
            self.assertGreaterEqual(float(size), floor, size)

    def test_the_written_specification_is_current(self):
        self.assertEqual(blueprint_spec.OUT.read_text(encoding="utf-8"), blueprint_spec.render())


class Realisation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx = render_core.context(MOTION_2D)
        cls.digest = render_core.render_digest(cls.ctx)
        cls.html = {role: render_core.page(cls.ctx, role, "PAGES", cls.digest) for role in ("CORE2", "CORE1A")}

    def marked(self, role: str) -> set[str]:
        return set(re.findall(r'data-g9-component="([A-Z_]+)"', self.html[role]))

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
        page = {"role": "CORE2", "blueprint_ref": "BP-CORE2-SOURCE-QUESTION@1.2.0",
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
        page = {"role": "CORE1A", "blueprint_ref": "BP-CORE1A-CONSTRUCTION@1.2.0",
                "units": [{"id": "MIC", "construction_units": ["CU-1", "CU-2"],
                           "components": [{"id": "STAGED_VISUAL", "items": 3, "unit": "CU-1"}]}]}
        problems = quality_contract.OPS["blueprint_components"](page, {"level": "REQUIRED"}, {})
        self.assertIn("MIC / CU-2: STAGED_VISUAL is absent", problems)
        self.assertNotIn("MIC / CU-1: STAGED_VISUAL is absent", problems)


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

    def test_the_depth_an_owner_bank_is_held_to_is_the_blueprints_target_not_a_number_in_the_tool(self):
        bank = owner_bank.new(self.INTAKE, "demo")
        raised = copy.deepcopy(REGISTRY)
        next(c for b in raised["blueprints"] if b["id"] == "BP-CORE2-SOURCE-QUESTION"
             for c in b["components"] if c["id"] == "HINT_LADDER")["target_items"] = 5
        with patch.object(blueprints, "load_registry", return_value=raised):
            self.assertIn("HINT_LADDER needs 5", " ".join(owner_bank.check(bank)))
        self.assertNotIn("HINT_LADDER needs", " ".join(owner_bank.check(bank)), "three rungs meet the blueprint's target of three")


if __name__ == "__main__":
    unittest.main()
