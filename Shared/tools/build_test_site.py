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

from Shared.library.resolve import build_index  # noqa: E402
from Shared.tools import atlas_index, build_test_question_bank, build_web_data, matrix_conformance, product_coverage, render_core, test_intake_registry, test_source_custody  # noqa: E402

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


def intake_banks() -> list[dict]:
    """Share the fail-closed identity gate with the TEST Question Bank producer."""
    return test_intake_registry.load_intake_banks(REPO)


def candidate_audits() -> list[dict]:
    audit_dir = TEST_ROOT / "candidates"
    if not audit_dir.is_dir():
        return []
    rows = []
    for path in sorted(audit_dir.glob("*.audit.json")):
        try:
            data = _json(path)
            if isinstance(data, dict) and data.get("schema_version") == "grade9v3-test-candidate-audit-v1":
                rows.append(data)
        except Exception:
            continue
    return rows


def owner_banks() -> list[dict]:
    bank_dir = TEST_ROOT / "question-bank"
    if not bank_dir.is_dir():
        return []
    banks = []
    for p in sorted(bank_dir.glob("*.json")):
        try:
            data = _json(p)
            if isinstance(data, dict) and data.get("schema_version") == "grade9v3-owner-supplied-bank-v1":
                banks.append(data)
        except Exception:
            continue
    return banks


def test_search_index() -> list[dict]:
    """TEST-only index: sourced READY means independent custody, not a stored workflow label."""
    custody = test_source_custody.reconcile(REPO)
    ready = set(custody["ready_ids"])
    held = set(custody["hold_ids"])
    rows: list[dict] = []
    for bank in intake_banks():
        for q in bank.get("questions", []):
            rows.append({
                "id": q.get("id"), "bank_id": bank.get("bank_id"), "kind": "OFFICIAL_INTAKE",
                "topic": q.get("topic_label"), "subtopic": q.get("subtopic_label"), "stem": q.get("stem"),
                "status": ("READY_FOR_BLUEPRINT" if q["id"] in ready else
                           "SOURCE_TEXT_HOLD" if q["id"] in held else "EVIDENCE_PENDING"),
                "difficulty": None, "demand": None,
            })
    for bank in owner_banks():
        for q in bank.get("questions", []):
            analysis = (q.get("extensions") or {}).get("grade9v3:analysis") or {}
            difficulty = analysis.get("difficulty") or {}
            demand = analysis.get("cognitive_demand") or {}
            rows.append({
                "id": q.get("id"), "bank_id": bank.get("bank_id"), "kind": "OWNER_SUPPLIED",
                "topic": analysis.get("topic"), "subtopic": analysis.get("concept_bucket"), "stem": q.get("stem"),
                "status": (q.get("answer") or {}).get("verification_status"),
                "difficulty": difficulty.get("band"),
                "demand": demand.get("primary") if isinstance(demand, dict) else demand,
            })
    return sorted(rows, key=lambda row: (str(row.get("bank_id") or ""), str(row.get("id") or "")))


