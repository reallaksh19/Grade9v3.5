"""Delta and transitive-resource regression tests for scoped continuous QRT."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import qrt_change_discovery as delta


BASE = "b" * 40
HEAD = "a" * 40
BANK = "Mathematics/library/bank/questions.v1.json"


def question(qid, stem="Before"):
    return {"id": qid, "stem": stem, "answer": {"summary": "derived"}}


def fixture(questions, *, version=1):
    return {"version": version, "questions": questions}


class QRTChangeDiscoveryTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.repo = Path(temp.name)
        bank = self.repo / BANK
        bank.parent.mkdir(parents=True)
        self.base = json.dumps(fixture([question("Q1")]))
        bank.write_text(self.base, encoding="utf-8")
        self.index = {"schema": "qrt-coverage-index/v1", "items": []}

    def discover(self, paths, old=None):
        return delta.discover(
            self.repo, base=BASE, head=HEAD, paths=paths,
            before=lambda path: (old or {}).get(path, self.base if path == BANK else ""),
            index=self.index,
        )

    def _indexed(self, qid="Q1", source=BANK):
        row = {
            "question_ref": qid, "question_source_path": source,
            "run": {"path": "Mathematics/library/run.json", "sha256": "sha256:" + "1" * 64},
            "tracked_inputs": [{"path": source, "sha256": "sha256:" + "2" * 64}],
        }
        self.index["items"].append(row)
        return row

    def test_unrelated_document_change_does_not_claim_global_qrt_approval(self):
        report = self.discover(["docs/README.md"])
        self.assertTrue(report["pass_changed_scope"])
        self.assertTrue(report["no_relevant_changes"])
        self.assertEqual(report["repository_wide_qrt_acceptance"], "NOT_EVALUATED")

    def test_new_question_requires_individual_index_entry(self):
        (self.repo / BANK).write_text(
            json.dumps(fixture([question("Q1"), question("Q2")])), encoding="utf-8",
        )
        report = self.discover([BANK])
        self.assertEqual([x["question_ref"] for x in report["impacts"]], ["Q2"])
        self.assertIn("CHANGED_QUESTION_REVIEW_REQUIRED",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_question_changed_while_file_name_stable_is_found(self):
        (self.repo / BANK).write_text(
            json.dumps(fixture([question("Q1", "New question")])), encoding="utf-8",
        )
        report = self.discover([BANK])
        self.assertEqual(report["impacts"][0]["reason"], "QUESTION_MODIFIED")
        self.assertFalse(report["pass_changed_scope"])

    def test_changed_bank_custody_envelope_impacts_every_member(self):
        before = json.dumps(fixture([question("Q1"), question("Q2")]))
        (self.repo / BANK).write_text(
            json.dumps(fixture([question("Q1"), question("Q2")], version=2)),
            encoding="utf-8",
        )
        report = self.discover([BANK], old={BANK: before})
        self.assertEqual({x["question_ref"] for x in report["impacts"]},
                         {"Q1", "Q2"})
        self.assertTrue(all(x["reason"] == "BANK_ENVELOPE_CHANGED"
                            for x in report["impacts"]))

    def test_deleted_question_does_not_receive_fictitious_green_approval(self):
        (self.repo / BANK).write_text(json.dumps(fixture([])), encoding="utf-8")
        report = self.discover([BANK])
        self.assertIn("QUESTION_REMOVAL_REQUIRES_LINEAGE_REVIEW",
                      [x["code"] for x in report["findings"]])

    def test_authored_original_practice_records_are_included(self):
        path = "TEST/imo-research/original-practice/seven-cell.json"
        new = {"schema": "authored", "records": [{
            "id": "IMO-1", "source_question": {"stem": "How many?"}
        }]}
        f = self.repo / path
        f.parent.mkdir(parents=True)
        f.write_text(json.dumps(new), encoding="utf-8")
        report = self.discover([path])
        self.assertEqual(report["impacts"][0]["question_ref"], "IMO-1")
        self.assertFalse(report["pass_changed_scope"])

    def test_malformed_changed_source_fails_closed(self):
        (self.repo / BANK).write_text('{"questions": [', encoding="utf-8")
        report = self.discover([BANK])
        self.assertIn("CHANGED_SOURCE_JSON_INVALID",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_global_renderer_change_with_empty_scope_is_not_silent(self):
        report = self.discover(["Shared/tools/render_core.py"])
        self.assertIn("GLOBAL_CHANGE_WITHOUT_INDEXED_QRT_SCOPE",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_published_page_change_without_bound_review_fails(self):
        p = "Physics/content/relative-motion-g9/publication/CORE2B.html"
        report = self.discover([p])
        self.assertIn("PUBLISHED_SURFACE_WITHOUT_QRT_BINDING",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_reachable_html_css_svg_dependency_invalidation(self):
        root = self.repo / "TEST/content/page.html"
        root.parent.mkdir(parents=True)
        root.write_text(
            '<article data-g9-unit="Q1"><a href="./help.html">help</a>'
            '<link rel="stylesheet" href="assets/style.css"></article>', encoding="utf-8",
        )
        help_file = root.parent / "help.html"
        help_file.write_text('<img src="assets/diagram.svg">', encoding="utf-8")
        css = root.parent / "assets/style.css"
        css.parent.mkdir(parents=True)
        css.write_text('article {background: url("./bg.png")}', encoding="utf-8")
        (css.parent / "bg.png").write_bytes(b"png")
        (css.parent / "diagram.svg").write_text('<svg/>', encoding="utf-8")
        deps, problems = delta.linked_dependencies(self.repo, "TEST/content/page.html")
        self.assertEqual(problems, [])
        self.assertEqual(deps, {
            "TEST/content/page.html", "TEST/content/help.html",
            "TEST/content/assets/style.css",
            "TEST/content/assets/bg.png", "TEST/content/assets/diagram.svg",
        })

    def test_changed_reachable_resource_needs_tracked_dependency_digest(self):
        path = "TEST/content/page.html"
        page = self.repo / path
        page.parent.mkdir(parents=True)
        page.write_text('<article data-g9-unit="Q1"><img src="figure.svg"></article>',
                        encoding="utf-8")
        fig = page.parent / "figure.svg"
        fig.write_text("<svg/>", encoding="utf-8")
        row = self._indexed()
        run = self.repo / row["run"]["path"]
        run.parent.mkdir(parents=True, exist_ok=True)
        run.write_text(json.dumps({"rendered_artifacts": [
            {"id": "PAGE", "path": path},
        ]}), encoding="utf-8")
        rendered = {"question_ref": "Q1", "status": "REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE"}
        with patch.object(delta.coverage, "candidate", return_value=rendered):
            report = self.discover(["TEST/content/figure.svg"])
        self.assertIn("CHANGED_REACHABLE_RESOURCE_NOT_PINNED",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_changed_question_cannot_pass_using_a_different_source_path(self):
        (self.repo / BANK).write_text(
            json.dumps(fixture([question("Q1", "different")])), encoding="utf-8",
        )
        self._indexed(source="Mathematics/library/other.json")
        with patch.object(delta.coverage, "candidate") as fake:
            report = self.discover([BANK])
        self.assertIn("INDEXED_SOURCE_IDENTITY_MISMATCH",
                      [x["code"] for x in report["findings"]])
        fake.assert_not_called()

    def test_untracked_learner_figure_change_without_index_fails_closed(self):
        path = "TEST/library/figures/diagram.svg"
        report = self.discover([path])
        self.assertIn("PUBLISHED_SURFACE_WITHOUT_QRT_BINDING",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_shared_interactive_runtime_change_without_scope_is_hold(self):
        report = self.discover(["Shared/web/explorer-runtime.js"])
        self.assertIn("GLOBAL_CHANGE_WITHOUT_INDEXED_QRT_SCOPE",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_question_list_with_unrecognized_shape_is_not_an_empty_success(self):
        path = "TEST/question-bank/unknown-format.json"
        new = {"questions": [{"ref": "Q1", "problem_text": "Unsupported schema"}]}
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(new), encoding="utf-8")
        report = self.discover([path])
        self.assertIn("QUESTION_COLLECTION_FORMAT_UNRECOGNIZED",
                      [x["code"] for x in report["findings"]])
        self.assertFalse(report["pass_changed_scope"])

    def test_nested_topic_question_records_are_discovered(self):
        path = "Physics/research/packages/topic.package.json"
        data = {"topics": [{"microtopics": [{
            "questions": [question("PHY-DEEP-1")]
        }]}]}
        file = self.repo / path
        file.parent.mkdir(parents=True, exist_ok=True)
        file.write_text(json.dumps(data), encoding="utf-8")
        report = self.discover([path])
        self.assertEqual(report["impacts"][0]["question_ref"], "PHY-DEEP-1")
        self.assertFalse(report["pass_changed_scope"])

    def test_static_resource_graph_path_escape_is_rejected(self):
        path = self.repo / "TEST/content/page.html"
        path.parent.mkdir(parents=True)
        path.write_text('<img src="../../../../../outside.svg">', encoding="utf-8")
        deps, errors = delta.linked_dependencies(self.repo, "TEST/content/page.html")
        self.assertFalse(errors)
        self.assertEqual(deps, {"TEST/content/page.html"})


if __name__ == "__main__":
    unittest.main()
