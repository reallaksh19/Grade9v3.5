# QRT Pilot Audit Trail — Grade 9 Mathematics: Surface Areas and Volumes

**Authority:** GitHub Issue #13  
**Implementation base:** PR #9  
**Execution PR:** PR #15, branch `feat/issue-13-surface-areas-and-volumes-pilot`  
**Product ID:** `PRODUCT-MAT-G9-SAV`  
**Status:** `PILOT_REPAIR_IN_PROGRESS` — not accepted, not released, not self-certified.  
**Protocol:** `reallaksh19/Common@149770a21ca073df49717a96e2106c967adddc2d:skills/engineering-pr-delivery-v3.2`

## Chronological authority and clarification record

### Owner input present in Issue #13

The owner supplied exactly:
- repository and PR #9 implementation authority;
- ten Grade 9 Mathematics question texts;
- required learner-facing Core2 and Core1A HTML;
- machine-readable QRT review evidence;
- requirement that the core prompt not be rewritten;
- requirement for a complete audit trail;
- explicit prohibition on execution-agent self-certification.

The ten question texts in `Mathematics/question-bank/surface-areas-and-volumes.owner-bank.v1.json` are now copied from Issue #13, including punctuation, paragraph breaks, emphasis markers and `75%`. Their custody hashes are hashes of the Issue #13 text itself, not of a normalized fixture.

### Agent custody interpretation

Because the question text was supplied directly by the owner in Issue #13, the execution agent classifies it as `OWNER_SUPPLIED_RAW_INPUT` for custody. This is an **agent-derived custody interpretation**, not an owner reply to a provenance questionnaire. It does not create NCERT/CBSE/exam/year/paper provenance.

The final deliverable explicitly requests Core2 and Core1A HTML, so those roles are treated as owner-requested outputs. No separate owner answer saying “PRESERVE_OWNER_QUESTIONS” is claimed.

### Missing owner input: learner knowledge

Issue #13 contains no learner knowledge state. The previous pilot incorrectly invented an all-`DEMONSTRATED`, 100% profile. That record has been replaced by:

`evidence/reviews/surface-areas-and-volumes/learner-profile.v1.json`

with:
- `provenance: UNKNOWN`;
- empty `held`;
- `knowledge_percentage: null`;
- `measured_fit_claim: false`.

An explicit clarification request has been posted on Issue #13. Until the owner answers it, learner-specific Y and personalised X/support-fit claims are unresolved. Non-learner-dependent work continues.

### Removed fabricated directive

The prior audit attributed an interactive-page request to the owner. Issue #13 contains no such directive. That attribution is withdrawn. Any interactive resource is outside the Issue #13 acceptance requirement unless separately requested or independently justified by a governed product contract.

## Repair decision log

### R1 — audit provenance

Decision: owner statements and agent inferences must be separately labelled.  
Evidence: Issue #13 body and comments.  
Result: fabricated owner resolutions removed from this audit.

### R2 — prompt custody

Decision: Issue #13 question text is the custody source.  
Evidence: `authority_record` on the owner bank points to Issue #13.  
Result: all ten stems and SHA-256 custody hashes are regenerated from the exact issue text.

### R3 — QRT semantics

The shared resolver previously used `stable_crux_move` as X and reused `crux_move_ref` as both Z and W. This produced answer-bearing X values and Z=W for the pilot.

Repair:
- X now prefers `review_bottleneck`, otherwise the demand-template bottleneck;
- Y requires actual `DEMONSTRATED` evidence; optional bridge text is trusted only when its capability is DEMONSTRATED;
- Z prefers `review_route_to_crux`, otherwise the move immediately before protected work, otherwise the demand-template route;
- W prefers explicit `protected_work`, then an explicit protected/crux move;
- if Z and W collapse, Z falls back to the demand-template route;
- X is rejected if it contains the full answer summary.

Each pilot question now carries explicit `review_bottleneck`, `review_route_to_crux`, and `protected_work` fields that describe cognitive work without embedding the numerical answer.

Material repair commit: `8351da85518cbac9a4a357ecfb1804a88292eb7c`.

## Pending repair units

- R4 Core1A safety/content: remove same-number answer leakage and correct Q5 hemisphere teaching.
- R5 Evidence truth: rebuild authoring evidence separately from post-render review evidence; remove false PASS/accept claims.
- R6 Artifact traceability: regenerate governed Core2/Core1A HTML and bind hashes to review.
- R7 Scope cleanup: revert unrelated PR #3 fixture churn and isolate any renderer change.
- R8 Verification: focused tests, real gate, browser/render evidence where supported.

## Current blockers

1. **Learner knowledge:** owner response pending; personalised Y/support fit cannot be final.
2. **Rendered acceptance evidence:** previous gate report was static-only and returned `FAIL / RENDERED_RULES_NOT_MEASURED`; it is not acceptance evidence.
3. **Publication artifacts:** previous PR description referred to local publication files not committed in PR #15. Final traceability must point to durable repo-backed artifacts and current commit hashes.

## Non-self-certification

No entry in this file is release approval. Final acceptance remains a separate human/reviewer action.

