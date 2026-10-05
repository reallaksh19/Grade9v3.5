"""Executable validation for the controlled ISS52 polynomial benchmark candidate.

This is a benchmark harness, not publication authority. It exercises the same repository
schema/owner-bank/selection/renderer code used by learner products while keeping the
candidate inputs under evidence/ until independent review.
"""
from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools import owner_bank, render_core

REPO = Path(__file__).resolve().parents[1]
ROOT = REPO / "evidence" / "benchmark" / "ISS52"
BANK = ROOT / "inputs" / "owner.bank.json"
PACKAGE = ROOT / "inputs" / "package.v1.json"
MANIFEST = ROOT / "inputs" / "product.manifest.json"
SCHEMA = REPO / "Shared" / "library" / "package.schema.json"


class ISS52PolynomialBenchmark(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))

    def test_owner_bank_is_strictly_complete_and_verbatim(self):
        self.assertEqual(owner_bank.check(self.bank, str(BANK), complete=True), [])
        self.assertEqual(
            [q["original_identifier"] for q in self.bank["questions"]],
            [f"Q{i}" for i in range(1, 11)],
        )
        for question in self.bank["questions"]:
            custody = question["extensions"]["grade9v3:source_custody"]
            self.assertEqual(custody["authority_class"], "OWNER_SUPPLIED_RAW_INPUT")
            self.assertEqual(custody["wording_custody"], "VERBATIM")
            self.assertNotIn("exam", custody)
            self.assertNotIn("year", custody)
            self.assertNotIn("paper", custody)

    def test_package_matches_canonical_schema(self):
        schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
        errors = sorted(
            Draft202012Validator(schema).iter_errors(self.package),
            key=lambda e: tuple(str(x) for x in e.absolute_path),
        )
        self.assertEqual(
            errors,
            [],
            "\n".join(
                f"{'/'.join(str(x) for x in e.absolute_path) or '<root>'}: {e.message}"
                for e in errors[:20]
            ),
        )

    def test_manifest_is_bounded_to_requested_roles_and_order(self):
        self.assertEqual(self.manifest["output_roles"], ["CORE1A", "CORE2"])
        self.assertEqual(
            self.manifest["selection"]["core2"],
            [f"ISS52-Q{i}" for i in range(1, 11)],
        )
        self.assertEqual(self.manifest["selection"]["core2a"], [])
        self.assertEqual(self.manifest["selection"]["core2b"], [])

    def test_reference_depth_render_has_no_governed_gaps(self):
        pages, gaps, digest, advisories, waived = render_core.build_report(
            MANIFEST, mode="PAGES", held_to="REFERENCE"
        )
        self.assertEqual(gaps, [], json.dumps(gaps, indent=2))
        self.assertRegex(digest, r"^[0-9a-f]{16}$")
        self.assertEqual(set(pages), {"core1a.html", "core2.html", "index.html"})
        self.assertTrue(waived)
        self.assertIsInstance(advisories, list)

        core2 = pages["core2.html"]
        actual = re.findall(
            r'<article\b[^>]*data-g9-unit="([^"]+)"[^>]*data-g9-kind="QUESTION"',
            core2,
        )
        self.assertEqual(actual, [f"ISS52-Q{i}" for i in range(1, 11)])
        self.assertGreaterEqual(core2.count("data-requires-attempt"), 10)
        self.assertIn('data-g9-unit="ISS52-Q4"', core2)
        self.assertIn('href="core1a.html#CU-MATH-ISS52-PARAMETER-1"', core2)

        core1a = pages["core1a.html"]
        self.assertIn('data-g9-cu="CU-MATH-ISS52-PARAMETER-1"', core1a)
        self.assertIn('data-g9-representation="REP-ISS52-PARAM-EVENT-MAP"', core1a)
        for stage in (
            "VIS-ISS52-PARAM-0",
            "VIS-ISS52-PARAM-1",
            "VIS-ISS52-PARAM-2",
            "VIS-ISS52-PARAM-3",
        ):
            self.assertIn(stage, core1a)

    def test_q4_is_unique_toughest_target_and_q10_special_degree_is_correct(self):
        ctx = render_core.context(MANIFEST)
        toughest = ctx.toughest()
        self.assertEqual(toughest["question_ref"], "ISS52-Q4")
        self.assertEqual(toughest["microtopic_ref"], "MIC-MATH-ISS52-PARAMETER")
        q10 = next(q for q in self.bank["questions"] if q["id"] == "ISS52-Q10")
        self.assertIn("degree 1 at t=1", q10["answer"]["summary"])


if __name__ == "__main__":
    unittest.main()
