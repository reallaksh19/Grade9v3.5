"""Issue #131: first genuine NCERT Q1-lineage TEST product; no canonical admission."""
from __future__ import annotations

import copy
import importlib.util
import json
import sys
import unittest
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import matrix_conformance, product_manifest, render_core, test_source_custody  # noqa: E402

PACKAGE = REPO / "TEST/library/ncert-u01-q01.v1.json"
MATRIX = REPO / "TEST/matrices/ncert-u01-q01.rungs.json"
MANIFEST = REPO / "TEST/products/ncert-u01-q01.manifest.json"
INTAKE = REPO / "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
SOURCE_ID = "ncert-exemplar-g9-math-u01-q01"
CORE2_VIEW = REPO / "TEST/library/ncert-u01-q01/core2-source-view.v1.json"
CORE2_AUTHOR = REPO / "TEST/library/ncert-u01-q01/core2-authoring.v1.json"
ADAPTER = REPO / "TEST/library/ncert_source_core2_view.py"
ADAPTER_SPEC = importlib.util.spec_from_file_location("test_ncert_q1_adapter", ADAPTER)
assert ADAPTER_SPEC is not None and ADAPTER_SPEC.loader is not None
adapter = importlib.util.module_from_spec(ADAPTER_SPEC)
ADAPTER_SPEC.loader.exec_module(adapter)


