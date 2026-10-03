#!/usr/bin/env python3
"""Build the Issue #10 Surface Areas & Volumes cold-run specimen.

This is evidence for the minimal-prompt authoring workflow, not canonical publication.
The ten owner questions stay verbatim and carry OWNER_SUPPLIED_RAW_INPUT custody.
Canonical teaching records are authored CANDIDATE Mathematics records and remain
separate from the owner questions' source custody.
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
    "Q1": "A wooden cube has edge length 7 cm.\n\nFind its total surface area.",
    "Q2": "A cylindrical water bottle has diameter 14 cm and height 20 cm.\n\nFind its curved surface area.",
    "Q3": "A cylindrical bucket is open at the top.\n\nIts internal radius is 7 cm and its height is 18 cm.\n\nFind the area of metal sheet required to make the bucket, ignoring the thickness of the sheet.",
    "Q4": "A conical tent has radius 7 m and vertical height 24 m.\n\nFind:\n\n1. its slant height;\n2. the area of canvas required to make the tent.\n\nThe base of the tent is open.",
    "Q5": "A hemispherical bowl has radius 10.5 cm.\n\nFind the area of its inner surface.\n\nExplain why the circular base is not included in your calculation.",
    "Q6": "A toy is made by mounting a cone on a hemisphere.\n\nThe cone and hemisphere have the same radius, 3.5 cm.\n\nThe vertical height of the cone is 12 cm.\n\nFind the total exposed surface area of the toy.\n\nThe circular face where the cone and hemisphere join is not exposed.",
    "Q7": "A cylindrical vessel of radius 7 cm and height 25 cm is open at the top.\n\nIt is to be painted:\n\n- on its entire outer curved surface; and\n- on the outside of its circular base.\n\nThe inside is not painted.\n\nFind the area to be painted.\n\nBefore calculating, state exactly which surfaces are included.",
    "Q8": "A rectangular water tank is 2 m long, 1.5 m wide and 1.2 m deep.\n\nIt is filled to 75% of its total capacity.\n\nHow many litres of water are in the tank?\n\nShow the unit conversion clearly.",
    "Q9": "A solid metallic sphere of radius 6 cm is melted and recast into identical solid spheres of radius 2 cm.\n\nAssume that no metal is lost.\n\nHow many smaller spheres are formed?\n\nExplain why surface area is not conserved in this process.",
    "Q10": "A cone and a cylinder have the same base radius and the same height.\n\nThe volume of the cylinder is 924 cm³.\n\nFind the volume of the cone.\n\nThen explain why the radius and height do not need to be calculated separately.",
}

# Package ids.
SRC = "SRC-OWNER-ISSUE10-SAV"
BUCKET = "BUCKET-MAT-09-SAV"
CAP_SURF = "CAP-MAT-SAV-SURFACE-INVENTORY"
CAP_CONE = "CAP-MAT-SAV-CONE-BRIDGE"
CAP_VOL = "CAP-MAT-SAV-VOLUME-STRUCTURE"
MIC_SURF = "MIC-MAT-SAV-SURFACE-INVENTORY"
MIC_CONE = "MIC-MAT-SAV-CONE-BRIDGE"
MIC_VOL = "MIC-MAT-SAV-VOLUME-STRUCTURE"
REP_OPEN = "REP-MAT-SAV-OPEN-CYLINDER"
REP_CONE = "REP-MAT-SAV-CONE-SLANT"
REP_JOINT = "REP-MAT-SAV-COMPOSITE-JOINT"
REL_SURF = "REL-MAT-SAV-SURFACE-SUM"
REL_CONE = "REL-MAT-SAV-CONE-SLANT-CSA"
REL_VOL = "REL-MAT-SAV-VOLUME-STRUCTURE"
FAM_SURF = "FAM-MAT-SAV-SURFACE-AREA"
FAM_VOL = "FAM-MAT-SAV-VOLUME"

BANK_IDS = {f"Q{i}": f"OWN-ISSUE10-SAV-{i:02d}" for i in range(1, 11)}
PRIMARY_CAP = {
    "Q1": CAP_SURF, "Q2": CAP_SURF, "Q3": CAP_SURF, "Q4": CAP_CONE,
    "Q5": CAP_SURF, "Q6": CAP_CONE, "Q7": CAP_SURF, "Q8": CAP_VOL,
    "Q9": CAP_VOL, "Q10": CAP_VOL,
}
FAMILY = {f"Q{i}": (FAM_SURF if i <= 7 else FAM_VOL) for i in range(1, 11)}
FIGURE = {"Q3": REP_OPEN, "Q4": REP_CONE, "Q6": REP_JOINT}


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


def representation(record_id: str, kind: str, purpose: str, asset: str, stages: list[tuple[str, str, str]], correspondence: list[dict]) -> dict:
    return {
        **base(record_id, source=False),
        "kind": kind,
        "purpose": purpose,
        "required_elements": [s[1] for s in stages],
        "relation_refs": [REL_SURF, REL_CONE],
        "read_order": [s[2] for s in stages],
        "instance_constraints": ["Pre-attempt stages must orient without stating a final area expression or numerical answer."],
        "accessibility": ["The SVG has an accessible name, title and description.", "Text labels duplicate any line-style meaning."],
        "misleading_alternatives": ["Treating a dashed hidden/open boundary as an exposed material surface."],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [{"id": sid, "label": label, "purpose": job, "visible_elements": [label]} for sid, label, job in stages],
    }


resource = {
    **base(SRC, source=False),
    "title": "Issue #10 owner-supplied Grade 9 Surface Areas & Volumes questions",
    "origin": "AUTHORED",
    "locator": "https://github.com/reallaksh19/Grade9v3.5/issues/10",
    "edition": "Owner prompt captured 2026-10-03",
    "section": "CORE PROMPT — VERBATIM OWNER INPUT / THE 10 QUESTIONS",
    "last_checked": "2026-10-03",
    "access_status": "FULL_ITEM_INSPECTED",
    "rights_status": "Owner-supplied text; no exam, textbook, year or official-answer identity claimed.",
    "snapshot_ref": None,
    "snapshot_digest": None,
    "role": ["QUESTION_BANK", "AUTHOR_CREATED"],
    "supports_claims": [],
    "entry_capabilities": [],
    "depth": ["REVISION"],
    "selection_reason": "Exact custody surface for the ten questions used by the Issue #10 cold-run.",
    "fallback": [],
}

bucket = {
    **base(BUCKET),
    "title": "Surface Areas and Volumes",
    "topic": "Mensuration",
    "intrinsic_badge": "MEDIUM",
    "badge_reason": "The central difficulty is choosing and coordinating surfaces or volume relations, not formula recall alone.",
    "depth_overlay": "FOUNDATION",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP_OPEN,
}

capabilities = [
    {**base(CAP_SURF), "action": "Inventory present, absent, hidden and exposed surfaces before selecting area relations", "success_criterion": "State exactly which physical surfaces contribute and exclude hidden/open faces with a reason", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_CONE), "action": "Derive a needed slant length before applying cone surface area and coordinate it with exposure", "success_criterion": "Use the axial right triangle for l and then apply only the exposed cone/solid surfaces", "prerequisite_refs": [CAP_SURF], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_VOL), "action": "Use volume as capacity, conserved material quantity, or a shared symbolic factor", "success_criterion": "Choose the correct invariant/ratio, preserve cubic units, and avoid solving unnecessary dimensions", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
]

relations = [
    {**base(REL_SURF), "expression": "required area = sum of the areas of physical surfaces that are present and included", "meaning": "Surface-area modelling starts with a physical surface inventory; a missing opening or hidden interface contributes no exposed area.", "symbols": [{"symbol": "A", "meaning": "area of an included surface", "unit_or_domain": "square length units"}], "conditions": ["Count each included physical surface once.", "Do not add an open face or an internal joining face."], "derivation": [step("SAV-S1", "DECLARE", "Name every physical surface before writing a formula.", "A formula can only be chosen after the geometry has been interpreted.", "surface inventory"), step("SAV-S2", "TRANSFORM", "Map each included surface to its 2D area relation.", "A 3D surface-area result is a sum of 2D areas.", "area terms"), step("SAV-S3", "VERIFY", "Check each term against a surface that can physically be pointed to.", "This catches missing, duplicate and hidden faces.", "verified surface sum")], "limits": ["The rule does not decide whether a real container has thickness; the question's model does."], "checks": ["Point to one physical surface for every area term and one reason for every omitted candidate face."], "gate_relation_ref": "REL-MAT-SAV-SURFACE-SUM"},
    {**base(REL_CONE), "expression": "l² = r² + h²; curved cone area = πrl", "meaning": "A cone's curved surface uses slant height l, so a problem that gives only vertical height h may require a geometry step first.", "symbols": [{"symbol": "r", "meaning": "base radius", "unit_or_domain": "positive length"}, {"symbol": "h", "meaning": "vertical height", "unit_or_domain": "positive length"}, {"symbol": "l", "meaning": "slant height", "unit_or_domain": "positive length"}], "conditions": ["The cone is right circular.", "The axial radius and vertical height form a right angle."], "derivation": [step("SAV-C1", "REPRESENT", "Take an axial cross-section and locate r, h and l.", "The cross-section exposes the right triangle that governs slant height.", "right triangle"), step("SAV-C2", "TRANSFORM", "Use Pythagoras to obtain l before surface area.", "The curved-area relation requires l rather than h.", "slant height"), step("SAV-C3", "VERIFY", "Check that l is longer than both r and h before using πrl.", "The hypotenuse must be the longest side.", "plausible slant height")], "limits": ["Do not use h in place of l in πrl."], "checks": ["Substitute the derived l back into l²=r²+h²."], "gate_relation_ref": "REL-MAT-SAV-CONE-SLANT-CSA"},
    {**base(REL_VOL), "expression": "volume measures occupied capacity; no-material-loss recasting conserves volume; for equal r and h, V_cone = V_cylinder/3", "meaning": "The same volume idea supports unit conversion, conservation under recasting, and structural comparison of formula factors.", "symbols": [{"symbol": "V", "meaning": "volume", "unit_or_domain": "cubic length units"}, {"symbol": "r", "meaning": "radius", "unit_or_domain": "positive length"}, {"symbol": "h", "meaning": "height", "unit_or_domain": "positive length"}], "conditions": ["Capacity conversion preserves the same physical volume.", "Recasting conservation assumes no material is lost.", "The cone/cylinder one-third relation requires equal radius and height."], "derivation": [step("SAV-V1", "DECLARE", "Identify what volume means in the question: capacity, material amount, or a formula factor.", "Different contexts use the same quantity for different reasoning jobs.", "volume role"), step("SAV-V2", "TRANSFORM", "Preserve cubic scaling and units while applying the relevant relation.", "Volume scales with three linear dimensions and must retain cubic meaning until a valid capacity conversion.", "volume relation"), step("SAV-V3", "VERIFY", "Use a ratio or reverse conversion to check the result.", "An independent ratio exposes unit or scaling mistakes.", "verified volume result")], "limits": ["Surface area is not generally conserved when a solid is divided or recast."], "checks": ["Reverse the unit conversion or compare the relevant formula ratio."], "gate_relation_ref": "REL-MAT-SAV-VOLUME-STRUCTURE"},
]

representations = [
    representation(REP_OPEN, "GEOMETRIC_CONSTRUCTION", "Separate an open cylinder into the curved wall and existing base while keeping the top visibly absent.", "evidence/authoring/issue10-surface-areas-volumes/assets/open-cylinder.svg", [("SAV-SURF-1", "Open shape", "See the opening before any formula."), ("SAV-SURF-2", "Physical surfaces", "Name wall and base as distinct pieces."), ("SAV-SURF-3", "Inventory rule", "Connect the picture to surface-first modelling.")], [{"element": "open top", "symbol": "no area term", "in_words": "the missing top is not material"}, {"element": "curved wall", "symbol": "curved surface", "in_words": "the cylindrical side surface"}]),
    representation(REP_CONE, "GEOMETRIC_CONSTRUCTION", "Expose the axial right triangle that links radius, vertical height and slant height without revealing the numerical result.", "evidence/authoring/issue10-surface-areas-volumes/assets/cone-slant.svg", [("SAV-CONE-1", "Axial triangle", "See the geometric dependency."), ("SAV-CONE-2", "r, h and l", "Map the symbols to segments."), ("SAV-CONE-3", "Needed length", "Choose the length required by the surface formula.")], [{"element": "horizontal radius", "symbol": "r", "in_words": "base radius"}, {"element": "vertical segment", "symbol": "h", "in_words": "vertical height"}, {"element": "sloping segment", "symbol": "l", "in_words": "slant height"}]),
    representation(REP_JOINT, "GEOMETRIC_CONSTRUCTION", "Make the cone-hemisphere joining circle visible as an internal interface rather than an exposed face.", "evidence/authoring/issue10-surface-areas-volumes/assets/composite-joint.svg", [("SAV-JOINT-1", "Assembled solid", "See the whole exterior."), ("SAV-JOINT-2", "Internal joint", "Distinguish the shared circle from the outside surfaces."), ("SAV-JOINT-3", "Touch test", "Use physical reachability to decide exposure.")], [{"element": "dashed joining ellipse", "symbol": "hidden interface", "in_words": "the shared circle is internal after assembly"}]),
]

families = [
    {**base(FAM_SURF), "title": "Surface inventory and area selection", "capability_refs": [CAP_SURF, CAP_CONE], "solution_structure": ["Inventory physical/exposed surfaces.", "Derive any missing geometric length.", "Map surfaces to area relations and add once."], "demand_dimensions": {"model_choice": "Choose which surfaces and relations actually apply.", "representation_translation": "Translate a 3D object or verbal condition into 2D surface terms.", "reasoning_steps": "Inventory, bridge if needed, calculate, check.", "novelty": "Open surfaces and hidden interfaces."}, "safe_variations": ["Change dimensions while preserving the same surface condition."], "transfer_boundaries": ["Do not infer material thickness or lids that the stem does not state."], "common_wrong_routes": ["Select a memorized total-surface-area formula before inventorying surfaces."], "item_refs": [BANK_IDS[f"Q{i}"] for i in range(1, 8)]},
    {**base(FAM_VOL), "title": "Volume as capacity, invariant and structural ratio", "capability_refs": [CAP_VOL], "solution_structure": ["Identify the role of volume.", "Apply the volume relation or invariant.", "Preserve cubic scaling/units and verify by ratio."], "demand_dimensions": {"model_choice": "Choose capacity conversion, conservation, or structural formula comparison.", "representation_translation": "Translate words such as filled or recast into volume operations.", "reasoning_steps": "Model, compute/compare, verify.", "novelty": "Same quantity used in three distinct reasoning contexts."}, "safe_variations": ["Change fill fraction, scale ratio, or common cylinder volume."], "transfer_boundaries": ["No-material-loss is required for recasting conservation."], "common_wrong_routes": ["Use surface area or a linear scale where a cubic quantity is required."], "item_refs": [BANK_IDS[f"Q{i}"] for i in range(8, 11)]},
]


def misconception(wrong: str, diagnostic: str, repair: str) -> dict:
    return {"wrong_idea": wrong, "diagnostic_prompt": diagnostic, "repair": repair}


microtopics = [
    {**base(MIC_SURF), "title": "Surface inventory before formula", "bucket_id": BUCKET, "primary_capability_ref": CAP_SURF, "intrinsic_badge": "MEDIUM", "badge_reason": "Open and joined solids punish formula-first reasoning.", "entry_assumptions": ["Can find areas of circles and standard curved surfaces."], "inferential_jump": "A surface-area expression must correspond to physical material that is present and included; open or internal faces contribute no exposed area.", "teaching_path": [step("SURF-T1", "DECIDE", "List candidate surfaces before selecting a formula.", "This separates modelling from arithmetic.", "candidate surface inventory"), step("SURF-T2", "REPRESENT", "Mark each candidate present, absent, hidden or exposed.", "The physical status determines inclusion.", "classified surfaces"), step("SURF-T3", "TRANSFORM", "Map each included surface to an area relation and add it once.", "The final area is a sum of the included physical pieces.", "surface-area model")], "relation_refs": [REL_SURF], "representation_refs": [REP_OPEN, REP_JOINT], "question_family_refs": [FAM_SURF], "misconceptions": [misconception("A named solid automatically implies its textbook total-surface-area formula.", "Does the top or joining disk physically exist as exposed material in this object?", "Inventory surfaces from the object/conditions first; choose formulas second.")], "exit_task": {"prompt": "A closed cylinder is fixed to a flat circular plate of the same radius along one base. Which cylinder surfaces remain exposed? Explain before calculating.", "source_ref": SRC, "answer": model_answer("The curved wall and the opposite circular base remain exposed; the attached base is hidden.", ["The shared base is an internal contact surface.", "Every other outer cylinder surface remains reachable."], "Use a touch/paint test on each surface."), "oracle": {"no_numeric_claim": "The task checks the surface inventory decision."}}, "research_contribution": "Issue #10 question evidence clusters Q3, Q5, Q6 and Q7 around a surface-inventory-before-formula construction.", "prerequisite_refs": [], "lineage": [], "elicitation": {"predict": {"prompt": "When a container is open, should the missing opening contribute an area term?", "defensible_answer": "No; an opening is not material."}, "attempt": {"produces": "A labelled surface inventory.", "closure": "RUBRIC", "rubric": [{"criterion": "Names present/exposed surfaces before formulas.", "evidence_of": "Models geometry before arithmetic."}], "accepted": ["Curved wall + existing base; no open top."], "rejected": ["Use total surface area because the word cylinder appears."], "task": {"prompt": "For an open cylinder, list present surfaces and omitted surfaces.", "givens": ["The top is open."], "representation_ref": REP_OPEN}}, "reconstruct": {"route": [{"ask": "What physical material can you touch?", "why_this_ask": "Reachability identifies exposed surfaces."}, {"ask": "Which candidate face is missing or internal?", "why_this_ask": "This prevents extra area terms."}], "differs_from_teaching_path": "The learner starts from a physical touch test instead of a formula list."}, "boundary_test": {"prompt": "If the top is added, what changes in the inventory?", "answer": "One circular disk becomes present and exposed.", "confirms": "Open/closed status changes a surface term, not the cylinder's curved relation."}}, "construction_units": [{"id": "CU-SAV-SURFACE-INVENTORY", "decision": "Decide what physical surface exists before choosing a formula", "step_refs": ["SURF-T1", "SURF-T2", "SURF-T3"], "representation_ref": REP_OPEN, "reveal_stage_refs": ["SAV-SURF-1", "SAV-SURF-2", "SAV-SURF-3"], "bank_anchor_ref": BANK_IDS["Q3"], "crux_question_refs": [BANK_IDS[x] for x in ("Q3", "Q5", "Q7")], "crux_step_ref": "SURF-T2", "misconception_indexes": [0], "independent_checks": [{"statement": "CHECK: Name the surfaces of an open cylinder without calculating.", "role": "CHECK"}, {"statement": "APPLY: Explain why a bowl mouth is not a circular material face.", "role": "APPLY"}, {"statement": "CONNECT: Use the same inventory test when two solids are joined.", "role": "CONNECT"}]}, {"id": "CU-SAV-HIDDEN-JOINT", "decision": "Remove internal joining faces from exposed surface area", "step_refs": ["SURF-T1", "SURF-T2", "SURF-T3"], "representation_ref": REP_JOINT, "reveal_stage_refs": ["SAV-JOINT-1", "SAV-JOINT-2", "SAV-JOINT-3"], "bank_anchor_ref": BANK_IDS["Q6"], "crux_question_refs": [BANK_IDS["Q6"]], "crux_step_ref": "SURF-T2", "misconception_indexes": [0], "independent_checks": [{"statement": "CHECK: Can paint reach a shared face after assembly?", "role": "CHECK"}, {"statement": "APPLY: State whether one, two or zero copies of the joining disk belong in exposed area.", "role": "APPLY"}, {"statement": "CONNECT: Distinguish exterior area from contact area in any composite solid.", "role": "CONNECT"}]}], "compact_anchor": {"prompt": "Open or hidden face? Inventory first.", "result": "Only physical surfaces that are present and included contribute area.", "representation_ref": REP_OPEN}},
    {**base(MIC_CONE), "title": "Auxiliary length before cone area", "bucket_id": BUCKET, "primary_capability_ref": CAP_CONE, "intrinsic_badge": "MEDIUM", "badge_reason": "The surface formula needs slant height even when the stem gives vertical height.", "entry_assumptions": ["Can use Pythagoras in a right triangle."], "inferential_jump": "The given height is not automatically the length required by the surface formula; derive the needed geometric quantity first.", "teaching_path": [step("CONE-T1", "REPRESENT", "Take an axial cross-section and label r, h and l.", "It reveals the right triangle embedded in the cone.", "axial triangle"), step("CONE-T2", "TRANSFORM", "Use l²=r²+h² to derive slant height.", "The curved surface follows the sloping generator, not the vertical height.", "slant height"), step("CONE-T3", "VERIFY", "Check l as the hypotenuse, then use πrl on the curved surface only.", "A plausible l and a surface inventory prevent height/base errors.", "verified cone area route")], "relation_refs": [REL_CONE, REL_SURF], "representation_refs": [REP_CONE], "question_family_refs": [FAM_SURF], "misconceptions": [misconception("Use the vertical height directly in πrl.", "Which segment actually lies along the cone's fabric?", "Locate l as the hypotenuse of the axial right triangle and derive it before area.")], "exit_task": {"prompt": "A cone has r=5 and h=12. Without finding any surface area, identify the length the curved-area formula needs and explain how to obtain it.", "source_ref": SRC, "answer": model_answer("It needs slant height l, found from l²=5²+12².", ["The curved surface follows the sloping side.", "The axial cross-section makes l the hypotenuse."], "l must exceed both 5 and 12."), "oracle": {"no_numeric_claim": "The task assesses route selection before arithmetic."}}, "research_contribution": "Q4 and Q6 repeatedly require a geometry bridge before mensuration.", "prerequisite_refs": [CAP_SURF], "lineage": [], "elicitation": {"predict": {"prompt": "Does πrl use vertical height h?", "defensible_answer": "No; it uses slant height l."}, "attempt": {"produces": "A labelled axial triangle and a slant-height relation.", "closure": "RUBRIC", "rubric": [{"criterion": "Distinguishes h from l.", "evidence_of": "Selects the correct length for curved area."}], "accepted": ["Use Pythagoras on r, h, l first."], "rejected": ["Put h directly into πrl."], "task": {"prompt": "Label r, h and l on the cone cross-section.", "givens": ["The cone is right circular."], "representation_ref": REP_CONE}}, "reconstruct": {"route": [{"ask": "Which segment is on the surface?", "why_this_ask": "It identifies l."}, {"ask": "What right triangle contains it?", "why_this_ask": "It supplies Pythagoras."}], "differs_from_teaching_path": "Starts from the formula's required symbol and works backward to the geometry."}, "boundary_test": {"prompt": "If l is already given, is Pythagoras necessary?", "answer": "No; use the supplied l after checking the surface condition.", "confirms": "The bridge is conditional on missing slant height."}}, "construction_units": [{"id": "CU-SAV-CONE-BRIDGE", "decision": "Derive the length the surface relation needs before calculating area", "step_refs": ["CONE-T1", "CONE-T2", "CONE-T3"], "representation_ref": REP_CONE, "reveal_stage_refs": ["SAV-CONE-1", "SAV-CONE-2", "SAV-CONE-3"], "bank_anchor_ref": BANK_IDS["Q4"], "crux_question_refs": [BANK_IDS[x] for x in ("Q4", "Q6")], "crux_step_ref": "CONE-T2", "misconception_indexes": [0], "independent_checks": [{"statement": "CHECK: Which of h or l lies on the curved surface?", "role": "CHECK"}, {"statement": "APPLY: Draw the right triangle for r, h and l.", "role": "APPLY"}, {"statement": "CONNECT: Use the derived l only after deciding which cone surfaces are exposed.", "role": "CONNECT"}]}], "compact_anchor": {"prompt": "Surface formula asks for l but the stem gives h.", "result": "Build the axial triangle and derive l first.", "representation_ref": REP_CONE}},
    {**base(MIC_VOL), "title": "Volume as capacity, invariant and shared factor", "bucket_id": BUCKET, "primary_capability_ref": CAP_VOL, "intrinsic_badge": "MEDIUM", "badge_reason": "The learner must decide what role volume plays before calculating.", "entry_assumptions": ["Can calculate standard solid volumes and convert m³ to litres."], "inferential_jump": "Volume is not just a formula result: it can represent capacity, conserved material amount, or a shared factor whose ratio avoids unnecessary unknowns.", "teaching_path": [step("VOL-T1", "DECIDE", "Name the role volume plays in the context.", "This determines whether to convert, conserve, or compare.", "volume role"), step("VOL-T2", "TRANSFORM", "Apply the matching volume relation while preserving cubic scaling.", "Volume depends on three-dimensional measure.", "volume result or ratio"), step("VOL-T3", "VERIFY", "Reverse-convert or use a dimensionless ratio to check.", "A second route catches unit and scale errors.", "verified volume reasoning")], "relation_refs": [REL_VOL], "representation_refs": [], "question_family_refs": [FAM_VOL], "misconceptions": [misconception("Treat recasting as surface-area conservation or use a linear scale ratio for volume.", "What physical quantity measures the amount of metal?", "No material loss conserves volume; similar-solid volume scales with the cube of the linear scale.")], "exit_task": {"prompt": "A cylinder and cone have equal base radius and height. Without solving r or h, compare their volumes and explain the common factor.", "source_ref": SRC, "answer": model_answer("The cone has one third of the cylinder's volume.", ["Both contain the common factor πr²h.", "Only the cone has coefficient 1/3."], "Multiply the cone volume by 3 to recover the cylinder volume."), "oracle": {"no_numeric_claim": "The task checks structural formula comparison."}}, "research_contribution": "Q8-Q10 show three uses of volume that should be connected rather than taught as isolated formulas.", "prerequisite_refs": [], "lineage": [], "elicitation": {"predict": {"prompt": "When a solid is melted without loss, which quantity must stay the same?", "defensible_answer": "Volume, because the amount of material is unchanged."}, "attempt": {"produces": "A choice among conversion, conservation and ratio reasoning.", "closure": "RUBRIC", "rubric": [{"criterion": "Names the correct role of volume before calculating.", "evidence_of": "Chooses the governing model rather than a surface/linear substitute."}], "accepted": ["No metal lost → conserve volume."], "rejected": ["Conserve surface area."], "task": {"prompt": "For capacity, recasting and equal-r/h comparison, name what volume is doing in each case.", "givens": [], "representation_ref": None}}, "reconstruct": {"route": [{"ask": "Is the question asking how much fits, how much material remains, or how two formulas compare?", "why_this_ask": "It selects the volume role."}], "differs_from_teaching_path": "Starts from context language and maps it to the invariant/operation."}, "boundary_test": {"prompt": "Is surface area conserved when one sphere becomes many smaller spheres?", "answer": "No; new boundary surface is created although volume is conserved.", "confirms": "Conservation applies to material volume, not boundary area."}}, "construction_units": [{"id": "CU-SAV-VOLUME-ROLES", "decision": "Choose what volume means in the problem before performing arithmetic", "step_refs": ["VOL-T1", "VOL-T2", "VOL-T3"], "representation_ref": None, "reveal_stage_refs": [], "bank_anchor_ref": BANK_IDS["Q9"], "crux_question_refs": [BANK_IDS[x] for x in ("Q8", "Q9", "Q10")], "crux_step_ref": "VOL-T1", "misconception_indexes": [0], "independent_checks": [{"statement": "CHECK: State 1 m³ in litres and explain why this is a volume conversion.", "role": "CHECK"}, {"statement": "APPLY: For a 3:1 radius ratio of spheres, state the volume ratio.", "role": "APPLY"}, {"statement": "CONNECT: Compare cone and cylinder formulas by cancelling their common πr²h factor.", "role": "CONNECT"}]}], "compact_anchor": {"prompt": "Capacity, recasting, or comparison?", "result": "Choose the role of volume first; then convert, conserve or take a ratio.", "representation_ref": None}},
]

package = {
    "schema_version": "0.2.0",
    "package_id": "EVIDENCE-LIB-MAT-ISSUE10-SAV",
    "title": "Surface Areas & Volumes — Issue #10 cold-run draft",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Mathematics",
    "scope_summary": "Grade 9 revision specimen derived from ten owner-supplied mensuration questions; candidate teaching records are authored independently and claim no official source identity.",
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
    "extensions": {"grade9v3:authoring_specimen": {"issue": 10, "purpose": "REVISION", "learner_profile_ref": "PROFILE-ISSUE10-SAV-REVISION", "qrt_evidence": "evidence/authoring/issue10-surface-areas-volumes/qrt-review.v1.json"}},
    "data": [],
}

# Build an owner-bank skeleton from the exact text, then author the agent-owned fields.
intake = {
    "status": "READY",
    "intake_digest": "issue10-owner-prompt-2026-10-03",
    "inputs": {"questions": [{"id": qid, "label": qid[1:], "text": STEMS[qid]} for qid in STEMS]},
}
bank = owner_bank.new(intake, "issue10-sav")
qrt_by_id = {row["question_id"]: row for row in QRT["items"]}

# Verified post-attempt reasoning; support remains separate in scaffolds.
MOVES = {
    "Q1": [("DECIDE", "Recognize total surface area as six square faces.", "A cube has six congruent square faces.", "six faces"), ("REPRESENT", "Write one-face area as 7² cm².", "Each face is a square of side 7 cm.", "49 cm² per face"), ("TRANSFORM", "Multiply by six.", "Total surface area sums all six face areas.", "294 cm²")],
    "Q2": [("DECIDE", "Use curved surface area only.", "The question asks for the curved wall, not the circular ends.", "CSA model"), ("REPRESENT", "Convert diameter 14 cm to radius 7 cm.", "The relation 2πrh is written in radius.", "r=7 cm"), ("TRANSFORM", "Evaluate 2πrh.", "Substitution now matches the formula variables.", "880 cm²")],
    "Q3": [("DECIDE", "Inventory the metal sheet as curved wall plus one bottom disk.", "The bucket is open at the top, so no top disk exists.", "wall + base"), ("REPRESENT", "Write 2πrh + πr².", "Those are the areas of the two physical sheet pieces.", "area model"), ("TRANSFORM", "Evaluate with r=7 cm, h=18 cm and π=22/7.", "The model now contains all and only included surfaces.", "946 cm²")],
    "Q4": [("DECIDE", "Identify slant height l as the length needed by cone curved area.", "Canvas follows the sloping surface, not the vertical axis.", "need l"), ("REPRESENT", "Use the axial right triangle with r=7 m and h=24 m.", "For a right cone, r and h are perpendicular legs and l is the hypotenuse.", "l²=7²+24²"), ("TRANSFORM", "Find l=25 m, then evaluate πrl for the open tent.", "The base is open, so only curved canvas is included.", "550 m²")],
    "Q5": [("DECIDE", "Treat the bowl mouth as an opening, not a material disk.", "The requested inner surface is the curved interior of the open hemisphere.", "curved hemisphere"), ("REPRESENT", "Use 2πr² rather than 3πr².", "3πr² would include a flat circular base that is not present.", "2πr²"), ("TRANSFORM", "Evaluate with r=10.5 cm.", "The expression matches the physical inner surface.", "693 cm²")],
    "Q6": [("DECIDE", "Inventory only the exterior cone and hemisphere surfaces; exclude the shared circle.", "The joining face is internal after assembly.", "exterior surfaces"), ("REPRESENT", "Use the cone axial triangle to find l from r=3.5 cm and h=12 cm.", "Cone curved area requires slant height.", "l=12.5 cm"), ("TRANSFORM", "Add πrl and 2πr², without a joining disk.", "These are exactly the reachable exterior surfaces.", "214.5 cm²"), ("VERIFY", "Check what an erroneous joining disk would add.", "A hidden disk would contribute πr²=38.5 cm², exposing the modelling error.", "hidden-interface check")],
    "Q7": [("DECIDE", "State the painted surfaces: outer curved wall and outside base only.", "The top is open and the inside is explicitly unpainted.", "two painted surfaces"), ("REPRESENT", "Write 2πrh + πr².", "Each term corresponds to one painted physical surface.", "paint-area model"), ("TRANSFORM", "Evaluate with r=7 cm and h=25 cm.", "The calculation now follows the stated paint specification.", "1254 cm²")],
    "Q8": [("DECIDE", "Find full tank volume before applying the fill percentage.", "Seventy-five percent describes the tank's capacity, not a single dimension.", "3.6 m³ full"), ("REPRESENT", "Take 75% of 3.6 m³.", "The water occupies three quarters of the full volume.", "2.7 m³ water"), ("TRANSFORM", "Convert 2.7 m³ to litres using 1 m³=1000 L.", "The conversion preserves the same physical volume.", "2700 L")],
    "Q9": [("DECIDE", "Use conservation of volume, not surface area.", "No metal lost means the amount of material is unchanged.", "volume invariant"), ("REPRESENT", "Set one large-sphere volume equal to n small-sphere volumes.", "The same total material volume is redistributed.", "6³ = n·2³ after common factors cancel"), ("TRANSFORM", "Solve n=(6/2)³.", "Sphere volume scales with the cube of radius.", "27 spheres"), ("VERIFY", "Compare surface areas before and after.", "144π becomes 27×16π=432π, so boundary area is not conserved.", "surface area triples")],
    "Q10": [("DECIDE", "Compare the cone and cylinder volume formulas before solving dimensions.", "The solids have the same r and h.", "common factor"), ("REPRESENT", "Cancel the common πr²h factor conceptually.", "Cylinder volume is πr²h while cone volume is one third of it.", "Vcone=Vcylinder/3"), ("TRANSFORM", "Compute 924/3.", "The structural ratio supplies the cone volume directly.", "308 cm³")],
}

checks = {row["question_id"]: row["independent_check"] for row in QRT["items"]}
for qid, row in zip(STEMS, bank["questions"]):
    evidence = qrt_by_id[qid]
    row["id"] = BANK_IDS[qid]
    row["original_identifier"] = qid
    row["primary_capability_ref"] = PRIMARY_CAP[qid]
    row["family_ref"] = FAMILY[qid]
    row["conditions"] = ["Use π = 22/7 wherever numerical approximation is required unless the question states otherwise."]
    row["figure_refs"] = [FIGURE[qid]] if qid in FIGURE else []
    move_rows = []
    for n, (kind, action, why, output) in enumerate(MOVES[qid], 1):
        move_rows.append({"id": f"{BANK_IDS[qid]}-MOVE-{n}", "kind": kind, "action": action, "why_valid": why, "inputs": ["stated givens and prior move"], "output": output})
    row["answer"] = {"kind": "EXACT", "summary": evidence["verified_answer"], "reasoning_route": move_rows, "crux_move_ref": move_rows[min(1, len(move_rows)-1)]["id"], "check": checks[qid], "verification_status": "CHECKED_BY_AUTHOR"}
    hints = list(evidence["hints"])
    if qid == "Q6":
        hints += ["Keep the shared joining circle on your inventory until you decide whether it is reachable from outside.", "Use a final touch/paint test on every area term before calculating the total."]
    stages = ["KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "FORMAL_MODEL", "CHECKPOINT"]
    kinds = ["CONNECT", "REPRESENT", "EXECUTE", "EXECUTE", "EXECUTE"]
    reveals = ["CONCEPT", "METHOD", "METHOD", "METHOD", "METHOD"]
    row["scaffolds"] = [{"text": text, "support_kind": kinds[i], "reveals": reveals[i], "learner_stage": stages[i], "supports_move_ref": move_rows[min(i, len(move_rows)-1)]["id"]} for i, text in enumerate(hints)]
    analysis = row["extensions"].setdefault("grade9v3:analysis", {})
    analysis["learner_question_type"] = "constructed_response"
    analysis["difficulty"] = evidence["difficulty"]
    analysis["common_wrong_route"] = evidence["misconception"]["M1"]
    analysis["expected_time_seconds"] = 90 if evidence["difficulty"]["band"] == "D1" else 150 if evidence["difficulty"]["band"] == "D2" else 240
    analysis["cognitive_demand"] = evidence["demand"]
    analysis["stable_crux_move"] = evidence["Z"]
    row["extensions"]["grade9v3:math_spans"] = []
    if qid not in FIGURE:
        row["extensions"]["grade9v3:component_waivers"] = {"REPRESENTATION": evidence["representation"]["reason"]}
    row.pop("hints", None)
    row.pop("hint_ladder", None)

manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-MAT-ISSUE10-SAV",
    "subject": "Mathematics",
    "home_href": "../../../index.html",
    "question_bank_href": "../../../question-bank/index.html",
    "package_refs": ["evidence/authoring/issue10-surface-areas-volumes/generated/package.v1.json"],
    "bank_refs": ["evidence/authoring/issue10-surface-areas-volumes/generated/owner.bank.json"],
    "selection": {"microtopics": [MIC_SURF, MIC_CONE, MIC_VOL], "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)], "core2a": [], "core2b": []},
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "owner.bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
