"""Research library pipeline: quotes must be in pinned sources; stages come from files, not claims."""
from __future__ import annotations

import copy
import hashlib
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO))

from Shared.tools import evidence_check, library_board  # noqa: E402

SUBJECT = "Physics"
SOURCE = (b"<html><body><h2>3.9 Projectile motion</h2><p>An object that is in flight after being thrown "
          b"or projected is called a projectile. One component is along a horizontal direction without any "
          b"acceleration and the other along the vertical direction with constant acceleration due to the "
          b"force of gravity. We shall assume that the air resistance has negligible effect on the motion of "
          b"the projectile. Example: a ball thrown at 20 m/s at 30 degrees stays in the air for 2 s when g is "
          b"10 m/s2. Many students think the velocity is zero at the top, but only the vertical component is "
          b"zero there. This chapter covers projectile motion in the Class 11 syllabus unit on kinematics."
          b"</p><p>Q1. A ball is thrown at 20 m/s at 30 degrees above the horizontal with g = 10 m/s2. "
          b"Find the time of flight. Q2. Find the maximum height of the same ball above the ground. "
          b"Q3. Find the horizontal range of the same ball on level ground. Answer key: Q1 2 s, Q2 5 m, "
          b"Q3 34.6 m</p></body></html>")
URL = "https://ncert.nic.in/textbook/test-projectile.html"
NODE = "PHY-11-MOTION-IN-A-PLANE-08"
CHAPTER = "PHY-11-MOTION-IN-A-PLANE"


def card(cid: str, kind: str, quote: str, claim: str | None = None, **extra) -> dict:
    return {"card_id": cid, "kind": kind, "claim": claim or f"Claim supported by: {quote[:40]}",
            "quote": quote, "acquisition_ref": "", "locator": {"page": 1},
            "harvested_by": "agent-researcher", "harvested_at": "2026-09-26", **extra}


class Sandbox:
    """A copy of the subject's research folder plus a private snapshot cache."""

    def __init__(self):
        self.root = Path(tempfile.mkdtemp(prefix="research-lib-"))
        research = self.root / SUBJECT / "research"
        research.mkdir(parents=True)
        for name in ("source-allowlist.json", "syllabus-spine.json", "work-rules.json"):
            shutil.copy(REPO / SUBJECT / "research" / name, research / name)
        for folder in ("acquisitions", "evidence", "verification", "packages"):
            (research / folder).mkdir()
        self.research = research
        self.cache = self.root / "cache"
        self.cache.mkdir()
        self.old_cache = evidence_check.CACHE
        evidence_check.CACHE = self.cache
        self.acq = self.pin(SOURCE, URL)

    def pin(self, data: bytes, url: str) -> str:
        sha = hashlib.sha256(data).hexdigest()
        acq = {"acquisition_id": f"ACQ-{sha[:20].upper()}", "version": "1.0.0", "subject": SUBJECT,
               "bucket_id": CHAPTER, "resource_ref": "SRC-TEST", "source_kind": "URL",
               "requested_locator": url, "resolved_locator": url, "acquired_at": "2026-09-26",
               "media_type": "text/html", "byte_length": len(data), "sha256": sha,
               "snapshot_ref": f".source-cache/{sha}.html"}
        (self.cache / f"{sha}.html").write_bytes(data)
        (self.research / "acquisitions" / f"{acq['acquisition_id']}.json").write_text(json.dumps(acq))
        return acq["acquisition_id"]

    def write_cards(self, node: str, cards: list[dict], acq: str | None = None) -> None:
        for row in cards:
            row["acquisition_ref"] = row["acquisition_ref"] or (acq or self.acq)
        doc = {"schema": "evidence-cards/v1", "subject": SUBJECT, "node_ref": node, "cards": cards}
        (self.research / "evidence" / f"{node}.cards.json").write_text(json.dumps(doc))

    def check(self, **kw) -> dict:
        return evidence_check.check(SUBJECT, repo=self.root, **kw)

    def board(self) -> dict:
        return library_board.build(SUBJECT, repo=self.root)

    def row(self, node: str = NODE) -> dict:
        return next(r for r in self.board()["nodes"] if r["node"] == node)

    def close(self):
        evidence_check.CACHE = self.old_cache
        shutil.rmtree(self.root, ignore_errors=True)


