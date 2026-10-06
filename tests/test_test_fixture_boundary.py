from __future__ import annotations

import json
import unittest
from collections import Counter
from pathlib import Path

from Shared.tools import build_learner_search_index, build_question_bank_web


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "TEST/question-bank/fixtures/pr61-math-42.fixture.json"


class TestTestFixtureBoundary(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.doc = json.loads(FIXTURE.read_text(encoding="utf-8"))

    def test_fixture_freezes_exactly_42_unique_coordinates_across_seven_topics(self):
        refs = self.doc["question_refs"]
        ids = [row["id"] for row in refs]
        topics = Counter(row["topic_label"] for row in refs)

        self.assertEqual(self.doc["question_count"], 42)
        self.assertEqual(len(refs), 42)
        self.assertEqual(len(set(ids)), 42)
        self.assertEqual(len(topics), 7)
        self.assertEqual(set(topics.values()), {6})
        self.assertEqual(self.doc["authority_status"], "UNVERIFIED_SANDBOX_FIXTURE")
        self.assertEqual(
            self.doc["excluded_provider_head"]["excluded_placeholder_records"],
            168,
        )

    def test_fixture_ids_are_absent_from_canonical_question_bank(self):
        fixture_ids = {row["id"] for row in self.doc["question_refs"]}
        projection = build_question_bank_web.build(REPO)
        canonical_ids = {row["id"] for row in projection["questions"]}

        self.assertTrue(fixture_ids.isdisjoint(canonical_ids))
        self.assertNotIn("TEST", {row.get("subject") for row in projection["questions"]})
        self.assertTrue(projection["questions"], "isolation must be checked against a non-empty Question Bank")

    def test_fixture_ids_are_absent_from_learner_search(self):
        fixture_ids = {row["id"] for row in self.doc["question_refs"]}
        documents, _manifest = build_learner_search_index.build_search_documents(REPO)
        search_ids = {row["id"] for row in documents}

        self.assertTrue(fixture_ids.isdisjoint(search_ids))

    def test_fixture_rows_carry_coordinates_only(self):
        allowed = {"id", "topic_label", "original_identifier"}
        forbidden = {
            "stem",
            "answer",
            "official_answer_text",
            "source_authority",
            "capture_method",
            "wording_custody",
            "text_verification_status",
            "workflow_status",
            "difficulty",
            "qrt",
            "primary_capability_ref",
            "secondary_capability_refs",
            "accepted",
            "acceptance",
        }

        for row in self.doc["question_refs"]:
            self.assertEqual(set(row), allowed, row)
            self.assertTrue(forbidden.isdisjoint(row), row)


if __name__ == "__main__":
    unittest.main()
