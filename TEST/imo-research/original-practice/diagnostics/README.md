# Grade 9 original-practice — structured response and diagnostic research

**Purpose:** test learner-answer *schemas* and modelled misconceptions for the seven newly authored, non-SOF-source practice problems merged in [PR #270](https://github.com/reallaksh19/Grade9v3.5/pull/270), commit `1caa71fc3deda2fbff70bed40f0a092a13457bff`. This is **research evidence for learner feedback design**, not a production free-text grader, proof assessor or canonical QRT/Core admission.

Each of the seven packets in `structured-checker-cases.v1.json` specifies a task-specific, structured response format; two mathematically equivalent illustrative passing inputs; and at least two incorrect examples mapped to a precise misconception **code** and actionable hint. The 18 intentionally incorrect examples cover missing proof warrants, sign/axis confusion, altitude and one-half factors, area-of-curved-surface versus end caps, change-in-x/slope traps, invoice variable swaps, and coordinate transformation/area-invariant errors.

| Item | Structured answer evidence | Example diagnostic |
| --- | --- | --- |
| 001 — consecutive integer divisibility | Claim truth, a parity factor, a factor divisible by 3, and selected universal warrant type | `EXAMPLE_ONLY`: testing specific products is not a universal proof |
| 002 — signed coordinate directions | x, y numbers | `AXES_SWAPPED`: swapped coordinate order |
| 003 — equal-area triangles | Equal-area flag, area in cm² and perpendicular-altitude flag | `TRIANGLE_HALF_FACTOR`: forgot one-half |
| 004 — cylinder sheet | Curved-surface-only scope and numeric area in cm² | `END_CAPS_INCLUDED`: counted uncovered ends |
| 005 — linear data relation | Slope, intercept, inverse-input value | `DELTA_X_IGNORED`: used the drop in y without dividing by change in x |
| 006 — print-shop costs | Two unit prices and new order total | `UNIT_PRICES_SWAPPED`: reversed booklet/card prices |
| 007 — reflection and translation | Three named final vertex coordinates, twice-area and area-preserved flag | `REFLECTION_TRANSLATION_MISORDER`: omitted or reordered steps |

`validate_practice_diagnostics.py` imports and runs the previously merged original-question mathematical validator first, then validates the seven answer schemas, all 14 positive/equivalent illustrative inputs, 18 negative misconception examples, immutable source ID/QRT proposal cross-links and research-only status. The predicate `diagnose(item, response)` returns `PASS`, a specific misconception code, `INVALID_STRUCTURE`, or a generic error.

**Important grading limitation:** a student can state a true theorem with invalid reasoning, or use legitimate prose this structured checker cannot understand. Item 001's parity/modulo-3 flags are only a structured *claim certificate*, not independent semantic proof verification. The arbitrary free-response questions as written cannot be graded with this checker without additional explicit response collection design, accessibility/product QA, ambiguity handling and model validation. It must not mark real students correct by simply matching keywords. The same limitation applies to free-form geometric proofs.

## Originality, learner safety and admission

No original SOF paper stem, answer-choice set, figure scan or PDF bytes are included. The practice source is newly AI-authored and is not presented as an official SOF paper. No global independent originality certificate is claimed. Independent human academic approval is **not applicable by owner instruction**; mathematical correctness and other software/product checks remain necessary.

Each diagnostic packet remains `RESEARCH_ONLY_NOT_LIVE` with learner accessibility and readability review `NOT_COMPLETED`, product owner decision `null`, accepted QRT `null`, Core-ready `false`, and learner-published `false`. These are the underlying truth conditions; the new diagnostic checker does **not** accept any of the 28 canonical QRT cells or admit a question to Core 2/Core 1A.

## Qualification

```sh
python TEST/imo-research/validate_practice_diagnostics.py
python -m unittest discover -s tests -p 'test_imo_practice_diagnostics.py' -v
python -m unittest discover -s tests -p 'test_imo_*.py' -v
```

The scoped `SOF IMO research seed integrity` CI executes this validator with the prior research checks. The 20 new adversarial tests explicitly reject booleans as numeric coordinates, `NaN`, missing fields, arbitrary proof prose, altered correct/mistake examples, misleading QRT/Core decisions and copied SOF original source text. Passing them would qualify the *research structured checker*, **not** learner deployment.

Responsibility: [issue #277](https://github.com/reallaksh19/Grade9v3.5/issues/277). The separate six-gate Core intake contract is tracked by [issue #271](https://github.com/reallaksh19/Grade9v3.5/issues/271) / [PR #274](https://github.com/reallaksh19/Grade9v3.5/pull/274).
