from __future__ import annotations

import json
from pathlib import Path
import unittest

from jsonschema import Draft202012Validator

from Shared.tools import core2_v2, render_core


REPO = Path(__file__).resolve().parents[1]


class Core2V2SupportProjection(unittest.TestCase):
    def test_adapted_question_hints_remain_source_support(self):
        question = {
            "origin": "ADAPTED",
            "hints": [{"text": "Source hint", "reveals": "CONCEPT"}],
            "scaffolds": [],
            "hint_ladder": [
                {
                    "order": 1,
                    "from": "hints[0]",
                    # A stale/misleading migration label must not override the
                    # canonical owning field for Core2 provenance.
                    "provenance": "AUTHORED_HINT",
                }
            ],
        }
        rows = core2_v2.project_support(question)
        self.assertEqual(rows[0]["provenance"], core2_v2.SOURCE_HINT)
        self.assertEqual(rows[0]["source"], "hints[0]")

    def test_authored_scaffold_is_not_presented_as_source_hint(self):
        question = {
            "hints": [],
            "scaffolds": [
                {
                    "text": "Choose the useful representation.",
                    "support_kind": "REPRESENT",
                    "reveals": "CONCEPT",
                    "supports_move_ref": "MOVE-1",
                }
            ],
        }
        source, authored = core2_v2.split_pre_solution_support(question)
        self.assertEqual(source, [])
        self.assertEqual(len(authored), 1)
        self.assertEqual(authored[0]["provenance"], core2_v2.AUTHORED_CORE2_SUPPORT)

    def test_source_and_authored_support_coexist_without_collapse(self):
        question = {
            "hints": [{"text": "Printed hint", "reveals": "CONCEPT"}],
            "scaffolds": [
                {
                    "text": "Write the first relation.",
                    "support_kind": "CONNECT",
                    "reveals": "METHOD",
                    "supports_move_ref": "MOVE-2",
                }
            ],
            "hint_ladder": [
                {"order": 1, "from": "hints[0]"},
                {"order": 2, "from": "scaffolds[0]"},
            ],
        }
        source, authored = core2_v2.split_pre_solution_support(question)
        self.assertEqual([row["text"] for row in source], ["Printed hint"])
        self.assertEqual([row["text"] for row in authored], ["Write the first relation."])

    def test_answer_revealing_rows_are_not_pre_solution_support(self):
        question = {
            "hints": [{"text": "This gives the final answer.", "reveals": "ANSWER"}],
            "scaffolds": [
                {
                    "text": "The requested result is 42.",
                    "support_kind": "EXECUTE",
                    "reveals": "ANSWER",
                    "supports_move_ref": "MOVE-3",
                }
            ],
        }
        all_rows = core2_v2.project_support(question)
        self.assertEqual(len(all_rows), 2)
        self.assertTrue(all(not row["eligible_pre_solution"] for row in all_rows))
        self.assertEqual(core2_v2.pre_solution_support(question), [])

    def test_core2_has_no_three_rung_minimum(self):
        for count in (0, 1, 2, 3):
            with self.subTest(count=count):
                question = {
                    "hints": [],
                    "scaffolds": [
                        {
                            "text": f"Support {i}",
                            "support_kind": "CONNECT",
                            "reveals": "METHOD",
                            "supports_move_ref": f"MOVE-{i}",
                        }
                        for i in range(count)
                    ],
                }
                self.assertEqual(len(core2_v2.pre_solution_support(question)), count)

    def test_explicit_learner_stage_is_preserved_not_inferred_from_text(self):
        question = {
            "hints": [],
            "scaffolds": [
                {
                    "text": "Reveal text",
                    "prompt": "What is the decisive idea?",
                    "learner_stage": "KEY_CONCEPT",
                    "support_kind": "CONNECT",
                    "reveals": "CONCEPT",
                    "supports_move_ref": "MOVE-1",
                }
            ],
        }
        row = core2_v2.project_support(question)[0]
        self.assertEqual(row["prompt"], "What is the decisive idea?")
        self.assertEqual(row["learner_stage"], "KEY_CONCEPT")

    def test_invalid_ladder_reference_fails_closed(self):
        question = {
            "hints": [{"text": "One", "reveals": "CONCEPT"}],
            "scaffolds": [],
            "hint_ladder": [{"order": 1, "from": "scaffolds[9]"}],
        }
        with self.assertRaises(core2_v2.Core2SupportProjectionError):
            core2_v2.project_support(question)


