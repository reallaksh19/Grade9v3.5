# Chemistry master-suite audit — PR #144 extraction

Date: 2026-09-20  
Source reviewed: PR #144 (`feat/topic-atlas-skill-matrix-progress`)  
Repair branch: `audit/chemistry-master-suites-standalone`

## Decision on PR #144

PR #144 is not suitable for whole-branch merge. It is far behind current `main` and combines
Topic Atlas changes plus stale Motion-1D, Motion-2D and Vector Algebra implementations with four
Chemistry suites. The Chemistry work is therefore extracted onto current `main` and audited
independently.

The four extracted suites are:

- Chemical Bonding & Molecular Structure
- Some Basic Concepts of Chemistry / Mole Concept
- Redox Reactions
- Behaviour of Gases

Each suite retains 20 local diagnostic records, for 80 records total. Current local answer status is 79 PASS / 1 FAIL; source provenance remains a separate axis.

## Diagnostic answer audit

Local mathematical/chemical review status after extraction:

| Suite | PASS | PENDING | FAIL |
| --- | ---: | ---: | ---: |
| Chemical Bonding | 20 | 0 | 0 |
| Mole Concept | 19 | 0 | 1 |
| Redox | 20 | 0 | 0 |
| Behaviour of Gases | 20 | 0 | 0 |
| **Total** | **79** | **0** | **1** |

A local answer audit is not source-item verification. After live-source checks, 76 records remain
`SOURCE_PROVENANCE_PENDING` and 4 are explicitly `SOURCE_UNVERIFIED`: BOND-Q19,
CHEM02-Q04, GAS-Q01 and GAS-Q06.

### BOND-Q19 — local answer corrected; source attribution rejected

The PR #144 record supplied “Bond Order = 3.5 and Paramagnetic”. The local audit corrected the
standard classroom-MO answer to **Bond Order = 2.5 and Paramagnetic (Option B)**. The current
ExamSIDE listing for the claimed JEE Main 2019 Online 10 April Morning paper does not contain
this CO⁺ question, so `sourceAudit=SOURCE_UNVERIFIED` even though the local answer audit now
passes.

### CHEM02-Q04 — failed answer/data consistency and source mismatch

The stated eudiometry data are internally inconsistent with every listed option:

- KOH contraction = 40 mL ⇒ CO₂ = 40 mL ⇒ x = 4.
- Residual before KOH = 65 mL ⇒ excess O₂ = 25 mL.
- O₂ consumed = 80 - 25 = 55 mL.
- 10(4 + y/4) = 55 ⇒ y = 6.

Therefore the stated data imply **C₄H₆**, not C₄H₁₀. The record now has `answerAudit=FAIL`,
`correct=null`, and is withheld from scoring rather than silently selecting a wrong option.
The current ExamSIDE listing for the claimed 2026 Online 8 April Evening paper does not contain
this eudiometry item, so its source attribution is also `SOURCE_UNVERIFIED`.

## External-corpus snapshot

The live ExamSIDE topic pages were checked on 2026-09-20. They report:

| Topic | Live corpus count | Embedded local diagnostics |
| --- | ---: | ---: |
| Chemical Bonding & Molecular Structure | 266 | 20 |
| Some Basic Concepts of Chemistry | 245 | 20 |
| Redox Reactions | 74 | 20 |
| Gaseous State | 66 | 20 |

These numbers are corpus snapshot metadata, not claims that the local 20-item slices cover or
verify the full corpus. The Gaseous State page currently reports **0 questions in 2026** and marks
the chapter out of syllabus; therefore the PR #144 attributions GAS-Q01 and GAS-Q06 to 2026 JEE
Main papers are explicitly rejected as `SOURCE_UNVERIFIED`.

## Simulator-fidelity audit

The PR #144 pages displayed “Load in Simulator” for every record even when most `simParams`
were ignored by the loader. Several records also targeted tab IDs that did not exist.

The repair makes source→state bindings explicit through `simBindingRefs`. No Chemistry item
currently claims `EXACT`.

