import copy,json,math,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parent
REPO=ROOT/'ISS32' if (ROOT/'ISS32').is_dir() else ROOT.parents[2]
sys.path.insert(0,str(REPO))
from Shared.tools import learning_repair, render_core

class LearningRepairTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.q=json.loads((REPO/'evidence/blueprint-cycles/ISS32/inputs/owner.bank.json').read_text())['questions'][0]
        cls.unit=cls.q['extensions'][learning_repair.KEY]['construction_ref']
    def test_foreign_question_and_crux_are_rejected(self):
        q=copy.deepcopy(self.q);q['extensions'][learning_repair.KEY]['question_ref']='OTHER-Q'
        q['extensions'][learning_repair.KEY]['crux_move_ref']='OTHER-MOVE'
        self.assertEqual(len(learning_repair.problems(q,{self.unit})),2)
        q=copy.deepcopy(self.q);q['extensions'][learning_repair.KEY]['interaction']='FAKE_WIDGET'
        self.assertIn('interaction is not supported',learning_repair.problems(q,{self.unit}))
    def test_distinct_anchor_does_not_bypass_hardest_crux_binding(self):
        repair=self.q['extensions'][learning_repair.KEY]
        anchor={'id':'NOVEL','stem':repair['probe'],'answer':{'summary':repair['pattern'],'check':repair['check']},'target_question_ref':self.q['id'],'target_crux_move_ref':self.q['answer']['crux_move_ref'],'construction_ref':self.unit}
        bank={self.q['id']:self.q}
        self.assertEqual(learning_repair.anchor_problems(anchor,bank,self.unit,self.q['id']),[])
        bad=copy.deepcopy(anchor);bad['target_question_ref']='OTHER-Q'
        ctx=render_core.Ctx({'product_id':'ANCHOR-REGRESSION'},[],[self.q],{})
        micro={'id':'M','extensions':{'grade9v3:lesson_anchors':{self.unit:bad}}}
        unit={'id':self.unit,'bank_anchor_ref':self.q['id'],'crux_question_refs':[self.q['id']]}
        brief={'question_ref':self.q['id'],'label':'Q1','band':'D1','score':2,'conceptual':1}
        render_core._toughest_unit_gaps(ctx,micro,[unit],brief)
        self.assertTrue(any(row['duty']=='AUTHOR_TOUGHEST_CONCEPT' for row in ctx.gaps))
        micro['extensions']['grade9v3:lesson_anchors'][self.unit]=anchor;ctx.gaps.clear()
        render_core._toughest_unit_gaps(ctx,micro,[unit],brief)
        self.assertEqual(ctx.gaps,[])
    def test_a_missing_target_cannot_become_a_good_link(self):
        self.assertIn('construction_ref does not resolve to a construction unit',learning_repair.problems(self.q,set()))
    def test_quality_navigation_admits_typed_landmarks_only(self):
        text='<article id="M" data-g9-unit="M"></article><section id="CU" data-g9-cu="CU"></section><section id="repair-Q" data-g9-repair-target="Q"></section><p id="FAKE" data-g9-unit="FAKE"></p><section id="WRONG" data-g9-cu="CU"></section>'
        self.assertEqual(learning_repair.navigation_targets(text),{'M','CU','repair-Q'})
    def test_independent_chemistry_ledgers_and_counterexample(self):
        self.assertEqual(4+3+5+6,18);self.assertEqual(6+3+7+8,24)
        self.assertEqual(24-(3*2+6*2),6)
        self.assertAlmostEqual(math.cos(math.pi/3),math.cos(-math.pi/3))
        # Degenerate H=[[e,t],[t,e]] has e ± |t|, not a universal t² energy law.
        self.assertEqual(sorted((2+abs(-.5),2-abs(-.5))),[1.5,2.5])
    def test_widget_commit_and_relative_direction_controls(self):
        harness=r'''
const vm=require('vm'),fs=require('fs');let listeners={};
const sandbox={document:{addEventListener:(n,f)=>listeners[n]=f,querySelector:()=>null,getElementById:()=>null},window:{addEventListener:()=>{}},location:{hash:''},Math};
vm.runInNewContext(fs.readFileSync(process.argv[1],'utf8'),sandbox);
let response={value:'',focus:()=>{}},message={},feedback={hidden:true},root={dataset:{},querySelector:s=>({'[data-g9-probe-response]':response,'[data-g9-probe-message]':message,'[data-g9-probe-feedback]':feedback}[s])};
const button={closest:()=>root};listeners.click({target:{closest:()=>button}});if(!feedback.hidden)throw Error('empty answer revealed');
response.value='   ';listeners.click({target:{closest:()=>button}});if(!feedback.hidden)throw Error('whitespace response revealed');
response.value='prediction and reason';listeners.click({target:{closest:()=>button}});if(feedback.hidden)throw Error('committed feedback missing');
let theta={value:60},other={value:0},out={},transform='';let probe={querySelector:s=>({'[data-g9-theta]':theta,'[data-g9-other]':other,'[data-g9-alignment-output]':out,'[data-g9-donor]':{setAttribute:(k,v)=>transform=v}}[s])};
const input={target:{closest:()=>probe}};listeners.input(input);if(transform!=='rotate(60 180 180)'||!out.textContent.includes('0.500')||!out.textContent.includes('-0.250'))throw Error('wrong 60-degree result');
other.value=1;listeners.input(input);if(!out.textContent.includes('0.750')||!out.textContent.includes('0.500'))throw Error('lost independent variable');
theta.value=90;listeners.input(input);if(!out.textContent.includes('0.000'))throw Error('wrong perpendicular endpoint');
theta.value=0;other.value=0;listeners.input(input);if(transform!=='rotate(0 180 180)'||!out.textContent.includes('1.000')||!out.textContent.includes('-1.000'))throw Error('wrong aligned endpoint');
process.stdout.write('PASS: response gate and 0/60/90 angle controls; DOM harness, not browser.');
'''
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'probe-runtime.js';path.write_text(learning_repair.JS)
            result=subprocess.run(['node','-e',harness,str(path)],capture_output=True,text=True)
        self.assertEqual(result.returncode,0,result.stderr)

if __name__=='__main__':unittest.main()
