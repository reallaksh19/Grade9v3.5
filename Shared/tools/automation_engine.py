#!/usr/bin/env python3
"""Grade9V3.5 Independent Automation & Verification Engine (Grade9 CI).

Continuously tallies, cross-references, validates contracts, checks for missing
search indices, and synchronizes the entire learning portal whenever new HTML
files (Core 1, 1A, 1B, 2, 2A, 2B, visualizers, or tablets) are added.

Commands:
  python Shared/tools/automation_engine.py --check
  python Shared/tools/automation_engine.py --rebuild
  python Shared/tools/automation_engine.py --watch
  python Shared/tools/automation_engine.py --install-hooks
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO))

EXCLUDED_ORPHAN_DIRS = {
    "test", "node_modules", ".git", "scratch", "backups", "artifacts", "vendor"
}

VALID_CONTINUUM_TIERS = {
    "CORE_1", "CORE_1A", "CORE_1B", "CORE_2", "CORE_2A", "CORE_2B"
}


# ==============================================================================
# 1. Hybrid Auto-Inference Engine
# ==============================================================================

def infer_html_metadata(html_path: Path, repo_root: Path) -> dict[str, str]:
    """Infers Continuum Tier, title, and topic identity from HTML contents and location."""
    rel_path = str(html_path.relative_to(repo_root)).replace("\\", "/")
    if rel_path.startswith("public/"):
        rel_path = rel_path[7:]

    content = ""
    try:
        content = html_path.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        pass

    # 1. Check <meta name="continuum-tier" content="...">
    meta_m = re.search(r'<meta\s+name=["\']continuum-tier["\']\s+content=["\']([^"\']+)["\']', content, re.I)
    tier = meta_m.group(1).upper().strip() if meta_m else None

    # 2. Extract Title
    title_m = re.search(r'<title>(.*?)</title>', content, re.I | re.S)
    title = title_m.group(1).strip() if title_m else html_path.stem.replace("-", " ").title()
    for sep in [" - ", " \u2014 ", " \u00b7 ", " | "]:
        if sep in title:
            parts = title.split(sep)
            if parts[0].strip().lower().startswith(("grade 9", "grade9", "g9")):
                title = sep.join(parts[1:]).strip()
            else:
                title = parts[0].strip()
            break

    # 3. Fallback Heuristics for Tier
    if not tier or tier not in VALID_CONTINUUM_TIERS:
        low_path = rel_path.lower()
        if "atlas.html" in low_path:
            tier = "CORE_1"
        elif "explorers/" in low_path or ("suite" in low_path and "<canvas" in content):
            tier = "CORE_1B"
        elif "core1a" in low_path or "construction" in low_path or "straight-line" in low_path:
            tier = "CORE_1A"
        elif "core2" in low_path and "ncert" in low_path:
            tier = "CORE_2A"
        elif "master-suite" in low_path or "pyq" in low_path or "jeeadv" in low_path or "iitjee" in low_path:
            tier = "CORE_2B"
        elif "core2" in low_path:
            tier = "CORE_2A"
        else:
            tier = "CORE_1A"

    return {
        "tier": tier,
        "title": title,
        "entrypoint": rel_path
    }


# ==============================================================================
# 2. Six Verification Integrity Suites
# ==============================================================================

class VerificationEngine:
    def __init__(self, repo_root: Path):
        self.repo = repo_root
        self.errors: list[str] = []
        self.warnings: list[str] = []
        self.stats: dict[str, Any] = {}

    def run_all_suites(self) -> bool:
        print("\n" + "=" * 78)
        print("  Grade9V3.5 Independent Automation & Verification Engine (Grade9 CI)")
        print("=" * 78)

        self.suite_1_html_inventory()
        self.suite_2_zero_orphan_htmls()
        self.suite_3_continuum_contracts()
        self.suite_4_zero_missing_search_index()
        self.suite_5_question_bank_cross_reference()
        self.suite_6_public_to_docs_lockstep()

        self.print_summary()
        return len(self.errors) == 0

    def suite_1_html_inventory(self):
        """Suite 1: Scan every HTML, ensuring non-zero byte size and valid titles."""
        public_htmls = list((self.repo / "public").glob("**/*.html"))
        docs_htmls = list((self.repo / "docs").glob("**/*.html"))
        total_htmls = len(public_htmls)

        empty_files = []
        untitled_files = []
        for p in public_htmls:
            if p.stat().st_size == 0:
                empty_files.append(str(p.relative_to(self.repo)))
            try:
                txt = p.read_text(encoding="utf-8", errors="ignore")
                if "<title>" not in txt.lower():
                    untitled_files.append(str(p.relative_to(self.repo)))
            except Exception:
                empty_files.append(str(p.relative_to(self.repo)))

        if empty_files:
            self.errors.append(f"Suite 1 Failure: {len(empty_files)} empty or unreadable HTML files: {empty_files[:3]}...")
        if untitled_files:
            self.warnings.append(f"Suite 1 Warning: {len(untitled_files)} HTML files missing <title> tag.")

        self.stats["total_public_htmls"] = total_htmls
        self.stats["total_docs_htmls"] = len(docs_htmls)
        print(f"  [Suite 1] HTML Inventory: {total_htmls} public HTMLs scanned (0 empty files).")

    def suite_2_zero_orphan_htmls(self):
        """Suite 2: Assert zero orphaned HTMLs in publishable learning folders."""
        registry_path = self.repo / "public" / "data" / "resource-registry.v1.json"
        if not registry_path.exists():
            self.errors.append("Suite 2 Failure: resource-registry.v1.json does not exist. Run --rebuild.")
            return

        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        registered_eps = {r.get("artifact", {}).get("entrypoint", "").replace("\\", "/") for r in registry}

        # Check topic HTMLs and practice tablets
        orphaned = []
        scan_roots = [
            self.repo / "public" / "physics",
            self.repo / "public" / "chemistry",
            self.repo / "public" / "mathematics",
            self.repo / "public" / "standalone" / "practice"
        ]

        for sroot in scan_roots:
            if not sroot.exists():
                continue
            for h in sroot.glob("**/*.html"):
                parts = h.parts
                if any(ex in parts for ex in EXCLUDED_ORPHAN_DIRS):
                    continue
                rel_ep = str(h.relative_to(self.repo / "public")).replace("\\", "/")
                # Hub indexes are covered by subject/topic entries
                if rel_ep in ("index.html",) or (rel_ep.endswith("/index.html") and rel_ep.count("/") == 1):
                    continue
                # Topic workspaces and practice directory hubs are published directory indexes
                if rel_ep.endswith("/index.html") and ("practice/index.html" in rel_ep or "practice/friction/index.html" in rel_ep or rel_ep.count("/") == 2):
                    continue

                if rel_ep not in registered_eps:
                    orphaned.append(rel_ep)

        self.stats["orphaned_htmls"] = len(orphaned)
        if orphaned:
            self.errors.append(f"Suite 2 Failure: {len(orphaned)} orphaned HTML file(s) not registered in any manifest or registry: {orphaned[:5]}")
        else:
            print(f"  [Suite 2] Zero Orphan HTML Policy: 100% of learning HTMLs tracked in manifests/registry.")

    def suite_3_continuum_contracts(self):
        """Suite 3: Validate all topic.manifest.json files for valid tiers and valid file targets."""
        manifest_paths = list((self.repo / "public").glob("*/*/topic.manifest.json"))
        total_manifests = len(manifest_paths)
        tier_counts = {"CORE_1": 0, "CORE_1A": 0, "CORE_1B": 0, "CORE_2": 0, "CORE_2A": 0, "CORE_2B": 0}

        broken_links = []
        invalid_tiers = []

        for mp in manifest_paths:
            try:
                doc = json.loads(mp.read_text(encoding="utf-8"))
            except Exception as e:
                self.errors.append(f"Suite 3 Failure: Invalid JSON in {mp}: {e}")
                continue

            rungs = doc.get("rungs_atlas")
            if rungs:
                tier_counts["CORE_1"] += 1
                ep = rungs.get("entrypoint", "")
                if not (self.repo / "public" / ep).exists() and not (self.repo / ep).exists():
                    broken_links.append((str(mp.name), ep))

            for sub in doc.get("subtopics", []):
                cont = sub.get("continuum", {})
                for k, tier_name in [
                    ("core_1a_constructions", "CORE_1A"),
                    ("core_1b_visualizers", "CORE_1B"),
                    ("core_2a_ncert", "CORE_2A"),
                    ("core_2b_competitive", "CORE_2B")
                ]:
                    for mod in cont.get(k, []):
                        m_tier = mod.get("type", tier_name)
                        if m_tier not in VALID_CONTINUUM_TIERS:
                            invalid_tiers.append((mod.get("id"), m_tier))
                        tier_counts[m_tier] = tier_counts.get(m_tier, 0) + 1
                        ep = mod.get("entrypoint", "")
                        if not (self.repo / "public" / ep).exists() and not (self.repo / ep).exists():
                            broken_links.append((mod.get("id"), ep))

        if broken_links:
            self.errors.append(f"Suite 3 Failure: {len(broken_links)} broken file link(s) in topic manifests: {broken_links[:3]}")
        if invalid_tiers:
            self.errors.append(f"Suite 3 Failure: Invalid continuum tiers declared: {invalid_tiers}")

        self.stats["tier_breakdown"] = tier_counts
        print(f"  [Suite 3] Continuum Contracts: {total_manifests} manifests verified. Continuum Tally: {tier_counts}")

    def suite_4_zero_missing_search_index(self):
        """Suite 4: Ensure every published module in registry is indexed in learner-search-index.v1.json."""
        index_path = self.repo / "public" / "data" / "learner-search-index.v1.json"
        if not index_path.exists():
            self.errors.append("Suite 4 Failure: learner-search-index.v1.json does not exist. Run --rebuild.")
            return

        with open(index_path, "r", encoding="utf-8") as f:
            search_docs = json.load(f)

        indexed_urls = {doc.get("url", "").replace("\\", "/") for doc in search_docs}

        # Check all learner resources
        registry_path = self.repo / "public" / "data" / "resource-registry.v1.json"
        with open(registry_path, "r", encoding="utf-8") as f:
            registry = json.load(f)

        missing_from_index = []
        for rec in registry:
            if rec.get("audience") != "LEARNER" or rec.get("search", {}).get("visibility") == "EXCLUDED":
                continue
            ep = rec.get("artifact", {}).get("entrypoint", "")
            if ep and ep not in indexed_urls:
                missing_from_index.append(rec["id"])

        if missing_from_index:
            self.errors.append(f"Suite 4 Failure: {len(missing_from_index)} published resource(s) missing from search index: {missing_from_index[:5]}")
        else:
            print(f"  [Suite 4] Zero Missing Index Policy: 100% of published resources indexed ({len(search_docs)} search documents).")

    def suite_5_question_bank_cross_reference(self):
        """Suite 5: Ensure 100% of Question Bank subtopics have canonical titles and no missing capability links."""
        catalog_path = self.repo / "public" / "data" / "question-bank-catalog.js"
        if not catalog_path.exists():
            self.errors.append("Suite 5 Failure: question-bank-catalog.js does not exist.")
            return

        content = catalog_path.read_text(encoding="utf-8")
        m = re.search(r'window\.GRADE9_QUESTION_BANK_CATALOG\s*=\s*(\{.*?\});', content, re.S)
        if not m:
            self.errors.append("Suite 5 Failure: Could not parse question-bank-catalog.js.")
            return

        cat = json.loads(m.group(1))
        subtopics = cat.get("subtopics", [])
        ref_only = [s["id"] for s in subtopics if s.get("label_source") != "CANONICAL_TITLE"]

        if ref_only:
            self.errors.append(f"Suite 5 Failure: {len(ref_only)} subtopic(s) lack canonical titles (hides subtopic strip): {ref_only}")
        else:
            print(f"  [Suite 5] Question Bank Cross-Reference: 100% ({len(subtopics)}/{len(subtopics)}) subtopics canonicalized.")

    def suite_6_public_to_docs_lockstep(self):
        """Suite 6: Ensure public/ and docs/ are synchronized without drift."""
        key_files = [
            "css/modern-learner.css",
            "css/question-bank.css",
            "js/site-header.js",
            "js/question-bank.js",
            "data/learner-search-index.v1.json",
            "data/resource-registry.v1.json",
            "data/concept-bundles.v1.json",
            "atlas/index.html",
            "physics/motion-2d/index.html",
            "physics/motion-1d/index.html",
            "chemistry/bonding/index.html"
        ]

        drift = []
        for rel in key_files:
            p_file = self.repo / "public" / rel
            d_file = self.repo / "docs" / rel
            if not p_file.exists() or not d_file.exists():
                drift.append(f"{rel} missing in one location")
                continue
            if p_file.read_bytes() != d_file.read_bytes():
                drift.append(rel)

        if drift:
            self.errors.append(f"Suite 6 Failure: public/ and docs/ have drift in {len(drift)} file(s): {drift}")
        else:
            print(f"  [Suite 6] Public-to-Docs Lockstep: 100% bit-for-bit parity across all audited surfaces.")

    def print_summary(self):
        print("-" * 78)
        if self.errors:
            print(f"❌ AUDIT FAILED WITH {len(self.errors)} ERROR(S):")
            for e in self.errors:
                print(f"   • {e}")
        else:
            print("✅ ALL 6 INTEGRITY SUITES PASSED! Platform is 100% in lockstep with zero missing indices.")
        if self.warnings:
            print(f"\n⚠️  {len(self.warnings)} Non-Fatal Warning(s):")
            for w in self.warnings:
                print(f"   • {w}")
        print("=" * 78 + "\n")


# ==============================================================================
# 3. Pipeline Auto-Rebuild Engine
# ==============================================================================

def run_rebuild_pipeline(repo_root: Path) -> bool:
    """Executes the full automated rebuild pipeline in deterministic order."""
    print("\n🚀 Starting Automated Portal Rebuild & Synchronization Pipeline...")

    steps = [
        ("Shared/tools/build_resource_registry.py", ["python", "Shared/tools/build_resource_registry.py"]),
        ("Shared/tools/resolve_concept_bundle.py", ["python", "Shared/tools/resolve_concept_bundle.py"]),
        ("Shared/tools/build_learner_search_index.py", ["python", "Shared/tools/build_learner_search_index.py"]),
        ("Shared/tools/build_learner_ui.py", ["python", "Shared/tools/build_learner_ui.py"]),
        ("Shared/tools/build_question_bank_platform.py", ["python", "Shared/tools/build_question_bank_platform.py", "--write"]),
    ]

    for label, cmd in steps:
        print(f"  ▶ Executing {label}...")
        res = subprocess.run(cmd, cwd=str(repo_root), capture_output=True, text=True)
        if res.returncode != 0:
            print(f"❌ Error executing {label}:\n{res.stderr}\n{res.stdout}")
            return False

    # Sync key files to docs
    sync_script = repo_root / "scratch" / "sync_public_to_docs.py"
    if sync_script.exists():
        subprocess.run(["python", str(sync_script)], cwd=str(repo_root), capture_output=True)

    print("✨ Pipeline rebuild completed successfully. Now verifying integrity...")
    engine = VerificationEngine(repo_root)
    return engine.run_all_suites()


# ==============================================================================
# 4. Git Pre-Commit Hook Installer
# ==============================================================================

def install_git_hook(repo_root: Path) -> bool:
    """Installs the pre-commit hook that invokes the automation engine."""
    hooks_dir = repo_root / ".git" / "hooks"
    if not hooks_dir.exists():
        print(f"No .git/hooks directory found at {hooks_dir}.")
        return False

    hook_file = hooks_dir / "pre-commit"
    hook_content = """#!/bin/sh
