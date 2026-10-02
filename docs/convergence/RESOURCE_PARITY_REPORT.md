# Grade9V3.5 Resource Parity Report

```text
GENERATED_AT: 2026-10-02T07:44:00Z
TOOL: Shared/tools/build_resource_registry.py
REGISTRY_DIGEST: sha256:5aea3306cb4a9d3a6a7bd385c0808b7810b203bd9d66218d640272761e327244
TOTAL_DISCOVERED: 9
DUPLICATE_IDS: 0
BROKEN_ENTRYPOINTS: 0
```

## Discovered Resource Table

| ID | Kind | Learner Role | Audience | Presentation | Entrypoint | Classification |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `chemistry.home` | `STRUCTURED_PRODUCT` | `LEARN` | `LEARNER` | `FULL_PAGE` | `chemistry/index.html` | Chemistry |
| `common.question-bank` | `QUESTION_COLLECTION` | `QUESTION_BANK` | `LEARNER` | `FULL_PAGE` | `question-bank/index.html` | Common |
| `mathematics.home` | `STRUCTURED_PRODUCT` | `LEARN` | `LEARNER` | `FULL_PAGE` | `mathematics/index.html` | Mathematics |
| `owner.test.atlas` | `OWNER_TOOL` | `NONE` | `OWNER` | `INTERNAL_HOST` | `test/atlas/index.html` | Internal |
| `owner.test.rungs` | `OWNER_TOOL` | `NONE` | `OWNER` | `INTERNAL_HOST` | `test/rungs/index.html` | Internal |
| `phy.nlm.friction.core1a` | `STRUCTURED_PRODUCT` | `LEARN` | `LEARNER` | `FULL_PAGE` | `standalone/practice/friction/core1a.html` | Physics (`phy.nlm`) |
| `phy.nlm.friction.core2` | `STRUCTURED_PRODUCT` | `PRACTICE` | `LEARNER` | `FULL_PAGE` | `standalone/practice/friction/core2.html` | Physics (`phy.nlm`) |
| `phy.nlm.friction.threshold-explorer` | `OPAQUE_APP` | `EXPLORE` | `LEARNER` | `COMPANION` | `physics/nlm/explorers/friction-threshold/index.html` | Physics (`phy.nlm`) |
| `physics.home` | `STRUCTURED_PRODUCT` | `LEARN` | `LEARNER` | `FULL_PAGE` | `physics/index.html` | Physics |

## Audience Separation Verification
- **Learner Surfaces**: 6 resources (`LEARNER` audience, `LEARNER` search visibility)
- **Owner/LAB Surfaces**: 3 resources (`OWNER`/`LAB` audience, `EXCLUDED` search visibility)
- Zero leak of authoring tools into learner discovery.
