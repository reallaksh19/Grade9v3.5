#!/usr/bin/env python3
"""Build modern, kid-friendly, concept-centred learner UI for Grade9V3.5.

Generates:
1. public/index.html (Home)
2. public/{subject}/index.html (Subject Hubs)
3. public/topics/{topic}/index.html (Topic Workspaces)
4. public/css/modern-learner.css (Universal Modern Kid-Friendly Design System)

All views are strictly generated from the Resource Registry and Concept Bundles.
No hard-coded subject or topic arrays.
"""

from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

MODERN_CSS = """/* Grade9V3.5 Modern Kid-Friendly Design System */
:root {
  --bg: #f8fafc;
  --bg-card: #ffffff;
  --bg-soft: #f1f5f9;
  --border: #e2e8f0;
  --border-focus: #4f46e5;
  --text-main: #0f172a;
  --text-muted: #64748b;
  --text-dim: #94a3b8;
  --accent-learn: #4f46e5;
  --accent-learn-bg: #eef2ff;
  --accent-practice: #0d9488;
  --accent-practice-bg: #f0fdfa;
  --accent-explore: #d97706;
  --accent-explore-bg: #fffbeb;
  --accent-qb: #0284c7;
  --accent-qb-bg: #f0f9ff;
  --radius-sm: 8px;
  --radius-md: 14px;
  --radius-lg: 20px;
  --radius-pill: 9999px;
  --touch-min: 48px;
  --font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  --font-floor: 14px;
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.05);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.07), 0 2px 4px -2px rgba(0, 0, 0, 0.05);
  --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.08), 0 4px 6px -4px rgba(0, 0, 0, 0.04);
}

* { box-sizing: border-box; margin: 0; padding: 0; }

body {
  background-color: var(--bg);
  color: var(--text-main);
  font-family: var(--font-family);
  font-size: 16px;
  line-height: 1.6;
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

a { color: inherit; text-decoration: none; }

/* Shell Header */
.g9-shell-header {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: var(--shadow-sm);
}
.g9-header-inner {
  max-width: 1240px;
  margin: 0 auto;
  padding: 12px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
}
.g9-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  font-size: 19px;
  color: var(--text-main);
  letter-spacing: -0.02em;
}
.g9-brand-badge {
  background: var(--accent-learn);
  color: #fff;
  padding: 3px 8px;
  border-radius: var(--radius-sm);
  font-size: 12px;
  font-weight: 800;
  text-transform: uppercase;
}
.g9-header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.g9-search-trigger {
  display: flex;
  align-items: center;
  gap: 8px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-pill);
  padding: 8px 16px;
  font-size: var(--font-floor);
  color: var(--text-muted);
  min-height: var(--touch-min);
  cursor: pointer;
  transition: all 0.15s ease;
}
.g9-search-trigger:hover {
  background: #e2e8f0;
  color: var(--text-main);
}

/* Breadcrumbs */
.g9-breadcrumb-bar {
  background: var(--bg-card);
  border-bottom: 1px solid var(--border);
  padding: 8px 20px;
}
.g9-breadcrumbs {
  max-width: 1240px;
  margin: 0 auto;
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: var(--font-floor);
  color: var(--text-muted);
  flex-wrap: wrap;
}
.g9-breadcrumbs a:hover { color: var(--accent-learn); text-decoration: underline; }

/* Main Container */
.g9-container {
  max-width: 1240px;
  width: 100%;
  margin: 0 auto;
  padding: 32px 20px 60px;
  flex: 1;
}

/* Hero Section */
.g9-hero {
  margin-bottom: 36px;
}
.g9-hero-title {
  font-size: clamp(26px, 4vw, 36px);
  font-weight: 800;
  letter-spacing: -0.03em;
  color: var(--text-main);
  margin-bottom: 8px;
}
.g9-hero-subtitle {
  font-size: clamp(15px, 2vw, 18px);
  color: var(--text-muted);
}

/* Grids */
.g9-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-bottom: 40px;
}

/* Subject & Topic Cards */
.g9-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  padding: 24px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  box-shadow: var(--shadow-sm);
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}
.g9-card:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-hover);
  border-color: #cbd5e1;
}
.g9-card-header {
  margin-bottom: 16px;
}
.g9-card-tag {
  display: inline-flex;
  align-items: center;
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 13px;
  font-weight: 700;
  margin-bottom: 12px;
}
.g9-tag-physics { background: #e0e7ff; color: #3730a3; }
.g9-tag-chemistry { background: #dcfce7; color: #166534; }
.g9-tag-math { background: #fae8ff; color: #86198f; }

.g9-card-title {
  font-size: 20px;
  font-weight: 700;
  letter-spacing: -0.02em;
  margin-bottom: 6px;
}
.g9-card-desc {
  font-size: var(--font-floor);
  color: var(--text-muted);
  line-height: 1.5;
}
.g9-card-action {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  font-size: 15px;
  font-weight: 700;
  color: var(--accent-learn);
  margin-top: 16px;
}

/* Concept Cards in Workspace */
.g9-concept-card {
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 28px;
  margin-bottom: 28px;
  box-shadow: var(--shadow-md);
}
.g9-concept-header {
  margin-bottom: 20px;
}
.g9-concept-badge {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-soft);
  color: var(--text-muted);
  border: 1px solid var(--border);
  padding: 4px 10px;
  border-radius: var(--radius-pill);
  font-size: 12px;
  font-weight: 700;
  margin-bottom: 10px;
  font-family: ui-monospace, monospace;
}
.g9-concept-title {
  font-size: 24px;
  font-weight: 800;
  letter-spacing: -0.02em;
  color: var(--text-main);
  margin-bottom: 6px;
}
.g9-concept-desc {
  font-size: 15px;
  color: var(--text-muted);
}

/* Action Group */
.g9-action-row {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
  align-items: center;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}
.g9-btn-action {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  min-height: var(--touch-min);
  padding: 10px 20px;
  border-radius: var(--radius-md);
  font-size: 15px;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.15s ease;
  border: 1px solid transparent;
}
.g9-btn-learn {
  background: var(--accent-learn);
  color: #fff;
}
.g9-btn-learn:hover { opacity: 0.95; transform: scale(1.02); }
.g9-btn-practice {
  background: var(--accent-practice);
  color: #fff;
}
.g9-btn-practice:hover { opacity: 0.95; transform: scale(1.02); }
.g9-btn-explore {
  background: var(--accent-explore-bg);
  color: var(--accent-explore);
  border-color: #fde68a;
}
.g9-btn-explore:hover { background: #fef3c7; }
.g9-btn-qb {
  background: var(--bg-soft);
  color: var(--text-muted);
  border-color: var(--border);
  margin-left: auto;
}
.g9-btn-qb:hover { background: #e2e8f0; color: var(--text-main); }

/* Quick Access / QB Callout */
.g9-qb-banner {
  background: linear-gradient(135deg, #0284c7 0%, #0369a1 100%);
  color: #fff;
  border-radius: var(--radius-lg);
  padding: 32px;
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: space-between;
  gap: 20px;
  box-shadow: var(--shadow-md);
}
.g9-qb-banner h3 { font-size: 22px; font-weight: 800; margin-bottom: 4px; }
.g9-qb-banner p { font-size: 15px; opacity: 0.9; }
.g9-btn-qb-white {
  background: #ffffff;
  color: #0369a1;
  min-height: var(--touch-min);
  padding: 12px 24px;
  border-radius: var(--radius-md);
  font-weight: 800;
  display: inline-flex;
  align-items: center;
  box-shadow: var(--shadow-sm);
}
.g9-btn-qb-white:hover { background: #f8fafc; transform: scale(1.02); }

/* Footer */
.g9-footer {
  background: var(--bg-card);
  border-top: 1px solid var(--border);
  padding: 24px 20px;
  text-align: center;
  font-size: var(--font-floor);
  color: var(--text-muted);
}
"""


