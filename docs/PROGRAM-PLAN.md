# Grade9V3 program plan

> **Authority / status:** Product/architecture programme context — not the live V2.5 execution roadmap. Its phase/status tables preserve the programme state and decisions established when this plan was authored; they are context, not a second current-state store.
>
> **Current engineering execution authority:** start at [`../agents/relay/REPO_STATE.yaml`](../agents/relay/REPO_STATE.yaml), then follow its [current V2.5 roadmap](../agents/relay/roadmap/OVERALL_ROADMAP.yaml), [progress source](../agents/relay/roadmap/PROGRESS.yaml), and `active_ep.path`. Do not execute work from this document merely because it contains a phase or task sequence.

Scope: **Physics, Mathematics and Chemistry**, **CBSE grades 9–11**, six learner products per subtopic bucket, with a front-end topic library and run builder.

This plan extends the R0–R7 roadmap in the V3B core system guide (`reallaksh19/Common`, PR #364) rather than replacing it; the R-stage each phase serves is named in the table below.

## Settled decisions

| # | Decision | Resolution |
|---|---|---|
| 1 | Repository and paths | New repository `reallaksh19/Grade9V3`. Greenfield — grade is carried as data, not as a directory name, so `Grade 9/V3B/...` path baggage does not follow. |
| 2 | Knowledge layering | **Two layers.** Technical engineering gates are upstream authority (what the science requires); the microtopic library is downstream teaching substance (how a transition is taught). They bind to each other; neither absorbs the other. |
| 3 | Six-Core for all subjects | **All three subjects adopt six-Core now.** Mathematics and Chemistry previously declared only CORE1/CORE2/CORE1A/CORE2A; CORE1B and CORE2B are new obligations for them. |
| 4 | Front-end order | Topic library browser first, run builder second. |

## The governing constraint

Subject and topic variation is **governed data**, never a branch in engine code. `Shared/` must work for all three subjects without knowing which one it is running for. This is enforced automatically by `Shared/tools/topic_independence_guard.py`, which exists because the parallel Physics track (`Common` PR #350) accumulated roughly eight hardcoded `PHY-M2D` literals in engine code — the failure this repository is structured to avoid.

## Phases

| Phase | Deliverable | Exit evidence | R-stage | Status |
|---|---|---|---|---|
| **P0** Foundations | Six-Core role specs (subject-neutral); all three subject contracts promoted to six-Core; topic independence guard + CI; this plan | Guard self-test detects a planted violation; three contracts parse and declare six products | R1 tail | **done** |
| **P1** Subject-neutral core | Port the proven publication host into `Shared/`, splitting the subject-specific parts into adapters: result shapes, comparison rules, units, representation kinds | The existing relative-motion run re-publishes through the refactored path with equivalent basis semantics; guard scans a non-trivial file count | R1 | **done** (byte-identical, see below) |
| **P2** Technical gate layer | Subject-neutral 16-point gate schema + validator + mutation falsifiers; Physics gate data; curriculum-scope binding registry | Gate DAG closed and acyclic; every falsifier caught; a scope claim without an exact binding reports `HELD`, not assumed authority | R2 | **done** (registry is partial by intent, see below) |
| **P3** Executable topic library | Library engine: intake validation, reference resolution, prerequisite closure, slice retrieval, `CANDIDATE → REVIEWED → CURATED` promotion. Publication consumes library packets | A bucket compiles from the library and publishes end-to-end with no hand-maintained lesson side-channel | R2/R3 | **done** (three of four products, see below) |
| **P4** Front end | Topic library browser; run builder emitting both the run config and the publication input triple; unified portal; deterministic architecture manifest with CI drift check | Static and offline-safe, no build step; manifest check green; builder fixtures validate | R2/R3 | **done** |
| **P5** Mathematics adapter | Exact-rational verification path, geometric construction and function-plot representations, proof obligations, Math gate data | One end-to-end Mathematics slice passing its own scientific and final-medium review | R5 | **machine checks done; review not run** |
| **P6** Chemistry adapter | Species/charge/phase/condition authority, conservation checks, particle–symbolic–macroscopic representation triplet, Chemistry gate data | One end-to-end Chemistry slice; study depth follows intrinsic badge, not readiness | R6 | owner-gated |

**P5 and P6 do not start until the owner accepts the Physics result.** That stop point is inherited from the V3B pending-activity handover. P5 was authorised by the owner directly; **that authorisation covers building the Mathematics adapter, not acceptance of the Physics content**, which remains machine-verified only, unmerged and unreviewed. P6 is still gated.

## What P1 must solve

Porting the publication host is not a file move. The three subjects return fundamentally different verification results:

| Subject | Result shape | Comparison |
|---|---|---|
| Physics | Scalar with a unit (plus one structured apex state) | Relative/absolute tolerance 1e-9 |
| Mathematics | Exact rational, or a rational coefficient list | Exact equality — a tolerance would silently accept a wrong exact answer |
| Chemistry | Element-count map, conservation ledger, extent map | Exact integer map equality |

The current engine hardcodes scalar-with-unit comparison and carries a Physics units table (`RESULT_UNITS`) inside shared code. P1 moves result shape, comparison rule and units into `validator_catalogue` in each subject adapter — already declared in P0 — so the shared engine compares what the adapter tells it to compare.

## What P2 and P3 actually established

**The gate registry is deliberately partial.** Six Physics gates cover the buckets this repository has authored, every one declared `OWNER_EXTENSION` against an empty binding set — because no exact CBSE binding for quantitative two-dimensional relative velocity at grade 9 has been established. The full grades 9–11 registry across three subjects is bulk authoring, and the V3B core system guide warns that building a large registry before proving its consumer risks another schema-only success. The machinery is proven against real content first.

**The library was not executable, and making it so required schema work.** Three things a publication needs had no home in the package schema, so they lived in a build script beside the lesson:

| Missing | Added | Why it mattered |
|---|---|---|
| Quantitative values | `data` collection of typed datum records | The numbers a lesson uses had no governed origin or provenance |
| Renderable equation form | `relation.mathml` | A product could not display a relation without re-authoring it |
| Machine-checkable answers | `question.verification` and `answer.numeric` | "magnitude 10 m/s" sat in prose; the oracle could not reach it |

With those, `BUCKET-RELATIVE-MOTION` compiles from the library and publishes end-to-end, its one numeric answer checked against the real Physics evaluator.

**Compilation stops where authoring begins, and says so.** The compiler derives buckets, obligations, atoms, questions and per-core coverage, and carries the library's own authored prose — teaching-path steps with their justifications, misconception repairs, exit tasks with answers — through verbatim. It does not synthesise teaching prose from graph records: that would manufacture exactly the plausible titles concealing missing reasoning the library exists to prevent. What remains is emitted as explicit authoring requirements rather than invented:

- **Core2B is reported unsupported** for this bucket — the library holds no question exposed to it. The compiler omits the product rather than padding it.
- Connecting narrative beyond what the library holds is declared as required authoring.

## What P5 proved, and what it changed

The Mathematics slice (`BUCKET-LINEAR-EQUATION`, solving `3x + 2 = 9` over the rationals) exists to test the P1 seam against a result shape the engine was never built for. It is not decoration: `2.333333333333` is within the Physics tolerance of `7/3` and is not a solution, so an engine that quietly reused the tolerance path would publish a wrong answer with a verification stamp on it. The run compares under `EXACT_RATIONAL_EQUALITY`, and `tests/test_mathematics.py` fails if that ever degrades.

Carrying a second subject forced four changes, each general rather than per-subject:

| Found | Changed | Scope |
|---|---|---|
| `EXACT_RATIONAL` results were declared unpublishable, so Mathematics could not publish at all | Added to `PUBLISHABLE_SHAPES`; the engine records the declared comparison in evidence and re-applies it on read-back | Engine |
| Preconditions like `domain: RATIONAL` had nowhere to travel — the engine enumerated the keys it would pass to a validator | The engine now passes through whatever preconditions a subject declares, and the package schema stops enumerating them too | Engine + schema |
| A source atom had to be an `int` or `float`, so an exact solution could only be stored rounded — destroying the distinction before anything could check it | `numeric_atom` returns a `Fraction` for an exactly-recorded atom; a decimal written as a string is refused, because that is a rounded value claiming to be exact | Engine |
| Every run reported `FIGURE_AUTHORING` unconditionally: a representation record could state what a figure must show but could not hold one | Representations carry `scene_instances`; the compiler emits figure blocks from them, bound to the microtopic's obligation, and reports authoring outstanding only for a representation that genuinely holds none | Schema + compiler |

Two smaller defects surfaced through the same slice and were fixed globally: authored fragments were being joined with an unconditional full stop (published `over the rationals..`), and the architecture manifest hashed a file a second tool generated, so the two artifacts could only be regenerated in one undocumented order. `build_manifest.py` now regenerates that file itself.

**Unlike the Physics run, no Mathematics publication is committed.** The Physics publication is frozen as the port oracle and guarded byte-for-byte. Mathematics compiles from its library packages on demand, and the tests do exactly that — a committed copy would be a second drift surface guarding nothing.

Still outstanding in Mathematics, recorded rather than worked around: `POLYNOMIAL_VALUE` and `POLYNOMIAL_FROM_ROOTS` take coefficient *lists*, and the engine binds one datum per variable (`ISS-MATH-LIST-BINDING`); Core2B has no exposed question; and `MIC-MATH-EXACT-SOLUTION` is the only microtopic with a drawn figure.

## Adapted from the parallel tracks

Both parallel tracks live in `reallaksh19/Common` and continue independently. Nothing is copied wholesale; what is taken is the design, re-implemented here.

| Source | Adapted | Deliberately not taken |
|---|---|---|
| PR #395 (Mathematics) | Subtopic-intelligence intake validation and `CANDIDATE → REVIEWED → CURATED` promotion (P3); run builder pattern (P4); architecture manifest with CI drift check (P4); topic independence guarding (P0) | Its schemas — the V3B microtopic library schema is richer and stays. Its discovery-benchmark corpus, until there is enough library content for discovery to be a real problem |
| PR #350 / #383 (Physics) | The 16-point gate contract as a subject-neutral data model (P2); curriculum-scope binding with fail-closed unbound state (P2); authority delegation boundary; `NOT_AUTHORIZED` as a state distinct from `HELD` and `BLOCKED` | Its hardcoded topic literals in engine code — the P0 guard exists to prevent repeating them |

## Scale

Roughly 40 subtopics per subject per band gives **120–150 gates** across three subjects and grades 9–11; at three to six microtopics per gate, **400–900 microtopics**; then six products per bucket.

P0–P4 is bounded architecture work. Everything past it is a **production programme**, not a plan step — which is precisely why P3 and P4 matter: the library and the run builder are what make per-bucket authoring repeatable instead of bespoke. No schedule is promised here; sequencing depends on measured cost per accepted bucket from the first library-driven runs.

## Standing non-claims

Nothing in this repository claims independent academic review, pedagogical acceptance, curriculum authority, measured learner fit, or learner release. Machine checks establish structure, custody and supported computation. They do not establish that an explanation teaches.