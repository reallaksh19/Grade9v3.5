# ISS66 U06A — representation instance/case binding inspection

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U06A only — inspect existing representation instance/case/data binding and replay wrong-case protection before schema change  
**Basis head:** `046caa9c3aaf8a93151d2a30d2d8125e3218eb27`

## Existing shared authority

The PR #65 representation repair already introduced a concrete scene-instance layer beneath the canonical representation record.

`Shared/library/package.schema.json` defines `scene_instance` with:

- `id`
- `cores[]`
- `datum_refs[]`
- `scene.kind/frame/caption`
- optional `asset_ref`
- `question_ref` or `microtopic_ref`

For question-instance use, the renderer does not select the first concept-compatible asset. The selected instance is named by the question's support/visual binding and then resolved against the representation.

## Render-time question-instance checks

`Shared/tools/render_core.py::figure(...)` fails closed when an explicit `instance_ref` is used unless:

1. the representation is not a source snapshot;
2. the named scene instance exists;
3. `scene_instance.question_ref == owner_ref/question id`;
4. the requested Core role appears in `scene_instance.cores`;
5. the scene instance has an authored `asset_ref`;
6. every `datum_ref` resolves to an actual data record;
7. the authored SVG exists and is accessible;
8. requested visual stages exist in that exact selected asset.

Rendered question-instance figures expose:

- `data-g9-case-instance`
- `data-g9-case-owner`
- `data-g9-case-data`
- `data-g9-representation`

so exact rendered evidence retains the selected case identity.

## Existing replay coverage

`tests/test_staged_support_repair.py` already exercises the frozen Set B staged replay.

Relevant cases prove:

- each actual question selects its own question-bound asset;
- two questions sharing a topic can select different scene instances rather than silently sharing the same case;
- wrong question owner is rejected;
- absent data binding is rejected;
- absent authored asset is rejected;
- wrong Core role is rejected;
- a source figure cannot be replaced by an adopted authored question case;
- an explicitly reviewed authored replacement remains selected both before and after attempt;
- staged-replay receipts include the selected case asset bytes.

At exact head `acce63cb1e721026670421fb5ef75deb5a26e122`:

- workflow: `learner-platform-code-tests`
- run: `37439526719`
- code-tests job: `112189508282`
- dedicated `Core2 staged support contract` step: **SUCCESS**
- **25 tests, OK**

The broader informational Python aggregation remains raw non-green and is not treated as representation acceptance.

## Wrong-case replay result

A concept-correct representation cannot silently satisfy a question-instance request merely because its topic/representation id matches.

The renderer requires the explicitly selected instance to match:
- the exact question;
- the exact Core role;
- existing data records;
- an authored case asset.

The frozen wrong-owner/data/asset/role mutations all result in an empty rendered figure plus governed `MOUNT_REPRESENTATION` / `BUILD_SCENE` gaps.

Therefore the original PR #65 wrong-case failure is already addressed by existing runtime authority.

## Schema contradiction found

The remaining shared defect is narrower.

The `scene_instance.question_ref` description says:

> Exactly one of microtopic_ref and question_ref carries the binding.

But the schema currently uses:

`anyOf`

with one branch requiring `microtopic_ref` and one requiring `question_ref`.

JSON Schema `anyOf` accepts an object satisfying **both** branches. Therefore a scene instance can be schema-valid while simultaneously claiming:
- a teaching/microtopic owner; and
- a question-instance owner.

That contradicts the declared single-owner semantics and leaves a representation role ambiguous before renderer selection.

## U06A disposition

### REUSE EXISTING

Do not add parallel fields for:
- question owner;
- Core role;
- case/instance identity;
- datum binding;
- authored asset binding.

Those relationships already exist and are enforced at render time.

### TRUE SCHEMA GAP

Change only the owner-choice constraint from `anyOf` to `oneOf`, preserving the existing two field names and all valid single-owner records.

Compatibility evidence must prove:

- question-only instance remains valid;
- microtopic-only instance remains valid;
- both owner refs are rejected;
- neither owner ref is rejected;
- frozen staged Set B scene instances remain valid;
- existing wrong-case render failures remain fail-closed.

## U06A result

**U06A COMPLETE. No production change.**

Parent U06 remains incomplete.

Parent denominator remains:
- **P = 5/10 = 50%**
- **E = 5/10 = 50%**

Next bounded task:

**U06B — replace the contradictory scene-instance owner `anyOf` with `oneOf`, add focused compatibility/wrong-case regressions, and close U06 only if the exact focused lane is green.**
