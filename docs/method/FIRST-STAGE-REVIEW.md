# First-stage review and six-Core authoring guidance - v3

Status: working method guidance, 2026-09-29. The Owner directed the first-stage sequence and explicitly prohibited new blockers or CI. Issue #352 adds difficulty-first authoring/review priority inside that existing route. Output details and implementation followups remain design recommendations. This document does not claim that the renderer or schemas already implement them. It records learning relationships and review expectations, not build admission conditions.

Material inspected: merged PR #346; issue #352 and its accepted review amendments; `PROTOCOL.md`; `Shared/roles/CORE1.md` and `CORE2.md`; package, competitive bank and observation schemas; `learner_metadata.py`; `atlas_index.py`; `render_core.py`; `tools/print/print-product.mjs`; the Polynomials stress report and golden candidate descriptions. Common V3.1 was read at `1ced68258afeaf50df113b1d38a4ceb9193587e3`. Revalidate live main before implementation.

## 1. Sequence directed by the Owner

Use this sequence:

```text
source / supplied question bank / syllabus
→ establish the real denominator + source state
→ choose the existing first-stage route
     usable bank/source-question corpus → Core2
     no usable bank                     → source-grounded Core1
→ triage canonical difficulty + why it is difficult + interaction value
→ author/review the hardest worthwhile vertical slice(s) first inside that route
→ present the first-stage learner packet with the complete denominator/coverage view
→ Medium
→ Low / remaining coverage
→ later Core work in the requested product scope
```

1. **Establish the denominator first.** Inventory the supplied source/bank scope or the scoped teaching/syllabus concepts before prioritizing. A supplied bank is not automatically verified, complete or an official PYQ bank; retain those distinctions per item.
2. **Choose the existing route from that source state.** When a usable question bank/source-question corpus is provided, the first-stage learner product is Core2. When no usable bank exists, the first-stage learner product is source-grounded Core1. Do not manufacture a bank to choose Core2.
3. **Triage before completing the first-stage artifact.** Use the existing concept difficulty and, for questions, existing D1-D4/question-component model. Separately explain the teaching/solving difficulty and judge interaction value. Do not create a second scoring system.
4. **Author/review Hard first inside the selected route.** Complete coherent vertical learning slices instead of chapter-wide shells. Hard-first is an authoring/review priority, not source reordering or mandatory learner navigation.
5. **Present the first-stage outputs and their review packet before generating the remaining Cores.** The packet includes actual learner HTML/PDF and the complete denominator/coverage view. For a Core2 route, Hard-first implementation must not hide Medium/Low/deferred or unresolved source items from that view. Research, sketching, independent solving and drafting across all Cores can continue throughout. This is the Owner's requested presentation order, with no new approval token, automated quality threshold or prerequisite PASS.
6. **Revise the same canonical records and product manifest.** Subsequent Cores extend that product. Preserve the previous review basis and show changes.

Required ordering distinction:

```text
authoring priority ≠ source order ≠ learner navigation order
```

A partially usable bank still takes the Core2 route: show the usable subset and every omitted/unresolved item with its reason. If nothing is usable, show the inventory and source gaps, continue acquisition/research and develop source-grounded Core1 material where possible. Explain that fallback; do not present an empty Core2 shell as the deliverable or wait on a form before doing useful work.

`LP-H* / LP-M* / LP-L*` are scheduling identifiers only. Interaction value (`HIGH / MEDIUM / LOW`) is an authoring judgement only. Neither belongs in learner difficulty, package authority or search metadata. Question-difficulty components belong to canonical question metadata when applicable; when the same ideas help explain why a concept is hard to teach, use them descriptively rather than silently creating concept component scores.

For a new or uncalibrated instructional pattern, one or two coherent Hard slices are the default calibration heuristic before broad helper parallelism. For an already-calibrated pattern, bounded helpers may start earlier from the same canonical design. In both cases one unit author owns and reconciles academic meaning. No calibration token is required.

If Polynomials is reused as a #352 pilot, consume a coherent #350 producer handoff plus canonical records. Do not regress to the historical 27-row stress ledger or treat stale/open PR prose as production authority merely because it is newer. The producer handoff should make acquisition identities/digests, denominator meaning, readback state, unresolved items, canonical question handoff, syllabus mapping and validation truth reconstructable to a zero-context consumer. This is producer/consumer coherence, not a permission gate.

## 2. What the first-stage packet contains

