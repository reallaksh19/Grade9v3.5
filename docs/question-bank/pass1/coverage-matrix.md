# Pass 1 competitive-exam coverage matrix

Issue: #216  
Scope: question-bank custody only; no practice sets or exams.

## Active bank

- `Physics/library/exam-bank/competitive-exam-question-bank.v2.json`
- `Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json`

All 77 learner-usable records are `PYQ_ADAPTED` children of independently verified first-party PYQ parents. No fully authored item is used to fill coverage gaps.

## Topic totals

| Topic / bucket | Accepted | D1 | D2 | D3 | D4 | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `BUCKET-PHY-NLM-FIRST-LAW` | 13 | 0 | 6 | 6 | 1 | Source-matched |
| `BUCKET-PHY-KIN-2D-MOTION` | 15 | 0 | 3 | 9 | 3 | Source-matched; circular motion excluded |
| `BUCKET-RELATIVE-MOTION` | 3 | 0 | 2 | 1 | 0 | Source-matched; still the sparsest topic |
| `BUCKET-CHEM-REDOX-REACTIONS` | 26 | 7 | 13 | 6 | 0 | Source-matched |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | 20 | 0 | 16 | 4 | 0 | Source-matched |
| **TOTAL** | **77** | **7** | **40** | **26** | **4** | No authored fill |


## Exam-family distribution

| Historical exam identity | Accepted items |
| --- | ---: |
| IIT-JEE | 27 |
| JEE (Advanced) | 39 |
| JEE Main | 5 |
| NEET (UG) | 6 |

The JEE Main 2026 Session 2 additions are matched to organizer-hosted shift papers and the NTA final answer key. Legacy IIT-JEE remains labelled IIT-JEE; JEE (Advanced) remains labelled JEE (Advanced). Unmatched JEE Main/AIEEE and AIPMT/NEET donor claims remain quarantined.

## Cross-dimensional matrix

This is the requested concept bucket × exam source × question type × D1/D2/D3/D4 × provenance view. Empty cells are not manufactured.

| Concept bucket | Exam source | Question type | D1 | D2 | D3 | D4 | Provenance | Count |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | ---: |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | IIT-JEE | `integer_answer` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | IIT-JEE | `single_correct_mcq` | 0 | 6 | 0 | 0 | `PYQ_ADAPTED` | 6 |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | JEE (Advanced) | `integer_answer` | 0 | 2 | 2 | 0 | `PYQ_ADAPTED` | 4 |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | JEE (Advanced) | `numerical_value` | 0 | 3 | 2 | 0 | `PYQ_ADAPTED` | 5 |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | JEE Main | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | NEET (UG) | `single_correct_mcq` | 0 | 3 | 0 | 0 | `PYQ_ADAPTED` | 3 |
| `BUCKET-CHEM-REDOX-REACTIONS` | IIT-JEE | `integer_answer` | 1 | 2 | 0 | 0 | `PYQ_ADAPTED` | 3 |
| `BUCKET-CHEM-REDOX-REACTIONS` | IIT-JEE | `multi_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-REDOX-REACTIONS` | IIT-JEE | `single_correct_mcq` | 4 | 0 | 0 | 0 | `PYQ_ADAPTED` | 4 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `integer_answer` | 0 | 1 | 2 | 0 | `PYQ_ADAPTED` | 3 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `multi_correct_mcq` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `non_negative_integer` | 0 | 1 | 1 | 0 | `PYQ_ADAPTED` | 2 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `numerical_value` | 0 | 6 | 2 | 0 | `PYQ_ADAPTED` | 8 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE Main | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-CHEM-REDOX-REACTIONS` | NEET (UG) | `single_correct_mcq` | 2 | 0 | 0 | 0 | `PYQ_ADAPTED` | 2 |
| `BUCKET-PHY-KIN-2D-MOTION` | IIT-JEE | `integer_answer` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-KIN-2D-MOTION` | IIT-JEE | `single_correct_mcq` | 0 | 0 | 1 | 1 | `PYQ_ADAPTED` | 2 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE (Advanced) | `integer_answer` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE (Advanced) | `multi_correct_mcq` | 0 | 0 | 1 | 1 | `PYQ_ADAPTED` | 2 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE (Advanced) | `non_negative_integer` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE (Advanced) | `numerical_value` | 0 | 2 | 3 | 1 | `PYQ_ADAPTED` | 6 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE (Advanced) | `single_correct_mcq` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-KIN-2D-MOTION` | JEE Main | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `assertion_reason_mcq` | 0 | 2 | 0 | 0 | `PYQ_ADAPTED` | 2 |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `integer_answer` | 0 | 2 | 1 | 0 | `PYQ_ADAPTED` | 3 |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `multi_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `single_correct_mcq` | 0 | 0 | 2 | 0 | `PYQ_ADAPTED` | 2 |
| `BUCKET-PHY-NLM-FIRST-LAW` | JEE (Advanced) | `matrix_match_mcq` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | JEE (Advanced) | `multi_correct_mcq` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | JEE (Advanced) | `numerical_value` | 0 | 0 | 0 | 1 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | JEE Main | `integer_answer` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-PHY-NLM-FIRST-LAW` | NEET (UG) | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-RELATIVE-MOTION` | IIT-JEE | `assertion_reason_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-RELATIVE-MOTION` | JEE (Advanced) | `integer_answer` | 0 | 0 | 1 | 0 | `PYQ_ADAPTED` | 1 |
| `BUCKET-RELATIVE-MOTION` | JEE Main | `single_correct_mcq` | 0 | 1 | 0 | 0 | `PYQ_ADAPTED` | 1 |

