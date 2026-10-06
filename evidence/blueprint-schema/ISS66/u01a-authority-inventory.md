# ISS66 U01A — exact authority inventory

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Microtask:** U01A only — live authority inventory  
**Basis branch:** `feat/iss66-blueprint-semantic-contracts`  
**Launch/base commit:** `2b11f2143cf9fd96be44014bab57d4f1f53bad37`  
**Protocol:** `reallaksh19/Common@e6b3eaf9c2d070bb97f362fc42288612c86753ef:skills/engineering-pr-delivery-v3.2`

This record inventories current shared authority before proposing any schema change. It does not accept the stress-test products and does not claim academic correctness.

## Authority map

| Layer | Current authority | Blob SHA / version | U01A observation |
| --- | --- | --- | --- |
| Blueprint registry | `Shared/web/interactive-page-blueprints.v1.json` | blob `592bffeb87ce283d62ea2479fa359a5278f4ee08`; registry `1.14.0` | Active Core1A is `BP-CORE1A-CONSTRUCTION@1.7.0`; active Core2 is `BP-CORE2-SOURCE-QUESTION@1.9.0`. |
| Blueprint schema | `Shared/web/interactive-page-blueprint.schema.json` | `a306b926a6ea39db6090b0121b6c612246f3aa9b` | Registry/blueprint structure is schema-controlled; responsive and interaction policies are blueprint fields. |
| Blueprint contract resolver | `Shared/tools/web_blueprint_contract.py` | `96b15ae6fb68ff71a56d3696e1f53edef6a3fc25` | Validates responsive fractions and registry constraints. |
| Core1A/Core2 browser audit | `tools/site-audit/core-page-audit.mjs` | `3ce84c73841c8a75fa1e3302fa2bde15c84fd029` | Consumes selected blueprint policy, but retains a separate split-layout expectation path described below. |
| Layout policy helper | `tools/site-audit/layout-observation.mjs` | `cffd543b2120d5d977e6c8ec5b26ee10a90c4584` | Correctly treats `expanded: SINGLE_PANE` as one-column policy. |
| Learner quality rules | `Shared/quality/learner-quality.v1.json` | `e808367a0c97633e6a89f4fd22493b7ae790be05` | Contains Core1A representation/depth rules; must remain distinct from blueprint layout authority. |
| QRT run schema | `Shared/quality/qrt-pipeline-run.schema.json` | `a4c25153ca5fa53a67b17565b15076215ebd7c9a` | Already types review basis as `AUTHOR_ONLY`, `RENDERED`, or `INDEPENDENT_RENDERED`; rendered artifacts require id/path/SHA/head. |
| QRT guard | `Shared/tools/qrt_pipeline_guard.py` | `a3cac884b1380180e403a1ceeea93143e56c0fa1` | Already excludes `AUTHOR_ONLY` from post-render evidence and checks review artifact SHA against rendered artifact SHA. |
| Difficulty derivation | `Shared/tools/question_difficulty.py` | `5219d99603d7de6c2d1e07294d19d4508a5c312e` | Already derives score/band mechanically from five components and keeps `requested_band` planning metadata separate. |
| QRT resolver | `Shared/tools/question_review_matrix.py` | `4121dc1ea9d6aa1cca83799a48a88816a82629a8` | Uses derived difficulty band and authored cognitive-demand primary; resolves W preferentially from protected/crux reasoning moves. |
| Canonical package schema | `Shared/library/package.schema.json` | `4eadda639dcdea82b6443d0381c6bd38befda9f6` | Already includes representation `scene_instances`, case `asset_ref`/question/role/data binding and `grade9v3:core2_support_plan`. |
| Exam-bank schema | `Shared/library/competitive-exam-bank.schema.json` | `6a95ffbd238aefb6c82ce9df24ea1c187fca638a` | Exposes optional Core2 support-plan extension and delegates canonical shape to package schema. |
| Core2 support projection | `Shared/tools/core2_v2.py` | `4757d7add0b19a407f0c1cdd36f4bc5aec8c7c7f` | Already resolves `protected_move_refs`, support completions and visual bindings; completion is explicitly authored rather than inferred from prose/purpose labels. |
| Renderer | `Shared/tools/render_core.py` | `e3ae6e074aa6b6d38a5671f03f629577809dce0c` | Requires selected question/case/role/asset binding for adopted scene instances and moves protected-completing support into the attempted-solution payload. |

## Active blueprint facts

### Core1A

`BP-CORE1A-CONSTRUCTION@1.7.0` is ACTIVE for `CORE1A`.

Its responsive policy is:

- compact: `SINGLE_PANE`
- medium: `SINGLE_PANE`
- expanded: `SINGLE_PANE`
- `primary_fraction: 0.6`
- `support_fraction: 0.4`
- `expanded_min_px: 1100`

The nonzero fractions remain metadata even though expanded layout is explicitly single-pane.

### Core2

`BP-CORE2-SOURCE-QUESTION@1.9.0` is ACTIVE for `CORE2`.

Its responsive policy is:

- compact: `SINGLE_PANE`
- medium: `STACKED_SUPPORT`
- expanded: `STAGE_SUPPORT`
- `primary_fraction: 0.42`
- `support_fraction: 0.58`
- `expanded_min_px: 980`

## Established contradiction candidate for U02

PR #65 added `layout-observation.mjs`, whose `matchesBlueprintLayout(...)` correctly treats a selected `expanded: SINGLE_PANE` policy as satisfied only by one-column measurements.

However, `core-page-audit.mjs` still computes:

`expectedLayout = policy && policy.support_fraction ? { ... } : null`

and its Core1A enforcement later interprets any non-null `expectedLayout` as requiring the expanded split at/above `minPx`.

Because Core1A is `SINGLE_PANE` **and** has `support_fraction: 0.4`, this second path is not derived from `responsive_policy.expanded`. It can therefore contradict the selected blueprint even though the helper-level `stageSupportLayout` reconciliation is correct.

**U01A classification:** existing implementation contradiction to reproduce/fix in U02; not a reason to change Core1A back to split layout.

## Existing-contract reuse: negative knowledge

The stress-test recommendation must not recreate the following as greenfield schema work:

1. **Review provenance is already typed.** `AUTHOR_ONLY` / `RENDERED` / `INDEPENDENT_RENDERED` exists.
2. **Rendered review already has byte binding.** The QRT guard compares review `artifact_sha256` to the declared rendered artifact.
3. **Requested versus derived difficulty already exists.** `question_difficulty.py` derives the band from five components and separately preserves `requested_band`.
4. **Protected support linkage already exists in a bounded Core2 form.** `protected_move_refs` plus authored support completions drive pre/post-attempt eligibility.
5. **Question/case representation binding already exists in a bounded form.** `scene_instances` can bind question, role, datum refs and authored asset; the renderer fails adopted cases that do not bind correctly.

Therefore later ISS66 units must begin with **gap analysis against these existing contracts**, not field proliferation.

## Not yet decided by U01A

U01A does **not** decide:

- whether review binding must additionally fingerprint blueprint/schema/assets beyond rendered SHA/head;
- whether difficulty primary-demand evidence needs a stronger canonical decision object;
- whether protected-act/support semantics should generalize beyond the current Core2 support-plan extension;
- whether diagnostic hypothesis/probe/evidence needs new schema;
- whether any subject-neutral interaction primitive passes the worth gate.

Those belong to later bounded units.

## U01A result

**COMPLETE as a microtask; no parent-unit progress credit.**

- P remains **0/10**.
- E remains **0/10**.
- Next microtask is **U01B — matched #49–#56 structural decision-delta ledger only**.