| Artifact | Core2 route | Core1 route |
|---|---|---|
| Learner HTML | Topic-organized selected source questions with stable question links, faithful content, typed commitment and staged help; Hard slices may be implemented/reviewed first | Compact concept orientation, relations with conditions, representations, prerequisites and scope; Hard concepts/transitions may be authored/reviewed first |
| Learner PDF | The same selected learner scope, labels, figures and ordering; readable working space; no protected answer or solution material | The same selected concept scope and representations, laid out as readable notes |
| Separate key PDF | Source key, independent result where verified, reasoning, hints and discrepancy explanations; missing answers stay explicit | Only applicable if the notes include a separate self-check; otherwise NOT_APPLICABLE |
| Coverage and mapping view | One row per inventoried question across the **complete supplied denominator**, with implemented/selected/Medium/Low/deferred/omitted/unresolved state and reason, source status, and topic/concept/family coverage | One row per scoped concept across the complete concept denominator, its source, difficulty/priority state, required relationships and coverage |
| Owner review record | Exact input/render/output hashes, findings, screenshots, PDF pages, test results, revisions and unresolved questions | Same |

Hard-first implementation/review priority must not narrow the denominator view. The first-stage packet may contain only a bounded learner slice while the mapping view still exposes every supplied item/concept and its current state. Distinguish implemented learner scope from denominator coverage explicitly.

Show links to the actual HTML and PDFs directly in the handoff. Include representative rendered pages alongside the mapping view. JSON, a log or a PASS report cannot replace the learner artifacts. Use the existing renderer and its browser print path for both formats.

## 3. Explicit content and metadata

| Element | Learner-facing requirement | Owner/audit detail |
|---|---|---|
| Identity | Product title, subject, Core, topic/subtopic, readable question or concept number | Stable canonical record ID, original source number, artifact revision; display order is not identity |
| Concept labels | Clear primary concept and relevant supporting concepts, with readable names | Primary/secondary capability refs, microtopic and bucket refs; unresolved or disputed mappings shown explicitly |
| Topic segregation | Contents and topic sections; HTML topic/concept/difficulty filters and clear empty results | Full supplied denominator, selected/implemented count, Medium/Low/deferred/omitted/unresolved counts, duplicates and multi-concept membership without double counting |
| Difficulty | Core2: D1-D4 question badge labelled as an estimate, with a short rationale. Core1: existing intrinsic concept badge with its reason | Preserve source rating separately when different; reuse the existing five-component model for **question** difficulty, not a new score or concept-component schema; unassessed is explicit |
| Authoring priority | Do not show LP-H/LP-M/LP-L or interaction-value labels as learner difficulty | Design Note/Worklog may record lot and interaction-value reasoning; they are not package/search authority |
| Source | Source name and original identifier; truthful original/adapted/authored/unverified label | Acquisition, exact locator, retained source digest, custody/readback, changed fields and missing components |
| Complete question | Stem, subparts, options, conditions, units, figures and captions; original relationships preserved | Component-by-component source comparison, including missing figure/table/key and transcription uncertainty |
| Response | Control appropriate to the question type and a clear commitment action; paper attempt supported where suitable | Commitment is participation, not correctness, grading or mastery evidence |
| Support | Hints revealed in sequence; source hints distinguished from authored support; solutions after commitment | Preserve source order; retain original source figures and separate any added solution overlays |
| Key and result | Post-attempt/key copy distinguishes printed key, independently verified result and disagreement | Reviewer, calculation/evidence and exact reviewed basis; no invented verification claim |
| Atlas | Link to the actual canonical topic/concept entry when available | Declared question -> capability -> microtopic -> bucket/Atlas edges, mapping basis and missing edges; no inference from similar titles |
| Interactive activity | Show an activity link only when it has a specific learning purpose and a working destination | Existing resource ID/ref, target concept, purpose, availability and pre/post-attempt timing; interaction value remains authoring rationale, not indexed academic metadata |
| Learner difficulty | Optional private observations by concept: not yet observed, tried with help, needs another look, demonstrated with evidence | Attempt, question, concept, date, help used, self-report and observed error stage remain distinct; no diagnosis from a chapter percentage |
| Coverage boundaries | Scope and known omissions stated plainly | Coverage of the provided source is distinguished from coverage of a syllabus; both need an explicit denominator |
| Next step | Available prerequisite or review destination, with a clear purpose | Missing downstream Cores are listed as planned in the Owner view, not offered as dead learner links |

