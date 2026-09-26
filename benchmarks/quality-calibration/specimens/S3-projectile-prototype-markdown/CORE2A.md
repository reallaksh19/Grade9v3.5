# Core2A — Supported familiar application

**Role:** familiar application with complete solutions  
**Practice provenance:** `AUTHORED_PRACTICE` from the canonical Motion-in-2D package  
**Assessment-surface claim:** none; ordinary Core2 custody is HOLD  
**Learner acceptance:** **HOLD** — no scoped capability evidence or explicit owner waiver is present.  
**Owner estimate:** 50% familiarity is retained as a support input only; it is not mastery evidence.

These items are author-created practice already stored in `Physics/library/phy-kin-2d-motion.v1.json`. They do not impersonate the five source anchors. `question.scaffolds[]` is rendered as authored pedagogy. No scaffold is labelled as a source hint.

---

## 2A-1 — One state, one clock

**Canonical item:** `Q-PHY-KIN-2D-2A-SHARED-CLOCK-01`  
**Primary capability:** `CAP-KIN-2D-INDEPENDENT-COMPONENTS`  
**Family:** `FAM-PHY-KIN-2D-PRACTICE`  
**Exposure role:** PRACTICE  
**Repair:** `K2D1-4`

**Stem:** A tracker reports `x(t)=4t` metres and `y(t)=10-2t²` metres for one particle in one fixed frame. Find the particle's position at `t=2 s`, and explain why x(2 s) may not be paired with y(3 s) to describe one position.

**Conditions:** same particle; same time coordinate; one fixed x-y frame.

**Representation:** `REP-KIN-2D-SHARED-CLOCK` — `VISUAL_HOLD`.

**Authored scaffold ladder:**
- REPRESENT → `R-KIN-2D-CLOCK-REPRESENT`: write x(t) and y(t) in two columns connected to one clock before substituting.
- CONNECT → `R-KIN-2D-CLOCK-PAIR`: label the time beside each evaluated component before pairing.

**Reasoning route:**
1. `R-KIN-2D-CLOCK-REPRESENT` — treat x(t), y(t) as projections of one particle tied to one event time.
2. `R-KIN-2D-CLOCK-EVALUATE` — evaluate both at t=2: x=8 m, y=2 m.
3. **CRUX `R-KIN-2D-CLOCK-PAIR`** — form (8,2) m and reject x(2), y(3) as one state.
4. `R-KIN-2D-CLOCK-CHECK` — verify timestamps match.

**Full solution:** `x(2)=8 m`; `y(2)=10-2(4)=2 m`; position `(8,2) m`. The mixed-time pair is not a simultaneous physical state.

**Independent check:** attach `t=2 s` to both components before calling the pair a position.

**Failure signal:** the answer combines values with different timestamps or treats component independence as independent clocks.

---

## 2A-2 — Constant acceleration on two axes

**Canonical item:** `Q-PHY-KIN-2D-2A-CONSTANT-ACCEL-02`  
**Primary capability:** `CAP-KIN-2D-CONSTANT-ACCELERATION`  
**Secondary:** `CAP-KIN-2D-INDEPENDENT-COMPONENTS`  
**Exposure role:** PRACTICE  
**Repair:** `K2D2-2`

**Stem:** A particle starts with velocity `(3i+4j) m/s` and constant acceleration `(2i-j) m/s²` for 3 s. Find its velocity and displacement after 3 s.

**Conditions:** both acceleration components are constant over the interval.

**Representation:** shared component table / `REP-KIN-2D-SHARED-CLOCK` — `VISUAL_HOLD`.

**Authored scaffolds:**
- REPRESENT → `R-KIN-2D-CA-REPRESENT`: make a signed table of `u_x,u_y,a_x,a_y`.
- CONNECT → `R-KIN-2D-CA-MODEL`: run the constant-a relation once on each axis with the same 3 s.

**Reasoning route:**
1. `R-KIN-2D-CA-REPRESENT` — x: `u_x=3,a_x=2`; y: `u_y=4,a_y=-1`; one `t=3 s`.
2. **CRUX `R-KIN-2D-CA-MODEL`** — the given constant vector makes both component accelerations constant, so component 1D relations are licensed.
3. `R-KIN-2D-CA-CALCULATE` — `v_x=9`, `v_y=1`, `Delta x=18`, `Delta y=7.5`.
4. `R-KIN-2D-CA-CHECK` — verify units, signs and common endpoint.

**Full solution:** `v=(9i+1j) m/s`; `Delta r=(18i+7.5j) m`.

**Independent check:** x uses only x values, y only y values, both use 3 s; velocity units m/s and displacement units m.

**Failure signal:** acceleration magnitude is used as both components, the sign of `a_y` is lost, or times differ between axes.

---

## 2A-3 — Apex event

**Canonical item:** `Q-PHY-KIN-2D-2A-PROJECTILE-APEX-03`  
**Primary capability:** `CAP-KIN-PROJECTILE-MODEL`  
**Secondary:** `CAP-KIN-2D-CONSTANT-ACCELERATION`  
**Exposure role:** PRACTICE  
**Repair:** `K2D3-4`

**Stem:** An ideal projectile has `u_x=12 m/s`, `u_y=20 m/s`, `g=10 m/s²`, +y upward. Find apex time, velocity, acceleration, and height gained.

