#!/usr/bin/env python3
"""Hold a learner page that did not come through the renderer to the shell's own policies.

`render_core.py` realizes the blueprint, so a page it makes meets the shell by construction. A page that does not come through it
(a snapshot, a suite, a page written by hand or scraped from another tool) meets none of the shell's rules unless something reads it
against them. Pull request 375 was that: 14 pages with a remote script in a shell that forbids one, text under the 14 px floor, maths
shown as raw TeX with control characters in it, and 67 dead links, all of it passing a gate the pull request had written for itself.

The registry's `shell.standalone_policy` names the rules; this tool executes them over the page's own bytes, with no browser, and the
numbers (the text floor, the zoom limit) come from the registry. What needs a rendered page (overflow, touch targets, the size an SVG label
ends up at, contrast) is the browser audit the same policy names.

    python3 Shared/tools/standalone_conformance.py PAGE.html [PAGE.html ...] [--json]
    python3 Shared/tools/standalone_conformance.py --governed [--enforce]          # every page under the governed roots, against the ledger
    python3 Shared/tools/standalone_conformance.py --governed --write-ledger       # regenerate the ledger (never edit it by hand)

The ledger (`Shared/web/standalone-ledger.v1.json`) is a ratchet: a page may have no more findings of a rule than the ledger records, and
a page the ledger does not list has none. It records what was already there when the rule arrived, so the rule can be switched on without
a flag day; it can only be tightened.
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

LEDGER = REPO / "Shared" / "web" / "standalone-ledger.v1.json"
RULES = ("REMOTE_RUNTIME", "VIEWPORT_ZOOM", "FONT_FLOOR", "LINKS_RESOLVE", "LINKS_LEAVE_ROOT", "MATH_CONTROL_CHARS",
         "MATH_UNRENDERED", "STORAGE_GUARDED", "VENDOR_CONFIG_DANGLING", "UNIQUE_IDS")

CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")
RAW_TEX = re.compile(r"\\\(|\\\[|\$\$|\$[^$\n]*\\[A-Za-z]+[^$\n]*\$")
MATH_CALL = re.compile(r"renderMathInElement|katex\s*\.\s*render|renderToString|MathJax|\.typeset")
FONT_SIZE = re.compile(r"font-size\s*:\s*([0-9]*\.?[0-9]+)\s*(px|rem|em|pt)\b", re.I)
TAILWIND_SMALL = re.compile(r"(?<![\w-])text-xs(?![\w-])|(?<![\w-])text-\[\s*([0-9]*\.?[0-9]+)px\s*\]")
REMOTE_IN_CODE = re.compile(r"""['"`](?:https?:)?//[^'"`\s]+?\.(?:js|mjs|css|woff2?|ttf|otf)(?:\?[^'"`\s]*)?['"`]""", re.I)
CSS_REMOTE = re.compile(r"(?:@import\s+(?:url\()?\s*|url\(\s*)['\"]?((?:https?:)?//[^'\")\s]+)", re.I)
STORAGE = re.compile(r"\b(?:localStorage|sessionStorage)\b")
# a link rel that is a statement about the page, not something the page needs in order to run
PASSIVE_RELS = {"canonical", "alternate", "author", "license", "help", "next", "prev", "search"}
LINK_ATTRS = {"a": ("href",), "link": ("href",), "script": ("src",), "img": ("src",), "iframe": ("src",), "source": ("src",),
              "video": ("src", "poster"), "audio": ("src",), "embed": ("src",), "object": ("data",)}


def policy() -> dict:
    from Shared.tools import web_blueprint_contract  # noqa: PLC0415  (the registry owns the rule)
    return web_blueprint_contract.load_registry()["shell"]


class _Page(HTMLParser):
    """What a page says about itself: its references, its ids, its visible text, its scripts and its styles."""

    def __init__(self, text: str):
        super().__init__(convert_charrefs=True)
        self.lines = text.count("\n") + 1
        self.refs: list[tuple[str, str, str, int]] = []   # (tag, attr, value, line)
        self.rels: dict[int, str] = {}
        self.ids: list[tuple[str, int]] = []
        self.viewport: str | None = None
        self.text: list[tuple[str, int]] = []
        self.scripts: list[tuple[dict, str, int]] = []    # (attrs, body, line)
        self.styles: list[tuple[str, int]] = []
        self.inline_styles: list[tuple[str, int]] = []
        self.classes: list[tuple[str, int]] = []
        self._open: list[str] = []
        self._buffer: list[str] = []
        self._attrs: dict = {}
        self._line = 1
        self.feed(text)
        self.close()

    def handle_starttag(self, tag, attrs):
        attrs = {k: (v or "") for k, v in attrs}
        line = self.getpos()[0]
        if tag in ("script", "style"):
            self._open.append(tag)
            self._buffer, self._attrs, self._line = [], attrs, line
        if "id" in attrs and attrs["id"]:
            self.ids.append((attrs["id"], line))
        if attrs.get("name") and tag == "a":
            self.ids.append((attrs["name"], line))
        if attrs.get("style"):
            self.inline_styles.append((attrs["style"], line))
        if attrs.get("class"):
            self.classes.append((attrs["class"], line))
        if tag == "meta" and attrs.get("name", "").lower() == "viewport":
            self.viewport = attrs.get("content", "")
        for attr in LINK_ATTRS.get(tag, ()):
            if attrs.get(attr):
                if tag == "link":
                    rel = {r.lower() for r in attrs.get("rel", "").split()}
                    if rel and rel <= PASSIVE_RELS:
                        continue
                self.refs.append((tag, attr, attrs[attr].strip(), line))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)

    def handle_endtag(self, tag):
        if self._open and self._open[-1] == tag:
            self._open.pop()
            body = "".join(self._buffer)
            (self.scripts if tag == "script" else self.styles).append(
                (self._attrs, body, self._line) if tag == "script" else (body, self._line))

    def handle_data(self, data):
        if self._open:
            self._buffer.append(data)
        elif data.strip():
            self.text.append((data, self.getpos()[0]))


def _remote(url: str) -> bool:
    return url.lower().startswith(("http://", "https://", "//"))


def _blank_strings_and_comments(code: str) -> str:
    """The code with every string and comment turned to spaces (newlines kept), so that a name inside a string is not a use."""
    out, i, n = [], 0, len(code)
    while i < n:
        c = code[i]
        if c in "\"'`":
            quote, j = c, i + 1
            while j < n and code[j] != quote:
                j += 2 if code[j] == "\\" else 1
            out.append(c + "".join(ch if ch == "\n" else " " for ch in code[i + 1:j]) + (quote if j < n else ""))
            i = j + 1
        elif code.startswith("//", i):
            j = code.find("\n", i)
            j = n if j < 0 else j
            out.append(" " * (j - i))
            i = j
        elif code.startswith("/*", i):
            j = code.find("*/", i + 2)
            j = n if j < 0 else j + 2
            out.append("".join(ch if ch == "\n" else " " for ch in code[i:j]))
            i = j
        else:
            out.append(c)
            i += 1
    return "".join(out)


def _unguarded_storage(code: str) -> list[int]:
    """Offsets where storage is read outside a try block: with storage blocked the read itself throws, and one throw ends the script."""
    clean = _blank_strings_and_comments(code)
    uses = {m.start() for m in STORAGE.finditer(clean)}
    stack: list[bool] = []
    found = []
    for i, c in enumerate(clean):
        if i in uses and not any(stack):
            found.append(i)
        if c == "{":
            stack.append(re.search(r"\btry\s*$", clean[max(0, i - 12):i]) is not None)
        elif c == "}" and stack:
            stack.pop()
    return found


def _fragment_ids(path: Path, cache: dict) -> set[str]:
    if path not in cache:
        try:
            cache[path] = {i for i, _ in _Page(path.read_text(encoding="utf-8", errors="replace")).ids}
        except OSError:
            cache[path] = set()
    return cache[path]


def check_page(path: Path, *, root: Path | None = None, shell: dict | None = None, _ids: dict | None = None) -> list[dict]:
    """Every finding of the standalone policy on one page: {rule, line, detail, severity}."""
    shell = shell or policy()
    rules = {r["id"]: r for r in shell["standalone_policy"]["rules"]}
    floor = shell["typography_policy"]["minimum_learner_text_css_px"]
    path = path.resolve()
    text = path.read_text(encoding="utf-8", errors="replace")
    page = _Page(text)
    out: list[dict] = []
    cache = _ids if _ids is not None else {}

    def add(rule: str, line: int, detail: str):
        if rule in rules:
            out.append({"rule": rule, "line": line, "detail": detail, "severity": rules[rule]["severity"]})

    # REMOTE_RUNTIME: the page needs the network to run (an anchor to a source is a citation, not a dependency)
    for tag, attr, value, line in page.refs:
        if tag != "a" and _remote(value):
            add("REMOTE_RUNTIME", line, f"<{tag} {attr}> loads {value}")
    for body, line in page.styles:
        for m in CSS_REMOTE.finditer(body):
            add("REMOTE_RUNTIME", line + body[:m.start()].count("\n"), f"a style loads {m.group(1)}")
    for attrs, body, line in page.scripts:
        for m in REMOTE_IN_CODE.finditer(body):
            add("REMOTE_RUNTIME", line + body[:m.start()].count("\n"), f"a script names {m.group(0).strip(chr(34) + chr(39) + chr(96))}")

    # VIEWPORT_ZOOM: the page declares a viewport and never turns zoom off
    if page.viewport is None:
        add("VIEWPORT_ZOOM", 1, "no viewport meta, so a tablet lays the page out as a desktop")
    else:
        view = {k.strip().lower(): v.strip().lower() for k, _, v in (p.partition("=") for p in page.viewport.split(",")) if k.strip()}
        if view.get("user-scalable") in ("no", "0"):
            add("VIEWPORT_ZOOM", 1, "user-scalable=no: the learner cannot zoom")
        try:
            if "maximum-scale" in view and float(view["maximum-scale"]) < shell["standalone_policy"]["zoom_max_scale_min"]:
                add("VIEWPORT_ZOOM", 1, f"maximum-scale={view['maximum-scale']} limits zoom below {shell['standalone_policy']['zoom_max_scale_min']}")
        except ValueError:
            add("VIEWPORT_ZOOM", 1, f"maximum-scale={view['maximum-scale']!r} is not a number")

    # FONT_FLOOR: a declared size under the learner text floor (a rendered size, which scaling can change, is the browser audit's)
    for body, line in [(b, ln) for b, ln in page.styles] + [(s, ln) for s, ln in page.inline_styles]:
        for m in FONT_SIZE.finditer(body):
            value, unit = float(m.group(1)), m.group(2).lower()
            if value == 0:
                continue
            px = value * {"px": 1, "rem": 16, "em": 16, "pt": 4 / 3}[unit]
            if px < floor:
                add("FONT_FLOOR", line + body[:m.start()].count("\n"), f"font-size {m.group(1)}{unit} is {px:g} px, under the {floor} px floor")
    for value, line in page.classes:
        for m in TAILWIND_SMALL.finditer(value):
            px = float(m.group(1)) if m.group(1) else 12.0
            if px < floor:
                add("FONT_FLOOR", line, f"class {m.group(0)!r} is {px:g} px, under the {floor} px floor")

    # LINKS_RESOLVE / LINKS_LEAVE_ROOT: every relative reference lands on a file, and every fragment on an id
    for tag, attr, value, line in page.refs:
        parts = urlsplit(value)
        if value == "#" or value.startswith("//") or parts.scheme:   # a bare #, a remote reference (judged above), mailto:, javascript:, data:
            continue
        target = path if not parts.path else (path.parent / unquote(parts.path)).resolve()
        if target.is_dir():
            target = target / "index.html"
        if not target.exists():
            add("LINKS_RESOLVE", line, f"<{tag} {attr}=\"{value}\"> points at {parts.path or '(this page)'}, which does not exist")
            continue
        if parts.fragment and target.suffix.lower() in (".html", ".htm") and parts.fragment not in _fragment_ids(target, cache):
            add("LINKS_RESOLVE", line, f"<{tag} {attr}=\"{value}\"> points at #{parts.fragment}, which {target.name} does not hold")
        if root is not None and tag != "link" and target.suffix.lower() in (".html", ".htm", ".js", ".css", ".json", ".woff", ".woff2"):
            try:
                target.relative_to(root.resolve())
            except ValueError:
                add("LINKS_LEAVE_ROOT", line, f"<{tag} {attr}=\"{value}\"> leaves {root.name}/, so the page is not whole where it is shipped alone")

    # MATH_CONTROL_CHARS: an escape that was read as a control character (\v for \vec, \f for \frac) is gone from the maths for good
    for match in CONTROL.finditer(text):
        add("MATH_CONTROL_CHARS", text.count("\n", 0, match.start()) + 1, f"control character U+{ord(match.group()):04X} in the source")
    # MATH_UNRENDERED: TeX in the visible text, and nothing on the page that renders it
    scripts_text = "\n".join(body for _, body, _ in page.scripts)
    if not MATH_CALL.search(scripts_text):
        for data, line in page.text:
            if RAW_TEX.search(data):
                add("MATH_UNRENDERED", line, f"raw TeX in the text ({RAW_TEX.search(data).group()!r}) and no script on the page renders maths")

    # STORAGE_GUARDED: storage read outside a try block throws when storage is blocked, and ends the script that read it
    for attrs, body, line in page.scripts:
        if attrs.get("src"):
            continue
        for offset in _unguarded_storage(body):
            add("STORAGE_GUARDED", line + body[:offset].count("\n"), "storage is read outside a try block")

    # VENDOR_CONFIG_DANGLING: configuration for a vendor script that the page does not load
    loaded = any("tailwind" in attrs.get("src", "").lower() for attrs, _, _ in page.scripts)
    for attrs, body, line in page.scripts:
        if not attrs.get("src") and re.search(r"\btailwind\.config\b", _blank_strings_and_comments(body)) \
                and not loaded and not re.search(r"\b(?:var|let|const|window\.)\s*tailwind\b", body):
            add("VENDOR_CONFIG_DANGLING", line, "tailwind.config is set and tailwind is never loaded: it throws on every load")

    # UNIQUE_IDS
    for name, count in Counter(i for i, _ in page.ids).items():
        if count > 1:
            add("UNIQUE_IDS", next(line for i, line in page.ids if i == name), f"id {name!r} appears {count} times")
    return sorted(out, key=lambda f: (f["line"], f["rule"]))


def counts(findings: list[dict]) -> dict[str, int]:
    """Findings that count for the ratchet: an advisory is said, not held."""
    return dict(sorted(Counter(f["rule"] for f in findings if f["severity"] == "BLOCK").items()))


def governed_files(shell: dict | None = None) -> list[Path]:
    """Every tracked page under the governed roots."""
    shell = shell or policy()
    roots = shell["standalone_policy"]["governed_roots"]
    listed = subprocess.run(["git", "ls-files", "--", *[f"{r}/**/*.html" for r in roots], *[f"{r}/*.html" for r in roots]],
                            cwd=REPO, capture_output=True, text=True, check=True).stdout.split()
    return sorted({REPO / p for p in listed})


def load_ledger() -> dict:
    return json.loads(LEDGER.read_text(encoding="utf-8")) if LEDGER.exists() else {"files": {}}


def ratchet(findings_by_file: dict[str, dict[str, int]], ledger: dict) -> list[str]:
    """What is worse than the ledger allows: a rule with more findings on a page than were recorded, or a new page with any."""
    held = ledger.get("files", {})
    problems = []
    for name, found in sorted(findings_by_file.items()):
        for rule, number in sorted(found.items()):
            allowed = held.get(name, {}).get(rule, 0)
            if number > allowed:
                problems.append(f"{name}: {rule} {number} (the ledger allows {allowed})")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("pages", nargs="*")
    parser.add_argument("--governed", action="store_true", help="every tracked page under the governed roots")
    parser.add_argument("--enforce", action="store_true", help="exit 1 when a page is worse than the ledger allows")
    parser.add_argument("--write-ledger", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    shell = policy()
    if args.governed:
        files = governed_files(shell)
    else:
        files = [Path(p) for p in args.pages]
    if not files:
        parser.error("name a page, or use --governed")
    roots = {r: REPO / r for r in shell["standalone_policy"]["governed_roots"]}
    ids: dict = {}
    result: dict[str, list[dict]] = {}
    for f in files:
        root = next((p for p in roots.values() if p in f.resolve().parents), None)
        key = str(f.resolve().relative_to(REPO)) if REPO in f.resolve().parents else str(f)
        result[key] = check_page(f, root=root, shell=shell, _ids=ids)
    held = {k: counts(v) for k, v in result.items() if counts(v)}
    if args.write_ledger:
        LEDGER.write_text(json.dumps({"schema_version": 1, "policy": f"{shell['id']}@{shell['version']}",
                                      "note": "Generated by standalone_conformance.py --governed --write-ledger. Findings that were already on a page when "
                                              "the rule arrived. A page may have no more than this; it can only be tightened.",
                                      "files": held}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"ledger written: {len(held)} page(s) with findings of {len(result)}")
        return 0
    if args.json:
        print(json.dumps(result, indent=2, ensure_ascii=False))
    else:
        for name, findings in result.items():
            total = Counter(f["rule"] for f in findings)
            print(f"{name}: " + (", ".join(f"{r} x{n}" for r, n in sorted(total.items())) if total else "conforms"))
            if len(files) == 1:
                for f in findings:
                    print(f"  {f['rule']:<22} line {f['line']:>5}  {f['detail']}")
    if args.enforce:
        problems = ratchet(held, load_ledger())
        for line in problems:
            print("WORSE THAN THE LEDGER:", line, file=sys.stderr)
        return 1 if problems else 0
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
