# House rules for a learner unit

1. Learner pages come from `Shared/tools/render_core.py` and its registered blueprints. Change the renderer for a new behavior; a hand-edited generated page is never the source.
2. A definition, value, relation or condition needs its evidence card. An original question and printed key cite their inventory item and cards. Keep the printed key verbatim; solve independently and explain any difference.
3. Put protected results in answer fields, later hint rungs, `attempt.produces`, model responses, boundary-test answers, failure signals and repairs. Stems, captions, figure labels and first stages pose the situation without settling the learner's decision. In HTML the renderer keeps protected bytes inert until commitment; a learner PDF omits those bytes; a key PDF includes them.
4. One author owns a unit's package, figures, design and revision. Source reader A registers/inventories and transcribes; a different session B cross-reads. A separate reviewer attempts the exact render as a learner.
5. Push after each phase. Record the current render digest, decisions, weaknesses, next step and spend in the unit worklog.
6. Declare weak or unresolved work. Descriptive reports help judgment; a passing linter never certifies academic depth. Open findings do not prevent delivering the best available work.
7. Research widely for pedagogy and log what shaped the design. Cite narrowly and exactly for factual claims. The repo's templates and goldens do not replace fresh reasoning.
8. Run the full local code suite before pushing a code change. Treat Chromium as NOT_RUN if unavailable. Content authors may use the advisory self-check without waiting on it.
9. Finish each phase with the nine brief step-back questions in the protocol. Fix wrong-way behavior in the phase or state why it remains open; the reflection is not a gate.
10. Use the [six-Core dependency guidance](FIRST-STAGE-REVIEW.md) to explain learning relationships and show the first-stage product early. Research, derivation and drafting remain open across Cores. The schema records understood ideas; if it cannot express one, retain the reasoning and propose a shared improvement. Missing metadata, feedback or an upstream artifact is not a new execution blocker. Add no CI or completion quota for this guidance.

**Attempt semantics.** The controls ask an honest self-learner to commit to an answer or to work on paper before seeing a protected solution. They do not mark correctness or prevent a determined learner from reading HTML source. Search, live DOM and accessibility text must not expose protected results before commitment. The Owner alone publishes by accepting the exact render digest.
