# Grade-9 Physics learner-loop audit

> Status: **derived evidence audit — academic inventory gap found**
>
> Roadmap basis: **RM-0006 / WP-TA-104 / EP-TA-005**
>
> Material basis: `ab6c3443b531bd92b22bfd1c91d93dd38fb4f05f`
>
> Machine-readable companion: `docs/grade9/grade9-physics-learner-loop.json`

## Result

Across the **30 required/prerequisite Grade-9 learner actions** in the six ordinary core matrices:

- **30/30** have canonical teaching paths;
- **30/30** have misconception diagnosis/repair;
- **30/30** have independent exit tasks;
- **23/30** have a direct Core2A primary practice question;
- **5/30** currently have a direct Core2B primary transfer question.

The Shared learner-loop machinery is not the missing layer. Current runtime contracts already preserve evidence precedence, downgrade helped success, refuse ambiguous failure attribution, route narrow repair, request fresh verification, and schedule later review.

## Bounded academic question backlog

The remaining learner-facing inventory is **25 questions**, bounded entirely by existing Grade-9 scope and matrix transfer specifications:

1. **7 direct Core2A practice items** for required actions that already have teaching/repair/exit evidence but no primary practice question.
2. **18 learner-executable Core2B items** for already-authored **core** matrix transfer rows in matrices that currently have no canonical Core2B inventory.

Gravitation's retained orbital R4/R5 transfer rows are excluded because those rungs are declared extensions, not ordinary Grade-9 core.

### Missing direct Core2A practice

| Matrix | Rung | Capability |
| --- | --- | --- |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R2` | `CAP-PHY-GRAV-INVERSE-SQUARE` |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R3` | `CAP-PHY-GRAV-FREE-FALL-G` |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R3W` | `CAP-PHY-GRAV-MASS-WEIGHT` |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R4` | `CAP-WEP-MECH-ENERGY-CONDITION` |
| `MATRIX-PHY-SOUND` | `R5` | `CAP-SOUND-REFLECTION` |
| `MATRIX-PHY-SIMPLE-MACHINES` | `R1` | `CAP-MACHINE-TRADEOFF` |
| `MATRIX-PHY-SIMPLE-MACHINES` | `R3` | `CAP-MACHINE-COMPARE` |

### Core transfer specifications that still need executable Core2B questions

| Matrix | Repair rung | Capability | Dimension | Changed demand |
| --- | --- | --- | --- | --- |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R2` | `CAP-PHY-GRAV-INVERSE-SQUARE` | model_choice | A spherical source is shown with the receiver outside it, but the problem labels altitude above the surface instead of centre distance. |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R1` | `CAP-PHY-GRAV-R1` | representation_translation | A projectile is moving upward near the same source: determine the gravitational-force direction without using its velocity direction. |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R3` | `CAP-PHY-GRAV-FREE-FALL-G` | model_choice | Two different test masses are placed at the same point; compare local g and gravitational force before either is released. |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | `R3W` | `CAP-PHY-GRAV-MASS-WEIGHT` | reasoning_steps | The same object has half the weight at a second location; infer the local-g ratio without changing the object's mass. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R4` | `CAP-WEP-MECH-ENERGY-CONDITION` | model_choice | A rough track replaces a frictionless one and the learner must decide whether simple mechanical-energy conservation still applies. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R1` | `CAP-WEP-WORK-DIRECTION` | representation_translation | A force-and-path diagram must be translated into signed work contributions before an energy balance can be written. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R4` | `CAP-WEP-MECH-ENERGY-CONDITION` | reasoning_steps | A moving support does work through its contact force, so the learner must include that external transfer before solving for the final kinetic energy. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R5` | `CAP-WEP-POWER-RATES` | novelty | Two machines perform the same task with different time profiles and the learner must separate total work from average and instantaneous power. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R6` | `CAP-WEP-GRADE9-QUANT` | model_choice | A numerical energy problem includes friction and the learner must decide whether to use mechanical-energy conservation alone or include an explicit transfer term. |
| `MATRIX-PHY-WORK-ENERGY-POWER` | `R5D` | `CAP-WEP-ENERGY-DERIVATIONS` | reasoning_steps | Instead of being given K = 0.5 m v^2 or Delta U_g = m g h, the learner must reconstruct each expression from previously authored work, force and motion relations. |
| `MATRIX-PHY-SOUND` | `R2` | `CAP-SOUND-LONGITUDINAL` | representation_translation | A compression/rarefaction description must be translated into local particle motion and propagation direction without drawing particles travelling with the wave. |
| `MATRIX-PHY-SOUND` | `R4` | `CAP-SOUND-PERCEPTION` | model_choice | Frequency, amplitude and wavelength are all changed in a comparison, requiring separate pitch, loudness and speed reasoning rather than one 'bigger wave' judgment. |
| `MATRIX-PHY-SOUND` | `R5` | `CAP-SOUND-REFLECTION` | novelty | A cave-mapping or animal echolocation problem must be recognized as an ordinary reflected-sound round-trip timing problem. |
| `MATRIX-PHY-SOUND` | `R3` | `CAP-SOUND-WAVE-QUANTITIES` | representation_translation | A sampled sound graph must be identified as spatial or temporal before the learner can decide whether horizontal repeat spacing means wavelength or period. |
| `MATRIX-PHY-SOUND` | `R4` | `CAP-SOUND-PERCEPTION` | model_choice | A frequency just outside the approximate human audible band must be classified using the Grade 9 hearing-range model without treating 20 Hz and 20,000 Hz as exact personal hearing thresholds. |
| `MATRIX-PHY-SIMPLE-MACHINES` | `R1` | `CAP-MACHINE-TRADEOFF` | novelty | An unfamiliar workshop tool must be analysed as a generic effort/load machine without being named as a lever, pulley or incline. |
| `MATRIX-PHY-SIMPLE-MACHINES` | `R3` | `CAP-MACHINE-COMPARE` | model_choice | A fixed pulley changes force direction but not magnitude, requiring the learner to reject the assumption that all useful machines have MA > 1. |
| `MATRIX-PHY-SIMPLE-MACHINES` | `R1` | `CAP-MACHINE-TRADEOFF` | reasoning_steps | A force advantage is given and the learner must infer the compensating distance tradeoff before calculating or claiming an energy gain. |

