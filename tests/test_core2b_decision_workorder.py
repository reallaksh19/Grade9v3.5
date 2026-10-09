"""I5 single-pair work-order integrity tests. Not independent academic review."""
from __future__ import annotations

import copy
import hashlib
import json
import unittest
from pathlib import Path

from Physics.tools import core2b_decision_workorder as audit

REPO = Path(__file__).resolve().parents[1]
SOURCE = REPO / audit.SOURCE


class ProtectedDecisionReviewPacketTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.fixture = json.loads(cls.source_bytes)

    def packet(self, mutate=None):
        data = copy.deepcopy(self.fixture)
        if mutate:
            mutate(data)
        return audit.build_packet(json.dumps(data).encode("utf-8"))

    @staticmethod
    def question(data, qid):
        return next(q for q in data["questions"] if q["id"] == qid)

    def test_exact_current_source_stays_internal_unassigned_not_academic_acceptance(self):
        packet = audit.build_packet(self.source_bytes)
        self.assertEqual(packet["source_sha256"],
                         "sha256:" + hashlib.sha256(self.source_bytes).hexdigest())
        self.assertEqual(packet["parent"]["id"], audit.PARENT)
        self.assertEqual(packet["child"]["id"], audit.CHILD)
        self.assertEqual(packet["child"]["protected_decide"]["kind"], "DECIDE")
        self.assertEqual(packet["child"]["repair_ref"], "K2D3-1")
        self.assertEqual(packet["packet_status"], "PREPARED_UNASSIGNED")
        self.assertEqual(packet["structural_holds"], [])
        self.assertEqual(packet["independent_academic_decision"],
                         "PENDING_INDEPENDENT_ADJUDICATION")
        self.assertIsNone(packet["independent_reviewer"])
        self.assertIsNone(packet["signed_evidence_ref"])
        self.assertFalse(packet["release_eligible"])
        self.assertEqual(packet["learner_observation"], "NOT_RUN")
        self.assertIn("PROTECTED_ANSWER", packet["audience"])
        self.assertEqual(len(packet["review_questions"]), 7)

    def test_digest_rebinds_to_changed_source_not_to_old_verdict(self):
        original = audit.build_packet(self.source_bytes)
        same = audit.build_packet(self.source_bytes)
        self.assertEqual(same["source_sha256"], original["source_sha256"])
        changed = self.packet(lambda data: self.question(data, audit.CHILD).update(
            {"stem": self.question(data, audit.CHILD)["stem"] + " A new phrase."}
        ))
        self.assertNotEqual(changed["source_sha256"], original["source_sha256"])
        self.assertNotEqual(changed["child"]["question_sha256"],
                            original["child"]["question_sha256"])
        self.assertEqual(changed["independent_academic_decision"],
                         "PENDING_INDEPENDENT_ADJUDICATION")
        self.assertFalse(changed["release_eligible"])

    def test_wrong_parent_makes_real_pair_structurally_held(self):
        def mutate(data):
            self.question(data, audit.CHILD)["transfer"]["builds_on"] = ["Q-OTHER"]
        packet = self.packet(mutate)
        self.assertIn("TRANSFER_CONCRETE_PARENT_LINEAGE_MISMATCH",
                      packet["structural_holds"])
        self.assertEqual(packet["packet_status"], "PREPARED_WITH_STRUCTURAL_HOLDS")

    def test_labelled_transfer_without_real_protected_decide_is_held(self):
        def mutate(data):
            child = self.question(data, audit.CHILD)
            step = next(m for m in child["answer"]["reasoning_route"]
                        if m["id"] == child["transfer"]["protected_move_ref"])
            step["kind"] = "CONNECT"
        packet = self.packet(mutate)
        self.assertIn("TRANSFER_PROTECTED_DECIDE_INVALID",
                      packet["structural_holds"])

    def test_wrong_family_or_cosmetic_stem_clone_cannot_be_clean(self):
        broken_family = self.packet(lambda d: self.question(d, audit.CHILD).update(
            {"family_ref": "FAM-UNRELATED"}
        ))
        self.assertIn("PAIR_FAMILY_MISMATCH", broken_family["structural_holds"])
        clone = self.packet(lambda d: self.question(d, audit.CHILD).update(
            {"stem": self.question(d, audit.PARENT)["stem"]}
        ))
        self.assertIn("PARENT_CHILD_STEMS_UNCHANGED", clone["structural_holds"])

    def test_missing_novelty_or_specific_repair_blocks_packet(self):
        absent_novelty = self.packet(lambda d: self.question(d, audit.CHILD)["transfer"].update(
            {"novelty": {}}
        ))
        self.assertIn("TRANSFER_CHANGED_DEMAND_UNSUPPORTED",
                      absent_novelty["structural_holds"])
        wrong_repair = self.packet(lambda d: self.question(d, audit.CHILD).update(
            {"repair_ref": "MISSING-TEACHING-STEP"}
        ))
        self.assertIn("TRANSFER_REPAIR_NOT_SPECIFIC_TEACHING_STEP",
                      wrong_repair["structural_holds"])

    def test_missing_rubric_does_not_earn_review_readiness(self):
        packet = self.packet(lambda d: self.question(d, audit.CHILD)["answer"].update(
            {"rubric": []}
        ))
        self.assertIn("TRANSFER_RUBRIC_MISSING", packet["structural_holds"])
        self.assertIsNone(packet["independent_reviewer"])

    def test_question_ids_cannot_be_duplicated_or_silently_reassigned(self):
        duplicate = copy.deepcopy(self.fixture)
        duplicate["questions"].append(copy.deepcopy(self.question(duplicate, audit.PARENT)))
        with self.assertRaisesRegex(ValueError, "DUPLICATE_QUESTION_ID"):
            audit.build_packet(json.dumps(duplicate).encode("utf-8"))
        missing = copy.deepcopy(self.fixture)
        missing["questions"] = [
            q for q in missing["questions"] if q["id"] != audit.CHILD
        ]
        with self.assertRaisesRegex(ValueError, "REVIEW_PAIR_SOURCE_QUESTION_MISSING"):
            audit.build_packet(json.dumps(missing).encode("utf-8"))


if __name__ == "__main__":
    unittest.main()
