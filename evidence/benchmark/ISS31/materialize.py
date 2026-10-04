#!/usr/bin/env python3
"""Materialize Issue #31 Chemistry hybridisation canonical inputs from frozen benchmark evidence.

The owner-bank skeleton MUST be created first by Shared/tools/owner_bank.py new.
This script fills authored fields without changing any stem or source-custody digest,
writes the Chemistry package and local SVG assets, and leaves manifest derivation to
Shared/tools/product_manifest.py in the cold-run workflow.
"""
from __future__ import annotations

import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
LEDGER = json.loads((HERE / "question-ledger.json").read_text(encoding="utf-8"))
BANK_PATH = REPO / "Chemistry/library/owner-bank/issue31-hybridisation.json"
PACKAGE_PATH = REPO / "Chemistry/library/chem-g11-hybridisation.v1.json"
FIG_DIR = REPO / "Chemistry/library/figures"

SRC_OWNER = "SRC-CHEM-ISS31-OWNER"
SRC_VSEPR = "SRC-CHEM-OPENSTAX-VSEPR-HYBRID"
SRC_SIGPI = "SRC-CHEM-OPENSTAX-SIGMA-PI"
BUCKET = "BUCKET-CHEM-G11-HYBRIDISATION"

CAPS = {
    "CAP-CHEM-G11-SP3-HYBRID-SET": (
        "Connect a stated electron-domain count to the introductory hybrid-orbital set size",
        "Explain that sp3 combines one s and three p orbitals to form four hybrid orbitals."
    ),
    "CAP-CHEM-G11-ELECTRON-DOMAIN-COUNT": (
        "Count electron-density regions locally around a chosen central atom",
        "Count each bonded neighbour as one region regardless of bond order and include only lone pairs on the chosen centre."
    ),
    "CAP-CHEM-G11-DOMAIN-TO-HYBRID-GEOMETRY": (
        "Map electron-domain count to introductory sp2/sp3 hybridisation and electron-domain geometry",
        "Map 3 regions to sp2/trigonal planar and 4 regions to sp3/tetrahedral without reading a flat Lewis layout as shape."
    ),
    "CAP-CHEM-G11-LEWIS-TO-3D-DOMAINS": (
        "Translate a 2D Lewis structure into a three-dimensional electron-domain arrangement",
        "Represent four electron domains tetrahedrally and distinguish electron-domain geometry from atom-only molecular geometry."
    ),
    "CAP-CHEM-G11-VSEPR-GEOMETRY": (
        "Use VSEPR to predict overall electron-domain and molecular geometry",
        "Use the central-atom domain inventory to distinguish tetrahedral electron-domain geometry from trigonal-pyramidal NH3 molecular geometry."
    ),
    "CAP-CHEM-G11-MODEL-SCOPE-VSEPR-VB": (
        "Select VSEPR or an orbital-overlap description according to the explanatory job",
        "Choose VSEPR for overall domain arrangement and state that orbital composition/overlap detail belongs to a valence-bond description."
    ),
    "CAP-CHEM-G11-SIGMA-PI-OVERLAP": (
        "Classify sigma and pi overlap from orbital orientation relative to the internuclear axis",
        "Identify end-on axial overlap as sigma and side-on overlap with a nodal plane through the axis as pi."
    ),
}

REL_DOMAIN = "REL-CHEM-HYB-DOMAIN-COUNT"
REL_HYBRID = "REL-CHEM-HYB-DOMAIN-HYBRID"
REL_3D = "REL-CHEM-HYB-LEWIS-3D"
REL_MODEL = "REL-CHEM-HYB-MODEL-SCOPE"
REL_SIGPI = "REL-CHEM-HYB-SIGMA-PI"

REP_DOMAIN = "REP-CHEM-HYB-DOMAIN-COUNT"
REP_HYBRID = "REP-CHEM-HYB-HYBRID-SETS"
REP_TETRA_CH4 = "REP-CHEM-HYB-CH4-TETRAHEDRAL"
REP_TETRA_NH3 = "REP-CHEM-HYB-NH3-DOMAINS"
REP_VSEPR = "REP-CHEM-HYB-VSEPR-GEOMETRY"
REP_MODEL = "REP-CHEM-HYB-MODEL-SCOPE"
REP_SIGPI = "REP-CHEM-HYB-SIGMA-PI"
REP_WEDGE = "REP-CHEM-HYB-WEDGE-DASH"

FAM_DOMAIN = "FAM-CHEM-HYB-DOMAINS"
FAM_3D = "FAM-CHEM-HYB-3D"
FAM_MODEL = "FAM-CHEM-HYB-MODEL-SCOPE"
FAM_SIGPI = "FAM-CHEM-HYB-SIGMA-PI"

Q_META = {
    "Q1": (REL_HYBRID, REP_HYBRID, FAM_DOMAIN, "Hybrid set size from four directions"),
    "Q2": (REL_DOMAIN, REP_DOMAIN, FAM_DOMAIN, "Multiple bond as one electron domain"),
    "Q3": (REL_HYBRID, REP_TETRA_CH4, FAM_DOMAIN, "Four domains to sp3 and tetrahedral geometry"),
    "Q4": (REL_3D, REP_TETRA_NH3, FAM_3D, "NH3: four domains in three dimensions"),
    "Q5": (REL_MODEL, REP_MODEL, FAM_MODEL, "Choose the model that answers the question"),
    "Q6": (REL_SIGPI, REP_SIGPI, FAM_SIGPI, "Sigma versus pi overlap geometry"),
    "Q7": (REL_3D, REP_WEDGE, FAM_3D, "Wedge/dash methane as a 3D tetrahedron"),
    "Q8": (REL_DOMAIN, REP_DOMAIN, FAM_DOMAIN, "Central-atom scope in NF3"),
    "Q9": (REL_DOMAIN, REP_DOMAIN, FAM_DOMAIN, "Diagnose double-bond domain overcounting"),
    "Q10": (REL_HYBRID, REP_HYBRID, FAM_DOMAIN, "Match domain count to sp2/sp3 set size"),
}


def base(record_id: str, source_refs: list[str] | None = None) -> dict:
    return {
        "id": record_id,
        "version": "0.1.0",
        "status": "CANDIDATE",
        "source_refs": list(source_refs or []),
        "evidence_refs": [],
        "extensions": {},
    }


def step(step_id: str, role: str, action: str, why: str, output: str) -> dict:
    return {
        "id": step_id,
        "role": role,
        "action": action,
        "why_valid": why,
        "inputs": [],
        "output": output,
    }


def model_answer(summary: str, reasoning: list[str], check: str) -> dict:
    return {
        "kind": "MODEL_RESPONSE",
        "summary": summary,
        "reasoning": reasoning,
        "check": check,
        "acceptable_alternatives": [],
        "subpart_answers": [],
        "verification_status": "INDEPENDENTLY_CHECKED",
    }


