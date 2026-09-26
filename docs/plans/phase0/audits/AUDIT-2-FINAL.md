# Audit 2 (final): process root causes of the Audit 1 defects

Issue: https://github.com/reallaksh19/Grade9V3/issues/297.

Every chain below starts from an Audit 1 finding (AUDIT-1-FINAL.md) and points to files at
branch `motion2d-six-core-20260926`, commit `d3fd51ab`:
- the generator `Physics/tools/build_motion2d_projectile_product.py` (565 lines, "gen" below);
- the duty register `Physics/content/motion-2d-projectile-demand/duty-register.v1.json`;
- the validation report `…/validation-report.v1.json`;
- the workflow `.github/workflows/motion2d-projectile-product.yml`.

This is the audit record; nothing was changed.

## Pipeline facts every chain relies on

1. **Duties are about outputs, not learner blocks.** The register has 7 duties (D1–D7), all
   `COMPLETED`: source identity, extension teaching, source acquisition, practice authoring,
   default learner, prior-exposure sequencing and review label.
   - None names a learner-facing block such as "mount canonical representation", "progressive
     hint ladder", "prerequisite bridge" or "safe initial representation".
   - "Complete" meant that the output artifact existed.
2. **A hand-written generator bypassed the renderer that already implements the blueprints.**
   - `Shared/workbench/core-learning-page.mjs:1064` emits `data-blueprint-slot` sections for
     every role blueprint and is tested (`tests/core_learning_page.test.mjs:504`).
   - It gates the solution behind a button (`data-action="solution"`) and renders hint and
     support slots.
   - gen writes each page as f-strings.
   - It emits `data-blueprint-ref` on `<body>` and **no slot markers** (Audit 3: 0 slots on
     all six pages).
   - The blueprint renderer is not complete either. It has no code for the named blocks
     `governing_relations`, `compact_anchor`, `exposure_family_closure`,
     `lineage_continuity_check` or `safe_initial_representation` (0 matches each). So invoking
     it would have fixed the slot structure and the reveal gating, not the missing blocks.
3. **Validation checked declarations, not the rendered experience.** The report claims
   `STRUCTURALLY_VALIDATED` from 10 checks and 19 "direct invariant" assertions. Examples:
   - `attempt_before_reveal: PASS`, with evidence "Core1B and Core2B use commit controls";
     Core2 was not examined.
   - `visual_binding: PASS`, with evidence "reuse shared-clock/event/projectile visual
     language".
   - `six_core_blueprint_identity`, which checks the attribute only.

   No check opens a rendered page, counts figures per concept, or finds placeholder text.
