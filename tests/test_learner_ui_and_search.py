#!/usr/bin/env python3
"""Unit tests for Grade9V3.5 Learner UI, Search Convergence, and Audience Separation (UNIT-11 to UNIT-15)."""

import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
from Shared.tools.build_learner_ui import (
    generate_home,
    generate_subject_hub,
    generate_topic_workspace,
)
from Shared.tools.build_learner_search_index import build_search_documents


class TestLearnerUiAndSearch(unittest.TestCase):
    def setUp(self):
        with open(REPO / "public" / "data" / "resource-registry.v1.json", "r", encoding="utf-8") as f:
            self.registry = json.load(f)
        with open(REPO / "public" / "data" / "concept-bundles.v1.json", "r", encoding="utf-8") as f:
            self.bundles = json.load(f)

    def test_home_page_contains_all_subjects_and_no_owner_surfaces(self):
        home_html = generate_home(self.registry)
        self.assertIn("Physics", home_html)
        self.assertIn("Chemistry", home_html)
        self.assertIn("Mathematics", home_html)
        self.assertIn("Question Bank", home_html)

        # Audience boundary: Zero authoring or owner tools on Home
        self.assertNotIn("test/atlas", home_html)
        self.assertNotIn("test/rungs", home_html)
        self.assertNotIn("owner.test", home_html)

    def test_topic_workspace_concept_centred_and_anti_cheating(self):
        ws_html = generate_topic_workspace("phy.nlm", "Newton's Laws", "Physics", self.bundles)

        # Microtopic 1 has interactive
        self.assertIn("MIC-PHY-NLM-FRICTION", ws_html)
        self.assertIn("Try visually", ws_html)
        self.assertIn("core1a.html", ws_html)
        self.assertIn("Practice in Question Bank", ws_html)
        self.assertIn("topic=nlm", ws_html)

        # Anti-cheating verification: Remove explorer from bundles and regenerate
        bundles_no_exp = [
            dict(b, interactive=[]) if b.get("topic_ref") == "phy.nlm" else b
            for b in self.bundles
        ]
        ws_no_exp = generate_topic_workspace("phy.nlm", "Newton's Laws", "Physics", bundles_no_exp)
        self.assertNotIn("Try visually", ws_no_exp, "Try visually must disappear when explorer relation is absent")

    def test_learner_search_excludes_owner_and_lab(self):
        docs, stats = build_search_documents(REPO)
        doc_ids = {d["id"] for d in docs}

        # Learner resources must be indexed
        self.assertIn("RES-phy.nlm.friction.core1a", doc_ids)
        self.assertIn("RES-phy.nlm.friction.core2", doc_ids)
        self.assertIn("RES-phy.nlm.friction.threshold-explorer", doc_ids)
        self.assertIn("CON-MIC-PHY-NLM-FRICTION", doc_ids)

        # Owner/Lab surfaces must be strictly EXCLUDED
        self.assertNotIn("RES-owner.test.atlas", doc_ids)
        self.assertNotIn("RES-owner.test.rungs", doc_ids)

        # Search index must not contain any owner tool
        for d in docs:
            self.assertNotEqual(d["type"], "OWNER_TOOL")

    def test_search_type_breakdown_covers_all_dimensions(self):
        docs, stats = build_search_documents(REPO)
        by_type = stats["by_type"]
        self.assertIn("LEARN_RESOURCE", by_type)
        self.assertIn("PRACTICE_RESOURCE", by_type)
        self.assertIn("EXPLORE_RESOURCE", by_type)
        self.assertIn("CONCEPT", by_type)
        self.assertIn("QUESTION", by_type)
        self.assertIn("QUESTION_BANK_RESOURCE", by_type)

    def test_synthetic_fourth_subject_discovered_without_hardcoding(self):
        synthetic_registry = list(self.registry) + [{
            "id": "biology.home",
            "resource_kind": "STRUCTURED_PRODUCT",
            "learner_role": "LEARN",
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": "Biology",
                "topic_refs": [],
                "capability_refs": []
            },
            "artifact": {"entrypoint": "biology/index.html", "generated": False},
            "search": {"title": "Biology Subject Hub", "visibility": "LEARNER"}
        }]
        home_html = generate_home(synthetic_registry)
        self.assertIn("Biology", home_html, "Synthetic fourth subject must be discovered dynamically")


if __name__ == "__main__":
    unittest.main()
