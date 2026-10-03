import json
import unittest
from pathlib import Path

from Shared.tools import quality_contract


REPO = Path(__file__).resolve().parents[1]


class AuthoringApplicabilityTests(unittest.TestCase):
    def setUp(self):
        self.registry = json.loads(
            (REPO / "Shared/web/interactive-page-blueprints.v1.json").read_text(encoding="utf-8")
        )

    def _blueprint(self, blueprint_id):
        return next(row for row in self.registry["blueprints"] if row["id"] == blueprint_id)

    def test_core1a_staged_visual_is_expected_not_required(self):
        bp = self._blueprint("BP-CORE1A-CONSTRUCTION")
        visual = next(c for c in bp["components"] if c["id"] == "STAGED_VISUAL")
        self.assertEqual(visual["level"], "EXPECTED")
        self.assertIn("not applicable", visual["authoring"]["hint"].lower())
        self.assertIn("reference depth", visual["authoring"]["hint"].lower())

    def test_core1a_missing_visual_still_fails_without_waiver(self):
        unit = {
            "figures": [],
            "waived": {},
            "construction_units": ["CU-1"],
            "representation_refs_unmounted": [],
        }
        check = {
            "min": 1,
            "stages": ["TEACHING", "PRE_ATTEMPT"],
            "waiver_component": "STAGED_VISUAL",
        }
        problems = quality_contract.OPS["figures_min"](unit, check, {})
        self.assertTrue(problems)

    def test_core1a_explicit_per_unit_visual_waiver_is_not_a_figure_failure(self):
        unit = {
            "figures": [],
            "waived": {"STAGED_VISUAL@CU-1": "symbolic comparison is the representation"},
            "construction_units": ["CU-1"],
            "representation_refs_unmounted": [],
        }
        check = {
            "min": 1,
            "stages": ["TEACHING", "PRE_ATTEMPT"],
            "waiver_component": "STAGED_VISUAL",
        }
        self.assertEqual(quality_contract.OPS["figures_min"](unit, check, {}), [])

    def test_core1a_blueprint_expected_component_accepts_scoped_waiver(self):
        page = {
            "role": "CORE1A",
            "blueprint_ref": "BP-CORE1A-CONSTRUCTION@1.4.0",
            "units": [{
                "id": "MIC",
                "construction_units": ["CU-1"],
                "components": [],
                "metadata": [],
                "waived": {"STAGED_VISUAL@CU-1": "no useful spatial representation"},
            }],
        }
        problems = quality_contract.OPS["blueprint_components"](
            page, {"level": "EXPECTED"}, {"contract": quality_contract.contract()}
        )
        self.assertNotIn("MIC / CU-1: STAGED_VISUAL is absent", problems)

    def test_core2_guidance_uses_applicability_not_mandatory_diagram_or_hint_count(self):
        bp = self._blueprint("BP-CORE2-SOURCE-QUESTION")
        rep = next(c for c in bp["components"] if "figure_refs" in (c.get("source") or []))
        ladder = next(c for c in bp["components"] if "scaffolds" in (c.get("source") or []))
        self.assertNotIn("every question gets one", rep["authoring"]["hint"].lower())
        self.assertIn("applicability", rep["authoring"]["hint"].lower())
        self.assertIn("reference depth", ladder["authoring"]["hint"].lower())
        self.assertIn("never create filler", ladder["authoring"]["hint"].lower())


if __name__ == "__main__":
    unittest.main()
