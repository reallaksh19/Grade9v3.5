# ISS50 Builder Improvement Proposal — CoordinatePlotResponse

**Issue:** #50  
**Round:** POLYNOMIAL-STRESS-V1  
**Status:** PROPOSAL ONLY — no shared builder code is changed by this candidate.

## Observed limitation in the exact rendered page

The governed Core2 render for Q5 asks the learner to produce a five-row value table and plot five ordered pairs. The actual `ATTEMPT` component renders as `data-g9-response-type="free_response"` with a textarea, while the support column mounts a safe blank coordinate-axes representation. The axes are useful because they expose only the requested coordinate frame; however, the learner cannot place, move or remove points in the page. They must describe coordinates in text or work externally on paper.

This is an interaction-fit limitation, not a mathematical-content defect. The exact render otherwise passes the reference-depth, protection, tablet-layout and accessibility audits.

## Minimal reusable proposal

Add an optional **`COORDINATE_PLOT_RESPONSE`** response type that lets an authored question request a learner-owned table/plot control without making the plot itself academic authority.

Suggested canonical response data:

```json
{
  "type": "COORDINATE_PLOT_RESPONSE",
  "x_axis": {"label": "x", "min": -2, "max": 2, "step": 1},
  "y_axis": {"label": "p(x)", "min": -2, "max": 4, "step": 1},
  "required_x_values": [-2, -1, 0, 1, 2],
  "allow_table": true,
  "allow_point_edit": true
}
```

The attempt control should:
- expose an editable value-table row for each governed input when `required_x_values` is present;
- allow touch, mouse and keyboard placement/removal of plotted points;
- keep every answer coordinate absent from the initial DOM/search corpus;
- provide a text/table equivalent to the plotted state for screen readers;
- preserve the existing “worked on paper” fallback;
- reveal comparison/solution material only after the existing commitment gate;
- avoid inferring misconception or mastery from an incorrect point unless a separate governed diagnostic explicitly warrants that claim.

## Insertion and authority boundaries

1. Extend the canonical question `response` schema rather than adding a second page-specific academic record.
2. Render it inside the existing Core2 `ATTEMPT` blueprint component; no new cognitive-demand or QRT authority is needed.
3. Reuse canonical `representation_ref` only for the visual frame when appropriate. Learner-entered points are response state, not a canonical representation.
4. Existing `free_response` items migrate unchanged. Adoption is opt-in, so older packages and owner banks remain valid.
5. Print/PDF fallback should materialise blank axes/table fields, not protected answer points.

## Required checks

A shared implementation should add retained-fixture tests for:
- no answer coordinates in initial HTML, metadata, search text or accessibility tree;
- keyboard-only point creation/edit/removal and visible focus;
- >=48 px touch targets under the tablet profile;
- semantic table/point announcement and labelled axes;
- no landscape/portrait overflow at the existing reference viewports;
- deterministic response serialisation and restoration;
- post-commit comparison only;
- print fallback and reduced-motion behaviour.

## Why this is preferable to changing this candidate locally

Q5's current textarea + paper fallback is honest and functional, so a one-off custom widget would create a second renderer path and violate the shared-builder boundary. The reusable response type solves the observed class of graph/table construction tasks across Mathematics and other coordinate-based subjects while preserving the current renderer and blueprint authority.
