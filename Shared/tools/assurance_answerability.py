#!/usr/bin/env python3
"""Blind answerability verifier per spec 16."""
from __future__ import annotations
import argparse
import json
import re
import sys
from pathlib import Path

try:
    import sympy
    from sympy import sin, cos, sqrt, pi, N as sym_N, rad as sym_rad
    _SYMPY_AVAILABLE = True
except ImportError:
    _SYMPY_AVAILABLE = False

try:
    from Shared.tools.assurance_record import make_evidence
except ImportError:
    def make_evidence(question_id, evidence_type, result, details=None):
        return {"question_id": question_id, "evidence_type": evidence_type, "result": result, "details": details}

def verify_self_containment(q):
    ext = q.get("extensions", {})
    spec = ext.get("problem_specification")
    
    if spec is None:
        stem = q.get("stem", "")
        answer = q.get("answer", {})
        has_numeric = "numeric" in answer
        stem_digits = re.findall(r'\d+', stem)
        ans_summary = answer.get("summary", "")
        has_num_result = bool(re.search(r'\d+', ans_summary))
        
        if has_numeric and not stem_digits:
            return "INCONCLUSIVE", "potential missing-given"
        if has_num_result and len(stem_digits) < 2:
            return "INCONCLUSIVE", "potential missing-given"
        return "NOT_APPLICABLE", "no problem spec"

    v = {f["symbol"] for f in spec.get("visible_facts", [])}
    c = {f["symbol"] for f in spec.get("permitted_constants", [])}
    a = set(spec.get("declared_assumptions", []))
    allowed = v | c | a

    ans = q.get("answer", {})
    text = (ans.get("summary", "") + " " + " ".join(ans.get("reasoning_route", [])) + " " + " ".join(ans.get("reasoning", [])))
    
    tokens = re.findall(r'\b[a-zA-Z]{1,2}\b', text)
    hidden = set()
    common_words = {"A", "a", "an", "the", "in", "on", "at", "to", "of", "is", "be", "it", "or", "so", "by", "if", "as", "no", "we"}
    for t in tokens:
        if t not in common_words and t not in allowed:
            hidden.add(t)
    
    if hidden:
        return "FAIL", {"findings": ["HIDDEN_GIVEN"], "symbols": list(hidden)}
    return "PASS", {}

def verify_answer_correctness(q):
    import math
    ext = q.get("extensions", {})
    comp = ext.get("computation_model")
    ans_contract = ext.get("answer_contract", {})
    ans = q.get("answer", {})
    numeric = ans.get("numeric")

    if not comp or not numeric:
        return "NOT_APPLICABLE", {}

    model_type = comp.get("model_type")
    variables = comp.get("variables", {})

    try:
        if model_type == "PROJECTILE_NO_DRAG":
            u = float(variables.get("u", {}).get("value", 0))
            theta_deg = float(variables.get("theta", {}).get("value", 0))
            g = float(variables.get("g", {}).get("value", 0))
            theta_rad = math.radians(theta_deg)
            computed = (u ** 2) * math.sin(2 * theta_rad) / g
        elif model_type == "PROJECTILE_MAX_HEIGHT":
            u = float(variables.get("u", {}).get("value", 0))
            theta_deg = float(variables.get("theta", {}).get("value", 0))
            g = float(variables.get("g", {}).get("value", 0))
            theta_rad = math.radians(theta_deg)
            computed = (u ** 2) * (math.sin(theta_rad) ** 2) / (2 * g)
        elif model_type == "PROJECTILE_TIME_OF_FLIGHT":
            u = float(variables.get("u", {}).get("value", 0))
            theta_deg = float(variables.get("theta", {}).get("value", 0))
            g = float(variables.get("g", {}).get("value", 0))
            theta_rad = math.radians(theta_deg)
            computed = 2 * u * math.sin(theta_rad) / g
        elif model_type == "LINEAR_KINEMATICS":
            # s = u*t + 0.5*a*t^2  or  v = u + a*t — dispatched by requested_output
            u = float(variables.get("u", {}).get("value", 0))
            a = float(variables.get("a", {}).get("value", 0))
            t = float(variables.get("t", {}).get("value", 0))
            req = comp.get("requested_outputs", ["s"])
            if "v" in req:
                computed = u + a * t
            else:
                computed = u * t + 0.5 * a * t ** 2
        else:
            return "NOT_APPLICABLE", {"model_type": model_type}

        stored = float(numeric.get("value", 0))
        tol_rel = ans_contract.get("tolerance", {}).get("relative", 0.01)

        if abs(computed - stored) <= tol_rel * abs(computed) + 1e-9:
            return "PASS", {"computed": round(computed, 6), "stored": stored}
        else:
            return "FAIL", {"computed": round(computed, 6), "stored": stored,
                            "diff": round(abs(computed - stored), 6)}
    except Exception as e:
        return "FAIL", {"error": str(e)}


def verify_dimensional_correctness(q):
    ext = q.get("extensions", {})
    contract = ext.get("answer_contract", {})
    ans = q.get("answer", {})
    numeric = ans.get("numeric", {})
    
    expected_dim = contract.get("expected_dimension")
    if not expected_dim:
        return "NOT_APPLICABLE", {}
        
    unit = numeric.get("unit")
    if not unit:
        return "FAIL", {"error": "Missing unit"}
        
    valid_units = {
        "LENGTH": ["m", "cm", "km", "ft"],
        "TIME": ["s", "ms", "min", "hr"],
        "SPEED": ["m/s", "km/h"],
        "ACCELERATION": ["m/s^2"],
        "FORCE": ["N", "kN"],
        "ANGLE": ["deg", "rad"]
    }
    
    if expected_dim in valid_units:
        if unit in valid_units[expected_dim]:
            return "PASS", {}
        else:
            return "FAIL", {"expected_dimension": expected_dim, "unit": unit}
            
    return "NOT_APPLICABLE", {}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--library-file", required=True)
    parser.add_argument("--enforce", action="store_true")
    parser.add_argument("--output")
    args = parser.parse_args()
    
    with open(args.library_file, "r") as f:
        data = json.load(f)
        
    questions = data.get("questions", [])
    
    all_evidence = []
    
    for q in questions:
        qid = q.get("id")
        
        res, det = verify_self_containment(q)
        ev1 = make_evidence(qid, "SELF_CONTAINMENT", res, det)
        all_evidence.append(ev1)
        
        res, det = verify_answer_correctness(q)
        ev2 = make_evidence(qid, "ANSWER_CORRECTNESS", res, det)
        all_evidence.append(ev2)
        
        res, det = verify_dimensional_correctness(q)
        ev3 = make_evidence(qid, "DIMENSIONAL_CORRECTNESS", res, det)
        all_evidence.append(ev3)
        
    for ev in all_evidence:
        qid = ev.get("question_id")
        ev_type = ev.get("evidence_type")
        res = ev.get("result")
        det = ev.get("details", {})
        if isinstance(det, str):
            det_str = det
        else:
            det_str = " ".join(f"{k}={v}" for k, v in det.items())
        if res != "NOT_APPLICABLE":
            print(f"{qid} | {ev_type} | {res} | {det_str}")
            
    if args.output:
        with open(args.output, "w") as f:
            json.dump(all_evidence, f, indent=2)

if __name__ == "__main__":
    main()