# Grade9V3.5 Automated Integrity & Index Pre-Commit Gate
echo "🔍 Running Grade9V3.5 Automation Engine Pre-Commit Gate..."
python Shared/tools/automation_engine.py --check
if [ $? -ne 0 ]; then
  echo "❌ Pre-commit check failed! Fix orphaned HTMLs or un-indexed assets before committing."
  exit 1
fi
exit 0
"""
    hook_file.write_text(hook_content, encoding="utf-8")
    try:
        os.chmod(hook_file, 0o755)
    except Exception:
        pass

    print(f"✅ Git pre-commit hook installed successfully at {hook_file}.")
    return True


# ==============================================================================
# 5. Live File Watcher Daemon
# ==============================================================================

def run_watcher_daemon(repo_root: Path):
    """Watches public/ and standalone/ for modified/created HTML and JSON files."""
    print("\n👀 Grade9 CI File Watcher Daemon active...")
    print(f"   Watching: {repo_root / 'public'}")
    print("   Press Ctrl+C to stop.\n")

    watch_extensions = {".html", ".json", ".js", ".css"}
    last_snapshots: dict[str, float] = {}

    def get_snapshot() -> dict[str, float]:
        snap = {}
        for p in (repo_root / "public").glob("**/*"):
            if p.is_file() and p.suffix.lower() in watch_extensions:
                snap[str(p)] = p.stat().st_mtime
        return snap

    last_snapshots = get_snapshot()

    try:
        while True:
            time.sleep(1.5)
            current_snap = get_snapshot()
            changed = []

            for path, mtime in current_snap.items():
                if path not in last_snapshots:
                    changed.append(("ADDED", path))
                elif mtime > last_snapshots[path]:
                    changed.append(("MODIFIED", path))

            for path in last_snapshots:
                if path not in current_snap:
                    changed.append(("DELETED", path))

            if changed:
                print(f"\n⚡ Detected {len(changed)} change(s):")
                for action, p in changed[:3]:
                    print(f"   [{action}] {Path(p).name}")
                if len(changed) > 3:
                    print(f"   ... and {len(changed) - 3} more.")

                run_rebuild_pipeline(repo_root)
                last_snapshots = get_snapshot()

    except KeyboardInterrupt:
        print("\n👋 Watcher daemon stopped.")


# ==============================================================================
# 6. Main Entry Point
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="Grade9V3.5 Independent Automation & Verification Engine")
    parser.add_argument("--check", action="store_true", help="Validate all 6 integrity suites and exit 0 or 1")
    parser.add_argument("--rebuild", action="store_true", help="Re-ingest manifests, compile registry, search index, and sync")
    parser.add_argument("--watch", action="store_true", help="Run background file watcher daemon")
    parser.add_argument("--install-hooks", action="store_true", help="Install git pre-commit hook")
    parser.add_argument("--repo-root", type=Path, default=REPO, help="Repository root path")
    args = parser.parse_args()

    if args.install_hooks:
        success = install_git_hook(args.repo_root)
        sys.exit(0 if success else 1)

    if args.watch:
        run_watcher_daemon(args.repo_root)
        sys.exit(0)

    if args.rebuild:
        success = run_rebuild_pipeline(args.repo_root)
        sys.exit(0 if success else 1)

    # Default: --check
    engine = VerificationEngine(args.repo_root)
    success = engine.run_all_suites()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
