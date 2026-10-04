#!/usr/bin/env python3
"""Materialise the Issue #33 independent-agent-A hybridisation candidate.

The ten owner-supplied stems remain verbatim. Academic analysis, teaching,
representations and answers are agent-authored candidate records.
"""
from __future__ import annotations
import json
from pathlib import Path
from Shared.tools import owner_bank

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"
QRT = json.loads((HERE / "qrt-review.v1.json").read_text(encoding="utf-8"))

STEMS = {
"Q1": "BF3 and NH3 each have three sigma bonds to the central atom. BF3 has no central lone pair; NH3 has one. Explain why three sigma bonds alone cannot determine the same central hybridisation and molecular shape for both.",
"Q2": "For H2C=O, assign the carbon hybridisation, count the sigma and pi components of the C=O bond, and identify the carbon orbital left available for the pi component. Keep electron-domain counting separate from counting shared electron pairs.",
"Q3": "Ethene is H2C=CH2. Translate this Lewis representation into a qualitative orbital-overlap diagram showing the C–C sigma framework, the two unhybridised carbon p orbitals and their side-on overlap. Label which directions are in the molecular plane and which are perpendicular to it.",
"Q4": "For CO2, connect the central-carbon Lewis domain count to its hybrid-orbital model, the number of remaining carbon p orbitals and the sigma/pi composition of its two C=O bonds. Explain how these pieces fit one consistent linear arrangement.",
"Q5": "Consider the claim: 'Any central atom with three sigma bonds must be sp2.' Given BF3: three B–F sigma bonds, zero boron lone pairs, planar; NH3: three N–H sigma bonds, one nitrogen lone pair, pyramidal. Decide whether these observations support the claim, give the decisive warrant, and state a more defensible introductory rule. Explain what the shape observations alone do not prove about orbitals.",
"Q6": "In CH3F, carbon has three C–H single bonds and one C–F single bond. Assign its introductory local hybridisation and explain why the number of electron-domain directions is unchanged from CH4 even though the attached atoms are different. Do not assume all bond properties are identical.",
"Q7": "HCN is represented as H–C≡N with a lone pair on nitrogen. Assign the introductory hybridisation at carbon and nitrogen, and count the sigma and pi components of the C≡N bond. Explain how the local domain count is compatible with those components.",
"Q8": "For methylamine, CH3–NH2, carbon has four single bonds and nitrogen has three single bonds plus a lone pair. Compare the introductory local hybridisation and arrangement of bonded atoms at carbon and nitrogen. Explain why the same hybridisation label does not require identical molecular shapes.",
"Q9": "A carbon centre has three sigma-bond directions, no lone pair, and participates in one pi bond. Translate this description into a qualitative local orbital arrangement and check that the orbitals used in the sigma and pi parts have not been counted twice.",
"Q10": "A student says, 'If the electron-domain geometry is tetrahedral, the atoms must form a tetrahedral molecular shape.' Evaluate the statement using CH4, NH3 and H2O, with their respective central lone-pair counts of zero, one and two.",
}

SRC="SRC-OWNER-ISS33-HYB"
BUCKET="BUCKET-CHEM-HYBRIDISATION"
CAP_DOMAIN="CAP-CHEM-HYB-DOMAIN-MODEL"
CAP_ORBITAL="CAP-CHEM-HYB-SIGMA-PI-ORBITALS"
CAP_SHAPE="CAP-CHEM-HYB-ELECTRON-VS-MOLECULAR-GEOMETRY"
MIC_DOMAIN="MIC-CHEM-HYB-DOMAIN-FIRST"
MIC_ORBITAL="MIC-CHEM-HYB-SIGMA-PI-ORBITAL-INVENTORY"
MIC_SHAPE="MIC-CHEM-HYB-DOMAIN-VS-MOLECULAR-SHAPE"
REP_DOMAIN="REP-CHEM-HYB-DOMAIN-SHAPE"
REP_SP2="REP-CHEM-HYB-SP2-ORBITAL-INVENTORY"
REP_LINEAR="REP-CHEM-HYB-LINEAR-P-INVENTORY"
FAM_DOMAIN="FAM-CHEM-HYB-DOMAIN-MODEL"
FAM_ORBITAL="FAM-CHEM-HYB-ORBITAL-OVERLAP"
FAM_SHAPE="FAM-CHEM-HYB-GEOMETRY-SHAPE"
BANK_IDS={f"Q{i}":f"OWN-ISS33-D2-V2-Q{i:02d}" for i in range(1,11)}