## Matrix status

| Matrix | Required actions | Direct Core2A | Core transfer specs | Canonical Core2B | Status |
| --- | ---: | ---: | ---: | ---: | --- |
| `MATRIX-PHY-KIN-1D-MOTION` | 5 | 5/5 | 5 | 5 | EXECUTABLE_BASELINE |
| `MATRIX-PHY-NLM-FIRST-LAW` | 6 | 6/6 | 3 | 16 | EXECUTABLE_BASELINE |
| `MATRIX-PHY-GRAV-UNIVERSAL-LAW` | 4 | 1/4 | 4 | 0 | ACADEMIC_INVENTORY_GAP |
| `MATRIX-PHY-WORK-ENERGY-POWER` | 7 | 6/7 | 6 | 0 | ACADEMIC_INVENTORY_GAP |
| `MATRIX-PHY-SOUND` | 5 | 4/5 | 5 | 0 | ACADEMIC_INVENTORY_GAP |
| `MATRIX-PHY-SIMPLE-MACHINES` | 3 | 1/3 | 3 | 0 | ACADEMIC_INVENTORY_GAP |

## Evidence semantics already satisfied

- Partial/unknown evidence stays distinct from rough owner/profile estimates.
- Help-dependent success cannot become independent demonstration.
- Ambiguous multi-capability failure is not guessed.
- Repair routes to the narrowest canonical teaching/misconception surface.
- Repair is followed by a fresh same-capability question or canonical exit-task fallback.
- Delayed review preserves distinct incorrect, helped-correct, independent-correct and transfer-independent outcomes.
- Core2A same-family practice and Core2B changed-demand transfer remain semantically distinct.

## Why EP-TA-005 stops before the fix

EP-TA-005 explicitly prohibits canonical Physics academic edits. Its falsifier shows the remaining blockers are canonical question inventory, not Shared runtime behavior. The correct next step is therefore a separately bounded academic authoring package inside WP-TA-104, not an orchestration rewrite.

That academic package should author only the seven missing direct-practice items and the eighteen existing core transfer specifications listed above, with truthful local `AUTHORED` provenance where no external question is copied, then rerun this learner-loop proof.

## Anti-drift

- no new mastery score or learner-state schema;
- no runtime generation of plausible questions;
- no Core2B label for number/story-only variants;
- no orbital/other extension transfer pulled into ordinary Grade 9;
- no question-demand/deferred matrix promoted into the ordinary completion boundary;
- no Grade-10 authoring until WP-TA-104 and the exit-readiness package are complete.

