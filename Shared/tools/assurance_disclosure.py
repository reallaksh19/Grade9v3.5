#!/usr/bin/env python3
"""Disclosure policy conformance per spec 12."""
from __future__ import annotations
import argparse
import json
import re

try:
    from Shared.tools.assurance_record import make_evidence
except ImportError:
    def make_evidence(question_id, evidence_type, result, details=None):
        return {"question_id": question_id, "evidence_type": evidence_type, "result": result, "details": details}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-file", required=True)
    parser.add_argument("--policy-file", required=True)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    with open(args.library_file, "r") as f:
        lib_data = json.load(f)

    questions = lib_data.get("questions", [])
    
    for q in questions:
        qid = q.get("id")
        hints = q.get("hints", [])
        hint_ladder = q.get("hint_ladder", [])
        
        if not hints and not hint_ladder:
            continue
            
        stem = q.get("stem", "")
        stem_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', stem))
        
        all_hints = list(hints)
        for h in hint_ladder:
            all_hints.append(h.get("text", ""))
            
        leak = False
        for h in all_hints:
            h_nums = set(re.findall(r'\b\d+(?:\.\d+)?\b', h))
            if h_nums - stem_nums:
                leak = True
                
        if leak:
            print(f"{qid} | DISCLOSURE_CONFORMANCE | FAIL | hint leaks info")
        else:
            print(f"{qid} | DISCLOSURE_CONFORMANCE | PASS | ")

if __name__ == "__main__":
    main()
