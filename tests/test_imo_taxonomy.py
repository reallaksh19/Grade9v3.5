"""Negative source-identity and academic-overclaim tests for IMO topic mapping."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

RESEARCH = Path(__file__).resolve().parents[1] / "TEST" / "imo-research"
sys.path.insert(0, str(RESEARCH))
from validate_seed import SeedError  # noqa: E402
from validate_taxonomy import validate_taxonomy  # noqa: E402


class TopicMapTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        root = Path(self.tmp.name)
        self.seed, self.taxonomy = root / "seed", root / "taxonomy"
        self.seed.mkdir(); self.taxonomy.mkdir()
        for filename in ("questions.jsonl", "sources.json", "source_observations.json"):
            (self.seed / filename).write_bytes((RESEARCH / "seed" / filename).read_bytes())
        for filename in ("sof-class9-topic-registry.v1.json", "seed-question-topic-map.v1.jsonl"):
            (self.taxonomy / filename).write_bytes((RESEARCH / "taxonomy" / filename).read_bytes())

    def run_audit(self):
        return validate_taxonomy(self.seed, self.taxonomy)

    def mutate_map(self, edit):
        p = self.taxonomy / "seed-question-topic-map.v1.jsonl"
        rows = [json.loads(x) for x in p.read_text().splitlines()]
        edit(rows)
        p.write_text("\n".join(json.dumps(x) for x in rows) + "\n")

    def mutate_registry(self, edit):
        p = self.taxonomy / "sof-class9-topic-registry.v1.json"
        data = json.loads(p.read_text())
        edit(data)
        p.write_text(json.dumps(data))

    def test_valid_coverage_is_not_accepted_qrt(self):
        outcome = self.run_audit()
        self.assertEqual(outcome["mapped_questions"], 66)
        self.assertEqual(outcome["official_topics"], 17)
        self.assertEqual(outcome["accepted_qrt_cells"], 0)
        self.assertEqual(outcome["core_eligible"], 0)
        self.assertEqual(outcome["by_topic"]["STATISTICS"], 4)

    def test_no_duplicate_question_identity(self):
        self.mutate_map(lambda rows: rows[1].update(question_id=rows[0]["question_id"]))
        with self.assertRaises(SeedError): self.run_audit()

    def test_missing_question_cannot_be_silent(self):
        self.mutate_map(lambda rows: rows.pop())
        with self.assertRaises(SeedError): self.run_audit()

    def test_unknown_topic_cannot_be_added(self):
        self.mutate_map(lambda rows: rows[0].update(primary_topic_id="MY_OLYMPIAD_CATEGORY"))
        with self.assertRaises(SeedError): self.run_audit()

    def test_source_identity_cannot_change(self):
        self.mutate_map(lambda rows: rows[0].update(source_id="FAKE_SOURCE"))
        with self.assertRaises(SeedError): self.run_audit()

    def test_new_research_status_cannot_be_relabelled_accepted(self):
        self.mutate_map(lambda rows: rows[0].update(academic_taxonomy_status="ACCEPTED"))
        with self.assertRaises(SeedError): self.run_audit()

    def test_qrt_cell_cannot_be_claimed_without_evidence(self):
        self.mutate_map(lambda rows: rows[0].update(accepted_primary_qrt_cell="QRT-JUSTIFY-D4"))
        with self.assertRaises(SeedError): self.run_audit()

    def test_achievers_is_exam_section_not_topic(self):
        def changed(rows):
            row = next(x for x in rows if x["attachment_entry"] == 65)
            row["primary_topic_id"] = "ACHIEVERS_SECTION"
        self.mutate_map(changed)
        with self.assertRaises(SeedError): self.run_audit()

    def test_sample_question_not_assigned_full_paper_section(self):
        def changed(rows):
            row = next(x for x in rows if x["source_id"].startswith("SOF-IMO-G09-SAMPLE"))
            row["full_paper_exam_section"] = "LOGICAL_REASONING"
        self.mutate_map(changed)
        with self.assertRaises(SeedError): self.run_audit()

    def test_q44_wrong_mathematical_reasoning_section(self):
        def changed(rows):
            row = next(x for x in rows if x["attachment_entry"] == 9)
            row["full_paper_exam_section"] = "MATHEMATICAL_REASONING"
        self.mutate_map(changed)
        with self.assertRaises(SeedError): self.run_audit()

    def test_critical_original_topic_syllabus_removed(self):
        self.mutate_registry(lambda d: d["official_topics"].pop())
        with self.assertRaises(SeedError): self.run_audit()

    def test_adjunct_cannot_be_presented_as_official_math(self):
        self.mutate_registry(lambda d: d["adjunct_topics"][1].update(official_syllabus=True))
        with self.assertRaises(SeedError): self.run_audit()

    def test_chart_subquestions_remain_separate(self):
        def changed(rows):
            row = next(x for x in rows if x["attachment_entry"] == 38 and x["attachment_subentry"] == "ii")
            row["subtopic_id"] = "STATISTICS-DATA-DISPLAYS"
        self.mutate_map(changed)
        with self.assertRaises(SeedError): self.run_audit()

    def test_subtopic_must_belong_to_primary_topic(self):
        self.mutate_map(lambda rows: rows[0].update(subtopic_id="ANGLES-VERTICALLY-OPPOSITE"))
        with self.assertRaises(SeedError): self.run_audit()


if __name__ == "__main__":
    unittest.main()
