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


def _parse_html_title(path: Path) -> str:
    """Extract and clean the <title> tag text from an HTML file."""
    import re as _re
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    m = _re.search(r"<title>(.*?)</title>", text, _re.IGNORECASE | _re.DOTALL)
    if not m:
        return path.stem
    title = m.group(1).strip()
    # Decode common HTML entities
    for entity, char in [("&amp;", "&"), ("&middot;", "\u00b7"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        title = title.replace(entity, char)
    # Truncate after first long separator
    for sep in [" | ", " \u00b7 ", " \u2014 ", " - "]:
        if sep in title:
            title = title.split(sep)[0].strip()
            break
    return title or path.stem


def _subject_from_name(name: str) -> str:
    if any(k in name for k in ("physics", "nlm", "motion", "thrust", "friction", "vector", "projectile", "sba")):
        return "Physics"
    if "chem" in name:
        return "Chemistry"
    if "math" in name or "equation" in name:
        return "Mathematics"
    return "Physics"


def _topic_refs_from_name(name: str) -> list:
    if "nlm" in name:
        return ["phy.nlm"]
    if "vector" in name:
        return ["phy.vectors"]
    if "thrust" in name or "pressure" in name:
        return ["phy.fluids"]
    if "projectile" in name:
        return ["phy.motion-2d"]
    if "2d" in name or "plane" in name:
        return ["phy.motion-2d"]
    if "1d" in name or "straight" in name:
        return ["phy.motion-1d"]
    if "motion" in name:
        return ["phy.motion"]
    return []


def _capability_refs_from_name(name: str) -> list:
    if "friction" in name:
        return ["MIC-PHY-NLM-FRICTION"]
    if "nlm" in name:
        return ["MIC-PHY-NLM-FIRST-LAW"]
    if "vector" in name:
        return ["MIC-PHY-VEC-ADDITION"]
    if "1d" in name or "straight" in name:
        return ["MIC-PHY-KIN-1D-MOTION"]
    if "2d" in name or "plane" in name or "projectile" in name or "sba" in name or "trajectory" in name:
        return ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"]
    if "thrust" in name or "pressure" in name:
        return ["MIC-PHY-FLUIDS-THRUST-PRESSURE"]
    return ["MIC-PHY-GENERAL-PRACTICE"]


def discover_standalone_practice(repo_root: Path, existing_entrypoints=None) -> list:
    """Auto-discover all standalone HTML files in public/standalone/practice/.

    Excludes:
    - index.html (navigation hub, not a product)
    - Files whose entrypoint is already registered (checked via existing_entrypoints set)
    - Files inside the friction/ subdirectory (handled by discover_product_manifests)
    """
    records = []
    practice_dir = repo_root / "public" / "standalone" / "practice"
    if not practice_dir.exists():
        return records

    if existing_entrypoints is None:
        existing_entrypoints = set()

    for html_path in sorted(practice_dir.glob("*.html")):
        fname = html_path.name
        # Skip navigation index
        if fname == "index.html":
            continue

        entrypoint = f"standalone/practice/{fname}"
        if entrypoint in existing_entrypoints:
            continue

        name = html_path.stem.lower()

        # learner_role from filename
        if "core1a" in name or ("core1" in name and "core2" not in name):
            learner_role = "LEARN"
        else:
            learner_role = "PRACTICE"

        # Generate schema-valid lowercase ID
        safe_stem = name.replace("_", "-")
        resource_id = f"product.{safe_stem}"

        title = _parse_html_title(html_path)
        subject = _subject_from_name(name)
        topic_refs = _topic_refs_from_name(name)
        capability_refs = _capability_refs_from_name(name)

        records.append({
            "schema": "grade9v3-resource/v1",
            "id": resource_id,
            "resource_kind": "STRUCTURED_PRODUCT",
            "learner_role": learner_role,
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": subject,
                "topic_refs": topic_refs,
                "capability_refs": capability_refs
            },
            "artifact": {
                "entrypoint": entrypoint,
                "generated": True
            },
            "platform_capabilities": [],
            "search": {
                "title": title,
                "aliases": [],
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

    return records


def discover_opaque_explorers(repo_root: Path) -> list[dict]:
    explorers = []

    explorer_specs = [
        # Physics
        {
            "id": "phy.nlm.friction.threshold-explorer",
            "rel_path": "public/physics/nlm/explorers/friction-threshold/index.html",
            "subject": "Physics",
            "topics": ["phy.nlm"],
            "caps": ["MIC-PHY-NLM-FRICTION"],
            "title": "Static-to-Kinetic Friction Threshold Explorer",
            "aliases": ["friction threshold", "friction simulation", "friction visualizer"]
        },
        {
            "id": "phy.nlm.atwood-pulleys.explorer",
            "rel_path": "public/physics/nlm/explorers/atwood-pulleys/index.html",
            "subject": "Physics",
            "topics": ["phy.nlm"],
            "caps": ["MIC-PHY-NLM-FIRST-LAW"],
            "title": "Atwood Machines & Pulley Constraints",
            "aliases": ["atwood machine", "pulleys", "constraints"]
        },
        {
            "id": "phy.nlm.connected-blocks.explorer",
            "rel_path": "public/physics/nlm/explorers/connected-blocks/index.html",
            "subject": "Physics",
            "topics": ["phy.nlm"],
            "caps": ["MIC-PHY-NLM-FIRST-LAW"],
            "title": "Connected Blocks Dynamics",
            "aliases": ["connected blocks", "tension", "contact forces"]
        },
        {
            "id": "phy.motion-1d.motion-in-1d.explorer",
            "rel_path": "public/physics/motion-1d/explorers/motion_in_1d/index.html",
            "subject": "Physics",
            "topics": ["phy.motion-1d"],
            "caps": ["MIC-PHY-KIN-1D-MOTION"],
            "title": "Motion in 1D Interactive Suite",
            "aliases": ["motion 1d", "kinematics 1d", "free fall"]
        },
        {
            "id": "phy.motion-2d.motion-in-a-plane.explorer",
            "rel_path": "public/physics/motion-2d/explorers/motion-in-a-plane/index.html",
            "subject": "Physics",
            "topics": ["phy.motion-2d"],
            "caps": ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"],
            "title": "Motion in a Plane Research Suite",
            "aliases": ["projectile motion", "motion in a plane", "trajectories"]
        },
        {
            "id": "phy.motion-in-2d.motions-in-2d.explorer",
            "rel_path": "public/physics/motion-in-2d/explorers/motions_in_2d/index.html",
            "subject": "Physics",
            "topics": ["phy.motion-2d"],
            "caps": ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"],
            "title": "2D Motion Master Suite",
            "aliases": ["2d kinematics", "relative motion", "river boat"]
        },
        # Chemistry
        {
            "id": "chem.bonding.chemical-bonding.explorer",
            "rel_path": "public/chemistry/bonding/explorers/chemical_bonding/index.html",
            "subject": "Chemistry",
            "topics": ["chem.bonding"],
            "caps": ["MIC-CHEM-BONDING"],
            "title": "Chemical Bonding & Molecular Structure Explorer",
            "aliases": ["chemical bonding", "vsepr", "lewis structures", "dipole"]
        },
        {
            "id": "chem.mole.mole-concept.explorer",
            "rel_path": "public/chemistry/some-basic-concepts/explorers/mole_concept/index.html",
            "subject": "Chemistry",
            "topics": ["chem.mole"],
            "caps": ["MIC-CHEM-MOLE-CONCEPT"],
            "title": "Mole Concept & Stoichiometry Explorer",
            "aliases": ["mole concept", "stoichiometry", "limiting reagent"]
        },
        {
            "id": "chem.gases.behaviour-of-gases.explorer",
            "rel_path": "public/chemistry/gases/explorers/behaviour_of_gases/index.html",
            "subject": "Chemistry",
            "topics": ["chem.gases"],
            "caps": ["MIC-CHEM-GAS-LAWS"],
            "title": "Behaviour of Gases Explorer",
            "aliases": ["gas laws", "ideal gas", "maxwell speed distribution"]
        },
        {
            "id": "chem.redox.redox-reactions.explorer",
            "rel_path": "public/chemistry/redox/explorers/redox_reactions/index.html",
            "subject": "Chemistry",
            "topics": ["chem.redox"],
            "caps": ["MIC-CHEM-REDOX"],
            "title": "Redox Reactions Explorer",
            "aliases": ["redox", "oxidation states", "electron transfer"]
        },
        # Mathematics
        {
            "id": "math.vectors.vector-algebra.explorer",
            "rel_path": "public/mathematics/vectors/explorers/vector_algebra/index.html",
            "subject": "Mathematics",
            "topics": ["math.vectors"],
            "caps": ["MIC-MATH-VECTOR-ALGEBRA"],
            "title": "Vector Algebra · 3D Master Suite",
            "aliases": ["vector algebra", "cross product", "dot product", "3d vectors"]
        }
    ]

    for spec in explorer_specs:
        target_path = repo_root / spec["rel_path"]
        if target_path.exists():
            entrypoint = spec["rel_path"].replace("public/", "").replace("\\", "/")
            explorers.append({
                "schema": "grade9v3-resource/v1",
                "id": spec["id"],
                "resource_kind": "OPAQUE_APP",
                "learner_role": "EXPLORE",
                "audience": "LEARNER",
                "presentation": "COMPANION",
                "classification": {
                    "subject_ref": spec["subject"],
                    "topic_refs": spec["topics"],
                    "capability_refs": spec["caps"]
                },
                "artifact": {
                    "entrypoint": entrypoint,
                    "generated": False
                },
                "platform_capabilities": ["interactive", "simulation", "visual-engine"],
                "search": {
                    "title": spec["title"],
                    "aliases": spec["aliases"],
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


def discover_core1a_books(repo_root: Path) -> list[dict]:
    books = []
    # Chemistry Core 1A: Chemical Bonding
    chem_c1a = repo_root / "public" / "chemistry" / "bonding" / "core1a.html"
    if chem_c1a.exists():
        books.append({
            "schema": "grade9v3-resource/v1",
            "id": "chem.bonding.core1a",
            "resource_kind": "STRUCTURED_PRODUCT",
            "learner_role": "LEARN",
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": "Chemistry",
                "topic_refs": ["chem.bonding"],
                "capability_refs": ["MIC-CHEM-BONDING"]
            },
            "artifact": {
                "entrypoint": "chemistry/bonding/core1a.html",
                "generated": True
            },
            "platform_capabilities": ["staged-representation", "worked-anchor", "related-practice"],
            "search": {
                "title": "Chemical Bonding · VSEPR & Geometry — Learn",
                "aliases": ["chemical bonding", "vsepr", "molecular geometry", "bonding core1a"],
                "visibility": "LEARNER"
            },
            "source": {
                "authority_ref": "chemistry/bonding/core1a.html",
                "generator_ref": "Shared/tools/build_learner_ui.py"
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })

    # Mathematics Core 1A: Vector Algebra
    math_c1a = repo_root / "public" / "mathematics" / "vectors" / "core1a.html"
    if math_c1a.exists():
        books.append({
            "schema": "grade9v3-resource/v1",
            "id": "math.vectors.core1a",
            "resource_kind": "STRUCTURED_PRODUCT",
            "learner_role": "LEARN",
            "audience": "LEARNER",
            "presentation": "FULL_PAGE",
            "classification": {
                "subject_ref": "Mathematics",
                "topic_refs": ["math.vectors"],
                "capability_refs": ["MIC-MATH-VECTOR-ALGEBRA"]
            },
            "artifact": {
                "entrypoint": "mathematics/vectors/core1a.html",
                "generated": True
            },
            "platform_capabilities": ["staged-representation", "worked-anchor", "related-practice"],
            "search": {
                "title": "Vector Algebra · Resolution & Components — Learn",
                "aliases": ["vector algebra", "vector resolution", "orthogonal components", "vectors core1a"],
                "visibility": "LEARNER"
            },
            "source": {
                "authority_ref": "mathematics/vectors/core1a.html",
                "generator_ref": "Shared/tools/build_learner_ui.py"
            },
            "validation": {
                "academic_evidence_ref": None,
                "structural_evidence_ref": None,
                "browser_evidence_ref": None,
                "publication_evidence_ref": None
            }
        })
    return books


def build_registry(repo_root: Path) -> list[dict]:
    records: list[dict] = []
    records.extend(discover_subject_homes(repo_root))
    records.extend(discover_question_bank(repo_root))
    records.extend(discover_product_manifests(repo_root))
    records.extend(discover_core1a_books(repo_root))
    records.extend(discover_opaque_explorers(repo_root))
    records.extend(discover_owner_lab_surfaces(repo_root))

    # Collect already-registered entrypoints before auto-discovering standalone files
    existing_entrypoints = {r["artifact"]["entrypoint"] for r in records}
    records.extend(discover_standalone_practice(repo_root, existing_entrypoints))

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
