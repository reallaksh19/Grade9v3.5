from __future__ import annotations

import copy
import json
import os
import shutil
import subprocess
import unittest
from pathlib import Path

from Shared.portable.binding import resolve_portable_target
from Shared.portable.package import COMPONENT_API_VERSION, PortablePackageError, validate_package
from Shared.tools import build_portable_workbench

REPO = Path(__file__).resolve().parents[1]


class PortableWorkbenchPackageTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.packages = build_portable_workbench.packages()
        cls.by_id = {row["id"]: row for row in cls.packages}

    def test_three_cross_subject_packages_share_one_contract(self):
        self.assertEqual(set(self.by_id), {
            "portable-long-division",
            "portable-redox-electron-equivalence",
            "portable-integration-riemann",
        })
        versions = {
            (row["packageVersion"], row["componentApiVersion"], row["transformationIrVersion"],
             row["adapterApiVersion"], row["scenePackageVersion"], row["adapter"]["id"])
            for row in self.packages
        }
        self.assertEqual(len(versions), 1)
        self.assertEqual(next(iter(versions))[1], COMPONENT_API_VERSION)

    def test_long_division_reuses_existing_core_witness(self):
        source = json.loads(
            (REPO / "tests/fixtures/workbench/arithmetic-division.json").read_text(encoding="utf-8")
        )
        self.assertEqual(self.by_id["portable-long-division"]["scene"], source)

    def test_packages_are_noncanonical_compiled_proofs(self):
        for package in self.packages:
            self.assertEqual(package["provenance"]["authority"], "NON_CANONICAL_COMPILED_PROOF")
            self.assertNotIn("mastery", json.dumps(package).lower())

    def test_canonical_provenance_requires_explicit_resource_and_representation(self):
        canonical = copy.deepcopy(self.packages[0])
        canonical["resourceRef"] = "ACT-TEST-CANONICAL"
        canonical["representationRefs"] = ["REP-TEST-CANONICAL"]
        canonical["sourceRefs"] = ["SRC-TEST-CANONICAL"]
        canonical["provenance"] = {
            "authority": "CANONICAL_COMPILED_RESOURCE",
            "sourceKind": "CANONICAL_RESOURCE",
            "sourceRefs": ["SRC-TEST-CANONICAL"],
            "resourceRef": "ACT-TEST-CANONICAL",
            "representationRef": "REP-TEST-CANONICAL",
        }
        validated = validate_package(canonical)
        self.assertEqual(validated["resourceRef"], "ACT-TEST-CANONICAL")
        self.assertEqual(validated["provenance"]["authority"], "CANONICAL_COMPILED_RESOURCE")

        missing = copy.deepcopy(canonical)
        del missing["provenance"]["resourceRef"]
        with self.assertRaises(PortablePackageError) as raised:
            validate_package(missing)
        self.assertEqual(raised.exception.code, "PORTABLE_CANONICAL_RESOURCE_REF_REQUIRED")

        mismatched = copy.deepcopy(canonical)
        mismatched["provenance"]["representationRef"] = "REP-OTHER"
        with self.assertRaises(PortablePackageError) as raised:
            validate_package(mismatched)
        self.assertEqual(raised.exception.code, "PORTABLE_CANONICAL_REPRESENTATION_REF_MISMATCH")

    def test_explicit_unknown_package_request_has_named_failure_path(self):
        html = build_portable_workbench.render()["public/portable-workbench/index.html"].decode("utf-8")
        self.assertIn("PORTABLE_PACKAGE_NOT_FOUND", html)
        self.assertNotIn(
            'requested&&catalog.packageIds.includes(requested)?requested:catalog.packageIds[0]',
            html,
        )

    def test_atlas_visual_target_binding_fails_closed_until_package_is_declared(self):
        visual_targets = {
            "ACT-KIN-2D-SHARED-CLOCK": {
                "resource_ref": "ACT-KIN-2D-SHARED-CLOCK",
                "representation_refs": ["REP-KIN-2D-SHARED-CLOCK"],
                "locator": "public/physics/motion-2d/explorers/shared-clock/index.html",
                "delivery_kind": "EXISTING_ACTIVITY",
                "delivery_profile": "REPO_BUNDLE",
                "portable_package_ref": None,
                "availability": {
                    "resource": "READY",
                    "locator": "READY",
                    "portable_package": "UNAVAILABLE",
                    "standalone": "UNAVAILABLE",
                },
            },
        }
        with self.assertRaises(PortablePackageError) as raised:
            resolve_portable_target(
                "ACT-KIN-2D-SHARED-CLOCK", visual_targets, {}
            )
        self.assertEqual(raised.exception.code, "STANDALONE_PACKAGE_UNAVAILABLE")

        with self.assertRaises(PortablePackageError) as raised:
            resolve_portable_target("ACT-NOT-HERE", visual_targets, {})
        self.assertEqual(raised.exception.code, "VISUAL_REF_UNAVAILABLE")

    def test_atlas_visual_target_binding_requires_exact_canonical_identity(self):
        canonical = copy.deepcopy(self.packages[0])
        canonical["id"] = "portable-motion-shared-clock"
        canonical["resourceRef"] = "ACT-KIN-2D-SHARED-CLOCK"
        canonical["representationRefs"] = ["REP-KIN-2D-SHARED-CLOCK"]
        canonical["sourceRefs"] = ["SRC-AUTHOR-KIN-2D-EXAMSIDE-ADAPTATION"]
        canonical["provenance"] = {
            "authority": "CANONICAL_COMPILED_RESOURCE",
            "sourceKind": "CANONICAL_RESOURCE",
            "sourceRefs": ["SRC-AUTHOR-KIN-2D-EXAMSIDE-ADAPTATION"],
            "resourceRef": "ACT-KIN-2D-SHARED-CLOCK",
            "representationRef": "REP-KIN-2D-SHARED-CLOCK",
        }
        target = {
            "resource_ref": "ACT-KIN-2D-SHARED-CLOCK",
            "representation_refs": ["REP-KIN-2D-SHARED-CLOCK"],
            "locator": "public/physics/motion-2d/explorers/shared-clock/index.html",
            "delivery_kind": "PORTABLE_PACKAGE",
            "delivery_profile": "SINGLE_FILE_OFFLINE",
            "portable_package_ref": "portable-motion-shared-clock",
            "availability": {
                "resource": "READY",
                "locator": "READY",
                "portable_package": "READY",
                "standalone": "READY",
            },
        }
        binding = resolve_portable_target(
            "ACT-KIN-2D-SHARED-CLOCK",
            {"ACT-KIN-2D-SHARED-CLOCK": target},
            {"portable-motion-shared-clock": canonical},
        )
        self.assertEqual(binding["portable_package_ref"], "portable-motion-shared-clock")
        self.assertEqual(binding["representation_ref"], "REP-KIN-2D-SHARED-CLOCK")

        mismatched = copy.deepcopy(canonical)
        mismatched["resourceRef"] = "ACT-OTHER"
        mismatched["provenance"]["resourceRef"] = "ACT-OTHER"
        with self.assertRaises(PortablePackageError) as raised:
            resolve_portable_target(
                "ACT-KIN-2D-SHARED-CLOCK",
                {"ACT-KIN-2D-SHARED-CLOCK": target},
                {"portable-motion-shared-clock": mismatched},
            )
        self.assertEqual(raised.exception.code, "PORTABLE_RESOURCE_BINDING_MISMATCH")

    def test_version_mismatch_fails_closed(self):
        broken = copy.deepcopy(self.packages[0])
        broken["componentApiVersion"] = "999.0.0"
        with self.assertRaises(PortablePackageError) as raised:
            validate_package(broken)
        self.assertEqual(raised.exception.code, "PORTABLE_COMPONENTAPIVERSION_MISMATCH")

    def test_executable_and_pixel_payloads_fail_closed(self):
        executable = copy.deepcopy(self.packages[0])
        executable["script"] = "alert(1)"
        with self.assertRaises(PortablePackageError) as raised:
            validate_package(executable)
        self.assertEqual(raised.exception.code, "PORTABLE_EXECUTABLE_FIELD_FORBIDDEN")
        pixel = copy.deepcopy(self.packages[0])
        pixel["scene"]["projections"][0]["placement"]["x"] = 20
        with self.assertRaises(PortablePackageError) as raised:
            validate_package(pixel)
        self.assertEqual(raised.exception.code, "PORTABLE_PIXEL_COORDINATE_FORBIDDEN")

    def test_generated_outputs_are_current(self):
        for relative, expected in build_portable_workbench.render().items():
            with self.subTest(path=relative):
                self.assertEqual((REPO / relative).read_bytes(), expected)

    def test_public_runtime_is_generated_from_delivered_core(self):
        self.assertEqual(
            (REPO / "public/portable-workbench/runtime.mjs").read_bytes(),
            (REPO / "Shared/workbench/runtime.mjs").read_bytes(),
        )
        self.assertEqual(
            (REPO / "public/portable-workbench/semantic-workbench.mjs").read_bytes(),
            (REPO / "Shared/workbench/semantic-workbench.mjs").read_bytes(),
        )

    def test_single_file_host_has_no_external_runtime_dependency(self):
        html = (REPO / "standalone/portable-workbench/index.html").read_text(encoding="utf-8")
        lowered = html.lower()
        self.assertNotIn(' src="', lowered)
        self.assertNotIn("https://", lowered)
        self.assertNotIn("http://", lowered)
        self.assertNotIn("fetch(", html)
        self.assertIn("PORTABLE_PACKAGES", html)

    def test_node_portable_contract(self):
        node = shutil.which("node")
        self.assertIsNotNone(node, "Node is required by the portable workbench contract tests")
        if os.environ.get("GITHUB_ACTIONS") == "true":
            self.assertIsNotNone(shutil.which("chromedriver"), "GitHub Actions portability proof requires ChromeDriver")
        result = subprocess.run(
            [node, "--test", str(REPO / "tests/portable_workbench.test.mjs")],
            cwd=REPO,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_migration_note_keeps_redox_bespoke_page_non_authoritative(self):
        text = (REPO / "docs/portable-workbench.md").read_text(encoding="utf-8")
        self.assertIn("reference prototype", text)
        self.assertIn("NON_CANONICAL_COMPILED_PROOF", text)
        self.assertIn("standalone/chemistry-redox-reactions-master-suite.html", text)


if __name__ == "__main__":
    unittest.main()
