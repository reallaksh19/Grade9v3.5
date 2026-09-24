# Core2B transfer-integrity migration

Core2B tests an established capability under a **genuinely changed demand**. Its defining
learner work is the new decision created by that change, and that decision must remain
the learner's before the attempt.

The repository already carries the right primitives:
`transfer.dimension`, `transfer.statement`, `transfer.builds_on[]`,
`answer.reasoning_route[]`, `transfer.protected_move_ref`, rubrics, repairs and
attempt-before-reveal runtime state. The migration closes the gap between those primitives
and the older transfer corpus; it does not create another transfer model.

## Forward contract

Every new or materially revised Core2B question must close all machine-checkable debt:

1. `answer.reasoning_route[]` exists;
2. `transfer.protected_move_ref` resolves to a `DECIDE` move;
3. lineage resolves to concrete prior exposure;
4. when an adaptation parent exists, that parent appears in `builds_on[]`;
5. a question anchor is familiar Core2A exposure rather than an unestablished transfer;
6. the current primary/secondary capabilities are already established by lineage or their
   prerequisite closure;
7. `repair_ref` resolves to a specific teaching-path step;
8. the answer has a non-empty rubric whose rows contain `criterion` and `evidence_of`.

These checks prove structural transfer integrity. They do **not** decide that an author's
changed-demand statement is pedagogically valid; pairwise review still adjudicates that
claim.

## Pairwise transfer audit

`Shared/tools/core2b_inventory.py` exposes the evidence needed for review:

```text
prior anchor
current task
family / primary capability
required versus established capabilities
transfer dimension
changed-demand statement
adaptation changed_fields
protected decision
hint reveal depths
repair specificity
rubric closure
```

Anchor priority is:
1. adaptation parent question;
2. question in `transfer.builds_on[]`;
3. microtopic lineage.

This makes the comparison reviewable without using lexical similarity as a verdict.

## Legacy debt baseline

Existing transfer items may remain unchanged while they migrate. Generate the deterministic
baseline with:

```bash
python3 Shared/tools/core2b_inventory.py --write-baseline
```

Guardrails enforce only forward motion:

```bash
python3 Shared/tools/core2b_inventory.py --enforce-forward
```

A new debt-bearing Core2B item fails. A materially revised existing item must close its
recorded debt rather than keeping the old exemption. Once debt closes, reverting it creates
new debt and fails.

The baseline is an inventory of migration work, **not an acceptance list**.

## Pre-attempt support

Canonical `hints[]` remain source/question custody and are not deleted merely because an
item is Core2B. Learner-time support has a stricter policy:

- before attempt, only support that does not disclose the changed decision may surface;
- a protected-move scaffold is already blocked by the interactive state machine;
- METHOD/ANSWER hints are not generically safe before a Core2B attempt;
- after an attempt, graduated METHOD support may be shown while the full answer remains
  available for self-study closure.

A static document cannot prove that a learner attempted before opening a disclosure.
Therefore its accessible hints/answers are a self-study affordance, not evidence that the
protected decision was empirically preserved. That distinction belongs in release/review
evidence rather than being hidden.

## Capability continuity

A changed context or representation is transfer only if the underlying capability already
exists in the prior-exposure closure. If the current task requires a new primary or
secondary capability, the inventory reports
`TRANSFER_REQUIRES_UNESTABLISHED_CAPABILITY`.

That finding means **upstream teaching / coverage gap**, not “make Core2B harder.”

## Repair

Core2B failure should route to the construction that repairs it. A whole microtopic or
another question is too broad to satisfy the forward contract merely because its id
resolves. The repair target is a specific teaching-path step.

## Dimension coverage

The inventory reports `model_choice`, `representation_translation`,
`reasoning_steps` and `novelty` counts as observations. No dimension quota exists.
Absence of a dimension is not a defect unless real source/question demand shows a missing
transfer family.
