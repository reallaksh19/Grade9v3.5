#!/usr/bin/env python3
"""Regression tests for the governed Graphical Cognitive Deconstruction Route."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]

from Shared.tools import explorer_design_guard


class ExplorerDesignContractTest(unittest.TestCase):
    def test_committed_gcdr_activities_pass_the_guard(self):
        self.assertEqual(explorer_design_guard.findings(REPO), [])

    def test_motion2d_gcdr_contracts_are_honestly_partial(self):
        package = json.loads(
            (REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
        )
        activities = [
            row for row in package["resources"]
            if row["id"].startswith("ACT-KIN-2D-")
        ]
        self.assertEqual(len(activities), 6)
        for row in activities:
            with self.subTest(activity=row["id"]):
                atlas = row["extensions"]["topic_atlas"]
                self.assertEqual(atlas["activity_kind"], "GRAPHICAL_COGNITIVE_DECONSTRUCTION")
                contract = atlas["gcdr_contract"]
                self.assertEqual(contract["schema_version"], "1.1.0")
                self.assertEqual(contract["conformance_status"], "IMPLEMENTATION_PARTIAL")
                self.assertEqual(contract["quality_audit"]["audit_status"], "PARTIAL")
                self.assertEqual(
                    contract["state_fidelity_contract"]["missing_parameter_policy"],
                    "NEVER_INVENT_AS_EXACT",
                )
                self.assertFalse(
                    contract["implementation_evidence"]["fresh_transfer_without_scaffold"],
                    "Prototype must not claim fresh-transfer implementation before it exists",
                )
                self.assertFalse(
                    contract["implementation_evidence"]["scaffold_fade"],
                    "Prototype must not claim scaffold fade before it exists",
                )

    def test_false_certification_is_rejected(self):
        package = json.loads(
            (REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
        )
        activity = next(
            row for row in package["resources"]
            if row["id"] == "ACT-KIN-2D-APEX-FALLACY"
        )
        activity = copy.deepcopy(activity)
        activity["extensions"]["topic_atlas"]["gcdr_contract"]["conformance_status"] = "CERTIFIED"

        mini = {
            "resources": [activity],
            "capabilities": [
                {"id": "CAP-KIN-PROJECTILE-MODEL"}
            ],
            "microtopics": [{
                "teaching_path": [{"id": "K2D3-4"}]
            }],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Shared/library").mkdir(parents=True)
            (root / "Physics/library").mkdir(parents=True)
            (root / "public/physics/motion-2d/explorers/apex-fallacy").mkdir(parents=True)
            (root / "Shared/library/explorer_design_contract.schema.json").write_text(
                (REPO / "Shared/library/explorer_design_contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "Physics/library/test.json").write_text(
                json.dumps(mini), encoding="utf-8"
            )
            (root / activity["locator"]).write_text("<html></html>", encoding="utf-8")

            found = explorer_design_guard.findings(root)

        self.assertIn("FALSE_CERTIFICATION", {row["point"] for row in found})

    def test_quality_audit_pass_with_pending_check_is_rejected(self):
        package = json.loads(
            (REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
        )
        activity = copy.deepcopy(next(
            row for row in package["resources"]
            if row["id"] == "ACT-KIN-2D-SHARED-CLOCK"
        ))
        audit = activity["extensions"]["topic_atlas"]["gcdr_contract"]["quality_audit"]
        audit["audit_status"] = "PASS"
        audit["audit_evidence_refs"] = ["TEST-EVIDENCE"]

        mini = {
            "resources": [activity],
            "capabilities": [{"id": "CAP-KIN-2D-INDEPENDENT-COMPONENTS"}],
            "microtopics": [{"teaching_path": [{"id": "K2D1-3"}, {"id": "K2D1-4"}]}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Shared/library").mkdir(parents=True)
            (root / "Physics/library").mkdir(parents=True)
            (root / "public/physics/motion-2d/explorers/shared-clock").mkdir(parents=True)
            (root / "Shared/library/explorer_design_contract.schema.json").write_text(
                (REPO / "Shared/library/explorer_design_contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "Physics/library/test.json").write_text(json.dumps(mini), encoding="utf-8")
            (root / activity["locator"]).write_text("<html></html>", encoding="utf-8")
            found = explorer_design_guard.findings(root)

        self.assertIn("FALSE_AUDIT_PASS", {row["point"] for row in found})

    def test_not_applicable_quality_check_requires_waiver(self):
        package = json.loads(
            (REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
        )
        activity = copy.deepcopy(next(
            row for row in package["resources"]
            if row["id"] == "ACT-KIN-2D-SHARED-CLOCK"
        ))
        audit = activity["extensions"]["topic_atlas"]["gcdr_contract"]["quality_audit"]
        audit["audit_3_reconstruction_teaching_transfer"]["answer_or_disposition_specific"] = "NOT_APPLICABLE"

        mini = {
            "resources": [activity],
            "capabilities": [{"id": "CAP-KIN-2D-INDEPENDENT-COMPONENTS"}],
            "microtopics": [{"teaching_path": [{"id": "K2D1-3"}, {"id": "K2D1-4"}]}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Shared/library").mkdir(parents=True)
            (root / "Physics/library").mkdir(parents=True)
            (root / "public/physics/motion-2d/explorers/shared-clock").mkdir(parents=True)
            (root / "Shared/library/explorer_design_contract.schema.json").write_text(
                (REPO / "Shared/library/explorer_design_contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "Physics/library/test.json").write_text(json.dumps(mini), encoding="utf-8")
            (root / activity["locator"]).write_text("<html></html>", encoding="utf-8")
            found = explorer_design_guard.findings(root)

        self.assertIn("UNJUSTIFIED_NOT_APPLICABLE", {row["point"] for row in found})

    def test_rejoin_step_must_be_one_of_the_activity_leaf_bindings(self):
        package = json.loads(
            (REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8")
        )
        activity = copy.deepcopy(next(
            row for row in package["resources"]
            if row["id"] == "ACT-KIN-2D-EVENT-CLOCK"
        ))
        activity["extensions"]["topic_atlas"]["gcdr_contract"]["exit_evidence"][
            "rejoin_step_ref"
        ] = "K2D3-4"

        mini = {
            "resources": [activity],
            "capabilities": [{"id": "CAP-KIN-2D-CONSTANT-ACCELERATION"}],
            "microtopics": [{"teaching_path": [{"id": "K2D2-3"}, {"id": "K2D3-4"}]}],
        }

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Shared/library").mkdir(parents=True)
            (root / "Physics/library").mkdir(parents=True)
            (root / "public/physics/motion-2d/explorers/event-clock").mkdir(parents=True)
            (root / "Shared/library/explorer_design_contract.schema.json").write_text(
                (REPO / "Shared/library/explorer_design_contract.schema.json").read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            (root / "Physics/library/test.json").write_text(json.dumps(mini), encoding="utf-8")
            (root / activity["locator"]).write_text("<html></html>", encoding="utf-8")

            found = explorer_design_guard.findings(root)

        self.assertIn("REJOIN_OUTSIDE_BINDING", {row["point"] for row in found})


if __name__ == "__main__":
    unittest.main()
