#!/usr/bin/env python3
"""Render researched, authored content into the learner deliverables.

Input is a job bundle: the owner's raw request, the authored content produced by the
research-and-author cycle, and the research evidence behind it. Output is the product a
learner actually uses, plus a delivery manifest the final gate checks:

    book/index.html        paged study book (front matter, diagnostic, per-subtopic pages)
    pages/<slug>.html      one web page per subtopic, sections tagged by Core role
    bank/questions.json    question bank; every unit carries a worked answer and a visual
    atlas/index.html       atlas linking every subtopic page and its Core sections
    builder/index.html     builder integration page, plus builder/run.json
    delivery.json          intake, evidence, coverage ledger and product locations

The renderer never writes a hold, a placeholder or a "pending" notice. If authored content
is missing, the corresponding element is simply absent and the delivery gate fails on the
rendered product. Subject vocabulary arrives as data; nothing here names a subject.

Usage:
    python3 Shared/tools/learner_product_render.py --bundle job.json --out DIR
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import raw_intake  # noqa: E402

STYLE = """
body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;margin:0;background:#fbfaf7;color:#1d2330;line-height:1.55}
main{max-width:760px;margin:0 auto;padding:16px}
.book-page{background:#fff;border:1px solid #ddd8cc;border-radius:8px;padding:20px 24px;margin:18px 0;break-after:page}
.page-no{color:#7a7466;font-size:.8rem;text-align:right}
figure{margin:14px 0}svg{width:100%;max-width:480px;height:auto;background:#fff;border:1px solid #e3dfd4;border-radius:6px}
figcaption{font-size:.85rem;color:#555}
[data-role=attempt]{background:#f3f7ff;border-left:3px solid #4a6fd8;padding:8px 12px;margin:8px 0}
[data-role=attempt] textarea{width:100%;min-height:3em}
details{margin:8px 0}summary{cursor:pointer;font-weight:600}
.misconception{background:#fff6ec;border-left:3px solid #d8894a;padding:8px 12px}
@media print{body{background:#fff}.book-page{border:0}}
""".strip()


def esc(value: object) -> str:
    return html.escape(str(value), quote=True)


def slug(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")[:60] or "topic"


def doc(title: str, body: str, depth: int = 1) -> str:
    return (
        "<!doctype html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        "<meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">\n"
        f"<title>{esc(title)}</title>\n<style>{STYLE}</style>\n</head>\n<body>\n<main>\n"
        f"{body}\n</main>\n</body>\n</html>\n"
    )


# ---------------------------------------------------------------- visuals

def _scale(points: list[tuple[float, float]], width=360, height=240, pad=34):
    xs = [p[0] for p in points] + [0.0]
    ys = [p[1] for p in points] + [0.0]
    x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
    sx = (width - 2 * pad) / ((x1 - x0) or 1)
    sy = (height - 2 * pad) / ((y1 - y0) or 1)
    s = min(sx, sy)

    def tr(x: float, y: float) -> tuple[float, float]:
        return round(pad + (x - x0) * s, 1), round(height - pad - (y - y0) * s, 1)

    return tr, s


def svg(visual: dict, uid: str) -> str:
    """Draw a descriptor as accessible inline SVG. Supported: vectors, curve, bars."""
    title, desc = visual.get("title", ""), visual.get("desc", "")
    parts: list[str] = []
    width, height = 360, 240
    if visual.get("bars"):
        bars = visual["bars"]
        top = max(float(b["value"]) for b in bars) or 1
        bw = (width - 60) / len(bars)
        parts.append(f'<line x1="40" y1="{height-30}" x2="{width-10}" y2="{height-30}" stroke="#555"/>')
        for i, bar in enumerate(bars):
            h = (height - 70) * float(bar["value"]) / top
            x = 50 + i * bw
            parts.append(f'<rect x="{x:.1f}" y="{height-30-h:.1f}" width="{bw*0.6:.1f}" height="{h:.1f}" fill="#4a6fd8"/>')
            parts.append(f'<text x="{x:.1f}" y="{height-12}" font-size="12">{esc(bar["label"])}</text>')
            parts.append(f'<text x="{x:.1f}" y="{height-36-h:.1f}" font-size="12">{esc(bar["value"])}{esc(visual.get("unit", ""))}</text>')
    else:
        points: list[tuple[float, float]] = []
        curve = visual.get("curve")
        if curve:
            a, b, c = (float(curve.get(k, 0)) for k in ("a", "b", "c"))
            lo, hi = (float(v) for v in curve["x"])
            n = 40
            points = [(lo + (hi - lo) * i / n, 0.0) for i in range(n + 1)]
            points = [(x, a * x * x + b * x + c) for x, _ in points]
        vectors = visual.get("vectors", [])
        extra = [tuple(map(float, v["from"])) for v in vectors] + [tuple(map(float, v["to"])) for v in vectors]
        marks = [tuple(map(float, m["at"])) for m in visual.get("marks", [])]
        circles = visual.get("circles", [])
        for circ in circles:
            cx, cy, r = float(circ["center"][0]), float(circ["center"][1]), float(circ["r"])
            extra += [(cx - r, cy - r), (cx + r, cy + r)]
        tr, s = _scale(points + extra + marks, width, height)
        ox, oy = tr(0, 0)
        parts.append(f'<line x1="10" y1="{oy}" x2="{width-8}" y2="{oy}" stroke="#999"/>')
        parts.append(f'<line x1="{ox}" y1="8" x2="{ox}" y2="{height-8}" stroke="#999"/>')
        parts.append(f'<text x="{width-22}" y="{oy-6}" font-size="12">{esc(visual.get("x_label", "x"))}</text>')
        parts.append(f'<text x="{ox+6}" y="18" font-size="12">{esc(visual.get("y_label", "y"))}</text>')
        for circ in circles:
            cx, cy = tr(float(circ["center"][0]), float(circ["center"][1]))
            parts.append(f'<circle cx="{cx}" cy="{cy}" r="{float(circ["r"])*s:.1f}" fill="none" stroke="#555" stroke-dasharray="4 3"/>')
        if points:
            path = " ".join(f"{'M' if i == 0 else 'L'}{x},{y}" for i, (x, y) in
                            enumerate(tr(px, py) for px, py in points))
            parts.append(f'<path d="{path}" fill="none" stroke="#d8894a" stroke-width="2"/>')
        marker = f"arrow-{uid}"
        parts.append(f'<defs><marker id="{marker}" markerUnits="userSpaceOnUse" markerWidth="9" markerHeight="9" refX="8" refY="4.5" orient="auto">'
                     '<path d="M0,0 L9,4.5 L0,9 z" fill="#2c4fb8"/></marker></defs>')
        for v in vectors:
            x1, y1 = tr(*map(float, v["from"]))
            x2, y2 = tr(*map(float, v["to"]))
            parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#2c4fb8" stroke-width="2" marker-end="url(#{marker})"/>')
            parts.append(f'<text x="{(x1+x2)/2+4:.1f}" y="{(y1+y2)/2-4:.1f}" font-size="12">{esc(v.get("label", ""))}</text>')
        for m in visual.get("marks", []):
            x, y = tr(*map(float, m["at"]))
            parts.append(f'<circle cx="{x}" cy="{y}" r="3.5" fill="#1d2330"/>')
            parts.append(f'<text x="{x+5}" y="{y-6}" font-size="12">{esc(m.get("label", ""))}</text>')
    return (
        f'<figure data-role="visual"><svg role="img" viewBox="0 0 {width} {height}" '
        f'aria-labelledby="t-{uid} d-{uid}"><title id="t-{uid}">{esc(title)}</title>'
        f'<desc id="d-{uid}">{esc(desc)}</desc>{"".join(parts)}</svg>'
        f"<figcaption>{esc(visual.get('caption') or title)}</figcaption></figure>"
    )


# ---------------------------------------------------------------- blocks

def attempt_block(prompt_label: str = "Your attempt") -> str:
    return (f'<div data-role="attempt"><label>{esc(prompt_label)} — write it before opening the answer.</label>'
            "<textarea aria-label=\"attempt\"></textarea></div>")


def steps_list(steps: list[str]) -> str:
    return "<ol>" + "".join(f"<li>{esc(s)}</li>" for s in steps) + "</ol>"


def question_block(q: dict, anchor: str, ident: dict | None, visual_uid: str) -> str:
    label = ""
    if ident and ident.get("status") == "RESOLVED":
        label = f'<p class="source">Source: {esc(ident["identity"]["label"])}</p>'
    elif q.get("owner_label"):
        label = f'<p class="source">Your question {esc(q["owner_label"])}</p>'
    parts = [f'<article id="{esc(anchor)}" data-role="question">', label, f"<p>{esc(q['text'])}</p>"]
    if q.get("visual"):
        parts.append(svg(q["visual"], visual_uid))
    parts.append(attempt_block())
    if q.get("hint"):
        parts.append(f"<details data-role=\"hint\"><summary>Hint</summary><p>{esc(q['hint'])}</p></details>")
    if q.get("steps"):
        parts.append('<details data-role="answer"><summary>Worked answer</summary>'
                     f"{steps_list(q['steps'])}<p><strong>Answer:</strong> {esc(q.get('answer', ''))}</p></details>")
    parts.append("</article>")
    return "".join(parts)


def teaching_block(sub: dict, anchor: str, uid: str) -> str:
    parts = [f'<section id="{esc(anchor)}" data-core="CORE1A" data-role="teaching">',
             f"<h3>Understand it</h3>"]
    parts += [f"<p>{esc(p)}</p>" for p in sub.get("explanation", [])]
    if sub.get("visual"):
        parts.append(svg(sub["visual"], uid))
    if sub.get("misconception"):
        parts.append(f'<p class="misconception"><strong>Common slip:</strong> {esc(sub["misconception"])}</p>')
    we = sub.get("worked_example")
    if we and we.get("steps"):
        parts.append('<section data-role="worked-example"><h4>Worked example</h4>'
                     f"<p>{esc(we['problem'])}</p>{steps_list(we['steps'])}"
                     f"<p><strong>Result:</strong> {esc(we.get('result', ''))}</p></section>")
    parts.append("</section>")
    return "".join(parts)


def reconstruct_block(sub: dict, anchor: str) -> str:
    rec = sub.get("reconstruct")
    if not rec:
        return ""
    return (f'<section id="{esc(anchor)}" data-core="CORE1B" data-role="reconstruction">'
            f"<h3>Rebuild it yourself</h3><p>{esc(rec['prompt'])}</p>{attempt_block()}"
            f'<details data-role="answer"><summary>Compare with a model answer</summary>'
            f"<p>{esc(rec['model_answer'])}</p></details></section>")


# ---------------------------------------------------------------- job

def _qkey(text: str) -> str:
    return raw_intake._question({"text": text})["id"]


def build(bundle: dict) -> dict:
    """Return {relative_path: text} for every product plus the delivery manifest."""
    plan = raw_intake.intake(bundle["request"])
    content, evidence = bundle["content"], bundle.get("evidence", {})
    questions_in = {q["id"]: q for q in plan["inputs"]["questions"]}
    label_ids = {q["label"]: q["id"] for q in plan["inputs"]["questions"] if q["text_status"] == "LABEL_ONLY"}
    syllabus_ids = {row["text"]: row["id"] for row in plan["inputs"]["syllabus"]}

    # Resolve authored questions to intake ids (supplied text, or a label recovered by research).
    authored: dict[str, dict] = {}
    for q in content.get("questions", []):
        qid = label_ids.get(q.get("supplied_as_label")) if q.get("supplied_as_label") else _qkey(q["text"])
        supplied = questions_in.get(qid)
        authored[qid] = {**q, "id": qid, "authored": supplied is None,
                         "owner_label": (supplied or {}).get("label")}
    identities = {}
    for row in evidence.get("identities", []):
        qid = label_ids.get(row.get("supplied_as_label")) if row.get("supplied_as_label") else _qkey(row["question"])
        identities[qid] = row

    subtopics = []
    for sub in content.get("subtopics", []):
        sid = syllabus_ids.get(raw_intake.clean(sub.get("syllabus"))) if sub.get("syllabus") else None
        kind = "syllabus" if sid else "research_subtopic"
        sid = sid or raw_intake.item_id("s", sub["title"])
        subtopics.append({**sub, "id": sid, "kind": kind, "slug": slug(sub["title"]),
                          "question_ids": [label_ids.get(t) or _qkey(t) for t in sub.get("practice", [])]})

    files: dict[str, str] = {}
    ledger: list[dict] = []
    bank: list[dict] = []
    title = content.get("title") or plan["subject"]

    # ---- web pages
    for sub in subtopics:
        page = f"pages/{sub['slug']}.html"
        body = [f'<p><a href="../atlas/index.html">Atlas</a> · <a href="../book/index.html">Book</a></p>',
                f"<h1>{esc(sub['title'])}</h1>",
                f'<section id="core1-{sub["id"]}" data-core="CORE1" data-role="orientation"><h2>Key idea</h2>'
                f"<p>{esc(sub.get('key_idea', ''))}</p></section>",
                teaching_block(sub, f"teach-{sub['id']}", f"w-{sub['id']}"),
                reconstruct_block(sub, f"rebuild-{sub['id']}"),
                f'<section id="practice-{sub["id"]}" data-core="CORE2" data-role="practice"><h2>Practice</h2>']
        for n, qid in enumerate(sub["question_ids"]):
            q = authored.get(qid)
            if not q:
                continue
            body.append(question_block(q, qid, identities.get(qid), f"wq-{qid}"))
            bank.append({
                "id": qid, "text": q["text"], "owner_label": q.get("owner_label"),
                "authored": q["authored"], "subtopic": sub["title"], "hint": q.get("hint"),
                "steps": q.get("steps", []), "answer": q.get("answer"),
                "visual": svg(q["visual"], f"b-{qid}") if q.get("visual") else None,
                "source_identity": (identities.get(qid) or {}).get("identity") if (identities.get(qid) or {}).get("status") == "RESOLVED" else None,
                "learner_location": f"{page}#{qid}",
            })
            if not q["authored"]:
                ledger.append({"input_id": qid, "kind": "question",
                               "teaching": f"{page}#teach-{sub['id']}",
                               "practice": f"{page}#{qid}",
                               "learner_location": f"book/index.html#book-{qid}"})
        body.append("</section>")
        files[page] = doc(f"{sub['title']} · {title}", "\n".join(body))
        ledger.append({"input_id": sub["id"], "kind": sub["kind"],
                       "teaching": f"{page}#teach-{sub['id']}",
                       "practice": f"{page}#practice-{sub['id']}",
                       "learner_location": f"book/index.html#book-teach-{sub['id']}"})

    # ---- book
    pages: list[str] = []

    def book_page(inner: str) -> None:
        pages.append(f'<section class="book-page" id="page-{len(pages)+1}">{inner}'
                     f'<p class="page-no">{len(pages)+1}</p></section>')

    start = plan["learner_start"]
    book_page(f"<h1>{esc(title)}</h1><p>{esc(content.get('introduction', ''))}</p>"
              "<p>How to use this book: read the key idea, study the explanation and the picture, follow the worked "
              "example line by line, then rebuild the idea in your own words before you try the practice questions. "
              "Always write your attempt before opening a hint or an answer; the comparison is where the learning happens.</p>")
    diag = content.get("diagnostic", [])
    book_page('<section id="diagnostic" data-role="diagnostic"><h2>Start here: a short check</h2>'
              f"<p>This book starts at the {esc(start['level'])} level with {esc(start['support'])} support. "
              "Answer these quick questions honestly. Your answers, not a guess about what you know, decide where to spend "
              "more time: if you miss one, read its subtopic slowly; if all are easy, move faster and go straight to practice.</p>"
              + "".join(f"<article><p>{esc(d['prompt'])}</p>{attempt_block()}"
                        f"<details data-role=\"answer\"><summary>Check</summary><p>{esc(d['answer'])}</p></details></article>"
                        for d in diag) + "</section>")
    book_page("<h2>Contents</h2><p>Each subtopic has four pages: the key idea, the full explanation with a picture, a worked "
              "example, and a page where you rebuild the idea and practise. The atlas and web pages hold the same material "
              "with interactive answers.</p><ol>"
              + "".join(f'<li><a href="#book-teach-{s["id"]}">{esc(s["title"])}</a></li>' for s in subtopics) + "</ol>")
    for sub in subtopics:
        book_page(f'<section data-core="CORE1"><h2>{esc(sub["title"])}</h2><h3>Key idea</h3>'
                  f"<p>{esc(sub.get('key_idea', ''))}</p><p>{esc((sub.get('explanation') or [''])[0])}</p></section>")
        explanation = dict(sub, worked_example=None)
        book_page(teaching_block(explanation, f"book-teach-{sub['id']}", f"bk-{sub['id']}"))
        we = sub.get("worked_example") or {}
        if we.get("steps"):
            book_page('<section data-role="worked-example" data-core="CORE1A"><h3>Worked example</h3>'
                      f"<p>{esc(we['problem'])}</p>{steps_list(we['steps'])}"
                      f"<p><strong>Result:</strong> {esc(we.get('result', ''))}</p></section>")
        inner = reconstruct_block(sub, f"book-rebuild-{sub['id']}") + "<h3>Practice</h3>"
        for qid in sub["question_ids"]:
            if qid in authored:
                inner += question_block(authored[qid], f"book-{qid}", identities.get(qid), f"bq-{qid}")
        book_page(inner)
    book_page("<h2>Self-check and next steps</h2><p>Before you finish, say each key idea aloud without looking. "
              "Mark any you could not explain and return to its explanation page.</p><ul>"
              + "".join(f"<li><strong>{esc(s['title'])}:</strong> {esc(s.get('key_idea', ''))}</li>" for s in subtopics)
              + "</ul>")
    files["book/index.html"] = doc(title, "\n".join(pages))

    # ---- atlas and builder
    files["atlas/index.html"] = doc(f"Atlas · {title}", f"<h1>Atlas · {esc(title)}</h1><ul>" + "".join(
        f'<li><a href="../pages/{s["slug"]}.html">{esc(s["title"])}</a> — '
        f'<a href="../pages/{s["slug"]}.html#core1-{s["id"]}">key idea</a>, '
        f'<a href="../pages/{s["slug"]}.html#teach-{s["id"]}">teaching</a>, '
        f'<a href="../pages/{s["slug"]}.html#rebuild-{s["id"]}">rebuild</a>, '
        f'<a href="../pages/{s["slug"]}.html#practice-{s["id"]}">practice</a>, '
        f'<a href="../book/index.html#book-teach-{s["id"]}">book</a></li>' for s in subtopics) + "</ul>")
    run = {"schema": "learner-product-run/v1", "intake_digest": plan["intake_digest"], "title": title,
           "book": "book/index.html", "atlas": "atlas/index.html", "question_bank": "bank/questions.json",
           "pages": [f"pages/{s['slug']}.html" for s in subtopics]}
    files["builder/run.json"] = json.dumps(run, indent=2, ensure_ascii=False) + "\n"
    files["builder/index.html"] = doc(f"Builder · {title}", f"<h1>Builder · {esc(title)}</h1>"
        '<p>Load <a href="run.json">run.json</a> in the run builder to rebuild or extend this job.</p><ul>'
        '<li><a href="../book/index.html">Book</a></li><li><a href="../atlas/index.html">Atlas</a></li>'
        + "".join(f'<li><a href="../pages/{s["slug"]}.html">{esc(s["title"])}</a></li>' for s in subtopics) + "</ul>")
    files["bank/questions.json"] = json.dumps({"schema": "question-bank-units/v1", "units": bank},
                                              indent=2, ensure_ascii=False) + "\n"

    # ---- evidence resolved to intake task ids
    research = []
    for row in evidence.get("research", []):
        ids = set()
        for text in row.get("covers", []):
            text = raw_intake.clean(text)
            ids |= {syllabus_ids.get(text), label_ids.get(text), _qkey(text), raw_intake.item_id("p", text)}
        research.append({"input_ids": sorted(i for i in ids if i), "kinds": row.get("kinds", []),
                         "sources": row.get("sources", []), "status": row.get("status", "DONE")})
    manifest = {
        "schema": "learner-product-delivery/v1",
        "intake": plan,
        "evidence": {"research": research,
                     "identities": [{**row, "input_id": qid} for qid, row in identities.items()]},
        "ledger": ledger,
        "products": {"book": "book/index.html", "pages": run["pages"], "question_bank": "bank/questions.json",
                     "atlas": "atlas/index.html", "builder": "builder/index.html"},
        "diagnostic": {"location": "book/index.html#diagnostic"},
    }
    files["delivery.json"] = json.dumps(manifest, indent=2, ensure_ascii=False) + "\n"
    return files


def write(bundle: dict, out: Path) -> Path:
    for rel, text in build(bundle).items():
        target = out / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text, encoding="utf-8")
    return out / "delivery.json"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--bundle", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)
    path = write(json.loads(Path(args.bundle).read_text(encoding="utf-8")), Path(args.out))
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
