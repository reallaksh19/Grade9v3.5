"""Independent audit observations, not a learner-release or browser certificate."""
import hashlib
import json
import math
import re
from pathlib import Path
from lxml import etree, html

ROOT = Path(__file__).resolve().parent
rows = []
for issue in (32, 34, 36, 38):
    directory = ROOT / f"ISS{issue}/evidence/benchmark/ISS{issue}"
    bank = json.loads((directory / ("bank.json" if issue == 34 else "generated/owner.bank.json")).read_text())
    package = json.loads((directory / ("package.json" if issue == 34 else "generated/package.v1.json")).read_text())
    ladders = [tuple(re.sub(r"Q\d+", "Q?", s["text"]) for s in q.get("scaffolds", [])) for q in bank["questions"]]
    assets = []
    for p in sorted((directory / "assets").glob("*.svg")):
        tree = etree.fromstring(p.read_bytes())
        stages = []
        for stage in tree.xpath(".//*[@data-g9-stage-id]"):
            stages.append({"stage": stage.get("data-g9-stage-id"), "children": [etree.QName(c).localname for c in stage if isinstance(c.tag, str)]})
        assets.append({"asset": p.name, "xml_valid": True, "sha256": hashlib.sha256(p.read_bytes()).hexdigest(), "stages": stages})
    document = html.fromstring((directory / "rendered/core2.html").read_bytes())
    disclosures = [{"kind": d.get("data-g9-secondary"), "starts_closed": "open" not in d.attrib} for d in document.xpath("//details[@data-g9-secondary]")]
    reviews = json.loads((directory / "qrt-review.json").read_text())
    records = reviews.get("items", reviews.get("records", reviews.get("question_evaluations", [])))
    canonical_templates = json.loads((ROOT / f"ISS{issue}/Shared/quality/question-demand-templates.v1.json").read_text())["templates"]
    known = {r["template_id"] for r in canonical_templates}
    refs = [{"qid": r.get("question_id"), "template_id": r.get("template_id"), "canonical": r.get("template_id") in known} for r in records]
    rows.append({"issue": issue, "normalised_unique_hint_ladders": len(set(ladders)), "question_count": len(bank["questions"]), "assets": assets, "closed_core2_disclosures": disclosures, "qrt_review_template_refs": refs})
oracle = {
    "status": "OBSERVED",
    "observation": "LOCAL_EXECUTION + ARTIFACT_INSPECTION",
    "oracle": "INDEPENDENT_DOMAIN_REASONING",
    "formamide": {"formula": "CH3NO", "valence_electrons": 4 + 3 + 5 + 6, "total_electrons": 6 + 3 + 7 + 8, "pi_subsystem_electrons_in_supplied_model": 4},
    "carbonate_pi": {"orbitals": 4, "electrons": 2 + 2 + 2, "warrant": "One C=O pi pair plus one perpendicular p lone pair on each singly bonded O in a contributor: six electrons in the four-p-orbital space."},
    "cosine": [{"angle_degrees": a, "cos_positive": math.cos(math.radians(a)), "cos_negative": math.cos(math.radians(-a))} for a in (0, 30, 60, 90)],
    "issue36_builder": {"declared_formula": "abs(cos(theta))", "formula_at_0": abs(math.cos(0)), "proposal_at_0": 0, "formula_at_90": abs(math.cos(math.pi/2)), "proposal_at_90": 1, "status": "CONTRADICTION", "correction": "Define terminal-plane dihedral separately from p-axis misalignment. For the stated terminal-plane endpoints use a shifted cosine/sine model; do not silently change the meaning of theta."},
    "huckel_counterexample": {"assumptions": "Two degenerate orthonormal orbitals; diagonal energy epsilon; coupling t0*cos(theta); two electrons in lower MO; neglect other interactions.", "eigenvalues": "epsilon +/- abs(t0*cos(theta))", "bonding_stabilisation": "2*abs(t0*cos(theta)), not a universal cos^2 law", "purpose": "Disproves the candidate's universal Hückel-square claim; not a formamide energy prediction."},
    "browser": {"status": "NOT_RUN", "reason": "No Chromium/Firefox executable or Playwright browser cache in audit runtime; SVG rasterization and HTML inspection do not replace browser QA."},
    "candidates": rows,
}
(ROOT / "additional-checks.json").write_text(json.dumps(oracle, indent=2) + "\n")
print(json.dumps({"formamide_valence": oracle["formamide"]["valence_electrons"], "candidates": [{"issue": r["issue"], "unique_ladders": r["normalised_unique_hint_ladders"], "noncanonical_review_refs": sum(not x["canonical"] for x in r["qrt_review_template_refs"]), "open_secondary": sum(not x["starts_closed"] for x in r["closed_core2_disclosures"])} for r in rows]}))
