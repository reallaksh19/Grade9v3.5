from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools import qrt_pipeline_guard as guard
from Shared.tools import question_review_matrix as qrt
from Shared.tools import render_core


REPO = Path(__file__).resolve().parents[1]
ISS32_MANIFEST = REPO / "evidence/blueprint-cycles/ISS32/inputs/product.manifest.json"
ISS32_BANK = REPO / "evidence/blueprint-cycles/ISS32/inputs/owner.bank.json"
ISS34_BANK = REPO / "evidence/blueprint-cycles/ISS34/inputs/owner.bank.json"
ISS36_BANK = REPO / "evidence/blueprint-cycles/ISS36/inputs/owner.bank.json"
ISS38_BANK = REPO / "evidence/blueprint-cycles/ISS38/inputs/owner.bank.json"
U10 = REPO / "evidence/blueprint-schema/ISS66/u10a-eight-run-integrated-replay.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class PhaseDHistoricalNegativeReplay(unittest.TestCase):
    def test_iss32_q1_protected_crux_is_rejected_when_pre_attempt_reachable(self):
        bank = load(ISS32_BANK)
        q = next(row for row in bank["questions"] if row["id"] == "OWN-ISSUE32-HYBRID-01")
        protected = q["answer"]["crux_move_ref"]
        run = {
            "questions": [{
                "id": q["id"],
                "slots": {"W": {"protected_move_ref": protected}},
            }],
            "pre_attempt_graphs": [{
                "question_ref": q["id"],
                "root": "question",
                "nodes": [
                    {"id": "question", "phase": "PRE_ATTEMPT", "move_refs": [], "links": ["bad-hint"]},
                    {"id": "bad-hint", "phase": "PRE_ATTEMPT", "move_refs": [protected], "links": []},
                ],
            }],
        }
        self.assertEqual(
            guard.validate_pre_attempt_graphs(run),
            [f"W_LEAK_PRE_ATTEMPT_REACHABLE: {q['id']}:bad-hint:{protected}"],
        )

    def test_iss32_q4_visual_replacement_owned_by_another_question_fails_review_binding(self):
        ctx = render_core.context(ISS32_MANIFEST)
        q4 = copy.deepcopy(next(q for q in ctx.selection_rows["core2"] if q["id"] == "OWN-ISSUE32-HYBRID-04"))
        review = q4["extensions"]["grade9v3:core2_visual_review"]
        review["authored_figure_refs"] = ["REP-ACADEMIC-ISS32-Q3"]

        output = render_core._core2_question_figures(ctx, q4, "PRE_ATTEMPT")
        self.assertNotIn('data-g9-representation="REP-ACADEMIC-ISS32-Q3"', output)
        findings = [
            gap for gap in ctx.gaps
            if gap["record"] == q4["id"] and gap["duty"] == "AUTHOR_CORE2_VISUAL_REVIEW"
        ]
        self.assertTrue(findings)

    def test_iss34_noncanonical_template_namespace_cannot_be_qrt_authority(self):
        matrix = qrt.load(qrt.MATRIX_PATH)
        vocab = qrt.load(qrt.VOCAB_PATH)
        canonical = {row["template_id"] for row in qrt.compile_templates(matrix, vocab)}
        self.assertEqual(len(canonical), 28)
        self.assertTrue(all(ref.startswith("QRT-") for ref in canonical))
        self.assertFalse(any(ref.startswith("TMPL-CHEM-G11-") for ref in canonical))

        bank = load(ISS34_BANK)
        recorded = {
            q["extensions"]["grade9v3:qrt_template"]["template_id"]
            for q in bank["questions"]
        }
        self.assertTrue(recorded <= canonical)

    def test_iss36_equal_scaffold_count_does_not_define_semantic_sufficiency(self):
        bank = load(ISS36_BANK)
        five = [q for q in bank["questions"] if len(q.get("scaffolds", [])) == 5]
        self.assertGreaterEqual(len(five), 6)
        demands = {
            q["extensions"]["grade9v3:analysis"]["cognitive_demand"]["primary"]
            for q in five
        }
        templates = {
            q["extensions"]["grade9v3:qrt_template"]["template_id"]
            for q in five
        }
        self.assertGreaterEqual(len(demands), 4)
        self.assertGreaterEqual(len(templates), 4)

        # Same count, different learner-owned acts: cardinality cannot substitute
        # for the demand-specific QRT semantics.
        counts = {len(q["scaffolds"]) for q in five}
        self.assertEqual(counts, {5})

    def test_iss38_canonical_review_facets_cannot_be_replaced_by_invented_system(self):
        schema = load(REPO / "Shared/quality/qrt-pipeline-run.schema.json")
        check = Draft202012Validator({
            "$schema": schema["$schema"],
            "$ref": "#/$defs/semanticReview",
            "$defs": schema["$defs"],
        })
        invented = {
            "question_ref": "OWN-ISSUE38-HYB-01",
            "basis": "AUTHOR_ONLY",
            "judgements": {
                "A1": {"verdict": "YES", "evidence": "Invented replacement facet."},
                "A2": {"verdict": "YES", "evidence": "Invented replacement facet."},
            },
        }
        self.assertTrue(list(check.iter_errors(invented)))

        matrix = qrt.load(qrt.MATRIX_PATH)
        vocab = qrt.load(qrt.VOCAB_PATH)
        for template in qrt.compile_templates(matrix, vocab):
            self.assertEqual(tuple(template["review"]), qrt.ASKS)

    def test_iss38_every_crux_is_owned_by_its_own_question_route(self):
        bank = load(ISS38_BANK)
        questions = bank["questions"]
        self.assertEqual(len(questions), 10)
        for q in questions:
            route_ids = {move["id"] for move in q["answer"]["reasoning_route"]}
            crux = q["answer"]["crux_move_ref"]
            self.assertIn(crux, route_ids)
            self.assertTrue(crux.startswith(q["id"] + "-"))

        q1 = questions[0]
        q10 = questions[-1]
        self.assertNotIn(
            q10["answer"]["crux_move_ref"],
            {move["id"] for move in q1["answer"]["reasoning_route"]},
        )

    def test_iss32_34_36_38_historical_receipts_are_evidence_not_acceptance(self):
        for issue in (32, 34, 36, 38):
            with self.subTest(issue=issue):
                receipt = load(REPO / f"evidence/blueprint-cycles/ISS{issue}/cycle-receipt.json")
                self.assertEqual(receipt["status"], "CANDIDATE")
                self.assertFalse(receipt["golden"])
                self.assertFalse(receipt["all_12_facets_independently_certified"])
                self.assertEqual(receipt["browser"], "NOT_RUN")

    def test_49_through_56_classification_claims_remain_replay_required(self):
        replay = load(U10)
        rows = {row["issue"]: row for row in replay["runs"]}
        self.assertEqual(set(rows), set(range(49, 57)))
        for issue in range(49, 57):
            with self.subTest(issue=issue):
                self.assertEqual(
                    rows[issue]["replay"]["difficulty_qrt"]["status"],
                    "REPLAY_REQUIRED",
                )
        coverage = replay["accepted_primary_coverage"]
        self.assertEqual(coverage["accepted_cells_from_u10a"], 0)
        self.assertEqual(coverage["status"], "REPLAY_REQUIRED")


if __name__ == "__main__":
    unittest.main()
