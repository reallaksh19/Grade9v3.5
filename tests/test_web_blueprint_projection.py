from __future__ import annotations

import unittest

from Shared.tools import core_template_contract
from Shared.tools.core_learning_projection_adapter import _web_delivery


class WebBlueprintProjectionTests(unittest.TestCase):
    def test_projection_delivery_is_role_driven_and_subject_neutral(self):
        expected = {
            "CORE1": "BP-CORE1-ORIENTATION@1.0.0",
            "CORE2": "BP-CORE2-SOURCE-QUESTION@1.0.0",
            "CORE1A": "BP-CORE1A-CONSTRUCTION@1.0.0",
            "CORE1B": "BP-CORE1B-RECONSTRUCTION@1.0.0",
            "CORE2A": "BP-CORE2A-SUPPORTED-APPLICATION@1.0.0",
            "CORE2B": "BP-CORE2B-TRANSFER@1.0.0",
        }
        for core, ref in expected.items():
            delivery = _web_delivery(core)
            self.assertEqual(delivery["blueprint_ref"], ref)
            self.assertEqual(delivery["shell_ref"], "G9-TABLET-SHELL-V1")
            self.assertGreaterEqual(delivery["touch_policy"]["minimum_target_css_px"], 48)
            self.assertEqual(
                set(delivery["packaging_modes"]),
                {"PUBLIC", "PAGES", "OFFLINE_DIRECTORY", "SINGLE_FILE", "EMBED"},
            )

    def test_adapter_has_no_subject_or_keyword_blueprint_switch(self):
        for core in core_template_contract.ROLE_ORDER:
            blueprint = core_template_contract.resolve_web_blueprint_for_core(core)
            self.assertIn(core, blueprint["core_roles"])


if __name__ == "__main__":
    unittest.main()
