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
                      +-- interactive HTML -> mandatory Chromium audit
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
- non-redundancy.

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

## Authoring is not review

The authoring record describes intended support. It is not a quality verdict.

After rendering, review the exact artifact bytes. Each question receives all twelve QRT judgements:

`H1 H2 H3 S1 S2 S3 P1 P2 P3 M1 M2 M3`

Applicable asks use `YES | PARTLY | NO` with evidence. `PARTLY` and `NO` require a fix. A genuine not-applicable ask records `NOT_APPLICABLE` plus a reason; it is not a fourth score.

The review record stores the rendered artifact SHA-256. A review of different bytes is stale.

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

Interactive resources may use a separately governed standalone-resource contract until a real interactive Blueprint is admitted.

## Interactive pages: Chromium is mandatory

A separate interactive/explorer page is not covered merely because Core1A/Core2 passed Chromium.

Every rendered artifact with kind `INTERACTIVE_HTML` or `INTERACTIVE_PAGE` must be audited with:

```bash
node tools/site-audit/interactive-page-audit.mjs path/to/interactive.html \
  --profile tablet-12.7 \
  --head <exact-head-sha> \
  --json path/to/interactive-audit.json
```

The audit launches **Playwright Chromium** across the four 12.7-inch target viewports and fails on browser/page errors, remote runtime requests, small touch targets, horizontal/wide-element overflow, keyboard-focus failures, invisible focus treatment, inaccessible SVGs or missing main/heading structure.

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

## Evidence and validation

Keep these verdicts separate:

1. `academic` — answer/reasoning verification;
2. `qrt_semantic` — exact-render H/S/P/M review and W protection;
3. `static` — standalone/static conformance;
4. `browser` — rendered layout, touch, overflow, SVG labels, keyboard interaction;
5. `print` — same-byte PDF/print receipt where applicable.

Interactive Chromium receipts are additional exact-artifact evidence inside the browser layer; they cannot be replaced by a static check.

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

The gate fails closed on the audited failure modes, including fabricated learner provenance, normalized question text not present in the owner prompt, answer-bearing X, Y without a demonstrated bridge, Z/W collapse with scaffolding, transitive W leaks, invented Blueprint refs, missing item self-audits, missing per-check evidence, failed calculation checks, unbound render review, missing H1-M3 judgements, Core1A publication without canonical truth, broken bidirectional lineage, missing/stale interactive Chromium evidence and aggregate self-certification.

## Acceptance replay

Issue #10 at exact head `32f31cbecea0e3ffd8bb8a8bb466a41a7ebe424c` demonstrated that the short owner prompt can reach governed Core1A/Core2 HTML and a successful 12.7-inch Chromium gate. That run supersedes the earlier hand-authored PR #14 product defects as the current acceptance baseline.

The next replay should additionally emit this hardened run contract so that:

- the committed QRT record is bound to the exact rendered bytes;
- each hint/solution/calculation carries self-audit evidence for every named criterion;
- any future interactive explorer carries its own exact-byte Chromium receipt.
