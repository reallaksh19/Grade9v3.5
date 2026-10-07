# QRT PR #3 Mathematics pilot

This is a **pilot overlay**, not a mutation of PR #3's question-bank custody records.

## Basis

- Source PR: #3 at `fceb5df4747b7f6ecb6d09c88bf3bdbbdb2b284a`.
- Source package: `Mathematics/library/polynomials.v1.json`.
- Render inspected: `public/mathematics/polynomials/core2.html`.
- The render is produced by `render_core`, exposes question anchors, and declares `BP-CORE2-SOURCE-QUESTION@1.0.0`.
- The active Blueprint 1.9 Core2 ref in the repository is `BP-CORE2-SOURCE-QUESTION@1.5.0`; therefore this pilot is **provisional evidence**, not acceptance evidence.

The coordinate-geometry path is not used for rendered review because its current PR #3 HTML has no Blueprint ref, no Core2 role marker, no `render_core` stamp and no source-question anchors.

## Five matrix cells exercised

| Source question | Pilot classification | Why |
|---|---|---|
| `Q-MAT-POLY-M1-P39-CHECK-POINT-1-1` | `QRT-RETRIEVE-D1` | retrieve the defining term-count classification criterion |
| `Q-MAT-POLY-M1-P39-CHECK-POINT-1-5` | `QRT-APPLY-D2` | execute the named remainder theorem correctly |
| `Q-MAT-POLY-M2-P01-ASSESSMENT-CORNER-SINGLE-CORRECT-TYPE-QUESTIONS-2` | `QRT-MODEL-D2` | choose the repeated-expression model before routine factorisation |
| `Q-MAT-POLY-M2-P06-HIGHER-ORDER-THINKING-SKILLS-HOTS-16` | `QRT-SYNTHESIZE-D3` | coordinate two remainder evaluations through one shared condition |
| `Q-MAT-POLY-M1-P44-CHECK-POINT-2-10` | `QRT-JUSTIFY-D3` | choose and apply a valid identity to establish the claim |

The pilot difficulty vectors are deliberately stored only in the fixture. PR #3's polynomial source records do not currently carry the full five-component difficulty object required by the QRT resolver.

## Render-level review result

All five inspected question articles have:
- one attempt box;
- solution disclosure behind the attempt;
- no hint ladder or rungs;
- no figure;
- no concept link;
- no `Why valid` support;
- no independent-check block.

For these symbolic algebra items the absence of a figure is treated as correctly not applicable rather than a defect. The common semantic review therefore records:
- H1/H2/H3: **NO** — no ladder exists;
- S1/S2/S3: **YES, correctly not applicable** — no useful figure is required for the selected symbolic items;
- P1: **YES** — solution remains behind the attempt boundary;
- P2/P3: **NO** — no concept repair link, per-move validity explanation or independent check;
- M1/M2/M3: **NO** — no misconception diagnosis/detection/repair support.

This is precisely the distinction the matrix is intended to add: the page can have a valid attempt boundary while still lacking demand-specific semantic support.

## What remains before canonical pilot acceptance

1. Normalize the PR #3 polynomial render to the active Core2 Blueprint 1.9 ref.
2. Normalize coordinate geometry onto the same renderer/Blueprint path.
3. Author canonical demand classification and full five-axis difficulty metadata only after review; do not copy the pilot overlay into source records automatically.
4. Re-run the resolver/review against the normalized exact render and bind the resulting product-review findings to its digest.

