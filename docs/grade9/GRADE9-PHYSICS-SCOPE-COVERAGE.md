# Grade-9 Physics scope coverage audit

> Status: **derived audit**
>
> Roadmap basis: **RM-0006 / EP-TA-004**
>
> Material basis: `43f1321839f259a882b07a3189495ca372cb3abf`
>
> Machine-readable companion: `docs/grade9/grade9-physics-scope-coverage.json`

## Purpose

This is the consolidated scope boundary for the current Grade-9-first programme. It answers a narrower question than “what Physics exists in the repository?”:

> Which current Physics matrices are ordinary Grade-9 core, true support/prerequisite, bounded real-question preparation, declared extension, or later/broader material?

It does **not** create curriculum authority, learner mastery state, or a new grade field. The canonical matrix contract remains unchanged.

## Result

All **20** current Physics matrices are accounted for exactly once at matrix level:

- **6 required core** — ordinary Grade-9 completion boundary;
- **2 support/prerequisite** — reusable where a Grade-9 learner action needs them, not standalone completion blockers;
- **3 question-demand** — bounded preparation justified by owner-approved real-question evidence, non-blocking for ordinary Grade-9 completion;
- **1 declared extension** — visible but non-default/non-blocking;
- **8 deferred later/broader** — retained in the repository but not pulled into Grade 9 for completeness.

A matrix-level classification does not imply every retained rung inside that matrix is mandatory. Existing non-default/extension rung controls still apply.

## Ordinary Grade-9 core

| Matrix | Scope reason | Grade-9 role | Pinnacle Terminal-1 relation | Ordinary completion blocker? |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-KIN-1D-MOTION` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | Motion 1 D: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | yes |
| `MATRIX-PHY-NLM-FIRST-LAW` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | NLM: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | yes |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | yes |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | yes |
| `MATRIX-PHY-SOUND` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | yes |
| `MATRIX-PHY-SIMPLE-MACHINES` | `SYLLABUS_REQUIREMENT` | REQUIRED_CORE | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | yes |

These six are the existing audited Grade-9 production slices. Their authoring pass is complete. “Complete” here means the ordinary route is structurally authored and regression-frozen; it is **not learner mastery evidence**.

## Support and prerequisite material

| Matrix | Scope reason | Grade-9 role | Pinnacle Terminal-1 relation | Ordinary completion blocker? |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-VECTOR-REPRESENTATION` | `PREREQUISITE` | SUPPORT_ONLY | Vectors: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | no |
| `MATRIX-PHY-VEC-ADD-SUB` | `PREREQUISITE` | SUPPORT_ONLY | Vectors: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | no |

Vector representation and vector add/sub remain support-first. The active Pinnacle Vectors chapter and approved ExamSIDE families justify using specific vector actions for preparation, but school micro-demand remains unconfirmed until Pinnacle-issued material says otherwise.

## Bounded real-question preparation

| Matrix | Scope reason | Grade-9 role | Pinnacle Terminal-1 relation | Ordinary completion blocker? |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-VEC-DIRECTION-UNIT` | `QUESTION_DEMAND` | QUESTION_DEMAND_NONBLOCKING | Vectors: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | no |
| `MATRIX-PHY-KIN-2D-MOTION` | `QUESTION_DEMAND` | QUESTION_DEMAND_NONBLOCKING | Motion in 2 D: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | no |
| `MATRIX-PHY-NLM-MOMENTUM-TRANSFER` | `QUESTION_DEMAND` | QUESTION_DEMAND_NONBLOCKING | NLM: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep CONFIRMED_EXAMSIDE | no |

These matrices exist because real approved preparation demand demonstrated independently fail-able learner actions. They remain deliberately separate from school-issued micro-scope:

```text
owner-approved ExamSIDE demand
→ valid preparation demand

Pinnacle school source absent
→ school_micro_demand stays MICRO_TO_CONFIRM
```

That distinction prevents JEE-style preparation breadth from being misreported as the school's syllabus.

## Declared extension

| Matrix | Scope reason | Grade-9 role | Pinnacle Terminal-1 relation | Ordinary completion blocker? |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-RELATIVE-MOTION` | `DECLARED_EXTENSION` | DECLARED_EXTENSION_NONBLOCKING | Motion in 2 D: CHAPTER_CONFIRMED; school micro MICRO_TO_CONFIRM; prep NOT_RECORDED_AS_CONFIRMED_IN_CURRENT_MICRO_SCOPE | no |

Relative motion stays visible and reusable, especially inside Motion-in-2-D contexts, but it is not an ordinary Grade-9 completion blocker by default.

## Deferred later/broader Physics

| Matrix | Scope reason | Grade-9 role | Pinnacle Terminal-1 relation | Ordinary completion blocker? |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-ELEC-CURRENT-OHM` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-FLUID-BERNOULLI-EQUATION` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-MAG-FIELD-LORENTZ` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-OPTICS-REFLECTION-MIRRORS` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-OPTICS-REFRACTION-LENSES` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-OSC-SHM-WAVES` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-ROT-RIGID-BODY` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |
| `MATRIX-PHY-THERMO-FIRST-SECOND-LAW` | `DEFER` | DEFERRED_LATER_OR_BROADER | NOT_IN_CURRENT_PINNACLE_TERMINAL1_BOUNDARY | no |

The broad-fluid case is the important nuance: a verified Grade-9 pressure/buoyancy learner action may justify a bounded capability, but that does **not** import the whole Bernoulli/fluid matrix into Grade 9.

## Pinnacle Terminal-1 evidence boundary

The current school sheet confirms only these chapter labels:

```text
Vectors
Motion 1 D
Motion in 2 D
NLM
```

For chapter-internal learner actions, the current machine-readable planning layer deliberately preserves:

```text
school chapter demand = CHAPTER_CONFIRMED
school micro demand   = MICRO_TO_CONFIRM
```

Approved ExamSIDE evidence may independently set preparation demand, and local capability state may independently be ready/partial/gap. Neither changes the school evidence field.

## Grade-9 completion implications

For ordinary Grade-9 scope, the completion boundary is the six `REQUIRED_CORE` matrices plus only the support actually required by their learner actions. The following do **not** block ordinary Grade-9 completion merely because they exist:

- extra vector depth beyond required support;
- Motion-in-2-D/projectile preparation;
- discrete momentum-transfer force;
- relative motion;
- electricity, magnetism, optics, thermodynamics, rotation, SHM/waves, or broad Bernoulli/fluid coverage.

They can become relevant only through a more specific current source, approved real-question demand, or a genuine prerequisite.

## Evidence still unresolved

1. Pinnacle school micro-demand remains unknown for chapter-internal actions until school-issued evidence confirms it.
2. Scope coverage is not learner evidence; actual Grade-9 exit readiness still requires observed learner performance and independent verification.
3. If future evidence promotes one deferred/support/extension slice, promote the **smallest bounded learner action**, not the whole connected matrix family.

## Anti-drift

- no grade/class field added to the matrix schema;
- no mastery percentage inferred from repository coverage;
- no chapter title expanded into invented micro-scope;
- no higher-grade pull-down for elegance or completeness;
- no external preparation evidence relabelled as Pinnacle-issued evidence;
- no canonical Physics content changed by this audit.
