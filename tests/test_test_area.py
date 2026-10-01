"""The TEST sandbox: a real subject, labelled drafts only, never accepted, never in the official bank."""
from __future__ import annotations

import contextlib
import copy
import io
import json
import re
import shutil
import sys
import tempfile
import unittest
import uuid
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import (accept_product, build_question_bank_web, build_test_site, check_subjects, deploy_test,  # noqa: E402
                          owner_bank, product_manifest, render_core)

PKG = "tests/fixtures/render/thin-kin-2d-motion.v1.json"
OFFICIAL_BANK = "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
OWNER_CUSTODY = {"authority_class": "OWNER_SUPPLIED_RAW_INPUT", "intake_ref": "sha256:fixture", "wording_custody": "VERBATIM"}


def owner_questions(package: dict, count: int = 2) -> list[dict]:
    """Official-bank questions for the fixture package's capabilities, rewritten as owner-supplied ones."""
    bank = json.loads((REPO / OFFICIAL_BANK).read_text(encoding="utf-8"))
    caps = {c["id"] for c in package["capabilities"]}
    rows = copy.deepcopy([q for q in bank["questions"] if q.get("primary_capability_ref") in caps][:count])
    for index, row in enumerate(rows, 1):
        row["extensions"]["grade9v3:source_custody"] = dict(OWNER_CUSTODY, text_sha256=owner_bank.text_digest(row["stem"]))
        row["id"] = f"Q-OWNER-FX-{index:02d}"
        row["original_identifier"] = f"Q{index}"
    return rows


class Fixture:
    """A TEST product built from the thin Physics fixture, in a scratch directory under TEST/."""

    def __init__(self):
        self.key = "fx" + uuid.uuid4().hex[:8]
        self.root = REPO / "TEST" / f"_{self.key}"
        self.slug = f"product-{self.key}"
        self.root.mkdir(parents=True)
        package = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        package["subject"] = "TEST"
        (self.root / "package.v1.json").write_text(json.dumps(package), encoding="utf-8")
        bank = {"schema_version": owner_bank.SCHEMA_VERSION, "bank_id": self.key, "questions": owner_questions(package)}
        (self.root / "owner.bank.json").write_text(json.dumps(bank), encoding="utf-8")
        self.manifest = self.root / "product.manifest.json"
        refresh = product_manifest.derive(f"TEST/_{self.key}/package.v1.json", [f"TEST/_{self.key}/owner.bank.json"],
                                          self.slug, "../../../index.html")
        self.manifest.write_text(json.dumps(refresh), encoding="utf-8")

    def cleanup(self):
        shutil.rmtree(self.root, ignore_errors=True)
        shutil.rmtree(deploy_test.PUBLIC_TEST / "products" / self.slug, ignore_errors=True)


class TestSubject(unittest.TestCase):
    def test_test_is_a_real_subject_that_declares_a_contract_and_adds_no_finding(self):
        report = check_subjects.run()
        row = next(r for r in report["subjects"] if r["subject"] == "TEST")
        self.assertEqual(row["state"], "CONTRACT_ONLY")
        self.assertEqual(row["findings"], [])

    def test_the_package_schema_accepts_test_and_the_official_bank_is_unchanged(self):
        schema = json.loads((REPO / "Shared/library/package.schema.json").read_text(encoding="utf-8"))
        self.assertIn("TEST", schema["properties"]["subject"]["enum"])
        bank_schema = json.loads((REPO / "Shared/library/competitive-exam-bank.schema.json").read_text(encoding="utf-8"))
        self.assertEqual(bank_schema["$defs"]["source_custody"]["properties"]["authority_class"]["enum"],
                         ["OFFICIAL_EXAM_ORGANIZER_ARCHIVE"])


