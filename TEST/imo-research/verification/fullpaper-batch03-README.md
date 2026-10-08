# SOF IMO Grade 9 — scanned full-paper maths audit B03

**Research evidence only. No original question stems, options, scanned diagrams or PDF bytes are reproduced.** The original input remains 66 question candidates from the user's supplied topic-wise compilation (58 from original full papers, 8 from organizer sample).

This is the **third non-overlapping mathematical audit batch**, grounded in school-hosted scans that carry SOF IMO printed original question numbers and options:

- [2023–24 Set A, original eight-page scan](https://iswkoman.com/uploads/olympiad/8919398-CL%20IX%20IMO%202023-24%20(1).pdf): 15 source positions — Q6, Q19, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q42, Q43, Q47, Q49, Q50.
- [2024–25 Set B, original eight-page scan](https://www.iswkoman.com/uploads/olympiad/2107431-CLASS%209-IMO24.pdf): one source position — Q43.

All sixteen original paper questions were inspected on their respective *printed PDF pages* (physical zero-index 1, 3, 5, 6, or 7 for 2023; 6 for 2024). The new `fullpaper-audit-b03.v1.json` records original question ID, attachment entry, source URL, printed section, mathematical answer, selected printed option, owner's claimed option, a researcher-worked derivation, independent reverse or alternative calculation and explicitly unapproved academic, original-key, rights, QRT and Core statuses.

## Source-grounded results

| Audit | Original full-paper question positions with AI-worked maths | Total coverage |
|---|---:|---:|
| B01 | 16 | 16/58 |
| B02 | 15 | 31/58 |
| **B03** | **16** | **47/58** |

All 16 mathematical answer-letter comparisons in this B03 batch align with the owner's provided option letters. This is **not** proof that every owner transcription is correct or that the school-hosted paper scan carries the official SOF answer key; no independent academic or copyright sign-off is claimed.

Key verification examples:

- **2023 Q35**: a 16⅔% compound-interest rate implies a two-year multiplier of 49/36; principal ₹20,825 × 36/49 = **₹15,300**, printed A.
- **2023 Q37**: 30% of all staff are high-earning men; 15% high-earning women out of 60% women; **3/4 of women** are not in the higher income bracket, printed D.
- **2023 Q47**: opposite-angle supplements prove the bisector quadrilateral cyclic; the diameter gives a right angle and the original cyclic quadrilateral gives the remaining **50°**, so both original assertions hold, printed C.
- **2023 Q49**: doubling triangle sides multiplies area by 4, i.e. a **300% increase**; the 5–12–13 triangle altitude to hypotenuse is **60/13**, not 60. Both assertions false, printed D.
- **2024 Q43**: solve two independent worker-output constraints to infer a man works 1/100 job/day and a boy 1/200 job/day. A group of 15 men + 20 boys finishes in **4 days**, printed A.

## What remains

- All **23 original seeded source positions from 2023–24 A and 12 from 2024–25 B** are now included in at least one of the B01/B02/B03 agent-worked audits. The remaining **11 original full-paper source candidates are exclusively in 2025–26 Set A**.
- Already documented answer or text discrepancies remain in their original observation ledgers; agreement in B03 does not erase the earlier Q1, Q2, Q22 or Q46 concerns.
- Separate organizer sample has ten identified question positions: original owner seed eight + two separately discovered source records, not part of the 58 original full-paper denominator.
- **Zero** official-answer-key receipts accepted for the school-hosted full papers, independent academic review approvals, rights/redistribution approvals, accepted 4×7 QRT cells, or Core 2/Core 1A admissions. No sample or fullpaper questions were made learner-facing.

## Integrity tests

```sh
python TEST/imo-research/validate_fullpaper_batch03.py
python -m unittest discover -s tests -p 'test_imo_fullpaper_batch03.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

`validate_fullpaper_batch03.py` checks source-page identity, original exam sections, independently derived answers, all 16 new IDs disjoint from B01 and B02, 47/58 source-position census, the 11 remaining source candidates all in 2025–26 Set A, and no false academic/rights/QRT/Core acceptance.

Scope: `TEST/imo-research/**`, focused tests and the dedicated IMO research workflow only. The NCERT/CBSE-only intake adapter, Shared library, canonical learner pages and source-document redistribution permissions are deliberately outside this responsibility.
