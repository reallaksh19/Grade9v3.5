# QRT Minimal-Prompt Pipeline

## Goal

The owner may provide only repository/implementation context plus ordinary questions and the requested learner-facing HTML/QRT evidence. The repository carries the rest of the workflow.

The owner is asked only for genuinely owner-owned missing information such as learner purpose and idea-level learner knowledge when those facts materially change support. The agent remains responsible for academic verification, difficulty, demand, QRT selection, X/Y/Z/W, hint/representation/misconception design, Core2/Core1A authoring decisions and rendering.

## Governing flow

```text
VERBATIM OWNER PROMPT
        |
        v
minimal-prompt intake
        |
        +-- ask missing learner purpose/knowledge only
        |
        v
owner-event-backed learner profile
        |
        v
candidate canonical question records
        |
        +-- academic solve/verification
        +-- five-component D1-D4
        +-- primary/secondary demand
        |
        v
QRT resolver (1 of 28 cells) + subject adapter
        |
        v
QuestionPedagogyRecord
X / demonstrated Y / Z / protected W
        |
        v
ITEM SELF-AUDIT BEFORE RENDER
every hint / solution move / calculation
has per-check result + evidence + basis refs
        |
        +-----------------------------+
        |                             |
        v                             v
Core2 records                 ConceptEvidenceRecords
        |                             |
        |                      + canonical truth refs
        |                             |
        |                         Core1A records
        |                             |
        +-------------+---------------+
                      v
               active Blueprint
                      v
                 render_core
                      v
               HTML / PDF bytes
                      |
                      +-- governed explorer -> mandatory Chromium audit
                      v
          independent exact-render QRT
          H1-H3 S1-S3 P1-P3 M1-M3
                      v
           findings -> fix -> rerender
                      v
     academic / static / browser / print
           evidence kept as separate layers
```

## Owner truth and custody

The exact owner prompt is immutable evidence. A normalized fixture or candidate record is derived data and must carry the prompt digest; it never replaces the prompt as authority.

Questions present in the owner's prompt may be labelled `OWNER_SUPPLIED` as an **agent custody interpretation**. That label is not an owner clarification reply and makes no external provenance claim.

Learner purpose, learner knowledge and explicit special directives must cite an actual owner event. Do not manufacture a reply or convert an agent assumption into `OWNER_ESTIMATE` evidence.

## QRT slot invariants

- **X** is the learner-specific bottleneck/misread. It must not contain the verified answer and must not simply copy Z or W.
- **Y** is a bridge backed by a `DEMONSTRATED` capability in the owner-event-backed learner profile.
- **Z** is the route/crux support should open toward.
- **W** is the decisive learner-owned move and carries a protected move ref where addressable.
- Z and W are distinct whenever pre-attempt scaffolding is present. If a task truly has no useful separation, use `NO_PREATTEMPT_SCAFFOLD` rather than pretending a ladder can preserve W.

## Mandatory item-level author self-audit

Before rendering, every authored hint, every solution move and every calculation must carry its own self-audit.

This is not a generic `PASS` field. Each item records:

- `status`;
- summary evidence;
- basis refs;
- named checks appropriate to the item.

Each named check is itself an evidence-bearing record:

```json
{
  "result": "PASS | FAIL | NOT_APPLICABLE",
  "evidence": "specific evidence for this criterion",
  "reason": "required when NOT_APPLICABLE"
}
```

One generic sentence cannot satisfy several different checks. A failed criterion blocks the item; a `NOT_APPLICABLE` criterion requires a reason.

### Hint checks

Every hint is checked for:

- academic correctness;
- alignment to its intended objective;
- W protection;
- learner fit;
- non-redundancy;
- purpose fit;
- actionable specificity.

If a hint contains a calculation, it explicitly declares `calculation_bearing: true` and links to the audited calculation row. A hint with no calculation declares `false`.

### Solution-move checks

Every solution step uses the learner-facing architecture:

`Action -> Why valid here -> Result`

and is self-checked for:

- academic correctness;
- question specificity;
- reasoning validity;
- units/symbols;
- correct post-attempt scope.

Calculation-bearing solution steps link to the exact calculation audit rows they use.

### Calculation checks

Every authored calculation has a stable id, expression and result and is self-checked for:

- arithmetic/algebra correctness;
- units/dimensions;
- input traceability back to the question or a previously established result;
- an independent check.

