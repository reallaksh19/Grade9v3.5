#!/usr/bin/env python3
"""Compile one Core projection into a schema-linked interactive-page package."""
from __future__ import annotations

import argparse
import copy
import html
import json
import re
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
CORE_DATA = REPO / "public" / "core-learning" / "data.js"
RUNTIME_DIR = REPO / "Shared" / "workbench"
PACKAGING_MODES = {"PUBLIC", "PAGES", "OFFLINE_DIRECTORY", "SINGLE_FILE", "EMBED"}


class InteractivePageBuildError(ValueError):
    """Raised when a projection cannot be rendered without inventing page architecture."""


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise InteractivePageBuildError(f"{code}: {detail}" if detail else code)


def _load_core_data(path: Path = CORE_DATA) -> dict[str, Any]:
    text = path.read_text(encoding="utf-8")
    marker = "window.GRADE9V3_CORE = "
    start = text.find(marker)
    _require(start >= 0, "INTERACTIVE_PAGE_CORE_DATA_INVALID", str(path))
    body = text[start + len(marker):].strip()
    if body.endswith(";"):
        body = body[:-1]
    try:
        payload = json.loads(body)
    except json.JSONDecodeError as exc:
        raise InteractivePageBuildError(f"INTERACTIVE_PAGE_CORE_DATA_INVALID: {exc}") from exc
    _require(isinstance(payload, dict), "INTERACTIVE_PAGE_CORE_DATA_INVALID")
    return payload


def _expected_blueprint(core: str) -> dict[str, Any]:
    try:
        from Shared.tools import core_template_contract
    except ModuleNotFoundError:  # direct script execution
        import sys
        if str(REPO) not in sys.path:
            sys.path.insert(0, str(REPO))
        from Shared.tools import core_template_contract
    return core_template_contract.resolve_web_blueprint_for_core(core)


def _mount_mode(row: dict[str, Any], projection: dict[str, Any]) -> str:
    scene_ref = row.get("scene_ref")
    adapter_ref = row.get("adapter_ref")
    _require(
        (scene_ref is None) == (adapter_ref is None),
        "INTERACTIVE_PAGE_WORKBENCH_BINDING_INCOMPLETE",
        str(row.get("id") or ""),
    )
    if scene_ref is not None:
        return "PORTABLE_SCENE"
    locator = row.get("explorer_locator")
    if isinstance(locator, str) and locator:
        return "LEGACY_IFRAME"
    initial = (projection.get("presentation") or {}).get("initial_visual_ref")
    if isinstance(initial, str) and initial:
        return "STATIC_FIGURE"
    return "NONE"


