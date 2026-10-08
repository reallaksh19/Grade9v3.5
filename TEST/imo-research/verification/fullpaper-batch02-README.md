# SOF IMO Grade 9 — printed-paper mathematical audit B02

**Research-only, no learner admission.** This second source/math audit extends the 16 previously examined full-paper source instances in `../seed/math_audit_batch01.json` by **15 distinct, previously unreviewed original-paper question positions**: six from SOF-branded 2023–24 Level 1 Set A and nine from 2024–25 Level 1 Set B.

The original scans were visually inspected (physical PDFs p.2–6): [2023–24 Set A](https://iswkoman.com/uploads/olympiad/8919398-CL%20IX%20IMO%202023-24%20(1).pdf), [2024–25 Set B](https://www.iswkoman.com/uploads/olympiad/2107431-CLASS%209-IMO24.pdf). These are school-hosted mirrors, not authenticated organizer answer keys or reproduction permission. Source page, printed number, section by original full-paper position, agent-derived mathematical outcome, chosen **printed** option, attachment-claimed choice and alternate check are separate fields in `fullpaper-source-math-batch02.v1.json`.

## Scope and discrepancy

| Paper | Original printed question numbers newly examined | Count |
|---|---|---:|
| 2023–24 A | Q3, Q13, Q25, Q27, Q28, Q29 | 6 |
| 2024–25 B | Q19, Q20, Q24, Q26, Q27, Q29, Q31, Q33, Q35 | 9 |
| **Total B02** | | **15** |

The **new concrete error** is Owner compilation **Q46** (2023–24 A printed Q13). Source digit transformation:
`5736928 → 4625817 → 1245678`.
The fourth digit is **5 (printed option B)**, but the compilation labels **4 (choice C)**. Its own intermediate sequence reveals that inconsistency. This is a mathematical/answer-source dispute and must not be silently cleared or recoded as an original option reorder. No official source solution/key for this school-mirrored full paper has been independently obtained.

All other **14 of 15 printed-option answers align with the compilation's claimed choice** in this bounded batch. That agreement reflects our agent calculations and the attachment; it is **not** an independently human-reviewed academic acceptance.

Combined counts: **16 B01 + 15 B02 = 31/58** original full Level 1 paper seed positions with agent mathematical checks. The distinct organizer sample is a separate document: the original seed includes 8 of its 10 sample positions; two separately discovered new source IDs were added through PR#241. Do not reinterpret sample-local questions as 50-question exam positions or count them as part of the 58 full-paper denominator. The original 66 source candidate record set remains unchanged.

## Validation and acceptance boundaries

```sh
python TEST/imo-research/validate_fullpaper_batch02.py
python -m unittest discover -s tests -p 'test_imo_fullpaper_batch02.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The source-aware validator checks exact B01/B02 disjointness, original PDF locator and section, per-question arithmetic or logic oracles, exactly one documented discrepancy, no copied original stems/options/figures, and no premature official-key/rights/QRT/Core acceptance. The dedicated IMO GitHub workflow executes the validator and all `test_imo_*.py` tests.

Open gaps: **27/58** original full-paper positions in the attachment not yet independently worked, including composite/diagram questions; the school-hosted scans lack a reviewed answer-key receipt; mathematical second reviewer, full transcriptions, source hashes, figure custody and reproduction rights are pending. Topic, subtopic and QRT proposals do **not** constitute accepted learner-facing material. Do not modify NCERT/CBSE-only intake #68 or produce Core 2/Core 1A products from this research.
