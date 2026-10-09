#!/usr/bin/env python3
"""Generate public and repository-alternate Core learner hosts from one neutral tablet template."""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

HOSTS = {
    "public/core-learning/index.html": {
        "data_src": "./data.js",
        "runtime_base": "../js/core-learning",
        "site_css": "../css/site.css",
        "display_src": "../js/display-controls.js",
        "header_src": "../js/site-header.js",
        "site_root": "../",
        "site_parent": "../index.html",
        "packaging_mode": "PUBLIC",
    },
    "standalone/core-learning/index.html": {
        "data_src": "../../public/core-learning/data.js",
        "runtime_base": "../../public/js/core-learning",
        "site_css": "../../public/css/site.css",
        "display_src": "../../public/js/display-controls.js",
        "header_src": "../../public/js/site-header.js",
        "site_root": "../../public/",
        "site_parent": "../../public/index.html",
        "packaging_mode": "REPOSITORY_ALTERNATE_HOST",
    },
}

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="grade9v3-packaging-mode" content="__PACKAGING_MODE__">
  <title>Core learner · Grade9V3</title>
  <link rel="stylesheet" href="__SITE_CSS__">
  <style>
    :root{--core-host-max:80rem}
    body{margin:0}
    main.core-host{max-width:var(--core-host-max);margin:0 auto;padding:1rem;display:grid;gap:1rem}
    .core-hero,.chooser,.explorer-panel,.delivery-band{display:grid;gap:.65rem;border:1px solid var(--border,#d7dce2);border-radius:1rem;padding:1rem;background:var(--surface,#fff)}
    .core-hero{grid-template-columns:minmax(0,1fr) auto;align-items:start}
    .core-kicker{margin:0;font-size:.78rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase;opacity:.72}
    .core-hero h1{margin:.15rem 0 .35rem;font-size:clamp(1.55rem,4vw,2.25rem)}
    .core-hero p{margin:.2rem 0}
    .delivery-chip{display:inline-flex;align-items:center;min-height:2rem;padding:.25rem .6rem;border:1px solid currentColor;border-radius:999px;font-size:.78rem;font-weight:700}
    .chooser>summary{font-weight:800;cursor:pointer;min-height:3rem;display:flex;align-items:center}
    .chooser-row{display:flex;flex-wrap:wrap;gap:.75rem;align-items:end}
    .chooser-row label{display:grid;gap:.35rem;min-width:min(100%,30rem);flex:1}
    select,button,.core-action-link{font:inherit;min-height:3rem}
    select,button{padding:.55rem .8rem}
    .core-action-link{display:inline-flex;align-items:center;padding:0 .85rem;border:1px solid currentColor;border-radius:.7rem;text-decoration:none}
    [data-status]{margin:0}
    .delivery-band{grid-template-columns:repeat(3,minmax(0,1fr))}
    .delivery-band strong{display:block;font-size:.78rem;text-transform:uppercase;letter-spacing:.06em;opacity:.68}
    .delivery-band span{display:block;margin-top:.2rem;overflow-wrap:anywhere}
    .explorer-heading{display:flex;gap:.75rem;align-items:center;justify-content:space-between;flex-wrap:wrap}
    .explorer-heading h2{margin:0}
    .migration-badge{font-size:.75rem;font-weight:800;letter-spacing:.05em;text-transform:uppercase}
    .explorer-frame{width:100%;min-height:32rem;border:1px solid currentColor;border-radius:.75rem;background:Canvas}
    .host-note{font-size:.9rem;opacity:.78}
    [hidden]{display:none!important}
    @media (max-width:56rem){
      main.core-host{padding:.75rem}
      .core-hero{grid-template-columns:1fr}
      .delivery-band{grid-template-columns:1fr}
      .explorer-frame{min-height:34rem}
    }
    @media (max-width:36rem){
      main.core-host{padding:.5rem}
      .core-hero,.chooser,.explorer-panel,.delivery-band{padding:.8rem;border-radius:.8rem}
      .chooser-row{display:grid}
      .explorer-frame{min-height:38rem}
    }
    @media (prefers-reduced-motion:reduce){*{scroll-behavior:auto!important}}
  </style>
</head>
<body>
  <header class="site-nav">
    <a href="__SITE_ROOT__index.html" class="brand-link">
      <span class="logo-icon" aria-hidden="true">⚡</span>
      <span>Grade9V3 Knowledge Portal</span>
      <span class="brand-badge">Core</span>
    </a>
    <nav class="nav-links" aria-label="Primary">
      <a href="__SITE_ROOT__index.html">Home</a>
      <a href="__SITE_ROOT__question-bank/index.html" data-site-question-bank>Question Bank</a>
      <button type="button" class="g9-display-trigger-btn" onclick="window.Grade9Display.togglePopover()" title="Adjust Font Size and UI Zoom Scale"><span>🔤 / 🔍 Display</span></button>
    </nav>
  </header>

  <main class="core-host">
    <section class="core-hero" aria-labelledby="projection-title">
      <div>
        <p class="core-kicker" id="subject-context">Compiled canonical learner activity</p>
        <h1 id="projection-title">Core learner</h1>
        <p class="host-note" role="note">Compiler design preview only. Curriculum approval, source custody and QRT release remain unverified; TEST sandbox activities are withheld from this chooser.</p>
        <p id="projection-status" data-status role="status" aria-live="polite"></p>
      </div>
      <span class="delivery-chip" id="delivery-chip">Resolving blueprint…</span>
    </section>

    <details class="chooser" open>
      <summary>Choose compiled activity</summary>
      <div class="chooser-row">
        <label>
          Activity
          <select id="projection-select" aria-describedby="projection-status"></select>
        </label>
        <button id="load-projection" type="button">Load activity</button>
      </div>
      <details id="availability-panel" hidden>
        <summary>Unavailable or held activities</summary>
        <ul id="availability-list"></ul>
      </details>
    </details>

    <section class="delivery-band" aria-label="Resolved web delivery contract">
      <div><strong>Blueprint</strong><span id="blueprint-ref">—</span></div>
      <div><strong>Layout</strong><span id="layout-family">—</span></div>
      <div><strong>Packaging</strong><span id="packaging-modes">—</span></div>
    </section>

    <section class="explorer-panel" id="explorer-panel" aria-labelledby="explorer-title" hidden>
      <div class="explorer-heading">
        <div>
          <span class="migration-badge">Legacy iframe · migration only</span>
          <h2 id="explorer-title">Interactive scientific representation</h2>
        </div>
        <a class="core-action-link" id="explorer-open" href="#" target="_blank" rel="noopener">Open full page</a>
      </div>
      <p class="host-note">New builder work should prefer a portable scene or component mount. This iframe preserves an existing explorer while it is migrated.</p>
      <iframe id="explorer-frame" class="explorer-frame" title="Interactive scientific representation" loading="lazy"></iframe>
    </section>

    <core-learning-page id="learner"></core-learning-page>
  </main>

  <script src="__CORE_DATA_SRC__"></script>
  <script src="__DISPLAY_SRC__"></script>
  <script src="__HEADER_SRC__" data-site-root="__SITE_ROOT__" data-site-parent="__SITE_PARENT__"></script>
  <script type="module">
    import "__CORE_RUNTIME_BASE__/semantic-workbench.mjs";
    import "__CORE_RUNTIME_BASE__/core-learning-page.mjs";
    import { mountCoreLearningPage } from "__CORE_RUNTIME_BASE__/core-learning-host.mjs";

    const data = window.GRADE9V3_CORE;
    const rows = (Array.isArray(data?.core_projections) ? data.core_projections : []).filter(row => row?.subject !== "TEST");
    const availability = (Array.isArray(data?.bucket_availability) ? data.bucket_availability : []).filter(row => row?.subject !== "TEST");
    const learner = document.getElementById("learner");
    const select = document.getElementById("projection-select");
    const loadButton = document.getElementById("load-projection");
    const status = document.getElementById("projection-status");
    const subjectContext = document.getElementById("subject-context");
    const deliveryChip = document.getElementById("delivery-chip");
    const blueprintRef = document.getElementById("blueprint-ref");
    const layoutFamily = document.getElementById("layout-family");
    const packagingModes = document.getElementById("packaging-modes");
    const availabilityPanel = document.getElementById("availability-panel");
    const availabilityList = document.getElementById("availability-list");
    const explorerPanel = document.getElementById("explorer-panel");
    const explorerFrame = document.getElementById("explorer-frame");
    const explorerOpen = document.getElementById("explorer-open");
    const registries = window.CORE_LEARNING_REGISTRIES || {};
    const siteRoot = "__SITE_ROOT__";

    function labelFor(row) {
      const core = row?.projection?.core || "Core";
      const source = row?.source_ref || row?.id || "activity";
      return [row?.subject, core, source].filter(Boolean).join(" · ");
    }

    function setStatus(message) { status.textContent = message; }

    function renderAvailability() {
      const unavailable = availability.filter((row) =>
        row?.status === "UNSUPPORTED" || (Array.isArray(row?.findings) && row.findings.length)
      );
      availabilityPanel.hidden = unavailable.length === 0;
      availabilityList.replaceChildren();
      for (const row of unavailable) {
        const item = document.createElement("li");
        const finding = Array.isArray(row.findings) && row.findings.length ? row.findings[0] : row;
        const code = finding?.code || "UNAVAILABLE";
        const detail = finding?.detail ? ` — ${finding.detail}` : "";
        item.textContent = [row.subject, row.bucket_ref, code].filter(Boolean).join(" · ") + detail;
        availabilityList.append(item);
      }
    }

    function explorerUrl(locator) {
      if (typeof locator !== "string" || !locator.startsWith("public/") || locator.includes("..")) return null;
      const relative = locator.slice("public/".length);
      return new URL(siteRoot + relative, window.location.href).href;
    }

    function mountExplorer(row) {
      const url = explorerUrl(row?.explorer_locator);
      explorerPanel.hidden = !url;
      if (url) {
        explorerFrame.src = url;
        explorerOpen.href = url;
      } else {
        explorerFrame.removeAttribute("src");
        explorerOpen.removeAttribute("href");
      }
    }

    function renderDelivery(row) {
      const web = row?.projection?.delivery?.web;
      if (!web) {
        deliveryChip.textContent = "Blueprint unavailable";
        blueprintRef.textContent = "Not assigned";
        layoutFamily.textContent = "Not assigned";
        packagingModes.textContent = "Not assigned";
        return;
      }
      deliveryChip.textContent = web.layout_family;
      blueprintRef.textContent = web.blueprint_ref;
      layoutFamily.textContent = web.layout_family + " · " + web.shell_ref;
      packagingModes.textContent = (web.packaging_modes || []).join(" · ");
      document.documentElement.dataset.webBlueprint = web.blueprint_ref;
      document.documentElement.dataset.layoutFamily = web.layout_family;
    }

    function mount(id, { updateUrl = true } = {}) {
      try {
        const row = rows.find((item) => item.id === id);
        if (!row) throw new Error("CORE_LEARNING_PROJECTION_NOT_PUBLIC_PREVIEW");
        const result = mountCoreLearningPage(learner, data, id, registries);
        select.value = result.id;
        mountExplorer(row);
        renderDelivery(row);
        subjectContext.textContent = [row?.subject, row?.projection?.core].filter(Boolean).join(" · ") || "Compiled canonical learner activity";
        setStatus(`Loaded ${labelFor(row)}.`);
        if (updateUrl) {
          const url = new URL(window.location.href);
          url.searchParams.set("projection", result.id);
          history.replaceState(null, "", url);
        }
      } catch (error) {
        const code = error?.code || error?.name || "CORE_LEARNING_LOAD_FAILED";
        setStatus(`Unable to load activity: ${code}.`);
      }
    }

    for (const row of rows) {
      if (!row || typeof row.id !== "string" || !row.id) continue;
      const option = document.createElement("option");
      option.value = row.id;
      option.textContent = labelFor(row);
      select.append(option);
    }

    renderAvailability();

    if (!select.options.length) {
      select.disabled = true;
      loadButton.disabled = true;
      const first = availability.find((row) => row?.status === "UNSUPPORTED");
      const reason = first?.code ? ` Reason: ${first.code}.` : "";
      setStatus("No compiled Core learner projections are available in this generated data build." + reason);
    } else {
      loadButton.addEventListener("click", () => mount(select.value));
      select.addEventListener("change", () => setStatus(`Selected ${labelFor(rows.find((row) => row.id === select.value))}.`));
      const requested = new URL(window.location.href).searchParams.get("projection");
      if (requested && rows.some((row) => row.id === requested)) mount(requested, { updateUrl: false });
      else if (requested) {
        select.value = rows[0].id;
        setStatus("Requested projection was not found. Select an available compiled activity.");
      } else mount(rows[0].id);
    }

    window.__coreLearningStaticHostReady = true;
  </script>
</body>
</html>
'''


def render_host(
    *,
    data_src: str,
    runtime_base: str,
    site_css: str,
    display_src: str,
    header_src: str,
    site_root: str,
    site_parent: str,
    packaging_mode: str,
) -> bytes:
    replacements = {
        "__CORE_DATA_SRC__": data_src,
        "__CORE_RUNTIME_BASE__": runtime_base,
        "__SITE_CSS__": site_css,
        "__DISPLAY_SRC__": display_src,
        "__HEADER_SRC__": header_src,
        "__SITE_ROOT__": site_root,
        "__SITE_PARENT__": site_parent,
        "__PACKAGING_MODE__": packaging_mode,
    }
    rendered = TEMPLATE
    for token, value in replacements.items():
        rendered = rendered.replace(token, value)
    unresolved = [token for token in replacements if token in rendered]
    if unresolved:
        raise ValueError("CORE_LEARNING_HOST_TEMPLATE_UNRESOLVED: " + ", ".join(unresolved))
    return rendered.encode("utf-8")


def render() -> dict[str, bytes]:
    return {
        relative: render_host(**config)
        for relative, config in HOSTS.items()
    }


def write() -> dict[str, bytes]:
    rendered = render()
    for relative, content in rendered.items():
        path = REPO / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    return rendered


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rendered = render()
    if args.check:
        stale = [
            relative for relative, content in rendered.items()
            if not (REPO / relative).is_file() or (REPO / relative).read_bytes() != content
        ]
        for relative in stale:
            print(f"generated file is stale: {relative}")
        return 1 if stale else 0
    write()
    for relative in sorted(rendered):
        print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
