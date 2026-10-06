# ISS69 PHASE-C — C02.1 Core2 runtime ownership map

Material basis: `fix/iss69-phase-c-runtime-alignment`

Recovered product authority: `BP-CORE2-SOURCE-QUESTION@1.11.0`

## Slot ownership

| Component | Blueprint slot | Runtime owner | Disclosure state |
| --- | --- | --- | --- |
| IDENTITY / SOURCE_PDF / DIFFICULTY_WHY | identity | `render_core.core2()` | page-open |
| STEM / CONDITIONS / ATTEMPT | attempt | `render_core.core2()` | page-open / commitment UI |
| REPRESENTATION | representation | `_core2_question_figures(..., PRE_ATTEMPT)` | only reviewed pre-attempt-safe stages |
| TRAP | support | currently mis-projected directly by `core2()` | should be AFTER_ATTEMPT assistance by default |
| HINT_LADDER | support | `_core2_support()` + `_core2_after_attempt_support()` | PRE_ATTEMPT_SAFE + AFTER_ATTEMPT from #66 support plan |
| CONCEPT_NAV | support | `_core2_concept_navigation()` | learner-requested assistance; exact Core1A target when available |
| DIAGNOSTIC_REPAIR | solution/SOLUTION | `learning_repair.card(...)` after typed evidence validation | never pre-attempt furniture |
| SOLUTION_STEPS / ANSWER / CHECK | solution/SOLUTION | `_core2_solution()`, source answer/check projection | attempted solution payload |
| solution-only extra support | solution | `_core2_completed_support()` | POST_SOLUTION |

## Existing disclosure state authority

`Shared/tools/core2_v2.py` already owns the three support states:

- `PRE_ATTEMPT_SAFE`
- `AFTER_ATTEMPT`
- `POST_SOLUTION`

`project_support()` resolves authored support rows against `grade9v3:core2_support_plan`.

A support completion that intersects `protected_move_refs` cannot be `PRE_ATTEMPT_SAFE`. ANSWER-revealing support cannot be PRE_ATTEMPT_SAFE or AFTER_ATTEMPT.

This is the state authority to reuse. No second TRAP-specific availability schema is justified.

## Current defect

`render_core.core2()` currently passes:

```text
STEM
CONDITIONS
TRAP
ATTEMPT
```

to `component_body(..., "attempt")`.

The active blueprint declares TRAP in `support`, so the renderer raises:

```text
KeyError: CORE2: TRAP not declared in attempt of BP-CORE2-SOURCE-QUESTION
```

This is the exact C02.2 projection seam.

## C02 ownership decision

1. **Attempt**
   - STEM
   - CONDITIONS
   - ATTEMPT
   - no common-wrong-route content.

2. **Pre-attempt support**
   - only rows already classified PRE_ATTEMPT_SAFE by the typed #66 support-plan authority.
   - source/authored provenance remains explicit.

3. **TRAP / common wrong route**
   - optional support component;
   - default disclosure boundary is AFTER_ATTEMPT because naming the tempting route can materially narrow model selection;
   - do not infer a learner diagnosis from the authored wrong-route hypothesis;
   - do not create a new availability field solely for TRAP.

4. **Concept navigation**
   - remains in support;
   - exact construction_ref wins when valid;
   - opening it is assistance and the same-question retry is not independent evidence.

5. **Diagnostic repair**
   - remains solution/evidence-side;
   - complete CONFIRMED diagnostic evidence is required for misconception-specific routing.

6. **Solution**
   - remains an attempted payload with POST_SOLUTION-only support inside it.

## Negative knowledge

- A collapsed `<details>` element is not semantic protection.
- Moving TRAP from attempt to support is necessary but insufficient; it must also be attempt-gated.
- PRE_ATTEMPT_SAFE support is not equivalent to “anything the learner chooses to open before attempting.”
- The support-plan state machine already solves protected-move availability; do not fork it.

## Next bounded change

C02.2 changes only `render_core.core2()` slot composition:

- remove TRAP from the attempt component body;
- place TRAP in support;
- preserve all other component owners;
- add a focused slot test;
- do not yet finalize the AFTER_ATTEMPT gating implementation beyond what is mechanically required for slot correctness. C02.3 owns the state-bound disclosure semantics.
