"""The Question Bank build graph gives one answer however it is scheduled (#359, STEP-QB-07)."""
from __future__ import annotations

import copy
import json
import os
import random
import subprocess
import sys
import unittest
from pathlib import Path

from Shared.tools import build_question_bank_web
from Shared.tools import question_bank_platform as qbp
from Shared.tools import question_bank_scale

ROOT = Path(__file__).resolve().parents[1]

CLEAN_RERUN = """
import json, sys
sys.path.insert(0, {root!r})
from Shared.tools import question_bank_platform as qbp, question_bank_scale
rows = question_bank_scale.synthetic_questions(120)
rows.append(dict(rows[3], id="fixture:question:dup-format", stem="  " + rows[3]["stem"].upper() + "  "))
platform = qbp.assemble_platform({{"questions": rows}})
print(json.dumps({{"build_id": platform["build_id"], "digest": qbp.digest(platform)}}))
"""


def fixture() -> tuple[dict, list[dict]]:
    """Synthetic questions with a formatting duplicate and a near duplicate, so dedup has evidence."""
    rows = question_bank_scale.synthetic_questions(150)
    rows.append(dict(rows[3], id="fixture:question:dup-format", stem="  " + rows[3]["stem"].upper() + "  "))
    rows.append(dict(rows[9], id="fixture:question:near", stem=rows[9]["stem"] + " Show working."))
    resources = [{
        "id": "FIXTURE-CLINIC-1",
        "kind": "study_clinic",
        "title": "Synthetic clinic",
        "subject": rows[0]["subject"],
        "topic": rows[0]["topic"],
        "topic_ref": rows[0]["topic_ref"],
        "path": "synthetic/clinic.html",
        "keywords": ["invariant"],
    }]
    return {"questions": rows}, resources


def build(browser: dict, resources: list[dict], **schedule) -> dict:
    return qbp.assemble_platform(copy.deepcopy(browser), copy.deepcopy(resources), **schedule)


def shuffled(seed: int):
    def order(ready: list[str]) -> list[str]:
        picked = list(ready)
        random.Random(seed).shuffle(picked)
        return picked
    return order


