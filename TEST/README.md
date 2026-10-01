# TEST: a sandbox subject for stress runs

TEST is a subject that exists so a test agent can prepare a learner product end to end without touching Physics,
Chemistry or Mathematics. **Nothing in TEST is curriculum, reviewed or accepted.** Its pages are labelled drafts,
`accept_product.py` refuses TEST, and no machine check here grants release.

On the site it is the **TEST** tab (`public/test/`, deployed as `docs/test/`): a hub, an **Atlas**, **Rungs** and
**Deployments** pages. They read what is in this directory and in `public/test/`; they say nothing is finished.

## The job, in order

1. **Core2**: the Owner's questions, kept verbatim, in an owner-supplied bank.
2. **Core1A**: the concept construction for the same topic.
3. **An explorer**: a guided page on the toughest concept of the same question set, written as a spec and built by the repo's tools.

Each one is deployed to the TEST tab as a draft. Do them in that order; stop and record friction instead of guessing. (The intake lists the Cores it will make in alphabetical order, `CORE1A` before `CORE2`; that is not the order of work.)

## What a page must show: the blueprint

A Core page is built from its **blueprint** (`Shared/web/interactive-page-blueprints.v1.json`; read it as
[docs/specs/PAGE-BLUEPRINT-COMPONENTS.md](../docs/specs/PAGE-BLUEPRINT-COMPONENTS.md)). The blueprint names the page's components (for Core2: the
header, the stem, the conditions, the common wrong route, the representation card, the hint ladder, the numbered working, the answer
and the check), the column each sits in and how much each matters. The renderer builds the page from it, the quality gate judges the page against
it, and `owner_bank.py new` scaffolds exactly the fields it lists. So the way to a good page is to supply what the blueprint lists.

A TEST page is new authoring, so it is held to the **reference page** (the benchmark the blueprint was measured from), not to the floor an
official product is judged at:

