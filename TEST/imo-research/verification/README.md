# SOF IMO Grade 9 — official 2026–27 sample maths and provisional QRT research

**Scope:** eight questions from the Owner's compiled seed that also occur in the [organizer-hosted Class 9 sample PDF](https://sofworld.org/download/file/fid/73719). The actual sample has ten numbered questions: Q1 and Q3 are still missing from the seed. This is **not** a complete past-paper corpus or a learner question bank.

Source PDF: two pages, SOF-hosted; the printed answer key and section headings are visible. Organizer-hosted source identity, answer-key sighting, our mathematical recomputation, a peer's academic verification, copyright permission and Core admission are **separate evidence statuses**.

## Deliverables

- `official-sample-2026-27-math-qrt-pilot.v1.json`: one research-only evidence record per sample source ID (original page, source section, printed option, AI-derived answer, derivation, independent calculation check, discrepancy, evidence statuses and provisional QRT selection). It contains **no original question stems, option sets, images, or PDF bytes**.
- `qrt-proposed-coverage.v1.json`: the full canonical **4 difficulty bands × 7 cognitive demands = 28** matrix, distinguishing proposed and academically accepted question IDs in every cell.
- `../validate_sample_pilot.py`: fail-closed source/identity/answer/key/QRT-score/status validator, with an explicit Q5 hold, Q9 transcription conflict, zero accepted cells and no Core promotion.
- `../../../tests/test_imo_sample_pilot.py`: scoped positive and adversarial regression tests; focused GitHub Actions is `.github/workflows/imo-research-validation.yml`.

## Results — proposed, not independently accepted

| Sample number | Source section | Printed key | AI-worked result | Primary QRT proposal |
|---|---|---|---|---|
| Q2 | Logical Reasoning | B | B — cipher mapping | REPRESENT / D2 |
| Q4 | Mathematical Reasoning | B | B — table-to-equation | REPRESENT / D1 |
| Q5 | Mathematical Reasoning | C | **FIGURE HOLD** | None |
| Q6 | Mathematical Reasoning | C | C — equal segments added to equals | JUSTIFY / D1 |
| Q7 | Everyday Mathematics | D | D — factor/divisibility constraints | MODEL / D3 |
| Q8 | Everyday Mathematics | D | D — conical-tent area/volume model | MODEL / D2 |
| Q9 | Achievers | D | D — Statement I false; Statement II = 3/80 | JUSTIFY / D3 |
| Q10 | Achievers | A | A — disproving a congruence claim | JUSTIFY / D3 |

There are **7 agent-mathematically-checked** answers out of 8 sampled source positions, matching **7 printed SOF answer-key options**; the remaining source Q5 is held because its decisive diagram-based geometric construction has not yet been independently established. This is **not** seven independent human-academic reviews. Source Q6 and Q10 have inspected diagrams and worked rationale, but figure reuse rights are not established.

The most serious source problem is **Owner compilation entry Q6, SOF source Q9**: its Statement II radicals, fifth-root indices and powers are **materially different** from the printed PDF. The original PDF expression simplifies to **3/80** (the source key supports D), but the *compiled transcription is not fit for learner publication*. Treat the conflicting uploaded wording as source-text evidence, not as an authentic exam stem.

The 4×7 ledger has **6 distinct provisionally occupied cells, 22 with no proposal, and 0 independently accepted cells**. Q5 has no proposed primary cell at all. No row has a Core-ready status, and this work does not backfill the five missing official syllabus topics in the seed.

## Authority and unresolved gates

SOF organizer paper/source: https://sofworld.org/download/file/fid/73719.

Seven cognitive demand definitions and the 4×7 question-semantic selection policy are historically documented by [Grade9v3.5 issue #29](https://github.com/reallaksh19/Grade9v3.5/issues/29) referencing commit `8678645ef2fd5e63401ef5af3621b94e925732a8`:
`Shared/vocabularies/cognitive-demand.v1.json` and `Shared/quality/question-demand-matrix.v1.json`. These paths are **not present on the current main branch**; this pilot therefore **pins historical exact authority** and proposes classifications without manufacturing a replacement canonical policy. The five 0–2 component dimensions and D1 0–2 / D2 3–5 / D3 6–7 / D4 8–10 score ranges are verified against current main `Shared/vocabularies/learner-question-metadata.v1.json`.

Pending: independent academic second-pass sign-off, exact Q5 diagram proof, original Q9 transcription repair as a *separate* source-verified representation, source document digest and reuse permission, further SOF papers, and approval of any proposed QRT cell. The source/maths evidence overlay is not the governed NCERT/CBSE #68 intake, and nothing is moved into learner-facing TEST/Core pages.

## Reproduce

```sh
python TEST/imo-research/validate_sample_pilot.py
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

Validation passing is evidence of **research-metadata integrity only**, not a claim about pedagogical efficacy, official key truth, publication rights, academic review or real-world learner readiness.
