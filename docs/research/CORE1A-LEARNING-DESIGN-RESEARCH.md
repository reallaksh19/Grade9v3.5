# Core1A learning-design research note

## Question

How should Core1A teach a concept on a tablet so that the learner sees the crux, understands one worked route, actively predicts/retrieves, and then applies the idea with less support—without turning the page into a wall of explanation?

## Findings used in this redesign

1. **Worked examples are valuable early, but guidance should fade.** Cognitive-load research consistently finds a worked-example advantage for learners who have not yet formed a schema, while additional worked guidance can become redundant as prior knowledge increases. The practical implication for Core1A is: show one high-quality worked route, then shift quickly to prediction and independent problem solving rather than stacking more explanation.
   - Sweller, van Merriënboer & Paas, *Cognitive Architecture and Instructional Design: 20 Years Later* (Educational Psychology Review, 2019): https://link.springer.com/article/10.1007/s10648-019-09465-5
   - Ruitenburg et al., *After initial acquisition, problem-solving leads to better long-term performance than example study* (Learning and Instruction, 2024/2025 online record): https://www.sciencedirect.com/science/article/pii/S0959475224001543

2. **Prediction/retrieval before revealing a worked step can improve later performance.** A 2025 Learning and Instruction study found better delayed recall and problem solving when learners attempted to retrieve/execute each next step before it was revealed. Core1A therefore uses a "predict step N, then reveal" interaction inside the worked example rather than showing every solution step immediately.
   - *Retrieval Practice in Stepwise Worked Examples Improves Learning* (Learning and Instruction, 2025): https://www.sciencedirect.com/science/article/pii/S0959475225001203

3. **More explanation is not automatically better.** Research on expertise reversal, guidance fading, and instructional explanations shows that redundant guidance can impose unnecessary load. Core1A should keep reference material available but secondary.
   - Sweller et al. 2019 above.
   - *How much is too much? Learning and motivation effects of adding instructional explanations to worked examples* (Learning and Instruction, 2013): https://www.sciencedirect.com/science/article/pii/S0959475212001016

4. **Signal the essential structure and remove competing material.** Multimedia-learning evidence supports coherence and signaling: exclude or defer nonessential material and cue the organization of what matters. Spatial contiguity also favors keeping explanatory words close to the visual they explain.
   - Mayer & Fiorella, *Principles for Reducing Extraneous Processing in Multimedia Learning* (Cambridge Handbook of Multimedia Learning): https://www.cambridge.org/core/books/abs/cambridge-handbook-of-multimedia-learning/principles-for-reducing-extraneous-processing-in-multimedia-learning-coherence-signaling-redundancy-spatial-contiguity-and-temporal-contiguity-principles/CD5B7AE1279A9AB81F8EEBB53DBEC86E
   - van Gog, *The Signaling (or Cueing) Principle in Multimedia Learning* (Cambridge Handbook, 2021): https://www.cambridge.org/core/books/cambridge-handbook-of-multimedia-learning/signaling-or-cueing-principle-in-multimedia-learning/3972D4ACC628D5B53F7B2B4785DB2B06

5. **Progressive disclosure is appropriate for useful secondary information.** It reduces the amount users must scan initially while keeping advanced/reference information available on demand. In a learning page this is a UX principle, not a substitute for pedagogy: the crux and the task must stay visible.
   - Nielsen Norman Group, *Progressive Disclosure*: https://www.nngroup.com/articles/progressive-disclosure/

6. **Error examples can be useful, but only when the learner has a diagnostic job.** A recent systematic review reports benefits from asking learners to identify, explain, correct, or reflect on errors, with overload as an important boundary condition. Therefore the Core1A mistake clinic remains available, but is not an always-open block competing with the main construction.
   - *Conditions for Effective Learning from Erroneous Examples: A Systematic Review* (Educational Psychology Review, 2025): https://link.springer.com/article/10.1007/s10648-025-10071-x

## Resulting Core1A information architecture

### Always visible — the learning path

1. **The key step** — one concise inferential crux.
2. **Build it** — 2–4 authored construction steps, with the crux step visibly signaled.
3. **See it** — the staged representation, with cumulative reveal and the explanatory label next to the relevant geometry.
4. **Watch one** — one authentic worked example, but each solution step is closed until the learner predicts the next move.
5. **Quick check** — brief CHECK / APPLY / CONNECT retrieval prompts.
6. **Now you do one** — an independent application with less support.

### Collapsed by default — useful reference/support

- prerequisites / model contract;
- why this section matters for the selected question set;
- formula meaning + validity table;
- mistake / diagnose / repair clinic;
- Core2 guided hint ladder.

This split is deliberate. "Collapsed" means secondary, not unimportant.

## Audit implications

A Core1A acceptance audit should fail when:
- the inferential crux is hidden inside a disclosure;
- the worked example exposes all solution steps before any prediction opportunity;
- a later SVG stage removes required earlier geometry;
- formula/reference material visually dominates the construction;
- the page contains no less-supported independent application;
- a collapsed control is not keyboard-operable or does not expose a clear label.

It should not fail merely because secondary material is closed on initial load.
