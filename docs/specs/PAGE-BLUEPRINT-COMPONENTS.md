# Page blueprint components

Generated from `Shared/web/interactive-page-blueprints.v1.json` by `Shared/tools/blueprint_spec.py`. Do not edit.
To change what a page shows, change the blueprint; the renderer, the quality gate and the owner-bank scaffold follow.

Registry 1.5.0. Levels: **REQUIRED**: The page is a gap while the component is absent or has fewer than min_items: the renderer records a typed gap that names the record to author, and the rendered-page gate fails the product. **EXPECTED**: A learner should see it. Its absence is an advisory that names the record field to author, never a silent omission, and never a reason to invent content. **OPTIONAL**: Shown when the record has it.

Depth: min_items is the floor below which a component does not count as present. target_items is the depth of the reference page, and target_items_by_band gives it by the difficulty band the record declares at band_source (for a Core1A construction unit, the hardest band among the bank questions it names in crux_question_refs). Between the floor and the reference depth the renderer says so as an advisory.

Waivers: A record may declare an EXPECTED component not applicable, with a written reason, in extensions['grade9v3:component_waivers'] as {COMPONENT_ID: reason}; the reason is kept in the page and the receipt. A REQUIRED component cannot be waived, and a page never waives anything itself.

Held to: FLOOR: official records and products are judged at the floor; an EXPECTED component that is absent is an advisory. REFERENCE: new authoring (a TEST deploy, a scaffolded owner bank) is judged at the reference depth, and an EXPECTED component must be present or waived by the record; otherwise it is a gap.

## BP-CORE2-SOURCE-QUESTION@1.4.0 (CORE2)

Learner job: Preserve authentic assessment demand while allowing bounded, provenance-explicit help that advances the learner without becoming a Question Clinic.

Theme: opens light, and the learner can switch.

Layout: from 980 px wide, the primary column is 42% and the support column 58%. Narrower, everything is one column, primary first.

| Slot | Column | Kept |
|---|---|---|
| `identity` | FULL | always |
| `attempt` | PRIMARY | always |
| `representation` | SUPPORT | when it has content |
| `support` | SUPPORT | when it has content |
| `solution` | FULL | always |

### Required components

Required: a page without it is a gap, and the quality gate fails it.

**IDENTITY** · slot `identity` · HEADER

- The learner gets: Say whose question this is and what kind of question it is before anything else.
- The reference page: selected_question_bank_TABLET_STUDY: question id, source line and badges in the header band
- Record fields: `id`, `original_identifier`, `extensions.grade9v3:source_custody`
- To author it: Identity comes from the question's custody. An owner-supplied question shows 'Owner-supplied question' and carries no exam, year or paper.

**STEM** · slot `attempt` · STEM

- The learner gets: The question exactly as set, under the label 'Attempt first'.
- The reference page: selected_question_bank_TABLET_STUDY: the left column's eyebrow and stem
- Record fields: `stem`

**ATTEMPT** · slot `attempt` · ATTEMPT

- The learner gets: Ask for a typed commitment before any answer or working opens.
- The reference page: selected_question_bank_TABLET_STUDY: the options cards; the commit step is this app's own attempt-first rule
- Record fields: `response`, `options`

**HINT_LADDER** · slot `support` · LADDER · at least 2 item(s); the reference has D1 3, D2 3, D3 5, D4 5 by difficulty band

- The learner gets: Let the learner ask for help one rung at a time; every rung says what it is for and whose words it carries.
- The reference page: selected_question_bank_TABLET_STUDY: 'Hint ladder · reveal only what you need', five rungs on a hard question (represent / first move, connect, crux, equation / formal model, assembly checkpoint) with SOURCE and EXPANSION pills
- Record fields: `scaffolds`, `hints`, `hint_ladder`
- To author it: Write scaffolds[], one rung per job, in the order a learner meets them: a D1 or D2 question needs 3 (REPRESENTATION, KEY_CONCEPT, CRUX), a D3 or D4 question 5 (then FORMAL_MODEL, which gives the relation to use, and CHECKPOINT, which gives an intermediate result to compare against). Each has text (the hint), prompt (a question that makes the learner do the step), support_kind (REPRESENT, CONNECT or EXECUTE), reveals (CONCEPT or METHOD; ANSWER is held back until the solution), learner_stage and supports_move_ref (the id of the move it prepares). A rung must teach something specific to this question and must not repeat another rung or state the answer. Delete the rungs the question's band does not need.