def full_cards() -> list[dict]:
    return [
        card("EV-T-DEF", "DEFINITION", "An object that is in flight after being thrown or projected is called a projectile."),
        card("EV-T-REL", "RELATION", "One component is along a horizontal direction without any acceleration"),
        card("EV-T-CON", "CONDITION", "assume that the air resistance has negligible effect on the motion of the projectile"),
        card("EV-T-WEX", "WORKED_EXAMPLE", "a ball thrown at 20 m/s at 30 degrees stays in the air for 2 s"),
        card("EV-T-MIS", "MISCONCEPTION", "Many students think the velocity is zero at the top"),
        card("EV-T-KEY", "ANSWER_KEY", "Answer key: Q1 2 s, Q2 5 m, Q3 34.6 m"),
        *[card(f"EV-T-Q{i}", "QUESTION", text, question={"exam": "NCERT exercise", "year": 2023, "paper": "Ch 3",
                                                          "question_number": f"Q{i}", "answer_key_card_ref": "EV-T-KEY"})
          for i, text in ((1, "A ball is thrown at 20 m/s at 30 degrees above the horizontal"),
                          (2, "Find the maximum height of the same ball above the ground"),
                          (3, "Find the horizontal range of the same ball on level ground"))],
    ]


class EvidenceCheck(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox()

    def tearDown(self):
        self.box.close()

    def test_verbatim_quote_in_pinned_source_passes(self):
        self.box.write_cards(NODE, full_cards())
        report = self.box.check()
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["cards_passing"], 9)

    def test_quote_is_matched_through_pdf_spacing_noise(self):
        self.assertTrue(evidence_check.quote_found(
            "Take another example: the maximum temperature", ["T ake another  example : the maximum\ntemperature"], 1))

    def test_one_changed_word_is_caught(self):
        self.box.write_cards(NODE, [card("EV-T-DEF", "DEFINITION", "An object that is in flight after being thrown or projected is called a missile.")])
        self.assertIn("EVIDENCE_QUOTE_NOT_FOUND", [f["code"] for f in self.box.check()["findings"]])

    def test_short_quote_and_wrong_page_are_refused(self):
        wrong = card("EV-T-DEF", "DEFINITION", "An object that is in flight after being thrown or projected is called a projectile.")
        wrong["locator"]["page"] = 3
        self.box.write_cards(NODE, [card("EV-T-S", "DEFINITION", "called a projectile"), wrong])
        codes = [f["code"] for f in self.box.check()["findings"]]
        self.assertIn("EVIDENCE_QUOTE_TOO_SHORT", codes)
        self.assertIn("EVIDENCE_PAGE_OUT_OF_RANGE", codes)

    def test_unlisted_host_and_tier_misuse_are_refused(self):
        blog = self.box.pin(SOURCE + b" ", "https://random-physics-blog.example/post")
        aggregator = self.box.pin(SOURCE + b"  ", "https://questions.examside.com/q/1")
        quote = "An object that is in flight after being thrown or projected is called a projectile."
        self.box.write_cards(NODE, [card("EV-T-A", "DEFINITION", quote, acquisition_ref=blog),
                                    card("EV-T-B", "DEFINITION", quote, acquisition_ref=aggregator)])
        codes = {f["where"]: f["code"] for f in self.box.check()["findings"]}
        self.assertEqual(codes["EV-T-A"], "EVIDENCE_HOST_NOT_ALLOWED")
        self.assertEqual(codes["EV-T-B"], "EVIDENCE_TIER_CANNOT_SUPPORT_KIND")

    def test_changed_snapshot_bytes_are_refused(self):
        self.box.write_cards(NODE, full_cards()[:1])
        for path in self.box.cache.glob("*.html"):
            path.write_bytes(b"tampered")
        self.box.write_cards(NODE, full_cards()[:3])
        report = self.box.check()
        self.assertIn("EVIDENCE_SNAPSHOT_NOT_FETCHED", [f["code"] for f in report["findings"]])
        self.assertEqual(report["cards_passing"], 0)

    def test_question_needs_an_answer_key_card(self):
        cards = full_cards()
        self.box.write_cards(NODE, [c for c in cards if c["card_id"] != "EV-T-KEY"])
        self.assertIn("EVIDENCE_ANSWER_KEY_MISSING", [f["code"] for f in self.box.check()["findings"]])

    def test_committed_evidence_is_well_formed(self):
        report = evidence_check.check(SUBJECT)
        structural = [f for f in report["findings"] if f["code"] != "EVIDENCE_SNAPSHOT_NOT_FETCHED"]
        self.assertEqual(structural, [])


