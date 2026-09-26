# Core1B — Self-tutor reconstruction: Motion in 2D

**Role:** open-ended conceptual reconstruction  
**Academic authority:** `Physics/library/phy-kin-2d-motion.v1.json`  
**Coverage:** identical to Core1A: exactly three canonical microtopics  
**Reveal rule:** PREDICT and ATTEMPT precede reconstruction/answer material. The interactive enforcement is implemented in `preview.html`.  
**Provenance:** CANONICAL_DERIVED.

Do not read a reconstruction until you have made the requested attempt.

---

## Cycle 1 — Independent components, one shared clock

**Canonical crux:** `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS.inferential_jump`  
**Representation:** `REP-KIN-2D-SHARED-CLOCK` — `VISUAL_HOLD`.

### PREDICT

If x and y components are independent, does the object have two different clocks? Commit to **yes or no** and give one sentence of reasoning.

### ATTEMPT

Produce a two-column x/y setup for one moving particle. Your setup must show:

- a declared frame;
- one x history and one y history;
- the time symbol(s) you intend to use;
- a rule for which component values may be paired into one state.

**Self-check rubric before reveal:** a defensible attempt makes a meaningful choice about what is separate and what is shared. It is not enough to write two formulas with no event/time statement.

### RECONSTRUCT — reveal after your attempt

1. Ask: **what must be declared before any component can have a sign?**  
   Recover one common frame, origin and time origin.
2. Ask: **what separates between axes, and what remains common because both descriptions belong to one event?**  
   x quantities stay with x; y quantities stay with y; the physical elapsed time stays common.
3. Ask: **which x and y values may be recombined?**  
   Only same-frame, same-instant values.

**Model response:** The component equations are independent, but they describe one object in one frame at one physical time. A valid state uses x(t) and y(t) at the same t.

**Accepted representative response:** “Separate x/y equations; same frame and same t for both.”

**Rejected representative response:** “Use any convenient t on each axis and pair the answers.”

### DIAGNOSE

**Wrong idea:** independent x and y motions may use different elapsed times.

**Diagnostic prompt:** At one instant 2 s after launch, may x use `t=2 s` while y uses `t=3 s`?

If you answered yes, you separated the clock instead of only the equations.

### REPAIR

Attach a timestamp explicitly to every component value. Refuse to form an ordered pair until the timestamps and frame match. Repeat with x(2), y(2) versus x(2), y(3).

### BOUNDARY TEST

If `a_x=0` but `a_y
eq0`, may `v_x` remain constant while `v_y` changes?

**Answer:** yes. That is exactly what independent component evolution permits.

**Criterion:** you can distinguish “different component evolution” from “different physical event”.

---

## Cycle 2 — Constant acceleration component by component

**Canonical crux:** `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION.inferential_jump`  
**Representations:** `REP-KIN-2D-SHARED-CLOCK`, `REP-KIN-2D-EVENT-CLOCK` — `VISUAL_HOLD`.

### PREDICT

If `a_x
eq0` and `a_y=0`, which velocity component changes with time? State your answer before writing any formula.

### ATTEMPT

Write two velocity equations and two displacement equations for a particle whose `a_x` and `a_y` are constant. Then write one sentence stating the model-validity condition and one sentence stating the time rule.

**Self-check rubric before reveal:**

- each axis contains only its own signed values;
- the relevant acceleration component is constant;
- both equations share one t.

**Accepted representative response:** `v_x=u_x+a_xt`, `v_y=u_y+a_yt` with one common t and a per-axis constancy check.

**Rejected representative response:** insert `|a|` into both equations, or use unrelated times.

### RECONSTRUCT — reveal after your attempt

1. **Before a constant-acceleration formula, what must be true about that axis?**  
   Its acceleration component must be constant over the interval.
2. **What does the 1D relation become on x? On y?**  
   Apply the same one-dimensional relation separately with signed component values.
3. **If one component finds the event time, what time must the other use?**  
   The same event time.

**Model response:**

[
v_x=u_x+a_xt,quad v_y=u_y+a_yt,
]
[
Delta x=u_xt+	frac12a_xt^2,quad
Delta y=u_yt+	frac12a_yt^2.
]

These are exact only on axes whose acceleration component is constant over the interval; one physical event supplies one shared t.

### DIAGNOSE

