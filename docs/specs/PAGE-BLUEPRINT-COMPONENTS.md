# Page blueprint components

Generated from `Shared/web/interactive-page-blueprints.v1.json` by `Shared/tools/blueprint_spec.py`. Do not edit.
To change what a page shows, change the blueprint; the renderer, the quality gate and the owner-bank scaffold follow.

Registry 1.16.0. Levels: **REQUIRED**: The page is a gap while the component is absent or has fewer than min_items: the renderer records a typed gap that names the record to author, and the rendered-page gate fails the product. **EXPECTED**: A learner should see it. Its absence is an advisory that names the record field to author, never a silent omission, and never a reason to invent content. **OPTIONAL**: Shown when the record has it.

Depth: min_items is the floor below which a component does not count as present. target_items is the depth of the reference page, and target_items_by_band gives it by the difficulty band the record declares at band_source (for a Core1A construction unit, the hardest band among the bank questions it names in crux_question_refs). Between the floor and the reference depth the renderer says so as an advisory.

Waivers: A record may declare an EXPECTED component not applicable, with a written reason, in extensions['grade9v3:component_waivers'] as {COMPONENT_ID: reason}; the reason is kept in the page and the receipt. A REQUIRED component cannot be waived, and a page never waives anything itself.

Held to: FLOOR: official records and products are judged at the floor; an EXPECTED component that is absent is an advisory. REFERENCE: new authoring (a TEST deploy, a scaffolded owner bank) is judged at the reference depth, and an EXPECTED component must be present or waived by the record; otherwise it is a gap.

## The shell (every page)

`G9-TABLET-SHELL-V1` 1.3.0: a fixed header with `BACK`, `HOME`, `SUBJECT_CONTEXT`, `QUESTION_BANK`, `PRINT_PDF`, `SEARCH`, `REFRESH`, `DISPLAY`, `OVERFLOW`.

**PRINT_PDF** · the PDF icon in the header. A learner or a teacher can print the page: a PDF icon in the fixed header opens the PDF printed from this very page, ready for the print dialog of the tablet.

- Pages: CORE1, CORE1A, CORE1B, CORE2, CORE2A, CORE2B, in PAGES mode; a single-file page has no control (no file beside it).
- It opens (in a new tab): the PDF printed from this very page, `{page_stem}.pdf`; its accessible name is "Open the PDF of this page to print it".
- It is a touch target of at least 48 px and is hidden when the page is printed.
- It never links: KEY_PDF (a key PDF holds the answers).
- A page that links its PDF is published only with that PDF beside it, printed from the same bytes (print-receipt.json); a link that does not resolve refuses the publication.
- A Core2 question whose source is a verified official past paper also links the paper itself as a PDF: see the `SOURCE_PDF` component.

## Pages that do not come through the renderer

A learner page that did not come through render_core (a snapshot, a suite, a page written by hand or taken from another tool) meets the shell's own policies, read from its own bytes. The renderer meets them by construction; nothing else does unless something checks.

Governed roots: `standalone/`. A page there that is not listed in the ledger has no findings; an unknown page fails closed. Checker: `Shared/tools/standalone_conformance.py`; zoom is never limited below 5x.

| Rule | Held | Assurance type | Executes | What it asks |
|---|---|---|---|---|
| `REMOTE_RUNTIME` | blocks | `NETWORK_POLICY` | `vendor_policy.pages_external_runtime` | A page loads no script, stylesheet, font, image or frame from the network. A link to a source is a citation and is allowed; a dependency is not. |
| `VIEWPORT_ZOOM` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `responsive_modes` | A page declares a viewport and never turns zoom off: no user-scalable=no, no maximum-scale under the limit. |
| `FONT_FLOOR` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `typography_policy.minimum_learner_text_css_px` | No declared text size is under the learner text floor. A size that scaling changes (an SVG label in a narrow column) is measured by the browser audit. |
| `LINKS_RESOLVE` | blocks | `LINK_INTEGRITY` | `responsive_modes` | Every relative reference lands on a file that exists, and every fragment on an id that page holds. |
| `LINKS_LEAVE_ROOT` | said | `LINK_INTEGRITY` | `vendor_policy.pages_external_runtime` | A reference that leaves the governed root means the page is not whole where it is shipped alone. Said, not held: whether it matters depends on what is shipped. |
| `MATH_CONTROL_CHARS` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `math_policy` | No control character in the source: a TeX escape read as one (\v for \vec, \f for \frac) is gone from the maths. |
| `MATH_UNRENDERED` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `math_policy.dynamic_renderer` | TeX in the visible text means a script on the page renders it; maths shown as raw delimiters is not maths. |
| `STORAGE_GUARDED` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `representation_accessibility_policy` | Storage is read only inside a try block: with storage blocked the read throws, and one throw ends the script. |
| `VENDOR_CONFIG_DANGLING` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `vendor_policy.unknown_runtime_dependency` | No configuration for a vendor script the page does not load: it throws on every load. |
| `UNIQUE_IDS` | blocks | `PROJECTION_STATIC_CONFORMANCE` | `representation_accessibility_policy` | An id appears once on a page. |

