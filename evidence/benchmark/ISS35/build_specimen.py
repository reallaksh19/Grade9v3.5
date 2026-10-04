#!/usr/bin/env python3
"""Materialise the controlled Issue #35 Chemistry candidate from immutable prompt + academic ledger."""
from __future__ import annotations

import json
import re
from pathlib import Path
from Shared.tools import owner_bank

HERE = Path(__file__).resolve().parent
OUT = HERE / "generated"
LEDGER = json.loads((HERE / "question-ledger.json").read_text(encoding="utf-8"))
CARDS = json.loads((HERE / "source-cards.json").read_text(encoding="utf-8"))
PROMPT = (HERE / "owner-core-prompt.md").read_text(encoding="utf-8")

# Parse, do not rewrite, the ten immutable stems from A/B/C custody.
_matches = re.findall(r"### Q(\d+)\n\n(.*?)(?=\n\n### Q\d+|\n\n## B — FINAL DELIVERABLES)", PROMPT, flags=re.S)
STEMS = {f"Q{n}": text.strip() for n, text in _matches}
if list(STEMS) != [f"Q{i}" for i in range(1, 11)]:
    raise SystemExit(f"owner prompt parse did not yield Q1-Q10 in order: {list(STEMS)}")

SRC_OWNER = "SRC-OWNER-ISS35-HYBRIDISATION"
SRC_HYB = "SRC-IUPAC-GOLDBOOK-HYBRIDIZATION"
SRC_RES = "SRC-IUPAC-GOLDBOOK-RESONANCE"
SRC_DEL = "SRC-IUPAC-GOLDBOOK-DELOCALIZATION"
SRC_ALLENE = "SRC-ACS-CENTSCI-ALLENE-2018"
SRC_NCERT = "SRC-NCERT-CLASSXI-CHEM-BONDING-SCOPE"
BUCKET = "BUCKET-CHEM-BOND-HYBRIDISATION-ISS35"
CAP_DEL = "CAP-CHEM-HYB-DELOCALISATION"
CAP_PI = "CAP-CHEM-HYB-PI-ORIENTATION"
CAP_LOCAL = "CAP-CHEM-HYB-LOCAL-SIGMA"
MIC_DEL = "MIC-CHEM-HYB-DELOCALISATION"
MIC_PI = "MIC-CHEM-HYB-PI-ORIENTATION"
MIC_LOCAL = "MIC-CHEM-HYB-LOCAL-PROCEDURE"
REP_DEL = "REP-CHEM-HYB-CONTRIBUTOR-INVARIANT-ORBITAL"
REP_ALLENE = "REP-CHEM-HYB-ALLENE-ORTHOGONAL-P"
REP_LOCAL = "REP-CHEM-HYB-LOCAL-DECISION"
REP_PI = "REP-CHEM-HYB-P-CONTINUITY"
FAM_DEL = "FAM-CHEM-HYB-DELOCALISATION"
FAM_PI = "FAM-CHEM-HYB-PI-GEOMETRY"
FAM_LOCAL = "FAM-CHEM-HYB-LOCAL-ASSIGNMENT"

by_qid = {row["question_id"]: row for row in LEDGER["items"]}
BANK_IDS = {qid: row["stable_id"] for qid, row in by_qid.items()}


def base(record_id: str, source_refs=None) -> dict:
    return {
        "id": record_id,
        "version": "0.1.0",
        "status": "CANDIDATE",
        "source_refs": list(source_refs if source_refs is not None else [SRC_OWNER]),
        "evidence_refs": [],
        "extensions": {},
    }


def teaching_step(step_id: str, role: str, action: str, why: str, output: str) -> dict:
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


