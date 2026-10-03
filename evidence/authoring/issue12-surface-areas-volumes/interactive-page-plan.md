# Architectural & Pedagogical Plan: Interactive Composite Solids
## Tough-Topic Interactive Page: Grade 9 Surface Areas & Volumes

> **Document Class:** Feature Specification & Pedagogical Architecture Plan  
> **Status:** PROPOSED & READY FOR IMPLEMENTATION  
> **Target Path:** `public/standalone/practice/surface-areas-volumes/interactive-composite-solids.html`  
> **Governing Standards:** BP-CORE2-STANDALONE@1.5.0 / BP-INTERACTIVE-EXPLORER@1.0.0, PR #8 Minimal-Prompt Intake Policy, `Shared/tools/toughest_concept.py`  

---

### 1. Owner Requirement & Context Intake

- **Owner Requirement:** *"Plan for a interactive page for the tough topic in topic list"*
- **Subject / Grade:** Mathematics · Grade 9
- **Topic Suite:** Surface Areas and Volumes (10 Questions, Q1–Q10)
- **Learner Profile:** `PROFILE-ISSUE12-SAV-REVISION` (Purpose: `REVISION`, Baseline capabilities: `DEMONSTRATED`)

---

### 2. Toughest Concept Determination & Justification

To objectively determine the "tough topic in the topic list," we apply the repository's canonical selection rule codified in [`Shared/tools/toughest_concept.py`](file:///c:/Users/reall/Documents/antigravity/lively-goodall/Shared/tools/toughest_concept.py):

> *"The question whose difficulty is most **conceptual** (`concept_model_selection` + `trap_exception_sensitivity`, each 0 to 2), then the higher total score, then `representation_translation`, then `reasoning_chain_length`, then the first in the bank."*

#### Ranking Analysis Across Q1–Q10:

| Rank | Question ID | Topic / Crux | Conceptual ($/4$) | Total Score ($/10$) | Band |
| :---: | :---: | :--- | :---: | :---: | :---: |
| **#1** | **Q6** | **Composite Solid: Cone on Hemisphere (Hidden Interface)** | **4** | **6** | **D3** |
| #2 | Q9 | Sphere Recasting (Volume Conservation vs Area Non-Conservation) | 3 | 5 | D2 |
| #3 | Q3 | Open Cylindrical Bucket (Single Base vs TSA) | 2 | 5 | D2 |
| #4 | Q5 | Hemispherical Bowl (Curved Inner vs Flat Base) | 2 | 5 | D2 |
| #5 | Q7 | Hollow Vessel Painting (Outer Wall + Bottom Base) | 2 | 5 | D2 |
| #6 | Q4 | Conical Tent (Pythagorean Slant Height Bridge) | 2 | 4 | D2 |
| #7 | Q8 | Cuboidal Tank Capacity (Unit Conversion Chain) | 2 | 4 | D2 |
| #8 | Q2 | Cylinder Curved Surface (Diameter Trap) | 2 | 3 | D2 |
| #9 | Q10 | Cone vs Cylinder Volume Ratio (Structural Comparison) | 2 | 3 | D2 |
| #10 | Q1 | Cube Total Surface Area (Direct Evaluation) | 0 | 1 | D1 |

**Selected Focus:** **Q6 — Composite Solids with Hidden Internal Interfaces** is the decisive #1 toughest concept:
- Maximum conceptual difficulty rating ($4/4$ on `concept_model_selection` and `trap_exception_sensitivity`).
- Only **Band D3** problem in the batch (Score $6/10$).
- High cognitive demand: `QRT-SYNTHESIZE-D3`.

---

### 3. Core Pedagogical Problem & Decisive Crux

#### The Primary Misconceptions ($M_1$ & $M_2$):
1. **The Additive Surface Fallacy ($M_1$):** Learners instinctively calculate $\text{Total Surface Area} = \text{TSA}_{\text{cone}} + \text{TSA}_{\text{hemisphere}}$. They mechanically add up formulas without evaluating whether the faces remain boundary surfaces:
   $$\text{Wrong:} \quad (\pi r l + \pi r^2) + (3\pi r^2) = \pi r l + 4\pi r^2$$
