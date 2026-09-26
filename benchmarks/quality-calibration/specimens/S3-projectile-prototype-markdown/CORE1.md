# Core1 — Projectile Motion / Motion in 2D

**Role:** compact semantic orientation  
**Academic authority:** `Physics/library/phy-kin-2d-motion.v1.json`  
**Bucket:** `BUCKET-PHY-KIN-2D-MOTION`  
**Canonical status:** CANDIDATE  
**Provenance:** CANONICAL_DERIVED  
**Learner estimate:** not used to change this product.

## Scope

This bucket covers one object moving in a plane, described in one declared Cartesian frame by signed x- and y-components that share one elapsed time. It then carries the familiar one-dimensional constant-acceleration relations onto each component where that component acceleration is constant. Ideal near-Earth projectile motion is the gravity-only specialization of that model.

The canonical conceptual units are exactly:

- `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS`
- `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION`
- `MIC-PHY-KIN-PROJECTILE-MODEL`

## Objects and conventions

Use one fixed, non-rotating x-y frame, one origin and one time origin for the event. Position/displacement, velocity and acceleration are read as signed component pairs. “Independent components” means the x equation contains x quantities and the y equation contains y quantities; it does **not** give the object two clocks.

For the displayed projectile specialization, choose +y upward. During ideal near-Earth free flight with air resistance neglected, `a_x=0` and `a_y=-g`.

## Canonical representation

**`REP-KIN-2D-SHARED-CLOCK`** is the primary representation. Read it as one physical object → one declared frame → one shared time marker → separate x/y histories → one simultaneous ordered-pair state. A pair such as x(t₁), y(t₂) with t₁≠t₂ may contain two individually meaningful measurements, but it is not one simultaneous state.

**Visual status:** `VISUAL_HOLD`. The representation record is CANDIDATE; a semantic review rendering appears in `preview.html`, but that rendering is not claimed academically reviewed.

## Governing relations

### Component velocity — `REL-KIN-2D-VELOCITY`

[
v_x=u_x+a_x t,qquad v_y=u_y+a_y t
]

Meaning: each velocity component follows the one-dimensional constant-acceleration relation over the **same** interval.

Conditions: the relevant acceleration component is constant over the interval; both component equations use the same frame and elapsed time.

### Component displacement — `REL-KIN-2D-DISPLACEMENT`

[
Delta x=u_x t+	frac12 a_x t^2,qquad
Delta y=u_y t+	frac12 a_y t^2
]

Meaning: each displacement component follows the one-dimensional constant-acceleration relation, then the simultaneous components reconstruct the plane displacement.

Conditions: the relevant acceleration component is constant; one frame; one common t.

### Ideal projectile specialization — `REL-PROJECTILE-COMPONENT-MODEL`

[
a_x=0,quad a_y=-g,quad
v_x=u_x,quad v_y=u_y-gt,
]
[
Delta x=u_x t,quad
Delta y=u_y t-	frac12gt^2.
]

Conditions: near-Earth approximately constant g, air resistance neglected, free flight after release, +y upward for the displayed signs.

## Three hard transitions

**R1 — separate equations, shared event.** Solve x and y independently, but combine only values belonging to the same frame and instant. Deeper construction: Core1A/Core1B → `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS`.

**R2 — validate per axis before formula use.** A constant `a_x` does not prove `a_y` is constant. If an event time is found on one axis, that same event time is reused on the other. Deeper construction: Core1A/Core1B → `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION`.

**R3 — choose the projectile model, then choose the event.** First establish gravity-only free flight. Then translate “apex”, “same-height return”, or “unequal-height impact” into its component condition. At an apex only `v_y=0`; `v_x` may remain nonzero and `a_y=-g`. Deeper construction: Core1A/Core1B → `MIC-PHY-KIN-PROJECTILE-MODEL`.

## Compact canonical anchors

- Same event: if a state is requested at `t=2 s`, evaluate both x(t) and y(t) at 2 s before pairing them.
- Constant acceleration: for `u=(0,5)` m/s and `a=(10,4)` m/s², the setup is `Delta x=0t+	frac12(10)t²`, `Delta y=5t+	frac12(4)t²`, using one t.
- Horizontal ideal launch: after release, `a_x=0`, `a_y=-g`; `v_x=u`, `v_y=-gt`; `Delta x=ut`, `Delta y=-	frac12gt²`.

These are canonical-derived orientation anchors, not source-exam questions.

## Explicit exclusions and demand boundaries

The fixed five-question corpus does **not** add curriculum. Its advanced demands stay outside Core1:

- Q28: differentiating x(t), y(t) to obtain velocity — `UNTaught_CAPABILITY_GAP`.
- Q15: energy-loss/restitution at a bounce — `IDENTITY_HOLD` plus extension demand.
- Q21: changed gravity after the apex — `EXTENSION`.
- Q26: trajectory-equation/specified-point geometry — `EXTENSION`.
- Q23: linear drag and differential-equation/integration treatment — `UNTaught_CAPABILITY_GAP`.

## Orientation closure

Before solving a Motion-in-2D problem, you should be able to answer four questions:

1. What frame/sign convention is being used?
2. Which quantities belong to x and which belong to y?
3. Are the needed acceleration components constant on the interval?
4. What physical condition identifies the requested event, and what one time belongs to both axes?

If any of those decisions is uncertain, use Core1A for the completed construction or Core1B to reconstruct it yourself.
