from __future__ import annotations
from collections import Counter
from pathlib import Path
import re, unittest
from urllib.parse import unquote, urlsplit
ROOT=Path(__file__).resolve().parents[1]
ROOT_PAGES=[ROOT/"standalone/core1a-motion-1d-straight-line-tablet.html",ROOT/"standalone/core1a-motion-in-a-plane-tablet.html",ROOT/"standalone/core1a-physics-nlm-tablet.html",ROOT/"standalone/core1a-vector-add-sub-tablet.html",ROOT/"standalone/core2-motion-in-a-plane-tablet.html",ROOT/"standalone/core2-physics-thrust-pressure-tablet.html"]
PRACTICE=[ROOT/"standalone/practice"/n for n in ["core1a-physics-motion-2d-ncert-tablet.html","core1a-physics-nlm-tablet.html","core1a-physics-vectors-tablet.html","core1a-sba-06-07-trajectory-and-height-tablet.html","core1a-sba-motion-in-a-plane-master-tablet.html","core2-motion-1d-straight-line-tablet.html","core2-motion-consolidated-practice-tablet.html","core2-motion-in-a-plane-tablet.html","core2-physics-thrust-pressure-tablet.html","core2a-projectile-study.html","index.html","motion-in-1d-master-suite.html","motion-in-2d-master-suite.html","physics-motion-in-a-plane-interactive-suite.html"]]
PAGES=ROOT_PAGES+PRACTICE
ATTR=re.compile(r"(?:href|src|action|poster)=[\"']([^\"']+)[\"']",re.I); IDS=re.compile(r"id=[\"']([^\"']+)[\"']",re.I); REMOTE=re.compile(r"<(?:script|link|img|iframe|source|embed|object|video|audio)[^>]*(?:src|href|data|poster)=[\"']https?://",re.I)
def ids(p): return set(IDS.findall(p.read_text(encoding="utf-8")))
class TestPR375U2Standalone(unittest.TestCase):
 def test_denominator(self):
  self.assertEqual(20,len(PAGES)); [self.assertTrue(p.is_file(),p) for p in PAGES]
 def test_offline_dependencies(self):
  for p in PAGES:
   s=p.read_text(encoding="utf-8"); self.assertIsNone(REMOTE.search(s),p); self.assertNotIn("www.gstatic.com/antigravity/web/dev/tailwindcss.min.js",s); self.assertNotIn("../../public/vendor/katex/0.16.8/",s)
  self.assertTrue((ROOT/"standalone/vendor/katex/0.16.8/katex.min.css").is_file()); self.assertTrue((ROOT/"standalone/vendor/tailwind/3.4.17/tailwind-play.js").is_file())
 def test_links_and_fragments(self):
  cache={p.resolve():ids(p) for p in PAGES}
  for p in PAGES:
   for ref in ATTR.findall(p.read_text(encoding="utf-8")):
    ref=ref.strip()
    if not ref or ref.startswith(("#","?","data:","javascript:","mailto:","tel:","blob:","//")): continue
    u=urlsplit(ref)
    if u.scheme in {"http","https"}: continue
    target=(p.parent/unquote(u.path)).resolve(); self.assertTrue(target.exists(),f"{p}: {ref}")
    if u.fragment and target.suffix.lower() in {".html",".htm"}: self.assertIn(unquote(u.fragment),cache.setdefault(target,ids(target)),f"{p}: {ref}")
 def test_duplicate_ids(self):
  p=ROOT/"standalone/practice/motion-in-2d-master-suite.html"
  s=p.read_text(encoding="utf-8")
  self.assertEqual(1,s.count('id="sbTeacherChalk"'))
 def test_root_legacy_links_gone(self):
  for p in ROOT_PAGES:
   s=p.read_text(encoding="utf-8"); self.assertNotIn('href="../index.html"',s); self.assertNotIn('href="../question-bank/index.html"',s); self.assertNotRegex(s,r'href="core[12]a?\.html#')
 def test_hub(self):
  s=(ROOT/"standalone/practice/index.html").read_text(encoding="utf-8"); self.assertEqual(13,len(re.findall(r'<a class="card" href="[^"]+">',s))); self.assertIn("59 questions",s); self.assertRegex(s,r'<div class="number">7</div><div class="label">Topics</div>'); self.assertRegex(s,r'<div class="number">0</div><div class="label">Remote CDN</div>')
 def test_jumps(self):
  s=(ROOT/"standalone/practice/core2-motion-in-a-plane-tablet.html").read_text(encoding="utf-8"); self.assertIn("function jumpToQuestion(qId)",s); self.assertEqual(59,len(re.findall(r'onclick="jumpToQuestion\(\'q\d{2}\'\); return false;"',s))); self.assertNotIn("min-height:36px;min-width:36px",s)
 def test_return_targets(self):
  for p in [x for x in PRACTICE if x.name!="index.html"]:
   s=p.read_text(encoding="utf-8"); self.assertIn('href="index.html"',s,p); self.assertIn('id="u2-practice-hub-target"',s,p)
