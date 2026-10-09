# #132 — NCERT Q1 canonical handoff dry run

This is a **read-only, non-publishing** first slice of issue #132. The end-to-end
parked product in #131 and the complete canonical producer/deletion-independence
trial are **not** qualified by this slice.

```bash
python3 -m unittest tests.test_test11_q1_dry_run -v
python3 TEST/promotion/q1_dry_run.py
```

The command reads the official TEST intake, source-custody overlay, historical
academic receipt and current Mathematics canonical Q1. It produces JSON on stdout
and does **not** regenerate or modify any repository file. It neither opens nor
copies `public/test` or `docs/test`, and deliberately works with those directories
absent.

## Decision and authority boundaries

- **DEFERRED**: reproducible candidate and verified source custody, but the
  available academic PASS receipt binds the prior stem digest and no new Owner
  admission decision exists. This is the expected live Q1 result.
- **REJECTED**: an identity, digest, answer, source locator or lineage invariant
  fails. Exit code is nonzero; zero files written.
- **ACCEPTED**: a reserved governed state; this diagnostic has **no path** to
  asserting it, accepting external approval flags, or publishing a record.
  It requires new independently validated academic evidence, separate explicit
  Owner authority and a qualified, exact-basis promotion procedure.

The emitted `candidate_digest` is a deterministic fingerprint over proposed
canonical **source fields**, not an acceptance signature or package digest.
`regeneration.producer_sequence` is the future authorized producer order
(Question Bank web/platform, Atlas/data, learner search, Pages). All producers
are **PLAN_ONLY_NOT_EXECUTED** here. The historical canonical Q1 remains
included on the old receipt; the tool does not silently withdraw or rebind it.
The correction/legacy mismatch is tracked in issue #132.

The tests prove the mapping survives deletion of TEST HTML, changes no source
file bytes, rejects duplicate identities and forged source/receipt lineage, and
cannot infer academic or Owner acceptance from a source READY status.