def resource(record_id: str, title: str, origin: str, locator: str, section: str,
             roles: list[str], supports: list[str], reason: str) -> dict:
    return {
        **base(record_id),
        "title": title,
        "origin": origin,
        "locator": locator,
        "edition": "checked 2026-10-04",
        "section": section,
        "last_checked": "2026-10-04",
        "access_status": "FULL_ITEM_INSPECTED",
        "rights_status": "Owner-supplied benchmark text or openly accessible educational source; no official-exam identity is claimed.",
        "snapshot_ref": None,
        "snapshot_digest": None,
        "role": roles,
        "supports_claims": supports,
        "entry_capabilities": [],
        "depth": ["FOUNDATION", "COMPETITION"],
        "selection_reason": reason,
        "fallback": [],
    }


def relation(record_id: str, expression: str, meaning: str, symbols: list[dict],
             conditions: list[str], derivation: list[dict], limits: list[str],
             checks: list[str], source: str) -> dict:
    return {
        **base(record_id, [source]),
        "expression": expression,
        "meaning": meaning,
        "symbols": symbols,
        "conditions": conditions,
        "derivation": derivation,
        "limits": limits,
        "checks": checks,
        "gate_relation_ref": record_id,
    }


def representation(record_id: str, kind: str, purpose: str, asset: str,
                   relation_refs: list[str], stages: list[tuple[str, str, str]],
                   correspondence: list[dict], source: str) -> dict:
    return {
        **base(record_id, [source]),
        "kind": kind,
        "purpose": purpose,
        "required_elements": [label for _, label, _ in stages],
        "relation_refs": relation_refs,
        "read_order": [job for _, _, job in stages],
        "instance_constraints": [
            "The pre-attempt view must orient the learner without printing the final answer.",
            "Labels must preserve electron-domain, molecular-geometry and orbital-overlap distinctions."
        ],
        "accessibility": [
            "The SVG has an accessible title and description.",
            "Text labels duplicate any depth, axis or overlap cue."
        ],
        "misleading_alternatives": [
            "Treating a flat Lewis layout as the three-dimensional geometry.",
            "Treating bond-order lines as separate VSEPR directions."
        ],
        "rendered_asset_refs": [asset],
        "scene_instances": [],
        "correspondence": correspondence,
        "reveal_stages": [
            {"id": sid, "label": label, "purpose": job, "visible_elements": [label]}
            for sid, label, job in stages
        ],
        "extensions": {"grade9v3:stage_mode": "CUMULATIVE"},
    }


def family(record_id: str, title: str, capability_refs: list[str], wrong: str,
           boundary: str) -> dict:
    return {
        **base(record_id, [SRC_VSEPR]),
        "title": title,
        "capability_refs": capability_refs,
        "solution_structure": [
            "Identify the central atom, requested representation or overlap reference axis.",
            "Apply the smallest relevant domain/model rule.",
            "State the result and check it against the named misconception."
        ],
        "demand_dimensions": {
            "model_choice": "Choose the representation/model that directly answers the requested quantity.",
            "representation_translation": "Translate Lewis, wedge/dash, domain or orbital-overlap information without conflating levels.",
            "reasoning_steps": "Represent, decide, verify.",
            "novelty": boundary,
        },
        "safe_variations": [
            "Change the molecule while preserving the same central-domain or overlap structure.",
            "Change the representation while preserving the same explanatory job."
        ],
        "transfer_boundaries": [boundary],
        "common_wrong_routes": [wrong],
        "item_refs": [],
    }


def friendly_microtopic(ref: str) -> str:
    return {
        "MIC-CHEM-G11-HYBRID-SET-SIZE": "Hybrid set size",
        "MIC-CHEM-G11-CENTRAL-DOMAIN-COUNT": "Count central electron domains",
        "MIC-CHEM-G11-FOUR-DOMAIN-MAPPING": "Four domains to sp3 and tetrahedral geometry",
        "MIC-CHEM-G11-LEWIS-TO-TETRAHEDRAL-DOMAINS": "Lewis structure to tetrahedral domain arrangement",
        "MIC-CHEM-G11-MODEL-SCOPE-SELECTION": "Choose a model by explanatory scope",
        "MIC-CHEM-G11-SIGMA-PI-GEOMETRY": "Sigma and pi overlap geometry",
        "MIC-CHEM-G11-TETRAHEDRAL-WEDGE-DASH": "Wedge/dash tetrahedral methane",
        "MIC-CHEM-G11-CENTRAL-ATOM-SCOPE": "Central-atom scope",
        "MIC-CHEM-G11-MULTIPLE-BOND-DOMAIN": "Multiple bond as one domain",
        "MIC-CHEM-G11-SP2-SP3-DOMAIN-MAP": "sp2/sp3 domain map",
    }[ref]


def source_for_question(qid: str) -> str:
    return SRC_SIGPI if qid == "Q6" else SRC_VSEPR


