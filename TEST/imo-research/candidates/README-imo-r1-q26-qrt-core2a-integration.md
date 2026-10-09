# IMO-R1 — one authored MODEL-D3 Core2A → existing Q26-like Core1A

**Authorized only by [issue #294, comment 6073301373](https://github.com/reallaksh19/Grade9v3.5/issues/294#issuecomment-6073301373), with the updated technical reference [comment 6073747124](https://github.com/reallaksh19/Grade9v3.5/issues/294#issuecomment-6073747124).** Research/TEST only. Stop after one draft PR and issue handoff; no extra batches or publisher source Core2.

## Reuse/provenance and dependency clarity

Base main `bc1af3e7ba438bd2404c54967dd46c652acad325` is the Core-foundation merge from [PR #310](https://github.com/reallaksh19/Grade9v3.5/pull/310). The existing authored Q26-like Core1A package originally exists on *separate, unmerged* [draft #308](https://github.com/reallaksh19/Grade9v3.5/pull/308) at `d0382084906206eafa8a186d1a1a3c7e8dff5b65`, package Git blob `e309f80defc905e236aa525d7945f0f74a9b5d32`. This R1 branch explicitly **copies its original authored Core1A construction and stage-SVG, with only a print-scoped CSS parity fix to show all three mathematical teaching stages on paper** to permit one self-contained test against merged main; it adds only the one practice question and family's `item_refs` and does **not edit #308 or present it as merged**. Maintain review/co-merge awareness of the duplicate candidate path; both PRs are drafts.

No original SOF stems, options, figures or key are stored in the learner output. [Original math-audit B02-010](../verification/fullpaper-source-math-batch02.v1.json) motivates the family *provisionally* through a shared-power multiplicative-factor crux; it does not grant authentic-source CORE2 product authority. The 68 authentic-source positions and seven already catalogued original practice candidates remain completely separate. This new authored supported-practice item is not represented as an eighth authentic source.

## One independently authored supported task

Real-exponent task **`4^(2u+1)=16^u+192`**, all bases positive and not one. The learner must select `t=4^(2u)=16^u>0`, recognize the *factor* `4^(2u+1)=4t` rather than `t+4`, derive `4t=t+192`, solve `t=64`, recover **`u=3/2`** and reverse-check the untransformed equation: **`4^4=256=16^(3/2)+192=64+192`**. Every one of the five reasoning moves names its separate why-valid mathematical law; the item has a stable `MOVE-IMO-R1-FACTOR` crux, realistic wrong route, 3 optional learner-requested supports and an exact `TC-02` repair link into the already-authored Core1A teaching construction. Same-family **CORE2A** supported practice, not Core2B transfer. There is **no preattempt answer SVG or visual**; the stem and conditions are the safe initial representation.

## QRT classification and integrity

Primary **MODEL** because the protected step chooses the shared positive exponential model; secondary REPRESENT/APPLY because the solver rewrites bases and computes/inverts the result. Five authoritative authored 0–2 evidence scores are **2+1+2+1+1=7**, thus the existing shared difficulty resolver derives **D3** and the existing shared QRT selects **`QRT-MODEL-D3`**. The rationale for each component is stored in the question record; no new score rule, matrix vocabulary, 28-cell projection, or fake per-capability learner mastery is introduced. Test profile knowledge percentages are explicitly synthetic and are checked not to alter QRT slot/cell resolution. Tests exercise existing X/Y/Z/W outputs and all H1–M3 twelve semantic review jobs; those are **jobs, not twelve visible hint quotas**.

The TEST manifest selects exactly `output_roles=["CORE1A","CORE2A"]`, `microtopics=["MIC-TEST-IMO-G9-COMMON-BASE-RELATION"]`, `core2a=["Q-TEST-IMO-G9-COMMON-BASE-SUPPORTED-01"]`, `core2=[]`, `core2b=[]`, empty source bank. Tests must reject a forged package question selected as authentic Core2, false D band and fabricated crux move. Authored Core1A is a **learner teaching repair**; no canonical Owner admission of the concept or QRT cell is inferred.

## Rendering and acceptance matrix

The workflow uses the **existing** `Shared/tools/deploy_test.py product`, sole `render_core.py` engine, TEST banner and print pipeline; it writes real generated HTML and both role PDFs to an ephemeral TEST output and uploads receipts/screenshots. It does **not** commit handcrafted derived HTML/PDF or publish a learner site. Its browser assertions cover four standard widths and 200%-text zoom; content visibility, typed synthetic commitment, Enter-triggered disclosure, no precommit solution materialization, same-concept clickable `TC-02` repair. Raw HTML is not cryptographic exam security.

| Review dimension | Initial disposition |
|---|---|
| Package/schema, subject authority, wrong-Core2 refusal | PENDING exact-head CI |
| Shared QRT check and write --check, 28-cell test suite | PENDING exact-head CI |
| Correct mathematical result, model, five why-valid steps | CHECKED_BY_AUTHOR, PENDING CI |
| Canonical technology HTML/manifest role projection, depth | PENDING exact-head CI |
| Browser 320/390/768/1280, 200%-text, keyboard/attempt/repair | PENDING actual Chromium |
| Printed real CORE1A and CORE2A PDFs + hashes/receipts + visual completeness | PENDING exact-head evidence; **all three stage headings asserted in PDF text; physical visual inspection separately required** |
| Manually operated screen-reader and student comprehension | NOT_RUN |
| Independent academic acceptance, product Owner admission, rights | NOT_GRANTED |
| Authentic SOF original Core2, source custody, QRT owner acceptance | ZERO / HOLD |
| Merge/publication/next academic batch | DEFERRED / NOT_AUTHORIZED |

**End of IMO-R1:** exactly one draft PR and one #294 evidence/hold comment. No further work until issue-scoped authorization.
