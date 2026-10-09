# I5 independent review work order — carrier-release model decision

**Work order:** `core2b-independent-decision-workorder/v1` · **Status:** PREPARED_UNASSIGNED · **Academic outcome:** PENDING_INDEPENDENT_ADJUDICATION · **Scope:** exactly one authored Physics Core2A→Core2B pair.

The source is `Physics/library/phy-kin-2d-motion.v1.json`, package `LIB-PHY-KIN-2D-MOTION-AUTHORED`, currently marked `CANDIDATE`. This is **not** an ordinary Core2 exam source, not a publisher-approved exam item and not independent academic evidence. The internal generator binds the **full source bytes and both exact canonical question records to SHA-256 hashes**, so a reviewer can identify precisely which mathematical claims and initial conditions they inspected. Do **not publish the generated JSON as learner content**: it deliberately contains the protected answer.

## Scope: what a learner already saw versus the proposed new decision

**Prior familiar exposure:** `Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04` (Core2A), a cliff launch with horizontal speed 15 m/s **given**, vertical displacement −20 m **given** and a shared physical event clock. The familiar crux `R-KIN-LAUNCH-EVENT` asks the learner to choose the *vertical landing event* as the source of the flight time, then reuse the result in horizontal range and impact velocity.

**Candidate changed-demand item:** `Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04` (Core2B). A plane moves at 50 m/s and releases a package from 80 m; air resistance is negligible. Now the model's initial horizontal velocity is *not given as the package's own launch speed*. The child is labelled `model_choice`; its protected `R-KIN-TRANSFER-MODEL` move claims the learner must **decide the package's release-state velocity in the ground frame**, distinguishing inherited carrier velocity from an invalid zero velocity or continued engine thrust.

The author claims the invariant is shared-time independent horizontal and vertical motion, with fall time still determined vertically. The author also claims Core1A/B and other Core2A anchors have never worked *this exact release-state choice*. **Those are claims to challenge, not findings automatically proved by the compiler or this packet.**

## Questions for an independent reviewer

| Area | Required judgement | Evidence anchored in packet |
| --- | --- | --- |
| A — familiar | What precise decision was taught in Core2A, and what information was already supplied? | Parent stem, crux, route, worked answer check |
| B — novelty | Is initial velocity at carrier release genuinely new cognitive work after the *actual* Core1A/B and Core2A teaching, or merely a familiar model in new words? | Both stems, canonical protected DECIDE, author novelty list, earlier exposure |
| C — prerequisites | Is any physical law newly required but **not** taught? | Capability closure from existing inventory and actual instructional content |
| D — correctness | Does the gravity-only model and frame change check out independently? | Assumptions, exact route, rubric, independent frame check; calculate 4 s and 200 m |
| E — withholding | Do navigations, staged images, hint, scaffold, static PDF or other pre-attempt paths leak the protected model choice? | Protected move, hints, scaffolds, authored invariant and transfer statement |
| F — repair | Does teaching step `K2D3-1` actually remediate a *wrong release velocity*, as opposed to stating only `a_x=0,a_y=-g`? Is the rubric specific? | Exact teaching step, misconception, child reasoning and rubric |
| G — independent disposition | **ACCEPT_TRANSFER**, **REWORK_TO_CORE2A** or **TEACH_PREREQUISITE_FIRST**, with reviewed-source, learner and mathematical evidence | Exact source/question digests plus signed review receipt |

**Specific challenge to the current repair:** `K2D3-1` correctly asks for post-release forces and component accelerations, but its wording does not explicitly teach *inherit the carrier's velocity at release*. If the reviewer confirms that as the missed decision, the repair could be insufficient despite resolving to a valid step. Do **not auto-accept** this case on the strength of a resolvable `repair_ref`.

## Generate the exact internal evidence packet

```sh
python Physics/tools/core2b_decision_workorder.py \
  --out /tmp/physics-transfer-decision-workorder.json \
  --enforce-structure
python -m unittest tests.test_core2b_decision_workorder
```

The first command checks only mechanical contradictions and emits a JSON packet with full authored reviewer-only answer content, source SHA-256, per-question SHA-256, seven review prompts and existing Core2B capability-debt notes. The `--enforce-structure` flag **does not** mean the independently judged transfer is accepted; the result remains `PREPARED_UNASSIGNED` or `PREPARED_WITH_STRUCTURAL_HOLDS`. The owning CI archives it as a **nonrelease internal review artifact**.

The packet does not invent a reviewer, signature, date, science sign-off, browser QRT pass, learner result, source license or rights grant. Any reviewer decision must be a separately authenticated receipt referring to the exact source-question and rendered-product digests; do not edit a generated work order to pretend that acceptance happened.

## Still held after this work order

- Independent academic novelty and capability-continuity verdict;
- independent check of whether `K2D3-1` is a sufficient *initial-velocity-specific* repair;
- real postattempt learner responses, downstream exact QRT and browser/PDF source/reveal review;
- authentic ordinary Core2 exam-source custody (#294; #68 remains parked);
- I6 six-role learner navigation and owner release authorization.

The bounded deliverable is a **reproducible, challengeable review packet**, not an additional transfer item or a six-Core completion claim.
