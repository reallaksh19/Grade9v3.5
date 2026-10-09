# Seven original practice questions — reconciled qualification evidence

**Status: research-only / no Core, QRT, learner or licensing promotion.** This is a
current-state **overlay**, not an edit to the historical intake snapshot
`original-practice-intake-contract.v1.json`. That snapshot intentionally says
PR #270 had not yet been verified as merged at its creation time. Do not
retroactively change that field or its existing validator/tests.

## Exact historical lineage

| Merged PR | Exact tested PR head | Dedicated SOF IMO focused run | Merge commit | Research scope |
| --- | --- | --- | --- | --- |
| [#270](https://github.com/reallaksh19/Grade9v3.5/pull/270) | `bbdbee6c9b056f9843f877a22386468be3d96e5d` | [37773725447](https://github.com/reallaksh19/Grade9v3.5/actions/runs/37773725447) — SUCCESS | `1caa71fc3deda2fbff70bed40f0a092a13457bff` | Seven AI-authored candidate questions and mathematical oracles |
| [#274](https://github.com/reallaksh19/Grade9v3.5/pull/274) | `43fff921627df50f80516d00be253289975b7a47` | [37776239987](https://github.com/reallaksh19/Grade9v3.5/actions/runs/37776239987) — SUCCESS | `041817515a5b6c7b0fd3bf54ccd12ef203977c60` | Six non-automatic product intake gates |
| [#279](https://github.com/reallaksh19/Grade9v3.5/pull/279) | `0899532e330a6e3732d9b2ed07283ff234918185` | [37777242871](https://github.com/reallaksh19/Grade9v3.5/actions/runs/37777242871) — SUCCESS | `c98122f2c676675590593b926e7e5b18f42a86e8` | Seven structured checking packets, 14 passing examples, 18 misconception probes |

These are GitHub workflow observations for the **prior exact PR heads**, not the
CI result of this qualification PR. Other broad workflows failed on those heads;
do not report them as green. The new PR must pass the same dedicated workflow
**at its own exact head**.

`original-practice-qualification-evidence.v1.json` pins the Git blob SHA of
each of the four already merged inputs: authored questions, structured
diagnostics, intake snapshot, and dated owner waiver. Its validator checks
against bytes, not mutable PR branch names or inferred metadata. It also invokes
the existing source seed, math, diagnostics, and intake validators.

## Item-level research position

| Candidate | Provisional cell | Existing negative misconception examples | Outstanding product-quality hold |
| --- | --- | ---: | --- |
| 001 | JUSTIFY-D3 | 2 | Structured proof certificate cannot validate a student's actual prose reasoning |
| 002 | REPRESENT-D1 | 3 | Signed axes, direction and unit accessibility need a learner-interface check |
| 003 | JUSTIFY-D1 | 3 | Perpendicular altitude interpretation and equal-area explanation need clarity review |
| 004 | MODEL-D2 | 2 | Learners must distinguish curved side from uncovered circular ends |
| 005 | REPRESENT-D2 | 3 | Equation input, inverse solving and actual written-working feedback remain untested |
| 006 | MODEL-D3 | 2 | Item units, variable meanings and feedback for swapped prices need review |
| 007 | REPRESENT-D3 | 3 | Transformation order, labelled vertices and determinant sign need accessible explanations |

The existing validator checks mathematical invariants and the *modelled*
structured responses. It does **not** assess arbitrary human mathematical proof,
live learner accessibility, language comprehension, original prior-art
uniqueness, or pedagogy. The open actions are review proposals, **not completed
learner tests**. The owner has waived mandatory independent human **academic**
signoff for research (8 October 2026); no independent expert approval is claimed,
and rights/source custody remain separate.

## Required next decisions

For each question, review source independence, learner language/accessibility,
Grade 9 curriculum fit, live response collection/feedback, and QRT scoring.
Then seek a separately identifiable, dated **product-owner** decision per
accepted QRT cell and Core delivery. Until then: **0/28 accepted QRT cells;
0/7 Core ready; 0/7 learner published**. Never copy the unlicensed original SOF
stems, option sets, or figures into a learner surface.

## Reproduce (repository root)

```bash
python TEST/imo-research/validate_qualification_evidence.py
python -m unittest discover -s tests -p 'test_imo_qualification_evidence.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The focused `SOF IMO research seed integrity` workflow calls the new
qualification validator and all `test_imo_*.py` falsifiers on its exact PR head.
A passing result is **research integrity**, not automatic QRT/Core admission.
