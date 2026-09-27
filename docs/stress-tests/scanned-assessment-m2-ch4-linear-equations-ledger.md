# Scanned Assessment Module `m2.pdf`: Chapter 4 Linear Equations in Two Variables Ledger (Pages 25–41)

> **Custody Metadata & Provenance**  
> - **Source ID**: `SRC-BOOK-MATH-CH2-CH3`  
> - **Acquisition ID**: `ACQ-1DD05CE5AA04B532EC68`  
> - **Source Title**: *Class 9 Mathematics Modules: Polynomials and Coordinate Geometry*  
> - **Binary Digest (SHA-256)**: `1dd05ce5aa04b532ec68c4054f55af1677ecb210be00b8f3085d6f29215a230c`  
> - **Specimen In Scope**: **Pages 25–41** (Book pages `4.1` through `4.17`, Chapter 4: Linear Equations in Two Variables)  
> - **OCR Engine**: RapidOCR 1.2.3  

---

## 1. Chapter Structure & Summary

Chapter 4 spans **17 PDF pages** covering the full algebraic and geometric theory of linear equations in two variables:
1. **Pages 25–32 (Book 4.1–4.9)**: Introduction, Standard Form \(ax + by + c = 0\), Finding Solutions, Graph of Linear Equation, Intercepts, Lines Parallel to Axes, Check Points 1 & 2.
2. **Pages 33–38 (Book 4.10–4.15)**: Assessment Corner (Fill in Blanks, True/False, Single Choice, Multiple Choice, Match Columns, Assertion-Reason, HOTS).
3. **Page 39 (Book 4.16)**: Archive Corner (Olympiad & NTSE items).
4. **Pages 40–41 (Book 4.17)**: Master Decoded Answer Key (Check Points 1 & 2, Assessment Corner, Match Columns, HOTS, Archive Corner).

---

## 2. Mathematical Family Clusters

1. **Standard Form & Coefficient Extraction**: Converting any linear relation to \(ax + by + c = 0\) with identified coefficients.
2. **Origin Incidence**: Testing whether \(c = 0 \iff\) line passes through \((0, 0)\).
3. **Lines Parallel to Axes**: \(x = k\) (vertical, parallel to y-axis) vs \(y = c\) (horizontal, parallel to x-axis).
4. **Infinite Solution Set & Line Equivalence**: Geometric interpretation of solutions as points on the line.
5. **One-Variable vs Two-Variable Dualism**: \(y = 4\) as a single point on a 1D line vs a full 2D line in \(\mathbb{R}^2\).
6. **Enclosed Geometric Triangle Areas**: Calculating area of triangles formed by intersecting lines and coordinate axes.
7. **Simultaneous Systems via Variable Substitution**: Solving for structured coordinates \((a+b, a-b)\).
8. **Quadrant Traversal & Linear Invariants**: Determining which quadrants a line intersects based on signs of intercepts.

---

## 3. Extracted Question Ledger & Official Keys

### Q-MAT-09-LE-CP1-02 (PDF Page 28 / Book 4.4)
- **Section**: CHECK_POINT_1 | **Type**: CHECK_POINT
- **Stem**: Express the following linear equations in the form ax + by + c = 0 and indicate the values of a, b, c: (a) 5x = 7y + 1, (c) 3x = 5y, (d) 9x = 4, (e) 7y + 4 = 0.
- **Official Answer Key**: `(a) 5x - 7y - 1 = 0 (a=5, b=-7, c=-1); (c) 3x - 5y = 0 (a=3, b=-5, c=0); (d) 9x - 4 = 0 (a=9, b=0, c=-4); (e) 7y + 4 = 0 (a=0, b=7, c=4)`
- **Independent Derivation**: Move all terms to LHS: 5x - 7y - 1 = 0; 3x - 5y = 0; 9x + 0y - 4 = 0; 0x + 7y + 4 = 0.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-CP2-07 (PDF Page 31 / Book 4.8)
- **Section**: CHECK_POINT_2 | **Type**: CHECK_POINT
- **Stem**: Does the line 7y + 3x = 0 pass through the origin?
   - *Options*: Yes | No
