#!/usr/bin/env python3
"""Build and validate the Grade9V3.5 Publishable Resource Registry.

Ingests publishable products, opaque apps, Question Bank, subject homes,
and owner/LAB tools into a deterministic, schema-validated registry.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

try:
    import jsonschema
except ImportError:
    jsonschema = None

SCHEMA_PATH = REPO / "Shared" / "resources" / "resource.schema.json"


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_subject_homes(repo_root: Path) -> list[dict]:
    homes = []
    subjects = [("Physics", "physics"), ("Chemistry", "chemistry"), ("Mathematics", "mathematics")]
    for subj_name, folder in subjects:
        entry = f"{folder}/index.html"
        full_path = repo_root / "public" / entry
        if full_path.exists() or (repo_root / entry).exists():
            homes.append({
                "schema": "grade9v3-resource/v1",
                "id": f"{folder}.home",
                "resource_kind": "STRUCTURED_PRODUCT",
                "learner_role": "LEARN",
                "audience": "LEARNER",
                "presentation": "FULL_PAGE",
                "classification": {
                    "subject_ref": subj_name,
                    "topic_refs": [],
                    "capability_refs": []
                },
                "artifact": {
                    "entrypoint": entry,
                    "generated": False
                },
                "platform_capabilities": ["subject-hub", "topic-index"],
                "search": {
                    "title": f"{subj_name} Subject Hub",
                    "aliases": [subj_name.lower(), f"{subj_name.lower()} hub"],
                    "visibility": "LEARNER"
                },
                "source": {
                    "authority_ref": f"{subj_name}/adapter/CoreContracts.json",
                    "generator_ref": None
                },
                "validation": {
                    "academic_evidence_ref": None,
                    "structural_evidence_ref": None,
                    "browser_evidence_ref": None,
                    "publication_evidence_ref": None
                }
            })
    return homes


def discover_question_bank(repo_root: Path) -> list[dict]:
    qb = []
    entry = "question-bank/index.html"
    if (repo_root / "public" / entry).exists() or (repo_root / entry).exists():
        qb.append({
            "schema": "grade9v3-resource/v1",
            "id": "common.question-bank",
            "resource_kind": "QUESTION_COLLECTION",
            "learner_role": "QUESTION_BANK",
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": "Common",
                "topic_refs": [],
                "capability_refs": []
            },
            "artifact": {
                "entrypoint": entry,
                "generated": True
            },
            "platform_capabilities": ["search", "filter", "multi-tier", "latex-math"],
            "search": {
                "title": "Question Bank",
                "aliases": ["question bank", "qb", "past papers", "problems", "pyq"],
                "visibility": "LEARNER"
            },
            "source": {
                "authority_ref": "products/question-bank/manifest.json",
                "generator_ref": "Shared/tools/build_qb_tablet_standalone.py"
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })
    return qb


def discover_product_manifests(repo_root: Path) -> list[dict]:
    records = []
    manifest_dir = repo_root / "products"
    if not manifest_dir.exists():
        return records

    for manifest_path in sorted(manifest_dir.glob("*/*.manifest.json")):
        try:
            with open(manifest_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            continue

        product_id = data.get("product_id", "")
        subject = data.get("subject", "Common")
        roles = data.get("output_roles", [])
        selection = data.get("selection", {})
        microtopics = selection.get("microtopics", [])

        # Topic ref derived from microtopic prefix or product id
        topic_refs = []
        if microtopics:
            prefix = microtopics[0].replace("MIC-", "").lower()
            parts = prefix.split("-")
            if len(parts) >= 2:
                topic_refs = [f"{parts[0]}.{parts[1]}"]

        clean_prod = product_id.lower().replace("product-", "").replace("-", ".")

        # Friction specific naming or general product mapping
        if "friction" in product_id.lower():
            if "CORE1A" in roles:
                records.append({
                    "schema": "grade9v3-resource/v1",
                    "id": "phy.nlm.friction.core1a",
                    "resource_kind": "STRUCTURED_PRODUCT",
                    "learner_role": "LEARN",
                    "audience": "LEARNER",
                    "presentation": "FULL_PAGE",
                    "classification": {
                        "subject_ref": subject,
                        "topic_refs": topic_refs or ["phy.nlm"],
                        "capability_refs": microtopics
                    },
                    "artifact": {
                        "entrypoint": "standalone/practice/friction/core1a.html",
                        "generated": True
                    },
                    "platform_capabilities": ["staged-representation", "worked-anchor", "related-practice"],
                    "search": {
                        "title": "Friction — Learn",
                        "aliases": ["friction", "friction learn", "limiting friction"],
                        "visibility": "LEARNER"
                    },
                    "source": {
                        "authority_ref": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
                        "generator_ref": "Shared/tools/render_core.py"
                    },
                    "validation": {
                        "academic_evidence_ref": None,
                        "structural_evidence_ref": None,
                        "browser_evidence_ref": None,
                        "publication_evidence_ref": None
                    }
                })
            if "CORE2" in roles:
                records.append({
                    "schema": "grade9v3-resource/v1",
                    "id": "phy.nlm.friction.core2",
                    "resource_kind": "STRUCTURED_PRODUCT",
                    "learner_role": "PRACTICE",
                    "audience": "LEARNER",
                    "presentation": "FULL_PAGE",
                    "classification": {
                        "subject_ref": subject,
                        "topic_refs": topic_refs or ["phy.nlm"],
                        "capability_refs": microtopics
                    },
                    "artifact": {
                        "entrypoint": "standalone/practice/friction/core2.html",
                        "generated": True
                    },
                    "platform_capabilities": ["multi-tier-problems", "solution-reveals", "past-papers"],
                    "search": {
                        "title": "Friction — Practice",
                        "aliases": ["friction practice", "friction pyq", "friction problems"],
                        "visibility": "LEARNER"
                    },
                    "source": {
                        "authority_ref": str(manifest_path.relative_to(repo_root)).replace("\\", "/"),
                        "generator_ref": "Shared/tools/render_core.py"
                    },
                    "validation": {
                        "academic_evidence_ref": None,
                        "structural_evidence_ref": None,
                        "browser_evidence_ref": None,
                        "publication_evidence_ref": None
                    }
                })
    return records


def discover_opaque_explorers(repo_root: Path) -> list[dict]:
    explorers = []
    # Friction Threshold explorer
    fric_exp = repo_root / "public" / "physics" / "nlm" / "explorers" / "friction-threshold" / "index.html"
    if fric_exp.exists():
        explorers.append({
            "schema": "grade9v3-resource/v1",
            "id": "phy.nlm.friction.threshold-explorer",
            "resource_kind": "OPAQUE_APP",
            "learner_role": "EXPLORE",
            "audience": "LEARNER",
            "presentation": "COMPANION",
            "classification": {
                "subject_ref": "Physics",
                "topic_refs": ["phy.nlm"],
                "capability_refs": ["MIC-PHY-NLM-FRICTION"]
            },
            "artifact": {
                "entrypoint": "physics/nlm/explorers/friction-threshold/index.html",
                "generated": False
            },
            "platform_capabilities": ["interactive", "svg-animation", "parameter-control"],
            "search": {
                "title": "Static-to-Kinetic Friction Threshold Explorer",
                "aliases": ["friction threshold", "friction simulation", "friction visualizer"],
                "visibility": "LEARNER"
            },
            "source": {
                "authority_ref": None,
                "generator_ref": None
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })
    return explorers


def discover_owner_lab_surfaces(repo_root: Path) -> list[dict]:
    surfaces = []
    # Test Atlas
    atlas = repo_root / "public" / "test" / "atlas"
    if atlas.exists():
        surfaces.append({
            "schema": "grade9v3-resource/v1",
            "id": "owner.test.atlas",
            "resource_kind": "OWNER_TOOL",
            "learner_role": "NONE",
            "audience": "OWNER",
            "presentation": "INTERNAL_HOST",
            "classification": {
                "subject_ref": "Internal",
                "topic_refs": [],
                "capability_refs": []
            },
            "artifact": {
                "entrypoint": "test/atlas/index.html",
                "generated": True
            },
            "platform_capabilities": ["authoring", "validation-matrix"],
            "search": {
                "title": "Authoring Test Atlas",
                "aliases": ["atlas", "test atlas"],
                "visibility": "EXCLUDED"
            },
            "source": {
                "authority_ref": None,
                "generator_ref": None
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })

    # Test Rungs
    rungs = repo_root / "public" / "test" / "rungs"
    if rungs.exists():
        surfaces.append({
            "schema": "grade9v3-resource/v1",
            "id": "owner.test.rungs",
            "resource_kind": "OWNER_TOOL",
            "learner_role": "NONE",
            "audience": "OWNER",
            "presentation": "INTERNAL_HOST",
            "classification": {
                "subject_ref": "Internal",
                "topic_refs": [],
                "capability_refs": []
            },
            "artifact": {
                "entrypoint": "test/rungs/index.html",
                "generated": True
            },
            "platform_capabilities": ["pedagogical-rungs", "authoring"],
            "search": {
                "title": "Authoring Test Rungs",
                "aliases": ["rungs"],
                "visibility": "EXCLUDED"
            },
            "source": {
                "authority_ref": None,
                "generator_ref": None
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })
    return surfaces


def build_registry(repo_root: Path) -> list[dict]:
    records: list[dict] = []
    records.extend(discover_subject_homes(repo_root))
    records.extend(discover_question_bank(repo_root))
    records.extend(discover_product_manifests(repo_root))
    records.extend(discover_opaque_explorers(repo_root))
    records.extend(discover_owner_lab_surfaces(repo_root))

    # Verify duplicate IDs
    seen_ids = set()
    for rec in records:
        rid = rec["id"]
        if rid in seen_ids:
            raise ValueError(f"DUPLICATE_RESOURCE_ID: Duplicate resource ID detected: {rid}")
        seen_ids.add(rid)

    # Sort deterministically by id
    records.sort(key=lambda r: r["id"])
    return records


def validate_records(records: list[dict], schema: dict) -> None:
    for rec in records:
        if jsonschema:
            jsonschema.validate(instance=rec, schema=schema)
        else:
            for req in schema["required"]:
                if req not in rec:
                    raise ValueError(f"Missing required field: {req} in {rec.get('id')}")


def main():
    parser = argparse.ArgumentParser(description="Build and validate Grade9V3.5 Resource Registry")
    parser.add_argument("--repo-root", type=Path, default=REPO, help="Repository root path")
    parser.add_argument("--output-registry", type=Path, default=REPO / "public" / "data" / "resource-registry.v1.json")
    parser.add_argument("--output-manifest", type=Path, default=REPO / "public" / "data" / "resource-registry-manifest.v1.json")
    parser.add_argument("--enforce", action="store_true", help="Exit 1 on broken entrypoints or validation errors")
    args = parser.parse_args()

    schema = load_schema()
    records = build_registry(args.repo_root)
    validate_records(records, schema)

    # Verify entrypoints
    broken_entrypoints = []
    for rec in records:
        ep = rec["artifact"]["entrypoint"]
        full_ep = args.repo_root / "public" / ep
        if not full_ep.exists() and not (args.repo_root / ep).exists():
            broken_entrypoints.append((rec["id"], ep))

    if broken_entrypoints:
        print(f"WARNING: {len(broken_entrypoints)} broken entrypoint(s) detected:")
        for rid, ep in broken_entrypoints:
            print(f"  [{rid}] -> {ep} (not found)")
        if args.enforce:
            sys.exit(1)

    # Write registry JSON
    args.output_registry.parent.mkdir(parents=True, exist_ok=True)
    registry_bytes = json.dumps(records, indent=2, sort_keys=True).encode("utf-8")
    with open(args.output_registry, "wb") as f:
        f.write(registry_bytes)

    registry_digest = f"sha256:{hashlib.sha256(registry_bytes).hexdigest()}"

    # Write manifest JSON
    manifest = {
        "schema": "resource-registry-manifest/v1",
        "generator": {
            "name": "build_resource_registry",
            "version": "1.0.0"
        },
        "registry_digest": registry_digest,
        "record_count": len(records),
        "resource_ids": [r["id"] for r in records],
        "broken_entrypoints": [r[0] for r in broken_entrypoints],
        "generated_at": datetime.now(timezone.utc).isoformat()
    }
    with open(args.output_manifest, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, sort_keys=True)

    print(f"Successfully generated Resource Registry:")
    print(f"  Total records: {len(records)}")
    print(f"  Registry path: {args.output_registry}")
    print(f"  Manifest path: {args.output_manifest}")
    print(f"  Digest: {registry_digest}")


if __name__ == "__main__":
    main()