class BuildScheduleIndependence(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser, cls.resources = fixture()
        cls.serial = build(cls.browser, cls.resources)

    def test_the_fixture_gives_dedup_and_lineage_something_to_report(self):
        self.assertGreaterEqual(self.serial["dedup"]["evidence_count"], 1)
        self.assertEqual(len(self.serial["lineage"]["questions"]), 152)

    def test_reversed_and_shuffled_orders_of_independent_workers_change_nothing(self):
        reverse = build(self.browser, self.resources, order=lambda ready: list(reversed(ready)))
        self.assertEqual(reverse, self.serial)
        for seed in range(12):
            with self.subTest(seed=seed):
                self.assertEqual(build(self.browser, self.resources, order=shuffled(seed)), self.serial)

    def test_running_independent_workers_in_parallel_changes_nothing(self):
        for _ in range(3):
            self.assertEqual(build(self.browser, self.resources, parallel=True), self.serial)
        self.assertEqual(
            build(self.browser, self.resources, parallel=True, order=shuffled(5)), self.serial)

    def test_a_clean_process_reproduces_the_build_under_any_hash_seed(self):
        digests = set()
        for hash_seed in ("0", "1", "2", "4242"):
            result = subprocess.run(
                [sys.executable, "-c", CLEAN_RERUN.format(root=str(ROOT))],
                capture_output=True, text=True, check=False,
                env={**os.environ, "PYTHONHASHSEED": hash_seed},
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            digests.add(json.loads(result.stdout)["digest"])
        self.assertEqual(len(digests), 1, "the build depends on set or dict iteration order")

    def test_no_worker_mutates_what_it_reads(self):
        browser, resources = copy.deepcopy(self.browser), copy.deepcopy(self.resources)
        before = (qbp.digest(browser), qbp.digest(resources))
        qbp.assemble_platform(browser, resources, parallel=True)
        self.assertEqual((qbp.digest(browser), qbp.digest(resources)), before)

    def test_repeating_a_build_in_one_process_does_not_drift(self):
        first = build(self.browser, self.resources)
        build(self.browser, self.resources, order=shuffled(3))
        self.assertEqual(build(self.browser, self.resources), first)


class IsolatedNodeRerun(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.browser, cls.resources = fixture()
        cls.platform = build(cls.browser, cls.resources)
        questions = [qbp.enrich_question_refs(q) for q in cls.browser["questions"]]
        scoped = [qbp._resource_scope(r) for r in cls.resources]
        cls.nodes = {n.worker_id: n for n in qbp.platform_nodes(questions, scoped, cls.platform["build_id"])}

    def receipt(self, worker_id: str) -> dict:
        return next(row for row in self.platform["receipt"]["workers"] if row["worker_id"] == worker_id)

    def test_each_independent_node_alone_reproduces_its_receipt(self):
        for worker_id in ("catalog", "search", "dedup"):
            with self.subTest(worker=worker_id):
                alone = qbp.run_nodes([self.nodes[worker_id]])[worker_id]
                self.assertEqual(alone.receipt, self.receipt(worker_id))

    def test_a_dependent_node_reruns_from_only_the_node_it_needs(self):
        results = qbp.run_nodes([self.nodes["search"], self.nodes["lineage"]])
        self.assertEqual(results["lineage"].output, self.platform["lineage"])
        self.assertEqual(results["lineage"].receipt["output_digest"], self.platform["receipt"]["outputs"]["lineage"])

    def test_no_worker_mutates_the_records_the_workers_share(self):
        questions = [qbp.enrich_question_refs(q) for q in self.browser["questions"]]
        scoped = [qbp._resource_scope(r) for r in self.resources]
        before = qbp.digest([questions, scoped])
        qbp.run_nodes(qbp.platform_nodes(questions, scoped, self.platform["build_id"]), parallel=True)
        self.assertEqual(qbp.digest([questions, scoped]), before)

    def test_a_node_cannot_run_without_what_it_needs(self):
        with self.assertRaisesRegex(qbp.ProjectionError, "unknown worker"):
            qbp.run_nodes([self.nodes["lineage"]])


class GraphContract(unittest.TestCase):
    @staticmethod
    def node(worker_id, needs=(), value=None):
        return qbp.Node(worker_id, tuple(needs), lambda done: value, lambda v: [worker_id, v])

    def test_a_cycle_is_named_instead_of_looping(self):
        with self.assertRaisesRegex(qbp.ProjectionError, "cycle"):
            qbp.run_nodes([self.node("a", ["b"]), self.node("b", ["a"])])

    def test_duplicate_worker_ids_are_refused(self):
        with self.assertRaisesRegex(qbp.ProjectionError, "duplicate worker id"):
            qbp.run_nodes([self.node("a"), self.node("a")])

    def test_an_order_that_drops_or_invents_a_worker_is_refused(self):
        with self.assertRaisesRegex(qbp.ProjectionError, "exactly the ready workers"):
            qbp.run_nodes([self.node("a"), self.node("b")], order=lambda ready: ready[:1])

    def test_dependents_wait_for_their_needs_under_every_order(self):
        seen: list[str] = []
        nodes = [
            qbp.Node("a", (), lambda done: None, lambda v: seen.append("a") or "a"),
            qbp.Node("b", (), lambda done: None, lambda v: seen.append("b") or "b"),
            qbp.Node("c", ("a", "b"), lambda done: (done["a"].output, done["b"].output),
                     lambda v: seen.append("c") or v),
        ]
        for order in (lambda r: list(r), lambda r: list(reversed(r))):
            seen.clear()
            results = qbp.run_nodes(nodes, order=order)
            self.assertEqual(seen[-1], "c")
            self.assertEqual(results["c"].output, ("a", "b"))


class LiveCorpus(unittest.TestCase):
    def test_the_committed_corpus_builds_identically_however_it_is_scheduled(self):
        browser = build_question_bank_web.build(ROOT)
        resources, basis = qbp.load_resources(ROOT)
        serial = qbp.assemble_platform(browser, resources, basis)
        for schedule in ({"order": shuffled(1)}, {"order": shuffled(2), "parallel": True}, {"parallel": True}):
            with self.subTest(schedule=sorted(schedule)):
                self.assertEqual(qbp.assemble_platform(browser, resources, basis, **schedule), serial)
        self.assertEqual(serial["receipt"]["counts"]["questions"], 305)


if __name__ == "__main__":
    unittest.main()
