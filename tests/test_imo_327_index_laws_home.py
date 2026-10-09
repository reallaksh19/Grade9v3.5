"""#327: draft Mathematics Number Systems / Index Laws routes must not grant Core access.

These pages are draft site surfaces, not academic acceptance and not an
alternative implementation of the authoritative Core product renderer.
"""
from __future__ import annotations
import copy
from html.parser import HTMLParser
import json
import posixpath
import unittest
from pathlib import Path
from urllib.parse import urlsplit

from Shared.tools import build_pages_site

ROOT = Path(__file__).resolve().parents[1]
PARENT = "mathematics/number-systems/index.html"
CHILD = "mathematics/number-systems/index-laws/index.html"
ROLES = {"CORE1A": "CANDIDATE_NOT_PUBLISHED",
         "CORE2A": "CANDIDATE_NOT_PUBLISHED",
         "CORE2": "SOURCE_CUSTODY_AND_RIGHTS_HOLD"}


class Collect(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.roles = []
        self.role_links = []
        self.headers = []
        self.main = []
        self.breadcrumb = False
        self.depth = 0
        self.article = None
        self.headline = ""
        self.source = ""

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main":
            self.main.append(a)
        if tag in ("h1", "h2", "h3"):
            self.headline = tag
        if tag == "article":
            self.depth += 1
            if a.get("data-g9-role"):
                self.article = a
                self.roles.append(a)
        if tag == "a":
            self.links.append(a.get("href", ""))
            if self.article is not None:
                self.role_links.append(a.get("href", ""))
        if tag in ("link", "script") and a.get("href", a.get("src")):
            self.links.append(a.get("href", a.get("src")))

    def handle_endtag(self, tag):
        if tag == "article":
            self.depth -= 1
            if self.depth == 0:
                self.article = None
        if tag in ("h1", "h2", "h3"):
            self.headline = ""

    def handle_data(self, data):
        if self.headline == "h1":
            self.headers.append(data.strip())
        self.source += data + " "


def parse(text: str) -> Collect:
    p = Collect()
    p.feed(text)
    return p


def audit(parent: str, child: str) -> None:
    p, c = parse(parent), parse(child)
    if not any("Number Systems" in s for s in p.headers):
        raise ValueError("Missing parent subtopic identity")
    if not any("Index Laws" in s for s in c.headers):
        raise ValueError("Missing Index Laws page identity")
    if len(c.main) != 1 or c.main[0].get("data-g9-subtopic") != "NS-INDEX-LAWS":
        raise ValueError("Academic subtopic ID is not explicit")
    if c.main[0].get("data-g9-academic-status") != "PROVISIONAL":
        raise ValueError("Subtopic classification was silently accepted")
    if {r.get("data-g9-role"): r.get("data-g9-authority") for r in c.roles} != ROLES or len(c.roles) != 3:
        raise ValueError("Core role statuses are false or missing")
    if any(r.get("data-g9-launch-authorized") != "false" for r in c.roles):
        raise ValueError("Draft home cannot activate unapproved product actions")
    if c.role_links:
        raise ValueError("A held Core product must not contain a clickable action")
    if "index-laws/index.html" not in p.links or "../index.html" not in c.links:
        raise ValueError("Parent-child navigation broken")
    if "../../imo-grade9/index.html#topic-ns" not in c.links:
        raise ValueError("Source references must remain on existing research browser")
    if any("/products/" in s or "core1a.html" in s or "core2a.html" in s for s in c.links):
        raise ValueError("Unaccepted role was linked into learner product routes")
    if not all(t in c.source for t in ("not yet", "source custody and rights hold", "not an official SOF question")):
        raise ValueError("Held and separately authored statuses must be visible")
    if "SOURCE_CUSTODY_AND_RIGHTS_HOLD" not in child:
        raise ValueError("No source rights authority exists")
    for page in (parent, child):
        if any(t in page for t in ("SOF-IMO-G09-L1-", "<iframe", "source_pdf_url",
                                   "source_key", "original_question_stem")):
            raise ValueError("Publisher source content or original authority leaked")


class HomeRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.parent = (ROOT / "public" / PARENT).read_text(encoding="utf-8")
        cls.child = (ROOT / "public" / CHILD).read_text(encoding="utf-8")

    def test_real_routes_are_role_held(self):
        audit(self.parent, self.child)

    def test_research_source_and_separate_authored_roles(self):
        self.assertEqual([r["data-g9-role"] for r in parse(self.child).roles],
                         ["CORE1A", "CORE2A", "CORE2"])
        self.assertIn("Negative and fractional indices", self.parent)
        self.assertIn("Common-base substitution", self.child)
        self.assertIn("not an official SOF question", self.child)

    def test_public_pages_match_generated_docs_projection(self):
        for path in (PARENT, CHILD):
            with self.subTest(path=path):
                original = (ROOT / "public" / path).read_bytes()
                expected = build_pages_site._public_payload(path, original)
                mirror = (ROOT / "docs" / path).read_bytes()
                self.assertEqual(mirror, expected)
        desired = build_pages_site.desired_files(ROOT)
        # desired_files includes the generated manifest payload; re-rendering
        # its inventory here would incorrectly add the manifest as its own row.
        expected_manifest = desired[".pages-manifest.json"][1]
        actual = (ROOT / "docs/.pages-manifest.json").read_bytes()
        self.assertEqual(actual, expected_manifest)

    def test_links_resolve_in_both_source_and_pages_roots(self):
        for site in ("public", "docs"):
            for relative in (PARENT, CHILD):
                with self.subTest(site=site, path=relative):
                    page = (ROOT / site / relative).read_text(encoding="utf-8")
                    for link in parse(page).links:
                        target = urlsplit(link)
                        if target.scheme or target.netloc or not target.path:
                            continue
                        path = posixpath.normpath(
                            posixpath.join(posixpath.dirname(relative), target.path))
                        self.assertFalse(path.startswith("../"), (relative, link))
                        self.assertTrue((ROOT / site / path).is_file(), (site, relative, link, path))

    def test_false_core2_admission_rejected(self):
        self.assertIn('data-g9-authority="SOURCE_CUSTODY_AND_RIGHTS_HOLD"', self.child)
        mutated = self.child.replace("SOURCE_CUSTODY_AND_RIGHTS_HOLD", "SOURCE_CORE2_APPROVED")
        with self.assertRaises(ValueError):
            audit(self.parent, mutated)

    def test_source_cannot_be_published_as_authored_core2a(self):
        changed = self.child.replace('data-g9-authority="CANDIDATE_NOT_PUBLISHED"',
                                     'data-g9-authority="SOURCE_CUSTODY_AND_RIGHTS_HOLD"', 1)
        with self.assertRaises(ValueError):
            audit(self.parent, changed)

    def test_live_core1a_button_rejected(self):
        changed = self.child.replace('data-g9-launch-authorized="false"',
                                     'data-g9-launch-authorized="true"', 1)
        with self.assertRaises(ValueError):
            audit(self.parent, changed)

    def test_hidden_core1a_action_rejected(self):
        changed = self.child.replace("<h3>Core 1A · Learn the concept</h3>",
                                     '<h3>Core 1A · Learn the concept</h3><a href="core1a.html">Launch</a>')
        with self.assertRaises(ValueError):
            audit(self.parent, changed)

    def test_incorrect_subtopic_identity_rejected(self):
        changed = self.child.replace('data-g9-subtopic="NS-INDEX-LAWS"',
                                     'data-g9-subtopic="NS-FRACTIONAL-INDICES"')
        with self.assertRaises(ValueError):
            audit(self.parent, changed)


if __name__ == "__main__":
    unittest.main()
