from __future__ import annotations

import copy
import json
import subprocess
import sys
import unittest
from pathlib import Path

try:
    import jsonschema
except ModuleNotFoundError:  # pragma: no cover - repository CI installs it
    jsonschema = None

from Shared.contracts import load
from Shared.tools import (
    atlas_need,
    compile_execution_packet,
    focus_inventory,
    measurement_pack,
    plan_request,
    resolve_request,
)

REPO = Path(__file__).resolve().parents[1]
NLM_MATRIX = "MATRIX-PHY-NLM-FIRST-LAW"
NLM_BUCKET = "BUCKET-PHY-NLM-FIRST-LAW"
MATH_MATRIX = "MATRIX-MATH-LINEAR-EQUATIONS"
MATH_BUCKET = "BUCKET-LINEAR-EQUATION"


def envelope(subject: str, matrix_id: str, subtopic: str, rows: list[dict]) -> dict:
    return {
        "format": "GRADE9V3_EXTERNAL_DIAGNOSTIC_GAP_ENVELOPE",
        "version": "0.1.0",
        "diagnostic_id": f"DG-{matrix_id}",
        "matrix_id": matrix_id,
        "subject": subject,
        "subtopic": subtopic,
        "when": "2026-09-20T00:00:00Z",
        "provenance": "HISTORICAL_IMPORT",
        "evidence_kind": "PRIOR_DIAGNOSTIC",
        "rows": rows,
    }


def nlm_envelope(rows: list[dict]) -> dict:
    return envelope("Physics", NLM_MATRIX, "Newton's first law and free-body diagrams", rows)


def math_envelope(rows: list[dict]) -> dict:
    return envelope("Mathematics", MATH_MATRIX, "One-unknown linear equations over the rationals", rows)


