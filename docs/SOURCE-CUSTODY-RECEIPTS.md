# Source custody receipts

A source URL is an instruction to inspect evidence. It is not itself evidence that the
source contains enough material for Core2, Core2A or Core2B.

The repository therefore separates three objects:

1. **source basis** — what the owner asked the agent to inspect;
2. **canonical resource/question records** — what the library actually holds;
3. **source inspection receipt** — an auditable statement of what was inspected and which
   canonical question records that inspection supports.

Requests never declare source sufficiency directly.

## Request contract

A plan request may contain:

```json
{
  "source_basis": ["https://example.org/source.pdf"],
  "source_receipt_ref": "SRCREC-..."
}
```

It may not contain a free-form `source_inspection.status`.

If `source_receipt_ref` is supplied, `source_basis` is required. The receipt must match
that basis exactly.

## Receipt contract

Receipts live under `Sources/receipts/` and conform to
`Shared/library/source-inspection-receipt.schema.json`.

Each receipt records:

- subject and bucket;
- the exact source-basis locators;
- the canonical resource refs inspected;
- inspector kind/id and inspection date;
- access scope;
- an immutable content SHA-256 when sufficiency is claimed;
- per-Core coverage status;
- the exact canonical question refs offered as evidence;
- a human-readable basis for each coverage statement.

Coverage states are `SUFFICIENT`, `INSUFFICIENT`, or `NOT_EVALUATED`.

## Verification

`Shared/tools/source_receipts.py` checks the receipt against the current library.

A receipt fails when, among other things:

- it points to a resource the library does not hold;
- its source basis does not equal a bound resource locator;
- its subject or bucket differs from the request;
- a claimed question does not exist;
- a claimed question belongs to a different bucket;
- a claimed question is not bound to one of the receipt resources;
- a Core2A/Core2B question is not actually exposed to that Core;
- Core2 custody is supported by an `AUTHORED` question;
- `SUFFICIENT` is claimed with no evidenced questions;
- `SUFFICIENT` is claimed without a content SHA-256;
- legacy migrated metadata claims sufficiency.

The last rule matters: migration can preserve that somebody previously inspected a section.
It cannot retroactively manufacture evidence of product coverage.

## Core2 custody

Core2 is a preservation product.

For a receipt to support Core2, its evidenced questions must be canonical questions with
`origin = ORIGINAL` or `ADAPTED`, must be bound through `source_refs` to a resource
named by the receipt, **and must carry a resolved question-level source-custody proof**.

The proof lives at `question.extensions.source_custody` and is validated against
`Shared/library/source-question-custody.schema.json`. It pins the source digest and item
locator, binds the current demand-bearing question signature, and records the custody state
of identity, stem, subparts, options, conditions, figures/captions, hints and source
answer/rubric. Missing, unresolved or stale proofs do not contribute to Core2 coverage even
when the question record itself is REVIEWED/CURATED.

An authored question can never close Core2, even if it is scientifically excellent and
even if it is useful in Core2A/Core2B.

## Practice coverage

Core2A/Core2B may have two legitimate paths:

- source-derived practice evidenced by a verified receipt; or
- project-authored candidate practice when the owner explicitly sets
  `ALLOW_AUTHORED_CANDIDATES`.

The second path never upgrades the source receipt and never changes Core2 custody.

If a receipt is insufficient and the owner selects `SOURCE_ONLY`, the practice product
remains blocked.

## Relative Motion migration receipt

`SRCREC-NCERT-KEPH103-RELATIVE-MOTION-LEGACY` preserves the repository's existing fact
that the NCERT Motion in a Plane resource had been section-inspected.

It deliberately reports Core2, Core2A and Core2B as `INSUFFICIENT` because the canonical
Relative Motion package contains no ORIGINAL/ADAPTED question bound to
`SRC-NCERT-PLANE`. It carries no frozen content digest and therefore cannot claim
sufficiency.

This is a truthful migration artifact, not a new inspection of the NCERT PDF.

## Source-basis drift

A stable URL is not necessarily a stable source scope. A publisher may reuse a filename,
move a chapter, rationalise a section, or replace an edition while leaving the locator
shape plausible.

Every receipt therefore carries a `basis_assessment`:

- `MATCH` — the inspected source matches the requested basis and topic scope;
- `DRIFT` — the locator is valid, but the current content no longer matches the scope the
  request appears to rely on;
- `UNKNOWN` — the inspection evidence is not strong enough to decide.

`DRIFT` is an owner-decision boundary. The planner must ask
`SOURCE_BASIS_DRIFT_DECISION` before it asks whether authored supplemental questions may
fill coverage gaps.

The owner may either keep the supplied basis despite the drift, in which case products are
judged only against what that current source actually contains, or change the source basis
to one of the receipt's replacement candidates and acquire/inspect that source separately.

An agent may not silently substitute:

- a historical copy that once occupied the same filename;
- a mirror with similar content;
- a newer chapter that looks closer to the intended topic;
- a different official URL.

### Current Relative Motion example

On 2026-09-18 the supplied official `keph103.pdf` resolves to *Motion in a Plane*. Historical
NCERT material used `keph103.pdf` for *Motion in a Straight Line*, which contained a
Relative Velocity section. Current NCERT places *Motion in a Straight Line* at
`keph102.pdf`.

The current receipt therefore records `DRIFT`, identifies `keph102.pdf` only as a
replacement candidate, and keeps all source-backed Relative Motion products waiting until
the owner decides whether to keep or change the supplied basis.

This is intentionally different from `INSUFFICIENT`: insufficiency means “this is the
right source but it does not cover enough”; drift means “before discussing coverage, decide
whether this is still the source you meant.”

## Execution packet pin

When a request names a receipt, the execution packet pins the receipt digest.

Changing the receipt, deleting it, changing its resource/question evidence, or making it
fail verification invalidates the packet. The authoring agent must re-plan rather than
continuing from stale custody assumptions.

## CI

CI enforces:

```text
python3 Shared/tools/source_receipts.py --audit --enforce
python3 Shared/tools/plan_request.py --audit --enforce
python3 Shared/tools/compile_execution_packet.py --audit --enforce
```

The source-receipt falsifiers live in `tests/test_source_receipts.py`.
