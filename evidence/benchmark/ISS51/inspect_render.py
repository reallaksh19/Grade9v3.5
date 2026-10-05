#!/usr/bin/env python3
"""Inspect exact governed Issue #51 HTML after render."""
from __future__ import annotations
import json,re,sys
from html.parser import HTMLParser
from pathlib import Path

root=Path(sys.argv[1])
core1a=(root/"core1a.html").read_text(encoding="utf-8")
core2=(root/"core2.html").read_text(encoding="utf-8")
expected=[f"OWN-ISS51-POLY-{i:02d}" for i in range(1,11)]
actual=re.findall(r'<article\b[^>]*data-g9-unit="([^"]+)"[^>]*data-g9-kind="QUESTION"',core2)
if actual!=expected:
    raise SystemExit(f"Core2 denominator/order mismatch: {actual!r}")

class VisibleText(HTMLParser):
    def __init__(self):
        super().__init__(); self.skip=0; self.buf=[]
    def handle_starttag(self,tag,attrs):
        if tag=="template": self.skip+=1
    def handle_endtag(self,tag):
        if tag=="template" and self.skip: self.skip-=1
    def handle_data(self,data):
        if not self.skip: self.buf.append(data)

p=VisibleText(); p.feed(core2)
visible=" ".join(" ".join(p.buf).split())
for forbidden in [
    "k=0; p(x)=(x-3)(x-2)(x+2)",
    "True. Let r=p-q",
    "For q there are no real zeros"
]:
    if forbidden in visible:
        raise SystemExit(f"protected conclusion visible before template protection: {forbidden}")

checks={
"core2_count":len(actual),
"core2_order":actual,
"only_requested_roles":all((root/x).exists() for x in ("core1a.html","core2.html")) and not any((root/x).exists() for x in ("core1b.html","core2a.html","core2b.html")),
"q8_changed_case_anchor":"Suppose f and g are real polynomials of degree at most one and agree at two distinct real inputs" in core1a,
"q8_source_stem_not_used_as_worked_anchor":"Two real polynomials $p$ and $q$ each have degree at most two and agree at three distinct real inputs" not in core1a,
"q8_repair_interaction":'data-g9-learning-repair="OWN-ISS51-POLY-08"' in core2 and 'data-g9-repair-target="OWN-ISS51-POLY-08"' in core1a,
"q8_staged_identity_bridge":all(f'data-g9-stage-id="POLY-ID-{i}"' in core1a for i in range(1,5)),
"protected_solution_templates":'<template data-g9-payload=' in core2
}
bad=[k for k,v in checks.items() if not v]
if bad: raise SystemExit("semantic inspection failed: "+", ".join(bad))
report={"status":"PASS",**checks,"protected_outcome_method":"visible text excludes inert template payloads before learner commitment"}
(root/"semantic-inspection.json").write_text(json.dumps(report,indent=2)+"\n",encoding="utf-8")
print(json.dumps(report,indent=2))
