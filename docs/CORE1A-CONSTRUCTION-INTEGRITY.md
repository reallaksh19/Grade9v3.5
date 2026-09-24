# Core1A conceptual-construction integrity

Issue: #254  
Programme: #252  
Stack base: Phase‑1 draft PR #258

## Governing question

> Given the concept this microtopic claims to teach, does Core1A explicitly construct the inference that makes the concept understandable?

The canonical crux is `microtopic.inferential_jump`.

A structurally complete Core1A record must support:

`entry assumptions → inferential jump → teaching path → why-valid → representation bridge → worked conceptual anchor → misconception/diagnostic/repair → independent check → exit closure`.

Field presence is necessary but not sufficient. The audit does **not** score prose length, keyword density or stylistic similarity. Reviewers still decide whether the route actually constructs the inferential jump and whether the worked anchor illuminates the concept rather than drifting into application drill.

## Structural audit

`Shared/library/core1a_construction.py` checks:

- entry assumptions;
- inferential jump;
- teaching-path presence;
- action + `why_valid` for every teaching step;
- subject-wide representation resolution;
- a Core1A scene bound to the same microtopic;
- explicit picture/word/symbol correspondence;
- misconception → diagnostic → repair closure;
- exit prompt, model closure and independent check;
- relation-owned learner checks where governing relations exist;
- a mapped question-family anchor exposed to Core1A with non-empty `answer.reasoning[]`;
- research contribution for MEDIUM/HARD concepts.

## Current baseline

Initial full-contract inventory:

- **91 microtopics**
- **2 structurally complete**
- **89 with legacy construction debt**

Finding counts:

- `REPRESENTATION_BRIDGE_MISSING`: **74**
- `REPRESENTATION_SCENE_BINDING_MISSING`: **9**
- `REPRESENTATION_CORRESPONDENCE_MISSING`: **1**
- `WORKED_CONCEPTUAL_ANCHOR_MISSING`: **85**

This is a migration baseline, not an acceptance declaration. Guardrails permits the committed legacy debt to remain temporarily but rejects any new structural finding for a new/materially revised microtopic.

## Important interpretation

The large debt count does **not** mean the existing teaching prose is worthless. It means the canonical library often has prose-level conceptual construction without the full explicit representation/worked-anchor closure required by the Core1A role contract.

Phase 2 therefore does not bulk-author 89 microtopics. Corpus migration should happen in bounded family slices after the architecture/audit stack is complete.

## Handoff to Core1B

Phase 3 consumes the same `inferential_jump` and asks a different question:

> Does the learner reconstruct this same conceptual inference before reveal/repair, rather than merely reading Core1A with prompts inserted?
