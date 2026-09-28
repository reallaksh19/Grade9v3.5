import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

P1_JSON = ROOT / "evidence" / "stress-tests" / "motion-in-a-plane" / "source-ledger.json"
P2_JSON = ROOT / "evidence" / "stress-tests" / "laws-of-motion" / "source-ledger.json"

P1_HTML = ROOT / "evidence" / "stress-tests" / "motion-in-a-plane" / "index.html"
P2_HTML = ROOT / "evidence" / "stress-tests" / "laws-of-motion" / "index.html"

P1_MD = ROOT / "evidence" / "stress-tests" / "scanned-assessment-p1-motion-in-a-plane-ledger.md"
P2_MD = ROOT / "evidence" / "stress-tests" / "scanned-assessment-p2-laws-of-motion-ledger.md"


class PhysicsScannedEvidenceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.p1 = json.loads(P1_JSON.read_text(encoding="utf-8"))
        cls.p2 = json.loads(P2_JSON.read_text(encoding="utf-8"))

    def test_p1_pins_exact_custody_and_sha256(self):
        sha = "db84892f0de76a6a48a867f89e9a8e15cd45fb2ba5ea5f846a029cc9af93f99b"
        acq = "ACQ-DB84892F0DE76A6A48A8"
        src = self.p1.get("source_basis", {})
        self.assertEqual(src["acquisition_id"], acq)
        self.assertEqual(src["source_sha256"], sha)
        self.assertEqual(src["registered_source"], "p1.pdf")
        self.assertEqual(src["in_scope_pdf_pages"], list(range(1, 51)))

    def test_p2_pins_exact_custody_and_sha256(self):
        sha = "4c6c8fe3b52dacc9c01c7e7ad428975a79b24e36c64ae0c9d95eedb9d6314a84"
        acq = "ACQ-4C6C8FE3B52DACC9C01C"
        src = self.p2.get("source_basis", {})
        self.assertEqual(src["acquisition_id"], acq)
        self.assertEqual(src["source_sha256"], sha)
        self.assertEqual(src["registered_source"], "p2.pdf")
        self.assertEqual(src["in_scope_pdf_pages"], list(range(1, 51)))

    def test_both_modules_have_populated_verified_ledgers(self):
        for mod, name in [(self.p1, "p1"), (self.p2, "p2")]:
            rows = mod.get("rows", [])
            self.assertGreaterEqual(len(rows), 20, f"{name} rows less than 20")
            self.assertEqual(mod["status"], "EVIDENCE_VERIFIED_COMPLETE")
            for row in rows:
                self.assertTrue(row["id"].startswith("Q-PHY-11-"))
                self.assertIsNotNone(row["stem"])
                self.assertIsNotNone(row["source_answer"])
                self.assertEqual(row["fidelity_status"], "VERIFIED")
                self.assertIn("overall", row["hardness"])

    def test_both_modules_have_concept_explorers_admitted(self):
        self.assertTrue(self.p1["explorer_recommendation"]["admission_test_passed"])
        self.assertTrue(self.p2["explorer_recommendation"]["admission_test_passed"])
        self.assertIn("Trajectory", self.p1["explorer_recommendation"]["name"])
        self.assertIn("Friction", self.p2["explorer_recommendation"]["name"])

    def test_both_modules_have_ranked_question_clinics(self):
        self.assertEqual(len(self.p1["clinic_candidates"]), 4)
        self.assertEqual(len(self.p2["clinic_candidates"]), 4)

    def test_html_projections_exist_and_touch_compliant(self):
        for html_path, name in [(P1_HTML, "P1 HTML"), (P2_HTML, "P2 HTML")]:
            self.assertTrue(html_path.exists(), f"{name} missing")
            content = html_path.read_text(encoding="utf-8")
            self.assertTrue("min-height: 48px" in content or "min-height:48px" in content, f"{name} lacks 48px touch target")
            self.assertNotIn("cdn.jsdelivr.net", content, f"{name} contains external CDN")

    def test_markdown_ledgers_exist_and_pin_custody(self):
        for md_path, name, sha in [
            (P1_MD, "P1 MD", "db84892f0de76a6a48a867f89e9a8e15cd45fb2ba5ea5f846a029cc9af93f99b"),
            (P2_MD, "P2 MD", "4c6c8fe3b52dacc9c01c7e7ad428975a79b24e36c64ae0c9d95eedb9d6314a84"),
        ]:
            self.assertTrue(md_path.exists(), f"{name} missing")
            content = md_path.read_text(encoding="utf-8")
            self.assertIn(sha, content)


if __name__ == "__main__":
    unittest.main()
