"""A product is judged against what the library holds, not against what its author listed: coverage, promotion and typeset, as the blueprint says."""
from __future__ import annotations

import copy
import glob
import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import product_coverage, product_manifest, render_core, web_blueprint_contract as blueprints

REPO = Path(__file__).resolve().parents[1]
MANIFESTS = sorted(REPO.glob("products/*/*.manifest.json"))
KIN_2D = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
LINEAR = REPO / "products/mathematics/linear-equations.manifest.json"
KIN_1D = REPO / "products/physics/phy-kin-1d-motion.manifest.json"
HARDEST_2D = "PYQ-PHY-JEEADV-2023-P1-Q01"


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def library(manifest: dict) -> tuple[list[dict], list[dict]]:
    packages = [load(REPO / ref) for ref in manifest["package_refs"]]
    bank = [q for ref in manifest.get("bank_refs", []) for q in load(REPO / ref).get("questions", [])]
    return packages, bank


def written(manifest: dict, folder: Path) -> Path:
    path = folder / "m.manifest.json"
    path.write_text(json.dumps(manifest), encoding="utf-8")
    return path


class Denominator(unittest.TestCase):
    def test_what_the_library_holds_is_what_derive_selects(self):
        for path in MANIFESTS:
            manifest = load(path)
            held = product_manifest.derive(manifest["package_refs"][0], manifest.get("bank_refs") or [], manifest["product_id"], manifest["home_href"])
            packages, bank = library(manifest)
            self.assertEqual({k: held["selection"][k] for k in ("core2", "core2a", "core2b")}, product_manifest.derivable(packages, bank), path.name)

    def test_the_report_counts_what_is_selected_and_what_the_library_holds(self):
        rep = product_coverage.for_manifest(KIN_2D)
        self.assertEqual([(rep["cores"][k]["selected"], rep["cores"][k]["available"]) for k in ("core2", "core2a", "core2b")], [(15, 15), (5, 5), (5, 5)])
        self.assertEqual(rep["toughest"]["selects_it"], True)
        rep = product_coverage.for_manifest(LINEAR)
        self.assertEqual((rep["cores"]["core2a"]["selected"], rep["cores"]["core2a"]["available"], len(rep["cores"]["core2a"]["unexplained"])), (1, 14, 13))
        self.assertEqual((rep["cores"]["core2b"]["selected"], rep["cores"]["core2b"]["available"], len(rep["cores"]["core2b"]["unexplained"])), (1, 6, 5))

    def test_a_shortfall_is_an_advisory_for_an_official_product_and_a_gap_for_new_authoring(self):
        _, gaps, _, advisories, _ = render_core.build_report(LINEAR, "PAGES", "FLOOR")
        self.assertEqual([a["core"] for a in advisories if a["component"] == "COVERAGE"], ["CORE2A", "CORE2B"])
        self.assertEqual([g for g in gaps if g.get("component") == "COVERAGE"], [])
        _, gaps, _, advisories, _ = render_core.build_report(LINEAR, "PAGES", "REFERENCE")
        covering = [g for g in gaps if g.get("component") == "COVERAGE"]
        self.assertEqual(sorted(g["core"] for g in covering), ["CORE2A", "CORE2B"])
        self.assertTrue(all(g["duty"] == "AUTHOR_COVERAGE" for g in covering))
        self.assertIn("coverage.omitted", covering[0]["detail"])
        self.assertEqual([a for a in advisories if a["component"] == "COVERAGE"], [])

    def test_a_product_that_selects_all_it_holds_has_no_finding_at_either_bar(self):
        for held in ("FLOOR", "REFERENCE"):
            _, gaps, _, advisories, _ = render_core.build_report(KIN_2D, "PAGES", held)
            self.assertEqual([x for x in gaps + advisories if x.get("component") in {"COVERAGE", "TYPESET"}], [], held)

    def test_a_record_omitted_with_a_reason_is_no_longer_a_shortfall_and_the_reason_is_kept(self):
        manifest = load(LINEAR)
        rep = product_coverage.for_manifest(LINEAR)
        left = rep["cores"]["core2a"]["unexplained"]
        manifest["coverage"] = {"omitted": {i: "practice only: the Core2A shape is not built for it yet" for i in left}}
        with tempfile.TemporaryDirectory() as tmp:
            _, gaps, _, advisories, _ = render_core.build_report(written(manifest, Path(tmp)), "PAGES", "REFERENCE")
        self.assertEqual([g["core"] for g in gaps if g.get("component") == "COVERAGE"], ["CORE2B"])
        report = product_coverage.report(manifest, *library(manifest))
        self.assertEqual(len(report["cores"]["core2a"]["omitted"]), 13)
        self.assertEqual(report["cores"]["core2a"]["unexplained"], [])

    def test_the_hardest_question_of_the_library_left_out_is_a_finding_of_its_own(self):
        manifest = load(KIN_2D)
        manifest["selection"]["core2"] = [i for i in manifest["selection"]["core2"] if i != HARDEST_2D]
        manifest["coverage"] = {"omitted": {HARDEST_2D: "left out on purpose to show what the check says about it"}}
        with tempfile.TemporaryDirectory() as tmp:
            _, gaps, _, _, _ = render_core.build_report(written(manifest, Path(tmp)), "PAGES", "REFERENCE")
        mine = [g for g in gaps if g.get("component") == "COVERAGE"]
        self.assertEqual([g["record"].endswith(":toughest") for g in mine], [True], mine)
        self.assertIn("hardest question", mine[0]["detail"])

    def test_the_sources_not_yet_records_are_counted_and_said_never_rendered(self):
        manifest = load(KIN_2D)
        manifest["coverage"] = {"sources": [
            {"source": "core-2-motion-in-a-plane-fixed.pdf", "kind": "SOURCE_CHALLENGES", "questions": 59, "ingested": 0, "status": "NOT_INGESTED"},
            {"source": "assimilation-sets.pdf", "kind": "PRACTICE_SETS", "questions": 48, "ingested": 8, "status": "PARTLY_INGESTED"},
            {"source": "ncert-problems.pdf", "kind": "NCERT", "questions": 19, "ingested": 0, "status": "EXCLUDED", "reason": "the chapter is outside the Grade 9 scope"}]}
        rep = product_coverage.report(manifest, *library(manifest))
        self.assertEqual({k: rep["sources"][k] for k in ("declared", "questions", "ingested", "not_yet_records")},
                         {"declared": 3, "questions": 126, "ingested": 8, "not_yet_records": 118})
        self.assertTrue(any("118 not yet records" in line for line in product_coverage.summary_lines(rep)))
        with tempfile.TemporaryDirectory() as tmp:
            pages, *_ = render_core.build_report(written(manifest, Path(tmp)), "PAGES", "FLOOR")
        self.assertNotIn("core-2-motion-in-a-plane-fixed", " ".join(pages.values()), "a source that is not a record is not on the page")


