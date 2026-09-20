# Topic Atlas webpage gap analysis — current governed basis

Date: 2026-09-20  
Execution package: `EP-TA-001`  
Owner architecture issue: #118

## Current basis

The live implementation basis includes the merged data-driven Topic Atlas, Motion-in-2D GCDR work, Motion-1D continuation, GCDR quality/runtime hardening, and the later master-suite audit. PR #117 is a superseded visual prototype and is not the current implementation authority.

The normal learner-facing operating model has exactly two optional inputs:

1. rough knowledge percentage for the current subtopic/matrix; and
2. latest external scanned-answer diagnostic gap rows.

No input is also valid: the Atlas remains a canonical browse surface without claiming learner placement.

## Correctness gaps owned by EP-TA-001

This execution package corrects the browser seam rather than creating a second curriculum/planner:

- exact capability identity is required; `rung_ref` cannot rescue an invalid capability;
- a conflicting capability/rung pair is rejected;
- diagnostic result, stage and score fail closed;
- invalid `repair_ref` drops only the unsupported narrow target and keeps the valid capability-level gap;
- knowledge estimate is not imported from or exported inside the diagnostic envelope;
- semantic addresses distinguish exact leaf+dimension, leaf+unknown-dimension and capability-only fallback;
- separate diagnostic dimensions on one semantic leaf remain separate and are never averaged;
- no learner input produces canonical browse mode, not a pseudo learner target;
- browser controls no longer maintain a parallel manual mastery ledger or derive knowledge percentage from leaf clicks;
- Core selection is a local request preview, not an authoritative readiness/prerequisite decision;
- browser request export targets the existing plan-level authoring-request contract;
- Measurement Pack browser export separates measurement-critical fields from routing-only context;
- the browser does not claim a nonexistent Measurement Pack schema.

## Remaining programme after EP-TA-001

### WP-TA-102 — Shared diagnostic/Core authority

Move browser-only composition into reusable Shared contracts/tools: validated transient diagnostic envelope, Measurement Pack exporter, semantic need resolver, Core focus/emphasis and focus-aware inventory. Reuse existing observation, authoring-request, planner, worksheet-map and canonical package semantics. Do not create a second learner store or new mastery model.

### WP-TA-103 — Atlas coverage and exact resource bindings

Generate missing Atlas surfaces only for matrices already backed by canonical data and bind activities at the smallest justified stable semantic target. No page may hard-code a claim that is absent from canonical resource bindings.

### WP-TA-104 — grounded academic inventory closure

Audit the remaining Agent-A content gaps against current canonical capabilities, teaching steps, misconceptions, question families and actual demand evidence. Author only evidenced missing content. Do not use arbitrary per-topic quotas or proliferate capabilities to make the UI look granular.

### WP-TA-105 — cross-subject acceptance and GCDR evidence closure

Prove the same diagnostic/resolver/request path in Physics and Mathematics, run full repository guardrails, and promote GCDR status only where the current evidence contract supports it.

## Explicit non-goals

No seventh Core, no physical `R5.1.0` matrix rows, no automatic mastery probability, no score averaging, no fuzzy curriculum identity, no silent `DEMONSTRATED` inference, and no browser-side clone of the authoritative Python planner.
