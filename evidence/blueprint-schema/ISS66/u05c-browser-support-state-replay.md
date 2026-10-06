# ISS66 U05C — browser replay of support disclosure states

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U05C only — verify pre-attempt, after-attempt, and solution-only boundaries in a real browser using the frozen staged Set B #55 pilot  
**Tested implementation head:** `acce63cb1e721026670421fb5ef75deb5a26e122`

## Fixture basis

The browser fixture is generated from the existing:

`tools/staged_set_b_replay.py`

using its frozen #55 Q1 adopted record:

`OWN-ISS55-POLY-01`

The fixture generator changes only disclosure metadata:

- one support completion that completes protected work is explicitly set to `AFTER_ATTEMPT`;
- the protected WORKED visual remains `POST_SOLUTION`.

Stem, answer, reasoning route, support words, representation asset, protected move refs and case binding remain from the staged replay.

## Browser assertions

Added:

- `tests/iss66_support_state_fixture.py`
- `tests/iss66_support_state_browser.mjs`

The Playwright replay checks three learner-visible states.

### 1. PRE_ATTEMPT

Before a valid commitment:

- **More support after your attempt** is locked;
- **Answer and working** is locked;
- neither payload slot is materialised for the learner.

### 2. AFTER_ATTEMPT

After entering a non-empty attempt and committing:

- the article records `data-attempted=1`;
- both commitment-gated disclosures unlock;
- opening **More support after your attempt** exposes the moved support row;
- the exact moved support is `scaffolds[1]`;
- **Answer and working** remains closed;
- the WORKED solution visual remains not visible.

### 3. POST_SOLUTION

Only after opening **Answer and working**:

- the WORKED visual becomes visible;
- the support row moved to `AFTER_ATTEMPT` is not duplicated in the solution-only completed-support list.

This demonstrates that after-attempt support is independently available without forcing the learner to open the full solution.

## Exact-head CI evidence

Workflow:
`learner-platform-code-tests`

Run:
`37439519409`

Job:
`112189508162` — `core2-v2-browser-audit`

Head:
`acce63cb1e721026670421fb5ef75deb5a26e122`

Relevant step:

`ISS66 staged support browser-state replay` — **SUCCESS**

Browser output:

```json
{
  "pre_attempt_locked": true,
  "after_attempt_support_visible": true,
  "solution_closed_during_after_attempt_support": true,
  "worked_visual_visible_only_after_solution_open": true,
  "moved_support_ref": "scaffolds[1]"
}
```

The isolated U05C step executes **before** the broader Motion-in-2D render/audit stages. Its result therefore remains usable even if those later historically non-green paths encounter unrelated render gaps.

## Harness correction

The first browser attempt failed before rendering because the standalone Python fixture script inherited `tests/` as `sys.path[0]` and could not import `Shared`.

Correction:
- insert the repository root explicitly into `sys.path` in the fixture generator.

This was a test-harness import failure only; no production support behavior changed.

## U05 acceptance result

U05 required:

- a canonical protected learner-work reference;
- machine-checkable support/visual relationships to that protected work;
- explicit disclosure eligibility rather than “closed means safe”;
- retained safe pre-attempt support;
- ability to defer protected-completing help until commitment without forcing full solution;
- solution-only material remaining separately disclosed;
- legacy compatibility.

All are now evidenced.

## U05 result

**U05 COMPLETE and successor-safe evidenced.**

Parent denominator:
- **P = 5/10 = 50%**
- **E = 5/10 = 50%**

No claim is made that:
- attempt commitment establishes correctness;
- support completion can be inferred safely from prose;
- every legacy question has an adopted support plan;
- broader Core2 browser/product suites are all green.

Next bounded unit:

**U06A — inspect existing representation instance/case binding and replay wrong-case failures before changing representation schema.**
