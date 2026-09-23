import json
import re
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PHYS_BANK = ROOT / "Physics/library/exam-bank/competitive-exam-question-bank.v1.json"
CHEM_BANK = ROOT / "Chemistry/library/exam-bank/competitive-exam-question-bank.v1.json"
LEDGER = ROOT / "docs/question-bank/pass1/source-acquisition-ledger.json"

ALLOWED_PROVENANCE = {"PYQ_VERIFIED", "PYQ_ADAPTED", "SOURCE_UNVERIFIED"}
CANONICAL_PROVENANCE = {"PYQ_VERIFIED", "PYQ_ADAPTED"}
ALLOWED_OFFICIAL_HOSTS = {"jeeadv.ac.in", "www.jeeadv.ac.in"}
DIFFICULTY_MAP = {0: "D1", 1: "D1", 2: "D1", 3: "D2", 4: "D2", 5: "D2", 6: "D3", 7: "D3", 8: "D4", 9: "D4", 10: "D4"}


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def record_ids(package):
    return {
        "buckets": {x["id"] for x in package.get("buckets", [])},
        "capabilities": {x["id"] for x in package.get("capabilities", [])},
        "families": {x["id"] for x in package.get("question_families", [])},
    }


class CompetitiveExamQuestionBankTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = load_json(PHYS_BANK)
        cls.chemistry = load_json(CHEM_BANK)
        cls.banks = [cls.physics, cls.chemistry]
        cls.questions = [q for bank in cls.banks for q in bank["questions"]]
        cls.sources = {
            source["id"]: source
            for bank in cls.banks
            for source in bank["source_records"]
        }
        cls.ledger = load_json(LEDGER)

        nlm = load_json(ROOT / "Physics/library/phy-nlm-first-law.v1.json")
        motion2d = load_json(ROOT / "Physics/library/phy-kin-2d-motion.v1.json")
        relative = load_json(ROOT / "Physics/library/relative-motion.v1.json")
        cls.physics_ids = {
            "buckets": set(),
            "capabilities": set(),
            "families": set(),
        }
        for package in (nlm, motion2d, relative):
            ids = record_ids(package)
            for kind in cls.physics_ids:
                cls.physics_ids[kind] |= ids[kind]

        resolution = cls.chemistry["concept_resolution"]
        cls.chem_ids = {
            "buckets": {x["id"] for x in resolution["proposed_buckets"]},
            "capabilities": {x["id"] for x in resolution["proposed_capabilities"]},
            "families": {x["id"] for x in resolution["proposed_families"]},
        }

    def test_pass1_contains_no_authored_questions_or_generated_sets(self):
        for bank in self.banks:
            self.assertFalse(bank["generated_sets"])
            self.assertFalse(bank["source_policy"]["authored_questions_allowed"])
        for question in self.questions:
            self.assertIn(question["provenance_status"], CANONICAL_PROVENANCE)
            self.assertNotEqual(question["provenance_status"], "AUTHORED")

    def test_provenance_classes_are_exact_and_unverified_is_not_promoted(self):
        for bank in self.banks:
            self.assertEqual(set(bank["source_policy"]["provenance_classes"]), ALLOWED_PROVENANCE)
        for question in self.questions:
            self.assertNotEqual(question["provenance_status"], "SOURCE_UNVERIFIED")
        for donor in self.ledger["donor_candidates"]:
            self.assertEqual(donor["pass1_provenance_status"], "SOURCE_UNVERIFIED")
            self.assertEqual(donor["promotion_status"], "QUARANTINED_DONOR_ONLY")

    def test_verified_question_source_refs_resolve_to_official_records(self):
        for question in self.questions:
            self.assertTrue(question["source_refs"])
            for ref in question["source_refs"]:
                self.assertIn(ref, self.sources)
                source = self.sources[ref]
                if question["provenance_status"] == "PYQ_VERIFIED":
                    self.assertEqual(source["authority_class"], "OFFICIAL_EXAM_ORGANIZER_ARCHIVE")
                    self.assertEqual(source["verification_status"], "PYQ_VERIFIED")
                    self.assertIn(urlparse(source["source_url"]).hostname, ALLOWED_OFFICIAL_HOSTS)
                    self.assertIn(urlparse(source["archive_url"]).hostname, ALLOWED_OFFICIAL_HOSTS)

    def test_original_identifiers_are_complete_without_invented_shift_or_number(self):
        seen = set()
        for question in self.questions:
            ident = question["original_identifier"]
            for field in ("exam", "year", "paper", "question_number"):
                self.assertNotIn(ident.get(field), (None, ""))
            key = (ident["exam"], ident["year"], ident["paper"], ident.get("section"), ident["question_number"])
            self.assertNotIn(key, seen)
            seen.add(key)
            if ident["year"] in {2007, 2008, 2011}:
                self.assertEqual(ident["exam"], "IIT-JEE")
            if ident["year"] == 2023:
                self.assertEqual(ident["exam"], "JEE (Advanced)")
            # Unknown session/shift values must remain null, not be fabricated placeholders.
            for field in ("session", "shift"):
                if field in ident and ident[field] is not None:
                    self.assertFalse(re.search(r"unknown|assumed|tbd", str(ident[field]), re.I))

    def test_difficulty_score_is_component_sum_and_band_matches_rubric(self):
        expected_components = {
            "concept_model_selection",
            "representation_translation",
            "reasoning_chain_length",
            "algebra_computational_load",
            "trap_exception_sensitivity",
        }
        for question in self.questions:
            difficulty = question["difficulty"]
            components = difficulty["components"]
            self.assertEqual(set(components), expected_components)
            for value in components.values():
                self.assertIsInstance(value, int)
                self.assertGreaterEqual(value, 0)
                self.assertLessEqual(value, 2)
            score = sum(components.values())
            self.assertEqual(difficulty["score"], score)
            self.assertEqual(difficulty["band"], DIFFICULTY_MAP[score])
            self.assertTrue(difficulty["basis"].strip())
            self.assertGreater(question["expected_time_seconds"], 0)

    def test_concept_bucket_capability_and_family_resolution(self):
        for question in self.physics["questions"]:
            self.assertIn(question["concept_bucket"], self.physics_ids["buckets"])
            self.assertIn(question["family_ref"], self.physics_ids["families"])
            self.assertIn(question["primary_capability_ref"], self.physics_ids["capabilities"])
            for ref in question["secondary_capability_refs"]:
                self.assertIn(ref, self.physics_ids["capabilities"])

        self.assertEqual(
            self.chemistry["concept_resolution"]["status"],
            "LOCAL_PROPOSALS_PENDING_CANONICAL_CHEMISTRY_LIBRARY",
        )
        for question in self.chemistry["questions"]:
            self.assertIn(question["concept_bucket"], self.chem_ids["buckets"])
            self.assertIn(question["family_ref"], self.chem_ids["families"])
            self.assertIn(question["primary_capability_ref"], self.chem_ids["capabilities"])
            for ref in question["secondary_capability_refs"]:
                self.assertIn(ref, self.chem_ids["capabilities"])

    def test_answer_verification_is_present_and_never_exam_label_based(self):
        allowed = {
            "SOURCE_KEY_AND_INDEPENDENT_CHECK",
            "INDEPENDENTLY_SOLVED_NO_OFFICIAL_KEY_LOCATED",
        }
        for question in self.questions:
            verification = question["answer_verification"]
            self.assertIn(verification["status"], allowed)
            self.assertTrue(verification["independent_check"].strip())
            self.assertNotIn(question["original_identifier"]["exam"], question["difficulty"]["basis"])
            if verification["status"] == "SOURCE_KEY_AND_INDEPENDENT_CHECK":
                self.assertIsNotNone(question["source_answer"]["value"])
            else:
                self.assertIn("verified_value", verification)
                self.assertIsNotNone(verification["verified_value"])

    def test_adaptation_parent_contract(self):
        all_ids = {q["id"] for q in self.questions}
        for question in self.questions:
            if question["provenance_status"] != "PYQ_ADAPTED":
                continue
            self.assertIn(question.get("parent_ref"), all_ids)
            self.assertTrue(question.get("changed_fields"))
            self.assertEqual(len(question["changed_fields"]), len(set(question["changed_fields"])))

    def test_variant_clusters_and_shared_context_resolve(self):
        cluster_rows = self.chemistry.get("variant_clusters", [])
        cluster_ids = {x["id"] for x in cluster_rows}
        context_ids = {x["id"] for x in self.chemistry.get("shared_source_contexts", [])}
        question_ids = {q["id"] for q in self.chemistry["questions"]}
        for question in self.chemistry["questions"]:
            if "variant_cluster_ref" in question:
                self.assertIn(question["variant_cluster_ref"], cluster_ids)
            if "shared_context_ref" in question:
                self.assertIn(question["shared_context_ref"], context_ids)
        for cluster in cluster_rows:
            self.assertTrue(set(cluster["member_refs"]).issubset(question_ids))
            if cluster.get("shared_context_ref"):
                self.assertIn(cluster["shared_context_ref"], context_ids)
            self.assertIsNone(cluster.get("parent_ref"))

    def test_duplicate_ids_and_source_identity_duplicates_are_rejected(self):
        ids = [q["id"] for q in self.questions]
        self.assertEqual(len(ids), len(set(ids)))
        identities = [
            (
                q["original_identifier"]["exam"],
                q["original_identifier"]["year"],
                q["original_identifier"]["paper"],
                q["original_identifier"]["question_number"],
            )
            for q in self.questions
        ]
        self.assertEqual(len(identities), len(set(identities)))

    def test_source_text_custody_is_locator_backed_and_not_a_reconstructed_original(self):
        for question in self.questions:
            custody = question["source_text_custody"]
            self.assertEqual(custody["mode"], "EXTERNAL_REFERENCE")
            self.assertIsNone(custody["verbatim_stem"])
            self.assertIsNone(custody["verbatim_options"])
            self.assertTrue(custody["conditions_preserved_by_locator"])
            self.assertTrue(question["stem_summary"].strip())
            self.assertEqual(question["reasoning_route_origin"], "INDEPENDENT_ANALYSIS_NOT_SOURCE_HINT")

    def test_scope_excludes_circular_motion_and_holds_unverified_1d_relative_motion(self):
        for question in self.physics["questions"]:
            text = " ".join([
                question["topic"],
                question["stem_summary"],
                question["stable_crux_move"],
            ]).lower()
            self.assertNotIn("circular motion", text)
            self.assertNotIn("centripetal", text)

        relative_questions = [
            q for q in self.physics["questions"]
            if q["concept_bucket"] == "BUCKET-RELATIVE-MOTION"
        ]
        self.assertEqual(relative_questions, [])
        holds = {x["concept_bucket"]: x for x in self.physics["coverage_holds"]}
        self.assertEqual(holds["BUCKET-RELATIVE-MOTION"]["status"], "NO_PYQ_VERIFIED_ACCEPTED")

    def test_donor_registries_are_preserved(self):
        for inventory in self.ledger["donor_inventories"]:
            self.assertTrue((ROOT / inventory["path"]).is_file())
            self.assertEqual(inventory["disposition"], "PRESERVED_AS_DONOR_EVIDENCE_NOT_DELETED")

    def test_transfer_profiles_distinguish_real_transfer_from_variation(self):
        allowed = {"REAL_TRANSFER_CANDIDATE", "SAME_FAMILY_VARIATION"}
        for question in self.questions:
            profile = question["transfer_profile"]
            self.assertIn(profile["classification"], allowed)
            for field in ("model_choice", "representation_translation", "novelty"):
                self.assertIsInstance(profile[field], int)
                self.assertGreaterEqual(profile[field], 0)
                self.assertLessEqual(profile[field], 2)
            self.assertGreaterEqual(profile["reasoning_steps"], 1)
            self.assertEqual(
                profile["core2b_candidate"],
                profile["classification"] == "REAL_TRANSFER_CANDIDATE",
            )


if __name__ == "__main__":
    unittest.main()
