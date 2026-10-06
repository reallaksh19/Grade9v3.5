# ISS69 PHASE-C — C02.5 diagnostic / solution boundary preservation

Material basis: Core2 runtime through `4277a9342887c115ff53fd415bdc9f7d89b94e05` and successor test commit `405d19fbec01ab6bd8f72dd2b0525241dd970e5f`.

## Diagnostic authority

Canonical diagnostic evidence remains owned by:

- `Shared/quality/diagnostic-evidence.schema.json`
- `Shared/tools/feedback.py`
- `Shared/tools/study_session.py`
- `tests/test_diagnostic_evidence_contract.py`

The contract requires a canonical misconception hypothesis/probe, observed response, diagnosis state and evaluator basis.

## Routing boundary retained

The focused contract proves:

- bare `misconception_index` -> `DIAGNOSE`, no repair;
- `INDETERMINATE` evidence -> `DIAGNOSE`, no misconception repair;
- `REFUTED` evidence -> `DIAGNOSE`, no misconception repair;
- mismatched/noncanonical probe -> rejected, no repair;
- only complete `CONFIRMED` evidence -> `REPAIR` with `MISCONCEPTION_REPAIR`;
- after repair -> fresh `VERIFY` using a different question.

## Assistance is not diagnosis

C02.4 adds browser interaction provenance only:

```text
assisted: boolean
assistance: [HINT_LADDER | WRONG_ROUTE | CONCEPT_NAV, ...]
```

These values are stored in the per-question browser state in `render_core.JS`.

They are **not** read by `feedback.py`, `study_session.py`, diagnostic schema validation, or misconception routing.

Therefore:

```text
help used / concept detour / wrong-route warning
    !=
diagnosis confirmed
```

The assisted flag affects independence provenance only. It cannot establish a misconception, choose a repair, or grade reasoning.

## Render boundary

`BP-CORE2-SOURCE-QUESTION@1.11.0` keeps:

- `DIAGNOSTIC_REPAIR` OPTIONAL under parent `SOLUTION`;
- `SOLUTION_STEPS`, `ANSWER`, and `CHECK` under the solution payload;
- TRAP/HINT/CONCEPT_NAV in support.

Thus diagnosis/repair and full solution remain distinct from pre-attempt support.

## Evidence

On the C02.4 production runtime head, the standard code-test workflow reports:

- diagnostic evidence contract: PASS;
- U09 migrated callers: PASS;
- representation binding: PASS;
- Issue69 recovery contract: PASS;
- staged-support: PASS;
- informational platform tests: PASS;
- blueprint-layout regressions: PASS.

No diagnostic production file is changed by C02.2–C02.4.

## Decision

C02.5 requires **NO production change**.

Adding assistance provenance must not be coupled into diagnostic classification. If a future learner-evidence layer consumes the assisted flag, its only valid use here is to distinguish supported vs independent evidence, not to infer a misconception.
