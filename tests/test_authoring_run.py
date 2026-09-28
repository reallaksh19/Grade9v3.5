"""Authoring-run scope enforcement and receipt falsifiers."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.contracts import digest  # noqa: E402
from Shared.tools import compile_execution_packet, execute_authoring_run  # noqa: E402


class AuthoringRun(unittest.TestCase):
    CORE2B = REPO / "Requests/relative-motion-core2b-candidate.author-request.json"
    TEACHING = REPO / "Requests/relative-motion-teaching.author-request.json"
    PACKAGE = REPO / "Physics/library/relative-motion.v1.json"

    def request(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def parent_question(self):
        package = json.loads(self.PACKAGE.read_text(encoding="utf-8"))
        return copy.deepcopy(next(q for q in package["questions"]
                                  if q["id"] == "Q-AUTHOR-REL-01"))

    def transfer_question(self):
        q = self.parent_question()
        q["id"] = "Q-AUTHOR-REL-TRANSFER-01"
        q["version"] = "0.1.0"
        q["original_identifier"] = "AUTHOR-REL-TRANSFER-01"
        q["stem"] = (
            "A travels at 6 m/s east and B at 8 m/s north. A display claims that "
            "the velocity of A relative to B is 10 m/s northeast. Decide whether "
            "the display could represent A relative to B, B relative to A, or neither, "
            "and justify the observer/order choice."
        )
        q["conditions"] = [
            "Constant velocities; common time and parallel nonrotating axes.",
            "The display gives only magnitude and compass direction, not components."
        ]
        q["difficulty"]["basis"] = (
            "Infer the observer and subtraction order from a disputed compass direction, "
            "then reject both proposed readings by comparing signed components."
        )
        q["answer"] = {
            "kind": "MODEL_RESPONSE",
            "summary": "Neither. A relative to B is southeast; B relative to A is northwest.",
            "reasoning": [
                "For A relative to B, subtract B's velocity from A's: (6,0)-(0,8)=(6,-8).",
                "That vector is southeast and has magnitude 10 m/s.",
                "Reversing the observer gives (-6,8), northwest, so northeast matches neither order."
            ],
            "check": "The two legitimate relative velocities must be exact opposites; southeast and northwest are opposite, northeast is not either one.",
            "acceptable_alternatives": [],
            "subpart_answers": [],
            "verification_status": "CHECKED_BY_AUTHOR",
            "difficult_move": 0
        }
        q["adaptation"] = {
            "parent_ref": "Q-AUTHOR-REL-01",
            "changed_fields": ["stem", "conditions", "answer"],
            "reason": "Changes the demand from direct component subtraction to deciding which observer/order a reported direction could represent."
        }
        q["exposure"] = [{
            "core": "CORE2B",
            "role": "TRANSFER_CANDIDATE",
            "artifact_ref": None
        }]
        q.pop("verification", None)
        q["hints"] = [{
            "text": "Before calculating, name the observer in each possible interpretation.",
            "reveals": "CONCEPT"
        }]
        q["transfer"] = {
            "dimension": "model_choice",
            "statement": "The learner must infer and test the observer/order from a reported direction instead of being handed the subtraction order.",
            "builds_on": ["Q-AUTHOR-REL-01"]
        }
        return q

    def proposal(self, request, packet, question=None):
        return {
            "run_id": "RUN-TEST-CORE2B-01",
            "version": "1.0.0",
            "actor_id": "test-agent",
            "run_date": "2026-09-18",
            "packet_digest": digest(packet),
            "request_digest": digest(request),
            "core": "CORE2B",
            "target_package": "Physics/library/relative-motion.v1.json",
            "proposed_records": [{
                "collection": "questions",
                "record": question or self.transfer_question(),
            }],
            "artifacts": [],
        }

    def test_core2b_fixture_compiles_to_candidate_authoring(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        order = next(row for row in packet["work_orders"] if row["core"] == "CORE2B")
        self.assertEqual(order["authoring_action"], "AUTHOR_CANDIDATE_QUESTION")
        self.assertEqual(order["write_scope"]["mode"], "CANDIDATE_RECORDS_ONLY")
        self.assertEqual(order["duties"], ["AUTHOR_SUPPLEMENTAL_PRACTICE"])

    def test_valid_candidate_run_emits_receipt_without_mutating_dry_run(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        before = self.PACKAGE.read_text(encoding="utf-8")
        report = execute_authoring_run.validate_run(
            request, packet, self.proposal(request, packet))
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(self.PACKAGE.read_text(encoding="utf-8"), before)
        receipt = report["receipt"]
        self.assertEqual(receipt["authoring_action"], "AUTHOR_CANDIDATE_QUESTION")
        self.assertEqual([row["id"] for row in receipt["changed_records"]],
                         ["Q-AUTHOR-REL-TRANSFER-01"])
        self.assertNotEqual(receipt["library_before"]["digest"],
                            receipt["library_after"]["digest"])
        self.assertEqual(receipt["validation"]["state"], "VALIDATED")

    def test_existing_canonical_record_cannot_be_mutated(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        question = self.transfer_question()
        question["id"] = "Q-AUTHOR-REL-01"
        report = execute_authoring_run.validate_run(
            request, packet, self.proposal(request, packet, question))
        self.assertIn("AUTHORING_EXISTING_RECORD_MUTATION_FORBIDDEN",
                      [row["point"] for row in report["findings"]])

    def test_core2b_requires_real_transfer_block(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        question = self.transfer_question()
        question.pop("transfer")
        report = execute_authoring_run.validate_run(
            request, packet, self.proposal(request, packet, question))
        self.assertIn("AUTHORING_CORE2B_TRANSFER_REQUIRED",
                      [row["point"] for row in report["findings"]])

    def test_core2b_cannot_fake_changed_fields(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        question = self.transfer_question()
        question["adaptation"]["changed_fields"] = ["version"]
        report = execute_authoring_run.validate_run(
            request, packet, self.proposal(request, packet, question))
        points = [row["point"] for row in report["findings"]]
        self.assertIn("AUTHORING_CORE2B_ADAPTATION_NOT_REAL", points)
        self.assertIn("AUTHORING_CORE2B_DEMAND_UNCHANGED", points)

    def test_candidate_cannot_self_promote_to_reviewed(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        question = self.transfer_question()
        question["status"] = "REVIEWED"
        report = execute_authoring_run.validate_run(
            request, packet, self.proposal(request, packet, question))
        self.assertIn("AUTHORING_STATUS_OUT_OF_SCOPE",
                      [row["point"] for row in report["findings"]])

    def test_stale_packet_digest_is_rejected(self):
        request = self.request(self.CORE2B)
        packet = compile_execution_packet.compile_packet(request)
        proposal = self.proposal(request, packet)
        proposal["packet_digest"] = "0" * 64
        report = execute_authoring_run.validate_run(request, packet, proposal)
        self.assertIn("AUTHORING_PACKET_STALE",
                      [row["point"] for row in report["findings"]])

    def test_product_output_run_cannot_touch_library(self):
        request = self.request(self.TEACHING)
        packet = compile_execution_packet.compile_packet(request)
        proposal = {
            "run_id": "RUN-TEST-CORE1-01",
            "version": "1.0.0",
            "actor_id": "test-agent",
            "run_date": "2026-09-18",
            "packet_digest": digest(packet),
            "request_digest": digest(request),
            "core": "CORE1",
            "target_package": "Physics/library/relative-motion.v1.json",
            "proposed_records": [],
            "artifacts": [{
                "relative_path": "core1.md",
                "media_type": "text/markdown",
                "content": "Synthetic product-output fixture; canonical records remain read-only."
            }],
        }
        report = execute_authoring_run.validate_run(request, packet, proposal)
        self.assertIn("AUTHORING_TARGET_PACKAGE_OUT_OF_SCOPE",
                      [row["point"] for row in report["findings"]])

    def test_product_output_path_cannot_escape_draft_root(self):
        request = self.request(self.TEACHING)
        packet = compile_execution_packet.compile_packet(request)
        proposal = {
            "run_id": "RUN-TEST-CORE1-01",
            "version": "1.0.0",
            "actor_id": "test-agent",
            "run_date": "2026-09-18",
            "packet_digest": digest(packet),
            "request_digest": digest(request),
            "core": "CORE1",
            "target_package": None,
            "proposed_records": [],
            "artifacts": [{
                "relative_path": "../../../../Shared/contracts.py",
                "media_type": "text/plain",
                "content": "escape attempt"
            }],
        }
        report = execute_authoring_run.validate_run(request, packet, proposal)
        self.assertIn("AUTHORING_ARTIFACT_PATH_OUT_OF_SCOPE",
                      [row["point"] for row in report["findings"]])

    def test_executor_audit_covers_all_runnable_write_scopes(self):
        report = execute_authoring_run.audit()
        self.assertTrue(report["passed"], report["findings"])
        self.assertGreaterEqual(report["requests"], 2)


if __name__ == "__main__":
    unittest.main()