def search_index_script(rows: list[dict]) -> str:
    payload = json.dumps(rows, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return f'<script type="application/json" id="g9-test-search-index">{payload}</script>'


def source_counts() -> dict:
    banks = sorted((TEST_ROOT / "question-bank").glob("*.json"))
    questions = sum(len(_json(p).get("questions") or []) for p in banks)
    intakes = intake_banks()
    intake_questions = sum(len(b.get("questions") or []) for b in intakes)
    return {
        "matrices": len(list((TEST_ROOT / "matrices").glob("*.rungs.json"))),
        "packages": len(list((TEST_ROOT / "library").glob("*.json"))),
        "banks": len(banks),
        "bank_questions": questions,
        "intake_banks": len(intakes),
        "intake_questions": intake_questions,
    }


# ------------------------------------------------------------------ page frame

def frame(depth: int, title: str, current: str, body: str, heading: str | None = None) -> str:
    root = "../" * depth
    home = root + "index.html"
    header = render_core.shell_header(home, root + "question-bank/index.html")
    # The shared product shell assumes a deeper product route for subject navigation.
    # TEST pages have depth 1 or 2: rebase only those three links to this page's root.
    for subject in ("physics", "chemistry", "mathematics"):
        assumed = f'href="../../../{subject}/index.html"'
        if assumed not in header:
            raise ValueError(f"TEST header lost its expected {subject} link")
        header = header.replace(assumed, f'href="{root}{subject}/index.html"')
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


BAR_STYLE = ("header[data-g9-test-banner]{display:flex;flex-wrap:wrap;gap:0 14px;align-items:center;padding:0 14px;"
             "background:#7c2d12;color:#fff;font:600 14px/1.4 system-ui,sans-serif}"
             "header[data-g9-test-banner] nav{display:flex;flex-wrap:wrap;gap:4px}"
             "header[data-g9-test-banner] a{display:inline-flex;align-items:center;min-height:48px;min-width:48px;"
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

def render_candidate_audit_section(audits: list[dict], custody: dict | None = None) -> str:
    if not audits:
        return ""
    # Old candidate audit receipts are immutable history, not present-day custody.
    # Project fresh custody facts without rewriting their recorded claims.
    if custody is None:
        custody = test_source_custody.reconcile(REPO)
    cards = []
    rank = {"PASS": 0, "NOT_APPLICABLE": 1, "PENDING": 2, "BLOCKED": 3}
    for audit in audits:
        checks = audit.get("checks") or {}
        legacy_note = ""
        if audit.get("candidate_id") == "NCERT-EXEMPLAR-G9-MATH-210":
            historical = audit.get("question_counts") or {}
            checks = dict(checks)
            checks["custody"] = {
                "status": "PENDING",
                "detail": ("The historical metadata PASS cannot verify official wording. "
                           f"Current source custody: {custody['ready_for_blueprint']} independently "
                           f"evidenced; {custody['source_text_hold']} source-text HOLD; "
                           f"{custody['evidence_pending']} awaiting evidence."),
            }
            counts_source = {
                "total": custody["total_intake"],
                "ready_for_blueprint": custody["ready_for_blueprint"],
                "source_text_hold": custody["source_text_hold"],
                "evidence_pending": custody["evidence_pending"],
            }
            legacy_note = (
                '<p class="g9-prov">Historical QA receipt (not current source authority): '
                f'{esc(historical.get("ready_for_blueprint", "?"))} previously labelled READY and '
                f'{esc(historical.get("duplicate_review", "?"))} duplicate-review. '
                'Present readiness is computed exclusively from source-custody evidence.</p>'
            )
        else:
            counts_source = audit.get("question_counts") or {}
        ordered = sorted(checks.items(), key=lambda item: (rank.get((item[1] or {}).get("status"), 9), item[0]))
        rows = "".join(
            f'<tr><td>{esc(name.replace("_", " ").title())}</td>'
            f'<td><strong>{esc((result or {}).get("status", "PENDING"))}</strong></td>'
            f'<td>{esc((result or {}).get("detail", ""))}</td></tr>'
            for name, result in ordered
        )
        counts = " · ".join(f"{esc(k.replace('_', ' '))}: {esc(v)}" for k, v in counts_source.items())
        promotion = audit.get("promotion") or {}
        origin = audit.get("origin") or {}
        origin_text = f'PR #{origin.get("pr")}' if origin.get("pr") else origin.get("type", "TEST")
        cards.append(card(
            f'candidate-{audit.get("candidate_id", "unknown")}',
            f'{audit.get("candidate_id", "")} {audit.get("title", "")} {audit.get("state", "")} '
            + " ".join(str((r or {}).get("status", "")) for r in checks.values()),
            f'<h2>QA candidate: {esc(audit.get("title") or audit.get("candidate_id"))}</h2>'
            f'<p class="g9-prov">{esc(audit.get("candidate_id"))} · {esc(origin_text)} · target {esc(audit.get("target_subject"))}'
            f'{(" / " + esc(audit.get("target_topic"))) if audit.get("target_topic") else ""}</p>'
            f'<p><strong>Lifecycle state:</strong> {esc(audit.get("state"))} · '
            f'<strong>Promotion:</strong> {esc(promotion.get("status", "BLOCKED"))} → {esc(promotion.get("target", ""))}</p>'
            f'{f"<p>{counts}</p>" if counts else ""}'
            f'<div class="g9-table-scroll"><table><thead><tr><th>Check</th><th>Status</th><th>Evidence / next action</th></tr></thead>'
            f'<tbody>{rows}</tbody></table></div>'
            f'<p class="g9-prov">Promotion reason: {esc(promotion.get("reason", ""))}</p>'
            + legacy_note
        ))
    return "".join(cards)


def render_owner_bank_section(banks: list[dict]) -> str:
    if not banks:
        return ""
    blocks = []
    for bank in banks:
        bank_id = bank.get("bank_id", "unknown")
        q_list = bank.get("questions", [])
        q_cards = []
        search_bits = ["owner bank", str(bank_id)]
        for q in q_list:
            qid = str(q.get("id", ""))
            stem = str(q.get("stem", ""))
            analysis = (q.get("extensions") or {}).get("grade9v3:analysis") or {}
            difficulty = analysis.get("difficulty") or {}
            demand = analysis.get("cognitive_demand") or {}
            primary = demand.get("primary") if isinstance(demand, dict) else demand
            secondary = demand.get("secondary", []) if isinstance(demand, dict) else []
            demand_text = ", ".join([str(x) for x in [primary, *secondary] if x])
            answer = q.get("answer") or {}
            summary = str(answer.get("summary", ""))
            verification = str(answer.get("verification_status", ""))
            custody = (q.get("extensions") or {}).get("grade9v3:source_custody") or {}
            search_bits.extend([qid, stem, str(analysis.get("topic", "")), str(analysis.get("concept_bucket", ""))])
            q_cards.append(
                f'<div style="border:1px solid #e2e8f0;border-radius:6px;padding:12px;margin:8px 0;background:#fff">'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;font-size:12px;margin-bottom:6px">'
                f'<span style="background:#7c3aed;color:#fff;padding:2px 6px;border-radius:4px">{esc(difficulty.get("band", "UNRATED"))} · score {esc(difficulty.get("score", ""))}</span>'
                f'<span style="background:#0369a1;color:#fff;padding:2px 6px;border-radius:4px">Demand: {esc(demand_text or "not analysed")}</span>'
                f'<span style="background:#16a34a;color:#fff;padding:2px 6px;border-radius:4px">{esc(verification or "NOT_RUN")}</span>'
                f'</div>'
                f'<p style="margin:0 0 6px 0"><strong>{esc(qid)}</strong> · {esc(q.get("original_identifier", ""))} · '
                f'<span class="g9-prov">{esc(custody.get("authority_class", "OWNER_SUPPLIED_RAW_INPUT"))} · {esc(custody.get("wording_custody", "VERBATIM"))}</span></p>'
                f'<p style="margin:0 0 6px 0">{esc(stem)}</p>'
                f'<details><summary>Inspect answer / verification evidence</summary><p>{esc(summary)}</p></details>'
                f'</div>'
            )
        blocks.append(card(
            f"owner-bank-{bank_id}",
            " ".join(search_bits),
            f'<h2>Owner Question Bank: {esc(bank_id)}</h2>'
            f'<p class="g9-prov">{len(q_list)} question(s) · owner-supplied custody · TEST-only preview · not accepted</p>'
            f'<p>This is the parked Core2 source bank. Inspect wording, difficulty/demand classification, answer reasoning and layout here before a TEST product is built.</p>'
            f'<details><summary>Inspect {len(q_list)} owner questions</summary>{"".join(q_cards)}</details>'
        ))
    return "".join(blocks)


INTAKE_HOME_FILTER_HTML = """<div data-g9-intake-controls style="display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,210px),1fr));gap:10px;margin:14px 0"><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Search staged questions<input type="search" data-g9-intake-search placeholder="Question, ID or topic" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Subject<select data-g9-intake-facet="subject" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All subjects</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Grade<select data-g9-intake-facet="grade" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All grades</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Source authority<select data-g9-intake-facet="authority" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All authorities</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Source kind<select data-g9-intake-facet="kind" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All source kinds</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Topic<select data-g9-intake-facet="topic" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All topics</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Subtopic<select data-g9-intake-facet="subtopic" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All subtopics</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Question type<select data-g9-intake-facet="type" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All types</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Intake state<select data-g9-intake-facet="intake" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All intake states</option></select></label><label style="display:grid;gap:4px;font-size:14px;font-weight:600">Blueprint readiness<select data-g9-intake-facet="blueprint" style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px"><option value="">All readiness states</option></select></label><button type="button" data-g9-intake-reset style="min-height:48px;width:100%;min-width:0;padding:8px;border:1px solid #64748b;border-radius:8px;cursor:pointer">Clear intake filters</button></div><p data-g9-intake-count aria-live="polite" style="font-size:14px"></p>"""
INTAKE_HOME_FILTER_SCRIPT = """<script src="question-bank/questions.js"></script><script>
(() => {
  const projection = window.G9_TEST_QUESTION_BANK || { banks: [] };
  const byId = new Map(projection.banks.flatMap(bank => bank.questions || []).map(q => [q.id, q]));
  const blueprint = q => q.custody_evidence_status === "INDEPENDENTLY_EVIDENCED" ? "READY_FOR_BLUEPRINT"
    : q.custody_evidence_status === "SOURCE_TEXT_HOLD" ? "SOURCE_TEXT_HOLD" : "EVIDENCE_PENDING";
  const dimensions = [
    ["subject", q => q.subject || "Unknown"],
    ["grade", q => String(q.grade ?? "Unknown")],
    ["authority", q => q.source_authority || "Unknown"],
    ["kind", q => q.source_kind || "Unknown"],
    ["topic", q => q.topic_label || "Unknown"],
    ["subtopic", q => q.subtopic_label || "Not labelled"],
    ["type", q => q.question_type || "Unknown"],
    ["intake", q => q.custody_evidence_status === "SOURCE_TEXT_HOLD" ? "SOURCE_TEXT_HOLD" : "TEST_VISIBLE"],
    ["blueprint", blueprint],
  ];
  for (const bank of document.querySelectorAll('article[data-g9-unit^="intake-"]')) {
    const container = bank.querySelector("[data-g9-intake-controls]");
    const count = bank.querySelector("[data-g9-intake-count]");
    if (!container || !count) continue;
    const cards = [...bank.querySelectorAll('details > div[style*="border:1px"]')];
    const rows = cards.map(el => {
      const id = el.querySelector("p strong")?.textContent?.trim();
      const q = byId.get(id);
      if (!q) throw new Error("TEST intake source projection missing " + id);
      const values = Object.fromEntries(dimensions.map(([key, get]) => [key, get(q)]));
      el.dataset.g9IntakeSourceId = q.id;
      return { el, values, search: [q.id, q.original_identifier, q.stem, q.topic_label,
        q.subtopic_label, q.chapter_or_unit, q.question_type].join(" ").toLowerCase() };
    });
    const facets = [...container.querySelectorAll("[data-g9-intake-facet]")];
    for (const select of facets) {
      const key = select.dataset.g9IntakeFacet;
      const distinct = [...new Set(rows.map(row => row.values[key]))].sort((a,b) => a.localeCompare(b));
      for (const value of distinct) {
        const option = document.createElement("option");
        option.value = value;
        option.textContent = value.replaceAll("_", " ");
        select.append(option);
      }
    }
    const search = container.querySelector("[data-g9-intake-search]");
    const apply = () => {
      const query = search.value.trim().toLowerCase();
      let shown = 0;
      for (const row of rows) {
        const ok = (!query || row.search.includes(query)) &&
          facets.every(select => !select.value || row.values[select.dataset.g9IntakeFacet] === select.value);
        row.el.hidden = !ok;
        if (ok) shown++;
      }
      count.textContent = shown + " of " + rows.length + " official questions shown";
    };
    search.addEventListener("input", apply);
    facets.forEach(select => select.addEventListener("change", apply));
    container.querySelector("[data-g9-intake-reset]").addEventListener("click", () => {
      search.value = "";
      facets.forEach(select => { select.value = ""; });
      apply();
      search.focus();
    });
    apply();
  }
})();
</script>"""


def render_intake_section(intakes: list[dict], custody: dict) -> str:
    ready = {row["intake_question_ref"]: row for row in custody["handoff"]}
    held = set(custody["hold_ids"])
    if not intakes:
        return ""
    blocks = []
    for bank in intakes:
        bank_id = bank.get("bank_id", "unknown")
        q_list = bank.get("questions", [])
        topics: dict[str, int] = {}
        for q in q_list:
            t = q.get("topic_label", "Unknown")
            topics[t] = topics.get(t, 0) + 1

        topic_summary = " · ".join(f"{esc(t)} ({cnt})" for t, cnt in sorted(topics.items()))

        q_cards = []
        for q in q_list:
            qid = q.get("id", "")
            stem = q.get("stem", "")
            opts = q.get("options") or []
            opts_html = "".join(f"<li>{esc(o)}</li>" for o in opts)
            opts_block = f"<ul style='margin:4px 0 8px 18px'>{opts_html}</ul>" if opts_html else ""
            source = ready.get(qid)
            ans_text = q.get("official_answer_text", "")
            key_evidenced = bool(source and source.get("official_answer_key_ref"))
            answer_label = ("Evidenced official answer" if key_evidenced
                            else "Recorded answer — official key custody pending")
            ans_block = (f"<p><strong>{answer_label}:</strong> {esc(ans_text)} "
                         f"<em>({esc(q.get('answer_key_locator', ''))})</em></p>") if ans_text else ""
            src_url = q.get("source_url", "")
            pdf_name = src_url.rsplit("/", 1)[-1] if src_url else ""
            evidence_state = ("SOURCE EVIDENCED" if source else
                              "SOURCE TEXT HOLD" if qid in held else "EVIDENCE PENDING")
            verified_page = source["source_locator"] if source else None
            page_note = (f' · Printed page {verified_page["printed_page"]} / PDF index {verified_page["pdf_page_index"]}'
                         if verified_page else ' · Exact official page not independently reconciled')
            safe_href = esc(src_url).replace("https:", "https&#58;")
            src_link = (f' · <a href="{safe_href}" target="_blank" rel="noopener noreferrer" '
                        f'style="display:inline-flex;min-height:48px;align-items:center">Official source PDF: {esc(pdf_name)}</a>'
                        f'<span class="g9-prov">{page_note}</span>') if pdf_name else ""

            q_cards.append(
                f'<div style="border:1px solid #e2e8f0;border-radius:6px;padding:12px;margin:8px 0;background:#fff">'
                f'<div style="display:flex;gap:8px;flex-wrap:wrap;font-size:12px;margin-bottom:6px">'
                f'<span style="background:#0284c7;color:#fff;padding:2px 6px;border-radius:4px">{esc(q.get("topic_label", ""))}</span>'
                f'<span style="background:#16a34a;color:#fff;padding:2px 6px;border-radius:4px">{esc(evidence_state)}</span>'
                f'<span style="background:#64748b;color:#fff;padding:2px 6px;border-radius:4px">Difficulty: not analysed</span>'
                f'<span style="background:#64748b;color:#fff;padding:2px 6px;border-radius:4px">Demand: not analysed</span>'
                f'</div>'
                f'<p style="margin:0 0 6px 0"><strong>{esc(qid)}</strong> ({esc(q.get("chapter_or_unit", ""))} · {esc(q.get("exercise_or_section", ""))} · Q{esc(q.get("question_number", ""))}){src_link}</p>'
                f'<p style="margin:0 0 6px 0">{esc(stem)}</p>'
                f'{opts_block}'
                f'{ans_block}'
                f'</div>'
            )

        all_q_html = "".join(q_cards)

        blocks.append(card(
            f"intake-{bank_id}",
            " ".join([
                "intake", str(bank_id), *topics.keys(), "stage-1 official questions",
                *(str(q.get("id", "")) for q in q_list),
                *(str(q.get("stem", "")) for q in q_list),
                *(str(q.get("subtopic_label", "")) for q in q_list),
            ]),
            f'<h2>Stage-1 Question Intake: {esc(bank_id)}</h2>'
            f'<p class="g9-prov">Source scope: {esc(", ".join(bank.get("source_scope", [])))} · {len(q_list)} question(s) · '
            f'Independent source custody: {sum(q["id"] in ready for q in q_list)} READY_FOR_BLUEPRINT · '
            f'{sum(q["id"] in held for q in q_list)} SOURCE_TEXT_HOLD · '
            f'{sum(q["id"] not in ready and q["id"] not in held for q in q_list)} EVIDENCE_PENDING · historical intake labels are not authority</p>'
            f'<p>Official questions ingested from <em>{esc(bank.get("created_from", "official source"))}</em>. '
            f'Independent official-document witnesses currently cover only the separately reconciled records; '
            f'a stored stem digest or historical verification label alone does not establish official custody. '
            f'Academic blueprinting (difficulty bands D1–D4, cognitive demand, QRT cells, worked solutions) is deferred.</p>'
            f'<p><strong>Topics:</strong> {topic_summary}</p>'
            f'<details><summary>Inspect {len(q_list)} parked intake questions</summary>{INTAKE_HOME_FILTER_HTML}{all_q_html}</details>'
        ))
    return "".join(blocks)


def hub_page() -> str:
    deployed = products()
    pages = interactive_pages()
    counts = source_counts()
    intakes = intake_banks()
    custody = test_source_custody.reconcile(REPO)
    owner = owner_banks()
    search_rows = test_search_index()
    audits = candidate_audits()

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
        'an <strong>explorer</strong> for the toughest concept of the same question set, and each lands here as a labelled draft. Nothing here is reviewed, '
        'accepted or curriculum, and <code>accept_product.py</code> refuses TEST.</p>'
        '<p class="g9-prov">A gap count of 0 means the depth check found nothing missing. It counts what is absent, '
        'not how good it is, and it does not say the content has been reviewed.</p>'
        + render_candidate_audit_section(audits, custody)
        + render_intake_section(intakes, custody)
        + render_owner_bank_section(owner)
        + stage(1, "Core2", "Owner-supplied questions, preserved verbatim", core2)
        + stage(2, "Core1A", "Concept construction for the same topic", core1a)
        + stage(3, "Explorer", "A guided page on the toughest concept of the same question set", inter)
        + card("places", "atlas rungs deployments",
               '<h2>Where things are</h2><ul>'
               f'<li>{link("question-bank/index.html", "Question Bank")}: parked source questions, explicitly unvalidated for academic admission</li>'
               f'<li>{link("atlas/index.html", "Atlas")}: the Topic Atlas for the TEST matrix</li>'
               f'<li>{link("rungs/index.html", "Rungs")}: the ladder, rung by rung</li>'
               f'<li>{link("deployments/index.html", "Deployments")}: every deployed draft, with its digest and gaps</li></ul>')
        + card("sources", "matrices packages question bank intake",
               f'<h2>Sources in this repository</h2><ul><li>{counts["matrices"]} rung matrix file(s) in TEST/matrices</li>'
               f'<li>{counts["packages"]} package file(s) in TEST/library</li>'
               f'<li>{counts["banks"]} owner-supplied question file(s) in TEST/question-bank, {counts["bank_questions"]} question(s)</li>'
               f'<li>{counts["intake_banks"]} official intake bank(s) in TEST/question-bank/intake, {counts["intake_questions"]} question(s)</li>'
               f'<li>{len(audits)} candidate QA record(s) in TEST/candidates</li>'
               f'<li>TEST-only search index: {len(search_rows)} parked question(s); production search untouched</li></ul>'
               '<p class="g9-prov">How to add each of them: TEST/README.md in the repository.</p>')
        + search_index_script(search_rows) + INTAKE_HOME_FILTER_SCRIPT)
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
        pdfs = (r.get("pdf") or {})
        copies = [(name, label) for name, label in present if name.replace(".html", ".pdf") in (pdfs.get("files") or {})]
        pdf_line = (" · ".join(link(f'../products/{r["slug"]}/{name.replace(".html", ".pdf")}', f"{label} (PDF)") for name, label in copies)
                    if copies else "")
        pdf_block = (f'<p>Print copies: {pdf_line}</p>' if pdf_line
                     else f'<p class="g9-prov">No PDF copies: {esc(pdfs.get("reason") or "this deploy printed none")}.</p>' if pdfs else "")
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
        cover = r.get("coverage") or {}
        cover_lines = product_coverage.summary_lines(cover)[1:] if cover.get("cores") else []
        cover_block = ('<p class="g9-prov">Coverage of what the library holds: ' + esc(" | ".join(line.strip() for line in cover_lines)) + '</p>'
                       if cover_lines else "")
        hardest = r.get("toughest")
        hardest_line = (f'<p>Toughest concept (what Core1A and the interactive page are built for): {esc(hardest["label"])} · '
                        f'{esc(hardest["band"])} · {esc(hardest.get("microtopic_title") or hardest.get("microtopic_ref") or "no concept book")}'
                        f'{" · the move learners miss: " + esc(hardest["crux_move"]["action"]) if hardest.get("crux_move") else ""}</p>'
                        if hardest else "")
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
                     f'<p>{links}</p>{pdf_block}{cover_block}<p>Selected records: {esc(counts)}. Gaps: {esc(gaps)} ({r["gap_count"]} in total).</p>{hardest_line}{gap_details}{advice_details}{waived_details}{quality_details}{empty}')
    for r in pages:
        built = r.get("built_by") == "EXPLORER_BUILDER"
        how = ("Built by the explorer builder from a spec: every number on it is computed, and was checked at every position of the sliders."
               if built else "Written by hand: nothing in it is machine-checked, and it is not built from the explorer blueprint.")
        hardest = r.get("toughest")
        target = (f'<p>Built for the toughest concept of the set: {esc(hardest["label"])} · {esc(hardest["band"])} · '
                  f'{esc(hardest.get("microtopic_title") or "no concept book")}</p>' if built and hardest else "")
        gaps = r.get("gaps") or []
        gap_list = "".join(f'<li>{esc(g["component"])} · {esc(g["where"])}: {esc(g["detail"])}</li>' for g in gaps)
        gap_details = (f'<details><summary>The {len(gaps)} gap(s): where the page is shallower than the blueprint asks</summary><ul>{gap_list}</ul></details>'
                       if gaps else ('<p class="g9-prov">No gap against the blueprint. That counts what is absent, not how good it is.</p>' if built else ""))
        checks = r.get("checks") or {}
        contract = r.get("design_contract") or {}
        evidence = (f'<p class="g9-prov">Checked at {checks.get("states_checked", 0)} positions of the sliders; design contract '
                    f'{esc(contract.get("conformance_status", ""))}, audit {esc(contract.get("audit_status", "").replace("_", " ").lower())}; '
                    f'{link("../interactive/" + r["slug"] + "/explorer-evidence.json", "evidence")} · '
                    f'{link("../interactive/" + r["slug"] + "/explorer-contract.json", "contract")}</p>' if built else "")
        links = r.get("links") or {}
        back = (f'<p>{link("../interactive/" + r["slug"] + "/" + links["question"], "The question it returns to")}</p>' if links.get("question") else "")
        body += card(f'interactive-{r["slug"]}', f'{r["slug"]} {r["title"]} {r["purpose"]} interactive',
                     f'<h2>{esc(r["title"])}</h2><p class="g9-prov">Interactive page {esc(r["slug"])} · DRAFT · accepted: no · '
                     f'blueprint {esc(r["blueprint_ref"])}</p><p>{esc(r["purpose"])}</p><p>{esc(how)}</p>{target}'
                     f'<p>{link("../interactive/" + r["slug"] + "/index.html", "Open the page")} · built from '
                     f'{esc(", ".join(r["records"]))}</p>{back}{gap_details}{evidence}')
    if not body:
        body = '<p>Nothing is deployed yet.</p><p class="g9-prov">deploy_test.py product / interactive puts drafts here.</p>'
    return frame(2, "Deployments", "deployments/index.html", body)


