#!/usr/bin/env python3
"""Ingest an owner-registered scanned book or paper so its pages can back evidence cards.

Runs on the owner's machine (the "local agent"). The scan bytes and the OCR text stay in the
git-ignored .source-cache/; the repository receives only:

  <subject>/research/acquisitions/<ACQ>.json   source identity + SHA-256 of the scan file
  <subject>/research/scans/<ACQ>.scan.json      OCR engine/version, page map, low-text pages,
                                                and a hashed 5-word shingle index per page

With the index, evidence_check.py can prove a card's quote is on the cited page anywhere
(CI, cloud agents) without the book's text being published.

Usage:
    scan_ingest.py hash --file book.pdf
    scan_ingest.py ingest --subject S --source-id SRC-X --file book.pdf --node NODE --agent ID \\
        (--ocr ocrmypdf | --text-layer --ocr-engine "name version" | --pages-json p.json --ocr-engine "name version") \\
        [--language eng] [--printed-page-offset N]
    scan_ingest.py pages --subject S --acq ACQ-... --page N      # OCR text for copying quotes
"""
from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import evidence_check, source_pipeline  # noqa: E402

MIN_PAGE_WORDS = 25


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _version(command: list[str]) -> str:
    try:
        out = subprocess.run(command, capture_output=True, text=True, check=False, timeout=60)
        return (out.stdout or out.stderr).strip().splitlines()[0]
    except (OSError, IndexError, subprocess.TimeoutExpired):
        return "unknown"


def ocr_with_ocrmypdf(scan: Path, language: str) -> tuple[list[str], dict]:
    """OCR with a pinned, reproducible engine; returns per-page text and engine metadata."""
    if not shutil.which("ocrmypdf"):
        raise SystemExit("ocrmypdf is not installed (pip install ocrmypdf, plus Tesseract); "
                         "or pass --pages-json from another OCR engine with --ocr-engine")
    with tempfile.TemporaryDirectory() as tmp:
        sidecar = Path(tmp) / "text.txt"
        command = ["ocrmypdf", "--force-ocr", "--deskew", "-l", language, "--sidecar", str(sidecar),
                   str(scan), str(Path(tmp) / "out.pdf")]
        subprocess.run(command, check=True)
        pages = sidecar.read_text(encoding="utf-8").split("\f")
    if pages and not pages[-1].strip():
        pages = pages[:-1]
    meta = {"engine": _version(["ocrmypdf", "--version"]), "tesseract": _version(["tesseract", "--version"]),
            "language": language, "command": "ocrmypdf --force-ocr --deskew -l " + language + " --sidecar"}
    return pages, meta


