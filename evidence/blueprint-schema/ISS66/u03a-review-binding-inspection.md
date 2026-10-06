# ISS66 U03A — review provenance and artifact-binding contract inspection

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U03A only — inspect existing review provenance and artifact binding before schema change  
**Basis head:** `d09d6d48b867fbed7d901fcd5afee334cbf60bc6`

## Acceptance behavior under inspection

U03 requires evidence that:

1. author-only/self-rendered review cannot satisfy an opt-in independent-rendered acceptance requirement; and
2. changed rendered bytes invalidate the bound review.

This task inspects whether those behaviors already exist before adding any new schema.

## Existing schema authority

`Shared/quality/qrt-pipeline-run.schema.json` blob:

`a4c25153ca5fa53a67b17565b15076215ebd7c9a`

### Review basis already typed

`semanticReview.basis` already permits exactly:

- `AUTHOR_ONLY`
- `RENDERED`
- `INDEPENDENT_RENDERED`

Semantics are explicit:
- `AUTHOR_ONLY`: retained author assessment; no rendered acceptance credit.
- `RENDERED`: exact-artifact review; independence unspecified.
- `INDEPENDENT_RENDERED`: exact-artifact review plus declared independently governed reviewer reference.

### Conditional schema requirements already exist

For non-`AUTHOR_ONLY` review, schema requires:
- `artifact_ref`
- `artifact_sha256`
- all twelve H1–H3 / S1–S3 / P1–P3 / M1–M3 judgements.

For `INDEPENDENT_RENDERED`, schema additionally requires:
- `reviewer_ref`.

Run-level opt-in requirement already exists:

`review_requirements.independent_rendered_review_required: boolean`

Its schema description states that, when true, every question needs an `INDEPENDENT_RENDERED` review; absent/false retains legacy rendered-review semantics.

## Existing consumer authority

`Shared/tools/qrt_pipeline_guard.py` blob:

`a3cac884b1380180e403a1ceeea93143e56c0fa1`

### AUTHOR_ONLY cannot satisfy rendered review

The guard skips `AUTHOR_ONLY` when building post-render review coverage.

A question with only author review therefore receives:

`POST_RENDER_QRT_REVIEW_MISSING:<question>`

### RENDERED cannot satisfy opt-in independent acceptance

When:

`review_requirements.independent_rendered_review_required == true`

the guard separately requires every question to appear in the set of `INDEPENDENT_RENDERED` reviews.

A self/ordinary `RENDERED` review therefore receives:

`INDEPENDENT_RENDERED_QRT_REVIEW_MISSING:<question>`

even if a `reviewer_ref` string is present.

### Current file bytes are checked

For every declared rendered artifact, the guard:
- verifies the file exists and is non-empty;
- recomputes SHA-256 from the current file;
- compares it to `renderedArtifact.sha256`;
- emits `RENDERED_ARTIFACT_DIGEST_MISMATCH:<artifact>` on drift;
- compares `renderedArtifact.head_sha` with `run_identity.head_sha`;
- emits `RENDERED_ARTIFACT_HEAD_MISMATCH:<artifact>` on head drift.

### Review binding is checked separately

For non-author reviews, the guard also requires:

`review.artifact_sha256 == renderedArtifact.sha256`

and emits:

`REVIEW_NOT_BOUND_TO_RENDERED_BYTES:<question>:<artifact>`

when the review still points at different bytes.

Therefore changed rendered bytes cannot silently retain the old review binding unless the review record itself is deliberately rewritten to claim the new digest.

## Existing regression tests

The strongest current acceptance tests are in:

`tests/test_staged_support_repair.py` blob
`3cba4ba361228eb7625b353a767c369c956baa74`

They explicitly test:

1. `test_author_only_record_is_retained_but_does_not_satisfy_rendered_review`
2. `test_legacy_rendered_reviews_keep_existing_binding_and_verdict_behavior`
3. `test_independent_rendered_review_requires_declared_reviewer`
4. `test_rendered_self_review_does_not_satisfy_opt_in_independent_requirement`
5. `test_independent_rendered_review_satisfies_opt_in_requirement_and_keeps_byte_binding`

Those tests directly exercise the U03 acceptance semantics.

## Exact-head workflow evidence

At head `d09d6d48b867fbed7d901fcd5afee334cbf60bc6`:

### Dedicated QRT hardening

Workflow run `37429243464` — `qrt-pipeline-hardening`:
- conclusion: **SUCCESS**
- job `112155958589` / `focused-regressions`: **SUCCESS**
- focused QRT regression step: **32 tests, OK**
- interactive Chromium smoke step: **SUCCESS**

However, that workflow currently runs:
- `tests.test_authoring_intake`
- `tests.test_qrt_pipeline_guard`
- `tests.test_qrt_content_self_audit`

It does **not** execute `tests.test_staged_support_repair`, where the direct review-basis/byte-binding acceptance tests live.

### Broader learner-platform code test

Workflow run `37429243471` — `learner-platform-code-tests`:
- workflow conclusion: **SUCCESS** because the broad Python step is explicitly informational / continue-on-error;
- raw Python suite result: **186 tests; 7 failures, 1 error, 1 skip**;
- therefore this broad job cannot be used as clean U03 acceptance evidence merely because the job-level conclusion is green.

No claim is made that the repository-wide Python suite is green.

## Contract gap classification

### Schema/consumer behavior

**REUSE EXISTING — sufficient for the declared U03 behavioral acceptance.**

No new `review_basis`, independent-review flag, artifact-SHA field, or parallel review record is justified.

### Focused evidence placement

**TRUE TEST-EVIDENCE GAP.**

The direct U03 acceptance regressions exist, but they are located in a staged-support repair test module rather than the dedicated QRT guard suite/workflow.

This makes the semantics harder to verify independently and lets unrelated broad-suite failures obscure whether the review-binding contract itself is green.

### Dependency identity beyond rendered bytes

Current canonical `renderedArtifact` requires only:
- id;
- path;
- sha256;
- head_sha.

The guard accepts an optional `artifact.blueprint_ref` if present and validates it against the active registry, but the rendered-artifact schema does not currently require blueprint/schema/asset dependency hashes.

U03A does **not** conclude that such additional dependency fields are necessary:
- `head_sha` already prevents reuse across a different declared repository head;
- rendered-byte SHA invalidates changed output bytes;
- relevant external dependency drift needs a concrete failing fixture before permanent schema expansion.

Therefore dependency-fingerprint expansion remains **DEFERRED**, not silently equated with byte binding.

## U03A result

**U03A COMPLETE. No production schema/guard change.**

The next bounded task is **U03B**:

- add the existing review-provenance/byte-binding acceptance cases to the dedicated `tests/test_qrt_pipeline_guard.py` surface;
- do not change behavior;
- use exact-head `qrt-pipeline-hardening` success as focused execution evidence.

U03 parent remains incomplete until that focused acceptance evidence is green.

Parent denominator remains:
- **P = 2/10 = 20%**
- **E = 2/10 = 20%**
