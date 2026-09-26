"""Learner quality contract: calibrated on the corpus, subject-neutral, and catches degraded units."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import quality_contract, quality_observe  # noqa: E402

FIXTURES = REPO / "tests/fixtures/quality"
MANIFEST = json.loads((REPO / "benchmarks/quality-calibration/manifest.v1.json").read_text(encoding="utf-8"))


def load(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def rules_failed(obs: dict) -> set[str]:
    return set(quality_contract.evaluate(obs)["rules_failed"])


def reference_reachable() -> bool:
    ref = next(r for r in MANIFEST["references"] if r["id"] == "R2")
    return subprocess.run(["git", "-C", str(REPO), "cat-file", "-e", ref["source"]["commit"]],
                          capture_output=True).returncode == 0


class Contract(unittest.TestCase):
    def test_contract_is_well_formed_and_encodes_every_reference_grammar_step(self):
        self.assertEqual(quality_contract.check_contract(), [])

    def test_every_negative_specimen_fails_for_its_audited_findings(self):
        for spec in MANIFEST["specimens"]:
            with self.subTest(specimen=spec["id"]):
                obs = quality_observe.observe_specimen(spec)
                self.assertEqual(quality_contract.validate_observation(obs), [])
                res = quality_contract.evaluate(obs)
                expected = {f["id"] for f in spec["expected_findings"]}
                self.assertEqual(expected - set(res["audit_refs_caught"]), set(), "missed audited findings")
                extra = {r for r in res["rules_failed"]
                         if not set(next(x for x in quality_contract.contract()["rules"] if x["id"] == r)["audit_refs"]) & expected}
                self.assertEqual(extra - set(spec.get("acknowledged_extra_rules", {})), set(),
                                 "a rule fails that nobody reviewed: acknowledge it in the manifest or fix the rule")

    @unittest.skipUnless(reference_reachable(), "reference R2 commit not fetched (git fetch origin feat/all-cores-curriculum-and-speed-hacks)")
    def test_calibration_passes_including_the_question_bank_reference(self):
        report = quality_contract.calibrate()
        self.assertTrue(report["passed"], [r for r in report["rows"] if not r["ok"]])
        r2 = next(r for r in report["rows"] if r["id"] == "R2")
        self.assertEqual(r2["units"], 77)
        self.assertGreaterEqual(len(r2["grammar_rules"]), 7)


class SubjectNeutral(unittest.TestCase):
    """Phase 1 exit: Mathematics and Chemistry units fit the contract without a schema change."""

    def test_mathematics_and_chemistry_samples_are_valid_and_pass_every_unit_rule(self):
        for name in ("math-core2a-two-step-linear.observation.json", "chem-core1a-mole-concept.observation.json"):
            with self.subTest(sample=name):
                obs = load(name)
                self.assertEqual(quality_contract.validate_observation(obs), [])
                # The only product rule a sample cannot meet: nothing is rendered by the Phase 3 renderer yet.
                self.assertEqual(rules_failed(obs), {"PRODUCT-RENDERED-FROM-RECORDS"})

    def test_subject_vocabulary_decides_figure_kinds_and_check_types(self):
        obs = load("math-core2a-two-step-linear.observation.json")
        unit = obs["pages"][0]["units"][0]
        unit["figures"][0]["kind"] = "FREE_BODY_DIAGRAM"      # a Physics kind in a Mathematics unit
        unit["check_types"] = ["ATOM_CONSERVATION_STOICHIOMETRY"]
        self.assertTrue({"ALL-FIGURE-KIND-KNOWN", "ALL-CHECK-TYPES-KNOWN"} <= rules_failed(obs))


class CatchesDegradedUnits(unittest.TestCase):
    def setUp(self):
        self.obs = load("math-core2a-two-step-linear.observation.json")
        self.unit = self.obs["pages"][0]["units"][0]

    def test_missing_representation_and_short_ladder(self):
        self.unit["figures"] = []
        self.unit["support_levels"] = self.unit["support_levels"][:1]
        self.assertTrue({"C2A-REPRESENTATION", "C2A-LADDER"} <= rules_failed(self.obs))

    def test_generic_support_repeated_across_items(self):
        twin = copy.deepcopy(self.unit)
        twin["id"] = "Q-MATH-LIN-2A-TWIN"
        self.obs["pages"][0]["units"].append(twin)
        self.assertIn("C2A-SPECIFIC-SUPPORT", rules_failed(self.obs))

    def test_solution_visible_before_an_attempt(self):
        self.unit["reveals"][0]["gated"] = False
        self.assertIn("C2A-REVEAL-GATED", rules_failed(self.obs))

    def test_placeholder_and_escape_state(self):
        self.unit["placeholders"] = ["Independent checks None supplied by the governed record."]
        self.obs["escape_states"] = ["HOLD"]
        self.assertTrue({"ALL-NO-PLACEHOLDER", "PRODUCT-NO-ESCAPE-STATE"} <= rules_failed(self.obs))

    def test_compressed_construction_and_unbridged_prerequisite(self):
        obs = load("chem-core1a-mole-concept.observation.json")
        unit = obs["pages"][0]["units"][0]
        unit["decisions"], unit["worked_anchors"] = 7, 1
        unit["prerequisites_bridged"] = unit["prerequisites_bridged"][:1]
        self.assertTrue({"C1A-ANCHOR-PER-DECISION", "C1A-PREREQUISITES-BRIDGED"} <= rules_failed(obs))


if __name__ == "__main__":
    unittest.main()
