# Core1 semantic-orientation integrity

Issue: #253  
Programme: #252

## Governing question

> Is this a short, correct semantic map of the bucket without pretending that stating a difficult inference is the same as teaching it?

Core1 is orientation. It owns the learner's map of:

- named quantities/objects and the conventions needed to read them;
- governing relations, their meaning and applicability conditions;
- compact anchor values when canonical data provides them;
- scope, exclusions and labelled extensions;
- honest curriculum-mapping status;
- the MEDIUM/HARD conceptual transitions that Core1A/Core1B must actually construct/reconstruct;
- the declared primary representation when the bucket owns one.

Core1 does **not** certify that an inferential jump has been taught merely because a sentence states it. That semantic judgment remains a reviewer obligation and belongs to the Phase‑2/3 progression, not to a prose-length or keyword heuristic.

## Mechanical audit boundary

`Shared/library/core1_orientation.py` enforces only falsifiable structural claims:

- relation references resolve through the subject-wide canonical index;
- a used governing relation has learner-readable meaning and at least one declared condition;
- an authored convention has a statement;
- every MEDIUM/HARD transition has `badge_reason`;
- each authored curriculum mapping declares `mapping_status`;
- a declared primary representation resolves and contains a Core1 scene;
- an authored scope object is not empty.

The report also records, but does not fail merely for:

- a bucket with no authored conventions;
- a bucket with no authored scope;
- a bucket that is not Core1-compilable because none of its microtopics binds a governing relation.

These states require semantic review/migration decisions rather than automatic filler.

## Current Phase‑1 baseline

The initial audit scans **21** ordinary canonical-library buckets:

- **14** are currently Core1-compilable under the compiler's governing-relation rule;
- **3** carry structural legacy findings;
- all three findings are `PRIMARY_REPRESENTATION_CORE1_SCENE_MISSING`.

Affected buckets:

1. `BUCKET-PHY-KIN-1D-MOTION`
2. `BUCKET-PHY-KIN-2D-MOTION`
3. `BUCKET-PHY-SOUND`

Each declares a primary representation whose current scene instances are bound to Core1A/Core1B but not Core1.

The committed baseline freezes these as migration debt. Guardrails rejects any **new** structural finding relative to that baseline and separately verifies that the committed report equals a fresh audit.

## What the gate deliberately cannot certify

The structural audit does not claim to prove:

- that Core1 wording is pedagogically concise;
- that an orientation sentence has not over-compressed a difficult inference;
- that the selected primary representation is the best learner orientation;
- that a concept deserves MEDIUM/HARD rather than another badge.

Those are semantic review questions. Phase 1 records them as manual-review obligations rather than manufacturing a numeric quality score.

## Stack handoff

Phase 2 (#254) consumes this Phase‑1 truth and audits the actual conceptual construction:

`entry assumptions → inferential jump → teaching path → why-valid → representation bridge → misconception/repair → independent check → exit closure`.

Phase 2 must not reinterpret Phase‑1 structural debt as permission to weaken Core1A.