PRIMARY_CAP={
"Q1":CAP_SHAPE,"Q2":CAP_ORBITAL,"Q3":CAP_ORBITAL,"Q4":CAP_ORBITAL,"Q5":CAP_DOMAIN,
"Q6":CAP_DOMAIN,"Q7":CAP_ORBITAL,"Q8":CAP_SHAPE,"Q9":CAP_ORBITAL,"Q10":CAP_SHAPE}
FAMILY={
"Q1":FAM_DOMAIN,"Q2":FAM_ORBITAL,"Q3":FAM_ORBITAL,"Q4":FAM_ORBITAL,"Q5":FAM_DOMAIN,
"Q6":FAM_DOMAIN,"Q7":FAM_ORBITAL,"Q8":FAM_SHAPE,"Q9":FAM_ORBITAL,"Q10":FAM_SHAPE}
FIGURE={
"Q1":REP_DOMAIN,"Q2":REP_SP2,"Q3":REP_SP2,"Q4":REP_LINEAR,"Q5":REP_DOMAIN,
"Q7":REP_LINEAR,"Q8":REP_DOMAIN,"Q9":REP_SP2,"Q10":REP_DOMAIN}

def base(record_id, source=True):
    return {"id":record_id,"version":"0.1.0","status":"CANDIDATE",
            "source_refs":[SRC] if source else [],"evidence_refs":[],"extensions":{}}

def step(step_id, role, action, why, output):
    return {"id":step_id,"role":role,"action":action,"why_valid":why,"inputs":[],"output":output}

def model_answer(summary, reasoning, check):
    return {"kind":"MODEL_RESPONSE","summary":summary,"reasoning":reasoning,"check":check,
            "acceptable_alternatives":[],"subpart_answers":[],"verification_status":"CHECKED_BY_AUTHOR"}

def misconception(wrong, diagnostic, repair):
    return {"wrong_idea":wrong,"diagnostic_prompt":diagnostic,"repair":repair}

def representation(record_id, purpose, asset, stages, correspondence):
    return {**base(record_id,False),"kind":"ORBITAL_GEOMETRY_SCHEMATIC","purpose":purpose,
      "required_elements":[s[1] for s in stages],"relation_refs":[],
      "read_order":[s[2] for s in stages],
      "instance_constraints":["Stages teach representation rules without naming the supplied question's final answer."],
      "accessibility":["SVG has title, description and accessible name.","Text labels duplicate line-style meaning."],
      "misleading_alternatives":["Treating a pi component as an extra electron-domain direction."],
      "rendered_asset_refs":[asset],"scene_instances":[],"correspondence":correspondence,
      "reveal_stages":[{"id":sid,"label":label,"purpose":job,"visible_elements":[label]} for sid,label,job in stages],
      "extensions":{"grade9v3:stage_mode":"CUMULATIVE"}}

resource={**base(SRC,False),"title":"Issue #33 owner-supplied hybridisation benchmark questions",
 "origin":"AUTHORED","locator":"https://github.com/reallaksh19/Grade9v3.5/issues/33",
 "edition":"Owner-requested pilot input captured 2026-10-04","section":"Core prompt A — Question set Q1–Q10",
 "last_checked":"2026-10-04","access_status":"FULL_ITEM_INSPECTED",
 "rights_status":"OWNER_SUPPLIED custody; coordinator/AI-drafted benchmark input; not official exam/PYQ and not personally authored by owner.",
 "snapshot_ref":None,"snapshot_digest":None,"role":["QUESTION_BANK","AUTHOR_CREATED"],
 "supports_claims":[],"entry_capabilities":[],"depth":["COMPETITION"],
 "selection_reason":"Exact custody surface for Issue #33 A/B/C questions.","fallback":[]}

