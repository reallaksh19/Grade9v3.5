# ISS66 U10A — eight-run integrated replay / handoff matrix

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U10A only — replay the structural contracts against frozen #49–#56 evidence and classify each outcome before final handoff  
**Integrated implementation head:** `6be1a704bbd9fef6f15292d41ed2277badd5c0ff`  
**Evidence branch basis before U10A:** `e88e7ab60d56b184bd22ad1bea538c6bf2e89b07`  
**PROTOCOL_REF:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`

## Disposition vocabulary

U10A uses only:

- **PASS** — the integrated contract directly resolves or safely constrains the reproduced structural failure and retained exact-head validation exists.
- **REPLAY_REQUIRED** — the frozen run predates evidence now required by the contract; preserve the historical claim but do not newly adjudicate/accept it.
- **NO_CHANGE** — the run/proposal does not justify another shared contract change.
- **PRE_EXISTING_BLOCKER** — comparable frozen evidence is incomplete, or an unrelated pre-existing product/runtime blocker prevents a stronger claim.

This vocabulary is deliberately about **contract replay**, not mathematical correctness of the frozen questions.

## Main result

The integrated contracts make several previously ambiguous platform decisions deterministic:

- Core1A layout expectation follows the selected blueprint, not generic stage/support fractions.
- author review cannot satisfy independent rendered acceptance;
- rendered review remains bound to exact bytes;
- protected-completing support can be distinguished from after-attempt help;
- question representations can be bound to an exact case/owner/data/asset;
- a learner misconception cannot become confirmed from a wrong answer or index alone;
- legacy generic repair remains available when no specific diagnostic claim is made;
- interaction proposals do not gain shared-schema status merely because they reuse a slider-like gesture.

However, the new contracts **do not retroactively validate the historical difficulty/QRT labels**.

That distinction is the central U10A result.

## Frozen-run matrix

| Run | Frozen basis | Main frozen signal | Presentation | Review basis | Difficulty / QRT | Support / representation | Diagnostic boundary | Interaction |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| **#49 A · intended D1** | `b9fabd2…` | Q10 D2/SYNTHESIZE; inherited Core1A stage-support finding | **PASS** | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |
| **#50 A · intended D2** | `a58eebe…` | Q10 D3/JUSTIFY; candidate acceptance pending | NO_CHANGE | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |
| **#51 A · intended D3** | `b94ede2…` | Q8 D4/JUSTIFY; explicit inherited layout mismatch | **PASS** | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |
| **#52 A · intended D4** | no symmetric frozen late-stage handoff in parent evidence | Q4 D4/SYNTHESIZE at available checkpoint | NO_CHANGE | **PRE_EXISTING_BLOCKER** | **REPLAY_REQUIRED** | **PRE_EXISTING_BLOCKER** | NO_CHANGE | **PRE_EXISTING_BLOCKER** |
| **#53 B · intended D1** | `bc464d8…` | different hardest target; zero-finding author posture; coefficient-grid proposal | **PASS** at shared authority | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |
| **#54 B · intended D2** | `3d17905…` | all D2; Q6 JUSTIFY; full author facet YES | NO_CHANGE | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |
| **#55 B · intended D3** | `91951ab…` | Q8 D3/JUSTIFY; same layout defect; staged-support/case pilot basis | **PASS** | **PASS** | **REPLAY_REQUIRED** | **PASS** | **PASS** | **NO_CHANGE** |
| **#56 B · intended D4** | `40ca527…` | Q3 D4/JUSTIFY; 7 D4 + 3 D3; scrubber proposal | NO_CHANGE | **PASS** | **REPLAY_REQUIRED** | NO_CHANGE | **PASS** | **NO_CHANGE** |

## Why every frozen academic classification is REPLAY_REQUIRED

I re-read each available frozen question ledger at its exact candidate head.

Available frozen ledgers:

| Issue | Frozen head | U04 `component_evidence` present? |
| --- | --- | --- |
| #49 | `b9fabd22e588f295eddce3ba3286b7cead4d5139` | **No** |
| #50 | `a58eebee28112080393cc47e4295862efc43dbed` | **No** |
| #51 | `b94ede24c7ba64ed36ba5f137b65d95816164599` | **No** |
| #53 | `bc464d831f4815a45dd45d29ecf6bcc16d5af8ab` | **No** |
| #54 | `3d17905ebee4ac6cf39057ac05d49947b1b50430` | **No** |
| #55 | `91951abc430ff50ae526110488d9b12e27e30af5` | **No** |
| #56 | `40ca52786c0b5d0c400a5c730314a01689de836a` | **No** |

#52 does not have symmetric frozen late-stage evidence available to the parent replay.

Some runs contain legacy component scores, crux refs or cognitive-demand prose. Those are useful historical evidence. They do not satisfy U04's new admission shape, which requires:

1. five per-component evidence strings against the canonical 0/1/2 rubric;
2. a canonical `answer.crux_move_ref` resolved inside `reasoning_route[]`;
3. normalized demand basis bound by the QRT resolver to that crux.

Therefore U10A does **not** choose between historical D-band disagreements.

It preserves:

- #49 vs #53 hardest-target divergence;
- #50 vs #54 strong D2 classification divergence;
- #51 vs #55 Q8 D4-vs-D3 disagreement;
- #52 vs #56 asymmetric D4 evidence;

as calibration fixtures for a fresh evidence-authoring replay.

## Pair dispositions

### D1 pair — #49 / #53

**Academic classification: REPLAY_REQUIRED.**

Both frozen ledgers predate component evidence. The new contract therefore prevents the earlier different hardest-target and band claims from being silently merged.

**Structural result:**
- presentation authority: PASS;
- review basis: PASS;
- interaction proposal: NO_CHANGE.

### D2 pair — #50 / #54

**Academic classification: REPLAY_REQUIRED.**

This remains the strongest historical disagreement:
- #50: mixed D1–D3, hardest Q10 D3/JUSTIFY;
- #54: all D2, hardest Q6 D2/JUSTIFY.

U04D already established:
- neither has component evidence;
- #50 additionally lacks canonical crux evidence in its frozen classification lane;
- #54 has crux refs but no normalized crux-bound demand basis.

No adjudication state is added until independently admissible replays still disagree.

### D3 pair — #51 / #55

**Academic classification: REPLAY_REQUIRED.**

The pair still has meaningful historical convergence:
- both select Q8;
- both select JUSTIFY;
- both use the same difference-polynomial/root-bound reasoning family.

But D4 vs D3 is not adjudicated because the frozen records predate U04 evidence admission.

**Structural result: PASS** for the shared layout defect.

#55 additionally supplies the retained pilot lineage used by:
- U05 support-disclosure replay;
- U06 question/case representation replay.

Those integrated retained tests are green.

### D4 pair — #52 / #56

**Academic classification: REPLAY_REQUIRED.**

#56 is a complete frozen candidate but still predates U04 evidence.

#52 never reached a symmetric late-stage semantic-review/builder handoff in the evidence available to this parent, so symmetric non-academic comparison remains:

**PRE_EXISTING_BLOCKER.**

No inference is manufactured to fill the missing side.

## Review acceptance replay

Several frozen runs contain strong authored review claims:
- #53 zero quality findings;
- #54 full facet YES;
- #56 10/10 H/S/P/M PASS plus zero W leakage.

Other runs explicitly preserve non-green/inherited findings:
- #49;
- #51;
- #55 layout analysis.

The integrated result is now deterministic:

> None of those author-review postures is independent rendered acceptance.

U03 retained guard evidence proves:
- `AUTHOR_ONLY` cannot satisfy an independent rendered-review requirement;
- rendered review must bind to exact artifact SHA;
- changed artifact bytes invalidate the binding.

Thus the historical difference in reviewer confidence no longer changes acceptance semantics.

**Disposition: PASS.**

## Presentation replay

The independently reproduced Core1A defect in #49/#51/#55 was:

```text
active Core1A blueprint = SINGLE_PANE
but quality/audit expectation = STAGE_SUPPORT because support_fraction existed
```

U02 now derives split expectation from:

`responsive_policy.expanded == STAGE_SUPPORT`

rather than fraction presence.

Retained layout observation tests on the integrated head:

**8 tests / 8 pass / 0 fail.**

**Disposition: PASS.**

#53's candidate also discussed CSS/fraction synchronization. U10A treats the **shared authority** part as fixed, but does not claim every frozen candidate's hand-authored CSS/layout observation was re-rendered.

## Protected support + representation replay

The strongest retained integration path is the staged Set B pilot derived from frozen **#55 Q1**.

On integrated head `6be1a704…`:

- Core2 staged-support contract: **25 tests, OK**;
- representation binding contract: **4 tests, OK**;
- Playwright staged-support state replay: **SUCCESS**.

Browser state proves:
- pre-attempt disclosures locked;
- after-attempt support becomes visible after commitment;
- full solution can remain closed;
- solution-only WORKED visual stays hidden until solution disclosure.

Representation tests prove wrong:
- question owner;
- datum;
- asset;
- Core role

all fail closed.

**#55 disposition: PASS.**

Other stress runs do not independently establish additional support/case-binding requirements.

**Other-run disposition: NO_CHANGE.**

## Diagnostic replay

Historical M1–M3 author records are retained as authored misconception hypotheses/review evidence.

They are **not** converted into learner diagnoses.

Integrated U07/U09 behavior now requires:

```text
canonical hypothesis
→ canonical discriminating probe
→ observed learner response
→ CONFIRMED | REFUTED | INDETERMINATE
```

Only `CONFIRMED` may select misconception-specific repair.

Bare index / unsupported claim remains `DIAGNOSE`.

Existing generic repair remains compatible when no specific diagnostic claim is made.

Exact-head evidence:
- diagnostic contract: **7 tests, OK**;
- migrated caller integration: **85 tests, OK**.

**Disposition: PASS.**

## Interaction replay

U08's final decision remains:

`NO_CHANGE`

The proposals are preserved:

- #49 bounded-parameter probe;
- #50 coordinate plot response;
- #53 polynomial coefficient grid;
- #54 rational-domain inspector;
- #56 continuous parameter scrubber.

The only repeated UI family is #49/#54/#56 numeric probing.

They do not yet share one independently demonstrated learner-state/evidence contract, and all recurrence remains inside the polynomial benchmark family.

No interaction schema is added.

## Accepted 4×7 QRT coverage

U10 acceptance requires coverage to be derived only from **accepted primary classifications**.

For #49–#56 under the integrated contract:

```text
accepted primary classifications = 0
accepted QRT cells contributed by these eight frozen runs = 0
```

This does **not** erase historical counts such as #49's 7/28 author-classified primary cells.

It means none of the historical rows has yet been:
1. re-authored with U04 component evidence;
2. bound to the normalized canonical crux/demand contract;
3. independently accepted.

Therefore U10A does not aggregate historical A/B duplicates into a coverage claim.

## Retained exact-head integrated evidence

Integrated implementation head:

`6be1a704bbd9fef6f15292d41ed2277badd5c0ff`

Retained validation:

- QRT hardening: **42 tests, OK**
- U07 diagnostic contract: **7 tests, OK**
- U09 migrated callers: **85 tests, OK**
- U06 representation binding: **4 tests, OK**
- U05 staged support: **25 tests, OK**
- U02 layout observation: **8/8 PASS**
- blueprint render snapshots: **SUCCESS**
- U05 isolated browser-state replay: **SUCCESS**

Separate non-green truth remains:

- broader Motion2D product render still exits on its pre-existing two render gaps;
- informational broad platform suite remains 190 tests / 7 failures / 1 error / 1 skip.

These are not rewritten as ISS66 failures or PASS.

## U10A result

**U10A COMPLETE.**

What became reproducible:
- layout authority;
- review acceptance basis;
- support disclosure states;
- question/case representation binding;
- diagnostic confirmation boundary;
- compatibility behavior.

What remains explicitly unresolved:
- historical D-band / demand / hardest-target disagreements until fresh U04 evidence replay;
- accepted 4×7 coverage from these runs;
- #52 symmetric late-stage comparison;
- unrelated Motion2D product render gaps.

Parent U10 remains incomplete until the final handoff/result package is frozen.

Parent denominator remains:

- **P = 9/10 = 90%**
- **E = 9/10 = 90%**

Next bounded task:

**U10B — freeze the final branch/PR/result handoff, record exact authority and evidence frontiers, publish the scoped TASK_RESULT, and close #66 only if the responsibility-level acceptance criteria are satisfied without claiming golden/publication acceptance.**
