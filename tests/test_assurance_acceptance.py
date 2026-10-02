"""The acceptance gate is REQUIRED: a product is accepted only when the assurance of it, as staged, is ELIGIBLE, counting the Owner's recorded waivers.

These tests stage a real product (the renderer's own pages for phy-kin-2d-motion) in the git-ignored publication/ area and take it through the gate. The PDFs the pages
link are not printed here (that needs a browser), so a test that wants the links to resolve puts a file where each PDF belongs; the assurance does not read a PDF, and
acceptance checks the PDFs itself (render_core.pdf_publication_problems).
"""
from __future__ import annotations

import io
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.assurance import aggregate, product, verifiers  # noqa: E402
from Shared.contracts import ContractError  # noqa: E402
from Shared.tools import accept_product  # noqa: E402

SLUG = "phy-kin-2d-motion"
MANIFEST = REPO / "products" / "physics" / f"{SLUG}.manifest.json"
STAGED = REPO / "publication" / "products" / "physics" / SLUG
WORK = REPO / "build" / "assurance" / SLUG
RELATIVE_PDF = re.compile(r'href="((?![a-z]+:|//)[^"#]+\.pdf)"')
WAIVED = {"ACCESSIBILITY", "ANSWERABILITY", "PROJECTION_COMPLETENESS", "REASONING_VALIDITY", "RESPONSIVE_LAYOUT", "SELF_CONTAINMENT", "SOURCE_INTEGRITY"}