Ledger (`Shared/web/standalone-ledger.v1.json`): A page may have no more findings of a rule than the ledger records, and a page the ledger does not list has none. The ledger holds what was already there when the rule arrived; the checker writes it, and it can only be tightened.

Browser audit (`tools/site-audit/core-page-audit.mjs --profile tablet-12.7`): measures horizontal overflow, touch targets of at least 48 px, rendered text size, SVG labels included, return navigation. These need a rendered page. A snapshot is not done until this audit has run on it; the static rules above are what a pull request can be held to without a browser.

## Rules about a whole product

**Coverage** (component `COVERAGE`, duty `AUTHOR_COVERAGE`). A product shows what the library holds for its subject, not what an author happened to list: the list of selected questions is a choice, and a choice leaves a record.

- The denominator: What product_manifest.derive would select: for Core2, the exam-bank questions whose capability or concept bucket belongs to the package; for Core2A and Core2B, the package questions exposed to that Core.
- The rule: Every record of the denominator is selected, or omitted by the manifest with a reason (coverage.omitted: {record id: why}); the hardest question of the denominator, by the toughest-concept rule, is selected.
- A shortfall is an advisory for an official product (held to the floor) and a gap for new authoring (held to the reference).
- Source documents whose questions the library does not hold as records yet are declared in the manifest (coverage.sources: source, kind, questions, ingested, status). They are counted and said on the page of Deployments and in the receipt; nothing is rendered from them, and the figures are the author's claim.

**Promotion.** A record that its own status says is not ready to teach is not selected into a product.

- Selectable statuses: CANDIDATE, REVIEWED, CURATED. Refused: DISCOVERED, DISPUTED, STALE, RETIRED, with `PRODUCT_SELECTION_STATUS_NOT_SELECTABLE`; it applies to microtopics, core2, core2a, core2b.
- A record that declares no status makes no claim and is not refused. What a selected record must contain is the blueprint's own components: a REQUIRED one that is absent is a gap, as before.

**Typeset** (component `TYPESET`, duty `AUTHOR_TYPESET`). An equation a learner is meant to read is typeset, not left as the author's plain text.

- A relation shown on a page carries presentation MathML (relation.mathml, the restricted subset the renderer accepts). One that has only an expression is shown as plain text, and the build says so.
- It is an advisory for an official product and a gap for new authoring.

## Rules about a record and its evidence

**Admission.** A question record is admitted by the library's own intake and resolver. A registration does not bring a gate of its own: a gate that checks that fields are non-empty cannot see a record that says nothing. Authority: `Shared/library/intake.py`, `Shared/library/resolve.py`, `Shared/library/question_admission.py`.

- `QUESTION_STEM` (blocks; evidence of type `STRUCTURAL_VALIDITY`): The stem asks something: it has at least 6 words and is not made of sentences that the record's own hints or solution also say.
- `QUESTION_STEM_COMPLETE` (said; evidence of type `STRUCTURAL_VALIDITY`): The stem ends where a sentence ends; a stem cut off mid-sentence asks half a question. Said, not held: a stem that ends on a variable looks the same from the text.
- `QUESTION_OPTIONS` (blocks; evidence of type `STRUCTURAL_VALIDITY`): An option carries text. A letter standing for itself ('(A) A') is a choice with nothing to choose.
- `QUESTION_GIVENS` (said; evidence of type `DISCLOSURE_CONFORMANCE`): A number a hint relies on is in the stem, the options or the conditions, so a learner who has not opened the hint can already start. Said, not held: a constant or a value worked out from the stem looks the same from the text.
- `QUESTION_SCOPE` (blocks; evidence of type `SCOPE_CONFORMANCE`): The question does not teach a concept the scope document defers (read from Shared/policy/grade9-physics.v1.json; an entry that names a row of the scope document is held to it by a test), unless the record is routed as a declared extension. A concept only the policy defers is said, not held, until the document names it. A question that excludes the concept ('do not invent a torque equation') is not refused. The capability tag is not the test: the registrar writes it.
- `ANSWER_ANCHORED` (blocks; evidence of type `CORPUS_SPECIFICITY`): The answer is about this question: it shares at least 2 words or numbers with the stem, options and conditions. No list of banned phrases is kept; an answer that could stand under any question fails without one.
- `ANSWER_WORKED` (blocks; evidence of type `CORPUS_SPECIFICITY`): The answer is worked: at least 2 reasoning steps and 80 characters of reasoning, and a summary of at most 500 characters that states the result; a page pasted in as the summary is not a result.
- `ANSWER_VERIFIED` (blocks; evidence of type `REASONING_VALIDITY`): A key that nobody ran (NOT_RUN), or that someone disputes, does not enter a library. The status is the author's word, so it is a floor and not a proof.
- Intake and the resolver stay the one gate of record: CI runs them over every committed library (tests/test_question_admission.py), and a registration does not bring a gate of its own. These sit beside the corpus checks that were already there (duplicated and templated text, unresolved references). A package intake refuses is not registered, whatever else is said about it. What none of this can do is tell a plausible wrong explanation from a right one; a numeric key computed from the stem's own givens by an oracle would. Each point and each page rule names the assurance type its evidence is of; a check that proves part of a type (a static page rule cannot prove a layout) feeds a type of its own and leaves the whole type open.

