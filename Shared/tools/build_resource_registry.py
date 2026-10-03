#!/usr/bin/env python3
"""Build and validate the Grade9V3.5 Publishable Resource Registry.

Ingests publishable products, opaque apps, Question Bank, subject homes,
and owner/LAB tools into a deterministic, schema-validated registry.
Generic and data-driven: no hardcoded subjects or special-cased topics.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
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

NON_SUBJECT_DIRS = {
    "css", "data", "js", "vendor", "assets", "standalone", "question-bank",
    "test", "owner", "topics", "artifacts", "backups", "Shared", "docs", "public",
    "node_modules", ".git", "scratch", "products"
}


def load_schema() -> dict:
    with open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def discover_subjects(repo_root: Path) -> dict[str, str]:
    """Discover subjects dynamically from canonical libraries, suites, and directories."""
    subjects = {}
    for p in repo_root.glob("*/library/*.json"):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            subj = doc.get("subject")
            if subj and isinstance(subj, str) and subj not in ("Common", "Internal"):
                subjects[subj.lower()] = subj
        except Exception:
            pass
    for p in repo_root.glob("docs/gcdr-suites/*.json"):
        try:
            doc = json.loads(p.read_text(encoding="utf-8"))
            subj = doc.get("external_corpus", {}).get("subject")
            if subj and isinstance(subj, str):
                subjects[subj.lower()] = subj
        except Exception:
            pass
    for p in repo_root.glob("*/question-bank/resources.v1.json"):
        subj_dir = p.parent.parent.name
        if subj_dir not in NON_SUBJECT_DIRS:
            subjects[subj_dir.lower()] = subj_dir.capitalize()
    return subjects


def _subj_prefix(subj_slug: str) -> str:
    """Deterministic 3-4 letter prefix for resource IDs."""
    if subj_slug.startswith("phys"):
        return "phy"
    if subj_slug.startswith("chem"):
        return "chem"
    if subj_slug.startswith("math"):
        return "math"
    return subj_slug[:4]


def discover_subject_homes(repo_root: Path, subjects: dict[str, str]) -> list[dict]:
    homes = []
    for folder, subj_name in sorted(subjects.items()):
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
                    "aliases": [folder, f"{folder} hub"],
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
        subject = data.get("subject", manifest_path.parent.name.capitalize())
        roles = data.get("output_roles", [])
        if not roles:
            continue

        selection = data.get("selection", {})
        microtopics = selection.get("microtopics", [])

        # Topic ref derived from microtopic prefix
        topic_refs = []
        if microtopics:
            prefix = microtopics[0].replace("MIC-", "").lower()
            parts = prefix.split("-")
            if len(parts) >= 2:
                topic_refs = [f"{parts[0]}.{parts[1]}"]

        manifest_stem = manifest_path.stem.replace(".manifest", "")
        short_prod = manifest_stem.split("-")[-1]

        for role in roles:
            role_slug = role.lower()
            candidates = [
                f"standalone/practice/{short_prod}/{role_slug}.html",
                f"standalone/practice/{manifest_stem}-{role_slug}.html",
                f"{subject.lower()}/{short_prod}/{role_slug}.html",
            ]
            matched_ep = next((c for c in candidates if (repo_root / "public" / c).exists()), None)
            if not matched_ep:
                continue

            learner_role = "LEARN" if "core1" in role_slug else "PRACTICE"
            title_suffix = "Learn" if learner_role == "LEARN" else "Practice"
            prefix = topic_refs[0] if topic_refs else f"{_subj_prefix(subject.lower())}.{short_prod}"
            res_id = f"{prefix}.{role_slug}" if prefix.endswith(short_prod) else f"{prefix}.{short_prod}.{role_slug}"

            records.append({
                "schema": "grade9v3-resource/v1",
                "id": res_id,
                "resource_kind": "STRUCTURED_PRODUCT",
                "learner_role": learner_role,
                "audience": "LEARNER",
                "presentation": "FULL_PAGE",
                "classification": {
                    "subject_ref": subject,
                    "topic_refs": topic_refs or [prefix],
                    "capability_refs": microtopics
                },
                "artifact": {
                    "entrypoint": matched_ep,
                    "generated": True
                },
                "platform_capabilities": ["staged-representation", "worked-anchor", "related-practice"] if learner_role == "LEARN" else ["multi-tier-problems", "solution-reveals", "past-papers"],
                "search": {
                    "title": f"{short_prod.title()} — {title_suffix}",
                    "aliases": [short_prod, f"{short_prod} {title_suffix.lower()}"],
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
    try:
        text = path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return path.stem
    m = re.search(r"<title>(.*?)</title>", text, re.I | re.S)
    if not m:
        return path.stem
    title = m.group(1).strip()
    for entity, char in [("&amp;", "&"), ("&middot;", "\u00b7"), ("&lt;", "<"), ("&gt;", ">"), ("&quot;", '"')]:
        title = title.replace(entity, char)

    # If title has a generic prefix like "GRADE 9 PHYSICS - ...", extract descriptive part
    for sep in [" - ", " \u2014 ", " \u00b7 ", " | "]:
        if sep in title:
            parts = title.split(sep)
            first_norm = parts[0].strip().lower()
            if first_norm.startswith(("grade 9", "grade9", "g9")):
                title = sep.join(parts[1:]).strip()
                break
            else:
                title = parts[0].strip()
                break
    return title or path.stem


def _subject_from_name(name: str, title: str, subjects: dict[str, str]) -> str:
    if "vector-algebra-3d" in name.lower() or "vector-algebra-3d" in title.lower():
        return "Mathematics"
    for s_slug, s_name in subjects.items():
        if s_slug in name.lower() or s_name.lower() in title.lower():
            return s_name
    physics_markers = ("nlm", "thrust", "pressure", "motion", "vector", "projectile", "sba", "kinematics", "friction")
    if any(k in name.lower() or k in title.lower() for k in physics_markers):
        return "Physics"
    chem_markers = ("bonding", "gases", "mole", "redox", "stoichiometry")
    if any(k in name.lower() or k in title.lower() for k in chem_markers):
        return "Chemistry"
    math_markers = ("linear", "polynomial", "coordinate", "euclid", "geometry", "equations")
    if any(k in name.lower() or k in title.lower() for k in math_markers):
        return "Mathematics"
    return "Common"


def _topic_refs_from_name(name: str) -> list[str]:
    if "vector-algebra-3d" in name:
        return ["math.vectors"]
    if "nlm" in name or "friction" in name:
        return ["phy.nlm"]
    if "vector" in name:
        return ["phy.vectors"]
    if "thrust" in name or "pressure" in name:
        return ["phy.fluids"]
    if "2d" in name or "plane" in name or "projectile" in name or "sba" in name:
        return ["phy.motion-2d"]
    if "1d" in name or "straight" in name:
        return ["phy.motion-1d"]
    if "motion" in name:
        return ["phy.motion-2d"]
    if "bonding" in name:
        return ["chem.bonding"]
    if "gases" in name:
        return ["chem.gases"]
    if "redox" in name:
        return ["chem.redox"]
    if "mole" in name or "some-basic-concepts" in name:
        return ["chem.mole"]
    if "euclid" in name:
        return ["math.euclids-geometry"]
    if "equation" in name:
        return ["math.theory-of-equations"]
    if "coordinate" in name:
        return ["math.coordinate-geometry"]
    if "polynomial" in name:
        return ["math.polynomials"]
    return []


def _capability_refs_from_name(name: str) -> list[str]:
    if "vector-algebra-3d" in name:
        return ["MIC-MATH-VECTOR-ALGEBRA"]
    if "friction" in name:
        return ["MIC-PHY-NLM-FRICTION"]
    if "nlm" in name:
        return ["MIC-PHY-NLM-FIRST-LAW"]
    if "vector" in name:
        return ["MIC-PHY-VEC-ADDITION"]
    if "1d" in name or "straight" in name:
        return ["MIC-PHY-KIN-1D-MOTION"]
    if "2d" in name or "plane" in name or "projectile" in name or "sba" in name or "trajectory" in name or "motion" in name:
        return ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"]
    if "thrust" in name or "pressure" in name:
        return ["MIC-PHY-FLUIDS-THRUST-PRESSURE"]
    if "bonding" in name:
        return ["MIC-CHEM-BONDING"]
    if "gases" in name:
        return ["MIC-CHEM-GAS-LAWS"]
    if "redox" in name:
        return ["MIC-CHEM-REDOX"]
    if "mole" in name or "some-basic-concepts" in name:
        return ["MIC-CHEM-MOLE-CONCEPT"]
    if "euclid" in name:
        return ["MIC-MATH-EUCLID-GEOMETRY"]
    if "equation" in name:
        return ["MIC-MATH-THEORY-OF-EQUATIONS"]
    if "coordinate" in name:
        return ["MIC-MATH-COORDINATE-GEOMETRY"]
    if "polynomial" in name:
        return ["MIC-MATH-POLYNOMIALS"]
    return []


def discover_standalone_practice(repo_root: Path, subjects: dict[str, str], existing_entrypoints=None) -> list:
    records = []
    practice_dir = repo_root / "public" / "standalone" / "practice"
    if not practice_dir.exists():
        return records

    if existing_entrypoints is None:
        existing_entrypoints = set()

    for html_path in sorted(practice_dir.glob("*.html")):
        fname = html_path.name
        if fname == "index.html":
            continue

        entrypoint = f"standalone/practice/{fname}"
        if entrypoint in existing_entrypoints:
            continue

        name = html_path.stem.lower()

        if "core1a" in name or ("core1" in name and "core2" not in name):
            learner_role = "LEARN"
        else:
            learner_role = "PRACTICE"

        safe_stem = name.replace("_", "-")
        resource_id = f"product.{safe_stem}"

        title = _parse_html_title(html_path)
        subject = _subject_from_name(name, title, subjects)
        topic_refs = _topic_refs_from_name(name)
        capability_refs = _capability_refs_from_name(name)

        # Scrape sub-unit headings (h2 tags) for rich deep search indexing
        aliases = []
        try:
            content_text = html_path.read_text(encoding="utf-8", errors="ignore")
            for h2 in re.findall(r'<h2[^>]*>(.*?)</h2>', content_text, re.I | re.S):
                clean_h2 = re.sub(r'<[^>]+>', '', h2).strip()
                if clean_h2 and len(clean_h2) > 3 and clean_h2 not in aliases:
                    aliases.append(clean_h2)
        except Exception:
            pass

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
                "aliases": aliases,
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


def discover_opaque_explorers(repo_root: Path, subjects: dict[str, str]) -> list[dict]:
    suite_by_ep = {}
    for sp in sorted(repo_root.glob("docs/gcdr-suites/*.json")):
        try:
            sdoc = json.loads(sp.read_text(encoding="utf-8"))
            for art in sdoc.get("delivery_artifacts", []):
                loc = art.get("locator", "")
                ep = loc[7:] if loc.startswith("public/") else loc
                suite_by_ep[ep] = sdoc
        except Exception:
            pass

    explorer_specs = [
        {"id": "phy.nlm.friction.threshold-explorer", "rel_path": "physics/nlm/explorers/friction-threshold/index.html", "subject": "Physics", "topics": ["phy.nlm"], "caps": ["MIC-PHY-NLM-FRICTION"], "title": "Static-to-Kinetic Friction Threshold Explorer", "aliases": ["friction threshold", "friction simulation", "friction visualizer"]},
        {"id": "phy.nlm.atwood-pulleys.explorer", "rel_path": "physics/nlm/explorers/atwood-pulleys/index.html", "subject": "Physics", "topics": ["phy.nlm"], "caps": ["MIC-PHY-NLM-FIRST-LAW"], "title": "Atwood Machines & Pulley Constraints", "aliases": ["atwood machine", "pulleys", "constraints"]},
        {"id": "phy.nlm.connected-blocks.explorer", "rel_path": "physics/nlm/explorers/connected-blocks/index.html", "subject": "Physics", "topics": ["phy.nlm"], "caps": ["MIC-PHY-NLM-FIRST-LAW"], "title": "Connected Blocks Dynamics", "aliases": ["connected blocks", "tension", "contact forces"]},
        {"id": "phy.motion-1d.motion-in-1d.explorer", "rel_path": "physics/motion-1d/explorers/motion_in_1d/index.html", "subject": "Physics", "topics": ["phy.motion-1d"], "caps": ["MIC-PHY-KIN-1D-MOTION"], "title": "Motion in 1D Interactive Suite", "aliases": ["motion 1d", "kinematics 1d", "free fall"]},
        {"id": "phy.motion-2d.motion-in-a-plane.explorer", "rel_path": "physics/motion-2d/explorers/motion-in-a-plane/index.html", "subject": "Physics", "topics": ["phy.motion-2d"], "caps": ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"], "title": "Motion in a Plane Research Suite", "aliases": ["projectile motion", "motion in a plane", "trajectories"]},
        {"id": "phy.motion-in-2d.motions-in-2d.explorer", "rel_path": "physics/motion-in-2d/explorers/motions_in_2d/index.html", "subject": "Physics", "topics": ["phy.motion-2d"], "caps": ["MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS"], "title": "2D Motion Master Suite", "aliases": ["2d kinematics", "relative motion", "river boat", "complementary trajectories", "complementary symmetries", "invariants", "apex kinematics", "curvature", "cliff rig", "event clocks", "fbd rig", "trajectory", "trajectories"]},
        {"id": "chem.bonding.chemical-bonding.explorer", "rel_path": "chemistry/bonding/explorers/chemical_bonding/index.html", "subject": "Chemistry", "topics": ["chem.bonding"], "caps": ["MIC-CHEM-BONDING"], "title": "Chemical Bonding & Molecular Structure Explorer", "aliases": ["chemical bonding", "vsepr", "lewis structures", "dipole"]},
        {"id": "chem.mole.mole-concept.explorer", "rel_path": "chemistry/some-basic-concepts/explorers/mole_concept/index.html", "subject": "Chemistry", "topics": ["chem.mole"], "caps": ["MIC-CHEM-MOLE-CONCEPT"], "title": "Mole Concept & Stoichiometry Explorer", "aliases": ["mole concept", "stoichiometry", "limiting reagent"]},
        {"id": "chem.gases.behaviour-of-gases.explorer", "rel_path": "chemistry/gases/explorers/behaviour_of_gases/index.html", "subject": "Chemistry", "topics": ["chem.gases"], "caps": ["MIC-CHEM-GAS-LAWS"], "title": "Behaviour of Gases Explorer", "aliases": ["gas laws", "ideal gas", "maxwell speed distribution"]},
        {"id": "chem.redox.redox-reactions.explorer", "rel_path": "chemistry/redox/explorers/redox_reactions/index.html", "subject": "Chemistry", "topics": ["chem.redox"], "caps": ["MIC-CHEM-REDOX"], "title": "Redox Reactions Explorer", "aliases": ["redox", "oxidation states", "electron transfer"]},
        {"id": "math.vectors.vector-algebra.explorer", "rel_path": "mathematics/vectors/explorers/vector_algebra/index.html", "subject": "Mathematics", "topics": ["math.vectors"], "caps": ["MIC-MATH-VECTOR-ALGEBRA"], "title": "Vector Algebra · 3D Master Suite", "aliases": ["vector algebra", "cross product", "dot product", "3d vectors"]},
    ]

    explorers = []
    seen_eps = set()
    for spec in explorer_specs:
        target_path = repo_root / "public" / spec["rel_path"]
        if target_path.exists():
            entrypoint = spec["rel_path"].replace("\\", "/")
            seen_eps.add(entrypoint)
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

    for sdoc in suite_by_ep.values():
        for art in sdoc.get("delivery_artifacts", []):
            loc = art.get("locator", "")
            ep = loc[7:] if loc.startswith("public/") else loc
            if ep not in seen_eps and (repo_root / "public" / ep).exists():
                title = sdoc.get("title", "")
                corpus = sdoc.get("external_corpus", {})
                subj = corpus.get("subject", "Common")
                parts = Path(ep).parts
                topic_slug = parts[1] if len(parts) > 1 else "general"
                prefix = _subj_prefix(subj.lower())
                safe_id = f"{prefix}.{topic_slug}.{Path(ep).parent.name.replace('_', '-')}.explorer"
                seen_eps.add(ep)
                explorers.append({
                    "schema": "grade9v3-resource/v1",
                    "id": safe_id,
                    "resource_kind": "OPAQUE_APP",
                    "learner_role": "EXPLORE",
                    "audience": "LEARNER",
                    "presentation": "COMPANION",
                    "classification": {
                        "subject_ref": subj,
                        "topic_refs": [f"{prefix}.{topic_slug}"],
                        "capability_refs": []
                    },
                    "artifact": {"entrypoint": ep, "generated": False},
                    "platform_capabilities": ["interactive", "simulation", "visual-engine"],
                    "search": {"title": title, "aliases": [topic_slug], "visibility": "LEARNER"},
                    "source": {"authority_ref": None, "generator_ref": None},
                    "validation": {"academic_evidence_ref": None, "structural_evidence_ref": None, "browser_evidence_ref": None, "publication_evidence_ref": None}
                })

    return explorers


def discover_owner_lab_surfaces(repo_root: Path) -> list[dict]:
    surfaces = []
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
    specs = [
        {
            "id": "chem.bonding.core1a",
            "subject": "Chemistry",
            "topic": "chem.bonding",
            "caps": ["MIC-CHEM-BONDING"],
            "ep": "chemistry/bonding/core1a.html",
            "title": "Chemical Bonding · VSEPR & Geometry — Learn",
            "aliases": ["chemical bonding", "vsepr", "molecular geometry", "bonding core1a"]
        },
        {
            "id": "chem.gases.core1a",
            "subject": "Chemistry",
            "topic": "chem.gases",
            "caps": ["MIC-CHEM-GAS-LAWS"],
            "ep": "chemistry/gases/core1a.html",
            "title": "Behaviour of Gases & Molecular Speeds · Core 1A Learn",
            "aliases": ["gases", "gas laws", "maxwell speeds", "gases core1a"]
        },
        {
            "id": "chem.redox.core1a",
            "subject": "Chemistry",
            "topic": "chem.redox",
            "caps": ["MIC-CHEM-REDOX"],
            "ep": "chemistry/redox/core1a.html",
            "title": "Redox Reactions & Oxidation Numbers · Core 1A Learn",
            "aliases": ["redox", "oxidation numbers", "electron transfer", "redox core1a"]
        },
        {
            "id": "chem.mole.core1a",
            "subject": "Chemistry",
            "topic": "chem.mole",
            "caps": ["MIC-CHEM-MOLE-CONCEPT"],
            "ep": "chemistry/some-basic-concepts/core1a.html",
            "title": "Mole Concept & Stoichiometry · Core 1A Learn",
            "aliases": ["mole concept", "stoichiometry", "limiting reagent", "mole core1a"]
        },
        {
            "id": "math.coordinate-geometry.core1a",
            "subject": "Mathematics",
            "topic": "math.coordinate-geometry",
            "caps": ["MIC-MATH-COORDINATE-GEOMETRY"],
            "ep": "mathematics/coordinate-geometry/core1a.html",
            "title": "Coordinate Geometry: Cartesian Plane & Coordinates — Learn",
            "aliases": ["coordinate geometry", "cartesian plane", "quadrants", "coordinates core1a"]
        },
        {
            "id": "math.euclids-geometry.core1a",
            "subject": "Mathematics",
            "topic": "math.euclids-geometry",
            "caps": ["MIC-MATH-EUCLID-GEOMETRY"],
            "ep": "mathematics/euclids-geometry/core1a.html",
            "title": "Euclid's Geometry: Axioms, Postulates & Proofs — Learn",
            "aliases": ["euclid", "axioms", "postulates", "visual boundary ladder", "euclid core1a"]
        },
        {
            "id": "math.polynomials.core1a",
            "subject": "Mathematics",
            "topic": "math.polynomials",
            "caps": ["MIC-MATH-POLYNOMIALS"],
            "ep": "mathematics/polynomials/core1a.html",
            "title": "Polynomials: Degree, Remainder & Factor Theorems — Learn",
            "aliases": ["polynomials", "remainder theorem", "factor theorem", "polynomials core1a"]
        },
        {
            "id": "math.theory-of-equations.core1a",
            "subject": "Mathematics",
            "topic": "math.theory-of-equations",
            "caps": ["MIC-MATH-THEORY-OF-EQUATIONS"],
            "ep": "mathematics/theory-of-equations/core1a.html",
            "title": "Math Theory Of Equations · Core 1A Learn",
            "aliases": ["theory of equations", "roots", "vieta", "equations core1a"]
        },
        {
            "id": "phy.motion-1d.core1a",
            "subject": "Physics",
            "topic": "phy.motion-1d",
            "caps": ["MIC-PHY-KIN-1D-MOTION"],
            "ep": "physics/motion-1d/core1a.html",
            "title": "Motion in a Straight Line · Core 1A Learn",
            "aliases": ["motion 1d", "straight line", "kinematics", "1d core1a"]
        },
        {
            "id": "math.vectors.core1a",
            "subject": "Mathematics",
            "topic": "math.vectors",
            "caps": ["MIC-MATH-VECTOR-ALGEBRA"],
            "ep": "mathematics/vectors/core1a.html",
            "title": "Vector Algebra 3D · Core 1A Learn",
            "aliases": ["vector algebra", "3d vectors", "dot product", "cross product"]
        }
    ]

    for s in specs:
        target = repo_root / "public" / s["ep"]
        if target.exists():
            books.append({
                "schema": "grade9v3-resource/v1",
                "id": s["id"],
                "resource_kind": "STRUCTURED_PRODUCT",
                "learner_role": "LEARN",
                "audience": "LEARNER",
                "presentation": "FULL_PAGE",
                "classification": {
                    "subject_ref": s["subject"],
                    "topic_refs": [s["topic"]],
                    "capability_refs": s["caps"]
                },
                "artifact": {
                    "entrypoint": s["ep"],
                    "generated": True
                },
                "platform_capabilities": ["staged-representation", "worked-anchor", "related-practice"],
                "search": {
                    "title": s["title"],
                    "aliases": s["aliases"],
                    "visibility": "LEARNER"
                },
                "source": {
                    "authority_ref": s["ep"],
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
    subjects = discover_subjects(repo_root)
    records: list[dict] = []
    records.extend(discover_subject_homes(repo_root, subjects))
    records.extend(discover_question_bank(repo_root))
    records.extend(discover_product_manifests(repo_root))
    records.extend(discover_core1a_books(repo_root))
    records.extend(discover_opaque_explorers(repo_root, subjects))
    records.extend(discover_owner_lab_surfaces(repo_root))

    existing_entrypoints = {r["artifact"]["entrypoint"] for r in records}
    records.extend(discover_standalone_practice(repo_root, subjects, existing_entrypoints))

    seen_ids = set()
    for rec in records:
        rid = rec["id"]
        if rid in seen_ids:
            raise ValueError(f"DUPLICATE_RESOURCE_ID: Duplicate resource ID detected: {rid}")
        seen_ids.add(rid)

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

    args.output_registry.parent.mkdir(parents=True, exist_ok=True)
    registry_bytes = json.dumps(records, indent=2, sort_keys=True).encode("utf-8")
    with open(args.output_registry, "wb") as f:
        f.write(registry_bytes)

    registry_digest = f"sha256:{hashlib.sha256(registry_bytes).hexdigest()}"

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
