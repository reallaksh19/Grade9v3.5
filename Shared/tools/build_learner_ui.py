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
:root, [data-theme="light"] {
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

[data-theme="dark"] {
  --bg: #0d1117;
  --bg-card: #161b22;
  --bg-soft: #21262d;
  --border: #30363d;
  --border-focus: #58a6ff;
  --text-main: #f0f6fc;
  --text-muted: #8b949e;
  --text-dim: #6e7681;
  --accent-learn: #58a6ff;
  --accent-learn-bg: rgba(56, 139, 253, 0.15);
  --accent-practice: #2dd4bf;
  --accent-practice-bg: rgba(45, 212, 191, 0.15);
  --accent-explore: #fbbf24;
  --accent-explore-bg: rgba(251, 191, 36, 0.15);
  --accent-qb: #38bdf8;
  --accent-qb-bg: rgba(56, 189, 248, 0.15);
  --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.5);
  --shadow-hover: 0 10px 15px -3px rgba(0, 0, 0, 0.6);
}

*, *::before, *::after { box-sizing: border-box; }
body, h1, h2, h3, h4, p { margin: 0; }

html {
  font-size: calc(16px * var(--font-scale, 1));
}

body {
  background-color: var(--bg);
  color: var(--text-main);
  font-family: var(--font-family);
  font-size: calc(1rem * var(--font-scale, 1));
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
  padding: 10px 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}