- **Official Answer Key**: `Yes`
- **Independent Derivation**: Substitute (x, y) = (0, 0): 7(0) + 3(0) = 0. LHS = RHS = 0, so the line passes through the origin.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-CP2-08 (PDF Page 31 / Book 4.8)
- **Section**: CHECK_POINT_2 | **Type**: CHECK_POINT
- **Stem**: State whether the line is parallel to x-axis or y-axis: (a) x = 4, (b) y = -2, (c) 2x + 5 = 0.
- **Official Answer Key**: `(a) parallel to y-axis, (b) parallel to x-axis, (c) parallel to y-axis`
- **Independent Derivation**: x = c represents vertical line parallel to y-axis; y = k represents horizontal line parallel to x-axis.
- **Hardness**: EASY (C1, R0, M0, A0)

### Q-MAT-09-LE-P33-FIB-01 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: FILL_IN_THE_BLANKS
- **Stem**: A rectangle is 8 cm long and 5 cm wide. Its perimeter is doubled when each of its sides is increased by x cm, then its new length is _____ cm.
- **Official Answer Key**: `21`
- **Independent Derivation**: Initial perimeter P = 2(8 + 5) = 26 cm. New perimeter = 2 * 26 = 52 cm. New dimensions are (8 + x) and (5 + x). New perimeter = 2(8 + x + 5 + x) = 2(13 + 2x) = 26 + 4x = 52 => 4x = 26 => x = 6.5 cm. New length = 8 + 6.5 = 14.5 (or if perimeter is doubled by adding x to each side, official key gives 21 or 14). Official key: 14.
- **Hardness**: EASY (C1, R1, M1, A1)

### Q-MAT-09-LE-P33-FIB-02 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: FILL_IN_THE_BLANKS
- **Stem**: The graph of a linear equation in one or two variables is always _____.
- **Official Answer Key**: `a straight line`
- **Independent Derivation**: Degree 1 polynomial equation ax + by + c = 0 defines a straight line in the Cartesian plane.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P33-FIB-05 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: FILL_IN_THE_BLANKS
- **Stem**: A linear equation in two variables has _____ solutions.
- **Official Answer Key**: `infinite`
- **Independent Derivation**: For every chosen real x, there corresponds a unique y = (-ax - c)/b. Thus there are infinitely many solution pairs.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P33-TF-01 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: TRUE_FALSE
- **Stem**: The equation 2x + 5y = 7 has a unique solution.
   - *Options*: True | False
- **Official Answer Key**: `False`
- **Independent Derivation**: A single linear equation in two variables has infinitely many real solutions. False.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P33-TF-02 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: TRUE_FALSE
- **Stem**: The graph of x = 3 is a line parallel to the y-axis.
   - *Options*: True | False
- **Official Answer Key**: `True`
- **Independent Derivation**: All points on x = 3 have x-coordinate 3, forming a vertical line parallel to the y-axis at distance 3. True.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P33-TF-03 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: TRUE_FALSE
- **Stem**: The point (0, 3) lies on the graph of the linear equation 3x + 4y = 12.
   - *Options*: True | False
- **Official Answer Key**: `True`
- **Independent Derivation**: Substitute (0, 3): 3(0) + 4(3) = 12. 12 = 12. True.
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P33-SC-01 (PDF Page 33 / Book 4.10)
- **Section**: ASSESSMENT_CORNER | **Type**: SINGLE_CHOICE
- **Stem**: The graph of the linear equation 2x + 3y = 6 cuts the y-axis at the point:
   - *Options*: (A) (2, 0) | (B) (0, 2) | (C) (3, 0) | (D) (0, 3)
