#!/usr/bin/env python3
"""The small expression language an explorer's numbers are written in, evaluated here to check them and in the page to show them.

An explorer (Shared/tools/explorer_build.py) states every number it shows as an expression over its parameters: the length of an
arrow, a value in a readout, the answer to a transfer question. The page evaluates the expressions in the learner's browser
(Shared/web/explorer-runtime.js); this module evaluates the same expressions when the spec is checked, so a claim the page makes
is a claim somebody computed. The two evaluators implement one grammar and are compared on a corpus by the tests.

    expression  := or
    or          := and ("or" and)*
    and         := not ("and" not)*
    not         := "not" not | comparison
    comparison  := sum (("<" | "<=" | ">" | ">=" | "==" | "!=") sum)?
    sum         := product (("+" | "-") product)*
    product     := unary (("*" | "/") unary)*
    unary       := ("-" | "+") unary | power
    power       := primary ("^" unary)?             (right associative; -a^2 is -(a^2))
    primary     := number | name | name "(" [expression ("," expression)*] ")" | "(" expression ")"

Names are letters, digits and underscores, starting with a letter; `pi` and `e` are constants. There is no implicit multiplication
(write 2*a*b). A comparison is 1 when it holds and 0 when it does not, `==` allows a relative tolerance of 1e-9, and `and`, `or`
and `not` read any non-zero number as true. A result that is not a finite number (a division by zero, a square root of a negative
number) is NaN and stays NaN; `if(c, a, b)` evaluates only the branch it takes, so a guard can avoid it.
Angles in sin, cos, tan and atan2 are radians; sind, cosd, tand, asind, acosd, atand and atan2d work in degrees.

Five forms read the explorer's model instead of one state (they need a resolver, see `evaluate`), and are allowed only where a claim
about the model is made, never in a quantity or in the geometry of a scene:

    at(Q, p, v, ...)     the quantity or parameter Q with parameter p set to v (and any further pairs), the rest as they are now
    maxover(Q, p)        the largest value of Q as parameter p takes every value of its range, the rest as they are now
    minover(Q, p)        the smallest
    argmax(Q, p)         the first value of p at which Q is largest (values within the tolerance of the largest count as equal)
    argmin(Q, p)         the first value of p at which Q is smallest
"""
from __future__ import annotations

import math
import re
from typing import Any

NaN = float("nan")
TOLERANCE = 1e-9
CONSTANTS = {"pi": math.pi, "e": math.e}
KEYWORDS = {"and", "or", "not"}
TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([A-Za-z][A-Za-z0-9_]*)|(<=|>=|==|!=|[-+*/^(),<>]))")


class ExprError(ValueError):
    """The text is not an expression of this language, or names something that does not exist."""


# ------------------------------------------------------------------ the functions

AGGREGATES = {"at", "maxover", "minover", "argmax", "argmin"}      # name -> read the model; their arguments are names, not values

def _finite(value: float) -> float:
    return value if math.isfinite(value) else NaN


def _guard(fn):
    def run(*args: float) -> float:
        try:
            return _finite(float(fn(*args)))
        except (ValueError, ZeroDivisionError, OverflowError):
            return NaN
    return run


def _round(x: float, digits: float = 0.0) -> float:
    if not math.isfinite(x):
        return NaN
    scale = 10 ** int(digits)
    return math.floor(x * scale + 0.5) / scale        # half up, as the page does


