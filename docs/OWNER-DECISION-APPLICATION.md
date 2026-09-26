# Owner decision application

The planner never waits for the owner. Every input it used to ask for is filled with a
default (median learner, `PRACTICE` purpose, `ALLOW_AUTHORED_CANDIDATES`) or given to the
agent as a research duty (source basis, source drift); see `defaults_applied` and
`agent_actions` in the plan. The owner may still **override** any of those defaults or duties.
Overrides must not be applied by ad-hoc request editing.

This layer turns owner answers into a typed, stale-detectable artifact and immediately
re-plans the request after applying them.

## Closed loop

```text
short request
   ↓
plan_request.py
   ↓
defaults_applied / agent_actions   (overridable_decisions)
   ↓
owner-decisions.json               (optional overrides)
   ↓
apply_owner_decisions.py
   ↓
patched request
   ↓
re-plan immediately
   ↓
remaining overridable decisions / agent actions / execution packet
```

The owner-decision artifact pins both:

- the request digest; and
- the full planner-result digest.

If either the request or the architecture changes after the artifact was prepared, the
decision is rejected as stale.

## Supported decisions

The current typed contract covers every override the planner can offer:

- `LEARNER_ENTRY`
- `CORE2A_PURPOSE`
- `CORE2B_PURPOSE`
- `SOURCE_BASIS`
- `SOURCE_BASIS_DRIFT_DECISION`
- `SUPPLEMENTAL_QUESTION_POLICY`

CI scans every committed plan fixture and fails if the planner offers an override with no
typed decision field, or if it ever lists a `required_owner_input` (the planner must default
or research instead of waiting).

## Incremental answers are legal

The owner does not need to answer every question at once.

A decision artifact may override only a subset of the currently offered decisions. The
applier then re-plans and returns the remaining overridable decisions.

## Source-basis drift

When a verified receipt reports `DRIFT`, the planner gives the agent the duty
`RESOLVE_SOURCE_BASIS_DRIFT` (research which basis matches the topic). The owner may override
with:

```text
KEEP_SUPPLIED_DESPITE_DRIFT
or
CHANGE_SOURCE_BASIS:<receipt-backed replacement candidate>
```

### Keep supplied

The applier records the drift acknowledgement and leaves the original receipt pinned.
Re-planning then evaluates that source exactly as it currently exists. If practice coverage
is insufficient, the agent receives `AUTHOR_SUPPLEMENTAL_PRACTICE`.

### Change source basis

The replacement must be one of the verified receipt's `replacement_candidates`. An
arbitrary locator is rejected.

Changing the basis automatically clears:

- the old `source_receipt_ref`;
- the drift acknowledgement;
- any `supplemental_question_policy` derived from the old source's gap.

The re-planned request therefore returns to:

```text
INSPECT_AND_INGEST_SOURCE_BASIS
```

No evidence or policy from the old source silently survives the replacement.

## Learner entry

The owner may provide a learner profile ref, an explicit rung or an owner knowledge estimate.
Without one — including an explicit `unknown` — the planner uses the default median learner
(`owner_estimate.knowledge_percentage = 50`, basis `DEFAULT_MEDIAN`). Learner-routed products
are never blocked for lack of learner data; a short diagnostic adjusts from actual attempts.

## Unsolicited decisions

The applier accepts only overrides of what the pinned plan defaulted or assigned to the agent.
For example, once a request already names its source basis, a `SOURCE_BASIS` override is
rejected as unsolicited.

## Commands

Generate a fillable decision template:

```text
python3 Shared/tools/apply_owner_decisions.py --request Requests/example.plan-request.json --template
```

Apply decisions and re-plan:

```text
python3 Shared/tools/apply_owner_decisions.py --request Requests/example.plan-request.json --decisions /path/to/owner-decisions.json
```

Audit the planner/applier contract:

```text
python3 Shared/tools/apply_owner_decisions.py --audit --enforce
```

Behavioral falsifiers live in `tests/test_owner_decisions.py`.
