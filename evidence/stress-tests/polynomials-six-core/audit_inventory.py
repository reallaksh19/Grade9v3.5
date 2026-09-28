"""Read-only inventory for the Polynomials six-Core stress evidence."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent
EXECUTION_BASIS = "68559ac4cb17eeb5f2d87aebecebf652b9a34efd"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def row(path):
    return {"path": path.relative_to(ROOT).as_posix(), "bytes": path.stat().st_size, "sha256": sha(path)}


inputs = [
    ROOT / p for p in (
        "Shared/tools/render_core.py",
        "Shared/tools/learner_metadata.py",
        "Shared/tools/product_manifest.py",
        "Shared/tools/quality_gate.py",
        "Shared/tools/quality_contract.py",
        "Shared/tools/quality_observe.py",
        "Shared/quality/learner-quality.v1.json",
        "Shared/vocabularies/learner-question-metadata.v1.json",
        "Mathematics/adapter/CoreContracts.json",
        "Mathematics/adapter/QualityVocabulary.json",
        "Mathematics/research/acquisitions/ACQ-DBC30792858FA1858D24.json",
        "Shared/library/package.schema.json",
        "Shared/library/competitive-exam-bank.schema.json",
        "Shared/web/interactive-page-blueprints.v1.json",
        "public/css/tablet-12-7.css",
        "golden/units/G-MATH-LINEAR-CONSTRAINT/manifest.json",
        "golden/units/G-MATH-LINEAR-CONSTRAINT/records.json",
        "golden/units/G-MATH-LINEAR-CONSTRAINT/bank.json",
        "evidence/stress-tests/polynomials-six-core/empty.manifest.json",
        "evidence/stress-tests/polynomials-six-core/untrusted-fixture/original-manifest.json",
        "evidence/stress-tests/polynomials-six-core/untrusted-fixture/replay-manifest.json",
        "evidence/stress-tests/polynomials-six-core/untrusted-fixture/package.json",
        "evidence/stress-tests/polynomials-six-core/untrusted-fixture/bank.json",
        "evidence/stress-tests/polynomials-six-core/prototype/build_records.py",
        "evidence/stress-tests/polynomials-six-core/prototype/records.json",
        "evidence/stress-tests/polynomials-six-core/prototype/manifest.json",
        "evidence/stress-tests/polynomials-six-core/prototype/power-cards.svg",
        "evidence/stress-tests/polynomials-six-core/browser-interaction.mjs",
        "tools/site-audit/core-page-audit.mjs",
        "tools/print/print-product.mjs",
    )
]
external_source = HERE / "source/iemh102.pdf"

schema_errors = {}
for data_name, schema_name in (
    ("package.json", "Shared/library/package.schema.json"),
    ("bank.json", "Shared/library/competitive-exam-bank.schema.json"),
):
    data = json.loads((HERE / "untrusted-fixture" / data_name).read_text(encoding="utf-8"))
    schema = json.loads((ROOT / schema_name).read_text(encoding="utf-8"))
    errors = sorted(Draft202012Validator(schema).iter_errors(data), key=lambda e: (str(list(e.absolute_path)), e.message))
    schema_errors[data_name] = [
        {"at": "/".join(map(str, e.absolute_path)) or "<root>", "detail": e.message}
        for e in errors
    ]

outputs = []
for folder in ("rendered", "golden-control", "pdf", "prototype/rendered", "prototype/pdf"):
    outputs.extend(row(p) for p in sorted((HERE / folder).glob("*")) if p.is_file())
for name in ("quality-static.json", "quality-browser.json", "chromium-audit.json", "golden-control-quality.json", "golden-chromium-audit.json", "browser-interaction.json", "prototype/quality-browser.json", "prototype/chromium-audit.json"):
    outputs.append(row(HERE / name))

pdf_text = {}
for p in sorted((HERE / "pdf").glob("core*.pdf")):
    reader = PdfReader(str(p))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_text[p.name] = {"pages": len(reader.pages), "text": extracted}

inventory = {
    "execution_basis": EXECUTION_BASIS,
    "evidence_commit": None,
    "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
    "inputs": [row(p) for p in inputs],
    "external_source": {"url": "https://ncert.nic.in/textbook/pdf/iemh102.pdf", "sha256": sha(external_source), "bytes": external_source.stat().st_size, "committed": False},
    "outputs": outputs,
    "untrusted_fixture_schema_errors": schema_errors,
    "pdf_text": pdf_text,
}
target = HERE / "inventory.json"
if "--verify" in sys.argv:
    recorded = json.loads(target.read_text(encoding="utf-8"))
    drift = []
    for group in ("inputs", "outputs"):
        for expected in recorded[group]:
            path = ROOT / expected["path"]
            if not path.is_file() or sha(path) != expected["sha256"]:
                drift.append(expected["path"])
    if recorded["execution_basis"] != EXECUTION_BASIS:
        drift.append("execution_basis")
    if external_source.is_file() and sha(external_source) != recorded["external_source"]["sha256"]:
        drift.append("external_source")
    print("VERIFY", "PASS" if not drift else "DRIFT", "\n".join(drift))
    raise SystemExit(1 if drift else 0)
target.write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("inputs", len(inputs), "outputs", len(outputs), "package errors", len(schema_errors["package.json"]), "bank errors", len(schema_errors["bank.json"]))
