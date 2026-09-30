# Validation of schema/blueprint post-mortem feedback

## Basis and conclusion

Reviewed 2026-09-29 against #353 correction head `fe889b9fccc0c5665271b388a180b3d18ba5f67d`, current main `e1bfe7a0e45c9a59cde33459d1d6f6bc8febe390`, and read-only local material in `C:/CodeA/G9_I329` at `753a7b08f3946d1c5ad5a5612829f099922929a9` plus its untracked files. The local coordinate bank and scratch generators are untracked; their bytes are not established by that commit. Historical versions of those outputs and the original m2 PDF were not re-read in this review, so no exact historical failure chain is claimed.

Inspected coordinate-bank file SHA-256: `ffe62098a55be6c58f14c65a17ac8a8f8e24fa3ad0a19592b0730fdbd581af49`. This identifies the current reproduction input without promoting local topic content into this PR.

The useful diagnosis is incomplete integration between canonical source/teaching data, the declared blueprint, the actual output producer and learner-artifact review. The proposed universal count/keyword/layout gates are not a sound remedy and conflict with the Owner's method direction. #353 is the scoped first-stage/NLM implementation; the local coordinate-bank work is not in its diff. #356's fixed-card interaction witness is a separate reviewed implementation.

## Claim-by-claim findings