def package_resource(card: dict) -> dict:
    role = ["SCIENTIFIC_CHECK"]
    origin = "WEB"
    if card["id"] == SRC_OWNER:
        role = ["QUESTION_BANK", "AUTHOR_CREATED"]
        origin = "AUTHORED"
    elif card["id"] == SRC_NCERT:
        role = ["CURRICULUM", "SCIENTIFIC_CHECK"]
    row = base(card["id"], [])
    row.update({
        "title": card["id"].replace("SRC-", "").replace("-", " ").title(),
        "origin": origin,
        "locator": card["locator"],
        "edition": "Issue #35 round-1 source check",
        "section": "; ".join(card["claims_supported"]),
        "last_checked": CARDS["checked_on"],
        "access_status": "SECTION_INSPECTED",
        "rights_status": "Reference/custody evidence only; no external publication authority is inherited.",
        "snapshot_ref": None,
        "snapshot_digest": None,
        "role": role,
        "supports_claims": list(card["claims_supported"]),
        "entry_capabilities": [],
        "depth": ["COMPETITION"],
        "selection_reason": card["model_boundary"],
        "fallback": [],
    })
    if card["id"] == SRC_OWNER:
        row["rights_status"] = "Owner-supplied benchmark custody; coordinating-agent draft; not official exam/PYQ and not personally authored by owner."
        row["extensions"]["grade9v3:benchmark_authorship"] = {
            "custody_class": "OWNER_SUPPLIED_RAW_INPUT",
            "drafted_by": "COORDINATING_AGENT",
            "personally_authored_by_owner": False,
            "official_exam_or_pyq": False,
        }
    return row


resources = [package_resource(card) for card in CARDS["cards"]]

bucket = base(BUCKET, [SRC_OWNER, SRC_NCERT])
bucket.update({
    "title": "Local hybridisation, p-orbital geometry and delocalisation",
    "topic": "Chemical Bonding and Molecular Structure",
    "intrinsic_badge": "HARD",
    "badge_reason": "The crux is coordinating atom-local sigma-framework labels with p-orbital orientation and translating localized Lewis contributors into one delocalised electronic description without conflating these model layers.",
    "depth_overlay": "ADVANCED",
    "curriculum_mappings": [],
    "prerequisite_refs": [],
    "primary_representation_ref": REP_DEL,
})

capabilities = [
    {**base(CAP_DEL, [SRC_RES, SRC_DEL, SRC_OWNER]), "action": "Translate formal Lewis contributors into one qualitative delocalised pi description while preserving the invariant sigma framework.", "success_criterion": "Separates invariant connectivity/sigma framework from contributor-local formal bond/charge placement and rejects temporal switching among contributors.", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_PI, [SRC_ALLENE, SRC_OWNER]), "action": "Coordinate local sigma-framework assignments with the count and orientation of unhybridised p orbitals required by pi bonding.", "success_criterion": "Uses p-orbital orientation to explain allene terminal-plane geometry, twisting effects, and continuous versus interrupted p pathways.", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
    {**base(CAP_LOCAL, [SRC_HYB, SRC_OWNER]), "action": "Assign introductory hybridisation locally from sigma-bond directions/lone-pair domains and verify the assignment against required unhybridised p orbitals.", "success_criterion": "Never assigns one label to a whole molecule and distinguishes multiple-bond components from local electron-domain count.", "prerequisite_refs": [], "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE"},
]


def representation(record_id: str, purpose: str, asset: str, stages: list[tuple[str, str, str]], correspondence: list[dict]) -> dict:
    row = base(record_id, [])
    row.update({
        "kind": "ORBITAL_MODEL",
        "purpose": purpose,
        "required_elements": [label for _, label, _ in stages],
        "relation_refs": [],
        "read_order": [job for _, _, job in stages],
        "instance_constraints": ["Pre-attempt stages orient or ask for a correspondence without displaying the protected final conclusion."],
        "accessibility": ["SVG has role=img, title and description.", "Text labels duplicate orientation/line meaning."],
        "misleading_alternatives": ["Treating a formal contributor as a time-resolved state.", "Assigning one hybridisation label to an entire molecule."],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [{"id": sid, "label": label, "purpose": job, "visible_elements": [label]} for sid, label, job in stages],
    })
    return row