**Evidence.** A digest is taken over the bytes of a file, so the bytes must be the same on every machine. Line endings: LF (`.gitattributes`). Text is LF in every working tree (`* text=auto eol=lf`). A file already committed with CRLF keeps its bytes, so no recorded digest moves; a new file is LF.

## BP-CORE2-SOURCE-QUESTION@1.10.0 (CORE2)

Learner job: Preserve the authentic source-question decision and an observable learner commitment before any assistance that completes or materially narrows protected work. Safe orientation may be available before commitment; learner-requested and post-attempt support remain provenance-explicit and state-bound; diagnosis and full solution remain distinct.

Theme: opens light, and the learner can switch.

Layout: from 980 px wide, the primary column is 42% and the support column 57.99999999999999%. Narrower, everything is one column, primary first.

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
- To author it: Identity comes from the question's custody. An owner-supplied question shows 'Owner-supplied question' and carries no exam, year or paper. Question-bound grade9v3:attempt_labels may supply neutral concept/family labels where titles settle the assessed act. Preserve canonical refs and show detailed titles only in the protected solution.

**STEM** · slot `attempt` · STEM

- The learner gets: The question exactly as set, under the label 'Attempt first'.
- The reference page: selected_question_bank_TABLET_STUDY: the left column's eyebrow and stem
- Record fields: `stem`

**ATTEMPT** · slot `attempt` · ATTEMPT

- The learner gets: Ask for a typed commitment before any answer or working opens.
- The reference page: selected_question_bank_TABLET_STUDY: the options cards; the commit step is this app's own attempt-first rule
- Record fields: `response`, `options`

**SOLUTION** · slot `solution` · DISCLOSURE

- The learner gets: Open the full working only after an attempt.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Teacher solution · complete derivation' disclosure
- Record fields: `answer`

**SOLUTION_STEPS** · slot `solution`, inside SOLUTION · STEP_LIST · at least 2 item(s); the reference has D1 3, D2 3, D3 4, D4 4 by difficulty band

- The learner gets: Show the working as numbered moves: what is done, why it is valid, what it gives.
- The reference page: selected_question_bank_TABLET_STUDY: three or four numbered steps with a bold lead and the reason (geometry, balance, Newton II, eliminate)
- Record fields: `answer.reasoning_route`, `answer.crux_move_ref`
- To author it: Write answer.reasoning_route[]: 3 moves for a D1 or D2 question, 4 for a D3 or D4. Each move has id, kind (DECIDE, REPRESENT, CONNECT, TRANSFORM or VERIFY), action (what is done), why_valid (the physical or logical reason this step is allowed; not 'this follows from the model'), inputs and output. Set crux_move_ref to the id of the move a learner is most likely to miss. Delete the move the band does not need. D1 repair: Keep neighbour/domain, bond-component and orbital-basis inventories distinct. A pi component is not axial density; VSEPR is qualitative. Each action needs its actual local warrant and output, rather than a generic assertion that the source/model permits it. D2 repair: Close the valence-basis ledger: hybrid outputs plus residual functions equal the independent inputs, with no double use. Nuclear shape excludes lone-pair vertices. A geometry drawing does not uniquely measure an orbital basis. D3 repair: Contributors are bookkeeping alternatives, not switching structures. Count the occupied delocalised pi space, not only a drawn double bond. Orthogonal p directions constrain allene terminal planes; Pauli is not a blanket one-bond-per-orbital ban. D4 repair: Separate local counts, occupancy, adjacency, alignment and empirical evidence. A supplied overlap factor is not total energy. Preserve formal electron inventory under torsion; strength, barrier and unique basis require specified further evidence.

**ANSWER** · slot `solution`, inside SOLUTION · ANSWER_BOX

- The learner gets: State the final answer in one place.
- The reference page: selected_question_bank_TABLET_STUDY: the green answer box
- Record fields: `answer.summary`

### Expected components

Expected: an official page missing it carries an advisory naming the field to author; new authoring must supply it or waive it with a written reason, else it is a gap.

**DIFFICULTY_WHY** · slot `identity` · DISCLOSURE_GRID

- The learner gets: Show the author-estimated band, score, time and five component scores. Protect the free-text rationale with the answer and working until the learner commits an attempt.
- The reference page: selected_question_bank_TABLET_STUDY: the D-pill and the 'Why this difficulty?' grid
- Record fields: `extensions.grade9v3:analysis.difficulty`, `extensions.grade9v3:analysis.expected_time_seconds`
- To author it: Fill extensions['grade9v3:analysis'].difficulty: five components (each 0 to 2), score (their sum), band for that score, basis (one sentence); and expected_time_seconds, your estimate of the time a prepared learner needs. They are your estimates and are shown as estimates. The basis may discuss the answer route, so it belongs only to the protected post-attempt solution. Never expose it in the initial difficulty grid.

**CONDITIONS** · slot `attempt` · CALLOUT_INFO

- The learner gets: The givens and assumptions the question states, apart from the question itself.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Conditions.' callout under the options
- Record fields: `conditions`
- To author it: List each stated condition (a constraint or assumption the question gives) as one entry of conditions[]. Never list a method or a result there.

**REPRESENTATION** · slot `representation` · VISUAL_CARD · at least 1 item(s)

