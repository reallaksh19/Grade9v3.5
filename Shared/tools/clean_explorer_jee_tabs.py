#!/usr/bin/env python3
"""Remove internal duplicate IIT-JEE question hub tabs from opaque explorers and link directly to canonical Question Bank."""

import re
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]

EXPLORERS = [
    REPO / "public" / "chemistry" / "bonding" / "explorers" / "chemical_bonding" / "index.html",
    REPO / "public" / "chemistry" / "gases" / "explorers" / "behaviour_of_gases" / "index.html",
    REPO / "public" / "chemistry" / "redox" / "explorers" / "redox_reactions" / "index.html",
    REPO / "public" / "chemistry" / "some-basic-concepts" / "explorers" / "mole_concept" / "index.html",
    REPO / "public" / "mathematics" / "vectors" / "explorers" / "vector_algebra" / "index.html",
    REPO / "public" / "physics" / "motion-1d" / "explorers" / "motion_in_1d" / "index.html",
    REPO / "public" / "physics" / "motion-in-2d" / "explorers" / "motions_in_2d" / "index.html",
]

STANDALONE = [
    REPO / "public" / "standalone" / "practice" / "motion-in-1d-master-suite.html",
    REPO / "public" / "standalone" / "practice" / "motion-in-2d-master-suite.html",
]

def clean_file(path: Path, is_standalone: bool = False):
    if not path.is_file():
        return
    txt = path.read_text(encoding="utf-8")
    orig_len = len(txt)
    qb_rel = "../../question-bank/index.html?exam=IIT-JEE+Diagnostic" if is_standalone else "../../../../question-bank/index.html?exam=IIT-JEE+Diagnostic"

    # 1. Replace switchTab('tab-quiz') header buttons
    txt = re.sub(
        r'<button\s+onclick=["\']switchTab\([\'"]tab-quiz[\'"]\)["\'][^>]*>.*?</button>',
        f'<a href="{qb_rel}" class="touch-target px-3.5 py-1.5 rounded-xl bg-gradient-to-r from-purple-600/30 to-indigo-600/30 hover:from-purple-600/50 hover:to-indigo-600/50 border border-purple-500/40 text-purple-200 text-[13px] font-bold transition flex items-center gap-2"><span>🎯</span><span>IIT-JEE Questions in QB &rarr;</span></a>',
        txt,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 2. Replace tab bar buttons for quiz
    txt = re.sub(
        r'<button[^>]*id=["\']btn-tab-quiz["\'][^>]*>.*?</button>',
        f'<a href="{qb_rel}" id="btn-tab-quiz" class="tab-btn-inactive px-3 py-2 rounded-t-lg transition whitespace-nowrap flex items-center gap-1.5 text-purple-300 hover:text-white" title="Open authentic IIT-JEE questions in canonical Question Bank"><span>🎯 Questions in QB &rarr;</span></a>',
        txt,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 3. For motion-in-2d specific buttons
    txt = re.sub(
        r'<button[^>]*id=["\']nav-quiz["\'][^>]*>.*?</button>',
        f'<a href="{qb_rel}" id="nav-quiz" class="tab-btn-inactive px-3 py-2 rounded-xl transition whitespace-nowrap text-purple-300 hover:text-white" title="Open authentic IIT-JEE questions in canonical Question Bank"><span>🎯 Questions in QB &rarr;</span></a>',
        txt,
        flags=re.DOTALL | re.IGNORECASE
    )

    # 4. Remove the quiz sections
    txt = re.sub(r'<section\s+id=["\']tab-quiz["\'][^>]*>.*?</section>', '<!-- IIT-JEE questions moved to Question Bank -->', txt, flags=re.DOTALL | re.IGNORECASE)
    txt = re.sub(r'<section\s+id=["\']tab-quiz-content["\'][^>]*>.*?</section>', '<!-- IIT-JEE questions moved to Question Bank -->', txt, flags=re.DOTALL | re.IGNORECASE)

    path.write_text(txt, encoding="utf-8")
    print(f"Cleaned {path.name}: {orig_len} -> {len(txt)} bytes")

    # Sync to docs if in public
    if "public" in path.parts:
        docs_path = REPO / "docs" / path.relative_to(REPO / "public")
        if docs_path.parent.is_dir():
            docs_path.write_text(txt, encoding="utf-8")

def main():
    for p in EXPLORERS:
        clean_file(p, is_standalone=False)
    for p in STANDALONE:
        clean_file(p, is_standalone=True)
    print("All explorer IIT-JEE tabs cleaned and linked to Question Bank.")

if __name__ == "__main__":
    main()
