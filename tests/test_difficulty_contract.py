from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools import question_difficulty


REPO = Path(__file__).resolve().parents[1]
COMPONENTS = set(question_difficulty.COMPONENT_KEYS)


class DifficultyContractTests(unittest.TestCase):
    def legacy_difficulty(self) -> dict:
        return {
            "band": "D3",
            "score": 6,
            "components": {
                "concept_model_selection": 1,
                "representation_translation": 2,
                "reasoning_chain_length": 2,
                "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
            "basis": "Representation plus a multi-step bridge.",
        }

    def difficulty_validator(self) -> Draft202012Validator:
        schema = json.loads(
            (REPO / "Shared" / "library" / "package.schema.json").read_text(encoding="utf-8")
        )
        return Draft202012Validator({
            "$schema": schema["$schema"],
            "$ref": "#/$defs/question_difficulty",
            "$defs": schema["$defs"],
        })

    def test_component_rubric_has_subject_neutral_zero_one_two_anchors(self):
        metadata = question_difficulty.metadata()
        rubric = metadata["question_difficulty_component_rubric"]
        self.assertEqual(rubric["schema"], "grade9v3-question-difficulty-component-rubric/v1")
        self.assertEqual(set(rubric["components"]), COMPONENTS)
        for component, row in rubric["components"].items():
            with self.subTest(component=component):
                self.assertEqual(set(row["anchors"]), {"0", "1", "2"})
                self.assertTrue(all(str(row["anchors"][key]).strip() for key in ("0", "1", "2")))
        text = json.dumps(rubric)
        self.assertNotIn("Physics", text)
        self.assertNotIn("Chemistry", text)
        self.assertNotIn("Mathematics", text)

    def test_component_evidence_is_backward_compatible_but_complete_when_present(self):
        check = self.difficulty_validator()
        legacy = self.legacy_difficulty()
        self.assertEqual(list(check.iter_errors(legacy)), [])

        with_evidence = copy.deepcopy(legacy)
        with_evidence["component_evidence"] = {
            "concept_model_selection": "One familiar model must be selected from the stated cues.",
            "representation_translation": "The directed diagram must be translated into signed algebra.",
            "reasoning_chain_length": "A short dependency chain links the sign convention to the final equation.",
            "algebra_computational_load": "Only routine local algebra remains after the representation is fixed.",
            "trap_exception_sensitivity": "No additional boundary or exception changes the route.",
        }
        self.assertEqual(list(check.iter_errors(with_evidence)), [])

        incomplete = copy.deepcopy(with_evidence)
        del incomplete["component_evidence"]["representation_translation"]
        self.assertTrue(list(check.iter_errors(incomplete)))


if __name__ == "__main__":
    unittest.main()
