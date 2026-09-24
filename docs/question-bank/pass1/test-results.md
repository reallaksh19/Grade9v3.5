# Pass 1 question-bank validation results

Issue: #216  
PR: #217  
Branch: `question-bank/pass1-provenance`  
Last checked: 2026-09-24

## Canonical bank under test

| Topic | Accepted |
| --- | ---: |
| Physics — Newton's Laws of Motion / NLM | 13 |
| Physics — Motion in 2D / Motion in a Plane, linear/projectile only | 15 |
| Physics — Motion in 1D, relative motion only | 3 |
| Chemistry — Redox Reactions | 26 |
| Chemistry — Some Basic Concepts / Mole Concept / Stoichiometry | 20 |
| **Total** | **77** |

No practice set or exam generation is enabled. The run manifest explicitly keeps corpus saturation unclaimed.

## Executable activity contract

PASS 1 is now governed by dedicated, machine-readable activity contracts rather than prompt prose alone:

- `Shared/library/competitive-exam-bank.schema.json`;
- `Shared/library/exam-source-verification.schema.json`;
- `Shared/library/question-bank-publication.schema.json`;
- `Shared/library/question-bank-run.schema.json`;
- `Shared/tools/competitive_exam_bank.py`;
- `docs/question-bank/pass1/run-manifest.json`.

The run manifest carries nine blocking gates:

1. `G0_SCOPE_FROZEN`
2. `G1_CORPUS_ENUMERATED`
3. `G2_SOURCE_AUTHORITY_CHECKED`
4. `G3_SOURCE_DISPOSITIONS_COMPLETE`
5. `G4_CANONICAL_ITEMS_VALID`
6. `G5_CONCEPT_REFS_RESOLVED`
7. `G6_ANSWERS_AND_DIFFICULTY_CHECKED`
8. `G7_COVERAGE_CLOSED`
9. `G8_PUBLICATION_CONTRACT_READY`

The validator is topic-neutral: bank paths, organizer hosts, forbidden scope terms and local concept registries are supplied by the run manifest rather than hard-coded into Shared tooling.

## Executed validation

### PASS — canonical question-bank contract

The dedicated `pass1-question-bank-contract` GitHub Actions workflow passes on the reconciled PR head.

It executes:

```bash
python Shared/tools/competitive_exam_bank.py
python -m unittest tests.test_competitive_exam_bank_contract tests.test_competitive_exam_question_bank
```

The activity validator reports **77 questions across 2 banks** with no contract findings.

The pre-existing PASS-1 invariant suite remains:

**PASS — 4,275 assertions, 0 failures** across all 77 canonical records.

The new contract tests additionally prove that:

- all four activity schemas are valid Draft 2020-12 schemas;
- the current 77-item bank closes the complete activity contract;
- a `SOURCE_UNVERIFIED` question is rejected if promoted into canonical custody.

## Validated invariants

- 77 unique canonical question IDs;
- 77 unique historical source identities;
- 77 canonical questions resolved to exactly one accepted authoritative ledger record;
- exact ledger paper URL / exam / year agreement with per-question source custody;
- official-organizer source hosts and subject-qualified original identifiers;
- honest `PYQ_ADAPTED` origin plus parent and changed-field custody;
- source refs and origin refs resolve;
- source hints remain distinct from authored scaffolds;
- reasoning route, crux move, independent answer check and rubric resolve;
- component-based D1-D4 scoring recomputes correctly and does not use exam prestige;
- capability/family/bucket refs resolve against canonical libraries or an explicitly declared local registry;
- donor registries remain present and donor candidates remain `SOURCE_UNVERIFIED` / quarantined;
- scope exclusions are supplied by the run manifest and enforced against canonical content;
- JEE Main 2026 accepted records preserve first-party paper custody plus official final-key authority;
- relative-motion coverage is three accepted official-parent items;
- donor claims `1D-Q16` and `REDOX-Q01` remain quarantined rather than being promoted;
- all blocking G0-G8 activity gates are present and closed before a PASS completion claim;
- publication semantics are declared independently of renderer pixel/layout implementation.

## Shared-schema conformance correction

The new package-record validation exposed a pre-existing inconsistency in the two v2 banks: 69 `answer.reasoning_route[]` moves used `kind: EXECUTE`, while the shared reasoning-move contract permits `REPRESENT | DECIDE | CONNECT | TRANSFORM | VERIFY`.

Those 69 reasoning moves were normalized to `TRANSFORM`. Scaffold `support_kind: EXECUTE` remains unchanged; execution support is valid scaffold vocabulary but was not a valid reasoning-state-transition kind.

## CI / repository status

The branch was reconciled with the integrated Core2/Core2A/Core2B architecture now on `main`.

Final validated head before merge: `11fb01570090ac3110523803dc3410b954ad2e2a`.

- PR #217 is **0 commits behind `main`** and GitHub reports it **mergeable**;
- `pass1-question-bank-contract` — **PASS** (run #16);
- `v31-relay` — **PASS** (run #1034);
- repository-wide `guardrails` — **PASS** (run #5106);
- full repository regression suite — **1,177 tests, PASS**;
- generated architecture/artifact consistency — **PASS**;
- topic-independence scan — **PASS**;
- all JSON documents parse — **PASS**;
- cross-Core progression ownership/lineage gate — **PASS**.

The PASS-1 v2 bank uses its governed extension layout for provenance and analysis metadata, while the earlier progression reader consumed the v1 layout. Integration therefore added a narrow v1/v2 compatibility read at the progression boundary; no learner-facing PYQ wording, source disposition or provenance class was changed.

The resulting family-level source-demand truth is explicit:

- `FAM-PHY-NLM-PRACTICE` — evidenced by the v2 bank;
- `FAM-PHY-KIN-2D-PRACTICE` — evidenced by the v2 bank;
- `FAM-RELATIVE-V` — now evidenced by **3** verified-parent v2 items;
- `FAM-PHY-NLM-INCLINE-MODELLING` — no longer receives an exact family-level anchor merely from the broader v2 NLM family mapping; it remains `SOURCE_DEMAND_NOT_YET_EVIDENCED` pending an explicit reviewed join.

The progression audit scans all **77** accepted v2 bank anchors while keeping competitive-bank evidence distinct from ordinary Core2 custody.

## Committed test contracts

`tests/test_competitive_exam_bank_contract.py` owns the activity-level schema/gate contract.

`tests/test_competitive_exam_question_bank.py` owns canonical question-bank invariants, including:

- counts and topic counts;
- provenance honesty and adaptation-parent resolution;
- source-ref and authoritative-ledger resolution;
- duplicate IDs/source identities;
- source hint / scaffold separation;
- answer verification and reasoning-route integrity;
- difficulty metadata;
- transfer-vs-same-family classification;
- concept/capability/family resolution;
- official paper/key custody;
- scope exclusions;
- donor preservation and quarantine.
