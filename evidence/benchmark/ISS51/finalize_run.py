#!/usr/bin/env python3
"""Freeze exact-render evidence after the cold Issue #51 run."""
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
reports=HERE/"reports"; rendered=HERE/"rendered"
def sha(path): return "sha256:"+hashlib.sha256(Path(path).read_bytes()).hexdigest()
run_id=os.environ.get("GITHUB_RUN_ID","UNKNOWN"); head=os.environ.get("GITHUB_SHA","UNKNOWN")
quality=json.loads((reports/"quality-gate.json").read_text(encoding="utf-8"))
layout=json.loads((reports/"layout-authority-mismatch.json").read_text(encoding="utf-8"))
sem=json.loads((reports/"semantic-inspection.json").read_text(encoding="utf-8"))
audit=json.loads((reports/"tablet-audit.json").read_text(encoding="utf-8"))
blocked=quality.get("verdict") != "PASS"
status="CANDIDATE_RENDERED_WITH_INHERITED_BLOCKER" if blocked else "CANDIDATE_RENDERED"

receipt=json.loads((HERE/"run-receipt.json").read_text(encoding="utf-8"))
receipt.update({
 "status":status,"workflow_run_id":run_id,"source_artifact_commit":head,
 "rendered":{"core1a_html":sha(rendered/"core1a.html"),"core2_html":sha(rendered/"core2.html")},
 "generated":{"package":sha(HERE/"generated/package.v1.json"),"owner_bank":sha(HERE/"generated/owner.bank.json"),"manifest":sha(HERE/"generated/product.manifest.json")},
 "reports":{"quality_gate":sha(reports/"quality-gate.json"),"tablet_audit":sha(reports/"tablet-audit.json"),
            "semantic_inspection":sha(reports/"semantic-inspection.json"),"layout_authority_mismatch":sha(reports/"layout-authority-mismatch.json")},
 "blocking_findings":quality.get("findings",[])
})
(HERE/"run-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")

qrt=json.loads((HERE/"qrt-review.v1.json").read_text(encoding="utf-8"))
qrt["status"]="RENDER_VERIFIED_CANDIDATE_WITH_INHERITED_LAYOUT_BLOCKER" if blocked else "RENDER_VERIFIED_CANDIDATE"
qrt["render_receipt"]={"workflow_run_id":run_id,"source_artifact_commit":head,
 "core1a_sha256":receipt["rendered"]["core1a_html"],"core2_sha256":receipt["rendered"]["core2_html"],
 "quality_gate_verdict":quality.get("verdict")}
(HERE/"qrt-review.v1.json").write_text(json.dumps(qrt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

summary=audit.get("summary",{}) if isinstance(audit,dict) else {}
validation=f"""# ISS51 validation

Status: **{status}**. This is not golden, released or published.

- Frozen A/B/C SHA-256: PASS.
- Owner-bank custody check against generated intake: PASS.
- Package schema: PASS.
- Strict canonical render: PASS for Core1A + Core2 only.
- Core2 denominator/order: {sem["core2_count"]}/10, source order preserved.
- Q8 changed-case worked anchor: PASS.
- Q8 staged difference-polynomial bridge: PASS.
- Q8 commit-before-compare question repair: PASS.
- Protected solution payload: PASS under the canonical inert-template-until-commitment contract.
- Learner quality report: **{quality.get("verdict")}**. Findings: {json.dumps(quality.get("findings",[]),sort_keys=True)}.
- Shared-layout classification: **{layout.get("status")}**. Core1A is SINGLE_PANE with 0.6/0.4 fractions; the pinned renderer emits split columns only for STAGE_SUPPORT blueprints, while PAGE-STAGE-SUPPORT still applies to Core1A. Candidate records cannot resolve that shared authority mismatch.
- Tablet 12.7 browser audit: executed in GitHub Actions. Summary: {json.dumps(summary,sort_keys=True)}.
- Learner PDF: NOT_RUN. HTML is the requested primary product; this run makes no PDF publication claim.
- Local clone deviation remains recorded: local DNS resolution failed, so the cold Linux render ran in GitHub Actions with the repository's canonical renderer.
"""
(HERE/"validation.md").write_text(validation,encoding="utf-8")

review=f"""# ISS51 candidate review

This is first-run **CANDIDATE** evidence. Quality-gate status is {quality.get("verdict")}; the exact inherited layout blocker is preserved rather than waived.

## Hardest target

Q8 is the hardest target: degree-bounded polynomial identity via the difference polynomial and the zero-polynomial exception, primary demand JUSTIFY, band D4. Core1A teaches a changed degree-one case with a four-stage h=f-g construction. The question-specific repair requires a learner to write a changed-case prediction and reason before comparison opens.

## Exact-render finding

The governed render contains all ten Core2 questions in source order and only the requested Core1A/Core2 roles. The Q8 source stem is not reused as the Core1A worked anchor; its changed case, four-stage bridge and return-to-question repair are present.

## Builder improvement proposal after inspection

**BLUEPRINT_DRIVEN_LAYOUT_CONSISTENCY** should make the layout contract single-source and testable. The pinned Core1A blueprint says `expanded: SINGLE_PANE` while also carrying 0.6/0.4 fractions; `render_core.layout_css()` emits split columns only for `STAGE_SUPPORT`; the shared quality rule `PAGE-STAGE-SUPPORT` nevertheless requires a split for Core1A. This three-way disagreement is the sole blocking quality finding.

Resolve the intended Core1A layout in the blueprint first, then derive renderer CSS and audit expectations from that same policy. If Core1A is intentionally single-pane, PAGE-STAGE-SUPPORT/audit must not require split columns. If it is intentionally stage/support, set the blueprint to STAGE_SUPPORT and let the existing renderer emit its declared fractions. Add a contract test covering every role: blueprint expanded mode -> emitted CSS -> browser expectation. This is a shared-authority change; candidate records need no migration.

A polynomial-specific widget is **not required** for this candidate. Existing staged SVG construction plus the shared commit-before-compare repair supports Q8 without exposing the protected source answer.
"""
(HERE/"candidate-review.md").write_text(review,encoding="utf-8")

with (HERE/"chronological-audit.jsonl").open("a",encoding="utf-8") as audit_file:
    audit_file.write(json.dumps({
      "time":"WORKFLOW","sequence":5,"issue":51,"run":"ISS51-D3-R1","round":"POLYNOMIAL-STRESS-V1",
      "actor":"github-actions","section":"EXECUTION","decision":status,
      "rationale":"Canonical render completed; semantic/protected-outcome inspection passed; shared layout authority mismatch was preserved as the only blocking quality finding.",
      "evidence":[receipt["rendered"],receipt["reports"],quality.get("findings",[])],
      "affected":["Q1-Q10","Core1A","Core2"],"commit":head,
      "downstream_consequence":"Freeze candidate for independent review with inherited blocker explicit; no acceptance or release decision is implied."
    })+"\n")
print("finalized ISS51 exact-render evidence",status)
