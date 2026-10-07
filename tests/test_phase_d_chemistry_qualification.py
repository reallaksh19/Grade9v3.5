from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import core2_v2, render_core


REPO = Path(__file__).resolve().parents[1]
MANIFEST = REPO / "evidence/blueprint-cycles/ISS32/inputs/product.manifest.json"
PACKAGE = REPO / "evidence/blueprint-cycles/ISS32/inputs/package.v1.json"
BANK = REPO / "evidence/blueprint-cycles/ISS32/inputs/owner.bank.json"
DEMAND_ADAPTER = REPO / "Chemistry/adapter/DemandReview.json"
CORE_CONTRACTS = REPO / "Chemistry/adapter/CoreContracts.json"
Q2 = "OWN-ISSUE32-HYBRID-02"
Q4 = "OWN-ISSUE32-HYBRID-04"


class PhaseDChemistryQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.adapter = json.loads(DEMAND_ADAPTER.read_text(encoding="utf-8"))
        cls.contracts = json.loads(CORE_CONTRACTS.read_text(encoding="utf-8"))
        cls.questions = {q["id"]: q for q in cls.bank["questions"]}
        cls.representations = {r["id"]: r for r in cls.package["representations"]}

    def test_iss32_remains_owner_supplied_evidence_not_official_source_authority(self):
        self.assertTrue(self.manifest["product_id"].startswith("EVIDENCE-CHE-ISSUE32-"))
        self.assertEqual(self.manifest["subject"], "Chemistry")
        self.assertEqual(len(self.manifest["selection"]["core2"]), 10)

        for qid in (Q2, Q4):
            ext = self.questions[qid]["extensions"]
            custody = ext["grade9v3:source_custody"]
            authorship = ext["grade9v3:authorship"]
            self.assertEqual(custody["authority_class"], "OWNER_SUPPLIED_RAW_INPUT")
            self.assertEqual(custody["wording_custody"], "VERBATIM")
            self.assertEqual(authorship["kind"], "COORDINATOR_AI_DRAFTED")
            self.assertTrue(authorship["owner_supplied"])
            self.assertFalse(authorship["personally_owner_authored"])

    def test_q2_primary_demand_crux_and_difficulty_are_question_owned_and_derived(self):
        q = self.questions[Q2]
        analysis = q["extensions"]["grade9v3:analysis"]
        difficulty = analysis["difficulty"]
        route = {move["id"]: move for move in q["answer"]["reasoning_route"]}

        self.assertEqual(analysis["cognitive_demand"]["primary"], "EXPLAIN")
        self.assertEqual(
            q["extensions"]["grade9v3:qrt_template"]["template_id"],
            "QRT-EXPLAIN-D2",
        )
        self.assertEqual(q["answer"]["crux_move_ref"], f"{Q2}-MOVE-2")
        self.assertEqual(route[q["answer"]["crux_move_ref"]]["kind"], "CONNECT")
        self.assertIn("one local VSEPR domain", route[q["answer"]["crux_move_ref"]]["action"])

        expected_keys = {
            "concept_model_selection",
            "representation_translation",
            "reasoning_chain_length",
            "algebra_computational_load",
            "trap_exception_sensitivity",
        }
        self.assertEqual(set(difficulty["components"]), expected_keys)
        self.assertEqual(difficulty["score"], sum(difficulty["components"].values()))
        vocabulary = json.loads(
            (REPO / "Shared/vocabularies/learner-question-metadata.v1.json").read_text(
                encoding="utf-8"
            )
        )
        band_range = vocabulary["question_difficulty_score_ranges"][difficulty["band"]]
        self.assertEqual(difficulty["band"], "D2")
        self.assertGreaterEqual(difficulty["score"], band_range["min"])
        self.assertLessEqual(difficulty["score"], band_range["max"])

    def test_chemistry_semantics_live_in_adapter_and_records_not_shared_renderer(self):
        self.assertEqual(self.adapter["subject"], "Chemistry")
        self.assertIn("Chemistry/adapter/CoreContracts.json", self.adapter["basis_refs"])
        self.assertIn("EXPLAIN", self.adapter["demands"])
        self.assertIn("which level it is operating at", self.contracts["subject_specific_notes"]["representation_triplet"].lower())

        shared_renderer = (REPO / "Shared/tools/render_core.py").read_text(encoding="utf-8")
        for token in ("OWN-ISSUE32-HYBRID-02", "OWN-ISSUE32-HYBRID-04", "HCHO", "NH3"):
            self.assertNotIn(token, shared_renderer)

    def test_iss32_core1a_uses_active_recovered_blueprint_and_authored_constructions(self):
        ctx = render_core.context(MANIFEST)
        bp = next(
            row for row in ctx.blueprints["blueprints"]
            if row["id"] == "BP-CORE1A-CONSTRUCTION" and row["status"] == "ACTIVE"
        )
        self.assertEqual(bp["version"], "1.8.0")

        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        selected = {
            row["id"]: row
            for row in ctx.selection_rows["microtopics"]
        }
        self.assertEqual(set(selected), set(self.manifest["selection"]["microtopics"]))
        for microtopic in selected.values():
            self.assertTrue(microtopic["construction_units"])
            for unit in microtopic["construction_units"]:
                self.assertIn(f'id="{unit["id"]}"', html)
                self.assertTrue(unit["step_refs"])
                self.assertTrue(unit["representation_ref"])
        self.assertFalse([gap for gap in ctx.gaps if gap["core"] == "CORE1A"])

    def test_q2_core2_attempt_support_is_bounded_and_diagnosis_is_not_confirmed(self):
        q = self.questions[Q2]
        source, authored = core2_v2.split_pre_solution_support(q)
        self.assertEqual(source, [])
        self.assertEqual(len(authored), 3)
        self.assertTrue(all(row["reveals"] != "ANSWER" for row in authored))
        self.assertEqual(
            [row["supports_move_ref"] for row in authored],
            [f"{Q2}-MOVE-1", f"{Q2}-MOVE-2", f"{Q2}-MOVE-3"],
        )

        repair = q["extensions"]["grade9v3:learning_repair"]
        self.assertEqual(repair["status"], "CORRECTION_CANDIDATE")
        self.assertNotIn("grade9v3:diagnostic_evidence", q["extensions"])

        ctx = render_core.context(MANIFEST)
        rendered = next(row for row in ctx.selection_rows["core2"] if row["id"] == Q2)
        html = render_core.core2(ctx, rendered)
        self.assertIn("Attempt first", html)
        self.assertIn("data-g9-attempt-box", html)
        self.assertIn("data-g9-commit", html)
        self.assertIn(f'data-g9-payload-ref="CORE2-{Q2}-solution"', html)
        self.assertEqual(html.count("template data-g9-rung-payload="), 3)
        self.assertNotIn('data-g9-support-reveals="ANSWER"', html)

    def test_q4_question_local_visual_preserves_nh3_species_inventory(self):
        q = self.questions[Q4]
        review = q["extensions"]["grade9v3:core2_visual_review"]
        self.assertEqual(review["question_ref"], Q4)
        self.assertEqual(review["authored_figure_refs"], ["REP-ACADEMIC-ISS32-Q4"])
        self.assertEqual(review["replaces_authored_figure_refs"], ["REP-CYCLE-ISS32-NH3"])

        rep = self.representations["REP-ACADEMIC-ISS32-Q4"]
        self.assertEqual(
            rep["extensions"]["grade9v3:authored_question_ref"],
            Q4,
        )
        asset = REPO / rep["rendered_asset_refs"][0]
        svg = asset.read_text(encoding="utf-8")
        self.assertIn("NH3 supplied Lewis inventory", svg)
        self.assertEqual(svg.count(">H</text>"), 3)
        self.assertIn(">:</text>", svg)
        self.assertNotIn("NH4", svg)

        ctx = render_core.context(MANIFEST)
        rendered_q4 = next(row for row in ctx.selection_rows["core2"] if row["id"] == Q4)
        figure_html = render_core._core2_question_figures(ctx, rendered_q4, "PRE_ATTEMPT")
        self.assertIn('data-g9-representation="REP-ACADEMIC-ISS32-Q4"', figure_html)
        self.assertNotIn('data-g9-representation="REP-CYCLE-ISS32-NH3"', figure_html)
        self.assertFalse([gap for gap in ctx.gaps if gap["record"] == Q4])


if __name__ == "__main__":
    unittest.main()
