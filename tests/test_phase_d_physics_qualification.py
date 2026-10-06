from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import core2_v2, render_core


REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
PACKAGE = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
MANIFEST = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
WITNESS = "PYQ-PHY-IITJEE-2011-P2-Q33"


class PhaseDPhysicsDemandCruxQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.question = next(q for q in cls.bank["questions"] if q["id"] == WITNESS)

    def test_product_selects_witness_without_overwriting_question_primary_demand(self):
        self.assertIn(WITNESS, self.manifest["selection"]["core2"])
        self.assertEqual(
            self.question["primary_capability_ref"],
            "CAP-KIN-PROJECTILE-MODEL",
        )
        capability = next(
            c for c in self.package["capabilities"]
            if c["id"] == self.question["primary_capability_ref"]
        )
        self.assertIn("projectile", capability["action"].lower())

        microtopic = next(
            m for m in self.package["microtopics"]
            if m["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        )
        self.assertEqual(
            microtopic["primary_capability_ref"],
            self.question["primary_capability_ref"],
        )

    def test_crux_is_bound_to_one_concrete_reasoning_move(self):
        analysis = self.question["extensions"]["grade9v3:analysis"]
        answer = self.question["answer"]
        route = {move["id"]: move for move in answer["reasoning_route"]}

        self.assertEqual(
            analysis["stable_crux_move"],
            "Use the vertical projectile event to get time, then include the train's accelerated displacement in the relative x equation.",
        )
        self.assertEqual(
            answer["crux_move_ref"],
            "PYQ-PHY-IITJEE-2011-P2-Q33-MOVE-2",
        )
        crux = route[answer["crux_move_ref"]]
        self.assertEqual(crux["kind"], "CONNECT")
        self.assertIn("Relative horizontal displacement", crux["action"])
        self.assertIn("accelerating train", crux["action"])
        self.assertEqual(answer["difficult_move"], 1)

    def test_crux_support_targets_the_same_move_reference(self):
        crux_ref = self.question["answer"]["crux_move_ref"]
        supports = [
            row for row in self.question["scaffolds"]
            if row["supports_move_ref"] == crux_ref
        ]
        self.assertEqual(len(supports), 1)
        self.assertEqual(supports[0]["support_kind"], "CONNECT")
        self.assertIn("ball-minus-train horizontal displacement", supports[0]["text"])

    def test_difficulty_score_is_exact_sum_of_the_five_canonical_components(self):
        difficulty = self.question["extensions"]["grade9v3:analysis"]["difficulty"]
        expected = {
            "concept_model_selection",
            "representation_translation",
            "reasoning_chain_length",
            "algebra_computational_load",
            "trap_exception_sensitivity",
        }
        self.assertEqual(set(difficulty["components"]), expected)
        self.assertTrue(
            all(
                isinstance(value, int) and not isinstance(value, bool) and 0 <= value <= 2
                for value in difficulty["components"].values()
            )
        )
        self.assertEqual(
            difficulty["score"],
            sum(difficulty["components"].values()),
        )
        self.assertEqual(difficulty["score"], 7)

    def test_recorded_d3_band_is_derived_from_the_active_score_range(self):
        difficulty = self.question["extensions"]["grade9v3:analysis"]["difficulty"]
        vocabulary = json.loads(
            (REPO / "Shared/vocabularies/learner-question-metadata.v1.json").read_text(
                encoding="utf-8"
            )
        )
        score_range = vocabulary["question_difficulty_score_ranges"][difficulty["band"]]
        self.assertEqual(difficulty["band"], "D3")
        self.assertEqual(score_range, {"min": 6, "max": 7})
        self.assertGreaterEqual(difficulty["score"], score_range["min"])
        self.assertLessEqual(difficulty["score"], score_range["max"])
        self.assertTrue(difficulty["basis"].strip())

    def test_core1a_projectile_uses_the_active_generic_construction_blueprint(self):
        ctx = render_core.context(MANIFEST)
        blueprint = next(
            row for row in ctx.blueprints["blueprints"]
            if row["id"] == "BP-CORE1A-CONSTRUCTION" and row["status"] == "ACTIVE"
        )
        self.assertEqual(blueprint["version"], "1.8.0")
        self.assertEqual(blueprint["responsive_policy"]["expanded"], "SINGLE_PANE")
        required = {row["id"] for row in blueprint["components"] if row["level"] == "REQUIRED"}
        self.assertTrue(
            {"CONCEPT_HEADER", "UNIT_HEADER", "CONSTRUCTION_STEPS", "KEY_STEP", "EXIT_RECALL"}
            <= required
        )

    def test_core1a_projectile_renders_all_authored_construction_units_without_core1a_gaps(self):
        ctx = render_core.context(MANIFEST)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        target = next(
            m for m in ctx.selection_rows["microtopics"]
            if m["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        )
        self.assertEqual(len(target["construction_units"]), 3)

        for unit in target["construction_units"]:
            self.assertGreaterEqual(len(unit["step_refs"]), 2)
            self.assertTrue(unit["representation_ref"])
            self.assertGreaterEqual(len(unit["reveal_stage_refs"]), 2)
            self.assertTrue(unit["worked_anchor_ref"])
            self.assertTrue(unit["independent_checks"])
            self.assertIn(f'id="{unit["id"]}"', html)
            self.assertIn(render_core.esc(unit["decision"]), html)
            for step_ref in unit["step_refs"]:
                self.assertIn(f'data-g9-step="{step_ref}"', html)

        self.assertIn(render_core.esc(target["inferential_jump"]), html)
        self.assertIn(render_core.esc(target["exit_task"]["prompt"]), html)
        self.assertFalse([gap for gap in ctx.gaps if gap["core"] == "CORE1A"])

    def test_generic_renderer_has_no_physics_projectile_or_witness_special_case(self):
        source = (REPO / "Shared/tools/render_core.py").read_text(encoding="utf-8")
        self.assertNotIn("MIC-PHY-KIN-PROJECTILE-MODEL", source)
        self.assertNotIn(WITNESS, source)

    def test_core2_witness_support_is_authored_safe_and_bound_to_reasoning_moves(self):
        source, authored = core2_v2.split_pre_solution_support(self.question)
        self.assertEqual(source, [])
        self.assertEqual(len(authored), 3)
        self.assertEqual(
            [row["source"] for row in authored],
            ["scaffolds[0]", "scaffolds[1]", "scaffolds[2]"],
        )
        self.assertEqual(
            [row["support_kind"] for row in authored],
            ["REPRESENT", "CONNECT", "EXECUTE"],
        )
        self.assertEqual(
            [row["supports_move_ref"] for row in authored],
            [move["id"] for move in self.question["answer"]["reasoning_route"]],
        )
        self.assertTrue(
            all(row["provenance"] == core2_v2.AUTHORED_CORE2_SUPPORT for row in authored)
        )
        self.assertTrue(all(row["reveals"] != "ANSWER" for row in authored))

    def test_core2_witness_renders_real_attempt_and_gated_solution_payload(self):
        ctx = render_core.context(MANIFEST)
        question = next(q for q in ctx.selection_rows["core2"] if q["id"] == WITNESS)
        html = render_core.core2(ctx, question)

        self.assertIn("Attempt first", html)
        self.assertIn('data-g9-attempt-box', html)
        self.assertIn('data-g9-commit', html)
        self.assertIn(
            f'data-g9-payload-ref="CORE2-{WITNESS}-solution"',
            html,
        )
        self.assertIn(
            f'<template data-g9-payload="CORE2-{WITNESS}-solution">',
            html,
        )
        self.assertIn('data-requires-attempt', html)
        self.assertEqual(html.count('template data-g9-rung-payload='), 3)
        self.assertNotIn('data-g9-support-reveals="ANSWER"', html)

    def test_q33_is_honestly_no_picture_instead_of_getting_a_decorative_case(self):
        self.assertEqual(self.question.get("figure_refs") or [], [])
        self.assertFalse(self.question.get("representation_roles"))
        self.assertNotIn("grade9v3:core2_support_plan", self.question["extensions"])

    def test_shared_clock_scene_has_one_owner_resolved_data_and_real_asset(self):
        rep = next(
            r for r in self.package["representations"]
            if r["id"] == "REP-KIN-2D-SHARED-CLOCK"
        )
        scene = next(
            row for row in rep["scene_instances"]
            if row["id"] == "SCENE-KIN-2D-SHARED-CLOCK-PORTABLE-01"
        )
        self.assertEqual(scene["microtopic_ref"], "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS")
        self.assertNotIn("question_ref", scene)
        self.assertEqual(scene["cores"], ["CORE1A", "CORE1B"])

        data = {row["id"]: row for row in self.package["data"]}
        self.assertEqual(
            scene["datum_refs"],
            ["DAT-KIN-2D-SHARED-T2", "DAT-KIN-2D-MIXED-T3"],
        )
        self.assertTrue(all(ref in data for ref in scene["datum_refs"]))
        self.assertEqual(data["DAT-KIN-2D-SHARED-T2"]["value"], 2)
        self.assertEqual(data["DAT-KIN-2D-MIXED-T3"]["value"], 3)

        self.assertEqual(
            rep["rendered_asset_refs"],
            ["Physics/assets/representations/REP-KIN-2D-SHARED-CLOCK.svg"],
        )
        self.assertTrue((REPO / rep["rendered_asset_refs"][0]).is_file())

    def test_secondary_demand_is_question_owned_not_manifest_owned(self):
        self.assertEqual(
            self.question["secondary_capability_refs"],
            [
                "CAP-KIN-2D-INDEPENDENT-COMPONENTS",
                "CAP-KIN-2D-CONSTANT-ACCELERATION",
            ],
        )
        self.assertNotIn("primary_capability_ref", self.manifest["selection"])
        self.assertNotIn("secondary_capability_refs", self.manifest["selection"])


if __name__ == "__main__":
    unittest.main()
