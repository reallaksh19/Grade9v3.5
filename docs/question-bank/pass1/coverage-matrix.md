# Pass 1 competitive-exam coverage matrix

Issue: #201  
Scope: question-bank custody only; no practice sets or exams.

## Active bank

The active expanded bank is the fixture-native v2 custody surface:

- `Physics/library/exam-bank/competitive-exam-question-bank.v2.json`
- `Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json`

All accepted learner-usable records are `PYQ_ADAPTED`: the historical parent is verified against a first-party organizer question paper, while stored learner wording is explicitly a faithful non-verbatim restatement. Source hints remain in `question.hints[]`; authored teaching support remains in `question.scaffolds[]`.

## Topic totals

| Topic / bucket | Accepted | D1 | D2 | D3 | D4 | Status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `BUCKET-PHY-NLM-FIRST-LAW` | 12 | 0 | 6 | 5 | 1 | Source-matched |
| `BUCKET-PHY-KIN-2D-MOTION` | 13 | 0 | 2 | 8 | 3 | Source-matched; circular motion excluded |
| `BUCKET-RELATIVE-MOTION` | 2 | 0 | 1 | 1 | 0 | Source-matched; narrow relative-motion scope remains sparse |
| `BUCKET-CHEM-REDOX-REACTIONS` | 25 | 7 | 12 | 6 | 0 | Source-matched |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | 19 | 0 | 15 | 4 | 0 | Source-matched |
| **TOTAL** | **71** | **7** | **36** | **24** | **4** | No authored fill |

## Exam-family distribution

| Historical exam identity | Accepted items |
| --- | ---: |
| IIT-JEE | 27 |
| JEE (Advanced) | 38 |
| NEET (UG) | 6 |

JEE Main/AIEEE and additional AIPMT/NEET candidates are **not** promoted from secondary attributions alone. They remain acquisition targets until a persistent first-party question-paper match is established.

## Accepted IDs by topic

### Newton's Laws of Motion / NLM (12)

- `PYQ-PHY-IITJEE-2007-P1-Q03`
- `PYQ-PHY-IITJEE-2007-P1-Q10`
- `PYQ-PHY-IITJEE-2008-P2-Q33`
- `PYQ-PHY-IITJEE-2011-P1-Q41`
- `PYQ-PHY-IITJEE-2011-P2-Q34`
- `PYQ-PHY-JEEADV-2014-P2-Q19`
- `PYQ-PHY-JEEADV-2020-P1-Q13`
- `PYQ-PHY-JEEADV-2014-P1-Q08`
- `PYQ-PHY-NEET-2020-E1-Q160`
- `PYQ-PHY-IITJEE-2009-P1-Q49`
- `PYQ-PHY-IITJEE-2009-P2-Q40`
- `PYQ-PHY-IITJEE-2009-P2-Q55`

### Motion in 2D / Motion in a Plane — linear/projectile only (13)

- `PYQ-PHY-IITJEE-2011-P2-Q33`
- `PYQ-PHY-JEEADV-2018-P2-Q08`
- `PYQ-PHY-JEEADV-2019-P2-Q09`
- `PYQ-PHY-JEEADV-2021-P1-Q05`
- `PYQ-PHY-JEEADV-2021-P1-Q06`
- `PYQ-PHY-JEEADV-2024-P2-Q09`
- `PYQ-PHY-IITJEE-2012-P1-Q05`
- `PYQ-PHY-JEEADV-2022-P1-Q08`
- `PYQ-PHY-JEEADV-2023-P1-Q01`
- `PYQ-PHY-JEEADV-2025-P2-Q15`
- `PYQ-PHY-IITJEE-2011-P2-Q26`
- `PYQ-PHY-JEEADV-2014-P1-Q11`
- `PYQ-PHY-JEEADV-2026-P1-Q06`

### Motion in 1D — relative motion only (2)

- `PYQ-PHY-IITJEE-2008-P2-Q32`
- `PYQ-PHY-JEEADV-2014-P1-Q18`

### Redox Reactions (25)

