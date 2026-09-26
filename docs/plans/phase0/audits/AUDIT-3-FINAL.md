# Audit 3 (final): blueprint, shell and web-standard compliance of the six Core pages

Issue: https://github.com/reallaksh19/Grade9V3/issues/298. Specimen:
`benchmarks/quality-calibration/specimens/S1-motion2d-six-core-html/`, from branch
`motion2d-six-core-20260926` at commit `d3fd51ab`. This is the audit record; nothing was
changed.

**Method**
- Rendered measurements: `node tools/site-audit/core-page-audit.mjs <dir> --json out.json`.
  It loads each page in Chromium at 1280×800, 800×1280 and 1180×820. The raw output is in
  `audit3-rendered-measurements.json`.
- Slot realization: judged from each page's DOM outline (headings, disclosures, attempt fields,
  figures) against the exact blueprint in `Shared/web/interactive-page-blueprints.v1.json`.
  A `data-blueprint-ref` attribute alone never counts.

**Status codes:** ✓ realized · ◐ partly realized · ✗ not realized.

**Gap-origin codes**
- **UNUSED:** the standard exists but the page does not use it.
- **MISSING:** no standard or implementation exists.
- **DIVERGED:** a renderer exists but the page was produced by another path.

## 1. Measured facts (identical at all three viewports)

| Page | Blueprint attribute | Slot markers | Controls < 48 px | Smallest text | Horizontal overflow | Figures (with title) | Disclosures | Attempt fields | Disclosures gated on attempt | JS | Home link |
|---|---|---|---|---|---|---|---|---|---|---|---|
| core1 | BP-CORE1-ORIENTATION | 0 | 15 / 15 | 12.5 px | 0 | 0 | 0 | 0 | — | 0 | none ("Preview" → index.html) |
| core1a | BP-CORE1A-CONSTRUCTION | 0 | 20 / 20 | 12.5 px | 0 | 5 (5) | 13 | 0 | — | 0 | none |
| core1b | BP-CORE1B-RECONSTRUCTION | 0 | 28 / 44 | 12.5 px | 0 | 5 (5) | 21 | 16 | 0 of 21 | 0 | none |
| core2 | BP-CORE2-SOURCE-QUESTION | 0 | 13 / 13 | 12.5 px | 0 | 0 | 0 | 0 | — | 0 | none |
| core2a | BP-CORE2A-SUPPORTED-APPLICATION | 0 | 17 / 22 | 12.5 px | 0 | 0 | 10 | 5 | 0 of 10 | 0 | none |
| core2b | BP-CORE2B-TRANSFER | 0 | 32 / 37 | 12.5 px | 0 | 5 (5) | 10 | 5 | 0 of 10 | 0 | none |

**Features on every page**
- Present: `<main>`, `<nav>` and `<header>`, one `<h1>`, the viewport meta tag, inline CSS only,
  and no external requests.
- Absent:
  - `<footer>`;
  - `:focus` styles (only browser defaults);
  - print CSS;
  - a sticky or fixed header;
  - a 68/32 stage-support layout (a single column, max 1040 px).

**Controls under 48 px:** every nav link is 37 px tall. Disclosure summaries are also under
48 px.

## 2. Blueprint slot realization

