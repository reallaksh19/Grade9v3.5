"""Does a question record ask a question, say something about it, and let a learner start before the first hint?

Intake could tell that 244 records had no source it could resolve and that their `answer.check` said the same thing 244 times. It could
not say what is wrong with the record in front of a learner: a stem that is the hint's own sentences, options that are the letters
A to D, an answer that never mentions what was asked, a hint that hands over the number the stem left out, a concept the scope defers.
Those are properties of one record and need no knowledge of a subject (the scope rule reads the scope's own list).

The registry's `component_policy.admission` names the points; this module is where they are checked, and intake calls it. Every point
that blocks was measured against every question the library held before it (0 refused) and against the 244 records of pull request 375.

  QUESTION_STEM           the stem has words enough to ask something, and is not made of sentences that its own hints or solution say
  QUESTION_STEM_COMPLETE  the stem ends where a sentence ends (a stem cut off mid-sentence asks half a question)            said
  QUESTION_OPTIONS        an option has text; a letter standing for itself ('(A) A') is a choice with nothing to choose
  QUESTION_GIVENS         a number a hint relies on is in the stem, the options or the conditions                              said
  QUESTION_SCOPE          the question does not teach a concept the scope document defers, unless it is routed as a declared extension
                          (a concept only the policy defers is said, not held)
  ANSWER_ANCHORED         the answer is about this question: it shares words or numbers with the stem, the options or the conditions
  ANSWER_WORKED           the answer is worked (two steps, a few lines) and its summary states a result; it is not a page pasted in
  ANSWER_VERIFIED         nobody has been asked to stand behind the key: a key not run, or disputed, does not enter a library

Two points are said, not held. Whether a number in a hint is data the stem left out or a constant, a coefficient or a value worked out
from what the stem gave cannot be told from the text (20 Hz in a hint about the audible range, 0.5 in the energy relation); whether a
stem that ends on a letter is cut or ends on a variable ('... = 5 + 3x') is the same kind of doubt. A check that cried wolf on authored
records would be switched off, so these are advisories: reported, not refusals.

What this cannot do: tell a plausible wrong explanation from a right one (the key of Q-PHY-KIN-2D-SRC-40 is right and its first step is
false; no text rule sees that), or trust `verification_status`, which an author writes. A numeric key that is computed from the stem's own
givens by an oracle would, and that is a larger change than a point here.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Iterator

STEM_MIN_WORDS = 6
ANCHORS_MIN = 2
WORKED_MIN_STEPS = 2
WORKED_MIN_CHARS = 80
SUMMARY_MAX_CHARS = 500
SCOPE_POLICY = Path(__file__).resolve().parents[1] / "policy" / "grade9-physics.v1.json"      # the one place the scope is written as data

SENTENCE = re.compile(r"(?<=[.?!])\s+")
OPTION_LABEL = re.compile(r"^\s*\(?([A-Za-z0-9])\)?\s*[.:)]?\s*")
NUMBER = re.compile(r"(?<![\w.])\d+(?:\.\d+)?(?![\w])")
WORD = re.compile(r"[^\W\d_]{4,}")
# where a stem may end: a sentence end, a closing mark, a number, a single variable, or a word that a blank completes
STEM_END = re.compile(r"""([.?!:;)\]}"'”’$%°=]|\d|(?:^|[\s(=+\-–×÷/^*,])[A-Za-z]|\b(?:is|are|be|has|have|equals?|called|given\s+by|from|of)|\b[A-Za-z]{1,2}\d*)$""")
# words that every question and every answer use; sharing one says nothing
STOP = frozenset("""find what when given which with from that this have has had does did will would could should about into over under then than they
them their there these those where while after before between because since also each both only other some such very more most same make made take
takes taken using used use uses its are were was been being and the for not but you your can may might must shall let say said per out off own one
two three four five six seven eight nine ten value values calculate determine state show give write explain describe following answer question""".split())
ANSWERING = {"ANSWER", "RESULT"}                 # a hint that gives the answer may state numbers the stem did not
REFUSED_VERIFICATION = {"NOT_RUN", "DISPUTED"}   # a key nobody ran, or that someone disputes
NEGATION = re.compile(r"\b(?:not|no|never|nor|ignore|ignoring|neglect|neglecting|without|exclude|excluding|avoid|don't)\b[^.?!;,]*$")
SENTENCE_RAW = re.compile(r"(?<=[.?!;])\s+")

