# IMO Grade 9 — Batch E: original-source statistics and probability research

**Sole coordination:** [IMO issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294), [next-batch instruction relay #6074404830](https://github.com/reallaksh19/Grade9v3.5/issues/294#issuecomment-6074404830). **Status:** `RESEARCH_ONLY`; original source component custody, independent academic acceptance, publisher reuse rights, original source Core2, QRT admission and product publication all remain **NOT_GRANTED**. This file is a research design map, not a learner question bank.

**Batch E:** 8 original inventoried positions = 4 `STATISTICS` + 4 `PROBABILITY`. It follows producer source mapping A=8, B=11, C=12, D=11; if validated, cumulative source research mapping becomes **50/68**, leaving **18 source identities** for F–G and unresolved taxonomy/custody reconciliation. Seven earlier authored practice candidates are separate, as is the recent original Core2A R1 candidate.

## Source positions, crux and prior mathematical evidence

| Stable original ID | Existing agent audit | Protected source math (provisional) | Registered discrepancy |
|---|---|---|---|
| `SOF-IMO-G09-L1-2024-25-B-Q016` | `IMO-AUDIT-B01-004` | Pie sectors: recover a shared population from 35% = 140, then English 15% = 60 | IMO-SOURCE-CONFLICT-004 |
| `SOF-IMO-G09-L1-2025-26-A-Q032` | `IMO-AUDIT-B01-010` | Convert two sector angles 70° + 55° out of 360° into 250 of 720 marks | IMO-SOURCE-CONFLICT-008 |
| `SOF-IMO-G09-L1-2025-26-A-Q033` | `IMO-AUDIT-B01-011` | Find missing 80° sector, then 200/9% (22 2/9%) | IMO-SOURCE-CONFLICT-008 |
| `SOF-IMO-G09-L1-2025-26-A-Q047` | `IMO-B04-009` | Three independent matches: midpoint class bound 5, range 75, scale length 20 cm | — |
| `SOF-IMO-G09-L1-2023-24-A-Q025` | `IMO-B02-003` | Survey complement: 150 private of 400, probability 3/8 | — |
| `SOF-IMO-G09-L1-2023-24-A-Q040` | `IMO-B03-010` | Equally likely black balls: 5 of 12, not one of three colour labels | — |
| `SOF-IMO-G09-L1-2024-25-B-Q027` | `IMO-B02-011` | Two fair dice: six ordered favourable outcomes out of 36, 1/6 | — |
| `SOF-IMO-G09-L1-2025-26-A-Q043` | `IMO-B04-005` | Inclusive 51–100 cards: 50 total, ten primes, 4/5 nonprime | — |

**Evidence distinctions, not admissions:** Each JSON record points to one pre-existing source audit B01/B02/B03/B04 and keeps its original source/question and owner-compilation IDs, source URL, math-computed answer/option, candidate crux, independent check, figure status and rights hold. Printed answer labels in the prior calculations **are not authenticated publisher full-paper keys**. An earlier agent's printed page sighting does **not** upgrade a null durable-custody locator: five Batch E positions have missing source-census observed page/number information and retain that absence explicitly, with separate prior math-audit page observations.

## Historic source discrepancy 004: pie-chart figure custody

2024–25 B Q16 uses two different labelled sectors of the **original** chart. A Mathematics sector marked 35% alongside 140 students implies total 400; the English 15% sector then represents 60. Owner's textual sector reconstruction does not preserve the published chart asset itself. `IMO-SOURCE-CONFLICT-004` remains **SOURCE_CHART_DEPENDENCY / SOURCE_FIGURE_CUSTODY_PENDING**: don't replace the authentic scan diagram with text under an unearned fidelity claim. A new *authored* semantic chart can be constructed later as pedagogical support but is not source provenance or publisher reuse permission.

## Historic source discrepancy 008: one chart, two printed questions

2025–26 A original printed **Q32** and **Q33** share a pie chart but are **two original source positions**. Owner's single compilation entry 38 with `i`/`ii` is not an official one-position merge. These tasks have **different reasoning demands**: Q32 aggregates Hindi + Social Science labelled sectors (70° + 55°) to get 250 marks from 720; Q33 finds an omitted Mathematics sector (80°) by angle complement and then computes `80/360×100=200/9%=22 2/9%`. They must retain distinct IDs and audit records, with a shared unlicensed-figure dependency. `IMO-SOURCE-CONFLICT-008` is a **printed-source split/owner compilation combining issue**, not incorrect probability arithmetic.

## Four distinct probability event models

1. **Survey categorical complement (2023 A Q25):** identify the entire 400-person equally likely selection space and private count `400−250=150`; `P=3/8`. The 250 government employees are not the requested event.
2. **Bag draw (2023 A Q40):** twelve equiprobable individual balls (3 red, 5 black, 4 white), yielding black `5/12` rather than one-third for three colours.
3. **Two fair dice (2024 B Q27):** 36 **ordered** outcomes and six with sum *strictly greater* than 9; `P=1/6`. The outcomes `(4,6)` and `(6,4)` are separate elementary cases.
4. **Nonprime card complement (2025 A Q43):** inclusive interval `51..100` holds **50 distinct cards**, ten prime-labelled cards, hence `40/50=4/5`. Neither the 49-count end-point error nor counting all odds as prime is valid.

These share some basic fractional vocabulary but need not have the same Core1A intervention. No lesson-per-source-item quota is asserted; each possible learner misconception is an **unobserved hypothesis**, not measured learner performance.

## Three independent statistical matches (2025 A Q47)

The source matching task deliberately switches objects: `class mark 10` plus upper class bound 15 yields lower bound **5**; range is **93−18=75**; and graph scale `0.4 cm per 50 people` maps 2,500 people to **20 cm**. Prior agent audit B04-009 maps P→(ii), Q→(iii), R→(i). It would be a teaching error to flatten all three into one pie-chart question merely because their provisional primary topic is `STATISTICS`. Publisher source text/columns remain research-reference only.

## Tests, holds and handoff

`tests/test_imo_batch_e_statistics_probability.py` independently checks all eight source taxonomy/census joins, prior audit row integrity and separate page-locator authority, all eight mathematical witnesses, exact historic conflicts 004/008, the original Q32/Q33 split, source-chart reuse refusal and zero rights/Core/QRT/publisher admission flags. Source-only tests use **standard-library Python** (no extra renderer or `jsonschema` dependency). Source-only workflow evidence must be read on the **exact PR head**, not inferred from green older runs.

**No new Core construction or QRT cell; no original SOF stem, figure or PDF bytes; no direct edit to Core architect PRs, source seeds, accepted library or NCERT.** Any correct provisional mathematics still requires retained source bytes/digests, authentic seven-component item checks, academic review, official key authority and reuse rights before an original Core2 could ever be considered.
