# STEP-05 / WP5 tablet and M5 evidence

Basis: `main@7515c2e5898eeea86ae56b71cdfd8f8175b8ff67`, draft SPEC-AM2 #321 at `1e7cb10624bd4da972b51fea141fb4810f0f653b`, `research/physics-library@622c54d277250c0e125aa2d077e84995123d57b5`. The research branch is an ancestor of current `main` (`git merge-base --is-ancestor` returned 0). No branch commit was replayed or Owner history rewritten.

## D8 class-by-class reconciliation

| Approved class | Observation and action |
|---|---|
| Keep source work | All 7 scan files, 54 acquisitions, 31 card files, 3 allowlists and 5 M2 evidence/ledger files from the research branch are present on main. No Owner source file was discarded. |
| Absorb tablet CSS | `public/css/tablet-12-7.css` remains the Owner input. `Shared/tools/render_core.py` now defines the 1380 px content width, 48 px touch minimum, spacing/type tokens and responsive six-Core shell in its own `CSS`. The existing stylesheet remains linked for site-wide tablet surfaces. |
| Discard hand-edited product pages | No `public/products` or `docs/products` file is tracked at the current head, so there was nothing in this approved class to discard. Builds still cannot publish; Owner acceptance remains the only publication action. |
| Vendor CDN runtime | `build_pages_site.py` rewrites the pinned jsDelivr KaTeX URLs to checked-in vendor assets; 48 KaTeX files are tracked across public and docs. No new remote runtime was added. |
| Normalize line endings | No branch merge or broad line-ending rewrite was needed. The research branch is already contained in main; M4 files were moved with identical bytes, including historical CRLF where present. |
| Classify raw intake | `public/js/raw-intake.js` is already `OUT_OF_SCOPE` in `docs/plans/phase0/renderer-inventory.v1.json` as an Owner intake tool. |
| Regenerate composer data | `public/data/prompt-composer-data.js` and its Pages mirror were regenerated in WP4 and verified current. |

## M4 unpublished stress tests

All 19 tracked `docs/stress-tests/` files moved to `evidence/stress-tests/` as 100% Git renames. Their bytes did not change. The Pages generator leaves them unpublished and its internal-link check passes.
Three evidence test modules now read the moved paths; all 20 focused tests pass. The first full discovery exposed their stale paths as three new setup errors, which were corrected before the final full run.

## Direct tablet evidence

The sole renderer built both Physics pilot products in PAGES mode with zero render gaps: NLM digest `15499c9f7bbdd871`, Motion 2D digest `4c8f37c00ac83ba7`. Chromium then loaded every Core page under `tools/site-audit/core-page-audit.mjs --profile tablet-12.7` at 1366×854, 1440×900, 854×1366 and 900×1440. The JSON reports are [NLM](tablet-12-7/nlm-audit.json) and [Motion 2D](tablet-12-7/motion2d-audit.json).

| Pilot | Cores × profiles | Controls measured per profile | Controls below 48 px | Max horizontal overflow | Hover-only element handlers | External requests | Page errors |
|---|---:|---:|---:|---:|---:|---:|---:|
| NLM | 6 × 4 | 481 | 0 | 0 px | 0 | 0 | 0 |
| Motion 2D | 6 × 4 | 236 | 0 | 0 px | 0 | 0 | 0 |

The minimum computed font is 12.07 px on a MathML `mtext` subscript in Core1; ordinary page text is larger. This remains a measured visual detail for Owner review. Representative viewport captures: [NLM Core1A landscape](tablet-12-7/nlm-core1a-landscape.png), [Motion Core2 portrait](tablet-12-7/motion2d-core2-portrait.png). These are current-render screenshots, not the Owner reference.

The Owner's attached HTML layout reference is unavailable in this checkout and issue/PR text. Visual fidelity to that reference is **NOT_RUN**; no such claim is made. The source file or URL has been requested. The approved D8 research class audit is complete, while the old "suite green" criterion remains **FAIL** on the existing local suite baseline and the WP4 Mathematics candidate content findings.

The broader site navigation audit observes 80 findings across 41 current pages (40 `NO_SHELL`, 26 `NO_WAY_HOME`, 13 `ORPHAN`, one `SITE_MAP_MISSING`). Those are outside the two six-Core pilot render audits and remain open for a separate site repair task; this slice does not call the site audit a pass.
