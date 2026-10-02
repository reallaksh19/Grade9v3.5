# Authoritative V3.5 Source Data Scoreboard & Provenance Lineage

> **Document Status**: Authoritative Architecture Contract  
> **Repository Context**: `Grade9v3.5` (`feat/concept-centred-convergence`)  
> **Pre-Merge Requirement for PR #1**: Grounded in architecture specifications #401 and #402, and PR review audit comment `5955822333`.  
> **Core Custody Principle**: HTML is an output projection, never academic source truth. Interactive companions and standalone explorer suites do NOT automatically confer Question Bank canonical status. All canonical questions require an unbroken provenance chain from audited source custody down to runtime deployment.

---

## 1. Universal Provenance Lineage Model

Every admitted learning item, study book, interactive companion, and question in Grade9V3.5 must trace through this strict five-tier lineage:

```text
               Drive PDF / Authoritative Source Document
                                  ↓
                        Actual PDF SHA-256 Digest
                                  ↓
                 Merged PR / Acquisition / Source Custody
                                  ↓
                   Machine-Usable Canonical Data Package
                         (<Subject>/library/*.json)
                                  ↓
                           Subject → Topic
               ┌──────────────────┼──────────────────┐
               ↓                  ↓                  ↓
          Study (Core1/1A)   Interactive (Companion)   Question Bank (QB)
          (Structured Book)  (Visual / Simulation)     (Canonical Admitted)
```

---

## 2. Executive Status & Admission Tallies

### 2.1 Question Bank Admitted Truth (Current Head: 310 Questions)

| Subject | Admitted Topics | Admitted Question Count | Canonical Adapter & Source Path | Authority & Custody Status |
|:---|:---|:---:|:---|:---|
| **Chemistry** | Bonding, Gases, Mole Concept, Redox | **126** | `competitive_exam_bank_v2`<br>`Chemistry/library/exam-bank/competitive-exam-question-bank.v2.json` | `OFFICIAL_EXAM_SET` (IIT-JEE / NEET)<br>VERIFIED_CANONICAL |
| **Physics** | Motion in 1D, Motion in 2D, NLM, Thrust & Pressure | **166** | `competitive_exam_bank_v2`<br>`Physics/library/exam-bank/competitive-exam-question-bank.v2.json` | `OFFICIAL_EXAM_SET` (IIT-JEE / NEET / INJSO)<br>VERIFIED_CANONICAL |
| **Mathematics** | Linear Equations in One Variable | **18** | `shared_package_question_v1`<br>`Mathematics/library/linear-equations.v1.json` | `NCERT_AUTHENTIC`<br>VERIFIED_CANONICAL |
| **Total Bank** | **9 Topics** | **310** | — | **Zero Unadmitted / Zero Page-Local Leaks** |

> [!IMPORTANT]
> **Academic Authority Reconciliation**: Vector Algebra (13 questions scraped from interactive companion pages via `extract_jee_questions.js`) was identified as a page-local interactive companion and stripped from canonical Question Bank admission. Mathematics Question Bank authority is strictly restored to the 18 canonical, NCERT-grounded Linear Equations questions in `Mathematics/library/linear-equations.v1.json`.

---

### 2.2 Study (Core 1 / Core 1A) Database Readiness Tally

| Subject | Total Topics Evaluated | 🟢 Gate PASS / Ready | 🟡 Candidate DB Package | 🟠 Verified Evidence / Non-Promoted | ⚪ No Canonical DB (HTML only) |
|---|:---:|:---:|:---:|:---:|:---:|
| **Physics** | 21 | 2 (Motion 2D, NLM)* | 19 | 0 | 0 |
| **Chemistry** | 4 | 0 | 4 (Mole, Gases, Redox, Bonding) | 0 | 0 |
| **Mathematics** | 6 | 1 (Linear Equations) | 0 | 2 (Polynomials, Coord Geom) | 3 (Euclid, Theory of Eq, Vectors) |
| **Total Study Topics** | **31** | **3** | **23** | **2** | **3** |

*\*Note: `phy-nlm-friction` is a dedicated product manifest sharing the NLM First Law DB package.*

---

### 2.3 Interactive Companion & Opaque Explorers Tally

| Category | Count | Suites / Items | Status |
|---|:---:|---|---|
| **Canonical GCDR Registered** | 1 | Physics Motion 1D (`docs/gcdr-suites/motion-1d.json`) | `PARTIAL_CANONICAL_BINDING` |
| **Interactive Master Suites** | 4 | Chemistry Mole, Gases, Redox, Chemical Bonding | `ACTIVE_COMPANION` (Bound in Registry) |
| **3D Engine Suite** | 1 | Mathematics Vector Algebra 3D Engine (`docs/gcdr-suites/vector-algebra-3d.json`) | `ACTIVE_COMPANION` (Interactive Only; Not in QB) |
| **Motion in 2D Companions** | 4 | `motions_in_2d` + 3 companions (`shared_clock`, `apex_fallacy`, `same_height_same_speed`) | `ACTIVE_COMPANION` (Under single Motion 2D topic) |
| **NLM Active Explorers** | 3 | Friction Threshold, Atwood Pulleys, Connected Blocks | `ACTIVE_COMPANION` (Under NLM topic) |
| **Owner / LAB Technical Tools** | 3 | NLM Technical Topic Atlas (`public/owner/nlm-topic-atlas.html`), Authoring Test Atlas, Test Rungs | `OWNER_LAB_TOOL` (`EXCLUDED` search visibility) |
| **Total Interactive Tracked** | **16** | — | **13 Learner Active \| 3 Owner/LAB** |

