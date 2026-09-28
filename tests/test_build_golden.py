"""Candidate exemplars remain runnable through the only learner renderer."""
from __future__ import annotations

import unittest
import importlib.util
import json

from Shared.tools import build_golden, render_core


class GoldenRenderTests(unittest.TestCase):
    def test_each_candidate_renders_without_gaps(self):
        manifests = build_golden.candidates()
        self.assertEqual({p.parent.name for p in manifests},
                         {"G-MATH-LINEAR-CONSTRAINT", "G-CORE2-R2"})
        for manifest in manifests:
            with self.subTest(golden=manifest.parent.name):
                result = build_golden.build_one(manifest, check=True)
                self.assertEqual(result["pages"], 7)
                self.assertEqual(result["gaps"], 0)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "jsonschema unavailable")
    def test_candidate_record_excerpts_follow_package_schema(self):
        import jsonschema  # noqa: PLC0415

        schema = json.loads((build_golden.REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))
        for manifest in build_golden.candidates():
            with self.subTest(golden=manifest.parent.name):
                records = json.loads((manifest.parent / "records.json").read_text(encoding="utf-8"))
                jsonschema.validate(records, schema)

    def test_core2_candidate_keeps_source_options_and_later_hints_inert(self):
        manifest = build_golden.GOLDEN / "G-CORE2-R2" / "manifest.json"
        pages, gaps, _ = render_core.build(manifest)
        self.assertFalse(gaps)
        page = pages["core2.html"]
        self.assertIn('data-g9-response-type="single_choice"', page)
        self.assertEqual(page.count('data-g9-choice type="radio"'), 4)
        self.assertEqual(page.count('<template data-g9-rung-payload='), 2)
        self.assertIn('<template data-g9-payload="CORE2-PYQ-PHY-IITJEE-2007-P1-Q03-solution">', page)
