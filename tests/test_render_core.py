"""One renderer, selection-only manifests, and the preserved M3 migration."""
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

from Shared.tools import migrate_math_linear, package_depth, product_manifest, promote_verified, render_core  # noqa: E402

# Frozen pre-pilot Motion in a Plane: the tests need a product that still has gaps.
PKG = "tests/fixtures/render/thin-kin-2d-motion.v1.json"
BANK = "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"


def manifest_file(tmp: Path, **overrides) -> Path:
    m = product_manifest.derive(PKG, [BANK], "PRODUCT-TEST", "../../index.html")
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


    def test_core1a_bucket_orientation_uses_canonical_bucket_and_selected_route(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        bucket = ctx.packages[0]["buckets"][0]

        self.assertIn("data-g9-bucket-orientation", html)
        self.assertIn(f'data-g9-bucket-ref="{bucket["id"]}"', html)
        self.assertIn(bucket["scope"]["covers"], html)
        for convention in bucket["conventions"]:
            self.assertIn(convention["statement"], html)

        concept_positions = [
            html.index(f'href="#{microtopic["id"]}"')
            for microtopic in ctx.selection_rows["microtopics"]
        ]
        self.assertEqual(concept_positions, sorted(concept_positions))
        self.assertNotIn("Trajectory-equation derivation as a first-slice requirement.", html)

    def test_core1a_construction_units_are_stable_deep_links_with_global_previous_next(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        route = render_core._core1a_route(ctx)

        self.assertGreater(len(route), 3)
        for row in route:
            self.assertIn(f'id="{row["unit_id"]}"', html)
            self.assertIn(f'href="#{row["unit_id"]}"', html)
        self.assertIn(f"Section 1 of {len(route)}", html)
        self.assertIn(f"Section {len(route)} of {len(route)}", html)
        self.assertEqual(html.count("data-g9-prev-section"), len(route) - 1)
        self.assertEqual(html.count("data-g9-next-section"), len(route) - 1)
        self.assertNotIn("data-g9-mastery", html)

    def test_core1a_relation_matrix_preserves_equation_meaning_and_validity_semantics(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))

        selected_relations = {
            ref
            for microtopic in ctx.selection_rows["microtopics"]
            for ref in microtopic.get("relation_refs", [])
        }
        self.assertIn("data-g9-equation-matrix", html)
        self.assertIn("<th scope=\"col\">Equation</th>", html)
        self.assertIn("<th scope=\"col\">What it tells you</th>", html)
        self.assertIn("<th scope=\"col\">When you can use it</th>", html)
        for relation_ref in selected_relations:
            relation = ctx.index("relations")[relation_ref]
            self.assertIn(f'data-g9-relation-ref="{relation_ref}"', html)
            self.assertIn(relation["meaning"], html)
            for condition in relation.get("conditions", []):
                self.assertIn(condition, html)

    def test_renderer_owns_tablet_asset_and_blueprint_digest(self):
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        pkg["representations"][0]["rendered_asset_refs"] = ["Physics/assets/representations/REP-KIN-2D-SHARED-CLOCK.svg"]
        pkg_path = self.tmp / "pkg-with-asset.json"
        pkg_path.write_text(json.dumps(pkg), encoding="utf-8")
        ctx = render_core.context(manifest_file(self.tmp, package_refs=[str(pkg_path)]))
        digest_before = render_core.render_digest(ctx)
        html = render_core.page(ctx, "CORE1", "PAGES", digest_before)
        self.assertIn('../../css/tablet-12-7.css', html)
        self.assertNotIn('cdn.jsdelivr.net', html)
        self.assertNotIn('vendor/katex/', html)

        labels = [label for label, _digest in ctx.authority_hashes]
        self.assertIn("renderer-source", labels)
        self.assertIn("blueprints", labels)
        self.assertIn("tablet-css", labels)
        self.assertTrue(any(label.startswith("bank:") for label in labels))
        self.assertTrue(any(label.startswith("asset:") for label in labels))

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
        m = product_manifest.derive(PKG, [BANK], "P", "../index.html")
        self.assertEqual(set(m["selection"]), {"microtopics", "core2", "core2a", "core2b"})
        text = json.dumps(m)
        pkg = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        self.assertNotIn(pkg["microtopics"][0]["inferential_jump"], text)


class Migration(unittest.TestCase):
    def test_math_staged_ids_and_references_remain_in_canonical_package(self):
        package = json.loads(migrate_math_linear.TARGET.read_text(encoding="utf-8"))
        ledger = json.loads(migrate_math_linear.LEDGER.read_text(encoding="utf-8"))
        self.assertEqual(ledger["staged_counts"]["question_families"], 4)
        self.assertEqual(ledger["staged_counts"]["questions"], 28)
        self.assertEqual(ledger["existing_counts"]["question_families"], 1)
        self.assertEqual(ledger["existing_counts"]["questions"], 4)
        self.assertEqual(migrate_math_linear.verify_ledger(package, ledger), [])

    def test_historical_merge_preserves_family_and_question_records(self):
        staging = {"question_families": [{"id": "F", "extensions": {}}],
                   "questions": [{"id": "Q", "family_ref": "F", "extensions": {}}]}
        item = {"node": "N", "verification": "v.json", "package": staging}
        merged = promote_verified.merge(None, {}, "Mathematics", "C", [item], "2026-09-28")
        self.assertEqual(merged["question_families"][0]["id"], "F")
        self.assertEqual(merged["questions"][0]["family_ref"], "F")
        self.assertEqual(merged["questions"][0]["extensions"]["grade9v3:promotion"]["verification"], "v.json")


if __name__ == "__main__":
    unittest.main()
