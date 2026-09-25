#!/usr/bin/env python3
"""Build non-Core EXPLORE pages from a resolved representation/activity plan."""
from __future__ import annotations

import argparse
import html
import json
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
PROFILE_REGISTRY = REPO / "Shared/web/explorer-profiles.v1.json"

if __package__ in (None, ""):
    import sys
    sys.path.insert(0, str(REPO))

from Shared.contracts import load
from Shared.library.resolve import build_index, load_packages
from Shared.tools import build_portable_workbench, build_web_data

PACKAGING_MODES = {"PUBLIC","PAGES","OFFLINE_DIRECTORY","SINGLE_FILE","EMBED"}


class ExplorePageBuildError(ValueError):
    pass


def _require(condition: bool, code: str, detail: str = "") -> None:
    if not condition:
        raise ExplorePageBuildError(f"{code}: {detail}" if detail else code)


def _records(subject: str, repo: Path) -> dict[str, dict]:
    paths = sorted((repo / subject / "library").glob("*.json"))
    return build_index(load_packages(paths)) if paths else {}


def _profile(repo: Path) -> dict:
    registry = load(repo / PROFILE_REGISTRY.relative_to(REPO))
    matches = [
        row for row in registry.get("profiles", [])
        if row.get("ref") == "XP-CANONICAL-EXPLORER@1.0.0"
    ]
    _require(len(matches) == 1, "EXPLORE_PROFILE_UNAVAILABLE")
    return matches[0]


def compile_page_package(plan: dict, repo: Path = REPO) -> dict:
    _require(plan.get("build_action") == "EXPLORE_PAGE_ADAPTER", "EXPLORE_PLAN_ACTION_INVALID")
    _require(plan.get("request_satisfaction") != "HOLD", "EXPLORE_PLAN_HELD")
    segments = plan.get("experience_segments") or []
    _require(len(segments) == 1 and segments[0].get("mode") == "EXPLORE", "EXPLORE_SEGMENT_REQUIRED")

    subject = plan["subject"]
    records = _records(subject, repo)
    refs = (plan.get("target") or {}).get("resolved_refs") or {}
    representation_refs = list(refs.get("representation_refs") or [])
    activity_refs = list(refs.get("activity_refs") or [])
    web = build_web_data.build()
    entry = (web.get("subjects") or {}).get(subject) or {}
    visual_targets = entry.get("visual_targets") or {}

    portable_packages = {row["id"]: row for row in build_portable_workbench.packages()}
    selected_activity = None
    mount_mode = None
    portable_package = None

    for ref in activity_refs:
        target = visual_targets.get(ref) or {}
        package_ref = target.get("portable_package_ref")
        if (
            target.get("availability", {}).get("portable_package") == "READY"
            and package_ref in portable_packages
        ):
            selected_activity = target
            mount_mode = "PORTABLE_SCENE"
            portable_package = portable_packages[package_ref]
            break

    if selected_activity is None:
        for ref in activity_refs:
            target = visual_targets.get(ref) or {}
            if target.get("availability", {}).get("locator") == "READY" and target.get("locator"):
                selected_activity = target
                mount_mode = "LEGACY_IFRAME"
                break

    representation = None
    if representation_refs:
        candidates = [
            records.get(ref) for ref in representation_refs
            if isinstance(records.get(ref), dict)
            and records.get(ref, {}).get("_collection") == "representations"
        ]
        if candidates:
            representation = candidates[0]

    if mount_mode is None and representation is not None:
        mount_mode = "STATIC_FIGURE"

    _require(mount_mode is not None, "EXPLORE_DELIVERY_UNAVAILABLE")
    profile = _profile(repo)
    if mount_mode == "LEGACY_IFRAME":
        _require(
            profile["representation_policy"]["legacy_iframe"] == "MIGRATION_ONLY",
            "EXPLORE_LEGACY_IFRAME_NOT_ALLOWED",
        )

    return {
        "schema_version": "1.0.0",
        "subject": subject,
        "request_id": plan.get("request_id"),
        "profile": profile,
        "mount_mode": mount_mode,
        "representation_ref": representation.get("id") if representation else None,
        "representation": representation,
        "activity_ref": selected_activity.get("resource_ref") if selected_activity else None,
        "activity": selected_activity,
        "portable_package": portable_package,
        "resolution_plan": plan,
    }


