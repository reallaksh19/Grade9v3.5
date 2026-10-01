from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.tools import core_template_contract, web_blueprint_contract

REPO = Path(__file__).resolve().parents[1]


class WebBlueprintContractTests(unittest.TestCase):
    def test_registry_is_structurally_sound_and_has_six_active_core_blueprints_and_the_explorers(self):
        report = web_blueprint_contract.audit_registry()
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["blueprints_checked"], 7)
        registry = web_blueprint_contract.load_registry()
        roles = sorted(role for row in registry["blueprints"] if row["status"] == "ACTIVE" for role in row["core_roles"])
        self.assertEqual(roles, ["CORE1", "CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B", "EXPLORER"])
        self.assertEqual(registry["shell"]["id"], "G9-TABLET-SHELL-V1")
        self.assertTrue(registry["shell"]["fixed_header"])

    def test_every_template_block_maps_to_exactly_one_blueprint_slot(self):
        contract = core_template_contract.load_contract()
        registry = web_blueprint_contract.load_registry()
        for role_name, role in contract["roles"].items():
            findings = web_blueprint_contract.validate_role_binding(role_name, role, registry)
            self.assertEqual(findings, [], f"{role_name}: {findings}")
            blueprint = web_blueprint_contract.resolve_blueprint(role["web_blueprint_ref"], registry)
            accepted = [
                block
                for slot in blueprint["slots"]
                for block in slot["accepts_blocks"]
            ]
            ordered = [block["id"] for block in role["ordered_blocks"]]
            self.assertEqual(set(ordered), set(accepted))
            self.assertEqual(len(accepted), len(set(accepted)))

    def test_unknown_or_stale_version_fails_closed(self):
        with self.assertRaisesRegex(
            web_blueprint_contract.WebBlueprintContractError,
            "WEB_BLUEPRINT_UNKNOWN",
        ):
            web_blueprint_contract.resolve_blueprint("BP-NOT-REAL@1.0.0")
        with self.assertRaisesRegex(
            web_blueprint_contract.WebBlueprintContractError,
            "WEB_BLUEPRINT_VERSION_UNSUPPORTED",
        ):
            web_blueprint_contract.resolve_blueprint("BP-CORE1-ORIENTATION@9.9.9")

    def test_incompatible_core_and_unmapped_block_are_named_findings(self):
        contract = core_template_contract.load_contract()
        registry = web_blueprint_contract.load_registry()
        role = copy.deepcopy(contract["roles"]["CORE1"])
        role["web_blueprint_ref"] = contract["roles"]["CORE2"]["web_blueprint_ref"]
        findings = web_blueprint_contract.validate_role_binding("CORE1", role, registry)
        points = {row["point"] for row in findings}
        self.assertIn("WEB_BLUEPRINT_CORE_INCOMPATIBLE", points)
        self.assertIn("WEB_BLUEPRINT_BLOCK_UNMAPPED", points)

    def test_schema_validates_registry_when_jsonschema_is_available(self):
        try:
            import jsonschema
        except ModuleNotFoundError:
            self.skipTest("jsonschema unavailable")
        schema = json.loads(
            (REPO / "Shared/web/interactive-page-blueprint.schema.json").read_text(encoding="utf-8")
        )
        registry = web_blueprint_contract.load_registry()
        jsonschema.Draft202012Validator(schema).validate(registry)


if __name__ == "__main__":
    unittest.main()