def microtopic(q: dict, bank_id: str) -> dict:
    qid = q["original_identifier"]
    relation_ref, rep_ref, family_ref, _ = Q_META[qid]
    sid = qid.replace("Q", "HYB-T")
    source = source_for_question(qid)
    steps = [
        step(f"{sid}-1", "DECLARE",
             f"State the governing distinction for {friendly_microtopic(q['microtopic_ref'])}.",
             "The learner needs a stable conceptual rule before translating a diagram or choosing a model.",
             "governing rule"),
        step(f"{sid}-2", "TRANSFORM",
             q["qrt"]["replacement_rule"],
             "This directly repairs the recorded misconception while preserving the question's requested representation level.",
             "correctly transformed representation or model choice"),
        step(f"{sid}-3", "VERIFY",
             "Check the conclusion against the central-atom scope, domain count, three-dimensional geometry or overlap-axis invariant.",
             "The check is independent of merely repeating the final answer.",
             "verified conclusion"),
    ]
    stage_ids = {
        REP_DOMAIN: ["DOM-1", "DOM-2", "DOM-3"],
        REP_HYBRID: ["HYB-1", "HYB-2", "HYB-3"],
        REP_TETRA_CH4: ["CH4-1", "CH4-2", "CH4-3"],
        REP_TETRA_NH3: ["NH3-1", "NH3-2", "NH3-3"],
        REP_VSEPR: ["VG-1", "VG-2", "VG-3"],
        REP_MODEL: ["MOD-1", "MOD-2", "MOD-3"],
        REP_SIGPI: ["SIG-1", "SIG-2", "SIG-3"],
        REP_WEDGE: ["WD-1", "WD-2", "WD-3"],
    }[rep_ref]
    return {
        **base(q["microtopic_ref"], [source]),
        "title": friendly_microtopic(q["microtopic_ref"]),
        "bucket_id": BUCKET,
        "primary_capability_ref": q["primary_capability_ref"],
        "intrinsic_badge": "MEDIUM",
        "badge_reason": q["difficulty"]["basis"],
        "entry_assumptions": [
            "Can read supplied atoms, single/double/triple bonds, and shared versus lone pairs in a simple Lewis structure."
        ],
        "inferential_jump": q["qrt"]["replacement_rule"],
        "teaching_path": steps,
        "relation_refs": [relation_ref],
        "representation_refs": [rep_ref],
        "question_family_refs": [family_ref],
        "misconceptions": [{
            "wrong_idea": q["qrt"]["wrong_idea"],
            "diagnostic_prompt": q["qrt"]["X"],
            "repair": q["qrt"]["replacement_rule"],
        }],
        "exit_task": {
            "prompt": f"Explain the rule behind {friendly_microtopic(q['microtopic_ref']).lower()} without copying the benchmark answer.",
            "source_ref": source,
            "answer": model_answer(
                q["qrt"]["replacement_rule"],
                [q["qrt"]["replacement_rule"], "Use the relevant representation/model boundary to justify the rule."],
                "The explanation must reject the recorded wrong idea for the same reason."
            ),
            "oracle": {"no_numeric_claim": "This exit task checks the conceptual rule rather than a memorized number."},
        },
        "research_contribution": f"Issue #31 {qid} and the cited OpenStax source isolate this decision as a learner-facing construction target.",
        "prerequisite_refs": [],
        "lineage": [],
        "elicitation": {
            "predict": {
                "prompt": f"Before revealing the rule, what would you use to decide {q['qrt']['X']}?",
                "defensible_answer": q["qrt"]["Z"],
            },
            "attempt": {
                "produces": "A one-sentence rule or labelled representation.",
                "closure": "RUBRIC",
                "rubric": [{"criterion": "Uses the correct representation/model distinction.", "evidence_of": q["qrt"]["replacement_rule"]}],
                "accepted": [q["qrt"]["replacement_rule"]],
                "rejected": [q["qrt"]["wrong_idea"]],
                "task": {
                    "prompt": f"Apply the rule to the benchmark anchor {qid} but stop before copying its final answer.",
                    "givens": ["Use the owner-supplied benchmark stem verbatim as the anchor."],
                    "representation_ref": rep_ref,
                },
            },
            "reconstruct": {
                "route": [
                    {"ask": q["qrt"]["Z"], "why_this_ask": "This is the smallest rule that protects the crux."},
                    {"ask": "What would falsify the tempting wrong route?", "why_this_ask": "A boundary check makes the rule transferable."},
                ],
                "differs_from_teaching_path": "The learner starts from a prediction and misconception test rather than receiving the conclusion first.",
            },
            "boundary_test": {
                "prompt": "What changes would make this rule or model choice no longer answer the same question?",
                "answer": "A changed central atom, requested representation level or overlap/model target can require a different count or model.",
                "confirms": "The rule is scoped to the chosen centre and explanatory job.",
            },
        },
        "construction_units": [{
            "id": f"CU-{qid}-ISS31",
            "decision": q["qrt"]["Z"],
            "step_refs": [s["id"] for s in steps],
            "representation_ref": rep_ref,
            "reveal_stage_refs": stage_ids,
            "bank_anchor_ref": bank_id,
            "crux_question_refs": [bank_id],
            "crux_step_ref": steps[1]["id"],
            "misconception_indexes": [0],
            "independent_checks": [
                {"statement": "CHECK: State the relevant invariant without using the final answer.", "role": "CHECK"},
                {"statement": "APPLY: Use the same rule on a nearby molecule or representation.", "role": "APPLY"},
                {"statement": "CONNECT: Explain which representation/model level the rule belongs to.", "role": "CONNECT"},
            ],
        }],
        "compact_anchor": {
            "prompt": q["qrt"]["X"],
            "result": q["qrt"]["replacement_rule"],
            "representation_ref": rep_ref,
        },
    }


def svg(title: str, desc: str, body: str) -> str:
    return f"""<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 760 400" role="img" aria-labelledby="title desc">
<title id="title">{title}</title>
<desc id="desc">{desc}</desc>
<rect x="1" y="1" width="758" height="398" rx="18" fill="white" stroke="currentColor"/>
{body}
</svg>
"""


