#!/usr/bin/env python3
"""Independent source oracles and falsifiers for Issue #212 Atlas indexing.

The source-truth tests intentionally do not use the Issue #212 resolver. They pin the
canonical witness facts directly from matrices, library records, and the merged Issue
#211 Core projection builder. The resolver tests are the first red tests for #212.
"""
from __future__ import annotations

import copy
import importlib
import unittest
from pathlib import Path

from Shared.contracts import load
from Shared.library.resolve import build_index
from Shared.tools import build_core_learning_data, build_web_data

REPO = Path(__file__).resolve().parents[1]

MOTION_MATRIX = "MATRIX-PHY-KIN-2D-MOTION"
NLM_MATRIX = "MATRIX-PHY-NLM-FIRST-LAW"
MATH_MATRIX = "MATRIX-MATH-LINEAR-EQUATIONS"

MOTION_BUCKET = "BUCKET-PHY-KIN-2D-MOTION"
NLM_BUCKET = "BUCKET-PHY-NLM-FIRST-LAW"
MATH_BUCKET = "BUCKET-LINEAR-EQUATION"


def subject_records(subject: str) -> dict:
    packages = [load(path) for path in sorted((REPO / subject / "library").glob("*.json"))]
    return build_index(packages)


def matrix_board(subject: str, matrix_id: str) -> dict:
    for path in sorted((REPO / subject / "matrices").glob("*.rungs.json")):
        board = load(path)
        if board.get("matrix_id") == matrix_id:
            return board
    raise AssertionError(f"missing matrix {matrix_id}")


def rung(board: dict, label: str) -> dict:
    return next(row for row in board["rungs"] if row["rung"] == label)


def activity_refs(records: dict, capability_ref: str) -> list[str]:
    return sorted(
        row["id"]
        for row in records.values()
        if row.get("_collection") == "resources"
        and "ACTIVITY" in row.get("role", [])
        and capability_ref in row.get("supports_claims", [])
    )


def core_availability(core: dict, subject: str, bucket_ref: str) -> dict:
    return next(
        row
        for row in core["bucket_availability"]
        if row["subject"] == subject and row["bucket_ref"] == bucket_ref
    )


def core_projection_refs_for_microtopic(core: dict, microtopic_ref: str) -> list[str]:
    return sorted(
        row["id"]
        for row in core["core_projections"]
        if (row.get("projection") or {}).get("concept", {}).get("microtopic_ref") == microtopic_ref
    )


def subject_payload(subject: str) -> dict:
    return build_web_data.build()["subjects"][subject]


def atlas_resolver():
    try:
        return importlib.import_module("Shared.tools.atlas_index")
    except ModuleNotFoundError as exc:
        raise AssertionError(
            "Issue #212 resolver helper Shared.tools.atlas_index is not implemented"
        ) from exc


def build_subject_index(subject: str, boards: list[dict], records: dict, core: dict) -> dict:
    module = atlas_resolver()
    builder = getattr(module, "build_subject_index", None)
    if not callable(builder):
        raise AssertionError(
            "Issue #212 resolver must expose build_subject_index(subject, boards, records, core_payload)"
        )
    return builder(subject, boards, records, core)


def find_row(result: dict, matrix_id: str, rung_label: str) -> dict:
    return next(
        row
        for row in result["atlas_index"]
        if row["matrix_id"] == matrix_id and row["rung"] == rung_label
    )


class IndependentSourceOracleTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = subject_records("Physics")
        cls.math = subject_records("Mathematics")
        cls.core = build_core_learning_data.build()
        cls.motion = matrix_board("Physics", MOTION_MATRIX)
        cls.nlm = matrix_board("Physics", NLM_MATRIX)
        cls.linear = matrix_board("Mathematics", MATH_MATRIX)

    def test_motion_r1_positive_chain_is_source_derived(self):
        source = rung(self.motion, "R1")
        self.assertEqual(30, source["ladder_position"])
        self.assertTrue(source.get("default_entry_eligible", True))
        self.assertEqual(
            "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
            source["microtopic_ref"],
        )

        micro = self.physics[source["microtopic_ref"]]
        capability_ref = micro["primary_capability_ref"]
        capability = self.physics[capability_ref]

        self.assertEqual("CAP-KIN-2D-INDEPENDENT-COMPONENTS", capability_ref)
        self.assertEqual(
            ["K2D1-1", "K2D1-2", "K2D1-3", "K2D1-4"],
            [step["id"] for step in micro["teaching_path"]],
        )
        self.assertEqual(
            ["CAP-VECTOR-SIGNED-COMPONENT"],
            micro["prerequisite_refs"],
        )
        self.assertEqual(
            ["CAP-VECTOR-SIGNED-COMPONENT"],
            capability["prerequisite_refs"],
        )
        self.assertEqual(
            ["REP-KIN-2D-SHARED-CLOCK"],
            micro["representation_refs"],
        )
        self.assertEqual(
            ["ACT-KIN-2D-SHARED-CLOCK"],
            activity_refs(self.physics, capability_ref),
        )
        activity = self.physics["ACT-KIN-2D-SHARED-CLOCK"]
        self.assertEqual(
            "public/physics/motion-2d/explorers/shared-clock/index.html",
            activity["locator"],
        )
        gcdr = activity.get("extensions", {}).get("topic_atlas", {}).get("gcdr_contract", {})
        self.assertEqual("REPO_BUNDLE", gcdr.get("delivery_profile", {}).get("profile"))
        self.assertNotIn("portable_package_ref", activity)

        availability = core_availability(self.core, "Physics", MOTION_BUCKET)
        self.assertEqual("AVAILABLE", availability["status"])
        self.assertEqual(
            [
                "physics:mic-phy-kin-2d-independent-components:core1a",
                "physics:mic-phy-kin-2d-independent-components:core1b",
                "physics:q-phy-kin-2d-2a-horizontal-launch-04:core2a",
                "physics:q-phy-kin-2d-2b-projectile-validity-04:core2b",
            ],
            core_projection_refs_for_microtopic(
                self.core,
                "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
            ),
        )

    def test_nlm_r5_activity_does_not_create_representation_edge(self):
        source = rung(self.nlm, "R5")
        self.assertEqual(78, source["ladder_position"])
        self.assertTrue(source.get("default_entry_eligible", True))
        self.assertEqual("MIC-PHY-NLM-FRICTION", source["microtopic_ref"])

        micro = self.physics[source["microtopic_ref"]]
        capability_ref = micro["primary_capability_ref"]
        capability = self.physics[capability_ref]

        self.assertEqual("CAP-NLM-FRICTION", capability_ref)
        self.assertEqual(
            ["NLM5-1", "NLM5-2", "NLM5-3", "NLM5-4"],
            [step["id"] for step in micro["teaching_path"]],
        )
        self.assertEqual(["CAP-NLM-FBD-BODY-OWNERSHIP"], micro["prerequisite_refs"])
        self.assertEqual(["CAP-NLM-FBD-BODY-OWNERSHIP"], capability["prerequisite_refs"])
        self.assertEqual([], micro["representation_refs"])
        self.assertEqual(
            ["ACT-NLM-FRICTION-THRESHOLD"],
            activity_refs(self.physics, capability_ref),
        )
        activity = self.physics["ACT-NLM-FRICTION-THRESHOLD"]
        self.assertEqual(
            "public/physics/nlm/explorers/friction-threshold/index.html",
            activity["locator"],
        )
        self.assertNotIn("portable_package_ref", activity)

        representation = self.physics["REP-NLM-FRICTION-THRESHOLD"]
        self.assertEqual(
            ["ACT-NLM-FRICTION-THRESHOLD"],
            representation["interactive_resource_refs"],
        )
        self.assertNotIn(
            "REP-NLM-FRICTION-THRESHOLD",
            micro["representation_refs"],
            "The mapper must not infer an R5 representation from its activity.",
        )

        availability = core_availability(self.core, "Physics", NLM_BUCKET)
        self.assertEqual("UNSUPPORTED", availability["status"])
        self.assertEqual("PARENT_TRANSFER_PAIR_MISSING", availability["code"])
        self.assertEqual([], availability["projection_refs"])

    def test_math_r1_preserves_two_prerequisite_authorities(self):
        source = rung(self.linear, "R1")
        self.assertEqual(20, source["ladder_position"])
        self.assertTrue(source.get("default_entry_eligible", True))
        self.assertEqual("MIC-MATH-CONSTRAINT", source["microtopic_ref"])

        micro = self.math[source["microtopic_ref"]]
        capability_ref = micro["primary_capability_ref"]
        capability = self.math[capability_ref]

        self.assertEqual("CAP-MATH-SUBSTITUTE", capability_ref)
        self.assertEqual(["MC-1", "MC-2", "MC-3"], [step["id"] for step in micro["teaching_path"]])
        self.assertEqual(["CAP-MATH-SUBSTITUTE"], micro["prerequisite_refs"])
        self.assertEqual([], capability["prerequisite_refs"])
        self.assertEqual(["REP-MATH-NUMBER-LINE"], micro["representation_refs"])
        self.assertEqual([], activity_refs(self.math, capability_ref))

        representation = self.math["REP-MATH-NUMBER-LINE"]
        self.assertEqual([], representation.get("interactive_resource_refs", []))

        availability = core_availability(self.core, "Mathematics", MATH_BUCKET)
        self.assertEqual("UNSUPPORTED", availability["status"])
        self.assertEqual("CORE_ROLES_MISSING", availability["code"])
        self.assertEqual([], availability["projection_refs"])

    def test_nlm_r4_remains_explicit_nondefault(self):
        source = rung(self.nlm, "R4")
        self.assertEqual(100, source["ladder_position"])
        self.assertFalse(source["default_entry_eligible"])
        self.assertEqual("MIC-PHY-NLM-FRAME-CHOICE", source["microtopic_ref"])


