from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import build_learner_search_index, build_question_bank_web, core2_v2, deploy_test, learner_metadata
from TEST.tools import derived_question_bank


REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "TEST/question-bank/ncert-number-systems-q1.v1.json"
INTAKE = REPO / "TEST/question-bank/intake/ncert-exemplar-g9-number-systems-pilot.v1.json"


class TestDerivedQuestionBank(unittest.TestCase):
    def setUp(self):
        self.bank = json.loads(BANK.read_text(encoding="utf-8"))
        self.question = self.bank["questions"][0]
        self.intake = json.loads(INTAKE.read_text(encoding="utf-8"))
        self.source = next(row for row in self.intake["questions"] if row["id"] == self.question["origin_ref"])

    def test_contract_and_source_lineage_are_exact(self):
        self.assertEqual(derived_question_bank.findings(self.bank), [])
        for field in ("original_identifier", "stem", "stem_sha256", "options"):
            self.assertEqual(self.question[field], self.source[field])
        custody = self.question["extensions"]["grade9v3:source_custody"]
        self.assertEqual(custody["source_locator"], self.source["source_locator"])
        self.assertEqual(custody["verification_evidence_ref"], self.source["verification_evidence_ref"])
        self.assertEqual(self.question["answer"]["source_key"]["value"], self.source["official_answer"]["answer_key"])

    def test_authored_overlay_is_distinct_from_source_authority(self):
        ext = self.question["extensions"]
        self.assertEqual(ext["grade9v3:provenance_class"], "CURRICULAR_VERIFIED")
        self.assertEqual(ext["grade9v3:authored_overlay"]["authority"], "AGENT_AUTHORED_SANDBOX")
        self.assertEqual(learner_metadata.bank_question_problems(self.question), [])
        source_rows, authored_rows = core2_v2.split_pre_solution_support(self.question)
        self.assertEqual(source_rows, [])
        self.assertEqual(len(authored_rows), 3)
        self.assertEqual(len(core2_v2.project_solution(self.question["answer"])), 3)

    def test_source_or_custody_drift_is_refused(self):
        for mutate in (
            lambda q: q.__setitem__("stem", q["stem"] + " changed"),
            lambda q: q["extensions"]["grade9v3:source_custody"].__setitem__("source_status", "CAPTURED_UNVERIFIED"),
            lambda q: q["answer"]["source_key"].__setitem__("value", "(A)"),
        ):
            changed = copy.deepcopy(self.bank)
            mutate(changed["questions"][0])
            with self.subTest(changed=changed["questions"][0]["id"]):
                self.assertTrue(derived_question_bank.findings(changed))

    def test_deploy_hook_rejects_invalid_claimed_derivative(self):
        manifest = {"bank_refs": ["TEST/question-bank/ncert-number-systems-q1.v1.json"]}
        deploy_test._validate_product_banks(manifest)
        with mock.patch.object(derived_question_bank, "findings", return_value=["forced drift"]):
            with self.assertRaisesRegex(deploy_test.DeployError, "TEST_DERIVED_BANK_INVALID"):
                deploy_test._validate_product_banks(manifest)

    def test_derivative_remains_outside_canonical_question_bank_and_global_search(self):
        qid = self.question["id"]
        projection = build_question_bank_web.build(REPO)
        self.assertNotIn(qid, {row["id"] for row in projection["questions"]})
        documents, _manifest = build_learner_search_index.build_search_documents(REPO)
        self.assertNotIn(qid, {row["id"] for row in documents})


if __name__ == "__main__":
    unittest.main()
