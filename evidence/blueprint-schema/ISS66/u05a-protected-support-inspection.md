# ISS66 U05A — protected-act and support-eligibility contract inspection

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U05A only — inspect existing protected-move/support-plan and renderer deferral machinery before schema change  
**Basis head:** `ed22c58958156deee2d799d394a00c3084c1f382`

## Existing shared authority

### Canonical support-plan schema

`Shared/library/package.schema.json`

The optional question extension:

`grade9v3:core2_support_plan`

already provides:

- `protected_move_refs[]` — one or more canonical reasoning-move ids owned by the learner before disclosure;
- `support_completions[]` — maps an existing support row to the reasoning moves it completes;
- `visuals[]` — maps a selected representation/case stage to the reasoning moves that stage completes.

References are structural. The plan does not infer protected work from prose.

### Core2 projection

`Shared/tools/core2_v2.py`

`support_plan(...)` resolves the authored plan against the exact question:

- every protected move must resolve inside `answer.reasoning_route[]`;
- every support completion must name a real hint/scaffold row;
- every completed move must resolve inside the reasoning route;
- every visual plan must name a unique representation and case instance;
- every visual stage must have a unique stage ref and only known completed moves.

`project_support(...)` then computes:

`eligible_pre_solution`

as:

1. false for rows already typed `reveals == ANSWER`; and
2. false when an authored `completed_move_refs` intersects `protected_move_refs`.

This is a genuine machine-checkable improvement over “panel starts closed.”

### Visual protection

`visual_support(...)` derives `pre_attempt_stage_refs` by excluding visual stages whose authored completed moves intersect protected moves.

This means a concept-correct representation can still be withheld when its **stage** completes learner-owned work.

### Render path

`Shared/tools/render_core.py`

Pre-solution support uses only rows returned by:

`core2_v2.split_pre_solution_support(...)`

Deferred rows/stages are collected by:

`_core2_completed_support(...)`

and are placed inside the existing gated:

`Answer and working`

payload.

That payload is materialised only after a valid learner attempt sets:

`data-attempted=1`

The page JS validates the response control as a commitment signal; it does not grade correctness.

## Existing exact regressions

`tests/test_staged_support_repair.py` already proves:

- a parameter-revealing support row that completes the protected move is absent from pre-solution support;
- the exact same authored words remain available later without relabelling;
- a protected visual stage is absent before attempt;
- the protected stage is present in the attempted solution payload;
- malformed or unresolved plan references fail closed;
- no-picture questions can omit visual plans without fabricating a figure.

This directly validates the PR #65 pilot behavior.

## What is already sufficient

**REUSE EXISTING**

The following do not need a second mechanism:

1. **Canonical protected work reference**  
   `protected_move_refs` already points at exact reasoning moves.

2. **Support-to-protected-work relationship**  
   `support_completions.completed_move_refs` already records which learner moves a support row completes.

3. **Visual-stage protection**  
   visual stage `completed_move_refs` already provides the same relationship for representations.

4. **Reference validation**  
   the projection fails closed on unknown moves, support rows, instances or visual stages.

5. **Attempt commitment**  
   the renderer already has a non-grading attempt state and restores it across page state.

Therefore U05 must extend this machinery, not fork a parallel “protected_act” object solely to rename what is already represented.

## Concrete gap

### Current eligibility is binary and renderer-derived

The current plan can distinguish only:

- support that remains `eligible_pre_solution`; versus
- support that is deferred into the attempted **Answer and working** payload.

It does **not** author or preserve a richer eligibility state such as:

- `PRE_ATTEMPT_SAFE`
- `AFTER_ATTEMPT`
- `POST_SOLUTION`

or an equivalent minimal state model.

This creates a real contract limitation:

> a support row may be safe immediately after commitment but still not be appropriate to bundle with the complete solution; the current schema has no way to express that distinction.

Likewise, a visual stage that completes protected work is either excluded pre-attempt or delivered in the same post-attempt solution payload. There is no separate authored eligibility boundary.

### “Requested support” is UI behavior, not eligibility authority

The hint ladder already reveals pre-solution rungs only when the learner asks for them.

However, “learner requested a hint” is not currently a schema eligibility state. The author can control ordering and completion relationships, but cannot state that one support row is available only after an earlier request/commitment state independently of full solution disclosure.

### Omitted completion remains author risk

The system intentionally does not guess from prose whether a support row completes a protected move.

If an author fails to record `completed_move_refs`, the row retains its existing reveal semantics.

That is unavoidable without semantic inference. U05 should improve explicit authoring state, not introduce a brittle prose classifier.

## U05A disposition

### Reuse

Keep:
- `protected_move_refs`
- `support_completions`
- visual-stage `completed_move_refs`
- exact reference resolution
- attempt commitment state
- existing source/authored provenance lanes.

### True contract gap

Add the **smallest explicit eligibility state** to the existing support-plan relationships so a protected-completing support item can distinguish at least:

- unavailable before commitment but available after attempt; from
- solution-only disclosure.

Do not add a new learner-decision identity object unless a later fixture proves the existing reasoning-move refs are insufficient.

### Deferred

Do not yet add:
- grading/correctness state;
- inferred misconception state;
- arbitrary workflow/state-machine proliferation;
- a topic-specific support type;
- automatic semantic inference from hint text.

## U05A result

**U05A COMPLETE. No production change.**

Parent U05 remains incomplete.

Parent denominator remains:
- **P = 4/10 = 40%**
- **E = 4/10 = 40%**

Next bounded task:

**U05B — extend the existing Core2 support-plan relationship with the minimum explicit eligibility states needed to distinguish post-attempt support from solution-only support, while preserving all legacy behavior and exact PR #65 protection tests.**
