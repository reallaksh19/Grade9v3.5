from __future__ import annotations

import ast
import copy
import json
import re
import unittest
from pathlib import Path

from Shared.library import core1a_construction
from Shared.tools import blueprint_spec, render_core
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
