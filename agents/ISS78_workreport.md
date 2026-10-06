# ISS78 work report — APP-A01 Mathematics custody/source inventory

## Responsibility
- Parent phase: #74 APPENDIX-A
- Programme: #69
- PRD: PRD-APP-A01
- Protocol: `reallaksh19/Common@44c779bafdabe20637270f6e34a3b865f584a26e:skills/engineering-pr-delivery-v3.2`
- Branch: `appendix-a/78-math-custody`
- Launch base: `9059848c2d2ea757b765a01c66841c8906cd7875`

## Write fence
This child may write Mathematics Question Bank source/custody records and Appendix-A evidence only. It does not own `Shared/**`, TEST rendering, or generated production Question Bank projections.

## U1 — exact source/canonical census
Completed against the launch base.

Observed canonical Question Bank:
- total: 310
- Physics: 166
- Chemistry: 126
- Mathematics: 18
- all 18 Mathematics projected records resolve to `Mathematics/library/linear-equations.v1.json`.

PR #61 candidate intake:
- 42 records
- seven topics, six records each
- claims `NCERT_OFFICIAL`, `TEXT_VERIFIED_AGAINST_OFFICIAL`, and `READY_FOR_BLUEPRINT`
- remains candidate staging evidence only; those status strings are not canonical admission.

#55 regression fixture:
- 10 questions
- schema `grade9v3-owner-supplied-bank-v1`
- authority class `OWNER_SUPPLIED_RAW_INPUT`
- coordinating-agent authored; `official_exam_or_pyq=false`
- must remain outside CBSE/NCERT canonical custody.

Machine-readable evidence: `evidence/appendix-a/ISS74/A01/canonical-census.v1.json`.

## Negative knowledge
- The 310-question platform denominator must not be described as 310 Mathematics questions.
- The 42 PR #61 TEST intake records are not part of that 310-question canonical denominator.
- A recorded stem digest proves integrity of recorded text, not independent equality to the official source.
- APP-A01 cannot repair missing shared source-intake machinery under `Shared/**`.

## Next
U2 independently verifies source custody for the 42 candidate records and records HOLD rather than accepting unverified source claims.


## PR #61 provider drift after U1

PR #61 moved from `a3b86bfe398bf85fc76dc56ebc92b09456071cea` to `76622024968ec21dcc66bb9fbeca666b935f6e2f` after the U1 census.

The new head expands the TEST intake from 42 to 210 records. The additional 168 records are not extracted NCERT questions: their stems explicitly identify themselves as placeholders (for example, “Expanded Question 7 ... official NCERT Exemplar problem intake placeholder to meet the 30-question requirement”), with generic options and answer values, while simultaneously claiming `NCERT_OFFICIAL`, `VERBATIM_EXTRACTION`, `TEXT_VERIFIED_AGAINST_OFFICIAL`, and `READY_FOR_BLUEPRINT`.

Disposition for APP-A01:
- 168 added placeholder records: `SOURCE_HOLD_FABRICATED_PLACEHOLDER`.
- original 42 non-placeholder records: `PENDING_INDEPENDENT_SOURCE_VERIFICATION`; prior self-declared verification is not accepted as independent evidence.
- production/public projection is also drifted: `public/test/index.html` reports 210 while `docs/test/index.html` still reports 42.
- exact-head GitHub Actions are not all green: Question Bank Platform, V31 Relay, and Core1A Tablet Browser are failed at observation time; Guardrails and Canonical Assurance are still running.

Evidence: `evidence/appendix-a/ISS74/A01/pr61-head-integrity-audit.v1.json`.

This drift does not invalidate U1's exact historical observation at `a3b86bfe`; it changes U2's verification frontier and must be preserved rather than silently rewriting the earlier basis.
