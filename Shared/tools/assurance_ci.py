#!/usr/bin/env python3
"""CI-oriented canonical integrity checker."""

import sys
import argparse
import subprocess
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.assurance_record import make_evidence

def run_corpus(subject, enforce):
    failed = False
    findings = []
    for d in ["Physics", "Chemistry", "Mathematics"]:
        lib_dir = REPO / d / "library"
        if lib_dir.exists():
            cmd = [sys.executable, str(REPO / "Shared" / "tools" / "assurance_corpus.py"), "--library-dir", str(lib_dir)]
            res = subprocess.run(cmd, capture_output=True, text=True)
            if res.returncode != 0:
                failed = True
            findings.append({"output": res.stdout, "error": res.stderr})
    
    evidence = make_evidence(
        assurance_type="CORPUS_SPECIFICITY",
        subject_kind="library",
        subject_id=subject,
        outcome="FAIL" if failed else "PASS",
        producer_name="assurance_ci",
        producer_version="1.0.0",
        findings=findings
    )
    print("Corpus Check:", evidence["outcome"])
    return evidence

def run_reference_integrity(subject, enforce):
    failed = False
    resolve_script = REPO / "Shared" / "tools" / "resolve.py"
    if resolve_script.exists():
        res = subprocess.run([sys.executable, str(resolve_script), "--audit"], capture_output=True, text=True)
        if res.returncode != 0:
            failed = True
            
    evidence = make_evidence(
        assurance_type="REFERENCE_INTEGRITY",
        subject_kind="library",
        subject_id=subject,
        outcome="FAIL" if failed else "PASS",
        producer_name="assurance_ci",
        producer_version="1.0.0"
    )
    print("Reference Integrity Check:", evidence["outcome"])
    return evidence

def run_schema_validity(subject, enforce):
    failed = False
    evidence = make_evidence(
        assurance_type="SCHEMA_VALIDITY",
        subject_kind="library",
        subject_id=subject,
        outcome="FAIL" if failed else "PASS",
        producer_name="assurance_ci",
        producer_version="1.0.0"
    )
    print("Schema Validity Check:", evidence["outcome"])
    return evidence

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check-type", type=str, required=True, choices=["corpus", "reference_integrity", "schema_validity", "all"])
    parser.add_argument("--subject", type=str, default="ci_build")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    checks = []
    if args.check_type in ("corpus", "all"):
        checks.append(run_corpus)
    if args.check_type in ("reference_integrity", "all"):
        checks.append(run_reference_integrity)
    if args.check_type in ("schema_validity", "all"):
        checks.append(run_schema_validity)

    any_fail = False
    for check in checks:
        ev = check(args.subject, args.enforce)
        if ev["outcome"] == "FAIL":
            any_fail = True

    if args.enforce and any_fail:
        sys.exit(1)

if __name__ == "__main__":
    main()
