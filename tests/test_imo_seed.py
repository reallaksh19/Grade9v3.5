"""Adversarial regression tests for the SOF IMO research-only seed guard."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(SRC))
from validate_seed import SeedError, validate  # noqa: E402


class SeedTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        for filename in ("questions.jsonl", "sources.json", "source_observations.json"):
            (self.root / filename).write_bytes((SRC / "seed" / filename).read_bytes())

    def get_questions(self):
        return [json.loads(x) for x in (self.root / "questions.jsonl").read_text().splitlines()]

    def put_questions(self, questions):
        (self.root / "questions.jsonl").write_text("\n".join(json.dumps(q) for q in questions) + "\n")

    def mutate_ledger(self, apply):
        p = self.root / "sources.json"
        data = json.loads(p.read_text())
        apply(data)
        p.write_text(json.dumps(data))

    def mutate_observations(self, apply):
        p = self.root / "source_observations.json"
        data = json.loads(p.read_text())
        apply(data)
        p.write_text(json.dumps(data))

    def test_printed_q44_uses_everyday_math(self):
        q = next(q for q in self.get_questions() if q["seed_entry"] == 9)
        self.assertEqual(q["exam_section"], "EVERYDAY_MATHEMATICS")

    def test_q44_cannot_revert_to_mathematical_reasoning(self):
        qs = self.get_questions()
        next(q for q in qs if q["seed_entry"] == 9)["exam_section"] = "MATHEMATICAL_REASONING"
        self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_valid_seed_is_research_only(self):
        result = validate(self.root)
        self.assertEqual((result["candidate_questions"], result["aliases"], result["ready_for_core"]), (66, 3, 0))
        self.assertEqual(result["accepted_qrt_cells"], 0)

    def test_duplicate_id(self):
        qs = self.get_questions()
        qs[1]["id"] = qs[0]["id"]
        self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_duplicate_locator_even_if_id_changes(self):
        qs = self.get_questions()
        qs[1]["source_id_claim"] = qs[0]["source_id_claim"]
        qs[1]["source_url_claim"] = qs[0]["source_url_claim"]
        qs[1]["original_question_number_claim"] = qs[0]["original_question_number_claim"]
        self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_broken_alias(self):
        self.mutate_ledger(lambda l: l["aliases"][0].update(alias_of_entry=99))
        with self.assertRaises(SeedError): validate(self.root)

    def test_wrong_organizer_host(self):
        self.mutate_ledger(lambda l: l["sources"][3].update(url="https://sofworld.org.evil.org/imo"))
        with self.assertRaises(SeedError): validate(self.root)

    def test_no_silent_core_promotion(self):
        qs = self.get_questions(); qs[0]["core_eligible"] = True; self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_no_unverified_source_promotion(self):
        self.mutate_ledger(lambda l: l["sources"][0].update(source_verification_status="VERIFIED"))
        with self.assertRaises(SeedError): validate(self.root)

    def test_no_unsubstantiated_answer_key(self):
        self.mutate_ledger(lambda l: l["sources"][0].update(answer_key_verified=True))
        with self.assertRaises(SeedError): validate(self.root)

    def test_no_silent_dispute_clearance(self):
        qs = self.get_questions()
        next(q for q in qs if q["seed_entry"] == 2)["transcription_status"] = "NOT_VERIFIED"
        self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_split_cannot_be_lost(self):
        qs = self.get_questions()
        next(q for q in qs if q["seed_entry"] == 38 and q["seed_subentry"] == "ii")["seed_subentry"] = "i"
        self.put_questions(qs)
        with self.assertRaises(SeedError): validate(self.root)

    def test_observation_must_refer_to_real_question(self):
        self.mutate_observations(lambda o: o["records"][0].update(question_id="FAKE"))
        with self.assertRaises(SeedError): validate(self.root)

    def test_missing_figure_observation_page(self):
        self.mutate_observations(lambda o: o["records"][2].pop("pdf_page_index"))
        with self.assertRaises(SeedError): validate(self.root)


if __name__ == "__main__": unittest.main()
