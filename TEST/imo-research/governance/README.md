# SOF IMO Grade 9 — owner-directed review policy and complete provisional official-sample QRT

**Owner policy effective 8 October 2026:** the user explicitly marked **independent human academic approval "Not applicable"**. It is therefore **not a prerequisite** for this SOF IMO Grade 9 research workflow. No previous expert review is claimed; the earlier source discrepancy and independent-review queue are historically accurate records of what had *not* been done when they were written. The new policy supersedes the demand for future human academic signatures, **without fabricating receipts** or silently rewriting that research history.

The [owner policy record](../governance/owner-independent-academic-review-waiver.v1.json) retains required source identity, original printed key sighting, mathematical derivation, independent analytic crosscheck and figure/notation dependency. It does **not** waive copyrighted SOF exam text/option/diagram reproduction permissions, material original-source transcription conflicts, official full-paper answer-key custody, or the separate QRT/Core product admission process.

## Ten-source sample census and 4×7 research proposals

The controlling artifact is the [SOF-hosted 2026–27 Grade 9 two-page sample PDF](https://sofworld.org/download/file/fid/73719), with ten printed source question positions and an organizer answer-key panel. Of these, eight were included in the owner's original 66-position compilation; two additional logical reasoning items, **Q1 and Q3**, were independently identified from the sample and have separate research source records. This does not expand the 66 original owner attachment records or change the 58/58 agent-worked full-paper subset census.

Seven sample questions already had individually justified QRT proposals in `official-sample-2026-27-math-qrt-pilot.v1.json`. The new `official-sample-2026-27-new-qrt-proposals.v1.json` adds three source-grounded rows:

| Source Q | Primary demand | Five scores (model / translate / chain / compute / trap) | Total | Band | Provisional cell |
|---|---|---|---:|---|---|
| Q1 — dice face/orientation | REPRESENT | 1 / 2 / 2 / 0 / 1 | 6 | D3 | QRT-REPRESENT-D3 |
| Q3 — radial numeric pattern | MODEL | 1 / 1 / 2 / 1 / 0 | 5 | D2 | QRT-MODEL-D2 |
| Q5 — parallel-line angle relation | JUSTIFY | 1 / 2 / 2 / 0 / 1 | 6 | D3 | QRT-JUSTIFY-D3 |

- **Q1:** reconstruct face-opposition and oriented rotations from multiple cube views; infer missing face 4, sample key B. Source figure needs custody and reuse permission.
- **Q3:** infer the squared-mean relation from three independent quadrants before obtaining 49, key B. A matching pattern across the given entries is research evidence, not a claim of uniqueness among every imaginable rule.
- **Q5:** the separate source figure agent proof uses `x+2y=180°` from corresponding parallel angles plus the printed two y sectors, hence `y=90°−x/2`, key C. The former sample pilot's figure hold and P0 reviewer status remain historical snapshots. Under the **new owner policy**, however, a human peer signature is **not required** for research mathematical QA. Source-figure fidelity, publisher rights and actual QRT product admission remain distinct.

**Result: 10/10 source sample positions have provisional, model-scored QRT classifications spanning seven unique cells of the 28-cell historical matrix.** Seven unique proposed cells do **not** mean seven filled or academically accepted cells. The original sample Q9 owner-stem radical/index rewrite remains a material source discrepancy and publication hold even though it has a research cognitive-demand classification.

## Separate gates unaffected

- **Research mathematical evidence:** seven older sample proposals plus three new source-derived calculations/figures; all original source IDs and printed keys are crosschecked. This policy authorizes research reliance on agent calculations with deterministic/falsifiable supporting evidence rather than a required external human signature.
- **Source fidelity:** source Q9 complex root notation remains disputed; original figures and full transcription are not automatically normalized or cleared.
- **Original question/figure rights:** no SOF paper text, complete answer choices or original image is copied in these overlays. Publicly accessible organizer or school-hosted PDFs do not alone authorize publication in this project.
- **QRT and Core decisions:** each proposal is marked `PROPOSED_NOT_ACCEPTED`; the established research register still shows **0 accepted QRT cells (0/28)** and **0 Core-ready questions**. Explicit governance admission remains necessary; no downstream learner production is changed.
- **Historical audit accuracy:** old records with `PENDING` describe a previous state and may be interpreted against the newer dated owner policy; they are not evidence that humans reviewed these items or that approval remains mandatory.

## Deterministic test

```sh
python TEST/imo-research/validate_owner_sample_qrt.py
python -m unittest discover -s tests -p 'test_imo_owner_sample_qrt.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The validator checks the earlier mathematics/sample source overlays, the newly merged Q5 vector/angle proof, original organizer keys, seven old plus three new proposal identities and unique-cell census, five-factor scoring bands, the explicit owner N/A policy, source/radical/figure custody, and no QRT/Core/rights acceptance. Eighteen added adversarial tests reject source mutation, false math factors, fake expert approval, rights claims, overwritten Q9/Q5 history and unearned product readiness.

**This is a governance and research-proposal completion milestone, not a publisher license or learner-facing question bank.** Source rights and any eventual product-level QRT/Core admission should be handled as separately evidenced decisions.

Issue: [#264](https://github.com/reallaksh19/Grade9v3.5/issues/264). Related original sample proof: [#258](https://github.com/reallaksh19/Grade9v3.5/issues/258).
