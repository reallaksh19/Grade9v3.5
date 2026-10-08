"""Adversarial regression tests for SOF IMO full-paper mathematics audit B02."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

BASE=Path(__file__).resolve().parents[1]/"TEST"/"imo-research"
sys.path.insert(0,str(BASE))
from validate_seed import SeedError  # noqa: E402
from validate_fullpaper_batch02 import validate_batch02, mathematical_oracles  # noqa: E402


class FullPaperB02Tests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root=Path(self.temp.name)
        self.seed=self.root/"seed"
        self.verify=self.root/"verification"
        self.seed.mkdir();self.verify.mkdir()
        for name in ("questions.jsonl","sources.json","source_observations.json","math_audit_batch01.json"):
            (self.seed/name).write_bytes((BASE/"seed"/name).read_bytes())
        self.batch=self.verify/"fullpaper-source-math-batch02.v1.json"
        self.batch.write_bytes((BASE/"verification"/self.batch.name).read_bytes())

    def validate(self):
        return validate_batch02(self.seed,self.batch)

    def alter(self, fn):
        d=json.loads(self.batch.read_text())
        fn(d)
        self.batch.write_text(json.dumps(d))

    def entry(self, doc,number):
        return next(x for x in doc["observations"] if x["owner_compilation_entry"]==number)

    def test_exact_15_research_only(self):
        d=self.validate()
        self.assertEqual((d["new_source_positions_reviewed"],d["cumulative_fullpaper_agent_reviewed"],
                          d["new_choice_disagreements"],d["qrt_accepted"]), (15,31,1,0))

    def test_predecessor_digit_math_oracle(self):
        oracle=mathematical_oracles()
        self.assertEqual(oracle[("2023-24-A",13)],"Fourth sorted predecessor digit = 5")
        self.assertEqual(oracle[("2024-25-B",27)],"1/6")

    def test_cannot_erase_wrong_compiler_choice(self):
        self.alter(lambda d: self.entry(d,46).update(owner_compilation_claimed_choice="B"))
        with self.assertRaises(SeedError):self.validate()

    def test_cannot_change_derived_choice(self):
        self.alter(lambda d: self.entry(d,46).update(printed_correct_choice_by_agent="C"))
        with self.assertRaises(SeedError):self.validate()

    def test_cannot_silently_clear_dispute(self):
        self.alter(lambda d: self.entry(d,46).update(disposition="NO_COMPLICATION"))
        with self.assertRaises(SeedError):self.validate()

    def test_cannot_change_computed_math(self):
        self.alter(lambda d: self.entry(d,25).update(independent_agent_answer="12sqrt(15) cm^2"))
        with self.assertRaises(SeedError):self.validate()

    def test_cannot_drop_source_position(self):
        self.alter(lambda d: d["observations"].pop())
        with self.assertRaises(SeedError):self.validate()

    def test_duplicate_original_question_fails(self):
        self.alter(lambda d: d["observations"][1].update(question_id=d["observations"][0]["question_id"]))
        with self.assertRaises(SeedError):self.validate()

    def test_original_page_index_is_essential(self):
        self.alter(lambda d: self.entry(d,46).update(source_pdf_page_index=1))
        with self.assertRaises(SeedError):self.validate()

    def test_source_host_identity_is_immutable(self):
        self.alter(lambda d: self.entry(d,42).update(source_url="https://example.com/paper.pdf"))
        with self.assertRaises(SeedError):self.validate()

    def test_official_key_cannot_be_assumed(self):
        self.alter(lambda d: self.entry(d,19).update(source_answer_key_receipt="OFFICIAL_KEY"))
        with self.assertRaises(SeedError):self.validate()

    def test_academic_review_cannot_be_forged(self):
        self.alter(lambda d: self.entry(d,40).update(second_independent_academic_reviewer="SIGNED"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_unapproved_qrt_admission(self):
        self.alter(lambda d: self.entry(d,13).update(qrt_accepted_cell="QRT-APPLY-D2"))
        with self.assertRaises(SeedError):self.validate()

    def test_no_original_question_text_copied(self):
        self.alter(lambda d: self.entry(d,7).update(stem="Original paper verbatim question text"))
        with self.assertRaises(SeedError):self.validate()


if __name__=="__main__":
    unittest.main()