A failed item self-check blocks rendering. Author self-audit is evidence of disciplined authoring; it does **not** replace independent post-render QRT review.

Run before render:

```bash
python Shared/tools/qrt_content_self_audit.py path/to/qrt-pipeline-run.json --phase authoring
```

`qrt_pipeline_precheck.py` also executes this item-level audit, so it cannot be bypassed by using the normal pre-render path.

## Purpose must change the learner-facing artifact

Recording `REVISION` or `COMPETITION` in metadata is not enough. When a new/updated run opts into
`purpose_delivery`, the exact rendered Core1A/Core2 bytes must contain the corresponding purpose projection.

- **REVISION** uses `REDUCED_SUPPORT` and a `NEXT_LEVEL` transfer attached to the same concept/question it extends.
  The transfer should be one meaningful step harder than the source item: an extra modelling decision, representation
  shift, or chained inference rather than a cosmetic number change.
- **COMPETITION** uses a `CHALLENGE_SET` / competition-transfer block. The transfer is mixed or less labelled and must
  not receive a purpose-specific hint ladder before attempt.
- A real IIT-JEE/IMO/past-paper identity is shown only when `source_kind=VERIFIED_COMPETITIVE_SOURCE` carries an
  inspectable HTTPS source ref and source label.
- Without that authority, use `AUTHOR_CREATED_COMPETITION_STYLE` and visibly label the item as original
  competition-style material. Never make an authored transfer look like an official past-paper question.

The run-level `purpose_delivery` evidence names the item ids projected into both Core1A and Core2. The completion gate
checks those ids against markers in the exact rendered HTML, so Revision and Competition cannot silently collapse to
the same artifact.

## Authoring is not review

The authoring record describes intended support. It is not a quality verdict.

After rendering, review the exact artifact bytes. Each question receives all twelve QRT judgements:

`H1 H2 H3 S1 S2 S3 P1 P2 P3 M1 M2 M3`

Applicable asks use `YES | PARTLY | NO` with evidence. `PARTLY` and `NO` require a fix. A genuine not-applicable ask records `NOT_APPLICABLE` plus a reason; it is not a fourth score.

The review record stores the rendered artifact SHA-256. A review of different bytes is stale.


### Exact question-to-page binding for new integration candidates (#313 I1a)

The existing `qrt-pipeline-run/v1` validator hashes full rendered HTML and checks all 12 judgements. A page digest alone does **not** establish that the reviewed *question* occurs in that page: a correct hash of a different page would be an apparently valid but misplaced review.

For a new/changed candidate opting into full identity evidence, set:

```json
{
  "review_requirements": {
    "independent_rendered_review_required": true,
    "question_anchor_binding_required": true
  }
}
```

The referenced `rendered_artifacts[]` row also declares `question_refs: ["Q-..."]` and points to **the same canonical HTML bytes** actually examined by the reviewer. The existing guard now requires each reviewed question to be both declared on that artifact **and present in an actual `<article data-g9-unit="Q-...">` opening tag**. It rejects unknown/duplicate question reviews, duplicated artifact IDs, absolute/path-escaping artifact paths and hash changes. Plain text, strings inside JavaScript or a different question's article cannot stand in for an exact article. This is structural identity binding; it does **not** assess whether the page's mathematics is good, whether reviewer identity is socially independent, or whether all reachable pre-attempt resources preserve W (the existing reachability audit remains mandatory).

The stricter flag is opt-in so historical runs do not acquire fabricated failures; new acceptance candidates should use it. A green validator here is **not** independent academic acceptance.

### Per-question scoped coverage and dependency freshness (#313 I1b)

`python Shared/tools/qrt_coverage_report.py --index docs/qrt-coverage-index.v1.json --out /tmp/qrt-coverage-report.json` recomputes a **read-only** result for the explicitly declared new/changed candidates, applying the **existing governed completion gate** rather than copying review status. It never creates 12-ask judgements, a reviewer identity, a source question or a published learner artifact.

The `qrt-coverage-index/v1` file is a work queue of the form:

```json
{
  "schema": "qrt-coverage-index/v1",
  "items": [{
    "question_ref": "Q-EXAMPLE",
    "run": {"path": "path/to/qrt-pipeline-run.json", "sha256": "sha256:FULL_SHA256_HEX"},
    "tracked_inputs": [
      {"path": "Shared/quality/question-demand-matrix.v1.json", "sha256": "sha256:..."},
      {"path": "Shared/vocabularies/cognitive-demand.v1.json", "sha256": "sha256:..."},
      {"path": "Shared/web/interactive-page-blueprints.v1.json", "sha256": "sha256:..."},
      {"path": "path/to/actual/question/source.json", "sha256": "sha256:..."},
      {"path": "path/to/actual/learner/profile.json", "sha256": "sha256:..."}
    ]
  }]
}
```