| Page | Slot | Blocks the blueprint accepts | Realized? | Observed |
|---|---|---|---|---|
| Core1 | identity | identity_scope | ✓ | h1 + "Scope and conventions" |
| | orientation | objects_conventions | ✓ | conventions list |
| | | canonical_representation | ✗ | only a list of explorer links; 0 figures |
| | | governing_relations, compact_anchor | ✗ | absent (A1-001) |
| | | hard_transition_map, exclusions_extensions | ✓ | three transition articles + extension map |
| | | orientation_closure | ◐ | exit prompts, no closure block |
| Core1A | identity | identity_entry_assumptions, convention_declaration | ✓ | "Entry assumptions" per concept |
| | construction | inferential_jump, completed_construction | ✓ | "Inferential jump", "Stepwise construction" |
| | | representation_bridge | ◐ | 5 of 8 concepts; R1–R3 print ids (A1-002) |
| | | worked_conceptual_anchor | ◐ | present; R3's does not exercise the construction (A1-004) |
| | repair_closure | plausible_wrong_path, diagnose, repair | ✓ | present for all 8 (as lists) |
| | | independent_checks | ◐ | R1 prints "None supplied" (A1-003) |
| | | exit_task_closure | ✓ | exit task + "Model answer" disclosure |
| Core1B | identity | identity_concept | ✓ | |
| | attempt | predict, attempt | ✓ | PREDICT + textarea |
| | reconstruction | reconstruct … rejoin_inferential_jump | ◐ | content complete; "open after your attempt" is text only, and the disclosure opens without an attempt (A3-004) |
| Core2 | identity | source_identity_provenance | ✓ | exam, paper and question number; custody notes |
| | attempt | source_question, source_figure | ◐ | restatement present; every figure is "None supplied" (A1-012) |
| | support | source_hint_ladder | ◐ | "Source hints only" heading; none supplied |
| | solution | source_answer_rubric, custody_status | ✗ as a slot | answer and reasoning inline, not learner-openable (A1-006) |
| Core2A | identity | family_identity_provenance | ◐ | an AUTHORED_PRACTICE label; no family identity |
| | attempt | question, initial_representation | ◐ | question ✓, representation ✗ (A1-007) |
| | support | pedagogical_scaffolds, application_crux, bound_representation | ◐ | one generic scaffold (A1-008); no representation |
| | reasoning | route … exposure_family_closure | ◐ | route, solution and check ✓; closure ✗ (A1-009); failure signal hard-coded |
| Core2B | identity | question_prior_exposure | ✓ | lineage links |
| | attempt | safe_initial_representation | ✗ | no pre-attempt figure (A1-010) |
| | | safe_pre_attempt_support | ◐ | the same generic sentence on all 5 tasks |
| | | attempt_commitment | ✓ | "Commit before support" textarea |
| | post_attempt | support … lineage_continuity_check | ◐ | changed demand, protected move, route, answer and rubric ✓; lineage check ✗ (A1-011); disclosure not gated on commitment (A3-004) |

## 3. Findings

