# ISS66 U04B — canonical difficulty component rubric + evidence shape

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U04B only — define and schema-test subject-neutral 0/1/2 anchors plus per-component evidence  
**Tested implementation head:** `5599574efbc81b2531ee208a492283fb84705115`

## Change 1 — canonical subject-neutral component rubric

Updated:

`Shared/vocabularies/learner-question-metadata.v1.json`

Vocabulary version:
- before: `1.0.0`
- after: `1.1.0`

Added:

`question_difficulty_component_rubric`

Rubric schema:

`grade9v3-question-difficulty-component-rubric/v1@1.0.0`

The scoring rule is explicit:

> Score each dimension independently from the learner-owned work required by the exact question before support. Use the highest anchor fully supported by question-specific evidence; do not score the intended cohort, topic prestige, answer length, or another dimension twice.

Each of the five canonical dimensions now has explicit subject-neutral anchors for 0 / 1 / 2:

1. `concept_model_selection`
2. `representation_translation`
3. `reasoning_chain_length`
4. `algebra_computational_load`
5. `trap_exception_sensitivity`

The anchors distinguish:
- no material demand;
- one familiar/local demand;
- a decisive/nontrivial demand.

The rubric contains no Physics, Chemistry or Mathematics-specific terminology.

## Change 2 — backward-compatible per-component evidence shape

Updated:

`Shared/library/package.schema.json`

Added optional:

`question_difficulty.component_evidence`

When present it must contain a non-empty question-specific evidence string for **all five** difficulty components and no unknown component keys.

Legacy records remain valid when `component_evidence` is absent.

This is deliberate:
- U04B adds a canonical evidence shape without retroactively invalidating the existing repository;
- later acceptance/adjudication policy can require this evidence for newly reviewed classifications;
- no bulk migration is performed merely to make old records conform to a new authoring aid.

## Change 3 — dedicated focused tests

Added:

`tests/test_difficulty_contract.py`

The isolated contract tests prove:

### Rubric integrity
- canonical rubric exists;
- rubric covers exactly the five compiler component keys;
- every component has exactly `0`, `1`, `2` anchors;
- every anchor is non-empty;
- rubric is subject-neutral.

### Schema compatibility
- a valid legacy `question_difficulty` record without component evidence remains schema-valid;
- a record with all five evidence fields remains valid;
- an incomplete `component_evidence` object is rejected.

The tests use the canonical `package.schema.json` `question_difficulty` definition through Draft 2020-12 validation.

## Change 4 — focused CI coverage

Updated:

`.github/workflows/qrt-pipeline-hardening.yml`

The workflow now:
- triggers when the package difficulty schema, difficulty vocabulary or focused difficulty-contract test changes;
- installs `jsonschema` for the schema contract test;
- executes `tests.test_difficulty_contract` alongside the existing QRT hardening modules.

No unrelated large regression module was added to this focused workflow.

## Intermediate failure evidence

### Attempt 1 — missing focused dependency

Head:
`7a2153ad21e39888bab696aa32ff3759c9544c21`

Run:
`37435013151`

Result:
- focused workflow failed to import `tests.test_question_review_matrix`;
- error: `ModuleNotFoundError: No module named 'jsonschema'`.

Correction:
- explicitly install `jsonschema` in the focused workflow.

This was a CI-environment dependency gap, not a rubric/schema behavior failure.

### Attempt 2 — unrelated pre-existing test surfaced

Head:
`f6fa2095941ef213b6111d63f1f0086b97eb5bf8`

Run:
`37435135270`

Result:
- new schema dependency installed successfully;
- the expanded `tests.test_question_review_matrix` module exposed an existing PR3 fixture-order assertion:
  the fixture carried all twelve asks but in a different dictionary insertion order from `qrt.ASKS`;
- 66 tests ran; one unrelated order assertion failed.

Correction:
- restored `tests/test_question_review_matrix.py` byte-for-byte to its pre-U04B blob `94940b77f1a05685cefced50b53799ebe4d71d4f`;
- created the dedicated `tests/test_difficulty_contract.py` module;
- focused workflow now runs only the new difficulty contract tests rather than absorbing unrelated historical QRT fixture behavior.

No PR3 fixture or unrelated QRT logic was changed.

## Final exact-head validation

Implementation head:

`5599574efbc81b2531ee208a492283fb84705115`

Workflow:
`qrt-pipeline-hardening`

Run:
`37435261717`

Job:
`112175394405`

Result:
- workflow: **SUCCESS**
- job: **SUCCESS**
- install schema validator: **SUCCESS**
- intake policy: **SUCCESS**
- focused QRT hardening regressions: **38 tests, OK**
- Chromium audit script syntax: **SUCCESS**
- pinned Chromium install: **SUCCESS**
- mandatory interactive Chromium smoke audit: **SUCCESS**

The prior focused U03 suite had 36 tests; the two dedicated U04B difficulty-contract tests account for the increase to 38.

## Material blobs at tested head

- difficulty vocabulary: `ef48260d85b2cf89b460fde40f52c5401fd90488`
- package schema: `bcad533091e2a66c883f4ea49f482c8a212e4e2c`
- restored general QRT test file: `94940b77f1a05685cefced50b53799ebe4d71d4f`
- focused difficulty tests: new `tests/test_difficulty_contract.py`
- QRT hardening workflow: final focused workflow at tested head

## U04B scope result

**U04B COMPLETE.**

What U04B establishes:
- one shared rubric now defines what 0/1/2 means for each difficulty component;
- newly adjudicated records have a canonical complete per-component evidence shape;
- existing records remain compatible;
- requested D-band and score→band logic are unchanged.

What U04B does **not** establish:
- that existing #49–#56 component scores become automatically correct under the new rubric;
- that primary cognitive demand is now reproducible;
- that two independent valid reviews can yet be represented as an explicit adjudication conflict;
- that legacy records must be bulk-migrated.

Parent U04 remains incomplete.

Parent denominator remains:
- **P = 3/10 = 30%**
- **E = 3/10 = 30%**

Next bounded task:
- **U04C — bind authored primary cognitive demand to the existing canonical reasoning/crux move and test the resolver contract.**
- Do not add adjudication-state machinery in U04C unless that binding replay first proves it necessary.