FUNCTIONS: dict[str, tuple[int, Any]] = {          # name -> (arity, function); arity -1: any number of arguments (at least one)
    "sqrt": (1, _guard(math.sqrt)), "abs": (1, _guard(abs)), "exp": (1, _guard(math.exp)),
    "ln": (1, _guard(math.log)), "log10": (1, _guard(math.log10)),
    "sin": (1, _guard(math.sin)), "cos": (1, _guard(math.cos)), "tan": (1, _guard(math.tan)),
    "asin": (1, _guard(math.asin)), "acos": (1, _guard(math.acos)), "atan": (1, _guard(math.atan)),
    "atan2": (2, _guard(math.atan2)),
    "sind": (1, _guard(lambda x: math.sin(math.radians(x)))), "cosd": (1, _guard(lambda x: math.cos(math.radians(x)))),
    "tand": (1, _guard(lambda x: math.tan(math.radians(x)))),
    "asind": (1, _guard(lambda x: math.degrees(math.asin(x)))), "acosd": (1, _guard(lambda x: math.degrees(math.acos(x)))),
    "atand": (1, _guard(lambda x: math.degrees(math.atan(x)))), "atan2d": (2, _guard(lambda y, x: math.degrees(math.atan2(y, x)))),
    "floor": (1, _guard(math.floor)), "ceil": (1, _guard(math.ceil)), "round": (-2, _round),
    "hypot": (2, _guard(math.hypot)), "pow": (2, _guard(math.pow)),
    "sign": (1, _guard(lambda x: (x > 0) - (x < 0))), "clamp": (3, _guard(lambda x, lo, hi: min(max(x, lo), hi))),
    "min": (-1, lambda *xs: NaN if any(math.isnan(x) for x in xs) else min(xs)),
    "max": (-1, lambda *xs: NaN if any(math.isnan(x) for x in xs) else max(xs)),
    "deg": (1, _guard(math.degrees)), "rad": (1, _guard(math.radians)),
    "if": (3, None),                                                   # lazy: handled by the evaluator
}


# ------------------------------------------------------------------ parsing

# What an author most likely meant by a character the language does not have.
_ADVICE = {
    "=": "a single = is not a comparison: write == (and a quantity's own expression has no name = before it)",
    "×": "write multiplication as *", "·": "write multiplication as *", "⋅": "write multiplication as *", "÷": "write division as /",
    "√": "write sqrt(x)", "²": "write powers with ^, as x^2", "³": "write powers with ^, as x^3", "π": "write pi",
    "°": "angles are plain numbers: use sind, cosd, tand (degrees) instead of a degree sign",
    "%": "there is no % operator: write /100", "&": "write and", "|": "write or, or abs(x) for a size", "!": "write not (or != for not equal)",
    "[": "use ( ) for brackets", "]": "use ( ) for brackets", "{": "use ( ) for brackets", "}": "use ( ) for brackets",
    "$": "write the expression as plain text, with no $", "\\": "write the expression as plain text, not LaTeX", "_": "a name may contain an underscore only after its first letter",
}


def _advice(text: str, where: int) -> str:
    char = text[where]
    if char in "θαβγδφωμλρστ" or "Α" <= char <= "ω":
        return " (write Greek letters as plain names: theta, alpha, beta)"
    if char == "*" or (where and text[where - 1] == "*" and char == "*"):
        return " (write powers with ^)"
    return f" ({_ADVICE[char]})" if char in _ADVICE else ""

Node = tuple


def _tokens(text: str) -> list[tuple[str, str]]:
    out, position = [], 0
    text = text.rstrip()
    while position < len(text):
        found = TOKEN.match(text, position)
        if not found or found.end() == position:
            where = position + len(text[position:]) - len(text[position:].lstrip())
            raise ExprError(f"unexpected character {text[where]!r} at position {where + 1}" + _advice(text, where))
        number, name, symbol = found.groups()
        out.append(("num", number) if number is not None else ("name", name) if name is not None else ("sym", symbol))
        position = found.end()
    return out


