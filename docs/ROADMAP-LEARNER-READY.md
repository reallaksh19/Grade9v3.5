# From machine-honest to learner-ready

> **Authority / status:** Learner-readiness conceptual/historical roadmap — not the live V2.5 execution roadmap. Counts, gap statements and R-stage ordering below are evidence snapshots and design reasoning from that roadmap pass. Keep them as history unless current governed work explicitly revalidates them.
>
> **Current engineering execution authority:** start at [`../agents/relay/REPO_STATE.yaml`](../agents/relay/REPO_STATE.yaml), then follow its [current V2.5 roadmap](../agents/relay/roadmap/OVERALL_ROADMAP.yaml), [progress source](../agents/relay/roadmap/PROGRESS.yaml), and `active_ep.path`. Do not execute work from this document merely because it contains a phase or task sequence.

**Intent this serves.** A student in grades 9–11 understands the hard concepts of physics, mathematics and chemistry through pictorial, self-explanatory material, and works through question banks that prepare them for IIT-JEE. Every phase below is measured against that sentence, not against the architecture.

**Where it stands.** The repository is machine-honest: 146 tests, nine fail-closed gates, two subjects publishing, a library that refuses teaching it has not checked. It is not yet learner-ready, and the distance is measurable. This document measures it, names the root cause, and orders the work.

---

## 1. Pending, concretely

