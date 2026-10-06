# ISS66 U07B — typed diagnostic evidence gate

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U07B only — prevent unsupported confirmed misconception diagnoses while retaining authored hypotheses, repair and fresh verification  
**Tested implementation head:** `54271dc9622b86ff628865f2f4bb32a8b57a3dd3`

## New shared diagnostic evidence contract

Added:

`Shared/quality/diagnostic-evidence.schema.json`

Schema id:

`grade9v3-diagnostic-evidence/v1`

A diagnostic evidence record now contains:

- `misconception_index`
- `probe`
- `observed_response`
- `diagnosis`
- `basis`

Diagnosis is exactly one of:

- `CONFIRMED`
- `REFUTED`
- `INDETERMINATE`

The schema requires all five fields and rejects extra fields.

## Canonical probe binding

`Shared/tools/feedback.py` now builds/validates diagnostic evidence against the existing canonical misconception row.

The runtime:
- resolves the misconception through the already-authored microtopic;
- resolves the exact canonical `diagnostic_prompt`;
- records that prompt as `probe`;
- requires a non-empty observed learner response;
- requires a non-empty evaluator basis;
- requires a valid diagnosis enum;
- rejects a probe string that does not equal the current canonical prompt.

The runtime still does **not** automatically infer whether the learner response confirms the misconception. The evaluator supplies the diagnosis; the contract makes the evidence supporting that judgment explicit.

## Bare index no longer confirms

The previous path:

```text
wrong answer
+ failed capability
+ misconception_index = 0
→ MISCONCEPTION_REPAIR
```

is no longer accepted as a confirmed diagnosis.

A bare index is now treated only as a hypothesis selector. Without complete diagnostic evidence the report:
- remains in `DIAGNOSE`;
- does not return `repair`;
- exposes `DIAGNOSTIC_EVIDENCE_REQUIRED`;
- does not call the misconception confirmed.

## Diagnosis-state behavior

### INDETERMINATE

Valid canonical probe/response evidence with:

`diagnosis = INDETERMINATE`

stays in:

`next_action = DIAGNOSE`

No misconception-specific repair is selected.

### REFUTED

Valid evidence with:

`diagnosis = REFUTED`

also remains in diagnosis and does not select that misconception's repair.

### CONFIRMED

Only complete valid evidence with:

`diagnosis = CONFIRMED`

may pass the misconception index into the existing `repair_for(...)` path.

The repair remains canonical authored content.

After repair, the existing fresh verification requirement remains unchanged:
- fresh same-capability question when available;
- otherwise canonical exit-task verification;
- no silent mastery promotion.

## Study-session integration

`Shared/tools/study_session.py` now supports:

- `diagnostic_response`
- `diagnosis`
- `diagnostic_basis`

alongside the existing `misconception_index`.

The CLI adds:

- `--diagnostic-response`
- `--diagnosis CONFIRMED|REFUTED|INDETERMINATE`
- `--diagnostic-basis`

When complete inputs are supplied, the session runner resolves and records the exact canonical probe before feedback routing.

The existing `--misconception-index` flag is retained for compatibility as a hypothesis selector, but it is intentionally insufficient for misconception-specific repair.

## Focused regression surface

Added:

`tests/test_diagnostic_evidence_contract.py`

Seven focused tests prove:

1. the schema requires probe, response, diagnosis and basis;
2. a bare misconception index cannot confirm or repair;
3. `INDETERMINATE` stays in diagnosis;
4. `REFUTED` does not select that repair;
5. `CONFIRMED` routes to canonical repair and then fresh verification;
6. a non-canonical probe is rejected;
7. the study-session runner resolves the canonical probe and carries complete evidence before repair.

## Exact-head validation

Workflow:

`learner-platform-code-tests`

Run:

`37443777194`

Job:

`112203556785` — `code-tests`

Head:

`54271dc9622b86ff628865f2f4bb32a8b57a3dd3`

Result:
- workflow: **SUCCESS**
- code-tests job: **SUCCESS**
- `Diagnostic evidence contract`: **SUCCESS**
- focused diagnostic suite: **7 tests, OK**
- `Representation instance binding contract`: **SUCCESS**
- `Core2 staged support contract`: **SUCCESS**
- blueprint-v2-render-snapshots job: **SUCCESS**

The separate `core2-v2-browser-audit` job remained failure on its broader product path. U07 acceptance does not rely on that job.

## Documentation migration

Updated:
- `docs/STUDY-SESSION-RUNNER.md`
- `docs/RELATIVE-MOTION-LIVE-PILOT-01.md`

The executable and human guidance now agree:
- do not equate a wrong answer with a confirmed misconception;
- record the response to the canonical diagnostic prompt;
- use `INDETERMINATE` when the evidence does not discriminate;
- only `CONFIRMED` may select misconception-specific repair.

## U07 acceptance result

U07 required separation of:

```text
hypothesis
→ discriminating probe
→ observed response
→ diagnosis / indeterminate
→ repair
→ recheck
```

That chain is now explicit:

- **hypothesis:** existing `wrong_idea`;
- **probe:** existing canonical `diagnostic_prompt`;
- **observed response:** diagnostic evidence record;
- **diagnosis:** typed CONFIRMED / REFUTED / INDETERMINATE;
- **repair:** existing canonical misconception repair, only after CONFIRMED;
- **recheck:** existing fresh verification path.

A wrong answer or bare misconception index can no longer become a confirmed misconception in the shared runtime.

## U07 result

**U07 COMPLETE and successor-safe evidenced.**

Parent denominator:
- **P = 7/10 = 70%**
- **E = 7/10 = 70%**

No claim is made that:
- the runtime semantically grades diagnostic free-form responses;
- evaluator basis is automatically correct;
- every authored diagnostic prompt is genuinely discriminating;
- a CONFIRMED record is permanent learner truth;
- broader product/browser suites are all green.

Next bounded unit:

**U08A — replay the recurring interaction proposals from #49–#56 and determine whether any subject-neutral capability passes the worth gate; return NO_CHANGE if recurrence + shared learner action are insufficient.**