bucket={**base(BUCKET),"title":"Hybridisation, sigma/pi overlap and molecular shape","topic":"Chemical bonding and hybridisation",
 "intrinsic_badge":"MEDIUM","badge_reason":"Most items require a short conceptual or representational bridge rather than formula execution.",
 "depth_overlay":"ADVANCED","curriculum_mappings":[],"prerequisite_refs":[],"primary_representation_ref":REP_SP2,
 "scope":{"covers":"Introductory localized hybrid-orbital descriptions for the supplied BF3/NH3, H2CO, ethene, CO2, CH3F, HCN, methylamine and CH4/NH3/H2O cases.",
          "excluded":["Delocalised molecular-orbital treatments, hypervalent models, radicals and amide resonance beyond the supplied questions."]}}

capabilities=[
 {**base(CAP_DOMAIN),"action":"Choose an introductory local hybrid model from the full electron-domain count rather than sigma-bond count alone",
  "success_criterion":"Count each local direction/region once, include lone pairs, and keep multiple bonds as one domain direction.",
  "prerequisite_refs":[],"curriculum_mappings":[],"external_provider":None,"acceptance_status":"CANDIDATE"},
 {**base(CAP_ORBITAL),"action":"Coordinate sigma-framework hybrid orbitals with unhybridised p orbitals used for pi overlap",
  "success_criterion":"Allocate each local orbital once, orient sigma and pi overlap correctly, and keep domain count separate from bond-component count.",
  "prerequisite_refs":[CAP_DOMAIN],"curriculum_mappings":[],"external_provider":None,"acceptance_status":"CANDIDATE"},
 {**base(CAP_SHAPE),"action":"Distinguish electron-domain geometry from the molecular shape traced by bonded atoms",
  "success_criterion":"Hold total domains fixed while accounting for lone-pair occupancy and correctly name the bonded-atom arrangement.",
  "prerequisite_refs":[CAP_DOMAIN],"curriculum_mappings":[],"external_provider":None,"acceptance_status":"CANDIDATE"}
]

representations=[
 representation(REP_DOMAIN,
  "Separate electron-domain directions from atom-only molecular shape and make lone-pair occupancy visible.",
  "evidence/benchmark/ISS33/assets/domain-shape.svg",
  [("HYB-DOMAIN-1","Domain directions","Count regions before labels."),
   ("HYB-DOMAIN-2","Lone-pair occupancy","See a domain with no atom."),
   ("HYB-DOMAIN-3","Atom-only shape","Separate all regions from bonded-atom positions.")],
  [{"element":"domain direction","symbol":"region","in_words":"one local direction of electron density"},
   {"element":"paired dots","symbol":"LP","in_words":"lone-pair occupancy without a bonded atom"}]),
 representation(REP_SP2,
  "Build a generic three-direction sigma frame and add a perpendicular p direction for side-on overlap without reusing orbitals.",
  "evidence/benchmark/ISS33/assets/sigma-pi-sp2.svg",
  [("HYB-SP2-1","Sigma-direction frame","Place three directions in one plane."),
   ("HYB-SP2-2","Perpendicular p direction","Add the remaining p direction."),
   ("HYB-SP2-3","Side-on overlap","Relate parallel p directions to pi overlap."),
   ("HYB-SP2-4","Inventory check","Check that domain and bond-component ledgers are not merged.")],
  [{"element":"three coplanar lines","symbol":"sigma directions","in_words":"local sigma-framework directions"},
   {"element":"paired vertical lobes","symbol":"p","in_words":"a direction perpendicular to the molecular plane"},
   {"element":"dashed side overlap","symbol":"pi overlap","in_words":"side-on overlap of parallel p orbitals"}]),
 representation(REP_LINEAR,
  "Coordinate a two-direction linear sigma axis with two independent p directions.",
  "evidence/benchmark/ISS33/assets/sigma-pi-linear.svg",
  [("HYB-LINEAR-1","Linear sigma axis","Hold two opposite domain directions."),
   ("HYB-LINEAR-2","First p direction","Add one p direction perpendicular to the axis."),
   ("HYB-LINEAR-3","Second p direction","Add a second independent p direction."),
   ("HYB-LINEAR-4","Separate ledgers","Keep domain count distinct from sigma/pi decomposition.")],
  [{"element":"horizontal axis","symbol":"sigma axis","in_words":"two opposite local directions"},
   {"element":"two p sets","symbol":"pA,pB","in_words":"two independent directions perpendicular to the axis"}])
]

