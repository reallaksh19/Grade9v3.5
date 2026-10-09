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

## Source-backed release boundary and physical public data quarantine

At the bounded-unit cutoff, the 24 canonical subject library packages hold
25 buckets (20 Physics, three Mathematics, two TEST). Every inspected package
and bucket declares `CANDIDATE`. The frozen 22-bucket report is a historical
structural inventory, **not** an independently approved learner-release set.
`CoreContracts.release_authority` says
`NOT_GRANTED_BY_ANY_MACHINE_CHECK` for these subjects.

**Two independent outputs now have different authority:**

1. `build_core_learning_data.build()` remains the full compiler-owned,
   `DESIGN_PREVIEW/PRACTICE` payload for internal web resolution,
   `preflight_projection()`, mechanical exact-set Core1 auditing and
   content-addressed derived engineering memory. Its TEST preview records
   continue to exist *internally*. No academic quality or release is implied.
2. `build_core_learning_data.build_public()` creates an **empty**
   `core_projections`, `bucket_availability` and `findings` payload,
   with `publication_gate.status=HOLD`,
   `code=NO_INDEPENDENT_CORE_PUBLICATION_GRANT` and
   `authority=NOT_GRANTED_BY_ANY_MACHINE_CHECK`. The public-file
   `rendered_file()` and `write()` emit this restricted payload while
   keeping the complete internal `build()` accessible. It is deliberately
   impossible to grant an item via a name, status, compiled result or
   historical inventory under this bounded change.

**Physical emission evidence:** the committed `public/core-learning/data.js`
and GitHub Pages mirror `docs/core-learning/data.js` have both been
replaced with the same deterministic **536-byte** HOLD payload; their Git
blob ID is `ebc279414f6e91ccef9e6d8d1a90fe19c7b2c4f3`.
Previously those assets were the same 2,497,022-byte preview blob.
The developer-facing `docs/core-learning/index.html` deployment mirror
has also been regenerated from the public host. The host template plus
public/standalone/Pages HTML now show the preview limitation and, when
`publication_gate.status=HOLD`, explicitly tell the learner there are no
authorized public activities. The chooser and direct-link UI additionally
exclude TEST rows as defense in depth; those UI filters alone would never
satisfy data custody.

The Pages generator now checks `public/core-learning/data.js` against the
source-authoritative `build_core_learning_data.rendered_file()` bytes
**before** copying any site assets. Missing Core host/data pairs, internal
preview payloads and tampered/forged release claims are rejected by named
`CORE_PUBLICATION_HOLD_*` errors. New focused tests exercise both the
validator and real `desired_files()` mirror generation with valid and
invalid temporary site roots. It is a source-generation guard, **not**
proof that remote Pages deployment or caches are current.

**Interrupted compilation boundary:** the `build_core_learning_data.write()`
path now emits the restrictive public HOLD file **before** calling the
canonical internal `build()` compiler or updating derived engineering memory.
An internal preview compilation error therefore cannot leave a previous,
preview-bearing `public/core-learning/data.js` untouched. A temporary-path
failure-injection regression proves the intended ordering without depending
on full canonical source compilation.

**Existing downstream consumers:** the public Core data asset is also read by
Motion Session and multiple Topic Atlas pages. These were not entitled to
consume internal previews after the HOLD. The ordinary Topic Atlas resolver
now distinguishes `publication_gate.status=HOLD` from a missing compiled
projection and explicitly labels Core navigation as withheld, without
suppressing separately governed visual/portable routes. The Motion Session
entrypoint fails before learner identity resolution with
`NO_INDEPENDENT_CORE_PUBLICATION_GRANT`, using its existing unavailable
panel and trace. Their public source files and GitHub Pages mirrors were
updated consistently. Focused regression assertions pin those source/mirror
invariants, **not** a successful real browser journey.

**Pages read-after-check protection:** The Pages generator separately checks
the actual `core-learning/data.js` bytes at the point they enter the mirror,
after initial public-source validation. This rejects content changed between
preflight and copying with `CORE_PUBLICATION_HOLD_MIRROR_SOURCE_CHANGED`.
A test simulates a valid first read and a preview-bearing second read. This
covers deterministic mirroring from the bytes read; it does not certify an
already-running remote deployment.

**Known positive-journey conflict, intentionally unresolved:** The existing
`tests/motion_session_251.test.mjs` positive identity test directly reads
`public/core-learning/data.js` and expects a published Core1B/Core2B chain.
Under the intentional zero-projection HOLD envelope it cannot satisfy that
assertion. Its browser journey expects the same public chain. These tests
must **not** be suppressed or declared green: the conflict demonstrates why
this safety leaf cannot be counted as joined six-Core continuity or merged
before a separately authorized positive publication route and real browser
proof exist. The previously
successful Motion Session and six-Core journey tests must not be rewritten
to treat publication HOLD as learner-success evidence.

The candidate Mathematics Polynomials Core1 entry is **not publicly served**
through these Core learner `data.js` outputs. Its separately qualified
Question Bank records are governed by their own publication contracts; this
change does not revoke or grant those rights.

### What this does NOT prove

- A proper per-bucket/subject *positive* Core release grant protocol, its
  independently verified reviewer signature, curriculum mapping, relevant
  route or time of authorization **does not yet exist** in this provider.
  It would be unsafe to invent such a protocol, promote the 22-bucket
  report or whitelist Physics/Mathematics candidates by status. Zero
  public Core projections is the **correct fail-closed outcome**, not a
  complete six-Core learner journey.
- Source previews persist internally and in derived artifacts under
  `publication/derived-artifacts/`; publication/deployment of any other
  directory or old already-live historical snapshots is separately out of
  scope. These newly saved bytes do not prove that a deployed Pages URL
  has updated, that caches have expired, or that no other independent
  public site references old previews.
- A deterministic-source and mirror-byte check is not an executing
  Python test or Chromium journey. The owning workflow now requests the full
  adapter suite, dedicated Pages custody tests, the existing Pages freshness
  suite, generator host parity and a full Pages --check. GitHub Actions has
  recently failed
  all jobs with **zero executed steps**. Exact-head execution and browser
  verification are mandatory.

### Required release completion work (separate authorization)

Obtain Owner/academic-controlled source-bound, separately authenticated
release-grant receipts and a formal eligible-domain predicate; design both
positive and negative tests against actual public bytes and real browser
requests, including previously approved learner content. Only after that
independent review may an approved, source-pinned projection be emitted
outside the internal preview. Reconcile stable study pathways without
using compiler renderability as qualification. Do not silently grant
source custody, QRT 28-cell signoff, V3.1/Common CI, transfer or merge
authority.

**State: DRAFT / publication HOLD / Python+browser NOT_TESTED until steps
actually execute.**