class Core2V2SolutionProjection(unittest.TestCase):
    @staticmethod
    def _answer() -> dict:
        return {
            "summary": "Verified result",
            "reasoning": ["Legacy line one", "Legacy line two"],
            "crux_move_ref": "MOVE-C",
            "reasoning_route": [
                {
                    "id": "MOVE-U",
                    "kind": "DECIDE",
                    "action": "Identify what the question is asking for.",
                    "why_valid": "The target determines which model outputs matter.",
                    "inputs": ["stem"],
                    "output": "Target quantity identified.",
                },
                {
                    "id": "MOVE-R",
                    "kind": "REPRESENT",
                    "action": "Resolve the situation into independent components.",
                    "why_valid": "The chosen axes make the independent directions explicit.",
                    "inputs": ["diagram", "axes"],
                    "output": "Component representation ready.",
                },
                {
                    "id": "MOVE-C",
                    "kind": "CONNECT",
                    "action": "Connect each component to its governing relation.",
                    "why_valid": "Each direction follows the same model under the stated conditions.",
                    "inputs": ["components", "relations"],
                    "output": "Equations for the unknowns.",
                },
                {
                    "id": "MOVE-X",
                    "kind": "TRANSFORM",
                    "action": "Solve the equations and combine the results.",
                    "why_valid": "Algebra preserves the established relations.",
                    "inputs": ["equations"],
                    "output": "Numerical result obtained.",
                },
                {
                    "id": "MOVE-I",
                    "kind": "VERIFY",
                    "action": "Interpret and independently check the result.",
                    "why_valid": "The sign, unit and limiting behaviour must match the physical situation.",
                    "inputs": ["result"],
                    "output": "Result is consistent with the scenario.",
                },
            ],
        }

    def test_structured_route_maps_to_preferred_learner_progression_without_losing_moves(self):
        rows = core2_v2.project_solution(self._answer())
        self.assertEqual(
            [row["stage"] for row in rows],
            ["UNDERSTAND", "REPRESENT", "CONNECT", "CALCULATE", "INTERPRET"],
        )
        self.assertEqual([row["move_id"] for row in rows], ["MOVE-U", "MOVE-R", "MOVE-C", "MOVE-X", "MOVE-I"])
        self.assertEqual([row["is_crux"] for row in rows], [False, False, True, False, False])

    def test_solution_projection_does_not_fabricate_missing_stage_boxes(self):
        answer = self._answer()
        answer["reasoning_route"] = [answer["reasoning_route"][2], answer["reasoning_route"][3]]
        answer["crux_move_ref"] = "MOVE-C"
        rows = core2_v2.project_solution(answer)
        self.assertEqual([row["stage"] for row in rows], ["CONNECT", "CALCULATE"])

    def test_repeated_stage_moves_remain_separate_intermediate_steps(self):
        answer = self._answer()
        extra = dict(answer["reasoning_route"][3])
        extra.update({"id": "MOVE-X2", "action": "Substitute the intermediate value into the second relation."})
        answer["reasoning_route"].insert(4, extra)
        rows = core2_v2.project_solution(answer)
        calculate = [row for row in rows if row["stage"] == "CALCULATE"]
        self.assertEqual([row["move_id"] for row in calculate], ["MOVE-X", "MOVE-X2"])

    def test_legacy_answer_has_no_structured_projection(self):
        self.assertEqual(core2_v2.project_solution({"reasoning": ["Legacy line"]}), [])

    def test_invalid_crux_reference_fails_closed(self):
        answer = self._answer()
        answer["crux_move_ref"] = "MISSING"
        with self.assertRaises(core2_v2.Core2SolutionProjectionError):
            core2_v2.project_solution(answer)


class Core2V2SchemaContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(cls.schema["$defs"]["scaffold"])

    def test_prompt_reveal_metadata_is_admitted_by_canonical_scaffold_schema(self):
        scaffold = {
            "text": "Resolve each component independently.",
            "prompt": "Which representation separates the two directions?",
            "learner_stage": "REPRESENTATION",
            "support_kind": "REPRESENT",
            "reveals": "METHOD",
            "supports_move_ref": "MOVE-1",
        }
        self.assertEqual(list(self.validator.iter_errors(scaffold)), [])

    def test_prompt_and_explicit_learner_stage_are_paired(self):
        base = {
            "text": "Use the governing relation.",
            "support_kind": "CONNECT",
            "reveals": "METHOD",
            "supports_move_ref": "MOVE-2",
        }
        self.assertTrue(list(self.validator.iter_errors({**base, "prompt": "What relation connects the knowns?"})))
        self.assertTrue(list(self.validator.iter_errors({**base, "learner_stage": "KEY_CONCEPT"})))


