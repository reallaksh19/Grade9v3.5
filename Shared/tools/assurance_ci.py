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
    not_run = False
    resolve_script = REPO / "Shared" / "library" / "resolve.py"

    if resolve_script.exists():
        try:
            # Collect all governed library JSON files across subjects
            packages = []
            for subj in ["Physics", "Chemistry", "Mathematics"]:
                lib_dir = REPO / subj / "library"
                if lib_dir.exists():
                    packages.extend(str(p) for p in sorted(lib_dir.glob("*.json")))

            if not packages:
                not_run = True
            else:
                # Invoke as subprocess with all packages to resolve cross-references
                result = subprocess.run(
                    [sys.executable, str(resolve_script)] + packages,
                    capture_output=True, text=True, cwd=str(REPO)
                )
                if result.returncode != 0:
                    failed = True
                    if result.stderr:
                        print(result.stderr[:600], file=sys.stderr)
        except Exception as e:
            failed = True
            print(f"Resolve failed: {e}", file=sys.stderr)
    else:
        not_run = True
            
    if not_run:
        outcome = "NOT_RUN"
    elif failed:
        outcome = "FAIL"
    else:
        outcome = "PASS"
        
    evidence = make_evidence(
        assurance_type="REFERENCE_INTEGRITY",
        subject_kind="library",
        subject_id=subject,
        outcome=outcome,
        producer_name="assurance_ci",
        producer_version="1.0.0",
        severity="S1" if outcome == "FAIL" else None
    )
    print("Reference Integrity Check:", evidence["outcome"])
    return evidence

def run_schema_validity(subject, enforce):
    failed = False
    findings = []
    
    try:
        import jsonschema
        has_jsonschema = True
    except ImportError:
        has_jsonschema = False

    schema_file = REPO / "Shared" / "library" / "package.schema.json"
    schema = None
    if schema_file.exists():
        import json
        with schema_file.open("r", encoding="utf-8") as f:
            schema = json.load(f)

    import json
    for d in ["Physics", "Chemistry", "Mathematics"]:
        lib_dir = REPO / d / "library"
        if not lib_dir.exists():
            continue
        for p in lib_dir.glob("*.json"):
            with p.open("r", encoding="utf-8") as f:
                try:
                    data = json.load(f)
                except json.JSONDecodeError:
                    continue
            
            if not isinstance(data, dict) or "questions" not in data:
                continue
                
            if has_jsonschema and schema:
                try:
                    jsonschema.validate(instance=data, schema=schema)
                except Exception as e:
                    failed = True
                    findings.append({"file": str(p), "error": str(e), "severity": "S1"})
                    
            # Manual required-fields check
            for idx, q in enumerate(data["questions"]):
                missing = []
                for req in ["id", "stem", "origin", "origin_ref", "answer", "primary_capability_ref"]:
                    if req not in q:
                        missing.append(req)
                if "answer" in q and isinstance(q["answer"], dict):
                    if "kind" not in q["answer"]:
                        missing.append("answer.kind")
                    if "summary" not in q["answer"]:
                        missing.append("answer.summary")
                        
                if missing:
                    failed = True
                    findings.append({"file": str(p), "question_index": idx, "missing": missing, "severity": "S1"})

    evidence = make_evidence(
        assurance_type="STRUCTURAL_VALIDITY",
        subject_kind="library",
        subject_id=subject,
        outcome="FAIL" if failed else "PASS",
        producer_name="assurance_ci",
        producer_version="1.0.0",
        findings=findings,
        severity="S1" if failed else None
    )
    print("Schema Validity Check:", evidence["outcome"])
    
    if enforce and failed:
        sys.exit(1)
        
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
