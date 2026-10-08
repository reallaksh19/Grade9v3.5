# SOF IMO Grade 9 — research-only seed (issue #225)

**Status:** provisional owner-supplied compilation metadata. No item is official-key verified, approved for learner use, or released. This is the **SOF International Mathematics Olympiad (school olympiad)**, not the International Mathematical Olympiad, and not the NCERT/CBSE Exemplar intake.

## Research input and custody

Owner-attached `IMO_Class9_Past_Papers_Topicwise.md`, 68 numbered entries. Entries Q66–Q68 are aliases of Q29, Q27, Q30, respectively; 65 independent compilation entries resolve to **66 original paper question positions** because entry Q38 combines 2025–26 printed Q32 and Q33. Four source claims: three SOF exam paper scans hosted by Indian School Wadi Kabir, Oman, and the SOF-hosted sample-page link for 2026–27. A school mirror is **not** an organiser-hosted or rights-cleared source; reaching a URL is not a complete custody audit.

- `seed/questions.jsonl`: one metadata record per source-position candidate, the attachment's entry/line/digest, original question number *claim*, compilation chapter, statuses, flags. **No stored question stems or option sets.** The paper locator is the de-duplication identity; a shared chart in Q32–33 does not make them one question.
- `seed/sources.json`: organiser/actual host distinction, access observations, source claims and compilation aliases.
- `seed/source_observations.json`: bounded independently inspected printed-page observations; document/page locators and review flags, not mathematical-acceptance receipts.
- `validate_seed.py`: fail-closed structural validation. Deliberately refuses unproven promotion rather than attempting to verify mathematics, source authenticity, copyright or QRT based on JSON presence.

## How to run

From repository root:

```bash
python TEST/imo-research/validate_seed.py
python -m unittest discover -s tests -p 'test_imo_seed.py' -v
```

No TEST question-bank loader, canonical question-bank generator, production or publication workflow is altered or invoked. The current NCERT/CBSE-only intake cannot ingest SOF by just swapping authority labels; a future **versioned SOF adapter** needs separate architectural review.

## Early scanned-page observations (2026-10-08)

| Owner entry | Printed source and page | Evidence result | Status |
|---|---|---|---|
| Q2 | 2025–26 Set A Q28, physical p.5 | Original says **additive identity**, compilation says **additive inverse**. Options include 0 and negative fraction; the source itself may have a mistake, but do not silently correct. | `TEXT_DISPUTED` |
| Q9 | 2024–25 Set B Q44, physical p.7 | Under Mathematical Reasoning; compiler erroneously assigns it to Achievers. | Locator reconciled; answer not independently checked |
| Q38 | 2025–26 Set A printed Q32/Q33, physical p.5 | Two numbered questions from a shared pie chart. | Split confirmed; figure retained as dependency |
| Q37 | 2024–25 Set B Q16, physical p.4 | Source has pie chart used by question, not just stated percentages. | Visual asset pending |

Other than this bounded verification evidence, source text, math keys, QRT and publication rights are not verified. This is a **research seed**, not a claim of full-paper ingestion, academic correctness or trusted learner assessment.

## Next responsibility / handoff

Download/hash full permitted source PDFs, compare each original printed page (stems, options, diagrams), independently solve with evidence, resolve disputes explicitly, map chapter/subtopic/microconcept, classify primary cognitive demand using five-component difficulty and one canonical 4×7 QRT cell per question. Only then design a SOF-specific TEST adapter and create draft Core2/Core1A products using the governed blueprint. Never turn source-access evidence into official-key, rights or learner-readiness approval.
