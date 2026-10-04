#!/usr/bin/env python3
"""Complete the Issue #37 owner-bank records to the Core2 D3/D4 semantic contract.

This is a deterministic authoring pass over build_specimen.py output. It adds only
question-analysis structure: stated conditions, five purposeful pre-solution supports,
four typed reasoning moves, and the five-component learner-relative difficulty score.
It never edits the verbatim owner stems.
"""
from __future__ import annotations

import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
BANK_PATH = HERE / "generated" / "owner.bank.json"

CONDITIONS = {
    "Q1": [
        "Molecule is formamide, H–C(=O)–NH2.",
        "Local Lewis count at nitrogen is three sigma bonds and one lone pair.",
        "The supplied approximately planar arrangement permits nitrogen-lone-pair donation into the adjacent carbonyl pi system.",
        "The supplied donation model requires a suitably aligned p-like orbital."
    ],
    "Q2": [
        "Use the formamide situation supplied in Q1.",
        "Compare an approximately planar arrangement with an approximately 90-degree twist about the C–N bond.",
        "Atom connectivity must be preserved.",
        "Formal electron count must be distinguished from orbital alignment.",
        "The qualitative sketches must not be treated as measurements of donation strength."
    ],
    "Q3": [
        "Atom connectivity is fixed.",
        "The benchmark supplies that twisting toward 90 degrees reduces nitrogen-to-carbonyl orbital alignment and the delocalisation contribution.",
        "The explanation must distinguish model assumptions from measured facts."
    ],
    "Q4": [
        "Site A is the amide nitrogen in H–C(=O)–NH2.",
        "Site B is the amine nitrogen in H–C(=O)–CH2–NH2.",
        "In the simplified introductory model, saturated CH2 provides no continuous aligned p-orbital pathway.",
        "Spatial proximity alone must not be equated with conjugation."
    ],
    "Q5": [
        "Use the supplied approximate observations: CH4 about 109.5 degrees, NH3 about 107 degrees, H2O about 104.5 degrees.",
        "All three are commonly introduced using an sp3 description at the central atom.",
        "The benchmark also supplies approximately planar amide nitrogen with lone-pair delocalisation.",
        "The replacement claim must state what further evidence is needed for a unique physical account."
    ],
    "Q6": [
        "Use Sites A and B as defined in Q4.",
        "Distinguish remembering the local four-domain counting rule from deciding whether its assumptions hold."
    ],
    "Q7": [
        "The benchmark supplies neutral CH3· as approximately planar.",
        "The unpaired electron is supplied as occupying a p-like orbital perpendicular to the three C–H sigma directions.",
        "The supplied model must be kept distinct from a universal claim."
    ],
    "Q8": [
        "Compare a completely localised pyramidal nitrogen-lone-pair description with an approximately planar nitrogen arrangement allowing possible donation into the carbonyl pi system.",
        "At least one proposed inference must be identified as not establishable by geometry alone."
    ],
    "Q9": [
        "The supplied simplified torsional model defines the relevant p-orbital overlap factor as cos(theta).",
        "theta is the angle between the relevant alignment directions.",
        "Compare theta = 0, 60 and 90 degrees.",
        "Execution of the supplied overlap model must be separated from claims about total molecular energy."
    ],
    "Q10": [
        "Audit the proposed rule against NH3, allene, formamide and H–C(=O)–CH2–NH2.",
        "The final framework must identify where local counting is useful and where additional evidence or a model is needed."
    ]
}

