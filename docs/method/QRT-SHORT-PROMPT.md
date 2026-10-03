# QRT short-prompt authoring

This is the front door for an owner prompt that contains only the repository/topic/questions and asks for learner HTML + QRT evidence.

## Owner-facing contract

The owner may supply only:

- subject;
- grade;
- topic;
- question texts;
- requested outputs.

The agent normalizes that natural-language prompt to `qrt-short-prompt-request/v1`.

The agent must then ask only for missing values that materially change provenance, personalization, or product role:

1. learner knowledge;
2. question provenance;
3. source details when the material is external/adapted and the source is unknown;
4. whether to preserve the supplied questions as owner/source questions or use them as authored practice.

The agent does **not** ask the owner for D-band, cognitive demand, QRT cell, X/Y/Z/W, capability mapping, solution route, hints, figures, or misconception repair.

## Learner clarification

If learner knowledge is absent, ask for idea-level states using:

`DEMONSTRATED | UNCERTAIN | MISSING`.

The owner may explicitly answer `USE_DEFAULT_GENERIC`. Only then may this short-prompt path use the repository generic/default learner start. It must begin with a short diagnostic before making personalised X/Y claims.

This is a preflight clarification step, not a product HOLD state.

## Provenance and role

- `OWNER_SUPPLIED` + `PRESERVE_OWNER_QUESTIONS` → Core2 / `BP-CORE2-SOURCE-QUESTION@1.5.0`.
- `AUTHORED_PRACTICE` or owner intent `AUTHORED_PRACTICE` → Core2A / `BP-CORE2A-SUPPORTED-APPLICATION@1.1.0`.
- `EXTERNAL_SOURCE` / `ADAPTED` → source custody must be researched/verified before source claims.

Owner-supplied questions carry no invented exam/year/paper identity.

## Agent flow

```text
short prompt
  ↓
normalize request
  ↓
owner clarification needed?
  ├─ yes → ask only listed questions → merge answers → plan again
  └─ no
       ↓
route Core2/Core2A
       ↓
research/map canonical topic and capabilities
       ↓
solve + verify every question
       ↓
derive five-component difficulty + D-band
       ↓
derive cognitive demand
       ↓
QRT resolve + Mathematics/Physics/Chemistry adapter
       ↓
author/repair support while preserving W
       ↓
build governed records + product manifest
       ↓
render_core
       ↓
real quality gates + exact-render QRT review
       ↓
learner HTML + QRT evidence
```

## CLI

Normalize and plan a request:

```bash
python Shared/tools/qrt_short_prompt.py plan --request request.json
```

If owner inputs are missing, output state is `OWNER_INPUT_REQUIRED` and the result contains only the decision-changing owner questions.

After those answers are merged into the request, the same command returns `READY_TO_AUTHOR`, the Core role/Blueprint, and the complete agent-duty work order.

## Example minimal normalized request

```json
{
  "schema": "qrt-short-prompt-request/v1",
  "subject": "Mathematics",
  "grade": 9,
  "topic": "Surface Areas and Volumes",
  "questions": [
    {"id": "Q1", "text": "A wooden cube has edge length 7 cm. Find its total surface area."},
    {"id": "Q2", "text": "A cylindrical water bottle has diameter 14 cm and height 20 cm. Find its curved surface area."}
  ],
  "requested_outputs": ["LEARNER_HTML", "QRT_EVIDENCE"]
}
```

This correctly produces owner clarification questions rather than silently assuming learner knowledge or provenance.

A completed request adds, for example:

```json
{
  "learner_input": {
    "mode": "PROFILE",
    "ideas": [
      {"idea": "radius versus diameter", "status": "UNCERTAIN"},
      {"idea": "substitution into a known formula", "status": "DEMONSTRATED"}
    ]
  },
  "provenance": {"kind": "OWNER_SUPPLIED"},
  "product_intent": "PRESERVE_OWNER_QUESTIONS"
}
```

The agent then maps those human idea names to canonical capability refs; the owner is not required to know repository IDs.

