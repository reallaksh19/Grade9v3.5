"""Regenerate correction pages and receipts with the current production authority.

This is a new render run. It does not recover historical test logs or certify
browser/academic quality. Run without --write to inspect prospective hashes.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, RefResolver

ISSUES = (32, 31, 34, 33, 36, 35, 38, 37)


def sha(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", type=Path, default=Path(__file__).resolve().parents[3])
    parser.add_argument("--write", action="store_true", help="Replace generated review copies, not source inputs")
    parser.add_argument("--out", type=Path, required=True, help="Write a prospective/current render report")
    args = parser.parse_args()
    repo = args.repo.resolve()
    sys.path.insert(0, str(repo))
    from Shared.tools import learning_repair, owner_bank, product_coverage, product_manifest, render_core, web_blueprint_contract

    def validate(record, schema_path):
        schema = load(schema_path)
        Draft202012Validator(schema, resolver=RefResolver.from_schema(schema, store={"": schema})).validate(record)

    registry = web_blueprint_contract.load_registry()
    validate(registry, repo / "Shared/web/interactive-page-blueprint.schema.json")
    basis = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
    authority_paths = [
        "Shared/tools/render_core.py",
        "Shared/tools/core2_v2.py",
        "Shared/tools/learning_repair.py",
        "Shared/web/interactive-page-blueprints.v1.json",
        "public/css/modern-learner.css",
        "public/css/tablet-12-7.css",
        "public/js/display-controls.js",
        "public/js/site-header.js",
    ]
    authorities = {path: sha((repo / path).read_bytes().replace(b"\r\n", b"\n")) for path in authority_paths}
    rows = []
    for issue in ISSUES:
        directory = repo / f"evidence/blueprint-cycles/ISS{issue}"
        package_path = directory / "inputs/package.v1.json"
        bank_path = directory / "inputs/owner.bank.json"
        manifest_path = directory / "inputs/product.manifest.json"
        package, bank, manifest = map(load, (package_path, bank_path, manifest_path))
        validate(package, render_core.PACKAGE_SCHEMA)
        basic = owner_bank.check(bank, complete=False)
        reference = owner_bank.check(bank, complete=True)
        if basic or reference:
            raise ValueError({"issue": issue, "basic": basic, "reference": reference})
        unit_ids = {u["id"] for m in package["microtopics"] for u in m["construction_units"]}
        repair_errors = {q["id"]: errors for q in bank["questions"]
                         if (errors := learning_repair.problems(q, unit_ids))}
        if repair_errors:
            raise ValueError(repair_errors)
        selection = product_manifest.validate_selection(manifest, [package], bank["questions"])
        product_coverage.validate(manifest, product_manifest.derivable([package], bank["questions"]))
        ctx = render_core.Ctx(manifest, [package], bank["questions"], registry, selection_rows=selection)
        pages = {render_core.ROLE_FILE[role]: render_core.page(ctx, role, "PAGES", render_core.DIGEST_SLOT)
                 for role in ("CORE1A", "CORE2")}
        pages["index.html"] = render_core.index_page(ctx, render_core.DIGEST_SLOT)
        if ctx.gaps:
            raise ValueError({"issue": issue, "render_gaps": ctx.gaps})
        digest = render_core._artifact_digest(pages)
        output = {name: text.replace(render_core.DIGEST_SLOT, digest).encode("utf-8")
                  for name, text in pages.items()}
        hashes = {name: sha(data) for name, data in output.items()}
        original_receipt = load(directory / "cycle-receipt.json")
        input_hashes = {}
        for source in (bank_path, package_path, manifest_path):
            relative = source.relative_to(repo).as_posix()
            committed = subprocess.check_output(["git", "-C", str(repo), "show", f"{basis}:{relative}"])
            if source.read_bytes() != committed:
                raise ValueError(f"ISS{issue}: committed canonical input changed: {relative}")
            input_hashes[relative] = sha(committed)
        receipt = {
            **original_receipt,
            "registry_version": registry["registry_version"],
            "render_digest": digest,
            "page_hashes": hashes,
            "render_gaps": ctx.gaps,
            "advisories": ctx.advisories,
            "render_basis": {
                "source_commit": basis,
                "authority_sha256": authorities,
                "authority_byte_policy": "UTF8_TEXT_LF",
                "canonical_input_sha256": input_hashes,
                "legacy_source_hashes": "Retained from predecessor receipt; not used as corrected-input digests.",
                "observation": "NEW_LOCAL_EXECUTION",
                "method": "PRODUCTION_RENDERER_API_WITH_LOCAL_SCHEMA_RESOLVER",
                "historical_artifact_snapshot": "46e91c9ec4285e14ca0db469eda281ff31df596a",
            },
            "browser": "NOT_RUN",
            "all_12_facets_independently_certified": False,
            "golden": False,
        }
        if args.write:
            for name, data in output.items():
                (directory / "rendered" / name).write_bytes(data)
            # Shell assets are part of the saved review closure, not inherited observations.
            for relative in ("css/modern-learner.css", "css/tablet-12-7.css",
                             "js/display-controls.js", "js/site-header.js"):
                target = directory / "rendered" / relative
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes((repo / "public" / relative).read_bytes().replace(b"\r\n", b"\n"))
            (directory / "cycle-receipt.json").write_text(
                json.dumps(receipt, indent=2, ensure_ascii=False) + "\n", encoding="utf-8", newline="\n")
            render_receipt_path = directory / "rendered/render-receipt.json"
            render_receipt = load(render_receipt_path)
            render_receipt.update({"digest": digest, "semantic_digest": render_core.render_digest(ctx),
                                   "gaps": ctx.gaps, "render_basis": receipt["render_basis"],
                                   "observation": "NEW_LOCAL_PRODUCTION_API_EXECUTION"})
            render_receipt_path.write_text(json.dumps(render_receipt, indent=2) + "\n",
                                           encoding="utf-8", newline="\n")
        rows.append({
            "issue": issue, "status": "REGENERATED" if args.write else "PROSPECTIVE",
            "render_digest": digest, "page_hashes": hashes,
            "previous_digest": original_receipt["render_digest"],
            "inputs_unchanged": True, "browser": "NOT_RUN", "golden": False,
        })
    report = {"schema": "blueprint-refresh/v1", "basis_commit": basis,
              "authority_sha256": authorities, "results": rows,
              "claim": "Current-authority regeneration; not historical receipt recovery or academic/browser acceptance."}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(json.dumps({"issues": [{"issue": r["issue"], "status": r["status"]} for r in rows]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
