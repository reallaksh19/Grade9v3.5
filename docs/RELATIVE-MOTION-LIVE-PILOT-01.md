# Relative Motion live pilot 01

This is the first actual learner-run protocol for the self-study v1 candidate.

It deliberately adds **no new architecture**. The purpose is to collect real evidence from one
Relative Motion session and use only observed failures to justify further changes.

## Source questions

Use:

`docs/pilots/relative-motion-live-01.worksheet.json`

The file retains only identifiers, capability mappings and source links for two externally
authored ExamSIDE JEE Main questions. Do not copy their full wording into canonical content.

The intended order is:

1. `EXAMSIDE-MIP-2026-01-21-RIVER`
2. `EXAMSIDE-MIP-2022-06-27-RAIN`

Use the question wording from the linked source page when presenting the problem to the
learner.

## Before the learner starts

Do not invent either of these inputs:

- prior mastery of `CAP-SIGNED-PAIR`;
- a rough Relative Motion percentage.

If genuine prior learner evidence already demonstrates `CAP-SIGNED-PAIR`, use the real
profile containing that evidence. Otherwise leave it unobserved. The plan should then remain
`valid=true, ready=false` and surface the Mathematics bridge.

A rough subtopic estimate may be supplied only if the parent genuinely has one. It is a
starting-position hint, not evidence.

## Generate the plan

Without a rough estimate:

```bash
python3 Shared/tools/study_session.py plan \
  --map docs/pilots/relative-motion-live-01.worksheet.json \
  --readable
```

With a genuine parent estimate, for example 60%:

```bash
python3 Shared/tools/study_session.py plan \
  --map docs/pilots/relative-motion-live-01.worksheet.json \
  --estimate "Relative motion=60" \
  --readable
```

If an actual learner profile is available, also pass:

```text
--profile <real-profile-path>
```

Do not manufacture a profile merely to bypass the bridge.

## Bridge rule

If the first action is:

```text
BRIDGE — CAP-SIGNED-PAIR -> Mathematics
```

stop the Physics session until the prerequisite is genuinely verified or repaired through
the provider boundary.

Do not mark it `DEMONSTRATED` because the learner says the topic looks familiar.

If existing evidence already demonstrates it, the runner should skip the bridge and continue
to the selected local Relative Motion rung.

## Learner attempt

Present the source question without hints or solution material.

For the first question, record only:

- the learner's final answer;
- enough working/reasoning to diagnose the attempt;
- whether any help was used;
- a short response summary for the evaluator.

Do not diagnose while the learner is still making the first independent attempt.

## Evaluate conservatively

The session runner does not grade free-form work. A human or approved evaluator supplies the
outcome.

If the answer is wrong but the failed capability is unclear, do **not** guess
`failed_capability_ref`. Let the feedback runtime return diagnostic prompts.

If the work clearly shows a Relative Motion failure, an example command is:

```bash
python3 Shared/tools/study_session.py attempt \
  --map docs/pilots/relative-motion-live-01.worksheet.json \
  --question EXAMSIDE-MIP-2026-01-21-RIVER \
  --result INCORRECT \
  --failed-capability CAP-RELATIVE-V \
  --error-stage CONCEPT \
  --response-summary "<brief factual description of what the learner did>" \
  --when <ISO-date-or-timestamp> \
  --readable
```

If the misconception is not yet confirmed, omit `--misconception-index`.

Only after presenting the canonical diagnostic prompt and recording the learner response
should the corresponding index be supplied. Misconception-specific repair additionally
requires `--diagnostic-response`, `--diagnosis CONFIRMED`, and a non-empty
`--diagnostic-basis`. If the evidence is ambiguous, use `INDETERMINATE`; the runtime stays
in diagnosis rather than pretending the misconception is confirmed.

For an independent correct attempt:

```bash
python3 Shared/tools/study_session.py attempt \
  --map docs/pilots/relative-motion-live-01.worksheet.json \
  --question EXAMSIDE-MIP-2026-01-21-RIVER \
  --result CORRECT \
  --help-used NONE \
  --response-summary "<brief factual description of the reasoning>" \
  --when <ISO-date-or-timestamp> \
  --readable
```

## What to retain after the session

Keep the returned:

- `observation_draft`;
- `review.next_review`;
- actual next action;
- any diagnosis or repair used;
- whether the fresh verification was answered independently.

The runner intentionally reports:

```text
persistence = NOT_WRITTEN
```

Review the observation before it becomes learner evidence.

## What counts as a real failure worth changing code for

Change core behavior only if the live session demonstrates something concrete such as:

- the plan starts at an obviously inappropriate rung despite correct inputs;
- a provider bridge cannot be represented or cleared correctly;
- the learner-facing output leaks an answer before an attempt;
- diagnosis cannot distinguish the observed failure;
- a repair is materially unrelated to the diagnosed misconception;
- fresh verification repeats the same demand instead of checking transfer;
- evidence produced by the session misrepresents what the learner actually demonstrated;
- the next-review date is inconsistent with the existing deterministic policy.

Do **not** add framework features because they might become useful later.

## Stop point

The repository work for this pilot is complete once this packet can be generated and the
runner is mechanically green.

The next missing datum is a real learner response to the first source question. Until that
exists, do not fabricate a successful or failed study episode.
