"""Independent Core/assessment contract checks for a rights-safe Core2A → Core1A journey.

No authentic-source Core2 is synthesized; QRT resolution uses the original
7-demand × D1–D4 compiler and its existing semantic review asks.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import product_manifest, product_coverage, question_review_matrix as qrt, render_core

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "TEST/library/core1a-render-qualified-divisibility.v1.json"
MANIFEST = ROOT / "TEST/products/core-authored-qrt-repair-journey.manifest.json"
ORIGINAL_MANIFEST = ROOT / "TEST/products/core1a-divisibility-render-maturity.manifest.json"
QUESTION_ID = "Q-TEST-CORE2A-THREE-ADJACENT-PRODUCT-PROOF"
CAPABILITY = "CAP-TEST-CORE1A-QUAL-G9-UNIVERSAL-DIVISIBILITY"


def records():
    pkg = json.loads(PACK.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    question = next(q for q in pkg["questions"] if q["id"] == QUESTION_ID)
    return pkg, manifest, question


class AuthoredQRTRepairJourneyTests(unittest.TestCase):
    def test_provenance_and_manifest_keep_original_source_core2_absent(self):
        pkg, manifest, question = records()
        self.assertEqual(pkg["subject"], "TEST")
        self.assertEqual(pkg["status"], "CANDIDATE")
        self.assertEqual(question["origin"], "AUTHORED")
        self.assertEqual(question["source_refs"], ["SRC-TEST-CORE1A-QUAL-G9-NS-AUTHORED"])
        self.assertEqual(question["exposure"][0]["core"], "CORE2A")
        self.assertEqual(manifest["output_roles"], ["CORE1A", "CORE2A"])
        self.assertEqual(manifest["selection"]["core2"], [])
        self.assertEqual(manifest["selection"]["core2b"], [])
        self.assertEqual(manifest["selection"]["core2a"], [QUESTION_ID])
        self.assertEqual(manifest["bank_refs"], [])
        self.assertNotIn("SOF", question["stem"])
        self.assertFalse(pkg["extensions"]["grade9v3:core2_source_custody_granted"])
        self.assertFalse(pkg["extensions"]["grade9v3:qrt_admitted"])
        self.assertFalse(pkg["extensions"]["grade9v3:learner_published"])
        selected = product_manifest.validate_selection(manifest, [pkg], [])
        self.assertEqual([q["id"] for q in selected["core2a"]], [QUESTION_ID])
        product_coverage.validate(manifest, product_manifest.derivable([pkg], []))
        core_only = json.loads(ORIGINAL_MANIFEST.read_text(encoding="utf-8"))
        self.assertIn(QUESTION_ID, core_only["coverage"]["omitted"])
        self.assertEqual(core_only["output_roles"], ["CORE1A"])

    def test_qrt_resolves_exact_justify_d2_cell_without_reclassification(self):
        _, _, q = records()
        m, v = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        self.assertEqual(qrt.check_paths(), [])
        profile = {
            "profile_id": "SYNTHETIC-CORE-JOURNEY-UNKNOWN",
            "provenance": "SYNTHETIC_TEST_ONLY",
            "held": {CAPABILITY: "UNCERTAIN"},
            "knowledge_percentage": 95,
            "measured_fit_claim": False,
        }
        out = qrt.resolve_review(q, profile, m, v)
        self.assertEqual(out["template_id"], "QRT-JUSTIFY-D2")
        self.assertEqual(out["classification"]["demand"]["primary"], "JUSTIFY")
        self.assertEqual(out["classification"]["band"], "D2")
        self.assertEqual(out["classification"]["difficulty_score"], 4)
        self.assertEqual(out["classification"]["demand"]["primary_move_ref"],
                         q["answer"]["crux_move_ref"])
        self.assertIn(CAPABILITY + " is UNCERTAIN", out["slots"]["X"]["text"])
        self.assertIn("UNRESOLVED", out["slots"]["Y"]["text"])
        self.assertIn("exhaustive three possible residues", out["slots"]["W"]["text"])
        self.assertEqual(tuple(out["review"]), qrt.ASKS)
        for row in out["review"].values():
            self.assertIn(row["verb"], (
                "CLARIFY", "CORRELATE", "OPEN_THE_WAY", "PROTECT",
                "ROUTE", "EXPLAIN_AND_CHECK", "DIAGNOSE", "DETECT", "REPAIR",
            ))
        # Learner percentage is summary metadata, not cell selection or mastery.
        profile["knowledge_percentage"] = 10
        low = qrt.resolve_review(q, profile, m, v)
        self.assertEqual(low["template_id"], out["template_id"])
        self.assertEqual(low["slots"], out["slots"])

    def test_qrt_refuses_fabricated_band_or_missing_protected_move(self):
        _, _, q = records()
        import copy
        m, v = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH)
        profile = {"profile_id": "SYNTHETIC-NO-MASTERY", "held": {}, "provenance": "SYNTHETIC_TEST_ONLY"}
        wrong = copy.deepcopy(q)
        wrong["difficulty"]["band"] = "D4"
        with self.assertRaisesRegex(qrt.QRTContractError, "QUESTION_DIFFICULTY_BAND_MISMATCH"):
            qrt.resolve_review(wrong, profile, m, v)
        wrong = copy.deepcopy(q)
        wrong["answer"]["crux_move_ref"] = "NONEXISTENT"
        with self.assertRaisesRegex(qrt.QRTContractError, "COGNITIVE_DEMAND_CRUX_MOVE_UNRESOLVED"):
            qrt.resolve_review(wrong, profile, m, v)

    def test_reasoning_route_teaches_exact_concept_without_relabelling_transfer(self):
        pkg, manifest, q = records()
        route = q["answer"]["reasoning_route"]
        self.assertEqual(len(route), 4)
        self.assertEqual(q["answer"]["crux_move_ref"], route[2]["id"])
        self.assertTrue(all(step["why_valid"] for step in route))
        self.assertEqual(q["repair_ref"], "TC-03")
        steps = {step["id"] for micro in pkg["microtopics"] for step in micro["teaching_path"]}
        self.assertIn(q["repair_ref"], steps)
        self.assertEqual(q["family_ref"], pkg["question_families"][0]["id"])
        self.assertEqual(q["family_exposure"]["family_ref"], q["family_ref"])
        self.assertNotIn("transfer", q)
        self.assertEqual(len(q["hint_ladder"]), 3)
        self.assertTrue(all(ref["cores"] == ["CORE2A"] for rep in pkg["representations"]
                            if rep["id"] == q["representation_roles"]["initial_ref"]
                            for ref in rep["scene_instances"]))
        self.assertEqual(q["representation_roles"]["stage_refs"], ["PRACTICE-FACTORS-ONLY"])
        initial_rep = next(rep for rep in pkg["representations"]
                           if rep["id"] == q["representation_roles"]["initial_ref"])
        self.assertFalse(any("parity" in label.lower() or "divisibility by 6" in label.lower()
                             for label in initial_rep["read_order"] + initial_rep["required_elements"]))
        # A single supported-practice question must not be treated as a sample of all 28 cells.
        self.assertEqual(len(manifest["selection"]["core2a"]), 1)

    def test_connected_product_builds_three_scoped_pages_with_clickable_repair(self):
        _, _, q = records()
        pages, gaps, _, advice, waivers = render_core.build_report(
            MANIFEST, "PAGES", held_to="REFERENCE"
        )
        self.assertEqual(set(pages), {"index.html", "core1a.html", "core2a.html"})
        self.assertEqual(gaps, [], gaps)
        self.assertEqual(advice, [], advice)
        self.assertEqual(waivers, [], waivers)
        a, b = pages["core1a.html"], pages["core2a.html"]
        self.assertIn(q["id"], b)
        self.assertIn("AUTHORED", b)
        self.assertIn("core1a.html#CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF", b)
        self.assertIn('data-g9-repair-ref="TC-03"', b)
        self.assertIn('data-g9-stage="PRE_ATTEMPT"', b)
        self.assertIn("PRACTICE-FACTORS-ONLY", b)
        self.assertIn('data-g9-stage="POST_ATTEMPT"', b)
        self.assertIn('id="CU-TEST-CORE1A-QUAL-G9-CONSECUTIVE-FACTOR-PROOF"', a)
        self.assertNotIn('data-g9-role="CORE2"', b)
        self.assertNotIn("SOF-IMO-G09-", b)
        self.assertNotIn('data-g9-role="CORE2B"', b)


if __name__ == "__main__":
    unittest.main()
