# Core2B — Changed-demand transfer candidates

**Role:** changed-demand transfer  
**Practice provenance:** `AUTHORED_PRACTICE` from the canonical Motion-in-2D package  
**Assessment-surface claim:** none; Core2 source custody is HOLD  
**Learner status:** **HOLD** — canonical parent lineage exists, but actual prior exposure and scoped learner capability evidence are not established for this learner.

The five candidates below stay inside already-taught canonical Motion-in-2D truth. None introduces drag, altered gravity, bounce/restitution, trajectory-equation derivation, or calculus. Each changed demand contains a `DECIDE` move named by `question.transfer.protected_move_ref`.

In `preview.html`, the protected move and answer are not inserted into the rendered task until the learner commits an attempt.

---

## 2B-1 — Representation translation

**Item:** `Q-PHY-KIN-2D-2B-REPRESENTATION-01`  
**Prior-exposure lineage:** `Q-PHY-KIN-2D-2A-SHARED-CLOCK-01`  
**Required canonical capability:** `CAP-KIN-2D-INDEPENDENT-COMPONENTS`  
**Transfer dimension:** `representation_translation`  
**Changed demand:** convert a verbal direction description into signed x/y state without being handed the component representation.  
**Protected move:** `R-KIN-2D-BREP-FRAME`  
**Repair:** `K2D1-2`

### Before attempt — safe support

**Stem:** At t=0 a particle at the origin moves east at 6 m/s and north at 2 m/s; its acceleration is 3 m/s² south and zero east-west. Choose a coordinate convention and write the signed component state for later calculation.

**Authored pre-attempt scaffold:** list the raw direction words and magnitudes **without** plus/minus signs.

This scaffold supports `R-KIN-2D-BREP-FACTS`; it does not tell the learner which positive axes to choose.

### Learner commitment

Write a frame choice and signed `u_x,u_y,a_x,a_y` before opening post-attempt support.

### After attempt

**Protected decision:** choose and declare one perpendicular positive-axis convention before assigning component signs.

**Reasoning route:**  
`R-KIN-2D-BREP-FACTS` REPRESENT raw directional facts →  
`R-KIN-2D-BREP-FRAME` **DECIDE** the frame →  
`R-KIN-2D-BREP-TRANSLATE` translate signs →  
`R-KIN-2D-BREP-CHECK` reverse an axis mentally and verify consistent sign reversal.

**Model response:** one valid convention is +x east, +y north, giving `u_x=+6`, `u_y=+2`, `a_x=0`, `a_y=-3` in SI units, with one shared t.

**Justification rubric:** declare the frame before signs; translate directions consistently; preserve one common time.

**Independent check:** another perpendicular axis convention is valid if all affected signs transform consistently.

---

## 2B-2 — Per-axis model validity

**Item:** `Q-PHY-KIN-2D-2B-MODEL-VALIDITY-02`  
**Prior-exposure lineage:** `Q-PHY-KIN-2D-2A-CONSTANT-ACCEL-02`  
**Required capability:** `CAP-KIN-2D-CONSTANT-ACCELERATION` plus independent components  
**Transfer dimension:** `model_choice`  
**Changed demand:** decide component-by-component whether constant-acceleration equations are exact instead of being told that they apply.  
**Protected move:** `R-KIN-2D-BMODEL-DECIDE`  
**Repair:** `K2D2-1`

### Before attempt — safe support

**Stem:** over `0≤t≤4 s`, `a_x=2 m/s²` and `a_y=3t m/s²`. Decide whether ordinary constant-acceleration equations may be used exactly on x, y, both or neither.

**Authored pre-attempt scaffold:** make one row for `a_x(t)` and one for `a_y(t)`; write the validity condition each row must satisfy.

### Learner commitment

Commit to x only / y only / both / neither, with one sentence of justification.

### After attempt

**Protected decision:** check constancy separately; x satisfies the condition, y does not.

**Reasoning route:** REPRESENT the two histories → **DECIDE** validity per axis → CONNECT the decision to which equations may be used → VERIFY by comparing endpoint accelerations.

**Model response:** constant-a equations are exact on x because `a_x=2` is constant; they are not exact on y because `a_y=3t` changes from 0 to 12 m/s².

**Rubric:** checks axes separately; licenses the model only where its condition holds.

**Independent check:** a constant x acceleration does not make y acceleration constant.

**Capability boundary:** no integration is taught or required. The task asks only for the already-taught model-validity decision.

---

## 2B-3 — Changed landing geometry

**Item:** `Q-PHY-KIN-2D-2B-UNEQUAL-HEIGHT-03`  
**Prior-exposure lineage:** `Q-PHY-KIN-2D-2A-SAME-HEIGHT-05`  
**Required capability:** `CAP-KIN-PROJECTILE-MODEL` plus constant acceleration  
**Transfer dimension:** `reasoning_steps`  
**Changed demand:** replace the familiar same-height condition with an unequal-height event condition and carry the resulting time across axes.  
**Protected move:** `R-KIN-2D-BHEIGHT-EVENT`  
**Repair:** `K2D3-6`

### Before attempt — safe support

