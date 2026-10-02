# Assurance architecture

How a question, a page and a product earn the word "assured" in this repository, and what stops the word being used when it has not been earned.

This is the architecture of the chain introduced by PR 395 (content supply chain), as adopted and made to hold its own contracts, with the blueprint rules (registry 1.9.0) as verifiers inside it. It describes what is built. Section 7 lists what is not.

## 1. The chain

```
subject  ->  verifier  ->  evidence (AE)  ->  bundle  ->  eligibility  ->  accept gate
(file)      (a check)     (one verdict,      (the facts   (the decision,   (Owner only)
                           bound to the       for a        recomputed)
                           subject digest)    product)
```

| Link | Module | What it is |
|---|---|---|
| contract | `Shared/assurance/contract.py` | The schemas are the definition. Every record is validated by the producer before it is written and by the consumer before it is read. Digests are over canonical JSON for records and over LF-normalised bytes for files. |
| evidence | `Shared/assurance/evidence.py` | One verdict about one subject for one assurance type: `PASS`, `FAIL`, `INCONCLUSIVE`, `NOT_APPLICABLE`, `NOT_RUN`. Its id is deterministic (no timestamp in it) and it carries the digest of the subject it judged. |
| verifiers | `Shared/assurance/verifiers.py`, `typed.py` | The checks. Package checks reuse intake's admission points; page checks reuse `standalone_conformance.py`; typed checks run a question's declared computation. |
| aggregation | `Shared/assurance/aggregate.py` | Bundle and decision. Worst-of reduction per (type, subject); stale evidence ignored; no vacuous truth. |
| ratchet | `Shared/assurance/baseline.py`, `Shared/web/standalone-ledger.v1.json` | What CI measures against: known canonical findings (by key) and known page counts (by count). Written by tools only. |
| projections | `build_search_index.py`, `build_projection_manifest.py`, `release_fingerprint.py`, `drift_detector.py` | What a release was made of, by digest, and whether it has drifted. |
| gate | `accept_product.py`, `Shared/assurance/product.py` | `acceptance_gate` is `REQUIRED`: accepting a product assures it as staged and refuses unless it is `ELIGIBLE`, counting the Owner's recorded waivers (Section 7). |

## 2. Design rules

1. **One contract per artifact.** A record that does not satisfy its schema is not evidence of anything. There is no second, hand-written list of required fields.
2. **Evidence is bound to what it judged.** It carries the digest of the subject. When the subject changes, the evidence is stale and is ignored, not trusted.
3. **A check that cannot run has not passed.** `INCONCLUSIVE` (the question declares nothing to check) and `NOT_RUN` (the check could not run) never read as `PASS`. A type with no evidence at all is missing, not satisfied.
4. **Worst of.** One failing record fails the cell. A `PASS` with a severe finding in it is not accepted from hand-written evidence either.
5. **The bundle is facts and is recomputed.** Release eligibility re-validates the bundle, re-collects the evidence, re-hashes the subjects as they are now and decides. It does not trust the bundle's own claims. Waivers apply only at the decision, only to a type the policy allows to be reviewed, and each names a reason and an approval.
6. **Evidence lives outside the subject.** `build/assurance/` is gitignored. Evidence about `standalone/`, `docs/` or `public/` is never written into them: that would change the digest it claims.
7. **A static check proves only part of a type.** The page checks feed `PROJECTION_STATIC_CONFORMANCE`, not `RESPONSIVE_LAYOUT` or `ACCESSIBILITY`. Those stay open until a browser audit says otherwise.
8. **Honest verdicts.** A question that declares no `problem_specification` is `INCONCLUSIVE` for self-containment; it is never `PASS`. Self-containment is a relation the specification states (what the computation needs is visible, a permitted constant or a declared assumption), not a scrape of words in the answer.

## 3. Two questions, answered differently

| | CI | Release |
|---|---|---|
| Asks | Did this change make anything worse? | Is the product good? |
| Measures against | The baseline, the ledger, the merge base | The policy, absolutely |
| A known failure | Does not fail the run | Is still a `FAIL`; the product is not eligible |
| Where | `.github/workflows/canonical-assurance.yml`: `assurance`, `regression-delta` (gating) | `release_eligibility.py`; the `release-status` job reports it and never gates |

