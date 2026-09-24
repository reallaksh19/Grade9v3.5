import unittest
from pathlib import Path

from Shared.tools import core_template_contract


REPO = Path(__file__).resolve().parents[1]


class CoreTemplateContractTests(unittest.TestCase):
    def test_contract_covers_all_six_roles_and_passes_structural_audit(self):
        report = core_template_contract.audit(REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md")
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["roles_checked"], 6)
        self.assertEqual(report["contract_version"], "1.0")

    def test_core1b_attempt_precedes_reconstruction(self):
        roles = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )["roles"]
        ids = [block["id"] for block in roles["CORE1B"]["ordered_blocks"]]
        self.assertLess(ids.index("attempt"), ids.index("reconstruct"))
        self.assertIn("ANSWER_BEFORE_ATTEMPT", roles["CORE1B"]["forbidden"])

    def test_core2b_protects_changed_decision_until_after_attempt(self):
        roles = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )["roles"]
        core2b = roles["CORE2B"]
        ids = [block["id"] for block in core2b["ordered_blocks"]]
        self.assertLess(ids.index("attempt_commitment"), ids.index("changed_demand_review"))
        self.assertIn("PROTECTED_MOVE", core2b["withheld_pre_attempt"])
        self.assertIn(
            "PROTECTED_MOVE_DISCLOSED_PRE_ATTEMPT",
            core2b["forbidden"],
        )

    def test_source_hints_and_authored_scaffolds_are_not_collapsed(self):
        roles = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )["roles"]
        self.assertIn(
            "AUTHORED_SCAFFOLD_PRESENTED_AS_SOURCE_HINT",
            roles["CORE2"]["forbidden"],
        )
        core2a_ids = {
            block["id"] for block in roles["CORE2A"]["ordered_blocks"]
        }
        self.assertIn("pedagogical_scaffolds", core2a_ids)
        self.assertIn("application_crux", core2a_ids)

    def test_all_role_anatomies_are_distinct(self):
        roles = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )["roles"]
        signatures = [
            tuple(block["id"] for block in roles[role]["ordered_blocks"])
            for role in core_template_contract.ROLE_ORDER
        ]
        self.assertEqual(len(signatures), len(set(signatures)))


if __name__ == "__main__":
    unittest.main()