class _Parser:
    def __init__(self, text: str):
        self.tokens = _tokens(text)
        self.at = 0

    def peek(self) -> tuple[str, str] | None:
        return self.tokens[self.at] if self.at < len(self.tokens) else None

    def take(self) -> tuple[str, str]:
        token = self.peek()
        if token is None:
            raise ExprError("the expression ends where more is expected")
        self.at += 1
        return token

    def accept(self, *symbols: str) -> str | None:
        token = self.peek()
        if token and token[1] in symbols and (token[0] == "sym" or token[1] in KEYWORDS):
            self.at += 1
            return token[1]
        return None

    def expect(self, symbol: str) -> None:
        if not self.accept(symbol):
            token = self.peek()
            raise ExprError(f"expected {symbol!r}" + (f" but found {token[1]!r}" if token else " at the end"))

    def parse(self) -> Node:
        if not self.tokens:
            raise ExprError("the expression is empty")
        node = self.or_()
        if self.peek() is not None:
            raise ExprError(f"unexpected {self.peek()[1]!r}" + self._hint())
        return node

    def unexpected(self, symbol: str) -> ExprError:
        before = self.tokens[self.at - 2] if self.at >= 2 else None
        if symbol == "*" and before and before[1] == "*":
            return ExprError("unexpected '*' (write powers with ^, as x^2, not **)")
        return ExprError(f"unexpected {symbol!r}")

    def _hint(self) -> str:
        token, before = self.peek(), self.tokens[self.at - 1] if self.at else None
        if token and before and token[0] in {"num", "name"} and before[0] in {"num", "name"} or (
                token and before and token[1] == "(" and before[0] in {"num"}):
            return " (there is no implicit multiplication: write 2*a*b, not 2ab)"
        return ""

    def or_(self) -> Node:
        node = self.and_()
        while self.accept("or"):
            node = ("or", node, self.and_())
        return node

    def and_(self) -> Node:
        node = self.not_()
        while self.accept("and"):
            node = ("and", node, self.not_())
        return node

    def not_(self) -> Node:
        if self.accept("not"):
            return ("not", self.not_())
        return self.comparison()

    def comparison(self) -> Node:
        left = self.sum_()
        op = self.accept("<=", ">=", "==", "!=", "<", ">")
        return ("cmp", op, left, self.sum_()) if op else left

    def sum_(self) -> Node:
        node = self.product()
        while True:
            op = self.accept("+", "-")
            if not op:
                return node
            node = ("bin", op, node, self.product())

    def product(self) -> Node:
        node = self.unary()
        while True:
            op = self.accept("*", "/")
            if not op:
                return node
            node = ("bin", op, node, self.unary())

    def unary(self) -> Node:
        op = self.accept("-", "+")
        if op:
            inner = self.unary()
            return ("neg", inner) if op == "-" else inner
        return self.power()

    def power(self) -> Node:
        base = self.primary()
        if self.accept("^"):
            return ("bin", "^", base, self.unary())
        return base

    def primary(self) -> Node:
        kind, value = self.take()
        if kind == "num":
            return ("num", float(value))
        if kind == "name":
            if value in KEYWORDS:
                raise ExprError(f"{value!r} is a keyword, not a value")
            if self.accept("("):
                args: list[Node] = []
                if not self.accept(")"):
                    args.append(self.or_())
                    while self.accept(","):
                        args.append(self.or_())
                    self.expect(")")
                return ("call", value, args)
            return ("var", value)
        if value == "(":
            node = self.or_()
            self.expect(")")
            return node
        raise self.unexpected(value)


def parse(text: str) -> Node:
    """The tree of an expression, or ExprError naming what is wrong with it."""
    if not isinstance(text, str):
        raise ExprError("an expression is a string")
    return _Parser(text).parse()


# ------------------------------------------------------------------ analysis

def names(node: Node) -> tuple[set[str], set[str]]:
    """(variables the expression reads, functions it calls)."""
    variables: set[str] = set()
    functions: set[str] = set()

    def walk(n: Node) -> None:
        kind = n[0]
        if kind == "var":
            variables.add(n[1])
        elif kind == "call":
            functions.add(n[1])
            for arg in n[2]:
                walk(arg)
        elif kind in {"neg", "not"}:
            walk(n[1])
        elif kind in {"bin", "cmp"}:
            walk(n[2])
            walk(n[3])
        elif kind in {"and", "or"}:
            walk(n[1])
            walk(n[2])

    walk(node)
    return variables - set(CONSTANTS), functions


