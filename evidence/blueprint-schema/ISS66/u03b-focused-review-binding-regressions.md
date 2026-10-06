# ISS66 U03B — focused QRT acceptance regressions

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U03B only — put review-provenance/byte-binding acceptance cases in the dedicated QRT guard test surface  
**Implementation head:** `5c767b4fa9579c90fa9eb4472f202f80103f36d4`

## Change

Updated:

`tests/test_qrt_pipeline_guard.py`

No production schema, guard, renderer or review behavior changed.

Added four focused acceptance regressions:

1. `test_author_only_review_cannot_satisfy_rendered_or_independent_acceptance`
2. `test_rendered_review_cannot_satisfy_opt_in_independent_acceptance`
3. `test_independent_rendered_review_requires_reviewer_and_satisfies_opt_in_requirement`
4. `test_changed_rendered_bytes_invalidate_preexisting_review_evidence`

The last case mutates the actual rendered file after a valid independent review is established and proves the guard returns:

`RENDERED_ARTIFACT_DIGEST_MISMATCH: CORE2`

Therefore exact rendered bytes cannot change while old review evidence remains acceptable.

## Exact-head focused workflow evidence

Workflow: `qrt-pipeline-hardening`  
Run: `37432377728`  
Job: `112166011601`  
Head: `5c767b4fa9579c90fa9eb4472f202f80103f36d4`

Result:
- workflow: **SUCCESS**
- job: **SUCCESS**
- focused QRT hardening regressions: **36 tests, OK**
- Chromium audit script syntax: **SUCCESS**
- mandatory interactive Chromium smoke audit: **SUCCESS**

The prior exact-head focused suite had 32 tests; these four acceptance cases account for the increase to 36.

## U03 acceptance result

Declared U03 acceptance required:
- author-only cannot satisfy independent rendered acceptance;
- rendered self-review cannot satisfy opt-in independent acceptance;
- independent rendered review requires declared reviewer identity;
- changed rendered bytes invalidate the old review binding;
- no duplicate provenance/artifact fields when existing contract already suffices.

All are now covered by the dedicated QRT regression surface and exact-head workflow.

## U03 result

**U03 COMPLETE and evidenced.**

Parent denominator:
- **P = 3/10 = 30%**
- **E = 3/10 = 30%**

No claim is made that:
- declared reviewer identity proves real organizational independence;
- byte/head binding captures every possible external dependency;
- repository-wide tests are all green.

Next bounded unit: **U04A — inspect live difficulty/QRT derivation against the matched stress-test classification disagreement before any schema change.**
