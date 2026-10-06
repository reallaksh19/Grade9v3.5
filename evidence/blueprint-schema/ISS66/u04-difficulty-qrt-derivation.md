# ISS66 U04 — canonical difficulty and QRT band derivation

**Status:** COMPLETE + EVIDENCED  
**Candidate code head:** `813fbea92f0ebd6f2c4c6e089a2ae90ffc5f2e70`  
**PR:** #67

## Stress-test problem

Matched #49–#56 runs often assigned different bands, demands and scores to the same inputs. Before U04, the QRT resolver trusted the stored `difficulty.band` directly even though the repository already had:

- a five-component score model;
- canonical score ranges in `Shared/vocabularies/learner-question-metadata.v1.json`;
- an exam-bank validator that separately reimplemented score→band validation.

That let a contradictory stored band select a different QRT cell.

## Shared difficulty authority

Added `Shared/tools/question_difficulty.py`.

It treats these as authored academic evidence:
- `concept_model_selection`
- `representation_translation`
- `reasoning_chain_length`
- `algebra_computational_load`
- `trap_exception_sensitivity`

It treats these as deterministic projections:
- score = component sum;
- band = the score range from `learner-question-metadata.v1.json`.

Canonical ranges remain the existing repository policy:
- D1: 0–2
- D2: 3–5
- D3: 6–7
- D4: 8–10

The helper validates range continuity and full 0–10 coverage rather than copying a second hard-coded map.

## Requested versus derived band

Both package and competitive-exam difficulty schemas now allow optional `requested_band`.

Semantics:
- `requested_band`: planning/stress-cohort target;
- `band`: derived classification from the five components;
- requested and derived may differ;
- requested band never selects the QRT cell.

Existing `band` remains for compatibility.

## QRT resolver behavior

`question_review_matrix._question_difficulty()` now calls the shared derivation.

The resolver fails closed when:
- component shape/value is invalid;
- stored score differs from component sum;
- stored band differs from canonical score→band projection.

The resolution exposes:
- derived `classification.band`;
- optional `classification.requested_band`;
- `classification.difficulty_score`.

Its `basis_digests` now includes `difficulty_metadata`, so changing the score-range authority changes the recorded resolution basis.

## Existing exam-bank validator

`competitive_exam_bank.py` now reuses the same shared difficulty helper. Its historical `DIFFICULTY_BAND` symbol remains as a compatibility alias generated from the vocabulary-backed map.

Direct script entry points remain supported through a package/script import fallback.

## Primary cognitive demand boundary

This unit does **not** mechanically infer the primary cognitive demand.

Reason: unlike score→band, there is no deterministic numeric transform from the question bytes to RETRIEVE/EXPLAIN/APPLY/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY. The existing cognitive-demand record must still supply:
- primary demand;
- secondary demands;
- a non-empty academic basis.

Therefore U04 removes a deterministic source of divergence without pretending schema code can adjudicate semantic demand disagreements. Matched A/B demand disagreements remain review/adjudication evidence for U10; they must not be forced to the intended cohort.

## Regression coverage

`tests/test_question_review_matrix.py` now proves:
1. valid component evidence derives D3 for score 6;
2. a stored score inconsistent with components is rejected;
3. a stored band inconsistent with score is rejected;
4. requested D4 with derived D3 still resolves to `QRT-REPRESENT-D3`;
5. requested band and derived score are preserved in the resolution payload;
6. the shared score map covers 0–10 exactly;
7. difficulty metadata participates in the resolution digest.

Existing QRT and question-bank suites exercise the shared helper through both consumers.

## Exact-head hosted evidence

At `813fbea92f0ebd6f2c4c6e089a2ae90ffc5f2e70`:

### qrt-pipeline-hardening — run 37421354520
`focused-regressions`: **SUCCESS**
- Intake policy: SUCCESS
- Focused QRT hardening regressions: SUCCESS
- Chromium audit script syntax: SUCCESS
- mandatory interactive Chromium smoke audit: SUCCESS

### pass1-question-bank-contract — run 37421354534
`validate`: **SUCCESS**
- `python Shared/tools/competitive_exam_bank.py`: SUCCESS
- `tests.test_competitive_exam_bank_contract`: SUCCESS
- `tests.test_competitive_exam_question_bank`: SUCCESS

Earlier code frontier `9d62a5061adf9f3b1022b7d7f6437a8016145e33` also passed `question-bank-platform` and `qrt-pipeline-hardening`; the only subsequent production-code change was additive QRT classification output, and the exact final QRT run above passed.

## Acceptance

- one canonical score→band authority: **YES**
- stored band contradiction can silently select QRT cell: **NO**
- requested cohort can force derived band: **NO**
- requested/derived band distinction representable: **YES**
- QRT result bound to score-range authority: **YES**
- primary cognitive demand falsely inferred by code: **NO**

Next: **U05 — protected act and support eligibility**.
