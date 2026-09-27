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

    def test_source_option_labels_are_printed_once(self):
        html = self.pages[render_core.ROLE_FILE["CORE2"]]
        self.assertIsNone(re.search(r"\([a-d]\) \([A-D1-4]\)", html))

    def test_authored_svg_asset_is_mounted_with_its_stages(self):
        m = json.loads(manifest_file(self.tmp).read_text(encoding="utf-8"))
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        svg = self.tmp / "rep.svg"
        svg.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10" role="img" aria-labelledby="t d">'
                       '<title id="t">t</title><desc id="d">Accessible teaching figure.</desc>'
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


    def test_renderer_owns_tablet_asset_and_blueprint_digest(self):
        ctx = render_core.context(manifest_file(self.tmp))
        digest_before = render_core.render_digest(ctx)
        html = render_core.page(ctx, "CORE1", "PAGES", digest_before)
        self.assertIn('../../css/tablet-12-7.css', html)
        self.assertNotIn('cdn.jsdelivr.net', html)
        self.assertNotIn('vendor/katex/', html)

        labels = [label for label, _digest in ctx.authority_hashes]
        self.assertIn("blueprints", labels)
        self.assertTrue(any(label.startswith("bank:") for label in labels))

        changed = copy.deepcopy(ctx)
        changed.authority_hashes = list(ctx.authority_hashes)
        label, old_hash = changed.authority_hashes[-2]
        changed.authority_hashes[-2] = (label, ("0" if old_hash[0] != "0" else "1") + old_hash[1:])
        self.assertNotEqual(digest_before, render_core.render_digest(changed))

        changed_bank = copy.deepcopy(ctx)
        changed_bank.authority_hashes = list(ctx.authority_hashes)
        bank_index = next(i for i, (label, _digest) in enumerate(changed_bank.authority_hashes) if label.startswith("bank:"))
        label, old_hash = changed_bank.authority_hashes[bank_index]
        changed_bank.authority_hashes[bank_index] = (label, ("0" if old_hash[0] != "0" else "1") + old_hash[1:])
        self.assertNotEqual(digest_before, render_core.render_digest(changed_bank))


    def test_repeated_svg_instances_are_id_scoped_with_local_aria_references(self):
        source = (
            '<svg xmlns="http://www.w3.org/2000/svg" aria-labelledby="t d">'
            '<title id="t">Title</title><desc id="d">Desc</desc>'
            '<defs><marker id="arrow"></marker></defs>'
            '<path id="p" marker-end="url(#arrow)"></path></svg>'
        )
        a = render_core._scope_svg_ids(source, "scope-a")
        b = render_core._scope_svg_ids(source, "scope-b")
        self.assertNotEqual(set(re.findall(r'(?<![-:\w])id="([^"]+)"', a)), set(re.findall(r'(?<![-:\w])id="([^"]+)"', b)))
        self.assertIn('aria-labelledby="scope-a--t scope-a--d"', a)
        self.assertIn('url(#scope-a--arrow)', a)
        self.assertNotIn('id="t"', a)

    def test_authored_svg_without_accessible_name_and_description_is_a_typed_gap(self):
        m = json.loads(manifest_file(self.tmp).read_text(encoding="utf-8"))
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        svg = self.tmp / "rep-inaccessible.svg"
        svg.write_text(
            '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 10 10">'
            '<g data-g9-stage-id="S1"></g><g data-g9-stage-id="S2"></g></svg>',
            encoding="utf-8",
        )
        rep = next(r for r in pkg["representations"] if r["id"] == "REP-KIN-2D-SHARED-CLOCK")
        rep["rendered_asset_refs"] = ["rep-inaccessible.svg"]
        original = render_core.asset_svg
        render_core.asset_svg = lambda ref: svg.read_text(encoding="utf-8")
        try:
            path = self.tmp / "m-accessible.json"
            m["package_refs"] = [str(self.tmp / "pkg-accessible.json")]
            (self.tmp / "pkg-accessible.json").write_text(json.dumps(pkg), encoding="utf-8")
            path.write_text(json.dumps(m), encoding="utf-8")
            ctx = render_core.context(path)
            ctx.packages = [pkg]
            html = render_core.page(ctx, "CORE1A", "PAGES", "d")
        finally:
            render_core.asset_svg = original
        self.assertNotIn('data-g9-representation="REP-KIN-2D-SHARED-CLOCK"', html)
        self.assertTrue(any(g["duty"] == "BUILD_SCENE" and "accessible name" in g["detail"] for g in ctx.gaps))


    def test_relation_mathml_is_rendered_only_from_the_restricted_schema_field(self):
        ctx = render_core.context(manifest_file(self.tmp))
        relation = ctx.packages[0]["relations"][0]
        relation["mathml"] = (
            '<math xmlns="http://www.w3.org/1998/Math/MathML" display="block">'
            '<mrow><mi>x</mi><mo>=</mo><mn>1</mn></mrow></math>'
        )
        out = render_core._relation_expression(ctx, relation, "M")
        self.assertIn('data-g9-math="mathml"', out)
        self.assertIn("<math", out)
        self.assertNotIn("&lt;math", out)

    def test_unsafe_relation_mathml_fails_to_plain_expression_and_records_gap(self):
        ctx = render_core.context(manifest_file(self.tmp))
        relation = ctx.packages[0]["relations"][0]
        relation["mathml"] = (
            '<math xmlns="http://www.w3.org/1998/Math/MathML">'
            '<script>alert(1)</script></math>'
        )
        out = render_core._relation_expression(ctx, relation, "M")
        self.assertIn("g9-expr", out)
        self.assertTrue(any(g["duty"] == "AUTHOR_GOVERNING_RELATION" and g["record"] == relation["id"]
                            for g in ctx.gaps))


    def test_single_file_inlines_tablet_shell_and_uses_role_anchors(self):
        pages, gaps, digest = render_core.build(manifest_file(self.tmp), mode="SINGLE_FILE")
        self.assertTrue(gaps)
        self.assertEqual(set(pages), {"product.html"})
        html = pages["product.html"]
        self.assertIn('data-g9-mode="SINGLE_FILE"', html)
        self.assertIn('data-g9-tablet-shell', html)
        self.assertNotIn('href="../../css/tablet-12-7.css"', html)
        for role in render_core.ROLES:
            self.assertIn(f'id="g9-role-{role}"', html)
            self.assertIn(f'href="#g9-role-{role}"', html)
        self.assertNotIn('href="core2a.html"', html)
        self.assertIn('href="../../../public/index.html"', html)
        self.assertIn('href="../../../public/question-bank/index.html"', html)
        ids = re.findall(r'(?<![-:\w])id="([^"]+)"', html)
        self.assertEqual(len(ids), len(set(ids)), "SINGLE_FILE output must not duplicate document ids")
        self.assertNotRegex(html, r'href="core\w+\.html#')

    def test_render_receipt_manifest_path_is_repository_relative(self):
        out = self.tmp / "receipt"
        path = manifest_file(self.tmp)
        # Temp manifests cannot be repo-relative, but repository manifests must be.
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        if repo_manifest.is_file():
            rc = render_core.main(["build", "--manifest", str(repo_manifest), "--out", str(out), "--draft"])
            self.assertEqual(rc, 0)
            receipt = json.loads((out / "render-receipt.json").read_text(encoding="utf-8"))
            self.assertEqual(receipt["manifest"], "products/physics/phy-kin-2d-motion.manifest.json")


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