class Integrity(unittest.TestCase):
    """A coverage block that says something untrue about the product is refused, like a malformed selection."""

    def refused(self, change, expected: str):
        manifest = load(KIN_2D)
        change(manifest)
        packages, bank = library(manifest)
        with self.assertRaises(product_manifest.ProductSelectionError) as caught:
            product_coverage.validate(manifest, product_manifest.derivable(packages, bank))
        self.assertIn(expected, str(caught.exception))

    def test_a_record_cannot_be_both_selected_and_omitted(self):
        self.refused(lambda m: m.update(coverage={"omitted": {m["selection"]["core2"][0]: "a perfectly good reason to leave it out"}}), "is also selected")

    def test_a_reason_attached_to_nothing_is_refused(self):
        self.refused(lambda m: m.update(coverage={"omitted": {"Q-NOT-IN-THE-LIBRARY": "a perfectly good reason to leave it out"}}), "names no record")

    def test_a_reason_is_a_sentence(self):
        self.refused(lambda m: m.update(coverage={"omitted": {"x": "no"}}), "a sentence")

    def test_a_source_that_ingested_more_than_it_holds_or_has_no_status_is_refused(self):
        self.refused(lambda m: m.update(coverage={"sources": [{"source": "a.pdf", "kind": "K", "questions": 3, "ingested": 4, "status": "INGESTED"}]}), "4 ingested of 3")
        self.refused(lambda m: m.update(coverage={"sources": [{"source": "a.pdf", "kind": "K", "questions": 3, "ingested": 1, "status": "MAYBE"}]}), "status is one of")
        self.refused(lambda m: m.update(coverage={"sources": [{"source": "a.pdf", "kind": "K", "questions": 3, "ingested": 0, "status": "EXCLUDED"}]}), "says why")
        self.refused(lambda m: m.update(coverage={"colour": "blue"}), "only 'omitted' and 'sources'")