| ID | Scope | Required policy | Observed | Severity | Systemic? | Gap origin |
|---|---|---|---|---|---|---|
| A3-001 | all six | Standalone page with an obvious, persistent link to the app home | The only "home" is `Preview` → `index.html`, a sibling preview page. There is no app-home link, and the pages break as standalone products | S1 | systemic | MISSING in the generator; the shell standard exists (`G9-TABLET-SHELL-V1`: HOME, BACK, SEARCH, …) but is UNUSED |
| A3-002 | all six | `G9-TABLET-SHELL-V1` fixed header with BACK, HOME, SUBJECT_CONTEXT, QUESTION_BANK, SEARCH, REFRESH, DISPLAY and OVERFLOW | No shell: a static pill nav that scrolls away, with none of those controls | S1 | systemic | UNUSED. No shared shell implementation exists that a page could include; `public/js/site-header.js` is the site header and its search is broken site-wide (T1 in the tablet spec, PR #295) |
| A3-003 | all six | Blueprint slots rendered as structure | 0 slot markers; `data-blueprint-ref` on `<body>` is the only link to the blueprint | S1 | systemic | DIVERGED: `core-learning-page.mjs` emits `data-blueprint-slot` sections; the pages came from a separate generator |
| A3-004 | Core1B, 2A, 2B | `attempt_before_reveal`; Core1B forbids `ANSWER_BEFORE_ATTEMPT`; Core2B forbids pre-attempt disclosure of the protected move | Every reveal (reconstruction, boundary answer, solution, post-attempt review) is a plain `<details>`, openable with an empty attempt: none of the 41 disclosures on these pages is gated. "Open after your attempt" is an instruction, not a control | S1 | role-wide | DIVERGED: the blueprint renderer gates the solution behind a stateful button; the pages have no JS |
| A3-005 | Core2 | `solution_policy: LEARNER_OPENABLE` | The solution is not behind any control | S1 | page | DIVERGED (same cause as A1-006) |
| A3-006 | all six | `minimum_target_css_px: 48` | 125 of 151 controls under 48 px, including every nav link (37 px) and summary | S2 | systemic | UNUSED: the policy is in every blueprint; the generator CSS ignores it |
| A3-007 | Core1A, 1B, 2, 2A, 2B | `responsive_policy.expanded: STAGE_SUPPORT`, 0.68/0.32 | A single column at every viewport; no stage/support split on a 1280 px tablet | S2 | systemic | UNUSED |
| A3-008 | Core2A, 2B | `progressive_support: true` | One support disclosure per question; no levels (A1-008) | S2 | role-wide | MISSING in the data (one scaffold) and DIVERGED in rendering |
| A3-009 | all six | Accessibility: focus states, landmarks | No `:focus` styles (browser defaults only); no `<footer>`. SVGs carry titles, plus an "Accessible element list" | S3 | systemic | MISSING: no page-level accessibility standard beyond the blueprint's "no hover-only information" rule (which the pages meet) |
| A3-010 | all six | Readable text on a 10-inch tablet | Smallest text 12.5 px (eyebrows, provenance, captions); body text 16 px | S3 | systemic | MISSING in the blueprints (no minimum text size); the tablet spec in PR #295 sets 14 px |
| A3-011 | all six | Print secondary to HTML; PDF comes from the page | No print CSS. The PDFs (specimen S2) were generated separately with ReportLab: text only, 0 images, 0 drawing operators | S2 | systemic | DIVERGED: a second render path for print |

**Packaging, as observed rather than tested per mode:**
- The pages are self-contained: inline CSS, no JS, no external requests, and relative links
  only to siblings.
- OFFLINE_DIRECTORY works.
- SINGLE_FILE works per page, but sibling links break.
- EMBED and PUBLIC/PAGES routing (portal and site-map entry) are not provided. The pages are
  not reachable from the portal (compare the site audit baseline in PR #295: ORPHAN pages).

**Pass (no finding):**
- no horizontal overflow at any viewport;
- figures scale and carry titles;
- no hover-only information;
- one `<h1>` with an h2/h3 hierarchy;
- no JS errors;
- no external runtime dependencies.

## 4. Compliance matrix

| Dimension | Core1 | Core1A | Core1B | Core2 | Core2A | Core2B |
|---|---|---|---|---|---|---|
| Slot realization | ◐ | ◐ | ◐ | ✗ | ◐ | ◐ |
| Attempt / reveal policy | n/a | ✓ (exit answer in disclosure) | ✗ not gated | ✗ inline | ✗ not gated | ✗ not gated |
| Progressive support | n/a | n/a | ◐ | ✗ | ✗ | ✗ |
| Representations | ✗ | ◐ | ◐ | ✗ | ✗ | ✗ (post-attempt only) |
| Shell / app home | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Touch (48 px) | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |
| Responsive policy | ✓ (single pane) | ✗ | ✗ | ✗ | ✗ | ✗ |
| Overflow | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Accessibility | ◐ | ◐ | ◐ | ◐ | ◐ | ◐ |
| Print from page | ✗ | ✗ | ✗ | ✗ | ✗ | ✗ |

## 5. Shared-shell and role-specific gaps

- **Shared shell (fix once for all Cores):** A3-001, A3-002, A3-006, A3-009, A3-010, A3-011.
  - These belong to one shell implementation.
  - The tablet shell spec (`docs/specs/TABLET-SHELL-AND-NAVIGATION.md`, PR #295) covers the
    header, home, search, display and tap targets.
  - The rebuild plan's Phase 3 makes Core pages use it.
- **Role-specific (fix in the blueprint renderer):** A3-003, A3-004, A3-005, A3-007, A3-008.

## 6. Existing standards and missing standards

- **Existing but unused, or diverged from:**
  - blueprint slots and interaction policies;
  - the touch policy;
  - the responsive policy;
  - the shell id `G9-TABLET-SHELL-V1`;
  - the blueprint renderer's slot and gating code.
- **Missing standards:**
  - a shell *implementation* that Core pages include;
  - a minimum text size;
  - focus-state and landmark rules;
  - print-from-page as the only PDF path;
  - per-mode packaging tests;
  - a rendered check that a page realizes its blueprint.

  The last one is the Phase 4 rendered gate. `tools/site-audit/core-page-audit.mjs` is its
  measurement seed.
