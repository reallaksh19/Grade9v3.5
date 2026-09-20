# Grade9V3

Self-study learner-material production system for **Physics, Mathematics and Chemistry**, **CBSE grades 9–11** (with explicit IIT-JEE tier classification where applicable).

## Agent start here — current execution authority

If you are an agent or maintainer entering this repository without prior conversation context, **read these before planning or changing files**:

1. [`agents/relay/REPO_STATE.yaml`](agents/relay/REPO_STATE.yaml) — V2.5 repository bootstrap. Use it to locate the current roadmap revision, current work package, and `active_ep.path`.
2. [`agents/relay/roadmap/OVERALL_ROADMAP.yaml`](agents/relay/roadmap/OVERALL_ROADMAP.yaml) — the **current machine-authoritative engineering execution roadmap**.
3. [`agents/relay/roadmap/PROGRESS.yaml`](agents/relay/roadmap/PROGRESS.yaml) — calculated roadmap/progress authority.
4. Follow `active_ep.path` from the relay state and execute only that package after satisfying its V2.5 takeover/material-write requirements.

The relay files above outrank README prose, issue summaries, PR descriptions, and older roadmap-like documents for **current execution state**. Do not copy the current percent, work package, or active EP into this README as a second state store; follow the structured sources instead.

The other roadmap-like documents remain useful, but they have different roles:

| Document | Role |
|---|---|
| [`docs/PROGRAM-PLAN.md`](docs/PROGRAM-PLAN.md) | Product/architecture programme context; not live execution authority |
| [`docs/ROADMAP-LEARNER-READY.md`](docs/ROADMAP-LEARNER-READY.md) | Learner-readiness conceptual/historical roadmap; not live execution authority |
| [`docs/PLAN-R0-R2.md`](docs/PLAN-R0-R2.md) and [`docs/PLAN-R3-R4.md`](docs/PLAN-R3-R4.md) | Prior execution plans retained as engineering history |
| [`docs/FUTURE-ROAD-PLAN.md`](docs/FUTURE-ROAD-PLAN.md) | Evidence-gated future ideas; explicitly not an implementation plan |

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