"""One renderer, selection-only manifests, and the preserved M3 migration."""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
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
        boundary = 'Trajectory-equation derivation as a first-slice requirement.'
        first_article = html.index('<article ')
        orientation_start = html.index('<section class="g9-core1a-book"')
        orientation_end = html.index('</section>', orientation_start) + len('</section>')
        orientation = html[orientation_start:orientation_end]
        self.assertIn('data-g9-block="scope_boundary"', orientation)
        self.assertIn(boundary, orientation)
        self.assertNotIn(boundary, html[first_article:])
        self.assertNotIn('data-locked', orientation)

        prerequisite_refs = bucket.get("prerequisite_refs") or []
        self.assertTrue(prerequisite_refs)
        for ref in prerequisite_refs:
            self.assertIn(f'data-g9-foundation-ref="{ref}"', orientation)
        self.assertEqual(
            orientation.count('data-g9-availability="unlinked"'),
            len(prerequisite_refs),
        )
        self.assertIn("direct route unavailable in this product", orientation)
        self.assertNotIn("locked", orientation.lower())

    def test_core1a_difficulty_is_context_not_navigation_or_mastery_state(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        route = render_core._core1a_route(ctx)

        self.assertIn('data-g9-meta-kind="concept-difficulty"', html)
        self.assertNotIn("data-g9-mastery", html)
        self.assertNotIn("data-g9-ready", html)
        for row in route:
            self.assertIn(f'href="#{row["unit_id"]}"', html)

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

    def test_core1a_structural_forms_compose_without_machine_archetype_classification(self):
        motion_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        motion_ctx = render_core.context(motion_manifest)
        motion_html = render_core.page(
            motion_ctx, "CORE1A", "PAGES", render_core.render_digest(motion_ctx)
        )

        # Explicit structure drives the view: staged representations stay staged,
        # relations stay semantic matrices, and worked/repair/check material keeps
        # its governed content. The renderer does not classify every figure or
        # VERIFY step into a new academic archetype.
        self.assertIn('data-g9-stage-sequence="true"', motion_html)
        self.assertIn("data-g9-equation-matrix", motion_html)
        self.assertIn('data-g9-block="independent_check"', motion_html)
        for microtopic in motion_ctx.selection_rows["microtopics"]:
            for unit in microtopic.get("construction_units") or []:
                if unit.get("representation_ref"):
                    self.assertIn(
                        f'data-g9-representation="{unit["representation_ref"]}"',
                        motion_html,
                    )
        self.assertNotIn("data-g9-scene-event", motion_html)
        self.assertNotIn("data-g9-compare-boundary", motion_html)

        derivation_manifest = REPO / "products" / "physics" / "phy-kin-1d-motion.manifest.json"
        derivation_ctx = render_core.context(derivation_manifest)
        derivation_html = render_core.page(
            derivation_ctx, "CORE1A", "PAGES", render_core.render_digest(derivation_ctx)
        )
        self.assertIn('data-g9-derivation-bridge="true"', derivation_html)

        for ctx in (motion_ctx, derivation_ctx):
            for microtopic in ctx.selection_rows["microtopics"]:
                self.assertNotIn("archetype", microtopic)


    def test_core1a_core1b_and_core2_keep_distinct_learner_roles(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)

        core1a = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        first_concept = ctx.selection_rows["microtopics"][0]["id"]
        a_start = core1a.index(f'<article id="{first_concept}"')
        a_end = core1a.index("</article>", a_start)
        a_article = core1a[a_start:a_end]
        self.assertLess(
            a_article.index('data-g9-block="inferential_jump"'),
            a_article.index("data-g9-attempt-box"),
        )

        core1b = render_core.page(ctx, "CORE1B", "PAGES", render_core.render_digest(ctx))
        b_start = core1b.index(f'<article id="{first_concept}"')
        b_end = core1b.index("</article>", b_start)
        b_article = core1b[b_start:b_end]
        self.assertLess(
            b_article.index('data-g9-block="predict"'),
            b_article.index("data-g9-attempt-box"),
        )
        self.assertIn("data-requires-attempt", b_article)
        self.assertGreater(
            b_article.index('data-g9-block="rejoin_jump"'),
            b_article.index("data-g9-attempt-box"),
        )

        core2 = render_core.page(ctx, "CORE2", "PAGES", render_core.render_digest(ctx))
        self.assertIn('data-g9-block="source_identity"', core2)
        self.assertNotIn('data-g9-block="inferential_jump"', core2)

    def test_core1a_companion_support_follows_each_unit_in_compact_dom_order(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        projectile = next(
            row for row in ctx.selection_rows["microtopics"]
            if row["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL"
        )
        article_start = html.index(f'<article id="{projectile["id"]}"')
        article_end = html.index("</article>", article_start)
        article = html[article_start:article_end]

        units = projectile["construction_units"]
        for index, unit in enumerate(units):
            primary_at = article.index(f'id="{unit["id"]}"')
            support_at = article.index(f'data-g9-support-for="{unit["id"]}"')
            next_boundary = (
                article.index(f'id="{units[index + 1]["id"]}"')
                if index + 1 < len(units)
                else article.index('data-g9-block="exit_task"')
            )
            self.assertLess(primary_at, support_at)
            self.assertLess(support_at, next_boundary)

            construction_slot = article.rfind(
                'data-blueprint-slot="construction"', 0, primary_at
            )
            support_slot = article.rfind(
                'data-blueprint-slot="repair_closure"', 0, support_at
            )
            self.assertGreaterEqual(construction_slot, 0)
            self.assertGreater(support_slot, construction_slot)

        self.assertIn(
            'body[data-core=CORE1A] article.g9-stage-support>.slot-identity{grid-column:1/-1}',
            render_core.CSS,
        )

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

    def test_core1a_watch_one_preserves_legacy_reasoning_and_check_without_fabricating_why(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        microtopic = ctx.selection_rows["microtopics"][0]
        unit = microtopic["construction_units"][0]
        question = ctx.index("questions")[unit["worked_anchor_ref"]]
        html = render_core._core1a_worked_anchor(question)

        self.assertIn(question["stem"], html)
        for step in question["answer"]["reasoning"]:
            self.assertIn(step, html)
        self.assertIn(question["answer"]["summary"], html)
        self.assertIn(render_core.esc(question["answer"]["check"]), html)
        self.assertNotIn("Why valid:", html)

    def test_core1a_watch_one_uses_structured_why_when_canonical_route_supplies_it(self):
        question = {
            "stem": "Explain one governed move.",
            "answer": {
                "summary": "Done.",
                "check": "Check independently.",
                "reasoning_route": [{
                    "id": "MOVE-1",
                    "action": "Choose the model.",
                    "why_valid": "The stated conditions match the model.",
                    "output": "One valid model.",
                }],
            },
        }
        html = render_core._core1a_worked_anchor(question)

        self.assertIn('data-g9-watch-step', html)
        self.assertIn('data-g9-move-ref="MOVE-1"', html)
        self.assertIn("Choose the model.", html)
        self.assertIn("Why valid: The stated conditions match the model.", html)
        self.assertIn("Result: One valid model.", html)

    def test_core1a_repair_and_check_content_occupies_the_blueprint_support_lane(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        construction_at = html.index('data-blueprint-slot="construction"')
        support_at = html.index('data-blueprint-slot="repair_closure"')

        self.assertLess(construction_at, support_at)
        self.assertLess(html.index('data-g9-block="worked_anchor"'), support_at)
        self.assertGreater(html.index('data-g9-block="wrong_path"'), support_at)
        self.assertGreater(html.index('data-g9-block="diagnose"'), support_at)
        self.assertGreater(html.index('data-g9-block="repair"'), support_at)
        self.assertGreater(html.index('data-g9-block="independent_check"'), support_at)
        self.assertGreater(html.index('data-g9-block="exit_task"'), support_at)
        self.assertEqual(html.count("data-g9-support-for"), len(render_core._core1a_route(ctx)))

    def test_core1a_attempt_remains_after_complete_construction(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        selected = ctx.selection_rows["microtopics"]

        for index, microtopic in enumerate(selected):
            start = html.index(f'<article id="{microtopic["id"]}"')
            end = (html.index(f'<article id="{selected[index + 1]["id"]}"', start)
                   if index + 1 < len(selected) else html.index("</main>", start))
            article = html[start:end]
            units = microtopic.get("construction_units") or []
            if units:
                self.assertLess(article.index(f'id="{units[-1]["id"]}"'), article.index('data-g9-attempt-box'))
            self.assertLess(article.rindex('data-g9-block="worked_anchor"'), article.index('data-g9-attempt-box'))

    def test_core1a_derivation_heavy_witness_uses_teaching_path_without_synthetic_units(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-1d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        target = next(
            microtopic for microtopic in ctx.selection_rows["microtopics"]
            if microtopic["id"] == "MIC-PHY-KIN-CONSTANT-ACCELERATION"
        )
        self.assertFalse(target.get("construction_units"))

        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        start = html.index(f'<article id="{target["id"]}"')
        selected = ctx.selection_rows["microtopics"]
        target_index = selected.index(target)
        end = (
            html.index(f'<article id="{selected[target_index + 1]["id"]}"', start)
            if target_index + 1 < len(selected)
            else html.index("</main>", start)
        )
        article = html[start:end]

        self.assertIn("data-g9-derivation-bridge", article)
        self.assertIn("data-g9-equation-matrix", article)
        for step in target["teaching_path"]:
            self.assertIn(f'data-g9-step="{step["id"]}"', article)
            self.assertIn(render_core.esc(step["action"]), article)
            self.assertIn(render_core.esc(step["why_valid"]), article)
            self.assertIn(render_core.esc(step["output"]), article)
        self.assertIn(f'href="#{target["id"]}"', html)

        renderer_source = (REPO / "Shared/tools/render_core.py").read_text(encoding="utf-8")
        self.assertNotIn(target["id"], renderer_source)
        self.assertNotIn("Trajectory-equation derivation as a first-slice requirement.", article)

    def test_core2a_and_core2b_repairs_return_to_exact_core1a_construction_unit_when_owned(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        step_owner = {}
        for microtopic in ctx.selection_rows["microtopics"]:
            for unit in microtopic.get("construction_units") or []:
                for step_ref in unit.get("step_refs") or []:
                    step_owner[step_ref] = (microtopic["id"], unit["id"])

        for role in ("CORE2A", "CORE2B"):
            html = render_core.page(ctx, role, "PAGES", render_core.render_digest(ctx))
            for question in ctx.selection_rows[role.lower()]:
                repair_ref = question.get("repair_ref")
                if repair_ref not in step_owner:
                    continue
                concept_id, unit_id = step_owner[repair_ref]
                self.assertIn(f'data-g9-repair-ref="{repair_ref}"', html)
                self.assertIn(f'data-g9-concept-ref="{concept_id}"', html)
                self.assertIn(f'data-g9-repair-target="{unit_id}"', html)
                self.assertIn(f'href="core1a.html#{unit_id}"', html)

    def test_single_file_scopes_nested_core1a_section_links_for_exact_repair_return(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        pages, _gaps, _digest = render_core.build(repo_manifest, mode="SINGLE_FILE")
        html = pages["product.html"]
        target = "CU-PHY-KIN-PROJECTILE-MODEL-3"

        self.assertIn(f'id="g9-CORE1A--{target}"', html)
        self.assertIn(f'href="#g9-CORE1A--{target}"', html)
        self.assertNotIn(f'href="core1a.html#{target}"', html)

    def test_real_motion_core1a_pages_single_file_and_embed_preserve_concept_book_identity(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        pages, page_gaps, page_digest = render_core.build(repo_manifest, mode="PAGES")
        single, single_gaps, single_digest = render_core.build(repo_manifest, mode="SINGLE_FILE")
        embed, embed_gaps, embed_digest = render_core.build(repo_manifest, mode="EMBED")

        self.assertRegex(page_digest, r"^[0-9a-f]{16}$")
        self.assertRegex(single_digest, r"^[0-9a-f]{16}$")
        self.assertRegex(embed_digest, r"^[0-9a-f]{16}$")
        semantic = render_core.semantic_metadata_digest(pages, "PAGES")
        self.assertEqual(semantic, render_core.semantic_metadata_digest(single, "SINGLE_FILE"))
        self.assertEqual(semantic, render_core.semantic_metadata_digest(embed, "EMBED"))
        self.assertFalse([gap for gap in page_gaps if gap["core"] == "CORE1A"])
        self.assertFalse([gap for gap in single_gaps if gap["core"] == "CORE1A"])
        self.assertFalse([gap for gap in embed_gaps if gap["core"] == "CORE1A"])

        core1a = pages["core1a.html"]
        product = single["product.html"]
        self.assertIn(f'render_core/2 {page_digest}', core1a)
        self.assertIn(f'render_core/2 {single_digest}', product)
        ctx = render_core.context(repo_manifest)
        for row in render_core._core1a_route(ctx):
            anchor = row["unit_id"]
            self.assertIn(f'id="{anchor}"', core1a)
            self.assertIn(f'id="g9-CORE1A--{anchor}"', product)
            self.assertIn(f'href="#g9-CORE1A--{anchor}"', product)

        self.assertIn("data-g9-bucket-orientation", core1a)
        self.assertIn("data-g9-equation-matrix", core1a)
        self.assertIn("data-g9-bucket-orientation", product)
        self.assertIn("data-g9-equation-matrix", product)
        self.assertNotRegex(product, r'href="core\w+\.html#')

    def test_core1a_tablet_contract_reuses_existing_shared_shell_invariants(self):
        repo_manifest = REPO / "products" / "physics" / "phy-kin-2d-motion.manifest.json"
        ctx = render_core.context(repo_manifest)
        html = render_core.page(ctx, "CORE1A", "PAGES", render_core.render_digest(ctx))
        blueprint = next(
            row for row in ctx.blueprints["blueprints"]
            if "CORE1A" in row["core_roles"]
        )

        self.assertEqual(blueprint["responsive_policy"]["expanded"], "STAGE_SUPPORT")
        self.assertAlmostEqual(
            blueprint["responsive_policy"]["primary_fraction"], 0.68, places=2
        )
        self.assertAlmostEqual(
            blueprint["responsive_policy"]["support_fraction"], 0.32, places=2
        )
        self.assertGreaterEqual(blueprint["touch_policy"]["minimum_target_css_px"], 48)
        self.assertGreaterEqual(blueprint["touch_policy"]["minimum_control_gap_css_px"], 8)
        self.assertFalse(blueprint["interaction_policy"]["progressive_support"])
        self.assertIn("ATTEMPT_FIRST_AS_PRIMARY_MODE", blueprint["forbidden"])

        self.assertIn("@media (min-width:1100px)", render_core.CSS)
        self.assertIn("grid-template-columns:.68fr .32fr", render_core.CSS)
        self.assertIn("min-height:var(--g9-touch-min)", render_core.CSS)
        self.assertIn("overflow-x:auto", render_core.CSS)
        self.assertIn(".g9-stage-controls{display:flex;align-items:center;gap:8px;flex-wrap:wrap", render_core.CSS)
        self.assertIn("[data-g9-concept-route] a,[data-g9-section-route] a{display:flex;width:100%;max-width:100%;min-width:0", render_core.CSS)
        self.assertIn("overflow-wrap:anywhere", render_core.CSS)
        self.assertIn('data-g9-equation-matrix', html)

    def test_core1a_browser_audit_contract_is_syntax_valid_and_covers_required_viewports(self):
        audit = REPO / "tools" / "site-audit" / "core-page-audit.mjs"
        source = audit.read_text(encoding="utf-8")

        for width, height in ((390, 844), (800, 1280), (820, 1180), (1180, 820), (1280, 800), (1440, 900)):
            self.assertIn(f"width: {width}, height: {height}", source)
        for marker in (
            "core1a-spec",
            "--http-root",
            "contentWidthPx",
            "core1aLayout",
            "tableContainment",
            "controlGeometry",
            "anchorSafety",
            "focusProbe",
            "learningStart",
            "constructionStart",
            "stageKeyboard",
            "sectionKeyboard",
            "historyRestored",
            "reducedMotion",
            "zoom200",
        ):
            self.assertIn(marker, source)

        if not shutil.which("node"):
            self.skipTest("Node.js unavailable for audit syntax check")
        result = subprocess.run(
            ["node", "--check", str(audit)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

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
