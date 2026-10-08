"""Adversarial tests for the SOF organizer sample mathematics / QRT research pilot."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(ROOT))
from validate_seed import SeedError  # noqa: E402
from validate_sample_pilot import check_pilot  # noqa: E402


class SamplePilotTests(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.seed = root / "seed"
        self.tax = root / "taxonomy"
        self.verify = root / "verification"
        for d in (self.seed,self.tax,self.verify):
            d.mkdir()
        for filename in ("questions.jsonl","sources.json","source_observations.json"):
            (self.seed / filename).write_bytes((ROOT/"seed"/filename).read_bytes())
        for filename in ("sof-class9-topic-registry.v1.json","sof-class9-subtopics.v1.json",
                         "official-sample-2026-27-observations.v1.json","seed-question-topic-map.v1.jsonl"):
            (self.tax / filename).write_bytes((ROOT/"taxonomy"/filename).read_bytes())
        self.pilot = self.verify / "official-sample-2026-27-math-qrt-pilot.v1.json"
        self.pilot.write_bytes((ROOT/"verification"/self.pilot.name).read_bytes())

    def check(self):
        return check_pilot(self.seed,self.tax,self.pilot)

    def mutate(self,fn):
        d=json.loads(self.pilot.read_text())
        fn(d)
        self.pilot.write_text(json.dumps(d))

    def sample(self,data,number):
        return next(x for x in data["records"] if x["sample_question_number"]==number)

    def test_pilot_safely_research_only(self):
        r=self.check()
        self.assertEqual((r["agent_calculated"],r["distinct_proposed_qrt_cells"],
                          r["accepted_qrt_cells"],r["on_figure_hold"]), (7,6,0,1))

    def test_duplicate_source_identity_refused(self):
        self.mutate(lambda d: d["records"][1].update(question_id=d["records"][0]["question_id"]))
        with self.assertRaises(SeedError):self.check()

    def test_organizer_answer_tamper_refused(self):
        self.mutate(lambda d: self.sample(d,8).update(organizer_printed_key="A"))
        with self.assertRaises(SeedError):self.check()

    def test_mathematics_mismatch_refused(self):
        self.mutate(lambda d: self.sample(d,7).update(answer_meaning="Rs 80"))
        with self.assertRaises(SeedError):self.check()

    def test_no_invented_q5_solution_or_demand(self):
        self.mutate(lambda d: self.sample(d,5).update(agent_derived_option="C"))
        with self.assertRaises(SeedError):self.check()

    def test_source_transcription_conflict_must_remain(self):
        self.mutate(lambda d: self.sample(d,9).update(source_vs_owner_transcription_status="RECONCILED"))
        with self.assertRaises(SeedError):self.check()

    def test_no_unsubstantiated_qrt_promotion(self):
        self.mutate(lambda d: self.sample(d,2).update(accepted_qrt_cell="QRT-REPRESENT-D2"))
        with self.assertRaises(SeedError):self.check()

    def test_no_core_promotion(self):
        self.mutate(lambda d: self.sample(d,2).update(core_eligible=True))
        with self.assertRaises(SeedError):self.check()

    def test_wrong_difficulty_sum_fails(self):
        def change(d):
            self.sample(d,7)["qrt_proposal"]["score"]=9
        self.mutate(change)
        with self.assertRaises(SeedError):self.check()

    def test_wrong_derived_band_fails(self):
        def change(d):
            self.sample(d,7)["qrt_proposal"]["band"]="D4"
        self.mutate(change)
        with self.assertRaises(SeedError):self.check()

    def test_difficulty_not_an_allowed_boolean(self):
        def change(d):
            self.sample(d,8)["qrt_proposal"]["score_components"]["concept_model_selection"]=True
        self.mutate(change)
        with self.assertRaises(SeedError):self.check()

    def test_no_unsupported_demand(self):
        def change(d):
            self.sample(d,2)["qrt_proposal"]["primary_demand"]="MEMORIZE"
        self.mutate(change)
        with self.assertRaises(SeedError):self.check()

    def test_no_unlicensed_original_question_stem(self):
        def change(d):
            self.sample(d,4)["stem"]="Original full exam text"
        self.mutate(change)
        with self.assertRaises(SeedError):self.check()

    def test_wrong_sample_section_fails(self):
        self.mutate(lambda d: self.sample(d,9).update(source_section="LOGICAL_REASONING"))
        with self.assertRaises(SeedError):self.check()

    def test_official_source_host_cannot_be_swapped(self):
        self.mutate(lambda d: d.update(source_url="https://example.invalid/sample.pdf"))
        with self.assertRaises(SeedError):self.check()


if __name__=="__main__":
    unittest.main()
