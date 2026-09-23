# Grade-9 Physics exit and Grade-10 transition report

This view is a **derived report** over the existing Grade-9 scope audit and learner-evidence contracts. It is not a mastery percentage, probability, certification database, or new learner-state owner.

## Evidence categories

- `SECURE`: existing learner evidence proves independent demonstration.
- `USABLE_BUT_FRAGILE`: there is demonstrated work, but independence is not proven; carry an unassisted recheck.
- `KNOWN_GAP`: evidence explicitly records missing understanding/performance.
- `INSUFFICIENT_OR_UNKNOWN`: the repository does not yet have enough evidence to decide.

Unknown evidence is neither mastery nor failure.

## Current repository evidence baseline

The current repository does **not** contain a live measured Grade-9 learner evidence set. `Learners/profiles/` contains two design-preview profiles with `UNKNOWN` provenance and no observation references, and there is no `Learners/observations/` directory on this branch.

Therefore the current programme-level learner disposition is **evidence incomplete**, not “Grade 9 failed” and not “Grade 10 ready”. The repository has enough canonical scope and routing machinery to make the transition decision once reviewed learner observations exist, but it must not manufacture that empirical evidence from authored coverage, profile estimates, or question inventory.

The next learner-facing action is bounded evidence acquisition through the existing study-start/session machinery:

1. start from the six required Grade-9 matrices and their genuine prerequisites;
2. with no prior estimate/evidence, use the existing bounded gateway behaviour (at most one representative uncertain/unobserved `QUICK_CHECK` per matrix in a route);
3. treat `QUICK_CHECK` as an attempt opportunity, never as evidence by itself;
4. persist only reviewed observations of what the learner actually did, with direct/no-help attempts carrying the independent-evidence meaning already owned by `learner_evidence.py`;
5. repair explicit known gaps, independently recheck fragile success, and rerun this derived exit view as evidence changes.

This is deliberately not a one-shot blanket recertification battery. Existing evidence is reused; only unresolved required/prerequisite uncertainty is investigated, and optional/enrichment/later-grade material stays non-blocking unless a separate authority makes it relevant.

## Transition interpretation

The report distinguishes three decision situations rather than forcing a binary grade verdict:

- `KNOWN_BLOCKER`: a required Grade-9 or genuine prerequisite gap is explicitly known. Repair it and obtain fresh verification before transition.
- `EVIDENCE_INCOMPLETE`: there is no known blocker, but required/prerequisite evidence is still unknown. Gather fresh evidence before claiming that Grade 10 is the next productive frontier.
- `GRADE10_WITH_TARGETED_RECHECKS`: there is no known blocker or unknown required evidence, but required/prerequisite evidence is usable-but-fragile. Grade 10 may begin while those items receive fresh independent rechecks.
- `GRADE10_NEXT_PRODUCTIVE_FRONTIER`: there is no known required/prerequisite blocker, unknown required evidence, or fragile required/prerequisite evidence.

Enrichment, later-grade sophistication, and other non-blocking scope remain visible in both machine and parent/agent views but do not block merely because evidence is absent or a gap is known.

## Usage

Machine-readable projection:

```bash
python3 Shared/tools/grade9_exit.py --profile-id <PROFILE_ID>
```

Parent/agent-readable Markdown:

```bash
python3 Shared/tools/grade9_exit.py --profile-id <PROFILE_ID> --format text
```

Every reported capability carries its scope role, evidence category, evidence trail, blocker disposition, repair/recheck action, and transition implication. When earlier difficulty is followed by fresh independent evidence, both observations remain visible rather than being overwritten.

Changed-demand identity is derived only when a canonical question has both a `CORE2B` exposure and transfer metadata. Availability, direct learner observation, and transition-requiredness are reported as separate facts. Current Grade-9 scope/Owner authority does not declare authored changed-demand inventory itself to be a transition requirement, so an available but unobserved changed-demand task remains visible and non-blocking. If future explicit transition authority requires such evidence, the report can represent that as `EVIDENCE_NEEDED` without creating new learner truth.

The report is recomputed from source truth and is not persisted as grade readiness.