def ingest(*, subject: str, source_id: str, scan: Path, node: str, agent: str, pages: list[str],
           ocr: dict, printed_page_offset: int | None, repo: Path = REPO) -> dict:
    allow = evidence_check.allowlist(subject, repo)
    sha = sha256_file(scan)
    entry = next((e for e in allow.get("local_sources", []) if e["source_id"] == source_id), None)
    if entry is None:
        raise SystemExit(f"{source_id} is not in local_sources of {subject}/research/source-allowlist.json; "
                         "the owner registers each scanned source first")
    if sha not in entry.get("scan_sha256s", []):
        raise SystemExit(f"sha256 {sha} of {scan.name} is not registered for {source_id}; "
                         "the owner adds it to scan_sha256s (scan_ingest.py hash --file ...)")
    if not pages or not any(p.strip() for p in pages):
        raise SystemExit("OCR produced no text")

    today = datetime.date.today().isoformat()
    record = source_pipeline.acquire_file(path=scan, subject=subject, bucket_id=node,
                                          resource_ref=source_id,
                                          requested_locator=f"{evidence_check.SCAN_SCHEME}{source_id}/{scan.name}",
                                          acquired_at=today)
    record["source_kind"] = "FILE"
    evidence_check.CACHE.mkdir(exist_ok=True)
    cached = evidence_check.cache_path(record)
    if not cached.exists():
        shutil.copyfile(scan, cached)
    record["snapshot_ref"] = f".source-cache/{cached.name}"
    record["resolved_locator"] = record["requested_locator"]
    local_pages = cached.with_suffix(cached.suffix + ".pages.json")
    local_pages.write_text(json.dumps({"pages": pages}, ensure_ascii=False), encoding="utf-8")

    acq_path = evidence_check.acquisition_path(subject, record["acquisition_id"], repo)
    acq_path.parent.mkdir(parents=True, exist_ok=True)
    acq_path.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")

    words = [len(evidence_check.tokens(p)) for p in pages]
    manifest = {
        "schema": "scan-manifest/v1",
        "acquisition_ref": record["acquisition_id"],
        "source_id": source_id,
        "file_name": scan.name,
        "page_count": len(pages),
        "ocr": ocr,
        "text_sha256": hashlib.sha256(json.dumps(pages, ensure_ascii=False).encode()).hexdigest(),
        "page_map": ({"rule": "printed_page = pdf_page + offset", "offset": printed_page_offset}
                     if printed_page_offset is not None else None),
        "low_text_pages": [i + 1 for i, n in enumerate(words) if n < MIN_PAGE_WORDS],
        "shingles": {"words": evidence_check.SHINGLE_WORDS, "hash": "sha256 hex prefix 8",
                     "pages": evidence_check.page_shingles(pages)},
        "produced_by": agent,
        "produced_at": today,
    }
    out = evidence_check.scan_manifest_path(subject, record["acquisition_id"], repo)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(manifest, indent=1) + "\n", encoding="utf-8")
    return {"acquisition_id": record["acquisition_id"], "pages": len(pages),
            "low_text_pages": manifest["low_text_pages"], "manifest": str(out.relative_to(repo))}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    h = sub.add_parser("hash")
    h.add_argument("--file", type=Path, required=True)
    i = sub.add_parser("ingest")
    for flag in ("--subject", "--source-id", "--node", "--agent"):
        i.add_argument(flag, required=True)
    i.add_argument("--file", type=Path, required=True)
    mode = i.add_mutually_exclusive_group(required=True)
    mode.add_argument("--ocr", choices=["ocrmypdf"])
    mode.add_argument("--text-layer", action="store_true", help="use the PDF's existing OCR text layer")
    mode.add_argument("--pages-json", type=Path, help='{"pages": ["page 1 text", ...]} from any OCR engine')
    i.add_argument("--ocr-engine", help="engine name and version (required with --text-layer/--pages-json)")
    i.add_argument("--language", default="eng")
    i.add_argument("--printed-page-offset", type=int)
    p = sub.add_parser("pages")
    p.add_argument("--subject", required=True)
    p.add_argument("--acq", required=True)
    p.add_argument("--page", type=int)
    args = parser.parse_args(argv)

    if args.cmd == "hash":
        print(sha256_file(args.file))
        return 0
    if args.cmd == "pages":
        return evidence_check.main(["pages", "--subject", args.subject, "--acq", args.acq]
                                   + (["--page", str(args.page)] if args.page else []))
    if args.ocr:
        pages, meta = ocr_with_ocrmypdf(args.file, args.language)
    else:
        if not args.ocr_engine:
            parser.error("--ocr-engine is required with --text-layer or --pages-json")
        if args.text_layer:
            pages = evidence_check.page_texts(args.file, "application/pdf")
            cached = args.file.with_suffix(args.file.suffix + ".pages.json")
            cached.unlink(missing_ok=True)  # page_texts caches beside the input; keep the user's folder clean
        else:
            pages = json.loads(args.pages_json.read_text(encoding="utf-8"))["pages"]
        meta = {"engine": args.ocr_engine, "language": args.language,
                "command": "text layer" if args.text_layer else f"pages-json {args.pages_json.name}"}
    print(json.dumps(ingest(subject=args.subject, source_id=args.source_id, scan=args.file, node=args.node,
                            agent=args.agent, pages=pages, ocr=meta,
                            printed_page_offset=args.printed_page_offset), indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
