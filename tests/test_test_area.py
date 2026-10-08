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
from unittest import mock

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.library import resolve  # noqa: E402
from Shared.tools import (accept_product, build_pages_site, build_question_bank_web, build_test_site, check_subjects,  # noqa: E402
                          deploy_test, owner_bank, product_manifest, render_core)

PKG = "tests/fixtures/render/thin-kin-2d-motion.v1.json"
OFFICIAL_BANK = "Physics/library/exam-bank/competitive-exam-question-bank.v2.json"
OWNER_CUSTODY = {"authority_class": "OWNER_SUPPLIED_RAW_INPUT", "intake_ref": "sha256:fixture", "wording_custody": "VERBATIM"}


def fill_page(row: dict) -> dict:
    """What an owner question needs to meet the Core2 blueprint at the reference depth (what `owner_bank.py new` leaves empty):
    a typed route and ladder at the band's depth, the EXPECTED components, and a recorded waiver for the one thing a fixture
    cannot draw."""
    band = ((row.get("extensions") or {}).get("grade9v3:analysis") or {}).get("difficulty", {}).get("band") or "D1"
    deep = band in ("D3", "D4")
    kinds = ["DECIDE", "REPRESENT", "TRANSFORM"] + (["VERIFY"] if deep else [])
    moves = [{"id": f"{row['id']}-MOVE-{n}", "kind": kind, "action": f"do step {n}", "why_valid": f"step {n} follows from the data",
              "inputs": ["the stated data"], "output": f"result {n}"}
             for n, kind in enumerate(kinds, 1)]
    row["answer"] = dict(row["answer"], reasoning_route=moves, crux_move_ref=moves[1]["id"], check="a limiting case agrees")
    rungs = (("CONNECT", "CONCEPT", "KEY_CONCEPT"), ("REPRESENT", "METHOD", "REPRESENTATION"), ("EXECUTE", "METHOD", "FIRST_MOVE"))
    if deep:
        rungs += (("EXECUTE", "METHOD", "FORMAL_MODEL"), ("EXECUTE", "METHOD", "CHECKPOINT"))
    row["scaffolds"] = [{"text": f"hint {n}", "support_kind": kind, "reveals": reveals, "learner_stage": stage,
                         "supports_move_ref": moves[min(n, len(moves)) - 1]["id"]}
                        for n, (kind, reveals, stage) in enumerate(rungs, 1)]
    row["conditions"] = row.get("conditions") or ["the stated model holds"]
    analysis = row["extensions"].setdefault("grade9v3:analysis", {})
    analysis["common_wrong_route"] = analysis.get("common_wrong_route") or "the tempting route that ignores the sign"
    analysis["expected_time_seconds"] = analysis.get("expected_time_seconds") or 120
    row["extensions"]["grade9v3:component_waivers"] = {"REPRESENTATION": "the fixture package has no authored figure"}
    row["figure_refs"] = []
    row.pop("hints", None)
    row.pop("hint_ladder", None)
    return row


def owner_questions(package: dict, count: int = 2) -> list[dict]:
    """Official-bank questions for the fixture package's capabilities, rewritten as owner-supplied ones."""
    bank = json.loads((REPO / OFFICIAL_BANK).read_text(encoding="utf-8"))
    caps = {c["id"] for c in package["capabilities"]}
    rows = copy.deepcopy([q for q in bank["questions"] if q.get("primary_capability_ref") in caps][:count])
    for index, row in enumerate(rows, 1):
        row["extensions"]["grade9v3:source_custody"] = dict(OWNER_CUSTODY, text_sha256=owner_bank.text_digest(row["stem"]))
        # An owner question names no exam: no exam badge and no exam provenance class, whatever the borrowed record carried.
        row["extensions"].pop("grade9v3:provenance_class", None)
        row["extensions"]["grade9v3:analysis"].pop("exam_source_badge", None)
        fill_page(row)
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


class TestManifestCommand(unittest.TestCase):
    def test_the_manifest_is_written_even_where_the_products_folder_does_not_exist_yet(self):
        package = REPO / "TEST" / f"_{uuid.uuid4().hex[:8]}"
        package.mkdir(parents=True)
        self.addCleanup(shutil.rmtree, package, True)
        (package / "package.v1.json").write_text(json.dumps(dict(json.loads((REPO / PKG).read_text(encoding="utf-8")), subject="TEST")),
                                                 encoding="utf-8")
        out = package / "products" / "m.manifest.json"
        with contextlib.redirect_stdout(io.StringIO()):
            code = product_manifest.main(["derive", "--package", f"TEST/{package.name}/package.v1.json", "--product-id", "m",
                                          "--home", "../../../index.html", "--out", str(out)])
        self.assertEqual(code, 0)
        self.assertTrue(out.is_file())


