"""Measure independently supplied NCERT PDF *bytes*, never grant source custody.

This tool deliberately does not download URLs, infer the origin of supplied bytes,
authenticate a reviewer, compare rendered mathematics, or alter the raw source
bank / READY-only handoff. A SHA-256 digest alone is not an official PDF witness.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
MANIFEST = "TEST/evidence/source-intake/ncert-exemplar-g9-r4-pdf-byte-preflight.v1.json"
BASE_URL = "https://ncert.nic.in/pdf/publication/exemplarproblem/classIX/mathematics/"
SCHEMA = "grade9v3-test-ncert-pdf-byte-preflight-v1"
SOURCE_IDS = (
    "ncert-exemplar-g9-math-u01-q07", "ncert-exemplar-g9-math-u01-q11",
    "ncert-exemplar-g9-math-u01-q12", "ncert-exemplar-g9-math-u02-q11",
    "ncert-exemplar-g9-math-u02-q12",
)
DOCS = (
    ("UNIT_1", "ieep201.pdf", (2, 3)),
    ("UNIT_2", "ieep202.pdf", (2,)),
    ("ANSWER_KEY", "ieep2an.pdf", (0, 3)),
)
SOURCES = (
    "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q07-q10.review.v1.json",
    "TEST/evidence/source-intake/ncert-exemplar-g9-r4-u01-u02-q11-q12.observation.v1.json",
    "TEST/evidence/source-intake/ncert-exemplar-g9-u01-q07.recapture-applied.v1.json",
)
ROOT_FIELDS = {
    "schema_version", "scope", "checked_on", "source_bank_ref",
    "official_document_set", "source_observation_refs", "source_ids",
    "official_pdf_bytes_obtained", "official_pdf_sha256_authenticated",
    "independent_official_origin_authenticated", "independent_reviewer_approved",
    "source_custody_granted", "academic_pass_granted", "publication_authorized",
    "status", "limitations",
}
DOC_FIELDS = {
    "document_id", "official_url", "local_filename", "observed_pdf_page_indices",
    "byte_sha256", "byte_length", "official_origin_authenticated",
}
LIMITATIONS = (
    "A local PDF header/footer and its SHA-256 only measure supplied bytes. "
    "They do NOT authenticate the NCERT web origin, content, independent reviewer, "
    "source-text accuracy, academic PASS, Owner acceptance or publication."
)


def _require(ok: bool, msg: str) -> None:
    if not ok:
        raise ValueError("NCERT byte preflight: " + msg)


def validate_manifest(repo: Path = REPO) -> dict:
    path = repo / MANIFEST
    try:
        doc = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("NCERT byte preflight: manifest missing/invalid") from exc
    _require(isinstance(doc, dict) and set(doc) == ROOT_FIELDS,
             "manifest root schema or injected authority field")
    _require(doc["schema_version"] == SCHEMA
             and doc["scope"] == "R4 U01/U02 visual-only NCERT Exemplar PDF byte acquisition preflight"
             and doc["checked_on"] == "2026-10-08"
             and doc["source_bank_ref"] == "TEST/question-bank/intake/ncert-cbse-math-g9-pilot.json"
             and doc["source_observation_refs"] == list(SOURCES)
             and doc["source_ids"] == list(SOURCE_IDS),
             "manifest source identity/scope changed")
    _require(doc["status"] == "OFFICIAL_PDF_BYTES_UNAVAILABLE"
             and doc["limitations"] == LIMITATIONS,
             "preflight limitations/status changed")
    _require(all(doc.get(flag) is False for flag in (
                "official_pdf_bytes_obtained", "official_pdf_sha256_authenticated",
                "independent_official_origin_authenticated",
                "independent_reviewer_approved", "source_custody_granted",
                "academic_pass_granted", "publication_authorized")),
             "manifest cannot claim byte custody, academic PASS, Owner or publish authority")
    rows = doc["official_document_set"]
    _require(isinstance(rows, list) and len(rows) == len(DOCS),
             "exact three official document declarations required")
    for row, (key, filename, indices) in zip(rows, DOCS):
        _require(isinstance(row, dict) and set(row) == DOC_FIELDS,
                 "document row shape or injected authority field")
        _require(row["document_id"] == key
                 and row["local_filename"] == filename
                 and row["official_url"] == BASE_URL + filename
                 and row["observed_pdf_page_indices"] == list(indices)
                 and row["byte_sha256"] is None
                 and row["byte_length"] is None
                 and row["official_origin_authenticated"] is False,
                 f"unverified official PDF declaration changed: {key}")
    return doc


def measure_pdf(path: Path) -> dict:
    """Return local measurements, not source-origin/authenticity certification."""
    _require(not path.is_symlink() and path.is_file(),
             f"missing regular, nonsymlink PDF: {path.name}")
    byte_length = path.stat().st_size
    _require(32 <= byte_length <= 100 * 1024 * 1024,
             f"PDF envelope size outside bounded range: {path.name}")
    sha = hashlib.sha256()
    head = b""
    tail = b""
    with path.open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            if not head:
                head = chunk[:16]
            tail = (tail + chunk)[-2048:]
            sha.update(chunk)
    _require(bool(re.match(rb"^%PDF-(1\.[0-7]|2\.0)(?:\r|\n|\s)", head)),
             f"PDF version/header invalid: {path.name}")
    _require(bool(re.search(rb"%%EOF[ \t\r\n]*$", tail)),
             f"PDF trailer marker absent: {path.name}")
    return {
        "byte_length": byte_length,
        "local_sha256": "sha256:" + sha.hexdigest(),
        "envelope_probe": "PDF_HEADER_TRAILER_ONLY_NOT_FULL_PDF_VALIDATION",
        "independent_official_origin_authenticated": False,
        "source_custody_granted": False,
    }


def preflight(repo: Path = REPO, pdf_dir: Path | None = None) -> dict:
    doc = validate_manifest(repo)
    if pdf_dir is None:
        return {
            "status": "OFFICIAL_PDF_BYTES_UNAVAILABLE",
            "document_count": 3,
            "measurements": [],
            "source_custody_granted": False,
            "academic_pass_granted": False,
            "publication_authorized": False,
        }
    _require(pdf_dir.is_dir(), "--pdf-dir must identify an existing directory")
    actual_names = sorted(p.name for p in pdf_dir.glob("*.pdf"))
    _require(actual_names == sorted(filename for _, filename, _ in DOCS),
             "PDF directory must contain exactly the three declared filenames")
    measurements = []
    for row in doc["official_document_set"]:
        measured = measure_pdf(pdf_dir / row["local_filename"])
        measurements.append({
            "document_id": row["document_id"],
            "official_url_claim_not_authenticated": row["official_url"],
            "filename": row["local_filename"],
            **measured,
        })
    return {
        "status": "LOCAL_PDF_BYTES_MEASURED_UNAUTHENTICATED",
        "document_count": 3,
        "measurements": measurements,
        "source_custody_granted": False,
        "academic_pass_granted": False,
        "publication_authorized": False,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo", type=Path, default=REPO)
    parser.add_argument("--pdf-dir", type=Path, help="local folder with all 3 independently fetched official PDFs")
    args = parser.parse_args(argv)
    try:
        result = preflight(args.repo, args.pdf_dir)
    except ValueError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
