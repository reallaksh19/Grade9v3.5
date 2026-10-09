#!/usr/bin/env python3
"""Check the IMO Core1A TEST teaching preview and honest Core2 PDF-acquisition holds."""
from __future__ import annotations

import argparse
import json
import sys
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "TEST" / "imo-research"))
from validate_qualification_evidence import git_blob_sha  # noqa: E402
from validate_core1a_candidate_package import (  # noqa: E402
    IMOCore1ACandidateError, validate_package
)
from validate_seed import SeedError  # noqa: E402
from validate_core_pilot_research import validate_census  # noqa: E402

PKG = REPO / "TEST/library/imo-g9-divisibility-core1a.v1.json"
QUEUE = REPO / "TEST/imo-research/intake/core2-source-acquisition-handoff.v1.json"
RECEIPT = REPO / "TEST/imo-research/intake/core1a-test-review-receipt.v1.json"
SOURCE = REPO / "TEST/imo-research/seed/sources.json"
SAMPLE = REPO / "TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json"
CENSUS = REPO / "TEST/imo-research/intake/core2-source-custody-eligibility.v1.json"
PUB = REPO / "public/test/imo-grade9/core1a.html"
DOCS = REPO / "docs/test/imo-grade9/core1a.html"
MATH_PUB = REPO / "public/mathematics/imo-grade9/index.html"
MATH_DOCS = REPO / "docs/mathematics/imo-grade9/index.html"
MAIN_SHA = "a5d80f7f9ade751eacb05c75d688e0202f9acaf6"
PKG_BLOB = "cbcfe1ffe69b7453a53ca3608f5b563b0f91776e"
SOURCE_BLOB = "4057e7642402915e9dacdb4b54fc7fbe9b42867f"
CENSUS_BLOB = "800a2f693e1b46162a026375c5854ad4b8b05257"
SAMPLE_BLOB = "95cdfc8dd277b1b9fcd78c05828b501361f1e763"


class PreviewError(ValueError):
    pass


def demand(ok: bool, why: str) -> None:
    if not ok:
        raise PreviewError(why)


def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise PreviewError(f"unreadable {path}: {exc}") from exc


def load(path: Path) -> dict:
    try:
        value = json.loads(read(path))
    except json.JSONDecodeError as exc:
        raise PreviewError(f"invalid JSON {path}: {exc}") from exc
    demand(isinstance(value, dict), "expected a JSON object")
    return value


