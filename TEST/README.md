# TEST: a sandbox subject for stress runs

TEST is a subject that exists so a test agent can prepare a learner product end to end without touching Physics,
Chemistry or Mathematics. **Nothing in TEST is curriculum, reviewed or accepted.** Its pages are labelled drafts,
`accept_product.py` refuses TEST, and no machine check here grants release.

On the site it is the **TEST** tab (`public/test/`, deployed as `docs/test/`): a hub, an **Atlas**, **Rungs** and
**Deployments** pages. They read what is in this directory and in `public/test/`; they say nothing is finished.

## The job, in order

1. **Core2**: the Owner's questions, kept verbatim, in an owner-supplied bank.
2. **Core1A**: the concept construction for the same topic.
3. **An interactive page** built from the same canonical records.

Each one is deployed to the TEST tab as a draft. Do them in that order; stop and record friction instead of guessing. (The intake lists the Cores it will make in alphabetical order, `CORE1A` before `CORE2`; that is not the order of work.)

## What a page must show: the blueprint

A Core page is built from its **blueprint** (`Shared/web/interactive-page-blueprints.v1.json`; read it as
[docs/specs/PAGE-BLUEPRINT-COMPONENTS.md](../docs/specs/PAGE-BLUEPRINT-COMPONENTS.md)). The blueprint names the page's components (for Core2: the
header, the stem, the conditions, the common wrong route, the representation card, the hint ladder, the numbered working, the answer
and the check), the column each sits in and how much each matters. The renderer builds the page from it, the quality gate judges the page against
it, and `owner_bank.py new` scaffolds exactly the fields it lists. So the way to a good page is to supply what the blueprint lists:

- **REQUIRED** and absent or too short: a *gap*, printed by the deploy with the record and the blueprint's own instruction for authoring it.
- **EXPECTED** and absent: an *advisory*, printed after the gaps. The reference page has it; write it where the question has one to give
  (a figure only where the question is about a picture; never invent one).
- Between a component's floor and the reference depth (a hint ladder of 2 rungs where the reference has 3) is an advisory too.
  `owner_bank.py check` holds a new bank to the reference depth.

Zero gaps does not mean the page is at the reference standard; read the advisories as well.

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
| Concepts, capabilities, Core1A material | `TEST/library/SLUG.v1.json` | a package (`Shared/library/package.schema.json`) with `"subject": "TEST"`. It needs at least one resource, bucket, capability and microtopic; every capability needs a microtopic whose `primary_capability_ref` names it, and every owner question a `family_ref` naming a question family in the package. The smallest complete example is `tests/fixtures/render/thin-kin-2d-motion.v1.json`; a real one is `Mathematics/library/linear-equations.v1.json`. Check it before you build a manifest with `python3 -m Shared.library.resolve --schema TEST/library/SLUG.v1.json` (the schema, up to six problems at a time, then the references; without `--schema` it checks references only). |
| Product manifest | `TEST/products/SLUG.manifest.json` | made by `product_manifest.py derive` (below) |
| Interactive page source | `TEST/interactive/SLUG/index.html` and `interactive.json` | see "An interactive page" |

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
python3 Shared/tools/build_web_data.py                      # the Atlas reads the matrix and package through public/data/data.js
python3 Shared/tools/deploy_test.py pages                   # rebuild the TEST pages and the Pages mirror

# 5  Core1A: extend the package, add "CORE1A" to output_roles, then step 3 again
# 6  the interactive page, then
python3 Shared/tools/deploy_test.py interactive TEST/interactive/SLUG

# checks
python3 Shared/tools/deploy_test.py pages --check           # the TEST pages and the Pages mirror (docs/) are current
python3 Shared/tools/site_nav_audit.py                      # no line may start with NEW
```

`deploy_test.py product` renders the manifest as a draft (gaps allowed), stamps every page with the TEST banner,
writes `public/test/products/SLUG/` and a receipt (`accepted: false`), then rebuilds the TEST pages and the Pages mirror.
It prints each gap (a thing the page still lacks, with the record it is about); the receipt and the Deployments page list
them all. A package or bank that fails the schema is refused with up to six problems named together and nothing written.
It refuses a manifest that is not under `TEST/`, whose subject is not `TEST`, or that uses records outside `TEST/`.
It sets the page links for its location, so `--home` does not have to be exact.

## An interactive page

`TEST/interactive/SLUG/interactive.json`:

```json
{"schema": "grade9v3-test-interactive-v1", "slug": "SLUG", "title": "...", "purpose": "what the learner manipulates, what becomes visible, which misconception it targets",
 "records": ["canonical record ids the page is built from"], "blueprint_ref": "a blueprint id, or NONE", "status": "DRAFT"}
```

`index.html` needs a viewport meta tag and must not load anything from another host (the site works offline); every
file it links must be in its folder. Only `.html .css .js .json .svg .png .jpg .webp .txt`, at most 30 files of 2 MB.
The deploy adds the TEST header (draft label, links to the portal and the TEST pages) to the page; do not add your own.
The academic content comes from the canonical records; the page may not carry its own facts. There is no registered
explorer blueprint yet (`Shared/web/interactive-page-blueprints.v1.json` has the six Core blueprints only): if you use
none, say `NONE` and record that as friction.

## Limits

- TEST has a contract (`TEST/adapter/`) and no adapter: no scenes and no validators, so no quantitative claim here is machine-checked by the subject.
- Owner-supplied banks are used only here. Official exam banks are unchanged; an owner bank may not live in an `exam-bank/` directory, and TEST is not part of the public Question Bank. The general design question is issue #371.