class TestPages(unittest.TestCase):
    def test_committed_pages_are_what_the_generator_writes(self):
        self.assertEqual(build_test_site.check(), [])

    def test_every_test_page_says_it_is_a_sandbox_draft(self):
        pages = sorted((REPO / "public" / "test").rglob("*.html"))
        self.assertGreaterEqual(len(pages), 4)
        for page in pages:
            text = page.read_text(encoding="utf-8")
            self.assertIn('data-g9-test="sandbox-draft"', text, page)
            self.assertIn("data-g9-test-banner", text, page)
            self.assertIn("data-g9-shell", text, f"{page}: the site audit needs the shell marker")
            self.assertIn("not accepted", text, page)
            self.assertNotRegex(text, r"https?://", f"{page}: a TEST page must work offline")
        for receipt in (REPO / "public" / "test").rglob("*receipt.json"):
            self.assertIs(json.loads(receipt.read_text(encoding="utf-8"))["accepted"], False, receipt)

    def test_the_atlas_is_bound_to_test_and_keeps_no_trace_of_laws_of_motion(self):
        atlas = (REPO / "public/test/atlas/index.html").read_text(encoding="utf-8")
        self.assertIn("subjects.TEST", atlas)
        for leftover in ("MATRIX-PHY-NLM-FIRST-LAW", "Laws of Motion", "phy-nlm-first-law", "NLM Topic Atlas"):
            self.assertNotIn(leftover, atlas)
        self.assertNotIn("\\n<script", atlas, "the template's literal backslash-n is fixed in the copy")

    def test_the_atlas_generator_fails_loudly_when_its_template_changes_shape(self):
        original = build_test_site.ATLAS_TRANSFORM
        transform = json.loads(original.read_text(encoding="utf-8"))
        template = (REPO / transform["template"]).read_text(encoding="utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            changed = Path(tmp) / "index.html"
            changed.write_text(template.replace("<body>", "<body class='x'>"), encoding="utf-8")
            altered = Path(tmp) / "transform.json"
            altered.write_text(json.dumps({**transform, "template": str(changed)}), encoding="utf-8")
            build_test_site.ATLAS_TRANSFORM = altered
            try:
                with self.assertRaisesRegex(ValueError, "template changed"):
                    build_test_site.atlas_page()
            finally:
                build_test_site.ATLAS_TRANSFORM = original

    def test_the_atlas_header_reaches_the_portal_and_every_test_page(self):
        atlas = (REPO / "public/test/atlas/index.html").read_text(encoding="utf-8")
        header = atlas[atlas.index("<header class=\"g9-shell\""):atlas.index("</header>")]
        for href in ("../../index.html", "../../test/index.html", "../../test/atlas/index.html",
                     "../../test/rungs/index.html", "../../test/deployments/index.html"):
            self.assertIn(f'href="{href}"', header)

    def test_the_tab_is_in_the_shared_header_and_on_the_hubs_and_the_site_can_reach_test(self):
        header = (REPO / "public/js/site-header.js").read_text(encoding="utf-8")
        self.assertIn("root+'test/index.html'", header)
        for page, href in (("index.html", "test/index.html"), ("physics/index.html", "../test/index.html"),
                           ("chemistry/index.html", "../test/index.html"), ("mathematics/index.html", "../test/index.html")):
            text = (REPO / "public" / page).read_text(encoding="utf-8")
            self.assertIn(f'href="{href}" class="test-link" data-site-test>TEST</a>', text, page)

    def test_test_is_not_a_question_bank_subject(self):
        projection = build_question_bank_web.build(REPO)
        self.assertNotIn("TEST", {q.get("subject") for q in projection["questions"]})
        self.assertEqual(len(projection["questions"]), 77)


class TestDeploy(unittest.TestCase):
    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.cleanup)

    def test_a_test_product_deploys_as_a_labelled_draft_and_shows_the_owner_questions(self):
        receipt = deploy_test.deploy_product(self.fixture.manifest)
        out = deploy_test.PUBLIC_TEST / "products" / self.fixture.slug
        self.assertIs(receipt["accepted"], False)
        self.assertEqual(receipt["subject"], "TEST")
        self.assertEqual(receipt["selection_counts"]["core2"], 2)
        self.assertTrue(receipt["draft"])
        core2 = (out / "core2.html").read_text(encoding="utf-8")
        self.assertIn("<h2>Q1</h2>", core2)
        self.assertIn("Owner-supplied question, verbatim", core2)
        self.assertNotIn("Source unverified", core2)
        identity = re.findall(r'data-g9-block="source_identity">(.*?)</div>', core2, flags=re.S)
        self.assertEqual(len(identity), 2, "one identity block per owner question")
        for block in identity:
            self.assertNotRegex(block, r"JEE|IIT|NTA|Official past paper|20\d\d")
        for name, sha in receipt["pages"].items():
            page = (out / name).read_text(encoding="utf-8")
            self.assertIn('data-g9-test="sandbox-draft"', page)
            self.assertIn("data-g9-test-banner", page)
            self.assertEqual(deploy_test._sha(page.encode("utf-8")), sha)
        self.assertEqual(json.loads((out / "deploy-receipt.json").read_text(encoding="utf-8"))["render_digest"],
                         receipt["render_digest"])

    def test_the_hub_and_deployments_pages_report_the_deployment_without_calling_it_done(self):
        deploy_test.deploy_product(self.fixture.manifest)
        pages = build_test_site.render_all()
        self.assertIn(self.fixture.slug, pages["deployments/index.html"])
        self.assertIn("accepted: no", pages["deployments/index.html"])
        self.assertIn("2 record(s) selected", pages["index.html"])
        self.assertNotRegex(pages["index.html"] + pages["deployments/index.html"], r"(?i)\b(complete|completed|published|approved|ready)\b")

    def test_only_test_products_made_of_test_records_can_be_deployed(self):
        manifest = json.loads(self.fixture.manifest.read_text(encoding="utf-8"))
        cases = {
            "another subject": (dict(manifest, subject="Physics"), self.fixture.manifest, "only TEST products"),
            "records outside TEST": (dict(manifest, package_refs=[PKG]), self.fixture.manifest, "outside TEST/"),
            "a bad slug": (dict(manifest, product_id="Bad Slug!"), self.fixture.manifest, "must match"),
        }
        for name, (changed, path, expected) in cases.items():
            with self.subTest(name):
                path.write_text(json.dumps(changed), encoding="utf-8")
                with self.assertRaisesRegex(deploy_test.DeployError, expected):
                    deploy_test.deploy_product(path)
        with tempfile.TemporaryDirectory() as tmp:
            elsewhere = Path(tmp) / "m.json"
            elsewhere.write_text(json.dumps(manifest), encoding="utf-8")
            with self.assertRaisesRegex(deploy_test.DeployError, "must live under TEST/"):
                deploy_test.deploy_product(elsewhere)
        self.assertFalse((deploy_test.PUBLIC_TEST / "products" / self.fixture.slug).exists(), "a refused product leaves nothing")

    def test_a_selection_the_renderer_rejects_is_one_line(self):
        manifest = json.loads(self.fixture.manifest.read_text(encoding="utf-8"))
        manifest["selection"]["core2"] = manifest["selection"]["core2a"][:1]  # a package question in the Core2 selection
        self.fixture.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaisesRegex(deploy_test.DeployError, "selection rejected: PRODUCT_SELECTION_WRONG_AUTHORITY"):
            deploy_test.deploy_product(self.fixture.manifest)

    def test_a_package_with_several_schema_problems_reports_them_together(self):
        package_path = self.fixture.root / "package.v1.json"
        package = json.loads(package_path.read_text(encoding="utf-8"))
        package["resources"], package["buckets"], package["microtopics"] = [], [], []
        package["capabilities"][0]["acceptance_status"] = "UNREVIEWED"
        package_path.write_text(json.dumps(package), encoding="utf-8")
        with self.assertRaises(ValueError) as caught:
            deploy_test.deploy_product(self.fixture.manifest)
        message = str(caught.exception)
        self.assertIn("PRODUCT_STRUCTURE_INVALID", message)
        for needle in ("buckets:", "microtopics:", "resources:", "acceptance_status:"):
            self.assertIn(needle, message)
        self.assertFalse((deploy_test.PUBLIC_TEST / "products" / self.fixture.slug).exists(), "a refused product leaves nothing")

    def test_an_empty_role_is_reported_in_the_receipt(self):
        manifest = json.loads(self.fixture.manifest.read_text(encoding="utf-8"))
        manifest["selection"]["core2"] = []
        self.fixture.manifest.write_text(json.dumps(manifest), encoding="utf-8")
        receipt = deploy_test.deploy_product(self.fixture.manifest)
        self.assertIn("CORE2", receipt["empty_roles"])
        self.assertIn("Roles with no records selected: CORE2", build_test_site.deployments_page())