**SOLUTION** · slot `solution` · DISCLOSURE

- The learner gets: Open the full working only after an attempt.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Teacher solution · complete derivation' disclosure
- Record fields: `answer`

**SOLUTION_STEPS** · slot `solution`, inside SOLUTION · STEP_LIST · at least 2 item(s); the reference has D1 3, D2 3, D3 4, D4 4 by difficulty band

- The learner gets: Show the working as numbered moves: what is done, why it is valid, what it gives.
- The reference page: selected_question_bank_TABLET_STUDY: three or four numbered steps with a bold lead and the reason (geometry, balance, Newton II, eliminate)
- Record fields: `answer.reasoning_route`, `answer.crux_move_ref`
- To author it: Write answer.reasoning_route[]: 3 moves for a D1 or D2 question, 4 for a D3 or D4. Each move has id, kind (DECIDE, REPRESENT, CONNECT, TRANSFORM or VERIFY), action (what is done), why_valid (the physical or logical reason this step is allowed; not 'this follows from the model'), inputs and output. Set crux_move_ref to the id of the move a learner is most likely to miss. Delete the move the band does not need.

**ANSWER** · slot `solution`, inside SOLUTION · ANSWER_BOX

- The learner gets: State the final answer in one place.
- The reference page: selected_question_bank_TABLET_STUDY: the green answer box
- Record fields: `answer.summary`

### Expected components

Expected: an official page missing it carries an advisory naming the field to author; new authoring must supply it or waive it with a written reason, else it is a gap.

**DIFFICULTY_WHY** · slot `identity` · DISCLOSURE_GRID

- The learner gets: Show the difficulty band, its score and about how long the question should take, with the five reasons behind it folded away until asked.
- The reference page: selected_question_bank_TABLET_STUDY: the D-pill and the 'Why this difficulty?' grid
- Record fields: `extensions.grade9v3:analysis.difficulty`, `extensions.grade9v3:analysis.expected_time_seconds`
- To author it: Fill extensions['grade9v3:analysis'].difficulty: five components (each 0 to 2), score (their sum), band for that score, basis (one sentence); and expected_time_seconds, your estimate of the time a prepared learner needs. They are your estimates and are shown as estimates.

**CONDITIONS** · slot `attempt` · CALLOUT_INFO

- The learner gets: The givens and assumptions the question states, apart from the question itself.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Conditions.' callout under the options
- Record fields: `conditions`
- To author it: List each stated condition (a constraint or assumption the question gives) as one entry of conditions[]. Never list a method or a result there.

**TRAP** · slot `attempt` · CALLOUT_WARN

- The learner gets: Name the tempting wrong route so the learner can watch for it.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Common wrong route.' box
- Record fields: `extensions.grade9v3:analysis.common_wrong_route`
- To author it: One sentence naming the wrong route learners take and why it tempts. It must not give the answer or the right route.

**REPRESENTATION** · slot `representation` · VISUAL_CARD · at least 1 item(s)

- The learner gets: Show the situation as a picture drawn only from what the question states; every question in the benchmark has one.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Representation' card with the question-aligned schematic
- Record fields: `figure_refs`
- To author it: Add a representation to the package with an authored SVG (role=img, aria-labelledby or aria-label, <title> and <desc>) drawn only from the question's own data (labels at least 14 units high in a viewBox no wider than 440 units, so they read on a tablet), then name its id in figure_refs. Every question gets one; a classification or a pure-number question can show the quantities as a labelled diagram. If a question truly has nothing to draw, say so in extensions['grade9v3:component_waivers'] with the reason.

**CHECK** · slot `solution`, inside SOLUTION · CHECK_BOX

- The learner gets: Test the answer by a route the working did not use.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Check.' line under the answer
- Record fields: `answer.check`
- To author it: One sentence that tests the result independently: a limiting case, a unit check or a special value.