def check(text: str, known: set[str] | frozenset[str] = frozenset(), *, parameters: set[str] | frozenset[str] | None = None,
          model_forms: bool = True) -> list[str]:
    """What is wrong with an expression's text: syntax, a function that does not exist or has the wrong number of arguments,
    a name that is not among `known`. Empty means it can be evaluated.

    `parameters` (when given) are the names that may be set or swept by at(), maxover() and the like; `model_forms=False` says
    the place the expression sits in may not read the model at all (a quantity, the geometry of a scene)."""
    try:
        tree = parse(text)
    except ExprError as caught:
        return [str(caught)]
    problems: list[str] = []
    variables, functions = names(tree)
    for function in sorted(functions):
        if function not in FUNCTIONS and function not in AGGREGATES:
            problems.append(f"{function}() is not a function of this language")
        elif function in AGGREGATES and not model_forms:
            problems.append(f"{function}() reads the whole model, so it can be used in a claim, a goal or an answer, "
                            "not in a quantity or in the geometry of a scene")
    for call in _calls(tree):
        if call[1] in AGGREGATES:
            problems.extend(_aggregate_problems(call, parameters))
            continue
        arity = FUNCTIONS.get(call[1], (None,))[0]
        count = len(call[2])
        if arity is not None and ((arity >= 0 and count != arity) or (arity == -1 and count < 1) or (arity == -2 and count not in (1, 2))):
            problems.append(f"{call[1]}() takes {'at least one' if arity == -1 else '1 or 2' if arity == -2 else arity} argument(s), got {count}")
    for variable in sorted(variables - set(known)):
        problems.append(f"{variable!r} is not a parameter or an earlier quantity")
    return problems


def _aggregate_problems(call: Node, parameters) -> list[str]:
    name, args = call[1], call[2]
    if name == "at":
        if len(args) < 3 or len(args) % 2 == 0:
            return [f"at() takes a quantity, then pairs of a parameter and a value: at(R, theta, 90); got {len(args)} argument(s)"]
        named = [args[0]] + args[1::2]
    else:
        if len(args) != 2:
            return [f"{name}() takes a quantity and a parameter: {name}(R, theta); got {len(args)} argument(s)"]
        named = args
    problems = [f"{name}() argument {i + 1} must be a name, not an expression" for i, node in enumerate(named) if node[0] != "var"]
    if not problems and parameters is not None:
        problems += [f"{node[1]!r} is not a parameter, so {name}() cannot set or sweep it" for node in named[1:] if node[1] not in parameters]
    return problems


def _calls(node: Node) -> list[Node]:
    found: list[Node] = []

    def walk(n: Node) -> None:
        kind = n[0]
        if kind == "call":
            found.append(n)
            for arg in n[2]:
                walk(arg)
        elif kind in {"neg", "not"}:
            walk(n[1])
        elif kind in {"bin", "cmp"}:
            walk(n[2])
            walk(n[3])
        elif kind in {"and", "or"}:
            walk(n[1])
            walk(n[2])

    walk(node)
    return found


# ------------------------------------------------------------------ evaluation

def _equal(x: float, y: float) -> bool:
    return abs(x - y) <= TOLERANCE * max(1.0, abs(x), abs(y))


