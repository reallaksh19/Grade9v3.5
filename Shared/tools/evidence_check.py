#!/usr/bin/env python3
"""Acquire allowlisted sources and prove every evidence card's quote is really in them.

A research agent's claim counts only when its verbatim quote is found, by this tool, on the
cited page of a pinned source snapshot whose SHA-256 matches the acquisition record. Memory,
paraphrase and unlisted hosts are not evidence.

Snapshots live in a git-ignored cache (.source-cache/<sha256>.<ext>); only the acquisition
record (URL + digest) and the cards are committed. `check --fetch` re-downloads a missing
snapshot and refuses it if the bytes changed.

Usage:
    evidence_check.py acquire --subject S --node NODE --resource-ref SRC-X --url URL
    evidence_check.py pages   --subject S --acq ACQ-... [--page N]
    evidence_check.py find    --subject S --acq ACQ-... --text "words to locate"
    evidence_check.py check   --subject S [--node NODE] [--fetch]
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import html.parser
import json
import logging
import re
import sys
import unicodedata
import urllib.parse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import source_pipeline  # noqa: E402

CACHE = REPO / ".source-cache"
CARDS_SCHEMA = REPO / "Shared/library/evidence-cards.schema.json"
MIN_QUOTE_WORDS = 6
EXTENSIONS = {"application/pdf": ".pdf", "text/html": ".html", "text/plain": ".txt"}


# ------------------------------------------------------------------ layout

def research_dir(subject: str, repo: Path = REPO) -> Path:
    return repo / subject / "research"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def allowlist(subject: str, repo: Path = REPO) -> dict:
    return load_json(research_dir(subject, repo) / "source-allowlist.json")


def tier_of(url: str, allow: dict) -> tuple[str | None, dict | None]:
    host = (urllib.parse.urlparse(url).hostname or "").lower()
    for tier, row in allow["tiers"].items():
        for entry in row["hosts"]:
            if host == entry["host"] or host.endswith("." + entry["host"]):
                return tier, entry
    return None, None


SCAN_SCHEME = "scan://"
SHINGLE_WORDS = 5
SCAN_NUMERIC_KINDS = {"QUESTION", "ANSWER_KEY", "WORKED_EXAMPLE", "RELATION"}
SECOND_READING_MIN_SIMILARITY = 0.85


def local_source(acq: dict, allow: dict) -> dict | None:
    """The owner-registered local source (a scanned book or paper) this acquisition pins."""
    locator = acq.get("requested_locator", "")
    if not locator.startswith(SCAN_SCHEME):
        return None
    source_id = locator[len(SCAN_SCHEME):].split("/", 1)[0]
    for entry in allow.get("local_sources", []):
        if entry["source_id"] == source_id and acq.get("sha256") in entry.get("scan_sha256s", []):
            return entry
    return None


def source_tier(acq: dict, allow: dict) -> tuple[str | None, list[str]]:
    """(tier, kinds it may support) for a URL or a registered local scan."""
    local = local_source(acq, allow)
    if local is not None:
        tier = local["tier"]
        return tier, list(local.get("may_support") or allow["tiers"][tier]["may_support"])
    tier, _ = tier_of(acq.get("requested_locator", ""), allow)
    return tier, (allow["tiers"][tier]["may_support"] if tier else [])


def scan_manifest_path(subject: str, acq_id: str, repo: Path = REPO) -> Path:
    return research_dir(subject, repo) / "scans" / f"{acq_id}.scan.json"


def tokens(text: str) -> list[str]:
    return re.findall(r"[0-9a-z]+", unicodedata.normalize("NFKC", text).lower())


def shingle_hashes(words: list[str]) -> list[str]:
    return [hashlib.sha256(" ".join(words[i:i + SHINGLE_WORDS]).encode()).hexdigest()[:8]
            for i in range(len(words) - SHINGLE_WORDS + 1)]


def page_shingles(pages: list[str]) -> list[str]:
    """Per page, the hashed 5-word shingles (including ones running into the next page).

    Committed instead of the text: a quote can be proven present without publishing the book.
    """
    out = []
    for i, text in enumerate(pages):
        words = tokens(text)
        if i + 1 < len(pages):
            words += tokens(pages[i + 1])[:SHINGLE_WORDS - 1]
        out.append(" ".join(sorted(set(shingle_hashes(words)))))
    return out


def quote_in_shingles(quote: str, index: list[str], page: int) -> bool:
    needed = set(shingle_hashes(tokens(quote)))
    if not needed:
        return False
    for i in (page - 1, page - 2, page):
        if 0 <= i < len(index) and needed <= set(index[i].split()):
            return True
    return False


def numbers(text: str) -> list[str]:
    return re.findall(r"\d+(?:\.\d+)?", unicodedata.normalize("NFKC", text))


def acquisition_path(subject: str, acq_id: str, repo: Path = REPO) -> Path:
    return research_dir(subject, repo) / "acquisitions" / f"{acq_id}.json"


def spine(subject: str, repo: Path = REPO) -> dict:
    return load_json(research_dir(subject, repo) / "syllabus-spine.json")


# ------------------------------------------------------------------ text

def normalize(text: str) -> str:
    """Compare text independent of PDF spacing, case, punctuation and ligatures."""
    text = unicodedata.normalize("NFKC", text).lower()
    return re.sub(r"[^0-9a-z]+", "", text)


class _Text(html.parser.HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in {"script", "style"}:
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in {"script", "style"} and self.skip:
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.parts.append(data)


def page_texts(path: Path, media_type: str) -> list[str]:
    """Extracted text per page (1 page for HTML/text). Cached next to the snapshot."""
    cached = path.with_suffix(path.suffix + ".pages.json")
    if cached.is_file():
        return load_json(cached)["pages"]
    data = path.read_bytes()
    if media_type == "application/pdf" or data[:5] == b"%PDF-":
        try:
            import pypdf  # noqa: PLC0415
        except ModuleNotFoundError as exc:
            raise RuntimeError("PDF evidence needs pypdf: pip install pypdf cffi") from exc
        logging.getLogger("pypdf").setLevel(logging.ERROR)
        reader = pypdf.PdfReader(str(path))
        pages = [(page.extract_text() or "") for page in reader.pages]
    elif "html" in media_type or data.lstrip()[:1] == b"<":
        parser = _Text()
        parser.feed(data.decode("utf-8", errors="replace"))
        pages = [" ".join(parser.parts)]
    else:
        pages = [data.decode("utf-8", errors="replace")]
    cached.write_text(json.dumps({"pages": pages}, ensure_ascii=False), encoding="utf-8")
    return pages


def quote_found(quote: str, pages: list[str], page: int) -> bool:
    needle = normalize(quote)
    if not needle:
        return False
    idx = page - 1
    windows = []
    for i in (idx, idx - 1, idx + 1):
        if 0 <= i < len(pages):
            windows.append(pages[i])
    if 0 <= idx < len(pages) - 1:
        windows.append(pages[idx] + " " + pages[idx + 1])  # quote crossing a page break
    return any(needle in normalize(window) for window in windows)


# ------------------------------------------------------------------ snapshots

def cache_path(acq: dict) -> Path:
    return CACHE / (acq["sha256"] + EXTENSIONS.get(acq.get("media_type", ""), ".bin"))


def ensure_snapshot(acq: dict, fetch: bool) -> tuple[Path | None, str | None]:
    path = cache_path(acq)
    if path.is_file() and hashlib.sha256(path.read_bytes()).hexdigest() == acq["sha256"]:
        return path, None
    if not fetch:
        return None, "snapshot not in local cache; run with --fetch"
    try:
        fresh = source_pipeline.acquire_url(
            url=acq["requested_locator"], subject=acq["subject"], bucket_id=acq["bucket_id"],
            resource_ref=acq["resource_ref"], acquired_at=acq["acquired_at"],
            snapshot_output=CACHE / "incoming.tmp")
    except Exception as exc:  # network or HTTP failure
        return None, f"download failed: {exc}"
    incoming = CACHE / "incoming.tmp"
    if fresh["sha256"] != acq["sha256"]:
        incoming.unlink(missing_ok=True)
        return None, "DIGEST_CHANGED"
    CACHE.mkdir(exist_ok=True)
    incoming.replace(path)
    return path, None


def acquire(subject: str, node: str, resource_ref: str, url: str, repo: Path = REPO) -> dict:
    allow = allowlist(subject, repo)
    tier, _ = tier_of(url, allow)
    if tier is None:
        raise SystemExit(f"host of {url} is not on {subject}/research/source-allowlist.json; it cannot be cited")
    CACHE.mkdir(exist_ok=True)
    today = datetime.date.today().isoformat()
    record = source_pipeline.acquire_url(url=url, subject=subject, bucket_id=node,
                                         resource_ref=resource_ref, acquired_at=today,
                                         snapshot_output=CACHE / "incoming.tmp")
    final = cache_path(record)
    (CACHE / "incoming.tmp").replace(final)
    record["snapshot_ref"] = str(final.relative_to(repo)) if final.is_relative_to(repo) else str(final)
    out = acquisition_path(subject, record["acquisition_id"], repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    if not out.exists():
        out.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    pages = page_texts(final, record["media_type"])
    return {"acquisition_id": record["acquisition_id"], "tier": tier, "pages": len(pages),
            "path": str(out.relative_to(repo))}


# ------------------------------------------------------------------ checking

def _finding(code: str, where: str, detail: str) -> dict:
    return {"code": code, "where": where, "detail": detail}


class _Index(list):
    """Page shingle index standing in for page text when the scan is not on this machine."""


def _is_index(pages: list) -> bool:
    return isinstance(pages, _Index)


def scan_pages(subject: str, acq: dict, repo: Path = REPO) -> list:
    """OCR page text if the scan was ingested on this machine, else the committed shingle index."""
    local = cache_path(acq).with_suffix(cache_path(acq).suffix + ".pages.json")
    if local.is_file():
        return load_json(local)["pages"]
    manifest = scan_manifest_path(subject, acq["acquisition_id"], repo)
    if manifest.is_file():
        return _Index(load_json(manifest)["shingles"]["pages"])
    return []


def second_reading_findings(cid: str, card: dict) -> list[dict]:
    """Numbers in a scanned card are OCR output until a second, independent reading agrees."""
    import difflib  # noqa: PLC0415
    check = card.get("scan_check")
    if not check:
        return [_finding("EVIDENCE_SCAN_SECOND_READING_MISSING", cid,
                         "a scanned card with numbers needs scan_check.second_reading from a different reader")]
    found = []
    if check.get("second_reader") == card.get("harvested_by"):
        found.append(_finding("EVIDENCE_SCAN_SECOND_READER_NOT_INDEPENDENT", cid,
                              "the second reading must be made by someone other than the harvester"))
    first, second = numbers(card.get("quote", "")), numbers(check.get("second_reading", ""))
    if first != second:
        found.append(_finding("EVIDENCE_SCAN_NUMBERS_DISAGREE", cid,
                              f"OCR quote numbers {first} vs second reading {second}; compare with the page image"))
    ratio = difflib.SequenceMatcher(None, normalize(card.get("quote", "")),
                                    normalize(check.get("second_reading", ""))).ratio()
    if ratio < SECOND_READING_MIN_SIMILARITY:
        found.append(_finding("EVIDENCE_SCAN_SECOND_READING_DIFFERS", cid,
                              f"second reading matches the OCR quote only {ratio:.0%}; it must be the same passage"))
    return found


def evidence_files(subject: str, node: str | None = None, repo: Path = REPO) -> list[Path]:
    folder = research_dir(subject, repo) / "evidence"
    files = sorted(folder.glob("*.cards.json"))
    return [p for p in files if node is None or p.name == f"{node}.cards.json"]


def check(subject: str, node: str | None = None, fetch: bool = False, repo: Path = REPO) -> dict:
    try:
        import jsonschema  # noqa: PLC0415
        validator = jsonschema.Draft202012Validator(load_json(CARDS_SCHEMA))
    except ModuleNotFoundError:
        validator = None
    allow = allowlist(subject, repo)
    nodes = {row["id"] for row in spine(subject, repo)["nodes"]}
    findings: list[dict] = []
    cards: dict[str, dict] = {}
    card_ok: dict[str, bool] = {}
    texts: dict[str, list[str]] = {}
    files = evidence_files(subject, node, repo)

    for path in files:
        rel = str(path.relative_to(repo))
        doc = load_json(path)
        if validator:
            for err in validator.iter_errors(doc):
                findings.append(_finding("EVIDENCE_STRUCTURE", rel + ":" + "/".join(map(str, err.path)), err.message))
        if doc.get("node_ref") not in nodes:
            findings.append(_finding("EVIDENCE_NODE_UNKNOWN", rel, f"{doc.get('node_ref')} is not a spine node"))
        if path.name != f"{doc.get('node_ref')}.cards.json":
            findings.append(_finding("EVIDENCE_FILE_NAME", rel, "file must be named <node_ref>.cards.json"))
        for card in doc.get("cards", []):
            cid = card.get("card_id", "?")
            if cid in cards:
                findings.append(_finding("EVIDENCE_DUPLICATE_CARD", cid, "card id used twice"))
            cards[cid] = {**card, "_file": rel, "_node": doc.get("node_ref")}

    for cid, card in cards.items():
        before = len(findings)
        acq_file = acquisition_path(subject, card.get("acquisition_ref", ""), repo)
        if not acq_file.is_file():
            findings.append(_finding("EVIDENCE_ACQUISITION_MISSING", cid, f"{card.get('acquisition_ref')} has no acquisition record"))
            card_ok[cid] = False
            continue
        acq = load_json(acq_file)
        tier, may_support = source_tier(acq, allow)
        kind = card.get("kind")
        scan = acq.get("requested_locator", "").startswith(SCAN_SCHEME)
        if tier is None:
            findings.append(_finding("EVIDENCE_HOST_NOT_ALLOWED", cid, acq.get("requested_locator", "") + (
                " (scan is not registered by the owner in local_sources with this sha256)" if scan else "")))
        elif kind not in may_support:
            findings.append(_finding("EVIDENCE_TIER_CANNOT_SUPPORT_KIND", cid,
                                     f"tier {tier} source cannot support a {kind} card"))
        words = re.findall(r"[A-Za-z0-9]+", card.get("quote", ""))
        if len(words) < MIN_QUOTE_WORDS:
            findings.append(_finding("EVIDENCE_QUOTE_TOO_SHORT", cid, f"quote has {len(words)} words; need {MIN_QUOTE_WORDS}"))
        acq_id = acq["acquisition_id"]
        if acq_id not in texts and scan:
            texts[acq_id] = scan_pages(subject, acq, repo)
            if not texts[acq_id]:
                findings.append(_finding("EVIDENCE_SCAN_MANIFEST_MISSING", acq_id,
                                         "scanned source has no scan manifest; run scan_ingest.py"))
        if acq_id not in texts:
            snap, problem = ensure_snapshot(acq, fetch)
            if snap is None:
                code = "EVIDENCE_SNAPSHOT_DIGEST_MISMATCH" if problem == "DIGEST_CHANGED" else "EVIDENCE_SNAPSHOT_NOT_FETCHED"
                findings.append(_finding(code, acq_id, problem or ""))
                texts[acq_id] = []
            else:
                texts[acq_id] = page_texts(snap, acq.get("media_type", ""))
        pages = texts[acq_id]
        page = (card.get("locator") or {}).get("page", 0)
        if pages:
            if not 1 <= page <= len(pages):
                findings.append(_finding("EVIDENCE_PAGE_OUT_OF_RANGE", cid, f"page {page} of {len(pages)}"))
            elif not (quote_in_shingles(card.get("quote", ""), pages, page) if scan and _is_index(pages)
                      else quote_found(card.get("quote", ""), pages, page)):
                findings.append(_finding("EVIDENCE_QUOTE_NOT_FOUND", cid,
                                         f"quote is not on page {page} (±1) of {acq_id}; copy it verbatim from `pages` output"))
        if scan and kind in SCAN_NUMERIC_KINDS:
            findings += second_reading_findings(cid, card)
        if kind == "QUESTION":
            q = card.get("question")
            if not q:
                findings.append(_finding("EVIDENCE_QUESTION_FIELDS_MISSING", cid, "QUESTION card needs exam, year, paper, question_number and answer_key_card_ref"))
            else:
                key = cards.get(q.get("answer_key_card_ref", ""))
                if not key or key.get("kind") != "ANSWER_KEY":
                    findings.append(_finding("EVIDENCE_ANSWER_KEY_MISSING", cid, "answer_key_card_ref must name an ANSWER_KEY card"))
        # A card whose source text could not be read is unproven, even if its finding was
        # recorded against another card of the same acquisition.
        card_ok[cid] = len(findings) == before and bool(pages)

    return {"subject": subject, "files": len(files), "cards": len(cards),
            "cards_passing": sum(card_ok.values()), "card_ok": card_ok,
            "findings": findings, "passed": not findings}


# ------------------------------------------------------------------ cli

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("acquire")
    for flag in ("--subject", "--node", "--resource-ref", "--url"):
        a.add_argument(flag, required=True)
    p = sub.add_parser("pages")
    p.add_argument("--subject", required=True)
    p.add_argument("--acq", required=True)
    p.add_argument("--page", type=int)
    p.add_argument("--fetch", action="store_true")
    f = sub.add_parser("find")
    f.add_argument("--subject", required=True)
    f.add_argument("--acq", required=True)
    f.add_argument("--text", required=True)
    f.add_argument("--fetch", action="store_true")
    c = sub.add_parser("check")
    c.add_argument("--subject", required=True)
    c.add_argument("--node")
    c.add_argument("--fetch", action="store_true")
    c.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.cmd == "acquire":
        print(json.dumps(acquire(args.subject, args.node, args.resource_ref, args.url), indent=2))
        return 0
    if args.cmd in {"pages", "find"}:
        acq = load_json(acquisition_path(args.subject, args.acq))
        if acq.get("requested_locator", "").startswith(SCAN_SCHEME):
            pages = scan_pages(args.subject, acq)
            if not pages or _is_index(pages):
                print("the OCR text of this scan exists only on the machine that ingested it")
                return 1
        else:
            snap, problem = ensure_snapshot(acq, args.fetch)
            if snap is None:
                print(problem)
                return 1
            pages = page_texts(snap, acq.get("media_type", ""))
        if args.cmd == "pages":
            chosen = [args.page] if args.page else range(1, len(pages) + 1)
            for n in chosen:
                print(f"===== page {n} of {len(pages)} =====\n{pages[n - 1]}")
            return 0
        needle = normalize(args.text)
        hits = [n for n, text in enumerate(pages, 1) if needle and needle in normalize(text)]
        print(json.dumps({"text": args.text, "pages": hits}))
        return 0 if hits else 1
    report = check(args.subject, args.node, args.fetch)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        for row in report["findings"]:
            print(f"{row['code']}  {row['where']}  {row['detail']}")
        print(f"evidence: {report['cards_passing']}/{report['cards']} cards verified in {report['files']} file(s)")
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