families=[
 {**base(FAM_DOMAIN),"title":"Domain count before hybrid label","capability_refs":[CAP_DOMAIN],
  "solution_structure":["Read the Lewis/local description.","Count domain directions including lone pairs.","Map the bounded introductory model and state its limits."],
  "demand_dimensions":{"model_choice":"Choose from total domains rather than sigma count.","representation_translation":"Translate Lewis regions into local directions.","reasoning_steps":"count → map → bound","novelty":"sigma-count distractors"},
  "safe_variations":["Change bonded atom identities while preserving local domain count."],
  "transfer_boundaries":["Do not infer bond polarity, length or strength from the hybrid label alone."],
  "common_wrong_routes":["Equate number of sigma bonds with number of electron domains."],
  "item_refs":[BANK_IDS[x] for x in ("Q1","Q5","Q6")]},
 {**base(FAM_ORBITAL),"title":"Sigma/pi orbital allocation","capability_refs":[CAP_ORBITAL],
  "solution_structure":["Count local domain directions.","Build the sigma-framework orbital set.","Allocate remaining p orbital(s) to pi overlap and close the orbital inventory."],
  "demand_dimensions":{"model_choice":"Choose the local introductory orbital set.","representation_translation":"Lewis/domain description to sigma/p-orbital geometry.","reasoning_steps":"domains → sigma set → p set → check","novelty":"double-counting trap"},
  "safe_variations":["Use three-domain or two-domain centres while preserving the allocation rule."],
  "transfer_boundaries":["This is an introductory localized valence-bond model, not a claim that shape alone measures orbital mixing."],
  "common_wrong_routes":["Count pi components as extra domain directions or reuse a hybrid orbital for a pi job."],
  "item_refs":[BANK_IDS[x] for x in ("Q2","Q3","Q4","Q7","Q9")]},
 {**base(FAM_SHAPE),"title":"Electron-domain geometry versus molecular shape","capability_refs":[CAP_SHAPE],
  "solution_structure":["Count all central domains.","Mark which positions contain bonded atoms and which contain lone pairs.","Name electron-domain geometry and atom-only molecular shape separately."],
  "demand_dimensions":{"model_choice":"Choose which geometry name the question asks for.","representation_translation":"All-domain scaffold to atom-only subset.","reasoning_steps":"count → occupancy → compare","novelty":"same domain geometry, different shapes"},
  "safe_variations":["Vary lone-pair count while keeping four total domains."],
  "transfer_boundaries":["Molecular shape omits lone-pair positions but lone pairs still affect geometry."],
  "common_wrong_routes":["Use tetrahedral electron-domain geometry as a universal atom-shape name."],
  "item_refs":[BANK_IDS[x] for x in ("Q8","Q10")]}
]