- The learner gets: Show a question-aligned representation only when it materially helps the learner interpret, translate or reason about the question; otherwise preserve the explicit applicability waiver.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Representation' card with the question-aligned schematic
- Record fields: `figure_refs`, `extensions.grade9v3:core2_visual_review`
- To author it: Decide representation applicability from the question's semantic review. If useful, add an accessible authored SVG drawn only from the question data and name it in figure_refs. If a figure would be decorative or would leak protected work, waive REPRESENTATION with a written reason. To correct a legacy authored visual while preserving frozen question refs, bind core2_visual_review to the exact question and replaced refs, with a rationale and question-owned authored refs. Authentic SOURCE_FIGURE resources cannot be superseded. A third stage needs a reason if it would perform the learner decision.

**HINT_LADDER** · slot `support` · LADDER

- The learner gets: Provide only the question-specific support the learner needs, one requestable step at a time, with provenance and an explicit disclosure boundary when support completes or materially narrows protected work.
- The reference page: selected_question_bank_TABLET_STUDY: 'Hint ladder · reveal only what you need', five rungs on a hard question (represent / first move, connect, crux, equation / formal model, assembly checkpoint) with SOURCE and EXPANSION pills
- Record fields: `scaffolds`, `hints`, `hint_ladder`
- To author it: Author question-specific support for the semantic jobs the resolved QRT requires: clarify the learner-relative obstacle, connect to demonstrated knowledge, represent relevant givens, or open a route toward the crux while preserving the learner-owned move. Rung count is not a quality target. Each support row keeps typed support_kind/reveals/learner_stage/supports_move_ref. If a row completes or materially narrows a protected move, declare it in grade9v3:core2_support_plan with AFTER_ATTEMPT or POST_SOLUTION availability; only support proven safe relative to protected_move_refs may be PRE_ATTEMPT_SAFE. Do not add filler to reach a number.

**CHECK** · slot `solution`, inside SOLUTION · CHECK_BOX

- The learner gets: Test the answer by a route the working did not use.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Check.' line under the answer
- Record fields: `answer.check`
- To author it: Use a changed case, conservation ledger, counterexample or independent operation with expected result. Repeating the wrong rule as a rejection is not an independent check.

### Optional components

Optional: shown when the record has it.

**SOURCE_PDF** · slot `identity` · LINK_LIST

- The learner gets: Give the learner the original past paper as a PDF, ready to print, when the question's custody names it.
- The reference page: Owner request 2026-10-01: a PDF icon that links the generated or the source PDF so that it is readily available for print
- Record fields: `extensions.grade9v3:source_custody.paper_url`, `extensions.grade9v3:source_custody.authority_class`, `extensions.grade9v3:source_custody.source_status`
- To author it: Nothing to write: the page links the paper when the question's source custody is an official exam organizer archive, verified (source_status PYQ_VERIFIED_PARENT), and paper_url is an https link to a PDF. An owner-supplied question has no source file and shows no link; never put a link in the record to make the icon appear.

**TRAP** · slot `support` · CALLOUT_WARN

- The learner gets: Offer a question-specific wrong-route warning only as assistance whose disclosure boundary preserves the learner-owned decision. A closed panel is not protection: if naming the wrong route would narrow or complete protected work, it is not pre-attempt-safe and belongs in typed after-attempt or solution support.
- The reference page: selected_question_bank_TABLET_STUDY: the 'Common wrong route.' box
- Record fields: `extensions.grade9v3:analysis.common_wrong_route`, `extensions.grade9v3:core2_support_plan`
- To author it: Treat common_wrong_route as an authored support hypothesis, not a diagnosis. It may appear before commitment only when the warning is genuinely PRE_ATTEMPT_SAFE relative to protected_move_refs. If the warning identifies the winning model, decisive exclusion, warrant, or other protected work, author it in typed question support and bind its availability through grade9v3:core2_support_plan as AFTER_ATTEMPT or POST_SOLUTION. Collapsed/closed presentation never makes otherwise unsafe content safe.

**CONCEPT_NAV** · slot `support` · LINK_LIST

- The learner gets: Let the learner deliberately leave the source question for the exact Core1A construction or repair, preserve origin/return context, and record the current question as assisted rather than independent.
- The reference page: selected_question_bank_TABLET_STUDY: concept links beside the hints (the Core1A cross-link)
- Record fields: `extensions.grade9v3:learning_repair.construction_ref`, `primary_capability_ref`, `secondary_capability_refs`
- To author it: Prefer an exact learning_repair.construction_ref when authored; otherwise resolve the capability to the exact construction that teaches the missing bridge. Opening concept help is learner-requested assistance: preserve the source/return anchor and do not count the same-question retry as independent transfer. A fresh changed item may later provide independent evidence.

**DIAGNOSTIC_REPAIR** · slot `solution`, inside SOLUTION · CHECK_BOX

