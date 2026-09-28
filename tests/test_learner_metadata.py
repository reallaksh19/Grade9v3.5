from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.tools import learner_metadata

REPO = Path(__file__).resolve().parents[1]
PACKAGE = REPO / "Physics/library/phy-nlm-first-law.v1.json"
BANK = REPO / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
MANIFEST = REPO / "products/physics/phy-nlm-first-law.manifest.json"


class LearnerMetadataProjection(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.vocab = learner_metadata.load_vocabulary()
        cls.package_questions = {q["id"]: q for q in cls.package["questions"]}
        cls.bank_questions = {q["id"]: q for q in cls.bank["questions"]}

    def test_question_type_vocabulary_covers_every_current_bank_value(self):
        current = {
            (q.get("extensions") or {}).get("grade9v3:analysis", {}).get("learner_question_type")
            for q in self.bank["questions"]
        }
        self.assertTrue(current <= set(self.vocab["question_types"]))

    def test_known_nlm_concept_owner_resolves_from_primary_capability(self):
        row = learner_metadata.resolve_concept(
            [self.package], "CAP-NLM-FRICTION-QUANT", self.vocab
        )
        self.assertEqual(row["concept_ref"], "MIC-PHY-NLM-FRICTION-QUANT")
        self.assertTrue(row["concept"])
        self.assertIn(row["concept_difficulty"], {"EASY", "MEDIUM", "HARD"})
        self.assertTrue(row["concept_difficulty_reason"])

    def test_selected_core2_projects_safe_source_metadata_from_custody(self):
        question = self.bank_questions[self.manifest["selection"]["core2"][0]]
        row = learner_metadata.project("CORE2", question, [self.package], self.vocab)
        by_kind = {item["kind"]: item for item in row["items"]}
        self.assertEqual(
            set(by_kind),
            {"concept", "concept-difficulty", "question-difficulty", "family",
             "question-type", "source", "provenance"},
        )
        self.assertEqual(by_kind["provenance"]["value"], "PYQ_ADAPTED")
        self.assertIn("IIT-JEE", by_kind["source"]["label"])
        self.assertNotIn("stable_crux_move", json.dumps(row))

    def test_duplicate_concept_owner_fails_closed(self):
        package = copy.deepcopy(self.package)
        duplicate = copy.deepcopy(package["microtopics"][0])
        duplicate["id"] += "-DUPLICATE"
        package["microtopics"].append(duplicate)
        with self.assertRaisesRegex(
            learner_metadata.LearnerMetadataError,
            r"METADATA_CONCEPT_OWNER_AMBIGUOUS",
        ):
            learner_metadata.resolve_concept(
                [package], duplicate["primary_capability_ref"], self.vocab
            )

    def test_authored_question_requires_explicit_difficulty_and_type(self):
        question = copy.deepcopy(
            self.package_questions[self.manifest["selection"]["core2a"][0]]
        )
        question.pop("difficulty", None)
        question.pop("learner_question_type", None)
        with self.assertRaisesRegex(
            learner_metadata.LearnerMetadataError,
            r"METADATA_QUESTION_DIFFICULTY_MISSING",
        ):
            learner_metadata.project("CORE2A", question, [self.package], self.vocab)

    def test_unknown_family_fails_closed(self):
        question = copy.deepcopy(
            self.bank_questions[self.manifest["selection"]["core2"][0]]
        )
        question["family_ref"] = "FAM-DOES-NOT-EXIST"
        with self.assertRaisesRegex(
            learner_metadata.LearnerMetadataError,
            r"METADATA_FAMILY_MISSING",
        ):
            learner_metadata.project("CORE2", question, [self.package], self.vocab)

    def test_invalid_authored_question_type_fails_closed(self):
        question = copy.deepcopy(
            self.package_questions[self.manifest["selection"]["core2a"][0]]
        )
        question["difficulty"] = {
            "band": "D2",
            "score": 4,
            "components": {
                "concept_model_selection": 1,
                "representation_translation": 1,
                "reasoning_chain_length": 1,
                "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
            "basis": "Synthetic valid difficulty for the negative type fixture.",
        }
        question["learner_question_type"] = "made_up_type"
        with self.assertRaisesRegex(
            learner_metadata.LearnerMetadataError,
            r"METADATA_QUESTION_TYPE_INVALID",
        ):
            learner_metadata.project("CORE2A", question, [self.package], self.vocab)

    def test_authored_question_cannot_claim_verified_external_provenance(self):
        question = copy.deepcopy(
            self.package_questions[self.manifest["selection"]["core2a"][0]]
        )
        question["difficulty"] = {
            "band": "D2",
            "score": 4,
            "components": {
                "concept_model_selection": 1,
                "representation_translation": 1,
                "reasoning_chain_length": 1,
                "algebra_computational_load": 1,
                "trap_exception_sensitivity": 0,
            },
            "basis": "Synthetic valid difficulty for the provenance negative fixture.",
        }
        question["learner_question_type"] = "constructed_response"
        question.setdefault("extensions", {})["grade9v3:provenance_class"] = "PYQ_VERIFIED"
        with self.assertRaisesRegex(
            learner_metadata.LearnerMetadataError,
            r"METADATA_AUTHORED_EXTERNAL_PROVENANCE",
        ):
            learner_metadata.project("CORE2A", question, [self.package], self.vocab)


class LearnerMetadataAuditTests(unittest.TestCase):
    def test_nlm_read_only_audit_has_complete_coverage(self):
        report = learner_metadata.audit_manifest(
            REPO / "products/physics/phy-nlm-first-law.manifest.json"
        )
        self.assertEqual(
            report["selection"],
            {"microtopics": 11, "core2": 13, "core2a": 22, "core2b": 16},
        )
        self.assertEqual(report["findings"], [])
        for row in report["coverage"].values():
            self.assertEqual(row["resolved"], row["selected"])

    def test_cross_topic_falsifiers_report_truth_without_nlm_assumptions(self):
        expected = {
            "phy-kin-2d-motion": {"microtopics": 3, "core2": 15, "core2a": 5, "core2b": 5},
            "phy-kin-1d-motion": {"microtopics": 7, "core2": 0, "core2a": 12, "core2b": 7},
            "phy-vec-add-sub": {"microtopics": 4, "core2": 0, "core2a": 6, "core2b": 5},
        }
        for name, selection in expected.items():
            with self.subTest(product=name):
                report = learner_metadata.audit_manifest(
                    REPO / f"products/physics/{name}.manifest.json"
                )
                self.assertEqual(report["selection"], selection)
                self.assertEqual(report["coverage"]["source"]["selected"], selection["core2"])
                self.assertEqual(
                    report["coverage"]["transfer-dimension"]["selected"],
                    selection["core2b"],
                )
                self.assertIsInstance(report["findings"], list)

        source = Path(learner_metadata.__file__).read_text(encoding="utf-8")
        self.assertNotIn("NLM", source)
        self.assertNotIn("Physics", source)


if __name__ == "__main__":
    unittest.main()
