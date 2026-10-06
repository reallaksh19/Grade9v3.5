# ISS66 U04D — matched classification replay

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U04D only — replay #50/#54 and #51/#55 against the U04B difficulty-evidence and U04C crux-bound demand contracts

## Replay admission bar

A classification is eligible for like-for-like adjudication only when the exact question record provides:

1. complete per-component evidence for all five difficulty dimensions against the U04B 0/1/2 rubric;
2. a canonical `answer.crux_move_ref` resolving inside `answer.reasoning_route[]`;
3. normalized cognitive-demand evidence with a non-empty basis that the U04C resolver can bind to that canonical crux.

The frozen stress-test labels are preserved as historical claims. They are not rewritten to make them fit this later contract.

## Whole-cohort replay

| Frozen run | Questions | U04B component evidence | Canonical crux resolves | Normalized crux-bound demand basis | Replay status |
| --- | ---: | ---: | ---: | ---: | --- |
| #50 D2 Set A | 10 | 0/10 | 0/10 in the frozen question ledger evidence | 0/10 | `REPLAY_REQUIRED_UNDER_EVIDENCED` |
| #54 D2 Set B | 10 | 0/10 | 10/10 | 0/10 | `REPLAY_REQUIRED_UNDER_EVIDENCED` |
| #51 D3 Set A | 10 | 0/10 | 10/10 | 0/10 | `REPLAY_REQUIRED_UNDER_EVIDENCED` |
| #55 D3 Set B | 10 | 0/10 | 10/10 | 0/10 | `REPLAY_REQUIRED_UNDER_EVIDENCED` |

Therefore **0/40 frozen classifications are admissible for new-contract independent adjudication without fresh evidence authoring**.

## D2 pair result — #50 / #54

The old evidence remains valuable:
- #50 derives D1–D3 inside the intended D2 cohort;
- #54 reports all ten as D2;
- Q6 differs D3 vs D2 despite both selecting JUSTIFY;
- Q10 differs D3/JUSTIFY vs D2/EXPLAIN.

But this is not yet a valid U04B/U04C adjudication pair:
- neither run records the five new per-component evidence strings;
- #50's frozen question-ledger/review evidence does not carry the canonical answer route/crux needed by U04C;
- #54 carries routes/cruxes but still lacks normalized crux-bound demand evidence.

**Disposition:** retain the disagreement as a calibration target; do not force either label and do not create a shared adjudication enum from legacy under-evidenced claims.

## D3 pair result — #51 / #55

The old convergence/divergence remains:
- Q8 independently selects JUSTIFY;
- #51 scores Q8 9/D4;
- #55 scores Q8 7/D3.

Both owner banks carry canonical reasoning routes/crux refs, but:
- neither has U04B per-component evidence;
- cognitive-demand data remains in the legacy analysis shape without the normalized non-empty basis required by U04C;
- matched records can also choose different crux moves, which means a later replay must first agree on what learner-owned bottleneck is being classified before comparing the demand label.

**Disposition:** fresh replay required. No shared adjudication state yet.

## Adjudication decision

**NO_SHARED_ADJUDICATION_STATE_ADDED.**

The promised U04D gate was:

> add an unresolved/adjudication representation only if two independently valid classifications still disagree under the same evidence contract.

That condition has not occurred. Adding `ADJUDICATION_REQUIRED` now would encode a state before its admission criteria have ever been satisfied.

For continuity, this evidence lane uses:

`REPLAY_REQUIRED_UNDER_EVIDENCED`

This is an evidence status, not a new runtime/schema authority.

## U04 result

U04 now has:
- deterministic score → band projection and requested-band separation;
- canonical 0/1/2 anchors for all five authored difficulty dimensions;
- complete optional per-component evidence shape for new adjudicated records;
- primary cognitive demand bound to the existing canonical crux move;
- matched-run replay showing legacy disagreements are not silently accepted or forced;
- an explicit reason **not** to add adjudication-state machinery yet.

**U04 COMPLETE and successor-safe evidenced.**

Parent denominator:
- **P = 4/10 = 40%**
- **E = 4/10 = 40%**

Future replay of #50/#54 and #51/#55 must author evidence under the new rubric/crux contract before any independent disagreement can earn an adjudication state.