def microtopic(record_id,title,cap,badge,reason,assumptions,jump,rep_refs,fam_ref,wrong,diagnostic,repair,
               steps,exit_prompt,exit_summary,exit_reasoning,exit_check,research,cu_id,decision,bank_q,crux_qs,rep,stage_refs):
    return {**base(record_id),"title":title,"bucket_id":BUCKET,"primary_capability_ref":cap,
      "intrinsic_badge":badge,"badge_reason":reason,"entry_assumptions":assumptions,"inferential_jump":jump,
      "teaching_path":steps,"relation_refs":[],"representation_refs":rep_refs,"question_family_refs":[fam_ref],
      "misconceptions":[misconception(wrong,diagnostic,repair)],
      "exit_task":{"prompt":exit_prompt,"source_ref":SRC,
        "answer":model_answer(exit_summary,exit_reasoning,exit_check),
        "oracle":{"no_numeric_claim":"The exit task checks a qualitative chemical-model correspondence."}},
      "research_contribution":research,"prerequisite_refs":[],"lineage":[],
      "elicitation":{"predict":{"prompt":diagnostic,"defensible_answer":repair},
        "attempt":{"produces":"A labelled domain/orbital/shape correspondence.","closure":"RUBRIC",
          "rubric":[{"criterion":"Uses the requested representation without merging domain and bond-component ledgers.","evidence_of":"Preserves the chemical-model invariant."}],
          "accepted":[repair],"rejected":[wrong],
          "task":{"prompt":exit_prompt,"givens":[],"representation_ref":rep}},
        "reconstruct":{"route":[{"ask":"What is being counted: directions, orbitals, bond components, or atom positions?","why_this_ask":"The central error in this topic is merging these ledgers."},
                                 {"ask":"Which parts must remain distinct when you translate to the next representation?","why_this_ask":"This protects the invariant before a label is chosen."}],
                       "differs_from_teaching_path":"The learner starts by naming the ledger/invariant, then rebuilds the model rather than following the expert's declarative sequence."},
        "boundary_test":{"prompt":"If a lone pair replaces one bonded atom while total domains stay fixed, which geometry description can change?","answer":"The atom-only molecular shape can change while electron-domain geometry stays fixed.","confirms":"The learner distinguishes all-domain geometry from atom-only shape."}},
      "construction_units":[{"id":cu_id,"decision":decision,"step_refs":[s["id"] for s in steps],
        "representation_ref":rep,"reveal_stage_refs":stage_refs,"bank_anchor_ref":BANK_IDS[bank_q],
        "crux_question_refs":[BANK_IDS[x] for x in crux_qs],"crux_step_ref":steps[1]["id"],
        "misconception_indexes":[0],
        "independent_checks":[{"statement":"CHECK: Restate which ledger is being counted before assigning a label.","role":"CHECK"},
                              {"statement":"APPLY: Allocate each domain/orbital/atom position exactly once in a fresh example.","role":"APPLY"},
                              {"statement":"CONNECT: Explain why a sigma/pi component count need not equal an electron-domain count.","role":"CONNECT"}]}],
      "compact_anchor":{"prompt":"Count the right thing before choosing a label.","result":jump,"representation_ref":rep},
      "extensions":{"grade9v3:component_waivers":{"EQUATIONS":"This construction is a qualitative orbital/geometry correspondence; an equation card would be decorative rather than explanatory."}}}

