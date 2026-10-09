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

## Source-backed release boundary and limited UI mitigation

At the pinned bounded-unit source cutoff, the 24 canonical subject library
packages contain 25 buckets: 20 Physics, three Mathematics and two TEST.
Every inspected package and bucket declares `status: CANDIDATE`. The
historical 22-bucket report contains the 20 Physics and two earlier
Mathematics buckets. It is **not** a list of independently release-approved
Core1 content. The three later buckets are compiler-orientable, not thereby
academically admitted. The source-level subject `CoreContracts.json`
records `release_authority: NOT_GRANTED_BY_ANY_MACHINE_CHECK`.

The learner-host template and its generated public and standalone HTML now
show a prominent compiler-preview notice. Their ordinary activity chooser
excludes `subject: TEST`; the direct-link mount path refuses IDs absent from
the filtered chooser. A focused test pins the notice and both client-side
checks. This is a **UI route mitigation only**, not content access control.
It does not qualify any Mathematics, Physics or TEST item for curricular
publication; Mathematics Polynomials remains a visible *candidate preview*.

**Critical remaining exposure:** both hosts still load
`public/core-learning/data.js`. The generator's `build()` emits TEST
compiler rows in `core_projections` and the generated public file could
therefore physically contain sandbox records regardless of chooser filtering.
The exact saved artifact is ~2.5 MB at its pinned Git blob and its complete
bytes have not been re-read or regenerated here. A user-visible filter does
not prevent data access through the JavaScript payload or a different
consumer. No publication/academic isolation PASS is claimed.

Before resolving Issue #326, independently select and enforce the canonical
learner-publication eligibility policy (with source/Owner review), split or
constrain **physical public-data emission** accordingly, preserve the
compiler's complete internal previews, and validate negative TEST/candidate
exposure tests against the actually emitted public file and both browser
hosts. A missing grant must fail closed. This must not silently convert the
frozen report into an approval whitelist or make all CANDIDATE rows releasable.

GitHub Actions retries at the previous head (candidate
`211db0c0c805b7d87d0dd45e9bd4d59647916ee7`, pinned-main diagnostic)
again returned zero executed job steps on attempt 3. The newer host changes
likewise require actual exact-head execution before verification. Retain
DRAFT and all source-custody/QRT/V3.1 holds.
