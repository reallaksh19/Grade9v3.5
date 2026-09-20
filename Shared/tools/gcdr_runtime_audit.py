#!/usr/bin/env python3
"""Audit GCDR HTML implementations with static checks and a DOM-lite JS smoke runtime.

This is not a visual/layout browser test. It executes inline JavaScript under Node's VM with
minimal DOM element semantics, mutates interactive controls, checks that handlers have causal
effects, and checks reset determinism. It is designed to falsify mock/dead controls and stale
runtime claims without pretending to prove rendering quality.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import subprocess
import sys
import tempfile
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

from Shared.tools import explorer_design_guard  # noqa: E402

KIND = explorer_design_guard.KIND
PLACEHOLDER_RE = re.compile(r"\b(undefined|null|todo|tbd|placeholder)\b", re.I)
RUNTIME_CHECKS = {
    "implementation_locator",
    "static_syntax",
    "handler_and_control_integrity",
    "identifier_integrity",
    "no_placeholder_or_undefined_output",
    "deterministic_reset",
    "runtime_smoke",
    "accessibility_baseline",
}


class ExplorerParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.elements: list[dict[str, Any]] = []
        self.ids: list[str] = []
        self.scripts: list[str] = []
        self.script_srcs: list[str] = []
        self.visible: list[str] = []
        self.label_for: set[str] = set()
        self._label_depth = 0
        self._script_depth = 0
        self._style_depth = 0
        self._script_buf: list[str] = []
        self._button_stack: list[dict[str, Any]] = []
        self._select_stack: list[dict[str, Any]] = []

    @staticmethod
    def _attrs(attrs):
        return {k: (v if v is not None else "") for k, v in attrs}

    def handle_starttag(self, tag, attrs):
        a = self._attrs(attrs)
        if tag == "label":
            self._label_depth += 1
            if a.get("for"):
                self.label_for.add(a["for"])
        if tag == "style":
            self._style_depth += 1
        if tag == "script":
            self._script_depth += 1
            self._script_buf = []
            if a.get("src"):
                self.script_srcs.append(a["src"])

        element_id = a.get("id") or None
        if element_id:
            self.ids.append(element_id)

        if tag in {"input", "select", "button", "textarea"} or element_id:
            key = element_id or f"anon-{len(self.elements)}"
            dataset = {
                k[5:].replace("-", "_"): v
                for k, v in a.items()
                if k.startswith("data-")
            }
            row = {
                "key": key,
                "id": element_id,
                "tag": tag,
                "type": a.get("type", "text" if tag == "input" else tag),
                "value": a.get("value", ""),
                "checked": "checked" in a,
                "disabled": "disabled" in a,
                "dataset": dataset,
                "options": [],
                "selected_index": 0,
                "wrapped_label": self._label_depth > 0,
                "aria_label": a.get("aria-label", ""),
                "aria_labelledby": a.get("aria-labelledby", ""),
                "title": a.get("title", ""),
                "text": "",
                "min": a.get("min"),
                "max": a.get("max"),
                "step": a.get("step"),
            }
            self.elements.append(row)
            if tag == "button":
                self._button_stack.append(row)
            if tag == "select":
                self._select_stack.append(row)

        if tag == "option" and self._select_stack:
            row = self._select_stack[-1]
            value = a.get("value", "")
            row["options"].append(value)
            if "selected" in a:
                row["selected_index"] = len(row["options"]) - 1

    def handle_endtag(self, tag):
        if tag == "label" and self._label_depth:
            self._label_depth -= 1
        if tag == "style" and self._style_depth:
            self._style_depth -= 1
        if tag == "script" and self._script_depth:
            self._script_depth -= 1
            if self._script_buf:
                self.scripts.append("".join(self._script_buf))
            self._script_buf = []
        if tag == "button" and self._button_stack:
            self._button_stack.pop()
        if tag == "select" and self._select_stack:
            row = self._select_stack.pop()
            if row["options"]:
                row["value"] = row["options"][row["selected_index"]]

    def handle_data(self, data):
        if self._script_depth:
            self._script_buf.append(data)
            return
        if self._style_depth:
            return
        if data.strip():
            self.visible.append(data)
        if self._button_stack:
            self._button_stack[-1]["text"] += data


NODE_HARNESS = r"""
const fs = require('fs');
const vm = require('vm');
const spec = JSON.parse(fs.readFileSync(0, 'utf8'));

