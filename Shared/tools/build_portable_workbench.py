"""Generate versioned portable workbench packages and host fixtures from one source."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from Shared.portable.package import (
    CANONICAL_PROVENANCE_AUTHORITY,
    COMPONENT_API_VERSION,
    PortablePackageError,
    build_package,
)
SOURCE_DIR = ROOT / "tests/fixtures/portable-workbench/sources"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _subject_roots() -> list[Path]:
    return sorted(path.parent.parent for path in ROOT.glob("*/adapter/CoreContracts.json"))


def _compile_canonical_portable(
    *,
    package: dict,
    representation: dict,
    scene_instance: dict,
) -> dict:
    portable = (scene_instance.get("scene") or {}).get("portable_workbench")
    if not isinstance(portable, dict):
        raise PortablePackageError("PORTABLE_CANONICAL_SOURCE_REQUIRED", representation.get("id", ""))
    if portable.get("schema_version") != "1.0.0":
        raise PortablePackageError(
            "PORTABLE_CANONICAL_SOURCE_VERSION_UNSUPPORTED",
            str(portable.get("schema_version")),
        )

    resource_refs = list(representation.get("interactive_resource_refs") or [])
    if len(resource_refs) != 1:
        raise PortablePackageError(
            "PORTABLE_CANONICAL_RESOURCE_AMBIGUOUS",
            representation.get("id", ""),
        )
    resource_ref = resource_refs[0]
    resources = {
        row.get("id"): row
        for row in package.get("resources", [])
        if isinstance(row, dict) and row.get("id")
    }
    resource = resources.get(resource_ref)
    if not isinstance(resource, dict):
        raise PortablePackageError("PORTABLE_CANONICAL_RESOURCE_UNKNOWN", resource_ref)

    grid = portable.get("grid")
    entities = portable.get("entities")
    target = portable.get("target")
    transactions = portable.get("transactions")
    if not isinstance(grid, dict) or not isinstance(entities, list) or not entities:
        raise PortablePackageError("PORTABLE_CANONICAL_SCENE_INVALID", representation.get("id", ""))
    if not isinstance(target, dict) or not isinstance(transactions, list) or not transactions:
        raise PortablePackageError("PORTABLE_CANONICAL_ACTION_INVALID", representation.get("id", ""))

    rows = list(grid.get("rows") or [])
    columns = list(grid.get("columns") or [])
    cells = [(row, column) for row in rows for column in columns]
    if len(cells) < len(entities) + 2:
        raise PortablePackageError("PORTABLE_CANONICAL_GRID_CAPACITY_INVALID", str(portable.get("scene_ref")))

    entity_ids = {row.get("id") for row in entities}
    target_id = target.get("id")
    target_cell = cells[-1]
    result_cell = cells[-2]

    compiled_entities = []
    compiled_projections = []
    for index, entity in enumerate(entities):
        entity_id = entity.get("id")
        if not isinstance(entity_id, str) or not entity_id:
            raise PortablePackageError("PORTABLE_CANONICAL_ENTITY_ID_REQUIRED")
        row_name, column_name = cells[index]
        compiled_entities.append({
            "id": entity_id,
            "label": entity.get("label") or entity_id,
            "semanticState": entity.get("semantic_state"),
            "xTimeRef": entity.get("x_time_ref"),
            "yTimeRef": entity.get("y_time_ref"),
            "provenance": {"kind": "SOURCE", "sourceEntityRefs": []},
        })
        compiled_projections.append({
            "id": f"{entity_id}-projection",
            "entityRef": entity_id,
            "label": entity.get("label") or entity_id,
            "representation": entity.get("semantic_state") or "canonical candidate",
            "placement": {
                "grid": grid.get("id"),
                "row": row_name,
                "column": column_name,
            },
        })

    compiled_target = {
        "id": target_id,
        "label": target.get("label") or target_id,
        "operation": target.get("operation"),
        "placement": {
            "grid": grid.get("id"),
            "row": target_cell[0],
            "column": target_cell[1],
        },
    }
    transformations = []
    adapter_rules = []
    for transaction in transactions:
        tx_id = transaction.get("id")
        source_id = transaction.get("source_entity_ref")
        if source_id not in entity_ids:
            raise PortablePackageError("PORTABLE_CANONICAL_TRANSACTION_SOURCE_UNKNOWN", str(source_id))
        if transaction.get("target_ref") != target_id:
            raise PortablePackageError("PORTABLE_CANONICAL_TRANSACTION_TARGET_MISMATCH", str(tx_id))
        if transaction.get("operation") != target.get("operation"):
            raise PortablePackageError("PORTABLE_CANONICAL_TRANSACTION_OPERATION_MISMATCH", str(tx_id))
        outcome = transaction.get("outcome")
        if outcome not in {"ACCEPT", "REJECT"}:
            raise PortablePackageError("PORTABLE_CANONICAL_TRANSACTION_OUTCOME_INVALID", str(tx_id))

        transformation_ref = f"{tx_id}-transformation"
        transformations.append({
            "id": transformation_ref,
            "sourceEntityRefs": [source_id],
            "targetRef": target_id,
        })
        rule = {
            "id": tx_id,
            "transformationRef": transformation_ref,
            "sourceEntityRef": source_id,
            "targetRef": target_id,
            "operation": transaction.get("operation"),
            "outcome": outcome,
        }
        if outcome == "REJECT":
            reason = transaction.get("reason")
            if not isinstance(reason, str) or not reason.strip():
                raise PortablePackageError("PORTABLE_CANONICAL_REJECTION_REASON_REQUIRED", str(tx_id))
            rule["reason"] = reason
        else:
            summary = transaction.get("summary")
            if not isinstance(summary, str) or not summary.strip():
                raise PortablePackageError("PORTABLE_CANONICAL_ACCEPT_SUMMARY_REQUIRED", str(tx_id))
            result_id = f"{tx_id}-result"
            rule["summary"] = summary
            rule["patch"] = {
                "addEntities": [{
                    "id": result_id,
                    "label": summary,
                    "provenance": {"kind": "DERIVED", "sourceEntityRefs": [source_id]},
                }],
                "addProjections": [{
                    "id": f"{result_id}-projection",
                    "entityRef": result_id,
                    "label": target.get("label") or target_id,
                    "representation": "accepted canonical reconstruction",
                    "placement": {
                        "grid": grid.get("id"),
                        "row": result_cell[0],
                        "column": result_cell[1],
                    },
                }],
            }
        adapter_rules.append(rule)

    scene = {
        "apiVersion": COMPONENT_API_VERSION,
        "sceneVersion": portable.get("schema_version"),
        "id": portable.get("scene_ref"),
        "grids": [{
            "id": grid.get("id"),
            "label": scene_instance.get("scene", {}).get("caption") or representation.get("title"),
            "rows": rows,
            "columns": columns,
        }],
        "entities": compiled_entities,
        "projections": compiled_projections,
        "targets": [compiled_target],
        "canonicalTransformations": transformations,
    }

    source = {
        "id": portable.get("package_ref"),
        "title": resource.get("title") or representation.get("title") or portable.get("package_ref"),
        "sourceKind": "CANONICAL_RESOURCE",
        "provenanceAuthority": CANONICAL_PROVENANCE_AUTHORITY,
        "sourceRefs": list(representation.get("source_refs") or []),
        "representationRefs": [representation.get("id")],
        "representationRef": representation.get("id"),
        "resourceRef": resource_ref,
        "assetRefs": list(representation.get("rendered_asset_refs") or []),
        "accessibilityRefs": list(representation.get("accessibility") or []),
        "questionBindings": [],
        "injections": [],
        "adapterRules": adapter_rules,
    }
    return build_package(source, scene)


def _canonical_packages() -> list[dict]:
    rows = []
    seen: set[str] = set()
    for subject_root in _subject_roots():
        for path in sorted((subject_root / "library").glob("*.json")):
            package = _json(path)
            for representation in package.get("representations", []):
                for scene_instance in representation.get("scene_instances", []):
                    if not isinstance((scene_instance.get("scene") or {}).get("portable_workbench"), dict):
                        continue
                    compiled = _compile_canonical_portable(
                        package=package,
                        representation=representation,
                        scene_instance=scene_instance,
                    )
                    if compiled["id"] in seen:
                        raise PortablePackageError("PORTABLE_CANONICAL_PACKAGE_ID_DUPLICATE", compiled["id"])
                    seen.add(compiled["id"])
                    rows.append(compiled)
    return rows


def packages() -> list[dict]:
    rows = []
    for path in sorted(SOURCE_DIR.glob("*.json")):
        source = _json(path)
        scene = _json(ROOT / source["sceneRef"]) if source.get("sceneRef") else source["scene"]
        rows.append(build_package(source, scene))
    rows.extend(_canonical_packages())
    return rows


def _host_html(*, title: str, asset_base: str, package_base: str) -> str:
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>:root{{--workbench-border:#64748b;--workbench-focus:#1d4ed8;--workbench-surface:#f8fafc}}body{{font:16px/1.45 system-ui,sans-serif;margin:0;padding:1rem}}main{{max-width:70rem;margin:auto}}.diagnostic{{white-space:pre-wrap;border:1px solid #b91c1c;padding:.75rem}}</style></head>
<body><main><h1>{title}</h1><p id="package-label">Loading portable package...</p><semantic-workbench id="portable-workbench"></semantic-workbench><pre id="diagnostic" class="diagnostic" hidden></pre></main>
<script type="module">
import "{asset_base}semantic-workbench.mjs";
import {{ mountPortableWorkbench }} from "{asset_base}portable-host.mjs";
const events=[];window.__portableEvents=events;const params=new URLSearchParams(location.search);
try{{const catalog=await fetch("{package_base}catalog.json").then(r=>r.json());const requested=params.get("package");if(requested&&!catalog.packageIds.includes(requested))throw new Error("PORTABLE_PACKAGE_NOT_FOUND: "+requested);const id=requested||catalog.packageIds[0];const response=await fetch("{package_base}packages/"+id+".json");if(!response.ok)throw new Error("PORTABLE_PACKAGE_LOAD_FAILED: "+id);const pkg=await response.json();const element=document.querySelector("#portable-workbench");element.addEventListener("semantic-workbench-event",e=>events.push(e.detail));mountPortableWorkbench(element,pkg);document.querySelector("#package-label").textContent=pkg.title;window.__portablePackageId=pkg.id;window.__portableWorkbenchReady=true}}catch(error){{const d=document.querySelector("#diagnostic");d.hidden=false;d.textContent=error instanceof Error?error.message:String(error);window.__portableWorkbenchError=d.textContent}}
</script></body></html>'''


def _strip_import(source: str, module_name: str) -> str:
    pattern = rf'^import\s*\{{.*?\}}\s*from\s*"{re.escape(module_name)}";\s*'
    return re.sub(pattern, "", source, count=1, flags=re.S)


def _offline_html(package_rows: list[dict]) -> str:
    runtime = (ROOT / "Shared/workbench/runtime.mjs").read_text(encoding="utf-8")
    component = _strip_import((ROOT / "Shared/workbench/semantic-workbench.mjs").read_text(encoding="utf-8"), "./runtime.mjs")
    portable = _strip_import((ROOT / "Shared/portable/portable-host.mjs").read_text(encoding="utf-8"), "../workbench/runtime.mjs")
    payload = json.dumps(package_rows, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portable Workbench Offline Host</title><style>:root{{--workbench-border:#64748b;--workbench-focus:#1d4ed8;--workbench-surface:#f8fafc}}body{{font:16px/1.45 system-ui,sans-serif;margin:0;padding:1rem}}main{{max-width:70rem;margin:auto}}</style></head><body><main><h1>Portable Workbench Offline Host</h1><p id="package-label"></p><semantic-workbench id="portable-workbench"></semantic-workbench><pre id="diagnostic" hidden></pre></main><script type="module">
{runtime}
{component}
{portable}
const PORTABLE_PACKAGES={payload};const events=[];window.__portableEvents=events;const params=new URLSearchParams(location.search);try{{const requested=params.get("package");const pkg=requested?PORTABLE_PACKAGES.find(row=>row.id===requested):PORTABLE_PACKAGES[0];if(!pkg)throw new Error("PORTABLE_PACKAGE_NOT_FOUND: "+requested);const element=document.querySelector("#portable-workbench");element.addEventListener("semantic-workbench-event",e=>events.push(e.detail));mountPortableWorkbench(element,pkg);document.querySelector("#package-label").textContent=pkg.title;window.__portablePackageId=pkg.id;window.__portableWorkbenchReady=true}}catch(error){{const d=document.querySelector("#diagnostic");d.hidden=false;d.textContent=error instanceof Error?error.message:String(error);window.__portableWorkbenchError=d.textContent}}
</script></body></html>'''


def render() -> dict[str, bytes]:
    package_rows = packages()
    outputs: dict[str, bytes] = {}
    for package in package_rows:
        outputs[f"public/portable-workbench/packages/{package['id']}.json"] = (json.dumps(package, ensure_ascii=True, indent=2) + "\n").encode("utf-8")
    catalog = {"schemaVersion": "portable-workbench-catalog", "packageIds": [row["id"] for row in package_rows]}
    outputs["public/portable-workbench/catalog.json"] = (json.dumps(catalog, indent=2) + "\n").encode("utf-8")
    outputs["public/portable-workbench/runtime.mjs"] = (ROOT / "Shared/workbench/runtime.mjs").read_bytes()
    outputs["public/portable-workbench/semantic-workbench.mjs"] = (ROOT / "Shared/workbench/semantic-workbench.mjs").read_bytes()
    portable_host = (ROOT / "Shared/portable/portable-host.mjs").read_text(encoding="utf-8").replace('from "../workbench/runtime.mjs"', 'from "./runtime.mjs"')
    outputs["public/portable-workbench/portable-host.mjs"] = portable_host.encode("utf-8")
    outputs["public/portable-workbench/index.html"] = _host_html(title="Grade9V3 Portable Workbench Host", asset_base="./", package_base="./").encode("utf-8")
    outputs["tests/fixtures/portable-workbench/external-host.html"] = _host_html(title="External Plain HTML Portable Workbench Host", asset_base="/public/portable-workbench/", package_base="/public/portable-workbench/").encode("utf-8")
    outputs["standalone/portable-workbench/index.html"] = _offline_html(package_rows).encode("utf-8")
    return outputs


def write() -> None:
    for relative, content in render().items():
        path = ROOT / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
        print(f"wrote {relative}")


def check() -> int:
    drift = []
    for relative, expected in render().items():
        path = ROOT / relative
        if not path.exists() or path.read_bytes() != expected:
            drift.append(relative)
    if drift:
        print("portable workbench generated artifacts have drifted:")
        for relative in drift:
            print(f"  {relative}")
        return 1
    print("portable workbench generated artifacts are current")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    if args.check:
        return check()
    write()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