class Promotion(unittest.TestCase):
    def selection(self, status):
        manifest = load(KIN_2D)
        packages, bank = library(manifest)
        packages = copy.deepcopy(packages)
        target = packages[0]["questions"][0]
        manifest["selection"]["core2a"] = [target["id"]]
        manifest["selection"]["core2b"] = []
        if status == "ABSENT":
            target.pop("status", None)
        else:
            target["status"] = status
        return manifest, packages, bank

    def test_a_record_whose_status_says_it_is_not_ready_is_refused_with_the_statuses_that_would_do(self):
        for status in ("DISCOVERED", "DISPUTED", "STALE", "RETIRED"):
            manifest, packages, bank = self.selection(status)
            with self.assertRaises(product_manifest.ProductSelectionError) as caught:
                product_manifest.validate_selection(manifest, packages, bank)
            self.assertIn(f"PRODUCT_SELECTION_STATUS_NOT_SELECTABLE: core2a:", str(caught.exception))
            self.assertIn(f":{status} (selectable: CANDIDATE, REVIEWED, CURATED)", str(caught.exception))

    def test_a_candidate_a_reviewed_a_curated_record_and_one_that_claims_nothing_are_selectable(self):
        for status in ("CANDIDATE", "REVIEWED", "CURATED", "ABSENT"):
            manifest, packages, bank = self.selection(status)
            self.assertEqual(len(product_manifest.validate_selection(manifest, packages, bank)["core2a"]), 1, status)

    def test_the_statuses_the_registry_names_are_the_package_schemas_own(self):
        schema = load(REPO / "Shared/library/package.schema.json")
        known = set(schema["properties"]["status"]["enum"])
        policy = product_manifest.promotion_policy()
        self.assertEqual(set(policy["selectable_statuses"]) | set(policy["refused_statuses"]), known)

    def test_every_product_the_library_builds_today_passes_the_gate(self):
        for path in MANIFESTS:
            manifest = load(path)
            packages, bank = library(manifest)
            product_manifest.validate_selection(manifest, packages, bank)


class Typeset(unittest.TestCase):
    def test_a_relation_with_only_an_expression_is_an_advisory_at_the_floor_and_a_gap_at_the_reference(self):
        _, gaps, _, advisories, _ = render_core.build_report(KIN_1D, "PAGES", "FLOOR")
        plain = [a for a in advisories if a["component"] == "TYPESET"]
        self.assertTrue(plain)
        self.assertIn("plain text", plain[0]["detail"])
        self.assertEqual([g for g in gaps if g.get("component") == "TYPESET"], [])
        _, gaps, _, advisories, _ = render_core.build_report(KIN_1D, "PAGES", "REFERENCE")
        self.assertEqual({g["record"] for g in gaps if g.get("component") == "TYPESET"}, {a["record"] for a in plain})
        self.assertTrue(all(g["duty"] == "AUTHOR_TYPESET" for g in gaps if g.get("component") == "TYPESET"))

    def test_a_relation_that_carries_mathml_has_no_finding_and_a_malformed_one_is_still_the_old_gap(self):
        ctx = render_core.Ctx(manifest={"product_id": "P"}, packages=[], bank=[], blueprints=blueprints.load_registry())
        good = {"id": "REL-A", "expression": "t = 2*v/g", "mathml": "<math xmlns=\"http://www.w3.org/1998/Math/MathML\"><mi>t</mi></math>"}
        render_core._relation_expression(ctx, good, "REL-A")
        self.assertEqual((ctx.gaps, ctx.advisories), ([], []))
        bad = {"id": "REL-B", "expression": "t = 2*v/g", "mathml": "<script>alert(1)</script>"}
        render_core._relation_expression(ctx, bad, "REL-B")
        self.assertEqual([g["duty"] for g in ctx.gaps], ["AUTHOR_GOVERNING_RELATION"])
        self.assertEqual(ctx.advisories, [])

    def test_an_empty_mathml_is_not_the_same_as_a_typeset_one(self):
        ctx = render_core.Ctx(manifest={"product_id": "P"}, packages=[], bank=[], blueprints=blueprints.load_registry())
        html = render_core._relation_expression(ctx, {"id": "REL-C", "expression": "F = m*a", "mathml": ""}, "REL-C")
        self.assertIn('class="g9-expr"', html)
        self.assertEqual([a["component"] for a in ctx.advisories], ["TYPESET"])

    def test_the_two_reference_products_have_every_equation_typeset(self):
        for path in (KIN_2D, REPO / "products/physics/phy-nlm-first-law.manifest.json"):
            _, _, _, advisories, _ = render_core.build_report(path, "PAGES", "FLOOR")
            self.assertEqual([a for a in advisories if a["component"] == "TYPESET"], [], path.name)


