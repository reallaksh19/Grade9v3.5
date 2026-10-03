#!/usr/bin/env python3
"""Unit tests verifying Core 1A Cognitive Demand calibration, review templates, and golden fixture specimen."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

REPO = Path(__file__).resolve().parents[1]
VOCABULARY_PATH = REPO / "Shared/vocabularies/learner-question-metadata.v1.json"
FIXTURE_JSON = REPO / "tests/fixtures/golden_demand_calibration/golden-core1a-demand-specimen.json"
COMPILED_PUBLIC_HTML = REPO / "public/standalone/practice/golden-core1a-demand-specimen.html"
COMPILED_DOCS_HTML = REPO / "docs/standalone/practice/golden-core1a-demand-specimen.html"

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

CANONICAL_CONCEPT_DIFFICULTIES = {"EASY", "MEDIUM", "HARD"}


class TestGoldenDemandCore1A(unittest.TestCase):
    def test_01_golden_core1a_specimen_payload_integrity(self):
        """Ensure golden Core 1A JSON specimen contains valid multi-demand units with full scaffolding."""
        self.assertTrue(FIXTURE_JSON.exists(), f"Missing fixture JSON: {FIXTURE_JSON}")
        data = json.loads(FIXTURE_JSON.read_text(encoding="utf-8"))

        units = data.get("units", [])
        self.assertGreaterEqual(len(units), 3)

        observed_demands = set()
        observed_difficulties = set()
        observed_templates = set()

        for u in units:
            self.assertIn("unit_id", u)
            self.assertIn("unit_title", u)

            # Concept difficulty
            self.assertIn("concept_difficulty", u)
            self.assertIn(u["concept_difficulty"], CANONICAL_CONCEPT_DIFFICULTIES)
            observed_difficulties.add(u["concept_difficulty"])

            # Cognitive demand
            self.assertIn("cognitive_demand", u)
            self.assertIn(u["cognitive_demand"], CANONICAL_DEMAND_KEYS)
            observed_demands.add(u["cognitive_demand"])

            # Review template ref
            self.assertIn("review_template_ref", u)
            observed_templates.add(u["review_template_ref"])

            # Scaffolding
            scaffolding = u.get("demand_scaffolding")
            self.assertIsInstance(scaffolding, dict)
            for var in ("x", "y", "z", "w"):
                self.assertIn(var, scaffolding)
                self.assertTrue(bool(scaffolding[var].strip()))

            # Entry assumptions & Exit task
            self.assertIn("entry_assumptions", u)
            self.assertIsInstance(u["entry_assumptions"], list)
            self.assertGreaterEqual(len(u["entry_assumptions"]), 1)

            exit_task = u.get("exit_task")
            self.assertIsInstance(exit_task, dict)
            self.assertIn("prompt", exit_task)
            self.assertIn("answer", exit_task)
            self.assertIn("check", exit_task)

        # Multi-demand coverage check
        self.assertIn("MULTISTEP_REASONING", observed_demands)
        self.assertIn("CONCEPTUAL_EXPLANATION", observed_demands)
        self.assertIn("PROOF_DERIVATION", observed_demands)

        self.assertIn("CRT-PHY-CONSTRUCTION", observed_templates)
        self.assertIn("CRT-MAT-CONSTRUCTION", observed_templates)

    def test_02_compiled_core1a_html_structure_and_badges(self):
        """Ensure compiled HTML contains correct demand badges, scaffolding grids, and exit gates."""
        self.assertTrue(COMPILED_PUBLIC_HTML.exists(), f"Missing public HTML: {COMPILED_PUBLIC_HTML}")
        html = COMPILED_PUBLIC_HTML.read_text(encoding="utf-8")

        # Demand badge and icons check
        self.assertIn('data-g9-demand="MULTISTEP_REASONING"', html)
        self.assertTrue("⛓️ Model & multi-step chain" in html or "⛓️ Model &amp; multi-step chain" in html)

        self.assertIn('data-g9-demand="CONCEPTUAL_EXPLANATION"', html)
        self.assertIn("💡 Conceptual explanation", html)

        self.assertIn('data-g9-demand="PROOF_DERIVATION"', html)
        self.assertTrue("📐 Proof & formal derivation" in html or "📐 Proof &amp; formal derivation" in html)

        # Concept difficulty pills check
        self.assertIn('data-g9-concept-difficulty="HARD"', html)
        self.assertIn("Hard concept", html)
        self.assertIn('data-g9-concept-difficulty="EASY"', html)
        self.assertIn("Easy concept", html)
        self.assertIn('data-g9-concept-difficulty="MEDIUM"', html)
        self.assertIn("Medium concept", html)

        # Review rubrics check
        self.assertIn("CRT-PHY-CONSTRUCTION", html)
        self.assertIn("CRT-MAT-CONSTRUCTION", html)

        # Demand scaffolding component check
        self.assertIn('data-g9-component="DEMAND_SCAFFOLDING"', html)
        self.assertIn("Target Concept ($X$)", html)
        self.assertIn("Entry Foundation ($Y$)", html)
        self.assertIn("Inferential Leap ($Z$)", html)
        self.assertIn("Exit Verification ($W$)", html)

        # Core 1A constitutional components check
        self.assertIn('data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.4.0"', html)
        self.assertIn('data-g9-component="MODEL_CONTRACT"', html)
        self.assertIn('data-g9-component="CONSTRUCTION_STEPS"', html)
        self.assertIn('data-g9-component="STAGED_VISUAL"', html)
        self.assertIn('data-g9-component="TRAP_REPAIR"', html)
        self.assertIn('data-g9-component="QUICK_CHECK"', html)
        self.assertIn('data-g9-component="EXIT_RECALL"', html)
        self.assertIn('data-g9-component="PRACTICE_LINKS"', html)
        self.assertIn('data-requires-attempt', html)

    def test_03_public_docs_lockstep_parity(self):
        """Ensure public and docs compiled HTMLs are bit-for-bit identical."""
        self.assertTrue(COMPILED_DOCS_HTML.exists(), f"Missing docs HTML: {COMPILED_DOCS_HTML}")
        pub_bytes = COMPILED_PUBLIC_HTML.read_bytes()
        docs_bytes = COMPILED_DOCS_HTML.read_bytes()
        self.assertEqual(pub_bytes, docs_bytes, "Drift detected between public/ and docs/ compiled specimen!")


if __name__ == "__main__":
    unittest.main()
