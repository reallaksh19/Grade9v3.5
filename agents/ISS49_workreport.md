# ISS49 work report — POLYNOMIAL-STRESS-V1

## Scope and custody

Executed the fixed Issue #49 Grade 9 Mathematics polynomial benchmark from pinned seed `91719ad8df2bfc06c6a481590d2e24c510c24835` using the existing Core1A/Core2 renderer, blueprint and QRT contracts. The frozen A/B/C SHA-256 is `c2cca6e6b92997c30d2f3a7eab91577bc8463ec9ce44ca90b9be728f3d1d46b8`. No other polynomial stress-run solution/output was consulted before this candidate was frozen.

Question custody is OWNER_SUPPLIED. The benchmark wording was AI/coordinator authored under the Owner's explicit request. No item is represented as an official exam/PYQ item, an authenticated textbook transcription, or personally authored by the Owner.

## Delivered

- Verbatim owner prompt and structured intake with exact custody.
- Deterministic owner-bank and package generation.
- Four Core1A concept construction units and ten fixed Core2 questions.
- Machine-readable QRT review for H1–H3, S1–S3, P1–P3 and M1–M3 on every question.
- Hardest-target brief and learner-relative misconception/repair hypothesis.
- Governed Core1A and Core2 learner HTML, render receipt, strict quality report and six-profile browser audit.
- Builder-improvement proposal grounded in the exact rendered candidate.

## Academic calibration

The owner label `D1 intended` is retained as cohort intent, not used as the actual difficulty result.

| Q | Actual band | Score | Primary demand |
|---|---|---:|---|
| Q1 | D1 | 2 | RETRIEVE |
| Q2 | D1 | 2 | RETRIEVE |
| Q3 | D1 | 1 | APPLY |
| Q4 | D1 | 2 | APPLY |
| Q5 | D2 | 3 | REPRESENT |
| Q6 | D2 | 3 | EXPLAIN |
| Q7 | D2 | 4 | MODEL |
| Q8 | D1 | 2 | APPLY |
| Q9 | D2 | 3 | JUSTIFY |
| Q10 | D2 | 5 | SYNTHESIZE |

Q10 is the selected hardest target. The decisive bridge is to represent the fixed-constant family as `p(x)=ax+2`, convert the specified zero into `p(1)=0`, solve the remaining coefficient, and then establish uniqueness by showing no parameter freedom remains.

The simulated preset demonstrates integer arithmetic, signed-number operations, powers, basic distribution and familiar substitution. It leaves polynomial terminology, missing coefficients, collecting terms, standard identities and interpretation of a zero uncertain. The Q10 misconception hypothesis is that a learner may know scalar multiples preserve a root but overlook that scaling changes the fixed constant. The changed-case repair uses constant 6 and zero 3 and requires a typed prediction/reason before comparison is revealed.

## Validation chronology

1. Run 37288268400 failed before generation because the frozen prompt file had one extra trailing newline. Only that byte was removed; the subsequent digest check passed.
2. Run 37288410954 passed freeze/generation/owner custody, then exposed the package requirement that relation derivations be non-empty. Typed local derivation records were added.
3. Run 37289027810 isolated five renderer gaps: one duplicate typed-math literal declaration on Q1 and authored-visual binding mismatches on Q5/Q6/Q7/Q10. These contract bindings were corrected without changing question wording or academic classification.
4. Run 37326165841 rendered successfully and exposed six candidate-specific Mathematics figure-kind vocabulary findings plus one Core1A layout finding. Figure kinds were changed to the registered `TABLE_OF_VALUES` / `AREA_MODEL` vocabulary.
5. Reference run 37327449789 at `bf52ef0d52dfe9b68b4ff8665ed3717560b77319` passed frozen-input verification, deterministic generation, owner-bank custody, package schema, focused shared-contract checks, governed rendering, quality-delta classification and the enforced browser audit.

