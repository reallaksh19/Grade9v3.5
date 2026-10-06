from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import build_learner_search_index, build_question_bank_web


REPO = Path(__file__).resolve().parents[1]
FIXTURE = REPO / "TEST/question-bank/fixtures/pr61-math-42.fixture.json"


class TestTestFixtureIsolation(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
        cls.fixture_ids = {row["id"] for row in cls.fixture["question_refs"]}

    def test_fixture_is_exactly_the_pre_placeholder_42_and_claims_no_source_authority(self):
        self.assertEqual(self.fixture["question_count"], 42)
        self.assertEqual(len(self.fixture_ids), 42)
        self.assertEqual(self.fixture["authority_status"], "UNVERIFIED_SANDBOX_FIXTURE")
        self.assertEqual(sum(self.fixture["topic_counts"].values()), 42)
        self.assertEqual(set(self.fixture["topic_counts"].values()), {6})
        self.assertEqual(
            self.fixture["excluded_provider_head"]["excluded_placeholder_records"], 168
        )

        raw = FIXTURE.read_text(encoding="utf-8")
        for forbidden in (
            "TEXT_VERIFIED_AGAINST_OFFICIAL",
            "READY_FOR_BLUEPRINT",
            "NCERT_OFFICIAL",
            "VERBATIM_EXTRACTION",
        ):
            self.assertNotIn(forbidden, raw)

    def test_fixture_ids_do_not_enter_canonical_question_bank(self):
        projection = build_question_bank_web.build(REPO)
        canonical_ids = {row["id"] for row in projection["questions"]}

        self.assertTrue(self.fixture_ids.isdisjoint(canonical_ids))
        self.assertNotIn("TEST", {row.get("subject") for row in projection["questions"]})

    def test_fixture_ids_do_not_enter_learner_search(self):
        documents, _manifest = build_learner_search_index.build_search_documents(REPO)
        search_ids = {row["id"] for row in documents}

        self.assertTrue(self.fixture_ids.isdisjoint(search_ids))


if __name__ == "__main__":
    unittest.main()
