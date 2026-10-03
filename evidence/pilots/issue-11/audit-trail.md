# Issue #11 — Surface Areas and Volumes pilot audit trail

Status: execution artifact; **not a release certification**. Final release/audit is intentionally separate.

## 1. Chronology and owner clarification

1. Issue #11 supplied the verbatim Grade 9 Mathematics prompt with Q1–Q10 and required learner-facing Core2/Core1A HTML plus machine-readable QRT evidence.
2. PR #9 short-prompt preflight was inspected at head `0fd5625ca1ab99365da666a5c1731c52605dfaca`. The implementation requires only learner knowledge, provenance, and product intent before authoring.
3. Owner answer in chat: `DEMONSTRATED`, `OWNER_SUPPLIED`, `PRESERVE_OWNER_QUESTIONS`.
4. Decision-changing interpretation: `DEMONSTRATED` was supplied without idea names. The run therefore applies that state only to the prerequisite ideas actually used by Q1–Q10 (basic area, radius/diameter, circle area, Pythagoras, rectangular-prism volume, percentage, m³↔L, sphere volume, ratios). It does **not** mark the six newly authored target capabilities as already demonstrated.
5. Provenance decision: `OWNER_SUPPLIED`. No exam, year, paper, textbook, or external source identity is asserted or researched because owner-supplied wording is custody in its own right.
6. Product-role decision: `PRESERVE_OWNER_QUESTIONS` routes to Core2 and `BP-CORE2-SOURCE-QUESTION@1.5.0`.

Evidence: Issue #11; `docs/method/QRT-SHORT-PROMPT.md`; `Shared/workflows/qrt-short-prompt.v1.json`; `Shared/tools/qrt_short_prompt.py`; `tests/test_qrt_short_prompt.py`; Issue #11 owner-clarification comment.

## 2. Provenance, custody and canonical mapping

- Owner questions live in an owner-supplied bank and retain verbatim stem digests under `grade9v3:source_custody.authority_class=OWNER_SUPPLIED_RAW_INPUT`.
- No source hints were supplied; therefore `hints[]` is empty. All guidance is authored separately in `scaffolds[]`.
- No existing Surface Areas and Volumes canonical Mathematics package was present in the inspected PR #9 tree. Six target capabilities and six Core1A microtopics are therefore marked `CANDIDATE`, not silently treated as reviewed curriculum authority.
- The owner’s demonstrated prerequisites are serialized in `evidence/pilots/issue-11/learner-profile.json` with `measured_fit_claim=false`.

Candidate target capabilities:

| Capability | Core1A microtopic | Main questions |
|---|---|---|
| `CAP-I11-SURFACE-SELECTION` | `MIC-I11-SURFACE-BOUNDARY` | Q1, Q2, Q3, Q5, Q7 |
| `CAP-I11-CONE-SLANT-SURFACE` | `MIC-I11-CONE-SLANT` | Q4 |
| `CAP-I11-COMPOSITE-EXPOSED` | `MIC-I11-COMPOSITE` | Q6 |
| `CAP-I11-CAPACITY-CONVERSION` | `MIC-I11-CAPACITY` | Q8 |
| `CAP-I11-RECAST-CONSERVATION` | `MIC-I11-RECAST` | Q9 |
| `CAP-I11-CONE-CYLINDER-RATIO` | `MIC-I11-RATIO` | Q10 |

## 3. Per-question academic and QRT decisions

Difficulty component order below is `concept/model, representation, reasoning chain, algebra/computation, trap/exception`; each component is 0–2 and the score is their sum. Bands follow the repository vocabulary: D1 0–2, D2 3–5, D3 6–7, D4 8–10.

