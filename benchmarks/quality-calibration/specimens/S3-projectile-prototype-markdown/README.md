# Projectile Motion — six-Core source-grounded prototype

**Repository basis:** `main@ca0de27e307e4f532412ac52713a6faf14b216a4`  
**Canonical academic package:** `Physics/library/phy-kin-2d-motion.v1.json`  
**Canonical bucket:** `BUCKET-PHY-KIN-2D-MOTION`  
**Prototype status:** review preview; learner release is not authorized.

This directory implements the six existing Core roles without changing their authority graph. Execution order was Core2 inspection → Core1 → Core1A → Core1B → Core2A → Core2B, but Core1/Core1A/Core1B derive only from canonical Motion-in-2D truth.

## Canonical conceptual coverage

The study products carry exactly the three canonical Motion-in-2D microtopics:

1. `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS` — R1 — one plane-motion event, separate signed x/y histories, one shared clock.
2. `MIC-PHY-KIN-2D-CONSTANT-ACCELERATION` — R2 — use one-dimensional constant-acceleration relations component by component only where each acceleration component is constant.
3. `MIC-PHY-KIN-PROJECTILE-MODEL` — R3 — ideal near-Earth projectile motion as the gravity-only specialization `a_x=0`, `a_y=-g`, with an explicit event condition.

The canonical packet explicitly excludes calculus differentiation of time-dependent position, trajectory-equation derivation as first-slice teaching, drag, variable gravity, and advanced projectile geometry. The five fixed demand anchors are therefore diagnostic inputs, not curriculum expansion authority.

## Deliverables

- `CORE1.md` — compact semantic orientation.
- `CORE2.md` — explicit source-custody HOLD product.
- `CORE1A.md` — detailed declarative teaching for the three canonical microtopics.
- `CORE1B.md` — the same three concepts as self-tutor reconstruction cycles.
- `CORE2A.md` — canonical authored familiar-practice set, with learner-acceptance HOLD.
- `CORE2B.md` — canonical authored changed-demand transfer candidates, with prior-exposure/learner-acceptance HOLD.
- `demand-map.json` — five-anchor demand analysis and canonical mapping.
- `traceability.json` — machine-readable cross-Core artifact trace.
- `validation-report.md` — structural and authority audit.
- `hold-register.json` — unresolved authority/eligibility/visual/publication dependencies.
- `preview.html` — rendered review preview with semantic visual panels and attempt-before-reveal interactions.

No PDFs are generated because source custody, learner eligibility/prior exposure, visual review, academic review, and publication readiness are not all closed.

## Status vocabulary

`STRUCTURALLY_VALIDATED` means the prototype obeys the checked structural/authority invariants. It does **not** imply `SOURCE_VERIFIED`, `ACADEMICALLY_REVIEWED`, or `PUBLICATION_READY`.

The learner's owner-supplied “approximately 50% familiarity” is retained only as `OWNER_ESTIMATE`. It is not used as evidence of prerequisite mastery, does not change Core1A/Core1B coverage, and does not establish Core2A/Core2B readiness.