**Stem:** an ideal projectile starts 15 m above ground with `u_x=10 m/s`, `u_y=10 m/s`, `g=10 m/s²`, +y upward. Find ground-impact time and horizontal range. Do not assume equal launch/landing height.

**Authored pre-attempt scaffold:** sketch only the launch level and ground relative to one vertical origin.

### Learner commitment

Write the vertical displacement condition that defines ground impact before solving.

### After attempt

**Protected decision:** use `Delta y=-15 m`, not the familiar `Delta y=0`.

**Reasoning route:** REPRESENT ground below launch → **DECIDE** `Delta y=-15` → solve `-15=10t-5t²` → select `t=3 s` → reuse in x to obtain 30 m → VERIFY by substitution.

**Full answer:** ground-impact time 3 s; horizontal range 30 m.

**Rubric:** actual vertical geometry sets the event condition; the same impact time is reused on x.

**Independent check:** `t=3 s` gives `Delta y=-15 m`; the familiar 2 s same-height time would give the wrong event.

---

## 2B-4 — Reject an invalid projectile specialization

**Item:** `Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04`  
**Prior-exposure lineage:** `Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04`  
**Required capabilities:** `CAP-KIN-PROJECTILE-MODEL`, `CAP-KIN-2D-CONSTANT-ACCELERATION`  
**Transfer dimension:** `model_choice`  
**Changed demand:** retained horizontal propulsion breaks the familiar gravity-only specialization; choose the valid parent model.  
**Protected move:** `R-KIN-TRANSFER-MODEL`  
**Repair:** `K2D3-1`

### Before attempt — safe support

**Stem:** after launch, a rocket motor remains active and gives `a_x=2 m/s²`, while gravity gives `a_y=-g`. Decide whether the standard `a_x=0,a_y=-g` projectile specialization is valid and state the correct bounded model.

**Authored pre-attempt scaffold:** list the post-release interactions and the acceleration components they imply before naming a motion model.

### Learner commitment

State **valid / invalid** for the standard projectile specialization and name the model you would use, without calculating a trajectory.

### After attempt

**Protected decision:** reject the standard projectile specialization because its defining `a_x=0` condition is violated.

**Reasoning route:** REPRESENT interactions → **DECIDE** specialization validity → CONNECT to the parent 2D constant-acceleration model with `a_x=2,a_y=-g` while those components remain constant → VERIFY by imagining the motor switched off.

**Model response:** standard gravity-only projectile motion is invalid during powered flight; use the more general component constant-acceleration model for the stated interval.

**Rubric:** checks the model condition; falls back to the smallest already-taught parent model rather than inventing new physics.

**Independent check:** when the motor is off and drag remains negligible, the standard projectile specialization becomes valid from that later instant.

---

## 2B-5 — Compare equal-height states without solving times

**Item:** `Q-PHY-KIN-2D-2B-SAME-HEIGHT-VELOCITY-05`  
**Prior-exposure lineage:** `Q-PHY-KIN-2D-2A-PROJECTILE-APEX-03`  
**Required capability:** `CAP-KIN-PROJECTILE-MODEL` plus independent components  
**Transfer dimension:** `reasoning_steps`  
**Changed demand:** compare two equal-height states by component invariants rather than carrying out the familiar event-time calculation.  
**Protected move:** `R-KIN-2D-BSTATE-DECIDE`  
**Repair:** `K2D3-7`

### Before attempt — safe support

**Stem:** an ideal projectile passes the same height once upward and once downward. Without calculating the times, compare `v_x`, `v_y`, speed and acceleration.

**Authored pre-attempt scaffold:** make a table with rows `v_x,v_y,speed,a`; enter only “same height”, “upward” and “downward” before choosing a method.

### Learner commitment

Fill the comparison table and state whether the two velocity vectors are identical.

### After attempt

**Protected decision:** use equal-height component invariants directly rather than solving for the two times.

**Reasoning route:** REPRESENT the two events → **DECIDE** direct invariant comparison → CONNECT component relations to speed → keep acceleration `(0,-g)` at both → VERIFY vector inequality from opposite `v_y` signs.

**Model response:** `v_x` is the same; `v_y` has equal magnitude and opposite sign; speed is the same; velocity vectors differ; acceleration is the same downward vector.

**Rubric:** preserves `v_x`; reverses only the sign of `v_y`; distinguishes speed from velocity; keeps gravity unchanged.

**Independent check:** the velocity vectors cannot be identical because the vertical component signs differ.

---

## Why the five fixed source demands are not Core2B items here

- Q28 requires an untaught calculus differentiation step.
- Q15 is identity-held and requires impact/energy/restitution capability not established here.
- Q21 changes the gravity model beyond the packet.
- Q26 requires trajectory-equation/advanced geometry machinery.
- Q23 requires linear-drag dynamics and integration.

Those are diagnostic evidence for future curriculum/bridge work, not transfer tasks for a capability that this learner has already been shown to possess.

## Release condition

The transfer designs above are structurally valid candidates with explicit parent lineage and protected `DECIDE` moves. For this learner, Core2B remains HOLD until the repository records actual prior exposure to each relevant Core2A parent and either scoped capability evidence or an explicit owner waiver authorizes routing.
