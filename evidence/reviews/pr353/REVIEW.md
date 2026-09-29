# Issue #352 / PR #353 corrective review

Date: 2026-09-29. Original PR head: `739150d86995065efb0219ecd32b5ccffb464d99`.
Base examined: `d60a939e473817bc55504987840bd30c4e2162d1`.
Common V3.1 basis: `1ced68258afeaf50df113b1d38a4ceb9193587e3`.
The commit containing this evidence supplies the corrected code basis. The PR and issue update name its exact hash.

## Concept and workflow

The method preserves source-dependent entry: Core2 for a usable bank, otherwise source-grounded Core1. Difficulty-first scheduling operates inside that route; it does not change source order, learner navigation or the full denominator view. Research, solving and sketches across Cores remain open. Scheduling labels and interaction-value rationale remain in authoring documents. Existing canonical records, the sole renderer and Owner exact-render acceptance remain authoritative.

The one-concept NLM pilot demonstrates the Core1 route. It does not prove a multi-question Core2 denominator reconciliation, golden instructional quality, all-six-Core readiness or Owner acceptance. The existing golden Core2 scope regressions exercise the other route without inventing a source bank for this pilot.

## Findings and corrections

| Finding reproduced on the original head | Correction | Evidence |
|---|---|---|
| Rendering all six roles then Core1 into the same directory leaves excluded HTML; receipt verification fails and print glob picks up obsolete Cores | Retire only allowlisted, prior-receipt-owned HTML outside the new scope; invalidate co-located derived learner/key PDFs and print receipts; preserve unrelated files | Repeat-render regression checks all-six → Core1 → SINGLE_FILE → PAGES and receipt verification |
| Core2A repair and Core2B lineage links point to omitted Core1A/Core2A pages; SINGLE_FILE has missing fragment targets | Resolve links using both role scope and selected record IDs; retain useful text when a target is absent | PAGES/SINGLE_FILE link-target regressions for Core2A, Core2B and a combined scope |
| Explicit `output_roles: null` silently expands to all six | Only an absent field invokes the legacy default | Null, wrong-type, empty, duplicate and unknown-role cases |
| Pilot PDF begins with a title-only page; compact-anchor heading is separated from its example | Allow long articles to paginate; keep headings with following content; reduce print footer spacing | Actual Chromium PDF, extracted text regression, visual inspection of every corrected page |
| PR adds CI dependency installation despite Owner's no-CI direction | Restore the workflow to the exact base version | No workflow delta against base; no Actions dispatched |

The structural scope checks do not assess content quality, restrict research or introduce a publication decision.

## Validation and precise limits

Reviewed artifacts: [Core1 HTML](packet/core1.html), [learner PDF](packet/core1.pdf), [render receipt](packet/render-receipt.json), [print receipt](packet/print-receipt.json), [quality findings](packet/gate-report.json), [tablet measurements](browser-observation.json). These are frozen evidence copies, not another authoring authority or a publication. Site-wide navigation assumes the ordinary deployed site and is not supplied by this evidence folder.

- Focused suite: **PASS**, 55 tests, no skips. Command: `python -m unittest tests.test_publication tests.test_render_core tests.test_renderer_inventory tests.test_quality_contract`.
- Original-head full discovery: **FAIL**, 1,521 tests, 28 failure occurrences, 17 errors, 4 skips, 486.403 seconds.
- Exact-main replay of all failing test identifiers: **FAIL**, 33 tests, the same 28 failure occurrences and 17 errors. Subtests account for counts exceeding test count. This is a targeted comparison, not a full-suite PASS on main.
- Corrected full discovery: **FAIL**, 1,523 tests, 28 failure occurrences, 17 errors, 4 skips, 522.962 seconds. No new or resolved failure/error occurrences versus the original head. See `validation.json` and `corrected-full-suite.txt` for exact identifiers and tracebacks.
- Chromium/PDF: **PASS for the exercised scoped pipeline and pagination checks**. Rebuilt with `python Shared/tools/build_products.py build --only phy-nlm-momentum-transfer`. Three PDF pages inspected visually; page one contains the concept body and governing relation; page three contains the compact-anchor heading, example and footer. No title-only or footer-only page remains in this pilot.
- Tablet browser observations: 1280×800 and 800×1280; document width equals viewport width; only Core1 appears in Core navigation; no LP-H1/interaction-value labels in visible text; zero figures. These observations do not certify every interaction across six Cores.
- Quality observation: **FAIL**, with `C1-REPRESENTATION` and `PRODUCT-ALL-ROLES` retained. `rendered_measured=true`, `not_measured=[]`. No decorative figure or extra Core was generated to hide these findings.
- GitHub Actions: **NOT_RUN** for this correction. Historical CI results for the old head do not certify the corrected head.
- Product acceptance/publication: **NOT_RUN**. No public output was written by this correction.

The attached raw logs preserve exact failing IDs, subtests and tracebacks. Reproduced main failures include publication manifest/runtime mismatches, equation-source mismatches, representation/gate-registry inconsistencies, nested-ID collisions, corpus/explorer checks and generated-file/manifest drift. They are not attributed wholesale to missing dependencies. The failure-ID comparison in `validation.json` identifies any new occurrences.

## Merge plan

1. Review the correction commit and this evidence on #353; retain the recorded full-suite FAIL and open academic findings.
2. On Owner merge authorization, refresh base/head and conflict status. If the code basis changes, rerun the affected checks and full local suite before any further code push.
3. Merge #353 into main without adding or dispatching CI. No merge is performed by this review.
4. Review/accept a particular learner render separately through the existing Owner exact-digest publication path. A code merge neither resolves representation debt nor accepts a learner product.

## Step-back check

- SBC-1 Learner: scoped packets have working available links, no stale excluded Cores, and readable pilot pagination.
- SBC-2 No new gate: quality findings remain advisory; added CI setup was removed.
- SBC-3 Thinking: the route and denominator were reviewed against source state; no interaction or decorative figure was invented.
- SBC-4 One of everything: existing manifest, package, renderer, print path and Owner publication authority retained.
- SBC-5 Construction: scope-aware target resolution and receipt-owned cleanup prevent defects at rendering time.
- SBC-6 Coherence: shared scope guidance and this evidence explain superseded old-head claims; historical worklog entries remain historical.
- SBC-7 Honest state: focused/browser checks PASS, full suite FAIL, Actions NOT_RUN, academic debt explicit.
- SBC-8 Convergence/cost: targeted corrections prepared for the same PR; no spend estimate invented.
- SBC-9 Reusable: fixes apply to every subject and either first-stage route.

Acted on: corrected all reproduced scope defects and pagination; restored the existing CI configuration; preserved unresolved academic findings and exact validation evidence.