**Conditions:** no air resistance; gravity only after release; components already resolved.

**Representation:** `REP-KIN-2D-PROJECTILE-MODEL` + event state — `VISUAL_HOLD`.

**Authored scaffolds:**
- REPRESENT → write the horizontal and vertical rules before choosing the top-of-path condition.
- CONNECT → decide which velocity component changes sign and set only that one to zero.

**Reasoning route:**
1. `R-KIN-2D-APEX-REPRESENT` — `a_x=0,a_y=-g`; `v_x=u_x`, `v_y=u_y-gt`.
2. **CRUX `R-KIN-2D-APEX-EVENT`** — apex means `v_y=0`, not full velocity or acceleration zero.
3. `R-KIN-2D-APEX-CALCULATE` — `t=2 s`; `v=(12,0) m/s`; `a=(0,-10) m/s²`; height `20 m`.
4. `R-KIN-2D-APEX-CHECK` — horizontal velocity and downward acceleration remain nonzero.

**Independent check:** only `v_y` vanishes at the apex.

**Failure signal:** setting `v_x=0` or `a_y=0` at the apex.

---

## 2A-4 — Horizontal launch to lower ground

**Canonical item:** `Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04`  
**Primary capability:** `CAP-KIN-PROJECTILE-MODEL`  
**Secondary:** `CAP-KIN-2D-INDEPENDENT-COMPONENTS`  
**Exposure role:** PRACTICE  
**Repair:** `K2D3-6`

**Stem:** A stone is launched horizontally at 15 m/s from a cliff 20 m above level ground. Take +y upward and `g=10 m/s²`. Find flight time, horizontal range and impact velocity.

**Conditions:** no air resistance; `u_y=0`; ground is 20 m below launch.

**Representation:** `REP-KIN-2D-SHARED-CLOCK` then `REP-KIN-2D-EVENT-CLOCK` — `VISUAL_HOLD`.

**Authored scaffolds:**
- REPRESENT → place the 20 m drop only in the y column while x and y share one t.
- CONNECT → name the ground-contact condition before solving.

**Reasoning route:**
1. `R-KIN-LAUNCH-REPRESENT` — `u_x=15,u_y=0,Delta y=-20,a_x=0,a_y=-10`.
2. **CRUX `R-KIN-LAUNCH-EVENT`** — ground contact is `-20=-5t²`, giving `t=2 s`.
3. `R-KIN-LAUNCH-REUSE` — range `=15(2)=30 m`; `v_x=15`, `v_y=-20`.
4. `R-KIN-LAUNCH-CHECK` — vertical motion sets fall time; horizontal speed sets range.

**Full solution:** flight time 2 s; range 30 m; impact velocity `(15i-20j) m/s`.

**Independent check:** doubling only horizontal speed would not change this ideal fall time.

**Failure signal:** use of a same-height shortcut or a horizontal equation to determine the fall event.

---

## 2A-5 — Same-height return

**Canonical item:** `Q-PHY-KIN-2D-2A-SAME-HEIGHT-05`  
**Primary capability:** `CAP-KIN-PROJECTILE-MODEL`  
**Secondary:** `CAP-KIN-2D-CONSTANT-ACCELERATION`  
**Exposure role:** PRACTICE  
**Repair:** `K2D3-5`

**Stem:** An ideal projectile later lands at the same height with `u_x=12 m/s`, `u_y=16 m/s`, `g=8 m/s²`. Find total flight time, range and landing velocity.

**Conditions:** air resistance neglected; launch and landing heights equal; +y upward.

**Representation:** `REP-KIN-2D-EVENT-CLOCK` — `VISUAL_HOLD`.

**Authored scaffolds:**
- REPRESENT → write the landing geometry first: `Delta y=0`.
- CONNECT → the vertical equation has a launch root and a later root; select the requested event.

**Reasoning route:**
1. `R-KIN-2D-SAME-REPRESENT` — landing condition `0=16t-4t²`.
2. **CRUX `R-KIN-2D-SAME-EVENT`** — choose the nonzero root `t=4 s`, not launch at t=0.
3. `R-KIN-2D-SAME-REUSE` — range `48 m`; landing `v_y=-16 m/s`.
4. `R-KIN-2D-SAME-CHECK` — `v_x` matches launch; `v_y` equal magnitude/opposite sign.

**Full solution:** total flight time 4 s; range 48 m; landing velocity `(12i-16j) m/s`.

**Independent check:** same-height return preserves the horizontal component and reverses the vertical component sign.

**Failure signal:** selecting the t=0 root as the landing event.

---

## Fixed-demand inheritance

The five owner anchors remain visible in `demand-map.json`, but none is silently substituted into this learner practice set.

- Q28: learner eligibility NOT_ESTABLISHED and differentiation is an upstream gap.
- Q15: learner EXCLUDED, identity HOLD, and bounce/energy capability not established.
- Q21: learner EXCLUDED; changed-gravity extension.
- Q26: learner EXCLUDED; trajectory/specified-point extension.
- Q23: learner EXCLUDED; linear-drag dynamics/calculus gap.

This Core2A content is structurally complete authored practice, but personalized learner acceptance remains HOLD until scoped capability evidence or an explicit owner waiver exists.
