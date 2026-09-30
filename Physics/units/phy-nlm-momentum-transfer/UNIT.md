---
unit: phy-nlm-momentum-transfer
package: Physics/library/phy-nlm-momentum-transfer.v1.json
owner_agent: chatgpt-gpt5.6-sol
spine_nodes: []
microtopics: ["MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE"]
sources: ["SRC-EXAMSIDE-NLM-MOMENTUM-RATE-DEMAND", "SRC-AUTHOR-NLM-MOMENTUM-TRANSFER"]
inventories: []
grade_profile:
  base_grade: null
  assumed_prerequisites: ["CAP-NLM-FBD-BODY-OWNERSHIP", "CAP-NLM-SECOND-LAW", "CAP-NLM-THIRD-LAW"]
  enrichment: []
coverage:
  mode: CURATED_SELECTION
  inventory: null
budget_usd: null
---

# Momentum-transfer force rate

Existing package scope (carried forward): Explicit-demand Grade-9 Pinnacle preparation extension for force as momentum transferred per unit time in a repeated discrete ejection stream. It supports the owner-supplied ExamSIDE machine-gun demand without importing a general collision, impulse-integral, rocket-equation or variable-mass curriculum.

## #352 pilot basis

Real denominator/source state used for this pilot:

- canonical concept denominator: **1 microtopic** — `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE`;
- intrinsic difficulty: **HARD**;
- canonical package source: `SRC-AUTHOR-NLM-MOMENTUM-TRANSFER`;
- external demand witness: `SRC-EXAMSIDE-NLM-MOMENTUM-RATE-DEMAND` stores a locator and short demand summary only; it is not a source-custodied canonical Core2 question record;
- current product manifest `products/physics/phy-nlm-momentum-transfer.manifest.json` has `selection.core2 = []`.

Therefore the first-stage route for this bounded #352 pilot is **Core1**, not Core2. The external demand witness can inform emphasis, but it must not be promoted into a supplied/verified bank merely to choose a Core2 route.

Difficulty-first authoring priority:

- **LP-H1 / primary vertical slice:** `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE` — the learner must coordinate system/body ownership, a declared direction, per-item momentum change, transfer rate, launcher reaction and balancing holding force. See `DESIGN-NOTE.md` for the teaching crux and interaction-admission reasoning.

Full denominator coverage state:

| Canonical ref | Difficulty | Lot | First-stage state | Reason |
|---|---|---|---|---|
| `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE` | HARD | LP-H1 | IMPLEMENT / REVIEW FIRST | sole scoped microtopic and the dominant conceptual bottleneck |

There are no Medium/Low concepts in this bounded package denominator. That is a property of this one-microtopic pilot, not a general exception to #352's complete-denominator requirement.

## First-stage learner projection

Use the existing product manifest and sole renderer. The pilot does not create a second product or hand-authored learner page. The existing microtopic selection is the Core1 concept denominator; existing Core2A/Core2B authored practice remains later-Core material and must not be described as already delivered prior exposure merely because records exist.

Expected first-stage evidence when the exact render is built:

- Core1 HTML for the selected microtopic;
- learner PDF for the same selected Core1 scope;
- mapping/coverage view showing the full one-concept denominator;
- exact render digest and source/package refs;
- search/Atlas inspection for safe concept/difficulty labels and absence of author-only lot/interaction-value labels;
- browser evidence when available.

A separate Core2 key PDF is **NOT_APPLICABLE** because this pilot takes the Core1 route.

## Status notes

- This is an inherited package; #352 does not rewrite its academic truth or promote candidate material.
- `spine_nodes`, grade and source-readback inventory remain unrecorded where the inherited package does not provide them.
- The selected product remains governed by its existing manifest.
- No learner render, browser result or Owner acceptance is claimed by this UNIT update; those require exact-build evidence.
