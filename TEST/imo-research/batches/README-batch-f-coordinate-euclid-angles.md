# IMO Grade 9 — Batch F coordinate geometry, Euclid and angle reasoning

**Sole IMO coordination:** [issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294), [owner next instruction relay #6074479863](https://github.com/reallaksh19/Grade9v3.5/issues/294#issuecomment-6074479863). **Research-only: no accepted source Core2, Core1A, QRT, publisher licence, original source bytes, official original full-paper answer key or learner release.** This is not a reproduction of SOF questions or an approved academic sequence.

**Exactly 10 printed/inventoried source positions:** `COORD` 4, `EUCLID` 3, `ANGLES` 3. Nine have prior agent-computed mathematical resolutions; **one official-sample angle diagram (Q5) is explicitly unresolved**. Every position has the original source ID, PDF URL, source-custody locator (including absent values), independent prior agent mathematical research pointer, provisional inference or explicit null, diagnostic hypothesis, figure dependency and hard rights/authority holds in the accompanying JSON.

| Distinct original source ID | Prior research audit | Original-specific inferred decision / known hold | Historic conflict |
|---|---|---|---|
| `SOF-IMO-G09-L1-2023-24-A-Q027` | `IMO-B02-004` | Line y-intercept: enforce x=0 first → (0,12) | — |
| `SOF-IMO-G09-L1-2023-24-A-Q050` | `IMO-B03-015` | Three coordinate models: y-axis reflection (-7,5), origin distance 5, quadrant III (-6,-3) | — |
| `SOF-IMO-G09-L1-2024-25-B-Q020` | `IMO-B02-008` | Abscissa 10 minus ordinate -4 = 14; signs and direction matter | — |
| `SOF-IMO-G09-L1-2025-26-A-Q046` | `IMO-B04-008` | Three coordinate transforms: x=3y+2 gives -10; additive inverse (0,0); x-axis reflection (4,-9) | — |
| `SOF-IMO-G09-L1-2023-24-A-Q033` | `IMO-B03-003` | Euclidean external point has exactly one parallel line (Playfair) | — |
| `SOF-IMO-G09-L1-2024-25-B-Q031` | `IMO-B02-013` | Euclid's third postulate is circle with arbitrary centre and radius | — |
| `SOF-IMO-G09-SAMPLE-2026-27-Q006` | `ORGANIZER-SAMPLE-6` | With P–Q–R–S and PQ=RS, segment addition gives PR=QS; sample key C sighted | — |
| `SOF-IMO-G09-L1-2023-24-A-Q019` | `IMO-B03-002` | Adjacent supplementary angle bisectors meet at 90°; four-right-angle rectangle | — |
| `SOF-IMO-G09-L1-2025-26-A-Q031` | `IMO-AUDIT-B01-009` | Source diagram a=84°, b=21°, c=48° vs owner's (57°,21°,48°) — historic conflict 007 | IMO-SOURCE-CONFLICT-007 |
| `SOF-IMO-G09-SAMPLE-2026-27-Q005` | `ORGANIZER-SAMPLE-5` | UNSOLVED original figure geometry; key C sighted, no checked independent derivation — historic conflict 009 | IMO-SOURCE-CONFLICT-009 |

## Geometry/proof branches, not a single “coordinate/angle” lesson

**Coordinate (4):** A point on the y-axis has `x=0` before solving any intercept; a y-axis reflection changes only `x`, whereas x-axis reflection changes only `y` and a point's additive inverse changes **both** signs. The origin distance of (3,4) is 5 (Pythagoras); distance to each axis is the **absolute** opposite coordinate, and quadrant III supplies both negative signs. Another original item asks a **directional** subtraction of abscissa and ordinate (`10−(−4)=14`). Separate these inferential moves rather than assigning a one-size-fits-all coordinate rule.

**Euclid (3):** Playfair's Euclidean parallel statement requires a point **outside the given line** and means **one and only one** parallel; Euclid's third postulate concerns drawing a circle with chosen centre and radius, not line extension or a common notion. Original organizer sample Q6 has a source-observed ordered straight-line figure `P–Q–R–S`; if `PQ=RS`, segment addition yields `PR=PQ+QR=QR+RS=QS`. The prior agent's suggested `QRT-JUSTIFY-D1` remains **PROPOSED and unaccepted**; it is not transferred into this research map as an approved QRT cell or canonical lesson.

**Angles (3):** Adjacent supplementary angles sum to 180°, so their bisectors form right angles. The prior agent used the source figure's parallel/bisector incidence to infer a rectangle from four right angles in 2023 A Q19, but no figure rights or complete original geometry custody are granted. Original 2025 A Q31 and organizer sample Q5 have **stronger unresolved source restrictions** described below.

## Historic conflict 007 — source vs owner is not an editorial typo to erase

2025–26 A Q31, source original PDF scan, agent derivation: `a=4b`, `a+b+75°=180°`, `2c=75°+b`. Thus `b=21°`, `a=84°`, `c=48°`, agent-selected printed **C**. Owner compilation claims **(57°,21°,48°)**, labelled **D**; notably `57+21+75=153≠180`. The historic source register case `IMO-SOURCE-CONFLICT-007` records a **FIGURE_DEPENDENT_ANSWER_DISAGREEMENT**. Before external academic acceptance, independently inspect exact original ray incidence, angle variables and complete printed options; an agent arithmetic proof based on interpreted image labels is not independent official custody. This draft does **not** alter either original ledger or owner's statement.

## Historic conflict 009 — original organizer sample Q5 remains UNSOLVED

The official sample prior audit for **Q5** reports `organizer_printed_key="C"`, but **`agent_derived_option=null`, `answer_meaning=null`, `source_mathematical_derivation=null`, `independent_check=null`**. Case `IMO-SOURCE-CONFLICT-009` is `UNSOLVED_FIGURE_GEOMETRY`; there is **no independent source-figure geometry proof**. The Batch F JSON deliberately retains nulls for independent answer, proof and protected decision. This is a source **review/hold**, not a completed mathematics solve or a proposed QRT cell. No source diagram is invented, copied or relabelled to make key C appear mathematically justified.

## 68-position denominator vs 66-position provisional topic map

The governed source-custody census has **68 distinct original source IDs**, but `TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl` currently lists only **66**. The two **real** census identities absent from that earlier taxonomy are **official organizer sample Q1 and Q3** (`SOF-IMO-G09-SAMPLE-2026-27-Q001` and `...Q003`), both classed `LOGIC` in the expanded census. Neither is fabricated, silently deleted or counted twice. Batch F maps ten existing identities only; by F completion A 8 + B 11 + C 12 + D 11 + E 8 + F 10 = **60/68 research-mapped**. A future separately authorized Batch G must reconcile **8 remaining distinct source IDs:** 2 CIRCLES + 4 LOGIC already topic-mapped + 2 census-only organizer-sample LOGIC positions. Any QRT or published original-source product still requires separate source custody and rights authorization.

## Exact research tests and hard scope

`tests/test_imo_batch_f_coordinate_euclid_angles.py` (Python standard-library-only) checks the full ten-ID taxonomy/census source join; all legacy math audit identities and any **null durable source locators**; exact conflicts 007/009; refusal to convert printed sample key C into a solved proof; math oracles for coordinate transformations and signed differences, Euclid's segment addition and third postulate, angle-bisector right angle and the competing original/owner figures; all zero Core2/QRT/Owner/rights/publication flags. CI status is PENDING until an actual exact-head run confirms it. Research mathematical success cannot cancel incomplete media custody or academic review.

No change to NCERT, Shared product framework/renderer, QRT vocabulary, original seed/answer records, independent Core architect's PR, existing authored practice, or other batches. **Stop after one Batch F draft PR and issue #294 handoff.**
