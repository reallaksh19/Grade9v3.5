from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
LEDGER = REPO / "evidence/architectural-recovery/ISS69/phase-e-e01-authority-ledger.v1.json"
GRAPH = REPO / "evidence/architectural-recovery/ISS69/phase-e-delp-execution-graph.v32.json"
D06 = REPO / "evidence/architectural-recovery/ISS69/phase-d-d06-freeze-handoff.v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


class PhaseEAuthorityLedger(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ledger = load(LEDGER)
        cls.graph = load(GRAPH)
        cls.d06 = load(D06)

    def test_e01_phase_graph_is_bounded_and_dependency_ordered(self):
        graph = self.graph
        self.assertEqual(graph["schema"], "relay-v3.2-delp-execution-graph")
        programme = graph["programme"]
        self.assertEqual(programme["total_weight"], 400)
        self.assertEqual(
            programme["engineering_protocol_ref"],
            "reallaksh19/Common@46916f4828090c1f32cf2856186b0b00defdbea3:skills/engineering-pr-delivery-v3.2",
        )
        policy = programme["decomposition_policy"]
        self.assertEqual(policy["mode"], "ENFORCED")

        leaves = [row for row in graph["nodes"] if row["kind"] == "LEAF"]
        self.assertEqual(
            {row["ref"].split("#")[-1] for row in leaves},
            {"115", "116", "117"},
        )
        self.assertEqual(sum(row["weight"] for row in leaves), 400)

        refs = {row["ref"] for row in graph["nodes"]}
        surfaces: dict[str, str] = {}
        for row in leaves:
            with self.subTest(leaf=row["ref"]):
                units = row["units"]
                self.assertGreaterEqual(len(units), policy["units"]["min"])
                self.assertLessEqual(len(units), policy["units"]["max"])
                total = sum(unit["weight"] for unit in units)
                self.assertTrue(all(unit["weight"] * 100 <= total * policy["units"]["max_share_percent"] for unit in units))
                self.assertTrue(all(unit["outcome"].strip() and unit["verify"].strip() for unit in units))
                self.assertTrue(row["outcome"].strip())
                self.assertTrue(row["write_surface"])
                self.assertTrue(all(dep in refs for dep in row.get("depends_on", [])))
                for path in row["write_surface"]:
                    owner = surfaces.get(path)
                    self.assertIsNone(owner, f"write-surface collision: {path} already owned by {owner}")
                    surfaces[path] = row["ref"]

        e02 = next(row for row in leaves if row["ref"].endswith("#116"))
        e03 = next(row for row in leaves if row["ref"].endswith("#117"))
        self.assertEqual(e02["depends_on"], ["reallaksh19/Grade9v3.5#115"])
        self.assertEqual(
            set(e03["depends_on"]),
            {"reallaksh19/Grade9v3.5#115", "reallaksh19/Grade9v3.5#116"},
        )

    def test_recorded_authority_blobs_equal_repository_bytes(self):
        authority = self.ledger["authority_graph"]
        refs = [
            (authority["blueprint_registry"]["path"], authority["blueprint_registry"]["blob"]),
            (authority["package_schema"]["path"], authority["package_schema"]["blob"]),
            (authority["qrt"]["matrix_path"], authority["qrt"]["matrix_blob"]),
            (authority["qrt"]["templates_path"], authority["qrt"]["templates_blob"]),
            (authority["qrt"]["compiler_path"], authority["qrt"]["compiler_blob"]),
            (authority["qrt"]["difficulty_path"], authority["qrt"]["difficulty_blob"]),
            (authority["projection"]["renderer_path"], authority["projection"]["renderer_blob"]),
            (authority["projection"]["core2_projection_path"], authority["projection"]["core2_projection_blob"]),
            (authority["projection"]["learner_metadata_path"], authority["projection"]["learner_metadata_blob"]),
            (
                authority["review_and_adapter_contracts"]["qrt_pipeline_schema"]["path"],
                authority["review_and_adapter_contracts"]["qrt_pipeline_schema"]["blob"],
            ),
            (
                authority["review_and_adapter_contracts"]["adapter_schema"]["path"],
                authority["review_and_adapter_contracts"]["adapter_schema"]["blob"],
            ),
        ]
        for subject in authority["review_and_adapter_contracts"]["subjects"]:
            refs.extend([
                (subject["demand_adapter"]["path"], subject["demand_adapter"]["blob"]),
                (subject["core_contract"]["path"], subject["core_contract"]["blob"]),
            ])

        for rel, expected in refs:
            with self.subTest(path=rel):
                self.assertEqual(git_blob_sha(REPO / rel), expected)

    def test_blueprint_authority_is_unique_and_current(self):
        row = self.ledger["authority_graph"]["blueprint_registry"]
        registry = load(REPO / row["path"])
        self.assertEqual(registry["registry_version"], row["registry_version"])

        active = [
            bp for bp in registry["blueprints"]
            if bp["status"] == "ACTIVE" and any(role in {"CORE1A", "CORE2"} for role in bp["core_roles"])
        ]
        by_role: dict[str, list[dict]] = {"CORE1A": [], "CORE2": []}
        for bp in active:
            for role in bp["core_roles"]:
                if role in by_role:
                    by_role[role].append(bp)

        self.assertEqual(len(by_role["CORE1A"]), 1)
        self.assertEqual(len(by_role["CORE2"]), 1)
        self.assertEqual((by_role["CORE1A"][0]["id"], by_role["CORE1A"][0]["version"]), ("BP-CORE1A-CONSTRUCTION", "1.8.0"))
        self.assertEqual((by_role["CORE2"][0]["id"], by_role["CORE2"][0]["version"]), ("BP-CORE2-SOURCE-QUESTION", "1.11.0"))

    def test_qrt_authority_is_exactly_the_canonical_28_cells(self):
        qrt = self.ledger["authority_graph"]["qrt"]
        matrix = load(REPO / qrt["matrix_path"])
        generated = load(REPO / qrt["templates_path"])

        self.assertEqual(matrix["schema"], "question-demand-matrix/v1")
        self.assertEqual(tuple(matrix["demands"]), tuple(qrt["canonical_demands"]))
        ids = [row["template_id"] for row in generated["templates"]]
        expected = [
            f"QRT-{demand}-{band}"
            for demand in qrt["canonical_demands"]
            for band in qrt["canonical_bands"]
        ]
        self.assertEqual(ids, expected)
        self.assertEqual(len(ids), 28)
        self.assertFalse(any(template_id.startswith("TMPL-CHEM-G11-") for template_id in ids))

    def test_subject_specific_semantics_remain_outside_shared_authority(self):
        contracts = self.ledger["authority_graph"]["review_and_adapter_contracts"]
        self.assertEqual(
            contracts["boundary"],
            "SUBJECT_SEMANTICS_IN_ADAPTERS_AND_RECORDS_NOT_SHARED_SPECIAL_CASES",
        )
        subjects = {row["subject"] for row in contracts["subjects"]}
        self.assertEqual(subjects, {"Physics", "Mathematics", "Chemistry"})
        for subject in contracts["subjects"]:
            self.assertFalse(subject["demand_adapter"]["path"].startswith("Shared/"))
            self.assertFalse(subject["core_contract"]["path"].startswith("Shared/"))

        # D06 froze Phase D with no Shared production delta.
        self.assertEqual(self.d06["shared_production_files_changed"], [])

    def test_compatibility_classes_cannot_compete_with_current_authority(self):
        rows = {row["id"]: row for row in self.ledger["compatibility_ledger"]}
        self.assertEqual(rows["ACTIVE_CORE1A_1_8"]["class"], "CURRENT_AUTHORITY")
        self.assertEqual(rows["ACTIVE_CORE2_1_11"]["class"], "CURRENT_AUTHORITY")
        self.assertEqual(rows["LEGACY_STANDALONE_BLUEPRINTS"]["state"], "OBSERVABLE_NOT_AUTHORITY")
        self.assertEqual(rows["HISTORICAL_ALT_QRT_NAMESPACE"]["state"], "NONCANONICAL")
        self.assertEqual(rows["HISTORICAL_49_56_CLASSIFICATIONS"]["state"], "REPLAY_REQUIRED_NONACCEPTING")

        generated = rows["STALE_CORE_LEARNING_GENERATED_1_7"]
        self.assertEqual(generated["issue"], 108)
        self.assertEqual(generated["state"], "OPEN_BLOCKS_E02")
        self.assertEqual(generated["repair_authority"], "Shared/tools/build_manifest.py")
        self.assertEqual(generated["manual_edit"], "FORBIDDEN")
        self.assertEqual(
            set(generated["files"]),
            {"public/core-learning/data.js", "docs/core-learning/data.js"},
        )

    def test_phase_d_lineage_and_non_grants_are_imported_exactly(self):
        lineage = self.ledger["predecessor_lineage"]["phase_d"]
        d06_heads = {
            (row["phase"], row["pr"], row["head_sha"])
            for row in self.d06["child_prs"]
        }
        ledger_heads = {
            (row["phase"], row["pr"], row["head_sha"])
            for row in lineage["child_heads"]
        }
        self.assertEqual(ledger_heads, d06_heads)
        self.assertEqual(lineage["freeze_head_sha"], "c4da59c56be1e148b8dfdb22654d9fb5e1a08541")

        imported = self.ledger["phase_d_imported_facts"]
        self.assertEqual(imported["accepted_cells"], self.d06["acceptance_summary"]["accepted_cell_count"])
        self.assertEqual(imported["unsupported_cells"], self.d06["acceptance_summary"]["unsupported_cell_count"])
        self.assertFalse(imported["independent_acceptance_granted"])

        self.assertEqual(
            self.ledger["phase_e_gate_state"]["e02"],
            "BLOCKED_UNTIL_E01_AND_ISS108_GENERATED_FRESHNESS",
        )
        self.assertTrue(all(value is False for value in self.ledger["non_grants"].values()))


if __name__ == "__main__":
    unittest.main()
