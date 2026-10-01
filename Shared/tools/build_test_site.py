#!/usr/bin/env python3
"""Generate the TEST area's hub, rungs and deployments pages from repository state.

TEST is a sandbox subject (see TEST/README.md). These pages are projections, never authority: rungs come from
TEST/matrices/*.rungs.json, deployments from the receipts `deploy_test.py` writes, counts from TEST/ files. Nothing
here says a stage is finished; it reports counts, gaps and digests, and that every deployment is an unaccepted draft.
The Atlas page is the existing Topic Atlas page (public/physics/nlm/index.html) with its NLM strings replaced, so it
is regenerated with the rest and fails loudly if the template changes shape.

    python3 Shared/tools/build_test_site.py            # write
    python3 Shared/tools/build_test_site.py --check    # verify, write nothing
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
if __package__ in (None, ""):
    sys.path.insert(0, str(REPO))

from Shared.tools import matrix_conformance, render_core  # noqa: E402

esc = render_core.esc
TEST_ROOT = REPO / "TEST"
PUBLIC_TEST = REPO / "public" / "test"
NAV = (("index.html", "TEST"), ("atlas/index.html", "Atlas"), ("rungs/index.html", "Rungs"), ("deployments/index.html", "Deployments"))
ROLE_PAGES = (("index.html", "Product index"), ("core2.html", "Core2"), ("core1a.html", "Core1A"), ("core1.html", "Core1"),
              ("core1b.html", "Core1B"), ("core2a.html", "Core2A"), ("core2b.html", "Core2B"))
BANNER = "TEST sandbox · drafts only · not reviewed, not accepted, not curriculum"


def _json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


# ------------------------------------------------------------------ repository state

def matrices() -> list[dict]:
    return [_json(p) for p in sorted((TEST_ROOT / "matrices").glob("*.rungs.json"))]


def matrix_findings(board: dict) -> list[dict]:
    """What the matrix conformance check says about one TEST rung matrix (the same check the other subjects' matrices pass)."""
    try:
        return matrix_conformance.board_findings(board)
    except (KeyError, TypeError, ValueError) as caught:
        return [{"point": "MATRIX_UNREADABLE", "where": "", "detail": str(caught)}]


def products() -> list[dict]:
    return [_json(p) for p in sorted((PUBLIC_TEST / "products").glob("*/deploy-receipt.json"))]


def interactive_pages() -> list[dict]:
    return [_json(p) for p in sorted((PUBLIC_TEST / "interactive").glob("*/interactive-receipt.json"))]


def source_counts() -> dict:
    banks = sorted((TEST_ROOT / "question-bank").glob("*.json"))
    questions = sum(len(_json(p).get("questions") or []) for p in banks)
    return {
        "matrices": len(list((TEST_ROOT / "matrices").glob("*.rungs.json"))),
        "packages": len(list((TEST_ROOT / "library").glob("*.json"))),
        "banks": len(banks),
        "bank_questions": questions,
    }


# ------------------------------------------------------------------ page frame

def frame(depth: int, title: str, current: str, body: str, heading: str | None = None) -> str:
    root = "../" * depth
    home = root + "index.html"
    header = render_core.shell_header(home, root + "question-bank/index.html")
    crumbs = "".join(
        f'<a href="{esc("../" * (depth - 1) + path if depth > 1 else path)}"{" aria-current=page" if path == current else ""}>{esc(label)}</a>'
        for path, label in NAV)
    banner = banner_html()
    return ("<!doctype html>\n"
            '<html lang="en" data-g9-shell data-g9-role="TEST" data-g9-test="sandbox-draft" data-g9-mode="PAGES">'
            '<head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<link rel="stylesheet" href="{root}css/tablet-12-7.css">'
            f'<title>{esc(title if title == "TEST" else title + " · TEST")} · Grade9V3</title><style>{render_core.CSS}</style></head>'
            f'<body data-core="TEST">{banner}{header}'
            f'<nav data-g9-breadcrumb aria-label="Breadcrumb"><a href="{esc(home)}">Home</a>{crumbs}</nav>'
            f'<noscript>Search and display controls need JavaScript.</noscript>'
            f'<main><h1>{esc(heading or title)}</h1>{body}</main>'
            f'<footer data-g9-footer>TEST · sandbox for stress runs · nothing here is accepted or curriculum</footer>'
            f'<script>{render_core.JS}</script></body></html>\n')


BAR_STYLE = ("header[data-g9-test-banner]{display:flex;flex-wrap:wrap;gap:6px 14px;align-items:center;padding:6px 14px;"
             "background:#7c2d12;color:#fff;font:600 14px/1.4 system-ui,sans-serif}"
             "header[data-g9-test-banner] nav{display:flex;flex-wrap:wrap;gap:4px}"
             "header[data-g9-test-banner] a{display:inline-flex;align-items:center;min-height:44px;min-width:44px;"
             "padding:0 10px;color:#fde68a}")


def sandbox_bar(to_root: str) -> str:
    """The TEST header for a page that has no shared shell header of its own (the Atlas, an interactive page).

    It is the draft label plus a way to the portal and to every TEST page, and it carries the shell marker the site
    audit looks for. `to_root` is the relative path from the page to the site root, ending in a slash. It is not
    sticky on purpose: the Atlas has a sticky header of its own and two would cover each other."""
    links = "".join(f'<a href="{esc(to_root + "test/" + path)}">{esc(label)}</a>' for path, label in NAV)
    return (f"<style>{BAR_STYLE}</style>"
            f'<header class="g9-shell" data-g9-shell data-g9-test-banner role="banner"><span>{esc(BANNER)}</span>'
            f'<nav aria-label="TEST"><a href="{esc(to_root)}index.html">Portal</a>{links}</nav></header>')


def banner_html() -> str:
    return (f'<div data-g9-test-banner role="note" style="background:#7c2d12;color:#fff;padding:8px 14px;'
            f'font:600 14px/1.4 system-ui,sans-serif">{esc(BANNER)}</div>')


def card(ident: str, search: str, inner: str) -> str:
    return f'<article data-g9-unit="{esc(ident)}" data-g9-role="TEST" data-g9-search-text="{esc(search.lower())}">{inner}</article>'


def link(href: str, label: str) -> str:
    return f'<a href="{esc(href)}">{esc(label)}</a>'


# ------------------------------------------------------------------ pages

def hub_page() -> str:
    deployed = products()
    pages = interactive_pages()
    counts = source_counts()

    def product_line(receipt: dict, role: str, selection_key: str) -> str:
        return (f'{esc(receipt["slug"])}: {receipt["selection_counts"].get(selection_key, 0)} record(s) selected, '
                f'{receipt["gaps_by_core"].get(role, 0)} gap(s), render {esc(receipt["render_digest"])}')

    def stage(number: int, name: str, what: str, lines: list[str]) -> str:
        state = "<ul>" + "".join(f"<li>{line}</li>" for line in lines) + "</ul>" if lines else "<p>Nothing deployed yet.</p>"
        return card(f"stage-{number}", f"{name} {what} {' '.join(lines)}",
                    f'<h2>{number}. {esc(name)}</h2><p class="g9-prov">{esc(what)}</p>{state}')

    core2 = [product_line(r, "CORE2", "core2") for r in deployed]
    core1a = [product_line(r, "CORE1A", "microtopics") for r in deployed]
    inter = [f'{esc(r["slug"])}: {esc(r["title"])}' for r in pages]
    body = (
        '<p>TEST is a sandbox for stress runs. A test agent prepares <strong>Core2</strong>, then <strong>Core1A</strong>, then '
        'an <strong>interactive page</strong> for one topic, and each lands here as a labelled draft. Nothing here is reviewed, '
        'accepted or curriculum, and <code>accept_product.py</code> refuses TEST.</p>'
        '<p class="g9-prov">A gap count of 0 means the depth check found nothing missing. It counts what is absent, '
        'not how good it is, and it does not say the content has been reviewed.</p>'
        + stage(1, "Core2", "Owner-supplied questions, preserved verbatim", core2)
        + stage(2, "Core1A", "Concept construction for the same topic", core1a)
        + stage(3, "Interactive page", "A page built from the same canonical records", inter)
        + card("places", "atlas rungs deployments",
               '<h2>Where things are</h2><ul>'
               f'<li>{link("atlas/index.html", "Atlas")}: the Topic Atlas for the TEST matrix</li>'
               f'<li>{link("rungs/index.html", "Rungs")}: the ladder, rung by rung</li>'
               f'<li>{link("deployments/index.html", "Deployments")}: every deployed draft, with its digest and gaps</li></ul>')
        + card("sources", "matrices packages question bank",
               f'<h2>Sources in this repository</h2><ul><li>{counts["matrices"]} rung matrix file(s) in TEST/matrices</li>'
               f'<li>{counts["packages"]} package file(s) in TEST/library</li>'
               f'<li>{counts["banks"]} owner-supplied question file(s) in TEST/question-bank, {counts["bank_questions"]} question(s)</li></ul>'
               '<p class="g9-prov">How to add each of them: TEST/README.md in the repository.</p>'))
    return frame(1, "TEST", "index.html", body, heading="TEST: a sandbox for stress runs")


def rungs_page() -> str:
    boards = matrices()
    if not boards:
        body = ('<p>No TEST rung matrix yet.</p><p class="g9-prov">Add TEST/matrices/SLUG.rungs.json (the format is '
                'like the rung matrices of the other subjects), then run build_web_data.py so the Atlas can read it.</p>')
        return frame(2, "Rungs", "rungs/index.html", body)
    body = ""
    for board in boards:
        rows = ""
        for rung in board.get("rungs", []):
            micro = rung.get("microtopic") or {}
            rows += (f'<tr><td>{esc(rung.get("rung"))}</td><td>{esc(rung.get("ladder_position"))}</td>'
                     f'<td>{esc(rung.get("microtopic_ref"))}<br>{esc(micro.get("title", ""))}</td>'
                     f'<td>{"<br>".join(esc(x) for x in rung.get("must_contain", []))}</td>'
                     f'<td>{esc(", ".join(rung.get("ceiling", [])))}</td></tr>')
        table = ('<div class="g9-table-scroll"><table><thead><tr><th>Rung</th><th>Position</th><th>Microtopic</th>'
                 f'<th>Must contain</th><th>Ceiling</th></tr></thead><tbody>{rows}</tbody></table></div>')
        found = matrix_findings(board)
        check = ("".join(f'<li>{esc(f["point"])} · {esc(f["where"])}: {esc(f["detail"])}</li>' for f in found))
        check = (f'<details open><summary>Matrix check: {len(found)} finding(s)</summary><ul>{check}</ul></details>' if found else
                 '<p class="g9-prov">Matrix check: no finding. That is not a review.</p>')
        body += card(str(board.get("matrix_id")), f'{board.get("topic", "")} {board.get("subtopic", "")} {board.get("matrix_id", "")}',
                     f'<h2>{esc(board.get("topic"))}: {esc(board.get("subtopic"))}</h2>'
                     f'<p class="g9-prov">{esc(board.get("matrix_id"))} · {len(board.get("rungs", []))} rung(s) · '
                     f'{link("../atlas/index.html?matrix=" + str(board.get("matrix_id")), "Open in the Atlas")}</p>{check}{table}')
    return frame(2, "Rungs", "rungs/index.html", body)


def deployments_page() -> str:
    deployed = products()
    pages = interactive_pages()
    body = ""
    for r in deployed:
        present = [(name, label) for name, label in ROLE_PAGES if name in r["pages"]]
        links = " · ".join(link(f'../products/{r["slug"]}/{name}', label) for name, label in present)
        gaps = ", ".join(f"{core} {count}" for core, count in r["gaps_by_core"].items()) or "none"
        empty = (f'<p class="g9-prov">Roles with no records selected: {esc(", ".join(r["empty_roles"]))}. '
                 'Their pages have no items.</p>') if r["empty_roles"] else ""
        counts = ", ".join(f"{k} {v}" for k, v in r["selection_counts"].items())
        gap_list = "".join(f'<li>{esc(g["core"])} · {esc(g["record"])}: {esc(g["detail"])}</li>' for g in r.get("gaps", []))
        gap_details = (f'<details><summary>The {r["gap_count"]} gap(s)</summary><ul>{gap_list}</ul></details>'
                       if gap_list else "")
        advised = r.get("advisories", [])
        advice_list = "".join(f'<li>{esc(a["core"])} · {esc(a["component"])} · {esc(a["record"])}: {esc(a["detail"])}</li>' for a in advised)
        advice_details = (f'<details><summary>{len(advised)} component(s) the blueprint expects and the records do not supply</summary>'
                          f'<p class="g9-prov">Advisory, not a gap: the reference page has each of these. '
                          f'Blueprint: {esc(", ".join(r.get("blueprints", {}).values()))}.</p><ul>{advice_list}</ul></details>'
                          if advice_list else "")
        waived = r.get("waived", [])
        waived_list = "".join(f'<li>{esc(w["core"])} · {esc(w["component"])} · {esc(w["record"])}: {esc(w["reason"])}</li>' for w in waived)
        waived_details = (f'<details><summary>{len(waived)} component(s) the records waive, with their reasons</summary>'
                          f'<p class="g9-prov">Held to the {esc(r.get("held_to", "FLOOR").lower())} depth: an expected component is '
                          f'supplied or waived by the record with a written reason. The reasons are the author\'s, for the Owner to accept or refuse.</p>'
                          f'<ul>{waived_list}</ul></details>' if waived_list else "")
        quality = r.get("quality") or {}
        quality_list = "".join(f'<li>{esc(f["severity"])} · {esc(f["rule"])} · {esc(f["where"])}: {esc(f["detail"])}</li>'
                               for f in quality.get("findings", []))
        quality_details = (f'<details><summary>Learner-quality check, static: {len(quality["findings"])} finding(s)</summary>'
                           f'<p class="g9-prov">What the learner would see, read off the pages against the quality contract. '
                           f'It does not say the content is right.</p><ul>{quality_list}</ul></details>'
                           if quality.get("findings") else
                           '<p class="g9-prov">Learner-quality check, static: no finding. That is not a review.</p>'
                           if quality.get("checked", "").startswith("static") else "")
        body += card(f'product-{r["slug"]}', f'{r["slug"]} {r["title"]} product',
                     f'<h2>{esc(r["title"])}</h2><p class="g9-prov">Product {esc(r["slug"])} · '
                     f'DRAFT, {"with gaps" if r["gap_count"] else "no gaps reported, not reviewed"} · accepted: no · render {esc(r["render_digest"])}</p>'
                     f'<p>{links}</p><p>Selected records: {esc(counts)}. Gaps: {esc(gaps)} ({r["gap_count"]} in total).</p>{gap_details}{advice_details}{waived_details}{quality_details}{empty}')
    for r in pages:
        body += card(f'interactive-{r["slug"]}', f'{r["slug"]} {r["title"]} {r["purpose"]} interactive',
                     f'<h2>{esc(r["title"])}</h2><p class="g9-prov">Interactive page {esc(r["slug"])} · DRAFT · accepted: no · '
                     f'blueprint {esc(r["blueprint_ref"])}</p><p>{esc(r["purpose"])}</p>'
                     f'<p>{link("../interactive/" + r["slug"] + "/index.html", "Open the page")} · built from '
                     f'{esc(", ".join(r["records"]))}</p>')
    if not body:
        body = '<p>Nothing is deployed yet.</p><p class="g9-prov">deploy_test.py product / interactive puts drafts here.</p>'
    return frame(2, "Deployments", "deployments/index.html", body)


ATLAS_TRANSFORM = REPO / "Shared" / "web" / "atlas-sandbox-transform.v1.json"
ATLAS_INIT = """<script>
  window.addEventListener('DOMContentLoaded', () => {
    const matrices = ((window.GRADE9V3 && window.GRADE9V3.subjects && window.GRADE9V3.subjects.TEST) || {}).matrices || [];
    const wanted = new URLSearchParams(location.search).get('matrix');
    const pick = matrices.find((m) => m.matrix_id === wanted) || matrices[0];
    if (!pick) {
      document.getElementById('atlasSubtopicSubtitle').textContent = 'No TEST rung matrix yet.';
      const note = document.createElement('p');
      note.style.cssText = 'overflow-wrap:anywhere;margin:12px 0;color:var(--text-muted)';
      note.textContent = 'The Atlas reads TEST/matrices/*.rungs.json through public/data/data.js. '
        + 'Add a matrix, then run build_web_data.py.';
      document.querySelector('.breadcrumb').after(note);
      return;
    }
    window.ATLAS.init(pick.matrix_id);
  });
</script>"""


def atlas_page() -> str:
    """An existing Topic Atlas page, bound to the TEST subject.

    Which page, and which of its strings are replaced, is data (Shared/web/atlas-sandbox-transform.v1.json).
    Every replacement must match exactly once: if the template changes shape this fails loudly rather than
    publishing a half-converted page."""
    transform = _json(ATLAS_TRANSFORM)
    text = (REPO / transform["template"]).read_text(encoding="utf-8")
    for step in transform["swaps"]:
        old, new = step["old"], step["new"].replace("{sandbox_bar}", sandbox_bar("../../"))
        if text.count(old) != 1:
            raise ValueError(f"the Topic Atlas template changed: expected exactly one {old[:60]!r}")
        text = text.replace(old, new)
    init = text.index(transform["init"]["block_start"])
    end = text.index("</script>", init) + len("</script>")
    if transform["init"]["call"] not in text[init:end]:
        raise ValueError("the Topic Atlas template changed: its init call moved")
    return text[:init] + ATLAS_INIT + text[end:]


def render_all() -> dict[str, str]:
    return {"index.html": hub_page(), "atlas/index.html": atlas_page(), "rungs/index.html": rungs_page(),
            "deployments/index.html": deployments_page()}


def write() -> None:
    for name, text in render_all().items():
        target = PUBLIC_TEST / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(text.encode("utf-8"))
    print(f"wrote {len(render_all())} TEST page(s) in public/test")
    for board in matrices():
        for found in matrix_findings(board):
            print(f"  matrix {board.get('matrix_id')}: {found['point']} {found['where']}: {found['detail']}")


def check() -> list[str]:
    findings = []
    for name, text in render_all().items():
        target = PUBLIC_TEST / name
        if not target.is_file():
            findings.append(f"public/test/{name} is missing; run deploy_test.py pages")
        elif target.read_bytes() != text.encode("utf-8"):
            findings.append(f"public/test/{name} is stale; run deploy_test.py pages")
    return findings


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        findings = check()
        print("\n".join(findings) if findings else "TEST pages are current")
        return 1 if findings else 0
    write()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
