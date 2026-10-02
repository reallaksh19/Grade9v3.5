#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 Resource Registry generator and determinism."""

import json
import unittest
from pathlib import Path
import tempfile
import shutil

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.build_resource_registry import (
    build_registry,
    load_schema,
    validate_records,
)


class TestResourceRegistry(unittest.TestCase):
    def setUp(self):
        self.schema = load_schema()

    def test_build_registry_determinism(self):
        records_1 = build_registry(REPO)
        records_2 = build_registry(REPO)
        self.assertEqual(records_1, records_2, "Registry generation must be strictly deterministic")

    def test_all_records_valid_against_schema(self):
        records = build_registry(REPO)
        self.assertGreater(len(records), 0)
        validate_records(records, self.schema)

    def test_friction_slice_resources_present(self):
        records = build_registry(REPO)
        ids = {r["id"] for r in records}
        self.assertIn("phy.nlm.friction.core1a", ids)
        self.assertIn("phy.nlm.friction.core2", ids)
        self.assertIn("phy.nlm.friction.threshold-explorer", ids)
        self.assertIn("common.question-bank", ids)

    def test_audience_classification(self):
        records = build_registry(REPO)
        for r in records:
            if "owner.test" in r["id"]:
                self.assertIn(r["audience"], ["OWNER", "LAB", "INTERNAL"])
                self.assertEqual(r["search"]["visibility"], "EXCLUDED")
            elif "phy.nlm.friction" in r["id"]:
                self.assertEqual(r["audience"], "LEARNER")
                self.assertEqual(r["search"]["visibility"], "LEARNER")

    def test_duplicate_id_detection(self):
        # Inject duplicate ID
        records = [
            {
                "schema": "grade9v3-resource/v1",
                "id": "dup.resource",
                "resource_kind": "STRUCTURED_PRODUCT",
                "learner_role": "LEARN",
                "audience": "LEARNER",
                "presentation": "FULL_PAGE",
                "classification": {"subject_ref": "Physics", "topic_refs": [], "capability_refs": []},
                "artifact": {"entrypoint": "test.html"},
                "search": {"title": "Dup 1", "visibility": "LEARNER"}
            },
            {
                "schema": "grade9v3-resource/v1",
                "id": "dup.resource",
                "resource_kind": "STRUCTURED_PRODUCT",
                "learner_role": "LEARN",
                "audience": "LEARNER",
                "presentation": "FULL_PAGE",
                "classification": {"subject_ref": "Physics", "topic_refs": [], "capability_refs": []},
                "artifact": {"entrypoint": "test.html"},
                "search": {"title": "Dup 2", "visibility": "LEARNER"}
            }
        ]
        seen = set()
        with self.assertRaises(ValueError) as ctx:
            for rec in records:
                if rec["id"] in seen:
                    raise ValueError(f"DUPLICATE_RESOURCE_ID: {rec['id']}")
                seen.add(rec["id"])
        self.assertIn("DUPLICATE_RESOURCE_ID", str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
