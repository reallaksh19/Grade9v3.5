import json

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
  "bank_refs": [],
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

with open("products/mathematics/polynomials.manifest.json", "w") as f:
    json.dump(manifest, f, indent=2)
