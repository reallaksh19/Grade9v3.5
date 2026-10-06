# ISS66 U01C — shared-contract disposition after authority + stress-pair replay

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Microtask:** U01C only — existing-field reuse + contradiction/negative-knowledge decision  
**Basis branch:** `feat/iss66-blueprint-semantic-contracts`  
**Current pre-U01C head:** `8b6c10c5f7567d2082abc3fe94d27640cc75404b`

U01C reconciles:
- U01A exact live authority inventory;
- U01B matched #49–#56 structural decision deltas;
- the V3.2 worth gate: do not add shared ceremony/fields unless a replayed failure requires them.

## Disposition table

| Proposed shared-contract area | Disposition | Reason |
| --- | --- | --- |
| Blueprint-selected layout as sole authority | **TRUE CONTRADICTION — FIX NEXT** | Core1A declares `expanded=SINGLE_PANE`; helper-level observation respects it, but `core-page-audit.mjs` still derives a later split expectation from nonzero `support_fraction`. #51/#55 independently reproduced the authority mismatch. |
| Review provenance (`AUTHOR_ONLY` / `RENDERED` / `INDEPENDENT_RENDERED`) | **REUSE EXISTING** | Already typed in `qrt-pipeline-run.schema.json`; guard excludes author-only from rendered evidence. Do not add duplicate review-state fields. |
| Rendered review byte binding | **REUSE EXISTING** | Existing rendered artifact + `artifact_sha256` guard rejects review not bound to declared rendered bytes. U03 may test dependency invalidation separately, but there is no U01 evidence for another parallel artifact-binding field. |
| Requested cohort/band versus derived band | **REUSE EXISTING** | `question_difficulty.py` already derives band mechanically from five component scores and preserves `requested_band` separately. Do not add another requested/actual band pair. |
| Five-component difficulty derivation | **REUSE EXISTING** | The mechanical score/band projection already exists. D2 A/B disagreement therefore points primarily to authored component evidence/judgment variance, not absence of a band derivation function. |
| Primary cognitive-demand derivation | **DEFER / NO CHANGE IN U01** | D2 and D3 show reviewer divergence, but current records already require one primary demand plus basis. The stress tests do not yet prove that a new schema object would make the academic judgment reproducible. Direct record-level replay is needed before changing shared schema. |
| Hardest-target selection | **DEFER / NO CHANGE IN U01** | A/B runs often choose different hardest items. That establishes authoring variance, not a demonstrated missing blueprint field. Existing toughest-concept tooling/brief evidence should be replayed before structural expansion. |
| Protected learner act / Core2 support deferral | **REUSE EXISTING, BOUNDED** | PR #65 already added `protected_move_refs`, authored support completions and deferred support behavior. Later U05 should test whether this bounded shape is sufficient before generalizing it. |
| Representation case/instance binding | **REUSE EXISTING** | `scene_instances` already bind question, role, data and asset; renderer rejects adopted case selections that do not bind correctly. U06 should test coverage/compatibility, not create a second representation-binding scheme. |
| Diagnostic hypothesis → probe → evidence → diagnosis | **DEFER / DIRECT GAP REPLAY REQUIRED** | Stress-test comments contain strong diagnostic self-claims, but U01 has not yet established the exact existing diagnostic schema/consumer deficiency. A new cross-product diagnostic state machine would be premature without direct failing fixtures. |
| Subject-neutral interaction primitives | **DEFER / NO CHANGE** | Builder proposals are mostly non-convergent. #49/#56 both suggest parameter exploration, but recurrence alone does not yet prove a shared primitive is worth permanent schema/runtime cost. U08 owns this worth-gated decision. |
| Topic-specific widgets/checks | **NO CHANGE** | `POLYNOMIAL_COEFFICIENT_GRID`, `rational-domain-inspector`, and similar one-run proposals are not eligible as shared blueprint/schema additions from current evidence. |
| PAGES asset self-packaging | **DEFER / OUTSIDE CURRENT SEMANTIC-CONTRACT PRIORITY** | Appears as a secondary #55 proposal, not a matched semantic-contract convergence. Handle separately if it becomes a portability responsibility. |

## U01 architecture conclusion

The stress tests do **not** justify a broad schema rewrite.

The live system after PR #65 already contains several of the contracts that the stress-test recommendation called for. The correct next move is therefore **repair-and-replay**, not field proliferation.

The first confirmed implementation target is narrow:

> make every Core1A browser-layout expectation derive from `responsive_policy.expanded`, so a nonzero historical `support_fraction` cannot silently override `SINGLE_PANE`.

After that fix, later ISS66 units must use failing fixtures/replay to earn any additional shared schema change.

## Negative knowledge retained

- A/B semantic disagreement is not itself proof of schema insufficiency.
- A full author H/S/P/M YES review is not independent acceptance, but review provenance/byte binding already have typed machinery.
- `requested_band` is already planning metadata and cannot be used to force the derived band.
- Existing Core2 protected support and representation-instance bindings are the starting authority; do not fork parallel mechanisms.
- No interaction component is approved by U01.

## U01 completion

U01 required:
1. exact-head authority inventory — U01A complete;
2. matched #49–#56 structural delta ledger — U01B complete;
3. existing-field reuse analysis — this record;
4. explicit contradictions and negative knowledge — this record.

Therefore **U01 is objectively complete and successor-safe evidenced**.

Parent denominator after this record:
- **P = 1/10 = 10%**
- **E = 1/10 = 10%**

Next bounded implementation task: **U02A — repair only the Core1A expanded-layout expectation path and add focused contract tests.**
