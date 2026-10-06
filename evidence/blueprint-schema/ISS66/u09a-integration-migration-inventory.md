# ISS66 U09A — integration / migration inventory before edits

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U09A only — enumerate every shared contract changed by U02–U07, identify compatibility paths, retained fixtures and actual migration debt before editing data/callers  
**Basis head:** `f88b8031755c50db8a7709a9147ec2af368c10e4`  
**PROTOCOL_REF:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`

## Executive result

The U02–U07 changes do **not** justify a bulk package migration.

The inventory finds four categories:

1. **No data migration:** U02 presentation audit authority and U03 review-binding evidence.
2. **Backward-compatible optional extension:** U04 difficulty component evidence and U05 disclosure availability.
3. **Strictness increase with no affected retained records found:** U06 exact-one scene ownership.
4. **Real caller migration required:** U07 diagnostic evidence, because legacy callers still use a bare `misconception_index` as if it confirmed a diagnosis.

Therefore U09B should migrate **diagnostic callers/tests/docs only**, then run retained contract lanes. It should not manufacture component evidence, availability fields, or owner refs merely to make every historical record look new.

## 1. U02 — presentation/layout authority

### Shared authority changed

- `tools/site-audit/layout-observation.mjs`
- `tools/site-audit/core-page-audit.mjs`

The audit now derives split expectation from the selected blueprint mode. A non-zero `support_fraction` cannot independently manufacture a split requirement when `responsive_policy.expanded = SINGLE_PANE`.

### Legacy compatibility

- Core1A-style `SINGLE_PANE`: retained 0.6 / 0.4 fractions do not force columns.
- Core2-style `STAGE_SUPPORT`: retained 0.42 / 0.58 split remains authoritative.

### Retained fixtures

- `tests/test_blueprint_layout.mjs`
- `evidence/staged-repair/ISS29-set-b/browser/core1a-layout-facts.json`
- `evidence/staged-repair/ISS29-set-b/rendered/core2.html`

### Migration disposition

**NO DATA MIGRATION.**

No blueprint JSON version, blueprint schema, renderer layout generation, learner-quality rule or subject package was changed by U02.

---

## 2. U03 — review provenance / immutable rendered bytes

### Shared authority changed

**None.**

U03 reused the pre-existing:

- `Shared/quality/qrt-pipeline-run.schema.json`
- `Shared/tools/qrt_pipeline_guard.py`

and moved the acceptance behaviors into the dedicated regression lane.

Existing authority already distinguishes:

- `AUTHOR_ONLY`
- `RENDERED`
- `INDEPENDENT_RENDERED`

and binds rendered reviews to exact artifact SHA.

### Legacy compatibility

Legacy rendered review behavior remains unchanged. The stronger independent-review requirement is opt-in through:

`review_requirements.independent_rendered_review_required`

### Retained fixture

- `tests/test_qrt_pipeline_guard.py`

### Migration disposition

**NO MIGRATION.**

Do not add duplicate review basis, artifact-digest or dependency-fingerprint fields.

---

## 3. U04 — difficulty evidence + primary-demand/crux binding

### Shared authorities changed

- `Shared/vocabularies/learner-question-metadata.v1.json` → version 1.1.0
- `Shared/library/package.schema.json`
- `Shared/vocabularies/cognitive-demand.v1.json` → version 1.1.0
- `Shared/tools/question_review_matrix.py`

### Difficulty change

A canonical subject-neutral 0/1/2 rubric now defines the five difficulty dimensions.

The package schema adds optional:

`difficulty.component_evidence`

When present it must supply all five evidence strings. When absent, legacy difficulty records remain schema-valid.

### Demand/crux change

Primary cognitive demand now classifies the **existing** canonical:

`answer.crux_move_ref`

QRT resolution requires that ref to resolve inside:

`answer.reasoning_route[]`

and derives:

- `primary_move_ref`
- `primary_move_kind`
- `primary_move_action`
- `basis_digests.primary_move`

No second authored move ref was added.

### Canonical-data scan

Scanned the 23 current subject-library JSON files under Mathematics / Physics / Chemistry at the U09A basis head.

Result:

| Measure | Count |
| --- | ---: |
| questions scanned | 250 |
| questions with existing analysis difficulty | 81 |
| with new `component_evidence` | 0 |
| without `component_evidence` | 81 |
| normalized `grade9v3:cognitive_demand.primary` records | 0 |

Interpretation:

- the 81 historical difficulty records are **valid by design**;
- bulk authoring 405 evidence strings would invent retrospective justification and is forbidden;
- no current canonical normalized-demand record needs a crux migration;
- legacy stress-test disagreements stay `REPLAY_REQUIRED_UNDER_EVIDENCED` until freshly reviewed under the new contract.

### Retained fixtures

- `tests/test_difficulty_contract.py`
- `tests/test_demand_move_binding.py`
- `tests/test_question_review_matrix.py`
- `evidence/blueprint-schema/ISS66/u04d-matched-classification-replay.json`

### Migration disposition

**NO BULK DATA MIGRATION.**

Only a future record entering new-contract adjudication needs:
- complete component evidence; and
- a resolvable crux-bound cognitive-demand claim.

---

## 4. U05 — protected work / support disclosure eligibility

### Shared authorities changed

- `Shared/library/package.schema.json`
- `Shared/tools/core2_v2.py`
- `Shared/tools/render_core.py`

The existing `grade9v3:core2_support_plan` remains the sole authority.

Optional `availability` was added to:
- `support_completions[]`;
- visual `stages[]`.

States:

- `PRE_ATTEMPT_SAFE`
- `AFTER_ATTEMPT`
- `POST_SOLUTION`

### Legacy default path

When `availability` is omitted:

- protected-completing support/stage → `POST_SOLUTION`;
- `reveals=ANSWER` → `POST_SOLUTION`;
- other support → `PRE_ATTEMPT_SAFE`.

The old:

`eligible_pre_solution`

boolean remains as a compatibility projection.

### Live-data scan

Current canonical subject libraries contain:

`0`

questions with `grade9v3:core2_support_plan`.

There is therefore no canonical support-plan migration to perform.

### Retained fixtures

- `tests/fixtures/staged_set_b/cases.json`
- `tools/staged_set_b_replay.py`
- `tests/test_staged_support_repair.py`
- `tests/iss66_support_state_fixture.py`
- `tests/iss66_support_state_browser.mjs`

The staged Set B replay intentionally omits `availability`, which is valuable retained evidence that legacy protected support still defaults to solution-only.

### Migration disposition

**NO BULK MIGRATION.**

Add `availability` only where an authored record needs behavior different from the old default, especially `AFTER_ATTEMPT`.

---

## 5. U06 — representation scene ownership

### Shared authority changed

`Shared/library/package.schema.json`

For `scene_instance`, owner selection changed:

`anyOf → oneOf`

over the existing:

- `microtopic_ref`
- `question_ref`

### Compatibility path

Still valid:

- microtopic-only;
- question-only.

Now invalid:

- both refs;
- neither ref.

### Canonical / retained scan

Across the 23 canonical subject-library JSON files:

| Scene ownership | Count |
| --- | ---: |
| total scene instances | 10 |
| microtopic-only | 10 |
| question-only | 0 |
| both | 0 |
| neither | 0 |

Additional retained fixtures checked:

- `golden/units/G-MATH-LINEAR-CONSTRAINT/records.json` — microtopic-only valid;
- `tests/fixtures/render/thin-kin-2d-motion.v1.json` — microtopic-only valid;
- staged Set B adopted cases — question-only valid.

No retained/canonical invalid owner-cardinality instance was found.

### Retained tests

- `tests/test_representation_binding_contract.py`
- existing staged-support replay regressions

### Migration disposition

**NO RECORD MIGRATION.**

Do not touch valid single-owner scene instances.

---

## 6. U07 — diagnostic evidence before misconception repair

### Shared authorities changed

- new `Shared/quality/diagnostic-evidence.schema.json`
- `Shared/tools/feedback.py`
- `Shared/tools/study_session.py`

The evidence chain is now:

```text
hypothesis
→ canonical diagnostic probe
→ observed learner response
→ CONFIRMED | REFUTED | INDETERMINATE
→ misconception-specific repair only if CONFIRMED
→ fresh verification
```

### Compatibility character

The API/CLI still accepts:

`misconception_index`

so the syntax is retained.

But its meaning is deliberately narrower:

> it is now a hypothesis selector, not proof of confirmation.

A caller that supplies only the index receives diagnosis behavior, not a confirmed misconception repair.

This is the one U02–U07 change with concrete migration debt.

### Legacy callers/tests found

Current branch still contains old expectations in:

- `tests/test_feedback.py` — multiple bare-index calls assert `REPAIR`;
- `tests/test_study_session.py` — confirmed-misconception test supplies only the index;
- `tests/test_neetprep_relative_motion_pilot.py`;
- `tests/test_c6_examside_motion_in_plane.py`;
- `docs/DRY-RUN-PHYSICS-RELATIVE-MOTION-Q4.md`;
- `docs/HIGH-LIKELIHOOD-LEARNING-SCENARIOS.md`;
- `docs/CORE-IMPLEMENTATION-PLAN-WORKSHEET-STUDY-FEEDBACK.md`.

The dedicated new contract test is already correct:

- `tests/test_diagnostic_evidence_contract.py`

and must remain the source of the negative guarantee that bare index alone does **not** repair.

### Migration rule for U09B

Only migrate a legacy example/test to `CONFIRMED` when its scenario already semantically asserts a discriminating learner response.

Such callers must add:

- `diagnostic_response`;
- `diagnosis="CONFIRMED"`;
- `diagnostic_basis`.

Do not mechanically set every old index to `CONFIRMED`.

If an old fixture does not actually record discriminating evidence, change its expected next action to `DIAGNOSE` instead.

---

## 7. Validation-lane inventory

### QRT hardening lane

Retain:

- `tests.test_qrt_pipeline_guard`
- `tests.test_difficulty_contract`
- `tests.test_demand_move_binding`

### Learner-quality code lane

Retain dedicated steps:

- `Diagnostic evidence contract`
- `Representation instance binding contract`
- `Core2 staged support contract`
- `Existing blueprint layout observation regressions`

At basis head `f88b8031755c50db8a7709a9147ec2af368c10e4`:

- learner-platform-code-tests run `37446718351`;
- code-tests job `112213230793`;
- all four dedicated ISS66 steps are successful.

The informational broad Python aggregation remains non-green:

`190 tests; 7 failures, 1 error, 1 skip`

and includes unrelated known renderer/ledger failures. U09 must not claim those failures are all caused by migration debt.

---

## 8. U09B edit boundary

U09B should do **only** the proven migration work:

1. migrate legacy diagnostic tests/examples that truly mean “confirmed” to explicit evidence;
2. preserve an explicit bare-index → `DIAGNOSE` regression;
3. update stale diagnostic documentation fields/flows;
4. run the dedicated U02–U07 retained lanes;
5. inspect the informational suite delta without claiming unrelated failures.

U09B should **not**:

- bulk-fill 81 legacy `component_evidence` objects;
- add `availability` to plans that already behave correctly by omission;
- rewrite valid single-owner scene instances;
- change QRT review provenance schema/guard;
- touch blueprint registry/layout policy records;
- manufacture adjudication state for historical under-evidenced stress tests.

## U09A result

**U09A COMPLETE. No production or migration edit performed.**

Parent U09 remains incomplete.

Parent denominator remains:

- **P = 8/10 = 80%**
- **E = 8/10 = 80%**

Next bounded task:

**U09B — migrate only the identified legacy diagnostic callers/tests/docs to the typed evidence contract, preserve bare-index DIAGNOSE behavior, and replay all retained U02–U07 focused lanes before closing U09.**
