# Motion in 2D RCA — 2026-09-20

## Incident

The Motion in 2D explorer was previously reported as repaired, but the repository and the supplied repaired HTML still exhibited the same learner-visible defects: generic or missing-looking answers, misleading simulator loading, weak use of traps/checks, and a Teacher's Chalkboard that did not operate as a per-question teaching surface.

This RCA treats the repository state as the source of truth rather than prior completion claims.

## Root causes

1. **The repaired artifact was not the live repository state.**  
   The main Motion in 2D bank still contained bucket-template final answers such as `Direct application of projectile formulas` and `Evaluate from coordinate kinematic equations`.

2. **The supplied HTML was not self-contained.**  
   It loads `jee_questions_data.js` as a sibling file. Opening or publishing only the HTML can therefore render the shell while losing the 104-question bank.

3. **The earlier Pages branch was incomplete.**  
   `audit/motion2d-simulator-pages` contains only the first seven compressed payload chunks (`app-000.b64` through `app-006.b64`) and no completed loader. It was never a deployable recovery path and no PR was opened from it.

4. **Two different "chalkboard" ideas were conflated.**  
   The original topic buttons drove six hard-coded SVG overlays, while question cards needed a question-specific teaching surface. The static overlays could not display each record's own derivation, audit disposition, teacher check, trap, transfer rule, or simulator fidelity.

5. **Simulator ingestion guessed values.**  
   `getQuestionSimulationParams` used regex extraction and then manufactured category defaults when a stem did not provide enough values. That made a generic demo look like a faithful question load.

6. **Topic hubs silently hid records.**  
   `renderInTabQuestions` used `filtered.slice(0, 6)`, so only six questions per filtered topic were rendered even when the badge advertised a larger count.

7. **A mathematical model error remained in the outfielder lab.**  
   The UI treated linearity of `tan(phi)` as linearity of `phi` and displayed an approximately zero second angular derivative. These are not equivalent.

8. **Static completion checks were too shallow.**  
   Syntax and DOM checks can pass while content is generic, a dependent data file is absent, or a simulator button injects invented values. The previous acceptance gate did not test the product contract.

## Repair implemented on `fix/motion2d-rca-content-simulator`

### Question bank

- 104 records are preserved.
- All known generic final-answer placeholders are removed.
- Every record now has:
  - `ans`
  - `formula`
  - `steps`
  - `takeaway`
  - `trap`
  - `teacherCheck`
  - `audit`
  - `simulation`
- Current audit status is intentionally conservative:
  - **62 verified**
  - **1 source-inconsistent** (`EXAM-20`)
  - **41 present-not-reaudited**
- The 41 retained records have specific existing answers and the required teaching metadata, but are **not** being mislabeled as independently re-solved in this pass.

Representative corrections include:

- `EXAM-04`: 15°/30° range ratio gives `x = sqrt(3)`; it is not a complementary-angle pair.
- `EXAM-32`: `a(1) = 30 j-hat cm/s^2`; the cubic coordinate must be differentiated instead of using constant-acceleration SUVAT.
- `PDF-12`: with wind from West, steering is **53.13° North of East**, not 36.87°.
- `PDF-04`: on the ideal catch course `tan(phi)=kt`, so `phi=atan(kt)` and `phi''` is generally nonzero.
- `EXAM-48`: the prior duplicated answer from another vector question is replaced by the evaluated direction `(2i+6j+9k)/11`.

### Teaching UI

The master question hub now makes the answer visible without requiring the learner to expand a derivation.

Each question exposes a real **Teacher's Chalkboard** with this sequence:

1. Governing model
2. Question-specific derivation
3. Final result / audit disposition
4. Independent teacher check
5. Trap / misconception diagnosis
6. Transfer rule
7. Simulator fidelity

The old topic-level SVG chalk buttons are renamed **Worked Example Overlay** so they are no longer presented as the per-question chalkboard.

Trap and teacher-check content are first-class visible cards in both the master hub and the in-topic hubs.

### Simulator contract

Question actions are now explicitly one of:

- **Exact Question Load**
- **Constraint-Faithful Demo**
- **Concept Demo**
- **Unavailable**

The simulator controller now reads only `q.simulation`. It does **not** regex-scrape a question and does **not** invent fallback speed, angle, height, gravity, river speed, or other values.

If a question has no faithful mapping, the UI says so instead of silently launching an unrelated sandbox state.

The current bank deliberately uses conservative Concept/Constraint mappings unless an exact parameter mapping is explicitly present.

### Rendering and integrity

- Removed the `slice(0, 6)` question truncation.
- Removed the duplicate static DOM id `sbTeacherChalk`.
- Added a visible bank-integrity failure banner if the external question data does not load or required fields are missing.
- Removed the blanket `100% Solved` UI claim and replaced it with per-item audit status.
- Corrected the outfielder lab wording so it no longer claims `phi'' ~= 0`.

## Regression protection

Extended the existing `tests/test_c6_examside_motion_in_plane.py` regression module with Motion2D explorer checks:

- exactly 104 unique records;
- required teaching/audit/simulator fields on every record;
- absence of known placeholder answers;
- specific regressions (`EXAM-04`, `EXAM-32`, `PDF-12`, `PDF-04`);
- explicit treatment of `EXAM-20` as source-inconsistent;
- presence of the question-specific chalkboard and integrity gate;
- no six-question truncation;
- no fabricated simulator fallback;
- unique static DOM IDs.

## Verification performed in this repair

Before committing `index.html`, the repair script verified:

- inline JavaScript parses successfully;
- no duplicate static DOM IDs remain;
- known generic answer text is absent from the HTML;
- the old fabricated simulator fallback is absent;
- the old false outfielder curvature message is absent;
- the six-question truncation is absent;
- the question-specific Chalkboard and fidelity UI exist.

The data-bank repair separately verified:

- 104 records parsed;
- zero known generic final-answer placeholders remain;
- zero records are missing the required content/audit/simulator fields.

## Remaining release gate

A real browser smoke test is still required before this should be called deployed or production-verified. The static and data-contract checks above passed, but this RCA does not substitute them for clicking the actual browser UI.

The incomplete `audit/motion2d-simulator-pages` branch is not used as a release artifact.
