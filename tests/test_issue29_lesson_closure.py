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
    def test_optional_probe_accepts_its_exact_authored_worked_anchor(self):
        from Shared.tools import learning_repair
        ctx=copy.deepcopy(self.ctx)
        m=ctx.selection_rows['microtopics'][0]
        unit=m['construction_units'][0]
        question=ctx.index('questions')[unit['worked_anchor_ref']]
        question['answer']['crux_move_ref']='AUTHORED-PROBE-CRUX'
        question['answer']['reasoning_route']=[{'id':'AUTHORED-PROBE-CRUX','kind':'DECIDE','action':'Hold the angle fixed while changing the independent contribution.','why_valid':'The declared toy has two independent inputs.','inputs':['Fixed angle'],'output':'Same factor can accompany different totals.'}]
        repair={field:'Declared toy-model review boundary.' for field in learning_repair.FIELDS}
        repair.update(question_ref=question['id'],label='Authored probe',construction_ref=unit['id'],
                      crux_move_ref=question['answer']['crux_move_ref'],interaction='MODEL_SCOPE_PROBE')
        question.setdefault('extensions',{})[learning_repair.KEY]=repair
        m.setdefault('extensions',{})['grade9v3:question_repairs']=[repair]
        html=render_core.core1a(ctx,m)
        self.assertIn('data-g9-alignment-probe',html)
        self.assertNotIn('Look along the fixed C-N axis.',html)
        self.assertNotIn('href="core2.html#'+question['id']+'"',html)
        self.assertNotIn('AUTHOR_LEARNING_REPAIR',[g['duty'] for g in ctx.gaps])
        foreign=copy.deepcopy(question);foreign['id']='FOREIGN-WORKED-PROBE'
        foreign['extensions'][learning_repair.KEY]['question_ref']=foreign['id']
        ctx.packages[0]['questions'].append(foreign)
        m['extensions']['grade9v3:question_repairs']=[foreign['extensions'][learning_repair.KEY]]
        ctx.gaps=[]
        render_core.core1a(ctx,m)
        self.assertTrue(any(g['duty']=='AUTHOR_LEARNING_REPAIR' for g in ctx.gaps))
    def test_pdf_publication_checks_the_modern_header_link(self):
        import tempfile
        with tempfile.TemporaryDirectory() as directory:
            folder=Path(directory)
            folder.joinpath('core1a.html').write_text('<a class="g9-header-btn" href="core1a.pdf" data-g9-action="pdf">PDF</a>', encoding='utf-8')
            problems=render_core.pdf_publication_problems(folder)
            self.assertTrue(any('links core1a.pdf, which is not there' in p for p in problems), problems)
    def test_difficulty_rationale_cannot_disclose_a_solution_before_attempt(self):
        from Shared.tools import owner_bank
        ctx=copy.deepcopy(self.ctx)
        q=ctx.selection_rows['core2'][0]
        sentinel='The correct final choice is SENTINEL-ANSWER.'
        q.setdefault('extensions',{}).setdefault(owner_bank.ANALYSIS_KEY,{})['difficulty']={
            'band':'D2','score':3,'basis':sentinel,'components':{'reasoning_chain_length':1}}
        source=render_core.core2(ctx,q)
        tree=OwnedHTML(source)
        self.assertNotIn(sentinel,render_core._difficulty_why(q['id'],q['extensions'][owner_bank.ANALYSIS_KEY]))
        marker=[r for r in tree.rows if r['attrs'].get('data-g9-block')=='difficulty_basis']
        self.assertTrue(marker)
        self.assertTrue(any(a['tag']=='template' for a in marker[0]['ancestors']))
        self.assertIn(sentinel,source)
    def test_repair_navigation_does_not_require_a_second_attempt(self):
        from Shared.tools import learning_repair
        repair={key:'A bounded changed-case check.' for key in learning_repair.FIELDS}
        for role in ('CORE1A','CORE2'):
            tree=OwnedHTML(learning_repair.card(repair,'Q-TEST',role))
            link=tree.with_attr('data-g9-repair-link')[0]
            self.assertFalse(tree.under(link,'data-g9-probe-feedback'))
            self.assertTrue(any(r['tag']=='div' and 'hidden' in r['attrs'] for r in tree.with_attr('data-g9-probe-feedback')))
    def test_answer_bearing_labels_are_question_bound_and_protected(self):
        from Shared.tools import learner_metadata
        ctx=copy.deepcopy(self.ctx); q=ctx.selection_rows['core2'][0]
        ext=q.setdefault('extensions',{})
        ext['grade9v3:attempt_labels']={'question_ref':q['id'],'concept':'Supplied situation','family':'Compare the givens'}
        projection=learner_metadata.project('CORE2',q,ctx.packages)
        actual=learner_metadata.resolve_concept(ctx.packages,q['primary_capability_ref'])['concept']
        self.assertNotIn(actual,learner_metadata.safe_search_text(projection,q,'CORE2'))
        html=render_core.core2(ctx,q); tree=OwnedHTML(html)
        node=next(r for r in tree.rows if r['attrs'].get('data-g9-block')=='detailed_concept_labels')
        self.assertTrue(any(a['tag']=='template' for a in node['ancestors']))
        ext['grade9v3:attempt_labels']['question_ref']='FOREIGN'
        with self.assertRaises(learner_metadata.LearnerMetadataError):learner_metadata.project('CORE2',q,ctx.packages)
    def test_authored_visual_review_rejects_foreign_question_and_source_resource(self):
        ctx=copy.deepcopy(self.ctx)
        q=ctx.selection_rows['core2'][0]
        rep=next(iter(ctx.index('representations')))
        q['figure_refs']=[rep]
        q.setdefault('extensions',{})['grade9v3:core2_visual_review']={
            'question_ref':'FOREIGN','replaces_authored_figure_refs':[rep],
            'authored_figure_refs':[rep],'rationale':'Corrected author support.'}
        render_core._core2_question_figures(ctx,q)
        self.assertTrue(any(g['duty']=='AUTHOR_CORE2_VISUAL_REVIEW' for g in ctx.gaps))
        ctx.gaps=[]
        q['extensions']['grade9v3:core2_visual_review']['question_ref']=q['id']
        target=ctx.index('representations')[rep]
        target.setdefault('extensions',{})['grade9v3:authored_question_ref']=q['id']
        render_core._core2_question_figures(ctx,q)
        self.assertFalse(any(g['duty']=='AUTHOR_CORE2_VISUAL_REVIEW' for g in ctx.gaps))
        target['extensions']['grade9v3:authored_question_ref']='FOREIGN'
        render_core._core2_question_figures(ctx,q)
        self.assertTrue(any(g['duty']=='AUTHOR_CORE2_VISUAL_REVIEW' for g in ctx.gaps))
        ctx.gaps=[]
        q['figure_refs']=['SOURCE-SNAPSHOT']
        q['extensions']['grade9v3:core2_visual_review']['replaces_authored_figure_refs']=['SOURCE-SNAPSHOT']
        render_core._core2_question_figures(ctx,q)
        self.assertTrue(any(g['duty']=='AUTHOR_CORE2_VISUAL_REVIEW' for g in ctx.gaps))
if __name__=='__main__':unittest.main()
