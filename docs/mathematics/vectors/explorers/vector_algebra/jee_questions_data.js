/**
 * Vector Algebra Master Question Registry & Step-by-Step Solutions Database
 * 13 locally audited diagnostic records selected from the live ExamSIDE JEE Main Mathematics Vector Algebra corpus.
 * Live source snapshot (2026-09-20): 282 questions, 2002-2026.
 * External question text is retained here only where already authored in this PR; source-corpus count is not a claim that all 282 questions are embedded locally.
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "VEC-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 5th April Evening Shift",
    "subtab": 1,
    "subtabName": "Basics & Linear Combinations",
    "year": "2026",
    "q": "Let O be the origin, vector OP = a and vector OQ = b. If R is a point on OP such that OP = 5 OR, and M is a point such that OQ = 5 RM, then the vector PM expressed in terms of a and b is:",
    "options": [
      {
        "key": "A",
        "text": "PM = ⅕ b - ⅘ a"
      },
      {
        "key": "B",
        "text": "PM = ⅘ a + ⅕ b"
      },
      {
        "key": "C",
        "text": "PM = ⅕ b - a"
      },
      {
        "key": "D",
        "text": "PM = b - ⅘ a"
      }
    ],
    "correct": "A",
    "formula": "PM = OM - OP,  OR = ⅕ a,  RM = ⅕ b ⇒ OM = OR + RM = ⅕ a + ⅕ b",
    "steps": [
      "Given: vector OP = a ⇒ R is on OP with OP = 5 OR ⇒ vector OR = ⅕ a.",
      "Given: vector OQ = b with OQ = 5 RM ⇒ vector RM = ⅕ b.",
      "Find position vector of M: vector OM = vector OR + vector RM = ⅕ a + ⅕ b.",
      "Compute vector PM = vector OM - vector OP = (⅕ a + ⅕ b) - a.",
      "Combine like terms: PM = (⅕ - 1) a + ⅕ b = -⅘ a + ⅕ b = ⅕ b - ⅘ a."
    ],
    "ans": "PM = ⅕ b - ⅘ a (Option A)",
    "trap": "Always track the origin of displacement vectors! Vector RM is relative to R, not O; OM = OR + RM.",
    "targetTab": "tab-basis",
    "simParams": {
      "ax": 5,
      "ay": 0,
      "bx": 0,
      "by": 5
    },
    "simSummary": [
      "Vector a = [5, 0, 0]",
      "Vector b = [0, 5, 0]",
      "PM = [1/5 b - 4/5 a]"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The basis rig can display vectors, but it does not represent the points O,P,Q,R,M or the affine construction in the question.",
    "teacherCheck": "Reconstruct OM=OR+RM=(a+b)/5, then subtract OP=a; the residual is PM=b/5-4a/5.",
    "takeaway": "With position vectors, first put every point relative to one origin before subtracting endpoints.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q02",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 24th January Morning Shift",
    "subtab": 1,
    "subtabName": "Basics & Linear Combinations",
    "year": "2025",
    "q": "If a and b are unit vectors such that |a + b| = √3, then the value of (2a - 5b) · (3a + b) is:",
    "options": [
      {
        "key": "A",
        "text": "-11/2"
      },
      {
        "key": "B",
        "text": "-7/2"
      },
      {
        "key": "C",
        "text": "+5/2"
      },
      {
        "key": "D",
        "text": "-9/2"
      }
    ],
    "correct": "A",
    "formula": "|a + b|² = |a|² + |b|² + 2(a · b) = 3 ⇒ 1 + 1 + 2(a · b) = 3 ⇒ a · b = ½",
    "steps": [
      "Given: |a| = 1, |b| = 1, and |a + b|² = 3.",
      "Expand norm squared: |a + b|² = |a|² + |b|² + 2(a · b) = 1 + 1 + 2(a · b) = 2 + 2(a · b).",
      "Set 2 + 2(a · b) = 3 ⇒ 2(a · b) = 1 ⇒ a · b = ½ (which corresponds to θ = 60°).",
      "Expand target dot product:",
      "E = (2a - 5b) · (3a + b) = 6|a|² + 2(a · b) - 15(a · b) - 5|b|².",
      "E = 6(1) - 13(a · b) - 5(1) = 1 - 13(a · b).",
      "Substitute a · b = ½: E = 1 - 13(½) = 1 - 6.5 = -5.5 = -11/2."
    ],
    "ans": "-11/2 (Option A)",
    "trap": "Do not treat vectors as scalars! The cross terms 2(a·b) - 15(b·a) combine to -13(a·b).",
    "targetTab": "tab-dot",
    "simParams": {
      "theta_deg": 60,
      "magA": 1,
      "magB": 1
    },
    "simSummary": [
      "Unit vectors: |a| = 1, |b| = 1",
      "Angle θ = 60° (a · b = 0.5)",
      "Target dot product = -11/2 = -5.5"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "EXACT",
    "simFidelityNote": "The dot-product rig exactly binds |a|=|b|=1 and θ=60°, which is the state implied by |a+b|=√3.",
    "teacherCheck": "Check |a+b|²=2+2cos60°=3, then independently expand the target dot product to -11/2.",
    "takeaway": "Convert norm information into a dot product before expanding linear combinations.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": [
      "simParams.theta_deg",
      "simParams.magA",
      "simParams.magB"
    ]
  },
  {
    "id": "VEC-Q03",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 30th January Morning Shift",
    "subtab": 1,
    "subtabName": "Basics & Linear Combinations",
    "year": "2024",
    "q": "If a unit vector u makes angles π/3 with i, π/4 with j, and an acute angle θ with k, then the value of θ is:",
    "options": [
      {
        "key": "A",
        "text": "π/6"
      },
      {
        "key": "B",
        "text": "π/3"
      },
      {
        "key": "C",
        "text": "π/4"
      },
      {
        "key": "D",
        "text": "5π/12"
      }
    ],
    "correct": "B",
    "formula": "cos² α + cos² β + cos² γ = 1",
    "steps": [
      "Direction cosines of unit vector u are: l = cos(π/3), m = cos(π/4), n = cos θ.",
      "We have l = ½, m = 1/√2, n = cos θ.",
      "Apply fundamental identity: l² + m² + n² = 1.",
      "(½)² + (1/√2)² + cos² θ = 1 ⇒ ¼ + ½ + cos² θ = 1.",
      "¾ + cos² θ = 1 ⇒ cos² θ = ¼.",
      "Since θ is an acute angle: cos θ = +½ ⇒ θ = π/3 (60°)."
    ],
    "ans": "π/3 (Option B)",
    "trap": "Direction cosines satisfy cos²α + cos²β + cos²γ = 1 (sum of squares = 1, NOT sum of angles = 180°!).",
    "targetTab": "tab-basis",
    "simParams": {
      "alpha_deg": 60,
      "beta_deg": 45,
      "gamma_deg": 60
    },
    "simSummary": [
      "Direction angles: α = 60°, β = 45°",
      "Sum of squared cosines: 0.25 + 0.5 + 0.25 = 1.0",
      "γ = 60°"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The basis rig demonstrates direction cosines, but the loader does not bind all three direction-angle constraints as the question's exact state.",
    "teacherCheck": "Verify cos²60°+cos²45°+cos²60°=1.",
    "takeaway": "Direction cosines obey a sum-of-squares identity; direction angles do not generally sum to 180°.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q04",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 24th January Evening Shift",
    "subtab": 2,
    "subtabName": "Dot Product & Projections",
    "year": "2026",
    "q": "Let a = 2i + 3j - k and b = i - 2j + 2k. The vector component of a orthogonal (perpendicular) to b is:",
    "options": [
      {
        "key": "A",
        "text": "⅓ (8i + 5j + k)"
      },
      {
        "key": "B",
        "text": "⅑ (24i + 15j - 3k)"
      },
      {
        "key": "C",
        "text": "⅔ (2i + 3j - k)"
      },
      {
        "key": "D",
        "text": "⅓ (5i + 11j - 7k)"
      }
    ],
    "correct": "A",
    "formula": "a_perp = a - a_parallel = a - [(a · b) / |b|²] b",
    "steps": [
      "Compute dot product: a · b = (2)(1) + (3)(-2) + (-1)(2) = 2 - 6 - 2 = -6.",
      "Compute magnitude squared |b|² = 1² + (-2)² + 2² = 1 + 4 + 4 = 9.",
      "Parallel projection along b: a_parallel = [(a · b) / |b|²] b = (-6 / 9) b = -⅔ (i - 2j + 2k).",
      "Perpendicular rejection: a_perp = a - a_parallel = (2i + 3j - k) - (-⅔ i + ⁴/₃ j - ⁴/₃ k).",
      "x-component: 2 + ⅔ = ⁸/₃.",
      "y-component: 3 - ⁴/₃ = ⁵/₃.",
      "z-component: -1 + ⁴/₃ = +⅓.",
      "Combine: a_perp = ⅓ (8i + 5j + k)."
    ],
    "ans": "⅓ (8i + 5j + k) (Option A)",
    "trap": "Remember a_perp = a - a_parallel! Verify orthogonality: (8)(1) + (5)(-2) + (1)(2) = 8 - 10 + 2 = 0.",
    "targetTab": "tab-dot",
    "simParams": {
      "ax": 2,
      "ay": 3,
      "az": -1,
      "bx": 1,
      "by": -2,
      "bz": 2
    },
    "simSummary": [
      "Vector a = 2i + 3j - k",
      "Vector b = i - 2j + 2k",
      "Orthogonal Rejection: a_perp · b = 0"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The projection rig shows parallel/rejection geometry but does not load the question's component vectors a and b.",
    "teacherCheck": "After computing a⊥=(8,5,1)/3, dot it with b=(1,-2,2): (8-10+2)/3=0.",
    "takeaway": "A rejection vector should be checked by a zero dot product with the projection direction.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q05",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 8th April Evening Shift",
    "subtab": 2,
    "subtabName": "Dot Product & Projections",
    "year": "2025",
    "q": "Let a and b be two non-zero vectors such that |a + b| = |a - b|. The angle between a and b is:",
    "options": [
      {
        "key": "A",
        "text": "0°"
      },
      {
        "key": "B",
        "text": "45°"
      },
      {
        "key": "C",
        "text": "90°"
      },
      {
        "key": "D",
        "text": "180°"
      }
    ],
    "correct": "C",
    "formula": "|a + b|² = |a - b|² ⇔ 4(a · b) = 0 ⇔ a ⊥ b",
    "steps": [
      "Square both sides: |a + b|² = |a - b|².",
      "Expand LHS: |a|² + |b|² + 2(a · b).",
      "Expand RHS: |a|² + |b|² - 2(a · b).",
      "Equate and cancel norms: 2(a · b) = -2(a · b) ⇒ 4(a · b) = 0.",
      "Since a and b are non-zero: a · b = 0 ⇒ cos θ = 0 ⇒ θ = 90° (π/2 radians)."
    ],
    "ans": "90° (Option C)",
    "trap": "A parallelogram has equal diagonals if and only if it is a rectangle (vectors are orthogonal)!",
    "targetTab": "tab-dot",
    "simParams": {
      "theta_deg": 90
    },
    "simSummary": [
      "|a + b| = |a - b|",
      "Dot product a · b = 0",
      "Angle θ = 90° (orthogonal)"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The dot rig binds the implied orthogonality constraint θ=90°. Vector magnitudes are not specified by the source and remain illustrative, so this is not an exact full-state mapping.",
    "teacherCheck": "Square both norms: equality cancels |a|² and |b|² and leaves 4a·b=0.",
    "takeaway": "Equal |a+b| and |a-b| is an orthogonality test for nonzero vectors.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": [
      "simParams.theta_deg"
    ]
  },
  {
    "id": "VEC-Q06",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 6th April Evening Shift",
    "subtab": 3,
    "subtabName": "Cross Product & Areas",
    "year": "2026",
    "q": "Let a = 2i + 3j + 3k and b = 6i + 3j + 3k. The square of the area of the triangle with adjacent sides determined by vectors (2a + 3b) and (a - b) is:",
    "options": [
      {
        "key": "A",
        "text": "225"
      },
      {
        "key": "B",
        "text": "450"
      },
      {
        "key": "C",
        "text": "900"
      },
      {
        "key": "D",
        "text": "1800"
      }
    ],
    "correct": "D",
    "formula": "Area = ½ |(2a + 3b) × (a - b)| = ⁵/₂ |a × b|",
    "steps": [
      "Let u = 2a + 3b and v = a - b.",
      "Expand cross product: u × v = -2(a × b) + 3(b × a) = -5(a × b).",
      "Area of triangle = ½ |u × v| = ⁵/₂ |a × b|.",
      "Compute a × b = 0i + 12j - 12k ⇒ |a × b| = √(144 + 144) = 12√2.",
      "Area of triangle = ⁵/₂ (12√2) = 30√2.",
      "Square of area = (30√2)² = 900 × 2 = 1800."
    ],
    "ans": "1800 (Option D)",
    "trap": "Cross product is anti-commutative: 3(b × a) = -3(a × b), so the coefficients add to -5, not +1!",
    "targetTab": "tab-cross",
    "simParams": {
      "ax": 2,
      "ay": 3,
      "az": 3,
      "bx": 6,
      "by": 3,
      "bz": 3
    },
    "simSummary": [
      "Vector a = 2i + 3j + 3k",
      "Vector b = 6i + 3j + 3k",
      "Cross product |a × b| = 12√2",
      "Area² = 1800"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The cross-product rig demonstrates triangle area and anti-commutativity but cannot bind the supplied 3D component vectors.",
    "teacherCheck": "Expand (2a+3b)×(a-b)=-5a×b and verify |a×b|=12√2; half its magnitude is 30√2.",
    "takeaway": "Expand cross products bilinearly before computing components; b×a=-a×b.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q07",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 7th April Shift",
    "subtab": 3,
    "subtabName": "Cross Product & Areas",
    "year": "2026",
    "q": "The diagonals of a parallelogram are given by vectors d₁ = 3i + j - 2k and d₂ = i - 3j + 4k. The area of the parallelogram is:",
    "options": [
      {
        "key": "A",
        "text": "5√3"
      },
      {
        "key": "B",
        "text": "10√3"
      },
      {
        "key": "C",
        "text": "5√5"
      },
      {
        "key": "D",
        "text": "20√3"
      }
    ],
    "correct": "A",
    "formula": "Area of Parallelogram with Diagonals = ½ |d₁ × d₂|",
    "steps": [
      "When diagonals are given, Area = ½ |d₁ × d₂|.",
      "Compute d₁ × d₂ = -2i - 14j - 10k.",
      "Magnitude: |d₁ × d₂| = √(4 + 196 + 100) = √300 = 10√3.",
      "Area = ½ (10√3) = 5√3."
    ],
    "ans": "5√3 (Option A)",
    "trap": "When diagonals are given, always multiply by ½! The formula Area = |a × b| applies ONLY when a and b are adjacent sides.",
    "targetTab": "tab-cross",
    "simParams": {
      "d1x": 3,
      "d1y": 1,
      "d1z": -2,
      "d2x": 1,
      "d2y": -3,
      "d2z": 4
    },
    "simSummary": [
      "Diagonal d₁ = 3i + j - 2k",
      "Diagonal d₂ = i - 3j + 4k",
      "|d₁ × d₂| = 10√3 ⇒ Area = 5√3"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The diagonal-area mode teaches the exact ½ factor, but the current rig cannot load d1 and d2 component vectors.",
    "teacherCheck": "Compute d1×d2=(-2,-14,-10), whose magnitude is 10√3; halve it to obtain 5√3.",
    "takeaway": "If the given vectors are diagonals rather than adjacent sides, parallelogram area is ½|d1×d2|.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q08",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Evening Shift",
    "subtab": 3,
    "subtabName": "Cross Product & Areas",
    "year": "2024",
    "q": "For any two vectors a and b, if |a| = 10, |b| = 2, and a · b = 12, then the magnitude of the cross product |a × b| is:",
    "options": [
      {
        "key": "A",
        "text": "16"
      },
      {
        "key": "B",
        "text": "8"
      },
      {
        "key": "C",
        "text": "12"
      },
      {
        "key": "D",
        "text": "10"
      }
    ],
    "correct": "A",
    "formula": "Lagrange's Identity: |a × b|² + (a · b)² = |a|² |b|²",
    "steps": [
      "Apply Lagrange's Identity: |a × b|² = |a|² |b|² - (a · b)².",
      "Substitute values: |a|² = 10² = 100, |b|² = 2² = 4.",
      "Product of squared norms: |a|² |b|² = 100 × 4 = 400.",
      "Squared dot product: (a · b)² = 12² = 144.",
      "|a × b|² = 400 - 144 = 256.",
      "Take square root: |a × b| = √256 = 16."
    ],
    "ans": "16 (Option A)",
    "trap": "Lagrange's Identity is instantaneous and avoids converting back and forth through trigonometric angles: |a×b|² + (a·b)² ≡ |a|²|b|²!",
    "targetTab": "tab-cross",
    "simParams": {
      "magA": 10,
      "magB": 2,
      "dotVal": 12
    },
    "simSummary": [
      "|a| = 10, |b| = 2",
      "a · b = 12",
      "Lagrange Identity: |a × b| = √256 = 16"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The cross rig exposes Lagrange's identity but cannot independently bind |a|=10, |b|=2 and a·b=12.",
    "teacherCheck": "Residual check: 16²+12²=256+144=400=(10²)(2²).",
    "takeaway": "Lagrange's identity is often the shortest route when norms and a dot product are given.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q09",
    "num": "JEE Main 2019",
    "source": "JEE Main 2019 (Online) 12th January Morning Shift",
    "subtab": 4,
    "subtabName": "Triple Products & Volume",
    "year": "2019",
    "q": "If the vectors μi + j + k, i + μj + k and i + j + μk are coplanar, then the sum of the distinct real values of μ is:",
    "options": [
      {
        "key": "A",
        "text": "-1"
      },
      {
        "key": "B",
        "text": "0"
      },
      {
        "key": "C",
        "text": "1"
      },
      {
        "key": "D",
        "text": "3"
      }
    ],
    "correct": "A",
    "formula": "Coplanarity ⇔ det([[μ,1,1],[1,μ,1],[1,1,μ]]) = 0 = (μ-1)²(μ+2)",
    "steps": [
      "Three vectors are coplanar exactly when their scalar triple product is zero.",
      "Form the determinant det([[μ,1,1],[1,μ,1],[1,1,μ]]).",
      "Expanding gives μ³ - 3μ + 2 = 0.",
      "Factor: μ³ - 3μ + 2 = (μ - 1)²(μ + 2).",
      "The distinct real values are μ = 1 and μ = -2.",
      "Their sum is 1 + (-2) = -1."
    ],
    "ans": "-1 (Option A)",
    "trap": "Zero scalar triple product means zero spanned volume/coplanarity; repeated roots still count once when the question asks for distinct real values.",
    "targetTab": "tab-triple",
    "simParams": {
      "mu_values": [
        1,
        -2
      ]
    },
    "simSummary": [
      "Coplanarity condition: scalar triple product = 0",
      "Distinct real roots: μ = 1 and μ = -2",
      "Sum = -1"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The triple-product rig visualizes coplanarity collapse, but it does not encode the symmetric μ-dependent vectors.",
    "teacherCheck": "Substitute each root into (μ-1)²(μ+2): μ=1 and μ=-2 both give zero determinant.",
    "takeaway": "Coplanarity is zero scalar triple product; distinguish distinct roots from algebraic multiplicity.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q10",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 1st February Evening Shift",
    "subtab": 4,
    "subtabName": "Triple Products & Volume",
    "year": "2024",
    "q": "The volume of the parallelepiped whose coterminous edges are represented by vectors a = 2i - 3j + 4k, b = i + 2j - k, and c = 3i - j + 2k is:",
    "options": [
      {
        "key": "A",
        "text": "7 cubic units"
      },
      {
        "key": "B",
        "text": "14 cubic units"
      },
      {
        "key": "C",
        "text": "21 cubic units"
      },
      {
        "key": "D",
        "text": "28 cubic units"
      }
    ],
    "correct": "A",
    "formula": "Volume V = | [a b c] | = | det(a, b, c) |",
    "steps": [
      "Set up determinant of coordinate matrix: det = 2(3) - (-3)(5) + 4(-7) = 6 + 15 - 28 = -7.",
      "Volume is absolute value: V = |-7| = 7 cubic units."
    ],
    "ans": "7 cubic units (Option A)",
    "trap": "Volume must be positive; always take the absolute value of the determinant!",
    "targetTab": "tab-triple",
    "simParams": {
      "ax": 2,
      "ay": -3,
      "az": 4,
      "bx": 1,
      "by": 2,
      "bz": -1,
      "cx": 3,
      "cy": -1,
      "cz": 2
    },
    "simSummary": [
      "Edges: a, b, c",
      "STP det = -7",
      "Volume = 7"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The volume rig demonstrates scalar-triple-product volume but uses a fixed illustrative parallelepiped, not the question's component vectors.",
    "teacherCheck": "Direct determinant check gives -7; geometric volume is its absolute value, 7.",
    "takeaway": "Scalar triple product carries orientation; physical volume uses its absolute value.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q11",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 5th April Morning Shift",
    "subtab": 5,
    "subtabName": "Vector Equations",
    "year": "2026",
    "q": "Let a = √7 i + j - k and b = j + 2k. If r is a vector such that r × a + a × b = 0 and r · a = 0, then the value of |3r|² is:",
    "options": [
      {
        "key": "A",
        "text": "44"
      },
      {
        "key": "B",
        "text": "54"
      },
      {
        "key": "C",
        "text": "86"
      },
      {
        "key": "D",
        "text": "132"
      }
    ],
    "correct": "A",
    "formula": "r × a + a × b = 0 ⇔ (r - b) × a = 0 ⇔ r - b = λ a ⇔ r = b + λ a",
    "steps": [
      "Rewrite r × a + a × b = 0 using a × b = -(b × a): (r - b) × a = 0.",
      "Therefore r - b is parallel to a, so r = b + λa.",
      "Use r · a = 0: (b + λa) · a = 0, hence λ = -(a · b)/|a|².",
      "Here |a|² = 7 + 1 + 1 = 9 and a · b = (1)(1) + (-1)(2) = -1, so λ = 1/9.",
      "Then |r|² = |b|² + 2λ(a · b) + λ²|a|² = 5 - 2/9 + 1/9 = 44/9.",
      "Therefore |3r|² = 9|r|² = 44."
    ],
    "ans": "44 (Option A)",
    "trap": "Never attempt to 'divide' by vector a! Factor (r - b) × a = 0 into collinear line r = b + λ a.",
    "targetTab": "tab-equations",
    "simParams": {
      "ax": 2.645,
      "ay": 1,
      "az": -1,
      "bx": 0,
      "by": 1,
      "bz": 2
    },
    "simSummary": [
      "Solution family before dot constraint: r = b + λa",
      "Auxiliary condition gives λ = 1/9",
      "|3r|² = 44"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The equation-solver rig currently uses a fixed illustrative a and particular solution; it does not load this question's a,b pair.",
    "teacherCheck": "Substitute λ=1/9 into r=b+λa and verify both residuals: (r-b)×a=0 and r·a=0; then |3r|²=44.",
    "takeaway": "A vector cross equation usually leaves a free component parallel to the crossed vector; an auxiliary constraint fixes it.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  },
  {
    "id": "VEC-Q12",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 29th January Evening Shift",
    "subtab": 5,
    "subtabName": "Vector Equations",
    "year": "2024",
    "q": "For any three vectors a, b, c, the vector triple product a × (b × c) is equal to (a · c) b - (a · b) c. If a × (b × c) = ½ b, where a, b, c are non-coplanar unit vectors, the angle between a and c is:",
    "options": [
      {
        "key": "A",
        "text": "30°"
      },
      {
        "key": "B",
        "text": "45°"
      },
      {
        "key": "C",
        "text": "60°"
      },
      {
        "key": "D",
        "text": "90°"
      }
    ],
    "correct": "C",
    "formula": "a × (b × c) = (a · c) b - (a · b) c = ½ b + 0 c",
    "steps": [
      "Apply BAC-CAB identity: a × (b × c) = (a · c) b - (a · b) c.",
      "Equating components along non-coplanar vectors b and c gives a · c = ½.",
      "Since a and c are unit vectors: cos θ = ½ ⇒ θ = 60°."
    ],
    "ans": "60° (Option C)",
    "trap": "Cross product is NOT associative: a × (b × c) lies in the plane of b and c, while (a × b) × c lies in the plane of a and b!",
    "targetTab": "tab-baccab",
    "simParams": {
      "theta_ac": 60
    },
    "simSummary": [
      "BAC-CAB rule: a × (b × c) = (a·c)b - (a·b)c",
      "a · c = 1/2 ⇒ θ = 60°",
      "a · b = 0 ⇒ orthogonal"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The VTP rig binds the required 60° a–c condition and demonstrates the BAC-CAB plane relation; the full source vector state is not reproduced.",
    "teacherCheck": "BAC-CAB gives coefficients along independent b and c: a·c=1/2 and a·b=0; unit vectors imply θac=60°.",
    "takeaway": "Cross product is non-associative; preserve parentheses before applying BAC-CAB.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": [
      "simParams.theta_ac"
    ]
  },
  {
    "id": "VEC-Q13",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 23rd January Morning Shift",
    "subtab": 6,
    "subtabName": "3D Spatial Geometry",
    "year": "2025",
    "q": "The shortest distance between the two skew lines r₁ = (i + 2j + 3k) + λ (2i + 3j + 4k) and r₂ = (2i + 4j + 5k) + μ (3i + 4j + 5k) is:",
    "options": [
      {
        "key": "A",
        "text": "1 / √6"
      },
      {
        "key": "B",
        "text": "2 / √6"
      },
      {
        "key": "C",
        "text": "1 / √3"
      },
      {
        "key": "D",
        "text": "0 (intersecting)"
      }
    ],
    "correct": "A",
    "formula": "d = | (a₂ - a₁) · (b₁ × b₂) | / | b₁ × b₂ |",
    "steps": [
      "a₂ - a₁ = i + 2j + 2k.",
      "b₁ × b₂ = -i + 2j - k ⇒ |b₁ × b₂| = √6.",
      "(a₂ - a₁) · (b₁ × b₂) = (1)(-1) + (2)(2) + (2)(-1) = 1.",
      "Shortest distance d = 1 / √6."
    ],
    "ans": "1 / √6 (Option A)",
    "trap": "Shortest distance between skew lines is the projection of the connector vector onto the common normal unit vector!",
    "targetTab": "tab-quiz",
    "simParams": {
      "dist": 0.408,
      "normal_mag": 2.449
    },
    "simSummary": [
      "Skew line 1: dir [2, 3, 4]",
      "Skew line 2: dir [3, 4, 5]",
      "Shortest distance d = 1/√6 ≈ 0.408"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "No current tab implements skew-line shortest distance; the stored target tab did not exist.",
    "teacherCheck": "Use n=b1×b2=(-1,2,-1), then project a2-a1=(1,2,2) onto n: |1|/√6.",
    "takeaway": "Shortest distance of skew lines is the connector's scalar projection on the common normal.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ],
    "simBindingRefs": []
  }
];
