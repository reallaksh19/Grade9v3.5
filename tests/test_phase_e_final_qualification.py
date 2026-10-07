from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from Shared.tools import build_core_learning_data, build_products, render_core


REPO = Path(__file__).resolve().parents[1]
GRAPH = REPO / "evidence/architectural-recovery/ISS69/phase-e-delp-execution-graph.v32.json"
EVIDENCE = REPO / "evidence/architectural-recovery/ISS69/phase-e-e02-final-qualification.v1.json"
MANIFEST = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
LEGACY_REVIEW = REPO / "products/verification/phy-kin-2d-motion.review.json"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class PhaseEFinalQualification(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = json.loads(GRAPH.read_text(encoding="utf-8"))
        cls.review = json.loads(LEGACY_REVIEW.read_text(encoding="utf-8"))
        cls.pages, cls.gaps, cls.render_digest = render_core.build(MANIFEST, mode="PAGES")
        cls.evidence = json.loads(EVIDENCE.read_text(encoding="utf-8")) if EVIDENCE.is_file() else None

    def test_e02_v32_leaf_is_bounded_and_exactly_six_units(self):
        node = next(row for row in self.graph["nodes"] if row["ref"].endswith("#116"))
        self.assertEqual(node["responsibility_id"], "ISS69-E02-FINAL-QUALIFICATION")
        self.assertEqual(len(node["units"]), 6)
        total = sum(row["weight"] for row in node["units"])
        self.assertTrue(all(row["weight"] * 100 <= total * 40 for row in node["units"]))
        self.assertLessEqual(node["size_budget"]["target_loc"], 700)
        self.assertLessEqual(node["size_budget"]["hard_loc"], 1500)
        self.assertIn("tests/test_phase_e_final_qualification.py", node["write_surface"])

    def test_final_tree_generated_projection_is_fresh_and_mirrored(self):
        public = REPO / "public/core-learning/data.js"
        docs = REPO / "docs/core-learning/data.js"
        self.assertEqual(public.read_bytes(), docs.read_bytes())
        self.assertNotIn("BP-CORE1A-CONSTRUCTION@1.7.0", public.read_text(encoding="utf-8"))

        rows = build_core_learning_data.build()["core_projections"]
        core1a = [r for r in rows if (r.get("projection") or {}).get("core") == "CORE1A"]
        self.assertTrue(core1a)
        for row in core1a:
            web = ((row["projection"].get("delivery") or {}).get("web") or {})
            self.assertEqual(web["blueprint_ref"], "BP-CORE1A-CONSTRUCTION@1.8.0")

        for row in [r for r in rows if (r.get("projection") or {}).get("core") == "CORE2"]:
            web = ((row["projection"].get("delivery") or {}).get("web") or {})
            self.assertEqual(web["blueprint_ref"], "BP-CORE2-SOURCE-QUESTION@1.11.0")

    def test_exact_motion_render_has_zero_gaps_and_active_blueprints(self):
        self.assertEqual(self.gaps, [])
        self.assertEqual(len(self.render_digest), 16)
        self.assertIn('data-blueprint-ref="BP-CORE1A-CONSTRUCTION@1.8.0"', self.pages["core1a.html"])
        self.assertIn('data-blueprint-ref="BP-CORE2-SOURCE-QUESTION@1.11.0"', self.pages["core2.html"])

    def test_legacy_motion_review_is_stale_for_current_render(self):
        old = self.review["render_digest"]
        self.assertEqual(old, "5e64f1570dc30ee2")
        self.assertNotEqual(old, self.render_digest)
        review_state, _published = build_products.decision_state(
            "phy-kin-2d-motion", "Physics", self.render_digest
        )
        self.assertEqual(review_state, "REVIEW_STALE")

    def test_final_evidence_binds_exact_generated_and_rendered_bytes(self):
        if self.evidence is None:
            self.skipTest("final E02 evidence is added only after the test itself is absorbed by the architecture manifest")

        evidence = self.evidence
        self.assertEqual(evidence["schema_version"], "grade9v3-phase-e-e02-final-qualification-v1")
        self.assertEqual(evidence["result"], "PASS_TECHNICAL_EXACT_HEAD_WITH_INHERITED_DEBT")

        generated = evidence["generated_bytes"]
        for relative in (
            "docs/architecture-manifest.json",
            "public/core-learning/data.js",
            "docs/core-learning/data.js",
        ):
            self.assertEqual(sha256(REPO / relative), generated[relative]["sha256"])

        rendered = evidence["rendered_evidence"]
        self.assertEqual(self.render_digest, rendered["render_digest"])
        self.assertEqual(
            hashlib.sha256(self.pages["core1a.html"].encode("utf-8")).hexdigest(),
            rendered["core1a_sha256"],
        )
        self.assertEqual(
            hashlib.sha256(self.pages["core2.html"].encode("utf-8")).hexdigest(),
            rendered["core2_sha256"],
        )
        self.assertEqual(rendered["gaps"], 0)

        stale = evidence["stale_receipt_invalidation"]
        self.assertEqual(stale["path"], "products/verification/phy-kin-2d-motion.review.json")
        self.assertEqual(stale["blob"], "4b4fe31524795102702c9de2a0c022b0d7db9680")
        self.assertEqual(stale["old_render_digest"], self.review["render_digest"])
        self.assertEqual(stale["current_render_digest"], self.render_digest)
        self.assertEqual(stale["disposition"], "REVIEW_STALE_DO_NOT_REUSE")

    def test_browser_evidence_and_non_grants_are_explicit(self):
        if self.evidence is None:
            self.skipTest("browser evidence is finalized after the retained exact-head artifact exists")

        browser = self.evidence["browser"]
        self.assertEqual(browser["workflow_run"], 37570371462)
        self.assertEqual(browser["artifact_id"], 11460701514)
        self.assertEqual(browser["core1a"]["blueprint"], "BP-CORE1A-CONSTRUCTION@1.8.0")
        self.assertEqual(browser["core2"]["blueprint"], "BP-CORE2-SOURCE-QUESTION@1.11.0")
        for role in ("core1a", "core2"):
            facts = browser[role]
            self.assertEqual(facts["horizontal_overflow_max_px"], 0)
            self.assertEqual(facts["browser_errors"], 0)
            self.assertEqual(facts["small_targets"], 0)
            self.assertEqual(facts["focus_failures"], 0)
            self.assertEqual(facts["premature_gated_open"], 0)
            self.assertEqual(facts["protected_search_matches"], 0)

        self.assertEqual(browser["core2_state_round_trip"], "PASS")
        self.assertEqual(
            browser["progressive_support_selected_witness"],
            "NOT_APPLICABLE",
        )

        self.assertEqual(
            self.evidence["non_grants"],
            {
                "merge_to_main": False,
                "golden_promotion": False,
                "learner_publication": False,
                "independent_academic_acceptance": False,
                "learning_effectiveness": False,
            },
        )


if __name__ == "__main__":
    unittest.main()
