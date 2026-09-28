import json

lib = {
  "schema_version": "0.2.0",
  "package_id": "LIB-MATH-POLYNOMIALS",
  "version": "0.1.0",
  "status": "CANDIDATE",
  "subject": "Mathematics",
  "scope_summary": "Polynomials Grade 9",
  "curriculum_mappings": [],
  "resources": [],
  "buckets": [
    {
      "id": "BUCKET-POLYNOMIALS",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "title": "Polynomials",
      "topic": "Polynomials",
      "intrinsic_badge": "MEDIUM",
      "badge_reason": "Algebraic complexity",
      "depth_overlay": "FOUNDATION",
      "curriculum_mappings": [],
      "prerequisite_refs": [],
      "primary_representation_ref": "REP-MATH-POLY-AREA-SQUARE"
    }
  ],
  "capabilities": [],
  "microtopics": [
    {
      "id": "MIC-MATH-POLY-DEF-DEGREE",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "bucket_id": "BUCKET-POLYNOMIALS",
      "title": "Polynomial Definitions",
      "gate_ref": "MATH-GATE-POLY-DEF",
      "capability_refs": [],
      "core_concepts": ["Polynomials have non-negative integer exponents."]
    }
  ],
  "teaching_routes": [
    {
      "id": "TEACH-POLY-DEF",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "microtopic_id": "MIC-MATH-POLY-DEF-DEGREE",
      "prerequisite_bridge": {
        "prerequisite_ref": "MIC-MATH-POLY-DEF-DEGREE",
        "narrative": "Recall variables and constants.",
        "relation_ref": "MATH-GATE-POLY-DEF"
      },
      "inferential_jump": {
        "narrative": "Combine terms.",
        "relation_ref": "MATH-GATE-POLY-DEF"
      },
      "worked_anchor": {
        "steps": [
          {"narrative": "Check exponent", "expression": "<math><mi>x</mi></math>"}
        ]
      }
    }
  ],
  "tasks": [
    {
      "id": "TASK-POLY-DEF-RECONSTRUCT",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "microtopic_id": "MIC-MATH-POLY-DEF-DEGREE",
      "role": ["RECONSTRUCTION"],
      "elicitation": {
        "attempt": {
          "task": "Is x^-1 a polynomial?",
          "input_kind": "BOOLEAN"
        },
        "misconceptions": [
          {
            "name": "Negative exponent ignored",
            "diagnostic": "Yes",
            "repair_route": "Recall exponents must be positive integers."
          }
        ]
      },
      "reconstruction": {
        "rubric": "No, because exponent is -1.",
        "boundary_test": "What about 1/x?"
      }
    }
  ],
  "questions": [
    {
      "id": "Q-MATH-POLY-2-01",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": ["EV-MAT-09-POLY-02"],
      "extensions": {},
      "bucket_id": "BUCKET-POLYNOMIALS",
      "role": ["SOURCE_ASSESSMENT"],
      "stem": "Find value at x=0",
      "rubric": "3",
      "ladder_hints": ["Substitute 0", "Evaluate"]
    },
    {
      "id": "Q-MATH-POLY-2A-01",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "bucket_id": "BUCKET-POLYNOMIALS",
      "role": ["SUPPORTED_APPLICATION"],
      "stem": "Find value at x=1",
      "rubric": "4",
      "solution_breakdown": ["Substitute 1", "Evaluate"]
    },
    {
      "id": "Q-MATH-POLY-2B-01",
      "version": "0.1.0",
      "status": "CANDIDATE",
      "source_refs": [],
      "evidence_refs": [],
      "extensions": {},
      "bucket_id": "BUCKET-POLYNOMIALS",
      "role": ["TRANSFER"],
      "stem": "Evaluate p(x+1) at x=0",
      "rubric": "Find p(1)",
      "transfer_novelty": {
        "checked_against": ["Q-MATH-POLY-2A-01"],
        "novelty": "Shifted argument."
      }
    }
  ]
}

manifest = {
  "schema_version": "1.0",
  "product_id": "PRODUCT-POLYNOMIALS",
  "subject": "Mathematics",
  "bucket_id": "BUCKET-POLYNOMIALS",
  "selections": {
    "CORE1A": ["MIC-MATH-POLY-DEF-DEGREE"],
    "CORE1B": ["MIC-MATH-POLY-DEF-DEGREE"],
    "CORE2": ["Q-MATH-POLY-2-01"],
    "CORE2A": ["Q-MATH-POLY-2A-01"],
    "CORE2B": ["Q-MATH-POLY-2B-01"]
  }
}

with open("Mathematics/library/polynomials.v1.json", "w") as f:
    json.dump(lib, f, indent=2)

with open("products/mathematics/polynomials.manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
