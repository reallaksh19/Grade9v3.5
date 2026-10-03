#!/usr/bin/env python3
"""Unit tests verifying Core 2 Cognitive Demand taxonomy, review templates, and golden fixture calibration."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = REPO / "Shared/vocabularies/learner-question-metadata.v1.json"
FIXTURE_JSON = REPO / "tests/fixtures/golden_demand_calibration/golden-core2-demand-specimen.json"
COMPILED_PUBLIC_HTML = REPO / "public/standalone/practice/golden-core2-demand-specimen.html"
COMPILED_DOCS_HTML = REPO / "docs/standalone/practice/golden-core2-demand-specimen.html"

CANONICAL_DEMAND_KEYS = {
    "MEMORY_RECALL",
    "CONCEPTUAL_EXPLANATION",
    "QUANTITATIVE_APPLICATION",
    "MULTISTEP_REASONING",
    "REPRESENTATION_TRANSLATION",
    "EXPERIMENTAL_REASONING",
    "ESTIMATION_LIMITS",
    "PROOF_DERIVATION",
    "CLASSIFICATION_PATTERN",
}


class TestGoldenDemandCore2(unittest.TestCase):
    def test_01_vocabulary_defines_cognitive_demand_taxonomy(self):
        """Ensure learner-question-metadata.v1.json formally includes the 9 cognitive demands."""
        self.assertTrue(VOCABULARY_PATH.exists(), f"Missing vocabulary file: {VOCABULARY_PATH}")
        vocab = json.loads(VOCABULARY_PATH.read_text(encoding="utf-8"))

        self.assertIn("cognitive_demand", vocab)
        demands = vocab["cognitive_demand"]
        self.assertEqual(set(demands.keys()), CANONICAL_DEMAND_KEYS)

        # Check field labels
        self.assertIn("field_labels", vocab)
        self.assertIn("cognitive-demand", vocab["field_labels"])
        self.assertEqual(vocab["field_labels"]["cognitive-demand"], "Cognitive demand")
        self.assertIn("review-template", vocab["field_labels"])

    def test_02_golden_specimen_payload_integrity(self):
        """Ensure golden JSON specimen contains multi-demand items with XYZW scaffolding."""
        self.assertTrue(FIXTURE_JSON.exists(), f"Missing fixture JSON: {FIXTURE_JSON}")
        data = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))

        questions = data.get("questions", [])
        self.assertGreaterEqual(len(questions), 3)

        observed_demands = set()
        observed_templates = set()

        for q in questions:
            self.assertIn("id", q)
            self.assertIn("cognitive_demand", q)
            self.assertIn(q["cognitive_demand"], CANONICAL_DEMAND_KEYS)
            observed_demands.add(q["cognitive_demand"])

            self.assertIn("review_template_ref", q)
            observed_templates.add(q["review_template_ref"])

            scaffolding = q.get("demand_scaffolding")
            self.assertIsInstance(scaffolding, dict)
            for var in ("x", "y", "z", "w"):
                self.assertIn(var, scaffolding)
                self.assertTrue(bool(scaffolding[var].strip()))

        # Check that calibration specimen exercises multiple demands & review templates
        self.assertIn("MULTISTEP_REASONING", observed_demands)
        self.assertIn("MEMORY_RECALL", observed_demands)
        self.assertIn("PROOF_DERIVATION", observed_demands)

        self.assertIn("QRT-PHY-MULTISTEP", observed_templates)
        self.assertIn("QRT-PHY-MEMORY", observed_templates)
        self.assertIn("QRT-MAT-PROOF", observed_templates)

    def test_03_compiled_specimen_html_structure_and_badges(self):
        """Ensure compiled HTML has correct demand badges, review rubrics, and scaffolding grids."""
        self.assertTrue(COMPILED_PUBLIC_HTML.exists(), f"Missing public HTML: {COMPILED_PUBLIC_HTML}")
        html = COMPILED_PUBLIC_HTML.read_text(encoding="utf-8")

        # Demand badge and icons check
        self.assertIn('data-g9-demand="MULTISTEP_REASONING"', html)
        self.assertTrue("⛓️ Model & multi-step chain" in html or "⛓️ Model &amp; multi-step chain" in html)

        self.assertIn('data-g9-demand="MEMORY_RECALL"', html)
        self.assertIn("🧠 Factual recall", html)

        self.assertIn('data-g9-demand="PROOF_DERIVATION"', html)
        self.assertTrue("📐 Proof & formal derivation" in html or "📐 Proof &amp; formal derivation" in html)

        # Review template pills check
        self.assertIn("QRT-PHY-MULTISTEP", html)
        self.assertIn("QRT-PHY-MEMORY", html)
        self.assertIn("QRT-MAT-PROOF", html)

        # Demand scaffolding component check
        self.assertIn('data-g9-component="DEMAND_SCAFFOLDING"', html)
        self.assertIn("Target Concept ($X$)", html)
        self.assertIn("Related Idea ($Y$)", html)
        self.assertIn("Crux Retrieval ($Z$)", html)
        self.assertIn("Student Step ($W$)", html)

        # Constitutional Core 2 features check
        self.assertIn('data-blueprint-ref="BP-CORE2-SOURCE-QUESTION@1.5.0"', html)
        self.assertIn('data-g9-component="HINT_LADDER"', html)
        self.assertIn('data-g9-component="ATTEMPT"', html)
        self.assertIn('data-requires-attempt', html)

    def test_04_public_docs_lockstep_parity(self):
        """Ensure public and docs compiled HTMLs are bit-for-bit identical."""
        self.assertTrue(COMPILED_DOCS_HTML.exists(), f"Missing docs HTML: {COMPILED_DOCS_HTML}")
        pub_bytes = COMPILED_PUBLIC_HTML.read_bytes()
        docs_bytes = COMPILED_DOCS_HTML.read_bytes()
        self.assertEqual(pub_bytes, docs_bytes, "Drift detected between public/ and docs/ compiled specimen!")


if __name__ == "__main__":
    unittest.main()
