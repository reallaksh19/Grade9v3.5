from __future__ import annotations

import json
import unittest
from pathlib import Path

from Shared.tools import build_learner_search_index, build_question_bank_web, core2_v2, learner_metadata
from TEST.tools import derived_question_bank


REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "TEST/question-bank/ncert-number-systems-q1.v1.json"
INTAKE = REPO / "TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json"


class TestVerifiedQ1Derivative(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.bank = json.loads(BANK.read_text(encoding="utf-8"))
        cls.question = cls.bank["questions"][0]
        intake = json.loads(INTAKE.read_text(encoding="utf-8"))
        cls.source = next(row for row in intake["questions"] if row["id"] == cls.question["origin_ref"])

    def test_a1_contract_and_source_owned_fields_are_exact(self):
        self.assertEqual(derived_question_bank.findings(self.bank), [])
        for field in ("original_identifier", "stem", "stem_sha256", "options"):
            self.assertEqual(self.question[field], self.source[field])
        custody = self.question["extensions"]["grade9v3:source_custody"]
        self.assertEqual(custody["source_locator"], self.source["source_locator"])
        self.assertEqual(custody["verification_evidence_ref"], self.source["verification_evidence_ref"])
        self.assertEqual(self.question["answer"]["source_key"]["value"], self.source["official_answer"]["answer_key"])

    def test_authored_support_and_solution_do_not_masquerade_as_source(self):
        ext = self.question["extensions"]
        self.assertEqual(ext["grade9v3:authored_overlay"]["authority"], "AGENT_AUTHORED_SANDBOX")
        self.assertEqual(self.question["hints"], [])
        source_rows, authored_rows = core2_v2.split_pre_solution_support(self.question)
        self.assertEqual(source_rows, [])
        self.assertEqual(len(authored_rows), 3)
        self.assertEqual(len(core2_v2.project_solution(self.question["answer"])), 3)

    def test_learner_metadata_is_verified_curricular(self):
        self.assertEqual(learner_metadata.bank_question_problems(self.question), [])
        metadata = learner_metadata.bank_question_metadata(self.question)
        self.assertEqual(metadata["provenance"], "CURRICULAR_VERIFIED")
        self.assertEqual(metadata["provenance_label"], "Verified curricular source")

    def test_derivative_is_absent_from_canonical_qb_and_global_search(self):
        qid = self.question["id"]
        qb = build_question_bank_web.build(REPO)
        self.assertNotIn(qid, {row["id"] for row in qb["questions"]})
        documents, _manifest = build_learner_search_index.build_search_documents(REPO)
        self.assertNotIn(qid, {row["id"] for row in documents})


if __name__ == "__main__":
    unittest.main()
