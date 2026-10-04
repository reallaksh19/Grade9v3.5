#!/usr/bin/env python3
"""Normalize Issue #37 package fields to the repository vocabulary without changing intent."""
from __future__ import annotations

import json
from pathlib import Path

path = Path(__file__).resolve().parent / "generated" / "package.v1.json"
doc = json.loads(path.read_text(encoding="utf-8"))

# Product intent is COMPETITION, but package depth vocabulary is
# FOUNDATION | EXAM | ADVANCED | RESEARCH. This candidate maps that intent to
# ADVANCED while keeping the owner product intent explicit in extensions.
for resource in doc.get("resources", []):
    if resource.get("id") == "SRC-ISS37-OWNER-BENCHMARK":
        resource["depth"] = ["ADVANCED"]
for bucket in doc.get("buckets", []):
    if bucket.get("id") == "BUCKET-CHEM-HYBRID-MODEL-BOUNDARIES":
        bucket["depth_overlay"] = "ADVANCED"

doc.setdefault("extensions", {}).setdefault("grade9v3:authoring_specimen", {})["product_intent"] = "COMPETITION"
path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"normalized package depth vocabulary: {path}")
