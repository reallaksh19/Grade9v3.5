#!/usr/bin/env python3
"""The model behind an explorer: its parameters, quantities and scene geometry for any state, and the checks that make every
number the page shows one somebody computed.

An explorer spec (Shared/web/explorer-spec.schema.json) states the numbers as expressions (Shared/tools/explorer_expr.py). This
module evaluates them exactly as the page will, over the whole lattice of states the learner's sliders can reach, and holds the
spec to what it claims:

  * a quantity that is not a number somewhere the learner can go is an error;
  * the equation the learner reconstructs equals the quantity it compresses, at every state;
  * every invariant holds at every state, and every oracle (the drawn geometry against the quantities) too;
  * a prediction's right option is the right one, and each wrong one has a state that refutes it;
  * an observation said to be always true is, and one said not to be has a state that shows it;
  * a boundary case's shortcut holds or fails as declared, and there is one of each;
  * every element stays inside the picture at every state;
  * a goal can be reached on the sliders and is not already met at the start;
  * the explorer is built for the toughest concept of the set, not another.

An ERROR is a page that would show something false or break; deploy refuses it. A GAP is a page that works and is shallower than the
blueprint (BP-EXPLORER-GCDR) asks; deploy reports it and says what to write.
"""
from __future__ import annotations

import copy
import itertools
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Iterator, NamedTuple

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import explorer_expr as expr  # noqa: E402
from Shared.tools import web_blueprint_contract as blueprints  # noqa: E402

SPEC_SCHEMA = REPO / "Shared/web/explorer-spec.schema.json"
SPEC_VERSION = "grade9v3-explorer-spec-v1"
ROLE = "EXPLORER"

SWEEP_CAP = 361          # most values one parameter contributes when a claim sweeps it
STATE_CAP = 3000         # most states a claim is evaluated at
GEOMETRY_STATES = 400    # most states the scene is checked at
VIEW_WIDTH = 440         # the scene is drawn 440 units wide, and its labels are 15 units high
ASPECT = (0.36, 1.1)     # the picture's height over its width
MARGIN = 0.005           # how far outside the world an element may reach, as a fraction of the world
TEMPLATE = re.compile(r"\{([A-Za-z][A-Za-z0-9_]*)(?::(\d+))?\}")
ELEMENT_FIELDS: dict[str, tuple[set[str], set[str]]] = {      # kind -> (required, optional) beyond id, kind, role, label, reveal
    "point": ({"at"}, set()),
    "segment": ({"from", "to"}, set()),
    "arrow": ({"from", "to"}, set()),
    "circle": ({"center", "r"}, set()),
    "arc": ({"center", "r", "from_deg", "to_deg"}, set()),
    "polygon": ({"points"}, set()),
    "curve": ({"param", "t_min", "t_max", "x", "y"}, {"steps"}),
    "text": ({"at", "text"}, {"anchor"}),
}
COMPONENT_OF = {"target": "TARGET", "context": "CONTEXT", "parameters": "PARAMETERS", "quantities": "QUANTITIES", "scene": "SCENE",
                "second_view": "SECOND_VIEW", "predict": "PREDICT", "manipulate": "MANIPULATE", "observe": "OBSERVE",
                "contradict": "CONTRADICT", "deconstruct": "DECONSTRUCT", "reconstruct": "RECONSTRUCT", "invariants": "INVARIANT",
                "oracles": "SCENE", "boundary": "BOUNDARY", "fade": "FADE", "transfer": "TRANSFER"}
RESERVED = set(expr.FUNCTIONS) | expr.AGGREGATES | set(expr.CONSTANTS) | expr.KEYWORDS


class Finding(NamedTuple):
    kind: str            # "error" or "gap"
    component: str
    where: str
    detail: str

    def line(self) -> str:
        return f"{self.component} {self.where}: {self.detail}" if self.where else f"{self.component}: {self.detail}"


class Report:
    def __init__(self) -> None:
        self.findings: list[Finding] = []
        self.evidence: dict[str, Any] = {}

    def error(self, component: str, where: str, detail: str) -> None:
        self._add(Finding("error", component, where, detail))

    def gap(self, component: str, where: str, detail: str) -> None:
        self._add(Finding("gap", component, where, detail))

    def _add(self, finding: Finding) -> None:
        if finding not in self.findings:
            self.findings.append(finding)

    @property
    def errors(self) -> list[Finding]:
        return [f for f in self.findings if f.kind == "error"]

    @property
    def gaps(self) -> list[Finding]:
        return [f for f in self.findings if f.kind == "gap"]


# ------------------------------------------------------------------ the blueprint

def blueprint(registry: dict | None = None) -> dict:
    """The active explorer blueprint."""
    registry = registry or blueprints.load_registry()
    found = blueprints.blueprint_for_role(registry, ROLE)
    if found is None:
        raise blueprints.WebBlueprintContractError("WEB_BLUEPRINT_UNKNOWN: no active blueprint for the EXPLORER role")
    return found


def minima(bp: dict) -> dict[str, tuple[int, int]]:
    """component -> (items it needs to count as present, items of the reference page)."""
    out = {}
    for c in blueprints.components(bp):
        floor = c.get("min_items") or 1
        out[c["id"]] = (floor, c.get("target_items") or floor)
    return out


def stages(bp: dict) -> list[str]:
    """The learner's route, in order: the blueprint's own list."""
    return list(bp.get("route") or [])


# ------------------------------------------------------------------ the model

def template_names(text: str) -> list[tuple[str, int | None]]:
    return [(m.group(1), int(m.group(2)) if m.group(2) is not None else None) for m in TEMPLATE.finditer(text or "")]


def element_vars(element: dict) -> list[tuple[str, str]]:
    """(variable, expression) for each number the geometry of an element states, named {id}_x, {id}_y1, {id}_r, {id}_a2 ..."""
    eid, kind = element["id"], element["kind"]
    out: list[tuple[str, str]] = []
    if kind in {"point", "text"}:
        out += [(f"{eid}_x", element["at"][0]), (f"{eid}_y", element["at"][1])]
    elif kind in {"segment", "arrow"}:
        out += [(f"{eid}_x1", element["from"][0]), (f"{eid}_y1", element["from"][1]),
                (f"{eid}_x2", element["to"][0]), (f"{eid}_y2", element["to"][1])]
    elif kind in {"circle", "arc"}:
        out += [(f"{eid}_cx", element["center"][0]), (f"{eid}_cy", element["center"][1]), (f"{eid}_r", element["r"])]
        if kind == "arc":
            out += [(f"{eid}_a1", element["from_deg"]), (f"{eid}_a2", element["to_deg"])]
    elif kind == "polygon":
        for i, (x, y) in enumerate(element["points"], 1):
            out += [(f"{eid}_x{i}", x), (f"{eid}_y{i}", y)]
    return out


