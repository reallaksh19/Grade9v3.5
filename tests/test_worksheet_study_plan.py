"""Learner-facing worksheet study plan composes existing core layers without new truth."""
from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import learner_evidence, worksheet_study_plan  # noqa: E402


class WorksheetStudyPlan(unittest.TestCase):
    FIXTURE = REPO / "tests/fixtures/study_route/physics-cross-matrix.worksheet.json"
    NLM_FIXTURE = REPO / "tests/fixtures/real_pilots/examside-nlm-constraints.worksheet.json"

    def mapping(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def by_capability(self, report):
        return {row["capability_ref"]: row for row in report["route"]}

    def test_no_learner_input_keeps_the_plan_neutral_and_diagnostic(self):
        report = worksheet_study_plan.resolve(self.mapping())
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["profile_id"], None)
        self.assertTrue(report["questions"])
        self.assertTrue(report["route"])
        self.assertIn("QUICK_CHECK", {row["recommended_action"] for row in report["route"]})
        self.assertIn("STUDY", {row["recommended_action"] for row in report["route"]})
        self.assertEqual(report["questions"][0]["learner_state"], "UNOBSERVED")
        self.assertIn("first attempt", report["questions"][0]["why_extra_attention"])

    def test_output_has_the_same_question_to_study_map_shape_as_the_parent_view(self):
        report = worksheet_study_plan.resolve(self.mapping())
        q1 = report["questions"][0]
        self.assertEqual(q1["question_id"], "Q1")
        self.assertEqual(q1["primary_capability_ref"], "CAP-KIN-ZERO-V-NONZERO-A")
        self.assertNotEqual(q1["core_lesson"], "UNRESOLVED")
        self.assertTrue(q1["what_is_being_learned"])
        rendered = worksheet_study_plan.readable(report)
        self.assertIn("Question -> study map", rendered)
        self.assertIn("Core lesson", rendered)
        self.assertIn("Difficulty (source)", rendered)
        self.assertIn("Canonical matrix", rendered)
        self.assertIn("Why extra attention?", rendered)
        self.assertIn("Ordered study route", rendered)

    def test_detailed_nlm_view_reuses_matrix_difficulty_estimate_and_evidence_layers(self):
        mapping = json.loads(self.NLM_FIXTURE.read_text(encoding="utf-8"))
        report = worksheet_study_plan.resolve(
            mapping,
            owner_estimates=[{
                "matrix_id": "MATRIX-PHY-NLM-FIRST-LAW",
                "knowledge_percentage": 60,
            }],
        )

        matrix = next(
            row for row in report["canonical_matrices"]
            if row["matrix_id"] == "MATRIX-PHY-NLM-FIRST-LAW"
        )
        self.assertEqual(
            [row["ladder_position"] for row in matrix["rungs"]],
            [20, 45, 70, 78, 86, 88, 90, 92, 93, 94, 100],
        )
        self.assertEqual(
            [row["rung"] for row in matrix["rungs"]],
            ["R1", "R2", "R3", "R5", "R6", "R8", "R9", "R10", "R11", "R7", "R4"],
        )
        r8 = next(row for row in matrix["rungs"] if row["rung"] == "R8")
        self.assertEqual(r8["capability_ref"], "CAP-NLM-FRICTION-QUANT")
        self.assertEqual(r8["intrinsic_difficulty"], "HARD")
        self.assertEqual(r8["microtopic_ref"], "MIC-PHY-NLM-FRICTION-QUANT")
        r4 = next(row for row in matrix["rungs"] if row["rung"] == "R4")
        self.assertFalse(r4["default_entry_eligible"])
        self.assertIn("Choose the body and frame", matrix["family_invariant"])

        friction = next(
            row for row in report["questions"]
            if row["primary_capability_ref"] == "CAP-NLM-FRICTION-QUANT"
        )
        self.assertEqual(friction["intrinsic_difficulty"], "HARD")
        self.assertEqual(
            friction["difficulty_source"],
            "MIC-PHY-NLM-FRICTION-QUANT",
        )
        self.assertEqual(friction["learner_state"], "UNOBSERVED")

        rendered = worksheet_study_plan.readable(report)
        self.assertIn("Rough starting estimates", rendered)
        self.assertIn("starting-point routing only", rendered)
        self.assertIn("does not create DEMONSTRATED", rendered)
        self.assertIn("Canonical matrix", rendered)
        self.assertIn("Difficulty (source)", rendered)
        self.assertIn("MIC-PHY-NLM-FRICTION-QUANT", rendered)
        self.assertIn("R5", rendered)
        self.assertIn("R6", rendered)
        self.assertIn("R8", rendered)
        self.assertIn("R7", rendered)
        self.assertIn("R4", rendered)
        self.assertIn("Learner route", rendered)

    def test_rough_estimate_survives_only_when_no_real_evidence_exists(self):
        report = worksheet_study_plan.resolve(
            self.mapping(),
            owner_estimates=[{
                "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
                "knowledge_percentage": 75,
            }],
        )
        rows = self.by_capability(report)
        self.assertEqual(
            rows["CAP-KIN-DISTANCE-DISPLACEMENT"]["recommended_action"],
            "QUICK_CHECK",
        )
        self.assertEqual(
            rows["CAP-KIN-ZERO-V-NONZERO-A"]["recommended_action"],
            "START_HERE",
        )
        self.assertEqual(
            rows["CAP-KIN-ZERO-V-NONZERO-A"]["learner_state"]["state"],
            "UNOBSERVED",
        )
        self.assertIn(
            "not evidence",
            rows["CAP-KIN-ZERO-V-NONZERO-A"]["action_reason"],
        )

    def test_observed_uncertainty_overrides_owner_estimate(self):
        profile = {
            "profile_id": "PROFILE-PLAN",
            "provenance": "UNKNOWN",
            "held": {
                "CAP-KIN-ZERO-V-NONZERO-A": "UNCERTAIN",
            },
            "observation_refs": [],
        }
        report = worksheet_study_plan.resolve(
            self.mapping(),
            owner_estimates=[{
                "matrix_id": "MATRIX-PHY-KIN-1D-MOTION",
                "knowledge_percentage": 75,
            }],
            profile=profile,
        )
        row = self.by_capability(report)["CAP-KIN-ZERO-V-NONZERO-A"]
        self.assertEqual(row["learner_state"]["state"], "UNCERTAIN")
        self.assertEqual(row["recommended_action"], "REPAIR")
        self.assertEqual(row["action_reason"], "Current learner evidence says UNCERTAIN.")

    def test_demonstrated_question_demand_gets_a_quick_check_not_a_study_detour(self):
        profile = {
            "profile_id": "PROFILE-PLAN",
            "provenance": "DIAGNOSTIC",
            "held": {
                "CAP-KIN-ZERO-V-NONZERO-A": "DEMONSTRATED",
            },
            "observation_refs": [],
        }
        report = worksheet_study_plan.resolve(self.mapping(), profile=profile)
        row = self.by_capability(report)["CAP-KIN-ZERO-V-NONZERO-A"]
        self.assertEqual(row["recommended_action"], "QUICK_CHECK")
        self.assertIn("Already demonstrated", row["action_reason"])

    def test_observation_text_populates_attention_without_inventing_a_diagnosis(self):
        observation = {
            "observation_id": "OBS-PLAN-1",
            "capability_ref": "CAP-KIN-ZERO-V-NONZERO-A",
            "method": "worksheet attempt",
            "evidence_kind": "DIRECT_ATTEMPT",
            "question_ref": "Q1",
            "observed": "treated zero velocity at the turning point as zero acceleration",
            "result": "UNCERTAIN",
            "when": "2026-09-18T10:00:00Z",
            "help": "NONE",
            "error_stage": "CONCEPT",
        }
        profile = {
            "profile_id": "PROFILE-PLAN",
            "provenance": "DIAGNOSTIC",
            "held": {},
            "observation_refs": ["OBS-PLAN-1"],
        }
        with patch.object(
            learner_evidence,
            "load_observations",
            return_value={"OBS-PLAN-1": observation},
        ):
            report = worksheet_study_plan.resolve(self.mapping(), profile=profile)

        q1 = report["questions"][0]
        self.assertEqual(q1["learner_state"], "UNCERTAIN")
        self.assertEqual(
            q1["why_extra_attention"],
            "Concept — treated zero velocity at the turning point as zero acceleration",
        )

    def test_external_bridge_is_a_blocker_until_learner_evidence_satisfies_it(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "Example/library").mkdir(parents=True)
            (root / "Example/matrices").mkdir(parents=True)
            (root / "Shared/library").mkdir(parents=True)
            (root / "Shared/library/worksheet-map.schema.json").write_text(
                (REPO / "Shared/library/worksheet-map.schema.json").read_text(
                    encoding="utf-8"
                ),
                encoding="utf-8",
            )
            (root / "Example/library/example.json").write_text(json.dumps({
                "capabilities": [
                    {
                        "id": "CAP-BRIDGE",
                        "action": "Use provider-owned prior knowledge",
                        "success_criterion": "Provider-owned prior knowledge is used correctly",
                        "prerequisite_refs": [],
                        "external_provider": "ProviderSubject",
                        "acceptance_status": "PROVIDER_REVIEW_REQUIRED",
                    },
                    {
                        "id": "CAP-TARGET",
                        "action": "Use the local target skill",
                        "success_criterion": "The local target skill is demonstrated",
                        "prerequisite_refs": ["CAP-BRIDGE"],
                        "external_provider": None,
                        "acceptance_status": "CANDIDATE",
                    },
                ],
                "microtopics": [{
                    "id": "MIC-TARGET",
                    "title": "Local target lesson",
                    "primary_capability_ref": "CAP-TARGET",
                }],
                "questions": [],
            }), encoding="utf-8")
            (root / "Example/matrices/example.rungs.json").write_text(json.dumps({
                "matrix_id": "MATRIX-EXAMPLE",
                "bucket_id": "BUCKET-EXAMPLE",
                "topic": "Synthetic",
                "subtopic": "Provider bridge",
                "rungs": [{
                    "rung": "R1",
                    "ladder_position": 20,
                    "microtopic_ref": "MIC-TARGET",
                }],
            }), encoding="utf-8")
            mapping = {
                "worksheet_id": "EXAMPLE-BRIDGE",
                "subject": "Example",
                "questions": [{
                    "question_id": "Q1",
                    "primary_capability_ref": "CAP-TARGET",
                    "secondary_capability_refs": [],
                    "mapping_basis": "MANUAL",
                }],
            }

            unobserved = worksheet_study_plan.resolve(mapping, repo=root)
            self.assertTrue(unobserved["valid"], unobserved["findings"])
            self.assertTrue(unobserved["passed"], unobserved["findings"])
            self.assertFalse(unobserved["ready"])
            rows = self.by_capability(unobserved)
            self.assertEqual(rows["CAP-BRIDGE"]["recommended_action"], "BRIDGE")
            self.assertEqual(rows["CAP-BRIDGE"]["provider"], "ProviderSubject")
            self.assertEqual(rows["CAP-BRIDGE"]["external_provider"], "ProviderSubject")
            self.assertIn("External bridge: ProviderSubject", worksheet_study_plan.readable(unobserved))
            self.assertEqual(
                [row["capability"] for row in unobserved["blockers"]],
                ["CAP-BRIDGE"],
            )

            profile = {
                "profile_id": "PROFILE-BRIDGE",
                "provenance": "UNKNOWN",
                "held": {"CAP-BRIDGE": "DEMONSTRATED"},
                "observation_refs": [],
            }
            demonstrated = worksheet_study_plan.resolve(mapping, profile=profile, repo=root)
            self.assertTrue(demonstrated["valid"], demonstrated["findings"])
            self.assertTrue(demonstrated["ready"], demonstrated["blockers"])
            self.assertEqual(demonstrated["blockers"], [])
            rows = self.by_capability(demonstrated)
            self.assertEqual(rows["CAP-BRIDGE"]["recommended_action"], "SKIP")
            self.assertIn("bridge is not needed", rows["CAP-BRIDGE"]["action_reason"])

    def test_synthetic_profile_is_refused_for_real_routing(self):
        profile = {
            "profile_id": "PROFILE-SYNTH",
            "provenance": "SYNTHETIC_TEST",
            "held": {},
            "observation_refs": [],
        }
        report = worksheet_study_plan.resolve(self.mapping(), profile=profile)
        self.assertFalse(report["passed"])
        self.assertIn(
            "WORKSHEET_STUDY_PLAN_SYNTHETIC_PROFILE_REFUSED",
            [row["point"] for row in report["findings"]],
        )
        self.assertEqual(report["route"], [])


if __name__ == "__main__":
    unittest.main()
