# ISS66 U03 — review provenance and exact-artifact acceptance

**Status:** COMPLETE + EVIDENCED  
**Candidate code head:** `75ba8a45a009a0205d1d65363301ed6538e9d014`  
**PR:** #67

## Problem reproduced

The merged QRT contract already separated:
- `AUTHOR_ONLY`: authored assessment, no post-render acceptance credit;
- `RENDERED`: review bound to exact rendered artifact bytes.

However, `RENDERED` carried no reviewer-independence information. A rendered self-review and an independent exact-render review were structurally identical, so a consumer could not request independent review without inventing an external convention.

## Change

### Semantic review basis

`Shared/quality/qrt-pipeline-run.schema.json` now accepts:

- `AUTHOR_ONLY`
- `RENDERED`
- `INDEPENDENT_RENDERED`

Compatibility semantics:

- missing `basis` retains legacy rendered behavior;
- `RENDERED` continues to mean exact-artifact review with independence unspecified;
- `INDEPENDENT_RENDERED` requires `reviewer_ref` and declares an independently governed reviewer identity/reference.

`reviewer_ref` records provenance only. The schema does **not** claim it can prove social/organizational independence.

### Opt-in acceptance requirement

A new optional run-level object is available:

```json
{
  "review_requirements": {
    "independent_rendered_review_required": true
  }
}
```

Absent/false preserves existing post-render acceptance semantics. This deliberately avoids installing a new universal publication gate.

### Guard behavior

`qrt_pipeline_guard.validate_artifacts_and_reviews()` now:

1. retains `AUTHOR_ONLY` without post-render credit;
2. accepts `RENDERED` and `INDEPENDENT_RENDERED` as rendered reviews;
3. retains the existing artifact file, digest, head and review-to-artifact SHA checks;
4. requires a non-empty `reviewer_ref` for an independent rendered review;
5. when the run opts into independent review, requires every question to have an `INDEPENDENT_RENDERED` review.

A rendered self-review still counts as rendered evidence, but does not satisfy the stronger opt-in independent requirement.

## Regression evidence

Added to `tests/test_staged_support_repair.py`:

1. `INDEPENDENT_RENDERED` is schema-invalid without `reviewer_ref`, valid with one.
2. A `RENDERED` self-review remains a valid ordinary post-render review but produces:
   `INDEPENDENT_RENDERED_QRT_REVIEW_MISSING: Q`
   when the run explicitly requires independent rendered review.
3. An `INDEPENDENT_RENDERED` review with reviewer identity satisfies the opt-in requirement.
4. Independent status does not weaken byte binding: changing `artifact_sha256` still yields `REVIEW_NOT_BOUND_TO_RENDERED_BYTES`.
5. Existing legacy rendered-review test remains unchanged and passing.

## Hosted exact-head validation

At code head `75ba8a45a009a0205d1d65363301ed6538e9d014`:

### qrt-pipeline-hardening — run 37420573268
Job `focused-regressions` **SUCCESS**:
- Intake policy: SUCCESS
- Focused QRT hardening regressions: SUCCESS
- Chromium audit script syntax: SUCCESS
- mandatory interactive Chromium smoke audit: SUCCESS

### learner-platform-code-tests — run 37420573263
- `code-tests`: **SUCCESS**
- informational platform code tests: SUCCESS
- existing blueprint layout observation regressions: SUCCESS
- `blueprint-v2-render-snapshots`: **SUCCESS**

The separate Core2-v2 browser lane is not U03 acceptance evidence and retains the inherited render-gap behavior already documented in U02.

## Acceptance

- author-only review cannot satisfy rendered review: **retained**
- rendered review remains bound to exact bytes/head: **retained**
- rendered self-review can be distinguished from independent rendered review: **YES**
- independent-review acceptance can be explicitly required: **YES**
- legacy rendered records remain valid: **YES**
- new universal gate added: **NO**

Next: **U04 — difficulty/QRT derivation**.
