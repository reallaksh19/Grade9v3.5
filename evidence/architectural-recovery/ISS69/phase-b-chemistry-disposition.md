# ISS69 PHASE-B — B02.3 Chemistry disposition proof

Material frontier inspected: `fix/iss69-phase-b-subject-neutrality@d2fd9bd2ee377be6b3051e8d7bde07251cc4b323`

## Question

Did removing the Chemistry D1–D4 repair prose from Shared discard canonical Chemistry truth, or should any of it be promoted into a subject adapter?

## Authorities inspected

### Chemistry/adapter/CoreContracts.json

The durable Chemistry-wide contract already owns cross-topic semantic boundaries:

- `representation_level`;
- `model_not_mechanism`;
- species/composition and conservation basis;
- symbol/species roles;
- representation kinds and subject validators.

These are appropriate subject-wide invariants.

### Chemistry/adapter/DemandReview.json

Chemistry specializes the canonical cognitive demands using:

- species identity/composition;
- macro ↔ particulate ↔ symbolic translation;
- conservation/charge;
- evidence-versus-mechanism;
- model/conditions.

It does not encode hybridisation/allene/torsion as universal Chemistry demand policy.

### Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json

Blob inspected: `38217edac6dc59763be4ed59ad6071dc4dba744a`.

Direct recursive string scan counts:

| term | count |
| --- | ---: |
| VSEPR | 0 |
| hybridization | 0 |
| hybridisation | 0 |
| resonance | 0 |
| allene | 0 |
| torsion | 0 |
| Pauli | 0 |
| overlap | 0 |

Therefore the removed Shared repair prose was not duplicating the canonical Chemistry exam-bank authority.

## Disposition of removed clusters

| Removed Shared cluster | Disposition | Reason |
| --- | --- | --- |
| neighbour/domain vs bond-component/orbital-basis inventory; “π component is not axial density”; VSEPR warning | HISTORICAL / TOPIC-SPECIFIC | Not present in canonical exam bank; too narrow for Chemistry-wide adapter. |
| hybrid outputs + residual functions ledger; lone-pair vertices; geometry vs orbital basis | HISTORICAL / TOPIC-SPECIFIC | Hybridisation/VSEPR-specific; no evidence of Chemistry-wide recurrence. |
| resonance contributors; delocalised π space; allene terminal planes; Pauli warning | HISTORICAL / QUESTION/TOPIC-SPECIFIC | No canonical exam-bank record and no subject-wide adapter basis. |
| local counts/occupancy/adjacency/alignment; overlap factor vs energy; torsion/electron inventory | HISTORICAL / QUESTION/TOPIC-SPECIFIC | Stress-cycle/model-boundary guidance, not a universal Chemistry contract. |

## Canonical-truth preservation conclusion

No canonical Chemistry record was deleted or modified in B02.1.

The generic truths embedded inside the stress prose were retained in Shared at the correct abstraction level:

- each reasoning move carries an actual local warrant;
- preserve model assumptions and representation invariants when material;
- keep bookkeeping/model/evidence boundaries explicit;
- crux identity is bound to an actual reasoning move;
- difficulty band does not prescribe route length.

The Chemistry-wide truths remain in `Chemistry/adapter/CoreContracts.json` and `Chemistry/adapter/DemandReview.json`.

## Decision

**Do not add a new Chemistry adapter field or copy the old repair block into an adapter.**

Subject-specific does not imply subject-wide. If a future Chemistry responsibility proves that one of these rules recurs across independently reviewed canonical records, it can be promoted under a Chemistry-owned contract then. Until that evidence exists, Issue #29/#66 comments and this architectural evidence retain the historical rationale without making it product authority.
