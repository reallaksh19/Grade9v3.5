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


    def test_layout_rule_keeps_legacy_id_but_uses_blueprint_semantics(self):
        rule = next(r for r in quality_contract.contract()["rules"] if r["id"] == "PAGE-STAGE-SUPPORT")
        self.assertEqual(rule["check"], {"op": "rendered_flag", "field": "stage_support_layout"})
        self.assertIn("selected blueprint", rule["text"].lower())
        self.assertNotIn("0.68/0.32", rule["text"])


    def test_core1a_legacy_quality_rules_do_not_reintroduce_optional_operators(self):
        rules = {r["id"]: r for r in quality_contract.contract()["rules"]}
        self.assertEqual(
            rules["C1A-BLOCKS"]["check"]["blocks"],
            ["inferential_jump", "construction", "exit_task"],
        )
        self.assertNotIn("worked_anchor", rules["C1A-BLOCKS"]["check"]["blocks"])
        self.assertNotIn("wrong_path", rules["C1A-BLOCKS"]["check"]["blocks"])
        self.assertNotIn("independent_check", rules["C1A-BLOCKS"]["check"]["blocks"])
        self.assertEqual(rules["C1A-REPRESENTATION-BRIDGE"]["check"]["min"], 0)
        self.assertIn("selected blueprint", rules["C1A-REPRESENTATION-BRIDGE"]["text"].lower())
        self.assertIn("not a failure by itself", rules["C1A-ANCHOR-PER-DECISION"]["text"])

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

    def test_product_figure_kind_comes_from_subject_core_contract(self):
        declared = json.loads((REPO / "Physics/adapter/CoreContracts.json").read_text(encoding="utf-8"))
        known = set(quality_contract.vocabulary("Physics")["representation_kinds"])
        self.assertTrue({row["id"] for row in declared["representation_kinds"]} <= known)
        self.assertIn("MOTION_DIAGRAM", known)  # existing quality-only figure vocabulary

        obs = load("math-core2a-two-step-linear.observation.json")
        obs["subject"] = "Physics"
        obs["pages"][0]["units"][0]["figures"][0]["kind"] = "CIRCUIT_SCHEMATIC"
        self.assertNotIn("ALL-FIGURE-KIND-KNOWN", rules_failed(obs))
        obs["pages"][0]["units"][0]["figures"][0]["kind"] = "NOT_DECLARED"
        self.assertIn("ALL-FIGURE-KIND-KNOWN", rules_failed(obs))


class RenderedMetadataSafety(unittest.TestCase):
    NEW_RULES = {
        "PAGE-METADATA-PRESENCE",
        "PAGE-SAFE-SEARCH-CORPUS",
        "PAGE-PROTECTED-SEARCH",
        "PAGE-GATED-INITIAL",
    }

    def test_new_browser_safety_rules_are_not_measured_without_browser_facts(self):
        obs = load("math-core2a-two-step-linear.observation.json")
        res = quality_contract.evaluate(obs)
        self.assertTrue(self.NEW_RULES <= set(res["not_measured"]))

    def test_browser_safety_facts_pass_at_zero_and_fail_when_protected_search_matches(self):
        obs = load("math-core2a-two-step-linear.observation.json")
        obs["pages"][0]["rendered"] = {
            "small_targets": 0,
            "stage_support_layout": True,
            "min_font_px": 16,
            "metadata_missing_units": 0,
            "search_corpus_missing_units": 0,
            "protected_search_matches": 0,
            "gated_open_before_attempt": 0,
        }
        self.assertEqual(self.NEW_RULES & rules_failed(obs), set())
        obs["pages"][0]["rendered"]["protected_search_matches"] = 1
        self.assertIn("PAGE-PROTECTED-SEARCH", rules_failed(obs))


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


    def test_absent_worked_anchor_is_not_density_debt(self):
        obs = load("chem-core1a-mole-concept.observation.json")
        unit = obs["pages"][0]["units"][0]
        unit["decisions"], unit["worked_anchors"] = 7, 0
        self.assertNotIn("C1A-ANCHOR-PER-DECISION", rules_failed(obs))


if __name__ == "__main__":
    unittest.main()
