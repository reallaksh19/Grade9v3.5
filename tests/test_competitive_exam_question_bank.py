import json
import unittest
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
PHYS_BANK = ROOT / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
CHEM_BANK = ROOT / "Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json"
LEDGER = ROOT / "docs/question-bank/pass1/source-acquisition-ledger.json"
CONCEPT_INVENTORY = ROOT / "docs/question-bank/pass1/concept-bucket-inventory.md"
PHYS_CANONICAL_LIBRARIES = [
    ROOT / "Physics/library/phy-nlm-first-law.v1.json",
    ROOT / "Physics/library/phy-kin-2d-motion.v1.json",
    ROOT / "Physics/library/relative-motion.v1.json",
]

OFFICIAL_HOSTS = {"jeeadv.ac.in", "www.jeeadv.ac.in", "neet.nta.nic.in", "cdnbbsr.s3waas.gov.in", "nta.ac.in", "www.nta.ac.in", "jeemain.nta.nic.in", "olympiads.hbcse.tifr.res.in"}
# INJSO friction records are canonical Pass-1 custody, not product-local fixtures.
EXPECTED_COUNTS = {
    "Physics": {
        "Newton's Laws of Motion / NLM": 17,
        "Motion in 2D / Motion in a Plane — linear/projectile only": 15,
        "Motion in 1D — relative motion only": 3,
    },
    "Chemistry": {
        "Redox Reactions": 26,
        "Some Basic Concepts of Chemistry / Mole Concept / Stoichiometry": 20,
    },
}


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


