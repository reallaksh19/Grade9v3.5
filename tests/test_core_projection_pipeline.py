"""STEP-TA10-002 structured application pipeline falsifiers."""
from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from Shared.library import intake, visual_support
from Physics.adapter import load as load_physics
from Shared.contracts import ContractError
from Shared.library.compile_inputs import compile_bucket, write
from Shared.library.resolve import build_index
from Shared.publication_host.host import publish
from Shared.publication_host.inputs import read_inputs

REPO = Path(__file__).resolve().parents[1]
PACKAGE_PATH = REPO / "Physics/library/relative-motion.v1.json"


def package_fixture() -> dict:
    return json.loads(PACKAGE_PATH.read_text(encoding="utf-8"))


def structured_question(package: dict) -> dict:
    question = next(row for row in package["questions"] if row["id"] == "Q-AUTHOR-REL-01")
    question["subparts"] = ["State the relative-velocity vector before finding its magnitude."]
    question["options"] = ["(6,-8) m/s", "(-6,8) m/s"]
    question["answer"]["subpart_answers"] = ["(6,-8) m/s"]
    question["answer"]["reasoning_route"] = [
        {
            "id": "MOVE-REPRESENT",
            "kind": "REPRESENT",
            "action": "Keep the declared east/north frame.",
            "why_valid": "Signed components only have meaning in a declared frame.",
            "inputs": ["v_A", "v_B"],
            "output": "common component frame",
            "representation_ref": "REP-REL-VECTOR",
            "visual_stage_ref": "VIS-REL-VECTOR-V1",
        },
        {
            "id": "MOVE-DECIDE",
            "kind": "DECIDE",
            "action": "Subtract the observer velocity from the target velocity.",
            "why_valid": "The ordered relative-velocity relation fixes the subtraction order.",
            "inputs": ["v_A", "v_B"],
            "output": "v_A/B = v_A - v_B",
        },
    ]
    question["answer"]["crux_move_ref"] = "MOVE-DECIDE"
    question["scaffolds"] = [
        {
            "text": "Keep the common axes visible before subtracting.",
            "support_kind": "REPRESENT",
            "reveals": "CONCEPT",
            "supports_move_ref": "MOVE-REPRESENT",
        }
    ]
    return question