| Feedback | Verdict | Evidence / correction |
|---|---|---|
| Core2 source blocks differ from Core2A/B teaching blocks | Confirmed; intentional distinction | `Shared/roles/CORE2.md` preserves source hints where supplied. Core2 still provides a typed attempt and protected answer/working. It is not merely a passive transcript. Source absence does not forbid separately identified authored help. |
| The bank has no reasoning-route expectations | Incorrect as a general claim | `Shared/tools/competitive_exam_bank.py` checks a nonempty reasoning route, resolvable crux and independent verification. Schema validation, this semantic checker, rendering and instructional review are different observations. |
| The cited data passed the named schema with zero errors | Not reproduced | The current local coordinate-bank object contains only `questions`. Direct Draft202012 validation against `competitive-exam-bank.schema.json` yields **2,131 errors**, including missing bank metadata and record requirements. Both cited records now have three hints and structured routes. Neither the historical bytes nor a zero-error command/log were supplied. A different sparse-bank consumer may have accepted it; that does not prove compliance with this schema. |
| `hints: null` is schema-valid | Incorrect for the base question schema | `package.schema.json` defines `hints` as an array; an empty array is permitted, null is not. Source hints and authored support are distinct. The specialized competitive-bank checker additionally flags nonempty source hints under its pass-one policy. Do not impose that specialized policy indiscriminately on all source banks. |
| `_ladder(...source=True)` silently emits nothing for absent hints | Confirmed behavior; not automatically a defect | There may genuinely be no source hint. The real missing projection is separately labelled authored Core2 support, where requested; structured `answer.reasoning_route` is also not projected by Core2, which reads flat `answer.reasoning`. Missing source material, unprovided authored help and not-applicable support must not be conflated. |
| No figure completeness contract exists | Incorrect; integration concern remains | `source-question-custody.schema.json` already records figures/captions as PRESERVED, NOT_PRESENT_IN_SOURCE, EXTERNAL_REFERENCE_VERIFIED or UNRESOLVED. `Shared/library/source_custody.py` reports a claimed source figure with empty refs. The current sparse records do not demonstrate that custody path was exercised. |
| Both cited empty `figure_refs` arrays prove missing required diagrams | Only partly supported | LA-04 says “In the figure given below” while its current refs are empty: a concrete missing-source-component concern. COMP-01 asks the learner to plot coordinates: a completed diagram may be the learner's work/answer. A blank grid and post-attempt solution figure serve different purposes. Original source pages still need readback. |
| Figure keywords should require an SVG | Reject | Keywords can surface advisory questions, not establish source presence or disclosure timing. “Pentagon” can occur in an option; automatically drawing it can reveal the answer. Images, accessible diagrams and learner drawing space are not interchangeable SVG counts. |
| D2/D3/D4 must have exactly/minimally three hints | Reject | Difficulty should inform support quality and review priority, not a numerical quota. Existing Core2A depth expectations do not justify copying a quota into source custody. A shorter purposeful ladder can be better than padded or leaking rungs. |
| No viewport/device contract or layout observations exist | Incorrect | Existing tablet spec, 12.7-inch CSS, blueprint 48px touch policy, renderer responsive grid and `tools/site-audit/tablet-audit.mjs` cover tablet dimensions/overflow. Actual coverage of a particular generated file must still be established. The historical tablet spec has older gate-oriented language; it does not override current Owner publication/no-gate directions. |
| Every question requires a 1.4:1 diagram grid | Reject as universal | Width, text, figure necessity and portrait reflow determine layout. An absent/unnecessary figure should not create an empty column. Existing content/support grids differ from content/diagram grids. |
| CDN dependency can break offline mathematics | Valid risk; stated cause overgeneralized | Existing vendor policy and tests already require local dependencies. The current local custom coordinate HTML references local KaTeX files. Earlier CDN failure is not established by those current bytes. `file://` does not invariably block external scripts: cross-origin embedding is generally allowed, while fetch/modules/fonts have distinct restrictions. See [MDN same-origin policy](https://developer.mozilla.org/en-US/docs/Web/Security/Defenses/Same-origin_policy). |
| `.katex` count proves math correctness | Insufficient | The sole renderer uses native MathML for relations. Its `para()` escapes question text; `grade9v3:math_spans` is not consumed there even though the blueprint declares typed question math. Reproduction: `para('Given $x^2 + y^2 = 1$')` leaves delimiters literal. Inspect intended formulas, errors, revealed content and print output, not merely library-specific element counts. |
| Assessment and laboratory explorers were conflated | Valid design concern; architecture already distinguishes them | Existing Core jobs and EXPLORE experience mode should guide use. #356's four-card witness does not realize its coordinate-dragging brief. Local scratch HTML generators also exist outside the sole renderer. No new universal widget schema is needed to express purpose, identity and disclosure. |

## Shared blueprint changes incorporated

`docs/method/FIRST-STAGE-REVIEW.md` now explicitly distinguishes:

1. source material, authored teaching and independent verification;
2. supplied figures, learner constructions and post-attempt explanatory figures;
3. assessment interactions and concept explorers;
4. difficulty-informed judgement from quotas;
5. existing tablet/offline/math contracts from proof that a particular output follows them.

These are advisory design/review requirements. No machine schema, renderer, academic content, CI workflow or acceptance authority changes in this documentation slice.

## Remaining shared implementation work, not claimed complete

- Reconcile the owning provenance fields for optional authored Core2 help and project that help/structured reasoning through the sole renderer with correct disclosure. Do not put invented teaching into source `hints[]`.
- Connect source-component completeness to the review packet; distinguish missing references from source absence. Resolve the existing source-resource/representation mounting distinction rather than introducing another media authority.
- Project existing typed question-math metadata consistently in HTML, inserted template bodies and PDF using local dependencies or the declared native representation.
- Exercise actual generated packets in both tablet orientations and their promised offline mode. Reports remain advisory; exact-render Owner acceptance remains the publication decision.
- Preserve the actual producing command, input/schema identities, code head, output hashes and rendered evidence. A green workflow, schema-valid record or zero renderer-depth gaps alone is not a golden-quality result.

## Validation truth

- Repository/schema/source inspection and the two direct reproductions above: RUN.
- Relative documentation links and `git diff --check`: PASS. This documentation-only correction leaves executable code identical to `fe889b9f`; no new full-suite execution is claimed.
- Original m2 PDF readback and historical failed-output reconstruction: NOT_RUN; historical claims remain qualified.
- New Chromium/PDF run for this documentation slice: NOT_RUN. Previous #353 observations remain bound to their prior code/render basis.
- No new CI run or gate. No library content or local untracked producer files edited.