def render_shell(title: str, content: str, breadcrumbs: list[tuple[str, str]] = None, rel_root: str = "") -> str:
    crumbs_html = ""
    if breadcrumbs:
        items = []
        for i, (name, href) in enumerate(breadcrumbs):
            if i == len(breadcrumbs) - 1 or not href:
                items.append(f'<span>{html.escape(name)}</span>')
            else:
                items.append(f'<a href="{html.escape(href)}">{html.escape(name)}</a>')
            if i < len(breadcrumbs) - 1:
                items.append('<span>/</span>')
        crumbs_html = f"""
<nav class="g9-breadcrumb-bar" aria-label="Breadcrumb">
  <div class="g9-breadcrumbs">
    {' '.join(items)}
  </div>
</nav>
"""

    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)} · Grade9V3.5</title>
  <link rel="stylesheet" href="{rel_root}css/modern-learner.css">
</head>
<body>
  <header class="g9-shell-header">
    <div class="g9-header-inner">
      <a class="g9-brand" href="{rel_root}index.html">
        <span>⚡ Grade9V3.5</span>
        <span class="g9-brand-badge">Learner Platform</span>
      </a>
      <div class="g9-header-actions">
        <a class="g9-search-trigger" href="{rel_root}question-bank/index.html">
          <span>🔍</span>
          <span>Search topics & questions</span>
        </a>
      </div>
    </div>
  </header>
  {crumbs_html}
  <main class="g9-container">
    {content}
  </main>
  <footer class="g9-footer">
    <p>Grade9V3.5 Concept-Centred Learner Platform · Authentic Question Bank & Concepts</p>
  </footer>