4. **The one executable control that could have run did not.** The report records
   `ci_observation.state = JOBS_TERMINATED_BEFORE_STEPS`; the unit-test suite never ran in CI.
   The newer `delivery_gate.py` (#290) and `web_blueprint_contract.py` were not in the
   product's command list for the rendered pages. `web_blueprint_contract.py` also checks only
   the registry and role mapping, not the DOM.
5. **The reference encoded quantity, not depth.**
   - `benchmarks/learner-product-reference/physics-motion-2d.json` counts items.
   - The owner references (textbook grammar and the H0–H4 question grammar) were never
     machine-encoded before Phase 0.

## Root-cause chains: every S1 finding

Chain form: learner defect → required duty → governing contract → intake/plan → agent context →
authored object → projection/render → validation → **failure point**.

### A1-002: canonical R1–R3 show representation ids instead of figures
- **Duty required:** mount the canonical representation in Core1A `representation_bridge`.
  No such duty exists (D2 is "author extension teaching").
- **Contract:** Core1A ordered blocks (`LEARNER-PRODUCT-TEMPLATES.md`); blueprint slot
  `construction.representation_bridge`.
- **Intake:** canonical records already bind `REP-KIN-2D-SHARED-CLOCK`, `-EVENT-CLOCK` and
  `-PROJECTILE-MODEL`, so the need was detectable.
- **Authored object:** the representation ids exist, but there is no figure asset for them.
- **Render:** gen line 223 falls back to
  `Canonical representation: <code>{ref}</code>; use the linked canonical explorer`.
- **Validation:** `visual_binding` passes on "visual language";
  `five_extension_visuals_rendered…` counts only extension figures.
- **Failure point:** RENDERER_FAILURE (a text fallback instead of a hard failure) on top of a
  DUTY_DEFINITION_FAILURE, missed by a VALIDATION_BLIND_SPOT.
- **Blast radius:** pipeline-wide. Any renderer with a fallback string does this for any
  subject.
- **Counterfactual:** a rendered gate that fails when an admitted concept's
  `representation_bridge` has no figure, and no text fallback in the renderer, would have
  stopped A1-002 at render time.

### A1-004: R3 compresses about 8 hard transitions into one construction
- **Duty required:** one construction unit per distinct learner decision, each with a worked
  anchor. No duty or contract field expresses "per decision"; Core1A accepts one
  `completed_construction` per concept.
- **Agent context:** the prompt defined completeness as "all 8 concepts present".
  `core1a_core1b_identical_eight_concept_coverage` then confirmed exactly that.
- **Authored object:** one microtopic record for the projectile model, whose single
  `worked_conceptual_anchor` states `a_x=0, a_y=-g`.
- **Failure point:** DUTY_DEFINITION_FAILURE plus a data-model limit (one anchor per concept),
  then AUTHORING_DEPTH_FAILURE and a BENCHMARK_BLIND_SPOT (the textbook's staged-construction
  grammar was not encoded).
- **Blast radius:** subject-wide. Every rich topic collapses into one article.
- **Counterfactual:** a contract rule "each hard transition in the concept's map has its own
  construction and anchor", checked against the rendered page, blocks A1-004.

### A1-005: no prerequisite bridge for the extensions
- **Duty required:** TEACH_PREREQUISITE_BRIDGE. It does not exist in
  `research-first.v1.json` or in the register.
- **Intake:** the extension records carry `assumed_prerequisite`, so the gap was detected as
  data.
- **Planning:** the planner turned it into nothing. gen lines 423/453 copy it into a
  `prerequisites` list in the trace.
- **Validation:** no check links a prerequisite to a teaching unit.
- **Failure point:** INTAKE detected the gap; DUTY_DEFINITION_FAILURE left it unconverted.
- **Blast radius:** subject-wide and cross-subject (any extension beyond grade).
- **Counterfactual:** a duty rule "every assumed prerequisite outside the learner's default
  grade either maps to an existing teaching unit or creates a bridge unit" blocks A1-005 at
  planning.

### A1-006: Core2 answers visible immediately
- **Duty required:** reveal the source answer on attempt (`source_answer_rubric: ON_REVEAL`).
- **Contract:** the Core2 template withholds `SOURCE_ANSWER` pre-attempt; the blueprint's
  `solution` slot is `LEARNER_OPENABLE`.
- **Render:** gen line 202 writes `Source-answer custody` and the full reasoning inline after
  the stem, with no `<details>`.
- **Validation:** the `attempt_before_reveal` check was scoped to Core1B and Core2B only.
- **Failure point:** RENDERER_FAILURE, missed by a VALIDATION_BLIND_SPOT (partial scope).
  CONTROL_EXISTS_NOT_INVOKED: `core-learning-page.mjs` renders the Core2 solution slot behind a
  disclosure.
- **Blast radius:** role-wide. Every Core2 from this generator.
- **Counterfactual:** rendering through the blueprint renderer, or a gate applying
  `withheld_pre_attempt` to every Core, blocks A1-006.

### A1-007: Core2A has no figures
- **Duty required:** question-aligned `initial_representation` and `bound_representation`.
- **Authored object:** each twin's reasoning route names a `representation_ref` and
  `visual_stage_ref`, but `figure_refs: []`, and the package schema allows the empty list.
- **Render:** gen's Core2A path (lines 283–310) has no figure output at all.
- **Validation:** no figure count per question.
- **Failure point:** AUTHORING_DEPTH_FAILURE (the figure was never made), allowed by the data
  model, then RENDERER_FAILURE (no slot), then VALIDATION_BLIND_SPOT.
- **Blast radius:** role-wide.
- **Counterfactual:** a schema rule "a question whose route binds a representation must carry
  a figure" blocks A1-007 at authoring.

### A1-008: one generic scaffold and failure signal for all 5 families
- **Duty required:** progressive, family-specific support (blueprint
  `progressive_support: true`; reference grammar H0–H4).
- **Authored object:** each twin has exactly one scaffold with identical text.
- **Render:** gen line 309 **hard-codes** the failure signal ("your route selects an equation
  before naming the model…"), so no authored per-family signal could have appeared.
- **Validation:** `core2a_reasoning_crux_check_repair_complete` checks that the fields exist.
- **Failure point:** RENDERER_FAILURE (hard-coded learner text) plus AUTHORING_DEPTH_FAILURE,
  with no duty or contract minimum on support levels (DUTY_DEFINITION_FAILURE).
- **Blast radius:** pipeline-wide (a generator writing academic text is forbidden by blueprint
  `PAGE_LOCAL_ACADEMIC_TRUTH`).
- **Counterfactual:** a gate forbidding learner text not traceable to a record, plus a
  contract minimum of ordered support levels per question, blocks A1-008.

### A1-010: Core2B has no safe initial representation
- **Duty required:** `safe_initial_representation` (IMMEDIATE). The authored object has a
  single figure that shows the protected move; no safe variant exists.
- **Render:** gen lines 332–340 place that figure inside the post-attempt disclosure. That is
  correct for the leaking figure, but no safe figure was ever required.
- **Validation:** `core2b_commit_before_changed_demand_and_protected_move` checks order only.
- **Failure point:** DUTY_DEFINITION_FAILURE (no "safe figure" object in the data model), then
  AUTHORING_DEPTH_FAILURE.
- **Blast radius:** role-wide.
- **Counterfactual:** a data model with two representation roles per transfer question
  (safe/pre-attempt and full/post-attempt), and a gate requiring the first, blocks A1-010.

## S2 findings, grouped by cause

| Cause | Findings | Class |
|---|---|---|
| Renderer prints a placeholder instead of failing (gen line 75 `None supplied by the governed record`) | A1-003, A1-012 | RENDERER_FAILURE + VALIDATION_BLIND_SPOT |
| A registered block has no renderer path in gen **or** in the blueprint renderer | A1-001 (`governing_relations`, `compact_anchor`), A1-009 (`exposure_family_closure`), A1-011 (`lineage_continuity_check`) | RENDERER_FAILURE; a missing control, not merely an unused one: the contract registers blocks that no renderer implements, and `core_template_contract.py` checks the registry, not renderer coverage |

## One-off errors and systemic failures

- **One-off authoring errors:** none of the 12 findings is an isolated slip. Each traces to a
  missing duty, a data-model gap, a generator shortcut or a validation blind spot, so each
  would recur on the next topic.
- **Existing controls not invoked:**
  - `core-learning-page.mjs` (slot structure, solution gating, hints; not the named blocks);
  - the unit-test suite in CI (jobs terminated before steps);
  - `delivery_gate.py` (not in the product's command list).
- **Missing controls:**
  - a rendered-page gate;
  - duties for representation mounting, prerequisite bridges, progressive support and safe
    representations;
  - a data model with per-decision constructions and per-role figures;
  - a "no placeholder, no generator-authored learner text" rule;
  - a machine-encoded reference grammar.

## Prioritized control-gap matrix

| Priority | Control gap | Kind | Findings blocked | Where it lands in the plan |
|---|---|---|---|---|
| 1 | One renderer for every Core that implements **every registered block** of every blueprint slot, checked by a registry-to-renderer coverage test; retire per-topic generators | partly exists, not invoked (slots and gating); partly missing (named blocks) | 001, 002, 003, 006, 008, 009, 011, 012 | Phase 3 (`render_core.py` on the blueprint engine; gen is RETIRE in the renderer inventory) |
| 2 | Rendered gate over the actual pages: figures per concept and question, withheld-before-attempt on every Core, no placeholder text, slot presence, progressive support | missing | all 12 | Phase 4 |
| 3 | Data model: per-decision constructions; per-role figures (safe/full, initial/bound); ordered support levels; `figure_refs` required when a route binds a representation | missing | 004, 007, 008, 010 | Phase 2 |
| 4 | Duties for learner blocks: MOUNT_REPRESENTATION, TEACH_PREREQUISITE_BRIDGE, AUTHOR_SUPPORT_LADDER, AUTHOR_SAFE_REPRESENTATION, each naming the contract rule it satisfies | missing | 002, 005, 007, 008, 010 | Phase 5 |
| 5 | Quality contract with the reference grammar and depth rules, calibrated on the corpus | missing (benchmark blind spot) | 004, 005, 008 | Phase 1 |
| 6 | Independent verification and tool-written reports, replacing self-attested `STRUCTURALLY_VALIDATED` | missing | all (detection) | Phase 4 |
| 7 | CI that actually runs, or a local pre-push gate while Actions is unavailable | exists, not invoked | detection of all | Phase 4 |
