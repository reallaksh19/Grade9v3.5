from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.contracts import ContractError
from Shared.tools import build_core_learning_data
from Shared.tools.core_learning_projection_adapter import _application

REPO = Path(__file__).resolve().parents[1]
MOTION = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
FAMILIAR = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
TRANSFER = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"
CONCEPT = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"


class CoreLearningProductionAdapter(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.payload = build_core_learning_data.build()
        cls.rows = cls.payload["core_projections"]
        cls.package = json.loads(MOTION.read_text(encoding="utf-8"))

    def row(self, *, core=None, source=None, concept=None):
        matches = [
            row for row in self.rows
            if (core is None or row["projection"]["core"] == core)
            and (source is None or row["source_ref"] == source)
            and (
                concept is None
                or (row["projection"].get("concept") or {}).get("microtopic_ref") == concept
            )
        ]
        self.assertEqual(len(matches), 1, [row["id"] for row in matches])
        return matches[0]

    def test_public_provider_is_compiler_backed_not_fixture_backed(self):
        self.assertEqual(self.payload["provider_status"], "PRODUCTION_COMPILED_CANONICAL")
        self.assertTrue(self.rows)
        self.assertFalse(any(row["id"].startswith("fixture:") for row in self.rows))
        self.assertEqual(
            self.payload["provider"]["mode"],
            "CANONICAL_LIBRARY_TO_COMPILE_BUCKET_TO_CORE_PROJECTION",
        )

    def test_core1_pair_shares_concept_but_changes_reveal_policy(self):
        a = self.row(core="CORE1A", concept=CONCEPT)
        b = self.row(core="CORE1B", concept=CONCEPT)
        self.assertEqual(a["projection"]["concept"]["microtopic_ref"], CONCEPT)
        self.assertEqual(a["projection"]["concept"]["inferential_jump"], b["projection"]["concept"]["inferential_jump"])
        self.assertFalse(a["projection"]["presentation"]["attempt_before_reveal"])
        self.assertTrue(a["projection"]["presentation"]["show_full_construction"])
        self.assertTrue(b["projection"]["presentation"]["attempt_before_reveal"])
        self.assertFalse(b["projection"]["presentation"]["show_full_construction"])
        self.assertTrue(b["projection"]["concept"]["elicitation"]["prompt"])

    def test_core2a_preserves_real_reasoning_crux_hints_and_scaffolds(self):
        row = self.row(core="CORE2A", source=FAMILIAR)
        source = next(q for q in self.package["questions"] if q["id"] == FAMILIAR)
        app = row["projection"]["application"]
        self.assertEqual(app["reasoning_route"], source["answer"]["reasoning_route"])
        self.assertEqual(app["crux_move_ref"], source["answer"]["crux_move_ref"])
        self.assertEqual(app["hints"], source["hints"])
        self.assertEqual(app["scaffolds"], source["scaffolds"])
        self.assertEqual(app["check"], source["answer"]["check"])
        for field in ("source_refs", "origin", "subparts", "options", "conditions", "figure_refs"):
            self.assertEqual(app[field], source[field])
        self.assertEqual(app["original_number"], source.get("original_identifier"))

    def test_compiled_question_parts_survive_without_rewriting(self):
        block = {
            "source_question_id": "Q-EXAMPLE",
            "family": "F-EXAMPLE",
            "stem": "Choose the valid relation.",
            "source_refs": ["SRC-EXAMPLE"],
            "origin": "ADAPTED",
            "original_number": "7(a)",
            "subparts": ["Find the first value.", "Explain the choice."],
            "options": ["A", "B"],
            "conditions": ["Assume a closed system."],
            "figure_refs": ["FIG-1"],
            "answer": {"reasoning_route": [], "check": "Check units."},
        }
        app = _application(block)
        for field in ("source_refs", "origin", "original_number", "subparts", "options", "conditions", "figure_refs"):
            self.assertEqual(app[field], block[field])

    def test_every_bucket_has_explicit_availability_or_finding(self):
        availability = self.payload["bucket_availability"]
        self.assertTrue(availability)
        self.assertEqual(len({(row["subject"], row["bucket_ref"]) for row in availability}), len(availability))
        self.assertEqual(
            {(row["subject"], row["bucket_ref"]) for row in self.payload["findings"]},
            {(row["subject"], row["bucket_ref"]) for row in availability if row["status"] == "UNSUPPORTED"},
        )
        for row in availability:
            self.assertIn(row["status"], {"AVAILABLE", "UNSUPPORTED"})
            if row["status"] == "AVAILABLE":
                self.assertTrue(row["projection_refs"])
                self.assertTrue(set(row["projection_refs"]).issubset({record["id"] for record in self.rows}))
            else:
                self.assertTrue(row["code"])
                self.assertEqual(row["projection_refs"], [])

    def test_compiler_error_is_reported_with_named_code(self):
        subject = next(name for name in build_core_learning_data.subjects() if name == "Physics")
        with patch.object(build_core_learning_data, "compile_bucket", side_effect=ContractError("BAD_SOURCE", "example")):
            rows, availability = build_core_learning_data._subject_rows(subject)
        self.assertEqual(rows, [])
        self.assertTrue(availability)
        self.assertTrue(all(row["status"] == "UNSUPPORTED" for row in availability))
        self.assertTrue(all(row["code"] == "BAD_SOURCE" for row in availability))

    def test_core2b_preserves_protected_transfer_without_scaffold_leak(self):
        row = self.row(core="CORE2B", source=TRANSFER)
        source = next(q for q in self.package["questions"] if q["id"] == TRANSFER)
        app = row["projection"]["application"]
        protected = source["transfer"]["protected_move_ref"]
        self.assertEqual(app["transfer"], source["transfer"])
        self.assertEqual(app["crux_move_ref"], protected)
        self.assertEqual(row["projection"]["presentation"]["protected_move_refs"], [protected])
        self.assertFalse(any(s["supports_move_ref"] == protected for s in app["scaffolds"]))

    def test_shared_clock_explorer_is_resolved_from_canonical_resource(self):
        row = self.row(core="CORE2A", source=FAMILIAR)
        self.assertEqual(
            row["explorer_locator"],
            "public/physics/motion-2d/explorers/shared-clock/index.html",
        )
        self.assertTrue((REPO / row["explorer_locator"]).is_file())

    def test_shared_tooling_has_no_motion_specific_identifier_switch(self):
        adapter = (REPO / "Shared/tools/core_learning_projection_adapter.py").read_text(encoding="utf-8")
        builder = (REPO / "Shared/tools/build_core_learning_data.py").read_text(encoding="utf-8")
        for forbidden in ("MIC-PHY-", "Q-PHY-", "BUCKET-PHY-", "motion2d", "Physics/library"):
            self.assertNotIn(forbidden, adapter)
            self.assertNotIn(forbidden, builder)


if __name__ == "__main__":
    unittest.main()
