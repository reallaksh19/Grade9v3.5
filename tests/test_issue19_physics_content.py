"""Issue #19 Physics first-slice content integrity tests.

These tests deliberately exercise only subject content. They do not add a second routing
architecture; they prove that the existing matrix -> microtopic -> capability -> prerequisite
and question -> capability contracts close for the migrated slice.
"""
from __future__ import annotations

import importlib.util
import json
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
LIB = REPO / "Physics/library"
MATRICES = REPO / "Physics/matrices"

SLICE_PACKAGES = {
    "phy-kin-1d-motion.v1.json",
    "phy-nlm-first-law.v1.json",
    "phy-work-energy-power.v1.json",
    "phy-sound.v1.json",
    "phy-simple-machines.v1.json",
}
SLICE_MATRICES = {
    "phy-kin-1d-motion.rungs.json",
    "phy-nlm-first-law.rungs.json",
    "phy-work-energy-power.rungs.json",
    "phy-sound.rungs.json",
    "phy-simple-machines.rungs.json",
}

KIN_EXT = {
    "CAP-KIN-AVERAGE-RATES",
    "CAP-KIN-MOTION-GRAPHS",
    "CAP-KIN-CONSTANT-ACCELERATION",
    "CAP-KIN-UNIFORM-CIRCULAR-MOTION",
}
NLM_EXT = {"CAP-NLM-FRICTION", "CAP-NLM-SECOND-LAW", "CAP-NLM-THIRD-LAW"}
WEP_EXT = {
    "CAP-WEP-POWER-RATES",
    "CAP-WEP-ENERGY-DERIVATIONS",
    "CAP-WEP-GRADE9-QUANT",
}
SOUND_EXT = {
    "CAP-SOUND-SOURCE-MEDIUM",
    "CAP-SOUND-LONGITUDINAL",
    "CAP-SOUND-WAVE-QUANTITIES",
    "CAP-SOUND-PERCEPTION",
    "CAP-SOUND-REFLECTION",
}
MACHINE_EXT = {
    "CAP-MACHINE-TRADEOFF",
    "CAP-MACHINE-MA",
    "CAP-MACHINE-COMPARE",
}
ALL_EXT = KIN_EXT | NLM_EXT | WEP_EXT | SOUND_EXT | MACHINE_EXT


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def physics_records():
    records = {}
    packages = {}
    for path in sorted(LIB.glob("*.json")):
        package = load_json(path)
        packages[path.name] = package
        for collection, rows in package.items():
            if not isinstance(rows, list):
                continue
            for row in rows:
                if isinstance(row, dict) and row.get("id"):
                    records[row["id"]] = {
                        **row,
                        "_collection": collection,
                        "_package_file": path.name,
                    }
    return records, packages


