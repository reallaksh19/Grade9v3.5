# ISS66 U02A — blueprint-driven expanded-layout expectation repair

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U02A only — repair the confirmed Core1A expanded-layout expectation contradiction  
**Basis before U02A:** `e99c3db98446022bfdfbf8af278d2999b62c55eb`

## Confirmed defect

The active Core1A blueprint is `BP-CORE1A-CONSTRUCTION@1.7.0` with:

```text
compact  = SINGLE_PANE
medium   = SINGLE_PANE
expanded = SINGLE_PANE
primary_fraction = 0.6
support_fraction = 0.4
```

PR #65 already made `matchesBlueprintLayout(...)` respect `expanded=SINGLE_PANE`.

However, `core-page-audit.mjs` retained two separate calculations based only on nonzero `support_fraction`:
- `expectedColumns`
- later `expectedLayout`

The later Core1A enforcement treated non-null `expectedLayout` as requiring an expanded split at/above `expanded_min_px`.

Therefore the historical fractions could override the selected `expanded=SINGLE_PANE` policy.

## Repair

### 1. One helper for split expectation

`tools/site-audit/layout-observation.mjs` now exports:

`splitLayoutExpectation(policy)`

It returns a split expectation **only** when:

```text
policy.expanded == STAGE_SUPPORT
and support_fraction is present
```

For `SINGLE_PANE`, it returns `null` even if historical primary/support fractions remain in the blueprint.

### 2. Audit consumes that helper in both places

`tools/site-audit/core-page-audit.mjs` now derives both:
- stylesheet `expectedColumns`; and
- later Core1A `expectedLayout`

from the same `splitLayoutExpectation(policy)` result.

There is no longer a second path where `support_fraction` alone can manufacture a split-layout requirement.

### 3. Retained behavior tests

`tests/test_blueprint_layout.mjs` adds:
- Core1A-style `SINGLE_PANE` + retained 0.6/0.4 fractions => **no split expectation**;
- Core2-style `STAGE_SUPPORT` + 0.42/0.58 => expected split remains 0.42/0.58 at 980px.

Existing tests still verify:
- measured one-pane content satisfies `SINGLE_PANE`;
- an actual two-column article violates `SINGLE_PANE`;
- an empty page cannot fabricate layout evidence;
- `STAGE_SUPPORT` keeps its existing measured-layout observation.

## Material commits

- `051a9a8c117596b269d28c7ae8eaefc20dc31c47` — helper: derive split layout only from blueprint mode.
- `8f0a70b3c1e04f82d8e0e3d5d6ecc4d9e7662f7b` — browser audit consumes the blueprint-derived expectation.
- `8cfe0eb0f1b9b6661d00062ddef6c286b11edf6e` — focused retained-mode tests.

Read-back blobs after patch:
- `layout-observation.mjs`: `f4a47df20d1858fc7bed1bc619faa05d046461ee`
- `core-page-audit.mjs`: `5ca16dede3bcd34e4bcfa23a22405eeafaf81b3d`
- `test_blueprint_layout.mjs`: `3e66eca93ae7243251db172819749536604fb76a`

## Focused validation

Exact patched helper + test bytes were replayed with:

```text
node --test tests/test_blueprint_layout.mjs
```

Result:

```text
tests 6
pass 6
fail 0
cancelled 0
skipped 0
todo 0
```

This proves the focused policy helper behavior only. It is **not** a full repository/browser acceptance claim.

## U02A scope result

**U02A complete.**

No blueprint JSON version, schema, learner-quality rule, renderer layout generation, or subject record was changed.

The repair is deliberately audit-policy reconciliation: the selected blueprint mode determines whether split columns are expected.

## Remaining U02 evidence

U02 parent unit is not yet complete. The next bounded task is **U02B**:

- replay an actual retained Core1A/Core2 layout fixture or governed render through the affected audit path;
- show Core1A `SINGLE_PANE` no longer receives a false split requirement;
- show a role with `STAGE_SUPPORT` still requires its declared split;
- record any environment limitation as NOT_RUN rather than treating the helper unit test as browser acceptance.

Until U02B, parent P/E remain **10% / 10%**.