class CompetitiveExamQuestionBankV2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.physics = load(PHYS_BANK)
        cls.chemistry = load(CHEM_BANK)
        cls.banks = [cls.physics, cls.chemistry]
        cls.resource_by_id = {
            resource["id"]: resource
            for bank in cls.banks
            for resource in bank.get("resources", [bank["resource"]])
        }
        cls.questions = [
            (cls.resource_by_id[q["origin_ref"]], q)
            for bank in cls.banks
            for q in bank["questions"]
        ]
        cls.ledger = load(LEDGER)
        cls.concept_inventory = CONCEPT_INVENTORY.read_text(encoding="utf-8")
        cls.physics_capability_ids = set()
        cls.physics_family_ids = set()
        for path in PHYS_CANONICAL_LIBRARIES:
            package = load(path)
            cls.physics_capability_ids.update(x["id"] for x in package["capabilities"])
            cls.physics_family_ids.update(x["id"] for x in package["question_families"])

    def test_fixture_native_v2_shape_and_counts(self):
        self.assertEqual(len(self.physics["questions"]), 35)
        self.assertEqual(len(self.chemistry["questions"]), 46)
        self.assertEqual(len(self.questions), 81)
        for bank in self.banks:
            self.assertEqual(bank["version"], "2.5.0")
            self.assertFalse(bank["extensions"]["grade9v3:generated_sets"])
            self.assertEqual(bank["access_status"], "FULL_ITEM_INSPECTED")

    def test_topic_coverage_is_explicit_and_balanced(self):
        for subject, bank in (("Physics", self.physics), ("Chemistry", self.chemistry)):
            counts = {}
            for q in bank["questions"]:
                topic = q["extensions"]["grade9v3:analysis"]["topic"]
                counts[topic] = counts.get(topic, 0) + 1
            self.assertEqual(counts, EXPECTED_COUNTS[subject])
            self.assertEqual(
                bank["extensions"]["grade9v3:topic_counts"],
                EXPECTED_COUNTS[subject],
            )

    def test_every_question_is_an_honest_pyq_adaptation(self):
        for resource, q in self.questions:
            self.assertEqual(q["origin"], "ADAPTED")
            self.assertEqual(q["extensions"]["grade9v3:provenance_class"], "PYQ_ADAPTED")
            self.assertEqual(q["origin_ref"], resource["id"])
            self.assertIn(q["origin_ref"], self.resource_by_id)
            self.assertTrue(set(q["source_refs"]).issubset(self.resource_by_id))
            self.assertEqual(q["adaptation"]["parent_ref"], q["original_identifier"])
            self.assertTrue(q["adaptation"]["changed_fields"])
            self.assertIn("stem", q["adaptation"]["changed_fields"])
            self.assertIn("Faithful non-verbatim restatement", q["adaptation"]["reason"])

    def test_source_custody_uses_official_organizer_and_subject_qualified_identity(self):
        seen = set()
        for resource, q in self.questions:
            custody = q["extensions"]["grade9v3:source_custody"]
            self.assertEqual(custody["authority_class"], "OFFICIAL_EXAM_ORGANIZER_ARCHIVE")
            self.assertEqual(custody["source_status"], "PYQ_VERIFIED_PARENT")
            self.assertEqual(custody["wording_custody"], "FAITHFUL_NON_VERBATIM_RESTATEMENT")
            self.assertGreaterEqual(custody["last_checked"], "2026-09-23")
            self.assertIn(custody["section"], {"Physics", "Chemistry"})
            self.assertIn(f"|{custody['section']}|", q["original_identifier"])
            self.assertEqual(custody["parent_ref"], q["original_identifier"])
            self.assertIn(urlparse(custody["paper_url"]).hostname, OFFICIAL_HOSTS)
            self.assertIn(urlparse(custody["archive_url"]).hostname, OFFICIAL_HOSTS)
            identity = (
                custody["exam"], custody["year"], custody["paper"],
                custody["section"], custody["question_number"],
            )
            self.assertNotIn(identity, seen)
            seen.add(identity)

    def test_jee_main_2026_records_require_official_paper_and_final_key(self):
        expected = {
            "PYQ-PHY-JEEMAIN-2026-04APR-S2-Q27",
            "PYQ-PHY-JEEMAIN-2026-04APR-S2-Q29",
            "PYQ-PHY-JEEMAIN-2026-06APR-S2-Q46",
            "PYQ-CHEM-JEEMAIN-2026-06APR-S2-Q51",
            "PYQ-CHEM-JEEMAIN-2026-04APR-S2-Q62",
        }
        actual = {q["id"] for _, q in self.questions if q["extensions"]["grade9v3:source_custody"]["exam"] == "JEE Main"}
        self.assertEqual(actual, expected)
        for _, q in self.questions:
            custody = q["extensions"]["grade9v3:source_custody"]
            if custody["exam"] != "JEE Main":
                continue
            self.assertEqual(custody["year"], 2026)
            self.assertIn("Session 2", custody["paper"])
            self.assertIn("Shift 2", custody["paper"])
            self.assertEqual(custody["answer_authority"], "OFFICIAL_NTA_FINAL_ANSWER_KEY")
            self.assertIn(urlparse(custody["answer_key_url"]).hostname, OFFICIAL_HOSTS)
            self.assertEqual(custody["last_checked"], "2026-09-23")

    def test_duplicate_ids_and_authoritative_source_ledger_resolution(self):
        seen_ids = set()
        accepted_by_id = {}
        for record in self.ledger["accepted_authoritative_records"]:
            for question_id in record["accepted_question_ids"]:
                self.assertNotIn(question_id, accepted_by_id)
                accepted_by_id[question_id] = record

        for _, q in self.questions:
            self.assertNotIn(q["id"], seen_ids)
            seen_ids.add(q["id"])
            self.assertIn(q["id"], accepted_by_id)
            record = accepted_by_id[q["id"]]
            custody = q["extensions"]["grade9v3:source_custody"]
            self.assertEqual(record["source_url"], custody["paper_url"])
            self.assertEqual(record["exam"], custody["exam"])
            self.assertEqual(record["year"], custody["year"])

        self.assertEqual(set(accepted_by_id), seen_ids)

    def test_concept_and_family_refs_resolve(self):
        for q in self.physics["questions"]:
            self.assertIn(q["primary_capability_ref"], self.physics_capability_ids)
            for capability_ref in q["secondary_capability_refs"]:
                self.assertIn(capability_ref, self.physics_capability_ids)
            self.assertIn(q["family_ref"], self.physics_family_ids)

        for q in self.chemistry["questions"]:
            # Chemistry identifiers are intentionally local proposals in PASS 1.
            self.assertIn("`" + q["primary_capability_ref"] + "`", self.concept_inventory)
            for capability_ref in q["secondary_capability_refs"]:
                self.assertIn("`" + capability_ref + "`", self.concept_inventory)
            self.assertIn("`" + q["family_ref"] + "`", self.concept_inventory)

    def test_native_question_fields_are_learner_usable(self):
        required = {
            "id", "version", "status", "source_refs", "evidence_refs", "extensions",
            "origin", "origin_ref", "original_identifier", "stem", "subparts",
            "options", "conditions", "figure_refs", "answer",
            "primary_capability_ref", "secondary_capability_refs", "family_ref",
            "adaptation", "exposure", "hints", "scaffolds",
        }
        for _, q in self.questions:
            self.assertTrue(required.issubset(q))
            self.assertTrue(q["stem"].strip())
            self.assertTrue(q["answer"]["summary"].strip())
            self.assertTrue(q["answer"]["reasoning"])
            self.assertTrue(q["answer"]["check"].strip())

    def test_source_hints_and_authored_scaffolds_are_not_conflated(self):
        for _, q in self.questions:
            self.assertEqual(
                q["hints"], [],
                msg=f"{q['id']} must not invent source-provided hints",
            )
            self.assertGreaterEqual(len(q["scaffolds"]), 2)
            move_ids = {move["id"] for move in q["answer"]["reasoning_route"]}
            for scaffold in q["scaffolds"]:
                self.assertIn(scaffold["support_kind"], {"REPRESENT", "CONNECT", "EXECUTE"})
                self.assertIn(scaffold["reveals"], {"CONCEPT", "METHOD", "ANSWER"})
                self.assertIn(scaffold["supports_move_ref"], move_ids)

    def test_reasoning_route_crux_and_check_resolve(self):
        for _, q in self.questions:
            answer = q["answer"]
            route = answer["reasoning_route"]
            self.assertGreaterEqual(len(route), 2)
            move_ids = {m["id"] for m in route}
            self.assertIn(answer["crux_move_ref"], move_ids)
            self.assertEqual(answer["verification_status"], "INDEPENDENTLY_CHECKED")
            self.assertTrue(answer["rubric"])
            for row in answer["rubric"]:
                self.assertTrue(row["criterion"].strip())
                self.assertTrue(row["evidence_of"].strip())

    def test_difficulty_is_component_based_not_exam_label_based(self):
        bands = {0:"D1", 1:"D1", 2:"D1", 3:"D2", 4:"D2", 5:"D2",
                 6:"D3", 7:"D3", 8:"D4", 9:"D4", 10:"D4"}
        keys = {
            "concept_model_selection", "representation_translation",
            "reasoning_chain_length", "algebra_computational_load",
            "trap_exception_sensitivity",
        }
        for _, q in self.questions:
            analysis = q["extensions"]["grade9v3:analysis"]
            difficulty = analysis["difficulty"]
            self.assertEqual(set(difficulty["components"]), keys)
            score = sum(difficulty["components"].values())
            self.assertEqual(difficulty["score"], score)
            self.assertEqual(difficulty["band"], bands[score])
            self.assertGreater(analysis["expected_time_seconds"], 0)
            self.assertNotIn(
                q["extensions"]["grade9v3:source_custody"]["exam"],
                difficulty["basis"],
            )

    def test_transfer_is_distinguished_from_same_family_practice(self):
        for _, q in self.questions:
            profile = q["extensions"]["grade9v3:analysis"]["transfer_profile"]
            self.assertIn(profile["classification"], {"REAL_TRANSFER_CANDIDATE", "SAME_FAMILY_VARIATION"})
            if profile["core2b_candidate"]:
                self.assertEqual(profile["classification"], "REAL_TRANSFER_CANDIDATE")
                self.assertIn(
                    profile["dimension"],
                    {"model_choice", "representation_translation", "reasoning_steps", "novelty"},
                )
            else:
                self.assertEqual(profile["classification"], "SAME_FAMILY_VARIATION")

    def test_scope_excludes_circular_motion(self):
        for _, q in self.questions:
            text = " ".join([
                q["extensions"]["grade9v3:analysis"]["topic"],
                q["stem"],
                q["extensions"]["grade9v3:analysis"]["stable_crux_move"],
            ]).lower()
            self.assertNotIn("circular motion", text)
            self.assertNotIn("centripetal", text)

    def test_relative_motion_hold_is_closed_by_official_records(self):
        relative = [
            q for _, q in self.questions
            if q["extensions"]["grade9v3:analysis"]["topic"] == "Motion in 1D — relative motion only"
        ]
        self.assertGreaterEqual(len(relative), 3)
        self.assertTrue(
            {
                "PYQ-PHY-IITJEE-2008-P2-Q32",
                "PYQ-PHY-JEEADV-2014-P1-Q18",
                "PYQ-PHY-JEEMAIN-2026-04APR-S2-Q27",
            }.issubset({q["id"] for q in relative})
        )

    def test_donor_registries_remain_quarantined_and_preserved(self):
        for inventory in self.ledger["donor_inventories"]:
            self.assertTrue((ROOT / inventory["path"]).is_file())
            self.assertEqual(inventory["disposition"], "PRESERVED_AS_DONOR_EVIDENCE_NOT_DELETED")
        for donor in self.ledger["donor_candidates"]:
            self.assertEqual(donor["pass1_provenance_status"], "SOURCE_UNVERIFIED")
            self.assertEqual(donor["promotion_status"], "QUARANTINED_DONOR_ONLY")


if __name__ == "__main__":
    unittest.main()
