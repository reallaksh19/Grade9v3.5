# ISS66 U02B — retained/live layout replay

**Responsibility:** #66 blueprint/schema semantic-contract hardening  
**Task:** U02B only — replay affected Core1A/Core2 layout paths after U02A  
**Exact head under test:** `f7d82d09b0a27120650e8fac193ae977dae6a872`  
**Draft PR:** #67 targeting `feat/issue29-integrated-core-templates`

## Retained evidence replay added

`tests/test_blueprint_layout.mjs` now replays two frozen PR #65 artifacts through the patched layout-policy helper.

### Core1A retained browser facts

Source:

`evidence/staged-repair/ISS29-set-b/browser/core1a-layout-facts.json`

Frozen facts:
- blueprint: `BP-CORE1A-CONSTRUCTION@1.7.0`;
- articleCount: 3;
- columnCounts: `[1, 1, 1]`;
- viewport: 1280×800;
- selected policy: compact/medium/expanded all `SINGLE_PANE`;
- historical fractions retained: 0.6 / 0.4.

Replay expectation:
- `splitLayoutExpectation(...)` returns `null`;
- `matchesBlueprintLayout(...)` accepts the measured one-pane geometry.

### Core2 retained rendered page

Source:

`evidence/staged-repair/ISS29-set-b/rendered/core2.html`

Active blueprint:
`BP-CORE2-SOURCE-QUESTION@1.9.0`

Replay expectation:
- `splitLayoutExpectation(...)` returns 0.42 / 0.58 at 980px;
- the frozen rendered page contains:
  `grid-template-columns:minmax(0,42fr) minmax(0,58fr)`;
- `STAGE_SUPPORT` therefore retains its existing split behavior.

## Exact-head CI evidence

Workflow: `learner-platform-code-tests`  
Run: `37428937464`  
Event: pull_request  
Head: `f7d82d09b0a27120650e8fac193ae977dae6a872`

### Focused code-test job

Job `112154976318` — `code-tests`

Relevant step:
- **Existing blueprint layout observation regressions** — **SUCCESS**

The workflow file executes:

```text
node --test tests/test_blueprint_layout.mjs
```

Therefore the retained Core1A/Core2 replay tests and all earlier layout helper regressions passed on the exact branch head.

## Live Core1A browser evidence

Workflow: `core1a-tablet-browser`  
Run: `37428937476`  
Job: `112154976436`

The exact Core1A viewport audit reached the browser enforcement step.

Result:
- browser step failed **only** on the already-known:
  `phone-390x844: 200% zoom overflow=7px`;
- Core1A row reports `BP-CORE1A-CONSTRUCTION@1.7.0`;
- no `integrated lesson unexpectedly split into columns`, `expanded layout ...`, or support-fraction layout failure is reported;
- keyboard stage control, section navigation/history restoration, reduced-motion check and normal unzoomed overflow metrics remained present in the measurement output.

Interpretation:
- the patched layout-policy path is not producing the former false split expectation;
- the live browser workflow remains **non-green overall** because of the pre-existing 7px phone/200%-zoom finding;
- U02 does not repair or waive that separate responsive-overflow issue.

## Live Core2 browser limitation

Workflow: `learner-platform-code-tests` run `37428937464`  
Job: `112154976534` — `core2-v2-browser-audit`

The job failed before the shared tablet browser audit because the governed Motion-in-2D render refused to write with:

```text
2 gap(s): nothing written. Run render_core.py gaps or --draft.
```

This is not introduced by the U02B replay commit:
- the previous exact head `5ed8fdd7715b096ca90252ebe0520311703ac1b8` had the same `core2-v2-browser-audit` job conclusion = failure;
- U02B changed only the focused layout test file.

Therefore live Core2 browser execution is **BLOCKED_BEFORE_AUDIT by existing render gaps**, not evidence of a new layout regression.

The retained exact Core2 render remains the compatibility evidence for U02.

## U02 acceptance check

Declared U02 evidence requirement:
- reproduce the prior conflict;
- repair the shared contract if still needed;
- retain role compatibility;
- remove forced stage/support assumption from single-pane Core1A.

Status:
- prior conflict reproduced in U01/U02A;
- one shared policy helper now governs split expectation;
- Core1A retained/live evidence no longer shows a forced split requirement;
- Core2 retained `STAGE_SUPPORT` split remains intact;
- focused exact-head CI is green;
- broader browser limitations are preserved honestly and are outside this layout-authority repair.

## U02 result

**U02 COMPLETE and evidenced.**

Parent denominator:
- **P = 2/10 = 20%**
- **E = 2/10 = 20%**

No claim is made that:
- the repository is all-green;
- the 7px phone/200%-zoom issue is fixed;
- the Core2 browser suite is accepted;
- any stress-test candidate is golden.

Next bounded unit: **U03A — inspect the existing review-provenance/artifact-binding contract against its declared acceptance requirement before changing schema.**
