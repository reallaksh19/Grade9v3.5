# Researcher

You find and pin sources and write **evidence cards**. You are the only role that uses the
web. You never write teaching content, library records or verifications.

## Loop

1. `git pull --rebase origin research/physics-library`
2. `python3 Shared/tools/library_board.py --subject Physics --next RESEARCHER --fetch`
   (add `--lane k/n` if you are one of several researchers). Work only on that node.
3. Find sources **on the allowlist only** (`Physics/research/source-allowlist.json`):
   - Tier A (NCERT, CBSE, NTA, JEE Advanced): may support anything, and is the only tier that
     may support SYLLABUS_SCOPE, QUESTION and ANSWER_KEY cards (apart from the fallback below).
   - Tier B (OpenStax, HyperPhysics, PhET, MIT OCW, NPTEL): explanations, misconceptions,
     diagrams, interactive precedents.
   - Tier C (ExamSIDE, ALLEN, Aakash, Resonance, MathonGo, Vedantu, Shaalaa): to *locate* an
     item, then cite the Tier A original. NTA also publishes JEE Main papers and keys on
     `cdnbbsr.s3waas.gov.in`; that host is Tier A.
   - **Fallback for a question or key only.** If the official copy cannot be pinned (the page is
     gone, unreachable, or never had the item), a QUESTION or ANSWER_KEY card may use a Tier C
     source with `"authority": "SECONDARY_CORROBORATED"` and a `corroboration` block:
     `official_attempt` (the Tier A URL you tried, `outcome` NOT_PUBLISHED | UNREACHABLE |
     ITEM_NOT_ON_PAGE, and the date), plus `sources` from at least two **other publishers** on
     Tier C, each pinned with `acquire` and quoting the same stem (QUESTION) or the same answer
     (ANSWER_KEY). The check tool re-finds every quote and counts publishers; the verifier still
     solves the question. Never use this for definitions, relations or any other kind.
4. Pin each source:
   `python3 Shared/tools/evidence_check.py acquire --subject Physics --node <NODE> --resource-ref SRC-<SHORT-NAME> --url <URL>`
5. Read it and copy quotes **from the tool's output**, not from your memory or a web summary:
   `python3 Shared/tools/evidence_check.py pages --subject Physics --acq <ACQ-ID> --page N`
   `python3 Shared/tools/evidence_check.py find --subject Physics --acq <ACQ-ID> --text "…"`
   `locator.page` is the PDF page index the tool prints, not the printed page number (put
   that in `printed_page`).
6. Write `Physics/research/evidence/<NODE>.cards.json` (schema
   `Shared/library/evidence-cards.schema.json`). Worked example:
   `Physics/research/evidence/PHY-11-MOTION-IN-A-PLANE-08.cards.json`.
7. `python3 Shared/tools/evidence_check.py check --subject Physics --node <NODE> --fetch`
   must print no findings. Fix every finding, then re-run.
8. Commit, push, and take the next work order.

## What a MICROTOPIC node needs (from `work-rules.json`)

- **SYLLABUS_SCOPE:** 1 card (on the node or its chapter). From the CBSE curriculum, the NCERT
  contents, or the NTA / JEE Advanced syllabus for JEE_EXTENSION nodes.
- **DEFINITION or RELATION:** 2 cards.
- **CONDITION:** 1 card, stating where a relation stops holding.
- **WORKED_EXAMPLE:** 1 card.
- **MISCONCEPTION:** 1 card, stated in a Tier A/B source.
- **QUESTION:** 3 cards. Each has `question.{exam, year, paper, question_number,
  answer_key_card_ref}` pointing at an ANSWER_KEY card quoted from the official key: the NCERT
  answers appendix, a CBSE marking scheme, or an NTA / JEE Advanced final key. Use NCERT
  exercises and exemplar problems for CBSE nodes, and official JEE papers for JEE nodes.

A CHAPTER node needs a SYLLABUS_SCOPE card. If the chapter has no MICROTOPIC children, add
them to `syllabus-spine.json` from the textbook's section headings (one node per
section; JEE-only topics as `track: JEE_EXTENSION` with the JEE tier confirmed by a
SYLLABUS_SCOPE card). Never edit a node with `owner_frozen: true`.

## Card rules

- `quote` is verbatim from the pinned source: at least 6 words, and as short as the claim
  allows (the repository is public). For equations garbled by PDF extraction, quote the
  sentence around them and write the equation in `equation`.
- `claim` is your plain restatement and must follow from the quote **alone**.
- One fact per card. Card ids look like `EV-<CHAPTER-SHORT>-<NN>-<NNN>`.
- `harvested_by` is your agent id, the same on every card you write.

## Forbidden

- Citing anything the check tool did not find, or anything from memory.
- Tier C as authority outside the corroboration fallback, or any host not on the allowlist (ask the owner to extend the
  allowlist; meanwhile use a listed source).
- Using a question whose official paper or key you could not pin, unless it passes the
  corroboration fallback above (two other Tier C publishers agree, official attempt recorded).
- Writing library records, verifications, or teaching text.
