# SOF IMO Grade 9 — final original full-paper maths research batch B04

**Research status: agent-computed, not independently academically accepted.** This completes the *original attachment-derived source-position audit census*, not the entire historical SOF IMO question corpus or the complete 50-question contents of each examined paper.

The user-provided topic-wise compilation generated **66 independent source-position candidates**: 58 original Level 1 full-paper positions and 8 local positions on the SOF 2026–27 organizer sample. Two further source positions Q1/Q3 on the official sample were discovered separately in PR #241; they are **not** smuggled into the original 66 seed.

Original B04 paper: [2025–26 Set A scanned Level 1 paper](https://www.iswkoman.com/uploads/olympiad/9262492-IMO%2025-26%20CLASS%209.pdf), school-hosted SOF-branded **7-page scan**. Original printed questions **Q36,Q37,Q38,Q40,Q43,Q44** are on printed page 6 / PDF index 5; Q45,Q46,Q47,Q48,Q50 on printed page 7 / PDF index 6. These were visually inspected; the B04 JSON links source identity, original printed position, section, agent mathematical calculation, independent reverse check, printed option, owner compilation answer label and rights/reviewer hold for each.

## Source-position audit census

| Audit | Scanned original question positions newly worked | Running full-paper coverage |
|---|---:|---:|
| B01 | 16 | 16/58 |
| B02 | 15 | 31/58 |
| B03 | 16 | 47/58 |
| **B04** | **11** | **58/58** |

The denominator **58** describes only the original full-paper question positions represented in the owner's supplied compilation across 2023–24 A (24 positions), 2024–25 B (12) and 2025–26 A (22). This does **not** mean all 150 potential question positions in three full exams have been ingested or source-key verified.

All 11 B04 selected-answer letters agree with the owner compilation. Example mathematical checks:

- **Printed Q36**: square original tree arrangement has 10,914+111=11,025 trees, hence 105 rows (B).
- **Printed Q40**: successive multipliers 1.40×0.90=1.26 give 26% increase (D).
- **Printed Q44**: two simultaneous savings constraints determine P's annual income to be ₹4,000 (C).
- **Printed Q48**: cone-to-cylinder volume and 3:4 cone ratios are consistent; the maximum sphere in a 7 cm cube is approximately 179.5 cm³, not 185.76, hence claim C is incorrect (C).
- **Printed Q50**: the shorter and longer chords of the same circle have centre distances 4 and 3 respectively. For the two cyclic quadrilaterals visible in the original diagram, the outer-circle equality ∠CDA=∠CBA and inner-circle equality ∠FEA=∠FBA, together with the source collinearities A/E/D and B/F/C, imply EF is parallel to DC. Both source assertions true (A). Figure inspected but original image is **not licensed or reproduced**.

Earlier research disagreements remain open: original paper 2023 Q18 versus the attachment's reordered option labels, printed 2025 Q28 *identity* versus attachment *inverse* wording, source 2025 Q31 intersection diagram versus attachment option, 2023 Q13 fourth sorted digit, plus the official sample Q9 rewritten roots/powers. B04 does not overwrite prior discrepancy evidence.

## Exact validation and custody

```sh
python TEST/imo-research/validate_fullpaper_batch04.py
python -m unittest discover -s tests -p 'test_imo_fullpaper_batch04.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The validator verifies B01–B04 source-position sets are pairwise disjoint, exhaust exactly **the 58 original full-paper source positions**, retain the eight original organizer sample positions separately, and require original printed locator/page/section, derived mathematical result, figure hold and honest no-acceptance status. The dedicated `SOF IMO research seed integrity` GitHub workflow now executes B04 and all focused `test_imo_*.py` tests.

**Outstanding gates remain nonzero despite the complete audit census:** independent qualified academic second pass, exact-source transcription/image custody and hashes, printed official **full-paper answer key** receipts, legal reuse permission for question text/option sets/figures, and evidence-based QRT 4×7 admission. Currently **0 independently approved full-paper answers, 0 accepted QRT cells, 0 copyright clearances and 0 Core-ready questions**. A green metadata/math validator does not grant those authorities.

Next responsible work should prioritize a discrepancy adjudication pack, 1:1 figure/notation capture with permission boundaries, and independent academic reviewer sign-off. Do not route SOF material through NCERT/CBSE-only intake #68 or create learner-facing Core 2/Core 1A products from this ledger.
