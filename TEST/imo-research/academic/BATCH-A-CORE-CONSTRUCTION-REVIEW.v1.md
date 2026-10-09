# IMO Grade 9 — independent Core conceptual review, Batch A

**Status:** ACADEMIC_DESIGN_PROPOSAL / NOT_ACCEPTED / NOT_CORE_PRODUCT  
**Scope:** Governing [#294](https://github.com/reallaksh19/Grade9v3.5/issues/294), review of [draft #305](https://github.com/reallaksh19/Grade9v3.5/pull/305), separately from its producer; source research basis \`main@7ee763c2db61f228d8064cdaea8bc4bb47ab529e\`.  
**Authority:** Research-only interpretation. No independent verification of original SOF text/options, publisher rights, printed keys, academic owner acceptance, canonical library write, QRT admission or learner publication. The existing [Core1A](../../../Shared/roles/CORE1A.md) and [Core2](../../../Shared/roles/CORE2.md) role contracts remain authoritative.

## 1. Decision on the Batch A academic model

Batch A has eight inventoried positions but **does not warrant eight Core1A modules**. The following are candidate *reasoning routes*, not a replacement taxonomy or canonically assigned capability identifiers. Interpret the #305 mappings as question-level **hypotheses from earlier agent audits** until retained-source component review permits confirmation.

| Source position | Candidate decisive inference | Conceptual construction / learner diagnosis | Explicit boundary |
|---|---|---|---|
| 2023–24 A Q18 | Evaluate a rational expression, **then** apply its additive inverse | Grouping, sign tracking and inverse as an operation on a completed result | Its source options are disputed (conflict 003): option letter is not invariant under reorder |
| 2025–26 A Q28 | Read **identity vs inverse** as a semantic decision before calculation | Contrasting \(x+0=x\) and \(x+(-x)=0\) | Conflict 006 changes the mathematical question; no silent stem correction |
| 2024–25 B Q33 | Model coupled numerator/denominator constraints before solving | Maintain original quantities vs transformed quantities; reverse-substitution test | Domain/denominator exclusions and original vs modified fraction must remain distinct |
| 2024–25 B Q26 | Rewrite exponential terms to reveal a common multiplicative object | Power laws, common-base substitution, factor relation, inverse mapping | Addition of exponential terms does **not** allow exponent-by-exponent equality |
| 2025–26 A Q35 | Parse nested signed fractional indices, with parentheses and exact roots | Positive-base law, reciprocal vs negative sign, principal roots | \((a^b)^c=a^{bc}\) needs domain assumptions, especially for nonpositive bases |
| 2025–26 A Q36 | Restore original cardinality before inverse square modelling | Square array \(N=n^2\); reverse an object-loss operation *before* taking positive root | \(\sqrt{N}\) is the nonnegative principal root; count \(n\) must be an admissible integer |
| 2025–26 A Q49 | Test claims independently with exact substitutions/counterexamples | Universal vs existential statement, exact radical simplification | A radical symbol alone does not imply irrationality |
| 2026–27 sample Q9 | Preserve notation scope before interpreting truth claims | Grouped radicals, powers, exact decimals/rationals; per-statement checking | Conflict 010: owner paraphrase and printed notation cannot be interchanged |

**No link from the current authored consecutive-integers/divisibility pilot to these eight positions has been established.** That pilot can test the renderer, not authenticated-source Batch A teaching coverage.

## 2. Selected golden Core1A construction — common-base exponential relations

**Source-facing candidate:** 2024–25 B Q26. **Core crux:** See that two exponentials are multiples of a common *quantity*, not two unrelated symbols. This is distinct from merely memorizing index laws.

- **Entry assumptions:** Positive integer bases; \(a^{m+n}=a^m a^n\); \((a^m)^n=a^{mn}\) in qualified domains; equality preservation when subtracting terms; injectivity of \(a^x\) for \(a>0,\ a\ne1\) when using real exponents.
- **Construction:** (i) express mixed bases using one base; (ii) identify a single common exponential \(t>0\); (iii) justify a **multiplicative** relationship between terms (e.g. one term is \(5t\), not \(t+5\)); (iv) solve the resulting linear relation in \(t\); (v) map \(t\) back to the original exponent; (vi) verify in the untransformed equation.
- **Worked authored anchor, not an SOF question:** Solve \(3^{2x+1}=9^x+162\). Because \(9^x=3^{2x}>0\), put \(t=3^{2x}\). Then \(3^{2x+1}=3t\), hence \(3t=t+162\), \(2t=162\), \(t=81=3^4\). Therefore \(2x=4,\ x=2\). Independent check: \(3^5=243=81+162\).
- **Wrong path:** Inferring \(2x+1=x+162\) by “equating exponents” across a sum. **Diagnostic:** Ask which two expressions form powers of the *same base* and which symbol is a standalone additive term; request the multiplicative factor between powers.
- **Representation:** Side-by-side equivalent expressions \(9^x=3^{2x}=t\) and \(3^{2x+1}=3t\); connector arrows labelled “same positive quantity” and “multiply by 3”. No unbound decoration.
- **Boundary check:** If \(t\) is computed as nonpositive, reject it since \(t=3^{2x}>0\). The substitution may fail to yield a real \(x\) for algebraic \(t\le0\); do not force a logarithm or invent a solution.
- **Independent exit, support hidden initially:** Solve \(2^{2y+1}=4^y+64\). Model: \(t=4^y>0;\ 2t=t+64\), so \(t=64=4^3\), \(y=3\). Require back-substitution \(2^7=4^3+64=128\).
- **Potential changed-decision transfer, separate review:** \(3^{z+2}-3^z=216\). Learner must choose to factor \(3^z\), obtaining \(8\cdot3^z=216\) and \(z=3\). Do not label this Core2B without demonstrating a genuinely protected changed demand relative to exposure; otherwise treat as supported same-family practice.

**Teaching depth:** Provide the full step-by-step construction as Core1A, then test open-ended inference in Core1B and support familiar application in Core2A only if later product scope authorizes those roles.

## 3. Selected golden Core1A construction — signed and fractional indices

**Source-facing candidate:** 2025–26 A Q35. **Core crux:** Parentheses determine which operation is exponentiated; a negative exponent denotes a reciprocal (for nonzero base), not a negative-valued power.

- **Conventions before calculation:** Rational powers are defined in the **positive real base** domain for this construction; principal positive root; \(a^{-p}=1/a^p\) for \(a>0\); \(a^{m/n}=(\sqrt[n]{a})^m\) where defined. Do not generalize fractional-power composition to arbitrary negative bases.
- **Construction:** (i) parse the exponent syntax with explicit parentheses; (ii) turn denominator/root notation into a named quantity; (iii) apply reciprocal law; (iv) apply the outside exponent to the whole interior quantity; (v) simplify exactly before division; (vi) reverse-check through the root relation.
- **Worked authored anchor:** \((81^{-3/4})^{-2}=(1/27)^{-2}=27^2=729\). Independent qualified power-law check \(81^{(-3/4)(-2)}=81^{3/2}=9^3=729\).
- **Wrong path:** Reading \(81^{-3/4}\) as \(-81^{3/4}\), or raising only the numerator to the outer power. **Diagnostic:** Ask for \((8^{-1/3})^{-1}\); correct result \(2\), whereas an incorrectly signed interpretation produces \(-2\).
- **Representation:** An exponent parse tree with interior \(81^{-3/4}\), exterior \(-2\), and exact fourth-root branch \(\sqrt[4]{81}=3\); bind all branches to the same stated expression.
- **Boundary check:** \((( -1)^2)^{1/2}=1\), whereas \((-1)^{2(1/2)}=-1\) under a naïve law for arbitrary negative bases. This demonstrates why the positive-base convention matters. Keep the Grade 9 lesson's primary examples positive-base.
- **Independent exit:** Evaluate \((32^{-2/5})^{-3}\). Model: \(32^{6/5}=(\sqrt[5]{32})^6=2^6=64\). Require an explicit reciprocal justification.

**Critical source hold:** Q35's original scanned notation must be component-checked independently before inferring that the author's chosen parsing matches every printed parenthesis, radical and fractional power. The authored lesson is permissible as a separate candidate without source reproduction.

## 4. Selected golden Core1A construction — statement falsification and exact radicals

**Source-facing candidate:** 2025–26 A Q49 (a *proposed* source-math link, not printed content reproduced).

- **Crux:** Determine whether each quantified statement is true or false *independently*. A universal claim can fail on one valid counterexample; a numerical approximation cannot always establish exact equality.
- **Entry assumptions:** Rational versus irrational, nonnegative principal square root, distributivity and conjugates, exact polynomial substitution.
- **Construction:** (i) isolate the quantified claim and its domain; (ii) choose proof for an always-claim or a counterexample to refute it; (iii) compute exact values with proper brackets; (iv) classify *each* statement before interpreting any bundled response format.
- **Worked authored anchor:** Claim: “\(\sqrt{m}\) is irrational for every positive integer \(m\).” False. Take \(m=9\): \(\sqrt9=3\in\mathbb Q\). The symbol \(\sqrt{}\) alone does not imply irrationality.
- **Second authored anchor:** Claim: “The sum of two irrational real numbers must be irrational.” False: \(\sqrt2\) and \(2-\sqrt2\) are irrational, yet sum to \(2\). Verify the latter's irrationality: if \(2-\sqrt2\) were rational then \(\sqrt2=2-(2-\sqrt2)\) would be rational, contradiction.
- **Wrong path:** Selecting a response from approximate magnitude without exact checking, or inferring all radicals are irrational. **Diagnostic:** Compare \(\sqrt{16},\sqrt{12}\) and ask which is rational and why.
- **Representation:** Small logical table with statement, quantifier, intended witness/proof method, exact computation and verdict. No spurious geometric diagram.
- **Independent exit:** Refute or prove “the product of two irrational real numbers is always irrational,” and justify with a concrete pair. Model: \(\sqrt2\cdot\sqrt2=2\) disproves it.
- **Boundary:** A valid counterexample requires that both inputs meet the claim's domain; a counterexample to “all real \(x\)” cannot be an undefined expression.

**Source-hold:** The original Q49 compound statements must be verified against a genuine item readback before an authentic-source Core2 answer is treated as fixed; this design intentionally does not quote those statements.

## 5. Conditional, smaller teaching routes — do not create eight modules by reflex

1. **Rational identity vs inverse (Q18/Q28):** Shared vocabulary foundation but two different learner decisions. Build a two-column identity/inverse comparison and a sign-evaluation microrepair. A learner-facing source-based Q28 awaits exact editorial source disposition.
2. **Constraint inversion (B Q33):** Build a notation bridge from original fraction \(n/(n+k)\) to modified \((n-a)/(n+k+b)\); ask the learner what each symbol represents *before* applying an equation. Require admissible denominators and a final original-fraction check.
3. **Square-array reverse modelling (A Q36):** Restore destroyed/removed objects to original \(n^2\); choose positive integer \(n\); distinguish count from geometry. This may need a brief targeted repair, not a full HARD construction.
4. **Sample Q9:** Its exact radical grouping and printed notation have a recorded conflict. Teach notation scope only from independently authored examples until component custody is resolved.

## 6. Core2 ⇄ Core1A ⇄ practice interaction contract

The same canonical capability/microtopic must anchor linked teaching; a topic-name match is insufficient.

| Stage | Learner-facing behavior | Protected / authority-sensitive dimension |
|---|---|---|
| Core2 attempt | Show exact rights-permitted source, conditions, options, figures; solicit typed or paper commitment | Before commitment, do not reveal the source key or decisive solution move through visible hints, PDF, accessibility text or search surfaces |
| Diagnosis | Offer *hypothetical* wrong-path checks, not a claim about an unobserved individual learner | Do not infer mastery from merely clicking/committing |
| Core1A repair | Reveal the complete, reusable inferential construction with justification and representation bridge | Do not use an official key as the authority for mathematical teaching |
| Core1B elicitation, if in scope | Ask the learner to reconstruct exactly the same canonical inference; provide self-check closure | Cannot reduce intrinsic conceptual coverage relative to Core1A |
| Core2A practice, if in scope | Familiar-family authored examples with a complete reasoning route and targeted support | Authored provenance must remain labelled; no relabelling as authentic Core2 |
| Core2B transfer, if in scope | Introduce a stated changed demand, preserving the changed decision until attempt | New numbers or new story alone do not justify a transfer claim |

**Answer-security honesty:** A disclosure closed in the UI while its content is already present in raw HTML is *not secure exam isolation*. Record this as a pedagogical reveal and test pre-attempt behavior in rendered DOM, accessible names, print/PDF and search. Do not promise secrecy against viewing source.

## 7. Independent academic review requests to the IMO producer

- Resolve Q26: Does the real printed question demand discovering the factor relationship, or is the transformation already suggested? Link the *exact* source-dependent decisive move and justify depth.
- Resolve Q35: Which parentheses and radical indices actually occur? The lesson may be mathematically correct yet answer a different transcription.
- Resolve Q49: Are the statements individually universal/existential, or simple numeric assertions? Diagnosis must match quantifier structure actually present.
- Resolve source conflicts 003/006/010 without silently modifying printed stems or option order.
- If a diagram would teach the concept, bind its labels and transitions to semantic steps. No decorative scene quota.
- For each proposed concept link, record: source-reasoning evidence ID; actual decisive inference; prerequisite; new learned move; expected wrong path; independent exit; applicability boundary; match/mismatch rationale and status.
- Do not add a new academic acceptance gate, canonical scoring system, library schema, or parallel QRT classifier. These are reviewer proposals to be reconciled with existing records.

## 8. Research disposition

**ACADEMIC_DESIGN_READY_FOR_CRITIQUE** means these authored worked examples and proposed conceptual separations are ready for the agent to compare against existing library and eventually source evidence. It does **not** mean peer review, source fidelity, genuine Core2 eligibility, rendered Core1A, academic admission, or permission to merge a product.

### Smallest next useful learner slice

Make the **Q26-like common-base relationship** the first genuine source-aligned teaching investigation, because its decisive inference and reverse check can be tested in wholly authored examples without copying SOF content. Present one canonical-shaped concept candidate and one draft renderer output for actual pedagogical review; retain its source-math link as provisional pending exact authenticated item custody. Independently finish QA of the existing divisibility TEST preview; do not call that source-aligned coverage.