| Q | Components → score/band | Primary / secondary demand | QRT cell | Stable crux / protected work | Verified answer | Figure decision |
|---|---|---|---|---|---|---|
| Q1 | `0/0/0/1/0` → 1/D1 | `APPLY` / — | `QRT-APPLY-D1` | Recognize that total surface area of a cube counts all six congruent square faces. | 294 cm². | Useful: `REP-I11-Q1-CUBE`; first stage is pre-attempt-safe. |
| Q2 | `1/1/1/1/1` → 5/D2 | `APPLY` / REPRESENT | `QRT-APPLY-D2` | Convert the stated diameter to the radius required by the cylinder curved-surface formula before substituting. | 280π cm², which is 880 cm² if π = 22/7. | Useful: `REP-I11-Q2-DIAMETER`; first stage is pre-attempt-safe. |
| Q3 | `1/1/1/1/1` → 5/D2 | `MODEL` / APPLY | `QRT-MODEL-D2` | Model an open cylindrical bucket as one curved surface plus one circular base, with no top circle. | 301π cm², which is 946 cm² if π = 22/7. | Useful: `REP-I11-Q3-OPEN`; first stage is pre-attempt-safe. |
| Q4 | `1/1/2/1/1` → 6/D3 | `SYNTHESIZE` / APPLY | `QRT-SYNTHESIZE-D3` | Use the radius and vertical height as perpendicular legs to obtain slant height before computing the open cone's curved canvas area. | Slant height = 25 m; canvas area = 175π m², which is 550 m² if π = 22/7. | Useful: `REP-I11-CONE-SLANT`; first stage is pre-attempt-safe. |
| Q5 | `1/1/1/1/1` → 5/D2 | `EXPLAIN` / APPLY | `QRT-EXPLAIN-D2` | Interpret 'inner surface of a hemispherical bowl' as the curved hemispherical surface only; the open circular mouth is not a material base. | 220.5π cm², which is 693 cm² if π = 22/7; the circular base is not included because the bowl is open there. | Useful: `REP-I11-HEMISPHERE`; first stage is pre-attempt-safe. |
| Q6 | `2/1/2/1/1` → 7/D3 | `SYNTHESIZE` / MODEL, APPLY | `QRT-SYNTHESIZE-D3` | Identify the hidden circular join and sum only the cone's curved surface and hemisphere's curved surface after finding the cone slant height. | 68.25π cm², which is 214.5 cm² if π = 22/7. | Useful: `REP-I11-COMPOSITE`; first stage is pre-attempt-safe. |
| Q7 | `1/1/1/1/1` → 5/D2 | `MODEL` / APPLY | `QRT-MODEL-D2` | Translate the painting instructions into exactly two included surfaces: the outer curved wall and the outside of the bottom base. | 399π cm², which is 1254 cm² if π = 22/7. | Useful: `REP-I11-Q7-PAINT`; first stage is pre-attempt-safe. |
| Q8 | `1/1/1/1/1` → 5/D2 | `APPLY` / REPRESENT | `QRT-APPLY-D2` | Keep the volume unit coherent while taking 75% of the tank volume and converting cubic metres to litres. | 2700 litres. | Useful: `REP-I11-CAPACITY`; first stage is pre-attempt-safe. |
| Q9 | `2/0/2/1/2` → 7/D3 | `SYNTHESIZE` / EXPLAIN | `QRT-SYNTHESIZE-D3` | Choose volume, not surface area, as the conserved quantity in recasting and use the cube of the radius ratio. | 27 smaller spheres; surface area is not conserved because recasting preserves material volume, while creating more pieces changes the total exposed surface. | Useful: `REP-I11-RECAST`; first stage is pre-attempt-safe. |
| Q10 | `1/0/1/0/1` → 3/D2 | `EXPLAIN` / APPLY | `QRT-EXPLAIN-D2` | Use the shared factor πr²h to see that a cone with the same radius and height has one-third the cylinder's volume. | 308 cm³; the radius and height are unnecessary because the cone and cylinder share the same πr²h factor. | Useful: `REP-I11-RATIO`; first stage is pre-attempt-safe. |

### Solution and checking policy

- Exact forms in π are retained where π is mathematically part of the result. Because the supplied dimensions make `π = 22/7` a conventional neat evaluation, that value is reported second where useful; it is not substituted silently.
- Every Core2 answer uses a typed reasoning route with an explicit `crux_move_ref` and a check independent of the main forward calculation.
- Q9 uses volume as the recasting invariant and separately compares total surface area; this avoids the common category error of treating surface area as conserved.
- Q10 uses the shared factor `πr²h`; separate radius and height values are intentionally not solved because the data do not determine them individually and they are unnecessary.

## 4. X / Y / Z / W resolution policy

- `X` is grounded in each question’s authored `stable_crux_move`.
- `Y` is selected by the QRT resolver from a demonstrated prerequisite capability in the owner-estimated learner profile; target capabilities are not pre-marked demonstrated.
- `Z` comes from the typed reasoning route and resolved QRT template.
- `W` is protected by the D-band policy and the question’s crux move. Core2 pre-solution scaffolds are `CONCEPT` or `METHOD`, never `ANSWER`.
- Exact resolved X/Y/Z/W strings, question/profile/matrix/vocabulary digests and Mathematics adapter digests are emitted by `evidence/pilots/issue-11/qrt-review-evidence.json`.

## 5. Hint, representation, helper and misconception design