| Suite | CONSTRAINT_FAITHFUL | CONCEPT_ONLY |
| --- | ---: | ---: |
| Chemical Bonding | 17 | 3 |
| Mole Concept | 5 | 15 |
| Redox | 8 | 12 |
| Behaviour of Gases | 2 | 18 |

For constraint-faithful records, only parameters actually consumed by the governed loader remain
in `simParams`. Concept-only records inject no question-specific state.

Invalid target IDs repaired:

- Mole: `tab-mole-scale → tab-mole`
- Redox: `tab-structural → tab-structural-ox`
- Redox: `tab-balance → tab-ion-electron`
- Gases: `tab-andrews → tab-isotherms`
- Gases: `tab-halos → tab-real-particle`

## UI / Canvas RCA

All four PR #144 Chemistry pages inherited the same high-DPI canvas feedback defect later found
in Motion-1D and Vector Algebra: `setupCanvas()` read the mutable HTML `height` attribute and
then assigned a DPR-scaled `canvas.height`. On DPR > 1, repeated redraws could recursively grow
the logical height.

Repairs:

- cache original logical canvas height once in `dataset.logicalHeight`;
- measure logical width from the parent minus padding;
- cap DPR at 2;
- update backing-store dimensions only when necessary;
- use `ctx.setTransform(...)` instead of cumulative scaling;
- keep CSS width at 100%;
- redraw current state on resize.

Chemical Bonding also used multiple global mouse/touch orbit listeners. These are replaced with
per-canvas Pointer Events, pointer capture and one binding per canvas.

## Question-bank UI truthfulness

The blanket label **“ExamSIDE Verified Bank”** was removed. Question cards now expose:

- local answer-audit state;
- source provenance pending;
- simulator fidelity;
- a visible integrity failure banner if required fields, answer keys, target tabs or binding
  contracts are invalid.

Items with `answerAudit != PASS` are not scored.

## Duplicate-family curation debt

The current 20-item slices contain several near-duplicate diagnostic families. This is not a
runtime blocker, but future curation should prefer broader coverage before increasing counts.
Examples include BOND-Q04/BOND-Q12, CHEM02-Q05/MOLE-Q15, GAS-Q03/GAS-Q09,
GAS-Q07/GAS-Q16 and GAS-Q08/GAS-Q10.

## GCDR v1.3 suite contracts

The four Chemistry suites now participate in the companion-contract architecture introduced by
GCDR v1.3:

- `docs/gcdr-suites/chemistry-chemical-bonding.json`
- `docs/gcdr-suites/chemistry-mole-concept.json`
- `docs/gcdr-suites/chemistry-redox.json`
- `docs/gcdr-suites/chemistry-gaseous-state.json`

All four are explicitly `UNBOUND_EXTENSION` at `JEE_EXTENSION` depth; no Grade-9 canonical
certification is claimed. The contracts govern the 20-item local slice, helper activation,
representation invariants, geometry-truth declaration, and both repo/standalone delivery profiles.

Question records now expose `teacherCheck`, `takeaway`, `helperTags`,
`simBindingRefs`, answer audit, source audit and simulator fidelity. The five item-driven helpers
used by these pages are governed as `AUDITED` against
`tests/test_chemistry_master_suites_audit.py`.

The suite-level invariants are:

- Chemical Bonding — MO bond-order / magnetic-state consistency;
- Mole Concept — stoichiometric extent and limiting-reagent conservation;
- Redox — oxidation/reduction electron balance and n-factor consistency;
- Gaseous State — Maxwell characteristic-speed ordering and analytic ratios.

Rendered geometry remains `DECLARED`, not browser/visual certified.

## Standalone delivery

Four standalone artifacts are committed:

- `standalone/chemistry-chemical-bonding-master-suite.html`
- `standalone/chemistry-mole-concept-master-suite.html`
- `standalone/chemistry-redox-reactions-master-suite.html`
- `standalone/chemistry-behaviour-of-gases-master-suite.html`

