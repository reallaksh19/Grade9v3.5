"""Adversarial tests for source-only completion of the official SOF Class 9 sample."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(RESEARCH))
from validate_seed import SeedError  # noqa: E402
from validate_sample_extension import validate_extension, check_geometric_math  # noqa: E402


class ExtensionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.seed, self.taxonomy, self.extension = (root/x for x in ("seed","taxonomy","verification"))
        for directory in (self.seed,self.taxonomy,self.extension):
            directory.mkdir()
        for file in ("questions.jsonl","sources.json","source_observations.json"):
            (self.seed/file).write_bytes((RESEARCH/"seed"/file).read_bytes())
        (self.taxonomy/"official-sample-2026-27-observations.v1.json").write_bytes(
            (RESEARCH/"taxonomy"/"official-sample-2026-27-observations.v1.json").read_bytes())
        self.document = self.extension/"official-sample-2026-27-new-positions.v1.json"
        self.document.write_bytes((RESEARCH/"verification"/self.document.name).read_bytes())

    def validate(self):
        return validate_extension(self.seed,self.taxonomy,self.extension)

    def mutate(self,change):
        payload=json.loads(self.document.read_text(encoding="utf-8"))
        change(payload)
        self.document.write_text(json.dumps(payload))

    def get(self,document,n):
        return next(x for x in document["entries"] if x["sample_question_number"]==n)

    def test_complete_sample_source_census_without_admission(self):
        outcome=self.validate()
        self.assertEqual(outcome["total_sample_source_positions"],10)
        self.assertEqual(outcome["attachment_seed_questions_unchanged"],66)
        self.assertEqual(outcome["new_sample_source_positions"],2)
        self.assertEqual(outcome["core_ready"],0)

    def test_geometric_independent_math_oracles(self):
        self.assertEqual(check_geometric_math(),(4,49))

    def test_duplicate_new_source_position_refused(self):
        self.mutate(lambda d: d["entries"][1].update(question_id=d["entries"][0]["question_id"],
                                                   sample_question_number=1))
        with self.assertRaises(SeedError):self.validate()

    def test_new_source_cannot_claim_owner_seed_membership(self):
        self.mutate(lambda d: self.get(d,1).update(original_owner_seed_membership=True))
        with self.assertRaises(SeedError):self.validate()

    def test_bogus_source_cannot_be_substituted(self):
        self.mutate(lambda d: self.get(d,3).update(source_url="https://example.invalid/dice.pdf"))
        with self.assertRaises(SeedError):self.validate()

    def test_wrong_dice_answer_fails(self):
        self.mutate(lambda d: self.get(d,1).update(agent_derived_option="A"))
        with self.assertRaises(SeedError):self.validate()

    def test_wrong_circle_number_fails(self):
        self.mutate(lambda d: self.get(d,3).update(independent_mathematical_check="49"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_assumed_rights(self):
        self.mutate(lambda d: self.get(d,1).update(publication_rights_status="CLEARED"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_peer_review_fabrication(self):
        self.mutate(lambda d: self.get(d,3).update(independent_academic_acceptance=True))
        with self.assertRaises(SeedError):self.validate()

    def test_no_qrt_cell_accepted(self):
        self.mutate(lambda d: self.get(d,1).update(accepted_primary_qrt_cell="QRT-REPRESENT-D2"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_original_figure_republication(self):
        self.mutate(lambda d: self.get(d,3).update(original_figure="<svg>raw scanned image</svg>"))
        with self.assertRaises(SeedError):self.validate()

    def test_missing_discovered_source_fails(self):
        self.mutate(lambda d: d["entries"].pop())
        with self.assertRaises(SeedError):self.validate()


if __name__ == "__main__":
    unittest.main()