### Optional components

Optional: shown when the record has it.

**CONCEPT_NAV** · slot `support` · LINK_LIST

- The learner gets: Send the learner back to the concept page for the idea the question uses.
- The reference page: selected_question_bank_TABLET_STUDY: concept links beside the hints (the Core1A cross-link)
- Record fields: `primary_capability_ref`, `secondary_capability_refs`

## BP-CORE1A-CONSTRUCTION@1.4.0 (CORE1A)

Learner job: Reveal and explain the complete conceptual construction at intrinsic subtopic depth, then connect the concept to selected authentic questions that exercise its canonical capability.

Theme: opens dark, and the learner can switch.

Layout: from 1100 px wide, the primary column is 60% and the support column 40%; the support column stays in view while the primary column scrolls. Narrower, everything is one column, primary first.

| Slot | Column | Kept |
|---|---|---|
| `identity` | FULL | always |
| `construction` | PRIMARY | always |
| `representation` | SUPPORT | always |
| `repair_closure` | SUPPORT | always |

### Required components

Required: a page without it is a gap, and the quality gate fails it.

**CONCEPT_HEADER** · slot `identity` · CONCEPT_HEADER

- The learner gets: Name the concept and where it sits.
- The reference page: core1a-motion-in-a-plane-tablet: the concept header with title and metadata
- Record fields: `title`, `extensions.grade9v3:learner_metadata`

**UNIT_HEADER** · slot `construction`, once per construction unit · UNIT_HEADER

- The learner gets: Number and title each construction unit.
- The reference page: core1a-motion-in-a-plane-tablet: the concept-card header with number, decision and unit id
- Record fields: `construction_units[].decision`

**KEY_STEP** · slot `construction` · BANNER

- The learner gets: Name the one step learners cannot infer on their own.
- The reference page: core1a-motion-in-a-plane-tablet: the inferential-leap banner
- Record fields: `inferential_jump`
- To author it: inferential_jump: one or two sentences naming the step a learner does not make unaided and why it is not obvious.

**CONSTRUCTION_STEPS** · slot `construction`, once per construction unit · STEP_CARDS · at least 2 item(s); the reference has D1 3, D2 3, D3 4, D4 4 by difficulty band

- The learner gets: Build the idea in steps; every step says what is done, why it is valid and what state it gives.
- The reference page: core1a-motion-in-a-plane-tablet: step cards (action, why physically valid, state output)
- Record fields: `construction_units[].step_refs`, `teaching_path`
- To author it: Each construction unit lists step_refs naming 2 or more teaching_path steps; each step has action, why_valid and output written for this unit, none repeated from another unit. A unit that builds the crux of a D3 or D4 question (it names that question in crux_question_refs) needs 4 steps, and its last step is the move that question turns on.

**WORKED_EXAMPLE** · slot `construction`, once per construction unit · WORKED_CARD

- The learner gets: Walk one authentic question through the construction.
- The reference page: core1a-motion-in-a-plane-tablet: the worked card
- Record fields: `construction_units[].worked_anchor_ref`, `construction_units[].bank_anchor_ref`
- To author it: worked_anchor_ref names a question of the package that exercises exactly this unit's move. For the unit that builds toward a question of the product's bank (an owner-supplied question), set bank_anchor_ref to that question's id instead: the page then walks through the Owner's own question with its verified route, and nothing is copied into the package.

**STAGED_VISUAL** · slot `representation`, once per construction unit · STAGED_VISUAL · at least 2 item(s); the reference has D1 3, D2 3, D3 4, D4 4 by difficulty band

- The learner gets: Show the idea as a picture that builds up stage by stage, with controls to step through it.
- The reference page: core1a-motion-in-a-plane-tablet: the rail's staged visual with stage buttons
- Record fields: `construction_units[].representation_ref`
- To author it: representation_ref names a representation of the package with an authored SVG that has 2 or more groups marked data-g9-stage-id and reveal_stages naming them (3 stages is the reference, 4 for a unit that builds the crux of a D3 or D4 question). Draw each unit's own picture; do not reuse one figure on many units. Draw it in a viewBox no wider than 440 units with every label at least 14 units high, so the labels read on a tablet.