microtopics=[
 microtopic(MIC_DOMAIN,"Domain count before hybridisation label",CAP_DOMAIN,"MEDIUM",
  "The key error is a model-selection shortcut: sigma-bond count is substituted for full electron-domain count.",
  ["Can draw simple Lewis structures.","Can count central electron domains.","Knows introductory 2/3/4-domain geometry rules."],
  "A sigma-bond count is not the local domain count when lone pairs are present; choose the introductory hybrid model only after the full domain inventory.",
  [REP_DOMAIN],FAM_DOMAIN,
  "Three sigma bonds always imply the same local hybridisation.","What changes in the central-domain count when a lone pair is present?",
  "Count every local electron-density direction, including lone pairs; a multiple bond still occupies one direction.",
  [step("DOM-T1","DECLARE","Separate sigma-bond count from total local electron-domain count.","Lone pairs occupy local electron-density regions even though they are not sigma bonds.","two distinct ledgers"),
   step("DOM-T2","TRANSFORM","Inventory bond directions and lone-pair domains before choosing the introductory hybrid label.","The introductory mapping is keyed to regions/directions, not merely the number of bonded atoms.","full local domain count"),
   step("DOM-T3","VERIFY","Check the proposed label against the electron-domain geometry and note that shape is model evidence, not direct orbital measurement.","This prevents a shape-only proof claim.","bounded model assignment")],
  "Two centres each have three sigma bonds; one also has a lone pair. What must you count before deciding whether their introductory local models match?",
  "Count total local electron domains, not sigma bonds alone.",
  ["The lone pair occupies an additional domain.","The introductory model follows the full local domain count."],
  "Recount the regions directly from the Lewis descriptions.",
  "Q1/Q5/Q6 cluster around the domain-count warrant that must precede hybrid labels.",
  "CU-HYB-DOMAIN-FIRST","Choose the local-domain ledger before the hybrid label","Q1",["Q1","Q5","Q6"],REP_DOMAIN,
  ["HYB-DOMAIN-1","HYB-DOMAIN-2","HYB-DOMAIN-3"]),
 microtopic(MIC_ORBITAL,"Sigma/pi orbital inventory without double-counting",CAP_ORBITAL,"HARD",
  "The learner must translate between Lewis domains and a 3D orbital-overlap representation while preserving two different counting systems.",
  ["Can count electron domains.","Knows introductory 2/3/4-domain geometry rules."],
  "Build the sigma-direction frame first, then allocate only the remaining unhybridised p orbital(s) to pi overlap; never count a pi component as a new sigma/domain direction.",
  [REP_SP2,REP_LINEAR],FAM_ORBITAL,
  "A pi bond is an extra electron-domain direction or can reuse a sigma hybrid orbital.","After the sigma framework is allocated, which local atomic orbitals remain unused?",
  "Give each local orbital one bonding job: hybrid directions support the sigma framework and separate unhybridised p orbitals support side-on pi overlap.",
  [step("ORB-T1","DECLARE","Keep the domain-direction ledger separate from the sigma/pi bond-component ledger.","A multiple bond is one local direction even though it contains more than one bond component.","two named ledgers"),
   step("ORB-T2","TRANSFORM","Construct the hybrid sigma framework from the local domain count, then identify the unhybridised p orbital(s) left over.","Hybridisation changes the basis used for the sigma framework while leaving specific p directions available for pi overlap.","orbital inventory"),
   step("ORB-T3","TRANSFORM","Orient remaining p orbitals for side-on overlap: perpendicular to an sp2 molecular plane, or as two independent p directions around an sp linear axis.","Pi overlap requires parallel p orbitals and is geometrically distinct from sigma overlap along the axis.","qualitative overlap model"),
   step("ORB-T4","VERIFY","Close the inventory by checking each local valence orbital has one assigned role and each multiple bond has exactly one sigma component.","This catches double-counting and domain/component conflation.","closed orbital ledger")],
  "A three-domain carbon has a sigma framework and one pi participation. Sketch the local orbital jobs without naming a molecule.",
  "Use three coplanar sigma-framework hybrid directions and one separate perpendicular p direction for pi participation.",
  ["Count local directions first.","Allocate sigma-framework orbitals once.","Reserve the remaining p orbital for side-on overlap."],
  "Tick each local orbital exactly once against a bonding job.",
  "Q2/Q3/Q4/Q7/Q9 supply repeated evidence that the hardest learner-relative bridge is orbital allocation across representations.",
  "CU-HYB-ORBITAL-INVENTORY","Translate domain count into sigma-framework and remaining-p orbital jobs","Q9",["Q3","Q4","Q9"],REP_SP2,
  ["HYB-SP2-1","HYB-SP2-2","HYB-SP2-3","HYB-SP2-4"]),
 microtopic(MIC_SHAPE,"Electron-domain geometry versus molecular shape",CAP_SHAPE,"MEDIUM",
  "The same all-domain geometry can project to different atom-only shapes when lone-pair occupancy changes.",
  ["Can count central domains.","Knows the four-domain tetrahedral rule."],
  "Electron-domain geometry names all local regions; molecular shape names bonded-atom positions, so lone pairs can change the latter without changing the former.",
  [REP_DOMAIN],FAM_SHAPE,
  "Tetrahedral electron-domain geometry means the bonded atoms must form a tetrahedron.","Which domain positions contain atoms and which contain lone pairs?",
  "Keep the tetrahedral all-domain scaffold, then derive molecular shape from only the bonded-atom positions.",
  [step("SHP-T1","DECLARE","Name electron-domain geometry and molecular shape as different projections.","One includes all regions; the other records atom positions.","two geometry meanings"),
   step("SHP-T2","TRANSFORM","Mark bond versus lone-pair occupancy on the common domain scaffold.","Changing occupancy changes which vertices are occupied by atoms.","occupied atom subset"),
   step("SHP-T3","VERIFY","Check CH4, NH3 and H2O as 0/1/2-lone-pair cases with four total domains.","A shared total domain count with different atom subsets is a direct counterexample to conflating the names.","shape distinction")],
  "Four central domains contain three bonds and one lone pair. Which geometry description still counts four positions, and what does the atom-only shape count?",
  "Electron-domain geometry retains all four positions; molecular shape follows the three bonded atoms.",
  ["Lone-pair occupancy does not remove a domain.","It does remove that position from the atom-only shape."],
  "Count total domains and bonded atoms separately.",
  "Q8/Q10 and the BF3/NH3 comparison show why geometry vocabulary must be kept explicit.",
  "CU-HYB-DOMAIN-VS-SHAPE","Project an all-domain geometry to the bonded-atom molecular shape","Q10",["Q1","Q8","Q10"],REP_DOMAIN,
  ["HYB-DOMAIN-1","HYB-DOMAIN-2","HYB-DOMAIN-3"])
]

