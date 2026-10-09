"""Fail-closed Core public-data and GitHub Pages mirror regressions.

Tests use authentic generator outputs and a temporary deployment root; no
curriculum/Owner approval or artifact publication is inferred from a PASS.
"""
from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from Shared.tools import build_core_learning_data, build_pages_site


class CorePublicDataBoundaryTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.repo = Path(self.temp.name)
        self.public = self.repo / "public/core-learning"
        self.public.mkdir(parents=True)
        (self.public / "index.html").write_text(
            "<!doctype html><title>Core learner</title>\n", encoding="utf-8"
        )
        self.expected = build_core_learning_data.rendered_file()[
            "public/core-learning/data.js"
        ]
        (self.public / "data.js").write_bytes(self.expected)

    def test_pages_admits_only_canonical_release_hold_bytes(self):
        # The normal mirror generator checks the source before copying anything.
        build_pages_site._assert_core_public_data_safe(self.repo)
        # Exercise the actual Pages generation path, not merely the helper.
        with patch.dict(build_pages_site.EXTRA_SOURCES, {}, clear=True):
            generated = build_pages_site.desired_files(self.repo)
        self.assertEqual(
            generated["core-learning/data.js"],
            ("public/core-learning/data.js", self.expected),
        )

    def test_pages_rejects_internal_preview_payload_even_if_valid_javascript(self):
        # A preview serializer must never become a Pages mirror input.
        internal = (
            '// internal compiler preview only\n'
            'window.GRADE9V3_CORE = {"core_projections":'
            '[{"id":"TEST-PREVIEW","subject":"TEST"}]};\n'
        )
        (self.public / "data.js").write_text(internal, encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD_PUBLIC_SOURCE_MISMATCH"):
            build_pages_site._assert_core_public_data_safe(self.repo)
        with patch.dict(build_pages_site.EXTRA_SOURCES, {}, clear=True):
            with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD_PUBLIC_SOURCE_MISMATCH"):
                build_pages_site.desired_files(self.repo)

    def test_pages_rejects_corrupt_and_missing_public_payload(self):
        path = self.public / "data.js"
        path.write_bytes(self.expected + b"/* forged approval */")
        with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD_PUBLIC_SOURCE_MISMATCH"):
            build_pages_site._assert_core_public_data_safe(self.repo)
        path.unlink()
        with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD_SOURCE_MISSING"):
            build_pages_site._assert_core_public_data_safe(self.repo)

    def test_pages_rejects_orphan_core_data_without_host(self):
        (self.public / "index.html").unlink()
        with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD_SOURCE_MISSING"):
            build_pages_site._assert_core_public_data_safe(self.repo)

    def test_no_core_site_is_permitted_in_unrelated_partial_mirror_fixture(self):
        (self.public / "index.html").unlink()
        (self.public / "data.js").unlink()
        build_pages_site._assert_core_public_data_safe(self.repo)

    def test_public_hold_is_committed_before_internal_preview_compilation_fails(self):
        data_path = self.public / "data.js"
        data_path.write_bytes(
            b'window.GRADE9V3_CORE = {"core_projections":'
            b'[{"subject":"TEST","id":"OLD-UNAPPROVED-PREVIEW"}]};\\n'
        )
        self.assertNotEqual(data_path.read_bytes(), self.expected)
        # A preview compiler crash must not leave stale public preview bytes
        # intact. The public envelope is emitted first, then the build fails.
        with patch.object(build_core_learning_data, "OUT", data_path):
            with patch.object(
                build_core_learning_data,
                "build",
                side_effect=RuntimeError("INJECTED_INTERNAL_PREVIEW_FAILURE"),
            ):
                with self.assertRaisesRegex(RuntimeError, "INJECTED_INTERNAL_PREVIEW_FAILURE"):
                    build_core_learning_data.write()
        self.assertEqual(data_path.read_bytes(), self.expected)

    def test_distributable_renderer_cannot_serialize_internal_previews(self):
        public = build_core_learning_data.build_public()
        mutated = dict(public)
        mutated["core_projections"] = [{"subject": "Physics", "id": "NO-GRANT"}]
        with self.assertRaisesRegex(ValueError, "CORE_PUBLICATION_HOLD"):
            build_core_learning_data.render(mutated)
        # The deployment output generator must remain independent of build().
        with patch.object(
            build_core_learning_data, "build", side_effect=AssertionError("preview build invoked")
        ):
            self.assertEqual(
                build_core_learning_data.rendered_file()[
                    "public/core-learning/data.js"
                ],
                self.expected,
            )


if __name__ == "__main__":
    unittest.main()
