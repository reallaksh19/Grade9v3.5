# Execution plan: R3 and R4

> **Authority / status:** Historical execution plan. This records the R3–R4 execution reasoning and measured reorderings from that stage. It is retained for engineering provenance, not as a current task package.
>
> **Current engineering execution authority:** start at [`../agents/relay/REPO_STATE.yaml`](../agents/relay/REPO_STATE.yaml), then follow its [current V2.5 roadmap](../agents/relay/roadmap/OVERALL_ROADMAP.yaml), [progress source](../agents/relay/roadmap/PROGRESS.yaml), and `active_ep.path`. Do not execute work from this document merely because it contains a phase or task sequence.

Written after R0–R2 landed, and after two measurements that reorder what the roadmap said to do next. The roadmap's R3 list was drawn up before R1's schema work and before R3.0's depiction audit; both changed what is buildable.

## Two findings that reorder the batch

### The roadmap's first renderer cannot be built honestly

R3 says `FREE_BODY_DIAGRAM` first, and states the rule every renderer follows: *proven by a scene instance compiled from a library record — never by a hand-authored plan.*

Physics' library holds no force content. `force`, `newton`, `friction` and `normal` return zero hits; the 72 hits for `tension` are all the word `extensions`. A `FREE_BODY_DIAGRAM` built now could only be proven against a fixture, which that rule forbids. It is blocked on content, not on effort, and moves behind the import.

`VECTOR_SUBTRACTION` takes its place. Two library representations declare it, in a bucket that compiles, with three `FIGURE_AUTHORING` requirements pointing at it — and R3's own exit evidence is *"`FIGURE_AUTHORING` count for Physics drops from three to zero"*, which only this renderer can achieve.

### Nothing checked that a product delivers what its spec requires

R1 compared each `requires` block against the schema and closed 68 findings. That comparison proves a requirement *can* be held. It says nothing about whether anything holds it, or whether the compiler carries it to a page.

`Shared/tools/spec_delivery.py` is that third comparison. Measuring only.

## R1.5 — measured

**94 undelivered requirements**, from 186 checked across two subjects.

| State | Count | Meaning |
|---|---:|---|
| `DELIVERED` | 65 | the authored value appears in the compiled product |
| `UNAUTHORED` | 58 | the library holds nothing at this path |
| `NOT_DELIVERED` | 36 | held, and no compiled product carries it |
| `UNDECIDABLE` | 25 | held, but every value is too short to search for without matching by accident |
| `NOT_COMPILED_HERE` | 2 | Core2B, which compiles no product for either bucket |

`UNDECIDABLE` is reported as itself rather than guessed. A false `DELIVERED` is worse than an admitted gap, and an enum or an id fragment can appear in compiled output by coincidence.

### The 36, adjudicated

**Real product defects — content a role requires and a learner never sees:**

- **`CORE1A` emits no misconceptions at all.** `_teaching_text` emits them only for Core1B. Core1A's spec asks for *"the plausible wrong path, named, with a diagnostic that would expose it and the repair that fixes it"* and then says, in words, *"A misconception the learner never hears is a misconception they keep."* Three paths, both subjects. This is the sharpest finding in the batch.
- **`CORE1A` carries no `relation.checks[]`** — *"checks the learner can run alone"*.
- **`CORE1A` carries no `entry_assumptions[]`** — *"the entry capability assumed"*, named first in its required content.
- **`CORE1A` carries no `correspondence[]`** — the representation bridge authored in R3.0 reaches nobody. The figure is emitted; what binds it to the mathematics is not.
- **`CORE1A` carries no worked examples** (`question.answer.reasoning[]` via a Core1A exposure).
- **`CORE1` carries no `datum.value`.** It prints each quantity's meaning and unit and omits the number. Its spec asks for *"the worked anchor values, if the bucket has one, stated compactly"*.
- **`CORE2`/`CORE2A` substitute `"LIBRARY"` for the question's `source_refs`**, and carry no `figure_refs[]`. Core2's spec requires source identity *"preserved verbatim"* and that *"figures and their captions survive"*.
- **`question.hints[]` is `UNAUTHORED` everywhere and `_question_block` hardcodes `"hints": []`.** Both halves are broken, so fixing either alone delivers nothing.

**Author-facing by design — held for a reviewer, not for a learner:**

- `elicitation.reconstruct.route[].why_this_ask` — printing "why I asked you this" to a learner defeats the ask.
- `elicitation.reconstruct.differs_from_teaching_path` — the sentence a reviewer checks the A/B claim against.
- `resource.access_status`, `microtopic.research_contribution` — arguable, and argued in R1.6 rather than assumed here.

The `requires` block cannot currently say this. R1.6 gives it a marker, so that "not for the learner" is a claim a reviewer can dispute rather than a silence the tool has to guess at.

**Delivered in transformed form — the check cannot see it:**

- `relation.expression` reaches Core1 as MathML, which is the typeset form of the same expression.
- `question.exposure[].role` is mapped through a translation table into `exposure_role`.
- `elicitation.attempt.closure` is delivered as its content rather than its enum name.

