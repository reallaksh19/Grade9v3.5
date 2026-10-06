# ISS66 U05B — explicit support disclosure boundaries

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U05B only — distinguish after-attempt support from solution-only support while preserving the existing protected-move model  
**Tested implementation head:** `f90fdf327f5ca8e1eba02194dac86369841741f0`

## Contract extension

The existing `grade9v3:core2_support_plan` remains the sole support-protection authority.

Added one optional field:

`availability`

to:
- `support_completions[]`; and
- individual visual `stages[]`.

Allowed values:

- `PRE_ATTEMPT_SAFE`
- `AFTER_ATTEMPT`
- `POST_SOLUTION`

No new protected-act object, support lane, or topic-specific schema was created.

## Backward compatibility

Omitted `availability` preserves PR #65 behavior:

- a support row/stage that completes protected work defaults to `POST_SOLUTION`;
- an answer-revealing support row defaults to `POST_SOLUTION`;
- other support retains pre-attempt eligibility.

Therefore legacy adopted plans do not silently move earlier in the learner journey.

## Fail-closed contradictions

The Core2 projection rejects:

- `PRE_ATTEMPT_SAFE` when the row/stage completes a protected move;
- `PRE_ATTEMPT_SAFE` or `AFTER_ATTEMPT` when the support row is already typed `reveals=ANSWER`;
- unknown availability values.

The implementation still does not infer completion from prose.

## Projection changes

`Shared/tools/core2_v2.py` now derives an explicit availability for every projected support row and provides:

- `pre_solution_support(...)`
- `after_attempt_support(...)`
- `post_solution_support(...)`

Visual bindings now expose:

- `pre_attempt_stage_refs`
- `after_attempt_stage_refs`
- `post_solution_stage_refs`

The existing `eligible_pre_solution` boolean remains as a compatibility projection of `PRE_ATTEMPT_SAFE`.

## Renderer changes

`Shared/tools/render_core.py` now keeps three disclosure surfaces distinct:

1. pre-attempt support remains in the existing hint ladder;
2. `AFTER_ATTEMPT` support renders in a separate commitment-gated **More support after your attempt** payload;
3. `POST_SOLUTION` support remains inside **Answer and working**.

Visual stages use the same boundary model. Both after-attempt and solution-only figures remain observationally `POST_ATTEMPT` figures for learner-quality tooling, while their disclosure containers remain distinct.

## Focused regressions

`tests/test_staged_support_repair.py` adds coverage that:

- explicit after-attempt support leaves the solution-only support list;
- explicit `POST_SOLUTION` is behaviorally identical to the legacy protected default;
- `PRE_ATTEMPT_SAFE` cannot complete protected work;
- a protected visual stage can be placed in `AFTER_ATTEMPT` without also entering the solution-only stage list.

The original PR #65 tests remain in place, including the default solution-only behavior for the `p_0(x)` support and WORKED stage.

## Intermediate test correction

The first exact-head broad run found one new test assertion failure.

The production split was correct; the test searched globally for the text `p_0(x)`, which also exists in a separate legacy solution-only visual. The assertion was narrowed to the exact `data-g9-support-source` identity of the support row being moved.

No production behavior changed for that correction.

## Dedicated CI evidence

`.github/workflows/learner-quality.yml` now has a non-informational step:

`Core2 staged support contract`

which runs only:

`python3 -m unittest tests.test_staged_support_repair`

At exact head `f90fdf327f5ca8e1eba02194dac86369841741f0`:

- learner-platform-code-tests run `37439011441`
- code-tests job `112187832348`
- **Core2 staged support contract: SUCCESS**

The broader informational Python suite remains separate and is not used as U05B acceptance authority.

## U05B result

**U05B COMPLETE.**

Parent U05 remains incomplete until browser-state replay confirms that AFTER_ATTEMPT support materialises after commitment independently of the full solution disclosure.

Parent denominator remains:
- **P = 4/10 = 40%**
- **E = 4/10 = 40%**

Next bounded task: **U05C — browser-state replay of pre-attempt → committed → full-solution disclosure using the staged-support fixture.**
