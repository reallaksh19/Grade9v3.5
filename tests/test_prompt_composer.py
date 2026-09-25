from __future__ import annotations

import copy
import json
import subprocess
import unittest
from pathlib import Path

from Shared.tools import prompt_composer, study_map

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests/fixtures/prompt-composer"


class PromptComposerTests(unittest.TestCase):
    def load(self, name):
        return json.loads((FIXTURES / name).read_text(encoding="utf-8"))

    def test_nested_exam_bank_question_resolves_through_existing_study_map(self):
        mapping = {
            "worksheet_id": "NESTED-QUESTION-PROOF",
            "subject": "Physics",
            "questions": [{
                "question_id": "Q28",
                "primary_capability_ref": "CAP-KIN-2D-INDEPENDENT-COMPONENTS",
                "secondary_capability_refs": ["CAP-KIN-PROJECTILE-MODEL"],
                "mapping_basis": "CANONICAL_QUESTION",
                "canonical_question_ref": "PYQ-PHY-JEEMAIN-2026-04APR-S2-Q29",
            }],
        }
        report = study_map.resolve(mapping)
        self.assertTrue(report["passed"], report["findings"])

    def test_projectile_stress_set_preserves_per_question_rungs_and_owner_scope(self):
        result = prompt_composer.compose(self.load("projectile-stress-set.json"))
        self.assertTrue(result["passed"], result["prompt_brief"]["holds"])
        brief = result["prompt_brief"]
        self.assertEqual(brief["scope"]["matrix_ref"], "MATRIX-PHY-KIN-2D-MOTION")
        self.assertEqual(brief["scope"]["status"], "OWNER_CONFIRMED_CANONICAL_RUNG")
        self.assertEqual(brief["scope"]["canonical_primary_rungs"], ["R1", "R2", "R3"])
        self.assertEqual(brief["scope"]["owner_confirmed_rung"]["rung"], "R3")
        self.assertEqual(
            [row["primary_location"]["rung"] for row in brief["question_rows"]],
            ["R1", "R3", "R3", "R3", "R2"],
        )
        self.assertEqual(
            [row["record_status"] for row in brief["question_rows"]],
            ["CANDIDATE"] * 5,
        )
        self.assertEqual(
            brief["learner_entry"]["owner_estimate"]["knowledge_percentage"], 50
        )
        self.assertEqual(
            brief["execution_order"],
            ["CORE2", "CORE1", "CORE1A", "CORE1B", "CORE2A", "CORE2B"],
        )
        self.assertNotIn("source_basis", result["authoring_request"])
        self.assertEqual(result["planner_handoff"]["state"] if "planner_handoff" in result else brief["planner_handoff"]["state"], "READY_FOR_PLANNER")

    def test_prompt_contains_clause_ids_role_refs_and_downstream_pdf_intent_without_rendering_pdf(self):
        result = prompt_composer.compose(self.load("projectile-stress-set.json"))
        text = result["agent_prompt"]
        for clause in [
            "GOAL_OUTCOME", "FIXED_SOURCE_QUESTIONS", "LEARNER_PROFILE",
            "EXECUTION_ORDER", "TOPIC_BOUNDARY", "CORE_OBLIGATIONS",
            "DIFFICULTY_PROGRESSION", "PROVENANCE_TRACE", "ACCEPTANCE",
            "NON_GOALS", "HOLD_FAIL", "DOWNSTREAM_DELIVERABLE",
        ]:
            self.assertIn(f"[{clause}]", text)
        self.assertIn("Shared/roles/CORE1A.md", text)
        self.assertIn("learner percentage must not shrink", text.lower())
        self.assertIn("#273 owns PDF publication", text)
        self.assertFalse(any(path.suffix == ".pdf" for path in (REPO / "public").rglob("*.pdf")))

    def test_mixed_subtopic_fails_closed(self):
        result = prompt_composer.compose(self.load("mixed-subtopic.json"))
        self.assertFalse(result["passed"])
        self.assertEqual(result["prompt_brief"]["scope"]["status"], "MIXED_SUBTOPIC_HOLD")
        self.assertTrue(any(h["status"] == "MIXED_SUBTOPIC_HOLD" for h in result["prompt_brief"]["holds"]))

    def test_unknown_exact_ref_does_not_fuzzy_match_short_label(self):
        result = prompt_composer.compose(self.load("unknown-question.json"))
        self.assertFalse(result["passed"])
        row = result["prompt_brief"]["question_rows"][0]
        self.assertEqual(row["mapping_status"], "UNMAPPED_HOLD")
        self.assertIsNone(row["primary_capability_ref"])
        self.assertTrue(any(h["point"] == "CANONICAL_QUESTION_UNKNOWN" for h in result["prompt_brief"]["holds"]))

    def test_agent_proposal_remains_pending_owner_review(self):
        doc = self.load("projectile-stress-set.json")
        doc["questions"] = [{
            "question_id": "P",
            "summary": "Agent-proposed mapping.",
            "mapping_basis": "AGENT_PROPOSAL",
            "primary_capability_ref": "CAP-KIN-PROJECTILE-MODEL",
            "secondary_capability_refs": ["CAP-KIN-2D-INDEPENDENT-COMPONENTS"],
        }]
        result = prompt_composer.compose(doc)
        self.assertFalse(result["passed"])
        self.assertEqual(result["prompt_brief"]["question_rows"][0]["mapping_status"], "AGENT_PROPOSAL_PENDING_REVIEW")

    def test_explicit_zero_is_preserved_and_absent_is_null(self):
        math = prompt_composer.compose(self.load("math-linear-equation.json"))
        self.assertEqual(math["prompt_brief"]["learner_entry"]["owner_estimate"]["knowledge_percentage"], 0)
        doc = self.load("math-linear-equation.json")
        doc.pop("learner")
        no_learner = prompt_composer.compose(doc)
        self.assertIsNone(no_learner["prompt_brief"]["learner_entry"])

    def test_source_basis_never_accepts_canonical_question_ids(self):
        doc = self.load("projectile-stress-set.json")
        doc["source_basis"] = ["PYQ-PHY-JEEADV-2023-P1-Q01"]
        result = prompt_composer.compose(doc)
        self.assertFalse(result["passed"])
        self.assertNotIn("source_basis", result["authoring_request"])
        self.assertTrue(any(h["point"] == "SOURCE_BASIS_QUESTION_ID_INVALID" for h in result["prompt_brief"]["holds"]))

    def test_cross_subject_math_uses_same_composer(self):
        result = prompt_composer.compose(self.load("math-linear-equation.json"))
        self.assertTrue(result["passed"], result["prompt_brief"]["holds"])
        row = result["prompt_brief"]["question_rows"][0]
        self.assertEqual(row["primary_capability_ref"], "CAP-MATH-ISOLATE")
        self.assertEqual(row["primary_location"]["matrix_id"], "MATRIX-MATH-LINEAR-EQUATIONS")
        self.assertEqual(row["primary_location"]["rung"], "R2")

    def test_digest_is_deterministic_and_input_change_is_visible(self):
        doc = self.load("projectile-stress-set.json")
        a = prompt_composer.compose(copy.deepcopy(doc))
        b = prompt_composer.compose(copy.deepcopy(doc))
        self.assertEqual(a["prompt_brief"]["input_digest"], b["prompt_brief"]["input_digest"])
        self.assertEqual(a["prompt_brief"]["prompt_digest"], b["prompt_brief"]["prompt_digest"])
        changed = copy.deepcopy(doc)
        changed["learner"]["owner_estimate"]["knowledge_percentage"] = 51
        c = prompt_composer.compose(changed)
        self.assertNotEqual(a["prompt_brief"]["input_digest"], c["prompt_brief"]["input_digest"])
        self.assertNotEqual(a["prompt_brief"]["prompt_digest"], c["prompt_brief"]["prompt_digest"])

    def test_hostile_summary_is_preserved_as_data_not_executed_markup(self):
        doc = self.load("math-linear-equation.json")
        doc["questions"][0]["summary"] = "<script>globalThis.pwned=true</script>"
        result = prompt_composer.compose(doc)
        self.assertIn("<script>globalThis.pwned=true</script>", result["agent_prompt"])
        self.assertEqual(result["prompt_brief"]["question_rows"][0]["summary"], "<script>globalThis.pwned=true</script>")


    def test_browser_parity_syntax_and_generated_projection_checks(self):
        commands = [
            ["node", "--check", "public/js/core-prompt-composer.js"],
            ["node", "--check", "public/js/topic-atlas.js"],
            ["node", "--test", "tests/prompt_composer.test.mjs"],
            ["python3", "Shared/tools/build_prompt_composer_data.py", "--check"],
        ]
        for command in commands:
            completed = subprocess.run(
                command,
                cwd=REPO,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            self.assertEqual(
                completed.returncode,
                0,
                f"{' '.join(command)} failed:\n{completed.stdout}",
            )


if __name__ == "__main__":
    unittest.main()
