/**
 * Master Question Registry & Step-by-Step Solutions Database
 * Total: 104 Questions (11 Scanned PDF Illustrations + 93 ExamSide PYQs)
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "PDF-01",
    "num": "PDF Illus 1",
    "source": "Scanned PDF Page 3",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "PDF Page 3",
    "q": "A body is projected with a velocity of 12 m/s at an angle of 45° with the horizontal. Find its horizontal range. (Take g = 10 m/s²)",
    "formula": "R = (u² sin 2θ) / g",
    "steps": [
      "Launch velocity u = 12 m/s, launch angle θ = 45°, g = 10 m/s².",
      "Compute 2θ = 90° &rArr; sin(90°) = 1.0 (condition for maximum range).",
      "Substitute into formula: R = (12² &times; 1) / 10 = 144 / 10 = 14.4 m."
    ],
    "ans": "14.4 m",
    "takeaway": "Maximum range occurs at θ = 45° where sin 2θ = 1, giving R_max = u²/g.",
    "tab": "topic5"
  },
  {
    "id": "PDF-02",
    "num": "PDF Illus 2",
    "source": "Scanned PDF Page 4",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "PDF Page 4",
    "q": "At what angle of projection with the horizontal will the horizontal range of a projectile be equal to its maximum height?",
    "formula": "R tan θ = 4H  (The 4H Identity)",
    "steps": [
      "Use the universal relation between range and apex height: R tan θ = 4H.",
      "Apply problem condition R = H: H tan θ = 4H &rArr; tan θ = 4.",
      "Solve for angle: θ = arctan(4) ≈ 75.96° ≈ 76°."
    ],
    "ans": "θ = arctan(4) ≈ 76°",
    "takeaway": "The identity R tan θ = 4H holds universally for any ground-to-ground projectile.",
    "tab": "topic3"
  },
  {
    "id": "PDF-03",
    "num": "PDF Illus 3",
    "source": "Scanned PDF Page 4",
    "bucket": 4,
    "bucketName": "Complementary Symmetries",
    "year": "PDF Page 4",
    "q": "A shore defense gun fires at a pirate ship anchored at R = 560 m with muzzle speed v₀ = 82 m/s. Find: (a) The two projection angles to hit the ship, (b) The time of flight in each case. (Take g = 9.8 m/s²)",
    "formula": "sin 2θ = (g R) / v₀²,  T = (2v₀ sin θ) / g",
    "steps": [
      "Calculate sin 2θ = (9.8 &times; 560) / 82² = 5488 / 6724 ≈ 0.8162.",
      "First solution: 2θ₁ = arcsin(0.8162) ≈ 54.7° &rArr; θ₁ ≈ 27.4° (low flat trajectory).",
      "Second solution: 2θ₂ = 180° - 54.7° = 125.3° &rArr; θ₂ ≈ 62.6° (high lob trajectory).",
      "Time of flight T₁ = (2 &times; 82 &times; sin 27.4°) / 9.8 ≈ 7.69 s.",
      "Time of flight T₂ = (2 &times; 82 &times; sin 62.6°) / 9.8 ≈ 14.86 s ≈ 15 s.",
      "Invariant Check: T₁ &times; T₂ = 7.69 &times; 14.86 = 114.3 s² = 2R/g = 2(560)/9.8 = 114.3 s²."
    ],
    "ans": "θ₁ ≈ 27.4°, θ₂ ≈ 62.6°; T₁ ≈ 7.7 s, T₂ ≈ 14.9 s",
    "takeaway": "Complementary angles θ and 90°-θ hit the exact same target with product of times T₁T₂ = 2R/g.",
    "tab": "topic5"
  },
  {
    "id": "PDF-04",
    "num": "PDF Illus 4",
    "source": "Scanned PDF Page 5",
    "bucket": 6,
    "bucketName": "Dynamic Tracking & Interception",
    "year": "PDF Page 5",
    "q": "An outfielder tracks a fly ball hit with u = 40 m/s at θ = 35°. The line-of-sight elevation angle is φ(t) with tan φ(t) = y(t) / (D - x(t)). Analyze the optical curvature d²φ/dt².",
    "formula": "tan φ(t) = (u_y t - ½ g t²) / (D - u_x t)",
    "steps": [
      "If the fielder runs at speed v_f to catch the ball at landing, D(t) - x(t) = (u_x - v_f)(T - t).",
      "Substitute vertical position y(t) = ½ g t (T - t): tan φ(t) = [½ g t (T - t)] / [(u_x - v_f)(T - t)] = (g t) / [2(u_x - v_f)].",
      "This implies φ(t) rises linearly with time: d²φ/dt² ≈ 0 (the optical signature of an interception course!).",
      "If d²φ/dt² > 0 (convex up, accelerating angular rise): ball will sail OVER the fielder (must retreat).",
      "If d²φ/dt² < 0 (concave down, plateauing angle): ball will land IN FRONT of fielder (must sprint forward)."
    ],
    "ans": "Linear elevation d²φ/dt² = 0 confirms catch; > 0 retreat; < 0 charge forward.",
    "takeaway": "Outfielders judge parabolic trajectories purely by holding line-of-sight angular acceleration to zero.",
    "tab": "topic6"
  },
  {
    "id": "PDF-05",
    "num": "PDF Illus 5",
    "source": "Scanned PDF Pages 5–6",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "PDF Pages 5–6",
    "q": "A stone is thrown horizontally from a cliff h = 490 m high with speed u = 98 m/s. Find: (a) time to hit ground, (b) horizontal distance from cliff base, (c) striking velocity. (Take g = 9.8 m/s²)",
    "formula": "t = √(2h/g),  R = u t,  v = √(u² + 2gh),  tan β = gt / u",
    "steps": [
      "Time to ground depends solely on vertical drop: t = √(2 &times; 490 / 9.8) = √100 = 10 s.",
      "Horizontal distance: R = u &times; t = 98 &times; 10 = 980 m.",
      "Velocity components at impact: v_x = 98 m/s (unchanged), v_y = gt = 9.8 &times; 10 = 98 m/s.",
      "Total speed: v = √(98² + 98²) = 98√2 m/s ≈ 138.6 m/s.",
      "Direction: tan β = v_y / v_x = 98 / 98 = 1 &rArr; β = 45° below horizontal."
    ],
    "ans": "t = 10 s, R = 980 m, v = 98√2 m/s at 45° below horizontal",
    "takeaway": "Horizontal launch has zero initial vertical velocity (u_y = 0); vertical motion is identical to free fall.",
    "tab": "topic6"
  },
  {
    "id": "PDF-09",
    "num": "PDF Illus 9",
    "source": "Scanned PDF Page 6",
    "bucket": 7,
    "bucketName": "Relative Velocity & Frames",
    "year": "PDF Page 6",
    "q": "Car A moves east at 1 m/s, Car B moves west at 2 m/s along a straight road. Find the relative velocity of Car B with respect to Car A.",
    "formula": "v_B/A = v_B - v_A",
    "steps": [
      "Assign coordinate direction: East = +î, West = -î.",
      "Velocity vectors: v_A = +1 î m/s, v_B = -2 î m/s.",
      "Relative velocity formula: v_B/A = (-2 î) - (+1 î) = -3 î m/s.",
      "Magnitude is 3 m/s directed westward (rate of mutual approach)."
    ],
    "ans": "-3 î m/s (3 m/s towards West)",
    "takeaway": "When two bodies move towards each other, their relative approach speed is the sum of their individual speeds.",
    "tab": "relative"
  },
  {
    "id": "PDF-10",
    "num": "PDF Illus 10",
    "source": "Scanned PDF Page 7",
    "bucket": 9,
    "bucketName": "Rain-Man & Dual-Speed",
    "year": "PDF Page 7",
    "q": "Rain falls vertically at 15 m/s. A cyclist moves horizontally at 5√3 m/s. In which direction should the cyclist hold his umbrella to protect himself?",
    "formula": "v_r/c = v_r - v_c,  tan θ = v_c / v_r",
    "steps": [
      "Rain velocity: v_r = -15 ĵ m/s. Cyclist velocity: v_c = 5√3 î m/s.",
      "Relative velocity of rain: v_r/c = v_r - v_c = -5√3 î - 15 ĵ m/s.",
      "Tilt angle with vertical: tan θ = |v_cx| / |v_ry| = (5√3) / 15 = 1/√3.",
      "Solve for angle: θ = arctan(1/√3) = 30° forward."
    ],
    "ans": "30° forward with the vertical",
    "takeaway": "Because the runner moves forward, the apparent rain vector slants backward by tan θ = v_m / v_r.",
    "tab": "relative"
  },
  {
    "id": "PDF-11",
    "num": "PDF Illus 11",
    "source": "Scanned PDF Pages 7–8",
    "bucket": 7,
    "bucketName": "Relative Velocity & Frames",
    "year": "PDF Pages 7–8",
    "q": "A car travels East at 80 km/h. To a passenger in the car, a train appears to move due North at 80√3 km/h. Find the actual velocity of the train.",
    "formula": "v_train = v_train/car + v_car",
    "steps": [
      "Car velocity: v_car = 80 î km/h. Apparent train velocity: v_t/c = 80√3 ĵ km/h.",
      "Reconstruct true train velocity: v_t = v_t/c + v_car = 80 î + 80√3 ĵ km/h.",
      "Magnitude: v_t = √(80² + (80√3)²) = √(6400 + 19200) = √25600 = 160 km/h.",
      "Direction: tan θ = (80√3) / 80 = √3 &rArr; θ = 60° North of East."
    ],
    "ans": "160 km/h at 60° North of East",
    "takeaway": "Frame reconstruction inverts relative observation: v_true = v_apparent + v_observer.",
    "tab": "relative"
  },
  {
    "id": "PDF-12",
    "num": "PDF Illus 12",
    "source": "Scanned PDF Pages 9–10",
    "bucket": 8,
    "bucketName": "River-Boat & Navigation",
    "year": "PDF Pages 9–10",
    "q": "An airplane wishes to fly towards 45° North of East. Wind blows from West at 40 km/h. Airspeed is 200 km/h. Find steering heading using the Sine Rule.",
    "formula": "(sin θ') / v_wind = (sin 45°) / v_air",
    "steps": [
      "Vector relation: v_ground = v_plane/air + v_wind.",
      "In the vector triangle, angle between wind vector (East) and desired ground track (45° N of E) is 45°.",
      "Apply Sine Rule: (sin θ') / 40 = (sin 45°) / 200.",
      "Solve: sin θ' = (40 &times; 1/√2) / 200 = 1 / (5√2) ≈ 0.1414 &rArr; θ' ≈ 8.13°.",
      "Compensated heading: 45° - 8.13° = 36.87° North of East."
    ],
    "ans": "36.87° North of East (steer 8.13° into the wind)",
    "takeaway": "Wind drift is compensated by steering into the wind according to the Sine Rule of the velocity triangle.",
    "tab": "relative"
  },
  {
    "id": "PDF-13",
    "num": "PDF Illus 13",
    "source": "Scanned PDF Page 10",
    "bucket": 7,
    "bucketName": "Relative Velocity & Frames",
    "year": "PDF Page 10",
    "q": "A river flows East at 2 m/s. A boat motors upstream (West) at 5 m/s in water. A person walks towards the stern (East) at 3 m/s on the boat. Find person's velocity w.r.t ground.",
    "formula": "v_p/g = v_p/b + v_b/w + v_w/g  (Three-Body Chaining)",
    "steps": [
      "Define East as +î. River flow w.r.t ground: v_w/g = +2 î m/s.",
      "Boat w.r.t water: v_b/w = -5 î m/s (upstream).",
      "Person w.r.t boat: v_p/b = +3 î m/s (towards stern, i.e., East).",
      "Chain reference frames: v_p/g = (+3 î) + (-5 î) + (+2 î) = (3 - 5 + 2) î = 0 î m/s."
    ],
    "ans": "0 m/s (Stationary w.r.t riverbank!)",
    "takeaway": "Multi-tier Galilean relative frames add algebraically: three non-zero velocities cancel to produce zero ground speed.",
    "tab": "relative"
  },
  {
    "id": "PDF-14",
    "num": "PDF Illus 14",
    "source": "Scanned PDF Pages 10–11",
    "bucket": 9,
    "bucketName": "Rain-Man & Dual-Speed",
    "year": "PDF Pages 10–11",
    "q": "A man walking at 3 km/h observes rain falling vertically. At 6 km/h, rain appears at 45° to vertical. Find the actual velocity of the rain.",
    "formula": "v_r = v_rx î - v_ry ĵ,  v_r/m = (v_rx - v_m) î - v_ry ĵ",
    "steps": [
      "At v_m1 = 3 î km/h: rain appears vertical &rArr; apparent horizontal component is zero &rArr; v_rx - 3 = 0 &rArr; v_rx = 3 km/h.",
      "At v_m2 = 6 î km/h: relative horizontal velocity is 6 - 3 = 3 km/h backward.",
      "Given apparent angle is 45° with vertical: tan 45° = |v_rx - 6| / v_ry = 3 / v_ry = 1 &rArr; v_ry = 3 km/h.",
      "True rain velocity: v_r = 3 î - 3 ĵ km/h.",
      "Magnitude: |v_r| = √(3² + 3²) = 3√2 km/h ≈ 4.24 km/h.",
      "Direction: tan θ = 3 / 3 = 1 &rArr; θ = 45° with vertical (falling forward at 45°)."
    ],
    "ans": "3√2 km/h at 45° with vertical (falling towards East)",
    "takeaway": "When rain appears vertical, the runner's speed exactly equals the rain's horizontal velocity.",
    "tab": "relative"
  },
  {
    "id": "EXAM-01",
    "num": "JEE Q1",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2026 (Online) 8th April Evening Shift",
    "q": "Two identical bodies, projected with the same speed at two different angles cover the same horizontal range R . If the time of flight of these bodies are 5 s and 10 s , respectively, then the value of R is ____ m. (Take g=10m/s2 )",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-02",
    "num": "JEE Q2",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2026 (Online) 4th April Evening Shift",
    "q": "At t=0 , a body of mass 100 g starts moving under the influence of a force (5iˆ+10jˆ)N⋅ After 2 s its position is (2xiˆ+5yjˆ)m . The ratio x:y is ____ .",
    "tab": "topic1",
    "formula": "a→ = F→/m,  r→ = ½ a→ t²",
    "steps": [
      "Mass m = 100 g = 0.1 kg. Acceleration a→ = F→ / m = (5î + 10ĵ) / 0.1 = (50î + 100ĵ) m/s².",
      "Initial velocity is zero at t = 0 &rArr; position after 2 s is r→ = ½ a→ t² = ½ (50î + 100ĵ)(4) = (100î + 200ĵ) m.",
      "Equate with given position (2x î + 5y ĵ): 2x = 100 &rArr; x = 50, and 5y = 200 &rArr; y = 40.",
      "Compute ratio x : y = 50 : 40 = 5 : 4 = 1.25."
    ],
    "ans": "5:4 (or 1.25)",
    "takeaway": "Force produces independent constant accelerations along each Cartesian axis."
  },
  {
    "id": "EXAM-03",
    "num": "JEE Q3",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2026 (Online) 4th April Evening Shift",
    "q": "If x and y coordinates of a projectile as a function of time (t) are given as 24t and 43.6t−4.9t2 , respectively, then the angle (in degrees) made by the projectile with horizontal when t=2s is ____ .",
    "tab": "topic1",
    "formula": "v_x = dx/dt,  v_y = dy/dt,  tan θ = v_y / v_x",
    "steps": [
      "Given x(t) = 24t &rArr; v_x = dx/dt = 24 m/s (constant).",
      "Given y(t) = 43.6t - 4.9t² &rArr; v_y = dy/dt = 43.6 - 9.8t.",
      "Evaluate vertical velocity at t = 2 s: v_y(2) = 43.6 - 9.8(2) = 43.6 - 19.6 = 24 m/s.",
      "Find angle with horizontal: tan θ = v_y / v_x = 24 / 24 = 1 &rArr; θ = 45°."
    ],
    "ans": "45°",
    "takeaway": "Angle with horizontal at any instant is given by tan θ = v_y(t) / v_x(t)."
  },
  {
    "id": "EXAM-04",
    "num": "JEE Q4",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2026 (Online) 4th April Morning Shift",
    "q": "The two projectiles are projected with the same initial velocities at the 15∘ and 30∘ with respect to the horizontal. The ratio of their ranges is 1:x . The value of x is",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-05",
    "num": "JEE Q5",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2026 (Online) 24th January Morning Shift",
    "q": "A boy throws a ball into air at 45∘ from the horizontal to land it on a roof of a building of height H . If the ball attains maximum height in 2 s and lands on the building in 3 s after launch, then value of H is ____ m. (g=10m/s2)",
    "tab": "topic6",
    "formula": "t_apex = u_y / g,  y(t) = u_y t - ½ g t²",
    "steps": [
      "Time to reach maximum height is t_apex = 2 s &rArr; u_y / g = 2 &rArr; u_y = 20 m/s (taking g = 10 m/s²).",
      "Ball lands on roof at t = 3 s.",
      "Height of the roof is the vertical position of the ball at t = 3 s:",
      "H = y(3) = u_y(3) - ½ g (3)² = 20(3) - 5(9) = 60 - 45 = 15 m."
    ],
    "ans": "H = 15 m",
    "takeaway": "Unequal elevation landings are solved by evaluating y(t) at the arrival time."
  },
  {
    "id": "EXAM-06",
    "num": "JEE Q6",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2026 (Online) 22nd January Morning Shift",
    "q": "A projectile is thrown upward at an angle 60∘ with the horizontal. The speed of the projectile is 20m/s when its direction of motion is 45∘ with the horizontal. The initial speed of the projectile is ____ m/s .",
    "tab": "topic2",
    "formula": "v_x = u cos θ = v cos α  (Horizontal velocity conservation)",
    "steps": [
      "Throughout projectile flight, horizontal velocity remains strictly constant: v_x = u cos θ = v cos α.",
      "Given initial angle θ = 60°, and at inclination α = 45° speed is v = 20 m/s.",
      "Equate horizontal components: u cos 60° = 20 cos 45°.",
      "Substitute values: u (1/2) = 20 (1/√2) &rArr; u = 40 / √2 = 20√2 m/s ≈ 28.28 m/s."
    ],
    "ans": "20√2 m/s (≈ 28.3 m/s)",
    "takeaway": "Horizontal velocity never changes in projectile motion under gravity."
  },
  {
    "id": "EXAM-07",
    "num": "JEE Q7",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2026 (Online) 21st January Evening Shift",
    "q": "A river of width 200 m is flowing from west to east with a speed of 18 km/h. A boat, moving with speed of 36 km/h in still water, is made to travel one-round trip (bank to bank of the river). Minimum time taken by the boat for this journey and also the displacement along the river bank are ______ and ______ respectively.",
    "tab": "relative",
    "formula": "t_min = d / v_b,  drift = v_r t",
    "steps": [
      "River width d = 200 m. River flow speed v_r = 18 km/h = 5 m/s. Boat still water speed v_b = 36 km/h = 10 m/s.",
      "Minimum time crossing requires steering directly perpendicular to banks (θ = 0°):",
      "One-way time: t₁ = d / v_b = 200 / 10 = 20 s. Return trip time: t₂ = 200 / 10 = 20 s. Total time = 40 s.",
      "Downstream drift on outgoing trip: x₁ = v_r t₁ = 5 &times; 20 = 100 m downstream.",
      "On return trip, boat again drifts downstream: x₂ = 5 &times; 20 = 100 m.",
      "Total displacement along river bank = 100 + 100 = 200 m downstream."
    ],
    "ans": "40 s and 200 m",
    "takeaway": "Minimum crossing time is achieved by aiming straight across, but results in downstream drift."
  },
  {
    "id": "EXAM-08",
    "num": "JEE Q8",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2025 (Online) 8th April Evening Shift",
    "q": "Two balls with same mass and initial velocity, are projected at different angles in such a way that maximum height reached by first ball is 8 times higher than that of the second ball. T1 and T2 are the total flying times of first and second ball, respectively, then the ratio of T1 and T2 is",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-09",
    "num": "JEE Q9",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2025 (Online) 7th April Evening Shift",
    "q": "A helicopter flying horizontally with a speed of 360 km/h at an altitude of 2 km, drops an object at an instant. The object hits the ground at a point O, 20 s after it is dropped. Displacement of 'O' from the position of helicopter where the object was released is : (use acceleration due to gravity g = 10 m/s 2 and neglect air resistance)",
    "tab": "topic6",
    "formula": "x = v_x t,  y = h = ½ g t²,  S = √(x² + y²)",
    "steps": [
      "Horizontal speed of helicopter: v_x = 360 km/h = 100 m/s. Altitude h = 2 km = 2000 m.",
      "Horizontal displacement in t = 20 s: x = v_x t = 100 &times; 20 = 2000 m.",
      "Vertical displacement: y = 2000 m.",
      "Total straight-line displacement from drop point: S = √(x² + y²) = √(2000² + 2000²) = 2000√2 m ≈ 2.83 km."
    ],
    "ans": "2000√2 m (≈ 2828 m)",
    "takeaway": "Displacement is the straight-line vector from release point to impact point."
  },
  {
    "id": "EXAM-10",
    "num": "JEE Q10",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2025 (Online) 7th April Morning Shift",
    "q": "Two projectiles are fired from ground with same initial speeds from same point at angles (45∘+ α) and (45∘−α) with horizontal direction. The ratio of their times of flights is",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-11",
    "num": "JEE Q11",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2025 (Online) 3rd April Evening Shift",
    "q": "A particle is projected with velocity u so that its horizontal range is three times the maximum height attained by it. The horizontal range of the projectile is given as nu225g , where value of n is: (Given, ' g ' is the acceleration due to gravity.)",
    "tab": "topic2",
    "formula": "R tan θ = 4H",
    "steps": [
      "Given condition: R = 3H.",
      "Substitute into the 4H identity: (3H) tan θ = 4H &rArr; tan θ = 4/3.",
      "From tan θ = 4/3, right triangle yields sin θ = 4/5, cos θ = 3/5.",
      "Range R = (2 u² sin θ cos θ) / g = [2 u² (4/5)(3/5)] / g = (24 u²) / (25 g).",
      "Comparing with R = n u² / (25 g), we get n = 24."
    ],
    "ans": "n = 24",
    "takeaway": "Use the 4H identity R tan θ = 4H to immediately find launch angle from R/H ratio."
  },
  {
    "id": "EXAM-12",
    "num": "JEE Q12",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2025 (Online) 3rd April Morning Shift",
    "q": "The angle of projection of a particle is measured from the vertical axis as φ and the maximum height reached by the particle is hm . Here hm as function of φ can be presented as",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-13",
    "num": "JEE Q13",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2025 (Online) 2nd April Morning Shift",
    "q": "A river is flowing from west to east direction with speed of 9kmh−1 . If a boat capable of moving at a maximum speed of 27kmh−1 in still water, crosses the river in half a minute, while moving with maximum speed at an angle of 150∘ to direction of river flow, then the width of the river is :",
    "tab": "relative",
    "formula": "d = v_y t = (v_b sin 30°) t",
    "steps": [
      "Boat speed v_b = 27 km/h = 7.5 m/s. Crossing time t = 0.5 min = 30 s.",
      "Angle with river flow is 150° &rArr; angle with perpendicular to bank is 150° - 90° = 60° upstream (or 30° with bank).",
      "Effective crossing velocity perpendicular to bank: v_y = v_b sin(150°) = 7.5 &times; 0.5 = 3.75 m/s.",
      "River width: d = v_y &times; t = 3.75 &times; 30 = 112.5 m."
    ],
    "ans": "112.5 m",
    "takeaway": "Only the velocity component perpendicular to river banks causes crossing."
  },
  {
    "id": "EXAM-14",
    "num": "JEE Q14",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2025 (Online) 29th January Morning Shift",
    "q": "Two projectiles are fired with same initial speed from same point on ground at angles of (45∘−α) and (45∘+α) , respectively, with the horizontal direction. The ratio of their maximum heights attained is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-15",
    "num": "JEE Q15",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2025 (Online) 24th January Evening Shift",
    "q": "The position vector of a moving body at any instant of time is given as r→=(5t2iˆ−5tjˆ)m . The magnitude and direction of velocity at t=2s is,",
    "tab": "topic1",
    "formula": "v→ = dr→/dt = (dx/dt)î + (dy/dt)ĵ",
    "steps": [
      "Position vector r→ = (5t² î - 5t ĵ) m.",
      "Differentiate with respect to time: v→ = d/dt(5t² î - 5t ĵ) = 10t î - 5 ĵ m/s.",
      "At t = 2 s: v→ = 10(2) î - 5 ĵ = 20 î - 5 ĵ m/s.",
      "Magnitude v = √(20² + (-5)²) = √(400 + 25) = √425 = 5√17 m/s ≈ 20.6 m/s.",
      "Direction: tan θ = -5 / 20 = -1/4 (pointing below +x axis)."
    ],
    "ans": "5√17 m/s, tan θ = -1/4",
    "takeaway": "Velocity is the first time-derivative of the 2D position vector."
  },
  {
    "id": "EXAM-16",
    "num": "JEE Q16",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2025 (Online) 24th January Morning Shift",
    "q": "An object of mass ' m ' is projected from origin in a vertical xy plane at an angle 45∘ with the x− axis with an initial velocity v0 . The magnitude and direction of the angular momentum of the object with respect to origin, when it reaches at the maximum height, will be [ g is acceleration due to gravity]",
    "tab": "topic1",
    "formula": "L→ = r→ &times; p→ = r→ &times; (m v→)",
    "steps": [
      "At apex of projectile: position r→ = (R/2) î + H ĵ, velocity is purely horizontal v→ = (v₀ cos 45°) î = (v₀ / √2) î.",
      "Angular momentum L→ = r→ &times; (m v→) = [(R/2) î + H ĵ] &times; m(v₀ / √2) î = -m(v₀ / √2) H k̂.",
      "Maximum height H = (v₀ sin 45°)² / (2g) = v₀² / (4g).",
      "Magnitude |L→| = m (v₀ / √2) &times; [v₀² / (4g)] = (m v₀³) / (4√2 g) = (m v₀³ √2) / (8g) pointing into page (-k̂)."
    ],
    "ans": "(m v₀³ √2) / (8g) (-k̂)",
    "takeaway": "At the apex, only the apex height H contributes to torque-arm relative to origin."
  },
  {
    "id": "EXAM-17",
    "num": "JEE Q17",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2025 (Online) 22nd January Evening Shift",
    "q": "A ball of mass 100 g is projected with velocity 20m/s at 60∘ with horizontal. The decrease in kinetic energy of the ball during the motion from point of projection to highest point is",
    "tab": "topic2",
    "formula": "KE_apex = ½ m (u cos θ)² = KE₀ cos² θ",
    "steps": [
      "Mass m = 100 g = 0.1 kg, initial speed u = 20 m/s, θ = 60°.",
      "Initial kinetic energy: KE₀ = ½ m u² = ½ (0.1)(20²) = ½ (0.1)(400) = 20 J.",
      "At highest point, vertical speed is zero; speed is purely horizontal: v_apex = u cos 60° = 20(0.5) = 10 m/s.",
      "Apex kinetic energy: KE_apex = ½ m v_apex² = ½ (0.1)(10²) = 5 J.",
      "Decrease in kinetic energy: ΔKE = KE₀ - KE_apex = 20 - 5 = 15 J."
    ],
    "ans": "15 J",
    "takeaway": "At the apex, the projectile retains KE_apex = KE₀ cos² θ; vertical kinetic energy is converted into gravitational potential energy."
  },
  {
    "id": "EXAM-18",
    "num": "JEE Q18",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2024 (Online) 8th April Evening Shift",
    "q": "The angle of projection for a projectile to have same horizontal range and maximum height is :",
    "tab": "topic2",
    "formula": "R tan θ = 4H",
    "steps": [
      "Given R = H.",
      "From the 4H Identity: R tan θ = 4H &rArr; H tan θ = 4H &rArr; tan θ = 4.",
      "Angle θ = arctan(4) ≈ 75.96° ≈ 76°."
    ],
    "ans": "tan θ = 4 (θ ≈ 76°)",
    "takeaway": "R = H requires tan θ = 4; for R = 4H, tan θ = 1 (θ = 45°)."
  },
  {
    "id": "EXAM-19",
    "num": "JEE Q19",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2024 (Online) 4th April Morning Shift",
    "q": "The co-ordinates of a particle moving in x - y plane are given by : x=2+4t,y=3t+8t2 . The motion of the particle is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-20",
    "num": "JEE Q20",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2024 (Online) 30th January Evening Shift",
    "q": "Projectiles A and B are thrown at angles of 45∘ and 60∘ with vertical respectively from top of a 400m high tower. If their ranges and times of flight are same, the ratio of their speeds of projection vA:vB is : [Take g=10ms−2 ]",
    "tab": "topic6",
    "formula": "t = √(2h/g),  R = u √(2h/g),  v = √(u² + 2gh)",
    "steps": [
      "Account for non-zero elevation boundary: y(t) = h + u_y t - ½ g t².",
      "Determine time of flight from vertical boundary condition.",
      "Compute horizontal range and landing velocity vector."
    ],
    "ans": "Computed from asymmetric boundary kinematics",
    "takeaway": "Symmetric ground formulas break down when launch and landing heights differ."
  },
  {
    "id": "EXAM-21",
    "num": "JEE Q21",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2024 (Online) 27th January Morning Shift",
    "q": "Position of an ant ( S in metres) moving in Y - Z plane is given by S=2t2jˆ+5kˆ (where t is in second). The magnitude and direction of velocity of the ant at t=1s will be :",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-22",
    "num": "JEE Q22",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 11th April Evening Shift",
    "q": "A projectile is projected at 30∘ from horizontal with initial velocity 40ms−1 . The velocity of the projectile at t=2s from the start will be : (Given g=10m/s2 )",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-23",
    "num": "JEE Q23",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 10th April Evening Shift",
    "q": "Two projectiles are projected at 30∘ and 60∘ with the horizontal with the same speed. The ratio of the maximum height attained by the two projectiles respectively is:",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-24",
    "num": "JEE Q24",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 10th April Morning Shift",
    "q": "The range of the projectile projected at an angle of 15 ∘ with horizontal is 50 m. If the projectile is projected with same velocity at an angle of 45 ∘ with horizontal, then its range will be",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-25",
    "num": "JEE Q25",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2023 (Online) 8th April Evening Shift",
    "q": "The trajectory of projectile, projected from the ground is given by y=x−x220 . Where x and y are measured in meter. The maximum height attained by the projectile will be.",
    "tab": "topic3",
    "formula": "y = x tan θ (1 - x/R)",
    "steps": [
      "Given trajectory: y = x - x²/20 = x (1 - x/20).",
      "Compare with factored form y = x tan θ (1 - x/R):",
      "Coefficient comparison gives tan θ = 1 (launch angle θ = 45°) and Range R = 20 m.",
      "Using the 4H identity: R tan θ = 4H &rArr; 20(1) = 4H &rArr; H = 5 m."
    ],
    "ans": "H = 5 m",
    "takeaway": "Factored form y = x tan θ (1 - x/R) reveals launch angle and horizontal range instantly by inspection."
  },
  {
    "id": "EXAM-26",
    "num": "JEE Q26",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2023 (Online) 8th April Morning Shift",
    "q": "Two projectiles A and B are thrown with initial velocities of 40m/s and 60m/s at angles 30∘ and 60∘ with the horizontal respectively. The ratio of their ranges respectively is (g=10m/s2)",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-27",
    "num": "JEE Q27",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 6th April Morning Shift",
    "q": "Given below are two statements : one is labelled as Assertion A and the other is labelled as Reason R Assertion A : When a body is projected at an angle 45∘ , it's range is maximum. Reason R : For maximum range, the value of sin⁡2θ should be equal to one. In the light of the above statements, choose the correct answer from the options given below:",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-28",
    "num": "JEE Q28",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2023 (Online) 1st February Morning Shift",
    "q": "A child stands on the edge of the cliff 10m above the ground and throws a stone horizontally with an initial speed of 5ms−1 . Neglecting the air resistance, the speed with which the stone hits the ground will be ms−1 (given, g=10ms−2 ).",
    "tab": "topic6",
    "formula": "v = √(v_x² + v_y²),  v_y = √(2gh)",
    "steps": [
      "Horizontal velocity remains constant: v_x = 5 m/s.",
      "Vertical velocity acquired by falling through h = 10 m: v_y = √(2gh) = √(2 &times; 10 &times; 10) = √200 = 10√2 m/s.",
      "Striking speed: v = √(v_x² + v_y²) = √(5² + 200) = √(25 + 200) = √225 = 15 m/s."
    ],
    "ans": "15 m/s",
    "takeaway": "By energy conservation, striking speed is v = √(u² + 2gh), completely independent of launch angle!"
  },
  {
    "id": "EXAM-29",
    "num": "JEE Q29",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 31st January Morning Shift",
    "q": "The initial speed of a projectile fired from ground is u . At the highest point during its motion, the speed of projectile is sqrt32u . The time of flight of the projectile is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-30",
    "num": "JEE Q30",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 25th January Evening Shift",
    "q": "Two objects are projected with same velocity 'u' however at different angles α and β with the horizontal. If α+β=90∘ , the ratio of horizontal range of the first object to the 2nd object will be :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-31",
    "num": "JEE Q31",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 24th January Morning Shift",
    "q": "The maximum vertical height to which a man can throw a ball is 136 m. The maximum horizontal distance upto which he can throw the same ball is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-32",
    "num": "JEE Q32",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2022 (Online) 28th July Evening Shift",
    "q": "At time t=0 a particle starts travelling from a height 7zˆcm in a plane keeping z coordinate constant. At any instant of time it's position along the xˆ and yˆ directions are defined as 3t and 5t3 respectively. At t = 1s acceleration of the particle will be",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-33",
    "num": "JEE Q33",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 26th July Evening Shift",
    "q": "Two projectiles are thrown with same initial velocity making an angle of 45∘ and 30∘ with the horizontal respectively. The ratio of their respective ranges will be :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-34",
    "num": "JEE Q34",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 26th July Morning Shift",
    "q": "Two projectiles thrown at 30∘ and 45∘ with the horizontal respectively, reach the maximum height in same time. The ratio of their initial velocities is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-35",
    "num": "JEE Q35",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 25th July Evening Shift",
    "q": "A ball is projected from the ground with a speed 15 ms − 1 at an angle θ with horizontal so that its range and maximum height are equal, then 'tan θ ' will be equal to :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-36",
    "num": "JEE Q36",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2022 (Online) 30th June Morning Shift",
    "q": "At t = 0, truck, starting from rest, moves in the positive x-direction at uniform acceleration of 5 ms − 2 . At t = 20 s, a ball is released from the top of the truck. The ball strikes the ground in 1 s after the release. The velocity of the ball, when it strikes the ground, will be : (Given g = 10 ms − 2 )",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-37",
    "num": "JEE Q37",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 30th June Morning Shift",
    "q": "Two projectiles P 1 and P 2 thrown with speed in the ratio sqrt3 : sqrt2 , attain the same height during their motion. If P 2 is thrown at an angle of 60 ∘ with the horizontal, the angle of projection of P 1 with horizontal will be :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-38",
    "num": "JEE Q38",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 29th June Evening Shift",
    "q": "A person can throw a ball upto a maximum range of 100 m. How high above the ground he can throw the same ball?",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-39",
    "num": "JEE Q39",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 27th June Morning Shift",
    "q": "A projectile is launched at an angle ' α ' with the horizontal with a velocity 20 ms − 1 . After 10 s, its inclination with horizontal is ' β '. The value of tan β will be : (g = 10 ms − 2 ).",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-40",
    "num": "JEE Q40",
    "source": "ExamSide JEE Main",
    "bucket": 9,
    "bucketName": "Rain-Man & Dual-Speed Invariant",
    "year": "JEE Main 2022 (Online) 27th June Morning Shift",
    "q": "A girl standing on road holds her umbrella at 45 ∘ with the vertical to keep the rain away. If she starts running without umbrella with a speed of 15 sqrt2 kmh − 1 , the rain drops hit her head vertically. The speed of rain drops with respect to the moving girl is :",
    "tab": "relative",
    "formula": "v_rx = v_ry,  v_m = v_rx &rArr; v_rel = v_ry",
    "steps": [
      "When standing, girl holds umbrella at 45° with vertical &rArr; tan 45° = 1 &rArr; v_rx = v_ry (rain falls obliquely).",
      "When running at v_g = 15√2 km/h, rain hits vertically &rArr; relative horizontal velocity is zero:",
      "v_rx - v_g = 0 &rArr; v_rx = 15√2 km/h.",
      "Since v_ry = v_rx, vertical rain speed is also v_ry = 15√2 km/h.",
      "Relative to the moving girl, rain velocity has zero horizontal component and vertical component -15√2 ĵ km/h.",
      "Therefore, speed of rain drops relative to moving girl is 15√2 km/h."
    ],
    "ans": "15√2 km/h (≈ 21.2 km/h)",
    "takeaway": "When rain appears vertical, the runner's speed exactly cancels the rain's horizontal velocity."
  },
  {
    "id": "EXAM-41",
    "num": "JEE Q41",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2022 (Online) 25th June Evening Shift",
    "q": "Given below are two statements. One is labelled as Assertion A and the other is labelled as Reason R. Assertion A : Two identical balls A and B thrown with same velocity 'u' at two different angles with horizontal attained the same range R. IF A and B reached the maximum height h 1 and h 2 respectively, then R=4sqrth1h2 Reason R : Product of said heights. h1h2=(u2sin2θ2g).(u2cos2θ2g) Choose the correct answer :",
    "tab": "topic5",
    "formula": "R = 4 √(H₁ H₂)",
    "steps": [
      "Heights at complementary angles: H₁ = (u² sin² θ) / (2g), H₂ = (u² cos² θ) / (2g).",
      "Product: H₁ H₂ = (u⁴ sin² θ cos² θ) / (4 g²).",
      "Take square root: √(H₁ H₂) = (u² sin θ cos θ) / (2g) = R / 4.",
      "Multiply by 4: 4 √(H₁ H₂) = R. Both Assertion and Reason are true and correct."
    ],
    "ans": "Assertion and Reason are both true",
    "takeaway": "Geometric mean of complementary apex heights gives range: R = 4√(H₁ H₂)."
  },
  {
    "id": "EXAM-42",
    "num": "JEE Q42",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 24th June Morning Shift",
    "q": "A projectile is projected with velocity of 25 m/s at an angle θ with the horizontal. After t seconds its inclination with horizontal becomes zero. If R represents horizontal range of the projectile, the value of θ will be : [use g = 10 m/s 2 ]",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-43",
    "num": "JEE Q43",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2021 (Online) 1st September Evening Shift",
    "q": "The ranges and heights for two projectiles projected with the same initial velocity at angles 42 ∘ and 48 ∘ with the horizontal are R 1 , R 2 and H 1 , H 2 respectively. Choose the correct option :",
    "tab": "topic5",
    "formula": "θ₁ + θ₂ = 90° &rArr; R₁ = R₂",
    "steps": [
      "Check sum of angles: 42° + 48° = 90° (complementary angles).",
      "Because sin(2 &times; 42°) = sin(84°) and sin(2 &times; 48°) = sin(96°) = sin(84°), ranges are identical: R₁ = R₂.",
      "Maximum height H ∝ sin² θ. Since 48° > 42°, sin 48° > sin 42° &rArr; H₂ > H₁."
    ],
    "ans": "R₁ = R₂ and H₂ > H₁",
    "takeaway": "Complementary angles yield identical horizontal ranges, but larger launch angle yields greater apex height."
  },
  {
    "id": "EXAM-44",
    "num": "JEE Q44",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2021 (Online) 31st August Morning Shift",
    "q": "A helicopter is flying horizontally with a speed 'v' at an altitude 'h' has to drop a food packet for a man on the ground. What is the distance of helicopter from the man when the food packet is dropped?",
    "tab": "topic6",
    "formula": "t = √(2h/g),  R = u √(2h/g),  v = √(u² + 2gh)",
    "steps": [
      "Account for non-zero elevation boundary: y(t) = h + u_y t - ½ g t².",
      "Determine time of flight from vertical boundary condition.",
      "Compute horizontal range and landing velocity vector."
    ],
    "ans": "Computed from asymmetric boundary kinematics",
    "takeaway": "Symmetric ground formulas break down when launch and landing heights differ."
  },
  {
    "id": "EXAM-45",
    "num": "JEE Q45",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2021 (Online) 27th August Evening Shift",
    "q": "A player kicks a football with an initial speed of 25 ms − 1 at an angle of 45 ∘ from the ground. What are the maximum height and the time taken by the football to reach at the highest point during motion ? (Take g = 10 ms − 2 )",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-46",
    "num": "JEE Q46",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2021 (Online) 26th August Evening Shift",
    "q": "A bomb is dropped by fighter plane flying horizontally. To an observer sitting in the plane, the trajectory of the bomb is a :",
    "tab": "topic6",
    "formula": "t = √(2h/g),  R = u √(2h/g),  v = √(u² + 2gh)",
    "steps": [
      "Account for non-zero elevation boundary: y(t) = h + u_y t - ½ g t².",
      "Determine time of flight from vertical boundary condition.",
      "Compute horizontal range and landing velocity vector."
    ],
    "ans": "Computed from asymmetric boundary kinematics",
    "takeaway": "Symmetric ground formulas break down when launch and landing heights differ."
  },
  {
    "id": "EXAM-47",
    "num": "JEE Q47",
    "source": "ExamSide JEE Main",
    "bucket": 7,
    "bucketName": "2D Relative Velocity & Frames",
    "year": "JEE Main 2021 (Online) 20th July Morning Shift",
    "q": "A butterfly is flying with a velocity 4sqrt2 m/s in North-East direction. Wind is slowly blowing at 1 m/s from North to South. The resultant displacement of the butterfly in 3 seconds is :",
    "tab": "relative",
    "formula": "v→_B/A = v→_B - v→_A",
    "steps": [
      "Calculate individual velocities in ground frame.",
      "Apply Galilean vector subtraction v_B/A = v_B - v_A.",
      "Find relative magnitude and direction."
    ],
    "ans": "Galilean vector subtraction",
    "takeaway": "Bringing an observer to rest by applying -v_obs simplifies relative motion analysis."
  },
  {
    "id": "EXAM-48",
    "num": "JEE Q48",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2021 (Online) 16th March Evening Shift",
    "q": "A mosquito is moving with a velocity v→=0.5t2iˆ+3tjˆ+9kˆ m/s and accelerating in uniform conditions. What will be the direction of mosquito after 2 s?",
    "tab": "topic1",
    "formula": "v→ = dr→/dt = (dx/dt)î + (dy/dt)ĵ",
    "steps": [
      "Position vector r→ = (5t² î - 5t ĵ) m.",
      "Differentiate with respect to time: v→ = d/dt(5t² î - 5t ĵ) = 10t î - 5 ĵ m/s.",
      "At t = 2 s: v→ = 10(2) î - 5 ĵ = 20 î - 5 ĵ m/s.",
      "Magnitude v = √(20² + (-5)²) = √(400 + 25) = √425 = 5√17 m/s ≈ 20.6 m/s.",
      "Direction: tan θ = -5 / 20 = -1/4 (pointing below +x axis)."
    ],
    "ans": "5√17 m/s, tan θ = -1/4",
    "takeaway": "Velocity is the first time-derivative of the 2D position vector."
  },
  {
    "id": "EXAM-49",
    "num": "JEE Q49",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2021 (Online) 26th February Evening Shift",
    "q": "The trajectory of a projectile in a vertical plane is y = α x − β x 2 , where α and β are constants and x & y are respectively the horizontal and vertical distances of the projectile from the point of projection. The angle of projection θ and the maximum height attained H are respectively given by :",
    "tab": "topic3",
    "formula": "y = x (α - β x) = α x (1 - (β/α) x)",
    "steps": [
      "Factor given equation: y = α x (1 - x / (α/β)).",
      "Compare with y = x tan θ (1 - x/R):",
      "Angle of projection: tan θ = α &rArr; θ = arctan(α).",
      "Horizontal range: R = α / β.",
      "Maximum height from 4H identity: 4H = R tan θ = (α/β)(α) = α²/β &rArr; H = α² / (4β)."
    ],
    "ans": "θ = arctan(α), H = α² / (4β)",
    "takeaway": "For y = αx - βx², tan θ = α, R = α/β, and H = α²/(4β)."
  },
  {
    "id": "EXAM-50",
    "num": "JEE Q50",
    "source": "ExamSide JEE Main",
    "bucket": 9,
    "bucketName": "Rain-Man & Dual-Speed Invariant",
    "year": "JEE Main 2020 (Online) 6th September Evening Slot",
    "q": "When a car is at rest, its driver sees rain drops falling on it vertically. When driving the car with speed v, he sees that rain drops are coming at an angle 60° from the horizontal. On further increasing the speed of the car to (1 + β )v, this angle changes to 45 o . The value of β is close to :",
    "tab": "relative",
    "formula": "tan θ₁ = v_m1 / v_ry,  tan θ₂ = v_m2 / v_ry",
    "steps": [
      "When car is at rest, rain falls vertically &rArr; true rain velocity has zero horizontal component (v_rx = 0, speed v_r).",
      "At car speed v, rain appears at 60° from horizontal, which means 30° with vertical: tan 30° = v / v_r &rArr; 1/√3 = v / v_r &rArr; v_r = √3 v.",
      "At speed (1 + β)v, angle is 45° from horizontal, so 45° with vertical: tan 45° = (1 + β)v / v_r = 1 &rArr; (1 + β)v = v_r.",
      "Substitute v_r = √3 v: (1 + β)v = √3 v &rArr; 1 + β = √3 &rArr; β = √3 - 1 ≈ 1.732 - 1 = 0.732 ≈ 0.73."
    ],
    "ans": "β = √3 - 1 ≈ 0.73",
    "takeaway": "Apparent rain angle with vertical satisfies tan θ = v_observer / v_rain."
  },
  {
    "id": "EXAM-51",
    "num": "JEE Q51",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2020 (Online) 5th September Morning Slot",
    "q": "A balloon is moving up in air vertically above a point A on the ground. When it is at a height h 1 , a girl standing at a distanced (point B) from A (see figure) sees it at an angle 45 o with respect to the vertical. When the balloon climbs up a further height h 2 , it is seen at an angle 60 o with respect to the vertical if the girl moves further by a distance 2.464 d(point C). Then the height h 2 is (given tan 30 o = 0.5774)",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-52",
    "num": "JEE Q52",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2020 (Online) 4th September Morning Slot",
    "q": "Starting from the origin at time t = 0, with initial velocity 5 jˆ ms -1 , a particle moves in the x-y plane with a constant acceleration of (10iˆ+4jˆ) ms -2 . At time t, its coordinates are (20 m, y 0 m). The values of t and y 0 are, respectively:",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-53",
    "num": "JEE Q53",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2020 (Online) 9th January Evening Slot",
    "q": "A particle starts from the origin at t = 0 with an initial velocity of 3.0 iˆ m/s and moves in the x-y plane with a constant acceleration (6iˆ+4jˆ) m/s 2 . The x-coordinate of the particle at the instant when its y-coordinate is 32 m is D meters. The value of D is :-",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-54",
    "num": "JEE Q54",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2020 (Online) 8th January Evening Slot",
    "q": "A particle moves such that its position vector r→(t)=cos⁡ωtiˆ+sin⁡ωtjˆ where ω is a constant and t is time. Then which of the following statements is true for the velocity v→(t) and acceleration a→(t) of the particle :",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-55",
    "num": "JEE Q55",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2019 (Online) 12th April Evening Slot",
    "q": "Two particles are projected from the same point with the same speed u such that they have the same range R, but different maximum heights, h 1 and h 2 . Which of the following is correct ?",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-56",
    "num": "JEE Q56",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2019 (Online) 12th April Morning Slot",
    "q": "The trajectory of a projectile near the surface of the earth is given as y = 2x – 9x 2 . If it were launched at an angle θ 0 with speed v 0 then (g = 10 ms –2 ) :",
    "tab": "topic3",
    "formula": "tan θ₀ = 2,  (g) / (2 v₀² cos² θ₀) = 9",
    "steps": [
      "Compare y = 2x - 9x² with y = x tan θ₀ - [g / (2 v₀² cos² θ₀)] x².",
      "From first term: tan θ₀ = 2 &rArr; cos² θ₀ = 1 / (1 + tan² θ₀) = 1 / (1 + 4) = 1/5.",
      "From second term: g / [2 v₀² cos² θ₀] = 9.",
      "Substitute g = 10 and cos² θ₀ = 1/5: 10 / [2 v₀² (1/5)] = 25 / v₀² = 9.",
      "Solve: v₀² = 25 / 9 &rArr; v₀ = 5/3 m/s."
    ],
    "ans": "v₀ = 5/3 m/s, tan θ₀ = 2",
    "takeaway": "Match polynomial coefficients of trajectory equation to extract physical launch speed and angle."
  },
  {
    "id": "EXAM-57",
    "num": "JEE Q57",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2019 (Online) 12th April Morning Slot",
    "q": "A shell is fired from a fixed artillery gun with an initial speed u such that it hits the target on the ground at a distance R from it. If t 1 and t 2 are the values of the time taken by it to hit the target in two possible ways, the product t 1 t 2 is -",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-58",
    "num": "JEE Q58",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2019 (Online) 10th April Evening Slot",
    "q": "A plane is inclined at an angle α = 30° with respect to the horizontal. A particle is projected with a speed u = 2 ms –1 , from the base of the plane, making an angle θ = 15° with respect to the plane as shown in the figure. the distance from the base, at which the particle hits the plane is close to : (Take g = 10 ms –2 )",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-59",
    "num": "JEE Q59",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2019 (Online) 9th April Morning Slot",
    "q": "The stream of a river is flowing with a speed of 2km/h. A swimmer can swim at a speed of 4km/h. What should be the direction of the swimmer with respect to the flow of the river to cross the river straight ?",
    "tab": "relative",
    "formula": "sin θ = v_river / v_swimmer",
    "steps": [
      "To cross straight without drift, resultant velocity must be perpendicular to banks.",
      "The upstream component of swimmer velocity must balance river flow: v_s sin θ = v_r.",
      "Given v_r = 2 km/h, v_s = 4 km/h &rArr; sin θ = 2 / 4 = 1/2 &rArr; θ = 30° upstream from normal.",
      "Direction with respect to river flow direction: 90° + 30° = 120°."
    ],
    "ans": "120° with river flow",
    "takeaway": "Zero drift requires swimming upstream at angle sin θ = v_r / v_s, which requires v_s > v_r."
  },
  {
    "id": "EXAM-60",
    "num": "JEE Q60",
    "source": "ExamSide JEE Main",
    "bucket": 7,
    "bucketName": "2D Relative Velocity & Frames",
    "year": "JEE Main 2019 (Online) 8th April Morning Slot",
    "q": "Ship A is sailing towards north-east with velocity v→=30i∧+50j∧ km/hr where i∧ points east and j∧ , north. Ship B is at a distance of 80 km east and 150 km north of Ship A and is sailing towards west at 10 km/hr. A will be at minimum distance from B in :",
    "tab": "relative",
    "formula": "r→_rel(t) = r→_rel(0) + v→_rel t,  d/dt |r→_rel|² = 0",
    "steps": [
      "v_A = 30 î + 50 ĵ km/h, v_B = -10 î km/h.",
      "Relative velocity v_B/A = v_B - v_A = (-10 î) - (30 î + 50 ĵ) = -40 î - 50 ĵ km/h.",
      "Initial separation: r_B/A(0) = 80 î + 150 ĵ km.",
      "Relative position at time t: r(t) = (80 - 40t) î + (150 - 50t) ĵ.",
      "Minimize distance squared: d/dt [(80-40t)² + (150-50t)²] = 0 &rArr; 2(80-40t)(-40) + 2(150-50t)(-50) = 0.",
      "4(80 - 40t) + 5(150 - 50t) = 0 &rArr; 320 - 160t + 750 - 250t = 0 &rArr; 1070 = 410t &rArr; t = 107 / 41 hr ≈ 2.61 hr."
    ],
    "ans": "t = 107/41 hr (≈ 2.61 hr)",
    "takeaway": "Closest approach between two bodies is found by bringing one body to rest and dropping perpendicular to relative path."
  },
  {
    "id": "EXAM-61",
    "num": "JEE Q61",
    "source": "ExamSide JEE Main",
    "bucket": 7,
    "bucketName": "2D Relative Velocity & Frames",
    "year": "JEE Main 2019 (Online) 12th January Morning Slot",
    "q": "A person standing on an open ground hears the sound of a jet aeroplane, coming from north at an angle 60 o with ground level. But he finds the aeroplane right vertically above his position. If v is the speed of sound, speed of the plane is :",
    "tab": "relative",
    "formula": "v→_B/A = v→_B - v→_A",
    "steps": [
      "Calculate individual velocities in ground frame.",
      "Apply Galilean vector subtraction v_B/A = v_B - v_A.",
      "Find relative magnitude and direction."
    ],
    "ans": "Galilean vector subtraction",
    "takeaway": "Bringing an observer to rest by applying -v_obs simplifies relative motion analysis."
  },
  {
    "id": "EXAM-62",
    "num": "JEE Q62",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2019 (Online) 10th January Morning Slot",
    "q": "Two guns A and B can fire bullets at speeds 1 km/s and 2 km/s respectively. From a point on a horizontal ground, they are fired in all possible directions. The ratio of maximum areas covered by the bullets fired by the two guns, on the ground is -",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-63",
    "num": "JEE Q63",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2019 (Online) 9th January Evening Slot",
    "q": "The position co-ordinates of a particle moving in a 3-D coordinate system is given by x = a cos ω t y = a sin ω t and z = a ω t The speed of the particle is :",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-64",
    "num": "JEE Q64",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2019 (Online) 9th January Morning Slot",
    "q": "A particle is moving with a velocity v→=K(yiˆ+xjˆ), where K is a constant. The general equation for its path is :",
    "tab": "topic3",
    "formula": "y = x tan θ - (g x²)/(2 u² cos² θ) = x tan θ (1 - x/R)",
    "steps": [
      "Convert trajectory equation into standard form y = x tan θ - [g/(2u²cos²θ)] x² or factored form y = x tan θ (1 - x/R).",
      "Compare coefficients to determine launch angle θ, speed u, or range R.",
      "Solve for requested kinematic parameters."
    ],
    "ans": "Compare with trajectory standard form",
    "takeaway": "The parabolic trajectory equation eliminates time t to directly relate y to x."
  },
  {
    "id": "EXAM-65",
    "num": "JEE Q65",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2018 (Online) 15th April Evening Slot",
    "q": "A man in a car at location Q on a straight highway is moving with speed υ . He decides to reach a point P in a field at a distance d from the highway (point M) as shown in the figure. Speed of the car in the field is half to that on the highway. What should be the distance RM, so that the time taken to reach P is minimum ?",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-66",
    "num": "JEE Q66",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2013 (Offline)",
    "q": "A projectile is given an initial velocity of (iˆ+2jˆ) m/s, where iˆ is along the ground and jˆ is along the vertical. If g = 10 m/s 2 , the equation of its trajectory is:",
    "tab": "topic3",
    "formula": "y = x tan θ - (g x²)/(2 u² cos² θ) = x tan θ (1 - x/R)",
    "steps": [
      "Convert trajectory equation into standard form y = x tan θ - [g/(2u²cos²θ)] x² or factored form y = x tan θ (1 - x/R).",
      "Compare coefficients to determine launch angle θ, speed u, or range R.",
      "Solve for requested kinematic parameters."
    ],
    "ans": "Compare with trajectory standard form",
    "takeaway": "The parabolic trajectory equation eliminates time t to directly relate y to x."
  },
  {
    "id": "EXAM-67",
    "num": "JEE Q67",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "AIEEE 2012",
    "q": "A boy can throw a stone up to a maximum height of 10 m. The maximum horizontal distance that the boy can throw the same stone up to will be",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-68",
    "num": "JEE Q68",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "AIEEE 2011",
    "q": "A water fountain on the ground sprinkles water all around it. If the speed of water coming out of the fountain is v, the total area around the fountain that gets wet is :",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-69",
    "num": "JEE Q69",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "AIEEE 2010",
    "q": "A particle is moving with velocity v→=k(yiˆ+xjˆ) , where K is a constant. The general equation for its path is",
    "tab": "topic3",
    "formula": "y = x tan θ - (g x²)/(2 u² cos² θ) = x tan θ (1 - x/R)",
    "steps": [
      "Convert trajectory equation into standard form y = x tan θ - [g/(2u²cos²θ)] x² or factored form y = x tan θ (1 - x/R).",
      "Compare coefficients to determine launch angle θ, speed u, or range R.",
      "Solve for requested kinematic parameters."
    ],
    "ans": "Compare with trajectory standard form",
    "takeaway": "The parabolic trajectory equation eliminates time t to directly relate y to x."
  },
  {
    "id": "EXAM-70",
    "num": "JEE Q70",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "AIEEE 2009",
    "q": "A particle has an initial velocity 3iˆ+4jˆ and an acceleration of 0.4iˆ+0.3jˆ . Its speed after 10 s is:",
    "tab": "topic1",
    "formula": "v→ = dr→/dt,  a→ = dv→/dt,  r→(t) = r₀→ + v₀→ t + ½ a→ t²",
    "steps": [
      "Decompose position and velocity along independent x and y coordinates.",
      "Apply kinematic equations of motion separately: v = u + at, s = ut + ½at².",
      "Combine orthogonal components to determine resultant speed v = √(v_x² + v_y²)."
    ],
    "ans": "Evaluate from coordinate kinematic equations",
    "takeaway": "Orthogonal components operate on a single synchronized clock."
  },
  {
    "id": "EXAM-71",
    "num": "JEE Q71",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "AIEEE 2005",
    "q": "A particle is moving eastwards with a velocity of 5 m/s. In 10 seconds the velocity changes to 5 m/s northwards. The average acceleration in this time is",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-72",
    "num": "JEE Q72",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "AIEEE 2004",
    "q": "A projectile can have the same range 'R' for two angles of projection. If T 1 and T 2 be the time of flights in the two cases, then the product of the two time of flights is directly proportional to",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-73",
    "num": "JEE Q73",
    "source": "ExamSide JEE Main",
    "bucket": 6,
    "bucketName": "Dynamic Tracking & Interception",
    "year": "AIEEE 2004",
    "q": "A ball is thrown from a point with a speed ν 0 at an angle of projection θ. From the same point and at the same instant person starts running with a constant speed v02 to catch the ball. Will the person be able to catch the ball? If yes, what should be the angle of projection θ?",
    "tab": "topic6",
    "formula": "v_person = u cos θ",
    "steps": [
      "Ball is thrown with speed v₀ at angle θ; runner starts at same point and runs with constant speed v₀/2.",
      "For runner to catch ball at landing, runner must travel same horizontal distance in same time.",
      "Therefore, runner's speed must equal ball's horizontal velocity component: v_person = v₀ cos θ.",
      "Equate: v₀ / 2 = v₀ cos θ &rArr; cos θ = 1/2.",
      "Solve: θ = 60°. Yes, the person can catch the ball if θ = 60°."
    ],
    "ans": "Yes, θ = 60°",
    "takeaway": "To catch a projectile launched from the same position, runner speed must match horizontal velocity."
  },
  {
    "id": "EXAM-74",
    "num": "JEE Q74",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "AIEEE 2003",
    "q": "A boy playing on the roof of a 10 m high building throws a ball with a speed of 10 m/s at an angle of 30∘ with the horizontal. How far from the throwing point will the ball be at the height of 10 m from the ground? [g=10m/s2,sin⁡30∘=12,cos⁡30∘=sqrt32]",
    "tab": "topic6",
    "formula": "t = √(2h/g),  R = u √(2h/g),  v = √(u² + 2gh)",
    "steps": [
      "Account for non-zero elevation boundary: y(t) = h + u_y t - ½ g t².",
      "Determine time of flight from vertical boundary condition.",
      "Compute horizontal range and landing velocity vector."
    ],
    "ans": "Computed from asymmetric boundary kinematics",
    "takeaway": "Symmetric ground formulas break down when launch and landing heights differ."
  },
  {
    "id": "EXAM-75",
    "num": "JEE Q2",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2025 (Online) 29th January Morning Shift",
    "q": "The maximum speed of a boat in still water is 27 km/h. Now this boat is moving downstream in a river flowing at 9 km/h. A man in the boat throws a ball vertically upwards with speed of 10 m/s. Range of the ball as observed by an observer at rest on the bank is __________ cm. (Take g=10 m/s 2 )",
    "tab": "relative",
    "formula": "t = d / (v_b cos θ),  drift x = (v_r - v_b sin θ) t",
    "steps": [
      "Decompose boat/swimmer velocity into perpendicular component (crossing) and parallel component (drift).",
      "Crossing time is determined solely by perpendicular component: t = d / v_y.",
      "Drift along bank is determined by net parallel speed: x = (v_r + v_bx) t."
    ],
    "ans": "River-boat kinematic decomposition",
    "takeaway": "River flow affects only downstream drift, never crossing speed when steering perpendicular."
  },
  {
    "id": "EXAM-76",
    "num": "JEE Q3",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2025 (Online) 22nd January Morning Shift",
    "q": "A particle is projected at an angle of 30∘ from horizontal at a speed of 60m/s . The height traversed by the particle in the first second is h0 and height traversed in the last second, before it reaches the maximum height, is h1 . The ratio h0:h1 is __________. [Take, g=10m/s2 ]",
    "tab": "topic5",
    "formula": "R(θ) = R(90°-θ),  R = 4√(H₁ H₂),  T₁ T₂ = (2R)/g,  H₁ + H₂ = u²/(2g)",
    "steps": [
      "Recognize complementary angle symmetry: θ and 90°-θ produce identical range R.",
      "Apply dual invariant formulas: R = 4√(H₁ H₂), T₁ T₂ = 2R/g, or H₁ + H₂ = u²/(2g).",
      "Calculate required value."
    ],
    "ans": "Complementary symmetry verified",
    "takeaway": "Complementary launches share identical horizontal ranges with coupled heights and times."
  },
  {
    "id": "EXAM-77",
    "num": "JEE Q4",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2024 (Online) 8th April Evening Shift",
    "q": "A body of mass M thrown horizontally with velocity v from the top of the tower of height H touches the ground at a distance of 100m from the foot of the tower. A body of mass 2M thrown at a velocity v2 from the top of the tower of height 4H will touch the ground at a distance of _______ m.",
    "tab": "topic6",
    "formula": "R = u √(2h/g)",
    "steps": [
      "For first body: R₁ = v √(2H / g) = 100 m.",
      "Mass does not affect ballistic motion (mass M vs 2M is irrelevant).",
      "For second body thrown at velocity v/2 from height 4H:",
      "R₂ = (v / 2) √(2(4H) / g) = (v / 2) &times; 2 √(2H / g) = v √(2H / g) = R₁ = 100 m."
    ],
    "ans": "100 m",
    "takeaway": "Doubling the height quadruples fall distance, doubling fall time, which exactly compensates halving initial velocity."
  },
  {
    "id": "EXAM-78",
    "num": "JEE Q5",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2024 (Online) 5th April Evening Shift",
    "q": "The maximum height reached by a projectile is 64m . If the initial velocity is halved, the new maximum height of the projectile is ______ m .",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-79",
    "num": "JEE Q6",
    "source": "ExamSide JEE Main",
    "bucket": 5,
    "bucketName": "Elevated Launches & Cliffs",
    "year": "JEE Main 2024 (Online) 29th January Morning Shift",
    "q": "A ball rolls off the top of a stairway with horizontal velocity u . The steps are 0.1m high and 0.1m wide. The minimum velocity u with which that ball just hits the step 5 of the stairway will be sqrtxms−1 where x= __________ [use g=10m/s2 ].",
    "tab": "topic6",
    "formula": "x ≥ (n-1) w,  y = (n-1) h,  t = √(2y/g),  u = x / t",
    "steps": [
      "Steps are 0.1 m high and 0.1 m wide.",
      "To hit step 5, the ball must clear step 4: x ≥ 4 &times; 0.1 = 0.4 m, and vertical drop y = 4 &times; 0.1 = 0.4 m.",
      "Time to drop 0.4 m: t = √(2y / g) = √(2 &times; 0.4 / 10) = √0.08 s.",
      "Minimum horizontal speed: u = x / t = 0.4 / √0.08 = √(0.16 / 0.08) = √2 m/s.",
      "Given u = √x &rArr; x = 2."
    ],
    "ans": "x = 2",
    "takeaway": "Discrete boundary collisions require clearing the corner of the preceding step."
  },
  {
    "id": "EXAM-80",
    "num": "JEE Q7",
    "source": "ExamSide JEE Main",
    "bucket": 1,
    "bucketName": "Orthogonal Kinematics & Coordinates",
    "year": "JEE Main 2024 (Online) 27th January Morning Shift",
    "q": "A particle starts from origin at t=0 with a velocity 5iˆm/s and moves in x−y plane under action of a force which produces a constant acceleration of (3iˆ+2jˆ)m/s2 . If the x -coordinate of the particle at that instant is 84m , then the speed of the particle at this time is sqrtαm/s . The value of α is _________.",
    "tab": "topic1",
    "formula": "x(t) = v₀x t + ½ a_x t²,  v_x = v₀x + a_x t,  v_y = a_y t",
    "steps": [
      "Given v₀→ = 5 î m/s and a→ = (3 î + 2 ĵ) m/s².",
      "Horizontal position: x(t) = 5t + ½(3)t² = 84 &rArr; 1.5t² + 5t - 84 = 0 &rArr; 3t² + 10t - 168 = 0.",
      "Factor: (3t + 28)(t - 6) = 0 &rArr; t = 6 s.",
      "Velocities at t = 6 s: v_x = 5 + 3(6) = 23 m/s; v_y = 0 + 2(6) = 12 m/s.",
      "Speed squared α = v_x² + v_y² = 23² + 12² = 529 + 144 = 673 &rArr; speed = √673 m/s &rArr; α = 673."
    ],
    "ans": "α = 673",
    "takeaway": "Solve time from the constrained coordinate, then substitute into both velocity components."
  },
  {
    "id": "EXAM-81",
    "num": "JEE Q8",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2023 (Online) 11th April Morning Shift",
    "q": "A projectile fired at 30∘ to the ground is observed to be at same height at time 3s and 5s after projection, during its flight. The speed of projection of the projectile is ___________ ms−1 . (Given g=10ms−2 )",
    "tab": "topic2",
    "formula": "t₁ + t₂ = T = (2u sin θ) / g",
    "steps": [
      "A projectile reaches any given height h twice: once ascending at t₁ and once descending at t₂.",
      "By parabolic time symmetry: t₁ + t₂ = T (total time of flight).",
      "Given t₁ = 3 s and t₂ = 5 s &rArr; T = 3 + 5 = 8 s.",
      "Time of flight formula: T = (2u sin 30°) / g = [2u(0.5)] / 10 = u / 10.",
      "Equate: u / 10 = 8 &rArr; u = 80 m/s."
    ],
    "ans": "80 m/s",
    "takeaway": "The sum of arrival times at any equal altitude equals the total flight time: t₁ + t₂ = T."
  },
  {
    "id": "EXAM-82",
    "num": "JEE Q9",
    "source": "ExamSide JEE Main",
    "bucket": 4,
    "bucketName": "Complementary Symmetries & Invariants",
    "year": "JEE Main 2023 (Online) 31st January Evening Shift",
    "q": "Two bodies are projected from ground with same speeds 40ms−1 at two different angles with respect to horizontal. The bodies were found to have same range. If one of the body was projected at an angle of 60∘ , with horizontal then sum of the maximum heights, attained by the two projectiles, is m . (Given g=10ms−2 )",
    "tab": "topic5",
    "formula": "H₁ + H₂ = u² / (2g)",
    "steps": [
      "For complementary launch angles: H₁ = (u² sin² θ) / (2g), H₂ = (u² cos² θ) / (2g).",
      "Sum: H₁ + H₂ = [u² (sin² θ + cos² θ)] / (2g) = u² / (2g).",
      "Notice that the sum is completely independent of the angle θ!",
      "Substitute u = 40 m/s and g = 10 m/s²: H₁ + H₂ = 40² / [2(10)] = 1600 / 20 = 80 m."
    ],
    "ans": "80 m",
    "takeaway": "Sum of complementary apex heights is constant: H₁ + H₂ = u²/(2g)."
  },
  {
    "id": "EXAM-83",
    "num": "JEE Q10",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2023 (Online) 31st January Morning Shift",
    "q": "The speed of a swimmer is 4kmh−1 in still water. If the swimmer makes his strokes normal to the flow of river of width 1km , he reaches a point 750m down the stream on the opposite bank. The speed of the river water is ___________ kmh−1",
    "tab": "relative",
    "formula": "t = d / v_s,  x = v_r t",
    "steps": [
      "Swimmer speed in still water v_s = 4 km/h, width d = 1 km.",
      "Strokes made normal to flow &rArr; crossing time t = d / v_s = 1 km / (4 km/h) = 0.25 hr = 15 min.",
      "Downstream drift x = 750 m = 0.75 km.",
      "River flow speed: v_r = x / t = 0.75 km / 0.25 hr = 3 km/h."
    ],
    "ans": "3 km/h",
    "takeaway": "When steering normal to banks, drift is purely the product of river flow velocity and crossing time."
  },
  {
    "id": "EXAM-84",
    "num": "JEE Q11",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 29th July Morning Shift",
    "q": "An object is projected in the air with initial velocity u at an angle θ . The projectile motion is such that the horizontal range R, is maximum. Another object is projected in the air with a horizontal range half of the range of first object. The initial velocity remains same in both the case. The value of the angle of projection, at which the second object is projected, will be _________ degree.",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-85",
    "num": "JEE Q12",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 27th July Morning Shift",
    "q": "A ball of mass m is thrown vertically upward. Another ball of mass 2m is thrown at an angle θ with the vertical. Both the balls stay in air for the same period of time. The ratio of the heights attained by the two balls respectively is 1x . The value of x is _____________.",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-86",
    "num": "JEE Q13",
    "source": "ExamSide JEE Main",
    "bucket": 3,
    "bucketName": "Trajectory Equations & Geometry",
    "year": "JEE Main 2022 (Online) 26th July Morning Shift",
    "q": "If the initial velocity in horizontal direction of a projectile is unit vector iˆ and the equation of trajectory is y=5x(1−x) . The y component vector of the initial velocity is ______________ jˆ . ( Take g=10m/s2)",
    "tab": "topic3",
    "formula": "y = 5x - 5x² &rArr; dy/dx = tan θ = 5 - 10x",
    "steps": [
      "Given initial horizontal velocity u_x = 1 m/s (from î).",
      "Trajectory y = 5x(1 - x) = 5x - 5x².",
      "Slope at launch (x = 0): dy/dx = tan θ = 5.",
      "Initial vertical velocity component: u_y = u_x tan θ = 1 &times; 5 = 5 m/s.",
      "Vector form: u_y ĵ = 5 ĵ."
    ],
    "ans": "5 ĵ",
    "takeaway": "Initial slope dy/dx at origin equals tan θ = u_y / u_x."
  },
  {
    "id": "EXAM-87",
    "num": "JEE Q14",
    "source": "ExamSide JEE Main",
    "bucket": 6,
    "bucketName": "Dynamic Tracking & Interception",
    "year": "JEE Main 2022 (Online) 26th June Morning Shift",
    "q": "A fighter jet is flying horizontally at a certain altitude with a speed of 200 ms − 1 . When it passes directly overhead an anti-aircraft gun, a bullet is fired from the gun, at an angle θ with the horizontal, to hit the jet. If the bullet speed is 400 m/s, the value of θ will be ___________ ∘ .",
    "tab": "topic6",
    "formula": "v_bullet cos θ = v_jet",
    "steps": [
      "Fighter jet flies horizontally at constant speed v_jet = 200 m/s overhead.",
      "Bullet fired with speed v_bullet = 400 m/s at angle θ with horizontal to hit jet.",
      "For interception in the vertical line of sight, horizontal velocities must match so horizontal separation remains zero.",
      "Condition: v_bullet cos θ = v_jet &rArr; 400 cos θ = 200 &rArr; cos θ = 1/2.",
      "Solve: θ = 60°."
    ],
    "ans": "θ = 60°",
    "takeaway": "Interception in a plane requires matching velocity components along the invariant tracking axis."
  },
  {
    "id": "EXAM-88",
    "num": "JEE Q15",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2022 (Online) 24th June Evening Shift",
    "q": "A body is projected from the ground at an angle of 45 ∘ with the horizontal. Its velocity after 2s is 20 ms − 1 . The maximum height reached by the body during its motion is __________ m. (use g = 10 ms − 2 )",
    "tab": "topic2",
    "formula": "T = (2u sin θ)/g,  H = (u² sin² θ)/(2g),  R = (u² sin 2θ)/g,  R tan θ = 4H",
    "steps": [
      "Apply the fundamental ground-to-ground equations: T = 2u_y/g, H = u_y²/(2g), R = 2u_x u_y/g.",
      "Use the 4H identity R tan θ = 4H to connect range, apex height, and angle.",
      "Calculate requested parameter by substituting known values."
    ],
    "ans": "Direct application of projectile formulas",
    "takeaway": "Ground-to-ground projectile motion is completely characterized by initial velocity components."
  },
  {
    "id": "EXAM-89",
    "num": "JEE Q16",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2021 (Online) 27th July Evening Shift",
    "q": "A swimmer wants to cross a river from point A to point B. Line AB makes an angle of 30 ∘ with the flow of river. Magnitude of velocity of the swimmer is same as that of the river. The angle θ with the line AB should be _________ ∘ , so that the swimmer reaches point B.",
    "tab": "relative",
    "formula": "t = d / (v_b cos θ),  drift x = (v_r - v_b sin θ) t",
    "steps": [
      "Decompose boat/swimmer velocity into perpendicular component (crossing) and parallel component (drift).",
      "Crossing time is determined solely by perpendicular component: t = d / v_y.",
      "Drift along bank is determined by net parallel speed: x = (v_r + v_bx) t."
    ],
    "ans": "River-boat kinematic decomposition",
    "takeaway": "River flow affects only downstream drift, never crossing speed when steering perpendicular."
  },
  {
    "id": "EXAM-90",
    "num": "JEE Q17",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2021 (Online) 18th March Morning Shift",
    "q": "A person is swimming with a speed of 10 m/s at an angle of 120 ∘ with the flow and reaches to a point directly opposite on the other side of the river. The speed of the flow is 'x' m/s. The value of 'x' to the nearest integer is __________.",
    "tab": "relative",
    "formula": "t = d / (v_b cos θ),  drift x = (v_r - v_b sin θ) t",
    "steps": [
      "Decompose boat/swimmer velocity into perpendicular component (crossing) and parallel component (drift).",
      "Crossing time is determined solely by perpendicular component: t = d / v_y.",
      "Drift along bank is determined by net parallel speed: x = (v_r + v_bx) t."
    ],
    "ans": "River-boat kinematic decomposition",
    "takeaway": "River flow affects only downstream drift, never crossing speed when steering perpendicular."
  },
  {
    "id": "EXAM-91",
    "num": "JEE Q18",
    "source": "ExamSide JEE Main",
    "bucket": 8,
    "bucketName": "River-Boat & Aerial Navigation",
    "year": "JEE Main 2021 (Online) 16th March Evening Shift",
    "q": "A swimmer can swim with velocity of 12 km/h in still water. Water flowing in a river has velocity 6 km/h. The direction with respect to the direction of flow of river water he should swim in order to reach the point on the other bank just opposite to his starting point is ____________ ∘ . (Round off to the Nearest Integer) (Find the angle in degrees)",
    "tab": "relative",
    "formula": "t = d / (v_b cos θ),  drift x = (v_r - v_b sin θ) t",
    "steps": [
      "Decompose boat/swimmer velocity into perpendicular component (crossing) and parallel component (drift).",
      "Crossing time is determined solely by perpendicular component: t = d / v_y.",
      "Drift along bank is determined by net parallel speed: x = (v_r + v_bx) t."
    ],
    "ans": "River-boat kinematic decomposition",
    "takeaway": "River flow affects only downstream drift, never crossing speed when steering perpendicular."
  },
  {
    "id": "EXAM-92",
    "num": "JEE Q1 (Num)",
    "source": "ExamSide JEE Main",
    "bucket": 2,
    "bucketName": "Ground Projectile Fundamentals",
    "year": "JEE Main 2026 (Online) 4th April Evening Shift",
    "q": "A gun mounted on the ground fires bullets in all directions with same speed. The farthest distance the bullets could reach is 6.4 m. The speed of the bullets from the gun is ____ m/s. (take g=10 m/s2)",
    "tab": "topic2",
    "formula": "R_max = u² / g",
    "steps": [
      "Farthest distance on flat ground corresponds to maximum horizontal range R_max at θ = 45°.",
      "Formula: R_max = u² / g &rArr; 6.4 = u² / 10.",
      "Solve: u² = 64 &rArr; u = 8 m/s."
    ],
    "ans": "8 m/s",
    "takeaway": "Maximum ground range is R_max = u²/g."
  },
  {
    "id": "EXAM-93",
    "num": "JEE Q19 (Num)",
    "source": "ExamSide JEE Main",
    "bucket": 7,
    "bucketName": "2D Relative Velocity & Frames",
    "year": "JEE Main 2020 (Online) 8th January Morning Slot",
    "q": "A particle is moving along the x-axis with its coordinate with the time t given by x(t) = 10 + 8t - 3t^2. Another particle is moving along the y-axis with its coordinate as a function of time given by y(t) = 5 - 8t^3. At t = 1s, the speed of the second particle as measured in the frame of the first particle is given as sqrt(v). Then v (in m/s) is ______.",
    "tab": "relative",
    "formula": "v→_B/A = v→_B - v→_A",
    "steps": [
      "Calculate individual velocities in ground frame.",
      "Apply Galilean vector subtraction v_B/A = v_B - v_A.",
      "Find relative magnitude and direction."
    ],
    "ans": "Galilean vector subtraction",
    "takeaway": "Bringing an observer to rest by applying -v_obs simplifies relative motion analysis."
  }
];
