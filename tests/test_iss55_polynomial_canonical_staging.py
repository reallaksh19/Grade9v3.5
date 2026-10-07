#!/usr/bin/env python3
import json
import unittest
from pathlib import Path

from Shared.tools import question_bank_platform
from Shared.library import intake

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Mathematics/library/polynomials.v1.json"
BANK = REPO / "TEST/question-bank/iss55-poly.json"
RECON = REPO / "TEST/candidates/iss55-poly.canonical-reconciliation.json"


class TestIss55PolynomialCanonicalStaging(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.recon = json.loads(RECON.read_text(encoding="utf-8"))

    def test_package_identity_is_canonical_candidate(self):
        self.assertEqual(self.package["package_id"], "LIB-MATH-POLYNOMIALS")
        self.assertEqual(self.package["subject"], "Mathematics")
        self.assertEqual(self.package["status"], "CANDIDATE")
        self.assertEqual(len(self.package["questions"]), 10)

    def test_verbatim_stems_and_reconciled_ids_are_preserved(self):
        source = {q["id"]: q for q in self.bank["questions"]}
        mapping = {q["source_id"]: q for q in self.recon["questions"]}
        staged = {q["id"]: q for q in self.package["questions"]}
        self.assertEqual(
            set(staged),
            {f"Q-MAT-POLY-ISS55-{n:02d}" for n in range(1, 11)},
        )
        for source_id, row in mapping.items():
            q = staged[row["canonical_id"]]
            self.assertEqual(q["stem"], source[source_id]["stem"])
            self.assertEqual(
                q["extensions"]["grade9v3:source_custody"]["text_sha256"],
                row["stem_sha256"],
            )
            self.assertEqual(q["origin_ref"], source_id)
            self.assertEqual(q["status"], "CANDIDATE")

    def test_question_bank_admission_is_explicitly_disabled(self):
        for q in self.package["questions"]:
            self.assertIs(
                q["extensions"]["grade9v3:question_bank"]["include"],
                False,
                q["id"],
            )

    def test_package_passes_library_intake(self):
        report = intake.check(self.package)
        self.assertEqual(
            [f"{row['point']}: {row['detail']}" for row in report["findings"]][:10],
            [],
        )
        self.assertTrue(report["admitted"])

    def test_non_admitted_candidate_does_not_influence_qb_titles(self):
        titles = question_bank_platform.load_subtopic_titles(REPO)
        for q in self.package["questions"]:
            self.assertNotIn(q["primary_capability_ref"], titles)

    def test_canonical_package_does_not_depend_on_test_assets(self):
        text = PACKAGE.read_text(encoding="utf-8")
        self.assertNotIn("TEST/library/figures/", text)
        for name in (
            "polynomial-sign-chart.svg",
            "card-cutout-area.svg",
            "polynomial-identity-difference.svg",
            "auxiliary-variable-domain.svg",
        ):
            self.assertTrue((REPO / "Mathematics/library/figures" / name).is_file())


if __name__ == "__main__":
    unittest.main()
