# ISS52 work report — POLYNOMIAL-STRESS-V1

Status: **CANDIDATE IN PROGRESS**  
Source basis: `91719ad8df2bfc06c6a481590d2e24c510c24835`  
Branch: `agent/iss52-polynomial-stress-v1`  
Owner A/B/C digest: `46058f7ade3862a6f5707fa0f49c5e284d74b6de56100312d6f1a840d65392b9` (verified)

## U1 — Intake/baseline — COMPLETE

The exact A/B/C block is frozen in `evidence/benchmark/ISS52/owner-core-prompt.md`. All ten questions are preserved in source order with per-question SHA-256 digests. The learner profile is simulated benchmark evidence only. Custody is OWNER_SUPPLIED intake; authorship is AI/coordinator under Owner request, with no exam/PYQ identity.

Pinned authority: registry 1.14.0, Core1A 1.7.0, Core2 1.9.0, sole renderer `Shared/tools/render_core.py`, the 4×7 QRT matrix, and the Mathematics adapter at the source commit. Requested Common engineering protocol V3.2 was read. Owner clarifications: **NONE**; A/B/C sufficed.

## U2 — Academic/task analysis — COMPLETE

All ten items were independently solved and checked before record authoring. `question-ledger.json` holds the answer derivations, five governed difficulty components, primary/secondary demands and QRT cells.

Actual primary-cell coverage is D2 EXPLAIN (Q6), D2 SYNTHESIZE (Q8), D3 JUSTIFY (Q1), D3 SYNTHESIZE (Q2,Q7), D3 MODEL (Q5), D4 JUSTIFY (Q3,Q9), and D4 SYNTHESIZE (Q4,Q10). Six questions are therefore recorded as easier than the intended D4 cohort rather than inflated.

## U3 — Hardest-target brief — COMPLETE

**Target:** Q4, exhaustive parameter classification from degree-drop, real-root-existence and root-coincidence events × **SYNTHESIZE D4**.

Learner-relative X/Y/Z/W:
- X: identify every event that can change degree, real-root existence or root coincidence.
- Y: routine factorization/simple identities and elementary real-domain reasoning are demonstrated.
- Z: derive event equations, order their parameter values and use them to partition the parameter line.
- W: the event-set/partition decision remains learner-owned in Core2 pre-attempt support.

Crux: derive the change events before sampling cases. Diagnostic hypothesis: a learner may solve the generic branch correctly but omit a degree drop or collision, producing a plausible but non-exhaustive table.

Core1A interaction: a staged, accessible parameter-event map for a **changed polynomial family**. The learner reveals degree-drop, existence-boundary and collision tests one stage at a time, then applies the workflow to a fresh case. The source Q4 event values are not disclosed in its pre-attempt Core2 support.

## U4–U8

U4 canonical records is in progress. U5 render/integration, U6 exact semantic/interaction review, U7 builder proposal and U8 frozen handoff remain open. No schema, renderer, browser or PDF result is claimed before it is actually run.

## Execution deviation

The local container cannot resolve external GitHub and therefore cannot obtain the pinned repository for direct execution. Connected GitHub repository actions remain available. This is recorded as an environment limitation, not a permission request. No second renderer and no hand-edited generated HTML will be introduced.
