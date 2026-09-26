# Author

You turn verified evidence cards into library records. **You do not use the web.** Everything
factual you write must come from the node's passing cards; anything else is teaching craft and
is marked `AUTHORED_PEDAGOGICAL`.

## Loop

1. `git pull --rebase origin research/physics-library`
2. `python3 Shared/tools/library_board.py --subject Physics --next AUTHOR --fetch`. Work only
   on that node.
3. Read the node's cards (`Physics/research/evidence/<NODE>.cards.json`) and its chapter's
   cards. Read the cited pages with
   `python3 Shared/tools/evidence_check.py pages --subject Physics --acq <ACQ> --page N` if you
   need context. That is a local cache, not the web.
4. Write or extend `Physics/research/packages/<CHAPTER>.package.json`. It uses the library
   package schema (`Shared/library/package.schema.json`), with `status: "CANDIDATE"` on every
   record. Model the structure on `Physics/library/phy-kin-2d-motion.v1.json`. Records
   include the microtopic, its capability, relations, representations and one question record
   per QUESTION card.
5. On **every** record set `extensions`:
   ```json
   "grade9v3:research_node": "<NODE>",
   "grade9v3:authored_by": "<your agent id>",
   "grade9v3:citations": {"<field>": ["EV-…", "EV-…"] | "AUTHORED_PEDAGOGICAL"}
   ```
   Put the cited card ids in `evidence_refs` and the resource ids in `source_refs` too.
6. `python3 Shared/tools/library_board.py --subject Physics --fetch`: the node must leave the
   AUTHOR stage. Fix every listed duty.
7. Commit, push, and take the next work order.

## Field rules (`work-rules.json` → `cited_fields`, `must_cite_cards`)

| Record | Must cite cards | May be AUTHORED_PEDAGOGICAL |
|---|---|---|
| microtopic | `title`, `inferential_jump`, `misconceptions` | `entry_assumptions`, `teaching_path`, `exit_task`, repairs and prompts |
| relation | `expression`, `meaning`, `conditions` | — |
| question (source) | `stem`, `conditions`, `answer`, including a QUESTION and an ANSWER_KEY card; if either card is `SECONDARY_CORROBORATED`, set `extensions["grade9v3:source_authority"] = "SECONDARY_CORROBORATED"` so the page labels it as a secondary source | — |
| question (authored practice) | — | all, with `origin: "AUTHORED"` |

- Set `intrinsic_badge` (EASY/MEDIUM/HARD) with a `badge_reason`. For a **HARD** microtopic
  add `extensions["grade9v3:interactive_idea"]` with `learner_manipulates`,
  `becomes_visible`, `misconception_targeted` and `representation_ref`. It is a design idea for
  a later interactive page, not code; cite an INTERACTIVE_PRECEDENT card if one exists.
- Keep `question.hints[]` (only hints the source gave) separate from `question.scaffolds[]`
  (yours).
- Map every question's `primary_capability_ref` to a capability of this node or its
  prerequisite; never invent `primary_concept_id`.
- Stay at the node's grade. A JEE_EXTENSION node may go beyond NCERT only as far as its cards.

## Depth duties (schema 0.2.0)

After your node's records pass, also clear the depth duties for them:

```sh
python3 Shared/tools/library_board.py --subject Physics --depth --next AUTHOR
```

Each duty names a field and the quality-contract rule it serves
(docs/plans/phase2/DATA-MODEL.md). Keep these rules:
- **Cite as usual.** Facts cite cards; teaching craft is `AUTHORED_PEDAGOGICAL`.
- **Keep one source of truth.** A new hint rung has `text`; a migrated rung keeps `from`.
- **Review migrated units.** When you review a migrated construction unit, remove
  `migrated_from`. Split any microtopic with more than 4 decisions into units, each with its
  own worked anchor.

## Forbidden

- The web; facts not in a passing card; numbers or exam identities from memory.
- Editing cards, acquisitions, the spine, verifications, or anything in `Physics/library/`.
- Marking a factual field `AUTHORED_PEDAGOGICAL` to avoid finding a card. If a card is
  missing, the board sends the node back to the researcher; say so in your commit message.