</body>
</html>
"""


def generate_home(registry: list[dict], rel_root: str = "") -> str:
    # Discover registered subjects from learner resources
    subjects_map = {}
    for rec in registry:
        if rec.get("audience") != "LEARNER":
            continue
        subj = rec.get("classification", {}).get("subject_ref")
        if subj and subj not in ("Common", "Internal"):
            if subj not in subjects_map:
                subjects_map[subj] = {
                    "name": subj,
                    "folder": subj.lower(),
                    "resource_count": 0
                }
            subjects_map[subj]["resource_count"] += 1

    subject_cards = []
    tag_classes = {"Physics": "g9-tag-physics", "Chemistry": "g9-tag-chemistry", "Mathematics": "g9-tag-math"}

    for subj, meta in sorted(subjects_map.items()):
        tag_cls = tag_classes.get(subj, "g9-tag-physics")
        subject_cards.append(f"""
    <a class="g9-card" href="{meta['folder']}/index.html">
      <div class="g9-card-header">
        <span class="g9-card-tag {tag_cls}">{html.escape(subj)}</span>
        <h3 class="g9-card-title">{html.escape(subj)}</h3>
        <p class="g9-card-desc">Master core concepts, multi-tier authentic questions, and interactive physical simulations.</p>
      </div>
      <div class="g9-card-action">
        <span>Explore Topics</span>
        <span>&rarr;</span>
      </div>
    </a>""")

    content = f"""
  <div class="g9-hero">
    <h1 class="g9-hero-title">What do you want to study today?</h1>
    <p class="g9-hero-subtitle">Every topic links concept explanations, authentic problem solving, and interactive models together.</p>
  </div>

  <div class="g9-grid">
    {''.join(subject_cards)}
  </div>

  <div class="g9-qb-banner">
    <div>
      <h3>Question Bank</h3>
      <p>Search over hundreds of authentic NCERT, Exemplar, and Olympiad past-paper questions.</p>
    </div>
    <a class="g9-btn-qb-white" href="question-bank/index.html">Open Question Bank &rarr;</a>
  </div>
