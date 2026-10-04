# ISS29 B-agent audit workreport

## Objective and authorization

Owner requested capturing Chemistry owner-bank/runtime friction in issue #29 and rigorous compilation of completed B-agent PRs. Classification: AUDIT/REVIEW. Candidate code, production code, issue prompts and branches remain unchanged. No agents launched/assigned, PRs retargeted, merges or publications. Owner assigns agents.

## Ground truth

Four frozen heads and launch seed are pinned in REPORT.md and grounding.json. Candidate bytes fetched from GitHub and compared against Git blob hashes. Executed repository code/JSON checked against the launch seed (76 checked files, zero mismatches). Local partial materialization is not a full checkout; unused historical fixtures differ and were not used for full-suite claims.

## Delivery denominator

1. Repository friction: captured in #29 kickoff comment 5978132952; path/API distinction and missing-runtime distinction incorporated in report.
2. Four-head artifact compilation: complete for the pinned B submissions.
3. Independent prompt/stem/custody/schema/selection/render reproduction: executed, all four page sets byte-equal; details in checks-ISS*.json.
4. Direct owner-bank CLI and static quality checks: executed; raw outputs and verdicts preserved, including failures/exit-code distinction.
5. Independent answer review: 40 questions, answer/reason/check ledger complete within reported scope; six shared finding groups and linked primary-source identity verification.
6. SVG XML/raster inspection: 13 assets executed; NOT a browser certificate.
7. CI attribution: eight target-specific job logs inspected; evidence recorded with job URLs and relevant lines.
8. Handover: report, ledger, scripts, results and recommendations prepared on isolated audit branch, linked from #29 after durable commit.

## Validation and limitations

Source-coupled artifact checks and independent chemistry oracles are identified separately. Package validation used official jsonschema 4.17.3 plus an explicit URN/local resolver. Default CLI environment lacks jsonschema; full renderer/toughest CLI is NOT certified. Standard owner-bank CLI was run directly. Static quality CLI report verdicts were observed; CLI report-schema validation was skipped by that tool when jsonschema was unavailable, which is explicitly disclosed. Chromium/Firefox executables are unavailable; browser NOT_RUN. No full suite, full 480-facet semantic certification, exhaustive literature validation, A-versus-B comparison or learner study claimed.

## Current disposition and continuation

All four are frozen candidates requiring repair, not golden fixtures. Preserve original heads, request correction rounds with finding IDs/parent hashes after independent A freeze, then measure exact Chemistry products in a real browser and compare both candidates against common concept oracles. Owner's A/B/C input remains minimal; audit duties stay separate. Keep Core1A revamp and Core2 structural-addition scope. No production code work resumed by this audit.

## Reproduction

Place pinned candidate changes over pinned seed source in isolated `ISS32`, `ISS34`, `ISS36`, `ISS38` directories adjacent to the audit scripts. Frozen bodies are preserved in `issue-bodies.json`; the original issue-inputs.json with discussion snapshots is also accepted by the checker. Core prompt blocks are committed in each candidate.

Run `inspect_candidate.py ISSUE` with jsonschema installed and the repository's schema resolver supported. The script uses an explicit resolver, does not monkeypatch production validators and writes independently regenerated pages into `reproductions/`. The renderer API route and schema check are disclosed rather than passed off as original CLI execution.

`additional_checks.py` needs lxml and writes artifact/hint/template/electron-count/cosine observations. `write_question_ledger.py` materializes the human-reviewed ledger without consulting candidate self-ratings. Direct CLI commands are recorded verbatim in owner-cli-results.json and quality-static-results.json. Their output is evidence, not an agent-provided free-text success assertion.
