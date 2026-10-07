# Research prompt: improve Grade9V3.5 Core1A

Use this prompt with a research-capable agent.

---

I am redesigning **Core1A**, a Grade 9 learner-facing concept-construction page in the repository `reallaksh19/Grade9v3.5`.

The current page can become dense. It may simultaneously show:
- the inferential/key step;
- prerequisites;
- links to questions the concept builds toward;
- 2–4 construction steps;
- equation/validity reference;
- a fully worked example;
- a staged SVG;
- misconception/diagnose/repair;
- three quick checks;
- an independent exit task.

I want a **research-backed redesign**, not a cosmetic critique.

## Research questions

1. For Grade 8–10 mathematics/STEM learners, what does the evidence say about:
   - worked examples;
   - completion problems and guidance fading;
   - prediction/retrieval before revealing a worked step;
   - self-explanation prompts;
   - error/incorrect examples and misconception repair;
   - progressive disclosure;
   - signaling, coherence, split attention, and spatial contiguity in text + diagrams;
   - the expertise-reversal effect?

2. Which information should be visible immediately on a concept page, and which information is better collapsed/on demand?

3. What is the best sequence for one concept unit? Compare at least these candidate flows:
   - explain → worked example → practice;
   - worked example → completion problem → independent problem;
   - predict next step → reveal → self-check → transfer;
   - any stronger alternative supported by evidence.

4. How should the design differ for:
   - **REVISION**: learner knows the basics and needs a harder next-level question;
   - **COMPETITION**: learner should face a less-labelled, mixed-transfer challenge with little/no mid-task bridging?

5. What measurable browser/audit checks could detect regressions in this learning design, rather than only CSS/layout defects?

## Evidence standard

Prioritize:
- peer-reviewed systematic reviews/meta-analyses;
- major handbook chapters;
- controlled studies in mathematics/STEM;
- primary studies where they materially change the recommendation.

For each important claim:
- give the source, year, DOI or stable URL;
- say whether the evidence is strong, moderate, mixed, or mainly a UX heuristic;
- state the learner population and task type;
- identify boundary conditions (especially prior knowledge / expertise).

Do **not** treat a general UX heuristic as equivalent to a learning-outcome study.

## Repository-specific constraints

- Core1A is **concept construction**, not the main attempt-first question page.
- The key inferential step must remain visible.
- Staged diagrams must be cumulative unless explicitly authored as replacement.
- Secondary information may use native `<details>` progressive disclosure.
- Touch targets must be at least 48 CSS px.
- Tablet target is approximately 1366×854 and portrait tablet variants.
- The final design must remain keyboard accessible and printable.
- Do not invent IIT-JEE/IMO provenance. A competition item may be called a real past-paper item only with inspectable source authority; otherwise label it original competition-style material.

## Deliverable

Produce:
1. a one-page evidence synthesis;
2. a table mapping each evidence finding to a concrete Core1A UI/template decision;
3. a proposed Core1A unit wireframe in text;
4. an "always visible vs collapsed" content rule;
5. a REVISION vs COMPETITION rule;
6. 8–12 acceptance tests that could be automated in Chromium;
7. a list of current Core1A elements that should be removed, merged, collapsed, or rewritten;
8. citations and a short section on uncertainties / evidence gaps.

Be critical: if an existing block has weak learner value, recommend removing or demoting it rather than preserving it because it already exists.