purpose_delivery={"COMPETITION":{"section_title":"Competition transfer","support_policy":"NO_MID_TASK_BRIDGING","items":[
 {"id":"HYB-COMP-TRANSFER-1","roles":["CORE1A","CORE2"],"concept_refs":[MIC_ORBITAL],"question_refs":[BANK_IDS["Q3"],BANK_IDS["Q9"]],
  "title":"Close an orbital inventory under a changed local description",
  "prompt":"A neutral carbon centre is described by three coplanar sigma-bond directions and one perpendicular p-orbital participation. Without using a memorised molecule name, give an orbital-job inventory and state one check that would expose double-counting.",
  "source_kind":"AUTHOR_CREATED_COMPETITION_STYLE","source_ref":None,
  "source_label":"Original transfer task; not claimed as an official exam/PYQ item.",
  "response":{"type":"free_response","paper_ok":True},
  "answer":{"summary":"Three sigma-framework hybrid directions and one separate p-orbital pi job; check that each local valence orbital is allocated once.",
            "reasoning":["The three sigma directions define the local sigma framework.","The perpendicular p direction is reserved for side-on pi overlap.","A closure check prevents any orbital from being assigned twice."]}},
 {"id":"HYB-COMP-TRANSFER-2","roles":["CORE1A","CORE2"],"concept_refs":[MIC_SHAPE],"question_refs":[BANK_IDS["Q10"]],
  "title":"Hold domain geometry fixed while changing atom occupancy",
  "prompt":"A four-domain centre is changed from four bonds to two bonds plus two lone pairs without changing the total domain count. Explain which geometry description is preserved and which atom-only description must be reconsidered.",
  "source_kind":"AUTHOR_CREATED_COMPETITION_STYLE","source_ref":None,
  "source_label":"Original transfer task; not claimed as an official exam/PYQ item.",
  "response":{"type":"free_response","paper_ok":True},
  "answer":{"summary":"The four-domain electron geometry stays tetrahedral; the molecular shape must be derived from the two bonded-atom positions.",
            "reasoning":["All four electron domains remain.","Molecular shape omits lone-pair positions."]}}
]}}

package={"schema_version":"0.2.0","package_id":"EVIDENCE-LIB-CHEM-ISS33-HYB",
 "title":"Chemical bonding & hybridisation — Issue #33 candidate","version":"0.1.0","status":"CANDIDATE",
 "subject":"Chemistry","scope_summary":"Grade 11 competition-preparation candidate preserving ten owner-supplied hybridisation questions and teaching bounded localized models.",
 "curriculum_mappings":[],"resources":[resource],"buckets":[bucket],"capabilities":capabilities,"microtopics":microtopics,
 "relations":[],"representations":representations,"question_families":families,"questions":[],"teaching_routes":[],
 "practice_profiles":[],"evidence":[],"known_issues":[],"extensions":{
   "grade9v3:authoring_specimen":{"issue":33,"purpose":"COMPETITION","learner_profile_ref":"PROFILE-ISS33-HYBRIDISATION-COMPETITION",
     "qrt_evidence":"evidence/benchmark/ISS33/qrt-review.v1.json"},
   "grade9v3:purpose_delivery":purpose_delivery},"data":[]}

intake={"status":"READY","intake_digest":"issue33-owner-core-prompt-v2",
 "inputs":{"questions":[{"id":qid,"label":qid[1:],"text":STEMS[qid]} for qid in STEMS]}}
