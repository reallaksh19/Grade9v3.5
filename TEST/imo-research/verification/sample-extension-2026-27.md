# SOF IMO 2026–27 Class 9 sample: previously missing Q1 and Q3

**Research source:** [organizer-hosted original PDF](https://sofworld.org/download/file/fid/73719), page 1 (physical PDF index 0); printed answer-key panel, page 2 (index 1). The SOF sample contains 10 questions. The Owner's attached compilation and original provisional 66-position source index included eight, omitting sample Q1 and Q3.

The supplemental ledger `official-sample-2026-27-new-positions.v1.json` records **two NEW discovery source positions** with stable sample IDs; it does **not** modify or renumber the original 66 supplied/compiled positions. Consequently, sample source census becomes **8 originally supplied + 2 newly discovered = 10/10 positions**, while the attached compilation still has **66 original candidate positions**. This does not imply full exam paper coverage, since this document is a sample with 10 questions rather than a 50-question Level 1 paper.

## Two independently reasoned sample answers

| Original sample question | Visual reasoning | SOF printed key | Status |
|---|---|---|---|
| Q1 — three cube views | From first and third shown views, opposite-face relationships determine that the unknown front in the second view is **4**. The checker verifies the three visible top/front/right orientations using a consistent right-handed cube representation. | B | Agent-solved, needs academic second reviewer and figure-rights review |
| Q3 — quadrant circular number pattern | In each quadrant the inner number is the square of the mean of its two immediately adjacent outer labels. Known values reproduce **121, 81, 64**; missing lower-right is **49**. | B | Agent-solved, needs academic second reviewer and figure-rights review |

These short explanations are researcher-generated. The original source question text, original multiple-choice text and diagram images are **not copied into the repository**. The original PDF controls what labels/positions are actually present, and a printed option label is not itself a proof of the result.

Both new questions are in the sample's **Logical Reasoning** section and provisionally assigned reasoning subtopics; these proposed academic microconcept identifiers are not automatically admitted into the earlier 49-subtopic taxonomy, which maps the **original 66 only**.

## Verify / next gates

```sh
python TEST/imo-research/validate_sample_extension.py
python -m unittest discover -s tests -p 'test_imo_sample_extension.py' -v
```

The integrity script validates the existing 66-question seed, the eight prior organizer sample sightings, two new source IDs, the 10/10 total, mathematically derived 4/49 results, negative rights and academic-acceptance assertions. The existing focused IMO workflow's `test_imo_*.py` discovery includes these tests on the PR head.

**Not done:** official PDF byte digest, independently signed academic answer check, figure transcriptions/permission, original-paper answer validation beyond current audits, accepted QRT cell, Core 2/Core 1A selection, or full 50-question paper coverage. The currently separate [sample-QRT pilot #238](https://github.com/reallaksh19/Grade9v3.5/pull/238) still owns Q5 diagram and Q9 notation holds; this independent source-expansion slice does not overrule that responsibility.