class TestPages(unittest.TestCase):
    def test_test_shell_subject_links_stay_under_portal_root_at_each_depth(self):
        for depth in (1, 2):
            with self.subTest(depth=depth):
                page = build_test_site.frame(depth, "TEST", "index.html", "")
                for subject in ("physics", "chemistry", "mathematics"):
                    self.assertIn(f'href="{"../" * depth}{subject}/index.html"', page)
                    self.assertNotIn(f'href="../../../{subject}/index.html"', page)

    def test_committed_pages_are_what_the_generator_writes(self):
        self.assertEqual(build_test_site.check(), [])

    def test_candidate_qa_registry_is_visible_and_both_candidates_remain_promotion_blocked(self):
        audits = build_test_site.candidate_audits()
        self.assertEqual({row["candidate_id"] for row in audits}, {"ISS55-POLY", "NCERT-EXEMPLAR-G9-MATH-210"})
        self.assertEqual({row["promotion"]["status"] for row in audits}, {"BLOCKED"})
        by_id = {row["candidate_id"]: row for row in audits}
        self.assertEqual(by_id["ISS55-POLY"]["state"], "TECH_PASS")
        self.assertEqual(by_id["NCERT-EXEMPLAR-G9-MATH-210"]["state"], "QA_IN_PROGRESS")
        hub = (REPO / "public/test/index.html").read_text(encoding="utf-8")
        self.assertIn("QA candidate: Issue #55 polynomial stress set", hub)
        self.assertIn("QA candidate: NCERT Exemplar Grade 9 Mathematics", hub)
        self.assertIn("2 candidate QA record(s) in TEST/candidates", hub)

    def test_stale_ncert_qa_counts_are_not_current_source_authority(self):
        """A 209-READY historical QA receipt must not override the custody ledger."""
        historical = next(a for a in build_test_site.candidate_audits()
                          if a["candidate_id"] == "NCERT-EXEMPLAR-G9-MATH-210")
        self.assertEqual(historical["question_counts"]["ready_for_blueprint"], 209)
        custody = {"total_intake": 210, "ready_for_blueprint": 0,
                   "source_text_hold": 0, "evidence_pending": 210}
        html = build_test_site.render_candidate_audit_section([historical], custody)
        self.assertIn("ready for blueprint: 0", html)
        self.assertIn("evidence pending: 210", html)
        self.assertIn("Historical QA receipt", html)
        self.assertNotIn("ready for blueprint: 209", html)
        self.assertEqual(historical["question_counts"]["ready_for_blueprint"], 209)

    def test_test_home_answers_do_not_claim_unverified_official_key_custody(self):
        """The 198 evidence-pending questions still carry recorded, not witnessed, keys."""
        home = build_test_site.render_intake_section(
            build_test_site.intake_banks(), build_test_site.test_source_custody.reconcile(REPO))
        self.assertIn("Recorded answer — official key custody pending:", home)
        self.assertIn("Evidenced official answer:", home)
        self.assertNotIn("Official Answer:", home)
        self.assertEqual(home.count("Evidenced official answer:"), 12)
        self.assertEqual(home.count("Recorded answer — official key custody pending:"), 198)

    def test_test_search_index_covers_parked_questions_without_becoming_canonical_search(self):
        rows = build_test_site.test_search_index()
        self.assertEqual(len(rows), 220)
        self.assertEqual(len([r for r in rows if r["kind"] == "OFFICIAL_INTAKE"]), 210)
        self.assertEqual(len([r for r in rows if r["kind"] == "OWNER_SUPPLIED"]), 10)
        self.assertEqual(len({r["id"] for r in rows}), 220)
        intake_rows = [r for r in rows if r["kind"] == "OFFICIAL_INTAKE"]
        self.assertEqual(sum(r["status"] == "READY_FOR_BLUEPRINT" for r in intake_rows), 12)
        self.assertEqual(sum(r["status"] == "SOURCE_TEXT_HOLD" for r in intake_rows), 0)
        self.assertEqual(sum(r["status"] == "EVIDENCE_PENDING" for r in intake_rows), 198)
        self.assertEqual(
            {r["id"] for r in intake_rows if r["status"] == "READY_FOR_BLUEPRINT"},
            {f"ncert-exemplar-g9-math-u01-q{n:02d}" for n in range(1, 7)} |
            {f"ncert-exemplar-g9-math-u02-q{n:02d}" for n in range(1, 7)},
        )
        hub = (REPO / "public/test/index.html").read_text(encoding="utf-8")
        self.assertIn('id="g9-test-search-index"', hub)
        self.assertIn("12 READY_FOR_BLUEPRINT · 0 SOURCE_TEXT_HOLD · 198 EVIDENCE_PENDING", hub)
        self.assertNotIn("SOURCE TEXT HOLD", hub)
        self.assertIn("Which one of the following is a polynomial?", hub)
        self.assertIn("Printed page 14 / PDF index 1", hub)
        self.assertIn("Inspect 210 parked intake questions", hub)
        self.assertIn("data-g9-intake-controls", hub)
        self.assertIn("data-g9-intake-facet=\"blueprint\"", hub)
        self.assertIn('src="question-bank/questions.js"', hub)
        self.assertIn('rel="noopener noreferrer"', hub)
        self.assertIn('href="https&#58;//ncert.nic.in/', hub)
        self.assertNotRegex(hub, r"https?://", "TEST pages stay offline despite optional official PDF links")
        self.assertEqual(hub.count("Official source PDF:"), 210)
        self.assertIn("Printed page 2 / PDF index 1", hub)
        self.assertNotIn("All items verified against official PDFs", hub)
        self.assertIn("TEST-only search index: 220 parked question(s); production search untouched", hub)
        canonical = (REPO / "public/data/search-index.v1.json").read_text(encoding="utf-8")
        learner = (REPO / "public/data/learner-search-index.v1.json").read_text(encoding="utf-8")
        for row in rows:
            self.assertNotIn(str(row["id"]), canonical)
            self.assertNotIn(str(row["id"]), learner)

    def test_owner_question_banks_are_visible_as_test_only_previews(self):
        page = (REPO / "public/test/index.html").read_text(encoding="utf-8")
        self.assertIn("Owner Question Bank: iss55-poly", page)
        self.assertIn("10 question(s) · owner-supplied custody · TEST-only preview · not accepted", page)
        for number in range(1, 11):
            self.assertIn(f"OWN-ISS55-POLY-{number:02d}", page)
        self.assertIn("Inspect answer / verification evidence", page)

    def test_committed_polynomial_core2_source_renders_through_current_renderer(self):
        manifest = REPO / "TEST/products/iss55-poly.manifest.json"
        pages, gaps, _digest, _advisories, _waived = render_core.build_report(manifest, "PAGES", held_to="REFERENCE")
        self.assertIn("core2.html", pages)
        core2 = pages["core2.html"]
        for number in range(1, 11):
            self.assertIn(f"OWN-ISS55-POLY-{number:02d}", core2)
        self.assertNotIn("Official past paper", core2)
        self.assertTrue(all(gap.get("core") == "CORE2" for gap in gaps), gaps)


    def test_a_rung_matrix_that_breaks_the_matrix_schema_says_so_on_the_rungs_page_and_in_the_build(self):
        board = {"matrix_id": "MX-BAD", "subject": "TEST", "topic": "Vectors", "subtopic": "Sums",
                 "rungs": [{"rung": "R1", "ladder_position": 110, "microtopic_ref": "MIC-X"}]}
        with mock.patch.object(build_test_site, "matrices", return_value=[board]):
            page = build_test_site.rungs_page()
            out = io.StringIO()
            with mock.patch.object(build_test_site, "PUBLIC_TEST", Path(tempfile.mkdtemp())), contextlib.redirect_stdout(out):
                build_test_site.write()
        self.assertIn("Matrix check:", page)
        self.assertIn("MATRIX_STRUCTURE", page)
        self.assertRegex(out.getvalue(), r"matrix MX-BAD: MATRIX_STRUCTURE .*110")

    def test_the_committed_matrix_passes_the_matrix_check_without_a_finding(self):
        for board in build_test_site.matrices():
            self.assertEqual(build_test_site.matrix_findings(board), [], board.get("matrix_id"))

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
        self.assertIn('data-g9-test-atlas-data', atlas)
        self.assertIn('.header-title-group{flex-wrap:wrap;min-width:0;max-width:100%}', atlas)
        self.assertIn('.header-subtitle{min-width:0;overflow-wrap:anywhere}', atlas)
        transform = json.loads(build_test_site.ATLAS_TRANSFORM.read_text(encoding="utf-8"))
        self.assertIn('.header-title-group{flex-wrap:wrap;min-width:0;max-width:100%}', transform["swaps"][-1]["new"])
        self.assertIn("MATRIX-TEST-ISS55-POLY", atlas)
        self.assertIn("MIC-MATH-POLY-IDENTITY-DEGREE-BOUND", atlas)
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
        self.assertEqual(len(projection["questions"]), 81)


    def test_polynomial_bank_uses_exact_primary_capabilities_and_keeps_concept_bridges_secondary(self):
        bank = json.loads((REPO / "TEST/question-bank/iss55-poly.json").read_text(encoding="utf-8"))
        expected = {
            "OWN-ISS55-POLY-01": ("CAP-MATH-POLY-FACTOR-PARAMETER", "CAP-MATH-POLY-CHANGE-OF-VARIABLE-DOMAIN"),
            "OWN-ISS55-POLY-02": ("CAP-MATH-POLY-MULTIPLICITY-SIGN", "CAP-MATH-POLY-SIGN-CHART-RIGOR"),
            "OWN-ISS55-POLY-03": ("CAP-MATH-POLY-INTERPOLATION-DEGREE-BOUND", "CAP-MATH-POLY-IDENTITY-THEOREM-DEGREE"),
            "OWN-ISS55-POLY-04": ("CAP-MATH-POLY-GEOMETRIC-AREA-DEGREE", "CAP-MATH-POLY-SIGN-CHART-RIGOR"),
            "OWN-ISS55-POLY-06": ("CAP-MATH-POLY-FACTOR-VALUE-CONSTRUCTION", "CAP-MATH-POLY-CHANGE-OF-VARIABLE-DOMAIN"),
            "OWN-ISS55-POLY-07": ("CAP-MATH-POLY-FACTOR-DIVISIBILITY-DEGREE", "CAP-MATH-POLY-IDENTITY-THEOREM-DEGREE"),
            "OWN-ISS55-POLY-09": ("CAP-MATH-POLY-PARAMETER-DEGREE-ZERO", "CAP-MATH-POLY-CHANGE-OF-VARIABLE-DOMAIN"),
        }
        rows = {q["id"]: q for q in bank["questions"]}
        for qid, (primary, bridge) in expected.items():
            self.assertEqual(rows[qid]["primary_capability_ref"], primary)
            self.assertIn(bridge, rows[qid].get("secondary_capability_refs", []))

        package = json.loads((REPO / "TEST/library/iss55-poly.v1.json").read_text(encoding="utf-8"))
        anchors = {
            a["target_question_ref"]: a
            for mic in package["microtopics"]
            for a in ((mic.get("extensions") or {}).get("grade9v3:lesson_anchors") or {}).values()
        }
        self.assertIn("(k - 4)x + 12", anchors["OWN-ISS55-POLY-01"]["stem"])
        self.assertIn("(a - 1)x^3 + (a + 1)x^2 - 2x", anchors["OWN-ISS55-POLY-09"]["stem"])
        self.assertIn("x^4 + 4x^2 + 4", anchors["OWN-ISS55-POLY-10"]["stem"])


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
        self.assertFalse([g for g in receipt["gaps"] if "PROVENANCE" in g["detail"] or "SOURCE_LABEL" in g["detail"]],
                         "an owner question needs no exam badge and takes the owner provenance")
        identity = re.findall(r'data-g9-block="source_identity">(.*?)</div>', core2, flags=re.S)
        self.assertEqual(len(identity), 2, "one identity block per owner question")
        for block in identity:
            self.assertNotRegex(block, r"JEE|IIT|NTA|Official past paper|20\d\d")
        for name, sha in receipt["pages"].items():
            page = (out / name).read_text(encoding="utf-8")
            self.assertIn('data-g9-test="sandbox-draft"', page)
            self.assertIn("data-g9-test-banner", page)
            self.assertIn("<title>TEST draft · ", page)
            self.assertEqual(deploy_test._sha(page.encode("utf-8")), sha)
        self.assertEqual(json.loads((out / "deploy-receipt.json").read_text(encoding="utf-8"))["render_digest"],
                         receipt["render_digest"])

    def test_every_role_page_links_the_pdf_printed_from_it_and_the_deploy_prints_them_never_a_key_pdf(self):
        receipt = deploy_test.deploy_product(self.fixture.manifest)
        out = deploy_test.PUBLIC_TEST / "products" / self.fixture.slug
        self.assertEqual(receipt["pdf"]["status"], "PRINTED", receipt["pdf"])
        role_pages = sorted(name for name in receipt["pages"] if name != "index.html")
        self.assertEqual(sorted(receipt["pdf"]["files"]), [name.replace(".html", ".pdf") for name in role_pages])
        for name in role_pages:
            link = re.search(r'<a data-g9-action="pdf"[^>]*href="([^"]+)"', (out / name).read_text(encoding="utf-8"))
            self.assertEqual(link.group(1), name.replace(".html", ".pdf"))
            data = (out / link.group(1)).read_bytes()
            self.assertTrue(data.startswith(b"%PDF"), name)
            self.assertEqual(receipt["pdf"]["files"][link.group(1)], deploy_test._sha(data))
        self.assertNotIn('data-g9-action="pdf"', (out / "index.html").read_text(encoding="utf-8"))
        self.assertEqual(list(out.glob("*.key.pdf")), [])
        self.assertEqual(render_core.pdf_publication_problems(out), [])
        self.assertEqual(json.loads((out / "print-receipt.json").read_text(encoding="utf-8"))["mode"], "LEARNER_PDF")
        page = build_test_site.deployments_page()
        self.assertIn("Print copies:", page)
        self.assertIn(f"../products/{self.fixture.slug}/core2.pdf", page)

    def test_a_printed_draft_still_says_it_is_a_draft(self):
        try:
            from pypdf import PdfReader
        except ImportError:
            self.skipTest("pypdf is not installed")
        deploy_test.deploy_product(self.fixture.manifest)
        out = deploy_test.PUBLIC_TEST / "products" / self.fixture.slug
        text = " ".join(page.extract_text() for page in PdfReader(str(out / "core2.pdf")).pages)
        self.assertIn("not accepted", text, "the sandbox label is printed with the page")
        self.assertIn("Owner-supplied question", text)

    def test_where_nothing_can_print_the_deploy_says_the_pdf_links_go_nowhere(self):
        stderr = io.StringIO()
        with mock.patch.object(deploy_test.shutil, "which", return_value=None), contextlib.redirect_stderr(stderr):
            receipt = deploy_test.deploy_product(self.fixture.manifest)
        self.assertEqual((receipt["pdf"]["status"], receipt["pdf"]["files"]), ("NOT_PRINTED", {}))
        self.assertIn("go nowhere", receipt["pdf"]["reason"])
        self.assertIn("do not work", stderr.getvalue())
        self.assertIn("No PDF copies:", build_test_site.deployments_page())

    def test_the_receipt_and_the_deployments_page_say_what_each_gap_is(self):
        receipt = deploy_test.deploy_product(self.fixture.manifest)
        self.assertEqual(len(receipt["gaps"]), receipt["gap_count"])
        self.assertTrue(receipt["gaps"], "the fixture package leaves gaps")
        first = receipt["gaps"][0]
        self.assertEqual(sorted(first), ["core", "detail", "duty", "record"])
        page = build_test_site.deployments_page()
        self.assertIn(f"The {receipt['gap_count']} gap(s)", page)
        self.assertIn(first["record"], page)
        self.assertIn(first["detail"].replace("&", "&amp;"), page.replace("&#x27;", "'"))

    def test_two_components_one_record_lacks_are_two_gaps_not_one(self):
        bank_path = self.fixture.root / "owner.bank.json"
        bank = json.loads(bank_path.read_text(encoding="utf-8"))
        row = bank["questions"][0]
        del row["scaffolds"]
        del row["answer"]["reasoning_route"]
        row["conditions"] = []
        row["extensions"]["grade9v3:component_waivers"].pop("REPRESENTATION")
        bank_path.write_text(json.dumps(bank), encoding="utf-8")
        receipt = deploy_test.deploy_product(self.fixture.manifest)
        mine = [g["detail"] for g in receipt["gaps"] if g["record"] == row["id"]]
        for component in ("HINT_LADDER", "SOLUTION_STEPS", "CONDITIONS", "REPRESENTATION"):
            self.assertTrue(any(d.startswith(component) for d in mine), (component, mine))
        self.assertLessEqual({g["component"] for g in receipt["gaps"] if g.get("component")}, set(receipt["authoring"]),
                             "the blueprint's instruction is kept for each component that has a gap")

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