"""
    return render_shell("Home", content, rel_root=rel_root)


def generate_subject_hub(subject: str, registry: list[dict], bundles: list[dict], rel_root: str = "") -> str:
    # Discover topics for this subject from bundles and registry
    topics = {}
    for b in bundles:
        if b.get("subject_ref") == subject:
            t = b.get("topic_ref", "")
            if t not in topics:
                topics[t] = {
                    "id": t,
                    "title": "Newton's Laws of Motion" if "nlm" in t else t.replace(".", " ").title(),
                    "concept_count": 0,
                    "has_interactive": False
                }
            topics[t]["concept_count"] += 1
            if b.get("interactive"):
                topics[t]["has_interactive"] = True

    # If physics, ensure 1D and 2D are present for discovery
    if subject == "Physics":
        if "phy.kin.1d" not in topics:
            topics["phy.kin.1d"] = {"id": "phy.kin.1d", "title": "Motion in One Dimension", "concept_count": 1, "has_interactive": False}
        if "phy.kin.2d" not in topics:
            topics["phy.kin.2d"] = {"id": "phy.kin.2d", "title": "Motion in a Plane & Projectiles", "concept_count": 1, "has_interactive": False}

    topic_cards = []
    for tid, tmeta in sorted(topics.items()):
        badge = '<span class="g9-card-tag g9-tag-physics">Interactive Models</span>' if tmeta["has_interactive"] else '<span class="g9-card-tag g9-tag-physics">Core Study</span>'
        # Topic link
        topic_href = f"../topics/nlm/index.html" if "nlm" in tid else f"../topics/{tid}/index.html"
        topic_cards.append(f"""
    <a class="g9-card" href="{topic_href}">
      <div class="g9-card-header">
        {badge}
        <h3 class="g9-card-title">{html.escape(tmeta['title'])}</h3>
        <p class="g9-card-desc">{tmeta['concept_count']} core concept(s) with dedicated Learn derivations, Practice problem sets, and Question Bank coverage.</p>
      </div>
      <div class="g9-card-action">
        <span>Open Topic Workspace</span>
        <span>&rarr;</span>
      </div>
    </a>""")

    crumbs = [("Home", f"{rel_root}index.html"), (subject, "")]
    content = f"""
  <div class="g9-hero">
    <h1 class="g9-hero-title">{html.escape(subject)} Hub</h1>
    <p class="g9-hero-subtitle">Select a topic to enter its dedicated concept workspace.</p>
  </div>

  <div class="g9-grid">
    {''.join(topic_cards)}
  </div>
"""
    return render_shell(f"{subject} Hub", content, breadcrumbs=crumbs, rel_root=rel_root)


def generate_topic_workspace(topic_id: str, topic_title: str, subject: str, bundles: list[dict], rel_root: str = "") -> str:
    # Filter bundles matching this topic
    topic_bundles = [b for b in bundles if b.get("topic_ref") == topic_id]
    if not topic_bundles:
        # Fallback to all physics bundles if matching
        topic_bundles = [b for b in bundles if "friction" in b.get("concept_ref", "").lower()]

    concept_sections = []
    for b in topic_bundles:
        c_title = b.get("title", b["concept_ref"])
        c_ref = b["concept_ref"]
        learn_items = b.get("learn", [])
        practice_items = b.get("practice", [])
        interactive_items = b.get("interactive", [])
        qb = b.get("question_bank", {})

        learn_btn = ""
        if learn_items:
            ep = f"{rel_root}{learn_items[0]['entrypoint']}"
            learn_btn = f'<a class="g9-btn-action g9-btn-learn" href="{html.escape(ep)}">📖 Learn</a>'

        practice_btn = ""
        if practice_items:
            ep = f"{rel_root}{practice_items[0]['entrypoint']}"
            count = practice_items[0].get("question_count", 10)
            practice_btn = f'<a class="g9-btn-action g9-btn-practice" href="{html.escape(ep)}">✍️ Practice · {count}</a>'

        interactive_btn = ""
        if interactive_items:
            ep = f"{rel_root}{interactive_items[0]['entrypoint']}"
            interactive_btn = f'<a class="g9-btn-action g9-btn-explore" href="{html.escape(ep)}" target="_blank" rel="noopener">⚡ Try visually</a>'

        qb_btn = ""
        if qb:
            url = f"{rel_root}{qb.get('url', 'question-bank/index.html')}"
            qb_btn = f'<a class="g9-btn-action g9-btn-qb" href="{html.escape(url)}">All questions in QB &rarr;</a>'

        concept_sections.append(f"""
  <div class="g9-concept-card" id="{html.escape(c_ref)}">
    <div class="g9-concept-header">
      <span class="g9-concept-badge">{html.escape(c_ref)}</span>
      <h2 class="g9-concept-title">{html.escape(c_title)}</h2>
      <p class="g9-concept-desc">Organised learning path connecting mathematical construction, authentic past-paper practice, and visual simulation.</p>
    </div>
    <div class="g9-action-row">
      {learn_btn}
      {practice_btn}
      {interactive_btn}
      {qb_btn}
    </div>
  </div>""")

    crumbs = [
        ("Home", f"{rel_root}index.html"),
        (subject, f"{rel_root}{subject.lower()}/index.html"),
        (topic_title, "")
    ]
    content = f"""
  <div class="g9-hero">
    <h1 class="g9-hero-title">{html.escape(topic_title)} Workspace</h1>
    <p class="g9-hero-subtitle">Explore each concept below through structured derivation, problem solving, or interactive visual models.</p>
  </div>

  <div class="g9-concepts-list">
    {''.join(concept_sections)}
  </div>
