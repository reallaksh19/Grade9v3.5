# Builder Improvement Proposal — Post-Render Inspection

- **Author:** Independent Agent B (Issue #56 · Matched Set B Run)
- **Date:** 2026-10-05
- **Render Inspected:** `evidence/benchmark/ISS56/rendered/core1a.html` and `core2.html`
- **Production Renderer:** `Shared/tools/render_core.py` (v2)
- **Status:** CANDIDATE

---

## 1. Concrete Limitation Observed in Rendered Page

Upon detailed inspection of `evidence/benchmark/ISS56/rendered/core1a.html` (under `MIC-MATH-POLY-PARAM-REPRESENTATION`) and `evidence/benchmark/ISS56/rendered/core2.html` (at `OWN-ISSUE56-POLY-04` and `OWN-ISSUE56-POLY-01`):

The rendered pages successfully mount all four authored vector assets:
- `poly-interpolation-coset.svg` (`INTERP-1`..`4`)
- `poly-sign-multiplicity.svg` (`PARITY-1`..`4`)
- `poly-parameter-bifurcation.svg` (`PARAM-1`..`4`)
- `poly-box-volume-model.svg` (`BOX-1`..`4`)

Learners navigate these figures via discrete stage buttons (`data-g9-stage-id`).

### The Limitation
Polynomial families with variable parameters (such as $F_a(x) = (a-1)x^4 + 2(a-1)x^3 + (a+2)x^2 + 2(a+2)x$ in Q4 or the unbounded interpolation coset $p(x) = x^2 + 1 + c \cdot x(x-1)(x-2)(x-3)$ in Q1) are **continuous dynamic algebraic systems**:
1. In Q4 ($F_a(x)$), as the real parameter $a$ varies continuously, the roots move along the real axis. Learners must conceptualize how roots collide to form a triple zero at $a = -2$, merge to form a double zero at $a = 2/5$, and cause the leading term to vanish at $a = 1$ (dropping the degree from 4 to 2). Discrete snapshot buttons at $a = -2, 2/5, 1$ show the aftermath of these bifurcations, but do not convey the trajectory of the roots or the topological continuity of the deformation.
2. In Q1 ($p(x) = x^2+1 + c\cdot V(x)$), learners need to see that as the scalar multiplier $c$ is continuously varied, the four data points $(0,1), (1,2), (2,5), (3,10)$ remain rigidly fixed (pinned nodes) while the rest of the polynomial flexes and oscillates through higher amplitudes.

Currently, `Shared/web/interactive-page-blueprints.v1.json` supports only:
- `STAGED_VISUAL` (discrete DOM visibility toggles)
- `INTERACTIVE_BRIDGE` (external hyperlink out of the tablet shell)

There is **no lightweight, accessible in-page parameter slider/scrubber** that enables continuous parameter exploration directly within the tablet shell without launching a full heavyweight external simulator.

---

## 2. Proposed Minimal Reusable Module

### Component Name
`CONTINUOUS_PARAMETER_SCRUBBER`

### Blueprint Role Placement
An optional child block inside the `FIGURE` / `STAGED_VISUAL` slot of `CORE1A` and `CORE2`.

### Schema Addition
In `Shared/web/interactive-page-blueprint.schema.json` (under `component.properties`):
```json
{
  "parameter_scrubber": {
    "type": "object",
    "description": "Accessible continuous parameter control that modulates CSS custom properties or SVG element coordinates.",
    "properties": {
      "id": { "type": "string" },
      "parameter_symbol": { "type": "string" },
      "min_value": { "type": "number" },
      "max_value": { "type": "number" },
      "step": { "type": "number" },
      "default_value": { "type": "number" },
      "css_variable": { "type": "string" },
      "critical_points": {
        "type": "array",
        "items": {
          "type": "object",
          "properties": {
            "value": { "type": "number" },
            "label": { "type": "string" },
            "bifurcation_kind": { "type": "string", "enum": ["DEGREE_DROP", "ROOT_COLLISION", "SIGN_FLIP"] }
          },
          "required": ["value", "label"]
        }
      }
    },
    "required": ["id", "parameter_symbol", "min_value", "max_value", "step", "css_variable"]
  }
}
```

### Runtime Implementation
1. **Accessible Control Rendering:**
   Inside the figure container header, render a native accessible slider:
   ```html
   <div class="g9-parameter-scrubber" data-g9-scrubber="param-a">
     <label for="scrub-param-a">Parameter <var>a</var>:</label>
     <input type="range" id="scrub-param-a" min="-3" max="3" step="0.05" value="0"
            aria-valuemin="-3" aria-valuemax="3" aria-valuenow="0" aria-valuetext="a = 0">
     <output for="scrub-param-a" class="g9-scrubber-output">a = 0.00</output>
     <div class="g9-critical-ticks">
       <span style="left: 16.7%;" title="Triple root at 0">a = -2.0</span>
       <span style="left: 56.7%;" title="Double root at -2">a = 0.4</span>
       <span style="left: 66.7%;" title="Degree drop to 2">a = 1.0</span>
     </div>
   </div>
   ```

2. **Zero-Overhead CSS Binding:**
   The slider event listener updates a single CSS custom property on the SVG root:
   ```javascript
   input.addEventListener('input', (e) => {
     svgElement.style.setProperty('--g9-param-val', e.target.value);
     outputElement.textContent = `a = ${parseFloat(e.target.value).toFixed(2)}`;
   });
   ```

3. **Dynamic Vector Modulation:**
   Authored SVGs utilize CSS variable transforms:
   ```xml
   <!-- Root marker dynamically translating along the x-axis -->
   <g class="bifurcation-marker" style="transform: translateX(calc(var(--g9-param-val, 0) * 40px));">
     <circle r="5" fill="#1a73e8" />
   </g>
   ```

### Non-Breaking Migration & Progressive Enhancement
- **No-JS / Accessible Fallback:** If JavaScript is disabled or unsupported, the discrete `<button data-g9-stage-id="...">` chips continue to toggle stages normally. The slider is styled as `display: none` in `@media (scripting: none)`.
- **Backward Compatibility:** All existing packages and blueprint schemas continue to pass 100% without modification, as `parameter_scrubber` is strictly optional (`level: "OPTIONAL"`).
- **Pedagogical Alignment:** Enables learners to dynamically observe how mathematical theorems operate continuously across parameter manifolds without violating the tablet shell's lightweight execution model.