class Board(unittest.TestCase):
    def setUp(self):
        self.box = Sandbox()
        scope = card("EV-T-SCOPE", "SYLLABUS_SCOPE", "This chapter covers projectile motion in the Class 11 syllabus")
        self.box.write_cards(CHAPTER, [scope])

    def tearDown(self):
        self.box.close()

    def staging(self, cite_everything: bool = True) -> dict:
        package = json.loads((REPO / "Physics/library/phy-kin-2d-motion.v1.json").read_text(encoding="utf-8"))
        mic = next(m for m in package["microtopics"] if m["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL")
        mic["intrinsic_badge"] = "MEDIUM"
        cites = {f: ["EV-T-DEF", "EV-T-REL"] for f in library_board.rules(SUBJECT)["cited_fields"]["microtopics"]}
        if not cite_everything:
            cites.pop("exit_task")
        mic["extensions"] = {library_board.NODE_KEY: NODE, library_board.AUTHOR_KEY: "agent-author",
                             library_board.CITATIONS: cites}
        for i in (1, 2, 3):
            q = copy.deepcopy(package["questions"][0])
            q["id"] = f"Q-T-{i}"
            q["extensions"] = {library_board.NODE_KEY: NODE, library_board.AUTHOR_KEY: "agent-author",
                               library_board.CITATIONS: {"stem": [f"EV-T-Q{i}"], "answer": ["EV-T-KEY"],
                                                         "conditions": ["EV-T-CON"]}}
            q["origin"] = "ORIGINAL"
            package["questions"].append(q)
        (self.box.research / "packages" / f"{CHAPTER}.package.json").write_text(json.dumps(package))
        return package

    def verify(self, by: str = "agent-verifier", agrees: bool = True, numeric: str = "2*20*sin(radians(30))/10"):
        package = json.loads((self.box.research / "packages" / f"{CHAPTER}.package.json").read_text())
        records = [row for col in ("microtopics", "capabilities", "relations", "representations", "questions")
                   for row in package.get(col, []) if (row.get("extensions") or {}).get(library_board.NODE_KEY) == NODE]
        doc = {"schema": "research-verification/v1", "subject": SUBJECT, "node_ref": NODE, "verified_by": by,
               "verified_at": "2026-09-27",
               "inputs_digest": library_board.inputs_digest(SUBJECT, NODE, records, self.box.root),
               "questions": [{"card_ref": f"EV-T-Q{i}", "independent_solution": ["u_y = 10 m/s", "t = 2u_y/g"],
                              "independent_answer": "2 s", "official_answer": ans, "agrees": agrees,
                              **({"numeric_check": numeric} if i == 1 else {})}
                             for i, ans in ((1, "2 s"), (2, "5 m"), (3, "34.6 m"))],
               "records": [{"record_ref": r["id"], "checked_fields": ["inferential_jump"], "agrees": True} for r in records],
               "findings": []}
        (self.box.research / "verification" / f"{NODE}.verification.json").write_text(json.dumps(doc))

    def test_stage_moves_only_when_files_prove_it(self):
        self.assertEqual(self.box.row()["stage"], "RESEARCHER")
        self.box.write_cards(NODE, full_cards())
        self.assertEqual(self.box.row()["stage"], "AUTHOR")
        self.staging(cite_everything=False)
        row = self.box.row()
        self.assertEqual(row["stage"], "AUTHOR")
        self.assertTrue(any("exit_task" in d["duty"] for d in row["duties"]), row["duties"])
        self.staging()
        self.assertEqual(self.box.row()["stage"], "VERIFIER")
        self.verify()
        self.assertEqual(self.box.row()["stage"], "VERIFIED", self.box.row()["duties"])

    def test_factual_fields_cannot_be_marked_authored(self):
        self.box.write_cards(NODE, full_cards())
        package = self.staging()
        mic = next(m for m in package["microtopics"] if m["id"] == "MIC-PHY-KIN-PROJECTILE-MODEL")
        mic["extensions"][library_board.CITATIONS]["inferential_jump"] = "AUTHORED_PEDAGOGICAL"
        mic["extensions"][library_board.CITATIONS]["teaching_path"] = "AUTHORED_PEDAGOGICAL"
        (self.box.research / "packages" / f"{CHAPTER}.package.json").write_text(json.dumps(package))
        duties = [d["duty"] for d in self.box.row()["duties"]]
        self.assertTrue(any("inferential_jump: carries facts" in d for d in duties), duties)
        self.assertFalse(any("teaching_path" in d for d in duties), duties)

    def test_verifier_must_be_independent_and_current(self):
        self.box.write_cards(NODE, full_cards())
        self.staging()
        self.verify(by="agent-author")
        self.assertIn("neither harvested nor authored", json.dumps(self.box.row()["duties"]))
        self.verify()
        cards = full_cards()
        cards[0]["claim"] = "A projectile is any object in flight after being thrown or projected."
        self.box.write_cards(NODE, cards)
        self.assertIn("verify again", json.dumps(self.box.row()["duties"]))

    def test_disagreement_and_bad_numeric_check_go_back_to_the_author(self):
        self.box.write_cards(NODE, full_cards())
        self.staging()
        self.verify(agrees=False, numeric="3*3")
        row = self.box.row()
        self.assertEqual(row["stage"], "AUTHOR")
        self.assertIn("disagrees with the official key", json.dumps(row["duties"]))
        self.assertIn("numeric check gives 9", json.dumps(row["duties"]))

    def test_numeric_checks_cannot_run_code(self):
        with self.assertRaises(ValueError):
            library_board.safe_eval("__import__('os').system('true')")
        self.assertAlmostEqual(library_board.safe_eval("2*20*sin(radians(30))/10"), 2.0)

    def test_work_orders_start_with_the_pilot_chapter_and_split_into_lanes(self):
        board = self.box.board()
        first = library_board.next_order(board, "RESEARCHER", None, SUBJECT)
        self.assertIn(CHAPTER, first.splitlines()[0])
        second = library_board.next_order(board, "RESEARCHER", "2/2", SUBJECT)
        self.assertNotEqual(first.splitlines()[0], second.splitlines()[0])


KEY = b"<html><body><p>JEE Main 2021 26 Feb Shift 1 Question 12 answer key: the correct option is (3) 20 m</p></body></html>"
KEY_QUOTE = "Question 12 answer key: the correct option is (3) 20 m"


class CorroborationFallback(unittest.TestCase):
    """A Tier C question or key is secondary authority only when other Tier C publishers agree."""

    def setUp(self):
        self.box = Sandbox()
        self.own = self.box.pin(KEY, "https://questions.examside.com/past-years/jee/question/q12")
        self.allen = self.box.pin(KEY + b" ", "https://www.allen.ac.in/jee-main/2021/key.html")
        self.aakash = self.box.pin(KEY + b"  ", "https://www.aakash.ac.in/jee-main/2021/key.html")
        self.examside2 = self.box.pin(KEY + b"   ", "https://www.examside.com/jee-main/2021/key.html")

    def tearDown(self):
        self.box.close()

    def key_card(self, sources, attempt="https://jeemain.nta.nic.in/answer-key-2021"):
        corr = {"official_attempt": {"url": attempt, "outcome": "UNREACHABLE", "attempted_at": "2026-09-26"},
                "sources": [{"acquisition_ref": a, "page": 1, "quote": KEY_QUOTE} for a in sources]}
        return card("EV-T-KEYC", "ANSWER_KEY", KEY_QUOTE, authority="SECONDARY_CORROBORATED", corroboration=corr)

    def codes(self, row):
        self.box.write_cards(NODE, [row], acq=self.own)
        return {f["code"] for f in self.box.check()["findings"]}

    def test_single_tier_c_host_cannot_support_a_key(self):
        codes = self.codes(card("EV-T-KEYC", "ANSWER_KEY", KEY_QUOTE))
        self.assertEqual(codes, {"EVIDENCE_TIER_CANNOT_SUPPORT_KIND"})

    def test_two_independent_publishers_and_an_official_attempt_pass(self):
        self.assertEqual(self.codes(self.key_card([self.allen, self.aakash])), set())

    def test_same_publisher_does_not_count_twice(self):
        codes = self.codes(self.key_card([self.allen, self.examside2]))
        self.assertEqual(codes, {"EVIDENCE_CORROBORATION_NOT_INDEPENDENT", "EVIDENCE_CORROBORATION_INSUFFICIENT"})

    def test_official_attempt_must_name_a_tier_a_page(self):
        codes = self.codes(self.key_card([self.allen, self.aakash], attempt="https://example.org/key"))
        self.assertEqual(codes, {"EVIDENCE_OFFICIAL_ATTEMPT_MISSING"})

    def test_explanations_are_never_corroborated(self):
        row = self.key_card([self.allen, self.aakash])
        row["kind"] = "DEFINITION"
        self.assertEqual(self.codes(row), {"EVIDENCE_CORROBORATION_WRONG_KIND"})

    def test_nta_cdn_is_primary_authority(self):
        tier, _ = evidence_check.tier_of("https://cdnbbsr.s3waas.gov.in/s3f8e59f4b2fe7c5705bf878bbd494ccdf/uploads/key.pdf",
                                         evidence_check.allowlist(SUBJECT))
        self.assertEqual(tier, "A")


if __name__ == "__main__":
    unittest.main()


class ScanProtocol(unittest.TestCase):
    """Local scans: owner-registered, OCR text stays local, quotes provable from a hashed index."""

    PAGES = [
        "Chapter 4 Projectile motion. A body projected into the air and moving under gravity alone "
        "is called a projectile, and its horizontal velocity stays constant throughout the flight.",
        "Worked example 4.2. A stone is thrown horizontally at 15 m/s from a cliff 20 m high. "
        "Taking g = 10 m/s2 it reaches the ground after 2 s at a distance of 30 m from the foot.",
        "Figure 4.3",
        "Exercise 4.7 A ball is thrown at 25 m/s at an angle of 37 degrees with the horizontal. "
        "Find its time of flight. Answers to exercises: 4.7 3 s, 4.8 45 m.",
    ]

    def setUp(self):
        from Shared.tools import scan_ingest  # noqa: PLC0415
        self.scan_ingest = scan_ingest
        self.box = Sandbox()
        self.scan = self.box.root / "book.pdf"
        self.scan.write_bytes(b"%PDF-1.4 scanned book bytes for the test")
        self.register(scan_ingest.sha256_file(self.scan))

    def tearDown(self):
        self.box.close()

    def register(self, sha: str) -> None:
        path = self.box.research / "source-allowlist.json"
        allow = json.loads(path.read_text())
        allow["local_sources"] = [{"source_id": "SRC-TEST-BOOK", "title": "Test Physics Book", "tier": "B",
                                   "may_support": ["DEFINITION", "WORKED_EXAMPLE", "QUESTION", "ANSWER_KEY"],
                                   "rights": "COPYRIGHTED_OWNED_COPY", "scan_sha256s": [sha],
                                   "registered_by": "owner", "registered_at": "2026-09-26"}]
        path.write_text(json.dumps(allow))

    def ingest(self) -> dict:
        return self.scan_ingest.ingest(subject=SUBJECT, source_id="SRC-TEST-BOOK", scan=self.scan, node=CHAPTER,
                                       agent="local-agent", pages=self.PAGES, ocr={"engine": "test-ocr 1.0"},
                                       printed_page_offset=40, repo=self.box.root)

    def scan_card(self, cid, kind, quote, page, **extra):
        return card(cid, kind, quote, locator={"page": page}, harvested_by="local-agent", **extra)

    def test_unregistered_scan_is_refused(self):
        self.register("0" * 64)
        with self.assertRaises(SystemExit):
            self.ingest()

    def test_quote_proven_locally_and_from_the_committed_index_alone(self):
        acq = self.ingest()["acquisition_id"]
        good = self.scan_card("EV-S-DEF", "DEFINITION",
                              "moving under gravity alone is called a projectile", 1, acquisition_ref=acq)
        self.box.write_cards(NODE, [good])
        self.assertTrue(self.box.check()["passed"], self.box.check()["findings"])
        for path in self.box.cache.glob("*.pages.json"):
            path.unlink()  # a cloud agent or CI has only the committed manifest
        report = self.box.check()
        self.assertTrue(report["passed"], report["findings"])
        self.assertEqual(report["cards_passing"], 1)
        bad = self.scan_card("EV-S-DEF", "DEFINITION",
                             "moving under gravity alone is called a missile", 1, acquisition_ref=acq)
        self.box.write_cards(NODE, [bad])
        self.assertIn("EVIDENCE_QUOTE_NOT_FOUND", [f["code"] for f in self.box.check()["findings"]])

    def test_manifest_holds_no_page_text_and_flags_low_text_pages(self):
        result = self.ingest()
        manifest = (self.box.root / result["manifest"]).read_text()
        self.assertNotIn("projectile", manifest)
        self.assertEqual(result["low_text_pages"], [3])

    def test_scanned_numbers_need_an_independent_second_reading(self):
        acq = self.ingest()["acquisition_id"]
        quote = "A stone is thrown horizontally at 15 m/s from a cliff 20 m high"
        base = dict(acquisition_ref=acq)
        cases = {
            "EVIDENCE_SCAN_SECOND_READING_MISSING": {},
            "EVIDENCE_SCAN_SECOND_READER_NOT_INDEPENDENT": {"scan_check": {
                "second_reading": quote, "second_reader": "local-agent", "method": "HUMAN"}},
            "EVIDENCE_SCAN_NUMBERS_DISAGREE": {"scan_check": {
                "second_reading": "A stone is thrown horizontally at 16 m/s from a cliff 20 m high",
                "second_reader": "owner", "method": "HUMAN"}},
        }
        for code, extra in cases.items():
            with self.subTest(code=code):
                self.box.write_cards(NODE, [self.scan_card("EV-S-WEX", "WORKED_EXAMPLE", quote, 2, **base, **extra)])
                self.assertIn(code, [f["code"] for f in self.box.check()["findings"]])
        ok = self.scan_card("EV-S-WEX", "WORKED_EXAMPLE", quote, 2, **base, scan_check={
            "second_reading": "A stone is thrown horizontally at 15 m/s from a cliff 20 m high",
            "second_reader": "owner", "method": "HUMAN"})
        self.box.write_cards(NODE, [ok])
        self.assertTrue(self.box.check()["passed"], self.box.check()["findings"])

    def test_owner_tier_narrowing_is_enforced(self):
        acq = self.ingest()["acquisition_id"]
        self.box.write_cards(NODE, [self.scan_card("EV-S-SC", "SYLLABUS_SCOPE",
                                                   "Chapter 4 Projectile motion. A body projected into the air", 1,
                                                   acquisition_ref=acq)])
        self.assertIn("EVIDENCE_TIER_CANNOT_SUPPORT_KIND", [f["code"] for f in self.box.check()["findings"]])