class Model:
    """Parameters, quantities and scene geometry as one function of the state, with the sweeps the model forms need."""

    def __init__(self, spec: dict) -> None:
        self.spec = spec
        self.parameters: list[dict] = list(spec["parameters"])
        self.ids = [p["id"] for p in self.parameters]
        self.by_id = {p["id"]: p for p in self.parameters}
        self.quantities: list[dict] = list(spec["quantities"])
        self.steps: list[tuple[str, str]] = [(q["id"], q["expr"]) for q in self.quantities]
        for element in spec["scene"]["elements"]:
            self.steps += element_vars(element)
        self._nodes: dict[str, Any] = {}
        self._values: dict[tuple, dict[str, float]] = {}
        self._sweeps: dict[tuple, list[tuple[float, float]]] = {}

    # --- states
    def initial(self) -> dict[str, float]:
        return {p["id"]: float(p["value"]) for p in self.parameters}

    def free(self) -> list[str]:
        return [p["id"] for p in self.parameters if not p.get("fixed")]

    def lattice(self, pid: str, cap: int = SWEEP_CAP) -> list[float]:
        """The values the learner's slider can take, thinned evenly to `cap` (the initial value and both ends always kept)."""
        p = self.by_id[pid]
        if p.get("fixed"):
            return [float(p["value"])]
        low, high, step = float(p["min"]), float(p["max"]), float(p["step"])
        count = int(math.floor((high - low) / step + 0.5))
        values = [low + k * step for k in range(count + 1)]
        values[-1] = high if abs(values[-1] - high) <= 1e-9 * max(1.0, abs(high)) else values[-1]
        if len(values) > cap:
            keep = {int(math.floor(i * (len(values) - 1) / (cap - 1) + 0.5)) for i in range(cap)}
            keep.add(min(range(len(values)), key=lambda i: abs(values[i] - p["value"])))
            values = [values[i] for i in sorted(keep)]
        return values

    def states(self, cap: int = STATE_CAP) -> Iterator[dict[str, float]]:
        """Every combination of the sliders' lattices, thinned to at most `cap` states; the initial state is always among them."""
        free = self.free()
        per = SWEEP_CAP if not free else max(5, int(math.floor(cap ** (1.0 / len(free)) + 1e-9)))
        grids = [self.lattice(pid, per) for pid in free]
        base = self.initial()
        yield dict(base)
        for combo in itertools.product(*grids):
            state = dict(base)
            state.update(zip(free, combo))
            if state != base:
                yield state

    # --- evaluation
    def node(self, text: str) -> Any:
        if text not in self._nodes:
            self._nodes[text] = expr.parse(text)
        return self._nodes[text]

    def values(self, state: dict[str, float]) -> dict[str, float]:
        """Parameters, then quantities, then scene geometry, in order: the whole env for this state."""
        key = tuple(state[pid] for pid in self.ids)
        cached = self._values.get(key)
        if cached is None:
            env = {pid: float(state[pid]) for pid in self.ids}
            for name, text in self.steps:
                env[name] = expr.evaluate(self.node(text), env)
            cached = env
            if len(self._values) < 400_000:
                self._values[key] = cached
        return cached

    def resolver(self, state: dict[str, float]) -> "Resolver":
        return Resolver(self, state)

    def evaluate(self, text: str, state: dict[str, float], extra: dict[str, float] | None = None) -> float:
        env = dict(self.values(state))
        if extra:
            env.update(extra)
        return expr.evaluate(self.node(text), env, self.resolver(state))

    def holds(self, text: str, state: dict[str, float]) -> bool:
        value = self.evaluate(text, state)
        return not math.isnan(value) and value != 0

    def with_set(self, overrides: dict[str, float], state: dict[str, float] | None = None) -> dict[str, float]:
        out = dict(state or self.initial())
        out.update({k: float(v) for k, v in overrides.items()})
        return out

    def describe(self, state: dict[str, float]) -> str:
        shown = [pid for pid in self.free()] or self.ids
        return ", ".join(f"{pid} = {_short(state[pid])}" for pid in shown)


class Resolver:
    """Answers the expression language's model forms for one state."""

    def __init__(self, model: Model, state: dict[str, float]) -> None:
        self.model, self.state = model, state

    def at(self, name: str, overrides: dict[str, float]) -> float:
        env = self.model.values(self.model.with_set(overrides, self.state))
        if name not in env:
            raise expr.ExprError(f"{name!r} is not a parameter or a quantity")
        return env[name]

    def sweep(self, name: str, parameter: str) -> list[tuple[float, float]]:
        model = self.model
        if parameter not in model.by_id:
            raise expr.ExprError(f"{parameter!r} is not a parameter")
        others = tuple(self.state[pid] for pid in model.ids if pid != parameter)
        key = (name, parameter, others)
        cached = model._sweeps.get(key)
        if cached is None:
            cached = []
            for value in model.lattice(parameter):
                env = model.values(dict(self.state, **{parameter: value}))
                if name not in env:
                    raise expr.ExprError(f"{name!r} is not a parameter or a quantity")
                cached.append((value, env[name]))
            model._sweeps[key] = cached
        return cached


def _short(value: float) -> str:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return "not a number"
    return f"{value:.6g}"


def _equal(x: float, y: float, tolerance: float = 1e-6) -> bool:
    return abs(x - y) <= tolerance * max(1.0, abs(x), abs(y))


# ------------------------------------------------------------------ the checks