- `PYQ-CHEM-IITJEE-2008-P1-Q66`
- `PYQ-CHEM-IITJEE-2011-P1-Q17`
- `PYQ-CHEM-IITJEE-2011-P1-Q18`
- `PYQ-CHEM-IITJEE-2012-P2-Q22`
- `PYQ-CHEM-JEEADV-2023-P2-Q08`
- `PYQ-CHEM-JEEADV-2024-P2-Q02`
- `PYQ-CHEM-JEEADV-2025-P1-Q08`
- `PYQ-CHEM-NEET-2020-E1-Q099`
- `PYQ-CHEM-NEET-2020-E1-Q125`
- `PYQ-CHEM-JEEADV-2014-P1-Q29`
- `PYQ-CHEM-JEEADV-2016-P1-Q34`
- `PYQ-CHEM-JEEADV-2018-P2-Q08`
- `PYQ-CHEM-JEEADV-2018-P2-Q09`
- `PYQ-CHEM-JEEADV-2019-P2-Q09`
- `PYQ-CHEM-JEEADV-2020-P2-Q03`
- `PYQ-CHEM-JEEADV-2021-P2-Q11`
- `PYQ-CHEM-JEEADV-2021-P2-Q12`
- `PYQ-CHEM-JEEADV-2022-P1-Q04`
- `PYQ-CHEM-JEEADV-2023-P2-Q10`
- `PYQ-CHEM-IITJEE-2009-P2-Q05`
- `PYQ-CHEM-IITJEE-2009-P2-Q16`
- `PYQ-CHEM-IITJEE-2010-P1-Q16`
- `PYQ-CHEM-IITJEE-2011-P2-Q01`
- `PYQ-CHEM-JEEADV-2015-P1-Q27`
- `PYQ-CHEM-JEEADV-2015-P2-Q28`

### Some Basic Concepts of Chemistry / Mole Concept / Stoichiometry (19)

- `PYQ-CHEM-IITJEE-2007-P1-Q39`
- `PYQ-CHEM-IITJEE-2007-P1-Q40`
- `PYQ-CHEM-IITJEE-2007-P1-Q41`
- `PYQ-CHEM-IITJEE-2008-P2-Q51`
- `PYQ-CHEM-IITJEE-2011-P2-Q14`
- `PYQ-CHEM-JEEADV-2023-P1-Q08`
- `PYQ-CHEM-JEEADV-2025-P1-Q12`
- `PYQ-CHEM-JEEADV-2025-P2-Q16`
- `PYQ-CHEM-NEET-2020-E1-Q106`
- `PYQ-CHEM-NEET-2020-E1-Q110`
- `PYQ-CHEM-NEET-2020-E1-Q123`
- `PYQ-CHEM-JEEADV-2014-P1-Q39`
- `PYQ-CHEM-JEEADV-2016-P1-Q32`
- `PYQ-CHEM-JEEADV-2018-P1-Q08`
- `PYQ-CHEM-IITJEE-2009-P1-Q01`
- `PYQ-CHEM-IITJEE-2009-P1-Q04`
- `PYQ-CHEM-JEEADV-2015-P2-Q25`
- `PYQ-CHEM-JEEADV-2017-P1-Q26`
- `PYQ-CHEM-JEEADV-2026-P1-Q09`

## Provenance and source-status boundary

The JEE (Advanced) organizer archive is the authority for IIT-JEE/JEE Advanced paper identities, including the current 2026 organizer-hosted paper and final key. Legacy items keep their historical **IIT-JEE** identity. NEET (UG) 2020 items are backed by the NTA-hosted official question paper plus the NTA final key.

The existing donor registries remain discovery inputs only. Their `SOURCE_UNVERIFIED` population remains quarantined and is not counted in the accepted total. No authored question is inserted to make this matrix rectangular.

## Core2 / Core2A custody split

- exact historical identity and first-party parent locator live in `extensions["grade9v3:source_custody"]`;
- learner-facing wording is `origin: "ADAPTED"` / `PYQ_ADAPTED`;
- source hint custody is `hints[]`;
- authored graduated teaching support is `scaffolds[]`;
- full answer, reasoning route, crux move, rubric and independent check live under `answer`.

This prevents a restatement or authored hint ladder from being mistaken for verbatim Core2 source custody.
