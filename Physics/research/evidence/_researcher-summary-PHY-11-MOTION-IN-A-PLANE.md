# Researcher summary — pilot chapter PHY-11-MOTION-IN-A-PLANE

Researcher: `agent-researcher-1` · 2026-09-26 · branch `research/physics-library`

`evidence_check.py check --subject Physics --fetch`: **210/210 cards verified in 15 files**.
All 15 pilot nodes have left the RESEARCHER stage. The chapter node shows VERIFIED because a
CHAPTER node needs only a scope card. The 14 microtopics are at AUTHOR.

## Sources pinned (all allowlisted)

| Tier | Source | Used for |
|---|---|---|
| A | NCERT keph103 (Motion in a Plane, reprint 2026-27) | concepts, worked examples, Points to Ponder, exercises 3.1–3.21 |
| A | NCERT keph1an (Part I answers) | answer keys for exercises in chapters 3 and 5 |
| A | NCERT Exemplar keep304 (ch. 4 Motion in a Plane) + keep316 (answers) | questions and answers; hints for X2/X3 |
| A | NCERT keph105 (Work, Energy and Power), keph202 (Fluids) | collisions (X3), resistive force / Stokes' law (X4), pendulum (X5) |
| A | CBSE Physics curriculum 2026-27 (cbseacademic.nic.in) | chapter SYLLABUS_SCOPE |
| A | JEE (Advanced) 2026 Information Brochure (jeeadv.ac.in) | JEE syllabus scope for X1–X5 |
| A | JEE (Advanced) 2014 P1, 2014 P2, 2017 P1 ("Questions with Answers" archive PDFs); 2026 P1 final solutions | JEE questions and official answers |
| B | OpenStax University Physics Vol. 1, sections 2.1, 2.2, 4.3, 4.4, 4.5, 6.4 | misconceptions, conditions, worked examples where NCERT has none |

The three original worked-example cards on node 08 are unchanged. The 17 cards added there are mine.

## JEE scope findings (recorded in each node's SYLLABUS_SCOPE card and commit message)

| Node | Finding |
|---|---|
| X1 Relative velocity | **In the syllabus**: JEE Advanced 2026 lists "Relative velocity". |
| X2 Projectile on an incline | **Not named**. Covered only by the general "projectiles" entry. |
| X3 Rebound with energy loss | **Not named**. The syllabus lists "Elastic and inelastic collisions" and "projectiles" separately. |
| X4 Projectile with linear drag | **Not in the syllabus**. Only Stokes' law and terminal velocity (fluids) are listed. |
| X5 Non-uniform circular motion | **Not named**. The syllabus lists only "Uniform circular motion". |

The spine's draft `jee_tier` values (MAIN for X1/X5, ADVANCED for X2–X4) are unconfirmed.
I did not change the spine; the owner should decide how to handle these extensions.

## Sources that could not be reached or used

1. **JEE Main syllabus, papers and keys.** NTA links them only from
   `cdnbbsr.s3waas.gov.in`, the government CDN behind jeemain.nta.nic.in. That host is not on
   the allowlist, so no JEE Main source is cited anywhere. nta.ac.in does not host them.
   *Owner action:* add `cdnbbsr.s3waas.gov.in` (NTA uploads) to Tier A if JEE Main is wanted.
   Note that NTA final keys list question IDs only, not question text.
2. **JEE Advanced keys after 2017.** jeeadv.ac.in archives papers from 2007–2025 but no
   answer keys. The 2007–2013, 2015, 2016 and 2019 PDFs are image-only, so the checker cannot
   find quotes in them. Only 2014, 2017 (papers with answers) and 2026 (final solutions) were
   usable. As a result, X2–X5 draw most of their questions from NCERT Exemplar and NCERT
   exercises, which are Tier A official questions with official answers. None of these is a
   JEE question on the exact extension topic.
3. **NCERT Exemplar 4.10** was avoided: its official key (b) conflicts with a direct solution.
4. **Garbled PDF text.** Some NCERT and Exemplar answers lose radicals, hats or degree signs
   (e.g. 3.19, 4.31, 4.32, 4.33, 4.34). Those cards give the intended expression in `equation`
   and say so in the claim. For 4.32 the printed answer must be read on the page image.
5. **OpenStax licence.** The OpenStax pages carry a notice restricting use in LLM training
   or ingestion. The owner may want to review whether Tier B OpenStax suits this pipeline.

## Verifier-findings run (agent-researcher-1, 2026-09-26)

Fixed every card-level finding on 02, 03, 04, 05, 06 (chapter card EV-PHY-11-MIP-00-001), 07,
X1, X2, X3, X4 and X5. Quotes now carry whole questions and options. Where a question crosses a
page break, a continuation QUESTION card was added: 03-017, 04-015 and 07-015. Claims were
trimmed to what their quotes say, and the JEE Main sentence was removed from X1–X5 SYLLABUS_SCOPE.

- **Exemplar 4.32 removed from X2 and X3.** The printed key on keep316 p.123 is
  "A v0^2 sin θ / g", with the letter A standing where the coefficient belongs. The only other
  allowlisted official edition, the Hindi exemplar (khep316 p.124), prints the same "A", so no
  source pins the coefficient. As a result the author records that cite X2-010/011 and
  X3-010/011 must be withdrawn.
- **X3 now has lossy-rebound evidence.** It adds NCERT Exemplar 5.24 (an object rebounds with
  half its speed; newly pinned keep305) with its key "(a) 12.5 N s (b) 18.75 kg m s–1". It also
  adds MIT OCW 8.01SC Ch.15 (Tier B, newly pinned): the definition of the coefficient of
  restitution, and e < 1 ⇒ kinetic energy decreases.
- **Still open, with no allowlisted source found:**
  - X2 is one QUESTION short: there is no incline-projectile question with an official key.
  - X5 has no QUESTION + ANSWER_KEY pair asking for a_T, a_c or the total acceleration with
    changing speed.
  - Searched: NCERT XI textbook ch.2–6 and answers; Exemplar ch.3–7 and answers; jeeadv.ac.in
    2014, 2017 and 2026 papers with answers. The 2018–2025 papers have no keys, and JEE Main is
    reachable only via cdnbbsr.s3waas.gov.in.
  - Two JEE Advanced items would qualify for X3 if their official keys were reachable:
    2023 P1 Q1 (restitution 1/√3) and 2018 P2 Q8 (the ball loses half its KE on the bounce).
