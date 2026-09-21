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
        self.assertNotIn("Subtract the observer velocity from the target velocity.", before)
        self.assertIn('data-reasoning-move="MOVE-REPRESENT"', after)
        self.assertIn('data-reasoning-move="MOVE-DECIDE"', after)
        self.assertIn('<span class="move-kind">Key decision</span>', after)
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



if __name__ == "__main__":
    unittest.main()