function makeElement(row) {
  return {
    _key: row.key,
    id: row.id,
    tagName: row.tag.toUpperCase(),
    type: row.type,
    value: row.value,
    checked: !!row.checked,
    disabled: !!row.disabled,
    dataset: Object.assign({}, row.dataset || {}),
    textContent: '',
    innerHTML: '',
    onclick: null,
    onchange: null,
    oninput: null,
    options: (row.options || []).map(v => ({value: v})),
    selectedIndex: row.selected_index || 0,
    min: row.min,
    max: row.max,
    step: row.step,
  };
}

function setup() {
  const elements = spec.elements.map(makeElement);
  const byId = {};
  for (const el of elements) if (el.id) byId[el.id] = el;
  const document = {
    querySelector(sel) {
      if (sel.startsWith('#')) return byId[sel.slice(1)] || null;
      return null;
    },
    getElementById(id) { return byId[id] || null; },
    querySelectorAll(sel) {
      const m = sel.match(/^\[data-([a-zA-Z0-9_-]+)\]$/);
      if (m) {
        const key = m[1].replace(/-/g, '_');
        return elements.filter(el => Object.prototype.hasOwnProperty.call(el.dataset, key));
      }
      return [];
    },
  };
  const context = {document, console, Math, JSON};
  for (const [id, el] of Object.entries(byId)) {
    if (/^[A-Za-z_$][A-Za-z0-9_$]*$/.test(id)) context[id] = el;
  }
  vm.createContext(context);
  for (const script of spec.scripts) vm.runInContext(script, context, {timeout: 1000});
  return {context, elements, byId};
}

function snapshot(elements) {
  const out = {};
  for (const el of elements) {
    out[el._key] = {
      value: String(el.value),
      checked: !!el.checked,
      textContent: String(el.textContent),
      innerHTML: String(el.innerHTML),
    };
  }
  return out;
}

function outputChanged(before, after, targetKey) {
  for (const key of Object.keys(after)) {
    if (key === targetKey) continue;
    if (JSON.stringify(before[key]) !== JSON.stringify(after[key])) return true;
  }
  return false;
}

function chooseHandler(el) {
  if (el.tagName === 'BUTTON') return el.onclick;
  if (el.type === 'checkbox' || el.type === 'radio') return el.onchange || el.onclick || el.oninput;
  return el.oninput || el.onchange || el.onclick;
}

function mutate(el) {
  if (el.tagName === 'BUTTON') return;
  if (el.type === 'checkbox' || el.type === 'radio') {
    el.checked = !el.checked;
    return;
  }
  if (el.tagName === 'SELECT' && el.options.length > 1) {
    el.selectedIndex = (el.selectedIndex + 1) % el.options.length;
    el.value = el.options[el.selectedIndex].value;
    return;
  }
  if (el.type === 'range' || el.type === 'number') {
    const current = Number(el.value);
    const min = el.min !== null && el.min !== undefined && el.min !== '' ? Number(el.min) : current - 1;
    const max = el.max !== null && el.max !== undefined && el.max !== '' ? Number(el.max) : current + 1;
    el.value = String(Math.abs(current - min) > 1e-9 ? min : max);
    return;
  }
  el.value = String(el.value) + '__changed';
}