Every hash shown is **illustrative, not a valid receipt**. Record actual 64-hex SHA-256 hashes only after inspecting the relevant files. Each declared tracked input and the run itself is rehashed from the checkout on every audit; a changed source, changed profile, changed matrix/Blueprint source, changed run, or changed rendered HTML invalidates the candidate. The run must identify the actual checkout HEAD, require `INDEPENDENT_RENDERED` review and exact question/article binding, include all 12 H/S/P/M results, and pass the normal custody/QRT/author-audit/W-reachability/interactive completion gate.

A fully coherent reviewed candidate becomes **`REVIEW_EVIDENCE_COMPLETE_NOT_ACCEPTANCE`**, never `ACADEMIC_ACCEPTED`. `PARTLY/NO` becomes `SEMANTIC_REWORK_REQUIRED` even if the reviewer supplied a valid fix order. Missing or stale evidence becomes `REVIEW_REQUIRED_OR_STALE`. Human reviewer independence is still an adjudication, not proved by a name string. The summary carries separate `NOT_EVALUATED` for academic, source-rights and repository-wide acceptance.

The committed index starts intentionally **empty**, since no new cross-Core candidate has earned a complete reviewer-bound receipt. An empty preview reports `empty_scope=true` and `passed_scoped_evidence=false`; it **does not** assert zero QRT debt or full coverage. For a scoped candidate gate, run `--enforce-scoped`, which fails on empty, stale, incomplete or rework-required evidence. The existing QRT hardening workflow invokes the read-only preview and switches to strict enforcement when the index contains declared candidates.

**Remaining integration obligation:** automatic changed-question discovery and source-to-reachable-resource dependency enumeration beyond the explicitly recorded hashes need a later authority-scoped implementation. Do not call this bounded explicit-index mechanism universal 24×7 production acceptance or treat unindexed changed source as checked.

## Transitive protected-work policy

P1 covers every resource reachable before commitment, not only text inside the question card.

Build a pre-attempt reachability graph containing:

- difficulty/trap panels;
- hint payloads;
- figures/stages;
- helpers;
- Core1A links;
- interactive/explorer links;
- any other pre-attempt resource.

If any reachable node exposes W's protected move ref, the run fails. A resource that teaches W fully must be post-attempt or expose a safe pre-attempt mode.

## Core2 to Core1A boundary

Question batches emit `ConceptEvidenceRecord` data: recurring cruxes, misconceptions, representation needs and question refs. This evidence determines emphasis, not mathematical authority.

A Core1A publication candidate requires canonical academic truth/research refs in addition to question evidence. The pipeline refuses `PUBLISH_CORE1A` when those refs are absent.

Lineage is bidirectional:

- Core2 question -> exact Core1A repair/construction unit;
- Core1A unit -> contributing question refs.

A generic link to the top of Core1A is insufficient when a specific repair target exists.

## Blueprint truth

Every declared `BLUEPRINT_ID@VERSION` must exist in `Shared/web/interactive-page-blueprints.v1.json`. A page may conform to standalone shell rules without conforming to a Blueprint; do not invent a Blueprint name to make a page look governed.

Guided interactive explorers already have active repository authority: `BP-EXPLORER-GCDR@1.0.0`, authored through `Shared/tools/explorer_build.py` and validated numerically by `Shared/tools/explorer_model.py`. A QRT-linked explorer must use that active Blueprint when it claims explorer conformance. A hand-written interactive draft may still exist as a draft, but it must not claim `BP-EXPLORER-GCDR` conformance unless it satisfies that contract.

## Staged SVGs: Chromium verifies the reveal, not just the source file

A staged representation is **cumulative by default**. Stage 2 keeps Stage 1 geometry visible and adds its annotation;
Stage 3 keeps the earlier structure and adds the next layer. An author may opt into replacement semantics only with
`extensions["grade9v3:stage_mode"] = "REPLACE"`.

