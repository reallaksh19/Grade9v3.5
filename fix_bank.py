import json

bank = {
  "schema_version": "0.1.0",
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
    }
  ]
}
with open("Mathematics/library/polynomials-bank.v1.json", "w") as f: json.dump(bank, f, indent=2)

manifest = {
  "schema": "product-manifest/v1",
  "product_id": "PRODUCT-POLYNOMIALS",
  "title": "Polynomials",
  "subject": "Mathematics",
  "home_href": "../../../index.html",
  "question_bank_href": "../../../question-bank/index.html",
  "package_refs": [
    "Mathematics/library/polynomials.v1.json"
  ],
  "bank_refs": [
    "Mathematics/library/polynomials-bank.v1.json"
  ],
  "selection": {
    "microtopics": [
      "MIC-MATH-POLY-DEF-DEGREE"
    ],
    "core2": [
      "Q-MATH-POLY-2-01"
    ],
    "core2a": [
      "Q-MATH-POLY-2A-01"
    ],
    "core2b": [
      "Q-MATH-POLY-2B-01"
    ]
  }
}
with open("products/mathematics/polynomials.manifest.json", "w") as f: json.dump(manifest, f, indent=2)

# I also need to remove Q-MATH-POLY-2-01 from polynomials.v1.json's "questions"
lib = json.load(open("Mathematics/library/polynomials.v1.json"))
lib["questions"] = [q for q in lib["questions"] if q["id"] != "Q-MATH-POLY-2-01"]
with open("Mathematics/library/polynomials.v1.json", "w") as f: json.dump(lib, f, indent=2)
