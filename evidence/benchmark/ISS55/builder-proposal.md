# Post-Render Builder Proposal: Set B Polynomial Stress Test V1 (Issue #55)

**Author:** Agent B (Independent Set B Execution)  
**Target Subject/Cohort:** Mathematics Grade 9, Cohort D3 (Polynomials in one variable with real coefficients)  
**Launch Baseline Commit:** `91719ad8df2bfc06c6a481590d2e24c510c24835`  
**Date:** 2026-10-05  

---

## 1. Executive Summary & Verification Summary

Set B has independently executed the Polynomial Stress Test V1 (Q1–Q10) under strict prompt custody and blind partition from Set A (#51). Both Core2 (`source questions`) and Core1A (`declarative detailed teaching`) have been compiled and rendered via the canonical production renderer `Shared/tools/render_core.py`.

### Verification Status:
1. **Schema Integrity:** `package.v1.json` validated against `Shared/library/package.schema.json` (Draft 2020-12): **0 errors**.
2. **Owner Bank Integrity:** `Shared/tools/owner_bank.py check evidence/benchmark/ISS55/generated/owner.bank.json`: **OK**.
3. **Renderer Depth & Authority Gate:** `Shared/tools/render_core.py gaps --manifest evidence/benchmark/ISS55/generated/product.manifest.json`: **0 depth gaps; 0 subject-authority findings**.
4. **Renderer Page Generation:** `Shared/tools/render_core.py build ... --mode PAGES`: **Successfully wrote `core1a.html`, `core2.html`, and `index.html`** (10 Core2 questions, 3 Core1A microtopics with 10 construction units).
5. **Quality Contract Static Gate:** `Shared/tools/quality_gate.py ... --static`: **0 findings**.
6. **Headless Browser Measurement:** `tools/site-audit/core-page-audit.mjs`:
   - `core2.html`: 0 small touch targets (<48px: 0/97), minFont 14px, 0 horizontal overflow, 10 accessible SVGs, `stage68=true`, 0 console/runtime errors.
   - `core1a.html`: 0 small touch targets (<48px: 0/144), minFont 14px, 0 horizontal overflow, 10 accessible SVGs, 0 console/runtime errors.

---

## 2. Builder Findings & Proposals

During end-to-end rendering and quality gating of Core1A and Core2, two builder-level improvements were identified:

### Finding 1 (Primary): Misalignment between Single-Pane Core1A and `PAGE-STAGE-SUPPORT` Quality Contract Rule

#### Root Cause Analysis:
- `BP-CORE1A-CONSTRUCTION@1.7.0` in `Shared/web/interactive-page-blueprints.v1.json` deliberately configures Core1A as single-pane:
  ```json
  "responsive_policy": {
    "compact": "SINGLE_PANE",
    "medium": "SINGLE_PANE",
    "expanded": "SINGLE_PANE",
    "primary_fraction": 0.6,
    "support_fraction": 0.4,
    "expanded_min_px": 1100,
    "support_sticky": false
  }
  ```
  This single-pane architecture ensures an integrated, distraction-free declarative lesson flow where worked examples and visual representations are read coherently in narrative order, as reinforced by `tools/site-audit/core-page-audit.mjs` (commit `31ea86c5`):
  `if (!want) { if (row.core1aLayout.expandedCount !== 0) failures.push("${vp.name}: integrated lesson unexpectedly split into columns"); }`
- However, `Shared/tools/render_core.py` (lines 2430–2433) only outputs split CSS grid columns when `rp.get("expanded") == "STAGE_SUPPORT"`:
  ```python
  if rp.get("expanded") != "STAGE_SUPPORT" or not rp.get("support_fraction"):
      continue
  ```
  Consequently, `render_core.py` does not emit `grid-template-columns: minmax(0, 60fr) minmax(0, 40fr)` into `core1a.html`.
- Meanwhile, `Shared/quality/learner-quality.v1.json` rule `PAGE-STAGE-SUPPORT` still lists `"CORE1A"` in its `roles`:
  ```json
  {
    "id": "PAGE-STAGE-SUPPORT",
    "roles": ["CORE1A", "CORE1B", "CORE2", "CORE2A", "CORE2B"],
    "check": { "op": "rendered_flag", "field": "stage_support_layout" }
  }
  ```
  And `tools/site-audit/core-page-audit.mjs` sets `stageSupportLayout` solely based on whether `expectedColumns` ({primary: 60, support: 40}) is found in the stylesheet:
  ```javascript
  stageSupportLayout: !!expectedColumns && new RegExp(`grid-template-columns:\\s*...`).test(sheetText)
  ```
  Because the single-pane Core1A stylesheet does not contain this split-grid rule, `stageSupportLayout` evaluates to `false`, causing `quality_gate.py` (when run with live browser measurement) to flag an S2 advisory: `PAGE-STAGE-SUPPORT: core1a.html: stage support layout absent`.

#### Proposed Builder Fix:
Update `tools/site-audit/core-page-audit.mjs` line 139:
```javascript
// Only expect split columns if the blueprint actually specifies STAGE_SUPPORT for expanded layout:
const expectedColumns = (policy && policy.expanded === 'STAGE_SUPPORT' && policy.support_fraction)
  ? { primary: pct(policy.primary_fraction), support: pct(policy.support_fraction) }
  : null;
```
And adjust `Shared/quality/learner-quality.v1.json` rule `PAGE-STAGE-SUPPORT` to exempt blueprints where `expanded` is `SINGLE_PANE`. This reconciles the quality contract with the intentional single-pane pedagogical structure of Core1A.

---

### Finding 2 (Secondary): Automatic Asset Packaging for `--mode PAGES` Builds

#### Observation:
When `render_core.py build ... --mode PAGES` writes HTML pages into `--out <DIR>`, the generated `<head>` includes relative links:
```html
<link rel="stylesheet" href="css/modern-learner.css">
<link rel="stylesheet" href="css/tablet-12-7.css">
```
and scripts:
```html
<script src="js/display-controls.js"></script>
<script src="js/site-header.js"></script>
```
However, `render_core.py` currently writes only `.html` and `render-receipt.json` files, leaving `css/` and `js/` to be copied manually or assumed from the host root.

#### Proposed Builder Fix:
Add an automatic asset synchronization step in `Shared/tools/render_core.py` for `mode == "PAGES"`:
```python
if mode == "PAGES":
    import shutil
    shutil.copytree(REPO / "public/css", out / "css", dirs_exist_ok=True)
    shutil.copytree(REPO / "public/js", out / "js", dirs_exist_ok=True)
```
This guarantees that any rendered artifact folder is immediately self-contained, portable, and offline-testable.

---

## 3. Reasoned Verdict on Candidate Package (`NO_CHANGE` to Upstream Tooling in Candidate Branch)

While the builder proposals above are recommended for upstream platform maintenance, the Set B candidate files strictly adhere to existing repository rules and do not introduce unapproved modifications to `Shared/tools/` or `Shared/quality/` within this candidate branch. All candidate inputs and generated pages comply 100% with the active production pipeline.
