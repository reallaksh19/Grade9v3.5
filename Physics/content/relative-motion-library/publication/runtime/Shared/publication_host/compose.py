"""Compose exact upstream objects into readable HTML, with answers separated."""

from html import escape
from itertools import combinations
from urllib.parse import quote

from Shared.contracts import digest, sentence
from .drawing import figure
from .science import equation_mathml, equation_review, numeric_expectation

STYLE = """
*{box-sizing:border-box}body{margin:0;color:#172c42;background:#f1f5f8;font:18px/1.6 Georgia,serif}
main{max-width:940px;margin:auto;background:white;padding:32px 42px}
h1,h2,h3,nav,.badge,summary{font-family:system-ui,sans-serif}h1{font-size:2rem;line-height:1.2}
h2{border-bottom:2px solid #b4d8dd;padding-bottom:8px;margin-top:36px}h3{font-size:1.1rem}
p{margin:12px 0}.badge{font-size:13px;color:#32546b}nav{font-size:14px}a{color:#075a88}
figure{margin:20px 0}img{display:block;width:auto;max-width:100%;max-height:370px;margin:auto}
figcaption{font-size:15px;line-height:1.45;margin-top:8px}math{font-size:1.2em;margin:18px 0}
.question{border-left:4px solid #398b93;padding-left:18px;margin:26px 0}
.source{font:13px/1.5 system-ui,sans-serif}.answer{padding:12px 18px;background:#f3f8f9;margin:24px 0}
.notice{font:14px/1.5 system-ui,sans-serif;padding:12px;background:#fff4db}
details{margin:12px 0}summary{cursor:pointer;font-size:15px}.numeric{font-weight:bold}
table{border-collapse:collapse;width:100%;font-size:14px}td,th{border:1px solid #bbcad2;padding:8px;text-align:left}
@media(max-width:600px){main{padding:20px}body{font-size:17px}h1{font-size:1.6rem}}
@media print{@page{size:A4;margin:15mm}body{background:white;font-size:11pt}main{max-width:none;padding:0}
nav{display:none}.answer-section{break-before:page}figure,math{break-inside:avoid}img{max-height:85mm}}
"""


def document(title, body):
    return ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width, initial-scale=1">'
            f'<title>{escape(title)}</title><style>{STYLE}</style></head><body><main>'
            + body + '</main></body></html>')


def compose(ctx):
    files, bindings, numeric, figures, reviews = {}, {}, {}, {}, {}
    for product in ctx["plan"]["products"]:
        core = product["core"]
        body = '<nav><a href="OWNER_BOARD.html">Publication status</a> · <a href="#answers">Answers and hints</a></nav>'
        body += '<p class="notice">Review preview — scientific and teaching approval remains pending.</p>'
        body += f'<h1>{escape(ctx["plan"]["title"])} · {core}</h1>'
        answers = []
        for unit in product["units"]:
            bucket = ctx["buckets"][unit["bucket_id"]]
            body += f'<h2>{escape(unit["title"])}</h2><p class="badge">Intrinsic concept difficulty: {bucket["badge"]}</p>'
            for block in unit["blocks"]:
                markup, answer = _block(ctx, block, files, numeric, figures, reviews, core)
                wrapped = f'<section data-object-id="{escape(block["id"], quote=True)}">{markup}</section>'
                bindings[block["id"]] = dict(core=core, content_digest=digest(block),
                                            artifact=core + '.html', kind=block["kind"])
                if block.get("placement") == "ANSWER":
                    answers.append(wrapped)
                elif block.get("placement") == "ELICITED_REVEAL":
                    # Closed, and open-able. The role wants attempt-first ordering and
                    # also says the answer stays accessible rather than locked, which is
                    # exactly what <details> is: a self-study learner can open it, and
                    # cannot read it by accident on the way past.
                    body += ('<details class="reveal"><summary>Check your answer</summary>'
                             + wrapped + '</details>')
                else:
                    body += wrapped
                if answer:
                    answers.append(answer)
        body += '<section class="answer-section" id="answers"><h2>Hints, answers and repair</h2>'
        body += ''.join(answers) + '</section>'
        files[core + '.html'] = document(ctx["plan"]["title"] + ' · ' + core, body)
    return files, {"objects": bindings, "numeric_answers": numeric, "figures": figures,
                   "scientific_review_requirements": reviews,
                   "reuse_candidates": reuse_candidates(ctx)}


