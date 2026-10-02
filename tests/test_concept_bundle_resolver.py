#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 Concept Bundle Resolver & Friction Proving Slice."""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.resolve_concept_bundle import (
    load_bundle_schema,
    resolve_bundle,
    resolve_all_bundles,
    validate_relationship_integrity,
)

try:
    import jsonschema
except ImportError:
    jsonschema = None


class TestConceptBundleResolver(unittest.TestCase):
    def setUp(self):
        self.schema = load_bundle_schema()
        registry_path = REPO / "public" / "data" / "resource-registry.v1.json"
        with open(registry_path, "r", encoding="utf-8") as f:
            self.registry = json.load(f)

    def test_friction_bundle_resolves_all_four_roles(self):
        bundle = resolve_bundle("MIC-PHY-NLM-FRICTION", self.registry)
        if jsonschema:
            jsonschema.validate(instance=bundle, schema=self.schema)

        # 1. Learn
        self.assertEqual(len(bundle["learn"]), 1)
        self.assertEqual(bundle["learn"][0]["resource_ref"], "phy.nlm.friction.core1a")
        self.assertIn("core1a.html", bundle["learn"][0]["entrypoint"])

        # 2. Practice
        self.assertEqual(len(bundle["practice"]), 1)
        self.assertEqual(bundle["practice"][0]["resource_ref"], "phy.nlm.friction.core2")
        self.assertIn("core2.html", bundle["practice"][0]["entrypoint"])

        # 3. Interactive
        self.assertEqual(len(bundle["interactive"]), 1)
        self.assertEqual(bundle["interactive"][0]["resource_ref"], "phy.nlm.friction.threshold-explorer")
        self.assertIn("friction-threshold", bundle["interactive"][0]["entrypoint"])

        # 4. Question Bank
        self.assertEqual(bundle["question_bank"]["filter"]["capability_ref"], "MIC-PHY-NLM-FRICTION")
        self.assertIn("capability=MIC-PHY-NLM-FRICTION", bundle["question_bank"]["url"])

    def test_anti_cheating_removing_explorer_relationship_removes_interactive_action(self):
        """Hard Anti-Cheating Invariant:
        Removing the explorer from registry truth MUST remove the interactive action
        from the concept bundle without editing any HTML template.
        """
        # Filter out the friction explorer from registry truth
        modified_registry = [r for r in self.registry if r["id"] != "phy.nlm.friction.threshold-explorer"]

        bundle = resolve_bundle("MIC-PHY-NLM-FRICTION", modified_registry)

        # Interactive list must now be strictly empty
        self.assertEqual(bundle["interactive"], [], "Interactive action must cease when relation is removed")

        # Learn, practice, and QB remain intact
        self.assertEqual(len(bundle["learn"]), 1)
        self.assertEqual(len(bundle["practice"]), 1)
        self.assertIsNotNone(bundle["question_bank"])

    def test_learner_app_without_learning_ref_fails_integrity(self):
        bad_registry = list(self.registry) + [{
            "id": "unclassified.app",
            "resource_kind": "OPAQUE_APP",
            "learner_role": "EXPLORE",
            "audience": "LEARNER",
            "presentation": "COMPANION",
            "classification": {
                "subject_ref": "Physics",
                "topic_refs": ["phy.nlm"],
                "capability_refs": []  # Empty!
            },
            "artifact": {"entrypoint": "test.html"},
            "search": {"title": "Test", "visibility": "LEARNER"}
        }]
        diags = validate_relationship_integrity(bad_registry)
        self.assertTrue(any("LEARNER_APP_WITHOUT_LEARNING_REF" in d for d in diags))


if __name__ == "__main__":
    unittest.main()