Stated as a limit of the tool, not excused: it looks for the authored value in the compiled output rather than mapping library paths onto block fields. A mapping would need updating whenever the compiler changes shape, by whoever changed it, which is the arrangement this whole layer exists to avoid.

## The batch, in dependency order

| Step | Work | Blocked by |
|---|---|---|
| R1.5 | the delivery gate, measuring only | — |
| R3.1 | `VECTOR_SUBTRACTION` renderer; `FIGURE_AUTHORING` 3 → 0 | — |
| R1.6 | mark author-facing paths, fix the compiler defects, enforce | R1.5 |
| R3.2 | Core1's canonical-figure slot | R3.1 |
| R3.3 | renderer priority by evidence rather than list order | — |
| R4.0 | import the 12 admissible Physics packets | — |
| R3.4 | `FREE_BODY_DIAGRAM` | R4.0 |

R3.3's exit condition is that its report independently names `VECTOR_SUBTRACTION` as highest-value and `FREE_BODY_DIAGRAM` as zero-value until R4.0 lands — reproducing what had to be measured by hand to write this document.

## Measured after R1.5, R3.1, R1.6 and R3.3

### R1.6 — the compiler drops nothing

`NOT_DELIVERED` is 0. 37 paths remain `UNAUTHORED`, named on every run.

The enforcement line is drawn between them deliberately: a compiler that drops content somebody wrote is a defect and always will be, while content nobody has written yet is a backlog — and a backlog that fails the build gets the build switched off rather than the backlog closed.

Two markers were needed because the `requires` block could not say what it meant. `[author]` marks a requirement held for a reviewer and not for a learner; `[derived]` marks one the learner does receive in a form the value-presence check cannot recognise. Inferring either in the tool would have been the tool deciding what the spec meant.

**A correction to R1.5's own numbers.** Its walker stopped at a container, so a full `question.hints[]` read `UNAUTHORED`. Seven paths were counted as unwritten with the content sitting inside them — the backlog was smaller than reported.

### R3.3 — and the answer is "none of them"

| Subject | Unbuilt kinds with a representation waiting |
|---|---:|
| Physics | 0 |
| Mathematics | 0 |
| Chemistry | 0 |

R3.1 closed every `FIGURE_AUTHORING`, so **no proposed renderer has any content waiting on it.** Which renderer is worth building next is decided by what R4.0 imports, not by the roadmap's list order — and one built now could only be proven against a hand-authored fixture, which the figure layer refuses.

The ranking is counted from the records rather than from bucket slices. The first version used slices and swallowed the ones that would not resolve, so a kind could read "nothing waiting" because the library would not resolve rather than because nothing needed it. Those are opposite answers and a ranking cannot be read if they look the same; buckets that will not slice are now named instead of dropped.

### R3.2 — Core1 carries the map

Core1 emitted no figure at all. It now carries the one the bucket declares, bound to its orientation rather than to a microtopic: there the figure is the map of the bucket, not the illustration of one transition in it.

`bucket.primary_representation_ref` is declared, never inferred. Choosing the first representation, or the one with the most instances, would make the map of a bucket depend on authoring order. A bucket with a drawable figure and no declared primary is a finding; one with nothing drawable is not asked to name one, because demanding a figure from a bucket that has none would be demanding one be invented.

Three findings guard it: undeclared, unknown, and named-but-undrawable.

### Where the batch ended

| Step | State |
|---|---|
| R1.5 | done — 94 measured, then corrected down by the container-walk fix |
| R3.1 | done — `VECTOR_SUBTRACTION` renders; Physics `FIGURE_AUTHORING` 3 → 0 |
| R1.6 | done — `NOT_DELIVERED` 36 → 0, enforced |
| R3.3 | done — nothing is waiting on any unbuilt renderer |
| R3.2 | done — Core1 carries its canonical figure |
| R4.0 | done — twelve candidates in, and they unblock nothing |
| R3.4 | still blocked, on authoring rather than on the import |

### R4.0 — the import lands, and the plan's premise was wrong

Twelve admissible packets imported under C5: `DIGEST_PINNED_CANDIDATE_SOURCE_ONLY`, `packet_authority: NONE`, each pinning its packet digest. The survey reproduces the committed intake report exactly — 43 packets, 12 admissible, 31 rejected.

**What they carry, measured:**

| | |
|---|---:|
| microtopics | 12 |
| relations | 0 |
| representations | 0 |
| data | 0 |
| questions | 0 |
| capabilities | 0 |

One microtopic per packet and nothing else, with 204 named gaps.

So **R4.0 does not unblock R3.4**, which is what this plan said it would. A free-body diagram needs forces as data atoms bound to a relation, and no packet carries either in a form the importer can take — by design, since filling those in mechanically is the manufactured teaching the importer exists to refuse. What unblocks the renderer is authoring a force bucket with `PHY-NLM-FIRST-LAW` as candidate input: content work sized like R2.2's elicitation authoring, not an import step.

The candidates sit in `Physics/candidates/`, never in a library. `CANDIDATE_IN_LIBRARY` refuses a file carrying `packet_authority: NONE` inside `library/`, checked at the boundary rather than trusted to a directory name — because the one way that claim gets lost is a file being moved to where everything trusts what it finds.