const result = {init_error: null, interactions: [], reset: {present: false, restores: false}, snapshots: []};
try {
  const initialRun = setup();
  const initial = snapshot(initialRun.elements);
  result.snapshots.push(initial);

  for (const row of spec.elements) {
    if (row.disabled) continue;
    if (!['input','select','button','textarea'].includes(row.tag)) continue;
    const run = setup();
    const el = run.elements.find(x => x._key === row.key);
    const handler = chooseHandler(el);
    const before = snapshot(run.elements);
    const item = {key: row.key, has_handler: typeof handler === 'function', causes_effect: false, error: null};
    try {
      if (typeof handler === 'function') {
        mutate(el);
        handler.call(el, {target: el, currentTarget: el});
        const after = snapshot(run.elements);
        item.causes_effect = outputChanged(before, after, el._key);
        result.snapshots.push(after);
      }
    } catch (err) {
      item.error = String(err && err.stack ? err.stack : err);
    }
    result.interactions.push(item);
  }

  const resetRow = spec.elements.find(row =>
    row.tag === 'button' && (
      /reset/i.test(row.id || '') ||
      /reset/i.test(row.text || '') ||
      String((row.dataset || {}).action || '').toLowerCase() === 'reset'
    )
  );
  if (resetRow) {
    result.reset.present = true;
    const run = setup();
    const resetEl = run.elements.find(x => x._key === resetRow.key);
    const targetRow = spec.elements.find(row =>
      !row.disabled && row.key !== resetRow.key &&
      ['input','select','button','textarea'].includes(row.tag)
    );
    if (targetRow) {
      const target = run.elements.find(x => x._key === targetRow.key);
      const handler = chooseHandler(target);
      if (typeof handler === 'function') {
        mutate(target);
        handler.call(target, {target, currentTarget: target});
      }
    }
    if (typeof resetEl.onclick === 'function') {
      resetEl.onclick.call(resetEl, {target: resetEl, currentTarget: resetEl});
      const afterReset = snapshot(run.elements);
      const normalizedInitial = JSON.parse(JSON.stringify(initial));
      delete normalizedInitial[resetRow.key];
      const normalizedAfter = JSON.parse(JSON.stringify(afterReset));
      delete normalizedAfter[resetRow.key];
      result.reset.restores = JSON.stringify(normalizedInitial) === JSON.stringify(normalizedAfter);
      result.snapshots.push(afterReset);
    }
  }
} catch (err) {
  result.init_error = String(err && err.stack ? err.stack : err);
}
process.stdout.write(JSON.stringify(result));
"""


def _parse_html(text: str) -> ExplorerParser:
    parser = ExplorerParser()
    parser.feed(text)
    parser.close()
    return parser


def _node_check(scripts: list[str]) -> tuple[bool, list[str]]:
    node = shutil.which("node")
    if not node:
        return False, ["node runtime unavailable"]
    errors = []
    with tempfile.TemporaryDirectory() as tmp:
        for idx, script in enumerate(scripts):
            path = Path(tmp) / f"script-{idx}.js"
            path.write_text(script, encoding="utf-8")
            try:
                proc = subprocess.run(
                    [node, "--check", str(path)],
                    text=True,
                    capture_output=True,
                    timeout=15,
                )
            except subprocess.TimeoutExpired:
                errors.append(f"{path.name}: node syntax check timed out after 15 seconds")
                continue
            if proc.returncode:
                errors.append((proc.stderr or proc.stdout).strip())
    return not errors, errors


def _runtime(parser: ExplorerParser) -> dict:
    node = shutil.which("node")
    if not node:
        return {"init_error": "node runtime unavailable", "interactions": [], "reset": {}}
    spec = {"elements": parser.elements, "scripts": parser.scripts}
    try:
        proc = subprocess.run(
            [node, "-e", NODE_HARNESS],
            input=json.dumps(spec),
            text=True,
            capture_output=True,
            timeout=20,
        )
    except subprocess.TimeoutExpired:
        return {
            "init_error": "DOM-lite Node runtime timed out after 20 seconds",
            "interactions": [],
            "reset": {},
        }
    if proc.returncode:
        return {
            "init_error": (proc.stderr or proc.stdout).strip() or f"node exited {proc.returncode}",
            "interactions": [],
            "reset": {},
        }
    try:
        return json.loads(proc.stdout)
    except json.JSONDecodeError:
        return {"init_error": f"invalid runtime JSON: {proc.stdout[:500]}", "interactions": [], "reset": {}}


def _accessible(parser: ExplorerParser) -> tuple[bool, list[str]]:
    problems = []
    for row in parser.elements:
        if row["disabled"]:
            continue
        if row["tag"] == "button":
            if not (row["text"].strip() or row["aria_label"] or row["title"]):
                problems.append(f"{row['key']}: button has no accessible name")
            continue
        if row["tag"] in {"input", "select", "textarea"}:
            if row["type"] == "hidden":
                continue
            labelled = (
                row["wrapped_label"]
                or bool(row["id"] and row["id"] in parser.label_for)
                or bool(row["aria_label"])
                or bool(row["aria_labelledby"])
            )
            if not labelled:
                problems.append(f"{row['key']}: control has no associated label")
    return not problems, problems


def inspect_html(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    parser = _parse_html(text)
    duplicates = sorted(k for k, n in Counter(parser.ids).items() if n > 1)
    syntax_ok, syntax_errors = _node_check(parser.scripts)
    runtime = _runtime(parser)
    interactions = runtime.get("interactions", [])
    active = [row for row in parser.elements if not row["disabled"]]
    expected_keys = {
        row["key"] for row in active
        if row["tag"] in {"input", "select", "button", "textarea"}
    }
    by_key = {row["key"]: row for row in interactions}
    handler_problems = [
        key for key in sorted(expected_keys)
        if key not in by_key or not by_key[key].get("has_handler") or by_key[key].get("error")
    ]
    element_by_key = {row["key"]: row for row in parser.elements}
    no_effect = [
        key for key in sorted(expected_keys)
        if key in by_key
        and element_by_key[key]["tag"] != "button"
        and by_key[key].get("has_handler")
        and not by_key[key].get("causes_effect")
        and not re.search(r"reset", key, re.I)
    ]
    all_runtime_text = "\n".join(
        json.dumps(snap, ensure_ascii=False)
        for snap in runtime.get("snapshots", [])
    )
    placeholder_hits = sorted(set(
        m.group(0).lower()
        for m in PLACEHOLDER_RE.finditer("\n".join(parser.visible) + "\n" + all_runtime_text)
    ))
    accessibility_ok, accessibility_problems = _accessible(parser)

    checks = {
        "implementation_locator": "PASS",
        "static_syntax": "PASS" if syntax_ok and not parser.script_srcs else "FAIL",
        "handler_and_control_integrity": "PASS" if not handler_problems and not no_effect else "FAIL",
        "identifier_integrity": "PASS" if not duplicates else "FAIL",
        "no_placeholder_or_undefined_output": "PASS" if not placeholder_hits else "FAIL",
        "deterministic_reset": "PASS" if runtime.get("reset", {}).get("present") and runtime.get("reset", {}).get("restores") else "FAIL",
        "runtime_smoke": "PASS" if runtime.get("init_error") is None and not handler_problems and not no_effect else "FAIL",
        "accessibility_baseline": "PASS" if accessibility_ok else "FAIL",
    }
    return {
        "artifact_sha256": hashlib.sha256(text.encode("utf-8")).hexdigest(),
        "checks": checks,
        "details": {
            "duplicate_ids": duplicates,
            "syntax_errors": syntax_errors,
            "external_scripts": parser.script_srcs,
            "handler_problems": handler_problems,
            "no_effect_controls": no_effect,
            "placeholder_hits": placeholder_hits,
            "runtime_init_error": runtime.get("init_error"),
            "reset": runtime.get("reset", {}),
            "accessibility_problems": accessibility_problems,
        },
    }


def governed_activities(repo: Path = REPO):
    for package_path, package in explorer_design_guard.packages(repo):
        for resource in package.get("resources", []):
            atlas = resource.get("extensions", {}).get("topic_atlas", {})
            if atlas.get("activity_kind") == KIND:
                yield package_path, resource, atlas["gcdr_contract"]


def audit(repo: Path = REPO) -> dict:
    rows = []
    blocking = []
    for package_path, resource, contract in governed_activities(repo):
        rid = resource["id"]
        locator = resource.get("locator", "")
        path = repo / locator
        if not locator.startswith("public/") or not path.is_file():
            measured = {
                "artifact_sha256": None,
                "checks": {name: "FAIL" for name in RUNTIME_CHECKS},
                "details": {"locator": locator, "error": "implementation locator missing"},
            }
        else:
            measured = inspect_html(path)

        declared = contract["quality_audit"]["audit_4_runtime_release_integrity"]
        contradictions = []
        for name in sorted(RUNTIME_CHECKS):
            declared_status = declared[name]
            measured_status = measured["checks"][name]
            if declared_status in {"PASS", "FAIL"} and declared_status != measured_status:
                contradictions.append(
                    f"{name}: declared {declared_status}, measured {measured_status}"
                )
        if contract["conformance_status"] == "CERTIFIED":
            for name in sorted(RUNTIME_CHECKS):
                if measured["checks"][name] != "PASS":
                    contradictions.append(
                        f"{name}: CERTIFIED implementation measured {measured['checks'][name]}"
                    )
        if contradictions:
            blocking.append({"resource": rid, "contradictions": contradictions})

        rows.append({
            "file": str(package_path.relative_to(repo)),
            "resource": rid,
            "locator": locator,
            "artifact_sha256": measured["artifact_sha256"],
            "checks": measured["checks"],
            "details": measured["details"],
            "declared": declared,
            "contradictions": contradictions,
        })

    return {
        "auditor": "Shared/tools/gcdr_runtime_audit.py",
        "auditor_version": "1.0.0",
        "scope": "STATIC_PLUS_DOM_LITE_JS_RUNTIME_NOT_VISUAL_BROWSER_PROOF",
        "activities": rows,
        "blocking": blocking,
        "passed": not blocking,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    report = audit()
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if args.enforce and not report["passed"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