class StructuredApplicationPipeline(unittest.TestCase):
    def test_intake_rejects_dangling_crux(self):
        package = package_fixture()
        q = structured_question(package)
        q["answer"]["crux_move_ref"] = "MOVE-MISSING"
        findings = intake.check(package)["findings"]
        self.assertTrue(any(f["point"] == "REASONING_ROUTE" and "does not resolve" in f["detail"]
                            for f in findings), findings)

    def test_intake_rejects_duplicate_move_ids(self):
        package = package_fixture()
        q = structured_question(package)
        q["answer"]["reasoning_route"][1]["id"] = "MOVE-REPRESENT"
        findings = intake.check(package)["findings"]
        self.assertTrue(any(f["point"] == "REASONING_ROUTE" and "unique" in f["detail"]
                            for f in findings), findings)

    def test_intake_requires_crux_to_name_a_decision_move(self):
        package = package_fixture()
        q = structured_question(package)
        q["answer"]["reasoning_route"][1]["kind"] = "TRANSFORM"
        findings = intake.check(package)["findings"]
        self.assertTrue(any(f["point"] == "REASONING_ROUTE" and "DECIDE" in f["detail"]
                            for f in findings), findings)

    def test_reasoning_move_visual_stage_ownership_is_validated(self):
        package = package_fixture()
        q = structured_question(package)
        q["answer"]["reasoning_route"][0]["visual_stage_ref"] = "VIS-NOT-IN-REP"
        findings = visual_support.findings(build_index([package]))
        self.assertTrue(any(f["code"] == "REASONING_VISUAL_STAGE_FOREIGN"
                            for f in findings), findings)

    def test_intake_rejects_scaffold_that_targets_protected_transfer_decision(self):
        package = package_fixture()
        q = structured_question(package)
        q["exposure"].append({"core": "CORE2B", "role": "NEW_TRANSFER", "artifact_ref": None})
        q["transfer"] = {
            "dimension": "model_choice",
            "statement": "Changed demand requires the learner to choose the subtraction order.",
            "builds_on": ["MIC-MEASURED-FROM"],
            "protected_move_ref": "MOVE-DECIDE",
        }
        q["scaffolds"][0]["supports_move_ref"] = "MOVE-DECIDE"
        findings = intake.check(package)["findings"]
        self.assertTrue(any(f["point"] == "TRANSFER" and "disclose" in f["detail"]
                            for f in findings), findings)

    def test_visual_support_validates_scaffold_stage_ownership(self):
        package = package_fixture()
        q = structured_question(package)
        q["scaffolds"][0]["visual_ref"] = "REP-REL-VECTOR"
        q["scaffolds"][0]["visual_stage_ref"] = "VIS-NOT-IN-REP"
        findings = visual_support.findings(build_index([package]))
        self.assertTrue(any(f["code"] == "SCAFFOLD_VISUAL_STAGE_FOREIGN"
                            for f in findings), findings)

    def test_compiler_preserves_source_shape_and_structured_application_truth(self):
        package = package_fixture()
        q = structured_question(package)
        self.assertTrue(intake.check(package)["admitted"], intake.check(package)["findings"])

        package_paths = sorted((REPO / "Physics/library").glob("*.json"))
        packages = [json.loads(path.read_text(encoding="utf-8")) for path in package_paths]
        packages = [copy.deepcopy(package) if p.get("package_id") == package["package_id"] else p
                    for p in packages]
        records = build_index(packages)
        compiled = compile_bucket(
            records,
            "BUCKET-RELATIVE-MOTION",
            topic_id="TEST-STRUCTURED-CORE",
            title="Structured projection test",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )
        blocks = [
            block
            for product in compiled["plan"]["products"]
            for unit in product["units"]
            for block in unit["blocks"]
            if block.get("source_question_id") == q["id"]
        ]
        core2a = next(block for block in blocks if block["id"].startswith("CORE2A-"))
        source_question = next(row for row in compiled["source"]["questions"] if row["id"] == q["id"])
        for field in ("subparts", "options", "conditions", "source_refs", "figure_refs", "hints"):
            self.assertEqual(source_question[field], q.get(field, []), field)
            self.assertEqual(core2a.get(field, []), q.get(field, []), field)
        self.assertEqual(core2a["answer"]["subparts"], q["answer"]["subpart_answers"])
        self.assertEqual(core2a["answer"]["reasoning_route"], q["answer"]["reasoning_route"])
        self.assertEqual(core2a["answer"]["crux_move_ref"], "MOVE-DECIDE")
        self.assertEqual(core2a["scaffolds"], q["scaffolds"])
        self.assertEqual(core2a["hints"], q["hints"])

    def test_compiler_preserves_new_transfer_exposure_and_protected_move(self):
        package = package_fixture()
        q = structured_question(package)
        q["exposure"].append({"core": "CORE2B", "role": "NEW_TRANSFER", "artifact_ref": None})
        q["transfer"] = {
            "dimension": "model_choice",
            "statement": "Changed demand requires the learner to choose the subtraction order.",
            "builds_on": ["MIC-MEASURED-FROM"],
            "protected_move_ref": "MOVE-DECIDE",
        }
        q["scaffolds"] = []
        self.assertTrue(intake.check(package)["admitted"], intake.check(package)["findings"])

        package_paths = sorted((REPO / "Physics/library").glob("*.json"))
        packages = [json.loads(path.read_text(encoding="utf-8")) for path in package_paths]
        packages = [copy.deepcopy(package) if p.get("package_id") == package["package_id"] else p
                    for p in packages]
        compiled = compile_bucket(
            build_index(packages),
            "BUCKET-RELATIVE-MOTION",
            topic_id="TEST-TRANSFER-CORE",
            title="Transfer projection test",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )
        blocks = [
            block
            for product in compiled["plan"]["products"]
            for unit in product["units"]
            for block in unit["blocks"]
            if block.get("source_question_id") == q["id"] and block["id"].startswith("CORE2B-")
        ]
        self.assertEqual(len(blocks), 1)
        self.assertEqual(blocks[0]["exposure_role"], "NEW_TRANSFER")
        self.assertEqual(blocks[0]["transfer"]["protected_move_ref"], "MOVE-DECIDE")


