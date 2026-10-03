#!/usr/bin/env python3
from __future__ import annotations
import argparse, copy, hashlib, json, os
from pathlib import Path

REPO = Path(__file__).resolve().parents[3]
import sys
sys.path.insert(0, str(REPO))
from Shared.tools import question_review_matrix as qrt

BANK = REPO / "Mathematics/question-bank/owner-supplied/issue-11-surface-areas-volumes.json"
PACKAGE = REPO / "Mathematics/library/surface-areas-volumes.issue11.v1.json"
MANIFEST = REPO / "products/mathematics/surface-areas-volumes.issue11.manifest.json"
PROFILE = REPO / "evidence/pilots/issue-11/learner-profile.json"
JUDGEMENTS = REPO / "evidence/pilots/issue-11/qrt-judgements.json"
ADAPTER = REPO / "Mathematics/adapter/DemandReview.json"
OUT = REPO / "evidence/pilots/issue-11"

def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))

def dump(path: Path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def sha(path: Path):
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()

def make_baseline(bank_out: Path, manifest_out: Path):
    bank = load(BANK)
    for q in bank["questions"]:
        q["scaffolds"] = []
        q["hint_ladder"] = []
        q["figure_refs"] = []
        q["representation_roles"] = {"initial_ref": None, "safe_ref": None, "bound_ref": None, "stage_refs": []}
        analysis = q["extensions"]["grade9v3:analysis"]
        analysis.pop("common_wrong_route", None)
        q["answer"]["check"] = ""
    dump(bank_out, bank)
    manifest = load(MANIFEST)
    manifest["bank_refs"] = [str(bank_out)]
    dump(manifest_out, manifest)

def build_evidence(gate_before: Path, gate_after: Path, render_dir: Path):
    bank, package, profile = load(BANK), load(PACKAGE), load(PROFILE)
    judgements = load(JUDGEMENTS)["reviews"]
    matrix, vocab, adapter = qrt.load(qrt.MATRIX_PATH), qrt.load(qrt.VOCAB_PATH), qrt.load(ADAPTER)
    by_cap = {m["primary_capability_ref"]: m["id"] for m in package["microtopics"]}
    core2 = (render_dir / "core2.html").read_text(encoding="utf-8")
    core1a = (render_dir / "core1a.html").read_text(encoding="utf-8")
    receipt = load(render_dir / "render-receipt.json")
    reviews, projections = [], []
    for question in bank["questions"]:
        resolution = qrt.specialize_resolution(qrt.resolve_review(question, profile, matrix, vocab), adapter)
        judgement = judgements[question["id"]]
        missing = [ask for ask in qrt.ASKS if ask not in judgement]
        if missing:
            raise SystemExit(f"{question['id']}: missing judgements {missing}")
        for ask in qrt.ASKS:
            if judgement[ask].get("verdict") not in qrt.VERDICTS:
                raise SystemExit(f"{question['id']}:{ask}: invalid verdict")
        projection = qrt.project_product_review_findings(resolution, judgement)
        projections.append(projection)
        mid = by_cap[question["primary_capability_ref"]]
        reviews.append({
            "question_ref": question["id"],
            "original_identifier": question["original_identifier"],
            "template_id": resolution["template_id"],
            "classification": resolution["classification"],
            "basis_digests": resolution["basis_digests"],
            "subject_adapter": resolution["subject_adapter"],
            "slots": resolution["slots"],
            "review_objectives": resolution["review"],
            "judgements": judgement,
            "exact_render_evidence": {
                "core2_question_marker_present": question["id"] in core2,
                "core1a_concept_marker_present": mid in core1a,
                "core2_html_sha256": sha(render_dir / "core2.html"),
                "core1a_html_sha256": sha(render_dir / "core1a.html"),
                "render_receipt_sha256": sha(render_dir / "render-receipt.json"),
                "render_artifact_digest": receipt.get("artifact_digest"),
                "render_semantic_digest": receipt.get("semantic_digest"),
            },
            "sign_off": {
                "author": "Issue #11 execution agent",
                "semantic_reviewer": "Issue #11 execution agent self-review",
                "reviewer_distinct_from_author": False,
                "release_certified": False,
                "independent_review_required": True,
                "date": "2026-10-03"
            }
        })
    before, after = load(gate_before), load(gate_after)
    delta = qrt.compare_quality_gate_reports(before, after)
    dump(OUT / "gate-delta.json", delta)
    dump(OUT / "product-review-qrt-findings.json", {
        "schema": "issue11-product-review-qrt-projection/v1",
        "source": "Shared/tools/question_review_matrix.py::project_product_review_findings",
        "projections": projections,
        "total_findings": sum(len(x["findings"]) for x in projections),
        "release_certification": False
    })
    dump(OUT / "qrt-review-evidence.json", {
        "schema": "issue11-qrt-review-evidence/v1",
        "issue": 11,
        "subject": "Mathematics",
        "grade": 9,
        "topic": "Surface Areas and Volumes",
        "blueprints": {
            "CORE2": "BP-CORE2-SOURCE-QUESTION@1.5.0",
            "CORE1A": "BP-CORE1A-CONSTRUCTION@1.4.0"
        },
        "profile_ref": profile["profile_id"],
        "profile_digest": qrt.canonical_digest(profile),
        "matrix_digest": qrt.canonical_digest(matrix),
        "adapter_digest": qrt.canonical_digest(adapter),
        "render": {
            "receipt": "evidence/pilots/issue-11/render/render-receipt.json",
            "core2": "evidence/pilots/issue-11/render/core2.html",
            "core1a": "evidence/pilots/issue-11/render/core1a.html",
            "core2_sha256": sha(render_dir / "core2.html"),
            "core1a_sha256": sha(render_dir / "core1a.html")
        },
        "reviews": reviews,
        "gate_delta_ref": "evidence/pilots/issue-11/gate-delta.json",
        "release_certification": False,
        "independent_review_required": True,
        "schema_limitation": "PR #9 does not contain the proposed Shared/quality/question-review.schema.json; this evidence therefore wraps the tool's question-review-resolution/v1 output plus explicit H1-M3 judgements."
    })
    dump(OUT / "execution-record.json", {
        "schema": "issue11-execution-record/v1",
        "source_commit_sha": os.environ.get("GITHUB_SHA"),
        "commands": [
            "python Shared/tools/question_review_matrix.py check",
            "python -m Shared.library.resolve --schema Mathematics/library/surface-areas-volumes.issue11.v1.json",
            "python Shared/tools/owner_bank.py check Mathematics/question-bank/owner-supplied/issue-11-surface-areas-volumes.json",
            "pytest -q tests/test_qrt_short_prompt.py tests/test_question_review_matrix.py",
            "python Shared/tools/render_core.py build --manifest /tmp/issue11-baseline-manifest.json --out /tmp/issue11-before --draft --reference",
            "python Shared/tools/quality_gate.py /tmp/issue11-before --subject Mathematics --product-id PILOT-I11-SA-VOLUMES --report evidence/pilots/issue-11/gate-before.json",
            "python Shared/tools/render_core.py build --manifest products/mathematics/surface-areas-volumes.issue11.manifest.json --out evidence/pilots/issue-11/render --reference",
            "python Shared/tools/quality_gate.py evidence/pilots/issue-11/render --subject Mathematics --product-id PILOT-I11-SA-VOLUMES --report evidence/pilots/issue-11/gate-after.json",
            "python evidence/pilots/issue-11/pilot_runner.py evidence ..."
        ],
        "files": {
            "package": {"path": str(PACKAGE.relative_to(REPO)), "sha256": sha(PACKAGE)},
            "owner_bank": {"path": str(BANK.relative_to(REPO)), "sha256": sha(BANK)},
            "manifest": {"path": str(MANIFEST.relative_to(REPO)), "sha256": sha(MANIFEST)},
            "profile": {"path": str(PROFILE.relative_to(REPO)), "sha256": sha(PROFILE)},
            "core2_html": {"path": str((render_dir / "core2.html").relative_to(REPO)), "sha256": sha(render_dir / "core2.html")},
            "core1a_html": {"path": str((render_dir / "core1a.html").relative_to(REPO)), "sha256": sha(render_dir / "core1a.html")},
            "render_receipt": {"path": str((render_dir / "render-receipt.json").relative_to(REPO)), "sha256": sha(render_dir / "render-receipt.json")},
            "gate_before": {"path": str(gate_before.relative_to(REPO)), "sha256": sha(gate_before)},
            "gate_after": {"path": str(gate_after.relative_to(REPO)), "sha256": sha(gate_after)}
        },
        "quality": {
            "gate_before_verdict": before.get("verdict"),
            "gate_after_verdict": after.get("verdict"),
            "rendered_measured_before": before.get("rendered_measured"),
            "rendered_measured_after": after.get("rendered_measured"),
            "qrt_actionable_findings": sum(len(x["findings"]) for x in projections)
        },
        "release_certification": False
    })

def main():
    p = argparse.ArgumentParser()
    sub = p.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("baseline")
    b.add_argument("--bank-out", type=Path, required=True)
    b.add_argument("--manifest-out", type=Path, required=True)
    e = sub.add_parser("evidence")
    e.add_argument("--gate-before", type=Path, required=True)
    e.add_argument("--gate-after", type=Path, required=True)
    e.add_argument("--render-dir", type=Path, required=True)
    a = p.parse_args()
    if a.cmd == "baseline":
        make_baseline(a.bank_out, a.manifest_out)
    else:
        build_evidence(a.gate_before, a.gate_after, a.render_dir)

if __name__ == "__main__":
    main()
