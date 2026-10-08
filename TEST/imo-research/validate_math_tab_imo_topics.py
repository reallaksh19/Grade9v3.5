#!/usr/bin/env python3
"""Fail-closed check for the Maths-tab IMO Grade 9 research directory and mirrors."""
from __future__ import annotations

import argparse
import html
import json
import sys
from collections import Counter, defaultdict
from html.parser import HTMLParser
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "TEST" / "imo-research"))
from validate_qualification_evidence import git_blob_sha  # noqa: E402

INDEX = REPO / "Mathematics" / "research" / "imo-g9-topic-browser.v1.json"
PUBLIC = REPO / "public" / "mathematics" / "imo-grade9" / "index.html"
DOCS = REPO / "docs" / "mathematics" / "imo-grade9" / "index.html"
PUBLIC_HUB = REPO / "public" / "mathematics" / "index.html"
DOCS_HUB = REPO / "docs" / "mathematics" / "index.html"
SOURCE_PATHS = (
    ("TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl",
     "80816f9bb5a579f4c822a477ce53e8b98be1381b"),
    ("TEST/imo-research/taxonomy/sof-class9-topic-registry.v1.json",
     "718b227c475e5d593b6b3254146a0432a64ea90c"),
    ("TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json",
     "95cdfc8dd277b1b9fcd78c05828b501361f1e763"),
    ("TEST/imo-research/seed/sources.json",
     "4057e7642402915e9dacdb4b54fc7fbe9b42867f"),
    ("TEST/imo-research/original-practice/seven-cell-original-problems.v1.json",
     "8ee7cc78f34cc1fa640e4abac84620f43d5538c1"),
    ("TEST/imo-research/adjudication/source-discrepancy-register.v1.json",
     "4761aecd4e54c0c694026ab10c4aa7cbfa539e56"),
)
PRACTICE_TOPICS = ("NS", "COORD", "TRIANGLE_AREAS", "MENSURATION",
                   "LIN_EQ", "LIN_EQ", "COORD")
TOP_KEYS = {
    "schema","responsibility_issue","source_research_basis_main",
    "source_git_blobs","editorial_status","rights_policy","placement",
    "publication_scope","publication_not_equal_core_acceptance",
    "historic_source_seed_positions","additional_organizer_sample_source_positions",
    "displayed_source_references","displayed_authored_practice_previews",
    "canonical_qrt_accepted","source_core2_admitted","authored_core_admitted",
    "official_syllabus_topics_referenced","taxonomy_topics","topic_counts","records"
}
SOURCE_KEYS = {
    "id","kind","topic_id","subtopic_id","concept_summary","source_id",
    "source_pdf_url","original_number_claim","exam_section",
    "printed_source_verbatim_present","source_custody","rights_status",
    "qrt_accepted","core2_admitted","discrepancy_case",
    "source_membership","source_stem","source_options","source_figure","answer"
}
PRACTICE_KEYS = {
    "id","kind","topic_id","title","stem","format","difficulty_proposal",
    "provisional_curriculum_scope","original_source_claim","origin",
    "question_display_authorization","qrt_accepted","core2_admitted",
    "core1a_admitted","learner_core_product_published","answer","source_membership"
}

class TopicBrowserError(ValueError):
    pass

def ensure(ok: bool, message: str) -> None:
    if not ok:
        raise TopicBrowserError(message)