def _text_of(value: Any) -> Any:
    """A number written where an expression goes is the expression that is that number."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return value
    return str(int(value)) if float(value).is_integer() else repr(float(value))


def normalize(spec: Any) -> Any:
    """The spec with the numbers an author wrote where an expression goes ([0, 0], "r": 2.5) written as the expressions they are.
    A copy; anything that is not a spec is returned as it is, for the structure check to say what is wrong with it."""
    if not isinstance(spec, dict) or not isinstance(spec.get("scene"), dict) or not isinstance(spec["scene"].get("elements"), list):
        return spec
    out = copy.deepcopy(spec)
    for element in out["scene"]["elements"]:
        if not isinstance(element, dict):
            continue
        for key in ("at", "from", "to", "center"):
            if isinstance(element.get(key), list):
                element[key] = [_text_of(v) for v in element[key]]
        if isinstance(element.get("points"), list):
            element["points"] = [[_text_of(v) for v in point] if isinstance(point, list) else point for point in element["points"]]
        for key in ("r", "from_deg", "to_deg", "t_min", "t_max", "x", "y"):
            if key in element:
                element[key] = _text_of(element[key])
    return out


def _schema_findings(spec: Any, report: Report) -> None:
    import jsonschema  # noqa: PLC0415
    schema = json.loads(SPEC_SCHEMA.read_text(encoding="utf-8"))
    problems: list[tuple[str, str, str]] = []
    for error in sorted(jsonschema.Draft202012Validator(schema).iter_errors(spec), key=lambda e: [str(p) for p in e.absolute_path]):
        path = list(error.absolute_path)
        where = ".".join(f"{part}" if isinstance(part, str) else f"[{part}]" for part in path).replace(".[", "[")
        top = path[0] if path and isinstance(path[0], str) else ""
        message = error.message
        if error.validator == "required":
            missing = re.findall(r"'([^']+)'", message)
            message = f"the key {missing[0]!r} is missing" if missing else message
            if not top and missing:
                top = missing[0]
        elif error.validator == "additionalProperties":
            extra = re.findall(r"'([^']+)'", message)
            message = f"unknown key {extra[0]!r}" if extra else message
        elif error.validator == "minLength":
            message = "is empty; write it"
        elif error.validator == "minItems":
            message = f"needs at least {error.validator_value} item(s)"
        elif error.validator == "pattern":
            message = f"{error.instance!r} does not look right (expected {error.validator_value})"
        elif error.validator == "const":
            message = f"must be {error.validator_value!r}"
        elif error.validator == "enum":
            message = f"{error.instance!r} is not one of {', '.join(map(str, error.validator_value))}"
        problems.append((COMPONENT_OF.get(top, "SPEC"), where, message))
    for component, where, message in problems:
        report.error(component, where, message)


def _expression(report: Report, component: str, where: str, text: str, known: set[str], parameters: set[str] | None,
                model_forms: bool = True) -> bool:
    problems = expr.check(text, known, parameters=parameters, model_forms=model_forms)
    for problem in problems:
        report.error(component, where, f"{text!r}: {problem}")
    return not problems


def _template(report: Report, component: str, where: str, text: str, known: set[str]) -> None:
    for name, _ in template_names(text):
        if name not in known:
            report.error(component, where, f"{{{name}}} in {text!r} is not a parameter or a quantity")


def _prose(report: Report, component: str, where: str, text: str, minimum: int = 12) -> None:
    if isinstance(text, str) and len(text.strip()) < minimum:
        report.gap(component, where, f"{text.strip()!r} is too short to teach anything; write a sentence")


def check(spec: dict, brief: dict | None, bp: dict | None = None) -> Report:
    """Hold a spec to the blueprint and to its own numbers."""
    report = Report()
    spec = normalize(spec)
    _schema_findings(spec, report)
    if report.errors:
        return report
    bp = bp or blueprint()
    floors = minima(bp)

    def count(component: str, where: str, have: int, noun: str) -> None:
        floor, target = floors.get(component, (1, 1))
        if have < target:
            report.gap(component, where, f"{have} {noun}; the blueprint's reference page has {target}"
                       + ("" if have >= floor else f" (and {floor} is the fewest that counts)"))

    ref = f"{bp['id']}@{bp['version']}"
    if spec["blueprint_ref"] != ref:
        report.error("SPEC", "blueprint_ref", f"{spec['blueprint_ref']!r} is not the active explorer blueprint {ref}")
    _check_target(spec, brief, report)
    parameter_names = set(_check_state(spec, report, count))
    known = parameter_names | {q["id"] for q in spec["quantities"]}
    elements = _check_scene(spec, report, count, known)
    _check_second_view(spec, report, known, parameter_names)
    if report.errors:
        return report            # the model itself is broken; claims about it would only repeat that
    model = Model(spec)
    states = list(model.states())
    report.evidence["states_checked"] = len(states)
    _check_numbers(model, states, report)
    if report.errors:
        return report
    _check_predict(spec, model, report, count, known, parameter_names)
    _check_goals(spec["manipulate"]["goals"], [f"manipulate.goals[{i}].goal" for i in range(len(spec["manipulate"]["goals"]))],
                 "MANIPULATE", model, states, report, known, parameter_names)
    count("MANIPULATE", "manipulate.goals", len(spec["manipulate"]["goals"]), "goal(s)")
    _check_observe(spec, model, states, report, count, known, parameter_names)
    _check_contradict(spec, model, states, report, known, parameter_names, elements)
    _check_deconstruct(spec, report, count, elements)
    _check_reconstruct(spec, model, states, report, count, {q["id"] for q in spec["quantities"]})
    _check_invariants(spec, model, states, report, count, known, parameter_names)
    _check_oracles(spec, model, states, report, known | {name for name, _ in model.steps}, parameter_names)
    _check_boundary(spec, model, report, count, known, parameter_names)
    _check_tasks(spec, model, report, count, known, parameter_names)
    _check_prose(spec, report)
    return report


def _check_target(spec: dict, brief: dict | None, report: Report) -> None:
    target = spec["target"]
    if brief is None:
        report.error("TARGET", "target.question_ref",
                     "the toughest concept of the set is not chosen (no question carries a complete difficulty estimate), so there is nothing to build for")
    elif target["question_ref"] != brief["question_ref"]:
        report.error("TARGET", "target.question_ref",
                     f"{target['question_ref']!r} is not the toughest concept of the set: that is {brief['label']} ({brief['question_ref']}), "
                     f"chosen by {brief['rule']}. An explorer is built for it")
    quantities = {q["id"] for q in spec["quantities"]}
    if target["quantity"] not in quantities:
        report.error("TARGET", "target.quantity", f"{target['quantity']!r} is not one of the quantities")


def _check_state(spec: dict, report: Report, count) -> list[str]:
    seen: set[str] = set()
    names: list[str] = []
    for i, p in enumerate(spec["parameters"]):
        where = f"parameters[{i}]"
        pid = p["id"]
        if pid in RESERVED:
            report.error("PARAMETERS", where, f"{pid!r} is a word of the expression language; choose another name")
        if pid in seen:
            report.error("PARAMETERS", where, f"{pid!r} is used twice")
        seen.add(pid)
        names.append(pid)
        if p.get("fixed"):
            continue
        if not all(k in p for k in ("min", "max", "step")):
            report.error("PARAMETERS", where, f"{pid} is a slider and needs min, max and step (or say fixed: true)")
            continue
        if not p["min"] < p["max"]:
            report.error("PARAMETERS", where, f"min {p['min']} must be below max {p['max']}")
            continue
        steps = (p["max"] - p["min"]) / p["step"]
        if abs(steps - round(steps)) > 1e-6:
            report.error("PARAMETERS", where, f"max - min ({p['max'] - p['min']:g}) is not a whole number of steps of {p['step']:g}")
        if steps > 4000:
            report.error("PARAMETERS", where, f"{round(steps)} steps is more than a slider can usefully offer; use a larger step")
        offset = (p["value"] - p["min"]) / p["step"]
        if not (p["min"] - 1e-9 <= p["value"] <= p["max"] + 1e-9) or abs(offset - round(offset)) > 1e-6:
            report.error("PARAMETERS", where, f"value {p['value']:g} must be a position of the slider (min {p['min']:g} plus a whole number of steps)")
    for i, q in enumerate(spec["quantities"]):
        where = f"quantities[{i}]"
        qid = q["id"]
        if qid in RESERVED:
            report.error("QUANTITIES", where, f"{qid!r} is a word of the expression language; choose another name")
        if qid in seen:
            report.error("QUANTITIES", where, f"{qid!r} is used twice")
        _expression(report, "QUANTITIES", f"{where}.expr", q["expr"], set(seen), None, model_forms=False)
        seen.add(qid)
    free = [p for p in spec["parameters"] if not p.get("fixed")]
    count("PARAMETERS", "parameters", len(free), "slider(s) (parameters that are not fixed)")
    count("QUANTITIES", "quantities", len(spec["quantities"]), "quantities")
    return names


def _check_scene(spec: dict, report: Report, count, known: set[str]) -> dict[str, dict]:
    scene = spec["scene"]
    world = scene["world"]
    (x0, x1), (y0, y1) = world["x"], world["y"]
    if not (x0 < x1 and y0 < y1):
        report.error("SCENE", "scene.world", "each range needs its first number below its second")
        return {}
    ratio = (y1 - y0) / (x1 - x0)
    if not ASPECT[0] <= ratio <= ASPECT[1]:
        report.error("SCENE", "scene.world", f"the world is {x1 - x0:g} wide and {y1 - y0:g} tall (a ratio of {ratio:.2f}); the picture is "
                     f"{VIEW_WIDTH} units wide, so keep the ratio between {ASPECT[0]} and {ASPECT[1]}")
    elements: dict[str, dict] = {}
    visible = set(known)
    for i, element in enumerate(scene["elements"]):
        where = f"scene.elements[{i}] ({element['id']})"
        eid, kind = element["id"], element["kind"]
        if eid in elements:
            report.error("SCENE", where, f"the id {eid!r} is used twice")
        elements[eid] = element
        required, optional = ELEMENT_FIELDS[kind]
        for key in sorted(required - set(element)):
            report.error("SCENE", where, f"a {kind} needs {key!r}")
        allowed = required | optional | {"id", "kind", "role", "label", "reveal"}
        for key in sorted(set(element) - allowed):
            report.error("SCENE", where, f"a {kind} has no {key!r}")
        if kind == "text" and "label" in element:
            report.error("SCENE", where, "a text element is its own label; use 'text'")
        local = {element["param"]} if kind == "curve" and "param" in element else set()
        if kind == "curve" and element.get("param") in visible:
            report.error("SCENE", where, f"the curve's parameter {element['param']!r} is already a parameter or a quantity; choose another name, for example t")
        reads: list[tuple[str, str]] = [(f"{where}.{var.split('_', 1)[1]}", text) for var, text in element_vars(element)] if not (required - set(element)) else []
        if kind == "curve" and not (required - set(element)):
            reads += [(f"{where}.t_min", element["t_min"]), (f"{where}.t_max", element["t_max"])]
        for place, text in reads:
            _expression(report, "SCENE", place, text, visible, None, model_forms=False)
        if kind == "curve" and not (required - set(element)):
            for key in ("x", "y"):
                _expression(report, "SCENE", f"{where}.{key}", element[key], visible | local, None, model_forms=False)
        for key in ("label", "text"):
            if key in element:
                _template(report, "SCENE", f"{where}.{key}", element[key], visible)
        if not (required - set(element)):
            visible |= {var for var, _ in element_vars(element)}
    if scene["elements"] and not any(e.get("reveal", "start") == "start" for e in scene["elements"]):
        report.error("SCENE", "scene.elements", "nothing is on show at the start (every element has a later reveal), so the learner meets an empty picture")
    count("SCENE", "scene.elements", len(scene["elements"]), "elements")
    return elements


def _check_second_view(spec: dict, report: Report, known: set[str], parameters: set[str]) -> None:
    view = spec["second_view"]
    quantities = {q["id"] for q in spec["quantities"]}
    movable = {p["id"] for p in spec["parameters"] if not p.get("fixed")}
    if view["x"] not in movable:
        report.error("SECOND_VIEW", "second_view.x", f"{view['x']!r} must be a parameter the learner can move (not fixed)")
    for i, series in enumerate(view["series"]):
        if series["quantity"] not in quantities:
            report.error("SECOND_VIEW", f"second_view.series[{i}].quantity", f"{series['quantity']!r} is not one of the quantities")
    for i, guide in enumerate(view.get("guides") or []):
        _expression(report, "SECOND_VIEW", f"second_view.guides[{i}].expr", guide["expr"], known, parameters)
        _template(report, "SECOND_VIEW", f"second_view.guides[{i}].label", guide["label"], known)
    ghost = view.get("ghost")
    if ghost and ghost["quantity"] not in quantities:
        report.error("SECOND_VIEW", "second_view.ghost.quantity", f"{ghost['quantity']!r} is not one of the quantities")
    shown = {series["quantity"] for series in view["series"]}
    if spec["target"]["quantity"] not in shown:
        report.gap("SECOND_VIEW", "second_view.series", f"the graph does not show the quantity the page is about, {spec['target']['quantity']!r}")


def _check_numbers(model: Model, states: list[dict], report: Report) -> None:
    """Every quantity and every scene number is a finite number at every state the sliders can reach."""
    bad: dict[str, dict] = {}
    for state in states:
        env = model.values(state)
        for name, _ in model.steps:
            if math.isnan(env[name]) and name not in bad:
                bad[name] = state
    for name, state in bad.items():
        component = "QUANTITIES" if name in {q["id"] for q in model.quantities} else "SCENE"
        report.error(component, name, f"is not a number when {model.describe(state)} (a division by zero, or a square root or logarithm of a negative number); "
                     "guard it with if(), or keep the slider away from there")


def _view_box(spec: dict) -> tuple[float, float]:
    (x0, x1), (y0, y1) = spec["scene"]["world"]["x"], spec["scene"]["world"]["y"]
    return VIEW_WIDTH, round(VIEW_WIDTH * (y1 - y0) / (x1 - x0))


def _geometry(model: Model, element: dict, state: dict[str, float]) -> list[tuple[float, float]]:
    """The points an element occupies at a state, enough to say whether it stays inside the picture."""
    env = model.values(state)
    eid, kind = element["id"], element["kind"]
    if kind in {"point", "text"}:
        return [(env[f"{eid}_x"], env[f"{eid}_y"])]
    if kind in {"segment", "arrow"}:
        return [(env[f"{eid}_x1"], env[f"{eid}_y1"]), (env[f"{eid}_x2"], env[f"{eid}_y2"])]
    if kind == "circle":
        cx, cy, r = env[f"{eid}_cx"], env[f"{eid}_cy"], env[f"{eid}_r"]
        return [(cx - r, cy - r), (cx + r, cy + r)]
    if kind == "arc":
        cx, cy, r = env[f"{eid}_cx"], env[f"{eid}_cy"], env[f"{eid}_r"]
        a1, a2 = env[f"{eid}_a1"], env[f"{eid}_a2"]
        angles = [a1, (a1 + a2) / 2, a2]
        return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in angles]
    if kind == "polygon":
        return [(env[f"{eid}_x{i}"], env[f"{eid}_y{i}"]) for i in range(1, len(element["points"]) + 1)]
    if kind == "curve":
        lo = model.evaluate(element["t_min"], state)
        hi = model.evaluate(element["t_max"], state)
        steps = element.get("steps", 60)
        out = []
        for k in range(steps + 1):
            t = lo + (hi - lo) * k / steps
            local = dict(env, **{element["param"]: t})
            out.append((expr.evaluate(model.node(element["x"]), local), expr.evaluate(model.node(element["y"]), local)))
        return out
    return []


def check_in_view(model: Model, report: Report) -> None:
    """Every element stays inside the picture at every state (rendered-geometry truth: nothing is drawn where it is clipped)."""
    spec = model.spec
    (x0, x1), (y0, y1) = spec["scene"]["world"]["x"], spec["scene"]["world"]["y"]
    mx, my = (x1 - x0) * MARGIN, (y1 - y0) * MARGIN
    sampled = list(model.states(GEOMETRY_STATES))
    first: dict[str, str] = {}
    for element in spec["scene"]["elements"]:
        for state in sampled:
            try:
                points = _geometry(model, element, state)
            except expr.ExprError:
                continue
            for x, y in points:
                if math.isnan(x) or math.isnan(y):
                    continue
                side = ("left of" if x < x0 - mx else "right of" if x > x1 + mx else "below" if y < y0 - my else "above" if y > y1 + my else "")
                if side and element["id"] not in first:
                    first[element["id"]] = (f"reaches ({_short(x)}, {_short(y)}), {side} the picture "
                                            f"(x {x0:g} to {x1:g}, y {y0:g} to {y1:g}) when {model.describe(state)}; widen scene.world")
                    break
    for eid, detail in first.items():
        report.error("SCENE", f"element {eid}", detail)


def _check_predict(spec: dict, model: Model, report: Report, count, known: set[str], parameters: set[str]) -> None:
    predict = spec["predict"]
    options = predict["options"]
    truths: list[bool] = []
    initial = model.initial()
    for i, option in enumerate(options):
        holds_all = True
        for j, test in enumerate(option["tests"]):
            where = f"predict.options[{i}].tests[{j}]"
            if not _set_ok(model, report, "PREDICT", f"{where}.set", test["set"]):
                holds_all = False
                continue
            if not _expression(report, "PREDICT", f"{where}.holds", test["holds"], known, parameters):
                holds_all = False
                continue
            if test.get("says"):
                _template(report, "PREDICT", f"{where}.says", test["says"], known)
            state = model.with_set(test["set"], initial)
            value = model.evaluate(test["holds"], state)
            if math.isnan(value):
                report.error("PREDICT", f"{where}.holds", f"{test['holds']!r} is not a number when {model.describe(state)}")
                holds_all = False
            elif value == 0:
                holds_all = False
        truths.append(holds_all)
    right = [i for i, ok in enumerate(truths) if ok]
    if predict["correct"] >= len(options):
        report.error("PREDICT", "predict.correct", f"there is no option {predict['correct']}")
    elif len(right) != 1:
        report.error("PREDICT", "predict.options", f"exactly one option should be true of the model, and {len(right)} are "
                     f"({', '.join(str(i) for i in right) or 'none'} by the tests); each false option needs a test that fails")
    elif predict["correct"] != right[0]:
        report.error("PREDICT", "predict.correct", f"says option {predict['correct']} is right, but the tests show it is option {right[0]}")
    count("PREDICT", "predict.options", len(options), "options")
    report.evidence["prediction"] = {"options": len(options), "true": right}


def _set_ok(model: Model, report: Report, component: str, where: str, overrides: dict[str, float], inside: bool = True) -> bool:
    ok = True
    for pid, value in overrides.items():
        if pid not in model.by_id:
            report.error(component, where, f"{pid!r} is not a parameter")
            ok = False
        elif inside and not model.by_id[pid].get("fixed") and not (model.by_id[pid]["min"] - 1e-9 <= value <= model.by_id[pid]["max"] + 1e-9):
            report.error(component, where, f"{pid} = {value:g} is outside the slider's range {model.by_id[pid]['min']:g} to {model.by_id[pid]['max']:g}")
            ok = False
    return ok


def _check_goals(goals: list[dict], places: list[str], component: str, model: Model, states: list[dict], report: Report, known: set[str],
                 parameters: set[str]) -> None:
    initial = model.initial()
    for goal, place in zip(goals, places):
        if not _expression(report, component, place, goal["goal"], known, parameters):
            continue
        reached = [s for s in states if model.holds(goal["goal"], s)]
        if not reached:
            report.error(component, place, f"{goal['goal']!r} is not true at any state the sliders can reach, so nobody can meet this goal")
        elif model.holds(goal["goal"], initial):
            report.error(component, place, f"{goal['goal']!r} is already true at the starting state, so there is nothing to do")


def _claim_truth(model: Model, claim: str, states: list[dict]) -> tuple[str, dict | None, dict | None]:
    """('always' | 'never' | 'sometimes', a state where it fails, a state where it holds)."""
    fails = holds = None
    for state in states:
        value = model.evaluate(claim, state)
        if math.isnan(value):
            raise expr.ExprError(f"not a number when {model.describe(state)}")
        if value != 0:
            holds = holds or state
        else:
            fails = fails or state
    return ("always" if fails is None else "never" if holds is None else "sometimes"), fails, holds


def _check_observe(spec: dict, model: Model, states: list[dict], report: Report, count, known: set[str], parameters: set[str]) -> None:
    statements = spec["observe"]["statements"]
    truths = []
    for i, statement in enumerate(statements):
        where = f"observe.statements[{i}]"
        if not _expression(report, "OBSERVE", f"{where}.claim", statement["claim"], known, parameters):
            continue
        try:
            truth, fails, holds = _claim_truth(model, statement["claim"], states)
        except expr.ExprError as caught:
            report.error("OBSERVE", f"{where}.claim", f"{statement['claim']!r} is {caught}")
            continue
        truths.append(truth)
        if truth != statement["truth"]:
            example = fails if truth != "always" else None
            report.error("OBSERVE", f"{where}.truth", f"says {statement['truth']!r}, but the claim {statement['claim']!r} is {truth!r} over the states the sliders can reach"
                         + (f" (it fails when {model.describe(example)})" if example else ""))
    count("OBSERVE", "observe.statements", len(statements), "statements")
    if truths and "always" not in truths:
        report.gap("OBSERVE", "observe.statements", "no statement is a general truth of the model (truth 'always'); the learner has nothing to confirm")
    if truths and all(t == "always" for t in truths):
        report.gap("OBSERVE", "observe.statements", "every statement is true; add the tempting claim ('never' or 'sometimes') so the learner must reject something")
    report.evidence["observations"] = truths


def _check_contradict(spec: dict, model: Model, states: list[dict], report: Report, known: set[str], parameters: set[str],
                      elements: dict[str, dict]) -> None:
    contradict = spec["contradict"]
    quantities = {q["id"] for q in spec["quantities"]}
    wrong, truth = contradict["wrong_model"]["quantity"], spec["target"]["quantity"]
    if wrong not in quantities:
        report.error("CONTRADICT", "contradict.wrong_model.quantity", f"{wrong!r} is not one of the quantities")
    elif wrong == truth:
        report.error("CONTRADICT", "contradict.wrong_model.quantity", "the tempting model is the true quantity itself")
    else:
        worst = max((abs(model.values(s)[wrong] - model.values(s)[truth]) for s in states
                     if not math.isnan(model.values(s)[wrong]) and not math.isnan(model.values(s)[truth])), default=0.0)
        if worst < 1e-6:
            report.error("CONTRADICT", "contradict.wrong_model", f"the tempting model {wrong!r} agrees with {truth!r} at every state, so it is not wrong")
        agree = sum(1 for s in states if _equal(model.values(s)[wrong], model.values(s)[truth]))
        report.evidence["contradiction"] = {"tempting_model": wrong, "largest_difference": round(worst, 6), "states_that_agree": agree}
    _check_goals([contradict["goal"]], ["contradict.goal.goal"], "CONTRADICT", model, states, report, known, parameters)
    ghost = (spec["second_view"].get("ghost") or {}).get("quantity")
    shown = [e for e in elements.values() if e.get("reveal") == "contradict"]
    if not shown and not ghost:
        report.gap("CONTRADICT", "contradict", "nothing in the picture or on the graph shows the tempting model, so there is no contradiction to see")
    elif ghost and ghost != wrong:
        report.gap("SECOND_VIEW", "second_view.ghost", f"the graph's ghost curve is {ghost!r}, not the tempting model {wrong!r}")
    elif not ghost:
        report.gap("SECOND_VIEW", "second_view.ghost", f"the graph does not draw the tempting model {wrong!r}; add a ghost")


def _check_deconstruct(spec: dict, report: Report, count, elements: dict[str, dict]) -> None:
    steps = spec["deconstruct"]["steps"]
    hidden = {eid for eid, e in elements.items() if e.get("reveal") == "deconstruct"}
    revealed: list[str] = []
    for i, step in enumerate(steps):
        where = f"deconstruct.steps[{i}]"
        for eid in step["reveals"]:
            if eid not in elements:
                report.error("DECONSTRUCT", f"{where}.reveals", f"{eid!r} is not an element of the scene")
            elif eid not in hidden:
                report.error("DECONSTRUCT", f"{where}.reveals", f"{eid!r} does not have reveal: 'deconstruct', so it is already on show and cannot be revealed here")
            elif eid in revealed:
                report.error("DECONSTRUCT", f"{where}.reveals", f"{eid!r} is revealed twice")
            revealed.append(eid)
        ask = step.get("ask")
        if ask and ask["correct"] >= len(ask["options"]):
            report.error("DECONSTRUCT", f"{where}.ask.correct", f"there is no option {ask['correct']}")
    for eid in sorted(hidden - set(revealed)):
        report.error("DECONSTRUCT", "scene", f"{eid!r} has reveal: 'deconstruct' but no step reveals it, so the learner never sees it")
    count("DECONSTRUCT", "deconstruct.steps", len(steps), "steps")
    if not hidden:
        report.gap("DECONSTRUCT", "scene.elements", "no element has reveal: 'deconstruct', so there is no mechanism to expose (the forces, components, constraints or relative motion)")


def _check_reconstruct(spec: dict, model: Model, states: list[dict], report: Report, count, known_q: set[str]) -> None:
    rec = spec["reconstruct"]
    for i, step in enumerate(rec["steps"]):
        if step["quantity"] not in known_q:
            report.error("RECONSTRUCT", f"reconstruct.steps[{i}].quantity", f"{step['quantity']!r} is not one of the quantities")
    equation = rec["equation"]["expr"]
    truth = spec["target"]["quantity"]
    try:
        used = expr.names(expr.parse(equation))[0]
    except expr.ExprError as caught:
        report.error("RECONSTRUCT", "reconstruct.equation.expr", f"{equation!r}: {caught}")
        return
    steps_used = sorted(used & known_q)
    if steps_used:
        report.error("RECONSTRUCT", "reconstruct.equation.expr",
                     f"{equation!r} uses {', '.join(steps_used)}, which are steps of the working. The equation is the closed form the steps compress into: "
                     f"write it with the parameters only ({', '.join(model.ids)})")
        return
    if not _expression(report, "RECONSTRUCT", "reconstruct.equation.expr", equation, set(model.ids), None, model_forms=False):
        return
    quantity_text = next(q["expr"] for q in spec["quantities"] if q["id"] == truth)
    if _normal(equation) == _normal(quantity_text):
        report.error("RECONSTRUCT", "reconstruct.equation.expr",
                     f"is the same expression as the quantity {truth!r}, so nothing was compressed: define {truth!r} from the steps the mechanism shows, "
                     "and write the equation as the closed form of them")
    worst, at = 0.0, None
    for state in states:
        a, b = model.evaluate(equation, state), model.values(state)[truth]
        if math.isnan(a) or math.isnan(b):
            continue
        gap = abs(a - b) / max(1.0, abs(a), abs(b))
        if gap > worst:
            worst, at = gap, state
    if worst > 1e-6:
        report.error("RECONSTRUCT", "reconstruct.equation.expr", f"{equation!r} is not equal to {truth!r}: they differ by {worst:.3g} (relative) when {model.describe(at)}")
    report.evidence["equation"] = {"expr": equation, "equals": truth, "largest_relative_difference": float(f"{worst:.3g}")}
    count("RECONSTRUCT", "reconstruct.steps", len(rec["steps"]), "steps")


def _normal(text: str) -> str:
    return re.sub(r"\s+", "", text)


def _check_invariants(spec: dict, model: Model, states: list[dict], report: Report, count, known: set[str], parameters: set[str]) -> None:
    held = 0
    for i, inv in enumerate(spec["invariants"]):
        where = f"invariants[{i}]"
        ok = all(_expression(report, "INVARIANT", f"{where}.{side}", inv[side], known, parameters) for side in ("lhs", "rhs"))
        if not ok:
            continue
        if _normal(inv["lhs"]) == _normal(inv["rhs"]):
            report.error("INVARIANT", where, "both sides are the same expression, so it says nothing")
            continue
        fails = None
        for state in states:
            a, b = model.evaluate(inv["lhs"], state), model.evaluate(inv["rhs"], state)
            if math.isnan(a) or math.isnan(b):
                fails = (state, "is not a number")
                break
            holds = {"==": _equal(a, b), "<=": a <= b or _equal(a, b), ">=": a >= b or _equal(a, b)}[inv["rel"]]
            if not holds:
                fails = (state, f"{_short(a)} {inv['rel']} {_short(b)} is false")
                break
        if fails:
            report.error("INVARIANT", where, f"is not an invariant: {inv['lhs']} {inv['rel']} {inv['rhs']} — {fails[1]} when {model.describe(fails[0])}")
        else:
            held += 1
    count("INVARIANT", "invariants", len(spec["invariants"]), "invariants")
    report.evidence["invariants_held"] = held


def _check_oracles(spec: dict, model: Model, states: list[dict], report: Report, known: set[str], parameters: set[str]) -> None:
    held = 0
    geometry = {name for name, _ in model.steps} - {q["id"] for q in spec["quantities"]}
    for i, oracle in enumerate(spec["oracles"]):
        where = f"oracles[{i}]"
        if not all(_expression(report, "SCENE", f"{where}.{side}", oracle[side], known, parameters) for side in ("left", "right")):
            continue
        read = expr.names(expr.parse(oracle["left"]))[0] | expr.names(expr.parse(oracle["right"]))[0]
        if not read & geometry:
            report.gap("SCENE", where, "does not read any element of the scene (element_x, element_y1 ...), so it checks the quantities against themselves, not the picture against them")
        worst, at = 0.0, None
        for state in states:
            a, b = model.evaluate(oracle["left"], state), model.evaluate(oracle["right"], state)
            if math.isnan(a) or math.isnan(b):
                continue
            gap = abs(a - b) / max(1.0, abs(a), abs(b))
            if gap > worst:
                worst, at = gap, state
        if worst > 1e-6:
            report.error("SCENE", where, f"the picture disagrees with the quantities: {oracle['left']} differs from {oracle['right']} by {worst:.3g} (relative) when {model.describe(at)}")
        else:
            held += 1
    report.evidence["oracles_held"] = held
    check_in_view(model, report)


def _check_boundary(spec: dict, model: Model, report: Report, count, known: set[str], parameters: set[str]) -> None:
    boundary = spec["boundary"]
    truth = spec["target"]["quantity"]
    results = []
    for i, case in enumerate(boundary["cases"]):
        where = f"boundary.cases[{i}]"
        if not _set_ok(model, report, "BOUNDARY", f"{where}.set", case["set"]):
            continue
        if not _expression(report, "BOUNDARY", f"{where}.shortcut", case["shortcut"], known, parameters):
            continue
        state = model.with_set(case["set"])
        a, b = model.evaluate(case["shortcut"], state), model.values(state)[truth]
        if math.isnan(a) or math.isnan(b):
            report.error("BOUNDARY", where, f"is not a number when {model.describe(state)}")
            continue
        outcome = "holds" if _equal(a, b) else "fails"
        results.append(outcome)
        if outcome != case["expect"]:
            report.error("BOUNDARY", f"{where}.expect", f"says the shortcut {case['expect']}, but {case['shortcut']!r} = {_short(a)} and {truth} = {_short(b)} when {model.describe(state)}, so it {outcome}")
    count("BOUNDARY", "boundary.cases", len(boundary["cases"]), "cases")
    if results and "holds" not in results:
        report.gap("BOUNDARY", "boundary.cases", "no case where the shortcut holds; the learner cannot tell where it is safe to use")
    if results and "fails" not in results:
        report.gap("BOUNDARY", "boundary.cases", "no case where the shortcut fails; there is no boundary to find")
    report.evidence["boundary"] = results


def _check_tasks(spec: dict, model: Model, report: Report, count, known: set[str], parameters: set[str]) -> None:
    initial = model.initial()
    for key, component, noun in (("fade", "FADE", "levels"), ("transfer", "TRANSFER", "tasks")):
        tasks = spec[key]
        for i, task in enumerate(tasks):
            where = f"{key}[{i}]"
            if not _set_ok(model, report, component, f"{where}.set", task["set"], inside=(key == "fade")):
                continue
            if not _expression(report, component, f"{where}.answer", task["answer"], known, parameters):
                continue
            state = model.with_set(task["set"], initial)
            value = model.evaluate(task["answer"], state)
            if math.isnan(value):
                report.error(component, f"{where}.answer", f"{task['answer']!r} is not a number when {model.describe(state)}")
            for line in (task.get("worked") or []) + [task["why"]]:
                _template(report, component, f"{where}.worked" if line != task["why"] else f"{where}.why", line, known | {"answer"})
            if key == "transfer" and all(abs(state[pid] - initial[pid]) < 1e-9 for pid in initial):
                report.error("TRANSFER", where, "uses the explorer's own starting numbers, so it is not a fresh task; give it numbers the learner has not seen")
        count(component, key, len(tasks), noun)
    if len(spec["fade"]) not in (3,):
        report.gap("FADE", "fade", f"{len(spec['fade'])} level(s); the ladder has three (values hidden, relation hidden, scene only)")
    sets = {json.dumps(t["set"], sort_keys=True) for t in spec["transfer"]}
    if len(spec["transfer"]) > 1 and len(sets) == 1:
        report.gap("TRANSFER", "transfer", "every task uses the same numbers; vary them")


DECIMAL = re.compile(r"(?<![\w.{:])\d+\.\d+(?![\w}])")


def _typed_numbers(spec: dict, report: Report) -> None:
    """A decimal typed into a sentence is a number nobody computed. It is fine when it is a given of the question (a slider's value or
    end, a number the author set in a task); otherwise the page should show it as {quantity:decimals}, so it is computed."""
    known: set[float] = set()
    for p in spec["parameters"]:
        known |= {float(p[k]) for k in ("value", "min", "max", "step") if k in p}
    for key in ("fade", "transfer"):
        for task in spec[key]:
            known |= {float(v) for v in task["set"].values()}
    for case in spec["boundary"]["cases"]:
        known |= {float(v) for v in case["set"].values()}
    for option in spec["predict"]["options"]:
        for test in option["tests"]:
            known |= {float(v) for v in test["set"].values()}
    fields: list[tuple[str, str, str]] = [("TARGET", "target.failure", spec["target"]["failure"]), ("TARGET", "target.invariant", spec["target"]["invariant"]),
                                          ("CONTRADICT", "contradict.imposes", spec["contradict"]["imposes"]),
                                          ("CONTRADICT", "contradict.why_correct", spec["contradict"]["why_correct"]),
                                          ("CONTRADICT", "contradict.why_wrong", spec["contradict"]["why_wrong"])]
    for i, statement in enumerate(spec["observe"]["statements"]):
        fields += [("OBSERVE", f"observe.statements[{i}].text", statement["text"]), ("OBSERVE", f"observe.statements[{i}].why", statement["why"])]
    for i, step in enumerate(spec["deconstruct"]["steps"]):
        fields.append(("DECONSTRUCT", f"deconstruct.steps[{i}].text", step["text"]))
        if step.get("ask"):
            fields.append(("DECONSTRUCT", f"deconstruct.steps[{i}].ask.why", step["ask"]["why"]))
    for i, step in enumerate(spec["reconstruct"]["steps"]):
        fields.append(("RECONSTRUCT", f"reconstruct.steps[{i}].text", step["text"]))
    for i, inv in enumerate(spec["invariants"]):
        fields += [("INVARIANT", f"invariants[{i}].text", inv["text"]), ("INVARIANT", f"invariants[{i}].try", inv["try"])]
    for key, component in (("fade", "FADE"), ("transfer", "TRANSFER")):
        for i, task in enumerate(spec[key]):
            fields += [(component, f"{key}[{i}].why", task["why"])] + [(component, f"{key}[{i}].worked", line) for line in task.get("worked") or []]
    for i, option in enumerate(spec["predict"]["options"]):
        fields += [("PREDICT", f"predict.options[{i}].text", option["text"])] + [("PREDICT", f"predict.options[{i}].tests[{j}].says", t["says"])
                                                                                 for j, t in enumerate(option["tests"]) if t.get("says")]
    for component, where, text in fields:
        for literal in DECIMAL.findall(text):
            if not any(abs(float(literal) - k) < 1e-9 for k in known):
                report.gap(component, where, f"types the number {literal} itself, which nothing checks; show it as {{quantity:decimals}} so the page computes it")


def _check_prose(spec: dict, report: Report) -> None:
    _typed_numbers(spec, report)
    for place, text in (("context.situation", spec["context"]["situation"]), ("target.failure", spec["target"]["failure"]),
                        ("target.operation", spec["target"]["operation"]), ("target.invariant", spec["target"]["invariant"]),
                        ("target.boundary", spec["target"]["boundary"]), ("contradict.why_correct", spec["contradict"]["why_correct"]),
                        ("contradict.why_wrong", spec["contradict"]["why_wrong"]), ("boundary.assumption", spec["boundary"]["assumption"]),
                        ("boundary.learner_must_identify", spec["boundary"]["learner_must_identify"])):
        _prose(report, COMPONENT_OF[place.split(".")[0]], place, text)
    for i, statement in enumerate(spec["observe"]["statements"]):
        _prose(report, "OBSERVE", f"observe.statements[{i}].why", statement["why"])
    for key in ("fade", "transfer"):
        for i, task in enumerate(spec[key]):
            _prose(report, COMPONENT_OF[key], f"{key}[{i}].why", task["why"])


# ------------------------------------------------------------------ for the page

def y_range(model: Model) -> list[float]:
    """The graph's vertical range, from every state the sliders can reach, so the axis does not jump about as the learner moves."""
    view = model.spec["second_view"]
    x = view["x"]
    series = [s["quantity"] for s in view["series"]] + ([view["ghost"]["quantity"]] if view.get("ghost") else [])
    low, high = math.inf, -math.inf
    for state in model.states(400):
        for value in model.lattice(x):
            env = model.values(dict(state, **{x: value}))
            for name in series:
                if math.isfinite(env[name]):
                    low, high = min(low, env[name]), max(high, env[name])
        for guide in view.get("guides") or []:
            if guide.get("orient", "h") == "h":
                value = model.evaluate(guide["expr"], state)
                if math.isfinite(value):
                    low, high = min(low, value), max(high, value)
    if not math.isfinite(low):
        return [0.0, 1.0]
    low = min(low, 0.0) if low >= 0 else low
    pad = (high - low) * 0.08 or 1.0
    return [low, high + pad]


