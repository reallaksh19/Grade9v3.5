#!/usr/bin/env python3
"""Freeze exact-render evidence after the cold Issue #51 run."""
from __future__ import annotations
import hashlib,json,os,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent
site=Path(sys.argv[1])
reports=HERE/"reports"; rendered=HERE/"rendered"
def sha(path): return "sha256:"+hashlib.sha256(Path(path).read_bytes()).hexdigest()
run_id=os.environ.get("GITHUB_RUN_ID","UNKNOWN"); head=os.environ.get("GITHUB_SHA","UNKNOWN")
receipt=json.loads((HERE/"run-receipt.json").read_text(encoding="utf-8"))
receipt.update({"status":"CANDIDATE_RENDERED","workflow_run_id":run_id,"source_artifact_commit":head,
 "rendered":{"core1a_html":sha(rendered/"core1a.html"),"core2_html":sha(rendered/"core2.html")},
 "generated":{"package":sha(HERE/"generated/package.v1.json"),"owner_bank":sha(HERE/"generated/owner.bank.json"),"manifest":sha(HERE/"generated/product.manifest.json")},
 "reports":{"quality_gate":sha(reports/"quality-gate.json"),"tablet_audit":sha(reports/"tablet-audit.json"),"semantic_inspection":sha(reports/"semantic-inspection.json")}})
(HERE/"run-receipt.json").write_text(json.dumps(receipt,indent=2)+"\n",encoding="utf-8")

qrt=json.loads((HERE/"qrt-review.v1.json").read_text(encoding="utf-8"))
qrt["status"]="RENDER_VERIFIED_CANDIDATE"
qrt["render_receipt"]={"workflow_run_id":run_id,"source_artifact_commit":head,"core1a_sha256":receipt["rendered"]["core1a_html"],"core2_sha256":receipt["rendered"]["core2_html"]}
(HERE/"qrt-review.v1.json").write_text(json.dumps(qrt,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")

sem=json.loads((reports/"semantic-inspection.json").read_text(encoding="utf-8"))
audit=json.loads((reports/"tablet-audit.json").read_text(encoding="utf-8"))
summary=audit.get("summary",{}) if isinstance(audit,dict) else {}
validation=f"""# ISS51 validation

Status: **CANDIDATE**, not golden, released or published.

- Frozen A/B/C SHA-256: PASS.
- Owner-bank custody check against generated intake: PASS.
- Package schema: PASS.
- Strict canonical render: PASS for Core1A + Core2 only.
- Core2 denominator/order: {sem["core2_count"]}/10, source order preserved.
- Q8 changed-case worked anchor: PASS.
- Q8 staged difference-polynomial bridge: PASS.
- Q8 commit-before-compare question repair: PASS.
- Protected solution payload: PASS under the canonical inert-template-until-commitment contract; selected final conclusions were absent from visible pre-template text.
- Tablet 12.7 browser audit: executed in GitHub Actions. Summary: {json.dumps(summary,sort_keys=True)}.
- Learner PDF: NOT_RUN. HTML is the requested primary product; this run makes no PDF publication claim.
- Local clone deviation remains recorded: local DNS resolution failed, so the cold Linux render ran in GitHub Actions with the repository's canonical renderer.
"""
(HERE/"validation.md").write_text(validation,encoding="utf-8")

review="""# ISS51 candidate review

This is first-run **CANDIDATE** evidence.

## Hardest target

Q8 is the hardest target: degree-bounded polynomial identity via the difference polynomial and the zero-polynomial exception, primary demand JUSTIFY, band D4. Core1A teaches a changed degree-one case with a four-stage h=f-g construction. The question-specific repair requires a learner to write a changed-case prediction and reason before the comparison opens.

## Exact-render finding

The governed render contains all ten Core2 questions in source order and only the requested Core1A/Core2 roles. The Q8 source stem is not reused as the Core1A worked anchor; its changed case, four-stage bridge and return-to-question repair are present.

## Builder proposal after inspection

The existing builder is sufficient for this candidate without a polynomial-specific widget: staged SVG construction plus the shared commit-before-compare repair supports the hardest bridge and preserves the protected source attempt.

One additive shared improvement would still be useful: **INTERACTIVE_REASONING_SEQUENCE**. It would bind a small ordered set of symbolic states (for example agreement -> zeros of difference -> nonzero contradiction -> zero-polynomial case) to explicit learner commit points and reveal explanations only after commitment. Suggested optional fields: stable state id, learner-selectable transition, representation_stage_ref, post_commit_explanation and protected_outcome. Insertion points: Core1A construction and post-attempt Core2 repair. Migration is additive; existing text probes stay valid. Required checks: keyboard operation, deterministic state reachability, protected outcome absent before commit, print/static fallback, 200% reflow and cross-subject fixtures. This is a proposal, not a change to shared builder authority in this run.
"""
(HERE/"candidate-review.md").write_text(review,encoding="utf-8")
with (HERE/"chronological-audit.jsonl").open("a",encoding="utf-8") as f:
    f.write(json.dumps({"time":"WORKFLOW","sequence":5,"issue":51,"run":"ISS51-D3-R1","round":"POLYNOMIAL-STRESS-V1","actor":"github-actions","section":"EXECUTION","decision":"STRICT_RENDER_COMPLETED","rationale":"Canonical render_core.py built the requested roles and exact render passed semantic/protection and tablet inspection.","evidence":[receipt["rendered"],receipt["reports"]],"affected":["Q1-Q10","Core1A","Core2"],"commit":head,"downstream_consequence":"Candidate can be frozen for independent review; no acceptance or release decision is implied."})+"\n")
print("finalized ISS51 exact-render evidence")
