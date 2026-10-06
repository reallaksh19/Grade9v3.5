# ISS66 U08B — NO_CHANGE interaction-contract decision

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U08B only — freeze the interaction decision after #49–#56 replay  
**Basis head:** `05d8d6549c41a0a7de3d11b216f554ae9d1a433f`

## Decision

`NO_CHANGE`

No new interaction primitive is added to:

- `Shared/web/interactive-page-blueprint.schema.json`
- `Shared/web/interactive-page-blueprints.v1.json`
- `Shared/library/package.schema.json`
- `Shared/tools/render_core.py`
- shared learner-quality rules
- shared cognitive/QRT authority

U08 therefore closes by **not** adding schema/runtime surface.

This is an intentional architecture decision, not missing implementation.

## Why NO_CHANGE is the correct result

The stress-test builder proposals contain several useful product ideas, but a permanent shared interaction contract needs recurring **semantics**, not recurring controls.

The only repeated cluster is numeric probing:

- #49 — bounded parameter + prediction/reason + derived readouts;
- #54 — independent-variable evaluation around a domain exclusion;
- #56 — continuous model-parameter deformation and critical visual states.

A range input can implement all three visually, but their academic state, response ownership and acceptance semantics are different.

Making `min/max/step` or a generic slider component part of the blueprint would standardise a DOM control while leaving the meaningful learner contract outside the schema.

That would invert authority:

`UI mechanism → guessed academic meaning`

instead of:

`canonical learner action/evidence → suitable presentation mechanism`.

## Existing mechanisms retained

### Design intent

The existing research-authoring object:

`grade9v3:interactive_idea`

already records:

- what the learner manipulates;
- what becomes visible;
- the misconception targeted;
- the representation involved.

Mathematics, Physics and Chemistry work rules use the same design-intent fields.

This is the appropriate level for unproven interaction ideas.

### Executable composition

Current learner pages already have reusable mechanisms for:

- staged visual revelation;
- question-specific representations;
- learner attempt/commitment;
- typed/free response;
- prediction-before-comparison;
- protected disclosure;
- static/print/paper fallback.

A proposed new primitive must demonstrate a recurring learner action that these surfaces cannot represent honestly, not merely make more visually dynamic.

## Reopening threshold

A future interaction proposal may reopen U08's NO_CHANGE decision only when **all** of the following evidence exists.

### 1. Independent semantic recurrence

At least two independently produced products must require the same learner-owned semantic operation.

The match must be expressible as the same state transition, for example:

`learner supplies/manipulates X → governed observation Y changes → learner records/commits Z`

not merely:

`both use a slider`.

### 2. Evidence breadth

The recurrence must span either:

- at least two subjects; or
- clearly distinct task families where topic vocabulary is not required by the primitive.

Two variants of one polynomial benchmark are insufficient.

### 3. Existing-composition failure

Each case must document why the existing combination of:

- `STAGED_VISUAL`;
- normal attempt controls;
- prediction/compare;
- authored representation stages;
- paper/static fallback;

cannot preserve the intended learner action/evidence without a custom one-off path.

Convenience alone is not enough.

### 4. Convergent canonical state

The independent cases must produce the same minimal authored/runtime state fields.

Those fields must describe learner/evidence semantics rather than CSS, SVG transforms or topic equations.

### 5. Shared protection semantics

The same primitive must have one coherent rule for:

- what exists before attempt;
- what learner state is persisted/restored;
- what is protected;
- what becomes visible after commitment;
- whether the state is evidence, exploration only, or graded elsewhere.

### 6. Accessibility and non-JS equivalence

One retained-fixture implementation must prove:

- keyboard/touch operation;
- semantic textual equivalent;
- no protected-answer leakage;
- printable/no-JS fallback that preserves the task rather than replacing it with the answer.

### 7. No topic branches

The shared implementation must serve the independent fixtures without branches such as:

- `if polynomial`;
- `if rational function`;
- `if root collision`;
- `if coordinate plot`.

Topic-specific computation may live in authored records or separate subject logic, but not define the shared primitive.

## Explicitly rejected premature abstractions

The current evidence does **not** justify adding any of these as shared semantic components:

- `POLYNOMIAL_COEFFICIENT_GRID_INTERACTOR`
- `rational-domain-inspector`
- `CONTINUOUS_PARAMETER_SCRUBBER`
- generic `parameter_scrubber` solely with min/max/step/CSS-variable fields
- `COORDINATE_PLOT_RESPONSE` as part of U08

`COORDINATE_PLOT_RESPONSE` may still be a legitimate future structured-response proposal, but #49–#56 do not provide recurrence for it. It should be evaluated separately if another independent task family requires the same learner-owned point/table response.

## Negative knowledge preserved

1. A repeated DOM control is not repeated academic semantics.
2. “Could be useful in Physics/Chemistry” is not cross-subject evidence.
3. One candidate author's claim of reusability does not establish shared worth.
4. Optional/backward-compatible schema is still permanent complexity.
5. Static fallback does not by itself prove semantic equivalence.
6. A visually richer interaction is not automatically better than staged disclosure.
7. No topic-specific component should enter the shared blueprint merely because the current benchmark is Mathematics.

## U08 acceptance result

U08 required:

> interaction capability schema only when a recurring subject-neutral primitive is justified; otherwise NO_CHANGE.

The evidence supports the second branch.

**U08 COMPLETE — NO_CHANGE.**

No production/shared-contract mutation is required for this unit.

Parent denominator:
- **P = 8/10 = 80%**
- **E = 8/10 = 80%**

Next bounded unit:

**U09A — integration/migration inventory: enumerate every shared contract changed by U02–U07, identify legacy compatibility paths and exact retained fixtures before any migration edit.**
