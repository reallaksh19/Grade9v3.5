# ISS66 U02 — presentation authority

**Status:** COMPLETE + EVIDENCED  
**Disposition:** minimal compatibility correction; no new layout mechanism  
**PR:** #67  
**Basis before U02:** `feat/issue29-integrated-core-templates@2b11f2143cf9fd96be44014bab57d4f1f53bad37`

## Finding

PR #65 already fixed the functional layout contradiction:

- active `BP-CORE1A-CONSTRUCTION@1.7.0` declares `responsive_policy.expanded = SINGLE_PANE`;
- `layout-observation.mjs` makes a measured one-column Core1A satisfy that selected policy;
- retained `STAGE_SUPPORT` policies still use the legacy split-column measurement;
- `tests/test_blueprint_layout.mjs` covers single-pane success, accidental two-column failure, empty-page failure, and retained stage/support behavior.

One residual shared-contract defect remained: `Shared/quality/learner-quality.v1.json` still described `PAGE-STAGE-SUPPORT` as “Expanded tablets use the 0.68/0.32 stage-support layout” for roles including Core1A. The runtime flag was already blueprint-aware, so the prose no longer described what the check actually meant.

## Change

Compatibility was preferred over a field/rule-id migration.

Retained unchanged:
- rule id `PAGE-STAGE-SUPPORT`;
- observation key `stage_support_layout`;
- existing historical observations/receipts;
- runtime layout selection and measurement behavior.

Changed:
1. `Shared/quality/learner-quality.v1.json`
   - normative rule text now says the rendered expanded layout must match the **selected blueprint responsive policy**;
   - explicitly names `SINGLE_PANE` and `STAGE_SUPPORT` semantics.
2. `Shared/quality/learner-observation.schema.json`
   - documents `stage_support_layout` as a **legacy v1 field name** retained for compatibility;
   - defines true as matching the selected blueprint policy, not necessarily having split columns.
3. `Shared/tools/quality_gate.py`
   - documentation now calls this a selected-blueprint layout measurement.
4. `tests/test_quality_contract.py`
   - regression locks the legacy id/key while requiring blueprint-driven wording and rejecting the old 0.68/0.32 universal statement.

## Why no new field

Adding `blueprint_layout_matches` would require migration of historical observations and downstream consumers while conveying no new runtime fact: PR #65 already reconciles `stageSupportLayout` through `matchesBlueprintLayout(policy, ...)`.

The legacy key is therefore treated as a compatibility alias. This removes the authority contradiction with less recurring ceremony.

## Validation

### Candidate PR #67 / head `29c8b064bb18c5e14d5aeda93783699ac2424707`

Hosted workflow `learner-platform-code-tests` run **37420067363**:

- job `code-tests`: **SUCCESS**;
- step `Informational platform code tests`: **SUCCESS** — includes the new Python contract regression;
- step `Existing blueprint layout observation regressions`: **SUCCESS**;
- job `blueprint-v2-render-snapshots`: **SUCCESS**.

The same workflow's `core2-v2-browser-audit` remains red at `Render real Motion-in-2D product` because the render reports **2 gaps**. This is not introduced by U02:

- integration-basis run **37350305125**, job **111899189071** fails the same step with `2 gap(s): nothing written`, exit 2;
- candidate run **37420067363**, job **112127220720** fails the same step with the same `2 gap(s): nothing written`, exit 2.

No browser PASS is claimed from that inherited failing lane.

### Prior merged-head browser evidence

Integration workflow `core1a-tablet-browser` run **37350305172** reached the exact Core1A audit and reported:

- `BP-CORE1A-CONSTRUCTION@1.7.0`;
- `stage68=true` after blueprint-aware reconciliation;
- no layout mismatch finding;
- failure was instead the already-recorded **phone 200% zoom overflow=7px**.

Thus the observed layout-authority defect is repaired while the unrelated overflow remains honestly open.

## U02 acceptance

- selected blueprint is the functional layout authority: **YES**;
- retained STAGE_SUPPORT behavior still tested: **YES**;
- no generic 0.68/0.32 assertion remains as normative Core1A policy: **YES**;
- compatibility with legacy rule id / observation key retained: **YES**;
- new universal gate introduced: **NO**.

U02 is complete and evidenced. Next unit: **U03 — review provenance & artifact binding**.
