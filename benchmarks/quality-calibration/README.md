# Quality calibration corpus

Fixed examples of bad and good learner products. Phase 1 turns them into a machine-readable
quality contract; Phase 4's rendered gate must **fail every negative specimen for the findings
listed** and **pass the positive references**. See
[docs/plans/LEARNER-PRODUCT-QUALITY-REBUILD.md](../../docs/plans/LEARNER-PRODUCT-QUALITY-REBUILD.md).

## Contents

| Id | Kind | What it is | Where |
|---|---|---|---|
| S1 | negative | Motion-in-2D six-Core HTML product | `specimens/S1-motion2d-six-core-html/` |
| S2 | negative | The same product's six PDFs (text only: no figures) | `specimens/S2-motion2d-six-core-pdf/` |
| S3 | negative | Projectile six-Core Markdown prototype (HOLD as output) | `specimens/S3-projectile-prototype-markdown/` |
| S4 | negative | PR #288 preview | `specimens/S4-pr288-preview/` |
| S5 | negative | Research-first renderer output (#290); no Core2A/2B | `specimens/S5-research-first-render/` |
| R1 | positive | Owner's compiled Core1A textbook (staged construction) | not in the repository; grammar encoded in the manifest |
| R2 | positive | Owner's tablet question bank (77 questions, SVG, hint ladder, trap, verification) | pinned by commit on `feat/all-cores-curriculum-and-speed-hacks` |

`manifest.v1.json` records, for every specimen, where it came from (branch, commit, generator),
the sha256 of every file, and the defects it shows (`expected_findings`, from Audits
#296–#298). For every reference, it records custody, the grammar the gate must recognise, and
where the file is.

## Rules

- **Never edit a specimen.** A specimen is evidence of a defect. To add one, create a new
  folder and a new manifest entry, with its source pin and expected findings.
- **References stay where they are.** R2 is pinned by commit and sha256, not copied.
- **Before each calibration run, search the repository for the references**, including the
  R1 textbook, which is not yet located:

  ```sh
  git fetch origin
  for b in $(git branch -r | grep -v HEAD); do
    git ls-tree -r --name-only "$b" | grep -iE '\.(pdf|html)$' | grep -iE 'core.?1a|textbook|combined|question.?bank|tablet' | sed "s|^|$b: |"
  done
  ```

  If R1 turns up, pin its branch, commit and sha256 in the manifest (`custody: REPOSITORY`).
- Check the corpus:

  ```sh
  python3 Shared/tools/calibration_corpus.py --check --refs
  ```

  `--refs` needs the reference branch fetched (`git fetch origin feat/all-cores-curriculum-and-speed-hacks`).
