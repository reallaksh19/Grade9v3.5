# Difficulty × Demand objective review

This is the semantic layer between canonical question analysis and Blueprint 1.9.

- `bands.v1.json` keeps the existing D1–D4 difficulty meaning and band-specific support posture.
- `demands/*.v1.json` define the seven cross-subject cognitive jobs and their X/Y/Z/W, H1–H3, figure, misconception, solution and extraction objectives.
- `question-demand-matrix.v1.json` materializes exactly 28 band × demand cells.
- `validation-strategies.v1.json` holds reusable checks without creating extra cells.
- `Shared/tools/objective_review.py packet --band D3 --demand MOD` resolves an agent-ready policy.

Blueprint 1.9 still decides page components, slots, reveal behavior and structural reference depth. The matrix decides what those components must accomplish pedagogically.

Difficulty and demand are independent axes: difficulty describes complexity/transfer sensitivity; demand identifies the decisive cognitive job. A question selects one primary demand and may later declare secondary demands without creating hybrid templates.

`W` is always learner-owned. Later QuestionPedagogyRecord integration may bind W to a protected reasoning move so direct leakage from hints, safe figures or pre-attempt panels can be detected structurally. This structural check will not replace the qualitative H/S/P/M review.

Core2 may provide demand evidence for Core1A emphasis and lineage; it does not become academic authority for Core1A.
