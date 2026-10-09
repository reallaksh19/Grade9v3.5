# IMO Grade 9 — independent Core conceptual review, Batch C: quantitative reasoning

**Status:** ACADEMIC_DESIGN_PROPOSAL / NOT_SOURCE_ACCEPTED / NOT_CORE_PRODUCT  
**Owner coordination:** [governing issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294)  
**Denominator:** 12 inventoried source positions out of **68**, plus seven separate authored practice questions outside that 68. These 12 positions occur in an analyst-defined **QUANT** grouping, not a claim that "Quantitative Aptitude" is an official SOF Mathematics Section-2 syllabus topic.  
**Evidence:** \`Mathematics/research/imo-g9-topic-browser.v1.json\` + prior agent-specific mathematical audits \`fullpaper-audit-b03.v1.json\`, \`fullpaper-audit-b04.v1.json\`, \`fullpaper-source-math-batch02.v1.json\`, \`seed/math_audit_batch01.json\` at base \`main@7ee763c2db61f228d8064cdaea8bc4bb47ab529e\`. Audits are existing **agent calculations**, not externally accepted keys, source item custody, peer academic review or publisher rights. Source facts below identify previously reported *mathematical decisions*, without reproducing original stems, figures or options.

## 1. Twelve positions, twelve accountable reasoning decisions

| Source position | Prior audit | Proposed decisive inference, tied to previous agent math | Conceptual repair family |
|---|---|---|---|
| 2023–24 Set A Q35 | B03-005 | Given a **final compounded amount**, invert the compound-growth multiplier to recover the original principal; rate and compounding periods must be stated | FIN-INTEREST / compound reverse |
| 2023–24 Set A Q36 | B03-006 | Workers' **work-per-day fractions add** when cooperating; completed-work time is reciprocal of joint rate | RATE-WORK / individual rates |
| 2023–24 Set A Q37 | B03-007 | Combine nested percentages **with the correct conditional denominator**, then find a complement within the requested population subgroup | DATA-CONDITIONAL / subgroup denominator |
| 2023–24 Set A Q39 | B03-009 | Oppositely moving trains' *relative speed* is the speed **sum**; passing/fully clearing requires **combined train lengths**, not just travel to first head alignment | MOTION-RELATIVE / train clearing |
| 2023–24 Set A Q42 | B03-011 | Convert calendar duration to **years** and solve \`A=P+Prt\` backwards for principal (simple interest, not compound) | FIN-INTEREST / simple reverse |
| 2023–24 Set A Q43 | B03-012 | Two ratios refer to **different time snapshots**; restore past-to-future time difference before cross-multiplying | TIME-AGE / shared shift |
| 2024–25 Set B Q19 | B02-007 | Given a **numerical equality** of interest-rate percentage and time-period values, preserve their different units while solving the positive root of a quadratic numeric relation | FIN-INTEREST / rate-term constraint |
| 2024–25 Set B Q43 | B03-016 | Infer **per-worker-type productivity** from two *different crew equations*, then form the new crew's weighted sum rate and inverse completion time | RATE-WORK / mixed inferred rates |
| 2025–26 Set A Q30 | B01-008 | A simple-interest observation identifies the annual **rate**; a separate investment then uses that rate under compounding, not the same SI amount | FIN-INTEREST / rate transfer |
| 2025–26 Set A Q38 | B04-003 | Equal work means invariant **workers × hours/day × days** under constant worker productivity, so infer missing workforce through inverse proportion | RATE-WORK / fixed workload |
| 2025–26 Set A Q39 | B01-014 | Changing capital investments across time segments require a **capital-month integral/sum** for each investor before allocating proportional profit | FIN-PARTNERSHIP / changing investments |
| 2025–26 Set A Q40 | B04-004 | Sequential percentage changes **multiply factors based on the current quantity**; an increase then decrease is not necessarily their arithmetic percentage difference | DATA-PERCENT / sequential multipliers |

**Current source disposition of all 12:** source-publisher component custody incomplete; original reuse rights unresolved; research links provisional; no original source Core2 admitted; no QRT acceptance; no canonical Core1A admission. The existing 68-position census and discrepancy register must not be overwritten by this design review.

## 2. Teaching architecture: distinct roots, not twelve cloned pages

- **FIN-INTEREST:** principal, amount, rate, time and compounding period; three genuinely distinct inference branches: invert SI, invert compound, and transfer a rate estimate from SI to a *separate* compound scenario. A rate–term *numerical equality* is a fourth constraint branch, not a physical unit equality.
- **RATE-WORK:** define work=rate×time with consistent units. Branches: sum independent workers' known fractional rates, infer different types' unknown rates from independent crew equations, and hold *total worker-hours* fixed under equal per-worker productivity.
- **DATA-CONDITIONAL:** choose the correct whole and correct subgroup denominator; complement belongs within the requested group.
- **MOTION-RELATIVE:** choose the reference frame and displacement needed for full clearing. This is **not** a work-rate question just because both contain speed=distance/time.
- **TIME-AGE:** apply identical time shifts to both people's ages before comparing ratios; difference invariant, ratio changes.
- **FIN-PARTNERSHIP:** integrate capital exposure over time (capital × duration), then distribute the profit proportionally; this is not ordinary compound interest.
- **DATA-PERCENT:** update multipliers, apply each percentage to its *then-current* base, and compare final to the original.

**Review priority:** The longer and representation-sensitive source cruxes are mixed-worker inferred rates (2024 B Q43), changing capital-month investments (2025 A Q39), two-time age ratio (2023 A Q43) and train full-clearance relative displacement (2023 A Q39). The exact intrinsic HARD/MEDIUM/EASY concept badges and question D-bands must be proposed through existing contracts and actual source difficulty evidence; none is assigned by this file.

## 3. Conceptual golden construction — work rates as dimensionally justified additive quantities

**Common invariant:** Work done by participant \(i\) over time \(t\) is \(w_i=r_i t\), so if work contributions are independent and measured in the same job units, \(W=t\sum_i n_i r_i\).

### 3A. Joint completion from known individual durations
- Declare a fixed, unit-sized job \(W=1\); if A finishes alone in \(a\) days, \(r_A=1/a\) job/day, similarly B. Their joint rate is \(1/a+1/b\), and time \(T=1/(1/a+1/b)\).
- **Authored anchor:** A needs 6 h alone, B 4 h alone. In each hour they finish \(1/6+1/4=5/12\) job, so together \(T=12/5=2.4\) h. Check \((12/5)(5/12)=1\).
- **Misconception:** Add durations (10 h) or average them (5 h) instead of adding rates. Diagnostic asks: *what fraction of the same job is produced in one hour?*
- **Representation:** A common time axis with separate shaded job fractions, labelled \(1/6\) and \(1/4\), joining to \(5/12\) per hour; words and units accompany symbols.
- **Independent exit:** Two people take 9 and 6 h independently. Together \(1/T=1/9+1/6=5/18\), hence \(T=18/5=3.6\) h. Require a one-job check.
- **Boundary:** They must work simultaneously at appropriately constant, noninterfering rates; breaks, fatigue or resource bottlenecks invalidate simple addition.

### 3B. Infer unknown worker-type rates before changing crew composition
- Source family differs from 3A: two crew configurations provide independent linear constraints. Let \(a,b\) denote **jobs per worker-day**, not days per job.
- **Authored anchor:** Crew I, with 2 A-workers + 2 B-workers, produces \(3/20\) job/day. Crew II, 3 A-workers + 2 B-workers, produces \(1/5\) job/day. Equations \(2a+2b=3/20\), \(3a+2b=1/5\). Subtract: \(a=1/20\), then \(b=1/40\). A new crew of 2 A + 4 B produces \(2/20+4/40=1/5\) job/day, hence takes **5 days**.
- **Diagnostic:** Reject the assertion that the number of workers alone determines rate without knowing each worker-type's per-day contribution. Subtract the two crew equations and explain what cancels.
- **Representation:** Row/column matrix (crew type, count of A, count of B, total daily work), with contributions explicitly labelled.
- **Independent exit:** Crew I: \(2a+b=1/5\) job/day. Crew II: \(a+2b=1/4\). Solve \(a=1/20,\ b=1/10\). New crew one A plus three B produces \(7/20\) job/day, so takes \(20/7\) days. Independently check both original crew rates.
- **Boundary:** Unknown productivity is uniquely identifiable only if crew configurations provide independent constraints; a pair of proportional equations is insufficient even if two observations were collected.

### 3C. Fixed-work labour-hour inverse proportion
- **Authored anchor:** 7 equally productive workers × 6 h/day × 4 days = **168 worker-hours**. If 8 people work 7 h/day, required days \(d=168/(8\cdot7)=3\).
- **Exit:** 6 workers × 5 h/day × 8 days =240 worker-hours. At 8 workers × 6 h/day, duration is \(240/48=5\) days.
- **Wrong path:** Holding days constant or adding worker counts to daily hours. The product \(Nhd\) is proportional to the *workload*, not to a person's rate.
- **Boundary:** This variant assumes all worker types are equally productive. If type A and type B differ, go to branch 3B; don't force an unweighted headcount model.

## 4. Golden construction — conditional percentages vs sequential percentage multipliers

### 4A. Denominator switching for nested subgroups
- If subgroup \(G\) is a fraction of the population \(N\), count \(N_G\) first. A within-\(G\) percentage multiplies \(N_G\), **not** the entire population a second time. A complement within group H uses denominator \(N_H\).
- **Authored anchor:** In a group of 100, 30 are in subgroup M. Of M, 60% satisfy condition P, so \(18\) satisfy P. Across all 100, 32 satisfy P. Thus 14 in the other subgroup H of 70 satisfy P; 56 of H do not, giving \(56/70=4/5\) of H. Track totals \(18+14=32\).
- **Diagnostic:** A percentage of all people and a percentage of *women/men/selected members* have different denominators. Ask the learner to write the base population before each multiplication.
- **Representation:** Partitioned frequency table with original population, within-group P count, within-group not-P count; every percentage labelled by its denominator.
- **Independent exit:** Of 200 participants, 25% belong to subgroup M; 40% of M have property P, while 30% of all participants have P. Find the fraction of subgroup H without P. Calculation: M=50, H=150; P in M=20, total P=60, P in H=40, not-P in H=110, fraction \(110/150=11/15\).
- **Boundary:** The groups must form the stated partition; unknown overlap cannot be silently treated as disjoint.

### 4B. Sequential percentages as multiplication
- **Authored anchor:** A price rises 35% then falls 20% from the *new* price. Final factor \(1.35\cdot0.80=1.08\), so net +8%, not +15%.
- **Exit:** An amount rises 50% then falls 20%. Final factor \(1.5\cdot0.8=1.2\), a +20% net change. Reverse-check a starting 100→150→120.
- **Wrong path:** Add signed percentages as though both refer to the same base. Diagnose by writing 100 as a test base and calculating each intermediate.
- **Boundary:** Percentage factors commute *as numerical products* when fixed fractions are applied sequentially, but a **fixed absolute change** or a percentage conditional on another evolving quantity changes the model. A +25% followed by -20% returns to the start (\(1.25\cdot0.80=1\)), which does **not** imply a general cancellation law.

## 5. Golden construction — finance: three different models and a shared unit contract

Declare principal \(P>0\), annual simple rate \(r\) as a **decimal fraction per year**, time \(t\) in years and interest \(I\). For annual compounding with annual rate \(r\), whole periods \(n\), use \(A=P(1+r)^n\). If rate is recorded as the **numeric percentage** \(R\), then \(r=R/100\). Do not conflate \(R\), \(r\), \(t\), \(I\), amount \(A\), or number of compounding periods.

### 5A. Simple-interest inverse
- \(\displaystyle A=P(1+rt)\), so \(\displaystyle P=A/(1+rt)\) where \(1+rt\ne0\).
- **Authored anchor:** Amount ₹1240 after 3 years at 8% *simple* interest: \(P=1240/(1+0.08\cdot3)=₹1000\).
- **Exit:** Amount ₹1430 after 3 years at 10% simple interest: \(P=1430/1.30=₹1100\), verify accrued ₹330.
- **Wrong path:** Divide by \((1+r)^t\) as though it compounded.

### 5B. Compound-interest inverse
- \(\displaystyle P=A/(1+r)^n\); annual compounding repeats the multiplier each year.
- **Authored anchor:** ₹1210 after two years of annual compound growth at 10%: \(P=1210/(1.1)^2=₹1000\). Check \(1000\times1.21=1210\).
- **Exit:** ₹1728 after three years at 20% compound interest: \(P=1728/(1.2)^3=₹1000\).
- **Boundary:** Fractional-year compounding conventions must be provided; do not assume that \(n\) can be a fractional exponent under an unstated contract.

### 5C. Transfer a rate observed under simple interest to a distinct compound scenario
- **Authored anchor:** ₹2400 earns ₹144 simple interest in 9 months. Annual rate \(r=144/(2400\cdot0.75)=0.08\), or 8%. A *separate* ₹5000 principal compounded annually for two years at that rate earns \(5000[(1.08)^2-1]=₹832\) compound interest.
- **Exit:** ₹3000 earns ₹180 simple interest in one year (6%); a separate ₹2000 compounded annually for two years earns \(2000[(1.06)^2-1]=₹247.20\).
- **Wrong path:** Carry the *₹144 interest amount* over to the new principal, rather than carrying the **annual rate**.
- **Boundary:** A named rate transfer is valid only under the problem's assertion that the rate is the same; SI and CI outcomes are not numerically equivalent over multiple periods.

### 5D. Numeric annual-rate equals numeric duration
- \(\displaystyle I/P=(R t)/100\), where \(R\) is the rate expressed as a *number of percent per year*, and \(t\) is years. A sentence saying the numerical values of rate and term are equal sets \(R=t\); it does **not** equate incompatible physical units.
- **Authored anchor:** Principal ₹2000 yields ₹180 simple interest, with \(R=t\) numerically. Then \(180/2000=R^2/100\Rightarrow R^2=9\Rightarrow R=3>0\). Rate 3% annually and term 3 years.
- **Exit:** Principal ₹2500, interest ₹400, numeric \(R=t\), solve \(R^2=16\), giving rate 4% annually and 4 years. Reject the negative root for a positive rate/duration.
- **Boundary:** Dimensional conventions and positivity are part of the reasoning, not an optional arithmetic detail.

## 6. Golden construction — moving trains need *full-clearance displacement*

- Choose a frame: two trains moving **toward** one another, with speeds \(u,v>0\). Relative closing speed is \(u+v\). For the **whole trains to clear each other** after their leading ends first meet, the relative displacement required is **combined lengths** \(L_1+L_2\); time \(t=(L_1+L_2)/(u+v)\) in consistent units.
- **Authored anchor:** Trains of lengths 90 m and 150 m approach at 45 km/h and 27 km/h. Relative speed \(72\ {\rm km/h}=20\ {\rm m/s}\). Combined clearance length \(240\ {\rm m}\), time \(12\ {\rm s}\).
- **Representation:** Position-versus-time strip with each train represented by a **finite segment**, not only a point, and arrows showing relative sliding of the full combined length. This diagram is pedagogically integral.
- **Wrong path:** Apply relative speed correctly but use only the longer train or head-to-head separation as the clearance distance. Another wrong path: mix km/h with metres without converting.
- **Exit:** Opposing trains of lengths 100 m and 125 m move at 60 km/h and 30 km/h. Relative speed \(90\ {\rm km/h}=25\ {\rm m/s}\), combined distance \(225\ {\rm m}\), time **9 seconds**. Verify \(25\cdot9=225\).
- **Boundary:** Same-direction overtaking uses \(|u-v|\), not \(u+v\); meeting *fronts* at a point is not the same as the tails fully clearing. The source audit B03-009 explicitly involves full clearance.

## 7. Golden construction — two-time age ratios with shared time

- **Crux:** A ratio of ages is *not invariant over time*, whereas the age **difference** is; both people progress by the same number of years. Carefully choose a reference epoch.
- **Authored anchor:** Two years ago A:B ages were 3:4. Four years from now they will be 4:5. Let their ages **two years ago** be \(3k\) and \(4k\); the latter reference time is six years later, so \((3k+6)/(4k+6)=4/5\), giving \(15k+30=16k+24\Rightarrow k=6\). Present ages A=20, B=26. Reverse-check: two years ago 18:24=3:4; four years hence 24:30=4:5.
- **Wrong path:** Use +4 rather than +6 to bridge the *two given epochs*; or preserve a ratio through time as though it were a difference.
- **Representation:** A two-person timeline with one reference origin, arrows labelled +2 to present and +4 to future, and a +6 span between observed ratio snapshots.
- **Exit:** One year ago A:B ages were 2:3; five years from now 3:4. Let one-year-ago ages \(2k,3k\). After six years \((2k+6)/(3k+6)=3/4\Rightarrow k=6\); present ages \(13,19\). Reverse-check past 12:18=2:3; future 18:24=3:4.
- **Boundary:** All modelled ages must be admissible and the timeline interpretation explicit; negative ages or impossible ratios require a model/source check, not a forced algebraic value.

## 8. Golden construction — capital-month sharing with investment changes

- **Crux:** Under an explicitly **time-weighted partnership** model, each participant's share is proportional to \(\sum_j C_{ij}\Delta t_j\), with capital \(C_{ij}\) held for duration \(\Delta t_j\). A single initial deposit does not represent changing capital across time.
- **Authored anchor:** Investor A contributes ₹2000 for 2 months then ₹3000 for the following 4 months: exposure \(2000\cdot2+3000\cdot4=16000\) rupee-months. B contributes ₹2500 for all 6 months: exposure \(2500\cdot6=15000\) rupee-months. Shares \(16:15\); on total profit ₹6200, A receives ₹3200 and B ₹3000. Check allocations sum to ₹6200.
- **Diagnostic:** A learner uses only final balances ₹3000:₹2500 and ignores duration. Ask which contribution was active for how long and why each interval must count.
- **Representation:** Time-segment table with each person's capital per interval, duration and weighted contribution. Add units (currency × months).
- **Exit:** A contributes ₹5000 for 3 months then ₹7000 for 3 months; B contributes ₹6000 continuously for six months. Exposures ₹36000 and ₹36000, thus equal shares; from ₹10000 profit, each receives ₹5000.
- **Boundary:** The time-weighted rule is a *stated contract*, not a universal corporate profit entitlement. Different agreements, losses, compounding, salary draws or start/end timing require revised assumptions. The audited source Q39 had multiple changing capital segments; a single-fixed-investment ratio is insufficient.

## 9. Core product design and evidence requirements

1. **Full source-denominator integrity:** every one of the 12 existing source IDs remains accounted for; these are **candidate** teaching links, never an eight/eleven/twelve-item product quota.
2. **Crux matches the actual problem:** For Q39 trains, meeting vs **fully clearing** is the key modelling decision; for Q37, choose the subgroup denominator; for Q43 mixed workers, infer per-type rates before combining; for Q39 partnership, time-varying exposures. Do not flatten into "proportions".
3. **Core1A meaning:** document \`microtopic.inferential_jump\`, entry assumptions, conventions, every \`teaching_path[].why_valid\`, bound representation bridge, credible error diagnosis and an independent answer/check. HARD teaching depth if later justified must survive Core1B reconstruction.
4. **Core2 protection:** preserve original source hints separately from pedagogical scaffolds. No pre-attempt reveal of the decisive move through overlays, hidden DOM, accessibility text or printable source question. Pedagogical disclosure is not secure cryptographic access control.
5. **Role progression:** authored same-family tasks in Core2A; *genuine changed-decision* tasks in Core2B. Simply swapping rupees, people or numbers is **not** transferable reasoning.
6. **Rights:** external links and archival custody do not establish permission to reproduce SOF paper items. Do not place source stems/options/images in rendered HTML/PDF absent explicit permissible display mode.
7. **Acceptance:** research PR #306 is independent academic **proposal** only. No canonical capability, QRT, source review signature, owner acceptance, engineering merge permission or learner publication follows from these computations.

### Questions for IMO producer to confirm against exact source component readback

- Q39 (trains): Is the required displacement defined by **full mutual crossing** rather than front alignment? The prior B03 audit says combined lengths.
- Q43 (mixed work): Are worker-type rates to be **solved from two crew observations**, or explicitly supplied? B03-016 says two independent equations.
- Q39 (partnership): Do capital amounts change by participant over separate intervals? B01-014 says yes.
- Q43 (ages): Which epochs do the printed ratios actually reference, and what is the exact interval between them?
- Q30 (SI-to-CI): Does the source ask for compound *interest* versus amount? Distinguish \(A\) from \(A-P\).
- B Q19: Is rate–duration equality stated numerically, and which units/positivity are explicit?

**Priority:** Start with one or two coherent high-value constructions (e.g. mixed-worker inference and capital-month allocation), while the full 12-position source-math and disposition crosswalk remains visible; do not silently create a QRT rating from this document.