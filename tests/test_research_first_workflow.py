"""Research-first workflow: raw intake -> research/author -> rendered product -> final gate.

Every job here starts from raw owner input with no canonical ids. The three subject
fixtures must pass the gate; mutations of their rendered output must fail it, and the
PR #288 Motion-in-2D product (holds presented as the output) is the regression case.
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

from Shared.tools import delivery_gate, learner_product_render, raw_intake

REPO = Path(__file__).resolve().parents[1]
FIXTURES = REPO / "tests/fixtures/research-first"
BENCHMARK = REPO / "benchmarks/learner-product-reference/physics-motion-2d.json"
SUBJECTS = ("physics-motion-2d", "mathematics-quadratics", "chemistry-mole-concept")


def load(name: str) -> dict:
    return json.loads((FIXTURES / f"{name}.json").read_text(encoding="utf-8"))


class Rendered:
    """A rendered job in a temp directory that a test may mutate."""

    def __init__(self, bundle: dict):
        self.dir = Path(tempfile.mkdtemp(prefix="research-first-"))
        self.manifest = learner_product_render.write(bundle, self.dir)

    def gate(self, benchmark=None) -> dict:
        return delivery_gate.check(self.manifest, benchmark)

    def edit(self, rel: str, fn) -> None:
        path = self.dir / rel
        path.write_text(fn(path.read_text(encoding="utf-8")), encoding="utf-8")

    def edit_manifest(self, fn) -> None:
        data = json.loads(self.manifest.read_text(encoding="utf-8"))
        fn(data)
        self.manifest.write_text(json.dumps(data), encoding="utf-8")

    def page(self, contains: str) -> str:
        return next(f"pages/{p.name}" for p in sorted((self.dir / "pages").glob("*.html")) if contains in p.name)

    def close(self):
        shutil.rmtree(self.dir, ignore_errors=True)


class IntakeTests(unittest.TestCase):
    def test_raw_inputs_start_without_ids_profile_or_scope(self):
        for name in SUBJECTS:
            plan = raw_intake.intake(load(name)["request"])
            self.assertEqual(plan["status"], "RESEARCH_AND_AUTHOR", name)
            self.assertEqual(plan["errors"], [])
            self.assertFalse(plan["learner_start"]["blocking"])
            self.assertEqual(plan["learner_start"]["support"], "full")
            self.assertGreaterEqual(plan["learner_start"]["diagnostic"]["min_items"], 3)
            self.assertNotIn("HOLD", json.dumps(plan))
            kinds = {t["kind"] for t in plan["research_tasks"]}
            self.assertIn("teach_subtopic", kinds)
            self.assertIn("solve_and_explain", kinds)
            ledger_ids = {r["input_id"] for r in plan["coverage_ledger_template"]}
            supplied = {q["id"] for q in plan["inputs"]["questions"]} | {s["id"] for s in plan["inputs"]["syllabus"]}
            self.assertEqual(ledger_ids, supplied)

    def test_missing_knowledge_percentage_never_blocks(self):
        request = {"subject": "Anything", "questions": ["Explain why the sky looks blue at noon."]}
        plan = raw_intake.intake(request)
        self.assertEqual(plan["status"], "RESEARCH_AND_AUTHOR")
        self.assertEqual(plan["learner_start"]["knowledge_percentage"], 50)
        self.assertEqual(plan["learner_start"]["source"], "DEFAULT_MEDIAN")
        zero = raw_intake.intake({**request, "learner": {"knowledge_percentage": 0}})
        self.assertEqual(zero["learner_start"]["knowledge_percentage"], 0)
        self.assertFalse(zero["learner_start"]["blocking"])

    def test_short_label_is_never_an_identity(self):
        plan = raw_intake.intake(load("physics-motion-2d")["request"])
        rows = {q["label"]: q for q in plan["inputs"]["questions"] if q["label"]}
        self.assertEqual(rows["Q15"]["text_status"], "SUPPLIED")
        self.assertTrue(rows["Q15"]["identity_claim_requested"])
        self.assertEqual(rows["Q15"]["conditions"], ["20", "30", "10"])
        self.assertEqual(rows["Q7"]["text_status"], "LABEL_ONLY")
        tasks = {t["id"] for t in plan["research_tasks"]}
        self.assertIn(f"recover_question_text:{rows['Q7']['id']}", tasks)
        self.assertIn(f"resolve_source_identity:{rows['Q15']['id']}", tasks)
        self.assertNotIn("canonical_question_ref", json.dumps(plan))

    def test_reconciliation_surfaces_questions_outside_the_syllabus(self):
        plan = raw_intake.intake(load("mathematics-quadratics")["request"])
        texts = {q["id"]: q["text"] for q in plan["inputs"]["questions"]}
        outside = [texts[i] for i in plan["reconciliation"]["questions_outside_syllabus"]]
        self.assertIn("The product of two consecutive positive integers is 132. Find the integers.", outside)
        tasks = {t["kind"] for t in plan["research_tasks"]}
        self.assertIn("place_unmatched_question", tasks)
        self.assertIn("author_practice", tasks)

    def test_empty_request_is_invalid_not_held(self):
        plan = raw_intake.intake({"subject": ""})
        self.assertEqual(plan["status"], "INVALID_REQUEST")
        self.assertEqual(len(plan["errors"]), 2)

    def test_ids_are_content_derived_and_stable(self):
        a = raw_intake.intake({"subject": "X", "questions": ["  Find  the  range. "]})
        b = raw_intake.intake({"subject": "X", "questions": ["Find the range.", "find the range."]})
        self.assertEqual(a["inputs"]["questions"][0]["id"], b["inputs"]["questions"][0]["id"])
        self.assertEqual(b["inputs"]["questions"][0]["supplied_count"], 2)


class DeliveryGateTests(unittest.TestCase):
    def setUp(self):
        self.jobs: list[Rendered] = []

    def tearDown(self):
        for job in self.jobs:
            job.close()

    def job(self, name: str, bundle: dict | None = None) -> Rendered:
        rendered = Rendered(bundle or load(name))
        self.jobs.append(rendered)
        return rendered

    def assertFails(self, report: dict, code: str):
        self.assertFalse(report["passed"])
        self.assertIn(code, report["codes"], report["findings"][:5])

    def test_every_subject_passes_from_raw_input(self):
        for name in SUBJECTS:
            report = self.job(name).gate()
            self.assertTrue(report["passed"], (name, report["findings"][:5]))

    def test_physics_reference_benchmark(self):
        job = self.job("physics-motion-2d")
        self.assertTrue(job.gate(BENCHMARK)["passed"])
        book = (job.dir / "book/index.html").read_text(encoding="utf-8")
        self.assertGreaterEqual(book.count('class="book-page"'), 35)
        bank = json.loads((job.dir / "bank/questions.json").read_text(encoding="utf-8"))["units"]
        self.assertGreaterEqual(sum(1 for u in bank if u["visual"] and u["steps"]), 15)

    def test_small_job_does_not_meet_the_reference_benchmark(self):
        report = self.job("chemistry-mole-concept").gate(BENCHMARK)
        self.assertFails(report, "benchmark_book_pages")
        self.assertFails(report, "benchmark_bank_units")

    def test_padded_book_pages_do_not_count(self):
        job = self.job("physics-motion-2d")
        job.edit("book/index.html", lambda t: t.replace(
            "</main>", "".join(f'<section class="book-page" id="pad-{i}"><p>Notes.</p></section>' for i in range(3)) + "</main>"))
        self.assertFails(job.gate(BENCHMARK), "book_page_thin")

    def test_hold_or_placeholder_text_fails_everywhere(self):
        for marker in ("VISUAL_HOLD", "HOLD", "TODO: add diagram", "Worked example coming soon", "placeholder"):
            job = self.job("mathematics-quadratics")
            page = job.page("factorisation")
            job.edit(page, lambda t: t.replace("<h3>Understand it</h3>", f"<h3>Understand it</h3><p>{marker}</p>", 1))
            self.assertFails(job.gate(), "learner_text_placeholder")
        job = self.job("chemistry-mole-concept")
        job.edit("bank/questions.json", lambda t: t.replace('"answer": "2 mol"', '"answer": "IDENTITY_HOLD"'))
        self.assertFails(job.gate(), "learner_text_placeholder")

    def test_manifest_pointing_at_files_is_not_evidence(self):
        job = self.job("chemistry-mole-concept")
        job.edit("book/index.html", lambda t: re.sub(r"<main>.*</main>", "<main><p>Book</p></main>", t, flags=re.S))
        report = job.gate()
        self.assertFails(report, "location_unresolved")
        self.assertFails(report, "diagnostic_missing")

    def test_dropped_input_fails_reconciliation(self):
        job = self.job("physics-motion-2d")
        job.edit_manifest(lambda m: m.__setitem__("ledger", m["ledger"][1:]))
        self.assertFails(job.gate(), "input_not_in_ledger")
        bundle = load("mathematics-quadratics")
        bundle["content"]["subtopics"] = [s for s in bundle["content"]["subtopics"] if s.get("syllabus")]
        self.assertFails(self.job("", bundle).gate(), "input_not_in_ledger")

    def test_teaching_needs_explanation_worked_example_and_visual(self):
        bundle = load("chemistry-mole-concept")
        sub = bundle["content"]["subtopics"][0]
        sub.pop("worked_example")
        sub.pop("visual")
        report = self.job("", bundle).gate()
        details = {f["detail"] for f in report["findings"] if f["code"] == "teaching_incomplete"}
        self.assertIn("no worked example with steps", details)
        self.assertIn("no visual with an accessible title", details)

    def test_attempt_must_precede_a_concealed_answer(self):
        job = self.job("mathematics-quadratics")
        page = job.page("factorisation")

        def swap(t):
            q = re.search(r'<article id="q[0-9a-f]+" data-role="question" data-core="CORE2">.*?</article>', t, re.S).group(0)
            attempt = re.search(r'<div data-role="attempt">.*?</div>', q, re.S).group(0)
            answer = re.search(r'<details data-role="answer">.*?</details>', q, re.S).group(0)
            moved = q.replace(attempt, "").replace(answer, answer.replace("<details", "<div").replace("</details>", "</div>") + attempt)
            return t.replace(q, moved)
        job.edit(page, swap)
        self.assertFails(job.gate(), "answer_before_attempt")

    def test_supplied_questions_are_core2_and_authored_practice_is_core2a(self):
        job = self.job("physics-motion-2d")
        bank = json.loads((job.dir / "bank/questions.json").read_text(encoding="utf-8"))["units"]
        for rel in sorted((job.dir / "pages").glob("*.html")):
            text = rel.read_text(encoding="utf-8")
            for unit in bank:
                tag = re.search(rf'<article id="{unit["id"]}" data-role="question" data-core="(CORE2A?)">', text)
                if tag:
                    self.assertEqual(tag.group(1), "CORE2A" if unit["authored"] else "CORE2", unit["id"])
        self.assertEqual(job.gate()["findings"], [])

    def test_authored_practice_presented_as_core2_fails(self):
        bundle = load("mathematics-quadratics")
        bundle["content"]["questions"].append({
            **copy.deepcopy(bundle["content"]["questions"][0]),
            "text": "Authored: factorise x^2 + 7x + 12 = 0 and solve it.",
        })
        sub = next(s for s in bundle["content"]["subtopics"] if bundle["content"]["questions"][0]["text"] in s.get("practice", []))
        sub["practice"].append("Authored: factorise x^2 + 7x + 12 = 0 and solve it.")
        job = self.job("", bundle)
        self.assertEqual(job.gate()["findings"], [])
        for rel in sorted((job.dir / "pages").glob("*.html")):
            job.edit(f"pages/{rel.name}", lambda t: t.replace('data-core="CORE2A"', 'data-core="CORE2"'))
        self.assertFails(job.gate(), "authored_as_core2")

    def test_supplied_question_must_be_rendered_where_the_ledger_says(self):
        job = self.job("chemistry-mole-concept")
        page = job.page("molar-mass")
        job.edit(page, lambda t: t.replace("How many moles are present in 36 g of water?", "Water question."))
        self.assertFails(job.gate(), "question_not_rendered")

    def test_identity_requires_matching_text_conditions_and_discriminator(self):
        base = load("physics-motion-2d")
        cases = {
            "identity_condition_mismatch": lambda r: r.__setitem__("source_text", r["source_text"].replace("30°", "60°")),
            "identity_text_mismatch": lambda r: r.__setitem__("source_text", "Q8. 20 30 10 projectile."),
            "identity_discriminator_missing": lambda r: r.pop("discriminator"),
            "identity_unresolved": lambda r: r.__setitem__("status", "IDENTITY_HOLD"),
        }
        for code, mutate in cases.items():
            bundle = copy.deepcopy(base)
            mutate(bundle["evidence"]["identities"][0])
            self.assertFails(self.job("", bundle).gate(), code)
        bundle = copy.deepcopy(base)
        bundle["evidence"]["identities"] = bundle["evidence"]["identities"][1:]
        self.assertFails(self.job("", bundle).gate(), "identity_unresolved")

    def test_unclaimed_identity_is_not_displayed(self):
        job = self.job("chemistry-mole-concept")
        page = job.page("percentage")
        job.edit(page, lambda t: t.replace("Your question Q3", "Board sample paper Q3"))
        self.assertFails(job.gate(), "identity_displayed_without_claim")

    def test_research_must_be_done_with_a_locator(self):
        bundle = load("mathematics-quadratics")
        bundle["evidence"]["research"][1]["sources"] = [{"note": "remembered"}]
        self.assertFails(self.job("", bundle).gate(), "research_open")

    def test_atlas_and_builder_link_every_page(self):
        job = self.job("physics-motion-2d")
        target = job.page("uniform")
        name = Path(target).name
        job.edit("atlas/index.html", lambda t: re.sub(rf'<li><a href="\.\./pages/{name}">.*?</li>', "", t, flags=re.S))
        job.edit("builder/index.html", lambda t: t.replace('<li><a href="../atlas/index.html">Atlas</a></li>', ""))
        report = job.gate()
        missing = [f for f in report["findings"] if f["code"] == "link_missing"]
        self.assertTrue(any(f["where"] == "atlas/index.html" for f in missing))
        self.assertTrue(any(f["where"] == "builder/index.html" for f in missing))

    def test_renderer_never_emits_hold_or_placeholder_text(self):
        job = self.job("physics-motion-2d")
        for path in job.dir.rglob("*"):
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                self.assertNotRegex(text, r"\b[A-Z_]*HOLD\b|TODO|TBD|(?i:placeholder|coming soon)", path)

    def test_pr288_motion_2d_regression_fails(self):
        """PR #288 passed its own audit with holds as the product. It must fail here."""
        work = Path(tempfile.mkdtemp(prefix="pr288-"))
        self.addCleanup(shutil.rmtree, work, True)
        shutil.copy(FIXTURES / "pr288-regression/preview.html", work / "preview.html")
        plan = raw_intake.intake({
            "subject": "Physics",
            "prompts": ["Projectile motion six-Core set for the owner's five anchors."],
            "syllabus": ["Independent perpendicular components", "Componentwise constant acceleration",
                         "Gravity-only projectile model"],
            "questions": ["Q28", "Q15", "Q21", "Q26", "Q23"],
        })
        ledger = [{"input_id": s["id"], "kind": "syllabus", "teaching": "preview.html#CORE1A",
                   "practice": "preview.html#CORE2A", "learner_location": "preview.html#CORE1"}
                  for s in plan["inputs"]["syllabus"]]
        ledger += [{"input_id": q["id"], "kind": "question", "teaching": "preview.html#CORE1A",
                    "practice": "preview.html#CORE2", "learner_location": "preview.html#CORE2",
                    "status": "HOLD"} for q in plan["inputs"]["questions"]]
        manifest = {
            "intake": plan, "ledger": ledger, "status": "STRUCTURALLY_VALIDATED_WITH_HOLDS",
            "evidence": {"research": [], "identities": [
                {"input_id": plan["inputs"]["questions"][1]["id"], "status": "IDENTITY_HOLD",
                 "candidates_considered": [{"label": "candidate A"}, {"label": "candidate B"}]}]},
            "products": {"book": "preview.html", "pages": ["preview.html"], "question_bank": "bank.json",
                         "atlas": "preview.html", "builder": "preview.html"},
            "diagnostic": {"location": "preview.html#diagnostic"},
        }
        (work / "delivery.json").write_text(json.dumps(manifest), encoding="utf-8")
        report = delivery_gate.check(work / "delivery.json", BENCHMARK)
        self.assertFalse(report["passed"])
        for code in ("learner_text_placeholder", "hold_as_state", "identity_unresolved", "research_open",
                     "product_missing", "question_not_rendered", "diagnostic_missing", "benchmark_book_pages"):
            self.assertIn(code, report["codes"])


