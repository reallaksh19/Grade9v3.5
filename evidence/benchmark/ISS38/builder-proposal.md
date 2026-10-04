# Builder Improvement Proposal — Post-Render Inspection

- **Author:** Independent Agent B (Issue #38)
- **Date:** 2026-10-04
- **Render inspected:** `evidence/benchmark/ISS38/rendered/core1a.html` and `core2.html`
- **Production renderer:** `Shared/tools/render_core.py` (v2)

---

## 1. Concrete Limitation Observed in Rendered Page

Upon inspecting `evidence/benchmark/ISS38/rendered/core1a.html` under `MIC-CHE-HYB-TORSION-ALIGNMENT`:
The page successfully mounts the staged visual (`formamide-orbital-twist.svg`) with four discrete reveal stages (`HYB-TWIST-1` to `HYB-TWIST-4`). The learner navigates these stages by clicking discrete stage chips.

**The Limitation:**
Orbital alignment under dihedral twist is physically a **continuous function of angle** (\(S(\theta) = S_0 \cos\theta\)). While discrete chips show snapshots at 0° and 90°, competition-level learners need to explore intermediate angles (e.g., 30°, 45°, 60°) to observe the non-linear relationship between dihedral angle, overlap integral, and stabilization energy. 

Currently, `interactive-page-blueprints.v1.json` provides:
- `STAGED_VISUAL` (discrete DOM stages)
- `INTERACTIVE_BRIDGE` (links to external workbench)

There is **no lightweight, accessible continuous parameter scrubber component** in the existing blueprint registry that allows direct interactive parameter scrubbing without booting a full heavyweight external simulator.

---

## 2. Proposed Minimal Reusable Module

### Component Name
`PARAMETER_SCRUBBER_COMPARATOR`

### Role Insertion
Available as an optional enhancement inside `CORE1A` (`construction`) and `CORE2` (`support`).

### Schema Addition
In `Shared/web/interactive-page-blueprint.schema.json`:
```json
{
  "parameter_control": {
    "type": "object",
    "properties": {
      "id": { "type": "string" },
      "parameter_name": { "type": "string" },
      "min_value": { "type": "number" },
      "max_value": { "type": "number" },
      "step": { "type": "number" },
      "unit": { "type": "string" },
      "css_variable": { "type": "string" },
      "display_relation_ref": { "type": "string" }
    },
    "required": ["id", "parameter_name", "min_value", "max_value", "css_variable"]
  }
}
```

### Runtime Implementation
1. Render an accessible `<input type="range" min="0" max="90" step="5" value="0">` inside the figure header.
2. Bind input changes to a CSS Custom Property on the parent SVG container:
   `svg.style.setProperty('--g9-scrub-angle', e.target.value + 'deg')`.
3. In the authored SVG:
   `<g transform="rotate(var(--g9-scrub-angle, 0deg) 450 260)"> ... </g>`
4. Live output element displays calculated value:
   `Output: S(θ) = S_0 · cos(θ) = 0.71 S_0 at θ = 45°`.

### Non-Breaking Migration & Fallback
- **No-JS / Accessible Fallback:** If JavaScript is disabled or unsupported, the discrete `<g data-g9-stage-id="...">` stages continue to function unchanged.
- **Existing Pages:** Zero changes required for existing packages; existing blueprints continue to pass without modification.
