# Issue #49 validation — POLYNOMIAL-STRESS-V1

## Scope and exact basis

The candidate is built from pinned seed `91719ad8df2bfc06c6a481590d2e24c510c24835` on `feat/iss49-polynomial-stress-d1`. The frozen A/B/C SHA-256 is `c2cca6e6b92997c30d2f3a7eab91577bc8463ec9ce44ca90b9be728f3d1d46b8`. The reference candidate before audit-only packaging is `a9f38c448eca0f8b092155d2e81764d22691a034`.

The Issue #49 workflow run `37329225494` passed on that exact head. It verified the frozen input, regenerated canonical records, checked owner-bank custody and package schema, ran focused blueprint/quality/QRT contract tests, rendered only Core1A and Core2 through `Shared/tools/render_core.py`, classified the strict-quality delta, enforced the browser audit, and confirmed that deterministic generated evidence required no further material commit.

## Academic and custody validation

All ten supplied stems remain owner-custody text and are preserved in original order. Authorship is disclosed as AI/coordinator authored under Owner request; no official-exam or authenticated-textbook identity is claimed.

The actual item results are not forced to the D1 cohort label:

| Question | Band | Score | Primary demand |
| --- | --- | ---: | --- |
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

Q10 is the hardest target. Its independent check verifies both constraints and uniqueness after solving the remaining coefficient. Q9 uses a symbolic distributive-law argument for the universal identity instead of sampled agreement.

An official NCERT Grade 9 Chapter 2.1 source was directly inspected on 2026-10-05. It supports the general terminology used here: one-variable polynomials, coefficients, constants, degree in the presented examples, and a non-zero constant polynomial as degree 0. It is not the provenance of the benchmark questions and supplies no difficulty/QRT adjudication.

## Render evidence

The governed receipt reports:

- renderer: `render_core/2`
- render digest: `ef9a4565a4bc05a5`
- semantic digest: `22512584ac9f1f6a`
- draft: `false`
- gaps: `[]`
- output roles: exactly `CORE1A`, `CORE2`

Learner HTML SHA-256:

- Core1A: `19af674ad2360cbe1542d9f3dc115688ec030ff065d8ada14a5804b48eca45c0`
- Core2: `07723efd4e1532358a1105dac8222a464e0b96af3dc70e9a9f6365d9198cb2d6`

Reference workflow artifact `11353965698` has SHA-256 `a258c19de1edda35eab169c33e450c038f5b68b970da8231f40a748ee3eed303`.

## QRT / semantic review

`qrt-review.json` contains H1–H3, S1–S3, P1–P3 and M1–M3 records for each of Q1–Q10. These are implementation-coupled author-review statuses, not independent semantic acceptance.

Primary-cell coverage in the canonical 4 × 7 matrix is 7/28 unique cells:

`RETRIEVE/D1`, `APPLY/D1`, `REPRESENT/D2`, `EXPLAIN/D2`, `MODEL/D2`, `JUSTIFY/D2`, `SYNTHESIZE/D2`.

The remaining 21 cells are gaps in primary-instance coverage; secondary acts are not counted as substitutes.

## Strict quality result

The strict quality report remains intentionally **non-green**. It has exactly one S2 finding:

`PAGE-STAGE-SUPPORT · core1a.html · stage support layout absent`.

The candidate-specific strict-quality finding count is zero. The workflow proves the relevant shared authorities are unchanged from the pinned seed and confirms the contradiction:

- `BP-CORE1A-CONSTRUCTION@1.7.0` declares expanded `SINGLE_PANE`;
- `Shared/quality/learner-quality.v1.json` applies `PAGE-STAGE-SUPPORT` to Core1A.

This finding is therefore preserved as inherited authority debt, not waived or converted to PASS.

## Exact-render browser audit

The enforced browser audit passed across six profiles: phone 390×844, portrait 800×1280 and 820×1180, landscape 1180×820 and 1280×800, and desktop 1440×900.

For both learner pages the observed summary is:

- root horizontal overflow: 0;
- undersized controls: 0;
- focus failures: 0;
- staged-SVG violations: 0;
- root horizontal overflow at 200% text scaling: 0.

Core1A reports `stageSupportLayout=false`, consistent with the inherited authority contradiction rather than hidden by the audit. Q10's exact learning page contains the typed prediction/reason interaction before comparison reveal.

## Failed/superseded runs retained

The audit preserves the initial trailing-newline digest failure, relation-schema failure, renderer binding gaps, and invalid Mathematics figure-kind findings. Each was corrected at the narrowest responsible layer; none is rewritten as an initial PASS.

## Repository-wide checks

Repository-wide guardrails and canonical assurance are not green. Their failures include pre-existing canonical Mathematics/Physics and legacy standalone-page debt outside the Issue #49 changed paths.

The exact PR-base versus candidate regression-delta job is the relevant same-environment comparison: it reports `new 0; fixed 0; still failing (not new) 99`. This does not make the repository green; it establishes that this candidate introduced no new exact failing test IDs in that comparison.

PR-event V3.1 Relay binding is also red because issue #49 has no Task Snapshot under `relay/GENERATED/tasks`. Push Relay validation on the exact candidate head passed. The missing read model is recorded as a coordination/observability handoff gap, not learner-product correctness evidence.

## Go / no-go

**GO:** independent review of draft PR #62 and inspection of the frozen candidate.

**NO-GO:** merge, golden promotion, learner publication, or claiming universal 28-cell coverage. Independent semantic acceptance is still pending, the strict quality report is non-green due the inherited Core1A authority contradiction, and PR-event V3.1 task-binding observability remains incomplete.