The governed render receipt is clean: `render_core/2`, render digest `ef9a4565a4bc05a5`, semantic digest `22512584ac9f1f6a`, `gaps: []`, non-draft, and output roles exactly `CORE1A` and `CORE2`.

Reference learner HTML SHA-256:
- `core1a.html`: `19af674ad2360cbe1542d9f3dc115688ec030ff065d8ada14a5804b48eca45c0`
- `core2.html`: `07723efd4e1532358a1105dac8222a464e0b96af3dc70e9a9f6365d9198cb2d6`

## Strict quality finding: inherited authority contradiction

The strict quality report is **not green**. It has exactly one S2 finding:

`PAGE-STAGE-SUPPORT · core1a.html · stage support layout absent`.

Candidate-specific strict-quality findings are zero after the Mathematics figure-kind repair. The remaining finding is classified by the workflow against unchanged pinned authorities: `BP-CORE1A-CONSTRUCTION@1.7.0` declares `responsive_policy.expanded = SINGLE_PANE`, while `Shared/quality/learner-quality.v1.json` applies `PAGE-STAGE-SUPPORT` to Core1A. The candidate does not locally override either authority.

## Browser evidence

The enforced browser audit passes. On both learner pages, across phone 390×844, portrait 800×1280 and 820×1180, landscape 1180×820 and 1280×800, and desktop 1440×900:
- root horizontal overflow: 0;
- undersized controls: 0;
- focus failures: 0;
- staged-SVG violations: 0;
- 200% text-scaling root horizontal overflow: 0.

Core1A reports `stageSupportLayout=false`, matching the inherited authority contradiction above. The Q10 exact Core1A HTML contains the question-specific typed prediction-and-reason repair interaction and return path.

## Builder proposal

The existing generic typed prediction/compare learning-repair interaction is subject-neutral and worked for Q10. The richer `MODEL_SCOPE_PROBE` in the current builder is hard-coded to a chemistry alignment/energy demonstration, so reusing it for algebra would be semantically false.

Proposed smallest reusable improvement: generalise that richer probe path into a **record-configured bounded-parameter probe**. The record should declare parameter label/range, changed-case expression or relation, derived readouts, invariant/fixed fields, learner prediction prompt, static no-JavaScript cases, and a clear non-mastery disclaimer. For Q10, a post-commit changed case could use `p(x)=ax+6` with zero 3, allow varying `a`, and show `p(3)`; the supplied target values must remain protected.

This avoids a polynomial-specific widget and converts one hard-coded subject module into reusable builder infrastructure.

## Review boundary

QRT facet statuses are implementation-coupled author review, not independent semantic acceptance. This candidate does not self-certify golden promotion, learner publication, merge, or independent review.

Generated machine evidence is preserved deterministically by the Issue #49 workflow. After the preservation commit, the same workflow must rerun on that exact material head before PR handoff.


## Audit packaging and repository-wide handoff classification

The issue-required audit surfaces are packaged under `evidence/benchmark/ISS49/`: chronological audit, question ledger, source cards, custody receipt, run receipt, validation record and candidate review, alongside canonical inputs, rendered pages and runtime evidence.

The official NCERT Grade 9 Part I Chapter 2.1 PDF was directly inspected during closeout; it supports the candidate's general polynomial terminology but is not treated as benchmark provenance or an answer/difficulty source.

Repository-wide PR checks remain non-green. The exact base/head regression-delta comparison reports `new 0; fixed 0; still failing (not new) 99`, so no new exact failing test IDs are attributable to this candidate in that comparison. PR-event V3.1 Relay binding separately reports that issue #49 has no Task Snapshot under `relay/GENERATED/tasks`; this is retained as a coordination/read-model handoff gap. Neither fact converts the repository to green.

Final audit-only packaging changes do not alter generated learner bytes. A fresh Issue #49 exact-head workflow is required after the last audit commit; its run/head are recorded in the terminal TASK_RESULT and PR body rather than predicted here.
