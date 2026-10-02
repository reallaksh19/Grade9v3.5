#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 resource schema (grade9v3-resource/v1)."""

import json
import unittest
from pathlib import Path

try:
    import jsonschema
except ImportError:
    jsonschema = None

REPO = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO / "Shared" / "resources" / "resource.schema.json"


class TestResourceSchema(unittest.TestCase):
    def setUp(self):
        with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
            self.schema = json.load(f)

        self.valid_record = {
            "schema": "grade9v3-resource/v1",
            "id": "phy.nlm.friction.core1a",
            "resource_kind": "STRUCTURED_PRODUCT",
            "learner_role": "LEARN",
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": "Physics",
                "topic_refs": ["phy.nlm"],
                "capability_refs": ["MIC-PHY-NLM-FRICTION"]
            },
            "artifact": {
                "entrypoint": "standalone/practice/friction/core1a.html",
                "generated": True
            },
            "platform_capabilities": ["staged-representation", "worked-anchor"],
            "search": {
                "title": "Friction — Learn",
                "aliases": ["friction", "limiting friction"],
                "visibility": "LEARNER"
            },
            "source": {
                "authority_ref": "products/physics/phy-nlm-friction.manifest.json",
                "generator_ref": "Shared/tools/render_core.py"
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        }

    def validate(self, record):
        if jsonschema:
            jsonschema.validate(instance=record, schema=self.schema)
        else:
            # Fallback manual validation
            for req in self.schema["required"]:
                self.assertIn(req, record)

    def test_valid_friction_core1a(self):
        self.validate(self.valid_record)

    def test_valid_opaque_explorer(self):
        record = dict(self.valid_record)
        record["id"] = "phy.nlm.friction.threshold-explorer"
        record["resource_kind"] = "OPAQUE_APP"
        record["learner_role"] = "EXPLORE"
        record["presentation"] = "COMPANION"
        record["artifact"] = {
            "entrypoint": "physics/nlm/explorers/friction-threshold/index.html",
            "generated": False
        }
        self.validate(record)

    def test_missing_audience_fails(self):
        if not jsonschema:
            self.skipTest("jsonschema not installed")
        record = dict(self.valid_record)
        del record["audience"]
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=record, schema=self.schema)

    def test_invalid_audience_enum_fails(self):
        if not jsonschema:
            self.skipTest("jsonschema not installed")
        record = dict(self.valid_record)
        record["audience"] = "STUDENT"  # Invalid enum
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=record, schema=self.schema)

    def test_invalid_resource_kind_fails(self):
        if not jsonschema:
            self.skipTest("jsonschema not installed")
        record = dict(self.valid_record)
        record["resource_kind"] = "WEBPAGE"  # Invalid enum
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=record, schema=self.schema)

    def test_invalid_id_pattern_fails(self):
        if not jsonschema:
            self.skipTest("jsonschema not installed")
        record = dict(self.valid_record)
        record["id"] = "UPPERCASE_NOT_ALLOWED"
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=record, schema=self.schema)

    def test_additional_properties_forbidden(self):
        if not jsonschema:
            self.skipTest("jsonschema not installed")
        record = dict(self.valid_record)
        record["arbitrary_hack"] = 123
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance=record, schema=self.schema)


if __name__ == "__main__":
    unittest.main()