- D1/D2 questions receive three purposeful authored support rungs: `REPRESENTATION`, `KEY_CONCEPT`, `CRUX`.
- D3 questions receive five purposeful rungs: the three above plus `FORMAL_MODEL` and `CHECKPOINT`. The extra rungs follow Blueprint reference depth; they do not replace the semantic H1/H2/H3 jobs.
- Every question has a staged authored representation because a geometric/unit-flow visual serves a real cognitive job here. Only the first stage is mounted before attempt; later stages are bound to requested scaffold reveals or post-attempt explanation.
- Common wrong routes are shown in Core2 `TRAP`; diagnostics and replacement rules are taught in the linked Core1A microtopic’s `misconceptions[]`.
- P2 concept navigation is derived from canonical `primary_capability_ref` ownership, not hand-written reciprocal links.

## 6. Core1A construction decisions

- Core1A uses `BP-CORE1A-CONSTRUCTION@1.4.0` and six construction units clustered from recurring reviewed cruxes rather than copying ten question solutions into ten lessons.
- Surface-boundary selection unifies cube/cylinder/open/hemisphere/painting items because the common teaching move is 'inventory the physical boundary before formula selection'.
- Cone slant height is its own construction because Q4 requires a dependency bridge from axial right triangle to lateral area.
- Composite exposed area is separate because Q6 adds hidden-interface reasoning and is the strongest combined conceptual/representation item in the set.
- Capacity conversion, recasting conservation, and cone-cylinder ratio each use distinct invariants/translation rules and therefore remain separate units.
- Each unit has `crux_question_refs`, a `crux_step_ref`, and a `bank_anchor_ref` to an owner question. Q6’s unit is explicitly built around Q6 as the likely toughest-concept anchor.
- `EXIT_RECALL` tasks are fresh authored checks after teaching; they do not reuse protected Core2 answers.

## 7. Quality/review record design

- The QRT resolver is run with the Mathematics demand adapter for every question.
- H1–H3, S1–S3, P1–P3 and M1–M3 receive explicit qualitative judgements plus evidence. No aggregate QRT score is produced.
- Actionable `PARTLY`/`NO` judgements would be projected through `question_review_matrix.py::project_product_review_findings`. The generated projection is stored even when all semantic judgements are YES.
- The exact rendered `core2.html` and `core1a.html` digests are attached to every question review after rendering.
- The execution deliberately produces a pre-QRT-support baseline render and a final governed render, runs the real `quality_gate.py` on both, and emits the tool-native before/after delta.

## 8. Deviation log

1. **Learner-profile shape:** PR #9 expects idea-level PROFILE entries; the owner supplied only the state `DEMONSTRATED`. Resolution: map that state to explicitly named prerequisites actually used by the questions; do not infer target mastery. This is preserved as an owner-estimate, `measured_fit_claim=false`.
2. **Owner-bank documentation/runtime mismatch:** `docs/method/REQUESTS.md` and `Shared/tools/owner_bank.py` describe owner banks as TEST-sandbox-only, while `render_core.py` explicitly accepts an owner-supplied bank at any non-`exam-bank/` path and the PR #9 short-prompt contract routes owner-supplied preserved questions to Core2. Resolution: use the runtime-supported owner-bank format under `Mathematics/question-bank/owner-supplied/`; do not invent official-exam custody.
3. **Question-review schema missing:** Issue #6 proposed `Shared/quality/question-review.schema.json`, but it is not present in PR #9’s changed-file set. Resolution: preserve the tool’s `question-review-resolution/v1` output and explicit H/S/P/M judgements inside `issue11-qrt-review-evidence/v1`; record this as an unresolved architecture limitation.
4. **Release sign-off:** the authoring agent also performs the first semantic review. `reviewer_distinct_from_author=false`; all outputs state `release_certification=false`. Independent owner/reviewer audit remains open by design.

## 9. Execution record and final traceability

Source paths:

- `Mathematics/library/surface-areas-volumes.issue11.v1.json`
- `Mathematics/question-bank/owner-supplied/issue-11-surface-areas-volumes.json`
- `products/mathematics/surface-areas-volumes.issue11.manifest.json`
- `evidence/pilots/issue-11/learner-profile.json`
- `evidence/pilots/issue-11/qrt-judgements.json`
- `evidence/pilots/issue-11/pilot_runner.py`

Generated paths (CI):

- `evidence/pilots/issue-11/render/core2.html`
- `evidence/pilots/issue-11/render/core1a.html`
- `evidence/pilots/issue-11/render/render-receipt.json`
- `evidence/pilots/issue-11/qrt-review-evidence.json`
- `evidence/pilots/issue-11/product-review-qrt-findings.json`
- `evidence/pilots/issue-11/gate-before.json`
- `evidence/pilots/issue-11/gate-after.json`
- `evidence/pilots/issue-11/gate-delta.json`
- `evidence/pilots/issue-11/execution-record.json`

The exact generated-artifact commit SHA is recorded on Issue #11 after the CI job commits the governed outputs. That external issue record avoids an impossible self-referential commit-SHA field inside the commit itself.