def evaluate(node: Node | str, env: dict[str, float] | None = None, resolver: Any = None) -> float:
    """The value of an expression for the given variables; NaN where it is not a finite number.

    `resolver` answers the model forms: resolver.at(name, overrides) is the value of `name` with those parameters set, and
    resolver.sweep(name, parameter) is [(value of the parameter, value of `name`), ...] over the parameter's whole range."""
    if isinstance(node, str):
        node = parse(node)
    env = env or {}

    def go(n: Node) -> float:
        kind = n[0]
        if kind == "num":
            return n[1]
        if kind == "var":
            if n[1] in CONSTANTS:
                return CONSTANTS[n[1]]
            if n[1] not in env:
                raise ExprError(f"{n[1]!r} has no value")
            return float(env[n[1]])
        if kind == "neg":
            return -go(n[1])
        if kind == "not":
            value = go(n[1])
            return NaN if math.isnan(value) else 0.0 if value != 0 else 1.0
        if kind == "and":
            left = go(n[1])
            if math.isnan(left):
                return NaN
            if left == 0:
                return 0.0
            right = go(n[2])
            return NaN if math.isnan(right) else 1.0 if right != 0 else 0.0
        if kind == "or":
            left = go(n[1])
            if math.isnan(left):
                return NaN
            if left != 0:
                return 1.0
            right = go(n[2])
            return NaN if math.isnan(right) else 1.0 if right != 0 else 0.0
        if kind == "cmp":
            left, right = go(n[2]), go(n[3])
            if math.isnan(left) or math.isnan(right):
                return NaN
            op = n[1]
            return float({"<": left < right, "<=": left <= right or _equal(left, right), ">": left > right,
                          ">=": left >= right or _equal(left, right), "==": _equal(left, right), "!=": not _equal(left, right)}[op])
        if kind == "bin":
            op, left, right = n[1], go(n[2]), go(n[3])
            if math.isnan(left) or math.isnan(right):
                return NaN
            try:
                if op == "+":
                    return _finite(left + right)
                if op == "-":
                    return _finite(left - right)
                if op == "*":
                    return _finite(left * right)
                if op == "/":
                    return _finite(left / right)
                return _finite(math.pow(left, right))
            except (ZeroDivisionError, ValueError, OverflowError):
                return NaN
        if kind == "call":
            name, args = n[1], n[2]
            if name in AGGREGATES:
                return aggregate(name, args)
            if name not in FUNCTIONS:
                raise ExprError(f"{name}() is not a function of this language")
            if name == "if":
                condition = go(args[0])
                if math.isnan(condition):
                    return NaN
                return go(args[1]) if condition != 0 else go(args[2])
            values = [go(arg) for arg in args]
            if any(math.isnan(value) for value in values):
                return NaN
            return float(FUNCTIONS[name][1](*values))
        raise ExprError(f"unknown node {kind}")

    def aggregate(name: str, args: list[Node]) -> float:
        if resolver is None:
            raise ExprError(f"{name}() reads the model, and there is no model here")
        problems = _aggregate_problems(("call", name, args), None)
        if problems:
            raise ExprError(problems[0])
        quantity = args[0][1]
        if name == "at":
            overrides: dict[str, float] = {}
            for key, value in zip(args[1::2], args[2::2]):
                overrides[key[1]] = go(value)
            return NaN if any(math.isnan(v) for v in overrides.values()) else float(resolver.at(quantity, overrides))
        points = resolver.sweep(quantity, args[1][1])
        if not points or any(math.isnan(y) for _, y in points):
            return NaN
        best_x, best_y = points[0]
        for x, y in points[1:]:
            better = y > best_y if name in {"maxover", "argmax"} else y < best_y
            if better and not _equal(y, best_y):
                best_x, best_y = x, y
        return float(best_y if name in {"maxover", "minover"} else best_x)

    return go(node)


def holds(text: str, env: dict[str, float], resolver: Any = None) -> bool:
    """True when the expression is a non-zero number for these variables."""
    value = evaluate(text, env, resolver)
    return not math.isnan(value) and value != 0


# ------------------------------------------------------------------ display

GREEK = {"alpha": "α", "beta": "β", "gamma": "γ", "delta": "δ", "theta": "θ", "phi": "φ", "omega": "ω", "mu": "μ", "lambda": "λ",
         "rho": "ρ", "sigma": "σ", "tau": "τ", "pi": "π", "epsilon": "ε", "eta": "η", "nu": "ν", "psi": "ψ", "Delta": "Δ", "Omega": "Ω"}
_FUNCTION_NAME = {"cosd": "cos", "sind": "sin", "tand": "tan", "acosd": "arccos", "asind": "arcsin", "atand": "arctan",
                  "atan2d": "arctan2", "acos": "arccos", "asin": "arcsin", "atan": "arctan", "atan2": "arctan2", "ln": "ln", "log10": "log"}
_PRECEDENCE = {"or": 1, "and": 2, "not": 3, "cmp": 4, "+": 5, "-": 5, "*": 6, "/": 6, "neg": 7, "^": 8}


def _escape(text: str) -> str:
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _identifier(name: str) -> str:
    if name in GREEK:
        return f"<mi>{GREEK[name]}</mi>"
    head, _, sub = name.partition("_")
    base = GREEK.get(head, head)
    return f"<msub><mi>{_escape(base)}</mi><mi>{_escape(sub)}</mi></msub>" if sub else f"<mi>{_escape(base)}</mi>"


