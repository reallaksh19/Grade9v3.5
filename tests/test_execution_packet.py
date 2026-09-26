"""Execution-packet lifecycle and stale-packet falsifiers."""
from __future__ import annotations

import copy
import json
import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import compile_execution_packet, plan_request  # noqa: E402


class AuthoringLifecycle(unittest.TestCase):
    FIXTURE = REPO / "Requests/relative-motion-teaching.author-request.json"

    def request(self):
        return json.loads(self.FIXTURE.read_text(encoding="utf-8"))

    def test_authoring_and_build_can_be_ready_before_human_review(self):
        report = plan_request.plan(self.request())
        self.assertEqual(report["lifecycle"]["AUTHORING"]["state"], "READY_FOR_AUTHORING")
        self.assertEqual(report["lifecycle"]["BUILD"]["state"], "READY_FOR_BUILD")
        self.assertEqual(report["lifecycle"]["RELEASE"]["state"], "OWNER_REVIEW")
        self.assertIn("ACADEMIC_REVIEW", report["lifecycle"]["RELEASE"]["review_labels"])
        self.assertIn("ACADEMIC_READINESS", report["lifecycle"]["RELEASE"]["review_labels"])

    def test_practice_only_request_uses_the_default_median_learner(self):
        request = {
            "request_id": "PRACTICE-ONLY",
            "subject": "Physics",
            "subtopic": "Relative motion",
            "requested_cores": ["CORE2A"],
            "practice": {"CORE2A": {"purpose": "PRACTICE"}},
        }
        report = plan_request.plan(request)
        self.assertEqual(report["required_owner_inputs"], [])
        learner = next(row for row in report["defaults_applied"] if row["field"] == "learner")
        self.assertEqual(learner["basis"], "DEFAULT_MEDIAN")
        self.assertNotEqual(report["learner_route"]["state"], "WAITING_FOR_OWNER_INPUT")


