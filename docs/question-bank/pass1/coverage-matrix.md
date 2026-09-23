# Pass 1 competitive-exam coverage matrix

Issue: #201  
Scope: question-bank custody only; no practice sets or exams.

## Accepted canonical candidates

This matrix is intentionally sparse. Cells are populated only by accepted source records; blank difficulty bands are not back-filled with authored material.

| Concept bucket | Exam source | Question type | D1 | D2 | D3 | D4 | Provenance | Item IDs |
| --- | --- | --- | ---: | ---: | ---: | ---: | --- | --- |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | IIT-JEE | `single_correct_mcq` | 0 | 3 | 0 | 0 | `PYQ_VERIFIED` | `PYQ-CHEM-IITJEE-2007-P1-Q39`, `PYQ-CHEM-IITJEE-2007-P1-Q40`, `PYQ-CHEM-IITJEE-2007-P1-Q41` |
| `BUCKET-CHEM-REDOX-REACTIONS` | IIT-JEE | `single_correct_mcq` | 1 | 0 | 0 | 0 | `PYQ_VERIFIED` | `PYQ-CHEM-IITJEE-2008-P1-Q66` |
| `BUCKET-CHEM-REDOX-REACTIONS` | JEE (Advanced) | `non_negative_integer` | 0 | 0 | 1 | 0 | `PYQ_VERIFIED` | `PYQ-CHEM-JEEADV-2023-P2-Q08` |
| `BUCKET-PHY-KIN-2D-MOTION` | IIT-JEE | `integer_answer` | 0 | 0 | 1 | 0 | `PYQ_VERIFIED` | `PYQ-PHY-IITJEE-2011-P2-Q33` |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `integer_answer` | 0 | 1 | 0 | 0 | `PYQ_VERIFIED` | `PYQ-PHY-IITJEE-2011-P1-Q41` |
| `BUCKET-PHY-NLM-FIRST-LAW` | IIT-JEE | `single_correct_mcq` | 0 | 0 | 1 | 0 | `PYQ_VERIFIED` | `PYQ-PHY-IITJEE-2007-P1-Q03` |
| `BUCKET-RELATIVE-MOTION` | — | — | 0 | 0 | 0 | 0 | — | **ACQUISITION HOLD** |

## Topic totals

| Topic / bucket | PYQ_VERIFIED | PYQ_ADAPTED | SOURCE_UNVERIFIED promoted | Coverage note |
| --- | ---: | ---: | ---: | --- |
| `BUCKET-PHY-NLM-FIRST-LAW` | 2 | 0 | 0 | Only organizer-verified items shown. |
| `BUCKET-PHY-KIN-2D-MOTION` | 1 | 0 | 0 | Only organizer-verified items shown. |
| `BUCKET-RELATIVE-MOTION` | 0 | 0 | 0 | No authoritative straight-line relative-motion source matched in Pass 1; donor candidates remain quarantined. |
| `BUCKET-CHEM-REDOX-REACTIONS` | 2 | 0 | 0 | Only organizer-verified items shown. |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | 3 | 0 | 0 | Only organizer-verified items shown. |

## Source-status boundary

The `SOURCE_UNVERIFIED` donor population is reported in `source-acquisition-ledger.json` and `rejected-unverified-sources.md`. Those candidates are deliberately excluded from D1-D4 cells because difficulty analysis is attached only after the source item is accepted into canonical custody. This avoids creating a visually rectangular matrix by manufacturing questions or analysis.

## Exam identity

Legacy 2007, 2008 and 2011 records remain labelled **IIT-JEE**. The 2023 record is labelled **JEE (Advanced)**. No historical relabelling is performed.
