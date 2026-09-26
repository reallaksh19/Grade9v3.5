#!/usr/bin/env python3
"""Final output gate for research-first learner-product jobs.

The gate reads the delivery manifest, then checks the rendered learner product itself.
A manifest that points at files is not evidence; a labelled gap is not a pass. It fails
when any of the following is true:

  * a product file is missing, or learner-facing text carries a hold, placeholder or
    "pending" marker (in the book, a web page, the atlas, the builder or the bank);
  * any supplied question or syllabus subtopic (or a subtopic research added) has no
    ledger row, or a ledger location does not resolve to an element on a rendered page;
  * a teaching location lacks explanation, a worked example with steps, or a visual;
  * a practice location lacks an attempt prompt placed before its worked answer, or a
    supplied question's text is not actually rendered there;
  * a source identity is displayed without a resolved claim, or a claim is not backed by
    source text whose wording and stated conditions match the supplied question, or
    several candidates were considered without a recorded discriminator;
  * a research task from the intake has no completed evidence with a source locator;
  * the product has no short diagnostic, or the atlas/builder do not link the pages;
  * with --benchmark: the book or bank is below the reference thresholds.

Usage:
    python3 Shared/tools/delivery_gate.py --manifest DIR/delivery.json [--benchmark FILE]
"""
from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import raw_intake  # noqa: E402

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
HIDDEN = {"script", "style"}


class Node:
    __slots__ = ("tag", "attrs", "children", "text", "parent", "order")

    def __init__(self, tag: str, attrs: dict, parent: "Node | None", order: int):
        self.tag, self.attrs, self.parent, self.order = tag, attrs, parent, order
        self.children: list[Node] = []
        self.text: list[str] = []

    def walk(self):
        yield self
        for child in self.children:
            yield from child.walk()

    def all_text(self) -> str:
        if self.tag in HIDDEN:
            return ""
        return " ".join([*self.text, *(c.all_text() for c in self.children)])

    def find(self, pred) -> list["Node"]:
        return [n for n in self.walk() if pred(n)]