representations = [
    representation(REP_DEL, "Stage the contributor -> invariant -> orbital translation without treating contributors as time states.", "evidence/benchmark/ISS35/assets/nitrate-contributor-orbital.svg", [
        ("HYB-DELOC-1", "Three Lewis contributors", "Compare source representations before accepting a model."),
        ("HYB-DELOC-2", "Invariant sigma skeleton", "Mark what remains fixed across contributors."),
        ("HYB-DELOC-3", "Perpendicular p direction", "Choose the orbital direction compatible with the planar sigma framework."),
        ("HYB-DELOC-4", "One delocalised pi overlay", "Reveal the post-commit target representation and no-switching statement."),
    ], [
        {"element": "three N-O connections", "symbol": "sigma skeleton", "in_words": "connectivity and three sigma directions remain invariant"},
        {"element": "formal N=O placement", "symbol": "contributor-local", "in_words": "formal placement differs among contributors"},
        {"element": "out-of-plane p set", "symbol": "pi system", "in_words": "one qualitative delocalised orbital description"},
    ]),
    representation(REP_ALLENE, "Show the two mutually perpendicular central p orbitals and connect each to a different terminal carbon without flattening allene.", "evidence/benchmark/ISS35/assets/allene-orthogonal-p.svg", [
        ("HYB-ALLENE-1", "Local sigma axes", "Read the C=C=C sigma axis and terminal sigma planes."),
        ("HYB-ALLENE-2", "First p overlap", "Track one terminal-central pi overlap."),
        ("HYB-ALLENE-3", "Second orthogonal p overlap", "Track the independent perpendicular pi overlap."),
        ("HYB-ALLENE-4", "Terminal-plane consequence", "Relate p-axis orientation to the two CH2 planes."),
    ], [{"element": "central linear sigma directions", "symbol": "sp sigma framework", "in_words": "two sigma directions at central carbon"}, {"element": "orthogonal p pairs", "symbol": "two p directions", "in_words": "two independent perpendicular pi-overlap directions"}]),
    representation(REP_LOCAL, "Use an atom-by-atom decision path: local sigma/lone-pair domains first, then a p-orbital consistency check.", "evidence/benchmark/ISS35/assets/local-hybridisation-check.svg", [
        ("HYB-LOCAL-1", "Choose one atom", "Prevent molecule-wide labeling."),
        ("HYB-LOCAL-2", "Count local domains", "Count sigma directions and lone-pair domains."),
        ("HYB-LOCAL-3", "Assign local model", "Map local domain geometry to sp/sp2/sp3."),
        ("HYB-LOCAL-4", "Check leftover p orbitals", "Verify required pi bonding and orientation."),
    ], [{"element": "atom-local box", "symbol": "one centre at a time", "in_words": "hybridisation is assigned locally"}, {"element": "p-orbital check", "symbol": "consistency", "in_words": "the local assignment must support the required pi system"}]),
    representation(REP_PI, "Contrast preserved sigma-axis overlap with orientation-sensitive p overlap and a continuous versus interrupted p-orbital chain.", "evidence/benchmark/ISS35/assets/pi-overlap-continuity.svg", [
        ("HYB-PI-1", "Sigma axis", "Track end-on overlap along the bond axis."),
        ("HYB-PI-2", "Parallel p requirement", "Track side-on overlap before twisting."),
        ("HYB-PI-3", "P-orbital chain", "Walk adjacent p orbitals along a conjugated chain."),
        ("HYB-PI-4", "Interrupted bridge", "Locate an sp3 centre with no bridging p orbital."),
    ], [{"element": "bond axis", "symbol": "sigma", "in_words": "axial overlap remains aligned under rotation about its own axis"}, {"element": "parallel p lobes", "symbol": "pi", "in_words": "side-on overlap depends on relative p orientation"}, {"element": "sp3 bridge", "symbol": "break", "in_words": "no unhybridised p orbital continues the chain"}]),
]

