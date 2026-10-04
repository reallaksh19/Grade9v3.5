# Issue #35 — post-render builder proposal

## Proposal: `correspondence-sort` interaction for representation bridges

### Why this proposal exists

The frozen Core1A page already has staged SVG controls, text attempts and gated reveals. That is adequate for viewing a representation sequence, but the hardest learner-relative target in this run is not merely seeing the sequence: Q2 is `QRT-REPRESENT-D3`, where the learner must preserve meaning while translating three Lewis contributors into one qualitative delocalised orbital description.

In the exact rendered page the learner can step through:

1. three contributors;
2. the invariant sigma skeleton;
3. the perpendicular p-orbital direction;
4. the final delocalised pi overlay.

The limitation is that the builder does not provide a structured way for the learner to *commit the correspondence* before the final reveal. The textarea can collect free text, but it does not distinguish a learner who knows the facts yet maps the representations incorrectly from one who lacks the component facts.

This matters specifically for the simulated preset in #35: simple sigma/pi and local hybridisation are demonstrated, while cross-representation coordination is uncertain. A better interaction should therefore test the bridge, not reteach the component facts.

## Minimal reusable module

Add an optional interaction primitive named `correspondence-sort` to the existing interactive-page builder.

The module presents a small set of source-representation features and asks the learner to classify or map them into target roles before the protected target representation is revealed.

For Q2 the concrete instance would use groups such as:

- **Preserved/invariant:** N–O connectivity; three planar sigma directions; total charge/electron inventory.
- **Contributor-local bookkeeping:** formal N=O placement; formal charge placement.
- **Target orbital meaning:** perpendicular p-orbital set; one delocalised pi description.

The learner must make the mapping first. Feedback should diagnose the mapping error rather than simply reveal the answer.

## Proposed record shape

```json
{
  "interaction": {
    "module": "correspondence-sort",
    "prompt": "Sort each feature by what it means when you move from Lewis contributors to one orbital description.",
    "groups": [
      {"id": "INVARIANT", "label": "Preserved across contributors"},
      {"id": "CONTRIBUTOR_LOCAL", "label": "Only the formal placement changes"},
      {"id": "TARGET_MODEL", "label": "Belongs to the orbital description"}
    ],
    "items": [
      {"id": "sigma-skeleton", "label": "Three planar N–O sigma directions", "target": "INVARIANT"},
      {"id": "formal-double", "label": "Which N–O is drawn double", "target": "CONTRIBUTOR_LOCAL"},
      {"id": "p-set", "label": "Perpendicular p-orbital set", "target": "TARGET_MODEL"}
    ],
    "submit_before_reveal": true,
    "diagnostic_mode": "ITEM_LEVEL",
    "keyboard_order": ["sigma-skeleton", "formal-double", "p-set"]
  }
}
```

The proposal is intentionally small. It does **not** require a new renderer, a chemistry-specific framework, drag-only interaction or a new publication path. The same primitive can support Physics diagram↔equation correspondences and Mathematics graph↔symbol correspondences.

## Insertion point

Use the module inside a Core1A construction unit immediately before the protected representation stage or worked bridge. It should consume existing `Representation.correspondence` data where possible instead of duplicating the academic mapping in a separate authoring surface.

For Core2, the same primitive may optionally appear as a diagnostic support step after a learner asks for help, but it must not open by default on D3 items because the representation bridge is protected work.

## Rendering / UX requirements

- Touch and keyboard must both work; do not depend on drag-and-drop.
- Minimum target geometry must continue to satisfy the repository touch contract.
- Screen-reader output must announce item, current group and move controls.
- Submission must be explicit before correctness feedback.
- The module must not put protected target assignments into the searchable pre-attempt corpus.
- Print should fall back to an unlabeled mapping worksheet, not the solved mapping.
- Wrong mappings should be retained long enough to support a diagnostic/repair message.

## Validation additions

Add reusable checks rather than subject-specific assertions:

1. every item has exactly one declared target group;
2. all group/item IDs are unique and referenced targets exist;
3. protected target assignments are absent from pre-attempt search text;
4. keyboard-only completion succeeds;
5. touch targets meet the existing size contract;
6. answer state does not open before submission;
7. post-submit feedback identifies the mismapped relation, not merely `wrong`;
8. print output does not leak solved assignments.

## Migration

This is additive. Existing pages render unchanged. Authors opt in by adding the interaction block to a construction unit or by allowing a later adapter to derive a starter instance from `Representation.correspondence`.

No existing `Representation` record needs migration. The first safe pilot should use this frozen #35 Q2 representation because the source/target correspondences and D3 protected bridge are already explicit.

## Separate findings that are **not** the module rationale

The exact quality gate also reported two contract-cleanup items:

- candidate figure records use `ORBITAL_MODEL`, while the pinned Chemistry vocabulary already recognizes `ORBITAL_DIAGRAM`;
- generic Core1A expected-component checks flag missing `EQUATIONS` even when the learning objective is a qualitative orbital correspondence.

Those should be reconciled as vocabulary/component-contract issues. They do not justify a new interaction module by themselves.

The browser audit also exposed focus-probe and landscape anchor-safety observations. Those belong to shell/accessibility hardening, not to this academic interaction proposal.

## Evidence boundary

This proposal was written after the frozen learner candidate was preserved at `b9246195e1ec208a920ef55afd53ce8e7b84aa9f`. During the later status lookup, the connector incidentally exposed the paired PR summary. That external summary is quarantined and was not used as design evidence here. Because the proposal was authored after that exposure, it should not be treated as perfectly blind pair-comparison evidence even though its rationale is explicitly derived from #35's frozen Q2/render evidence.
