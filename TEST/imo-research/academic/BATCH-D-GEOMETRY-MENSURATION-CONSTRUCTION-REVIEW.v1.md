# IMO Grade 9 — Independent Core conceptual review, Batch D (geometry and mensuration)

**Status:** PROVISIONAL ACADEMIC DESIGN / NOT PRINTED-SOURCE CERTIFICATION / NOT CORE ADMISSION  
**Coordination:** [governing issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294) is the only IMO agent instruction channel. This document in [draft PR #306](https://github.com/reallaksh19/Grade9v3.5/pull/306) is my source-safe academic review, not agent-produced source evidence.  
**Denominator:** 11 of 68 distinct inventoried original-paper positions: 6 \`MENSURATION\`, 5 \`TRIANGLES\`. Existing seven independently authored practice drafts remain a separate denominator.  
**Source basis:** \`Mathematics/research/imo-g9-topic-browser.v1.json\` + agent research audits B01, B02, B03, B04 and official organizer-sample pilot, at the earlier \`main@7ee763c2db61f228d8064cdaea8bc4bb47ab529e\`. This analysis does **not** quote original exam stems, options, diagrams or keys in full. All original paper source custody/reproduction rights remain ungranted; visibly checked sample figures are not permission to republish.

## 1. Full 11-position source-to-inference map

| Existing position | Prior math audit | Decisive inference *provisionally supported by the agent math evidence* | Teaching connection and explicit hold |
|---|---|---|---|
| 2023–24 A Q17 · MENSURATION | B01-001 | For cones **with equal base radii**, volume ratio reduces to height ratio; cancel the common \(\frac13\pi r^2\) factor | Cone area–volume relation. **Source conflict 002**: a printed distractor/compiled option differs; never normalize options |
| 2023–24 A Q34 · MENSURATION | B03-004 | Sphere's **surface area** scales as the square of radius, not linearly | Area-scale root with sphere formula as specific representation |
| 2023–24 A Q45 · MENSURATION | B01-003 | From rim circumference recover radius; choose **curved** (not total) hemispherical area; convert units of **area** before pricing | Formula selection + dimensional conversion + rate/cost chain |
| 2024–25 B Q29 · MENSURATION | B02-012 | The cone's curved surface area is \(\pi r\ell\), with **slant** height \(\ell\); combine two CSA ratios without replacing \(\ell\) by perpendicular height \(h\) | Surface area modelling and symbolic relation between two cones |
| 2025–26 A Q48 · MENSURATION | B04-010 | Verify **three different** solid-geometry claims independently: cone/cylinder equal-volume height, 3:4 radius-to-height to 5-part slant, and a sphere inscribed in a cube | A cluster of independent solid models, not one forced generic formula lesson |
| 2026–27 organizer sample Q8 · MENSURATION | Sample Q8 | Distinguish the **ground footprint (cone base area)** from enclosed **air volume**; infer cone height via \(\frac13Bh=V\) | Two physical quantities to two different geometric measures; sample key sighted, not accepted |
| 2023–24 A Q29 · TRIANGLES | B02-006 | Recognize that the given sides form a **right triangle** and use either the right-triangle area or justified Heron; infer altitude from **area expressed with the requested base** | Earlier taxonomy says Heron, but the *decisive calculation* in B02 is right-angle recognition and area–altitude conversion |
| 2023–24 A Q49 · TRIANGLES | B03-014 | Evaluate two specific claims independently: a scale factor of 2 multiplies area by 4 (**300% increase**), while altitude to the hypotenuse follows the base–area identity, not a guessed height | Triangle-area square-law vs right-triangle alternate-base height; no assumption that these claims are globally quantified theorems |
| 2024–25 B Q35 · TRIANGLES | B02-015 | Infer three side lengths **from linked constraints**, verify triangle inequalities, then compute semiperimeter and Heron radicand exactly | Unlike 2023 Q29, the side-constraint setup is part of the protected inference |
| 2025–26 A Q34 · TRIANGLES | B01-012 | Uniform **linear** similarity scaling multiplies triangle area by square of the factor (rather than the same linear factor) | Share a dimensional-scale *principle* with sphere surface Q34, but maintain distinct objects and data |
| 2026–27 organizer sample Q10 · TRIANGLES | Sample Q10 | Test a bundle of **different** triangle statements: equal corresponding angles imply similarity, not necessarily congruence; median divides a triangle into equal areas; geometry claims requiring the source figure need actual figure constraints | Independent conceptual branches. **Figure-dependent**; no source diagram reuse absent permissible rights and complete components |

All 11 have a provisional academic inference and remain **research-only**. No inferred “agent math result” is an independent official key, and no position may be counted as an admitted Core2 product or approved Core1A module.

## 2. Concept architecture: six roots, not eleven required lessons

1. **Dimensional scaling:** under a linear factor \(k\), lengths multiply by \(k\), areas by \(k^2\), and volumes by \(k^3\), for geometrically similar objects. This principle **does not** apply if only some dimensions change.
2. **Solid measurement and dimensions:** cone volume \(\frac13\pi r^2 h\), cone CSA \(\pi r\ell\), sphere surface area \(4\pi r^2\), hemisphere curved area \(2\pi r^2\), cylinder volume \(\pi r^2 h\), and sphere-in-cube diameter relation. Each formula belongs to a specific measured object.
3. **Geometric models from physical quantities:** distinguish footprint, volume, painted surface, cost-per-area, and capacity before choosing a formula. Geometric units and practical restrictions matter.
4. **Triangle area with a chosen base:** \(\frac12bh\) where the height is perpendicular to the *selected base*, independent of the triangle's visual orientation; obtain area via perpendicular sides, Heron, or other warranted methods.
5. **Constraints before geometric calculation:** resolve unknown side lengths/perimeter, check triangle existence, then apply Heron's formula. This is more than a formula recall task.
6. **Similarity, congruence, and statement warrants:** equal corresponding angles show similarity in triangles, while congruence requires size agreement; equal-area median reasoning requires common altitude or shared-base/area arguments; figure-dependent claims are not interchangeable with a diagram-free statement.

Do not claim a teaching connection based solely on the generic topic name “mensuration” or “triangles.” A candidate Core1A unit must demonstrate the actual inferential gap and an authored independent exit.

## 3. Golden construction — what dimension is being scaled?

**Central inference:** Write the changed *linear quantities* first; only then deduce how the desired measured quantity transforms. \(A\propto r^2\), \(V\propto r^3\) only under correct shape and scale assumptions.

- **Authored worked anchor:** A sphere with radius 3 cm becomes a sphere with radius 9 cm. The radius factor is \(k=3\); surface-area ratio new:old is \(9:1\) because \(4\pi(9)^2/[4\pi(3)^2]=9\). Volume ratio is \(27:1\) because \(\frac43\pi9^3/[\frac43\pi3^3]=27\). A percentage **increase** of area is \((9-1)100\%=800\%\), not 900%.
- **Representation:** Three aligned length/area/volume columns, factor \(k,k^2,k^3\) and correctly labelled units. A figure is meaningful only if the scaling of *all corresponding lengths* is shown.
- **Wrong path:** “Radius triples, so sphere area triples,” or “four times the area is a 400% *increase*.” **Diagnostic:** Start with a unit radius and count the old-area unit before computing percent gain.
- **Independent exit:** A geometrically similar triangle's side lengths all grow by factor 4. Its area grows by **16**, and its percentage area increase is **1500%**. Explain \(16-1=15\) old-area units.
- **Boundary:** Raising only a cone's height by factor \(4\) with unchanged radius multiplies cone volume by \(4\), **not** \(4^3\). Raising both radius and height by \(4\) multiplies it by \(4^3=64\). This boundary separates source Q17 from a blanket similarity claim.
- **Source alignment:** sphere Q34 and triangle Q34 share a valid area-square principle; triangle Q49 adds the nontrivial distinction between ratio/new area and **percentage increase**, so they are not automatically the same lesson variant.

## 4. Golden construction — two independent cone models: volume vs curved surface

### 4A. Equal-radius cone volumes and interpreting air-space models

If two cones have equal radii, \(V_1/V_2=h_1/h_2\). If the radii differ, \(V_1/V_2=(r_1^2h_1)/(r_2^2h_2)\). Cancel a dimension only when it is genuinely common.

- **Authored anchor:** Two cones share base radius 5 cm; their heights are 6 and 15 cm. Their volume ratio is \(6:15=2:5\), even without evaluating \(\pi\). **Diagnostic:** If one cone radius is doubled but height unchanged, why does its volume quadruple rather than double?
- **Independent exit:** With equal radii, cone 1 height 8 cm and volume \(160\ \mathrm{cm}^3\), cone 2 height 14 cm; find volume \(160(14/8)=280\ \mathrm{cm}^3\). If the radius is not common, this inference is invalid.
- **Physical measurement bridge:** A cone-shaped shelter housing eight people provides **2 square metres of base footprint** and **12 cubic metres of air** per person. Then base area \(B=16\ \mathrm{m}^2\); enclosed air volume \(V=96\ \mathrm{m}^3\); cone height \(h=3V/B=18\ \mathrm m\). Distinguish *area/person* from *volume/person*.
- **Independent physical exit:** Five occupants need base footprint \(3\ \mathrm{m}^2\) each and air \(12\ \mathrm{m}^3\) each. Base \(B=15\), volume \(V=60\), so \(h=12\ \mathrm m\).
- **Boundaries:** This mathematical calculation assumes the cone's full volume is available air and the full base region is usable footprint. Actual structural thickness, occupied volume, ventilation and floor plan may change that model. It is an authored model, not practical design advice.

### 4B. Cone curved surface area ratios require *slant* height

For cones, curved surface area \(S=\pi r\ell\), where \(\ell=\sqrt{r^2+h^2}\) in a right circular cone. Radius and slant height, **not radius and perpendicular height**, appear in \(S\).

- **Authored anchor:** Cone 1's curved area is triple cone 2's; cone 2's slant height is twice cone 1's. Then \(r_1\ell_1=3r_2\ell_2=6r_2\ell_1\), so \(r_1:r_2=6:1\). No perpendicular-height equation is justified by these facts alone.
- **Wrong path:** Replace \(\ell\) by \(h\) merely because both are called "height." **Diagnostic:** On a labelled right-cone diagram, mark radius, vertical height, and surface generator separately.
- **Independent exit:** If \(S_1=2S_2\) and \(\ell_2=3\ell_1\), infer \(r_1:r_2=6:1\). Demand a reverse check with positive example measurements.
- **Boundary:** Do not confuse curved surface with total cone surface \(\pi r\ell+\pi r^2\); total area does not allow the same cancellation.

## 5. Golden construction — hemisphere area, circumference, unit price

**Protected modelling sequence:** rim circumference \(\rightarrow\) radius \(\rightarrow\) **hemisphere curved** surface area \(\rightarrow\) area-unit conversion \(\rightarrow\) cost-per-unit. Length and area conversions have different scale factors.

- **Authored anchor:** A hemispherical cover has circular rim circumference **44 m**, with \(\pi=22/7\). From \(2\pi r=44\), \(r=7\ \mathrm m\). Curved area \(2\pi r^2=308\ \mathrm{m}^2\). Convert to \(3{,}080{,}000\ \mathrm{cm}^2\). At ₹5 per \(100\ \mathrm{cm}^2\), cost \(3{,}080{,}000/100\cdot5=₹154{,}000\).
- **Representation:** An annotated unit ladder showing \(1\ \mathrm m=100\ \mathrm{cm}\) but \(1\ \mathrm{m}^2=10{,}000\ \mathrm{cm}^2\). Highlight *curved only* versus adding the base circular disk.
- **Wrong path:** Convert 308 square metres to 30,800 square centimetres by multiplying by 100; another is charge for \(3\pi r^2\) without evidence that the flat circular base is coated.
- **Independent exit:** Rim circumference **22 m**, \(\pi=22/7\), coating costs ₹2 per \(100\ \mathrm{cm}^2\). Radius 3.5 m; curved area 77 \(\mathrm{m}^2=770{,}000\ \mathrm{cm}^2\); final cost **₹15,400**.
- **Boundary:** If *total* hemispherical surface (including the circular face) is painted, use \(3\pi r^2\) instead of \(2\pi r^2\). Source component review is needed to know the actual paint surface.

## 6. Golden construction — triangle sides, chosen altitude, and Heron

There are **two source-facing branches** here.

**Branch A — known right-triangle sides then alternate-base altitude (2023 A Q29):** Recognize the right angle through a squared-side relation or provided geometry, get area from the perpendicular sides, and for a requested base \(b\) compute its own height as \(2A/b\). **Authored anchor:** Right triangle with perpendicular sides 9 and 12 cm, hypotenuse 15 cm. Area \(A=54\ \mathrm{cm}^2\); altitude to hypotenuse \(h=2\cdot54/15=7.2\ \mathrm{cm}\). If one mistakenly uses a 12-cm leg as the altitude to hypotenuse, the area would be wrong. **Exit:** Right triangle with legs 5 and 12, hypotenuse 13: area 30, height to hypotenuse \(h=60/13\ \mathrm{cm}\). Verify \(13h/2=30\). Heron's formula can provide an independent cross-check, but need not be the decisive method.

**Branch B — side constraints before Heron (2024 B Q35):** First represent unknown sides and the perimeter, enforce triangle inequality, then compute semiperimeter \(s\) and Heron's \(A=\sqrt{s(s-a)(s-b)(s-c)}\).

- **Authored anchor:** Three consecutive integer sides have perimeter 42 cm. Let them \(x,x+1,x+2\); \(3x+3=42\Rightarrow x=13\); sides \(13,14,15\) obey triangle inequality. Then \(s=21\), area \(\sqrt{21\cdot8\cdot7\cdot6}=\sqrt{7056}=84\ \mathrm{cm}^2\). Requested altitude to 14-cm side would be \(2\cdot84/14=12\ \mathrm{cm}\).
- **Wrong path:** Apply Heron's with parameter \(x\) still unresolved or fail to check triangle existence. **Diagnostic:** Sides 2,3,6 cannot form a triangle although an algebraic expression might be written.
- **Independent exit:** Sides \(x,x+2,x+4\) have perimeter 36. Then \(3x+6=36\Rightarrow x=10\); sides \(10,12,14\); \(s=18\); area \(\sqrt{18\cdot8\cdot6\cdot4}=\sqrt{3456}=24\sqrt6\ \mathrm{cm}^2\). Check that triangle inequalities hold.
- **Representation:** Triangle with *chosen* base and its perpendicular altitude; separate a table computing all \((s-a),(s-b),(s-c)\). A geometric picture needs correct side labels; not an arbitrary unsourced diagram.

## 7. Golden construction — solid-geometry assertion bundle

**Source family (2025 A Q48):** Different claims need different representations and proofs; no rule permits transferring a cone model blindly to a sphere-in-cube claim.

- **Authored claim A:** A cylinder of radius 3 cm and height 8 cm has the same volume as a cone of radius 6 cm and height 6 cm. Both are \(72\pi\ \mathrm{cm}^3\); **TRUE**.
- **Authored claim B:** A right circular cone with \(r:h=3:4\) and volume \(96\pi\ \mathrm{cm}^3\) has slant height 10 cm. Let \(r=3k,h=4k,\ell=5k\). Volume \(12\pi k^3=96\pi\Rightarrow k=2\Rightarrow\ell=10\); **TRUE**.
- **Authored claim C:** A sphere inscribed in a cube of side 12 cm has volume \(576\pi\ \mathrm{cm}^3\). Its radius is \(12/2=6\) cm; volume \((4/3)\pi6^3=288\pi\), so **FALSE**.
- **Wrong path:** Confuse an inscribed sphere's radius with cube side, or assume a formula from a preceding claim applies to the next object.
- **Independent exit:** In a cube of side 9 cm, the maximal inscribed sphere has \(r=4.5\) cm and volume \( (4/3)\pi(4.5)^3=121.5\pi\ \mathrm{cm}^3\). A claim of \(243\pi\) is false. Require the diameter-equals-cube-edge geometric justification.
- **Boundary:** Each individual statement's assumed geometry must be supplied; an inscribed sphere is tangent to the cube's faces when maximally inscribed. If not specified as maximal, a smaller sphere could also lie inside the cube.

## 8. Golden construction — similarity is not congruence; median equal-area logic

**Source-facing sample Q10:** An angle-angle-angle argument in triangles supports **similarity**, not size equality. Separate statements that invoke a median and altitudes may need the actual figure's labels and incidence; we do not copy it.

- **Authored anchor for AAA limitation:** A triangle with sides 3,4,5 and one with sides 6,8,10 have equal corresponding angles and ratio 1:2, but their corresponding sides are not equal; they are **similar but not congruent**. Misconception: "all equal angles imply congruent" (valid for shape, not size).
- **Authored median-area demonstration:** In triangle PQR, M is the midpoint of QR. Triangle PQM and PMR have bases QM=MR and **the same altitude from P to line QR**, so equal areas. Conversely, measured against the common base PM, equality of areas implies equal perpendicular distances from Q and R to line PM, provided each is correctly interpreted as altitude to that line. This second step requires a bound labelled geometric representation, not just a diagram assertion.
- **Wrong path:** Assume a median creates two congruent triangles (not generally true) simply because it bisects the opposite side. Equal **area** does not imply all corresponding sides/angles are equal.
- **Independent exit:** Two triangles share a 10-cm base and each has altitude 7 cm to the base line. They have equal area 35 \(\mathrm{cm}^2\), yet need not be congruent. Produce two apex locations with same distance from base line but different horizontal positions; the side lengths will generally differ.
- **Boundary:** AA/AAA sufficiency is triangle-specific; arbitrary polygons do not share this congruence/similarity shortcut. If exact sample source figure requires specific collinearity, parallelism or perpendicular feet, do not infer them from this generic authored model.

## 9. Source and Core product review contract

For any of these 11 original items, require:
- An exact recorded source ID, printed locator, figure-dependency state, rights/custody state, and previous agent math-audit reference. Keep **source conflict 002** as an unchanged editorial record.
- A **mathematical model selection** justified by actual wording/figure (CSA vs total area; hemisphere curve vs total; footprint vs air; similar vs congruent; one altitude for each base). Treat mismatches as source-to-teaching objections, not merely algebra mistakes.
- Any associated Core1A construction must document prerequisites, decisive inference, correct representations, mathematical explanation \`why_valid\`, predicted misconception as *unobserved learner hypothesis*, independent exit and explicit boundary. Actual Core1B and Core2A/B contracts are not populated merely by writing these words.
- A Core2 original source product is **not** rendered, admitted or licensed by this note. Original question text, option order and source figures stay out of learner outputs without permitted rights and durable complete component readback; source URL remains reference-only.
- Distinguish source-paper pages seen in an online viewer from retained, verified original PDF bytes, and distinguish previous agent calculations from independently accepted academic review.
- No forced Core1A lesson-per-question ratio or QRT classification quota. Appropriate response to a low-inference arithmetic item may be a brief repair rather than a heavy scene.

**Specific questions to the IMO producer, answered only on [#294](https://github.com/reallaksh19/Grade9v3.5/issues/294):** (1) Q29 TRIANGLES 2023–24 A: confirm right-triangle recognition, not Heron's, is the decisive source math; (2) Q49 TRIANGLES 2023–24 A: ensure area ratio 4 means **300% increase**, and the alternate-base height is \(60/13\), not 60; (3) 2025–26 A Q48: verify original three object models without importing my authored numbers; (4) sample Q10: identify exact figure relations genuinely needed for median/equal-height deductions; (5) source conflict 002: confirm it is about printed answer-option mismatch, not a changed cone-volume stem.

**Disposition:** This file is an authored, falsifiable Core teaching design proposal covering 11 source positions. It grants **zero** source Core2 eligibility, rights, canonical admission, QRT acceptance, academic owner sign-off, or publication.
