"""Cross-Core progression integrity falsifiers."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.library import core_progression, source_custody  # noqa: E402
from Shared.library.resolve import build_index  # noqa: E402


class CrossCoreProgression(unittest.TestCase):
    def test_current_tree_has_nonvacuous_family_progression_report(self):
        report = core_progression.audit(REPO)
        self.assertTrue(report["passed"], report["findings"])
        self.assertGreater(report["summary"]["practice_families"], 0)
        self.assertGreater(report["summary"]["core2a_questions"], 0)
        self.assertGreater(report["summary"]["core2b_questions"], 0)
        self.assertFalse(report["semantics"]["renderability_is_readiness"])
        self.assertFalse(
            report["semantics"]["competitive_bank_evidence_is_ordinary_core2_custody"]
        )

    def test_real_nlm_family_joins_verified_bank_demand_without_rewriting_provenance(self):
        report = core_progression.audit(REPO)
        row = next(
            item for item in report["families"]
            if item["subject"] == "Physics"
            and item["family_ref"] == "FAM-PHY-NLM-PRACTICE"
        )
        self.assertEqual(
            row["source_demand_state"],
            "COMPETITIVE_BANK_VERIFIED_DEMAND",
        )
        self.assertTrue(row["source_demand_evidenced"])
        self.assertTrue(row["core2a_question_refs"])
        self.assertTrue(row["core2b_question_refs"])
        self.assertTrue(any(
            anchor["kind"] == "COMPETITIVE_BANK_VERIFIED_DEMAND"
            for anchor in row["source_anchors"]
        ))

    def test_relative_motion_family_joins_verified_v2_bank_demand(self):
        report = core_progression.audit(REPO)
        row = next(
            item for item in report["families"]
            if item["subject"] == "Physics"
            and item["family_ref"] == "FAM-RELATIVE-V"
        )
        self.assertEqual(
            row["source_demand_state"],
            "COMPETITIVE_BANK_VERIFIED_DEMAND",
        )
        self.assertTrue(row["source_demand_evidenced"])
        self.assertEqual(len(row["source_anchors"]), 3)
        self.assertNotIn("SOURCE_DEMAND_NOT_YET_EVIDENCED", row["gaps"])

    def test_incline_family_does_not_inherit_broad_nlm_bank_evidence(self):
        report = core_progression.audit(REPO)
        row = next(
            item for item in report["families"]
            if item["subject"] == "Physics"
            and item["family_ref"] == "FAM-PHY-NLM-INCLINE-MODELLING"
        )
        self.assertEqual(
            row["source_demand_state"],
            "SOURCE_DEMAND_NOT_YET_EVIDENCED",
        )
        self.assertIn("SOURCE_DEMAND_NOT_YET_EVIDENCED", row["gaps"])

    def test_authored_practice_is_never_an_ordinary_core2_anchor(self):
        physics = REPO / "Physics"
        records = core_progression.ordinary_records(physics)
        authored = [
            q for q in records.values()
            if q.get("_collection") == "questions" and q.get("origin") == "AUTHORED"
        ]
        self.assertTrue(authored)
        self.assertFalse(any(
            source_custody.valid_for_core2(q, records) for q in authored
        ))

    def test_core2b_parent_must_be_a_familiar_same_family_anchor(self):
        package_path = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package = copy.deepcopy(package)
        transfer = next(
            q for q in package["questions"]
            if any(e.get("core") == "CORE2B" for e in q.get("exposure", []))
            and isinstance(q.get("adaptation"), dict)
        )
        parent = next(
            q for q in package["questions"]
            if q["id"] == transfer["adaptation"]["parent_ref"]
        )
        parent["family_ref"] = "FAM-PLANTED-DIFFERENT"
        records = build_index([package])
        findings = core_progression._b_pair_findings(transfer, records)
        self.assertIn(
            "CORE_PROGRESSION_TRANSFER_FAMILY_CHANGED",
            [row["point"] for row in findings],
        )

    def test_competitive_bank_anchor_is_evidence_not_library_record_injection(self):
        physics = REPO / "Physics"
        records = core_progression.ordinary_records(physics)
        ids_before = set(records)
        anchors = core_progression.bank_anchors(physics)
        self.assertTrue(anchors)
        self.assertEqual(ids_before, set(records))
        self.assertTrue(all(anchor["question_id"] not in records for anchor in anchors))


if __name__ == "__main__":
    unittest.main()