SUPPORTS = {
    "Q1": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Start with two separate facts: the Lewis-domain count is local bookkeeping; the stem also supplies a delocalisation condition that depends on orbital direction."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Sketch three nitrogen sigma directions in one plane and leave a separate perpendicular direction available; do not label the final hybridisation yet."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Ask which local description can accommodate both the sigma framework and the supplied p-like donor direction."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Test the automatic four-domain rule against the supplied alignment requirement rather than assuming either description is universally exact."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Before committing, add one sentence saying what the chosen label describes and one stronger claim it does not establish uniquely.")
    ],
    "Q2": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Separate what rotation can change from what it cannot: orientation can change while connectivity and formal electron count stay fixed."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Draw the same H–C(=O)–NH2 skeleton twice before drawing any orbital directions."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "On the planar copy, mark the nitrogen donor direction and carbonyl p direction so their relative alignment is visible."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "On the twisted copy, rotate only the relevant C–N torsional orientation toward 90 degrees; leave the Lewis lone pair and connectivity unchanged."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Check your caption: it may say alignment is poorer, but it must not turn the sketch into a numerical donation measurement.")
    ],
    "Q3": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "The stem gives the structural change and qualitative outcome; your task is to supply a mechanism without promoting a label into a cause."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Compare the donor and carbonyl p directions before and after torsion; focus on whether side-on overlap can be maintained."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "State how reduced compatible overlap can reduce the delocalisation contribution in the supplied model."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Now audit the sentence 'the hybridisation label changes': ask whether changing a name is itself a physical interaction."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Tag each final statement as prompt-given, model inference, or something that would need independent measurement/calculation.")
    ],
    "Q4": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "A lone pair and a nearby pi bond are not yet a conjugation decision; build a sequence of tests that can fail."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Trace a potential orbital path from each nitrogen toward the carbonyl rather than judging by drawing distance."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "For each site, check local inventory first, then adjacency, then whether a continuous compatible pathway exists in the supplied simplified model."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Apply the alignment/model-validity checkpoint only after connectivity passes; do not let spatial proximity bypass a saturated interruption."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Create one structural counterfactual that changes the orbital pathway itself; verify that your procedure would then re-open the decision.")
    ],
    "Q5": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Stress-test the word 'uniquely' before trying to replace the whole hybridisation model."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Make a four-row table: CH4, NH3, H2O, amide N; separate domain-count language from observed molecular geometry."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Use the three supplied angles to show that a shared introductory domain description does not fix one exact bond angle."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Use lone-pair occupancy and the amide delocalisation boundary to write a qualified replacement rather than the opposite absolute claim."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Name evidence beyond geometry that would be needed before claiming one unique electronic/orbital account.")
    ],
    "Q6": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Write the familiar four-domain classification rule, but put a second box beside it labelled 'conditions for using it'."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Compare Site A and Site B with the same local-count column and a separate orbital-pathway/evidence column."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Identify when the localised picture is enough for an introductory classification."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Identify evidence—such as delocalisation-sensitive alignment or radical/SOMO information—that makes an automatic stop at the count inadequate."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Your final answer should contain two verbs: 'recall' the rule and 'test' whether its conditions hold.")
    ],
    "Q7": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "The dot in CH3· is occupancy information. Keep it visible before thinking about any hybridisation slogan."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Draw three coplanar C–H sigma directions and a perpendicular p-like orbital, then place the supplied unpaired electron in that orbital."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Classify that orbital as empty, singly occupied or doubly occupied from the stem—not from a memorised three-coordinate rule."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Now test the word 'always': decide whether one supplied radical model can logically establish a rule for every three-sigma-bond centre."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Check that your sketch and sentence agree on occupancy; an empty p orbital would contradict the given radical model.")
    ],
    "Q8": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Discriminating evidence should make the two proposed descriptions expect different outcomes; it need not prove one unique orbital partition."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "List evidence in separate rows: geometry, C–N structural/rotational behaviour, spectroscopy, and a defined electronic-structure calculation."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "For each row, state the qualitative observation that would be more consistent with one description than the other."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Separate 'supports/consistent with' from 'measures donation' and 'uniquely proves an orbital model'."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Ensure at least one final sentence says exactly what geometry alone cannot establish.")
    ],
    "Q9": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Underline the noun attached to the formula: the stem defines an overlap factor, not a total-energy equation."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Place 0°, 60° and 90° beside the same two orbital-direction arrows so only theta changes."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Evaluate cos(theta) at the three requested angles and label every result 'overlap factor'."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Before discussing energy, search the givens for a second relation connecting overlap factor to total molecular energy."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "Use a counterexample test: could some other energy contribution change while theta—and thus the supplied overlap factor—stays the same?")
    ],
    "Q10": [
        ("CONNECT", "CONCEPT", "KEY_CONCEPT", "Do not replace one slogan with another. Turn the proposed one-line rule into a sequence of decisions with stop/escalate points."),
        ("REPRESENT", "METHOD", "REPRESENTATION", "Give each named case one row and mark which checkpoint it stresses: lone-pair geometry, orthogonal p systems, delocalisation, or a broken p pathway."),
        ("EXECUTE", "METHOD", "FIRST_MOVE", "Start the framework with local sigma/lone-pair inventory because that remains useful information."),
        ("EXECUTE", "METHOD", "FORMAL_MODEL", "Add connectivity/alignment/model-sufficiency checks before letting a hybridisation label carry explanatory weight."),
        ("EXECUTE", "METHOD", "CHECKPOINT", "End with an explicit evidence-escalation rule for stronger shape, reactivity, resonance or energy claims.")
    ]
}

