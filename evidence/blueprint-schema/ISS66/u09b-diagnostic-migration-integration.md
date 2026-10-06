# ISS66 U09B — diagnostic caller migration + retained integration replay

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U09B only — migrate proven legacy diagnostic callers/docs, preserve non-misconception repair compatibility, and replay retained U02–U07 lanes  
**Tested implementation head:** `6be1a704bbd9fef6f15292d41ed2277badd5c0ff`  
**PROTOCOL_REF:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`

## Migration performed

### Legacy tests / pilots

Migrated confirmed-diagnosis scenarios in:

- `tests/test_feedback.py`
- `tests/test_study_session.py`
- `tests/test_neetprep_relative_motion_pilot.py`
- `tests/test_c6_examside_motion_in_plane.py`

Confirmed scenarios now carry the evidence required by U07:

- canonical misconception index / hypothesis;
- learner response to the canonical diagnostic prompt;
- `diagnosis = CONFIRMED`;
- non-empty evaluator basis.

Direct `feedback.run(...)` fixtures build canonical diagnostic evidence through `feedback.diagnostic_evidence_for(...)`.

`study_session.attempt(...)` fixtures pass:

- `misconception_index`
- `diagnostic_response`
- `diagnosis`
- `diagnostic_basis`

The index therefore remains an identity/hypothesis selector, not proof by itself.

### Session-boundary contract

Updated:

`tests/test_high_likelihood_scenario_matrix_contract.py`

The matrix/session separation test now also forbids durable skill matrices from containing:

- `diagnostic_response`
- `diagnosis`
- `diagnostic_basis`
- `diagnostic_evidence`

These remain transient learner/session evidence.

### Documentation

Updated:

- `docs/DRY-RUN-PHYSICS-RELATIVE-MOTION-Q4.md`
- `docs/HIGH-LIKELIHOOD-LEARNING-SCENARIOS.md`
- `docs/CORE-IMPLEMENTATION-PLAN-WORKSHEET-STUDY-FEEDBACK.md`

Human guidance now matches runtime semantics:
- a bare misconception index is not confirmation;
- diagnosis records the canonical probe response and evaluator basis;
- `INDETERMINATE` / `REFUTED` do not enter misconception-specific repair;
- only `CONFIRMED` does.

## Integration defect found by first U09 run

Initial migration head:

`1abb266b3c4820585b47d14c7f8f838e286268d2`

Workflow:
`learner-platform-code-tests`

Run:
`37456537971`

Job:
`112245420319`

The new dedicated:

`U09 diagnostic caller migration`

ran **85 tests** and exposed four failures.

Two examples were generic feedback repairs:

- explicit prerequisite-capability failure expected an existing microtopic repair;
- explicit question `repair_ref` expected an existing teaching-step repair.

Two were existing NLM study-session repairs that also did not claim a specific misconception.

All four returned `DIAGNOSE` after U07.

### Root cause

The U07 implementation had placed the confirmed-diagnostic gate **before all repair routing**.

That was too broad.

The intended U07 contract was:

> only misconception-specific repair requires a confirmed misconception diagnosis.

It did **not** intend to block:
- an explicit canonical question `repair_ref`;
- a generic microtopic repair after the failed capability is already attributable and retry support is exhausted.

The first U09 run therefore found a real integration regression rather than missing diagnostic evidence.

## Compatibility correction

Updated:

`Shared/tools/feedback.py`

The repair boundary is now:

### Diagnostic claim present

When either:
- `evaluation.diagnostic_evidence` is supplied; or
- legacy `evaluation.misconception_index` is supplied,

the runtime will not enter misconception-specific repair unless the diagnostic evidence is valid and `CONFIRMED`.

Thus:
- bare index → `DIAGNOSE`;
- invalid evidence → `DIAGNOSE`;
- `INDETERMINATE` → `DIAGNOSE`;
- `REFUTED` → `DIAGNOSE`;
- complete `CONFIRMED` evidence may select the corresponding misconception repair.

### No diagnostic claim present

When the caller has **not** claimed a specific misconception, the existing non-misconception repair path remains available after normal hint/attribution rules:

- explicit question `repair_ref` → canonical teaching-step repair;
- otherwise one attributable microtopic → generic microtopic repair.

No misconception is called confirmed in those paths.

This restores pre-U07 generic repair compatibility without weakening the U07 evidence gate.

## Dedicated migration CI

Updated:

`.github/workflows/learner-quality.yml`

Added non-informational step:

`U09 diagnostic caller migration`

which runs:

```text
tests.test_feedback
tests.test_study_session
tests.test_neetprep_relative_motion_pilot
tests.test_c6_examside_motion_in_plane
tests.test_high_likelihood_scenario_matrix_contract
```

## Exact-head retained validation

### QRT / U03–U04

Workflow:
`qrt-pipeline-hardening`

Run:
`37456950847`

Job:
`112246780996`

Result:
- focused-regressions: **SUCCESS**
- focused QRT hardening: **42 tests, OK**
- mandatory interactive Chromium smoke: **SUCCESS**

This retains:
- U03 review provenance / byte binding;
- U04 difficulty rubric/evidence;
- U04 primary-demand/crux binding.

### Learner-quality code lane / U02 + U05 + U06 + U07 + U09

Workflow:
`learner-platform-code-tests`

Run:
`37456950863`

Job:
`112246780871`

Result:
- job: **SUCCESS**
- `Diagnostic evidence contract`: **7 tests, OK**
- `U09 diagnostic caller migration`: **85 tests, OK**
- `Representation instance binding contract`: **4 tests, OK**
- `Core2 staged support contract`: **25 tests, OK**
- `Existing blueprint layout observation regressions`: **8 tests, 8 pass, 0 fail**
- `blueprint-v2-render-snapshots` job: **SUCCESS**

### Retained U05 browser-state replay

Job:
`112246781553` — `core2-v2-browser-audit`

The isolated step:

`ISS66 staged support browser-state replay`

is **SUCCESS**.

Observed result:

```json
{
  "pre_attempt_locked": true,
  "after_attempt_support_visible": true,
  "solution_closed_during_after_attempt_support": true,
  "worked_visual_visible_only_after_solution_open": true,
  "moved_support_ref": "scaffolds[1]"
}
```

The next unrelated step:

`Render real Motion-in-2D product`

still fails with the existing two render gaps and exits before the remaining browser audit stages.

That job-level failure is not treated as an ISS66 migration regression because:
- the retained ISS66 browser-state replay passed first;
- the same broader Motion2D render gap pre-dates U09;
- U09 made no Motion2D source/representation migration.

## Informational broad suite

The informational platform aggregation remains:

- **190 tests**
- **7 failures**
- **1 error**
- **1 skipped**

This is the same broader non-green class already recorded before U09 migration.

U09 does not relabel those failures as green and does not use the informational step for acceptance.

## Data-migration result

U09A's no-bulk-migration decisions remain unchanged:

- no retrospective difficulty `component_evidence` authoring;
- no support `availability` backfill;
- no scene-owner rewrite;
- no U03 review-schema rewrite;
- no blueprint registry migration;
- no historical stress-test adjudication fabrication.

The only proven migration debt was diagnostic callers/docs, and that debt is now migrated.

## U09 acceptance result

U09 required integration/migration of the U02–U07 contract changes while preserving legacy compatibility.

That is now evidenced:

- optional/new contracts remain optional where declared;
- strict scene ownership has no affected retained record;
- legacy support omission preserves behavior;
- old diagnostic examples no longer equate an index with confirmation;
- generic non-misconception repair behavior is restored;
- all dedicated U02–U07 focused lanes pass on one exact implementation head.

## U09 result

**U09 COMPLETE and successor-safe evidenced.**

Parent denominator:

- **P = 9/10 = 90%**
- **E = 9/10 = 90%**

Next bounded unit:

**U10A — construct the final #49–#56 replay/handoff matrix against the integrated U02–U09 contracts, with explicit PASS / REPLAY_REQUIRED / NO_CHANGE / pre-existing-blocker dispositions before issue closure.**
