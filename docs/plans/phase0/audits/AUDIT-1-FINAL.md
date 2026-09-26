# Audit 1 (final): academic completeness of the Motion-in-2D six-Core product

Issue: https://github.com/reallaksh19/Grade9V3/issues/296. Specimen:
`benchmarks/quality-calibration/specimens/S1-motion2d-six-core-html/`, from branch
`motion2d-six-core-20260926` at commit `d3fd51ab`. This is the audit record; nothing was
changed.

This pass completes the five items the first pass left open. It adds one finding, **A1-012**,
and extends **A1-001**.

## 1. Concept × Core completeness matrix

**Concepts**
- Canonical: R1 `2D-INDEPENDENT-COMPONENTS`, R2 `2D-CONSTANT-ACCELERATION`, R3 `PROJECTILE-MODEL`.
- Extensions: E1 `2D-VEL-FROM-POSITION`, E2 `PROJ-BOUNCE-ENERGY`, E3 `PROJ-PIECEWISE-G`,
  E4 `PROJ-TRAJECTORY-POINT`, E5 `2D-LINEAR-DRAG`.

Core2 is keyed by source question, not concept (see §2), and appears in §2 and §3.

**Status codes**
- **OK**: the learner-facing content materially meets the role.
- **THIN**: present but below the role or the reference.
- **MISSING**: a required block is absent.
- **WRONG_ROLE**: present but in the wrong interaction position.
- **—**: the role does not require this concept.

| Concept | Core1 | Core1A | Core1B | Core2A | Core2B |
|---|---|---|---|---|---|
| R1 | THIN (A1-001) | THIN (A1-002, A1-003) | THIN (A1-002 propagated) | — | — |
| R2 | THIN (A1-001) | THIN (A1-002) | THIN (A1-002 propagated) | — | — |
| R3 | THIN (A1-001) | THIN (A1-002, A1-004) | THIN (A1-002 propagated) | — | — |
| E1 | mapped only | THIN (A1-005: derivative) | OK | THIN (A1-007, 008, 009) | MISSING (A1-010), THIN (A1-011) |
| E2 | mapped only | THIN (A1-005: resolution) | OK | THIN (A1-007, 008, 009) | MISSING (A1-010), THIN (A1-011) |
| E3 | mapped only | OK | OK | THIN (A1-007, 008, 009) | MISSING (A1-010), THIN (A1-011) |
| E4 | mapped only | THIN (A1-005: resolution) | OK | THIN (A1-007, 008, 009) | MISSING (A1-010), THIN (A1-011) |
| E5 | mapped only | THIN (A1-005: exponential decay) | OK | THIN (A1-007, 008, 009) | MISSING (A1-010), THIN (A1-011) |

**What was measured**, per page (Core1A and Core1B have 8 articles each; Core2A and Core2B have 5):

| Page | What it contains |
|---|---|
| Core1 | 0 figures |
| Core1A | Canonical articles R1–R3: 0 figures. They print `Canonical representation: <id>` six times in all (1, 2 and 3 times). Extension articles: 1 figure each |
| Core1B | Canonical articles: 0 figures. Extension articles: 1 figure each |
| Core2A | 0 figures in any article |
| Core2B | 1 figure per article, inside the post-attempt disclosure |

Core1B scores OK for E1–E5 on content: predict, attempt, reconstruct and boundary test are all
present. Whether its reveal is actually gated is an interaction question and belongs to Audit 3
(A3-004).

## 2. Core2 source questions

| Source | Identity and custody | Answer position | Figures |
|---|---|---|---|
| JEE Main 2026 S2 04 Apr Shift 2 Q29 | OK | WRONG_ROLE (A1-006) | "None supplied" (A1-012); Conditions also "None supplied" |
| JEE Adv 2018 P2 Q8 (Q15 resolution) | OK: discriminator vs 2023 P1 Q1 kept | WRONG_ROLE (A1-006) | "None supplied" (A1-012) |
| JEE Adv 2022 P1 Q8 | OK | WRONG_ROLE (A1-006) | "None supplied" (A1-012) |
| JEE Adv 2026 P1 Q6 | OK | WRONG_ROLE (A1-006) | "None supplied" (A1-012) |
| JEE Adv 2025 P2 Q15 | OK | WRONG_ROLE (A1-006) | "None supplied" (A1-012) |
| JEE Adv 2023 P1 Q1 (retained alternative) | OK | WRONG_ROLE (A1-006) | "None supplied" (A1-012) |

## 3. Demand-family trace (teaching → reconstruction → supported practice → transfer)

