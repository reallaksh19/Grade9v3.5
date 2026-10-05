# Compatibility recovery checkpoint — 4 October 2026

The cumulative implementation and all eight review packs were committed at `46e91c9ec4285e14ca0db469eda281ff31df596a`. That checkpoint contains the executable production additions, corrected canonical inputs, HTML, SVGs, receipts, portable replay and 65-test logs. All 179 published file blobs were verified against the exact local manifest. The eight original PR heads remain unchanged.

## Additive Core2 compatibility correction

CI's friction reference-depth job rejected ten unchanged Physics questions because DIAGNOSTIC_REPAIR had been registered as EXPECTED. This was an introduced compatibility regression. The component is now OPTIONAL for legacy records. When a repair is authored, its real question, crux and construction target must still validate; semantic M1–M3 review remains mandatory. This is an opt-in authoring component, not a waiver of evidence or of the existing quality gates.

The replacement registry blob is `49ea62b11c8890257d31d66852d853928b8b0d75`, SHA256 `d141f40df8ef514f00aa6e521fed348203d7a5b4daac3ccaade19c7cf3e771da`. It was recovered through the GitHub connector and matched the already-tested local file exactly.

Before the execution connection failed, the local amendment passed 66 tests (59 existing plus 7 focused), a 35-record canonical Physics compatibility check, and all eight exact-byte replays of regenerated pages. These are recorded local observations. Their refreshed logs, receipts and generated pages have NOT been uploaded. Do not treat this commit as containing those 66-test receipts or the refreshed render evidence.

## Artifact custody and reproduction

The published HTML and ARTIFACT-MANIFEST.json remain the immutable **pre-compatibility snapshot at 46e91c9ec4285e14ca0db469eda281ff31df596a**. Reproduce them using that commit, not the current head's registry. Current-head replay of old stored page hashes is not a PASS claim. The revised registry changes render stamps, so all eight pages must be refreshed together with receipts and manifest before claiming head-matched replay.

`pending-compatibility-upload.json` records 63 pending file paths and their expected Git blob and SHA256 identities, plus the full 181-file expected local amendment. It is a recovery inventory, not proof that those objects were published. The source workspace returned `409 environment_offline: Environment is not connected` for both attempted read calls. No test or render was run after that failure.

## Remote CI observations at 46e91c9ec4285e14ca0db469eda281ff31df596a

- learner-platform-code-tests and v31-relay: success.
- friction-core-browser: failure in Reference-depth blueprint report, before browser execution. Introduced DIAGNOSTIC_REPAIR expectation corrected in this checkpoint; successful remote rerun still required.
- core1a-tablet-browser: failure on the existing Physics motion-in-a-plane fixture (phone overflow, control spacing, focus and zoom). Origin is unproven; it is not safe to dismiss it as inherited or claim it tests these eight chemistry candidates.
- guardrails: failure. Full unittest summary: 2289 run, 85 failures, 42 errors, 7 skipped. The diagnostic expectation appears in owner-bank failures; blueprint/projection/specification version drift is also visible. Broader failures include generated outputs, existing Mathematics/library contracts and runtime audits. Individual origins require exact baseline reproduction. Do not call the full suite green or absorb new failures into a baseline.
- canonical-assurance: observed in progress. Final outcome has not been certified.

No workflow, test tolerance, fixture deletion or baseline acceptance was changed to suppress these failures.

## Exact continuation

1. Restore the execution workspace and upload the identified compatibility amendment; verify every published blob against its manifest.
2. Reconcile generated blueprint projections/specification and version-sensitive integration tests with the authoritative registry, regenerate affected products honestly, and investigate all introduced CI regressions. Keep unrelated baseline defects separately evidenced.
3. Run real browsers on the exact eight chemistry artifacts, including initial/gated/repair/return states, geometry, focus, touch, overflow and zoom. Current candidate browser status is NOT_RUN.
4. Independently adjudicate all answers, warrants, checks, ancillary teaching tasks, sources, difficulty, hardest-target selection and twelve QRT facets. The 20 instantiated primary cells leave eight cells uncovered. No automatic YES or forced reclassification.
5. Regress through all D1–D4 again. Golden admission remains pending.

The original B→blueprint→A order remains D1 #32→#31, D2 #34→#33, D3 #36→#35, D4 #38→#37. No new benchmark issue, agent assignment, merge or learner release was made.
