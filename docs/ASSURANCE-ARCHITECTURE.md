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
| gate | `accept_product.py` | Refuses a product whose eligibility is not `ELIGIBLE`, once the policy's `acceptance_gate` is `REQUIRED` (Section 8). |

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

The ratchet does not soften the evidence. The 4 known canonical findings are `FAIL` in the evidence, and the product is `INELIGIBLE` with them. CI refuses only what is new. Neither the baseline nor the ledger is edited by hand: `assurance_run.py --write-baseline`, `standalone_conformance.py --write-ledger`.

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

## 7. What is not built

| Gap | Effect today |
|---|---|
| No verifier for `SOURCE_INTEGRITY`, `ANSWERABILITY`, `PROJECTION_COMPLETENESS` | Open needs in every bundle. |
| `PROJECTION_INTEGRITY` and `DEPLOYMENT_INTEGRITY` are produced on demand | `verify_projection_manifest.py` and `drift_detector.py` write them when someone runs them (the latter against an accepted fingerprint). CI runs neither, so they are open in the bundle. `SEARCH_MEMBERSHIP` and `SEARCH_RETRIEVABILITY` are produced by `verify_search_index.py`, which CI does run. |
| `RESPONSIVE_LAYOUT`, `ACCESSIBILITY` | Open. The browser audits exist (`tools/site-audit/`) but are not wired to write evidence. |
| `SELF_CONTAINMENT`, `ANSWER_CORRECTNESS`, `DIMENSIONAL_CORRECTNESS` on authored questions | `INCONCLUSIVE` or `NOT_APPLICABLE`: no authored record declares a `problem_specification` or a `computation_model`. Declaring them is authoring work. |
| `ANSWER_VERIFIED` is advisory | A key checked only by its author is reported (`AUTHOR_ONLY`), not blocked. |
| Two ratchets | The baseline (canonical, by key) and the ledger (pages, by count) are separate files with separate tools. |
| Mathematics reference collisions | 4 nested-id collisions in `LIB-MATH-LINEAR-EQUATIONS` exist on `main`. They are real, they are in the baseline, and they keep `REFERENCE_INTEGRITY` failing for that package until fixed. |

## 8. Owner decisions

1. `learner-release-default.acceptance_gate` is `ADVISORY`. Setting it to `REQUIRED` makes `accept_product.py` refuse a product that is not `ELIGIBLE`. Today no product would be (Section 7).
2. `ANSWER_VERIFIED`: whether a key checked only by its author should block admission.
3. The scope policy's `DEFER` entries that no scope document row names.
4. The Mathematics collisions: fix in the library, or record as accepted debt.