def compile_page_package(row: dict[str, Any]) -> dict[str, Any]:
    _require(isinstance(row, dict), "INTERACTIVE_PAGE_ROW_REQUIRED")
    projection = row.get("projection")
    _require(isinstance(projection, dict), "INTERACTIVE_PAGE_PROJECTION_REQUIRED")
    core = projection.get("core")
    _require(isinstance(core, str) and core, "INTERACTIVE_PAGE_CORE_REQUIRED")

    expected = _expected_blueprint(core)
    delivery = ((projection.get("delivery") or {}).get("web"))
    _require(isinstance(delivery, dict), "WEB_BLUEPRINT_REF_MISSING", core)
    _require(
        delivery.get("blueprint_ref") == expected["ref"],
        "WEB_BLUEPRINT_CORE_INCOMPATIBLE",
        f"{core}: {delivery.get('blueprint_ref')} != {expected['ref']}",
    )
    for field in ("shell_ref", "layout_family"):
        _require(
            delivery.get(field) == expected[field],
            "WEB_BLUEPRINT_DELIVERY_MISMATCH",
            f"{core}:{field}",
        )

    mount_mode = _mount_mode(row, projection)
    representation_policy = delivery.get("representation_policy") or {}
    if mount_mode == "LEGACY_IFRAME":
        _require(
            representation_policy.get("legacy_iframe") == "MIGRATION_ONLY",
            "WEB_BLUEPRINT_LEGACY_IFRAME_NOT_ALLOWED",
            str(row.get("id") or ""),
        )
    elif mount_mode not in {"NONE"}:
        _require(
            mount_mode in (representation_policy.get("preferred_mount_modes") or []),
            "WEB_BLUEPRINT_REPRESENTATION_MODE_UNSUPPORTED",
            mount_mode,
        )

    package = {
        "schema_version": "grade9v3-interactive-page-package-v1",
        "projection_id": row.get("id"),
        "subject": row.get("subject"),
        "source_ref": row.get("source_ref"),
        "core": core,
        "blueprint": {
            "ref": delivery["blueprint_ref"],
            "id": delivery["blueprint_id"],
            "version": delivery["blueprint_version"],
            "shell_ref": delivery["shell_ref"],
            "layout_family": delivery["layout_family"],
            "required_slots": list(delivery.get("required_slots") or []),
            "slot_order": list(delivery.get("slot_order") or []),
            "interaction_policy": copy.deepcopy(delivery.get("interaction_policy") or {}),
            "representation_policy": copy.deepcopy(representation_policy),
            "responsive_policy": copy.deepcopy(delivery.get("responsive_policy") or {}),
            "touch_policy": copy.deepcopy(delivery.get("touch_policy") or {}),
            "packaging_modes": list(delivery.get("packaging_modes") or []),
            "forbidden": list(delivery.get("forbidden") or []),
        },
        "representation": {
            "mount_mode": mount_mode,
            "scene_ref": row.get("scene_ref"),
            "adapter_ref": row.get("adapter_ref"),
            "injection_refs": list(row.get("injection_refs") or []),
            "explorer_locator": row.get("explorer_locator"),
            "initial_visual_ref": (projection.get("presentation") or {}).get("initial_visual_ref"),
            "initial_visual_stage_ref": (projection.get("presentation") or {}).get("initial_visual_stage_ref"),
        },
        "projection": copy.deepcopy(projection),
    }
    _require(
        set(package["blueprint"]["packaging_modes"]) == PACKAGING_MODES,
        "WEB_BLUEPRINT_PACKAGING_MODES_INVALID",
        str(delivery.get("blueprint_ref") or ""),
    )
    return package


def resolve_projection(payload: dict[str, Any], projection_id: str) -> dict[str, Any]:
    rows = payload.get("core_projections")
    _require(isinstance(rows, list), "INTERACTIVE_PAGE_PROJECTIONS_REQUIRED")
    matches = [row for row in rows if isinstance(row, dict) and row.get("id") == projection_id]
    _require(len(matches) == 1, "INTERACTIVE_PAGE_PROJECTION_NOT_FOUND", projection_id)
    return matches[0]


def agent_contract(package: dict[str, Any]) -> dict[str, Any]:
    blueprint = package["blueprint"]
    return {
        "core": package["core"],
        "web_blueprint_ref": blueprint["ref"],
        "shell_ref": blueprint["shell_ref"],
        "layout_family": blueprint["layout_family"],
        "required_slots": blueprint["required_slots"],
        "slot_order": blueprint["slot_order"],
        "interaction_policy": copy.deepcopy(blueprint["interaction_policy"]),
        "representation_policy": copy.deepcopy(blueprint["representation_policy"]),
        "responsive_policy": copy.deepcopy(blueprint["responsive_policy"]),
        "touch_policy": copy.deepcopy(blueprint["touch_policy"]),
        "packaging_modes": list(blueprint["packaging_modes"]),
        "forbidden": list(blueprint["forbidden"]),
        "authority_note": (
            "Blueprint controls presentation/delivery only. Academic truth remains in the "
            "compiled canonical projection and its source records."
        ),
    }


def _module(name: str) -> str:
    return (RUNTIME_DIR / name).read_text(encoding="utf-8")


def html_escape(value: str) -> str:
    return html.escape(str(value), quote=True)


