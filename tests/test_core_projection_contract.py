"""Contract-only falsifiers for the six-Core structured projection migration.

STEP-TA10-001 deliberately changes role/schema vocabulary only. Cross-record semantic
resolution belongs to STEP-TA10-002; these tests prove the schema can express the
contract without invalidating legacy packages or conflating source hints with authored
scaffolds.
"""
from __future__ import annotations

import json
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
SCHEMA = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))


class CoreProjectionContract(unittest.TestCase):
    def test_reasoning_move_contract_is_stable_and_decision_capable(self):
        move = SCHEMA["$defs"]["reasoning_move"]
        self.assertEqual(
            move["properties"]["kind"]["enum"],
            ["REPRESENT", "DECIDE", "CONNECT", "TRANSFORM", "VERIFY"],
        )
        self.assertEqual(
            move["required"],
            ["id", "kind", "action", "why_valid", "inputs", "output"],
        )
        self.assertEqual(
            move["dependentRequired"],
            {
                "representation_ref": ["visual_stage_ref"],
                "visual_stage_ref": ["representation_ref"],
            },
        )

    def test_reasoning_visual_binding_is_atomic(self):
        validator = Draft202012Validator(SCHEMA["$defs"]["reasoning_move"])
        base = {
            "id": "MOVE-1",
            "kind": "DECIDE",
            "action": "Choose the physically valid model.",
            "why_valid": "The state determines which relation applies.",
            "inputs": ["state"],
            "output": "selected model",
        }
        self.assertEqual([], list(validator.iter_errors(base)))
        broken = {**base, "representation_ref": "REP-1"}
        self.assertTrue(list(validator.iter_errors(broken)))

    def test_scaffold_is_separate_from_source_hint_and_targets_a_move(self):
        question = SCHEMA["$defs"]["question"]["properties"]
        self.assertIn("hints", question)
        self.assertIn("scaffolds", question)
        self.assertNotEqual(question["hints"], question["scaffolds"])

        scaffold = SCHEMA["$defs"]["scaffold"]
        self.assertEqual(
            scaffold["required"],
            ["text", "support_kind", "reveals", "supports_move_ref"],
        )
        self.assertEqual(
            scaffold["properties"]["support_kind"]["enum"],
            ["REPRESENT", "CONNECT", "EXECUTE"],
        )

    def test_scaffold_visual_binding_is_atomic(self):
        validator = Draft202012Validator(SCHEMA["$defs"]["scaffold"])
        base = {
            "text": "Choose axes before resolving forces.",
            "support_kind": "REPRESENT",
            "reveals": "CONCEPT",
            "supports_move_ref": "MOVE-1",
        }
        self.assertEqual([], list(validator.iter_errors(base)))
        broken = {**base, "visual_stage_ref": "VIS-1"}
        self.assertTrue(list(validator.iter_errors(broken)))

    def test_structured_application_fields_are_optional_legacy_migration_fields(self):
        answer = SCHEMA["$defs"]["answer"]
        self.assertIn("reasoning_route", answer["properties"])
        self.assertIn("crux_move_ref", answer["properties"])
        self.assertNotIn("reasoning_route", answer["required"])
        self.assertNotIn("crux_move_ref", answer["required"])
        self.assertIn("difficult_move", answer["properties"])

        transfer = SCHEMA["$defs"]["question"]["properties"]["transfer"]["properties"]
        self.assertIn("protected_move_ref", transfer)
        transfer_required = SCHEMA["$defs"]["question"]["properties"]["transfer"]["required"]
        self.assertNotIn("protected_move_ref", transfer_required)

    def test_roles_define_crux_and_source_custody_without_new_academic_authority(self):
        core2 = (REPO / "Shared/roles/CORE2.md").read_text(encoding="utf-8")
        core2a = (REPO / "Shared/roles/CORE2A.md").read_text(encoding="utf-8")
        core2b = (REPO / "Shared/roles/CORE2B.md").read_text(encoding="utf-8")
        readme = (REPO / "Shared/roles/README.md").read_text(encoding="utf-8")

        self.assertIn("hints", core2)
        self.assertIn("scaffold", core2a.lower())
        self.assertIn("crux", core2a.lower())
        self.assertIn("protected", core2b.lower())
        self.assertIn("microtopic.inferential_jump", readme.lower())
        self.assertIn("application", readme.lower())


if __name__ == "__main__":
    unittest.main()
