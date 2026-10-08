# Draft TEST canonical package — IMO Grade 9 universal divisibility

**Status:** `CANDIDATE`. **Not a learner Core1A product or admitted academic truth.**
Research continuation of [Issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294),
tracked in [Issue #296](https://github.com/reallaksh19/Grade9v3.5/issues/296).
Draft source-custody [PR #295](https://github.com/reallaksh19/Grade9v3.5/pull/295)
remains an independent prerequisite for reliable SOF Core2 source selection.

This author-created TEST package is the **next implementation step toward Core1A**,
not a conversion of the seven original-practice questions into Core2 or a
claim that the official SOF syllabus explicitly certifies divisibility proofs.
The authored mathematical steps are grounded in elementary parity,
consecutive residues modulo three and coprimality, not in printed SOF answer
keys. The concept is independently research-authored and not product-accepted.

## Actual canonical-shape candidate

`TEST/library/imo-g9-divisibility-core1a.v1.json` uses the existing
`Shared/library/package.schema.json` names and fields:

| Object | Count | Evidence / expected meaning |
| --- | ---: | --- |
| `resource` | 1 | `AUTHORED` math; source custody is Issue #296, not SOF |
| `bucket` | 1 | Domain, divisibility and modular conventions |
| `capability` | 1 | Prove universal consecutive-product divisibility |
| `microtopic` | 1 | HARD is a **proposed intrinsic judgement**, not measured learner difficulty |
| `relation` | 1 | Triple product divisible by 6 for every positive start |
| `representation` | 1 | Two-way words/symbols residue-table **spec**; no rendered figure |
| `question_family` | 1 | Authored conceptual family; **zero source questions** |
| `CORE1A teaching route` | 1 | Declarative complete inference and independently checkable exit |

Core1A construction steps: (1) choose arbitrary `n`; (2) guarantee
an even term, so factor 2; (3) exhaust remainders 0,1,2 modulo 3 and
guarantee factor 3; (4) combine via gcd(2,3)=1 to obtain factor 6.

A single misconception record diagnoses why testing three examples is
not proof for all `n`. The independent exit task constructs an actual
argument for **any four consecutive integers to be divisible by 24**:
two of the factors supply 8 and one supplies 3, with gcd(8,3)=1. The
validator checks the modulo 6 and modulo 24 residue classes exhaustively.

### Explicit gaps — not falsely marked complete

- **No source-backed Core2 question:** zero canonical source question
  records, zero official SOF stems/options/figures copied, zero rights claims.
  This package intentionally does not create an ordinary Core2 learner page.
- **No rendered concept representation:** it specifies rows and
  correspondences, but `rendered_asset_refs` and `scene_instances` are empty;
  a proper rendered learner scene is later authored and browser-reviewed.
- **No concept worked-question record:** the full conceptual teaching steps
  and exit are present; a separate canonical authored worked-example record
  and actual artifact review will be needed for the final Core1A product.
- **No acceptance:** topic-level organizer syllabus evidence is not proof
  of explicit divisibility-proof curriculum endorsement. There is no learner
  evaluation, HTML/PDF render, accessibility/keyboard/print audit, QRT
  admission, or product owner approval. Missing evidence remains visible.
- **No source-rights waiver:** the dated owner waiver applies to independent
  human academic signoff only. Reuse of SOF paper components needs a separate
  publisher-rights decision.

## How to inspect

```sh
python TEST/imo-research/validate_core1a_candidate_package.py
python -m unittest discover -s tests -p 'test_imo_core1a_candidate_package.py' -v
# Actual full-schema validation additionally requires jsonschema:
python -m Shared.library.resolve --schema TEST/library/imo-g9-divisibility-core1a.v1.json
```

The standalone validator checks candidate status, source/authorship,
field/ID conservation, full construction, mathematical residues,
misconception and exit, and the repository's built-in
`validate_library` reference/acyclicity checks. It **does not claim**
to run the full external `jsonschema` validator; the above full-schema
command is an explicit additional acceptance item where that dependency
is available. Adversarial tests reject false admissions, fabricated rights,
implicit SOF Core2/question identities, dropped why-valid steps and
unverified exit responses.

This unit is deliberately smaller than a product: it is a coherent first
candidate slice, not an excuse to skip the full 68-position source-denominator
inventory in Issue #294.
