# ISS69 PHASE-B — B02.4/B02.5 subject symmetry and runtime-branch scan

Material basis: `fix/iss69-phase-b-subject-neutrality`

## B02.4 — Mathematics/Physics symmetry check

Targeted Shared scans were run for polynomial/root-bound, projectile/kinematic, VSEPR/allene/torsion/orbital-basis terms.

### Findings

| Shared hit | Classification | Disposition |
| --- | --- | --- |
| `Shared/tools/build_resource_registry.py` subject/topic keyword markers | CATALOG/DISCOVERY | NO_CHANGE. Used to classify/register resources, not to prescribe learner reasoning. |
| `Shared/tools/build_learner_ui.py` titles/descriptions for subject resources | PORTAL CONTENT | NO_CHANGE. Learner navigation/catalog copy, not Core blueprint policy. |
| `Shared/policy/grade9-physics.v1.json` physics curriculum concepts | SUBJECT POLICY DATA | NO_CHANGE. Explicitly a Physics policy record, not generic Core pedagogy. |
| `Shared/assurance/typed.py` projectile/kinematics model functions | TYPED ASSURANCE MODEL | NO_CHANGE in this responsibility. These are named mathematical model validators, not subject-conditional Core rendering rules. |
| `Shared/web/standalone-ledger.v1.json` named standalone artifacts | ARTIFACT LEDGER | NO_CHANGE. Historical/governed artifact metadata. |
| `Shared/tools/topic_independence_allowlist.json` polynomial stress evidence path | HISTORICAL EVIDENCE ALLOWLIST | NO_CHANGE. It explicitly labels stress-test evidence as historical rather than engine authority. |

No polynomial/root-bound or motion/kinematics repair prescription analogous to the former Chemistry SOLUTION_STEPS block remains in the active Core1A/Core2 blueprint authority.

## B02.5 — Shared runtime academic subject-conditional scan

Inspected:
- `Shared/tools/render_core.py`
- `Shared/tools/core2_v2.py`
- `Shared/tools/learning_repair.py`
- `Shared/tools/quality_gate.py`
- `Shared/tools/question_review_matrix.py`
- `Shared/tools/question_difficulty.py`
- `Shared/tools/web_blueprint_contract.py`
- `Shared/tools/core_template_contract.py`

### Findings

`render_core.py`
- subject names are used to build portal navigation links;
- current-vs-prerequisite subject identity is used to label cross-subject prerequisite links;
- subject slug is used to resolve subject landing-page navigation.
- **No Chemistry/Mathematics/Physics branch selects different Core1A/Core2 academic content, support depth, diagnosis rule, or reasoning route.**

`core2_v2.py`
- no subject-name or subject-conditional branch found.

`learning_repair.py`
- no subject-name or subject-conditional branch found.

`quality_gate.py`
- “Physics” appears only in command-line usage documentation; no subject-specific academic gate branch found.

`question_review_matrix.py`
- the set `("Physics", "Chemistry", "Mathematics")` validates that the loaded adapter declares one of the supported subjects.
- demand keys must still equal the canonical seven-demand vocabulary.
- this is adapter identity/schema validation, not subject-specific QRT-cell invention or learner-product branching.

`question_difficulty.py`, `web_blueprint_contract.py`, `core_template_contract.py`
- no subject academic branching found.

## Decision

**NO_CHANGE** for B02.4 and B02.5.

The recovery invariant is not “Shared can contain no subject names.” Shared may enumerate supported subjects, navigate to subject resources, validate adapter identity, or host explicitly typed domain validators. The prohibited pattern is a subject name controlling generic Core1A/Core2 pedagogy, QRT meaning, support depth, diagnostic truth, or renderer anatomy. No such branch was found in this bounded scan.
