# Improvements

> Status: **future concepts only**.
>
> This file is not roadmap authority, execution authority, academic truth, or an amendment to an accepted mother issue.
> Current work must continue to follow the live relay roadmap / `REPO_STATE.yaml` / active execution package.
> A concept recorded here becomes real work only after evidence exposes a concrete problem and the Owner/current roadmap explicitly promotes it.

## 1. Current governing task — Mother Issue #159

**Mother issue:** [#159 — Core: Subtopic session router: evidence → support → visual hints → exercise demand](https://github.com/reallaksh19/Grade9V3/issues/159)

For the subtopic-session router, Issue #159 is the governing contract ("bible") unless a later explicit Owner/roadmap decision supersedes it.

Its owned responsibility is the reusable, subject-neutral runtime that composes existing canonical structures into the next learner action:

~~~text
matrix / rung
+ capability evidence
+ support ladder
+ canonical representation / scene
+ question family / question
+ hint ladder
+ transfer metadata
        ↓
derived session routing
~~~

The mother contract's important invariants remain authoritative:

- evidence and runtime posture are different things;
- READY / REINFORCE / REBUILD are derived session outcomes, not persisted mastery states;
- a rough owner estimate is orientation only and cannot create DEMONSTRATED evidence;
- starting support and post-difficulty hints have different jobs;
- support availability must come from the active canonical family support ladder;
- helped/guided success is not independent DEMONSTRATED evidence;
- repair is followed by fresh verification before confidence is restored;
- transfer is justified only by stable same-family independent evidence;
- question demand is independent from interaction mechanics;
- representation / scene, reasoning checkpoint, and pedagogy injection are separate;
- renderer behavior must not rewrite academic truth;
- interaction telemetry is not learner mastery unless an explicit exercise contract turns it into a valid DIRECT_ATTEMPT observation;
- canonical Physics/matrix content remains the academic authority; Shared routing consumes refs rather than rewriting subject truth.

### Current interpretation rule

Do **not** silently reinterpret Issue #159 from this file.

In particular, the current mother contract says starting support is what is handed over before an attempt and maps the baseline posture as:

~~~text
READY      -> low support
REINFORCE  -> medium support
REBUILD    -> high support
~~~

That remains the present accepted contract.

The concept below is deliberately **not** a correction to that contract today. It is a possible later refinement to investigate only if real learner-facing use demonstrates a problem.

---

## 2. Future concept — self-paced minimal-feedback disclosure

### Why this concept is recorded

Grade9V3 is intended to be a personal, self-paced learning system in which the learner increasingly discovers gaps and verifies learning with little external steering.

A future learner-facing question may therefore be worth testing:

> Should evidence determine what support is automatically shown, or only what support is safe/recommended/available if the learner needs it?

This is currently a **concept**, not an implementation requirement.

### Hypothesis

A minimal-feedback, self-paced system may eventually need to distinguish three states that are currently easy to conflate:

~~~text
support_available
    what canonical help may safely be offered

support_recommended
    what the evidence-based posture suggests would be useful

support_consumed / revealed
    what the learner actually chose to see or use
~~~

Possible future principle:

> Evidence constrains what the system may infer and what help it may safely offer. The learner controls pace and, where practical, whether optional help is consumed.

This principle must **not** be implemented merely because it sounds preferable. The existing model gets priority until an executable learner/host falsifier proves that automatic starting support is harming the intended self-paced experience.

### Existing-model-first question

Before adding any new Core state or abstraction, test whether the existing Issue #159 output already supports the desired behavior.

If the host can treat `starting_support` as a safe/recommended support contract while still allowing a clean learner attempt and only revealing optional help on learner request, then **no Core architecture change is needed**.

A renderer/host behavior problem should remain a renderer/host problem.

Do not add:

- a new mastery state;
- an independence score;
- another difficulty scale;
- another question taxonomy;
- a per-click learner model;
- a second hint system;
- duplicated support scenes.

### Primary future falsifier

The strongest falsifier is not "does the hint preserve the answer?"

It is:

> Can a learner with UNCERTAIN/MISSING history still make a clean independent fresh attempt without the system automatically consuming the support that evidence says is appropriate?

If the answer is already yes in the real host, this concept requires no implementation.

If the answer is no, classify the defect before changing Core:

~~~text
host/UI disclosure behavior?
presentation-contract ambiguity?
content support ladder?
actual Core routing limitation?
~~~

Choose the smallest owner-correct repair.

### R3 witness — body ownership

Future test case:

1. learner has REINFORCE evidence for R3;
2. a fresh body-ownership problem is opened;
3. the learner is allowed a clean attempt without optional orientation being consumed automatically;
4. support such as "choose one body first" remains available;
5. if the learner requests it, subsequent work is correctly treated as helped;
6. force ownership / interaction membership is never silently solved by the support;
7. a later fresh unassisted success may restore independent evidence.

A failure would be meaningful if the learner cannot attempt the protected body/interaction decision independently because the host always exposes medium/high support first.

### R8 witness — friction model choice

Future test case:

1. learner has REINFORCE or prior REBUILD history for quantitative friction;
2. a fresh problem does not state whether contact sticks or slips;
3. the learner may first attempt the model choice without optional help;
4. if requested, assistance progresses from contact/orientation to force inventory to static-feasibility reasoning;
5. no support reveals static versus kinetic state before the learner makes/test that decision;
6. help usage keeps the result non-independent until fresh verification.

A failure would be meaningful if evidence-driven starting presentation automatically reveals enough structure that the supposedly fresh model-choice attempt is no longer genuinely independent.

### Minimal-feedback retry question

The same distinction may apply after a wrong answer.

Current feedback correctly selects the next safe non-answer hint. A later learner-facing test should determine whether the best self-paced experience is:

~~~text
incorrect
-> smallest result/diagnostic signal
-> retry
-> hint available on request
~~~

rather than automatically displaying Hint 1 on every first failure.

Again, this is not a request to change `feedback.py` now. First prove the behavior is actually harmful in real learner use.

### Self-paced challenge access

A later product decision may also distinguish:

~~~text
transfer_eligible
    the system has enough evidence to recommend/claim readiness for transfer

learner_can_open_transfer
    the learner is allowed to explore a harder problem voluntarily
~~~

A self-paced learner may be allowed to explore ahead without the system treating that exploration as evidence of prerequisite readiness.

Do not turn this into architecture unless the real host currently couples those two concepts and that coupling causes a demonstrated problem.

---

## 3. Promotion rule for this concept

This idea should remain in `improvements.md` until all of the following are true:

1. a real learner-facing or host-level case reproduces the problem;
2. the exact protected learner decision is identified;
3. current Issue #159 behavior is measured rather than inferred;
4. the existing model is tried first;
5. ownership is classified correctly between Core, content, Atlas host, and workbench/renderer;
6. an executable falsifier demonstrates that the smallest current model cannot express the required self-paced behavior;
7. regression checks preserve the mother issue's evidence, repair, transfer, hint, renderer, and academic-truth invariants;
8. the current Owner/roadmap explicitly promotes the concept into active work.

Until then:

> **Issue #159 is the governing implementation contract.  
> Self-paced support disclosure is only a future concept to test, not a reason to rewrite completed work.**
