"""A page that did not come through the renderer meets the shell's policies, read from its own bytes."""
from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from Shared.tools import blueprint_spec, standalone_conformance as sc, web_blueprint_contract as contract

CLEAN = """<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>t</title><style>body{font-size:17px}.note{font-size:0.9rem}</style></head><body><h1 id="top">A page</h1>
<p>A relation <math><mi>F</mi></math> and a <a href="https://example.org/source">source</a>.</p><a href="#top">top</a></body></html>"""


def page(body: str = "", head: str = "", viewport: str = "width=device-width,initial-scale=1") -> str:
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="{viewport}"><title>t</title>{head}</head>'
            f"<body>{body}</body></html>")


class Rules(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)
        (self.dir / "vendor").mkdir()
        for name in ("katex.min.js", "vendor/tailwind.js"):
            (self.dir / name).write_text("/* vendored */", encoding="utf-8")

    def check(self, html: str, name: str = "p.html") -> dict[str, int]:
        path = self.dir / name
        path.write_text(html, encoding="utf-8")
        return sc.counts(sc.check_page(path, root=self.dir))

    def test_a_clean_page_conforms(self):
        self.assertEqual(self.check(CLEAN), {})

    def test_a_remote_script_is_refused_and_a_link_to_a_source_is_not(self):
        """The finding of pull request 375: a Tailwind script from another host, in a shell that forbids one."""
        self.assertEqual(self.check(page(head='<script src="https://www.gstatic.com/antigravity/web/dev/tailwindcss.min.js"></script>')),
                         {"REMOTE_RUNTIME": 1})
        for head in ('<link rel="stylesheet" href="//fonts.example/x.css">', "<style>@import url('https://x.example/a.css');</style>",
                     "<style>a{background:url(https://x.example/i.png)}</style>", "<script>import('https://cdn.example/m.js')</script>"):
            self.assertEqual(self.check(page(head=head)), {"REMOTE_RUNTIME": 1}, head)
        self.assertEqual(self.check(page(body='<a href="https://example.org/paper.pdf">source</a>')), {})

    def test_zoom_is_never_turned_off(self):
        self.assertEqual(self.check(page(viewport="width=device-width,user-scalable=no")), {"VIEWPORT_ZOOM": 1})
        self.assertEqual(self.check(page(viewport="width=device-width,maximum-scale=1")), {"VIEWPORT_ZOOM": 1})
        self.assertEqual(self.check(page(viewport="width=device-width,maximum-scale=5.0")), {})
        self.assertEqual(self.check("<!doctype html><html><body>x</body></html>"), {"VIEWPORT_ZOOM": 1})

    def test_text_under_the_floor_is_refused_from_the_registry_not_from_a_number_in_the_tool(self):
        floor = contract.load_registry()["shell"]["typography_policy"]["minimum_learner_text_css_px"]
        self.assertEqual(floor, 14)
        self.assertEqual(self.check(page(head="<style>.a{font-size:13px}.b{font-size:0.8rem}</style>")), {"FONT_FLOOR": 2})
        self.assertEqual(self.check(page(body='<span style="font-size:12px">x</span><i class="text-xs">y</i><i class="text-[11px]">z</i>')), {"FONT_FLOOR": 3})
        self.assertEqual(self.check(page(head="<style>.a{font-size:14px}.b{font-size:0}</style>")), {})

    def test_a_rem_is_the_size_the_page_itself_declares_for_its_root(self):
        """The renderer writes html{font-size:calc(var(--g9-type-body) * var(--g9-zoom))} with 17px and 1: 0.85rem is 14.45 px there, not 13.6."""
        renderer = "<style>:root{--g9-type-body:17px;--g9-zoom:1}html{font-size:calc(var(--g9-type-body) * var(--g9-zoom))}.a{font-size:.85rem}</style>"
        self.assertEqual(self.check(page(head=renderer)), {})
        self.assertEqual(self.check(page(head=renderer.replace(".85rem", ".8rem"))), {"FONT_FLOOR": 1}, "0.8rem is 13.6 px on a 17 px root")
        self.assertEqual(self.check(page(head="<style>html{font-size:18px}.a{font-size:.8rem}</style>")), {})
        self.assertEqual(self.check(page(head="<style>.a{font-size:.85rem}</style>")), {"FONT_FLOOR": 1}, "no root declared: 16 px, as a browser has it")

    def test_a_root_the_checker_does_not_follow_is_not_guessed(self):
        for root in ("html{font-size:calc(100% + 4px)}", "html{font-size:calc(var(--missing) * 1)}", "html{font-size:200px}",
                     "@media (min-width:900px){html{font-size:20px}}", ".x html{font-size:20px}"):
            self.assertEqual(self.check(page(head=f"<style>{root}.a{{font-size:.85rem}}</style>")), {"FONT_FLOOR": 1}, root)
        self.assertEqual(self.check(page(head="<style>html{font-size:2px}</style>")), {"FONT_FLOOR": 1}, "a root that is itself under the floor is refused")

    def test_a_staged_page_is_judged_where_it_will_be_served(self):
        staged, site = self.dir / "publication", self.dir / "public"
        (staged / "products").mkdir(parents=True)
        (site / "css").mkdir(parents=True)
        (site / "css" / "tablet.css").write_text("/* the site's stylesheet */", encoding="utf-8")
        path = staged / "products" / "p.html"
        path.write_text(page(head='<link rel="stylesheet" href="../css/tablet.css">', body='<a href="gone.html">x</a>'), encoding="utf-8")
        self.assertEqual(sc.counts(sc.check_page(path)), {"LINKS_RESOLVE": 2})
        found = sc.check_page(path, published=(staged, site))
        self.assertEqual(sc.counts(found), {"LINKS_RESOLVE": 1})
        self.assertIn("gone.html", found[0]["detail"], "what is missing from the site is still missing")

    def test_every_relative_reference_lands_on_a_file_and_every_fragment_on_an_id(self):
        (self.dir / "other.html").write_text(page(body='<h2 id="here">h</h2>'), encoding="utf-8")
        self.assertEqual(self.check(page(body='<a href="other.html#here">a</a><a href="#">b</a><a href="mailto:a@b.c">c</a>')), {})
        found = self.check(page(body='<a href="../index.html">a</a><a href="other.html#nope">b</a><a href="#nope">c</a><script src="gone.js"></script>'))
        self.assertEqual(found, {"LINKS_RESOLVE": 4})

    def test_a_reference_that_leaves_the_root_is_said_not_held(self):
        sub = self.dir / "root"
        sub.mkdir()
        (self.dir / "outside.js").write_text("1", encoding="utf-8")
        path = sub / "p.html"
        path.write_text(page(body='<script src="../outside.js"></script>'), encoding="utf-8")
        findings = sc.check_page(path, root=sub)
        self.assertEqual([(f["rule"], f["severity"]) for f in findings], [("LINKS_LEAVE_ROOT", "ADVISE")])
        self.assertEqual(sc.counts(findings), {})

    def test_maths_that_was_read_as_a_control_character_is_found(self):
        """\\vec read as \\v + 'ec' is a vertical tab in the source: the maths is gone for good."""
        self.assertEqual(self.check(page(body="<p>$\x0bec{F}$ and $\x0crac{a}{b}$</p>")), {"MATH_CONTROL_CHARS": 2})

    def test_raw_tex_needs_something_on_the_page_that_renders_it(self):
        raw = "<p>speed \\(v = u + at\\) and $\\theta$</p>"
        self.assertEqual(self.check(page(body=raw)), {"MATH_UNRENDERED": 1})
        self.assertEqual(self.check(page(body=raw, head='<script src="katex.min.js"></script>')), {"MATH_UNRENDERED": 1},
                         "loading a renderer is not rendering")
        self.assertEqual(self.check(page(body=raw + "<script>const k = window.katex; /* katex is loaded */</script>")), {"MATH_UNRENDERED": 1},
                         "a script that mentions the renderer and never calls it (U3-3 of the validation: KaTeX loaded, auto-render never run)")
        self.assertEqual(self.check(page(body=raw + "<script>renderMathInElement(document.body)</script>")), {})
        self.assertEqual(self.check(page(body=raw + "<script>katex.render('x', el)</script>")), {})
        self.assertEqual(self.check(page(body="<p>it costs $5 and $6</p>")), {})

    def test_storage_is_read_inside_a_try_block_only(self):
        self.assertEqual(self.check(page(body="<script>const s = localStorage.getItem('k');</script>")), {"STORAGE_GUARDED": 1})
        self.assertEqual(self.check(page(body="<script>function g(){ try { return localStorage.getItem('k'); } catch (e) { return null; } }</script>")), {})
        self.assertEqual(self.check(page(body="<script>try { x(); } catch (e) { localStorage.clear(); }</script>")), {"STORAGE_GUARDED": 1},
                         "the catch block is not the guard")
        self.assertEqual(self.check(page(body="<script>// localStorage is used later\nconst a = 'localStorage';</script>")), {},
                         "a name in a comment or a string is not a use")

    def test_configuration_for_a_vendor_script_the_page_does_not_load(self):
        orphan = "<script>tailwind.config = { theme: {} };</script>"
        self.assertEqual(self.check(page(body=orphan)), {"VENDOR_CONFIG_DANGLING": 1})
        self.assertEqual(self.check(page(body=orphan, head='<script src="vendor/tailwind.js"></script>')), {})

    def test_an_id_appears_once(self):
        self.assertEqual(self.check(page(body='<i id="a"></i><b id="a"></b><u id="b"></u>')), {"UNIQUE_IDS": 1})


