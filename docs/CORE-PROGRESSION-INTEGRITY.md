# Cross-Core progression integrity

Core2, Core2A and Core2B are connected products with different ownership. They must
form a traceable progression without making one record pretend to own all three roles.

## Progression invariant

```text
verified assessment demand
        ↓
Core2 — source custody
        ↓ family-level evidence
Core2A — familiar application teaching
        ↓ concrete parent / prior exposure
Core2B — changed-demand transfer
```

The invariant is:

> Core2 proves the real assessment demand; Core2A teaches the familiar application of
> that demand; Core2B changes the demand and tests transfer without changing the taught
> truth.

## Ownership boundaries

### Core2

Core2 may render only an ordinary canonical question that is:

- source-derived (`ORIGINAL` or `ADAPTED`);
- `REVIEWED` or `CURATED`;
- backed by a resolved Phase-1 `extensions.source_custody` proof.

An `AUTHORED` practice question cannot become Core2 because it is useful, appears in the
same family, or has a verified answer.

### Core2A

Core2A may legitimately use authored familiar applications. Their provenance remains
`AUTHORED`. The forward contract is the Phase-2 structured application route/crux; the
legacy debt inventory remains explicit while topics migrate.

### Core2B

Core2B is a changed-demand claim relative to prior familiar exposure. Its concrete
question parent must remain a Core2A familiar anchor in the same family, and the
Phase-3 protected-decision audit governs forward migration.

## Source-demand evidence is not source custody

The competitive exam bank is a governed source-demand evidence product outside the
ordinary `Subject/library/*.json` package graph.

A bank question with accepted provenance (`PYQ_VERIFIED` or `PYQ_ADAPTED`) may prove
that a canonical family reflects real assessment demand. It does **not** thereby become
an ordinary Core2 question, and it is not copied into the ordinary package model.

The allowed join is:

```text
verified bank item
  └─ family_ref / capability
       └─ source-demand evidence for the practice family
```

The forbidden join is:

```text
verified bank item
  └─ copy or relabel authored practice
       └─ pretend it is Core2 custody
```

`Shared/library/core_progression.py` therefore reports two distinct source states:

- `ORDINARY_CORE2_CUSTODY`
- `COMPETITIVE_BANK_VERIFIED_DEMAND`

and an honest gap state:

- `SOURCE_DEMAND_NOT_YET_EVIDENCED`

## Family progression report

For every family used by Core2A/Core2B the audit reports:

- source-demand evidence state and exact anchors;
- all Core2A familiar questions;
- which Core2A questions have migrated to structured reasoning;
- all Core2B transfer questions;
- which Core2B questions have migrated to a protected decision;
- explicit gaps.

A missing source-demand anchor is visible but is not automatically a repository failure.
An authored family may exist before its assessment-demand evidence has been established;
the audit must describe that state rather than manufacture custody.

Core2B parent/family divergence **is** a mechanical failure because it breaks the declared
familiar-to-transfer progression.

## Renderability is not progression readiness

`compile_inputs.compile_bucket()` exposes `product_support`.

For each Core it reports:

- `renderable`: canonical content can be compiled into learner blocks;
- `renderability_reason`;
- `progression_readiness = NOT_EVALUATED_BY_COMPILER`.

This is intentional. A renderer/compiler does not grant:

- source-custody authority;
- family source-demand evidence;
- Core2A reasoning maturity;
- Core2B protected-transfer maturity;
- learner release.

Those are separate evidence layers.

## CI

Guardrails run:

```bash
python3 Shared/tools/core2a_inventory.py --enforce-forward
python3 Shared/tools/core2b_inventory.py --enforce-forward
python3 Shared/library/core_progression.py --enforce
```

The progression audit fails mechanically falsifiable ownership/lineage collapse. It does
not convert descriptive maturity gaps into scores or quotas.

## Non-goals

This layer does not:

- flatten competitive-bank questions into ordinary library packages;
- require a Core2B item for every family;
- infer transfer from difficulty or text dissimilarity;
- rewrite authored Core2A provenance;
- make a source-demand bank anchor equivalent to ordinary Core2 custody;
- infer progression readiness merely because a product renders.

## Reviewer interpretation

A mature family may look like:

```text
SOURCE_EVIDENCED
→ Core2A familiar items present
→ Core2A structured reasoning migrated
→ Core2B changed-demand child present
→ Core2B protected decision migrated
```

A legitimate incomplete family may instead say:

```text
SOURCE_DEMAND_NOT_YET_EVIDENCED
→ Core2A authored familiar practice present
→ no genuine transfer authored
```

The second state is a named gap, not permission to fabricate either a source question or
a transfer item for symmetry.
