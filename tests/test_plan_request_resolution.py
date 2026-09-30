"""A person's words reach a matrix, or the planner lists candidates; it never guesses silently."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import plan_request  # noqa: E402

ONE_D = "BUCKET-PHY-KIN-1D-MOTION"


def resolve(subtopic: str = "", **extra):
    return plan_request.resolve_board({"subject": "Physics", "subtopic": subtopic, **extra})


class SubtopicResolution(unittest.TestCase):
    def test_the_exact_matrix_title_still_resolves_without_a_disclosure(self):
        board, findings = resolve("One-dimensional motion")
        self.assertEqual(findings, [])
        self.assertEqual(board["bucket_id"], ONE_D)
        self.assertNotIn("_resolved_by", board)

    def test_words_that_identify_one_matrix_reach_it_and_say_so(self):
        board, findings = resolve("Motion in 1D")
        self.assertEqual(findings, [])
        self.assertEqual(board["bucket_id"], ONE_D)
        self.assertEqual(board["_resolved_by"]["basis"], "TOKEN_MATCH")
        self.assertEqual(board["_resolved_by"]["requested"], "Motion in 1D")

    def test_words_that_fit_several_matrices_list_them_and_choose_none(self):
        board, findings = resolve("motion")
        self.assertIsNone(board)
        self.assertEqual(findings[0]["point"], "AUTHORING_REQUEST_SUBTOPIC_AMBIGUOUS")
        candidates = {c["bucket_id"] for c in findings[0]["candidates"]}
        self.assertIn(ONE_D, candidates)
        self.assertGreater(len(candidates), 1)

    def test_a_request_no_matrix_answers_lists_the_nearest_without_picking(self):
        board, findings = resolve("Motion in 3D")
        self.assertIsNone(board)
        self.assertEqual(findings[0]["point"], "AUTHORING_REQUEST_SUBTOPIC_UNRESOLVED")
        self.assertTrue(findings[0]["candidates"])

    def test_an_explicit_bucket_id_is_never_reinterpreted(self):
        board, findings = resolve("something unrelated", bucket_id=ONE_D)
        self.assertEqual(findings, [])
        self.assertEqual(board["bucket_id"], ONE_D)
        self.assertNotIn("_resolved_by", board)

    def test_dimension_words_and_spacing_normalise_to_one_token(self):
        self.assertEqual(plan_request._tokens("Motion in 2 D"), {"motion", "2d"})
        self.assertEqual(plan_request._tokens("Two-dimensional motion"), {"2d", "motion"})
        self.assertEqual(plan_request._tokens("One dimension"), {"1d"})

    def test_a_word_match_becomes_a_visible_agent_duty_in_the_plan(self):
        report = plan_request.plan({
            "request_id": "T-MOTION-1D", "subject": "Physics", "subtopic": "Motion in 1D",
            "requested_cores": ["CORE1A"],
            "learner": {"owner_entry": {"rung": "R1", "by": "owner", "instruction": "start at R1"}}})
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["bucket"], ONE_D)
        self.assertEqual([r["basis"] for r in report["resolutions"]], ["TOKEN_MATCH"])
        self.assertIn("CONFIRM_SUBTOPIC_RESOLUTION", [a["id"] for a in report["agent_actions"]])

    def test_an_unresolved_request_returns_no_plan_but_keeps_the_report_shape(self):
        report = plan_request.plan({"request_id": "T-NONE", "subject": "Physics",
                                    "subtopic": "Astrology", "requested_cores": ["CORE2"]})
        self.assertFalse(report["passed"])
        self.assertEqual(report["resolutions"], [])
        self.assertEqual(report["products"], [])


if __name__ == "__main__":
    unittest.main()
