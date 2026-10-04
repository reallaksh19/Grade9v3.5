# Builder Improvement Proposal — Issue #32 (Agent B)

## 1. Post-Render Inspection Context

The rendered deliverables for Issue #32 (`core1a.html` and `core2.html`) were inspected in the governed tablet reading shell across desktop and tablet viewport configurations.

### Observed Strengths
1. **Governed Blueprint Execution:** Both `core1a.html` (Construction) and `core2.html` (Source Questions) render with zero gaps (`draft: false`) under Blueprint 1.9.0 registry rules.
2. **Pedagogical Alignment:** The 3-stage SVG figures (`hybrid-tetrahedral-3d.svg`, `sigma-pi-overlap.svg`, `electron-domains-hcho.svg`) legibly isolate the essential mental models:
   - 2D flat cross illusion versus 3D tetrahedral electrostatic minimization.
   - Coaxial end-on sigma overlap with cylindrical symmetry versus lateral side-on pi overlap with an internuclear nodal plane.
   - Multiple-bond steric domain envelopes (single spatial direction for double bonds).
3. **W Protection & Inert Payloads:** Hint ladders and solutions remain strictly inert prior to learner commitment.

---

## 2. Concrete Rendered Limitation

In questions requiring stereochemical translation (notably **Q4** for $\mathrm{NH_3}$ and **Q7** for $\mathrm{CH_4}$), the prompt demands:
> *"translate that information into a labelled diagram showing all four electron domains; distinguish the lone pair from the three bond directions. Do not treat the planar Lewis sketch as the molecular shape."*

### Current Interaction Delivery
In the current Core2 reader interface:
- Learners have a free-text response field (`<textarea>`) and an option to confirm self-worked paper sketches.
- The staged SVG provides sequential revelation of the stereochemical conventions.
- However, the learner cannot interactively manipulate or test their own 3D orientation hypothesis (e.g. testing whether placing four bonds at 90° coplanar vs 109.5° non-coplanar satisfies spatial repulsion constraints) directly within the page before opening hints or reveals.

---

## 3. Minimal Reusable Module: `STEREO_WEDGE_DASH_INTERACTOR`

To bridge this specific representational gap without introducing heavy 3D WebGL or external JavaScript runtimes, we propose a lightweight, accessible HTML5/SVG interactive module.

### A. Module Schema
```json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "title": "StereoWedgeDashInteractor",
  "type": "object",
  "properties": {
    "module_id": { "type": "string" },
    "central_atom": { "type": "string" },
    "coordination_number": { "type": "integer", "enum": [2, 3, 4] },
    "target_geometry": { "type": "string", "enum": ["LINEAR", "TRIGONAL_PLANAR", "TETRAHEDRAL"] },
    "bond_slots": {
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "slot_id": { "type": "string" },
          "angle_degrees": { "type": "number" },
          "supported_depths": {
            "type": "array",
            "items": { "type": "string", "enum": ["IN_PLANE_LINE", "PROJECTING_WEDGE", "RECEDING_DASH", "LONE_PAIR_LOBE"] }
          }
        },
        "required": ["slot_id", "supported_depths"]
      }
    }
  },
  "required": ["module_id", "central_atom", "coordination_number", "target_geometry", "bond_slots"]
}
```

### B. Blueprint Integration & Insertion Point
- **Target Role:** `BP-CORE1A-CONSTRUCTION` (under `CU-CHE-3D-REPRESENTATION`) and `BP-CORE2-SOURCE-QUESTION` (under interactive attempt mode).
- **Slot:** Inserted as an optional child within the existing `figure` container immediately adjacent to the `g9-stage-controls`.
- **Learner Interaction:** Learners click or press `Enter`/`Space` on a bond axis node to cycle through bond depth styles (`Line` → `Wedge` → `Dash` → `Lone Pair Lobe`).
- **Feedback Mechanism:** Upon committing their configuration, the module visually contrasts their selected spatial layout with the ideal minimum-energy electrostatic geometry, displaying the angular penalty of 2D coplanar (90°) crowding versus 3D tetrahedral (109.5°) separation.

### C. Backward Compatibility & Non-Disruption
1. **Strictly Additive:** If a question or package omits the `StereoWedgeDashInteractor` extension, `render_core.py` renders the standard static/staged SVG asset without change.
2. **Zero External Dependencies:** Implemented using pure inline SVG elements, standard DOM manipulation, and CSS variables matching `public/css/tablet-12-7.css`.
3. **Accessibility Standards:** Meets WCAG 2.1 AA and Grade9 tablet specifications:
   - Minimum 48px touch targets for each bond node.
   - Screen reader text announcing current depth state (e.g. `aria-label="Bond 3: Projecting solid wedge (forward)"`).
   - High-contrast visual focus ring (`outline: 3px solid var(--accent)`).

---

## 4. Evidence-Based Summary
- **Recommendation:** Implement `STEREO_WEDGE_DASH_INTERACTOR` in a future template release as a targeted extension for 3D stereochemical and VSEPR question sets.
- **Current Candidate Status:** For the present Issue #32 candidate freeze, the current governed implementation passes all strict quality gates with zero gaps.