class TestNcertQ1ParkedProduct(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.package = json.loads(PACKAGE.read_text(encoding="utf-8"))
        cls.matrix = json.loads(MATRIX.read_text(encoding="utf-8"))
        cls.manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        cls.bank = json.loads(INTAKE.read_text(encoding="utf-8"))
        cls.view = json.loads(CORE2_VIEW.read_text(encoding="utf-8"))
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
        self.assertEqual(self.manifest["bank_refs"], [CORE2_VIEW.relative_to(REPO).as_posix()])
        self.assertEqual(self.view["source_bank_ref"], INTAKE.relative_to(REPO).as_posix())
        self.assertEqual(self.manifest["selection"]["core2"], [SOURCE_ID])
        self.assertEqual(self.manifest["output_roles"], ["CORE2", "CORE1A"])
        self.assertEqual(len(self.bank["questions"]), 210)
        self.assertEqual(len({q["id"] for q in self.bank["questions"]}), 210)
        self.assertEqual(self.manifest["subject"], "TEST")

    def test_manifest_selection_resolves_in_production_selection_contract(self):
        selected = product_manifest.validate_selection(
            self.manifest, [self.package], self.view["questions"])
        self.assertEqual([q["id"] for q in selected["core2"]], [SOURCE_ID])
        self.assertEqual(len(selected["microtopics"]), 1)
        self.assertEqual(selected["core2a"], [])
        self.assertEqual(selected["core2b"], [])

    def test_authoring_view_is_deterministic_and_cannot_grant_source_ready(self):
        self.assertEqual(CORE2_VIEW.read_text(encoding="utf-8"), adapter.generated_bytes(REPO))
        self.assertEqual(adapter.main(["--repo", str(REPO), "--check"]), 0)
        self.assertEqual(len(self.view["questions"]), 1)
        row = self.view["questions"][0]
        self.assertEqual(row["id"], SOURCE_ID)
        self.assertEqual(row["stem"], self.question["stem"])
        self.assertEqual(row["options"], self.question["options"])
        self.assertEqual(row["original_identifier"], self.question["original_identifier"])
        self.assertEqual(row["status"], "CANDIDATE")
        self.assertEqual(row["answer"]["verification_status"], "CHECKED_BY_AUTHOR")
        self.assertEqual(row["answer"]["source_key"]["value"], self.question["official_answer_text"])
        self.assertEqual(row["extensions"]["grade9v3:ncert_source_lineage"]["stem_sha256"],
                         self.question["stem_sha256"])
        consumer_custody = row["extensions"]["grade9v3:source_custody"]
        self.assertEqual(consumer_custody["authority_class"], "CURRICULAR_STANDARD")
        self.assertEqual(consumer_custody["source_status"], "NCERT_AUTHENTIC")
        self.assertEqual(consumer_custody["wording_custody"], "FAITHFUL_NCERT")
        with mock.patch.object(adapter.test_source_custody, "reconcile",
                               return_value={"ready_ids": [], "handoff": []}):
            with self.assertRaisesRegex(ValueError, "not independently custody READY"):
                adapter.build(REPO)

    def test_actual_production_renderer_builds_both_selected_roles(self):
        pages, gaps, digest, advisories, waivers = render_core.build_report(
            MANIFEST, mode="PAGES", held_to="REFERENCE")
        self.assertEqual(set(pages), {"index.html", "core2.html", "core1a.html"})
        self.assertIn(SOURCE_ID, pages["core2.html"])
        self.assertIn(self.question["stem"], pages["core2.html"])
        self.assertIn(self.package["microtopics"][0]["title"], pages["core1a.html"])
        self.assertIn(self.package["microtopics"][0]["id"], pages["core1a.html"])
        self.assertTrue(digest)
        self.assertTrue(all(gap.get("core") in {"CORE1A", "CORE2"} for gap in gaps))
        self.assertIsInstance(advisories, list)
        self.assertIsInstance(waivers, list)
        for page in pages.values():
            self.assertNotIn("accepted=true", page.lower())

    def test_witnessed_ncert_metadata_is_complete_without_academic_admission(self):
        from Shared.tools import learner_metadata

        row = self.view["questions"][0]
        self.assertEqual(
            row["extensions"]["grade9v3:provenance_class"], "NCERT_CUSTODY_WITNESSED"
        )
        self.assertEqual(learner_metadata.bank_question_problems(row), [])
        analysis = row["extensions"]["grade9v3:analysis"]
        self.assertEqual(analysis["learner_question_type"], "single_correct_mcq")
        self.assertEqual(analysis["difficulty"]["band"], "D2")
        self.assertEqual(
            analysis["difficulty"]["score"],
            sum(analysis["difficulty"]["components"].values()),
        )
        self.assertTrue(row["extensions"]["grade9v3:ncert_source_lineage"][
            "academic_status_not_granted_by_view"
        ])
        self.assertEqual(row["status"], "CANDIDATE")

    def test_mutated_intake_or_answer_witness_cannot_reuse_render_view(self):
        manipulated = copy.deepcopy(self.bank)
        manipulated["questions"][0]["stem_sha256"] = "sha256:" + "0" * 64
        with mock.patch.object(adapter.test_intake_registry, "load_intake_banks",
                               return_value=[manipulated]):
            with self.assertRaisesRegex(ValueError, "source stem digest changed"):
                adapter.build(REPO)
        valid = test_source_custody.reconcile(REPO)
        bad = copy.deepcopy(valid)
        q1 = next(row for row in bad["handoff"] if row["intake_question_ref"] == SOURCE_ID)
        q1["official_answer_key_ref"]["answer_key"] = "(A)"
        with mock.patch.object(adapter.test_source_custody, "reconcile", return_value=bad):
            with self.assertRaisesRegex(ValueError, "official answer key not independently evidenced"):
                adapter.build(REPO)

    def test_matrix_uses_same_microtopic_and_has_real_content(self):
        mic = self.package["microtopics"][0]["id"]
        self.assertEqual(self.matrix["bucket_id"], self.package["buckets"][0]["id"])
        self.assertEqual([r["rung"] for r in self.matrix["rungs"]], ["R1", "R2", "R3"])
        self.assertEqual([r["ladder_position"] for r in self.matrix["rungs"]], [20, 60, 100])
        self.assertTrue(all(r["microtopic_ref"] == mic and r["must_contain"]
                            and r["controlled_variation"] for r in self.matrix["rungs"]))
        self.assertIn(SOURCE_ID, self.package["question_families"][0]["item_refs"])
        self.assertEqual(matrix_conformance.board_findings(self.matrix), [])

    def test_publication_and_generated_pages_are_not_being_faked(self):
        self.assertFalse((REPO / "Mathematics/library/ncert-u01-q01.v1.json").exists())
        self.assertNotIn("accepted", self.package)
        self.assertEqual(self.package["extensions"]["grade9v3:test_source_lineage"]["acceptance"],
                         "DRAFT_NOT_ACCEPTED")
        self.assertEqual(self.manifest["coverage"]["sources"][0]["ingested"], 1)


if __name__ == "__main__":
    unittest.main()
