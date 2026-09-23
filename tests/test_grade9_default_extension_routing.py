"""Ordinary Grade-9 placement must not turn retained extensions into requirements."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import (  # noqa: E402
    capability_graph,
    compile_execution_packet,
    plan_request,
    resolve_request,
    study_map,
    study_start,
)


class Grade9DefaultExtensionRouting(unittest.TestCase):
    TARGETS = {
        "Physics/matrices/phy-kin-1d-motion.rungs.json": {"R3", "R6"},
        "Physics/matrices/phy-nlm-first-law.rungs.json": {"R4"},
        "Physics/matrices/phy-grav-universal-law.rungs.json": {"R4", "R5"},
    }

    def matrix(self, relative: str) -> dict:
        return json.loads((REPO / relative).read_text(encoding="utf-8"))

    def request(self, bucket: str, percentage: int) -> dict:
        return {
            "request_id": f"TEST-{bucket}-{percentage}",
            "subject": "Physics",
            "bucket_id": bucket,
            "cores": ["CORE1A", "CORE1B"],
            "learner": {"owner_estimate": {"knowledge_percentage": percentage, "by": "owner", "instruction": "routing estimate only"}},
        }

    def author_request(self, subtopic: str, learner: dict) -> dict:
        return {"request_id": f"AUTHOR-{subtopic}", "subject": "Physics", "subtopic": subtopic, "requested_cores": ["CORE1A", "CORE1B"], "learner": learner}

    def test_only_audited_grade9_extensions_are_nondefault(self):
        for relative, expected in self.TARGETS.items():
            with self.subTest(matrix=relative):
                board = self.matrix(relative)
                actual = {row["rung"] for row in board["rungs"] if row.get("default_entry_eligible", True) is False}
                self.assertEqual(actual, expected)

    def test_owner_estimates_skip_extension_coordinates_and_default_segments(self):
        cases = [
            ("BUCKET-PHY-KIN-1D-MOTION", 70, "R2", ["R2", "R4G", "R4", "R5"]),
            ("BUCKET-PHY-NLM-FIRST-LAW", 100, "R7", ["R7"]),
            ("BUCKET-PHY-GRAV-UNIVERSAL-LAW", 80, "R3W", ["R3W"]),
        ]
        for bucket, percentage, entry, segment in cases:
            with self.subTest(bucket=bucket, percentage=percentage):
                report = resolve_request.plan(self.request(bucket, percentage))
                self.assertTrue(report["passed"], report["findings"])
                self.assertEqual(report["entry"]["rung"], entry)
                self.assertEqual(report["segment"], segment)

    def test_missing_extension_evidence_does_not_gate_required_motion_work(self):
        board = self.matrix("Physics/matrices/phy-kin-1d-motion.rungs.json")
        caps, mics = capability_graph.subject_graph("Physics")
        profile = {"held": {"CAP-KIN-DISTANCE-DISPLACEMENT": "DEMONSTRATED", "CAP-KIN-AVERAGE-RATES": "DEMONSTRATED"}}
        entry = resolve_request.entry_from_profile(board["rungs"], profile, caps, mics)
        self.assertEqual(entry["rung"], "R4G")
        self.assertEqual(entry["capability"], "CAP-KIN-MOTION-GRAPHS")

    def test_missing_gravitation_extensions_do_not_prevent_core_completion(self):
        board = self.matrix("Physics/matrices/phy-grav-universal-law.rungs.json")
        caps, mics = capability_graph.subject_graph("Physics")
        profile = {"held": {
            "CAP-PHY-GRAV-R1": "DEMONSTRATED",
            "CAP-PHY-GRAV-INVERSE-SQUARE": "DEMONSTRATED",
            "CAP-PHY-GRAV-FREE-FALL-G": "DEMONSTRATED",
            "CAP-PHY-GRAV-MASS-WEIGHT": "DEMONSTRATED",
        }}
        entry = resolve_request.entry_from_profile(board["rungs"], profile, caps, mics)
        self.assertIsNone(entry["rung"])
        self.assertEqual(entry["why"], "ABOVE_THE_LADDER")

    def test_explicit_owner_extension_entry_remains_reachable(self):
        request = {
            "request_id": "TEST-GRAV-EXTENSION", "subject": "Physics", "bucket_id": "BUCKET-PHY-GRAV-UNIVERSAL-LAW",
            "cores": ["CORE1A", "CORE1B"],
            "learner": {"owner_entry": {"rung": "R4", "by": "owner", "instruction": "explicit extension demand"}},
        }
        report = resolve_request.plan(request)
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["entry"]["rung"], "R4")
        self.assertEqual(report["segment"], ["R4", "R5"])

    def test_execution_packet_uses_the_same_default_segment_boundary(self):
        ordinary = plan_request.plan(self.author_request("Universal gravitation, free fall and orbital motion", {
            "owner_estimate": {"knowledge_percentage": 80, "by": "owner", "instruction": "routing estimate only"}
        }))
        self.assertEqual(ordinary["learner_route"]["entry"], "R3W")
        self.assertEqual([row["rung"] for row in compile_execution_packet._segment(ordinary)], ["R3W"])
        explicit = plan_request.plan(self.author_request("Universal gravitation, free fall and orbital motion", {
            "owner_entry": {"rung": "R4", "by": "owner", "instruction": "explicit extension demand"}
        }))
        self.assertEqual([row["rung"] for row in compile_execution_packet._segment(explicit)], ["R4", "R5"])

    def test_worksheet_owner_estimate_coordinates_ignore_nondefault_rungs(self):
        positions = study_start._teaching_positions(study_map.subject_index("Physics"))
        expected_absent = {
            "MATRIX-PHY-KIN-1D-MOTION": {"R3", "R6"},
            "MATRIX-PHY-NLM-FIRST-LAW": {"R4"},
            "MATRIX-PHY-GRAV-UNIVERSAL-LAW": {"R4", "R5"},
        }
        for matrix_id, excluded in expected_absent.items():
            with self.subTest(matrix=matrix_id):
                actual = {row["rung"] for row in positions[matrix_id]}
                self.assertFalse(actual & excluded)

    def test_explicit_worksheet_question_demand_can_reach_nondefault_rung(self):
        mapping = json.loads(
            (REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json")
            .read_text(encoding="utf-8")
        )
        report = study_start.resolve(mapping, [{
            "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
            "knowledge_percentage": 75,
        }])
        rows = {row["capability_ref"]: row for row in report["route"]}
        self.assertEqual(
            rows["CAP-KIN-ZERO-V-NONZERO-A"]["learner_action"],
            "START_HERE",
        )
        self.assertEqual(report["start_decisions"][0]["selected_rung"], "R3")

    def test_default_grade9_rungs_do_not_depend_on_nondefault_rungs(self):
        caps, mics = capability_graph.subject_graph("Physics")
        for relative in self.TARGETS:
            board = self.matrix(relative)
            by_rung, _ = capability_graph.ladder_capabilities(board, mics)
            extension_caps = {by_rung[row["rung"]]["capability"] for row in board["rungs"] if row.get("default_entry_eligible", True) is False and row["rung"] in by_rung}
            for row in board["rungs"]:
                if row.get("default_entry_eligible", True) is False:
                    continue
                capability = by_rung[row["rung"]]["capability"]
                closure = set(capability_graph.prerequisite_closure(capability, caps))
                self.assertFalse(closure & extension_caps, f'{capability} depends on non-default Grade-9 extension(s): {sorted(closure & extension_caps)}')


if __name__ == "__main__":
    unittest.main()
