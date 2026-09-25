/**
 * Redox Reactions & Electrochemistry Fundamentals
 * Master Question Registry & Step-by-Step Solutions Database
 * Curated from ExamSIDE IIT-JEE Main Questions (2013-2026)
 */
window.JEE_QUESTIONS_DATA = [
  {
    "id": "REDOX-Q01",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 6th April Evening Shift",
    "subtab": 1,
    "subtabName": "Structural Oxidation States",
    "year": "2026",
    "q": "The oxidation state of Chromium in chromium pentoxide (CrO₅, blue butterfly peroxo compound) is:",
    "options": [
      {
        "key": "A",
        "text": "+6"
      },
      {
        "key": "B",
        "text": "+10"
      },
      {
        "key": "C",
        "text": "+5"
      },
      {
        "key": "D",
        "text": "+4"
      }
    ],
    "correct": "A",
    "formula": "CrO₅ has a butterfly structure: one oxo oxygen (=O, O.S. = -2) and two peroxo bridges (-O-O-, four oxygens each with O.S. = -1)",
    "steps": [
      "Step 1: Inspect the structure before using the usual oxygen rule. CrO₅ contains one oxo oxygen and two O–O peroxo groups; oxygen in a peroxide unit is assigned oxidation state -1.",
      "Step 2: Let the chromium oxidation state be x. The oxo oxygen contributes -2 and the four peroxo oxygens contribute 4 × (-1).",
      "Step 3: Charge balance for neutral CrO₅: x + (-2) + 4(-1) = 0, so x = +6.",
      "Step 4: The tempting x + 5(-2) = 0 calculation fails because it assumes every oxygen is ordinary oxide oxygen and ignores the O–O peroxide bonds.",
      "Step 5: Oxidation state is a formal electron-bookkeeping assignment, not a measured charge sitting on the chromium atom."
    ],
    "ans": "+6 (Option A)",
    "trap": "Do not apply O = -2 blindly. First scan the structure for O–O peroxide or superoxide units; the structural exception changes the bookkeeping.",
    "distractorTraps": {
      "B": "Fell into the algebraic trap assuming all five oxygens are oxide ions (O²⁻).",
      "C": "Confused with valence d-electron count.",
      "D": "Confused with chromyl chloride or lower oxide."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {
      "compound": "CrO5"
    },
    "simSummary": [
      "CrO₅ Butterfly Structure",
      "1 Oxo Oxygen (=O) at -2",
      "4 Peroxo Oxygens (-O-O-) at -1",
      "Net Cr Oxidation State = +6"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.compound"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds compound only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: +6 + (-2) + 4(-1) = 0, so the assigned oxidation states reproduce the neutral formula exactly.",
    "takeaway": "Transfer rule: before oxidation-number algebra, scan for structural exceptions such as O–O peroxide bonds, superoxides, hydrides and elemental bonds.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q02",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 29th January Morning Shift",
    "subtab": 4,
    "subtabName": "The n-Factor Matrix",
    "year": "2025",
    "q": "The n-factor (valency factor) of potassium permanganate (KMnO₄) when it acts as an oxidizing agent in acidic, neutral/weakly alkaline, and strongly basic mediums respectively is:",
    "options": [
      {
        "key": "A",
        "text": "5, 3, 1"
      },
      {
        "key": "B",
        "text": "5, 1, 3"
      },
      {
        "key": "C",
        "text": "3, 5, 1"
      },
      {
        "key": "D",
        "text": "1, 3, 5"
      }
    ],
    "correct": "A",
    "formula": "n-factor = |Δ(Oxidation State)|. Acidic: Mn⁷⁺ → Mn²⁺ (Δ=5). Neutral: Mn⁷⁺ → MnO₂ (Mn⁴⁺, Δ=3). Basic: Mn⁷⁺ → MnO₄²⁻ (Mn⁶⁺, Δ=1)",
    "steps": [
      "Step 1: Initial oxidation state of Mn in KMnO₄: +1 + x + 4(-2) = 0 ⇒ x = +7.",
      "Step 2: In acidic medium: MnO₄⁻ + 8H⁺ + 5e⁻ → Mn²⁺ + 4H₂O. Change in O.S. = 7 - 2 = 5. Therefore, n = 5.",
      "Step 3: In neutral or weakly alkaline medium: MnO₄⁻ + 2H₂O + 3e⁻ → MnO₂ + 4OH⁻. Final O.S. of Mn in MnO₂ is +4. Change in O.S. = 7 - 4 = 3. Therefore, n = 3.",
      "Step 4: In strongly basic medium: MnO₄⁻ + e⁻ → MnO₄²⁻ (manganate ion). Final O.S. of Mn is +6. Change in O.S. = 7 - 6 = 1. Therefore, n = 1.",
      "Step 5: Sequence: 5, 3, 1 (Remember mnemonic: BAN = 1, 3, 5 for Basic, Alkaline/neutral, aNacidic)."
    ],
    "ans": "5, 3, 1 (Option A)",
    "trap": "Students frequently swap neutral (n = 3) and strongly basic (n = 1). In strongly basic medium, it reduces only to manganate (Mn⁶⁺, green)!",
    "distractorTraps": {
      "B": "Inverted neutral and strongly basic mediums.",
      "C": "Put neutral first before acidic.",
      "D": "Completely reversed order."
    },
    "targetTab": "tab-nfactor",
    "simParams": {
      "medium": "acidic"
    },
    "simSummary": [
      "KMnO₄: Mn⁷⁺ Initial",
      "Acidic: Mn²⁺ (n = 5)",
      "Neutral: MnO₂ (n = 3)",
      "Strongly Basic: MnO₄²⁻ (n = 1)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.medium"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds medium only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: the three reduction half-reactions consume 5 e⁻, 3 e⁻ and 1 e⁻ per MnO₄⁻ in acidic, neutral/weakly alkaline and strongly basic conditions respectively.",
    "takeaway": "Transfer rule: n-factor comes from the actual redox product. Identify the medium and product first, then count the oxidation-state change.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q03",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 31st January Morning Shift",
    "subtab": 4,
    "subtabName": "The n-Factor Matrix",
    "year": "2024",
    "q": "In the disproportionation reaction of white phosphorus in basic solution: P₄ + 3OH⁻ + 3H₂O → PH₃ + 3H₂PO₂⁻, the equivalent weight of P₄ (Molar mass M) is:",
    "options": [
      {
        "key": "A",
        "text": "M / 3"
      },
      {
        "key": "B",
        "text": "M / 4"
      },
      {
        "key": "C",
        "text": "M / 12"
      },
      {
        "key": "D",
        "text": "3 M / 4"
      }
    ],
    "correct": "A",
    "formula": "For this balanced disproportionation, n-factor(P₄) = electrons transferred per mole of P₄ = 3.",
    "steps": [
      "Step 1: In P₄, phosphorus is 0. In PH₃ it is -3, while in H₂PO₂⁻ it is +1.",
      "Step 2: The balanced reaction sends one of the four P atoms to -3 and the other three P atoms to +1.",
      "Step 3: The reduced P atom gains 3 e⁻. The three oxidized P atoms each lose 1 e⁻, for 3 e⁻ lost in total.",
      "Step 4: Electron loss and gain therefore match at 3 e⁻ per mole of P₄.",
      "Step 5: n-factor(P₄) = 3, so equivalent weight = M/3."
    ],
    "ans": "M / 3 (Option A)",
    "trap": "Do not count a hypothetical change for all four P atoms in the same direction. Disproportionation splits identical starting atoms between oxidation and reduction products.",
    "distractorTraps": {
      "B": "Divided by 4 (number of atoms in P₄).",
      "C": "Used total electrons (12) without dividing by stoichiometric moles.",
      "D": "Inverted the n-factor."
    },
    "targetTab": "tab-nfactor",
    "simParams": {},
    "simSummary": [
      "White Phosphorus Disproportionation",
      "1 atom P reduced (0 → -3, 3 e⁻)",
      "3 atoms P oxidized (0 → +1, 3 e⁻)",
      "n-factor = 3 ⇒ E = M/3"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: electrons lost = 3 × 1 = 3 and electrons gained = 1 × 3 = 3; the electron ledger closes.",
    "takeaway": "Transfer rule: for disproportionation, use the balanced product split and count the matched electron transfer per mole of the reacting substance.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q04",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 28th January Evening Shift",
    "subtab": 1,
    "subtabName": "Structural Oxidation States",
    "year": "2025",
    "q": "In the tetrathionate ion (S₄O₆²⁻), the oxidation states of the four sulfur atoms are respectively:",
    "options": [
      {
        "key": "A",
        "text": "+5, 0, 0, +5"
      },
      {
        "key": "B",
        "text": "+2.5, +2.5, +2.5, +2.5"
      },
      {
        "key": "C",
        "text": "+6, 0, 0, +6"
      },
      {
        "key": "D",
        "text": "+4, +1, +1, +4"
      }
    ],
    "correct": "A",
    "formula": "S₄O₆²⁻ structure: [O₃S - S - S - SO₃]²⁻. Homonuclear S-S bonds have Δ(O.S.) = 0",
    "steps": [
      "Step 1: Formula algebra gives an average sulfur oxidation number of +2.5 because 4x + 6(-2) = -2.",
      "Step 2: That +2.5 is a formula-average description; the structure lets us make atom-by-atom formal assignments.",
      "Step 3: In the S–S–S–S skeleton, homonuclear S–S bonds contribute zero to oxidation-state assignment, so the two central sulfur atoms are assigned 0.",
      "Step 4: Let each equivalent terminal sulfur be x. Using the whole ion: 2x + 0 + 0 + 6(-2) = -2, giving x = +5.",
      "Step 5: The atom-by-atom formal assignments are therefore +5, 0, 0, +5.",
      "Step 6: Check: (+5) + 0 + 0 + (+5) + 6(-2) = -2, matching the ion charge."
    ],
    "ans": "+5, 0, 0, +5 (Option A)",
    "trap": "Do not confuse the formula-average value (+2.5) with the atom-by-atom structural assignment requested in the question.",
    "distractorTraps": {
      "B": "Picked the algebraic average (+2.5) instead of structural localized states.",
      "C": "Assumed terminal sulfur was +6 like in sulfate.",
      "D": "Distributed charge evenly across adjacent pairs."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {
      "compound": "S4O6"
    },
    "simSummary": [
      "Tetrathionate S₄O₆²⁻",
      "Two Terminal S: +5 each",
      "Two Central S: 0 each",
      "Average = (5 + 0 + 0 + 5)/4 = +2.5"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.compound"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds compound only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: +5 + 0 + 0 + +5 - 12 = -2, exactly reproducing the tetrathionate charge.",
    "takeaway": "Transfer rule: when equivalent-looking algebra gives an average value, inspect connectivity; homonuclear bonds contribute zero and can reveal distinct formal oxidation states.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q05",
    "num": "JEE Main 2026",
    "source": "JEE Main 2026 (Online) 7th April Morning Shift",
    "subtab": 5,
    "subtabName": "Redox Titrations & Burette Equivalence",
    "year": "2026",
    "q": "How many moles of acidified K₂Cr₂O₇ are required to completely oxidize 1 mole of ferrous oxalate (FeC₂O₄)?",
    "options": [
      {
        "key": "A",
        "text": "0.50 mol"
      },
      {
        "key": "B",
        "text": "0.33 mol"
      },
      {
        "key": "C",
        "text": "0.60 mol"
      },
      {
        "key": "D",
        "text": "1.00 mol"
      }
    ],
    "correct": "A",
    "formula": "Equivalents of K₂Cr₂O₇ = Equivalents of FeC₂O₄. n₁ × (n-factor₁) = n₂ × (n-factor₂)",
    "steps": [
      "Step 1: Calculate the n-factor of K₂Cr₂O₇ in acidic medium: Cr₂O₇²⁻ + 14H⁺ + 6e⁻ → 2Cr³⁺ + 7H₂O. 2 Cr atoms go from +6 to +3 ⇒ n-factor = 2 × 3 = 6.",
      "Step 2: Calculate the n-factor of ferrous oxalate (FeC₂O₄):",
      "        Both the cation AND the anion get oxidized!",
      "        Fe²⁺ → Fe³⁺ + e⁻  (1 electron lost by iron)",
      "        C₂O₄²⁻ → 2CO₂ + 2e⁻ (2 electrons lost by oxalate carbon: 2 × (+4 - +3) = 2)",
      "        Total electrons lost per mole of FeC₂O₄ = 1 + 2 = 3. Therefore, n-factor of FeC₂O₄ = 3!",
      "Step 3: Apply Law of Chemical Equivalence: Equivalents of K₂Cr₂O₇ = Equivalents of FeC₂O₄.",
      "        moles(K₂Cr₂O₇) × 6 = moles(FeC₂O₄) × 3.",
      "Step 4: For 1 mole of FeC₂O₄: moles(K₂Cr₂O₇) × 6 = 1 × 3 ⇒ moles(K₂Cr₂O₇) = 3 / 6 = 0.50 mol."
    ],
    "ans": "0.50 mol (Option A)",
    "trap": "The colossal trap: forgetting that BOTH Fe²⁺ and C₂O₄²⁻ oxidize! FeC₂O₄ has n-factor = 1 + 2 = 3, not 1 or 2.",
    "distractorTraps": {
      "B": "Only oxidized oxalate (n = 2 ⇒ 2/6 = 0.33 mol).",
      "C": "Used wrong Cr oxidation change.",
      "D": "Assumed 1:1 molar equivalence."
    },
    "targetTab": "tab-titration",
    "simParams": {},
    "simSummary": [
      "K₂Cr₂O₇ n-factor = 6",
      "FeC₂O₄ n-factor = 1 (Fe) + 2 (Oxalate) = 3",
      "Molar Ratio = 3/6 = 0.50 mol"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: one dichromate accepts 6 e⁻, while one FeC₂O₄ loses 3 e⁻; therefore 0.5 mol dichromate accepts the electrons from 1 mol FeC₂O₄.",
    "takeaway": "Transfer rule: when several parts of one formula unit are oxidized, add all electron losses before matching them to the oxidant.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q06",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 29th January Evening Shift",
    "subtab": 1,
    "subtabName": "Structural Oxidation States",
    "year": "2024",
    "q": "In magnetic iron oxide (Fe₃O₄, magnetite), the oxidation state of iron is best described as:",
    "options": [
      {
        "key": "A",
        "text": "A mixture of Fe(II) and Fe(III) in 1 : 2 ratio"
      },
      {
        "key": "B",
        "text": "+8/3 on each iron atom"
      },
      {
        "key": "C",
        "text": "All Fe(II)"
      },
      {
        "key": "D",
        "text": "All Fe(III)"
      }
    ],
    "correct": "A",
    "formula": "Fe₃O₄ is a stoichiometric mixed oxide: FeO · Fe₂O₃",
    "steps": [
      "Step 1: Formula algebra gives the average value 3x + 4(-2) = 0, so x = +8/3.",
      "Step 2: Magnetite is conventionally described as a mixed-valence oxide containing Fe(II) and Fe(III) in a 1:2 stoichiometric ratio.",
      "Step 3: A useful formal decomposition is FeO·Fe₂O₃, corresponding to one Fe(II) and two Fe(III) per Fe₃O₄ formula unit.",
      "Step 4: Average check: [2 + 3 + 3]/3 = 8/3.",
      "Step 5: These oxidation states are formal bookkeeping labels; they should not be described as literal localized atomic charges."
    ],
    "ans": "A mixture of Fe(II) and Fe(III) in 1 : 2 ratio (Option A)",
    "trap": "The question asks for the mixed-valence description, not merely the formula-average +8/3. Do not equate either oxidation-state notation with measured atomic charge.",
    "distractorTraps": {
      "B": "Picked the statistical average without recognizing mixed oxide reality.",
      "C": "Assumed all divalent.",
      "D": "Assumed all trivalent."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {
      "compound": "Fe3O4"
    },
    "simSummary": [
      "Magnetite Fe₃O₄ = FeO &middot; Fe₂O₃",
      "1 &times; Fe²⁺ (+2)",
      "2 &times; Fe³⁺ (+3)",
      "Ratio Fe(II) : Fe(III) = 1 : 2"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.compound"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds compound only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: one +2 and two +3 assignments sum to +8, exactly balancing four O at -2.",
    "takeaway": "Transfer rule: distinguish a formula-average oxidation number from a structure-supported mixed-valence formal assignment.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q07",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 24th January Evening Shift",
    "subtab": 4,
    "subtabName": "n-Factor Matrix & Medium Dependency",
    "year": "2023",
    "q": "When potassium permanganate (KMnO₄, molar mass M) acts as an oxidizing agent in neutral or faintly alkaline medium (such as Baeyer's reagent), its oxidation state changes from +7 to +4 (MnO₂). The equivalent mass of KMnO₄ in this medium is:",
    "options": [
      {
        "key": "A",
        "text": "M / 3"
      },
      {
        "key": "B",
        "text": "M / 5"
      },
      {
        "key": "C",
        "text": "M / 1"
      },
      {
        "key": "D",
        "text": "M / 2"
      }
    ],
    "correct": "A",
    "formula": "Equivalent Mass = Molar Mass / n-factor. Half-reaction: MnO₄⁻ + 2H₂O + 3e⁻ → MnO₂ + 4OH⁻ ⇒ n = 3",
    "steps": [
      "Step 1: Write the reduction half-reaction in neutral or faintly alkaline aqueous medium: MnO₄⁻ + 2H₂O + 3e⁻ → MnO₂(s) + 4OH⁻.",
      "Step 2: Determine oxidation states: Manganese changes from +7 in KMnO₄ to +4 in MnO₂.",
      "Step 3: Total electrons gained per mole of KMnO₄ is |+7 - +4| = 3. Therefore, n-factor = 3.",
      "Step 4: Compute equivalent mass: Equivalent mass = Molar mass (M) / n-factor = M / 3.",
      "Step 5: Contrast across media: Acidic medium gives Mn²⁺ (n=5 ⇒ M/5); strongly basic gives MnO₄²⁻ (n=1 ⇒ M/1); neutral gives MnO₂ (n=3 ⇒ M/3)."
    ],
    "ans": "M / 3 (Option A)",
    "trap": "In acidic medium, n-factor = 5 (M/5). In strongly basic medium, n-factor = 1 (M/1). In neutral/faintly alkaline medium, n-factor = 3 (M/3)!",
    "distractorTraps": {
      "B": "Used acidic medium n-factor = 5.",
      "C": "Used strongly basic medium n-factor = 1.",
      "D": "Arbitrary factor 2."
    },
    "targetTab": "tab-nfactor",
    "simParams": {
      "medium": "neutral"
    },
    "simSummary": [
      "Neutral / Weak Alkaline Medium",
      "MnO₄⁻ (+7) → MnO₂ (+4)",
      "n-factor = 3",
      "Equivalent Mass = M / 3"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.medium"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds medium only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: MnO₄⁻ + 2H₂O + 3e⁻ → MnO₂ + 4OH⁻ balances atoms and charge, confirming n = 3.",
    "takeaway": "Transfer rule: equivalent mass depends on the reaction product; write or identify the relevant half-reaction before using M/n.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q08",
    "num": "JEE Main 2025",
    "source": "JEE Main 2025 (Online) 23rd January Morning Shift",
    "subtab": 5,
    "subtabName": "Redox Titrations & Galvanic Cells",
    "year": "2025",
    "q": "For the standard galvanic cell Zn(s) | Zn²⁺(aq, 1M) || Cu²⁺(aq, 1M) | Cu(s), given standard reduction potentials E°(Zn²⁺/Zn) = -0.76 V and E°(Cu²⁺/Cu) = +0.34 V, the standard Gibbs free energy change ΔG° for the cell reaction at 298 K is (Faraday constant F ≈ 96500 C/mol):",
    "options": [
      {
        "key": "A",
        "text": "-212.3 kJ/mol"
      },
      {
        "key": "B",
        "text": "+212.3 kJ/mol"
      },
      {
        "key": "C",
        "text": "-106.1 kJ/mol"
      },
      {
        "key": "D",
        "text": "-424.6 kJ/mol"
      }
    ],
    "correct": "A",
    "formula": "E°_cell = E°_cathode - E°_anode = 0.34 - (-0.76) = 1.10 V. ΔG° = -n F E°_cell (with n = 2)",
    "steps": [
      "Step 1: Calculate standard EMF: E°_cell = E°(Cu²⁺/Cu) - E°(Zn²⁺/Zn) = +0.34 V - (-0.76 V) = +1.10 V.",
      "Step 2: Identify moles of electrons transferred: Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s) ⇒ n = 2 mol of electrons.",
      "Step 3: Relate EMF to Gibbs energy: ΔG° = -n F E°_cell.",
      "Step 4: Calculate numerical value: ΔG° = -2 × 96500 C/mol × 1.10 J/C = -212300 J/mol = -212.3 kJ/mol.",
      "Step 5: Negative ΔG° confirms the spontaneity of the galvanic cell under standard conditions."
    ],
    "ans": "-212.3 kJ/mol (Option A)",
    "trap": "Always remember the negative sign in ΔG° = -nFE°! A spontaneous cell with E° > 0 must always have ΔG° < 0.",
    "distractorTraps": {
      "B": "Missed the minus sign in ΔG° = -nFE°.",
      "C": "Used n = 1 instead of n = 2.",
      "D": "Multiplied by 4 instead of 2."
    },
    "targetTab": "tab-galvanic",
    "simParams": {},
    "simSummary": [
      "E°_cell = 0.34 - (-0.76) = +1.10 V",
      "n = 2 moles electrons",
      "ΔG° = -2 × 96500 × 1.10 = -212.3 kJ/mol",
      "Spontaneous Cell"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: 2 × 96500 × 1.10 = 212300 J mol⁻¹, and E°cell > 0 requires ΔG° < 0 through ΔG° = -nFE°.",
    "takeaway": "Transfer rule: calculate E°cell from reduction potentials, determine the electron count n from the balanced cell reaction, then use ΔG° = -nFE° with units.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q09",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 1st February Morning Shift",
    "subtab": 1,
    "subtabName": "Structural Bond Cleavage Tool",
    "year": "2024",
    "q": "The oxidation states of sulfur in Caro's acid (H₂SO₅) and Marshall's acid (H₂S₂O₈) respectively are:",
    "options": [
      {
        "key": "A",
        "text": "+6 and +6"
      },
      {
        "key": "B",
        "text": "+8 and +7"
      },
      {
        "key": "C",
        "text": "+6 and +7"
      },
      {
        "key": "D",
        "text": "+4 and +6"
      }
    ],
    "correct": "A",
    "formula": "H₂SO₅ has 1 peroxo linkage (-O-O-, O.S. = -1 each); H₂S₂O₈ has 1 peroxo bridge linking two -SO₃H groups.",
    "steps": [
      "Step 1: Inspect each acid for an O–O peroxide linkage before assigning every oxygen as -2.",
      "Step 2: In H₂SO₅, three oxygens are assigned -2 and the two peroxide oxygens are -1: 2(+1) + x + 3(-2) + 2(-1) = 0, so S = +6.",
      "Step 3: In H₂S₂O₈, six oxygens are assigned -2 and the two peroxide oxygens are -1: 2(+1) + 2x + 6(-2) + 2(-1) = 0.",
      "Step 4: Solving gives 2x = 12, so each sulfur is +6.",
      "Step 5: The wrong +8 or +7 results come from applying O = -2 to the peroxide oxygens."
    ],
    "ans": "+6 and +6 (Option A)",
    "trap": "When an oxoacid contains an O–O peroxide bond, the two peroxide oxygens are assigned -1. The structural exception—not a valence-electron 'ceiling'—is what fixes the calculation.",
    "distractorTraps": {
      "B": "BLIND ALGEBRA TRAP: Calculated +8 for H₂SO₅ and +7 for H₂S₂O₈ assuming all oxygens are -2 oxide.",
      "C": "Calculated Caro's acid correctly (+6) but fell into algebraic trap for Marshall's acid (+7).",
      "D": "Confused with sulfurous acid derivatives."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {},
    "simSummary": [
      "H₂SO₅: S = +6 (1 peroxo -O-O-)",
      "H₂S₂O₈: S = +6 each (1 peroxo bridge)",
      "Octet ceiling = +6"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: H₂SO₅ gives +2 +6 -6 -2 = 0; H₂S₂O₈ gives +2 +12 -12 -2 = 0.",
    "takeaway": "Transfer rule: recognize peroxide connectivity first; only then apply the oxidation-number sum rule.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q10",
    "num": "JEE Main 2024",
    "source": "JEE Main 2024 (Online) 29th January Evening Shift",
    "subtab": 1,
    "subtabName": "Structural Bond Cleavage Tool",
    "year": "2024",
    "q": "In the brown ring complex [Fe(H₂O)₅(NO)]SO₄ formed during the nitrate ring test, the oxidation state of Iron and the magnetic moment (μ) are:",
    "options": [
      {
        "key": "A",
        "text": "+1 and 3.87 BM (3 unpaired electrons)"
      },
      {
        "key": "B",
        "text": "+2 and 4.90 BM (4 unpaired electrons)"
      },
      {
        "key": "C",
        "text": "+3 and 5.92 BM (5 unpaired electrons)"
      },
      {
        "key": "D",
        "text": "+1 and 1.73 BM (1 unpaired electron)"
      }
    ],
    "correct": "A",
    "formula": "JEE/formal model: treating coordinated NO as NO⁺ gives Fe(I); the {FeNO}⁷ unit has quartet spin S = 3/2, giving μspin-only = √15 ≈ 3.87 BM.",
    "steps": [
      "Step 1: The complex cation [Fe(H₂O)₅(NO)]²⁺ has overall charge +2; water is neutral.",
      "Step 2: In the conventional exam bookkeeping model, coordinated NO is treated as NO⁺. Charge balance then gives x + (+1) = +2, so Fe is assigned +1.",
      "Step 3: The observed/formal {FeNO}⁷ unit is a quartet (S = 3/2), corresponding to three unpaired electrons in the simple spin-only count.",
      "Step 4: μ = √[n(n+2)] = √[3×5] = √15 ≈ 3.87 BM.",
      "Step 5: Advanced caveat: metal nitrosyls are non-innocent. Modern bonding descriptions often use Enemark–Feltham {FeNO}⁷ notation rather than claiming a unique localized Fe(I)/NO⁺ electron distribution."
    ],
    "ans": "+1 and 3.87 BM (3 unpaired electrons) (Option A)",
    "trap": "Do not claim that the magnetic moment uniquely proves a literal Fe(I)–NO⁺ charge distribution. The +1 answer is the conventional exam formalism; the Fe–NO unit is electronically non-innocent.",
    "distractorTraps": {
      "B": "Treated NO as neutral ligand, concluding Fe = +2 with 4 unpaired electrons (μ = 4.90 BM).",
      "C": "Assumed Fe³⁺ high-spin state with 5 unpaired electrons.",
      "D": "Assumed low-spin pairing leaving only 1 unpaired electron."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {},
    "simSummary": [
      "[Fe(H₂O)₅(NO⁺)]²⁺: Fe is +1",
      "3d⁷ high spin ⇒ n = 3 unpaired e⁻",
      "μ = √15 ≈ 3.87 BM"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed on 2026-09-20 under the conventional JEE Fe(I)/NO⁺ formalism; modern Fe–NO bonding is non-innocent, so the local oxidation-state description is model-dependent. Source-item provenance/key remains unverified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check under the stated JEE convention: Fe(+1) + NO(+1) gives the +2 complex charge, while n = 3 unpaired electrons gives √15 ≈ 3.87 BM.",
    "takeaway": "Transfer rule: with redox-active or non-innocent ligands, state the formal electron-counting convention explicitly and separate it from a literal charge picture.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q11",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 13th April Morning Shift",
    "subtab": 4,
    "subtabName": "The n-Factor Matrix & Disproportionation",
    "year": "2023",
    "q": "When ferrous oxalate (FeC₂O₄) is oxidized completely by acidic KMnO₄ to Fe³⁺ and CO₂, the n-factor of FeC₂O₄ is:",
    "options": [
      {
        "key": "A",
        "text": "3"
      },
      {
        "key": "B",
        "text": "2"
      },
      {
        "key": "C",
        "text": "1"
      },
      {
        "key": "D",
        "text": "5"
      }
    ],
    "correct": "A",
    "formula": "n-factor = ∑ (Moles of e⁻ lost by each oxidized atom per mole of salt) = n(Fe²⁺ → Fe³⁺) + n(C₂O₄²⁻ → 2 CO₂)",
    "steps": [
      "Step 1: In FeC₂O₄, BOTH the cation (Fe²⁺) and the anion (C₂O₄²⁻) undergo oxidation!",
      "Step 2: Oxidation of iron: Fe²⁺ → Fe³⁺ + 1 e⁻ (Change in O.S. = 3 - 2 = 1, e⁻ lost = 1).",
      "Step 3: Oxidation of oxalate: C₂O₄²⁻ → 2 CO₂ + 2 e⁻ (Carbon goes from +3 to +4, 2 atoms × 1 = 2 e⁻ lost).",
      "Step 4: Total electrons lost per formula unit of FeC₂O₄ = 1 + 2 = 3 electrons.",
      "Step 5: Therefore, n-factor of FeC₂O₄ = 3. (1 mole of FeC₂O₄ reacts with 3/5 mole of KMnO₄ in acid)."
    ],
    "ans": "3 (Option A)",
    "trap": "DUAL OXIDATION TRAP: Students count only the oxalate ion (n=2) or only the iron ion (n=1); because BOTH are oxidized, their n-factors ADD together (1 + 2 = 3)!",
    "distractorTraps": {
      "B": "Counted only oxalate oxidation: C₂O₄²⁻ → 2 CO₂ (n = 2).",
      "C": "Counted only iron oxidation: Fe²⁺ → Fe³⁺ (n = 1).",
      "D": "Reported the n-factor of KMnO₄ in acid (n = 5)."
    },
    "targetTab": "tab-nfactor",
    "simParams": {
      "medium": "acidic"
    },
    "simSummary": [
      "Fe²⁺ → Fe³⁺ (1 e⁻)",
      "C₂O₄²⁻ → 2 CO₂ (2 e⁻)",
      "Total n-factor = 1 + 2 = 3"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.medium"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds medium only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: Fe²⁺ loses 1 e⁻ and C₂O₄²⁻ loses 2 e⁻, so the formula unit loses 3 e⁻ in total.",
    "takeaway": "Transfer rule: compute n-factor from the complete reaction of the whole formula unit; add electron changes from every redox-active component.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q12",
    "num": "JEE Main 2023",
    "source": "JEE Main 2023 (Online) 25th January Morning Shift",
    "subtab": 1,
    "subtabName": "Structural Bond Cleavage Tool",
    "year": "2023",
    "q": "Bleaching powder (CaOCl₂) contains two chlorine atoms. Their individual oxidation states are:",
    "options": [
      {
        "key": "A",
        "text": "-1 and +1"
      },
      {
        "key": "B",
        "text": "0 and 0"
      },
      {
        "key": "C",
        "text": "-1 and -1"
      },
      {
        "key": "D",
        "text": "+1 and +1"
      }
    ],
    "correct": "A",
    "formula": "Textbook/JEE idealization: bleaching powder is represented as Ca(OCl)Cl, containing Cl⁻ and OCl⁻; the two chlorine oxidation states are -1 and +1.",
    "steps": [
      "Step 1: Use the textbook/JEE representation Ca(OCl)Cl for bleaching powder; real commercial bleaching powder can have more complex composition.",
      "Step 2: The chloride component is Cl⁻, so that chlorine is -1.",
      "Step 3: In hypochlorite OCl⁻, oxygen is -2 and x + (-2) = -1, giving chlorine +1.",
      "Step 4: Therefore the two formal chlorine oxidation states in the model are -1 and +1.",
      "Step 5: Their arithmetic average is 0, but the question asks for the distinct species represented in the structural model."
    ],
    "ans": "-1 and +1 (Option A)",
    "trap": "Do not report only the average value 0 when the textbook model explicitly contains chloride and hypochlorite chlorine in different environments.",
    "distractorTraps": {
      "B": "Reported average oxidation state (0) for both atoms.",
      "C": "Assumed both chlorines are simple chloride ions (-1).",
      "D": "Assumed both chlorines are hypochlorite (+1)."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {},
    "simSummary": [
      "Bleaching powder: Ca(OCl)Cl",
      "Chloride Cl⁻ ⇒ O.S. = -1",
      "Hypochlorite OCl⁻ ⇒ O.S. = +1"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: Ca²⁺ + Cl⁻ + OCl⁻ is charge-neutral, and the OCl⁻ assignment (+1) + (-2) = -1.",
    "takeaway": "Transfer rule: for mixed salts, split the formula into its constituent ions before assigning oxidation states.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q13",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 27th July Evening Shift",
    "subtab": 4,
    "subtabName": "The n-Factor Matrix & Disproportionation",
    "year": "2022",
    "q": "The equivalent weight of potassium permanganate (KMnO₄, molecular mass M) in acidic, neutral/faintly alkaline, and strongly basic media respectively is:",
    "options": [
      {
        "key": "A",
        "text": "M/5,  M/3,  M/1"
      },
      {
        "key": "B",
        "text": "M/5,  M/1,  M/3"
      },
      {
        "key": "C",
        "text": "M/3,  M/5,  M/1"
      },
      {
        "key": "D",
        "text": "M/5,  M/5,  M/5"
      }
    ],
    "correct": "A",
    "formula": "Equivalent Weight = M / (n-factor). In Acid: Mn⁷⁺ → Mn²⁺ (n=5). In Neutral: Mn⁷⁺ → MnO₂ (n=3). In Strong Base: Mn⁷⁺ → MnO₄²⁻ (n=1).",
    "steps": [
      "Step 1: Acidic Medium: MnO₄⁻ + 8 H⁺ + 5 e⁻ → Mn²⁺ + 4 H₂O. Mn(+7 → +2), Δ(O.S.) = 5 ⇒ n = 5 ⇒ Eq Wt = M/5.",
      "Step 2: Neutral / Faintly Alkaline (Bayer's reagent): MnO₄⁻ + 2 H₂O + 3 e⁻ → MnO₂ + 4 OH⁻. Mn(+7 → +4), Δ(O.S.) = 3 ⇒ n = 3 ⇒ Eq Wt = M/3.",
      "Step 3: Strongly Basic Medium: MnO₄⁻ + e⁻ → MnO₄²⁻ (manganate ion). Mn(+7 → +6), Δ(O.S.) = 1 ⇒ n = 1 ⇒ Eq Wt = M/1.",
      "Step 4: Compiling equivalent weights: Acidic = M/5, Neutral = M/3, Strongly basic = M/1."
    ],
    "ans": "M/5,  M/3,  M/1 (Option A)",
    "trap": "Remember the mnemonic 'BAN 153': Basic n=1, Acidic n=5, Neutral n=3!",
    "distractorTraps": {
      "B": "Swapped neutral (n=3) and strongly basic (n=1) n-factors.",
      "C": "Swapped acidic and neutral media.",
      "D": "Assumed n-factor is invariant (always 5)."
    },
    "targetTab": "tab-nfactor",
    "simParams": {
      "medium": "acidic"
    },
    "simSummary": [
      "Acidic: n = 5 ⇒ M/5",
      "Neutral: n = 3 ⇒ M/3",
      "Strongly Basic: n = 1 ⇒ M/1"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.medium"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds medium only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: M/5, M/3 and M/1 follow directly from 5, 3 and 1 electrons accepted per permanganate in the three stated media.",
    "takeaway": "Transfer rule: equivalent weight is reaction-dependent; determine the reduction product and n-factor before using M/n.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q14",
    "num": "JEE Main 2022",
    "source": "JEE Main 2022 (Online) 26th June Evening Shift",
    "subtab": 4,
    "subtabName": "The n-Factor Matrix & Disproportionation",
    "year": "2022",
    "q": "In the disproportionation reaction of white phosphorus with alkali: P₄ + 3 OH⁻ + 3 H₂O → PH₃ + 3 H₂PO₂⁻, the n-factor of P₄ is:",
    "options": [
      {
        "key": "A",
        "text": "3"
      },
      {
        "key": "B",
        "text": "4"
      },
      {
        "key": "C",
        "text": "12"
      },
      {
        "key": "D",
        "text": "6"
      }
    ],
    "correct": "A",
    "formula": "For disproportionation: n-factor = Total moles of electrons transferred per mole of substance.",
    "steps": [
      "Step 1: Determine oxidation state changes from P₄ (O.S. = 0):",
      "        Reduction: P₄ → PH₃ (P is -3). Change per P atom = 3.",
      "        Oxidation: P₄ → H₂PO₂⁻ (P is +1). Change per P atom = 1.",
      "Step 2: In the balanced equation: 1 mole of P₄ produces 1 mole of PH₃ and 3 moles of H₂PO₂⁻.",
      "Step 3: Reduction half-reaction: 1 P atom gains 3 electrons ⇒ Total electrons gained = 3 e⁻.",
      "Step 4: Oxidation half-reaction: 3 P atoms each lose 1 electron ⇒ Total electrons lost = 3 e⁻.",
      "Step 5: The total number of electrons transferred per formula unit of P₄ is exactly 3.",
      "Step 6: Therefore, the n-factor of P₄ = 3 (Equivalent weight = M / 3)."
    ],
    "ans": "3 (Option A)",
    "trap": "Do not multiply 4 atoms × 3 = 12! Only 1 of the 4 phosphorus atoms is reduced (gaining 3 e⁻), while the other 3 are oxidized (each losing 1 e⁻, total 3 e⁻). The net exchange per P₄ is 3 electrons!",
    "distractorTraps": {
      "B": "Assumed all 4 atoms undergo oxidation or reduction.",
      "C": "Multiplied 4 × 3 = 12 without accounting for disproportionation fraction.",
      "D": "Added reduction (3) + oxidation (3) = 6 electrons (double counting transfer)."
    },
    "targetTab": "tab-nfactor",
    "simParams": {
      "medium": "neutral"
    },
    "simSummary": [
      "P₄ (0) → 1 PH₃ (-3) [gains 3 e⁻]",
      "P₄ (0) → 3 H₂PO₂⁻ (+1) [loses 3 e⁻]",
      "Net transfer = 3 e⁻ ⇒ n-factor = 3"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [
      "simParams.medium"
    ],
    "simFidelity": "CONSTRAINT_FAITHFUL",
    "simFidelityNote": "The simulator binds medium only. Remaining question details stay in the worked solution; this is not an exact full-state replay.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: 3 e⁻ are lost by three P atoms and 3 e⁻ are gained by the one reduced P atom, so n(P₄) = 3.",
    "takeaway": "Transfer rule: in disproportionation, count the matched electron transfer from the balanced split of atoms between the two products.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q15",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 24th February Evening Shift",
    "subtab": 3,
    "subtabName": "Ion-Electron Balancing Rig",
    "year": "2021",
    "q": "When iodide (I⁻) is oxidized by permanganate (MnO₄⁻) in faint alkaline medium, it forms iodate (IO₃⁻) and manganese dioxide (MnO₂). The stoichiometric ratio of MnO₄⁻ to I⁻ in the balanced equation is:",
    "options": [
      {
        "key": "A",
        "text": "2 : 1"
      },
      {
        "key": "B",
        "text": "1 : 2"
      },
      {
        "key": "C",
        "text": "5 : 1"
      },
      {
        "key": "D",
        "text": "2 : 5"
      }
    ],
    "correct": "A",
    "formula": "2 MnO₄⁻ + I⁻ + H₂O → 2 MnO₂ + IO₃⁻ + 2 OH⁻",
    "steps": [
      "Step 1: Reduction half-reaction in alkaline medium: MnO₄⁻ (+7) + 2 H₂O + 3 e⁻ → MnO₂ (+4) + 4 OH⁻ (gains 3 e⁻).",
      "Step 2: Oxidation half-reaction: I⁻ (-1) + 6 OH⁻ → IO₃⁻ (+5) + 3 H₂O + 6 e⁻ (loses 6 e⁻).",
      "Step 3: Equalize electron transfer: Multiply reduction half by 2 so it consumes 2 × 3 = 6 e⁻.",
      "Step 4: Balanced net ionic equation:",
      "        2 MnO₄⁻ + I⁻ + H₂O → 2 MnO₂ + IO₃⁻ + 2 OH⁻.",
      "Step 5: The stoichiometric ratio of MnO₄⁻ to I⁻ is 2 : 1."
    ],
    "ans": "2 : 1 (Option A)",
    "trap": "MEDIUM TRAP: In ACIDIC medium, I⁻ oxidizes to I₂ (ratio 2:10 = 1:5). But in FAINTLY ALKALINE medium, I⁻ oxidizes all the way to IO₃⁻ (ratio 2:1)!",
    "distractorTraps": {
      "B": "Inverted the ratio (I⁻ to MnO₄⁻).",
      "C": "Used acidic medium reduction of permanganate (n=5) without checking medium.",
      "D": "Acidic medium ratio for oxidation to I₂ (2 MnO₄⁻ : 10 I⁻)."
    },
    "targetTab": "tab-ion-electron",
    "simParams": {},
    "simSummary": [
      "Alkaline medium: I⁻ → IO₃⁻ (6 e⁻ lost)",
      "MnO₄⁻ → MnO₂ (3 e⁻ gained)",
      "Ratio = 2 MnO₄⁻ : 1 I⁻"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: 2MnO₄⁻ + I⁻ + H₂O → 2MnO₂ + IO₃⁻ + 2OH⁻ has equal atoms and net charge -3 on both sides.",
    "takeaway": "Transfer rule: the reaction medium can change the oxidation product; balance the actual half-reactions before reading the stoichiometric ratio.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q16",
    "num": "JEE Main 2021",
    "source": "JEE Main 2021 (Online) 25th July Morning Shift",
    "subtab": 6,
    "subtabName": "Galvanic Cell & Nernst Potential",
    "year": "2021",
    "q": "Given standard reduction potentials: E°(Zn²⁺/Zn) = -0.76 V and E°(Fe²⁺/Fe) = -0.44 V. The standard EMF of the galvanic cell Zn | Zn²⁺ || Fe²⁺ | Fe and the spontaneity of the forward reaction are:",
    "options": [
      {
        "key": "A",
        "text": "+0.32 V and Spontaneous"
      },
      {
        "key": "B",
        "text": "-0.32 V and Non-spontaneous"
      },
      {
        "key": "C",
        "text": "+1.20 V and Spontaneous"
      },
      {
        "key": "D",
        "text": "-1.20 V and Non-spontaneous"
      }
    ],
    "correct": "A",
    "formula": "E°_cell = E°_cathode - E°_anode. Reaction is spontaneous if E°_cell > 0 (ΔG° < 0).",
    "steps": [
      "Step 1: Identify cathode and anode from cell notation Zn | Zn²⁺ || Fe²⁺ | Fe:",
      "        Anode (oxidation, left): Zn → Zn²⁺ + 2e⁻.",
      "        Cathode (reduction, right): Fe²⁺ + 2e⁻ → Fe.",
      "Step 2: Calculate standard EMF: E°_cell = E°_cathode - E°_anode = E°(Fe²⁺/Fe) - E°(Zn²⁺/Zn).",
      "Step 3: Substitute values: E°_cell = (-0.44 V) - (-0.76 V) = -0.44 + 0.76 = +0.32 V.",
      "Step 4: Since E°_cell > 0, ΔG° = -nFE° < 0, meaning the cell reaction Zn + Fe²⁺ → Zn²⁺ + Fe is thermodynamically spontaneous."
    ],
    "ans": "+0.32 V and Spontaneous (Option A)",
    "trap": "SIGN TRAP: Always subtract the anode potential: E°_cathode - E°_anode = (-0.44) - (-0.76) = +0.32 V, not -1.20 V!",
    "distractorTraps": {
      "B": "Reversed cathode and anode, obtaining -0.32 V.",
      "C": "Subtracted with double negative error: -0.44 - 0.76.",
      "D": "Added negative potentials: -0.44 + (-0.76) = -1.20 V."
    },
    "targetTab": "tab-galvanic",
    "simParams": {},
    "simSummary": [
      "Cathode: Fe²⁺ (-0.44 V)",
      "Anode: Zn (-0.76 V)",
      "E°_cell = +0.32 V (Spontaneous)"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: (-0.44) - (-0.76) = +0.32 V; a positive standard cell potential gives negative ΔG° for the written forward reaction.",
    "takeaway": "Transfer rule: with tabulated reduction potentials, identify cathode and anode first, then use E°cell = E°cathode - E°anode.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q17",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 6th September Evening Shift",
    "subtab": 1,
    "subtabName": "Structural Bond Cleavage Tool",
    "year": "2020",
    "q": "The individual oxidation states of the two nitrogen atoms in ammonium nitrate (NH₄NO₃) are:",
    "options": [
      {
        "key": "A",
        "text": "-3 and +5"
      },
      {
        "key": "B",
        "text": "+1 and +1"
      },
      {
        "key": "C",
        "text": "-3 and +3"
      },
      {
        "key": "D",
        "text": "0 and +2"
      }
    ],
    "correct": "A",
    "formula": "NH₄NO₃ ionizes into NH₄⁺ and NO₃⁻. In NH₄⁺: x + 4(+1) = +1 ⇒ x = -3. In NO₃⁻: y + 3(-2) = -1 ⇒ y = +5.",
    "steps": [
      "Step 1: Treat NH₄NO₃ as the ionic compound NH₄⁺ + NO₃⁻.",
      "Step 2: In NH₄⁺: x + 4(+1) = +1, so N = -3.",
      "Step 3: In NO₃⁻: y + 3(-2) = -1, so N = +5.",
      "Step 4: Applying one average value to the empirical formula would give +1, but that average hides the two chemically distinct nitrogen environments.",
      "Step 5: Oxidation states are formal bookkeeping assignments, not literal measured charges on the nitrogen atoms."
    ],
    "ans": "-3 and +5 (Option A)",
    "trap": "Do not average across chemically distinct polyatomic ions when the question asks for the individual formal oxidation states.",
    "distractorTraps": {
      "B": "Reported the blind algebraic average (+1) for both nitrogen atoms.",
      "C": "Confused nitrate NO₃⁻ with nitrite NO₂⁻ (+3).",
      "D": "Calculated oxidation states incorrectly."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {},
    "simSummary": [
      "NH₄⁺: N is -3 (sp³ tetrahedral)",
      "NO₃⁻: N is +5 (sp² planar)",
      "Average = +1, Real = -3 and +5"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: (-3) + 4(+1) = +1 for NH₄⁺ and (+5) + 3(-2) = -1 for NO₃⁻.",
    "takeaway": "Transfer rule: split ionic compounds into their actual ions before doing oxidation-state arithmetic.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q18",
    "num": "JEE Main 2020",
    "source": "JEE Main 2020 (Online) 3rd September Morning Shift",
    "subtab": 5,
    "subtabName": "Redox Titration Bench",
    "year": "2020",
    "q": "The volume of 0.1 M Na₂S₂O₃ (hypo) required to titrate the iodine liberated by adding excess KI to 25.0 mL of 0.02 M K₂Cr₂O₇ in acidic solution is:",
    "options": [
      {
        "key": "A",
        "text": "30.0 mL"
      },
      {
        "key": "B",
        "text": "15.0 mL"
      },
      {
        "key": "C",
        "text": "10.0 mL"
      },
      {
        "key": "D",
        "text": "5.0 mL"
      }
    ],
    "correct": "A",
    "formula": "Cr₂O₇²⁻ accepts 6 e⁻ in acid; 2S₂O₃²⁻ → S₄O₆²⁻ + 2e⁻, so each thiosulfate transfers 1 e⁻.",
    "steps": [
      "Step 1: In acid, one dichromate ion accepts 6 e⁻, so 0.02 M K₂Cr₂O₇ corresponds to 0.12 equivalents per litre.",
      "Step 2: 25.0 mL contains 0.12 × 25.0 = 3.0 milliequivalents of oxidizing capacity.",
      "Step 3: Iodine carries the same electron-equivalent amount into the thiosulfate titration.",
      "Step 4: The titration half-reaction is 2S₂O₃²⁻ → S₄O₆²⁻ + 2e⁻, so thiosulfate has n-factor 1 in this reaction and 0.1 M = 0.1 N.",
      "Step 5: 0.1 N × V = 3.0 meq, so V = 30.0 mL."
    ],
    "ans": "30.0 mL (Option A)",
    "trap": "Track electron equivalents through both redox stages. Do not infer the thiosulfate n-factor from a misleading average sulfur oxidation number.",
    "distractorTraps": {
      "B": "Used n-factor = 3 for dichromate (15.0 mL).",
      "C": "Equated molarities directly without n-factor (0.02 × 25 / 0.1 = 5 mL) or calculated 10 mL.",
      "D": "Calculated 5.0 mL using n = 1 for both."
    },
    "targetTab": "tab-titration",
    "simParams": {},
    "simSummary": [
      "K₂Cr₂O₇: n = 6 ⇒ 3.0 meq",
      "Hypo: n = 1 ⇒ N = 0.1 N",
      "V_hypo = 3.0 / 0.1 = 30.0 mL"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check by moles: 0.0005 mol dichromate accepts 0.003 mol e⁻; 0.030 L × 0.1 mol/L = 0.003 mol thiosulfate transfers the same electron amount.",
    "takeaway": "Transfer rule: in linked iodometric titrations, carry electron equivalents through each reaction rather than memorizing disconnected volume formulas.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q19",
    "num": "JEE Main 2019",
    "source": "JEE Main 2019 (Online) 10th January Evening Shift",
    "subtab": 6,
    "subtabName": "Galvanic Cell & Nernst Potential",
    "year": "2019",
    "q": "For the Daniell cell Zn(s) | Zn²⁺(aq) || Cu²⁺(aq) | Cu(s), if the concentration of Zn²⁺ is increased by a factor of 10 while keeping [Cu²⁺] constant at 298 K, the cell potential E_cell will:",
    "options": [
      {
        "key": "A",
        "text": "Decrease by 0.0295 V"
      },
      {
        "key": "B",
        "text": "Increase by 0.0295 V"
      },
      {
        "key": "C",
        "text": "Decrease by 0.0591 V"
      },
      {
        "key": "D",
        "text": "Increase by 0.0591 V"
      }
    ],
    "correct": "A",
    "formula": "E_cell = E° - (0.0591 / n) log([Zn²⁺] / [Cu²⁺]), with n = 2",
    "steps": [
      "Step 1: Write overall cell reaction: Zn(s) + Cu²⁺(aq) → Zn²⁺(aq) + Cu(s), where n = 2 electrons transferred.",
      "Step 2: Nernst equation at 298 K: E_cell = E°_cell - (0.0591 / 2) log Q = E°_cell - 0.02955 log([Zn²⁺] / [Cu²⁺]).",
      "Step 3: When [Zn²⁺] increases by 10 times: Δ(log Q) = log(10) = 1.",
      "Step 4: Change in EMF: ΔE = -0.02955 × 1 = -0.02955 V ≈ -0.0295 V.",
      "Step 5: Therefore, the cell potential decreases by 0.0295 V."
    ],
    "ans": "Decrease by 0.0295 V (Option A)",
    "trap": "Notice that Zn²⁺ is the OXIDIZED product on the right side of the reaction! Increasing product concentration shifts equilibrium backward (Le Chatelier) and reduces EMF by 0.0591 / n = 0.0295 V.",
    "distractorTraps": {
      "B": "Assumed increasing ion concentration increases cell potential.",
      "C": "Forgot n = 2 in the Nernst denominator, obtaining -0.0591 V.",
      "D": "Forgot n = 2 and inverted sign."
    },
    "targetTab": "tab-galvanic",
    "simParams": {},
    "simSummary": [
      "n = 2 electrons",
      "log([Zn²⁺]/[Cu²⁺]) increases by 1",
      "ΔE = -(0.0591/2) × 1 = -0.0295 V"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: multiplying [Zn²⁺] by 10 increases log Q by 1, so ΔE = -(0.0591/2) = -0.02955 V.",
    "takeaway": "Transfer rule: write the reaction quotient from the balanced cell reaction, then use its direction of change to predict the sign before calculating the Nernst shift.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  },
  {
    "id": "REDOX-Q20",
    "num": "JEE Main 2018",
    "source": "JEE Main 2018 (Offline) 8th April Shift",
    "subtab": 1,
    "subtabName": "Structural Bond Cleavage Tool",
    "year": "2018",
    "q": "Red lead (minium, Pb₃O₄) is a mixed oxide. The individual oxidation states of lead and their stoichiometric ratio are:",
    "options": [
      {
        "key": "A",
        "text": "Two Pb in +2 and one Pb in +4 (Ratio 2:1)"
      },
      {
        "key": "B",
        "text": "All three Pb in +8/3"
      },
      {
        "key": "C",
        "text": "One Pb in +2 and two Pb in +3 (Ratio 1:2)"
      },
      {
        "key": "D",
        "text": "Two Pb in +3 and one Pb in +2 (Ratio 2:1)"
      }
    ],
    "correct": "A",
    "formula": "Pb₃O₄ = 2 PbO · PbO₂. Reaction with HNO₃ yields 2 Pb(NO₃)₂ + PbO₂ + 2 H₂O.",
    "steps": [
      "Step 1: Formula algebra gives the average lead oxidation number +8/3 because 3x + 4(-2) = 0.",
      "Step 2: Red lead is conventionally represented as the mixed-valence oxide 2PbO·PbO₂.",
      "Step 3: That formal description contains two Pb(II) and one Pb(IV) per Pb₃O₄ formula unit.",
      "Step 4: Average check: [2 + 2 + 4]/3 = 8/3.",
      "Step 5: Dilute nitric acid dissolves the PbO component while PbO₂ remains, supporting the mixed-oxide chemical description."
    ],
    "ans": "Two Pb in +2 and one Pb in +4 (Ratio 2:1) (Option A)",
    "trap": "The +8/3 value is the formula-average oxidation number. For this mixed oxide, the requested formal description is two Pb(II) and one Pb(IV); do not describe oxidation state as literal atomic charge.",
    "distractorTraps": {
      "B": "Reported fractional mathematical average +8/3.",
      "C": "Pb does not exhibit stable +3 oxidation state due to inert pair effect.",
      "D": "Incorrect stoichiometric ratio."
    },
    "targetTab": "tab-structural-ox",
    "simParams": {},
    "simSummary": [
      "Pb₃O₄ = 2 PbO · PbO₂",
      "Two Pb(+2) : One Pb(+4)",
      "PbO dissolves in HNO₃, PbO₂ remains insoluble"
    ],
    "sourceAudit": "SOURCE_PROVENANCE_PENDING",
    "answerAudit": "PASS",
    "answerAuditNote": "Locally reviewed/recomputed on 2026-09-20; source-item provenance/key has not been independently verified.",
    "simBindingRefs": [],
    "simFidelity": "CONCEPT_ONLY",
    "simFidelityNote": "The simulator opens the relevant mechanism only; no question-specific state is injected.",
    "sourceAuditNote": "Attributed source item/key has not yet been independently matched against the cited ExamSIDE record.",
    "teacherCheck": "Independent check: 2(+2) + (+4) + 4(-2) = 0, so the mixed-valence assignment exactly balances Pb₃O₄.",
    "takeaway": "Transfer rule: for known mixed-valence oxides, distinguish the formula-average value from the chemically useful integer formal assignments.",
    "helperTags": [
      "TEACHERS_CHALKBOARD",
      "TRAP_ALERT",
      "INDEPENDENT_CHECK",
      "TRANSFER_TAKEAWAY",
      "EXACTNESS_BADGE"
    ]
  }
];
