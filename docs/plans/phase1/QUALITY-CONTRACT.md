# Phase 1: learner quality contract

Part of [LEARNER-PRODUCT-QUALITY-REBUILD.md](../LEARNER-PRODUCT-QUALITY-REBUILD.md). This is
the document for the owner's calibration review (owner decision 3).

## What it is

| File | Role |
|---|---|
| `Shared/quality/learner-quality.v1.json` | The contract: 41 subject-neutral rules, the blocks each Core role must show, thresholds, and the two reference grammars |
| `Shared/quality/learner-observation.schema.json` | What the rules judge: a *learner observation*, i.e. what a learner can see and do on a delivered product (blocks, figures and when they appear, attempt controls, gated reveals, support levels, shell facts) |
| `Shared/tools/quality_contract.py` | `--check` (the contract is well formed), `evaluate <observation>`, `calibrate` |
| `Shared/tools/quality_observe.py` | Extractors that turn delivered files into observations |
| `<Subject>/adapter/QualityVocabulary.json` | Physics, Chemistry, Mathematics: figure kinds, check types, prerequisite domains. The only subject-specific part |
| `tests/test_quality_contract.py` | Calibration, subject neutrality, and degraded-unit tests |

**A rule never reads a record's claims.**
- It judges what reached the learner. A `data-blueprint-ref`, a validation report or a duty
  marked `COMPLETED` counts for nothing.
- Every rule names the audit findings it would have caught (`audit_refs`) and the reference
  grammar step it encodes (`grammar`).

**Rule families**

| Family | Rules | Covers |
|---|---|---|
| DEPTH | 23 | content and its depth |
| INTERACTION | 5 | attempt before reveal |
| PAGE | 7 | shell, home link, slots, touch, layout, print CSS, figure titles |
| INTEGRITY | 6 | placeholders, escape states, renderer provenance, all six roles, shared Atlas, print from page |

Two PAGE rules need a browser (`tools/site-audit/core-page-audit.mjs`). They are reported as
NOT_MEASURED when no measurement is supplied.

## Calibration result

`python3 Shared/tools/quality_contract.py calibrate`:

```
ok  S1  negative: caught 21/21 expected; also fails (reviewed) C1A-STAGED-REPRESENTATION, C2A-PROVENANCE, C2B-SAFE-SUPPORT-SPECIFIC, PRODUCT-RENDERED-FROM-RECORDS
ok  S2  negative: caught 2/2 expected; also fails (reviewed) PRODUCT-RENDERED-FROM-RECORDS
ok  S3  negative: caught 2/2 expected
ok  S4  negative: caught 1/1 expected; also fails (reviewed) PRODUCT-RENDERED-FROM-RECORDS
ok  S5  negative: caught 2/2 expected; also fails (reviewed) PRODUCT-RENDERED-FROM-RECORDS
ok  R1  positive: NOT_LOCATED
ok  R2  positive: CALIBRATED, 77 units, grammar rules 7; outside its grammar also fails ALL-FIGURES-TITLED, C2A-FAMILY-CLOSURE, C2A-REVEAL-GATED, PRODUCT-RENDERED-FROM-RECORDS
calibration passed
```

- **Right reasons, not just a failure.** Each S1 finding is caught by the rule written for it,
  on the units the audit named. For example:
  - `C1A-ANCHOR-PER-DECISION` flags only R3 ("7 decisions carried by 1 worked anchor").
  - `C1A-REPRESENTATION-BRIDGE` flags only R1–R3.
  - `C2A-SPECIFIC-SUPPORT` quotes the repeated failure signal.
- **Strict both ways.** A rule that fails on a specimen but maps to none of its findings must
  be reviewed and recorded in the manifest (`acknowledged_extra_rules`, with the reason), or
  calibration fails. This caught one real defect the audits missed: S1's Core2B tasks show no
  provenance label, although the product's validation report claims `AUTHORED_PRACTICE`
  labels on both Core2A and Core2B.
- **The question-bank reference (R2) passes every rule that encodes its grammar.**
  - Across all 77 items and both subjects in it (Physics and Chemistry), it has stem first,
    trap, question-aligned figure, ≥ 3-rung support, complete derivation, answer +
    independent check, and provenance.
  - It fails four rules outside its grammar, correctly: its figures have no accessible title,
    it has no family/exposure closure, its hint rungs print open (it is a print-oriented
    edition), and it has no renderer stamp.

**Thresholds set by the corpus**
- **`max_decisions_per_anchor = 4`:** S1's Core1A concepts have 3, 4, 4, 4, 4, 4, 4 and 7
  decisions, one anchor each. Only the audited R3 exceeds it.
- **`min_support_levels = 3`:** every R2 item has exactly 3 rungs.
- **Conditions block not mandatory in Core2A:** 3 of R2's 77 items state no separate
  conditions. The first calibration run flagged them, so the rule was relaxed rather than the
  reference.

## Exit gate

| Gate | Status |
|---|---|
| Rejects every negative specimen for the right reasons | done: 28 of 28 audited findings across S1–S5; extra failures reviewed |
| Accepts the reference grammar | R2: done. R1: not located on any branch, so its grammar is encoded as rules (each of its 7 steps maps to a rule or to the subject vocabulary) but it has not been run against the file |
| A Mathematics and a Chemistry unit fit without a schema change | done: `tests/fixtures/quality/math-core2a-two-step-linear.observation.json` and `chem-core1a-mole-concept.observation.json` validate and pass every unit rule |

## Known limits, for the owner's review

1. **R1 is uncalibrated.** If the compiled Core1A textbook is in the repository under a name
   the search did not try, pointing to it lets `calibrate` run it. It would need an extractor
   for its format.
2. **Legacy extractors.**
   - S1 and R2 have full unit extraction. S2–S5 have product-level facts only.
   - The extractors read those specific page families. The Phase 3 renderer will mark blocks,
     figure stages and reveals with `data-g9-*` attributes and needs one generic extractor.
3. **The prerequisite rule flags all 8 S1 concepts, not only the 5 extensions in A1-005.**
   None of their entry assumptions links to a teaching unit. The rule asks for a link; it
   cannot judge whether an unlinked assumption is "obviously known". Adjusting this is an
   owner call.
4. **Severities are the audit's**, including S0 for escape states and S1 for missing
   representations and ungated reveals. Please confirm or change them. Every threshold is a
   single value in the contract's `thresholds`.
