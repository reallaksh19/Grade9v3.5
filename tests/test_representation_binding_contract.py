from __future__ import annotations

import copy
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools import render_core
from tools import staged_set_b_replay as replay


REPO = Path(__file__).resolve().parents[1]


def scene_validator() -> Draft202012Validator:
    schema = render_core.load_json(REPO / "Shared/library/package.schema.json")
    return Draft202012Validator({
        "$schema": schema["$schema"],
        "$ref": "#/$defs/scene_instance",
        "$defs": schema["$defs"],
    })


class RepresentationBindingContractTests(unittest.TestCase):
    def test_scene_instance_has_exactly_one_owner_binding(self):
        check = scene_validator()
        _, rep, _ = replay.adopt(replay.cases()[0])
        question_case = copy.deepcopy(rep["scene_instances"][0])
        self.assertEqual(list(check.iter_errors(question_case)), [])

        teaching_case = copy.deepcopy(question_case)
        teaching_case["microtopic_ref"] = "MIC-TEST"
        del teaching_case["question_ref"]
        self.assertEqual(list(check.iter_errors(teaching_case)), [])

        ambiguous = copy.deepcopy(question_case)
        ambiguous["microtopic_ref"] = "MIC-TEST"
        self.assertTrue(list(check.iter_errors(ambiguous)))

        ownerless = copy.deepcopy(question_case)
        del ownerless["question_ref"]
        self.assertTrue(list(check.iter_errors(ownerless)))

    def test_all_frozen_staged_question_instances_remain_schema_valid(self):
        check = scene_validator()
        for case in replay.cases():
            with self.subTest(issue=case["issue"]):
                _, rep, _ = replay.adopt(case)
                errors = list(check.iter_errors(rep["scene_instances"][0]))
                self.assertEqual(errors, [], [error.message for error in errors])

    def test_concept_correct_case_for_another_question_is_rejected(self):
        ctx = replay.context()
        q1 = ctx.bank[0]
        q2 = copy.deepcopy(q1)
        q2["id"] = "OTHER-QUESTION-SAME-TOPIC"
        # Keep the same representation and exact selected instance deliberately.
        output = render_core._core2_question_figures(ctx, q2)
        self.assertEqual(output, "")
        self.assertTrue(ctx.gaps)
        self.assertEqual(ctx.gaps[-1]["duty"], "MOUNT_REPRESENTATION")

    def test_wrong_owner_data_asset_and_role_all_fail_closed(self):
        for defect in ("owner", "datum", "asset", "role"):
            with self.subTest(defect=defect):
                ctx = replay.context()
                case = ctx.packages[0]["representations"][0]["scene_instances"][0]
                case.update({
                    "owner": {"question_ref": "WRONG"},
                    "datum": {"datum_refs": ["ABSENT"]},
                    "asset": {"asset_ref": "absent.svg"},
                    "role": {"cores": ["CORE1A"]},
                }[defect])
                output = render_core._core2_question_figures(ctx, ctx.bank[0])
                self.assertEqual(output, "")
                self.assertTrue(ctx.gaps)
                self.assertIn(ctx.gaps[-1]["duty"], {"MOUNT_REPRESENTATION", "BUILD_SCENE"})


if __name__ == "__main__":
    unittest.main()