families = [
    {**base(FAM_DEL), "title": "Formal contributors to delocalised orbital model", "capability_refs": [CAP_DEL], "solution_structure": ["Separate invariant from contributor-local features.", "Fix the sigma framework.", "Construct one delocalised pi description.", "Check equivalent bonds and no-switching language."], "demand_dimensions": {"model_choice": "Localized versus delocalised description.", "representation_translation": "Lewis contributors to one orbital description.", "reasoning_steps": "Compare, preserve invariants, translate, verify.", "novelty": "Formal contributor status and multi-centre delocalisation."}, "safe_variations": ["Use nitrate or carbonate while preserving the same representation boundary."], "transfer_boundaries": ["Do not infer quantitative bond order or energy from a qualitative diagram."], "common_wrong_routes": ["Treat one contributor as permanent or say the molecule switches among contributors."], "item_refs": [BANK_IDS[x] for x in ("Q1", "Q2", "Q7")]},
    {**base(FAM_PI), "title": "P-orbital orientation and continuity", "capability_refs": [CAP_PI], "solution_structure": ["Assign local sigma framework.", "Inventory remaining p orbitals.", "Check relative p directions.", "Infer geometry/continuity consequence."], "demand_dimensions": {"model_choice": "Orbital arrangement supporting required pi bonds.", "representation_translation": "2D formula to 3D p-orbital orientation.", "reasoning_steps": "Local count, orient, connect, check.", "novelty": "Orthogonal cumulene pi systems and conjugation interruption."}, "safe_variations": ["Compare ethene/allene or conjugated/isolated dienes."], "transfer_boundaries": ["A qualitative overlap sketch does not supply a numerical torsional barrier."], "common_wrong_routes": ["Flatten all multiple-bond systems into an ethene-like plane."], "item_refs": [BANK_IDS[x] for x in ("Q3", "Q4", "Q8", "Q9")]},
    {**base(FAM_LOCAL), "title": "Atom-local hybridisation procedure", "capability_refs": [CAP_LOCAL], "solution_structure": ["Choose one atom.", "Count sigma/lone-pair domains.", "Assign local introductory model.", "Verify leftover p orbitals."], "demand_dimensions": {"model_choice": "Local rather than molecule-wide label.", "representation_translation": "Structure to atom-local domain table.", "reasoning_steps": "Count, assign, verify.", "novelty": "Counterexample-driven repair of an overgeneralised heuristic."}, "safe_variations": ["Apply to propyne, allene, CO2, nitrate or NH3 within the stated introductory model."], "transfer_boundaries": ["Do not use bond equivalence alone as a hybridisation criterion."], "common_wrong_routes": ["Assign one label to the whole molecule or count a triple bond as three local domains."], "item_refs": [BANK_IDS[x] for x in ("Q5", "Q6", "Q10")]},
]


def misconception(wrong: str, diagnostic: str, repair: str) -> dict:
    return {"wrong_idea": wrong, "diagnostic_prompt": diagnostic, "repair": repair}


