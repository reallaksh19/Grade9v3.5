"""Canonical Motion-in-2D production proof for Issue #174."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from Physics.adapter import load as load_physics
from Shared.contracts import ContractError
from Shared.library import intake, visual_support
from Shared.library.compile_inputs import compile_bucket, write
from Shared.library.resolve import build_index
from Shared.publication_host.host import publish
from Shared.publication_host.inputs import read_inputs

REPO = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
MATRIX_PATH = REPO / "Physics/matrices/phy-kin-2d-motion.rungs.json"

FAMILIAR = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
TRANSFER = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"
REP_SHARED = "REP-KIN-2D-SHARED-CLOCK"
REP_EVENT = "REP-KIN-2D-EVENT-CLOCK"
REP_MODEL = "REP-KIN-2D-PROJECTILE-MODEL"
FAMILIAR_CRUX = "R-KIN-LAUNCH-EVENT"
TRANSFER_CRUX = "R-KIN-TRANSFER-MODEL"


def load_package() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def load_matrix() -> dict:
    return json.loads(MATRIX_PATH.read_text(encoding="utf-8"))


def all_packages_with(package: dict) -> list[dict]:
    packages = [
        json.loads(path.read_text(encoding="utf-8"))
        for path in sorted((REPO / "Physics/library").glob("*.json"))
    ]
    return [
        copy.deepcopy(package) if row.get("package_id") == package["package_id"] else row
        for row in packages
    ]


def compile_motion(package: dict) -> dict:
    return compile_bucket(
        build_index(all_packages_with(package)),
        "BUCKET-PHY-KIN-2D-MOTION",
        topic_id="TEST-MOTION2D-CANONICAL",
        title="Motion in 2D canonical production proof",
        subject="Physics",
        practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
    )


def practice_only(compiled: dict) -> dict:
    """Keep strict publication validation focused on the two practice products."""
    compiled = copy.deepcopy(compiled)
    selected = {"CORE2A", "CORE2B"}
    compiled["plan"]["products"] = [
        product for product in compiled["plan"]["products"]
        if product["core"] in selected
    ]
    compiled["baseline"]["selected_cores"] = [
        core for core in compiled["baseline"]["selected_cores"] if core in selected
    ]
    obligations = []
    for obligation in compiled["baseline"]["obligations"]:
        required = [core for core in obligation["required_cores"] if core in selected]
        if not required:
            continue
        row = copy.deepcopy(obligation)
        row["required_cores"] = required
        obligations.append(row)
    compiled["baseline"]["obligations"] = obligations
    compiled["baseline"]["required_questions"] = [
        row for row in compiled["baseline"]["required_questions"]
        if row["core"] in selected
    ]
    accounted = {
        atom_id
        for obligation in obligations
        for atom_id in obligation["source_atom_ids"]
    }
    compiled["source"]["atoms"] = [
        atom for atom in compiled["source"]["atoms"] if atom["id"] in accounted
    ]
    return compiled


class Motion2DCanonicalData(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = load_package()
        cls.matrix = load_matrix()
        cls.questions = {row["id"]: row for row in cls.package["questions"]}
        cls.microtopics = {row["id"]: row for row in cls.package["microtopics"]}
        cls.resources = {row["id"]: row for row in cls.package["resources"]}
        cls.representations = {row["id"]: row for row in cls.package["representations"]}

    def test_matrix_remains_family_authority(self):
        family = self.matrix["family"]
        self.assertEqual(
            family["difficult_move"],
            "Keeping model choice and event choice separate: first decide which component equations are valid, then decide what condition identifies the requested instant, while preserving one common clock.",
        )
        self.assertIn("one-clock consistency", family["independent_check"])
        self.assertEqual(
            [row["level"] for row in family["support_ladder"]],
            ["high", "medium", "low"],
        )
        for rep in self.representations.values():
            self.assertNotIn("invariant_demand", rep)
            self.assertNotIn("difficult_move", rep)
            self.assertNotIn("independent_check", rep)
            self.assertNotIn("support_ladder", rep)

    def test_three_canonical_representations_bind_existing_activities(self):
        expected = {
            REP_SHARED: "ACT-KIN-2D-SHARED-CLOCK",
            REP_EVENT: "ACT-KIN-2D-EVENT-CLOCK",
            REP_MODEL: "ACT-KIN-2D-PROJECTILE-MODEL-GATE",
        }
        # The canonical three must exist; item-specific figures (ALL-FIGURE-SPECIFIC) may be added beside them.
        self.assertLessEqual(set(expected), set(self.representations))
        for rep_id, activity_id in expected.items():
            rep = self.representations[rep_id]
            self.assertEqual(rep["interactive_resource_refs"], [activity_id])
            self.assertIn(activity_id, self.resources)
            stages = [row["id"] for row in rep["reveal_stages"]]
            self.assertEqual(len(stages), len(set(stages)))
            self.assertEqual(
                {row["support_level"] for row in rep["support_stage_map"]},
                {"low", "medium", "high"},
            )
            for binding in rep["support_stage_map"]:
                self.assertIn(binding["visual_stage_ref"], stages)

    def test_microtopic_bindings_preserve_rep_reuse_and_primary_activity_step_ownership(self):
        expected = {
            "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS": [REP_SHARED],
            "MIC-PHY-KIN-2D-CONSTANT-ACCELERATION": [REP_SHARED, REP_EVENT],
            "MIC-PHY-KIN-PROJECTILE-MODEL": [REP_SHARED, REP_EVENT, REP_MODEL],
        }
        for micro_id, rep_ids in expected.items():
            self.assertEqual(self.microtopics[micro_id]["representation_refs"], rep_ids)

        primary_owners = {
            REP_SHARED: "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS",
            REP_EVENT: "MIC-PHY-KIN-2D-CONSTANT-ACCELERATION",
            REP_MODEL: "MIC-PHY-KIN-PROJECTILE-MODEL",
        }
        for rep_id, micro_id in primary_owners.items():
            activity_id = self.representations[rep_id]["interactive_resource_refs"][0]
            activity_steps = set(
                self.resources[activity_id]["extensions"]["topic_atlas"]["teaching_step_refs"]
            )
            micro_steps = {row["id"] for row in self.microtopics[micro_id]["teaching_path"]}
            self.assertTrue(activity_steps)
            self.assertTrue(activity_steps <= micro_steps)

    def test_familiar_route_has_event_choice_crux_and_preserves_source_hints(self):
        q = self.questions[FAMILIAR]
        self.assertEqual(
            q["hints"],
            [
                {
                    "text": "Which component equation contains the known 20 m drop?",
                    "reveals": "CONCEPT",
                },
                {
                    "text": "Find the common impact time from y first, then use that same time in x and in the velocity components.",
                    "reveals": "METHOD",
                },
            ],
        )
        route = {row["id"]: row for row in q["answer"]["reasoning_route"]}
        self.assertEqual(q["answer"]["crux_move_ref"], FAMILIAR_CRUX)
        self.assertEqual(route[FAMILIAR_CRUX]["kind"], "DECIDE")
        self.assertEqual(route[FAMILIAR_CRUX]["representation_ref"], REP_EVENT)
        self.assertEqual(route[FAMILIAR_CRUX]["visual_stage_ref"], "VIS-KIN-2D-EVENT-V2")
        self.assertEqual(q["answer"]["difficult_move"], 0)
        self.assertEqual(
            [row["supports_move_ref"] for row in q["scaffolds"]],
            ["R-KIN-LAUNCH-REPRESENT", FAMILIAR_CRUX],
        )

    def test_transfer_protects_model_choice_and_preserves_source_hint(self):
        q = self.questions[TRANSFER]
        self.assertEqual(
            q["hints"],
            [
                {
                    "text": "Which post-release assumption makes a_x=0 in the standard projectile model, and is it true here?",
                    "reveals": "CONCEPT",
                }
            ],
        )
        route = {row["id"]: row for row in q["answer"]["reasoning_route"]}
        protected = q["transfer"]["protected_move_ref"]
        self.assertEqual(protected, TRANSFER_CRUX)
        self.assertEqual(q["answer"]["crux_move_ref"], protected)
        self.assertEqual(route[protected]["kind"], "DECIDE")
        self.assertEqual(route[protected]["representation_ref"], REP_MODEL)
        self.assertEqual(route[protected]["visual_stage_ref"], "VIS-KIN-2D-PROJ-V3")
        self.assertEqual(q["answer"]["difficult_move"], 2)
        self.assertNotIn(
            protected,
            {row["supports_move_ref"] for row in q["scaffolds"]},
        )

        rep = self.representations[REP_MODEL]
        stages = [row["id"] for row in rep["reveal_stages"]]
        protected_index = stages.index(route[protected]["visual_stage_ref"])
        for scaffold in q["scaffolds"]:
            self.assertEqual(scaffold["visual_ref"], REP_MODEL)
            self.assertLess(stages.index(scaffold["visual_stage_ref"]), protected_index)

    def test_intake_and_visual_support_accept_real_motion_package(self):
        report = intake.check(self.package)
        self.assertTrue(report["admitted"], report["findings"])
        findings = visual_support.findings(build_index(all_packages_with(self.package)))
        relevant = [
            row for row in findings
            if "KIN-2D" in json.dumps(row, sort_keys=True)
        ]
        self.assertEqual([], relevant)

    def test_compiler_preserves_routes_scaffolds_hints_and_transfer_protection(self):
        compiled = compile_motion(self.package)
        blocks = {
            block["source_question_id"]: block
            for product in compiled["plan"]["products"]
            for unit in product["units"]
            for block in unit["blocks"]
            if block.get("source_question_id") in {FAMILIAR, TRANSFER}
        }
        familiar = blocks[FAMILIAR]
        transfer = blocks[TRANSFER]
        self.assertEqual(familiar["answer"]["crux_move_ref"], FAMILIAR_CRUX)
        self.assertEqual(transfer["answer"]["crux_move_ref"], TRANSFER_CRUX)
        self.assertEqual(transfer["transfer"]["protected_move_ref"], TRANSFER_CRUX)
        self.assertEqual(familiar["hints"], self.questions[FAMILIAR]["hints"])
        self.assertEqual(transfer["hints"], self.questions[TRANSFER]["hints"])
        self.assertEqual(
            [row["supports_move_ref"] for row in familiar["scaffolds"]],
            ["R-KIN-LAUNCH-REPRESENT", FAMILIAR_CRUX],
        )

    def test_publication_boundary_rejects_protected_move_leakage(self):
        compiled = practice_only(compile_motion(self.package))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(compiled, root)
            plan = json.loads((root / "plan.json").read_text(encoding="utf-8"))
            baseline = json.loads((root / "baseline.json").read_text(encoding="utf-8"))
            block = next(
                block
                for product in plan["products"]
                for unit in product["units"]
                for block in unit["blocks"]
                if block.get("source_question_id") == TRANSFER
                and block["id"].startswith("CORE2B-")
            )
            block["scaffolds"] = [{
                "text": "Use the model decision now.",
                "support_kind": "CONNECT",
                "reveals": "METHOD",
                "supports_move_ref": TRANSFER_CRUX,
            }]
            with self.assertRaises(ContractError) as raised:
                read_inputs(plan, baseline, root, load_physics())
        self.assertEqual("PROTECTED_MOVE_DISCLOSED_BY_SCAFFOLD", raised.exception.code)

    def test_publication_renders_familiar_support_and_protects_transfer_decision(self):
        compiled = practice_only(compile_motion(self.package))
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            write(compiled, root / "inputs")
            publish(
                root / "inputs/plan.json",
                root / "inputs/baseline.json",
                root / "inputs",
                root / "publication",
                load_physics(),
            )
            familiar = (root / "publication/CORE2A.html").read_text(encoding="utf-8")
            transfer = (root / "publication/CORE2B.html").read_text(encoding="utf-8")

        familiar_before, familiar_after = familiar.split('<section class="answer-section"', 1)
        self.assertIn("20 m drop", familiar_before)
        self.assertIn(f'data-supports-move="{FAMILIAR_CRUX}"', familiar_before)
        self.assertNotIn(
            "Use the vertical ground-contact condition Delta y=-20 m to determine the flight time",
            familiar_before,
        )
        self.assertIn(f'data-reasoning-move="{FAMILIAR_CRUX}"', familiar_after)
        self.assertIn("Key decision", familiar_after)

        transfer_before, transfer_after = transfer.split('<section class="answer-section"', 1)
        self.assertIn("post-release interactions", transfer_before.lower())
        self.assertNotIn(TRANSFER_CRUX, transfer_before)
        self.assertNotIn(
            "Reject the standard gravity-only projectile specialization",
            transfer_before,
        )
        self.assertIn(f'data-reasoning-move="{TRANSFER_CRUX}"', transfer_after)
        self.assertIn("protected from pre-attempt scaffolding", transfer_after)


if __name__ == "__main__":
    unittest.main()