Test these three wrong ideas:

- “Use the acceleration magnitude on both axes.”
- “If x has constant acceleration, y may automatically use constant-a equations.”
- “If x gives t=3 s, y may use a different convenient t.”

A correct diagnosis rejects all three.

### REPAIR

Make a validity table before calculation:

| Axis | acceleration history | constant on interval? | constant-a relation licensed? |
|---|---|---|---|
| x | `a_x(t)` | yes/no | yes/no |
| y | `a_y(t)` | yes/no | yes/no |

Then write the **same event time** beside both rows before recombining.

### BOUNDARY TEST

If `a_y` changes with time while `a_x` stays constant, may the constant-acceleration equations remain exact on both axes?

**Answer:** no. They may remain exact on x but not on y over that interval.

**Criterion:** model validity is checked component by component, not granted globally.

---

## Cycle 3 — Select the projectile model, then the event

**Canonical crux:** `MIC-PHY-KIN-PROJECTILE-MODEL.inferential_jump`  
**Representations:** `REP-KIN-2D-PROJECTILE-MODEL`, `REP-KIN-2D-EVENT-CLOCK` — `VISUAL_HOLD`.

### PREDICT

Immediately after a horizontal launch in the ideal model, which acceleration component is zero? What is the other component if +y is upward?

### ATTEMPT

For a launched object, produce this decision sequence without looking ahead:

1. list the post-release interactions;
2. decide whether the ideal projectile specialization is valid;
3. if valid, write `a_x` and `a_y`;
4. name a component condition for one event: apex, same-height return, or lower-ground impact;
5. state how you will reuse the resulting event time.

**Self-check rubric before reveal:** you must make the model decision **before** using projectile equations and the event decision **before** solving a named projectile quantity.

**Accepted representative response:** establish gravity-only free flight, set `a_x=0`, `a_y=-g`, choose the event condition, then solve/recombine with one t.

**Rejected representative response:** start from a memorized range/height formula without checking the post-release model or landing/event condition.

### RECONSTRUCT — reveal after your attempt

1. **What interactions remain after release?**  
   Gravity only in the idealized model.
2. **What component equations follow from that interaction state?**  
   `a_x=0`, `a_y=-g`; therefore `v_x=u_x`, `v_y=u_y-gt`, `Delta x=u_xt`, `Delta y=u_yt-	frac12gt^2`.
3. **What exact condition identifies the requested event?**  
   Apex: `v_y=0`. Same-height return: later root of `Delta y=0`. Unequal-height impact: actual signed `Delta y=y_f-y_i`.
4. **At the apex, what becomes zero and what does not?**  
   Only `v_y`; horizontal motion can continue and acceleration remains downward.
5. **Does launch height equal landing height?**  
   If not, a same-height shortcut is invalid.

### DIAGNOSE

Use the canonical misconception checks:

- If `a_x=0`, can `v_x
eq0`? **Yes.**
- One second after a horizontal launch, is `v_y=0`? **No.**
- At an apex, are the full velocity and acceleration both zero? **No.**
- From a roof to lower ground, may a same-height flight shortcut be used without checking `Delta y`? **No.**
- At equal height on ascent/descent, are velocity vectors identical? **No: `v_y` changes sign.**
- Does horizontal speed determine ideal fall time from a fixed height? **No.**

### REPAIR

Return to the sequence **model → event → shared time → simultaneous state**. Do not repair a failed projectile problem by adding another memorized shortcut.

### BOUNDARY TEST

A launched object continues under significant horizontal thrust after release. May the standard `a_x=0`, `a_y=-g` projectile specialization be used?

**Answer:** no. Gravity-only free flight is false; use a more general valid model if one is already established.

**Criterion:** a curved path or “launched object” label never overrides model conditions.

---

## Coverage and extension check

Core1B has the same three concepts as Core1A and no others. The five fixed assessment demands are not extra reconstruction chapters:

- Q28 differentiation — upstream capability gap.
- Q15 bounce/energy demand — `IDENTITY_HOLD` plus extension.
- Q21 altered gravity — extension.
- Q26 trajectory equation/specified-point geometry — extension.
- Q23 linear drag — upstream capability gap.

The interactive preview enforces attempt-before-reveal for these cycles; hidden reconstruction text is inserted only after learner commitment.
