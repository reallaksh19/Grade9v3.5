from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

from Shared.tools.competitive_exam_bank import (
    ROOT,
    BANK_SCHEMA,
    PUBLICATION_SCHEMA,
    RUN_SCHEMA,
    check,
    _validate_bank,
)


class CompetitiveExamBankContractTest(unittest.TestCase):
    def test_all_activity_schemas_are_valid_draft_2020_12(self):
        for path in (
            BANK_SCHEMA,
            ROOT / "Shared/library/exam-source-verification.schema.json",
            PUBLICATION_SCHEMA,
            RUN_SCHEMA,
        ):
            Draft202012Validator.check_schema(json.loads(path.read_text(encoding="utf-8")))

    def test_current_pass1_bank_closes_the_activity_contract(self):
        result = check()
        self.assertTrue(result["passed"], msg=json.dumps(result["findings"], indent=2))
        self.assertEqual(result["questions_checked"], 77)
        self.assertEqual(result["banks_checked"], 2)

    def test_source_unverified_cannot_be_promoted_to_canonical_bank(self):
        source = ROOT / "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
        bank = json.loads(source.read_text(encoding="utf-8"))
        bank = copy.deepcopy(bank)
        bank["questions"][0]["extensions"]["grade9v3:provenance_class"] = "SOURCE_UNVERIFIED"

        ledger = json.loads(
            (ROOT / "docs/question-bank/pass1/source-acquisition-ledger.json").read_text(encoding="utf-8")
        )
        concepts = (ROOT / "docs/question-bank/pass1/concept-bucket-inventory.md").read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.json"
            path.write_text(json.dumps(bank), encoding="utf-8")
            findings, _ = _validate_bank(path, ledger, concepts)

        self.assertIn("EXAM_BANK_UNVERIFIED_PROMOTED", {f["point"] for f in findings})


if __name__ == "__main__":
    unittest.main()
