#!/usr/bin/env python3
"""Corpus-scale answer/hint quality analyzer."""

import sys
import json
import argparse
import re
from pathlib import Path
from collections import defaultdict

REPO = Path(__file__).resolve().parents[2]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from Shared.tools.assurance_record import make_evidence, write_evidence

BOILERPLATE_PATTERNS = [
    r"^apply 2d projectile kinematic decomposition\.?$",
    r"^apply \u03a3f = ma\.?$",
    r"^follow step-by-step kinematics\.?$",
    r"^apply newton[''`]?s (first|second|third) law\.?$",
    r"^use kinematic equations?\.?$",
    r"^apply the equations? of motion\.?$",
]
COMPILED_PATTERNS = [re.compile(p) for p in BOILERPLATE_PATTERNS]

def run_analysis(library_dir: Path):
    findings = []
    stems = defaultdict(list)
    answers = defaultdict(list)
    ids = defaultdict(list)
    answer_lengths = []
    
    for file_path in library_dir.rglob("*.json"):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue
            
        records = data.get("questions", data) if isinstance(data, dict) else data
        if not isinstance(records, list):
            continue
            
        for r in records:
            if not isinstance(r, dict):
                continue
            r_id = r.get("id")
            if r_id:
                ids[r_id].append(file_path.name)
            
            stem = r.get("stem", "")
            if stem:
                stems[stem.strip()].append(r_id)
            
            ans = r.get("answer", {})
            if isinstance(ans, dict):
                ans_sum = ans.get("summary", "")
                if ans_sum:
                    norm = " ".join(ans_sum.lower().split())
                    answers[norm].append(r_id)
                    answer_lengths.append(len(ans_sum))
                    
                    for p in COMPILED_PATTERNS:
                        if p.match(norm):
                            findings.append({"type": "GENERIC_ANSWER", "id": r_id, "detail": ans_sum})
            
            hints = r.get("hints", [])
            for h in hints:
                if isinstance(h, str):
                    h_norm = " ".join(h.lower().split())
                    for p in COMPILED_PATTERNS:
                        if p.match(h_norm):
                            findings.append({"type": "GENERIC_HINT", "id": r_id, "detail": h})
                            
    for stem, r_ids in stems.items():
        if len(r_ids) > 1:
            findings.append({"type": "DUPLICATE_STEM", "ids": r_ids})
            
    for ans, r_ids in answers.items():
        if len(r_ids) > 1:
            findings.append({"type": "DUPLICATE_ANSWER", "ids": r_ids})
            
    for r_id, files in ids.items():
        if len(files) > 1:
            findings.append({"type": "DUPLICATE_ID", "id": r_id, "files": files})
            
    if answer_lengths:
        answer_lengths.sort()
        mid = len(answer_lengths) // 2
        median = (answer_lengths[mid] + answer_lengths[~mid]) / 2.0
        if median < 15:
            findings.append({"type": "SHORT_ANSWERS", "median_length": median})
            
    return findings

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-dir", type=str, required=True)
    parser.add_argument("--subject", type=str, default="corpus")
    parser.add_argument("--output", type=str)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    library_dir = Path(args.library_dir)
    findings = run_analysis(library_dir)
    
    outcome = "FAIL" if findings else "PASS"
    evidence = make_evidence(
        assurance_type="CORPUS_SPECIFICITY",
        subject_kind="library",
        subject_id=args.subject,
        outcome=outcome,
        producer_name="assurance_corpus",
        producer_version="1.0.0",
        findings=findings,
        severity="S1" if outcome == "FAIL" else None
    )
    
    if args.output:
        write_evidence(evidence, Path(args.output))
        
    print(f"Outcome: {outcome}")
    print(f"Findings: {len(findings)}")
    for f in findings:
        print(f"  - {f}")
        
    if args.enforce and outcome == "FAIL":
        sys.exit(1)

if __name__ == "__main__":
    main()
