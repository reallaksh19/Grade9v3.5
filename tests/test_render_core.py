"""Phase 3: one renderer, selection-only manifests, verified-only promotion."""
from __future__ import annotations

import copy
import json
import re
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import package_depth, package_migrate, product_manifest, promote_verified, render_core  # noqa: E402

# Frozen pre-pilot Motion in a Plane: the tests need a product that still has gaps.
PKG = "tests/fixtures/render/thin-kin-2d-motion.v1.json"
BANK = "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"


def manifest_file(tmp: Path, **overrides) -> Path:
    m = product_manifest.derive(PKG, [BANK], "PRODUCT-TEST", "Motion in a Plane", "../../index.html")
    m.update(overrides)
    path = tmp / "m.json"
    path.write_text(json.dumps(m), encoding="utf-8")
    return path


class Renderer(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.pages, self.gaps, self.digest = render_core.build(manifest_file(self.tmp))

    def test_every_role_renders_through_its_blueprint_slots_in_the_shell(self):
        blueprints = json.loads(render_core.BLUEPRINTS.read_text(encoding="utf-8"))
        for role in render_core.ROLES:
            html = self.pages[render_core.ROLE_FILE[role]]
            bp = next(b for b in blueprints["blueprints"] if role in b["core_roles"])
            with self.subTest(role=role):
                self.assertIn("data-g9-shell", html)
                self.assertIn("data-g9-shell-header", html)
                self.assertIn('data-g9-home href="../../index.html"', html)
                self.assertIn(f"{render_core.RENDERER_VERSION} {self.digest}", html)
                slots = re.findall(r'data-blueprint-slot="([^"]+)"', html)
                allowed = [s["id"] for s in bp["slots"]]
                self.assertTrue(slots and set(slots) <= set(allowed), (slots, allowed))
                self.assertIn("@media print", html)

    def test_reveals_are_gated_and_no_record_id_or_placeholder_reaches_the_learner(self):
        for name, html in self.pages.items():
            with self.subTest(page=name):
                self.assertNotIn("None supplied", html)
                self.assertIsNone(re.search(r">\s*(FAM|K2D)[A-Z0-9-]+\s*<", html))
                for details in re.findall(r"<details[^>]*>", html):
                    self.assertIn("data-requires-attempt", details)

    def test_missing_inputs_are_typed_gaps_that_the_board_knows(self):
        kinds = {g["duty"] for g in self.gaps}
        self.assertIn("BUILD_SCENE", kinds)                    # no authored SVG asset yet
        self.assertTrue(kinds <= set(package_depth.DUTIES) | {"AUTHOR_PRACTICE"}, kinds)

    def test_a_product_with_gaps_is_never_written_as_a_publication(self):
        out = self.tmp / "out"
        rc = render_core.main(["build", "--manifest", str(manifest_file(self.tmp)), "--out", str(out)])
        self.assertEqual(rc, 2)
        self.assertFalse(out.exists())
        render_core.main(["build", "--manifest", str(manifest_file(self.tmp)), "--out", str(out), "--draft"])
        self.assertIn("data-g9-draft", (out / "core1.html").read_text(encoding="utf-8"))

    def test_authored_svg_asset_is_mounted_with_its_stages(self):
        m = json.loads(manifest_file(self.tmp).read_text(encoding="utf-8"))
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        svg = self.tmp / "rep.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10"><title>t</title>'
                       '<g data-g9-stage-id="S1"></g><g data-g9-stage-id="S2"></g></svg>', encoding="utf-8")
        rep = next(r for r in pkg["representations"] if r["id"] == "REP-KIN-2D-SHARED-CLOCK")
        rep["rendered_asset_refs"] = [str(svg.relative_to(REPO)) if svg.is_relative_to(REPO) else str(svg)]
        pkg_path = self.tmp / "pkg.json"
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        original = render_core.asset_svg
        render_core.asset_svg = lambda ref: svg.read_text(encoding="utf-8") if ref == rep["rendered_asset_refs"][0] else None
        try:
            m["package_refs"] = [str(pkg_path)]
            path = self.tmp / "m2.json"
            path.write_text(json.dumps(m), encoding="utf-8")
            ctx = render_core.context(path)
            ctx.packages = [pkg]
            html = render_core.page(ctx, "CORE1A", "PAGES", "d")
        finally:
            render_core.asset_svg = original
        self.assertIn('data-g9-representation="REP-KIN-2D-SHARED-CLOCK"', html)
        self.assertIn('data-g9-stages="S1 S2"', html)
        self.assertNotIn("REP-KIN-2D-SHARED-CLOCK", [g["record"] for g in ctx.gaps if g["duty"] == "BUILD_SCENE"])


class Manifest(unittest.TestCase):
    def test_manifest_holds_selection_only(self):
        m = product_manifest.derive(PKG, [BANK], "P", "T", "../index.html")
        self.assertEqual(set(m["selection"]), {"microtopics", "core2", "core2a", "core2b"})
        text = json.dumps(m)
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        self.assertNotIn(pkg["microtopics"][0]["inferential_jump"], text)


class Promotion(unittest.TestCase):
    def board(self, stage):
        return {"subject": "Physics", "nodes": [{"node": "N1", "chapter": "C", "level": "MICROTOPIC",
                                                 "stage": stage, "duties": [], "verification": "v.json"}]}

    def staging(self, rec_patch=None):
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        q = copy.deepcopy(next(x for x in pkg["questions"] if any(e["core"] == "CORE2A" for e in x["exposure"])))
        q["extensions"] = {"grade9v3:research_node": "N1"}
        if rec_patch:
            rec_patch(q)
        return {"C": {"schema_version": "0.2.0", "questions": [q]}}

    def test_unverified_or_shallow_records_are_refused(self):
        taught, limit = package_depth.taught_capabilities(), package_migrate.max_decisions()
        self.assertEqual(promote_verified.plan(self.board("VERIFIER"), self.staging(), taught, limit)["promotable"], [])
        res = promote_verified.plan(self.board("VERIFIED"), self.staging(), taught, limit)
        self.assertEqual(res["promotable"], [])
        self.assertEqual(res["refused"][0]["reason"], "depth duties")

    def test_verified_deep_records_are_promoted_with_a_stamp(self):
        def deepen(q):
            q["hint_ladder"] = [{"order": i, "purpose": "ORIENT", "provenance": "AUTHORED_HINT", "text": f"rung {i}"} for i in (1, 2, 3)]
            q["representation_roles"] = {"initial_ref": "REP-KIN-2D-SHARED-CLOCK"}
            q["failure_signal"] = "Pairs x(2 s) with y(3 s)."
            q["family_exposure"] = {"family_ref": q["family_ref"], "closure": "Same-time pairing is established."}
        res = promote_verified.plan(self.board("VERIFIED"), self.staging(deepen),
                                    package_depth.taught_capabilities(), package_migrate.max_decisions())
        self.assertEqual([i["node"] for i in res["promotable"]], ["N1"])
        merged = promote_verified.merge(None, {}, "Physics", "C", res["promotable"], "2026-09-26")
        stamp = merged["questions"][0]["extensions"]["grade9v3:promotion"]
        self.assertEqual(stamp["verification"], "v.json")
        self.assertEqual(merged["schema_version"], "0.2.0")


if __name__ == "__main__":
    unittest.main()