- The learner gets: After learner evidence warrants diagnosis, distinguish a misconception hypothesis from a slip/alternative route, show a bounded repair only when confirmed, then require a fresh verification before treating the repair as successful.
- The reference page: Issue #32 Q1/Q4 observed hint and representation defects; Issue #31 repeated reject-the-rule checks, correction cycle R2.
- Record fields: `extensions.grade9v3:learning_repair`
- To author it: An authored wrong_idea/diagnostic_prompt is a hypothesis, not a learner diagnosis. Use the typed diagnostic-evidence contract: canonical hypothesis + discriminating probe + observed learner response + evaluator basis. Only complete CONFIRMED evidence may select misconception-specific repair; INDETERMINATE, REFUTED, invalid, or bare-index claims remain non-confirming. Preserve uncertainty and require fresh verification after repair; do not grade free response by keyword or declare mastery.

## BP-CORE1A-CONSTRUCTION@1.8.0 (CORE1A)

Learner job: Build a reusable concept by constructing the decisive bridge, using an adjacent representation when it materially helps, summarizing the key insight, and then independently retrieving, explaining, or applying it in a changed case. Worked examples, completion, comparison, quick checks, and repair are conditional teaching operators rather than mandatory panels; protected source questions are not the default teaching anchor.

Theme: opens light, and the learner can switch.

Layout: from 1100 px wide, the primary column is 60% and the support column 40%. Narrower, everything is one column, primary first.

| Slot | Column | Kept |
|---|---|---|
| `identity` | FULL | always |
| `construction` | FULL | always |
| `repair_closure` | FULL | always |

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

**CONSTRUCTION_STEPS** · slot `construction`, once per construction unit · STEP_CARDS · at least 2 item(s)

- The learner gets: Build the idea in steps; every step says what is done, why it is valid and what state it gives.
- The reference page: core1a-motion-in-a-plane-tablet: step cards (action, why physically valid, state output)
- Record fields: `construction_units[].step_refs`, `teaching_path`
- To author it: Each construction unit names at least 2 teaching_path steps, and every authored step states the action, why it is valid, and the state/output it establishes. Choose additional steps only when the inferential burden requires them; difficulty band does not prescribe a panel count. A unit that builds a question crux binds the actual crux_question_refs and crux_step_ref so the decisive bridge is taught explicitly. Preserve representation invariants, model boundaries, applicability conditions, and changed-case transfer when those are material to the concept; do not import subject-specific repair rules into the shared blueprint.

**KEY_STEP** · slot `construction` · BANNER

- The learner gets: Name the one step learners cannot infer on their own.
- The reference page: core1a-motion-in-a-plane-tablet: the inferential-leap banner
- Record fields: `inferential_jump`
- To author it: inferential_jump: one or two sentences naming the step a learner does not make unaided and why it is not obvious.

**EXIT_RECALL** · slot `repair_closure` · RECALL_CARD

- The learner gets: Require an independent attempt with less support after the construction and worked example.
- The reference page: core1a-motion-in-a-plane-tablet: the active-recall attempt
- Record fields: `exit_task`

### Expected components

Expected: an official page missing it carries an advisory naming the field to author; new authoring must supply it or waive it with a written reason, else it is a gap.

**MODEL_CONTRACT** · slot `construction` · DISCLOSURE_TILE

- The learner gets: Keep prerequisites available without competing with the construction; collapsed by default.
- The reference page: core1a-motion-in-a-plane-tablet: the 'Model contract & assumptions' tile
- Record fields: `entry_assumptions`, `prerequisite_refs`
- To author it: List in entry_assumptions[] each thing a learner must already be able to do before this concept, one per entry and specific to this concept.

**STAGED_VISUAL** · slot `construction`, once per construction unit · STAGED_VISUAL · at least 2 item(s)

- The learner gets: When a spatial or mechanism representation materially helps the construction, show it as a picture that builds stage by stage. A construction with no useful visual is explicitly waived by the authored record; no decorative figure is invented.
- The reference page: core1a-motion-in-a-plane-tablet: the rail's staged visual with stage buttons
- Record fields: `construction_units[].representation_ref`
- To author it: First decide whether a staged visual has a real semantic job for this construction. When it does, representation_ref names an accessible representation and reveal_stages contains only the stages needed to construct the correspondence or mechanism. Stage count follows the representation, not the question's D-band. When a visual is genuinely not applicable, waive STAGED_VISUAL with a written reason instead of drawing decoration.

**EQUATIONS** · slot `construction`, once per construction unit · DISCLOSURE_EQUATION_CARD

- The learner gets: Keep formulas, meaning and validity conditions available as on-demand reference rather than a mandatory reading detour.
- The reference page: core1a-motion-in-a-plane-tablet: the equation card of every concept card (definition and validity scope)
- Record fields: `construction_units[].relation_refs`, `relation_refs`
- To author it: Each construction unit names the microtopic's relations it uses in construction_units[].relation_refs; each relation record needs its expression, meaning and conditions. A subject that declares no gates writes gate_relation_ref: null.

**WORKED_EXAMPLE** · slot `construction`, once per construction unit · WORKED_CARD

- The learner gets: When a completed instance materially helps the learner consolidate the constructed idea, show a coherent worked explanation with explicit warrants and outputs. A concept may instead proceed from construction directly to reduced-support independent application when that better preserves the learning job.
- The reference page: core1a-motion-in-a-plane-tablet: the worked card
- Record fields: `construction_units[].worked_anchor_ref`, `construction_units[].bank_anchor_ref`, `extensions.grade9v3:lesson_anchors`
- To author it: Use a lesson anchor or other mapped worked instance when seeing a completed route materially helps this construction. Bind any hardest-target bridge to the precise target question/crux/construction, but do not require the protected source question itself to become the teaching anchor. If a worked example would merely replay the construction or leak the next independent task, author an explicit applicability waiver instead.

