# SOF IMO Grade 9 — Batch A / Number Systems concept review

**Programme:** [#294](https://github.com/reallaksh19/Grade9v3.5/issues/294) · **Baseline:** `main@7ee763c2db61f228d8064cdaea8bc4bb47ab529e` · **Scope:** 8 of the existing **68** distinct authentic-source positions. The seven authored-practice candidates are separate. The ten known discrepancy cases covering eleven positions remain a programme-wide denominator; **three** of those cases occur in this batch.

**Review kind:** research-only source-to-capability engineering, with the prior B01/B02/B04 and sample mathematical work reused. This is not an independent academic sign-off, official key acceptance, QRT acceptance, publisher licence, canonical Core1A/Core2 product, or released learner HTML/PDF.

The machine-readable [eight-position source/capability crosswalk](batch-a-number-systems-capabilities.v1.json) records each printed source ID, page/position, source-host category, previous math audit, evidence-derived answer, specific source dispute, proposed conceptual decision, mathematical warrant, predicted wrong path, teaching connection and custody/product hold. It contains **no verbatim SOF question stems, option sets, figure assets, or original publisher PDF bytes**.

## All eight positions — no unaccounted question

| Original source identity | Printed PDF page (1-based) | Existing evidence; agent-selected choice | Primary mathematical decision / conceptual crux | Disposition |
|---|---:|---|---|---|
| 2023–24 A Q18 | 4 | B01-002; `-5/12` (source choice C) | Compute a compound rational expression, then negate; do not carry the compilation's reordered choice A | **HOLD** conflict 003 (option order) |
| 2025–26 A Q28 | 5 | B01-006; literal identity `0` (source choice B) | Decide whether the task asks for additive **identity** or **inverse**; these are different mathematical operations | **HOLD** conflict 006 (meaning-changing stem) |
| 2024–25 B Q33 | 6 | B02-014; `5/8` (source choice A) | Define linked numerator/denominator variables, apply modifications to the right quantities, solve and reverse-check | **HOLD** source custody and rights |
| 2024–25 B Q26 | 5 | B02-010; `x=2` (source choice C) | Rewrite unlike-looking exponential terms in a common base and recognize the one-factor relationship | **HOLD** custody/rights; high-value authored teaching candidate |
| 2025–26 A Q35 | 5 | B01-013; `18` (source choice B) | Evaluate nested fractional/negative indices with precise parentheses, roots and reciprocals | **HOLD** full notation custody/rights; high-value authored teaching candidate |
| 2025–26 A Q36 | 6 | B04-001; `105 rows` (source choice B) | Restore lost members of a square array before taking a positive square root | **HOLD** custody and rights |
| 2025–26 A Q49 | 7 | B01-016; `F,F,F` (source choice A) | Check each surd/polynomial assertion independently; use exact falsification rather than radical-looking plausibility | **HOLD** custody/rights; high-value authored teaching candidate |
| 2026–27 organizer sample Q9 | 2 | Sample math/QRT pilot; Statement II `3/80`, answer D | Preserve nested radical/power scope and evaluate separate truth claims; owner notation was rewritten | **HOLD** conflict 010 (notation); sample key sighted, not accepted academic review |

**Paper-boundary evidence:** 2023–24 A, 2024–25 B and 2025–26 A URLs are *school-hosted SOF-branded scans*, **not organizer-hosted sources**. The 2026–27 sample is linked from the SOF organizer. The PDF byte-access result from [PR #304](https://github.com/reallaksh19/Grade9v3.5/pull/304) is a **temporary GitHub-runner verification of four downloads, not durable repository custody**. No source element has been promoted to a ready Core2.

## Mathematical reasoning reuse and new academic synthesis

- **Q18 vs Q28 must not share an undifferentiated “rational operations” repair:** Q18's learner decision is *execute then negate* and its discrepancy is **option order**; Q28's decision is *which operation does the printed noun authorize?* and its discrepancy is **semantic wording**. The original Q28 wording cannot be silently rewritten. Existing B01 source calculations and discrepancy case records remain unchanged.
- **Q26 vs Q35 vs sample Q9 do not automatically use one teaching module:** Q26's bottleneck is relational substitution between powers, Q35's is evaluation of compound exponent syntax, and sample Q9's is faithful interpretation of nested radicals/powers in two truth-value tests. They share an index/root representation bridge, not the exact decisive inference.
- **Q49 and sample Q9 both demand truth-value decisions but test different mathematical content.** A general “check every assertion” strategy is reusable, but their radical and index validity arguments, example boundaries and source-notation holds must be distinct.
- **Q33 and Q36 are modelling inversions with different learner decisions:** linked numerator/denominator constraints versus restoring the full cardinality of a square array. Chapter similarity is not a teaching-dependency link.

**Authoring priority, not acceptance or QRT difficulty:** Investigate Q26, Q35 and Q49 first for distinct conceptual teaching constructions. Their predicted errors and transfer boundaries are captured in the crosswalk. Q28 and sample Q9 require early editorial/notation reconciliation before using the source itself in a learner task. The remaining items receive appropriate repair connections only if a learner decision requires them; **eight source positions does not imply eight Core1A modules**.

Two *separately authored* diagnostic proposals are in the JSON: a fresh exponential factoring/equation pair and a falsifiable irrational-sum claim. These are **not original SOF positions, source Core2, or the seven already-inventoried authored practice questions**. No synthetic task is counted as an authentic Core2 release.

## Product and evidence disposition

For each of the eight positions: mathematical audit evidence is **REUSED_AGENT_WORK** (not independently accepted), custody is **INCOMPLETE**, copyright/reproduction rights are **NOT_REVIEWED**, QRT is **UNACCEPTED**, and source Core2 product eligibility is **FALSE**. All eight have explicit HOLD reasons; none has a learner rendering or protected question presentation. 2026–27 sample Q9 retains its existing proposed `QRT-JUSTIFY-D3` research classification only; the others receive no invented cell.

The authored divisibility construction at `TEST/library/imo-g9-divisibility-core1a.v1.json` is a legitimate **separate TEST Core1A renderer candidate**; none of the eight reviewed source cruxes establishes a divisibility-over-consecutive-integers alignment. **Authentic-source teaching coverage therefore remains zero for this candidate**, regardless of #304 browser success.

## Bounded next work and tests

1. On the [QA PR #304](https://github.com/reallaksh19/Grade9v3.5/pull/304) track, finish actual browser/print exact-head evidence before merging that separate responsibility.
2. Obtain private, permitted retained PDF source custody with observed digests and precise item-component readback, preserving source-host and rights status. Source reference links remain available; no source replication before rights clearance.
3. Build original Core1A mathematical constructions for one or two selected cruxes, linked to the checked source reasoning only where justified. Render through the existing canonical engine and inspect actual learner tasks.
4. After review, advance Batch B and onward without modifying the 68-source denominator, original seed, ten conflicts or seven authored-practice provenance.

Focused validation for this PR: `python -m unittest tests/test_imo_batch_a_capabilities.py -v` or `python -m unittest discover -s tests -p 'test_imo_*.py' -v`. The new test checks all eight unique source references against the 68-position upstream census, joins old paper/math evidence, replays small independent arithmetic oracles, preserves the three relevant discrepancy cases, and fails closed on Core/rights/QRT promotion. Status **NOT_RUN** until the exact branch test has actually executed.

**Owner review requests:** mathematical crux quality; appropriate Grade 9 index-law depth; a defensible source/editorial disposition for Q28 and sample Q9; publisher licensing/external-reference rules; any subsequent canonical Core1A/Core2 admission. No decision is inferred here.