def _block(ctx, block, files, numeric, figures, reviews, core):
    kind = block["kind"]
    if kind == "TEXT":
        return '<p>' + escape(block["text"]).replace('\n', '<br>') + '</p>', ''
    if kind == "EQUATION":
        body = equation_mathml(ctx, block) + '<p>' + escape(block["meaning"]) + '</p>'
        review = equation_review(ctx, block)
        if review is not None:
            reviews[block['id']] = review
            body += '<p class="notice">Equation adaptation awaiting scientific review.</p>'
            body += '<p>' + escape(block['transformation']['reason']) + '</p>'
            body += _list(block['transformation']['steps'])
        body += _list(block["symbols"]) + '<p>Applies when:</p>' + _list(block["conditions"])
        return body, ''
    if kind == "FIGURE":
        svg, evidence = figure(ctx, block)
        name = 'figures/' + digest(svg)[:24] + '.svg'
        files[name] = svg
        figures[block["id"]] = {**evidence, "artifact": name, "source_atom_ids": block["source_atom_ids"]}
        spec = block["scene"]
        caption = sentence(spec["caption"]) + ' Frame: ' + sentence(spec["frame"]) + ' Quantitative diagram.'
        if spec['kind'] == 'GRAPH':
            caption += f' Vertical axis minimum: {evidence["y_axis_min"]:g} {spec["y_unit"]}.'
        bridge = ''.join(
            f'<li><b>{escape(row["element"])}</b> is <code>{escape(row["symbol"])}</code>'
            f' &mdash; {escape(row["in_words"])}</li>'
            for row in block.get("correspondence") or [])
        if bridge:
            # Both directions, which is what the role specifications ask for and what a
            # caption alone cannot give: the picture's part, the symbol it stands for,
            # and the same thing said in words.
            bridge = f'<p>Reading this figure:</p><ul class="bridge">{bridge}</ul>'
        return (f'<figure><img src="{name}" alt="{escape(caption, quote=True)}">'
                f'<figcaption>{escape(caption)}</figcaption>{bridge}</figure>'), ''
    expected = numeric_expectation(ctx, block)
    if expected is not None:
        numeric[block["id"]] = expected
        if expected['status'] == 'SCIENTIFIC_REVIEW_REQUIRED':
            reviews[block['id']] = expected
    return _question(ctx, block, expected, core)


def _list(items):
    return '<ol>' + ''.join('<li>' + escape(x) + '</li>' for x in items) + '</ol>'



def _scaffold_support(block, core):
    if core not in {"CORE2A", "CORE2B"}:
        return ""
    scaffolds = block.get("scaffolds") or []
    if not scaffolds:
        return ""
    body = ('<aside class="scaffolds" aria-label="Optional problem-solving support" '
            'style="border:1px solid #c8d9df;padding:12px 16px;margin:18px 0;background:#f8fbfc">')
    body += '<h4>Support before you solve</h4>'
    for level, scaffold in enumerate(scaffolds, 1):
        label = scaffold["support_kind"].title()
        body += (
            f'<details data-supports-move="{escape(scaffold["supports_move_ref"], quote=True)}" '
            f'data-support-kind="{escape(scaffold["support_kind"], quote=True)}" '
            f'data-reveals="{escape(scaffold["reveals"], quote=True)}">'
            f'<summary>Support {level}: {escape(label)}</summary>'
            f'<p>{escape(scaffold["text"])}</p></details>'
        )
    return body + '</aside>'


