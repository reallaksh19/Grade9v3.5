# Practical study-session runner

`Shared/tools/study_session.py` is a thin orchestration layer over the existing core.
It does not create new curriculum truth, grade free-form answers, or silently update learner
state.

The intended loop is:

```text
worksheet capability map
→ session-readiness check
→ rough starting estimate / existing learner evidence
→ ordered study route
→ worksheet attempt
→ diagnosis / repair / fresh verification
→ observation draft
→ review date
```

## First supported pilot: Relative Motion

Relative Motion is currently `SESSION_READY_WITH_BRIDGE`.

The local Relative Motion matrix has teaching, Core1A/Core1B reconstruction, misconception
diagnosis/repair, and exit verification on all four rungs. Signed-coordinate arithmetic is
kept visible as a Mathematics bridge rather than assumed mastered.

A rough parent estimate can use the subtopic name directly:

```bash
python3 Shared/tools/study_session.py plan \
  --map tests/fixtures/study_session/relative-motion.worksheet.json \
  --estimate "Relative motion=60" \
  --readable
```

The estimate chooses where to try first inside the matrix. It never marks earlier
capabilities demonstrated.

## Validity versus execution readiness

The plan now keeps two different ideas separate:

- `valid=true`: the worksheet route and capability delivery graph are structurally sound;
- `ready=true`: the plan is valid and every external-provider prerequisite needed for this
  learner is already satisfied.

A Relative Motion plan can therefore be valid while still returning `ready=false` and a
Mathematics bridge as the first action. If learner evidence already demonstrates that
prerequisite, the same route becomes ready and the bridge is skipped.

All prerequisite delivery decisions use the shared `capability_delivery` resolver rather
than reimplementing bridge logic in the session layer.

## Session-only owner resolution

When the plan returns `OWNER_DECISION`, the owner may resolve only the current session
without editing canonical content.

Two narrow forms are supported:

```text
CAPABILITY=LOCATION:MATRIX_ID:RUNG
CAPABILITY=EXTERNAL:PROVIDER
```

`LOCATION` may select only a location already offered by the canonical route.
`EXTERNAL` supplies a session-only bridge label and never creates a canonical provider.

Example:

```bash
python3 Shared/tools/study_session.py plan \
  --map path/to/worksheet.json \
  --owner-choice "CAP-EXAMPLE=EXTERNAL:Owner-selected tutor" \
  --readable
```

Applied owner choices remain visible in the report, use `EXECUTE_WITH_FALLBACK`, and do
not mutate matrices, capabilities, learner evidence, or academic review state.

## Record one attempt

The runner does not decide whether a free-form answer is correct. A human or another
approved evaluator supplies the outcome.

Example: the learner ignored direction in a relative-velocity question.

```bash
python3 Shared/tools/study_session.py attempt \
  --map tests/fixtures/study_session/relative-motion.worksheet.json \
  --question SCHOOL-REL-Q1 \
  --result INCORRECT \
  --failed-capability CAP-RELATIVE-V \
  --error-stage CONCEPT \
  --response-summary "Subtracted the speeds as scalars and ignored direction." \
  --when 2026-09-18 \
  --readable
```

For a transient worksheet question there is no invented hint ladder. The runtime diagnoses
from the canonical microtopic. If a misconception is then confirmed, pass its index:

```bash
python3 Shared/tools/study_session.py attempt \
  --map tests/fixtures/study_session/relative-motion.worksheet.json \
  --question SCHOOL-REL-Q1 \
  --result INCORRECT \
  --failed-capability CAP-RELATIVE-V \
  --error-stage CONCEPT \
  --misconception-index 0 \
  --diagnostic-response "<what the learner said/did on the canonical diagnostic prompt>" \
  --diagnosis CONFIRMED \
  --diagnostic-basis "<why that probe response supports this diagnosis>" \
  --when 2026-09-18 \
  --readable
```

A bare `--misconception-index` is only a hypothesis selector and is not enough to confirm a
misconception. The runtime requires the canonical diagnostic prompt, an observed response,
an explicit `CONFIRMED | REFUTED | INDETERMINATE` evaluator conclusion and a non-empty basis
before misconception-specific repair. `INDETERMINATE` and `REFUTED` remain in diagnosis.

The result may include a canonical repair, a fresh verification question or exit task, an
observation draft, diagnostic evidence, and a review date.

## Safety / anti-drift rules

- Matrix readiness remains truthful, but it is not a blanket execution kill switch. If the
  actually demanded rung is usable inside a `PILOT_READY` or `NOT_READY` matrix, the
  session may continue as `EXECUTE_WITH_FALLBACK` while the surrounding gaps remain visible.
- If the demanded delivery/rung cannot be selected safely, return `OWNER_DECISION` rather
  than guessing. These are the only two exceptional execution dispositions added by the
  fallback-first policy.
- `OWNER_DECISION` propagates through prerequisite dependencies: a dependent capability is
  not allowed to leap over an unresolved prerequisite. Unrelated worksheet branches may
  still continue.
- `PILOT_READY` remains visibly weaker than `SESSION_READY`, and `NOT_READY` remains a
  truthful matrix-level readiness statement.
- External worksheet questions remain transient demand; they are not automatically promoted
  to Core2/source custody.
- External-provider prerequisites remain explicit bridges.
- Rough percentages are routing hints, never mastery evidence.
- Attempt evaluation is supplied by the caller.
- Observation drafts are returned but never written automatically.
- Academic/source warnings remain visible to the parent even when a private pilot is
  mechanically executable.

## What comes next

Use live learner sessions and the independent Question → Study Map benchmark to test the
fallback boundary. New tightening rules should not create additional execution-state enums:
normal actions remain normal, safe degradation uses `EXECUTE_WITH_FALLBACK`, and cases that
need a human choice use `OWNER_DECISION`.