class Gate(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.had_staging = STAGED.exists()
        if cls.had_staging:
            raise unittest.SkipTest("publication/ already holds a staged render of this product; not touching it")
        STAGED.mkdir(parents=True)
        done = subprocess.run([sys.executable, str(REPO / "Shared/tools/render_core.py"), "build", "--manifest", str(MANIFEST), "--out", str(STAGED), "--mode", "PAGES"],
                              cwd=REPO, capture_output=True, text=True)
        if done.returncode:
            shutil.rmtree(STAGED, ignore_errors=True)
            raise RuntimeError(done.stderr[-500:])
        cls.pristine = Path(tempfile.mkdtemp())
        shutil.copytree(STAGED, cls.pristine / "staged")

    @classmethod
    def tearDownClass(cls):
        if not cls.had_staging:
            shutil.rmtree(STAGED, ignore_errors=True)
            shutil.rmtree(cls.pristine, ignore_errors=True)
            shutil.rmtree(WORK, ignore_errors=True)

    def setUp(self):
        shutil.rmtree(STAGED, ignore_errors=True)
        shutil.copytree(self.pristine / "staged", STAGED)

    def print_pdfs(self):
        """A stand-in file where each relative PDF link of a staged page points (a link to a source on another host is a citation, not a PDF to print)."""
        for page in STAGED.glob("*.html"):
            for link in set(RELATIVE_PDF.findall(page.read_text(encoding="utf-8"))):
                (STAGED / link).write_bytes(b"%PDF-1.4 a stand-in; acceptance checks the real ones")

    def decide(self):
        return product.assure_staged(SLUG, REPO)

    def test_the_policy_is_required(self):
        gate = aggregate.load_policies(["learner-release-default"])[0]["acceptance_gate"]
        self.assertEqual(gate, "REQUIRED")

    def test_a_staged_product_with_everything_it_can_be_checked_for_is_eligible_with_exactly_the_waived_types_open(self):
        self.print_pdfs()
        decision = self.decide()
        self.assertEqual((decision["status"], decision["missing"], decision["problems"]), ("ELIGIBLE", [], []))
        self.assertEqual({w["type"] for w in decision["waived"]}, WAIVED, "what the decision rests on the Owner's waiver for, and nothing else")
        self.assertTrue((WORK / "bundle.json").is_file() and (WORK / "eligibility.json").is_file())

    def test_a_link_to_a_pdf_that_was_not_printed_makes_it_ineligible_and_nothing_else_does(self):
        decision = self.decide()
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertEqual({(m["type"], m["reason"]) for m in decision["missing"]}, {("LINK_INTEGRITY", "FAIL")}, "the one need that is not met is the one that failed")
        self.assertEqual({f["code"] for f in decision["reviewable_findings"] if f["severity"] == "S1"}, {"LINKS_RESOLVE"})

    def test_a_page_edited_after_it_was_rendered_is_refused(self):
        self.print_pdfs()
        page = STAGED / "core1.html"
        page.write_text(page.read_text(encoding="utf-8").replace("<h1", "<h1 data-edited", 1), encoding="utf-8")
        decision = self.decide()
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("RECEIPT_MISMATCH", {f["code"] for f in decision["reviewable_findings"]})

    def test_a_remote_script_in_a_staged_page_is_refused(self):
        self.print_pdfs()
        page = STAGED / "core1.html"
        page.write_text(page.read_text(encoding="utf-8").replace("</head>", '<script src="https://cdn.example/x.js"></script></head>', 1), encoding="utf-8")
        decision = self.decide()
        self.assertEqual(decision["status"], "INELIGIBLE")
        self.assertIn("REMOTE_RUNTIME", {f["code"] for f in decision["reviewable_findings"]})

    def test_the_waiver_does_not_cover_a_type_that_has_a_checker_and_fails(self):
        self.print_pdfs()
        waivers = aggregate.default_waivers()
        waivers["NETWORK_POLICY@*"] = {"type": "NETWORK_POLICY", "subject": "*", "reason": "a waiver for a type that does have a checker", "approval_ref": "nobody"}
        page = STAGED / "core1.html"
        page.write_text(page.read_text(encoding="utf-8").replace("</head>", '<script src="https://cdn.example/x.js"></script></head>', 1), encoding="utf-8")
        self.assertEqual(product.assure_staged(SLUG, REPO, waivers)["status"], "INELIGIBLE")

    def test_nothing_staged_is_not_assured(self):
        shutil.rmtree(STAGED)
        with self.assertRaises(ContractError) as ctx:
            self.decide()
        self.assertEqual(ctx.exception.code, "PRODUCT_NOT_STAGED")

    def test_accept_product_refuses_without_a_bundle_and_goes_on_with_a_good_one(self):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            allowed, record = accept_product._release_decision(SLUG, None, REPO)
        self.assertFalse(allowed, err.getvalue())
        self.assertEqual(record["status"], "INELIGIBLE")
        self.print_pdfs()
        with redirect_stdout(out), redirect_stderr(err):
            allowed, record = accept_product._release_decision(SLUG, None, REPO)
        self.assertTrue(allowed, err.getvalue())
        self.assertIn("waived   RESPONSIVE_LAYOUT", out.getvalue())

    def test_a_product_that_is_not_staged_is_refused_by_the_gate_with_a_reason(self):
        shutil.rmtree(STAGED)
        err = io.StringIO()
        with redirect_stdout(io.StringIO()), redirect_stderr(err):
            allowed, record = accept_product._release_decision(SLUG, None, REPO)
        self.assertEqual((allowed, record), (False, None))
        self.assertIn("nothing is staged", err.getvalue())


class PageSets(unittest.TestCase):
    """What a set of pages is and is not judged for, without a product."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.tmp, True)
        (self.tmp / "standalone").mkdir()
        (self.tmp / "standalone" / "a.html").write_text(
            '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>t</title></head>'
            "<body><h1>t</h1></body></html>", encoding="utf-8")

    def subject(self):
        return aggregate.projection_subjects(["standalone=standalone"], self.tmp)[0]

    def test_search_and_deployment_are_not_about_a_set_of_pages_and_the_receipt_is_claimed_only_where_there_is_one(self):
        out = verifiers.projection_extras(self.subject(), self.tmp)
        self.assertEqual({t: v.outcome for t, v in out.items()}, {"SEARCH_MEMBERSHIP": "NOT_APPLICABLE", "SEARCH_RETRIEVABILITY": "NOT_APPLICABLE",
                                                                  "DEPLOYMENT_INTEGRITY": "NOT_APPLICABLE"})
        self.assertNotIn("PROJECTION_INTEGRITY", out, "no receipt, nothing claimed, nothing proved")

    def test_the_run_writes_those_verdicts_as_evidence(self):
        result = verifiers.run(self.tmp, [], ["standalone=standalone"], self.tmp / "evidence")
        by_type = {e["assurance_type"]: e["outcome"] for e in result.evidence}
        self.assertEqual(by_type["SEARCH_MEMBERSHIP"], "NOT_APPLICABLE")
        self.assertNotIn("PROJECTION_INTEGRITY", by_type)
        self.assertEqual(json.loads(next((self.tmp / "evidence").glob("*.json")).read_text())["schema"], "assurance-evidence/v1")


if __name__ == "__main__":
    unittest.main()
