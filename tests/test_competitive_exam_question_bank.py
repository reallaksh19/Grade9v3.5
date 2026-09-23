import json
import unittest
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
PHYSICS = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
CHEMISTRY = REPO / "Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json"
FIXTURE = REPO / "tests/fixtures/source_ingest/custody-manifest.json"

DONOR_PATHS = [
    REPO / "public/chemistry/redox/explorers/redox_reactions/jee_questions_data.js",
    REPO / "public/chemistry/some-basic-concepts/explorers/mole_concept/jee_questions_data.js",
    REPO / "public/physics/motion-1d/explorers/motion_in_1d/jee_questions_data.js",
    REPO / "public/physics/motion-in-2d/explorers/motions_in_2d/jee_questions_data.js",
]

ALLOWED_SCAFFOLD_KINDS = {"REPRESENT", "CONNECT", "EXECUTE"}
ALLOWED_REVEALS = {"CONCEPT", "METHOD", "ANSWER"}

CHEM_CAPS = {
    "CAP-CHEM-REDOX-OXIDATION-STATE",
    "CAP-CHEM-REDOX-DISPROPORTIONATION",
    "CAP-CHEM-REDOX-BALANCE-ELECTRON",
    "CAP-CHEM-MOLE-CONCENTRATION-TO-AMOUNT",
    "CAP-CHEM-STOICH-MOLE-RATIO",
    "CAP-CHEM-STOICH-MASS-MOLE",
}
CHEM_FAMILIES = {
    "FAM-CHEM-REDOX-REACTION-CLASSIFICATION",
    "FAM-CHEM-REDOX-ACIDIC-MEDIUM-BALANCE",
    "FAM-CHEM-MOLE-ELECTROLYTIC-STOICH",
    "FAM-CHEM-STOICH-AMOUNT-MAPPING",
}

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def ids_from_package(path, key):
    package = load(path)
    return {row["id"] for row in package.get(key, [])}

