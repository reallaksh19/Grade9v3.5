# Grade 9 IMO · Mathematics topic-wise public reference browser

Issue [#298](https://github.com/reallaksh19/Grade9v3.5/issues/298).
Owner direction dated 2026-10-08: "segregate questions to relevant topics and post in math tab."

## Display scope

- **68** SOF original-paper **question-number references**, derived without retyping or embedding their copyrighted question stems, options, figures or answer keys. Each gives a research-classified topic, a concise concept/demand description, original-paper locator and a link to read the original paper at its source host. **Not reviewed Core2 custody**; no publisher reproduction permission is inferred.
  - 58 full-paper positions across 2023–24 Set A, 2024–25 Set B and 2025–26 Set A.
  - Eight positions in the 2026–27 organizer sample in the 66-row seed.
  - Two additional sample positions (sample Q1 and Q3) documented separately from the 66-row seed.
- **Seven** model-authored and newly worded original practice questions shown **in full as draft public previews**, each linked to a proposed mathematics topic. They are explicitly **not official SOF** source questions and remain unreviewed for Core/QRT acceptance and learner-feedback quality.
- **15 populated topic groups**, built from the 17 official Mathematics syllabus topic labels and two analyst adjunct sections (LOGIC/QUANT) without implying that the latter are SOF Section 2 topics. Four of the official Mathematics topics are not in this scoped source/practice set, and no false completeness is claimed.
- The Mathematics tab publishes links to this page in both `public/mathematics/index.html` and `docs/mathematics/index.html`. The two new browser pages are identical.
- A topic dropdown, question-type filter, search box, jump-to-topic links, stable question IDs, explicit source-vs-authored labels, and notices for known source discrepancies are provided. No answers or automatic grading are posted.
- Original practice #006 (two simultaneous equations) and #007 (multi-step coordinate transformations/determinant reasoning) retain **Grade 9 scope review** warnings.

## Data/authority separation

`Mathematics/research/imo-g9-topic-browser.v1.json` pins exact Git blob SHA receipts for:
1. `TEST/imo-research/taxonomy/seed-question-topic-map.v1.jsonl`
2. `TEST/imo-research/taxonomy/sof-class9-topic-registry.v1.json`
3. `TEST/imo-research/verification/official-sample-2026-27-new-positions.v1.json`
4. `TEST/imo-research/seed/sources.json`
5. `TEST/imo-research/original-practice/seven-cell-original-problems.v1.json`
6. `TEST/imo-research/adjudication/source-discrepancy-register.v1.json`

The original evidence records are unchanged. Human academic signature research waiver remains distinct from publisher rights and dated product-owner acceptance. The **public posting of the authored research-preview stems** is an explicit owner request; it does *not* magically promote them to canonical Core2, Core1A, Core2A, accepted QRT or a licensed official exam reproduction. Avoid saying "no text was published": the seven authored draft stems are visibly posted as research previews. There are **0 source SOF stems republished, 0 QRT accepted, 0 Core2 admitted, 0 authored Core admitted**.

## Reproduction and gating

```sh
python TEST/imo-research/validate_math_tab_imo_topics.py
python -m unittest discover -s tests -p 'test_imo_math_tab.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The dedicated SOF IMO research-integrity workflow runs the validator and wildcard-discovered tests. It must pass on the exact latest PR head; broad unrelated failures may be reported independently. This is *site index and authored preview placement*, not a complete Core product, browser usability certification, source digest custody or academic review.