class Core2V2RendererContract(unittest.TestCase):
    @staticmethod
    def _ctx() -> render_core.Ctx:
        return render_core.Ctx(
            manifest={"product_id": "test-product"},
            packages=[],
            bank=[],
            blueprints={},
        )

    @staticmethod
    def _question() -> dict:
        return {
            "id": "Q-1",
            "stem": "Find the requested quantity.",
            "answer": {"summary": "Verified result", "reasoning": ["Reasoning step"]},
            "hints": [{"text": "Printed source hint", "reveals": "CONCEPT"}],
            "scaffolds": [
                {
                    "text": "Use components before substituting values.",
                    "prompt": "Which representation separates the independent directions?",
                    "learner_stage": "REPRESENTATION",
                    "support_kind": "REPRESENT",
                    "reveals": "METHOD",
                    "supports_move_ref": "MOVE-1",
                },
                {
                    "text": "The final requested result is 42.",
                    "learner_stage": "FIRST_MOVE",
                    "support_kind": "EXECUTE",
                    "reveals": "ANSWER",
                    "supports_move_ref": "MOVE-2",
                },
            ],
            "hint_ladder": [
                {"order": 1, "from": "hints[0]"},
                {"order": 2, "from": "scaffolds[0]"},
                {"order": 3, "from": "scaffolds[1]"},
            ],
        }

    @staticmethod
    def _structured_question() -> dict:
        q = Core2V2RendererContract._question()
        q["answer"] = Core2V2SolutionProjection._answer()
        return q

    def test_renderer_keeps_source_and_authored_support_in_separate_groups(self):
        ctx = self._ctx()
        rendered = render_core._core2_support(ctx, self._question())
        self.assertIn('data-g9-support-group="SOURCE_HINT"', rendered)
        self.assertIn('data-g9-support-group="AUTHORED_CORE2_PROMPT_REVEAL"', rendered)
        self.assertIn('data-g9-support-provenance="SOURCE_HINT"', rendered)
        self.assertIn('data-g9-support-provenance="AUTHORED_CORE2_PROMPT_REVEAL"', rendered)
        self.assertEqual(rendered.count("<ol data-g9-ladder></ol>"), 2)
        self.assertNotIn("The final requested result is 42.", rendered)
        self.assertEqual(ctx.gaps, [])

    def test_authored_prompt_precedes_bounded_reveal_and_keeps_explicit_stage(self):
        rendered = render_core._core2_support(self._ctx(), self._question())
        prompt = "Which representation separates the independent directions?"
        reveal = "Use components before substituting values."
        self.assertIn('data-g9-support-stage="REPRESENTATION"', rendered)
        self.assertIn('data-g9-support-prompt', rendered)
        self.assertIn('details data-g9-support-reveal', rendered)
        self.assertLess(rendered.index(prompt), rendered.index(reveal))

    def test_core2_entrypoint_consumes_authored_support_projection(self):
        ctx = self._ctx()
        rendered = render_core.core2(ctx, self._question())
        self.assertIn('data-g9-block="authored_core2_support"', rendered)
        self.assertIn('data-g9-support-provenance="AUTHORED_CORE2_PROMPT_REVEAL"', rendered)
        self.assertNotIn("The final requested result is 42.", rendered)

    def test_projection_error_records_gap_and_renders_no_support(self):
        ctx = self._ctx()
        question = self._question()
        question["hint_ladder"] = [{"order": 1, "from": "scaffolds[99]"}]
        self.assertEqual(render_core._core2_support(ctx, question), "")
        self.assertEqual(ctx.gaps[0]["duty"], "AUTHOR_CORE2_SUPPORT")

    def test_structured_solution_renders_every_move_with_stage_and_crux_semantics(self):
        ctx = self._ctx()
        rendered = render_core._core2_reasoning_solution(ctx, self._structured_question())
        expected = ["UNDERSTAND", "REPRESENT", "CONNECT", "CALCULATE", "INTERPRET"]
        positions = [rendered.index(f'data-g9-solution-stage="{stage}"') for stage in expected]
        self.assertEqual(positions, sorted(positions))
        for move in ("MOVE-U", "MOVE-R", "MOVE-C", "MOVE-X", "MOVE-I"):
            self.assertIn(f'data-g9-reasoning-move="{move}"', rendered)
        self.assertIn('data-g9-solution-crux="true"', rendered)
        self.assertIn("Equations for the unknowns.", rendered)
        self.assertEqual(ctx.gaps, [])

    def test_structured_solution_does_not_emit_unwritten_stage_boxes(self):
        q = self._structured_question()
        q["answer"]["reasoning_route"] = q["answer"]["reasoning_route"][2:4]
        q["answer"]["crux_move_ref"] = "MOVE-C"
        rendered = render_core._core2_reasoning_solution(self._ctx(), q)
        self.assertIn('data-g9-solution-stage="CONNECT"', rendered)
        self.assertIn('data-g9-solution-stage="CALCULATE"', rendered)
        self.assertNotIn('data-g9-solution-stage="UNDERSTAND"', rendered)
        self.assertNotIn('data-g9-solution-stage="REPRESENT"', rendered)
        self.assertNotIn('data-g9-solution-stage="INTERPRET"', rendered)

    def test_legacy_solution_keeps_existing_reasoning_fallback(self):
        rendered = render_core._core2_reasoning_solution(self._ctx(), self._question())
        self.assertIn('data-g9-block="working"', rendered)
        self.assertIn("Reasoning step", rendered)
        self.assertNotIn("data-g9-solution-route", rendered)

    def test_invalid_structured_solution_records_gap_and_does_not_fall_back_silently(self):
        ctx = self._ctx()
        q = self._structured_question()
        q["answer"]["crux_move_ref"] = "MISSING"
        self.assertEqual(render_core._core2_reasoning_solution(ctx, q), "")
        self.assertEqual(ctx.gaps[0]["duty"], "AUTHOR_CORE2_SOLUTION")


if __name__ == "__main__":
    unittest.main()
