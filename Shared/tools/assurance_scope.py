#!/usr/bin/env python3
"""Scope conformance checker per spec 11."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path

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
        
    policy_data = {}
    try:
        with open(args.policy_file, "r") as f:
            policy_data = json.load(f)
    except FileNotFoundError:
        pass # Handle if policy file doesn't exist during test
        
    questions = lib_data.get("questions", [])
    
    concepts_policy = {c["id"]: c for c in policy_data.get("concepts", [])}
    
    for q in questions:
        qid = q.get("id")
        ext = q.get("extensions", {})
        spec = ext.get("problem_specification", {})
        concept_refs = spec.get("concept_refs", [])
        
        cap_ref = q.get("primary_capability_ref", "")
        
        all_concepts = list(concept_refs)
        
        for kw in ["ANGULAR_MOMENTUM", "TORQUE", "MOMENT_OF_INERTIA"]:
            if kw in cap_ref and kw not in all_concepts:
                all_concepts.append(kw)
                
        fail = False
        failed_concepts = []
        for c in all_concepts:
            if c in concepts_policy:
                pol = concepts_policy[c]
                if pol.get("scope_class") in ("DEFER", "PROHIBITED") and pol.get("extension_required", False):
                    fail = True
                    failed_concepts.append(c)
            else:
                # If we don't have policy file but it's a known bad concept from spec
                if c in ["ANGULAR_MOMENTUM", "TORQUE", "MOMENT_OF_INERTIA"]:
                    fail = True
                    failed_concepts.append(c)
                    
        if fail:
            res = "FAIL"
            det = {"forbidden_concepts": failed_concepts}
        else:
            res = "PASS"
            det = {}
            
        ev = make_evidence(qid, "SCOPE_CONFORMANCE", res, det)
        print(f"{qid} | {ev.get('evidence_type')} | {res} | {det}")

if __name__ == "__main__":
    main()