2. **The Hidden Circular Joint Trap ($M_2$):** When the cone is mounted on the hemisphere, their circular faces (each of area $\pi r^2$) meet in planar contact. This joint becomes completely interior to the composite toy. It cannot be touched, painted, or exposed. Including it counts an internal interface as external boundary.
3. **The Auxiliary Bridge Gap ($M_3$):** Given radius $r = 3.5\text{ cm}$ and vertical height $h = 12\text{ cm}$, learners frequently substitute the vertical height $h$ directly into $\pi r l$, bypassing the necessary Pythagorean derivation:
   $$l = \sqrt{r^2 + h^2} = \sqrt{3.5^2 + 12^2} = \sqrt{12.25 + 144} = \sqrt{156.25} = 12.5\text{ cm}$$

#### Target Learning Goal:
Enable the learner to build an unbreakable physical intuition:
$$\mathbf{\text{Exposed Surface Area} = \text{Cone CSA} + \text{Hemisphere CSA} = \pi r l + 2\pi r^2}$$
**The interface circle ($\pi r^2$) contributes $0\text{ cm}^2$ to the exposed area.**

---

### 4. Interactive Page Functional Architecture

The planned interactive page will be structured into five focused learning modules:

```
+-----------------------------------------------------------------------------------+
|  Tablet / Desktop Shell: Header, Breadcrumbs, Theme Toggle, Font Scale Controls   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Module 1: Exploded View 3D/Isometric Canvas ] [ Module 2: Parameter Controls ]  |
|  * Interactive Separation Slider (0 mm to 80 mm) * Radius r Slider (1.0 to 7.0 cm)|
|  * Cone lifts off Hemisphere                     * Height h Slider (4.0 to 20 cm) |
|  * Cyan: Cone CSA (Exposed)                      * Real-time Pythagoras readout:  |
|  * Amber: Hemisphere CSA (Exposed)                 l = sqrt(r^2 + h^2)            |
|  * Red Hatched: Hidden Joint (Zero Area!)                                         |
|                                                                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Module 3: "Paint the Solid" Surface Inventory Tool ]                           |
|  * Clickable 3D regions to apply virtual paint                                     |
|  * Cone curved wall: Paintable (Checked + adds pi*r*l)                            |
|  * Hemisphere curved wall: Paintable (Checked + adds 2*pi*r^2)                     |
|  * Flat mating disk: BLOCKED! Intercept banner explains: "Paint can't reach inside"|
|                                                                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Module 4: Dynamic Live Formula & Calculation Ledger ]                          |
|  * Step-by-step arithmetic updating instantly as sliders move                     |
|  * KaTeX algebraic breakdown: pi*r*(l + 2r)                                       |
|  * Toggle: Exact pi vs Decimal (pi = 22/7)                                        |
|                                                                                   |
+-----------------------------------------------------------------------------------+
|                                                                                   |
|  [ Module 5: Generalization Lab: "The Double-Face Subtraction Rule" ]             |
|  * Formula rule: Area = TSA_1 + TSA_2 - 2*(Contact Area)                          |
|  * Test on other composites: Cylinder + Cone (Pencil), Cylinder + 2 Hemi (Capsule)|
|                                                                                   |
+-----------------------------------------------------------------------------------+
|  Navigation Bar: [Back to Gateway] [Core 2 Practice] [Core 1A Construction Book]  |
+-----------------------------------------------------------------------------------+
```

---

### 5. Detailed Component Specifications

#### Module 1: Exploded View Interactive SVG Visualizer
- **Assembly / Separation Distance Slider ($\Delta y \in [0, 80\text{ mm}]$):**
  - At $\Delta y = 0\text{ mm}$ (Joined):
    - Cone base rests flush on hemisphere rim.
    - Outer boundary forms a continuous composite silhouette.
    - A dashed line indicates the internal interface with a label: *"Internal Interface: Hidden (Contribution = 0 cm²)"*.
  - At $\Delta y > 0\text{ mm}$ (Exploded):
    - Cone smoothly translates upward along the vertical axis.
    - The bottom base of the cone and the top base of the hemisphere tilt slightly into 2.5D perspective, revealing the two mating disks.
    - Cross-hatching pattern appears on both disks in muted red with cautionary callout: *"These surfaces disappear when pressed together!"*

#### Module 2: Geometric Parameter Sliders & Pythagorean Bridge
- **Radius Slider ($r$):** Range $1.0\text{ to }7.0\text{ cm}$ (step $0.5\text{ cm}$, default $3.5\text{ cm}$).
- **Cone Height Slider ($h$):** Range $4.0\text{ to }20.0\text{ cm}$ (step $0.5\text{ cm}$, default $12.0\text{ cm}$).
- **Dynamic Right-Triangle Overlay:**
  - An internal cross-section triangle is drawn inside the cone:
    - Horizontal leg: $r$
    - Vertical leg: $h$
    - Hypotenuse: $l$ highlighted in vivid gold.
  - Interactive formula card:
    $$l = \sqrt{r^2 + h^2} = \sqrt{3.5^2 + 12^2} = \sqrt{12.25 + 144} = \sqrt{156.25} = 12.5\text{ cm}$$

