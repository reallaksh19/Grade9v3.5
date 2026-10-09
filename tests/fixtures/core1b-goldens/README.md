# Three Core1B student journeys — golden behavioural fixtures (HELD TEST)

**This is a test fixture, not canonical lesson admission, QRT owner signoff, educator review, or learner publication.** It freezes three cases the owner tried in the standalone offline HTML prototype, plus their protected answers and distinct stages. Do not put this directory in `public/` or upload raw answer-bearing HTML as a CI artifact.

## Four bands × seven cognitive demands

Actual repository QRT: `Shared/quality/question-demand-matrix.v1.json`; band order D1/D2/D3/D4; demand order RETRIEVE/EXPLAIN/APPLY/MODEL/REPRESENT/SYNTHESIZE/JUSTIFY. `matrix-coverage.v1.json` lists **all 28 cells**, including the **25 not exercised**. The three intentionally distinct sample selections:

| Case | Subject | Selected base QRT cell | Decisive learner work |
| --- | --- | --- | --- |
| consecutive | Math: divisibility | **JUSTIFY-D3** | General even-factor proof, modulo-3 exhaustion, coprimality; distinguish samples from a proof |
| algebra | Math: algebraic identity | **REPRESENT-D2** | Translate a binomial square correctly, preserve cross terms, distinguish a special value from identity |
| motion | Physics: motion | **MODEL-D2** | Choose distance/speed versus displacement/velocity and test a changed trip |

These are authored fixture classifications **not** new canonical QRT resolutions. The math case originates in merged TEST pilot; algebra and physics remain newly authored **UNAPPROVED** demonstrations. **No D1 or D4 case is covered; do not claim the 4×7 grid is validated.**

## Student-centred expected experience

1. Encourage an original idea without requiring a length or correctness threshold. Short `33` and an explicit paper attempt must unlock **diagnostic reconstruction only**; blank/whitespace alone cannot.
2. Reveal focused diagnosis one prompt at a time. A wrong attempt must be welcomed and differentiated from a validated proof.
3. A repair commitment is needed before the model/reference answer can be opened; the worked answer is clearly labelled **Answer 1 / Answer 2 / Answer 3**, not buried as “reference reasoning”.
4. Independently require an attempt for each changed-boundary question. Completing proof/repair must not unlock the boundary answer.
5. Never award automatic mastery or claim AI-judged student correctness. This is **UI behavioural goldens**, not evidence a real Grade 9 learner improved.

Fixtures intentionally store answer prose **for offline TEST use only**; no key is packaged into the public evidence artifact. Linked historical HTML prototype was delivered to the user in chat (not in repository publication). The canonical merged Core1B renderer remains a separate subject of its own browser test.

## Acceptance and unresolved holds

Run `python -m unittest tests.test_core1b_three_case_goldens -v` along with existing `tests.test_core1b_reconstruction_maturity` and Playwright Core1B browser QA. Frozen guard rails include 28-cell matrix identity, semantic case-to-cell mapping, no fake 28/28 coverage, math/physics warrant falsifiers, legitimate short response, whitespace denial, paper escape, independent boundary, authentic-source nonadmission, and no automatic grading.

U6 independent Grade 9 learning / assistive-tech / source custody, and print/key owner review **NOT_RUN / NOT_GRANTED**; all experimental golden fixtures stay TEST-only and cannot change canonical-QRT ownership.
