# ISS66 U01B — matched stress-test structural decision-delta ledger

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Microtask:** U01B only — matched #49–#56 structural decision deltas  
**Basis branch:** `feat/iss66-blueprint-semantic-contracts`  
**Launch/base commit:** `2b11f2143cf9fd96be44014bab57d4f1f53bad37`  
**Protocol:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`

This ledger compares only structural authoring/review decisions that can inform shared blueprint/schema work. It does not adjudicate mathematical correctness, does not rewrite frozen candidate evidence, and does not convert author review into acceptance.

## Comparison fields

For each intended-band A/B pair, compare only:

1. actual derived band / primary-demand signal;
2. hardest-target selection;
3. author review / quality claim;
4. shared layout/blueprint finding;
5. post-render builder-capability proposal;
6. pair comparability limitation.

## D1 intended — #49 Set A vs #53 Set B

### #49 Set A

Evidence:
- issue comment `#5996700858`: actual classifications include Q1 D1/RETRIEVE, Q2 D1/RETRIEVE, Q3 D1/APPLY, Q4 D1/APPLY, Q5 D2/REPRESENT, Q6 D2/EXPLAIN, Q7 D2/MODEL, Q8 D1/APPLY;
- issue comment `#5998142157`: hardest target Q10 = **D2 / SYNTHESIZE / score 5**;
- issue comment `#5997156014`: strict quality remains non-green due inherited S2 `PAGE-STAGE-SUPPORT`; candidate-specific findings = 0; comment explicitly records Core1A `SINGLE_PANE` versus stage-support expectation;
- issue comment `#5998143846`: builder proposal is a **record-configured bounded-parameter probe**; no shared code changed.

Structural signal:
- intended D1 cohort resolves to mixed D1/D2;
- hardest target is not D1;
- author preserves inherited shared-layout contradiction instead of claiming full quality green;
- interaction proposal is parameter/state exploration, not a D1-specific schema conclusion.

### #53 Set B

Evidence:
- issue comment `#5995119195`: quality gate reported **0 findings / 0 continuity gaps**;
- same comment: hardest conceptual target **Q9**, score 5/conceptual 3; runner-up **Q10**, score 6, described as D3 linear synthesis;
- issue comment `#5995130355` and frozen builder file blob `48682de4439e8606678b42c308f8fa4573dcd96c`: builder proposal reports blueprint/CSS fraction desynchronization and proposes a topic-specific `POLYNOMIAL_COEFFICIENT_GRID` interaction;
- frozen candidate head: `bc464d831f4815a45dd45d29ecf6bcc16d5af8ab`.

