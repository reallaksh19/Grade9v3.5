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
| Q9 | 2024–25 Set B Q44, physical p.7 | Under Everyday Mathematics; compiler erroneously assigns it to Achievers. | Locator reconciled; answer not independently checked |
| Q38 | 2025–26 Set A printed Q32/Q33, physical p.5 | Two numbered questions from a shared pie chart. | Split confirmed; figure retained as dependency |
| Q37 | 2024–25 Set B Q16, physical p.4 | Source has pie chart used by question, not just stated percentages. | Visual asset pending |

Other than this bounded verification evidence, source text, math keys, QRT and publication rights are not verified. This is a **research seed**, not a claim of full-paper ingestion, academic correctness or trusted learner assessment.

## Next responsibility / handoff

Download/hash full permitted source PDFs, compare each original printed page (stems, options, diagrams), independently solve with evidence, resolve disputes explicitly, map chapter/subtopic/microconcept, classify primary cognitive demand using five-component difficulty and one canonical 4×7 QRT cell per question. Only then design a SOF-specific TEST adapter and create draft Core2/Core1A products using the governed blueprint. Never turn source-access evidence into official-key, rights or learner-readiness approval.

## Batch B01 — first source + arithmetic verification (2026-10-08)

The owner asked to proceed after the seed PR. The source scans for 2023–24 A, 2024–25 B, 2025–26 A were independently viewed page-by-page, and **16 individual printed-source questions** across mathematical reasoning, everyday mathematics and Achievers were recalculated.

- `seed/math_audit_batch01.json` stores printed-paper page indexes, original Q number and source URL, derived numeric/symbolic result, **printed** option letter, compilation option letter, calculation and review/rights/figure holds.
- `validate_math_audit.py` recomputes question-specific mathematical oracles and verifies source instance/position identities; it requires the exact three known answer-label disputes, enforces the printed exam-section routing and forbids official-key, Core, or QRT promotion.
- `tests/test_imo_math_audit.py` checks the positive audit and 11 negative/maths cases.

```bash
python TEST/imo-research/validate_math_audit.py
python -m unittest discover -s tests -p 'test_imo_math_audit.py' -v
```

**Measured within B01:** 16/66 candidate positions have inspected printed pages plus independent AI-worked calculations. 13 have the same printed-choice label as the compilation, **3 differ**. Zero have independent peer-review acceptance, independent official key confirmation, rights clearance or verified admission to Core/QRT.

| Compilation entry | Source printed question | Independent calculation | Disposition |
|---|---|---|---|
| Q1 | 2023–24 A Q18, p.4 | -5/12, printed **C**; owner's re-ordered options marked **A** | ORIGINAL_OPTIONS_DIFFER / HOLD |
| Q2 | 2025–26 A Q28, p.5 | Source literally asks *additive identity* => 0, printed **B**; owner rewrote as *additive inverse* => -32/75, claimed **C** | MEANING_CHANGING_SOURCE_TEXT / HOLD |
| Q22 | 2025–26 A Q31, p.5 | From printed rays, b=21°, a=84°, c=48°, printed **C**; owner claimed **D** | DIAGRAM_DEPENDENT_ANSWER_DISPUTE / HOLD |
| Q31 | 2023–24 A Q17, p.4 | Cone height ratio 4:9, printed **C**, agreed with owner's answer | Option A differs from original scan; options HOLD |

The source shows 2023–24 A Q45 and 2024–25 B Q42 with essentially the same hemispherical dome task and answer options. **These are separate exam/source-instance identities** even if a content fingerprint eventually groups them; 2024–25 Q42 is *not* another item in the owner seed.

PDF scans and worked calculations support research claims only: an AI-computed correct result is *not* a separately reviewed mathematical receipt, and a school-mirrored paper is not verified organizer custody or reuse permission. No new question stems, figures, or solution pages were republished.

**CI qualification caveat:** Original PR#228 head `f01430cde4a30fc4d49e5e5e9aad76cf39a0f6e0` had hosted v31-relay and learner-platform-code-tests successes but guardrails and canonical-assurance failures in broad subject/runtime suites. Do not attribute those failures to IMO or assert baseline equivalence without a direct baseline comparison. Any subsequent edit invalidates exact-head qualification; recheck the new PR head before delivery. This research-only branch must remain a draft until independent review/owner decision.
