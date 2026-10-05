# ISS56 Work Report — Independent Candidate B

- **Issue:** [#56](https://github.com/reallaksh19/Grade9v3.5/issues/56) — Polynomial stress test v1 · D4 · Q1–Q10 · Core2 + Core1A · Set B
- **Matched Issue:** [#52](https://github.com/reallaksh19/Grade9v3.5/issues/52) (Independent Candidate A)
- **Branch:** `agent/iss56-polynomial-stress-v1`
- **Pinned Launch Seed:** `91719ad8df2bfc06c6a481590d2e24c510c24835`
- **Renderer Authority:** `Shared/tools/render_core.py` (v2)
- **Protocol:** `Engineering PR delivery v3.2` (`reallaksh19/Common@149770a21ca073df49717a96e2106c967adddc2d`)
- **Independence Status:** Issue #52 and its candidate submissions were **NOT inspected** at any time.
- **Owner Clarification:** NONE required; A/B/C core prompt was completely sufficient and self-contained.
- **Deliverable Status:** CANDIDATE (No golden or publication release self-promotion claimed)

---

## Eight-Unit Delivery Status

| Unit | Status | Evidence Head |
|---|---|---|
| **U1 — Intake & baseline** | PASS | `owner-core-prompt.md` (SHA-256: `46058f7ade3862a6f5707fa0f49c5e284d74b6de56100312d6f1a840d65392b9`, 6539 bytes), launch baseline commit `91719ad8df2bfc06c6a481590d2e24c510c24835`, `chronological-audit.jsonl`. |
| **U2 — Academic/task analysis** | PASS | `question-ledger.json`, `source-cards.json` (10/10 solved, 7 D4 + 3 D3, 5 primary cognitive demands). |
| **U3 — Hardest-target brief** | PASS | `OWN-ISSUE56-POLY-03` (Q3 · JUSTIFY · D4 · Root Multiplicity Parity & Minimal Degree 5 Proof); X/Y/Z/W defined. |
| **U4 — Canonical records** | PASS | `owner.bank.json` (0 problems via `owner_bank.check(complete=True)`), `package.v1.json` (0 schema validation errors via `Draft202012Validator`), `product.manifest.json`. |
| **U5 — Rendered deliverables** | PASS | `rendered/core1a.html` (116,405 bytes), `rendered/core2.html` (253,466 bytes), `rendered/index.html` (22,995 bytes), `render-receipt.json` (0 depth gaps, draft: false, digest: `7909c2addb49b09e`). |
| **U6 — Semantic/interaction audit** | PASS | `qrt-review.json` (10/10 questions achieve full H1–M3 YES verdicts; 10/10 W-leak check PASS), `validation.md`. |
| **U7 — Builder proposal after page** | PASS | `builder-proposal.md` proposing `CONTINUOUS_PARAMETER_SCRUBBER` derived from rendered HTML inspection. |
| **U8 — Independent handoff** | FROZEN | Draft PR created, `candidate-review.md`, `run-receipt.json`, all SHA-256 digests reconciled. |

---

## Key Academic Insights & Decisions

1. **Polynomial Interpolation vs. Infinite Cosets (Q1):** Four data points $(0,1), (1,2), (2,5), (3,10)$ uniquely determine the quadratic $p(x) = x^2 + 1$ only under the degree bound $\deg(p) \le 3$ via the Polynomial Identity Theorem. When the bound is removed, the solution set forms an infinite affine coset $p(x) = x^2 + 1 + x(x-1)(x-2)(x-3)q(x)$ for arbitrary $q(x) \in \mathbb{R}[x]$.
2. **Root Multiplicity Parity (Q2):** Real polynomial curves cross the x-axis with a sign flip if and only if root multiplicity is odd; tangency without crossing preserves sign, forcing even multiplicity ($\ge 2$). Under $\deg(p) \le 4$, zeros at $\pm 2$ (odd $\ge 1$) and $0$ (even $\ge 2$) saturate the degree ($1+1+2=4$), fixing $p(x) = x^4 - 4x^2$ uniquely.
3. **Hardest Target — Minimal Degree 5 Proof (Q3):** Combining positive evaluations $p(0)=1, p(2)=1$ with zero $x=1$ traps $\operatorname{mult}(1) \ge 2$ by the Intermediate Value Theorem, eliminating degrees 1–3. A degree 4 polynomial with zeros only at $\pm 1$ requires an irreducible quadratic factor with $\Delta < 0$, which maintains a strictly constant sign on $\mathbb{R}$, forcing $p(0)$ and $p(2)$ to have opposite signs when multiplied by $(x^2-1)$. This eliminates degree 4. The minimal degree is exactly 5, explicitly constructed as $p(x) = \frac{1}{12}(x-1)^2(x+1)(3x^2-10x+12)$ where $\Delta = -44 < 0$.
4. **Parameter Bifurcations & Degree Drops (Q4):** In $F_a(x) = (a-1)x^4 + 2(a-1)x^3 + (a+2)x^2 + 2(a+2)x = x(x+2)[(a-1)x^2 + (a+2)]$, the parameter $a=1$ causes the leading coefficients of $x^4$ and $x^3$ to vanish simultaneously, dropping the degree to 2. Coincidences between quadratic roots and fixed roots create a triple root at $x=0$ ($a=-2$) and a double root at $x=-2$ ($a=2/5$).
5. **Physical Modeling vs. Empirical Overfitting (Q5):** A folded open rectangular box has physical volume $V(x) = x(10-2x)^2 = 4x^3 - 40x^2 + 100x$ on $(0, 5)$. An empirical quadratic fit $Q(x) = -28x^2 + 92x$ matches entries at $x=0, 1, 2$ purely because 3 points algebraically determine a quadratic; however, $Q(x)$ predicts an unphysical zero at $x=23/7 \approx 3.29$ cm and negative volumes beyond it, diverging by a factor of 2 at $x=3$ cm ($V(3)=48$ vs $Q(3)=24$).
6. **Domain Preservation vs. Function Extension (Q6):** Rational cancellation $\frac{(x-a)(x-1)}{x-a} = x-1$ is valid only on $D_a = \mathbb{R} \setminus \{a\}$. For $a=1$, $x=1$ is excluded from the domain, so $R_1(1)$ is undefined and $R_1$ has no real zeros on its domain. The continuous extension $\tilde{R}(x) = x-1$ exists on $\mathbb{R}$, but extending a function modifies its domain.
7. **Symmetry and Modal Logic (Q7):** Even symmetry $p(-x)=p(x)$ reflects zeros to $\pm 1, \pm 2$, forcing $\deg(p) \ge 4$. Under $\deg \le 4$, $p(x) = x^4 - 5x^2 + 4$ uniquely. Modal claims are classified as necessary under the bound, but shift to contingent possibilities when the degree bound is removed.
8. **Autonomous Difference Polynomials (Q8):** The difference $d(x) = p(x) - q(x)$ is uniquely determined as $2x^3 - 2x$ (yielding $p(3)-q(3)=48$), while individual components $p$ and $q$ remain underdetermined.
9. **Exhaustive Monic Characterization (Q9):** Any candidate quadratic factor must have constant term $c=-1$ to satisfy $p(0)=1$, forcing $\Delta = b^2 + 4 > 0$, so no irreducible quadratic factor can exist. Multiplicity parity forces $a$ even in $(x-1)^a(x+1)^b$, admitting exactly two monic polynomials: $(x-1)^2(x+1)$ and $(x^2-1)^2$.
10. **Refuting Heuristic Rules (Q10):** Decision procedures refute informal heuristics by enforcing domain preservation for cancellation, non-zero leading coefficients for degree, complex conjugate pairs for root counts, and degree bounds for interpolation identity.

---

## Rendered Deliverables

- **Core1A Concept Learning Page:** `evidence/benchmark/ISS56/rendered/core1a.html`
- **Core2 Source Questions Page:** `evidence/benchmark/ISS56/rendered/core2.html`
- **Product Index Portal:** `evidence/benchmark/ISS56/rendered/index.html`
- **Render Receipt:** `evidence/benchmark/ISS56/rendered/render-receipt.json`

Zero gaps remain. Production build completed cleanly with `Shared/tools/render_core.py`.
