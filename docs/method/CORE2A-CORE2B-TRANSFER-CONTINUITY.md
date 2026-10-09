# I4/I5 — Core2A familiarity to Core2B changed-decision learner progression

Programme: [parent #29](https://github.com/reallaksh19/Grade9v3.5/issues/29), [coordinator #313](https://github.com/reallaksh19/Grade9v3.5/issues/313).

## What the learner now has

The shared compiler-backed Core learner host now offers a question-specific **Core2A familiar worked application → Core2B changed-decision attempt** navigation region, independent of the concept-only Core1/1A/1B path. It uses only already-compiled CoreProjection records, the actual provider `bucket_availability` groups and canonical `question_ref`, `family_ref` and `transfer.builds_on` identities. The feature cannot create a practice question, promote `AUTHORED` to ordinary source Core2, derive a new model or invent a learner's prior knowledge.

A pair is navigable only when:

1. Both sides are in the same available compiler bucket and subject. The child's `transfer.builds_on` names exactly one present structured familiar parent **question**, not just a microtopic or shared family label.
2. Both belong to the same canonical family. Core2A has a resolved reasoning-route crux, authored worked steps and a specific learner check.
3. Core2B includes a declared changed-demand `dimension` (model choice, representation translation, reasoning steps or novelty), an explanatory `statement`, a preserved `invariant` and a concrete `novelty.why_new` assertion.
4. `transfer.protected_move_ref` resolves to one **DECIDE** move that also equals the Core2B reasoning crux. The learner page retains `attempt_before_reveal=true`, the protected move and preattempt answer-withholding posture.
5. The child has an existing specific repair step and an evidence-oriented rubric. A missing or duplicated parent, same stem, dangling/non-DECIDE protected move, missing novelty explanation, missing repair or incorrect reveal posture is a **HOLD**.

The resulting status is intentionally **`STRUCTURED_REVIEW_REQUIRED`**, not academic approval. The reason text is evidence to be checked by an independent reviewer: no string comparison or self-authored `why_new` field can prove a question demands a genuinely novel mental decision.

The learner host exposes only the **transfer dimension** (such as model choice) before entering Core2B. Both the authored `transfer.statement` and the preserved `transfer.invariant` can contain the protected W decision, so the navigation **withholds their verbatim content on Core2A and pre-attempt Core2B**. It reveals them only after Core2B's real `attempt_committed` event; the learner component independently protects its solution/action until attempt. It provides native keyboard-navigation buttons to the exact compiled parent/child IDs and distinguishes **opening the familiar Core2A page** from **actually revealing its worked reasoning after an attempt** (the existing learner component's `reveal_changed` event). Direct Core2B entry produces **prior capability unverified**; mere A page viewing still reports that the worked explanation was not observed. Only if the worked reasoning was revealed does the host disclose that the following transfer is **assisted by instructional exposure**, not certified mastery or a qualified independent transfer assessment. The event observation is transient and does not reach across tabs/devices.

## Real canonical witness / tests

Use the existing authored Physics item `Q-PHY-KIN-2D-2A-HORIZONTAL-LAUNCH-04` → `Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04`. The familiar item provides a stated horizontal launch speed; the transfer child requires identifying the released package's initial velocity from the moving carrier, rather than treating it as rest or continuing the carrier's thrust. The child claims `model_choice` and protects its `R-KIN-TRANSFER-MODEL` DECIDE move. The canonical source already states the preserved shared-clock/gravity-only fall-time invariant and has a specific repair step and rubric. This PR does not author a second answer or alter the physics truth.

Checks include `tests/familiar_transfer.test.mjs` (real generated provider witness, valid structural pair, wrong family, absent/duplicate parent, bogus `builds_on`, same question, missing novelty, invalid decision kind, missing repair/rubric or unsafe W reveal) and the real Chromium `tests/core1_continuity_browser.mjs` (direct B entry warns unverified prior exposure; navigate B→A→B, mark assisted encounter, and verify protected DECIDE action absent from preattempt DOM). The shared workflow `.github/workflows/core1-study-continuity.yml` runs these alongside I2 Core1 learner navigation and existing core page/adapter tests, with exact generated public/standalone HTML check.

## Non-grants / next adjudication

**Explicit holds:** ordinary Core2 authentic source custody (#294 and parked NCERT #68), independent scientific/academic judgement that Core2B really changes DECIDE, QRT-reviewed exact render, learner competence and understanding, independent learner/a11y review, same-screen interaction depth and PDF/browser cross-format review. A structural green CI result neither certifies these nor gives owner authorization to merge/publish. Unmodified legacy Core2B debt remains explicitly managed by `core2b_inventory.py`, not retroactively green.

Further I5 work should create a review packet comparing *what a learner knew after Core2A*, *the parent's solved move*, *the child's genuinely new protected decision* and *specific repair/rubric* with a real independent academic reviewer; then I6 must trace all six roles and attempt/repair/return navigation. Do not call this I4/I5 learner link a fully accepted six-Core product.

## Exact construction repair and honest return (I6 partial)

The existing canonical `application.repair` names a source-specific teaching-path step, not simply a generic topic. `resolveTransferRepair` now requires the step to be present **exactly once** in the same available subject/bucket's compiled `Core1A` microtopic, with matching step ID and authored action. A missing or ambiguous route is **HOLD**.

The learner-host route is **Core2B committed attempt → learner-elected targeted Core1A step → same-question assisted retry**. Until an actual B commitment, no targeted repair link is exposed. The page records the original question and repair-step reference in in-page transient context; returning to B remounts the original learner projection with its independent pre-attempt reveal gate reset. The host expressly states that no wrong mental model was diagnosed and that answering the same question after construction is **assisted practice, not fresh independent transfer**. No automated correctness judgment or learner-data persistence is claimed.

For the existing Physics `K2D3-1` route, the step is canonical and reachable, but **its ability to repair the particular inherited release-velocity decision remains pending independent academic judgement**. Do not upgrade a valid link to a validated teaching repair.

The actual Docs/Pages `docs/core-learning/index.html` now uses the same canonical host template as `public/` and `standalone/`; the browser regression checks both public and Docs/Pages learner hosts, and the builder's `--check` includes all three.

This does **not** close I6: authentic source Core2, independent fresh-item verification, supported diagnosis, staged PDF/print review, a11y and learner evidence are still separate holds.
