# Minimal-prompt authoring workflow

## Goal

The owner should be able to start a question-authoring responsibility with a short request containing only repository context plus ordinary source questions.

The owner is **not** expected to provide D-band, cognitive demand, QRT template, X/Y/Z/W, hints, figures, misconceptions, solution design or Core1A structure.

Those are agent responsibilities.

## Owner-owned vs agent-owned

### Ask the owner when materially missing

- subject, grade or topic;
- the actual question batch;
- learner purpose: `STARTER | PRACTICE | REVISION | COMPETITION`;
- idea-level learner knowledge for the *small set of prerequisite/bridge capabilities identified by the agent*: `DEMONSTRATED | UNCERTAIN | MISSING`;
- explicit owner constraints when the task says they exist but does not state them.

Do not infer learner knowledge from an overall percentage. Do not fabricate a production learner profile.

### Do not ask the owner to do the agent's work

The agent must independently determine and verify:

- canonical capability/concept mapping;
- answers and academic correctness;
- five-component difficulty evidence and D1-D4;
- primary/secondary cognitive demand;
- the one QRT cell;
- stable crux and learner-relative X/Y/Z/W after learner evidence is known;
- H1/H2/H3 and any additional useful support;
- whether a figure is useful and what it must show;
- misconceptions, diagnostics and repair;
- independent checks;
- Core2 support content;
- concept-evidence synthesis and Core1A recommendation;
- Blueprint projection and HTML output.

## Required interaction sequence

```text
owner prompt + questions
        |
        v
extract subject / grade / topic / questions
        |
        v
agent independently scans academic prerequisites/bridges
        |
        +---- missing purpose? ------------------------------+
        |                                                    |
        +---- missing learner state for material bridges? ---+--> ask owner once, batched
        |                                                         e.g. Solid/Shaky/Not yet
        v
convert owner answer to
DEMONSTRATED / UNCERTAIN / MISSING
        |
        v
materialize OWNER_ESTIMATE learner profile
        |
        v
agent solves/verifies questions
        |
        v
author D-band + cognitive demand
        |
        v
QRT resolver + subject adapter
        |
        v
author/review Core2 support
        |
        v
Blueprint 1.9 / governed renderer
        |
        v
learner-facing HTML + machine review evidence
```

## Example: Grade 9 Surface Areas and Volumes

A short owner prompt may supply ten questions but no learner data.

The agent first scans the batch and may decide that only these learner states materially change support:

1. circle circumference and area;
2. exposed versus hidden surfaces;
3. area/volume units and litre conversion;
4. Pythagoras for cone slant height;
5. volume conservation during recasting.

The owner-facing clarification should be concise, for example:

> What is the purpose: STARTER, PRACTICE, REVISION or COMPETITION? Also tell me for each item below whether it is Solid, Shaky or Not yet: circle area/circumference; exposed vs hidden surfaces; area/volume unit conversion; Pythagoras/slant height; conservation of volume in recasting.

The agent maps:

- `Solid` -> `DEMONSTRATED`
- `Shaky` -> `UNCERTAIN`
- `Not yet` -> `MISSING`

The owner is never asked to select `D2`, `MODEL`, `QRT-MODEL-D2`, or to design a hint/SVG.

## Tooling

Create a normalized intake JSON from the owner prompt, then run:

```bash
python Shared/tools/authoring_intake.py plan --intake build/intake.json
```

The first result may contain `SCAN_RELEVANT_LEARNER_CAPABILITIES`; that is agent work.

After the agent writes a small capability scan:

```bash
python Shared/tools/authoring_intake.py plan \
  --intake build/intake.json \
  --capabilities build/capability-scan.json
```

If owner facts are missing, the output is `CLARIFICATION_REQUIRED` with only owner-owned questions.

After owner answers are added to the intake:

```bash
python Shared/tools/authoring_intake.py profile \
  --intake build/intake.json \
  --capabilities build/capability-scan.json \
  > build/learner-profile.json
```

The generated profile uses `OWNER_ESTIMATE`, leaves `knowledge_percentage` null, and keeps `measured_fit_claim=false`.

That profile can then be passed to the QRT resolver from the stacked QRT implementation.

## Source custody

Pasted questions are `OWNER_SUPPLIED` unless real provenance is provided. Missing source metadata is not a reason to interrogate the owner unless provenance is materially required by the task. Never invent an exam, year, textbook page, official answer or PDF.

## Blueprint boundary

This intake layer does not create another page blueprint. Blueprint 1.9 remains projection authority. QRT remains semantic review authority. The intake layer only makes the human/agent boundary explicit and produces the learner evidence required for personalized review.