class Ledger(unittest.TestCase):
    def test_a_page_may_not_be_worse_than_the_ledger_and_a_new_page_has_no_findings(self):
        ledger = {"files": {"standalone/a.html": {"FONT_FLOOR": 3}}}
        self.assertEqual(sc.ratchet({"standalone/a.html": {"FONT_FLOOR": 3}}, ledger), [])
        self.assertEqual(sc.ratchet({"standalone/a.html": {"FONT_FLOOR": 2}}, ledger), [])
        self.assertEqual(len(sc.ratchet({"standalone/a.html": {"FONT_FLOOR": 4}}, ledger)), 1)
        self.assertEqual(len(sc.ratchet({"standalone/a.html": {"REMOTE_RUNTIME": 1}}, ledger)), 1)
        self.assertEqual(len(sc.ratchet({"standalone/new.html": {"FONT_FLOOR": 1}}, ledger)), 1)

    def test_every_governed_page_in_the_repository_is_no_worse_than_the_ledger(self):
        """The gate. A pull request that adds a page with a remote script, or makes a listed page worse, fails here."""
        shell = sc.policy()
        found: dict[str, dict[str, int]] = {}
        ids: dict = {}
        for path in sc.governed_files(shell):
            root = REPO_ROOT / "standalone"
            counts = sc.counts(sc.check_page(path, root=root, shell=shell, _ids=ids))
            if counts:
                found[str(path.relative_to(REPO_ROOT))] = counts
        self.assertEqual(sc.ratchet(found, sc.load_ledger()), [])

    def test_the_ledger_names_only_pages_that_exist(self):
        for name in sc.load_ledger()["files"]:
            self.assertTrue((REPO_ROOT / name).exists(), f"{name} is in the ledger and not in the repository: tighten it")


