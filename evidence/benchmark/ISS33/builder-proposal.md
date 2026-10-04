# ISS33 builder improvement proposal — constrained allocation interaction

Status: **PROPOSED AFTER EXACT RENDER INSPECTION**  
Observed render: `0af8b1fb4a99e3e75f6b008545e1eb6c4f9f82b5`  
Core1A SHA-256: `8ac3ca400fe9facb661826c3a27892ab9f02b7b03d1adaaf4ed437a51c906f9e`  
Core2 SHA-256: `1ff7dd5c5c8665863787670fc211dd2d330fc2976f81f3bfe5b641e788d49d55`

## Observed limitation

The hardest learner-relative target is the REPRESENT task shared by Q3/Q4/Q9: keep the electron-domain ledger separate from the sigma/pi bond-component ledger and allocate each local orbital exactly once. The governed Core1A page does provide a meaningful cumulative staged SVG for this bridge. That is useful for seeing the construction, but the learner can only advance/review stages; the page cannot require the learner to allocate three hybrid-orbital jobs to the sigma framework and the remaining unhybridised p orbital to the pi job, nor can it detect duplicate assignment.

This is not a request for another renderer. The sole production HTML path remains `Shared/tools/render_core.py`; any accepted module should be represented in canonical records/blueprints and projected through the existing runtime.

## Minimal reusable module

Proposed semantic primitive: **ONE_TO_ONE_ALLOCATION**.

It is deliberately subject-neutral. Chemistry can use it for orbital → bonding-role allocation; mathematics could use it for expression → transformation-role matching; physics could use it for force/vector → axis/component assignment.

Suggested authored record shape:

```json
{
  "kind": "ONE_TO_ONE_ALLOCATION",
  "prompt": "Assign each item once.",
  "items": [{"id": "a", "label": "..." }],
  "targets": [{"id": "sigma", "label": "Sigma framework", "capacity": 3}],
  "constraints": {
    "unique_item_assignment": true,
    "require_all_items": true
  },
  "feedback": {
    "policy": "AFTER_COMMIT",
    "accepted_assignments": {"a": "sigma"},
    "explain_on_reveal": true
  }
}
```

The schema should require stable item/target IDs, explicit capacities, keyboard-readable labels, and an authored accepted mapping. It must not infer the correct mapping from display order or chemistry-specific names.

## Insertion policy

For Core1A, insert the allocator immediately after the staged representation in a construction unit when an author supplies the interaction. It should precede the independent check so the learner first commits to the mapping, then checks it.

For Core2, do **not** auto-project an allocator merely because a question's primary demand is REPRESENT. A pre-attempt allocator is allowed only when an authored safe version has passed W-protection; otherwise the current static/staged representation remains the fallback.

## Runtime behavior

- Drag/drop may be offered, but every action must also work with keyboard/touch controls.
- An item cannot occupy two targets when `unique_item_assignment=true`.
- Commit is explicit; feedback appears only after commit.
- Reset is available and does not expose the accepted mapping.
- State is local/offline and records assistance/attempt state without grading mastery.
- Screen-reader announcements state the item, destination and whether capacity is full.
- Minimum target geometry follows the existing 48 CSS px touch policy.
- No network or external-script dependency.

## Migration and compatibility

Existing packages are unchanged because the new block is opt-in. Existing staged SVGs remain valid fallbacks. The blueprint/schema should add the interaction as an accepted optional block rather than reinterpret an existing representation record. Historical render digests remain historical; accepting this module requires new renderer/builder tests and new exact-render receipts.

## Acceptance checks

1. Schema rejects duplicate item IDs, unknown target IDs and impossible capacities.
2. Runtime prevents double assignment and supports keyboard-only completion.
3. Single-file/offline modes contain no network dependency.
4. Pre-attempt Core2 search corpus and markup do not contain accepted assignments unless policy permits post-attempt reveal.
5. Tablet audit reports no sub-48px targets, no overflow and visible focus.
6. A chemistry specimen for Q9-style allocation proves that three sigma jobs plus one p-orbital pi job close the inventory without duplicate assignment.
7. A non-chemistry fixture proves the primitive is not hard-coded to orbital vocabulary.

## Separate source-honesty finding

The exact Core2 render also exposes a metadata limitation: `OWNER_SUPPLIED` renders as “Owner-supplied question” but cannot additionally disclose the coordinator/AI-drafted authorship distinction required by this benchmark. That discrepancy is recorded in the semantic review. It should be addressed by source-custody metadata design, not by overloading the allocation interaction.
