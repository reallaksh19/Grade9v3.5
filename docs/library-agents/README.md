# Research library agents

Three agents build a cited, reusable Physics library for CBSE Grades 9–11 and JEE. Every Core
(1, 1A, 1B, 2, 2A, 2B) later draws on it. The design assumes the agents are inexperienced
and may drift or invent facts, so none of them is trusted:

- **No quote, no claim.** A fact exists only as an evidence card whose verbatim quote
  `Shared/tools/evidence_check.py` re-finds on the cited page of a pinned, allowlisted source.
- **Nobody approves their own work.** The researcher collects evidence, the author writes
  records from that evidence without web access, and the verifier independently re-solves and
  checks. The board refuses a verification signed by the node's researcher or author.
- **Progress is derived, never reported.** `Shared/tools/library_board.py` computes each
  node's stage from the files on disk. An agent that says "done" while the board disagrees is
  not done.
- **Agents never pick their own topic.** Work orders come from the syllabus spine
  (`Physics/research/syllabus-spine.json`), pilot chapter first.
- **No escape states.** A failed check is a duty for a named role (see
  `Shared/workflows/research-first.v1.json`); nothing is parked as "held".

## Pipeline

```
spine node ──RESEARCHER──▶ evidence cards (quotes verified in pinned sources)
           ──AUTHOR──────▶ staging package records citing those cards
           ──VERIFIER────▶ independent re-solutions + field checks
           ──▶ VERIFIED ──▶ owner spot-check ──▶ promotion into Physics/library/
```

| Role | Guide | Writes only |
|---|---|---|
| Researcher | [RESEARCHER.md](RESEARCHER.md) | `Physics/research/acquisitions/`, `Physics/research/evidence/`, new MICROTOPIC nodes in `syllabus-spine.json` |
| Author | [AUTHOR.md](AUTHOR.md) | `Physics/research/packages/<chapter>.package.json` |
| Verifier | [VERIFIER.md](VERIFIER.md) | `Physics/research/verification/` |

## How many agents

At most three, one per role, because the roles must stay separate for independence. The
pilot (Motion in a Plane) starts with one of each.

The researcher is the bottleneck. Author and verifier wait at first, because they need cards
and records to work on. Once the board shows a steady queue, extra capacity goes to research:
a second researcher on `--lane 2/2` can replace one of the other roles for a while. An agent
never authors or verifies a node it researched.

## Shared commands

```sh
pip install jsonschema pypdf cffi
python3 Shared/tools/library_board.py --subject Physics --fetch             # board
python3 Shared/tools/library_board.py --subject Physics --next RESEARCHER   # your work order
python3 Shared/tools/evidence_check.py check --subject Physics --fetch      # all evidence
```

Source bytes are cached in `.source-cache/` (git-ignored). Only acquisition records (URL +
SHA-256) and cards are committed; `--fetch` re-downloads and refuses changed bytes.

## Git

All agents work on the branch `research/physics-library`. Before each work order run
`git pull --rebase origin research/physics-library`. Commit one node per commit
(`research(PHY-11-MOTION-IN-A-PLANE-08): …`) and push. Roles write disjoint files, so rebases do
not conflict. The owner merges the branch into `main` through a pull request.

## Owner duties (labels, never stops)

- Freeze reviewed spine nodes by setting `owner_frozen: true`.
- Spot-check about 10% of VERIFIED nodes: open the cited pages and compare.
- Promote VERIFIED staging records into `Physics/library/` (a separate reviewed step).