def write_assets() -> dict[str, str]:
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    assets = {
        "issue31-domain-count.svg": svg(
            "Electron-domain counting",
            "A central atom with three distinct neighbour directions; a double bond remains one direction.",
            '<g data-g9-stage-id="DOM-1"><circle cx="270" cy="200" r="34" fill="none" stroke="currentColor" stroke-width="3"/><text x="255" y="207" font-size="24">C</text><text x="210" y="55" font-size="22">Choose the counting centre</text></g>'
            '<g data-g9-stage-id="DOM-2"><line x1="304" y1="200" x2="430" y2="200" stroke="currentColor" stroke-width="3"/><line x1="307" y1="210" x2="430" y2="210" stroke="currentColor" stroke-width="3"/><line x1="245" y1="175" x2="170" y2="95" stroke="currentColor" stroke-width="3"/><line x1="245" y1="225" x2="170" y2="305" stroke="currentColor" stroke-width="3"/><text x="445" y="208" font-size="22">O — one direction</text><text x="130" y="90" font-size="22">H</text><text x="130" y="325" font-size="22">H</text></g>'
            '<g data-g9-stage-id="DOM-3"><text x="170" y="365" font-size="20">Count local directions/regions, not bond lines or neighbour lone pairs.</text></g>'
        ),
        "issue31-hybrid-sets.svg": svg(
            "Hybrid set size",
            "Three directions map to sp2 and four directions map to sp3; hybrid set size equals direction count.",
            '<g data-g9-stage-id="HYB-1"><text x="155" y="55" font-size="26">Start with direction count</text><text x="110" y="105" font-size="24">3 directions</text><text x="500" y="105" font-size="24">4 directions</text></g>'
            '<g data-g9-stage-id="HYB-2"><circle cx="210" cy="205" r="25" fill="none" stroke="currentColor" stroke-width="3"/><line x1="210" y1="180" x2="210" y2="120" stroke="currentColor" stroke-width="3"/><line x1="190" y1="220" x2="120" y2="270" stroke="currentColor" stroke-width="3"/><line x1="230" y1="220" x2="300" y2="270" stroke="currentColor" stroke-width="3"/><text x="160" y="325" font-size="26">sp²</text><circle cx="535" cy="205" r="25" fill="none" stroke="currentColor" stroke-width="3"/><line x1="535" y1="180" x2="535" y2="120" stroke="currentColor" stroke-width="3"/><line x1="510" y1="210" x2="430" y2="245" stroke="currentColor" stroke-width="3"/><line x1="560" y1="210" x2="640" y2="245" stroke="currentColor" stroke-width="3"/><line x1="535" y1="230" x2="535" y2="315" stroke="currentColor" stroke-width="3"/><text x="500" y="350" font-size="26">sp³</text></g>'
            '<g data-g9-stage-id="HYB-3"><text x="115" y="385" font-size="20">sp² = 3 hybrids; sp³ = 4 hybrids. Set size equals the modelled directions.</text></g>'
        ),
        "issue31-ch4-tetrahedral.svg": svg(
            "Methane four-domain mapping",
            "Four bonding domains around carbon build a tetrahedral electron-domain arrangement.",
            '<g data-g9-stage-id="CH4-1"><text x="315" y="205" font-size="30">C</text><text x="220" y="55" font-size="22">4 C–H bonding domains</text></g>'
            '<g data-g9-stage-id="CH4-2"><line x1="330" y1="180" x2="330" y2="90" stroke="currentColor" stroke-width="4"/><line x1="310" y1="210" x2="190" y2="285" stroke="currentColor" stroke-width="4"/><polygon points="350,205 525,145 490,195" fill="none" stroke="currentColor" stroke-width="4"/><line x1="350" y1="225" x2="485" y2="320" stroke="currentColor" stroke-width="3" stroke-dasharray="9 7"/><text x="315" y="75" font-size="22">H</text><text x="160" y="310" font-size="22">H</text><text x="540" y="145" font-size="22">H</text><text x="500" y="340" font-size="22">H</text></g>'
            '<g data-g9-stage-id="CH4-3"><text x="170" y="380" font-size="21">4 domains → sp³ model → tetrahedral electron-domain geometry (~109.5° ideal).</text></g>'
        ),
        "issue31-nh3-domains.svg": svg(
            "Ammonia four electron domains",
            "Nitrogen with three bonding domains and one lone-pair domain arranged tetrahedrally.",
            '<g data-g9-stage-id="NH3-1"><text x="345" y="210" font-size="30">N</text><text x="205" y="55" font-size="22">3 N–H domains + 1 lone-pair domain</text></g>'
            '<g data-g9-stage-id="NH3-2"><line x1="365" y1="185" x2="365" y2="80" stroke="currentColor" stroke-width="4"/><text x="325" y="65" font-size="21">lone pair</text><line x1="345" y1="210" x2="210" y2="275" stroke="currentColor" stroke-width="4"/><polygon points="385,210 535,150 505,195" fill="none" stroke="currentColor" stroke-width="4"/><line x1="380" y1="225" x2="505" y2="310" stroke="currentColor" stroke-width="3" stroke-dasharray="9 7"/><text x="180" y="300" font-size="22">H</text><text x="550" y="150" font-size="22">H</text><text x="520" y="330" font-size="22">H</text></g>'
            '<g data-g9-stage-id="NH3-3"><text x="125" y="380" font-size="20">Electron-domain geometry: tetrahedral. Atom-only NH₃ molecular geometry: trigonal pyramidal.</text></g>'
        ),
        "issue31-vsepr-geometry.svg": svg(
            "VSEPR geometry naming",
            "The same NH3 domain inventory is used to distinguish electron-domain geometry from molecular geometry.",
            '<g data-g9-stage-id="VG-1"><text x="80" y="80" font-size="26">Count all four electron domains around N</text><text x="310" y="155" font-size="28">NH₃ + lone pair</text></g>'
            '<g data-g9-stage-id="VG-2"><text x="80" y="235" font-size="24">Electron-domain geometry</text><text x="470" y="235" font-size="24">tetrahedral</text></g>'
            '<g data-g9-stage-id="VG-3"><text x="80" y="315" font-size="24">Molecular geometry (atoms only)</text><text x="470" y="315" font-size="24">trigonal pyramidal</text><text x="135" y="370" font-size="19">Lone-pair direction counts for EDG but is omitted from the atom-only molecular shape name.</text></g>'
        ),
        "issue31-model-scope.svg": svg(
            "Which model answers this question?",
            "A two-lens comparison between VSEPR and orbital-overlap descriptions for ammonia.",
            '<g data-g9-stage-id="MOD-1"><text x="130" y="70" font-size="25">Q5 asks for overall 3D electron-domain arrangement</text></g>'
            '<g data-g9-stage-id="MOD-2"><line x1="380" y1="95" x2="380" y2="335" stroke="currentColor" stroke-width="2"/><text x="90" y="130" font-size="30">VSEPR lens</text><text x="60" y="180" font-size="20">4 domains → tetrahedral domain geometry</text><text x="60" y="220" font-size="20">NH₃ atoms → trigonal pyramidal</text></g>'
            '<g data-g9-stage-id="MOD-3"><text x="455" y="130" font-size="30">Orbital-overlap lens</text><text x="420" y="180" font-size="20">Orbital composition and overlap detail</text><text x="420" y="220" font-size="20">Useful, but more detail than Q5 requests</text><text x="180" y="365" font-size="22">Choose by explanatory job, not chapter keyword.</text></g>'
        ),
        "issue31-sigma-pi.svg": svg(
            "Sigma and pi overlap",
            "End-on overlap lies along the internuclear axis; side-on overlap lies on opposite sides of the axis.",
            '<g data-g9-stage-id="SIG-1"><line x1="70" y1="200" x2="700" y2="200" stroke="currentColor" stroke-width="2" stroke-dasharray="6 6"/><text x="260" y="185" font-size="20">internuclear axis</text></g>'
            '<g data-g9-stage-id="SIG-2"><ellipse cx="160" cy="120" rx="70" ry="35" fill="none" stroke="currentColor" stroke-width="3"/><ellipse cx="240" cy="120" rx="70" ry="35" fill="none" stroke="currentColor" stroke-width="3"/><text x="105" y="75" font-size="24">σ: end-on along axis</text></g>'
            '<g data-g9-stage-id="SIG-3"><ellipse cx="510" cy="120" rx="35" ry="65" fill="none" stroke="currentColor" stroke-width="3"/><ellipse cx="620" cy="120" rx="35" ry="65" fill="none" stroke="currentColor" stroke-width="3"/><ellipse cx="510" cy="280" rx="35" ry="65" fill="none" stroke="currentColor" stroke-width="3"/><ellipse cx="620" cy="280" rx="35" ry="65" fill="none" stroke="currentColor" stroke-width="3"/><text x="455" y="380" font-size="22">π: side-on; nodal plane contains axis</text></g>'
        ),
        "issue31-wedge-dash.svg": svg(
            "Methane wedge and dash",
            "Carbon with two bonds in plane, one solid wedge toward the viewer and one dashed bond behind the plane.",
            '<g data-g9-stage-id="WD-1"><text x="365" y="210" font-size="30">C</text><line x1="360" y1="195" x2="250" y2="120" stroke="currentColor" stroke-width="3"/><text x="220" y="110" font-size="24">H</text><line x1="390" y1="195" x2="500" y2="120" stroke="currentColor" stroke-width="3"/><text x="515" y="110" font-size="24">H</text></g>'
            '<g data-g9-stage-id="WD-2"><polygon points="355,220 235,315 325,245" fill="none" stroke="currentColor" stroke-width="4"/><text x="195" y="340" font-size="24">H toward</text><line x1="400" y1="225" x2="520" y2="315" stroke="currentColor" stroke-width="4" stroke-dasharray="10 8"/><text x="530" y="340" font-size="24">H behind</text></g>'
            '<g data-g9-stage-id="WD-3"><text x="180" y="385" font-size="20">Wedge/dash encodes non-coplanar tetrahedral depth (~109.5° ideal), not a flat 90° cross.</text></g>'
        ),
    }
    for name, content in assets.items():
        (FIG_DIR / name).write_text(content, encoding="utf-8")
    return {name: f"Chemistry/library/figures/{name}" for name in assets}


