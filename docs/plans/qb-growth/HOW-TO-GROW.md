# Growing the Question Bank: where things live and how to add to them (#359)

For an agent or engineer who has never seen the history. Everything here is checked by a test or a
command named in the same line; if a statement stops being true, that check fails.

## The one rule

The browser knows no subject, topic, subtopic, count or resource. It learns all of them from generated
files. So growth is done in canonical records, then `generate`, then `check`. Never in
`public/js/question-bank.js` (a test fails if it names a subject or topic from the corpus) and never by
hand in `docs/` (it is generated).

## Where truth lives (edit these)

| What | Canonical location | Notes |
|---|---|---|
| Competitive-exam questions | `<Subject>/library/exam-bank/competitive-exam-question-bank.v2.json` | picked up by `build_question_bank_web.py` |
| Package-shaped questions | `<Subject>/library/*.json`, `questions[]` | included **only** if the package or the question has `extensions["grade9v3:question_bank"] = {"include": true, ...}`. The browser metadata (`difficulty` with a `band`, `learner_question_type` or `question_type`, `expected_time_seconds`) comes from the question's `extensions["grade9v3:analysis"]` or from that opt-in block; if any is missing the build raises and names the question |
| Topics | a bank question's topic is `extensions["grade9v3:analysis"].topic`; a package question's is `topic_label` in the opt-in block, else the package title | an exam-bank topic has only a label-derived identity today (`identity_basis: LEGACY_LABEL_DERIVED` in the catalog), so renaming its label changes its ref. A package question can pin a stable `topic_ref` in the opt-in block (`EXPLICIT_REF`). Carrying an explicit topic ref through the exam-bank projection is not done |
| Subtopics | a question's `primary_capability_ref` and `secondary_capability_refs` | a subtopic is titled from the one microtopic in a library package that names it as `primary_capability_ref`; a ref with no owner or several owners stays `REF_ONLY` and is counted in `counts.subtopics_without_title` |
| Resources (Study Clinics, banks, explorers) | `<Subject>/question-bank/resources.v1.json` (schema `grade9v3-question-bank-resources-v1`), plus explorer suites discovered from `docs/gcdr-suites/*.json` (those with a `REPO_BUNDLE` delivery artifact) | each registry record needs `id`, `kind`, `title`, `path`; `path` is relative to `public/` and must exist; add `topic` or `topic_ref` to attach it to a topic; `kind` is a shared vocabulary (`study_clinic`, `question_bank`, `interactive`, `explorer`, `worked_examples`, `revision`, `representation`, `assessment`, `reference`). **A resource appears in a topic banner only when its `topic_ref` equals that topic's**: a discovered suite takes its topic from its own `external_corpus.topic`, which usually differs from the question topic, so it is searchable but not linked from the banner until the two are joined (see the last section) |
| Saved collections | `Shared/tools/question-bank-views.v1.json` | resolved to question ids at build time; an id that names no question fails the build |

Nothing else holds question, topic or resource facts. The generated files below only project these.

## What is generated (never edit)

| File | Holds | Read by |
|---|---|---|
| `public/data/question-bank-manifest.js` | build id, which artifacts to load and whether each is required, detail shard paths | the page, first |
| `public/data/question-bank-catalog.js` | subjects, topics, subtopics with counts and labels; saved views | tabs, topic and subtopic strips, stats |
| `public/data/question-bank-questions.js` | one summary per question (what a result card and the filters need) | result list |
| `public/data/question-bank-search.js` | compact search documents, questions and resources | search |
| `public/data/question-bank-resources.js` | resource records | topic banner (optional: the page works without it) |
| `public/data/question-bank-details/*.js` | full question detail, one shard per subject | Study, on demand |
| `artifacts/question-bank/build-receipt.json` | build id, inputs, per-worker input and output digests, counts, `near_duplicate_search_complete` | audit |
| `artifacts/question-bank/dedup-report.json` | duplicate, variant and near-duplicate evidence and how much of the corpus the near-duplicate search covered | review |
| `artifacts/question-bank/lineage.json` | question to source, membership, adapter and build | `--explain` |
| `public/data/question-bank-data.js` | the older monolithic projection, still read by the site header's search | header search |
| `docs/**` | deployment mirror of `public/` | GitHub Pages |

## Regenerate and check, in this order