Structural delta:
- hardest-target choice diverges (#49 Q10 vs #53 Q9);
- quality interpretation diverges (#49 explicit inherited non-green vs #53 zero findings);
- both runs surface layout-policy concerns, but they describe/fix them differently;
- builder interaction proposals do not converge on one capability.

## D2 intended — #50 Set A vs #54 Set B

### #50 Set A

Evidence:
- issue comment `#5998066723`: actual classification retained rather than forced:
  - Q3 = D1;
  - Q1/Q2/Q4/Q5/Q7/Q8/Q9 = D2;
  - Q6/Q10 = D3;
- same comment: hardest target **Q10 = JUSTIFY / D3 / score 7**;
- issue comment `#5998067503`: builder proposal **COORDINATE_PLOT_RESPONSE** in Core2 ATTEMPT;
- issue comment `#5998087573`: status remains CANDIDATE; independent exact-render/academic review outstanding.

### #54 Set B

Evidence:
- issue comment `#5994949247`: all ten items reported in D2 score range 3–4;
- same comment: hardest target **Q6 = JUSTIFY / D2 / score 4**;
- same comment: full YES across H1–H3, S1–S3, P1–P3, M1–M3;
- issue comment `#5994959975` and frozen builder file blob `f0dafb58d93a1947e3ef12610afc4aec921bc821`: builder proposal `<rational-domain-inspector>`;
- frozen head: `3d17905ebee4ac6cf39057ac05d49947b1b50430`.

Structural delta:
- strongest A/B classification divergence in the eight-run set;
- #50 derives D1–D3 from the same intended cohort while #54 keeps every item D2;
- hardest target diverges in both question and band (Q10/D3 vs Q6/D2), though both select JUSTIFY;
- interaction proposals are different learner-action classes;
- Set B self-review is materially stronger than Set A's acceptance posture and therefore cannot be treated as paired acceptance evidence.

## D3 intended — #51 Set A vs #55 Set B

### #51 Set A

Evidence:
- issue comment `#5998352246`: hardest target **Q8 / JUSTIFY / D4**;
- issue comment `#5998349546`: learner quality exposes one S2 `PAGE-STAGE-SUPPORT` finding;
- issue comment `#5998350457`: classifies it `INHERITED_AUTHORITY_MISMATCH` because Core1A blueprint says `SINGLE_PANE`, renderer splits only for `STAGE_SUPPORT`, while the quality rule still expects stage/support;
- issue comment `#5998351353`: proposal `BLUEPRINT_DRIVEN_LAYOUT_CONSISTENCY`.

### #55 Set B

Evidence:
- issue comment `#5996679120`: hardest target **Q8 / JUSTIFY / D3**, same difference-polynomial/root-bound crux family;
- same comment: static quality reported 0 content findings;
- frozen builder file blob `970131d8c6bf2dd9b4336b70caea162df3427c54`: primary finding is the same Core1A `SINGLE_PANE` versus `PAGE-STAGE-SUPPORT` mismatch; proposed fix makes browser/quality expectation conditional on actual blueprint layout;
- same builder file adds a secondary automatic PAGES asset-packaging proposal;
- frozen head: `91951abc430ff50ae526110488d9b12e27e30af5`.

Structural delta:
- strongest convergence in the eight-run set:
  - same question Q8;
  - same primary demand JUSTIFY;
  - same reasoning family;
  - independently reproduced same shared layout-authority mismatch;
- remaining semantic divergence is the derived band (D4 vs D3);
- #55's secondary asset-packaging proposal is single-run evidence, not matched convergence.

## D4 intended — #52 Set A vs #56 Set B

### #52 Set A

Evidence:
- issue comment `#5996826417`: U2 reports actual D2/D3/D4 bands; U3 selects hardest target **Q4 / SYNTHESIZE / D4**;
- same comment: candidate was still at U5 exact render/integration; no renderer/browser/PDF PASS claimed at that checkpoint;
- issue thread evidence available to U01B does not provide a completed U6/U7 semantic-review/builder checkpoint comparable to #56.

### #56 Set B

Evidence:
- issue comment `#5995062262`: hardest target **Q3 / JUSTIFY / D4 / score 9**;
- same comment: 10/10 PASS claimed for each H1–H3, S1–S3, P1–P3, M1–M3 family and zero W leakage;
- issue comment `#5995131372`: question ledger reports **7 D4 + 3 D3**;
- issue comment `#5995076172` and frozen builder file blob `a06f6f3d8c5f47fdb4c0c977cf0b9557c3470dc2`: proposal `CONTINUOUS_PARAMETER_SCRUBBER`;
- frozen audited head recorded for the Set B candidate: `40ca52786c0b5d0c400a5c730314a01689de836a`.

Structural delta:
- hardest-target choice and primary demand differ (Q4/SYNTHESIZE vs Q3/JUSTIFY);
- #56 does not force all items to D4;
- pair is **not symmetric enough** for semantic-review or builder convergence claims because #52's issue-thread execution evidence is incomplete at the comparable stages.

## Cross-pair observed deltas

These are observations only; U01C decides whether they justify a contract change.

| Structural decision | D1 pair | D2 pair | D3 pair | D4 pair |
| --- | --- | --- | --- | --- |
| Derived-band agreement | partial / mixed | **low** | differs on hardest item | partial; A incomplete |
| Primary-demand agreement on hardest target | no | yes (JUSTIFY), different question | **yes (JUSTIFY)** | no |
| Hardest-target agreement | no | no | **yes: Q8** | no |
| Shared layout issue reproduced | yes, but interpreted differently | not principal pair signal | **yes, independently** | not comparable |
| Strong self-review vs cautious/non-green posture | yes | **yes** | yes | B only comparable |
| Builder proposal convergence | no | no | **primary layout finding converges** | not comparable |

## U01B bounded findings

1. **Difficulty/demand/hardest-target decisions are not reproducible merely because intake and baseline are matched.** D2 is the clearest case.
2. **The Core1A layout-authority mismatch is the strongest independently reproduced platform finding.** It appears explicitly in #51 and #55 and is also present in the D1 evidence.
3. **Author review strength is not a comparable acceptance signal.** Some candidates report zero findings/full facet YES while matched runs preserve unresolved quality findings.
4. **Builder proposals are mostly non-convergent.** Parameter exploration recurs in #49/#56, but coordinate response, coefficient grid, rational-domain inspector and asset packaging are single-run or pair-specific signals.
5. **D4 cannot support symmetric A/B architectural inference at the same evidence depth** because #52 had not reached comparable semantic-review/builder evidence in the issue thread.

## What U01B does not decide

U01B does not decide:
- which fields should be added, removed or generalized;
- whether the existing PR #65 contracts already absorb the reproduced findings;
- whether author-review provenance/artifact binding is sufficient;
- whether primary-demand derivation needs a new canonical object;
- whether any interaction primitive passes the V3.2 worth gate.

Those decisions belong to U01C.

## U01B result

**COMPLETE as a microtask; no parent-unit progress credit.**

- P remains **0/10**.
- E remains **0/10**.
- Next microtask: **U01C — existing-field reuse + contradiction/negative-knowledge decision only**.