class PublicationBoundaryStructuredRefs(unittest.TestCase):
    def compiled(self, transfer=False):
        package = package_fixture()
        q = structured_question(package)
        if transfer:
            q["exposure"].append({"core": "CORE2B", "role": "NEW_TRANSFER", "artifact_ref": None})
            q["transfer"] = {
                "dimension": "model_choice",
                "statement": "Changed demand requires the learner to choose the subtraction order.",
                "builds_on": ["MIC-MEASURED-FROM"],
                "protected_move_ref": "MOVE-DECIDE",
            }
            q["scaffolds"] = []
        package_paths = sorted((REPO / "Physics/library").glob("*.json"))
        packages = [json.loads(path.read_text(encoding="utf-8")) for path in package_paths]
        packages = [copy.deepcopy(package) if p.get("package_id") == package["package_id"] else p
                    for p in packages]
        return compile_bucket(
            build_index(packages),
            "BUCKET-RELATIVE-MOTION",
            topic_id="TEST-PUBLICATION-STRUCTURED",
            title="Publication structured validation",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )

    def validate_after(self, mutate, *, transfer=False):
        compiled = self.compiled(transfer=transfer)
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
                if block.get("source_question_id") == "Q-AUTHOR-REL-01"
                and block["id"].startswith("CORE2B-" if transfer else "CORE2A-")
            )
            mutate(block)
            return read_inputs(plan, baseline, root, load_physics())

    def test_valid_structured_application_reaches_publication_boundary(self):
        ctx = self.validate_after(lambda block: None)
        self.assertIn("CORE2A-Q-AUTHOR-REL-01", ctx["objects"])

    def test_publication_boundary_rejects_dangling_crux(self):
        with self.assertRaises(ContractError) as raised:
            self.validate_after(
                lambda block: block["answer"].__setitem__("crux_move_ref", "MOVE-MISSING")
            )
        self.assertEqual("CRUX_MOVE_UNKNOWN", raised.exception.code)

    def test_publication_boundary_rejects_protected_move_scaffold_disclosure(self):
        def disclose(block):
            block["scaffolds"] = [{
                "text": "Use the subtraction order now.",
                "support_kind": "CONNECT",
                "reveals": "METHOD",
                "supports_move_ref": "MOVE-DECIDE",
            }]

        with self.assertRaises(ContractError) as raised:
            self.validate_after(disclose, transfer=True)
        self.assertEqual("PROTECTED_MOVE_DISCLOSED_BY_SCAFFOLD", raised.exception.code)