Concept labels that reveal the deciding move need disclosure care. Default to safe topic/concept labels for learning; put solution-bearing labels, detailed mapping rationales and repair suggestions after commitment. Full mappings remain visible to the Owner. Do not put protected answers, method hints, authoring-lot labels or solution-bearing transfer rationale in pre-attempt search metadata, accessibility labels or figure alternatives.

## 4. Identity and learner evidence semantics

Use three existing identity levels rather than inventing a parallel page-ID system:

- Logical page: product identity plus Core role.
- Item/concept: canonical record ID, used as a stable HTML fragment and printed beside the corresponding item.
- Exact version: input digest and render digest, plus HTML/PDF file hashes in existing receipts.

A PDF locator can link to the corresponding HTML fragment. Add a QR code only when a stable, accessible URL exists; a local Windows path is not a usable QR destination. An optional activity has its own existing resource identity and is not the question page's identity.

Learner difficulty is an evidence view, not an authored property of a topic. Start with **not yet observed**. A self-report such as "hard" is stored/displayed as self-report; a hint click is an event. Neither proves inability. Multi-concept questions do not justify assigning the same failure to every concept. Show uncertainty and the observed error stage; retain recency, support used and evidence links. Topic summaries show concept-level observations and counts, never inferred mastery percentages. A generic product carries no child's private history; a personalized view requires supplied observations. Any new self-report/event fields belong in the existing learner/session evidence contract, not the academic package.

## 5. Core1-first content boundary

Core1 first needs a source-grounded authoring path independent of Core1A. Its minimum useful content is:

- Scope, prerequisite map and topic/concept navigation.
- Objects, definitions, notation, units and conventions.
- Governing relations with meaning, conditions and relevant boundary cases.
- A compact illustrative anchor and useful labelled representation where they clarify the concept.
- Common confusions or intrinsically difficult transitions, without turning the notes into Core1A construction lessons.
- Source references, explicit gaps and planned next teaching needs.

Difficulty-first Core1 authoring may complete the hardest transitions first, but the first-stage mapping view still shows the full scoped concept denominator and the state of Medium/Low/remaining coverage.

Preserve existing frozen Core1 material and identify corrections separately. New source-authored Core1 must carry its own review status; it cannot borrow a future Core1A review. Reading notes or ticking "understood" does not establish mastery.

## 6. HTML and PDF review evidence

Review the same selected learner scope in both formats and reconcile it with the full denominator/coverage view. The learner PDF must retain all required givens, conditions and demand-bearing figures while excluding protected hints, keys and solutions. Optional authored help belongs in the key PDF by default; help explicitly printed as part of a source question is retained and labelled as source material.

Keep stems with options and their figures when practical; long questions may continue with repeated identity. Provide sensible working space, readable mathematics, page numbers and topic headers. Remove web-only disclosure controls. Avoid accidental title-only/footer-only pages. Preserve the existing 280 x 175 mm landscape fixture profile as a comparison basis while judging actual readability and pagination; do not label a format change as fixture parity.

For HTML, capture raw HTML, real Chromium DOM/accessibility/search/interaction evidence and tablet landscape/portrait views. Check a valid typed commitment, invalid/blank commitment, hint order, inserted figures, keyboard focus, touch targets and absence of solution text from pre-attempt search/accessibility surfaces. For PDFs, inspect every page visually and extract text to compare item IDs, content, figures and answer separation. Browser unavailable means NOT_RUN.

For each reviewed requirement, record PASS, FAIL, NOT_RUN or NOT_APPLICABLE against the exact render. Report empty content, missing sources, wrong mappings and layout defects separately. These observations inform judgement; they do not decide publication or impose a numerical improvement quota.

### Existing fixture observation

Read-only inspection of `C:/CodeA/Grade9V3/prb-direct-pdf/core2.pdf` and `core2.key.pdf` found a useful negative example: one question spans three learner pages and four key pages. The learner PDF has a title-only page and a trailing web disclosure control/footer page; the key has a footer-only final page. The key usefully distinguishes the rounded printed answer from the exact verified result. Preserve that semantic distinction while treating the pagination as a defect, not a golden layout. These historical fixture findings do not certify current main.

## 7. Minimal shared changes needed after contract finalization

