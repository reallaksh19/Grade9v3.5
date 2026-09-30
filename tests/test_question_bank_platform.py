from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from Shared.tools import build_question_bank_platform
from Shared.tools import question_bank_platform as qbp

ROOT = Path(__file__).resolve().parents[1]


def question(qid, stem, *, subject="Biology", topic="Cell Biology", topic_ref=None,
             exam="Fixture", year=2026, paper="A", number="1", family=None):
    row = {
        "id": qid,
        "subject": subject,
        "topic": topic,
        "question_type": "constructed_response",
        "exam": exam,
        "year": year,
        "paper": paper,
        "question_number": number,
        "stem": stem,
        "subparts": [],
        "options": [],
        "conditions": [],
        "difficulty": {"band": "D2", "score": 4},
        "primary_capability_ref": "CAP-BIO-CELL",
        "secondary_capability_refs": [],
        "family_ref": family,
        "answer": {"summary": "fixture"},
    }
    if topic_ref:
        row["topic_ref"] = topic_ref
    return row


class QuestionBankPlatformTest(unittest.TestCase):
    def test_catalog_search_resource_and_explain_are_generated_from_records(self):
        questions = [
            question("BIO-Q1", "Which organelle releases usable energy?", topic_ref="TOPIC-BIO-CELL"),
            question("BIO-Q2", "State one function of mitochondria.", topic_ref="TOPIC-BIO-CELL", number="2"),
        ]
        resources = [{
            "id": "BIO-CLINIC-CELL",
            "kind": "study_clinic",
            "title": "Cell Biology Study Clinic",
            "subject": "Biology",
            "topic": "Cell Biology",
            "topic_ref": "TOPIC-BIO-CELL",
            "path": "biology/cell-biology/core2.html",
            "keywords": ["mitochondria", "cell"],
        }]
        platform = qbp.assemble_platform({"questions": questions}, resources)
        self.assertEqual(platform["catalog"]["counts"]["questions"], 2)
        self.assertEqual(platform["catalog"]["counts"]["resources"], 1)
        self.assertEqual(platform["catalog"]["subjects"][0]["label"], "Biology")
        self.assertEqual(platform["catalog"]["topics"][0]["id"], "TOPIC-BIO-CELL")
        hits = qbp.search(platform["search"], "mitochondria")
        self.assertEqual({row["id"] for row in hits}, {"BIO-Q2", "BIO-CLINIC-CELL"})
        explained = qbp.explain(platform, "BIO-Q1")
        self.assertTrue(explained["lineage"]["search_indexed"])
        self.assertEqual(explained["lineage"]["topic_ref"], "TOPIC-BIO-CELL")

    def test_resource_discovery_uses_data_records_not_subject_branches(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            registry = root / "Biology" / "question-bank"
            registry.mkdir(parents=True)
            (registry / "resources.v1.json").write_text(json.dumps({
                "schema_version": qbp.RESOURCE_SCHEMA,
                "resources": [{
                    "id": "RES-BIO-CELL-CLINIC",
                    "kind": "study_clinic",
                    "title": "Cell Clinic",
                    "topic": "Cell Biology",
                    "topic_ref": "TOPIC-BIO-CELL",
                    "path": "biology/cell/core2.html",
                    "keywords": ["cell", "mitochondria"],
                }],
            }), encoding="utf-8")
            suites = root / "docs" / "gcdr-suites"
            suites.mkdir(parents=True)
            (suites / "bio-cell.json").write_text(json.dumps({
                "suite_id": "GCDR-BIO-CELL",
                "title": "Cell Explorer",
                "external_corpus": {"subject": "Biology", "topic": "Cell Biology"},
                "delivery_artifacts": [{"profile": "REPO_BUNDLE", "locator": "public/biology/cell/explorer/index.html"}],
            }), encoding="utf-8")
            resources, basis = qbp.load_resources(root)
            self.assertEqual({r["id"] for r in resources}, {"RES-BIO-CELL-CLINIC", "GCDR-BIO-CELL"})
            self.assertEqual(len(basis), 2)
            self.assertTrue(all(r["subject_ref"] == "SUBJECT-BIOLOGY" for r in resources))

    def test_explicit_stable_topic_identity_survives_label_change(self):
        first = qbp.build_catalog([question("BIO-Q1", "A", topic="Cell Biology", topic_ref="TOPIC-BIO-CELL")])
        renamed = qbp.build_catalog([question("BIO-Q1", "A", topic="Cells & Organelles", topic_ref="TOPIC-BIO-CELL")])
        self.assertEqual(first["topics"][0]["id"], renamed["topics"][0]["id"])
        self.assertNotEqual(first["topics"][0]["label"], renamed["topics"][0]["label"])

    def test_package_adapter_is_shape_driven_and_requires_explicit_opt_in(self):
        package = {
            "package_id": "LIB-BIO-CELL",
            "title": "Cell Biology",
            "subject": "Biology",
            "extensions": {"grade9v3:question_bank": {"include": True, "expected_time_seconds": 60}},
        }
        q = {
            "id": "BIO-PKG-Q1",
            "version": "1.0.0",
            "status": "CANDIDATE",
            "origin": "SOURCE",
            "stem": "Name the organelle associated with aerobic respiration.",
            "subparts": [], "options": [], "conditions": [],
            "primary_capability_ref": "CAP-BIO-CELL",
            "secondary_capability_refs": [],
            "family_ref": "FAM-BIO-CELL",
            "hints": [],
            "answer": {"summary": "Mitochondrion", "reasoning": [], "check": "", "verification_status": "CHECKED"},
            "extensions": {
                "grade9v3:analysis": {"difficulty": {"band": "D1", "score": 2}, "learner_question_type": "constructed_response"},
                "grade9v3:source_custody": {"exam": "Fixture", "year": 2026, "paper": "A", "question_number": "1"},
            },
        }
        projected = qbp.project_package_question(package, q)
        self.assertEqual(projected["subject"], "Biology")
        self.assertEqual(projected["topic_ref"], "LIB-BIO-CELL")
        self.assertEqual(projected["lineage"]["adapter"], "shared_package_question_v1")
        package["extensions"] = {}
        self.assertIsNone(qbp.project_package_question(package, q))

    def test_dedup_layers_produce_compact_evidence_without_deleting(self):
        base = question("Q1", "Find the degree of x^2 + 2x + 1", number="1")
        formatted = question("Q2", "Find  the degree of $x^2 + 2x + 1$.", number="2")
        self.assertEqual(qbp.compare_pair(base, formatted)["classification"], "DUPLICATE")

        collision = dict(base, id="Q3", stem="A materially different question")
        collision["question_number"] = "1"
        self.assertEqual(qbp.compare_pair(base, collision)["classification"], "SOURCE_COLLISION")

        v1 = question("Q4", "Solve 2x + 1 = 5", number="4", family="FAM-LINEAR")
        v2 = question("Q5", "Solve 3x + 1 = 7", number="5", family="FAM-LINEAR")
        self.assertEqual(qbp.compare_pair(v1, v2)["classification"], "VARIANT")

        report = qbp.build_dedup_report([base, formatted, collision, v1, v2])
        self.assertEqual(report["question_count"], 5)
        classifications = {row["classification"] for row in report["groups"]}
        self.assertIn("DUPLICATE", classifications)
        self.assertIn("SOURCE_COLLISION", classifications)
        self.assertIn("VARIANT", classifications)
        self.assertEqual(report["authority"], "EVIDENCE_ONLY_NO_SILENT_DELETION")

    def test_variant_evidence_does_not_expand_quadratically(self):
        rows = [
            question(f"V{i:03d}", f"Solve {i + 2}x + 1 = {i + 4}", number=str(i + 1), family="FAM-SCALE")
            for i in range(100)
        ]
        report = qbp.build_dedup_report(rows)
        variant_groups = [row for row in report["groups"] if row["classification"] == "VARIANT"]
        self.assertEqual(len(variant_groups), 1)
        self.assertEqual(len(variant_groups[0]["member_ids"]), 100)
        self.assertLess(report["evidence_count"], 100)

    def test_exact_dedup_preserves_mathematical_operators(self):
        plus = question("PLUS", "Solve x + 1 = 4", number="10")
        minus = question("MINUS", "Solve x - 1 = 4", number="11")
        result = qbp.compare_pair(plus, minus)
        self.assertNotEqual(result["classification"], "DUPLICATE")
        self.assertNotEqual(qbp.normalized_exact_fingerprint(plus), qbp.normalized_exact_fingerprint(minus))

    def test_duplicate_canonical_id_fails_closed(self):
        with self.assertRaises(qbp.ProjectionError):
            qbp.validate_unique_ids([question("SAME", "A"), question("SAME", "B")])

    def test_build_identity_and_worker_receipts_are_deterministic(self):
        browser = {"questions": [question("BIO-Q1", "A", topic_ref="TOPIC-BIO-CELL")]}
        a = qbp.assemble_platform(browser)
        b = qbp.assemble_platform(browser)
        self.assertEqual(a["build_id"], b["build_id"])
        self.assertEqual(a["receipt"], b["receipt"])
        self.assertEqual([w["worker_id"] for w in a["receipt"]["workers"]], ["catalog", "dedup", "search"])

    def test_direct_script_entrypoints_import_without_repo_pythonpath(self):
        for rel in (
            "Shared/tools/build_question_bank_web.py",
            "Shared/tools/build_question_bank_platform.py",
        ):
            result = subprocess.run(
                [sys.executable, str(ROOT / rel), "--help"],
                cwd=ROOT,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, msg=f"{rel}: {result.stderr}")

    def test_live_projection_builds_shared_contracts_without_changing_denominator(self):
        platform = build_question_bank_platform.build(ROOT)
        self.assertEqual(platform["catalog"]["counts"]["questions"], 77)
        question_docs = [row for row in platform["search"]["documents"] if row["kind"] == "question"]
        self.assertEqual(len(question_docs), 77)
        self.assertIsNotNone(qbp.explain(platform, "PYQ-CHEM-IITJEE-2008-P1-Q66"))
        resource_ids = {row["id"] for row in platform["resources"]["resources"]}
        self.assertIn("RES-PHY-MOTION-2D-MASTER-SUITE", resource_ids)
        self.assertIn("RES-CHEM-REDOX-ADAPTIVE-PROOF", resource_ids)


if __name__ == "__main__":
    unittest.main()