class LearnerFacingStructuredProjection(unittest.TestCase):
    def render(self, *, transfer=False):
        package = package_fixture()
        q = structured_question(package)
        if transfer:
            q["exposure"].append({"core": "CORE2B", "role": "NEW_TRANSFER", "artifact_ref": None})
            q["transfer"] = {
                "dimension": "model_choice",
                "statement": "Changed demand requires the learner to choose the subtraction order.",
                "builds_on": ["MIC-MEASURED-FROM"],
                "protected_move_ref": "MOVE-DECIDE",
            }
        self.assertTrue(intake.check(package)["admitted"], intake.check(package)["findings"])

        package_paths = sorted((REPO / "Physics/library").glob("*.json"))
        packages = [json.loads(path.read_text(encoding="utf-8")) for path in package_paths]
        packages = [copy.deepcopy(package) if p.get("package_id") == package["package_id"] else p
                    for p in packages]
        compiled = compile_bucket(
            build_index(packages),
            "BUCKET-RELATIVE-MOTION",
            topic_id="TEST-RENDER-STRUCTURED",
            title="Structured learner rendering",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )
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
            return {
                core: (root / "publication" / f"{core}.html").read_text(encoding="utf-8")
                for core in ("CORE2A", "CORE2B")
                if (root / "publication" / f"{core}.html").exists()
            }

    def test_core2a_scaffold_precedes_answer_and_crux_is_visibly_distinct(self):
        html = self.render()["CORE2A"]
        before, after = html.split('<section class="answer-section"', 1)
        self.assertIn("Support before you solve", before)
        self.assertIn("Keep the common axes visible before subtracting.", before)
        self.assertIn('data-support-kind="REPRESENT"', before)
        self.assertIn('data-reveals="CONCEPT"', before)
        self.assertNotIn("Subtract the observer velocity from the target velocity.", before)
        self.assertIn('data-reasoning-move="MOVE-REPRESENT"', after)
        self.assertIn('data-reasoning-move="MOVE-DECIDE"', after)
        self.assertIn('class="move-kind"', after)
        self.assertIn('>Key decision</span>', after)
        self.assertIn("<strong>Independent check:</strong>", after)

    def test_core2b_protected_decision_is_absent_from_pre_attempt_support(self):
        html = self.render(transfer=True)["CORE2B"]
        before, after = html.split('<section class="answer-section"', 1)
        self.assertIn("Support before you solve", before)
        self.assertIn('data-supports-move="MOVE-REPRESENT"', before)
        self.assertNotIn("MOVE-DECIDE", before)
        self.assertNotIn("Subtract the observer velocity from the target velocity.", before)
        self.assertIn('data-reasoning-move="MOVE-DECIDE"', after)
        self.assertIn("This decision was protected from pre-attempt scaffolding", after)



