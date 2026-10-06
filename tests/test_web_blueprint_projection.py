from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import build_core_learning_data, core_template_contract
from Shared.tools.core_learning_projection_adapter import _web_delivery


REPO = Path(__file__).resolve().parents[1]


class WebBlueprintProjectionTests(unittest.TestCase):
    def test_projection_delivery_is_role_driven_and_subject_neutral(self):
        for core in core_template_contract.ROLE_ORDER:
            ref = core_template_contract.resolve_web_blueprint_for_core(core)["ref"]
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

    def test_committed_core_learning_data_matches_the_governed_generator(self):
        path = REPO / "public/core-learning/data.js"
        expected = build_core_learning_data.rendered_file()["public/core-learning/data.js"]
        self.assertEqual(
            path.read_bytes(),
            expected,
            "generated Core-learning data is stale; run python3 Shared/tools/build_manifest.py",
        )

    def test_generated_projection_blueprint_is_invariant_across_subject_rows(self):
        path = REPO / "public/core-learning/data.js"
        text = path.read_text(encoding="utf-8")
        marker = "window.GRADE9V3_CORE = "
        payload = json.loads(text[text.index(marker) + len(marker):].strip().rstrip(";"))
        refs_by_core = {}
        subjects_by_core = {}
        for row in payload["core_projections"]:
            core = row["projection"]["core"]
            ref = row["projection"]["delivery"]["web"]["blueprint_ref"]
            refs_by_core.setdefault(core, set()).add(ref)
            subjects_by_core.setdefault(core, set()).add(row.get("subject"))
        for core, refs in refs_by_core.items():
            self.assertEqual(
                len(refs),
                1,
                f"{core} must resolve one role-driven blueprint regardless of subject rows: {refs}",
            )
            expected = core_template_contract.resolve_web_blueprint_for_core(core)["ref"]
            self.assertEqual(next(iter(refs)), expected)
        self.assertTrue(any(len(subjects) > 1 for subjects in subjects_by_core.values()))


if __name__ == "__main__":
    unittest.main()
