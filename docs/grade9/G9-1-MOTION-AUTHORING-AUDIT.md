# G9-1 Motion authoring audit

> Workstream: **Grade 9 Physics only**
>
> Matrix: `MATRIX-PHY-KIN-1D-MOTION`
>
> Result: **the six-rung Grade-9 canonical spine remains the required/default boundary; Issue #126 adds R6 only as an Owner-authorized, non-default circular-dynamics extension.**

## Authoritative scope checked

The current CBSE Academic **Class IX Science (2026-27), Standard** syllabus places Motion in
Unit III, *Motion, Force, Work and Sound*. Its Motion section requires:

- displacement, velocity and acceleration;
- straight-line graphical representation for constant velocity and constant acceleration;
- constant-acceleration kinematic equations by graphical method;
- elementary uniform circular motion;
- differentiating distance/displacement and speed/velocity;
- average velocity / average acceleration from the corresponding graphs;
- deriving and applying the kinematic equations;
- deriving the expression for speed in uniform circular motion.

Official locator:

`https://cbseacademic.nic.in/web_material/CurriculumMain27/SecPart1/ScienceSt_SecP1_2026-27.pdf`

Relevant section: **Motion, PDF page 14**.

The current NCERT Class IX Science book also contains **Chapter 4 — Describing Motion Around Us**.
This audit uses the CBSE 2026-27 Standard syllabus as the workstream scope check and does not
promote any repository record to curriculum authority.

## Current matrix-to-scope working sheet

`SCOPE_REASON` is planning metadata only. It is not persisted into the matrix schema.

| Rung | Canonical microtopic | Primary capability | SCOPE_REASON | Grade-9 decision |
| --- | --- | --- | --- | --- |
| R1 | `MIC-PHY-KIN-DISTANCE-DISPLACEMENT` | `CAP-KIN-DISTANCE-DISPLACEMENT` | `SYLLABUS_REQUIREMENT` | Keep; directly covers distance vs displacement |
| R2 | `MIC-PHY-KIN-AVERAGE-RATES` | `CAP-KIN-AVERAGE-RATES` | `SYLLABUS_REQUIREMENT` | Keep; covers average speed / average velocity distinction |
| R3 | `MIC-PHY-KIN-ZERO-V-NONZERO-A` | `CAP-KIN-ZERO-V-NONZERO-A` | `DECLARED_EXTENSION` | Keep as a compact misconception/diagnostic rung; do not treat it as a separate syllabus claim |
| R4G | `MIC-PHY-KIN-MOTION-GRAPHS` | `CAP-KIN-MOTION-GRAPHS` | `SYLLABUS_REQUIREMENT` | Keep; directly covers position-time and velocity-time graph interpretation |
| R4 | `MIC-PHY-KIN-CONSTANT-ACCELERATION` | `CAP-KIN-CONSTANT-ACCELERATION` | `SYLLABUS_REQUIREMENT` | Keep; directly covers graphical derivation/application of the Grade-9 equations |
| R5 | `MIC-PHY-KIN-UNIFORM-CIRCULAR-MOTION` | `CAP-KIN-UNIFORM-CIRCULAR-MOTION` | `SYLLABUS_REQUIREMENT` | Keep; current Standard syllabus explicitly includes elementary uniform circular motion |
| R6 | `MIC-PHY-KIN-CIRCULAR-DYNAMICS-ROLE` | `CAP-KIN-CIRCULAR-DYNAMICS-ROLE` | `OWNER_EXTENSION` | Non-default Issue #126 extension; radial acceleration/net-force role, friction capacity, cut-string transfer and bounded vertical-circle reasoning must not be interpreted as ordinary Grade-9 completion scope |

## Four QA checks

### 1. Is each rung justified in the Grade-9 slice?

Yes for R1, R2, R4G, R4 and R5 by the inspected Standard syllabus.

R6 is **not** justified as a Standard-syllabus requirement. It exists only because the Owner explicitly activated Issue #126 after the Grade-9 programme baseline was reconciled; the matrix marks it `default_entry_eligible: false` and R5 retains its `centripetal force formula` ceiling.

