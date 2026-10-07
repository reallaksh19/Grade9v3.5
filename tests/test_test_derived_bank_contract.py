from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import deploy_test
from TEST.tools import derived_question_bank


REPO = Path(__file__).resolve().parents[1]
INTAKE = REPO / "TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json"


def valid_bank() -> dict:
    intake = json.loads(INTAKE.read_text(encoding="utf-8"))
    source = next(row for row in intake["questions"] if row["id"] == "ncert-exemplar-g9-math-u01-q01")
    docs = {row["id"]: row for row in intake["documents"]}
    source_doc = docs[source["source_document_ref"]]
    answer = source["official_answer"]
    answer_doc = docs[answer["document_ref"]]
    return {
        "schema": derived_question_bank.SCHEMA,
        "bank_id": "TEST-FIXTURE-DERIVED-Q1",
        "version": "0.1.0",
        "subject": "TEST",
        "authority_model": "SOURCE_LINKED_DERIVATIVE",
        "source_intake_ref": "TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json",
        "questions": [{
            "id": "Q-TEST-FIXTURE-Q1",
            "version": "0.1.0",
            "status": "CANDIDATE",
            "source_refs": [source_doc["id"], answer_doc["id"]],
            "evidence_refs": [source["verification_evidence_ref"], answer["verification_evidence_ref"]],
            "extensions": {
                "grade9v3:provenance_class": "CURRICULAR_VERIFIED",
                "grade9v3:source_custody": {
                    "authority_class": "CURRICULAR_STANDARD",
                    "source_status": "NCERT_AUTHENTIC",
                    "wording_custody": "VERBATIM",
                    "source_document_ref": source_doc["id"],
                    "source_document_title": source_doc["title"],
                    "source_url": source_doc["url"],
                    "source_locator": source["source_locator"],
                    "text_verification_status": source["text_verification_status"],
                    "verification_evidence_ref": source["verification_evidence_ref"],
                    "answer_key_document_ref": answer_doc["id"],
                    "answer_key_url": answer_doc["url"],
                    "answer_key_evidence_ref": answer["verification_evidence_ref"],
                },
                "grade9v3:analysis": {
                    "exam_source_badge": "NCERT Exemplar",
                    "learner_question_type": "single_correct_mcq",
                    "difficulty": {},
                    "expected_time_seconds": 45,
                    "common_wrong_route": "fixture",
                    "stable_crux_move": "fixture",
                    "transfer_profile": {},
                },
                "grade9v3:authored_overlay": {
                    "authority": "AGENT_AUTHORED_SANDBOX",
                    "fields": ["grade9v3:analysis"],
                },
            },
            "origin": "SOURCE",
            "origin_ref": source["id"],
            "original_identifier": source["original_identifier"],
            "stem": source["stem"],
            "stem_sha256": source["stem_sha256"],
            "subparts": [],
            "options": source["options"],
            "conditions": [],
            "figure_refs": [],
            "response": {"type": "single_choice"},
            "answer": {
                "kind": "MODEL_RESPONSE",
                "summary": "fixture",
                "reasoning": ["a"],
                "reasoning_route": [],
                "crux_move_ref": "fixture",
                "check": "fixture",
                "verification_status": "CHECKED_BY_AUTHOR",
                "source_key": {
                    "state": "PRESENT",
                    "value": answer["answer_key"],
                    "document_ref": answer_doc["id"],
                    "verification_evidence_ref": answer["verification_evidence_ref"],
                },
            },
            "primary_capability_ref": "CAP-TEST-FIXTURE",
            "secondary_capability_refs": [],
            "family_ref": "FAM-TEST-FIXTURE",
            "adaptation": None,
            "exposure": [{"core": "CORE2", "role": "SOURCE", "artifact_ref": None}],
            "hints": [],
            "scaffolds": [{"text": "a"}, {"text": "b"}, {"text": "c"}],
        }],
    }


class TestDerivedQuestionBankContract(unittest.TestCase):
    def test_valid_source_linked_fixture_passes(self):
        self.assertEqual(derived_question_bank.findings(valid_bank()), [])

    def test_structural_or_source_drift_fails_closed(self):
        for mutate in (
            lambda b: b.__setitem__("schema", "wrong-schema"),
            lambda b: b["questions"][0].__setitem__("stem", "changed"),
            lambda b: b["questions"][0]["extensions"]["grade9v3:source_custody"].__setitem__("source_status", "CAPTURED_UNVERIFIED"),
            lambda b: b["questions"][0]["answer"]["source_key"].__setitem__("value", "(A)"),
        ):
            bank = copy.deepcopy(valid_bank())
            mutate(bank)
            self.assertTrue(derived_question_bank.findings(bank))

    def test_claimed_derivative_with_invalid_findings_is_refused_before_render(self):
        manifest = {"bank_refs": ["TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json"]}
        with mock.patch.object(derived_question_bank, "is_claimed", return_value=True), \
             mock.patch.object(derived_question_bank, "findings", return_value=["forced drift"]):
            with self.assertRaisesRegex(deploy_test.DeployError, "TEST_DERIVED_BANK_INVALID"):
                deploy_test._validate_product_banks(manifest)


if __name__ == "__main__":
    unittest.main()
