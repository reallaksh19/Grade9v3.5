# Grade9V3

Self-study learner-material production system for **Physics, Mathematics and Chemistry**, **CBSE grades 9–11** (with explicit IIT-JEE tier classification where applicable).

**Current Owner progression:** Physics is sequenced **Grade 9 → Grade 10 → Grade 11**, with **Grade 9 first**. Mathematics/Chemistry and cross-subject infrastructure remain available, but they are not the present completion target.

**Learner outcome:** make the learner increasingly capable of deciding what she knows, discovering with little external steering what she does not know, repairing the right Physics gap, and independently verifying a solution. Grade 9 is complete enough when the foundation is usable for Grade 10—not when every optional extension is exhausted.

## Agent start here — mandatory first reads

If you are an agent or maintainer entering this repository without prior conversation context, **do not plan from issue titles, old roadmap documents, or repository breadth**. Read these first:

1. [`agents/relay/roadmap/OVERALL_ROADMAP.yaml`](agents/relay/roadmap/OVERALL_ROADMAP.yaml) — the **current machine-authoritative roadmap** and current Grade-9 Physics programme outcome.
2. [`agents/relay/roadmap/owner-decisions/ODR-0003-G9-PHYSICS-INDEPENDENCE.yaml`](agents/relay/roadmap/owner-decisions/ODR-0003-G9-PHYSICS-INDEPENDENCE.yaml) — the Owner-intent mutation defining what “success” means and what must not be inferred.
3. [`agents/relay/REPO_STATE.yaml`](agents/relay/REPO_STATE.yaml) — the V2.5 machine bootstrap for the current roadmap revision, work package and `active_ep.path`.
4. [`agents/relay/roadmap/PROGRESS.yaml`](agents/relay/roadmap/PROGRESS.yaml) — calculated progress authority.
5. Follow `active_ep.path` from `REPO_STATE.yaml` and execute only that package after satisfying its V2.5 takeover/material-write requirements.

For deterministic V2.5 execution routing, `REPO_STATE.yaml` remains the bootstrap locator. The roadmap and Owner decision are first-read programme intent; they do **not** replace the active-EP/write-admission contract.

These relay sources outrank README prose, issue summaries, PR descriptions, and older roadmap-like documents for current programme/execution truth. Do not copy the current percent, work package, or active EP into this README as a second state store; follow the structured sources instead.

The other roadmap-like documents remain useful, but they have different roles:

| Document | Role |
|---|---|
| [`docs/PROGRAM-PLAN.md`](docs/PROGRAM-PLAN.md) | Product/architecture programme context; not live execution authority |
| [`docs/ROADMAP-LEARNER-READY.md`](docs/ROADMAP-LEARNER-READY.md) | Learner-readiness conceptual/historical predecessor; current Grade-9 progression intent is the V2.5 roadmap + ODR-0003 |
| [`docs/PLAN-R0-R2.md`](docs/PLAN-R0-R2.md) and [`docs/PLAN-R3-R4.md`](docs/PLAN-R3-R4.md) | Prior execution plans retained as engineering history |
| [`docs/FUTURE-ROAD-PLAN.md`](docs/FUTURE-ROAD-PLAN.md) | Evidence-gated ideas and anti-overarchitecture guardrails; the Grade-9 scope/exit items promoted by RM-0006 are no longer merely future ideas |

Six learner products per subtopic bucket:

| Product | Purpose |
|---|---|
| Core1 | Compact basic notes / semantic orientation |
| Core2 | Source questions with ladder hints, source identity and answers |
| Core1A | Declarative detailed teaching, by intrinsic subtopic difficulty |
| Core1B | Open-ended conceptual reconstruction (self-tutor) |
| Core2A | Purpose-adjusted practice with complete solution breakdowns |
| Core2B | Supported application and transfer |

## Shape

```
Shared/            subject-neutral engine — no subject, topic or gate identifier may be hardcoded here
  roles/           the six Core role specifications
  gates/           technical engineering gate schema + validator        (P2)
  library/         microtopic library engine: intake, promotion, resolver (P3)
  publication_host/ composition, closure, storage, audit, figures        (P1)
  tools/           guardrails and generators
Physics/ Mathematics/ Chemistry/
  adapter/         subject contract: validator families, representation vocabulary,
                   equation semantic fields, curriculum bindings
  gates/           subject gate data, grades 9–11
  library/         microtopic packages
  content/         authored runs and published products
tools/             topic library browser, run builder, portal            (P4)
docs/              program plan and architecture
```

The governing rule: **subject and topic variation is governed data, never a branch in engine code.** `Shared/` is checked for this automatically — see `Shared/tools/topic_independence_guard.py`.

## Running it

```sh
# compile one bucket from its library into publication inputs
python3 Shared/library/compile_inputs.py Mathematics/library/*.json \
  --bucket BUCKET-LINEAR-EQUATION --subject Mathematics \
  --topic-id MATH-LINEQ-G9 --title "Linear equations in one unknown" --out /tmp/lineq

# publish through that subject's adapter
python3 Mathematics/run.py publish --plan /tmp/lineq/plan.json \
  --baseline /tmp/lineq/baseline.json --source-root /tmp/lineq --out /tmp/lineq/publication

# research-first job from raw questions/syllabus (see docs/RESEARCH-FIRST-WORKFLOW.md)
python3 Shared/tools/raw_intake.py --input request.json
python3 Shared/tools/render_core.py build --manifest product.json --out /tmp/job
python3 Shared/tools/quality_gate.py /tmp/job --subject Physics --product-id P

python3 -m unittest discover -s tests -p "test_*.py"   # full suite
python3 Shared/tools/topic_independence_guard.py       # engine carries no subject
python3 Shared/tools/build_manifest.py                 # regenerates the manifest and tools/data.js
```

A committed publication pins a snapshot of the engine that produced it, and the suite re-verifies every committed run. So after changing the engine or a subject adapter, refresh them:

```sh
python3 Shared/tools/republish.py            # verify every committed run against its snapshot
python3 Shared/tools/republish.py --write    # refresh them
```

`--write` refuses if the composed pages or figures would change, because that is a change to what a learner reads rather than a routine refresh. Pass `--accept-output-change` when you mean it, and say so in the commit message.

`tools/index.html` opens over `file://` with no build step.

## Status

Two subjects publish end-to-end: Physics (relative motion, frozen as the port oracle) and Mathematics (linear equations, compiled from its library on demand). Chemistry has a contract but no library yet.

For current engineering execution, use the V2.5 relay sources in **Agent start here** above. [docs/PROGRAM-PLAN.md](docs/PROGRAM-PLAN.md) remains product/architecture programme context and records what earlier phases established. **Nothing here claims independent academic review, learner release or curriculum authority** — machine checks establish structure, custody and supported computation, not that an explanation teaches.

## Provenance

Architecture derives from the V3B work in `reallaksh19/Common` (draft PR #364, branch `draft/core-relay-architecture-review-20260913`), with adaptations from the parallel tracks in that repository: PR #350/#383 (Physics engineering gates, curriculum-scope binding, authority delegation) and PR #395 (Mathematics observability, subtopic intelligence library, topic-independence guarding). Those tracks are referenced and adapted, never copied wholesale.