class TestInteractive(unittest.TestCase):
    META = {"schema": deploy_test.INTERACTIVE_SCHEMA, "title": "Vector sandbox", "purpose": "add two vectors by dragging heads",
            "records": ["MIC-FX-1"], "blueprint_ref": "NONE", "status": "DRAFT"}
    HTML = '<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>x</title></head><body><main>hi</main></body></html>'

    def setUp(self):
        self.slug = "ix" + uuid.uuid4().hex[:8]
        self.source = REPO / "TEST" / "interactive" / self.slug
        self.source.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, self.source, True)
        self.addCleanup(shutil.rmtree, deploy_test.PUBLIC_TEST / "interactive" / self.slug, True)
        self.addCleanup(lambda: (REPO / "TEST" / "interactive").exists() and not any((REPO / "TEST" / "interactive").iterdir())
                        and (REPO / "TEST" / "interactive").rmdir())
        self.write()

    def write(self, html: str | None = None, **meta):
        (self.source / "index.html").write_text(html if html is not None else self.HTML, encoding="utf-8")
        (self.source / "interactive.json").write_text(json.dumps({**self.META, "slug": self.slug, **meta}), encoding="utf-8")

    def test_an_interactive_page_deploys_as_a_labelled_draft_with_a_receipt(self):
        receipt = deploy_test.deploy_interactive(self.source)
        page = (deploy_test.PUBLIC_TEST / "interactive" / self.slug / "index.html").read_text(encoding="utf-8")
        self.assertIn("data-g9-test-banner", page)
        self.assertIn('data-g9-test="sandbox-draft"', page)
        self.assertIn("data-g9-shell", page)
        self.assertIn('href="../../../index.html">Portal</a>', page)
        self.assertIs(receipt["accepted"], False)
        self.assertEqual(receipt["blueprint_ref"], "NONE")
        self.assertIn(self.slug, build_test_site.deployments_page())

    def test_an_interactive_page_may_link_its_own_files(self):
        (self.source / "app.js").write_text("console.log('x')", encoding="utf-8")
        self.write(self.HTML.replace("</body>", '<script src="app.js"></script></body>'))
        receipt = deploy_test.deploy_interactive(self.source)
        self.assertEqual(sorted(receipt["files"]), ["app.js", "index.html", "interactive.json"])

    def test_a_page_with_no_html_element_cannot_be_stamped(self):
        with self.assertRaisesRegex(deploy_test.DeployError, "exactly one html element"):
            deploy_test.stamp("<body>hi</body>", "../../index.html")

    def test_what_an_interactive_page_may_not_be(self):
        cases = {
            "loads another host": (self.HTML.replace("<title>", '<script src="https://cdn.example.com/x.js"></script><title>'), {}, "another host"),
            "no viewport": (self.HTML.replace('<meta name="viewport" content="width=device-width,initial-scale=1">', ""), {}, "viewport"),
            "links to a file that is not there": (self.HTML.replace("<main>", '<link rel="stylesheet" href="style.css"><main>'), {}, "links to style.css"),
            "a fragment, not a page": ("<main>hi</main>", {}, "viewport"),
            "not a draft": (None, {"status": "FINAL"}, "status must be DRAFT"),
            "no purpose": (None, {"purpose": ""}, "missing"),
            "no records": (None, {"records": []}, "missing"),
            "slug differs from folder": (None, {"slug": "other"}, "must equal the directory name"),
        }
        for name, (html, meta, expected) in cases.items():
            with self.subTest(name):
                self.write(html, **meta)
                (self.source / "interactive.json").write_text(
                    json.dumps({**self.META, "slug": meta.get("slug", self.slug), **{k: v for k, v in meta.items() if k != "slug"}}),
                    encoding="utf-8")
                with self.assertRaisesRegex(deploy_test.DeployError, expected):
                    deploy_test.deploy_interactive(self.source)
        self.write()
        (self.source / "payload.exe").write_bytes(b"x")
        with self.assertRaisesRegex(deploy_test.DeployError, "not allowed"):
            deploy_test.deploy_interactive(self.source)

    def test_the_source_must_live_under_test_interactive(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(deploy_test.DeployError, "under TEST/interactive/"):
                deploy_test.deploy_interactive(Path(tmp))


class TestNeverAccepted(unittest.TestCase):
    def test_accept_product_refuses_a_test_product(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            (repo / "products" / "test").mkdir(parents=True)
            (repo / "products" / "test" / "fx.manifest.json").write_text(json.dumps({"subject": "TEST"}), encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "TEST is a sandbox subject"):
                accept_product.accept("fx", repo=repo, confirm=lambda _prompt: "y")


class TestOwnerBank(unittest.TestCase):
    def bank(self, **custody):
        package = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        rows = owner_questions(package, 1)
        rows[0]["extensions"]["grade9v3:source_custody"].update(custody)
        return {"schema_version": owner_bank.SCHEMA_VERSION, "bank_id": "b", "questions": rows}

    def test_a_good_owner_bank_passes(self):
        self.assertEqual(owner_bank.check(self.bank()), [])

    def test_an_owner_question_cannot_carry_an_invented_exam_identity(self):
        problems = owner_bank.check(self.bank(exam="JEE Main", year=2019, paper="P1"))
        self.assertTrue(any("official-exam fields" in p and "exam" in p for p in problems), problems)

    def test_the_other_ways_an_owner_bank_can_be_wrong(self):
        self.assertTrue(any("authority_class" in p for p in owner_bank.check(self.bank(authority_class="OFFICIAL_EXAM_ORGANIZER_ARCHIVE"))))
        self.assertTrue(any("intake_ref" in p for p in owner_bank.check(self.bank(intake_ref=""))))
        self.assertTrue(any("VERBATIM" in p for p in owner_bank.check(self.bank(wording_custody="FAITHFUL_NON_VERBATIM_RESTATEMENT"))))
        self.assertTrue(any("schema_version" in p for p in owner_bank.check({"questions": []})))

    def test_no_owner_question_is_in_an_official_exam_bank(self):
        for path in REPO.glob("*/library/exam-bank/*.json"):
            text = path.read_text(encoding="utf-8")
            self.assertNotIn("OWNER_SUPPLIED_RAW_INPUT", text, path)
            self.assertNotIn(owner_bank.SCHEMA_VERSION, text, path)

    def test_the_renderer_refuses_a_malformed_owner_bank_with_one_line_and_an_owner_bank_in_exam_bank(self):
        fixture = Fixture()
        self.addCleanup(fixture.cleanup)
        bank_path = fixture.root / "owner.bank.json"
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
        bank["questions"][0]["extensions"]["grade9v3:source_custody"]["exam"] = "JEE Main"
        bank_path.write_text(json.dumps(bank), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, r"PRODUCT_STRUCTURE_INVALID: .*official-exam fields"):
            render_core.build(fixture.manifest, "PAGES")


class TestOwnerBankFromIntake(unittest.TestCase):
    """The Owner's words are kept exactly: copied from the intake, digested, and checked against both."""
    INTAKE = {"status": "RESEARCH_AND_AUTHOR", "errors": [], "intake_digest": "sha256:aaa",
              "inputs": {"questions": [{"id": "q1", "label": "1", "text": "Given p = (2, \u22121) and q = (\u22125, 3), find p + q"},
                                       {"id": "q2", "label": "2", "text": "A boat points due east at 4 m/s."}]}}

    def bank(self, fill=True):
        bank = owner_bank.new(self.INTAKE, "vec")
        if fill:
            for row in bank["questions"]:
                row["answer"] = {"summary": "an answer", "reasoning": ["a step"]}
                row["primary_capability_ref"] = "CAP-X"
        return bank

    def test_new_copies_the_text_exactly_and_records_where_it_came_from(self):
        bank = self.bank(fill=False)
        self.assertEqual([q["stem"] for q in bank["questions"]], [q["text"] for q in self.INTAKE["inputs"]["questions"]])
        self.assertEqual([q["id"] for q in bank["questions"]], ["OWN-VEC-01", "OWN-VEC-02"])
        self.assertEqual([q["original_identifier"] for q in bank["questions"]], ["Q1", "Q2"])
        custody = bank["questions"][0]["extensions"]["grade9v3:source_custody"]
        self.assertEqual(custody, {"authority_class": "OWNER_SUPPLIED_RAW_INPUT", "intake_ref": "q1", "wording_custody": "VERBATIM",
                                   "text_sha256": owner_bank.text_digest(self.INTAKE["inputs"]["questions"][0]["text"])})
        self.assertEqual(bank["intake_digest"], "sha256:aaa")

    def test_the_skeleton_says_what_is_left_to_fill_and_a_filled_bank_passes(self):
        problems = owner_bank.check(self.bank(fill=False), intake=self.INTAKE)
        self.assertEqual(sum("answer.summary is required" in p for p in problems), 2, problems)
        self.assertEqual(sum("primary_capability_ref is required" in p for p in problems), 2, problems)
        self.assertEqual(owner_bank.check(self.bank(), intake=self.INTAKE), [])

    def test_tidying_a_stem_is_caught_even_without_the_intake(self):
        bank = self.bank()
        bank["questions"][0]["stem"] = bank["questions"][0]["stem"].replace("\u2212", "-")
        problems = owner_bank.check(bank)
        self.assertTrue(any("not the text the Owner supplied" in p for p in problems), problems)

    def test_editing_the_stem_and_its_digest_together_is_caught_against_the_intake(self):
        bank = self.bank()
        row = bank["questions"][1]
        row["stem"] = "A boat heads east at 4 m/s."
        row["extensions"]["grade9v3:source_custody"]["text_sha256"] = owner_bank.text_digest(row["stem"])
        self.assertEqual(owner_bank.check(bank), [], "the digest alone cannot tell")
        problems = owner_bank.check(bank, intake=self.INTAKE)
        self.assertTrue(any("not the intake's text for q2" in p for p in problems), problems)

    def test_a_dropped_question_and_a_different_intake_are_reported(self):
        bank = self.bank()
        bank["questions"].pop()
        self.assertTrue(any("intake question q2" in p and "not in the bank" in p for p in owner_bank.check(bank, intake=self.INTAKE)))
        other = dict(self.INTAKE, intake_digest="sha256:bbb")
        self.assertTrue(any("different intake" in p for p in owner_bank.check(self.bank(), intake=other)))
        ghost = self.bank()
        ghost["questions"][0]["extensions"]["grade9v3:source_custody"]["intake_ref"] = "q9"
        self.assertTrue(any("not a question id in the intake" in p for p in owner_bank.check(ghost, intake=self.INTAKE)))

    def test_a_bank_with_no_digest_is_refused_and_says_how_to_make_one(self):
        bank = self.bank()
        del bank["questions"][0]["extensions"]["grade9v3:source_custody"]["text_sha256"]
        self.assertTrue(any("owner_bank.py new" in p for p in owner_bank.check(bank)))

    def test_new_refuses_what_it_cannot_keep_verbatim(self):
        for name, intake, bank_id, expected in (
                ("errors", dict(self.INTAKE, status="INVALID_REQUEST", errors=["subject is required"]), "vec", "the intake has errors"),
                ("no questions", {"inputs": {"questions": []}}, "vec", "no questions"),
                ("no text", {"inputs": {"questions": [{"id": "q1", "text": " "}]}}, "vec", "nothing to keep verbatim"),
                ("bad id", self.INTAKE, "Bad Id", "must match")):
            with self.subTest(name), self.assertRaisesRegex(ValueError, expected):
                owner_bank.new(intake, bank_id)

    def test_the_command_writes_only_under_test_question_bank_and_never_over_an_existing_bank(self):
        intake_dir = Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, intake_dir, True)
        intake = intake_dir / "intake.json"
        intake.write_text(json.dumps(self.INTAKE), encoding="utf-8")
        name = "cli" + uuid.uuid4().hex[:8]
        out = REPO / "TEST" / "question-bank" / f"{name}.json"
        self.addCleanup(lambda: out.unlink() if out.exists() else None)
        argv = ["new", "--intake", str(intake), "--bank-id", name, "--out", str(out)]

        def run(arguments):
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                return owner_bank.main(arguments)

        self.assertEqual(run(["new", "--intake", str(intake), "--bank-id", name, "--out", str(intake_dir / "x.json")]), 1)
        self.assertFalse((intake_dir / "x.json").exists())
        self.assertEqual(run(argv), 0)
        written = json.loads(out.read_text(encoding="utf-8"))
        self.assertEqual(len(written["questions"]), 2)
        written["questions"][0]["answer"] = {"summary": "kept"}
        out.write_text(json.dumps(written), encoding="utf-8")
        self.assertEqual(run(argv), 1, "a second run must not erase the answers")
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["questions"][0]["answer"], {"summary": "kept"})
        self.assertEqual(run(argv + ["--force"]), 0)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["questions"][0]["answer"], {"summary": ""})


if __name__ == "__main__":
    unittest.main()
