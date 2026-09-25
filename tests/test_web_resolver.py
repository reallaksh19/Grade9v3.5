from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import build_explore_page, derived_artifact_registry, web_resolver, web_validator

MOTION = "MATRIX-PHY-KIN-2D-MOTION"
NLM = "MATRIX-PHY-NLM-FIRST-LAW"
MATH = "MATRIX-MATH-LINEAR-EQUATIONS"
FAMILIAR = "Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04"


def request(subject, target, mode, *, core=None, interaction="OPTIONAL", packaging="PUBLIC", preparation=False):
    target = dict(target)
    if preparation:
        target["preparation_request"] = True
    segment = {"mode": mode, "interaction_requirement": interaction}
    if core:
        segment["core"] = core
    return {
        "schema_version": "1.0.0",
        "request_id": f"TEST-{subject}-{mode}-{core or 'NONE'}",
        "subject": subject,
        "target": target,
        "experience_segments": [segment],
        "packaging_mode": packaging,
    }


def prepared_route(exact_ref=FAMILIAR):
    target_id = "TARGET-TEST"
    move_id = "MOVE-TEST"
    return {
        "schema_version": "1.1.0",
        "route_bundle_id": "ROUTE-TEST",
        "subject": "Physics",
        "learner_context": {
            "evidence_state": "UNKNOWN", "owner_estimate_percent": None,
            "owner_routing_waiver": False, "readiness_claim_allowed": False,
            "support_policy": "STANDARD",
        },
        "targets": [{
            "target_id": target_id, "owner_ref": exact_ref, "summary": "Target application",
            "identity": {
                "state": "EXACT_CONFIRMED", "exact_ref": exact_ref,
                "candidate_refs": [exact_ref], "candidate_set_provenance": "Canonical ref",
                "demand_fingerprint": {
                    "setup": "Horizontal launch", "requested_output": "Range",
                    "special_condition": None, "answer_type": "Numeric",
                    "distinctive_transformation": "Separate component motion",
                },
                "discriminating_features": [], "rejected_candidates": [],
                "resolution_decision": "Exact ref", "resolution_reviewer": "reviewer",
                "identity_confidence": "HIGH",
            },
            "authority": {
                "target_authority": "OWNER_FIXED", "direct_source_use": "ALLOWED",
                "instructional_demand_use": "ALLOWED", "assessment_claim": "HOLD",
            },
            "source_custody_state": "PASS",
            "demand_moves": [{
                "move_id": move_id, "description": "Resolve components",
                "decision_type": "DECIDE", "provenance_class": "CANONICAL_DERIVED",
                "required_capability_refs": ["CAP-KIN-PROJECTILE-MODEL"],
                "unresolved_capability_descriptions": [],
                "closure": {
                    "state": "ESTABLISHED_CURRENT_SCOPE",
                    "canonical_refs": ["CAP-KIN-PROJECTILE-MODEL"],
                    "bridge_candidate_ref": None, "hold_close_when": None,
                },
                "coverage": {
                    "entry_task_ref": "ENTRY-TEST", "teaching_refs": ["TEACH-TEST"],
                    "supported_attempt_refs": ["GUIDED-TEST"],
                    "independent_evidence_refs": ["EVIDENCE-TEST"],
                    "target_use_ref": target_id, "coverage_state": "INDEPENDENT_EVIDENCE",
                },
            }],
            "coverage_state": "INDEPENDENT_EVIDENCE_COMPLETE",
            "authorization_state": "READY", "preparation_state": "PREPARED",
            "target_route": [
                {"sequence": 1, "kind": "CORE2A", "ref": "PRACTICE-TEST",
                 "prepares_move_refs": [move_id], "reason": "Familiar application"},
                {"sequence": 2, "kind": "TARGET", "ref": target_id,
                 "prepares_move_refs": [move_id], "reason": "Attempt target"},
            ],
            "terminal_block": None,
        }],
        "bridge_candidates": [],
        "core_demand_influences": [],
        "validation": {
            "all_fixed_targets_accounted_for": True,
            "all_required_moves_have_coverage_ledgers": True,
            "generic_practice_not_used_as_target_closure": True,
            "core1_family_scope_unchanged": True,
            "owner_waiver_not_treated_as_mastery": True,
            "owner_waiver_not_used_to_bypass_academic_review": True,
            "blocked_target_counted_as_prepared": False,
            "fixed_target_preparation_acceptance": "PASS",
        },
    }


