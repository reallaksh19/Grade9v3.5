# ISS51 validation

Status: **CANDIDATE_RENDERED_WITH_INHERITED_BLOCKER**. This is not golden, released or published.

- Frozen A/B/C SHA-256: PASS.
- Owner-bank custody check against generated intake: PASS.
- Package schema: PASS.
- Strict canonical render: PASS for Core1A + Core2 only.
- Core2 denominator/order: 10/10, source order preserved.
- Q8 changed-case worked anchor: PASS.
- Q8 staged difference-polynomial bridge: PASS.
- Q8 commit-before-compare question repair: PASS.
- Protected solution payload: PASS under the canonical inert-template-until-commitment contract.
- Learner quality report: **FAIL** with one finding only: `S2 PAGE-STAGE-SUPPORT core1a.html: stage support layout absent`.
- Shared-layout classification: **INHERITED_AUTHORITY_MISMATCH**. Pinned Core1A is `SINGLE_PANE` with 0.6/0.4 fractions; pinned renderer emits split columns only for `STAGE_SUPPORT`; shared PAGE-STAGE-SUPPORT still applies to Core1A. Candidate records do not control that layout.
- Dedicated tablet audit: PASS to completion on 1366×landscape, 1440×landscape, 854×portrait and 900×portrait for both requested pages. At every audited viewport: 0 small targets, 0 horizontal overflow, 0 wide elements, 0 hover-only handlers, 0 focus failures, 0 missing metadata units, 0 missing safe-search corpora, 0 gated disclosures open initially, 0 protected-search matches and 0 external requests.
- Core1A staged visuals: 4/4 SVGs accessible, 0 staged-SVG violations. Smallest measured figure text was 41.6 px at 1366 landscape and 25.7 px at 854 portrait.
- Core2 stage/support layout: measured true at all four tablet viewports. Core1A stage/support layout: measured false at all four viewports, matching the inherited authority mismatch above rather than a candidate-record delta.
- Learner PDF: **NOT_RUN**. HTML is the requested primary product; this run makes no PDF publication claim.
- Local clone deviation remains recorded: local DNS resolution failed, so the cold Linux render ran in GitHub Actions with the repository's canonical renderer.

Exact evidence:
- workflow run: `37337745550`
- source/artifact-producing commit: `ca4a85f4004cf3fac9a264a5ba1aa35b31a6c078`
- preserved artifact commit: `e0a84c17f0a646f529ba0ad145cacbecfcd3b1fd`
- render stamp: `render_core/2 98312239d6f159f6`
- Core1A SHA-256: `338e302a67c7b171e2b87b109f1dfc56b906d40052e0dbc1b2678112b83127c6`
- Core2 SHA-256: `dbcc5514238f7fc499b9be02ec696687d4b092ad1a26e7385e7b4e31cdd87341`
