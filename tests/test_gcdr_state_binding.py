#!/usr/bin/env python3
"""Regression tests for governed GCDR external-state bindings."""
from __future__ import annotations

import math
import unittest

from Shared.tools.gcdr_state_binding import resolve_external_state


def contract(policy="EXACT_OR_CONSTRAINT_FAITHFUL"):
    return {
        "external_state_mapping": policy,
        "external_state_bindings": [
            {
                "id": "G",
                "source_pointer": "/parameters/g",
                "target_state_path": "physics.gravity",
                "control_id": "g",
                "required_for_exact": True,
                "source_unit": "m/s^2",
                "target_unit": "m/s^2",
                "transform": "IDENTITY",
                "transform_note": None,
                "missing_behavior": "LEAVE_UNSPECIFIED",
            },
            {
                "id": "THETA",
                "source_pointer": "/launch/theta_deg",
                "target_state_path": "launch.theta_rad",
                "control_id": "theta",
                "required_for_exact": True,
                "source_unit": "deg",
                "target_unit": "rad",
                "transform": "DEGREES_TO_RADIANS",
                "transform_note": None,
                "missing_behavior": "LEAVE_UNSPECIFIED",
            },
        ],
    }


class GCDRStateBindingTest(unittest.TestCase):
    def test_all_required_values_produce_exact_mapping(self):
        result = resolve_external_state(
            contract(),
            {"parameters": {"g": 9.8}, "launch": {"theta_deg": 30}},
        )
        self.assertEqual(result["fidelity"], "EXACT")
        self.assertEqual(result["loaded_state"]["physics.gravity"], 9.8)
        self.assertAlmostEqual(result["loaded_state"]["launch.theta_rad"], math.pi / 6)

    def test_missing_required_value_is_constraint_faithful_without_default(self):
        result = resolve_external_state(contract(), {"parameters": {"g": 10}})
        self.assertEqual(result["fidelity"], "CONSTRAINT_FAITHFUL")
        self.assertEqual(result["loaded_state"], {"physics.gravity": 10})
        self.assertIn("THETA", result["missing_bindings"])
        self.assertNotIn("launch.theta_rad", result["loaded_state"])

    def test_exact_required_fails_closed_when_required_value_missing(self):
        result = resolve_external_state(
            contract("EXACT_REQUIRED"),
            {"parameters": {"g": 10}},
        )
        self.assertEqual(result["fidelity"], "UNAVAILABLE")
        self.assertEqual(result["loaded_state"], {})

    def test_concept_mapping_can_fall_back_without_inventing_state(self):
        result = resolve_external_state(
            contract("CONCEPT_MAPPING_ALLOWED"),
            {"unrelated": True},
        )
        self.assertEqual(result["fidelity"], "CONCEPT_ONLY")
        self.assertEqual(result["loaded_state"], {})

    def test_custom_transform_requires_subject_adapter(self):
        c = contract()
        c["external_state_bindings"][0]["transform"] = "CUSTOM_DECLARED"
        c["external_state_bindings"][0]["transform_note"] = "Use the subject-owned conversion adapter."
        result = resolve_external_state(
            c,
            {"parameters": {"g": 9.8}, "launch": {"theta_deg": 30}},
        )
        self.assertEqual(result["fidelity"], "CONSTRAINT_FAITHFUL")
        self.assertNotIn("physics.gravity", result["loaded_state"])
        self.assertTrue(any("subject adapter" in x for x in result["reasons"]))

    def test_not_applicable_returns_unavailable(self):
        c = contract("NOT_APPLICABLE")
        c["external_state_bindings"] = []
        result = resolve_external_state(c, {"parameters": {"g": 9.8}})
        self.assertEqual(result["fidelity"], "UNAVAILABLE")
        self.assertEqual(result["loaded_state"], {})


if __name__ == "__main__":
    unittest.main()
