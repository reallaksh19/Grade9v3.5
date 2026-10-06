# ISS66 U06B — exact-one scene ownership + focused representation binding regressions

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U06B only — repair ambiguous scene-instance ownership and retain wrong-case protection  
**Tested implementation head:** `2ef46b812f73ce4463ef0a0f9dd6e84f76e16446`

## Production change

Updated:

`Shared/library/package.schema.json`

For `$defs.scene_instance`, changed only the owner-choice combinator:

- before: `anyOf`
- after: `oneOf`

The two existing owner fields are unchanged:

- `microtopic_ref`
- `question_ref`

No new representation role, owner, case, data, asset, or renderer-selection field was introduced.

## Contract effect

A scene instance is now schema-valid only when exactly one owner relationship is present:

- teaching/microtopic instance: `microtopic_ref` only;
- question/case instance: `question_ref` only.

The schema now rejects:

- an ambiguous record containing both owner refs;
- an ownerless record containing neither.

This makes the executable schema match its existing prose contract.

## Focused regression surface

Added:

`tests/test_representation_binding_contract.py`

Four focused tests cover:

1. **exact owner cardinality**
   - question-only valid;
   - microtopic-only valid;
   - both invalid;
   - neither invalid.

2. **frozen compatibility**
   - all four staged Set B adopted question instances remain schema-valid.

3. **same-topic wrong-question replay**
   - a concept-correct representation using the same selected instance cannot satisfy another question merely because the representation/topic matches;
   - renderer returns no figure and records `MOUNT_REPRESENTATION`.

4. **wrong-case mutations**
   - wrong question owner;
   - missing datum record;
   - absent authored asset;
   - wrong Core role;
   all fail closed through governed `MOUNT_REPRESENTATION` / `BUILD_SCENE` gaps.

## Dedicated CI lane

Updated:

`.github/workflows/learner-quality.yml`

Added a non-informational step:

`Representation instance binding contract`

which runs:

`python3 -m unittest tests.test_representation_binding_contract`

The existing non-informational:

`Core2 staged support contract`

remains immediately adjacent, so representation compatibility with the PR #65 staged repair is checked on the same exact head.

## Exact-head validation

Workflow:

`learner-platform-code-tests`

Run:

`37440990330`

Job:

`112194412104` — `code-tests`

Head:

`2ef46b812f73ce4463ef0a0f9dd6e84f76e16446`

Relevant steps:

- **Representation instance binding contract — SUCCESS**
- **Core2 staged support contract — SUCCESS**

The broader informational Python aggregate was still running when this U06 evidence was frozen and is not required for U06 acceptance.

## U06 acceptance result

U06 required evidence that a concept-correct but wrong-case asset cannot silently satisfy a question-instance representation and that compatibility is retained.

That is now satisfied by:

- explicit question owner binding;
- explicit Core role binding;
- explicit datum refs;
- explicit selected instance and authored asset;
- render-time exact-question validation;
- exact-one owner schema semantics;
- focused same-topic wrong-question failure;
- frozen staged Set B compatibility.

## U06 result

**U06 COMPLETE and successor-safe evidenced.**

Parent denominator:
- **P = 6/10 = 60%**
- **E = 6/10 = 60%**

No claim is made that:
- the schema proves the academic correctness of an SVG;
- datum existence proves the figure faithfully depicts the datum;
- every legacy representation has a question-bound scene instance;
- source snapshots are replaceable by authored cases.

Next bounded unit:

**U07A — inspect the existing diagnostic/misconception, probe, learner-response, repair and recheck authorities; replay whether a wrong answer can currently become a confirmed diagnosis without discriminating evidence before adding diagnostic schema.**
