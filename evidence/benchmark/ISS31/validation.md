# Issue 31 validation ledger

Candidate: independent agent A · governed rendered continuation  
Pinned source: `e01c6365acfd6aec84c0a6e94f11b683bd961f6e`  
Frozen first partial submission: `27dd6611b6bf9c824f8e066386a41af22a6ea88c`  
Owner execution clarification: issue comment `5978104772`  
Validated generated-artifact commit: `c3eef85875c7499466a3aeb3903167f60a86482f`

| Check | State | Evidence / consequence |
|---|---|---|
| Q1–Q10 verbatim owner custody | PASS | Owner bank was created through repaired `owner_bank.py new`, then checked against the exact ten-question intake. |
| Official/PYQ identity avoided | PASS | Owner custody remains `OWNER_SUPPLIED_RAW_INPUT`; no exam/year/paper identity introduced. |
| Owner-bank path repair regressions | PASS | Focused path, altered-stem, intake-mismatch and official-identity regressions passed in cold-run `37194109839`. |
| Chemistry package schema + references | PASS | Cold-run schema validator and `Shared.library.resolve --schema` passed. |
| Product manifest | PASS | Chemistry package + owner bank; 7 canonical microtopics; exactly 10 Core2 questions; `output_roles = ["CORE1A","CORE2"]`. |
| `render_core.py gaps` | PASS | 0 depth gaps; 0 subject-authority findings. |
| `render_core.py build` | PASS | `render_core/2`; render digest `b7e0eed726cf0caa`; semantic digest `5754d048b745feab`; non-draft output. |
| Core1A HTML | PASS | 174,556 bytes; SHA-256 `42f8b0801ba2c7a78fb40e84129cc350db611f3a86292b1baf0211f6e883bf02`. |
| Core2 HTML | PASS | 226,103 bytes; SHA-256 `01bdf42d39a70ef53a9ed3d7ff301eeff098585c4da9502f4f6c2fad4078d523`. |
| Strict learner-quality gate | PASS | Contract 1.8.1; 0 findings; rendered measurement complete. |
| Chromium tablet audit | PASS | Both pages have `errors: []`; sampled portrait/landscape viewports have 0 horizontal overflow, 0 small targets, 0 protected-search matches, 0 external requests and 0 staged-SVG violations. |
| Hardest target | PASS | Q5 · MODEL · D2. |
| Meaningful Q5 interaction | PASS | Attempt-first Core2 + three-stage two-lens Core1A visual + predict/reveal worked route + gated support. |
| Builder-improvement inspection | PASS | Actual pages inspected; no builder code change recommended because existing reusable components express the intended decision and pass quality/browser gates. |
| Paired issue #32 inspected | NO | Independence preserved. |
| Golden/release promotion | NO | Candidate is validated, but no merge/publication/golden authority is inferred. |

## Benchmark blocker resolution

The two blockers remain historically visible in the audit. The first was repaired in `f1621cd…`. The second was resolved operationally by using a governed GitHub Actions checkout/runtime rather than pretending the connector or local shell was a repository runtime.

The final HTML bytes were not hand-edited; they are the exact output preserved by the successful cold-run.
