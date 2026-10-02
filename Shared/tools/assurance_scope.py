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
        pass
        
    questions = lib_data.get("questions", [])
    
    deferred_concepts = set()
    for c in policy_data.get("concept_policies", []):
        if c.get("scope_class") in ("DEFER", "PROHIBITED"):
            deferred_concepts.add(c.get("concept_id"))
            
    # For testing if no policy provided
    if not deferred_concepts:
        deferred_concepts.update(["CONCEPT-ANGULAR-MOMENTUM", "CONCEPT-TORQUE", "CONCEPT-MOMENT-OF-INERTIA", "CONCEPT-ROTATIONAL-KINETIC-ENERGY"])
    
    any_fail = False
    
    for q in questions:
        qid = q.get("id")
        ext = q.get("extensions", {})
        spec = ext.get("problem_specification", {})
        concept_refs = spec.get("concept_refs", [])
        
        cap_ref = q.get("primary_capability_ref", "").lower().replace("_", "-")
        stem = q.get("stem", "").lower().replace("_", "-")
        
        fail = False
        failed_concepts = []
        
        for deferred_c in deferred_concepts:
            dc_norm = deferred_c.lower().replace("_", "-")
            
            # Check concept_refs substring
            in_refs = any(dc_norm in c_ref.lower().replace("_", "-") for c_ref in concept_refs)
            
            # Check primary capability and stem text case-insensitive substring
            if in_refs or dc_norm in cap_ref or dc_norm in stem:
                fail = True
                if deferred_c not in failed_concepts:
                    failed_concepts.append(deferred_c)
                    
        if fail:
            res = "FAIL"
            any_fail = True
            det = {"forbidden_concepts": failed_concepts}
        else:
            res = "PASS"
            det = {}
            
        try:
            from Shared.tools.assurance_record import make_evidence
        except ImportError:
            pass
            
        print(f"{qid} | SCOPE_CONFORMANCE | {res} | {det}")

    if args.enforce and any_fail:
        sys.exit(1)

if __name__ == "__main__":
    main()