## Accepted IDs by topic

### Newton's Laws of Motion / NLM (13)

- `PYQ-PHY-IITJEE-2007-P1-Q03`
- `PYQ-PHY-IITJEE-2007-P1-Q10`
- `PYQ-PHY-IITJEE-2008-P2-Q33`
- `PYQ-PHY-IITJEE-2009-P1-Q49`
- `PYQ-PHY-IITJEE-2009-P2-Q40`
- `PYQ-PHY-IITJEE-2009-P2-Q55`
- `PYQ-PHY-IITJEE-2011-P1-Q41`
- `PYQ-PHY-IITJEE-2011-P2-Q34`
- `PYQ-PHY-JEEADV-2014-P1-Q08`
- `PYQ-PHY-JEEADV-2014-P2-Q19`
- `PYQ-PHY-JEEADV-2020-P1-Q13`
- `PYQ-PHY-JEEMAIN-2026-06APR-S2-Q46`
- `PYQ-PHY-NEET-2020-E1-Q160`

### Motion in 2D / Motion in a Plane — linear/projectile only (15)

- `PYQ-PHY-IITJEE-2011-P2-Q26`
- `PYQ-PHY-IITJEE-2011-P2-Q33`
- `PYQ-PHY-IITJEE-2012-P1-Q05`
- `PYQ-PHY-JEEADV-2013-P1-Q07`
- `PYQ-PHY-JEEADV-2014-P1-Q11`
- `PYQ-PHY-JEEADV-2018-P2-Q08`
- `PYQ-PHY-JEEADV-2019-P2-Q09`
- `PYQ-PHY-JEEADV-2021-P1-Q05`
- `PYQ-PHY-JEEADV-2021-P1-Q06`
- `PYQ-PHY-JEEADV-2022-P1-Q08`
- `PYQ-PHY-JEEADV-2023-P1-Q01`
- `PYQ-PHY-JEEADV-2024-P2-Q09`
- `PYQ-PHY-JEEADV-2025-P2-Q15`
- `PYQ-PHY-JEEADV-2026-P1-Q06`
- `PYQ-PHY-JEEMAIN-2026-04APR-S2-Q29`

### Motion in 1D — relative motion only (3)

- `PYQ-PHY-IITJEE-2008-P2-Q32`
- `PYQ-PHY-JEEADV-2014-P1-Q18`
- `PYQ-PHY-JEEMAIN-2026-04APR-S2-Q27`

### Redox Reactions (26)

