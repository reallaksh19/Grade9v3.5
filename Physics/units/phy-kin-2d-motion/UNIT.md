---
unit: phy-kin-2d-motion
package: Physics/library/phy-kin-2d-motion.v1.json
owner_agent: UNASSIGNED
spine_nodes: []
microtopics: ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS", "MIC-PHY-KIN-2D-CONSTANT-ACCELERATION", "MIC-PHY-KIN-PROJECTILE-MODEL"]
sources: ["SRC-AUTHOR-KIN-2D-EXAMSIDE-ADAPTATION", "ACT-KIN-2D-SHARED-CLOCK", "ACT-KIN-2D-EVENT-CLOCK", "ACT-KIN-2D-PROJECTILE-MODEL-GATE", "ACT-KIN-2D-APEX-FALLACY", "ACT-KIN-2D-EQUAL-HEIGHT-STATE", "ACT-KIN-2D-LANDING-GEOMETRY"]
inventories: []
grade_profile:
  base_grade: null
  assumed_prerequisites: ["CAP-KIN-2D-CONSTANT-ACCELERATION", "CAP-KIN-2D-INDEPENDENT-COMPONENTS", "CAP-KIN-CONSTANT-ACCELERATION", "CAP-VECTOR-SIGNED-COMPONENT"]
  enrichment: []
coverage:
  mode: CURATED_SELECTION
  inventory: null
budget_usd: null
---

# Two-dimensional kinematics and projectile model

Existing package scope (carried forward): Owner-approved ExamSIDE question-demand slice for plane motion, now semantically decomposed for the Topic Atlas: one-frame/two-component motion, componentwise constant acceleration, and the gravity-only projectile model with explicit apex, same-height and horizontal/unequal-height event reasoning. Trajectory-equation derivation, drag, variable gravity, moving-launcher/relative-motion cases and advanced projectile geometry remain outside this bounded packet.

## Status notes

- This is an inherited package. Unit ownership, source readback and budget are not assigned by this migration.
- `spine_nodes`, sources, grade and prerequisites above are copied from explicit package data; empty or null means unrecorded.
- No design note, self-critique, prototype review or Owner calibration is claimed here.
- The selected product remains governed by its existing manifest; an inventory denominator is not yet declared.
