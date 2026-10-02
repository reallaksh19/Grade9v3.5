"""The assurance of one product as it is staged for acceptance: its packages, and the pages built from them, through every verifier to a release decision.

accept_product.py asks this when the release policy's acceptance_gate is REQUIRED and no bundle was given, so that accepting a product does not mean assembling a
bundle by hand. The evidence, the bundle and the decision are written to build/assurance/<slug>/ (never into the trees they judge) and the decision is returned.

What is judged: each package the manifest names (package_refs; competitive banks are not packages and are not judged here), the staged PAGES render, and the staged
single-file page when there is one. Pages are judged where they will be served (public/), so a link to the site's stylesheet is checked against the site's stylesheet.
"""
from __future__ import annotations

import json
from pathlib import Path

from Shared.assurance import aggregate, contract, verifiers
from Shared.contracts import ContractError

POLICIES = ("canonical-admission-default", "learner-release-default")


def manifest_of(slug: str, repo: Path) -> tuple[Path, dict]:
    found = sorted((repo / "products").glob(f"*/{slug}.manifest.json"))
    if len(found) != 1:
        raise ContractError("PRODUCT_MANIFEST", f"expected exactly one manifest for {slug}, got {len(found)}")
    return found[0], json.loads(found[0].read_text(encoding="utf-8"))


def staged_projections(slug: str, manifest: dict, repo: Path) -> list[str]:
    """`ID=PATH` for what is staged for this product, relative to the repository."""
    subject = manifest["subject"].lower()
    pages = repo / "publication" / "products" / subject / slug
    if not (pages / "render-receipt.json").is_file():
        raise ContractError("PRODUCT_NOT_STAGED", f"nothing is staged for {slug} at {pages.relative_to(repo).as_posix()}: build it first (build_products.py build)")
    out = [f"{slug}={pages.relative_to(repo).as_posix()}"]
    single = repo / "publication" / "standalone" / "products" / subject / f"{slug}.html"
    if single.is_file():
        out.append(f"{slug}-standalone={single.relative_to(repo).as_posix()}")
    return out


def assure_staged(slug: str, repo: Path = contract.REPO, waivers: dict | None = None) -> dict:
    """The release decision for `slug` as staged, recomputed from evidence the verifiers have just written. Raises ContractError if nothing is staged."""
    _, manifest = manifest_of(slug, repo)
    packages = list(manifest.get("package_refs", []))
    projections = staged_projections(slug, manifest, repo)
    evidence_dir = repo / "build" / "assurance" / slug / "evidence"
    verifiers.run(repo, packages, projections, evidence_dir, clean=True)

    subjects = aggregate.package_subjects(packages, repo) + aggregate.projection_subjects(projections, repo)
    policies = aggregate.load_policies(list(POLICIES))
    records, problems = aggregate.collect(evidence_dir)
    evaluation = aggregate.evaluate(subjects, policies, records)
    evaluation.problems = problems + evaluation.problems
    bundle = aggregate.build_bundle(slug, subjects, policies, evaluation)
    decision = aggregate.evaluate_release(bundle, evidence_dir, policies, aggregate.default_waivers() if waivers is None else waivers, repo=repo)
    out = repo / "build" / "assurance" / slug
    contract.write_json(out / "bundle.json", bundle)
    contract.write_json(out / "eligibility.json", decision)
    return decision
