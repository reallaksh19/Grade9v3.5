"""Final contract for common learner scenarios against session-ready skill matrices.

This is deliberately not another runtime. It proves that matrices already declared
SESSION_READY / SESSION_READY_WITH_BRIDGE contain enough durable pedagogical design for
the common feedback loop while keeping learner/session state out of canonical matrices.
"""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import session_readiness  # noqa: E402


READY_STATUSES = {
    session_readiness.READY,
    session_readiness.READY_WITH_BRIDGE,
}
REQUIRED_SUPPORT_LEVELS = {"low", "medium", "high"}
SESSION_ONLY_KEYS = {
    "result",
    "help_used",
    "error_stage",
    "attempt_number",
    "shown_hint_indices",
    "attempted_question_refs",
    "failed_capability_ref",
    "misconception_index",
    "diagnostic_response",
    "diagnosis",
    "diagnostic_basis",
    "diagnostic_evidence",
    "learner_state",
    "knowledge_percentage",
}


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def nested_keys(value):
    if isinstance(value, dict):
        for key, child in value.items():
            yield key
            yield from nested_keys(child)
    elif isinstance(value, list):
        for child in value:
            yield from nested_keys(child)


class HighLikelihoodScenarioMatrixContract(unittest.TestCase):
    def ready_matrices(self):
        rows = []
        for path in sorted(REPO.glob("*/matrices/*.rungs.json")):
            matrix = load(path)
            report = session_readiness.audit_matrix(
                matrix["subject"],
                matrix,
                REPO,
            )
            if report["status"] in READY_STATUSES:
                rows.append((path, matrix, report))
        self.assertTrue(rows, "expected at least one session-ready matrix")
        return rows

    def test_session_ready_matrices_have_common_support_design(self):
        """Ready matrices can author low/medium/high assistance without session data."""
        for path, matrix, report in self.ready_matrices():
            with self.subTest(matrix=matrix["matrix_id"], status=report["status"]):
                family = matrix.get("family")
                self.assertIsInstance(family, dict, path)
                for key in (
                    "invariant_demand",
                    "difficult_move",
                    "independent_check",
                    "support_ladder",
                ):
                    self.assertTrue(family.get(key), f"{path}: missing family.{key}")

                support = family["support_ladder"]
                levels = {row["level"] for row in support}
                self.assertTrue(
                    REQUIRED_SUPPORT_LEVELS.issubset(levels),
                    f"{path}: support ladder needs low/medium/high; got {sorted(levels)}",
                )

                # minimum remains optional. Requiring it would turn an uncommon
                # family-recognition case into mandatory matrix ceremony.
                self.assertLessEqual(levels, {"minimum", *REQUIRED_SUPPORT_LEVELS})

    def test_session_ready_matrices_keep_attempt_history_out(self):
        for path, matrix, _report in self.ready_matrices():
            keys = set(nested_keys(matrix))
            leaked = sorted(SESSION_ONLY_KEYS & keys)
            with self.subTest(matrix=matrix["matrix_id"]):
                self.assertEqual(
                    leaked,
                    [],
                    f"{path}: learner/session keys belong in runtime observations, not matrices",
                )

    def test_session_ready_rungs_reference_canonical_diagnosis_repair_and_verification(self):
        """The matrix points at learner-facing records instead of restating them."""
        for path, matrix, report in self.ready_matrices():
            by_rung = {row["rung"]: row for row in report["rungs"]}
            for rung in matrix["rungs"]:
                detail = by_rung[rung["rung"]]
                with self.subTest(matrix=matrix["matrix_id"], rung=rung["rung"]):
                    self.assertTrue(rung.get("microtopic_ref"), path)
                    self.assertTrue(detail["teaching"], detail)
                    self.assertTrue(detail["diagnostic_repair"], detail)
                    self.assertTrue(detail["verification"], detail)

    def test_optional_minimum_level_is_not_required_for_ready_status(self):
        ready = self.ready_matrices()
        matrices_without_minimum = [
            matrix["matrix_id"]
            for _path, matrix, _report in ready
            if "minimum" not in {
                row["level"]
                for row in matrix["family"]["support_ladder"]
            }
        ]
        self.assertTrue(
            matrices_without_minimum,
            "the contract intentionally permits ready matrices without minimum support",
        )


if __name__ == "__main__":
    unittest.main()
