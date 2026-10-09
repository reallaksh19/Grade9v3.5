# Core1B reconstruction: mathematical and offline-closure review

**Status:** Core architect's **self-audit**, independent reviewer **NOT_RUN**, learner trial **NOT_RUN**, acceptance/publication **NOT_GRANTED**.  
**Context:** [draft PR #311](https://github.com/reallaksh19/Grade9v3.5/pull/311). This is an authored, source-safe **TEST** vertical slice; authentic SOF/NCERT source Core2 and all publisher rights remain unresolved. Core agent issue coordination is restricted to IMO #294 / NCERT #68.

## Academic target and falsifiable mathematical oracle

**Learner problem:** For any integer `t≥3`, reconstruct a proof that
`(t−2)(t−1)t` is divisible by 6. Do not infer "for all" from three tested examples. An otherwise correct numerical product cannot substitute for an exhaustive warrant.

One valid proof, stated fully so the reviewer can audit each obligation:

- **General quantifier:** Let `t≥3` be arbitrary; its three factors are consecutive positive integers.
- **Parity:** `t−1` and `t` are consecutive; one is even, so 2 divides the whole product.
- **Mod 3, exhaustive:** If `t mod 3` is `0`, then `t` is divisible by 3; if it is `1`, then `t−1` is; if it is `2`, then `t−2` is. These are all possible integer residues, so 3 divides the product for every permitted `t`.
- **Coprimality:** Since the same whole integer product is divisible by coprime integers 2 and 3, it is divisible by 6. The two divisors can arise from *different* factors; no single factor needs to be a multiple of 6.
- **Counterexample boundary:** Replacing the three consecutive factors by only two, `(t−1)t` for all `t≥2`, is false: `t=2` gives `1×2=2`, not a multiple of 6. The even-factor guarantee survives; the guaranteed multiple-of-three factor does not.

This is one concept re-elicited, not a novel independent six-Core topic or Core2B changed-demand transfer. Its relationship to Core1A `n(n+1)(n+2)` is `n=t−2`. The re-elicitation is *who performs the generalization and when the warrant is available*: Core1A provides a full route; Core1B requires a learner-written proof and then makes rubric, diagnosis and closure available.

## Exact six-step Core1B semantic review

| Obligation | Authored product | What would constitute failure |
| --- | --- | --- |
| **Predict** | Judge whether checking `t=3,4,5` proves an arbitrary-t claim | Accepting finite samples as a universal theorem |
| **Attempt** | Typed general proof for arbitrary `t`, with parity, all 3 residues and coprimality | Merely calculating `t=3,4,5` or writing "always true" |
| **Reconstruct** | Question-led route: what does "every" require? which pair is even? where is a factor of 3 in each residue? how do divisors combine? does it cover every t? | Giving expert prose before learner commitment |
| **Diagnose** | Existing microtopic misconception: checking particular values is enough; diagnostic question asks what general invariant guarantees untested cases | A vague "try again" without discriminating the mistaken proof |
| **Repair** | Reconstruct full mod-2/mod-3 residue argument and the coprime-product rule from the same governed misconception entry | Treating the failure as only a careless numerical error |
| **Boundary** | Two-factor reduction `(t−1)t`, `t=2` counterexample | Rewording the original proof without testing its dependence on three factors |

**Self-contained closure:** The source package's governed `elicitation.predict.defensible_answer` and `elicitation.attempt.rubric[]` already carried correct knowledge. The earlier Core1B renderer displayed only bare criterion labels and accepted examples: it silently omitted the prediction answer, `rubric[].evidence_of`, and `attempt.rejected[]`. That was an **actual product defect**; students could not fully check wrong routes even after committing. The narrowly scoped Core1B render update now materializes all these **same source fields** only in the existing protected postattempt "Reconstruct" disclosure. No duplicate academic data or new schema is introduced. Targeted tests require the prediction answer, evidence explanations, both accepted/rejected examples, and precommit gate.

## Distinguish an attempt handout from an offline answer key

The repository's existing `tools/print/print-product.mjs` deliberately has two modes:

1. **`LEARNER_PDF`** prints the generated pages *without materializing protected answer templates*. The Core1B handout contains prediction, safe factor diagram, task, givens and boundary challenge. It must **not** reveal the worked solution or rejected-example commentary before the student has attempted it.
2. **`KEY_PDF`**, invoked with the existing `--key` option and a **separate evidence-only directory**, opens/materializes protected responses and full reconstruction including accepted/rejected answers, criterion evidence, prediction feedback and the counterexample boundary answer. This supplies an offline self-check without weakening the preattempt handout or creating another renderer.

The earlier `S1 PRODUCT-PRINT-FROM-PAGE` reported **three figures in the learner PDF** versus **four on the complete web pages**. That number difference is **intentional for the learner handout only**: Core1B's second figure is protected inside the postattempt answer. It would be academically misleading to declare the handout "fully self-tutoring" without a separate key, or to suppress the `S1` advisory. The new exact-head CI requires both PDF modes, separate receipts with exact input/PDF hashes, the key's previously omitted closure text, **2 Core1B key figures vs 1 Core1B learner figure**, and explicit absence of those answers from the learner copy. This is a semantic adjudication, not a waiver of the print check.

**Distribution warning:** KEY PDFs in CI artifacts are for academic review and local self-study *only*. Do not place them on a public learner route or package them under the same accessible URL as a withheld assessment without a deliberate product policy. The present branch is a TEST experiment, not a secure examiner-only system. Source HTML includes inert answer templates, so browser disclosure is **pedagogical** and not cryptographic security.

## Safety, accessibility, integration and limits

- **Controlled source authority:** The one `microtopic.elicitation` and its existing `misconceptions[]` are the only academic homes for this reconstruction. Existing package schema, Core1B role semantics, shared print tool and 28 QRT templates stay authoritative; no protected W move is silently redefined.
- **Independent check of mathematics:** The residue case `t=0,1,2 mod 3` points to `t,t−1,t−2` respectively; `t=2` is a genuine failure for two consecutive factors. Small values validate sample arithmetic but never establish the universal claim.
- **Automated user-interface evaluation:** Real Chromium tests inspect 320/390/768/1280 px plus 200%-text width, keyboard Enter, precommit withheld payload, synthetic typed attempt and revealed reconstruction. This is not a human grade-nine learner trial or screen-reader test.
- **Paper UX risk:** A teacher must clearly label and separately supply the **KEY_PDF** to an offline independent learner; a lone printed attempt handout is not closed self-tutoring. The product cannot claim offline independent completion otherwise.
- **Potential overhelp:** With access to previously studied Core1A, some students may simply recall the argument. No study has established whether learners can reconstruct without copying. Independent review should examine whether the sequential questions retain a meaningful inferential decision.
- **Provenance:** No official SOF Q26 stem, chart, figure, question key, NCERT source, rights or publisher PDF was copied. The author-generated triple ending at `t` is not original-source Core2 eligibility or QRT acceptance.
- **Release verdict:** Engineering evidence **PENDING exact-head key-mode confirmation**. Academic independent reviewer, real learner success, human screen reader, curriculum owner signoff and publication all **NOT_RUN / NOT_GRANTED**. The Core architect cannot self-approve those gates.

The next independent reviewer should inspect the actual learner/key PDF pair, check whether a child who gave one of the *rejected* answers can use the rubric and diagnose/repair prompts unaided, and verify the false two-factor boundary. Passing CI does not prove this instructional outcome.
