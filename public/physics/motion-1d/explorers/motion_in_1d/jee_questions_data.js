/**
 * Motion in 1D Master Question Registry & Step-by-Step Solutions Database
 * 18 locally audited diagnostic records selected from the live ExamSIDE JEE Main Physics Motion in a Straight Line corpus.
 * Live source snapshot (2026-09-20): 123 questions, 2002-2026.
 * External question text is retained here only where already authored in this PR; source-corpus count is not a claim that all 123 questions are embedded locally.
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "1D-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 5th April Evening Shift",
    "subtab": 1,
    "subtabName": "Displacement & Distance",
    "year": "2026",
    "q": "The velocity-time graph of a particle moving along a straight line is shown. In the time interval 0 to 40 s, the velocity increases linearly from 0 to +20 m/s in 10 s, stays constant at 20 m/s for 10 s (to t=20s), decreases linearly to 0 at t=30s, and reaches -20 m/s at t=40s. Find the total distance travelled and the average velocity during this 40 s period.",
    "options": [
      {
        "key": "A",
        "text": "Distance = 400 m, |Average Velocity| = 5 m/s"
      },
      {
        "key": "B",
        "text": "Distance = 500 m, |Average Velocity| = 7.5 m/s"
      },
      {
        "key": "C",
        "text": "Distance = 400 m, |Average Velocity| = 7.5 m/s"
      },
      {
        "key": "D",
        "text": "Distance = 500 m, |Average Velocity| = 5 m/s"
      }
    ],
    "correct": "B",
    "formula": "Distance S = ∫|v|dt,  Displacement Δx = ∫v dt,  v_avg = Δx / Δt",
    "steps": [
      "Split the v-t graph wherever the velocity law changes and at the sign change.",
      "0–10 s: triangle area = ½(10)(20) = +100 m.",
      "10–20 s: rectangle area = (10)(20) = +200 m.",
      "20–30 s: triangle area = ½(10)(20) = +100 m.",
      "30–40 s: triangle lies below the time axis, so signed area = -½(10)(20) = -100 m.",
      "Total distance = 100 + 200 + 100 + 100 = 500 m.",
      "Net displacement = 100 + 200 + 100 - 100 = +300 m.",
      "Average velocity = displacement / total time = 300/40 = +7.5 m/s."
    ],
    "ans": "Distance = 500 m, |Average Velocity| = 7.5 m/s (Option B)",
    "trap": "Distance is the scalar path length ∫|v|dt; never subtract the negative area when calculating distance!",
    "targetTab": "tab-disp-dist",
    "simParams": {
      "v0": 20,
      "t_turn": 30,
      "t_total": 40,
      "a_reverse": -2
    },
    "simSummary": [
      "Question graph has four time segments and a velocity sign reversal",
      "Distance = 500 m",
      "Displacement = +300 m",
      "Average velocity = +7.5 m/s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The current constant-acceleration track cannot reproduce the question's four-segment v-t graph. It opens the distance/displacement reversal concept only.",
    "teacherCheck": "Recompute signed area and absolute area separately; the two agree only when v never changes sign.",
    "takeaway": "Whenever velocity crosses zero, split the interval before computing total distance.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q02",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 28th January Evening Shift",
    "subtab": 1,
    "subtabName": "Displacement & Distance",
    "year": "2026",
    "q": "A particle moves along the x-axis with position x(t) = 6t - t² (in meters). What is the total distance travelled by the particle between t = 0 and t = 5 s?",
    "options": [
      {
        "key": "A",
        "text": "5 m"
      },
      {
        "key": "B",
        "text": "9 m"
      },
      {
        "key": "C",
        "text": "13 m"
      },
      {
        "key": "D",
        "text": "25 m"
      }
    ],
    "correct": "C",
    "formula": "v(t) = dx/dt = 0 ⇒ t_turn; S = |x(t_turn) - x(0)| + |x(5) - x(t_turn)|",
    "steps": [
      "Differentiate position: v(t) = dx/dt = 6 - 2t.",
      "Identify turning point where v = 0: 6 - 2t = 0 ⇒ t_turn = 3 s.",
      "Evaluate position at key moments: x(0) = 0 m; x(3) = 6(3) - 3² = 18 - 9 = 9 m; x(5) = 6(5) - 5² = 30 - 25 = 5 m.",
      "Distance in forward segment (0 to 3 s): S₁ = |x(3) - x(0)| = |9 - 0| = 9 m.",
      "Distance in reverse segment (3 to 5 s): S₂ = |x(5) - x(3)| = |5 - 9| = 4 m.",
      "Total distance travelled S = S₁ + S₂ = 9 + 4 = 13 m.",
      "Net displacement is merely x(5) - x(0) = 5 m!"
    ],
    "ans": "13 m (Option C)",
    "trap": "Plugging t = 5 directly into x(t) yields displacement (5 m), completely ignoring the 4 m retraced backward!",
    "targetTab": "tab-disp-dist",
    "simParams": {
      "v0": 6,
      "a": -2,
      "t_stop": 5
    },
    "simSummary": [
      "Velocity law: v = 6 - 2t m/s",
      "Turning point: t = 3 s at x = +9 m",
      "Final position at t = 5 s: x = +5 m"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The track reproduces v(0)=6 m/s and a=-2 m/s²; the 0–5 s observation interval is not a governed control binding.",
    "teacherCheck": "Differentiate x(t): v=6-2t. At t=3 s, v=0 and x=9 m; x(5)=5 m, so distance is 9+4=13 m.",
    "takeaway": "For distance from x(t), find every turning time inside the interval before summing path segments.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q03",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 3rd April Evening Shift",
    "subtab": 1,
    "subtabName": "Displacement & Distance",
    "year": "2025",
    "q": "The position of a particle is given by x(t) = 4t³ - 18t² + 24t + 2 (in meters). Find the acceleration of the particle at the instant when its instantaneous velocity is zero for the second time.",
    "options": [
      {
        "key": "A",
        "text": "-12 m/s²"
      },
      {
        "key": "B",
        "text": "+12 m/s²"
      },
      {
        "key": "C",
        "text": "0 m/s²"
      },
      {
        "key": "D",
        "text": "+6 m/s²"
      }
    ],
    "correct": "B",
    "formula": "v(t) = dx/dt = 12t² - 36t + 24 = 0;  a(t) = dv/dt = 24t - 36",
    "steps": [
      "Velocity v(t) = dx/dt = 12t² - 36t + 24.",
      "Set v(t) = 0: 12(t² - 3t + 2) = 0 ⇒ 12(t - 1)(t - 2) = 0.",
      "The roots are t₁ = 1 s and t₂ = 2 s.",
      "The second turning point occurs at t = 2 s.",
      "Acceleration function a(t) = dv/dt = 24t - 36.",
      "Substitute t = 2 s: a(2) = 24(2) - 36 = 48 - 36 = +12 m/s²."
    ],
    "ans": "+12 m/s² (Option B)",
    "trap": "Never assume acceleration is zero at a turning point! At t = 2 s, v = 0 but acceleration is +12 m/s².",
    "targetTab": "tab-disp-dist",
    "simParams": {
      "v0": 24,
      "poly": "4t^3-18t^2+24t+2",
      "t_eval": 2
    },
    "simSummary": [
      "Cubic position x(t)",
      "Turning points at t = 1 s and t = 2 s",
      "Acceleration at 2nd turn: +12 m/s²"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The current track is constant-acceleration and cannot represent the cubic position law with time-varying acceleration.",
    "teacherCheck": "Differentiate twice and verify at the second zero of v: v=12(t-1)(t-2), a=24t-36, so a(2)=12 m/s².",
    "takeaway": "A turning point sets instantaneous velocity to zero; it does not force acceleration to zero.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q04",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 29th January Morning Shift",
    "subtab": 1,
    "subtabName": "Displacement & Distance",
    "year": "2024",
    "q": "A body travels the first half of a total distance D with speed v₁ = 30 km/h and the remaining half with speed v₂ = 60 km/h. Its average speed over the total journey is:",
    "options": [
      {
        "key": "A",
        "text": "45 km/h"
      },
      {
        "key": "B",
        "text": "40 km/h"
      },
      {
        "key": "C",
        "text": "42.5 km/h"
      },
      {
        "key": "D",
        "text": "48 km/h"
      }
    ],
    "correct": "B",
    "formula": "v_avg = Total Distance / Total Time = 2 v₁ v₂ / (v₁ + v₂)",
    "steps": [
      "Time for first half: t₁ = (D/2) / v₁ = D / (2v₁).",
      "Time for second half: t₂ = (D/2) / v₂ = D / (2v₂).",
      "Total time: T = t₁ + t₂ = (D/2) (1/v₁ + 1/v₂) = (D/2) ((v₁ + v₂) / (v₁ v₂)).",
      "Average speed: v_avg = D / T = 2 v₁ v₂ / (v₁ + v₂) (Harmonic Mean).",
      "Substitute values: v_avg = 2(30)(60) / (30 + 60) = 3600 / 90 = 40 km/h."
    ],
    "ans": "40 km/h (Option B)",
    "trap": "Average speed for equal distances is the HARMONIC mean, NOT the arithmetic mean (30+60)/2 = 45 km/h!",
    "targetTab": "tab-disp-dist",
    "simParams": {
      "v1": 30,
      "v2": 60,
      "dist": 100
    },
    "simSummary": [
      "Phase 1: speed = 30 km/h over D/2",
      "Phase 2: speed = 60 km/h over D/2",
      "Harmonic average speed = 40 km/h"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "No current rig models equal-distance two-speed average-speed timing, so loading parameters would be misleading.",
    "teacherCheck": "Use equal half-distances: total time is D/(2v1)+D/(2v2), giving the harmonic mean 2v1v2/(v1+v2).",
    "takeaway": "For equal distances, average speed is the harmonic mean, not the arithmetic mean.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q05",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 11th April Morning Shift",
    "subtab": 1,
    "subtabName": "Displacement & Distance",
    "year": "2023",
    "q": "A particle moves in a straight line such that its displacement x at time t is related by t = α x² + β x, where α and β are positive constants. The acceleration of the particle in terms of velocity v is:",
    "options": [
      {
        "key": "A",
        "text": "-2 α v²"
      },
      {
        "key": "B",
        "text": "-2 α v³"
      },
      {
        "key": "C",
        "text": "+2 α v³"
      },
      {
        "key": "D",
        "text": "-α v²"
      }
    ],
    "correct": "B",
    "formula": "dt/dx = 1/v = 2αx + β;  d/dx(1/v) = -v⁻² dv/dx;  a = v dv/dx",
    "steps": [
      "Differentiate t with respect to x: dt/dx = 2αx + β.",
      "Since v = dx/dt, we have 1/v = 2αx + β.",
      "Differentiate both sides with respect to x: -1/v² · (dv/dx) = 2α.",
      "Multiply both sides by -v²: dv/dx = -2α v².",
      "Acceleration a = v (dv/dx) = v (-2α v²) = -2α v³."
    ],
    "ans": "-2 α v³ (Option B)",
    "trap": "Chain rule execution: differentiating with respect to x gives dv/dx, then multiplying by v gives a = v(dv/dx) = -2α v³.",
    "targetTab": "tab-disp-dist",
    "simParams": {
      "alpha": 0.05,
      "beta": 0.2,
      "v0": 5
    },
    "simSummary": [
      "Time law: t = α x² + β x",
      "Velocity: v = (2αx + β)⁻¹",
      "Acceleration: a = -2α v³"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The current v-x rig demonstrates a=v dv/dx, but it does not represent t=αx²+βx or bind α, β.",
    "teacherCheck": "From 1/v=2αx+β, differentiate with respect to x: dv/dx=-2αv², then a=v dv/dx=-2αv³.",
    "takeaway": "When the law is given as t(x), invert through dt/dx=1/v before applying a=v dv/dx.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q06",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 24th January Evening Shift",
    "subtab": 2,
    "subtabName": "Kinematic Graphs",
    "year": "2026",
    "q": "The velocity-displacement (v-x) graph of a particle moving in a straight line is a straight line with negative slope: v(x) = -m x + v₀ (where m, v₀ > 0). The corresponding acceleration-displacement (a-x) graph is:",
    "options": [
      {
        "key": "A",
        "text": "A straight line with negative slope and negative intercept"
      },
      {
        "key": "B",
        "text": "A parabola opening upwards"
      },
      {
        "key": "C",
        "text": "A straight line with POSITIVE slope and negative intercept"
      },
      {
        "key": "D",
        "text": "A hyperbola in the fourth quadrant"
      }
    ],
    "correct": "C",
    "formula": "a = v (dv/dx) = (-mx + v₀)(-m) = m² x - m v₀",
    "steps": [
      "Given: v = -mx + v₀.",
      "Slope of v-x graph: dv/dx = -m (constant negative slope).",
      "Fundamental relation: a = v (dv/dx).",
      "Substitute: a(x) = (-mx + v₀) · (-m) = m² x - m v₀.",
      "Compare with standard line equation y = M x + C:",
      "Slope M = m² > 0 (strictly positive slope!).",
      "y-intercept C = -m v₀ < 0 (negative intercept).",
      "Hence, the a-x plot is a straight line with POSITIVE slope!"
    ],
    "ans": "A straight line with POSITIVE slope and negative intercept (Option C)",
    "trap": "Negative v-x slope produces a POSITIVE a-x slope because (-m) × (-m) = +m²!",
    "targetTab": "tab-graph-vx",
    "simParams": {
      "m": 1.5,
      "v0": 15,
      "x_max": 10,
      "profile": "linear_down"
    },
    "simSummary": [
      "v-x line: v = -1.5x + 15 m/s",
      "Slope dv/dx = -1.5 s⁻¹",
      "Resulting a-x: a = +2.25x - 22.5 m/s²"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "EXACT",
    "simFidelityNote": "The linear-down v-x profile with v0=15 m/s and x0=10 m gives m=v0/x0=1.5 and exactly reproduces a=m²x-mv0.",
    "teacherCheck": "Differentiate the loaded v(x): dv/dx=-1.5; multiplying by v(x) gives an a-x line with slope +(1.5)².",
    "takeaway": "The sign of dv/dx alone does not determine the slope of a(x); use a=v dv/dx.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q07",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 8th April Morning Shift",
    "subtab": 2,
    "subtabName": "Kinematic Graphs",
    "year": "2025",
    "q": "The v² versus x graph of a particle moving in a straight line is a straight line passing through (0, 100) and (25, 0) (where v is in m/s and x is in m). The magnitude of acceleration of the particle is:",
    "options": [
      {
        "key": "A",
        "text": "4 m/s²"
      },
      {
        "key": "B",
        "text": "2 m/s²"
      },
      {
        "key": "C",
        "text": "8 m/s²"
      },
      {
        "key": "D",
        "text": "1 m/s²"
      }
    ],
    "correct": "B",
    "formula": "v² = u² + 2ax ⇒ Slope of v²-x graph = 2a ⇒ a = ½ (Slope)",
    "steps": [
      "From the 3rd equation of kinematics: v² = u² + 2ax.",
      "This is of the linear form Y = M X + C, where Y = v², X = x, C = u², and Slope M = 2a.",
      "Calculate slope from given points: M = (0 - 100) / (25 - 0) = -100 / 25 = -4 m/s².",
      "Since Slope = 2a, we have 2a = -4 ⇒ a = -2 m/s².",
      "The magnitude of acceleration is |a| = 2 m/s²."
    ],
    "ans": "2 m/s² (Option B)",
    "trap": "Forgetting the factor of 2: the slope of v²-x is 2a, NOT a!",
    "targetTab": "tab-graph-vx",
    "simParams": {
      "u2": 100,
      "x_stop": 25,
      "a": -2,
      "v0": 10,
      "x_max": 25,
      "profile": "constant_accel"
    },
    "simSummary": [
      "Initial v² = 100 m²/s² (u = 10 m/s)",
      "Stopping distance = 25 m",
      "Slope = 2a = -4 ⇒ a = -2 m/s²"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "EXACT",
    "simFidelityNote": "The constant-acceleration v-x profile is loaded with v0=10 m/s and stopping position x0=25 m, exactly matching v²=100-4x.",
    "teacherCheck": "The v²-x slope is -4, so 2a=-4 and a=-2 m/s²; magnitude is 2 m/s².",
    "takeaway": "On a v²-x graph, slope equals 2a.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q08",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 31st January Evening Shift",
    "subtab": 2,
    "subtabName": "Kinematic Graphs",
    "year": "2024",
    "q": "The acceleration-time (a-t) graph of a particle starting from rest at t = 0 is a triangle with base from t = 0 to t = 8 s and peak acceleration a_max = 6 m/s² at t = 4 s. The maximum velocity reached by the particle is:",
    "options": [
      {
        "key": "A",
        "text": "48 m/s"
      },
      {
        "key": "B",
        "text": "24 m/s"
      },
      {
        "key": "C",
        "text": "12 m/s"
      },
      {
        "key": "D",
        "text": "36 m/s"
      }
    ],
    "correct": "B",
    "formula": "Δv = v_final - v_initial = Area under a-t graph",
    "steps": [
      "Initial velocity v(0) = 0 (starts from rest).",
      "Change in velocity Δv = ∫ a dt = Area under a-t graph.",
      "The graph is a single positive triangle with base b = 8 s and height h = 6 m/s².",
      "Area = ½ × base × height = ½ × 8 × 6 = 24 m/s.",
      "Since a ≥ 0 throughout, velocity increases monotonically and reaches its maximum at t = 8 s.",
      "v_max = v(0) + Δv = 0 + 24 = 24 m/s."
    ],
    "ans": "24 m/s (Option B)",
    "trap": "Do not stop integration at peak acceleration (t = 4 s); acceleration remains positive until t = 8 s, so velocity keeps rising!",
    "targetTab": "tab-graph-vx",
    "simParams": {
      "t_base": 8,
      "a_max": 6,
      "v_max": 24
    },
    "simSummary": [
      "Triangle a-t curve: base 8 s, height 6 m/s²",
      "Total Area = Δv = 24 m/s",
      "Peak velocity at t = 8 s: v = 24 m/s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "No current rig represents an arbitrary triangular a-t graph and its integrated velocity.",
    "teacherCheck": "Velocity change is the signed area under the a-t graph: ½(8)(6)=24 m/s.",
    "takeaway": "Velocity can keep increasing after acceleration has passed its maximum, as long as acceleration remains positive.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q09",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 25th January Morning Shift",
    "subtab": 2,
    "subtabName": "Kinematic Graphs",
    "year": "2023",
    "q": "A particle moves such that its acceleration a versus displacement x is given by a(x) = 3x² + 2x. If the particle starts from origin (x = 0) with initial velocity v = 2 m/s, its velocity when it reaches x = 2 m is:",
    "options": [
      {
        "key": "A",
        "text": "6 m/s"
      },
      {
        "key": "B",
        "text": "2√7 m/s"
      },
      {
        "key": "C",
        "text": "4√2 m/s"
      },
      {
        "key": "D",
        "text": "2√10 m/s"
      }
    ],
    "correct": "B",
    "formula": "∫ v dv = ∫ a(x) dx ⇒ ½(v² - u²) = Area under a-x curve",
    "steps": [
      "Use differential work-energy relation: a = v (dv/dx) ⇒ v dv = a(x) dx.",
      "Integrate both sides from x = 0 (v = 2) to x = 2 (v = v_f):",
      "∫₂^{v_f} v dv = ∫₀² (3x² + 2x) dx.",
      "LHS: ½ (v_f² - 2²) = ½ (v_f² - 4).",
      "RHS: [x³ + x²]₀² = (2³ + 2²) - 0 = 8 + 4 = 12.",
      "Equate: ½ (v_f² - 4) = 12 ⇒ v_f² - 4 = 24 ⇒ v_f² = 28.",
      "v_f = √28 = 2√7 m/s ≈ 5.29 m/s."
    ],
    "ans": "2√7 m/s (Option B)",
    "trap": "Area under a-x curve equals CHANGE IN KINETIC ENERGY PER UNIT MASS, ½(v² - u²), NOT simply v - u!",
    "targetTab": "tab-graph-vx",
    "simParams": {
      "u": 2,
      "x_target": 2,
      "integral_val": 12
    },
    "simSummary": [
      "Initial velocity u = 2 m/s at x = 0",
      "Area under a-x: ∫(3x²+2x)dx = 12 m²/s²",
      "Final velocity = √28 = 2√7 m/s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "The current v-x profiles do not represent the arbitrary law a(x)=3x²+2x.",
    "teacherCheck": "Integrate v dv=a(x)dx: ½(v²-4)=∫₀²(3x²+2x)dx=12, hence v²=28.",
    "takeaway": "Area under an a-x graph gives half the change in v², not the change in v.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q10",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 8th April Evening Shift",
    "subtab": 3,
    "subtabName": "Vertical & Balloons",
    "year": "2026",
    "q": "A gas balloon is going up with a constant velocity of 10 m/s. When this balloon reached a height of 75 m from the ground, a stone is dropped from it while the balloon continues rising with the same velocity. The height of the balloon when the stone hits the ground is: (Take g = 10 m/s²)",
    "options": [
      {
        "key": "A",
        "text": "100 m"
      },
      {
        "key": "B",
        "text": "125 m"
      },
      {
        "key": "C",
        "text": "150 m"
      },
      {
        "key": "D",
        "text": "110 m"
      }
    ],
    "correct": "B",
    "formula": "y_stone(t) = h + u t - ½ g t² = 0;  h_balloon(t) = h + u t",
    "steps": [
      "CRITICAL INHERITANCE: The dropped stone inherits the balloon's upward velocity: u_stone = +10 m/s.",
      "Equation of vertical motion for stone with origin at ground (upwards positive):",
      "y(t) = 75 + 10 t - ½(10) t² = 75 + 10 t - 5 t².",
      "When stone hits ground, y(t) = 0: 5 t² - 10 t - 75 = 0 ⇒ t² - 2 t - 15 = 0.",
      "Factor quadratic: (t - 5)(t + 3) = 0 ⇒ t = 5 s (since t > 0).",
      "During these 5 s, the balloon continues rising at steady 10 m/s:",
      "Height of balloon at t = 5 s: H = 75 + (10 m/s × 5 s) = 75 + 50 = 125 m."
    ],
    "ans": "125 m (Option B)",
    "trap": "Assuming dropped stone has u = 0 leads to t = √(2h/g) = √15 ≈ 3.87 s and completely incorrect balloon height!",
    "targetTab": "tab-balloon",
    "simParams": {
      "v_balloon": 10,
      "h_release": 75,
      "g": 10
    },
    "simSummary": [
      "Balloon upward velocity = 10 m/s",
      "Stone release height = 75 m",
      "Stone flight time = 5 s; Balloon height = 125 m"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "EXACT",
    "simFidelityNote": "Release height, inherited upward velocity and g map directly to the balloon rig.",
    "teacherCheck": "Substitute t=5 s into both trajectories: the stone reaches y=0 while the balloon reaches 125 m.",
    "takeaway": "At release, an object inherits the platform's instantaneous ground-frame velocity.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q11",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 28th January Morning Shift",
    "subtab": 3,
    "subtabName": "Vertical & Balloons",
    "year": "2026",
    "q": "Water drops fall from a tap on the floor 5 m below at regular time intervals. The first drop strikes the floor at the exact instant the sixth drop begins to fall. The height of the fourth drop from the ground at that instant is: (Take g = 10 m/s²)",
    "options": [
      {
        "key": "A",
        "text": "3.20 m"
      },
      {
        "key": "B",
        "text": "4.20 m"
      },
      {
        "key": "C",
        "text": "4.80 m"
      },
      {
        "key": "D",
        "text": "3.75 m"
      }
    ],
    "correct": "B",
    "formula": "s_n = ½ g (n Δt)²;  H_total = ½ g (N-1)² Δt²",
    "steps": [
      "Let the regular time interval between successive drops be Δt.",
      "When the 6th drop begins to fall, the 1st drop has already fallen for 5 intervals: T = 5Δt.",
      "For the 1st drop, 5 = ½(10)(5Δt)² = 125Δt², so Δt² = 0.04 and Δt = 0.20 s.",
      "At the same instant, the 4th drop has been falling for 2 intervals: t₄ = 2Δt = 0.40 s.",
      "Distance fallen by the 4th drop = ½(10)(0.40)² = 0.80 m.",
      "Height of the 4th drop above the floor = 5.00 - 0.80 = 4.20 m."
    ],
    "ans": "4.20 m (Option B)",
    "trap": "Careful with drop indexing! The 4th drop has experienced 2 intervals of fall, NOT 4 intervals. Also remember question asks for height FROM GROUND, not distance from tap!",
    "targetTab": "tab-drops",
    "simParams": {
      "total_h": 5,
      "num_drops": 6,
      "target_drop": 4,
      "g": 10
    },
    "simSummary": [
      "Tap height = 5.0 m",
      "6 drops in flight; time interval Δt = 0.2 s",
      "4th drop is at 4.20 m above floor"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "EXACT",
    "simFidelityNote": "Tap height and drop count map directly to the stroboscopic drop rig; the target is the fourth drop when the sixth is released.",
    "teacherCheck": "Check the clock indexing: first drop has 5 intervals, fourth has 2; Δt=0.2 s and the fourth is 4.2 m above the floor.",
    "takeaway": "For equally timed releases, index elapsed intervals from the release event before using s∝t².",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q12",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 4th April Morning Shift",
    "subtab": 3,
    "subtabName": "Vertical & Balloons",
    "year": "2025",
    "q": "A paratrooper after bailing out falls 50 m without friction. When the parachute opens, he decelerates downwards at 2 m/s². He reaches the ground with a speed of 3 m/s. At what height did he bail out? (Take g = 9.8 m/s²)",
    "options": [
      {
        "key": "A",
        "text": "293 m"
      },
      {
        "key": "B",
        "text": "111 m"
      },
      {
        "key": "C",
        "text": "243 m"
      },
      {
        "key": "D",
        "text": "300 m"
      }
    ],
    "correct": "A",
    "formula": "v₁² = 2 g h₁;  v₂² = v₁² - 2 a_brake h₂;  H = h₁ + h₂",
    "steps": [
      "Phase 1 (Free Fall): h₁ = 50 m, initial speed u = 0, acceleration g = 9.8 m/s².",
      "Velocity when chute opens: v₁² = u² + 2 g h₁ = 0 + 2(9.8)(50) = 980 (m/s)².",
      "Phase 2 (Decelerated Descent): Initial velocity v₁, landing velocity v₂ = 3 m/s, deceleration a = 2 m/s².",
      "Apply 3rd equation: v₂² = v₁² - 2 a h₂ ⇒ 3² = 980 - 2(2) h₂.",
      "9 = 980 - 4 h₂ ⇒ 4 h₂ = 971 ⇒ h₂ = 242.75 m.",
      "Total bail-out height H = h₁ + h₂ = 50 + 242.75 = 292.75 m ≈ 293 m."
    ],
    "ans": "293 m (Option A)",
    "trap": "The terminal speed of Phase 1 is the INITIAL speed of Phase 2. Piecewise boundary matching is mandatory!",
    "targetTab": "tab-braking",
    "simParams": {
      "h1": 50,
      "g": 9.8,
      "a_brake": 2,
      "v_land": 3
    },
    "simSummary": [
      "Free fall drop: h₁ = 50 m",
      "Parachute deceleration: a = 2.0 m/s²",
      "Total bail out height: H ≈ 293 m"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "EXACT",
    "simFidelityNote": "Free-fall distance, parachute deceleration and landing speed map directly to the two-phase braking rig.",
    "teacherCheck": "State continuity check: v1²=2gh1=980; the same v1 enters phase 2, giving h2=242.75 m and H=292.75 m.",
    "takeaway": "At a phase boundary, terminal position and velocity become the next phase's initial state.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q13",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 1st February Morning Shift",
    "subtab": 3,
    "subtabName": "Vertical & Balloons",
    "year": "2024",
    "q": "A ball is thrown vertically upwards from the top of a tower of height h with velocity u. It reaches the ground in time t₁. If it is thrown vertically downwards from the same spot with the same speed u, it reaches the ground in time t₂. If it is simply dropped from rest, the time t₃ taken to reach the ground is:",
    "options": [
      {
        "key": "A",
        "text": "t₃ = (t₁ + t₂) / 2"
      },
      {
        "key": "B",
        "text": "t₃ = √(t₁ t₂)"
      },
      {
        "key": "C",
        "text": "t₃ = 2 t₁ t₂ / (t₁ + t₂)"
      },
      {
        "key": "D",
        "text": "t₃ = √(t₁² + t₂²)"
      }
    ],
    "correct": "B",
    "formula": "-h = u t₁ - ½ g t₁²;  -h = -u t₂ - ½ g t₂²;  h = ½ g t₃²",
    "steps": [
      "Case 1 (Thrown Up): -h = u t₁ - ½ g t₁² ⇒ ½ g t₁² - u t₁ - h = 0.",
      "Case 2 (Thrown Down): -h = -u t₂ - ½ g t₂² ⇒ ½ g t₂² + u t₂ - h = 0.",
      "Eliminating u between the two quadratic roots yields: h = ½ g (t₁ t₂).",
      "For free drop from rest: h = ½ g t₃².",
      "Equating gives t₃² = t₁ t₂ ⇒ t₃ = √(t₁ t₂)."
    ],
    "ans": "t₃ = √(t₁ t₂) (Option B)",
    "trap": "This beautiful invariant shows the geometric mean relationship: t₃ is neither the arithmetic mean nor root-mean-square!",
    "targetTab": "tab-balloon",
    "simParams": {
      "h": 80,
      "u": 20,
      "g": 10
    },
    "simSummary": [
      "Tower height h = 80 m, launch speed u = 20 m/s",
      "Upward t₁ = 6 s, Downward t₂ = 2 s",
      "Free drop t₃ = √(6 × 2) = √12 ≈ 3.46 s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The balloon rig illustrates inherited vertical launch velocity but does not simultaneously model upward throw, downward throw and free drop from a tower.",
    "teacherCheck": "Eliminate u between the upward/downward equations to obtain h=½gt1t2; compare with h=½gt3².",
    "takeaway": "When two launch cases differ only by ±u, eliminate u before solving each trajectory separately.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q14",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 22nd January Morning Shift",
    "subtab": 4,
    "subtabName": "Calculus & Drag",
    "year": "2026",
    "q": "The deceleration experienced by a moving motor boat after its engine is cut off is given by dv/dt = -k v³, where k is a positive constant. If v₀ is the speed when the engine is cut off, the speed v after traversing a distance s is:",
    "options": [
      {
        "key": "A",
        "text": "v = v₀ e^{-ks}"
      },
      {
        "key": "B",
        "text": "v = v₀ / (1 + k s v₀)"
      },
      {
        "key": "C",
        "text": "v = v₀ / √(1 + 2 k s v₀²)"
      },
      {
        "key": "D",
        "text": "v = v₀ - k s"
      }
    ],
    "correct": "B",
    "formula": "a = v (dv/ds) = -k v³ ⇒ dv/ds = -k v²",
    "steps": [
      "Given dv/dt = -k v³.",
      "Transform time derivative to spatial derivative: dv/dt = v (dv/ds).",
      "Equate: v (dv/ds) = -k v³ ⇒ dv/ds = -k v².",
      "Separate variables: v⁻² dv = -k ds.",
      "Integrate from s = 0 (v = v₀) to s (v = v): [-1/v]_{v₀}^v = -k s ⇒ 1/v - 1/v₀ = k s.",
      "1/v = (1 + k s v₀) / v₀ ⇒ v = v₀ / (1 + k s v₀)."
    ],
    "ans": "v = v₀ / (1 + k s v₀) (Option B)",
    "trap": "dv/dt = -k v³ does NOT mean dv/ds = -k v³! Always apply the spatial chain rule a = v(dv/ds).",
    "targetTab": "tab-braking",
    "simParams": {
      "v0": 10,
      "k": 0.05,
      "s_max": 20
    },
    "simSummary": [
      "Cubic time drag: dv/dt = -k v³",
      "Spatial law: dv/ds = -k v²",
      "Velocity decay: v(s) = v₀ / (1 + k s v₀)"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "The paratrooper braking rig uses constant deceleration; it does not implement dv/dt=-kv³.",
    "teacherCheck": "Apply dv/dt=v dv/ds, then integrate dv/ds=-kv² to obtain 1/v-1/v0=ks.",
    "takeaway": "For velocity-dependent drag, do not substitute constant-acceleration formulas.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q15",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 29th January Evening Shift",
    "subtab": 4,
    "subtabName": "Calculus & Drag",
    "year": "2025",
    "q": "A particle moves in a resistive medium with acceleration a = -β v, where β is a constant and v is instantaneous velocity. If the initial velocity is v₀ at x = 0, the maximum distance the particle can penetrate before coming to rest is:",
    "options": [
      {
        "key": "A",
        "text": "v₀ / β"
      },
      {
        "key": "B",
        "text": "v₀² / (2β)"
      },
      {
        "key": "C",
        "text": "Infinity"
      },
      {
        "key": "D",
        "text": "2 v₀ / β"
      }
    ],
    "correct": "A",
    "formula": "a = v (dv/dx) = -β v ⇒ dv/dx = -β ⇒ Δv = -β x_max",
    "steps": [
      "Express acceleration spatially: a = v (dv/dx).",
      "Given a = -β v ⇒ v (dv/dx) = -β v ⇒ dv/dx = -β.",
      "Integrate from x = 0 (v = v₀) to x_max (v = 0):",
      "∫_{v₀}^0 dv = -β ∫₀^{x_max} dx ⇒ (0 - v₀) = -β x_max ⇒ x_max = v₀ / β."
    ],
    "ans": "v₀ / β (Option A)",
    "trap": "Even though it takes infinite time for velocity to asymptotically reach zero (v(t) = v₀ e^{-β t}), the total spatial penetration is strictly FINITE: x_max = v₀ / β!",
    "targetTab": "tab-braking",
    "simParams": {
      "v0": 12,
      "beta": 0.5,
      "x_max": 24
    },
    "simSummary": [
      "Linear velocity drag: a = -β v",
      "Infinite time horizon but finite distance",
      "Stopping limit: x_max = v₀ / β = 24 m"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "The paratrooper rig does not implement the velocity-dependent law a=-βv.",
    "teacherCheck": "Use v dv/dx=-βv, cancel v away from the limiting endpoint, and integrate dv/dx=-β to get xmax=v0/β.",
    "takeaway": "Infinite stopping time can coexist with a finite stopping distance.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q16",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 4th April Evening Shift",
    "subtab": 5,
    "subtabName": "1D Relative Motion",
    "year": "2026",
    "q": "Two cars A and B travel in the same direction along a straight highway. Car A moves at constant speed v_A = 20 m/s. Car B is initially 100 m ahead of Car A and moves at constant speed v_B = 10 m/s. At t = 0, Car B begins to brake with constant deceleration a_B = 1 m/s². Find the time when Car A overtakes Car B.",
    "options": [
      {
        "key": "A",
        "text": "6.67 s"
      },
      {
        "key": "B",
        "text": "8.00 s"
      },
      {
        "key": "C",
        "text": "10.0 s"
      },
      {
        "key": "D",
        "text": "7.32 s"
      }
    ],
    "correct": "D",
    "formula": "x_{B/A}(t) = x_{B/A}(0) + v_{rel} t + ½ a_{rel} t² = 0",
    "steps": [
      "Set up relative coordinate frame with Car A as reference origin:",
      "Initial relative position: x_{rel}(0) = x_B(0) - x_A(0) = +100 m.",
      "Initial relative velocity: v_{rel} = v_B - v_A = 10 - 20 = -10 m/s.",
      "Relative acceleration: a_{rel} = a_B - a_A = (-1) - 0 = -1 m/s².",
      "Relative position equation: x_{rel}(t) = 100 - 10 t - 0.5 t² = 0.",
      "Multiply by 2: t² + 20 t - 200 = 0 ⇒ t = [-20 + √(400 + 800)] / 2 = -10 + 10√3 ≈ 7.32 s.",
      "Check if B stopped: t_stop = 10 / 1 = 10 s > 7.32 s. Overtaking occurs while B is still moving!"
    ],
    "ans": "7.32 s (Option D)",
    "trap": "Always verify whether the braking vehicle stops before overtaking happens; here 7.32 s < 10 s, so the motion is valid throughout.",
    "targetTab": "tab-relative",
    "simParams": {
      "vA": 20,
      "vB": 10,
      "d0": 100,
      "aB": -1
    },
    "simSummary": [
      "Car A: 20 m/s steady",
      "Car B: 10 m/s decelerating at 1 m/s² from 100 m ahead",
      "Overtaking at t ≈ 7.32 s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_ITEM_VERIFIED",
    "simFidelity": "EXACT",
    "simFidelityNote": "vA, vB, initial gap and B's deceleration map directly to the relative-pursuit rig.",
    "teacherCheck": "Solve 100-10t-½t²=0 and independently check t=7.32 s is before B's 10 s stopping time.",
    "takeaway": "After solving a relative-motion event, verify that every body's assumed motion law is still valid at that event time.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q17",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Morning Shift",
    "subtab": 5,
    "subtabName": "1D Relative Motion",
    "year": "2024",
    "q": "Two trains A and B, each of length 150 m, are moving in opposite directions on parallel tracks with speeds 72 km/h and 36 km/h respectively. The time of complete crossing is:",
    "options": [
      {
        "key": "A",
        "text": "10 s"
      },
      {
        "key": "B",
        "text": "15 s"
      },
      {
        "key": "C",
        "text": "20 s"
      },
      {
        "key": "D",
        "text": "30 s"
      }
    ],
    "correct": "A",
    "formula": "t_cross = (L_A + L_B) / v_{rel}",
    "steps": [
      "Convert speeds to SI units: v_A = 72 × (5/18) = 20 m/s, v_B = 36 × (5/18) = 10 m/s.",
      "Opposite directions add relative speed: v_{rel} = v_A + v_B = 20 + 10 = 30 m/s.",
      "Total distance to clear: D = L_A + L_B = 150 + 150 = 300 m.",
      "Crossing time: t = D / v_{rel} = 300 / 30 = 10 s."
    ],
    "ans": "10 s (Option A)",
    "trap": "Opposite directions ADD relative velocities (20 + 10 = 30 m/s), rather than subtracting them!",
    "targetTab": "tab-relative",
    "simParams": {
      "vA": 20,
      "vB": -10,
      "LA": 150,
      "LB": 150
    },
    "simSummary": [
      "Train A: 20 m/s east, length 150 m",
      "Train B: 10 m/s west, length 150 m",
      "Relative speed = 30 m/s, crossing time = 10 s"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "UNAVAILABLE",
    "simFidelityNote": "The current pursuit rig models point vehicles and does not include train lengths or complete-crossing geometry.",
    "teacherCheck": "Convert to SI, add speeds for opposite directions, and divide the sum of train lengths by relative speed.",
    "takeaway": "For complete crossing, the relative distance is the sum of the object lengths, not the initial gap alone.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "1D-Q18",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 30th January Evening Shift",
    "subtab": 5,
    "subtabName": "1D Relative Motion",
    "year": "2023",
    "q": "Two trains travelling on the same track are approaching each other with speeds of 40 m/s and 20 m/s respectively. When they are 1.2 km apart, both drivers simultaneously apply brakes which produce equal decelerations of 1 m/s² in each train. The collision:",
    "options": [
      {
        "key": "A",
        "text": "Will be averted, stopping with a gap of 200 m"
      },
      {
        "key": "B",
        "text": "Will occur with relative speed 10 m/s"
      },
      {
        "key": "C",
        "text": "Will be averted, stopping with a gap of 100 m"
      },
      {
        "key": "D",
        "text": "Will occur exactly when both reach zero velocity"
      }
    ],
    "correct": "A",
    "formula": "s₁ = u₁² / (2a₁),  s₂ = u₂² / (2a₂);  s_total = s₁ + s₂ < D_initial",
    "steps": [
      "Calculate stopping distance of Train 1: s₁ = u₁² / (2a) = 40² / (2 × 1) = 1600 / 2 = 800 m.",
      "Calculate stopping distance of Train 2: s₂ = u₂² / (2a) = 20² / (2 × 1) = 400 / 2 = 200 m.",
      "Total stopping distance: s_total = s₁ + s₂ = 800 + 200 = 1000 m = 1.0 km.",
      "Initial separation: D = 1.2 km = 1200 m.",
      "Since s_total (1000 m) < D (1200 m), the collision is completely averted!",
      "Remaining gap between stopped trains: Gap = 1200 - 1000 = 200 m."
    ],
    "ans": "Will be averted, stopping with a gap of 200 m (Option A)",
    "trap": "Do not treat both trains as one combined deceleration if they stop at different times (Train 2 stops in 20 s, Train 1 stops in 40 s)! Calculate individual stopping distances.",
    "targetTab": "tab-relative",
    "simParams": {
      "vA": 40,
      "vB": -20,
      "d0": 1200,
      "aA": -1,
      "aB": 1
    },
    "simSummary": [
      "Train 1: 40 m/s, s₁ = 800 m",
      "Train 2: 20 m/s, s₂ = 200 m",
      "Gap = 1200 - 1000 = 200 m (collision averted)"
    ],
    "answerAudit": "PASS",
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The current pursuit rig can show separation and one braking vehicle, but it cannot bind both trains' independent braking laws exactly.",
    "teacherCheck": "Individual stopping distances are 800 m and 200 m; their sum is 1000 m, leaving a 200 m gap from 1200 m.",
    "takeaway": "When bodies stop at different times, compare their individual stopping distances instead of inventing one common deceleration.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  }
];