class Issue19PhysicsFirstSlice(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.records, cls.packages = physics_records()

    def test_matrix_to_microtopic_to_capability_closure(self):
        for name in SLICE_MATRICES:
            matrix = load_json(MATRICES / name)
            last = -1
            for rung in matrix["rungs"]:
                self.assertGreater(rung["ladder_position"], last, name)
                last = rung["ladder_position"]
                self.assertEqual(rung["provenance"], "AUTHORED", (name, rung["rung"]))
                microtopic = self.records.get(rung.get("microtopic_ref"))
                self.assertIsNotNone(microtopic, (name, rung))
                self.assertEqual(microtopic["_collection"], "microtopics")
                capability = self.records.get(microtopic["primary_capability_ref"])
                self.assertIsNotNone(capability, microtopic["id"])
                self.assertEqual(capability["_collection"], "capabilities")

    def test_capability_prerequisites_resolve_and_are_acyclic(self):
        caps = {
            rid: row for rid, row in self.records.items()
            if row["_collection"] == "capabilities"
        }
        for rid, row in caps.items():
            for prereq in row.get("prerequisite_refs", []):
                self.assertIn(prereq, caps, (rid, prereq))

        visiting, done = set(), set()

        def visit(rid, stack):
            if rid in done:
                return
            self.assertNotIn(rid, visiting, " -> ".join(stack + [rid]))
            visiting.add(rid)
            for prereq in caps[rid].get("prerequisite_refs", []):
                visit(prereq, stack + [rid])
            visiting.remove(rid)
            done.add(rid)

        for rid in caps:
            visit(rid, [])

    def test_prerequisite_edges_are_explicit_and_minimal(self):
        self.assertEqual(
            self.records["CAP-KIN-MOTION-GRAPHS"]["prerequisite_refs"],
            ["CAP-KIN-AVERAGE-RATES"],
        )
        self.assertEqual(
            self.records["CAP-KIN-CONSTANT-ACCELERATION"]["prerequisite_refs"],
            ["CAP-KIN-MOTION-GRAPHS"],
        )
        self.assertEqual(
            self.records["CAP-KIN-UNIFORM-CIRCULAR-MOTION"]["prerequisite_refs"],
            [],
        )
        self.assertEqual(
            self.records["CAP-NLM-FBD-BODY-OWNERSHIP"]["prerequisite_refs"],
            [],
        )
        for cap_id in ("CAP-NLM-FRICTION", "CAP-NLM-SECOND-LAW", "CAP-NLM-THIRD-LAW"):
            self.assertEqual(
                self.records[cap_id]["prerequisite_refs"],
                ["CAP-NLM-FBD-BODY-OWNERSHIP"],
            )
        self.assertEqual(
            self.records["CAP-WEP-WORK-DIRECTION"]["prerequisite_refs"],
            [],
        )
        self.assertEqual(
            self.records["CAP-WEP-POWER-RATES"]["prerequisite_refs"],
            ["CAP-WEP-WORK-DIRECTION"],
        )
        self.assertEqual(
            self.records["CAP-WEP-GRADE9-QUANT"]["prerequisite_refs"],
            ["CAP-WEP-MECH-ENERGY-CONDITION"],
        )
        self.assertEqual(
            self.records["CAP-WEP-ENERGY-DERIVATIONS"]["prerequisite_refs"],
            [
                "CAP-WEP-WORK-DIRECTION",
                "CAP-NLM-SECOND-LAW",
                "CAP-KIN-CONSTANT-ACCELERATION",
            ],
        )
        self.assertEqual(
            self.records["CAP-MACHINE-TRADEOFF"]["prerequisite_refs"],
            ["CAP-WEP-WORK-DIRECTION"],
        )

    def test_questions_resolve_and_belong_to_bucket_through_primary_capability(self):
        cap_buckets = {}
        for row in self.records.values():
            if row["_collection"] != "microtopics":
                continue
            cap_buckets.setdefault(row["primary_capability_ref"], set()).add(row["bucket_id"])

        for name in SLICE_PACKAGES:
            package = self.packages[name]
            bucket = package["buckets"][0]["id"]
            for question in package.get("questions", []):
                primary = question["primary_capability_ref"]
                self.assertIn(primary, self.records, question["id"])
                self.assertEqual(self.records[primary]["_collection"], "capabilities")
                self.assertEqual(cap_buckets.get(primary), {bucket}, question["id"])
                for secondary in question.get("secondary_capability_refs", []):
                    self.assertIn(secondary, self.records, (question["id"], secondary))
                    self.assertEqual(self.records[secondary]["_collection"], "capabilities")

    def test_sparse_secondary_capability_examples_are_preserved(self):
        expected = {
            "Q-PHY-KIN-2A-COV-05": (
                "CAP-KIN-MOTION-GRAPHS",
                ["CAP-KIN-ZERO-V-NONZERO-A"],
            ),
            "Q-PHY-KIN-PRACTICAL-13": (
                "CAP-KIN-MOTION-GRAPHS",
                ["CAP-KIN-CONSTANT-ACCELERATION"],
            ),
            "Q-PHY-WEP-PRACTICAL-09": (
                "CAP-WEP-GRADE9-QUANT",
                ["CAP-WEP-MECH-ENERGY-CONDITION", "CAP-WEP-ENERGY-DERIVATIONS"],
            ),
            "Q-PHY-SOUND-2A-01": (
                "CAP-SOUND-WAVE-QUANTITIES",
                ["CAP-SOUND-PERCEPTION"],
            ),
            "Q-PHY-MACHINE-2A-01": (
                "CAP-MACHINE-MA",
                ["CAP-MACHINE-TRADEOFF"],
            ),
            "Q-PHY-NLM-PRACTICAL-12": (
                "CAP-NLM-SECOND-LAW",
                ["CAP-NLM-FBD-BODY-OWNERSHIP"],
            ),
        }
        for qid, (primary, secondary) in expected.items():
            q = self.records[qid]
            self.assertEqual(q["primary_capability_ref"], primary)
            self.assertEqual(q["secondary_capability_refs"], secondary)
        for name in SLICE_PACKAGES:
            for q in self.packages[name].get("questions", []):
                self.assertLessEqual(len(q.get("secondary_capability_refs", [])), 2, q["id"])

    def test_owner_extensions_do_not_claim_curriculum_authority(self):
        for cap_id in ALL_EXT:
            cap = self.records[cap_id]
            self.assertEqual(cap["status"], "CANDIDATE")
            self.assertEqual(cap["curriculum_mappings"], [])
            self.assertEqual(cap["extensions"].get("issue19:scope_class"), "OWNER_EXTENSION")
            self.assertEqual(cap["extensions"].get("issue19:donor"), "PR9")

        for name in SLICE_PACKAGES:
            bucket = self.packages[name]["buckets"][0]
            self.assertEqual(bucket["curriculum_mappings"], [])
            self.assertEqual(
                bucket["extensions"].get("issue19:scope_class"), "OWNER_EXTENSION"
            )

        gate = load_json(REPO / "Physics/gates/foundational-relations.v1.json")
        grade9_gates = [
            row for row in gate["gates"]
            if row["curriculum"]["grade"] == 9
        ]
        grade9_gate_ids = {row["gate_id"] for row in grade9_gates}
        grade9_owner_extension_ids = {
            row["gate_id"] for row in grade9_gates
            if row["curriculum"]["scope_class"] == "OWNER_EXTENSION"
        }
        self.assertEqual(grade9_gate_ids, grade9_owner_extension_ids)
        self.assertIn(
            "PHY-KIN-CIRCULAR-DYNAMICS-EXTENSION",
            grade9_owner_extension_ids,
        )
        for row in gate["gates"]:
            self.assertEqual(row["curriculum"]["scope_class"], "OWNER_EXTENSION")

    def test_authored_questions_do_not_manufacture_source_custody(self):
        for name in SLICE_PACKAGES:
            package = self.packages[name]
            authored_resources = {
                row["id"] for row in package.get("resources", [])
                if row.get("origin") == "AUTHORED"
            }
            for q in package.get("questions", []):
                self.assertEqual(q["status"], "CANDIDATE", q["id"])
                self.assertEqual(q["origin"], "AUTHORED", q["id"])
                self.assertIn(q["origin_ref"], authored_resources, q["id"])
                self.assertIn(q["origin_ref"], q["source_refs"], q["id"])

    def test_gate_validators_exist_in_contract_and_implementation(self):
        required = {
            "AVERAGE_RATE",
            "AVERAGE_POWER",
            "INSTANTANEOUS_POWER",
            "CONSTANT_ACCELERATION_DISPLACEMENT",
            "CONSTANT_ACCELERATION_NO_TIME",
            "NEWTON_SECOND_LAW",
            "WORK_CONSTANT_FORCE",
            "KINETIC_ENERGY",
            "GRAVITATIONAL_POTENTIAL_ENERGY",
            "AVERAGE_ACCELERATION",
            "UNIFORM_CIRCULAR_SPEED",
            "CONSTANT_ACCELERATION_GRAPH_AREA",
            "WAVE_SPEED",
            "FREQUENCY_PERIOD",
            "ECHO_DISTANCE",
            "MECHANICAL_ADVANTAGE",
        }
        contract = load_json(REPO / "Physics/adapter/CoreContracts.json")
        declared = {row["id"] for row in contract["validator_catalogue"]}
        self.assertTrue(required <= declared, sorted(required - declared))

        spec = importlib.util.spec_from_file_location(
            "physics_validator", REPO / "Physics/adapter/validator.py"
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        spec.loader.exec_module(module)
        self.assertTrue(required <= module.VALIDATORS, sorted(required - module.VALIDATORS))

    def test_practice_only_donor_anchors_trace_to_existing_rungs(self):
        expected = {
            "Q-PHY-GRAV-2A-01": (
                "CAP-PHY-GRAV-R1",
                "MIC-PHY-GRAV-R1",
                "Physics/matrices/phy-grav-universal-law.rungs.json",
            ),
            "Q-PHY-VECOPS-2A-01": (
                "CAP-VEC-SUB-ORDER",
                "MIC-PHY-VEC-SUB-ORDER",
                "Physics/matrices/phy-vec-add-sub.rungs.json",
            ),
            "Q-PHY-VECREP-2A-01": (
                "CAP-VECTOR-VS-SCALAR",
                "MIC-VECTOR-VS-SCALAR",
                "Physics/matrices/vector-representation.rungs.json",
            ),
        }
        for question_id, (capability_id, microtopic_id, matrix_path) in expected.items():
            question = self.records[question_id]
            self.assertEqual(question["primary_capability_ref"], capability_id)
            self.assertEqual(question["origin"], "AUTHORED")
            self.assertEqual(question["status"], "CANDIDATE")
            microtopic = self.records[microtopic_id]
            self.assertEqual(microtopic["primary_capability_ref"], capability_id)
            matrix = load_json(REPO / matrix_path)
            self.assertTrue(
                any(row.get("microtopic_ref") == microtopic_id for row in matrix["rungs"]),
                (question_id, microtopic_id),
            )

    def test_teaching_routes_reference_real_microtopics(self):
        for name in SLICE_PACKAGES:
            package = self.packages[name]
            for route in package.get("teaching_routes", []):
                for ref in route.get("microtopic_refs", []):
                    row = self.records.get(ref)
                    self.assertIsNotNone(row, (route["id"], ref))
                    self.assertEqual(row["_collection"], "microtopics")


if __name__ == "__main__":
    unittest.main()
