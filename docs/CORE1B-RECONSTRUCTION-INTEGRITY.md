# Core1B genuine-reconstruction integrity

Issue: #255  
Programme: #252  
Stack base: Phase‑2 draft PR #260

## Governing question

> Does the learner reconstruct the same conceptual inference Core1A teaches before the completed construction is revealed?

Core1B owns no second conceptual truth. The canonical crux remains `microtopic.inferential_jump`.

Its progression is:

`predict → attempt → reconstruct → diagnose → repair → boundary test`.

The audit distinguishes structural evidence from semantic review. It can prove that the self-tutor cycle is present, routed and closed; it cannot prove from wording similarity that a reconstruction is cognitively genuine.

## Structural audit

`Shared/library/core1b_reconstruction.py` checks:

- Core1A/Core1B teaching-route coverage equality;
- prediction prompt + defensible answer;
- stated learner production;
- governed closure:
  - `MODEL_RESPONSE` requires a model response;
  - `CRITERIA` requires a rubric;
  - `RUBRIC` requires rubric + accepted + rejected examples;
- learner reconstruction route with `ask` + `why_this_ask`;
- any `from_step_ref` resolves to the Core1A teaching path;
- authored `differs_from_teaching_path` claim;
- shared misconception diagnosis + repair;
- boundary prompt + answer + what it confirms;
- compiler prompt-before-reveal ordering.

No text-similarity, keyword-count or question-mark heuristic is used to certify genuine reconstruction.

## Current baseline

- **91 canonical microtopics**
- **90 routed into the Core1A/Core1B study progression**
- **90/90 routed microtopics structurally complete for Core1B**
- **0 Core1A/Core1B coverage mismatches**
- **0 routed reconstruction-debt findings**
- **1 unrouted concept**

The unrouted concept is:

`MIC-FRAME-QUALIFICATION-BOUNDARY`

It belongs to the Relative Motion bucket but is physically stored in `vector-representation.v1.json`. Neither Core1A nor Core1B teaching routes claim it. Existing repository provenance already records routing as the unresolved next action.

Phase 3 therefore does **not** fabricate a Core1B elicitation failure for it. It emits the Phase‑4 handoff:

`CROSS_CORE_ROUTING_UNRESOLVED`.

## Reviewer obligations

Structural completeness still does not answer:

- whether the prediction requires a real conceptual decision;
- whether the learner route genuinely differs from the expert teaching route;
- whether the boundary test checks understanding rather than recall.

Those remain explicit reviewer obligations.

## Handoff

Phase 4 must reconcile the full Core1 → Core1A → Core1B progression, including the one unrouted Relative Motion boundary concept.
