/**
 * Behaviour of Gases & States of Matter
 * Master Question Registry & Step-by-Step Solutions Database
 * Curated from ExamSIDE IIT-JEE Main Questions (2013-2026)
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "GAS-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 4th April Morning Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor Z vs P",
    "year": "2026",
    "q": "For one mole of a van der Waals gas at low pressure, the compressibility factor Z is expressed as:",
    "options": [
      {
        "key": "A",
        "text": "Z = 1 - a / (R T V_m)"
      },
      {
        "key": "B",
        "text": "Z = 1 + P b / (R T)"
      },
      {
        "key": "C",
        "text": "Z = 1 + a / (R T V_m)"
      },
      {
        "key": "D",
        "text": "Z = 1 - P b / (R T)"
      }
    ],
    "correct": "A",
    "formula": "(P + a/V_m²)(V_m - b) = R T. At low pressure, V_m >> b ⇒ V_m - b ≈ V_m",
    "steps": [
      "Step 1: Start from the van der Waals equation for 1 mole: (P + a/V_m²)(V_m - b) = RT.",
      "Step 2: At low pressure, the molar volume V_m is very large compared to the molecular excluded volume b: (V_m - b) ≈ V_m.",
      "Step 3: The equation reduces to: (P + a/V_m²) V_m = RT ⇒ P V_m + a / V_m = RT.",
      "Step 4: Divide both sides by RT: (P V_m) / (RT) + a / (RT V_m) = 1.",
      "Step 5: Since Z = (P V_m) / (RT), we obtain: Z = 1 - a / (RT V_m).",
      "Step 6: Since a, R, T, V_m > 0, Z < 1 at low to moderate pressures due to predominant attractive forces!"
    ],
    "ans": "Z = 1 - a / (R T V_m) (Option A)",
    "trap": "Option B applies at very HIGH pressure (where repulsive forces dominate and excluded volume b cannot be neglected)!",
    "distractorTraps": {
      "B": "This is the high-pressure approximation where P(V - b) = RT ⇒ Z = 1 + Pb/RT.",
      "C": "Sign error: attractive forces decrease effective pressure, leading to Z < 1, not Z > 1.",
      "D": "Inverted both sign and volume correction."
    },
    "targetTab": "tab-compressibility",
    "simParams": {
      "tempK": 300
    },
    "simSummary": [
      "Low Pressure Regime",
      "V_m >> b ⇒ (V_m - b) ≈ V_m",
      "Z = 1 - a/(RTV_m) < 1",
      "Attractive Forces Dominant"
    ],
    "sourceAudit": "SOURCE_UNVERIFIED",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.tempK"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds tempK only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "ExamSIDE currently reports zero JEE Main Gaseous State questions in 2026 and labels the chapter out of syllabus; this 2026 attribution is therefore inconsistent with the live corpus snapshot.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Z = 1 - a / (R T V_m) (Option A).",
    "takeaway": "Transfer rule: start from (P + a/V_m²)(V_m - b) = R T; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q02",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 29th January Evening Shift",
    "subtab": 5,
    "subtabName": "Critical Constants & Liquefaction",
    "year": "2025",
    "q": "The van der Waals constant 'a' for four gases are: Gas W = 4.17, Gas X = 0.244, Gas Y = 1.36, and Gas Z = 2.25 (in atm L² mol⁻²). The gas that can be most easily liquefied is:",
    "options": [
      {
        "key": "A",
        "text": "Gas W"
      },
      {
        "key": "B",
        "text": "Gas X"
      },
      {
        "key": "C",
        "text": "Gas Y"
      },
      {
        "key": "D",
        "text": "Gas Z"
      }
    ],
    "correct": "A",
    "formula": "Critical Temperature T_c = 8a / (27 R b). Ease of liquefaction ∝ intermolecular attraction ∝ a",
    "steps": [
      "Step 1: The van der Waals constant 'a' represents the magnitude of attractive intermolecular forces between gas molecules.",
      "Step 2: A higher value of 'a' implies stronger attractive forces, which holds gas molecules together more readily to form a liquid.",
      "Step 3: The critical temperature T_c = 8a / (27 R b). Higher 'a' results in a higher critical temperature, meaning the gas can be liquefied at higher temperatures with less cooling.",
      "Step 4: Comparing values: Gas W (a = 4.17) > Gas Z (2.25) > Gas Y (1.36) > Gas X (0.244).",
      "Step 5: Therefore, Gas W (which corresponds to NH₃) is the most easily liquefied."
    ],
    "ans": "Gas W (Option A)",
    "trap": "Do not confuse constant 'a' (attraction) with constant 'b' (molecular size / repulsion)!",
    "distractorTraps": {
      "B": "Gas X has the lowest 'a' (like He), making it the most DIFFICULT to liquefy.",
      "C": "Intermediate value chosen arbitrarily.",
      "D": "Gas Z has second highest 'a', but W is significantly higher."
    },
    "targetTab": "tab-isotherms",
    "simParams": {},
    "simSummary": [
      "Gas W: a = 4.17 atm L²/mol²",
      "Maximum Critical Temperature T_c",
      "Most easily liquefied"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Gas W (Option A).",
    "takeaway": "Transfer rule: start from Critical Temperature T_c = 8a / (27 R b); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q03",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 30th January Morning Shift",
    "subtab": 2,
    "subtabName": "Maxwell-Boltzmann Speed Distribution",
    "year": "2024",
    "q": "The ratio of the most probable speed (v_mp), average speed (v_avg), and root mean square speed (v_rms) of gas molecules at temperature T is:",
    "options": [
      {
        "key": "A",
        "text": "1 : 1.128 : 1.224"
      },
      {
        "key": "B",
        "text": "1 : 1.224 : 1.128"
      },
      {
        "key": "C",
        "text": "1.224 : 1.128 : 1"
      },
      {
        "key": "D",
        "text": "1 : 1 : 1"
      }
    ],
    "correct": "A",
    "formula": "v_mp = √(2RT/M),  v_avg = √(8RT/πM),  v_rms = √(3RT/M)",
    "steps": [
      "Step 1: Write explicit formulas for molecular speeds: v_mp = √(2RT/M), v_avg = √(8RT/πM), v_rms = √(3RT/M).",
      "Step 2: Factor out √(RT/M): Ratio v_mp : v_avg : v_rms = √2 : √(8/π) : √3.",
      "Step 3: Evaluate numerical square roots: √2 ≈ 1.414. √(8/π) = √(8/3.1416) = √2.546 ≈ 1.596. √3 ≈ 1.732.",
      "Step 4: Normalize by dividing by √2 (1.414): 1.414/1.414 : 1.596/1.414 : 1.732/1.414 = 1 : 1.128 : 1.224.",
      "Step 5: Note the universal strict inequality: v_mp < v_avg < v_rms (Remember mnemonic: RAM in reverse)."
    ],
    "ans": "1 : 1.128 : 1.224 (Option A)",
    "trap": "Students frequently invert the order of v_avg and v_rms. Remember: v_rms is always the largest!",
    "distractorTraps": {
      "B": "Inverted v_avg and v_rms.",
      "C": "Reversed the ratio from highest to lowest.",
      "D": "Assumed all speed metrics are identical."
    },
    "targetTab": "tab-maxwell",
    "simParams": {
      "tempK": 300
    },
    "simSummary": [
      "v_mp = √(2RT/M)",
      "v_avg = √(8RT/πM)",
      "v_rms = √(3RT/M)",
      "Ratio: 1 : 1.128 : 1.224"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.tempK"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds tempK only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 1 : 1.128 : 1.224 (Option A).",
    "takeaway": "Transfer rule: start from v_mp = √(2RT/M),  v_avg = √(8RT/πM),  v_rms = √(3RT/M); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q04",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 27th January Morning Shift",
    "subtab": 3,
    "subtabName": "Real Gas Constants & Excluded Volume",
    "year": "2025",
    "q": "The effective excluded volume 'b' for 1 mole of a gas having spherical molecules of radius 'r' is equal to:",
    "options": [
      {
        "key": "A",
        "text": "4 × N_A × (4/3 π r³)"
      },
      {
        "key": "B",
        "text": "N_A × (4/3 π r³)"
      },
      {
        "key": "C",
        "text": "8 × N_A × (4/3 π r³)"
      },
      {
        "key": "D",
        "text": "2 × N_A × (4/3 π r³)"
      }
    ],
    "correct": "A",
    "formula": "b = 4 × N_A × V_molecule. For a colliding pair, excluded sphere radius is 2r ⇒ volume is 8 × V_m / 2 = 4 V_m",
    "steps": [
      "Step 1: When two spherical molecules of radius r collide, the distance between their centers cannot be less than 2r.",
      "Step 2: Thus, the sphere of exclusion for a pair of molecules has radius R = 2r.",
      "Step 3: Volume of the exclusion sphere for a pair = 4/3 π (2r)³ = 8 × (4/3 π r³).",
      "Step 4: Since this exclusion sphere belongs to TWO molecules, the excluded volume PER MOLECULE = ½ × 8 × (4/3 π r³) = 4 × (4/3 π r³).",
      "Step 5: For 1 mole (N_A molecules), total excluded volume b = 4 × N_A × (4/3 π r³) = 4 × (Actual volume of molecules)."
    ],
    "ans": "4 × N_A × (4/3 π r³) (Option A)",
    "trap": "The #1 trap in Gaseous State: thinking excluded volume b is equal to the actual volume of the molecules (factor of 4 missing)!",
    "distractorTraps": {
      "B": "Assumed excluded volume equals the physical atomic volume without pair-exclusion factor of 4.",
      "C": "Forgot to divide the pair volume by 2.",
      "D": "Arbitrary factor of 2."
    },
    "targetTab": "tab-real-particle",
    "simParams": {},
    "simSummary": [
      "Collision Diameter = 2r",
      "Pair Exclusion Volume = 8 × V_m",
      "Excluded Volume per Molecule = 4 × V_m",
      "b = 4 × N_A × V_m"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 4 × N_A × (4/3 π r³) (Option A).",
    "takeaway": "Transfer rule: start from b = 4 × N_A × V_molecule; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q05",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 1st February Evening Shift",
    "subtab": 6,
    "subtabName": "Graham's Law of Effusion",
    "year": "2024",
    "q": "Under identical conditions of temperature and pressure, 50 mL of gas A effuses through a pinhole in 20 seconds, while 40 mL of O₂ effuses in 40 seconds. The molar mass of gas A is:",
    "options": [
      {
        "key": "A",
        "text": "5.12 g/mol"
      },
      {
        "key": "B",
        "text": "12.8 g/mol"
      },
      {
        "key": "C",
        "text": "20.0 g/mol"
      },
      {
        "key": "D",
        "text": "16.0 g/mol"
      }
    ],
    "correct": "A",
    "formula": "Rate of effusion r = V / t.  r_A / r_O₂ = √(M_O₂ / M_A)",
    "steps": [
      "Step 1: Compute rate of effusion of gas A: r_A = 50 mL / 20 s = 2.50 mL/s.",
      "Step 2: Compute rate of effusion of O₂: r_O₂ = 40 mL / 40 s = 1.00 mL/s.",
      "Step 3: Apply Graham's Law: r_A / r_O₂ = √(M_O₂ / M_A).",
      "Step 4: Substitute values: 2.50 / 1.00 = √(32 / M_A).",
      "Step 5: Square both sides: 6.25 = 32 / M_A ⇒ M_A = 32 / 6.25 = 5.12 g/mol."
    ],
    "ans": "5.12 g/mol (Option A)",
    "trap": "Rate is Volume / Time (mL/s); do not compare times directly without normalizing for different diffused volumes!",
    "distractorTraps": {
      "B": "Inverted time ratio: (20/40) × 32 = 16 or missed squaring.",
      "C": "Compared times directly: (20/40)² × 32 = 8.",
      "D": "Assumed Gas A was methane (16 g/mol)."
    },
    "targetTab": "tab-effusion",
    "simParams": {},
    "simSummary": [
      "Rate A = 2.50 mL/s",
      "Rate O₂ = 1.00 mL/s",
      "Ratio = 2.50",
      "M_A = 32 / (2.5)² = 5.12 g/mol"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 5.12 g/mol (Option A).",
    "takeaway": "Transfer rule: start from Rate of effusion r = V / t; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q06",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 5th April Evening Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor Z vs P",
    "year": "2026",
    "q": "At the Boyle temperature (T_B), a real gas behaves like an ideal gas over an appreciable range of pressure. The mathematical expression for Boyle temperature in terms of van der Waals constants is:",
    "options": [
      {
        "key": "A",
        "text": "T_B = a / (R b)"
      },
      {
        "key": "B",
        "text": "T_B = 2a / (R b)"
      },
      {
        "key": "C",
        "text": "T_B = 8a / (27 R b)"
      },
      {
        "key": "D",
        "text": "T_B = a / (27 R b²)"
      }
    ],
    "correct": "A",
    "formula": "At T_B, initial slope (∂Z/∂P)_{P→0} = 0 ⇒ b - a/(RT) = 0 ⇒ T_B = a / (Rb)",
    "steps": [
      "Step 1: The virial expansion of the van der Waals equation gives: Z = 1 + (b - a/(RT))(1/V_m) + ...",
      "Step 2: For the gas to obey ideal gas behavior as P → 0, the second virial coefficient must vanish: b - a / (RT) = 0.",
      "Step 3: Solving for temperature: RT = a / b ⇒ T_B = a / (Rb).",
      "Step 4: Note related landmarks: Inversion temperature T_i = 2a / (Rb) = 2 T_B. Critical temperature T_c = 8a / (27 Rb)."
    ],
    "ans": "T_B = a / (R b) (Option A)",
    "trap": "Option B is the Inversion Temperature (T_i = 2a/Rb); Option C is the Critical Temperature (T_c = 8a/27Rb)!",
    "distractorTraps": {
      "B": "Confused with Inversion temperature T_i = 2a/(Rb).",
      "C": "Confused with Critical temperature T_c = 8a/(27Rb).",
      "D": "Confused with Critical pressure P_c = a/(27b²)."
    },
    "targetTab": "tab-compressibility",
    "simParams": {},
    "simSummary": [
      "Boyle Temperature T_B = a / (Rb)",
      "Second Virial Coefficient B₂ = b - a/(RT) = 0",
      "(∂Z/∂P)_{P→0} = 0"
    ],
    "sourceAudit": "SOURCE_UNVERIFIED",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "ExamSIDE currently reports zero JEE Main Gaseous State questions in 2026 and labels the chapter out of syllabus; this 2026 attribution is therefore inconsistent with the live corpus snapshot.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select T_B = a / (R b) (Option A).",
    "takeaway": "Transfer rule: start from At T_B, initial slope (∂Z/∂P)_{P→0} = 0 ⇒ b - a/(RT) = 0 ⇒ T_B = a / (Rb); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q07",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 25th January Morning Shift",
    "subtab": 5,
    "subtabName": "Andrews Isotherms & Critical State",
    "year": "2023",
    "q": "The critical constants of a van der Waals gas are P_c = a / (27 b²), V_c = 3 b, and T_c = 8 a / (27 R b). The value of the critical compressibility factor Z_c = (P_c V_c) / (R T_c) for any van der Waals gas is:",
    "options": [
      {
        "key": "A",
        "text": "0.375 (or 3/8)"
      },
      {
        "key": "B",
        "text": "0.280"
      },
      {
        "key": "C",
        "text": "1.000"
      },
      {
        "key": "D",
        "text": "0.750"
      }
    ],
    "correct": "A",
    "formula": "Z_c = (P_c V_c) / (R T_c) = [ (a / 27b²) · (3b) ] / [ R · (8a / 27Rb) ] = 3/8 = 0.375",
    "steps": [
      "Step 1: Write critical parameters in terms of van der Waals constants: P_c = a / (27b²), V_c = 3b, T_c = 8a / (27Rb).",
      "Step 2: Form the critical compressibility ratio: Z_c = (P_c V_c) / (R T_c).",
      "Step 3: Substitute expressions: Z_c = [ (a / 27b²) × 3b ] / [ R × 8a / (27Rb) ] = (3a / 27b) / (8a / 27b) = 3/8.",
      "Step 4: Express in decimals: 3/8 = 0.375. This is a universal invariant for all fluids obeying the van der Waals equation."
    ],
    "ans": "0.375 (or 3/8) (Option A)",
    "trap": "Never assume Z = 1 at the critical point! Intermolecular attractions and co-volume effects are maximized near the liquid-gas coexistence dome, driving Z_c down to 0.375.",
    "distractorTraps": {
      "B": "Confused with Berthelot model compressibility.",
      "C": "Assumed ideal gas equation applies at the critical point.",
      "D": "Inverted the numerator factor 3/8 into 6/8 = 0.75."
    },
    "targetTab": "tab-isotherms",
    "simParams": {},
    "simSummary": [
      "P_c = a/(27b²)",
      "V_c = 3b",
      "T_c = 8a/(27Rb)",
      "Critical Invariant Z_c = 3/8 = 0.375"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 0.375 (or 3/8) (Option A).",
    "takeaway": "Transfer rule: start from Z_c = (P_c V_c) / (R T_c) = [ (a / 27b²) · (3b) ] / [ R · (8a / 27Rb) ] = 3/8 = 0; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q08",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 24th January Morning Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor Z vs P",
    "year": "2025",
    "q": "At very high pressure, the van der Waals equation for 1 mole of a real gas simplifies to which of the following linear forms for compressibility factor Z?",
    "options": [
      {
        "key": "A",
        "text": "Z = 1 + (P b) / (R T)"
      },
      {
        "key": "B",
        "text": "Z = 1 - a / (V R T)"
      },
      {
        "key": "C",
        "text": "Z = 1 - (P b) / (R T)"
      },
      {
        "key": "D",
        "text": "Z = 1 + a / (V R T)"
      }
    ],
    "correct": "A",
    "formula": "P >> a/V² ⇒ P(V_m - b) = RT ⇒ PV_m - Pb = RT ⇒ Z = PV_m / RT = 1 + Pb / (RT)",
    "steps": [
      "Step 1: At extremely high pressure, the attractive internal pressure term a/V² becomes negligible relative to external pressure P (P >> a/V²).",
      "Step 2: The equation reduces to P(V_m - b) = RT.",
      "Step 3: Expand the product: PV_m - Pb = RT ⇒ PV_m = RT + Pb.",
      "Step 4: Divide both sides by RT: Z = PV_m / (RT) = 1 + (Pb) / (RT).",
      "Step 5: Because b > 0 and P > 0, Z is strictly greater than 1, yielding a positive slope with pressure where repulsive forces dominate."
    ],
    "ans": "Z = 1 + (P b) / (R T) (Option A)",
    "trap": "At moderate/low pressure, attraction dominates giving Z = 1 - a/(VRT) < 1. At high pressure, repulsive exclusion volume b dominates giving Z = 1 + Pb/(RT) > 1.",
    "distractorTraps": {
      "B": "Formula for low-to-moderate pressure where attraction dominates.",
      "C": "Incorrect negative sign for repulsive co-volume term.",
      "D": "Inverted algebraic sign on attractive correction."
    },
    "targetTab": "tab-compressibility",
    "simParams": {},
    "simSummary": [
      "High Pressure Regime: P >> a/V²",
      "P(V - b) = RT",
      "Repulsive Excluded Volume Dominates",
      "Z = 1 + Pb/(RT) > 1"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Z = 1 + (P b) / (R T) (Option A).",
    "takeaway": "Transfer rule: start from P >> a/V² ⇒ P(V_m - b) = RT ⇒ PV_m - Pb = RT ⇒ Z = PV_m / RT = 1 + Pb / (RT); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q09",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Morning Shift",
    "subtab": 2,
    "subtabName": "Maxwell-Boltzmann Speed Distribution",
    "year": "2024",
    "q": "The ratio of the most probable speed (v_mp), average speed (v_avg), and root-mean-square speed (v_rms) of gas molecules at a given temperature is:",
    "options": [
      {
        "key": "A",
        "text": "1 : 1.128 : 1.224  (√2 : √(8/π) : √3)"
      },
      {
        "key": "B",
        "text": "1.224 : 1.128 : 1  (√3 : √(8/π) : √2)"
      },
      {
        "key": "C",
        "text": "1 : 1 : 1"
      },
      {
        "key": "D",
        "text": "1 : 1.224 : 1.128"
      }
    ],
    "correct": "A",
    "formula": "v_mp = √(2RT/M),  v_avg = √(8RT/πM),  v_rms = √(3RT/M)",
    "steps": [
      "Step 1: Write explicit expressions for molecular speeds from Maxwell-Boltzmann kinetic distribution:",
      "        v_mp = √(2RT/M) ≈ 1.414 √(RT/M)",
      "        v_avg = √(8RT/πM) ≈ √(2.546 RT/M) ≈ 1.596 √(RT/M)",
      "        v_rms = √(3RT/M) ≈ 1.732 √(RT/M)",
      "Step 2: Normalize by dividing each by v_mp = √(2RT/M):",
      "        v_mp / v_mp = 1.0",
      "        v_avg / v_mp = √(4 / π) ≈ 1.128",
      "        v_rms / v_mp = √(3 / 2) ≈ 1.224",
      "Step 3: The invariant speed hierarchy is strictly: v_mp < v_avg < v_rms, yielding ratio 1 : 1.128 : 1.224."
    ],
    "ans": "1 : 1.128 : 1.224  (√2 : √(8/π) : √3) (Option A)",
    "trap": "Notice the ordering: v_mp (peak of curve) is lowest, v_avg is intermediate, and v_rms is highest! The ratio is always in ascending order 1 : 1.128 : 1.224.",
    "distractorTraps": {
      "B": "Inverted the ratio in descending order (v_rms : v_avg : v_mp).",
      "C": "Assumed all molecular speed averages are identical.",
      "D": "Swapped v_avg and v_rms."
    },
    "targetTab": "tab-maxwell",
    "simParams": {},
    "simSummary": [
      "v_mp = √(2RT/M) [Peak]",
      "v_avg = √(8RT/πM)",
      "v_rms = √(3RT/M) [Highest]",
      "Ratio = 1 : 1.128 : 1.224"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 1 : 1.128 : 1.224  (√2 : √(8/π) : √3) (Option A).",
    "takeaway": "Transfer rule: start from v_mp = √(2RT/M),  v_avg = √(8RT/πM),  v_rms = √(3RT/M); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q10",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 30th January Morning Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor (Z vs P)",
    "year": "2024",
    "q": "At very high pressures, the van der Waals equation for 1 mole of a real gas reduces to the linear equation:",
    "options": [
      {
        "key": "A",
        "text": "Z = 1 + (Pb / RT)"
      },
      {
        "key": "B",
        "text": "Z = 1 - (a / VRT)"
      },
      {
        "key": "C",
        "text": "Z = 1 + (a / VRT)"
      },
      {
        "key": "D",
        "text": "Z = 1 - (Pb / RT)"
      }
    ],
    "correct": "A",
    "formula": "At high pressure, P >> a/V² ⇒ (P + a/V²)(V - b) = RT becomes P(V - b) = RT ⇒ PV = RT + Pb ⇒ Z = 1 + Pb/RT.",
    "steps": [
      "Step 1: Write van der Waals equation for 1 mole: (P + a/V²)(V - b) = RT.",
      "Step 2: At very high pressures, P is extremely large, so the attractive correction a/V² becomes negligible compared to P: (P + a/V²) ≈ P.",
      "Step 3: However, the volume V is compressed and approaches the molecular co-volume b, so (V - b) cannot be neglected.",
      "Step 4: Equation simplifies to: P(V - b) = RT ⇒ PV - Pb = RT.",
      "Step 5: Divide through by RT: (PV / RT) - (Pb / RT) = 1 ⇒ Z = 1 + (Pb / RT).",
      "Step 6: This explains why at high pressure, Z > 1 and increases linearly with pressure with slope b/RT!"
    ],
    "ans": "Z = 1 + (Pb / RT) (Option A)",
    "trap": "Notice the PLUS sign: Z = 1 + Pb/RT! A minus sign (Z = 1 - a/VRT) occurs only at LOW pressures where intermolecular attractions dominate.",
    "distractorTraps": {
      "B": "Low-pressure approximation where attraction dominates: Z = 1 - a/VRT.",
      "C": "Sign error on low-pressure attraction term.",
      "D": "Negative sign on the high-pressure repulsive co-volume term."
    },
    "targetTab": "tab-compressibility",
    "simParams": {},
    "simSummary": [
      "High pressure: P >> a/V²",
      "P(V - b) = RT ⇒ PV = RT + Pb",
      "Z = 1 + Pb/RT (Linear slope b/RT)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Z = 1 + (Pb / RT) (Option A).",
    "takeaway": "Transfer rule: start from At high pressure, P >> a/V² ⇒ (P + a/V²)(V - b) = RT becomes P(V - b) = RT ⇒ PV = RT + Pb ⇒ Z = 1 + Pb/RT; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q11",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 10th April Morning Shift",
    "subtab": 1,
    "subtabName": "The Ideal Gas Piston Engine",
    "year": "2023",
    "q": "A gas is collected over water at 27°C and a total pressure of 750 mm Hg. If the aqueous tension of water at 27°C is 24 mm Hg, the actual pressure exerted by the dry gas is:",
    "options": [
      {
        "key": "A",
        "text": "726 mm Hg"
      },
      {
        "key": "B",
        "text": "774 mm Hg"
      },
      {
        "key": "C",
        "text": "750 mm Hg"
      },
      {
        "key": "D",
        "text": "375 mm Hg"
      }
    ],
    "correct": "A",
    "formula": "P_dry gas = P_total - P_aqueous tension  (Dalton's Law of Partial Pressures)",
    "steps": [
      "Step 1: When a gas is collected over water by downward displacement, the gas becomes saturated with water vapor.",
      "Step 2: Total measured pressure is the sum of dry gas pressure and saturated water vapor pressure (aqueous tension):",
      "        P_total = P_dry gas + P_aqueous tension.",
      "Step 3: Solve for dry gas pressure: P_dry gas = P_total - P_aqueous tension.",
      "Step 4: Substitute given values: P_dry gas = 750 mm Hg - 24 mm Hg = 726 mm Hg.",
      "Step 5: In all subsequent ideal gas calculations (PV = nRT), the dry pressure 726 mm Hg must be used, not 750 mm Hg!"
    ],
    "ans": "726 mm Hg (Option A)",
    "trap": "Always SUBTRACT aqueous tension! Students often ADD aqueous tension (750 + 24 = 774 mm Hg), which violates Dalton's law.",
    "distractorTraps": {
      "B": "Added aqueous tension instead of subtracting: 750 + 24 = 774 mm Hg.",
      "C": "Ignored water vapor pressure entirely (moist gas fallacy).",
      "D": "Divided total pressure by 2."
    },
    "targetTab": "tab-ideal",
    "simParams": {},
    "simSummary": [
      "P_total = 750 mm Hg",
      "P_aqueous = 24 mm Hg",
      "P_dry = 750 - 24 = 726 mm Hg"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 726 mm Hg (Option A).",
    "takeaway": "Transfer rule: start from P_dry gas = P_total - P_aqueous tension  (Dalton's Law of Partial Pressures); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q12",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 29th January Evening Shift",
    "subtab": 6,
    "subtabName": "Graham's Effusion Orifice",
    "year": "2023",
    "q": "Under identical conditions of temperature and pressure, 50 mL of gas X effuses through a porous pinhole in 20 minutes, whereas 40 mL of oxygen gas (O₂) effuses in 10 minutes. The molar mass of gas X is:",
    "options": [
      {
        "key": "A",
        "text": "81.9 g/mol (≈ 82 g/mol)"
      },
      {
        "key": "B",
        "text": "32 g/mol"
      },
      {
        "key": "C",
        "text": "16 g/mol"
      },
      {
        "key": "D",
        "text": "64 g/mol"
      }
    ],
    "correct": "A",
    "formula": "Rate r = V / t. By Graham's Law: r_X / r_O2 = √(M_O2 / M_X)",
    "steps": [
      "Step 1: Compute effusion rate of gas X: r_X = V_X / t_X = 50 mL / 20 min = 2.5 mL/min.",
      "Step 2: Compute effusion rate of O₂: r_O2 = V_O2 / t_O2 = 40 mL / 10 min = 4.0 mL/min.",
      "Step 3: State Graham's Law of Effusion: r_X / r_O2 = √(M_O2 / M_X).",
      "Step 4: Substitute rates and molar mass of O₂ (32 g/mol):",
      "        2.5 / 4.0 = √(32 / M_X) ⇒ 5 / 8 = √(32 / M_X).",
      "Step 5: Square both sides: 25 / 64 = 32 / M_X.",
      "Step 6: Solve for M_X: M_X = (32 × 64) / 25 = 2048 / 25 = 81.92 g/mol ≈ 82 g/mol."
    ],
    "ans": "81.9 g/mol (≈ 82 g/mol) (Option A)",
    "trap": "RATE NORMALIZATION TRAP: Do not compare times directly without normalizing by volume! Rate is Volume/Time (50/20 vs 40/10).",
    "distractorTraps": {
      "B": "Assumed rate is identical to oxygen.",
      "C": "Inverted square root ratio.",
      "D": "Ignored volume difference and used only times (t_X / t_O2 = 2 ⇒ M = 32 × 4 = 128 or 64)."
    },
    "targetTab": "tab-effusion",
    "simParams": {},
    "simSummary": [
      "r_X = 50/20 = 2.5 mL/min",
      "r_O2 = 40/10 = 4.0 mL/min",
      "M_X = 32 × (4/2.5)² = 81.92 g/mol"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 81.9 g/mol (≈ 82 g/mol) (Option A).",
    "takeaway": "Transfer rule: start from Rate r = V / t; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q13",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 28th June Evening Shift",
    "subtab": 3,
    "subtabName": "Real Gas Particle Halos (Excluded Volume b)",
    "year": "2022",
    "q": "The excluded volume (van der Waals constant b) for a gas composed of spherical molecules of radius r is related to the actual molecular volume (V_m) by:",
    "options": [
      {
        "key": "A",
        "text": "b = 4 N_A V_m  (4 times the actual molecular volume)"
      },
      {
        "key": "B",
        "text": "b = N_A V_m"
      },
      {
        "key": "C",
        "text": "b = 2 N_A V_m"
      },
      {
        "key": "D",
        "text": "b = 8 N_A V_m"
      }
    ],
    "correct": "A",
    "formula": "Excluded volume per pair = (4/3) π (2r)³ = 8 V_m. Excluded volume per molecule = 8 V_m / 2 = 4 V_m.",
    "steps": [
      "Step 1: Consider two spherical molecules A and B, each of radius r.",
      "Step 2: The center of molecule B cannot approach closer than distance 2r from the center of molecule A during collision.",
      "Step 3: Therefore, the exclusion sphere around molecule A has radius 2r.",
      "Step 4: Volume of this exclusion sphere = (4/3) π (2r)³ = 8 × [(4/3) π r³] = 8 V_m.",
      "Step 5: This exclusion sphere is shared equally between the two colliding molecules, so excluded volume per single molecule = 8 V_m / 2 = 4 V_m.",
      "Step 6: For 1 mole of gas (N_A molecules): b = 4 N_A V_m = 4 N_A [(4/3) π r³]."
    ],
    "ans": "b = 4 N_A V_m  (4 times the actual molecular volume) (Option A)",
    "trap": "Why is it 4 and not 8? Because each collision involves A PAIR of molecules, so the 8 V_m excluded sphere is divided by 2 per molecule!",
    "distractorTraps": {
      "B": "Assumed excluded volume equals the physical molecular volume (ignoring collision kinematics).",
      "C": "Divided by 4 instead of 2.",
      "D": "Forgot to divide the 8 V_m pair exclusion sphere by 2."
    },
    "targetTab": "tab-real-particle",
    "simParams": {},
    "simSummary": [
      "Exclusion sphere radius = 2r",
      "Exclusion volume per pair = 8 V_m",
      "b = 4 N_A V_m (4× actual volume)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select b = 4 N_A V_m  (4 times the actual molecular volume) (Option A).",
    "takeaway": "Transfer rule: start from Excluded volume per pair = (4/3) π (2r)³ = 8 V_m; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q14",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 24th June Morning Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor (Z vs P)",
    "year": "2022",
    "q": "For which of the following gases is the compressibility factor Z strictly greater than 1 (Z > 1) at ALL pressures at room temperature?",
    "options": [
      {
        "key": "A",
        "text": "H₂ and He"
      },
      {
        "key": "B",
        "text": "CH₄ and CO₂"
      },
      {
        "key": "C",
        "text": "NH₃ and SO₂"
      },
      {
        "key": "D",
        "text": "N₂ and O₂"
      }
    ],
    "correct": "A",
    "formula": "For H₂ and He, intermolecular attractive forces are negligible (a ≈ 0) due to very small size and low polarizability ⇒ Z = 1 + Pb/RT > 1.",
    "steps": [
      "Step 1: H₂ and He are extremely light molecules with very few electrons (2 electrons each) and minimal polarizability.",
      "Step 2: Their intermolecular attractive forces are exceptionally weak, so van der Waals constant a ≈ 0.",
      "Step 3: When a ≈ 0, the van der Waals equation reduces to: P(V - b) = RT ⇒ Z = 1 + (Pb / RT).",
      "Step 4: Since P > 0, b > 0, and T > 0, the term Pb/RT is strictly positive at all pressures.",
      "Step 5: Hence, for H₂ and He, the curve of Z vs P never dips below 1.0 (no attractive minimum) and rises monotonically above 1.0 at all pressures."
    ],
    "ans": "H₂ and He (Option A)",
    "trap": "H₂ and He do not exhibit the typical dip (Z < 1) at room temperature because room temp (298 K) is far above their Boyle temperatures (T_B for H₂ is 110 K, He is 24 K)!",
    "distractorTraps": {
      "B": "CH₄ and CO₂ have strong dispersion/quadrupole forces, showing deep dips below Z = 1 at low P.",
      "C": "NH₃ and SO₂ have strong dipole-dipole attractions and easily liquefy (Z << 1).",
      "D": "N₂ and O₂ exhibit pronounced dips below Z = 1 at moderate pressures."
    },
    "targetTab": "tab-compressibility",
    "simParams": {},
    "simSummary": [
      "H₂ & He: a ≈ 0 at 298 K",
      "Z = 1 + Pb/RT > 1 at all pressures",
      "Room temp >> Boyle temp"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select H₂ and He (Option A).",
    "takeaway": "Transfer rule: start from For H₂ and He, intermolecular attractive forces are negligible (a ≈ 0) due to very small size and low polarizability ⇒ Z = 1 + Pb/RT > 1; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q15",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 16th March Evening Shift",
    "subtab": 4,
    "subtabName": "Compressibility Factor (Z vs P)",
    "year": "2021",
    "q": "The Boyle temperature (T_B) of a van der Waals gas is defined as the temperature at which the initial slope (dZ/dP)_{P→0} is zero. It is given by:",
    "options": [
      {
        "key": "A",
        "text": "T_B = a / (R b)"
      },
      {
        "key": "B",
        "text": "T_B = 8a / (27 R b)"
      },
      {
        "key": "C",
        "text": "T_B = 2a / (R b)"
      },
      {
        "key": "D",
        "text": "T_B = a / (2 R b)"
      }
    ],
    "correct": "A",
    "formula": "Z = 1 + (b - a/RT)(P/RT). Setting coefficient of P to zero: b - a/(RT_B) = 0 ⇒ T_B = a / (Rb).",
    "steps": [
      "Step 1: Write virial expansion of van der Waals equation: Z = 1 + B₂ P + B₃ P² + ...",
      "Step 2: Second virial coefficient B₂ = (b - a/RT) / RT.",
      "Step 3: At the Boyle temperature T_B, real gas obeys ideal gas law over an appreciable range of low pressures, meaning (dZ/dP)_{P→0} = B₂ = 0.",
      "Step 4: Set second virial coefficient to zero: b - a / (R T_B) = 0.",
      "Step 5: Solve for Boyle temperature: T_B = a / (R b).",
      "Step 6: Contrast with Critical temperature T_c = 8a / (27Rb) and Inversion temperature T_i = 2a / (Rb) = 2 T_B."
    ],
    "ans": "T_B = a / (R b) (Option A)",
    "trap": "Do not confuse Boyle temperature T_B = a/Rb with Critical temperature T_c = 8a/(27Rb) or Inversion temperature T_i = 2a/Rb!",
    "distractorTraps": {
      "B": "Critical temperature formula: T_c = 8a / (27Rb).",
      "C": "Joule-Thomson Inversion temperature formula: T_i = 2a / (Rb).",
      "D": "Half of Boyle temperature."
    },
    "targetTab": "tab-compressibility",
    "simParams": {},
    "simSummary": [
      "Boyle Temp: T_B = a / (Rb)",
      "Critical Temp: T_c = 8a / (27Rb)",
      "Inversion Temp: T_i = 2 T_B = 2a / (Rb)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select T_B = a / (R b) (Option A).",
    "takeaway": "Transfer rule: start from Z = 1 + (b - a/RT)(P/RT); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q16",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 20th July Morning Shift",
    "subtab": 5,
    "subtabName": "Andrews Isotherms & Critical State",
    "year": "2021",
    "q": "The value of the critical compressibility factor (Z_c = P_c V_c / R T_c) for any gas obeying the van der Waals equation is a universal constant equal to:",
    "options": [
      {
        "key": "A",
        "text": "3 / 8  (= 0.375)"
      },
      {
        "key": "B",
        "text": "8 / 3  (≈ 2.67)"
      },
      {
        "key": "C",
        "text": "1.00"
      },
      {
        "key": "D",
        "text": "2 / 3  (≈ 0.667)"
      }
    ],
    "correct": "A",
    "formula": "P_c = a / (27 b²),  V_c = 3 b,  T_c = 8 a / (27 R b) ⇒ Z_c = (P_c V_c) / (R T_c) = 3/8 = 0.375",
    "steps": [
      "Step 1: Write expressions for critical constants in terms of van der Waals parameters a and b:",
      "        Critical pressure: P_c = a / (27 b²)",
      "        Critical molar volume: V_c = 3 b",
      "        Critical temperature: T_c = 8 a / (27 R b)",
      "Step 2: Calculate product P_c V_c = [a / (27 b²)] × [3 b] = 3a / (27 b) = a / (9 b).",
      "Step 3: Calculate product R T_c = R × [8 a / (27 R b)] = 8 a / (27 b).",
      "Step 4: Compute critical compressibility factor:",
      "        Z_c = (P_c V_c) / (R T_c) = [a / (9 b)] / [8 a / (27 b)] = (1 / 9) × (27 / 8) = 27 / 72 = 3 / 8 = 0.375.",
      "Step 5: This 3/8 ratio is a fundamental universal invariant independent of the nature of the gas!"
    ],
    "ans": "3 / 8  (= 0.375) (Option A)",
    "trap": "Notice that Z_c = 0.375 is much less than 1.0! At the critical point, intermolecular forces cause massive volume collapse compared to an ideal gas.",
    "distractorTraps": {
      "B": "Inverted the ratio: 8/3 ≈ 2.67.",
      "C": "Assumed ideal gas behavior Z = 1 at the critical point.",
      "D": "Confused with 2/3."
    },
    "targetTab": "tab-isotherms",
    "simParams": {},
    "simSummary": [
      "P_c = a/27b², V_c = 3b, T_c = 8a/27Rb",
      "Z_c = (P_c V_c)/(R T_c) = 3/8 = 0.375",
      "Universal invariant"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 3 / 8  (= 0.375) (Option A).",
    "takeaway": "Transfer rule: start from P_c = a / (27 b²),  V_c = 3 b,  T_c = 8 a / (27 R b) ⇒ Z_c = (P_c V_c) / (R T_c) = 3/8 = 0; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q17",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 4th September Evening Shift",
    "subtab": 1,
    "subtabName": "The Ideal Gas Piston Engine",
    "year": "2020",
    "q": "Two flasks A and B of equal volume contain 1.0 g of H₂ and 1.0 g of O₂ respectively at the same temperature T. Which of the following statements regarding the total translational kinetic energy (E_trans) of the gases is correct?",
    "options": [
      {
        "key": "A",
        "text": "E_trans(H₂) is 16 times E_trans(O₂)"
      },
      {
        "key": "B",
        "text": "E_trans(H₂) equals E_trans(O₂)"
      },
      {
        "key": "C",
        "text": "E_trans(O₂) is 16 times E_trans(H₂)"
      },
      {
        "key": "D",
        "text": "E_trans(H₂) is 4 times E_trans(O₂)"
      }
    ],
    "correct": "A",
    "formula": "Total translational KE = (3/2) n R T = (3/2) (m / M) R T ∝ 1 / M for equal mass",
    "steps": [
      "Step 1: Total translational kinetic energy of an ideal gas is: E_trans = (3/2) n R T.",
      "Step 2: Note that kinetic energy PER MOLE is (3/2)RT, and PER MOLECULE is (3/2)k_B T (both depend only on T).",
      "Step 3: But here we have EQUAL MASSES (m = 1.0 g), not equal moles!",
      "Step 4: Moles of H₂: n(H₂) = 1.0 g / 2 g/mol = 0.50 mol.",
      "Step 5: Moles of O₂: n(O₂) = 1.0 g / 32 g/mol = 0.03125 mol.",
      "Step 6: Ratio of total kinetic energies: E(H₂) / E(O₂) = n(H₂) / n(O₂) = 0.50 / 0.03125 = 32 / 2 = 16."
    ],
    "ans": "E_trans(H₂) is 16 times E_trans(O₂) (Option A)",
    "trap": "KE PER MOLECULE is the same ((3/2)k_B T), but TOTAL KE depends on total moles! 1 g of H₂ contains 16 times more moles than 1 g of O₂, hence 16 times more total KE.",
    "distractorTraps": {
      "B": "Confused total kinetic energy with average kinetic energy PER MOLECULE ((3/2)k_B T).",
      "C": "Inverted molar mass ratio.",
      "D": "Took square root of molar mass ratio (√16 = 4), which applies to rms speed, not kinetic energy!"
    },
    "targetTab": "tab-ideal",
    "simParams": {},
    "simSummary": [
      "Per molecule KE = (3/2)k_B T (same for both)",
      "Total KE = (3/2) n R T ∝ moles",
      "E(H₂) = 16 × E(O₂)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select E_trans(H₂) is 16 times E_trans(O₂) (Option A).",
    "takeaway": "Transfer rule: start from Total translational KE = (3/2) n R T = (3/2) (m / M) R T ∝ 1 / M for equal mass; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q18",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 2nd September Morning Shift",
    "subtab": 5,
    "subtabName": "Andrews Isotherms & Critical State",
    "year": "2020",
    "q": "Under what condition can a gas be liquefied purely by applying mechanical pressure without cooling?",
    "options": [
      {
        "key": "A",
        "text": "Only when temperature T is at or below its critical temperature (T ≤ T_c)"
      },
      {
        "key": "B",
        "text": "At any temperature, provided the pressure applied is sufficiently high"
      },
      {
        "key": "C",
        "text": "Only when temperature T is above its Boyle temperature (T > T_B)"
      },
      {
        "key": "D",
        "text": "Only when pressure P is less than the critical pressure (P < P_c)"
      }
    ],
    "correct": "A",
    "formula": "Critical temperature T_c is the maximum temperature above which a gas CANNOT be liquefied, no matter how much pressure is applied.",
    "steps": [
      "Step 1: Thomas Andrews' experiments on CO₂ established the fundamental concept of critical temperature (T_c).",
      "Step 2: Above T_c, the thermal kinetic energy of the gas molecules (3/2 k_B T) is so intense that attractive intermolecular forces cannot hold molecules together in the liquid phase.",
      "Step 3: Even under enormous pressures exceeding thousands of atmospheres, a gas above T_c merely compresses into a dense supercritical fluid without undergoing a discrete phase transition into liquid.",
      "Step 4: Therefore, liquefaction by application of pressure alone is possible IF AND ONLY IF T ≤ T_c."
    ],
    "ans": "Only when temperature T is at or below its critical temperature (T ≤ T_c) (Option A)",
    "trap": "Common student intuition assumes ANY gas can be liquefied if you squeeze it hard enough. Physics disproves this: above T_c, no amount of pressure will liquefy a gas!",
    "distractorTraps": {
      "B": "Common misconception that infinite pressure always causes liquefaction.",
      "C": "Boyle temperature relates to ideal gas behavior, not liquefaction.",
      "D": "To liquefy, pressure must be AT LEAST equal to vapor pressure at that temperature."
    },
    "targetTab": "tab-isotherms",
    "simParams": {},
    "simSummary": [
      "T_c is the upper ceiling for liquefaction",
      "Above T_c: Supercritical fluid (no liquefaction)",
      "Liquefaction possible only when T ≤ T_c"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Only when temperature T is at or below its critical temperature (T ≤ T_c) (Option A).",
    "takeaway": "Transfer rule: start from Critical temperature T_c is the maximum temperature above which a gas CANNOT be liquefied, no matter how much pressure is applied; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q19",
    "num": "JEE Main 2019",
    "source": "JEE Main 2019 (Online) 9th April Evening Shift",
    "subtab": 3,
    "subtabName": "Real Gas Particle Halos (Excluded Volume b)",
    "year": "2019",
    "q": "The SI units of the van der Waals constants a and b respectively are:",
    "options": [
      {
        "key": "A",
        "text": "N m⁴ mol⁻²  and  m³ mol⁻¹"
      },
      {
        "key": "B",
        "text": "N m² mol⁻²  and  m³ mol⁻¹"
      },
      {
        "key": "C",
        "text": "N m⁴ mol⁻¹  and  m² mol⁻¹"
      },
      {
        "key": "D",
        "text": "atm L² mol⁻²  and  L mol⁻¹ (in CGS/practical units)"
      }
    ],
    "correct": "A",
    "formula": "Pressure correction: [a n² / V²] = [P] ⇒ [a] = [P] [V²] / [n²]. Volume correction: [n b] = [V] ⇒ [b] = [V] / [n].",
    "steps": [
      "Step 1: In the van der Waals equation: (P + an²/V²)(V - nb) = nRT.",
      "Step 2: By dimensional homogeneity, an²/V² must have dimensions of Pressure:",
      "        [a] = [P] [V]² / [n]² = (N m⁻²) (m³)² / (mol)² = N m⁻² m⁶ mol⁻² = N m⁴ mol⁻².",
      "Step 3: Similarly, nb must have dimensions of Volume:",
      "        [b] = [V] / [n] = m³ / mol = m³ mol⁻¹.",
      "Step 4: Compiling SI units: a has N m⁴ mol⁻², and b has m³ mol⁻¹.",
      "Step 5: Note: in practical chemistry units, a is in atm L² mol⁻² and b is in L mol⁻¹."
    ],
    "ans": "N m⁴ mol⁻²  and  m³ mol⁻¹ (Option A)",
    "trap": "Read units carefully! The question specifies SI UNITS (N and m), not practical units (atm and L). Option D gives practical units, but Option A gives the correct SI units.",
    "distractorTraps": {
      "B": "Dimension error: N m² instead of N m⁴.",
      "C": "Omitted square on moles in a (mol⁻¹ instead of mol⁻²).",
      "D": "Gave practical/atmospheric units instead of strict SI units."
    },
    "targetTab": "tab-real-particle",
    "simParams": {},
    "simSummary": [
      "[a] = [P][V²]/[n²] = N m⁴ mol⁻²",
      "[b] = [V]/[n] = m³ mol⁻¹",
      "Practical: atm L² mol⁻² & L mol⁻¹"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select N m⁴ mol⁻²  and  m³ mol⁻¹ (Option A).",
    "takeaway": "Transfer rule: start from Pressure correction: [a n² / V²] = [P] ⇒ [a] = [P] [V²] / [n²]; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "GAS-Q20",
    "num": "JEE Main 2018",
    "source": "JEE Main 2018 (Offline) 8th April Shift",
    "subtab": 2,
    "subtabName": "Maxwell-Boltzmann Speed Distribution",
    "year": "2018",
    "q": "At what absolute temperature will the root mean square speed (v_rms) of SO₂ molecules be equal to the v_rms of O₂ molecules at 300 K? (Molar masses: SO₂ = 64 g/mol, O₂ = 32 g/mol)",
    "options": [
      {
        "key": "A",
        "text": "600 K"
      },
      {
        "key": "B",
        "text": "150 K"
      },
      {
        "key": "C",
        "text": "450 K"
      },
      {
        "key": "D",
        "text": "1200 K"
      }
    ],
    "correct": "A",
    "formula": "v_rms = √(3RT/M) ⇒ T / M = constant for equal v_rms",
    "steps": [
      "Step 1: Formula for root mean square speed: v_rms = √(3 R T / M).",
      "Step 2: Equating speeds: v_rms(SO₂) = v_rms(O₂) ⇒ √(3 R T_SO2 / M_SO2) = √(3 R T_O2 / M_O2).",
      "Step 3: Square both sides and cancel 3R:",
      "        T_SO2 / M_SO2 = T_O2 / M_O2.",
      "Step 4: Solve for T_SO2: T_SO2 = T_O2 × (M_SO2 / M_O2).",
      "Step 5: Substitute M_SO2 = 64 g/mol, M_O2 = 32 g/mol, and T_O2 = 300 K:",
      "        T_SO2 = 300 K × (64 / 32) = 300 × 2 = 600 K."
    ],
    "ans": "600 K (Option A)",
    "trap": "Heavier molecule requires HIGHER temperature to attain the same rms speed! SO₂ is twice as heavy as O₂, so temperature must be doubled (300 × 2 = 600 K, not halved).",
    "distractorTraps": {
      "B": "Inverted the molar mass ratio: 300 / 2 = 150 K (halving temperature for heavier gas error).",
      "C": "Added 150 K.",
      "D": "Squared the molar mass ratio (300 × 4 = 1200 K)."
    },
    "targetTab": "tab-maxwell",
    "simParams": {},
    "simSummary": [
      "T_SO2 / 64 = 300 / 32",
      "T_SO2 = 300 × 2 = 600 K",
      "v_rms(SO₂ at 600 K) = v_rms(O₂ at 300 K)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 600 K (Option A).",
    "takeaway": "Transfer rule: start from v_rms = √(3RT/M) ⇒ T / M = constant for equal v_rms; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  }
];
