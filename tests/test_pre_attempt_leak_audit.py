from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

from Shared.tools import pre_attempt_leak_audit as audit

REPO = Path(__file__).resolve().parents[1]
BANK = REPO / "Mathematics" / "question-bank" / "surface-areas-and-volumes.owner-bank.v1.json"
PACKAGE = REPO / "Mathematics" / "library" / "surface-areas-and-volumes.v1.json"


class PreAttemptLeakAuditTests(unittest.TestCase):
    def records(self):
        return (
            json.loads(BANK.read_text(encoding="utf-8")),
            json.loads(PACKAGE.read_text(encoding="utf-8")),
        )

    def test_surface_areas_volumes_has_no_transitive_pre_attempt_answer_leak(self):
        bank, package = self.records()
        report = audit.audit(bank, package, REPO)
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(len(report["items"]), 10)
        self.assertTrue(all(item["verdict"] == "PASS" for item in report["items"]))

    def test_linked_core1a_representation_with_final_answer_is_caught(self):
        bank, package = self.records()
        changed = copy.deepcopy(package)
        rep = next(row for row in changed["representations"] if row["id"] == "REP-MAT-SAV-COMPOSITE-SOLIDS")
        rep["purpose"] += " Final answer 214.5 cm²."
        report = audit.audit(bank, changed, REPO)
        q6 = next(row for row in report["items"] if row["question_ref"] == "Q6")
        self.assertEqual(q6["verdict"], "FAIL")
        self.assertTrue(any(f["code"] == "PROTECTED_RESULT_REACHABLE" for f in q6["findings"]))

    def test_missing_linked_asset_is_a_failure(self):
        bank, package = self.records()
        changed = copy.deepcopy(package)
        rep = next(row for row in changed["representations"] if row["id"] == "REP-MAT-SAV-COMPOSITE-SOLIDS")
        rep["rendered_asset_refs"] = ["Mathematics/assets/representations/DOES-NOT-EXIST.svg"]
        report = audit.audit(bank, changed, REPO)
        q6 = next(row for row in report["items"] if row["question_ref"] == "Q6")
        self.assertTrue(any(f["code"] == "PREATTEMPT_RESOURCE_MISSING" for f in q6["findings"]))


    def test_answer_leaking_condition_is_caught(self):
        bank, package = self.records()
        changed = copy.deepcopy(bank)
        q5 = next(row for row in changed["questions"] if row["id"] == "Q5")
        q5["conditions"].append("The inner surface area is 220.5π cm².")
        report = audit.audit(changed, package, REPO)
        item = next(row for row in report["items"] if row["question_ref"] == "Q5")
        self.assertEqual(item["verdict"], "FAIL")
        self.assertTrue(any(
            finding["resource_kind"] == "CORE2_CONDITION"
            and finding["code"] == "PROTECTED_RESULT_REACHABLE"
            for finding in item["findings"]
        ))


if __name__ == "__main__":
    unittest.main()
