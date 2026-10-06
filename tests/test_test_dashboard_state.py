from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import build_test_site


EXPECTED_CORES = {"CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"}


class TestTestDashboardState(unittest.TestCase):
    def test_dashboard_state_projects_contract_fixture_and_safety_without_question_content(self):
        state = build_test_site.dashboard_state()

        self.assertEqual(state["core_contract"]["subject"], "TEST")
        self.assertEqual(
            {row["core"] for row in state["core_contract"]["roles"]},
            EXPECTED_CORES,
        )
        self.assertEqual(
            {row["production"] for row in state["core_contract"]["roles"]},
            {"COMPILED"},
        )
        self.assertEqual(
            state["core_contract"]["package_schema_path"],
            "Shared/library/package.schema.json",
        )
        self.assertEqual(
            state["core_contract"]["release_authority"],
            "NOT_GRANTED_BY_ANY_MACHINE_CHECK",
        )
        self.assertEqual(state["core_contract"]["validator_catalogue"], [])

        self.assertEqual(state["quality_vocabulary"]["schema"], "quality-vocabulary/v1")
        self.assertEqual(
            state["quality_vocabulary"]["shared_quality_contract_path"],
            "Shared/quality/learner-quality.v1.json",
        )

        self.assertEqual(state["fixture"]["question_count"], 42)
        self.assertEqual(len(state["fixture"]["topic_counts"]), 7)
        self.assertEqual(set(state["fixture"]["topic_counts"].values()), {6})
        self.assertEqual(
            state["fixture"]["authority_status"],
            "UNVERIFIED_SANDBOX_FIXTURE",
        )
        self.assertEqual(
            state["fixture"]["excluded_provider_head"]["excluded_placeholder_records"],
            168,
        )
        self.assertEqual(state["safety"]["fixture_scope"], "TEST_ONLY_NOT_CANONICAL")

        serialized = json.dumps(state)
        for forbidden in (
            '"question_refs"',
            '"stem"',
            '"answer"',
            '"official_answer_text"',
            '"text_verification_status"',
            '"workflow_status"',
            '"difficulty"',
            '"qrt"',
        ):
            self.assertNotIn(forbidden, serialized)

    def test_wrong_subject_core_contract_fails_loudly(self):
        contract = json.loads(build_test_site.CORE_CONTRACT.read_text(encoding="utf-8"))
        contract["subject"] = "Mathematics"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "CoreContracts.json"
            path.write_text(json.dumps(contract), encoding="utf-8")
            with mock.patch.object(build_test_site, "CORE_CONTRACT", path):
                with self.assertRaisesRegex(ValueError, "must declare subject TEST"):
                    build_test_site.dashboard_state()

    def test_invalid_fixture_denominator_fails_loudly(self):
        fixture = json.loads(build_test_site.FIXTURE_MANIFEST.read_text(encoding="utf-8"))
        fixture["question_count"] = 41
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fixture.json"
            path.write_text(json.dumps(fixture), encoding="utf-8")
            with mock.patch.object(build_test_site, "FIXTURE_MANIFEST", path):
                with self.assertRaisesRegex(ValueError, "exactly 42 coordinates"):
                    build_test_site.dashboard_state()

    def test_missing_fixture_is_not_silently_skipped(self):
        with tempfile.TemporaryDirectory() as tmp:
            missing = Path(tmp) / "missing.fixture.json"
            with mock.patch.object(build_test_site, "FIXTURE_MANIFEST", missing):
                with self.assertRaises(FileNotFoundError):
                    build_test_site.dashboard_state()

    def test_wrong_quality_vocabulary_schema_fails_loudly(self):
        vocabulary = json.loads(build_test_site.QUALITY_VOCABULARY.read_text(encoding="utf-8"))
        vocabulary["schema"] = "quality-vocabulary/v0"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "QualityVocabulary.json"
            path.write_text(json.dumps(vocabulary), encoding="utf-8")
            with mock.patch.object(build_test_site, "QUALITY_VOCABULARY", path):
                with self.assertRaisesRegex(ValueError, "must use quality-vocabulary/v1"):
                    build_test_site.dashboard_state()


if __name__ == "__main__":
    unittest.main()