Each embeds its 20-record bank and has no repository-local runtime/data dependency. They are
**SINGLE_FILE_ONLINE**, not offline artifacts: Tailwind and KaTeX remain CDN dependencies.

## Release limitations

This audit provides static/data/math review and CI falsifiers. It does not claim:

- source-item verification for the 80 attributed ExamSIDE labels;
- full external-corpus coverage;
- offline delivery;
- browser visual proof until a real browser smoke test is completed.

## Redox follow-up: scientific-content + Grade-9 pedagogy audit (2026-09-20)

A second, content-first audit was performed after the initial packaging audit. This review used
GCDR v1.3's mandatory sequence (predict → manipulate/observe → reconstruct → transfer) and checked
the redox explanations against the formal oxidation-state model rather than treating the task as
a canvas-only repair.

### Root runtime defect

The Redox page read `currentCompound` and `currentStructMode` during the load sequence but never
initialized either variable. The first `updateStructuralLedger()` call could therefore throw a
`ReferenceError`, aborting subsequent canvas initialization. Both variables are now explicitly
initialized, and the first learner route is the new Foundations tab.

### Canvas-content defect

Five canvas tabs were syntactically valid but only painted a single line of text. They were
placeholders, not graphical cognitive deconstructions. The follow-up replaces them with:

- a prediction-first Zn/Cu electron-transfer scene;
- a donor/acceptor electron-flow diagram;
- a four-stage ion-electron balancing ledger;
- a redox-titration electron-equivalence diagram;
- a Daniell-cell electron/salt-bridge diagram;
- an oxidation-number ladder practice view.

Every canvas also has an accessible label and a visible text invariant, so the concept does not
depend solely on pixel rendering.

### Scientific-model corrections

The previous copy repeatedly described oxidation states as "physical reality", "real localized
charges", or asserted that fractional oxidation states are physically impossible. Those claims
were removed. The suite now treats oxidation state as formal electron bookkeeping based on an
ionic approximation of bonds. Mixed-valence examples distinguish a formula-average value from a
structure-supported formal assignment without equating either with measured atomic charge.

Specific repairs include:

- CrO5 / peroxo acids: the error is now identified as ignoring O-O peroxide connectivity, not as
  violating a simplistic valence-electron ceiling.
- S4O6(2-): +2.5 is presented as the formula average; +5,0,0,+5 is the requested structural formal
  assignment, with a whole-ion charge check.
- Fe3O4 and Pb3O4: mixed-valence formal descriptions are separated from literal charge language.
- Brown-ring complex: the JEE Fe(I)/NO+ convention is retained for the attributed item, but the
  Chalkboard now discloses nitrosyl non-innocence and the more robust {FeNO}7 description.
- Na2S2O3 titration: electron transfer is checked from the balanced thiosulfate/tetrathionate
  half-reaction instead of a misleading average-sulfur shortcut.
- Bleaching powder: the Ca(OCl)Cl representation is explicitly identified as the textbook/JEE
  idealization.

### Pedagogy/order corrections

The page previously opened on structural exceptions (CrO5, tetrathionate, magnetite) before a
young learner had a causal model of redox. A new **Grade 9 Bridge** now precedes the JEE material:

1. predict the electron donor;
2. reveal Zn → Cu2+ electron transfer;
3. label oxidation/reduction from electron loss/gain;
4. connect donor/acceptor to reducing/oxidizing agent;
5. only then introduce oxidation-number bookkeeping.

The overall suite contract remains `UNBOUND_EXTENSION / JEE_EXTENSION`; the foundation tab is a
bridge, not a new Grade-9 certification claim.

### Feedback and disclosure corrections

A wrong MCQ click previously highlighted the correct option immediately, collapsing diagnosis,
hinting and repair into one reveal. Wrong attempts now keep the answer hidden, give
distractor-specific process feedback when available, and leave the Teacher Chalkboard as an
explicit repair action. Generic independent-check and transfer boilerplate was replaced across all
20 redox records with task-specific checks and reusable decision rules.

Source provenance status is unchanged: local answer/content review does not convert the attributed
ExamSIDE labels into verified source records.



