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
.g9-header-btn.g9-drive-btn {
  color: var(--text-main);
  text-decoration: none;
}
.g9-header-btn.g9-drive-btn:hover {
  border-color: #4285f4;
  background: rgba(66, 133, 244, 0.1);
  color: #4285f4;
}

/* Header Dropdown (for Drive PDFs) */
.g9-header-dropdown {
  position: relative;
  display: inline-block;
}
.g9-header-dropdown summary {
  list-style: none;
}
.g9-header-dropdown summary::-webkit-details-marker {
  display: none;
}
.g9-header-dropdown[open] .g9-btn-caret {
  transform: rotate(180deg);
}
.g9-btn-caret {
  font-size: 11px;
  transition: transform 0.15s ease;
  margin-left: 2px;
}
.g9-dropdown-menu {
  position: absolute;
  top: calc(100% + 8px);
  right: 0;
  min-width: 320px;
  background: var(--bg-card);
  border: 1px solid var(--border);
  border-radius: var(--radius-md);
  box-shadow: var(--shadow-hover);
  padding: 8px 0;
  z-index: 1000;
  animation: g9DropIn 0.15s ease-out;
}
@keyframes g9DropIn {
  from { opacity: 0; transform: translateY(-6px); }
  to { opacity: 1; transform: translateY(0); }
}
.g9-dropdown-header {
  padding: 6px 16px 8px;
  font-size: 11.5px;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--text-dim);
  border-bottom: 1px solid var(--border);
}
.g9-dropdown-item {
  display: flex;
  align-items: flex-start;
  gap: 10px;
  padding: 10px 16px;
  color: var(--text-main);
  text-decoration: none;
  font-size: 13.5px;
  transition: background 0.12s ease;
}
.g9-dropdown-item:hover {
  background: var(--bg-soft);
  color: var(--accent-learn);
}
.g9-dropdown-item .g9-item-icon {
  font-size: 16px;
  line-height: 1.3;
  flex-shrink: 0;
}
.g9-dropdown-item strong {
  display: block;
  font-weight: 700;
  font-size: 13.5px;
}
.g9-dropdown-item small {
  display: block;
  color: var(--text-muted);
  font-size: 11.5px;
  word-break: break-all;
  margin-top: 2px;
}
.g9-dropdown-divider {
  height: 1px;
  background: var(--border);
  margin: 6px 0;
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
  color: var(--text-main);
  border-color: var(--border);
}
.g9-btn-qb:hover { background: #e2e8f0; color: var(--text-main); }
.g9-btn-atlas {
  background: var(--bg-soft);
  color: var(--text-muted);
  border-color: var(--border);
  font-weight: 600;
}
.g9-btn-atlas:hover { background: #e2e8f0; color: var(--accent-learn); }

/* Continuum Bar & Segmented Action Pills */
.g9-continuum-bar {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  align-items: center;
  padding-top: 18px;
  border-top: 1px solid var(--border);
}

.g9-btn-pill {
  display: inline-flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  min-height: 44px;
  border-radius: var(--radius-pill);
  font-size: 13.5px;
  font-weight: 700;
  text-decoration: none;
  transition: all 0.15s ease;
  border: 1px solid var(--border);
  box-shadow: var(--shadow-sm);
}
.g9-btn-pill:hover {
  transform: translateY(-1px);
  box-shadow: var(--shadow-md);
}

.g9-pill-1a {
  background: var(--accent-learn-bg);
  color: var(--accent-learn);
  border-color: rgba(79, 70, 229, 0.3);
}
.g9-pill-1a:hover {
  background: var(--accent-learn);
  color: #ffffff;
}

.g9-pill-1b {
  background: var(--accent-explore-bg);
  color: var(--accent-explore);
  border-color: rgba(217, 119, 6, 0.3);
}
.g9-pill-1b:hover {
  background: #d97706;
  color: #ffffff;
}

.g9-pill-2a {
  background: #f0fdf4;
  color: #15803d;
  border-color: rgba(22, 163, 74, 0.3);
}
[data-theme="dark"] .g9-pill-2a {
  background: rgba(34, 197, 94, 0.12);
  color: #4ade80;
  border-color: rgba(74, 222, 128, 0.3);
}
.g9-pill-2a:hover {
  background: #16a34a;
  color: #ffffff;
}

.g9-pill-2b {
  background: #faf5ff;
  color: #7e22ce;
  border-color: rgba(126, 34, 206, 0.3);
}
[data-theme="dark"] .g9-pill-2b {
  background: rgba(168, 85, 247, 0.12);
  color: #c084fc;
  border-color: rgba(192, 132, 252, 0.3);
}
.g9-pill-2b:hover {
  background: #7e22ce;
  color: #ffffff;
}

.g9-pill-qb {
  background: var(--accent-qb-bg);
  color: var(--accent-qb);
  border-color: rgba(2, 132, 199, 0.3);
}
.g9-pill-qb:hover {
  background: var(--accent-qb);
  color: #ffffff;
}

.g9-pill-atlas {
  background: var(--bg-soft);
  color: var(--text-muted);
  border-color: var(--border);
}
.g9-pill-atlas:hover {
  background: var(--bg-card);
  color: var(--text-main);
  border-color: var(--border-focus);
}

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


def render_shell(title: str, content: str, breadcrumbs: list[tuple[str, str]] = None, rel_root: str = "", extra_header_actions: str = "") -> str:
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
        <a href="{rel_root}atlas/index.html">Atlas &amp; Rungs</a>
      </nav>
      <div class="g9-header-actions">
        {extra_header_actions}
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

    CANONICAL_SUBJECT_ORDER = ["Physics", "Chemistry", "Mathematics"]
    for subj, meta in sorted(subjects_map.items(), key=lambda item: (CANONICAL_SUBJECT_ORDER.index(item[0]) if item[0] in CANONICAL_SUBJECT_ORDER else 999, item[0])):
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


TOPIC_DRIVE_PDFS = {
    "chem.gases": [
        {
            "title": "Core 1 Study Guide",
            "name": "chemistry_core1_behaviour_of_gases_answercheck_rebuild.pdf",
            "size": "104 KB",
            "id": "1ZigrQD5EhUoUszUjjj7TEude9qtgJhbT",
        },
        {
            "title": "Core 2 Problem Suite",
            "name": "chemistry_core2_behaviour_of_gases_answercheck_rebuild.pdf",
            "size": "1.1 MB",
            "id": "1qITaK4d98QpVFfdL-oFwxUTdnJW1a6_k",
        }
    ],
    "chem.bonding": [
        {
            "title": "Core 2 Problem Suite",
            "name": "chemistry_core2_chemical_bonding.pdf",
            "size": "1.6 MB",
            "id": "1eLXnAeefMFyc5KL4KD18swsUNYEX3SU5",
        }
    ],
    "chem.mole": [
        {
            "title": "Core 1 Study Guide",
            "name": "chemistry_core1_some_basic_concepts_answercheck_rebuild.pdf",
            "size": "305 KB",
            "id": "1IHeHI7iTlggO3WYzsAYSo6wzvlmpyW6T",
        },
        {
            "title": "Core 2 Problem Suite",
            "name": "chemistry_core2_some_basic_concepts_answercheck_rebuild.pdf",
            "size": "3.0 MB",
            "id": "1ZqgdPSsx4ZEOerqmw9Dl6nKuwzHF9hqG",
        }
    ],
    "chem.redox": [
        {
            "title": "Core 1 Study Guide",
            "name": "chemistry_core1_redox_reactions.pdf",
            "size": "135 KB",
            "id": "1ApxwaUKm8fxFh2CHOk_1Bw2kuP7xoxnz",
        },
        {
            "title": "Core 2 Problem Suite",
            "name": "chemistry_core2_redox_reactions.pdf",
            "size": "579 KB",
            "id": "18Mu0ejUU1486V3Gs0A2aRnipg8JY0Coc",
        }
    ],
    "phy.motion-1d": [
        {
            "title": "Core 1 Study Guide",
            "name": "physics-motion-1d-revised-core1.pdf",
            "size": "110 KB",
            "id": "19VYLi4F_aZwMQ70YVG_z-mEcvkzZ_hfx",
        },
        {
            "title": "Core 2 Problem Suite (14 Qs)",
            "name": "physics-motion-1d-revised-core2.pdf",
            "size": "140 KB",
            "id": "1bmpHmcoLEc5Nmoyv9PiSodlRNHolR5-L",
        },
        {
            "title": "Consolidated Practice Sets",
            "name": "Motion_Grade9_Student_Core_FINAL_Consolidated.pdf",
            "size": "1.2 MB",
            "id": "1ZdXT1d8aA-vYRz0uQo_OWe-nk71AzLqn",
        },
        {
            "title": "Difficulty Level Sets",
            "name": "Motion_Combined_Concept_Difficulty_v6.pdf",
            "size": "461 KB",
            "id": "1aEfYToYSvB8Z1dj-v0AAUqebfigWgoYi",
        }
    ],
    "phy.motion-2d": [
        {
            "title": "Core 1A Full Combined Study",
            "name": "core1A-motion-in-a-plane-full-combined-fixed.pdf",
            "size": "548 KB",
            "id": "10o2pEXQNApxzn9s-jrR8VNMAUdFCCOHO",
        },
        {
            "title": "Core 2 Comprehensive Practice (v2)",
            "name": "Emailing physics-motion-2d-revised-core2-v2.pdf",
            "size": "8.6 MB",
            "id": "1EoG0kYYuSG67HrihvP3M_HK05qD7enIb",
        },
        {
            "title": "NCERT Core 1 Study",
            "name": "physics-motion-2d-ncert-revised-core1.pdf",
            "size": "95 KB",
            "id": "1i_9Mkv5REW-HUF_xcWMPV783v4h9D78A",
        },
        {
            "title": "NCERT Core 2 Practice",
            "name": "physics-motion-2d-ncert-revised-core2.pdf",
            "size": "107 KB",
            "id": "126MoBNOZUiZ_lNZuFwOwv3hK4RMVCPYa",
        },
        {
            "title": "SBA-06 Trajectory Equations",
            "name": "M2D-SBA-06-professional-textbook-lossless-v1-1.pdf",
            "size": "131 KB",
            "id": "1U68frEgpQ76szu0omNjJEQ75hk0RGqVW",
        },
        {
            "title": "SBA-07 Maximum Height",
            "name": "M2D-SBA-07-professional-textbook-lossless-v1-1.pdf",
            "size": "141 KB",
            "id": "1KoGR37aNjyHTpwRwuWMrEf0SktsxAdjk",
        },
        {
            "title": "SBA Master Invariants",
            "name": "DOC-20260913-WA0016.pdf",
            "size": "108 KB",
            "id": "1QkmPTvky4B3l8j4DsKQMpyIPWtKPDc6y",
        }
    ],
    "phy.nlm": [
        {
            "title": "Core 1 Study Guide",
            "name": "physics-nlm-revised-core1.pdf",
            "size": "103 KB",
            "id": "1jz2v_6oxak0LSWj2o-hYINIHoJOXl0zD",
        },
        {
            "title": "Core 2 Problem Suite",
            "name": "physics-nlm-revised-core2.pdf",
            "size": "172 KB",
            "id": "1gKA0mLn6lhtRcQQ3dFFcUM-BcWatEl64",
        }
    ],
    "phy.vectors": [
        {
            "title": "Core 1 Study Guide",
            "name": "Emailing physics-vectors-revised-core1.pdf",
            "size": "108 KB",
            "id": "1vUxetmEcwVQoZNtozh8rR7bgX4fIFNuc",
        },
        {
            "title": "Core 2 Problem Suite",
            "name": "physics-vectors-revised-core2.pdf",
            "size": "137 KB",
            "id": "1LMnplYRFOmAzZ8bxkOwblqRw29EbrLLk",
        }
    ],
    "math.euclids-geometry": [
        {
            "title": "Core 1 Study Guide",
            "name": "Euclids_Geometry_Core1_Final_CrossCore_v2.pdf",
            "size": "465 KB",
            "id": "1QNx6-AvyfdbHfXCePYXgdwnwPeD2lnHu",
        },
        {
            "title": "Core 2 Practice (49 Tasks)",
            "name": "Euclids_Geometry_Core2_Final_CrossCore_v1.pdf",
            "size": "501 KB",
            "id": "1eBfxf8dU0WvBIujgnIIKGbMzf9P3Oa3f",
        }
    ],
    "math.theory-of-equations": [
        {
            "title": "Core 1 Study Guide",
            "name": "Theory_of_Equations_Core1_Textbook_Rebuild (1).pdf",
            "size": "84 KB",
            "id": "1DQwtYf5Y8dCb_CkclAvC8hpDV_dNUWWP",
        },
        {
            "title": "Core 2 Practice Suite",
            "name": "Theory_of_Equations_Core2_Textbook_Rebuild (1).pdf",
            "size": "77 KB",
            "id": "1Yt3oBNqNP2zB9oRHXktFcYbZ71pkF-XS",
        },
        {
            "title": "Challenge Problems (WA0023)",
            "name": "DOC-20260913-WA0023.pdf",
            "size": "151 KB",
            "id": "1NeKPK4I84MiHGSunp4vytzQJlLRoO-ld",
        }
    ]
}

DRIVE_SVG_ICON = """<svg class="g9-btn-icon" width="16" height="16" viewBox="0 0 87.3 78" aria-hidden="true" style="vertical-align: middle;">
  <path d="m6.6 66.85 3.85 6.65c.8 1.4 1.95 2.5 3.3 3.3l13.75-23.8H0c0 1.55.4 3.1 1.2 4.5z" fill="#0066da"/>
  <path d="M43.65 25 29.9 1.2c-1.35.8-2.5 1.9-3.3 3.3l-25.4 44C.4 49.9 0 51.45 0 53h27.5z" fill="#00ac47"/>
  <path d="M73.55 76.8c1.35-.8 2.5-1.9 3.3-3.3l1.6-2.75 7.65-13.25c.8-1.4 1.2-2.95 1.2-4.5H59.8l5.85 10.15z" fill="#ea4335"/>
  <path d="M43.65 25 57.4 1.2C56.05.4 54.5 0 52.9 0H34.4c-1.6 0-3.15.45-4.5 1.2z" fill="#00832d"/>
  <path d="M59.8 53H27.5L13.75 76.8c1.35.8 2.9 1.2 4.5 1.2h50.8c1.6 0 3.15-.45 4.5-1.2z" fill="#2684fc"/>
  <path d="m73.4 26.5-12.7-22c-.8-1.4-1.95-2.5-3.3-3.3L43.65 25 59.8 53h27.5c0-1.55-.4-3.1-1.2-4.5z" fill="#ffba00"/>
</svg>"""


def render_drive_header_action(pdfs: list[dict]) -> str:
    if not pdfs:
        return ""
    if len(pdfs) == 1:
        pdf = pdfs[0]
        url = f"https://drive.google.com/file/d/{pdf['id']}/view"
        title = html.escape(f"Open Source PDF in Google Drive: {pdf['name']}")
        return f"""
        <a href="{url}" target="_blank" rel="noopener" class="g9-header-btn g9-drive-btn" title="{title}" aria-label="Open Source PDF in Google Drive">
          {DRIVE_SVG_ICON}
          <span class="g9-btn-text">Source PDF</span>
        </a>"""

    items_html = []
    for pdf in pdfs:
        url = f"https://drive.google.com/file/d/{pdf['id']}/view"
        items_html.append(f"""
      <a href="{url}" target="_blank" rel="noopener" class="g9-dropdown-item">
        <span class="g9-item-icon">📄</span>
        <div class="g9-item-info">
          <strong>{html.escape(pdf['title'])}</strong>
          <small>{html.escape(pdf['name'])} ({html.escape(pdf.get('size', ''))})</small>
        </div>
      </a>""")

    items_html.append(f"""
      <div class="g9-dropdown-divider"></div>
      <a href="https://drive.google.com/drive/folders/1ipfk8TDM7ACDqbPdjRc3ZIE6UTFQMvyw" target="_blank" rel="noopener" class="g9-dropdown-item">
        <span class="g9-item-icon">📁</span>
        <div class="g9-item-info">
          <strong>Grade 9 Drive Repository</strong>
          <small>Open Full Google Drive Folder</small>
        </div>
      </a>""")

    return f"""
        <details class="g9-header-dropdown">
          <summary class="g9-header-btn g9-drive-btn" aria-label="Google Drive Source PDFs" title="Access Original Source PDFs in Google Drive">
            {DRIVE_SVG_ICON}
            <span class="g9-btn-text">Source PDFs</span>
            <span class="g9-btn-caret" aria-hidden="true">▾</span>
          </summary>
          <div class="g9-dropdown-menu">
            <div class="g9-dropdown-header">Google Drive Source PDFs</div>
            {''.join(items_html)}
          </div>
        </details>"""


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
    "math.euclids-geometry": "Euclid's Geometry",
    "math.theory-of-equations": "Theory of Equations",
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
        n_concepts = tmeta['concept_count']
        concept_label = "1 core concept" if n_concepts == 1 else f"{n_concepts} core concepts"
        topic_cards.append(f"""
    <a class="g9-card" href="{topic_href}">
      <div class="g9-card-header">
        {badge}
        <h3 class="g9-card-title">{html.escape(tmeta['title'])}</h3>
        <p class="g9-card-desc">{concept_label} with dedicated Learn derivations and Question Bank practice.</p>
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

        # Dynamic Continuum Bar
        pills = []
        topic_slug = topic_id.split(".")[-1]

        # 1A: Concept Construction & Derivations
        c1a_items = b.get("core_1a") or learn_items
        for item in c1a_items:
            ep = f"{rel_root}{item['entrypoint']}"
            t = item.get("title", "1A Derivation")
            clean_t = t
            for pfx in ["GRADE 9 PHYSICS - ", "GRADE 9 CHEMISTRY - ", "GRADE 9 MATHEMATICS - ", "CORE (1A) ", "Core 1A "]:
                if clean_t.startswith(pfx):
                    clean_t = clean_t[len(pfx):].strip()
            clean_t = clean_t.split("·")[-1].split("|")[0].replace("— Learn", "").strip() or "1A Construction"
            if len(clean_t) > 30:
                clean_t = clean_t[:28] + "…"
            pills.append(f'<a class="g9-btn-pill g9-pill-1a" href="{html.escape(ep)}" title="1A Derivation · {html.escape(t)}"><span class="g9-pill-icon">📖</span><span class="g9-pill-text">{html.escape(clean_t)}</span></a>')

        # 1B: Visualizers & Simulators
        c1b_items = b.get("interactive") if "interactive" in b else b.get("core_1b", [])
        if c1b_items is None:
            c1b_items = []
        for item in c1b_items:
            ep = f"{rel_root}{item['entrypoint']}"
            t = item.get("title", "1B Visualizer")
            clean_t = t.split("·")[-1].replace("Visual Proof", "Proof").replace("Visualizer", "Sim").replace("Simulation", "Sim").replace("Explorer", "").strip() or "1B Visualizer"
            if len(clean_t) > 30:
                clean_t = clean_t[:28] + "…"
            pills.append(f'<a class="g9-btn-pill g9-pill-1b" href="{html.escape(ep)}" target="_blank" rel="noopener" title="Try visually · 1B Visualizer · {html.escape(t)}"><span class="g9-pill-icon">⚡</span><span class="g9-pill-text">Try visually: {html.escape(clean_t)}</span></a>')

        # 2A: NCERT Problem Helpers
        c2a_items = b.get("core_2a", [])
        for item in c2a_items:
            ep = f"{rel_root}{item['entrypoint']}"
            t = item.get("title", "2A NCERT Helper")
            pills.append(f'<a class="g9-btn-pill g9-pill-2a" href="{html.escape(ep)}" title="2A NCERT · {html.escape(t)}"><span class="g9-pill-icon">📝</span><span class="g9-pill-text">2A NCERT Helper</span></a>')

        # 2B: Competitive PYQ Challenge Suites
        c2b_items = b.get("core_2b", [])
        for item in c2b_items:
            ep = f"{rel_root}{item['entrypoint']}"
            t = item.get("title", "2B Competitive Suite")
            pills.append(f'<a class="g9-btn-pill g9-pill-2b" href="{html.escape(ep)}" title="2B JEE PYQ · {html.escape(t)}"><span class="g9-pill-icon">🏆</span><span class="g9-pill-text">2B JEE Suite</span></a>')

        # Core 2: Question Bank Direct Filter
        practice_url = f"{rel_root}question-bank/index.html?topic={topic_slug}&capability={html.escape(c_ref)}&mode=study"
        pills.append(f'<a class="g9-btn-pill g9-pill-qb" href="{practice_url}" title="Practice in Question Bank"><span class="g9-pill-icon">🎯</span><span class="g9-pill-text">Practice in Question Bank &rarr;</span></a>')

        # Core 1: Rung Ladder
        atlas_url = f"{rel_root}atlas/index.html#{html.escape(topic_slug)}"
        pills.append(f'<a class="g9-btn-pill g9-pill-atlas" href="{atlas_url}" title="View Curriculum & Pedagogical Rungs"><span class="g9-pill-icon">🪜</span><span class="g9-pill-text">Rung Ladder</span></a>')

        action_row = f'<div class="g9-continuum-bar">\n        ' + "\n        ".join(pills) + "\n      </div>"

        display_title = c_title
        if c_title == "Math Euclid Geometry":
            display_title = "Axioms, Postulates & Deductive Proofs"
        elif c_title == "Math Theory Of Equations":
            display_title = "Polynomial Roots & Vieta's Relations"

        concept_sections.append(f"""
  <div class="g9-concept-card" id="{html.escape(c_ref)}">
    <div class="g9-concept-header">
      <span class="g9-concept-badge">Core Concept</span>
      <h2 class="g9-concept-title">{html.escape(display_title)}</h2>
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
    topic_drive_action = render_drive_header_action(TOPIC_DRIVE_PDFS.get(topic_id, []))
    return render_shell(f"{topic_title} Workspace", content, breadcrumbs=crumbs, rel_root=rel_root, extra_header_actions=topic_drive_action)


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
    CANONICAL_SUBJECT_ORDER = ["Physics", "Chemistry", "Mathematics"]
    discovered_subjects = sorted(
        list(set(
            rec.get("classification", {}).get("subject_ref")
            for rec in registry
            if rec.get("audience") == "LEARNER" and rec.get("classification", {}).get("subject_ref") not in (None, "Common", "Internal")
        )),
        key=lambda s: (CANONICAL_SUBJECT_ORDER.index(s) if s in CANONICAL_SUBJECT_ORDER else 999, s)
    )
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