def _shell(packaging_mode: str) -> str:
    return f'''<header class="site-nav" data-shell-ref="G9-TABLET-SHELL-V1">
<button id="back" type="button">← Back</button><a href="./index.html">Home</a>
<strong id="subject-context">Grade9V3 Explore</strong><a href="./question-bank/index.html">Question Bank</a>
<form id="site-search" role="search"><input id="site-search-input" type="search" aria-label="Search this page"><button type="submit">Search</button></form>
<button id="refresh" type="button">↻ Refresh</button><button id="display-down" type="button">A−</button><button id="display-up" type="button">A+</button>
<details><summary>More</summary><div>Packaging: {html.escape(packaging_mode)}</div></details>
</header>'''


def _shell_style() -> str:
    return """.site-nav{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:.5rem;min-height:3.5rem;padding:.4rem .75rem;border-bottom:1px solid #bbb;background:#fff;flex-wrap:wrap}
.site-nav a,.site-nav button,.site-nav input,.site-nav summary{font:inherit;min-height:3rem;box-sizing:border-box}
.site-nav a,.site-nav button,.site-nav summary{display:inline-flex;align-items:center;padding:.4rem .7rem;border:1px solid #999;border-radius:.5rem;text-decoration:none;color:inherit;background:#fff}
.site-nav input{padding:.4rem .6rem}.site-nav form{display:flex;gap:.5rem}.site-nav #subject-context{margin-inline:auto}
.explore-shell{display:grid;grid-template-columns:minmax(0,72fr) minmax(16rem,28fr);gap:1rem;max-width:80rem;margin:auto;padding:1rem}
.explore-stage,.explore-support{border:1px solid currentColor;border-radius:.75rem;padding:1rem;min-width:0}
.explore-stage iframe{width:100%;min-height:65vh;border:0}.meta{font-size:.85rem;opacity:.75}
@media(max-width:56rem){.explore-shell{grid-template-columns:minmax(0,1fr)}}"""


def _shell_script() -> str:
    return """<script>
document.querySelector("#back")?.addEventListener("click",()=>history.length>1?history.back():null);
document.querySelector("#refresh")?.addEventListener("click",()=>location.reload());
document.querySelector("#site-search")?.addEventListener("submit",(e)=>{e.preventDefault();const q=document.querySelector("#site-search-input").value.trim();if(q&&typeof window.find==="function")window.find(q);});
let scale=1;const apply=()=>document.documentElement.style.fontSize=(16*scale)+"px";
document.querySelector("#display-down")?.addEventListener("click",()=>{scale=Math.max(.8,scale-.1);apply();});
document.querySelector("#display-up")?.addEventListener("click",()=>{scale=Math.min(1.5,scale+.1);apply();});
</script>"""


def _static_representation(rep: dict | None) -> str:
    if not rep:
        return "<p>No static representation payload supplied.</p>"
    required = "".join(f"<li>{html.escape(str(item))}</li>" for item in rep.get("required_elements") or [])
    order = "".join(f"<li>{html.escape(str(item))}</li>" for item in rep.get("read_order") or [])
    correspondence = "".join(
        f"<li><strong>{html.escape(str(row.get('element','')))}</strong> ↔ {html.escape(str(row.get('symbol','')))}: {html.escape(str(row.get('in_words','')))}</li>"
        for row in rep.get("correspondence") or []
        if isinstance(row, dict)
    )
    return f"""<h2>Canonical representation</h2>
<p>{html.escape(str(rep.get("purpose") or ""))}</p>
{f"<h3>Required elements</h3><ul>{required}</ul>" if required else ""}
{f"<h3>Read order</h3><ol>{order}</ol>" if order else ""}
{f"<h3>Representation bridge</h3><ul>{correspondence}</ul>" if correspondence else ""}"""


