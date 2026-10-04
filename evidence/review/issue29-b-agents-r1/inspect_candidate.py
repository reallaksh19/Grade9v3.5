"""Independent artifact checks; never repair candidate bytes or replace a check with a claim."""
import hashlib
import json
import re
import sys
from pathlib import Path

issue = int(sys.argv[1])
ROOT = Path(__file__).resolve().parent
repo = ROOT / f"ISS{issue}"
sys.path.insert(0, str(repo))
from jsonschema import Draft202012Validator, RefResolver
from Shared.tools import owner_bank, product_manifest, product_coverage, render_core
from Shared.tools import web_blueprint_contract

directory = repo / f"evidence/benchmark/ISS{issue}"
snapshot = ROOT / "issue-bodies.json"
if not snapshot.is_file():
    snapshot = ROOT / "issue-inputs.json"
inputs = next(x for x in json.loads(snapshot.read_text()) if x["issue"] == issue)
body = inputs["body"]
core = body[body.index("## A — Question set Q1–Q10"):body.index("\n---\n\n## Audit-trail requirement")]
expected = dict((int(m[0]), m[1].strip()) for m in re.findall(r"### Q(\d+)\n\n([\s\S]*?)(?=\n\n### Q\d+|\n\n## B —)", core))
sha = lambda b: hashlib.sha256(b).hexdigest()
load = lambda p: json.loads(p.read_text())
bank_path = directory / ("bank.json" if issue == 34 else "generated/owner.bank.json")
package_path = directory / ("package.json" if issue == 34 else "generated/package.v1.json")
manifest_path = directory / ("manifest.json" if issue == 34 else "generated/product.manifest.json")
bank, package, manifest = map(load, (bank_path, package_path, manifest_path))
receipt = load(directory / "rendered/render-receipt.json")
report = {"issue": issue, "observation": "LOCAL_EXECUTION + ARTIFACT_INSPECTION", "oracle": "INDEPENDENT_REPRODUCTION + IMPLEMENTATION_COUPLED", "core_prompt_expected_sha256": sha(core.encode()), "core_prompt_committed_sha256": sha((directory / "owner-core-prompt.md").read_bytes()), "core_prompt_exact_match": (directory / "owner-core-prompt.md").read_bytes() == core.encode(), "question_count": len(bank.get("questions", [])), "stems": [], "schema": {}, "receipt": receipt, "limitations": ["Official jsonschema 4.17.3 with explicit URN-local resolver; full CLI checked separately.", "API reproduction is not evidence that the agent actually executed its claimed commands.", "Browser not executed by this script."]}
for n, q in enumerate(bank.get("questions", []), 1):
    label = q.get("original_identifier", "")
    qn = int(re.search(r"\d+", label).group()) if re.search(r"\d+", label) else n
    actual = q.get("stem", "")
    report["stems"].append({"qid": q["id"], "label": label, "exact_intake_match": actual == expected.get(qn), "expected_sha256": sha(expected.get(qn, "").encode()), "actual_sha256": sha(actual.encode())})
report["owner_bank_incomplete_problems"] = owner_bank.check(bank, complete=False)
report["owner_bank_complete_problems"] = owner_bank.check(bank, complete=True)
schema = load(render_core.PACKAGE_SCHEMA)
validator = Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store={"": schema}))
try:
    errors = list(validator.iter_errors(package))
    report["schema"] = {"status": "PASS" if not errors else "FAIL", "errors": [{"path": "/".join(map(str, e.absolute_path)), "message": e.message} for e in errors]}
except Exception as e:
    report["schema"] = {"status": "NOT_RUN", "exception": repr(e)}
try:
    selection = product_manifest.validate_selection(manifest, [package], bank["questions"])
    product_coverage.validate(manifest, product_manifest.derivable([package], bank["questions"]))
    report["selection"] = {"status": "PASS", "counts": {k: len(v) for k, v in selection.items()}}
except Exception as e:
    report["selection"] = {"status": "FAIL", "exception": repr(e)}
    selection = None
if selection is not None:
    # Same title derivation and public page/build functions as production, without pretending the CLI ran.
    manifest["title"] = package.get("title") or next((b.get("title") for b in package.get("buckets", []) if b.get("title")), None) or manifest["product_id"].replace("-", " ").title()
    try:
        ctx = render_core.Ctx(manifest, [package], bank["questions"], web_blueprint_contract.load_registry(), selection_rows=selection)
        pages = {render_core.ROLE_FILE[r]: render_core.page(ctx, r, "PAGES", render_core.DIGEST_SLOT) for r in product_manifest.selected_output_roles(manifest)}
        pages["index.html"] = render_core.index_page(ctx, render_core.DIGEST_SLOT)
        digest = render_core._artifact_digest(pages)
        pages = {k: v.replace(render_core.DIGEST_SLOT, digest) for k, v in pages.items()}
        out = ROOT / "reproductions" / f"ISS{issue}"
        out.mkdir(parents=True, exist_ok=True)
        rows = []
        for name, text in pages.items():
            (out / name).write_text(text)
            committed = (directory / "rendered" / name).read_bytes()
            actual = text.encode()
            rows.append({"name": name, "byte_equal": actual == committed, "committed_sha256": sha(committed), "reproduced_sha256": sha(actual), "committed_size": len(committed), "reproduced_size": len(actual)})
        report["production_API_reproduction"] = {"status": "PASS" if all(r["byte_equal"] for r in rows) else "FAIL", "digest": digest, "receipt_digest_match": digest == receipt.get("digest"), "files": rows, "actual_gaps": ctx.gaps, "actual_advisories": ctx.advisories}
    except Exception as e:
        report["production_API_reproduction"] = {"status": "FAIL", "exception": repr(e)}
report["stored_html_sizes"] = {p.name: len(p.read_bytes()) for p in (directory / "rendered").glob("*.html")}
output = ROOT / f"checks-ISS{issue}.json"
output.write_text(json.dumps(report, indent=2) + "\n")
print(json.dumps({"issue": issue, "core_exact": report["core_prompt_exact_match"], "stem_mismatches": [s["label"] for s in report["stems"] if not s["exact_intake_match"]], "bank_errors": len(report["owner_bank_incomplete_problems"]), "bank_complete_errors": len(report["owner_bank_complete_problems"]), "schema_status": report["schema"]["status"], "schema_errors": len(report["schema"].get("errors", [])), "selection": report["selection"]["status"], "reproduction": report.get("production_API_reproduction"), "result_file": str(output)}))
