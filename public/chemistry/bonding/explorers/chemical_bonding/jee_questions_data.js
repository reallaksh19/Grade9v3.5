/**
 * Chemical Bonding and Molecular Structure
 * Master Question Registry & Step-by-Step Solutions Database
 * Curated from ExamSIDE IIT-JEE Main Questions (2013-2026)
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "BOND-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 8th April Morning Shift",
    "subtab": 5,
    "subtabName": "Molecular Orbital Theory (MOT)",
    "year": "2026",
    "q": "According to Molecular Orbital Theory (MOT), which of the following oxygen species is diamagnetic and has the shortest bond length?",
    "options": [
      {
        "key": "A",
        "text": "O₂²⁺"
      },
      {
        "key": "B",
        "text": "O₂"
      },
      {
        "key": "C",
        "text": "O₂⁻"
      },
      {
        "key": "D",
        "text": "O₂²⁻"
      }
    ],
    "correct": "A",
    "formula": "Bond Order BO = ½ (N_b - N_a). Bond Length ∝ 1 / (Bond Order). Species is diamagnetic if all electrons are paired.",
    "steps": [
      "Step 1: Write electronic configuration of neutral O₂ (16 electrons, > 14 e⁻, NO 2s-2p mixing):",
      "        σ₁ₛ² σ*₁ₛ² σ₂ₛ² σ*₂ₛ² σ₂ₚ_z² (π₂ₚ_x² = π₂ₚ_y²) (π*₂ₚ_x¹ = π*₂ₚ_y¹).",
      "        For neutral O₂: N_b = 10, N_a = 6 ⇒ BO = ½ (10 - 6) = 2.0. Paramagnetic (2 unpaired electrons).",
      "Step 2: For O₂²⁺ (14 electrons, like N₂):",
      "        Remove 2 electrons from the antibonding π* orbitals: N_b = 10, N_a = 4.",
      "        BO = ½ (10 - 4) = 3.0. All electrons are paired ⇒ Diamagnetic!",
      "Step 3: For O₂⁻ (17 electrons): BO = ½ (10 - 7) = 1.5. Paramagnetic (1 unpaired electron).",
      "Step 4: For O₂²⁻ (18 electrons, peroxide): BO = ½ (10 - 8) = 1.0. Diamagnetic.",
      "Step 5: Comparing Bond Orders: O₂²⁺ (3.0) > O₂ (2.0) > O₂⁻ (1.5) > O₂²⁻ (1.0).",
      "Step 6: Since Bond Length ∝ 1 / (Bond Order), O₂²⁺ has the highest bond order (3.0) and therefore the SHORTEST bond length, while being completely diamagnetic."
    ],
    "ans": "O₂²⁺ (Option A)",
    "trap": "Both O₂²⁺ and O₂²⁻ are diamagnetic! But O₂²⁻ has a single bond (BO = 1.0, longest bond length), whereas O₂²⁺ has a triple bond (BO = 3.0, shortest bond length).",
    "distractorTraps": {
      "B": "O₂ is paramagnetic with 2 unpaired electrons (famous experiment with liquid O₂ sticking to magnets).",
      "C": "O₂⁻ (superoxide) is paramagnetic with 1 unpaired electron.",
      "D": "O₂²⁻ is diamagnetic, but has the LONGEST bond length (BO = 1.0 vs 3.0)."
    },
    "targetTab": "tab-mot",
    "simParams": {
      "electrons": 14
    },
    "simSummary": [
      "O₂²⁺ (14 electrons)",
      "Bond Order = 3.0 (Triple Bond)",
      "Shortest Bond Length",
      "Diamagnetic (0 Unpaired)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.electrons"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds electrons only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select O₂²⁺ (Option A).",
    "takeaway": "Transfer rule: start from Bond Order BO = ½ (N_b - N_a); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q02",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 24th January Morning Shift",
    "subtab": 2,
    "subtabName": "3D VSEPR & Bent's Rule",
    "year": "2025",
    "q": "The geometry and net dipole moment of XeF₄ and SF₄ respectively are:",
    "options": [
      {
        "key": "A",
        "text": "XeF₄: Square planar, μ = 0; SF₄: See-saw, μ ≠ 0"
      },
      {
        "key": "B",
        "text": "XeF₄: Tetrahedral, μ = 0; SF₄: Square planar, μ = 0"
      },
      {
        "key": "C",
        "text": "XeF₄: See-saw, μ ≠ 0; SF₄: Square planar, μ = 0"
      },
      {
        "key": "D",
        "text": "XeF₄: Square planar, μ ≠ 0; SF₄: See-saw, μ = 0"
      }
    ],
    "correct": "A",
    "formula": "Steric Number = Bond Pairs + Lone Pairs. XeF₄ = 4 + 2 = 6 (sp³d²). SF₄ = 4 + 1 = 5 (sp³d)",
    "steps": [
      "Step 1: Calculate Steric Number for XeF₄: Xe has 8 valence electrons. 4 bond pairs to F + 2 lone pairs = 6 electron domains ⇒ Octahedral electronic geometry.",
      "Step 2: VSEPR minimization puts the 2 lone pairs opposite to each other (axial positions, 180° apart) to minimize 90° lp-bp repulsions.",
      "Step 3: The 4 fluorine atoms lie in a single plane at 90° angles ⇒ Square Planar molecular geometry.",
      "Step 4: Vectorial Dipole Sum for XeF₄: The four Xe-F bond dipoles cancel out in pairs in the plane, and the two axial lone pair moments cancel each other ⇒ Net Dipole Moment μ = 0.",
      "Step 5: Calculate Steric Number for SF₄: S has 6 valence electrons. 4 bond pairs to F + 1 lone pair = 5 electron domains ⇒ Trigonal Bipyramidal electronic geometry.",
      "Step 6: Bent's Rule / VSEPR: Lone pair occupies an equatorial position (experiencing only two 90° repulsions instead of three) ⇒ See-saw molecular geometry.",
      "Step 7: In See-saw SF₄, the axial F-S-F bond angle is ~173° (bent by lone pair) and equatorial F-S-F angle is ~102°. The dipoles do NOT cancel ⇒ Net Dipole Moment μ ≠ 0."
    ],
    "ans": "XeF₄: Square planar, μ = 0; SF₄: See-saw, μ ≠ 0 (Option A)",
    "trap": "Do not treat XeF₄ as tetrahedral! The two lone pairs force it into an octahedral family with square planar geometry.",
    "distractorTraps": {
      "B": "Assumed 4 substituents always mean tetrahedral.",
      "C": "Swapped geometries of XeF₄ and SF₄.",
      "D": "Inverted dipole moments."
    },
    "targetTab": "tab-vsepr",
    "simParams": {
      "molecule": "XeF4"
    },
    "simSummary": [
      "XeF₄: Steric 6 (sp³d²), 2 Axial Lone Pairs, Square Planar, μ = 0",
      "SF₄: Steric 5 (sp³d), 1 Equatorial Lone Pair, See-saw, μ ≠ 0"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select XeF₄: Square planar, μ = 0; SF₄: See-saw, μ ≠ 0 (Option A).",
    "takeaway": "Transfer rule: start from Steric Number = Bond Pairs + Lone Pairs; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q03",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Evening Shift",
    "subtab": 3,
    "subtabName": "Vectorial Dipole Moments",
    "year": "2024",
    "q": "Although Nitrogen and Fluorine are both highly electronegative, the dipole moment of NH₃ (1.47 D) is significantly greater than that of NF₃ (0.24 D). The correct explanation is:",
    "options": [
      {
        "key": "A",
        "text": "In NH₃, the orbital dipole of the lone pair reinforces the resultant N-H bond dipoles, whereas in NF₃ it opposes the N-F bond dipoles."
      },
      {
        "key": "B",
        "text": "The N-H bond is more polar than the N-F bond."
      },
      {
        "key": "C",
        "text": "NF₃ is planar while NH₃ is pyramidal."
      },
      {
        "key": "D",
        "text": "NH₃ has atomic number smaller than NF₃."
      }
    ],
    "correct": "A",
    "formula": "μ_net = Σ μ_bond + μ_lonepair (Vector sum in 3D)",
    "steps": [
      "Step 1: Both NH₃ and NF₃ have trigonal pyramidal geometries (Steric number 4, 3 bond pairs + 1 lone pair, sp³ hybridization).",
      "Step 2: In NH₃, Nitrogen is more electronegative than Hydrogen (EN: N = 3.04, H = 2.20). Therefore, the three N-H bond dipoles point UPWARD toward Nitrogen.",
      "Step 3: The lone pair dipole also points UPWARD away from the Nitrogen nucleus. Thus, all four vector dipoles reinforce in the same direction ⇒ High dipole moment (μ = 1.47 D).",
      "Step 4: In NF₃, Fluorine is more electronegative than Nitrogen (EN: F = 3.98, N = 3.04). Therefore, the three N-F bond dipoles point DOWNWARD toward the Fluorines.",
      "Step 5: The lone pair dipole points UPWARD, directly OPPOSING the downward resultant of the three N-F bonds ⇒ Drastic cancellation ⇒ Small net dipole moment (μ = 0.24 D)."
    ],
    "ans": "In NH₃, lone pair reinforces N-H bonds; in NF₃, lone pair opposes N-F bonds (Option A)",
    "trap": "Do not argue that N-F bond is less polar; F is the most electronegative element! The cancellation is purely VECTORIAL in 3D.",
    "distractorTraps": {
      "B": "False: N-F electronegativity difference (0.94) is greater than N-H (0.84).",
      "C": "Both molecules are pyramidal; neither is planar.",
      "D": "Atomic number does not determine dipole moment."
    },
    "targetTab": "tab-dipole",
    "simParams": {},
    "simSummary": [
      "NH₃: 3 N-H (↑) + Lone Pair (↑) = Reinforcing (μ = 1.47 D)",
      "NF₃: 3 N-F (↓) + Lone Pair (↑) = Opposing (μ = 0.24 D)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select In NH₃, lone pair reinforces N-H bonds; in NF₃, lone pair opposes N-F bonds (Option A).",
    "takeaway": "Transfer rule: start from μ_net = Σ μ_bond + μ_lonepair (Vector sum in 3D); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q04",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 5th April Morning Shift",
    "subtab": 4,
    "subtabName": "Hybridization & Axial Elongation",
    "year": "2026",
    "q": "In gaseous phosphorus pentachloride (PCl₅), the axial P-Cl bonds are longer and weaker than the equatorial P-Cl bonds because:",
    "options": [
      {
        "key": "A",
        "text": "Axial bond pairs experience three 90° repulsions from equatorial bond pairs, whereas equatorial pairs experience only two 90° repulsions."
      },
      {
        "key": "B",
        "text": "Axial bonds are formed by pure p-orbitals while equatorial bonds are sp²."
      },
      {
        "key": "C",
        "text": "Chlorine atoms in axial positions are more electronegative."
      },
      {
        "key": "D",
        "text": "PCl₅ is unstable and immediately dissociates."
      }
    ],
    "correct": "A",
    "formula": "In sp³d trigonal bipyramidal: Axial pairs suffer 3 × 90° bp-bp repulsions; Equatorial pairs suffer 2 × 90° bp-bp repulsions.",
    "steps": [
      "Step 1: PCl₅ has sp³d hybridization (Steric number = 5, trigonal bipyramidal geometry).",
      "Step 2: An axial P-Cl bond lies at 90° to all three equatorial P-Cl bonds. Hence, each axial bond pair suffers THREE 90° electron-pair repulsions.",
      "Step 3: An equatorial P-Cl bond lies at 120° to the other two equatorial bonds and 90° to the two axial bonds. Hence, each equatorial bond pair suffers only TWO 90° repulsions (120° repulsions are negligible).",
      "Step 4: Due to greater repulsive force (3 vs 2), the axial bond pairs are pushed further away from the central Phosphorus nucleus to minimize repulsion.",
      "Step 5: Consequently, axial bonds are longer (240 pm) and weaker than equatorial bonds (202 pm), explaining why PCl₅ easily dissociates into PCl₃ + Cl₂ upon heating!"
    ],
    "ans": "Axial bond pairs suffer three 90° repulsions vs two for equatorial pairs (Option A)",
    "trap": "All 5 attached atoms are identical chlorine atoms! The bond asymmetry arises purely from the non-equivalent 3D spatial geometry.",
    "distractorTraps": {
      "B": "sp³d is often conceptualized as sp² + pd_z², but the physical cause of elongation is 90° repulsion balance.",
      "C": "All five chlorines have identical electronegativity.",
      "D": "PCl₅ exists stably in the gas phase at moderate temperatures."
    },
    "targetTab": "tab-hybridization",
    "simParams": {},
    "simSummary": [
      "PCl₅ (sp³d Trigonal Bipyramidal)",
      "3 Equatorial P-Cl: 202 pm (Shorter, Stronger)",
      "2 Axial P-Cl: 240 pm (Longer, Weaker)",
      "Dissociation: PCl₅ → PCl₃ + Cl₂"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Axial bond pairs suffer three 90° repulsions vs two for equatorial pairs (Option A).",
    "takeaway": "Transfer rule: start from In sp³d trigonal bipyramidal: Axial pairs suffer 3 × 90° bp-bp repulsions; Equatorial pairs suffer 2 × 90° bp-bp repulsions; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q05",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 30th January Morning Shift",
    "subtab": 6,
    "subtabName": "Hydrogen Bonding & Physical Properties",
    "year": "2025",
    "q": "ortho-Nitrophenol is steam volatile and has a lower boiling point than para-nitrophenol because:",
    "options": [
      {
        "key": "A",
        "text": "o-Nitrophenol exhibits intramolecular H-bonding (chelation), while p-nitrophenol exhibits intermolecular H-bonding."
      },
      {
        "key": "B",
        "text": "o-Nitrophenol has a higher molecular weight."
      },
      {
        "key": "C",
        "text": "p-Nitrophenol has intramolecular H-bonding."
      },
      {
        "key": "D",
        "text": "o-Nitrophenol is non-polar."
      }
    ],
    "correct": "A",
    "formula": "Intramolecular H-bonding prevents association with neighboring molecules; Intermolecular H-bonding causes molecular association.",
    "steps": [
      "Step 1: In ortho-nitrophenol, the -OH and -NO₂ groups are adjacent (1,2-positions on benzene ring).",
      "Step 2: The phenolic hydrogen forms a 6-membered planar ring with the oxygen of the adjacent nitro group: INTRAMOLECULAR Hydrogen Bonding (chelation).",
      "Step 3: This internal bonding prevents the molecule from associating with neighboring molecules, keeping it as discrete, non-associated units with low boiling point and high steam volatility.",
      "Step 4: In para-nitrophenol, the -OH and -NO₂ groups are far apart (1,4-positions). Intramolecular H-bonding is geometrically impossible!",
      "Step 5: Instead, p-nitrophenol forms strong INTERMOLECULAR Hydrogen Bonds between adjacent molecules, creating extensive molecular associations that require much higher thermal energy to vaporize."
    ],
    "ans": "o-Nitrophenol exhibits intramolecular H-bonding; p-nitrophenol exhibits intermolecular H-bonding (Option A)",
    "trap": "Do not swap the two! ortho = internal chelation (steam volatile); para = intermolecular association (high boiling point).",
    "distractorTraps": {
      "B": "Both are constitutional isomers with identical molecular weight (139.11 g/mol).",
      "C": "Inverted the positions: para groups are too far apart for internal bonding.",
      "D": "Both isomers have polar bonds."
    },
    "targetTab": "tab-hbonding",
    "simParams": {},
    "simSummary": [
      "o-Nitrophenol: Intramolecular H-Bond (Cheled 6-Ring) → Steam Volatile",
      "p-Nitrophenol: Intermolecular H-Bond (Linear Chains) → High BP"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select o-Nitrophenol exhibits intramolecular H-bonding; p-nitrophenol exhibits intermolecular H-bonding (Option A).",
    "takeaway": "Transfer rule: start from Intramolecular H-bonding prevents association with neighboring molecules; Intermolecular H-bonding causes molecular association; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q06",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 27th January Morning Shift",
    "subtab": 5,
    "subtabName": "Molecular Orbital Theory (MOT)",
    "year": "2024",
    "q": "According to Molecular Orbital Theory (MOT), which of the following homonuclear diatomic species is paramagnetic with two unpaired electrons in degenerate π orbitals despite having an even total number of electrons?",
    "options": [
      {
        "key": "A",
        "text": "B₂ and O₂"
      },
      {
        "key": "B",
        "text": "C₂ and N₂"
      },
      {
        "key": "C",
        "text": "Li₂ and Be₂"
      },
      {
        "key": "D",
        "text": "N₂ and O₂²⁻"
      }
    ],
    "correct": "A",
    "formula": "B₂ (10e⁻): π_2p_x¹ = π_2p_y¹ (2 unpaired e⁻). O₂ (16e⁻): π*_2p_x¹ = π*_2p_y¹ (2 unpaired e⁻)",
    "steps": [
      "Step 1: Write MOT configuration for B₂ (10 electrons, ≤ 14e⁻ regime with 2s-2p mixing crossover): σ_1s² σ*_1s² σ_2s² σ*_2s² (π_2p_x¹ = π_2p_y¹). The last two electrons singly occupy the degenerate bonding π_2p orbitals with parallel spins ⇒ Paramagnetic (2 unpaired electrons).",
      "Step 2: Write MOT configuration for C₂ (12 electrons): σ_1s² σ*_1s² σ_2s² σ*_2s² (π_2p_x² = π_2p_y²). All electrons are paired ⇒ Diamagnetic.",
      "Step 3: Write MOT configuration for O₂ (16 electrons, > 14e⁻ regime without crossover): σ_1s² σ*_1s² σ_2s² σ*_2s² σ_2p_z² (π_2p_x² = π_2p_y²) (π*_2p_x¹ = π*_2p_y¹). The last two electrons singly occupy the degenerate antibonding π* orbitals ⇒ Paramagnetic (2 unpaired electrons).",
      "Step 4: Therefore, both B₂ and O₂ have two unpaired electrons in degenerate π orbitals and are paramagnetic."
    ],
    "ans": "B₂ and O₂ (Option A)",
    "trap": "Lewis electron-dot structures erroneously predict both B₂ and O₂ to have only paired electrons (diamagnetic). MOT's successful prediction of paramagnetism was historical proof of molecular orbital theory!",
    "distractorTraps": {
      "B": "C₂ and N₂ have all paired electrons and are diamagnetic.",
      "C": "Li₂ is diamagnetic; Be₂ has bond order 0 and does not exist.",
      "D": "N₂ and O₂²⁻ have all paired electrons."
    },
    "targetTab": "tab-mot",
    "simParams": {
      "electrons": 16
    },
    "simSummary": [
      "B₂ (10 e⁻): π_2p_x¹ = π_2p_y¹ (2 unpaired e⁻, Paramagnetic)",
      "O₂ (16 e⁻): π*_2p_x¹ = π*_2p_y¹ (2 unpaired e⁻, Paramagnetic)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.electrons"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds electrons only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select B₂ and O₂ (Option A).",
    "takeaway": "Transfer rule: start from B₂ (10e⁻): π_2p_x¹ = π_2p_y¹ (2 unpaired e⁻); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q07",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 25th January Evening Shift",
    "subtab": 3,
    "subtabName": "Vectorial Dipole Moments",
    "year": "2023",
    "q": "Both ammonia (NH₃) and nitrogen trifluoride (NF₃) have trigonal pyramidal geometries with one lone pair on nitrogen. However, the dipole moment of NH₃ (1.47 D) is substantially greater than that of NF₃ (0.24 D) because:",
    "options": [
      {
        "key": "A",
        "text": "In NH₃, the lone-pair orbital dipole and N-H bond dipoles reinforce each other; in NF₃, the lone-pair dipole opposes the N-F bond dipoles."
      },
      {
        "key": "B",
        "text": "Nitrogen is more electronegative than fluorine."
      },
      {
        "key": "C",
        "text": "NF₃ is a planar molecule while NH₃ is pyramidal."
      },
      {
        "key": "D",
        "text": "The N-H bond length is greater than the N-F bond length."
      }
    ],
    "correct": "A",
    "formula": "μ_net = μ_lone-pair + ∑ μ_bond (Vector addition)",
    "steps": [
      "Step 1: Both NH₃ and NF₃ have sp³ hybridized nitrogen with 3 bond pairs and 1 lone pair (trigonal pyramidal geometry).",
      "Step 2: In NH₃, EN(N) = 3.0 > EN(H) = 2.1. The three N-H bond dipoles point toward nitrogen (upward toward the apex), in the same direction as the upward orbital dipole of the lone pair. The vectors reinforce constructively ⇒ μ_net = 1.47 D.",
      "Step 3: In NF₃, EN(F) = 4.0 > EN(N) = 3.0. The three N-F bond dipoles point downward away from nitrogen toward fluorine, OPPOSING the upward lone-pair dipole. The vectors cancel destructively ⇒ μ_net = 0.24 D.",
      "Step 4: Vectorial cancellation explains why NF₃ has a remarkably small dipole moment despite having highly polar N-F bonds."
    ],
    "ans": "In NH₃, lone pair and bond dipoles reinforce; in NF₃, they oppose (Option A)",
    "trap": "Never judge net dipole by bond polarity alone! Fluorine is far more electronegative than hydrogen, but vectorial direction causes nearly complete cancellation in NF₃.",
    "distractorTraps": {
      "B": "Factually incorrect: EN(F) = 4.0 is much higher than EN(N) = 3.0.",
      "C": "Both molecules are trigonal pyramidal.",
      "D": "Bond length difference does not account for vector opposition."
    },
    "targetTab": "tab-dipole",
    "simParams": {
      "molecule": "NH3_vs_NF3"
    },
    "simSummary": [
      "NH₃: N-H dipoles add to lone pair vector (μ = 1.47 D)",
      "NF₃: N-F dipoles oppose lone pair vector (μ = 0.24 D)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select In NH₃, lone pair and bond dipoles reinforce; in NF₃, they oppose (Option A).",
    "takeaway": "Transfer rule: start from μ_net = μ_lone-pair + ∑ μ_bond (Vector addition); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q08",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 29th January Evening Shift",
    "subtab": 1,
    "subtabName": "Lewis Structures & Formal Charge",
    "year": "2025",
    "q": "In the resonance contributor of the ozone molecule (O₃: O_a - O_b = O_c), the formal charges on the single-bonded terminal oxygen (O_a), the central oxygen (O_b), and the double-bonded terminal oxygen (O_c) are respectively:",
    "options": [
      {
        "key": "A",
        "text": "-1, +1, 0"
      },
      {
        "key": "B",
        "text": "0, +1, -1"
      },
      {
        "key": "C",
        "text": "+1, -1, 0"
      },
      {
        "key": "D",
        "text": "0, 0, 0"
      }
    ],
    "correct": "A",
    "formula": "Formal Charge = Valence e⁻ - Non-bonding e⁻ - ½(Bonding e⁻)",
    "steps": [
      "Step 1: Apply the universal formal charge formula: FC = V - L - ½ B.",
      "Step 2: For central oxygen O_b: V = 6, 1 lone pair (L = 2), 1 single bond + 1 double bond (B = 6). FC(O_b) = 6 - 2 - ½(6) = 6 - 2 - 3 = +1.",
      "Step 3: For terminal single-bonded oxygen O_a: V = 6, 3 lone pairs (L = 6), 1 single bond (B = 2). FC(O_a) = 6 - 6 - ½(2) = 6 - 6 - 1 = -1.",
      "Step 4: For terminal double-bonded oxygen O_c: V = 6, 2 lone pairs (L = 4), 1 double bond (B = 4). FC(O_c) = 6 - 4 - ½(4) = 6 - 4 - 2 = 0.",
      "Step 5: Check sum of formal charges: (-1) + (+1) + 0 = 0 (neutral molecule). Hence the charges are -1, +1, 0."
    ],
    "ans": "-1, +1, 0 (Option A)",
    "trap": "Always count individual non-bonding electrons L, not electron pairs! In O_a, 3 lone pairs = 6 non-bonding electrons.",
    "distractorTraps": {
      "B": "Inverted the terminal oxygen positions.",
      "C": "Assigned positive charge to the terminal oxygen.",
      "D": "Assumed all atoms in a neutral molecule have zero formal charge."
    },
    "targetTab": "tab-lewis",
    "simParams": {
      "molecule": "O3"
    },
    "simSummary": [
      "O₃ Lewis Structure",
      "Central O: FC = 6 - 2 - 3 = +1",
      "Single-bonded O: FC = 6 - 6 - 1 = -1",
      "Double-bonded O: FC = 6 - 4 - 2 = 0"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select -1, +1, 0 (Option A).",
    "takeaway": "Transfer rule: start from Formal Charge = Valence e⁻ - Non-bonding e⁻ - ½(Bonding e⁻); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q09",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 31st January Evening Shift",
    "subtab": 2,
    "subtabName": "3D VSEPR & Bent's Rule",
    "year": "2024",
    "q": "The total number of lone pairs on the central atom of XeF₄, SF₄, and ClF₃ respectively are:",
    "options": [
      {
        "key": "A",
        "text": "2, 1, 2"
      },
      {
        "key": "B",
        "text": "1, 2, 2"
      },
      {
        "key": "C",
        "text": "2, 2, 1"
      },
      {
        "key": "D",
        "text": "0, 1, 2"
      }
    ],
    "correct": "A",
    "formula": "Lone pairs LP = ½ [V - B], where V = valence e⁻ of central atom, B = bonded monovalent atoms",
    "steps": [
      "Step 1: For XeF₄: Xe has 8 valence electrons. Steric Number = 4 σ-bonds + ½(8 - 4) = 4 + 2 = 6 (sp³d²). Central atom has 2 lone pairs.",
      "Step 2: For SF₄: S has 6 valence electrons. Steric Number = 4 σ-bonds + ½(6 - 4) = 4 + 1 = 5 (sp³d). Central atom has 1 lone pair (see-saw).",
      "Step 3: For ClF₃: Cl has 7 valence electrons. Steric Number = 3 σ-bonds + ½(7 - 3) = 3 + 2 = 5 (sp³d). Central atom has 2 lone pairs (T-shaped).",
      "Step 4: Compiling lone pairs on central atoms: XeF₄ = 2, SF₄ = 1, ClF₃ = 2."
    ],
    "ans": "2, 1, 2 (Option A)",
    "trap": "Do not count lone pairs on fluorine atoms! The question specifically demands lone pairs ON THE CENTRAL ATOM.",
    "distractorTraps": {
      "B": "Swapped lone pairs of XeF₄ and SF₄.",
      "C": "Assumed SF₄ has 2 lone pairs like XeF₄.",
      "D": "Assumed XeF₄ is tetrahedral with 0 lone pairs."
    },
    "targetTab": "tab-vsepr",
    "simParams": {
      "molecule": "XeF4"
    },
    "simSummary": [
      "XeF₄: 2 LP (Square Planar)",
      "SF₄: 1 LP (See-saw)",
      "ClF₃: 2 LP (T-shaped)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select 2, 1, 2 (Option A).",
    "takeaway": "Transfer rule: start from Lone pairs LP = ½ [V - B], where V = valence e⁻ of central atom, B = bonded monovalent atoms; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q10",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 29th January Morning Shift",
    "subtab": 1,
    "subtabName": "Lewis Structure & Formal Charge",
    "year": "2024",
    "q": "The formal charge on each oxygen atom in the resonance hybrid of the carbonate ion (CO₃²⁻) is:",
    "options": [
      {
        "key": "A",
        "text": "-2 / 3"
      },
      {
        "key": "B",
        "text": "-1 / 3"
      },
      {
        "key": "C",
        "text": "-1"
      },
      {
        "key": "D",
        "text": "-2"
      }
    ],
    "correct": "A",
    "formula": "Average Formal Charge = (Total ionic charge) / (Number of equivalent resonating oxygen atoms)",
    "steps": [
      "Step 1: Write the canonical Lewis resonance forms of CO₃²⁻. Carbon forms 1 C=O double bond and 2 C-O⁻ single bonds.",
      "Step 2: Total formal charge on the oxygen atoms is -2 (since central carbon has FC = 4 - 0 - ½(8) = 0).",
      "Step 3: All 3 oxygen atoms participate equally in resonance delocalization across 3 equivalent canonical forms.",
      "Step 4: Average formal charge per oxygen atom: FC_avg = -2 / 3 ≈ -0.67.",
      "Step 5: The C-O bond order in the hybrid is 4/3 = 1.33 (4 bonding pairs shared over 3 C-O linkages)."
    ],
    "ans": "-2 / 3 (Option A)",
    "trap": "Do not report the charge of a single localized canonical form (-1 on single-bonded oxygen, 0 on double-bonded); the real molecule is the delocalized resonance hybrid (-2/3 on all oxygens)!",
    "distractorTraps": {
      "B": "Divided -1 by 3 instead of total charge -2.",
      "C": "Reported the charge in a localized single-bonded canonical Lewis structure.",
      "D": "Reported the total charge of the polyatomic ion."
    },
    "targetTab": "tab-lewis",
    "simParams": {
      "molecule": "CO3"
    },
    "simSummary": [
      "CO₃²⁻ Hybrid: 3 equivalent O atoms",
      "Average FC = -2/3",
      "Bond Order = 4/3 = 1.33"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select -2 / 3 (Option A).",
    "takeaway": "Transfer rule: start from Average Formal Charge = (Total ionic charge) / (Number of equivalent resonating oxygen atoms); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q11",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 6th April Morning Shift",
    "subtab": 5,
    "subtabName": "Molecular Orbital Theory (MOT)",
    "year": "2023",
    "q": "According to Molecular Orbital Theory (MOT), in which of the following diatomic species does the double bond consist of ONLY π bonds with NO σ bond?",
    "options": [
      {
        "key": "A",
        "text": "C₂"
      },
      {
        "key": "B",
        "text": "O₂"
      },
      {
        "key": "C",
        "text": "N₂"
      },
      {
        "key": "D",
        "text": "B₂"
      }
    ],
    "correct": "A",
    "formula": "Electronic configuration of C₂ (12 e⁻): σ₁ₛ² σ*₁ₛ² σ₂ₛ² σ*₂ₛ² (π₂ₚ_x² = π₂ₚ_y²)",
    "steps": [
      "Step 1: Carbon has Z = 6 ≤ 7, so 2s-2p mixing occurs, pushing σ₂ₚ_z above the degenerate π₂ₚ orbitals.",
      "Step 2: Neutral C₂ has 12 electrons. Fill molecular orbitals:",
      "        σ₁ₛ² σ*₁ₛ² σ₂ₛ² σ*₂ₛ² (π₂ₚ_x² = π₂ₚ_y²).",
      "Step 3: The 4 bonding electrons responsible for the double bond (BO = (8 - 4)/2 = 2) reside strictly in the degenerate π₂ₚ_x and π₂ₚ_y orbitals.",
      "Step 4: The σ₂ₚ_z orbital is completely empty! Hence the double bond in C₂ consists exclusively of two π bonds and zero σ bonds."
    ],
    "ans": "C₂ (Option A)",
    "trap": "Valence Bond Theory dogma states that a double bond is always 1σ + 1π. C₂ is the famous MOT proof that a double bond can consist solely of two π bonds!",
    "distractorTraps": {
      "B": "O₂ has 1 σ and 1 π bond (BO = 2 with 2 unpaired electrons in π*).",
      "C": "N₂ has a triple bond (1 σ + 2 π).",
      "D": "B₂ has a single bond (BO = 1) consisting of two half π bonds."
    },
    "targetTab": "tab-mot",
    "simParams": {
      "electrons": 12
    },
    "simSummary": [
      "C₂ (12 e⁻): π₂ₚ_x² = π₂ₚ_y²",
      "BO = 2.0 (Double π bond)",
      "Zero σ bonds",
      "Diamagnetic"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.electrons"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds electrons only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select C₂ (Option A).",
    "takeaway": "Transfer rule: start from Electronic configuration of C₂ (12 e⁻): σ₁ₛ² σ*₁ₛ² σ₂ₛ² σ*₂ₛ² (π₂ₚ_x² = π₂ₚ_y²); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q12",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 11th April Evening Shift",
    "subtab": 4,
    "subtabName": "Hybridization & PCl₅ Axial Elongation",
    "year": "2023",
    "q": "In gaseous PCl₅, the axial P-Cl bonds are longer (240 pm) than the equatorial P-Cl bonds (202 pm) because:",
    "options": [
      {
        "key": "A",
        "text": "Axial bond pairs experience three 90° repulsions, whereas equatorial pairs experience only two 90° repulsions"
      },
      {
        "key": "B",
        "text": "Axial bonds are formed by sp² hybrid orbitals and equatorial bonds by pd hybrid orbitals"
      },
      {
        "key": "C",
        "text": "Chlorine atoms at axial positions have greater electronegativity"
      },
      {
        "key": "D",
        "text": "Equatorial bonds have greater d-character than axial bonds"
      }
    ],
    "correct": "A",
    "formula": "sp³d = sp² (equatorial, 120°) + pd (axial, 180°). Repulsions at 90°: Axial = 3, Equatorial = 2.",
    "steps": [
      "Step 1: Trigonal bipyramidal geometry (sp³d) has two geometrically distinct sets of bonds: 3 equatorial and 2 axial.",
      "Step 2: An equatorial bond makes two 90° angles (with the two axial bonds) and two 120° angles (with equatorial bonds).",
      "Step 3: An axial bond makes three 90° angles (with all three equatorial bonds).",
      "Step 4: Since electron-pair repulsion is extremely sensitive to angle (90° repulsions are far stronger than 120°), the three 90° repulsions push the axial chlorines further away from phosphorus.",
      "Step 5: Therefore, axial bonds lengthen to 240 pm and are significantly weaker, explaining why PCl₅ dissociates upon mild heating: PCl₅ → PCl₃ + Cl₂."
    ],
    "ans": "Axial bond pairs experience three 90° repulsions, whereas equatorial pairs experience only two 90° repulsions (Option A)",
    "trap": "Notice the orbital composition: axial bonds are formed from p_z + d_z² (zero s-character, longer), while equatorial bonds are formed from sp² (33% s-character, shorter).",
    "distractorTraps": {
      "B": "Inverted orbital allocation: equatorial is sp² and axial is pd, not vice-versa.",
      "C": "All chlorine atoms have identical electronegativity.",
      "D": "Axial bonds use the d_z² orbital, so axial has more d-character."
    },
    "targetTab": "tab-hybridization",
    "simParams": {
      "mode": "ground"
    },
    "simSummary": [
      "Axial: 240 pm (Three 90° repulsions)",
      "Equatorial: 202 pm (Two 90° repulsions)",
      "Cleavage: PCl₅ → PCl₃ + Cl₂"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.mode"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds mode only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Axial bond pairs experience three 90° repulsions, whereas equatorial pairs experience only two 90° repulsions (Option A).",
    "takeaway": "Transfer rule: start from sp³d = sp² (equatorial, 120°) + pd (axial, 180°); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q13",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 28th July Morning Shift",
    "subtab": 3,
    "subtabName": "Vectorial Dipole Sum",
    "year": "2022",
    "q": "Among the following molecules, which one has a non-zero permanent dipole moment (μ ≠ 0)?",
    "options": [
      {
        "key": "A",
        "text": "NF₃"
      },
      {
        "key": "B",
        "text": "BF₃"
      },
      {
        "key": "C",
        "text": "BeF₂"
      },
      {
        "key": "D",
        "text": "CO₂"
      }
    ],
    "correct": "A",
    "formula": "μ_net = ∑ μ_bond + μ_lp ≠ 0 for pyramidal geometry",
    "steps": [
      "Step 1: Check BF₃: Trigonal planar (sp²), 120° bond angles. The three equal B-F bond dipoles cancel completely by symmetry ⇒ μ = 0.",
      "Step 2: Check BeF₂: Linear (sp), 180° bond angle. The two equal Be-F bond dipoles point in opposite directions ⇒ μ = 0.",
      "Step 3: Check CO₂: Linear (sp), 180° bond angle. The two C=O bond dipoles cancel ⇒ μ = 0.",
      "Step 4: Check NF₃: Trigonal pyramidal (sp³) with 1 lone pair on N. The geometry is non-planar and asymmetric, so vector sum of bond dipoles and lone pair dipole does not cancel ⇒ μ = 0.24 D ≠ 0."
    ],
    "ans": "NF₃ (Option A)",
    "trap": "Although NF₃ has a very small dipole moment (0.24 D) because N-F dipoles oppose the lone pair, it is strictly NON-ZERO because geometry is trigonal pyramidal!",
    "distractorTraps": {
      "B": "BF₃ is perfectly planar with 120° symmetry, so μ = 0.",
      "C": "BeF₂ is linear and symmetrical, μ = 0.",
      "D": "CO₂ is linear and symmetrical, μ = 0."
    },
    "targetTab": "tab-dipole",
    "simParams": {
      "dipolePair": "NH3_NF3"
    },
    "simSummary": [
      "NF₃: Pyramidal, μ = 0.24 D (≠ 0)",
      "BF₃: Planar, μ = 0",
      "CO₂, BeF₂: Linear, μ = 0"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.dipolePair"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds dipolePair only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select NF₃ (Option A).",
    "takeaway": "Transfer rule: start from μ_net = ∑ μ_bond + μ_lp ≠ 0 for pyramidal geometry; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q14",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 25th June Evening Shift",
    "subtab": 2,
    "subtabName": "3D VSEPR & Bent's Rule",
    "year": "2022",
    "q": "The hybridization of the central atom and the molecular shape of BrF₅ are:",
    "options": [
      {
        "key": "A",
        "text": "sp³d² and Square Pyramidal"
      },
      {
        "key": "B",
        "text": "sp³d and Trigonal Bipyramidal"
      },
      {
        "key": "C",
        "text": "sp³d² and Octahedral"
      },
      {
        "key": "D",
        "text": "sp³d and See-saw"
      }
    ],
    "correct": "A",
    "formula": "Steric Number = Bond Pairs + Lone Pairs = 5 + 1 = 6 (sp³d²). Molecular geometry = Square Pyramidal.",
    "steps": [
      "Step 1: Bromine has 7 valence electrons in its outer shell.",
      "Step 2: 5 valence electrons form 5 single σ-bonds with 5 fluorine atoms.",
      "Step 3: Remaining 2 electrons form 1 lone pair on Br.",
      "Step 4: Steric Number = 5 bond pairs + 1 lone pair = 6 ⇒ sp³d² hybridization.",
      "Step 5: Electron geometry is Octahedral. Because 1 position is occupied by a lone pair, the molecular shape is Square Pyramidal."
    ],
    "ans": "sp³d² and Square Pyramidal (Option A)",
    "trap": "Do not confuse ELECTRON GEOMETRY (octahedral) with MOLECULAR SHAPE (square pyramidal, which considers only atomic nuclei)!",
    "distractorTraps": {
      "B": "Assumed 5 bonds implies steric number 5 (sp³d), forgetting the lone pair.",
      "C": "Reported electron pair geometry (Octahedral) instead of molecular shape.",
      "D": "Confused with SF₄ (4 bonds + 1 lone pair = see-saw)."
    },
    "targetTab": "tab-vsepr",
    "simParams": {
      "molecule": "XeF4"
    },
    "simSummary": [
      "BrF₅: 5 BP + 1 LP = 6 domains",
      "Hybridization = sp³d²",
      "Shape = Square Pyramidal"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select sp³d² and Square Pyramidal (Option A).",
    "takeaway": "Transfer rule: start from Steric Number = Bond Pairs + Lone Pairs = 5 + 1 = 6 (sp³d²); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q15",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 25th February Morning Shift",
    "subtab": 6,
    "subtabName": "Hydrogen Bonding & Boiling Points",
    "year": "2021",
    "q": "The correct order of bond dissociation enthalpy of halogen molecules (X₂) is:",
    "options": [
      {
        "key": "A",
        "text": "Cl₂ > Br₂ > F₂ > I₂"
      },
      {
        "key": "B",
        "text": "F₂ > Cl₂ > Br₂ > I₂"
      },
      {
        "key": "C",
        "text": "Cl₂ > F₂ > Br₂ > I₂"
      },
      {
        "key": "D",
        "text": "I₂ > Br₂ > Cl₂ > F₂"
      }
    ],
    "correct": "A",
    "formula": "Bond Dissociation Enthalpies: Cl₂ (242.6) > Br₂ (192.8) > F₂ (158.8) > I₂ (151.1 kJ/mol)",
    "steps": [
      "Step 1: In general, bond dissociation energy decreases down the group as bond length increases: Cl₂ > Br₂ > I₂.",
      "Step 2: Fluorine (F₂) has an exceptionally small internuclear distance (142 pm).",
      "Step 3: The non-bonding lone pairs in the compact 2p orbitals experience severe interelectronic repulsion across the single F-F bond.",
      "Step 4: This intense lone pair-lone pair repulsion significantly weakens the F-F bond (158.8 kJ/mol), dropping its dissociation energy below Cl₂ and Br₂!",
      "Step 5: The verified experimental order is: Cl₂ > Br₂ > F₂ > I₂."
    ],
    "ans": "Cl₂ > Br₂ > F₂ > I₂ (Option A)",
    "trap": "The Halogen Anomaly: students assume F₂ has the highest bond energy because it has the shortest bond length. Intense 2p lone pair repulsion makes it 3rd, not 1st!",
    "distractorTraps": {
      "B": "Standard periodic trend fallacy (assuming shortest bond F-F is strongest).",
      "C": "Placed F₂ second instead of third.",
      "D": "Inverted the entire periodic order."
    },
    "targetTab": "tab-hbonding",
    "simParams": {
      "pair": "ortho_para"
    },
    "simSummary": [
      "Cl₂ (242.6 kJ/mol) > Br₂ (192.8) > F₂ (158.8) > I₂ (151.1)",
      "F₂ weakened by 2p lone-pair repulsions"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.pair"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds pair only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Cl₂ > Br₂ > F₂ > I₂ (Option A).",
    "takeaway": "Transfer rule: start from Bond Dissociation Enthalpies: Cl₂ (242; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q16",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 20th July Evening Shift",
    "subtab": 2,
    "subtabName": "3D VSEPR & Bent's Rule",
    "year": "2021",
    "q": "The hybridization and geometry of the triiodide ion (I₃⁻) are:",
    "options": [
      {
        "key": "A",
        "text": "sp³d and Linear"
      },
      {
        "key": "B",
        "text": "sp³ and Bent"
      },
      {
        "key": "C",
        "text": "sp³d² and Linear"
      },
      {
        "key": "D",
        "text": "sp and Linear"
      }
    ],
    "correct": "A",
    "formula": "Steric Number = 2 σ-bonds + 3 lone pairs = 5 (sp³d). Equatorial lone pairs minimize 90° repulsion ⇒ Linear shape.",
    "steps": [
      "Step 1: Central iodine atom has 7 valence electrons + 1 extra electron (negative charge) = 8 electrons.",
      "Step 2: 2 electrons are shared with two terminal iodine atoms to form 2 σ-bonds.",
      "Step 3: Remaining 6 electrons form 3 lone pairs on the central iodine.",
      "Step 4: Steric Number = 2 bond pairs + 3 lone pairs = 5 ⇒ sp³d hybridization (Trigonal Bipyramidal electron geometry).",
      "Step 5: According to Bent's Rule / VSEPR, the 3 bulky lone pairs occupy the equatorial positions (120° apart) to minimize 90° repulsions.",
      "Step 6: The two axial I-I bonds form a straight line with bond angle 180° ⇒ Molecular shape is Linear."
    ],
    "ans": "sp³d and Linear (Option A)",
    "trap": "Do not assume a linear molecule must be sp hybridized! I₃⁻ and XeF₂ are linear with sp³d hybridization because 3 lone pairs occupy equatorial sites.",
    "distractorTraps": {
      "B": "Assumed I₃⁻ is bent like ICl₂⁺ or water.",
      "C": "Calculated steric number 6.",
      "D": "Assumed linear geometry implies sp hybridization (BeCl₂ fallacy)."
    },
    "targetTab": "tab-vsepr",
    "simParams": {
      "molecule": "XeF4"
    },
    "simSummary": [
      "I₃⁻: 2 BP + 3 LP = 5 (sp³d)",
      "3 LP equatorial at 120°",
      "Linear shape, 180° angle"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.molecule"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds molecule only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select sp³d and Linear (Option A).",
    "takeaway": "Transfer rule: start from Steric Number = 2 σ-bonds + 3 lone pairs = 5 (sp³d); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q17",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 5th September Morning Shift",
    "subtab": 6,
    "subtabName": "Hydrogen Bonding & Boiling Points",
    "year": "2020",
    "q": "The correct order of boiling points for the Group 16 hydrides (chalcogen hydrides) is:",
    "options": [
      {
        "key": "A",
        "text": "H₂O > H₂Te > H₂Se > H₂S"
      },
      {
        "key": "B",
        "text": "H₂O > H₂S > H₂Se > H₂Te"
      },
      {
        "key": "C",
        "text": "H₂Te > H₂Se > H₂S > H₂O"
      },
      {
        "key": "D",
        "text": "H₂S > H₂Se > H₂Te > H₂O"
      }
    ],
    "correct": "A",
    "formula": "H₂O (373 K) >> H₂Te (269 K) > H₂Se (232 K) > H₂S (213 K)",
    "steps": [
      "Step 1: From H₂S to H₂Te, molecular mass increases ⇒ van der Waals dispersion forces increase ⇒ boiling point increases: H₂Te > H₂Se > H₂S.",
      "Step 2: However, oxygen is highly electronegative with a small atomic radius.",
      "Step 3: H₂O forms an extensive 3D network of strong intermolecular hydrogen bonds (4 H-bonds per H₂O molecule in tetrahedral geometry).",
      "Step 4: This massive hydrogen bonding energy pushes the boiling point of H₂O to 373 K (100°C), far above all other hydrides.",
      "Step 5: Overall order: H₂O (100°C) > H₂Te (-4°C) > H₂Se (-41°C) > H₂S (-60°C)."
    ],
    "ans": "H₂O > H₂Te > H₂Se > H₂S (Option A)",
    "trap": "Notice H₂S has the LOWEST boiling point of all, not the second highest! Do not assume monotonic decrease from H₂O.",
    "distractorTraps": {
      "B": "Assumed boiling point decreases monotonically down the group.",
      "C": "Ignored hydrogen bonding and ranked strictly by molar mass.",
      "D": "Inverted the order of the heavier hydrides."
    },
    "targetTab": "tab-hbonding",
    "simParams": {
      "pair": "ethanol_ether"
    },
    "simSummary": [
      "H₂O: 373 K (Strong H-bonds)",
      "H₂Te: 269 K, H₂Se: 232 K, H₂S: 213 K",
      "H₂S has the lowest boiling point"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.pair"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds pair only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select H₂O > H₂Te > H₂Se > H₂S (Option A).",
    "takeaway": "Transfer rule: start from H₂O (373 K) >> H₂Te (269 K) > H₂Se (232 K) > H₂S (213 K); enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q18",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 7th January Morning Shift",
    "subtab": 4,
    "subtabName": "Hybridization & PCl₅ Axial Elongation",
    "year": "2020",
    "q": "In the solid state, PCl₅ exists as an ionic compound composed of:",
    "options": [
      {
        "key": "A",
        "text": "[PCl₄]⁺ (tetrahedral) and [PCl₆]⁻ (octahedral)"
      },
      {
        "key": "B",
        "text": "[PCl₂]⁺ (linear) and [PCl₆]⁻ (octahedral)"
      },
      {
        "key": "C",
        "text": "[PCl₄]⁺ (square planar) and [PCl₆]⁻ (octahedral)"
      },
      {
        "key": "D",
        "text": "Discrete trigonal bipyramidal PCl₅ molecules held by van der Waals forces"
      }
    ],
    "correct": "A",
    "formula": "2 PCl₅(s) → [PCl₄]⁺ [PCl₆]⁻. [PCl₄]⁺ is sp³ (tetrahedral); [PCl₆]⁻ is sp³d² (octahedral).",
    "steps": [
      "Step 1: In the gas and liquid phases, PCl₅ exists as discrete trigonal bipyramidal molecules with sp³d hybridization.",
      "Step 2: In the solid state, to minimize steric repulsions and achieve electrostatic lattice stabilization, it auto-ionizes:",
      "        2 PCl₅(s) ⇌ [PCl₄]⁺ + [PCl₆]⁻.",
      "Step 3: Cation [PCl₄]⁺: P has 5 - 1 = 4 valence electrons forming 4 σ-bonds ⇒ sp³ hybridization, Tetrahedral geometry.",
      "Step 4: Anion [PCl₆]⁻: P has 5 + 1 = 6 valence electrons forming 6 σ-bonds ⇒ sp³d² hybridization, Octahedral geometry.",
      "Step 5: Contrast with solid PBr₅, which exists as [PBr₄]⁺ Br⁻ due to the large steric bulk of bromine preventing [PBr₆]⁻ formation!"
    ],
    "ans": "[PCl₄]⁺ (tetrahedral) and [PCl₆]⁻ (octahedral) (Option A)",
    "trap": "Notice the phase state! In gas phase PCl₅ is molecular TBP (sp³d), but in SOLID STATE it is ionic [PCl₄]⁺ [PCl₆]⁻!",
    "distractorTraps": {
      "B": "Incorrect formula for cation [PCl₂]⁺.",
      "C": "[PCl₄]⁺ is tetrahedral (sp³), not square planar (dsp²).",
      "D": "Discrete TBP molecules exist only in GAS or liquid phase, not solid state."
    },
    "targetTab": "tab-hybridization",
    "simParams": {
      "mode": "thermal"
    },
    "simSummary": [
      "Solid PCl₅: [PCl₄]⁺ [PCl₆]⁻",
      "[PCl₄]⁺: sp³ Tetrahedral",
      "[PCl₆]⁻: sp³d² Octahedral"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.mode"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds mode only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select [PCl₄]⁺ (tetrahedral) and [PCl₆]⁻ (octahedral) (Option A).",
    "takeaway": "Transfer rule: start from 2 PCl₅(s) → [PCl₄]⁺ [PCl₆]⁻; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q19",
    "num": "JEE Main 2019",
    "source": "JEE Main 2019 (Online) 10th April Morning Shift",
    "subtab": 5,
    "subtabName": "Molecular Orbital Theory (MOT)",
    "year": "2019",
    "q": "The bond order and magnetic behavior of the carbon monoxide cation (CO⁺) according to MOT are:",
    "options": [
      {
        "key": "A",
        "text": "Bond Order = 3.5 and Paramagnetic"
      },
      {
        "key": "B",
        "text": "Bond Order = 2.5 and Paramagnetic"
      },
      {
        "key": "C",
        "text": "Bond Order = 3.0 and Diamagnetic"
      },
      {
        "key": "D",
        "text": "Bond Order = 2.5 and Diamagnetic"
      }
    ],
    "correct": "B",
    "formula": "Standard classroom MO count for CO gives BO = 3. Ionization to CO⁺ removes one electron from the highest occupied valence MO; in the usual bond-order counting used for JEE-level MO diagrams, BO decreases by ½ to 2.5. An odd electron remains, so CO⁺ is paramagnetic.",
    "steps": [
      "Step 1: Neutral CO has 14 electrons and is treated as isoelectronic with N₂ in the standard introductory MO scheme, with bond order 3.",
      "Step 2: Forming CO⁺ removes one electron from the highest occupied valence molecular orbital.",
      "Step 3: In the standard JEE-level bond-order count, removal of one bonding electron decreases bond order by 0.5: BO = 3.0 - 0.5 = 2.5.",
      "Step 4: CO⁺ has an odd total electron count, so one electron is unpaired and the species is paramagnetic.",
      "Step 5: Therefore the locally audited answer is Bond Order = 2.5 and Paramagnetic."
    ],
    "ans": "Bond Order = 2.5 and Paramagnetic (Option B)",
    "trap": "Do not use the obsolete shortcut that labels the CO HOMO as simply antibonding and raises the bond order to 3.5 on ionization. For the standard classroom MO answer used here, CO⁺ is assigned bond order 2.5 and is paramagnetic.",
    "distractorTraps": {
      "A": "Uses the obsolete 3.5 shortcut by treating ionization as removal of a purely antibonding electron.",
      "C": "Keeps the neutral-CO bond order and also misses the odd-electron paramagnetism.",
      "D": "Gets the 2.5 bond order but incorrectly calls the odd-electron cation diamagnetic."
    },
    "targetTab": "tab-mot",
    "simParams": {
      "electrons": 13
    },
    "simSummary": [
      "CO⁺ · 13 electrons",
      "Locally audited BO = 2.5",
      "Paramagnetic · one unpaired electron"
    ],
    "sourceAudit": "SOURCE_UNVERIFIED",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally corrected under the standard classroom MO treatment: removing one electron from the highest occupied CO valence MO gives the commonly used bond-order result 2.5; the odd-electron cation is paramagnetic.",
    "simBindingRefs": [
      "simParams.electrons"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds electrons only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "The current ExamSIDE listing for JEE Main 2019 Online 10 April Morning does not contain this CO+ bond-order question; the attribution is therefore not accepted as verified.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Bond Order = 2.5 and Paramagnetic (Option B).",
    "takeaway": "Transfer rule: start from Standard classroom MO count for CO gives BO = 3; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "BOND-Q20",
    "num": "JEE Main 2018",
    "source": "JEE Main 2018 (Offline) 8th April Shift",
    "subtab": 6,
    "subtabName": "Hydrogen Bonding & Boiling Points",
    "year": "2018",
    "q": "Ortho-nitrophenol is more volatile in steam than para-nitrophenol because:",
    "options": [
      {
        "key": "A",
        "text": "Ortho-nitrophenol exhibits intramolecular hydrogen bonding (chelation), whereas para-nitrophenol forms intermolecular hydrogen bonds"
      },
      {
        "key": "B",
        "text": "Para-nitrophenol has a lower molecular mass than ortho-nitrophenol"
      },
      {
        "key": "C",
        "text": "Ortho-nitrophenol forms stronger intermolecular hydrogen bonds than water"
      },
      {
        "key": "D",
        "text": "Para-nitrophenol undergoes sublimation at room temperature"
      }
    ],
    "correct": "A",
    "formula": "Intramolecular H-bonding ⇒ Chelate ring ⇒ Discrete molecules ⇒ Lower BP, Steam Volatile. Intermolecular H-bonding ⇒ Association ⇒ Higher BP.",
    "steps": [
      "Step 1: In ortho-nitrophenol, the -OH and -NO₂ groups are on adjacent carbon atoms.",
      "Step 2: The hydrogen of -OH forms an intramolecular H-bond with the oxygen of -NO₂, closing a planar 6-membered chelate ring.",
      "Step 3: This intramolecular chelation shields the polar groups, preventing association with neighboring molecules ⇒ Low boiling point (216°C), steam-volatile.",
      "Step 4: In para-nitrophenol, the -OH and -NO₂ groups are far apart (at positions 1 and 4), precluding intramolecular bonding.",
      "Step 5: It forms extensive intermolecular H-bonding networks linking molecules into polymers ⇒ High boiling point (279°C), non-volatile in steam."
    ],
    "ans": "Ortho-nitrophenol exhibits intramolecular hydrogen bonding (chelation), whereas para-nitrophenol forms intermolecular hydrogen bonds (Option A)",
    "trap": "Remember: INTRAmolecular H-bonding LOWERS boiling point (makes steam-volatile); INTERmolecular H-bonding RAISES boiling point!",
    "distractorTraps": {
      "B": "They are structural isomers and have identical molecular mass (139.11 g/mol).",
      "C": "Ortho-nitrophenol does not form stronger intermolecular bonds with water.",
      "D": "Para-nitrophenol does not sublime at room temperature."
    },
    "targetTab": "tab-hbonding",
    "simParams": {
      "pair": "ortho_para"
    },
    "simSummary": [
      "o-nitrophenol: Intramolecular chelation (BP 216°C, Steam volatile)",
      "p-nitrophenol: Intermolecular association (BP 279°C)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.pair"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds pair only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: recompute the governing relation and verify that the stem constraints select Ortho-nitrophenol exhibits intramolecular hydrogen bonding (chelation), whereas para-nitrophenol forms intermolecular hydrogen bonds (Option A).",
    "takeaway": "Transfer rule: start from Intramolecular H-bonding ⇒ Chelate ring ⇒ Discrete molecules ⇒ Lower BP, Steam Volatile; enforce every structural, stoichiometric, charge or state constraint before comparing answer choices.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  }
];
