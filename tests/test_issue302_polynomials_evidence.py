import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGER = ROOT / "docs" / "stress-tests" / "polynomials-agent1" / "source-ledger.json"
HTML = ROOT / "docs" / "stress-tests" / "polynomials-agent1" / "index.html"


class Issue302PolynomialsEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(LEDGER.read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")

    def test_exact_source_basis_is_pinned(self):
        source = self.data["source_basis"]
        repo = self.data["repository_basis"]
        self.assertEqual(source["acquisition_id"], "ACQ-1DD05CE5AA04B532EC68")
        self.assertEqual(source["bucket_id"], "MAT-09-POLYNOMIALS")
        self.assertEqual(source["registered_source"], "m2.pdf")
        self.assertEqual(
            source["source_sha256"],
            "1dd05ce5aa04b532ec68c4054f55af1677ecb210be00b8f3085d6f29215a230c",
        )
        self.assertEqual(source["page_count"], 49)
        self.assertEqual(source["in_scope_pdf_pages"], list(range(1, 12)))
        self.assertIsNone(source["page_map"])
        self.assertEqual(repo["source_pr"], 306)

    def test_source_text_is_available_and_ledger_populated(self):
        access = self.data["source_access"]
        ledger = self.data["ledger"]
        self.assertEqual(access["status"], "AVAILABLE")
        self.assertGreater(ledger["question_count"], 0)
        self.assertEqual(len(ledger["rows"]), ledger["question_count"])
        self.assertEqual(ledger["coverage_status"], "COMPLETE_PAGES_1_TO_11")

    def test_prior_art_is_explicitly_non_authoritative(self):
        prior = self.data["prior_art"]
        self.assertFalse(prior["source_authority"])
        self.assertEqual(
            prior["path"],
            "standalone/mathematics-polynomials-and-coordinates-suite.html",
        )
        self.assertIn("source stems", prior["forbidden_as_authority_for"])
        self.assertIn("source answers", prior["forbidden_as_authority_for"])

    def test_hardness_preserves_math_scan_and_length_invariants(self):
        taxonomy = self.data["hardness_taxonomy"]
        self.assertFalse(taxonomy["psychometric_claim"])
        self.assertIn("does not make", taxonomy["algebraic_length"]["invariant"])
        self.assertIn("never contributes", taxonomy["source_scan"]["invariant"])
        self.assertIn("S3 blocks", taxonomy["source_scan"]["invariant"])

    def test_explorer_and_clinic_selections_are_grounded(self):
        explorer = self.data["explorer_admission"]
        clinics = self.data["clinic_ranking"]
        witnesses = self.data["classification_witnesses"]
        self.assertIsNotNone(explorer["current_recommendation"])
        self.assertEqual(explorer["current_status"], "ADMITTED")
        self.assertTrue(3 <= len(clinics["current_candidates"]) <= 6)
        self.assertEqual(clinics["current_status"], "EVALUATED_AND_RANKED")
        self.assertIsNotNone(witnesses["easy"])
        self.assertIsNotNone(witnesses["medium"])
        self.assertIsNotNone(witnesses["hard"])

    def test_html_embeds_the_same_machine_truth(self):
        match = re.search(
            r'<script id="evidence-json" type="application/json">(.*?)</script>',
            self.html,
            flags=re.S,
        )
        self.assertIsNotNone(match)
        embedded = json.loads(match.group(1).replace("<\\/", "</"))
        self.assertEqual(embedded, self.data)

    def test_html_is_touch_readable_and_has_no_external_runtime_dependency(self):
        self.assertTrue("min-height: 48px" in self.html or "min-height:48px" in self.html)
        self.assertNotIn("cdn.jsdelivr.net", self.html)
        self.assertNotIn("https://", self.html)


if __name__ == "__main__":
    unittest.main()
