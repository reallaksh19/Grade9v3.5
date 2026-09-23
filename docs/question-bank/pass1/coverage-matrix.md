# Pass 1 competitive-exam coverage matrix

Issue: #216  
Scope: question-bank custody only; no practice sets or exams.

## Active bank

The active fixture-native v2 custody surface contains **54 source-matched PYQ adaptations**:

- `Physics/library/exam-bank/competitive-exam-question-bank.v2.json` — **21**
- `Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json` — **33**

Every learner-facing item is `PYQ_ADAPTED`: its historical parent is matched to a first-party organizer question source, while stored wording is explicitly a faithful non-verbatim restatement. Source `hints[]` remains source-only; authored teaching support is in `scaffolds[]`.

## Topic totals

| Topic / bucket | Accepted items | D1 | D2 | D3 | D4 | Source status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `BUCKET-PHY-NLM-FIRST-LAW` | 9 | 0 | 5 | 3 | 1 | Source-matched |
| `BUCKET-PHY-KIN-2D-MOTION` | 10 | 0 | 2 | 6 | 2 | Source-matched; circular motion excluded |
| `BUCKET-RELATIVE-MOTION` | 2 | 0 | 1 | 1 | 0 | Source-matched; narrow acquisition remains sparse |
| `BUCKET-CHEM-REDOX-REACTIONS` | 19 | 4 | 10 | 5 | 0 | Source-matched |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | 14 | 0 | 11 | 3 | 0 | Source-matched |
| **TOTAL** | **54** | **4** | **29** | **18** | **3** | No authored fill |


## Accepted IDs by topic

### Newton's Laws of Motion / NLM (9)

- `PYQ-PHY-IITJEE-2007-P1-Q03`
- `PYQ-PHY-IITJEE-2007-P1-Q10`
- `PYQ-PHY-IITJEE-2008-P2-Q33`
- `PYQ-PHY-IITJEE-2011-P1-Q41`
- `PYQ-PHY-IITJEE-2011-P2-Q34`
- `PYQ-PHY-JEEADV-2014-P1-Q08`
- `PYQ-PHY-JEEADV-2014-P2-Q19`
- `PYQ-PHY-JEEADV-2020-P1-Q13`
- `PYQ-PHY-NEET-2020-E1-Q160`

### Motion in 2D / Motion in a Plane — linear/projectile only (10)

- `PYQ-PHY-IITJEE-2011-P2-Q33`
- `PYQ-PHY-IITJEE-2012-P1-Q05`
- `PYQ-PHY-JEEADV-2018-P2-Q08`
- `PYQ-PHY-JEEADV-2019-P2-Q09`
- `PYQ-PHY-JEEADV-2021-P1-Q05`
- `PYQ-PHY-JEEADV-2021-P1-Q06`
- `PYQ-PHY-JEEADV-2022-P1-Q08`
- `PYQ-PHY-JEEADV-2023-P1-Q01`
- `PYQ-PHY-JEEADV-2024-P2-Q09`
- `PYQ-PHY-JEEADV-2025-P2-Q15`

### Motion in 1D — relative motion only (2)

- `PYQ-PHY-IITJEE-2008-P2-Q32`
- `PYQ-PHY-JEEADV-2014-P1-Q18`

### Redox Reactions (19)

- `PYQ-CHEM-IITJEE-2008-P1-Q66`
- `PYQ-CHEM-IITJEE-2011-P1-Q17`
- `PYQ-CHEM-IITJEE-2011-P1-Q18`
- `PYQ-CHEM-IITJEE-2012-P2-Q22`
- `PYQ-CHEM-JEEADV-2014-P1-Q29`
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
- `PYQ-CHEM-NEET-2020-E1-Q099`
- `PYQ-CHEM-NEET-2020-E1-Q125`

### Some Basic Concepts of Chemistry / Mole Concept / Stoichiometry (14)

- `PYQ-CHEM-IITJEE-2007-P1-Q39`
- `PYQ-CHEM-IITJEE-2007-P1-Q40`
- `PYQ-CHEM-IITJEE-2007-P1-Q41`
- `PYQ-CHEM-IITJEE-2008-P2-Q51`
- `PYQ-CHEM-IITJEE-2011-P2-Q14`
- `PYQ-CHEM-JEEADV-2014-P1-Q39`
- `PYQ-CHEM-JEEADV-2016-P1-Q32`
- `PYQ-CHEM-JEEADV-2018-P1-Q08`
- `PYQ-CHEM-JEEADV-2023-P1-Q08`
- `PYQ-CHEM-JEEADV-2025-P1-Q12`
- `PYQ-CHEM-JEEADV-2025-P2-Q16`
- `PYQ-CHEM-NEET-2020-E1-Q106`
- `PYQ-CHEM-NEET-2020-E1-Q110`
- `PYQ-CHEM-NEET-2020-E1-Q123`

## Source-lineage status

| Lineage | PASS 1 status | Rule |
| --- | --- | --- |
| IIT-JEE / JEE (Advanced) | **ACCEPTED** | Organizer archive supplies persistent historical question papers. |
| NEET | **PARTIAL ACCEPTED** | 2020 English Set E1 is matched to the official NEET paper and NTA final key. |
| JEE Main / AIEEE | **HELD** | Official notices/keys were located, but targeted donor stems are not promoted without a persistent first-party paper parent. |
| AIPMT | **HELD** | Official CBSE key material alone is not enough to promote a question. |

The bank is therefore larger without lowering the provenance threshold. Secondary donor registries remain discovery inputs only.

## Core2 / Core2A custody split

- historical identity and official source locator: `extensions["grade9v3:source_custody"]`;
- learner-facing wording: `origin: "ADAPTED"` / `PYQ_ADAPTED`;
- source hints: `hints[]`;
- authored graduated help: `scaffolds[]`;
- answer, reasoning route, crux, rubric and independent check: `answer`.

No practice set or exam is generated in PASS 1.
