# Issue #35 validation — frozen candidate

## Candidate identity

- Governing issue: #35
- Candidate PR: #40
- Branch: `candidate/iss35-d3-hybridisation-agent-a-r1`
- Controlled seed/base: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`
- Source head that entered the governed cold run: `9030856abb0edf30fc2af4f85e4147af13a1f9b6`
- Workflow evidence preservation commit: `b9246195e1ec208a920ef55afd53ce8e7b84aa9f`
- Core1A SHA-256: `7362ed60e3542ea0e9c3fe080c2672c50a0484b0fa21393bc1f7ebec34b2f6c3`
- Core2 SHA-256: `1d4adb94036b5d76a6b2d0031326d8669ddd0bbbccf88576dcb1f57ca9456048`

The learner-product bytes above are frozen. Later audit documentation must not be interpreted as a re-render or as validation of changed learner bytes.

## Cold-run execution

GitHub Actions workflow run `37188151319`, job `111394463379` (`cold-run`) completed successfully.

All material steps concluded `success`:

1. controlled-seed and prompt preflight;
2. materialise candidate records;
3. custody and package-schema validation;
4. governed Core1A/Core2 render through `Shared/tools/render_core.py`;
5. pinned Playwright/Chromium installation;
6. strict learner-quality gate;
7. tablet-12.7 exact-render browser audit;
8. evidence preservation and receipt generation;
9. generated-evidence commit;
10. artifact upload.

The run receipt records Python 3.12, Node 22 and Playwright 1.56.1.

## Intake/custody checks

- Exact A/B/C prompt SHA-256: `cc448399f7c44781f8e3ca659aaa96da8b9fde5edc7a66625b45729f728a29d5` — PASS.
- The candidate remains descended from the pinned seed — PASS.
- No `Shared/**` file was changed between the controlled seed and the cold-run source head — PASS.
- `owner.bank.json` custody validation — PASS.
- package v1 schema validation — PASS.
- Q1–Q10 materialisation count/order — PASS.

## Academic/task analysis

All ten items were independently solved before rendering and then reviewed again against the exact render.

Actual primary QRT cells:

| Q | Cell | Band |
|---|---|---|
| Q1 | JUSTIFY | D3 |
| Q2 | REPRESENT | D3 |
| Q3 | SYNTHESIZE | D3 |
| Q4 | EXPLAIN | D3 |
| Q5 | JUSTIFY | D3 |
| Q6 | APPLY | D2 |
| Q7 | MODEL | D3 |
| Q8 | EXPLAIN | D2 |
| Q9 | REPRESENT | D2 |
| Q10 | MODEL | D3 |

This preserves the issue rule that the D3 issue label is a cohort label rather than a forced per-question classification.

The hardest learner-relative target remains Q2 / `QRT-REPRESENT-D3`: translating formal Lewis contributors into one delocalised multi-centre pi description while preserving the invariant sigma framework. The staged interaction does not use `sp2` as proof of delocalisation and does not describe resonance contributors as time-resolved molecular states.

Exact-render H1–M3 verdicts are recorded in `semantic-review.v1.json`.

## Strict learner-quality gate

Report: `reports/quality-gate.json`

- Contract version: 1.8.1
- Render stamp: `render_core/2 ce7531223bb97485`
- Verdict: **PASS**
- Blocking fail reasons: none
- Non-blocking findings: **16 S3 findings**

### Finding group A — figure vocabulary (13)

The candidate uses representation kind `ORBITAL_MODEL`; the pinned Chemistry adapter vocabulary contains `ORBITAL_DIAGRAM`, not `ORBITAL_MODEL`.

Affected rendered surfaces:

- all 3 Core1A construction units;
- all 10 Core2 question units.

Disposition: **OPEN / candidate-record naming defect.** Do not treat the green gate as evidence that the vocabulary mismatch is correct. Because the first learner candidate was already frozen before the pair-comparison boundary was crossed, this run does not rewrite the candidate bytes to repair it. A later correction round should use the canonical Chemistry token or explicitly revise the vocabulary contract if a genuinely different representation kind is required.

### Finding group B — expected EQUATIONS component (3)

Each Core1A construction unit lacks `EQUATIONS`, which the generic blueprint marks as expected.

Disposition: **JUSTIFIED NON-BLOCKING CONTRACT MISMATCH.** These three targets are qualitative representation/model bridges. Adding ornamental equations would not improve the intended learning objective. The better follow-up is to make expected-component applicability explicit rather than inserting irrelevant content solely to silence a warning.

## Exact-render browser audit

Report: `reports/tablet-audit.json`

Workflow step conclusion: **success**.

Positive evidence from the audited profiles:

- 0 small touch targets reported;
- 0 horizontal overflow;
- no hover-only handlers;
- all 3 Core1A SVGs exposed accessible SVG metadata;
- staged SVG violations: 0;
- protected-search matches: 0;
- gated disclosures open before attempt: 0;
- Core1A support remains side-by-side at the tablet landscape widths expected by the blueprint and stacks at narrower widths;
- Core1A/Core2 shell, print and focus styles were present.

Non-blocking browser observations preserved for handoff:

- focus probe: 10 failures among 105 candidates in the audited profiles;
- landscape sticky-header geometry marks deep-link anchors as at risk of being obscured; portrait, where the header is not sticky, reports no such anchor risk.

Disposition: **OPEN shell/accessibility hardening; not an academic-content blocker.** These findings are not hidden by the successful workflow conclusion.

## Semantic / model-boundary audit

No substantive academic correction was required after exact-render inspection.

Key boundaries retained:

- hybridisation is applied atom-locally as an introductory sigma-framework model;
- bond equivalence is not used as the criterion for assigning `sp2`;
- a multiple bond supplies one sigma direction for local domain counting while containing separate pi component(s);
- nitrate/carbonate Lewis contributors are formal contributors to one electronic description, not required temporal states;
- the allene central carbon uses two mutually perpendicular unhybridised p orbitals in the conventional qualitative model;
- ethene twisting is described via loss of side-on p overlap without claiming a numerical barrier from the sketch;
- conjugation is treated as requiring a continuous suitably aligned p-orbital pathway, and an sp3 carbon interrupts that pathway.

External source cards remain model-boundary checks only; benchmark givens are not relabelled as measured facts or official exam provenance.

## Post-render builder finding

`builder-proposal.md` proposes the optional `correspondence-sort` interaction. The proposal is derived from the frozen Q2/render limitation: current stage controls show the sequence but do not require a structured pre-reveal mapping of invariant versus contributor-local versus target-model features.

The proposal is additive and does not authorize a second renderer or publication path.

## Blindness / comparison boundary

The governed run and evidence-preservation commit `b9246195...` were completed before any paired-candidate information was surfaced.

During a later PR-status lookup, the connector search response incidentally returned the paired PR #43 summary. That information is quarantined. No learner content, academic answer, QRT classification, hardest-target choice, render asset or render byte was changed after the exposure.

Because `builder-proposal.md` and final audit/handoff documentation were authored after the exposure, they should not be treated as perfectly blind pair-comparison evidence. The frozen U1–U6 learner candidate itself remains the pre-exposure candidate.

## Promotion status

**CANDIDATE ONLY.** This execution agent does not certify release, golden promotion or merge readiness. PR #40 must remain unmerged unless a separate authorized review promotes it.