class Registry(unittest.TestCase):
    def test_the_policy_and_the_checker_name_the_same_rules(self):
        policy = contract.load_registry()["shell"]["standalone_policy"]
        self.assertEqual([r["id"] for r in policy["rules"]], list(sc.RULES))
        self.assertEqual(sc.LEDGER, REPO_ROOT / policy["ledger"])
        self.assertTrue((REPO_ROOT / policy["checker"]).exists())
        self.assertTrue((REPO_ROOT / policy["browser_audit"]["tool"]).exists())

    def test_every_rule_executes_a_policy_the_shell_actually_has(self):
        shell = contract.load_registry()["shell"]
        for rule in shell["standalone_policy"]["rules"]:
            self.assertIn(rule["executes"].split(".")[0], shell, rule["id"])

    def test_the_schema_accepts_the_registry_and_refuses_one_without_the_policy(self):
        import jsonschema
        schema = json.loads((REPO_ROOT / "Shared/web/interactive-page-blueprint.schema.json").read_text(encoding="utf-8"))
        validator = jsonschema.Draft202012Validator(schema)
        registry = json.loads(json.dumps(contract.load_registry()))
        self.assertEqual([e.message for e in validator.iter_errors(registry)], [])
        for where, key in (("shell", "standalone_policy"), ("component_policy", "admission"), ("component_policy", "evidence")):
            broken = json.loads(json.dumps(registry))
            parent = broken["shell"] if where == "shell" else broken["component_policy"]
            del parent[key]
            self.assertTrue(list(validator.iter_errors(broken)), f"a registry without {key} is accepted")

    def test_the_generated_spec_states_the_policy(self):
        spec = blueprint_spec.render()
        self.assertIn("Pages that do not come through the renderer", spec)
        for rule in sc.RULES:
            self.assertIn(f"`{rule}`", spec)


class LineEndings(unittest.TestCase):
    def test_text_is_lf_in_every_working_tree(self):
        attributes = (REPO_ROOT / contract.load_registry()["component_policy"]["evidence"]["attributes_file"]).read_text(encoding="utf-8")
        self.assertIn("* text=auto eol=lf", attributes)


REPO_ROOT = Path(__file__).resolve().parents[1]

if __name__ == "__main__":
    unittest.main()
