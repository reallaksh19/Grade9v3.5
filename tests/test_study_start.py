"""Subtopic-wise rough estimates choose practical local start points, not mastery."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import study_start  # noqa: E402


class StudyStartOverlay(unittest.TestCase):
    PHYSICS = REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json"

    def mapping(self):
        return json.loads(self.PHYSICS.read_text(encoding="utf-8"))

    def by_capability(self, report):
        return {row["capability_ref"]: row for row in report["route"]}

    def test_estimates_apply_only_inside_their_local_matrices(self):
        report = study_start.resolve(self.mapping(), [
            {
                "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
                "knowledge_percentage": 75,
            },
            {
                "matrix_id": "MATRIX-PHY-NLM-FIRST-LAW",
                "knowledge_percentage": 75,
            },
            {
                "matrix_id": "MATRIX-PHY-WORK-ENERGY-POWER",
                "knowledge_percentage": 65,
            },
        ])
        self.assertTrue(report["passed"], report["findings"])
        rows = self.by_capability(report)

        self.assertEqual(rows["CAP-KIN-DISTANCE-DISPLACEMENT"]["learner_action"], "QUICK_CHECK")
        self.assertEqual(rows["CAP-KIN-ZERO-V-NONZERO-A"]["learner_action"], "START_HERE")

        self.assertEqual(rows["CAP-NLM-NET-ZERO-MOTION"]["learner_action"], "QUICK_CHECK")
        self.assertEqual(rows["CAP-NLM-FORCES-SUM-ZERO"]["learner_action"], "QUICK_CHECK")
        self.assertEqual(rows["CAP-NLM-FBD-BODY-OWNERSHIP"]["learner_action"], "START_HERE")

        self.assertEqual(rows["CAP-WEP-WORK-DIRECTION"]["learner_action"], "QUICK_CHECK")
        self.assertEqual(rows["CAP-WEP-NET-WORK-SIGN"]["learner_action"], "QUICK_CHECK")
        self.assertEqual(rows["CAP-WEP-POTENTIAL-ELIGIBILITY"]["learner_action"], "START_HERE")
        self.assertEqual(rows["CAP-WEP-MECH-ENERGY-CONDITION"]["learner_action"], "STUDY")

    def test_quick_check_is_never_written_as_demonstrated_mastery(self):
        report = study_start.resolve(self.mapping(), [{
            "matrix_id": "MATRIX-PHY-NLM-FIRST-LAW",
            "knowledge_percentage": 75,
        }])
        quick = [row for row in report["route"] if row["learner_action"] == "QUICK_CHECK"]
        self.assertTrue(quick)
        rendered = json.dumps(quick)
        self.assertNotIn('"DEMONSTRATED"', rendered)
        for row in quick:
            basis = row.get("estimate_basis") or row.get("gateway_basis")
            self.assertIsNotNone(basis)
            self.assertTrue(basis["not_evidence"])

    def test_no_estimate_uses_a_bounded_local_gateway_not_mastery(self):
        report = study_start.resolve(self.mapping(), [])
        self.assertTrue(report["passed"], report["findings"])
        self.assertTrue(report["route"])
        quick = [row for row in report["route"] if row["learner_action"] == "QUICK_CHECK"]
        study = [row for row in report["route"] if row["learner_action"] == "STUDY"]
        self.assertTrue(quick)
        self.assertTrue(study)
        self.assertTrue(report["gateway_decisions"])
        self.assertTrue(all(len(row["capability_refs"]) <= 1 for row in report["gateway_decisions"]))
        self.assertTrue(all(row["gateway_basis"]["not_evidence"] for row in quick))
        self.assertNotIn('"DEMONSTRATED"', json.dumps(report["gateway_decisions"]))

    def test_estimate_below_first_teaching_point_starts_at_first_teaching_point(self):
        report = study_start.resolve(self.mapping(), [{
            "matrix_id": "MATRIX-PHY-WORK-ENERGY-POWER",
            "knowledge_percentage": 5,
        }])
        self.assertTrue(report["passed"], report["findings"])
        decision = report["start_decisions"][0]
        self.assertEqual(decision["selected_rung"], "R1")
        self.assertEqual(decision["selected_position"], 20)
        rows = self.by_capability(report)
        self.assertEqual(rows["CAP-WEP-WORK-DIRECTION"]["learner_action"], "START_HERE")

    def test_recordless_matrix_rung_is_not_used_as_a_start_coordinate(self):
        mapping = {
            "worksheet_id": "START-FALSIFIER",
            "subject": "Physics",
            "questions": [],
        }
        route = {
            "worksheet_id": "START-FALSIFIER",
            "subject": "Physics",
            "route": [{
                "order": 1,
                "capability_ref": "CAP-A",
                "scope": "PREREQUISITE",
                "reasons": ["PREREQUISITE"],
                "required_by_questions": [],
                "syllabus_source_refs": [],
                "depends_on": [],
                "locations": [{
                    "matrix_id": "MATRIX-X",
                    "bucket_id": "BUCKET-X",
                    "rung": "R1",
                    "ladder_position": 20,
                    "microtopic_ref": "MIC-A",
                }],
                "state": "RESOLVED",
            }],
            "findings": [],
            "passed": True,
        }
        index = {
            "locations": {
                "CAP-A": [{
                    "matrix_id": "MATRIX-X",
                    "bucket_id": "BUCKET-X",
                    "rung": "R1",
                    "ladder_position": 20,
                    "microtopic_ref": "MIC-A",
                }],
                "CAP-B": [{
                    "matrix_id": "MATRIX-X",
                    "bucket_id": "BUCKET-X",
                    "rung": "R3",
                    "ladder_position": 80,
                    "microtopic_ref": "MIC-B",
                }],
            },
        }
        boards = {
            "MATRIX-X": {
                "matrix_id": "MATRIX-X",
                "bucket_id": "BUCKET-X",
                "topic": "Synthetic",
                "subtopic": "Start falsifier",
                "rungs": [
                    {"rung": "R1", "ladder_position": 20, "microtopic_ref": "MIC-A"},
                    {"rung": "R2", "ladder_position": 50, "microtopic_ref": None},
                    {"rung": "R3", "ladder_position": 80, "microtopic_ref": "MIC-B"},
                ],
            },
        }
        with patch.object(
            study_start.study_route,
            "resolve",
            return_value=route,
        ), patch.object(
            study_start.study_map,
            "subject_index",
            return_value=index,
        ), patch.object(
            study_start,
            "_boards",
            return_value=boards,
        ):
            report = study_start.resolve(mapping, [{
                "matrix_id": "MATRIX-X",
                "knowledge_percentage": 50,
            }])

        self.assertTrue(report["passed"], report["findings"])
        decision = report["start_decisions"][0]
        self.assertEqual(decision["selected_rung"], "R1")
        self.assertEqual(decision["selected_position"], 20)

    def test_bucket_id_can_be_used_when_it_identifies_one_matrix(self):
        report = study_start.resolve(self.mapping(), [{
            "bucket_id": "BUCKET-PHY-WORK-ENERGY-POWER",
            "knowledge_percentage": 65,
        }])
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(
            report["start_decisions"][0]["matrix_id"],
            "MATRIX-PHY-WORK-ENERGY-POWER",
        )

    def test_unknown_matrix_estimate_warns_and_falls_back_to_neutral_route(self):
        report = study_start.resolve(self.mapping(), [{
            "matrix_id": "MATRIX-NOT-REAL",
            "knowledge_percentage": 50,
        }])
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["findings"], [])
        self.assertEqual(report["execution_disposition"], "EXECUTE_WITH_FALLBACK")
        self.assertIn(
            "STUDY_START_MATRIX_UNKNOWN",
            [row["point"] for row in report["warnings"]],
        )
        self.assertTrue(report["route"])

    def test_out_of_range_estimate_warns_and_falls_back_to_neutral_route(self):
        report = study_start.resolve(self.mapping(), [{
            "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
            "knowledge_percentage": 140,
        }])
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["execution_disposition"], "EXECUTE_WITH_FALLBACK")
        self.assertIn(
            "STUDY_START_ESTIMATE_OUT_OF_RANGE",
            [row["point"] for row in report["warnings"]],
        )

    def test_duplicate_estimate_warns_and_keeps_first_deterministic_choice(self):
        report = study_start.resolve(self.mapping(), [
            {
                "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
                "knowledge_percentage": 40,
            },
            {
                "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
                "knowledge_percentage": 70,
            },
        ])
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["execution_disposition"], "EXECUTE_WITH_FALLBACK")
        self.assertIn(
            "STUDY_START_ESTIMATE_DUPLICATE",
            [row["point"] for row in report["warnings"]],
        )
        self.assertEqual(report["start_decisions"][0]["knowledge_percentage"], 40)


if __name__ == "__main__":
    unittest.main()
