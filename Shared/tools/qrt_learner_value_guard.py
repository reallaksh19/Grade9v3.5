#!/usr/bin/env python3
"""Check that rendered learner pages do not expose low-value authoring vocabulary by default.

The source may retain QRT IDs and misconception evidence for auditability. This guard requires the
shared learner stylesheet to suppress those authoring-only tokens in normal learner presentation,
while still refusing legacy learner-facing crux wording in the HTML itself.
"""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
TABLET_CSS = REPO / "public/css/tablet-12-7.css"


class _LearnerParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, dict[str, str]]] = []
        self.problems: list[str] = []
        self._text_stack: list[list[str]] = []

    def handle_starttag(self, tag: str, attrs) -> None:
        amap = {str(k): str(v or "") for k, v in attrs}
        self.stack.append((tag, amap))
        self._text_stack.append([])

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        open_tag, _attrs = self.stack.pop()
        texts = self._text_stack.pop() if self._text_stack else []
        text = " ".join(t.strip() for t in texts if t.strip()).strip()
        if open_tag in {"span", "p", "h3", "h4"} and text == "The step the hard question turns on":
            self.problems.append("AUTHORING_CRUX_PHRASE_VISIBLE")
        if self._text_stack and text:
            self._text_stack[-1].append(text)

    def handle_data(self, data: str) -> None:
        if self._text_stack:
            self._text_stack[-1].append(data)


def check_shell_policy() -> list[str]:
    try:
        css = TABLET_CSS.read_text(encoding="utf-8")
    except OSError as exc:
        return [f"LEARNER_VALUE_STYLESHEET_MISSING:{exc}"]
    required = {
        ".g9-rung-no": "machine hint ids must be hidden from the learner",
        ".g9-pill-guided": "the Guided implementation badge must be hidden from the learner",
        '.g9-component[data-g9-component="TRAP"]': "pre-attempt wrong-route priming must be hidden; diagnosis remains post-attempt",
    }
    problems: list[str] = []
    for selector, reason in required.items():
        if selector not in css:
            problems.append(f"LEARNER_VALUE_POLICY_MISSING:{selector}:{reason}")
    return problems


def check_html(path: Path) -> list[str]:
    parser = _LearnerParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser.problems


def check(run: dict[str, Any]) -> list[str]:
    problems: list[str] = check_shell_policy()
    for artifact in run.get("rendered_artifacts") or []:
        if not isinstance(artifact, dict):
            continue
        path = REPO / str(artifact.get("path") or "")
        if path.suffix.lower() != ".html" or not path.is_file():
            continue
        role = str(artifact.get("role") or artifact.get("kind") or "")
        if role and role not in {"CORE1A", "CORE2", "LEARNER_HTML", "INTERACTIVE_HTML", "INTERACTIVE_PAGE"}:
            continue
        for detail in check_html(path):
            problems.append(f"LEARNER_VALUE:{artifact.get('id')}:{detail}")
    return problems
