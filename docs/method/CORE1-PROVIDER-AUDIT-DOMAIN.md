# Core1 provider coverage vs audited snapshot (Issue #326)

**Scope:** This is a mechanical parity correction, **not** new Core1 curriculum, QRT
review, source rights, or learner release authority. It preserves the six-role
programme's prior inventory history and uses the existing canonical compiler.

## Two intentionally different snapshots

- `docs/core1-orientation-report.json` is a committed historical structural
  report of **22** Mathematics/Physics buckets. It must not become a runtime
  whitelist or an implicit admission policy; its absence of newly added canonical
  buckets is *not* evidence those buckets are ineligible for a compiler preview.
- `Shared.library.core1_orientation.audit(REPO)` audits **current** canonical
  `*/library/*.json` buckets. The matching compiler-backed Core1 projections in
  `build_core_learning_data.build()["core_projections"]` represent only
  **compilability**. An exact live-audit/provider set equality protects against
  silently missing either existing or newly introduced orientable buckets.

The current historical-to-live delta is deliberately tested by exact identity:

| Subject | Canonical bucket | Status |
| --- | --- | --- |
| Mathematics | `BUCKET-MAT-POLYNOMIALS` | `CANDIDATE` |
| TEST | `BUCKET-TEST-IMO-G9-NS-DIVISIBILITY` | `CANDIDATE`, sandbox |
| TEST | `BUCKET-MATH-POLY-STRESS-ISS55` | `CANDIDATE`, sandbox |

These three are compiler previews. `build_core_learning_data` calls the
compiler with `practice_control.mode=DESIGN_PREVIEW` and
`practice_control.purpose=PRACTICE`. The test checks both exact present-day
identities and the preview-only compiler control. A later addition or removal
requires an explicit inventory reconciliation rather than being hidden by
taking a set intersection. Crucially, **CANDIDATE is not a filter**: a large
fraction of the already tracked Physics/Mathematics packages are candidates too.

## Non-grants

- `PRODUCTION_COMPILED_CANONICAL` is a *compiler provenance* statement, not a
  learner publication, curriculum, owner, academic, source-custody, or QRT grant.
- The historical report is not silently regenerated into the old approved
  denominator. A live structural audit is not an accepted question count.
- TEST candidate previews remain TEST: this ticket does not establish that any
  particular learner host can be publicly exposed. A separate explicit
  publication/visibility policy must govern deployability.
- Do not change `Core2` source-custody rules, QRT 28-cell review requirements,
  V3.1 validation, or original question ownership to correct this assertion.

## Mechanical verification

```sh
python -m unittest tests.test_core_learning_adapter -v
```

The dedicated `core1-provider-audit-parity` workflow runs this unchanged
assertion plus candidate/preview boundary checks on the exact branch head.
Workflow outcomes must be inspected for actual job step execution; a GitHub
Actions infrastructure failure or zero-step run is **NOT_TESTED**, not PASS.
The exact historical `main` baseline must likewise be observed executing
before claiming a runtime baseline result.
