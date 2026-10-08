# SOF IMO Class 9 — source-to-syllabus taxonomy (issue #231)

**Research-only.** This indexes the 66 distinct paper-question positions of the Owner's compilation; it does not publish question text, certify SOF keys or admit a question to a Core. Source identity/wording/rights remain with `../seed/`.

## Authority and orthogonal classification axes

1. SOF's Class 9 official syllabus: https://sofworld.org/imo/class-9/imo-syllabus/imo-syllabus-class-9 (inspected 2026-10-08). There are **17 expressly named Section 2 topics**. Section 1 is verbal/non-verbal reasoning; Section 3 refers to Mathematical Reasoning and Quantitative Aptitude; Section 4 is HOTS over Section 2.
2. Class 9 Level 1 has 50 positions: Logical Reasoning Q1–15, Mathematical Reasoning Q16–35, Everyday Mathematics Q36–45, Achievers Q46–50. This positioning is an exam-section rule **for a full Level 1 paper only**, not the syllabus topic of a question.
3. The Owner's attachment holds 65 distinct compilation entries. Compilation Q38 maps to **two separately numbered original paper questions** and Q66–Q68 are aliases: 66 question IDs. Sample paper numbers Q1–10 cannot be assumed to be full exam Q1–10; their exam sections remain `null` until a genuine sample-paper section locator is checked.
4. Subtopic and learning-demand summaries are **analyst-proposed classifications** from the attachment. They have not passed an independent academic review. Don't mistake them for verified source taxonomy or proof of a learner misconception.

`sof-class9-topic-registry.v1.json` stores the organiser syllabus order, exam slots, 17 official topics and two distinctly labelled analyst grouping categories, `LOGIC` (Section 1) and `QUANT` (Section 3 quantitative aptitude). These adjuncts are not new official Section 2 topics. `sof-class9-subtopics.v1.json` normalizes the **49 provisional subtopic/microconcept groups**. `seed-question-topic-map.v1.jsonl` links each source-instance ID to exactly one provisional primary topic, subtopic and microconcept, independently of its exam section, and preserves the no-acceptance state.

## Current coverage (66/66 mapped, not academically accepted)

| SOF Section 2 topic | Candidate records |
|---|---:|
| Number Systems | 8 |
| Polynomials | 3 |
| Algebraic Identities | 1 |
| Coordinate Geometry | 4 |
| Linear Equations in Two Variables | 7 |
| Introduction to Euclid's Geometry | 3 |
| Lines and Angles | 3 |
| Sequences and Progressions | **0** |
| Triangles | 5 |
| Quadrilaterals | **0** |
| Areas of Parallelograms and Triangles | **0** |
| Circles | 2 |
| Area and Perimeter | **0** |
| Constructions | **0** |
| Surface Areas and Volumes | 6 |
| Statistics | 4 |
| Introduction to Probability | 4 |
| **Analyst grouping (outside Section 2): Logical Reasoning** | **4** |
| **Analyst grouping (outside Section 2): Quantitative Aptitude** | **12** |

These are *seed inventory frequencies*, not question likelihoods or assertions that absent official topics are absent from SOF papers.

**Question section provenance:** 28 seeded candidates map by printed paper position to Mathematical Reasoning, 19 to Everyday Mathematics, 8 to Achievers, 3 to Logical Reasoning and **8 organiser sample questions have section unresolved**. The combined chapter count, original exam section and proposed cognitive-demand classification are independent axes.

## Known boundary/cross-topic cases

- Attachment Q9: printed 2024–25 Set B Q44 is an **Everyday Mathematics** question with an **Algebraic Identities** microtopic. It is *not* Mathematical Reasoning or Achievers.
- Attachment Q65: printed 2025–26 Set A Q49 is in **Achievers** but the principal content is **Number Systems / surds**, not an academic topic called "Achievers".
- Attachment Q38(i), Q38(ii): separately numbered 2025–26 printed Q32/Q33; both require the pie chart, with distinct percentage/mark demands.
- Attachment Q2: *identity* vs *inverse* wording remains an unresolved source-text discrepancy. The provisional topic is rational operations, not an acceptance decision.
- Compound true/false questions (e.g., Q27, Q29, Q30, Q36 and Q65) currently have **one provisional primary subtopic** and may need secondary concept links once independently reviewed.
- Q48–Q61: most *Everyday Mathematics* applications are provisionally grouped under Section 3 Quantitative Aptitude. No claim is made that SOF explicitly lists `QUANT` as a Section 2 chapter.

## Reproducible checks

```sh
python TEST/imo-research/validate_seed.py
python TEST/imo-research/validate_math_audit.py
python TEST/imo-research/validate_taxonomy.py
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The taxonomy validator derives topic/section counts from the bank, checks exact question references and official syllabus/section separation, rejects silent omission, and **does not permit an accepted QRT cell, an academic acceptance or a Core-ready claim**. Current accepted QRT coverage is **0/28** even though all 66 questions have provisional topic mappings. Under #69, seven demands × four derived difficulty bands may only be populated after independent question-specific crux/score evidence.

## Remaining research gates

1. Verify each printed original source question, option order, diagrams and exact book page against scans, including the eight SOF sample candidates, without bulk reproducing unlicensed text.
2. Independently review mathematical answers, and retain source/answer/rights status per question.
3. Adjudicate multi-concept primary/secondary mappings and prerequisites, including the ambiguous source stem in Q2.
4. Separately derive the canonical QRT demand/band and then decide which reviewed source questions may enter a **SOF-compatible TEST intake adapter**. This mapping never enters NCERT-only #68 by changing the source-authority label.
