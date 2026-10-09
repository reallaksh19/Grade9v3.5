#!/usr/bin/env python3
"""Build an allowlisted CI evidence artifact, never a distributable offline KEY.

KEY_PDFs and postattempt HTML/screen captures stay within the ephemeral CI job
for its substantive tests. The archive can include learner role PDFs and neutral
receipts only; this is exposure minimization, NOT exam-answer confidentiality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
from pathlib import Path
from pypdf import PdfReader

LEARNER_PDFS = ("core1a.pdf", "core1b.pdf", "core2a.pdf")
LEARNER_METADATA = (
    "deploy-receipt.json",
    "print-receipt.json",
    "core1b-evidence/core1b-browser-report.json",
    "core1b-evidence/qualification.json",
)
EXPECTED_KEY_PDFS = ("core1a.key.pdf", "core1b.key.pdf", "core2a.key.pdf")
KEY_DIGEST_RECEIPT = "key-digests-only.json"
MANIFEST = "artifact-manifest.json"
ARTIFACT_FILES = (*LEARNER_PDFS, *LEARNER_METADATA, KEY_DIGEST_RECEIPT, MANIFEST)
WITHHELD_CORE1B = (
    "No. Three checks are instances",
    "Evidence:",
    "The factor t is always divisible by 3",
    "At t=2",
)


def digest(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def is_beneath(child: Path, parent: Path) -> bool:
    return child == parent or parent in child.parents


def stage(source: Path, keydir: Path, destination: Path, head_sha: str) -> dict:
    source, keydir, destination = (p.resolve() for p in (source, keydir, destination))
    if any(is_beneath(destination, p) or is_beneath(p, destination)
           for p in (source, keydir)):
        raise ValueError("Evidence output must not overlap public source or private key directory")
    if source.name != "core1b-authored-reconstruction-journey":
        raise ValueError("Incorrect TEST product source")
    if not source.is_dir() or not keydir.is_dir():
        raise FileNotFoundError("Learner tree or local CI-only key tree missing")
    if set(p.name for p in keydir.glob("*.key.pdf")) != set(EXPECTED_KEY_PDFS):
        raise ValueError("Offline key set differs from 3 expected CI-only role keys")
    if list(source.rglob("*.key.pdf")) or list(source.rglob("print-key-receipt.json")):
        raise ValueError("Offline KEY PDF/receipt unexpectedly present in public tree")
    key_receipt = json.loads((keydir / "print-key-receipt.json").read_text())
    learner_receipt = json.loads((source / "print-receipt.json").read_text())
    if key_receipt.get("mode") != "KEY_PDF" or learner_receipt.get("mode") != "LEARNER_PDF":
        raise ValueError("Print mode custody mismatch")
    key_rows = {r["pdf"]: r for r in key_receipt["pages"]}
    learner_rows = {r["pdf"]: r for r in learner_receipt["pages"]}
    if set(key_rows) != set(EXPECTED_KEY_PDFS) or set(learner_rows) != set(LEARNER_PDFS):
        raise ValueError("Print receipts incomplete or unexpectedly expanded")
    if len(set(r["page_digest"] for r in learner_rows.values())) < 1:
        raise ValueError("Learner render receipt absent")
    for role in ("core1a", "core1b", "core2a"):
        k, l = key_rows[role + ".key.pdf"], learner_rows[role + ".pdf"]
        if k["page"] != l["page"] or k["page_digest"] != l["page_digest"]:
            raise ValueError(f"{role}: key/learner source page divergence")
        if k["pdf_digest"] != digest(keydir / k["pdf"]):
            raise ValueError(f"{role}: KEY PDF digest mismatch")
        if l["pdf_digest"] != digest(source / l["pdf"]):
            raise ValueError(f"{role}: learner PDF digest mismatch")
    handout = " ".join((p.extract_text() or "") for p in PdfReader(source / "core1b.pdf").pages)
    for withheld in WITHHELD_CORE1B:
        if withheld in handout:
            raise ValueError(f"Core1B print exposes protected answer: {withheld}")
    qualification = json.loads((source / "core1b-evidence/qualification.json").read_text())
    if qualification.get("canonical_publication") is not False or qualification.get("QRT_cells") != 28:
        raise ValueError("Missing TEST nonrelease and QRT status evidence")
    browser = json.loads((source / "core1b-evidence/core1b-browser-report.json").read_text())
    if browser.get("failures") or browser.get("boundary_independent_attempt") != "SEPARATE_COMMIT_GATES_BROWSER_VERIFIED_UNGRADED":
        raise ValueError("Cannot export a failed or misrepresented browser gate as qualified evidence")
    if destination.exists():
        shutil.rmtree(destination)
    destination.mkdir(parents=True)
    digest_rows = {}
    for rel in (*LEARNER_PDFS, *LEARNER_METADATA):
        src, target = source / rel, destination / rel
        if not src.is_file():
            raise FileNotFoundError(f"Expected allowlisted evidence missing: {rel}")
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(src, target)
        digest_rows[rel] = digest(target)
    # Only hashes, figure counts and page associations; never a KEY PDF payload.
    key_digest = {
        "schema": "core1b-key-digests-only/v1",
        "release_authorized": False,
        "key_pdf_bytes_uploaded": False,
        "key_artifact_distribution": "WITHHELD_UNTIL_NAMED_OWNER_DECISION",
        "roles": [
            {"role": role.upper(), "page": key_rows[role + ".key.pdf"]["page"],
             "page_digest": key_rows[role + ".key.pdf"]["page_digest"],
             "key_pdf_digest": key_rows[role + ".key.pdf"]["pdf_digest"],
             "figures": key_rows[role + ".key.pdf"]["figures"]}
            for role in ("core1a", "core1b", "core2a")
        ],
    }
    (destination / KEY_DIGEST_RECEIPT).write_text(json.dumps(key_digest, indent=2) + "\n")
    digest_rows[KEY_DIGEST_RECEIPT] = digest(destination / KEY_DIGEST_RECEIPT)
    manifest = {
        "schema": "core1b-safe-ci-evidence/v1",
        "head_sha": head_sha,
        "audience": "CI_TEST_REVIEW_METADATA_ONLY_NOT_OFFLINE_KEY_DELIVERY",
        "retention_days_requested": 7,
        "contents": digest_rows,
        "offline_keys_generated_and_verified_within_CI": True,
        "offline_key_pdf_bytes_in_artifact": False,
        "generated_html_in_artifact": False,
        "postattempt_screenshots_in_artifact": False,
        "learner_published": False,
        "key_distribution_owner_approval": "NOT_GRANTED",
        "html_source_templates_still_contain_answers": True,
    }
    (destination / MANIFEST).write_text(json.dumps(manifest, indent=2) + "\n")
    actual = {p.relative_to(destination).as_posix() for p in destination.rglob("*") if p.is_file()}
    if actual != set(ARTIFACT_FILES):
        raise ValueError(f"Unsafe CI artifact files: {sorted(actual ^ set(ARTIFACT_FILES))}")
    for rel in actual:
        if rel.endswith((".html", ".png", ".key.pdf")) or "offline-key" in rel:
            raise ValueError(f"Forbidden KEY/HTML/reveal material in evidence: {rel}")
    print(json.dumps({"artifact_status": "SAFE_ALLOWLIST_STAGED",
                      "head_sha": head_sha, "files": sorted(actual),
                      "key_pdf_bytes_uploaded": False, "key_distribution_owner_approval": "NOT_GRANTED"}))
    return manifest


if __name__ == "__main__":
    cli = argparse.ArgumentParser()
    cli.add_argument("--source", type=Path, required=True)
    cli.add_argument("--keydir", type=Path, required=True)
    cli.add_argument("--out", type=Path, required=True)
    cli.add_argument("--head-sha", required=True)
    args = cli.parse_args()
    stage(args.source, args.keydir, args.out, args.head_sha)
