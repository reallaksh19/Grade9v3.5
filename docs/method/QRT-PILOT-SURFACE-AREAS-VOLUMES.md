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



## Additional self-audit and interactive-browser requirements

### R9 — hint / solution / calculation self-audit

Owner requirement added during repair: every question must carry inspectable self-check evidence for its hints, solution route and calculations.

Implementation:
- `Shared/tools/question_content_audit.py` independently audits all question scaffolds, reasoning moves and arithmetic evidence.
- Each question now carries `extensions["grade9v3:calculation_audit"]` entries with a calculation ID, owning reasoning move, safe arithmetic expression, expected result, unit, and whether that result is protected pre-attempt work.
- Hint audit checks non-empty content, valid stage, valid target move, absence of protected calculated results, and absence of the complete answer summary.
- Solution audit checks a structured reasoning route, unique move IDs, a resolving crux reference, answer summary, independent check, and verification-status declaration.
- Calculation audit re-evaluates every declared expression independently and binds it to its reasoning move.
- A local PASS from this tool is explicitly **not** QRT semantic acceptance, Chromium evidence, or release approval.

Question-bank repair commits:
- `523ace6e4b3390624abb8a966bde872dd7dc7b55` — Q1–Q5 protected hint ladders + calculation evidence.
- `51cd975655a5a9fd17acc01ae4017b7eb39827c8` — Q6–Q10 protected hint ladders + calculation evidence.
- `0facd8fa5400a753b982e800ab2038e5ddf64a75` — deterministic content-audit implementation.
- `44e0a2fe52e03a51afb05b1fd385bde52a359bae` — audit evidence schema.
- `d83abd19e8bcb7479a62f8c4da2508eb3e4bb525` — regressions including a deliberate answer-leaking hint that must fail.

### R10 — Chromium is mandatory for interactive pages

Owner requirement added during repair: an interactive page is not considered reviewed unless Chromium evidence exists for the exact HTML bytes.

Implementation:
- `tools/site-audit/interactive-page-audit.mjs` launches Playwright Chromium and measures both tablet landscape and portrait.
- It records runtime smoke, page errors, console errors, external network requests, horizontal overflow, 48px touch targets, accessibility baseline, and keyboard focus.
- Receipt schema: `interactive-chromium-audit/v1`.
- `Shared/tools/interactive_chromium_gate.py` fails closed unless:
  - the receipt engine is exactly `chromium`;
  - receipt status is `PASS`;
  - all mandatory browser checks are `PASS`;
  - receipt `html_sha256` matches the current HTML bytes.
- Missing browser capability is therefore `NOT_RUN` / blocking for an interactive artifact, never an inferred PASS.

Implementation commits:
- `70fe4b28e648b1f77066ec1eb59e419d4588dea7` — Chromium audit runner.
- `c28a18d133b9d8871c2510133b5399fc033ca77d` — exact-digest Chromium gate.
- `0eec8a408c853d7502df2f8670680845e0440d9e` — receipt schema.
- `87fc63af62ea940148fac2611061677e80728064` — fail-closed receipt tests.

The Issue #13 prompt does not itself require an interactive page. If one is later included, it cannot appear in the final deliverable/audit as reviewed without this Chromium receipt.
