# ISS66 U04A — difficulty/QRT derivation gap inspection

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U04A only — inspect live difficulty/QRT derivation against matched #50/#54 and #51/#55 disagreement  
**Basis head:** `d0d6d04abc1a59f9a220ff545a82511c5bb32683`

## Live authority

### Mechanical difficulty projection

`Shared/tools/question_difficulty.py` blob:

`5219d99603d7de6c2d1e07294d19d4508a5c312e`

The shared compiler:

1. requires exactly five integer components, each 0–2:
   - `concept_model_selection`
   - `representation_translation`
   - `reasoning_chain_length`
   - `algebra_computational_load`
   - `trap_exception_sensitivity`
2. sums them;
3. derives band from the canonical ranges;
4. rejects stored score/band that disagree with the derived projection;
5. preserves `requested_band` only as planning metadata.

Canonical band ranges from `learner-question-metadata.v1.json@1.0.0`:

- D1 = 0–2
- D2 = 3–5
- D3 = 6–7
- D4 = 8–10

Therefore the **score → band transformation is deterministic**.

### QRT cell resolution

`Shared/tools/question_review_matrix.py` blob:

`4121dc1ea9d6aa1cca83799a48a88816a82629a8`

The resolver:
- obtains the derived band through `question_difficulty.derive(...)`;
- obtains primary cognitive demand from authored `grade9v3:cognitive_demand.primary`;
- requires that demand to be one of the seven canonical demand values;
- requires a non-empty authored demand `basis`;
- combines primary demand + derived band to select one QRT cell;
- carries `requested_band` separately and does not use it to select the cell.

Existing `tests/test_question_review_matrix.py` already verifies:
- score/band mismatch is rejected;
- requested D-band cannot override actual derived band;
- primary demand and band are orthogonal axes;
- score ranges cover 0–10 exactly once.

## Matched-run input comparison

The important comparison is not only final D-band. It is the authored input vector that the deterministic compiler receives.

### D2 intended pair — #50 vs #54

Frozen inputs:
- #50 PR #63 head `a58eebee28112080393cc47e4295862efc43dbed`
- #54 frozen head `3d17905ebee4ac6cf39057ac05d49947b1b50430`

Records:
- #50 `evidence/benchmark/ISS50/question-ledger.json`
- #54 `evidence/benchmark/ISS54/question-ledger.json`

Observed over Q1–Q10:

- exact five-component vector agreement: **1/10** (Q4 only);
- component-vector disagreement: **9/10**;
- derived-band agreement: **7/10**;
- derived-band disagreement: **3/10** (Q3, Q6, Q10);
- primary-demand agreement: **8/10**;
- primary-demand disagreement: **2/10** (Q7, Q10).

Examples:

**Q6**
- #50: components `2,1,1,0,2` → score 6 → D3, JUSTIFY
- #54: components `1,1,1,0,1` → score 4 → D2, JUSTIFY

The band divergence is completely explained by authored differences in:
- concept/model selection: 2 vs 1;
- trap/exception sensitivity: 2 vs 1.

The band compiler behaves consistently.

**Q10**
- #50: `2,1,2,0,2` → 7 → D3, JUSTIFY
- #54: `1,0,1,0,1` → 3 → D2, EXPLAIN

This is disagreement in both difficulty evidence and decisive cognitive demand, not a resolver arithmetic defect.

### D3 intended pair — #51 vs #55

Frozen inputs:
- #51 PR #64 head `b94ede24c7ba64ed36ba5f137b65d95816164599`
- #55 frozen head `91951abc430ff50ae526110488d9b12e27e30af5`

Records:
- #51 `evidence/benchmark/ISS51/qrt-review.v1.json`
- #55 `evidence/benchmark/ISS55/generated/qrt-review.v1.json`

Observed over Q1–Q10:

- exact five-component vector agreement: **0/10**;
- component-vector disagreement: **10/10**;
- derived-band agreement: **4/10**;
- derived-band disagreement: **6/10**;
- primary-demand agreement: **6/10**;
- primary-demand disagreement: **4/10**.

Examples:

**Q8 — strongest semantic-target convergence**
- #51: `2,2,2,1,2` → 9 → D4, JUSTIFY
- #55: `2,1,2,0,2` → 7 → D3, JUSTIFY

Both independently agree on the decisive demand and target family, while disagreeing on two difficulty components:
- representation translation: 2 vs 1;
- algebra/computational load: 1 vs 0.

That is direct evidence that the current problem is **component calibration**, not QRT-cell lookup.

**Q1**
- #51: `1,0,2,1,1` → 5 → D2, SYNTHESIZE
- #55: `1,1,2,1,1` → 6 → D3, APPLY

A single-point representation-translation disagreement crosses the D2/D3 boundary, while the primary demand also differs.

## Root-cause classification

### What is already deterministic

**REUSE EXISTING**
- component sum;
- score → D-band range;
- requested-band separation;
- QRT cell lookup from primary demand + derived band.

No second band resolver or requested/actual classification pair is justified.

### Where reproducibility currently fails

**TRUE AUTHORING-CONTRACT GAP**

The shared schema constrains each difficulty component only to integer 0–2 and requires one overall free-text `basis`.

The shared vocabulary defines:
- component names indirectly through consumers;
- D-band names/ranges;

but it does **not** provide canonical subject-neutral score anchors explaining what 0, 1, and 2 mean for each of the five components.

Therefore two agents can both produce schema-valid records and mechanically valid bands while assigning materially different component scores to the same question.

This is exactly what the matched runs demonstrate.

### Primary-demand selection

The seven canonical demand definitions already include a subject-neutral `decisive_act` in `question-demand-matrix.v1.json`.

However, the QRT resolver currently validates only:
- primary enum;
- secondary list;
- non-empty free-text basis.

It does not require the primary demand to bind to the question's canonical reasoning/crux move.

Matched demand disagreement is smaller than component disagreement, but still material:
- D2 pair: 2/10
- D3 pair: 4/10

This is a second authoring-contract gap, but it should be handled after the difficulty component rubric rather than combined into one large change.

## Schema observation

`Shared/library/package.schema.json` already has a canonical `question_difficulty` object:
- band;
- requested_band;
- score;
- five components;
- one overall basis.

It does not currently require per-component evidence/rationale.

The namespaced cognitive-demand record is consumed by `question_review_matrix.py`; the package schema's generic `extensions` object does not currently provide a dedicated typed cognitive-demand definition.

U04A does not yet change either shape.

## U04A disposition

1. **Do not change score → band logic.**
2. **Do not force requested cohort labels.**
3. **Do not treat A/B disagreement as a resolver bug.**
4. The first justified shared change is a **subject-neutral 0/1/2 scoring rubric for each five-component difficulty dimension**, with record-level evidence tied to those dimensions.
5. Primary-demand/crux binding is a separate follow-on microtask after difficulty evidence is calibrated.
6. Explicit cross-review `ADJUDICATION_REQUIRED` state should be considered only after two independently valid classifications can be compared under the same rubric; do not invent it before the evidence shape is stable.

## U04A result

**U04A COMPLETE. No production change.**

Parent U04 remains incomplete.

Parent denominator remains:
- **P = 3/10 = 30%**
- **E = 3/10 = 30%**

Next bounded task:
- **U04B — define and schema-test canonical subject-neutral 0/1/2 anchors + per-component evidence for the five difficulty dimensions only.**
- Do not modify primary-demand binding in U04B; keep that for a later microtask.
