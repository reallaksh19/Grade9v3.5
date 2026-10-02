"""Owner decision publishes one exact render; building cannot mutate public pages."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import accept_product, build_products, quality_gate, render_core

REPO = Path(__file__).resolve().parents[1]


LINK = '<a data-g9-action="pdf" class="g9-pdf-link" href="core1.pdf" target="_blank" rel="noopener" type="application/pdf" aria-label="PDF"><span>PDF</span></a>'


def printed(out: Path, *, mode: str = "LEARNER_PDF", pdf: bytes = b"%PDF-1.4 learner copy", page_digest: str | None = None) -> None:
    """What print-product.mjs leaves beside the pages: core1.pdf and the receipt that ties it to the exact bytes of core1.html."""
    sha = lambda data: "sha256:" + hashlib.sha256(data).hexdigest()  # noqa: E731
    (out / "core1.pdf").write_bytes(pdf)
    (out / "print-receipt.json").write_text(json.dumps({"tool": "print-product/2", "mode": mode, "pages": [
        {"page": "core1.html", "page_digest": page_digest or sha((out / "core1.html").read_bytes()), "pdf": "core1.pdf", "pdf_digest": sha(pdf), "figures": 0}]}))


def fixture(repo: Path, *, review: bool = False, cited: bool = False, link: bool = False) -> tuple[Path, str]:
    manifest = repo / "products" / "physics" / "sample.manifest.json"
    manifest.parent.mkdir(parents=True, exist_ok=True)
    pkg = repo / "Physics" / "library" / "sample.v1.json"
    pkg.parent.mkdir(parents=True, exist_ok=True)
    ext = {"grade9v3:authored_by": "author-1"}
    if cited:
        ext["grade9v3:citations"] = {"stem": ["EV-1"]}
    pkg.write_text(json.dumps({"microtopics": [{"id": "MIC-1", "extensions": ext}]}))
    manifest.write_text(json.dumps({"subject": "Physics", "product_id": "sample",
                                    "package_refs": ["Physics/library/sample.v1.json"]}))
    out = repo / "publication" / "products" / "physics" / "sample"
    out.mkdir(parents=True, exist_ok=True)
    neutral = '<html><head><meta name="g9-render" content="render_core/1 g9-digest-pending"></head><body>Prompt</body></html>'
    neutrals = {"core1.html": neutral.replace("<body>", "<body>" + LINK) if link else neutral, "index.html": neutral}
    h = hashlib.sha256()
    for name in ("core1.html", "index.html"):
        h.update(name.encode() + b"\0" + neutrals[name].encode())
    digest = h.hexdigest()[:16]
    for name in ("core1.html", "index.html"):
        (out / name).write_text(neutrals[name].replace("g9-digest-pending", digest))
    (out / "render-receipt.json").write_text(json.dumps({
        "renderer": "render_core/1", "digest": digest, "mode": "PAGES",
        "draft": False, "pages": ["core1.html", "index.html"], "gaps": []
    }))
    if review:
        path = repo / "products" / "verification" / "sample.review.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps({
            "schema": "product-review/v2", "render_digest": digest, "reviewer": "reviewer-2",
            "findings": [{"id": "F-1", "severity": "S1", "record": "MIC-1"}],
            "overall": {"recommendation": "revise"}
        }))
    return manifest, digest


class VerifyRender(unittest.TestCase):
    """The digest is written into two stamped fields; nowhere else may it appear."""

    TEMPLATE = ('<html data-g9-render-digest="g9-digest-pending"><head>'
                '<meta name="g9-render" content="render_core/2 g9-digest-pending"></head>'
                '<body>{body}</body></html>')

    def render(self, body: str = "Prompt", tamper=None) -> Path:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        out = Path(tmp.name)
        neutral = self.TEMPLATE.format(body=body)
        digest = hashlib.sha256(b"core1.html\0" + neutral.encode()).hexdigest()[:16]
        page = neutral.replace("g9-digest-pending", digest)
        (out / "core1.html").write_text(tamper(page, digest) if tamper else page)
        (out / "render-receipt.json").write_text(json.dumps({
            "renderer": "render_core/2", "digest": digest, "mode": "PAGES",
            "draft": False, "pages": ["core1.html"], "gaps": []}))
        return out

    def test_a_render_stamped_in_both_fields_verifies(self):
        self.assertEqual(len(accept_product.verify_render(self.render())["digest"]), 16)

    def test_the_digest_anywhere_else_in_a_page_is_refused(self):
        out = self.render(tamper=lambda page, digest: page.replace("Prompt", f"Prompt {digest}"))
        with self.assertRaisesRegex(ValueError, "outside its stamped fields"):
            accept_product.verify_render(out)

    def test_a_changed_state_scope_attribute_is_refused(self):
        out = self.render(tamper=lambda page, digest: page.replace(
            f'data-g9-render-digest="{digest}"', 'data-g9-render-digest="0000000000000000"'))
        with self.assertRaisesRegex(ValueError, "no longer match"):
            accept_product.verify_render(out)


class Publication(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.repo = Path(self.tmp.name)
        self.manifest, self.digest = fixture(self.repo)
        self.current_basis = mock.patch.object(accept_product, "verify_current_basis")
        self.current_basis.start()

    def tearDown(self):
        self.current_basis.stop()
        self.tmp.cleanup()

    def test_build_does_not_write_or_remove_public_even_with_a_failed_report(self):
        public = self.repo / "public" / "products" / "physics" / "sample"
        public.mkdir(parents=True)
        (public / "sentinel").write_bytes(b"an earlier Owner decision")
        before = (public / "sentinel").read_bytes()
        standalone = self.repo / "standalone" / "products" / "physics" / "sample.html"
        standalone.parent.mkdir(parents=True)
        standalone.write_bytes(b"an earlier Owner standalone decision")
        out = self.repo / "publication" / "products"
        report = {"verdict": "FAIL", "fail_reasons": ["DRAFT"], "findings": []}
        with mock.patch.object(build_products, "WORK", out), mock.patch.object(build_products, "PUBLIC", self.repo / "public" / "products"), mock.patch.object(build_products, "ACCEPTANCE", self.repo / "products" / "acceptance"), mock.patch.object(build_products, "REVIEWS", self.repo / "products" / "verification"), mock.patch.object(build_products, "STANDALONE", self.repo / "standalone" / "products"), mock.patch.object(build_products, "STANDALONE_WORK", self.repo / "publication" / "standalone" / "products"), mock.patch.object(build_products.quality_gate, "gate", return_value=report):
            # build_one clears the work directory; the fake renderer restores it.
            def recreate(_args):
                fixture(self.repo)
                receipt_path = self.repo / "publication" / "products" / "physics" / "sample" / "render-receipt.json"
                receipt = json.loads(receipt_path.read_text())
                receipt["gaps"] = [{"duty": "AUTHOR", "record": "MIC-1"}]
                receipt_path.write_text(json.dumps(receipt))
                return 0
            with mock.patch.object(build_products.render_core, "main", side_effect=recreate), mock.patch.object(build_products.render_core, "build", return_value=({"product.html": "<html>staged</html>"}, [], self.digest)):
                build_products.build_one(self.manifest, static=True)
        self.assertEqual((public / "sentinel").read_bytes(), before)
        self.assertEqual(standalone.read_bytes(), b"an earlier Owner standalone decision")
        self.assertEqual((self.repo / "publication" / "standalone" / "products" / "physics" / "sample.html").read_bytes(), b"<html>staged</html>")

    def test_only_owner_acceptance_publishes_matching_bytes(self):
        with mock.patch.object(accept_product, "mirror_pages") as mirror:
            decision = accept_product.accept("sample", repo=self.repo)
        self.assertEqual(decision["render_digest"], self.digest)
        published = self.repo / "public" / "products" / "physics" / "sample"
        self.assertEqual(accept_product.verify_render(published)["digest"], self.digest)
        self.assertEqual((published / "core1.html").read_bytes(),
                         (self.repo / "publication" / "products" / "physics" / "sample" / "core1.html").read_bytes())
        self.assertEqual(json.loads((self.repo / "products" / "acceptance" / "sample.json").read_text())["render_digest"], self.digest)
        mirror.assert_called_once_with(self.repo)

    def test_the_acceptance_records_what_the_release_decision_rested_on(self):
        assurance = {"status": "ELIGIBLE", "assurance_bundle_digest": "sha256:" + "a" * 64,
                     "waived": [{"type": "ACCESSIBILITY", "subject": "PROJECTION:sample", "outcome": "MISSING", "waiver": "ACCESSIBILITY@*", "approval_ref": "the Owner"},
                                {"type": "ACCESSIBILITY", "subject": "PROJECTION:sample-standalone", "outcome": "MISSING", "waiver": "ACCESSIBILITY@*", "approval_ref": "the Owner"},
                                {"type": "SOURCE_INTEGRITY", "subject": "CANONICAL_RECORD:p", "outcome": "MISSING", "waiver": "SOURCE_INTEGRITY@*", "approval_ref": "the Owner"}]}
        with mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept("sample", repo=self.repo, assurance=assurance)
        recorded = json.loads((self.repo / "products" / "acceptance" / "sample.json").read_text())["assurance"]
        self.assertEqual(recorded, decision["assurance"])
        self.assertEqual(recorded, {"status": "ELIGIBLE", "bundle_digest": "sha256:" + "a" * 64, "waived": ["ACCESSIBILITY", "SOURCE_INTEGRITY"]})

    def test_an_acceptance_without_a_release_decision_records_none(self):
        with mock.patch.object(accept_product, "mirror_pages"):
            accept_product.accept("sample", repo=self.repo)
        self.assertNotIn("assurance", json.loads((self.repo / "products" / "acceptance" / "sample.json").read_text()))

    def accept_with_links(self, **printing):
        fixture(self.repo, link=True)
        out = self.repo / "publication" / "products" / "physics" / "sample"
        if printing is not None:
            printed(out, **printing)
        return out

    def test_the_learner_pdf_a_page_links_is_published_beside_it_and_the_key_pdf_never_is(self):
        out = self.accept_with_links()
        (out / "core1.key.pdf").write_bytes(b"%PDF-1.4 THE ANSWERS")
        (out / "print-key-receipt.json").write_text("{}")
        with mock.patch.object(accept_product, "mirror_pages"):
            accept_product.accept("sample", repo=self.repo)
        published = self.repo / "public" / "products" / "physics" / "sample"
        self.assertEqual((published / "core1.pdf").read_bytes(), b"%PDF-1.4 learner copy")
        self.assertFalse((published / "core1.key.pdf").exists(), "a key PDF holds the answers")
        self.assertFalse((published / "print-key-receipt.json").exists())
        self.assertEqual(render_core.pdf_publication_problems(published), [])

    def test_a_page_that_links_a_pdf_that_is_not_there_is_not_published(self):
        fixture(self.repo, link=True)
        with mock.patch.object(accept_product, "mirror_pages"), self.assertRaises(ValueError) as caught:
            accept_product.accept("sample", repo=self.repo)
        self.assertIn("core1.pdf", str(caught.exception))
        self.assertIn("print-product.mjs", str(caught.exception))
        self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())

    def test_a_pdf_that_is_not_the_one_printed_from_that_page_is_not_published(self):
        for what, printing in {"the page changed after it was printed": {"page_digest": "sha256:" + "0" * 64},
                               "a key receipt": {"mode": "KEY_PDF"}}.items():
            with self.subTest(what):
                out = self.accept_with_links(**printing)
                with mock.patch.object(accept_product, "mirror_pages"), self.assertRaises(ValueError):
                    accept_product.accept("sample", repo=self.repo)
                self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())
        out = self.accept_with_links()
        (out / "core1.pdf").write_bytes(b"%PDF-1.4 swapped after printing")
        with mock.patch.object(accept_product, "mirror_pages"), self.assertRaises(ValueError) as caught:
            accept_product.accept("sample", repo=self.repo)
        self.assertIn("bytes differ", str(caught.exception))

    def test_a_pdf_nobody_can_trace_to_a_page_is_not_published(self):
        out = self.accept_with_links()
        (out / "extra.pdf").write_bytes(b"%PDF-1.4 who made this")
        with mock.patch.object(accept_product, "mirror_pages"), self.assertRaises(ValueError) as caught:
            accept_product.accept("sample", repo=self.repo)
        self.assertIn("extra.pdf", str(caught.exception))

    def test_a_link_that_points_anywhere_but_a_learner_pdf_beside_the_page_is_refused(self):
        out = self.accept_with_links()
        page = out / "core1.html"
        page.write_text(page.read_text().replace('href="core1.pdf"', 'href="../../../secret/core1.key.pdf"'))
        self.assertTrue(any("not a learner PDF beside the page" in p for p in render_core.pdf_publication_problems(out)))

    def test_acceptance_records_where_the_owner_approved_without_requiring_it(self):
        with mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept(
                "sample", repo=self.repo,
                approval_ref="  https://github.com/o/r/issues/1#issuecomment-5   \n accepted")
        self.assertEqual(decision["approval_ref"], "https://github.com/o/r/issues/1#issuecomment-5 accepted")
        self.assertEqual(decision["accepted_by"], "owner")
        record = json.loads((self.repo / "products" / "acceptance" / "sample.json").read_text())
        self.assertEqual(record["approval_ref"], decision["approval_ref"])

    def test_acceptance_without_an_approval_reference_still_publishes(self):
        with mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept("sample", repo=self.repo)
        self.assertIsNone(decision["approval_ref"])
        self.assertEqual(decision["accepted_by"], "owner")
        self.assertTrue((self.repo / "public" / "products" / "physics" / "sample").is_dir())

    def test_an_oversized_approval_reference_is_trimmed_not_refused(self):
        with mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept("sample", repo=self.repo, approval_ref="x" * 900)
        self.assertEqual(len(decision["approval_ref"]), 500)

    def test_owner_acceptance_also_publishes_the_staged_standalone_page(self):
        standalone = self.repo / "publication" / "standalone" / "products" / "physics" / "sample.html"
        standalone.parent.mkdir(parents=True)
        standalone.write_bytes(b"<html>one file</html>")
        standalone.with_suffix(".receipt.json").write_text(json.dumps({
            "pages_digest": self.digest, "render_digest": self.digest,
            "sha256": hashlib.sha256(standalone.read_bytes()).hexdigest(), "mode": "SINGLE_FILE",
        }))
        with mock.patch.object(accept_product.render_core, "build", return_value=({"product.html": "<html>one file</html>"}, [], self.digest)), mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept("sample", repo=self.repo)
        self.assertEqual(decision["standalone_sha256"], hashlib.sha256(standalone.read_bytes()).hexdigest())
        self.assertEqual((self.repo / "standalone" / "products" / "physics" / "sample.html").read_bytes(), standalone.read_bytes())

    def test_changed_page_is_rejected_before_publication(self):
        page = self.repo / "publication" / "products" / "physics" / "sample" / "core1.html"
        page.write_text(page.read_text().replace("Prompt", "Changed answer"))
        with self.assertRaisesRegex(ValueError, "no longer match"):
            accept_product.accept("sample", repo=self.repo)
        self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())

    def test_changed_standalone_is_rejected_before_publication(self):
        standalone = self.repo / "publication" / "standalone" / "products" / "physics" / "sample.html"
        standalone.parent.mkdir(parents=True)
        standalone.write_bytes(b"<html>changed</html>")
        standalone.with_suffix(".receipt.json").write_text(json.dumps({
            "pages_digest": self.digest, "render_digest": self.digest,
            "sha256": hashlib.sha256(standalone.read_bytes()).hexdigest(), "mode": "SINGLE_FILE",
        }))
        with mock.patch.object(accept_product.render_core, "build", return_value=({"product.html": "<html>original</html>"}, [], self.digest)):
            with self.assertRaisesRegex(ValueError, "staged standalone page"):
                accept_product.accept("sample", repo=self.repo)
        self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())

    def test_existing_standalone_cannot_be_left_stale_by_pages_acceptance(self):
        standalone = self.repo / "standalone" / "products" / "physics" / "sample.html"
        standalone.parent.mkdir(parents=True)
        standalone.write_bytes(b"earlier published page")
        with self.assertRaisesRegex(ValueError, "rebuild both modes"):
            accept_product.accept("sample", repo=self.repo)
        self.assertEqual(standalone.read_bytes(), b"earlier published page")
        self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())

    def test_owner_decline_leaves_public_untouched(self):
        fixture(self.repo, review=True, cited=True)
        with self.assertRaisesRegex(ValueError, "did not accept"):
            accept_product.accept("sample", repo=self.repo, confirm=lambda _: "n")
        self.assertFalse((self.repo / "public" / "products" / "physics" / "sample").exists())
        self.assertFalse((self.repo / "products" / "acceptance" / "sample.json").exists())

    def test_open_s1_and_unclassified_source_are_visible_but_owner_can_accept(self):
        fixture(self.repo, review=True, cited=True)
        prompts = []
        with mock.patch.object(accept_product, "mirror_pages"):
            decision = accept_product.accept("sample", repo=self.repo,
                                             confirm=lambda question: prompts.append(question) or "y")
        self.assertEqual(len(prompts), 1)
        self.assertEqual(decision["accepted_open_findings"], ["F-1"])
        self.assertEqual(decision["unverified_fact_records"], ["MIC-1"])

    def test_quality_report_cli_default_is_advisory_strict_is_for_tool_tests(self):
        report = {"verdict": "FAIL", "fail_reasons": ["DRAFT"], "findings": [], "continuity": [],
                  "product_id": "sample"}
        with mock.patch.object(quality_gate, "gate", return_value=report), mock.patch.object(quality_gate, "validate", return_value=[]):
            args = [str(self.repo), "--subject", "Physics", "--product-id", "sample"]
            self.assertEqual(quality_gate.main(args), 0)
            self.assertEqual(quality_gate.main(args + ["--strict"]), 1)

    @unittest.skipUnless(importlib.util.find_spec("jsonschema"), "NOT_RUN: jsonschema unavailable locally")
    def test_new_review_shape_is_parseable_and_historical_reviews_are_left_as_history(self):
        import jsonschema
        schema = json.loads((REPO / "Shared/quality/product-review.schema.json").read_text())
        jsonschema.Draft202012Validator.check_schema(schema)
        review = {
            "schema": "product-review/v2", "product": "sample", "reviewer": "reviewer-2",
            "reviewer_session": "session-2", "reviewed_at": "2026-09-27", "render_digest": self.digest,
            "read_first": ["DESIGN-NOTE.md"], "strengths": [],
            "findings": [{"id": "F-1", "severity": "S1", "kind": "content", "record": "MIC-1",
                          "page": "core1.html", "learner_impact": "Premature result",
                          "detail": "The prompt states the conclusion", "suggested_fix": "Move it to the solution"}],
            "previous_findings": [], "overall": {"teaches_at_reference_depth": "partly",
                                                 "recommendation": "revise", "summary": "Needs a safer prompt"},
        }
        self.assertEqual(list(jsonschema.Draft202012Validator(schema).iter_errors(review)), [])


if __name__ == "__main__":
    unittest.main()
