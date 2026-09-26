# Phase 2: a data model that can hold depth

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md). Phase 1 defined
what a learner must see. Phase 2 makes the library records able to carry it, and turns every
place where a record cannot yet carry it into a named duty.

## Schema 0.2.0 (`Shared/library/package.schema.json`)

`schema_version` accepts `0.1.0` and `0.2.0`. The new fields are optional in the schema, so every
package loads. A missing field is a duty on the board, never a silent default.

| Field | Holds | Contract rules it serves |
|---|---|---|
| `microtopic.construction_units[]` | one distinct decision/event each: `decision` (or `decision_from`), `step_refs` into `teaching_path`, `representation_ref` + `reveal_stage_refs`, `worked_anchor_ref` (a CORE1A question), `misconception_indexes`, `independent_checks[]` | C1A-ANCHOR-PER-DECISION, C1A-REPRESENTATION-BRIDGE, C1A-BLOCKS |
| `question.hint_ladder[]` | ordered rungs with `purpose` (ORIENT → REPRESENT → FIRST_RELATION … ANSWER) and `provenance` (SOURCE_HINT / AUTHORED_HINT / AUTHORED_SCAFFOLD); a migrated rung points to its hint or scaffold with `from` | C2A-LADDER, C2A-SPECIFIC-SUPPORT |
| `question.representation_roles` | `initial_ref` (with the stem), `safe_ref` (before commitment, no protected move), `bound_ref` (with support or solution), `stage_refs` | C2A-REPRESENTATION, C2B-SAFE-REPRESENTATION |
| `question.independent_check` | a structured check with `check_type` from the subject vocabulary, when `answer.check` does not already state it | C2A-BLOCKS |
| `question.failure_signal` | the item-specific sign of the tempting wrong route | C2A-TRAP, C2A-SPECIFIC-SUPPORT |
| `question.family_exposure` | `family_ref` + `closure`: what the item establishes for a later transfer | C2A-FAMILY-CLOSURE |
| `question.transfer.invariant` | what stays valid from `builds_on` while `statement` changes | C2B-LINEAGE |
| `microtopic.prerequisite_refs` | may name another subject's capability as `<Subject>:<id>` | C1A-PREREQUISITES-BRIDGED |

**One source of truth.** Migration never copies text:
- a migrated rung points to its hint or scaffold (`from: "hints[0]"`);
- a migrated unit points to its microtopic's inferential jump (`decision_from`);
- `answer.check` stays where it is.

The first version copied text, and the authoring-run test caught the problem: an edited hint
left its copy stale, and the duplicate-text checker flagged it.

## Migration (`Shared/tools/package_migrate.py`)

`--write` migrated all 21 packages (20 Physics, 1 Mathematics); `--check` fails if any package
is not current. The migration only restructures what a record already says:
- **One construction unit per microtopic**, only where its `teaching_path` has at most 4
  decisions (the Phase 1 threshold). It records `migrated_from: teaching_path`, so an author
  reviews the unit boundary. Nine Physics microtopics have 5 to 8 decisions and get no unit:
  splitting them is an author's decision.
- **Worked anchor:** the CORE1A question of the same capability, where one exists.
- **Hint ladder:** existing hints and scaffolds, ordered by how much each reveals.
- **Bound representation:** the representation its reasoning route already names.

Nothing else is filled in, so the rest stays a duty.

## Depth duties (`Shared/tools/package_depth.py`, `library_board.py --depth`)

Each duty names:
- the role that fixes it (AUTHOR, RESEARCHER or RENDERER);
- the record;
- the contract rules the gap would fail.

Supplying the field removes exactly that duty (`tests/test_package_depth.py`).

```sh
python3 Shared/tools/library_board.py --subject Physics --depth --next AUTHOR
python3 Shared/tools/package_depth.py --summary          # all subjects
```

Snapshot on 2026-09-26: 682 duties (AUTHOR 664, RESEARCHER 12, RENDERER 6):

| Subject | Duty | Role | Count |
|---|---|---|---|
| Mathematics | AUTHOR_FAILURE_SIGNAL | AUTHOR | 1 |
| Mathematics | AUTHOR_FAMILY_EXPOSURE | AUTHOR | 1 |
| Mathematics | AUTHOR_INDEPENDENT_CHECK | AUTHOR | 3 |
| Mathematics | AUTHOR_WORKED_ANCHOR | AUTHOR | 2 |
| Mathematics | REVIEW_MIGRATED_UNIT | AUTHOR | 3 |
| Mathematics | STAGE_REPRESENTATION | AUTHOR | 1 |
| Mathematics | TEACH_PREREQUISITE_BRIDGE | RESEARCHER | 2 |
| Physics | AUTHOR_CONSTRUCTION_UNITS | AUTHOR | 9 |
| Physics | AUTHOR_FAILURE_SIGNAL | AUTHOR | 67 |
| Physics | AUTHOR_FAMILY_EXPOSURE | AUTHOR | 67 |
| Physics | AUTHOR_HINT_LADDER | AUTHOR | 60 |
| Physics | AUTHOR_INDEPENDENT_CHECK | AUTHOR | 79 |
| Physics | AUTHOR_LINEAGE_CHECK | AUTHOR | 38 |
| Physics | AUTHOR_QUESTION_REPRESENTATION | AUTHOR | 62 |
| Physics | AUTHOR_SAFE_REPRESENTATION | AUTHOR | 38 |
| Physics | AUTHOR_WORKED_ANCHOR | AUTHOR | 78 |
| Physics | BUILD_SCENE | RENDERER | 6 |
| Physics | MOUNT_REPRESENTATION | AUTHOR | 68 |
| Physics | REVIEW_MIGRATED_UNIT | AUTHOR | 79 |
| Physics | STAGE_REPRESENTATION | AUTHOR | 8 |
| Physics | TEACH_PREREQUISITE_BRIDGE | RESEARCHER | 10 |

**What the numbers say**
- The library holds rich teaching paths, misconceptions, reasoning routes and staged
  representations (16 representations; 10 already have scene instances).
- But 62 of 67 Physics Core2A items have no representation shown with the stem.
- No item has a failure signal or a family closure.
- No transfer task has a safe representation or an invariant.
- 60 practice items have fewer than 3 support rungs.

These are exactly the S1 defects, now visible in the data before anything is rendered.

## Exit gate

| Gate | Status |
|---|---|
| Schema and migration merged | on this branch (PR #295) |
| Every package loads | all 21 validate against schema 0.2.0; migration is idempotent |
| The board shows a duty for every depth gap across all subjects | Physics and Mathematics: yes. **Chemistry has no microtopic library package** (only its exam bank), so it has no depth duties yet. Its gap is upstream: the research library has no Chemistry spine. Adding a Chemistry spine is the first researcher duty for that subject |

## Handled elsewhere

- The request planner already schedules `SCHEDULE_PREREQUISITE_BRIDGES` for unresolved
  prerequisites (`plan_request.py`); the library side is `TEACH_PREREQUISITE_BRIDGE`.
- Scene rendering: 6 representations have no scene instance (`BUILD_SCENE`, RENDERER). The
  shared scene renderer is Phase 3.
