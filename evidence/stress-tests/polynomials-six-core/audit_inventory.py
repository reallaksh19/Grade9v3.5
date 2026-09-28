"""Read-only inventory for the Polynomials six-Core stress evidence."""
import hashlib
import json
import subprocess
from pathlib import Path

from jsonschema import Draft202012Validator
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[3]
HERE = Path(__file__).resolve().parent


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
        "Shared/tools/quality_observe.py",
        "Shared/quality/learner-quality.v1.json",
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
    )
]

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
for folder in ("rendered", "golden-control", "pdf"):
    outputs.extend(row(p) for p in sorted((HERE / folder).glob("*")) if p.is_file())
for name in ("quality-static.json", "quality-browser.json", "chromium-audit.json", "golden-control-quality.json", "golden-chromium-audit.json", "browser-interaction.json"):
    outputs.append(row(HERE / name))

pdf_text = {}
for p in sorted((HERE / "pdf").glob("core*.pdf")):
    reader = PdfReader(str(p))
    extracted = "\n".join(page.extract_text() or "" for page in reader.pages)
    pdf_text[p.name] = {"pages": len(reader.pages), "text": extracted}

inventory = {
    "head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "branch": subprocess.check_output(["git", "branch", "--show-current"], cwd=ROOT, text=True).strip(),
    "inputs": [row(p) for p in inputs],
    "outputs": outputs,
    "untrusted_fixture_schema_errors": schema_errors,
    "pdf_text": pdf_text,
}
(HERE / "inventory.json").write_text(json.dumps(inventory, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
print("inputs", len(inputs), "outputs", len(outputs), "package errors", len(schema_errors["package.json"]), "bank errors", len(schema_errors["bank.json"]))
