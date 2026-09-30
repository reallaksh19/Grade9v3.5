# From a request to the first-stage Core

How a new job enters, who chooses the first Core, and what the word "rung" means. This is guidance in the same spirit as the rest of `docs/method`: it orders work and adds no gate.

## Ways in

| You have | Use | It gives you |
|---|---|---|
| Raw questions, a syllabus list, or instructions, in your own words | `public/raw-intake/index.html`, or `python3 Shared/tools/raw_intake.py --input request.json` | An intake with research and authoring tasks for every input, the first-stage route, and the outputs to expect. Nothing needs an identifier. |
| One subtopic that already has a matrix, and a list of Cores to plan | a `Requests/*.json` file and `python3 Shared/tools/plan_request.py --plan FILE` | A plan per Core with the duties each still has. One subtopic per request; give a syllabus of several subtopics as several requests. |

## Who chooses the first Core

In this order:

1. **A Core the requester names wins** (`requested_cores`, or the "First Core to build" choice on the intake form).
2. Otherwise **supplied question text starts with Core2**.
3. Otherwise, with no question bank, **source-grounded Core1**.

Core2 asked for without question text is not a reason to stop or to invent a bank: acquire the source questions, or offer Core1 or clearly labelled authored practice. Cores that were not chosen first are planned, not generated, until the first-stage packet has been shown ([FIRST-STAGE-REVIEW.md](FIRST-STAGE-REVIEW.md)). Research, solving and drafting for them continue meanwhile.

## Naming a subtopic

Give the matrix title or its `bucket_id` and it resolves exactly. Otherwise the planner matches by words, with dimension words normalised (so "Motion in 1D" reaches "One-dimensional motion"):

- **one matrix fits** — it is used, the plan records the match under `resolutions`, and the plan carries a `CONFIRM_SUBTOPIC_RESOLUTION` duty: say which subtopic you took it to be in the first-stage packet so it can be corrected;
- **several fit** — none is chosen; the plan lists them in `candidates`;
- **none fit** — no plan is produced; the nearest matrices are listed.

The planner never picks between competing matrices for you.

## When the input is thin

Four things a cold-start run hit. Each is stated as the tools behave today.

- **Subject.** `raw_intake.py` needs a `subject` (free text, no canonical id). Without one it exits 1 with `INVALID_REQUEST: subject is required`, printed on stderr (and in the `errors` field of the JSON, which is also why `questions` then reads 0: the request was rejected, not empty). Add the subject to **your copy** of the request; never edit the Owner's file.
- **From an intake to a plan.** The intake output is not a planner input. The planner takes an authoring request (`Requests/*.json`: `request_id`, `subject`, `bucket_id` or a matrix title, `cores`, optional `learner`); see `Requests/relative-motion-g9.request.json`. Write one from the intake's subject and the subtopic you resolved, then `python3 Shared/tools/plan_request.py --plan FILE`. If it lists several candidates and chooses none, say which you took and that the Owner should confirm it. `product_manifest.py derive` also takes the intake (`--intake intake.json`).
- **Owner-supplied questions in Core2: not possible yet.** [CORE2.md](../../Shared/roles/CORE2.md) says they are custody in their own right (class `OWNER_SUPPLIED`) and appear verbatim. Today Core2 takes its records only from exam-bank files, whose schema requires an official exam, year, paper and archive URLs, and a package question in the `core2` selection is rejected (`PRODUCT_SELECTION_WRONG_AUTHORITY`). Do not invent an exam identity to get past it. Author the answers in your workspace, record the blocker, and keep going with the rest. Tracked in #371.
- **Checks for a job that is not yet a unit.** `self_check.py --unit SUBJECT/slug` needs an existing unit. For a rendered draft use `python3 Shared/tools/quality_gate.py RENDER_DIR --subject SUBJECT --product-id ID --static --report FILE`. A draft build (`render_core.py build --draft`) succeeds with gaps; it prints `selected records: ...` and warns for any role in the product that selects none.

## "Rung" means two things

Say which one you mean.

- **Ladder rung** (`R1`, `R2`, …, from `<Subject>/matrices/*.rungs.json`): a position on a capability ladder. It sets where Core1A and Core1B start for a learner, and it decides the support level of practice.
- **Hint rung** (first hint, second hint, …): a step of staged help on a question in Core2 and Core2A. Source hints (`hints[]`) and authored support (`scaffolds[]`) are different lanes and are never presented as one another.

## Recording the approval

Only the Owner accepts an exact render. When the Owner has approved one, name where they said so: `python3 Shared/tools/accept_product.py SLUG --approval-ref "<link to the message or comment, or a quotation>"`. The reference is written into the acceptance record beside `accepted_by`. It is recorded, not verified, and acceptance does not require it.
