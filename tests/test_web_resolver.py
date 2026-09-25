from __future__ import annotations

import unittest

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
        self.assertEqual(segment["remembered_reuse"], "DIRECT")

    def test_core2a_exact_question_uses_provider_and_saved_artifact(self):
        plan = web_resolver.resolve(request(
            "Physics", {"exact_ref": FAMILIAR},
            "PRACTICE", core="CORE2A",
        ))
        self.assertEqual(plan["request_satisfaction"], "FULL")
        segment = plan["experience_segments"][0]
        self.assertEqual(segment["provider_status"], "READY_EXISTING")
        self.assertEqual(segment["remembered_reuse"], "DIRECT")
        self.assertEqual(plan["target"]["resolved_refs"]["question_refs"], [FAMILIAR])

    def test_target_preparation_requires_286_receipt_and_independent_authorization(self):
        req = request(
            "Physics", {"exact_ref": FAMILIAR},
            "PRACTICE", core="CORE2A", preparation=True,
        )
        missing = web_resolver.resolve(req)
        self.assertEqual(missing["request_satisfaction"], "HOLD")
        self.assertTrue(any(row["code"] == "WEB_TARGET_ROUTE_REQUIRED" for row in missing["findings"]))

        route = {
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
        resolved = web_resolver.resolve(req, route_artifact=route)
        self.assertNotEqual(resolved["request_satisfaction"], "HOLD")
        self.assertEqual(resolved["target_route"]["contract_version"], "1.1.0")


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


class DerivedArtifactRegistryTests(unittest.TestCase):
    def test_current_core_projections_are_searchable_by_exact_semantic_refs(self):
        rows, _ = derived_artifact_registry.current_entries()
        self.assertTrue(rows)
        emitted = {row["core"] for row in rows}
        self.assertTrue({"CORE1","CORE1A","CORE1B","CORE2A","CORE2B"}.issubset(emitted))
        self.assertTrue(emitted.issubset({"CORE1","CORE1A","CORE1B","CORE2","CORE2A","CORE2B"}))
        results = derived_artifact_registry.search(
            subject="Physics", core="CORE2A", exact_ref=FAMILIAR,
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["freshness"], "CURRENT")
        self.assertEqual(results[0]["reuse"], "DIRECT")


if __name__ == "__main__":
    unittest.main()
