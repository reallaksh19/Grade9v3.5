#!/usr/bin/env python3
"""Build Issue #37 Agent-A round-1 candidate inputs for the sole Core renderer.

The owner questions are preserved verbatim and retain OWNER_SUPPLIED benchmark custody.
Teaching records are CANDIDATE agent-authored records. Generated learner HTML is never
hand-edited; Shared/tools/render_core.py is the sole renderer.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path

from Shared.tools import owner_bank

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"

STEMS = {
    "Q1": "In formamide, H–C(=O)–NH2, a local Lewis count gives nitrogen three sigma bonds and a lone pair. You are also given that the approximately planar amide arrangement permits nitrogen-lone-pair donation into the adjacent carbonyl pi system, which requires a suitably aligned p-like orbital. Choose a model that accounts for both the sigma framework and delocalisation. Resolve the apparent conflict with an automatic 'four domains therefore sp3' label and state the limits of your chosen hybridisation description.",
    "Q2": "For the formamide situation supplied in Q1, construct one qualitative representation connecting the Lewis lone pair on nitrogen, the nitrogen orbital used for donation and the carbonyl pi system. Then construct the corresponding approximately 90-degree-twisted arrangement about the C–N bond. Preserve atom connectivity and distinguish changes in orbital alignment from changes in formal electron count. Do not claim these sketches alone measure the donation strength.",
    "Q3": "The benchmark supplies a qualitative model result: with atom connectivity fixed, twisting a planar amide arrangement toward 90 degrees reduces the nitrogen-to-carbonyl orbital alignment and the delocalisation contribution. Explain that result through orbital overlap. Assess whether 'the hybridisation label changes, so donation disappears' is a sufficient explanation, and identify which parts of your account are model assumptions rather than measured facts.",
    "Q4": "Compare two nitrogen sites: A is the amide nitrogen in H–C(=O)–NH2; B is the amine nitrogen in H–C(=O)–CH2–NH2. In the simplified introductory model, the intervening saturated CH2 group has no continuous aligned p-orbital pathway. Develop a decision procedure combining local sigma/lone-pair counting, adjacency, orbital alignment and the model's validity conditions. Apply it to A and B, then state a counterfactual structural change that would require you to reassess your procedure. Do not equate spatial proximity with conjugation.",
    "Q5": "A student claims: 'Hybridisation uniquely determines bond angles and any deviation proves the hybridisation label wrong.' The benchmark supplies approximate observations: CH4 tetrahedral about 109.5 degrees; NH3 pyramidal about 107 degrees; H2O bent about 104.5 degrees; all three commonly use an introductory sp3 description at the central atom. It also supplies approximately planar amide nitrogen with lone-pair delocalisation. Construct and test a qualified replacement claim using these observations, local domain counting, lone-pair effects and the amide boundary case. State what further evidence would be needed before treating a qualitative orbital picture as a unique physical account.",
    "Q6": "Consider the two nitrogen sites A and B in Q4. State the conditions under which the local four-domain counting rule is a useful introductory classification, and the evidence that would make its automatic use inadequate. Distinguish recalling a rule from deciding whether its conditions hold.",
    "Q7": "A neutral methyl radical, CH3·, is supplied as approximately planar, with the unpaired electron in a p-like orbital perpendicular to the three C–H sigma directions. Translate that supplied model into an orbital sketch and assess whether 'three sigma bonds always leave an empty p orbital' follows. Keep the given model distinct from a universal claim.",
    "Q8": "Two qualitative descriptions of formamide are proposed: a completely localised pyramidal nitrogen lone pair, and an approximately planar nitrogen arrangement with possible lone-pair donation into the carbonyl pi system. Propose observations that could discriminate between them, explain the warranted inferences, and identify at least one inference that geometry alone cannot establish.",
    "Q9": "The benchmark supplies a simplified torsional model in which the relevant p-orbital overlap factor varies as cos(theta), where theta is the angle between their alignment directions. Compare theta = 0, 60 and 90 degrees, then assess the claim that the molecule's total energy must therefore vary as cos(theta). Separate execution of the given model from a justified claim about the physical system.",
    "Q10": "A proposed teaching rule says, 'Count sigma bonds and lone pairs, assign a hybridisation label, and the label explains every shape and reactivity difference.' Audit this rule against NH3, allene, formamide and the separated amine site H–C(=O)–CH2–NH2. Produce a qualified decision framework, identify where local counting is useful, and state what evidence or model is needed beyond it."
}
EXPECTED_HASHES = {
    "Q1": "d44703bfca8465f1d0144848011fc482da2f051713ebd198f9ceeddcbc8c4a64",
    "Q2": "e77d068ee216f7ce6c6df8fd652b3bfb50acc34be6cf3ebf753aaf4714e6ffdf",
    "Q3": "2ea9cdfb2b9e677a9d002da309d5d5b5bf609116ba8769085d39046b9830957c",
    "Q4": "a5bd1762999003bff70b76b12d5f49f846d627ef8f1c2fd9a16e5fdeb4f7bc52",
    "Q5": "7fa193cc29562ab720488b660310f07f11d3639ebe7970a967d0b56b063e46f8",
    "Q6": "07e8eeccb58cc7be624d67404fff3a1e4eb1d94528f0bad6f34bd6e09f4641ab",
    "Q7": "c695e46f711c83181466ec9d16ed4c02218a3622f31d825ec44fed2cf2e99f1f",
    "Q8": "706e95213624157e3574a604f282e592cdef37d9c006c6c4a3874aad31959949",
    "Q9": "7ef3b550ea1f2fbcb45cde77a92ed08db1dfbd1d8c631676914cca9190c9a52f",
    "Q10": "dfef0e64ec86b772252e01b766d2c1c19c91c72393833c9f5448bb551dc4149b"
}
for qid, text in STEMS.items():
    actual = hashlib.sha256(text.encode("utf-8")).hexdigest()
    if actual != EXPECTED_HASHES[qid]:
        raise SystemExit(f"verbatim intake hash drift for {qid}: {actual}")

SRC = "SRC-ISS37-OWNER-BENCHMARK"
BUCKET = "BUCKET-CHEM-HYBRID-MODEL-BOUNDARIES"
CAP = "CAP-CHEM-MODEL-SCOPE-ALIGNMENT"
MIC = "MIC-CHEM-HYBRID-MODEL-SCOPE"
REL = "REL-CHEM-ISS37-MODEL-SCOPE"
REP = "REP-CHEM-ISS37-TORSION-OVERLAP"
FAM = "FAM-CHEM-ISS37-MODEL-BOUNDARY"
BANK_IDS = {f"Q{i}": f"ISS37-D4-R1-Q{i:02d}" for i in range(1, 11)}


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

resource = {
    **base(SRC, source=False),
    "title": "Issue #37 coordinator-drafted owner-supplied hybridisation benchmark",
    "origin": "AUTHORED",
    "locator": "https://github.com/reallaksh19/Grade9v3.5/issues/37",
    "edition": "Independent agent A, paired benchmark v2, round 1",
    "section": "Core prompt — A/B/C",
    "last_checked": "2026-10-04",
    "access_status": "FULL_ITEM_INSPECTED",
    "rights_status": "OWNER_SUPPLIED custody; coordinating-agent authored benchmark; not official exam/PYQ and not personally authored by the owner.",
    "snapshot_ref": "e01c6365acfd6aec84c0a6e94f11b683bd961f6e",
    "snapshot_digest": "sha256:52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7",
    "role": ["QUESTION_BANK", "AUTHOR_CREATED"],
    "supports_claims": [],
    "entry_capabilities": [],
    "depth": ["COMPETITION"],
    "selection_reason": "Exact custody surface for the ten questions in Issue #37 agent-A round-1 benchmark.",
    "fallback": [],
}

bucket = {
    **base(BUCKET),
    "title": "Hybridisation as a bounded orbital model",
    "topic": "Chemical bonding and hybridisation",
    "intrinsic_badge": "HARD",
    "badge_reason": "The hard move is not recalling sp/sp2/sp3 labels; it is deciding when local counting is adequate and what orbital/model evidence warrants beyond it.",
    "depth_overlay": "COMPETITION",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP,
}

capabilities = [{
    **base(CAP),
    "action": "Use local hybridisation language conditionally, test orbital alignment/connectivity, and keep qualitative model variables separate from stronger physical claims",
    "success_criterion": "The learner can execute the supplied model, identify its warranted inference, reject a causal/quantitative overclaim, and state what additional evidence/model would be needed.",
    "prerequisite_refs": [],
    "curriculum_mappings": [],
    "external_provider": None,
    "acceptance_status": "CANDIDATE",
}]

relations = [{
    **base(REL),
    "expression": "supplied overlap factor = cos(theta); model scope does not automatically extend to total molecular energy",
    "meaning": "A mathematical relation is evidence only about the quantity it defines. At 0°, 60° and 90° the supplied overlap-factor values are 1, 1/2 and 0; a total-energy law requires an additional energetic model or evidence.",
    "symbols": [
        {"symbol": "theta", "meaning": "angle between the supplied orbital-alignment directions", "unit_or_domain": "degrees in the benchmark model"},
        {"symbol": "cos(theta)", "meaning": "the supplied qualitative overlap factor", "unit_or_domain": "dimensionless"}
    ],
    "conditions": [
        "Use the relation only for the overlap factor named in Q9.",
        "Keep atom connectivity and formal electron count distinct from orbital orientation in the torsion comparison.",
        "Do not infer donation magnitude or total molecular energy without an additional specified relation/model."
    ],
    "derivation": [
        step("ISS37-M1", "DECLARE", "Name the exact quantity the supplied formula describes.", "This prevents a functional form from being transferred to a different physical quantity.", "defined model variable"),
        step("ISS37-M2", "TRANSFORM", "Evaluate the supplied relation only for the requested angles.", "This executes the model without adding assumptions.", "1, 1/2, 0 for the overlap factor"),
        step("ISS37-M3", "VERIFY", "Ask whether any independent energy-vs-overlap relation was supplied.", "Without that bridge, the total-energy functional form is underdetermined.", "bounded inference")
    ],
    "limits": [
        "The cosine rule is a benchmark-supplied simplified overlap model, not a measured complete electronic-structure Hamiltonian.",
        "Hybridisation labels are descriptive model vocabulary and do not by themselves cause delocalisation or geometry."
    ],
    "checks": ["For every conclusion, point to the prompt-given relation, an authored model assumption, or an external evidence source."],
    "gate_relation_ref": REL,
}]

representations = [{
    **base(REP, source=False),
    "kind": "GEOMETRIC_CONSTRUCTION",
    "purpose": "Hold formamide connectivity and formal electron count fixed while revealing how orbital directions change with C-N torsion, then attach the supplied cosine relation only to the overlap-factor claim.",
    "required_elements": ["same formamide connectivity", "planar aligned orbital directions", "approximately 90-degree orthogonal directions", "explicit model-scope warning"],
    "relation_refs": [REL],
    "read_order": ["Same connectivity", "Compare orbital directions", "Attach the cosine relation to overlap factor only"],
    "instance_constraints": ["The first stage must not reveal the Q9 protected conclusion.", "No visual element may imply measured donation strength or a total-energy curve."],
    "accessibility": ["SVG has title, description and text equivalents for orientation changes.", "No meaning is encoded by colour alone."],
    "misleading_alternatives": ["Changing Lewis electron count when twisting the C-N bond.", "Drawing a total-energy cosine curve as if it were supplied evidence."],
    "rendered_asset_refs": ["evidence/benchmark/ISS37/assets/torsion-overlap.svg"],
    "scene_instances": [],
    "correspondence": [
        {"element": "vertical donor and carbonyl p directions", "symbol": "aligned p directions", "in_words": "qualitative alignment in the planar reference"},
        {"element": "vertical versus horizontal directions", "symbol": "approximately 90-degree twist", "in_words": "qualitative orthogonality after torsion"}
    ],
    "reveal_stages": [
        {"id": "ISS37-ALIGN-1", "label": "Same connectivity", "purpose": "Freeze connectivity and formal electron count before discussing orbitals.", "visible_elements": ["same connectivity", "formal count unchanged"]},
        {"id": "ISS37-ALIGN-2", "label": "Orbital directions", "purpose": "Compare aligned and orthogonal donor/acceptor directions without quantifying donation.", "visible_elements": ["donor p-like direction", "carbonyl p direction", "orthogonal twisted directions"]},
        {"id": "ISS37-ALIGN-3", "label": "Model boundary", "purpose": "Attach cos(theta) to the supplied overlap factor and block an unsupported total-energy inference.", "visible_elements": ["overlap factor scope", "energy-law warning"]}
    ]
}]

families = [{
    **base(FAM),
    "title": "Local counting, orbital alignment and model-scope decisions",
    "capability_refs": [CAP],
    "solution_structure": ["Inventory local sigma/lone-pair/SOMO information.", "Check adjacency and a continuous compatible orbital pathway.", "Execute only the supplied model relation.", "State the inference boundary and evidence needed for stronger claims."],
    "demand_dimensions": {
        "model_choice": "Choose whether local counting is sufficient or whether an orbital-alignment/model-boundary analysis is required.",
        "representation_translation": "Translate connectivity and torsion into orbital alignment without altering formal electron count.",
        "reasoning_steps": "Classify assumptions, execute model, critique overclaim, transfer framework.",
        "novelty": "Amide, radical, allene and evidence/model-boundary cases beyond routine label recall."
    },
    "safe_variations": ["Change the angle or separate-site connectivity while preserving an explicit statement of what model relation is supplied."],
    "transfer_boundaries": ["Do not infer conjugation from spatial proximity alone.", "Do not infer a whole-system energy law from an overlap-factor formula alone."],
    "common_wrong_routes": ["Count domains and stop.", "Treat a hybridisation label as a cause.", "Promote a qualitative sketch into a measurement."],
    "item_refs": [BANK_IDS[f"Q{i}"] for i in range(1, 11)],
}]

microtopics = [{
    **base(MIC),
    "title": "When a hybridisation label stops being the answer",
    "bucket_id": BUCKET,
    "primary_capability_ref": CAP,
    "intrinsic_badge": "HARD",
    "badge_reason": "The learner already knows labels; the new work is evaluating applicability, orbital alignment and evidence scope.",
    "entry_assumptions": ["Can recall simple sp/sp2/sp3 labels.", "Can distinguish sigma and pi overlap.", "Knows electron-domain versus molecular geometry.", "Knows introductory resonance contributors."],
    "inferential_jump": "A local count can be a useful first model without being a complete physical explanation: structural connectivity and orbital alignment decide whether a delocalisation-sensitive model is needed, and a formula only warrants claims about the quantity it actually defines.",
    "teaching_path": [
        step("ISS37-T1", "DECIDE", "Separate three questions: what is counted locally, what orbitals can align, and what quantity the model actually predicts.", "Each question has a different evidence base; merging them creates the benchmark's main misconceptions.", "three-layer model check"),
        step("ISS37-T2", "REPRESENT", "Hold formamide connectivity/electron count fixed while changing only C-N torsional alignment.", "This isolates orbital orientation from Lewis bookkeeping.", "aligned versus twisted representation"),
        step("ISS37-T3", "VERIFY", "For the supplied cos(theta) factor, compute only the named overlap quantity before evaluating any total-energy claim.", "A defined functional form cannot be silently transferred to another system quantity.", "warranted-inference boundary")
    ],
    "relation_refs": [REL],
    "representation_refs": [REP],
    "question_family_refs": [FAM],
    "misconceptions": [{
        "wrong_idea": "Once a hybridisation label or simple formula is known, the label/formula explains every geometry, delocalisation and energy change.",
        "diagnostic_prompt": "Which exact quantity is supplied by the model, and which extra physical claim are you trying to make?",
        "repair": "Keep local counting, orbital alignment and whole-system claims on separate evidence tracks; connect them only when a relation or independent evidence warrants the bridge."
    }],
    "exit_task": {
        "prompt": "A model says an orbital-overlap factor is 0.5 at one geometry. A classmate concludes that the molecule's total electronic energy is therefore half its reference value. What is warranted, what is not, and what extra information would be needed?",
        "source_ref": SRC,
        "answer": model_answer("Only the overlap-factor statement is warranted from the supplied relation; the total-energy ratio is not determined.", ["Name the quantity actually defined by the model.", "Check whether any relation from overlap factor to total energy was supplied.", "Request a specified energetic model or independent calculation/measurement before making the energy claim."], "The conclusion should remain valid even if another energy contribution changes while the same overlap factor is held fixed."),
        "oracle": {"no_numeric_energy_claim": "No total-energy number follows from the overlap factor alone."}
    },
    "research_contribution": "Issue #37 clusters amide, radical and teaching-rule questions around one transferable skill: use orbital models conditionally and police the boundary between a model variable and a stronger physical claim.",
    "prerequisite_refs": [],
    "lineage": [],
    "elicitation": {
        "predict": {"prompt": "At theta = 0°, 60° and 90°, what values does the supplied cos(theta) overlap-factor model give? Before revealing anything else, decide whether those three values also determine total molecular energy.", "defensible_answer": "The overlap-factor values can be calculated; the total-energy claim needs a separate relation."},
        "attempt": {"produces": "Three overlap-factor predictions plus a written yes/no judgement on the total-energy claim and one sentence naming missing evidence.", "closure": "RUBRIC", "rubric": [{"criterion": "Keeps cos(theta) attached to the overlap factor.", "evidence_of": "Executes the given model without transferring its functional form to total energy."}, {"criterion": "Names missing bridge evidence/model.", "evidence_of": "Understands model scope rather than merely rejecting the claim."}], "accepted": ["1, 1/2, 0 for overlap; total-energy law underdetermined without another model."], "rejected": ["Energy must be 1, 1/2, 0 because overlap is."], "task": {"prompt": "Compute overlap-factor values, then audit the energy claim.", "givens": ["overlap factor = cos(theta)", "theta = 0°, 60°, 90°"], "representation_ref": REP}},
        "reconstruct": {"route": [{"ask": "What noun immediately follows the supplied formula in the question?", "why_this_ask": "It binds the formula to the overlap factor."}, {"ask": "Where is an energy-vs-overlap equation supplied?", "why_this_ask": "Its absence exposes the unsupported bridge."}, {"ask": "Could another energy contribution vary while theta stays fixed?", "why_this_ask": "It tests whether total energy is underdetermined by overlap alone."}], "differs_from_teaching_path": "The learner reconstructs the evidence boundary from the claim itself rather than memorising a warning."},
        "boundary_test": {"prompt": "If a later problem explicitly supplies E(theta)=E0+A cos²(theta), may you then calculate its energy-angle dependence?", "answer": "Yes, within that supplied energetic model and its stated conditions; that still does not make the Q9 total-energy law cos(theta).", "confirms": "Model scope depends on the defined quantity and relation, not on a ban against mathematical models."}
    },
    "construction_units": [{
        "id": "CU-ISS37-MODEL-SCOPE",
        "decision": "Execute a supplied orbital model while preventing an unsupported transfer from overlap to total energy",
        "step_refs": ["ISS37-T1", "ISS37-T2", "ISS37-T3"],
        "representation_ref": REP,
        "reveal_stage_refs": ["ISS37-ALIGN-1", "ISS37-ALIGN-2", "ISS37-ALIGN-3"],
        "bank_anchor_ref": BANK_IDS["Q9"],
        "crux_question_refs": [BANK_IDS[x] for x in ("Q3", "Q5", "Q8", "Q9", "Q10")],
        "crux_step_ref": "ISS37-T3",
        "misconception_indexes": [0],
        "independent_checks": [
            {"statement": "CHECK: At 60°, compute only the supplied overlap factor.", "role": "CHECK"},
            {"statement": "APPLY: Explain why unchanged formal electron count does not imply unchanged orbital alignment after torsion.", "role": "APPLY"},
            {"statement": "CONNECT: Use the same model-scope test when judging whether geometry alone proves resonance magnitude.", "role": "CONNECT"}
        ]
    }],
    "compact_anchor": {"prompt": "What does the model actually define?", "result": "Execute that relation, then stop unless a second relation/evidence warrants the stronger claim.", "representation_ref": REP}
}]

package = {
    "schema_version": "0.2.0",
    "package_id": "EVIDENCE-LIB-CHEM-ISS37-HYBRID",
    "title": "Hybridisation model boundaries — Issue #37 candidate",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Chemistry",
    "scope_summary": "Grade 11 competition-preparation benchmark on hybridisation, amide/radical extensions, orbital alignment and model-scope reasoning. Owner questions are preserved verbatim; teaching records are independent CANDIDATE authoring.",
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
    "extensions": {"grade9v3:authoring_specimen": {"issue": 37, "agent": "A", "round": 1, "purpose": "COMPETITION", "learner_profile_ref": "SIMULATED-OWNER-PRESET-ISS37", "qrt_evidence": "evidence/benchmark/ISS37/question-ledger.json", "custody_discrepancy": "Owner benchmark requires exact questions in Core2 although generic Core2 role normally expects teacher-original/approved source custody; preserve rather than relabel."}},
    "data": [],
}

ANSWERS = {
    "Q1": "Use an approximately sp2/trigonal-planar sigma-framework description for amide N with a p-like lone-pair donor orbital aligned to the carbonyl pi system. The four-domain sp3 shortcut is not sufficient here. Treat sp2 as a compact model description, not the cause of delocalisation or a unique measured decomposition.",
    "Q2": "Keep atom connectivity and formal Lewis count unchanged. In the planar qualitative model the N donor p-like orbital can align with the carbonyl p system; after an approximately 90-degree C-N twist the relevant directions are orthogonal/poorly aligned. The sketches do not measure donation strength.",
    "Q3": "Within the supplied qualitative model, twisting reduces compatible N-to-carbonyl orbital overlap, so the delocalisation contribution associated with that interaction falls. A change of hybridisation label is not a sufficient causal explanation. Exact donation and energetics require a specified model or measurement.",
    "Q4": "Use a sequence: local sigma/lone-pair inventory -> adjacency to a pi acceptor -> continuous compatible orbital pathway -> alignment -> model-validity check. A passes under the supplied amide model; B fails because saturated CH2 interrupts the introductory p pathway. An unsaturated or otherwise orbital-connected bridge would require reassessment.",
    "Q5": "Replace the claim with: hybridisation/domain labels are useful first-order local models, but exact bond angles also depend on electron-pair occupancy and the molecular/electronic environment. CH4, NH3 and H2O can share an introductory four-domain/sp3-type description while having different shapes/angles; amide N adds a delocalisation-sensitive boundary. Geometry alone does not uniquely prove an orbital decomposition.",
    "Q6": "Four-domain counting is useful for a first local classification when bonding is sufficiently localised and no supplied evidence demands a conjugation-sensitive model. Automatic use is inadequate when aligned donor/acceptor orbitals, resonance-sensitive planarity, radical/SOMO character or structural changes affect the model. Recalling the rule is separate from testing its applicability.",
    "Q7": "Represent three coplanar C-H sigma directions plus the supplied singly occupied p-like orbital perpendicular to that plane. 'Three sigma bonds always leave an empty p orbital' does not follow: the orbital in this radical model is singly occupied, and one supplied case cannot establish a universal rule.",
    "Q8": "Discriminating evidence could include nitrogen planarity/pyramidality, C-N structural or rotational behaviour, spectroscopy, and a defined electronic-structure calculation. Planarity is consistent with a delocalised amide model but geometry alone cannot quantify donation or uniquely establish one orbital/electronic partition.",
    "Q9": "For the supplied overlap factor: cos(0°)=1, cos(60°)=1/2, cos(90°)=0. The claim that total molecular energy must therefore vary as cos(theta) is not warranted: total energy contains other contributions, and a relation from overlap factor to energy would need to be supplied or established independently.",
    "Q10": "Use local counting as the first stage, then test connectivity/adjacency, compatible p/SOMO/donor-acceptor pathways and model sufficiency before using a hybridisation label at the warranted descriptive level. NH3 exposes lone-pair geometry effects, allene requires orthogonal p systems, formamide is delocalisation-sensitive, and the separated amine lacks the supplied continuous p pathway. Stronger shape/reactivity claims need an appropriate orbital/electronic model and evidence."
}

HINTS = {
    "Q1": ["Separate the local Lewis count from the extra orbital-alignment information explicitly supplied in the stem.", "Ask what orbital must remain available if the lone pair is to align with the carbonyl pi system.", "State what your chosen label describes, then name at least one thing it does not uniquely establish."],
    "Q2": ["Freeze atom connectivity and the formal Lewis electron count before you rotate anything.", "Use two separate marks: one for the nitrogen donor-orbital direction and one for the carbonyl p direction.", "Your second sketch should change orientation, not invent a new electron count or a numerical donation scale."],
    "Q3": ["The stem already tells you what changes during twisting: orbital alignment. Start there rather than with a label.", "Distinguish a descriptive label from the geometric feature that directly controls side-on p-orbital overlap in the supplied model.", "Sort each sentence you plan to write as prompt-given result, model inference, or measured fact."],
    "Q4": ["Build a checklist that can fail at more than one point; do not jump from 'lone pair exists' to 'conjugated'.", "For each site, trace whether there is an adjacent, continuous orbital pathway in the simplified model.", "Make your counterfactual change the pathway or model assumptions, not merely move atoms closer in space."],
    "Q5": ["Test the word 'uniquely' against the three supplied bond angles before discussing amide nitrogen.", "Keep electron-domain classification distinct from molecular geometry and exact angle.", "For the final sentence, ask what observation or calculation would be needed to choose among competing electronic descriptions."],
    "Q6": ["Write the counting rule first, then add a separate 'when may I stop here?' test.", "Use Site A and Site B to identify evidence that localised counting misses.", "Your answer should distinguish remembering a classification rule from checking whether its assumptions hold."],
    "Q7": ["Translate the supplied model literally: three sigma directions plus one p-like orbital.", "Check the occupancy word in the stem before calling that orbital empty, filled or singly occupied.", "Decide whether one supplied radical model logically proves a statement about every three-coordinate centre."],
    "Q8": ["Choose observations for which the two proposed descriptions would make different qualitative expectations.", "Separate 'consistent with' from 'uniquely proves'.", "Include at least one evidence type that probes more than geometry alone."],
    "Q9": ["Before calculating, write the name of the quantity whose formula is actually supplied.", "Evaluate the three requested cosine values without adding any new physical relation.", "Then inspect the energy claim separately: identify what extra equation or evidence would be required to connect the two quantities."],
    "Q10": ["Turn the one-line teaching rule into a sequence of decisions rather than replacing it with another slogan.", "Use each named case to expose a different checkpoint: lone-pair geometry, orthogonal p systems, delocalisation, or broken orbital pathway.", "End by specifying when evidence/model escalation is required beyond a local label."]
}

CHECKS = {
    "Q1": "If your explanation still works after replacing the word 'sp2' with 'planar sigma framework plus aligned p-like lone pair', the causal reasoning is not being outsourced to the label.",
    "Q2": "Count atoms and formal electrons in both sketches; they must match while orbital directions differ.",
    "Q3": "Remove the hybridisation word from your explanation. If the overlap-based explanation survives, you have identified the actual model mechanism.",
    "Q4": "Run the same checklist on a counterfactual unsaturated bridge and confirm that the outcome can change for a structural reason.",
    "Q5": "Your replacement claim must accommodate 109.5°, 107° and 104.5° without calling the common introductory four-domain model meaningless.",
    "Q6": "For each site, state both the recalled local count and the separate evidence-based applicability decision.",
    "Q7": "Label the p-like orbital with one electron; if it is drawn empty, the supplied radical model has been mistranslated.",
    "Q8": "For every proposed observation, write one inference it supports and one stronger inference it does not establish alone.",
    "Q9": "Imagine another energy contribution changes while theta stays fixed. The supplied overlap factor is unchanged, showing why total energy is not fixed by that factor alone.",
    "Q10": "The framework must classify all four named cases without using 'hybridisation explains it' as the final reason."
}

DIFFICULTY = {"Q1":"D4","Q2":"D4","Q3":"D4","Q4":"D4","Q5":"D4","Q6":"D3","Q7":"D3","Q8":"D4","Q9":"D4","Q10":"D4"}
DEMAND = {
    "Q1": ("justify", "critique"), "Q2": ("interpret", "transfer"), "Q3": ("critique", "justify"),
    "Q4": ("transfer", "justify"), "Q5": ("critique", "justify"), "Q6": ("critique", "classify"),
    "Q7": ("interpret", "critique"), "Q8": ("justify", "critique"), "Q9": ("critique", "interpret"),
    "Q10": ("transfer", "critique")
}

intake = {"status": "READY", "intake_digest": "sha256:52306a397ecc6f327a8aba16b73479547c9e78d75139bdf14839c00038eedde7", "inputs": {"questions": [{"id": qid, "label": qid[1:], "text": STEMS[qid]} for qid in STEMS]}}
bank = owner_bank.new(intake, "iss37-d4-agent-a-r1")

for qid, row in zip(STEMS, bank["questions"]):
    row["id"] = BANK_IDS[qid]
    row["original_identifier"] = qid
    row["primary_capability_ref"] = CAP
    row["family_ref"] = FAM
    row["conditions"] = []
    row["figure_refs"] = [REP] if qid in {"Q2", "Q3", "Q9"} else []
    moves = [
        {"id": f"{BANK_IDS[qid]}-MOVE-1", "kind": "DECIDE", "action": "Identify the exact model/given and the claim being tested.", "why_valid": "The benchmark is designed to separate supplied facts from model assumptions and overclaims.", "inputs": ["owner-supplied stem"], "output": "bounded target claim"},
        {"id": f"{BANK_IDS[qid]}-MOVE-2", "kind": "REPRESENT", "action": "Apply the relevant local-count/orbital-alignment/model-scope reasoning without changing unstated givens.", "why_valid": "The reasoning must preserve connectivity, occupancy and model scope stated by the question.", "inputs": ["target claim", "stated givens"], "output": ANSWERS[qid]},
        {"id": f"{BANK_IDS[qid]}-MOVE-3", "kind": "VERIFY", "action": CHECKS[qid], "why_valid": "An independent boundary check catches label-causality, occupancy and evidence-scope errors.", "inputs": ["reasoned answer"], "output": "checked model-boundary answer"}
    ]
    row["answer"] = {"kind": "EXACT", "summary": ANSWERS[qid], "reasoning_route": moves, "crux_move_ref": moves[1]["id"], "check": CHECKS[qid], "verification_status": "CHECKED_BY_AUTHOR"}
    row["scaffolds"] = [
        {"text": HINTS[qid][0], "support_kind": "CONNECT", "reveals": "CONCEPT", "learner_stage": "KEY_CONCEPT", "supports_move_ref": moves[0]["id"]},
        {"text": HINTS[qid][1], "support_kind": "REPRESENT", "reveals": "METHOD", "learner_stage": "REPRESENTATION", "supports_move_ref": moves[1]["id"]},
        {"text": HINTS[qid][2], "support_kind": "EXECUTE", "reveals": "METHOD", "learner_stage": "FIRST_MOVE", "supports_move_ref": moves[1]["id"]}
    ]
    analysis = row["extensions"].setdefault("grade9v3:analysis", {})
    analysis["learner_question_type"] = "constructed_response"
    analysis["difficulty"] = {"band": DIFFICULTY[qid], "learner_relative_reason": "Classification derived independently from the simulated preset; D6/Q7 remain D3 because the key advanced givens are supplied."}
    analysis["common_wrong_route"] = HINTS[qid][0]
    analysis["expected_time_seconds"] = 300 if DIFFICULTY[qid] == "D4" else 210
    analysis["cognitive_demand"] = {"primary": DEMAND[qid][0], "secondary": DEMAND[qid][1]}
    analysis["stable_crux_move"] = moves[1]["id"]
    analysis["custody"] = "OWNER_SUPPLIED benchmark input drafted by coordinating agent; not official exam/PYQ."
    if not row["figure_refs"]:
        row["extensions"]["grade9v3:component_waivers"] = {"REPRESENTATION": "No additional pre-attempt figure is needed for this item; the key job is verbal/model-boundary reasoning and a figure would either decorate or risk leaking the protected inference."}
    row["extensions"]["grade9v3:math_spans"] = []
    row.pop("hints", None)
    row.pop("hint_ladder", None)

manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-CHEM-ISS37-HYBRID-A-R1",
    "subject": "Chemistry",
    "home_href": "../../../index.html",
    "question_bank_href": "../../../question-bank/index.html",
    "package_refs": ["evidence/benchmark/ISS37/generated/package.v1.json"],
    "bank_refs": ["evidence/benchmark/ISS37/generated/owner.bank.json"],
    "selection": {"microtopics": [MIC], "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)], "core2a": [], "core2b": []},
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "owner.bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