def _reasoning_route(answer, transfer):
    route = answer.get("reasoning_route") or []
    if not route:
        return _list(answer["steps"])

    crux = answer["crux_move_ref"]
    protected = (transfer or {}).get("protected_move_ref")
    labels = {
        "REPRESENT": "Set up representation",
        "DECIDE": "Decision",
        "CONNECT": "Connect ideas",
        "TRANSFORM": "Execute",
        "VERIFY": "Verify",
    }
    body = '<section class="reasoning-route" aria-label="Reasoning route"><h4>Reasoning route</h4><ol>'
    for move in route:
        move_id = move["id"]
        is_crux = move_id == crux
        classes = "reasoning-move crux" if is_crux else "reasoning-move"
        heading = "Key decision" if is_crux else labels[move["kind"]]
        move_style = ("margin:12px 0;padding:10px 12px;border-left:6px solid #398b93;"
                      "background:#eef7f8" if is_crux else
                      "margin:12px 0;padding:10px 12px;border-left:3px solid #9ab8c1")
        body += (
            f'<li class="{classes}" style="{move_style}" '
            f'data-reasoning-move="{escape(move_id, quote=True)}" '
            f'data-move-kind="{escape(move["kind"], quote=True)}">'
            f'<span class="move-kind" style="font:12px/1.4 system-ui,sans-serif;'
            f'text-transform:uppercase;letter-spacing:.04em">{escape(heading)}</span>'
            f'<p><strong>{escape(move["action"])}</strong></p>'
            f'<p>{escape(move["why_valid"])}</p>'
            f'<p><strong>Result:</strong> {escape(move["output"])}</p></li>'
        )
    body += '</ol></section>'
    if protected:
        body += (
            '<p class="protected-note" style="font:14px/1.5 system-ui,sans-serif;'
            'border-left:4px solid #6f7880;padding-left:10px"><strong>Transfer decision:</strong> '
            'This decision was protected from pre-attempt scaffolding and is shown here '
            'only with the full answer.</p>'
        )
    return body


def _question(ctx, block, numeric_assessment, core):
    qid = escape(block["id"], quote=True)
    source = ctx["sources"][block["source_id"]]
    source_link = 'inputs/sources/' + quote(source["ref"]["path"], safe='/')
    provenance = escape(source["origin"] + ' · ' + source["citation"])
    body = f'<div class="question"><h3>Question {escape(block["original_number"])}</h3>'
    body += f'<p>{escape(block["stem"])}</p>' + _list(block.get("subparts", []))
    if block.get("conditions"):
        body += '<p>Conditions:</p>' + _list(block["conditions"])
    if block.get("options"):
        body += '<p>Options:</p>' + _list(block["options"])
    body += f'<p class="source"><a href="{source_link}">{provenance}</a></p>'
    body += _scaffold_support(block, core)
    body += f'<a href="#answer-{qid}">Hints and full answer</a></div>'
    answer = block["answer"]
    reveal = f'<article class="answer" id="answer-{qid}" data-answer-id="{qid}">'
    reveal += f'<h3>Question {escape(block["original_number"])}</h3>'
    for level, hint in enumerate(block.get("hints", []), 1):
        if isinstance(hint, str):
            reveal += f'<details class="source-hint"><summary>Hint {level}</summary><p>{escape(hint)}</p></details>'
        else:
            reveal += (
                f'<details class="source-hint" data-reveals="{escape(hint["reveals"], quote=True)}">'
                f'<summary>Hint {level}</summary><p>{escape(hint["text"])}</p></details>'
            )
    if block.get('guidance'):
        reveal += '<p>Guidance:</p>' + _list(block['guidance'])
    if numeric_assessment and numeric_assessment['status'] == 'SCIENTIFIC_REVIEW_REQUIRED':
        reveal += '<p class="notice">Numerical answer awaiting scientific review; not automatically verified.</p>'
    reveal += '<p>' + escape(answer["summary"]) + '</p>'
    if "numeric" in answer:
        n = answer["numeric"]
        reveal += f'<p class="numeric"><span data-answer-value="{qid}" data-unit="{escape(n["unit"], quote=True)}">{escape(str(n["value"]))}</span> {escape(n["unit"])}</p>'
    transfer = block.get("transfer") or {}
    reveal += _reasoning_route(answer, transfer) + _list(answer.get("subparts", []))
    check_label = "Independent check" if answer.get("reasoning_route") else "Check"
    reveal += '<p><strong>' + check_label + ':</strong> ' + escape(answer["check"]) + '</p>'
    rubric = answer.get("rubric") or []
    if rubric:
        reveal += '<p><strong>What a strong justification contains:</strong></p><ul>'
        for row in rubric:
            reveal += ('<li>' + escape(row["criterion"]) +
                       '<br><span class="source">This shows: ' +
                       escape(row["evidence_of"]) + '</span></li>')
        reveal += '</ul>'
    transfer = block.get("transfer") or {}
    if transfer:
        reveal += ('<p><strong>What changed in this transfer:</strong> ' +
                   escape(transfer["statement"]) + '</p>')
        reveal += ('<p class="source">Transfer dimension: ' +
                   escape(transfer["dimension"]) + '. Builds on: ' +
                   escape(", ".join(transfer.get("builds_on") or [])) + '</p>')
    if block.get("repair_ref"):
        reveal += ('<p><strong>Repair route:</strong> <code>' +
                   escape(block["repair_ref"]) + '</code></p>')
    reveal += '</article>'
    return body, reveal


