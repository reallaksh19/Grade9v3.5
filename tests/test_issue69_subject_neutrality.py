from __future__ import annotations

import ast
import copy
import json
import re
import unittest
from pathlib import Path

from Shared.library import core1a_construction
from Shared.tools import blueprint_spec, owner_bank, render_core
from tests.test_core1a_construction import fixture as core1a_fixture


REPO = Path(__file__).resolve().parents[1]
SUBJECTS = ("Chemistry", "Mathematics", "Physics")
CANONICAL_DEMANDS = {
    "RETRIEVE",
    "EXPLAIN",
    "APPLY",
    "MODEL",
    "REPRESENT",
    "SYNTHESIZE",
    "JUSTIFY",
}
DEMAND_FIELDS = {
    "review_focus",
    "representation_kinds",
    "check_types",
    "misconception_patterns",
}
FORBIDDEN_ADAPTER_POLICY_KEYS = {
    "web_blueprint_ref",
    "components",
    "slots",
    "layout_family",
    "qrt_cell",
    "template_id",
    "core_role",
}


class Issue69SubjectNeutrality(unittest.TestCase):
    @staticmethod
    def adapter(subject: str) -> dict:
        return json.loads(
            (REPO / subject / "adapter" / "DemandReview.json").read_text(encoding="utf-8")
        )

    def test_demand_adapters_specialize_the_same_canonical_demands_without_qrt_identity(self):
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                adapter = self.adapter(subject)
                self.assertEqual(adapter["schema"], "demand-review-adapter/v1")
                self.assertEqual(set(adapter["demands"]), CANONICAL_DEMANDS)
                self.assertNotIn("QRT-", json.dumps(adapter, sort_keys=True))
                for demand, row in adapter["demands"].items():
                    self.assertEqual(set(row), DEMAND_FIELDS, (subject, demand))

    def test_demand_adapters_do_not_own_page_or_product_policy(self):
        for subject in SUBJECTS:
            with self.subTest(subject=subject):
                adapter = self.adapter(subject)
                self.assertEqual(
                    adapter["basis_refs"],
                    [
                        f"{subject}/adapter/QualityVocabulary.json",
                        f"{subject}/adapter/CoreContracts.json",
                    ],
                )
                self.assertEqual(
                    adapter["vocabulary_ref"],
                    f"{subject}/adapter/QualityVocabulary.json",
                )
                payload = json.dumps(adapter, sort_keys=True)
                for key in FORBIDDEN_ADAPTER_POLICY_KEYS:
                    self.assertNotIn(f'"{key}"', payload, (subject, key))

    def test_role_blueprint_and_generated_spec_form_one_successor_chain(self):
        role_text = (
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        ).read_text(encoding="utf-8")
        match = re.search(r"```core-templates\s*\n([\s\S]*?)\n```", role_text)
        self.assertIsNotNone(match)
        contract = json.loads(match.group(1))
        registry = json.loads(
            (REPO / "Shared" / "web" / "interactive-page-blueprints.v1.json").read_text(
                encoding="utf-8"
            )
        )
        active = {
            role: f"{blueprint['id']}@{blueprint['version']}"
            for blueprint in registry["blueprints"]
            if blueprint["status"] == "ACTIVE"
            for role in blueprint["core_roles"]
        }

        self.assertEqual(contract["version"], "1.4")
        self.assertEqual(registry["registry_version"], "1.17.0")
        self.assertEqual(
            contract["roles"]["CORE1A"]["web_blueprint_ref"],
            "BP-CORE1A-CONSTRUCTION@1.8.0",
        )
        self.assertEqual(
            contract["roles"]["CORE2"]["web_blueprint_ref"],
            "BP-CORE2-SOURCE-QUESTION@1.11.0",
        )
        for role, row in contract["roles"].items():
            self.assertEqual(row["web_blueprint_ref"], active[role], role)

        generated = (
            REPO / "docs" / "specs" / "PAGE-BLUEPRINT-COMPONENTS.md"
        ).read_text(encoding="utf-8")
        self.assertEqual(generated, blueprint_spec.render(registry))

    def test_core1a_audit_does_not_make_repair_or_worked_anchor_universal(self):
        micro, rep, relation, question = core1a_fixture()
        micro["misconceptions"] = []
        question["exposure"] = []
        row = core1a_construction.audit_microtopic(
            "Test",
            "Test/library/test.json",
            micro,
            representations={rep["id"]: rep},
            relations={relation["id"]: relation},
            questions=[question],
        )
        self.assertNotIn("MISCONCEPTION_REPAIR_MISSING", row["finding_codes"])
        self.assertNotIn("WORKED_CONCEPTUAL_ANCHOR_MISSING", row["finding_codes"])

        question["exposure"] = [{"core": "CORE1A", "role": "PLANNED_WORKED_ANCHOR"}]
        question["answer"]["reasoning"] = []
        row = core1a_construction.audit_microtopic(
            "Test",
            "Test/library/test.json",
            micro,
            representations={rep["id"]: rep},
            relations={relation["id"]: relation},
            questions=[question],
        )
        self.assertIn("WORKED_CONCEPTUAL_ANCHOR_MISSING", row["finding_codes"])

    def test_core1a_renderer_does_not_create_a_manual_gap_for_absent_worked_example(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        microtopic = copy.deepcopy(ctx.selection_rows["microtopics"][0])
        extensions = microtopic.setdefault("extensions", {})
        extensions["grade9v3:lesson_anchors"] = {}
        for unit in microtopic.get("construction_units") or []:
            unit.pop("bank_anchor_ref", None)
            unit.pop("worked_anchor_ref", None)

        before = len(ctx.gaps)
        render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before:]
        self.assertFalse(
            [gap for gap in new_gaps if gap["duty"] == "AUTHOR_WORKED_ANCHOR"],
            new_gaps,
        )

        # Absence is valid, but an explicitly authored bad reference is still invalid.
        first = microtopic["construction_units"][0]
        first["worked_anchor_ref"] = "Q-NOT-A-REAL-QUESTION"
        before = len(ctx.gaps)
        render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before:]
        self.assertTrue(
            [
                gap for gap in new_gaps
                if gap["duty"] == "AUTHOR_WORKED_ANCHOR"
                and gap["record"] == first["id"]
            ],
            new_gaps,
        )

    def test_core1a_renderer_does_not_require_per_unit_quick_checks(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        microtopic = copy.deepcopy(ctx.selection_rows["microtopics"][0])
        for unit in microtopic.get("construction_units") or []:
            unit["independent_checks"] = []

        before = len(ctx.gaps)
        html = render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before:]
        self.assertFalse(
            [gap for gap in new_gaps if gap["duty"] == "AUTHOR_INDEPENDENT_CHECK"],
            new_gaps,
        )
        self.assertIn('data-g9-block="exit_task"', html)

    def test_core1a_renderer_does_not_fabricate_optional_companion_support(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        microtopic = copy.deepcopy(ctx.selection_rows["microtopics"][0])
        microtopic["misconceptions"] = []
        for unit in microtopic.get("construction_units") or []:
            unit["misconception_indexes"] = []
            unit["independent_checks"] = []

        html = render_core.core1a(ctx, microtopic)
        for unit in microtopic.get("construction_units") or []:
            self.assertNotIn(f'data-g9-support-for="{unit["id"]}"', html)
        self.assertIn('data-g9-block="exit_task"', html)

        one = render_core._quick_check([
            {"role": "CHECK", "statement": "State the invariant once."},
        ])
        self.assertIn("Quick check", one)
        self.assertNotIn("1-2-3 quick check", one)
        self.assertEqual(one.count("<li "), 1)

    def test_core1a_repair_can_render_without_a_quick_check(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        microtopic = copy.deepcopy(ctx.selection_rows["microtopics"][0])
        self.assertTrue(microtopic.get("misconceptions"))
        for unit in microtopic.get("construction_units") or []:
            unit["independent_checks"] = []

        html = render_core.core1a(ctx, microtopic)
        self.assertIn('data-g9-block="wrong_path"', html)
        self.assertNotIn('data-g9-block="independent_check"', html)
        self.assertIn('data-g9-block="exit_task"', html)

    def test_toughest_target_requires_crux_binding_not_source_question_as_worked_example(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        toughest = ctx.toughest()
        self.assertTrue(toughest)
        microtopic = copy.deepcopy(next(
            row for row in ctx.selection_rows["microtopics"]
            if row["id"] == toughest["microtopic_ref"]
        ))
        units = microtopic.get("construction_units") or []
        self.assertTrue(units)
        builder = units[0]
        builder["crux_question_refs"] = [toughest["question_ref"]]
        builder.pop("bank_anchor_ref", None)
        builder.pop("worked_anchor_ref", None)
        microtopic.setdefault("extensions", {})["grade9v3:lesson_anchors"] = {}

        before = len(ctx.gaps)
        render_core._toughest_unit_gaps(ctx, microtopic, units, toughest)
        new_gaps = ctx.gaps[before:]
        self.assertFalse(
            [gap for gap in new_gaps if gap["duty"] == "AUTHOR_TOUGHEST_CONCEPT"],
            new_gaps,
        )

        builder["crux_question_refs"] = []
        before = len(ctx.gaps)
        render_core._toughest_unit_gaps(ctx, microtopic, units, toughest)
        new_gaps = ctx.gaps[before:]
        self.assertTrue(
            [gap for gap in new_gaps if gap["duty"] == "AUTHOR_TOUGHEST_CONCEPT"],
            new_gaps,
        )

    def test_core1a_unit_worked_example_waiver_projects_without_empty_panel(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        ctx.held_to = "REFERENCE"
        microtopic = copy.deepcopy(next(
            row for row in ctx.selection_rows["microtopics"]
            if row["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        ))
        unit = microtopic["construction_units"][0]
        unit.pop("worked_anchor_ref", None)
        unit.pop("bank_anchor_ref", None)
        microtopic.setdefault("extensions", {})["grade9v3:lesson_anchors"] = {}
        reason = "this construction proceeds directly to reduced-support application"
        unit.setdefault("extensions", {})["grade9v3:component_waivers"] = {
            "WORKED_EXAMPLE": reason,
        }

        before_gaps = len(ctx.gaps)
        before_waived = len(ctx.waived)
        html = render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before_gaps:]
        new_waived = ctx.waived[before_waived:]

        self.assertFalse(
            [
                gap for gap in new_gaps
                if gap["record"] == unit["id"] and gap.get("component") == "WORKED_EXAMPLE"
            ],
            new_gaps,
        )
        self.assertIn('data-g9-component-waiver="WORKED_EXAMPLE"', html)
        self.assertIn(f'data-g9-component-unit="{unit["id"]}"', html)
        self.assertIn(render_core.esc(reason), html)
        self.assertIn(
            ("WORKED_EXAMPLE", unit["id"], reason),
            [(row["component"], row["record"], row["reason"]) for row in new_waived],
        )

        start = html.index(f'id="{unit["id"]}"')
        next_start = html.index(f'id="{microtopic["construction_units"][1]["id"]}"', start)
        self.assertNotIn('data-g9-block="worked_anchor"', html[start:next_start])

    def test_core1a_unit_staged_visual_waiver_projects_without_decorative_figure(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        ctx.held_to = "REFERENCE"
        microtopic = copy.deepcopy(next(
            row for row in ctx.selection_rows["microtopics"]
            if row["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        ))
        unit = microtopic["construction_units"][1]
        unit.pop("representation_ref", None)
        reason = "no representation adds semantic information for this construction"
        unit.setdefault("extensions", {})["grade9v3:component_waivers"] = {
            "STAGED_VISUAL": reason,
        }

        before_gaps = len(ctx.gaps)
        before_waived = len(ctx.waived)
        html = render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before_gaps:]
        new_waived = ctx.waived[before_waived:]

        self.assertFalse(
            [
                gap for gap in new_gaps
                if gap["record"] == unit["id"] and gap.get("component") == "STAGED_VISUAL"
            ],
            new_gaps,
        )
        self.assertIn('data-g9-component-waiver="STAGED_VISUAL"', html)
        self.assertIn(f'data-g9-component-unit="{unit["id"]}"', html)
        self.assertIn(
            ("STAGED_VISUAL", unit["id"], reason),
            [(row["component"], row["record"], row["reason"]) for row in new_waived],
        )

        start = html.index(f'id="{unit["id"]}"')
        next_start = html.index(f'id="{microtopic["construction_units"][2]["id"]}"', start)
        self.assertNotIn('data-g9-figure', html[start:next_start])

    def test_core1a_unit_waiver_does_not_leak_to_another_construction(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        ctx.held_to = "REFERENCE"
        microtopic = copy.deepcopy(next(
            row for row in ctx.selection_rows["microtopics"]
            if row["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        ))
        first, second = microtopic["construction_units"][:2]
        for unit in (first, second):
            unit.pop("worked_anchor_ref", None)
            unit.pop("bank_anchor_ref", None)
        microtopic.setdefault("extensions", {})["grade9v3:lesson_anchors"] = {}
        first.setdefault("extensions", {})["grade9v3:component_waivers"] = {
            "WORKED_EXAMPLE": "first construction intentionally has no worked example",
        }

        before_gaps = len(ctx.gaps)
        before_waived = len(ctx.waived)
        render_core.core1a(ctx, microtopic)
        new_gaps = ctx.gaps[before_gaps:]
        new_waived = ctx.waived[before_waived:]

        self.assertIn(
            ("WORKED_EXAMPLE", first["id"]),
            [(row["component"], row["record"]) for row in new_waived],
        )
        self.assertNotIn(
            ("WORKED_EXAMPLE", second["id"]),
            [(row["component"], row["record"]) for row in new_waived],
        )
        self.assertFalse(
            [
                gap for gap in new_gaps
                if gap["record"] == first["id"] and gap.get("component") == "WORKED_EXAMPLE"
            ],
            new_gaps,
        )
        self.assertTrue(
            [
                gap for gap in new_gaps
                if gap["record"] == second["id"] and gap.get("component") == "WORKED_EXAMPLE"
            ],
            new_gaps,
        )

    def test_core2_trap_is_owned_by_support_not_attempt(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        question = next(
            row for row in ctx.selection_rows["core2"]
            if (((row.get("extensions") or {}).get(owner_bank.ANALYSIS_KEY) or {}).get("common_wrong_route"))
        )

        html = render_core.core2(ctx, question)
        attempt_at = html.index('data-blueprint-slot="attempt"')
        representation_at = html.index('data-blueprint-slot="representation"', attempt_at)
        support_at = html.index('data-blueprint-slot="support"', representation_at)
        solution_at = html.index('data-blueprint-slot="solution"', support_at)
        attempt = html[attempt_at:representation_at]
        support = html[support_at:solution_at]

        self.assertNotIn('data-g9-component="TRAP"', attempt)
        self.assertNotIn('data-g9-block="common_wrong_route"', attempt)
        self.assertIn('data-g9-component="TRAP"', support)
        self.assertIn('data-g9-block="common_wrong_route"', support)

    def test_core2_wrong_route_is_inert_until_commitment(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        question = next(
            row for row in ctx.selection_rows["core2"]
            if (((row.get("extensions") or {}).get(owner_bank.ANALYSIS_KEY) or {}).get("common_wrong_route"))
        )
        wrong_route = ((question.get("extensions") or {}).get(owner_bank.ANALYSIS_KEY) or {})["common_wrong_route"]

        html = render_core.core2(ctx, question)
        support_at = html.index('data-blueprint-slot="support"')
        solution_at = html.index('data-blueprint-slot="solution"', support_at)
        support = html[support_at:solution_at]
        self.assertIn('data-g9-component="TRAP"', support)
        self.assertIn('data-requires-attempt', support)
        self.assertIn(f'data-g9-payload-ref="CORE2-{question["id"]}-wrong-route"', support)

        live_support = re.sub(
            r'<template data-g9-payload="[^"]+">.*?</template>',
            '',
            support,
            flags=re.S,
        )
        self.assertNotIn('data-g9-block="common_wrong_route"', live_support)
        self.assertNotIn(render_core.esc(wrong_route), live_support)
        self.assertIn('data-g9-block="common_wrong_route"', support)
        self.assertIn(render_core.esc(wrong_route), support)

    def test_core2_pre_attempt_safe_hint_lane_remains_separate_from_wrong_route(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(manifest)
        question = next(
            row for row in ctx.selection_rows["core2"]
            if render_core._core2_support(ctx, row)
            and (((row.get("extensions") or {}).get(owner_bank.ANALYSIS_KEY) or {}).get("common_wrong_route"))
        )

        support = render_core._core2_support(ctx, question)
        self.assertTrue(support)
        self.assertNotIn('data-requires-attempt', support)
        self.assertNotIn('data-g9-block="common_wrong_route"', support)

    def test_motion2d_floor_render_is_gap_free_for_browser_replay(self):
        manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        _pages, gaps, _digest, _advisories, _waived = render_core.build_report(
            manifest, mode="PAGES", held_to="FLOOR"
        )
        self.assertEqual(gaps, [], json.dumps(gaps, indent=2, sort_keys=True))

    def test_render_core_has_no_academic_subject_literal_comparison(self):
        path = REPO / "Shared" / "tools" / "render_core.py"
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        violations: list[tuple[int, list[str]]] = []
        subject_names = set(SUBJECTS)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Compare):
                continue
            literals = {
                child.value
                for child in ast.walk(node)
                if isinstance(child, ast.Constant)
                and isinstance(child.value, str)
                and child.value in subject_names
            }
            if literals:
                violations.append((node.lineno, sorted(literals)))

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
