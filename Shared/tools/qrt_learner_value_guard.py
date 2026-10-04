#!/usr/bin/env python3
"""Check that rendered learner pages do not expose low-value authoring vocabulary by default."""
from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]


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
        if amap.get("data-g9-block") == "common_wrong_route":
            protected = any(
                t == "details" and ("data-requires-attempt" in a or "data-g9-stuck" in a or "data-g9-post-attempt" in a)
                for t, a in self.stack[:-1]
            )
            if not protected:
                self.problems.append("COMMON_WRONG_ROUTE_PRIMES_BEFORE_ATTEMPT")

    def handle_endtag(self, tag: str) -> None:
        if not self.stack:
            return
        open_tag, attrs = self.stack.pop()
        texts = self._text_stack.pop() if self._text_stack else []
        text = " ".join(t.strip() for t in texts if t.strip()).strip()
        if open_tag in {"span", "p", "h3", "h4"}:
            if text == "The step the hard question turns on":
                self.problems.append("AUTHORING_CRUX_PHRASE_VISIBLE")
            if "g9-rung-no" in attrs.get("class", "") and text.startswith("H") and text[1:].isdigit():
                self.problems.append(f"MACHINE_HINT_ID_VISIBLE:{text}")
            if "g9-pill-guided" in attrs.get("class", "") and text.lower() == "guided":
                self.problems.append("GUIDED_IMPLEMENTATION_BADGE_VISIBLE")
        if self._text_stack and text:
            self._text_stack[-1].append(text)
        if open_tag != tag:
            # malformed HTML is handled by other gates; do not try to repair the stack here.
            pass

    def handle_data(self, data: str) -> None:
        if self._text_stack:
            self._text_stack[-1].append(data)


def check_html(path: Path) -> list[str]:
    parser = _LearnerParser()
    parser.feed(path.read_text(encoding="utf-8", errors="replace"))
    return parser.problems


def check(run: dict[str, Any]) -> list[str]:
    problems: list[str] = []
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
