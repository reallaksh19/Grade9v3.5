# SOF IMO Grade 9 — Core 1A TEST teaching preview (Issue #301)

**Preview status: STATIC TEST REVIEW ONLY · CANDIDATE · NO CANONICAL ACCEPTANCE.**

Review entrypoints **after this PR is qualified and merged**:
- Mathematics hub → [IMO Grade 9 by topic](../../../../docs/mathematics/imo-grade9/index.html) → *Study concept · TEST Core 1A candidate review*.
- Direct local mirror: `docs/test/imo-grade9/core1a.html`; canonical published learner Core1A is **not** changed.
- Authored academic draft source: `TEST/library/imo-g9-divisibility-core1a.v1.json` with pinned Git blob `cbcfe1ffe69b7453a53ca3608f5b563b0f91776e`.
- Exact test page bytes, public/docs page and Math-topic entrypoint blobs in `TEST/imo-research/intake/core1a-test-review-receipt.v1.json`.

## What can be reviewed now

A standalone, accessible-semantic HTML lesson page (built as a **static direct TEST review layout**, **not** passed through the canonical production compiler) that shows:

1. Entry assumptions: positive integers, even/odd, modulo three and coprime divisibility. Scope/conventions declared before mathematical steps.
2. Four complete candidate teaching moves: arbitrary `n`, one guaranteed factor of 2, exhaustive residues modulo 3 yielding a guaranteed factor of 3, and combining coprime factors into 6.
3. An actual semantic `<table>` from the candidate representation specification with rows `n mod 3 = 0,1,2`; the divisible factors are `n,n+2,n+1` respectively. Separate parity explanation prevents the misleading inference that 2 and 3 must occur in one factor.
4. Explicit false-path diagnosis: testing finitely many examples does not prove a universal claim; exhaustive remainder classes repair it.
5. An independent exit proving **four** consecutive integers yield a multiple of **24**. It has an optional unlabeled-by-grading local response textarea and a native `<details>` model closure, closed initially. Its answer is embedded in static HTML, **not securely hidden** and not a Core 2 pre-attempt answer; the page makes that boundary explicit.
6. Clear provenance and constraints: no copied official SOF questions/figures, no source Core 2 admission, no automatic grading or QRT product acceptance.

The page is mirrored byte-identically at `public/test/imo-grade9/core1a.html` and `docs/test/imo-grade9/core1a.html`, with a clear TEST review link under the existing rights-safe Mathematics topic browser.

## Actual testing and acceptance status

- Static semantic source and package-to-page content verification: **automated validator and adversarial tests submitted for exact-head CI** (not pre-claimed passed).
- Keyboard/manual tab order and native disclosure, high zoom/320px display, assistive-technology/screen-reader speaking mathematics, contrast in dark mode, live mobile browser, print/PDF layout: **NOT RUN**.
- Independent student comprehension, response correctness grading, curriculum endorsement, mathematical human product acceptance and learner/publication approval: **NOT RUN / NOT GRANTED**.
- The static TEST page is **publicly addressable once deployed**, not a private access-control boundary. It must not be marketed as canonical Core 1A or official SOF until the separate dated Owner gates.
- Actual browser/PDF inspection and canonical compiler/rendering parity remain following engineering units; no fake screenshot or rendered PDF is claimed.

## Core 2 source acquisition remains a separate gate

`TEST/imo-research/intake/core2-source-acquisition-handoff.v1.json` queues the four known PDFs without saying downloads succeeded:

| Research source | Question positions | Host role |
| --- | ---: | --- |
| 2023–24 full paper | 24 | School-hosted mirror |
| 2024–25 full paper | 12 | School-hosted mirror |
| 2025–26 full paper | 22 | School-hosted mirror |
| 2026–27 organizer sample | 10 | Organizer-hosted direct sample PDF |
| **Total** | **68** | Strict zero-Core2 admission |

Real `Shared/tools/source_pipeline.py acquire` requires retained bytes and returns the observed SHA256, resolved URL and byte count. `verify_acquisition` must independently verify the retained bytes; only then may acquisition be recorded. **Current queue contains no PDF bytes, hashes or acquisition receipts.** Separate item-component verification, printed key/math reconciliation, copyright/external-reference disposition and product acceptance are still required before source Core2.

## Reproduce CI checks

```sh
python TEST/imo-research/validate_core1a_test_review.py
python -m unittest discover -s tests -p 'test_imo_core1a_test_review.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

This PR qualifies **static candidate review material only**, not actual source-custody sufficiency or the canonical Core product.