| Surface | Required change |
|---|---|
| Method protocol, unit-author role/prompt and templates | Express denominator → route → triage → Hard-first vertical authoring → complete first-stage packet; preserve full denominator visibility and no new gate |
| Design Note / Worklog | Record difficulty-first authoring rationale, interaction purpose, lot state, calibration/parallel basis and actual/planned exposure without creating a parallel academic datastore |
| Core1 role | Add the direct source-grounded initial authoring path while preserving frozen notes and truthful review status |
| Existing product manifest / build command / receipt | Represent intended first-stage role and selected output roles; generate that learner scope; record other roles as not generated; report selected-scope findings without requiring completion of other Cores |
| Sole renderer and metadata projection | Topic grouping, secondary concepts, stable item anchors, useful links, explicit missing metadata and truthful partial navigation; display existing difficulty provenance/rationale only |
| Existing canonical schemas | Reuse IDs, capability refs, family refs, figures, source custody, difficulty and resource refs; extend only proven missing mapping/disclosure information in their owning schema |
| Existing learner/session evidence | Preserve actual attempts, self-reports and help separately; derive the child's concept/topic view from referenced evidence |
| Existing browser print path | Learner/key content parity, print structure, working space, headers/footers and identity links; no second PDF renderer |
| Existing evidence and acceptance path | Bind review to inputs/render/file hashes, preserve revisions and mark stale reviews after relevant changes; exact-digest Owner acceptance remains the sole publication action |

New schema fields and implementation details remain proposed until reconciled with live main. Do not copy authoring lot or interaction-value labels into package records to satisfy checks. The next implementation slice should demonstrate the corrected first-stage path and show its outputs before generating other Cores. Topic content, database work and unrelated site/UI repair remain with their separately scoped work; this guidance defines what those consumers should expose. No new CI job, refusal rule, quota, approval state, calibration state or whole-product completion check is introduced.

## 8. Dependencies across all six Cores

These are dependencies of academic claims and learner experience, not locks on authoring order. The canonical package and actual sources own the underlying truth. Rendered Core pages are projections of that truth, not new sources to scrape or duplicate. Research may expose a problem anywhere and revise the shared design.

| Core | Evidence and design it draws on | Distinct learner work and output | What it contributes downstream |
|---|---|---|---|
| Core1 - orientation | Teaching sources, canonical concepts/relations/prerequisites; Core2 mappings can reveal demand and omissions when a bank exists | Read a compact map of meaning, notation, conditions, boundaries and difficult transitions | Shared concept/topic vocabulary, scope and representation orientation for all other Cores; it does not prove teaching or mastery |
| Core2 - source questions | Actual bank, source custody, original item structure, canonical concept/Atlas mappings | Attempt the source question; consult source-faithful material and clearly distinguished authored help | Observed demand, source identities, question families and difficulty evidence for Core1 refinement, Core1A/B emphasis and Core2A/B design; bank coverage does not establish syllabus coverage |
| Core1A - construction | Same canonical concepts as Core1, teaching research, prerequisites and useful Core2 demand evidence | Follow why a difficult inference works through explanations, worked anchors, representations and checks | A construction route and conceptual truth that Core1B elicits; taught capabilities and repair destinations for Core2A/B |
| Core1B - reconstruction | Same conceptual crux and intended coverage as Core1A; misconceptions, representations and boundary cases | Predict, construct or explain before seeing reconstruction, diagnosis and repair | Evidence of the learner's conceptual reasoning and specific repair needs; optional support input for practice |
| Core2A - familiar application | Canonical taught capability, Core1A/B reasoning and repair routes; Core2 family/demand evidence when available, otherwise honestly authored practice | Attempt familiar application with staged support, a complete reasoning route and independent check | Concrete familiar exposure for Core2B comparison; application errors that may improve teaching/repair |
| Core2B - changed demand | A named familiar exposure (normally Core2A), the earlier teaching/prerequisite closure and reviewed source demand when relevant | Make a genuinely changed decision while transferring established knowledge; then inspect solution, rubric and repair | Evidence about transfer and new design weaknesses; feedback into Core1A/B, Core2A and the shared map |

Typical bank-first design: **Core2 demand map -> Core1 orientation -> Core1A/Core1B conceptual construction and reconstruction -> Core2A familiar application -> Core2B changed demand**.

Typical no-bank design: **Core1 source-grounded orientation -> Core1A/Core1B -> authored Core2A -> Core2B**. Continue source research; add Core2 when a real bank becomes available. Practice and transfer can be authored without a PYQ bank, with no claim about unobserved exam coverage.

The arrows describe what each design should explain. Authors can draft Core1A/B together, sketch a transfer task early to discover missing teaching, or investigate a difficult source question before finishing mappings. Record planned versus actually delivered exposure. Do not call an unseen parent "prior exposure" or an untested learner "demonstrated". An incomplete lineage is a visible review finding while useful authoring continues.

