#!/usr/bin/env python3
"""Move rendered Core2 concept navigation into the existing post-attempt solution payload.

QRT protected-work policy is transitive: an immediate Core2 -> Core1A link can leak a
question's decisive learner-owned move even when the local hint ladder is safe.  The normal
Core2 renderer already keeps solution payloads inert until the learner commits an attempt.
This deterministic projection reuses that boundary: it removes immediate concept-navigation
components and places their navigation block inside the matching solution template.

The transform is intentionally fail-closed for renderer output it does not recognise.  It
changes no academic text and no link target; it changes only when the existing link becomes
reachable.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ARTICLE_RE = re.compile(
    r'(?P<article><article\b[^>]*\bid="(?P<qid>[^"]+)"[^>]*data-g9-role="CORE2"[^>]*>.*?</article>)',
    re.S,
)
NAV_RE = re.compile(
    r'<div class="g9-component g9-c-link-list" data-g9-component="CONCEPT_NAV"[^>]*>'
    r'(?P<block><div class="g9-block" data-g9-block="concept_navigation">.*?</ul></div>)'
    r'</div>',
    re.S,
)


class NavigationProtectionError(ValueError):
    pass


def protect_html(text: str) -> tuple[str, int]:
    changed = 0

    def transform_article(match: re.Match[str]) -> str:
        nonlocal changed
        article = match.group("article")
        qid = match.group("qid")
        navs = list(NAV_RE.finditer(article))
        if not navs:
            return article
        if len(navs) != 1:
            raise NavigationProtectionError(f"{qid}: expected one Core2 concept navigation block, found {len(navs)}")
        nav = navs[0]
        block = nav.group("block")
        article = article[:nav.start()] + article[nav.end():]
        marker = f'<template data-g9-payload="CORE2-{qid}-solution">'
        if article.count(marker) != 1:
            raise NavigationProtectionError(
                f"{qid}: concept navigation exists but matching attempt-gated solution payload was not found exactly once"
            )
        protected = (
            '<div class="g9-post-attempt-concept-nav" data-g9-post-attempt-concept-nav>'
            + block
            + '</div>'
        )
        article = article.replace(marker, marker + protected, 1)
        changed += 1
        return article

    out = ARTICLE_RE.sub(transform_article, text)
    return out, changed


def check_html(text: str) -> int:
    links = list(re.finditer(r'<a\b[^>]*data-g9-concept-link\b', text))
    if not links:
        return 0
    protected_ranges: list[tuple[int, int]] = []
    for m in re.finditer(
        r'<template data-g9-payload="CORE2-[^"]+-solution">.*?</template>',
        text,
        re.S,
    ):
        protected_ranges.append((m.start(), m.end()))
    exposed = [m.start() for m in links if not any(start <= m.start() < end for start, end in protected_ranges)]
    if exposed:
        raise NavigationProtectionError(
            f"{len(exposed)} Core2 concept link(s) remain reachable outside attempt-gated solution payloads"
        )
    return len(links)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    text = args.html.read_text(encoding="utf-8")
    if args.write:
        text, changed = protect_html(text)
        args.html.write_text(text, encoding="utf-8")
        print(f"post-attempt concept navigation: moved {changed} question block(s)")
    links = check_html(text)
    print(f"post-attempt concept navigation: PASS ({links} protected link(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