def reuse_candidates(ctx):
    rows = [v for v in ctx["objects"].values() if v["content"]["kind"] == "QUESTION"]
    flags = []
    for a, b in combinations(rows, 2):
        x, y = a["content"], b["content"]
        same_source = (x["source_id"], x["source_question_id"]) == (y["source_id"], y["source_question_id"])
        same_family = x["family"] == y["family"]
        if same_source or same_family:
            fresh = "NEW_TRANSFER" in {x["exposure_role"], y["exposure_role"]}
            flags.append({"objects": [x["id"], y["id"]], "cores": [a["core"], b["core"]],
                          "same_source": same_source, "same_declared_family": same_family,
                          "status": "TRANSFER_REVIEW_REQUIRED" if fresh else "INTENTIONAL_REUSE_REVIEW_REQUIRED"})
    return {"objects_compared": len(rows), "pairs_compared": len(rows) * (len(rows) - 1) // 2,
            "candidates": flags, "semantic_novelty_validated": False}


def owner_board(report):
    subject = escape(report["subject"])
    rows = ''.join(f'<tr><td>{escape(k)}</td><td>{escape(v)}</td></tr>' for k, v in report["gates"].items())
    body = f'<h1>{subject} publication evidence</h1><p class="notice">Review preview. Learner release is not authorized.</p>'
    body += '<p>Basis: <code>' + report["basis_digest"] + '</code></p>'
    body += '<table><thead><tr><th>Gate</th><th>Observed status</th></tr></thead><tbody>' + rows + '</tbody></table>'
    body += '<h2>Learner products</h2><ul>'
    for core in report["products"]:
        body += f'<li><a href="{core}.html">{core}</a></li>'
    body += '</ul><p><a href="evidence.json">Detailed evidence, coverage and reuse candidates</a></p>'
    body += '<p>Next: independent scientific/pedagogical review and final-medium inspection. Machine closure does not prove explanation quality.</p>'
    return document(report["subject"] + ' owner board', body)


def report_for(ctx, evidence, basis):
    return {**evidence, "schema_version": "1.0.0", "basis_digest": basis,
            "subject": ctx["adapter"].subject,
            "products": [p["core"] for p in ctx["plan"]["products"]],
            "coverage": ctx["coverage"], "release_authorized": False,
            "gates": {
                "Source bytes and declared inventory": "CHECKED; extraction accuracy needs independent review",
                "Required object and declared-question closure": "CHECKED; embedded prose prompts need academic review",
                "Published numerical answers": "Supported families: oracle checked; other numeric candidates: transcription only, scientific review required",
                "Scientific adaptations awaiting review": str(len(evidence['scientific_review_requirements'])) + " — draft permitted; learner-ready acceptance held",
                "Figure data and artifact binding": "CHECKED for vector/graph families; scientific visual review NOT_RUN",
                "Core purpose and difficult inference depth": "NOT_RUN — independent academic review required",
                "Reuse and transfer": "All declared question pairs screened; semantic adjudication NOT_RUN",
                "Learner fit": ctx["learner_fit"],
                "Final-medium layout": "NOT_RUN — browser/print inspection required",
                "Portable inputs and command code": "COPIED; independent agent restart NOT_RUN",
                "Learner release": "BLOCKED — no automatic owner or reviewer authority"}}
