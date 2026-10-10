"""Check a proposed eight-position Batch A map against upstream evidence; no admissions."""
from __future__ import annotations

import json
import unittest
from fractions import Fraction as F
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
IMO = ROOT / "TEST" / "imo-research"
BATCH = IMO / "batches" / "batch-a-number-systems-capabilities.v1.json"


def read(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class BatchANumberSystemsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(BATCH.read_text(encoding="utf-8"))
        cls.census = read("TEST/imo-research/intake/core2-source-custody-eligibility.v1.json")
        cls.topics = [
            json.loads(x)
            for x in (IMO / "taxonomy" / "seed-question-topic-map.v1.jsonl")
            .read_text(encoding="utf-8").splitlines() if x.strip()
        ]
        cls.sources = {
            "TEST/imo-research/seed/math_audit_batch01.json": "questions",
            "TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json": "observations",
            "TEST/imo-research/verification/fullpaper-audit-b04.v1.json": "records",
            "TEST/imo-research/verification/official-sample-2026-27-math-qrt-pilot.v1.json": "records",
        }

    def test_exact_denominator_and_source_identity(self):
        self.assertEqual(self.doc["programme_source_position_denominator"], 68)
        self.assertEqual(self.doc["batch_source_positions"], 8)
        self.assertEqual(len(self.census["records"]), 68)
        self.assertEqual(self.doc["authored_practice_separate"], 7)
        expected = {q["question_id"] for q in self.topics if q["primary_topic_id"] == "NS"}
        actual = {q["question_id"] for q in self.doc["records"]}
        self.assertEqual(len(expected), 8)
        self.assertEqual(actual, expected)
        self.assertEqual(len(actual), len(self.doc["records"]))
        byid = {r["question_id"]: r for r in self.census["records"]}
        bytopic = {r["question_id"]: r for r in self.topics}
        for r in self.doc["records"]:
            with self.subTest(r=r["question_id"]):
                original = byid[r["question_id"]]
                self.assertEqual(r["source_id"], original["source_id"])
                self.assertEqual(r["source_url"], original["source_document_url"])
                self.assertEqual(r["original_printed_position"], bytopic[r["question_id"]]["original_q"])
                self.assertEqual(r["provisional_taxonomy_subtopic"], bytopic[r["question_id"]]["subtopic_id"])
                self.assertEqual(r["owner_attachment_entry"], bytopic[r["question_id"]]["attachment_entry"])

    def test_audits_are_exact_references_not_new_source_keys(self):
        for row in self.doc["records"]:
            path = row["source_math_evidence"]["file"]
            self.assertIn(path, self.sources)
            candidates = read(path)[self.sources[path]]
            matches = [q for q in candidates if q["question_id"] == row["question_id"]]
            self.assertEqual(len(matches), 1, row["question_id"])
            source = matches[0]
            self.assertEqual(row["source_pdf_page_index"], source["source_pdf_page_index"])
            self.assertEqual(row["source_math_evidence"]["math_selected_printed_option"],
                             source.get("math_derived_printed_choice",
                                        source.get("printed_correct_choice_by_agent",
                                                   source.get("printed_choice_selected_by_math",
                                                              source.get("agent_derived_option")))))
            self.assertEqual(row["source_math_evidence"]["official_key"] ==
                             "SAMPLE_PRINTED_KEY_D_SIGHTED",
                             row["source_kind"] == "SOF_ORGANIZER_HOSTED_SAMPLE")

    def test_dispute_holds_are_preserved(self):
        conflicts = read("TEST/imo-research/adjudication/source-discrepancy-register.v1.json")
        all_conflicts = {qid: case["case_id"] for case in conflicts["cases"] for qid in case["question_ids"]}
        for r in self.doc["records"]:
            actual = r["source_conflict"]["case_id"] if r["source_conflict"] else None
            self.assertEqual(actual, all_conflicts.get(r["question_id"]))
        self.assertEqual({r["source_conflict"]["case_id"] for r in self.doc["records"]
                          if r["source_conflict"]},
                         {"IMO-SOURCE-CONFLICT-003", "IMO-SOURCE-CONFLICT-006",
                          "IMO-SOURCE-CONFLICT-010"})

    def test_fail_closed_product_and_mapping(self):
        for key in ("independent_peer_admissions", "core2_eligible", "core2_admitted",
                    "core1a_canonical_admitted", "accepted_qrt_cells",
                    "publisher_rights_granted", "new_official_source_key_claims",
                    "rendered_core2_html_pdf"):
            self.assertEqual(self.doc[key], 0, key)
        self.assertEqual(self.doc["core1a_pilot_alignment"],
                         "NO_EVIDENCED_SOURCE_CRUX_CONNECTION_FROM_THIS_BATCH")
        for r in self.doc["records"]:
            custody, teaching = r["source_custody"], r["capability_proposal"]
            self.assertFalse(custody["pdf_retained_in_canonical_custody"])
            self.assertFalse(custody["source_reuse_permission"])
            self.assertFalse(custody["source_core2_eligible"])
            self.assertFalse(custody["source_core2_admitted"])
            self.assertIsNone(r["qrt"]["accepted_cell"])
            self.assertFalse(r["core1a"]["canonical_admission"])
            self.assertFalse(r["core1a"]["existing_divisibility_candidate_claimed_alignment"])
            self.assertEqual(r["learner_render"], "NOT_AVAILABLE")
            for name in ("decisive_inference", "mathematical_warrant",
                         "predicted_wrong_path", "crux_reuse_boundary", "teaching_connection"):
                self.assertTrue(teaching[name], r["question_id"] + ": " + name)

    def test_recompute_bounded_mathematical_oracles(self):
        self.assertEqual(-(F(1, 4) - (F(-2, 3) + F(1, 2))), F(-5, 12))
        self.assertEqual(F(-16, 35) / F(-15, 14), F(32, 75))
        self.assertEqual(F(5, 5 + 3), F(5, 8))
        self.assertEqual(F(5-3, 8+2), F(1, 5))
        self.assertEqual(5 * (25 ** (2-1)), 25 ** (2-1) + 100)
        self.assertEqual(F(125 - 4 - 64, 1) / (F(5, 3) + 1 + F(1, 2)), 18)
        self.assertEqual(105 * 105 - 111, 10914)
        self.assertEqual(12 + 2 * 5, 22)
        self.assertEqual(F(25, 2) / F(1000, 3), F(3, 80))


if __name__ == "__main__":
    unittest.main()
