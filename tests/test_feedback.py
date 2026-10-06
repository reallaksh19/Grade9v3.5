"""Feedback runtime gives the smallest useful help and never guesses learner state."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import feedback  # noqa: E402


def confirmed_diagnostic_evidence(subject, capability_ref, observed_response, basis, *, root=REPO, index=0):
    records = feedback.subject_records(subject, root)
    evidence, error = feedback.diagnostic_evidence_for(
        records,
        capability_ref,
        index,
        observed_response,
        "CONFIRMED",
        basis,
    )
    if error:
        raise AssertionError(error)
    return evidence


class FeedbackRuntime(unittest.TestCase):
    SUBJECT = "Mathematics"
    QUESTION = "Q-MATH-LINEAR-01"

    def request(self, **overrides):
        request = {
            "subject": self.SUBJECT,
            "question_ref": self.QUESTION,
            "attempt_number": 1,
            "shown_hint_indices": [],
            "attempted_question_refs": [self.QUESTION],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": "SESSION-1",
            "response_summary": "Could not isolate x.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-MATH-ISOLATE",
                "error_stage": "SETUP",
            },
        }
        for key, value in overrides.items():
            if key == "evaluation":
                request["evaluation"].update(value)
            else:
                request[key] = value
        return request

    def test_first_wrong_attempt_gets_directional_hint_not_answer(self):
        report = feedback.run(self.request())
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["next_action"], "RETRY")
        self.assertEqual(report["hint"]["index"], 0)
        self.assertEqual(report["hint"]["reveals"], "CONCEPT")
        self.assertNotIn("7/3", report["hint"]["text"])

    def test_second_wrong_attempt_escalates_to_method_hint(self):
        report = feedback.run(self.request(
            attempt_number=2,
            shown_hint_indices=[0],
            help_used="HINT",
        ))
        self.assertEqual(report["next_action"], "RETRY")
        self.assertEqual(report["hint"]["index"], 1)
        self.assertEqual(report["hint"]["reveals"], "METHOD")

    def test_answer_hint_is_never_emitted_by_retry_runtime(self):
        report = feedback.run(self.request(
            attempt_number=2,
            shown_hint_indices=[0, 1],
            help_used="HINT",
            evaluation={"diagnostic_evidence": confirmed_diagnostic_evidence(
                self.SUBJECT,
                "CAP-MATH-ISOLATE",
                "I would change only one side of the equation.",
                "The canonical probe response repeats the one-sided-operation misconception.",
            )},
        ))
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertNotIn("hint", report)
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")

    def test_repair_is_followed_by_a_fresh_verification_task(self):
        report = feedback.run(self.request(
            attempt_number=3,
            shown_hint_indices=[0, 1],
            help_used="HINT",
            evaluation={"diagnostic_evidence": confirmed_diagnostic_evidence(
                self.SUBJECT,
                "CAP-MATH-ISOLATE",
                "I would change only one side of the equation.",
                "The canonical probe response repeats the one-sided-operation misconception.",
            )},
        ))
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["microtopic_ref"], "MIC-MATH-EQUIVALENT-OPS")
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        verification = report["after_repair"]["verification"]
        # A fresh same-capability question is preferred: the transfer task added in the
        # Phase 6 pilot. Core1A worked anchors never qualify (their solution is shown).
        self.assertEqual(verification["kind"], "QUESTION")
        self.assertEqual(verification["question_ref"], "Q-MATH-LINEAR-2B-01")
        self.assertNotIn("answer", verification)

    def test_exit_task_verifies_when_no_fresh_question_remains(self):
        report = feedback.run(self.request(
            attempt_number=3,
            shown_hint_indices=[0, 1],
            help_used="HINT",
            attempted_question_refs=[self.QUESTION, "Q-MATH-LINEAR-2B-01"],
            evaluation={"diagnostic_evidence": confirmed_diagnostic_evidence(
                self.SUBJECT,
                "CAP-MATH-ISOLATE",
                "I would change only one side of the equation.",
                "The canonical probe response repeats the one-sided-operation misconception.",
            )},
        ))
        verification = report["after_repair"]["verification"]
        self.assertEqual(verification["kind"], "EXIT_TASK")
        self.assertNotIn("answer", verification)

    def test_correct_after_hint_is_uncertain_until_fresh_verification(self):
        report = feedback.run(self.request(
            shown_hint_indices=[0],
            help_used="HINT",
            response_summary="Solved after one hint.",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        ))
        self.assertEqual(report["next_action"], "VERIFY")
        self.assertEqual(report["observation_draft"]["result"], "UNCERTAIN")
        self.assertEqual(report["observation_draft"]["help"], "HINT")
        self.assertEqual(report["review"]["outcome"], "CORRECT_WITH_HINT")
        self.assertEqual(report["review"]["next_review"], "2026-09-21")
        self.assertIsNotNone(report["verification"])

    def test_independent_correct_attempt_can_continue(self):
        report = feedback.run(self.request(
            response_summary="Solved independently.",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        ))
        self.assertEqual(report["next_action"], "CONTINUE")
        self.assertEqual(report["observation_draft"]["result"], "DEMONSTRATED")
        self.assertEqual(report["observation_draft"]["capability_ref"], "CAP-MATH-ISOLATE")
        self.assertEqual(report["review"]["outcome"], "CORRECT_INDEPENDENT")
        self.assertEqual(report["review"]["next_review"], "2026-09-25")

    def test_multi_capability_failure_without_attribution_is_diagnosed_not_guessed(self):
        report = feedback.run(self.request(
            evaluation={
                "result": "INCORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        ))
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertIsNone(report["failed_capability_ref"])
        self.assertIsNone(report["observation_draft"])
        capabilities = {row["capability_ref"] for row in report["diagnostic_options"]}
        self.assertIn("CAP-MATH-ISOLATE", capabilities)
        self.assertIn("CAP-MATH-EXACTNESS", capabilities)

    def test_invalid_failed_capability_is_not_written_into_learner_evidence(self):
        report = feedback.run(self.request(
            evaluation={"failed_capability_ref": "CAP-NOT-IN-QUESTION"},
        ))
        self.assertFalse(report["passed"])
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertIsNone(report["observation_draft"])
        self.assertIn(
            "FEEDBACK_FAILED_CAPABILITY_NOT_REQUIRED",
            [row["point"] for row in report["findings"]],
        )

    def test_explicit_prerequisite_failure_is_valid_attribution(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "Example/library"
            library.mkdir(parents=True)
            (library / "example.v1.json").write_text(json.dumps({
                "package_id": "PKG-EXAMPLE",
                "capabilities": [
                    {"id": "CAP-BASE", "prerequisite_refs": []},
                    {"id": "CAP-TARGET", "prerequisite_refs": ["CAP-BASE"]},
                ],
                "microtopics": [
                    {
                        "id": "MIC-BASE",
                        "primary_capability_ref": "CAP-BASE",
                        "title": "Base capability",
                        "misconceptions": [{
                            "wrong_idea": "Base idea is missing.",
                            "diagnostic_prompt": "Can you show the base move?",
                            "repair": "Rebuild the base move first.",
                        }],
                        "teaching_path": [{
                            "id": "STEP-BASE",
                            "action": "Rebuild the base move.",
                            "why_valid": "The target depends on it.",
                        }],
                    },
                    {
                        "id": "MIC-TARGET",
                        "primary_capability_ref": "CAP-TARGET",
                        "title": "Target capability",
                        "misconceptions": [],
                        "teaching_path": [],
                    },
                ],
                "questions": [{
                    "id": "Q-TARGET",
                    "primary_capability_ref": "CAP-TARGET",
                    "secondary_capability_refs": [],
                    "stem": "Use the target capability.",
                    "hints": [],
                    "answer": {"kind": "MODEL_RESPONSE"},
                }],
            }), encoding="utf-8")
            report = feedback.run({
                "subject": "Example",
                "question_ref": "Q-TARGET",
                "attempt_number": 1,
                "shown_hint_indices": [],
                "attempted_question_refs": ["Q-TARGET"],
                "help_used": "NONE",
                "when": "2026-09-18",
                "response_summary": "Work explicitly fails at the prerequisite move.",
                "evaluation": {
                    "result": "INCORRECT",
                    "failed_capability_ref": "CAP-BASE",
                    "error_stage": "CONCEPT",
                },
            }, root)
            self.assertTrue(report["passed"], report["findings"])
            self.assertEqual(report["failed_capability_ref"], "CAP-BASE")
            self.assertEqual(report["observation_draft"]["capability_ref"], "CAP-BASE")
            self.assertEqual(report["observation_draft"]["result"], "MISSING")
            self.assertEqual(report["next_action"], "REPAIR")
            self.assertEqual(report["repair"]["microtopic_ref"], "MIC-BASE")

    def test_unknown_question_stops_cleanly(self):
        request = self.request()
        request["question_ref"] = "Q-NOT-REAL"
        report = feedback.run(request)
        self.assertFalse(report["passed"])
        self.assertEqual(report["next_action"], "STOP")
        self.assertEqual(report["findings"][0]["point"], "FEEDBACK_QUESTION_UNKNOWN")

    def test_pre_attempt_transfer_support_is_concept_only_for_every_dimension(self):
        for dimension in ("model_choice", "representation_translation", "reasoning_steps", "novelty"):
            with self.subTest(dimension=dimension):
                question = {
                    "hints": [
                        {"text": "Inspect the invariant first.", "reveals": "CONCEPT"},
                        {"text": "Use this method now.", "reveals": "METHOD"},
                        {"text": "The answer is supplied.", "reveals": "ANSWER"},
                    ],
                    "transfer": {
                        "dimension": dimension,
                        "statement": "The learner must make the changed decision.",
                        "builds_on": ["Q-PRIOR"],
                    },
                }
                first = feedback.pre_attempt_safe_hint(question, [])
                self.assertEqual(first["reveals"], "CONCEPT")
                self.assertIsNone(feedback.pre_attempt_safe_hint(question, [0]))

    def test_post_attempt_non_model_choice_transfer_can_escalate_to_method(self):
        question = {
            "hints": [
                {"text": "Inspect the representation.", "reveals": "CONCEPT"},
                {"text": "Translate the axes before calculating.", "reveals": "METHOD"},
            ],
            "transfer": {
                "dimension": "representation_translation",
                "statement": "The learner must choose the representation.",
                "builds_on": ["Q-PRIOR"],
            },
        }
        hint = feedback.next_safe_hint(question, [0])
        self.assertEqual(hint["reveals"], "METHOD")

    def test_model_choice_transfer_never_receives_a_method_hint(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "Example/library"
            library.mkdir(parents=True)
            (library / "example.v1.json").write_text(json.dumps({
                "package_id": "PKG-EXAMPLE",
                "capabilities": [{
                    "id": "CAP-CHOICE",
                    "prerequisite_refs": [],
                }],
                "microtopics": [{
                    "id": "MIC-CHOICE",
                    "primary_capability_ref": "CAP-CHOICE",
                    "title": "Choose a model",
                    "misconceptions": [{
                        "wrong_idea": "Pick from surface words.",
                        "diagnostic_prompt": "What relation is actually constrained?",
                        "repair": "Name the invariant before selecting a model.",
                    }],
                    "teaching_path": [{
                        "id": "STEP-CHOICE",
                        "action": "Name the invariant.",
                        "why_valid": "It selects the model from structure.",
                    }],
                }],
                "questions": [{
                    "id": "Q-TRANSFER",
                    "primary_capability_ref": "CAP-CHOICE",
                    "secondary_capability_refs": [],
                    "stem": "Choose and apply the model.",
                    "hints": [
                        {"text": "What remains invariant?", "reveals": "CONCEPT"},
                        {"text": "Use model X.", "reveals": "METHOD"},
                        {"text": "The answer is Y.", "reveals": "ANSWER"},
                    ],
                    "transfer": {
                        "dimension": "model_choice",
                        "statement": "The learner must choose the model.",
                        "builds_on": ["MIC-CHOICE"],
                    },
                    "answer": {"kind": "MODEL_RESPONSE"},
                }],
            }), encoding="utf-8")

            request = {
                "subject": "Example",
                "question_ref": "Q-TRANSFER",
                "attempt_number": 2,
                "shown_hint_indices": [0],
                "attempted_question_refs": ["Q-TRANSFER"],
                "help_used": "HINT",
                "when": "2026-09-18",
                "response_summary": "Still chose the wrong model.",
                "evaluation": {
                    "result": "INCORRECT",
                    "failed_capability_ref": "CAP-CHOICE",
                    "error_stage": "CONCEPT",
                    "diagnostic_evidence": confirmed_diagnostic_evidence(
                        "Example",
                        "CAP-CHOICE",
                        "I chose the model without checking the invariant relation.",
                        "The response to the canonical probe repeats the wrong structural rule.",
                        root=root,
                    ),
                },
            }
            report = feedback.run(request, root)
            self.assertEqual(report["next_action"], "REPAIR")
            self.assertNotIn("hint", report)
            self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")

    def test_explicit_repair_ref_resolves_to_specific_teaching_step(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            library = root / "Example/library"
            library.mkdir(parents=True)
            (library / "example.v1.json").write_text(json.dumps({
                "package_id": "PKG-EXAMPLE",
                "capabilities": [{"id": "CAP-X", "prerequisite_refs": []}],
                "microtopics": [{
                    "id": "MIC-X",
                    "primary_capability_ref": "CAP-X",
                    "title": "X",
                    "misconceptions": [],
                    "teaching_path": [{
                        "id": "STEP-X",
                        "action": "Rebuild the setup.",
                        "why_valid": "The setup determines the relation.",
                    }],
                }],
                "questions": [{
                    "id": "Q-X",
                    "primary_capability_ref": "CAP-X",
                    "secondary_capability_refs": [],
                    "stem": "Solve X.",
                    "hints": [],
                    "repair_ref": "STEP-X",
                    "answer": {"kind": "MODEL_RESPONSE"},
                }],
            }), encoding="utf-8")
            request = {
                "subject": "Example",
                "question_ref": "Q-X",
                "attempt_number": 3,
                "shown_hint_indices": [],
                "attempted_question_refs": ["Q-X"],
                "help_used": "NONE",
                "when": "2026-09-18",
                "response_summary": "Setup failed.",
                "evaluation": {
                    "result": "INCORRECT",
                    "failed_capability_ref": "CAP-X",
                    "error_stage": "SETUP",
                },
            }
            report = feedback.run(request, root)
            self.assertEqual(report["next_action"], "REPAIR")
            self.assertEqual(report["repair"]["kind"], "TEACHING_STEP")
            self.assertEqual(report["repair"]["repair_ref"], "STEP-X")
            self.assertEqual(
                report["after_repair"]["next_action"],
                "VERIFICATION_ITEM_REQUIRED",
            )


    def test_arbitrary_worksheet_question_can_produce_observation_and_review(self):
        fixture = json.loads(
            (REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json")
            .read_text(encoding="utf-8")
        )
        row = fixture["questions"][0]
        report = feedback.run({
            "subject": fixture["subject"],
            "question_ref": row["question_id"],
            "worksheet_question": row,
            "attempt_number": 1,
            "attempted_question_refs": [row["question_id"]],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": fixture["worksheet_id"],
            "response_summary": "Explained the top-of-flight case correctly.",
            "evaluation": {
                "result": "CORRECT",
                "error_stage": "UNKNOWN",
            },
        })
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "CONTINUE")
        self.assertEqual(
            report["observation_draft"]["capability_ref"],
            row["primary_capability_ref"],
        )
        self.assertEqual(
            report["observation_draft"]["question_ref"],
            row["question_id"],
        )
        self.assertEqual(report["review"]["next_review"], "2026-09-25")

    def test_arbitrary_worksheet_question_diagnoses_instead_of_inventing_a_hint(self):
        fixture = json.loads(
            (REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json")
            .read_text(encoding="utf-8")
        )
        row = fixture["questions"][0]
        report = feedback.run({
            "subject": fixture["subject"],
            "question_ref": row["question_id"],
            "worksheet_question": row,
            "attempt_number": 1,
            "attempted_question_refs": [row["question_id"]],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": fixture["worksheet_id"],
            "response_summary": "Said acceleration must be zero because velocity is zero.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": row["primary_capability_ref"],
                "error_stage": "CONCEPT",
            },
        })
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["question_origin"], "WORKSHEET_MAPPING")
        self.assertEqual(report["next_action"], "DIAGNOSE")
        self.assertNotIn("hint", report)
        prompts = [
            item
            for option in report["diagnostic_options"]
            for item in option["diagnostics"]
        ]
        self.assertTrue(prompts)
        self.assertIn("diagnostic_prompt", prompts[0])

    def test_diagnosed_worksheet_failure_routes_to_existing_repair_then_fresh_check(self):
        fixture = json.loads(
            (REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json")
            .read_text(encoding="utf-8")
        )
        row = fixture["questions"][0]
        report = feedback.run({
            "subject": fixture["subject"],
            "question_ref": row["question_id"],
            "worksheet_question": row,
            "attempt_number": 1,
            "attempted_question_refs": [row["question_id"]],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": fixture["worksheet_id"],
            "response_summary": "Velocity zero, therefore acceleration zero.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": row["primary_capability_ref"],
                "error_stage": "CONCEPT",
                "diagnostic_evidence": confirmed_diagnostic_evidence(
                    fixture["subject"],
                    row["primary_capability_ref"],
                    "Velocity zero means the acceleration must also be zero.",
                    "The response to the canonical probe explicitly repeats the targeted apex misconception.",
                ),
            },
        })
        self.assertEqual(report["next_action"], "REPAIR")
        self.assertEqual(report["repair"]["kind"], "MISCONCEPTION_REPAIR")
        self.assertEqual(
            report["repair"]["microtopic_ref"],
            "MIC-PHY-KIN-ZERO-V-NONZERO-A",
        )
        self.assertEqual(report["after_repair"]["next_action"], "VERIFY")
        verification = report["after_repair"]["verification"]
        self.assertEqual(verification["kind"], "QUESTION")
        self.assertEqual(
            verification["question_ref"],
            "Q-PHY-KIN-VERT-2A-APEX-05",
        )
        self.assertNotIn("answer", verification)

    def test_arbitrary_worksheet_mapping_with_unknown_capability_stops(self):
        report = feedback.run({
            "subject": "Physics",
            "question_ref": "SCHOOL-Q-404",
            "worksheet_question": {
                "question_id": "SCHOOL-Q-404",
                "primary_capability_ref": "CAP-NOT-REAL",
                "secondary_capability_refs": [],
                "mapping_basis": "MANUAL",
            },
            "attempt_number": 1,
            "help_used": "NONE",
            "when": "2026-09-18",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-NOT-REAL",
                "error_stage": "CONCEPT",
            },
        })
        self.assertFalse(report["passed"])
        self.assertEqual(report["next_action"], "STOP")
        self.assertIn(
            "FEEDBACK_WORKSHEET_CAPABILITY_UNKNOWN",
            [row["point"] for row in report["findings"]],
        )

    def test_canonical_question_remains_authoritative_if_a_supplied_mapping_drifts(self):
        report = feedback.run({
            "subject": "Mathematics",
            "question_ref": self.QUESTION,
            "worksheet_question": {
                "question_id": self.QUESTION,
                "primary_capability_ref": "CAP-MATH-SUBSTITUTE",
                "secondary_capability_refs": [],
                "mapping_basis": "AGENT_PROPOSAL",
            },
            "attempt_number": 1,
            "help_used": "NONE",
            "when": "2026-09-18",
            "evaluation": {
                "result": "CORRECT",
                "error_stage": "UNKNOWN",
            },
        })
        self.assertFalse(report["passed"])
        self.assertEqual(report["question_origin"], "CANONICAL_QUESTION")
        self.assertIn(
            "FEEDBACK_CANONICAL_MAPPING_DRIFT",
            [row["point"] for row in report["findings"]],
        )
        self.assertEqual(
            report["observation_draft"]["capability_ref"],
            "CAP-MATH-ISOLATE",
        )


class LearningLoopScenarioScanner(unittest.TestCase):
    """Exhaust the finite feedback-policy branch space without fabricating learner evidence."""

    ALLOWED_ACTIONS = {
        "STOP",
        "DIAGNOSE",
        "RETRY",
        "REPAIR",
        "VERIFY",
        "VERIFICATION_ITEM_REQUIRED",
        "CONTINUE",
    }

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        library = self.repo / "Example/library"
        library.mkdir(parents=True)
        (library / "example.v1.json").write_text(json.dumps({
            "package_id": "PKG-SCANNER",
            "capabilities": [
                {"id": "CAP-A", "prerequisite_refs": []},
                {"id": "CAP-B", "prerequisite_refs": []},
            ],
            "microtopics": [
                {
                    "id": "MIC-A",
                    "primary_capability_ref": "CAP-A",
                    "title": "Capability A",
                    "misconceptions": [{
                        "wrong_idea": "Uses the wrong structural rule.",
                        "diagnostic_prompt": "Which relation must remain true?",
                        "repair": "Rebuild the relation before calculating.",
                    }],
                    "teaching_path": [{
                        "id": "STEP-A",
                        "action": "Rebuild A.",
                        "why_valid": "A determines the required relation.",
                    }],
                    "exit_task": {
                        "prompt": "Fresh A check.",
                        "source_ref": "AUTHORED-SCANNER",
                    },
                },
                {
                    "id": "MIC-B",
                    "primary_capability_ref": "CAP-B",
                    "title": "Capability B",
                    "misconceptions": [{
                        "wrong_idea": "Uses B in the wrong place.",
                        "diagnostic_prompt": "Where does B enter?",
                        "repair": "Place B only where its condition applies.",
                    }],
                    "teaching_path": [{
                        "id": "STEP-B",
                        "action": "Rebuild B.",
                        "why_valid": "B is a separate learner action.",
                    }],
                },
            ],
            "questions": [
                {
                    "id": "Q-A",
                    "primary_capability_ref": "CAP-A",
                    "secondary_capability_refs": ["CAP-B"],
                    "stem": "Solve A with B.",
                    "hints": [
                        {"text": "Name the governing relation.", "reveals": "CONCEPT"},
                        {"text": "Apply the relation before calculating.", "reveals": "METHOD"},
                        {"text": "The answer is 42.", "reveals": "ANSWER"},
                    ],
                    "answer": {"kind": "MODEL_RESPONSE"},
                },
                {
                    "id": "Q-A-FRESH",
                    "primary_capability_ref": "CAP-A",
                    "secondary_capability_refs": [],
                    "stem": "Fresh A question.",
                    "hints": [],
                    "answer": {"kind": "MODEL_RESPONSE"},
                },
                {
                    "id": "Q-B",
                    "primary_capability_ref": "CAP-B",
                    "secondary_capability_refs": [],
                    "stem": "Solve B.",
                    "hints": [],
                    "repair_ref": "STEP-B",
                    "answer": {"kind": "MODEL_RESPONSE"},
                },
                {
                    "id": "Q-TRANSFER",
                    "primary_capability_ref": "CAP-A",
                    "secondary_capability_refs": [],
                    "stem": "Choose the model, then solve.",
                    "hints": [
                        {"text": "What remains invariant?", "reveals": "CONCEPT"},
                        {"text": "Use model X.", "reveals": "METHOD"},
                        {"text": "The answer is Y.", "reveals": "ANSWER"},
                    ],
                    "transfer": {
                        "dimension": "model_choice",
                        "statement": "Choose the model from structure.",
                        "builds_on": ["MIC-A"],
                    },
                    "answer": {"kind": "MODEL_RESPONSE"},
                },
            ],
        }), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def request(self, **overrides):
        request = {
            "subject": "Example",
            "question_ref": "Q-A",
            "attempt_number": 1,
            "shown_hint_indices": [],
            "attempted_question_refs": ["Q-A"],
            "help_used": "NONE",
            "when": "2026-09-18",
            "session_ref": "SESSION-SCANNER",
            "response_summary": "Synthetic scanner response.",
            "evaluation": {
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-A",
                "error_stage": "CONCEPT",
            },
        }
        for key, value in overrides.items():
            if key == "evaluation":
                request["evaluation"].update(value)
            else:
                request[key] = value
        return request

    def scan(self, **overrides):
        return feedback.run(self.request(**overrides), self.repo)

    def test_exhaustive_valid_result_help_stage_attempt_matrix(self):
        """3 results × 5 help levels × 5 error stages × 3 attempts = 225 scans."""
        scanned = 0
        for result in sorted(feedback.RESULTS):
            for help_used in sorted(feedback.HELP_LEVELS):
                for error_stage in sorted(feedback.ERROR_STAGES):
                    for attempt_number in (1, 2, 3):
                        evaluation = {
                            "result": result,
                            "error_stage": error_stage,
                        }
                        if result == "INCORRECT":
                            evaluation["failed_capability_ref"] = "CAP-A"
                        else:
                            evaluation["failed_capability_ref"] = None

                        report = self.scan(
                            help_used=help_used,
                            attempt_number=attempt_number,
                            evaluation=evaluation,
                        )
                        scanned += 1
                        with self.subTest(
                            result=result,
                            help=help_used,
                            stage=error_stage,
                            attempt=attempt_number,
                        ):
                            self.assertTrue(report["passed"], report["findings"])
                            self.assertIn(report["next_action"], self.ALLOWED_ACTIONS)

                            observation = report.get("observation_draft")
                            if result == "UNDECIDABLE":
                                self.assertIsNone(observation)
                                self.assertEqual(report["next_action"], "DIAGNOSE")
                            elif result == "CORRECT":
                                self.assertIsNotNone(observation)
                                expected = (
                                    "DEMONSTRATED"
                                    if help_used == "NONE"
                                    else "UNCERTAIN"
                                )
                                self.assertEqual(observation["result"], expected)
                            else:
                                self.assertIsNotNone(observation)
                                expected = (
                                    "MISSING"
                                    if error_stage in {"CONCEPT", "SETUP"}
                                    else "UNCERTAIN"
                                )
                                self.assertEqual(observation["result"], expected)

                            hint = report.get("hint")
                            if hint:
                                self.assertNotEqual(hint.get("reveals"), "ANSWER")

        self.assertEqual(scanned, 225)

    def test_hint_history_scanner_never_reveals_answer(self):
        """All eight shown-hint subsets preserve the no-answer invariant."""
        for mask in range(8):
            shown = [index for index in range(3) if mask & (1 << index)]
            report = self.scan(
                attempt_number=2,
                shown_hint_indices=shown,
                help_used="HINT" if shown else "NONE",
            )
            with self.subTest(shown=shown):
                self.assertTrue(report["passed"], report["findings"])
                hint = report.get("hint")
                if hint:
                    self.assertNotEqual(hint["reveals"], "ANSWER")
                    self.assertNotEqual(hint["index"], 2)

    def test_multi_capability_attribution_scanner(self):
        cases = [
            (None, "DIAGNOSE", None, None),
            ("CAP-A", "RETRY", "CAP-A", None),
            ("CAP-B", "RETRY", "CAP-B", None),
            (
                "CAP-NOT-REQUIRED",
                "DIAGNOSE",
                None,
                "FEEDBACK_FAILED_CAPABILITY_NOT_REQUIRED",
            ),
        ]
        for failed, action, expected_failed, finding in cases:
            report = self.scan(
                evaluation={
                    "result": "INCORRECT",
                    "failed_capability_ref": failed,
                    "error_stage": "CONCEPT",
                },
            )
            with self.subTest(failed=failed):
                self.assertEqual(report["next_action"], action)
                self.assertEqual(report["failed_capability_ref"], expected_failed)
                points = [row["point"] for row in report["findings"]]
                if finding:
                    self.assertIn(finding, points)
                    self.assertIsNone(report["observation_draft"])
                else:
                    self.assertNotIn(
                        "FEEDBACK_FAILED_CAPABILITY_NOT_REQUIRED",
                        points,
                    )

    def test_reachable_feedback_action_scanner(self):
        """Every public feedback action is reached by at least one semantic scenario."""
        reports = {}

        reports["STOP"] = feedback.run({
            "subject": "Example",
            "question_ref": "Q-A",
            "evaluation": {"result": "NOT-A-RESULT"},
        }, self.repo)

        reports["DIAGNOSE"] = self.scan(
            evaluation={
                "result": "UNDECIDABLE",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )

        reports["RETRY"] = self.scan()

        reports["REPAIR"] = self.scan(
            attempt_number=3,
            shown_hint_indices=[0, 1],
            help_used="HINT",
            evaluation={"diagnostic_evidence": confirmed_diagnostic_evidence(
                self.SUBJECT,
                "CAP-MATH-ISOLATE",
                "I would change only one side of the equation.",
                "The canonical probe response repeats the one-sided-operation misconception.",
            )},
        )

        reports["VERIFY"] = self.scan(
            help_used="HINT",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )

        reports["VERIFICATION_ITEM_REQUIRED"] = self.scan(
            question_ref="Q-B",
            attempted_question_refs=["Q-B"],
            help_used="HINT",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )

        reports["CONTINUE"] = self.scan(
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )

        self.assertEqual(set(reports), self.ALLOWED_ACTIONS)
        for expected, report in reports.items():
            with self.subTest(expected=expected):
                self.assertEqual(report["next_action"], expected)

    def test_retry_repair_verify_sequence_is_explicit(self):
        first = self.scan()
        self.assertEqual(first["next_action"], "RETRY")
        self.assertEqual(first["hint"]["reveals"], "CONCEPT")

        second = self.scan(
            attempt_number=2,
            shown_hint_indices=[0],
            help_used="HINT",
        )
        self.assertEqual(second["next_action"], "RETRY")
        self.assertEqual(second["hint"]["reveals"], "METHOD")

        third = self.scan(
            attempt_number=3,
            shown_hint_indices=[0, 1],
            help_used="HINT",
            evaluation={"diagnostic_evidence": confirmed_diagnostic_evidence(
                self.SUBJECT,
                "CAP-MATH-ISOLATE",
                "I would change only one side of the equation.",
                "The canonical probe response repeats the one-sided-operation misconception.",
            )},
        )
        self.assertEqual(third["next_action"], "REPAIR")
        self.assertEqual(third["after_repair"]["next_action"], "VERIFY")
        self.assertEqual(
            third["after_repair"]["verification"]["question_ref"],
            "Q-A-FRESH",
        )

    def test_model_choice_transfer_never_receives_method_or_answer_hint(self):
        first = self.scan(
            question_ref="Q-TRANSFER",
            attempted_question_refs=["Q-TRANSFER"],
            evaluation={
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-A",
                "error_stage": "CONCEPT",
            },
        )
        self.assertEqual(first["next_action"], "RETRY")
        self.assertEqual(first["hint"]["reveals"], "CONCEPT")

        second = self.scan(
            question_ref="Q-TRANSFER",
            attempted_question_refs=["Q-TRANSFER"],
            attempt_number=2,
            shown_hint_indices=[0],
            help_used="HINT",
            evaluation={
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-A",
                "error_stage": "CONCEPT",
                "diagnostic_evidence": confirmed_diagnostic_evidence(
                    "Example",
                    "CAP-A",
                    "I chose the model without preserving the invariant relation.",
                    "The canonical probe response directly matches the authored structural misconception.",
                    root=self.repo,
                ),
            },
        )
        self.assertEqual(second["next_action"], "REPAIR")
        self.assertNotIn("hint", second)

    def test_worksheet_mapping_scanner_diagnoses_before_repair(self):
        worksheet = {
            "question_id": "W-A",
            "primary_capability_ref": "CAP-A",
            "secondary_capability_refs": [],
            "mapping_basis": "AGENT_PROPOSAL",
        }
        first = self.scan(
            question_ref="W-A",
            worksheet_question=worksheet,
            attempted_question_refs=["W-A"],
            evaluation={
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-A",
                "error_stage": "CONCEPT",
            },
        )
        self.assertEqual(first["next_action"], "DIAGNOSE")
        self.assertNotIn("hint", first)

        diagnosed = self.scan(
            question_ref="W-A",
            worksheet_question=worksheet,
            attempted_question_refs=["W-A"],
            evaluation={
                "result": "INCORRECT",
                "failed_capability_ref": "CAP-A",
                "error_stage": "CONCEPT",
                "diagnostic_evidence": confirmed_diagnostic_evidence(
                    "Example",
                    "CAP-A",
                    "I used the wrong structural rule instead of preserving the required relation.",
                    "The canonical probe response directly repeats the authored misconception.",
                    root=self.repo,
                ),
            },
        )
        self.assertEqual(diagnosed["next_action"], "REPAIR")
        self.assertEqual(
            diagnosed["repair"]["kind"],
            "MISCONCEPTION_REPAIR",
        )

    def test_verification_fallback_scanner_covers_question_exit_and_missing(self):
        fresh = self.scan(
            help_used="HINT",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )
        self.assertEqual(fresh["verification"]["kind"], "QUESTION")
        self.assertEqual(fresh["verification"]["question_ref"], "Q-A-FRESH")

        exit_task = self.scan(
            help_used="HINT",
            attempted_question_refs=["Q-A", "Q-A-FRESH", "Q-TRANSFER"],
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )
        self.assertEqual(exit_task["verification"]["kind"], "EXIT_TASK")

        missing = self.scan(
            question_ref="Q-B",
            attempted_question_refs=["Q-B"],
            help_used="HINT",
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )
        self.assertEqual(
            missing["next_action"],
            "VERIFICATION_ITEM_REQUIRED",
        )
        self.assertIsNone(missing["verification"])

    def test_help_normalisation_and_review_intervals(self):
        cases = [
            (
                {"help_used": "NONE", "shown_hint_indices": []},
                "DEMONSTRATED",
                "NONE",
                "CORRECT_INDEPENDENT",
                "2026-09-25",
            ),
            (
                {"help_used": "NONE", "shown_hint_indices": [0]},
                "UNCERTAIN",
                "HINT",
                "CORRECT_WITH_HINT",
                "2026-09-21",
            ),
            (
                {"help_used": "WORKED_EXAMPLE", "shown_hint_indices": []},
                "UNCERTAIN",
                "WORKED_EXAMPLE",
                "CORRECT_WITH_HINT",
                "2026-09-21",
            ),
            (
                {"help_used": "SOLUTION", "shown_hint_indices": []},
                "UNCERTAIN",
                "SOLUTION",
                "CORRECT_WITH_HINT",
                "2026-09-21",
            ),
            (
                {"help_used": "NOT-A-LEVEL", "shown_hint_indices": []},
                "UNCERTAIN",
                "UNKNOWN",
                "INCORRECT",
                "2026-09-19",
            ),
        ]
        for request_bits, state, help_value, outcome, next_review in cases:
            report = self.scan(
                **request_bits,
                evaluation={
                    "result": "CORRECT",
                    "failed_capability_ref": None,
                    "error_stage": "UNKNOWN",
                },
            )
            with self.subTest(request_bits=request_bits):
                self.assertEqual(report["observation_draft"]["result"], state)
                self.assertEqual(report["observation_draft"]["help"], help_value)
                self.assertEqual(report["review"]["outcome"], outcome)
                self.assertEqual(report["review"]["next_review"], next_review)

    def test_transfer_independent_success_uses_fourteen_day_review(self):
        report = self.scan(
            question_ref="Q-TRANSFER",
            attempted_question_refs=["Q-TRANSFER"],
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )
        self.assertEqual(report["next_action"], "CONTINUE")
        self.assertEqual(report["observation_draft"]["result"], "DEMONSTRATED")
        self.assertEqual(report["review"]["outcome"], "TRANSFER_INDEPENDENT")
        self.assertEqual(report["review"]["next_review"], "2026-10-02")

    def test_observation_is_always_draft_not_reviewed_live_evidence(self):
        report = self.scan(
            evaluation={
                "result": "CORRECT",
                "failed_capability_ref": None,
                "error_stage": "UNKNOWN",
            },
        )
        observation = report["observation_draft"]
        self.assertEqual(
            observation["provenance"],
            "UNREVIEWED_SESSION_DRAFT",
        )
        self.assertEqual(observation["evidence_kind"], "DIRECT_ATTEMPT")
        self.assertEqual(observation["session_ref"], "SESSION-SCANNER")

    def test_invalid_or_unusable_inputs_fail_without_inventing_evidence(self):
        cases = [
            (
                {"question_ref": "Q-NOT-REAL"},
                "FEEDBACK_QUESTION_UNKNOWN",
            ),
            (
                {
                    "question_ref": "W-UNKNOWN",
                    "worksheet_question": {
                        "question_id": "W-UNKNOWN",
                        "primary_capability_ref": "CAP-NOT-REAL",
                        "secondary_capability_refs": [],
                        "mapping_basis": "AGENT_PROPOSAL",
                    },
                },
                "FEEDBACK_WORKSHEET_CAPABILITY_UNKNOWN",
            ),
            (
                {
                    "question_ref": "W-A",
                    "worksheet_question": {
                        "question_id": "W-DIFFERENT",
                        "primary_capability_ref": "CAP-A",
                        "secondary_capability_refs": [],
                        "mapping_basis": "AGENT_PROPOSAL",
                    },
                },
                "FEEDBACK_WORKSHEET_QUESTION_ID_MISMATCH",
            ),
        ]
        for overrides, point in cases:
            request = self.request(**overrides)
            report = feedback.run(request, self.repo)
            with self.subTest(point=point):
                self.assertFalse(report["passed"])
                self.assertEqual(report["next_action"], "STOP")
                self.assertIn(point, [row["point"] for row in report["findings"]])
                self.assertIsNone(report.get("observation_draft"))



if __name__ == "__main__":
    unittest.main()
