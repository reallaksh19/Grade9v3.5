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

from Shared.portable.package import build_package
SOURCE_DIR = ROOT / "tests/fixtures/portable-workbench/sources"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def packages() -> list[dict]:
    rows = []
    for path in sorted(SOURCE_DIR.glob("*.json")):
        source = _json(path)
        scene = _json(ROOT / source["sceneRef"]) if source.get("sceneRef") else source["scene"]
        rows.append(build_package(source, scene))
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
try{{const catalog=await fetch("{package_base}catalog.json").then(r=>r.json());const requested=params.get("package");const id=requested&&catalog.packageIds.includes(requested)?requested:catalog.packageIds[0];const pkg=await fetch("{package_base}packages/"+id+".json").then(r=>r.json());const element=document.querySelector("#portable-workbench");element.addEventListener("semantic-workbench-event",e=>events.push(e.detail));mountPortableWorkbench(element,pkg);document.querySelector("#package-label").textContent=pkg.title;window.__portablePackageId=pkg.id;window.__portableWorkbenchReady=true}}catch(error){{const d=document.querySelector("#diagnostic");d.hidden=false;d.textContent=error instanceof Error?error.message:String(error);window.__portableWorkbenchError=d.textContent}}
</script></body></html>'''


def _strip_import(source: str, module_name: str) -> str:
    pattern = rf'^import\s*\{{.*?\}}\s*from\s*"{re.escape(module_name)}";\s*'
    return re.sub(pattern, "", source, count=1, flags=re.S)


def _offline_html(package_rows: list[dict]) -> str:
    runtime = (ROOT / "Shared/workbench/runtime.mjs").read_text(encoding="utf-8")
    component = _strip_import((ROOT / "Shared/workbench/semantic-workbench.mjs").read_text(encoding="utf-8"), "./runtime.mjs")
    portable = _strip_import((ROOT / "Shared/portable/portable-host.mjs").read_text(encoding="utf-8"), "../workbench/runtime.mjs")
    payload = json.dumps(package_rows, ensure_ascii=True, separators=(",", ":")).replace("</", "<\\/")
    return f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Portable Workbench Offline Host</title><style>:root{{--workbench-border:#64748b;--workbench-focus:#1d4ed8;--workbench-surface:#f8fafc}}body{{font:16px/1.45 system-ui,sans-serif;margin:0;padding:1rem}}main{{max-width:70rem;margin:auto}}</style></head><body><main><h1>Portable Workbench Offline Host</h1><p id="package-label"></p><semantic-workbench id="portable-workbench"></semantic-workbench></main><script type="module">
{runtime}
{component}
{portable}
const PORTABLE_PACKAGES={payload};const events=[];window.__portableEvents=events;const pkg=PORTABLE_PACKAGES[0];const element=document.querySelector("#portable-workbench");element.addEventListener("semantic-workbench-event",e=>events.push(e.detail));mountPortableWorkbench(element,pkg);document.querySelector("#package-label").textContent=pkg.title;window.__portablePackageId=pkg.id;window.__portableWorkbenchReady=true;
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
