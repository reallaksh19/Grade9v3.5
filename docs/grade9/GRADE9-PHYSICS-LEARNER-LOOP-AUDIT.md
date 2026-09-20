# Grade-9 Physics learner-loop architecture audit

> Roadmap: **RM-0007**
>
> Current foundation: **WP-TA-104 / canonical representations and staged visual help**
>
> Machine-readable companion: `docs/grade9/grade9-physics-learner-loop.json`

## Correction to the previous audit

Question inventory is **not** a Grade-9 completion denominator. The earlier 7-Core2A + 18-Core2B expansion converted a learner-loop architecture question into a coverage-count problem, so those EP-TA-006 additions are removed.

Three already-existing NLM questions are sufficient smoke fixtures for the visual-support contract:

- `Q-PHY-NLM-2A-COV-03` — FBD body ownership;
- `Q-PHY-NLM-2A-FRICTION-STATIC-09` — static-friction response;
- `Q-PHY-NLM-2B-FRICTION-STATE-01` — transfer/model choice under unknown contact state.

## Architecture now enforced

```text
RUNG / CAPABILITY
  |
  +--> CANONICAL REPRESENTATION
  |       academic visual meaning
  |       |
  |       +--> static rendering, when a renderer exists
  |       +--> ACTIVITY / interactive explorer
  |       +--> author-defined reveal stages
  |
  +--> QUESTION FAMILY -> QUESTION
          |
          +--> starting support (matrix support ladder; before attempt)
          +--> hints (ordered failure escalation; after difficulty)
          |       +--> optional representation + reveal-stage refs
          +--> practice / transfer demand
```

The webpage is not the representation. The question does not own the representation. A hint does not duplicate the representation; it only names which stage of canonical visual truth may be revealed.

## NLM pilot

Two canonical representations make previously implicit NLM visual truth explicit:

1. `REP-NLM-FBD-BODY-OWNERSHIP` — bound to R3 and the existing connected-blocks explorer.
2. `REP-NLM-FRICTION-THRESHOLD` — bound to R8 and the existing friction-threshold explorer.

Both use `FREE_BODY_DIAGRAM` but deliberately carry no `scene_instances`, because the Physics adapter still declares the static FREE_BODY_DIAGRAM renderer **PROPOSED**, not implemented.

Each representation owns its own reveal sequence. The schema does not impose a global V0–V4 template.

## Starting support is not hint depth

The NLM matrix already owns LOW, MEDIUM and HIGH starting support. The canonical representations map those pre-attempt levels to an initial visual stage.

The question's ordered hints remain post-failure escalation. The three smoke questions demonstrate that a hint can reference a later canonical stage without changing the matrix's starting-support policy.

## Remaining work

WP-TA-104 establishes the reusable visual foundation. It does not decide which support level a learner receives.

That belongs to **WP-TA-107**, which must derive a routing posture from current learner evidence, choose starting support/initial visual state, choose appropriate exercise demand, and retain the existing hint → repair → fresh verification → delayed-review loop.

The intended routing postures are derived decisions, not learner truth:

```text
independent DEMONSTRATED -> READY
UNCERTAIN / unobserved    -> REINFORCE
MISSING                   -> REBUILD
```

Error stage also matters: an execution or careless slip must not automatically trigger conceptual rebuilding.

## Preserved boundaries

- no mastery percentage or probabilistic learner model;
- no question-count completion proxy;
- no HTML/explorer as academic source of truth;
- no conflation of pre-attempt support with post-failure hints;
- no fake FREE_BODY_DIAGRAM renderer status;
- no Grade-10 transition until WP-TA-107 and the Grade-9 exit-readiness package are complete.