class SharedTopicAtlasCoreTest(unittest.TestCase):
    def test_transient_schema_accepts_browser_envelope_and_rejects_demonstrated(self):
        if jsonschema is None:
            self.skipTest("jsonschema not installed")
        schema = load(REPO / "Shared/library/diagnostic-gap-envelope.schema.json")
        valid = nlm_envelope([{
            "capability_ref": "CAP-NLM-FRICTION",
            "repair_ref": "NLM5-2",
            "result": "MISSING",
            "error_stage": "CONCEPT",
            "score": 20,
            "observed": "Used object velocity instead of contact slip tendency.",
        }])
        self.assertEqual([], list(jsonschema.Draft202012Validator(schema).iter_errors(valid)))
        invalid = copy.deepcopy(valid)
        invalid["rows"][0]["result"] = "DEMONSTRATED"
        self.assertTrue(list(jsonschema.Draft202012Validator(schema).iter_errors(invalid)))

    def test_nlm_exact_unknown_and_capability_fallback_addresses_are_independent(self):
        report = atlas_need.resolve(nlm_envelope([
            {
                "capability_ref": "CAP-NLM-FRICTION",
                "repair_ref": "NLM5-2",
                "result": "MISSING",
                "error_stage": "CONCEPT",
                "score": 20,
                "observed": "Concept gap.",
            },
            {
                "capability_ref": "CAP-NLM-FRICTION",
                "repair_ref": "NLM5-2",
                "result": "UNCERTAIN",
                "error_stage": "SETUP",
                "score": 50,
                "observed": "Setup gap.",
            },
            {
                "capability_ref": "CAP-NLM-FRICTION",
                "repair_ref": "NO-SUCH-STEP",
                "result": "MISSING",
                "error_stage": "EXECUTION",
                "observed": "Narrow target was not canonical.",
            },
        ]))
        self.assertEqual("VALID", report["state"])
        self.assertEqual(["R5.1.0", "R5.1.1", "R5.99"],
                         [row["address"] for row in report["targets"]])
        self.assertEqual([20, 50, None], [row["score"] for row in report["targets"]])
        self.assertEqual("CAPABILITY_ONLY_FALLBACK", report["targets"][2]["fallback_level"])
        self.assertEqual(1, len(report["warnings"]))

    def test_invalid_rows_are_isolated_without_fuzzy_mapping(self):
        report = atlas_need.resolve(nlm_envelope([
            {
                "capability_ref": "CAP-NLM-FRICTION",
                "repair_ref": "NLM5-2",
                "result": "MISSING",
                "error_stage": "UNKNOWN",
                "observed": "Valid row.",
            },
            {
                "capability_ref": "CAP-NOT-REAL",
                "result": "MISSING",
                "error_stage": "CONCEPT",
                "observed": "Unknown capability.",
            },
            {
                "capability_ref": "CAP-NLM-FRICTION",
                "result": "DEMONSTRATED",
                "error_stage": "CONCEPT",
                "observed": "Invalid gap result.",
            },
        ]))
        self.assertEqual("PARTIAL", report["state"])
        self.assertFalse(report["passed"])
        self.assertEqual(["R5.1.99"], [row["address"] for row in report["targets"]])
        self.assertEqual(2, len(report["rejected"]))

    def test_measurement_pack_separates_measurement_from_routing_context(self):
        pack = measurement_pack.build("Physics", NLM_MATRIX)
        r5 = next(row for row in pack["targets"]
                  if row["routing_context"]["rung"] == "R5")
        self.assertEqual("CAP-NLM-FRICTION", r5["measurement"]["capability_ref"])
        self.assertIn("NLM5-2", [x["id"] for x in r5["measurement"]["semantic_actions"]])
        self.assertNotIn("ladder_position", r5["measurement"])
        self.assertEqual(78, r5["routing_context"]["ladder_position"])
        self.assertEqual(["MISSING", "UNCERTAIN"],
                         pack["diagnostic_contract"]["result_values"])
        self.assertIn("UNKNOWN", pack["diagnostic_contract"]["error_stage_values"])

    def test_measurement_pack_cli_runs_for_physics_and_mathematics(self):
        for subject, matrix_id in (
            ("Physics", NLM_MATRIX),
            ("Mathematics", MATH_MATRIX),
        ):
            completed = subprocess.run(
                [
                    sys.executable,
                    "Shared/tools/measurement_pack.py",
                    "--subject",
                    subject,
                    "--matrix",
                    matrix_id,
                ],
                cwd=REPO,
                check=True,
                capture_output=True,
                text=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(matrix_id, payload["matrix_id"])
            self.assertEqual(subject, payload["subject"])
            self.assertTrue(payload["targets"])

    def test_math_uses_same_resolver_and_keeps_inventory_fallback_truthful(self):
        report = atlas_need.resolve(math_envelope([{
            "capability_ref": "CAP-MATH-ISOLATE",
            "repair_ref": "ME-1",
            "result": "MISSING",
            "error_stage": "SETUP",
            "observed": "Applied an operation to one side only.",
        }]))
        self.assertEqual("R2.0.1", report["targets"][0]["address"])
        inventory = focus_inventory.for_core(
            "Mathematics", MATH_BUCKET, "CORE1A", report["targets"]
        )
        questions = inventory["targets"][0]["questions"]
        self.assertEqual(["Q-MATH-LINEAR-01"], [x["id"] for x in questions])
        self.assertEqual("CAPABILITY_LEVEL", questions[0]["precision"])

    def test_nlm_inventory_prefers_explicit_repair_binding_and_activity_does_not_overclaim(self):
        report = atlas_need.resolve(nlm_envelope([{
            "capability_ref": "CAP-NLM-FRICTION",
            "repair_ref": "NLM5-2",
            "result": "MISSING",
            "error_stage": "CONCEPT",
            "observed": "Used wrong friction direction rule.",
        }]))
        inventory = focus_inventory.for_core(
            "Physics", NLM_BUCKET, "CORE2A", report["targets"]
        )
        target = inventory["targets"][0]
        by_id = {row["id"]: row for row in target["questions"]}
        self.assertEqual("EXACT_REPAIR_REF",
                         by_id["Q-PHY-NLM-2A-COV-04"]["precision"])
        activities = {row["id"]: row for row in target["activities"]}
        self.assertEqual(
            "CAPABILITY_LEVEL",
            activities["ACT-NLM-FRICTION-THRESHOLD"]["precision"],
        )

    def test_plan_request_focus_does_not_change_readiness_or_estimate_route(self):
        request = {
            "request_id": "REQ-TA2-PLAN",
            "subject": "Physics",
            "bucket_id": NLM_BUCKET,
            "requested_cores": ["CORE1A", "CORE2A"],
            "learner": {"owner_estimate": {"knowledge_percentage": 100}},
            "practice": {"CORE2A": {"purpose": "PRACTICE"}},
        }
        diagnostic = nlm_envelope([{
            "capability_ref": "CAP-NLM-FRICTION",
            "repair_ref": "NLM5-2",
            "result": "MISSING",
            "error_stage": "CONCEPT",
            "observed": "Wrong contact-slip rule.",
        }])
        baseline = plan_request.plan(request)
        focused = plan_request.plan(request, diagnostic=diagnostic)
        for key in ("products", "readiness", "learner_route",
                    "required_owner_inputs", "findings", "lifecycle"):
            self.assertEqual(baseline.get(key), focused.get(key), key)
        self.assertEqual("R7", focused["learner_route"]["entry"])
        self.assertNotEqual("R4", focused["learner_route"]["entry"])
        self.assertEqual("R5.1.0", focused["diagnostic_focus"]["targets"][0]["address"])

    def test_strict_resolver_focus_does_not_change_core_or_segment_authority(self):
        request = {
            "request_id": "REQ-TA2-STRICT",
            "subject": "Physics",
            "bucket_id": NLM_BUCKET,
            "cores": ["CORE1A", "CORE2A"],
            "learner": {
                "owner_estimate": {
                    "knowledge_percentage": 80,
                    "by": "OWNER",
                    "instruction": "Use as a routing coordinate only.",
                }
            },
            "practice": {"CORE2A": {"purpose": "PRACTICE"}},
        }
        diagnostic = nlm_envelope([{
            "capability_ref": "CAP-NLM-FRICTION",
            "repair_ref": "NLM5-2",
            "result": "MISSING",
            "error_stage": "SETUP",
            "observed": "Setup did not identify slip tendency.",
        }])
        baseline = resolve_request.plan(request)
        focused = resolve_request.plan(request, diagnostic=diagnostic)
        for key in ("entry", "segment", "cores", "findings", "passed"):
            self.assertEqual(baseline.get(key), focused.get(key), key)
        self.assertEqual("R5.1.1", focused["diagnostic_focus"]["targets"][0]["address"])

    def test_execution_packet_pins_diagnostic_and_detects_staleness(self):
        request = {
            "request_id": "REQ-TA2-PACKET",
            "subject": "Physics",
            "bucket_id": NLM_BUCKET,
            "requested_cores": ["CORE1A"],
            "learner": {"owner_estimate": {"knowledge_percentage": 80}},
        }
        diagnostic = nlm_envelope([{
            "capability_ref": "CAP-NLM-FRICTION",
            "repair_ref": "NLM5-2",
            "result": "MISSING",
            "error_stage": "CONCEPT",
            "score": 20,
            "observed": "Concept evidence.",
        }])
        packet = compile_execution_packet.compile_packet(request, diagnostic=diagnostic)
        self.assertIsNotNone(packet["pins"]["diagnostic"])
        self.assertEqual(
            "R5.1.0",
            packet["work_orders"][0]["target"]["diagnostic_focus"]["targets"][0]["address"],
        )
        self.assertTrue(
            compile_execution_packet.verify(packet, request, diagnostic=diagnostic)["passed"]
        )
        changed = copy.deepcopy(diagnostic)
        changed["rows"][0]["score"] = 21
        stale = compile_execution_packet.verify(packet, request, diagnostic=changed)
        self.assertFalse(stale["passed"])
        self.assertIn(
            "EXECUTION_PACKET_DIAGNOSTIC_STALE",
            [row["point"] for row in stale["findings"]],
        )


if __name__ == "__main__":
    unittest.main()