class CompetitiveExamQuestionBankV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = load(PHYSICS)
        cls.chemistry = load(CHEMISTRY)
        cls.manifests = [cls.physics, cls.chemistry]
        cls.questions = cls.physics["questions"] + cls.chemistry["questions"]
        cls.fixture = load(FIXTURE)

        cls.physics_caps = set()
        cls.physics_families = set()
        for path in [
            REPO / "Physics/library/phy-nlm-first-law.v1.json",
            REPO / "Physics/library/phy-kin-2d-motion.v1.json",
            REPO / "Physics/library/relative-motion.v1.json",
        ]:
            pkg = load(path)
            cls.physics_caps |= {row["id"] for row in pkg.get("capabilities", [])}
            cls.physics_families |= {row["id"] for row in pkg.get("question_families", [])}

    def test_fixture_native_manifest_shape(self):
        fixture_required = {
            "manifest_id", "version", "acquisition_ref", "target_package",
            "inspector_id", "inspection_sections", "access_status",
            "resource", "questions",
        }
        self.assertTrue(fixture_required.issubset(self.fixture))
        for manifest in self.manifests:
            self.assertTrue(fixture_required.issubset(manifest))
            self.assertEqual(manifest["version"], "2.0.0")
            self.assertEqual(manifest["access_status"], "FULL_ITEM_INSPECTED")
            self.assertFalse(manifest["extensions"]["grade9v3:generated_sets"])

    def test_expanded_counts_and_topic_balance(self):
        self.assertEqual(len(self.questions), 30)
        counts = Counter(
            q["extensions"]["grade9v3:analysis"]["concept_bucket"]
            for q in self.questions
        )
        self.assertEqual(counts["BUCKET-PHY-NLM-FIRST-LAW"], 7)
        self.assertEqual(counts["BUCKET-PHY-KIN-2D-MOTION"], 6)
        self.assertEqual(counts["BUCKET-RELATIVE-MOTION"], 2)
        self.assertEqual(counts["BUCKET-CHEM-REDOX-REACTIONS"], 7)
        self.assertEqual(counts["BUCKET-CHEM-MOLE-STOICHIOMETRY"], 8)

    def test_no_authored_fill_and_adaptation_parent_contract(self):
        for q in self.questions:
            self.assertEqual(q["origin"], "ADAPTED")
            self.assertEqual(q["extensions"]["grade9v3:provenance_class"], "PYQ_ADAPTED")
            custody = q["extensions"]["grade9v3:source_custody"]
            self.assertEqual(custody["source_status"], "PYQ_VERIFIED_PARENT")
            self.assertEqual(q["adaptation"]["parent_ref"], custody["parent_ref"])
            self.assertIn("stem", q["adaptation"]["changed_fields"])
            self.assertTrue(q["adaptation"]["reason"])
            self.assertEqual(custody["wording_custody"], "FAITHFUL_NON_VERBATIM_RESTATEMENT")

    def test_official_source_identity_is_complete_and_historical(self):
        for q in self.questions:
            custody = q["extensions"]["grade9v3:source_custody"]
            self.assertIn(custody["exam"], {"IIT-JEE", "JEE (Advanced)"})
            self.assertIsInstance(custody["year"], int)
            self.assertTrue(custody["paper"])
            self.assertTrue(custody["question_number"])
            self.assertTrue(custody["paper_url"].startswith(("https://jeeadv.ac.in/", "https://www.jeeadv.ac.in/")))
            self.assertEqual(custody["archive_url"], "https://jeeadv.ac.in/archive.html")
            self.assertEqual(custody["last_checked"], "2026-09-23")
            if custody["year"] <= 2012:
                self.assertEqual(custody["exam"], "IIT-JEE")
            if custody["year"] >= 2014:
                self.assertEqual(custody["exam"], "JEE (Advanced)")

    def test_ids_and_source_identities_are_unique(self):
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        source_ids = [
            (
                q["extensions"]["grade9v3:source_custody"]["exam"],
                q["extensions"]["grade9v3:source_custody"]["year"],
                q["extensions"]["grade9v3:source_custody"]["paper"],
                q["extensions"]["grade9v3:source_custody"]["question_number"],
            )
            for q in self.questions
        ]
        self.assertEqual(len(source_ids), len(set(source_ids)))

    def test_native_question_content_is_present(self):
        required = {
            "id", "version", "status", "source_refs", "evidence_refs",
            "extensions", "origin", "origin_ref", "original_identifier",
            "stem", "subparts", "options", "conditions", "figure_refs",
            "answer", "primary_capability_ref", "secondary_capability_refs",
            "family_ref", "adaptation", "exposure", "hints", "scaffolds",
        }
        for q in self.questions:
            self.assertTrue(required.issubset(q), q["id"])
            self.assertTrue(q["stem"].strip())
            self.assertIsInstance(q["options"], list)
            self.assertIsInstance(q["conditions"], list)
            self.assertGreaterEqual(len(q["conditions"]), 1)

    def test_source_hints_are_not_conflated_with_authored_scaffolds(self):
        for q in self.questions:
            self.assertEqual(q["hints"], [], q["id"])
            self.assertGreaterEqual(len(q["scaffolds"]), 2, q["id"])
            move_ids = {m["id"] for m in q["answer"]["reasoning_route"]}
            for scaffold in q["scaffolds"]:
                self.assertIn(scaffold["support_kind"], ALLOWED_SCAFFOLD_KINDS)
                self.assertIn(scaffold["reveals"], ALLOWED_REVEALS)
                self.assertIn(scaffold["supports_move_ref"], move_ids)

    def test_answer_solution_route_rubric_and_check_are_complete(self):
        for q in self.questions:
            answer = q["answer"]
            self.assertTrue(answer["summary"])
            self.assertGreaterEqual(len(answer["reasoning"]), 3)
            self.assertGreaterEqual(len(answer["reasoning_route"]), 3)
            self.assertTrue(answer["check"])
            self.assertEqual(answer["verification_status"], "INDEPENDENTLY_CHECKED")
            self.assertGreaterEqual(len(answer["rubric"]), 2)
            for row in answer["rubric"]:
                self.assertTrue(row["criterion"])
                self.assertTrue(row["evidence_of"])
            move_ids = {m["id"] for m in answer["reasoning_route"]}
            self.assertIn(answer["crux_move_ref"], move_ids)

    def test_difficulty_score_and_band_are_consistent(self):
        for q in self.questions:
            difficulty = q["extensions"]["grade9v3:analysis"]["difficulty"]
            score = sum(difficulty["components"].values())
            self.assertEqual(score, difficulty["score"])
            expected = "D1" if score <= 2 else "D2" if score <= 5 else "D3" if score <= 7 else "D4"
            self.assertEqual(difficulty["band"], expected)
            self.assertTrue(difficulty["basis"])
            self.assertGreater(q["extensions"]["grade9v3:analysis"]["expected_time_seconds"], 0)

    def test_capability_and_family_refs_resolve_or_are_explicit_local_proposals(self):
        for q in self.physics["questions"]:
            self.assertIn(q["primary_capability_ref"], self.physics_caps, q["id"])
            for ref in q["secondary_capability_refs"]:
                self.assertIn(ref, self.physics_caps, q["id"])
            self.assertIn(q["family_ref"], self.physics_families, q["id"])

        for q in self.chemistry["questions"]:
            self.assertIn(q["primary_capability_ref"], CHEM_CAPS, q["id"])
            for ref in q["secondary_capability_refs"]:
                self.assertIn(ref, CHEM_CAPS, q["id"])
            self.assertIn(q["family_ref"], CHEM_FAMILIES, q["id"])

        self.assertEqual(
            self.chemistry["extensions"]["grade9v3:concept_namespace"],
            "LOCAL_PROPOSAL_PENDING_CANONICAL_CHEMISTRY_LIBRARY",
        )

    def test_scope_excludes_circular_motion_and_relative_hold_is_closed(self):
        physics_text = json.dumps(self.physics).lower()
        self.assertNotIn("circular motion", physics_text)
        relative = [
            q for q in self.physics["questions"]
            if q["extensions"]["grade9v3:analysis"]["concept_bucket"] == "BUCKET-RELATIVE-MOTION"
        ]
        self.assertEqual(len(relative), 2)
        self.assertNotIn("acquisition_hold", physics_text)

    def test_transfer_is_analysis_only_not_generated_core2b_set(self):
        candidates = [
            q for q in self.questions
            if q["extensions"]["grade9v3:analysis"]["transfer_profile"]["core2b_candidate"]
        ]
        self.assertGreaterEqual(len(candidates), 5)
        for q in candidates:
            profile = q["extensions"]["grade9v3:analysis"]["transfer_profile"]
            self.assertIn(
                profile["dimension"],
                {"model_choice", "novelty", "reasoning_steps", "representation_translation"},
            )
            self.assertEqual(profile["classification"], "REAL_TRANSFER_CANDIDATE")
        for q in self.questions:
            self.assertEqual(q["exposure"][0]["core"], "CORE2A")

    def test_donor_registries_are_preserved(self):
        for path in DONOR_PATHS:
            self.assertTrue(path.exists(), path)
            self.assertGreater(path.stat().st_size, 0, path)

    def test_no_generated_practice_set_or_exam(self):
        for manifest in self.manifests:
            self.assertFalse(manifest["extensions"]["grade9v3:generated_sets"])
        text = json.dumps(self.manifests).lower()
        self.assertNotIn('"practice_set"', text)
        self.assertNotIn('"mock_exam"', text)

if __name__ == "__main__":
    unittest.main()
