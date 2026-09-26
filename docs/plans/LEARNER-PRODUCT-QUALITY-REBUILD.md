# Plan: rebuild learner-product quality across subtopics and subjects

Status: proposed · Inputs: audits reallaksh19/Grade9V3#296 (academic), #297 (process), #298
(HTML/blueprint), the Motion-in-2D six-Core product on `motion2d-six-core-20260926`, and the
owner's two quality references (the compiled Core1A textbook PDF and the tablet question-bank
HTML).

This is not a fix for Motion in 2D. The Motion-in-2D product is the **specimen** that shows
how the system fails. Every phase below changes a shared contract, data model, tool or role
so that the same failures cannot reach a learner in any subtopic of Physics, Mathematics or
Chemistry.

---

## 1. Why the output was poor (system level)

| # | Systemic cause | How it showed in the specimen |
|---|---|---|
| C1 | **"Complete" meant structurally present.** Contracts name each Core's blocks and slots, but nothing states how deep a block must be. The no-escape policy then pushed agents to fill every slot with something rather than stop. | Core1 is thin; the projectile construction is over-compressed; a single generic scaffold appears in every Core2A question |
| C2 | **Many renderers, none enforced.** The engine (projection, blueprint, `build_interactive_page`) exists, yet three parallel renderers were written: `learner_product_render.py` (#290), `build_motion2d_projectile_product.py` and a ReportLab PDF script. Each silently drops or flattens what the blueprint requires. | Core2 has no attempt step; the Core2B visual appears only after the attempt; "None supplied by the governed record" is printed; the PDFs contain no figures |
| C3 | **The data model cannot hold depth.** A microtopic has one `teaching_path`, and a question has at most a few scaffolds. There is no place for staged construction units, per-step representations, question-specific hint ladders, independent checks or cross-subject prerequisite bridges. | R1–R3 have representation IDs but no drawable scene; there are no maths bridges (derivative, trigonometry, exponential) |
| C4 | **Checks inspect metadata, not the rendered experience.** Tests assert IDs, markers and ordering strings. `core_template_contract` and `web_blueprint_contract` validate the contracts but never the produced pages. | The validation report says `visual_binding: PASS` on the strength of prose |
| C5 | **Self-attestation.** The agent that built the product wrote its own validation report. No independent verifier exists for products (only for library evidence). | Every check reads PASS while Audit 1 finds 11 defects |
| C6 | **Two disconnected pipelines.** The cited research library (evidence, staging, verification) and product building never meet, so products are authored from memory-grade package fields. | The product's extension package duplicates the research library's verified extension work |
| C7 | **Quality references were never encoded.** The owner's references define the expected depth, but they exist only as files a human reads. | Nothing measurable pushed the product toward the textbook's staged visual construction or the question bank's progressive hint ladder |

---

## 2. Target architecture (one path, every subject)

```
syllabus spine ─▶ RESEARCH (cited evidence cards) ─▶ AUTHOR (staging records, depth units)
      ─▶ ILLUSTRATE (representation scenes) ─▶ VERIFY (independent) ─▶ PROMOTE (canonical library)
      ─▶ COMPILE (Core projections, all six roles) ─▶ RENDER (blueprint renderer, one per role)
      ─▶ QUALITY GATE (rendered DOM + quality contract + continuity) ─▶ PUBLISH (web; PDF = print of web)
```

Invariants:

1. **Learner products are compiled, never hand-authored.** The only authored inputs are
   library records and representation scenes.
2. **There is one renderer per Core role**, driven by the blueprint. A required input that is
   missing is a **build error that becomes a named duty**, never fallback text.
3. **Quality is data.** A subject-neutral quality contract states the minimum depth per role
   and block. Subject adapters supply only vocabulary: what counts as a representation, a
   check or a model condition in that subject.
4. **Gates run on what the learner sees**: the rendered DOM in a browser. Metadata alone
   passes nothing.
5. **Nobody grades their own work.** Validation reports are written by tools and by an
   independent verifier, never by the builder.

---

## 3. Phases

Each phase ends with an exit gate. Later phases do not start until the gate passes. Phase
outputs are shared: none is specific to Motion in 2D.

### Phase 0 — Freeze, inventory and baseline

- Stop generating new learner products until Phase 4.
- Finish Audits #296–#298 as evidence (they are the acceptance baseline).
- Inventory every renderer and product path in the repository: engine, `learner_product_render.py`,
  `Physics/tools/build_motion2d_projectile_product.py`, ReportLab PDF scripts, hand-written
  `product.v1.json` files and any per-topic generators. Mark each as **KEEP** (the engine) or
  **RETIRE**.
- Freeze the specimen products and the two owner references as a **calibration corpus**
  (`benchmarks/quality-calibration/`):
  - Negative specimens: the Motion-in-2D product, #288 and #290 outputs.
  - Positive references: the owner's two files, stored in local or private custody if
    copyrighted, with only the extracted grammar committed.

**Exit gate:**
- the three audits are closed with final matrices;
- the renderer inventory is committed;
- the calibration corpus is in place.

### Phase 1 — Learner Product Quality Contract (subject-neutral)

> **Status (2026-09-26):** built and calibrated. See [phase1/QUALITY-CONTRACT.md](phase1/QUALITY-CONTRACT.md).
> R2 passes its grammar and all 28 audited findings are caught. R1 is not located, and the
> owner's calibration review is pending.

Turn the owner's references and the audit findings into a machine-readable contract,
`Shared/quality/learner-quality.v1.json`, validated by `Shared/tools/quality_contract.py`.
It extends the existing `LEARNER-PRODUCT-TEMPLATES` blocks with **depth rules**, for example:

| Role | Required per unit (examples of the kind of rule, final values calibrated in this phase) |
|---|---|
| Core1 | For every microtopic: scope sentence, named quantities, **governing relation with meaning and validity condition**, one compact anchor and one pointer to Core1A/1B. Relations and anchors must be materially present, not just named. |
| Core1A | For every microtopic: **≥ 1 construction unit per distinct decision/event** in the inferential jump (a decomposition rule: e.g. model selection, apex, same-height return, unequal-height landing are separate units when the jump contains them). Each unit has a staged representation (≥ 2 reveal stages), reasoned steps (each step with "why valid"), and a worked anchor that exercises **that unit's** move, wrong path → diagnose → repair, a non-empty independent check, and an exit task with a model answer. |
| Core1B | The same units as Core1A (coverage parity is enforced). Each has predict → attempt → reconstruct → diagnose → repair → boundary test; no reveal before commitment; a representation available pre-attempt in a **safe stage** (no protected content). |
| Core2 | For every source item: identity, verbatim/faithful stem and conditions, a question-aligned representation where the source has a figure or the demand is spatial, **an attempt slot**, source hints only if the source has them, and the answer/working **behind a reveal**. |
| Core2A | For every item: a question-aligned representation, a **question-specific hint ladder of ≥ 3 rungs** (orientation → model/representation → first executable relation), a complete reasoning route with crux, answer, independent check, a failure signal and repair pointer specific to that item, and an explicit family/exposure record. |
| Core2B | For every item: explicit prior-exposure lineage to named Core1A/1B/2A units; an **invariant-versus-changed** statement; a safe pre-attempt representation; commitment before the protected DECIDE move; full rubric, independent check and repair route. |
| All | No fallback or placeholder text; every visual has a title and description and is bound to a representation record; every prompt closes without a tutor. |

Contract structure:

- **Subject adapters** (`<Subject>/adapter/QualityVocabulary.json`) define the subject's kinds
  of representation (for example, free-body diagrams, graphs, structural formulas, number
  lines), check types (units, dimensions, limiting cases, back-substitution, conservation)
  and prerequisite domains.
- **Calibration against the corpus:** the positive references must pass and every negative
  specimen must fail, with findings that match Audit 1's IDs. Thresholds are tuned until
  both hold.

**Exit gate:**
- `quality_contract.py` rejects every negative specimen for the right reasons and accepts
  the reference grammar;
- a Mathematics and a Chemistry sample unit are expressible in the contract without changing
  its schema.

### Phase 2 — Canonical data model that can hold depth

Extend `Shared/library/package.schema.json` (with a version bump and a migration tool) so that
records can carry what Phase 1 requires:

- **`construction_units[]` on microtopics:** each unit has an ordered decision/event,
  steps with justifications, a representation ref with reveal stages, a worked anchor ref,
  wrong path/diagnose/repair, independent checks and an exit task. `teaching_path` is
  migrated into units.
- **Representation scenes:** declarative, subject-neutral scene specifications (elements,
  labels, stages, invariants), rendered to accessible SVG by one shared scene renderer
  (building on `Shared/publication_host/drawing.py`). The engine holds no subject geometry;
  subjects contribute scene templates as data.
- **Questions:** `hint_ladder[]` (rungs with purpose, provenance and reveal order),
  `representation_ref`, `independent_check`, `failure_signal`, `repair_ref`, and a
  `family_exposure` closure record.
- **Cross-subject prerequisite capabilities:** Physics extensions may require Mathematics
  capabilities (derivative as rate, trigonometric resolution, exponential decay). The graph
  already supports prerequisites. Allow and require cross-subject refs, and have the
  planner emit `TEACH_PREREQUISITE_BRIDGE` for them.
- **Migration report:** run over every existing package (Physics, Mathematics, Chemistry).
  Every missing depth field becomes a named duty on the research board. Nothing is silently
  defaulted.

**Exit gate:**
- the schema and migration are merged;
- every package loads;
- the board shows a duty for every depth gap across all subjects.

### Phase 3 — One pipeline, one renderer

1. **Merge the pipelines.** The research library (evidence → staging → verification) becomes
   the **only** way content enters the canonical library. Promotion from staging to canonical
   is a tool step (`promote_verified.py`) that requires a current verification and a passing
   quality-contract check on the records.
2. **Blueprint renderer.** A single `Shared/tools/render_core.py` renders any Core role from
   its projection and its blueprint, and only through the blueprint's slots. It produces
   every packaging mode (PUBLIC, PAGES, OFFLINE_DIRECTORY, SINGLE_FILE, EMBED) and the tablet
   shell (`docs/specs/TABLET-SHELL-AND-NAVIGATION.md`). Missing required input raises a
   typed error that the board turns into a duty.
3. **PDF equals print of the web page**, through headless Chromium with a print stylesheet.
   There is no separate PDF generator.
4. **Retire** every renderer marked RETIRE in Phase 0, and add a guard test that fails if a
   new learner-page generator appears outside `render_core.py`. The existing Core1 learning
   host and interactive pages are migrated onto it.
5. **Product manifests** (which units, which questions, which order) replace hand-written
   product JSON. They are derived from the spine and the owner's question set, and hold
   selection only, never content.

**Exit gate:**
- all existing pages regenerate through `render_core.py`;
- the retired renderers are deleted;
- the guard test is green;
- PDFs are produced by print.

### Phase 4 — Gates on the rendered learner experience

1. **Rendered quality gate** (`Shared/tools/quality_gate.py`, driving Chromium) runs on every
   built page:
   - every required slot and block is present in the DOM in blueprint order;
   - the reveal state holds in the rendered page (answers are hidden until the learner acts);
   - every visual is actually rendered, bound to a representation and accessible;
   - the depth rules of the quality contract hold;
   - no placeholder or fallback strings appear (a generic rule, not a word list);
   - tablet layout rules (from the tablet spec) hold.
2. **Cross-Core continuity checker:** every unit and question family is traced through
   Core1 → 1A → 1B → 2A → 2B. Terminology, conditions and representations must agree.
   Core2B prior-exposure refs must resolve to rendered units.
3. **Independent product verifier role:** a verifier agent audits a sample of units against
   the owner rubric (derived from Audits 1 and 3) and records findings as duties. It may not
   have built the product.
4. **Tool-written validation reports only.** A report states which checks ran, on which
   digests, with their outputs. Free-text PASS claims are rejected by schema.

**Exit gate:**
- the calibration corpus's negative specimens fail the gate with findings matching Audits 1
  and 3;
- regenerated positive material passes;
- the gate runs in CI.

### Phase 5 — Agent system and prompts aligned to the contract

- **Roles:** Researcher, Author, Illustrator (representation scenes), Verifier. The Scanner is
  a local researcher. The Builder is a tool, not an agent.
- **New duties** in `research-first.v1.json`:
  - `AUTHOR_CONSTRUCTION_UNITS`
  - `AUTHOR_REPRESENTATION_SCENE`
  - `AUTHOR_HINT_LADDER`
  - `TEACH_PREREQUISITE_BRIDGE` (cross-subject)
  - `CLOSE_FAMILY_EXPOSURE`
  - `STATE_TRANSFER_INVARIANTS`

  Each duty names the exact record fields and quality-contract rules it satisfies.
- **Prompts** (`template/library-agents/`, the stress prompts and the composer) define
  "complete" as passing the quality contract and the rendered gate. They include the
  calibration grammar as examples. The stress prompt's acceptance section is replaced by the
  gates.
- **Board stages** extend to units, scenes and products, and are still derived from files only.
- **Budget and cost controls:** per-role token and cost ceilings per node, logged on the
  board.

**Exit gate:**
- a dry run on one new subtopic produces zero "complete but thin" items: the gate catches
  any, and the board routes them back automatically.

### Phase 6 — Pilot across subjects

Run the full pipeline end-to-end, from spine to published pages, on four units chosen to
stress different shapes of content:

| Subject | Unit | Why |
|---|---|---|
| Physics | Motion in a Plane (R1–R3 + extensions) | The specimen; compare directly with Audits 1 and 3 |
| Physics | Laws of Motion (friction / connected bodies) | Force diagrams, a different representation family |
| Mathematics | Linear equations or vectors | Symbolic manipulation, number-line and graph representations |
| Chemistry | Mole concept | Proportional reasoning, particle and quantity representations |

**Acceptance:**
- Audits #296 and #298 are re-run on the pilot outputs with no S0/S1 findings;
- the owner reviews one unit per subject against the references;
- measured cost and time per unit are recorded.

### Phase 7 — Scale-out and backfill

- Work the board chapter by chapter per subject, driven by the syllabus spine (Classes 9–11,
  JEE extensions).
- Backfill: every existing published product is regenerated through the pipeline or
  withdrawn from navigation.
- **Ratchets:** quality-gate findings and the site navigation audit may only go down, and
  tests fail on regressions.
- A monthly owner sampling review (about 5% of new units) feeds calibration updates back
  into the Phase 1 contract, which is versioned. Existing products are re-gated on each
  contract change.

---

## 4. What is retired

| Item | Replaced by |
|---|---|
| `Shared/tools/learner_product_render.py`, `delivery_gate.py` (research-first renderer and gate, #290) | `render_core.py` + `quality_gate.py` (Phase 3/4); keep `raw_intake.py` as intake |
| `Physics/tools/build_motion2d_projectile_product.py`, `Physics/content/*/product.v1.json` (hand content) | Library records + product manifest + `render_core.py` |
| ReportLab/other PDF generators | Print of rendered web pages |
| Free-text validation reports | Tool-written reports (Phase 4) |
| Parallel extension packages outside the research pipeline | Promoted, verified records only |

## 5. Owner decisions (answered 2026-09-26)

1. **Phase order and freeze:** approved. See [phase0/FREEZE.md](phase0/FREEZE.md).
2. **Quality references:** they live in the repository and agents search for them. The tablet
   question bank (R2) is pinned by commit in `benchmarks/quality-calibration/manifest.v1.json`.
   The compiled Core1A textbook (R1) is on no branch today, so its grammar is encoded there and
   agents re-search before each calibration run.
3. **Reviewer:** the owner reviews calibration (Phase 1) and pilot units (Phase 6).
4. **Sources:** `cdnbbsr.s3waas.gov.in` (NTA's CDN) is Tier A. When no official copy of a
   question or answer key can be pinned, a Tier C copy counts as *secondary* authority only if
   the official attempt is recorded and at least two other Tier C publishers carry the same
   stem or answer. Tier C publishers: ExamSIDE, ALLEN, Aakash, Resonance, MathonGo, Vedantu,
   Shaalaa. `evidence_check.py` enforces this, and pages label such questions as secondary.
5. **Cost ceiling per unit (still open).** Agents are paid per token, so every subtopic costs
   money to research, author, verify and render. The ceiling is the most the owner is willing
   to spend on one subtopic (one "unit": its six Cores and question set) before the board
   reports it for a look. It is not a stop state: the unit keeps its place, and the board shows
   the spend next to the quality result so a runaway loop (an agent retrying the same failing
   gate) is visible early. For scale, the Physics researcher pilot pinned 15 nodes for about
   US$10.50, roughly $0.70 per node. Proposed default: **US$15 per unit across all roles**
   (researcher $5, author $4, verifier $3, rendering and gate retries $3), reported on the board
   at 100% and escalated to the owner at 200%. Phase 5 implements the logging.
