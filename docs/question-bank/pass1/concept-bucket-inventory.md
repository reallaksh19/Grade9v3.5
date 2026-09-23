# Pass 1 concept-bucket inventory

Issue: #201

The inventory reuses canonical Physics capabilities/microtopics already present on `main`. Chemistry currently has no canonical subject-library package for the two requested topics, so its entries remain **local proposals** inside the exam-bank namespace and are not silently promoted into the global capability namespace.

## Physics — canonical reuse

| Pass-1 topic | Canonical bucket | Capability | Existing microtopic | Family | Decision |
| --- | --- | --- | --- | --- | --- |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-SECOND-LAW` | `MIC-PHY-NLM-SECOND-LAW` | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-FRICTION-QUANT` | `MIC-PHY-NLM-FRICTION-QUANT` | `FAM-PHY-NLM-INCLINE-MODELLING` | REUSE |
| Newton's Laws of Motion / NLM | `BUCKET-PHY-NLM-FIRST-LAW` | `CAP-NLM-IDEAL-STRING-TENSION` | `MIC-PHY-NLM-IDEAL-STRING-TENSION` | `FAM-PHY-NLM-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-2D-INDEPENDENT-COMPONENTS` | `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-2D-CONSTANT-ACCELERATION` | `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 2D — linear/projectile only | `BUCKET-PHY-KIN-2D-MOTION` | `CAP-KIN-PROJECTILE-MODEL` | `MIC-PHY-KIN-PROJECTILE-MODEL` | `FAM-PHY-KIN-2D-PRACTICE` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-SAME-TIME` | `MIC-SAME-TIME` | `FAM-RELATIVE-V` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-RELATIVE-V` | `MIC-COMMON-INTERVAL` | `FAM-RELATIVE-V` | REUSE |
| Motion in 1D — relative motion only | `BUCKET-RELATIVE-MOTION` | `CAP-VECTOR-CHECK` | `MIC-GEOMETRIC-CHECK` | `FAM-RELATIVE-V` | REUSE |

### Physics scope notes

- The 2D bank excludes circular-motion demands entirely. No circular-motion capability or family is added.
- Straight-line relative motion reuses the existing general relative-motion capability family rather than creating train/car/story-specific capability IDs.
- No new Physics family was required by the accepted questions in this pass.

## Chemistry — local invariant-demand proposals

| Topic | Proposed bucket | Proposed capability | Invariant learner action | Status |
| --- | --- | --- | --- | --- |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-OXIDATION-STATE` | Assign and compare oxidation states using composition and charge constraints. | LOCAL_PROPOSAL |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-DISPROPORTIONATION` | Recognize when the same element in one reactant is simultaneously oxidized and reduced. | LOCAL_PROPOSAL |
| Redox Reactions | `BUCKET-CHEM-REDOX-REACTIONS` | `CAP-CHEM-REDOX-BALANCE-ELECTRON` | Balance oxidation and reduction electron inventories in the specified reaction medium. | LOCAL_PROPOSAL |
| Some Basic Concepts / Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-MOLE-CONCENTRATION-TO-AMOUNT` | Convert concentration and sample volume into amount of substance. | LOCAL_PROPOSAL |
| Some Basic Concepts / Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-STOICH-MOLE-RATIO` | Map amounts through a balanced stoichiometric or electron-transfer ratio. | LOCAL_PROPOSAL |
| Some Basic Concepts / Mole Concept / Stoichiometry | `BUCKET-CHEM-MOLE-STOICHIOMETRY` | `CAP-CHEM-STOICH-MASS-MOLE` | Convert between amount and mass after the reacting amount has been established. | LOCAL_PROPOSAL |

### Proposed Chemistry families

| Family | Invariant application demand | Why it is not story-specific |
| --- | --- | --- |
| `FAM-CHEM-REDOX-REACTION-CLASSIFICATION` | Classify a redox pattern by oxidation-state changes. | The family is keyed to a reusable model/operation, not to phosphorus, permanganate, NaCl, an electrode material, or any other surface story. |
| `FAM-CHEM-REDOX-ACIDIC-MEDIUM-BALANCE` | Balance an acidic-medium redox reaction and count transferred electrons/products. | The family is keyed to a reusable model/operation, not to phosphorus, permanganate, NaCl, an electrode material, or any other surface story. |
| `FAM-CHEM-MOLE-ELECTROLYTIC-STOICH` | Convert solution amount into electrolysis stoichiometric outputs using one shared reacting inventory. | The family is keyed to a reusable model/operation, not to phosphorus, permanganate, NaCl, an electrode material, or any other surface story. |

## Core2B transfer distinction

The bank stores a `transfer_profile` on every accepted item with four explicit dimensions: `model_choice`, `representation_translation`, `novelty`, and `reasoning_steps`. A different number set, exam year, or surface story is not sufficient for `REAL_TRANSFER_CANDIDATE`.

Current real-transfer candidates are:

- `PYQ-PHY-IITJEE-2011-P2-Q33`: projectile timing must be reconciled with accelerated observer/train displacement.
- `PYQ-CHEM-JEEADV-2023-P2-Q08`: acidic-medium electron balancing must be converted into both product amount and transferred-electron count.

This is analysis metadata only; no Core2B practice asset or final set is created in Pass 1.
