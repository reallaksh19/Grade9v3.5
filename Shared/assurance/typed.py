"""The typed checks: a question that declares what it gives, what it asks and how to compute it can be checked by running it.

A question may carry three extensions (Shared/assurance/question-assurance-extension.schema.json):

  problem_specification  the facts the learner can see (visible_facts), the constants the problem may assume (permitted_constants), the assumptions it declares
  answer_contract        what kind of answer, in which dimension, within which tolerance
  computation_model      a model type and its variables, computed here

What these checks do not do is guess. A question that declares none of this is INCONCLUSIVE for the check, never PASS: a check that cannot run has not passed.
Self-containment is the relation the specification states: the symbols the computation needs are visible facts, permitted constants or declared assumptions,
and a visible numeric fact is in the text the learner reads. (The first version scraped one- and two-letter words out of the answer text and called them
required symbols; units and small words are not symbols.)
"""
from __future__ import annotations

import math
import re
from typing import Any, Callable

NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
UNITS = {"LENGTH": ["m", "cm", "km", "ft"], "TIME": ["s", "ms", "min", "hr"], "SPEED": ["m/s", "km/h"], "ACCELERATION": ["m/s^2"],
         "FORCE": ["N", "kN"], "ANGLE": ["deg", "rad"]}


def _value(variables: dict, name: str) -> float:
    return float(variables[name]["value"])


def _projectile_range(v: dict, requested: list[str]) -> float:
    return _value(v, "u") ** 2 * math.sin(2 * math.radians(_value(v, "theta"))) / _value(v, "g")


def _projectile_height(v: dict, requested: list[str]) -> float:
    return _value(v, "u") ** 2 * math.sin(math.radians(_value(v, "theta"))) ** 2 / (2 * _value(v, "g"))


def _projectile_time(v: dict, requested: list[str]) -> float:
    return 2 * _value(v, "u") * math.sin(math.radians(_value(v, "theta"))) / _value(v, "g")


def _linear(v: dict, requested: list[str]) -> float:
    u, a, t = _value(v, "u"), _value(v, "a"), _value(v, "t")
    return u + a * t if "v" in requested else u * t + 0.5 * a * t ** 2


MODELS: dict[str, Callable[[dict, list[str]], float]] = {
    "PROJECTILE_NO_DRAG": _projectile_range, "PROJECTILE_MAX_HEIGHT": _projectile_height,
    "PROJECTILE_TIME_OF_FLIGHT": _projectile_time, "LINEAR_KINEMATICS": _linear,
}


def question_text(q: dict) -> str:
    """What the learner reads before opening anything."""
    parts = [q.get("stem", "")] + [o for o in q.get("options") or [] if isinstance(o, str)] + [c for c in q.get("conditions") or [] if isinstance(c, str)]
    return " ".join(str(p) for p in parts)


def self_containment(q: dict) -> tuple[str, list[dict]]:
    """(outcome, problems) for one question; each problem is {code, message}."""
    ext = q.get("extensions") or {}
    spec, model = ext.get("problem_specification"), ext.get("computation_model")
    if not isinstance(spec, dict):
        return "INCONCLUSIVE", [{"code": "NO_PROBLEM_SPECIFICATION", "message": "the question declares what it gives in no problem_specification, so self-containment cannot be certified"}]
    visible = {f["symbol"]: f for f in spec.get("visible_facts", []) if isinstance(f, dict) and "symbol" in f}
    constants = {f["symbol"] for f in spec.get("permitted_constants", []) if isinstance(f, dict) and "symbol" in f}
    allowed = set(visible) | constants | {a for a in spec.get("declared_assumptions", []) if isinstance(a, str)}
    problems: list[dict] = []
    text_numbers = {float(n) for n in NUMBER.findall(question_text(q))}
    for symbol, fact in visible.items():
        value = fact.get("value")
        if isinstance(value, (int, float)) and not isinstance(value, bool) and fact.get("visible_in", "STEM") == "STEM" and float(value) not in text_numbers:
            problems.append({"code": "GIVEN_NOT_VISIBLE", "message": f"{symbol} = {value} is declared visible and is not in the stem, options or conditions"})
    if not isinstance(model, dict):
        return ("FAIL", problems) if problems else ("INCONCLUSIVE", [{"code": "NO_COMPUTATION_MODEL", "message": "no computation_model says what the solution needs"}])
    for name, var in (model.get("variables") or {}).items():
        if name not in allowed:
            problems.append({"code": "HIDDEN_GIVEN", "message": f"the computation needs {name}, which is not a visible fact, a permitted constant or a declared assumption"})
        elif name in visible and "value" in visible[name] and "value" in var and visible[name]["value"] != var["value"]:
            problems.append({"code": "GIVEN_MISMATCH", "message": f"{name} is {visible[name]['value']} in the specification and {var['value']} in the computation"})
    return ("FAIL", problems) if problems else ("PASS", [])


def answer_correctness(q: dict) -> tuple[str, list[dict]]:
    ext = q.get("extensions") or {}
    model, contract_ = ext.get("computation_model"), ext.get("answer_contract") or {}
    numeric = (q.get("answer") or {}).get("numeric")
    if not isinstance(model, dict) or not isinstance(numeric, dict):
        return "NOT_APPLICABLE", []
    run = MODELS.get(model.get("model_type"))
    if run is None:
        return "INCONCLUSIVE", [{"code": "UNKNOWN_MODEL", "message": f"no model {model.get('model_type')!r} is implemented"}]
    try:
        computed = run(model.get("variables") or {}, model.get("requested_outputs") or [])
        stored = float(numeric["value"])
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as exc:
        return "FAIL", [{"code": "COMPUTATION_FAILED", "message": f"{type(exc).__name__}: {exc}"}]
    tolerance = (contract_.get("tolerance") or {}).get("relative", 0.01)
    if abs(computed - stored) <= tolerance * abs(computed) + 1e-9:
        return "PASS", []
    return "FAIL", [{"code": "WRONG_ANSWER", "message": f"the model gives {computed:.6g} and the key says {stored:g}"}]


def dimensional_correctness(q: dict) -> tuple[str, list[dict]]:
    dimension = ((q.get("extensions") or {}).get("answer_contract") or {}).get("expected_dimension")
    if not dimension or dimension not in UNITS:
        return "NOT_APPLICABLE", []
    unit = ((q.get("answer") or {}).get("numeric") or {}).get("unit")
    if not unit:
        return "FAIL", [{"code": "UNIT_MISSING", "message": f"the answer is {dimension} and carries no unit"}]
    if unit in UNITS[dimension]:
        return "PASS", []
    return "FAIL", [{"code": "WRONG_UNIT", "message": f"the answer is {dimension} and its unit is {unit!r}"}]
