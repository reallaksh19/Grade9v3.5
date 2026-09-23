# Pass 1 competitive-exam coverage matrix

Issue: #201  
Scope: question-bank custody only; no practice sets or exams.

## Active bank

The active expanded bank is the fixture-native v2 custody surface:

- `Physics/library/exam-bank/competitive-exam-question-bank.v2.json`
- `Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json`

The superseded 8-question v1 bank files have been removed. The v2 custody manifests are the sole active exam-bank truth under the subject libraries.

All 30 learner-usable v2 records are `PYQ_ADAPTED`: the parent exam identity is source-verified against the official organizer archive, while the stored stem/options/conditions are explicitly faithful non-verbatim restatements. Source-provided hint ladders remain in `question.hints[]` (empty for this accepted set); authored teaching support is kept separately in `question.scaffolds[]`.

## Topic totals

| Topic / bucket | Accepted v2 items | D1 | D2 | D3 | D4 | Relative/source status |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| `BUCKET-PHY-NLM-FIRST-LAW` | 7 | 0 | 4 | 2 | 1 | Source-matched |
| `BUCKET-PHY-KIN-2D-MOTION` | 6 | 0 | 2 | 4 | 0 | Source-matched; circular motion excluded |
| `BUCKET-RELATIVE-MOTION` | 2 | 0 | 1 | 1 | **Previous acquisition hold closed** |
| `BUCKET-CHEM-REDOX-REACTIONS` | 7 | 2 | 4 | 1 | 0 | Source-matched |
| `BUCKET-CHEM-MOLE-STOICHIOMETRY` | 8 | 0 | 7 | 1 | 0 | Source-matched |
| **TOTAL** | **30** | **2** | **18** | **9** | **1** | No authored fill |

## Accepted IDs by topic

### Physics — Newton's Laws of Motion / NLM (7)

- `PYQ-PHY-IITJEE-2007-P1-Q03`
- `PYQ-PHY-IITJEE-2007-P1-Q10`
- `PYQ-PHY-IITJEE-2008-P2-Q33`
- `PYQ-PHY-IITJEE-2011-P1-Q41`
- `PYQ-PHY-IITJEE-2011-P2-Q34`
- `PYQ-PHY-JEEADV-2014-P2-Q19`
- `PYQ-PHY-JEEADV-2020-P1-Q13`

### Physics — Motion in 2D, linear/projectile only (6)

- `PYQ-PHY-IITJEE-2011-P2-Q33`
- `PYQ-PHY-JEEADV-2018-P2-Q08`
- `PYQ-PHY-JEEADV-2019-P2-Q09`
- `PYQ-PHY-JEEADV-2021-P1-Q05`
- `PYQ-PHY-JEEADV-2021-P1-Q06`
- `PYQ-PHY-JEEADV-2024-P2-Q09`

### Physics — Motion in 1D, relative motion only (2)

- `PYQ-PHY-IITJEE-2008-P2-Q32`
- `PYQ-PHY-JEEADV-2014-P1-Q18`

### Chemistry — Redox Reactions (7)

- `PYQ-CHEM-IITJEE-2008-P1-Q66`
- `PYQ-CHEM-IITJEE-2011-P1-Q17`
- `PYQ-CHEM-IITJEE-2011-P1-Q18`
- `PYQ-CHEM-IITJEE-2012-P2-Q22`
- `PYQ-CHEM-JEEADV-2023-P2-Q08`
- `PYQ-CHEM-JEEADV-2024-P2-Q02`
- `PYQ-CHEM-JEEADV-2025-P1-Q08`

### Chemistry — Mole Concept / Stoichiometry (8)

- `PYQ-CHEM-IITJEE-2007-P1-Q39`
- `PYQ-CHEM-IITJEE-2007-P1-Q40`
- `PYQ-CHEM-IITJEE-2007-P1-Q41`
- `PYQ-CHEM-IITJEE-2008-P2-Q51`
- `PYQ-CHEM-IITJEE-2011-P2-Q14`
- `PYQ-CHEM-JEEADV-2023-P1-Q08`
- `PYQ-CHEM-JEEADV-2025-P1-Q12`
- `PYQ-CHEM-JEEADV-2025-P2-Q16`

## Provenance and source-status boundary

The official JEE (Advanced) past-paper archive is the primary authority for this expanded pass. Legacy papers retain their historical **IIT-JEE** identity; 2014+ records use **JEE (Advanced)**.

The existing donor registries remain discovery inputs only. Their `SOURCE_UNVERIFIED` population remains quarantined and is not counted in the 30 accepted v2 records. No authored question was inserted to make this matrix rectangular.

## Core2 / Core2A custody split

The v2 shape follows the repository's source-ingest and native question fixtures:

- exact historical identity and official parent locator live in `extensions["grade9v3:source_custody"]`;
- the learner-facing restatement is marked `origin: "ADAPTED"` and `PYQ_ADAPTED`;
- source hint custody is `hints[]`;
- authored graduated teaching support is `scaffolds[]`;
- full answer, reasoning route, crux move, rubric and independent check live under `answer`.

This prevents the previous error of treating a prose summary or an authored hint ladder as verbatim Core2 source custody.
