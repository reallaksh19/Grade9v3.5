# ISS66 U04C — bind primary cognitive demand to canonical crux move

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U04C only — bind the authored primary cognitive-demand claim to the existing canonical reasoning/crux move  
**Tested implementation head:** `b1d984e12db8b3c19e18f92e3b826d7912889d36`

## Architectural decision

Do **not** add another authored `primary_move_ref`.

The repository already has one canonical question-specific bottleneck:

`answer.crux_move_ref`

which resolves inside:

`answer.reasoning_route[]`

Adding a second move reference under `grade9v3:cognitive_demand` would create parallel semantic authority and could itself drift.

Therefore the shared QRT contract now states:

> the primary cognitive demand classifies the existing canonical question crux at `answer.crux_move_ref`.

## Shared vocabulary change

Updated:

`Shared/vocabularies/cognitive-demand.v1.json`

Version:
- before: `1.0.0`
- after: `1.1.0`

Added one subject-neutral selection rule:

`selection.primary_move_binding`

The rule requires QRT resolution to bind the primary demand to the existing canonical crux and explicitly says not to author a competing second move reference.

The seven demand definitions and their decisive-act meanings are unchanged.

## Resolver hardening

Updated:

`Shared/tools/question_review_matrix.py`

The `_question_demand(...)` contract now requires:

1. a valid primary demand enum;
2. valid secondary demands;
3. a non-empty authored basis;
4. a non-empty `answer.crux_move_ref`;
5. that crux reference to resolve inside `answer.reasoning_route[]`;
6. the resolved crux move to have a non-empty action.

The resolved classification now carries:

- `primary_move_ref`
- `primary_move_kind`
- `primary_move_action`

These are derived from the canonical answer route, not separately authored.

The resolution basis also now carries:

`basis_digests.primary_move`

which is a canonical digest of the exact resolved crux move.

Changing the crux move therefore changes the evidence identity even when the primary demand label remains the same.

## Failure modes added

A floating demand claim is now rejected with:

- `COGNITIVE_DEMAND_CRUX_MOVE_MISSING:<question>`
- `COGNITIVE_DEMAND_CRUX_MOVE_UNRESOLVED:<question>:<ref>`
- `COGNITIVE_DEMAND_CRUX_MOVE_ACTION_MISSING:<question>:<ref>`

This means QRT classification can no longer select a cell from a demand label that is disconnected from the question's canonical learner bottleneck.

## Focused regressions

Added:

`tests/test_demand_move_binding.py`

The four focused tests prove:

1. primary demand resolves with the canonical crux move identity/action;
2. the `primary_move` evidence digest changes when the canonical crux move changes;
3. a demand record without `answer.crux_move_ref` is rejected;
4. an unresolved crux reference is rejected.

No subject-specific examples or topic-specific move kinds are introduced.

## Focused CI coverage

Updated:

`.github/workflows/qrt-pipeline-hardening.yml`

The workflow now:
- triggers on `cognitive-demand.v1.json`;
- triggers on `tests/test_demand_move_binding.py`;
- runs `tests.test_demand_move_binding` with the existing focused QRT suites.

## Exact-head validation

Workflow:
`qrt-pipeline-hardening`

Run:
`37436337463`

Job:
`112178953134`

Head:
`b1d984e12db8b3c19e18f92e3b826d7912889d36`

Result:
- workflow: **SUCCESS**
- focused job: **SUCCESS**
- schema validator install: **SUCCESS**
- intake policy: **SUCCESS**
- focused QRT hardening regressions: **42 tests, OK**
- Chromium audit script syntax: **SUCCESS**
- pinned Chromium install: **SUCCESS**
- mandatory interactive Chromium smoke audit: **SUCCESS**

The previous U04B focused suite had 38 tests; the four U04C demand-move tests account for the increase to 42.

## What U04C establishes

- A primary-demand claim is no longer structurally free-floating.
- The demand label, authored basis and existing canonical crux move are returned together in the classification.
- The crux move has its own digest-bound evidence identity.
- The existing `answer.crux_move_ref` remains the single move authority.
- No topic-specific schema or second move-reference field was created.

## What U04C does not establish

- The resolver still does not automatically infer whether a crux move is APPLY versus JUSTIFY versus another semantic demand; that remains an academic classification judgment constrained by the seven canonical decisive-act definitions.
- U04C does not adjudicate #50/#54 or #51/#55 disagreements.
- No `ADJUDICATION_REQUIRED` state is added yet.
- Existing stress-test labels are not rewritten.

## U04C result

**U04C COMPLETE.**

Parent U04 remains incomplete because the new difficulty rubric + crux-bound demand inputs still need matched-run replay to determine how disagreement is represented without forcing consensus.

Parent denominator remains:
- **P = 3/10 = 30%**
- **E = 3/10 = 30%**

Next bounded task:

**U04D — replay the matched D2/D3 stress-test classifications against the new rubric and crux-bound demand contract; define the minimal unresolved/adjudication representation only if the replay still produces independently valid disagreement.**
