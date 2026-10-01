"""The toughest concept of a question set: chosen from the records by one written rule, and used by Core1A and the explorer."""
from __future__ import annotations

import unittest

from Shared.tools import toughest_concept


def question(qid: str, parts: dict, band: str = "D2", score: int | None = None, capability: str = "CAP-A", label: str = "",
             moves: bool = True, wrong: str = "") -> dict:
    components = {"algebra_computational_load": 0, "concept_model_selection": 0, "reasoning_chain_length": 0,
                  "representation_translation": 0, "trap_exception_sensitivity": 0, **parts}
    row = {"id": qid, "original_identifier": label or qid, "stem": f"stem of {qid}", "primary_capability_ref": capability,
           "extensions": {"grade9v3:analysis": {"difficulty": {"band": band, "score": sum(components.values()) if score is None else score,
                                                              "components": components},
                                                "common_wrong_route": wrong}}}
    if moves:
        row["answer"] = {"crux_move_ref": f"{qid}-M2", "reasoning_route": [
            {"id": f"{qid}-M1", "kind": "DECIDE", "action": "decide", "why_valid": "w1", "output": "o1"},
            {"id": f"{qid}-M2", "kind": "TRANSFORM", "action": "the move that is missed", "why_valid": "w2", "output": "o2"}]}
    return row


MICROTOPICS = [{"id": "MIC-A", "title": "Concept A", "primary_capability_ref": "CAP-A", "relation_refs": ["REL-A"]},
               {"id": "MIC-B", "title": "Concept B", "primary_capability_ref": "CAP-B", "relation_refs": []}]


class Rule(unittest.TestCase):
    def test_conceptual_difficulty_outranks_a_higher_total_that_is_all_algebra(self):
        algebra = question("Q-ALG", {"algebra_computational_load": 2, "reasoning_chain_length": 2, "representation_translation": 2},
                           band="D3")
        concept = question("Q-CON", {"concept_model_selection": 2, "trap_exception_sensitivity": 1}, band="D2")
        brief = toughest_concept.derive([algebra, concept], MICROTOPICS)
        self.assertEqual(brief["question_ref"], "Q-CON")
        self.assertEqual(brief["conceptual"], 3)

    def test_ties_fall_to_the_total_then_the_representation_then_the_chain_then_the_bank_order(self):
        base = {"concept_model_selection": 1, "trap_exception_sensitivity": 1}
        higher_total = question("Q-TOTAL", {**base, "algebra_computational_load": 1})
        same = question("Q-SAME", base)
        self.assertEqual(toughest_concept.derive([same, higher_total], MICROTOPICS)["question_ref"], "Q-TOTAL")
        by_representation = question("Q-REP", {**base, "representation_translation": 1})
        by_chain = question("Q-CHAIN", {**base, "reasoning_chain_length": 1})
        self.assertEqual(toughest_concept.derive([by_chain, by_representation], MICROTOPICS)["question_ref"], "Q-REP")
        first, second = question("Q-1", base), question("Q-2", base)
        self.assertEqual(toughest_concept.derive([first, second], MICROTOPICS)["question_ref"], "Q-1")
        self.assertEqual(toughest_concept.derive([second, first], MICROTOPICS)["question_ref"], "Q-2")

    def test_nothing_is_chosen_on_a_guess(self):
        bare = {"id": "Q-X", "stem": "s", "extensions": {}}
        half = question("Q-H", {})
        half["extensions"]["grade9v3:analysis"]["difficulty"]["band"] = "D9"
        self.assertIsNone(toughest_concept.derive([bare, half], MICROTOPICS))
        self.assertIn("not chosen", toughest_concept.describe(None)[0])

    def test_the_brief_names_the_concept_the_move_missed_and_the_tempting_route(self):
        hard = question("Q-HARD", {"concept_model_selection": 2, "trap_exception_sensitivity": 2}, band="D3", label="Q8",
                        wrong="Assuming the sizes always add.")
        easy = question("Q-EASY", {"concept_model_selection": 1}, band="D1")
        sibling = question("Q-SIB", {"concept_model_selection": 1, "trap_exception_sensitivity": 1})
        other = question("Q-OTHER", {"algebra_computational_load": 2}, capability="CAP-B")
        brief = toughest_concept.derive([easy, hard, sibling, other], MICROTOPICS)
        self.assertEqual((brief["question_ref"], brief["label"], brief["band"]), ("Q-HARD", "Q8", "D3"))
        self.assertEqual((brief["microtopic_ref"], brief["microtopic_title"], brief["relation_refs"]), ("MIC-A", "Concept A", ["REL-A"]))
        self.assertEqual(brief["crux_move"]["action"], "the move that is missed")
        self.assertEqual(brief["wrong_route"], "Assuming the sizes always add.")
        self.assertEqual(brief["related_question_refs"], ["Q-SIB", "Q-EASY"])
        self.assertEqual(brief["runner_up"]["question_ref"], "Q-SIB")
        text = " ".join(toughest_concept.describe(brief))
        for phrase in ("Q8", "Concept A", "the move that is missed", "Assuming the sizes always add", "most conceptual"):
            self.assertIn(phrase, text)

    def test_a_question_whose_capability_no_concept_owns_is_still_named_and_says_so(self):
        orphan = question("Q-O", {"concept_model_selection": 2}, capability="CAP-NOBODY")
        brief = toughest_concept.derive([orphan], MICROTOPICS)
        self.assertIsNone(brief["microtopic_ref"])
        self.assertIn("no microtopic", toughest_concept.describe(brief)[0])

    def test_a_unit_takes_the_depth_of_the_hardest_question_it_builds_toward(self):
        d1 = question("Q-1", {}, band="D1")
        d3 = question("Q-3", {"concept_model_selection": 2, "trap_exception_sensitivity": 2}, band="D3")
        self.assertEqual(toughest_concept.crux_band({"crux_question_refs": ["Q-1", "Q-3"]}, [d1, d3]), "D3")
        self.assertEqual(toughest_concept.crux_band({"crux_question_refs": ["Q-1"]}, [d1, d3]), "D1")
        self.assertIsNone(toughest_concept.crux_band({}, [d1, d3]))
        self.assertIsNone(toughest_concept.crux_band({"crux_question_refs": ["Q-MISSING"]}, [d1, d3]))


if __name__ == "__main__":
    unittest.main()
