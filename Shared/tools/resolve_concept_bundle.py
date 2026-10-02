#!/usr/bin/env python3
"""Concept Bundle / Relationship Resolver for Grade9V3.5.

Derives concept-centred relationships (Learn, Practice, Interactive, Question Bank)
from registered resources and canonical academic capability identities.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

try:
    import jsonschema
except ImportError:
    jsonschema = None

BUNDLE_SCHEMA_PATH = REPO / "Shared" / "resources" / "concept-bundle.schema.json"


def load_bundle_schema() -> dict:
    with open(BUNDLE_SCHEMA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


CONCEPT_TITLES = {
    "MIC-PHY-NLM-FRICTION": "Limiting & Kinetic Friction",
    "MIC-PHY-NLM-FRICTION-QUANT": "Quantitative Friction & Connected Bodies",
    "MIC-PHY-NLM-FIRST-LAW": "First Law & Inertia",
    "MIC-PHY-KIN-1D-MOTION": "Motion in a Straight Line",
    "MIC-PHY-KIN-2D-INDEPENDENT-COMPONENTS": "Motion in a Plane & Projectiles",
    "MIC-PHY-VEC-ADDITION": "Vector Addition & Resolution",
    "MIC-PHY-FLUIDS-THRUST-PRESSURE": "Thrust & Hydrostatic Pressure",
    "MIC-CHEM-BONDING": "Chemical Bonding & Molecular Structure",
    "MIC-CHEM-GAS-LAWS": "Behaviour of Gases & Molecular Speeds",
    "MIC-CHEM-REDOX": "Redox Reactions & Oxidation States",
    "MIC-CHEM-MOLE-CONCEPT": "Mole Concept & Stoichiometry",
    "MIC-MATH-VECTOR-ALGEBRA": "Vector Algebra · 3D Engine",
}


def validate_relationship_integrity(registry: list[dict]) -> list[str]:
    """Detect broken relationships, unclassified resources, or ungrounded apps."""
    diagnostics = []
    seen_ids = set()

    for rec in registry:
        rid = rec.get("id", "")
        if rid in seen_ids:
            diagnostics.append(f"DUPLICATE_RESOURCE_ID: {rid}")
        seen_ids.add(rid)

        role = rec.get("learner_role")
        audience = rec.get("audience")
        kind = rec.get("resource_kind")
        classification = rec.get("classification", {})
        caps = classification.get("capability_refs", [])

        # Learner resource without classification
        if audience == "LEARNER" and role in ("LEARN", "PRACTICE", "EXPLORE") and not caps:
            # Subject home and QB don't strictly require microtopics, but topic/concept resources do
            if "home" not in rid and "question-bank" not in rid:
                diagnostics.append(f"LEARNER_RESOURCE_WITHOUT_CLASSIFICATION: Resource {rid} has empty capability_refs")

        # Learner app without learning refs
        if kind == "OPAQUE_APP" and audience == "LEARNER" and not caps:
            diagnostics.append(f"LEARNER_APP_WITHOUT_LEARNING_REF: Opaque app {rid} missing capability_refs")

    return diagnostics


def resolve_bundle(concept_ref: str, registry: list[dict]) -> dict:
    """Resolve the complete concept bundle for a given concept reference."""
    learn_items = []
    practice_items = []
    interactive_items = []
    subject_ref = "Physics"
    topic_ref = "phy.nlm"

    for rec in registry:
        caps = rec.get("classification", {}).get("capability_refs", [])
        if concept_ref not in caps:
            continue

        subj = rec.get("classification", {}).get("subject_ref", "Physics")
        topics = rec.get("classification", {}).get("topic_refs", ["phy.nlm"])
        if subj:
            subject_ref = subj
        if topics:
            topic_ref = topics[0]

        role = rec.get("learner_role")
        ep = rec.get("artifact", {}).get("entrypoint", "")
        title = rec.get("search", {}).get("title", rec.get("id"))
        rid = rec.get("id")

        if role == "LEARN":
            learn_items.append({
                "resource_ref": rid,
                "entrypoint": ep,
                "title": title
            })
        elif role == "PRACTICE":
            practice_items.append({
                "resource_ref": rid,
                "entrypoint": ep,
                "title": title,
                "question_count": 10 if "core2" in rid else 5
            })
        elif role == "EXPLORE":
            interactive_items.append({
                "resource_ref": rid,
                "entrypoint": ep,
                "title": title
            })

    title = CONCEPT_TITLES.get(concept_ref, concept_ref.replace("MIC-", "").replace("-", " ").title())

    bundle = {
        "schema": "concept-bundle/v1",
        "concept_ref": concept_ref,
        "subject_ref": subject_ref,
        "topic_ref": topic_ref,
        "title": title,
        "learn": learn_items,
        "practice": practice_items,
        "interactive": interactive_items,
        "question_bank": {
            "filter": {
                "capability_ref": concept_ref
            },
            "url": f"question-bank/index.html?capability={concept_ref}"
        }
    }
    return bundle


def resolve_all_bundles(registry: list[dict]) -> list[dict]:
    # Collect all unique capability refs across all resources
    all_concepts = set()
    for rec in registry:
        caps = rec.get("classification", {}).get("capability_refs", [])
        for c in caps:
            all_concepts.add(c)

    bundles = []
    for concept in sorted(all_concepts):
        bundle = resolve_bundle(concept, registry)
        bundles.append(bundle)

    bundles.sort(key=lambda b: b["concept_ref"])
    return bundles


def main():
    parser = argparse.ArgumentParser(description="Resolve Grade9V3.5 Concept Bundles")
    parser.add_argument("--registry", type=Path, default=REPO / "public" / "data" / "resource-registry.v1.json")
    parser.add_argument("--output", type=Path, default=REPO / "public" / "data" / "concept-bundles.v1.json")
    parser.add_argument("--concept", type=str, help="Resolve only a specific concept ref")
    parser.add_argument("--enforce", action="store_true", help="Exit 1 on integrity diagnostics")
    args = parser.parse_args()

    if not args.registry.exists():
        print(f"ERROR: Registry file not found: {args.registry}")
        sys.exit(1)

    with open(args.registry, "r", encoding="utf-8") as f:
        registry = json.load(f)

    diagnostics = validate_relationship_integrity(registry)
    if diagnostics:
        print(f"Integrity findings ({len(diagnostics)}):")
        for d in diagnostics:
            print(f"  {d}")
        if args.enforce:
            sys.exit(1)

    schema = load_bundle_schema()

    if args.concept:
        bundle = resolve_bundle(args.concept, registry)
        if jsonschema:
            jsonschema.validate(instance=bundle, schema=schema)
        print(json.dumps(bundle, indent=2))
        return

    bundles = resolve_all_bundles(registry)
    for b in bundles:
        if jsonschema:
            jsonschema.validate(instance=b, schema=schema)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(bundles, f, indent=2, sort_keys=True)

    print(f"Successfully resolved {len(bundles)} concept bundles to {args.output}")


if __name__ == "__main__":
    main()