| Family | Core1A teaching | Core1B reconstruction | Core2A practice | Core2B transfer | Break in the chain |
|---|---|---|---|---|---|
| E1 velocity direction from x(t), y(t) | figure, no derivative bridge | OK | prose only, generic scaffold | figure only after the attempt | The derivative meaning is never taught (A1-005). The learner meets it cold in Core2A and Core2B |
| E2 rebound with energy change | figure; KE→speed² step assumed | OK | prose only | figure only after the attempt | Speed-component resolution not bridged (A1-005) |
| E3 gravity changes after the apex | OK | OK | prose only | figure only after the attempt | Weakest link is Core2A: no stage-boundary figure (A1-007) |
| E4 trajectory through a point | figure; resolution assumed | OK | prose only | figure only after the attempt | Resolution not bridged (A1-005); no "mark P" figure (A1-007) |
| E5 linear drag | figure; exponential solution assumed | OK | prose only | figure only after the attempt | Exponential decay not bridged (A1-005); the heaviest mathematical jump has the least support |

Every family has the same pattern:
- Core1A and Core1B carry a figure.
- Core2A carries **none** (A1-007).
- Core2B shows its figure only **after** the learner commits (A1-010).

The learner therefore works both practice Cores without the representation that the teaching
Cores used.

## 4. Prerequisite closure for the default Grade-9 learner

A1-005 stands after the full pass. Four of the five admitted extensions (E1, E2, E4 and E5)
depend on a move the six-Core sequence never teaches:
- the meaning of a derivative;
- trigonometric resolution of a launch speed;
- following an exponential-decay solution.

No duty in the product's duty register (D1–D7) produces a prerequisite bridge.

## 5. Contract-mandated gaps and benchmark-quality gaps

**Basis codes**
- **CONTRACT**: a registered block or policy in `LEARNER-PRODUCT-TEMPLATES.md` or the role
  blueprint is unmet.
- **BENCHMARK**: the page meets the letter of the contract but falls short of the owner
  references (grammar recorded in `benchmarks/quality-calibration/manifest.v1.json`).

| Finding | Core | Severity | Basis | One line |
|---|---|---|---|---|
| A1-001 | Core1 | S2 | CONTRACT | No `governing_relations` / `compact_anchor` block. **Extended:** Core1 mounts no representation at all (0 figures), although the blueprint's orientation slot accepts `canonical_representation` |
| A1-002 | Core1A → 1B | S1 | CONTRACT + BENCHMARK | R1–R3 print representation ids instead of mounting figures; only the 5 extension figures render |
| A1-003 | Core1A | S2 | CONTRACT | "None supplied by the governed record" shown to the learner in place of independent checks |
| A1-004 | Core1A | S1 | BENCHMARK (+ CONTRACT on the worked anchor) | R3 compresses about 8 hard transitions into one construction; the worked anchor only exercises `a_x=0, a_y=-g` |
| A1-005 | Core1A/1B → 2A | S1 | BENCHMARK (academic sequencing; no contract block exists) | No prerequisite bridge for derivative, resolution or exponential decay |
| A1-006 | Core2 | S1 | CONTRACT | Answers and reasoning visible immediately; 0 attempt and 0 disclosure controls |
| A1-007 | Core2A | S1 | CONTRACT + BENCHMARK | 0 figures although every reasoning route binds a representation; `figure_refs: []` |
| A1-008 | Core2A | S1 | CONTRACT (progressive support) + BENCHMARK (H0–H4 ladder) | One identical generic scaffold and one identical failure signal across all 5 families |
| A1-009 | Core2A | S2 | CONTRACT | No learner-facing family or exposure closure before Core2B |
| A1-010 | Core2B | S1 | CONTRACT | No safe initial representation; figure only after the attempt |
| A1-011 | Core2B | S2 | CONTRACT | Lineage is listed as links; `lineage_continuity_check` absent |
| **A1-012** (new) | Core2 | S2 | CONTRACT | "Figures and captions: None supplied by the governed record" printed for all 6 source questions, and "Conditions: None supplied" for Q29. The learner sees an internal absence. Whether each original paper has a figure could not be checked against a pinned source here; the research library's QUESTION cards carry `has_figure` for that |

**Totals:** 12 findings (7 S1, 5 S2, no S0).
- By basis: 8 CONTRACT, 1 BENCHMARK, 3 both.
- These findings are the acceptance baseline: the Phase 4 rendered gate must fail specimen S1
  for every one (they are listed in the calibration manifest as `expected_findings`).

## Positive findings (unchanged from the first pass)

- All 8 governed concepts are present in Core1A and Core1B.
- Core1B follows PREDICT → ATTEMPT → RECONSTRUCT → BOUNDARY TEST.
- Five Core2A twins have complete routes, crux references and checks.
- All five Core2B tasks change the demand genuinely, and their protected DECIDE moves stay after the attempt.
- Q15 custody is clear; source and authored material are distinguishable.