ATLAS_TRANSFORM = REPO / "Shared" / "web" / "atlas-sandbox-transform.v1.json"


def atlas_subject_payload() -> dict:
    """Build only the TEST subject's Atlas read model.

    Production data.js stays untouched. Core destinations are intentionally unavailable until
    a TEST product is actually deployed; the Atlas can still inspect the package/matrix mapping.
    """
    packages = [_json(p) for p in sorted((TEST_ROOT / "library").glob("*.json"))]
    records = build_index(packages) if packages else {}
    empty_core = {"bucket_availability": [], "core_projections": []}
    entry = {
        "matrices": build_web_data.matrix_summary("TEST", records),
        "library_available": bool(packages),
    }
    entry.update(atlas_index.build_subject_index("TEST", matrices(), records, empty_core))
    return entry


def atlas_data_script() -> str:
    """Inline TEST-local Atlas projection without mutating production data/search."""
    payload = json.dumps(atlas_subject_payload(), ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    return ("<script data-g9-test-atlas-data>"
            "window.GRADE9V3=window.GRADE9V3||{subjects:{}};"
            "window.GRADE9V3.subjects=window.GRADE9V3.subjects||{};"
            f"window.GRADE9V3.subjects.TEST={payload};"
            "</script>")


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
    text = text[:init] + ATLAS_INIT + text[end:]
    marker = '<script src="../../data/data.js"></script>'
    if text.count(marker) != 1:
        raise ValueError("the Topic Atlas template changed: its global data script moved")
    return text.replace(marker, marker + "\n" + atlas_data_script(), 1)


def question_bank_page() -> str:
    return build_test_question_bank.render_page(REPO)


def render_all() -> dict[str, str]:
    return {"index.html": hub_page(), "question-bank/index.html": question_bank_page(),
            "question-bank/questions.js": build_test_question_bank.render_data(REPO),
            "atlas/index.html": atlas_page(), "rungs/index.html": rungs_page(),
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
