from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import core2_v2
from Shared.tools import question_review_matrix as qrt
from Shared.tools import render_core

from tests import iss69_d02_mathematics_fixture as fixture


REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Mathematics/library/linear-equations.v1.json"
ADAPTER = REPO / "Mathematics/adapter/DemandReview.json"


class PhaseDMathematicsQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.canonical = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.pkg, cls.question, cls.microtopic = fixture.qualification_package()

    def test_d02_1_source_custody_remains_authentic_ncert_and_canonical_record_is_untouched(self):
        source = next(q for q in self.canonical["questions"] if q["id"] == fixture.WITNESS)
        custody = source["extensions"]["grade9v3:source_custody"]
        self.assertEqual(source["origin"], "ORIGINAL")
        self.assertEqual(source["origin_ref"], "SRC-NCERT-EXEMPLAR-9-LINEQ-TWO")
        self.assertEqual(custody["source_status"], "NCERT_AUTHENTIC")
        self.assertEqual(custody["authority_class"], "CURRICULAR_STANDARD")
        self.assertEqual(custody["wording_custody"], "FAITHFUL_NCERT")
        self.assertEqual(custody["provenance_class"], "NCERT_PRACTICE_RECORD")
        self.assertIn("NCERT Exemplar Problems, Class IX Mathematics", source["original_identifier"])
        self.assertEqual(source["stem"], self.question["stem"])
        self.assertEqual(source["answer"]["summary"], self.question["answer"]["summary"])
        self.assertEqual(source["status"], "PUBLISHED")
        self.assertEqual(self.question["status"], "CANDIDATE")

    def test_d02_2_fresh_primary_demand_and_five_component_difficulty_resolve_canonically(self):
        ext = self.question["extensions"]
        difficulty = ext["grade9v3:analysis"]["difficulty"]
        self.assertEqual(difficulty["score"], sum(difficulty["components"].values()))
        self.assertEqual(difficulty["score"], 5)
        self.assertEqual(difficulty["band"], "D2")
        self.assertEqual(ext["grade9v3:cognitive_demand"]["primary"], "MODEL")
        self.assertEqual(self.question["answer"]["crux_move_ref"], "Q37-DEC")

        profile = {
            "profile_id": "ISS69-D02-QUALIFICATION-PROFILE",
            "held": {
                "CAP-MAT-LEQ-04-TWO-VARIABLE-SOLUTIONS": "UNCERTAIN",
                "CAP-MAT-LEQ-02-SAME-OPERATION-BOTH-SIDES": "DEMONSTRATED",
            },
        }
        matrix = qrt.load(qrt.MATRIX_PATH)
        vocab = qrt.load(qrt.VOCAB_PATH)
        resolution = qrt.resolve_review(self.question, profile, matrix, vocab)
        self.assertEqual(resolution["template_id"], "QRT-MODEL-D2")
        self.assertEqual(resolution["classification"]["demand"]["primary_move_ref"], "Q37-DEC")
        self.assertEqual(resolution["classification"]["difficulty_score"], 5)

        specialized = qrt.specialize_resolution(
            resolution,
            json.loads(ADAPTER.read_text(encoding="utf-8")),
        )
        self.assertEqual(specialized["subject"], "Mathematics")
        self.assertEqual(specialized["subject_adapter"]["demand"], "MODEL")

    def test_d02_3_core1a_uses_active_blueprint_and_qualification_owned_visual_without_renderer_fallback(self):
        ctx = fixture.context()
        bp = next(
            row for row in ctx.blueprints["blueprints"]
            if row["id"] == "BP-CORE1A-CONSTRUCTION" and row["status"] == "ACTIVE"
        )
        self.assertEqual(bp["version"], "1.8.0")

        html = render_core.page(ctx, "CORE1A", "SINGLE_FILE", render_core.render_digest(ctx))
        self.assertIn(f'id="{fixture.TARGET_UNIT}"', html)
        self.assertIn('data-g9-representation="REP-MAT-LEQ-04-SOLUTION-LINE"', html)
        self.assertIn("VIS-MAT-LEQ-04-G1", html)
        self.assertIn("VIS-MAT-LEQ-04-G2", html)
        self.assertIn("The step the hard question turns on", html)
        self.assertFalse([gap for gap in ctx.gaps if gap["core"] == "CORE1A"], ctx.gaps)

        rep = next(r for r in self.pkg["representations"] if r["id"] == fixture.REPRESENTATION)
        self.assertEqual(rep["rendered_asset_refs"], [fixture.QUALIFICATION_ASSET])
        canonical_rep = next(r for r in self.canonical["representations"] if r["id"] == fixture.REPRESENTATION)
        self.assertEqual(canonical_rep["rendered_asset_refs"], [])

    def test_d02_4_core2_preserves_authentic_attempt_and_bounded_authored_support(self):
        source, authored = core2_v2.split_pre_solution_support(self.question)
        self.assertEqual(source, [])
        self.assertEqual(len(authored), 3)
        protected = self.question["transfer"]["protected_move_ref"]
        self.assertEqual(protected, "Q37-DEC")
        self.assertTrue(all(row["supports_move_ref"] != protected for row in authored))
        self.assertTrue(all(row["reveals"] != "ANSWER" for row in authored))

        ctx = fixture.context()
        html = render_core.core2(ctx, ctx.selection_rows["core2"][0])
        self.assertIn("Attempt first", html)
        self.assertIn("data-g9-attempt-box", html)
        self.assertIn("data-g9-commit", html)
        self.assertIn(f'data-g9-payload-ref="CORE2-{fixture.WITNESS}-solution"', html)
        self.assertEqual(html.count("template data-g9-rung-payload="), 3)
        self.assertNotIn('data-g9-support-reveals="ANSWER"', html)
        self.assertNotIn('data-g9-figure', html)
        self.assertFalse(
            [gap for gap in ctx.gaps if gap["duty"] == "AUTHOR_LEARNER_METADATA"],
            ctx.gaps,
        )
        self.assertEqual(
            self.question["extensions"]["grade9v3:provenance_class"],
            "ORIGINAL",
        )
        self.assertEqual(
            self.question["extensions"]["grade9v3:analysis"]["exam_source_badge"],
            "NCERT Exemplar · Class IX Mathematics",
        )

    def test_d02_5_concept_detour_targets_exact_construction_and_preserves_question_return(self):
        ctx = fixture.context()
        html = render_core.core2(ctx, ctx.selection_rows["core2"][0])
        expected = (
            f'core1a.html?g9-return={fixture.WITNESS}'
            f'&amp;g9-concept={fixture.MICROTOPIC}#{fixture.TARGET_UNIT}'
        )
        self.assertIn(expected, html)
        self.assertIn(f'data-g9-question-ref="{fixture.WITNESS}"', html)
        self.assertIn(f'data-g9-concept-ref="{fixture.MICROTOPIC}"', html)

        repair = self.question["extensions"]["grade9v3:learning_repair"]
        self.assertEqual(repair["construction_ref"], fixture.TARGET_UNIT)
        self.assertEqual(repair["crux_move_ref"], "Q37-DEC")
        self.assertNotIn("grade9v3:diagnostic_evidence", self.question["extensions"])

    def test_d02_6_fixture_render_is_self_contained_and_current_blueprints_are_visible(self):
        ctx = fixture.context()
        digest = render_core.render_digest(ctx)
        core1a = render_core.page(ctx, "CORE1A", "SINGLE_FILE", digest)
        core2 = render_core.page(ctx, "CORE2", "SINGLE_FILE", digest)
        self.assertIn('data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.8.0"', core1a)
        self.assertIn('data-blueprint-ref="BP-CORE2-SOURCE-QUESTION@1.11.0"', core2)
        self.assertIn("data-g9-tablet-shell", core1a)
        self.assertIn("data-g9-tablet-shell", core2)
        self.assertIn(f'data-g9-render-digest="{digest}"', core1a)
        self.assertIn(f'data-g9-render-digest="{digest}"', core2)


if __name__ == "__main__":
    unittest.main()