class EntryAndCliTests(unittest.TestCase):
    def test_cli_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp)
            subprocess.run(["python3", "Shared/tools/learner_product_render.py", "--bundle",
                            str(FIXTURES / "mathematics-quadratics.json"), "--out", str(out)],
                           cwd=REPO, check=True, stdout=subprocess.PIPE)
            gate = subprocess.run(["python3", "Shared/tools/delivery_gate.py", "--manifest", str(out / "delivery.json")],
                                  cwd=REPO, stdout=subprocess.PIPE, text=True)
            self.assertEqual(gate.returncode, 0, gate.stdout[-2000:])
            request = out / "request.json"
            request.write_text(json.dumps(load("chemistry-mole-concept")["request"]), encoding="utf-8")
            intake = subprocess.run(["python3", "Shared/tools/raw_intake.py", "--input", str(request)],
                                    cwd=REPO, stdout=subprocess.PIPE, text=True)
            self.assertEqual(intake.returncode, 0)
            self.assertEqual(json.loads(intake.stdout)["status"], "RESEARCH_AND_AUTHOR")

    def test_browser_entry_matches_python_intake(self):
        for command in (["node", "--check", "public/js/raw-intake.js"],
                        ["node", "--test", "tests/raw_intake.test.mjs"]):
            done = subprocess.run(command, cwd=REPO, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            self.assertEqual(done.returncode, 0, done.stdout[-3000:])


if __name__ == "__main__":
    unittest.main()