### Optional components

Optional: shown when the record has it.

**SECTION_ROUTE** · slot `identity` · CHIPS

- The learner gets: Let the learner jump to a construction step.
- The reference page: core1a-motion-in-a-plane-tablet: the section tabs

**QUESTION_BRIDGE** · slot `construction`, once per construction unit · DISCLOSURE_INFO

- The learner gets: Keep question-set rationale available on demand without interrupting the learning path.
- The reference page: core1a-motion-in-a-plane-tablet: each concept card is built around the inferential leap the practice questions need
- Record fields: `construction_units[].crux_question_refs`, `construction_units[].crux_step_ref`, `answer.crux_move_ref`
- To author it: Name actual crux_question_refs and crux_step_ref. The hardest-target unit must teach that precise bridge through its worked instance; a distinct lesson anchor must explicitly bind the target question, its actual crux move and this construction unit. A shared topic alone is insufficient.

**MODEL_SCOPE_PROBE** · slot `construction`, once per construction unit · CHECK_BOX

- The learner gets: When explicitly authored, make bounded parameter/countermodel construction visible beside the staged visual; keep diagnostic help separately closed.
- The reference page: Issue #37 Q9 and #38 Q2/Q9 correction cycle: absent continuous model-boundary construction.
- Record fields: `extensions.grade9v3:question_repairs`
- To author it: Opt in with a question/crux/construction-bound MODEL_SCOPE_PROBE repair record. Declare axis, independent variables, toy versus physical outputs and a static fallback. Do not infer applicability from the demand label.

**TRAP_REPAIR** · slot `repair_closure`, once per construction unit · DISCLOSURE_TRAP_CARD · at least 1 item(s)

- The learner gets: When there is an evidence-supported confusable model or recurring wrong route worth distinguishing, offer a requestable mistake clinic with a discriminating probe, bounded replacement rule, and fresh application. Do not manufacture a misconception or repair panel merely to complete the page.
- The reference page: core1a-motion-in-a-plane-tablet: the easy-mistake card with diagnostic and repair
- Record fields: `misconceptions`, `construction_units[].misconception_indexes`
- To author it: Author misconception rows only when a plausible wrong idea is materially relevant to this construction. Each row carries wrong_idea, a diagnostic_prompt that can distinguish the hypothesis from a slip/alternative route, and a bounded repair. A construction unit names only the rows that actually apply; absence of a justified misconception is valid and requires no filler.

**QUICK_CHECK** · slot `repair_closure`, once per construction unit · CHECK_BOX · at least 1 item(s)

- The learner gets: When a compact checkpoint materially helps consolidation before the independent exit, ask one or more question-specific checks that retrieve, apply, connect, compare, or explain the concept without imposing a fixed role count.
- The reference page: core1a-motion-in-a-plane-tablet: the 1-2-3 quick check (CHECK, APPLY, CONNECT)
- Record fields: `construction_units[].independent_checks`
- To author it: independent_checks[] is optional intermediate evidence. Author only the checks that add a distinct learner job for this unit; CHECK/APPLY/CONNECT are available roles, not a mandatory triad. Do not duplicate the mandatory EXIT_RECALL or create filler to reach a number.

**PRACTICE_LINKS** · slot `repair_closure` · CHIPS

- The learner gets: Point to the authentic questions that practise this concept.
- The reference page: core1a-motion-in-a-plane-tablet: the practice chips
- Record fields: `practice`

**INTERACTIVE_BRIDGE** · slot `repair_closure` · VISUAL_CARD

- The learner gets: Contextual action to open an interactive simulation when one is bound to this concept.
- The reference page: core1a-nlm-friction-tablet: interactive threshold explorer bridge
- Record fields: `concept_bundle.interactive`

**LEARNING_TRANSITIONS** · slot `repair_closure` · CHIPS

- The learner gets: Derived transitions connecting Learn, Practice, Interactive, and Question Bank.
- The reference page: core1a-nlm-friction-tablet: learning transition bar
- Record fields: `concept_bundle`

## BP-EXPLORER-GCDR@1.0.0 (EXPLORER)

Learner job: Test the tempting model of the hardest concept of the question set against a model that cannot be argued with, rebuild the mathematics from what is visible, find where it stops being true, and then do a fresh task without the explorer.

Theme: opens light, and the learner can switch.

Layout: from 1100 px wide, the primary column is 66% and the support column 34%; the support column stays in view while the primary column scrolls. Narrower, everything is one column, primary first.

Route: the learner meets the steps in this order, each after the one before is done: CONTEXT → PREDICT → MANIPULATE → OBSERVE → CONTRADICT → DECONSTRUCT → RECONSTRUCT → INVARIANT → BOUNDARY → FADE → TRANSFER.

| Slot | Column | Kept |
|---|---|---|
| `identity` | FULL | always |
| `stage` | PRIMARY | always |
| `route` | SUPPORT | always |

