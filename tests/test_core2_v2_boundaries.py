from __future__ import annotations

import unittest

from Shared.tools import core_template_contract, render_core


class Core2V2LearnerJobBoundary(unittest.TestCase):
    @staticmethod
    def _ctx() -> render_core.Ctx:
        return render_core.Ctx(
            manifest={"product_id": "test-product"},
            packages=[],
            bank=[],
            blueprints={},
            selection_rows={"microtopics": [], "core2": []},
        )

    def test_core2_v2_blueprint_versions_are_resolvable_from_the_authoritative_template_contract(self):
        core1a = core_template_contract.resolve_web_blueprint_for_core("CORE1A")
        core2 = core_template_contract.resolve_web_blueprint_for_core("CORE2")

        self.assertEqual(core1a["ref"], "BP-CORE1A-CONSTRUCTION@1.4.0")
        self.assertEqual(core2["ref"], "BP-CORE2-SOURCE-QUESTION@1.4.0")
        self.assertIn(
            "practice_navigation",
            next(slot for slot in core1a["slots"] if slot["id"] == "repair_closure")["accepts_blocks"],
        )
        self.assertIn(
            "concept_navigation",
            next(slot for slot in core2["slots"] if slot["id"] == "support")["accepts_blocks"],
        )

    def test_routine_zero_support_question_stays_lightweight_and_non_clinic(self):
        question = {
            "id": "Q-ROUTINE",
            "original_identifier": "School|2026|Physics|Q1",
            "stem": "State the requested quantity.",
            "conditions": [],
            "hints": [],
            "scaffolds": [],
            "answer": {"summary": "Verified result", "reasoning": ["Use the stated relation."]},
            "response": {"type": "short_text"},
        }

        rendered = render_core.core2(self._ctx(), question)

        # Routine Core2 remains an authentic attempt + gated solution encounter.
        self.assertIn('data-g9-attempt-box', rendered)
        self.assertIn('Answer and working', rendered)

        # No empty/filler support UI is manufactured merely to satisfy a ladder quota.
        self.assertNotIn('data-g9-block="source_hints"', rendered)
        self.assertNotIn('data-g9-block="authored_core2_support"', rendered)
        self.assertNotIn('data-g9-next-rung', rendered)

        # Question-Clinic-only anatomy is not injected into routine Core2.
        for block in (
            "failure_signal",
            "protected_move",
            "rubric",
            "independent_check",
            "repair",
            "lineage_check",
        ):
            with self.subTest(block=block):
                self.assertNotIn(f'data-g9-block="{block}"', rendered)


if __name__ == "__main__":
    unittest.main()