class PromotionBatch(unittest.TestCase):
    """A prerequisite taught by a sibling node counts only when the sibling is promoted in the same batch."""

    def run_plan(self, verified):
        def node(n, cap, pre):
            ext = {"grade9v3:research_node": n}
            return [{"id": f"MIC-{n}", "primary_capability_ref": cap, "prerequisite_refs": pre, "extensions": ext},
                    {"id": cap, "extensions": ext}]
        mics_a, caps_a = node("A", "CAP-A", [])
        mics_b, caps_b = node("B", "CAP-B", ["CAP-A"])
        staging = {"C": {"schema_version": "0.2.0", "microtopics": [mics_a, mics_b], "capabilities": [caps_a, caps_b]}}
        board = {"subject": "Mathematics", "nodes": [
            {"node": n, "chapter": "C", "level": "MICROTOPIC", "stage": "VERIFIED" if n in verified else "VERIFIER",
             "duties": [], "verification": f"{n}.json"} for n in ("A", "B")]}
        original = package_depth.package_duties
        package_depth.package_duties = lambda pkg, rel, taught, limit: [
            {"duty": "TEACH_PREREQUISITE_BRIDGE"} for m in pkg.get("microtopics", [])
            for r in m.get("prerequisite_refs", []) if r not in taught]
        try:
            return promote_verified.plan(board, staging, set(), 4)
        finally:
            package_depth.package_duties = original

    def test_a_verified_sibling_unblocks_its_dependent(self):
        self.assertEqual(sorted(i["node"] for i in self.run_plan({"A", "B"})["promotable"]), ["A", "B"])

    def test_an_unpromoted_sibling_does_not(self):
        res = self.run_plan({"B"})
        self.assertEqual(res["promotable"], [])
        self.assertIn("depth duties", {r["reason"] for r in res["refused"]})

if __name__ == "__main__":
    unittest.main()