- **REQUIRED** and absent or shallower than the reference for the question's difficulty band: a *gap*, printed by the deploy with the record
  and the blueprint's own instruction for authoring it. The reference depth depends on the band you declare in
  `difficulty.band`: a D1 or D2 question has 3 hint rungs and 3 working steps, a D3 or D4 question 5 rungs and 4 steps
  (the spec lists each component's depth by band). Delete the scaffold's rungs and steps your band does not need.
- **EXPECTED** and absent: also a *gap*, unless the record **waives** it. Write the component where the question has one to give (a figure
  for every question: even a pure-number question can show its quantities as a labelled diagram, drawn only from the question's own data).
  Where a question truly has none, say so, with the reason, in the question's `extensions["grade9v3:component_waivers"]`
  as `{"COMPONENT_ID": "why it does not apply"}`. A REQUIRED component cannot be waived. The receipt and the Deployments page list every waiver
  with its reason, for the Owner to accept or refuse; never invent content to avoid a gap or a waiver.
- `owner_bank.py check` holds a bank to the same bar before you deploy, with the same messages.
- The intake's per-question `conditions` are numbers scraped from the question's text, not the conditions the question states; write `conditions` from what the question gives.

Zero gaps, with every waiver reasoned, is the standard. A gap-free page that waives what the question could have given is not at it.

## What TEST can and cannot make

TEST makes **HTML drafts**: Core pages, the rungs table, the Atlas view and an interactive page. It cannot make PDFs,
a key PDF, question-bank records, a coverage export or an owner review packet, although the intake lists some of them
as deliverables. Report each of those as NOT DONE (a limit of TEST) and do not invent one.

## Where each thing goes

`SLUG` is the name you give the job (for example `vectors-g9`). Use the same one everywhere.

| What | Where | Format |
|---|---|---|
| Owner's questions (Core2) | `TEST/question-bank/SLUG.json` | an **owner-supplied bank**, made by `owner_bank.py new` (below). One question per intake question: `stem` is the Owner's text, unchanged. The scaffold lists every field a Core2 page is built from; fill each empty one (what each is for, and what it must hold, is in [the page blueprint](../docs/specs/PAGE-BLUEPRINT-COMPONENTS.md)), and `primary_capability_ref`, `family_ref`, `learner_question_type` and `difficulty` (five components each 0 to 2, `score` their sum, `band` D1 to D4 for that score, `basis` one sentence; your estimate, shown as one). There is **no exam, year, paper or URL** and you must not add one. |
| The ladder (Rungs) | `TEST/matrices/SLUG.rungs.json` | same shape as `Mathematics/matrices/linear-equations.rungs.json`, with `"subject": "TEST"` |
| Concepts, capabilities, Core1A material | `TEST/library/SLUG.v1.json` | a package (`Shared/library/package.schema.json`) with `"subject": "TEST"`. It needs at least one resource, bucket, capability and microtopic; every capability needs a microtopic whose `primary_capability_ref` names it, and every owner question a `family_ref` naming a question family in the package. Start from the schema and let the resolver tell you what is missing (below): the example `tests/fixtures/render/thin-kin-2d-motion.v1.json` is small as packages go but still about 5,000 lines, most of it gate-contract blocks a TEST package does not need; a real one is `Mathematics/library/linear-equations.v1.json`. A construction unit's `worked_anchor_ref` and a family's `item_refs` name questions **of the package**, never questions of the owner bank (the resolver rejects them): write the worked example as a question of the package, which is yours and not the Owner's, and leave `item_refs` empty. A relation may say `"gate_relation_ref": null`: TEST has no gate registry. A figure is an SVG file you author under `TEST/library/figures/` and name in the representation's `rendered_asset_refs`. Check it before you build a manifest with `python3 -m Shared.library.resolve --schema TEST/library/SLUG.v1.json` (the schema, up to six problems at a time, then the references; without `--schema` it checks references only). |
| Product manifest | `TEST/products/SLUG.manifest.json` | made by `product_manifest.py derive` (below) |
| The explorer | `TEST/interactive/SLUG/explorer.json` | a spec made by `explorer_build.py new` (below); see "An explorer" |

A question is selected into Core2 when its `primary_capability_ref` is a capability of the package. Optional question
fields (`conditions`, `subparts`, `figure_refs`, `response`, typed maths in `extensions["grade9v3:math_spans"]`) are
shown by any question in `Physics/library/exam-bank/competitive-exam-question-bank.v2.json`. Maths in a question or its steps shows
as the plain text you typed (`sqrt(3^2 + 4^2)`) unless you declare it in `extensions["grade9v3:math_spans"]`, for example
`{"target": "answer_reasoning:1", "literal": "sqrt(3^2 + 4^2)", "tex": "\\sqrt{3^{2}+4^{2}}", "display": false}`; the literal must occur
in the text at that target (`stem`, `answer_summary`, `answer_reasoning:N`, `conditions`), or the page reports a gap. An owner
question has no exam identity. Do not give it one. If research matches the original later, that is a new record with its own custody, not an
edit of this one.

## Step by step

```
# 1  the Owner's questions, exactly as supplied (the intake gives each one an id)
python3 Shared/tools/raw_intake.py --input workspace/request.json --out workspace/intake.json
python3 Shared/tools/owner_bank.py new --intake workspace/intake.json --bank-id SLUG --out TEST/question-bank/SLUG.json
#    fill every empty field the scaffold lists in each question (docs/specs/PAGE-BLUEPRINT-COMPONENTS.md says what each is for); never edit a stem
python3 Shared/tools/owner_bank.py check TEST/question-bank/SLUG.json --intake workspace/intake.json

# 2  a package (capabilities first; concepts for Core1A later), then the manifest
python3 Shared/tools/product_manifest.py derive --package TEST/library/SLUG.v1.json --bank TEST/question-bank/SLUG.json \
    --product-id SLUG --home ../../../index.html --intake workspace/intake.json --out TEST/products/SLUG.manifest.json
#    then edit the manifest: "output_roles" = the Cores the Owner asked for, for example ["CORE2"] (without it all six are rendered);
#    "diagnostic" = the ids of three owner questions to show as "start here" on the product's index page

# 3  Core2 on the TEST tab
python3 Shared/tools/deploy_test.py product TEST/products/SLUG.manifest.json

# 4  the ladder and the Atlas
python3 Shared/tools/build_web_data.py                      # the Atlas reads the matrix and package through public/data/data.js (it also rewrites the generated copy tools/data.js; leave both as written)
python3 Shared/tools/deploy_test.py pages                   # rebuild the TEST pages and the Pages mirror

# 5  Core1A: extend the package, add "CORE1A" to output_roles, then step 3 again
# 6  the explorer for the toughest concept
python3 Shared/tools/toughest_concept.py TEST/products/SLUG.manifest.json                # which concept that is, and why
python3 Shared/tools/explorer_build.py new TEST/products/SLUG.manifest.json              # writes TEST/interactive/SLUG/explorer.json
python3 Shared/tools/explorer_build.py check TEST/interactive/SLUG                        # repeat until it says no error
python3 Shared/tools/deploy_test.py interactive TEST/interactive/SLUG

# checks
python3 Shared/tools/deploy_test.py pages --check           # the TEST pages and the Pages mirror (docs/) are current
python3 Shared/tools/site_nav_audit.py                      # no line may start with NEW
python3 Shared/tools/matrix_conformance.py                  # the rung matrix (the Rungs page shows its findings too)
```

`self_check.py --unit` writes its report under `publication/` (git-ignored), outside TEST/; run it only if the method asks you to, and say so.
A deploy prints `matrix ...` lines when a rung matrix breaks the matrix schema (for example `ladder_position` above 100): fix the matrix.

`deploy_test.py product` renders the manifest as a draft (gaps allowed), stamps every page with the TEST banner,
writes `public/test/products/SLUG/` and a receipt (`accepted: false`), then rebuilds the TEST pages and the Pages mirror.
It prints each gap (a thing the page still lacks, with the record it is about); the receipt and the Deployments page list
them all. A package or bank that fails the schema is refused with up to six problems named together and nothing written.
It refuses a manifest that is not under `TEST/`, whose subject is not `TEST`, or that uses records outside `TEST/`.
It sets the page links for its location, so `--home` does not have to be exact.

## An explorer

The interactive page of a TEST job is an **explorer**, not a sandbox: a guided route through the one concept the question set is hardest on.
That concept is not your choice: it is the question whose difficulty is most conceptual (`python3 Shared/tools/toughest_concept.py MANIFEST` names it and says why), and the
Core1A page is built toward the same question. A spec for any other question is refused, and so is a page that could be played with before anything is predicted.

You do not write HTML or JavaScript. You write the **content** of each step as data (`explorer.json`); `Shared/tools/explorer_build.py` writes the page (a layout made for a 12.7-inch
tablet, the locking, the behaviour, the accessibility) and `Shared/tools/explorer_model.py` checks every number in it, at every position the learner's sliders can reach. The blueprint is
`BP-EXPLORER-GCDR`, from the repo's own standard for explorers ([docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md](../docs/GRAPHICAL-COGNITIVE-DECONSTRUCTION-BLUEPRINT.md));
read it as [docs/specs/PAGE-BLUEPRINT-COMPONENTS.md](../docs/specs/PAGE-BLUEPRINT-COMPONENTS.md), where each component says what to write.

**The route the learner walks** (each step opens only when the one before is done):
CONTEXT (the question, word for word) → PREDICT (the sliders stay locked until a prediction is locked in) → MANIPULATE (reach goals on the sliders) → OBSERVE (judge statements; the page
checks each against the whole model) → CONTRADICT (impose the tempting wrong model and see it fail, in the picture and on a graph) → DECONSTRUCT (the hidden mechanism appears one cause at a time)
→ RECONSTRUCT (build the mathematics from it; the closed-form equation is checked equal to the quantity) → INVARIANT (try to break what survives every position) → BOUNDARY (where the
shortcut holds and where it fails) → FADE (three levels, with less help each time) → TRANSFER (a fresh task, with the explorer closed, and the way back to the question).

**What you write**, in the order the scaffold lists it:

- the **state**: `parameters` (the sliders, each with min, max, step and a starting value; and the givens of the question with `"fixed": true`) and `quantities` (every number the page shows, as an
  expression of the parameters and the quantities before it: `"expr": "sqrt(a^2 + b^2 + 2*a*b*cosd(theta))"`; no number is typed anywhere, the page computes them);
- the **picture**: `scene.elements` of kind point, segment, arrow, circle, arc, polygon, curve or text, with coordinates as expressions, a role (object, given, result, wrong, helper, frame) and when it
  appears (`reveal`: start, manipulate, contradict, deconstruct), and a `second_view` graph of the quantity against a slider; `oracles` tie the drawing to the numbers;
- the **route**: the prediction and its options, the goals, the statements, the tempting model and the state where it visibly fails, the causes in the order they act, the steps of the
  working and the equation they compress into, the invariants, the boundary cases, the three fade tasks and the fresh tasks.

**The expression language**: `+ - * / ^ ( )`, comparisons, `and or not`, `if(c, a, b)`; `sqrt abs hypot min max clamp round floor ceil sign exp ln log10`; `sin cos tan asin acos atan atan2` in radians and
`sind cosd tand asind acosd atand atan2d` in degrees; `pi`, `e`. Write `2*a*b`, never `2ab`. A quantity that is not a number somewhere the sliders reach (a division by zero, a root of a
negative) is an error that names the position. For claims about the whole model (predictions, statements, invariants, answers) four forms read it: `at(R, theta, 90)` is R with theta set to 90,
`maxover(R, theta)` and `minover(R, theta)` its largest and smallest over the slider, `argmax(R, theta)` and `argmin(R, theta)` where they are. In a sentence, show a number as `{R:1}` (R, one
decimal) and the page computes it; a decimal you type into a sentence is flagged, because nothing checks it.

**What the check holds the spec to** (an *error* stops the deploy: the page would show something false or break; a *gap* is reported and the page deploys as a draft):

- the explorer is for the toughest concept (error);
- every number is a number at every position of the sliders (error);
- the right prediction is the one the model supports, and each wrong option is refuted by a test that fails (error); a statement said to hold always does, and one said not to has a position that
  shows it (error); a goal can be reached on the slider's steps and is not already met at the start (error);
- the tempting model is wrong somewhere (error) and is drawn in the picture and on the graph (gap);
- the equation equals the quantity at every position, and is written with the parameters only, not as the quantity's own expression (error); each invariant holds at every position (error);
- every element stays inside the picture at every position, and each oracle (the drawing against the numbers) holds (error);
- each boundary case's shortcut holds or fails as declared, with at least one of each (error / gap); a fresh task uses numbers the learner has not seen (error);
- the reference depth of the blueprint: three prediction options, three goals, four statements, four causes, three steps of working, two invariants, three boundary cases, three fade levels, three
  fresh tasks (gaps).

`explorer_build.py check` prints each finding with the component it belongs to and the blueprint's own instruction for authoring it. Zero gaps is the standard.

**An example of the format.** [tests/fixtures/explorer/projectile-range.explorer.json](../tests/fixtures/explorer/projectile-range.explorer.json) is a complete spec for a different concept (the range
of a projectile). It shows what each field looks like; its sentences are about projectiles and are not yours to reuse: a spec that repeats two of them is refused.

`deploy_test.py interactive` builds the page, refuses a spec with an error (nothing is written), and otherwise deploys `index.html` with the TEST header, `explorer-contract.json` (the design
contract of `Shared/library/explorer_design_contract.schema.json`, `IMPLEMENTATION_PARTIAL`, audit `NOT_RUN`: no machine here certifies it) and `explorer-evidence.json` (what the check computed),
plus a receipt. The end of the route links back to the question on the product's Core2 page and to its Core1A concept book when the product is deployed, so **deploy the product first**.

A page written by hand (`TEST/interactive/SLUG/index.html` and `interactive.json`, schema `grade9v3-test-interactive-v1`) is still accepted as a draft, but the receipt and the Deployments page say it is
hand-written, that nothing in it is machine-checked and that it is not built from the explorer blueprint. It needs a viewport meta tag, may load nothing from another host and may carry no facts of its own.

## Limits

- TEST has a contract (`TEST/adapter/`) and no adapter: no scenes and no validators of its own. An explorer's numbers are checked by the explorer model against the spec's own expressions (that the
  page agrees with itself and with its equation), not against a subject authority: whether the physics or the mathematics in the spec is the right one is for the Owner to decide.
- Owner-supplied banks are used only here. Official exam banks are unchanged; an owner bank may not live in an `exam-bank/` directory, and TEST is not part of the public Question Bank. The general design question is issue #371.
