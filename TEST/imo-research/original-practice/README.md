# SOF IMO Grade 9 study skills — seven newly authored practice candidates

This is a **research-only, source-independent practice pilot**. The seven question scenarios, free-response prompts, expected answers, worked derivations and counterchecks in `seven-cell-original-problems.v1.json` were freshly composed for this project. They are **not SOF original printed examination questions**, not paraphrased reproductions of their stems or option sets, and carry no original source diagrams. The pilot does not claim universal prior-art uniqueness or grant publishing rights to any third-party source.

The owner-designated research standard permits agent mathematical checking **without independent human academic signoff**; it does not turn an unsupported result into fact. The repository validator recomputes each of the seven answers from arithmetic or coordinate invariants. Source reuse permissions for the previously audited SOF papers remain separate and unchanged.

## Original practice inventory

| New ID | Original Grade 9 practice concept | Answer and check | Provisional historical 4×7 QRT cell |
| --- | --- | --- | --- |
| 001 | Prove universal divisibility of three successive integers | Consecutive factors supply 2 and 3; verify all six residue classes | JUSTIFY-D3 |
| 002 | Translate a west/north map instruction into ordered coordinates | (-4, 3); reverse-read both directions | REPRESENT-D1 |
| 003 | Explain why two triangles with equal base and altitude have equal area | 42 cm² each; determinant check using different apex coordinates | JUSTIFY-D1 |
| 004 | Choose curved cylinder surface, excluding uncovered circular ends | 880 cm²; unroll to a 44×20 rectangle | MODEL-D2 |
| 005 | Translate a four-row decreasing table to a linear equation and invert | y=-2x+5; x=7; check four pairs and target | REPRESENT-D2 |
| 006 | Model two distinct print-shop invoices by simultaneous equations | 112 rupees; independently recompute both invoices | MODEL-D3 |
| 007 | Reflect three vertices in the y-axis and translate; test area invariant | (6,-1),(1,-1),(4,2); signed determinant reverses but absolute area 7.5 | REPRESENT-D3 |

These are **seven distinct provisional 4×7 QRT cells**, deliberately aligned with the seven historical research-cell categories already observed in the 2026–27 official sample. The original questions themselves do not reuse the SOF dice, quadrant puzzle, parallel-line diagram, stems or options. Their Grade 9 content is created from general educational mathematics (divisibility, coordinate geometry, triangles, surface area, linear relations and simultaneous equations).

A learner may benefit from these tasks after standard quality and product review. However, this PR **does not** populate the canonical QRT matrix, turn them into Core 2/Core 1A learner pages, or claim live learner publication.

## Evidence and controls

- Each question is a new free-response task with its own scenario, complete original prompt, expected result, reasoned working, alternate/reverse test, one important student mistake to diagnose, and protected cognitive action.
- Each tentative QRT classification has a primary demand, optional secondary demands, **five explicit score components** and a score/band/cell derived from the [historical demand matrix](../../../../Shared/quality/question-demand-matrix.v1.json). A research-cell proposal is not an accepted Matrix slot.
- `validate_original_practice.py` uses independent arithmetic checks, including all residue classes modulo 6; two determinant triangle areas; curved cylinder/unrolled rectangle; four linear table rows; both invoice constraints; and signed/absolute triangle area invariance under reflection and translation.
- No third-party source stems, complete choice lists, figures or paper bytes are copied. The original owner 66-item source seed, 58 AI-worked fullpaper subset and 10 organizer sample source-position census are untouched.
- Authorship is transparently marked **AI-generated**. No independent human reviewer is required by the owner's current policy and none is falsely claimed. Neither a publisher reuse license nor an exclusive originality guarantee has been established.
- **0/28 accepted QRT cells** in the original-source acceptance ledger; **zero Core-ready or learner-published items** in this new practice pilot. Admission and learner publication, if desired, require an explicit separate product-level decision.

## Qualification commands

```sh
python TEST/imo-research/validate_original_practice.py
python -m unittest discover -s tests -p 'test_imo_original_practice.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The dedicated `SOF IMO research seed integrity` workflow runs the practice validator and all `test_imo_*.py` regressions on the PR head. It rejects answer tampering, incorrect score bands, source-ID misattribution, unlicensed SOF content, false rights approvals, unsupported human signoffs or QRT/Core promotion.

**Dependency note:** original-practice research is intentionally independent of the still-open owner-waiver/sample-QRT proposal [PR #266](https://github.com/reallaksh19/Grade9v3.5/pull/266). Its own CI run was queued at this branch's creation, so no #266 merge is presumed.

Responsibility: [issue #267](https://github.com/reallaksh19/Grade9v3.5/issues/267).
