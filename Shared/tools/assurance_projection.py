#!/usr/bin/env python3
"""Projection assurance checks."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Add Shared/tools to sys.path if needed
sys.path.insert(0, str(Path(__file__).resolve().parent))
try:
    from assurance_record import make_evidence, write_evidence
except ImportError:
    pass

def check_completeness(html_files: list[Path]) -> list[str]:
    fails = []
    for f in html_files:
        content = f.read_text(encoding="utf-8")
        if 'data-g9-question=' in content or 'data-question=' in content:
            # Look at content near these tags to determine if it's empty
            # The heuristic: find tag instances and their surrounding context
            tags = re.finditer(r'(data-g9-question=|data-question=)[^>]*>', content)
            is_empty = False
            for match in tags:
                end_pos = match.end()
                after = content[end_pos:end_pos+200]
                inner_text = re.sub(r'<[^>]+>', '', after)
                if len(inner_text.strip()) < 50:
                    is_empty = True
                    break
            
            if is_empty:
                fails.append(str(f))
    return fails

def check_link_integrity(html_files: list[Path], render_dir: Path) -> list[str]:
    fails = []
    for f in html_files:
        content = f.read_text(encoding="utf-8")
        links = re.findall(r'(?:href|src)="([^"]+)"', content)
        has_dead_link = False
        for link in links:
            if link.startswith(('http://', 'https://', '//', 'data:', 'mailto:', '#')):
                continue
            
            link_path = link.split('#')[0].split('?')[0]
            if not link_path:
                continue
                
            target_path = (f.parent / link_path).resolve()
            if not target_path.exists():
                has_dead_link = True
                break
                
        if has_dead_link:
            fails.append(str(f))
    return fails

def check_network_policy(html_files: list[Path]) -> list[str]:
    fails = []
    patterns = ['https://', 'http://', '//cdn.', 'gstatic.com', 'jsdelivr.net', 'unpkg.com', 'cdnjs.cloudflare.com']
    for f in html_files:
        content = f.read_text(encoding="utf-8")
        if '<!-- allowed-remote:' in content:
            continue
        if any(p in content for p in patterns):
            fails.append(str(f))
    return fails

def check_viewport(html_files: list[Path]) -> list[str]:
    fails = []
    for f in html_files:
        content = f.read_text(encoding="utf-8")
        vp_match = re.search(r'<meta[^>]*name="viewport"[^>]*content="([^"]+)"', content, re.IGNORECASE)
        if vp_match:
            vp = vp_match.group(1).lower()
            if 'width=device-width' not in vp:
                fails.append(str(f))
            elif 'user-scalable=no' in vp:
                fails.append(str(f))
            elif 'maximum-scale=1.0' in vp:
                fails.append(str(f))
    return fails

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-dir", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()

    render_dir = Path(args.render_dir)
    html_files = list(render_dir.rglob("*.html"))
    
    metrics = {
        "PROJECTION_COMPLETENESS": check_completeness(html_files),
        "LINK_INTEGRITY": check_link_integrity(html_files, render_dir),
        "NETWORK_POLICY": check_network_policy(html_files),
        "RESPONSIVE_LAYOUT": check_viewport(html_files),
    }
    
    has_error = False
    print("Assurance Projection Summary:")
    for metric, fails in metrics.items():
        outcome = "FAIL" if fails else "PASS"
        if fails:
            has_error = True
        print(f"{metric}: {outcome} ({len(fails)} issues)")
        if fails:
            for fail in fails:
                print(f"  - {fail}")
        
        evidence = make_evidence(
            assurance_type=metric,
            subject_kind="PROJECTION",
            subject_id=str(render_dir),
            outcome=outcome,
            producer_name="assurance_projection",
            producer_version="1.0",
            findings=[{"file": f} for f in fails] if fails else None
        )
        write_evidence(evidence, render_dir / f"{metric}_evidence.json")
        
    if has_error and args.enforce:
        sys.exit(1)

if __name__ == "__main__":
    main()