def to_mathml(node: Node | str) -> str:
    """Presentation MathML (the restricted subset the pages allow) for an expression, built from the tree and never from the text."""
    if isinstance(node, str):
        node = parse(node)

    def number(value: float) -> str:
        text = repr(int(value)) if float(value).is_integer() else repr(value)
        return f"<mn>{text}</mn>"

    def paren(markup: str) -> str:
        return f"<mrow><mo>(</mo>{markup}<mo>)</mo></mrow>"

    def weight(n: Node) -> int:
        kind = n[0]
        if kind == "bin":
            return _PRECEDENCE[n[1]]
        if kind in {"cmp", "and", "or", "not"}:
            return _PRECEDENCE[kind]
        if kind == "neg":
            return _PRECEDENCE["neg"]
        return 9

    def aggregate_markup(name: str, args: list[Node]) -> str:
        quantity = _identifier(args[0][1])
        if name == "at":
            sets = "".join(("<mo>,</mo>" if i else "") + f"<mrow>{_identifier(key[1])}<mo>=</mo>{go(value)}</mrow>"
                           for i, (key, value) in enumerate(zip(args[1::2], args[2::2])))
            return f"<msub><mrow>{quantity}</mrow><mrow>{sets}</mrow></msub>"
        word = {"maxover": "max", "minover": "min", "argmax": "arg max", "argmin": "arg min"}[name]
        return f"<mrow><msub><mi>{word}</mi>{_identifier(args[1][1])}</msub>{quantity}</mrow>"

    def go(n: Node) -> str:
        kind = n[0]
        if kind == "num":
            return number(n[1])
        if kind == "var":
            return _identifier(n[1])
        if kind == "neg":
            inner = go(n[1])
            return f"<mrow><mo>−</mo>{paren(inner) if weight(n[1]) < 7 else inner}</mrow>"
        if kind == "not":
            return f"<mrow><mo>¬</mo>{go(n[1])}</mrow>"
        if kind in {"and", "or"}:
            return f"<mrow>{go(n[1])}<mo>{'∧' if kind == 'and' else '∨'}</mo>{go(n[2])}</mrow>"
        if kind == "cmp":
            symbol = {"<": "&lt;", "<=": "≤", ">": "&gt;", ">=": "≥", "==": "=", "!=": "≠"}[n[1]]
            return f"<mrow>{go(n[2])}<mo>{symbol}</mo>{go(n[3])}</mrow>"
        if kind == "bin":
            op, left, right = n[1], n[2], n[3]
            if op == "^":
                base = go(left)
                return f"<msup>{paren(base) if weight(left) < 9 else base}{go(right)}</msup>"
            if op == "/":
                return f"<mfrac>{go(left)}{go(right)}</mfrac>"
            level = _PRECEDENCE[op]
            left_markup = paren(go(left)) if weight(left) < level else go(left)
            right_markup = paren(go(right)) if weight(right) <= level and op in {"-", "*"} or weight(right) < level else go(right)
            sign = {"+": "+", "-": "−", "*": "⋅"}[op]
            return f"<mrow>{left_markup}<mo>{sign}</mo>{right_markup}</mrow>"
        if kind == "call":
            name, args = n[1], n[2]
            if name in AGGREGATES and not _aggregate_problems(n, None):
                return aggregate_markup(name, args)
            if name == "sqrt" and len(args) == 1:
                return f"<msqrt>{go(args[0])}</msqrt>"
            if name == "abs" and len(args) == 1:
                return f"<mrow><mo>|</mo>{go(args[0])}<mo>|</mo></mrow>"
            label = _FUNCTION_NAME.get(name, name)
            inner = "".join(go(arg) if i == 0 else f"<mo>,</mo>{go(arg)}" for i, arg in enumerate(args))
            return f"<mrow><mi>{_escape(label)}</mi><mo>⁡</mo>{paren(inner)}</mrow>"
        raise ExprError(f"unknown node {kind}")

    return f'<math xmlns="http://www.w3.org/1998/Math/MathML" display="inline">{go(node)}</math>'