## Redox adaptive visual-builder proof: 50% entry, hard concept + implementation (2026-09-20)

A separate proof page was added at \`public/chemistry/redox/explorers/redox_reactions/adaptive-hard-concept-proof.html\` (plus a standalone copy) to test the proposed adaptive model without destabilising the audited master suite.

The proof deliberately assumes a rough 50% knowledge estimate only as an entry coordinate. It does not mark foundations mastered and does not create canonical Chemistry evidence because the Redox suite remains \`UNBOUND_EXTENSION / JEE_EXTENSION\`.

It tests three hard conceptual pivots:

1. CrO5 structural oxidation-state exception: formula-only blanket rules versus peroxide connectivity, followed by charge-ledger implementation.
2. Reaction-dependent permanganate n-factor: medium/product -> final Mn oxidation state -> electron uptake, followed by n-factor implementation.
3. FeC2O4/dichromate electron equivalence: count both Fe and oxalate electron donation, followed by stoichiometric electron matching.

Each block has two separate demands (concept model choice and implementation), up to three staged visual hints, and one coarse session outcome:

- both first attempts correct with no help -> READY;
- mixed performance or any help -> REINFORCE;
- both first attempts incorrect -> REBUILD.

This is intentionally a falsifiable UI proof rather than a canonical router. It does not perform per-click misconception classification, does not persist READY/REINFORCE/REBUILD as learner evidence, and does not replace the generic Core/Atlas work tracked in issues #159 and #160.


## Redox full ExamSIDE content map (2026-09-20)

The master page now contains a first-class ExamSIDE content map rather than only the 50% adaptive proof.

- Live corpus snapshot remains 74 JEE Main Redox positions: 29 Numerical and 45 single-correct MCQ.
- All 74 positions are mapped once to a primary subtopic-local learning track: oxidation-state model, redox roles/classification, disproportionation, half-reaction balancing, reaction-dependent n-factor, electron equivalence, redox titration, or an explicitly adjacent equivalents/acid-base bucket.
- The 20 locally audited questions are mapped to the same tracks and remain explicitly SOURCE_PROVENANCE_PENDING; pedagogical mapping is not represented as source verification.
- REDOX-Q08, REDOX-Q16 and REDOX-Q19 are now visibly marked as Electrochemistry extension / off the live ExamSIDE Redox corpus because ExamSIDE maintains Electrochemistry as a separate topic.
- The page opens on the ExamSIDE Content Map, from which the learner can open the mapped visual or jump to any local audited item.
- Regression tests require exactly 74 unique corpus refs, the 29/45 type split, complete 20-item local mapping, expected track counts, and standalone/public map parity.

The subject-specific map data is embedded in the Redox page (and standalone copy) rather than placed in a public `.js` engine file; this preserves the repository topic-independence guard.


## Redox hover previews + 14-question oxidation bookkeeping lab (2026-09-20)

The ExamSIDE map now supports pointer hover, keyboard focus and touch/click previews for every one of the 74 corpus references. Every corpus row has a non-empty paraphrased question preview; touch pins the tooltip and outside click/Escape closes it.

The Oxidation-State / Structural Exceptions page now contains all 14 live corpus positions mapped to that track:
`N08, N12, N15, N16, N17, N18, N25, N29, M04, M26, M28, M29, M33, M35`.

Each item has:
- a concise source-derived question prompt;
- an explicit visual-flow bridge identifying the representation that matters;
- a written explanation of why that visual applies;
- a multi-step derivation;
- a derived result shown only after the reasoning section;
- a caveat where the formal model needs qualification (for example the brown-ring nitrosyl formalism).

The 74 tooltip previews are paraphrases of the live ExamSIDE index snapshot rather than verbatim corpus reproduction. Some non-OS source prompts contain rendered chemical notation not recoverable as machine text from the index; those previews describe the task without inventing missing notation.


## Redox tooltip placement, equation workbench and in-tab banks (2026-09-20)

Three learner-facing issues from screenshot review were corrected:

1. **Question-preview overlay:** the tooltip is now fully opaque, narrower, uses a high top-layer z-index, and prefers placement to the right or left of the hovered/touched reference before falling back above/below. This prevents the translucent text collision visible in the prior implementation. Hover, focus, touch pinning, outside-click close and Escape remain supported.
2. **Dedicated equation representation:** the oxidation-bookkeeping page now has a reusable interactive Equation Workbench. Any of the 14 mapped oxidation-state PYQs can load its own staged ledger into one canvas; Prev/Next/Reset reveal the derivation incrementally rather than duplicating fourteen static diagrams.
3. **Question banks inside learning tabs:** Electron Conveyor, Ion-Electron Balance, n-factor/disproportionation, Titration/equivalence and Electrochemistry Extension now surface their mapped question banks directly in the respective page. The first four use live ExamSIDE corpus mappings; Electrochemistry shows the three local off-corpus extension items.


## Redox in-tab question completion + corpus correction (2026-09-20)

Screenshot review showed that the learner-facing non-oxidation tabs were still only mapped-question indexes. They now use a common teaching-card contract:

```
question
  -> reasoning checkpoint
  -> reviewed derivation
  -> derived result