class TestToughestConcept(unittest.TestCase):
    """The concept book is built for the hardest question, not only named after it."""

    def setUp(self):
        self.fixture = Fixture()
        self.addCleanup(self.fixture.cleanup)
        self.package_path = self.fixture.root / "package.v1.json"

    def deploy(self):
        return deploy_test.deploy_product(self.fixture.manifest)

    def unit_for(self, receipt: dict, **overrides) -> dict:
        """A construction unit of the concept the hardest question belongs to, built from that concept's own steps."""
        package = json.loads(self.package_path.read_text(encoding="utf-8"))
        brief = receipt["toughest"]
        microtopic = next(m for m in package["microtopics"] if m["id"] == brief["microtopic_ref"])
        steps = [step["id"] for step in microtopic["teaching_path"]][:4]
        unit = {"id": "CU-FX-HARD-1", "decision": "Build the idea the hardest question turns on", "step_refs": steps,
                "representation_ref": microtopic["representation_refs"][-1],
                "independent_checks": [{"statement": f"check {n}", "role": role}
                                       for n, role in enumerate(("CHECK", "APPLY", "CONNECT"), 1)],
                "bank_anchor_ref": brief["question_ref"], "crux_question_refs": [brief["question_ref"]],
                "crux_step_ref": steps[-1], **overrides}
        microtopic["construction_units"] = [unit]
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        return unit

    def toughest_gaps(self, receipt: dict) -> list[str]:
        return [f"{g.get('component')}: {g['detail']}" for g in receipt["gaps"] if g["duty"] == "AUTHOR_TOUGHEST_CONCEPT"]

    def test_the_deploy_names_the_toughest_concept_and_a_book_that_never_builds_toward_it_is_a_gap(self):
        receipt = self.deploy()
        brief = receipt["toughest"]
        self.assertEqual((brief["question_ref"], brief["band"]), ("Q-OWNER-FX-01", "D3"))
        self.assertTrue(brief["microtopic_ref"] and brief["crux_move"]["action"])
        gaps = self.toughest_gaps(receipt)
        self.assertEqual(len(gaps), 1, gaps)
        self.assertIn("Q1 is the toughest question in this set", gaps[0])
        self.assertIn("crux_question_refs", gaps[0])
        self.assertIn("QUESTION_BRIDGE", receipt["authoring"])
        self.assertIn("Toughest concept", build_test_site.deployments_page())

    def test_a_unit_that_builds_toward_it_and_works_the_question_itself_closes_the_gap_and_shows_why(self):
        receipt = self.deploy()
        self.unit_for(receipt)
        receipt = self.deploy()
        self.assertEqual(self.toughest_gaps(receipt), [])
        page = (deploy_test.PUBLIC_TEST / "products" / self.fixture.slug / "core1a.html").read_text(encoding="utf-8")
        self.assertIn('data-g9-component="QUESTION_BRIDGE"', page)
        self.assertIn("the hardest question in this set", page)
        self.assertIn('href="core2.html#Q-OWNER-FX-01"', page)
        self.assertIn("data-g9-crux-step", page)
        self.assertRegex(page, r'data-g9-anchor-source>Q1 · Owner-supplied question, verbatim')
        depth = [g["detail"] for g in receipt["gaps"] if g.get("component") == "CONSTRUCTION_STEPS"]
        self.assertEqual(depth, [], "four steps meet the reference for a D3 question")

    def test_the_unit_takes_the_depth_of_the_hard_question_it_builds_toward(self):
        receipt = self.deploy()
        unit = self.unit_for(receipt)
        package = json.loads(self.package_path.read_text(encoding="utf-8"))
        microtopic = next(m for m in package["microtopics"] if m["id"] == receipt["toughest"]["microtopic_ref"])
        microtopic["construction_units"][0]["step_refs"] = unit["step_refs"][:3]
        microtopic["construction_units"][0]["crux_step_ref"] = unit["step_refs"][2]
        self.package_path.write_text(json.dumps(package), encoding="utf-8")
        details = [g["detail"] for g in self.deploy()["gaps"] if g.get("component") == "CONSTRUCTION_STEPS"]
        self.assertEqual(len(details), 1, details)
        self.assertIn("3 of the 4 steps the reference page has for a D3 question", details[0])

    def test_naming_the_question_is_not_enough_the_unit_must_work_it_and_point_at_its_step(self):
        receipt = self.deploy()
        self.unit_for(receipt, bank_anchor_ref=None, worked_anchor_ref=None)
        gaps = self.toughest_gaps(self.deploy())
        self.assertEqual(len(gaps), 1, gaps)
        self.assertIn("its worked example is not Q1", gaps[0])
        self.unit_for(receipt, crux_step_ref="NOT-A-STEP")
        details = [g["detail"] for g in self.deploy()["gaps"] if g["duty"] == "AUTHOR_QUESTION_BRIDGE"]
        self.assertEqual(len(details), 1, details)
        self.assertIn("crux_step_ref", details[0])

    def test_a_bank_ref_that_names_no_question_of_the_bank_is_a_gap_that_says_which(self):
        receipt = self.deploy()
        self.unit_for(receipt, bank_anchor_ref="Q-NOT-IN-THE-BANK", crux_question_refs=["Q-ALSO-NOT"])
        gaps = {g["duty"]: g["detail"] for g in self.deploy()["gaps"] if g["duty"] in ("AUTHOR_WORKED_ANCHOR", "AUTHOR_QUESTION_BRIDGE")}
        self.assertIn("Q-NOT-IN-THE-BANK is not a question of this product's bank", gaps["AUTHOR_WORKED_ANCHOR"])
        self.assertIn("Q-ALSO-NOT", gaps["AUTHOR_QUESTION_BRIDGE"])

    def test_an_official_product_is_judged_at_its_floor_and_is_not_asked_for_this(self):
        from Shared.tools import render_core
        manifest = REPO / "products/physics/phy-kin-2d-motion.manifest.json"
        _pages, gaps, _digest, _advisories, _waived = render_core.build_report(manifest, "PAGES")
        self.assertEqual([g for g in gaps if g["duty"] in ("AUTHOR_TOUGHEST_CONCEPT", "AUTHOR_QUESTION_BRIDGE")], [])


