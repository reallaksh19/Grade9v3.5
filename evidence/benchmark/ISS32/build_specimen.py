#!/usr/bin/env python3
"""Build the Issue #32 Chemistry: Chemical Bonding and Hybridisation specimen.

This is evidence for the minimal-prompt authoring workflow (Agent B).
The ten owner questions stay verbatim and carry OWNER_SUPPLIED custody.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

REPO = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"
OUT.mkdir(parents=True, exist_ok=True)

# Update qrt-review.json and question-ledger.json with calibrated band mappings
qrt_path = HERE / "qrt-review.json"
QRT = json.loads(qrt_path.read_text(encoding="utf-8"))

BAND_FOR_SCORE = {
    2: "D1",
    3: "D2",
    4: "D2",
    5: "D2",
    6: "D3"
}

for it in QRT["items"]:
    score = it["difficulty"]["score"]
    it["difficulty"]["band"] = BAND_FOR_SCORE[score]
    it["template_id"] = f"QRT-{it['demand']['primary']}-{it['difficulty']['band']}"

qrt_path.write_text(json.dumps(QRT, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Also sync question-ledger.json
ledger_path = HERE / "question-ledger.json"
ledger = json.loads(ledger_path.read_text(encoding="utf-8"))
for it in ledger["items"]:
    score = it["difficulty"]["score"]
    it["difficulty"]["band"] = BAND_FOR_SCORE[score]
    it["qrt_template"] = f"QRT-{it['demand']['primary']}-{it['difficulty']['band']}"
    it["difficulty"]["basis"] = f"{it['crux']['X']} Decisive learner move: {it['crux']['Z']}. Evaluated difficulty score {score} resolves to band {BAND_FOR_SCORE[score]}."
ledger_path.write_text(json.dumps(ledger, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

# Load verbatim stems from owner-core-prompt.md
core_text = (HERE / "owner-core-prompt.md").read_text(encoding="utf-8")
lines = core_text.split("\n")

STEMS: dict[str, str] = {}
curr_q = None
curr_lines = []
for line in lines:
    if line.startswith("### Q"):
        if curr_q:
            STEMS[curr_q] = "\n\n".join([p for p in "\n".join(curr_lines).split("\n\n") if p.strip()]).strip()
        curr_q = line.strip().split()[1]
        curr_lines = []
    elif line.startswith("## B —") or line.startswith("## B ΓÇö"):
        if curr_q:
            STEMS[curr_q] = "\n\n".join([p for p in "\n".join(curr_lines).split("\n\n") if p.strip()]).strip()
            curr_q = None
    elif curr_q:
        curr_lines.append(line)

print("Parsed stems count:", len(STEMS))

SRC = "SRC-OWNER-ISSUE32-HYBRID"
BUCKET = "BUCKET-CHE-11-BONDING"

CAP_DOM = "CAP-CHE-BOND-DOMAIN-COUNTING"
CAP_HYB = "CAP-CHE-BOND-HYBRID-ORBITAL-MAPPING"
CAP_3D  = "CAP-CHE-BOND-3D-REPRESENTATION-MODELS"

MIC_DOM = "MIC-CHE-BOND-DOMAIN-COUNTING"
MIC_HYB = "MIC-CHE-BOND-HYBRID-ORBITAL-MAPPING"
MIC_3D  = "MIC-CHE-BOND-3D-REPRESENTATION-MODELS"

REP_TET = "REP-CHE-TETRAHEDRAL-3D"
REP_SIG = "REP-CHE-SIGMA-PI-OVERLAP"
REP_DOM = "REP-CHE-DOMAINS-HCHO"

REL_STR = "REL-CHE-STERIC-NUMBER"
REL_CON = "REL-CHE-HYBRID-ORBITAL-CONSERVATION"
REL_SYM = "REL-CHE-ORBITAL-OVERLAP-SYMMETRY"

FAM_DOM = "FAM-CHE-BOND-STERIC-DOMAINS"
FAM_HYB = "FAM-CHE-BOND-HYBRID-GEOMETRY"

BANK_IDS = {f"Q{i}": f"OWN-ISSUE32-HYBRID-{i:02d}" for i in range(1, 11)}
PRIMARY_CAP = {
    "Q1": CAP_HYB, "Q2": CAP_DOM, "Q3": CAP_HYB, "Q4": CAP_3D, "Q5": CAP_3D,
    "Q6": CAP_HYB, "Q7": CAP_3D, "Q8": CAP_DOM, "Q9": CAP_DOM, "Q10": CAP_HYB,
}
PRIMARY_MIC = {
    "Q1": MIC_HYB, "Q2": MIC_DOM, "Q3": MIC_HYB, "Q4": MIC_3D, "Q5": MIC_3D,
    "Q6": MIC_HYB, "Q7": MIC_3D, "Q8": MIC_DOM, "Q9": MIC_DOM, "Q10": MIC_HYB,
}
FAMILY = {f"Q{i}": (FAM_DOM if PRIMARY_CAP[f"Q{i}"] == CAP_DOM else FAM_HYB) for i in range(1, 11)}
FIGURE = {
    "Q1": REP_TET, "Q2": REP_DOM, "Q3": REP_TET, "Q4": REP_TET, "Q5": REP_TET,
    "Q6": REP_SIG, "Q7": REP_TET, "Q8": REP_DOM, "Q9": REP_DOM, "Q10": REP_TET
}

def base(record_id: str, source: bool = True) -> dict:
    return {
        "id": record_id,
        "version": "0.1.0",
        "status": "CANDIDATE",
        "source_refs": [SRC] if source else [],
        "evidence_refs": [],
        "extensions": {},
    }

def step(step_id: str, role: str, action: str, why: str, output: str) -> dict:
    return {"id": step_id, "role": role, "action": action, "why_valid": why, "inputs": [], "output": output}

def model_answer(summary: str, reasoning: list[str], check: str) -> dict:
    return {
        "kind": "MODEL_RESPONSE",
        "summary": summary,
        "reasoning": reasoning,
        "check": check,
        "acceptable_alternatives": [],
        "subpart_answers": [],
        "verification_status": "CHECKED_BY_AUTHOR",
    }

def misconception(wrong: str, diagnostic: str, repair: str) -> dict:
    return {"wrong_idea": wrong, "diagnostic_prompt": diagnostic, "repair": repair}

def representation(record_id: str, kind: str, purpose: str, asset: str, stages: list[tuple[str, str, str]], correspondence: list[dict]) -> dict:
    return {
        **base(record_id, source=False),
        "kind": kind,
        "purpose": purpose,
        "required_elements": [s[1] for s in stages],
        "relation_refs": [REL_STR, REL_CON],
        "read_order": [s[2] for s in stages],
        "instance_constraints": ["Pre-attempt stages must orient without disclosing the final target answer W."],
        "accessibility": ["The SVG has an accessible name, title and description.", "Text labels duplicate any line-style meaning."],
        "misleading_alternatives": ["Treating a flat 2D Lewis sketch as a physical 90-degree molecular shape."],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [{"id": sid, "label": label, "purpose": job, "visible_elements": [label]} for sid, label, job in stages],
        "extensions": {"grade9v3:stage_mode": "CUMULATIVE"},
    }

resource = {
    **base(SRC, source=False),
    "title": "Issue #32 owner-supplied Grade 11 Chemistry Bonding & Hybridisation benchmark questions",
    "origin": "AUTHORED",
    "locator": "https://github.com/reallaksh19/Grade9v3.5/issues/32",
    "edition": "Owner prompt captured 2026-10-04",
    "section": "CORE PROMPT — VERBATIM OWNER INPUT / THE 10 QUESTIONS",
    "last_checked": "2026-10-04",
    "access_status": "FULL_ITEM_INSPECTED",
    "rights_status": "Owner-supplied text; no exam, textbook, year or official-answer identity claimed.",
    "snapshot_ref": None,
    "snapshot_digest": None,
    "role": ["QUESTION_BANK", "AUTHOR_CREATED"],
    "supports_claims": [],
    "entry_capabilities": [],
    "depth": ["COMPETITION"],
    "selection_reason": "Exact custody surface for the ten questions used by the Issue #32 run.",
    "fallback": [],
}

bucket = {
    **base(BUCKET),
    "title": "Chemical Bonding and Hybridisation",
    "topic": "Chemical Bonding and Molecular Structure",
    "intrinsic_badge": "MEDIUM",
    "badge_reason": "The central difficulty is coordinating spatial 3D stereochemical representation with steric domain definitions and orbital conservation.",
    "depth_overlay": "FOUNDATION",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP_TET,
}

capabilities = [
    {**base(CAP_DOM), "action": "Inventory central-atom steric electron domains by grouping multiple bonds into single domains and including only central lone pairs", "success_criterion": "Count bonded atoms and central lone pairs accurately without counting terminal lone pairs or inflating double/triple bonds", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_HYB), "action": "Map steric electron domain counts to introductory hybrid-orbital sets (sp, sp2, sp3) and classify coaxial vs lateral orbital overlaps", "success_criterion": "Apply orbital conservation (n atomic orbitals mix to yield n hybrid orbitals) and distinguish cylindrical sigma symmetry from nodal pi symmetry", "prerequisite_refs": [CAP_DOM], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_3D), "action": "Translate flat Lewis connectivity sketches into 3D wedge-dash stereochemical representations and evaluate qualitative models", "success_criterion": "Accurately depict 3D tetrahedral bond angles (109.5° / 107°) with wedge-dash notation and evaluate VSEPR predictive scope vs orbital overlap boundaries", "prerequisite_refs": [CAP_DOM, CAP_HYB], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
]

relations = [
    {
        **base(REL_STR),
        "expression": "Steric Number = (number of bonded atoms) + (number of lone pairs on central atom)",
        "meaning": "Each bonded atom constitutes exactly one bonding domain regardless of bond order (single, double, triple); only lone pairs localized on the central atom contribute to its steric environment.",
        "symbols": [
            {"symbol": "SN", "meaning": "steric number / total electron domains", "unit_or_domain": "integer {2, 3, 4, 5, 6}"},
            {"symbol": "B", "meaning": "number of attached bonded atoms", "unit_or_domain": "integer"},
            {"symbol": "LP", "meaning": "number of non-bonding electron pairs on the central atom", "unit_or_domain": "integer"}
        ],
        "conditions": [
            "Count each attached atom as one domain regardless of single/double/triple bond order.",
            "Include only unshared electron pairs on the central atom, excluding terminal ligand lone pairs."
        ],
        "derivation": [
            step("STR-S1", "DECLARE", "Identify the central atom and inventory attached atoms.", "Attached atoms define primary bonding directions.", "bonded atom count"),
            step("STR-S2", "DECLARE", "Count non-bonding valence electron pairs residing strictly on the central atom.", "Terminal lone pairs do not affect the central atom's steric number.", "central lone pair count"),
            step("STR-S3", "TRANSFORM", "Sum bonded atoms and central lone pairs to determine total electron domains.", "Total domains govern spatial electrostatic repulsion.", "steric number SN")
        ],
        "limits": ["Steric number assumes localized electron domains; delocalized resonance structures require evaluating resonance hybrids."],
        "checks": ["Verify that double or triple bonds are not counted as multiple spatial directions."],
        "gate_relation_ref": "REL-CHE-STERIC-NUMBER"
    },
    {
        **base(REL_CON),
        "expression": "n atomic orbitals mixed -> n hybrid orbitals produced (sp -> 2, sp2 -> 3, sp3 -> 4)",
        "meaning": "Linear combination of valence atomic orbitals conserves total orbital count; the number of directional hybrid orbitals formed equals the steric number of electron domains.",
        "symbols": [
            {"symbol": "n", "meaning": "number of hybrid orbitals produced", "unit_or_domain": "integer"},
            {"symbol": "s, p", "meaning": "constituent atomic orbitals mixed", "unit_or_domain": "wavefunctions"}
        ],
        "conditions": [
            "Hybridisation occurs between orbitals of comparable energy in the valence shell of the central atom.",
            "Number of hybrid orbitals formed strictly equals the number of pure atomic orbitals hybridized."
        ],
        "derivation": [
            step("CON-S1", "DECLARE", "Determine the required number of equivalent electron domain directions.", "Steric number sets directional requirement.", "domain count"),
            step("CON-S2", "TRANSFORM", "Mix 2s with one, two, or three 2p orbitals to form the corresponding hybrid set.", "Conservation of orbitals governs hybrid set formation.", "hybrid orbital set"),
            step("CON-S3", "VERIFY", "Check that the number of hybrid orbital directions matches the steric domain count.", "Matching avoids excess or missing orbital directions.", "verified hybrid set")
        ],
        "limits": ["Hybridisation is a valence-bond mathematical model, not a physical excitation step."],
        "checks": ["Count pure atomic orbitals: 1s + 1p = 2 (sp); 1s + 2p = 3 (sp2); 1s + 3p = 4 (sp3)."],
        "gate_relation_ref": "REL-CHE-HYBRID-ORBITAL-CONSERVATION"
    },
    {
        **base(REL_SYM),
        "expression": "σ bond: coaxial end-on overlap with cylindrical symmetry; π bond: lateral side-on overlap with nodal plane on internuclear axis",
        "meaning": "Covalent bonds are classified by orbital overlap geometry: sigma bonds have electron density concentrated directly along the internuclear axis; pi bonds have electron density above and below that axis.",
        "symbols": [
            {"symbol": "σ", "meaning": "sigma bond / coaxial overlap", "unit_or_domain": "symmetry class"},
            {"symbol": "π", "meaning": "pi bond / lateral overlap", "unit_or_domain": "symmetry class"}
        ],
        "conditions": [
            "Internuclear axis is conventionally taken as the z-axis.",
            "Atomic orbitals must have matching symmetry and favorable phase overlap."
        ],
        "derivation": [
            step("SYM-S1", "DECLARE", "Identify the internuclear line connecting the two nuclei.", "The bond axis serves as the spatial reference.", "internuclear axis"),
            step("SYM-S2", "TRANSFORM", "Evaluate orbital lobe orientation: along the axis (end-on) versus perpendicular to the axis (side-on).", "Overlap geometry determines boundary symmetry.", "overlap classification"),
            step("SYM-S3", "VERIFY", "Check for cylindrical symmetry (sigma) or a nodal plane on the axis (pi).", "Symmetry criteria confirm bond classification.", "verified bond type")
        ],
        "limits": ["Pi bonds cannot form without an underlying sigma framework between the same nuclei."],
        "checks": ["Confirm zero electron density along the internuclear axis for pi bonds."],
        "gate_relation_ref": "REL-CHE-ORBITAL-OVERLAP-SYMMETRY"
    }
]

representations = [
    representation(
        REP_TET, "STRUCTURAL_FORMULA",
        "Translate flat 2D Lewis drawings into 3D non-coplanar tetrahedral geometry using wedge-dash notation.",
        "evidence/benchmark/ISS32/assets/hybrid-tetrahedral-3d.svg",
        [
            ("TET-STAGE-1", "Flat 2D cross", "Recognise that flat drawings force artificial 90-degree angles."),
            ("TET-STAGE-2", "3D spatial separation", "See four electron domains repel into a 109.5-degree regular tetrahedron."),
            ("TET-STAGE-3", "Wedge-dash notation", "Use solid in-plane lines, forward solid wedge, and backward dashed wedge.")
        ],
        [
            {"element": "solid in-plane lines", "symbol": "in-plane bonds", "in_words": "two bonds lying within the drawing surface"},
            {"element": "solid wedge", "symbol": "projecting bond", "in_words": "bond directed forward toward the viewer"},
            {"element": "dashed wedge", "symbol": "receding bond", "in_words": "bond directed backward away from the viewer"}
        ]
    ),
    representation(
        REP_SIG, "ORBITAL_DIAGRAM",
        "Classify orbital overlaps as coaxial end-on sigma bonds versus lateral side-on pi bonds with nodal planes.",
        "evidence/benchmark/ISS32/assets/sigma-pi-overlap.svg",
        [
            ("SIGMA-PI-1", "Internuclear axis", "Establish the reference line connecting the nuclei."),
            ("SIGMA-PI-2", "End-on coaxial overlap", "Identify cylindrical symmetry and density along the axis for sigma bonds."),
            ("SIGMA-PI-3", "Lateral side-on overlap", "Identify parallel lobes and the nodal plane along the axis for pi bonds.")
        ],
        [
            {"element": "coaxial overlap", "symbol": "σ bond", "in_words": "head-to-head overlap with cylindrical symmetry"},
            {"element": "lateral overlap", "symbol": "π bond", "in_words": "side-on overlap with a nodal plane on the internuclear axis"}
        ]
    ),
    representation(
        REP_DOM, "STRUCTURAL_FORMULA",
        "Group bonding and non-bonding electron pairs into spatial steric domains around central atoms.",
        "evidence/benchmark/ISS32/assets/electron-domains-hcho.svg",
        [
            ("DOM-STAGE-1", "Lewis structure", "Identify shared pairs and non-bonding pairs."),
            ("DOM-STAGE-2", "Steric domain envelopes", "Group the double bond as a single spatial domain constrained along the C-O axis."),
            ("DOM-STAGE-3", "Trigonal planar outcome", "Establish three domains (sp2, 120 degrees) in H2C=O.")
        ],
        [
            {"element": "C=O domain envelope", "symbol": "1 electron domain", "in_words": "both electron pairs of the double bond occupy one spatial direction"}
        ]
    )
]

families = [
    {
        **base(FAM_DOM),
        "title": "Steric electron-domain counting and multiple-bond constraints",
        "capability_refs": [CAP_DOM],
        "solution_structure": [
            "Locate the central atom and identify all attached bonded atoms.",
            "Treat single, double, or triple bonds to an attached atom as exactly one bonding domain.",
            "Count unshared lone pairs residing directly on the central atom; exclude terminal lone pairs.",
            "Sum bonding domains and central lone pairs to obtain total steric number."
        ],
        "demand_dimensions": {
            "model_choice": "Distinguish electron pair count from steric spatial domain count.",
            "representation_translation": "Translate Lewis structural formulas into steric domain groupings.",
            "reasoning_steps": "Inventory bonded atoms, add central lone pairs, verify exclusion of terminal lone pairs.",
            "novelty": "Multiple bonds (double/triple) and peripheral lone pairs as intentional distractors."
        },
        "safe_variations": ["Change central atom or ligand atoms while preserving steric number rules."],
        "transfer_boundaries": ["Odd-electron free radicals or hypervalent expanded octets require advanced extensions."],
        "common_wrong_routes": ["Count double bonds as two domains or add terminal halogen lone pairs to the central atom count."],
        "item_refs": [BANK_IDS[x] for x in ("Q2", "Q8", "Q9")]
    },
    {
        **base(FAM_HYB),
        "title": "Hybrid-orbital mapping, orbital symmetry, and 3D stereochemical representation",
        "capability_refs": [CAP_HYB, CAP_3D],
        "solution_structure": [
            "Determine total electron domains from steric inventory.",
            "Map domain count to hybrid set (2->sp, 3->sp2, 4->sp3) using orbital conservation.",
            "Represent non-coplanar 3D geometry using wedge-dash notation (two in-plane, one wedge, one dash).",
            "Classify orbital overlaps (sigma vs pi) and evaluate predictive boundaries of VSEPR vs orbital models."
        ],
        "demand_dimensions": {
            "model_choice": "Select between VSEPR geometric repulsion and Valence Bond orbital overlap.",
            "representation_translation": "Translate flat 2D Lewis sketches into 3D wedge-dash stereochemical structures.",
            "reasoning_steps": "Determine steric domains, select hybrid set, construct 3D representation, check symmetry/angles.",
            "novelty": "Distinguishing what VSEPR predicts (geometry) from what it leaves unresolved (wave mechanics)."
        },
        "safe_variations": ["Vary steric numbers 2, 3, and 4 and compare coaxial vs lateral overlap scenarios."],
        "transfer_boundaries": ["d-orbital participation in hypervalent molecules is omitted in introductory models."],
        "common_wrong_routes": ["Assume 4 domains produce 90-degree square planar geometry on flat paper."],
        "item_refs": [BANK_IDS[x] for x in ("Q1", "Q3", "Q4", "Q5", "Q6", "Q7", "Q10")]
    }
]

microtopics = [
    {
        **base(MIC_DOM),
        "title": "Steric electron-domain counting and multiple bonds",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_DOM,
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "Multiple bonds and terminal lone pairs frequently trigger incorrect steric number counts.",
        "entry_assumptions": ["Recognises single and multiple bonds in simple Lewis structures."],
        "inferential_jump": "An electron domain is a spatial direction of repulsive charge; all electrons between two bonded atoms constitute exactly one domain.",
        "teaching_path": [
            step("DOM-T1", "DECLARE", "Count each bonded atom as one domain regardless of bond order.", "Multiple electron pairs between the same two nuclei share one internuclear direction.", "bonded atom domain count"),
            step("DOM-T2", "DECLARE", "Include only lone pairs residing directly on the central atom.", "Peripheral lone pairs on ligands do not influence the central atom's steric number.", "central lone pair count"),
            step("DOM-T3", "TRANSFORM", "Sum bonding domains and central lone pairs to obtain total electron domains.", "Total domains determine the underlying electrostatic geometry.", "total electron domains")
        ],
        "relation_refs": [REL_STR],
        "representation_refs": [REP_DOM],
        "question_family_refs": [FAM_DOM],
        "misconceptions": [
            misconception(
                "A double bond counts as two electron domains because it contains two pairs of electrons.",
                "Can the pi bond electrons point into an independent spatial direction away from the C=O axis?",
                "An electron domain corresponds to a direction in space; all electrons between two nuclei form a single domain."
            )
        ],
        "exit_task": {
            "prompt": "For hydrogen cyanide (H-C≡N), determine the number of electron domains around carbon and state whether the triple bond counts as one, two, or three domains.",
            "source_ref": SRC,
            "answer": model_answer("Carbon has 2 electron domains (one C-H single bond and one C≡N triple bond). The triple bond counts as exactly one domain.", ["Carbon has 2 attached atoms (H and N) and 0 lone pairs.", "All 6 shared electrons in the triple bond occupy the single spatial direction between C and N."], "Steric number = 2 + 0 = 2 domains (linear geometry, sp hybridisation)."),
            "oracle": {"no_numeric_claim": "The task checks domain counting on a multiple bond."}
        },
        "research_contribution": "Q2, Q8, and Q9 demonstrate that domain definition is the primary gatekeeper for geometry.",
        "prerequisite_refs": [],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Does a C=O double bond count as two separate directions around carbon?", "defensible_answer": "No; both pairs share the same internuclear coordinate line and act as one domain."},
            "attempt": {
                "produces": "A domain inventory distinguishing bonded atoms from individual electron pairs.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Treats double bond as 1 domain and excludes terminal lone pairs.", "evidence_of": "Understands spatial definition of electron domains."}],
                "accepted": ["Double bond = 1 domain; only central lone pairs count."],
                "rejected": ["Double bond = 2 domains.", "Include terminal fluorine lone pairs in central count."],
                "task": {"prompt": "List the bonding domains and central lone pairs for H2C=O.", "givens": ["Lewis structure of formaldehyde."], "representation_ref": REP_DOM}
            },
            "reconstruct": {
                "route": [
                    {"ask": "How many distinct atoms are attached to the central carbon?", "why_this_ask": "Each attached atom defines one bonding domain."},
                    {"ask": "Are there any unshared pairs localized on carbon?", "why_this_ask": "Identifies central non-bonding domains."}
                ],
                "differs_from_teaching_path": "Starts from attached atom count rather than electron pair enumeration."
            },
            "boundary_test": {"prompt": "If a triple bond is present instead of a double bond, how many domains does it count as?", "answer": "Exactly one domain; all shared pairs occupy the same internuclear space.", "confirms": "Domain count depends on bonded atom direction, not bond multiplicity."}
        },
        "construction_units": [
            {
                "id": "CU-CHE-DOMAIN-COUNTING",
                "decision": "Count each bonded atom as one domain and add only central lone pairs",
                "step_refs": ["DOM-T1", "DOM-T2", "DOM-T3"],
                "representation_ref": REP_DOM,
                "reveal_stage_refs": ["DOM-STAGE-1", "DOM-STAGE-2", "DOM-STAGE-3"],
                "bank_anchor_ref": BANK_IDS["Q2"],
                "crux_question_refs": [BANK_IDS["Q2"], BANK_IDS["Q8"], BANK_IDS["Q9"]],
                "crux_step_ref": "DOM-T1",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: Count electron domains in CO2 without confusing two double bonds with four domains.", "role": "CHECK"},
                    {"statement": "APPLY: Explain why peripheral lone pairs on oxygen in H2C=O do not affect carbon's geometry.", "role": "APPLY"},
                    {"statement": "CONNECT: Connect 3 electron domains in H2C=O to 120-degree trigonal planar geometry.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Double bond or multiple lone pairs? Inventory spatial directions first.", "result": "Each bonded atom is 1 domain; only central lone pairs count.", "representation_ref": REP_DOM}
    },
    {
        **base(MIC_HYB),
        "title": "Hybridisation, orbital conservation, and overlap symmetry",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_HYB,
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "Learners must correlate domain counts with conserved hybrid sets and classify overlap symmetry.",
        "entry_assumptions": ["Understands basic s and p atomic orbital shapes."],
        "inferential_jump": "The number of hybrid orbitals produced strictly equals the number of pure atomic orbitals mixed; end-on overlap gives cylindrical sigma symmetry, while lateral overlap produces a nodal plane.",
        "teaching_path": [
            step("HYB-T1", "DECLARE", "Match the steric domain count to the required number of hybrid orbitals.", "Electrons repel into symmetric 3D directions requiring equivalent hybrid orbitals.", "domain-hybrid requirement"),
            step("HYB-T2", "TRANSFORM", "Combine one s orbital with the necessary p orbitals (sp, sp2, sp3) conserving total orbital count.", "Orbital conservation dictates that mixing n atomic orbitals yields n hybrid orbitals.", "conserved hybrid orbital set"),
            step("HYB-T3", "VERIFY", "Classify bond overlaps: coaxial end-on as sigma (cylindrical) and lateral side-on as pi (nodal plane).", "Symmetry criteria confirm bond type.", "verified overlap and bond class")
        ],
        "relation_refs": [REL_CON, REL_SYM],
        "representation_refs": [REP_SIG],
        "question_family_refs": [FAM_HYB],
        "misconceptions": [
            misconception(
                "An sp3 hybrid set contains 3 orbitals because of the exponent 3 on p.",
                "How many atomic orbitals were mixed in total to make an sp3 set?",
                "Orbital count is conserved: one s + three p = four sp3 hybrid orbitals."
            )
        ],
        "exit_task": {
            "prompt": "BeCl2 has two bonding domains and zero central lone pairs. Identify the hybridisation of beryllium and state whether the Be-Cl bonds are sigma or pi.",
            "source_ref": SRC,
            "answer": model_answer("Beryllium is sp hybridized (mixing 1s + 1p = 2 hybrid orbitals at 180°). Both Be-Cl single bonds are sigma bonds formed by coaxial end-on overlap.", ["Steric number = 2 bonding domains + 0 lone pairs = 2 domains.", "Two directions require sp hybridisation.", "Single bonds formed along the internuclear axis are sigma bonds."], "Confirm that two hybrid orbitals yield linear geometry with cylindrical bond symmetry."),
            "oracle": {"no_numeric_claim": "The task assesses hybridisation mapping and sigma classification."}
        },
        "research_contribution": "Q1, Q3, Q6, and Q10 establish the link between steric domain counts, orbital conservation, and overlap classification.",
        "prerequisite_refs": [CAP_DOM],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "When 1 s orbital and 2 p orbitals mix, how many hybrid orbitals are formed?", "defensible_answer": "Three sp2 hybrid orbitals, conserving the number of mixed orbitals."},
            "attempt": {
                "produces": "A hybridisation assignment and overlap symmetry classification.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Conserves orbital count and classifies end-on as sigma and side-on as pi.", "evidence_of": "Applies Valence Bond hybridisation and symmetry principles."}],
                "accepted": ["sp3 has 4 orbitals; end-on is sigma; side-on is pi."],
                "rejected": ["sp3 has 3 orbitals.", "Side-on overlap is sigma."],
                "task": {"prompt": "Match BF3 (3 domains) and CH4 (4 domains) to their hybrid sets and classify coaxial overlap.", "givens": ["Domain counts for BF3 and CH4."], "representation_ref": REP_SIG}
            },
            "reconstruct": {
                "route": [
                    {"ask": "How many pure atomic orbitals entered the hybridisation?", "why_this_ask": "Enforces orbital conservation."},
                    {"ask": "Is the electron density concentrated along the internuclear axis or split by a nodal plane?", "why_this_ask": "Discriminates sigma from pi overlap."}
                ],
                "differs_from_teaching_path": "Starts from symmetry inspection and orbital tally rather than formula matching."
            },
            "boundary_test": {"prompt": "Can a pi bond form along the internuclear axis without an existing sigma bond?", "answer": "No; pi overlap is lateral and occurs only after coaxial sigma framework is in place.", "confirms": "Sigma and pi bonds have distinct geometric and energetic roles."}
        },
        "construction_units": [
            {
                "id": "CU-CHE-HYBRID-CONSERVATION",
                "decision": "Conserve total orbital count when mapping electron domains to hybrid sets and classifying overlap",
                "step_refs": ["HYB-T1", "HYB-T2", "HYB-T3"],
                "representation_ref": REP_SIG,
                "reveal_stage_refs": ["SIGMA-PI-1", "SIGMA-PI-2", "SIGMA-PI-3"],
                "bank_anchor_ref": BANK_IDS["Q10"],
                "crux_question_refs": [BANK_IDS["Q1"], BANK_IDS["Q3"], BANK_IDS["Q6"], BANK_IDS["Q10"]],
                "crux_step_ref": "HYB-T2",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: State the number of hybrid orbitals in an sp2 set and name their geometric separation.", "role": "CHECK"},
                    {"statement": "APPLY: Classify the second bond in a C=C double bond as sigma or pi using nodal criteria.", "role": "APPLY"},
                    {"statement": "CONNECT: Verify that 4 equivalent domains in CH4 require an sp3 set with 109.5-degree angles.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Domain count to hybrid set? Conserve orbital count.", "result": "n domains require n hybrid orbitals; coaxial = sigma, lateral = pi.", "representation_ref": REP_SIG}
    },
    {
        **base(MIC_3D),
        "title": "3D Stereochemical representation and qualitative models",
        "bucket_id": BUCKET,
        "primary_capability_ref": CAP_3D,
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "Translating flat 2D Lewis drawings into 3D wedge-dash geometry and understanding model boundaries are major sticking points.",
        "entry_assumptions": ["Understands that molecules occupy 3D space."],
        "inferential_jump": "Flat Lewis structures show connectivity, not 3D shape; wedge-dash conventions capture non-coplanar angles (109.5° / 107°), and VSEPR predicts geometry from domain repulsion without solving orbital wavefunctions.",
        "teaching_path": [
            step("REP-T1", "DECLARE", "Distinguish 2D topological connectivity (Lewis) from 3D spatial geometry (VSEPR/wedge-dash).", "Paper is flat, but four electron domains maximize separation in three dimensions.", "dimensional distinction"),
            step("REP-T2", "TRANSFORM", "Apply wedge-dash conventions: two bonds in-plane (lines), one forward (wedge), one backward (dash).", "Standard stereochemical notation makes non-coplanar depth explicit.", "wedge-dash 3D construction"),
            step("REP-T3", "VERIFY", "Delineate model boundaries: VSEPR predicts domain geometry and angles; it leaves orbital wavefunctions and spectra unresolved.", "Clear scope prevents over-claiming qualitative model abilities.", "verified model scope")
        ],
        "relation_refs": [REL_STR, REL_CON],
        "representation_refs": [REP_TET],
        "question_family_refs": [FAM_HYB],
        "misconceptions": [
            misconception(
                "A flat Lewis cross indicates that methane has 90-degree bond angles.",
                "Does a flat 2D drawing represent true spatial distribution when 3D space is available?",
                "In 3D space, domains achieve 109.5-degree separation in a tetrahedron, which has less repulsion than 90 degrees."
            )
        ],
        "exit_task": {
            "prompt": "For water (H2O), sketch a 3D representation using wedge-dash notation showing both lone pairs. Explain why the H-O-H bond angle is ~104.5° rather than 90° or 180°.",
            "source_ref": SRC,
            "answer": model_answer("Oxygen has 4 electron domains (2 bonding, 2 lone pairs) arranged tetrahedrally. Two bonds lie in-plane or with wedge/dash, while lone pairs occupy the other vertices. Lone pair repulsion compresses the ideal 109.5° tetrahedral angle to ~104.5°.", ["Steric number = 2 bonding + 2 lone pairs = 4 domains.", "Four domains repel into 3D tetrahedral geometry, not a 180° flat line or 90° square.", "Lone-pair–lone-pair and lone-pair–bonding-pair repulsion compresses the H-O-H angle to 104.5°."], "Confirm 4 tetrahedral domains and trigonal planar/bent distinction."),
            "oracle": {"no_numeric_claim": "The task assesses 3D wedge-dash translation and lone pair repulsion."}
        },
        "research_contribution": "Q4, Q5, and Q7 require learners to move beyond flat drawings and evaluate theoretical models.",
        "prerequisite_refs": [CAP_DOM, CAP_HYB],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Are the four C-H bonds in methane coplanar?", "defensible_answer": "No; they point towards the vertices of a 3D tetrahedron and cannot be made coplanar."},
            "attempt": {
                "produces": "A 3D wedge-dash drawing and model boundary evaluation.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Uses wedge-dash notation and identifies VSEPR predictions vs limits.", "evidence_of": "Understands 3D stereochemical representation and theoretical model boundaries."}],
                "accepted": ["Wedge-dash shows 3D depth; VSEPR predicts geometry but not orbital overlap wavefunctions."],
                "rejected": ["Flat Lewis drawing represents shape.", "VSEPR explains wave mechanics of bonding."],
                "task": {"prompt": "Draw CH4 using wedge-dash notation and contrast with a flat Lewis cross.", "givens": ["CH4 molecular formula."], "representation_ref": REP_TET}
            },
            "reconstruct": {
                "route": [
                    {"ask": "What angle maximizes separation among four identical charge clouds in 3D?", "why_this_ask": "Derives the 109.5 degree tetrahedral angle."},
                    {"ask": "How do we show that two bonds point out of the plane on paper?", "why_this_ask": "Motivates wedge-dash notation."}
                ],
                "differs_from_teaching_path": "Starts from electrostatic optimization in 3D rather than drawing rules."
            },
            "boundary_test": {"prompt": "If only 3 domains are present (as in BF3), do they require wedge-dash for out-of-plane depth?", "answer": "No; 3 domains lie entirely in a single plane at 120 degrees (trigonal planar).", "confirms": "Wedge-dash is necessary specifically for non-coplanar 3D geometries."}
        },
        "construction_units": [
            {
                "id": "CU-CHE-3D-REPRESENTATION",
                "decision": "Depict non-coplanar tetrahedral domains with wedge-dash notation and evaluate qualitative model boundaries",
                "step_refs": ["REP-T1", "REP-T2", "REP-T3"],
                "representation_ref": REP_TET,
                "reveal_stage_refs": ["TET-STAGE-1", "TET-STAGE-2", "TET-STAGE-3"],
                "bank_anchor_ref": BANK_IDS["Q4"],
                "crux_question_refs": [BANK_IDS["Q4"], BANK_IDS["Q5"], BANK_IDS["Q7"]],
                "crux_step_ref": "REP-T2",
                "misconception_indexes": [0],
                "independent_checks": [
                    {"statement": "CHECK: Identify which line style indicates a bond pointing towards the observer.", "role": "CHECK"},
                    {"statement": "APPLY: Draw NH3 in 3D showing how lone pair repulsion compresses the H-N-H angle to ~107 degrees.", "role": "APPLY"},
                    {"statement": "CONNECT: Explain what VSEPR predicts about NH3 and what it leaves for Valence Bond theory.", "role": "CONNECT"}
                ]
            }
        ],
        "compact_anchor": {"prompt": "Flat cross or 3D tetrahedron? Use wedge-dash.", "result": "Four domains require 3D wedge-dash; VSEPR predicts shape from repulsion.", "representation_ref": REP_TET}
    }
]

purpose_delivery = {
    "COMPETITION": {
        "section_title": "Competition transfer",
        "support_policy": "NO_MID_TASK_BRIDGING",
        "items": [
            {
                "id": "CHE-COMP-TRANSFER-ALLENE",
                "roles": ["CORE1A", "CORE2"],
                "concept_refs": [MIC_HYB],
                "question_refs": [BANK_IDS["Q6"]],
                "title": "Orbital overlap planes in allene (H2C=C=CH2)",
                "prompt": "In propadiene (allene, H2C=C=CH2), the central carbon atom forms two double bonds. Identify the hybridisation of the central carbon and deduce whether the two terminal CH2 groups lie in the same plane or in mutually perpendicular planes. Support your conclusion using orbital overlap symmetry.",
                "source_kind": "AUTHOR_CREATED_COMPETITION_STYLE",
                "source_ref": None,
                "source_label": "Original competition-style transfer; not claimed as an official past-paper item.",
                "response": {"type": "free_response", "paper_ok": True},
                "answer": {
                    "summary": "The central carbon is sp hybridized, and the two terminal CH2 groups lie in mutually perpendicular planes.",
                    "reasoning": [
                        "The central carbon has 2 bonding domains and 0 lone pairs, giving sp hybridisation with a linear 180° C-C-C backbone.",
                        "The central carbon has two unhybridized 2p orbitals (say, 2py and 2pz) that are mutually orthogonal (at 90° to each other).",
                        "One double bond is formed by lateral overlap with a 2py orbital of the left carbon, while the other double bond is formed by lateral overlap with a 2pz orbital of the right carbon.",
                        "Because the two pi bonds are oriented in perpendicular planes, the sigma frameworks and terminal CH2 groups must also be oriented in mutually perpendicular planes."
                    ]
                }
            },
            {
                "id": "CHE-COMP-TRANSFER-AMIDE-DELOC",
                "roles": ["CORE1A", "CORE2"],
                "concept_refs": [MIC_DOM],
                "question_refs": [BANK_IDS["Q2"]],
                "title": "Nitrogen hybridisation in formamide and lone pair delocalisation",
                "prompt": "In an isolated amine (such as NH3), nitrogen is sp3 hybridized with a pyramidal geometry. In formamide (HCONH2), however, the nitrogen atom is experimentally observed to be nearly planar. Using electron domain and resonance arguments, explain why nitrogen's lone pair changes its effective steric behavior and hybridisation.",
                "source_kind": "AUTHOR_CREATED_COMPETITION_STYLE",
                "source_ref": None,
                "source_label": "Original competition-style transfer; not claimed as an official past-paper item.",
                "response": {"type": "free_response", "paper_ok": True},
                "answer": {
                    "summary": "The nitrogen lone pair is delocalised into the adjacent C=O carbonyl pi system via resonance, requiring nitrogen to adopt sp2 hybridisation and planar geometry.",
                    "reasoning": [
                        "The nitrogen lone pair participates in resonance: H2N-CH=O <-> H2N+=CH-O-.",
                        "For resonance overlap to occur, nitrogen's non-bonding pair must occupy an unhybridized 2p orbital parallel to the carbonyl pi bond.",
                        "This re-hybridizes nitrogen from sp3 to sp2, leaving three in-plane sigma bonding directions (trigonal planar, ~120°) and one perpendicular p orbital containing the delocalised pair."
                    ]
                }
            }
        ]
    }
}

package = {
    "schema_version": "0.2.0",
    "package_id": "PKG-CHE-11-HYBRIDISATION-D1-B",
    "title": "Chemical Bonding and Hybridisation — Issue #32 specimen",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Chemistry",
    "scope_summary": "Grade 11 competition specimen derived from ten owner-supplied bonding and hybridisation questions; candidate teaching records are authored independently and claim no official source identity.",
    "curriculum_mappings": [],
    "resources": [resource],
    "buckets": [bucket],
    "capabilities": capabilities,
    "microtopics": microtopics,
    "relations": relations,
    "representations": representations,
    "question_families": families,
    "questions": [],
    "teaching_routes": [],
    "practice_profiles": [],
    "evidence": [],
    "known_issues": [],
    "extensions": {
        "grade9v3:authoring_specimen": {
            "issue": 32,
            "purpose": "COMPETITION",
            "learner_profile_ref": "PROFILE-ISSUE32-CHEM-HYBRIDISATION",
            "qrt_evidence": "evidence/benchmark/ISS32/qrt-review.json"
        },
        "grade9v3:purpose_delivery": purpose_delivery,
    },
    "data": [],
}

(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote package.v1.json successfully")

# Construct owner.bank.json
MOVES_PER_Q = {
    "Q1": [
        ("DECIDE", "Identify required domain directions", "Four equivalent directions point toward the corners of a tetrahedron.", "4 directions", "directions"),
        ("CONNECT", "Combine valence s and p atomic orbitals", "One 2s and three 2p atomic orbitals combine via linear combination.", "1s + 3p combination", "orbital mixing"),
        ("TRANSFORM", "Name hybrid set and state count", "Mixing 4 atomic orbitals yields 4 sp3 hybrid orbitals.", "sp3, 4 orbitals", "sp3 set and count"),
        ("VERIFY", "Check orbital conservation", "1 + 3 = 4, verifying that orbital count is strictly conserved.", "conservation check", "verified count")
    ],
    "Q2": [
        ("DECIDE", "Inventory electron pairs in double bond", "A C=O double bond has four shared electrons (one sigma and one pi bond).", "two shared pairs", "electron inventory"),
        ("CONNECT", "Evaluate spatial region between C and O nuclei", "Both sigma and pi electrons reside between the same carbon and oxygen nuclei along one internuclear axis.", "shared internuclear region", "spatial constraint"),
        ("TRANSFORM", "Conclude single electron domain", "Because both pairs share the same direction, they act as a single localized repulsive domain.", "1 electron domain", "domain assignment"),
        ("VERIFY", "Check total domains around carbon", "Carbon has two C-H single bonds (2 domains) and one C=O double bond (1 domain), totaling 3 domains.", "3 domains total", "domain verification")
    ],
    "Q3": [
        ("DECIDE", "Count bonding domains and central lone pairs", "CH4 has 4 single C-H bonds and 0 lone pairs on carbon.", "4 bonding, 0 lone pair", "domain counts"),
        ("TRANSFORM", "Sum domains for steric number", "4 bonding domains + 0 lone pairs = 4 electron domains.", "4 domains", "total domains"),
        ("CONNECT", "Map domains to geometry and hybridisation", "Four electron domains repel to tetrahedral geometry (109.5°) and require sp3 hybridisation.", "sp3, tetrahedral", "model assignment"),
        ("VERIFY", "Check orbital direction agreement", "Four sp3 hybrid orbitals match four bonding domains in three dimensions.", "agreement check", "verified mapping")
    ],
    "Q4": [
        ("DECIDE", "Inventory domains in NH3", "Nitrogen has 3 N-H bonding pairs and 1 central lone pair, giving 4 electron domains.", "4 domains (3 bond, 1 LP)", "domain tally"),
        ("REPRESENT", "Construct 3D wedge-dash diagram", "Draw N with two in-plane bonds, one wedge, one dash, and one lone pair in an axial lobe.", "3D wedge-dash diagram", "stereochemical drawing"),
        ("TRANSFORM", "Contrast with flat Lewis sketch", "Explain that flat Lewis cross is 2D topological connectivity, while electron repulsion enforces 3D tetrahedral domain geometry (~107° trigonal pyramidal molecule).", "3D vs flat contrast", "geometric explanation"),
        ("VERIFY", "Check non-coplanarity and lone pair distinction", "Confirm that 3 bonds are non-coplanar and the lone pair is localized at the fourth tetrahedral vertex.", "verified 3D diagram", "drawing verification")
    ],
    "Q5": [
        ("DECIDE", "Select qualitative model", "Select VSEPR because only overall 3D domain arrangement is requested, not detailed orbital overlap.", "VSEPR model", "model selection"),
        ("CONNECT", "Identify what chosen model predicts", "VSEPR predicts tetrahedral electron domain geometry, trigonal pyramidal shape, and ~107° angle compression via electrostatic repulsion.", "geometric predictions", "predictive successes"),
        ("TRANSFORM", "Identify what chosen model leaves unresolved", "VSEPR does not explain quantum wavefunctions, atomic orbital mixing, orbital symmetry/phases, bond energies, or electronic spectra.", "unresolved orbital aspects", "model boundaries"),
        ("VERIFY", "Confirm boundary delineation", "Confirm that VSEPR provides a complete geometric account while acknowledging wave-mechanical limits.", "boundary verification", "verified evaluation")
    ],
    "Q6": [
        ("DECIDE", "Establish internuclear axis reference", "The internuclear axis serves as the spatial reference connecting the two nuclei.", "internuclear axis", "spatial axis"),
        ("CONNECT", "Classify Overlap A as sigma", "End-on coaxial overlap produces cylindrical symmetry along the axis with maximum density between nuclei.", "sigma (σ) bond", "sigma classification"),
        ("TRANSFORM", "Classify Overlap B as pi", "Lateral side-on overlap of parallel orbitals creates a nodal plane containing the internuclear axis.", "pi (π) bond", "pi classification"),
        ("VERIFY", "Verify nodal and symmetry criteria", "Sigma has non-zero density along the axis; pi has zero density (nodal plane) on the axis.", "symmetry check", "verified classification")
    ],
    "Q7": [
        ("DECIDE", "Identify tetrahedral geometry of CH4", "Four C-H bonds point toward the vertices of a regular tetrahedron at 109.5° angles.", "tetrahedral 109.5°", "spatial target"),
        ("REPRESENT", "Draw 3D wedge-dash structure", "Draw two solid in-plane lines at 109.5°, one solid wedge forward, and one dashed wedge backward.", "wedge-dash CH4", "3D drawing"),
        ("TRANSFORM", "Contrast with 2D Lewis cross", "Explain that 2D cross falsely implies 90° planar angles, whereas wedge-dash captures non-coplanar 109.5° 3D geometry.", "3D vs 2D explanation", "stereochemical contrast"),
        ("VERIFY", "Check angle and depth convention", "Confirm that four bonds are equivalent and out-of-plane depth is clearly communicated.", "verified representation", "drawing check")
    ],
    "Q8": [
        ("DECIDE", "Identify central atom and attached atoms", "Nitrogen is the central atom with 3 single bonds to fluorine atoms.", "3 N-F single bonds", "central coordination"),
        ("CONNECT", "Distinguish central from terminal lone pairs", "Nitrogen has 1 central lone pair; the three fluorines carry 9 peripheral lone pairs (3 each).", "1 central LP, 9 terminal LP", "lone pair inventory"),
        ("TRANSFORM", "Count domains around nitrogen", "Count: 3 bonding domains + 1 central lone pair = 4 domains. Only nitrogen's lone pair belongs in the central-atom count.", "4 domains, N lone pair only", "domain calculation"),
        ("VERIFY", "Check exclusion of peripheral electrons", "Verify that the 9 terminal fluorine lone pairs do not affect nitrogen's steric domain number.", "exclusion check", "verified count")
    ],
    "Q9": [
        ("DECIDE", "Locate student counting error", "The student incorrectly counted the C=O double bond as two separate spatial directions.", "multiple-bond counting error", "error diagnosis"),
        ("CONNECT", "Explain physical domain constraint", "Both electron pairs of the double bond share the same internuclear axis and constitute only one domain.", "1 domain for double bond", "physical principle"),
        ("TRANSFORM", "Calculate corrected domain count", "Corrected count: 2 (C-H bonds) + 1 (C=O bond) = 3 electron domains around carbon (trigonal planar, sp2).", "3 electron domains", "corrected count"),
        ("VERIFY", "Verify trigonal planar geometry", "Three domains repel to 120° trigonal planar geometry, confirming the corrected count.", "geometry check", "verified correction")
    ],
    "Q10": [
        ("DECIDE", "Review benchmark table domain counts", "BF3 has 3 bonding domains, 0 lone pairs (3 domains); CH4 has 4 bonding domains, 0 lone pairs (4 domains).", "3 domains vs 4 domains", "domain review"),
        ("CONNECT", "Match molecules to hybrid sets", "BF3 matches sp2 (1s + 2p = 3 hybrid orbitals); CH4 matches sp3 (1s + 3p = 4 hybrid orbitals).", "BF3->sp2, CH4->sp3", "hybrid matching"),
        ("TRANSFORM", "Check domain-orbital agreement", "Confirm that sp2 forms 3 directions matching BF3 (3=3) and sp3 forms 4 directions matching CH4 (4=4).", "3=3 and 4=4 agreement", "conservation agreement"),
        ("VERIFY", "Verify orbital conservation law", "Confirm that number of hybrid orbitals formed strictly equals the domain count in both cases.", "conservation verification", "verified synthesis")
    ]
}

CRUX_REF = {
    "Q1": "M-Q1-3", "Q2": "M-Q2-3", "Q3": "M-Q3-3", "Q4": "M-Q4-2", "Q5": "M-Q5-3",
    "Q6": "M-Q6-2", "Q7": "M-Q7-2", "Q8": "M-Q8-3", "Q9": "M-Q9-1", "Q10": "M-Q10-3"
}

bank_questions = []
for qid in [f"Q{i}" for i in range(1, 11)]:
    stem = STEMS[qid]
    moves_spec = MOVES_PER_Q[qid]
    crux_id = CRUX_REF[qid]
    
    # Matching item from QRT
    qrt_item = next(it for it in QRT["items"] if it["question_id"] == qid)
    hints = list(qrt_item["hints"])
    if qid == "Q5":
        hints = [
            "Evaluate the question requirement: only the overall 3D domain arrangement is needed, without detailed orbital wave mechanics.",
            "Compare what VSEPR explains (electrostatic repulsion minimizing potential energy) versus what Valence Bond orbital overlap explains.",
            "Select VSEPR as the model that directly satisfies the condition of predicting 3D geometry without requiring orbital overlap.",
            "Detail what VSEPR predicts: tetrahedral electron-domain geometry, trigonal pyramidal molecular geometry, and bond angle compression to ~107 degrees due to lone-pair repulsion.",
            "Detail what VSEPR leaves unresolved: it does not explain the wave-mechanical nature of bonds, atomic orbital mixing, orbital symmetry/phases, bond energies, or electronic spectra."
        ]
    
    move_rows = []
    for n, (kind, action, why, output, role_name) in enumerate(moves_spec, 1):
        move_rows.append({
            "id": f"{BANK_IDS[qid]}-MOVE-{n}",
            "kind": kind,
            "action": action,
            "why_valid": why,
            "inputs": ["stated givens and prior move"],
            "output": output
        })
    
    stages = ["KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "FORMAL_MODEL", "CHECKPOINT"]
    kinds = ["CONNECT", "REPRESENT", "EXECUTE", "EXECUTE", "EXECUTE"]
    reveals = ["CONCEPT", "METHOD", "METHOD", "METHOD", "METHOD"]
    scaffolds = [
        {
            "text": text,
            "support_kind": kinds[i],
            "reveals": reveals[i],
            "learner_stage": stages[i],
            "supports_move_ref": move_rows[min(i, len(move_rows)-1)]["id"]
        }
        for i, text in enumerate(hints)
    ]
    
    stem_sha = "sha256:" + hashlib.sha256(stem.encode("utf-8")).hexdigest()
    
    q_obj = {
        "id": BANK_IDS[qid],
        "original_identifier": qid,
        "stem": stem,
        "conditions": [
            "Introductory valence-bond model and VSEPR rules apply; assume ideal coordination geometry unless specified."
        ],
        "family_ref": FAMILY[qid],
        "figure_refs": [FIGURE[qid]],
        "answer": {
            "kind": "EXACT",
            "summary": qrt_item["verified_answer"],
            "reasoning_route": move_rows,
            "crux_move_ref": move_rows[min(1, len(move_rows)-1)]["id"],
            "check": qrt_item["independent_check"],
            "verification_status": "CHECKED_BY_AUTHOR"
        },
        "scaffolds": scaffolds,
        "primary_capability_ref": PRIMARY_CAP[qid],
        "extensions": {
            "grade9v3:source_custody": {
                "authority_class": "OWNER_SUPPLIED_RAW_INPUT",
                "intake_ref": qid,
                "wording_custody": "VERBATIM",
                "text_sha256": stem_sha
            },
            "grade9v3:analysis": {
                "learner_question_type": "constructed_response",
                "difficulty": {
                    "band": qrt_item["difficulty"]["band"],
                    "score": qrt_item["difficulty"]["score"],
                    "components": qrt_item["difficulty"]["components"],
                    "basis": f"{qrt_item['X']} Decisive move: {qrt_item['Z']}. Total score {qrt_item['difficulty']['score']} -> {qrt_item['difficulty']['band']}."
                },
                "common_wrong_route": qrt_item["misconception"]["M1"],
                "expected_time_seconds": 90 if qrt_item["difficulty"]["band"] == "D1" else 150 if qrt_item["difficulty"]["band"] == "D2" else 240,
                "cognitive_demand": qrt_item["demand"]["primary"],
                "stable_crux_move": qrt_item["Z"]
            },
            "grade9v3:math_spans": [],
            "grade9v3:component_waivers": {
                "TRAP": f"The decisive misconception ({qrt_item['misconception']['M1']}) is taught directly in the concept unit and addressed in hint 1 and the solution.",
                "CONDITIONS": "The question specifies all boundary conditions within the stem.",
                "CHECK": f"Independent check is integrated: {qrt_item['independent_check']}"
            }
        }
    }
    bank_questions.append(q_obj)

owner_bank = {
    "schema_version": "grade9v3-owner-supplied-bank-v1",
    "bank_id": "own-issue32-hybrid",
    "questions": bank_questions
}

(OUT / "owner.bank.json").write_text(json.dumps(owner_bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote owner.bank.json successfully")

# Product manifest
manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-CHE-ISSUE32-HYBRID",
    "subject": "Chemistry",
    "home_href": "../../../index.html",
    "question_bank_href": "../../../question-bank/index.html",
    "package_refs": [
        "evidence/benchmark/ISS32/generated/package.v1.json"
    ],
    "bank_refs": [
        "evidence/benchmark/ISS32/generated/owner.bank.json"
    ],
    "selection": {
        "microtopics": [
            MIC_DOM,
            MIC_HYB,
            MIC_3D
        ],
        "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)],
        "core2a": [],
        "core2b": []
    },
    "output_roles": [
        "CORE1A",
        "CORE2"
    ]
}

(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("Wrote product.manifest.json successfully")
