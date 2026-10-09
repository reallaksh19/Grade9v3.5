# IMO G9 — source-safe Q26-like Core1A candidate, real canonical renderer proof

**Task coordination:** [IMO governing issue #294](https://github.com/reallaksh19/Grade9v3.5/issues/294). **Research status:** AUTHOR_CREATED_TEST_CANDIDATE, **not owner-accepted**, not published. Programme keeps **68** source positions and seven separate authored practice items. [Batch A draft #305](https://github.com/reallaksh19/Grade9v3.5/pull/305) is the provisional source-specific reference; the independent academic [construction review #306](https://github.com/reallaksh19/Grade9v3.5/pull/306) proposes the source-safe example. This package does **not** authenticate the printed source question or reproduce its stem, options, figures or key.

## What the source-checked mathematical audit actually supports

Original research identity: 2024–25 school-mirror SOF IMO G9 Set B printed Q26, PDF physical page index 4, source math audit `IMO-B02-010` in `TEST/imo-research/verification/fullpaper-source-math-batch02.v1.json`. The observed decisive move is to rewrite two exponential terms using a **common positive quantity**, preserve the factor created by an exponent offset, solve for that quantity, then return to the exponent. Source item-component fidelity, official full-paper key and publisher reuse rights are still **unapproved and incomplete**.

**Newly authored anchor** (not a transcription): `3^(2x+1)=9^x+162`. With positive `t=3^(2x)`, write `3t=t+162`, hence `t=81=3^4` and `x=2`. Independently check `3^5=9²+162=243`.

The learner receives five named and justified moves: declare the real positive-base domain, rewrite powers to a common quantity, justify the multiplicative factor, solve in `t` and map back, then verify original equality. Explicit wrong paths are equating exponents across a *sum* and accepting a nonpositive `t`. A text-symbol relation table aligns `9^x` with `t` and `3^(2x+1)` with `3t`. No decorative or licensed source figure is used.

**Independent authored exit:** `2^(2y+1)=4^y+64`. Correct `t=4^y=64`, `y=3`; reverse-check `128=128`. An additional nonpositive-`t` counterexample tests domain boundaries. The construction is a proposed repair for the verified *mathematical reasoning*, not guaranteed fidelity to every original printed component.

## Artifacts and canonical render path

- `TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.v1.json` — canonical-shaped **authored** `TEST` library schema `0.2.0`, one capability, one microtopic, one complete Core1A construction, no source Core2 questions or source-bound materials.
- `TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.test.manifest.json` — selects **CORE1A only**, empty source bank and no other Core role; all seven authored practice questions remain separately inventoried.
- `tests/test_imo_q26_common_base_core1a.py` — schema/references, maths oracles, explicit no-acceptance assertions and real renderer in-memory output test.
- `.github/workflows/imo-q26-authored-core1a-render.yml` — invokes **existing** `Shared/tools/render_core.py build --draft`, then **existing** `tools/print/print-product.mjs`, then actual Playwright Chromium at 320/390/768/1280 and 390/200% text size, and verifies exact learner PDF bytes + print receipt.
- `tools/site-audit/imo-q26-core1a-render-review.mjs` — browser check and authored screenshot measurements; no teacher/key material or original SOF PDF acquisition.

**Outputs:** Only generated to `/tmp/imo-q26-core-render` on the CI runner, with `core1a.html`, `core1a.pdf`, `render-receipt.json`, `print-receipt.json`, browser screenshots and evidence JSON uploaded as a dated workflow artifact. The CI job is the provenance for actual output links when successful. Do **not** hand-edit derived HTML, mirror it to `public`, or advertise the TEST CI artifact as a learner release.

## Protected product boundaries

| Decision axis | State |
|---|---|
| Authored Core1A package and full mathematical explanation | CANDIDATE / agent-authored |
| Relationship to original printed Q26 | RESEARCH_MATH_CRUX_PROVISIONAL |
| Source SOF PDF retained, components and rights | NO / INCOMPLETE / NOT_GRANTED |
| Source Core2 eligible, admitted or rendered | ZERO |
| QRT acceptance | ZERO |
| Canonical-product academic/Owner acceptance | NOT_GRANTED |
| Published learner page or SOF original question | NONE |
| Independent human comprehension/screen-reader inspection | NOT_RUN |
| Renderer-generated candidate HTML/PDF | CI_GATE_PENDING |

Run locally in an actual cloned repository:
```sh
python -m pip install jsonschema pypdf
npm install --no-save playwright@1.56.1
npx playwright install chromium
python -m unittest discover -s tests -p 'test_imo_q26_common_base_core1a.py' -v
python Shared/tools/render_core.py build \
  --manifest TEST/imo-research/candidates/imo-g9-q26-common-base-core1a.test.manifest.json \
  --out /tmp/imo-q26-core-render --mode PAGES --draft
node tools/print/print-product.mjs /tmp/imo-q26-core-render
node tools/site-audit/imo-q26-core1a-render-review.mjs
```

**Draft decision:** even if these procedures pass, the genuine original Core2 question remains held, this source-tuned lesson is only a **proposed** conceptual link, and academic/Owner acceptance is handled through issue #294. No new Core gate or authority token is created.