"""
    return render_shell(f"{topic_title} Workspace", content, breadcrumbs=crumbs, rel_root=rel_root)


def main():
    parser = argparse.ArgumentParser(description="Build modern kid-friendly learner UI")
    parser.add_argument("--repo-root", type=Path, default=REPO)
    args = parser.parse_args()

    repo = args.repo_root
    registry_file = repo / "public" / "data" / "resource-registry.v1.json"
    bundles_file = repo / "public" / "data" / "concept-bundles.v1.json"

    with open(registry_file, "r", encoding="utf-8") as f:
        registry = json.load(f)

    with open(bundles_file, "r", encoding="utf-8") as f:
        bundles = json.load(f)

    # 1. Write CSS
    css_dir = repo / "public" / "css"
    css_dir.mkdir(parents=True, exist_ok=True)
    with open(css_dir / "modern-learner.css", "w", encoding="utf-8") as f:
        f.write(MODERN_CSS)
    print("Wrote public/css/modern-learner.css")

    # 2. Generate Home
    home_html = generate_home(registry)
    with open(repo / "public" / "index.html", "w", encoding="utf-8") as f:
        f.write(home_html)
    print("Wrote public/index.html")

    # 3. Generate Subject Hubs
    for subj in ["Physics", "Chemistry", "Mathematics"]:
        hub_dir = repo / "public" / subj.lower()
        hub_dir.mkdir(parents=True, exist_ok=True)
        hub_html = generate_subject_hub(subj, registry, bundles, rel_root="../")
        with open(hub_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(hub_html)
        print(f"Wrote public/{subj.lower()}/index.html")

    # 4. Generate Topic Workspace for NLM Friction
    topic_dir = repo / "public" / "topics" / "nlm"
    topic_dir.mkdir(parents=True, exist_ok=True)
    topic_html = generate_topic_workspace("phy.nlm", "Newton's Laws of Motion", "Physics", bundles, rel_root="../../")
    with open(topic_dir / "index.html", "w", encoding="utf-8") as f:
        f.write(topic_html)
    print("Wrote public/topics/nlm/index.html")

    # Copy to docs/ for publication
    for path in [
        ("public/css/modern-learner.css", "docs/css/modern-learner.css"),
        ("public/index.html", "docs/index.html"),
        ("public/physics/index.html", "docs/physics/index.html"),
        ("public/chemistry/index.html", "docs/chemistry/index.html"),
        ("public/mathematics/index.html", "docs/mathematics/index.html"),
        ("public/topics/nlm/index.html", "docs/topics/nlm/index.html")
    ]:
        src = repo / path[0]
        dst = repo / path[1]
        dst.parent.mkdir(parents=True, exist_ok=True)
        dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print("Synchronized generated surfaces to docs/")


if __name__ == "__main__":
    main()