DIFFICULTY = {
    "Q1": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q2": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q3": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q4": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q5": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q6": ("D3", {"concept_model_selection":2,"representation_translation":1,"reasoning_chain_length":1,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q7": ("D3", {"concept_model_selection":1,"representation_translation":2,"reasoning_chain_length":1,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q8": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2}),
    "Q9": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":1,"trap_exception_sensitivity":2}),
    "Q10": ("D4", {"concept_model_selection":2,"representation_translation":2,"reasoning_chain_length":2,"algebra_computational_load":0,"trap_exception_sensitivity":2})
}

# Question-specific four-move routes. The crux is deliberately the third move: the
# move from execution/representation into model-boundary judgement.
ROUTES = {
    "Q1": [
        ("DECIDE", "Separate the local Lewis-domain count from the supplied delocalisation/alignment requirement.", "They are different evidence layers and both must be explained."),
        ("REPRESENT", "Represent a planar sigma framework while reserving a p-like donor direction on nitrogen.", "The supplied donation condition requires a suitably aligned p-like orbital."),
        ("CONNECT", "Choose an approximately sp2-like local description and explain why automatic four-domain sp3 is insufficient here.", "A useful local label must accommodate the sigma framework and the supplied delocalisation-sensitive orbital direction rather than overwrite either."),
        ("VERIFY", "State that the label is descriptive and does not uniquely measure or cause delocalisation.", "Hybridisation is model vocabulary; stronger electronic claims require additional evidence/model definition.")
    ],
    "Q2": [
        ("DECIDE", "Freeze connectivity and formal Lewis electron count as invariants of the comparison.", "The stem explicitly requires these to be preserved while torsional orientation changes."),
        ("REPRESENT", "Draw aligned nitrogen-donor and carbonyl-p directions in the planar qualitative arrangement.", "Compatible direction is the geometric feature the supplied delocalisation model needs."),
        ("TRANSFORM", "Rotate the C–N torsional arrangement toward 90 degrees while leaving connectivity and formal count unchanged.", "Torsion changes relative orbital orientation without requiring a different Lewis electron inventory."),
        ("VERIFY", "Label the sketch qualitative rather than a measurement of donation strength.", "A drawing of orientation supplies no calibrated observable for donation magnitude.")
    ],
    "Q3": [
        ("DECIDE", "Take the supplied reduction in alignment on twisting as the benchmark result to explain, not a quantity to re-measure.", "The stem fixes the qualitative result and asks for its orbital-overlap account."),
        ("REPRESENT", "Compare side-on compatibility of the donor and carbonyl p directions before and after torsion.", "Pi-type interaction depends on compatible spatial orientation in this simplified model."),
        ("CONNECT", "Attribute the reduced delocalisation contribution to reduced compatible overlap rather than to a changed label itself.", "Changing a descriptive label is not a physical interaction; orbital geometry supplies the model mechanism."),
        ("VERIFY", "Separate prompt-given result and qualitative model inference from any exact energetic/donation claim.", "Exact magnitudes require a specified calculation or measurement beyond the given qualitative model.")
    ],
    "Q4": [
        ("DECIDE", "Inventory the local sigma/lone-pair structure and identify the candidate adjacent pi acceptor for each site.", "A conjugation decision needs both a donor and a structurally reachable acceptor."),
        ("REPRESENT", "Trace whether a continuous compatible orbital pathway connects each nitrogen to the carbonyl in the supplied simplified model.", "Continuity and alignment, not drawing distance, determine whether the introductory conjugation route is available."),
        ("CONNECT", "Classify A as pathway-available and B as interrupted by saturated CH2 under the stated model.", "The stem explicitly states that the intervening saturated CH2 supplies no continuous aligned p pathway."),
        ("VERIFY", "Change the bridge to an unsaturated/appropriately connected counterfactual and rerun the procedure.", "A structural change to the pathway invalidates the earlier stop decision and tests transfer of the procedure.")
    ],
    "Q5": [
        ("DECIDE", "Test the student's word 'uniquely' against the three supplied four-domain cases and their different observed angles.", "One exact angle cannot be uniquely fixed by a label shared across differing observations."),
        ("REPRESENT", "Separate electron-domain classification, molecular geometry and observed angle for CH4, NH3, H2O and amide N.", "These are related but non-identical descriptive layers."),
        ("CONNECT", "Replace the absolute claim with a first-order model statement that allows lone-pair/environment effects and the amide delocalisation boundary.", "A useful model may organize local bonding without uniquely determining all quantitative geometry or electronic structure."),
        ("VERIFY", "Name structural, spectroscopic or defined computational evidence needed for a stronger unique physical account.", "Geometry alone generally underdetermines a unique orbital partition or resonance magnitude.")
    ],
    "Q6": [
        ("DECIDE", "Recall the local four-domain rule without yet deciding that it is sufficient.", "Rule knowledge and applicability are separate tasks in the question."),
        ("REPRESENT", "Compare Sites A and B using local count plus a separate column for delocalisation/alignment evidence.", "This prevents the count from erasing information that belongs to another model layer."),
        ("CONNECT", "Stop at local classification only when bonding is sufficiently localised and no supplied evidence requires a conjugation-sensitive model.", "A model is adequate only when the phenomena relevant to the task fall within its assumptions."),
        ("VERIFY", "Use Site A's supplied delocalisation and Site B's interrupted pathway as opposite applicability checks.", "The paired sites test whether the decision responds to evidence rather than to memorised wording.")
    ],
    "Q7": [
        ("DECIDE", "Read the radical dot as explicit orbital-occupancy information.", "The stem supplies an unpaired electron, so occupancy cannot be inferred as empty."),
        ("REPRESENT", "Draw three coplanar C–H sigma directions and one perpendicular p-like orbital containing one electron.", "That representation is the literal translation of the supplied planar methyl-radical model."),
        ("CONNECT", "Reject the universal empty-p rule because this supplied p-like orbital is singly occupied and one case cannot establish 'always'.", "Both the occupancy fact and the scope of the evidence contradict the proposed universal statement."),
        ("VERIFY", "Check that the sketch, electron count and verbal conclusion are mutually consistent.", "A missing radical electron or an empty p orbital would contradict the givens.")
    ],
    "Q8": [
        ("DECIDE", "Choose observations for which the localised-pyramidal and planar-delocalised descriptions make different qualitative expectations.", "Discrimination requires evidence connected to a prediction difference."),
        ("REPRESENT", "Organize planarity, C–N structural/rotational behaviour, spectroscopy and defined electronic-structure calculations as distinct evidence channels.", "Different channels probe different consequences and reduce reliance on one ambiguous observable."),
        ("CONNECT", "For each channel, state only the inference it warrants—for example consistency with delocalisation rather than a unique measured resonance fraction.", "Evidence can favour a model without uniquely fixing an orbital partition or donation magnitude."),
        ("VERIFY", "Identify explicitly that geometry alone cannot quantify donation or prove one unique electronic account.", "Multiple electronic descriptions can be compatible with similar geometry, so stronger claims need additional probes/models.")
    ],
    "Q9": [
        ("DECIDE", "Bind the supplied cos(theta) formula to the named quantity: p-orbital overlap factor.", "A mathematical relation warrants claims only about the variable it defines unless another bridge is given."),
        ("TRANSFORM", "Evaluate cos(0 degrees), cos(60 degrees) and cos(90 degrees) as 1, 1/2 and 0.", "These are the exact trigonometric values requested by the supplied simplified overlap model."),
        ("CONNECT", "Reject the inference that total molecular energy must therefore follow cos(theta).", "No relation connecting the overlap factor to total molecular energy is supplied, and total energy can contain additional contributions."),
        ("VERIFY", "Hold theta fixed while imagining another energy contribution changing; note that overlap stays fixed while total energy need not.", "This counterexample exposes the underdetermination without denying the supplied overlap calculation.")
    ],
    "Q10": [
        ("DECIDE", "Retain local sigma/lone-pair inventory as the first useful step rather than discarding hybridisation language entirely.", "The proposed rule contains useful local information even though its explanatory scope is overclaimed."),
        ("REPRESENT", "Map NH3, allene, formamide and the separated amine to the extra checkpoint each case demands.", "The four examples stress different limits: lone-pair geometry, orthogonal p systems, delocalisation and pathway interruption."),
        ("CONNECT", "Build a staged framework: local count -> connectivity/adjacency -> compatible orbital path -> model sufficiency -> warranted label/claim.", "Each escalation is triggered by evidence the simpler local description cannot by itself resolve."),
        ("VERIFY", "Attach an evidence/model escalation rule to claims about exact geometry, resonance magnitude, energy or reactivity.", "Stronger physical claims require observations or explicit models that go beyond a local hybridisation label.")
    ]
}

bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
for row in bank["questions"]:
    qid = row["original_identifier"]
    row["conditions"] = CONDITIONS[qid]

    moves = []
    for number, (kind, action, why) in enumerate(ROUTES[qid], 1):
        move_id = f"{row['id']}-MOVE-{number}"
        moves.append({
            "id": move_id,
            "kind": kind,
            "action": action,
            "why_valid": why,
            "inputs": ["owner-supplied stem" if number == 1 else f"output of move {number-1}"],
            "output": row["answer"]["summary"] if number == 4 else f"{qid} reasoning checkpoint {number}"
        })
    row["answer"]["reasoning_route"] = moves
    row["answer"]["crux_move_ref"] = moves[2]["id"]

    row["scaffolds"] = []
    for number, (kind, reveals, stage, text) in enumerate(SUPPORTS[qid]):
        support_ref = moves[min(number, 2)]["id"]
        row["scaffolds"].append({
            "text": text,
            "support_kind": kind,
            "reveals": reveals,
            "learner_stage": stage,
            "supports_move_ref": support_ref
        })

    band, components = DIFFICULTY[qid]
    score = sum(components.values())
    row["extensions"]["grade9v3:analysis"]["difficulty"] = {
        "band": band,
        "score": score,
        "basis": "Learner-relative estimate from the simulated owner preset using the canonical five components; no mastery percentage is inferred.",
        "components": components
    }

BANK_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"finalized semantic Core2 records: {BANK_PATH}")
