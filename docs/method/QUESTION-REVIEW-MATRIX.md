# Question Review Matrix (QRT)

## Purpose

The Question Review Matrix is the semantic review layer for question support.

It resolves exactly one base review template from:

```text
primary cognitive demand × question difficulty band
7 demands × 4 bands = 28 cells
```

It does **not** define learner-page structure. Blueprint 1.9 remains the authority for Core page components, disclosure boundaries and rendering.

The layers are:

```text
canonical question record
  ├─ question difficulty D1–D4
  ├─ five difficulty components
  ├─ authored cognitive demand
  └─ stable question/crux evidence
            +
learner profile
  └─ per-capability DEMONSTRATED / UNCERTAIN / MISSING
            ↓
QRT resolver
            ↓
one of 28 base cells
            +
subject DemandReview adapter
            ↓
agent/reviewer worksheet
            ↓
semantic judgements
            ├─ actionable findings → product-review/v2
            └─ structural/render evidence → existing quality_gate/1
```

## Source files

Do not edit the generated 28-cell projection directly.

- `Shared/vocabularies/cognitive-demand.v1.json` — seven demand IDs.
- `Shared/quality/question-demand-matrix.v1.json` — demand policies, D-band policies and H1–M3 asks.
- `Shared/quality/question-demand-matrix.schema.json` — source-contract schema.
- `Shared/quality/question-demand-templates.v1.json` — generated 28-cell projection.
- `<Subject>/adapter/DemandReview.json` — subject specialization.
- `Shared/tools/question_review_matrix.py` — compiler, checker, resolver, review projection and gate delta.

## Seven cognitive demands

The primary demand identifies the learner act whose success most directly decides the question.

- `RETRIEVE` — reconstruct/select a fact, category, definition, property, unit or condition.
- `EXPLAIN` — explain why a relation, mechanism, pattern or result holds.
- `APPLY` — execute a known model, algorithm, relation or procedure under the right conditions.
- `MODEL` — choose/formulate the governing model, law, variables, process or strategy.
- `REPRESENT` — preserve meaning while translating between representations.
- `SYNTHESIZE` — coordinate dependent ideas/steps where route selection is part of the difficulty.
- `JUSTIFY` — establish a conclusion from explicit warrants or evidence.

Secondary demands may be recorded, but they do not select another base cell.

Do not infer cognitive demand from question type, chapter label, transfer dimension or learner percentage.

## Difficulty

Question difficulty remains the repository D1–D4 model.

The five components remain:

- `concept_model_selection`
- `representation_translation`
- `reasoning_chain_length`
- `algebra_computational_load`
- `trap_exception_sensitivity`

QRT does not introduce a second difficulty system.

The band changes what support must leave learner-owned:

- D1 — one meaningful identification, relation, translation or execution.
- D2 — a short connection/choice plus execution.
- D3 — the important bridge between ideas, representations or models.
- D4 — the decisive model, strategy, synthesis, exception or warrant.

Hint counts or figure counts never establish quality.

## X / Y / Z / W

X/Y/Z/W live in the resolved review, not as universal learner-independent truth.

- **X** — what this learner is likely to misread or what the question turns on for this learner.
- **Y** — a relevant bridge the learner has already `DEMONSTRATED`.
- **Z** — the key move, anchored to the stable crux / crux move where available.
- **W** — the decisive step that must remain learner-owned.

The resolver proposes candidates from the question record and learner profile. A reviewer may refine them with evidence.

For Core2B, W should align with `transfer.protected_move_ref` when present.

`knowledge_percentage` is stored only as summary metadata. It never selects a cell or a bridge.

## Twelve semantic asks

The base matrix always resolves the same 12 ask IDs:

```text
H1 H2 H3
S1 S2 S3
P1 P2 P3
M1 M2 M3
```

Their jobs are semantic:

- H1 clarifies X.
- H2 connects X to Y.
- H3 opens the way to Z while preserving W.
- S1 makes the situation/X visible without answering it.
- S2 puts Y into the question's representation.
- S3 shows construction toward Z without disclosing W.
- P1 checks that pre-attempt panels preserve W.
- P2 checks that concept navigation lands where X/Y is actually taught or repaired.
- P3 checks per-move validity explanation plus an independent check.
- M1 represents the likely wrong idea.
- M2 distinguishes misconception from execution slip.
- M3 shows why the wrong idea fails and gives the replacement rule.

Additional hint rungs or visual stages are allowed when useful. The 12 asks are review objectives, not a support-depth cap.

A figure can be correctly not applicable. Do not create decorative SVG merely to satisfy presence.

## Commands

Validate the contract and committed generated projection:

```bash
python Shared/tools/question_review_matrix.py check
python Shared/tools/question_review_matrix.py write --check
```

Inspect the generated 28 cells:

```bash
python Shared/tools/question_review_matrix.py compile
```

Resolve one question + learner profile:

```bash
python Shared/tools/question_review_matrix.py resolve \
  --source path/to/package-or-question.json \
  --question Q-... \
  --profile Learners/profiles/profile.json
```

Resolve and add subject specialization:

```bash
python Shared/tools/question_review_matrix.py resolve \
  --source path/to/package-or-question.json \
  --question Q-... \
  --profile Learners/profiles/profile.json \
  --adapter Mathematics/adapter/DemandReview.json
```

The adapter may specialize representation kinds, check types, review focus and misconception patterns. It may not change the selected `QRT-<DEMAND>-<BAND>` identity.

## Review authority

The resolved QRT worksheet is an agent/reviewer work surface, not a second publication authority.

Use qualitative verdicts:

```text
YES | PARTLY | NO
```

A genuine not-applicable case is represented as a justified applicability decision, not a fourth score.

Actionable `NO` / `PARTLY` outcomes project into the existing `product-review/v2` finding model. Optional traceability fields are:

- review `profile_ref`;
- finding `asks: H1 ... M3`.

Do not compute an aggregate QRT score.

## Real-gate delta

QRT does not reimplement render or quality gates.

Run the real pipeline first and obtain tool-written `quality_gate/1` reports. Then compare them:

```bash
python Shared/tools/question_review_matrix.py gate-delta \
  --before build/before-quality.json \
  --after build/after-quality.json
```

The delta reports:

- new findings;
- closed findings;
- persisting findings;
- new/closed continuity findings;
- changed rendered-page digests.

This is a work-order/read-model over real gate evidence, not another gate.

## Blueprint 1.9 boundary

Blueprint 1.9 owns:

- page components;
- required/expected/optional structure;
- attempt/reveal boundaries;
- layout/presentation;
- reference-depth construction guidance.

QRT owns:

- demand-specific purpose of support;
- what H/S/P/M must accomplish;
- protected learner work W;
- learner-specific bridge Y;
- semantic judgement of the exact support.

Therefore:

- do not create 28 Core2 blueprints;
- do not use hint counts as a QRT pass condition;
- do not make every question draw a figure;
- do not move authored scaffolds into source hints;
- do not duplicate existing renderer/quality rules inside the matrix.

## Core2 → Core1A

Stable question evidence can inform downstream construction:

```text
reviewed stable crux / Z
        ↓
recurring demand/crux cluster
        ↓
Core1A construction unit
  crux_question_refs
  crux_step_ref
```

Learner-relative Y and W are not copied into canonical Core1A truth.

Core2 W is protected assessment work. Core1A may teach the underlying construction fully and then use its own fresh exit task.

## Transfer

The seven demand classes do not replace the four transfer dimensions:

- `model_choice`
- `novelty`
- `reasoning_steps`
- `representation_translation`

Demand asks what kind of work the question principally requires. Transfer describes what changed relative to prior exposure.

## PR #3 pilot

See `docs/method/QRT-PR3-MATH-PILOT.md`.

The pilot intentionally uses an overlay rather than mutating source-bank records. Its current polynomial render is useful for semantic review but still declares an older Core2 Blueprint ref. Coordinate geometry remains blocked from render-level QRT review until it is normalized onto the governed renderer/Blueprint path.