def microtopic(record_id: str, title: str, cap: str, rep: str, fam: str, steps: list[dict], jump: str, wrong: str, diag: str, repair: str, anchor: str, crux: tuple[str, ...], crux_step: str, exit_prompt: str, exit_summary: str) -> dict:
    row = base(record_id)
    row["extensions"]["grade9v3:learner_metadata"] = {"purpose": "COMPETITION", "learner_profile_ref": "PROFILE-ISS35-HYBRIDISATION-COMPETITION", "provenance": "SIMULATED_OWNER_PRESET"}
    row.update({
        "title": title,
        "bucket_id": BUCKET,
        "primary_capability_ref": cap,
        "intrinsic_badge": "HARD",
        "badge_reason": "The decisive move coordinates more than one representation or atomic centre rather than recalling a label.",
        "entry_assumptions": ["Owner preset: local sp/sp2/sp3 counting, sigma/pi components and elementary p overlap are DEMONSTRATED; multi-centre/representation coordination is UNCERTAIN."],
        "inferential_jump": jump,
        "teaching_path": steps,
        "relation_refs": [],
        "representation_refs": [rep],
        "question_family_refs": [fam],
        "misconceptions": [misconception(wrong, diag, repair)],
        "exit_task": {"prompt": exit_prompt, "source_ref": SRC_OWNER, "answer": model_answer(exit_summary, [repair, "Check the conclusion against the local sigma framework and required p-orbital arrangement."], "The explanation must preserve the stated invariant and the model boundary."), "oracle": {"no_numeric_claim": "Conceptual model/representation task; no numerical oracle required."}},
        "research_contribution": "Issue #35 independent-agent-A round-1 construction derived from Q1-Q10 plus cited model-boundary checks.",
        "prerequisite_refs": [],
        "lineage": [],
        "elicitation": {
            "predict": {"prompt": "Commit to the invariant or next orbital/model move before revealing the explanation.", "defensible_answer": "The prediction must preserve the supplied local geometry and representation invariants."},
            "attempt": {"produces": "A written or selected representation/model correspondence.", "closure": "RUBRIC", "rubric": [{"criterion": "Preserves invariant information and keeps the decisive inference learner-owned until commitment.", "evidence_of": "Representation/model reasoning rather than label recall."}], "accepted": ["Reasoning that preserves local sigma-framework and p-orbital constraints."], "rejected": ["Molecule-wide labels, temporal resonance switching, or unsupported orbital geometry."], "task": {"prompt": "State the invariant and the next model move in your own words.", "givens": [], "representation_ref": rep}},
            "reconstruct": {"route": [{"ask": "What is local and what is invariant across the representation?", "why_this_ask": "Separates atom-local sigma reasoning from multi-centre pi description."}, {"ask": "Which orbital direction or availability must survive the translation?", "why_this_ask": "Prevents surface-feature copying."}], "differs_from_teaching_path": "Reconstruction starts from invariants and works backward from orbital consistency."},
            "boundary_test": {"prompt": "Would the conclusion still follow if the protected invariant or p-orbital requirement were removed?", "answer": "No; the conclusion depends on the stated local geometry/equivalence/orbital requirement.", "confirms": "The learner is using a warrant rather than a memorized label."},
        },
        "construction_units": [{
            "id": "CU-" + record_id,
            "decision": jump,
            "step_refs": [s["id"] for s in steps],
            "representation_ref": rep,
            "reveal_stage_refs": [stage["id"] for stage in next(r["reveal_stages"] for r in representations if r["id"] == rep)],
            "bank_anchor_ref": BANK_IDS[anchor],
            "crux_question_refs": [BANK_IDS[x] for x in crux],
            "crux_step_ref": crux_step,
            "misconception_indexes": [0],
            "independent_checks": [{"statement": "CHECK: " + exit_prompt, "role": "CHECK"}, {"statement": "APPLY: Re-run the same procedure on the paired benchmark example in this family.", "role": "APPLY"}, {"statement": "CONNECT: State separately the local sigma-framework claim and the pi-system claim.", "role": "CONNECT"}],
        }],
        "compact_anchor": {"prompt": title, "result": jump, "representation_ref": rep},
    })
    return row

