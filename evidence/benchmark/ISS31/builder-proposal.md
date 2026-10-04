# Issue 31 builder proposal checkpoint

**State: COMPLETE — actual rendered pages inspected. Recommendation: NO BUILDER CODE CHANGE.**

The exact governed learner artifacts are committed at `c3eef85875c7499466a3aeb3903167f60a86482f` and were produced by `render_core/2`. The strict quality gate reports `PASS` with zero findings, and the tablet browser audit reports no errors for either Core1A or Core2.

## Hardest-target inspection: Q5

Q5 is the benchmark's hardest learner-relative target: **MODEL · D2**, choosing the explanatory model that fits the requested output for NH3.

The actual pages express that target through existing governed components:

- Core2 is attempt-first and keeps the solution gated until an attempt.
- The pre-attempt representation exposes only the requested target.
- Authored support progressively reveals the VSEPR lens without exposing the final solution up front.
- Core1A uses a three-stage cumulative visual: requested output → VSEPR lens → orbital-overlap lens.
- The worked anchor requires a prediction before each revealed reasoning move and explicitly states both what VSEPR predicts and what it leaves unresolved.

This preserves the key invariant: VSEPR and orbital-overlap descriptions are not presented as competing truths; they answer different explanatory questions.

## Builder decision

The earlier academic sketch considered a bespoke “sort predictions into predicts / does not resolve” interaction. After inspecting the actual render, there is no demonstrated product defect that requires such a new module. The existing reusable `STAGED_VISUAL`, attempt control, predict/reveal worked example and gated ladder already create meaningful learner action around the model-scope decision, and they passed both the learner-quality and browser gates.

**Recommendation: no builder change for issue #31.** Do not add a topic-specific sorter merely to mirror the planning sketch. Revisit only if learner evidence later shows that the staged comparison fails to produce the intended model-selection decision.
