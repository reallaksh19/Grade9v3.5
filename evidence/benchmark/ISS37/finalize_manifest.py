#!/usr/bin/env python3
"""Scope the Issue #37 benchmark product to the two owner-requested learner roles."""
from __future__ import annotations

import json
from pathlib import Path

path = Path(__file__).resolve().parent / "generated" / "product.manifest.json"
doc = json.loads(path.read_text(encoding="utf-8"))

selection = doc.get("selection") or {}
if selection.get("core2a") != [] or selection.get("core2b") != []:
    raise SystemExit("Issue #37 must not silently carry Core2A/Core2B practice into this paired benchmark")

# product_manifest.py preserves legacy all-six-role output when output_roles is
# absent. Issue #37 explicitly requests only Core1A and Core2, so scope the
# projection rather than weakening AUTHOR_PRACTICE coverage checks.
doc["output_roles"] = ["CORE1A", "CORE2"]

path.write_text(json.dumps(doc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"scoped manifest output roles: {path}")
