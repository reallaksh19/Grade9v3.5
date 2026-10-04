# QRT Pilot Audit Trail — Grade 9 Mathematics: Surface Areas and Volumes

**Authority:** GitHub Issue #13  
**Implementation base:** PR #9  
**Execution PR:** PR #15, branch `feat/issue-13-surface-areas-and-volumes-pilot`  
**Product ID:** `PRODUCT-MAT-G9-SAV`  
**Status:** `PILOT_REPAIR_VERIFIED_AWAITING_OWNER_PROFILE_AND_HUMAN_ACCEPTANCE` — targeted repair work is verified, but the product is not accepted, released, or self-certified.  
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

## Completed repair units

- **R4 Core1A safety/content — complete.** Pre-attempt Core1A representations are generic rather than question-answer worked diagrams. Q5 now consistently teaches the curved inner hemispherical material surface versus the open circular mouth; its badge reason, inferential jump, relation, misconception, exit task, teaching-step inputs, representation title/description, and construction path no longer model hemisphere capacity/volume.
- **R5 Evidence truth — complete for the targeted repair.** The learner profile remains `UNKNOWN` rather than fabricated as 100% demonstrated. Generated pedagogy therefore reports `PENDING_OWNER_PROFILE`; no personalised Y/support-fit PASS is claimed.
- **R6 Artifact traceability — complete for CI evidence.** The governed render is generated in CI and exact hashes are recorded for `core2.html`, `core1a.html`, and `render-receipt.json`.
- **R7 Scope/determinism cleanup — complete.** The PR #3 QRT fixture is restored to canonical ask order, derived Question Bank/Pages artifacts were regenerated deterministically, and the temporary repair workflow was returned to its normal check-only behavior.
- **R8 Verification — complete for the targeted repair.** Focused semantic/safety regressions, transitive pre-attempt leak audit, reference-depth render, measured quality gate, tablet Chromium audit, and final evidence enforcement all pass.
- **R11 Transitive pre-attempt leak protection — complete.** The auditor follows reachable Core2 scaffolds/conditions/analysis plus linked Core1A unit decisions, teaching steps, representation records, and user-visible SVG text. SVG HTML entities are decoded before parsing; raw SVG coordinate metadata is not treated as learner-visible text. The real ten-question package passes with zero leak findings.
- **R12 Rendered shell integration — complete.** Governed pages expose the `data-g9-shell-header` marker and concept breadcrumb/action groups are navigation landmarks inheriting the 48px touch-target contract.

## Final verification evidence

Verified workflow: `surface-areas-volumes-pilot` run **37168541548** on head `669d4b63be5e3a0a032e9e62b28821eaca07088a`.

- Focused semantic and safety regressions: **47 tests, 47 passing**.
- Question content self-audit: **PASS**.
- Transitive pre-attempt leak audit: **PASS**, 10 questions, **0 findings**.
- Reference-depth render: **0 depth gaps**. The renderer separately reports 8 `GATE_RELATION_BINDING_ABSENT` subject-authority findings; this audit does not claim engineering-gate binding for those eight mathematical relations.
- Measured quality gate: **PASS; 0 findings**.
- Tablet Chromium enforcement: **PASS**; `core1a.html` and `core2.html` both have **0** targets below 48px and no horizontal overflow in the enforced tablet viewports.
- Interactive-page count: **0**. No interactive artifact is claimed as part of the current pilot evidence.
- Final rendered-evidence enforcement: **PASS**.
- CI evidence artifact digest: `sha256:f646819201b27e9f431ec9293db0d82cbaa12d89f2cb0ea94ff6c714aa0e3473`.
- Governed artifact hashes:
  - `core2.html`: `sha256:0c8c1fa5fb34b5ee0ba5fe5f282bcc5b839bd1fc443e9bc37629325a3a54e736`
  - `core1a.html`: `sha256:f9622e96cf85dd3637f9627b4a834c453fe40e431c498077af041e26cf197401`
  - `render-receipt.json`: `sha256:98cb6d03eb4fdaef222f90792f199cec98db9c522ca17df52b61409c101ad616`
- Render stamp: `render_core/2 277bb3878e080331`.

## Remaining limitations / blockers to product acceptance

1. **Learner knowledge remains unresolved:** the owner has not supplied demonstrated learner capability evidence. The generated pedagogy batch correctly remains `PENDING_OWNER_PROFILE`; learner-specific Y and personalised support-fit claims are not final.
2. **Human acceptance remains required:** a green repair workflow is evidence, not release approval or owner acceptance.
3. **Relation engineering-gate binding is not claimed:** the reference renderer reports eight subject-authority findings for mathematical relations that state subject truth without an engineering gate behind them. They are disclosed here rather than converted into a false PASS claim.

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


### R13 — final targeted repair status

At the verified head above, the four repair targets that motivated this repair cycle are now in these states:

- **X/Y/Z/W semantics:** implemented and regression-covered. X is the review bottleneck, Y requires demonstrated learner evidence, Z is the route to the crux / preceding move, W is explicit protected work; Z/W collapse and answer-bearing X are rejected.
- **Audit truth:** repaired. Owner input is separated from agent inference; Issue #13 remains the custody authority; the fabricated 100% learner profile and fabricated interactive owner directive are withdrawn.
- **Transitive leak protection:** implemented, CI-wired, regression-covered, and passing on the real Surface Areas & Volumes package.
- **Q5/Core1A mapping:** repaired end-to-end to curved inner surface versus open mouth; the prior hemisphere volume/capacity contamination has been removed from canonical teaching metadata and the SVG representation.

Therefore the **targeted repair set is complete**, subject to the unresolved learner-profile input and separate human acceptance described above.