def load(path: Path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise TopicBrowserError(f"unreadable {path}: {exc}") from exc

def read(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise TopicBrowserError(f"unreadable {path}: {exc}") from exc

def jsonl(path: Path):
    try:
        return [json.loads(line) for line in read(path).splitlines() if line.strip()]
    except json.JSONDecodeError as exc:
        raise TopicBrowserError(f"bad JSONL {path}: {exc}") from exc

class PageHTML(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.items = {}
        self.sections = {}
        self.links = {}
        self.active_item = None
        self.active_section = None
        self.labels = defaultdict(list)
        self.attrs = {}
    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class","").split()
        if tag == "section" and "imo-topic" in classes:
            self.active_section = attrs.get("data-topic")
            ensure(self.active_section not in self.sections,
                   "duplicate topic HTML section")
            self.sections[self.active_section] = 0
        if tag == "li" and "imo-item" in classes:
            id = attrs.get("id")
            ensure(id and id not in self.items and self.active_section,
                   "duplicate/malformed item ID or missing section")
            self.active_item = id
            self.items[id] = {
                "kind": attrs.get("data-kind"),
                "topic": self.active_section,
                "text": "",
                "urls": [],
            }
            self.sections[self.active_section] += 1
        if tag == "a" and self.active_item is not None:
            self.items[self.active_item]["urls"].append(attrs.get("href"))
            ensure(attrs.get("target") != "_blank" or
                   attrs.get("rel") == "noopener noreferrer",
                   "external link lacks noreferrer/noopener")
    def handle_data(self, data):
        if self.active_item is not None:
            self.items[self.active_item]["text"] += data
    def handle_endtag(self, tag):
        if tag == "li" and self.active_item is not None:
            self.active_item = None
        if tag == "section" and self.active_section is not None:
            self.active_section = None

def validate_directory(
    index: Path = INDEX, public: Path = PUBLIC, docs: Path = DOCS,
    public_hub: Path = PUBLIC_HUB, docs_hub: Path = DOCS_HUB
) -> dict:
    d = load(index)
    ensure(isinstance(d,dict) and set(d) == TOP_KEYS
           and d["schema"] == "imo-g9-mathematics-topic-browser-v1"
           and type(d["responsibility_issue"]) is int and d["responsibility_issue"] == 298
           and d["source_research_basis_main"] ==
               "9a51fb9ae65a4b81f2dc6b791cbbc4eeba3c4260",
           "unreviewed data/schema fields or false research provenance")
    ensure(d["editorial_status"] ==
           "OWNER_DIRECTED_PUBLIC_TOPIC_INDEX_WITH_UNREVIEWED_AUTHORED_PRACTICE_PREVIEWS"
           and d["rights_policy"] ==
           "SOURCE_ONLY_LINKS_NO_SOF_STEMS_OPTIONS_FIGURES_OR_ANSWERS_COPIED"
           and d["placement"] == "MATHEMATICS_HUB_TOPIC_BROWSER_NOT_CORE2_OR_CORE1A"
           and d["publication_scope"] ==
           "RESEARCH_REFERENCE_AND_AUTHORED_PREVIEW_VISIBLE_ON_MATH_TAB"
           and d["publication_not_equal_core_acceptance"] is True,
           "page misrepresents source rights, reviewer or public-preview status")
    expected_ints = {
        "historic_source_seed_positions":66,
        "additional_organizer_sample_source_positions":2,
        "displayed_source_references":68,
        "displayed_authored_practice_previews":7,
        "canonical_qrt_accepted":0,
        "source_core2_admitted":0,
        "authored_core_admitted":0,
        "official_syllabus_topics_referenced":17,
    }
    ensure(all(type(d.get(k)) is int and d[k] == v
               for k,v in expected_ints.items()),
           "false source denominator or QRT/Core acceptance")
    pins = d.get("source_git_blobs")
    ensure(isinstance(pins,list) and len(pins) == len(SOURCE_PATHS),
           "six source Git blob custody references required")
    for pin,(path,sha) in zip(pins,SOURCE_PATHS):
        ensure(isinstance(pin,dict) and pin == dict(path=path,git_blob_sha=sha)
               and git_blob_sha(REPO/path) == sha, "input source drift or false Git blob")
    seed,registry,extra,sources,practice,disputes = (
        jsonl(REPO/SOURCE_PATHS[0][0]),
        load(REPO/SOURCE_PATHS[1][0]),
        load(REPO/SOURCE_PATHS[2][0]),
        load(REPO/SOURCE_PATHS[3][0]),
        load(REPO/SOURCE_PATHS[4][0]),
        load(REPO/SOURCE_PATHS[5][0]),
    )
    available_topics = registry["official_topics"]+registry["adjunct_topics"]
    expected_topics = [
      dict(topic_id=x["topic_id"],label=x["label"],
           syllabus_section=x["section"],
           classification_authority="OFFICIAL_SYLLABUS_TOPIC_LABEL" if
           x["official_syllabus"] else "ANALYST_ADJUNCT_NOT_OFFICIAL_SECTION2_TOPIC")
      for x in available_topics
    ]
    ensure(d["taxonomy_topics"] == expected_topics,
           "official syllabus labels or adjunct authority misrepresented")
    by_topic = {t["topic_id"]:t for t in expected_topics}
    by_source = {x["source_id"]:x for x in sources["sources"]}
    affected = {}
    for case in disputes["cases"]:
        for q in case["question_ids"]:
            ensure(q not in affected,"duplicate dispute position")
            affected[q] = case["case_id"]
    ensure(len(seed) == 66 and len(extra["entries"]) == 2 and len(affected) == 11,
           "seed, additional sample or multi-question split changed")
    expected = {}
    for q in seed:
        id = q["question_id"]
        src = by_source[q["source_id"]]
        ensure(id not in expected and q["primary_topic_id"] in by_topic,
               "duplicate/unknown source question or topic")
        expected[id] = {
          "id":id,"kind":"SOF_SOURCE_REFERENCE_ONLY",
          "topic_id":q["primary_topic_id"],"subtopic_id":q["subtopic_id"],
          "concept_summary":q["learning_demand_summary"],
          "source_id":q["source_id"],
          "source_pdf_url":extra["official_source_url"] if
            "SAMPLE" in q["source_id"] else src["url"],
          "original_number_claim":str(q["original_q"]),
          "exam_section":q["sample_section_observed"] or q["full_paper_exam_section"] or "NOT_ESTABLISHED",
          "printed_source_verbatim_present":False,
          "source_custody":"NOT_VERIFIED","rights_status":"NOT_REVIEWED",
          "qrt_accepted":False,"core2_admitted":False,
          "discrepancy_case":affected.get(id),
          "source_membership":"OWNER_SEED_66",
          "source_stem":None,"source_options":None,"source_figure":None,"answer":None
        }
    for q in extra["entries"]:
        id = q["question_id"]
        ensure(id not in expected and q["primary_topic_proposal"] in by_topic,
               "additional organizer sample collision")
        expected[id] = {
          "id":id,"kind":"SOF_SOURCE_REFERENCE_ONLY",
          "topic_id":q["primary_topic_proposal"],
          "subtopic_id":q["subtopic_proposal"],
          "concept_summary":"Spatial reasoning from dice orientations" if
          q["figure_kind"]=="SPATIAL_DICE_ORIENTATIONS" else
          "Number-pattern reasoning from a radial diagram",
          "source_id":q["source_id"],"source_pdf_url":extra["official_source_url"],
          "original_number_claim":str(q["sample_question_number"]),
          "exam_section":q["section_observed"],
          "printed_source_verbatim_present":False,
          "source_custody":"NOT_VERIFIED","rights_status":"NOT_REVIEWED",
          "qrt_accepted":False,"core2_admitted":False,
          "discrepancy_case":None,
          "source_membership":"ADDITIONAL_ORGANIZER_SAMPLE_2",
          "source_stem":None,"source_options":None,"source_figure":None,"answer":None
        }
    for i,q in enumerate(practice["records"]):
        id = q["id"]
        ensure(id not in expected and i < 7,
               "authored practice identity collides with source")
        expected[id] = {
          "id":id,"kind":"AUTHORED_PRACTICE_PREVIEW",
          "topic_id":PRACTICE_TOPICS[i],"title":q["title"],
          "stem":q["question_text"],"format":q["question_format"],
          "difficulty_proposal":q["qrt_proposal"]["difficulty_band"],
          "provisional_curriculum_scope":
             "REVIEW_AS_POSSIBLE_ABOVE_GRADE_ENRICHMENT" if i in (5,6)
             else "TOPIC_MATCH_ONLY",
          "original_source_claim":False,"origin":"MODEL_AUTHORED_NEW_PRACTICE",
          "question_display_authorization":"OWNER_DIRECT_MATH_TAB_REQUEST_2026_10_08",
          "qrt_accepted":False,"core2_admitted":False,"core1a_admitted":False,
          "learner_core_product_published":False,"answer":None,
          "source_membership":"SEVEN_AUTHORED_RESEARCH_PRACTICE"
        }
    rows = d.get("records")
    ensure(isinstance(rows,list) and len(rows) == 75,
           "68 source + 7 authored questions must be represented")
    ensure(len({r.get("id") for r in rows if isinstance(r,dict)}) == 75,
           "duplicate or missing topic entry")
    ensure([r["id"] for r in rows] == sorted(
           expected,key=lambda id:(expected[id]["topic_id"],
                                    expected[id]["kind"],id)),
           "topic/source order must be deterministic")
    for row in rows:
        id = row["id"]
        ensure(isinstance(row,dict)
               and set(row) == (SOURCE_KEYS if id.startswith("SOF-IMO-") else PRACTICE_KEYS)
               and row == expected.get(id),
               f"{id}: incorrect topic, verbatim source copied, or Core status inflated")
    counts = defaultdict(lambda: {"source_references":0,"authored_previews":0})
    for r in rows:
        k="source_references" if r["kind"]=="SOF_SOURCE_REFERENCE_ONLY" else "authored_previews"
        counts[r["topic_id"]][k] += 1
    ensure(dict(counts) == d["topic_counts"] and len(counts) == 15,
           "topic counts, or official-versus-adjunct topic segregation altered")
    first,second,hub1,hub2 = map(read,(
        public,docs,public_hub,docs_hub
    ))
    ensure(first == second and hub1 == hub2,
           "public/docs Mathematics mirrors diverged")
    ensure('href="imo-grade9/index.html"' in hub1,
           "Maths hub no longer links to IMO browser")
    ensure('<title>IMO Grade 9' in first
           and '<h1 class="g9-hero-title">IMO Grade 9' in first
           and '<label for="imo-topic-select">' in first
           and 'id="imo-search"' in first
           and 'aria-live="polite"' in first,
           "site is missing title, discoverability or keyboard-search controls")
    page = PageHTML()
    page.feed(first)
    ensure(len(page.items) == 75 and set(page.items) == set(expected),
           "site HTML is missing a question, duplicates a question, or invents an ID")
    ensure(len(page.sections) == 15 and
           set(page.sections) == set(d["topic_counts"]),
           "page lacks topic group or its heading")
    for id,record in expected.items():
        item = page.items[id]
        ensure(item["kind"] ==
               ("source" if record["kind"]=="SOF_SOURCE_REFERENCE_ONLY" else "authored")
               and item["topic"] == record["topic_id"],
               f"{id}: displayed under incorrect topic or source class")
        if item["kind"] == "source":
            ensure(item["urls"] == [record["source_pdf_url"]]
                   and record["concept_summary"] in item["text"]
                   and record["original_number_claim"] in item["text"],
                   f"{id}: unsafe/missing source PDF link or concept label")
            if record["discrepancy_case"]:
                ensure(record["discrepancy_case"] in item["text"],
                       f"{id}: material source dispute suppressed")
        else:
            ensure(item["urls"] == []
                   and record["stem"] in item["text"]
                   and record["title"] in item["text"],
                   f"{id}: original authored question missing/unexpected source link")
            if record["provisional_curriculum_scope"].startswith("REVIEW"):
                ensure("Grade-level enrichment review required" in item["text"],
                       f"{id}: scope warning removed")
    ensure("No answers or solutions appear on this page." in first
           and "not an official sof" in first.lower(),
           "learners are misled about published research preview status")
    return {
        "status":"MATH_TAB_RESEARCH_INDEX_WITH_DRAFT_PRACTICE_ONLY",
        "source_linked_question_positions":68,
        "model_authored_practice_stems_visible":7,
        "topic_groups":15,"source_conflict_rows":11,
        "source_stems_redistributed":0,"official_source_cores_accepted":0,
        "qrt_cells_accepted":0,"mirrored_site_pages":2,
    }

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--index", type=Path, default=INDEX)
    parser.add_argument("--public", type=Path, default=PUBLIC)
    parser.add_argument("--docs", type=Path, default=DOCS)
    args=parser.parse_args()
    try:
        print(json.dumps(validate_directory(
          index=args.index,public=args.public,docs=args.docs
        ),sort_keys=True))
    except TopicBrowserError as exc:
        parser.exit(1, f"IMO_MATH_TAB_INVALID: {exc}\n")

if __name__ == "__main__":
    main()
