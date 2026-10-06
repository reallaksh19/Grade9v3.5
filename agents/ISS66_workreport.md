# ISS66 work report — blueprint/schema semantic-contract hardening

## Responsibility

- Issue: #66
- Parent/product context: #29
- Protocol: `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`
- Topology: `SINGLE_RESPONSIBILITY`
- Launch integration head: `2b11f2143cf9fd96be44014bab57d4f1f53bad37`
- Implementation branch: `feat/iss66-blueprint-semantic-contracts`
- Denominator: 10 declared units
- Current state after U04: P40% / E40% (4/10 complete and successor-safe evidenced)

## Chronology

### A1 — implementation start

Issue #66 published `PLAN_UPDATE — implementation-start`. No progress was awarded. The implementation branch was created from the exact observed integration head.

### U01 — authority / decision graph — COMPLETE + EVIDENCED

Evidence:
- `evidence/blueprint-schema/ISS66/u01-authority-decision-graph.md`
- exact stress candidate heads and ledger/QRT blob identities are recorded there;
- exact active shared authority blob identities are recorded there.

Findings:
1. PR #65 already repaired the reproduced Core1A layout-authority contradiction; U02 should verify first and return `NO_CHANGE` if no contradiction remains.
2. QRT review already distinguishes `AUTHOR_ONLY` from `RENDERED` and binds rendered review to exact artifact bytes/head, but it does not encode reviewer independence.
3. `scene_instance` already carries question/microtopic, datum, asset and Core-role binding; do not create a duplicate representation system without a failing replay.
4. `core2_support_plan` already connects protected reasoning moves to support rows and visual stages; do not create a duplicate deferment mechanism.
5. Difficulty/QRT selection remains directly driven by authored `difficulty.band` and cognitive-demand labels despite five-component evidence existing in the schema.
6. Matched #49–#56 runs show substantial classification variance. Across D1–D4 pairs, only 5/10, 6/10, 2/10 and 2/10 questions respectively share the same band+demand cell.
7. Canonical diagnostic authoring remains weaker than the M2 semantic objective: wrong idea + prompt + repair exists, but discriminating response evidence and confirmed/indeterminate state are not first-class.

Negative knowledge:
- no second layout authority;
- no duplicate scene-instance schema;
- no duplicate protected-support mechanism;
- no topic-specific widget schema from one candidate proposal;
- no claim that schemas alone determine academically correct classification.

### U02 — presentation authority — COMPLETE + EVIDENCED

Evidence:
- `evidence/blueprint-schema/ISS66/u02-presentation-authority.md`
- draft PR #67;
- candidate workflow `learner-platform-code-tests` run `37420067363`.

Change:
- retained legacy `PAGE-STAGE-SUPPORT` rule id and `stage_support_layout` observation key for v1 compatibility;
- corrected the quality/schema contract wording so that the field means “matches the selected blueprint responsive policy”;
- added a regression preventing restoration of the universal 0.68/0.32 Core1A claim.

Validation:
- candidate `code-tests`: SUCCESS;
- existing blueprint layout observation regressions: SUCCESS;
- blueprint-v2 render snapshots: SUCCESS;
- the separate Core2 browser lane still fails before browser audit because the Motion-in-2D render has two gaps; the exact integration-basis lane fails the same step with the same two-gap/exit-2 result, so U02 does not relabel it as a candidate regression;
- historical merged-head Core1A browser evidence reaches the layout audit successfully and fails instead on the separately recorded 7px phone/200%-zoom overflow.

Decision:
- no new layout field or second authority was added;
- the legacy observation field is a compatibility alias over blueprint-aware measurement.

### U03 — review provenance & artifact binding — COMPLETE + EVIDENCED

Evidence:
- `evidence/blueprint-schema/ISS66/u03-review-provenance.md`
- code head `75ba8a45a009a0205d1d65363301ed6538e9d014`
- qrt-pipeline-hardening run `37420573268`: SUCCESS
- learner-platform-code-tests run `37420573263`: code-tests + blueprint snapshot jobs SUCCESS

Change:
- extended semantic review basis with `INDEPENDENT_RENDERED`;
- independent rendered review requires a declared `reviewer_ref`;
- added optional run-level `review_requirements.independent_rendered_review_required`;
- legacy/missing-basis rendered reviews remain valid ordinary exact-artifact reviews;
- opt-in independent requirement is enforced by the existing QRT guard without becoming a universal publication gate.

Regressions prove:
- rendered self-review remains evidence but does not satisfy the opt-in independent requirement;
- independent rendered review satisfies it only with reviewer identity;
- artifact digest binding remains mandatory after the stronger provenance claim.

### U04 — difficulty/QRT derivation — COMPLETE + EVIDENCED

Evidence:
- `evidence/blueprint-schema/ISS66/u04-difficulty-qrt-derivation.md`
- code head `813fbea92f0ebd6f2c4c6e089a2ae90ffc5f2e70`
- qrt-pipeline-hardening run `37421354520`: SUCCESS
- pass1-question-bank-contract run `37421354534`: SUCCESS

Change:
- centralized score→band derivation in `Shared/tools/question_difficulty.py`, sourced from the existing learner-question metadata vocabulary;
- QRT resolution now verifies component sum, stored score and stored band before selecting a cell;
- package/exam schemas distinguish optional planning `requested_band` from derived `band`;
- QRT resolution records requested band, derived score and a digest of the difficulty-range authority;
- competitive exam validation reuses the same derivation instead of a second hard-coded map.

Boundary:
- primary cognitive demand remains a semantic academic classification with a written basis; software does not fabricate it from score/components.

## Next substantial unit

**U05 — Protected act & support eligibility.** Reuse the existing core2_support_plan/reasoning-move mechanism, then determine the smallest shared learner-owned decision identity/state vocabulary needed to make hint/visual/solution eligibility coherent without a duplicate support system.
