# Issue 31 — production-input boundary

Status: **ROUND 2 / PARTIAL**. The custody-path defect is repaired; the render/runtime defect remains open.

## Finding preserved from the pinned seed

At `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`, `Shared/tools/owner_bank.py` documented and enforced only `TEST/question-bank/`. The renderer could recognise owner-bank records, so the mismatch was an authoring-path inconsistency rather than permission to change provenance.

Owner clarification `#issuecomment-5978104772` authorised the smallest repair while preserving verbatim text, digests, intake linkage, duplicate/answer/support validation, safe path handling, overwrite protection, and strict separation from `exam-bank/`.

## Repair

Commit `f1621cd167a569f85ea42909ad97db1060028db5`:

- retains `TEST/question-bank/<slug>.json`;
- adds `<Subject>/library/owner-bank/<slug>.json` only for an existing canonical subject with `adapter/CoreContracts.json`;
- resolves the destination before classification so path traversal/symlink escape cannot authorize an outside-repository write;
- refuses `exam-bank/`, unknown top-level subjects and non-JSON destinations;
- retains the existing no-overwrite default and `--force` opt-in;
- does not change the owner-bank schema, custody class, digests, stem checking, intake completeness, duplicate checks or official-identity prohibition.

This resolves the first blocker without relabelling the ten questions as official/PYQ.

## Separate runtime limitation

The current chat has a shell/container but no mounted checkout of this repository. An outbound Git probe failed with `Could not resolve host: github.com`. The GitHub connector can read/write repository objects and observe Actions, but it does not expose an interactive Python/Chromium checkout for arbitrary issue-specific authoring commands.

Therefore the following remain **NOT_RUN**:

1. create `Chemistry/library/owner-bank/issue31-hybridisation.json` through the repaired CLI;
2. create and validate the Chemistry hybridisation package;
3. derive the CORE1A/CORE2 manifest;
4. run `owner_bank.py check`, package resolver/schema validation and `render_core.py`;
5. inspect exact generated pages with the browser audit;
6. decide any builder-module change from the actual render.

No hand-authored HTML, alternate renderer, TEST-as-Chemistry substitution or invented exam identity is used.
