#!/usr/bin/env python3
"""Presentation MathML for a relation written as a plain expression, ready to paste into `relation.mathml`.

The blueprint's typeset rule asks every equation a page shows to carry presentation MathML; with only an expression the page shows plain text
and the deploy reports `AUTHOR_TYPESET`. For an equation in the arithmetic of the explorer's expression language (`+ - * / ^`, `sqrt`, `sin`,
`cos`, ..., numbers and names; write `2*a*b`, never `2ab`) the markup is built from the parsed tree, never from the text. An equation the
language cannot read (words, set-builder notation, implications) is not guessed at: write its MathML by hand, in the subset the pages allow
(math, mrow, mi, mn, mo, msub, msup, mfrac, msqrt, mtext).

    python3 Shared/tools/typeset_relation.py "t = 2*v0y/g"
    python3 Shared/tools/typeset_relation.py "R = v^2*sin(2*theta)/g" --json
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import explorer_expr  # noqa: E402

_LONE_EQUALS = re.compile(r"(?<![<>=!])=(?!=)")      # a single = is the equation's own sign; the language spells equality ==


class NotTypesettable(ValueError):
    """The expression is outside the language this tool reads."""


def mathml(expression: str) -> str:
    """Presentation MathML for `expression`, or NotTypesettable with what the language could not read."""
    text = _LONE_EQUALS.sub("==", expression.strip())
    try:
        return explorer_expr.to_mathml(text)
    except explorer_expr.ExprError as caught:
        raise NotTypesettable(f"{caught} (it reads + - * / ^, sqrt, sin, cos, tan, names and numbers: an equation with words in it is written by hand)") from caught


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("expression")
    parser.add_argument("--json", action="store_true", help="print the markup as a JSON string, the way a record holds it")
    args = parser.parse_args(argv)
    try:
        markup = mathml(args.expression)
    except NotTypesettable as caught:
        print(f"typeset_relation: {caught}", file=sys.stderr)
        return 1
    print(json.dumps(markup, ensure_ascii=False) if args.json else markup)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
