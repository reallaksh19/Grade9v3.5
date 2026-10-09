# #327 — Core1A concept reconstruction versus Core2A question hints

Status: **AUTHORING CANDIDATE ONLY**, NOT an admitted QRT/runtime behaviour or learner release. Stacked on draft PR #312. Do not place SOF original questions or answers here.

## Pedagogical difference (testable, not a label)

| | Core1A concept reconstruction | Core2A optional scaffold / future authentic Core2 if rights-cleared |
|---|---|---|
| First screen | Explain the principle using neutral powers, independent of the learner's attempted item | Show the specific unseen question and learner input; no worked construction |
| Progress | General law → concept discrimination → guided new-base representation → worked example → unassisted exit | Learner tries → small question-local nudge → learner still chooses and completes moves |
| Feedback | Distinguish wrong model **by reason**, e.g. offset is a factor because `b^(r+1)=b*b^r` | A limited clue answers “what to attend to next,” not “what is the full t/answer?” |
| Credit | Explain general rule without relying on memorized `x=2`, then do a fresh example | Record hint-used attempt as assisted, not independent mastery |
| Return | Use concept explanation then require learner to apply it to a genuinely new attempt | Optional support is confined to attempted question; reveal answer only following an attempt and do not promote that as independently solved |
| Authority | Wholly authored teaching candidate | Current Core2A is wholly authored; authentic SOF Core2 remains rights/custody held |

### Exact learner script — Core1A content sequence

1. **Concept, no target question:** If `P=2^3=8`, is `2^4` equal to `2P` or `P+2`? Compare 16 against 10. Explain why adding one to the exponent multiplies by the base.
2. **Concept discrimination, no worked problem:** If `Q=5^n`, is `5^(n+1)=5Q` or `Q+5`? The learner must choose and justify `5^(n+1)=5*5^n`, not memorize `x=2`.
3. **Guided different-number application:** Only now present independently authored `3^(2x+1)=9^x+162`, name `t=9^x=3^(2x)>0` and explain `3^(2x+1)=3t`. Continue with the five unchanged mathematically justified steps, including exact reverse-check.
4. **Graduated aid when genuinely stuck:** Diagnose (factor confusion, nonpositive t, bad inversion). Explain the specific general law *before* showing its application to the target line; avoid a one-click answer dump.
5. **Unassisted exit:** `2^(2y+1)=4^y+64`, requiring fresh identification, factor relation, inverse and verification; model answer is only revealed after an attempt in the existing TEST renderer.

**Updated implementation honesty:** An opt-in `grade9v3:concept_checkpoint` now causes the TEST Core1A renderer to show a neutral-law demonstration and ask for a factor-law choice **plus a minimal explanatory rationale** before revealing the guided worked anchor and stages. This is a browser-only, keyword/choice **formative format gate**. It is not proof that the learner understands the concept, nor a signed assessment/mastery receipt. The `compact_anchor` remains authoring content, not an authority claim.

### Question-scoped Core2A hints (authored task `4^(2u+1)=16^u+192`)

- **Optional H1 — Notice:** “Look at 16 and 4: which is a power of the other?” No chosen variable, substituted equation or numeric solution.
- **Optional H2 — Recall relevant law:** “An exponent increased by one multiplies the existing power by its base. Where is the one-step exponent offset in your equation?” This is help for the particular question, not a replacement five-stage lesson.
- **Optional H3 — Connect your own model:** “Choose a strictly positive common power, express both sides through it, then solve and reverse-check.” No disclosed `4t=t+192`, `t=64` or `u=3/2`.
- **Post-attempt solution and link:** The TEST renderer gates the full solution behind a typed commitment and links to `TC-02`. Core2A H1 is now **hidden until explicitly requested**, and H1/H2/H3 usage marks the article assisted with best-effort local-state persistence. It **does not** authenticate the typed math attempt, provide server-signed hint-use evidence or independent mastery credit, prove semantic understanding from its concept-format check, or enforce a genuinely fresh return attempt. These are still evidence/UX debts.

### Next acceptance requirements — separate work, not claimed complete

- Improve the implemented TEST concept-first input beyond a radio choice + keyword-matched reason: validate reasoning semantically and distinguish misconception versus execution slip without false mastery claims.
- Preserve the implemented local Core2A hint-used flag as **assisted**, then implement a signed/verified attempt-and-disclosure chronology before it can inform any independent proficiency decision.
- When a learner returns from Core2A to Core1A, preserve the original failed attempt, route to the *general law* ahead of target numbers, check the law in a neutral example, and return to a **fresh** independently authored same-family item.
- A completed repair must not automatically mark the previously missed item correct. Reassess with a new unseen problem before any independent mastery claim.
- Tested keyboard, screen-reader, 200%-zoom and print behaviour; source rights and academic/QRT/Owner signoff remain independent gates.
- Never recast a model-authored practice item as an original SOF Core2. Original Q26/Q35 source custody, publisher reproduction rights and verified full question/key remain held by #294.

### Exact current bounds

Authoring-only changes are scoped to the existing #312 package and a separate semantic regression suite. Existing `repair_ref=TC-02`, manifest `output_roles=[CORE1A, CORE2A]`, zero authentic Core2, five teaching steps and source-authored provenance remain unchanged. Do not edit central render, assessment credit, academic authority, V3.1 relay, source custody or generated Mathematics hub in this proposal.