class Tree(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.root = Node("#root", {}, None, 0)
        self.cur = self.root
        self.count = 0

    def handle_starttag(self, tag, attrs):
        self.count += 1
        node = Node(tag, {k: (v or "") for k, v in attrs}, self.cur, self.count)
        self.cur.children.append(node)
        if tag not in VOID:
            self.cur = node

    def handle_startendtag(self, tag, attrs):
        self.count += 1
        self.cur.children.append(Node(tag, {k: (v or "") for k, v in attrs}, self.cur, self.count))

    def handle_endtag(self, tag):
        node = self.cur
        while node is not self.root and node.tag != tag:
            node = node.parent
        if node is not self.root:
            self.cur = node.parent

    def handle_data(self, data):
        self.cur.text.append(data)


def parse(text: str) -> Node:
    tree = Tree()
    tree.feed(text)
    return tree.root


def role(node: Node, name: str) -> bool:
    return node.attrs.get("data-role") == name


def words(text: str) -> list[str]:
    return re.findall(r"[A-Za-z0-9]+", text)


def overlap(needle: str, haystack: str) -> float:
    a = set(raw_intake.tokens(needle))
    return 1.0 if not a else len(a & set(raw_intake.tokens(haystack))) / len(a)


class Gate:
    def __init__(self, manifest_path: Path, workflow: dict | None = None, benchmark: dict | None = None):
        self.base = manifest_path.parent
        self.manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.workflow = workflow or raw_intake.load_workflow()
        self.cfg = self.workflow["gate"]
        self.benchmark = benchmark
        self.findings: list[dict] = []
        self.docs: dict[str, Node] = {}
        self.raw: dict[str, str] = {}

    def fail(self, code: str, where: str, detail: str) -> None:
        self.findings.append({"code": code, "where": where, "detail": detail})

    # ---- loading
    def page(self, rel: str) -> Node | None:
        rel = posixpath.normpath(rel)
        if rel not in self.docs:
            path = self.base / rel
            if not path.is_file():
                return None
            self.raw[rel] = path.read_text(encoding="utf-8")
            self.docs[rel] = parse(self.raw[rel])
        return self.docs[rel]

    def locate(self, ref: str | None, where: str) -> Node | None:
        if not ref or "#" not in ref:
            self.fail("location_unresolved", where, f"location {ref!r} is not page#anchor")
            return None
        rel, anchor = ref.split("#", 1)
        doc = self.page(rel)
        if doc is None:
            self.fail("location_unresolved", where, f"{rel} does not exist")
            return None
        hits = doc.find(lambda n: n.attrs.get("id") == anchor)
        if not hits:
            self.fail("location_unresolved", where, f"{rel} has no element #{anchor}")
            return None
        return hits[0]

    # ---- checks
    def check_products(self) -> None:
        products = self.manifest.get("products", {})
        rels = [products.get(k) for k in ("book", "atlas", "builder", "question_bank")] + list(products.get("pages", []))
        for key in ("book", "atlas", "builder", "question_bank"):
            if not products.get(key):
                self.fail("product_missing", "products", f"no {key} declared")
        if not products.get("pages"):
            self.fail("product_missing", "products", "no web pages declared")
        forbidden = [re.compile(p) for p in self.cfg["forbidden_learner_text"]]
        for rel in filter(None, rels):
            path = self.base / rel
            if not path.is_file():
                self.fail("product_missing", rel, "declared product file does not exist")
                continue
            if rel.endswith(".html"):
                text = self.page(rel).all_text()
            else:
                text = " ".join(_strings(json.loads(path.read_text(encoding="utf-8"))))
            for pattern in forbidden:
                match = pattern.search(text)
                if match:
                    self.fail("learner_text_placeholder", rel, f"learner-facing text contains {match.group(0)!r}")
        status = json.dumps({k: self.manifest.get(k) for k in ("status", "ledger")})
        if re.search(r"\b[A-Z_]*HOLD\b", status):
            self.fail("hold_as_state", "delivery.json", "a hold is recorded as a delivery or ledger state")

    def check_ledger(self) -> None:
        intake = self.manifest.get("intake", {})
        inputs = intake.get("inputs", {})
        rows = {row.get("input_id"): row for row in self.manifest.get("ledger", [])}
        required = [(q["id"], "question") for q in inputs.get("questions", [])] + \
                   [(s["id"], "syllabus") for s in inputs.get("syllabus", [])]
        required += [(r["input_id"], r["kind"]) for r in self.manifest.get("ledger", [])
                     if r.get("kind") == "research_subtopic"]
        questions = {q["id"]: q for q in inputs.get("questions", [])}
        bank_ids = {u.get("id") for u in self._bank_units()}
        for input_id, kind in required:
            row = rows.get(input_id)
            if not row:
                self.fail("input_not_in_ledger", input_id, f"supplied {kind} has no coverage ledger row")
                continue
            teach = self.locate(row.get("teaching"), f"{input_id}.teaching")
            practice = self.locate(row.get("practice"), f"{input_id}.practice")
            self.locate(row.get("learner_location"), f"{input_id}.learner_location")
            if teach is not None:
                self.check_teaching(teach, f"{input_id}.teaching")
            if practice is not None:
                self.check_practice(practice, f"{input_id}.practice")
            if kind == "question":
                if input_id not in bank_ids:
                    self.fail("question_not_in_bank", input_id, "supplied question is missing from the question bank")
                q = questions[input_id]
                shown = practice.all_text() if practice is not None else ""
                text = q["text"] or self._recovered_text(input_id)
                if not text:
                    self.fail("question_not_rendered", input_id, "label-only question has no recovered text")
                elif overlap(text, shown) < self.cfg["question_rendered_overlap"]:
                    self.fail("question_not_rendered", input_id, "question text is not rendered at its practice location")

    def check_teaching(self, node: Node, where: str) -> None:
        paragraphs = [p for p in node.find(lambda n: n.tag == "p") if len(words(p.all_text())) >= 12]
        if not paragraphs:
            self.fail("teaching_incomplete", where, "no explanation paragraph")
        worked = node.find(lambda n: role(n, "worked-example"))
        steps = [li for w in worked for li in w.find(lambda n: n.tag == "li") if words(li.all_text())]
        if len(steps) < self.cfg["min_worked_steps"]:
            self.fail("teaching_incomplete", where, "no worked example with steps")
        if not self._visuals(node):
            self.fail("teaching_incomplete", where, "no visual with an accessible title")

    def check_practice(self, node: Node, where: str) -> None:
        items = [node] if role(node, "question") else node.find(lambda n: role(n, "question"))
        if not items:
            self.fail("practice_incomplete", where, "no practice question")
        for item in items:
            attempts = item.find(lambda n: role(n, "attempt"))
            answers = item.find(lambda n: role(n, "answer"))
            if not attempts or not answers:
                self.fail("practice_incomplete", where, "question lacks an attempt prompt or a worked answer")
                continue
            if min(a.order for a in answers) < min(a.order for a in attempts):
                self.fail("answer_before_attempt", where, "worked answer appears before the attempt prompt")
            if not any(len(a.find(lambda n: n.tag == "li")) >= self.cfg["min_worked_steps"] for a in answers):
                self.fail("practice_incomplete", where, "worked answer has fewer steps than required")
            if answers[0].tag != "details" and not answers[0].attrs.get("hidden"):
                self.fail("answer_before_attempt", where, "worked answer is not concealed until opened")

    def check_identities(self) -> None:
        questions = {q["id"]: q for q in self.manifest.get("intake", {}).get("inputs", {}).get("questions", [])}
        claims = {row.get("input_id"): row for row in self.manifest.get("evidence", {}).get("identities", [])}
        for qid, q in questions.items():
            row = claims.get(qid)
            if q.get("identity_claim_requested") and not row:
                self.fail("identity_unresolved", qid, "identity was requested but no research record exists")
                continue
            if not row:
                continue
            status = row.get("status")
            if status not in {"RESOLVED", "NOT_CLAIMED"}:
                self.fail("identity_unresolved", qid, f"identity status {status!r} is not a delivery state")
                continue
            text = q["text"] or self._recovered_text(qid)
            if status == "RESOLVED":
                source = row.get("source_text", "")
                ident = row.get("identity") or {}
                if not ident.get("label") or not ident.get("locator"):
                    self.fail("identity_unresolved", qid, "resolved identity lacks a label or locator")
                if overlap(text, source) < self.cfg["identity_text_overlap"]:
                    self.fail("identity_text_mismatch", qid, "source text wording does not match the question")
                missing = [c for c in raw_intake.conditions(text) if c not in raw_intake.conditions(source)]
                if missing:
                    self.fail("identity_condition_mismatch", qid, f"stated conditions {missing} are absent from the source text")
                if len(row.get("candidates_considered", [])) > 1 and not row.get("discriminator"):
                    self.fail("identity_discriminator_missing", qid, "several candidates considered, none ruled out")
            else:
                for label in filter(None, [(row.get("identity") or {}).get("label"), q.get("source_hint")]):
                    for rel in self.manifest.get("products", {}).get("pages", []) + [self.manifest["products"].get("book", "")]:
                        doc = self.page(rel) if rel else None
                        if doc and label in doc.all_text():
                            self.fail("identity_displayed_without_claim", qid, f"{rel} shows {label!r} without a resolved claim")

    def check_research(self) -> None:
        records = self.manifest.get("evidence", {}).get("research", [])
        for task in self.manifest.get("intake", {}).get("research_tasks", []):
            ok = [r for r in records if task["input_id"] in r.get("input_ids", [])
                  and task["kind"] in r.get("kinds", []) and r.get("status") == "DONE"
                  and any(s.get("locator") for s in r.get("sources", []))]
            if not ok:
                self.fail("research_open", task["id"], "no completed research evidence with a source locator")

    def check_diagnostic_and_links(self) -> None:
        diag = self.locate((self.manifest.get("diagnostic") or {}).get("location"), "diagnostic")
        need = self.workflow["default_learner_start"]["diagnostic"]["min_items"]
        if diag is None or len(diag.find(lambda n: role(n, "attempt"))) < need:
            self.fail("diagnostic_missing", "diagnostic", f"fewer than {need} diagnostic attempts")
        products = self.manifest.get("products", {})
        for key, targets in (("atlas", products.get("pages", [])),
                             ("builder", [products.get("atlas"), products.get("book")] + products.get("pages", []))):
            rel = products.get(key)
            doc = self.page(rel) if rel else None
            if doc is None:
                continue
            linked = {posixpath.normpath(posixpath.join(posixpath.dirname(rel), a.attrs["href"].split("#")[0]))
                      for a in doc.find(lambda n: n.tag == "a" and n.attrs.get("href"))}
            for target in filter(None, targets):
                if posixpath.normpath(target) not in linked:
                    self.fail("link_missing", rel, f"{key} does not link {target}")

    def check_benchmark(self) -> None:
        if not self.benchmark:
            return
        book = self.page(self.manifest["products"]["book"])
        pages = book.find(lambda n: "book-page" in n.attrs.get("class", "").split()) if book else []
        thin = [p.attrs.get("id") for p in pages if len(words(p.all_text())) < self.cfg["min_words_per_book_page"]]
        if thin:
            self.fail("book_page_thin", "book", f"pages below {self.cfg['min_words_per_book_page']} words: {thin}")
        if len(pages) < self.benchmark["min_book_pages"]:
            self.fail("benchmark_book_pages", "book", f"{len(pages)} pages < {self.benchmark['min_book_pages']}")
        units = [u for u in self._bank_units() if u.get("text") and u.get("steps") and u.get("visual")]
        if len(units) < self.benchmark["min_question_visual_units"]:
            self.fail("benchmark_bank_units", "question_bank",
                      f"{len(units)} question+visual units < {self.benchmark['min_question_visual_units']}")

    # ---- helpers
    def _bank_units(self) -> list[dict]:
        rel = self.manifest.get("products", {}).get("question_bank")
        path = self.base / rel if rel else None
        if not path or not path.is_file():
            return []
        return json.loads(path.read_text(encoding="utf-8")).get("units", [])

    def _recovered_text(self, qid: str) -> str:
        return next((u.get("text", "") for u in self._bank_units() if u.get("id") == qid), "")

    @staticmethod
    def _visuals(node: Node) -> list[Node]:
        out = []
        for fig in node.find(lambda n: role(n, "visual")):
            for img in fig.find(lambda n: n.tag in {"svg", "img"}):
                titled = img.attrs.get("alt") or any(t.tag == "title" and t.all_text().strip() for t in img.walk())
                shapes = img.find(lambda n: n.tag in {"line", "path", "rect", "circle", "polyline", "polygon"})
                if titled and (img.tag == "img" or len(shapes) >= 3):
                    out.append(img)
        return out

    def run(self) -> dict:
        self.check_products()
        self.check_ledger()
        self.check_identities()
        self.check_research()
        self.check_diagnostic_and_links()
        self.check_benchmark()
        return {"passed": not self.findings, "findings": self.findings,
                "codes": sorted({f["code"] for f in self.findings})}


def _strings(value) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, dict):
        return [s for v in value.values() for s in _strings(v)]
    if isinstance(value, list):
        return [s for v in value for s in _strings(v)]
    return []


def check(manifest: Path, benchmark: Path | dict | None = None) -> dict:
    if isinstance(benchmark, Path):
        benchmark = json.loads(benchmark.read_text(encoding="utf-8"))
    return Gate(manifest, benchmark=benchmark).run()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", required=True)
    parser.add_argument("--benchmark")
    args = parser.parse_args(argv)
    report = check(Path(args.manifest), Path(args.benchmark) if args.benchmark else None)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
