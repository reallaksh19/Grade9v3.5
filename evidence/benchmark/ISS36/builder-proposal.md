# Builder Proposal: Dynamic Dihedral & Orbital-Overlap Comparator Module

## 1. Concrete Rendered Limitation Observed in Exact Artifacts
Upon inspecting the exact rendered learner pages (`evidence/benchmark/ISS36/rendered/core1a.html` and `core2.html`), the current production renderer (`Shared/tools/render_core.py`) mounts SVG figures as discrete, staged groups (`<g data-g9-stage-id="...">`) with sequential reveal buttons.

While this structure guarantees accessibility and clean stage-by-stage cognitive pacing, it exposes a pedagogical limitation for stereochemical 3D hybridisation concepts:
- In `MIC-CHEM-G11-ALLENE-STEREO` (teaching Q3 and Q4), the learner must understand why copying the planar ethene sketch to allene fails because the central carbon's unhybridised $p$-orbitals are orthogonal ($p_y \perp p_z$), and forcing the terminal groups to be coplanar produces zero net $\pi$-overlap integral ($\langle p_y | p_z \rangle = 0$).
- In `MIC-CHEM-G11-HYBRID-EPISTEMICS-CONJUGATION` (teaching Q8), the learner must understand why twisting ethene degrades $\pi$-overlap proportional to $\cos\theta$ while ethane rotation preserves cylindrical $\sigma$-overlap.

In the rendered page, learners view discrete SVG stages, but cannot interactively twist or adjust the dihedral angle $\theta$ to observe the continuous degradation of the $\pi$-overlap integral.

## 2. Minimal Reusable Module Specification
We propose a lightweight, zero-external-dependency module for the existing interactive builder: `dihedral-orbital-comparator`.

### A. Component Schema Extension (`representation.schema.json`)
```json
{
  "$id": "https://grade9v3.net/schemas/dihedral-orbital-comparator.v1.json",
  "type": "object",
  "properties": {
    "module": { "const": "DIHEDRAL_ORBITAL_COMPARATOR" },
    "target_group_id": { "type": "string" },
    "rotation_axis": { "type": "string", "enum": ["X", "Y", "Z"] },
    "angle_range": {
      "type": "object",
      "properties": {
        "min_deg": { "type": "number", "default": 0 },
        "max_deg": { "type": "number", "default": 90 },
        "step_deg": { "type": "number", "default": 5 },
        "equilibrium_deg": { "type": "number" }
      },
      "required": ["equilibrium_deg"]
    },
    "overlap_function": {
      "type": "string",
      "enum": ["COS_THETA", "SIN_THETA", "INVARIANT_SIGMA"]
    },
    "pedagogical_callout": { "type": "string" }
  },
  "required": ["module", "target_group_id", "rotation_axis", "angle_range", "overlap_function"]
}
```

### B. Blueprint Integration
- **Insertion point:** Mounted within `BP-CORE1A-CONSTRUCTION` slot `representation` when `representation.extensions["grade9v3:interactive_module"]` is present.
- **Client runtime implementation:** 30 lines of accessible vanilla JavaScript in `public/js/tablet-shell.js` that attaches an accessible slider (`<input type="range" min="0" max="90" step="5" aria-label="Dihedral Angle">`) to apply SVG matrix transforms (`transform="rotate(θ, cx, cy)"`) and updates an inline overlap meter:
  $$\text{Overlap}(\theta) = |\cos\theta|$$
  - At $\theta = 0^\circ$ (coplanar allene): Overlap $= 0.00$ (PROHIBITED / BROKEN $\pi$-BOND).
  - At $\theta = 90^\circ$ (orthogonal allene): Overlap $= 1.00$ (MAXIMUM STABILISATION / GROUND STATE).

### C. Backward Compatibility & Migration
- Existing static and multi-stage SVGs remain 100% backward compatible without changes.
- Products without this extension render the standard multi-stage SVG as currently generated.
- Fully accessible: supports keyboard navigation (left/right arrow keys) and ARIA live regions for screen readers.
