"""One visible question can be traced back to its canonical record and forward to its deployment (#359, STEP-QB-10)."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from Shared.tools import build_question_bank_platform as bqp
from Shared.tools import build_question_bank_web
from Shared.tools import question_bank_platform as qbp

ROOT = Path(__file__).resolve().parents[1]
CHEMISTRY = "PYQ-CHEM-IITJEE-2008-P1-Q66"
PHYSICS = "PYQ-PHY-IITJEE-2007-P1-Q03"


def math_question_projection() -> tuple[dict, dict]:
    """A real canonical Mathematics record, opted in in memory only: production content is untouched."""
    package = json.loads((ROOT / "Mathematics/library/linear-equations.v1.json").read_text(encoding="utf-8"))
    question = copy.deepcopy(package["questions"][0])
    question.setdefault("extensions", {})["grade9v3:question_bank"] = {
        "include": True,
        "difficulty": question["difficulty"],
        "question_type": question["learner_question_type"],
        "expected_time_seconds": 120,
    }
    return package, question


def biology_projection() -> tuple[dict, list[dict]]:
    question = {
        "id": "BIO-CELL-Q1", "order": 0, "subject": "Biology", "topic": "Cell Biology",
        "topic_ref": "TOPIC-BIO-CELL", "subtopic_refs": ["SUB-BIO-MITOCHONDRIA"],
        "question_type": "constructed_response", "exam": "Synthetic", "year": 2026, "paper": "A",
        "question_number": "1", "stem": "Which organelle releases usable energy?", "subparts": [], "options": [],
        "conditions": [], "difficulty": {"band": "D1", "score": 2}, "answer": {"summary": "Mitochondria"},
        "lineage": {"adapter": "synthetic_fixture_v1", "package_id": "FIXTURE-BIOLOGY"},
        "source_status": "SYNTHETIC_FIXTURE", "authority_class": "TEST_ONLY",
    }
    resources = [
        {"id": "BIO-CLINIC-CELL", "kind": "study_clinic", "title": "Cell Biology Study Clinic", "subject": "Biology",
         "topic": "Cell Biology", "topic_ref": "TOPIC-BIO-CELL", "path": "biology/cell-biology/core2.html"},
        {"id": "BIO-EXPLORER-CELL", "kind": "interactive", "title": "Mitochondria explorer", "subject": "Biology",
         "topic": "Cell Biology", "topic_ref": "TOPIC-BIO-CELL", "path": "biology/cell-biology/explorer.html"},
    ]
    return {"questions": [question]}, resources


class LiveWitnesses(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.platform = bqp.build(ROOT)

    def assert_complete(self, result):
        self.assertIsNotNone(result)
        self.assertEqual(result["broken_links"], [])
        self.assertEqual(set(result["chain"]), set(bqp.TRACE_LINKS))

    def test_chemistry_witness_traces_from_bank_to_deployment(self):
        result = bqp.trace(self.platform, CHEMISTRY, ROOT)
        self.assert_complete(result)
        chain = result["chain"]
        self.assertEqual(chain["canonical_record"]["source_path"],
                         "Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json")
        self.assertEqual(chain["canonical_record"]["adapter"], "competitive_exam_bank_v2")
        self.assertEqual(chain["taxonomy_membership"]["subject_ref"], "SUBJECT-CHEMISTRY")
        self.assertEqual(chain["source_provenance"]["exam"], "IIT-JEE")
        self.assertEqual(chain["browser_id"]["id"], CHEMISTRY)
        self.assertEqual(chain["build"]["build_id"], self.platform["build_id"])
        self.assertTrue(result["deployment"]["deployed"], result["deployment"])

    def test_physics_witness_traces_from_bank_to_deployment(self):
        result = bqp.trace(self.platform, PHYSICS, ROOT)
        self.assert_complete(result)
        self.assertEqual(result["chain"]["taxonomy_membership"]["subject_ref"], "SUBJECT-PHYSICS")
        self.assertTrue(result["deployment"]["deployed"], result["deployment"])

    def test_every_live_question_has_an_unbroken_chain(self):
        ids = [row["id"] for row in self.platform["lineage"]["questions"]]
        self.assertEqual(len(ids), 81)
        broken = {qid: bqp.trace(self.platform, qid)["broken_links"] for qid in ids}
        self.assertEqual({qid: links for qid, links in broken.items() if links}, {})

    def test_an_unknown_id_has_no_trace(self):
        self.assertIsNone(bqp.trace(self.platform, "NOT-A-QUESTION"))

    def test_the_command_line_explains_with_the_same_trace(self):
        result = subprocess.run(
            [sys.executable, str(ROOT / "Shared/tools/build_question_bank_platform.py"), "--explain", CHEMISTRY],
            capture_output=True, text=True, check=False, cwd=ROOT)
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["trace"]["broken_links"], [])
        self.assertTrue(payload["trace"]["deployment"]["deployed"])


class MathematicsWitness(unittest.TestCase):
    def test_a_real_canonical_mathematics_record_enters_through_the_package_adapter(self):
        package, question = math_question_projection()
        projected = qbp.project_package_question(package, question, order=999)
        browser = build_question_bank_web.build(ROOT)
        live = len(browser["questions"])
        browser = {**browser, "questions": [*browser["questions"], projected]}
        platform = bqp.build_from_projection(browser)

        self.assertEqual(platform["catalog"]["counts"]["questions"], live + 1)
        result = bqp.trace(platform, question["id"])
        self.assertEqual(result["broken_links"], [])
        chain = result["chain"]
        self.assertEqual(chain["canonical_record"]["adapter"], "shared_package_question_v1")
        self.assertEqual(chain["canonical_record"]["package_id"], "LIB-MATH-LINEAR-EQUATIONS")
        self.assertEqual(chain["taxonomy_membership"]["subject_ref"], "SUBJECT-MATHEMATICS")
        self.assertEqual(chain["generated_artifacts"]["detail_shard"]["id"], "details:SUBJECT-MATHEMATICS")
        # It appears in search and lineage without any Mathematics branch in the platform code.
        self.assertTrue(qbp.search(platform["search"], "linear"))

    def test_production_content_is_not_changed_by_the_witness(self):
        package = json.loads((ROOT / "Mathematics/library/linear-equations.v1.json").read_text(encoding="utf-8"))
        opted_in = [q["id"] for q in package["questions"]
                    if ((q.get("extensions") or {}).get("grade9v3:question_bank") or {}).get("include")]
        self.assertEqual(opted_in, [], "the witness must not opt production Mathematics into the public bank")


class BiologyWitness(unittest.TestCase):
    def test_a_new_subject_is_traceable_end_to_end_without_a_central_branch(self):
        browser, resources = biology_projection()
        platform = bqp.build_from_projection(browser, resources)
        result = bqp.trace(platform, "BIO-CELL-Q1")
        self.assertEqual(result["broken_links"], [])
        self.assertEqual(result["chain"]["canonical_record"]["package_id"], "FIXTURE-BIOLOGY")
        self.assertEqual(result["chain"]["generated_artifacts"]["detail_shard"]["id"], "details:SUBJECT-BIOLOGY")
        kinds = sorted(row["kind"] for row in platform["resources"]["resources"])
        self.assertEqual(kinds, ["interactive", "study_clinic"])
        self.assertTrue(qbp.search(platform["search"], "mitochondria"))
        self.assertTrue(qbp.search(platform["search"], "explorer", kind="resource"))


class BrokenChainsAreNamed(unittest.TestCase):
    def test_a_question_missing_from_its_detail_shard_is_a_named_broken_link(self):
        browser, resources = biology_projection()
        platform = bqp.build_from_projection(browser, resources)
        platform["detail_shards"][0]["payload"]["questions"] = []
        result = bqp.trace(platform, "BIO-CELL-Q1")
        self.assertIn("generated_artifacts", result["broken_links"])
        self.assertIn("browser_id", result["broken_links"])

    def test_a_drifted_deployment_copy_is_reported_not_assumed(self):
        browser, resources = biology_projection()
        platform = bqp.build_from_projection(browser, resources)
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            for path, data in bqp.artifact_payloads(platform).items():
                if path.suffix != ".js":
                    continue
                for base in (repo, repo / "docs"):
                    target = base / (path if base == repo else path.relative_to("public"))
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.write_bytes(data)
            clean = bqp.trace(platform, "BIO-CELL-Q1", repo)
            self.assertTrue(clean["deployment"]["deployed"], clean["deployment"])
            mirror = repo / "docs" / "data" / "question-bank-search.js"
            mirror.write_text(mirror.read_text(encoding="utf-8") + "// drift\n", encoding="utf-8")
            drifted = bqp.trace(platform, "BIO-CELL-Q1", repo)
            self.assertFalse(drifted["deployment"]["deployed"])
            search_row = next(r for r in drifted["deployment"]["artifacts"] if r["artifact"].endswith("search.js"))
            self.assertTrue(search_row["public_matches_build"])
            self.assertFalse(search_row["docs_matches_build"])


if __name__ == "__main__":
    unittest.main()