## 10. Open blockers / non-certifications

- Independent reviewer sign-off is not performed by the execution agent.
- The absence of the proposed canonical question-review schema remains an implementation gap in PR #9.
- Any gate or browser-measurement limitation reported in `gate-after.json` remains open and must not be silently waived.

- PR #9 contract tests at pilot runtime: pytest exit 1. Current observed failure is the PR #3 pilot fixture review-key ordering assertion; QRT matrix compile/check itself passed. This is preserved as an unresolved upstream finding, not suppressed as a pass.

## 11. Pilot execution findings and remediation chronology

### Package validation

The first materialized Mathematics package did not pass the canonical package schema. Validation exposed 23 initial findings: one invalid convention shape, six empty relation derivations, and fifteen relation symbols without required unit/domain declarations; the next validation exposed two noncanonical resource-role labels. These were repaired in the governed records rather than waived. The final package and owner-supplied bank both pass their repository validators.

### Strict render-depth findings

The first strict reference render exposed 10 depth-gap instances:
- six governing relations had no presentation MathML;
- three SVGs contained clipped labels, with the composite representation used in both Core1A and Core2 and therefore producing four visual gap instances.

The six relations were given explicit presentation MathML, and the clipped SVG labels were shortened/repositioned without changing their semantic jobs. The subsequent strict reference run reported **0 depth gaps**.

### Subject-authority findings

After depth remediation, the strict renderer still reports six `GATE_RELATION_BINDING_ABSENT` authority findings, one for each new candidate relation:
- `REL-I11-SA-BOUNDARY`
- `REL-I11-CONE-SLANT`
- `REL-I11-COMPOSITE`
- `REL-I11-CAPACITY`
- `REL-I11-RECAST`
- `REL-I11-CONE-CYL`

No engineering-gate relation was invented to silence these findings. They remain explicit repository-integration limitations for independent review.

### Real quality-gate delta

The deliberately unsupported baseline render produced **45 findings** and a `FAIL` verdict. The governed final render closes all question-support findings and carries a valid governed-renderer stamp, but the real gate remains **FAIL with 4 blocking findings**:
- Core1A: `PAGE-SHELL` / S1 — `shell_header` absent;
- Core2: `PAGE-SHELL` / S1 — `shell_header` absent;
- Core1A: `PAGE-TOUCH` / S2 — 6 small targets;
- Core2: `PAGE-TOUCH` / S2 — 6 small targets.

Inspection ties these four findings to the shared renderer/shell contract rather than to missing question support. The renderer emits `<header class="g9-shell-header">` while `quality_observe.shell_facts()` requires the `data-g9-shell-header` marker, and the modern shell stylesheet permits controls below the blueprint's 48 px minimum. No gate rule was weakened and no waiver was issued.

### QRT contract regression record

`question_review_matrix.py check` compiles the complete 28-cell matrix successfully. The combined PR #9 test invocation records one pre-existing fixture-order regression in `test_pr3_math_pilot_exercises_five_real_source_question_cells`: the PR #3 fixture's H/S/P/M key insertion order differs from the canonical `qrt.ASKS` order. The run records **1 failed, 34 passed, 31 subtests passed** and preserves the nonzero exit code. This failure is not caused by the Issue #11 question classifications or rendered artifacts.

### Question Bank projection record

Repository Question Bank platform tests themselves pass, but adding the new owner-supplied bank makes committed generated Question Bank projections stale. The platform check identifies catalog/search/questions/resources/manifest/detail and lineage/dedup/build-receipt outputs for regeneration. This is recorded as a repository publication-integration blocker rather than being conflated with academic/QRT correctness.

### Evidence-provenance correction

The first generated execution record used the workflow event SHA as `source_commit_sha`, even though the rerun explicitly checked out the current pilot branch. The pilot runner was corrected to record `git rev-parse HEAD` as the actual checked-out source commit and to retain the workflow event SHA separately. The render receipt's `digest` is also now bound into each question's exact-render evidence under `render_artifact_digest`.

## 12. Current unresolved findings / waivers

No waivers were issued. The remaining open items are:
1. independent reviewer sign-off and release decision;
2. six candidate Mathematics relations lacking engineering-gate bindings;
3. the shared renderer/gate shell-marker and minimum-touch-target mismatch causing the four final real-gate findings;
4. the missing canonical `Shared/quality/question-review.schema.json` proposed by Issue #6;
5. the recorded PR #3 fixture-order regression in the PR #9 QRT tests;
6. stale generated Question Bank platform projections after introducing this owner-supplied bank.

The execution agent does not self-certify release. The governed learner HTML and machine evidence remain the pilot products, while the items above remain auditable blockers/limitations.