def decimals_of(step: float) -> int:
    """How many decimals a slider's readout needs to show its steps."""
    text = f"{step:.10g}"
    return len(text.split(".")[1]) if "." in text else 0


def compile_page_model(spec: dict) -> dict:
    """What the page's runtime (Shared/web/explorer-model.js) is given: the sliders, the steps in the order they are evaluated,
    how many decimals each number shows, the scene's elements with the names of their numbers, and the graph's range."""
    model = Model(spec)
    parameters = []
    for p in spec["parameters"]:
        row = {"id": p["id"], "label": p["label"], "unit": p.get("unit", ""), "value": p["value"], "fixed": bool(p.get("fixed"))}
        if not row["fixed"]:
            row.update(min=p["min"], max=p["max"], step=p["step"], decimals=decimals_of(p["step"]))
        else:
            row["decimals"] = decimals_of(p["value"]) if float(p["value"]) != int(p["value"]) else 0
        parameters.append(row)
    elements = []
    for element in spec["scene"]["elements"]:
        row = {"id": element["id"], "kind": element["kind"], "role": element.get("role", "object"),
               "reveal": element.get("reveal", "start"), "vars": [name for name, _ in element_vars(element)]}
        for key in ("label", "text", "anchor"):
            if key in element:
                row[key] = element[key]
        if element["kind"] == "curve":
            row["curve"] = {key: element[key] for key in ("param", "t_min", "t_max", "x", "y")}
            row["curve"]["steps"] = element.get("steps", 60)
        elements.append(row)
    return {
        "parameters": parameters,
        "steps": [[name, text] for name, text in model.steps],
        "decimals": {q["id"]: q.get("decimals", 2) for q in spec["quantities"]} | {p["id"]: p["decimals"] for p in parameters},
        "elements": elements,
        "world": spec["scene"]["world"],
        "view_box": list(_view_box(spec)),
        "y_range": y_range(model),
    }


def main(argv: list[str] | None = None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description="check an explorer spec's numbers (Shared/tools/explorer_build.py check does this with the toughest concept of a product)")
    parser.add_argument("spec")
    args = parser.parse_args(argv)
    spec = json.loads(Path(args.spec).read_text(encoding="utf-8"))
    report = check(spec, {"question_ref": spec["target"]["question_ref"], "label": spec["target"]["question_ref"], "rule": "(not derived: no product given)"})
    for finding in report.findings:
        print(f"{finding.kind.upper():5s} {finding.line()}")
    print(json.dumps(report.evidence, ensure_ascii=False))
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
