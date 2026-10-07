# Builder Proposal: Issue #53 (Set B) — Polynomial Stress Test v1

**Proposal ID:** `BUILDER-PROP-ISS53-COEFF-GRID-01`  
**Author:** Agent B (Independent Candidate Developer)  
**Date:** 2026-10-05  
**Subject:** Mathematics / Core Builder Infrastructure  
**Delivery Unit:** U7 (Builder Improvement Proposal)  

---

## 1. Concrete Observed Limitations

During the construction and quality gate audit of the Grade 9 Mathematics Polynomial benchmark (`EVIDENCE-MATH-ISSUE53-POLY-D1`), two concrete builder-level limitations were identified:

### Limitation A: Blueprint-to-CSS Policy Desynchronization
- **Observation:** In `Shared/web/interactive-page-blueprints.v1.json`, blueprint `BP-CORE1A-CONSTRUCTION@1.7.0` declares:
  ```json
  "responsive_policy": {
    "primary_fraction": 0.6,
    "support_fraction": 0.4,
    "expanded_min_px": 1100
  }
  ```
  However, the shared tablet stylesheet `public/css/tablet-12-7.css` hardcodes:
  ```css
  .stage-grid-12-7 {
    grid-template-columns: 1.85fr 1fr;
  }
  ```
  `1.85fr 1fr` corresponds to approximately `64.9% / 35.1%`, not `60% / 40%`.
- **Impact:** The browser audit `tools/site-audit/core-page-audit.mjs` executes a strict regex search for `minmax(0, 60fr) minmax(0, 40fr)`, which inevitably fails against the static CSS unless overridden or relaxed. This creates an artificial blocking failure in browser-based quality gate runs even when the visual layout is completely sound.

### Limitation B: Absence of Interactive Positional Table Component
- **Observation:** In Grade 9 Mathematics (Polynomials), the core cognitive hurdle is representing omitted variable powers as explicit zero entries ($0 \cdot x^k = 0$) and aligning like terms for addition.
- **Impact:** Because the builder only offers static figures (`STAGED_VISUAL`) with SVG image assets or plain HTML textareas for attempts, authors must handcraft complex multi-stage SVGs (`poly-coeff-table.svg`) to illustrate power rows. Learners have no interactive tactile mechanism to place zero entries into power slots and verify dimensional alignment before calculating sums.

---

## 2. Proposed Solution

### Proposal 1: Synchronize Blueprint Fractions with Standardized Responsive CSS
Update `BP-CORE1A-CONSTRUCTION` in `Shared/web/interactive-page-blueprints.v1.json` to synchronize with `tablet-12-7.css`:
```json
{
  "primary_fraction": 0.65,
  "support_fraction": 0.35,
  "expanded_min_px": 1100
}
```
And update `render_core.py` to inject the precise `grid-template-columns` matching the blueprint declaration directly into the page stylesheet `<style data-g9-tablet-shell>` rather than relying on a disconnected static file.

### Proposal 2: Introduce `POLYNOMIAL_COEFFICIENT_GRID_INTERACTOR`
A lightweight, declarative interactor component for Mathematics that can be mounted in `CORE1A` or `CORE2`:
- **Component ID:** `POLYNOMIAL_COEFFICIENT_GRID`
- **Presentation Mode:** `INTERACTIVE_GRID`
- **Component Spec:**
  ```json
  {
    "component": "POLYNOMIAL_COEFFICIENT_GRID",
    "degree": 3,
    "variable": "x",
    "expected_coefficients": [
      {"power": 3, "value": 5, "editable": false, "label": "Leading term"},
      {"power": 2, "value": 0, "editable": true, "label": "Missing quadratic term"},
      {"power": 1, "value": -2, "editable": false, "label": "Linear term"},
      {"power": 0, "value": 7, "editable": false, "label": "Constant term"}
    ],
    "verification_rule": "ALL_POWERS_ACCOUNTED"
  }
  ```
- **Learner Experience:** Learners drag or enter scalar coefficients for omitted powers, receiving immediate visual confirmation that $0 \cdot x^2 = 0$ preserves index alignment before like-term addition.

---

## 3. Schema, Migration, and Check Implications

1. **Schema Implications:**
   - In `Shared/web/interactive-page-blueprints.v1.json`: Add `POLYNOMIAL_COEFFICIENT_GRID` to `allowed_components` under `slot-construction` and `slot-attempt`.
   - In `Mathematics/adapter/QualityVocabulary.json`: Add `COEFFICIENT_GRID` to `representation_kinds`.
2. **Backward Compatibility & Migration:**
   - 100% backward compatible. Existing static SVGs (such as `poly-coeff-table.svg`) remain valid `TABLE_OF_VALUES` representations.
   - When JavaScript is unavailable, the component degrades gracefully to a standard HTML `<table>`.
3. **Verification Check Additions:**
   - Add static rule `MATH-COEFF-GRID-COMPLETE` to `Shared/quality/learner-quality.v1.json`:
     - Verifies all powers from degree $n$ down to $0$ are explicitly declared.
     - Verifies omitted powers have expected value $0$.

---

## 4. Verdict & Recommendation

This proposal solves both an existing automated testing discrepancy (responsive fraction matching) and enhances learner engagement with a high-fidelity, reusable pedagogical component. Recommended for adoption in the next builder release cycle.