class TestPagesCommand(unittest.TestCase):
    """`deploy_test.py pages` is what a person runs after build_web_data.py: it must refresh the Pages mirror too."""

    def run_pages(self, *args):
        with mock.patch.object(build_test_site, "write") as write, mock.patch.object(build_pages_site, "write") as mirror, \
                mock.patch.object(build_test_site, "check", return_value=[]) as check, \
                mock.patch.object(build_pages_site, "check", return_value=["docs/data/data.js is stale"]) as mirror_check, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = deploy_test.main(["pages", *args])
        return code, out.getvalue(), write, mirror, check, mirror_check

    def test_pages_rebuilds_the_test_pages_and_then_the_mirror(self):
        code, _out, write, mirror, _check, _mc = self.run_pages()
        self.assertEqual((code, write.call_count, mirror.call_count), (0, 1, 1))

    def test_no_mirror_leaves_the_mirror_alone(self):
        _code, _out, write, mirror, _check, _mc = self.run_pages("--no-mirror")
        self.assertEqual((write.call_count, mirror.call_count), (1, 0))

    def test_check_fails_on_a_stale_mirror_not_only_on_stale_test_pages(self):
        code, out, _w, _m, _c, mirror_check = self.run_pages("--check")
        self.assertEqual(code, 1)
        self.assertIn("docs/data/data.js is stale", out)
        self.assertEqual(self.run_pages("--check", "--no-mirror")[0], 0)


