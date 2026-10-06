from __future__ import annotations

import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]


EXPECTED_CORES = {"CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"}


class TestTestProductionCoreBinding(unittest.TestCase):
    def test_shared_package_schema_is_the_only_package_schema_for_test(self):
        schema_path = REPO / "Shared/library/package.schema.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertIn("TEST", schema["properties"]["subject"]["enum"])
        self.assertEqual(
            list((REPO / "TEST").rglob("package.schema.json")),
            [],
            "TEST must consume the production package schema rather than fork it",
        )

    def test_test_declares_exactly_the_six_production_core_roles(self):
        contract = json.loads(
            (REPO / "TEST/adapter/CoreContracts.json").read_text(encoding="utf-8")
        )

        self.assertEqual(contract["subject"], "TEST")
        self.assertEqual(set(contract["learner_products"]), EXPECTED_CORES)
        for core in EXPECTED_CORES:
            self.assertEqual(contract["learner_products"][core]["production"], "COMPILED")

    def test_machine_checks_cannot_grant_test_release_authority(self):
        contract = json.loads(
            (REPO / "TEST/adapter/CoreContracts.json").read_text(encoding="utf-8")
        )

        self.assertEqual(
            contract["release_authority"],
            "NOT_GRANTED_BY_ANY_MACHINE_CHECK",
        )
        self.assertEqual(contract["validator_catalogue"], [])


if __name__ == "__main__":
    unittest.main()