- **Official Answer Key**: `B`
- **Independent Derivation**: At y-axis, x = 0. 2(0) + 3y = 6 => 3y = 6 => y = 2. Point is (0, 2).
- **Hardness**: EASY (C0, R0, M0, A0)

### Q-MAT-09-LE-P34-SC-12 (PDF Page 34 / Book 4.11)
- **Section**: ASSESSMENT_CORNER | **Type**: SINGLE_CHOICE
- **Stem**: Geometric representation of y = 4 as an equation in one variable is:
   - *Options*: (A) A straight line parallel to x-axis | (B) A point on a number line | (C) A straight line parallel to y-axis | (D) A ray in the plane
- **Official Answer Key**: `B`
- **Independent Derivation**: In one variable, y = 4 represents a single unique point on the real number line. In two variables, it represents a line parallel to the x-axis.
- **Hardness**: MEDIUM (C1, R2, M0, A0)

### Q-MAT-09-LE-P37-HOTS-01 (PDF Page 37 / Book 4.14)
- **Section**: HOTS | **Type**: HOTS
- **Stem**: Draw the graphs of 4x - 3y + 4 = 0 and 4x + 3y - 20 = 0. Find the area of the region bounded by these lines and the x-axis.
   - *Options*: (A) 36 sq units | (B) 18 sq units | (C) 12 sq units | (D) 24 sq units
- **Official Answer Key**: `C`
- **Independent Derivation**: Intersection of the two lines: add equations => 8x - 16 = 0 => x = 2. Substitute x = 2 => 4(2) - 3y + 4 = 0 => 3y = 12 => y = 4. Vertex at (2, 4). Intercepts on x-axis (y=0): line 1 gives 4x + 4 = 0 => x = -1. Line 2 gives 4x - 20 = 0 => x = 5. Base of triangle on x-axis is from x = -1 to x = 5, length = 5 - (-1) = 6. Height = y-coordinate of vertex = 4. Area = 1/2 * base * height = 1/2 * 6 * 4 = 12 sq units.
- **Hardness**: MEDIUM (C2, R2, M2, A2)

### Q-MAT-09-LE-P38-HOTS-05 (PDF Page 38 / Book 4.15)
- **Section**: HOTS | **Type**: HOTS
- **Stem**: If (a + b, a - b) is the solution of the equations 3x + 2y = 20 and 4x - 5y = 42, then find the values of a and b.
- **Official Answer Key**: `a = 3, b = 5`
- **Independent Derivation**: Let X = a+b, Y = a-b. System: 3X + 2Y = 20, 4X - 5Y = 42. Multiply (1) by 5 and (2) by 2: 15X + 10Y = 100, 8X - 10Y = 84. Adding gives 23X = 184 => X = 8. Then 3(8) + 2Y = 20 => 2Y = -4 => Y = -2. Now a + b = 8 and a - b = -2. Adding gives 2a = 6 => a = 3. Subtracting gives 2b = 10 => b = 5.
- **Hardness**: MEDIUM (C2, R1, M2, A2)

### Q-MAT-09-LE-P39-ARC-06 (PDF Page 39 / Book 4.16)
- **Section**: ARCHIVE_CORNER | **Type**: ARCHIVE_CORNER
- **Stem**: The line x + y = 2 passes through which quadrants?
   - *Options*: (A) 1st and 3rd | (B) 2nd and 3rd | (C) 3rd and 4th | (D) 1st, 2nd, and 4th
- **Official Answer Key**: `D`
- **Independent Derivation**: x-intercept is (2, 0) in Quadrant I/IV boundary; y-intercept is (0, 2) in Quadrant I/II boundary. The line traverses Quadrants II, I, and IV. It never enters Quadrant III (where both x < 0 and y < 0, making x+y < 0 != 2). Result: 1st, 2nd, 4th quadrants.
- **Hardness**: EASY (C1, R1, M1, A1)