BLOCKING = {"QUESTION_STEM": "BLOCK", "QUESTION_STEM_COMPLETE": "ADVISE", "QUESTION_OPTIONS": "BLOCK", "QUESTION_GIVENS": "ADVISE",
            "QUESTION_SCOPE": "BLOCK", "ANSWER_ANCHORED": "BLOCK", "ANSWER_WORKED": "BLOCK", "ANSWER_VERIFIED": "BLOCK"}


def _squash(text: str) -> str:
    return re.sub(r"[\W_]+", " ", text.lower()).strip()


def _sentences(text: str) -> list[str]:
    return [s for s in (_squash(p) for p in SENTENCE.split(text or "")) if len(s.split()) >= 3]


def _answer(row: dict) -> dict:
    return row.get("answer") if isinstance(row.get("answer"), dict) else {}


def _reasoning(row: dict) -> list[str]:
    return [step for step in _answer(row).get("reasoning") or [] if isinstance(step, str)]


def _solution_text(row: dict) -> list[str]:
    """Every sentence the record uses to teach the answer: its reasoning steps and its hints."""
    parts = _reasoning(row)
    parts += [str(hint.get("text", "")) for hint in row.get("hints") or [] if isinstance(hint, dict)]
    parts += [str(rung.get("text", "")) for rung in row.get("hint_ladder") or [] if isinstance(rung, dict)]
    return [s for part in parts for s in _sentences(part)]


def _question_text(row: dict) -> str:
    """What a learner has before opening anything: the stem, the options and the conditions."""
    stem = row.get("stem") if isinstance(row.get("stem"), str) else ""
    options = [o for o in row.get("options") or [] if isinstance(o, str)]
    conditions = [c for c in row.get("conditions") or [] if isinstance(c, str)]
    subparts = [str(s.get("text", s)) if isinstance(s, dict) else str(s) for s in row.get("subparts") or []]
    return " ".join([stem, *options, *conditions, *subparts])


def _anchors(text: str) -> set[str]:
    return {w for w in WORD.findall(text.lower()) if w not in STOP} | {f"#{n}" for n in NUMBER.findall(text)}


def _significant(numbers: set[str]) -> set[str]:
    """A number that is data: a decimal, or an integer above ten. Small integers are counts, steps and exponents."""
    return {n for n in numbers if "." in n or float(n) > 10}


@lru_cache(maxsize=1)
def scope() -> dict:
    """The concepts the scope defers, read from the scope policy (`Shared/policy/grade9-physics.v1.json`), the one place the scope is written as data."""
    policy = json.loads(SCOPE_POLICY.read_text(encoding="utf-8"))
    deferred = [{"concept": c["concept_id"], "row": c.get("document_row") or c["concept_id"], "document_row": c.get("document_row"), "terms": c["terms"],
                 "owners": c.get("owners", []), "route": c["scope_class"]}
                for c in policy["concept_policies"] if c["scope_class"] in ("DEFER", "PROHIBITED")]
    return {"policy": policy["policy_id"], "source": policy["source"], "waiver_routes": policy["waiver_routes"], "deferred": deferred}


def _concept_refs(row: dict) -> list:
    spec = (row.get("extensions") or {}).get("problem_specification") if isinstance(row.get("extensions"), dict) else None
    refs = spec.get("concept_refs") if isinstance(spec, dict) else None
    return refs if isinstance(refs, list) else []


def _scope_findings(row: dict, package_id: str | None) -> Iterator[tuple[str, str]]:
    """A deferred concept used as a concept: a mention that excludes it ('do not invent a torque equation') is not a use."""
    route = (row.get("extensions") or {}).get("grade9v3:scope_route") if isinstance(row.get("extensions"), dict) else None
    if route in scope().get("waiver_routes", []):
        return
    parts = [_question_text(row), *_reasoning(row), str(_answer(row).get("summary", ""))]
    sentences = [s.lower().replace("-", " ") for part in parts for s in SENTENCE_RAW.split(part) if s.strip()]
    declared = {re.sub(r"^CONCEPT_", "", re.sub(r"[^A-Z0-9]+", "_", str(ref).upper())) for ref in _concept_refs(row)}
    for entry in scope().get("deferred", []):
        if package_id in entry.get("owners", []):
            continue
        if entry["concept"] in declared:                                   # the question says so itself, in its problem specification
            held = "BLOCK" if entry["document_row"] else "ADVISE"
            yield (f"declares the concept {entry['concept']}, which the scope defers ({entry['row']!r}: {entry['route']}); route the record as a declared extension "
                   f"(extensions['grade9v3:scope_route']), or take the concept out", held)
            continue
        for term in entry["terms"]:
            pattern = re.compile(rf"\b{re.escape(term.lower().replace('-', ' '))}\b")
            used = any(not NEGATION.search(s[max(0, m.start() - 60):m.start()]) for s in sentences for m in pattern.finditer(s))
            if used:
                held = "BLOCK" if entry["document_row"] else "ADVISE"       # the scope document is the authority; a deferral only the policy states is said
                yield (f"uses '{term}', which the scope defers ({entry['row']!r}: {entry['route']}"
                       f"{'' if entry['document_row'] else ', in the policy and not yet in the scope document'}); take it out, or route the record as a "
                       f"declared extension (extensions['grade9v3:scope_route'])", held)


