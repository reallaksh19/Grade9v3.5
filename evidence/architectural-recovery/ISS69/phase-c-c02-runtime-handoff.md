# ISS69 PHASE-C — Core2 runtime handoff

## Recovered runtime contract

Core2 now projects the product contract from `BP-CORE2-SOURCE-QUESTION@1.11.0` without a parallel disclosure model.

### Attempt

The attempt slot contains the authentic question/conditions/attempt only.

Wrong-route content is not attempt furniture.

### Support

The existing #66 availability contract remains authoritative:

```text
PRE_ATTEMPT_SAFE
AFTER_ATTEMPT
POST_SOLUTION
```

- generic progressive support uses the typed support-plan lane;
- `common_wrong_route` is AFTER_ATTEMPT assistance by default;
- content completing protected work cannot be PRE_ATTEMPT_SAFE;
- no separate TRAP-availability schema was added.

### Assistance

The learner-visible question records assistance provenance:

```text
HINT_LADDER
WRONG_ROUTE
CONCEPT_NAV
```

Assistance is persisted per exact question and is not diagnosis.

### Concept detour

PAGES mode:

```text
core2.html#QUESTION
  -> core1a.html?g9-return=QUESTION&g9-concept=CONCEPT#CONSTRUCTION
  -> exact Return to question
```

The query-bound route is primary. localStorage is a compatibility/persistence aid, not the navigation authority.

SINGLE_FILE mode rewrites query-bearing cross-Core URLs to scoped in-document anchors; the same-document runtime preserves the exact return affordance.

### Diagnosis

No change to #66 typed diagnosis:
- complete CONFIRMED evidence may select misconception-specific repair;
- INDETERMINATE / REFUTED / invalid / bare claims cannot;
- opening help does not create diagnosis.

## Production fixes in Phase C

- TRAP moved from attempt projection to support projection.
- wrong-route body is gated until commitment.
- hidden support buttons are excluded from browser interaction locators.
- query-bearing Core links are rewritten correctly in SINGLE_FILE.
- URL-bound return remains available when storage is blocked.
- two orphan Motion2D figure_refs were removed rather than replaced with fabricated figures.

## Remaining evidence / handoff

The exact browser replay remains the qualification surface for:
- visible support control activation;
- PAGES round trip;
- SINGLE_FILE round trip;
- storage-blocked URL return;
- wrong-route assistance persistence.

Generated Core-learning compiler bytes are handled separately by C03.6 and MUST be regenerated through `Shared/tools/build_manifest.py`, never hand-edited.
