"""Issue #131: first genuine NCERT Q1-lineage TEST product; no canonical admission."""
from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import product_manifest, test_source_custody  # noqa: E402

PACKAGE = REPO / "TEST/library/ncert-u01-q01.v1.json"
MATRIX = REPO / "TEST/matrices/ncert-u01-q01.rungs.json"
MANIFEST = REPO / "TEST/products/ncert-u01-q01.manifest.json"
INTAKE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
SOURCE_ID = "ncert-exemplar-g9-math-u01-q01"


class TestNcertQ1ParkedProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.bank = json.loads(INTAKE.read_text(encoding="utf-8"))
        cls.question = next(q for q in cls.bank["questions"] if q["id"] == SOURCE_ID)

    def test_package_conforms_to_production_renderer_schema(self):
        schema = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))
        errors = list(Draft202012Validator(schema).iter_errors(self.package))
        self.assertEqual(errors, [], [e.message for e in errors[:7]])
        self.assertEqual(self.package["subject"], "TEST")
        self.assertEqual(self.package["status"], "CANDIDATE")
        self.assertEqual(len(self.package["microtopics"]), 1)
        self.assertEqual(len(self.package["question_families"]), 1)
        self.assertEqual(self.package["questions"], [])

    def test_manifest_selects_original_custody_ready_id_once(self):
        custody = test_source_custody.reconcile(REPO)
        self.assertIn(SOURCE_ID, custody["ready_ids"])
        self.assertEqual(custody["ready_for_blueprint"], 12)
        self.assertEqual(custody["evidence_pending"], 198)
        source = self.package["extensions"]["grade9v3:test_source_lineage"]
        self.assertEqual(source["source_id"], SOURCE_ID)
        self.assertEqual(source["stem_sha256"], self.question["stem_sha256"])
        self.assertEqual(source["source_url"], self.question["source_url"])
        self.assertEqual(source["original_identifier"], self.question["original_identifier"])
        self.assertEqual(self.manifest["bank_refs"], [INTAKE.relative_to(REPO).as_posix()])
        self.assertEqual(self.manifest["selection"]["core2"], [SOURCE_ID])
        self.assertEqual(self.manifest["output_roles"], ["CORE2", "CORE1A"])
        self.assertEqual(len(self.bank["questions"]), 210)
        self.assertEqual(len({q["id"] for q in self.bank["questions"]}), 210)
        self.assertEqual(self.manifest["subject"], "TEST")

    def test_manifest_selection_resolves_in_production_selection_contract(self):
        selected = product_manifest.validate_selection(
            self.manifest, [self.package], self.bank["questions"])
        self.assertEqual([q["id"] for q in selected["core2"]], [SOURCE_ID])
        self.assertEqual(len(selected["microtopics"]), 1)
        self.assertEqual(selected["core2a"], [])
        self.assertEqual(selected["core2b"], [])

    def test_matrix_uses_same_microtopic_and_has_real_content(self):
        mic = self.package["microtopics"][0]["id"]
        self.assertEqual(self.matrix["bucket_id"], self.package["buckets"][0]["id"])
        self.assertEqual([r["rung"] for r in self.matrix["rungs"]], ["R1", "R2", "R3"])
        self.assertEqual([r["ladder_position"] for r in self.matrix["rungs"]], [20, 60, 100])
        self.assertTrue(all(r["microtopic_ref"] == mic and r["must_contain"]
                            and r["controlled_variation"] for r in self.matrix["rungs"]))
        self.assertIn(SOURCE_ID, self.package["question_families"][0]["item_refs"])

    def test_publication_and_generated_pages_are_not_being_faked(self):
        self.assertFalse((REPO / "Mathematics/library/ncert-u01-q01.v1.json").exists())
        self.assertNotIn("accepted", self.package)
        self.assertEqual(self.package["extensions"]["grade9v3:test_source_lineage"]["acceptance"],
                         "DRAFT_NOT_ACCEPTED")
        self.assertEqual(self.manifest["coverage"]["sources"][0]["ingested"], 1)


if __name__ == "__main__":
    unittest.main()
