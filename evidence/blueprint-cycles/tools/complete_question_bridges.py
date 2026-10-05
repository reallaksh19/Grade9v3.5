"""Give every corrected question one exact construction, retaining existing unit IDs.

This is authored lesson expansion, not relabeling or changing the owner-question
denominator. Each original question keeps its text, source figures and custody.
"""
import argparse,copy,json
from pathlib import Path
from close_d1 import write
ROOT=Path(__file__).resolve().parents[3]
def complete(issue):
    directory=ROOT/f'evidence/blueprint-cycles/ISS{issue}/inputs'
    b=json.loads((directory/'owner.bank.json').read_text());p=json.loads((directory/'package.v1.json').read_text())
    for m in p['microtopics']:
        relevant=[q for q in b['questions'] if q['extensions']['grade9v3:learning_repair']['microtopic_ref']==m['id']]
        old=m['construction_units'];by_q={u['bank_anchor_ref']:u for u in old}
        original_misconception=copy.deepcopy((m.get('misconceptions') or [{}])[0])
        anchors={};units=[];steps=[]
        for q in relevant:
            r=q['extensions']['grade9v3:learning_repair']
            u=copy.deepcopy(by_q.get(q['id'],old[0]))
            if q['id'] not in by_q:u['id']=old[0]['id']+'-'+q['original_identifier']
            u['bank_anchor_ref']=q['id'];u['crux_question_refs']=[q['id']]
            u['decision']=r['clarify']
            refs=[]
            for n,row in enumerate(q['answer']['reasoning_route'],1):
                sid=u['id']+f'-TEACH-{n}';refs.append(sid)
                # Keep canonical teaching-path structure; only authored operations change.
                s=copy.deepcopy(m['teaching_path'][0]);s.update(id=sid,action=row['action'],why_valid=row['why_valid'],output=row['output'])
                if 'inputs' in s:s['inputs']=row['inputs']
                steps.append(s)
            u['step_refs']=refs;u['crux_step_ref']=refs[1]
            rep_id=next(iter(q.get('figure_refs',[])),u.get('representation_ref'))
            if rep_id:
                u['representation_ref']=rep_id
                rep=next(rep for rep in p['representations'] if rep['id']==rep_id)
                u['reveal_stage_refs']=[stage['id'] for stage in rep.get('reveal_stages',[])]
            u['independent_checks']=[{'role':'CHECK','statement':r['check']},{'role':'APPLY','statement':r['transfer']},{'role':'CONNECT','statement':r['connect']}]
            r['construction_ref']=u['id']
            result=r['pattern'].split(' Repeated')[0].split(' A repeated')[0].split(' Persistent')[0].split(' A recurring')[0].split(' Recurrent')[0]
            anchors[u['id']]={'id':'ANCHOR-'+u['id'],'stem':r['probe'],
                'answer':{'summary':result,'reasoning':[r['connect'],result,r['rule']],'check':r['check']},
                'target_question_ref':q['id'],'target_crux_move_ref':q['answer']['crux_move_ref'],'construction_ref':u['id']}
            units.append(u)
        # Every pre-existing named construction anchor is retained, even when the question order differs.
        lost={u['id'] for u in old}-{u['id'] for u in units}
        for original in old:
            if original['id'] not in lost:continue
            u=copy.deepcopy(original);q=next(q for q in b['questions'] if q['id']==u['bank_anchor_ref'])
            u.pop('crux_question_refs',None);u['step_refs']=[]
            for n,row in enumerate(q['answer']['reasoning_route'],1):
                sid=u['id']+f'-TEACH-{n}';u['step_refs'].append(sid)
                s=copy.deepcopy(m['teaching_path'][0]);s.update(id=sid,action=row['action'],why_valid=row['why_valid'],output=row['output']);steps.append(s)
            u['crux_step_ref']=u['step_refs'][1]
            r=q['extensions']['grade9v3:learning_repair']
            anchors[u['id']]={'id':'ANCHOR-'+u['id'],'stem':r['probe'],
                'answer':{'summary':r['pattern'],'reasoning':[r['connect'],r['rule']],'check':r['check']},
                'target_question_ref':q['id'],'target_crux_move_ref':q['answer']['crux_move_ref'],'construction_ref':u['id']}
            units.append(u)
        misconceptions=[]
        for u in units:
            q=next(q for q in b['questions'] if q['id']==u['bank_anchor_ref']);r=q['extensions']['grade9v3:learning_repair']
            row=copy.deepcopy(original_misconception)
            row.update(wrong_idea=r['wrong_idea'],diagnostic_prompt=r['probe'],repair=r['rule']+' '+r['check'])
            if 'why_wrong' in row:row['why_wrong']=r['check']
            if 'id' in row:row['id']='MIS-'+u['id']
            u['misconception_indexes']=[len(misconceptions)];misconceptions.append(row)
        m['misconceptions']=misconceptions
        m['construction_units']=units;m['teaching_path']=steps
        m['extensions']['grade9v3:lesson_anchors']=anchors
        m['extensions']['grade9v3:question_repairs']=[q['extensions']['grade9v3:learning_repair'] for q in relevant]
    write(directory/'owner.bank.json',b);write(directory/'package.v1.json',p)
    print(f'ISS{issue}: {sum(len(m["construction_units"]) for m in p["microtopics"])} exact question constructions; original named anchors retained.')
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('issue',type=int,choices=range(31,39));complete(a.parse_args().issue)
