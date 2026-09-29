# Design note — phy-nlm-momentum-transfer

1. **The idea.** Convert a signed momentum change for one fixed-mass ejectum into an average momentum-transfer rate for a repeated stream, while keeping force roles attached to the bodies they act on. The learner should be able to distinguish force on the ejecta, equal-and-opposite launcher recoil, and the external holding force needed for a stationary launcher.

2. **Wrong routes.** Existing canonical package misconceptions already identify the main failure modes:
   - use final momentum instead of `Delta p = m(v_out - v_in)` when `v_in != 0`;
   - put ejecta force and launcher recoil in the same direction;
   - import rocket/continuously-variable-mass methods into a bounded discrete stream;
   - interpret `R Delta p_item` as instantaneous force rather than stream-average force.

3. **Representations.** The current canonical microtopic has no `representation_refs`. Do not invent a page-local force diagram or interactive resource for the pilot. A useful future representation would make body ownership and signed directions explicit before equations are revealed; it must be added through the canonical representation/resource model if implemented.

4. **Task arc and difficulty-first triage.**

   Denominator: one canonical microtopic, `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE`. The external ExamSIDE resource is a demand witness/locator, not a source-custodied Core2 question; current manifest `selection.core2` is empty. First-stage route: **Core1**.

   | Concept/question ref | Topic/subtopic | Canonical concept | Concept difficulty | Question D1–D4 + components when applicable | Why teaching/solving is difficult | Prerequisite | Wrong route | Teaching crux | Interaction value + purpose | Target Core | Source/uncertainty | Lot |
   |---|---|---|---|---|---|---|---|---|---|---|---|---|
   | `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE` | Force and Laws of Motion / momentum-transfer force rate | Force from a steady stream of discrete momentum changes | HARD | NOT_APPLICABLE — concept row | Several individually familiar ideas must be coordinated: signed `Delta p` for one item, items-per-second rate, body ownership of action/reaction, and a separate holding force. The arithmetic is short; model/system selection and sign discipline carry the difficulty. | `CAP-NLM-FBD-BODY-OWNERSHIP`, `CAP-NLM-SECOND-LAW`, `CAP-NLM-THIRD-LAW` | final momentum only; same-direction recoil; rocket-model import; average=instantaneous | Keep one declared frame/positive direction and label the body for every force before multiplying rate by per-item momentum change. | HIGH candidate — a body/direction switcher could let the learner choose ejecta vs launcher vs support and see which signed force belongs to each body; **not admitted to implementation in this slice because no canonical representation/resource exists yet** | Core1 orientation first; later Core1A/Core1B construction/reconstruction | Canonical package is CANDIDATE; no source inventory/readback denominator beyond this one scoped microtopic; external demand text is not copied/custodied here | LP-H1 |

   Required distinctions for this pilot:

   ```text
   HARD concept badge
   ≠ question difficulty score
   ≠ interaction admission
   ≠ learner mastery
   ```

   Interactive admission result: **one candidate identified, zero new interactive resources implemented**. The concept has high potential interaction value because body ownership/sign changes are relational and decision-based, but #352 does not authorize inventing a resource outside the canonical representation system. Static canonical Core1 projection is therefore the correct pilot implementation unless a later evidence-backed representation change is approved in the owning model.

   Core-by-Core task arc:

   | Core | Item | Decision practiced | New versus earlier | Canonical records / source basis | Actual or planned prior exposure | Open dependency and useful next work |
   |---|---|---|---|---|---|---|
   | Core1 | `MIC-PHY-NLM-MOMENTUM-TRANSFER-RATE` | Orient to the body/direction/rate distinctions and bounded model | First-stage orientation | canonical microtopic + relations in `phy-nlm-momentum-transfer.v1.json` | actual once exact Core1 render is delivered; currently planned | Build/inspect exact Core1 HTML/PDF; verify safe metadata and complete one-concept coverage view |
   | Core1A | same canonical microtopic | Follow why `R Delta p_item` is an average force and why reaction/holding forces differ | Complete construction rather than compact orientation | same canonical microtopic teaching path | planned | Later requested Core scope; do not claim delivered exposure yet |
   | Core1B | same canonical microtopic | Choose frame/body/sign before reconstruction and repair | Elicits decision before explanation | same canonical microtopic elicitation | planned | Later requested Core scope |
   | Core2 | none selected | Authentic source-question attempt | NOT_APPLICABLE in current first-stage route | current manifest `core2=[]`; external demand is not canonical question custody | none | Requires a real source-custodied bank question if later added |
   | Core2A | existing authored package questions | Familiar supported application | Applies the taught capability | package questions exposed to CORE2A | **planned, not actual learner exposure in this pilot** | Do not use as Core2B prior exposure until delivered |
   | Core2B | existing authored package questions | Changed demand / transfer | Must protect changed decision | package questions exposed to CORE2B | **planned**; lineage cannot be claimed from mere record existence | Verify actual delivered Core2A lineage before any transfer claim |

5. **Transfer plan.** The invariant is signed momentum transfer in one declared frame with explicit body ownership. A genuine changed demand must alter model choice, representation, context or required decision, not merely numbers or hint count. Existing Core2B records remain authored candidates; this pilot does not certify their transfer lineage.

6. **Clinic/Explorer admission.** No separate Clinic/Explorer surface is introduced. The one interaction candidate is retained as design rationale only until a canonical representation/resource need is proven.

7. **Research log.**
   - `Physics/library/phy-nlm-momentum-transfer.v1.json`: canonical package truth for scope, HARD badge/reason, capability, teaching path, misconceptions and authored later-Core questions.
   - `products/physics/phy-nlm-momentum-transfer.manifest.json`: current learner-product selection; establishes one microtopic and no Core2 source questions.
   - #352 method revision: scheduling/triage guidance only; does not alter academic truth.

8. **Known weaknesses.**
   - No canonical representation is bound to the microtopic, so the strongest interaction idea remains unimplemented.
   - The external demand witness is not a source-custodied canonical Core2 item; Core2 route would be dishonest without new source work.
   - Package status is CANDIDATE and the unit has no source inventory/readback record; pilot evidence must not be described as publication readiness.
   - Exact HTML/PDF/browser/search/Atlas evidence is still pending after this design slice.
