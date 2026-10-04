# Issue 37 — Agent A Round 1 Work Report

## Candidate identity

- Issue: #37
- Agent: A
- Round: 1
- Target: D4 hybridisation
- Requested learner roles: `CORE1A` + `CORE2` only
- Branch: `feat/iss37-d4-hybridisation-agent-a-r1`
- Controlled seed: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`
- Controlled integration line: draft PR #30 head `feat/issue29-integrated-core-templates`
- Canonical handoff PR: draft PR #47, based on that controlled seed line
- Final evidence-reconciled artifact head before this report-only update: `c056ba9a5e26fe9a71054a79bc7f1b9a136a1044`

This is a frozen comparison candidate, not a release/golden certification. Do not merge until the paired independent comparison and owner decision are complete.

## Custody and intake

- The ten benchmark questions are preserved verbatim from the Issue #37 owner-supplied intake.
- Owner-core SHA-256: `52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7`.
- Custody remains `OWNER_SUPPLIED` benchmark input drafted by the coordinating agent under the owner pilot; it is not an official exam/PYQ and is not attributed as personally authored by the owner.
- First learner-artifact freeze occurred before any partner output was inspected.

## U1–U8 delivery trace

### U1 — Freeze intake and authority

- `evidence/benchmark/ISS37/owner-core-prompt.md`
- `evidence/benchmark/ISS37/question-ledger.json`
- `evidence/benchmark/ISS37/source-cards.json`
- Controlled seed pinned to `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`.

### U2 — Independent academic analysis

- Ten questions classified by primary/secondary demand and learner-relative difficulty.
- Hardest target: Q9, D4 critique/interpret — execute a supplied `cos(theta)` orbital-overlap model without transferring that functional form to total molecular energy.
- The planning ledger records X/Y/Z/W for every question and a richer interactive target for Q9.

### U3 — Source/custody discipline

- The candidate preserves the benchmark wording and records the custody discrepancy rather than inventing official-exam provenance.
- Sources and benchmark custody are carried in `source-cards.json`, the ledger, package records and learner-facing provenance.

### U4 — Governed authoring

- Candidate records are built by `evidence/benchmark/ISS37/build_specimen.py` plus normalization/finalization scripts.
- Product manifest is explicitly scoped to `output_roles = ["CORE1A", "CORE2"]`.
- The torsion/orbital representation uses Chemistry-native `ORBITAL_DIAGRAM` vocabulary.

### U5 — Sole-renderer projection

- `Shared/tools/render_core.py` remained the sole HTML renderer; learner HTML was not hand-edited.
- Frozen learner outputs:
  - `evidence/benchmark/ISS37/rendered/core1a.html`
  - `evidence/benchmark/ISS37/rendered/core2.html`
- Render digest: `7f17edbe1aa29a5f`.
- First frozen renderer-artifact commit: `d813c58a6e689ec392bfd5af1089a7aedbb9ad74`.

### U6 — Validation

Green source run `37202577119` at `49c9e2957e91a31e7a40a74cbadd83377c36f1e7` passed:

- focused/pinned authoring-authority tests
- verbatim intake hash
- package schema
- requested output-role scope
- governed renderer gap report: **0 depth gaps; 0 subject-authority findings**
- governed Core1A/Core2 render
- strict learner quality gate
- tablet-12.7 browser audit
- exact renderer-artifact preservation

Evidence-reconciliation run `37203892577` at `b12960eb69a40402ae2f3c49c7b2bdc477e6d85e` also passed the full chain, including exact-render QRT reconciliation, and produced bot commit `c056ba9a5e26fe9a71054a79bc7f1b9a136a1044`.

### U7 — Exact-render QRT review and builder decision

- Machine-readable review: `evidence/benchmark/ISS37/exact-render-review.json`.
- All Q1–Q10 ledger rows now point to that review as `EXACT_RENDER_REVIEWED_WITH_LIMITATIONS`; no `PENDING_EXACT_RENDER` rows remain.
- H1–M3 are recorded per question. The review deliberately retains `PARTLY` where the rendered product routes misconception diagnosis or later visual construction through Core1A rather than fully instantiating it on the Core2 question surface.
- Q9 is the strongest rendered case: predict-before-reveal worked steps, a three-stage accessible orbital diagram, explicit model-boundary diagnosis/repair, and an attempt-gated transfer task.
- Residual limitation: the frozen Q9 page does not implement the richer planned continuous theta slider/live named-output/counterfactual probe.
- Builder proposal: opt-in reusable `MODEL_SCOPE_PROBE` through the existing Core1A interaction path, relation-bound and with a static fallback; **no second HTML renderer and no bulk migration**.

### U8 — Frozen handoff

- Canonical draft PR: #47.
- PR base: `feat/issue29-integrated-core-templates` at the issue-pinned seed `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`.
- An earlier draft PR #45 incorrectly targeted current `main`; it was closed unmerged after branch-history contamination was identified. The candidate branch itself remained clean against the controlled seed.
- A clean-main probe confirmed current `main` lacks the pinned authoring runtime, so `main` is not the controlled benchmark baseline for this pair.

## Final assessment

The Agent-A Round-1 learner candidate is technically green and evidence-complete for the controlled comparison handoff. The exact-render academic review is intentionally more conservative than the automated quality gate: the product passes rendering, accessibility/quality and tablet checks, while the QRT record preserves pedagogical limitations instead of converting those gates into a false all-YES academic judgement.

The candidate remains **draft, frozen and unmerged** pending the paired independent comparison and owner decision.
