#!/usr/bin/env python3
"""Generate public and standalone Core learner hosts from one neutral template."""
from __future__ import annotations

import argparse
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

HOSTS = {
    "public/core-learning/index.html": {
        "data_src": "./data.js",
        "runtime_base": "../js/core-learning",
    },
    "standalone/core-learning/index.html": {
        "data_src": "../../public/core-learning/data.js",
        "runtime_base": "../../public/js/core-learning",
    },
}

TEMPLATE = r'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Core learner</title>
  <style>
    :root{font-family:system-ui,-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;color-scheme:light dark}
    body{margin:0;padding:1rem} main{max-width:72rem;margin:0 auto;display:grid;gap:1rem}
    .chooser,.explorer-panel{display:grid;gap:.5rem;border:1px solid currentColor;border-radius:.75rem;padding:1rem}
    .chooser-row{display:flex;flex-wrap:wrap;gap:.75rem;align-items:end}
    label{display:grid;gap:.35rem;min-width:min(100%,28rem);flex:1}
    select,button{font:inherit;min-height:2.75rem} button{padding:.5rem .85rem}
    [data-status]{margin:0}.explorer-frame{width:100%;min-height:30rem;border:1px solid currentColor;border-radius:.5rem;background:Canvas}
    [hidden]{display:none!important}
    @media (max-width:36rem){body{padding:.5rem}.chooser,.explorer-panel{padding:.75rem}.explorer-frame{min-height:36rem}}
  </style>
</head>
<body>
  <main>
    <section class="chooser" aria-labelledby="projection-title">
      <h1 id="projection-title">Core learner</h1>
      <div class="chooser-row">
        <label>
          Compiled learning activity
          <select id="projection-select" aria-describedby="projection-status"></select>
        </label>
        <button id="load-projection" type="button">Load</button>
      </div>
      <p id="projection-status" data-status role="status" aria-live="polite"></p>
    </section>
    <section class="explorer-panel" id="explorer-panel" aria-labelledby="explorer-title" hidden>
      <h2 id="explorer-title">Interactive scientific representation</h2>
      <iframe id="explorer-frame" class="explorer-frame" title="Interactive scientific representation"></iframe>
    </section>
    <core-learning-page id="learner"></core-learning-page>
  </main>

  <script src="__CORE_DATA_SRC__"></script>
  <script type="module">
    import "__CORE_RUNTIME_BASE__/semantic-workbench.mjs";
    import "__CORE_RUNTIME_BASE__/core-learning-page.mjs";
    import { mountCoreLearningPage } from "__CORE_RUNTIME_BASE__/core-learning-host.mjs";

    const data = window.GRADE9V3_CORE;
    const rows = Array.isArray(data?.core_projections) ? data.core_projections : [];
    const learner = document.getElementById("learner");
    const select = document.getElementById("projection-select");
    const loadButton = document.getElementById("load-projection");
    const status = document.getElementById("projection-status");
    const explorerPanel = document.getElementById("explorer-panel");
    const explorerFrame = document.getElementById("explorer-frame");
    const registries = window.CORE_LEARNING_REGISTRIES || {};

    function labelFor(row) {
      const core = row?.projection?.core || "Core";
      const source = row?.source_ref || row?.id || "activity";
      return [row?.subject, core, source].filter(Boolean).join(" · ");
    }

    function setStatus(message) { status.textContent = message; }

    function explorerUrl(locator) {
      if (typeof locator !== "string" || !locator.startsWith("public/") || locator.includes("..")) return null;
      return new URL("../../" + locator, window.location.href).href;
    }

    function mountExplorer(row) {
      const url = explorerUrl(row?.explorer_locator);
      explorerPanel.hidden = !url;
      if (url) explorerFrame.src = url;
      else explorerFrame.removeAttribute("src");
    }

    function mount(id, { updateUrl = true } = {}) {
      try {
        const row = rows.find((item) => item.id === id);
        const result = mountCoreLearningPage(learner, data, id, registries);
        select.value = result.id;
        mountExplorer(row);
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

    if (!select.options.length) {
      select.disabled = true;
      loadButton.disabled = true;
      setStatus("No compiled Core learner projections are available in this generated data build.");
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


def render_host(*, data_src: str, runtime_base: str) -> bytes:
    rendered = TEMPLATE.replace("__CORE_DATA_SRC__", data_src).replace("__CORE_RUNTIME_BASE__", runtime_base)
    if "__CORE_DATA_SRC__" in rendered or "__CORE_RUNTIME_BASE__" in rendered:
        raise ValueError("CORE_LEARNING_HOST_TEMPLATE_UNRESOLVED")
    return rendered.encode("utf-8")


def render() -> dict[str, bytes]:
    return {
        relative: render_host(data_src=config["data_src"], runtime_base=config["runtime_base"])
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
    parser = argparse.ArgumentParser(description="Generate or verify Core learner hosts")
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
    for relative in sorted(rendered): print(f"wrote {relative}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