The ratchet does not soften the evidence. A known finding stays a `FAIL` in the evidence, and a product with one is `INELIGIBLE`; CI refuses only what is new. (The canonical baseline is empty today. The page ledger is not: the pages merged from #375 carry known text-size, storage and maths findings, and a product page set with one fails the gate.) Neither the baseline nor the ledger is edited by hand: `assurance_run.py --write-baseline`, `standalone_conformance.py --write-ledger`.

The regression delta compares **test ids**, not counts (`run_test_ids.py`, `diff_test_failures.py`). One test fixed and another broken has an unchanged count. A HEAD that ran no tests, or has a module that no longer loads, fails the comparison; it is not "no new failures". There is no `|| true`, no `continue-on-error` and no path filter on a gate.

## 4. One vocabulary: the blueprint names the type

Every admission point and every standalone rule in the blueprint registry carries an `assurance_type`. The verifier reads it from the registry; it does not keep its own table.

| Registry | Id | Assurance type |
|---|---|---|
| admission | `QUESTION_STEM`, `QUESTION_STEM_COMPLETE`, `QUESTION_OPTIONS` | `STRUCTURAL_VALIDITY` |
| admission | `QUESTION_GIVENS` | `DISCLOSURE_CONFORMANCE` |
| admission | `QUESTION_SCOPE` | `SCOPE_CONFORMANCE` |
| admission | `ANSWER_ANCHORED`, `ANSWER_WORKED` | `CORPUS_SPECIFICITY` |
| admission | `ANSWER_VERIFIED` | `REASONING_VALIDITY` |
| standalone | `REMOTE_RUNTIME` | `NETWORK_POLICY` |
| standalone | `LINKS_RESOLVE`, `LINKS_LEAVE_ROOT` | `LINK_INTEGRITY` |
| standalone | `VIEWPORT_ZOOM`, `FONT_FLOOR`, `MATH_CONTROL_CHARS`, `MATH_UNRENDERED`, `STORAGE_GUARDED`, `VENDOR_CONFIG_DANGLING`, `UNIQUE_IDS` | `PROJECTION_STATIC_CONFORMANCE` |

Intake (`Shared/library/intake.py`) remains the gate of record for a new package. The verifier runs the same admission code over the packages that are already there, so a rule has one implementation and two moments of use.

## 5. Scope has one source

`Shared/policy/grade9-physics.v1.json` is the only statement of what Grade 9 physics includes and defers. Each `DEFER` entry has its terms, an owner and the document row it comes from. Question admission and the scope verifier both read it. Where the policy lists a concept that no scope document row names, the finding is advisory, not blocking: the Owner decides whether the concept is really deferred.

## 6. Adding to the chain

- **A check on an existing type.** Add the rule or point to the blueprint registry with its `assurance_type`, implement it in `question_admission.py` or `standalone_conformance.py`, regenerate with `blueprint_spec.py --write`. The verifier picks it up. A test must show it failing on a defective fixture and passing on a clean one.
- **A new type.** Add it to the evidence schema and to a policy. Until a verifier writes evidence for it, it is an open need in every bundle, which is correct.
- **Paying down debt.** Fix the finding, run `assurance_run.py` (it prints `FIXED (tighten the baseline)`), then `--write-baseline`. The baseline only gets shorter.

## 7. The acceptance gate, and the Owner's waiver

`learner-release-default.acceptance_gate` is `REQUIRED`. `accept_product.py <slug>` assures the product as it is staged (`build_products.py build` first): its packages (the manifest's `package_refs`), the staged PAGES render, and the staged single-file page when there is one, judged where they will be served (`public/`). It writes the evidence, bundle and decision to `build/assurance/<slug>/`, prints the decision, and refuses unless it is `ELIGIBLE`. The acceptance record says what the decision rested on (`assurance`: status, bundle digest, the waived types). A bundle given with `--eligibility` is recomputed the same way.

A set of pages is not the subject of `SEARCH_MEMBERSHIP`, `SEARCH_RETRIEVABILITY` or `DEPLOYMENT_INTEGRITY` (the search index is a projection of its own; drift is judged against an accepted fingerprint, which a first acceptance has not got), so a page set gets an explicit `NOT_APPLICABLE` for them. The render receipt beside the pages is verified as `PROJECTION_INTEGRITY`.

**Waivers.** Seven types have no working checker or cannot conclude. The Owner waived them, on 2026-10-02, "waive all, record as future scope" (`Shared/assurance/waivers/learner-release.v1.json`, which quotes the approval). A waiver:

- covers a need that is **missing, inconclusive or not run**, for every subject of its type; and nothing else. It never covers a `FAIL`, evidence gone stale, a broken record or an S0/S1 finding;
- is part of the decision, not of the bundle (the bundle stays facts), and every use is listed in the eligibility record (`waived`) and in the acceptance record;
- needs no taking down when a checker arrives: from then on the real verdict, `PASS` or `FAIL`, is what counts.

| Waived type | Why there is no verdict | What ends the waiver (future scope) |
|---|---|---|
| `RESPONSIVE_LAYOUT` | a rendered fact; the static page checks do not claim it | a verifier that runs `tools/site-audit/core-page-audit.mjs` and writes evidence |
| `ACCESSIBILITY` | contrast, tap targets and focus are rendered facts | the same browser audit, for contrast, 48 px targets, keyboard focus |
| `ANSWERABILITY` | needs each question to declare what it gives and asks | questions that declare `problem_specification` and `answer_contract`, and a verifier over them |
| `SOURCE_INTEGRITY` | no tool that writes evidence checks the cited sources | a verifier over the fact-status machinery `accept_product` already prints |
| `PROJECTION_COMPLETENESS` | no tool that writes evidence compares selection with pages | a verifier over the manifest's selection and the receipt's gaps |
| `SELF_CONTAINMENT` | inconclusive: no authored question declares its givens | authored questions that declare `problem_specification` and `computation_model` |
| `REASONING_VALIDITY` | inconclusive: keys are checked by their author or not at all | an independent check of each key, by a person or a declared computation |

## 8. What is not built, and what remains for the Owner

- The seven waived checkers above are future scope. Until they exist, an `ELIGIBLE` product is eligible for what is checked, and says so in its record.
- `DEPLOYMENT_INTEGRITY` and the search types are produced against the release (`drift_detector.py`, `verify_search_index.py`); nothing gates acceptance on them.
- Competitive banks (`bank_refs`) are not packages and are not judged by the package verifiers.
- Two ratchets (baseline by key, ledger by count) remain separate files with separate tools. The canonical baseline is now empty: the four Mathematics nested-id collisions were renamed (with the Owner's approval) and the migration ledger of that package was amended by its tool (`migrate_math_linear.py --amend`).
- The committed single-file copies under `standalone/products/` carry the shared stylesheet as it was; the stylesheet now keeps learner text at 14 px, and a copy takes it up when the Owner next accepts that product.
- `ANSWER_VERIFIED` blocks a key nobody ran (`NOT_RUN`), by the Owner's decision; a key checked only by its author is reported (`AUTHOR_ONLY`), not blocked.
- Scope-policy `DEFER` entries that no scope-document row names are advisory until the row is added or the entry dropped.
