# Library agent prompts

Paste-ready prompts for the agents that build the cited Physics research library. The role
rules they point to live in `docs/library-agents/`; these files only start an agent.

| File | Agent | Where it runs | Start it when |
|---|---|---|---|
| `01-researcher.md` | Researcher (web) | cloud session | any time; it feeds everyone else |
| `02-author.md` | Author (no web) | cloud session | the board shows a node at the AUTHOR stage |
| `03-verifier.md` | Verifier | cloud session | the board shows a node at the VERIFIER stage |
| `04-scanner.md` | Scanner (scanned books) | owner's local machine | the owner has registered a scan in `local_sources` |

**Phase 0 freeze** (docs/plans/phase0/FREEZE.md): these agents build cited records only. No agent
generates learner pages, PDFs or handouts until Phase 4.

Use at most three agents at once, one per role. The scanner counts as a researcher.
Check the stages with:

```sh
python3 Shared/tools/library_board.py --subject Physics --fetch
```

## Filling in a prompt

Copy everything below the `---` line and replace:

- `{{AGENT_ID}}`: a stable id, unique per agent (for example `agent-author-1`). The board uses
  it to enforce independence, so never reuse an id across roles.
- `{{SUBJECT}}`: `Physics`.
- `{{CHAPTER}}`: the spine chapter id to work through (for example
  `PHY-11-MOTION-IN-A-PLANE`). Use `ALL` to follow the board's priority order.
- `{{BRANCH}}`: the shared work branch, normally `research/physics-library`.

Never give an agent a different role's prompt, and never let the verifier share an id with the
researcher or author of the nodes it verifies.

For the website (tablet shell and navigation), see `template/site-agents/01-tablet-shell-agent.md` and the spec `docs/specs/TABLET-SHELL-AND-NAVIGATION.md`.