bank=owner_bank.new(intake,"issue33-hybridisation-agent-a")
qrt_by_id={row["question_id"]:row for row in QRT["items"]}

for qid,row in zip(STEMS,bank["questions"]):
    review=qrt_by_id[qid]
    row["id"]=BANK_IDS[qid]
    row["original_identifier"]=qid
    row["primary_capability_ref"]=PRIMARY_CAP[qid]
    row["family_ref"]=FAMILY[qid]
    row["conditions"]=["Use the bounded introductory localized hybrid-orbital model requested by the question; do not treat molecular shape alone as direct measurement of orbital mixing."]
    row["figure_refs"]=[FIGURE[qid]] if qid in FIGURE else []
    moves=[
      {"id":f"{BANK_IDS[qid]}-MOVE-1","kind":"DECIDE","action":review["X"],"why_valid":"The question turns on identifying the correct counting/model distinction before a label is chosen.","inputs":["supplied stem"],"output":"crux identified"},
      {"id":f"{BANK_IDS[qid]}-MOVE-2","kind":"CONNECT","action":review["Z"],"why_valid":"This is the reviewed learner-relative bridge from demonstrated knowledge to the requested representation/explanation.","inputs":["crux","learner anchor"],"output":"question-specific model"},
      {"id":f"{BANK_IDS[qid]}-MOVE-3","kind":"VERIFY","action":review["independent_check"],"why_valid":"An independent ledger/domain check tests the conclusion without merely restating it.","inputs":["question-specific model"],"output":"verified response"}
    ]
    row["answer"]={"kind":"EXACT","summary":review["verified_answer"],"reasoning_route":moves,
      "crux_move_ref":moves[1]["id"],"check":review["independent_check"],"verification_status":"CHECKED_BY_AUTHOR"}
    stages=["KEY_CONCEPT","REPRESENTATION","FIRST_MOVE"]
    kinds=["CONNECT","REPRESENT","EXECUTE"]
    row["scaffolds"]=[{"text":text,"support_kind":kinds[i],"reveals":"CONCEPT" if i==0 else "METHOD",
       "learner_stage":stages[i],"supports_move_ref":moves[min(i,1)]["id"]} for i,text in enumerate(review["hints"])]
    analysis=row.setdefault("extensions",{}).setdefault("grade9v3:analysis",{})
    analysis["learner_question_type"]="constructed_response"
    analysis["difficulty"]={**review["difficulty"],"basis":f"{review['X']} Five-component score {review['difficulty']['score']} resolves to {review['difficulty']['band']}."}
    analysis["common_wrong_route"]=review["misconception"]["M1"]
    analysis["expected_time_seconds"]=120 if review["difficulty"]["band"]=="D1" else 240
    analysis["cognitive_demand"]=review["demand"]
    analysis["stable_crux_move"]=review["Z"]
    row["extensions"]["grade9v3:math_spans"]=[]
    if qid not in FIGURE:
        row["extensions"]["grade9v3:component_waivers"]={"REPRESENTATION":review["representation"]["reason"]}
    row.pop("hints",None); row.pop("hint_ladder",None)

manifest={"schema":"product-manifest/v1","product_id":"EVIDENCE-CHEM-ISS33-HYB-A",
 "subject":"Chemistry","purpose":"COMPETITION","home_href":"../../../index.html",
 "question_bank_href":"../../../question-bank/index.html",
 "package_refs":["evidence/benchmark/ISS33/generated/package.v1.json"],
 "bank_refs":["evidence/benchmark/ISS33/generated/owner.bank.json"],
 "output_roles":["CORE1A","CORE2"],
 "selection":{"microtopics":[MIC_DOMAIN,MIC_ORBITAL,MIC_SHAPE],
              "core2":[BANK_IDS[f"Q{i}"] for i in range(1,11)],"core2a":[],"core2b":[]}}

OUT.mkdir(parents=True,exist_ok=True)
(OUT/"package.v1.json").write_text(json.dumps(package,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(OUT/"owner.bank.json").write_text(json.dumps(bank,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
(OUT/"product.manifest.json").write_text(json.dumps(manifest,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(f"wrote {OUT}")
