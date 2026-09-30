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


class FirstStageRouteTests(unittest.TestCase):
    """The first-stage Core follows the owner's choice, then the source state."""

    QUESTIONS = ["Q1. A car goes from 10 m/s to 30 m/s in 8 s. Find its acceleration.",
                 "Q2. A stone is dropped from 80 m. Find the time to fall. Take g = 10 m/s^2."]

    def plan(self, **extra):
        return raw_intake.intake({"subject": "Physics", **extra})

    def test_supplied_questions_start_with_core2_and_its_key_pdf(self):
        plan = self.plan(questions=self.QUESTIONS)
        stage = plan["first_stage"]
        self.assertEqual((stage["basis"], stage["cores"]), ("SUPPLIED_QUESTIONS", ["CORE2"]))
        self.assertEqual(stage["later_cores"], ["CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"])
        self.assertEqual(plan["deliverables"][:4], ["core2_html", "core2_pdf", "core2_key_pdf",
                                                    "core2_question_bank_records"])
        self.assertNotIn("six_cores", plan["deliverables"])

    def test_a_syllabus_alone_starts_with_source_grounded_core1(self):
        plan = self.plan(syllabus=["Distance and displacement", "Constant acceleration"])
        self.assertEqual(plan["first_stage"]["basis"], "NO_QUESTION_BANK")
        self.assertEqual(plan["first_stage"]["cores"], ["CORE1"])
        self.assertNotIn("core2_key_pdf", plan["deliverables"])

    def test_a_requested_core_wins_over_the_source_state(self):
        plan = self.plan(questions=self.QUESTIONS, requested_cores=["core1a"])
        self.assertEqual(plan["requested_cores"], ["CORE1A"])
        self.assertEqual(plan["first_stage"]["basis"], "REQUESTED_CORES")
        self.assertEqual(plan["first_stage"]["cores"], ["CORE1A"])
        self.assertEqual(plan["deliverables"], ["core1a_html", "core1a_pdf", "coverage_view",
                                                "atlas_links", "owner_review_packet"])

    def test_requested_cores_accept_a_comma_separated_string_in_canonical_order(self):
        plan = self.plan(syllabus=["Vectors"], requested_cores="CORE2, core1a")
        self.assertEqual(plan["first_stage"]["cores"], ["CORE1A", "CORE2"])

    def test_core2_without_question_text_is_noted_not_invented(self):
        plan = self.plan(questions=["Q5"], requested_cores=["CORE2"])
        self.assertEqual(plan["status"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(plan["first_stage"]["cores"], ["CORE2"])
        self.assertTrue(any(n.startswith("CORE2_REQUESTED_WITHOUT_QUESTION_TEXT")
                            for n in plan["first_stage"]["notes"]))

    def test_an_unknown_core_is_an_input_error_naming_the_valid_ones(self):
        plan = self.plan(questions=self.QUESTIONS, requested_cores=["CORE9"])
        self.assertEqual(plan["status"], "INVALID_REQUEST")
        self.assertIn("CORE9", plan["errors"][0])
        self.assertIn("CORE1A", plan["errors"][0])

    def test_the_route_does_not_change_the_intake_digest(self):
        with_route = self.plan(questions=self.QUESTIONS, requested_cores=["CORE1A"])
        without = self.plan(questions=self.QUESTIONS)
        self.assertEqual(with_route["intake_digest"], without["intake_digest"])


class EntryAndCliTests(unittest.TestCase):
    def test_cli_intake_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            request = Path(tmp) / "request.json"
            request.write_text(json.dumps(load("chemistry-mole-concept")["request"]), encoding="utf-8")
            intake = subprocess.run(["python3", "Shared/tools/raw_intake.py", "--input", str(request)],
                                    cwd=REPO, stdout=subprocess.PIPE, text=True)
            self.assertEqual(intake.returncode, 0)
            self.assertEqual(json.loads(intake.stdout)["status"], "RESEARCH_AND_AUTHOR")

    def test_a_rejected_request_says_why_on_stderr_even_when_the_json_goes_to_a_file(self):
        """A cold-start run got exit 1 and no output for a request with no subject: the reason was only inside the file."""
        with tempfile.TemporaryDirectory() as tmp:
            request = Path(tmp) / "request.json"
            request.write_text(json.dumps({"grade": "9", "questions": ["1. Find |a| if a = 3i + 4j."]}), encoding="utf-8")
            out = Path(tmp) / "intake.json"
            done = subprocess.run(["python3", "Shared/tools/raw_intake.py", "--input", str(request), "--out", str(out)],
                                  cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            self.assertEqual(done.returncode, 1)
            self.assertEqual(done.stdout, "")
            self.assertIn("INVALID_REQUEST: subject is required", done.stderr)
            self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["status"], "INVALID_REQUEST")

    def test_browser_entry_matches_python_intake(self):
        for command in (["node", "--check", "public/js/raw-intake.js"],
                        ["node", "--test", "tests/raw_intake.test.mjs"]):
            done = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.assertEqual(done.returncode, 0, done.stdout[-3000:])


if __name__ == "__main__":
    unittest.main()