R3 is not being used as a new curriculum claim. It is retained as an explicitly declared
conceptual extension/diagnostic because it distinguishes velocity from acceleration at a
turning point and already has complete teaching, misconception repair and fresh verification.

### 2. Does canonical teaching already exist?

Yes for the six-rung Grade-9 spine. Issue #126 does not duplicate R5; it adds a separate R6 microtopic because the existing R5 ceiling explicitly excludes the centripetal-force formula.

R6 reuses `CAP-KIN-UNIFORM-CIRCULAR-MOTION` and `CAP-NLM-SECOND-LAW` as prerequisites rather than expanding either prerequisite owner's meaning.

### 3. Is each row independently fail-able?

Yes. The six Grade-9 spine capabilities have separate observable success criteria:

- endpoint change versus path travelled;
- average speed versus average velocity from the correct totals;
- zero velocity versus nonzero acceleration;
- graph height/slope and graph-type interpretation;
- constant-acceleration model choice and equations;
- uniform circular speed with changing velocity direction.

R6 is not story-specific: it owns the reusable circular-dynamics move `real-force radial components → net inward role`, with string, friction, gravity and vertical-circle cases treated as mechanisms/transfer contexts.

### 4. Is any apparent need only a context change?

Yes. Falling/throwing, runners, vehicles and similar Motion stories should map to these
reusable actions rather than creating context-named capabilities.

## Correction made in this pass

The Motion bucket previously declared:

`BUCKET-PHY-VEC-ADD-SUB`

as a whole-bucket prerequisite.

That is too broad for the Grade-9 Standard Motion slice. It causes the publication compiler
to carry the complete vector-addition bucket into the Motion baseline even though the
current Motion capabilities do not require general two-dimensional vector composition.

The bucket-level prerequisite is therefore removed.

This does **not** prohibit a future worksheet from bringing vector addition into a study route.
If a real question needs it, it enters through `QUESTION_DEMAND`, a genuine capability
prerequisite, or `DECLARED_EXTENSION`.

## What is deliberately not changed

- No matrix schema field is added for grade/class.
- No rung is added merely because the syllabus has another wording; R6 is an explicit Owner extension and remains non-default.
- No Grade-10/11 projectile-motion or general 2D kinematics content is imported.
- No source question is fabricated.
- No record is promoted from `CANDIDATE`.
- No exact CBSE `PRESCRIBED` binding is claimed; the curriculum-binding registry remains the
  authority for that stronger claim.
- Historical matrix ID `MATRIX-PHY-KIN-1D-MOTION` is retained for compatibility even though
  the current Grade-9 tail includes elementary uniform circular motion.

## G9-1 disposition

```text
current six-rung Motion matrix
→ scope checked against current Grade-9 Standard syllabus
→ canonical teaching already exists
→ one unjustified broad bucket prerequisite removed
→ no missing Grade-9 Motion teaching identified
→ proceed to G9-2 Force and Laws of Motion after guardrails are green
```


## Issue #126 Owner-extension amendment

The later Owner instruction to proceed with the next remaining backlog item activates Issue #126 without rewriting the Grade-9 scope finding above.

The durable boundary is:

```text
R5  = elementary uniform circular motion
      tangent velocity + inward acceleration qualitatively + v = 2 pi r / T
      Grade-9/default eligible

R6  = circular dynamics force-role extension
      a_r = v^2/r
      Sigma F_r = m v^2/r
      force-type vs net-radial-role classification
      friction-capacity / cut-string / vertical-circle transfer
      default_entry_eligible = false
```

R6 therefore adds capability for an explicit Owner-requested extension while preserving the statement that no additional **Grade-9 required** Motion teaching was missing in the original audit.

The matrix coordinate changes only to preserve strict prerequisite ordering inside the schema-bounded 0–100 ladder: R5 moves from 100 to 99 and R6 occupies 100. This is a routing coordinate change, not a change to R5's syllabus status, microtopic, capability, ceiling, teaching meaning, or default eligibility.
