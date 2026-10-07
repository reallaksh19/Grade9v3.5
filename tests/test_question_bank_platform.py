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

    def _linked_repo(self, root, links, suite_topic="Cell Biology (provider label)"):
        registry = root / "Biology" / "question-bank"
        registry.mkdir(parents=True)
        (registry / "resources.v1.json").write_text(json.dumps({
            "schema_version": qbp.RESOURCE_SCHEMA, "resources": [], "topic_links": links,
        }), encoding="utf-8")
        suites = root / "docs" / "gcdr-suites"
        suites.mkdir(parents=True)
        (suites / "bio-cell.json").write_text(json.dumps({
            "suite_id": "GCDR-BIO-CELL", "title": "Cell Explorer",
            "external_corpus": {"subject": "Biology", "topic": suite_topic},
            "delivery_artifacts": [{"profile": "REPO_BUNDLE", "locator": "public/biology/cell/explorer/index.html"}],
        }), encoding="utf-8")

    def test_recorded_topic_link_puts_a_discovered_suite_in_the_question_topic(self):
        link = {"resource_id": "GCDR-BIO-CELL", "topic_ref": "TOPIC-BIO-CELL", "reason": "same chapter"}
        questions = [question("BIO-Q1", "Which organelle releases usable energy?", topic_ref="TOPIC-BIO-CELL")]
        with tempfile.TemporaryDirectory() as tmp:
            self._linked_repo(Path(tmp), [])
            unlinked_resources, unlinked_basis = qbp.load_resources(Path(tmp))
        unlinked = qbp.assemble_platform({"questions": questions}, unlinked_resources, unlinked_basis)
        self.assertEqual(len(unlinked["catalog"]["topics"]), 2, "without a link the suite makes a topic of its own")
        with tempfile.TemporaryDirectory() as tmp:
            self._linked_repo(Path(tmp), [link])
            resources, basis = qbp.load_resources(Path(tmp))
        platform = qbp.assemble_platform({"questions": questions}, resources, basis)
        topics = platform["catalog"]["topics"]
        self.assertEqual([(t["id"], t["question_count"], t["resource_count"]) for t in topics], [("TOPIC-BIO-CELL", 1, 1)])
        row = platform["resources"]["resources"][0]
        self.assertEqual((row["topic_ref"], row["topic"], row["source_topic"]),
                         ("TOPIC-BIO-CELL", "Cell Biology", "Cell Biology (provider label)"))
        self.assertEqual(row["topic_link"]["reason"], "same chapter")
        self.assertEqual({d["id"] for d in qbp.search(platform["search"], "provider label")}, {"GCDR-BIO-CELL"},
                         "the provider's own words still find the resource")

    def test_a_topic_link_that_does_not_resolve_fails_the_build(self):
        questions = [question("BIO-Q1", "A", topic_ref="TOPIC-BIO-CELL")]
        cases = {
            "names no resource": ({"resource_id": "GCDR-NOPE", "topic_ref": "TOPIC-BIO-CELL", "reason": "r"}, "GCDR-NOPE"),
            "creates a topic": ({"resource_id": "GCDR-BIO-CELL", "topic_ref": "TOPIC-BIO-INVENTED", "reason": "r"}, "may not create a topic"),
            "has no reason": ({"resource_id": "GCDR-BIO-CELL", "topic_ref": "TOPIC-BIO-CELL", "reason": " "}, "needs resource_id, topic_ref and reason"),
        }
        for name, (link, expected) in cases.items():
            with self.subTest(name), tempfile.TemporaryDirectory() as tmp:
                self._linked_repo(Path(tmp), [link])
                with self.assertRaises(qbp.ProjectionError) as caught:
                    resources, basis = qbp.load_resources(Path(tmp))
                    qbp.assemble_platform({"questions": questions}, resources, basis)
                self.assertIn(expected, str(caught.exception))
        twice = {"resource_id": "GCDR-BIO-CELL", "topic_ref": "TOPIC-BIO-CELL", "reason": "r"}
        with tempfile.TemporaryDirectory() as tmp:
            self._linked_repo(Path(tmp), [twice, dict(twice, topic_ref="TOPIC-BIO-OTHER")])
            with self.assertRaisesRegex(qbp.ProjectionError, "more than one topic"):
                qbp.load_resources(Path(tmp))
        with tempfile.TemporaryDirectory() as tmp:
            self._linked_repo(Path(tmp), [twice])
            resources, basis = qbp.load_resources(Path(tmp))
        other_subject = [question("PHY-Q1", "A", subject="Physics", topic="Motion", topic_ref="TOPIC-BIO-CELL")]
        with self.assertRaisesRegex(qbp.ProjectionError, "which belongs to SUBJECT-PHYSICS"):
            qbp.assemble_platform({"questions": other_subject}, resources, basis)

    def test_changing_a_topic_link_changes_the_build_identity(self):
        questions = [question("BIO-Q1", "A", topic_ref="TOPIC-BIO-CELL")]
        ids = []
        for reason in ("first reason", "second reason"):
            with tempfile.TemporaryDirectory() as tmp:
                self._linked_repo(Path(tmp), [{"resource_id": "GCDR-BIO-CELL", "topic_ref": "TOPIC-BIO-CELL", "reason": reason}])
                resources, basis = qbp.load_resources(Path(tmp))
            ids.append(qbp.assemble_platform({"questions": questions}, resources, basis)["build_id"])
        self.assertNotEqual(ids[0], ids[1])

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

    def test_a_near_duplicate_is_reported_and_an_unrelated_pair_is_not(self):
        stem = ("A particle moves along a straight line with constant acceleration starting from rest and after "
                "six seconds its speed is twelve metres per second find the distance covered in that time")
        original = question("ND1", stem, number="1")
        reworded = question("ND2", stem.replace("find the distance", "determine the distance"), number="2")
        unrelated = question("ND3", "Name the organelle that releases usable energy in a plant cell", number="3")
        self.assertEqual(qbp.compare_pair(original, reworded)["classification"], "NEAR_DUPLICATE")
        self.assertEqual(qbp.compare_pair(original, unrelated)["classification"], "DISTINCT")
        report = qbp.build_dedup_report([qbp.enrich_question_refs(q) for q in (original, reworded, unrelated)])
        pairs = [(row["left_id"], row["right_id"]) for row in report["relationships"]]
        self.assertEqual(pairs, [("ND1", "ND2")], "the near duplicate is evidence; the unrelated question is not")
        self.assertEqual(report["question_count"], 3, "nothing is deleted")

    def test_exact_dedup_preserves_mathematical_operators(self):
        plus = question("PLUS", "Solve x + 1 = 4", number="10")
        minus = question("MINUS", "Solve x - 1 = 4", number="11")
        result = qbp.compare_pair(plus, minus)
        self.assertNotEqual(result["classification"], "DUPLICATE")
        self.assertNotEqual(qbp.normalized_exact_fingerprint(plus), qbp.normalized_exact_fingerprint(minus))

    def test_near_duplicate_search_says_when_it_declined_to_look(self):
        # A small topic is searched completely.
        small = [question(f"BIO-S{i}", f"Explain organelle number {i} in a plant cell.", topic_ref="TOPIC-BIO-CELL",
                          number=str(i)) for i in range(6)]
        report = qbp.build_dedup_report([qbp.enrich_question_refs(q) for q in small])
        self.assertTrue(report["near_duplicate_coverage"]["complete"])
        self.assertEqual(report["near_duplicate_coverage"]["shingle_buckets_skipped_as_too_common"], 0)
        self.assertEqual(report["near_duplicate_coverage"]["records_whose_shingles_were_all_skipped"], 0)

        # A record that shares no shingle with anyone has nothing to compare; that is not a skip.
        alone = small + [question("BIO-ALONE", "Quantum tunnelling of electrons through a barrier.",
                                  topic_ref="TOPIC-BIO-CELL", number="99")]
        report = qbp.build_dedup_report([qbp.enrich_question_refs(q) for q in alone])
        self.assertEqual(report["near_duplicate_coverage"]["records_whose_shingles_were_all_skipped"], 0)
        self.assertTrue(report["near_duplicate_coverage"]["complete"])

        # One topic of templated stems is larger than the bucket bound: the search skips the shared
        # shingles, and the report must say so instead of looking like "no near duplicates".
        crowd = qbp.NEAR_MAX_BUCKET + 8
        crowded = [question(f"BIO-C{i}", f"Explain organelle number {i} in a plant cell.",
                            topic_ref="TOPIC-BIO-CELL", number=str(i)) for i in range(crowd)]
        report = qbp.build_dedup_report([qbp.enrich_question_refs(q) for q in crowded])
        coverage = report["near_duplicate_coverage"]
        self.assertFalse(coverage["complete"])
        self.assertGreater(coverage["shingle_buckets_skipped_as_too_common"], 0)
        self.assertEqual(coverage["records_whose_shingles_were_all_skipped"], crowd)
        self.assertEqual(coverage["records"], crowd)

    def test_truncated_candidate_lists_are_counted(self):
        count = qbp.NEAR_MAX_CANDIDATES_PER_RECORD + 4  # within the bucket bound, above the per-record cap
        self.assertLessEqual(count, qbp.NEAR_MAX_BUCKET)
        rows = [question(f"BIO-T{i}", f"Explain organelle number {i} in a plant cell.",
                         topic_ref="TOPIC-BIO-CELL", number=str(i)) for i in range(count)]
        coverage = qbp.build_dedup_report([qbp.enrich_question_refs(q) for q in rows])["near_duplicate_coverage"]
        self.assertFalse(coverage["complete"])
        self.assertEqual(coverage["records_with_truncated_candidates"], count)
        self.assertEqual(coverage["shingle_buckets_skipped_as_too_common"], 0)

    def test_the_build_receipt_carries_whether_the_near_duplicate_search_was_complete(self):
        platform = qbp.assemble_platform({"questions": [question("BIO-Q1", "A short stem about cells", topic_ref="T")]})
        self.assertIs(platform["receipt"]["counts"]["near_duplicate_search_complete"], True)

    def test_summaries_carry_what_a_result_list_needs_and_nothing_of_the_study_detail(self):
        rich = question("BIO-Q1", "Which organelle releases usable energy?", topic_ref="TOPIC-BIO-CELL")
        rich.update({
            "options": ["(A) x", "(B) y"], "conditions": ["c"], "source_hints": ["h"], "scaffolds": [{"text": "s"}],
            "visual_ref": "assets/figure.svg", "answer": {"summary": "Mitochondria", "reasoning": ["r"]},
            "math_spans": [{"target": "stem", "literal": "x", "tex": "x"}, {"target": "option:0", "literal": "y", "tex": "y"}],
        })
        platform = qbp.assemble_platform({"questions": [rich]})
        row = platform["summaries"]["questions"][0]
        for detail in ("options", "conditions", "source_hints", "scaffolds", "visual_ref", "answer"):
            self.assertNotIn(detail, row)
        self.assertEqual((row["id"], row["subject_ref"], row["topic_ref"]), ("BIO-Q1", "SUBJECT-BIOLOGY", "TOPIC-BIO-CELL"))
        self.assertEqual((row["has_visual"], row["option_count"]), (True, 2))
        self.assertEqual([span["target"] for span in row["math_spans"]], ["stem"])
        self.assertEqual(platform["summaries"]["question_count"], 1)

    def test_saved_views_are_membership_in_the_catalog_and_may_not_dangle(self):
        questions = [question("BIO-Q1", "A", topic_ref="T1"), question("BIO-Q2", "B", topic_ref="T1", number="2")]
        view = {"id": "v1", "title": "Two", "description": "d", "match_mode": "EXACT_POLICY_SET",
                "presentation": {"badge": "2", "source_label": "s", "default_mode": "study"},
                "resolved_question_refs": ["BIO-Q2", "BIO-Q1"], "policy": {"anything": True}}
        platform = qbp.assemble_platform({"questions": questions, "views": [view]})
        self.assertEqual(platform["catalog"]["counts"]["views"], 1)
        saved = platform["catalog"]["views"][0]
        self.assertEqual(saved["resolved_question_refs"], ["BIO-Q2", "BIO-Q1"], "the collection's own order is kept")
        self.assertNotIn("policy", saved, "how a view was chosen is not part of what the browser needs")
        with self.assertRaisesRegex(qbp.ProjectionError, "unknown questions"):
            qbp.assemble_platform({"questions": questions, "views": [{**view, "resolved_question_refs": ["GONE"]}]})
        with self.assertRaisesRegex(qbp.ProjectionError, "missing or repeated"):
            qbp.assemble_platform({"questions": questions, "views": [view, view]})

    def test_live_summaries_and_views_agree_with_the_catalog(self):
        platform = build_question_bank_platform.build(ROOT)
        self.assertEqual(platform["summaries"]["question_count"], platform["catalog"]["counts"]["questions"])
        listed = {row["id"] for row in platform["summaries"]["questions"]}
        for view in platform["catalog"]["views"]:
            self.assertLessEqual(set(view["resolved_question_refs"]), listed)

    def test_subtopics_carry_a_canonical_title_or_say_they_have_none(self):
        a = question("BIO-Q1", "A", topic_ref="T1")
        a["subtopic_refs"] = ["CAP-A"]
        b = question("BIO-Q2", "B", topic_ref="T1", number="2")
        b["subtopic_refs"] = ["CAP-A", "CAP-B"]
        titles = {"CAP-A": {"title": "Cells release energy", "source_ref": "MIC-A"}}
        catalog = qbp.assemble_platform({"questions": [a, b]}, subtopic_titles=titles)["catalog"]
        rows = {row["id"]: row for row in catalog["subtopics"]}
        self.assertEqual(rows["CAP-A"]["label"], "Cells release energy")
        self.assertEqual((rows["CAP-A"]["label_source"], rows["CAP-A"]["label_source_ref"]), ("CANONICAL_TITLE", "MIC-A"))
        self.assertEqual((rows["CAP-B"]["label"], rows["CAP-B"]["label_source"]), ("CAP-B", "REF_ONLY"))
        self.assertNotIn("label_source_ref", rows["CAP-B"])
        self.assertEqual(rows["CAP-A"]["question_count"], 2)
        self.assertEqual(catalog["counts"]["subtopics_without_title"], 1)

    def test_subtopic_titles_are_part_of_the_build_identity(self):
        browser = {"questions": [question("BIO-Q1", "A", topic_ref="T1")]}
        plain = qbp.assemble_platform(browser)
        titled = qbp.assemble_platform(browser, subtopic_titles={"CAP-BIO-CELL": {"title": "Cells", "source_ref": "M"}})
        self.assertNotEqual(plain["build_id"], titled["build_id"], "an artifact that changed must not keep its build id")
        self.assertEqual(plain["build_id"], qbp.assemble_platform(browser)["build_id"])

    def test_only_an_unambiguous_owning_microtopic_titles_a_capability(self):
        with tempfile.TemporaryDirectory() as tmp:
            library = Path(tmp) / "Subject" / "library"
            library.mkdir(parents=True)
            (library / "one.json").write_text(json.dumps({"microtopics": [
                {"id": "MIC-1", "title": " Sole owner ", "primary_capability_ref": "CAP-A"},
                {"id": "MIC-2", "title": "First claimant", "primary_capability_ref": "CAP-B"},
                {"id": "MIC-3", "title": "", "primary_capability_ref": "CAP-D"},
            ]}), encoding="utf-8")
            (library / "two.json").write_text(json.dumps({"microtopics": [
                {"id": "MIC-4", "title": "Second claimant", "primary_capability_ref": "CAP-B"},
            ]}), encoding="utf-8")
            (library / "broken.json").write_text("{not json", encoding="utf-8")
            titles = qbp.load_subtopic_titles(Path(tmp))
        self.assertEqual(titles, {"CAP-A": {"title": "Sole owner", "source_ref": "MIC-1"}})

    def test_live_subtopic_labels_come_from_records_and_the_rest_are_marked(self):
        platform = build_question_bank_platform.build(ROOT)
        titles = qbp.load_subtopic_titles(ROOT)
        for row in platform["catalog"]["subtopics"]:
            if row["label_source"] == "CANONICAL_TITLE":
                self.assertEqual(row["label"], titles[row["id"]]["title"])
            else:
                self.assertEqual((row["label"], row["label_source"]), (row["id"], "REF_ONLY"))
                self.assertNotIn(row["id"], titles)
        without = sum(1 for row in platform["catalog"]["subtopics"] if row["label_source"] == "REF_ONLY")
        self.assertEqual(platform["catalog"]["counts"]["subtopics_without_title"], without)

    def test_duplicate_canonical_id_fails_closed(self):
        with self.assertRaises(qbp.ProjectionError):
            qbp.validate_unique_ids([question("SAME", "A"), question("SAME", "B")])

    def test_build_identity_and_worker_receipts_are_deterministic(self):
        browser = {"questions": [question("BIO-Q1", "A", topic_ref="TOPIC-BIO-CELL")]}
        a = qbp.assemble_platform(browser)
        b = qbp.assemble_platform(browser)
        self.assertEqual(a["build_id"], b["build_id"])
        self.assertEqual(a["receipt"], b["receipt"])
        self.assertEqual([w["worker_id"] for w in a["receipt"]["workers"]], ["catalog", "dedup", "search", "summaries"])

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
        self.assertEqual(platform["catalog"]["counts"]["questions"], 349)
        question_docs = [row for row in platform["search"]["documents"] if row["kind"] == "question"]
        self.assertEqual(len(question_docs), 349)
        self.assertIsNotNone(qbp.explain(platform, "PYQ-CHEM-IITJEE-2008-P1-Q66"))
        resource_ids = {row["id"] for row in platform["resources"]["resources"]}
        self.assertIn("RES-PHY-MOTION-2D-MASTER-SUITE", resource_ids)
        self.assertIn("RES-CHEM-REDOX-ADAPTIVE-PROOF", resource_ids)


if __name__ == "__main__":
    unittest.main()