Core1A and Core1B share conceptual truth, not identical prompts. Core2A and Core2B share capability continuity, not interchangeable demands. Changing numbers, removing hints or adding a harder badge does not by itself establish transfer.

## 9. How first-stage findings guide later work

Reuse the first-stage source inventory, concept/Atlas references, uncertainty notes, difficulty-first triage and review feedback in the existing UNIT, DESIGN-NOTE and WORKLOG. These remain revisable evidence, not a frozen checklist. For each later Core, explain the specific learner decision, the existing records it uses and the experience it adds. No duplicate handoff schema or academic package is needed.

| First-stage finding | Useful downstream response |
|---|---|
| Unclear concept meaning or prerequisite | Research its explanation and representation in Core1A; elicit the key distinction in Core1B; refine Core1's orientation |
| Question difficulty comes from translation or a multi-step inference | Target that actual reasoning move with Core2A support; design a deliberate changed decision for Core2B if educationally useful |
| Repeated source family or missing source coverage | Make selection and omissions visible; vary practice thoughtfully; continue acquisition without inventing PYQ coverage |
| Figure, notation, source key or mapping uncertainty | Preserve the evidence and disagreement; investigate independently; carry the uncertainty to affected consumers while other work continues |
| Child's observed conceptual error | Link to a precise Core1A/B construction or repair, then try fresh application; record whether the observation was helped or independent |
| Child's observed execution error | Use a targeted Core2A check or worked step without automatically reteaching the whole concept |
| Useful interactive representation | Bind its existing resource to the concept and learning purpose; choose disclosure timing separately for each Core |
| HTML/PDF mismatch or answer leakage | Correct the shared projection/print behavior and identify affected renders; avoid topic-specific copies of the renderer |

A new bank, changed concept mapping, revised figure or altered familiar task may affect later outputs. Use existing input digests and record refs to identify affected reviews; label their evidence stale, retain the prior result and inspect the affected claims. Staleness guides attention and does not stop research or require rerunning unrelated work.

## 10. Research and thinking remain open

- Research the web and original sources as widely as useful. Repo examples, goldens, current taxonomy and an incomplete Atlas are starting points, not the limits of inquiry. Distinguish factual authority from inspiration for teaching.
- Think, derive, compare explanations, sketch figures and try alternative tasks before fitting results into fields. There is no mandatory research query list, source count, scaffold count, question count or improvement quota.
- Keep unexpected ideas and unresolved claims in the existing research log/design note, with evidence and a reasoned next step. A useful idea that lacks a schema field is a representation gap to investigate, not a reason to discard the idea or invent filler.
- At a canonical write boundary, preserve valid references and serialize accurately. If the current schema cannot express an insight, retain the full reasoning in the design note and propose the smallest shared extension. Do not mislabel the insight to fit a convenient enum. Schema limitations do not constrain exploration or independently solvable work.
- Separate unknown, unavailable, not applicable and contradicted evidence in prose. Do not give any of them a fake "complete" value. Missing learner observations mean unknown learner state; they do not prevent authoring a useful default experience.
- Apply every guideline with judgement and a brief explanation when an alternative serves the learner better. An independent reviewer can challenge both the artifact and the guideline. Record meaningful revisions and negative findings, not a transcript of every browser click.
- Use advisory local observations and actual artifacts. Add no new delivery blockers, CI workflows, schema completeness gates, publication authority or permission requests. The Owner's exact-render acceptance remains the publication decision.

## 11. Adoption in existing work processes

The method index and protocol point to this guidance. Unit-author and reviewer roles/prompts apply it to the chosen first stage and subsequent Cores. UNIT records the denominator, entry route and scope; DESIGN-NOTE records difficulty-first triage, interaction purpose, dependency/task arc and research; WORKLOG records lot/slice state, denominator coverage, outputs, findings, decisions and affected followups. Those existing documents provide the audit trail without a new ledger.

A practical session is: inspect available inputs; establish the denominator; choose the first-stage route; triage difficulty and interaction value; author/review the hardest worthwhile vertical slice; show actual HTML/PDF plus the complete denominator mapping/coverage view and gaps; incorporate feedback; continue Medium/Low coverage and expand learner decisions Core by Core. Repeat the research/design loop whenever evidence warrants it. No stage label, missing field, report outcome or reviewer score grants or denies permission to keep working.
