#!/usr/bin/env python3
"""Phase-0 freeze: the quality calibration corpus must stay byte-identical to its manifest.

Checks benchmarks/quality-calibration/manifest.v1.json against the files on disk:
every specimen file exists with its recorded sha256, no unlisted file sits in a specimen
folder, every specimen carries at least one expected finding, and every positive reference
records its custody (a pinned repository location, or the search that failed to find it).
With --refs it also re-reads each repository-pinned reference at its commit and checks the
sha256 (needs the branch fetched).

Usage:
    calibration_corpus.py [--check] [--refs]
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
ROOT = REPO / "benchmarks/quality-calibration"
MANIFEST = ROOT / "manifest.v1.json"
CUSTODY = {"REPOSITORY", "NOT_LOCATED_IN_REPOSITORY"}


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check(root: Path = ROOT, refs: bool = False) -> list[dict]:
    manifest = json.loads((root / "manifest.v1.json").read_text(encoding="utf-8"))
    findings: list[dict] = []
    add = lambda code, where, detail="": findings.append({"code": code, "where": where, "detail": detail})
    for spec in manifest["specimens"]:
        files = spec.get("files", {})
        if not spec.get("expected_findings"):
            add("SPECIMEN_WITHOUT_FINDINGS", spec["id"], "a negative specimen must name the defects it shows")
        for rel, digest in files.items():
            path = root / rel
            if not path.is_file():
                add("SPECIMEN_FILE_MISSING", rel)
            elif sha(path.read_bytes()) != digest:
                add("SPECIMEN_FILE_CHANGED", rel, "the corpus is frozen; add a new specimen instead of editing one")
        folder = root / spec["dir"]
        for path in sorted(p for p in folder.rglob("*") if p.is_file()):
            rel = str(path.relative_to(root))
            if rel not in files:
                add("SPECIMEN_FILE_UNLISTED", rel)
    for ref in manifest["references"]:
        custody = ref.get("custody")
        if custody not in CUSTODY:
            add("REFERENCE_CUSTODY_UNSET", ref["id"], str(custody))
        if not ref.get("grammar"):
            add("REFERENCE_WITHOUT_GRAMMAR", ref["id"])
        if custody == "NOT_LOCATED_IN_REPOSITORY" and not ref.get("search"):
            add("REFERENCE_SEARCH_UNRECORDED", ref["id"])
        if custody == "REPOSITORY" and refs:
            src = ref["source"]
            for f in src["files"]:
                if "sha256" not in f:
                    continue
                got = subprocess.run(["git", "-C", str(REPO), "show", f"{src['commit']}:{f['path']}"],
                                     capture_output=True)
                if got.returncode:
                    add("REFERENCE_UNREACHABLE", f"{ref['id']}:{f['path']}", "git fetch origin " + src["branch"])
                elif sha(got.stdout) != f["sha256"]:
                    add("REFERENCE_CHANGED", f"{ref['id']}:{f['path']}")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--refs", action="store_true", help="also verify repository-pinned references")
    args = parser.parse_args(argv)
    findings = check(refs=args.refs)
    for f in findings:
        print(f"{f['code']}: {f['where']} {f['detail']}".rstrip(), file=sys.stderr)
    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    n = sum(len(s.get("files", {})) for s in manifest["specimens"])
    print(f"calibration corpus: {len(manifest['specimens'])} specimens, {n} files, "
          f"{len(manifest['references'])} references, {len(findings)} findings")
    return 1 if args.check and findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
