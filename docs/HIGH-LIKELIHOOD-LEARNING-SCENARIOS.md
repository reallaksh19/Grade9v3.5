# High-likelihood learner scenarios and matrix contract

> Status: final design for the one-learner self-study blueprint.
>
> Scope: common learner/session branches only. The exhaustive test scanner may exercise many
> structurally valid combinations, but those combinations are not separate architecture.

## Research basis

This design keeps a cold learner attempt before assistance, gives specific task/process
feedback rather than generic praise, escalates help only as needed, uses worked examples or
repair after repeated failure, and returns to independent retrieval/verification.

The main evidence behind those choices is:

- Butler & Winne (1995), *Feedback and Self-Regulated Learning*:
  monitoring and feedback are central to self-regulated learning.
  DOI: https://doi.org/10.3102/00346543065003245
- Shute (2008), *Focus on Formative Feedback*:
  formative feedback is most useful when it is supportive, timely and specific; hints,
  verification and worked examples are different forms of assistance, not interchangeable
  labels. DOI: https://doi.org/10.3102/0034654307313795
- Hattie & Timperley (2007), *The Power of Feedback*:
  feedback effects depend on the type and level of feedback, so the system should target the
  task/process actually failing instead of issuing a generic response.
  DOI: https://doi.org/10.3102/003465430298487
- VanLehn (2011), *The Relative Effectiveness of Human Tutoring, Intelligent Tutoring
  Systems, and Other Tutoring Systems*: step-level tutoring is a useful granularity for
  guided problem solving, supporting the repository's diagnose/hint/repair progression.
  DOI: https://doi.org/10.1080/00461520.2011.611369
- Chi et al. (1989), *Self-Explanations*: learners who actively explain worked examples
  develop more example-independent knowledge than learners who passively follow them.
  DOI: https://doi.org/10.1207/s15516709cog1302_1
- Adaptive worked-example fading has evidence in high-school geometry; assistance can be
  reduced as performance improves rather than fixing one support level for every learner.
  See the expertise-reversal/adaptive-fading literature summarized at
  https://doi.org/10.1007/s11251-009-9102-0
- Retrieval practice supports delayed retention broadly, but the mathematics-specific 2025
  meta-analysis finds a clearer effect for spacing than for testing-versus-restudy alone.
  Therefore fresh checks and delayed review are retained, while the repository does **not**
  claim that its exact 1/3/7/14-day schedule is an empirically optimal schedule.
  DOI: https://doi.org/10.1007/s10648-025-10035-1

These sources justify the direction of the policy. They do not supply a probability that any
one scenario will occur for this learner. "High-likelihood" below means ordinary recurring
branches of a self-study loop, not measured incidence.

## Final learner scenarios

The practical runtime should optimize for seven learner scenarios.

### S1 — Independent correct attempt

Evidence:

```text
result = CORRECT
help = NONE
```

Action:

```text
CONTINUE
```

The direct attempt may support `DEMONSTRATED` only under the repository's existing evidence
rules. A missing canonical verification path limits the draft to `UNCERTAIN`.

### S2 — Correct after help

Evidence:

```text
result = CORRECT
help = HINT | WORKED_EXAMPLE | SOLUTION | UNKNOWN
```

Action:

```text
UNCERTAIN
→ fresh VERIFY when available
```

Correctness after assistance is useful learning evidence but not independent mastery.

### S3 — Clear concept/setup failure

Evidence:

```text
result = INCORRECT
failed capability is supported by the work
error_stage = CONCEPT | SETUP
```

Action:

```text
MISSING
→ smallest safe hint
→ RETRY
```

The first repair target is the earliest supported capability failure, not the whole topic.

### S4 — Clear execution/careless failure

Evidence:

```text
result = INCORRECT
failed capability is supported by the work
error_stage = EXECUTION | CARELESS | UNKNOWN
```

Action:

```text
UNCERTAIN
→ RETRY with the smallest useful support
```

A procedural slip is not automatically evidence that the underlying concept is missing.

### S5 — Ambiguous or undecidable failure

Evidence:

```text
result = UNDECIDABLE
or
INCORRECT with multiple plausible capability causes and no supported attribution
```

