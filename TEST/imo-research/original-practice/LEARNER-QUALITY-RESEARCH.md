# SOF IMO Grade 9 — seven original-practice learner-quality design proposals

**Research-only.** This is a continuation of merged PR [#291](https://github.com/reallaksh19/Grade9v3.5/pull/291), tracked in [issue #292](https://github.com/reallaksh19/Grade9v3.5/issues/292). The seven questions are AI-authored original practice, **not** copied SOF paper questions. Their previous question wording, answers, mathematical tests, original-source records, intake gates and accepted-QRT state remain untouched.

## What the evidence actually covers

`learner-quality-proposals.v1.json` cross-references every candidate ID to its historical quality-hold code, an existing diagnostic misconception code and the official **topic label** in the existing organizer-hosted SOF Class 9 syllabus registry. Per item it provides:

1. An analyst-identified wording/comprehension risk.
2. A draft optional scaffold that does not directly supply the answer.
3. A written description of how to read the notation aloud; **not** a screen-reader test result.
4. A proposed accessible input/response-collection specification.
5. A new error-specific feedback draft tied to one of the prior 18 deterministic misconception examples.
6. A Grade 9 scope risk, including explicit enrichment holds where appropriate.

These are **static research proposals**. No learner observation, usability study, screen-reader/keyboard browser execution, empirical readability score, independent grade-level curriculum approval, owner signoff or third-party originality/rights review occurred. A proposed spoken-math note is not an accessibility audit. The prior checker still cannot evaluate arbitrary proof prose, geometric reasoning or unrestricted algebraic responses.

## Specific questions and unresolved design decisions

| Candidate | Proposed SOF syllabus topic | Learner support and response work | Remaining decision |
| --- | --- | --- | --- |
| 001 | Number Systems | Explain the distinction between samples and proof; collect written justification separately from factor flags | No automated proof certification; manual reasoning rubric/response QA needed |
| 002 | Coordinate Geometry | Read signed x/y directions in order; label inputs and units explicitly | Test real screen-reader/keyboard handling of negative coordinates |
| 003 | Areas of Parallelograms and Triangles | Clarify that altitude is perpendicular to the *line* of the base, not a sloping edge | Test wording without requiring a diagram; review explanation feedback |
| 004 | Surface Areas and Volumes | Present a text-only unrolled side-wall model and exclude uncovered ends | Test accessible geometry wording and curved-only response scope |
| 005 | Linear Equations in Two Variables | Spell out the change-in-y/change-in-x step and how to read the equation aloud | Written algebra input and equivalent-expression feedback untested |
| 006 | Linear Equations in Two Variables | Identify booklet and poster-card price variables with units and two invoice checks | **Potential enrichment scope:** two simultaneous equations/elimination need separate Grade 9 curriculum judgement |
| 007 | Coordinate Geometry | Describe reflection then translation sequentially; allow area via base × height | **Potential enrichment scope:** two-step transformations and determinant explanation may exceed intended Grade 9 tier |

The official **topic** label does not prove every cognitive operation within a practice candidate appears in the official syllabus or is age-appropriate. Do not silently mark #006 or #007 Grade 9 syllabus-certified. The registry's own topic maps are research evidence, not academic QRT acceptance.

## Source and governance protection

- Anchors: original practice `#270`; six-gate intake `#274`; structured diagnostics `#279`; qualification overlay `#291`. Four exact Git blob hashes are pinned and re-read by `validate_learner_quality.py`. It also runs the upstream qualification validator, which checks the source seed, mathematical oracles, diagnostics, existing intake, dated waiver, and historic receipts.
- Owner waiver (2026-10-08): **independent human academic signature not required for this research workflow**. This is not proof of a human review, accessibility check, publishing rights or Core/QRT product authorization.
- QRT proposals are **not accepted**. Source rights for original SOF papers remain unreviewed. The new packet never copies official SOF stems/options/diagrams and never changes the original authored questions.
- No learner UI, production grader, Core, accepted-QRT ledger, product owner decision, or publication pipeline is modified.

## Qualification

From repository root:

```bash
python TEST/imo-research/validate_learner_quality.py
python -m unittest discover -s tests -p 'test_imo_learner_quality.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The dedicated **SOF IMO research seed integrity** workflow runs this validator and all `test_imo_*.py` adversarial tests on PR branches. An exact-head success qualifies *research-only metadata consistency*, not real learner accessibility or Grade 9 teaching efficacy.

**Acceptance remains:** 0/28 canonical QRT cells, 0/7 product-approved, 0/7 Core-ready, 0/7 learner-published. Next real product gate: assess these draft supports in an actual accessible TEST-only interaction, record observations, adjudicate candidate #006/#007 curriculum scope, and seek explicit dated product-owner approval before any learner admission.