- `PYQ-CHEM-IITJEE-2008-P1-Q66`
- `PYQ-CHEM-IITJEE-2009-P2-Q05`
- `PYQ-CHEM-IITJEE-2009-P2-Q16`
- `PYQ-CHEM-IITJEE-2010-P1-Q16`
- `PYQ-CHEM-IITJEE-2011-P1-Q17`
- `PYQ-CHEM-IITJEE-2011-P1-Q18`
- `PYQ-CHEM-IITJEE-2011-P2-Q01`
- `PYQ-CHEM-IITJEE-2012-P2-Q22`
- `PYQ-CHEM-JEEADV-2014-P1-Q29`
- `PYQ-CHEM-JEEADV-2015-P1-Q27`
- `PYQ-CHEM-JEEADV-2015-P2-Q28`
- `PYQ-CHEM-JEEADV-2016-P1-Q34`
- `PYQ-CHEM-JEEADV-2018-P2-Q08`
- `PYQ-CHEM-JEEADV-2018-P2-Q09`
- `PYQ-CHEM-JEEADV-2019-P2-Q09`
- `PYQ-CHEM-JEEADV-2020-P2-Q03`
- `PYQ-CHEM-JEEADV-2021-P2-Q11`
- `PYQ-CHEM-JEEADV-2021-P2-Q12`
- `PYQ-CHEM-JEEADV-2022-P1-Q04`
- `PYQ-CHEM-JEEADV-2023-P2-Q08`
- `PYQ-CHEM-JEEADV-2023-P2-Q10`
- `PYQ-CHEM-JEEADV-2024-P2-Q02`
- `PYQ-CHEM-JEEADV-2025-P1-Q08`
- `PYQ-CHEM-JEEMAIN-2026-04APR-S2-Q62`
- `PYQ-CHEM-NEET-2020-E1-Q099`
- `PYQ-CHEM-NEET-2020-E1-Q125`

### Some Basic Concepts of Chemistry / Mole Concept / Stoichiometry (20)

- `PYQ-CHEM-IITJEE-2007-P1-Q39`
- `PYQ-CHEM-IITJEE-2007-P1-Q40`
- `PYQ-CHEM-IITJEE-2007-P1-Q41`
- `PYQ-CHEM-IITJEE-2008-P2-Q51`
- `PYQ-CHEM-IITJEE-2009-P1-Q01`
- `PYQ-CHEM-IITJEE-2009-P1-Q04`
- `PYQ-CHEM-IITJEE-2011-P2-Q14`
- `PYQ-CHEM-JEEADV-2014-P1-Q39`
- `PYQ-CHEM-JEEADV-2015-P2-Q25`
- `PYQ-CHEM-JEEADV-2016-P1-Q32`
- `PYQ-CHEM-JEEADV-2017-P1-Q26`
- `PYQ-CHEM-JEEADV-2018-P1-Q08`
- `PYQ-CHEM-JEEADV-2023-P1-Q08`
- `PYQ-CHEM-JEEADV-2025-P1-Q12`
- `PYQ-CHEM-JEEADV-2025-P2-Q16`
- `PYQ-CHEM-JEEADV-2026-P1-Q09`
- `PYQ-CHEM-JEEMAIN-2026-06APR-S2-Q51`
- `PYQ-CHEM-NEET-2020-E1-Q106`
- `PYQ-CHEM-NEET-2020-E1-Q110`
- `PYQ-CHEM-NEET-2020-E1-Q123`

## Provenance boundary

- Core2 source identity lives in `extensions["grade9v3:source_custody"]`, including exam, year, session/shift paper identity, original question number, first-party paper URL, answer-key URL where available, last-checked date and verification status.
- Learner wording is explicitly `origin: "ADAPTED"` / `PYQ_ADAPTED`; each adaptation preserves `parent_ref` and an exact `changed_fields` list.
- Official source hints remain in `hints[]`; authored pedagogical support remains separate in `scaffolds[]`.
- Existing public/explorer registries are preserved as donor evidence and do not become authority merely by carrying an exam label.
- No final practice set or exam is generated in PASS 1.
