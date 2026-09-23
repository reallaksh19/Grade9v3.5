"""STEP-TA9-001 falsifiers for the derived Grade-9 exit evidence view."""
from __future__ import annotations

import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import grade9_exit

REPO = Path(__file__).resolve().parents[1]


class Grade9ExitProjectionTest(unittest.TestCase):
    def test_bench_ta9_001_frozen_exit_state_truth_table(self):
        cases = [
            (
                {"state": "DEMONSTRATED", "independence_proven": True},
                {"result": "DEMONSTRATED", "help": "NONE"},
                grade9_exit.SECURE,
            ),
            (
                {"state": "UNCERTAIN", "independence_proven": False},
                {"result": "DEMONSTRATED", "help": "HINT"},
                grade9_exit.USABLE_BUT_FRAGILE,
            ),
            (
                {"state": "MISSING", "independence_proven": True},
                {"result": "MISSING", "help": "NONE"},
                grade9_exit.KNOWN_GAP,
            ),
            (
                {"state": "UNOBSERVED", "independence_proven": False},
                None,
                grade9_exit.INSUFFICIENT_OR_UNKNOWN,
            ),
            (
                {
                    "state": "DEMONSTRATED",
                    "source": "PROFILE_OWNER_ESTIMATE",
                    "independence_proven": False,
                },
                None,
                grade9_exit.INSUFFICIENT_OR_UNKNOWN,
            ),
        ]
        for effective, observation, expected in cases:
            with self.subTest(effective=effective, observation=observation):
                self.assertEqual(
                    grade9_exit.evidence_category(effective, observation),
                    expected,
                )

    def test_required_scope_is_six_core_matrices_and_nondefault_rungs_do_not_leak(self):
        coverage = grade9_exit.scope_coverage(REPO)
        required = [
            row for row in coverage["matrices"]
            if row["role"] == "REQUIRED_CORE"
        ]
        self.assertEqual(len(required), 6)
        self.assertTrue(all(row["default_grade9_completion_blocker"] for row in required))

        by_id = {row["matrix_id"]: row for row in required}
        motion = grade9_exit.matrix_capabilities(
            by_id["MATRIX-PHY-KIN-1D-MOTION"], REPO
        )
        nlm = grade9_exit.matrix_capabilities(
            by_id["MATRIX-PHY-NLM-FIRST-LAW"], REPO
        )
        grav = grade9_exit.matrix_capabilities(
            by_id["MATRIX-PHY-GRAV-UNIVERSAL-LAW"], REPO
        )

        self.assertNotIn(
            "CAP-KIN-ZERO-V-NONZERO-A",
            {row["capability_ref"] for row in motion},
        )
        self.assertNotIn(
            "CAP-NLM-FRAME-CHOICE",
            {row["capability_ref"] for row in nlm},
        )
        self.assertNotIn(
            "CAP-PHY-GRAV-R4",
            {row["capability_ref"] for row in grav},
        )
        self.assertNotIn(
            "CAP-PHY-GRAV-R5",
            {row["capability_ref"] for row in grav},
        )

    def test_required_transfer_sampling_comes_only_from_canonical_question_metadata(self):
        coverage = grade9_exit.scope_coverage(REPO)
        required = {
            row["matrix_id"]: row
            for row in coverage["matrices"]
            if row["role"] == "REQUIRED_CORE"
        }
        motion = grade9_exit.matrix_capabilities(
            required["MATRIX-PHY-KIN-1D-MOTION"], REPO
        )
        nlm = grade9_exit.matrix_capabilities(
            required["MATRIX-PHY-NLM-FIRST-LAW"], REPO
        )
        grav = grade9_exit.matrix_capabilities(
            required["MATRIX-PHY-GRAV-UNIVERSAL-LAW"], REPO
        )

        self.assertIn(
            "representation_translation",
            {
                dimension
                for row in motion
                for dimension in row["transfer_question_dimensions"].values()
            },
        )
        self.assertTrue(any(row["transfer_question_dimensions"] for row in nlm))
        self.assertFalse(any(row["transfer_question_dimensions"] for row in grav))


    def test_changed_demand_identity_requires_core2b_exposure_plus_transfer_metadata(self):
        scope_row = {
            "matrix_id": "MATRIX-SYNTHETIC",
            "path": "Physics/matrices/synthetic.rungs.json",
            "role": "REQUIRED_CORE",
            "ordinary_grade9_core": True,
            "default_grade9_completion_blocker": True,
        }
        matrix = {
            "rungs": [{
                "rung": "R1",
                "microtopic_ref": "MIC-SYNTHETIC",
                "default_entry_eligible": True,
            }]
        }
        package = {
            "capabilities": [{"id": "CAP-SYNTHETIC", "prerequisite_refs": []}],
            "microtopics": [{
                "id": "MIC-SYNTHETIC",
                "primary_capability_ref": "CAP-SYNTHETIC",
            }],
            "questions": [
                {
                    "id": "Q-CORE2A-WITH-TRANSFER",
                    "primary_capability_ref": "CAP-SYNTHETIC",
                    "exposure": [{"core": "CORE2A", "role": "PRACTICE", "artifact_ref": None}],
                    "transfer": {"dimension": "model_choice"},
                },
                {
                    "id": "Q-CORE2B-WITH-TRANSFER",
                    "primary_capability_ref": "CAP-SYNTHETIC",
                    "exposure": [{"core": "CORE2B", "role": "FREE_FORM_ROLE", "artifact_ref": None}],
                    "transfer": {"dimension": "representation_translation"},
                },
                {
                    "id": "Q-CORE2B-WITHOUT-TRANSFER",
                    "primary_capability_ref": "CAP-SYNTHETIC",
                    "exposure": [{"core": "CORE2B", "role": "FREE_FORM_ROLE", "artifact_ref": None}],
                },
            ],
        }

        with patch.object(grade9_exit, "load", side_effect=[matrix, package]):
            rows = grade9_exit.matrix_capabilities(scope_row, REPO)

        self.assertEqual(len(rows), 1)
        self.assertEqual(
            rows[0]["transfer_question_dimensions"],
            {"Q-CORE2B-WITH-TRANSFER": "representation_translation"},
        )

    def test_changed_demand_observation_requires_direct_no_help_known_question(self):
        history = [
            {
                "observation_id": "OBS-HINTED",
                "evidence_kind": "DIRECT_ATTEMPT",
                "question_ref": "Q-X-TRANSFER",
                "result": "DEMONSTRATED",
                "help": "HINT",
                "observed": "Solved after a hint.",
                "when": "2026-09-22T10:00:00Z",
            },
            {
                "observation_id": "OBS-PRIOR",
                "evidence_kind": "PRIOR_DIAGNOSTIC",
                "question_ref": "Q-X-TRANSFER",
                "result": "DEMONSTRATED",
                "help": "NONE",
                "observed": "Historical diagnostic success.",
                "when": "2026-09-21T10:00:00Z",
            },
            {
                "observation_id": "OBS-UNRESOLVED",
                "evidence_kind": "DIRECT_ATTEMPT",
                "question_ref": "Q-NOT-CANONICAL",
                "result": "DEMONSTRATED",
                "help": "NONE",
                "observed": "Solved an unresolved question.",
                "when": "2026-09-20T10:00:00Z",
            },
        ]
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=history,
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "UNCERTAIN",
                "source": "DIRECT_ATTEMPT",
                "independence_proven": False,
                "independence_basis": "HELP_USED",
            },
        ):
            projected = grade9_exit.capability_projection(
                {"profile_id": "PROFILE-X"},
                "CAP-X",
                REPO,
                transfer_question_dimensions={
                    "Q-X-TRANSFER": "representation_translation",
                },
            )

        self.assertEqual(projected["independent_transfer_dimensions"], [])

    def test_live_transfer_inventory_is_available_not_transition_required(self):
        independent_practice = [{
            "observation_id": "OBS-PRACTICE",
            "evidence_kind": "DIRECT_ATTEMPT",
            "question_ref": "Q-NONTRANSFER-PRACTICE",
            "result": "DEMONSTRATED",
            "help": "NONE",
            "observed": "Independent familiar-practice success.",
            "when": "2026-09-22T10:00:00Z",
            "error_stage": None,
        }]
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=independent_practice,
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "DEMONSTRATED",
                "source": "DIRECT_ATTEMPT",
                "independence_proven": True,
                "independence_basis": "DIRECT_ATTEMPT_WITH_NO_HELP",
            },
        ):
            projection = grade9_exit.project(
                {"profile_id": "PROFILE-LIVE-WITNESS"},
                REPO,
            )

        motion = next(
            row for row in projection["domains"]
            if row["matrix_id"] == "MATRIX-PHY-KIN-1D-MOTION"
        )
        nlm = next(
            row for row in projection["domains"]
            if row["matrix_id"] == "MATRIX-PHY-NLM-FIRST-LAW"
        )
        for domain in (motion, nlm):
            self.assertEqual(
                domain["transfer_evidence"]["status"],
                "AVAILABLE_UNOBSERVED",
            )
            self.assertFalse(domain["transfer_evidence"]["transition_required"])
            self.assertTrue(domain["transfer_evidence"]["available_dimensions"])
            self.assertEqual(
                domain["transfer_evidence"]["independent_observed_dimensions"],
                [],
            )

        report = grade9_exit.transition_report(projection)
        self.assertEqual(
            report["transition_state"],
            "GRADE10_NEXT_PRODUCTIVE_FRONTIER",
        )

    def test_capability_projection_preserves_history_and_independent_transfer(self):
        history = [
            {
                "observation_id": "OBS-TRANSFER",
                "capability_ref": "CAP-X",
                "method": "question attempt Q-X-TRANSFER",
                "evidence_kind": "DIRECT_ATTEMPT",
                "question_ref": "Q-X-TRANSFER",
                "observed": "Solved without help.",
                "result": "DEMONSTRATED",
                "help": "NONE",
                "when": "2026-09-21T10:00:00Z",
                "error_stage": None,
            },
            {
                "observation_id": "OBS-OLD-GAP",
                "capability_ref": "CAP-X",
                "method": "prior diagnostic",
                "evidence_kind": "PRIOR_DIAGNOSTIC",
                "question_ref": "Q-X-PRACTICE",
                "observed": "Missed the model choice.",
                "result": "MISSING",
                "help": "NONE",
                "when": "2026-09-20T10:00:00Z",
                "error_stage": "CONCEPT",
            },
        ]
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=history,
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "DEMONSTRATED",
                "source": "DIRECT_ATTEMPT",
                "independence_proven": True,
                "independence_basis": "DIRECT_ATTEMPT_WITH_NO_HELP",
            },
        ):
            projected = grade9_exit.capability_projection(
                {"profile_id": "PROFILE-X"},
                "CAP-X",
                REPO,
                transfer_question_dimensions={
                    "Q-X-TRANSFER": "representation_translation",
                },
            )

        self.assertEqual(projected["evidence_category"], grade9_exit.SECURE)
        self.assertEqual(
            projected["independent_transfer_dimensions"],
            ["representation_translation"],
        )
        self.assertEqual(
            projected["evidence_change"],
            "PRIOR_DIFFICULTY_NOW_INDEPENDENTLY_DEMONSTRATED",
        )
        self.assertEqual(
            [row["observation_ref"] for row in projected["basis"]],
            ["OBS-TRANSFER", "OBS-OLD-GAP"],
        )
        self.assertEqual(
            projected["basis"][0]["transfer_dimension"],
            "representation_translation",
        )

    def test_enrichment_without_evidence_stays_unknown_and_nonblocking(self):
        coverage = grade9_exit.scope_coverage(REPO)
        enrichment = next(
            row for row in coverage["matrices"]
            if row["role"] == "DECLARED_EXTENSION_NONBLOCKING"
        )
        cap = grade9_exit.matrix_capabilities(enrichment, REPO)[0]

        profile = {"profile_id": "PROFILE-EMPTY", "held": {}, "observation_refs": []}
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=[],
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "UNOBSERVED",
                "source": "UNOBSERVED",
                "independence_proven": False,
                "independence_basis": "UNOBSERVED",
            },
        ):
            projected = grade9_exit.capability_projection(
                profile, cap["capability_ref"], REPO
            )

        self.assertEqual(
            projected["evidence_category"],
            grade9_exit.INSUFFICIENT_OR_UNKNOWN,
        )
        self.assertFalse(cap["default_grade9_completion_blocker"])
        self.assertFalse(cap["ordinary_grade9_core"])

    def test_deferred_scope_stays_visible_without_requiring_complete_bindings(self):
        coverage = grade9_exit.scope_coverage(REPO)
        electricity = next(
            row for row in coverage["matrices"]
            if row["matrix_id"] == "MATRIX-PHY-ELEC-CURRENT-OHM"
        )

        capabilities = grade9_exit.matrix_capabilities(electricity, REPO)
        self.assertEqual(
            {row["capability_ref"] for row in capabilities},
            {
                "CAP-ELEC-CURRENT-CONSERVATION",
                "CAP-ELEC-OHMIC-MODEL-TEST",
            },
        )
        self.assertFalse(electricity["ordinary_grade9_core"])
        self.assertFalse(electricity["default_grade9_completion_blocker"])

        profile = {"profile_id": "PROFILE-EMPTY", "held": {}, "observation_refs": []}
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=[],
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "UNOBSERVED",
                "source": "UNOBSERVED",
                "independence_proven": False,
                "independence_basis": "UNOBSERVED",
            },
        ):
            report = grade9_exit.project(profile, REPO)

        domain = next(
            row for row in report["domains"]
            if row["matrix_id"] == "MATRIX-PHY-ELEC-CURRENT-OHM"
        )
        self.assertEqual(
            domain["evidence_category"],
            grade9_exit.INSUFFICIENT_OR_UNKNOWN,
        )
        self.assertFalse(domain["ordinary_grade9_core"])
        self.assertFalse(domain["default_grade9_completion_blocker"])

    def test_bench_ta9_002_transition_blocker_boundary(self):
        rows = [
            {
                "matrix_id": "MATRIX-REQ-A",
                "capability_ref": "CAP-REQ-A",
                "ordinary_grade9_core": True,
                "matrix_role": "REQUIRED_CORE",
                "prerequisite_refs": ["CAP-PREREQ"],
                "evidence_category": grade9_exit.KNOWN_GAP,
            },
            {
                "matrix_id": "MATRIX-SUPPORT",
                "capability_ref": "CAP-PREREQ",
                "ordinary_grade9_core": False,
                "matrix_role": "SUPPORT_ONLY",
                "prerequisite_refs": [],
                "evidence_category": grade9_exit.KNOWN_GAP,
            },
            {
                "matrix_id": "MATRIX-SUPPORT",
                "capability_ref": "CAP-UNUSED-SUPPORT",
                "ordinary_grade9_core": False,
                "matrix_role": "SUPPORT_ONLY",
                "prerequisite_refs": [],
                "evidence_category": grade9_exit.KNOWN_GAP,
            },
            {
                "matrix_id": "MATRIX-ENRICH",
                "capability_ref": "CAP-ENRICH",
                "ordinary_grade9_core": False,
                "matrix_role": "DECLARED_EXTENSION_NONBLOCKING",
                "prerequisite_refs": [],
                "evidence_category": grade9_exit.KNOWN_GAP,
            },
            {
                "matrix_id": "MATRIX-LATER",
                "capability_ref": "CAP-LATER",
                "ordinary_grade9_core": False,
                "matrix_role": "DEFERRED_LATER_OR_BROADER",
                "prerequisite_refs": [],
                "evidence_category": grade9_exit.KNOWN_GAP,
            },
            {
                "matrix_id": "MATRIX-REQ-B",
                "capability_ref": "CAP-REQ-UNKNOWN",
                "ordinary_grade9_core": True,
                "matrix_role": "REQUIRED_CORE",
                "prerequisite_refs": [],
                "evidence_category": grade9_exit.INSUFFICIENT_OR_UNKNOWN,
            },
        ]

        decisions = {
            row["capability_ref"]: row
            for row in grade9_exit.transition_boundary(rows)
        }

        self.assertTrue(decisions["CAP-REQ-A"]["blocks_transition"])
        self.assertEqual(
            decisions["CAP-REQ-A"]["reason"],
            "REQUIRED_SCOPE_GAP",
        )
        self.assertTrue(decisions["CAP-PREREQ"]["blocks_transition"])
        self.assertEqual(
            decisions["CAP-PREREQ"]["reason"],
            "GENUINE_PREREQUISITE_GAP",
        )
        self.assertFalse(decisions["CAP-UNUSED-SUPPORT"]["blocks_transition"])
        self.assertEqual(
            decisions["CAP-UNUSED-SUPPORT"]["disposition"],
            "NON_BLOCKING_GAP",
        )
        self.assertFalse(decisions["CAP-ENRICH"]["blocks_transition"])
        self.assertFalse(decisions["CAP-LATER"]["blocks_transition"])
        self.assertEqual(
            decisions["CAP-REQ-UNKNOWN"]["disposition"],
            "EVIDENCE_REQUIRED",
        )
        self.assertFalse(decisions["CAP-REQ-UNKNOWN"]["blocks_transition"])

    def test_bench_ta9_003_parent_report_reconstructs_transition_basis(self):
        projection = {
            "profile_id": "PROFILE-REPORT",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-SECURE",
                    "matrix_role": "REQUIRED_CORE",
                    "ordinary_grade9_core": True,
                    "evidence_category": grade9_exit.SECURE,
                    "basis": [
                        {
                            "observation_ref": "OBS-SECURE",
                            "help": "NONE",
                            "error_stage": None,
                        }
                    ],
                },
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-GAP",
                    "matrix_role": "REQUIRED_CORE",
                    "ordinary_grade9_core": True,
                    "evidence_category": grade9_exit.KNOWN_GAP,
                    "basis": [
                        {
                            "observation_ref": "OBS-GAP",
                            "help": "NONE",
                            "error_stage": "CONCEPT",
                        }
                    ],
                },
                {
                    "matrix_id": "MATRIX-ENRICH",
                    "capability_ref": "CAP-OPTIONAL",
                    "matrix_role": "DECLARED_EXTENSION_NONBLOCKING",
                    "ordinary_grade9_core": False,
                    "evidence_category": grade9_exit.KNOWN_GAP,
                    "basis": [{"observation_ref": "OBS-OPTIONAL"}],
                },
            ],
            "transition_boundary": [
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-SECURE",
                    "blocks_transition": False,
                    "disposition": "NON_BLOCKING",
                    "reason": "NO_KNOWN_BLOCKER",
                },
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-GAP",
                    "blocks_transition": True,
                    "disposition": "BLOCKER",
                    "reason": "REQUIRED_SCOPE_GAP",
                },
                {
                    "matrix_id": "MATRIX-ENRICH",
                    "capability_ref": "CAP-OPTIONAL",
                    "blocks_transition": False,
                    "disposition": "NON_BLOCKING_GAP",
                    "reason": "NON_BLOCKING_SCOPE_GAP",
                },
            ],
        }

        report = grade9_exit.transition_report(projection)
        self.assertEqual(report["projection_kind"], "DERIVED_REPORT")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")
        self.assertEqual(report["transition_state"], "GRADE9_REPAIR_REQUIRED")

        gap = next(row for row in report["rows"] if row["capability_ref"] == "CAP-GAP")
        self.assertEqual(gap["evidence_basis"][0]["observation_ref"], "OBS-GAP")
        self.assertEqual(gap["blocker_status"], "BLOCKER")
        self.assertIn("concept gap", gap["repair_recheck_context"])
        self.assertIn("before treating Grade 10", gap["transition_implication"])

        optional = next(
            row for row in report["rows"]
            if row["capability_ref"] == "CAP-OPTIONAL"
        )
        self.assertEqual(optional["blocker_status"], "NON_BLOCKING_GAP")

        text = grade9_exit.parent_agent_text(report)
        self.assertIn("GRADE9_REPAIR_REQUIRED", text)
        self.assertIn("CAP-GAP", text)
        self.assertIn("OBS-GAP", text)
        self.assertIn("CAP-OPTIONAL", text)
        self.assertIn("Visible non-blocking items:", text)
        self.assertIn("Named misconception identity/severity is not inferred", text)
        self.assertNotIn("mastery_percentage", text.lower())
        self.assertNotIn("mastery_probability", text.lower())

    def test_authored_changed_demand_without_transition_authority_is_visible_nonblocking(self):
        projection = {
            "profile_id": "PROFILE-TRANSFER-AVAILABLE",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "matrix_role": "REQUIRED_CORE",
                "ordinary_grade9_core": True,
                "evidence_category": grade9_exit.SECURE,
                "basis": [{"observation_ref": "OBS-PRACTICE", "help": "NONE"}],
                "independent_transfer_dimensions": [],
            }],
            "domains": [{
                "matrix_id": "MATRIX-REQ",
                "ordinary_grade9_core": True,
                "transfer_evidence": {
                    "status": "AVAILABLE_UNOBSERVED",
                    "available_dimensions": ["representation_translation"],
                    "independent_observed_dimensions": [],
                    "transition_required": False,
                    "transition_requirement_source": None,
                },
            }],
            "transition_boundary": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "scope_relevance": "REQUIRED_SCOPE",
                "blocks_transition": False,
                "disposition": "NON_BLOCKING",
                "reason": "NO_KNOWN_BLOCKER",
            }],
        }
        report = grade9_exit.transition_report(projection)
        self.assertEqual(
            report["transition_state"],
            "GRADE10_NEXT_PRODUCTIVE_FRONTIER",
        )
        text = grade9_exit.parent_agent_text(report)
        self.assertIn("Changed-demand evidence:", text)
        self.assertIn("AVAILABLE_UNOBSERVED / not-declared-required", text)

    def test_explicit_transition_authority_can_require_changed_demand_evidence(self):
        projection = {
            "profile_id": "PROFILE-TRANSFER-REQUIRED",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "matrix_role": "REQUIRED_CORE",
                "ordinary_grade9_core": True,
                "evidence_category": grade9_exit.SECURE,
                "basis": [{"observation_ref": "OBS-PRACTICE", "help": "NONE"}],
                "independent_transfer_dimensions": [],
            }],
            "domains": [{
                "matrix_id": "MATRIX-REQ",
                "ordinary_grade9_core": True,
                "transfer_evidence": {
                    "status": "EVIDENCE_NEEDED",
                    "available_dimensions": ["representation_translation"],
                    "independent_observed_dimensions": [],
                    "transition_required": True,
                    "transition_requirement_source": "SYNTHETIC_TRANSITION_AUTHORITY",
                },
            }],
            "transition_boundary": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "scope_relevance": "REQUIRED_SCOPE",
                "blocks_transition": False,
                "disposition": "NON_BLOCKING",
                "reason": "NO_KNOWN_BLOCKER",
            }],
        }
        report = grade9_exit.transition_report(projection)
        self.assertEqual(report["transition_state"], "GRADE9_EVIDENCE_INCOMPLETE")
        self.assertIn("explicit transition authority", report["transition_message"])
        text = grade9_exit.parent_agent_text(report)
        self.assertIn("EVIDENCE_NEEDED / required", text)

    def test_observed_changed_demand_satisfies_explicit_transition_requirement(self):
        projection = {
            "profile_id": "PROFILE-TRANSFER-OBSERVED",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "matrix_role": "REQUIRED_CORE",
                "ordinary_grade9_core": True,
                "evidence_category": grade9_exit.SECURE,
                "basis": [{"observation_ref": "OBS-TRANSFER", "help": "NONE"}],
                "independent_transfer_dimensions": ["representation_translation"],
            }],
            "domains": [{
                "matrix_id": "MATRIX-REQ",
                "ordinary_grade9_core": True,
                "transfer_evidence": {
                    "status": "OBSERVED",
                    "available_dimensions": ["representation_translation"],
                    "independent_observed_dimensions": ["representation_translation"],
                    "transition_required": True,
                    "transition_requirement_source": "SYNTHETIC_TRANSITION_AUTHORITY",
                },
            }],
            "transition_boundary": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-SECURE",
                "scope_relevance": "REQUIRED_SCOPE",
                "blocks_transition": False,
                "disposition": "NON_BLOCKING",
                "reason": "NO_KNOWN_BLOCKER",
            }],
        }
        report = grade9_exit.transition_report(projection)
        self.assertEqual(
            report["transition_state"],
            "GRADE10_NEXT_PRODUCTIVE_FRONTIER",
        )

    def test_fragile_required_evidence_carries_targeted_recheck_into_transition(self):
        projection = {
            "profile_id": "PROFILE-FRAGILE",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-FRAGILE",
                "matrix_role": "REQUIRED_CORE",
                "ordinary_grade9_core": True,
                "evidence_category": grade9_exit.USABLE_BUT_FRAGILE,
                "basis": [{"observation_ref": "OBS-HINTED", "help": "HINT"}],
            }],
            "transition_boundary": [{
                "matrix_id": "MATRIX-REQ",
                "capability_ref": "CAP-FRAGILE",
                "scope_relevance": "REQUIRED_SCOPE",
                "blocks_transition": False,
                "disposition": "NON_BLOCKING",
                "reason": "NO_KNOWN_BLOCKER",
            }],
        }
        report = grade9_exit.transition_report(projection)
        self.assertEqual(report["transition_state"], "GRADE10_WITH_TARGETED_RECHECKS")
        self.assertEqual(report["fragile_rechecks"], ["CAP-FRAGILE"])
        self.assertIn("rechecked independently", report["transition_message"])

    def test_optional_gap_remains_visible_but_nonblocking_in_parent_view(self):
        projection = {
            "profile_id": "PROFILE-OPTIONAL",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [{
                "matrix_id": "MATRIX-ENRICH",
                "capability_ref": "CAP-OPTIONAL",
                "matrix_role": "DECLARED_EXTENSION_NONBLOCKING",
                "ordinary_grade9_core": False,
                "evidence_category": grade9_exit.KNOWN_GAP,
                "basis": [{"observation_ref": "OBS-OPTIONAL"}],
            }],
            "transition_boundary": [{
                "matrix_id": "MATRIX-ENRICH",
                "capability_ref": "CAP-OPTIONAL",
                "scope_relevance": "NON_BLOCKING_SCOPE",
                "blocks_transition": False,
                "disposition": "NON_BLOCKING_GAP",
                "reason": "NON_BLOCKING_SCOPE_GAP",
            }],
        }
        report = grade9_exit.transition_report(projection)
        text = grade9_exit.parent_agent_text(report)
        self.assertIn("Visible non-blocking items:", text)
        self.assertIn("CAP-OPTIONAL", text)
        self.assertIn("NON_BLOCKING_GAP", text)
        self.assertEqual(report["transition_state"], "GRADE10_NEXT_PRODUCTIVE_FRONTIER")

    def test_report_keeps_unknown_required_evidence_distinct_from_known_gap(self):
        projection = {
            "profile_id": "PROFILE-UNKNOWN",
            "scope_source": grade9_exit.SCOPE_COVERAGE,
            "capabilities": [
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-UNKNOWN",
                    "matrix_role": "REQUIRED_CORE",
                    "ordinary_grade9_core": True,
                    "evidence_category": grade9_exit.INSUFFICIENT_OR_UNKNOWN,
                    "basis": [],
                }
            ],
            "transition_boundary": [
                {
                    "matrix_id": "MATRIX-REQ",
                    "capability_ref": "CAP-UNKNOWN",
                    "blocks_transition": False,
                    "disposition": "EVIDENCE_REQUIRED",
                    "reason": "REQUIRED_SCOPE_EVIDENCE_UNKNOWN",
                }
            ],
        }
        report = grade9_exit.transition_report(projection)
        self.assertEqual(
            report["transition_state"],
            "GRADE9_EVIDENCE_INCOMPLETE",
        )
        row = report["rows"][0]
        self.assertEqual(row["blocker_status"], "EVIDENCE_REQUIRED")
        self.assertNotEqual(row["evidence_category"], grade9_exit.KNOWN_GAP)
        self.assertIn("Collect direct independent evidence", row["repair_recheck_context"])


    def test_bench_ta9_004_no_second_mastery_store_or_protected_write_path(self):
        source = (REPO / "Shared/tools/grade9_exit.py").read_text(encoding="utf-8")
        lowered = source.lower()

        for forbidden in (
            "mastery_percentage",
            "mastery_probability",
            "grade_readiness_store",
            "persisted_grade_state",
        ):
            self.assertNotIn(forbidden, lowered)

        for write_primitive in (
            ".write_text(",
            ".write_bytes(",
            "unlink(",
            "mkdir(",
            "shutil.",
        ):
            self.assertNotIn(write_primitive, source)

        self.assertNotIn("Learners/", source)
        self.assertNotIn("Physics/library/", source)
        self.assertNotIn("Physics/matrices/", source)

        profile = {"profile_id": "PROFILE-EMPTY", "held": {}, "observation_refs": []}
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=[],
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "UNOBSERVED",
                "source": "UNOBSERVED",
                "independence_proven": False,
                "independence_basis": "UNOBSERVED",
            },
        ):
            projection = grade9_exit.project(profile, REPO)
            report = grade9_exit.transition_report(projection)

        self.assertEqual(projection["persistence"], "NOT_WRITTEN")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")
        self.assertEqual(
            report["transition_state"],
            "GRADE9_EVIDENCE_INCOMPLETE",
        )


    def test_projection_is_derived_and_does_not_create_grade_truth(self):
        profile = {"profile_id": "PROFILE-EMPTY", "held": {}, "observation_refs": []}
        with patch.object(
            grade9_exit.learner_evidence,
            "evidence_for_capability",
            return_value=[],
        ), patch.object(
            grade9_exit.learner_evidence,
            "effective_state",
            return_value={
                "state": "UNOBSERVED",
                "source": "UNOBSERVED",
                "independence_proven": False,
                "independence_basis": "UNOBSERVED",
            },
        ):
            report = grade9_exit.project(profile, REPO)

        self.assertEqual(report["projection_kind"], "DERIVED_QUERY")
        self.assertEqual(report["persistence"], "NOT_WRITTEN")
        self.assertEqual(
            sum(1 for row in report["domains"] if row["ordinary_grade9_core"]),
            6,
        )
        self.assertTrue(
            all(
                row["evidence_category"] == grade9_exit.INSUFFICIENT_OR_UNKNOWN
                for row in report["capabilities"]
            )
        )
        serialized = repr(report).lower()
        self.assertNotIn("mastery_percentage", serialized)
        self.assertNotIn("mastery_probability", serialized)


if __name__ == "__main__":
    unittest.main()