class WebResolverTests(unittest.TestCase):
    def test_motion_r1_required_explore_reuses_portable_activity(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
            "EXPLORE", interaction="REQUIRED",
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        self.assertEqual(plan["build_action"], "EXPLORE_PAGE_ADAPTER")
        self.assertEqual(plan["availability"]["representation"]["status"], "READY")
        self.assertEqual(plan["availability"]["activity"]["status"], "READY")
        self.assertEqual(plan["availability"]["portable_package"]["status"], "READY")
        package = build_explore_page.compile_page_package(plan)
        self.assertEqual(package["mount_mode"], "PORTABLE_SCENE")
        self.assertEqual(package["portable_package"]["id"], "portable-motion-shared-clock")

    def test_motion_explore_adapter_emits_shell_and_local_portable_runtime(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
            "EXPLORE", interaction="REQUIRED",
        ))
        package = build_explore_page.compile_page_package(plan)
        rendered = build_explore_page.render_directory(package, "PUBLIC")
        html = rendered["index.html"].decode("utf-8")
        self.assertIn('data-shell-ref="G9-TABLET-SHELL-V1"', html)
        self.assertIn("<semantic-workbench", html)
        self.assertIn("portable-package.json", rendered)
        self.assertIn("portable-host.mjs", rendered)
        self.assertNotIn("https://", html)

    def test_nlm_r5_activity_does_not_invent_missing_rung_representation(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": NLM, "rung": "R5"},
            "EXPLORE", interaction="REQUIRED",
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        self.assertEqual(plan["availability"]["representation"]["requirement"], "NOT_REQUIRED")
        self.assertEqual(plan["availability"]["representation"]["status"], "NOT_REQUIRED")
        self.assertEqual(plan["availability"]["activity"]["status"], "READY")
        self.assertEqual(plan["target"]["resolved_refs"]["representation_refs"], [])

    def test_math_r1_static_representation_is_not_interactive(self):
        optional = web_resolver.resolve(request(
            "Mathematics", {"matrix_ref": MATH, "rung": "R1"},
            "EXPLORE", interaction="OPTIONAL",
        ))
        self.assertTrue(optional["artifact_buildable"])
        self.assertEqual(optional["request_satisfaction"], "DEGRADED_ACCEPTABLE")
        self.assertEqual(optional["availability"]["representation"]["status"], "READY")
        self.assertEqual(optional["availability"]["activity"]["status"], "NOT_REQUIRED")
        self.assertEqual(optional["availability"]["renderer"]["status"], "READY")
        self.assertIn("STATIC_RENDERER_INSTEAD_OF_INTERACTIVE_ACTIVITY", optional["fallback_used"])

        required = web_resolver.resolve(request(
            "Mathematics", {"matrix_ref": MATH, "rung": "R1"},
            "EXPLORE", interaction="REQUIRED",
        ))
        self.assertTrue(required["artifact_buildable"])
        self.assertEqual(required["request_satisfaction"], "HOLD")
        self.assertEqual(required["build_action"], "HOLD")
        self.assertTrue(any(
            row["code"] == "WEB_REQUIRED_INTERACTION_UNAVAILABLE"
            for row in required["findings"]
        ))

    def test_learn_mode_includes_core1_not_only_ab_variants(self):
        plan = web_resolver.resolve(request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
            "LEARN", core="CORE1",
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        self.assertEqual(plan["build_action"], "CORE_PAGE_ADAPTER")
        segment = plan["experience_segments"][0]
        self.assertEqual(segment["provider_status"], "READY_EXISTING")
        self.assertTrue(segment["projection_ref"])
        self.assertIsNone(segment["remembered_reuse"])

    def test_core2a_exact_question_uses_provider_and_saved_artifact(self):
        plan = web_resolver.resolve(request(
            "Physics", {"exact_ref": FAMILIAR},
            "PRACTICE", core="CORE2A",
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        segment = plan["experience_segments"][0]
        self.assertEqual(segment["provider_status"], "READY_EXISTING")
        self.assertIsNone(segment["remembered_reuse"])
        self.assertEqual(plan["target"]["resolved_refs"]["question_refs"], [FAMILIAR])

    def test_target_preparation_requires_286_receipt_and_independent_authorization(self):
        req = request(
            "Physics", {"exact_ref": FAMILIAR},
            "PRACTICE", core="CORE2A", preparation=True,
        )
        missing = web_resolver.resolve(req)
        self.assertEqual(missing["request_satisfaction"], "HOLD")
        self.assertTrue(any(row["code"] == "WEB_TARGET_ROUTE_REQUIRED" for row in missing["findings"]))

        forged = {
            "schema_version": "1.1.0",
            "route_bundle_id": "ROUTE-TEST",
            "subject": "Physics",
            "targets": [{
                "target_id": "TARGET-TEST",
                "owner_ref": FAMILIAR,
                "identity": {"exact_ref": FAMILIAR},
                "coverage_state": "INDEPENDENT_EVIDENCE_COMPLETE",
                "authorization_state": "READY",
                "preparation_state": "PREPARED",
            }],
        }
        held = web_resolver.resolve(req, route_artifact=forged)
        self.assertEqual(held["request_satisfaction"], "HOLD")
        self.assertTrue(any(row["code"] == "WEB_TARGET_ROUTE_INVALID" for row in held["findings"]))

        route = prepared_route()
        resolved = web_resolver.resolve(req, route_artifact=route)
        self.assertNotEqual(resolved["request_satisfaction"], "HOLD")
        self.assertEqual(resolved["target_route"]["contract_version"], "1.1.0")
        self.assertEqual(resolved["target_route"]["demand_move_refs"], ["MOVE-TEST"])

        broken = copy.deepcopy(route)
        broken["targets"][0]["demand_moves"][0]["coverage"]["independent_evidence_refs"] = []
        held = web_resolver.resolve(req, route_artifact=broken)
        self.assertEqual(held["request_satisfaction"], "HOLD")
        self.assertTrue(any(row["code"] == "WEB_TARGET_ROUTE_INVALID" for row in held["findings"]))

    def test_atlas_only_exact_ref_cannot_replace_canonical_record(self):
        entry = {"atlas_index": [{
            "matrix_id": MOTION, "rung": "R1",
            "microtopic_ref": "MIC-EXISTS", "capability_ref": "CAP-EXISTS",
            "representation_refs": ["REP-ATLAS-ONLY"],
        }]}
        resolved, _, findings = web_resolver._target_resolution(
            request("Physics", {"exact_ref": "REP-ATLAS-ONLY"}, "EXPLORE"),
            entry, {},
        )
        self.assertIsNone(resolved["canonical_collection"])
        self.assertIn("WEB_CANONICAL_REF_INVALID", {row["code"] for row in findings})

    def test_offline_explore_uses_static_fallback_instead_of_remote_locator(self):
        plan = {
            "build_action": "EXPLORE_PAGE_ADAPTER",
            "request_satisfaction": "DEGRADED_ACCEPTABLE",
            "subject": "Physics", "request_id": "TEST-OFFLINE",
            "packaging_mode": "OFFLINE_DIRECTORY",
            "experience_segments": [{"mode": "EXPLORE", "interaction_requirement": "OPTIONAL"}],
            "target": {"resolved_refs": {
                "representation_refs": ["REP-TEST"], "activity_refs": ["ACT-TEST"],
            }},
        }
        representation = {"id": "REP-TEST", "_collection": "representations", "purpose": "Observe a model."}
        web = {"subjects": {"Physics": {"visual_targets": {
            "ACT-TEST": {
                "resource_ref": "ACT-TEST", "locator": "https://example.org/remote",
                "availability": {"portable_package": "UNAVAILABLE", "locator": "READY"},
            },
        }}}}
        profile = {
            "ref": "XP-TEST@1.0.0", "shell_ref": "G9-TABLET-SHELL-V1",
            "representation_policy": {"legacy_iframe": "MIGRATION_ONLY"},
            "packaging_modes": ["OFFLINE_DIRECTORY", "SINGLE_FILE"],
        }
        with (
            patch.object(build_explore_page, "_records", return_value={"REP-TEST": representation}),
            patch.object(build_explore_page, "_profile", return_value=profile),
            patch.object(build_explore_page.build_web_data, "build", return_value=web),
            patch.object(build_explore_page.build_portable_workbench, "packages", return_value=[]),
        ):
            package = build_explore_page.compile_page_package(plan)
        self.assertEqual(package["mount_mode"], "STATIC_FIGURE")
        html = build_explore_page.render_directory(package, "OFFLINE_DIRECTORY")["index.html"].decode()
        self.assertNotIn("<iframe", html)
        self.assertNotIn("https://example.org/remote", html)

        plan["experience_segments"][0]["interaction_requirement"] = "REQUIRED"
        with (
            patch.object(build_explore_page, "_records", return_value={"REP-TEST": representation}),
            patch.object(build_explore_page, "_profile", return_value=profile),
            patch.object(build_explore_page.build_web_data, "build", return_value=web),
            patch.object(build_explore_page.build_portable_workbench, "packages", return_value=[]),
        ):
            with self.assertRaisesRegex(
                build_explore_page.ExplorePageBuildError, "EXPLORE_REQUIRED_INTERACTION_UNAVAILABLE",
            ):
                build_explore_page.compile_page_package(plan)

    def test_static_single_file_explore_renders_declared_shell(self):
        package = {
            "mount_mode": "STATIC_FIGURE",
            "profile": {"ref": "XP-TEST@1.0.0", "shell_ref": "G9-TABLET-SHELL-V1"},
            "representation": {"purpose": "Read a canonical model.", "required_elements": ["axis"]},
        }
        html = build_explore_page.render_single_file(package).decode()
        self.assertIn('data-shell-ref="G9-TABLET-SHELL-V1"', html)
        self.assertIn("Read a canonical model.", html)


class WebValidatorTests(unittest.TestCase):
    def test_validator_re_reads_authority_and_rejects_tampered_receipt(self):
        req = request(
            "Physics", {"matrix_ref": MOTION, "rung": "R1"},
            "EXPLORE", interaction="REQUIRED",
        )
        plan = web_resolver.resolve(req)
        good = web_validator.validate(req, plan)
        self.assertTrue(good["passed"])
        self.assertTrue(good["release_ready"])

        tampered = dict(plan)
        tampered["request_satisfaction"] = "DEGRADED_ACCEPTABLE"
        bad = web_validator.validate(req, tampered)
        self.assertFalse(bad["passed"])
        self.assertTrue(any(
            row["code"] == "WEB_RESOLUTION_STALE_OR_DIVERGENT"
            for row in bad["findings"]
        ))

    def test_persisting_core_does_not_invalidate_the_same_semantic_plan(self):
        req = request("Physics", {"matrix_ref": MOTION, "rung": "R1"}, "LEARN", core="CORE1")
        plan = web_resolver.resolve(req)
        fresh = copy.deepcopy(plan)
        fresh["experience_segments"][0]["remembered_artifact_ref"] = "ART-NEW"
        fresh["experience_segments"][0]["remembered_reuse"] = "DIRECT"
        with patch.object(web_validator.web_resolver, "resolve", return_value=fresh):
            report = web_validator.validate(req, plan)
        self.assertTrue(report["passed"], report["findings"])


class DerivedArtifactRegistryTests(unittest.TestCase):
    def test_current_core_projections_are_searchable_by_exact_semantic_refs(self):
        rows, _ = derived_artifact_registry.current_entries()
        self.assertTrue(rows)
        emitted = {row["core"] for row in rows}
        self.assertTrue({"CORE1","CORE1A","CORE1B","CORE2A","CORE2B"}.issubset(emitted))
        self.assertTrue(emitted.issubset({"CORE1","CORE1A","CORE1B","CORE2","CORE2A","CORE2B"}))
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            row = next(
                row for row in rows
                if row["subject"] == "Physics" and row["core"] == "CORE2A"
                and FAMILIAR in row["question_refs"]
            )
            root = repo / "publication/derived-artifacts"
            root.mkdir(parents=True)
            with patch.object(derived_artifact_registry, "current_entries", return_value=([row], {})):
                self.assertEqual(derived_artifact_registry.search(
                    subject="Physics", core="CORE2A", exact_ref=FAMILIAR, repo=repo,
                ), [])
                index = {"contract_version": "1.0.0", "artifacts": [{
                    key: value for key, value in row.items() if key != "_payload"
                }]}
                (root / "derived-artifact-index.v1.json").write_text(json.dumps(index))
                missing = derived_artifact_registry.search(
                    subject="Physics", core="CORE2A", exact_ref=FAMILIAR, repo=repo,
                )
                self.assertEqual(missing[0]["reuse"], "FORBIDDEN")
                stored = root / row["payload_path"]
                stored.parent.mkdir(parents=True)
                stored.write_text(json.dumps(row["_payload"]))
                direct = derived_artifact_registry.search(
                    subject="Physics", core="CORE2A", exact_ref=FAMILIAR, repo=repo,
                )
                self.assertEqual(direct[0]["reuse"], "DIRECT")
                stored.write_text(json.dumps({"tampered": True}))
                invalid = derived_artifact_registry.search(
                    subject="Physics", core="CORE2A", exact_ref=FAMILIAR, repo=repo,
                )
                self.assertEqual(invalid[0]["reuse"], "FORBIDDEN")

    def test_run_bundle_webpage_is_persisted_searchable_and_basis_checked(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            canonical_record = {"id": "Q-TEST", "_collection": "questions", "stem": "Original question"}
            canonical = {
                "subject": "Physics", "authority": "CANONICAL_SLICE_FOR_REPRODUCTION_ONLY",
                "records": {"Q-TEST": canonical_record},
            }
            plan = {
                "request_id": "RUN-TEST", "subject": "Physics",
                "request_satisfaction": "FULL", "experience_segments": [],
                "pins": {"core_provider_contract_version": "1.1"},
                "target": {"exact_ref": "Q-TEST", "matrix_ref": None, "rung": None,
                           "resolved_refs": {"question_refs": ["Q-TEST"]}},
            }
            files = {
                "canonical/canonical-slice.json": (json.dumps(canonical) + "\n").encode(),
                "resolution/web-resolution-plan.json": (json.dumps(plan) + "\n").encode(),
                "outputs/index.html": b"<html><body>Question</body></html>\n",
                "manifest.json": b'{"request_id":"RUN-TEST"}\n',
            }
            with patch.object(derived_artifact_registry, "current_entries", return_value=([], {})):
                derived_artifact_registry.write(repo)
                registered = derived_artifact_registry.register_run_bundle(
                    files=files, plan=plan, release_ready=True, repo=repo,
                )
                self.assertEqual(len(registered), len(files))
                with patch.object(derived_artifact_registry, "_subject_records",
                                  return_value={"Q-TEST": canonical_record}):
                    found = derived_artifact_registry.search(
                        subject="Physics", artifact_type="WEBPAGE",
                        exact_ref="Q-TEST", repo=repo,
                    )
                self.assertEqual(len(found), 1)
                self.assertEqual(found[0]["reuse"], "DIRECT")
                changed = {**canonical_record, "stem": "Revised canonical question"}
                with patch.object(derived_artifact_registry, "_subject_records",
                                  return_value={"Q-TEST": changed}):
                    stale = derived_artifact_registry.search(
                        subject="Physics", artifact_type="WEBPAGE",
                        exact_ref="Q-TEST", repo=repo,
                    )
                self.assertEqual(stale[0]["reuse"], "REGENERATE")
                generator = repo / "Shared/tools/web_resolver.py"
                generator.parent.mkdir(parents=True)
                generator.write_text("# updated delivery contract\n")
                with patch.object(derived_artifact_registry, "_subject_records",
                                  return_value={"Q-TEST": canonical_record}):
                    incompatible = derived_artifact_registry.search(
                        subject="Physics", artifact_type="WEBPAGE",
                        exact_ref="Q-TEST", repo=repo,
                    )
                self.assertEqual(incompatible[0]["reuse"], "REGENERATE")
                held_plan = {**plan, "request_id": "RUN-HELD"}
                derived_artifact_registry.register_run_bundle(
                    files=files, plan=held_plan, release_ready=False, repo=repo,
                )
                with patch.object(derived_artifact_registry, "_subject_records",
                                  return_value={"Q-TEST": canonical_record}):
                    held = derived_artifact_registry.search(
                        subject="Physics", artifact_type="WEBPAGE",
                        exact_ref="Q-TEST", repo=repo,
                    )
                self.assertEqual(next(row for row in held if row["semantic_id"].startswith("RUN-HELD"))["reuse"], "FORBIDDEN")
                stored = repo / "publication/derived-artifacts" / found[0]["payload_path"]
                stored.write_bytes(b"<html>Tampered</html>")
                with patch.object(derived_artifact_registry, "_subject_records",
                                  return_value={"Q-TEST": canonical_record}):
                    self.assertEqual(derived_artifact_registry.search(
                        artifact_type="WEBPAGE", exact_ref="Q-TEST", repo=repo,
                    )[0]["reuse"], "FORBIDDEN")


if __name__ == "__main__":
    unittest.main()