class Motion2DRealWitness(unittest.TestCase):
    """Read-only canonical Motion2D truth proves the structured pipeline end to end."""

    CONCEPT = "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"
    FAMILIAR = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"
    TRANSFER = "Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04"

    def package(self):
        path = REPO / "Physics/library/phy-kin-2d-motion.v1.json"
        package = json.loads(path.read_text(encoding="utf-8"))
        familiar = next(q for q in package["questions"] if q["id"] == self.FAMILIAR)
        transfer = next(q for q in package["questions"] if q["id"] == self.TRANSFER)

        familiar["answer"]["reasoning_route"] = [
            {
                "id": "MOVE-K2D-2A-REPRESENT",
                "kind": "REPRESENT",
                "action": "Separate horizontal and vertical equations while keeping one common elapsed time.",
                "why_valid": "The components evolve independently but describe the same stone during one event.",
                "inputs": ["u_x=15 m/s", "u_y=0", "Delta y=-20 m", "a_y=-10 m/s^2"],
                "output": "Two component equations coupled by one event time.",
            },
            {
                "id": "MOVE-K2D-2A-EVENT",
                "kind": "DECIDE",
                "action": "Use the vertical ground-contact condition to determine the flight time.",
                "why_valid": "Impact is defined by the known vertical displacement, so the y equation determines when the event occurs.",
                "inputs": ["Delta y=-20 m", "u_y=0", "a_y=-10 m/s^2"],
                "output": "t=2 s is the common impact time.",
            },
            {
                "id": "MOVE-K2D-2A-EXECUTE",
                "kind": "TRANSFORM",
                "action": "Reuse the common impact time in horizontal displacement and both velocity components.",
                "why_valid": "Range and impact velocity must refer to the same physical instant as ground contact.",
                "inputs": ["t=2 s", "u_x=15 m/s", "a_x=0", "a_y=-10 m/s^2"],
                "output": "Delta x=30 m and v=(15 i - 20 j) m/s.",
            },
            {
                "id": "MOVE-K2D-2A-VERIFY",
                "kind": "VERIFY",
                "action": "Check that horizontal speed changes range but not the ideal fall time.",
                "why_valid": "The vertical event equation contains no horizontal speed when a_x=0 and air resistance is neglected.",
                "inputs": ["vertical event equation", "a_x=0"],
                "output": "The result respects component independence and one shared clock.",
            },
        ]
        familiar["answer"]["crux_move_ref"] = "MOVE-K2D-2A-EVENT"
        familiar["scaffolds"] = [
            {
                "text": "Write separate x and y columns, but draw one shared t between them; place the 20 m drop in the y column.",
                "support_kind": "REPRESENT",
                "reveals": "CONCEPT",
                "supports_move_ref": "MOVE-K2D-2A-REPRESENT",
            }
        ]

        transfer["answer"]["reasoning_route"] = [
            {
                "id": "MOVE-K2D-2B-REPRESENT",
                "kind": "REPRESENT",
                "action": "List the post-release acceleration components before selecting a named motion model.",
                "why_valid": "Model validity depends on the actual post-release forces and resulting acceleration components.",
                "inputs": ["a_x=2 m/s^2", "a_y=-g", "rocket thrust remains active"],
                "output": "The motion has nonzero horizontal acceleration and gravitational vertical acceleration.",
            },
            {
                "id": "MOVE-K2D-2B-DECIDE",
                "kind": "DECIDE",
                "action": "Reject the standard gravity-only projectile specialization.",
                "why_valid": "That specialization requires a_x=0 after release, but the active motor gives a_x=2 m/s^2.",
                "inputs": ["standard projectile condition a_x=0", "actual a_x=2 m/s^2"],
                "output": "The familiar projectile specialization is invalid for this interval.",
            },
            {
                "id": "MOVE-K2D-2B-CONNECT",
                "kind": "CONNECT",
                "action": "Use the parent two-dimensional constant-acceleration model.",
                "why_valid": "Both acceleration components are stated constant, so the more general component model remains valid.",
                "inputs": ["a_x=2 m/s^2", "a_y=-g"],
                "output": "Use constant-acceleration equations independently in x and y with one common time.",
            },
            {
                "id": "MOVE-K2D-2B-VERIFY",
                "kind": "VERIFY",
                "action": "Check the switch-off boundary.",
                "why_valid": "If horizontal thrust ends and drag is negligible, a_x returns to zero and the standard projectile specialization becomes valid again.",
                "inputs": ["motor off", "drag negligible"],
                "output": "The model choice changes exactly when its defining condition changes.",
            },
        ]
        transfer["answer"]["crux_move_ref"] = "MOVE-K2D-2B-DECIDE"
        transfer["scaffolds"] = [
            {
                "text": "Before naming a model, list the acceleration components that remain after release.",
                "support_kind": "REPRESENT",
                "reveals": "CONCEPT",
                "supports_move_ref": "MOVE-K2D-2B-REPRESENT",
            }
        ]
        transfer["transfer"]["protected_move_ref"] = "MOVE-K2D-2B-DECIDE"
        return package

    def compiled(self):
        package = self.package()
        report = intake.check(package)
        self.assertTrue(report["admitted"], report["findings"])
        packages = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in sorted((REPO / "Physics/library").glob("*.json"))
        ]
        packages = [
            copy.deepcopy(package) if p.get("package_id") == package["package_id"] else p
            for p in packages
        ]
        return compile_bucket(
            build_index(packages),
            "BUCKET-PHY-KIN-2D-MOTION",
            topic_id="TEST-MOTION2D-STRUCTURED",
            title="Motion in 2D structured witness",
            subject="Physics",
            practice_control={"mode": "DESIGN_PREVIEW", "purpose": "PRACTICE"},
        )

    def test_real_motion2d_core1a_and_core1b_share_one_concept_obligation(self):
        package = self.package()
        compiled = self.compiled()
        obligation = f"OB-{self.CONCEPT}"
        concept = next(row for row in package["microtopics"] if row["id"] == self.CONCEPT)

        core1a = next(row for row in compiled["plan"]["products"] if row["core"] == "CORE1A")
        core1b = next(row for row in compiled["plan"]["products"] if row["core"] == "CORE1B")
        a_blocks = core1a["units"][0]["blocks"]
        b_blocks = core1b["units"][0]["blocks"]

        declarative = next(
            block for block in a_blocks
            if block.get("obligation_ids") == [obligation] and block["kind"] == "TEXT"
        )
        ask_index = next(
            i for i, block in enumerate(b_blocks)
            if block["id"] == f"CORE1B-{self.CONCEPT}-ASK"
        )
        reveal_index = next(
            i for i, block in enumerate(b_blocks)
            if block["id"] == f"CORE1B-{self.CONCEPT}-ASK-REVEAL"
        )
        ask = b_blocks[ask_index]
        reveal = b_blocks[reveal_index]

        self.assertIn(concept["inferential_jump"], declarative["text"])
        self.assertEqual([obligation], ask["obligation_ids"])
        self.assertEqual([obligation], reveal["obligation_ids"])
        self.assertLess(ask_index, reveal_index)
        self.assertEqual("ELICITED_REVEAL", reveal["placement"])
        self.assertEqual(ask["id"], reveal["reveals_block_id"])
        self.assertNotIn(concept["inferential_jump"], ask["text"])
        self.assertIn(
            "What separates between axes, and what must stay common",
            reveal["text"],
        )

    def practice_only(self, compiled):
        """Project the real bucket to the two practice products this witness proves.

        Motion2D currently also advertises a compact Core1 orientation product whose
        authoring gap is unrelated to the Core2 projection contract. Keep publication
        validation strict by pruning the plan and obligations together rather than
        teaching the host to ignore that missing product.
        """
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
            atom_id for obligation in obligations for atom_id in obligation["source_atom_ids"]
        }
        compiled["source"]["atoms"] = [
            atom for atom in compiled["source"]["atoms"] if atom["id"] in accounted
        ]
        return compiled

    def test_real_motion2d_questions_survive_compile_with_distinct_crux_and_protection(self):
        compiled = self.compiled()
        blocks = {
            block["source_question_id"]: block
            for product in compiled["plan"]["products"]
            for unit in product["units"]
            for block in unit["blocks"]
            if block.get("source_question_id") in {self.FAMILIAR, self.TRANSFER}
        }
        familiar = blocks[self.FAMILIAR]
        transfer = blocks[self.TRANSFER]
        self.assertEqual("MOVE-K2D-2A-EVENT", familiar["answer"]["crux_move_ref"])
        self.assertEqual("MOVE-K2D-2B-DECIDE", transfer["answer"]["crux_move_ref"])
        self.assertEqual("MOVE-K2D-2B-DECIDE", transfer["transfer"]["protected_move_ref"])
        self.assertEqual("NEW_TRANSFER", transfer["exposure_role"])
        self.assertEqual(self.FAMILIAR, transfer["transfer"]["builds_on"][0])

    def test_real_motion2d_publish_keeps_protected_decision_after_attempt(self):
        compiled = self.practice_only(self.compiled())
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

        familiar_before, familiar_answer = familiar.split('<section class="answer-section"', 1)
        self.assertIn("one shared t", familiar_before)
        self.assertNotIn("Use the vertical ground-contact condition", familiar_before)
        self.assertIn('data-reasoning-move="MOVE-K2D-2A-EVENT"', familiar_answer)
        self.assertIn("Key decision", familiar_answer)

        transfer_before, transfer_answer = transfer.split('<section class="answer-section"', 1)
        self.assertIn("list the acceleration components", transfer_before.lower())
        self.assertNotIn("Reject the standard gravity-only projectile specialization", transfer_before)
        self.assertNotIn("MOVE-K2D-2B-DECIDE", transfer_before)
        self.assertIn('data-reasoning-move="MOVE-K2D-2B-DECIDE"', transfer_answer)
        self.assertIn("protected from pre-attempt scaffolding", transfer_answer)



if __name__ == "__main__":
    unittest.main()
