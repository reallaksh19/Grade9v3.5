"""External-provider prerequisites stay explicit without blocking the whole study route."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import study_map, study_route, study_scope_audit, study_start  # noqa: E402
from Shared.tools import worksheet_study_plan  # noqa: E402


class ExternalProviderBridge(unittest.TestCase):
    def fixture(self):
        tmp = tempfile.TemporaryDirectory()
        root = Path(tmp.name)
        (root / "Example/library").mkdir(parents=True)
        (root / "Example/matrices").mkdir(parents=True)
        (root / "Shared/library").mkdir(parents=True)
        (root / "Shared/library/worksheet-map.schema.json").write_text(
            (REPO / "Shared/library/worksheet-map.schema.json").read_text(
                encoding="utf-8"
            ),
            encoding="utf-8",
        )
        (root / "Example/library/example.json").write_text(json.dumps({
            "capabilities": [
                {
                    "id": "CAP-EXT",
                    "action": "Use the external prerequisite.",
                    "success_criterion": "External prerequisite is usable.",
                    "prerequisite_refs": [],
                    "external_provider": "Mathematics",
                    "acceptance_status": "PROVIDER_REVIEW_REQUIRED",
                },
                {
                    "id": "CAP-MAIN",
                    "action": "Apply the main capability.",
                    "success_criterion": "Main capability is applied.",
                    "prerequisite_refs": ["CAP-EXT"],
                },
            ],
            "microtopics": [{
                "id": "MIC-MAIN",
                "title": "Main lesson",
                "primary_capability_ref": "CAP-MAIN",
                "misconceptions": [],
            }],
            "questions": [],
        }), encoding="utf-8")
        (root / "Example/matrices/main.rungs.json").write_text(json.dumps({
            "matrix_id": "MATRIX-MAIN",
            "bucket_id": "BUCKET-MAIN",
            "topic": "Example",
            "subtopic": "Main",
            "rungs": [{
                "rung": "R1",
                "ladder_position": 20,
                "microtopic_ref": "MIC-MAIN",
            }],
        }), encoding="utf-8")
        mapping = {
            "worksheet_id": "EXTERNAL-BRIDGE-DEMO",
            "subject": "Example",
            "questions": [{
                "question_id": "Q1",
                "primary_capability_ref": "CAP-MAIN",
                "secondary_capability_refs": [],
                "mapping_basis": "MANUAL",
            }],
        }
        return tmp, root, mapping

    def test_prerequisite_external_provider_is_bridge_not_missing_teaching(self):
        tmp, root, mapping = self.fixture()
        try:
            report = study_route.resolve(mapping, root)
        finally:
            tmp.cleanup()

        self.assertTrue(report["passed"], report["findings"])
        rows = {row["capability_ref"]: row for row in report["route"]}
        bridge = rows["CAP-EXT"]
        self.assertEqual(bridge["state"], "EXTERNAL_BRIDGE")
        self.assertEqual(bridge["external_provider"], "Mathematics")
        self.assertEqual(bridge["acceptance_status"], "PROVIDER_REVIEW_REQUIRED")
        self.assertLess(bridge["order"], rows["CAP-MAIN"]["order"])
        self.assertNotIn(
            study_route.NO_TEACHING_LOCATION,
            [row["point"] for row in report["findings"]],
        )

    def test_direct_worksheet_demand_can_resolve_to_explicit_external_bridge(self):
        tmp, root, mapping = self.fixture()
        mapping["questions"][0]["primary_capability_ref"] = "CAP-EXT"
        try:
            report = study_map.resolve(mapping, root)
        finally:
            tmp.cleanup()

        self.assertTrue(report["passed"], report["findings"])
        cap = report["questions"][0]["capabilities"][0]
        self.assertEqual(cap["state"], "EXTERNAL_BRIDGE")
        self.assertEqual(cap["external_provider"], "Mathematics")
        self.assertEqual(cap["locations"], [])

    def test_scope_audit_accepts_declared_external_bridge(self):
        tmp, root, mapping = self.fixture()
        try:
            report = study_scope_audit.audit(mapping, repo=root)
        finally:
            tmp.cleanup()

        self.assertTrue(report["passed"], report["findings"])
        bridge = next(
            row for row in report["route"]
            if row["capability_ref"] == "CAP-EXT"
        )
        self.assertEqual(bridge["state"], "EXTERNAL_BRIDGE")

    def test_study_start_turns_external_provider_into_bridge_action(self):
        tmp, root, mapping = self.fixture()
        try:
            report = study_start.resolve(mapping, [], root)
        finally:
            tmp.cleanup()

        self.assertTrue(report["passed"], report["findings"])
        rows = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(rows["CAP-EXT"]["learner_action"], "BRIDGE")
        self.assertEqual(rows["CAP-MAIN"]["learner_action"], "QUICK_CHECK")
        self.assertTrue(rows["CAP-MAIN"]["gateway_basis"]["not_evidence"])

    def test_learner_facing_plan_names_provider_and_continues(self):
        tmp, root, mapping = self.fixture()
        try:
            report = worksheet_study_plan.resolve(mapping, repo=root)
            rendered = worksheet_study_plan.readable(report)
        finally:
            tmp.cleanup()

        self.assertTrue(report["passed"], report["findings"])
        rows = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(rows["CAP-EXT"]["recommended_action"], "BRIDGE")
        self.assertIn("Mathematics", rows["CAP-EXT"]["action_reason"])
        self.assertIn("External bridge: Mathematics", rendered)
        self.assertEqual(rows["CAP-MAIN"]["recommended_action"], "QUICK_CHECK")


if __name__ == "__main__":
    unittest.main()
