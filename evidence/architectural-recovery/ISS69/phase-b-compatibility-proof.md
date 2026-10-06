# ISS69 PHASE-B — B02.6 compatibility proof

Exact material frontier: `fix/iss69-phase-b-subject-neutrality@30f92d267e4e329d2b5acd60d4c04e95344db773`

## Authority readback

- blueprint registry: `1.17.0`
- active Core2 blueprint: `BP-CORE2-SOURCE-QUESTION@1.11.0`
- role-template binding: `CORE2 -> BP-CORE2-SOURCE-QUESTION@1.11.0`
- generated `docs/specs/PAGE-BLUEPRINT-COMPONENTS.md` names `1.11.0` and reflects the subject-neutral `SOLUTION_STEPS` authoring contract.

## CI evidence boundary

### blueprint-v2-render-snapshots is NOT exact-head evidence

The workflow's `Materialize current main authority` step runs:

`git worktree add --detach /tmp/g9-main origin/main`

and all snapshot rendering uses `working-directory: /tmp/g9-main`.

Therefore its green result is a **main-baseline snapshot only**. It must not be cited as proof of this Phase-B branch. Earlier Phase-B wording that called this exact-head evidence is superseded by this correction.

### branch-exact code-tests responsibility lanes

Job `112375137197`:

- Diagnostic evidence contract: **SUCCESS**
- U09 diagnostic caller migration: **SUCCESS**
- Representation instance binding contract: **SUCCESS**
- Core2 staged support contract: **FAIL — one known downstream projection error**

Exact error:

`KeyError: 'CORE2: TRAP not declared in attempt of BP-CORE2-SOURCE-QUESTION'`

The staged-support suite ran 25 tests and stopped on this one error. This is the PHASE-A/PHASE-C seam already recorded in #70: the recovered blueprint correctly places TRAP in support, while the old renderer still injects TRAP into the attempt slot.

No B02 change touches `render_core.py`, support-plan schema, diagnostic evidence schema, or representation-binding logic.

## Compatibility conclusion

B02 neutralization does not regress #66 semantic-contract invariants.

The branch-exact evidence supports:
- subject-neutral solution authoring authority: direct contract readback PASS;
- typed diagnostic evidence contract: PASS;
- diagnostic caller migration: PASS;
- representation instance binding: PASS;
- staged-support semantic logic: unchanged up to the known renderer placement seam.

Snapshot-render/denominator behavior for the Phase-B head remains **not yet proven by the snapshot job**, because that job intentionally renders `origin/main`.

The whole repository is **not** claimed green. The TRAP projection seam remains explicitly owned by PHASE-C, and broad pre-existing guardrail/assurance failures remain separate.