**TRAP_REPAIR** · slot `repair_closure`, once per construction unit · TRAP_CARD · at least 1 item(s)

- The learner gets: Show the mistake learners make here, how to notice it and how to repair it.
- The reference page: core1a-motion-in-a-plane-tablet: the easy-mistake card with diagnostic and repair
- Record fields: `misconceptions`, `construction_units[].misconception_indexes`
- To author it: misconceptions[] holds wrong_idea, diagnostic_prompt and repair for this concept; each construction unit names the ones that apply in misconception_indexes.

**QUICK_CHECK** · slot `repair_closure`, once per construction unit · TRIAD · at least 1 item(s) (the reference has 3)

- The learner gets: Let the learner test the idea three ways before moving on: recall it, use it on a small case, and say where it leads next.
- The reference page: core1a-motion-in-a-plane-tablet: the 1-2-3 quick check (CHECK, APPLY, CONNECT)
- Record fields: `construction_units[].independent_checks`
- To author it: Each construction unit lists three independent_checks, each with a role: CHECK (a question that recalls the idea), APPLY (a small case to work with numbers or a picture given in the question) and CONNECT (one sentence saying which idea this leads to next). Each statement is specific to the unit.

**EXIT_RECALL** · slot `repair_closure` · RECALL_CARD

- The learner gets: Ask for the idea back with less support, then show a model answer.
- The reference page: core1a-motion-in-a-plane-tablet: the active-recall attempt
- Record fields: `exit_task`

### Expected components

Expected: an official page missing it carries an advisory naming the field to author; new authoring must supply it or waive it with a written reason, else it is a gap.

**MODEL_CONTRACT** · slot `construction` · TILE

- The learner gets: Say what the learner must already hold and what model is assumed.
- The reference page: core1a-motion-in-a-plane-tablet: the 'Model contract & assumptions' tile
- Record fields: `entry_assumptions`, `prerequisite_refs`
- To author it: List in entry_assumptions[] each thing a learner must already be able to do before this concept, one per entry and specific to this concept.

**EQUATIONS** · slot `construction`, once per construction unit · EQUATION_CARD

- The learner gets: Put the relations a unit uses beside their meaning and when they hold.
- The reference page: core1a-motion-in-a-plane-tablet: the equation card of every concept card (definition and validity scope)
- Record fields: `construction_units[].relation_refs`, `relation_refs`
- To author it: Each construction unit names the microtopic's relations it uses in construction_units[].relation_refs; each relation record needs its expression, meaning and conditions. A subject that declares no gates writes gate_relation_ref: null.

### Optional components

Optional: shown when the record has it.

**SECTION_ROUTE** · slot `identity` · CHIPS

- The learner gets: Let the learner jump to a construction step.
- The reference page: core1a-motion-in-a-plane-tablet: the section tabs

**QUESTION_BRIDGE** · slot `construction`, once per construction unit · CALLOUT_INFO

- The learner gets: Say which source question this unit builds toward and the move a learner most often misses in it, so the concept is taught for that question and not only named after it.
- The reference page: core1a-motion-in-a-plane-tablet: each concept card is built around the inferential leap the practice questions need
- Record fields: `construction_units[].crux_question_refs`, `construction_units[].crux_step_ref`, `answer.crux_move_ref`
- To author it: Write crux_question_refs on a construction unit: the ids of the bank questions whose crux the unit builds, and crux_step_ref: the one of its step_refs that builds the move those questions turn on (the page marks that step). The toughest question of the set (the deploy names it) must be named by a unit of the concept it belongs to; that unit's steps must lead to the move the question turns on, and its worked example is that question (bank_anchor_ref). A unit that only shares the question's topic does not build its crux, and a step that mentions the idea in passing is not the step that builds it: draw the whole idea (for a sum of two vectors, every angle and not only the right angle).

**PRACTICE_LINKS** · slot `repair_closure` · CHIPS

- The learner gets: Point to the authentic questions that practise this concept.
- The reference page: core1a-motion-in-a-plane-tablet: the practice chips
- Record fields: `practice`