### Required components

Required: a page without it is a gap, and the quality gate fails it.

**ROUTE_RAIL** · slot `identity` · ROUTE_RAIL

- The learner gets: See the eleven steps of the route and which one the learner is on, so the page is a path with an end and not a toy.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): the mandatory cognitive sequence, one chip per step

**TARGET** · slot `route` · CALLOUT_INFO

- The learner gets: Name the one concept the page is for, the tempting model it replaces, the move to acquire, what survives and where it stops: the toughest concept of the question set.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): one explorer, one cognitive target
- Record fields: `target`
- To author it: target: question_ref is the toughest question of the set (python3 Shared/tools/explorer_build.py new fills it in; python3 Shared/tools/toughest_concept.py MANIFEST names it). failure: the learner's tempting model, one sentence, in the learner's words. operation: the move to acquire. invariant: what survives every valid variation. boundary: where the shortcut stops being right. quantity: the id of the quantity the whole page is about.

**SOURCE** · slot `route` · STEM

- The learner gets: Show the owner's question the concept comes from, word for word, so that the explorer rejoins it.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): the exit rejoins the same semantic leaf

**PARAMETERS** · slot `stage` · CONTROL_PANEL · at least 1 item(s)

- The learner gets: The state the learner moves (sliders) and the givens that stay fixed: the only way the page changes.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): direct manipulation of one governed state
- Record fields: `parameters`
- To author it: parameters: each {id, label, unit, min, max, step, value} for a slider, or {id, label, unit, value, fixed: true} for a given of the question. max - min must be a whole number of steps and value a position of the slider. Ids are letters, digits and underscores (theta, v_1); never a word of the expression language (min, max, if, e, pi).

**QUANTITIES** · slot `stage` · CONTROL_PANEL · at least 3 item(s) (the reference has 4)

- The learner gets: Every number the page shows, as an expression of the parameters, so each one is computed and none is typed.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): one authoritative state; no invented exact parameters
- Record fields: `quantities`
- To author it: quantities: in order, each {id, label, unit, expr, decimals}; expr uses the parameters and earlier quantities: + - * / ^ ( ), sqrt abs hypot min max clamp round if(c,a,b) sin cos tan (radians), sind cosd tand asind acosd atand atan2d (degrees), pi, and comparisons with and/or/not. Write 2*a*b, never 2ab; v_x is written as a subscript. Include the quantity the page is about, the tempting model's value, and the parts the mechanism shows.

**SCENE** · slot `stage` · STAGE_VIEW · at least 5 item(s) (the reference has 8)

- The learner gets: The phenomenon and, one step at a time, its hidden mechanism, drawn from the model's own numbers; and the checks that tie the drawing to them.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): G1 phenomenon and G2 mechanism; rendered-geometry truth
- Record fields: `scene`, `oracles`
- To author it: scene: title, job (what this view shows that the other cannot), description (what a learner who cannot see it is told), world {x:[min,max], y:[min,max]} (keep the aspect between 0.36 and 1.1), elements of kind point, segment, arrow, circle, arc, polygon, curve, text. Coordinates are expressions: at/from/to/center are [x, y]; curve has param, t_min, t_max, x, y. role: object, given, result, wrong (the tempting model, dashed), helper, frame. label may show a number as {quantity:decimals}. reveal: start (the situation), manipulate (the result), contradict (the tempting model), deconstruct (the mechanism: components, constraints, forces, relative motion). The check says where an element leaves the picture. oracles: expressions that tie the drawing to the quantities using an element's numbers (arrow_x1, arrow_y2, point_x, circle_r, arc_a2).

**SECOND_VIEW** · slot `stage` · STAGE_VIEW · at least 1 item(s)

- The learner gets: A second representation that does a different reasoning job from the picture: the quantity against the slider, with the tempting model's curve as a ghost.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): coordinated representations that add distinct reasoning value
- Record fields: `second_view`
- To author it: second_view: kind graph, title, job, description, x (a slider parameter), series [{quantity, label, role}] (include the quantity the page is about), guides [{expr, label, orient: h or v}] for bounds the learner should see, ghost {quantity, label} for the tempting model (drawn only at the contradiction).

**CONTEXT** · slot `route` · ROUTE_STEP

- The learner gets: Place the learner in the situation the question describes, with the question itself, before any equation or control.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): CONTEXT
- Record fields: `context`
- To author it: context.situation: one to three sentences placing the learner in the physical or geometric situation, with no equation and no hint of the answer.

**PREDICT** · slot `route` · ROUTE_STEP · at least 3 item(s)

- The learner gets: The learner commits to a prediction before any control moves; the page keeps it and returns to it after the evidence.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): PREDICT; prediction occurs before answer reveal
- Record fields: `predict`
- To author it: predict.prompt, predict.options (three): each {text, tests: [{set: {parameter: value}, holds: expression, says: sentence with {quantity:decimals}}]}. An option is true of the model when all its tests hold. Exactly one option is true (predict.correct is its index); every other has a test that fails, and says tells the learner what that test showed. Make the tempting wrong model one of the options. Expressions may read the whole model: at(R, theta, 90) is R with theta set to 90, maxover(R, theta) and minover(R, theta) its largest and smallest, argmax(R, theta) where it is largest.

