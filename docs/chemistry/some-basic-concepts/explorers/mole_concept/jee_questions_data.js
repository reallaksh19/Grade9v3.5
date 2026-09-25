/**
 * Some Basic Concepts of Chemistry (Mole Concept & Stoichiometry)
 * Master Question Registry & Step-by-Step Solutions Database
 * Curated from ExamSIDE IIT-JEE Main Questions (2013-2026)
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "CHEM02-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 6th April Morning Shift",
    "subtab": 2,
    "subtabName": "Limiting Reagent & Yield",
    "year": "2026",
    "q": "56 g of N₂ gas and 10 g of H₂ gas are mixed to produce NH₃ gas via the Haber process: N₂(g) + 3H₂(g) → 2NH₃(g). If the reaction proceeds to completion, the mass of NH₃ produced and the mass of the excess reactant remaining unreacted are respectively:",
    "options": [
      {
        "key": "A",
        "text": "56.7 g NH₃, 9.3 g N₂ remaining"
      },
      {
        "key": "B",
        "text": "56.7 g NH₃, 2.0 g N₂ remaining"
      },
      {
        "key": "C",
        "text": "51.0 g NH₃, 2.0 g N₂ remaining"
      },
      {
        "key": "D",
        "text": "56.7 g NH₃, 0.67 g H₂ remaining"
      }
    ],
    "correct": "A",
    "formula": "Moles n = mass / Molar mass. Limiting Reagent = min(n_N₂ / 1, n_H₂ / 3)",
    "steps": [
      "Step 1: Calculate moles of initial reactants: n(N₂) = 56 g / 28 g/mol = 2.00 mol. n(H₂) = 10 g / 2 g/mol = 5.00 mol.",
      "Step 2: Compare molar stoichiometric ratios: Required H₂ for 2.00 mol N₂ is 2.00 × 3 = 6.00 mol. But we only have 5.00 mol H₂. Therefore, H₂ is the Limiting Reagent (LR).",
      "Step 3: Moles of NH₃ produced based on LR (H₂): n(NH₃) = 5.00 × (2/3) = 3.333 mol.",
      "Step 4: Mass of NH₃ produced = 3.333 mol × 17 g/mol = 56.67 g ≈ 56.7 g.",
      "Step 5: Moles of N₂ consumed = 5.00 / 3 = 1.667 mol. Moles of N₂ unreacted = 2.00 - 1.667 = 0.333 mol.",
      "Step 6: Mass of unreacted N₂ = 0.333 mol × 28 g/mol = 9.33 g ≈ 9.3 g."
    ],
    "ans": "56.7 g NH₃, 9.3 g N₂ remaining (Option A)",
    "trap": "Never declare N₂ as limiting just because 56g is larger than 10g! Stoichiometry demands 3 moles of H₂ per mole of N₂.",
    "distractorTraps": {
      "B": "Incorrectly computed unreacted mass by simple difference of grams.",
      "C": "Assumed 100% conversion of N₂ without checking H₂ requirement.",
      "D": "Wrongly identified N₂ as the limiting reagent."
    },
    "targetTab": "tab-limiting",
    "simParams": {
      "massN2": 56,
      "massH2": 10
    },
    "simSummary": [
      "N₂ = 2.0 mol",
      "H₂ = 5.0 mol (Limiting Reagent)",
      "NH₃ Formed = 3.33 mol (56.7 g)",
      "Excess N₂ = 0.33 mol (9.3 g)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.massN2",
      "simParams.massH2"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds massN2, massH2 only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 56.7 g NH₃, 9.3 g N₂ remaining (Option A).",
    "takeaway": "Transfer rule: start from Moles n = mass / Molar mass; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q02",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 28th January Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Terms & Temperature",
    "year": "2025",
    "q": "Which of the following sets of concentration terms is completely independent of temperature changes?",
    "options": [
      {
        "key": "A",
        "text": "Molarity, Normality, and % (w/v)"
      },
      {
        "key": "B",
        "text": "Molality, Mole fraction, and Mass percentage (% w/w)"
      },
      {
        "key": "C",
        "text": "Molality, Molarity, and ppm"
      },
      {
        "key": "D",
        "text": "Formality, Normality, and Mole fraction"
      }
    ],
    "correct": "B",
    "formula": "V = V(T) due to thermal expansion, while mass m is temperature-invariant.",
    "steps": [
      "Step 1: Temperature affects liquid volume: V(T) = V₀(1 + γ ΔT). Density changes with temperature.",
      "Step 2: Any concentration unit that includes solution volume in the denominator (Molarity M = n/V, Normality N = eq/V, % w/v = mass/V) is temperature dependent.",
      "Step 3: Units based solely on mass (Molality m = n_solute / kg_solvent, Mole fraction X = n_A / n_total, Mass % = m_solute / m_total × 100) are strictly temperature-independent.",
      "Step 4: Therefore, Molality, Mole fraction, and Mass percentage (% w/w) remain invariant under heating."
    ],
    "ans": "Molality, Mole fraction, and Mass percentage (% w/w) (Option B)",
    "trap": "Students often confuse Molarity (mol/L solution, temp-dependent) with Molality (mol/kg solvent, temp-independent).",
    "distractorTraps": {
      "A": "Molarity and Normality contain volume V in denominator, hence decrease upon heating.",
      "C": "Molarity is included, which is temperature-dependent.",
      "D": "Normality contains volume V in denominator, hence temperature-dependent."
    },
    "targetTab": "tab-concentration",
    "simParams": {
      "tempC": 25
    },
    "simSummary": [
      "Molality = 1.00 m (Constant with T)",
      "Molarity drops as solution expands thermally",
      "Mass conservation invariant"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.tempC"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds tempC only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Molality, Mole fraction, and Mass percentage (% w/w) (Option B).",
    "takeaway": "Transfer rule: start from V = V(T) due to thermal expansion, while mass m is temperature-invariant; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q03",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 24th January Evening Shift",
    "subtab": 3,
    "subtabName": "Sequential Reactions & % Yield",
    "year": "2025",
    "q": "Consider the two-step synthesis: A + 2B → C (yield = 80%), followed by C + D → E (yield = 75%). Starting with 5.0 moles of A and excess of B and D, the moles of final product E obtained is:",
    "options": [
      {
        "key": "A",
        "text": "3.00 mol"
      },
      {
        "key": "B",
        "text": "3.75 mol"
      },
      {
        "key": "C",
        "text": "4.00 mol"
      },
      {
        "key": "D",
        "text": "2.50 mol"
      }
    ],
    "correct": "A",
    "formula": "Overall Fractional Yield Y_overall = Y₁ × Y₂. n_final = n_initial × Y_overall",
    "steps": [
      "Step 1: Step 1 theoretical moles of C from 5.0 mol A: n_theory(C) = 5.0 mol.",
      "Step 2: Actual moles of C obtained at 80% yield: n_actual(C) = 5.0 × 0.80 = 4.00 mol.",
      "Step 3: In Step 2, 4.00 moles of C react with excess D. Theoretical moles of E: n_theory(E) = 4.00 mol.",
      "Step 4: Actual moles of E obtained at 75% yield: n_actual(E) = 4.00 × 0.75 = 3.00 mol.",
      "Step 5: Alternatively, Overall Yield = 0.80 × 0.75 = 0.60 (60%). n(E) = 5.0 × 0.60 = 3.00 mol."
    ],
    "ans": "3.00 mol (Option A)",
    "trap": "Do not add the percentage losses (20% + 25% = 45%); sequential yields multiply as fractions: 0.80 × 0.75 = 0.60!",
    "distractorTraps": {
      "B": "Only applied the second reaction's yield (5.0 × 0.75 = 3.75).",
      "C": "Only applied the first reaction's yield (5.0 × 0.80 = 4.00).",
      "D": "Subtracted (1 - 0.20 - 0.25) × 5 = 2.75 incorrectly rounded."
    },
    "targetTab": "tab-sequential",
    "simParams": {
      "yield1": 80,
      "yield2": 75
    },
    "simSummary": [
      "Initial A = 5.0 mol",
      "Yield 1 = 80% → C = 4.0 mol",
      "Yield 2 = 75% → E = 3.0 mol",
      "Net Efficiency = 60.0%"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.yield1",
      "simParams.yield2"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds yield1, yield2 only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 3.00 mol (Option A).",
    "takeaway": "Transfer rule: start from Overall Fractional Yield Y_overall = Y₁ × Y₂; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q04",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 8th April Evening Shift",
    "subtab": 5,
    "subtabName": "Eudiometry & Gas Volume Contraction",
    "year": "2026",
    "q": "10 mL of a gaseous hydrocarbon C_x H_y is exploded with 80 mL of O₂ in an eudiometer tube. On cooling to room temperature, the residual gas volume is 65 mL. After treatment with aqueous KOH solution, the volume contracts further by 40 mL. The molecular formula of the hydrocarbon is:",
    "options": [
      {
        "key": "A",
        "text": "C₄H₁₀"
      },
      {
        "key": "B",
        "text": "C₄H₈"
      },
      {
        "key": "C",
        "text": "C₃H₈"
      },
      {
        "key": "D",
        "text": "C₂H₆"
      }
    ],
    "correct": null,
    "formula": "C_x H_y + (x + y/4) O₂ → x CO₂ + (y/2) H₂O(l). Contraction by KOH = Volume of CO₂ = 10 x mL",
    "steps": [
      "Step 1: For 10 mL C_xH_y, combustion consumes 10(x + y/4) mL O₂ and forms 10x mL CO₂; water condenses on cooling.",
      "Step 2: KOH removes 40 mL CO₂, so 10x = 40 and x = 4.",
      "Step 3: Before KOH, the 65 mL residual is CO₂ + excess O₂. Therefore excess O₂ = 65 - 40 = 25 mL.",
      "Step 4: O₂ consumed = 80 - 25 = 55 mL.",
      "Step 5: 10(4 + y/4) = 55, so 4 + y/4 = 5.5 and y = 6.",
      "Step 6: The stated data therefore imply C₄H₆. None of the listed options matches; this item is withheld from scoring pending source verification."
    ],
    "ans": "No listed option — stated data imply C₄H₆",
    "trap": "Water vapor condenses to liquid at room temperature; never count H₂O as part of the residual gas volume!",
    "distractorTraps": {
      "B": "Forgot to account for unreacted excess O₂ in residual gas.",
      "C": "Misread KOH contraction as unreacted oxygen instead of carbon dioxide.",
      "D": "Assumed liquid water contributed to gaseous pressure."
    },
    "targetTab": "tab-eudiometry",
    "simParams": {},
    "simSummary": [
      "Question withheld from scoring",
      "KOH contraction ⇒ x = 4",
      "Residual/O₂ balance ⇒ y = 6",
      "Implied formula = C₄H₆ (not listed)"
    ],
    "sourceAudit": "SOURCE_UNVERIFIED",
    "answerAudit": "FAIL",
    "answerAuditNote": "Internal arithmetic contradiction: KOH contraction gives x=4; 65 mL residual leaves 25 mL O₂, so 55 mL O₂ was consumed and y=6. The data imply C₄H₆, which is not a listed option.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "The current ExamSIDE listing for JEE Main 2026 Online 8 April Evening does not contain this eudiometry item; the stated attribution is not accepted as verified.",
    "teacherCheck": "Independent check: recompute the stated quantities from the stem instead of forcing an option. The local audit result is No listed option — stated data imply C₄H₆.",
    "takeaway": "Transfer rule: start from C_x H_y + (x + y/4) O₂ → x CO₂ + (y/2) H₂O(l); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q05",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 30th January Evening Shift",
    "subtab": 6,
    "subtabName": "Empirical & Molecular Formula",
    "year": "2025",
    "q": "An organic compound contains 40.0% Carbon, 6.7% Hydrogen, and 53.3% Oxygen by mass. If its vapour density is 30, its molecular formula is:",
    "options": [
      {
        "key": "A",
        "text": "CH₂O"
      },
      {
        "key": "B",
        "text": "C₂H₄O₂"
      },
      {
        "key": "C",
        "text": "C₃H₆O₃"
      },
      {
        "key": "D",
        "text": "C₄H₈O₄"
      }
    ],
    "correct": "B",
    "formula": "Molecular Mass = 2 × Vapour Density. n = Molecular Mass / Empirical Mass",
    "steps": [
      "Step 1: Compute moles in 100 g sample: n(C) = 40.0 / 12 = 3.33 mol. n(H) = 6.7 / 1 = 6.70 mol. n(O) = 53.3 / 16 = 3.33 mol.",
      "Step 2: Divide by the smallest mole value (3.33): C : H : O = (3.33/3.33) : (6.70/3.33) : (3.33/3.33) = 1 : 2 : 1. Empirical Formula = CH₂O.",
      "Step 3: Empirical Formula Mass = 12 + 2(1) + 16 = 30 g/mol.",
      "Step 4: Molecular Mass = 2 × Vapour Density = 2 × 30 = 60 g/mol.",
      "Step 5: Factor n = Molecular Mass / Empirical Mass = 60 / 30 = 2.",
      "Step 6: Molecular Formula = (CH₂O)₂ = C₂H₄O₂ (Acetic acid / Methyl formate)."
    ],
    "ans": "C₂H₄O₂ (Option B)",
    "trap": "Do not stop at the empirical formula CH₂O! Vapour density = 30 means Molar Mass = 60 g/mol.",
    "distractorTraps": {
      "A": "Selected the empirical formula without multiplying by factor n = 2.",
      "C": "Assumed Vapour Density equals Molecular Mass without the factor of 2.",
      "D": "Multiplied by n = 4 incorrectly."
    },
    "targetTab": "tab-empirical",
    "simParams": {},
    "simSummary": [
      "Empirical Formula = CH₂O (Mass 30)",
      "Vapour Density = 30 ⇒ Molar Mass = 60",
      "Factor n = 2 ⇒ Molecular Formula = C₂H₄O₂"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select C₂H₄O₂ (Option B).",
    "takeaway": "Transfer rule: start from Molecular Mass = 2 × Vapour Density; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q06",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Terms & Temperature",
    "year": "2024",
    "q": "The molality of a 10% (w/w) aqueous solution of glucose (C₆H₁₂O₆, Molar mass = 180 g/mol) is:",
    "options": [
      {
        "key": "A",
        "text": "0.617 m"
      },
      {
        "key": "B",
        "text": "0.556 m"
      },
      {
        "key": "C",
        "text": "0.485 m"
      },
      {
        "key": "D",
        "text": "0.720 m"
      }
    ],
    "correct": "A",
    "formula": "Molality m = (moles of solute) / (mass of solvent in kg). 10% w/w means 10g glucose in 90g water.",
    "steps": [
      "Step 1: Basis: Take 100 g of solution. Mass of glucose solute = 10 g. Mass of water solvent = 100 - 10 = 90 g = 0.090 kg.",
      "Step 2: Calculate moles of glucose: n = 10 g / 180 g/mol = 0.05556 mol.",
      "Step 3: Calculate molality: m = 0.05556 mol / 0.090 kg = 0.617 mol/kg = 0.617 m."
    ],
    "ans": "0.617 m (Option A)",
    "trap": "Do not divide moles by 100 g (total solution mass); molality denominator is solvent mass only (90 g)!",
    "distractorTraps": {
      "B": "Divided by 100 g solution mass: 0.0556 / 0.100 = 0.556 m.",
      "C": "Used 18 g solute instead of 10 g.",
      "D": "Inverted solvent and solute fractions."
    },
    "targetTab": "tab-concentration",
    "simParams": {},
    "simSummary": [
      "Solute = 10 g glucose",
      "Solvent = 90 g H₂O",
      "Molality = 0.617 m"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 0.617 m (Option A).",
    "takeaway": "Transfer rule: start from Molality m = (moles of solute) / (mass of solvent in kg); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q07",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 9th April Morning Shift",
    "subtab": 1,
    "subtabName": "The Mole Scale & Avogadro",
    "year": "2026",
    "q": "The total number of atoms present in 4.4 g of CO₂ gas at STP is (N_A = 6.022 × 10²³ mol⁻¹):",
    "options": [
      {
        "key": "A",
        "text": "1.807 × 10²³ atoms"
      },
      {
        "key": "B",
        "text": "6.022 × 10²² atoms"
      },
      {
        "key": "C",
        "text": "1.204 × 10²³ atoms"
      },
      {
        "key": "D",
        "text": "2.408 × 10²³ atoms"
      }
    ],
    "correct": "A",
    "formula": "Total Atoms = (mass / M) × N_A × (atomicity). For CO₂, atomicity = 1 + 2 = 3.",
    "steps": [
      "Step 1: Calculate moles of CO₂: n = 4.4 g / 44 g/mol = 0.10 mol.",
      "Step 2: Number of CO₂ molecules = 0.10 × N_A = 0.10 × 6.022 × 10²³ = 6.022 × 10²² molecules.",
      "Step 3: Each CO₂ molecule consists of 1 Carbon atom + 2 Oxygen atoms = 3 atoms.",
      "Step 4: Total number of atoms = 3 × 6.022 × 10²² = 1.8066 × 10²³ ≈ 1.807 × 10²³ atoms."
    ],
    "ans": "1.807 × 10²³ atoms (Option A)",
    "trap": "Always multiply by molecular atomicity (3 for CO₂); 6.022 × 10²² is the number of molecules, not atoms!",
    "distractorTraps": {
      "B": "Forgot atomicity factor of 3; reported number of molecules.",
      "C": "Only counted Oxygen atoms (2 × 6.022 × 10²²).",
      "D": "Multiplied by 4 instead of 3."
    },
    "targetTab": "tab-mole",
    "simParams": {
      "massG": 4.4
    },
    "simSummary": [
      "Mass = 4.4 g",
      "Moles = 0.10 mol",
      "Molecules = 6.022 × 10²²",
      "Total Atoms = 1.807 × 10²³"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.massG"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds massG only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 1.807 × 10²³ atoms (Option A).",
    "takeaway": "Transfer rule: start from Total Atoms = (mass / M) × N_A × (atomicity); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "CHEM02-Q08",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 31st January Evening Shift",
    "subtab": 2,
    "subtabName": "Limiting Reagent & Yield",
    "year": "2024",
    "q": "When 50 mL of 0.5 M BaCl₂ solution is mixed with 50 mL of 0.2 M Na₂SO₄ solution, the mass of BaSO₄ precipitated is (Molar mass of BaSO₄ = 233.3 g/mol):",
    "options": [
      {
        "key": "A",
        "text": "2.33 g"
      },
      {
        "key": "B",
        "text": "5.83 g"
      },
      {
        "key": "C",
        "text": "1.17 g"
      },
      {
        "key": "D",
        "text": "3.50 g"
      }
    ],
    "correct": "A",
    "formula": "BaCl₂ + Na₂SO₄ → BaSO₄(s)↓ + 2 NaCl. Millimoles = M × V(mL)",
    "steps": [
      "Step 1: Calculate millimoles of BaCl₂: 50 mL × 0.5 M = 25.0 mmol.",
      "Step 2: Calculate millimoles of Na₂SO₄: 50 mL × 0.2 M = 10.0 mmol.",
      "Step 3: Stoichiometry is 1:1. Na₂SO₄ has fewer millimoles (10.0 mmol vs 25.0 mmol), so Na₂SO₄ is the Limiting Reagent.",
      "Step 4: Millimoles of BaSO₄ precipitate formed = 10.0 mmol = 0.010 mol.",
      "Step 5: Mass of BaSO₄ = 0.010 mol × 233.3 g/mol = 2.333 g ≈ 2.33 g."
    ],
    "ans": "2.33 g (Option A)",
    "trap": "Do not base product mass on BaCl₂! Ba²⁺ is in substantial excess (15.0 mmol remains in solution).",
    "distractorTraps": {
      "B": "Used BaCl₂ as limiting reagent: 0.025 × 233.3 = 5.83 g.",
      "C": "Divided by total volume 100 mL incorrectly.",
      "D": "Averaged the two reagent quantities."
    },
    "targetTab": "tab-limiting",
    "simParams": {},
    "simSummary": [
      "BaCl₂ = 25.0 mmol",
      "Na₂SO₄ = 10.0 mmol (Limiting)",
      "Precipitate = 10.0 mmol BaSO₄ = 2.33 g"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 2.33 g (Option A).",
    "takeaway": "Transfer rule: start from BaCl₂ + Na₂SO₄ → BaSO₄(s)↓ + 2 NaCl; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q09",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 1st February Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Invariants & Thermal Expansion",
    "year": "2024",
    "q": "Which of the following concentration units changes when the temperature of the solution is altered?",
    "options": [
      {
        "key": "A",
        "text": "Molarity"
      },
      {
        "key": "B",
        "text": "Molality"
      },
      {
        "key": "C",
        "text": "Mole fraction"
      },
      {
        "key": "D",
        "text": "Mass percentage (% w/w)"
      }
    ],
    "correct": "A",
    "formula": "Molarity M = (Moles of solute) / (Volume of solution in L). Volume expands with temperature: V ∝ T ⇒ M decreases.",
    "steps": [
      "Step 1: Examine mass-based units: Molality (m = n_solute / kg_solvent), Mole fraction (X = n_i / n_total), and Mass percent (% w/w = mass_solute / mass_solution × 100).",
      "Step 2: Mass is strictly conserved and completely independent of thermal expansion or temperature changes.",
      "Step 3: Molarity (M) and Normality (N) are defined per unit volume of solution.",
      "Step 4: Since liquid solvents expand upon heating (ΔV > 0), the denominator increases while solute moles remain constant.",
      "Step 5: Therefore, Molarity decreases as temperature rises, making it temperature-dependent."
    ],
    "ans": "Molarity (Option A)",
    "trap": "Remember the distinction: Any unit involving VOLUME (Molarity, Normality, % v/v, % w/v) is temperature-dependent; units based strictly on MASS (Molality, Mole fraction, ppm by mass, % w/w) are temperature-independent!",
    "distractorTraps": {
      "B": "Molality is moles per kilogram of solvent (mass-based), so it is temperature-invariant.",
      "C": "Mole fraction is ratio of moles (mass-based), temperature-invariant.",
      "D": "Mass percentage is ratio of masses, strictly temperature-invariant."
    },
    "targetTab": "tab-concentration",
    "simParams": {},
    "simSummary": [
      "Volume expands with temperature",
      "Molarity decreases upon heating",
      "Molality & Mole Fraction stay invariant"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Molarity (Option A).",
    "takeaway": "Transfer rule: start from Molarity M = (Moles of solute) / (Volume of solution in L); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q10",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Evening Shift",
    "subtab": 5,
    "subtabName": "Eudiometry Gas Combustion Tube",
    "year": "2024",
    "q": "10 mL of a gaseous hydrocarbon (C_x H_y) requires 65 mL of O₂ for complete combustion and produces 40 mL of CO₂ gas under identical conditions of temperature and pressure. The molecular formula of the hydrocarbon is:",
    "options": [
      {
        "key": "A",
        "text": "C₄H₁₀"
      },
      {
        "key": "B",
        "text": "C₄H₈"
      },
      {
        "key": "C",
        "text": "C₃H₈"
      },
      {
        "key": "D",
        "text": "C₅H₁₀"
      }
    ],
    "correct": "A",
    "formula": "C_x H_y + (x + y/4) O₂ → x CO₂ + (y/2) H₂O. By Gay-Lussac's Law: V_CO2 = x × V_hydrocarbon,  V_O2 = (x + y/4) × V_hydrocarbon.",
    "steps": [
      "Step 1: By Gay-Lussac's Law of combining volumes, at constant T and P, volume ratio equals mole ratio.",
      "Step 2: Volume of CO₂ produced: V_CO2 = x × V_HC ⇒ 40 mL = x (10 mL) ⇒ x = 4.",
      "Step 3: Volume of O₂ consumed: V_O2 = (x + y/4) × V_HC ⇒ 65 mL = (4 + y/4) (10 mL).",
      "Step 4: Solve for y: 4 + y/4 = 6.5 ⇒ y/4 = 2.5 ⇒ y = 10.",
      "Step 5: Formula is C₄H₁₀ (Butane)."
    ],
    "ans": "C₄H₁₀ (Option A)",
    "trap": "Notice that water formed is in liquid state at room temperature, so its volume condenses to negligible; oxygen consumed accounts for both carbon dioxide and water formation!",
    "distractorTraps": {
      "B": "For C₄H₈, O₂ required would be (4 + 8/4)×10 = 60 mL, not 65 mL.",
      "C": "For C₃H₈, CO₂ produced would be 30 mL, not 40 mL.",
      "D": "Calculated x = 5 incorrectly."
    },
    "targetTab": "tab-eudiometry",
    "simParams": {},
    "simSummary": [
      "10 mL C_x H_y → 40 mL CO₂ ⇒ x = 4",
      "65 mL O₂ ⇒ (4 + y/4) = 6.5 ⇒ y = 10",
      "Formula = C₄H₁₀"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select C₄H₁₀ (Option A).",
    "takeaway": "Transfer rule: start from C_x H_y + (x + y/4) O₂ → x CO₂ + (y/2) H₂O; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q11",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 15th April Morning Shift",
    "subtab": 1,
    "subtabName": "The Dual-Reality Mole Scale",
    "year": "2023",
    "q": "The number of moles of electrons in 1.0 kg of electrons is approximately: (Mass of electron m_e = 9.109 × 10⁻³¹ kg, N_A = 6.022 × 10²³ mol⁻¹)",
    "options": [
      {
        "key": "A",
        "text": "1.82 × 10⁶ mol"
      },
      {
        "key": "B",
        "text": "6.02 × 10²³ mol"
      },
      {
        "key": "C",
        "text": "1.09 × 10³⁰ mol"
      },
      {
        "key": "D",
        "text": "9.11 × 10⁻⁸ mol"
      }
    ],
    "correct": "A",
    "formula": "Moles = (Total number of electrons) / N_A = M_total / (m_e × N_A)",
    "steps": [
      "Step 1: Total mass M = 1.0 kg.",
      "Step 2: Number of electrons in 1 kg: N = M / m_e = 1.0 / (9.109 × 10⁻³¹ kg) ≈ 1.098 × 10³⁰ electrons.",
      "Step 3: Number of moles of electrons: n = N / N_A = (1.098 × 10³⁰) / (6.022 × 10²³ mol⁻¹).",
      "Step 4: Compute: n = (1.098 / 6.022) × 10⁷ = 0.1823 × 10⁷ = 1.82 × 10⁶ moles.",
      "Step 5: Physical insight: 1 mole of electrons weighs only 0.548 mg (m_e × N_A = 5.48 × 10⁻⁷ kg), so 1 kg contains nearly 2 million moles of electrons!"
    ],
    "ans": "1.82 × 10⁶ mol (Option A)",
    "trap": "Do not report the total NUMBER of electrons (1.1 × 10³⁰); the question specifically asks for the number of MOLES of electrons (divide by N_A)!",
    "distractorTraps": {
      "B": "Reported Avogadro's number N_A.",
      "C": "Reported total number of electrons (1.09 × 10³⁰) without dividing by N_A.",
      "D": "Divided mass of electron by mass in grams."
    },
    "targetTab": "tab-mole",
    "simParams": {},
    "simSummary": [
      "Mass = 1 kg",
      "Total e⁻ = 1.098 × 10³⁰",
      "Moles = 1.82 × 10⁶ mol"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 1.82 × 10⁶ mol (Option A).",
    "takeaway": "Transfer rule: start from Moles = (Total number of electrons) / N_A = M_total / (m_e × N_A); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q12",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 8th April Evening Shift",
    "subtab": 2,
    "subtabName": "Limiting Reagent Assembly Factory",
    "year": "2023",
    "q": "56.0 g of nitrogen gas (N₂) and 10.0 g of hydrogen gas (H₂) are mixed and allowed to react completely to form ammonia (NH₃). The mass of NH₃ produced is: (Molar masses: N₂ = 28 g/mol, H₂ = 2 g/mol, NH₃ = 17 g/mol)",
    "options": [
      {
        "key": "A",
        "text": "56.7 g"
      },
      {
        "key": "B",
        "text": "68.0 g"
      },
      {
        "key": "C",
        "text": "66.0 g"
      },
      {
        "key": "D",
        "text": "85.0 g"
      }
    ],
    "correct": "A",
    "formula": "N₂ + 3 H₂ → 2 NH₃. Limiting reagent determines maximum product yield.",
    "steps": [
      "Step 1: Compute moles of each reactant:",
      "        Moles of N₂ = 56.0 g / 28 g/mol = 2.0 moles.",
      "        Moles of H₂ = 10.0 g / 2.0 g/mol = 5.0 moles.",
      "Step 2: Determine limiting reagent by dividing moles by stoichiometric coefficients:",
      "        For N₂: 2.0 / 1 = 2.0.",
      "        For H₂: 5.0 / 3 = 1.667.",
      "        Since 1.667 < 2.0, H₂ is the LIMITING REAGENT!",
      "Step 3: Calculate moles of NH₃ formed from limiting reagent H₂:",
      "        Moles of NH₃ = (2/3) × Moles of H₂ = (2/3) × 5.0 = 10/3 ≈ 3.333 moles.",
      "Step 4: Compute mass of NH₃: Mass = (10/3 mol) × 17 g/mol = 170 / 3 ≈ 56.67 g ≈ 56.7 g.",
      "Step 5: Unreacted N₂ remaining = 2.0 - (5.0 / 3) = 1/3 mol = 9.33 g. Total mass = 56.67 + 9.33 = 66.0 g (Mass is conserved!)."
    ],
    "ans": "56.7 g (Option A)",
    "trap": "Do not assume N₂ is limiting because 56 g looks like 2 moles; 2 moles of N₂ requires 6 moles (12 g) of H₂, but only 10 g is available! H₂ runs out first.",
    "distractorTraps": {
      "B": "Assumed N₂ is limiting: 2 mol N₂ → 4 mol NH₃ ⇒ 4 × 17 = 68.0 g (excess reagent fallacy).",
      "C": "Simply added reactant masses: 56 g + 10 g = 66.0 g (assuming 100% conversion with no unreacted excess).",
      "D": "Multiplied 5 moles of H₂ by 17 g/mol directly."
    },
    "targetTab": "tab-limiting",
    "simParams": {},
    "simSummary": [
      "2.0 mol N₂ + 5.0 mol H₂",
      "H₂ is Limiting (needs 6 mol, has 5 mol)",
      "NH₃ formed = 56.7 g"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 56.7 g (Option A).",
    "takeaway": "Transfer rule: start from N₂ + 3 H₂ → 2 NH₃; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q13",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 29th June Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Invariants & Thermal Expansion",
    "year": "2022",
    "q": "The mole fraction of a solute in an aqueous solution is 0.05. The molality of the solution is approximately: (Molar mass of water = 18 g/mol)",
    "options": [
      {
        "key": "A",
        "text": "2.92 m"
      },
      {
        "key": "B",
        "text": "2.78 m"
      },
      {
        "key": "C",
        "text": "3.20 m"
      },
      {
        "key": "D",
        "text": "1.95 m"
      }
    ],
    "correct": "A",
    "formula": "Molality m = (X_solute × 1000) / ((1 - X_solute) × M_solvent)",
    "steps": [
      "Step 1: In 1 mole of total solution, moles of solute n₁ = 0.05 mol.",
      "Step 2: Moles of solvent (water) n₂ = 1 - 0.05 = 0.95 mol.",
      "Step 3: Mass of solvent in kg: W_solvent = (0.95 mol × 18 g/mol) / 1000 = 17.1 / 1000 = 0.0171 kg.",
      "Step 4: Molality m = n_solute / W_solvent(kg) = 0.05 / 0.0171 = 50 / 17.1 ≈ 2.924 mol/kg = 2.92 m.",
      "Step 5: Invariant check: In dilute solution, m ≈ X × 1000 / 18 = 0.05 × 55.55 = 2.78 m; here 2.92 m accounts for the denominator (1 - X)."
    ],
    "ans": "2.92 m (Option A)",
    "trap": "Do not forget the (1 - X) factor in the denominator! Approximating (1 - X) ≈ 1 gives 2.78 m, which is a classic distractor trap.",
    "distractorTraps": {
      "B": "Approximated 1 - X ≈ 1 (dilute approximation error): 0.05 × 1000 / 18 = 2.78 m.",
      "C": "Used molar mass 16 g/mol for water.",
      "D": "Calculated molarity assuming volume = 1 L without density."
    },
    "targetTab": "tab-concentration",
    "simParams": {},
    "simSummary": [
      "X_solute = 0.05, X_water = 0.95",
      "m = (0.05 × 1000) / (0.95 × 18)",
      "Molality = 2.92 m"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 2.92 m (Option A).",
    "takeaway": "Transfer rule: start from Molality m = (X_solute × 1000) / ((1 - X_solute) × M_solvent); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q14",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 25th June Evening Shift",
    "subtab": 3,
    "subtabName": "Sequential & Parallel Yield Pipeline",
    "year": "2022",
    "q": "A synthesis involves two sequential steps: A → B with 80% yield, followed by B → C with 50% yield. If 10.0 moles of A are initially taken, how many moles of C are obtained?",
    "options": [
      {
        "key": "A",
        "text": "4.0 moles"
      },
      {
        "key": "B",
        "text": "6.5 moles"
      },
      {
        "key": "C",
        "text": "5.0 moles"
      },
      {
        "key": "D",
        "text": "3.0 moles"
      }
    ],
    "correct": "A",
    "formula": "Overall Yield η_net = η₁ × η₂. Moles of C = n_A × η_net.",
    "steps": [
      "Step 1: Initial feed of reactant A = 10.0 moles.",
      "Step 2: Step 1 (A → B) has 80% yield (η₁ = 0.80): Moles of B produced = 10.0 × 0.80 = 8.0 moles.",
      "Step 3: Step 2 (B → C) has 50% yield (η₂ = 0.50): Moles of C produced = 8.0 × 0.50 = 4.0 moles.",
      "Step 4: Overall sequential yield η_net = 0.80 × 0.50 = 0.40 = 40%.",
      "Step 5: Total moles of C obtained = 10.0 × 0.40 = 4.0 moles."
    ],
    "ans": "4.0 moles (Option A)",
    "trap": "Sequential yields multiply (η_net = η₁ × η₂ = 40%), they NEVER average! The arithmetic mean (80 + 50)/2 = 65% is the classic exam trap.",
    "distractorTraps": {
      "B": "Averaged yields: (80 + 50)/2 = 65% ⇒ 6.5 moles (arithmetic average fallacy).",
      "C": "Applied only the second yield 50% directly on initial feed A.",
      "D": "Subtracted yields (80 - 50 = 30%)."
    },
    "targetTab": "tab-sequential",
    "simParams": {
      "yield1": 80,
      "yield2": 50
    },
    "simSummary": [
      "Feed A = 10.0 mol",
      "η_net = 80% × 50% = 40%",
      "Final Product C = 4.0 mol"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.yield1",
      "simParams.yield2"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds yield1, yield2 only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 4.0 moles (Option A).",
    "takeaway": "Transfer rule: start from Overall Yield η_net = η₁ × η₂; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q15",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 26th February Morning Shift",
    "subtab": 6,
    "subtabName": "Empirical & Molecular Formula Resolver",
    "year": "2021",
    "q": "An organic compound contains 40.0% Carbon, 6.7% Hydrogen, and 53.3% Oxygen by mass. If its vapor density is 30, its molecular formula is:",
    "options": [
      {
        "key": "A",
        "text": "C₂H₄O₂"
      },
      {
        "key": "B",
        "text": "CH₂O"
      },
      {
        "key": "C",
        "text": "C₃H₆O₃"
      },
      {
        "key": "D",
        "text": "C₂H₆O"
      }
    ],
    "correct": "A",
    "formula": "Molar Mass = 2 × Vapor Density. n = (Molar Mass) / (Empirical Formula Mass).",
    "steps": [
      "Step 1: Find mole ratio of elements in 100 g sample:",
      "        Moles of C = 40.0 / 12 = 3.33.",
      "        Moles of H = 6.7 / 1 = 6.70.",
      "        Moles of O = 53.3 / 16 = 3.33.",
      "Step 2: Divide by the smallest value (3.33):",
      "        C : H : O = (3.33 / 3.33) : (6.70 / 3.33) : (3.33 / 3.33) = 1 : 2.01 : 1 ≈ 1 : 2 : 1.",
      "Step 3: Empirical formula is CH₂O. Empirical Formula Mass = 12 + 2 + 16 = 30 g/mol.",
      "Step 4: Molar mass = 2 × Vapor Density = 2 × 30 = 60 g/mol.",
      "Step 5: Integer multiplier n = (Molar Mass) / (Empirical Mass) = 60 / 30 = 2.",
      "Step 6: Molecular formula = (CH₂O)₂ = C₂H₄O₂ (Acetic acid / Methyl formate)."
    ],
    "ans": "C₂H₄O₂ (Option A)",
    "trap": "Notice the difference between EMPIRICAL formula (CH₂O) and MOLECULAR formula (C₂H₄O₂)! Don't stop at the empirical ratio.",
    "distractorTraps": {
      "B": "Reported EMPIRICAL formula CH₂O instead of molecular formula.",
      "C": "Multiplied by 3 instead of 2.",
      "D": "Ethanol formula C₂H₆O does not match the elemental mass percentages."
    },
    "targetTab": "tab-empirical",
    "simParams": {},
    "simSummary": [
      "Empirical = CH₂O (30 g/mol)",
      "Molar Mass = 2 × 30 = 60 g/mol",
      "Molecular = C₂H₄O₂"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select C₂H₄O₂ (Option A).",
    "takeaway": "Transfer rule: start from Molar Mass = 2 × Vapor Density; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q16",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 27th July Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Invariants & Thermal Expansion",
    "year": "2021",
    "q": "100 mL of 0.2 M H₂SO₄ is mixed with 200 mL of 0.1 M HCl. What is the resulting concentration of H⁺ ions in the final mixture?",
    "options": [
      {
        "key": "A",
        "text": "0.20 M"
      },
      {
        "key": "B",
        "text": "0.133 M"
      },
      {
        "key": "C",
        "text": "0.15 M"
      },
      {
        "key": "D",
        "text": "0.30 M"
      }
    ],
    "correct": "A",
    "formula": "[H⁺] = (Total millimoles of H⁺) / (Total volume in mL)",
    "steps": [
      "Step 1: H₂SO₄ is a diprotic acid (basicity = 2): 1 molecule of H₂SO₄ releases 2 H⁺ ions.",
      "        Millimoles of H⁺ from H₂SO₄ = 2 × (Molarity × Volume) = 2 × (0.2 M × 100 mL) = 40 mmol.",
      "Step 2: HCl is a monoprotic acid (basicity = 1): 1 molecule releases 1 H⁺ ion.",
      "        Millimoles of H⁺ from HCl = 1 × (0.1 M × 200 mL) = 20 mmol.",
      "Step 3: Total millimoles of H⁺ = 40 + 20 = 60 mmol.",
      "Step 4: Total volume of solution = 100 mL + 200 mL = 300 mL.",
      "Step 5: Concentration of H⁺: [H⁺] = 60 mmol / 300 mL = 0.20 M."
    ],
    "ans": "0.20 M (Option A)",
    "trap": "BASICITY TRAP: Forgetting that H₂SO₄ provides TWO H⁺ ions per molecule yields (20 + 20)/300 = 0.133 M, a very common exam trap!",
    "distractorTraps": {
      "B": "Treated H₂SO₄ as monoprotic: (20 + 20)/300 = 40/300 ≈ 0.133 M (basicity omission error).",
      "C": "Took arithmetic average of molarities (0.2 + 0.1)/2 = 0.15 M.",
      "D": "Added molarities directly: 0.2 + 0.1 = 0.30 M."
    },
    "targetTab": "tab-concentration",
    "simParams": {},
    "simSummary": [
      "H₂SO₄ (diprotic): 40 mmol H⁺",
      "HCl (monoprotic): 20 mmol H⁺",
      "[H⁺] = 60 mmol / 300 mL = 0.20 M"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 0.20 M (Option A).",
    "takeaway": "Transfer rule: start from [H⁺] = (Total millimoles of H⁺) / (Total volume in mL); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q17",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 9th January Morning Shift",
    "subtab": 4,
    "subtabName": "Concentration Invariants & Thermal Expansion",
    "year": "2020",
    "q": "The strength of an aqueous KOH solution is 30% by mass (% w/w). If its density is 1.29 g/mL, its molarity is: (Molar mass of KOH = 56.1 g/mol)",
    "options": [
      {
        "key": "A",
        "text": "6.90 M"
      },
      {
        "key": "B",
        "text": "5.35 M"
      },
      {
        "key": "C",
        "text": "7.50 M"
      },
      {
        "key": "D",
        "text": "6.20 M"
      }
    ],
    "correct": "A",
    "formula": "Molarity M = (10 × x × d) / M_solute,  where x = % by mass, d = density in g/mL",
    "steps": [
      "Step 1: Consider 100 g of solution:",
      "        Mass of solute (KOH) = 30 g.",
      "        Volume of 100 g solution = Mass / Density = 100 g / 1.29 g/mL = 77.52 mL = 0.07752 L.",
      "Step 2: Moles of KOH = 30 g / 56.1 g/mol = 0.5348 mol.",
      "Step 3: Molarity M = (Moles of solute) / (Volume in L) = 0.5348 / 0.07752 = 6.899 ≈ 6.90 M.",
      "Step 4: Check via master conversion shortcut formula:",
      "        M = (10 × %w/w × d) / M_solute = (10 × 30 × 1.29) / 56.1 = 387 / 56.1 = 6.898 ≈ 6.90 M."
    ],
    "ans": "6.90 M (Option A)",
    "trap": "Remember the factor of 10 in the shortcut formula M = 10 × x × d / M_solute comes from 1000/100!",
    "distractorTraps": {
      "B": "Used molality formula with solvent mass (70 g) instead of solution volume.",
      "C": "Approximated density as 1.4 g/mL.",
      "D": "Used molar mass of NaOH (40 g/mol) instead of KOH (56.1 g/mol)."
    },
    "targetTab": "tab-concentration",
    "simParams": {},
    "simSummary": [
      "30% w/w KOH, d = 1.29 g/mL",
      "Shortcut: 10 × 30 × 1.29 / 56.1",
      "Molarity = 6.90 M"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 6.90 M (Option A).",
    "takeaway": "Transfer rule: start from Molarity M = (10 × x × d) / M_solute,  where x = % by mass, d = density in g/mL; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q18",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 7th January Evening Shift",
    "subtab": 2,
    "subtabName": "Limiting Reagent Assembly Factory",
    "year": "2020",
    "q": "A 20.0 g sample of limestone (impure CaCO₃) on thermal decomposition yields 4.4 g of carbon dioxide (CO₂). The percentage purity of CaCO₃ in the sample is: (Molar masses: CaCO₃ = 100 g/mol, CO₂ = 44 g/mol)",
    "options": [
      {
        "key": "A",
        "text": "50%"
      },
      {
        "key": "B",
        "text": "44%"
      },
      {
        "key": "C",
        "text": "75%"
      },
      {
        "key": "D",
        "text": "22%"
      }
    ],
    "correct": "A",
    "formula": "CaCO₃ → CaO + CO₂. % Purity = (Pure mass calculated from stoichiometry / Impure sample mass) × 100",
    "steps": [
      "Step 1: Write decomposition equation: CaCO₃(s) → CaO(s) + CO₂(g).",
      "Step 2: 1 mole of pure CaCO₃ (100 g) produces 1 mole of CO₂ (44 g).",
      "Step 3: Moles of CO₂ produced = 4.4 g / 44 g/mol = 0.10 mol.",
      "Step 4: Moles of pure CaCO₃ that reacted = 0.10 mol.",
      "Step 5: Mass of pure CaCO₃ = 0.10 mol × 100 g/mol = 10.0 g.",
      "Step 6: Percentage purity = (10.0 g / 20.0 g) × 100 = 50.0%."
    ],
    "ans": "50% (Option A)",
    "trap": "Do not confuse mass of CO₂ (4.4 g) with mass percentage! 4.4 g CO₂ represents 10.0 g of pure CaCO₃ in 20.0 g of ore.",
    "distractorTraps": {
      "B": "Reported molar mass of CO₂ (44%) directly.",
      "C": "Assumed 15 g reacted.",
      "D": "Divided 4.4 g directly by 20.0 g to get 22% (CO₂ mass fraction, not limestone purity)."
    },
    "targetTab": "tab-limiting",
    "simParams": {},
    "simSummary": [
      "4.4 g CO₂ = 0.10 mol",
      "Pure CaCO₃ = 0.10 × 100 = 10.0 g",
      "Purity = 10 / 20 = 50%"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 50% (Option A).",
    "takeaway": "Transfer rule: start from CaCO₃ → CaO + CO₂; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q19",
    "num": "JEE Main 2019",
    "source": "JEE Main 2019 (Online) 12th April Morning Shift",
    "subtab": 5,
    "subtabName": "Eudiometry Gas Combustion Tube",
    "year": "2019",
    "q": "A mixture of 20 mL of CO and 20 mL of O₂ is sparked in an eudiometer. After complete reaction and cooling to initial room temperature, the total volume of the resulting gas mixture is:",
    "options": [
      {
        "key": "A",
        "text": "30 mL"
      },
      {
        "key": "B",
        "text": "20 mL"
      },
      {
        "key": "C",
        "text": "40 mL"
      },
      {
        "key": "D",
        "text": "10 mL"
      }
    ],
    "correct": "A",
    "formula": "2 CO(g) + O₂(g) → 2 CO₂(g)",
    "steps": [
      "Step 1: Write balanced stoichiometric equation: 2 CO + 1 O₂ → 2 CO₂.",
      "Step 2: 2 volumes of CO react with 1 volume of O₂ to give 2 volumes of CO₂.",
      "Step 3: Initial volumes: V_CO = 20 mL, V_O2 = 20 mL.",
      "Step 4: CO is limiting: 20 mL of CO consumes 10 mL of O₂ and forms 20 mL of CO₂.",
      "Step 5: Remaining gases in the eudiometer:",
      "        V_CO = 0 mL (completely consumed)",
      "        V_O2 (unreacted excess) = 20 mL - 10 mL = 10 mL",
      "        V_CO2 (formed) = 20 mL",
      "Step 6: Total final gas volume = 10 mL (O₂) + 20 mL (CO₂) = 30 mL."
    ],
    "ans": "30 mL (Option A)",
    "trap": "Do not forget the UNREACTED EXCESS O₂ (10 mL)! The resulting mixture consists of both formed CO₂ (20 mL) and leftover O₂ (10 mL).",
    "distractorTraps": {
      "B": "Counted only the formed CO₂ (20 mL), forgetting excess oxygen.",
      "C": "Assumed no volume contraction (20 + 20 = 40 mL).",
      "D": "Reported only the excess oxygen (10 mL)."
    },
    "targetTab": "tab-eudiometry",
    "simParams": {},
    "simSummary": [
      "20 mL CO + 20 mL O₂",
      "CO is limiting: consumes 10 mL O₂",
      "Final = 20 mL CO₂ + 10 mL O₂ = 30 mL"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 30 mL (Option A).",
    "takeaway": "Transfer rule: start from 2 CO(g) + O₂(g) → 2 CO₂(g); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "MOLE-Q20",
    "num": "JEE Main 2018",
    "source": "JEE Main 2018 (Offline) 8th April Shift",
    "subtab": 1,
    "subtabName": "The Dual-Reality Mole Scale",
    "year": "2018",
    "q": "Which of the following samples contains the MAXIMUM number of molecules?",
    "options": [
      {
        "key": "A",
        "text": "1.0 g of H₂"
      },
      {
        "key": "B",
        "text": "1.0 g of O₂"
      },
      {
        "key": "C",
        "text": "1.0 g of N₂"
      },
      {
        "key": "D",
        "text": "1.0 g of CH₄"
      }
    ],
    "correct": "A",
    "formula": "Number of molecules N = (Mass / Molar Mass) × N_A ∝ 1 / M_molar for equal mass",
    "steps": [
      "Step 1: Number of molecules in equal mass m = 1.0 g is inversely proportional to molar mass M: N ∝ 1 / M.",
      "Step 2: For 1.0 g H₂: M = 2 g/mol ⇒ Moles = 1.0 / 2 = 0.50 mol ⇒ N = 0.50 N_A.",
      "Step 3: For 1.0 g CH₄: M = 16 g/mol ⇒ Moles = 1.0 / 16 = 0.0625 mol ⇒ N = 0.0625 N_A.",
      "Step 4: For 1.0 g N₂: M = 28 g/mol ⇒ Moles = 1.0 / 28 = 0.0357 mol ⇒ N = 0.0357 N_A.",
      "Step 5: For 1.0 g O₂: M = 32 g/mol ⇒ Moles = 1.0 / 32 = 0.03125 mol ⇒ N = 0.03125 N_A.",
      "Step 6: Comparing molecules: H₂ (0.50 N_A) >> CH₄ (0.0625 N_A) > N₂ (0.0357 N_A) > O₂ (0.03125 N_A)."
    ],
    "ans": "1.0 g of H₂ (Option A)",
    "trap": "Smallest molar mass gives the HIGHEST number of molecules per gram! H₂ has M = 2, so it has 16 times more molecules than equal mass of O₂.",
    "distractorTraps": {
      "B": "O₂ has the heaviest molar mass (32 g/mol) and therefore the FEWEST molecules per gram.",
      "C": "N₂ has M = 28 g/mol, much fewer molecules than H₂.",
      "D": "CH₄ has 5 atoms per molecule, but the question asks for MOLECULES, not total atoms!"
    },
    "targetTab": "tab-mole",
    "simParams": {},
    "simSummary": [
      "1.0 g H₂ = 0.50 N_A molecules (Maximum!)",
      "Molecules ∝ 1 / Molar Mass"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 1.0 g of H₂ (Option A).",
    "takeaway": "Transfer rule: start from Number of molecules N = (Mass / Molar Mass) × N_A ∝ 1 / M_molar for equal mass; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  }
];
