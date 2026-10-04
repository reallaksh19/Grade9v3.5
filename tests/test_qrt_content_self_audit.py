from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import qrt_content_self_audit as audit


def checks(names):
    return {
        name: {"result": "PASS", "evidence": f"Evidence for {name}."}
        for name in names
    }


def passing_viewports():
    return {
        name: {
            "controls": 3,
            "smallTargets": 0,
            "smallTargetSample": [],
            "horizontalOverflowPx": 0,
            "wideElements": 0,
            "focusFailures": 0,
            "focusVisibleFailures": 0,
            "svgCount": 1,
            "inaccessibleSvgCount": 0,
            "mainCount": 1,
            "headingCount": 2,
        }
        for name in audit.EXPECTED_VIEWPORTS
    }


class QRTContentSelfAuditTests(unittest.TestCase):
    def base_run(self):
        return {
            "run_identity": {"head_sha": "a" * 40},
            "questions": [
                {
                    "id": "Q1",
                    "hints": [
                        {
                            "id": "H1",
                            "text": "Count the physical faces first.",
                            "calculation_bearing": False,
                            "calculation_refs": [],
                            "self_audit": {
                                "status": "PASS",
                                "summary_evidence": ["Does not reveal the final expression."],
                                "basis_refs": ["Q1.W", "QRT-APPLY-D1.H1"],
                                "checks": checks(audit.HINT_CHECKS),
                            },
                        }
                    ],
                    "solution_steps": [
                        {
                            "id": "SOLUTION-1",
                            "action": "Find one face area.",
                            "why_valid_here": "Each face is a square of side 7 cm.",
                            "result": "49 cm2 per face.",
                            "calculation_bearing": True,
                            "calculation_refs": ["C1"],
                            "self_audit": {
                                "status": "PASS",
                                "summary_evidence": ["The move is anchored to the cube dimensions."],
                                "basis_refs": ["Q1.stem", "Q1.C1"],
                                "checks": checks(audit.SOLUTION_CHECKS),
                            },
                        }
                    ],
                    "calculations": [
                        {
                            "id": "C1",
                            "expression": "7 × 7",
                            "result": "49 cm2",
                            "self_audit": {
                                "status": "PASS",
                                "summary_evidence": ["Independent multiplication check: 7×7=49."],
                                "basis_refs": ["Q1.stem"],
                                "checks": checks(audit.CALCULATION_CHECKS),
                            },
                        }
                    ],
                }
            ],
            "pre_attempt_graphs": [],
            "rendered_artifacts": [],
            "validation": {"interactive_chromium_receipts": []},
        }

    def test_every_hint_requires_self_audit(self):
        run = self.base_run()
        del run["questions"][0]["hints"][0]["self_audit"]
        self.assertIn(
            "SELF_AUDIT_MISSING: Q1:HINT:H1",
            audit.validate_content_self_audits(run),
        )

    def test_hint_audit_requires_purpose_fit_and_actionable_specificity(self):
        run = self.base_run()
        del run["questions"][0]["hints"][0]["self_audit"]["checks"]["purpose_fit"]
        problems = audit.validate_content_self_audits(run)
        self.assertIn(
            "SELF_AUDIT_CHECK_MISSING_OR_INVALID: Q1:HINT:H1:purpose_fit",
            problems,
        )
        self.assertNotIn(
            "SELF_AUDIT_CHECK_MISSING_OR_INVALID: Q1:HINT:H1:actionable_specificity",
            problems,
        )

    def test_every_named_check_requires_its_own_evidence(self):
        run = self.base_run()
        run["questions"][0]["hints"][0]["self_audit"]["checks"]["w_protection"]["evidence"] = ""
        self.assertIn(
            "SELF_AUDIT_CHECK_EVIDENCE_MISSING: Q1:HINT:H1:w_protection",
            audit.validate_content_self_audits(run),
        )

    def test_solution_calculation_reference_must_resolve(self):
        run = self.base_run()
        run["questions"][0]["solution_steps"][0]["calculation_refs"] = ["NOPE"]
        self.assertIn(
            "CALCULATION_REF_UNKNOWN: Q1:SOLUTION:SOLUTION-1:NOPE",
            audit.validate_content_self_audits(run),
        )

    def test_failed_calculation_check_blocks(self):
        run = self.base_run()
        run["questions"][0]["calculations"][0]["self_audit"]["checks"]["units_dimensions"]["result"] = "FAIL"
        self.assertIn(
            "SELF_AUDIT_CHECK_FAILED: Q1:CALCULATION:C1:units_dimensions",
            audit.validate_content_self_audits(run),
        )

    def test_interactive_page_requires_chromium_receipt(self):
        run = self.base_run()
        run["rendered_artifacts"] = [
            {"id": "EXPLORER", "kind": "INTERACTIVE_HTML", "sha256": "sha256:" + "1" * 64}
        ]
        self.assertIn(
            "INTERACTIVE_CHROMIUM_RECEIPT_MISSING: EXPLORER",
            audit.validate_interactive_chromium(run),
        )

    def test_active_explorer_blueprint_requires_chromium_even_without_kind(self):
        run = self.base_run()
        run["rendered_artifacts"] = [
            {
                "id": "EXPLORER",
                "blueprint_ref": "BP-EXPLORER-GCDR@1.0.0",
                "sha256": "sha256:" + "1" * 64,
            }
        ]
        self.assertIn(
            "INTERACTIVE_CHROMIUM_RECEIPT_MISSING: EXPLORER",
            audit.validate_interactive_chromium(run),
        )

    def test_linked_interactive_node_must_register_artifact(self):
        run = self.base_run()
        run["pre_attempt_graphs"] = [
            {
                "question_ref": "Q1",
                "nodes": [
                    {
                        "id": "EXPLORER-LINK",
                        "phase": "POST_ATTEMPT",
                        "resource_kind": "EXPLORER",
                        "blueprint_ref": "BP-EXPLORER-GCDR@1.0.0",
                    }
                ],
            }
        ]
        self.assertIn(
            "INTERACTIVE_GRAPH_ARTIFACT_REF_MISSING: Q1:EXPLORER-LINK",
            audit.validate_interactive_chromium(run),
        )

    def test_linked_interactive_node_cannot_point_to_noninteractive_artifact(self):
        run = self.base_run()
        run["rendered_artifacts"] = [{"id": "CORE2", "kind": "CORE2_HTML", "sha256": "sha256:" + "1" * 64}]
        run["pre_attempt_graphs"] = [
            {
                "question_ref": "Q1",
                "nodes": [
                    {
                        "id": "EXPLORER-LINK",
                        "phase": "POST_ATTEMPT",
                        "resource_kind": "EXPLORER",
                        "artifact_ref": "CORE2",
                    }
                ],
            }
        ]
        self.assertIn(
            "INTERACTIVE_GRAPH_ARTIFACT_NOT_INTERACTIVE: Q1:EXPLORER-LINK:CORE2",
            audit.validate_interactive_chromium(run),
        )

    def test_chromium_receipt_is_bound_to_exact_artifact_and_report_bytes(self):
        run = self.base_run()
        original_repo = audit.REPO
        try:
            with tempfile.TemporaryDirectory() as tmp:
                audit.REPO = Path(tmp)
                page = audit.REPO / "interactive.html"
                page.write_text("<main><h1>Explorer</h1></main>", encoding="utf-8")
                artifact_digest = audit.sha256_file(page)
                report = {
                    "schema": "interactive-page-audit/v1",
                    "tool": audit.CHROMIUM_TOOL,
                    "engine": audit.CHROMIUM_ENGINE,
                    "profile": "tablet-12.7",
                    "head_sha": "a" * 40,
                    "artifact_sha256": artifact_digest,
                    "status": "PASS",
                    "viewports": passing_viewports(),
                    "page_errors": [],
                    "console_errors": [],
                    "external_requests": [],
                    "failures": [],
                }
                report_path = audit.REPO / "interactive-audit.json"
                report_path.write_text(json.dumps(report), encoding="utf-8")
                report_digest = audit.sha256_file(report_path)

                run["rendered_artifacts"] = [
                    {
                        "id": "EXPLORER",
                        "kind": "INTERACTIVE_HTML",
                        "blueprint_ref": "BP-EXPLORER-GCDR@1.0.0",
                        "path": "interactive.html",
                        "sha256": artifact_digest,
                    }
                ]
                run["validation"]["interactive_chromium_receipts"] = [
                    {
                        "artifact_ref": "EXPLORER",
                        "artifact_sha256": artifact_digest,
                        "head_sha": "a" * 40,
                        "tool": audit.CHROMIUM_TOOL,
                        "engine": audit.CHROMIUM_ENGINE,
                        "profile": "tablet-12.7",
                        "status": "PASS",
                        "report_path": "interactive-audit.json",
                        "report_sha256": report_digest,
                    }
                ]
                self.assertEqual(audit.validate_interactive_chromium(run), [])

                page.write_text("<main><h1>Changed explorer</h1></main>", encoding="utf-8")
                run["rendered_artifacts"][0]["sha256"] = audit.sha256_file(page)
                problems = audit.validate_interactive_chromium(run)
                self.assertIn("INTERACTIVE_CHROMIUM_ARTIFACT_DIGEST_MISMATCH: EXPLORER", problems)
        finally:
            audit.REPO = original_repo

    def test_report_cannot_claim_pass_with_hidden_browser_failure(self):
        report = {
            "schema": "interactive-page-audit/v1",
            "tool": audit.CHROMIUM_TOOL,
            "engine": audit.CHROMIUM_ENGINE,
            "profile": "tablet-12.7",
            "head_sha": "a" * 40,
            "artifact_sha256": "sha256:" + "1" * 64,
            "status": "PASS",
            "viewports": passing_viewports(),
            "page_errors": ["boom"],
            "console_errors": [],
            "external_requests": [],
            "failures": [],
        }
        problems = audit._validate_report_facts("EXPLORER", report, "sha256:" + "1" * 64, "a" * 40)
        self.assertIn("INTERACTIVE_CHROMIUM_REPORT_FIELD_NOT_EMPTY: EXPLORER:page_errors", problems)


if __name__ == "__main__":
    unittest.main()