def _offline_index(packaging_mode: str = "OFFLINE_DIRECTORY", shell_ref: str = "") -> str:
    html = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="grade9v3-packaging-mode" content="__PACKAGING_MODE__">
<title>Grade9V3 Interactive Page</title>
<style>
body{font:16px/1.45 system-ui,sans-serif;margin:0;background:#fff;color:#111}
.site-nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:.5rem;min-height:3.5rem;padding:.4rem .75rem;border-bottom:1px solid #bbb;background:#fff;flex-wrap:wrap}
.site-nav a,.site-nav button,.site-nav input,.site-nav summary{font:inherit;min-height:3rem;box-sizing:border-box}
.site-nav a,.site-nav button,.site-nav summary{display:inline-flex;align-items:center;padding:.4rem .7rem;border:1px solid #999;border-radius:.5rem;text-decoration:none;color:inherit;background:#fff}
.site-nav input{min-width:10rem;padding:.4rem .6rem}
.site-nav form{display:flex;gap:.5rem}
.site-nav .context{font-weight:700;margin-inline:auto}
.site-nav details{position:relative}
.site-nav details div{position:absolute;right:0;top:100%;background:#fff;border:1px solid #bbb;border-radius:.5rem;padding:.5rem;min-width:12rem;z-index:30}
main{max-width:80rem;margin:auto;padding:1rem}
.meta{font-size:.85rem;opacity:.75}
</style></head><body>
<header class="site-nav" data-shell-ref="__SHELL_REF__">
<button id="back" type="button" aria-label="Back">← Back</button>
<a id="home" href="./index.html">Home</a>
<span id="subject-context" class="context">Grade9V3</span>
<a id="question-bank" href="./question-bank/index.html">Question Bank</a>
<form id="site-search" role="search"><input id="site-search-input" type="search" aria-label="Search this page"><button type="submit">Search</button></form>
<button id="refresh" type="button" aria-label="Refresh">↻ Refresh</button>
<button id="display-down" type="button" aria-label="Decrease text size">A−</button>
<button id="display-up" type="button" aria-label="Increase text size">A+</button>
<details><summary>More</summary><div><p>Packaging: __PACKAGING_MODE__</p><p>Offline-safe learner page.</p></div></details>
</header>
<main><p class="meta" id="delivery"></p><core-learning-page id="learner"></core-learning-page></main>
<script src="./data.js"></script>
<script type="module">
import "./semantic-workbench.mjs";
import "./core-learning-page.mjs";
import {mountCoreLearningPage} from "./core-learning-host.mjs";
const data=window.GRADE9V3_CORE,row=data.core_projections[0],learner=document.querySelector("#learner");
mountCoreLearningPage(learner,data,row.id,window.CORE_LEARNING_REGISTRIES||{});
document.querySelector("#subject-context").textContent=[row.subject,row.projection.core].filter(Boolean).join(" · ");
document.querySelector("#delivery").textContent=row.projection.delivery.web.blueprint_ref+" · "+row.projection.delivery.web.layout_family;
document.querySelector("#back").addEventListener("click",()=>history.length>1?history.back():null);
document.querySelector("#refresh").addEventListener("click",()=>location.reload());
document.querySelector("#site-search").addEventListener("submit",(event)=>{{event.preventDefault();const q=document.querySelector("#site-search-input").value.trim();if(q&&typeof window.find==="function")window.find(q);}});
let scale=1;
const applyScale=()=>document.documentElement.style.fontSize=(16*scale)+"px";
document.querySelector("#display-down").addEventListener("click",()=>{{scale=Math.max(.8,scale-.1);applyScale();}});
document.querySelector("#display-up").addEventListener("click",()=>{{scale=Math.min(1.5,scale+.1);applyScale();}});
window.__interactivePageReady=true;
</script></body></html>
"""
    return html.replace("__PACKAGING_MODE__", packaging_mode).replace("__SHELL_REF__", html_escape(shell_ref))


def render_offline_directory(package: dict[str, Any], packaging_mode: str = "OFFLINE_DIRECTORY") -> dict[str, bytes]:
    row = {
        "id": package["projection_id"],
        "subject": package["subject"],
        "source_ref": package["source_ref"],
        "projection": package["projection"],
        "scene_ref": package["representation"]["scene_ref"],
        "adapter_ref": package["representation"]["adapter_ref"],
        "injection_refs": package["representation"]["injection_refs"],
        "explorer_locator": package["representation"]["explorer_locator"],
    }
    payload = {
        "provider_status": "INTERACTIVE_PAGE_PACKAGE",
        "core_projections": [row],
        "bucket_availability": [],
    }
    return {
        "index.html": _offline_index(packaging_mode, package["blueprint"]["shell_ref"]).encode("utf-8"),
        "data.js": (
            "window.GRADE9V3_CORE = "
            + json.dumps(payload, ensure_ascii=False, indent=2)
            + ";\n"
        ).encode("utf-8"),
        "runtime.mjs": _module("runtime.mjs").encode("utf-8"),
        "semantic-workbench.mjs": _module("semantic-workbench.mjs").encode("utf-8"),
        "core-learning-page.mjs": _module("core-learning-page.mjs").encode("utf-8"),
        "core-learning-host.mjs": _module("core-learning-host.mjs").encode("utf-8"),
        "interactive-page-package.json": (
            json.dumps(package, ensure_ascii=False, indent=2) + "\n"
        ).encode("utf-8"),
    }


def _js_string(value: str) -> str:
    return json.dumps(value, ensure_ascii=False).replace("</", "<\\/")


def render_single_file(package: dict[str, Any]) -> bytes:
    row = {
        "id": package["projection_id"],
        "subject": package["subject"],
        "source_ref": package["source_ref"],
        "projection": package["projection"],
        "scene_ref": package["representation"]["scene_ref"],
        "adapter_ref": package["representation"]["adapter_ref"],
        "injection_refs": package["representation"]["injection_refs"],
        "explorer_locator": package["representation"]["explorer_locator"],
    }
    data = {
        "provider_status": "INTERACTIVE_PAGE_PACKAGE",
        "core_projections": [row],
        "bucket_availability": [],
    }
    runtime = _module("runtime.mjs")
    semantic = _module("semantic-workbench.mjs")
    page = _module("core-learning-page.mjs")
    host = _module("core-learning-host.mjs")
    data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="grade9v3-packaging-mode" content="SINGLE_FILE">
<title>Grade9V3 Interactive Page</title>
<style>
body{{font:16px/1.45 system-ui,sans-serif;margin:0;background:#fff;color:#111}}
.site-nav{{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:.5rem;min-height:3.5rem;padding:.4rem .75rem;border-bottom:1px solid #bbb;background:#fff;flex-wrap:wrap}}
.site-nav a,.site-nav button,.site-nav input,.site-nav summary{{font:inherit;min-height:3rem;box-sizing:border-box}}
.site-nav a,.site-nav button,.site-nav summary{{display:inline-flex;align-items:center;padding:.4rem .7rem;border:1px solid #999;border-radius:.5rem;text-decoration:none;color:inherit;background:#fff}}
.site-nav input{{min-width:10rem;padding:.4rem .6rem}}.site-nav form{{display:flex;gap:.5rem}}.site-nav .context{{font-weight:700;margin-inline:auto}}
.site-nav details{{position:relative}}.site-nav details div{{position:absolute;right:0;top:100%;background:#fff;border:1px solid #bbb;border-radius:.5rem;padding:.5rem;min-width:12rem;z-index:30}}
main{{max-width:80rem;margin:auto;padding:1rem}}.meta{{font-size:.85rem;opacity:.75}}
</style></head><body>
<header class="site-nav" data-shell-ref="{html_escape(package['blueprint']['shell_ref'])}">
<button id="back" type="button" aria-label="Back">← Back</button><a href="./index.html">Home</a><span id="page-title" class="context">Grade9V3</span>
<a href="./question-bank/index.html">Question Bank</a>
<form id="site-search" role="search"><input id="site-search-input" type="search" aria-label="Search this page"><button type="submit">Search</button></form>
<button id="refresh" type="button" aria-label="Refresh">↻ Refresh</button>
<button id="display-down" type="button" aria-label="Decrease text size">A−</button><button id="display-up" type="button" aria-label="Increase text size">A+</button>
<details><summary>More</summary><div><p>Packaging: SINGLE_FILE</p><p>Offline-safe learner page.</p></div></details>
</header>
<main><p class="meta" id="delivery"></p><core-learning-page id="learner"></core-learning-page></main>
<script type="module">
const SOURCES={{
  runtime:{_js_string(runtime)},
  semantic:{_js_string(semantic)},
  page:{_js_string(page)},
  host:{_js_string(host)}
}};
const urls={{}};
urls.runtime=URL.createObjectURL(new Blob([SOURCES.runtime],{{type:"text/javascript"}}));
urls.semantic=URL.createObjectURL(new Blob([SOURCES.semantic.replace('"./runtime.mjs"',JSON.stringify(urls.runtime))],{{type:"text/javascript"}}));
urls.page=URL.createObjectURL(new Blob([SOURCES.page],{{type:"text/javascript"}}));
urls.host=URL.createObjectURL(new Blob([SOURCES.host.replace('"./core-learning-page.mjs"',JSON.stringify(urls.page))],{{type:"text/javascript"}}));
await import(urls.semantic);
await import(urls.page);
const hostModule=await import(urls.host);
const data={data_json};
const row=data.core_projections[0],learner=document.querySelector("#learner");
hostModule.mountCoreLearningPage(learner,data,row.id,window.CORE_LEARNING_REGISTRIES||{{}});
document.querySelector("#page-title").textContent=[row.subject,row.projection.core].filter(Boolean).join(" · ");
document.querySelector("#delivery").textContent=row.projection.delivery.web.blueprint_ref+" · "+row.projection.delivery.web.layout_family;
document.querySelector("#back").addEventListener("click",()=>history.length>1?history.back():null);
document.querySelector("#refresh").addEventListener("click",()=>location.reload());
document.querySelector("#site-search").addEventListener("submit",(event)=>{{event.preventDefault();const q=document.querySelector("#site-search-input").value.trim();if(q&&typeof window.find==="function")window.find(q);}});
let scale=1;const applyScale=()=>document.documentElement.style.fontSize=(16*scale)+"px";
document.querySelector("#display-down").addEventListener("click",()=>{{scale=Math.max(.8,scale-.1);applyScale();}});
document.querySelector("#display-up").addEventListener("click",()=>{{scale=Math.min(1.5,scale+.1);applyScale();}});
window.__interactivePageReady=true;
</script></body></html>"""
    return html.encode("utf-8")


def write_mode(package: dict[str, Any], mode: str, out: Path) -> None:
    _require(mode in PACKAGING_MODES, "INTERACTIVE_PAGE_PACKAGING_MODE_UNSUPPORTED", mode)
    _require(mode in package["blueprint"]["packaging_modes"], "WEB_BLUEPRINT_PACKAGING_MODE_NOT_ALLOWED", mode)
    if mode == "SINGLE_FILE":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(render_single_file(package))
        return
    out.mkdir(parents=True, exist_ok=True)
    for name, content in render_offline_directory(package, mode).items():
        (out / name).write_bytes(content)
    (out / "agent-contract.json").write_text(
        json.dumps(agent_contract(package), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--projection-id", required=True)
    parser.add_argument("--mode", choices=sorted(PACKAGING_MODES), default="EMBED")
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--core-data", type=Path, default=CORE_DATA)
    args = parser.parse_args()
    payload = _load_core_data(args.core_data)
    package = compile_page_package(resolve_projection(payload, args.projection_id))
    write_mode(package, args.mode, args.out)
    print(json.dumps({
        "projection_id": package["projection_id"],
        "core": package["core"],
        "blueprint_ref": package["blueprint"]["ref"],
        "mode": args.mode,
        "out": str(args.out),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
