# SOF IMO Grade 9 — governed intake for seven newly authored practice candidates

This is an **unadmitted decision template**, not a learner question bank and not a source-paper license. It provides seven named slots corresponding to the **newly authored** research questions proposed separately in [PR #270](https://github.com/reallaksh19/Grade9v3.5/pull/270). That PR was **unmerged and awaiting its focused research integrity CI** when this template was created. A slot naming a candidate does not prove the candidate exists in merged `main` or that its proposed QRT cell has been accepted.

The user's instruction on 8 October 2026 makes **independent human academic approval not applicable** in this research workflow. Correct mathematical explanations, independent source-of-content checking, intellectual-property boundaries, learner clarity and product-owner decisions are nonetheless required. GitHub Actions is a mechanical test executor, **not** the product owner and not a source-rights licensing authority.

## Six gates before a learner-facing promotion

| Gate | Evidence required | Why it is separate |
|---|---|---|
| 1. Upstream research qualification | Candidate PR merged with immutable commit, its exact-head dedicated IMO mathematical tests succeeded | A draft or queued CI cannot become a production input |
| 2. Mathematical correctness | Per-question independent numerical/geometry oracles and solution consistency | A plausible answer is not sufficient for correctness |
| 3. Source independence | Confirm wording, options (if any), diagrams and scenario were newly written, not copied from copyrighted SOF exam material | Publicly viewable source papers do not license copied questions |
| 4. QRT decision | Evidence of primary cognitive demand, five-factor difficulty and **explicit product-level acceptance** into a named matrix cell | Research cell proposals do not fill any of the 28 canonical cells |
| 5. Learner quality | Age-appropriate language, accessibility, answer checking and misconception-specific feedback | A mathematically correct answer may still be poor teaching content |
| 6. Product-owner authorization | Explicit dated identity and decision for Core 2 or Core 1A delivery | Automated tests cannot approve live learner publication |

The seven slots enumerate **JUSTIFY-D3, REPRESENT-D1, JUSTIFY-D1, MODEL-D2, REPRESENT-D2, MODEL-D3, REPRESENT-D3** as anticipated research classifications, not admissions. A future separately reviewed PR should bind exact merged candidate content hashes/commit IDs, supply mathematical receipts, indicate which QRT cells are being admitted and specify the learner surface. Until then, every slot must report no QRT decision, no Core readiness and no publication.

The existing historical SOF source corpus of **66 original uploaded entries** stays unchanged. The full-paper **58/58** figure counts only attachment-selected, agent-worked positions; it is not a whole-paper question bank or publication permission. This intake document contains **no original SOF source stem, complete answer choices or figure images**.

## QA

```sh
python TEST/imo-research/validate_intake_contract.py
python -m unittest discover -s tests -p 'test_imo_intake_contract.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The validator crosschecks all seven expected IDs against original seed identity, six non-automatic evidence gates, future candidate merge status, no invented product-owner action, no source license, and no premature canonical QRT/Core promotion. The dedicated SOF IMO research workflow now includes the new validator and the 18 negative/positive tests. Passing this validator **only certifies the integrity of an unadmitted intake template**.

The user can later authorize admission of specific original questions once exact merged sources and content-quality evidence are available. The current contract explicitly preserves **0 accepted QRT cells, 0 product-approved candidates and 0 learner-published questions**.

Responsibility: [issue #271](https://github.com/reallaksh19/Grade9v3.5/issues/271).
