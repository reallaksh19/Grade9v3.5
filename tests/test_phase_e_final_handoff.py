from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
EVIDENCE = REPO / "evidence/architectural-recovery/ISS69/phase-e-e03-final-handoff.v1.json"
GRAPH = REPO / "evidence/architectural-recovery/ISS69/phase-e-delp-execution-graph.v32.json"
MATRIX = REPO / "Shared/quality/question-demand-matrix.v1.json"
BLUEPRINTS = REPO / "Shared/web/interactive-page-blueprints.v1.json"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def git_blob_sha(path: Path) -> str:
    data = path.read_bytes()
    header = f"blob {len(data)}\0".encode("utf-8")
    return hashlib.sha1(header + data).hexdigest()


class PhaseEFinalHandoff(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evidence = load(EVIDENCE)
        cls.graph = load(GRAPH)
        cls.matrix = load(MATRIX)

    def test_v32_leaf_stays_bounded_and_declares_generated_manifest_surface(self):
        node = next(row for row in self.graph["nodes"] if row["ref"].endswith("#117"))
        self.assertEqual(node["responsibility_id"], "ISS69-E03-FINAL-HANDOFF")
        self.assertEqual(len(node["units"]), 5)
        total = sum(row["weight"] for row in node["units"])
        self.assertTrue(all(row["weight"] * 100 <= total * 40 for row in node["units"]))
        self.assertLessEqual(node["size_budget"]["target_loc"], 700)
        self.assertLessEqual(node["size_budget"]["hard_loc"], 1500)
        self.assertIn("docs/architecture-manifest.json", node["write_surface"])
        self.assertIn("tests/test_phase_e_final_handoff.py", node["write_surface"])

    def test_accepted_coverage_is_exactly_zero_of_the_canonical_28_cells(self):
        coverage = self.evidence["accepted_coverage"]
        demands = list(self.matrix["demands"])
        bands = list(self.matrix["band_policies"])
        expected = {f"{d}-{b}" for d in demands for b in bands}

        self.assertEqual(len(demands), 7)
        self.assertEqual(len(bands), 4)
        self.assertEqual(coverage["accepted_row_count"], 0)
        self.assertEqual(coverage["accepted_cell_count"], 0)
        self.assertEqual(coverage["unsupported_cell_count"], 28)
        self.assertEqual(coverage["coverage_fraction"], "0/28")
        self.assertEqual(coverage["accepted_rows"], [])
        self.assertEqual(coverage["accepted_cells"], [])
        self.assertEqual(
            {row["cell"] for row in coverage["unsupported_cells"]},
            expected,
        )
        self.assertTrue(all(
            row["status"] == "UNSUPPORTED_NO_CURRENT_INDEPENDENT_RENDERED_ACCEPTANCE"
            for row in coverage["unsupported_cells"]
        ))

    def test_current_e01_e02_and_phase_d_evidence_blobs_are_pinned_exactly(self):
        frontier = self.evidence["frontier"]
        pins = [
            (
                frontier["phase_d"]["evidence_path"],
                frontier["phase_d"]["evidence_blob"],
            ),
            (
                frontier["phase_e"]["e01"]["evidence_path"],
                frontier["phase_e"]["e01"]["evidence_blob"],
            ),
            (
                frontier["phase_e"]["e02"]["evidence_path"],
                frontier["phase_e"]["e02"]["evidence_blob"],
            ),
        ]
        for relative, expected in pins:
            with self.subTest(path=relative):
                self.assertEqual(git_blob_sha(REPO / relative), expected)

    def test_active_blueprints_and_legacy_migration_states_are_not_conflated(self):
        compat = self.evidence["compatibility_and_migration"]
        blueprints = load(BLUEPRINTS)["blueprints"]
        active = {
            f'{row["id"]}@{row["version"]}'
            for row in blueprints
            if row["status"] == "ACTIVE" and row["role"] in {"CORE1A", "CORE2"}
        }
        self.assertEqual(active, set(compat["current_blueprints"]))
        self.assertEqual(
            compat["legacy_blueprints"]["disposition"],
            "OBSERVABLE_COMPATIBILITY_NOT_CURRENT_AUTHORITY",
        )
        self.assertEqual(
            compat["generated_projection_migration"]["final_state"],
            "FRESH_ON_E02_EXACT_TREE",
        )
        self.assertEqual(
            compat["historical_classification_replay"]["state"],
            "REPLAY_REQUIRED_NONACCEPTING",
        )
        self.assertEqual(
            compat["rendered_review_receipt"]["disposition"],
            "REVIEW_STALE_DO_NOT_REUSE",
        )

    def test_frontier_preserves_application_and_returned_finding_boundaries(self):
        appendix = self.evidence["frontier"]["appendix_a"]
        self.assertEqual(appendix["technical_state"], "COMPLETE_BROWSER_PASS")
        self.assertEqual(appendix["promotion_release_state"], "SEPARATE_NOT_GRANTED")

        findings = self.evidence["frontier"]["returned_architecture_findings"]
        atlas = next(row for row in findings if row["issue"] == 125)
        self.assertTrue(atlas["responsibility_complete"])
        self.assertFalse(atlas["merge_release_granted"])
        self.assertEqual(
            atlas["validation"],
            "DEDICATED_BROWSER_AND_EXACT_TEST_ID_PASS",
        )

    def test_programme_task_result_is_responsibility_complete_without_release_claims(self):
        result = self.evidence["task_result"]
        self.assertEqual(result["RESULT_SCOPE"], "RESPONSIBILITY")
        self.assertEqual(result["COVERAGE"], "architectural recovery programme #69")
        self.assertEqual(result["RESPONSIBILITY_COMPLETE"], "YES")
        self.assertEqual(result["ACCEPTED_QRT_COVERAGE"], "0/28")

        non_grants = self.evidence["non_grants"]
        self.assertEqual(
            non_grants,
            {
                "merge_to_main": False,
                "golden_promotion": False,
                "learner_publication": False,
                "independent_academic_acceptance": False,
                "learning_effectiveness": False,
            },
        )

    def test_limitations_remain_explicit_instead_of_becoming_completion_claims(self):
        limitations = {row["id"]: row for row in self.evidence["limitations"]}
        self.assertEqual(limitations["UNSUPPORTED_QRT_COVERAGE"]["state"], "28_CELLS_UNSUPPORTED")
        self.assertEqual(limitations["INHERITED_REPOSITORY_DEBT"]["state"], "109_NOT_NEW")
        self.assertEqual(limitations["APPENDIX_A_PROMOTION"]["state"], "SEPARATE_NOT_GRANTED")
        self.assertEqual(limitations["OPEN_DRAFT_PRS"]["state"], "NOT_MERGED_BY_E03")
        self.assertEqual(
            limitations["INDEPENDENT_ACADEMIC_ACCEPTANCE"]["state"],
            "NOT_GRANTED",
        )


if __name__ == "__main__":
    unittest.main()