| # | Item | State |
|---|---|---|
| 1 | Core2B has never been produced from any library | No transfer question exists; four of its five required fields have no schema home |
| 2 | Physics figures are hand-authored | Three representations hold no scene instance; the frozen run's figures live in its plan, not the library |
| 3 | Four exit-task oracles held | `ISS-MATH-LIST-BINDING` and three `*-EXIT-DATA` issues |
| 4 | Engine binds one datum per variable | `POLYNOMIAL_VALUE` and `POLYNOMIAL_FROM_ROOTS` take coefficient lists and cannot be bound |
| 5 | Chemistry is contract-only | No validator, no scenes, no library; three validators honestly marked `PROPOSED` |
| 6 | 25 admissible imported packets not yet imported | 13 Mathematics, 12 Physics; the pilot proved the mechanism and stopped |
| 7 | Every gate is `NOT_IN_JEE`, grade 9, `OWNER_EXTENSION` | Zero JEE-tiered content; zero CBSE bindings; the tier vocabulary exists and is unused |
| 8 | No academic or pedagogical review of anything | `CANDIDATE → REVIEWED → CURATED` is implemented and has never been exercised |
| 9 | Chemistry SIL report (#403) not posted | 52/52 rejected is a conversation, not a PR comment |

---

## 2. Product-by-product review, against the role specs

Each product is judged against `Shared/roles/<CORE>.md`, which is the authority for what it must be.

### Core1 — compact orientation notes

**Renders:** the bucket's quantities with meanings and units; each governing relation typeset with its meaning, symbols and conditions, drawn from the library's bound copy of the gate; where the hard work is, with the reason. Verified on `BUCKET-LINEAR-EQUATION`.

**Meets the spec.** Named objects ✓, canonical relations with conditions ✓, hard-transition pointers ✓, anchor values ✓ (via quantities).

**Gap against the intent:** a map with no picture. The spec does not require a figure; the intent does. Core1 should carry the bucket's canonical figure — the one representation that shows what the objects *are* — and today it can only do so where a scene instance exists, which is one Mathematics figure and zero Physics ones.

### Core2 — source question custody

**Renders:** every question the bucket holds, original identity preserved, `SOURCE_CUSTODY` role, machine-checked answer.

**Meets the spec, except one required item has nowhere to live.** The spec requires *ladder hints, where the source supplies them, in their original ordering*. The question schema has no `hints` field. This is the same defect class as the six-Core gap: a spec requiring what the schema cannot hold.

### Core1A — declarative detailed teaching

**Renders:** per microtopic, the inferential jump, the teaching path with each step's action and justification, the exit task with model answer and check; figures where the library holds instances.

**Meets the spec.** This is the strongest product. Steps carry `why_valid`; transforms must show the changed state; exit answers carry an oracle or say why not.

**Gaps against the intent, from the rendered page:**

- *Density.* It is correct and complete, and reads as a proof. A grade-9 student meets a wall of justified prose before any picture.
- *The figure is last.* The compiler appends figure blocks after every text block, so the number line that would have explained exact-versus-truncation appears after the learner has read the whole argument in prose. A figure bound to a microtopic should sit with that microtopic.
- *Broken sentences.* The compiler embeds authored sentences inside its own — *"This gives For x = 2: 3(2) + 2 = 8"*, *"This gives Evidence that the equation selects values"*. The embedded sentence's capital survives. `sentence()` fixed doubled terminators; nothing handles the join.

### Core1B — conceptual self-tutor

**Renders:** Core1A with a "Predict first:" line and a misconception note inserted before each teaching path.

**Fails its own rule.** The README's A/B differentiation rule says the B product must *"elicit the conceptual decision, then supply reconstruction help and misconception repair"*, and warns that *"turning B into A with the nouns changed … fails this rule."* Diffing the two pages: Core1B is Core1A plus eight lines. On the rendered page, *"Predict first: In 3x + 2 = 9, what would you 'work out' before you know x?"* is followed on the very next line by *"A common wrong idea is that The equals sign means work out the left side…"* — the answer, printed under the question, in the same flow. Nothing is elicited, nothing is gated behind the learner's attempt, and there is no reconstruction help distinct from the teaching path. It also inherits both Core1A composition defects, and adds a third: *"A common wrong idea is that The equals sign"* — the same mid-sentence capital.

This is the product the intent leans on hardest — "self-explanatory" — and it is the thinnest.

### Core2A — supported practice with complete solutions

**Renders:** the question with identity and provenance; the solution as a step sequence; the verified numeric; a check.

**Meets the spec on structure.** Identity ✓, breakdown ✓, check ✓, family ✓, exposure role ✓.

**Two gaps.** The spec requires *"the first difficult move made explicit rather than glossed"*; no field marks which step is the difficult move, so nothing can render it differently or verify it is there. And *"hints, where useful"* — no field. With one question per bucket the practice routing the spec describes has nothing to route.

### Core2B — application and transfer

**Never produced.** Not for lack of a question: the compiler correctly refuses to pad it with the Core2A question, because same-family practice is not transfer. But four of the five things the spec requires — the **changed-demand statement**, the **repair route**, the **exposure lineage**, and the **rubric** — have no schema field at all. Even with a transfer question authored, the product could not carry what makes it transfer.

---

## 3. Review against the intent

| Intent | State | Measure |
|---|---|---|
| **Pictorial** | 3 renderers exist: `VECTOR`, `GRAPH`, `NUMBER_LINE` | 8 of 11 declared representation kinds have no renderer. Free-body diagrams, ray diagrams, circuit schematics, particle diagrams, energy profiles, geometric constructions, function plots — the representations that carry meaning at this level — cannot be drawn |
| **Self-explanatory** | Core1B is Core1A with prompts prepended | The A/B rule is not met; nothing elicits before it reveals |
| **Question banks** | One question per bucket | No hints field, no difficulty ladder, no bank; practice routing described in the spec is unimplemented |
| **IIT-JEE** | Nothing tiered | `JEE_MAINS`, `JEE_ADVANCED`, `BOTH` exist in the gate vocabulary and are used zero times; examiner-trap misconceptions exist only in the parallel tracks' nano-research documents |
| **Fool-proof agent execution** | Strong on acceptance, absent on authoring | Nine gates make it nearly impossible to *admit* hollow content. Nothing tells an agent how to *produce* content that will be admitted — it authors, submits, and reads the refusals |

---

## 4. The root cause, and the global fix

Three independent findings this session had the same shape:

1. All three contracts declared six products; the compiler built four.
2. Core2's spec requires ladder hints; the question schema has no field.
3. Core2B's spec requires four things; the schema has none of them.

The role specs were written to the intent. The schema was written to what already existed. Nothing checked one against the other, so the specs stayed aspirational and the schema stayed honest about a smaller thing.

The fix is the same as every gate before it: **a spec↔schema conformance check**, built before the fields, measuring first. Each role spec's *Required content* section names fields; the check reads them and fails when the schema has no home for one. It cannot be written as a free-text parser — the specs are prose — so the specs gain a small machine-readable block naming the fields they require, and the check compares that block against the schema. The prose stays the authority for meaning; the block is the authority for presence.

That is Phase R1, and everything else depends on it.

---

## 5. Roadmap

Phases are in dependency order. Each has exit evidence that can be checked mechanically, and each leaves the repository strictly better if work stops after it.

### R0 — What a learner sees today is broken in three small ways — **DONE**

Cheap, global, and inherited by every phase after, so first. Two of the three were real; both are fixed (`50fc952`, `8981995`).

- **Sentence joins.** ~~the embedded sentence's initial capital is lowered unless it opens with a symbol, a numeral or a proper noun the library marks as such.~~ **Superseded before implementation:** telling a proper noun from a symbol needs knowledge nothing here has, and no library marking existed to supply it. `join()` decides instead whether the authored field is a *fragment*, which belongs inside its lead-in, or a *sentence*, which takes its own line under a lead-in turned into a colon — asking `is_prose`, the predicate the substance gate already trusts. Also narrowed on measurement: three sites were claimed, two were real. `Answer:`, `Predict first:`, `Check yourself:` and `Verify:` end in colons, where a following capital is correct English. Falsifier: *"This gives For x = 2"* is refused, and generally, no composed block may put a capitalised word directly after a lead-in word.
- **Figure placement.** `_figure_blocks` emits each figure immediately after the microtopic block it is bound to, not after all of them. The obligation binding already says which microtopic; the order is the only change. Practice-obligation figures stay with the questions. The falsifier moves the figure onto the *first* microtopic, so landing last fails rather than coincidentally passing.
- ~~Label collision on the number line.~~ **Retracted.** Claimed from a screenshot, then measured against the rendered SVG: no two labels share a row, and nothing extends outside the frame. The figure is correct as drawn. R0 is two items, not three.

**Exit evidence, met:** 153 tests, guard, capability audit, subject sweep, publication sweep and manifest green at both commits. The committed Physics run reports `learner_visible_changes: []`. The compiled Mathematics products embed no sentence mid-sentence — asserted generally across Core1/Core1A/Core1B, not against the two strings found — and every microtopic figure is the block immediately after its microtopic.

~~`republish.py --write` reports the change and it is accepted explicitly.~~ **Retracted: nothing to accept.** There is no committed Mathematics publication — that bucket compiles to inputs on demand. Neither fix changed a published byte; they change what the Mathematics compiler will produce the first time the bucket is published.

### R1 — Close the specs against the schema — **DONE**

Measured before fixing: 100 requirements across the six specs, **68 with no home**. The prediction in §2 named about seven, because it was drawn from reviewing *rendered products* and so found only what the compiler visibly could not emit. Core1 contributed nine findings, none predicted: it renders without complaint, emitting what it has and saying nothing about what the spec asked for and it never received. **A product that silently omits a required element is indistinguishable, on the page, from one that has it.**

Adjudicated: 28 were the spec's name for something the schema already holds (paths corrected), 40 were real (13 fields added, all optional). Three paths were withdrawn as over-translations, including a `kind` enum that would have put subject vocabulary in the engine. `spec_conformance.py --enforce` is in CI.

**Build** the conformance check, measuring only. **Then** add the fields it finds missing:

| Product | Field | Holds |
|---|---|---|
| Core2, Core2A | `question.hints[]` | ordered ladder hints, each with `reveals` (what it gives away) so a hint that hands over the answer is detectable |
| Core2A | `question.answer.difficult_move` | index of the step the spec calls "the first difficult move", so it renders distinctly and its presence is checkable |
| Core2B | `question.transfer` | `{dimension: MODEL_CHOICE \| REPRESENTATION \| CONTEXT \| REASONING_LOAD, statement, builds_on: [question ids]}` — the changed-demand statement and exposure lineage |
| Core2B | `question.repair_ref` | the microtopic teaching-path step the predictable failure points back to |
| Core2B | `question.rubric` | what a good justification contains, as checkable items |
| Core1B | `microtopic.elicitation` | `{prompt, decision_required, reveal_after: ATTEMPT \| HINT \| NEVER_INLINE}` — the conceptual decision the learner must make before the reveal |

**Then enforce** in CI. **Exit evidence:** the check passes; every field a role spec names has a schema home; a planted spec requirement with no field fails.

### R2 — Core1B becomes a self-tutor — **DONE**

Core1B compiles from `microtopic.elicitation` and no longer from the declarative text. Six microtopics authored across Mathematics and Physics; the A/B check refuses the shape the product used to have, and runs over every bucket in the subject sweep. Reveals render inside `<details>`, proven against the rendered HTML. Core1A is byte-identical.

Using `elicitation`: the compiler emits Core1B as *prompt → space for the attempt → reveal gated behind it → reconstruction help → misconception repair*, in that order, with the teaching path as the reveal rather than the opening. The engine renders the gate as a disclosure the learner opens, so a self-study reader cannot read straight through.

**Exit evidence:** the A/B rule is testable and tested — Core1B's learner action differs from Core1A's on every microtopic; a Core1B that is Core1A with prompts prepended is refused.

### R3 — The pictorial engine — **partly done; the list was wrong**

`VECTOR_SUBTRACTION` built, not `FREE_BODY_DIAGRAM`. Physics holds no force content (`force`, `newton`, `friction`, `normal`: zero hits), so the roadmap's first renderer could only have been proven against a hand-authored fixture, which R3's own rule forbids. Physics `FIGURE_AUTHORING` is 0 and Core1 carries each bucket's declared canonical figure. `depiction.py --next` now ranks unbuilt kinds by what is waiting on them; today that is nothing for every kind in every subject, so the next renderer is chosen by what R4.0 imports rather than by this list.

The eight renderers, in the order the existing and admissible buckets need them:

| Renderer | Subject | Unblocks |
|---|---|---|
| `FREE_BODY_DIAGRAM` | Physics | Newton's laws, friction, tension, normal — 8 of the 12 admissible Physics packets |
| `GEOMETRIC_CONSTRUCTION` | Mathematics | triangles, circles, coordinates — 4 of 13 admissible |
| `FUNCTION_PLOT` | Mathematics | quadratics, limits, derivatives, conics — 7 of 13 |
| `RAY_DIAGRAM` | Physics | mirrors, lenses, eye |
| `CIRCUIT_SCHEMATIC` | Physics | Ohm, power |
| `PARTICLE_DIAGRAM` | Chemistry | atoms, bonding, reactions — needed for any Chemistry at all |
| `SYMBOLIC_EQUATION` | Chemistry | balanced equations with state symbols |
| `ENERGY_PROFILE` | Chemistry | thermochemistry, kinetics |

Each renderer follows the `NUMBER_LINE` pattern: declares its own required elements, refuses an undeclared endpoint or frame, digests its marks exactly, and is proven by a scene instance compiled from a library record — never by a hand-authored plan. Core1 gains a canonical-figure slot bound to the bucket's primary representation.

**Exit evidence:** every `IMPLEMENTED` representation kind has a scene instance in a committed library and renders in a committed publication; `FIGURE_AUTHORING` count for Physics drops from three to zero.

### R4 — Question banks, not questions

The schema gains what a bank needs and a single question does not:

- `question.difficulty`: `FOUNDATION | STANDARD | STRETCH | TRAP` — the last named honestly, for items whose difficulty is an examiner's trap rather than a concept
- `question.tier`: the existing gate vocabulary, `NOT_IN_JEE | JEE_MAINS | JEE_ADVANCED | BOTH`
- `bucket.bank_target`: the number of items per difficulty the bucket is meant to hold, so a thin bucket is a measured gap rather than an invisible one
- `question_family` becomes load-bearing: items in a family are same-structure practice; transfer is between families, and the exposure audit checks the claim

Import the 25 admissible packets' `families[]` as family candidates — that is the one layer of the SIL data that maps cleanly.

**Exit evidence:** one bucket at its bank target, every item verified or held with a reason, difficulty distribution reported on the owner board.

### R5 — Practice routing

The role specs describe inputs nothing implements: *scoped capability evidence or an explicit owner waiver*. Add `learner_state` as a run input — `{capabilities: [{id, status: DEMONSTRATED | UNCERTAIN | MISSING, evidence_ref, scope}], waiver: {by, demand, support} | null}` — and route Core2A/Core2B selection from it, holding personalised acceptance when neither is present, exactly as the specs say. Study products proceed unaffected.

**Exit evidence:** the same bucket compiled with three learner states produces three different Core2A selections and the owner board says why; with no state it says `HELD`, and Core1A/Core1B are byte-identical across all four.

### R6 — The JEE layer

Now, not before, because it needs banks (R4), routing (R5) and figures (R3):

- Gates gain `JEE_MAINS` / `JEE_ADVANCED` tiers where the concept genuinely appears; `BOTH` where a grade-9 concept is examined at JEE depth
- The parallel tracks' nano-research documents are the one substantive source of examiner-trap material — Mathematics covers all 15 subtopics, Physics 12 of 43 — and their *Nano-Misconception Diagnostic Matrix* and *Examiner Traps* sections map onto `misconceptions[]` with `difficulty: TRAP`
- Core2B transfer tasks are where JEE-Advanced lives: model choice under an unfamiliar cover story is the exam's defining move

**Exit evidence:** one bucket with `BOTH` tiering publishes a Core2B transfer task with a stated dimension, a rubric, and a repair route, and the exposure audit accepts the transfer claim.

### R7 — The agent authoring contract

The gates say what will be accepted. Nothing says how to produce it. `docs/AUTHORING-CONTRACT.md` plus `Shared/tools/author_bucket.py --scaffold` give an agent:

1. the exact record skeleton for one bucket, with every required field present and empty
2. the order to fill them in — gate binding first, then data, then relations, then microtopics, then questions — because each gate depends on the one before
3. the command that runs every check on the partial package and reports the next gap, not all of them
4. the acceptance criterion: intake admits, authority passes, capability audit passes, one publication verifies

**Exit evidence:** an agent given only the contract and a gate registry authors a bucket that is admitted on first submission, and the time it took is recorded. That number — cost per admitted bucket — is the one the production programme has never had.

### R8 — Review actually happens

`promote.py` is implemented and has never promoted anything. Exercise it: one bucket goes `CANDIDATE → REVIEWED` on real review evidence from a named reviewer who inspected the originals, and the owner board stops saying `NOT_RUN`. This is the first point at which anything here can honestly be called study material rather than machine-checked structure.

**Exit evidence:** one `REVIEWED` bucket; the maturity-monotone check holds across its dependencies.

### R9 — Chemistry

Last, because it needs the particle and equation renderers (R3) and because it is the only subject whose result shape — element-count maps, conservation ledgers — has no publication path yet. Validator module, `PUBLISHABLE_SHAPES` gains the map shape with its own read-back, first library package through the same gates.

**Exit evidence:** one Chemistry bucket publishes six products through the unchanged engine.

---

## 6. Schema deltas, in one place

```
question
  + hints[]              [{text, reveals: CONCEPT | METHOD | ANSWER}]
  + difficulty           FOUNDATION | STANDARD | STRETCH | TRAP
  + tier                 NOT_IN_JEE | JEE_MAINS | JEE_ADVANCED | BOTH
  + transfer             {dimension, statement, builds_on[]}      (Core2B)
  + repair_ref           step id                                   (Core2B)
  + rubric[]             checkable items                           (Core2B)
  answer
    + difficult_move     step index                               (Core2A)

microtopic
  + elicitation          {prompt, decision_required, reveal_after}  (Core1B)

bucket
  + bank_target          {FOUNDATION: n, STANDARD: n, STRETCH: n, TRAP: n}
  + canonical_representation_ref                                   (Core1)

learner_state  (new run input, not a library record)
  capabilities[]         {id, status, evidence_ref, scope}
  waiver                 {by, demand, support} | null

representation_kinds  (contract)
  FREE_BODY_DIAGRAM, GEOMETRIC_CONSTRUCTION, FUNCTION_PLOT, RAY_DIAGRAM,
  CIRCUIT_SCHEMATIC, PARTICLE_DIAGRAM, SYMBOLIC_EQUATION, ENERGY_PROFILE
  each: PROPOSED until its renderer and a compiled scene instance exist

roles/<CORE>.md
  + machine-readable `requires:` block naming the schema fields the prose demands
```

Every addition follows the rule the rest of the repository already enforces: a field either carries the thing or says why it does not. `hints[]` may be empty; `transfer` may be absent on a Core2A item; `elicitation.reveal_after: NEVER_INLINE` is a legal answer. Silence is not.

---

## 7. The agent execution contract, in brief

An agent authoring one bucket runs this sequence, and each step's gate is the one that accepts it:

| Step | Produces | Accepted by |
|---|---|---|
| 1 | gate bindings for the bucket's relations | `authority.py` — expression matches the gate, conditions never dropped |
| 2 | `data[]` with every value the questions and exit tasks will bind | `intake` point 8 — every oracle binding resolves |
| 3 | `relations[]` as bound copies | `authority.py` |
| 4 | `microtopics[]` with roles on every step, elicitation, exit oracle | `intake` points 1–8, `substance.py` — distinct, demonstrated, custodied |
| 5 | `questions[]` at bank target, with hints, difficulty, tier, family | `intake`, exposure audit |
| 6 | one Core2B item with a stated transfer dimension | exposure audit accepts the transfer claim |
| 7 | scene instances for the bucket's representations | renderer refuses an undeclared frame or endpoint |
| 8 | compile and publish | `verify-publication` passes; owner board shows nothing `HELD` |

The contract's own falsifier: an agent that skips step 1 cannot complete step 3; one that skips step 2 cannot complete step 4. The order is enforced by dependency, not by instruction.

---

## 8. What this does not claim

Nothing in this roadmap produces reviewed study material by itself. R1–R7 make the repository *able* to hold and check learner-ready material; R8 is where a human says it teaches. The cost-per-bucket number from R7 is the first honest input to a schedule, and no schedule is promised before it exists.

The parallel tracks' packets remain candidate input only. Twelve Physics and thirteen Mathematics are admissible; their nano-research documents are the best examiner-trap source available and are prose, not records. Chemistry's 52 packets are not a shortcut to R9.