from __future__ import annotations

import json
import unittest

from Shared.tools import build_question_bank_platform
from Shared.tools import question_bank_platform as qbp

ROOT = build_question_bank_platform.REPO


class QuestionBankPlatformRuntimeTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.platform = build_question_bank_platform.build(ROOT)

    def test_detail_shards_cover_current_denominator_without_eager_global_payload(self):
        shards = self.platform["detail_shards"]
        self.assertEqual(len(shards), 2)
        self.assertEqual(sum(row["question_count"] for row in shards), 81)
        self.assertEqual({row["subject_ref"] for row in shards}, {"SUBJECT-CHEMISTRY", "SUBJECT-PHYSICS"})
        workers = {row["worker_id"] for row in self.platform["receipt"]["workers"]}
        self.assertIn("details", workers)

    def test_lineage_witness_resolves_canonical_bank_path(self):
        explained = qbp.explain(self.platform, "PYQ-CHEM-IITJEE-2008-P1-Q66")
        self.assertIsNotNone(explained)
        lineage = explained["lineage"]
        self.assertEqual(lineage["adapter"], "competitive_exam_bank_v2")
        self.assertEqual(
            lineage["source_path"],
            "Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json",
        )
        self.assertTrue(lineage["search_indexed"])

    def test_manifest_declares_bootstrap_and_on_demand_detail_shards(self):
        payloads = build_question_bank_platform.artifact_payloads(self.platform)
        raw = payloads[build_question_bank_platform.OUTPUTS["manifest"]].decode("utf-8")
        prefix = "window.GRADE9_QUESTION_BANK_MANIFEST="
        self.assertTrue(raw.startswith(prefix))
        manifest = json.loads(raw[len(prefix):].rstrip().rstrip(";"))
        self.assertEqual(manifest["build_id"], self.platform["build_id"])
        self.assertEqual(len(manifest["detail_shards"]), 2)
        self.assertIn("STUDY_DETAIL_READY_ON_DEMAND", manifest["readiness"])
        self.assertTrue(all(row["path"].startswith("data/question-bank-details/") for row in manifest["detail_shards"]))


if __name__ == "__main__":
    unittest.main()
