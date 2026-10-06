# ISS69 PHASE-B — B03 adapter/QRT boundary proof

## Adapters inspected

- Chemistry/adapter/DemandReview.json
- Mathematics/adapter/DemandReview.json
- Physics/adapter/DemandReview.json
- corresponding QualityVocabulary.json and CoreContracts.json

## Canonical-demand result

Each DemandReview adapter:

- declares schema `demand-review-adapter/v1`;
- declares its own subject;
- exposes exactly these seven demand keys, in canonical order:

```text
RETRIEVE
EXPLAIN
APPLY
MODEL
REPRESENT
SYNTHESIZE
JUSTIFY
```

- contains **zero** `QRT-<DEMAND>-D1..D4` identifiers;
- references its own subject QualityVocabulary and CoreContracts as basis;
- therefore specializes review semantics without claiming canonical QRT-cell identity.

## Renderer-authority result

Each subject CoreContracts.json states:

```text
renderer_authority = COMPOSITION_ONLY
```

The subject adapter therefore owns subject academic semantics while Shared renderer/blueprint composition remains separate.

## Boundary

Allowed:

```text
canonical demand
    ↓
subject DemandReview specialization
    ↓
question-specific review evidence
```

Not allowed:

```text
subject adapter
    ↓
invent subject-specific QRT cell ID
    ↓
replace canonical 4×7 identity
```

## Result

B03.1 canonical QRT namespace regression basis: PASS.
B03.2 adapter specialization independence: PASS.

The existing focused regression in tests/test_blueprint_components.py additionally asserts that DemandReview adapters do not contain canonical-looking QRT template IDs.
