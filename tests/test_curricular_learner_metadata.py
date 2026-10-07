from __future__ import annotations

import copy
import unittest

from Shared.tools import learner_metadata


def question() -> dict:
    return {
        "id": "Q-TEST-NCERT-01",
        "extensions": {
            "grade9v3:provenance_class": "CURRICULAR_VERIFIED",
            "grade9v3:source_custody": {
                "authority_class": "CURRICULAR_STANDARD",
                "source_status": "NCERT_AUTHENTIC",
                "wording_custody": "VERBATIM",
            },
            "grade9v3:analysis": {
                "exam_source_badge": "NCERT Exemplar",
                "learner_question_type": "single_correct_mcq",
                "difficulty": {
                    "band": "D1",
                    "score": 1,
                    "basis": "Single set-inclusion recognition.",
                    "components": {
                        "algebra_computational_load": 0,
                        "concept_model_selection": 1,
                        "reasoning_chain_length": 0,
                        "representation_translation": 0,
                        "trap_exception_sensitivity": 0,
                    },
                },
            },
        },
    }


class TestCurricularLearnerMetadata(unittest.TestCase):
    def test_verified_curricular_custody_projects_truthful_provenance(self):
        row = learner_metadata._bank_question_metadata(question(), learner_metadata.load_vocabulary())
        self.assertEqual(row["source"], "NCERT Exemplar")
        self.assertEqual(row["provenance"], "CURRICULAR_VERIFIED")
        self.assertEqual(row["provenance_label"], "Verified curricular source")

    def test_curricular_provenance_cannot_self_assert_without_verified_custody(self):
        row = question()
        row["extensions"]["grade9v3:source_custody"]["source_status"] = "CAPTURED_UNVERIFIED"
        with self.assertRaisesRegex(learner_metadata.LearnerMetadataError, "METADATA_PROVENANCE_SOURCE_CONTRADICTION"):
            learner_metadata._bank_question_metadata(row, learner_metadata.load_vocabulary())

    def test_verified_curricular_custody_cannot_be_labelled_source_unverified_or_original(self):
        for false_provenance in ("SOURCE_UNVERIFIED", "ORIGINAL", "PYQ_VERIFIED"):
            row = question()
            row["extensions"]["grade9v3:provenance_class"] = false_provenance
            with self.subTest(false_provenance=false_provenance):
                with self.assertRaisesRegex(learner_metadata.LearnerMetadataError, "METADATA_PROVENANCE_SOURCE_CONTRADICTION"):
                    learner_metadata._bank_question_metadata(row, learner_metadata.load_vocabulary())

    def test_existing_pyq_rule_is_unchanged(self):
        row = question()
        row["extensions"]["grade9v3:provenance_class"] = "PYQ_VERIFIED"
        row["extensions"]["grade9v3:source_custody"] = {
            "authority_class": "OFFICIAL_EXAM_ORGANIZER_ARCHIVE",
            "source_status": "PYQ_VERIFIED_PARENT",
        }
        projected = learner_metadata._bank_question_metadata(row, learner_metadata.load_vocabulary())
        self.assertEqual(projected["provenance"], "PYQ_VERIFIED")


if __name__ == "__main__":
    unittest.main()
