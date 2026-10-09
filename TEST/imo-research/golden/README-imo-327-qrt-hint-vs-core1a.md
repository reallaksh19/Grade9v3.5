# Golden learner-facing samples — Core2A/item hint versus Core1A concept-first repair

**Issue:** [#327](https://github.com/reallaksh19/Grade9v3.5/issues/327) · **Draft candidate:** [#333](https://github.com/reallaksh19/Grade9v3.5/pull/333), stacked on #312 · **Authoring goldens only:** no user research, QRT Owner verdict, academic promotion, real original-SOF Core2, learner release, actual interaction/assessment implementation or source clearance.

## Matrix coverage, not a claim of 28 audited productions

The authoritative [7 cognitive demands × 4 derived difficulty bands](../../../Shared/quality/question-demand-matrix.v1.json) defines **28** distinct `QRT-DEMAND-Dn` cells. We freeze **three different representative cells (3/28)** here. The primary demand is the learner's decisive act, not question type; D1–D4 is derived mechanically from five academically authored evidence components. The three examples below are independent samples, **not an assertion that 25 other cells pass a learner experience audit**.

| Band \\ demand | RETRIEVE | EXPLAIN | APPLY | MODEL | REPRESENT | SYNTHESIZE | JUSTIFY |
|---|---|---|---|---|---|---|---|
| D1 | — | — | — | — | — | — | — |
| D2 | — | **Golden 1** | — | — | — | — | — |
| D3 | — | — | — | **Golden 2** | — | — | — |
| D4 | — | — | — | — | — | — | **Golden 3** |

**Do not confuse QRT `H1,H2,H3,S1,S2,S3,P1,P2,P3,M1,M2,M3`** (the 12 author/reviewer *semantic objectives*) with exactly three mandatory user-visible hints. The examples intentionally show three optional item-help rungs as one possible authored UI. The QRT matrix never establishes a quota. The protected `W` step changes with each cell and is not revealed by pre-attempt question hints.

## Golden 1 — EXPLAIN–D2 (short conceptual connection)

**Question shown before attempt:** For real n, *why* is `5^(n+1) = 5 * 5^n`, rather than `5^n + 5`? Exhibit a discriminating example.

**Core2A/item lane:** H1 asks what changed in the exponent; H2 reminds the familiar same-base power law; H3 invites the learner to write `n+1` as a sum and complete the explanation. **Protected W:** give the law-to-outcome warrant and disprove the additive relation. Do **not** furnish the proof or test value in a hint.

**Core1A concept lane (separate from question):** Start with `P=3^2=9`; compare `3^3=27=3P` against `P+3=12`. Derive the principle that one exponent increment appends a factor. **Concept-only checkpoint:** for `Q=2^r`, choose `2Q` versus `Q+2`, explaining the law. Then guided application on base 7 and fresh unassisted transfer on base 11.

**Reviewer reference answer, not a pre-attempt hint:** `5^(n+1)=5^n*5^1` and n=0 refutes `5^n+5`: 5 versus 6.

[Golden JSON](imo-327-explain-d2.v1.json)

## Golden 2 — MODEL–D3 (choose an exponential model)

**Question shown before attempt:** The actual **wholly authored Core2A** draft #312 question: `4^(2u+1)=16^u+192`, real u.

**Core2A/item lane:** H1 points to linked bases 4 and 16; H2 mentions power-of-power and same-base product laws separately; H3 asks the learner to choose their own consistent representation. **Protected W:** choosing `t=4^(2u)=16^u>0` and recognising the multiplier `4t`, which must *not* appear in hints.

**Core1A concept lane:** Before the failed question, compare `P=2^3`, `2^4=2P`, not `P+2`; state `b^(r+1)=b*b^r`. **Concept-only checkpoint:** use `Q=5^n`, choose `5Q` or `Q+5` *with a reason*. Only then examine the separately authored 3/9 teaching equation. **Fresh unassisted exit:** `5^(2v+1)=25^v+100`.

**Reviewer reference answer, not a hint:** `t=64`, `u=3/2`, both original sides 256.

**Source-role hold:** This is **Core2A**, *not* an original SOF Core2 question. Source custody/rights must not be smuggled in through QRT sample labels.

[Golden JSON](imo-327-model-d3.v1.json)

## Golden 3 — JUSTIFY–D4 (prove existence, uniqueness and exception)

**Question shown before attempt:** For a>1, real k, determine *with proof* when `a^(2x+1)=(a^2)^x+k` has exactly one real solution. Include k=0 and explain what changes for 0<a<1.

**Core2A/item lane:** H1 clarifies the quantifiers and three obligations; H2 points only to the range and uniqueness *properties* of positive-base exponentials; H3 suggests a necessary/sufficient/uniqueness structure. **Protected W:** construct the sign-compatible iff argument and the exception. Hints must not state `(a-1)t=k`, `k>0`, `k<0` or the inverse formula.

**Core1A concept lane:** Away from the proof, inspect the positive range of `Z=2^r`; understand how a signed coefficient acts on a positive variable and why injectivity is separate from existence. **Concept-only checkpoint:** decide whether `4^q=0`, `4^q=-2` or two different q giving 16 are possible, with reasons. Guide `3Z=12` versus `-2Z=12` (Z>0); then require a fresh **0<b<1** proof case with b=1/2.

**Reviewer reference answer, not a hint:** `(a-1)t=k` with t>0 implies k>0 for a>1 and k<0 for 0<a<1. Uniqueness follows because positive-base exponentiation is one-to-one; k=0 is excluded in both cases.

[Golden JSON](imo-327-justify-d4.v1.json)

## Golden acceptance checks and limits

The accompanying `tests/test_imo_327_qrt_help_golden.py` must:

1. Compile the unchanged repository 7×4 source to 28 distinct QRT cells, resolve each fixture from its **five actual authored component judgments**, and verify the exact required template ID, 12 review objectives and protected W.
2. Confirm the MODEL–D3 sample's stem, origin, difficulty evidence and Core2A exposure against the **actual current #312 candidate**, rather than letting this fixture invent an original SOF Core2.
3. Reject a leaked item answer/model/proof in H1–H3, a concept explanation collapsed to an answer toggle, shuffled hint ordering, a false source-Core2/academic/Owner release, or a declared runtime gate/independent credit that does not exist.
4. Check representative mathematics for D2 (real index factor), D3 (real equation and unseen exit) and D4 (both base intervals, sign, zero, unique invertible positive exponent).

**What this does not prove:** the content does not implement a functioning learner input, a semantically verified Core1A gate, trusted/signed hint-use telemetry, author/Owner QRT acceptance, an authentic original-paper Core2, a new unseen attempt after remediation, a browser/screen-reader UX trial or production release. `reviewer_only` is a test fixture answer reference within a **public source repository**, never cryptographically protected answer storage. These JSON records must not be copied into learner pre-attempt payloads; actual render/attempt safety requires a separate real-runtime gate.

### Sequence to validate after eventual runtime implementation

`ITEM_ATTEMPT_STARTED` → `ITEM_HINT_DISCLOSED? (ASSISTED)` → `INITIAL_ATTEMPT_COMMITTED` → `REPAIR_CONCEPT_FIRST` → `NEUTRAL_CHECK` → `GUIDED_DIFFERENT_INSTANCE` → `FRESH_UNSEEN_ITEM` → `UNASSISTED_VERIFIED?`

Showing the answer, visiting repair, or returning to the *same* problem can never create an independent-mastery receipt. The TEST renderer **now partially implements** the beginning: H1 is optional, disclosed hints set a best-effort local assisted flag, and Core1A's guided explanation stays hidden until a neutral-law choice plus rule-worded reason is entered. This is **format validation only**; it is bypassable in client HTML, cannot certify understanding, and does not implement a fresh unseen retry or signed mastery evidence. The full sequence above remains unimplemented; these files are frozen review targets, not a fake pass.
