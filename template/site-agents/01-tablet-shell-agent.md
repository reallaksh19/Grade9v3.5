# Prompt: Tablet shell and navigation agent (local machine)

> **Phase 0 freeze** (docs/plans/phase0/FREEZE.md): this agent changes site chrome and navigation only.
> Do not add or edit learner content, and do not add a renderer:
> `python3 Shared/tools/renderer_inventory.py --check` must still pass.

Give this to a local agent with Python 3, Node.js and git. Copy everything below the line.

---

You are implementing `docs/specs/TABLET-SHELL-AND-NAVIGATION.md` in the Grade9V3 repository.
Your agent id is `{{AGENT_ID}}`.

1. Read the spec **in full** before changing anything, twice if needed. It is the only source
   of truth; where this prompt and the spec differ, the spec wins.
2. Follow its tasks **T0 → T9 in order**, one commit per task (`ui(T<n>): …`) on the branch
   `ui/tablet-shell`. Do not start a task until the previous task's **Accept** checks pass, and
   paste each task's acceptance output into your notes.
3. Two tools decide whether you are done; your own impression does not:
   - `python Shared/tools/site_nav_audit.py`, the static navigation audit. Its baseline may
     only shrink.
   - `node tools/site-audit/tablet-audit.mjs`, the browser audit at 10-inch tablet sizes. It
     needs `python -m http.server 8765` running from the repository root.
4. Hard rules (spec §2 and §8):
   - edit `public/` only, never `docs/`, and never any file under `public/**/explorers/**`;
   - change generators, not generated files;
   - no CDNs or new external hosts;
   - do not edit tests (except shrinking the site-audit baseline after real fixes);
   - write readable JavaScript: no one-liners, and never use `top`, `name`, `status`,
     `parent` or `self` as variable names.
5. The known 5 browser-runtime unit-test failures (listed in spec T0) are not yours to fix.
   Any **other** failing test is.
6. If the spec does not cover a situation, choose the option that changes fewer files, and
   record it under "Decisions" in your report.
7. Finish with spec T9:
   - write the final report (spec §10) as the PR description;
   - push `ui/tablet-shell`;
   - open a pull request titled `Tablet shell and navigation repair`.
