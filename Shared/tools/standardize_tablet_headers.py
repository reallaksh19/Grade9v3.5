#!/usr/bin/env python3
"""Standardize all practice tablet headers and eliminate separate tab strips.

Enforces:
1. Standard single-bar `header.app-header` with:
   - Title + Emoji + Subject Badge
   - `← Previous Page` button (`history.back()` with topic fallback)
   - Direct Topic Workspace link
   - `⚡ Home` portal link
   - Synchronized `🌓 Mode` toggle
2. Strictly NO separate tabs (`<nav class="tab-nav">` or `.tabs-scroll-row` removed).
   If tab switching is used, module buttons are moved into the responsive sidebar widget.
3. Universal across Physics, Chemistry, and Mathematics.
"""

from pathlib import Path
import re

REPO = Path(__file__).resolve().parents[2]
PRACTICE_DIR = REPO / "public" / "standalone" / "practice"

TABLET_CONFIG = {
    # Chemistry
    "core1a-chemistry-behaviour-of-gases-tablet.html": {
        "subject": "Chemistry",
        "title": "Behaviour of Gases · 12.7\" Tablet Suite",
        "emoji": "💨",
        "badge": "Chemistry · Core 1",
        "workspace_url": "../../chemistry/gases/index.html",
        "workspace_label": "Gases Workspace",
    },
    "core2-chemistry-behaviour-of-gases-tablet.html": {
        "subject": "Chemistry",
        "title": "Behaviour of Gases Core 2 Challenge Suite",
        "emoji": "💨",
        "badge": "Chemistry · Core 2",
        "workspace_url": "../../chemistry/gases/index.html",
        "workspace_label": "Gases Workspace",
    },
    "chemistry-behaviour-of-gases-master-suite.html": {
        "subject": "Chemistry",
        "title": "Behaviour of Gases Master Suite",
        "emoji": "💨",
        "badge": "Chemistry · Master Suite",
        "workspace_url": "../../chemistry/gases/index.html",
        "workspace_label": "Gases Workspace",
    },
    "core1a-chemistry-chemical-bonding-tablet.html": {
        "subject": "Chemistry",
        "title": "Chemical Bonding · 12.7\" Tablet Suite",
        "emoji": "🧪",
        "badge": "Chemistry · Core 1",
        "workspace_url": "../../chemistry/bonding/index.html",
        "workspace_label": "Bonding Workspace",
    },
    "core2-chemistry-chemical-bonding-tablet.html": {
        "subject": "Chemistry",
        "title": "Chemical Bonding Core 2 Challenge Suite",
        "emoji": "🧪",
        "badge": "Chemistry · Core 2",
        "workspace_url": "../../chemistry/bonding/index.html",
        "workspace_label": "Bonding Workspace",
    },
    "chemistry-chemical-bonding-master-suite.html": {
        "subject": "Chemistry",
        "title": "Chemical Bonding Master Suite",
        "emoji": "🧪",
        "badge": "Chemistry · Master Suite",
        "workspace_url": "../../chemistry/bonding/index.html",
        "workspace_label": "Bonding Workspace",
    },
    "core1a-chemistry-some-basic-concepts-tablet.html": {
        "subject": "Chemistry",
        "title": "Mole Concept & Stoichiometry · 12.7\" Tablet Suite",
        "emoji": "⚖️",
        "badge": "Chemistry · Core 1",
        "workspace_url": "../../chemistry/some-basic-concepts/index.html",
        "workspace_label": "Mole Workspace",
    },
    "core2-chemistry-some-basic-concepts-tablet.html": {
        "subject": "Chemistry",
        "title": "Mole Concept Core 2 Challenge Suite",
        "emoji": "⚖️",
        "badge": "Chemistry · Core 2",
        "workspace_url": "../../chemistry/some-basic-concepts/index.html",
        "workspace_label": "Mole Workspace",
    },
    "chemistry-mole-concept-master-suite.html": {
        "subject": "Chemistry",
        "title": "Some Basic Concepts & Mole Master Suite",
        "emoji": "⚖️",
        "badge": "Chemistry · Master Suite",
        "workspace_url": "../../chemistry/some-basic-concepts/index.html",
        "workspace_label": "Mole Workspace",
    },
    "core1a-chemistry-redox-reactions-tablet.html": {
        "subject": "Chemistry",
        "title": "Redox Reactions · 12.7\" Tablet Suite",
        "emoji": "⚡",
        "badge": "Chemistry · Core 1",
        "workspace_url": "../../chemistry/redox/index.html",
        "workspace_label": "Redox Workspace",
    },
    "core2-chemistry-redox-reactions-tablet.html": {
        "subject": "Chemistry",
        "title": "Redox Reactions Core 2 Challenge Suite",
        "emoji": "⚡",
        "badge": "Chemistry · Core 2",
        "workspace_url": "../../chemistry/redox/index.html",
        "workspace_label": "Redox Workspace",
    },
    "chemistry-redox-reactions-master-suite.html": {
        "subject": "Chemistry",
        "title": "Redox Reactions Master Suite",
        "emoji": "⚡",
        "badge": "Chemistry · Master Suite",
        "workspace_url": "../../chemistry/redox/index.html",
        "workspace_label": "Redox Workspace",
    },

    # Mathematics
    "core1a-mathematics-euclids-geometry-tablet.html": {
        "subject": "Mathematics",
        "title": "Euclid's Geometry · 12.7\" Tablet Suite",
        "emoji": "📐",
        "badge": "Mathematics · Core 1",
        "workspace_url": "../../mathematics/euclids-geometry/index.html",
        "workspace_label": "Euclid Workspace",
    },
    "core2-mathematics-euclids-geometry-tablet.html": {
        "subject": "Mathematics",
        "title": "Euclid's Geometry Core 2 Challenge Suite",
        "emoji": "📐",
        "badge": "Mathematics · Core 2",
        "workspace_url": "../../mathematics/euclids-geometry/index.html",
        "workspace_label": "Euclid Workspace",
    },
    "core1a-mathematics-theory-of-equations-tablet.html": {
        "subject": "Mathematics",
        "title": "Theory of Equations · 12.7\" Tablet Suite",
        "emoji": "🔢",
        "badge": "Mathematics · Core 1",
        "workspace_url": "../../mathematics/theory-of-equations/index.html",
        "workspace_label": "Equations Workspace",
    },
    "core2-mathematics-theory-of-equations-tablet.html": {
        "subject": "Mathematics",
        "title": "Theory of Equations Core 2 Challenge Suite",
        "emoji": "🔢",
        "badge": "Mathematics · Core 2",
        "workspace_url": "../../mathematics/theory-of-equations/index.html",
        "workspace_label": "Equations Workspace",
    },
    "vector-algebra-3d-master-suite.html": {
        "subject": "Mathematics",
        "title": "Vector Algebra · 3D Master Suite",
        "emoji": "📐",
        "badge": "Mathematics · Master Suite",
        "workspace_url": "../../mathematics/vectors/index.html",
        "workspace_label": "Vectors Workspace",
    },

    # Physics
    "core1a-physics-motion-2d-ncert-tablet.html": {
        "subject": "Physics",
        "title": "Motion in 2D · NCERT Foundation Tablet",
        "emoji": "🌀",
        "badge": "Physics · Core 1",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core1a-sba-motion-in-a-plane-master-tablet.html": {
        "subject": "Physics",
        "title": "Motion in a Plane SBA Master Suite",
        "emoji": "🎯",
        "badge": "Physics · SBA Master",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core1a-sba-06-07-trajectory-and-height-tablet.html": {
        "subject": "Physics",
        "title": "Trajectory & Height SBA Tablet",
        "emoji": "🎯",
        "badge": "Physics · SBA 06/07",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core2-motion-in-a-plane-tablet.html": {
        "subject": "Physics",
        "title": "Motion in a Plane Core 2 Challenge Suite",
        "emoji": "🎯",
        "badge": "Physics · Core 2",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core1a-motion-in-a-plane-tablet.html": {
        "subject": "Physics",
        "title": "Motion in a Plane Construction Tablet",
        "emoji": "🎯",
        "badge": "Physics · Construction",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core2a-projectile-study.html": {
        "subject": "Physics",
        "title": "Projectile Motion Core 2A Study Suite",
        "emoji": "🎯",
        "badge": "Physics · Core 2A",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "motion-in-2d-master-suite.html": {
        "subject": "Physics",
        "title": "Motions in 2D Master Suite",
        "emoji": "🌀",
        "badge": "Physics · Master Suite",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "physics-motion-in-a-plane-interactive-suite.html": {
        "subject": "Physics",
        "title": "Motion in a Plane Interactive Research Suite",
        "emoji": "🎯",
        "badge": "Physics · Interactive",
        "workspace_url": "../../physics/motion-2d/index.html",
        "workspace_label": "Motion 2D Workspace",
    },
    "core1a-physics-nlm-tablet.html": {
        "subject": "Physics",
        "title": "Newton's Laws of Motion · 12.7\" Tablet Suite",
        "emoji": "🍎",
        "badge": "Physics · Core 1",
        "workspace_url": "../../physics/nlm/index.html",
        "workspace_label": "NLM Workspace",
    },
    "core1a-physics-vectors-tablet.html": {
        "subject": "Physics",
        "title": "Vector Algebra & Resolution Tablet",
        "emoji": "↗️",
        "badge": "Physics · Core 1",
        "workspace_url": "../../physics/vectors/index.html",
        "workspace_label": "Vectors Workspace",
    },
    "core1a-vector-add-sub-tablet.html": {
        "subject": "Physics",
        "title": "Vector Addition & Subtraction Tablet",
        "emoji": "↗️",
        "badge": "Physics · Construction",
        "workspace_url": "../../physics/vectors/index.html",
        "workspace_label": "Vectors Workspace",
    },
    "core1a-physics-thrust-pressure-tablet.html": {
        "subject": "Physics",
        "title": "Thrust & Hydrostatic Pressure Tablet",
        "emoji": "🌊",
        "badge": "Physics · Core 1",
        "workspace_url": "../../physics/fluids/index.html",
        "workspace_label": "Fluids Workspace",
    },
    "core2-physics-thrust-pressure-tablet.html": {
        "subject": "Physics",
        "title": "Thrust & Hydrostatic Pressure Core 2 Suite",
        "emoji": "🌊",
        "badge": "Physics · Core 2",
        "workspace_url": "../../physics/fluids/index.html",
        "workspace_label": "Fluids Workspace",
    },
    "core2-motion-consolidated-practice-tablet.html": {
        "subject": "Physics",
        "title": "Motion Consolidated Practice Suite",
        "emoji": "🏎️",
        "badge": "Physics · Consolidated",
        "workspace_url": "../../physics/motion-1d/index.html",
        "workspace_label": "Motion 1D Workspace",
    },
    "motion-in-1d-master-suite.html": {
        "subject": "Physics",
        "title": "Motion in One Dimension Master Suite",
        "emoji": "🏎️",
        "badge": "Physics · Master Suite",
        "workspace_url": "../../physics/motion-1d/index.html",
        "workspace_label": "Motion 1D Workspace",
    },

    # General
    "core2-canonical-question-bank-tablet.html": {
        "subject": "General",
        "title": "Canonical Question Bank Tablet Suite",
        "emoji": "📚",
        "badge": "Grade9 · Question Bank",
        "workspace_url": "../../question-bank/index.html",
        "workspace_label": "Question Bank",
    },
}

REQUIRED_CSS = """
/* Standard App Header & Navigation Styles */
header.app-header {
  background-color: var(--bg-surface, #0f172a);
  border-bottom: 1.5px solid var(--border, #263859);
  padding: 14px 24px;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

[data-theme="light"] header.app-header {
  background-color: #ffffff;
  border-bottom-color: #cbd5e1;
}

.header-inner {
  max-width: var(--tab12-container-max, 1400px);
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 16px;
  flex-wrap: wrap;
}

.header-brand h1 {
  font-size: 20px;
  font-weight: 800;
  color: var(--text-primary, #f8fafc);
  display: flex;
  align-items: center;
  gap: 10px;
  margin: 0;
}

[data-theme="light"] .header-brand h1 {
  color: #0f172a;
}

.subject-badge {
  font-size: 14px;
  text-transform: uppercase;
  padding: 4px 10px;
  border-radius: 999px;
  background-color: rgba(56, 189, 248, 0.15);
  color: var(--accent, #38bdf8);
  border: 1px solid var(--accent, #38bdf8);
  font-weight: 700;
}

.nav-hub-btn {
  background-color: var(--bg-card, #152238);
  color: var(--text-primary, #f8fafc);
  border: 1.5px solid var(--border, #263859);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 600;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-height: 44px;
  cursor: pointer;
  transition: all 0.15s ease;
  white-space: nowrap;
}

[data-theme="light"] .nav-hub-btn {
  background-color: #f1f5f9;
  color: #0f172a;
  border-color: #cbd5e1;
}

.nav-hub-btn:hover {
  border-color: var(--accent, #38bdf8);
  background-color: var(--bg-card-subtle, #1a2942);
}

[data-theme="light"] .nav-hub-btn:hover {
  background-color: #e2e8f0;
}

.theme-toggle-btn {
  background-color: var(--bg-card, #152238);
  color: var(--text-primary, #f8fafc);
  border: 1.5px solid var(--border, #263859);
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  white-space: nowrap;
}

[data-theme="light"] .theme-toggle-btn {
  background-color: #f1f5f9;
  color: #0f172a;
  border-color: #cbd5e1;
}
"""


def build_app_header(cfg: dict) -> str:
    return f"""  <header class="app-header">
    <div class="header-inner">
      <div class="header-brand">
        <h1>
          <span>{cfg['emoji']}</span> {cfg['title']}
          <span class="subject-badge">{cfg['badge']}</span>
        </h1>
      </div>
      <div class="header-actions" style="display:flex;align-items:center;gap:10px;">
        <button type="button" onclick="if(document.referrer &amp;&amp; document.referrer.indexOf(window.location.host) !== -1){{history.back();}}else{{location.href='{cfg['workspace_url']}';}}" class="nav-hub-btn" aria-label="Previous Page" title="Back to Previous Page">← Previous Page</button>
        <a href="{cfg['workspace_url']}" class="nav-hub-btn" aria-label="Back to Topic Workspace" title="Back to {cfg['workspace_label']}">{cfg['workspace_label']}</a>
        <a href="../../index.html" class="nav-hub-btn" aria-label="Portal Home" title="Portal Home">⚡ Home</a>
        <button id="themeToggle" class="theme-toggle-btn" aria-label="Toggle Theme">🌓 Mode</button>
      </div>
    </div>
  </header>"""


def process_tablet(file_path: Path, cfg: dict):
    content = file_path.read_text(encoding="utf-8", errors="ignore")

    # 1. Check if <nav class="tab-nav"> or .tabs-scroll-row exists
    tab_nav_match = re.search(r'(<nav[^>]*class=["\'][^"\']*tab-nav[^"\']*["\'][^>]*>.*?</nav>)', content, flags=re.DOTALL)
    tabs_scroll_match = re.search(r'(<div[^>]*class=["\'][^"\']*tabs-scroll-row[^"\']*["\'][^>]*>.*?</div>)', content, flags=re.DOTALL)
    
    tab_buttons_html = ""
    if tab_nav_match:
        tab_nav_content = tab_nav_match.group(1)
        buttons = re.findall(r'<button[^>]*>.*?</button>', tab_nav_content, flags=re.DOTALL)
        if buttons:
            sidebar_buttons = []
            for b in buttons:
                styled_b = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 btn"', b)
                styled_b = re.sub(r'>', r' style="min-height:36px; padding:6px 12px; font-size:14px; text-align:left; border:1px solid var(--border); border-radius:6px; background:var(--bg-surface); color:var(--text-primary); cursor:pointer; width:100%; display:flex; align-items:center;">', styled_b, count=1)
                sidebar_buttons.append(styled_b)
            tab_buttons_html = "\n          ".join(sidebar_buttons)
        # Remove the tab-nav
        content = content.replace(tab_nav_match.group(1), "")

    if tabs_scroll_match:
        tabs_content = tabs_scroll_match.group(1)
        buttons = re.findall(r'<button[^>]*>.*?</button>', tabs_content, flags=re.DOTALL)
        if buttons and not tab_buttons_html:
            sidebar_buttons = []
            for b in buttons:
                styled_b = re.sub(r'class=["\']([^"\']*)["\']', r'class="\1 btn"', b)
                styled_b = re.sub(r'>', r' style="min-height:36px; padding:6px 12px; font-size:14px; text-align:left; border:1px solid var(--border); border-radius:6px; background:var(--bg-surface); color:var(--text-primary); cursor:pointer; width:100%; display:flex; align-items:center;">', styled_b, count=1)
                sidebar_buttons.append(styled_b)
            tab_buttons_html = "\n          ".join(sidebar_buttons)
        content = content.replace(tabs_scroll_match.group(1), "")

    # 2. Inject study modules into sidebar if found and not already present
    if tab_buttons_html and "Study Modules" not in content and "Study Sections" not in content:
        module_widget = f"""
      <div class="support-widget" style="margin-bottom:16px;">
        <h3><span>📑</span> Study Modules</h3>
        <div style="display:flex; flex-direction:column; gap:6px;">
          {tab_buttons_html}
        </div>
      </div>
"""
        aside_match = re.search(r'(<aside[^>]*>)', content)
        if aside_match:
            content = content[:aside_match.end()] + module_widget + content[aside_match.end():]

    # 3. Replace existing header with standard app-header
    new_header = build_app_header(cfg)

    # Check for existing headers:
    # Pattern A: <header class="app-header">...</header>
    app_hdr_match = re.search(r'<header[^>]*class=["\'][^"\']*app-header[^"\']*["\'][^>]*>.*?</header>', content, flags=re.DOTALL)
    # Pattern B: <header class="top-nav">...</header>
    top_nav_match = re.search(r'<header[^>]*class=["\'][^"\']*top-nav[^"\']*["\'][^>]*>.*?</header>', content, flags=re.DOTALL)
    # Pattern C: <header data-g9-shell-header[^>]*>.*?</header>
    shell_hdr_match = re.search(r'<header[^>]*data-g9-shell-header[^>]*>.*?</header>', content, flags=re.DOTALL)

    if app_hdr_match:
        content = content[:app_hdr_match.start()] + new_header + content[app_hdr_match.end():]
    elif top_nav_match:
        content = content[:top_nav_match.start()] + new_header + content[top_nav_match.end():]
    elif shell_hdr_match:
        content = content[:shell_hdr_match.start()] + new_header + content[shell_hdr_match.end():]
    else:
        # Insert after <body>
        body_match = re.search(r'<body[^>]*>', content)
        if body_match:
            content = content[:body_match.end()] + "\n" + new_header + content[body_match.end():]

    # 4. Remove any orphaned breadcrumbs like <nav data-g9-breadcrumb>...</nav>
    content = re.sub(r'<nav[^>]*data-g9-breadcrumb[^>]*>.*?</nav>', '', content, flags=re.DOTALL)

    # 5. Inject REQUIRED_CSS before </head> if .nav-hub-btn is not already in style
    if ".nav-hub-btn" not in content:
        head_end = content.find("</head>")
        if head_end != -1:
            css_block = f"<style id=\"tablet-standard-header-css\">{REQUIRED_CSS}</style>\n"
            content = content[:head_end] + css_block + content[head_end:]

    # 6. Ensure themeToggle script is hooked up properly
    if "tablet12_theme" not in content:
        theme_script = """
<script>
  (function() {
    const themeBtn = document.getElementById('themeToggle');
    if (!themeBtn) return;
    const htmlEl = document.documentElement;
    const savedTheme = localStorage.getItem('tablet12_theme') || 'dark';
    htmlEl.setAttribute('data-theme', savedTheme);
    themeBtn.addEventListener('click', function() {
      const current = htmlEl.getAttribute('data-theme');
      const next = current === 'dark' ? 'light' : 'dark';
      htmlEl.setAttribute('data-theme', next);
      localStorage.setItem('tablet12_theme', next);
    });
  })();
</script>
"""
        body_end = content.rfind("</body>")
        if body_end != -1:
            content = content[:body_end] + theme_script + content[body_end:]

    file_path.write_text(content, encoding="utf-8")
    print(f"Standardized {file_path.name}")


def main():
    for filename, cfg in TABLET_CONFIG.items():
        p = PRACTICE_DIR / filename
        if p.exists():
            process_tablet(p, cfg)
        else:
            print(f"Warning: {filename} not found!")


if __name__ == "__main__":
    main()
