# Scanned Assessment Module `m2.pdf`: Chapter 5 Introduction to Euclid's Geometry Ledger (Pages 42–49)

> **Custody Metadata & Provenance**  
> - **Source ID**: `SRC-BOOK-MATH-CH2-CH3`  
> - **Acquisition ID**: `ACQ-1DD05CE5AA04B532EC68`  
> - **Source Title**: *Class 9 Mathematics Modules: Polynomials and Coordinate Geometry*  
> - **Binary Digest (SHA-256)**: `1dd05ce5aa04b532ec68c4054f55af1677ecb210be00b8f3085d6f29215a230c`  
> - **Specimen In Scope**: **Pages 42–49** (Book pages `5.1` through `5.8`, Chapter 5: Introduction to Euclid's Geometry)  
> - **OCR Engine**: RapidOCR 1.2.3  

---

## 1. Chapter Structure & Summary

Chapter 5 spans **8 PDF pages** establishing the foundation of axiomatic mathematics and deductive proofs:
1. **Pages 42–44 (Book 5.1–5.3)**: Historical Context (Thales, Pythagoras, Euclid circa 300 BCE), Definitions (point, line, surface).
2. **Pages 45–46 (Book 5.4–5.5)**: Euclid's 7 Axioms and 5 Postulates (specifically Postulate 5: Parallel Postulate).
3. **Pages 47–48 (Book 5.6–5.7)**: Deductive Illustrations 5.1–5.5 (midpoint uniqueness, parallel lines through a point, collinearity proofs).
4. **Page 49 (Book 5.8)**: Structural Outline, Theorems (e.g. Theorem 5.1: Two lines intersect at at most one point), Axioms summary.

---

## 2. Mathematical Family Clusters

1. **Axiomatic Geometry & Definitions**: Definitions of undefined terms (point, line, plane) in deductive systems.
2. **Axioms of Equality & Superposition**: Application of Euclid's 7 axioms (wholes, parts, equals added to equals).
3. **Parallel Postulate & Equivalences**: Euclid's 5th Postulate (\(lpha + eta < 180^\circ\)) and Playfair's Axiom.
4. **Deductive Proofs from Axioms**: Proving midpoint properties without metric distance formulas.
5. **Incidence & Intersection Invariants**: Uniqueness of straight lines through two points; intersection at at most one point.

---

## 3. Extracted Question Ledger & Proof Invariants

### Q-MAT-09-EG-DEF-01 (PDF Page 43 / Book 5.2)
- **Section**: EUCLIDS_DEFINITIONS | **Type**: DEFINITION
- **Stem**: State Euclid's definition of: (i) a point, (ii) a line, (iii) a surface.
- **Official Answer Key / Proof Goal**: `(i) A point is that which has no part; (ii) A line is breadthless length; (iii) A surface is that which has length and breadth only.`
- **Independent Derivation**: Direct quote from Euclid's Elements, Book I Definitions 1, 2, and 5.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-EG-AXIOM-01 (PDF Page 45 / Book 5.4)
- **Section**: EUCLIDS_AXIOMS | **Type**: AXIOM
- **Stem**: If b = a and c = a, then what is the relationship between b and c according to Euclid's Axioms?
- **Official Answer Key / Proof Goal**: `b = c`
- **Independent Derivation**: Euclid's Axiom 1: Things which are equal to the same thing are equal to one another.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-EG-AXIOM-04 (PDF Page 45 / Book 5.4)
- **Section**: EUCLIDS_AXIOMS | **Type**: AXIOM
- **Stem**: Things which coincide with one another are _____ to one another.
- **Official Answer Key / Proof Goal**: `equal`
- **Independent Derivation**: Euclid's Axiom 4: Principle of superposition—geometric figures that coincide exactly in position and dimensions are equal.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-EG-POST-05 (PDF Page 46 / Book 5.5)
- **Section**: EUCLIDS_POSTULATES | **Type**: POSTULATE
- **Stem**: State Euclid's Fifth Postulate and its modern equivalent (Playfair's Axiom).
- **Official Answer Key / Proof Goal**: `If a straight line falling on two straight lines makes the interior angles on the same side of it taken together less than two right angles, then the two straight lines, if produced indefinitely, meet on that side on which the sum of angles is less than two right angles. Playfair's Axiom: For every line l and for every point P not lying on l, there exists a unique line m passing through P and parallel to l.`
- **Independent Derivation**: Euclid Book I Postulate 5 establishes non-intersecting parallel lines and uniqueness of parallels.
- **Hardness**: MEDIUM (C2, R1, M1, A0)

### Q-MAT-09-EG-ILL-01 (PDF Page 47 / Book 5.6)
- **Section**: ILLUSTRATIONS | **Type**: PROOF_ILLUSTRATION
- **Stem**: If a point C lies between two points A and B such that AC = BC, then prove that AC = 1/2 AB.
- **Official Answer Key / Proof Goal**: `AC = 1/2 AB (Proved)`
- **Independent Derivation**: Since C lies between A and B, AC + BC = AB. Given AC = BC. Adding AC to both sides (Axiom 2): AC + AC = BC + AC => 2AC = AB. Applying Axiom 7 (halves of equals are equal): AC = 1/2 AB.
- **Hardness**: EASY (C1, R1, M1, A1)

### Q-MAT-09-EG-ILL-02 (PDF Page 47 / Book 5.6)
- **Section**: ILLUSTRATIONS | **Type**: PROOF_ILLUSTRATION
- **Stem**: Prove that every line segment has one and only one mid-point.
- **Official Answer Key / Proof Goal**: `Unique mid-point (Proved by contradiction)`
- **Independent Derivation**: Suppose segment AB has two distinct mid-points C and D. Then AC = 1/2 AB and AD = 1/2 AB. By Axiom 1 (things equal to the same thing are equal): AC = AD. Subtracting AC from AD gives CD = 0, which contradicts that C and D are distinct. Hence C and D coincide.
- **Hardness**: MEDIUM (C2, R1, M2, A1)

### Q-MAT-09-EG-ILL-05 (PDF Page 48 / Book 5.7)
- **Section**: ILLUSTRATIONS | **Type**: PROOF_ILLUSTRATION
- **Stem**: If lines AB, AC, AD and AE are all parallel to a line l, prove that points A, B, C, D and E are collinear.
- **Official Answer Key / Proof Goal**: `Points A, B, C, D, E are collinear (Proved)`
- **Independent Derivation**: By Playfair's Axiom (equivalent to Postulate 5), through a point A not on l, there can pass only one unique line parallel to l. Since AB, AC, AD, AE all pass through point A and are parallel to l, they must represent the same identical line. Hence all points A, B, C, D, E lie on the same line and are collinear.
- **Hardness**: MEDIUM (C2, R1, M2, A0)

### Q-MAT-09-EG-P49-TH-01 (PDF Page 49 / Book 5.8)
- **Section**: THEOREMS | **Type**: THEOREM
- **Stem**: Two distinct lines cannot have more than one point in common. Prove.
- **Official Answer Key / Proof Goal**: `At most one point of intersection (Proved)`
- **Independent Derivation**: Let l and m be two distinct lines. Suppose they intersect at two distinct points P and Q. Then both lines l and m pass through points P and Q. But by Axiom 5.1 / Postulate 1, there is a unique line passing through two distinct points. This contradicts that l and m are distinct lines. Therefore, two distinct lines cannot have more than one point in common.
- **Hardness**: EASY (C1, R0, M1, A0)

