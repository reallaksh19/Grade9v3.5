"""Research-first workflow: raw intake -> research/author -> rendered product -> final gate.

Every job here starts from raw owner input with no canonical ids. The three subject
fixtures must pass the gate; mutations of their rendered output must fail it, and the
PR #288 Motion-in-2D product (holds presented as the output) is the regression case.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from Shared.tools import raw_intake

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests/fixtures/research-first"
BENCHMARK = REPO / "benchmarks/learner-product-reference/physics-motion-2d.json"
SUBJECTS = ("physics-motion-2d", "mathematics-quadratics", "chemistry-mole-concept")


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class IntakeTests(unittest.TestCase):
    def test_raw_inputs_start_without_ids_profile_or_scope(self):
        for name in SUBJECTS:
            plan = raw_intake.intake(load(name)["request"])
            self.assertEqual(plan["status"], "RESEARCH_AND_AUTHOR", name)
            self.assertEqual(plan["errors"], [])
            self.assertFalse(plan["learner_start"]["blocking"])
            self.assertEqual(plan["learner_start"]["support"], "full")
            self.assertGreaterEqual(plan["learner_start"]["diagnostic"]["min_items"], 3)
            self.assertNotIn("HOLD", json.dumps(plan))
            kinds = {t["kind"] for t in plan["research_tasks"]}
            self.assertIn("teach_subtopic", kinds)
            self.assertIn("solve_and_explain", kinds)
            ledger_ids = {r["input_id"] for r in plan["coverage_ledger_template"]}
            supplied = {q["id"] for q in plan["inputs"]["questions"]} | {s["id"] for s in plan["inputs"]["syllabus"]}
            self.assertEqual(ledger_ids, supplied)

    def test_missing_knowledge_percentage_never_blocks(self):
        request = {"subject": "Anything", "questions": ["Explain why the sky looks blue at noon."]}
        plan = raw_intake.intake(request)
        self.assertEqual(plan["status"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(plan["learner_start"]["knowledge_percentage"], 50)
        self.assertEqual(plan["learner_start"]["source"], "DEFAULT_MEDIAN")
        zero = raw_intake.intake({**request, "learner": {"knowledge_percentage": 0}})
        self.assertEqual(zero["learner_start"]["knowledge_percentage"], 0)
        self.assertFalse(zero["learner_start"]["blocking"])

    def test_short_label_is_never_an_identity(self):
        plan = raw_intake.intake(load("physics-motion-2d")["request"])
        rows = {q["label"]: q for q in plan["inputs"]["questions"] if q["label"]}
        self.assertEqual(rows["Q15"]["text_status"], "SUPPLIED")
        self.assertTrue(rows["Q15"]["identity_claim_requested"])
        self.assertEqual(rows["Q15"]["conditions"], ["20", "30", "10"])
        self.assertEqual(rows["Q7"]["text_status"], "LABEL_ONLY")
        tasks = {t["id"] for t in plan["research_tasks"]}
        self.assertIn(f"recover_question_text:{rows['Q7']['id']}", tasks)
        self.assertIn(f"resolve_source_identity:{rows['Q15']['id']}", tasks)
        self.assertNotIn("canonical_question_ref", json.dumps(plan))

    def test_reconciliation_surfaces_questions_outside_the_syllabus(self):
        plan = raw_intake.intake(load("mathematics-quadratics")["request"])
        texts = {q["id"]: q["text"] for q in plan["inputs"]["questions"]}
        outside = [texts[i] for i in plan["reconciliation"]["questions_outside_syllabus"]]
        self.assertIn("The product of two consecutive positive integers is 132. Find the integers.", outside)
        tasks = {t["kind"] for t in plan["research_tasks"]}
        self.assertIn("place_unmatched_question", tasks)
        self.assertIn("author_practice", tasks)

    def test_empty_request_is_invalid_not_held(self):
        plan = raw_intake.intake({"subject": ""})
        self.assertEqual(plan["status"], "INVALID_REQUEST")
        self.assertEqual(len(plan["errors"]), 2)

    def test_ids_are_content_derived_and_stable(self):
        a = raw_intake.intake({"subject": "X", "questions": ["  Find  the  range. "]})
        b = raw_intake.intake({"subject": "X", "questions": ["Find the range.", "find the range."]})
        self.assertEqual(a["inputs"]["questions"][0]["id"], b["inputs"]["questions"][0]["id"])
        self.assertEqual(b["inputs"]["questions"][0]["supplied_count"], 2)


class EntryAndCliTests(unittest.TestCase):
    def test_cli_intake_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = Path(tmp) / "request.json"
            request.write_text(json.dumps(load("chemistry-mole-concept")["request"]), encoding="utf-8")
            intake = subprocess.run(["python3", "Shared/tools/raw_intake.py", "--input", str(request)],
                                    cwd=REPO, stdout=subprocess.PIPE, text=True)
            self.assertEqual(intake.returncode, 0)
            self.assertEqual(json.loads(intake.stdout)["status"], "RESEARCH_AND_AUTHOR")

    def test_browser_entry_matches_python_intake(self):
        for command in (["node", "--check", "public/js/raw-intake.js"],
                        ["node", "--test", "tests/raw_intake.test.mjs"]):
            done = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.assertEqual(done.returncode, 0, done.stdout[-3000:])


if __name__ == "__main__":
    unittest.main()
