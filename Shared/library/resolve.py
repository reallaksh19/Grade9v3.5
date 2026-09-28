"""Index library packages, resolve their references, and retrieve a relevant slice.

An author should receive the slice their bucket actually needs -- its microtopics,
the relations and representations those cite, the capabilities they assume and the
questions bound to them -- not the whole library. Handing over everything is how a
packet becomes unreadable and a dependency goes unnoticed.

Records may reference records in other packages. Identity is therefore global: two
packages may not define the same id, and a reference that resolves nowhere is an
error rather than a silently missing edge.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from Shared.contracts import load, require

COLLECTIONS = ("resources", "capabilities", "microtopics", "relations", "representations",
               "application_contexts", "question_families", "questions", "teaching_routes",
               "practice_profiles", "buckets", "data")
# An internal reference looks like a governed identifier. A value that does not --
# a file path, a URL, a prose instruction -- is external by construction and is not
# expected to resolve inside the library.
INTERNAL_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)+$")
PREREQUISITE_FIELDS = ("prerequisite_refs",)


def build_index(packages: list[dict]) -> dict:
    records: dict[str, dict] = {}
    owner: dict[str, str] = {}
    for package in packages:
        pid = package.get("package_id")
        for collection in COLLECTIONS:
            for row in package.get(collection, []):
                rid = row.get("id")
                require(isinstance(rid, str) and rid, "LIBRARY_RECORD_ID_REQUIRED", f"{pid}:{collection}")
                require(rid not in records, "LIBRARY_DUPLICATE_ID",
                        f"{rid} defined in {owner.get(rid)} and {pid}")
                records[rid] = {**row, "_collection": collection, "_package": pid}
                owner[rid] = pid
    return records


# References that deliberately leave the library. A gate relation is owned by the
# engineering registry, so resolving it against library records would report every
# correctly bound relation as a dangling reference. A learner profile leaves for a
# different reason: a learner is not a property of a physics package, and the two that
# lived inside one meant the same learner studying a second bucket needed a duplicate.
# Both are resolved by their own gate instead.
EXTERNAL_REF_KEYS = {"gate_relation_ref", "practice_profile_ref", "snapshot_ref",
                     "grade9v3:acquisition_ref", "evidence_refs"}


def references(value, path: str = "") -> list[tuple[str, str]]:
    """Every internal-looking reference in a record, as (field path, id)."""
    found: list[tuple[str, str]] = []
    if isinstance(value, dict):
        for key, item in value.items():
            if key.startswith("_"):
                continue
            here = f"{path}.{key}"
            if key in EXTERNAL_REF_KEYS:
                continue
            if key.endswith("_ref") or key == "bucket_id":
                if isinstance(item, str) and INTERNAL_ID.match(item):
                    found.append((here, item))
            elif key.endswith("_refs") and isinstance(item, list):
                found += [(here, x) for x in item if isinstance(x, str) and INTERNAL_ID.match(x)]
            found += references(item, here)
    elif isinstance(value, list):
        for position, item in enumerate(value):
            found += references(item, f"{path}[{position}]")
    return found


def nested_ids(record: dict) -> set[str]:
    """Ids declared inside a record: teaching steps, derivation steps, scene instances.

    They are addressable and are addressed -- an exit task names the step it closes, a
    reconstruct ask names the step it arrives at, a repair route names the construction
    it sends a learner back to. Indexing them as records instead would be wrong in the
    other direction: a step is not a record, has no collection and no provenance of its
    own, and would start appearing in every sweep that iterates the library.

    The rule is structural rather than a list of field names, so a nested id added to the
    schema later is addressable the day it lands.
    """
    found: set[str] = set()
    if isinstance(record, dict):
        for key, value in record.items():
            if key.startswith("_"):
                continue
            if key == "id" and isinstance(value, str):
                found.add(value)
            else:
                found |= nested_ids(value)
    elif isinstance(record, list):
        for item in record:
            found |= nested_ids(item)
    return found


def addressable(records: dict) -> set[str]:
    """Every id a reference in this library may legitimately name."""
    return set(records) | {nested for record in records.values()
                           for nested in nested_ids(record)}


def unresolved(records: dict) -> list[dict]:
    missing, known = [], addressable(records)
    for rid, record in records.items():
        for field, target in references(record):
            if target not in known:
                missing.append({"record": rid, "field": field.lstrip("."), "target": target})
    return missing


def prerequisite_edges(records: dict) -> dict[str, list[str]]:
    edges = {}
    for rid, record in records.items():
        targets = []
        for field in PREREQUISITE_FIELDS:
            targets += [x for x in record.get(field, []) or [] if isinstance(x, str)]
        edges[rid] = targets
    return edges


def prerequisite_closure(records: dict, start: list[str]) -> list[str]:
    """Everything `start` transitively depends on, deepest dependency first."""
    edges = prerequisite_edges(records)
    order, seen, active = [], set(), set()

    def visit(node: str, trail: list[str]):
        if node in seen:
            return
        require(node not in active, "LIBRARY_PREREQUISITE_CYCLE", " -> ".join(trail + [node]))
        require(node in records, "LIBRARY_PREREQUISITE_UNKNOWN", node)
        active.add(node)
        for target in edges.get(node, []):
            visit(target, trail + [node])
        active.discard(node)
        seen.add(node)
        order.append(node)

    for node in start:
        visit(node, [])
    return order


def slice_for_bucket(records: dict, bucket_id: str) -> dict:
    """The library slice an author needs to build one bucket, and nothing else."""
    require(bucket_id in records, "LIBRARY_BUCKET_UNKNOWN", bucket_id)
    microtopics = [rid for rid, r in records.items()
                   if r["_collection"] == "microtopics" and r.get("bucket_id") == bucket_id]
    require(microtopics, "LIBRARY_BUCKET_HAS_NO_MICROTOPICS", bucket_id)

    wanted: set[str] = {bucket_id, *microtopics}
    wanted.update(prerequisite_closure(records, microtopics))
    frontier = list(wanted)
    while frontier:
        rid = frontier.pop()
        for _, target in references(records[rid]):
            if target in records and target not in wanted:
                wanted.add(target)
                frontier.append(target)

    grouped: dict[str, list[dict]] = {}
    for rid in sorted(wanted):
        record = records[rid]
        grouped.setdefault(record["_collection"], []).append(record)
    return {"bucket_id": bucket_id,
            "microtopic_order": [m for m in prerequisite_closure(records, microtopics) if m in microtopics],
            "records": grouped,
            "record_count": len(wanted)}


def id_collisions(records: dict) -> list[str]:
    """Nested ids that shadow a record id, or each other.

    Making nested ids addressable makes a collision silent: a reference meaning the step
    would resolve to the record, or to another microtopic's step, and nothing would say
    so. Cheap to check, and the alternative is a repair route that quietly points
    somewhere else.
    """
    seen: dict[str, str] = {rid: rid for rid in records}
    clashes = []
    for rid, record in records.items():
        for nested in sorted(nested_ids(record)):
            if nested == rid:
                continue
            if nested in seen:
                clashes.append(f"{nested} declared in {seen[nested]} and again in {rid}")
            seen[nested] = rid
    return clashes


def validate_library(packages: list[dict]) -> dict:
    records = build_index(packages)
    missing = unresolved(records)
    require(not missing, "LIBRARY_UNRESOLVED_REFERENCE",
            "; ".join(f"{m['record']}.{m['field']} -> {m['target']}" for m in missing[:5]))

    # Application contexts describe where a capability is exercised. They are not
    # learnable graph nodes and must never satisfy a prerequisite edge. Without this
    # boundary, a story/scenario can silently become a mastery requirement simply
    # because its id is reachable.
    context_ids = {
        rid for rid, record in records.items()
        if record.get("_collection") == "application_contexts"
    }
    context_prerequisites = [
        (rid, target)
        for rid, record in records.items()
        for target in record.get("prerequisite_refs", []) or []
        if target in context_ids
    ]
    require(
        not context_prerequisites,
        "APPLICATION_CONTEXT_USED_AS_PREREQUISITE",
        "; ".join(f"{source} -> {target}" for source, target in context_prerequisites[:5]),
    )

    # A context reference must name a context, not merely any existing library id.
    # Existence-only validation would let a capability or microtopic masquerade as a
    # context and collapse the type boundary the schema is intended to create.
    wrong_context_refs = [
        (rid, target, records[target].get("_collection"))
        for rid, record in records.items()
        for target in record.get("context_refs", []) or []
        if target in records and target not in context_ids
    ]
    require(
        not wrong_context_refs,
        "APPLICATION_CONTEXT_REFERENCE_WRONG_TYPE",
        "; ".join(
            f"{source}.context_refs -> {target} ({collection})"
            for source, target, collection in wrong_context_refs[:5]
        ),
    )

    clashes = id_collisions(records)
    require(not clashes, "LIBRARY_NESTED_ID_COLLISION", "; ".join(clashes[:5]))
    nodes = [rid for rid, r in records.items()
             if r["_collection"] in {"microtopics", "capabilities", "buckets"}]
    prerequisite_closure(records, nodes)
    buckets = sorted(rid for rid, r in records.items() if r["_collection"] == "buckets")
    return {"packages": [p.get("package_id") for p in packages], "record_count": len(records),
            "buckets": buckets, "unresolved_references": 0, "prerequisite_graph": "ACYCLIC"}


def load_packages(paths: list[Path]) -> list[dict]:
    return [load(path) for path in paths]


def main() -> int:
    import argparse
    parser = argparse.ArgumentParser(description="Validate a library and optionally print a bucket slice")
    parser.add_argument("packages", nargs="+", type=Path)
    parser.add_argument("--slice", help="bucket id to retrieve")
    args = parser.parse_args()
    packages = load_packages(args.packages)
    report = validate_library(packages)
    if args.slice:
        records = build_index(packages)
        chosen = slice_for_bucket(records, args.slice)
        report["slice"] = {"bucket_id": chosen["bucket_id"], "record_count": chosen["record_count"],
                           "microtopic_order": chosen["microtopic_order"],
                           "collections": {k: len(v) for k, v in sorted(chosen["records"].items())}}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
