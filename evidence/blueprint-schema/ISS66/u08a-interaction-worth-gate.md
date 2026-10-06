# ISS66 U08A — interaction proposal replay and worth gate

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U08A only — replay #49–#56 builder proposals and decide whether any interaction class earns shared-contract status

## Worth gate

A permanent shared interaction primitive is justified only when all of these are evidenced:

1. **Independent recurrence** — the same learner-owned action recurs in at least two independently executed frozen runs.
2. **Semantic convergence** — runs agree on what learner state/action the primitive means, not merely on a widget gesture such as “slider”.
3. **Subject neutrality** — the authored contract can be named and parameterised without polynomial/domain/topic semantics.
4. **Learner ownership** — it captures or exposes learner action/observation, not only authored animation.
5. **Existing-composition gap** — current staged visuals, attempt controls, prediction/compare repair, representation binding and `grade9v3:interactive_idea` cannot already express the need honestly.
6. **Protection/fallback viability** — the same contract can support protected state, keyboard/touch access, static/print fallback and restoration.
7. **Evidence breadth** — recurrence only inside one benchmark/topic family is not enough for permanent shared runtime/schema cost unless the semantic contract is independently demonstrated across distinct task families.

## Proposal replay

| Issue | Builder proposal | Learner action | U08 classification |
| --- | --- | --- | --- |
| #49 | record-configured bounded-parameter probe | vary parameter; predict/reason; inspect derived readouts | candidate numeric-probe signal |
| #50 | `COORDINATE_PLOT_RESPONSE` | author learner-owned table/points | distinct structured-response action |
| #51 | `BLUEPRINT_DRIVEN_LAYOUT_CONSISTENCY` | none | platform/layout, not interaction |
| #52 | no symmetric frozen builder evidence available to this parent replay | — | asymmetric evidence |
| #53 | `POLYNOMIAL_COEFFICIENT_GRID_INTERACTOR` | fill coefficient/power slots | topic-specific structured response |
| #54 | `rational-domain-inspector` | move x-probe; compare evaluations at exclusion | related numeric-probe gesture, topic-specific semantics |
| #55 | layout reconciliation + PAGES asset packaging | none | platform/packaging, not interaction |
| #56 | `CONTINUOUS_PARAMETER_SCRUBBER` | vary model parameter; observe state/critical ticks | candidate numeric-probe signal |

## Recurring cluster — numeric probe / range control

The only plausible recurrence is #49 + #54 + #56.

### What actually converges

All three want:
- one numeric control over a bounded/continuous domain;
- accessible range input or equivalent;
- live authored readout/representation change;
- a static or staged fallback.

That is a recurring **UI gesture**.

### What does not converge

The semantic state differs:

- **#49:** parameter change is paired with learner prediction/reason and derived readouts; the frozen product already reports generic typed prediction/compare as sufficient.
- **#54:** the control probes an **independent variable**, compares original vs simplified function evaluation, and detects an excluded-domain singularity. The proposed component embeds rational-function/domain semantics.
- **#56:** the control varies a **model parameter** and animates representation trajectories / critical bifurcation ticks.

These are not yet the same learner-response contract.

A generic field such as “slider min/max/step” would standardise presentation mechanics while leaving the academically meaningful state unspecified. That would be a UI toolkit feature masquerading as a semantic blueprint contract.

## Existing authority that already captures design intent

The research/authoring workflow already has:

`microtopic.extensions["grade9v3:interactive_idea"]`

with:
- `learner_manipulates`
- `becomes_visible`
- `misconception_targeted`
- `representation_ref`

and the same required fields are used by Mathematics, Physics and Chemistry work rules.

That object is intentionally a **design idea, not runtime code**. It is sufficient to preserve cross-subject interaction intent while the executable primitive remains unproven.

The current renderer also already provides:
- staged visuals;
- learner attempt/commit controls;
- typed prediction/compare patterns;
- representation binding;
- paper/static fallbacks.

## Worth-gate result

For the recurring numeric-probe cluster:

| Gate | Result |
| --- | --- |
| Independent recurrence | PASS |
| Semantic convergence | **FAIL** |
| Subject neutrality | **FAIL** at executable-contract level |
| Learner ownership | PASS |
| Existing-composition gap | **FAIL / not demonstrated** |
| Protection/fallback viability | PASS in proposals |
| Evidence breadth | **FAIL** — same polynomial benchmark family |

Therefore no proposal currently clears the full worth gate.

## U08A result

**U08A COMPLETE.**

Decision at this checkpoint:

`NO_SHARED_INTERACTION_PRIMITIVE_YET`

This is not a claim that numeric probes are unhelpful. It means current evidence does not justify permanent shared blueprint/schema/runtime authority.

Parent U08 remains incomplete until U08B freezes the NO_CHANGE disposition and negative knowledge.

Parent denominator remains:
- **P = 7/10 = 70%**
- **E = 7/10 = 70%**

Next bounded task: **U08B — formalise the NO_CHANGE disposition, define the evidence threshold for reopening a generic numeric-probe primitive, and close U08 without production schema/runtime changes.**
