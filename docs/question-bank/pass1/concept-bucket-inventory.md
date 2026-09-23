# Pass 1 concept-bucket inventory

Issue: #201

The expanded v2 bank reuses canonical Physics capabilities/families already present in the subject library. Chemistry still has no canonical subject-library package for the requested topics, so its identifiers remain local invariant-demand proposals inside the exam-bank namespace rather than being silently promoted globally.

## Physics — canonical reuse

| Pass-1 topic | Canonical bucket | Capability | Existing microtopic | Family | Decision |
| --- | --- | --- | --- | --- | --- |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-SECOND-LAW` | `MIC-PHY-NLM-SECOND-LAW` | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-FORCES-SUM-ZERO` | canonical capability | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-FRAME-CHOICE` | canonical capability | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-CONNECTED-COMMON-ACCEL` | canonical capability | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-FRICTION-QUANT` | `MIC-PHY-NLM-FRICTION-QUANT` | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-IDEAL-STRING-TENSION` | `MIC-PHY-NLM-IDEAL-STRING-TENSION` | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-2D-INDEPENDENT-COMPONENTS` | `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-2D-CONSTANT-ACCELERATION` | `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-PROJECTILE-MODEL` | `MIC-PHY-KIN-PROJECTILE-MODEL` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-SAME-TIME` | `MIC-SAME-TIME` | `FAM-RELATIVE-V` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-RELATIVE-V` | `MIC-COMMON-INTERVAL` | `FAM-RELATIVE-V` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-VECTOR-CHECK` | `MIC-GEOMETRIC-CHECK` | `FAM-RELATIVE-V` | REUSE |

### Physics scope notes

- The 2D bank excludes circular motion entirely.
- Straight-line relative motion reuses the existing relative-motion family; the relative-motion family now has three official-paper parent items, including a first-party JEE Main 2026 item; it remains the sparsest requested topic.
- No train/car/story-specific capability was created.

## Chemistry — local invariant-demand proposals

| Topic | Proposed bucket | Proposed capability | Invariant learner action | Status |
| --- | --- | --- | --- | --- |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-OXIDATION-STATE` | Assign and compare oxidation states using composition and charge constraints. | LOCAL_PROPOSAL |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-DISPROPORTIONATION` | Recognize simultaneous oxidation and reduction of the same element. | LOCAL_PROPOSAL |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-BALANCE-ELECTRON` | Balance electron inventories in the specified redox medium. | LOCAL_PROPOSAL |
| Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-MOLE-CONCENTRATION-TO-AMOUNT` | Convert concentration and sample volume into amount of substance. | LOCAL_PROPOSAL |
| Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-STOICH-MOLE-RATIO` | Map amounts through balanced stoichiometric or electron-transfer ratios. | LOCAL_PROPOSAL |
| Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-STOICH-MASS-MOLE` | Convert between amount and mass after reacting amount is established. | LOCAL_PROPOSAL |

### Proposed Chemistry families

| Family | Invariant application demand | Status |
| --- | --- | --- |
| `FAM-CHEM-REDOX-REACTION-CLASSIFICATION` | Classify or quantify a redox pattern from oxidation-state changes. | LOCAL_PROPOSAL |
| `FAM-CHEM-REDOX-ACIDIC-MEDIUM-BALANCE` | Balance electron inventories and map balanced coefficients to requested quantities. | LOCAL_PROPOSAL |
| `FAM-CHEM-MOLE-ELECTROLYTIC-STOICH` | Convert a shared solution inventory into electrolysis outputs. | LOCAL_PROPOSAL |
| `FAM-CHEM-STOICH-AMOUNT-MAPPING` | Carry amount through formula units, ion counts, yield, polymer units, hydrolysis or gas-generation stoichiometry. | LOCAL_PROPOSAL |

## Source hints versus authored support

The native repository distinction is preserved:

- `question.hints[]` is source/question custody. For the accepted 77 items no official hint ladder is supplied, so it remains empty.
- `question.scaffolds[]` is authored Core2A/Core2B pedagogical support. Each accepted record has a graduated scaffold ladder bound to stable `answer.reasoning_route[]` move IDs.

## Core2B transfer analysis

Transfer remains an analysis claim, not a generated practice set. Real-transfer candidates are flagged only where the demand changes materially, including:

- `PYQ-PHY-JEEADV-2020-P1-Q13` — multi-stage stick/slip reasoning with changing support reactions;
- `PYQ-PHY-IITJEE-2011-P2-Q33` — projectile event time plus accelerated relative displacement;
- `PYQ-PHY-JEEADV-2019-P2-Q09` — infinite rebound sequence requiring separate displacement/time series;
- `PYQ-PHY-JEEADV-2024-P2-Q09` — relative projectile motion removes common gravity;
- `PYQ-PHY-JEEADV-2014-P1-Q18` — competing free-particle versus finite-chamber interpretations;
- `PYQ-PHY-JEEADV-2023-P1-Q01` — energy, projectile impact and restitution across successive events;
- `PYQ-PHY-JEEADV-2025-P2-Q15` — linear drag changes the governing horizontal model;
- `PYQ-PHY-IITJEE-2009-P2-Q40` — accelerating-frame model choice introduces pseudo-force;
- `PYQ-PHY-IITJEE-2011-P2-Q26` — projectile timing must be coupled to collision momentum;
- `PYQ-PHY-JEEADV-2014-P1-Q11` — vector relative velocity plus a perpendicularity constraint;
- `PYQ-PHY-JEEADV-2026-P1-Q06` — prescribed-point projectile geometry plus apex-location reasoning;
- `PYQ-CHEM-JEEADV-2015-P2-Q28` — ligand and metal oxidation must be combined before permanganate balancing;
- `PYQ-CHEM-JEEADV-2023-P2-Q08` — half-reaction balancing plus two requested stoichiometric outputs;
- `PYQ-CHEM-JEEADV-2025-P2-Q16` — hydrolysis-water accounting before mass-fraction and integer composition constraints.

No final Core2B practice set is generated in PASS 1.


## JEE Main 2026 source diversification

The 2026 Session 2 additions reuse existing invariant-demand capabilities and families: `CAP-NLM-FRICTION-QUANT`, `CAP-KIN-2D-INDEPENDENT-COMPONENTS`, `CAP-RELATIVE-V`, `CAP-CHEM-REDOX-OXIDATION-STATE`, `CAP-CHEM-STOICH-MASS-MOLE`, `FAM-PHY-NLM-PRACTICE`, `FAM-PHY-KIN-2D-PRACTICE`, `FAM-RELATIVE-V`, `FAM-CHEM-REDOX-REACTION-CLASSIFICATION`, and `FAM-CHEM-STOICH-AMOUNT-MAPPING`. No car-, incline-, projectile-equation-, or transition-metal-story-specific capability was introduced.
