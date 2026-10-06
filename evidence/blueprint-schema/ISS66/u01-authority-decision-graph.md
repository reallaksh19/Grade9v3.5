# ISS66 U01 — authority graph and matched-run decision delta

**Responsibility:** #66 — blueprint/schema semantic-contract hardening  
**Protocol:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`  
**Observed integration basis:** `feat/issue29-integrated-core-templates@2b11f2143cf9fd96be44014bab57d4f1f53bad37`  
**Purpose:** establish what the merged shared contracts already do, what #49–#56 independently disagree about, and which planned changes are actually missing before coding later units.

## 1. Frozen matched-run bases

| Cohort | Set A | Frozen/head evidence | Set B | Frozen/head evidence |
| --- | --- | --- | --- | --- |
| D1 intended | #49 / PR #62 | `b9fabd22e588f295eddce3ba3286b7cead4d5139`; ledger blob `bc0ae903a77fdf7cc10a1debc2d60aad532c585b` | #53 / PR #59 | `bc464d831f4815a45dd45d29ecf6bcc16d5af8ab`; ledger blob `fb19160dc2ac0aedf666bee9eff3aed4fe773a87` |
| D2 intended | #50 / PR #63 | `a58eebee28112080393cc47e4295862efc43dbed`; ledger blob `ecd527733a6aab9b847e19667d75ef825138a567` | #54 / PR #57 | `3d17905ebee4ac6cf39057ac05d49947b1b50430`; ledger blob `9435a16f089b0e2f2d48ad7dd48ac072cd698828` |
| D3 intended | #51 / PR #64 | `b94ede24c7ba64ed36ba5f137b65d95816164599`; QRT blob `f07df3e5bb348019f17753fb3d14a8777c8fb62f` | #55 / PR #61 | `91951abc430ff50ae526110488d9b12e27e30af5`; QRT blob `131d9a8f3aa936e1cd8c1d2dc7acca6a54e581c6` |
| D4 intended | #52 / PR #60 | `2c373cebccddba0080d0513b11350ef692608fa0`; ledger blob `67833b07d526832caa4043f54542796d8d0079d9` | #56 / PR #58 | `40ca52786c0b5d0c400a5c730314a01689de836a`; ledger blob `f930c64a2b4b8274f8583e8f10c5d8ec313f7e72` |

All eight candidate PRs remain separate first-run evidence. This ledger does not rewrite their historical classifications.

## 2. Matched A/B classification delta

The same Q1–Q10 inputs inside each pair were compared on **derived band, primary demand and five-component total score** as recorded by each execution.

| Cohort | Band disagreements | Primary-demand disagreements | Score disagreements | Same band+demand cell | Exact band+demand+score |
| --- | ---: | ---: | ---: | ---: | ---: |
| D1 | 3/10 | 3/10 | 7/10 | 5/10 | 1/10 |
| D2 | 3/10 | 2/10 | 8/10 | 6/10 | 2/10 |
| D3 | 6/10 | 4/10 | 7/10 | 2/10 | 1/10 |
| D4 | 5/10 | 5/10 | 7/10 | 2/10 | 1/10 |

This is structural evidence that an intended cohort label and a complete author review do not make difficulty/QRT classification reproducible.

### Per-question cells

| Pair | Q | Set A | Set B |
| --- | --- | --- | --- |
| D1 | Q1 | D1 · RETRIEVE · 2 | D1 · EXPLAIN · 2 |
| D1 | Q2 | D1 · RETRIEVE · 2 | D2 · JUSTIFY · 4 |
| D1 | Q3 | D1 · APPLY · 1 | D1 · APPLY · 2 |
| D1 | Q4 | D1 · APPLY · 2 | D1 · APPLY · 2 |
| D1 | Q5 | D2 · REPRESENT · 3 | D2 · REPRESENT · 4 |
| D1 | Q6 | D2 · EXPLAIN · 3 | D2 · JUSTIFY · 3 |
| D1 | Q7 | D2 · MODEL · 4 | D2 · MODEL · 3 |
| D1 | Q8 | D1 · APPLY · 2 | D2 · APPLY · 3 |
| D1 | Q9 | D2 · JUSTIFY · 3 | D2 · JUSTIFY · 5 |
| D1 | Q10 | D2 · SYNTHESIZE · 5 | D3 · SYNTHESIZE · 6 |
| D2 | Q1 | D2 · EXPLAIN · 4 | D2 · EXPLAIN · 3 |
| D2 | Q2 | D2 · APPLY · 3 | D2 · APPLY · 3 |
| D2 | Q3 | D1 · APPLY · 2 | D2 · APPLY · 3 |
| D2 | Q4 | D2 · MODEL · 4 | D2 · MODEL · 4 |
| D2 | Q5 | D2 · REPRESENT · 4 | D2 · REPRESENT · 3 |
| D2 | Q6 | D3 · JUSTIFY · 6 | D2 · JUSTIFY · 4 |
| D2 | Q7 | D2 · SYNTHESIZE · 5 | D2 · APPLY · 4 |
| D2 | Q8 | D2 · JUSTIFY · 4 | D2 · JUSTIFY · 3 |
| D2 | Q9 | D2 · SYNTHESIZE · 5 | D2 · SYNTHESIZE · 4 |
| D2 | Q10 | D3 · JUSTIFY · 7 | D2 · EXPLAIN · 3 |
| D3 | Q1 | D2 · SYNTHESIZE · 5 | D3 · APPLY · 6 |
| D3 | Q2 | D3 · JUSTIFY · 7 | D3 · EXPLAIN · 7 |
| D3 | Q3 | D3 · JUSTIFY · 6 | D3 · JUSTIFY · 7 |
| D3 | Q4 | D2 · MODEL · 4 | D3 · MODEL · 6 |
| D3 | Q5 | D2 · REPRESENT · 5 | D3 · REPRESENT · 7 |
| D3 | Q6 | D3 · SYNTHESIZE · 6 | D3 · SYNTHESIZE · 6 |
| D3 | Q7 | D4 · JUSTIFY · 8 | D3 · JUSTIFY · 7 |
| D3 | Q8 | D4 · JUSTIFY · 9 | D3 · JUSTIFY · 7 |
| D3 | Q9 | D2 · SYNTHESIZE · 5 | D3 · EXPLAIN · 7 |
| D3 | Q10 | D3 · MODEL · 7 | D3 · JUSTIFY · 7 |
| D4 | Q1 | D3 · JUSTIFY · 6 | D4 · JUSTIFY · 8 |
| D4 | Q2 | D3 · SYNTHESIZE · 7 | D4 · SYNTHESIZE · 8 |
| D4 | Q3 | D4 · JUSTIFY · 8 | D4 · JUSTIFY · 9 |
| D4 | Q4 | D4 · SYNTHESIZE · 9 | D4 · EXPLAIN · 8 |
| D4 | Q5 | D3 · MODEL · 7 | D3 · MODEL · 7 |
| D4 | Q6 | D2 · EXPLAIN · 5 | D3 · EXPLAIN · 7 |
| D4 | Q7 | D3 · SYNTHESIZE · 7 | D4 · JUSTIFY · 8 |
| D4 | Q8 | D2 · SYNTHESIZE · 4 | D3 · APPLY · 7 |
| D4 | Q9 | D4 · JUSTIFY · 8 | D4 · SYNTHESIZE · 8 |
| D4 | Q10 | D4 · SYNTHESIZE · 8 | D4 · JUSTIFY · 8 |

## 3. Live shared authority graph

The merged tree currently resolves the relevant responsibilities as follows.

| Authority | Exact blob at launch | Current role / finding |
| --- | --- | --- |
| `Shared/web/interactive-page-blueprints.v1.json` | `592bffeb87ce283d62ea2479fa359a5278f4ee08` | Active page-shape policy. Core1A expanded policy is `SINGLE_PANE`. |
| `Shared/web/interactive-page-blueprint.schema.json` | `a306b926a6ea39db6090b0121b6c612246f3aa9b` | Allows `SINGLE_PANE`, `STAGE_SUPPORT`, `LIST_DETAIL`; structural blueprint validation. |
| `Shared/tools/web_blueprint_contract.py` | `96b15ae6fb68ff71a56d3696e1f53edef6a3fc25` | Selects exactly one active blueprint per role; component band lookup still reads a record-declared band. |
| `Shared/tools/render_core.py` | `e3ae6e074aa6b6d38a5671f03f629577809dce0c` | Sole learner Core renderer; consumes blueprint, case scenes and protected-support projection. |
| `tools/site-audit/layout-observation.mjs` | `cffd543b2120d5d977e6c8ec5b26ee10a90c4584` | PR #65 fix: measured `SINGLE_PANE` satisfies selected policy; other policies retain legacy column observation. |
| `Shared/quality/learner-quality.v1.json` | `98eee75334d27d7b107329c41eeeebcdf5fa1b13` | Quality contract consumes rendered observations; no longer needs to redefine Core1A layout independently. |
| `Shared/library/package.schema.json` | `e23af6c68c76d4991c119ea87c335ff70134e325` | Holds `question_difficulty`, `scene_instance`, and optional `core2_support_plan`. |
| `Shared/tools/core2_v2.py` | `4757d7add0b19a407f0c1cdd36f4bc5aec8c7c7f` | Resolves authored support completion against reasoning moves and derives pre-solution eligibility. |
| `Shared/quality/question-demand-matrix.v1.json` | `3779a53ae7d20efbb4644bc3f9243909e93dc145` | Defines 7 demands, band-protected work, H/S/P/M semantic objectives. Explicitly says Blueprint remains page-shape authority. |
| `Shared/tools/question_review_matrix.py` | `f9a8f7164daf7fb867beb0b972d6cc8179cc0a05` | Resolves QRT from `difficulty.band` + `cognitive_demand.primary`; it validates labels but does not derive them from component evidence. |
| `Shared/quality/qrt-pipeline-run.schema.json` | `beace40c74d657eb50416d5ae8918c17b70ce974` | Review basis currently `AUTHOR_ONLY | RENDERED`; rendered review requires artifact ref + artifact SHA. |
| `Shared/tools/qrt_pipeline_guard.py` | `8df677914c95db74a5934f977f0f3008663dbd14` | Author-only review receives no post-render credit; artifact bytes and head are verified; rendered review SHA must match artifact SHA. |

## 4. What PR #65 already solved

### 4.1 Presentation authority — already implemented, verify rather than redesign

`layout-observation.mjs` explicitly interprets the selected `responsive_policy.expanded`. For `SINGLE_PANE`, measured one-column articles satisfy the policy; for `STAGE_SUPPORT`, existing two-column observation remains required.

**U02 implication:** begin as a replay/verification unit. Do not add a second layout policy unless a remaining exact failure proves one is needed.

### 4.2 Review basis + rendered byte binding — partially implemented

The QRT schema already distinguishes:

- `AUTHOR_ONLY`: retained without rendered acceptance credit;
- `RENDERED`: requires `artifact_ref`, `artifact_sha256`, judgements.

The guard verifies:

- artifact path exists and is non-empty;
- actual file SHA equals declared artifact SHA;
- artifact `head_sha` equals run head;
- rendered review SHA equals referenced artifact SHA;
- author-only review does not satisfy `POST_RENDER_QRT_REVIEW`.

**Remaining gap for U03:** `RENDERED` says nothing about **review independence/identity**. A self-authored rendered review and an independent rendered review are structurally indistinguishable.

### 4.3 Question/case representation binding — already substantially present

`scene_instance` contains:

- `cores`;
- `datum_refs`;
- `asset_ref`;
- exactly one teaching/question binding through `microtopic_ref` or `question_ref`.

The staged-support regressions reject wrong owner/datum/asset/role bindings.

**U06 implication:** first prove whether any missing generic role/case semantics remain. Do not duplicate `scene_instance` under a new representation schema.

### 4.4 Protected support linkage — already substantially present

`core2_support_plan` contains:

- `protected_move_refs`;
- support rows with `completed_move_refs`;
- visual stages with `completed_move_refs`.

`core2_v2.project_support()` makes an authored support row pre-solution ineligible when it completes any protected reasoning move; visual support derives safe pre-attempt stages the same way.

**U05 implication:** the missing question is not “can support be deferred?” — that exists. The later unit must test whether the **state vocabulary and canonical learner-owned decision identity** are sufficient beyond the current pre-solution/attempted-solution split.

## 5. Gaps established by U01

### G1 — Difficulty/QRT is still authored-label driven

`question_difficulty` already requires five component scores, total score, band and basis. However:

- the schema does not distinguish an intended/requested cohort from the derived band;
- `question_review_matrix._question_band()` reads the stored `difficulty.band` directly;
- primary demand is similarly read from the stored cognitive-demand extension;
- no common resolver derives/validates band from the five component scores and shared band rule before selecting the QRT cell.

Given the matched-run delta above, this is the strongest unresolved shared-contract gap.

### G2 — Rendered review has no independence identity

The current `basis` is provenance of **artifact inspection**, not provenance of **reviewer independence**. `RENDERED` can still be self-review.

The contract needs either a separate reviewer/review-context dimension or a more precise basis model without breaking legacy rendered records.

### G3 — Diagnostic authoring is too weakly typed

Existing misconception structures contain `wrong_idea`, `diagnostic_prompt`, and `repair`, but do not structurally represent:

- expected discriminating responses/evidence;
- observed learner evidence;
- `CONFIRMED | INDETERMINATE`;
- recheck evidence.

The QRT M2 objective demands discrimination, but the canonical content record cannot currently prove that its diagnostic is discriminating.

### G4 — Protected support is linked to reasoning moves, but not yet a universal learner-decision object

PR #65's support plan is useful and should be reused. A later unit must determine whether `reasoning_move.id` is sufficient as the canonical protected act for all demand types/representations or whether a narrow shared decision reference is justified.

This is a replay question, not an automatic schema expansion.

## 6. Negative knowledge / rejected changes

- Do **not** introduce a second layout authority: the PR #65 layout reconciliation already makes blueprint policy authoritative for the observed conflict.
- Do **not** add a new question-instance representation system before proving `scene_instance.question_ref + datum_refs + asset_ref + cores` is insufficient.
- Do **not** add a second protected-support mechanism: `core2_support_plan` already links completion to reasoning moves and visual stages.
- Do **not** infer that a schema can settle the correct D-band or cognitive demand. It can make derivation inputs and disagreement explicit; academic adjudication remains separate.
- Do **not** promote the individual #49–#56 builder widget names into shared schema from U01 evidence.

## 7. U01 disposition

U01 is complete when this ledger is committed/read back together with the work report.

**Recommended next unit:** U02 is a **verification-first** unit. Re-run/inspect the merged presentation-authority behavior and add code only if an exact contradiction remains. If the existing PR #65 tests prove the declared U02 acceptance criteria, close U02 with `NO_CHANGE` plus exact evidence rather than manufacturing another layout change.
