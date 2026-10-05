"""Behavioral regressions for integrated teaching and portable product navigation."""
import copy
import unittest
from pathlib import Path
from html.parser import HTMLParser
from Shared.tools import render_core

ROOT=Path(__file__).resolve().parents[1]
class OwnedHTML(HTMLParser):
    def __init__(self,source):
        super().__init__();self.rows=[];self.stack=[];self.feed(source)
    def handle_starttag(self,tag,attrs):
        row={'tag':tag,'attrs':dict(attrs),'ancestors':list(self.stack)};self.rows.append(row)
        if tag not in {'area','base','br','col','embed','hr','img','input','link','meta','param','source','track','wbr'}:self.stack.append(row)
    def handle_endtag(self,tag):
        for n in range(len(self.stack)-1,-1,-1):
            if self.stack[n]['tag']==tag:self.stack=self.stack[:n];break
    def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
    def with_attr(self,attr):return [r for r in self.rows if attr in r['attrs']]
    @staticmethod
    def under(row,attr):return any(attr in a['attrs'] for a in row['ancestors'])
class LessonClosure(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ctx=render_core.context(ROOT/'products/physics/phy-kin-2d-motion.manifest.json')
    def test_current_conditions_and_visual_precede_the_summary(self):
        tree=OwnedHTML(render_core.page(self.ctx,'CORE1A','PAGES','test'))
        unit=tree.with_attr('data-g9-cu')[0]
        markers=[r['attrs']['data-g9-component'] for r in tree.with_attr('data-g9-component') if unit in r['ancestors']]
        self.assertLess(markers.index('MODEL_CONTRACT'),markers.index('CONSTRUCTION_STEPS'))
        self.assertLess(markers.index('CONSTRUCTION_STEPS'),markers.index('STAGED_VISUAL'))
        self.assertLess(markers.index('STAGED_VISUAL'),markers.index('KEY_STEP'))
        conditions=[r for r in tree.rows if r['attrs'].get('data-g9-block')=='entry_assumptions']
        self.assertTrue(conditions)
        self.assertFalse(any(a['tag']=='details' for r in conditions for a in r['ancestors']))
    def test_worked_explanation_is_visible_but_fresh_exit_answer_is_inert(self):
        tree=OwnedHTML(render_core.page(self.ctx,'CORE1A','PAGES','test'))
        worked=tree.with_attr('data-g9-watch-step');self.assertTrue(worked)
        self.assertFalse(any(a['tag']=='details' for r in worked for a in r['ancestors']))
        exit_nodes=[r for r in tree.with_attr('data-g9-component') if r['attrs']['data-g9-component']=='EXIT_RECALL']
        close=[r for r in tree.rows if any(a in r['ancestors'] for a in exit_nodes)]
        self.assertFalse(any(r['tag']=='details' and 'open' in r['attrs'] for r in close))
        self.assertTrue(any(r['tag']=='template' for r in close))
    def test_single_file_has_no_external_shell_dependencies(self):
        pages,_,_=render_core.build(ROOT/'products/physics/phy-kin-2d-motion.manifest.json','SINGLE_FILE')
        tree=OwnedHTML(pages['product.html'])
        self.assertFalse(any((r['tag']=='script' and 'src' in r['attrs']) or (r['tag']=='link' and r['attrs'].get('rel')=='stylesheet') for r in tree.rows))
        self.assertTrue(tree.with_attr('data-g9-modern-shell'));self.assertTrue(tree.with_attr('data-g9-tablet-shell'))
        ids={r['attrs']['id'] for r in tree.with_attr('id')}
        for link in [r['attrs']['href'] for r in tree.with_attr('href') if r['tag']=='a' and r['attrs']['href'].startswith('#')]:
            self.assertIn(link[1:],ids)
    def test_standalone_shell_uses_only_selected_existing_role_routes(self):
        ctx=copy.copy(self.ctx);ctx.manifest=copy.deepcopy(ctx.manifest)
        ctx.manifest.update(home_href='index.html',question_bank_href='index.html',output_roles=['CORE1A','CORE2'])
        tree=OwnedHTML(render_core.page(ctx,'CORE1A','PAGES','test'))
        links=[r['attrs']['href'] for r in tree.with_attr('href') if r['tag']=='a' and any(a['tag']=='header' for a in r['ancestors'])]
        self.assertEqual(links,['index.html','index.html','core1a.pdf'])
        self.assertFalse(any('topics/nlm' in r['attrs']['href'] for r in tree.with_attr('href')))
        roles=[r['attrs']['href'] for r in tree.with_attr('href') if any('g9-triad-actions' in a['attrs'].get('class','') for a in r['ancestors'])]
        self.assertEqual(roles,['core1a.html','core2.html'])
    def test_pdf_publication_checks_the_modern_header_link(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            folder.joinpath('core1a.html').write_text('<a class="g9-header-btn" href="core1a.pdf" data-g9-action="pdf">PDF</a>', encoding='utf-8')
            problems=render_core.pdf_publication_problems(folder)
            self.assertTrue(any('links core1a.pdf, which is not there' in p for p in problems), problems)
if __name__=='__main__':unittest.main()