```
python3 Shared/tools/build_question_bank_web.py            # older projection (also --check)
python3 Shared/tools/build_question_bank_platform.py --write
python3 Shared/tools/build_pages_site.py                    # docs/ from public/
python3 Shared/tools/build_manifest.py                      # architecture manifest last
rm -rf publication/                                         # build_manifest leaves a git-ignored registry that breaks two resolver tests
```

`--check` on each of the first three, and on `build_manifest.py`, reports drift without writing.
`python3 Shared/tools/build_question_bank_platform.py --explain <question id>` prints one question's
lineage: canonical record, membership, provenance, normalising worker, generated artifacts, search
document, browser id, build id, and whether the committed `public/` and `docs/` copies equal what the
build would generate.

## How search gets populated

`build_search_index` turns every question and resource into one document during the platform build. There
is no second registry to edit: add a canonical record, regenerate, and it is searchable. The browser
search (`Grade9QuestionBankData.search`) is DOM-independent and finds at least every question the
original in-page search found (`tests/question_bank_search_parity.test.mjs`).

## How to read the dedup evidence

Nothing is deleted. Each finding classifies a relationship: `DUPLICATE` (same canonical content after
normalisation, or the same source identity and structure), `SOURCE_COLLISION` (same source identity,
different content), `VARIANT` (an explicit shared `family_ref`, kept distinct), `NEAR_DUPLICATE` (very
similar wording; candidate for a human decision), `DISTINCT`. A duplicate canonical id fails the build.
The near-duplicate search is bounded, so read `near_duplicate_coverage` first: `complete: false` means it
skipped shared wording in a crowded topic and "no near duplicates" is not established.

## Add a subject, topic or subtopic: what to do

1. Put the questions in canonical records (table above) with a stable `topic_ref` and capability refs.
2. Give each capability an owning microtopic in a library package if you want its subtopic shown; until
   then the page shows the topic but not its subtopic strip, and the build counts the gap.
3. Add Study Clinics and interactive pages as resource records with `topic_ref`.
4. Regenerate and check as above. The subject appears as a tab, its topics and subtopics as strips, its
   counts from the catalog, search results, and resource links, with no code change.

`tests/question_bank_runtime_browser.mjs` proves this end to end on a synthetic Biology subject (two
canonically titled subtopics, a saved view, a Study Clinic and an interactive resource) and fails if the
runtime or stylesheet names a subject or topic.

## The contracts between workstreams

Two workstreams can proceed without touching each other because each side depends only on a named
contract, not on the other's code.

| Producer (Python) | Contract | Consumer (browser) |
|---|---|---|
| `question_bank_platform.py`, `build_question_bank_platform.py` | the manifest lists artifacts by path and `required`; every artifact carries the manifest's `build_id`; catalog, summaries, search and resource shapes as emitted (schema strings in the files) | `question-bank-data-service.js` loads them in order and rejects any artifact of another build |
| `question-bank-data-service.js` | `bootstrap`, `readiness`, `summaries`, `views`, `resources`, `search`, `loadDetail`, `loadQuestion`, `reset` and the `QB_*` error codes | `question-bank.js` (page), the site header |
| `question-bank.js` | URL state: `view q subject topic subtopic difficulty exam type mode sort` and a question id in the hash; stable ids are written, labels are still accepted | links, bookmarks |

Producers may add fields and artifacts. They may not change a shape a consumer reads without a new
schema string. Consumers may not read anything the manifest does not name.

## Determinism

The build is a graph of named workers. Any schedule of independent workers (serial, reversed, shuffled,
parallel) and any process gives the same output digest (`tests/test_question_bank_determinism.py`), so a
worker may be run alone (`run_nodes`) and its receipt compared.

## Measurements and limits

`docs/plans/qb-growth/SCALE-DECISION.md` records what was measured and what it decides (no Web Worker and no
index sharding at the current target; where to revisit). Not yet done:
- the site header's search still uses the older monolithic file;
- subtopics for topics whose capabilities have no owning microtopic (2 of 5 live topics show them);
- joining resources to question topics: 6 of the 8 live resources (the explorer suites) carry a topic
  label that is not any question topic's, so no topic banner links them. The fix is data, not code: record
  which question topic each suite belongs to (for example an explicit `topic_ref` in the subject's
  `resources.v1.json`) and let the build honour it;
- an explicit topic ref for exam-bank topics (see the topics row);
- a per-topic work budget for the near-duplicate search.
