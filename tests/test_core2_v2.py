from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
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


class Core2V2ConceptJoinProjection(unittest.TestCase):
    @staticmethod
    def _microtopics() -> list[dict]:
        return [
            {"id": "MIC-A", "title": "Concept A", "primary_capability_ref": "CAP-A"},
            {"id": "MIC-B", "title": "Concept B", "primary_capability_ref": "CAP-B"},
        ]

    @staticmethod
    def _questions() -> list[dict]:
        return [
            {
                "id": "Q-PRIMARY",
                "primary_capability_ref": "CAP-A",
                "secondary_capability_refs": [],
            },
            {
                "id": "Q-MULTI",
                "primary_capability_ref": "CAP-B",
                "secondary_capability_refs": ["CAP-A", "CAP-B", "CAP-A"],
            },
            {
                "id": "Q-UNRELATED",
                "primary_capability_ref": "CAP-X",
                "secondary_capability_refs": [],
            },
        ]

    def test_primary_and_secondary_capabilities_generate_both_directions(self):
        join = core2_v2.concept_question_join(self._microtopics(), self._questions())
        self.assertEqual(join["question_to_microtopics"]["Q-PRIMARY"], ["MIC-A"])
        self.assertEqual(join["question_to_microtopics"]["Q-MULTI"], ["MIC-B", "MIC-A"])
        self.assertEqual(join["microtopic_to_questions"]["MIC-A"], ["Q-PRIMARY", "Q-MULTI"])
        self.assertEqual(join["microtopic_to_questions"]["MIC-B"], ["Q-MULTI"])

    def test_repeated_capability_refs_do_not_duplicate_reciprocal_links(self):
        join = core2_v2.concept_question_join(self._microtopics(), self._questions())
        self.assertEqual(join["question_to_microtopics"]["Q-MULTI"].count("MIC-A"), 1)
        self.assertEqual(join["microtopic_to_questions"]["MIC-A"].count("Q-MULTI"), 1)

    def test_unrelated_selected_question_does_not_get_generic_chapter_link(self):
        join = core2_v2.concept_question_join(self._microtopics(), self._questions())
        self.assertEqual(join["question_to_microtopics"]["Q-UNRELATED"], [])

    def test_ambiguous_selected_capability_ownership_fails_closed(self):
        microtopics = self._microtopics() + [
            {"id": "MIC-A2", "title": "Second A", "primary_capability_ref": "CAP-A"},
        ]
        with self.assertRaises(core2_v2.Core2ConceptJoinError):
            core2_v2.concept_question_join(microtopics, self._questions())

    def test_duplicate_selected_question_id_fails_closed(self):
        questions = self._questions() + [dict(self._questions()[0])]
        with self.assertRaises(core2_v2.Core2ConceptJoinError):
            core2_v2.concept_question_join(self._microtopics(), questions)


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