microtopics = [
    microtopic(MIC_DEL, "From Lewis contributors to one delocalised pi description", CAP_DEL, REP_DEL, FAM_DEL, [
        teaching_step("DELOC-T1", "DECLARE", "Compare all contributors and classify features as invariant or contributor-local.", "Translation must begin from meaning, not line-position copying.", "invariant/contributor-local split"),
        teaching_step("DELOC-T2", "TRANSFORM", "Fix the common planar sigma skeleton.", "All contributors preserve the same connectivity and sigma directions.", "one sigma framework"),
        teaching_step("DELOC-T3", "TRANSFORM", "Orient the relevant p orbitals perpendicular to the planar sigma framework.", "Side-on pi overlap uses an orbital direction distinct from the in-plane sigma framework.", "multi-centre p set"),
        teaching_step("DELOC-T4", "VERIFY", "Construct one delocalised pi description and translate back without switching language.", "The target representation must preserve the supplied equivalent positions and treat contributors as formal components.", "one delocalised description"),
    ], "Separate the invariant sigma framework from contributor-local formal bond/charge placement, then build one delocalised pi model without turning resonance drawings into time states.", "The ion rapidly switches among localized Lewis contributors.", "Which atom positions or sigma bonds would physically change if switching were literal?", "Treat contributors as formal components; preserve one sigma framework and translate pi information into one delocalised description.", "Q2", ("Q1", "Q2", "Q7"), "DELOC-T4", "Three formal contributors share one atomic skeleton. Which features survive into one orbital description?", "Connectivity, overall charge/electron inventory and the sigma skeleton survive; formal localized double-bond/charge placement does not become a time-resolved state."),
    microtopic(MIC_PI, "Coordinate p-orbital directions across several centres", CAP_PI, REP_ALLENE, FAM_PI, [
        teaching_step("PI-T1", "DECLARE", "Assign local sigma frameworks atom by atom.", "Adjacent atoms can legitimately have different local models.", "local labels"),
        teaching_step("PI-T2", "TRANSFORM", "Inventory unhybridised p orbitals left at each relevant centre.", "Pi bonding uses orbitals not consumed by the local sigma framework.", "p-orbital inventory"),
        teaching_step("PI-T3", "TRANSFORM", "Align neighboring p orbitals for every required pi overlap or continuous pathway.", "Side-on overlap requires compatible relative orientation and adjacency.", "overlap map"),
        teaching_step("PI-T4", "VERIFY", "Infer the spatial consequence and test every required pi bond/pathway simultaneously.", "The orbital construction must satisfy all pi requirements at once.", "geometry/continuity consequence"),
    ], "After local sigma-framework counting, use the number and direction of remaining unhybridised p orbitals as a consistency check on the three-dimensional pi system.", "Flatten allene into an ethene-like plane or assume separated double bonds are automatically conjugated.", "How many distinct central p orbitals are required in allene, or is there a p orbital on every bridge atom in the diene?", "Use local p-orbital inventory and orientation/adjacency checks before inferring geometry or conjugation.", "Q3", ("Q3", "Q4", "Q8", "Q9"), "PI-T4", "Allene needs two pi overlaps at its central carbon. What local sigma model and p-orbital arrangement can support both?", "The central carbon is locally sp with two orthogonal unhybridised p orbitals; each overlaps with a terminal p orbital, producing perpendicular terminal CH2 planes."),
    microtopic(MIC_LOCAL, "A reliable atom-local hybridisation procedure", CAP_LOCAL, REP_LOCAL, FAM_LOCAL, [
        teaching_step("LOCAL-T1", "DECLARE", "Choose one atom and list its local sigma-bond directions and lone-pair electron domains.", "A molecule can contain different local environments.", "one local centre"),
        teaching_step("LOCAL-T2", "TRANSFORM", "Count local domains; a multiple bond contributes one sigma direction.", "Electron-domain geometry follows sigma directions/lone-pair domains rather than total bond order.", "domain count"),
        teaching_step("LOCAL-T3", "TRANSFORM", "Map the local count to the introductory sp/sp2/sp3 sigma-framework model.", "The label describes a local orbital model.", "local label"),
        teaching_step("LOCAL-T4", "VERIFY", "Check remaining p orbitals against all required pi bonds/delocalisation and their orientation.", "A label that cannot supply the required pi orbitals is internally inconsistent.", "orbital-consistent assignment"),
    ], "Treat hybridisation as an atom-local sigma-framework model, then verify that enough correctly oriented unhybridised p orbitals remain for the required pi system.", "Assign one hybridisation label to an entire molecule, infer sp2 from equivalent bonds, or count a triple bond as three local domains.", "What are the separate domain counts at each nonequivalent atom, and do the resulting labels leave the required p orbitals?", "Assign locally from the sigma framework, then run an independent p-orbital count/orientation check.", "Q10", ("Q5", "Q6", "Q10"), "LOCAL-T4", "Apply the local procedure to propyne and allene. Does one label fit every carbon?", "No. Propyne is locally sp3/sp/sp; allene is sp2/sp/sp2, and those assignments leave the p orbitals required by their pi bonds."),
]