def build_package(asset_refs: dict[str, str], bank_ids: dict[str, str]) -> dict:
    all_caps = list(CAPS)
    resources = [
        resource(SRC_OWNER, "Issue #31 owner-supplied Grade 11 hybridisation benchmark", "AUTHORED",
                 "https://github.com/reallaksh19/Grade9v3.5/issues/31",
                 "A/B/C and Q1-Q10 owner-supplied benchmark input", ["QUESTION_BANK", "AUTHOR_CREATED"], [],
                 "Custody surface for the exact benchmark questions; not an official exam/PYQ source."),
        resource(SRC_VSEPR, "OpenStax Chemistry 2e — Molecular Structure and Polarity; Hybrid Atomic Orbitals", "WEB",
                 "https://openstax.org/books/chemistry-2e/pages/7-6-molecular-structure-and-polarity",
                 "VSEPR electron-density regions and introductory hybrid atomic orbitals", ["SCIENTIFIC_CHECK", "EXPLANATION"],
                 [c for c in all_caps if c != "CAP-CHEM-G11-SIGMA-PI-OVERLAP"],
                 "Supports electron-domain counting, VSEPR geometry, sp2/sp3 set size and model-scope boundaries used by Q1-Q5 and Q7-Q10."),
        resource(SRC_SIGPI, "OpenStax Chemistry: Atoms First 2e — Valence Bond Theory; Multiple Bonds", "WEB",
                 "https://openstax.org/books/chemistry-atoms-first-2e/pages/5-3-multiple-bonds",
                 "Sigma/pi overlap and multiple-bond geometry", ["SCIENTIFIC_CHECK", "EXPLANATION"],
                 ["CAP-CHEM-G11-SIGMA-PI-OVERLAP", "CAP-CHEM-G11-ELECTRON-DOMAIN-COUNT"],
                 "Supports sigma/pi overlap geometry and the distinction between bond components and VSEPR directions."),
    ]

    capabilities = [{
        **base(cid, [SRC_SIGPI if cid == "CAP-CHEM-G11-SIGMA-PI-OVERLAP" else SRC_VSEPR]),
        "action": action, "success_criterion": criterion, "prerequisite_refs": [],
        "curriculum_mappings": [], "external_provider": None, "acceptance_status": "CANDIDATE",
    } for cid, (action, criterion) in CAPS.items()]

    relations = [
        relation(REL_DOMAIN,
                 "electron-domain count = bonded-neighbour regions + lone-pair regions on the chosen central atom",
                 "VSEPR domain counting is local to the selected centre. A single, double or triple bond to one neighbour occupies one region/direction.",
                 [{"symbol": "N_domain", "meaning": "number of electron-density regions around the selected central atom", "unit_or_domain": "non-negative integer"}],
                 ["Choose the central atom before counting.", "Treat each bonded neighbour as one region regardless of bond order."],
                 [step("DOM-R1", "DECLARE", "Choose the central atom.", "The count is local to one centre.", "counting centre"),
                  step("DOM-R2", "TRANSFORM", "Count each bonded neighbour once and add lone pairs on that centre.", "VSEPR counts regions of electron density, not drawn bond lines.", "domain count"),
                  step("DOM-R3", "VERIFY", "Check that neighbour lone pairs were excluded.", "They belong to domains centred on those neighbours.", "verified local count")],
                 ["Do not count lone pairs on terminal atoms when the question asks for domains around the central atom."],
                 ["A double bond to one neighbour must not create a second direction."], SRC_VSEPR),
        relation(REL_HYBRID,
                 "3 electron-domain directions ↔ sp2 ↔ 3 hybrids; 4 directions ↔ sp3 ↔ 4 hybrids",
                 "In the introductory valence-bond model, the number of hybrid orbitals equals the number of atomic orbitals combined and matches the modelled electron-domain directions.",
                 [{"symbol": "sp2", "meaning": "one s plus two p orbitals combined", "unit_or_domain": "introductory hybrid set"},
                  {"symbol": "sp3", "meaning": "one s plus three p orbitals combined", "unit_or_domain": "introductory hybrid set"}],
                 ["Use this as an introductory local bonding model, not as a complete quantum description."],
                 [step("HYB-R1", "DECLARE", "Count the electron-domain directions.", "Hybrid set choice follows the directional set being modelled.", "domain-direction count"),
                  step("HYB-R2", "TRANSFORM", "Map three directions to sp2 and four to sp3.", "One s orbital is included in both labels, so set size is 3 or 4 respectively.", "hybrid set"),
                  step("HYB-R3", "VERIFY", "Check set size equals the number of modelled directions.", "The superscript alone is not the number of hybrids.", "verified set size")],
                 ["The model rationalises directional bonding; it is not a full many-electron wavefunction description."],
                 ["sp2 must give three hybrids and sp3 four."], SRC_VSEPR),
        relation(REL_3D,
                 "four electron domains → tetrahedral electron-domain arrangement; molecular geometry omits lone-pair positions from the atom-only name",
                 "A flat Lewis structure records connectivity/electron pairs but does not by itself encode the three-dimensional domain geometry.",
                 [{"symbol": "EDG", "meaning": "electron-domain geometry", "unit_or_domain": "geometry label"},
                  {"symbol": "MG", "meaning": "molecular geometry from atom positions", "unit_or_domain": "geometry label"}],
                 ["Four regions around a centre are arranged tetrahedrally in the introductory VSEPR model."],
                 [step("GEO-R1", "DECLARE", "Preserve the domain count from the Lewis structure.", "Connectivity comes before spatial naming.", "domain inventory"),
                  step("GEO-R2", "TRANSFORM", "Place four domains along tetrahedral directions.", "Four regions minimise repulsion in a tetrahedral arrangement.", "3D domain arrangement"),
                  step("GEO-R3", "VERIFY", "Name electron-domain and molecular geometry separately when lone pairs are present.", "The molecular name counts atom positions, not lone-pair directions.", "verified geometry labels")],
                 ["A 2D cross drawing is not evidence of 90° molecular geometry."],
                 ["NH3: tetrahedral electron-domain geometry but trigonal-pyramidal molecular geometry."], SRC_VSEPR),
        relation(REL_MODEL,
                 "model choice follows requested explanatory output",
                 "VSEPR is the economical model for overall electron-domain arrangement; orbital-overlap/valence-bond descriptions answer orbital composition and overlap questions.",
                 [{"symbol": "VSEPR", "meaning": "electron-domain arrangement model", "unit_or_domain": "explanatory model"},
                  {"symbol": "VB", "meaning": "valence-bond/orbital-overlap description", "unit_or_domain": "explanatory model"}],
                 ["Choose the model after identifying what the question asks to predict."],
                 [step("MOD-R1", "DECLARE", "State the requested output.", "Model adequacy is relative to an explanatory task.", "requested output"),
                  step("MOD-R2", "TRANSFORM", "Choose VSEPR for overall domain arrangement and orbital overlap for orbital-level bonding detail.", "Each model carries a different explanatory scope.", "fit-for-purpose model"),
                  step("MOD-R3", "VERIFY", "State what the chosen model does not resolve.", "A scope boundary prevents treating one model as universally more correct.", "scope-limited conclusion")],
                 ["Neither model should be presented as universally superior; the question determines the useful level."],
                 ["For Q5, VSEPR answers the requested overall 3D arrangement without needing orbital wavefunction detail."], SRC_VSEPR),
        relation(REL_SIGPI,
                 "sigma: end-on overlap along internuclear axis; pi: side-on overlap with density on opposite sides of the axis",
                 "Sigma/pi classification is defined by overlap symmetry/orientation relative to the internuclear axis, not merely by seeing a single or double bond label.",
                 [{"symbol": "σ", "meaning": "axially symmetric end-on overlap", "unit_or_domain": "bonding-overlap class"},
                  {"symbol": "π", "meaning": "side-on overlap with a nodal plane containing the internuclear axis", "unit_or_domain": "bonding-overlap class"}],
                 ["Use the internuclear axis as the reference direction."],
                 [step("SIG-R1", "DECLARE", "Mark the internuclear axis.", "The classification is defined relative to this axis.", "reference axis"),
                  step("SIG-R2", "TRANSFORM", "Classify end-on overlap as sigma and side-on overlap as pi.", "The overlap symmetry differs with orientation.", "overlap class"),
                  step("SIG-R3", "VERIFY", "Check for the pi nodal plane through the axis.", "This distinguishes side-on pi overlap from axial sigma overlap.", "verified overlap class")],
                 ["Bond multiplicity is related but is not the defining geometric test."],
                 ["A pi diagram must place overlap density on opposite sides of the internuclear axis."], SRC_SIGPI),
    ]

    assets = {
        REP_DOMAIN: asset_refs["issue31-domain-count.svg"], REP_HYBRID: asset_refs["issue31-hybrid-sets.svg"],
        REP_TETRA_CH4: asset_refs["issue31-ch4-tetrahedral.svg"], REP_TETRA_NH3: asset_refs["issue31-nh3-domains.svg"],
        REP_VSEPR: asset_refs["issue31-vsepr-geometry.svg"], REP_MODEL: asset_refs["issue31-model-scope.svg"],
        REP_SIGPI: asset_refs["issue31-sigma-pi.svg"], REP_WEDGE: asset_refs["issue31-wedge-dash.svg"],
    }
    representations = [
        representation(REP_DOMAIN, "ORBITAL_DIAGRAM", "Make local central-atom domain counting visible and show why a multiple bond remains one direction.", assets[REP_DOMAIN], [REL_DOMAIN],
                       [("DOM-1", "Choose centre", "Mark the atom whose domains are being counted."), ("DOM-2", "Distinct directions", "Count neighbouring directions, not bond lines."), ("DOM-3", "Local lone pairs", "Include lone pairs only on the chosen centre.")],
                       [{"element": "central atom", "symbol": "counting centre", "in_words": "all domains are counted around this atom"}, {"element": "double bond", "symbol": "one direction", "in_words": "two bond lines to one neighbour still form one VSEPR region"}], SRC_VSEPR),
        representation(REP_HYBRID, "ORBITAL_DIAGRAM", "Show the introductory mapping from 3/4 electron-domain directions to sp2/sp3 hybrid set size.", assets[REP_HYBRID], [REL_HYBRID],
                       [("HYB-1", "Domain count", "Start from the number of directions."), ("HYB-2", "Hybrid label", "Map 3 to sp2 and 4 to sp3."), ("HYB-3", "Set size", "Verify the number of hybrids equals the number of directions.")],
                       [{"element": "three-direction set", "symbol": "sp2", "in_words": "one s plus two p orbitals gives three hybrids"}, {"element": "four-direction set", "symbol": "sp3", "in_words": "one s plus three p orbitals gives four hybrids"}], SRC_VSEPR),
        representation(REP_TETRA_CH4, "ORBITAL_DIAGRAM", "Build methane's four bonding domains into an sp3 tetrahedral arrangement.", assets[REP_TETRA_CH4], [REL_HYBRID, REL_3D],
                       [("CH4-1", "Four bonding domains", "Count the four C-H regions around carbon."), ("CH4-2", "Tetrahedral directions", "Move the four directions out of a flat drawing."), ("CH4-3", "sp3 check", "Connect four directions to the introductory sp3 set and tetrahedral geometry.")],
                       [{"element": "four C-H directions", "symbol": "4 domains", "in_words": "four bonding regions around carbon"}, {"element": "tetrahedral depth", "symbol": "sp3", "in_words": "four non-coplanar hybrid directions"}], SRC_VSEPR),
        representation(REP_TETRA_NH3, "ORBITAL_DIAGRAM", "Translate NH3's three bonding domains and one lone-pair domain into tetrahedral directions.", assets[REP_TETRA_NH3], [REL_3D],
                       [("NH3-1", "Four domains", "Inventory three N-H bonds plus one N lone pair."), ("NH3-2", "Tetrahedral directions", "Move the four domains out of a flat Lewis plane."), ("NH3-3", "Two geometry names", "Separate electron-domain geometry from molecular geometry.")],
                       [{"element": "three N-H directions", "symbol": "bonding domains", "in_words": "three atom directions"}, {"element": "lone-pair direction", "symbol": "nonbonding domain", "in_words": "counts in electron-domain geometry but not in the atom-only molecular-geometry name"}], SRC_VSEPR),
        representation(REP_VSEPR, "DATA_TABLE", "Distinguish the electron-domain geometry and atom-only molecular geometry predicted by VSEPR for NH3.", assets[REP_VSEPR], [REL_3D],
                       [("VG-1", "Domain inventory", "Count all four electron domains around nitrogen."), ("VG-2", "Electron-domain geometry", "Name the tetrahedral arrangement of all four domains."), ("VG-3", "Molecular geometry", "Omit the lone-pair position only when naming the atom-only shape.")],
                       [{"element": "electron-domain row", "symbol": "EDG", "in_words": "tetrahedral because all four domains count"}, {"element": "molecular-geometry row", "symbol": "MG", "in_words": "trigonal pyramidal because only atom positions are named"}], SRC_VSEPR),
        representation(REP_MODEL, "DATA_TABLE", "Compare what VSEPR and orbital-overlap descriptions predict for the same NH3 anchor.", assets[REP_MODEL], [REL_MODEL],
                       [("MOD-1", "Requested output", "Identify that Q5 asks for overall 3D electron-domain arrangement."), ("MOD-2", "VSEPR lens", "See the prediction that directly answers that request."), ("MOD-3", "Overlap lens", "Mark orbital-level details that are outside the requested output.")],
                       [{"element": "VSEPR column", "symbol": "overall arrangement", "in_words": "electron-domain and molecular geometry"}, {"element": "orbital-overlap column", "symbol": "bonding detail", "in_words": "orbital composition and overlap"}], SRC_VSEPR),
        representation(REP_SIGPI, "ORBITAL_DIAGRAM", "Anchor sigma/pi classification to the internuclear axis and overlap orientation.", assets[REP_SIGPI], [REL_SIGPI],
                       [("SIG-1", "Internuclear axis", "Use the atom-atom line as the reference."), ("SIG-2", "End-on overlap", "Identify sigma overlap along the axis."), ("SIG-3", "Side-on overlap", "Identify pi overlap and its nodal-plane relation.")],
                       [{"element": "end-on lobes", "symbol": "σ", "in_words": "overlap lies along the internuclear axis"}, {"element": "side-on lobes", "symbol": "π", "in_words": "overlap lies on opposite sides of the axis"}], SRC_SIGPI),
        representation(REP_WEDGE, "STRUCTURAL_FORMULA", "Use wedge/dash depth encoding to distinguish tetrahedral methane from a flat cross Lewis drawing.", assets[REP_WEDGE], [REL_3D],
                       [("WD-1", "Connectivity", "Keep carbon bonded to four hydrogens."), ("WD-2", "Depth cues", "Use wedge and dash for bonds toward and behind the viewer."), ("WD-3", "Tetrahedral check", "Reject a coplanar 90-degree cross interpretation.")],
                       [{"element": "solid wedge", "symbol": "toward viewer", "in_words": "one bond projects out of the page"}, {"element": "hashed/dashed bond", "symbol": "behind viewer", "in_words": "one bond projects behind the page"}], SRC_VSEPR),
    ]

    families = [
        family(FAM_DOMAIN, "Electron domains and introductory hybrid-set mapping",
               ["CAP-CHEM-G11-ELECTRON-DOMAIN-COUNT", "CAP-CHEM-G11-SP3-HYBRID-SET", "CAP-CHEM-G11-DOMAIN-TO-HYBRID-GEOMETRY"],
               "Count bond lines or read hybrid superscripts as the number of directions.",
               "The count is local to the chosen centre and the hybrid mapping is an introductory model."),
        family(FAM_3D, "Lewis-to-3D domain geometry",
               ["CAP-CHEM-G11-LEWIS-TO-3D-DOMAINS", "CAP-CHEM-G11-VSEPR-GEOMETRY"],
               "Treat a planar Lewis layout as the molecular geometry.",
               "Electron-domain geometry counts lone-pair directions; molecular geometry names atom positions."),
        family(FAM_MODEL, "Model-scope selection",
               ["CAP-CHEM-G11-MODEL-SCOPE-VSEPR-VB", "CAP-CHEM-G11-VSEPR-GEOMETRY"],
               "Choose the orbital-overlap model simply because the chapter is about hybridisation.",
               "The useful model is selected by the requested explanatory output."),
        family(FAM_SIGPI, "Sigma/pi overlap geometry",
               ["CAP-CHEM-G11-SIGMA-PI-OVERLAP"],
               "Classify pi only from the appearance of a double bond.",
               "Use orientation and symmetry relative to the internuclear axis."),
    ]

    questions = LEDGER["questions"]
    # Canonical library ownership is one microtopic per primary capability. The benchmark
    # ledger deliberately keeps finer question-level microtopic labels as review evidence,
    # but repeating a primary capability across library microtopics makes concept ownership
    # ambiguous to the renderer.
    representatives = []
    seen_caps = set()
    for q in questions:
        if q["primary_capability_ref"] not in seen_caps:
            representatives.append(q)
            seen_caps.add(q["primary_capability_ref"])
    micros = [microtopic(q, bank_ids[q["original_identifier"]]) for q in representatives]

    # VSEPR is a secondary capability in the benchmark questions, so give it one explicit
    # canonical owner without changing any question's primary capability.
    q4 = next(q for q in questions if q["original_identifier"] == "Q4")
    vsepr = json.loads(json.dumps(microtopic(q4, bank_ids["Q4"])))
    def rename_nested(value):
        if isinstance(value, str):
            return value.replace("HYB-T4", "HYB-TV").replace("CU-Q4-ISS31", "CU-VSEPR-ISS31")
        if isinstance(value, list):
            return [rename_nested(x) for x in value]
        if isinstance(value, dict):
            return {k: rename_nested(v) for k, v in value.items()}
        return value
    vsepr = rename_nested(vsepr)
    vsepr["id"] = "MIC-CHEM-G11-VSEPR-GEOMETRY"
    vsepr["title"] = "VSEPR electron-domain versus molecular geometry"
    vsepr["primary_capability_ref"] = "CAP-CHEM-G11-VSEPR-GEOMETRY"
    vsepr["representation_refs"] = [REP_VSEPR]
    vsepr["elicitation"]["attempt"]["task"]["representation_ref"] = REP_VSEPR
    vsepr["construction_units"][0]["representation_ref"] = REP_VSEPR
    vsepr["construction_units"][0]["reveal_stage_refs"] = ["VG-1", "VG-2", "VG-3"]
    vsepr["compact_anchor"]["representation_ref"] = REP_VSEPR
    vsepr["inferential_jump"] = "Use the electron-domain arrangement to predict geometry, then omit lone-pair positions only when naming atom-only molecular geometry."
    vsepr["badge_reason"] = "The learner must keep electron-domain geometry and molecular geometry as related but non-identical outputs."
    micros.append(vsepr)

    bucket = {
        **base(BUCKET, [SRC_VSEPR, SRC_SIGPI]),
        "title": "Hybridisation, electron domains and bonding models", "topic": "Chemical Bonding",
        "intrinsic_badge": "MEDIUM",
        "badge_reason": "The slice combines local electron-domain counting, 2D-to-3D translation, model-scope selection and overlap geometry.",
        "depth_overlay": "FOUNDATION", "curriculum_mappings": [], "prerequisite_refs": [],
        "primary_representation_ref": REP_MODEL,
    }
    route = {
        **base("ROUTE-CHEM-G11-HYBRIDISATION-CORE1A", [SRC_VSEPR, SRC_SIGPI]),
        "title": "Construct hybridisation from electron-domain decisions", "cores": ["CORE1A"],
        "microtopic_refs": [m["id"] for m in micros],
        "entry_needs": ["Learner can identify atoms, bond order, shared pairs and lone pairs in a supplied simple Lewis structure."],
        "learner_actions": [
            "Count domains locally around the selected central atom.",
            "Translate domain count into 3D VSEPR geometry and the introductory hybrid-set mapping.",
            "Choose VSEPR versus orbital-overlap descriptions by explanatory scope.",
            "Classify sigma versus pi overlap from the internuclear axis."
        ],
        "help_plan": [
            "Mark the central atom before counting.", "Collapse any multiple bond to one VSEPR direction.",
            "Separate electron-domain geometry from molecular geometry.",
            "Ask what the question wants the model to predict before naming a model."
        ],
        "reveal_plan": "Build the local counting and representation rules first, then use Q5 as the model-scope crux and Q6 as the overlap-geometry boundary.",
        "source_preferences": [
            {"resource_ref": SRC_VSEPR, "purpose": "VSEPR and hybrid-orbital model", "reason": "Supports domain counting, geometry and introductory sp2/sp3 mapping."},
            {"resource_ref": SRC_SIGPI, "purpose": "Sigma/pi overlap", "reason": "Supports the internuclear-axis classification used in Q6 and the multiple-bond distinction used in Q2/Q9."},
        ],
        "when_not_suitable": ["Do not extend this slice into delocalisation, resonance-sensitive hybridisation exceptions, radicals, hypervalency or a complete quantum-mechanical treatment."],
        "practice_profile_ref": None,
    }
    return {
        "schema_version": "0.2.0", "package_id": "LIB-CHEM-G11-HYBRIDISATION-ISS31",
        "title": "Hybridisation: domains, geometry and model choice", "version": "0.1.0",
        "status": "CANDIDATE", "subject": "Chemistry",
        "scope_summary": "Grade 11 introductory hybridisation and bonding-model slice for Issue #31: central-atom electron-domain counting, sp2/sp3 set size, tetrahedral domain geometry, Lewis-to-3D translation, VSEPR versus orbital-overlap model scope, and sigma/pi overlap geometry. Advanced delocalisation and exception chemistry are outside this packet.",
        "curriculum_mappings": [], "resources": resources, "buckets": [bucket],
        "capabilities": capabilities, "microtopics": micros, "relations": relations,
        "representations": representations, "question_families": families, "questions": [],
        "teaching_routes": [route], "practice_profiles": [], "evidence": [], "known_issues": [],
        "extensions": {"grade9v3:benchmark_issue": 31}, "data": [],
    }


