import unittest
from pathlib import Path

from Shared.tools import build_core_learning_data, core_template_contract


REPO = Path(__file__).resolve().parents[1]


class CoreTemplateContractTests(unittest.TestCase):
    def test_all_six_roles_resolve_versioned_web_blueprints(self):
        contract = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )
        self.assertEqual(set(contract["roles"]), set(core_template_contract.ROLE_ORDER))
        for role in core_template_contract.ROLE_ORDER:
            ref = contract["roles"][role]["web_blueprint_ref"]
            self.assertRegex(ref, r"^BP-[A-Z0-9-]+@[0-9]+\.[0-9]+\.[0-9]+$")
            blueprint = core_template_contract.resolve_web_blueprint_for_core(role)
            self.assertEqual(blueprint["ref"], ref)
            self.assertIn(role, blueprint["core_roles"])
            self.assertEqual(blueprint["shell_ref"], "G9-TABLET-SHELL-V1")


    @classmethod
    def setUpClass(cls):
        cls.projections = build_core_learning_data.build()["core_projections"]

    @classmethod
    def projection(cls, core, *, source_ref=None, microtopic_ref=None):
        matches = [
            row["projection"]
            for row in cls.projections
            if row["projection"]["core"] == core
            and (source_ref is None or row["source_ref"] == source_ref)
            and (
                microtopic_ref is None
                or (row["projection"].get("concept") or {}).get("microtopic_ref")
                == microtopic_ref
            )
        ]
        if len(matches) != 1:
            raise AssertionError(
                f"expected one {core} witness; found {len(matches)}"
            )
        return matches[0]

    def test_contract_covers_all_six_roles_and_passes_structural_audit(self):
        report = core_template_contract.audit(REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md")
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["roles_checked"], 6)
        self.assertEqual(report["contract_version"], "1.4")

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

    def test_core1a_optional_repair_and_core2_protected_assistance_are_explicit(self):
        roles = core_template_contract.load_contract(
            REPO / "Shared" / "roles" / "LEARNER-PRODUCT-TEMPLATES.md"
        )["roles"]
        core1a = roles["CORE1A"]
        self.assertNotIn("microtopic.misconceptions[]", core1a["required_inputs"])
        self.assertIn("FABRICATED_MISCONCEPTION_REPAIR", core1a["forbidden"])
        self.assertIn("BAND_AS_PANEL_COUNT", core1a["forbidden"])
        self.assertEqual(core1a["web_blueprint_ref"], "BP-CORE1A-CONSTRUCTION@1.8.0")

        core2 = roles["CORE2"]
        self.assertIn("PROTECTED_MOVE_COMPLETING_SUPPORT", core2["withheld_pre_attempt"])
        self.assertIn("CLOSED_DISCLOSURE_AS_SEMANTIC_PROTECTION", core2["forbidden"])
        self.assertIn("UNTRACKED_PRE_ATTEMPT_ASSISTANCE", core2["forbidden"])
        self.assertEqual(core2["web_blueprint_ref"], "BP-CORE2-SOURCE-QUESTION@1.11.0")

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


    def test_real_canonical_witnesses_match_role_template_boundaries(self):
        bucket = "BUCKET-PHY-KIN-2D-MOTION"
        concept = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"
        familiar = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
        transfer = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"

        core1 = self.projection("CORE1", source_ref=bucket)
        self.assertIsNotNone(core1["orientation"])
        self.assertIsNone(core1["concept"])
        self.assertIsNone(core1["application"])

        core1a = self.projection("CORE1A", microtopic_ref=concept)
        self.assertTrue(core1a["presentation"]["show_full_construction"])
        self.assertFalse(core1a["presentation"]["attempt_before_reveal"])
        self.assertTrue(core1a["concept"]["inferential_jump"])
        self.assertTrue(core1a["concept"]["teaching_path"])

        core1b = self.projection("CORE1B", microtopic_ref=concept)
        self.assertTrue(core1b["presentation"]["attempt_before_reveal"])
        self.assertFalse(core1b["presentation"]["show_full_construction"])
        self.assertTrue(core1b["concept"]["elicitation"]["predict"]["prompt"])
        self.assertTrue(core1b["concept"]["elicitation"]["attempt"]["produces"])

        core2_rows = [
            row["projection"]
            for row in self.projections
            if row["projection"]["core"] == "CORE2"
        ]
        self.assertEqual(
            core2_rows,
            [],
            "current production has no reviewed source-custody Core2; authored practice must not be promoted to fill that hold",
        )

        core2a = self.projection("CORE2A", source_ref=familiar)
        self.assertTrue(core2a["application"]["reasoning_route"])
        self.assertTrue(core2a["application"]["crux_move_ref"])
        self.assertIn("scaffolds", core2a["application"])
        self.assertTrue(core2a["application"]["solution"]["summary"])

        core2b = self.projection("CORE2B", source_ref=transfer)
        protected = core2b["application"]["transfer"]["protected_move_ref"]
        self.assertIn(protected, core2b["presentation"]["protected_move_refs"])
        safe_limit = core2b["presentation"]["pre_attempt_scaffold_limit"]
        for scaffold in core2b["application"]["scaffolds"][:safe_limit]:
            self.assertNotEqual(scaffold.get("supports_move_ref"), protected)
            self.assertEqual(scaffold.get("reveals"), "CONCEPT")
        self.assertTrue(core2b["application"]["solution"]["rubric"])
        self.assertIsNotNone(core2b["application"]["repair"])


if __name__ == "__main__":
    unittest.main()
