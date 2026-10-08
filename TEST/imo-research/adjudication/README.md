# SOF IMO Grade 9 — source-versus-compilation discrepancy register

**Research evidence / no learner admission.** The original owner attachment `IMO_Class9_Past_Papers_Topicwise.md` and all 66 original research seed IDs remain unchanged. The B01–B04 full-paper AI-worked census is 58/58 original *attachment-selected* full-paper positions, not the total content of three 50-question examinations. Official sample Q1/Q3 were added separately to the source census.

This directory is a **reviewer-facing custody and adjudication overlay**, not a file of altered question stems or a rewrite of any earlier answer. Its records cite the particular PDF page, original printed question number and prior audit evidence. The official 2026–27 sample PDF is [organizer-hosted](https://sofworld.org/download/file/fid/73719); full-paper PDFs are **school mirrors**, not an official answer-key receipt or question text reuse permission.

## What is currently documented

| Owner compilation entry | Source paper, printed question | Type of difference | Source-grounded research finding |
|---|---|---|---|
| Q46 | 2023–24 A Q13 | Wrong mathematical choice | Sort the predecessor digits: the fourth is **5, printed B**, not 4/C. |
| Q31 | 2023–24 A Q17 | Altered distractor | Source option A contains a radical ratio; attachment's A is 1:1. Correct computed volume ratio stays 4:9 (C). |
| Q1 | 2023–24 A Q18 | Correct option reordered | Numerically −5/12, but **source C**, attachment **A**. |
| Q37 | 2024–25 B Q16 | Original figure dependency | Printed pie chart supports English count 60 (A); attachment supplies reconstructed percentages, not licensed source figure. |
| Q9 | 2024–25 B Q44 | Wrong exam-section tag | Printed **Everyday Mathematics**, not Achievers; this source locator was already corrected in seed/taxonomy, distinct from the algebra topic. |
| Q2 | 2025–26 A Q28 | Changed stem semantics | Source says **additive identity**, literal answer 0 (B); attachment says **inverse**, leading to −32/75 (C). We cannot pronounce the source a typo without external authority. |
| Q22 | 2025–26 A Q31 | Diagram-dependent wrong answer | Source angles give **a=84°, b=21°, c=48° (C)**; owner gives (57°,21°,48°) (D). Source rays/labels require independent geometry sign-off. |
| Q38 (i) and (ii) | 2025–26 A Q32, Q33 | One owner item maps to two printed positions | Retain two source IDs sharing one chart; both computed printed options B. |
| Q23 | Official sample Q5 | Printed key without validated geometric derivation | SOF sample key **C** sighted; *agent derivation, QRT and academic approval held*. |
| Q6 | Official sample Q9 | Original complex notation rewritten | Printed fifth roots / powers yield Statement II **3/80** and choice D; compilation changes the expression and references 0.03, which is not equivalent. |

This makes **10 discrepancy/custody cases relating to 11 unique source-question positions**. Some are fully established *source-format observations*, others are open *mathematical or figure/transcription adjudications*. It would be wrong to report all 10 as confirmed incorrect answers.

### Authority is separated

- `source_finding_status` concerns what a visually inspected source PDF prints and how it differs from the owner's file. A section/locator can be corrected without accepting the academic mathematics or guaranteeing a full original verbatim transcription.
- `agent_mathematical_result` is an AI worked calculation, not a separate qualified academic peer review. The official sample's printed key is specifically marked `organizer_sample_key_sighted`; these key sightings are not independent mathematical proofs.
- `verbatim_source_publication_rights_status` and `figure_reuse_rights_status` remain `NOT_REVIEWED`. The registry contains researcher-generated comparison summaries, **not** source question stems, complete choices, original scans or diagram bytes.
- `accepted_qrt_cell` is `null` for each case; Core eligibility `false` everywhere. The 4×7 matrix remains **0/28 independently accepted**, regardless of provisional cognitive-demand classifications.

### Required decisions before a learner-facing bank

1. **Source-fidelity gate:** a reviewer checks printed Q13/Q17/Q18, Q28/Q31, official sample Q5/Q9 and the chart positions against their source scan. Preserve original compilation error history; produce separate versioned source-aligned representations only after the scan is independently transcribed and licensed.
2. **Mathematical academic gate:** qualified independent reviewer signs a separate answer/derivation record for each item. In particular, confirm 2025 Q31 ray/angle positioning, source sample Q5 parallel-line diagram, and the precise radical/exponent notation of sample Q9. No bulk inferred acceptance from matching the author's answer label.
3. **Legal / asset gate:** obtain permissions or license terms for question/option/figure reuse and secure diagram assets, or author independent analogous instructional variants without claiming they are original SOF exam questions.
4. **Governed QRT and Core intake gate:** after individual source and academic reviews, propose a primary demand + derived difficulty with question-specific evidence, then seek explicit academic/product acceptance. Never route SOF-origin material into the NCERT-only #68 intake merely by changing a source label.

### Validation

```sh
python TEST/imo-research/validate_discrepancy_register.py
python -m unittest discover -s tests -p 'test_imo_discrepancy_register.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The validator checks exact 10-case/11-question census, source PDF/landing URL distinctions, matching original compilation entries, existing B01/B02 and official sample mathematical evidence, analytic arithmetic invariants, source option/stem differences and fail-closed no-rights/no-peer/no-QRT/no-Core claims. A passing check **only qualifies research metadata integrity**, not independent academic or source-license acceptance.

Reference responsibility: [GitHub issue #250](https://github.com/reallaksh19/Grade9v3.5/issues/250).