Action:

```text
DIAGNOSE
→ one discriminating prompt
→ do not guess learner state
```

This is expected on multi-capability exam questions and is a normal branch, not an exception.

### S6 — Persistent failure after safe hints

Evidence:

```text
repeated incorrect attempts
or
no safe non-answer hint remains
```

Action:

```text
REPAIR
→ canonical misconception repair / teaching step / worked example
→ learner explains or reconstructs the step
→ fresh VERIFY
```

The runtime may increase assistance, but answer-revealing material is repair, not a hidden
"hint".

### S7 — Fresh verification after help or repair

Evidence:

```text
fresh same-capability question
or
canonical microtopic exit task
```

Action:

```text
independent correct → stronger direct evidence
helped correct      → UNCERTAIN
wrong               → MISSING or UNCERTAIN according to supported failure
no fresh item       → VERIFICATION_ITEM_REQUIRED
```

Fresh verification must not be fabricated merely to make the state machine move.

## Operational branches, not learner scenarios

Two operational conditions remain outside S1-S7:

```text
safe but incomplete route
→ EXECUTE_WITH_FALLBACK

unresolved / ambiguous / unsafe teaching delivery
→ OWNER_DECISION
```

They affect executability, not the learner's knowledge state.

## What the matrix must own

A skill matrix is durable pedagogical design. It does **not** own attempt history.

For a matrix considered `SESSION_READY` or `SESSION_READY_WITH_BRIDGE`, the final design
expects:

```text
rungs[]
  → microtopic_ref
  → ladder_position
  → controlled_variation
  → must_contain / ceiling where useful

family
  → invariant_demand
  → difficult_move
  → independent_check
  → support_ladder
       low
       medium
       high

transfer[]                      optional when genuinely justified
  → changed_demand
  → information_not_handed_over
  → repair_to
```

`minimum` support remains optional. It is useful only when recognizing the family itself is
part of the demand. Requiring it everywhere would add ceremony without improving the common
self-study loop.

### Support ladder semantics

Use the existing vocabulary consistently:

- **low** — preserve the full decision; provide only the situation/task.
- **medium** — provide representation/setup information but not the core decision.
- **high** — provide substantial structure or the relevant relation, while still leaving an
  executable learner step.
- **minimum** — optional unlabelled/family-recognition form.

The matrix support ladder is an **authoring/design constraint**, not a runtime hint database.
The matrix may not become a second learner-facing source of truth.

## What the canonical library must own

The matrix references canonical records rather than copying them.

```text
microtopic
  → teaching_path
  → misconception
       wrong_idea
       diagnostic_prompt
       repair
  → exit_task

question
  → primary / secondary capability refs
  → hints[]
       reveals = CONCEPT | METHOD | ANSWER
  → repair_ref
  → transfer metadata where applicable
```

These records are what the runtime may use for actual feedback.

## What session state must own

The following are transient learner/session facts and must never move into a skill matrix:

```text
result
help_used
error_stage
attempt_number
shown_hint_indices
attempted_question_refs
failed_capability_ref
misconception_index
diagnostic_response
diagnosis = CONFIRMED / REFUTED / INDETERMINATE
diagnostic_basis
DEMONSTRATED / UNCERTAIN / MISSING
```

The clean boundary is therefore:

```text
SKILL MATRIX
durable pedagogical design
        ↓
CANONICAL LIBRARY
learner-facing teaching / hints / repairs / verification
        ↓
SESSION RUNTIME
attempt history + next safe action
        ↓
LEARNER OBSERVATION
reviewed evidence only
```

## Deliberately excluded scenario classes

The architecture does not get a special branch for combinations such as:

```text
CORRECT + CARELESS
UNDECIDABLE + SOLUTION
attempt 17
arbitrary malformed hint history
```

The generic policy still handles them safely, and the exhaustive scanner may test them, but
they do not deserve additional architecture, matrix fields or execution states.

## Acceptance rule

A change to this design now requires one of:

```text
real learner/session failure
real worksheet demand
repeated benchmark failure
clear research-backed defect in the current contract
```

Otherwise keep the seven scenarios, the existing two execution dispositions, and the
matrix/library/session separation unchanged.
