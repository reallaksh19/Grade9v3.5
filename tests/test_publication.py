"""Owner decision publishes one exact render; building cannot mutate public pages."""
from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from Shared.tools import accept_product, build_products, quality_gate

REPO = Path(__file__).resolve().parents[1]


def fixture(repo: Path, *, review: bool = False, cited: bool = False) -> tuple[Path, str]:
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
    h = hashlib.sha256()
    for name in ("core1.html", "index.html"):
        h.update(name.encode() + b"\0" + neutral.encode())
    digest = h.hexdigest()[:16]
    for name in ("core1.html", "index.html"):
        (out / name).write_text(neutral.replace("g9-digest-pending", digest))
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