class CurrentPayloadFailureSurfaceTest(unittest.TestCase):
    def test_subject_payload_has_versioned_atlas_index(self):
        physics = subject_payload("Physics")
        self.assertEqual("2.0", physics["atlas_index_contract_version"])
        self.assertIn("atlas_index", physics)
        self.assertIn("visual_targets", physics)

    def test_motion_r1_consumer_row_exposes_source_relations(self):
        physics = subject_payload("Physics")
        rows = physics["atlas_index"]
        row = next(
            item
            for item in rows
            if item["matrix_id"] == MOTION_MATRIX and item["rung"] == "R1"
        )
        self.assertEqual("MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS", row["microtopic_ref"])
        self.assertEqual("CAP-KIN-2D-INDEPENDENT-COMPONENTS", row["capability_ref"])
        self.assertEqual(["REP-KIN-2D-SHARED-CLOCK"], row["representation_refs"])
        self.assertEqual(["ACT-KIN-2D-SHARED-CLOCK"], row["activity_refs"])
        self.assertEqual(
            ["CAP-VECTOR-SIGNED-COMPONENT"],
            row["microtopic_prerequisite_refs"],
        )
        self.assertEqual(
            ["CAP-VECTOR-SIGNED-COMPONENT"],
            row["capability_prerequisite_refs"],
        )
        self.assertEqual("READY", row["availability"]["representation"])
        self.assertEqual("READY", row["availability"]["activity"])
        self.assertEqual("READY", row["availability"]["locator"])
        self.assertEqual("UNAVAILABLE", row["availability"]["portable_package"])
        self.assertEqual("UNAVAILABLE", row["availability"]["standalone"])
        target = physics["visual_targets"]["ACT-NLM-FRICTION-THRESHOLD"]
        self.assertIn(
            "REP-NLM-FRICTION-THRESHOLD",
            target["representation_refs"],
            "Resource provenance may name a representation without creating an R5 rung edge.",
        )
        self.assertEqual(
            "public/physics/nlm/explorers/friction-threshold/index.html",
            target["locator"],
        )
        self.assertIsNone(target["portable_package_ref"])
        target = physics["visual_targets"]["ACT-KIN-2D-SHARED-CLOCK"]
        self.assertEqual(
            ["REP-KIN-2D-SHARED-CLOCK"],
            target["representation_refs"],
        )
        self.assertEqual(
            "public/physics/motion-2d/explorers/shared-clock/index.html",
            target["locator"],
        )
        self.assertEqual("REPO_BUNDLE", target["delivery_profile"])
        self.assertIsNone(target["portable_package_ref"])
        self.assertEqual("READY", target["availability"]["locator"])
        self.assertEqual("UNAVAILABLE", target["availability"]["portable_package"])
        self.assertEqual("UNAVAILABLE", target["availability"]["standalone"])

    def test_math_r1_consumer_row_does_not_collapse_prerequisites(self):
        math = subject_payload("Mathematics")
        row = next(
            item
            for item in math["atlas_index"]
            if item["matrix_id"] == MATH_MATRIX and item["rung"] == "R1"
        )
        self.assertEqual(["CAP-MATH-SUBSTITUTE"], row["microtopic_prerequisite_refs"])
        self.assertEqual([], row["capability_prerequisite_refs"])
        self.assertEqual(["REP-MATH-NUMBER-LINE"], row["representation_refs"])
        self.assertEqual([], row["activity_refs"])
        self.assertEqual("READY", row["availability"]["representation"])
        self.assertEqual("UNAVAILABLE", row["availability"]["activity"])
        self.assertEqual("UNAVAILABLE", row["availability"]["locator"])
        self.assertEqual("UNAVAILABLE", row["availability"]["portable_package"])
        self.assertEqual("UNAVAILABLE", row["availability"]["standalone"])
        self.assertEqual("UNAVAILABLE", row["availability"]["locator"])
        self.assertEqual("UNAVAILABLE", row["availability"]["portable_package"])
        self.assertEqual("UNAVAILABLE", row["availability"]["standalone"])

    def test_nlm_r5_consumer_row_does_not_infer_representation(self):
        physics = subject_payload("Physics")
        row = next(
            item
            for item in physics["atlas_index"]
            if item["matrix_id"] == NLM_MATRIX and item["rung"] == "R5"
        )
        self.assertEqual([], row["representation_refs"])
        self.assertEqual(["ACT-NLM-FRICTION-THRESHOLD"], row["activity_refs"])
        self.assertEqual([], row["core_projection_refs"])
        self.assertEqual("UNAVAILABLE", row["availability"]["representation"])
        self.assertEqual("READY", row["availability"]["activity"])
        self.assertEqual("READY", row["availability"]["locator"])
        self.assertEqual("UNAVAILABLE", row["availability"]["portable_package"])
        self.assertEqual("UNAVAILABLE", row["availability"]["standalone"])


class ResolverAdversarialFalsifierTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = subject_records("Physics")
        cls.math = subject_records("Mathematics")
        cls.core = build_core_learning_data.build()
        cls.motion = matrix_board("Physics", MOTION_MATRIX)
        cls.nlm = matrix_board("Physics", NLM_MATRIX)
        cls.linear = matrix_board("Mathematics", MATH_MATRIX)

    def test_missing_microtopic_keeps_row_and_marks_invalid(self):
        board = copy.deepcopy(self.motion)
        rung(board, "R1")["microtopic_ref"] = "MIC-DOES-NOT-EXIST"

        result = build_subject_index("Physics", [board], self.physics, self.core)
        row = find_row(result, MOTION_MATRIX, "R1")

        self.assertEqual("MIC-DOES-NOT-EXIST", row["microtopic_ref"])
        self.assertEqual("INVALID", row["availability"]["mapping"])
        self.assertIn(
            "MICROTOPIC_REF_UNRESOLVED",
            [finding["code"] for finding in row["findings"]],
        )

    def test_unresolved_capability_keeps_declared_ref_visible(self):
        records = copy.deepcopy(self.physics)
        records["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"]["primary_capability_ref"] = (
            "CAP-DOES-NOT-EXIST"
        )

        result = build_subject_index("Physics", [self.motion], records, self.core)
        row = find_row(result, MOTION_MATRIX, "R1")

        self.assertEqual("CAP-DOES-NOT-EXIST", row["capability_ref"])
        self.assertEqual("INVALID", row["availability"]["mapping"])
        self.assertIn(
            "CAPABILITY_REF_UNRESOLVED",
            [finding["code"] for finding in row["findings"]],
        )

    def test_broken_representation_ref_is_not_reported_ready(self):
        records = copy.deepcopy(self.physics)
        records["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"]["representation_refs"] = [
            "REP-DOES-NOT-EXIST"
        ]

        result = build_subject_index("Physics", [self.motion], records, self.core)
        row = find_row(result, MOTION_MATRIX, "R1")

        self.assertEqual(["REP-DOES-NOT-EXIST"], row["representation_refs"])
        self.assertEqual("INVALID", row["availability"]["representation"])
        self.assertEqual("INVALID", row["availability"]["mapping"])

    def test_missing_activity_resource_does_not_erase_representation(self):
        records = copy.deepcopy(self.physics)
        records.pop("ACT-KIN-2D-SHARED-CLOCK")

        result = build_subject_index("Physics", [self.motion], records, self.core)
        row = find_row(result, MOTION_MATRIX, "R1")

        self.assertEqual(["REP-KIN-2D-SHARED-CLOCK"], row["representation_refs"])
        self.assertEqual("READY", row["availability"]["representation"])
        self.assertEqual("INVALID", row["availability"]["activity"])
        self.assertEqual("INVALID", row["availability"]["mapping"])

    def test_duplicate_composite_key_is_explicit_and_never_first_wins(self):
        duplicate = copy.deepcopy(self.motion)
        result = build_subject_index(
            "Physics",
            [self.motion, duplicate],
            self.physics,
            self.core,
        )

        duplicate_findings = [
            finding
            for finding in result["findings"]
            if finding["code"] == "ATLAS_DUPLICATE_KEY"
        ]
        self.assertTrue(duplicate_findings)
        duplicate_rows = [
            row
            for row in result["atlas_index"]
            if row["matrix_id"] == MOTION_MATRIX and row["rung"] == "R1"
        ]
        self.assertGreaterEqual(len(duplicate_rows), 2)
        self.assertTrue(
            all(row["availability"]["mapping"] == "INVALID" for row in duplicate_rows)
        )

    def test_nondefault_eligibility_is_preserved(self):
        result = build_subject_index("Physics", [self.nlm], self.physics, self.core)
        row = find_row(result, NLM_MATRIX, "R4")
        self.assertEqual(100, row["ladder_position"])
        self.assertFalse(row["default_entry_eligible"])

    def test_unsupported_core_is_explicit_not_fabricated(self):
        result = build_subject_index("Physics", [self.nlm], self.physics, self.core)
        row = find_row(result, NLM_MATRIX, "R5")

        self.assertEqual([], row["core_projection_refs"])
        self.assertEqual("UNAVAILABLE", row["availability"]["core"])
        self.assertIn(
            "CORE_PROJECTION_UNAVAILABLE",
            [finding["code"] for finding in row["findings"]],
        )

    def test_math_representation_without_activity_stays_asymmetric(self):
        result = build_subject_index("Mathematics", [self.linear], self.math, self.core)
        row = find_row(result, MATH_MATRIX, "R1")

        self.assertEqual(["REP-MATH-NUMBER-LINE"], row["representation_refs"])
        self.assertEqual([], row["activity_refs"])
        self.assertEqual("READY", row["availability"]["representation"])
        self.assertEqual("UNAVAILABLE", row["availability"]["activity"])

    def test_record_permutation_does_not_change_semantic_output(self):
        reversed_records = dict(reversed(list(self.physics.items())))

        normal = build_subject_index("Physics", [self.motion], self.physics, self.core)
        permuted = build_subject_index("Physics", [self.motion], reversed_records, self.core)

        self.assertEqual(normal, permuted)

    def test_every_source_rung_appears_once_in_authored_order(self):
        result = build_subject_index(
            "Physics",
            [self.motion, self.nlm],
            self.physics,
            self.core,
        )
        expected = [
            (board["matrix_id"], source["rung"])
            for board in (self.motion, self.nlm)
            for source in board["rungs"]
        ]
        observed = [(row["matrix_id"], row["rung"]) for row in result["atlas_index"]]

        self.assertEqual(expected, observed)
        self.assertEqual(len(observed), len(set(observed)))


if __name__ == "__main__":
    unittest.main()
