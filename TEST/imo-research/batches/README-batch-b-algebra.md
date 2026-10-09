# Batch B — 11 algebra source positions, separated conceptual decisions

**Authority:** [Governing IMO issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294). This is a source-specific producer review, not an academic Core lesson approval. The separate independent [Core construction review #306](https://github.com/reallaksh19/Grade9v3.5/pull/306) owns conceptual teaching specifications; it must be compared and adjudicated through #294 rather than silently substituted into this source record.

**Exact base:** `main@7ee763c2db61f228d8064cdaea8bc4bb47ab529e`. **Programme:** 68 inventoried source positions = 24 + 12 + 22 + 10; seven authored-practice candidates remain separate. **Academic batching:** 8 Number Systems (Batch A, [#305](https://github.com/reallaksh19/Grade9v3.5/pull/305)) + **11 algebra (this batch)** = 19 source positions mapped. This is not 19 source Core2 products or 19 accepted concepts.

The exact research row, scanned/source page, prior math observation, mathematical warrant, predicted wrong path and hold are in [the machine-readable Batch B crosswalk](batch-b-algebra-source-capabilities.v1.json). **No SOF stem, option set, original diagram or PDF bytes are copied.** Earlier B01–B04 and official sample mathematical pilot evidence is reused as *agent-worked source observations*, not peer-certified math or official full-paper key.

## All eleven source-level mathematics/meaning decisions

| Source position | Reused agent audit/result | Why this is a distinct learner decision |
|---|---|---|
| 2023–24 A Q28 | B02-005; multivariable polynomial difference, source choice C | Decide which polynomial is subtracted from which; only like monomials combine; reverse by adding the difference |
| 2025–26 A Q45 | B04-007; `x(x−3)(x+4)`, B | Algebraically factor volume then separately enforce positive-length domain (`x>3`) |
| 2026–27 sample Q7 | Sample pilot; `P(4)=60`, source key D | Translate two linear-divisor conditions into two zero/root constraints on unknown coefficients |
| 2024–25 B Q44 | B01-005; `4x⁴−2x³+27x²+4x+11`, B | Expand full square with middle term, then subtract and sign-track the second polynomial; preserve historical **conflict 005** over the original exam section |
| 2023–24 A Q38 | B03-008; `−25x+y=700`, A | Separate fixed-cost intercept from rate per extra litre before rearranging |
| 2024–25 B Q24 | B02-009; `p=3,q=5`, A | Apply a known ordered pair to two parameter equations, not solve for the pair again |
| 2025–26 A Q29 | B01-007; `q=−1`, A | Use the supplied shared point; derive the first parameter and carry it into the second relation |
| 2026–27 sample Q4 | Sample pilot; `y=2x−1`, sample key B | Infer slope and intercept from tabulated ordered pairs, then check unused entries |
| 2025–26 A Q37 | B04-002; future age `20`, A | Move both ages through a historical time shift before applying the 5:1 ratio |
| 2025–26 A Q42 | B01-015; `28x−4y=75`, B | Preserve currency units and every term when clearing decimal coefficients |
| 2025–26 A Q44 | B04-006; P's income `4000`, C | Model independent income and expense ratio scales, then impose *equal savings* as two simultaneous constraints |

**Host distinction:** Nine of these are from school-hosted SOF-branded scans, not organizer-hosted documents. Two are 2026–27 SOF organizer-sample positions; the sample math audit reports printed keys but does not supply an independently accepted academic reviewer or source-republication rights. The paper year/set/printed position and PDF index are retained individually in the JSON.

## Specific conceptual reuse boundaries

1. **Known point / parameter equations** (Q24 versus Q29): Both involve point substitution, but Q29 requires a **dependent parameter-elimination sequence**, unlike independently constraining p and q at Q24. Do not publish one indistinguishable repair by topic-name similarity.
2. **Polynomial work** (Q28/Q45/sample Q7): Sign-disciplined polynomial difference, symbolic factorization subject to a positive-dimension *model*, and factor-theorem zero constraints are **three different decisive inferences**. The sample polynomial divisibility question is unrelated to the existing authored consecutive-integers divisibility pilot.
3. **Contextual linear modelling** (Q38/Q42/Q37/Q44): fixed/rate decomposition, unit-scaled price relationship, synchronized age shift and two-ratio savings system have different constraints and likely wrong paths. Q44 is a higher-value candidate for reviewed teaching because treating income/expense ratios as a single scaling variable erases a genuine independence condition.
4. **Table vs equation** (sample Q4 versus Q24/Q29): Inferring a rule from several tabulated pairs is not the same as testing a *given* point against parameterized equations.

**Suggested hard teaching investigations (not approved Core1A):** sample Q7's simultaneous root constraints, 2025 Q44's independent ratio scales and Q45's physical-domain reasoning. Original authored diagnostic proposals can use fresh symbols/numbers only; no SOF original content or answer options should be reproduced. Reviewer #306 may accept, narrow or reject teaching links through #294.

## Conflict / rights / source admission

Batch B inherits **one** registered case: `IMO-SOURCE-CONFLICT-005` at 2024–25 B Q44, where a formerly mislabeled exam section is historically documented. The case cannot be removed just because B01 mathematics has a consistent answer. The programme retains ten known cases affecting eleven source positions; no new conflict is invented or silently resolved here.

| Gate | New Batch B admission |
|---|---:|
| Source positions with individual research capability proposals | **11/11** |
| Physically retained/reverified exact source PDF custody | **0** |
| Source components authenticated and reproduction rights cleared | **0** |
| Independently externally accepted source mathematics / full-paper keys | **0** |
| Authentic source Core2 admitted or learner-rendered | **0** |
| Canonical Core1A, accepted QRT or owner publication decisions | **0** |

The previous [#304](https://github.com/reallaksh19/Grade9v3.5/pull/304) download probe is **temporary runner verification, not legally cleared retained source**. Until each authentic item has verified source custody and copyright scope, this crosswalk permits external reference and authored concept planning only.

**Focused tests:** `python -m unittest discover -s tests -p 'test_imo_batch_b_algebra.py' -v`, then the owning `SOF IMO research seed integrity` CI. The tests check exact 11/68 membership, prior math source/result/option-page joins, original conflict 005, closed product gates and algebraic reverse oracles. Status **NOT_RUN** until the new branch workflow executes. PR remains draft even when tests become green.
