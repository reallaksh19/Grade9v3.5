from __future__ import annotations

import subprocess
import unittest
from pathlib import Path

from Shared.tools import build_question_bank_web

ROOT = Path(__file__).resolve().parents[1]


# Friction denominator regression is intentionally part of the canonical browser count.
class QuestionBankWebTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = build_question_bank_web.build(ROOT)

    def test_canonical_counts_and_topics(self):
        self.assertEqual(self.data["counts"]["questions"], 310)
        self.assertEqual(self.data["counts"]["subjects"], {"Chemistry": 126, "Mathematics": 18, "Physics": 166})
        self.assertEqual(len(self.data["counts"]["topics"]), 11)

    def test_selected_d3d4_view_is_exact_and_canonical(self):
        view = next(v for v in self.data["views"] if v["id"] == "selected-d3d4-non-jee-advanced")
        self.assertEqual(len(view["resolved_question_refs"]), 7)
        by_id = {q["id"]: q for q in self.data["questions"]}
        selected = [by_id[x] for x in view["resolved_question_refs"]]
        self.assertTrue(all(q["subject"] == "Physics" for q in selected))
        self.assertTrue(all(q["difficulty"]["band"] in {"D3", "D4"} for q in selected))
        self.assertTrue(all(q["exam"] in {"IIT-JEE", "JEE Main"} for q in selected))
        self.assertFalse(any(q["exam"] == "JEE (Advanced)" for q in selected))

    def test_source_hints_are_not_authored_scaffolds(self):
        for question in self.data["questions"]:
            self.assertEqual(question["source_hints"], [])
            self.assertGreaterEqual(len(question["scaffolds"]), 2)

    def test_browser_projection_is_current(self):
        intended = build_question_bank_web.render(self.data)
        self.assertEqual((ROOT / "public/data/question-bank-data.js").read_text(encoding="utf-8"), intended)

    def test_browser_runtimes_parse_and_do_not_use_inner_html(self):
        for rel in ("public/js/question-bank.js", "public/js/question-bank-data-service.js", "public/js/site-header.js"):
            path = ROOT / rel
            result = subprocess.run(["node", "--check", str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, msg=result.stderr)
            self.assertNotIn("innerHTML", path.read_text(encoding="utf-8"))

    def test_question_bank_page_has_shared_shell_and_starts_from_the_manifest(self):
        text = (ROOT / "public/question-bank/index.html").read_text(encoding="utf-8")
        self.assertIn("../data/question-bank-manifest.js", text)
        self.assertIn("../js/question-bank-data-service.js", text)
        self.assertIn("../js/site-header.js", text)
        self.assertIn("Question browser", text)
        # Progressive loading: the page starts from the manifest and never ships the monolith or a
        # question list of its own; everything else is named by the manifest and loaded in order.
        self.assertNotIn("../data/question-bank-data.js", text)
        for artifact in ("catalog", "questions", "search", "resources", "details"):
            self.assertNotIn(f"question-bank-{artifact}", text, "the manifest, not the page, names artifacts")

    def test_question_bank_page_has_a_modal_study_dialog(self):
        html = (ROOT / "public/question-bank/index.html").read_text(encoding="utf-8")
        for marker in ('id="qbStudyDialog"', 'class="qb-study-dialog"', 'id="qbDialogClose"', 'id="qbSubjectTabs"',
                       'id="qbTopicStrip"', 'id="qbTopicBanner"', 'id="qbStatus"'):
            self.assertIn(marker, html)
        js = (ROOT / "public/js/question-bank.js").read_text(encoding="utf-8")
        for name in ("openStudyModal", "closeStudyModal", "showModal"):
            self.assertIn(name, js)

    def test_the_runtime_names_no_subject_topic_or_resource_from_the_corpus(self):
        """Adding a subject must never need a branch in the runtime (#359 falsifier, derived from the corpus)."""
        text = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in (
            "public/js/question-bank.js", "public/js/question-bank-data-service.js", "public/css/question-bank.css"))
        lowered = text.casefold()
        names = {str(q["subject"]) for q in self.data["questions"]} | {str(q["topic"]) for q in self.data["questions"]}
        names |= {"Mathematics", "Physics", "Chemistry", "Biology"}
        found = sorted(name for name in names if name.casefold() in lowered)
        self.assertEqual(found, [], "the runtime and its stylesheet must learn subjects from the generated catalog")
        for destination in self.data["destinations"]:
            self.assertNotIn(destination["path"], text)
        self.assertNotIn("data-subject=", text, "no per-subject styling hooks")

    def test_destinations_include_governed_master_suites(self):
        destinations = self.data["destinations"]
        paths = {d["path"] for d in destinations}
        expected_chemistry_suites = [
            "chemistry/bonding/explorers/chemical_bonding/index.html",
            "chemistry/some-basic-concepts/explorers/mole_concept/index.html",
            "chemistry/redox/explorers/redox_reactions/index.html",
            "chemistry/gases/explorers/behaviour_of_gases/index.html",
            "chemistry/redox/explorers/redox_reactions/adaptive-hard-concept-proof.html",
        ]
        for expected in expected_chemistry_suites:
            self.assertIn(expected, paths, f"missing expected suite destination {expected}")
            self.assertTrue((ROOT / "public" / expected).is_file(), f"destination target missing: {expected}")
        for d in destinations:
            self.assertTrue(
                (ROOT / "public" / d["path"]).is_file() or (ROOT / d["path"]).is_file(),
                f"destination file does not exist on disk: {d['path']}",
            )


if __name__ == "__main__":
    unittest.main()