def render_directory(package: dict, packaging_mode: str = "PUBLIC") -> dict[str, bytes]:
    _require(packaging_mode in PACKAGING_MODES - {"SINGLE_FILE"}, "EXPLORE_PACKAGING_MODE_INVALID")
    mount = package["mount_mode"]
    stage = ""
    files: dict[str, bytes] = {}

    if mount == "PORTABLE_SCENE":
        portable = package["portable_package"]
        stage = """<semantic-workbench id="portable-workbench"></semantic-workbench>
<p id="portable-label" class="meta"></p>
<script type="module">
import "./semantic-workbench.mjs";
import {mountPortableWorkbench} from "./portable-host.mjs";
const pkg=await fetch("./portable-package.json").then(r=>r.json());
mountPortableWorkbench(document.querySelector("#portable-workbench"),pkg);
document.querySelector("#portable-label").textContent=pkg.title;
window.__explorePageReady=true;
</script>"""
        rendered = build_portable_workbench.render()
        for source, target in [
            ("public/portable-workbench/runtime.mjs", "runtime.mjs"),
            ("public/portable-workbench/semantic-workbench.mjs", "semantic-workbench.mjs"),
            ("public/portable-workbench/portable-host.mjs", "portable-host.mjs"),
        ]:
            files[target] = rendered[source]
        files["portable-package.json"] = (
            json.dumps(portable, indent=2, ensure_ascii=False) + "\n"
        ).encode("utf-8")
    elif mount == "LEGACY_IFRAME":
        locator = html.escape(str(package["activity"]["locator"]), quote=True)
        stage = f"""<p class="meta">Existing ACTIVITY reused through the explicitly migration-only locator path.</p>
<iframe title="Existing interactive activity" src="{locator}" data-legacy-iframe="MIGRATION_ONLY"></iframe>"""
    else:
        stage = _static_representation(package.get("representation"))

    support = f"""<h2>Resolved delivery</h2>
<dl><dt>Mode</dt><dd>EXPLORE</dd><dt>Mount</dt><dd>{html.escape(mount)}</dd>
<dt>Representation</dt><dd>{html.escape(str(package.get("representation_ref") or "not required"))}</dd>
<dt>Activity</dt><dd>{html.escape(str(package.get("activity_ref") or "not required"))}</dd></dl>"""
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="grade9v3-packaging-mode" content="{html.escape(packaging_mode)}"><title>Grade9V3 Explore</title>
<style>body{{font:16px/1.45 system-ui,sans-serif;margin:0}}{_shell_style()}</style></head><body>
{_shell(packaging_mode)}<main class="explore-shell" data-explorer-profile="{html.escape(package['profile']['ref'])}" data-mount-mode="{html.escape(mount)}">
<section class="explore-stage">{stage}</section><aside class="explore-support">{support}</aside></main>{_shell_script()}</body></html>"""
    files["index.html"] = page.encode("utf-8")
    files["explore-page-package.json"] = (
        json.dumps({k:v for k,v in package.items() if k != "portable_package"}, indent=2, ensure_ascii=False) + "\n"
    ).encode("utf-8")
    return files


def render_single_file(package: dict) -> bytes:
    mount = package["mount_mode"]
    _require(mount != "LEGACY_IFRAME", "EXPLORE_SINGLE_FILE_LEGACY_IFRAME_UNSUPPORTED")
    if mount == "PORTABLE_SCENE":
        base = build_portable_workbench._offline_html([package["portable_package"]])
        base = base.replace(
            "<body><main>",
            "<body>" + _shell("SINGLE_FILE") + "<main>",
            1,
        )
        base = base.replace("</body>", _shell_script() + "</body>")
        return base.encode("utf-8")

    stage = _static_representation(package.get("representation"))
    page = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="grade9v3-packaging-mode" content="SINGLE_FILE"><title>Grade9V3 Explore</title>
<style>body{{font:16px/1.45 system-ui,sans-serif;margin:0}}{_shell_style()}</style></head><body>{_shell("SINGLE_FILE")}
<main class="explore-shell" data-explorer-profile="{html.escape(package['profile']['ref'])}" data-mount-mode="STATIC_FIGURE">
<section class="explore-stage">{stage}</section><aside class="explore-support"><h2>Static canonical delivery</h2></aside></main>
{_shell_script()}</body></html>"""
    return page.encode("utf-8")


def write_mode(package: dict, mode: str, out: Path) -> None:
    _require(mode in package["profile"]["packaging_modes"], "EXPLORE_PACKAGING_MODE_NOT_ALLOWED", mode)
    if mode == "SINGLE_FILE":
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(render_single_file(package))
        return
    out.mkdir(parents=True, exist_ok=True)
    for name, content in render_directory(package, mode).items():
        path = out / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--plan", type=Path, required=True)
    parser.add_argument("--mode", choices=sorted(PACKAGING_MODES), required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    package = compile_page_package(load(args.plan))
    write_mode(package, args.mode, args.out)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
