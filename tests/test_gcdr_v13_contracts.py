#!/usr/bin/env python3
"""Regression tests for GCDR v1.3 explorer/suite companion contracts."""
from __future__ import annotations

import json
import unittest
from pathlib import Path

import jsonschema

from Shared.tools import gcdr_suite_guard

REPO = Path(__file__).resolve().parents[1]


class GcdrV13ContractsTest(unittest.TestCase):
    def test_master_suite_guard_passes(self):
        self.assertEqual(gcdr_suite_guard.findings(REPO), [])

    def test_companion_schemas_are_draft_2020_12_and_versioned(self):
        expected = {
            "gcdr_diagnostic_item.schema.json": "urn:grade9v3:gcdr-diagnostic-item:1.0.0",
            "gcdr_helper_contract.schema.json": "urn:grade9v3:gcdr-helper-contract:1.0.0",
            "gcdr_suite_contract.schema.json": "urn:grade9v3:gcdr-suite-contract:1.0.0",
        }
        for name, schema_id in expected.items():
            with self.subTest(schema=name):
                schema = json.loads((REPO / "Shared/library" / name).read_text(encoding="utf-8"))
                self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
                self.assertEqual(schema["$id"], schema_id)
                jsonschema.Draft202012Validator.check_schema(schema)

    def test_explorer_contract_is_v13(self):
        schema = json.loads(
            (REPO / "Shared/library/explorer_design_contract.schema.json").read_text(encoding="utf-8")
        )
        self.assertEqual(schema["properties"]["schema_version"]["const"], "1.3.0")
        for key in (
            "scope_contract",
            "representation_invariants",
            "geometry_truth_contract",
            "delivery_profile",
        ):
            self.assertIn(key, schema["required"])

    def test_generic_filler_final_answers_are_release_blocked(self):
        for value in ("apply formula", "Evaluate", "use the equation", "Solve"):
            with self.subTest(value=value):
                self.assertTrue(gcdr_suite_guard.is_generic_final_answer(value))
        for value in ("44", "13 m (Option C)", "π/3 (Option B)"):
            with self.subTest(value=value):
                self.assertFalse(gcdr_suite_guard.is_generic_final_answer(value))

    def test_suite_scope_and_delivery_claims_are_explicit(self):
        motion = json.loads((REPO / "docs/gcdr-suites/motion-1d.json").read_text(encoding="utf-8"))
        vector = json.loads((REPO / "docs/gcdr-suites/vector-algebra-3d.json").read_text(encoding="utf-8"))
        self.assertEqual(motion["scope_contract"]["canonical_binding_status"], "PARTIAL")
        self.assertEqual(vector["scope_contract"]["canonical_binding_status"], "UNBOUND_EXTENSION")
        self.assertEqual(motion["external_corpus"]["coverage_claim"], "CURATED_SLICE_AUDITED")
        self.assertEqual(vector["external_corpus"]["coverage_claim"], "CURATED_SLICE_AUDITED")
        self.assertEqual(
            {row["profile"] for row in motion["delivery_artifacts"]},
            {"REPO_BUNDLE", "SINGLE_FILE_ONLINE"},
        )
        self.assertEqual(
            {row["profile"] for row in vector["delivery_artifacts"]},
            {"REPO_BUNDLE", "SINGLE_FILE_ONLINE"},
        )


if __name__ == "__main__":
    unittest.main()
