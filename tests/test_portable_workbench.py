from __future__ import annotations

import copy
import json
import unittest
from pathlib import Path

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

    def test_migration_note_keeps_redox_bespoke_page_non_authoritative(self):
        text = (REPO / "docs/portable-workbench.md").read_text(encoding="utf-8")
        self.assertIn("reference prototype", text)
        self.assertIn("NON_CANONICAL_COMPILED_PROOF", text)
        self.assertIn("standalone/chemistry-redox-reactions-master-suite.html", text)


if __name__ == "__main__":
    unittest.main()