```

Coverage added for every live ExamSIDE position assigned to the visible core learning tabs:
- ROLE: 16
- BAL: 4
- NFACTOR: 5
- DISP: 9
- EQUIV: 6
- TITR: 8

Total new in-tab helpers: **48**.

Together with the existing 14 oxidation-state helpers, all **62 live Redox-corpus questions assigned to core learner tabs** now have a rich helper surface. The remaining 12 `RELATED` positions remain explicitly adjacent equivalent/acid-base material visible in the corpus map rather than being silently presented as core Redox teaching content.

The three local Electrochemistry extension questions now also render their existing local `steps[]` and `ans` inside the Electrochemistry tab. Their source provenance remains `SOURCE_PROVENANCE_PENDING`; local answer audit must not be misrepresented as exact ExamSIDE provenance.

### Corrected mapping defect

`N13 · 2023` had accidentally inherited the `N15` Fe(CO)₅ / VO²⁺ / WO₃ oxidation-state preview. Live ExamSIDE identifies N13 as the dichromate/Fe²⁺ balancing numerical. The corpus preview is corrected to:

`Cr₂O₇²⁻ + XH⁺ + 6Fe²⁺ → YCr³⁺ + 6Fe³⁺ + ZH₂O`

with the reviewed derivation `X=14, Y=2, Z=7`, hence `X+Y+Z=23`.

Regression tests now require:
- exactly 48 non-OS core helper refs matching the corpus mapping;
- non-empty bridge, derivation and answer for every helper;
- N13 remains BAL and cannot contain the N15 Fe(CO) preview;
- N15 remains OS;
- public/standalone helper parity.


## Redox checkpoint vs visual semantics correction (2026-09-20)

A learner-facing wording audit found that the non-OS teaching cards labelled procedural reasoning as a `VISUAL / METHOD BRIDGE`. This was semantically wrong: instructions such as

`identify product -> compute ΔO.S. -> convert to electrons -> read n-factor`

are **reasoning checkpoints**, not drawable canvas states.

The 48 non-OS helper records now use `checkpoint`, not `bridge`, and the learner UI labels the block **REASONING CHECKPOINT**.

Separation:

```
VISUAL / SCENE
  what can actually be shown or manipulated

CHECKPOINT
  what the learner must decide/verify before proceeding

DERIVATION
  the explicit scientific/mathematical reconstruction

RESULT
  the derived answer
```

For n-factor the checkpoint is now:

`First identify the actual reduction/oxidation product in the stated medium. Compare the initial and final oxidation states, convert |ΔO.S.| into electron count, and only then determine n-factor or equivalent mass.`

A checkpoint may reference or trigger a canonical visual, but it is not itself required to be visualizable.

Regression coverage now rejects the obsolete `bridge` field in these helper records and rejects the `VISUAL / METHOD BRIDGE` learner label.