class TestLibraryCheck(unittest.TestCase):
    def test_the_schema_option_reports_what_a_product_build_would_refuse(self):
        package = json.loads((REPO / PKG).read_text(encoding="utf-8"))
        package["subject"] = "TEST"
        package["capabilities"][0]["acceptance_status"] = "UNREVIEWED"
        package["capabilities"][1]["acceptance_status"] = "NOT-A-STATUS"
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "p.json"
            path.write_text(json.dumps(package), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as strict:
                self.assertEqual(resolve.main(["--schema", str(path)]), 1)
        self.assertIn("capabilities/0/acceptance_status", strict.getvalue())
        self.assertIn("capabilities/1/acceptance_status", strict.getvalue())


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
        self.assertIn("<title>TEST draft · x</title>", page)
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
                fill_page(row)
                row["answer"]["summary"] = "an answer"
                row["primary_capability_ref"] = "CAP-X"
                row["family_ref"] = "FAM-X"
                analysis = row["extensions"]["grade9v3:analysis"]
                analysis["learner_question_type"] = "constructed_response"
                analysis["difficulty"].update(band="D1", score=1, basis="a direct application")
                analysis["difficulty"]["components"]["concept_model_selection"] = 1
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
        self.assertEqual(sum("METADATA_QUESTION_DIFFICULTY" in p for p in problems), 2, problems)
        self.assertEqual(sum("METADATA_QUESTION_TYPE" in p for p in problems), 2, problems)
        self.assertTrue(any("score 0 to 2" in p for p in problems), "the difficulty message says what the bands are")
        self.assertTrue(any("learner_question_type is one of" in p for p in problems), problems)
        self.assertEqual(owner_bank.check(self.bank(), intake=self.INTAKE), [])

    def test_the_skeleton_carries_the_deepest_ladder_and_route_and_check_names_what_is_empty(self):
        bank = self.bank(fill=False)
        row = bank["questions"][0]
        # The skeleton is the reference depth for a D3 or D4 question: the author deletes what the band does not need.
        self.assertEqual([m["kind"] for m in row["answer"]["reasoning_route"]], ["DECIDE", "REPRESENT", "TRANSFORM", "VERIFY"])
        self.assertEqual([r["learner_stage"] for r in row["scaffolds"]],
                         ["REPRESENTATION", "KEY_CONCEPT", "CRUX", "FORMAL_MODEL", "CHECKPOINT"])
        self.assertEqual({r["supports_move_ref"] for r in row["scaffolds"]} - {m["id"] for m in row["answer"]["reasoning_route"]}, set())
        problems = " ".join(owner_bank.check(bank))
        self.assertIn("scaffolds[0].text is empty", problems)
        self.assertIn("is missing action", problems)

    def test_a_question_with_no_hint_ladder_or_route_is_refused_and_says_why(self):
        bank = self.bank()
        row = bank["questions"][0]
        del row["scaffolds"]
        del row["answer"]["reasoning_route"]
        problems = " ".join(owner_bank.check(bank))
        self.assertIn("HINT_LADDER needs 3, the record supplies 0", problems)
        self.assertIn("SOLUTION_STEPS needs 3, the record supplies 0", problems)
        self.assertIn("scaffolds[]", problems, "the message carries the blueprint's own instruction for the author")

    def test_a_rung_must_point_at_a_move_the_crux_must_name_one_and_an_owner_question_has_no_source_hints(self):
        bank = self.bank()
        row = bank["questions"][0]
        row["scaffolds"][0]["supports_move_ref"] = "NOT-A-MOVE"
        row["answer"]["crux_move_ref"] = "ALSO-NOT"
        row["hints"] = ["a hint the Owner never wrote"]
        problems = " ".join(owner_bank.check(bank))
        self.assertIn("scaffolds[0].supports_move_ref must be the id of a reasoning_route move", problems)
        self.assertIn("answer.crux_move_ref must be the id of the move", problems)
        self.assertIn("an owner question has no source", problems)

    def test_a_rung_that_gives_the_answer_does_not_count_towards_the_ladder(self):
        bank = self.bank()
        for rung in bank["questions"][0]["scaffolds"]:
            rung["reveals"] = "ANSWER"
        self.assertIn("only 0 of 3 scaffold(s) can be shown before the answer", " ".join(owner_bank.check(bank)))

    def test_every_expected_component_is_supplied_or_waived_with_a_reason(self):
        bank = self.bank()
        for row in bank["questions"]:
            row["extensions"].pop("grade9v3:component_waivers")
            row["conditions"] = []
            row["extensions"]["grade9v3:analysis"].pop("common_wrong_route")
            del row["answer"]["check"]
        notes = " ".join(owner_bank.check(bank))
        for component in ("CONDITIONS", "TRAP", "REPRESENTATION", "CHECK"):
            self.assertIn(f"{component} is absent", notes)   # the blueprint's EXPECTED components, named as it names them
        self.assertIn("component_waivers", notes, "the message says how to waive")
        self.assertEqual(owner_bank.check(bank, complete=False), [], "the renderer builds a draft and reports a gap instead")
        for row in bank["questions"]:
            row["extensions"]["grade9v3:component_waivers"] = {"CONDITIONS": "the question states none", "TRAP": "no tempting route",
                                                               "REPRESENTATION": "nothing to draw", "CHECK": "a unit check adds nothing"}
        self.assertEqual(owner_bank.check(bank), [])

    def test_a_deep_question_is_held_to_the_deep_ladder_and_route(self):
        bank = self.bank()
        row = bank["questions"][0]
        row["extensions"]["grade9v3:analysis"]["difficulty"].update(band="D3", score=5)
        problems = " ".join(owner_bank.check(bank))
        self.assertIn("HINT_LADDER needs 5, the record supplies 3", problems)
        self.assertIn("SOLUTION_STEPS needs 4, the record supplies 3", problems)

    def test_an_owner_question_cannot_take_an_exam_provenance_class(self):
        bank = self.bank()
        bank["questions"][0]["extensions"]["grade9v3:provenance_class"] = "PYQ_ADAPTED"
        problems = owner_bank.check(bank)
        self.assertTrue(any("METADATA_PROVENANCE_INVALID" in p and "OWNER_SUPPLIED" in p for p in problems), problems)

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
        written["questions"][0]["answer"]["summary"] = "kept"
        out.write_text(json.dumps(written), encoding="utf-8")
        self.assertEqual(run(argv), 1, "a second run must not erase the answers")
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["questions"][0]["answer"]["summary"], "kept")
        self.assertEqual(run(argv + ["--force"]), 0)
        self.assertEqual(json.loads(out.read_text(encoding="utf-8"))["questions"][0]["answer"]["summary"], "")


if __name__ == "__main__":
    unittest.main()