class ExecutionPacket(unittest.TestCase):
    TEACHING = REPO / "Requests/relative-motion-teaching.author-request.json"
    SIX = REPO / "Requests/relative-motion-six-core.plan-request.json"
    CURRENT = REPO / "Requests/relative-motion-six-core.ncert-current.plan-request.json"

    def request(self, path):
        return json.loads(path.read_text(encoding="utf-8"))

    def test_authoring_ready_request_compiles_a_ready_packet(self):
        request = self.request(self.TEACHING)
        packet = compile_execution_packet.compile_packet(request)
        self.assertEqual(packet["packet_state"], "READY")
        self.assertEqual(packet["summary"]["runnable_cores"],
                         ["CORE1", "CORE1A", "CORE1B"])
        self.assertEqual(packet["summary"]["research_and_author_cores"], [])
        self.assertTrue(compile_execution_packet.verify(packet, request)["passed"])

    def test_packet_pins_role_matrix_library_and_request(self):
        packet = compile_execution_packet.compile_packet(self.request(self.TEACHING))
        self.assertRegex(packet["request_digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(packet["pins"]["library"]["digest"], r"^[0-9a-f]{64}$")
        self.assertRegex(packet["pins"]["matrix"]["digest"], r"^[0-9a-f]{64}$")
        for order in packet["work_orders"]:
            self.assertRegex(order["role"]["sha256"], r"^[0-9a-f]{64}$")
            self.assertTrue(order["role"]["required_fields"])

    def test_six_core_prompt_runs_every_core_with_duties_first(self):
        packet = compile_execution_packet.compile_packet(self.request(self.SIX))
        self.assertEqual(packet["packet_state"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(packet["summary"]["runnable_cores"],
                         ["CORE1", "CORE2", "CORE1A", "CORE1B", "CORE2A", "CORE2B"])
        self.assertEqual(packet["summary"]["research_and_author_cores"],
                         ["CORE2", "CORE2A", "CORE2B"])
        for order in packet["work_orders"]:
            self.assertNotEqual(order["write_scope"]["mode"], "NO_WRITE")

    def test_source_drift_is_researched_only_for_source_backed_work_orders(self):
        packet = compile_execution_packet.compile_packet(self.request(self.CURRENT))
        core1 = next(row for row in packet["work_orders"] if row["core"] == "CORE1")
        self.assertEqual(core1["authoring_action"], "BUILD_FROM_CANONICAL")
        for core in ("CORE2", "CORE2A", "CORE2B"):
            order = next(row for row in packet["work_orders"] if row["core"] == core)
            self.assertEqual(order["authoring_action"], "RESEARCH_SOURCE")
            self.assertIn("RESOLVE_SOURCE_BASIS_DRIFT", order["duties"])

    def test_core2_source_custody_is_never_replaced_by_authored_generation(self):
        request = self.request(self.SIX)
        request["source_receipt_ref"] = "SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY"
        request["learner"] = {
            "owner_entry": {
                "rung": "R1", "by": "test",
                "instruction": "Routing decision for a packet test."
            }
        }
        request["practice"] = {
            "CORE2A": {"purpose": "PRACTICE"},
            "CORE2B": {"purpose": "COMPETITION"},
        }
        request["supplemental_question_policy"] = "ALLOW_AUTHORED_CANDIDATES"
        packet = compile_execution_packet.compile_packet(request)
        core2 = next(row for row in packet["work_orders"] if row["core"] == "CORE2")
        self.assertNotEqual(core2["authoring_action"], "AUTHOR_CANDIDATE_QUESTION")
        self.assertEqual(core2["authoring_action"],
                         "BUILD_FROM_CANONICAL" if core2["product_state"] == "READY"
                         else "RESEARCH_SOURCE")
        self.assertNotEqual(core2["write_scope"].get("origin"), "AUTHORED")

    def test_authored_supplement_can_only_be_a_candidate_practice_question(self):
        request = self.request(self.SIX)
        request["source_receipt_ref"] = "SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY"
        request["learner"] = {
            "owner_entry": {
                "rung": "R1", "by": "test",
                "instruction": "Routing decision for a packet test."
            }
        }
        request["practice"] = {
            "CORE2A": {"purpose": "PRACTICE"},
            "CORE2B": {"purpose": "COMPETITION"},
        }
        request["supplemental_question_policy"] = "ALLOW_AUTHORED_CANDIDATES"
        packet = compile_execution_packet.compile_packet(request)
        core2b = next(row for row in packet["work_orders"] if row["core"] == "CORE2B")
        self.assertEqual(core2b["authoring_action"], "AUTHOR_CANDIDATE_QUESTION")
        self.assertEqual(core2b["write_scope"]["mode"], "CANDIDATE_RECORDS_ONLY")
        self.assertEqual(core2b["write_scope"]["status"], "CANDIDATE")
        self.assertEqual(core2b["write_scope"]["origin"], "AUTHORED")

    def test_source_receipt_is_pinned_and_staleness_is_detected(self):
        request = self.request(self.SIX)
        request["source_receipt_ref"] = "SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY"
        request["learner"] = {
            "owner_entry": {
                "rung": "R1", "by": "test",
                "instruction": "Routing decision for a packet test."
            }
        }
        request["practice"] = {
            "CORE2A": {"purpose": "PRACTICE"},
            "CORE2B": {"purpose": "COMPETITION"},
        }
        request["supplemental_question_policy"] = "ALLOW_AUTHORED_CANDIDATES"
        packet = compile_execution_packet.compile_packet(request)
        pin = packet["pins"]["source_receipt"]
        self.assertEqual(pin["receipt_id"],
                         "SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY")
        self.assertRegex(pin["digest"], r"^[0-9a-f]{64}$")
        packet["pins"]["source_receipt"]["digest"] = "0" * 64
        report = compile_execution_packet.verify(packet, request)
        self.assertIn("EXECUTION_PACKET_SOURCE_RECEIPT_STALE",
                      [row["point"] for row in report["findings"]])

    def test_request_change_invalidates_the_packet(self):
        request = self.request(self.TEACHING)
        packet = compile_execution_packet.compile_packet(request)
        changed = copy.deepcopy(request)
        changed["learner"]["owner_entry"]["rung"] = "R3"
        report = compile_execution_packet.verify(packet, changed)
        self.assertIn("EXECUTION_PACKET_REQUEST_STALE",
                      [row["point"] for row in report["findings"]])

    def test_role_contract_change_invalidates_the_packet(self):
        request = self.request(self.TEACHING)
        packet = compile_execution_packet.compile_packet(request)
        packet["work_orders"][0]["role"]["sha256"] = "0" * 64
        report = compile_execution_packet.verify(packet, request)
        self.assertIn("EXECUTION_PACKET_ROLE_STALE",
                      [row["point"] for row in report["findings"]])


if __name__ == "__main__":
    unittest.main()