.g9-brand {
  display: flex;
  align-items: center;
  gap: 10px;
  font-weight: 800;
  font-size: 18px;
  color: var(--text-main);
  letter-spacing: -0.02em;
}
.g9-brand-badge {
  background: var(--accent-learn);
  color: #fff;
  padding: 2px 7px;
  border-radius: var(--radius-sm);
  font-size: 11px;
  font-weight: 800;
  text-transform: uppercase;
}
.g9-header-nav {
  display: flex;
  align-items: center;
  gap: 16px;
  font-size: 14px;
  font-weight: 600;
  color: var(--text-muted);
}
.g9-header-nav a:hover,
.g9-header-nav a.active {
  color: var(--accent-learn);
}
.g9-header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}
.g9-header-btn {
  display: inline-flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-soft);
  border: 1px solid var(--border);
  border-radius: var(--radius-sm);
  padding: 6px 12px;
  font-size: 13.5px;
  font-weight: 600;
  color: var(--text-main);
  cursor: pointer;
  min-height: 38px;
  transition: all 0.15s ease;
  font-family: inherit;
}
.g9-header-btn:hover {
  background: var(--border);
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
  font-family: inherit;
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

/* Search Dialog (Unified Across Portal) */
.g9-search-dialog {
  width: min(680px, calc(100vw - 32px));
  max-height: min(80vh, 720px);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  background: var(--bg-card);
  color: var(--text-main);
  padding: 0;
  box-shadow: 0 24px 60px -12px rgba(0, 0, 0, 0.35);
  margin: auto;
  overflow: hidden;
}
.g9-search-dialog::backdrop {
  background: rgba(15, 23, 42, 0.7);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}
.g9-search-wrap {
  display: flex;
  flex-direction: column;
  padding: 20px;
  gap: 14px;
}
.g9-search-top {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
.g9-search-top strong {
  font-size: 18px;
  font-weight: 800;
  color: var(--text-main);
}
.g9-search-top .site-icon-btn {
  background: var(--bg-soft);
  border: 1px solid var(--border);
  color: var(--text-muted);
  width: 36px;
  height: 36px;
  border-radius: 50%;
  font-size: 20px;
  line-height: 1;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.15s ease;
}
.g9-search-top .site-icon-btn:hover {
  background: var(--border);
  color: var(--text-main);
}
.g9-search-wrap input[type="search"] {
  width: 100%;
  min-height: 48px;
  border: 1.5px solid var(--border);
  border-radius: var(--radius-md);
  padding: 12px 16px;
  background: var(--bg);
  color: var(--text-main);
  font-family: inherit;
  font-size: 16px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s;
  box-sizing: border-box;
}
.g9-search-wrap input[type="search"]:focus {
  border-color: var(--border-focus);
  box-shadow: 0 0 0 3px rgba(79, 70, 229, 0.15);
}
.g9-search-hint {
  font-size: 13px;
  color: var(--text-muted);
  display: flex;
  align-items: center;
  gap: 6px;
}
.g9-search-results {
  max-height: 420px;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 8px;
  padding-right: 4px;
}
.g9-search-result {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto;
  grid-template-rows: auto auto;
  gap: 2px 12px;
  padding: 12px 16px;
  border-radius: var(--radius-md);
  border: 1px solid var(--border);
  background: var(--bg-card);
  text-decoration: none;
  transition: all 0.15s ease;
}
.g9-search-result:hover, .g9-search-result:focus-visible {
  background: var(--bg-soft);
  border-color: var(--accent-learn);
  transform: translateY(-1px);
}
.g9-search-result-main {
  font-size: 15px;
  font-weight: 700;
  color: var(--text-main);
  grid-column: 1;
}
.g9-search-result-sub {
  font-size: 13px;
  color: var(--text-muted);
  grid-column: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.g9-search-result-kind {
  grid-column: 2;
  grid-row: 1 / span 2;
  align-self: center;
  font-size: 11.5px;
  font-weight: 800;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  padding: 4px 8px;
  border-radius: var(--radius-pill);
  background: var(--bg-soft);
  color: var(--text-muted);
  border: 1px solid var(--border);
}
.g9-search-result:hover .g9-search-result-kind {
  background: var(--accent-learn-bg);
  color: var(--accent-learn);
  border-color: var(--accent-learn);
}
.g9-search-empty {
  text-align: center;
  padding: 32px 16px;
  font-size: 14.5px;
  color: var(--text-muted);
}

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
<html lang="en" data-g9-shell>
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
        <span class="logo-icon">⚡</span>
        <span class="brand-title">Grade9V3.5</span>
        <span class="g9-brand-badge">Learner Platform</span>
      </a>
      <nav class="g9-header-nav" aria-label="Portal Navigation">
        <a href="{rel_root}index.html">Home</a>
        <a href="{rel_root}physics/index.html">Physics</a>
        <a href="{rel_root}chemistry/index.html">Chemistry</a>
        <a href="{rel_root}mathematics/index.html">Mathematics</a>
        <a href="{rel_root}question-bank/index.html">Question Bank</a>
      </nav>
      <div class="g9-header-actions">
        <button type="button" class="g9-header-btn g9-search-btn" data-g9-action="search" title="Search Grade9V3 (Ctrl/⌘ K)" aria-label="Search">
          <span class="g9-btn-icon">🔍</span>
          <span class="g9-btn-text">Search</span>
        </button>
        <button type="button" class="g9-header-btn g9-display-btn" data-g9-action="display" title="Display & Theme Settings" aria-label="Display & Theme">
          <span class="g9-btn-icon">🌙 / ☀️</span>
          <span class="g9-btn-text">Display</span>
        </button>
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
<script src="{rel_root}js/display-controls.js"></script>
<script src="{rel_root}js/site-header.js" data-site-root="{rel_root}"></script></body>
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

  <div style="margin-top: 32px; padding: 16px; text-align: center; font-size: 13.5px; color: var(--muted, #64748b);">
    <span>Authoring & Intake: <a href="raw-intake/index.html" style="color: inherit; text-decoration: underline;">Question Intake Workbench</a></span>
  </div>
"""
    return render_shell("Home", content, rel_root=rel_root)


SUBJECT_EXPLORERS = {
    "Chemistry": [
        {
            "title": "Chemical Bonding & Molecular Structure",
            "href": "bonding/explorers/chemical_bonding/index.html",
            "desc": "Lewis formal charge diagrams, VSEPR 3D electron geometry, net dipole cancellation, and PCl5 axial vs equatorial geometry.",
            "tag": "Interactive"
        },
        {
            "title": "Mole Concept & Stoichiometry",
            "href": "some-basic-concepts/explorers/mole_concept/index.html",
            "desc": "Mole scale, limiting reagent exhaustion, sequential and parallel reaction yield tracking, and eudiometry.",
            "tag": "Interactive"
        },
        {
            "title": "Behaviour of Gases",
            "href": "gases/explorers/behaviour_of_gases/index.html",
            "desc": "Ideal/real gases, Maxwell speed distributions, excluded volume, compressibility factor Z, and critical state.",
            "tag": "Interactive"
        },
        {
            "title": "Redox Reactions",
            "href": "redox/explorers/redox_reactions/index.html",
            "desc": "Oxidation state balance, electrochemical potential, and electron transfer visualizer.",
            "tag": "Interactive"
        }
    ],
    "Mathematics": [
        {
            "title": "Vector Algebra · 3D Master Suite",
            "href": "vectors/explorers/vector_algebra/index.html",
            "desc": "Rotatable 3D Euclidean vector engine, Gram-Schmidt orthogonal projection split, cross product, and triple products.",
            "tag": "Interactive"
        },
        {
            "title": "Polynomials & Coordinate Geometry Research Suite",
            "href": "../standalone/mathematics-polynomials-and-coordinates-suite.html",
            "desc": "2D Cartesian coordinate plane, orthogonal axis projections, Remainder Theorem calculator, and cubic identity visualizer.",
            "tag": "Interactive"
        }
    ],
    "Physics": [
        {
            "title": "Motion in 1D Suite",
            "href": "motion-1d/explorers/motion_in_1d/index.html",
            "desc": "Kinematic equations, free fall under gravity, velocity-time graph area integrals, and turnaround points.",
            "tag": "Interactive"
        },
        {
            "title": "Motion in a Plane Research Suite",
            "href": "motion-2d/explorers/motion-in-a-plane/index.html",
            "desc": "Cartesian projectile resolution, parabolic trajectory tracing, complementary angle invariance, and banked roads.",
            "tag": "Interactive"
        },
        {
            "title": "2D Motion Master Suite",
            "href": "motion-in-2d/explorers/motions_in_2d/index.html",
            "desc": "Full 2D kinematic engine: rain-man relative velocity, river-boat crossing drift, and cliff-launch trajectories.",
            "tag": "Interactive"
        },
        {
            "title": "Independent Components & Shared Clock",
            "href": "motion-in-2d/explorers/independent_components_shared_clock/index.html",
            "desc": "Direct visual proof of orthogonal independence in two-dimensional kinematics under uniform gravity.",
            "tag": "Interactive"
        },
        {
            "title": "Same Height Same Speed Symmetries",
            "href": "motion-in-2d/explorers/same_height_same_speed/index.html",
            "desc": "Horizontal symmetry and kinetic-potential energy conservation along parabolic flight trajectories.",
            "tag": "Interactive"
        },
        {
            "title": "The Apex Fallacy",
            "href": "motion-in-2d/explorers/the_apex_fallacy/index.html",
            "desc": "Non-zero acceleration at the apex: why net force is not zero when vertical velocity vanishes.",
            "tag": "Interactive"
        },
        {
            "title": "Atwood Machines & Pulley Constraints",
            "href": "nlm/explorers/atwood-pulleys/index.html",
            "desc": "Inextensible string kinematics, movable pulley mechanical advantage, and acceleration constraint equations.",
            "tag": "Interactive"
        },
        {
            "title": "Connected Blocks Dynamics",
            "href": "nlm/explorers/connected-blocks/index.html",
            "desc": "Multi-body contact forces, internal tension cancellation, and common acceleration systems.",
            "tag": "Interactive"
        },
        {
            "title": "Static-to-Kinetic Friction Threshold",
            "href": "nlm/explorers/friction-threshold/index.html",
            "desc": "Real-time physical simulation of self-adjusting static friction, impending slip threshold, and kinetic drop.",
            "tag": "Interactive"
        }
    ]
}


TOPIC_TITLES = {
    "phy.nlm": "Newton's Laws of Motion",
    "phy.motion-1d": "Motion in One Dimension",
    "phy.motion-2d": "Motion in a Plane (2D)",
    "phy.vectors": "Vector Methods in Physics",
    "phy.fluids": "Thrust & Hydrostatic Pressure",
    "chem.bonding": "Chemical Bonding & Molecular Structure",
    "chem.mole": "Mole Concept & Stoichiometry",
    "chem.gases": "Behaviour of Gases",
    "chem.redox": "Redox Reactions",
    "math.polynomials": "Polynomials & Remainder Theorem",
    "math.coordinate-geometry": "Coordinate Geometry",
}


def generate_subject_hub(subject: str, registry: list[dict], bundles: list[dict], rel_root: str = "") -> str:
    # Discover topics for this subject from bundles: ONLY topics with Core 1 / Core 1A learning content
    topics = {}
    for b in bundles:
        if b.get("subject_ref") == subject and len(b.get("learn", [])) > 0:
            t = b.get("topic_ref", "")
            if t not in topics:
                title = TOPIC_TITLES.get(t, t.replace(".", " ").title())
                topics[t] = {
                    "id": t,
                    "title": title,
                    "concept_count": 0,
                    "learn_items": b.get("learn", [])
                }
            topics[t]["concept_count"] += 1

    tag_classes = {"Physics": "g9-tag-physics", "Chemistry": "g9-tag-chemistry", "Mathematics": "g9-tag-math"}
    tag_cls = tag_classes.get(subject, "g9-tag-physics")

    topic_cards = []
    for tid, tmeta in sorted(topics.items()):
        badge = f'<span class="g9-card-tag {tag_cls}">Core Study</span>'
        # Topic link: use local subject-relative folder or topics/
        tid_short = tid.split(".")[-1]
        if tid == "chem.mole":
            topic_href = "some-basic-concepts/index.html"
        else:
            topic_href = f"{tid_short}/index.html"
        topic_cards.append(f"""
    <a class="g9-card" href="{topic_href}">
      <div class="g9-card-header">
        {badge}
        <h3 class="g9-card-title">{html.escape(tmeta['title'])}</h3>
        <p class="g9-card-desc">{tmeta['concept_count']} core concept(s) with dedicated Learn derivations and Question Bank practice.</p>
      </div>
      <div class="g9-card-action">
        <span>Open Topic Workspace</span>
        <span>&rarr;</span>
      </div>
    </a>""")

    exp_cards = []
    for exp in SUBJECT_EXPLORERS.get(subject, []):
        exp_cards.append(f"""
    <a class="g9-card" href="{exp['href']}">
      <div class="g9-card-header">
        <span class="g9-card-tag {tag_cls}">{html.escape(exp['tag'])}</span>
        <h3 class="g9-card-title">{html.escape(exp['title'])}</h3>
        <p class="g9-card-desc">{html.escape(exp['desc'])}</p>
      </div>
      <div class="g9-card-action">
        <span>⚡ Try visually</span>
        <span>&rarr;</span>
      </div>
    </a>""")

    sections_html = []
    if topic_cards:
        sections_html.append(f"""
  <h2 style="font-size: 20px; font-weight: 700; margin: 24px 0 12px;">Core Topic Workspaces</h2>
  <div class="g9-grid">
    {''.join(topic_cards)}
  </div>""")

    if exp_cards:
        sections_html.append(f"""
  <h2 style="font-size: 20px; font-weight: 700; margin: 28px 0 12px;">Interactive Explorers & Visual Suites</h2>
  <div class="g9-grid">
    {''.join(exp_cards)}
  </div>""")

    crumbs = [("Home", f"{rel_root}index.html"), (subject, "")]
    content = f"""
  <div class="g9-hero">
    <h1 class="g9-hero-title">{html.escape(subject)} Hub</h1>
    <p class="g9-hero-subtitle">Select a topic or visual simulation model to explore.</p>
  </div>

  {''.join(sections_html)}
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
        interactive_items = b.get("interactive", [])

        learn_btn = ""
        if learn_items:
            ep = f"{rel_root}{learn_items[0]['entrypoint']}"
            learn_btn = f'<a class="g9-btn-action g9-btn-learn" href="{html.escape(ep)}">📖 Learn (Core 1A)</a>'

        practice_items = b.get("practice", [])
        tablet_btn = ""
        if practice_items:
            ep = f"{rel_root}{practice_items[0]['entrypoint']}"
            tablet_btn = f'<a class="g9-btn-action g9-btn-practice" href="{html.escape(ep)}">✍️ Practice Tablet (Core 2)</a>'

        interactive_btn = ""
        if interactive_items:
            ep = f"{rel_root}{interactive_items[0]['entrypoint']}"
            interactive_btn = f'<a class="g9-btn-action g9-btn-explore" href="{html.escape(ep)}" target="_blank" rel="noopener">⚡ Try visually</a>'

        topic_slug = topic_id.split(".")[-1]
        practice_url = f"{rel_root}question-bank/index.html?subject={html.escape(subject)}&topic={html.escape(topic_slug)}&mode=study"
        practice_btn = f'<a class="g9-btn-action g9-btn-qb" href="{practice_url}">🎯 Practice in Question Bank &rarr;</a>'

        action_buttons = [learn_btn, tablet_btn, interactive_btn, practice_btn]
        action_row = "\n      ".join(btn for btn in action_buttons if btn)

        concept_sections.append(f"""
  <div class="g9-concept-card" id="{html.escape(c_ref)}">
    <div class="g9-concept-header">
      <span class="g9-concept-badge">{html.escape(c_title)}</span>
      <h2 class="g9-concept-title">{html.escape(c_title)}</h2>
      <p class="g9-concept-desc">Organised learning path connecting mathematical construction, authentic past-paper practice, and visual simulation.</p>
    </div>
    <div class="g9-action-row">
      {action_row}
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
    # 3. Generate Subject Hubs (dynamically discovered from registry)
    discovered_subjects = sorted(list(set(
        rec.get("classification", {}).get("subject_ref")
        for rec in registry
        if rec.get("audience") == "LEARNER" and rec.get("classification", {}).get("subject_ref") not in (None, "Common", "Internal")
    )))
    if not discovered_subjects:
        discovered_subjects = ["Physics", "Chemistry", "Mathematics"]

    for subj in discovered_subjects:
        hub_dir = repo / "public" / subj.lower()
        hub_dir.mkdir(parents=True, exist_ok=True)
        hub_html = generate_subject_hub(subj, registry, bundles, rel_root="../")
        with open(hub_dir / "index.html", "w", encoding="utf-8") as f:
            f.write(hub_html)
        print(f"Wrote public/{subj.lower()}/index.html")

    # 4. Generate Topic Workspaces dynamically from concept bundles that have Core 1/Core 1A
    discovered_topics = {}
    for b in bundles:
        subj = b.get("subject_ref", "Physics")
        t = b.get("topic_ref")
        if t and len(b.get("learn", [])) > 0:
            if t not in discovered_topics:
                title = TOPIC_TITLES.get(t, t.replace(".", " ").title())
                discovered_topics[t] = {
                    "subject": subj,
                    "title": title
                }
    if not discovered_topics:
        discovered_topics["phy.nlm"] = {"subject": "Physics", "title": "Newton's Laws of Motion"}

    generated_topic_rel_paths = []
    for tid, tinfo in discovered_topics.items():
        slug = tid.split(".")[-1]
        subj_slug = tinfo["subject"].lower()

        topic_html = generate_topic_workspace(tid, tinfo["title"], tinfo["subject"], bundles, rel_root="../../")

        target_dirs = [
            repo / "public" / "topics" / slug,
            repo / "public" / subj_slug / slug,
        ]
        if tid == "chem.mole":
            target_dirs.append(repo / "public" / subj_slug / "some-basic-concepts")

        for tdir in target_dirs:
            tdir.mkdir(parents=True, exist_ok=True)
            with open(tdir / "index.html", "w", encoding="utf-8") as f:
                f.write(topic_html)
            rel_str = str((tdir / "index.html").relative_to(repo)).replace("\\", "/")
            generated_topic_rel_paths.append(rel_str)
            print(f"Wrote {rel_str}")

    # Copy to docs/ for publication
    sync_targets = [
        ("public/css/modern-learner.css", "docs/css/modern-learner.css"),
        ("public/index.html", "docs/index.html")
    ]
    for subj in discovered_subjects:
        sync_targets.append((f"public/{subj.lower()}/index.html", f"docs/{subj.lower()}/index.html"))
    for rel_path in generated_topic_rel_paths:
        sync_targets.append((rel_path, rel_path.replace("public/", "docs/")))

    for src_rel, dst_rel in sync_targets:
        src = repo / src_rel
        dst = repo / dst_rel
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_text(src.read_text(encoding="utf-8"), encoding="utf-8")
    print("Synchronized generated surfaces to docs/")


if __name__ == "__main__":
    main()
