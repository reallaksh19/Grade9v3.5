"""Negative and positive coverage tests using real governed QRT identity/W checks."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import qrt_coverage_report as coverage
from Shared.tools import qrt_pipeline_guard as guard


HEAD = "a" * 40


class QRTPipelineCoverageTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.repo = Path(self.tmp.name)
        self.inputs = sorted(coverage.REQUIRED_INPUTS | {
            "TEST/question.json", "TEST/learner-profile.json",
        })
        for name in self.inputs:
            file = self.repo / name
            file.parent.mkdir(parents=True, exist_ok=True)
            file.write_text('{"evidence":"independent input"}', encoding="utf-8")
        page = self.repo / "TEST/page.html"
        page.write_text('<article data-g9-unit="Q1">Question Q1</article>', encoding="utf-8")
        page_sha = coverage.sha256(page)
        self.run = {
            "schema": "qrt-pipeline-run/v1",
            "run_identity": {"head_sha": HEAD},
            "questions": [{
                "id": "Q1", "slots": {"W": {"protected_move_ref": "W-DECISION"}},
            }],
            "pre_attempt_graphs": [{
                "question_ref": "Q1", "root": "PAGE",
                "nodes": [{"id": "PAGE", "phase": "PRE_ATTEMPT",
                           "move_refs": [], "links": ["SAFE"]},
                          {"id": "SAFE", "phase": "PRE_ATTEMPT",
                           "move_refs": [], "links": []}],
            }],
            "rendered_artifacts": [{
                "id": "CORE2", "path": "TEST/page.html", "sha256": page_sha,
                "head_sha": HEAD, "question_refs": ["Q1"],
            }],
            "review_requirements": {
                "question_anchor_binding_required": True,
                "independent_rendered_review_required": True,
            },
            "reviews": [{
                "question_ref": "Q1", "artifact_ref": "CORE2",
                "artifact_sha256": page_sha, "basis": "INDEPENDENT_RENDERED",
                "reviewer_ref": "reviewer:external-record-1",
                "judgements": {
                    ask: {"verdict": "YES", "evidence": "exact reviewed step"}
                    for ask in guard.ASKS
                },
            }],
        }
        self.run_file = self.repo / "TEST/run.json"
        self._save()
        self.entry = {
            "question_ref": "Q1",
            "run": {"path": "TEST/run.json", "sha256": coverage.sha256(self.run_file)},
            "tracked_inputs": [
                {"path": name, "sha256": coverage.sha256(self.repo / name)}
                for name in self.inputs
            ],
        }
        self.index = {"schema": "qrt-coverage-index/v1", "items": [self.entry]}

    def _save(self):
        self.run_file.write_text(json.dumps(self.run), encoding="utf-8")

    def _snapshot(self):
        # Keep identity and graph validation real; full gate composition is
        # separately exercised by existing governed pipeline hardening tests.
        real_guard = lambda run: (guard.validate_artifacts_and_reviews(run)
                                  + guard.validate_pre_attempt_graphs(run))
        with patch.object(guard, "REPO", self.repo), patch.object(
            coverage.qrt_pipeline_gate, "check", side_effect=real_guard,
        ):
            return coverage.report(copy.deepcopy(self.index), repo=self.repo, head=HEAD)

    def test_valid_12_ask_strict_evidence_is_not_academic_acceptance(self):
        result = self._snapshot()
        self.assertTrue(result["passed_scoped_evidence"])
        self.assertEqual(result["rows"][0]["status"], "REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE")
        self.assertEqual(len(result["rows"][0]["ask_verdicts"]), 12)
        self.assertEqual(result["academic_acceptance"], "NOT_EVALUATED")
        self.assertEqual(result["repository_wide_qrt_acceptance"], "NOT_EVALUATED")

    def test_changed_question_source_invalidates_unchanged_render_and_review(self):
        (self.repo / "TEST/question.json").write_text('{"source":"changed"}', encoding="utf-8")
        row = self._snapshot()["rows"][0]
        self.assertIn("INPUT_DIGEST_STALE", [x["code"] for x in row["findings"]])
        self.assertEqual(row["status"], "REVIEW_REQUIRED_OR_STALE")

    def test_changed_html_even_with_unchanged_review_digest_is_invalid(self):
        (self.repo / "TEST/page.html").write_text(
            '<article data-g9-unit="Q1">New text</article>', encoding="utf-8",
        )
        row = self._snapshot()["rows"][0]
        self.assertTrue(any("RENDERED_ARTIFACT_DIGEST_MISMATCH" in x["detail"]
                            for x in row["findings"]))
        self.assertEqual(row["status"], "REVIEW_REQUIRED_OR_STALE")

    def test_recalculated_wrong_article_hash_is_still_a_false_review(self):
        page = self.repo / "TEST/page.html"
        page.write_text('<article data-g9-unit="Q2">Wrong question</article>', encoding="utf-8")
        sha = coverage.sha256(page)
        self.run["rendered_artifacts"][0]["sha256"] = sha
        self.run["reviews"][0]["artifact_sha256"] = sha
        self._save()
        self.entry["run"]["sha256"] = coverage.sha256(self.run_file)
        row = self._snapshot()["rows"][0]
        self.assertTrue(any("QRT_REVIEW_QUESTION_NOT_RENDERED_IN_ARTIFACT" in x["detail"]
                            for x in row["findings"]))

    def test_transitive_w_reachability_invalidates_review(self):
        self.run["pre_attempt_graphs"][0]["nodes"][1]["move_refs"] = ["W-DECISION"]
        self._save()
        self.entry["run"]["sha256"] = coverage.sha256(self.run_file)
        row = self._snapshot()["rows"][0]
        self.assertTrue(any("W_LEAK_PRE_ATTEMPT_REACHABLE" in x["detail"]
                            for x in row["findings"]))

    def test_required_authority_omission_is_not_forgiven_by_green_guard(self):
        self.entry["tracked_inputs"] = self.entry["tracked_inputs"][:1]
        row = self._snapshot()["rows"][0]
        self.assertIn("CANONICAL_AUTHORITY_INPUT_UNTRACKED",
                      [x["code"] for x in row["findings"]])
        self.assertIn("QUESTION_OR_PROFILE_SOURCE_UNTRACKED",
                      [x["code"] for x in row["findings"]])

    def test_run_head_or_run_content_change_is_detected(self):
        self.run["run_identity"]["head_sha"] = "b" * 40
        self._save()
        self.entry["run"]["sha256"] = coverage.sha256(self.run_file)
        row = self._snapshot()["rows"][0]
        self.assertIn("RUN_HEAD_STALE", [x["code"] for x in row["findings"]])
        self.run["run_identity"]["head_sha"] = HEAD
        self._save()
        row = self._snapshot()["rows"][0]
        self.assertIn("RUN_DIGEST_STALE", [x["code"] for x in row["findings"]])

    def test_independent_review_flag_is_required(self):
        self.run["review_requirements"]["independent_rendered_review_required"] = False
        self._save()
        self.entry["run"]["sha256"] = coverage.sha256(self.run_file)
        row = self._snapshot()["rows"][0]
        self.assertIn("INDEPENDENT_REVIEW_NOT_REQUIRED_BY_RUN",
                      [x["code"] for x in row["findings"]])

    def test_partly_is_an_actionable_rework_not_a_green_acceptance(self):
        self.run["reviews"][0]["judgements"]["H3"] = {
            "verdict": "PARTLY", "evidence": "still vague",
            "fix": "replace pre-attempt hint with a safe question-specific one",
        }
        self._save()
        self.entry["run"]["sha256"] = coverage.sha256(self.run_file)
        row = self._snapshot()["rows"][0]
        self.assertEqual(row["status"], "SEMANTIC_REWORK_REQUIRED")
        self.assertFalse(self._snapshot()["passed_scoped_evidence"])

    def test_empty_and_duplicate_scope_cannot_pass_candidate_gate(self):
        empty = coverage.report({"schema": "qrt-coverage-index/v1", "items": []},
                                repo=self.repo, head=HEAD)
        self.assertTrue(empty["empty_scope"])
        self.assertFalse(empty["passed_scoped_evidence"])
        self.index["items"].append(copy.deepcopy(self.entry))
        result = self._snapshot()
        self.assertIn("CANDIDATE_DUPLICATE", [x["code"] for x in result["findings"]])
        self.assertFalse(result["passed_scoped_evidence"])

    def test_path_escape_rejected_even_if_review_receipt_names_it(self):
        self.entry["run"]["path"] = "../run.json"
        row = self._snapshot()["rows"][0]
        self.assertIn("RUN_PATH_OUTSIDE_REPOSITORY", [x["code"] for x in row["findings"]])


if __name__ == "__main__":
    unittest.main()