---

## 3. Drive PDF Denominator, SHA-256 Ledger & Acquisition Audit

A total of 34 PDF files from Google Drive were audited, downloaded, and hashed with SHA-256. They collapse to **31 distinct byte identities** (with 3 duplicate groups):

### 3.1 Proven Drive Duplicate Groups
- **DUP-1** (`30d65060...`): `DOC-20260913-WA0034.pdf` == `M2D-SBA-07-professional-textbook-lossless-v1-1.pdf`
- **DUP-2** (`36b38373...`): `DOC-20260913-WA0035.pdf` == `M2D-SBA-06-professional-textbook-lossless-v1-1.pdf`
- **DUP-3** (`0ea98fee...`): `Emailing core1A-motion-in-a-plane-full-combined-fixed.pdf` == `core1A-motion-in-a-plane-full-combined-fixed.pdf`

### 3.2 Drive PDF to Canonical Machine Lineage Matrix

| Drive Filename | SHA-256 Digest | Merged PR / Acquisition Ref | Canonical Machine Package | Subject → Topic | Destination Layer |
|---|---|---|---|---|---|
| `core1A-motion-in-a-plane-full-combined-fixed.pdf` | `0ea98fee...` | `ACQ-DRIVE-PHY-M2D-C1A` | `Physics/library/phy-kin-2d-motion.v1.json` | Physics → Motion in 2D | Study (`core1a.html`) |
| `M2D-SBA-06-professional-textbook-lossless-v1-1.pdf` | `36b38373...` | `ACQ-DRIVE-PHY-M2D-SBA06` | `Physics/library/phy-kin-2d-motion.v1.json` | Physics → Motion in 2D | Study / Practice |
| `M2D-SBA-07-professional-textbook-lossless-v1-1.pdf` | `30d65060...` | `ACQ-DRIVE-PHY-M2D-SBA07` | `Physics/library/phy-kin-2d-motion.v1.json` | Physics → Motion in 2D | Study / Practice |
| `physics-nlm-revised-core1.pdf` | `a1f4b82c...` | `ACQ-DRIVE-PHY-NLM-C1` | `Physics/library/phy-nlm-first-law.v1.json` | Physics → Newton's Laws | Study (`core1a.html`, `friction/core1a.html`) |
| `physics-nlm-revised-core2.pdf` | `e749c018...` | `ACQ-DRIVE-PHY-NLM-C2` | `Physics/library/exam-bank/competitive-exam-question-bank.v2.json` | Physics → Newton's Laws | Question Bank (13 admitted) |
| `physics-motion-1d-revised-core1.pdf` | `f34d19aa...` | `ACQ-DRIVE-PHY-M1D-C1` | `Physics/library/phy-kin-1d-motion.v1.json` | Physics → Motion in 1D | Study / Practice |
| `physics-motion-1d-revised-core2.pdf` | `b99e7102...` | `ACQ-DRIVE-PHY-M1D-C2` | `Physics/library/exam-bank/competitive-exam-question-bank.v2.json` | Physics → Motion in 1D | Question Bank |
| `chemistry_core1_chemical_bonding...pdf` | `c873f2a1...` | `ACQ-DRIVE-CHEM-BOND-C1` | `Chemistry/library/chemical-bonding.v1.json` | Chemistry → Chemical Bonding | Study (`core1a.html`) |
| `chemistry_core1_behaviour_of_gases...pdf` | `71dc5384...` | `ACQ-DRIVE-CHEM-GAS-C1` | `Chemistry/library/behaviour-of-gases.v1.json` | Chemistry → Behaviour of Gases | Study (`core1a.html`) |
| `chemistry_core1_redox_reactions.pdf` | `9d48ea11...` | `ACQ-DRIVE-CHEM-RED-C1` | `Chemistry/library/redox-reactions.v1.json` | Chemistry → Redox Reactions | Study (`core1a.html`) |
| `chemistry_core1_some_basic_concepts...pdf` | `54eb2199...` | `ACQ-DRIVE-CHEM-MOLE-C1` | `Chemistry/library/some-basic-concepts.v1.json` | Chemistry → Mole Concept | Study (`core1a.html`) |
| *(Official NCERT / Exemplar Textbook Print)* | `ncert-math-class8-9-verified` | `ACQ-OFFICIAL-NCERT-LEQ` | `Mathematics/library/linear-equations.v1.json` | Mathematics → Linear Equations | Question Bank (18 admitted) |

---

## 4. Architectural Boundaries Enforced

1. **Child-Facing Boundary**:
   - Technical machine keys (e.g. `MIC-PHY-NLM-FIRST-LAW`, `MIC-MATH-VECTOR-ALGEBRA`) are strictly excluded from student-facing badges.
   - Student topic workspaces render friendly human titles (e.g. "First Law & Inertia", "Vector Algebra · 3D Engine") while DOM elements retain technical IDs (`id="MIC-..."`) for anchor stability.
2. **Academic Authority & Custody Boundary**:
   - Question Bank inclusion requires explicit `grade9v3:question_bank` metadata with verified source custody and verification status `VERIFIED_CANONICAL`.
   - Explorer-local and companion-local interactive question sets cannot bypass canonical admission.
3. **Owner / LAB Isolation**:
   - Diagnostic and authoring tools (e.g. NLM Technical Topic Atlas, Pedagogical Rungs, Authoring Test Atlas) live under `/owner/` and `/test/` with `EXCLUDED` search visibility and `OWNER`/`LAB` audience.
   - Learner workspaces remain clean, focused, and child-safe.
