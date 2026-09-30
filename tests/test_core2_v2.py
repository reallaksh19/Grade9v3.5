from __future__ import annotations

import unittest

from Shared.tools import core2_v2


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


if __name__ == "__main__":
    unittest.main()