package = {
    "schema_version": "0.2.0",
    "package_id": "EVIDENCE-LIB-CHEM-ISS35-HYB",
    "title": "Hybridisation and pi-system reasoning — Issue #35 independent candidate",
    "version": "0.1.0",
    "status": "CANDIDATE",
    "subject": "Chemistry",
    "scope_summary": "Issue #35 Grade-11 competition-preparation specimen: local introductory hybridisation, p-orbital orientation and Lewis-contributor to delocalised-pi translation. Owner-supplied benchmark questions remain separate verbatim custody; external references support model boundaries only.",
    "curriculum_mappings": [],
    "resources": resources,
    "buckets": [bucket],
    "capabilities": capabilities,
    "microtopics": microtopics,
    "relations": [],
    "representations": representations,
    "question_families": families,
    "questions": [],
    "teaching_routes": [],
    "practice_profiles": [],
    "evidence": [],
    "known_issues": [],
    "extensions": {"grade9v3:authoring_specimen": {"issue": 35, "agent": "A", "round": 1, "purpose": "COMPETITION", "learner_profile_ref": "PROFILE-ISS35-HYBRIDISATION-COMPETITION", "qrt_evidence": "evidence/benchmark/ISS35/generated/qrt-review.v1.json", "launch_commit": "e01c6365acfd6aec84c0a6e94f11b683bd961f6e", "independence": "Issue #36 not inspected before candidate freeze"}},
    "data": [],
}

# Build the owner-supplied bank through the repository's custody helper; then fill agent-owned fields.
intake = {
    "status": "READY",
    "intake_digest": "sha256:cc448399f7c44781f8e3ca659aaa96da8b9fde5edc7a66625b45729f728a29d5",
    "inputs": {"questions": [{"id": qid, "label": qid[1:], "text": STEMS[qid]} for qid in STEMS]},
}
bank = owner_bank.new(intake, "iss35-hyb")

