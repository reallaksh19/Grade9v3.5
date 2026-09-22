#!/usr/bin/env python3
"""Generate public and standalone Core learner hosts from one neutral template.

The host owns composition and resource wiring only. Projection data and runtime
behavior remain external generated authorities.
"""
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

_TEMPLATE = "<!doctype html>\n<html lang=\"en\">\n<head>\n  <meta charset=\"utf-8\">\n  <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n  <title>Core learner</title>\n  <style>\n    :root{font-family:system-ui,-apple-system,BlinkMacSystemFont,\"Segoe UI\",sans-serif;color-scheme:light dark}\n    body{margin:0;padding:1rem}\n    main{max-width:72rem;margin:0 auto;display:grid;gap:1rem}\n    .chooser{display:grid;gap:.5rem;border:1px solid currentColor;border-radius:.75rem;padding:1rem}\n    .chooser-row{display:flex;flex-wrap:wrap;gap:.75rem;align-items:end}\n    label{display:grid;gap:.35rem;min-width:min(100%,28rem);flex:1}\n    select,button{font:inherit;min-height:2.75rem}\n    button{padding:.5rem .85rem}\n    [data-status]{margin:0}\n    @media (max-width:36rem){body{padding:.5rem}.chooser{padding:.75rem}}\n  </style>\n</head>\n<body>\n  <main>\n    <section class=\"chooser\" aria-labelledby=\"projection-title\">\n      <h1 id=\"projection-title\">Core learner</h1>\n      <div class=\"chooser-row\">\n        <label>\n          Compiled learning activity\n          <select id=\"projection-select\" aria-describedby=\"projection-status\"></select>\n        </label>\n        <button id=\"load-projection\" type=\"button\">Load</button>\n      </div>\n      <p id=\"projection-status\" data-status role=\"status\" aria-live=\"polite\"></p>\n    </section>\n    <core-learning-page id=\"learner\"></core-learning-page>\n  </main>\n\n  <script src=\"__CORE_DATA_SRC__\"></script>\n  <script type=\"module\">\n    import \"__CORE_RUNTIME_BASE__/semantic-workbench.mjs\";\n    import \"__CORE_RUNTIME_BASE__/core-learning-page.mjs\";\n    import { mountCoreLearningPage } from \"__CORE_RUNTIME_BASE__/core-learning-host.mjs\";\n\n    const data = window.GRADE9V3_CORE;\n    const rows = Array.isArray(data?.core_projections) ? data.core_projections : [];\n    const learner = document.getElementById(\"learner\");\n    const select = document.getElementById(\"projection-select\");\n    const loadButton = document.getElementById(\"load-projection\");\n    const status = document.getElementById(\"projection-status\");\n    const registries = window.CORE_LEARNING_REGISTRIES || {};\n\n    function labelFor(row) {\n      const core = row?.projection?.core || \"Core\";\n      const source = row?.source_ref || row?.id || \"activity\";\n      return [row?.subject, core, source].filter(Boolean).join(\" · \");\n    }\n\n    function setStatus(message) {\n      status.textContent = message;\n    }\n\n    function mount(id, { updateUrl = true } = {}) {\n      try {\n        const result = mountCoreLearningPage(learner, data, id, registries);\n        select.value = result.id;\n        setStatus(`Loaded ${labelFor(rows.find((row) => row.id === result.id))}.`);\n        if (updateUrl) {\n          const url = new URL(window.location.href);\n          url.searchParams.set(\"projection\", result.id);\n          history.replaceState(null, \"\", url);\n        }\n      } catch (error) {\n        const code = error?.code || error?.name || \"CORE_LEARNING_LOAD_FAILED\";\n        setStatus(`Unable to load activity: ${code}.`);\n      }\n    }\n\n    for (const row of rows) {\n      if (!row || typeof row.id !== \"string\" || !row.id) continue;\n      const option = document.createElement(\"option\");\n      option.value = row.id;\n      option.textContent = labelFor(row);\n      select.append(option);\n    }\n\n    if (!select.options.length) {\n      select.disabled = true;\n      loadButton.disabled = true;\n      setStatus(\"No compiled Core learner projections are available in this generated data build.\");\n    } else {\n      loadButton.addEventListener(\"click\", () => mount(select.value));\n      select.addEventListener(\"change\", () => setStatus(`Selected ${labelFor(rows.find((row) => row.id === select.value))}.`));\n\n      const requested = new URL(window.location.href).searchParams.get(\"projection\");\n      if (requested && rows.some((row) => row.id === requested)) {\n        mount(requested, { updateUrl: false });\n      } else if (requested) {\n        select.value = rows[0].id;\n        setStatus(\"Requested projection was not found. Select an available compiled activity.\");\n      } else {\n        mount(rows[0].id);\n      }\n    }\n\n    window.__coreLearningStaticHostReady = true;\n  </script>\n</body>\n</html>\n"


def render_host(*, data_src: str, runtime_base: str) -> bytes:
    rendered = (
        _TEMPLATE
        .replace("__CORE_DATA_SRC__", data_src)
        .replace("__CORE_RUNTIME_BASE__", runtime_base)
    )
    if "__CORE_DATA_SRC__" in rendered or "__CORE_RUNTIME_BASE__" in rendered:
        raise ValueError("CORE_LEARNING_HOST_TEMPLATE_UNRESOLVED")
    return rendered.encode("utf-8")


def render() -> dict[str, bytes]:
    return {
        relative: render_host(
            data_src=config["data_src"],
            runtime_base=config["runtime_base"],
        )
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
            relative
            for relative, content in rendered.items()
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
