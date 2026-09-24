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
    DEFAULT_RUN,
    check,
    load,
    validate_bank,
    _canonical_ids,
    _local_registry,
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

    def test_current_bank_closes_the_activity_contract(self):
        result = check()
        self.assertTrue(result["passed"], msg=json.dumps(result["findings"], indent=2))
        self.assertEqual(result["questions_checked"], 77)
        self.assertEqual(result["banks_checked"], 2)

    def test_source_unverified_cannot_be_promoted_to_canonical_bank(self):
        run = load(DEFAULT_RUN)
        source = ROOT / run["bank_paths"][0]
        bank = copy.deepcopy(load(source))
        bank["questions"][0]["extensions"]["grade9v3:provenance_class"] = "SOURCE_UNVERIFIED"

        ledger = load(ROOT / run["ledger_path"])
        local_registry = _local_registry(run["local_ref_registry_paths"])
        canonical = _canonical_ids()
        allowed_hosts = set(run["authority_hosts"])
        forbidden_topics = run["scope"]["forbidden_topics"]

        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "bank.json"
            path.write_text(json.dumps(bank), encoding="utf-8")
            findings, _ = validate_bank(
                path,
                ledger,
                local_registry,
                canonical,
                allowed_hosts,
                forbidden_topics,
            )

        self.assertIn("EXAM_BANK_UNVERIFIED_PROMOTED", {f["point"] for f in findings})


if __name__ == "__main__":
    unittest.main()
