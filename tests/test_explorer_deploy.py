"""An explorer is deployed to the TEST tab only when its numbers are right, with its contract and its evidence; a hand-written page is kept and said to be unchecked."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import sys
import unittest
from unittest import mock
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import build_test_site, deploy_test  # noqa: E402
from Shared.tools import explorer_build as eb  # noqa: E402
from tests.test_explorer_build import SPEC  # noqa: E402
from tests.test_test_area import Fixture  # noqa: E402


class Deploy(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.cleanup)
        self.slug = self.fixture.slug
        self.folder = eb.INTERACTIVE_ROOT / self.slug
        self.folder.mkdir(parents=True)
        self.out = deploy_test.PUBLIC_TEST / "interactive" / self.slug
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.addCleanup(shutil.rmtree, self.out, True)
        self.brief = eb.Brief(self.fixture.manifest)

    def write_spec(self, change=None) -> Path:
        spec = copy.deepcopy(SPEC)
        spec.update(slug=self.slug, product=self.fixture.manifest.relative_to(REPO).as_posix())
        spec["target"]["question_ref"] = self.brief.brief["question_ref"]
        if change:
            change(spec)
        (self.folder / eb.SPEC_FILE).write_text(json.dumps(spec), encoding="utf-8")
        return self.folder

    def test_a_checked_spec_is_deployed_as_a_labelled_draft_with_its_contract_and_its_evidence(self):
        deploy_test.deploy_product(self.fixture.manifest)         # the product it returns to is deployed first
        receipt = deploy_test.deploy_interactive(self.write_spec())
        self.assertEqual((receipt["built_by"], receipt["machine_checked"], receipt["status"], receipt["accepted"]), ("EXPLORER_BUILDER", True, "DRAFT", False))
        self.assertEqual(sorted(receipt["files"]), ["explorer-contract.json", "explorer-evidence.json", "index.html"])
        for name in receipt["files"]:
            self.assertTrue((self.out / name).is_file(), name)
        self.assertEqual(receipt["toughest"]["question_ref"], self.brief.brief["question_ref"])
        self.assertIn(self.brief.brief["question_ref"], receipt["records"])
        self.assertEqual(receipt["gap_count"], 0, receipt["gaps"])
        self.assertEqual(receipt["checks"]["states_checked"], 81)

    def test_the_page_says_it_is_a_sandbox_draft_in_the_markup_and_links_back_to_the_question(self):
        deploy_test.deploy_product(self.fixture.manifest)
        deploy_test.deploy_interactive(self.write_spec())
        page = (self.out / "index.html").read_text(encoding="utf-8")
        self.assertIn('data-g9-test="sandbox-draft"', page)
        self.assertIn("data-g9-test-banner", page)
        self.assertIn("<title>TEST draft · ", page)
        question = self.brief.brief["question_ref"]
        self.assertIn(f'href="../../products/{self.slug}/core2.html#{question}"', page)
        self.assertTrue((deploy_test.PUBLIC_TEST / "products" / self.slug / "core2.html").is_file())

    def test_without_the_product_there_is_nothing_to_link_to_and_the_page_says_so(self):
        receipt = deploy_test.deploy_interactive(self.write_spec())
        self.assertEqual(receipt["links"], {"question": None, "concept": None})
        self.assertIn("not deployed yet", (self.out / "index.html").read_text(encoding="utf-8"))

    def test_the_contract_is_the_standards_own_schema_and_claims_no_audit(self):
        receipt = deploy_test.deploy_interactive(self.write_spec())
        contract = json.loads((self.out / "explorer-contract.json").read_text(encoding="utf-8"))
        self.assertEqual(eb.contract_findings(contract), [])
        self.assertEqual(contract["conformance_status"], "IMPLEMENTATION_PARTIAL")
        self.assertEqual((contract["quality_audit"]["audit_status"], contract["quality_audit"]["audit_provenance"]["mode"]), ("NOT_RUN", "NOT_RUN"))
        self.assertIn("not eligible for canonical GCDR certification", contract["scope_contract"]["certification_scope"])
        self.assertEqual(contract["delivery_profile"], {"profile": "SINGLE_FILE_OFFLINE", "artifact_locator": f"public/test/interactive/{self.slug}/index.html",
                                                       "remote_dependencies_declared": []})
        self.assertEqual(contract["exit_evidence"]["rejoin_step_ref"], self.brief.brief["question_ref"])
        self.assertEqual(receipt["design_contract"], {"file": "explorer-contract.json", "conformance_status": "IMPLEMENTATION_PARTIAL", "audit_status": "NOT_RUN"})

    def test_the_evidence_is_what_the_build_computed_and_says_what_it_did_not_check(self):
        deploy_test.deploy_interactive(self.write_spec())
        evidence = json.loads((self.out / "explorer-evidence.json").read_text(encoding="utf-8"))
        self.assertEqual(evidence["states_checked"], 81)
        self.assertEqual(evidence["observations"], ["sometimes", "always", "always", "never"])
        self.assertEqual(evidence["page_sha256"], json.loads((self.out / "interactive-receipt.json").read_text(encoding="utf-8"))["files"]["index.html"])
        self.assertTrue(any("audit" in line for line in evidence["not_checked_here"]))
        self.assertEqual(len(evidence["oracles"]), 3)

    def test_a_spec_with_a_wrong_number_is_refused_with_the_lines_that_say_where_and_nothing_is_written(self):
        folder = self.write_spec(lambda spec: spec["reconstruct"]["equation"].update(expr="v^2*sind(theta)/g"))
        with self.assertRaises(deploy_test.DeployError) as caught:
            deploy_test.deploy_interactive(folder)
        message = str(caught.exception)
        self.assertIn("1 error(s) in explorer.json; no page was written", message)
        self.assertIn("RECONSTRUCT reconstruct.equation.expr", message)
        self.assertIn("is not equal to 'R'", message)
        self.assertIn("explorer_build.py check", message)
        self.assertFalse(self.out.exists())

    def test_a_spec_for_another_question_than_the_toughest_is_refused(self):
        folder = self.write_spec(lambda spec: spec["target"].update(question_ref="Q-OWNER-FX-02"))
        with self.assertRaisesRegex(deploy_test.DeployError, "is not the toughest concept of the set"):
            deploy_test.deploy_interactive(folder)
        self.assertFalse(self.out.exists())

    def test_gaps_deploy_the_page_as_a_draft_and_are_reported_not_hidden(self):
        folder = self.write_spec(lambda spec: spec["predict"]["options"].pop())
        receipt = deploy_test.deploy_interactive(folder)
        self.assertEqual(receipt["gap_count"], 1)
        self.assertEqual(receipt["gaps"][0]["component"], "PREDICT")
        self.assertIn("2 options; the blueprint's reference page has 3", receipt["gaps"][0]["detail"])

    def test_the_deployments_page_says_how_the_page_was_made_and_what_it_was_built_for(self):
        deploy_test.deploy_product(self.fixture.manifest)
        deploy_test.deploy_interactive(self.write_spec(lambda spec: spec["predict"]["options"].pop()))
        page = build_test_site.deployments_page()
        self.assertIn("Built by the explorer builder from a spec", page)
        self.assertIn("Built for the toughest concept of the set: Q1", page)
        self.assertIn("The 1 gap(s): where the page is shallower than the blueprint asks", page)
        self.assertIn("design contract IMPLEMENTATION_PARTIAL, audit not run", page)
        self.assertIn(f"{self.slug}/explorer-evidence.json", page)

    def test_the_command_line_prints_what_was_built_for_and_how_many_positions_were_checked(self):
        deploy_test.deploy_product(self.fixture.manifest)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err), mock.patch.object(build_test_site, "write"):
            code = deploy_test.main(["interactive", str(self.write_spec(lambda spec: spec["predict"]["options"].pop())), "--no-mirror"])
        self.assertEqual(code, 0, err.getvalue())
        text = out.getvalue()
        self.assertIn(f"deployed interactive {self.slug}: 3 file(s), DRAFT, accepted=false", text)
        self.assertIn("built by the explorer builder for the toughest concept of the set, Q1", text)
        self.assertIn("81 positions of the sliders checked; 1 gap(s)", text)
        self.assertRegex(text, r"gap PREDICT\s+predict\.options: 2 options")

    def test_the_command_line_refuses_an_unchecked_spec_in_one_message_and_a_nonzero_status(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()), mock.patch.object(build_test_site, "write"):
            code = deploy_test.main(["interactive", str(self.write_spec(lambda spec: spec["context"].update(situation=""))), "--no-mirror"])
        self.assertEqual(code, 1)
        self.assertRegex(err.getvalue(), r"deploy_test: 1 error\(s\) in explorer.json; no page was written")
        self.assertIn("CONTEXT context.situation: is empty; write it", err.getvalue())


class HandWritten(unittest.TestCase):
    def setUp(self):
        self.slug = "hw-" + SPEC["slug"][:20]
        self.folder = eb.INTERACTIVE_ROOT / self.slug
        self.folder.mkdir(parents=True)
        self.out = deploy_test.PUBLIC_TEST / "interactive" / self.slug
        self.addCleanup(shutil.rmtree, self.folder, True)
        self.addCleanup(shutil.rmtree, self.out, True)
        (self.folder / "index.html").write_text('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width">'
                                               '<title>x</title></head><body><main><h1>x</h1></main></body></html>', encoding="utf-8")
        (self.folder / "interactive.json").write_text(json.dumps({
            "schema": deploy_test.INTERACTIVE_SCHEMA, "slug": self.slug, "title": "A sandbox", "purpose": "play",
            "records": ["Q-1"], "blueprint_ref": "NONE", "status": "DRAFT"}), encoding="utf-8")

    def test_a_hand_written_page_is_still_a_draft_and_is_flagged_as_unchecked(self):
        receipt = deploy_test.deploy_interactive(self.folder)
        self.assertEqual((receipt["built_by"], receipt["machine_checked"], receipt["accepted"]), ("HAND_WRITTEN", False, False))
        self.assertNotIn("toughest", receipt)
        page = build_test_site.deployments_page()
        self.assertIn("Written by hand: nothing in it is machine-checked", page)

    def test_the_command_line_says_so_and_points_at_the_explorer_spec(self):
        err = io.StringIO()
        with contextlib.redirect_stderr(err), contextlib.redirect_stdout(io.StringIO()), mock.patch.object(build_test_site, "write"):
            code = deploy_test.main(["interactive", str(self.folder), "--no-mirror"])
        self.assertEqual(code, 0)
        self.assertIn("written by hand, so nothing in it is machine-checked", err.getvalue())
        self.assertIn("explorer_build.py new", err.getvalue())


if __name__ == "__main__":
    unittest.main()