The Core-page Chromium audit clicks every stage control. For cumulative figures it fails if a later stage shows fewer
stage groups than its ordinal or loses structural SVG geometry (`path`, `line`, `rect`, `circle`, `ellipse`,
`polygon`, `polyline`). This catches the failure mode where labels such as `r`, `h`, `l` remain visible while
the cone/triangle itself disappears.

Run the tablet audit with enforcement when accepting learner HTML:

```bash
node tools/site-audit/core-page-audit.mjs path/to/rendered   --profile tablet-12.7   --http-root path/to/rendered   --enforce
```

## Interactive pages: Chromium is mandatory

A separate interactive/explorer page is not covered merely because Core1A/Core2 passed Chromium.

Every governed explorer (`BP-EXPLORER-GCDR@...`) and every rendered artifact declared as `EXPLORER`, `INTERACTIVE_HTML`, or `INTERACTIVE_PAGE` must be registered in the governed artifact inventory and audited with:

```bash
node tools/site-audit/interactive-page-audit.mjs path/to/interactive.html \
  --profile tablet-12.7 \
  --head <exact-head-sha> \
  --json path/to/interactive-audit.json
```

The audit launches **Playwright Chromium** across the four 12.7-inch target viewports and fails on browser/page errors, remote runtime requests, small touch targets, horizontal/wide-element overflow, keyboard-focus failures, invisible focus treatment, inaccessible SVGs or missing main/heading structure.

A Core2/Core1A reachability-graph node that links an interactive resource must name its `artifact_ref`. That artifact must exist in the governed artifact inventory, so an explorer cannot evade Chromium by being omitted from the receipt list.

The governed run stores a receipt containing:

- artifact ref;
- exact artifact SHA-256;
- exact head SHA;
- tool id;
- `engine: playwright.chromium`;
- `profile: tablet-12.7`;
- audit report path + SHA-256;
- `status: PASS`.

Changing the interactive HTML invalidates the receipt because the audit report itself records the HTML SHA-256.

`explorer_model.py` and the Chromium audit prove different things: the explorer model checks the authored numerical/mechanism model; Chromium checks the actual interactive learner page. A governed explorer needs both.

## Evidence and validation

Keep these verdicts separate:

1. `academic` — answer/reasoning verification;
2. `qrt_semantic` — exact-render H/S/P/M review and W protection;
3. `static` — standalone/static conformance;
4. `browser` — rendered layout, touch, overflow, SVG labels, keyboard interaction;
5. `print` — same-byte PDF/print receipt where applicable.

Interactive Chromium receipts are additional exact-artifact evidence inside the browser layer; they cannot be replaced by a static check or by explorer-model arithmetic checks.

Do not publish an aggregate self-certified `PASS`. Static conformance cannot prove browser behavior.

A governed run records:

- exact branch/head;
- exact owner prompt + digest;
- actual owner events;
- matrix/adapter/profile/Blueprint-registry digests;
- artifact paths + SHA-256;
- item-level self-audits for every hint/solution/calculation, including per-check evidence;
- review artifact SHA-256;
- interactive Chromium receipts where applicable;
- separate validation-layer evidence refs.

## Completion gate

Lower-level tools may be run while authoring, but the completion command is:

```bash
python Shared/tools/qrt_pipeline_gate.py path/to/qrt-pipeline-run.json
```

It combines the custody/QRT/exact-render guard with item self-audit and interactive-Chromium enforcement.

The gate fails closed on the audited failure modes, including fabricated learner provenance, normalized question text not present in the owner prompt, answer-bearing X, Y without a demonstrated bridge, Z/W collapse with scaffolding, transitive W leaks, invented Blueprint refs, missing item self-audits, missing per-check evidence, failed calculation checks, unbound render review, missing H1-M3 judgements, Core1A publication without canonical truth, broken bidirectional lineage, unregistered interactive resources, missing/stale interactive Chromium evidence and aggregate self-certification.

## Acceptance replay

Issue #10 at exact head `32f31cbecea0e3ffd8bb8a8bb466a41a7ebe424c` demonstrated that the short owner prompt can reach governed Core1A/Core2 HTML and a successful 12.7-inch Chromium gate. That run supersedes the earlier hand-authored PR #14 product defects as the current acceptance baseline.

The next replay should additionally emit this hardened run contract so that:

- the committed QRT record is bound to the exact rendered bytes;
- each hint/solution/calculation carries self-audit evidence for every named criterion;
- any future interactive explorer is registered under the existing explorer authority and carries its own exact-byte Chromium receipt.
