# Issue 37 — Agent A Round 1 Work Report

## Candidate

- Issue: #37
- Agent: A
- Round: 1
- Target: D4 hybridisation, Core1A + Core2 only
- Branch: `feat/iss37-d4-hybridisation-agent-a-r1`
- Validated source head: `49c9e2957e91a31e7a40a74cbadd83377c36f1e7`
- Frozen renderer-artifact commit from that green run: `d813c58a6e689ec392bfd5af1089a7aedbb9ad74`

## Custody

- The ten benchmark questions are preserved verbatim from the owner-supplied Issue #37 intake.
- Owner-core SHA-256: `52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7`.
- Custody remains `OWNER_SUPPLIED` benchmark input drafted by the coordinating agent; it is not an official exam/PYQ and is not attributed as personally authored by the owner.

## Authoring and rendering

- Product output roles are strictly scoped to `CORE1A` and `CORE2`.
- The torsion/orbital representation is normalized to Chemistry-native `ORBITAL_DIAGRAM` vocabulary.
- `Shared/tools/render_core.py` remained the sole HTML renderer; rendered learner HTML was not hand-edited.
- Frozen learner outputs:
  - `evidence/benchmark/ISS37/rendered/core1a.html`
  - `evidence/benchmark/ISS37/rendered/core2.html`

## Validation

GitHub Actions cold run `37202577119` passed the complete candidate chain at source head `49c9e2957e91a31e7a40a74cbadd83377c36f1e7`:

- focused/pinned authoring-authority tests: **PASS**
- verbatim intake hash: **PASS**
- package schema: **PASS**
- requested output-role scope: **PASS**
- governed renderer gap report: **0 depth gaps; 0 subject-authority findings**
- governed Core1A/Core2 render: **PASS**
- strict learner quality gate: **PASS**
- tablet-12.7 browser audit: **PASS**
- renderer artifact preservation: **PASS**

The workflow then produced artifact-only commit `d813c58a6e689ec392bfd5af1089a7aedbb9ad74`, freezing the exact governed Core1A and Core2 render from the green run.

## Handoff

This candidate is frozen for the paired independent comparison required by Issue #37. Do not merge it until that paired-decision step is complete.
