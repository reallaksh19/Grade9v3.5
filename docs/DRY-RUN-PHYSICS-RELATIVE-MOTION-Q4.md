# Dry run — Physics Relative Motion Q4

> Status: **system dry run complete — synthetic evidence, not learner evidence**
>
> This replaces the unavailable interactive learner turn with explicit simulated attempt
> signatures. It follows the same adaptation principle used for the earlier Mathematics
> pilot work: exercise the real routing/feedback contracts, but never pretend a generated
> response came from the learner.

## Why this exists

The live packet in `docs/EMPIRICAL-SESSION-PHYSICS-RELATIVE-MOTION-Q4.md` remains the
correct protocol when learner input is available. In the current workflow it is not
available, so this dry run is the strongest honest substitute.

The dry run may prove:

- the real external Q4 maps to the intended reusable capabilities;
- common learner outcomes reach safe next actions;
- prerequisite failures can be routed when they are explicitly supported by the work;
- repairs use canonical content;
- fresh verification is available;
- no synthetic path is persisted as learner evidence.

It cannot prove:

- what this learner actually knows;
- which misconception this learner actually has;
- that the learner can perform the skill independently;
- empirical acceptance under Issue #50.

Therefore every generated observation remains:

```text
provenance = UNREVIEWED_SESSION_DRAFT
persistence = NOT_WRITTEN
```

and the empirical layer remains `PENDING_REAL_EVIDENCE`. This does not block the completed system dry-run lane.

## Real demand under test

Question:

`NEETPREP-MQB-REL-Q4`

Direct mapped demand:

```text
primary   CAP-VEC-RESULTANT-CONSTRAINT
secondary CAP-RELATIVE-V
```

Prerequisite route:

```text
CAP-VECTOR-VS-SCALAR
        ↓
CAP-SIGNED-PAIR-BRIDGE        [Mathematics external bridge]
        ↓
CAP-VECTOR-SIGNED-COMPONENT
        ↓
CAP-VEC-COMPONENT-SUM
        ↓
CAP-VEC-RESULTANT-CONSTRAINT

plus CAP-RELATIVE-V
```

The dry run does not copy prerequisite capabilities into the worksheet's secondary mapping.
Prerequisite ownership still comes from the canonical capability graph.

## High-likelihood scenarios

### D1 — independent correct

Synthetic evaluated attempt:

```text
result = CORRECT
help = NONE
```

Expected:

```text
CONTINUE
draft = DEMONSTRATED
provenance = UNREVIEWED_SESSION_DRAFT
persistence = NOT_WRITTEN
```

This proves only that the runtime can represent an independently correct evaluated attempt.
It is not a learner claim.

### D2 — correct after help

Synthetic evaluated attempt:

```text
result = CORRECT
help = HINT
```

Expected:

```text
draft = UNCERTAIN
→ VERIFY
→ canonical CAP-VEC-RESULTANT-CONSTRAINT exit task
```

The fresh item must remain independent of the original river context.

### D3 — clear resultant-constraint concept failure

Synthetic reasoning signature:

```text
"directly opposite" is applied to the swimmer vector itself
instead of to the ground-relative resultant
```

Explicit attribution:

```text
failed_capability_ref = CAP-VEC-RESULTANT-CONSTRAINT
error_stage = CONCEPT
misconception_index = 0
diagnostic_response = "I applied the directly-opposite condition to the swimmer vector instead of the ground-relative resultant."
diagnosis = CONFIRMED
diagnostic_basis = "The response to the canonical probe places the constraint on the wrong vector."
```

Expected:

```text
MISSING
→ canonical misconception REPAIR
→ fresh VERIFY
```

### D4 — clear execution slip

Synthetic reasoning signature:

```text
resultant constraint is set up correctly
but arithmetic/execution fails
```

Expected:

```text
UNCERTAIN
→ DIAGNOSE / RETRY
```

A procedural slip must not be promoted into a concept-missing claim.

### D5 — ambiguous failure

Synthetic evaluated attempt:

```text
result = UNDECIDABLE
failed capability = none
```

Expected:

```text
DIAGNOSE
no observation draft
no guessed capability
```

### D6 — explicit local prerequisite failure

Two common prerequisite signatures are exercised separately:

```text
CAP-VECTOR-SIGNED-COMPONENT
CAP-VEC-COMPONENT-SUM
```

These are not direct worksheet secondary capabilities. They are canonical prerequisites of
the primary capability.

If the supplied work explicitly supports one of them as the first failure, the runtime
should accept that attribution and route to the canonical local diagnosis/repair. It should
not reject the capability merely because it was reached through prerequisite closure.

This dry run is intentionally a falsifier for that boundary.

### D7 — explicit external prerequisite failure

Synthetic reasoning isolates the external signed-coordinate prerequisite:

```text
failed_capability_ref = CAP-SIGNED-PAIR-BRIDGE
```

Expected:

```text
OWNER_DECISION
external provider = Mathematics
```

The Physics runtime may not fabricate local teaching for an explicitly external failure.

## Fresh verification

For D2/D3, verification should resolve to the canonical exit task owned by
`MIC-PHY-VEC-RESULTANT-CONSTRAINT`:

```text
current contributes +3 along x
choose swimmer x-component so resultant x-component is 0
state the equation
```

The dry run checks the existence and routing of this item. It does not invent a learner
answer to it.

## Acceptance of the dry run

The dry run passes when the repository proves all of the following:

```text
real Q4 mapping resolves
independent-correct path is non-persistent
helped-correct path requests fresh verification
clear primary failure repairs from canonical content
execution slip remains UNCERTAIN
ambiguous failure diagnoses without guessing
explicit local prerequisite failures remain locally attributable
explicit external prerequisite failure becomes OWNER_DECISION
no path creates LIVE_LEARNER evidence
```

Any failing row is treated as a system integration defect, not as evidence about the learner.

## Relationship to empirical acceptance

```text
DRY RUN
synthetic system evidence
        ↓
regression / integration confidence

LIVE SESSION
actual learner work
        ↓
reviewed LIVE_LEARNER observation
        ↓
empirical acceptance
```

The first path can proceed without student input. It must never be relabelled as the second.


## Dry-run finding

The first executable dry run exposed one integration defect: feedback accepted explicit
failure attribution only to a question's direct primary/secondary capabilities. That meant
a learner work trace could clearly isolate a canonical prerequisite failure but the runtime
would discard that attribution.

The repair is deliberately generic and narrow:

- direct worksheet mappings remain sparse;
- canonical prerequisite closure is used only when the evaluator explicitly names a failed
  prerequisite;
- local prerequisite failures can use their existing canonical diagnosis/repair;
- an explicitly failed external prerequisite resolves to `OWNER_DECISION`;
- ambiguous attempts do not automatically expand across the full prerequisite closure.

This preserves the no-guessing rule and avoids turning prerequisite topology into extra
worksheet tags or a larger matrix schema.


## Completion

This dry run was merged in PR #72 and is now part of the accepted system-evidence lane
described in `docs/SYSTEM-DRY-RUN-ACCEPTANCE.md`.

Final merged validation:

```text
651 tests
OK
```

The live learner packet remains available only for later empirical evidence if such input
becomes available.