**MANIPULATE** · slot `route` · ROUTE_STEP · at least 2 item(s) (the reference has 3)

- The learner gets: Direct manipulation with a purpose: goals the learner reaches on the sliders. The controls stay locked until the prediction is made.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): MANIPULATE; meaningful direct manipulation
- Record fields: `manipulate`
- To author it: manipulate.goals: each {prompt, goal: an expression true at the state to reach, hint}. Each goal must be reachable on the sliders' steps and not already met at the start; the check says if not.

**OBSERVE** · slot `route` · ROUTE_STEP · at least 3 item(s) (the reference has 4)

- The learner gets: The learner judges statements about what they saw; the page checks each against the whole model and shows a state that settles it.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): OBSERVE
- Record fields: `observe`
- To author it: observe.statements: each {text, claim, truth, why}. claim is an expression checked at every state the sliders reach; truth says what that gives: always (a law of the model), never, or sometimes. Include at least one that is always true and the tempting one that is not. why explains it in a sentence.

**CONTRADICT** · slot `route` · ROUTE_STEP · at least 1 item(s)

- The learner gets: The learner imposes the tempting model and sees, in the picture and on the graph, where it cannot be right, and why the correct model works.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): CONTRADICT; counterfactual requirement
- Record fields: `contradict`
- To author it: contradict: wrong_model {label, quantity} (the quantity that states the tempting model), imposes (one sentence: suppose the model were true), goal {prompt, goal, hint} (find a state where it visibly fails), why_correct and why_wrong (feedback must answer both why the correct model works and why the tempting one cannot). Show the tempting model in the scene with reveal: contradict, and as second_view.ghost.

**DECONSTRUCT** · slot `route` · ROUTE_STEP · at least 3 item(s) (the reference has 4)

- The learner gets: Expose what is normally invisible, one cause at a time, in the order the cause acts.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): GRAPHICAL DECONSTRUCTION; G2 mechanism; explicit causal chain
- Record fields: `deconstruct`
- To author it: deconstruct.steps: each {text, reveals: [element ids], ask?: {prompt, options, correct, why}}; the elements it reveals have reveal: deconstruct in the scene and each is revealed by exactly one step. Order the steps as the causes act. A step may reveal nothing and only say what the last one means.

**RECONSTRUCT** · slot `route` · ROUTE_STEP · at least 2 item(s) (the reference has 3)

- The learner gets: Build the mathematics from the visible mechanism: each step is a quantity the picture shows, and the final equation compresses them and is checked equal to the quantity at every state.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): MATHEMATICAL RECONSTRUCTION; the final equation is a compression of the visible mechanism
- Record fields: `reconstruct`
- To author it: reconstruct.steps: each {text, quantity} naming a quantity the mechanism showed; reconstruct.equation {text, expr}: the closed form that must equal the quantity the page is about at every state (the check says where it does not, and rejects an expression identical to the quantity's own).

**INVARIANT** · slot `route` · ROUTE_STEP · at least 2 item(s)

- The learner gets: The learner tries to break what survives every valid variation, and finds they cannot.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): INVARIANT DISCOVERY; representation invariants need an oracle
- Record fields: `invariants`
- To author it: invariants: each {text, lhs, rel, rhs, try}; rel is ==, <= or >=; the relation must hold at every state the sliders reach (the check says where it does not). try tells the learner how to look for a state that breaks it.

**BOUNDARY** · slot `route` · ROUTE_STEP · at least 2 item(s) (the reference has 3)

- The learner gets: The learner finds where the shortcut stops being right: cases where it holds and cases where it fails, judged against the model.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): BOUNDARY STRESS
- Record fields: `boundary`
- To author it: boundary: assumption (what must hold for the shortcut), learner_must_identify (the point the learner takes away), cases: each {text, set: {parameter: value}, shortcut_label, shortcut: expression, expect: holds or fails}. The page compares the shortcut with the quantity the page is about at that state; expect must agree, and at least one case holds and one fails.

**FADE** · slot `route` · ROUTE_STEP · at least 3 item(s)

- The learner gets: The supports are taken away in three levels: the numbers on the picture, then the relation, then the mechanism; the learner answers with less each time.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): SCAFFOLD FADE
- Record fields: `fade`
- To author it: fade: three tasks, each {prompt, set: {parameter: value}, answer: expression, unit, decimals, tolerance, why}. Level 1 hides the numbers on the picture, level 2 also hides the mechanism and the graph, level 3 shows the physical scene only. The page sets the state to `set`; the answer is an expression at that state.

**TRANSFER** · slot `route` · ROUTE_STEP · at least 2 item(s) (the reference has 3)

- The learner gets: A fresh task, with the explorer closed: new numbers the learner has not seen, answered from what was learned.
- The reference page: GCDR v1.3 (docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md): FRESH TRANSFER; the exit rejoins the same semantic leaf
- Record fields: `transfer`
- To author it: transfer: tasks, each {prompt, set: {parameter: value}, answer: expression, unit, decimals, tolerance, why, worked: [lines with {quantity:decimals}]}. set must differ from the starting numbers (fresh); the answer is an expression at that state; worked is the solution shown after the learner's attempt, every number computed.