#### Module 3: "Paint the Toy" Diagnostic Game
- The learner is challenged: *"Select every surface that must be painted to cover the exterior of the toy."*
- Clickable target zones:
  - **Zone A (Cone Slanted Face):** Correct! Adds $\pi r l$ to inventory. Turns painted blue.
  - **Zone B (Hemisphere Dome):** Correct! Adds $2\pi r^2$ to inventory. Turns painted amber.
  - **Zone C (Cone Base Disk):** 🛑 **Diagnostic Trap Alert!**
    - Triggers interactive dialog:
      > *"Diagnostic Alert: In the assembled toy, this face is glued against the hemisphere. Can rain or paint touch it? No! It is inside the solid. Hidden faces do not contribute to exposed surface area."*
  - **Zone D (Hemisphere Flat Rim):** 🛑 **Diagnostic Trap Alert!** (Identical explanation).

#### Module 4: Live Dynamic Calculation Breakdown
- Updates synchronously with any slider or paint interaction.
- Displays full KaTeX working:
  $$\text{Cone CSA} = \pi \times 3.5 \times 12.5 = 43.75\pi \approx 137.5\text{ cm}^2$$
  $$\text{Hemisphere CSA} = 2\pi \times 3.5^2 = 24.5\pi \approx 77.0\text{ cm}^2$$
  $$\text{Total Exposed Area} = 43.75\pi + 24.5\pi = 68.25\pi = \frac{22}{7} \times 68.25 = 214.5\text{ cm}^2$$

#### Module 5: Generalization & Universal Law Explorer
- Demonstrates why the general formula holds for any two solid bodies $A$ and $B$ joined along matching interface area $A_{\text{joint}}$:
  $$\text{Exposed Area} = \text{TSA}_A + \text{TSA}_B - 2 \cdot A_{\text{joint}}$$
  - Explains the factor of $2$: Each solid previously contributed one face to its own TSA. Joining them eliminates both faces from the exterior.
  - For cone + hemisphere:
    $$(\pi r l + \pi r^2) + (3\pi r^2) - 2(\pi r^2) = \pi r l + 2\pi r^2$$

---

### 6. Technical, Conformance & Accessibility Architecture

1. **Standalone Conformance:**
   - Evaluated against [`Shared/tools/standalone_conformance.py`](file:///c:/Users/reall/Documents/antigravity/lively-goodall/Shared/tools/standalone_conformance.py).
   - Zero external scripts, fonts, or CDNs (`REMOTE_RUNTIME`).
   - Local KaTeX distribution (`../../vendor/katex/0.16.8/`).
2. **Typography & Legibility:**
   - Strict adherence to font floor: all font sizes $\ge 14\text{px}$ (`FONT_FLOOR`).
   - High contrast ratios (WCAG AAA compliant in both light and dark themes).
3. **Interactive Accessibility:**
   - All slider controls have visible numeric inputs and keyboard support (`ArrowLeft`, `ArrowRight`, `Home`, `End`).
   - Touch targets for all interactive zones, buttons, and slider thumbs are $\ge 48\text{px} \times 48\text{px}$.
   - Screen-reader accessible live regions (`aria-live="polite"`) announce updated surface area values and diagnostic alerts.

---

### 7. Implementation Roadmap & Milestones

| Stage | Activity | Deliverable |
| :---: | :--- | :--- |
| **Stage 1** | Mathematical & Vector Engine | SVG parametric renderer with slider-driven vertical translation ($\Delta y$) and cone/hemisphere mesh. |
| **Stage 2** | Pythagorean Auxiliary Bridge | Dynamic right-triangle overlay and live KaTeX square-root evaluation. |
| **Stage 3** | Diagnostic Misconception & Paint Module | Clickable surface detection, paint state management, and diagnostic trap alerts. |
| **Stage 4** | Universal Generalization Explorer | Interactive comparison between direct CSA addition and $2 \times A_{\text{joint}}$ subtraction. |
| **Stage 5** | Conformance Audit & Integration | Validation via `standalone_conformance.py`; linking from `index.html`, `core2.html`, and `core1a.html`. |
