# Issue #215 — Core → Atlas → standalone visual readiness join

This is the reviewer-facing evidence index for #210's final readiness join. It is not an academic source of truth.

## Material basis

- Programme parent: #210
- Integration issue: #215
- Delivery PR: #237
- Rebased current-main input: `9aa02e89050529dc2abb6312d5ba10fa94c9c5b4`
  - includes merged #233 correction
  - includes merged #234 correction
- Integrated validation head before this report-only refresh: `b0de9e9a5295ff71270365e708b43345e0e7b664`
- Guardrails run: `35959333031`
- V3.1 run: `35959333242`
- V3.1 planning basis: `reallaksh19/Common@29c3c123029c56307a92818a6fd3b9176240f7d7`

The final report commit is revalidated separately. The final closure claim is made only after PR #237 merges and the resulting current-main SHA receives the same exact-main verification.

## Canonical positive chain

| Hop | Canonical identity |
| --- | --- |
| Atlas selection | `MATRIX-PHY-KIN-2D-MOTION / R1` |
| Microtopic | `MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS` |
| Capability | `CAP-KIN-2D-INDEPENDENT-COMPONENTS` |
| Core1B | `physics:mic-phy-kin-2d-independent-components:core1b` |
| Representation | `REP-KIN-2D-SHARED-CLOCK` |
| Resource | `ACT-KIN-2D-SHARED-CLOCK` |
| Portable package | `portable-motion-shared-clock` |

Separate protected-decision witness:

`physics:q-phy-kin-2d-2b-projectile-validity-04:core2b`
→ source `Q-PHY-KIN-2D-2B-PROJECTILE-VALIDITY-04`
→ protected decision `R-KIN-TRANSFER-MODEL`.

Core2B is intentionally a separate transfer witness, not the rung's academic identity.

## Joined executable proof

`tests/readiness_join_215.test.mjs` is the real-browser cross-surface oracle.  
`tests/test_readiness_join_215.py` is the thin unittest adapter that makes that browser proof part of normal repository guardrail discovery.

The oracle directly observes:

1. keyboard selection of exact Motion R1 composite identity;
2. AtlasIndex 2.0 canonical microtopic/capability/representation/activity/Core/package identities;
3. downstream navigation using IDs captured at the Atlas boundary rather than title rediscovery;
4. Core1B reconstruction absent before attempt and visible after commitment;
5. separate Core2B protected decision absent before commitment and visible afterward;
6. same-time reconstruction → ACCEPT / revision 1 / simultaneous text;
7. mixed-time reconstruction → REJECT / revision 0 / “single physical state” text;
8. equal academically meaningful events across repository, external-host fixture and standalone host;
9. keyboard operation, visible active outline treatment and textual meaning;
10. direct `file://` standalone loading with zero runtime resource requests;
11. R999 fail-closed behavior with no enabled Core/visual/portable actions;
12. Mathematics R1 contrast: representation and canonical Core1A/Core1B study delivery are READY while activity/explorer/portable surfaces remain explicitly unavailable.

## Integrated P1–P5 matrix

Evidence at `b0de9e9a...`:

| Item | Status | Observation | Oracle | Failure origin |
| --- | --- | --- | --- | --- |
| P1 — AtlasIndex data | PASS | remote execution + source inspection | independent source-derived assertions | N/A |
| P2 — Atlas browser | PASS | remote real-browser execution | exact-ID keyboard/fail-closed browser oracle | N/A |
| P3 — Core | PASS | remote real-browser execution | attempt-before-reveal + protected-decision oracle | N/A |
| P4 — portable/offline | PASS | remote real-browser execution | cross-host semantic parity + direct-file offline check | N/A |
| #215 joined oracle | PASS | remote real-browser execution | cross-surface executable oracle | N/A |
| P5 — repository | PASS | exact-head remote execution | generated freshness + full discovery | N/A |

Exact provider result:

- V3.1: **PASS**
- generated architecture-manifest freshness: **PASS**
- #233 owner-extension test: **PASS**
- #234 FBD backlog test: **PASS**
- joined #215 Chrome/Node proof: **PASS**
- full unittest discovery: **1127 tests / 0 failures**
- final result: **OK**

## P5 debt disposition

### #232
Resolved on main by merged PR #235.

### #233
Resolved on main by merged PR #241. The Grade-9 owner-extension population is derived from canonical gates; circular dynamics remains explicitly `OWNER_EXTENSION`; negative curriculum-authority behavior remains intact.

### #234
Resolved on main by merged PR #242. Waiting FREE_BODY_DIAGRAM counts are derived from canonical representation/microtopic identities; renderer status remains `PROPOSED`; no renderer capability was invented.

## Generated artifact policy

`docs/architecture-manifest.json` remains builder-owned output.

For every material rebase the sequence is:

1. rebase meaningful source/test/report material;
2. render the workflow-generated artifact preview;
3. regenerate/reconcile the manifest from that exact tree;
4. run `build_manifest.py --check`;
5. never hand-select stale hashes from another branch.

The resolved-P5 #215 preview reports 247 components and 285 relations and includes both joined-proof tests plus the merged #233/#234 test state.

## Negative assurance

#215 did not:

- change canonical Physics truth;
- infer identity from titles, URLs, source order or proximity;
- relax Core reveal or protected-decision semantics;
- change Atlas production behavior;
- change portable academic behavior;
- promote a fixture to canonical coverage;
- infer mastery from interaction events;
- hide unavailable states;
- build or claim an FBD renderer;
- change curriculum authority;
- alter workflow or Relay files.

## Current consumer disposition

**PR-head disposition: P1–P5 PASS.**

PR #237 is therefore technically eligible for merge under the current #215 contract.

However, programme closure is not claimed from the unmerged branch. After merge:

1. identify the resulting exact current-main SHA;
2. read back main guardrails/V3.1;
3. require the joined browser proof and full discovery to pass on that same current-main basis;
4. publish the final #215/#210 closure evidence.

If any post-merge main result differs, the closure claim is withdrawn and the exact failing owner is reopened/routed.