class TypesetHelper(unittest.TestCase):
    """The gap is only fair if the author can close it: for plain arithmetic the markup is built from the parsed tree."""

    def test_the_markup_is_what_the_pages_accept_and_says_the_same_equation(self):
        from Shared.tools import typeset_relation
        for expression in ("t = 2*v0y/g", "R = v^2*sin(2*theta)/g", "x = sqrt(a^2 + b^2)", "F = m*a", "a <= b", "a != b"):
            markup = typeset_relation.mathml(expression)
            self.assertIsNotNone(render_core._safe_mathml(markup), expression)
        self.assertIn("<mo>=</mo>", typeset_relation.mathml("F = m*a"))
        self.assertIn("<mo>≤</mo>", typeset_relation.mathml("a <= b"), "a comparison the author wrote is not turned into an equals sign")
        self.assertIn("<mfrac>", typeset_relation.mathml("t = 2*v0y/g"))

    def test_a_relation_with_words_in_it_is_refused_and_not_guessed_at(self):
        from Shared.tools import typeset_relation
        with self.assertRaises(typeset_relation.NotTypesettable) as caught:
            typeset_relation.mathml("s is a solution of L(x) = R(x)")
        self.assertIn("written by hand", str(caught.exception))

    def test_the_command_prints_a_json_string_and_exits_one_on_what_it_cannot_read(self):
        import contextlib
        import io
        from Shared.tools import typeset_relation
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(typeset_relation.main(["F = m*a", "--json"]), 0)
        self.assertTrue(isinstance(json.loads(out.getvalue()), str))
        with contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(typeset_relation.main(["a solution"]), 1)

    def test_the_gap_tells_the_author_about_the_tool(self):
        from Shared.tools import deploy_test
        self.assertIn("typeset_relation.py", deploy_test.authoring_hints(["CORE1"])["TYPESET"]["hint"])


class Registry(unittest.TestCase):
    def test_the_three_rules_are_in_the_registry_the_schema_and_the_written_specification(self):
        import jsonschema
        registry = blueprints.load_registry()
        schema = load(REPO / "Shared/web/interactive-page-blueprint.schema.json")
        self.assertEqual([e.message for e in jsonschema.Draft202012Validator(schema).iter_errors(registry)], [])
        policy = registry["component_policy"]
        self.assertEqual(policy["coverage"]["held_to"], {"FLOOR": "ADVISORY", "REFERENCE": "GAP"})
        self.assertEqual(policy["typeset"]["duty"], "AUTHOR_TYPESET")
        spec = (REPO / "docs/specs/PAGE-BLUEPRINT-COMPONENTS.md").read_text(encoding="utf-8")
        for heading in ("## Rules about a whole product", "**Coverage**", "**Promotion.**", "**Typeset**"):
            self.assertIn(heading, spec)

    def test_a_registry_without_one_of_the_rules_is_refused_by_its_schema(self):
        import jsonschema
        schema = load(REPO / "Shared/web/interactive-page-blueprint.schema.json")
        for rule in ("coverage", "promotion", "typeset"):
            broken = copy.deepcopy(blueprints.load_registry())
            del broken["component_policy"][rule]
            self.assertTrue(list(jsonschema.Draft202012Validator(schema).iter_errors(broken)), rule)

    def test_the_duties_the_rules_name_are_known_to_the_depth_check(self):
        from Shared.tools import package_depth
        for duty in ("AUTHOR_COVERAGE", "AUTHOR_TYPESET"):
            self.assertIn(duty, package_depth.DUTIES)


if __name__ == "__main__":
    unittest.main()
