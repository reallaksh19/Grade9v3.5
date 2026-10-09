# Repository-wide six-Core + continuous QRT integration

**Coordination:** [#313](https://github.com/reallaksh19/Grade9v3.5/issues/313) (child of [#29](https://github.com/reallaksh19/Grade9v3.5/issues/29)).  
**Status:** integration-readiness inventory and dependency plan; **not** completion, academic admission, signed accessibility acceptance, merger or learner release.  
**Role authority:** `Shared/roles/README.md` and `Shared/roles/CORE-AUTHORITY-CONTRACT.md`. **QRT authority:** `docs/method/QUESTION-REVIEW-MATRIX.md`. This page does **not** create a new educational schema, duplicate the canonical facts, override the six role contracts or assign accepted status to any question.

## QRT 24/7 means continuous application, not a new matrix

The governed QRT is **7 demands × 4 derived D-bands = 28 base cells**, not 24×7 templates. Each eligible question selects one base cell from its canonical primary demand and five-component difficulty derivation, then resolves learner-specific **X/Y/Z/W** and undergoes **H1–3 / S1–3 / P1–3 / M1–3** semantic judgement against the exact post-render artifact.

There are **four different layers**: authored QRT intent, author self-audit of each hint/solution/calculation, independent 12-ask review bound to rendered hashes, and web/PDF/keyboard/quality regression. A valid matrix projection or synthetic browser pass cannot substitute for an independent semantic review. `NO` and `PARTLY` are fix orders, not another numeric score. Pre-attempt **W protection is transitive** across figures, hints, navigation, help and linked interactives. If a changed render has new bytes, prior rendered review is stale.

**Operational meaning of 'always on':** Relevant new/changed canonical questions, their scaffolds, solutions, representations, renderer/print pipeline or learner profile must trigger the appropriate existing precheck, QRT resolver, artifact build and exact-render review/delta. CI can ensure mechanical steps ran and fail on stale/missing evidence; human semantic review remains its own explicit gate. Do not require all unrelated PRs to re-review unchanged questions, or disguise historic red `main` checks as new Core regressions.

## Real six-Core lineage, not six symmetric empty pages

| Core role | Distinct learner work and owner | Integration edge / gating evidence |
| --- | --- | --- |
| **Core1** | Orientation from canonical conceptual truth | Maps the **same canonical concept and intrinsic difficulty** used by Core1A/B, without pretending to teach it |
| **Core1A** | Full worked construction of `microtopic.inferential_jump` | Exposes the warranted conceptual bridge, its source/representation boundaries and independently checkable exit |
| **Core1B** | Learner predicts, commits, reconstructs, diagnoses, repairs, tests a boundary | Identical canonical microtopic coverage to Core1A; different learner action and timing; closed feedback and genuine boundary test |
| **Core2** | Authentic source question, custody, protected learner attempt | Original stem/conditions/figure/key/rights traceable; authored practice **may not fill this role** |
| **Core2A** | Familiar supported application with full reasoning | Structured route/crux, valid independent check, authored versus source-backed identity visible; exact Core1 repair concept |
| **Core2B** | Genuine transfer through a newly required decision | Established **prior** Core1A/B/2A capability, pairwise `transfer.dimension`, `DECIDE` protected ref, safe support, specific repair + rubric |

Both progression chains must join **bidirectionally**: Core2 attempts lead to the *specific* Core1A/B construction and back to the originating item; Core2A establishes familiar exposure before Core2B; failed transfer returns to the appropriate construction. A renderer's six valid files or a concept label shared across pages does **not** prove these edges.

## Inventory snapshot versus acceptance

The governing live-audit entrypoints are `Shared/library/core1_progression.py`, `core1b_reconstruction.py`, `core_progression.py`, `Shared/tools/core2a_inventory.py`, `core2b_inventory.py` and `question_review_matrix.py`. Run `python Shared/tools/repo_core_readiness.py` for a **read-only snapshot of the current checkout**, not manually copied acceptance flags.

At historical main `bc1af3e7`, committed reports indicated:
- **Core1:** 21 buckets, 91 canonical microtopics, 90 coherent across Core1/A/B, 1 **unrouted Relative Motion** concept; 89 separate Phase-2 Core1A local construction-debt microtopics. Reported Core1B parity is structural, not a proof of student understanding.
- **Core2:** 25 practice families, 3 with separate competitive-bank demand evidence, **zero ordinary Core2 custody anchors**, 84 Core2A items (20 structured), 47 Core2B items (30 protected-move structured), eight cross-progression findings.
- **Core2B historical migration:** 32 legacy baseline debt rows, overlapping the inventory counts; debt is protected by forward-migration guardrails, not automatically accepted.
- **QRT:** 28 generated templates; **the number of independently accepted template cells and exact-render question reviews is not inferred from the template count**.

These are not promises of current values. The read-only tool recomputes the inventories from the checkout. Independent acceptance must be cited from an external, exact-artifact review record or remain `NOT_REVIEWED`.

## Milestones and strict dependencies

| Milestone | Responsible stream | Concrete exit | Not allowed to infer |
| --- | --- | --- | --- |
| **I0 — Live denominators** | #313 integrator | Recompute all inventory counts and findings, link exact checkout SHA and CI state; separate **MISSING**, **MIGRATION_DEBT**, **NOT_REVIEWED** and **NOT_APPLICABLE** | Rendered counts are readiness |
| **I1 — QRT always-on** | Existing QRT pipeline + #313 integration | Resolved demand/band + scoped X/Y/Z/W; individual item audits; 12 independent exact-byte reviews and fail/rework on changed bytes | Every valid QRT template has accepted learner content |
| **I2 — Core1 continuity** | Core1 progression/academic | Resolve unrouted microtopic without erasing 89 local construction debts; Core1A/B full coverage and different student agency; browser/PDF plus human review status | A/B text similarity or unit parity measures learning |
| **I3 — Core2 source eligibility** | IMO #294 / NCERT #68 | Inspected origin + question/figure/key/rights; authentic Core2 only when eligible | Authored TEST practice is official Core2 |
| **I4 — Core2A family** | Existing Core2A inventory | Migrate real reasoning/crux/check for selected familiar applications; link exact prior teaching | A complete worked answer proves mastery |
| **I5 — Core2B changed demand** | Existing transfer inventory | One pairwise reviewed transfer with new protected DECIDE, established capability, concrete family/parent/repair and postattempt rubric; regress W across links | Cosmetic numeric/context variants are transfer |
| **I6 — Whole learner path** | #313 integrator + Owner | True six-role product and navigable attempt→repair→retry→changed-demand journey, printed learner/key distinction, human a11y/Grade 9 observations or explicit NOT_RUN, Owner disposition | TEST/CI == curriculum/publication acceptance |

**Priority:** I0/I1 are cross-cutting; I2 repairs the concept chain; I4 provides familiar application; I5 only after established exposure; I3 source research proceeds solely through already authorized channels, never coerced to meet a 6/6 target. I6 waits for an actual custody-eligible Core2. If source rights are missing, show a truthful **5-role authored learning path + blocked Core2** instead of a fake six-role success.

## Active slices and non-grants

- [Merged #310](https://github.com/reallaksh19/Grade9v3.5/pull/310) verifies **Core1A → authored Core2A** in TEST, not whole-repo teaching/review admission.
- [Draft #311](https://github.com/reallaksh19/Grade9v3.5/pull/311) adds same-concept **Core1B** self-check and separate answer-key qualification. It stays a dependency under academic/print/accessibility review, **not** the six-Core integration PR.
- [IMO #294](https://github.com/reallaksh19/Grade9v3.5/issues/294) owns the single authorized original/author-created source line, custody and research questions. [NCERT #68](https://github.com/reallaksh19/Grade9v3.5/issues/68) remains independently parked. [IMO research owner-policy #264](https://github.com/reallaksh19/Grade9v3.5/issues/264) concerns the research human-signoff waiver; it does not by itself approve learner release or all Core teaching.
- `docs/CORE2B-TRANSFER-MIGRATION.md` owns forward transfer migration, not this page; `docs/CORE1-PROGRESSION-INTEGRITY.md` owns Core1/A/B lineage. The integrator calls both; it does not replace them.

## Evidence discipline

Each future acceptance row needs **record ID, selected role, exact content/HTML/PDF digest, QRT cell and 12 judgements when applicable, concept/capability and transfer lineage, reviewer decision, source/rights status, observed child/assistive-tech result or NOT_RUN, and owner release disposition**. Every row may remain PENDING. No row may be auto-marked as academically accepted because tests pass.

This integrated ledger is an **implementation plan**, not a permission to modify QRT 28-cell definitions, accept source questions, bypass W or merge #311.