def findings(package: dict) -> Iterator[dict]:
    """{point, detail, severity} for every question of the package that fails an admission point."""
    package_id = package.get("package_id")
    for row in package.get("questions", []):
        if not isinstance(row, dict):
            continue
        qid = row.get("id", "<unidentified>")

        def found(point: str, detail: str) -> dict:
            return {"point": point, "severity": BLOCKING[point], "detail": f"{qid}: {detail}"}

        stem = row.get("stem") if isinstance(row.get("stem"), str) else ""
        words = stem.split()
        if len(words) < STEM_MIN_WORDS:
            yield found("QUESTION_STEM", f"the stem is {len(words)} word(s); it does not ask anything")
        else:
            own, solution = _sentences(stem), set(_solution_text(row))
            echoed = [s for s in own if s in solution]
            if own and 2 * len(echoed) >= len(own):
                yield found("QUESTION_STEM", f"{len(echoed)} of {len(own)} stem sentences are sentences of its own hints or solution; the stem says what the answer says")
            if not STEM_END.search(stem.rstrip()):
                yield found("QUESTION_STEM_COMPLETE", f"the stem ends '...{stem.rstrip()[-30:]}', which is not where a sentence ends")

        options = [o for o in row.get("options") or [] if isinstance(o, str)]
        empty = [o for o in options if not OPTION_LABEL.sub("", o, count=1).strip()
                 or _squash(OPTION_LABEL.sub("", o, count=1)) == _squash(OPTION_LABEL.match(o).group(1) if OPTION_LABEL.match(o) else "")]
        if options and empty:
            yield found("QUESTION_OPTIONS", f"{len(empty)} of {len(options)} option(s) carry no text beyond their letter (e.g. {empty[0]!r})")

        question = _question_text(row)
        hints = " ".join(str(h.get("text", "")) for h in (row.get("hints") or []) if isinstance(h, dict) and h.get("reveals") not in ANSWERING)
        late = sorted(_significant(set(NUMBER.findall(hints))) - set(NUMBER.findall(question)), key=float)
        if late:
            yield found("QUESTION_GIVENS", f"a hint relies on {', '.join(late[:4])}, which the stem, options and conditions do not give")

        for detail, severity in _scope_findings(row, package_id):
            yield {**found("QUESTION_SCOPE", detail), "severity": severity}

        answer, steps = _answer(row), _reasoning(row)
        said = " ".join([str(answer.get("summary", "")), *steps])
        shared = _anchors(question) & _anchors(said)
        if answer and len(shared) < ANCHORS_MIN:
            yield found("ANSWER_ANCHORED", f"the answer shares {len(shared)} word(s) or number(s) with the question; an answer that could stand under any "
                                           f"question is not an answer to this one")
        summary = str(answer.get("summary", ""))
        if answer and (len(steps) < WORKED_MIN_STEPS or sum(map(len, steps)) < WORKED_MIN_CHARS or len(summary) > SUMMARY_MAX_CHARS):
            yield found("ANSWER_WORKED", f"{len(steps)} reasoning step(s), {sum(map(len, steps))} characters, a summary of {len(summary)} characters: "
                                         f"the answer needs {WORKED_MIN_STEPS}+ steps, {WORKED_MIN_CHARS}+ characters and a summary of at most {SUMMARY_MAX_CHARS}")
        if answer.get("verification_status") in REFUSED_VERIFICATION:
            yield found("ANSWER_VERIFIED", f"the key is {answer['verification_status']}: nobody has been asked to stand behind it")