def fill_bank() -> dict[str, str]:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    ledger_by_q = {q["original_identifier"]: q for q in LEDGER["questions"]}
    bank_ids: dict[str, str] = {}
    for row in bank["questions"]:
        qid = row["original_identifier"]
        q = ledger_by_q[qid]
        bank_ids[qid] = row["id"]
        _, rep_ref, family_ref, _ = Q_META[qid]
        move1, move2, move3 = [f"{row['id']}-MOVE-{n}" for n in (1, 2, 3)]
        first_stage = {REP_DOMAIN:"DOM-1",REP_HYBRID:"HYB-1",REP_TETRA_CH4:"CH4-1",REP_TETRA_NH3:"NH3-1",REP_VSEPR:"VG-1",REP_MODEL:"MOD-1",REP_SIGPI:"SIG-1",REP_WEDGE:"WD-1"}[rep_ref]
        second_stage = {REP_DOMAIN:"DOM-2",REP_HYBRID:"HYB-2",REP_TETRA_CH4:"CH4-2",REP_TETRA_NH3:"NH3-2",REP_VSEPR:"VG-2",REP_MODEL:"MOD-2",REP_SIGPI:"SIG-2",REP_WEDGE:"WD-2"}[rep_ref]
        row["answer"] = {
            "kind": "EXACT", "summary": q["answer"]["summary"], "reasoning": list(q["answer"]["reasoning"]),
            "reasoning_route": [
                {"id":move1,"kind":"REPRESENT","action":f"Identify the target: {q['qrt']['X']}.","why_valid":"The representation/model must be tied to what the question actually asks for.","inputs":["owner-supplied stem"],"output":"target represented at the correct level","representation_ref":rep_ref,"visual_stage_ref":first_stage},
                {"id":move2,"kind":"DECIDE","action":q["qrt"]["replacement_rule"],"why_valid":"This is the source-grounded repair rule for the benchmark misconception.","inputs":["represented target","governing chemistry rule"],"output":q["answer"]["summary"]},
                {"id":move3,"kind":"VERIFY","action":"Check the conclusion against the central-atom/domain, three-dimensional geometry, model-scope or internuclear-axis invariant.","why_valid":"The verification attacks the misconception independently of repeating the final statement.","inputs":["candidate conclusion"],"output":"conclusion verified against the relevant invariant"},
            ],
            "crux_move_ref": move2,
            "check": f"Reject this tempting route explicitly: {q['qrt']['wrong_idea']}",
            "acceptable_alternatives": [], "subpart_answers": [], "verification_status": "INDEPENDENTLY_CHECKED",
        }
        row["primary_capability_ref"] = q["primary_capability_ref"]
        row["family_ref"] = family_ref
        row["conditions"] = [{"Q6":"Classify overlap from orbital orientation relative to the internuclear axis.","Q5":"Choose the model only for the explanatory output requested in the stem."}.get(qid,"Use the stated central atom and the introductory VSEPR/valence-bond model; count electron-density regions rather than drawn bond lines.")]
        row["figure_refs"] = [rep_ref]
        row["scaffolds"] = [
            {"text":f"Clarify the target before solving: {q['qrt']['X']}","support_kind":"CONNECT","reveals":"CONCEPT","learner_stage":"KEY_CONCEPT","supports_move_ref":move1},
            {"text":f"Use this rule without substituting the final answer yet: {q['qrt']['Z']}","support_kind":"REPRESENT","reveals":"METHOD","learner_stage":"REPRESENTATION","supports_move_ref":move2,"visual_ref":rep_ref,"visual_stage_ref":second_stage},
            {"text":"Check your conclusion against the named invariant and the tempting wrong route before revealing the solution.","support_kind":"EXECUTE","reveals":"METHOD","learner_stage":"CHECKPOINT","supports_move_ref":move3},
        ]
        analysis = row["extensions"].setdefault("grade9v3:analysis", {})
        analysis["learner_question_type"] = "constructed_response"
        analysis["difficulty"] = q["difficulty"]
        analysis["expected_time_seconds"] = 150 if q["difficulty"]["band"] == "D2" else 90
        analysis["common_wrong_route"] = q["qrt"]["wrong_idea"]
        analysis["cognitive_demand"] = {"primary":q["primary_demand"],"secondary":q.get("secondary_demands",[])}
        analysis["stable_crux_move"] = q["qrt"]["Z"]
        row["extensions"]["grade9v3:component_waivers"] = {}
        row.pop("hints", None)
        row.pop("hint_ladder", None)

    BANK_PATH.write_text(json.dumps(bank, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return bank_ids


def main() -> None:
    if not BANK_PATH.is_file():
        raise SystemExit(f"{BANK_PATH} does not exist; create it first with owner_bank.py new")
    asset_refs = write_assets()
    bank_ids = fill_bank()
    package = build_package(asset_refs, bank_ids)
    PACKAGE_PATH.write_text(json.dumps(package, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    expected = {q["original_identifier"]: q["stem"] for q in LEDGER["questions"]}
    actual = {q["original_identifier"]: q["stem"] for q in bank["questions"]}
    if actual != expected:
        raise SystemExit("owner-bank stem drift detected")
    print(f"materialized {PACKAGE_PATH.relative_to(REPO)}")
    print(f"filled {BANK_PATH.relative_to(REPO)} with {len(bank['questions'])} verbatim questions")
    print(f"wrote {len(asset_refs)} Chemistry representation assets")


if __name__ == "__main__":
    main()