for qid, row in zip(STEMS, bank["questions"]):
    evidence = by_qid[qid]
    row["id"] = evidence["stable_id"]
    row["original_identifier"] = qid
    row["primary_capability_ref"] = evidence["capability_ref"]
    row["secondary_capability_refs"] = []
    row["family_ref"] = evidence["family_ref"]
    row["conditions"] = []
    row["figure_refs"] = [evidence["representation_ref"]]
    move_rows = []
    for number, (kind, action, why, output) in enumerate(evidence["solution_route"], 1):
        move_rows.append({"id": f"{row['id']}-MOVE-{number}", "kind": kind, "action": action, "why_valid": why, "inputs": ["supplied benchmark stem and prior move"], "output": output})
    row["answer"] = {
        "kind": "MODEL_RESPONSE",
        "summary": evidence["verified_answer"],
        "reasoning_route": move_rows,
        "crux_move_ref": move_rows[-1]["id"],
        "check": evidence["independent_check"],
        "verification_status": "INDEPENDENTLY_CHECKED",
    }
    stages = ["KEY_CONCEPT", "REPRESENTATION", "FIRST_MOVE", "FORMAL_MODEL", "CHECKPOINT"]
    kinds = ["CONNECT", "REPRESENT", "CONNECT", "EXECUTE", "EXECUTE"]
    row["scaffolds"] = [{"text": text, "support_kind": kinds[min(i, 4)], "reveals": "CONCEPT" if i == 0 else "METHOD", "learner_stage": stages[min(i, 4)], "supports_move_ref": move_rows[min(i, len(move_rows) - 1)]["id"]} for i, text in enumerate(evidence["hints"])]
    analysis = row["extensions"].setdefault("grade9v3:analysis", {})
    analysis["learner_question_type"] = "constructed_response"
    analysis["difficulty"] = evidence["difficulty"]
    analysis["common_wrong_route"] = evidence["misconception"]["M1"]
    analysis["expected_time_seconds"] = 240 if evidence["difficulty"]["band"] == "D3" else 150
    analysis["cognitive_demand"] = evidence["demand"]
    analysis["stable_crux_move"] = evidence["Z"]
    analysis["topic"] = "Chemical Bonding and Molecular Structure"
    analysis["concept_bucket"] = BUCKET
    row["extensions"]["grade9v3:benchmark_authorship"] = {"custody_class": "OWNER_SUPPLIED_RAW_INPUT", "drafted_by": "COORDINATING_AGENT", "personally_authored_by_owner": False, "official_exam_or_pyq": False}
    row["extensions"].setdefault("grade9v3:component_waivers", {})["CONDITIONS"] = "The supplied benchmark stem already states its material conditions; no extra condition is added to the verbatim task."
    row["extensions"]["grade9v3:math_spans"] = []
    row.pop("hints", None)
    row.pop("hint_ladder", None)

manifest = {
    "schema": "product-manifest/v1",
    "product_id": "EVIDENCE-CHEM-ISS35-HYB-A",
    "subject": "Chemistry",
    "home_href": "../../../index.html",
    "question_bank_href": "../../../question-bank/index.html",
    "package_refs": ["evidence/benchmark/ISS35/generated/package.v1.json"],
    "bank_refs": ["evidence/benchmark/ISS35/generated/owner.bank.json"],
    "output_roles": ["CORE1A", "CORE2"],
    "selection": {"microtopics": [MIC_DEL, MIC_PI, MIC_LOCAL], "core2": [BANK_IDS[f"Q{i}"] for i in range(1, 11)], "core2a": [], "core2b": []},
}

qrt = {
    "schema": "issue35-qrt-authoring-evidence/v1",
    "status": "AUTHORED_NOT_RENDER_VERIFIED",
    "repository": "reallaksh19/Grade9v3.5",
    "issue": 35,
    "agent": "A",
    "round": 1,
    "subject": "Chemistry",
    "grade": 11,
    "topic": "Chemical bonding and hybridisation",
    "source_status": "OWNER_SUPPLIED_COORDINATING_AGENT_DRAFT",
    "controlled_inputs": {"launch_commit": LEDGER["launch_commit"], "core_prompt_sha256": LEDGER["core_prompt_sha256"], "blueprint_registry": "1.9.0", "core1a_blueprint": "BP-CORE1A-CONSTRUCTION@1.4.0", "core2_blueprint": "BP-CORE2-SOURCE-QUESTION@1.5.0", "question_demand_matrix": "question-demand-matrix/v1@1.0.0"},
    "learner_profile": LEDGER["learner_profile"],
    "hardest_target": LEDGER["hardest_target"],
    "matrix_coverage": LEDGER["matrix_coverage"],
    "items": [{key: row[key] for key in ("question_id", "stable_id", "difficulty", "demand", "qrt_cell", "X", "Y", "Z", "W", "verified_answer", "hints", "misconception", "independent_check")} for row in LEDGER["items"]],
}

OUT.mkdir(parents=True, exist_ok=True)
(OUT / "package.v1.json").write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "owner.bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "product.manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
(OUT / "qrt-review.v1.json").write_text(json.dumps(qrt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print(f"wrote {OUT}")