class Core2V2BlueprintContract(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads((REPO / "Shared/web/interactive-page-blueprints.v1.json").read_text(encoding="utf-8"))

    def _blueprint(self, role: str) -> dict:
        return next(bp for bp in self.registry["blueprints"] if role in bp["core_roles"])

    def test_both_sides_admit_derived_navigation_blocks(self):
        core1a = self._blueprint("CORE1A")
        core2 = self._blueprint("CORE2")
        core1a_blocks = {block for slot in core1a["slots"] for block in slot["accepts_blocks"]}
        core2_blocks = {block for slot in core2["slots"] for block in slot["accepts_blocks"]}
        self.assertIn("practice_navigation", core1a_blocks)
        self.assertIn("concept_navigation", core2_blocks)


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
    def _join_ctx() -> tuple[render_core.Ctx, dict, dict, dict]:
        microtopic_a = {"id": "MIC-A", "title": "Concept A", "primary_capability_ref": "CAP-A"}
        microtopic_b = {"id": "MIC-B", "title": "Concept B", "primary_capability_ref": "CAP-B"}
        question = {
            "id": "Q-JOIN",
            "original_identifier": "Exam|2026|Paper 1|Physics|Q7",
            "primary_capability_ref": "CAP-B",
            "secondary_capability_refs": ["CAP-A"],
            "stem": "A source question.",
            "answer": {"summary": "Answer", "reasoning": ["Working"]},
            "hints": [{"text": "Hidden source hint", "reveals": "CONCEPT"}],
            "scaffolds": [],
        }
        ctx = render_core.Ctx(
            manifest={"product_id": "test-product"},
            packages=[],
            bank=[],
            blueprints={},
            selection_rows={
                "microtopics": [microtopic_a, microtopic_b],
                "core2": [question],
            },
        )
        return ctx, microtopic_a, microtopic_b, question

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

    def test_structured_solution_renders_every_move_stage_and_crux_without_legacy_duplication(self):
        ctx = self._ctx()
        question = self._question()
        question["answer"] = Core2V2SolutionProjection._answer()
        rendered = render_core._core2_solution(ctx, question, question["answer"])
        self.assertEqual(rendered.count('class="g9-solution-move"'), 5)
        for stage in ("UNDERSTAND", "REPRESENT", "CONNECT", "CALCULATE", "INTERPRET"):
            self.assertIn(f'data-g9-solution-stage="{stage}"', rendered)
        self.assertIn(
            'data-g9-solution-move="MOVE-C" data-g9-solution-kind="CONNECT" '
            'data-g9-solution-stage="CONNECT" data-g9-solution-crux="true"',
            rendered,
        )
        self.assertNotIn("Legacy line one", rendered)
        self.assertLess(rendered.index("MOVE-U"), rendered.index("MOVE-R"))
        self.assertLess(rendered.index("MOVE-R"), rendered.index("MOVE-C"))
        self.assertLess(rendered.index("MOVE-C"), rendered.index("MOVE-X"))
        self.assertLess(rendered.index("MOVE-X"), rendered.index("MOVE-I"))
        self.assertEqual(ctx.gaps, [])

    def test_rendered_solution_preserves_repeated_calculation_moves(self):
        ctx = self._ctx()
        question = self._question()
        answer = Core2V2SolutionProjection._answer()
        extra = dict(answer["reasoning_route"][3])
        extra.update({"id": "MOVE-X2", "action": "Substitute the intermediate value into the second relation."})
        answer["reasoning_route"].insert(4, extra)
        question["answer"] = answer
        rendered = render_core._core2_solution(ctx, question, answer)
        self.assertEqual(rendered.count('data-g9-solution-stage="CALCULATE"'), 2)
        self.assertLess(rendered.index('data-g9-solution-move="MOVE-X"'), rendered.index('data-g9-solution-move="MOVE-X2"'))

    def test_legacy_solution_fallback_remains_plain_working(self):
        ctx = self._ctx()
        question = self._question()
        rendered = render_core._core2_solution(ctx, question, question["answer"])
        self.assertIn('data-g9-block="working"', rendered)
        self.assertIn("Reasoning step", rendered)
        self.assertNotIn("data-g9-solution-stage", rendered)
        self.assertEqual(ctx.gaps, [])

    def test_invalid_structured_solution_fails_closed_without_legacy_fallback(self):
        ctx = self._ctx()
        question = self._question()
        answer = Core2V2SolutionProjection._answer()
        answer["crux_move_ref"] = "MISSING"
        question["answer"] = answer
        self.assertEqual(render_core._core2_solution(ctx, question, answer), "")
        self.assertNotIn("Legacy line one", render_core._core2_solution(ctx, question, answer))
        self.assertTrue(any(gap["duty"] == "AUTHOR_CORE2_SOLUTION" for gap in ctx.gaps))

    def test_core2_entrypoint_consumes_structured_solution_projection(self):
        ctx = self._ctx()
        question = self._question()
        question["answer"] = Core2V2SolutionProjection._answer()
        rendered = render_core.core2(ctx, question)
        self.assertIn('data-g9-block="structured_working"', rendered)
        self.assertIn('data-g9-solution-stage="CONNECT"', rendered)
        self.assertNotIn("Legacy line one", rendered)

    def test_core1a_practice_navigation_is_exact_and_safe(self):
        ctx, microtopic_a, _microtopic_b, _question = self._join_ctx()
        rendered = render_core._core1a_practice_navigation(ctx, microtopic_a)
        self.assertIn('data-g9-block="practice_navigation"', rendered)
        self.assertIn('href="core2.html#Q-JOIN"', rendered)
        self.assertIn('data-g9-question-ref="Q-JOIN"', rendered)
        self.assertNotIn("Hidden source hint", rendered)

    def test_core2_concept_navigation_uses_primary_and_secondary_exact_concepts(self):
        ctx, _microtopic_a, _microtopic_b, question = self._join_ctx()
        rendered = render_core._core2_concept_navigation(ctx, question)
        self.assertIn('data-g9-block="concept_navigation"', rendered)
        self.assertIn('href="core1a.html#MIC-B"', rendered)
        self.assertIn('href="core1a.html#MIC-A"', rendered)
        self.assertLess(rendered.index("MIC-B"), rendered.index("MIC-A"))
        self.assertNotIn("Hidden source hint", rendered)

    def test_unrelated_question_renders_no_generic_concept_navigation(self):
        ctx, _microtopic_a, _microtopic_b, question = self._join_ctx()
        question = dict(question)
        question["id"] = "Q-OTHER"
        question["primary_capability_ref"] = "CAP-X"
        question["secondary_capability_refs"] = []
        ctx.selection_rows["core2"] = [question]
        self.assertEqual(render_core._core2_concept_navigation(ctx, question), "")

    def test_malformed_join_records_typed_gap_and_no_link(self):
        ctx, microtopic_a, _microtopic_b, question = self._join_ctx()
        ctx.selection_rows["microtopics"].append(
            {"id": "MIC-A2", "title": "Second A", "primary_capability_ref": "CAP-A"}
        )
        self.assertEqual(render_core._core2_concept_navigation(ctx, question), "")
        self.assertEqual(render_core._core1a_practice_navigation(ctx, microtopic_a), "")
        self.assertTrue(any(gap["duty"] == "RESOLVE_CORE2_CONCEPT_JOIN" for gap in ctx.gaps))

    def test_single_file_rewrite_keeps_cross_core_join_exact(self):
        page = (
            '<main><article id="MIC-A">'
            '<a data-g9-practice-link href="core2.html#Q-JOIN">Practice</a>'
            '</article></main>'
        )
        fragment = render_core._single_file_fragment(page, "CORE1A")
        self.assertIn('id="g9-CORE1A--MIC-A"', fragment)
        self.assertIn('href="#g9-CORE2--Q-JOIN"', fragment)


class Core2V2RoundTripStateContract(unittest.TestCase):
    def test_state_namespace_binds_product_render_digest_and_exact_question(self):
        js = render_core.JS
        self.assertIn("root.dataset.g9Product+':'+root.dataset.g9RenderDigest", js)
        self.assertIn("'state:'+scope+':'+a.dataset.g9Unit", js)
        self.assertIn("'return:'+scope+':'+concept", js)

    def test_persisted_payload_contains_interaction_state_not_academic_html(self):
        js = render_core.JS
        start = js.index("function saveCore2State")
        end = js.index("function restoreCore2State")
        save = js[start:end]
        self.assertIn("JSON.stringify({attempted:!!a.dataset.attempted,fields,ladders,reveals})", save)
        self.assertNotIn("innerHTML", save)
        self.assertNotIn("textContent", save)

    def test_restore_replays_attempt_fields_support_depth_and_commitment(self):
        js = render_core.JS
        self.assertIn("while(rungCount(l)<count&&nextRung(l)){}", js)
        self.assertIn("if(state.attempted){a.dataset.attempted='1';materialise(a)}", js)
        self.assertIn("el.type==='checkbox'||el.type==='radio'", js)
        self.assertIn("state.reveals||[]", js)
        self.assertIn("d.addEventListener('toggle',()=>saveCore2State(a))", js)

    def test_concept_round_trip_marks_only_the_exact_origin_question(self):
        js = render_core.JS
        self.assertIn("saveCore2State(a);const key=returnKey(link.dataset.g9ConceptRef)", js)
        self.assertIn("store.set(key,link.dataset.g9QuestionRef||a.dataset.g9Unit)", js)
        self.assertIn("const active=!!key&&store.get(key)===link.dataset.g9QuestionRef", js)
        self.assertIn("link.dataset.g9ReturnLink=''", js)
        self.assertIn("store.remove(key);refreshReturnLinks()", js)

    def test_storage_failure_is_non_blocking(self):
        js = render_core.JS
        self.assertIn("catch(e){return null}", js)
        self.assertIn("catch(e){return false}", js)
        # The static exact links remain the navigation authority when storage is unavailable.
        ctx, microtopic_a, _microtopic_b, question = Core2V2RendererContract._join_ctx()
        self.assertIn('href="core2.html#Q-JOIN"', render_core._core1a_practice_navigation(ctx, microtopic_a))
        self.assertIn('href="core1a.html#MIC-B"', render_core._core2_concept_navigation(ctx, question))

    def test_rendered_page_exposes_digest_scope_and_role_on_the_question_article(self):
        question = Core2V2RendererContract._question()
        ctx = render_core.Ctx(
            manifest={
                "product_id": "PRODUCT-STATE",
                "title": "State test",
                "subject": "Physics",
                "home_href": "index.html",
                "question_bank_href": "index.html",
            },
            packages=[],
            bank=[],
            blueprints={
                "blueprints": [
                    {
                        "id": "BP-STATE",
                        "version": "1.0.0",
                        "core_roles": ["CORE2"],
                        "responsive_policy": {"expanded": "STAGE_SUPPORT"},
                    }
                ]
            },
            selection_rows={"core2": [question], "microtopics": []},
        )
        rendered = render_core.page(ctx, "CORE2", "PAGES", "digest-123")
        self.assertIn('data-g9-product="PRODUCT-STATE"', rendered)
        self.assertIn('data-g9-render-digest="digest-123"', rendered)
        self.assertIn('data-g9-unit="Q-1" data-g9-kind="QUESTION" data-g9-role="CORE2"', rendered)

    def test_state_runtime_is_valid_javascript(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("node is unavailable")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "runtime.js"
            path.write_text(render_core.JS, encoding="utf-8")
            result = subprocess.run([node, "--check", str(path)], capture_output=True, text=True, check=False)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