class ReviewHTML(HTMLParser):
    """Read rendered text by teaching-step, exit-step and residue, not just regex."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.text = []
        self.steps: dict[str, str] = {}
        self.exit: dict[str, str] = {}
        self.residues: dict[str, str] = {}
        self.mode: str | None = None
        self.key: str | None = None
        self.details = 0
        self.model_reveal_closed = True
        self.summary_inside = False
        self.unsafe_links = []
        self.labels = []
        self.exit_field = False

    def handle_starttag(self, tag, attrs):
        att = dict(attrs)
        if tag == "li" and "data-core1a-step-id" in att:
            self.key = att["data-core1a-step-id"]
            demand(self.key not in self.steps, "duplicate Core1A teaching step")
            self.mode = "steps"
            self.steps[self.key] = ""
        if tag == "li" and "data-exit-reasoning" in att:
            self.key = att["data-exit-reasoning"]
            demand(self.key not in self.exit, "duplicate exit reasoning step")
            self.mode = "exit"
            self.exit[self.key] = ""
        if tag == "tr" and "data-residue" in att:
            self.key = att["data-residue"]
            demand(self.key not in self.residues, "duplicate residue class")
            self.mode = "residues"
            self.residues[self.key] = ""
        if tag == "details" and att.get("id") == "exit-model-closure":
            self.details += 1
            if "open" in att:
                self.model_reveal_closed = False
        if tag == "summary":
            self.summary_inside = True
        if tag == "textarea" and att.get("id") == "exit-response":
            self.exit_field = True
        if tag == "label":
            self.labels.append(att.get("for"))
        if tag in {"script", "img", "iframe", "form"}:
            if tag != "script" or not att.get("src", "").startswith("../../js/"):
                self.unsafe_links.append(tag)
        if tag == "a":
            href = att.get("href", "")
            if href.startswith(("http:", "https:", "javascript:", "data:")):
                self.unsafe_links.append("external or active anchor")

    def handle_data(self, data):
        self.text.append(data)
        if self.mode is not None and self.key is not None:
            target = getattr(self, self.mode)
            target[self.key] += data

    def handle_endtag(self, tag):
        if (tag == "li" and self.mode in {"steps", "exit"}) or (
                tag == "tr" and self.mode == "residues"):
            self.mode = None
            self.key = None
        if tag == "summary":
            self.summary_inside = False


def validate_preview(
    pkg_path: Path = PKG, preview: Path = PUB, mirror: Path = DOCS,
    math_pub: Path = MATH_PUB, math_docs: Path = MATH_DOCS,
    receipt_path: Path = RECEIPT, queue_path: Path = QUEUE,
) -> dict:
    try:
        validate_package(pkg_path)
        validate_census()
    except (IMOCore1ACandidateError, SeedError) as exc:
        raise PreviewError(f"upstream source/Core1A candidate invalid: {exc}") from exc
    pkg = load(pkg_path)
    micro = pkg["microtopics"][0]
    bucket = pkg["buckets"][0]
    rep = pkg["representations"][0]
    page_text = read(preview)
    demand(page_text == read(mirror), "TEST public/docs pages diverge")
    demand(read(math_pub) == read(math_docs), "Mathematics site mirrors diverge")
    demand('data-test-review-link="IMO-G9-CORE1A-CANDIDATE"' in read(math_pub)
           and 'href="../../test/imo-grade9/core1a.html"' in read(math_pub),
           "Mathematics topic browser loses clearly labeled TEST review link")

    demand('data-g9-role="TEST"' in page_text
           and 'data-g9-test="sandbox-draft"' in page_text
           and 'data-g9-preview-core="CORE1A"' in page_text
           and 'data-g9-canonical-acceptance="false"' in page_text
           and 'data-g9-role="CORE1A"' not in page_text,
           "review preview incorrectly marketed as canonical Core1A")
    demand("TEST REVIEW ONLY · CANDIDATE" in page_text
           and "real device, keyboard, assistive-technology and print inspections are NOT RUN" in page_text
           and "not an academically accepted Core 1A product" in page_text,
           "TEST and unperformed QA disclosure must be visible")
    demand("SOF-IMO-G09-" not in page_text and
           "http://sofworld.org" not in page_text and
           "https://sofworld.org" not in page_text,
           "source-paper item/URL inserted into authored concept review")
    h = ReviewHTML()
    h.feed(page_text)
    all_text = " ".join(h.text)
    demand(h.details == 1 and h.model_reveal_closed
           and "exit-response" in h.labels and h.exit_field,
           "exit task disclosure must be initially closed and response accessible")
    demand(not h.unsafe_links, "unexpected external script/media/form/link")
    demand(all(k in all_text for k in (pkg["package_id"],
           micro["inferential_jump"], micro["exit_task"]["prompt"])),
           "candidate package identity, decisive inference or exit prompt missing")
    for assumption in micro["entry_assumptions"]:
        demand(assumption in all_text, "required entry assumption dropped")
    for convention in bucket["conventions"]:
        demand(convention["statement"] in all_text, "domain convention dropped")
    steps = micro["teaching_path"]
    demand(list(h.steps) == [step["id"] for step in steps],
           "ordered canonical four-move construction altered")
    for step in steps:
        section = h.steps[step["id"]]
        demand(all(x in section for x in (
            step["action"], step["output"], step["why_valid"])),
            "teaching step loses action/output or why-valid proof")
    demand(rep["id"] in page_text and set(h.residues) == {"0", "1", "2"}
           and "Exhaustive modulo-3 cases" in all_text,
           "text-symbol-table representation bridge is incomplete")
    for i,factor in [("0","n"),("1","n+2"),("2","n+1")]:
        demand(factor in h.residues[i] and
               "remainder" in h.residues[i].lower(),
               f"residue {i} table missing labelled guaranteed factor")
    mis = micro["misconceptions"][0]
    demand(all(mis[k] in all_text for k in (
        "wrong_idea", "diagnostic_prompt", "repair")),
        "wrong path, diagnostic and repair not constructed")
    model = micro["exit_task"]["answer"]
    demand(list(h.exit) == ["1","2","3","4"]
           and all(x in h.exit[str(i)] for i,x in enumerate(model["reasoning"],1))
           and model["summary"] in all_text
           and model["check"] in all_text,
           "authored independent exit proof or check removed")
    demand("no automatic proof grading" in page_text.lower()
           or "No accepted QRT cells, automatic proof grading" in page_text,
           "must not claim trained response scoring")
    demand("does not submit or save them" in page_text,
           "response collection safety must be disclosed")

    queue = load(queue_path)
    demand(queue.get("schema") == "imo-g9-source-acquisition-handoff-queue-v1"
           and queue.get("responsibility_issue") == 301
           and queue.get("base_main_sha") == MAIN_SHA
           and queue.get("source_positions") == 68
           and queue.get("source_documents") == 4
           and queue.get("retained_pdf_documents") == 0
           and queue.get("verified_sha256_documents") == 0
           and queue.get("source_core2_eligible") == 0
           and queue.get("source_core2_admitted") == 0
           and queue.get("qrt_accepted") == 0
           and queue.get("publisher_pdf_redistribution_rights_claimed") is False
           and queue.get("all_documents_pending") is True
           and queue.get("source_pdf_contents_embedded") is False
           and queue.get("test_preview_uses_original_sof_source_text") is False,
           "pending source custody and zero-admission boundary falsely upgraded")
    pins = [
        ("TEST/imo-research/seed/sources.json", SOURCE_BLOB, SOURCE),
        ("TEST/imo-research/intake/core2-source-custody-eligibility.v1.json", CENSUS_BLOB, CENSUS),
        ("TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json", SAMPLE_BLOB, SAMPLE),
    ]
    demand(queue.get("inputs") == [
        {"path":path, "git_blob_sha":sha} for path,sha,_ in pins
    ], "source-byte queue exact input lineage changed")
    for path,sha,file in pins:
        demand(git_blob_sha(file) == sha, f"{path}: pinned historical research drifted")
    ledger=load(SOURCE)
    sample=load(SAMPLE)
    census=load(CENSUS)
    expected_counts={}
    for row in census["records"]:
        k=row["source_id"]
        expected_counts[k] = expected_counts.get(k,0)+1
    srcs=ledger["sources"]
    items=queue.get("source_documents_queue")
    demand(isinstance(items,list) and len(items) == len(srcs),
           "must retain each of four source PDFs")
    for original,row in zip(srcs,items):
        expected_url=(sample["official_source_url"] if "SAMPLE" in original["source_id"]
                      else original["url"])
        demand(row.get("source_id") == original["source_id"]
               and row.get("origin_host_kind") == original["host_type"]
               and row.get("source_locator_claim") == original["url"]
               and row.get("requested_pdf_url") == expected_url
               and type(row.get("position_count_in_68")) is int
               and row["position_count_in_68"] == expected_counts[original["source_id"]],
               "source URL, mirror-vs-organizer host or position census altered")
        for name in ("document_pdf_obtained","bytes_retained",
                     "source_locator_verified_for_all_positions",
                     "seven_component_custody_complete",
                     "source_answer_independently_reconciled_for_all_positions",
                     "source_core2_eligible"):
            demand(row.get(name) is False, "pretend Core2 acquisition/qualification")
        for name in ("acquired_at","acquisition_receipt_ref","document_sha256",
                     "actual_pdf_byte_length"):
            demand(row.get(name) is None, "invented PDF bytes, digest or receipt")
        demand(row.get("publisher_reproduction_permission") == "NOT_REVIEWED"
               and row.get("external_reference_rights_decision") == "NOT_REVIEWED"
               and isinstance(row.get("next_steps"),list)
               and len(row["next_steps"]) == 4,
               "fabricated publisher rights or missing source actions")

    receipt=load(receipt_path)
    demand(receipt.get("schema") == "imo-g9-core1a-test-review-render-receipt-v1"
           and receipt.get("issue") == 301
           and receipt.get("main_parent") == MAIN_SHA
           and receipt.get("status") ==
               "STATIC_TEST_REVIEW_CANDIDATE_NOT_PRODUCT_ACCEPTANCE"
           and receipt.get("package_id") == pkg["package_id"]
           and receipt.get("package_status") == "CANDIDATE"
           and receipt.get("input_package_git_blob_sha") == PKG_BLOB
           and git_blob_sha(pkg_path) == PKG_BLOB
           and receipt.get("canonical_pipeline_rendered") is False
           and receipt.get("html_static_review_exists") is True
           and receipt.get("emitted_html_passes_real_browser_test") is False
           and receipt.get("no_auto_promotion") is True,
           "unearned canonical rendering, review status or package lineage")
    expected_pages=[
        {"path":"public/test/imo-grade9/core1a.html","git_blob_sha":git_blob_sha(preview)},
        {"path":"docs/test/imo-grade9/core1a.html","git_blob_sha":git_blob_sha(mirror)},
    ]
    expected_links=[
        {"path":"public/mathematics/imo-grade9/index.html","git_blob_sha":git_blob_sha(math_pub)},
        {"path":"docs/mathematics/imo-grade9/index.html","git_blob_sha":git_blob_sha(math_docs)},
    ]
    demand(receipt.get("derived_review_pages") == expected_pages
           and receipt.get("mathematics_topic_links") == expected_links
           and receipt.get("core2_source_acquisition_handoff") == {
              "path":"TEST/imo-research/intake/core2-source-acquisition-handoff.v1.json",
              "git_blob_sha":git_blob_sha(queue_path)
           }, "review artifact/page/source-queue Git blob receipts stale")
    checks=receipt.get("review_checks",{})
    for x in ("accessibility_keyboard","assistive_technology_screen_reader",
              "responsive_visual_browser","printed_pdf_layout",
              "independent_learner_comprehension"):
        demand(checks.get(x) == "NOT_RUN", "actual device/learner review falsely claimed")
    for x in ("formal_math_academic_acceptance","owner_product_acceptance"):
        demand(checks.get(x) == "NOT_GRANTED", "academic/product acceptance falsely claimed")
    demand(receipt.get("content_claims") == {
        "source_core2_question_count":0,
        "canonical_core1a_admitted":0,
        "qrt_accepted":0,
        "original_sof_stems_embedded":0,
        "test_page_publicly_addressable_as_preview":True,
        "published_canonical_learner_product":False,
    }, "published preview confused with approved canonical learner product")
    return {
        "result":"IMO_G9_TEST_CORE1A_REVIEW_PAGE_UNAPPROVED",
        "teaching_steps":len(steps),
        "residue_table_cases":len(h.residues),
        "model_exit_steps":len(model["reasoning"]),
        "review_page_mirrors":2,
        "source_pdfs_pending":len(items),
        "source_positions_held":sum(expected_counts.values()),
        "source_sha256_receipts":0,
        "source_core2_admitted":0,
        "canonical_core1a_admitted":0,
        "qrt_accepted":0,
        "browser_a11y_and_print_review":"NOT_RUN",
    }


def main() -> None:
    parser=argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--preview",type=Path,default=PUB)
    parser.add_argument("--mirror",type=Path,default=DOCS)
    parser.add_argument("--math-public",type=Path,default=MATH_PUB)
    parser.add_argument("--math-docs",type=Path,default=MATH_DOCS)
    parser.add_argument("--receipt",type=Path,default=RECEIPT)
    parser.add_argument("--queue",type=Path,default=QUEUE)
    args=parser.parse_args()
    try:
        print(json.dumps(validate_preview(
            preview=args.preview,mirror=args.mirror,
            math_pub=args.math_public,math_docs=args.math_docs,
            receipt_path=args.receipt,queue_path=args.queue
        ),sort_keys=True))
    except PreviewError as exc:
        parser.exit(1,f"IMO_CORE1A_PREVIEW_INVALID: {exc}\n")


if __name__=="__main__":
    main()
