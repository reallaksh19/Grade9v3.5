import unittest
from pathlib import Path

from Shared.tools import core_authority_contract


REPO = Path(__file__).resolve().parents[1]


class CoreAuthorityContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.contract = core_authority_contract.load_contract(
            REPO / "Shared" / "roles" / "CORE-AUTHORITY-CONTRACT.md"
        )

    def test_contract_passes_structural_audit(self):
        report = core_authority_contract.audit(
            REPO / "Shared" / "roles" / "CORE-AUTHORITY-CONTRACT.md"
        )
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["roles_checked"], 6)
        self.assertEqual(report["contract_version"], "1.0")

    def test_execution_order_cannot_be_used_as_authority_order(self):
        self.assertTrue(
            self.contract["invariants"]["execution_order_is_not_authority_order"]
        )
        self.assertEqual(
            self.contract["planning_distinctions"]["execution_order"],
            "PRODUCTION_CONTROL_ONLY",
        )

    def test_core1_family_comes_from_canonical_academic_truth_not_core2(self):
        for role in ("CORE1", "CORE1A", "CORE1B"):
            row = self.contract["roles"][role]
            self.assertEqual(row["required_authority"], ["CANONICAL_ACADEMIC_TRUTH"])
            self.assertIn(
                "AUTHORIZED_SOURCE_CUSTODY",
                row["forbidden_authority_substitution"],
            )

    def test_core2_requires_source_custody_and_may_hold_without_rewriting_study_truth(self):
        row = self.contract["roles"]["CORE2"]
        self.assertEqual(row["required_authority"], ["AUTHORIZED_SOURCE_CUSTODY"])
        self.assertTrue(
            self.contract["invariants"]["core2_hold_does_not_rewrite_academic_authority"]
        )
        self.assertTrue(
            self.contract["invariants"][
                "core2_hold_does_not_automatically_block_valid_study_roles"
            ]
        )

    def test_per_question_primary_is_preserved_separately_from_set_scope(self):
        self.assertEqual(
            self.contract["canonical_field_rules"]["question_primary"],
            "question.primary_capability_ref",
        )
        self.assertTrue(
            self.contract["invariants"]["set_scope_must_not_overwrite_question_primary"]
        )
        self.assertEqual(
            self.contract["planning_distinctions"]["set_level_scope"],
            "COMPOSITION_CONTEXT_ONLY",
        )

    def test_demand_evidence_is_not_learner_eligibility(self):
        self.assertTrue(
            self.contract["invariants"][
                "demand_evidence_and_learner_eligibility_are_distinct"
            ]
        )
        self.assertEqual(
            self.contract["planning_distinctions"]["learner_eligibility"],
            "INDEPENDENT_REVIEW_STATE",
        )

    def test_source_hints_and_authored_scaffolds_keep_separate_custody(self):
        fields = self.contract["canonical_field_rules"]
        self.assertEqual(fields["source_hints"], "question.hints[]")
        self.assertEqual(fields["authored_scaffolds"], "question.scaffolds[]")
        self.assertTrue(
            self.contract["invariants"][
                "source_hints_and_authored_scaffolds_are_distinct"
            ]
        )

    def test_extension_pressure_cannot_expand_core1_family(self):
        self.assertTrue(
            self.contract["invariants"][
                "extensions_require_canonical_admission_before_core1_family"
            ]
        )

    def test_learner_estimate_cannot_become_mastery_or_core1_scope_authority(self):
        self.assertTrue(
            self.contract["invariants"]["learner_estimate_is_not_mastery_evidence"]
        )
        self.assertTrue(
            self.contract["invariants"][
                "learner_estimate_cannot_change_core1_family_intrinsic_scope"
            ]
        )


if __name__ == "__main__":
    unittest.main()
