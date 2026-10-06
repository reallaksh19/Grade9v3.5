# ISS66 U07A — diagnostic evidence contract inspection

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U07A only — inspect current misconception hypothesis/probe/response/repair/recheck authority and replay whether a wrong answer can become a confirmed diagnosis without discriminating evidence  
**Basis head:** `cd42d371a96ef334c47cda9053b33a1f7c75a460`

## Existing authoring authority

Canonical microtopics already carry useful authored misconception hypotheses:

- `wrong_idea`
- `diagnostic_prompt`
- `repair`

This is correctly treated as authored curriculum content: a plausible wrong path, a probe intended to distinguish it, and a repair.

The authoring/readiness checks already reject incomplete misconception rows.

## Existing runtime caution that should be retained

`Shared/tools/feedback.py` is conservative in several important ways:

- an incorrect multi-capability answer does not automatically pick a failed capability;
- `UNDECIDABLE` routes to `DIAGNOSE`;
- transient worksheet questions do not receive invented hint ladders;
- diagnostic options expose canonical `wrong_idea` + `diagnostic_prompt`;
- repair is followed by a fresh verification candidate;
- observation drafts are explicit and are not silently persisted.

These are sound foundations.

## Concrete unsafe promotion path

The runtime currently accepts:

`evaluation.misconception_index`

as a bare integer.

`feedback.repair_for(...)` uses that integer directly to select a canonical misconception row and returns:

`kind = MISCONCEPTION_REPAIR`

with no machine requirement that the learner was actually asked the canonical diagnostic prompt or that a response to that probe was observed.

The thin session runner exposes the same path:

`study_session.attempt(..., misconception_index=0)`

and the CLI exposes:

`--misconception-index 0`

without any required probe-response evidence.

Existing tests explicitly demonstrate that a bare index is sufficient to route to misconception-specific repair.

## Documentation is stricter than executable behavior

The live pilot documentation already says:

> If the misconception is not yet confirmed, omit --misconception-index.

and:

> Only after the diagnostic prompt confirms a specific canonical misconception should the corresponding index be supplied for repair.

That is good human guidance, but it is not an executable contract.

A caller can currently supply:
- wrong answer;
- failed capability;
- `misconception_index=0`;

and receive a specific misconception repair even when no discriminating probe or learner response is recorded.

Therefore a wrong answer plus caller assertion can become operationally equivalent to a confirmed diagnosis.

## Recheck behavior

The runtime already has a useful post-repair boundary:

- after a misconception-specific repair, it selects a fresh canonical verification question or exit task;
- correct-with-help evidence remains weaker than independent verification.

This should be retained and bound explicitly to the diagnosis evidence rather than replaced.

## Root-cause classification

### REUSE EXISTING

Keep:
- canonical authored misconception hypothesis (`wrong_idea`);
- canonical discriminating prompt (`diagnostic_prompt`);
- canonical repair text;
- capability attribution safeguards;
- fresh verification after repair;
- observation drafts and non-silent persistence.

### TRUE CONTRACT GAP

The runtime lacks a typed distinction between:

- a **hypothesis** being considered;
- the **probe** actually presented;
- the **learner response** observed;
- an evaluator conclusion of `CONFIRMED`, `REFUTED`, or `INDETERMINATE`.

A bare misconception index currently collapses all four into one caller assertion.

## Minimum justified U07B contract

Add a small runtime diagnostic-evidence object tied to the existing canonical misconception row.

Minimum fields:

- `misconception_index`
- `probe` — must equal the canonical `diagnostic_prompt`
- `observed_response` — non-empty factual learner evidence
- `diagnosis` — one of `CONFIRMED`, `REFUTED`, `INDETERMINATE`
- `basis` — non-empty evaluator basis

Rules:

1. `misconception_index` alone never confirms a misconception.
2. `CONFIRMED` is allowed only with the exact canonical probe, observed response, and evaluator basis.
3. `INDETERMINATE` remains in `DIAGNOSE`; it does not select misconception-specific repair.
4. `REFUTED` does not select that misconception-specific repair.
5. Only `CONFIRMED` may route to the corresponding `MISCONCEPTION_REPAIR`.
6. Fresh verification after repair remains mandatory.
7. No automatic semantic grader is introduced; the evaluator supplies the diagnosis over recorded evidence.

## U07A result

**U07A COMPLETE. No production change.**

Parent U07 remains incomplete.

Parent denominator remains:
- **P = 6/10 = 60%**
- **E = 6/10 = 60%**

Next bounded task:

**U07B — implement the typed diagnostic evidence gate in feedback/study_session, preserve authored hypothesis + repair + fresh verification, add focused regressions proving bare wrong answer/index cannot become CONFIRMED, and close U07 only on green exact-head focused evidence.**
