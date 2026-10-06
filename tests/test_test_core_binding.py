from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import build_web_data, check_subjects


REPO = Path(__file__).resolve().parents[1]
EXPECTED_CORES = {"CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"}


class TestTestProductionCoreBinding(unittest.TestCase):
    def test_shared_package_schema_is_the_package_authority_for_test(self):
        schema_path = REPO / "Shared/library/package.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertIn("TEST", schema["properties"]["subject"]["enum"])
        self.assertFalse(
            list((REPO / "TEST").rglob("package.schema.json")),
            "TEST must not fork the production package schema",
        )

    def test_test_contract_declares_the_six_production_learner_products(self):
        contract = json.loads(
            (REPO / "TEST/adapter/CoreContracts.json").read_text(encoding="utf-8")
        )

        self.assertEqual(contract["subject"], "TEST")
        self.assertEqual(set(contract["learner_products"]), EXPECTED_CORES)
        self.assertEqual(
            contract["release_authority"],
            "NOT_GRANTED_BY_ANY_MACHINE_CHECK",
        )
        self.assertEqual(contract["validator_catalogue"], [])

    def test_subject_discovery_treats_test_like_every_other_contract_subject(self):
        checked_subjects = {path.name for path in check_subjects.subjects(REPO)}

        self.assertIn("TEST", checked_subjects)
        self.assertIn("TEST", build_web_data.subjects())

    def test_test_quality_vocabulary_is_subject_data_not_a_parallel_quality_contract(self):
        vocabulary = json.loads(
            (REPO / "TEST/adapter/QualityVocabulary.json").read_text(encoding="utf-8")
        )
        contract = json.loads(
            (REPO / "Shared/quality/learner-quality.v1.json").read_text(encoding="utf-8")
        )

        self.assertEqual(vocabulary["subject"], "TEST")
        self.assertEqual(vocabulary["schema"], "quality-vocabulary/v1")
        self.assertIsInstance(contract, dict)
        self.assertFalse(
            list((REPO / "TEST").rglob("learner-quality*.json")),
            "TEST may provide vocabulary, not fork the production learner-quality contract",
        )


if __name__ == "__main__":
    unittest.main()
