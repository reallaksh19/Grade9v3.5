"""Rebuild real subject specimens; preserve the canonical Mathematics library.

Invalid historical publication enums are quarantined only in a derived review
copy. Source verification is NOT_RUN, never granted by a successful render.
"""
import copy, hashlib, json, shutil
import os
from pathlib import Path
from Shared.tools import product_manifest, render_core

ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / os.environ.get('G9_REVIEW_DIR','evidence/blueprint-cycles/closure-20261005') / 'subjects'
KEYS = ['concept_model_selection','representation_translation','reasoning_chain_length','algebra_computational_load','trap_exception_sensitivity']

def save(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False)+'\n', encoding='utf-8', newline='\n')

def build_math():
    source=ROOT/'Mathematics/library/linear-equations.v1.json'
    p=json.loads(source.read_text(encoding='utf-8')); original=copy.deepcopy(p)
    quarantined=[]
    for q in p['questions']:
        if q['status']=='PUBLISHED':
            previous={'id':q['id'],'status':q['status'],'verification_status':q['answer']['verification_status']}
            quarantined.append(previous)
            q['extensions']['grade9v3:legacy_claim_quarantine']=previous
            q['status']='CANDIDATE'; q['answer']['verification_status']='NOT_RUN'
    questions=[q for q in p['questions'] if q['origin']=='ORIGINAL'][:10]
    # Explicit estimates for the actual ten tasks, not their legacy score labels.
    estimates=[
      ([0,1,1,1,1], 'Equality must first become an equation; test four candidates, keeping both sides distinct.'),
      ([1,0,1,1,1], 'Generate a candidate from opposite side changes, then check both sides.'),
      ([0,1,1,1,0], 'Translate the missing slot into an unknown and substitute the given negative solution.'),
      ([0,0,1,0,0], 'One same-operation cancellation leaves the stated integer.'),
      ([0,0,1,1,1], 'Collect variable terms and constants; preserve negative signs through the exact check.'),
      ([0,0,1,1,1], 'Collect the two variable occurrences, undo the constant and verify the signed solution in the original equation.'),
      ([0,0,1,1,1], 'Variable occurrences are on opposite sides, including a negative coefficient.'),
      ([0,0,0,0,1], 'Classify the preserved solution under the explicitly nonzero multiplier condition.'),
      ([0,0,1,1,1], 'Distribute on both sides, collect terms and check the negative result.'),
      ([0,1,2,2,1], 'Translate three bracketed groups into signed terms, coordinate collection and exact division, then check both original sides.')]
    for q,(vector,basis) in zip(questions,estimates):
        score=sum(vector);band='D1' if score<=2 else 'D2' if score<=5 else 'D3' if score<=7 else 'D4'
        ext=q['extensions'];ext['grade9v3:provenance_class']='SOURCE_UNVERIFIED'
        ext['grade9v3:source_custody']['continuation_verification']='NOT_RUN'
        ext['grade9v3:analysis']={'learner_question_type':'single_correct_mcq' if q['options'] else 'constructed_response',
          'difficulty':{'band':band,'score':score,'components':dict(zip(KEYS,vector)),'basis':basis},
          'exam_source_badge':'Legacy textbook/exemplar wording; verification pending',
          'cognitive_demand':{'primary':'RETRIEVE' if 'EXEMPLAR9-4-1-Q16' in q['id'] else 'APPLY','secondary':['JUSTIFY']},
          'stable_crux_move':q['answer']['reasoning_route'][0]['action']}
        ext['grade9v3:classification_status']='AUTHOR_ESTIMATE_REQUIRES_REVIEW'
        ext['grade9v3:unavailable_authored_visuals']={'original_representation_roles':copy.deepcopy(q.get('representation_roles',{})),'reason':'Legacy authored SVG assets are absent. The source supplies no figure; text/scaffolds remain complete. No decorative substitute or source-figure claim.'}
        q['representation_roles']={}
        for rung in q.get('hint_ladder',[]):rung.pop('visual_stage_ref',None)
        for scaffold in q.get('scaffolds',[]):scaffold.pop('visual_stage_ref',None)
    selected={q['id'] for q in questions};p['questions']=[q for q in p['questions'] if q['id'] not in selected]
    directory=OUT/'mathematics'
    transfer=next(q for q in p['questions'] if q['id']=='Q-MATH-LINEAR-2B-01')
    transfer['transfer']['novelty']['checked_against'].extend(q['id'] for q in questions)
    transfer['transfer']['novelty']['why_new']='Relative to the named plain-equation worked anchor Q-MATH-LINEAR-01, the outer multiplication changes the natural undo order. Earlier selected source questions already contain brackets; this is familiar practice compatibility, not proven whole-product novel transfer or independent learning.'
    rep=copy.deepcopy(next(r for r in p['representations'] if r['id']=='REP-MATH-NUMBER-LINE'))
    rep.update(id='REP-ISS29-MATH-TRANSFER-EXACT',scene_instances=[],rendered_asset_refs=[])
    rep['reveal_stages']=[{'id':'VIS-ISS29-MATH-TRANSFER-DOMAIN','label':'Declared domain','purpose':'Rational number line only; no target point before the attempt.','visible_elements':['Declared domain']},{'id':'VIS-ISS29-MATH-TRANSFER-RESULT','label':'Exact point','purpose':'Show the protected exact 8/3 solution of this transfer equation, distinct from 7/3 in the earlier worked anchor.','visible_elements':['Declared domain','Marked solution with its exact label','Bracketing integer ticks','Whether each marked endpoint is included']}]
    asset=directory/'assets/exact-transfer.svg';asset.parent.mkdir(parents=True,exist_ok=True)
    asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 720 240" role="img" aria-label="Question-specific rational number line" font-size="22"><title>Question-specific rational number line</title><desc>A rational axis; exact 8/3 point stays in the protected result stage.</desc><g data-g9-stage-id="VIS-ISS29-MATH-TRANSFER-DOMAIN"><path d="M70 135H650" stroke="#334155" stroke-width="3"/><text x="70" y="55">Declared domain: rational numbers</text><text x="170" y="180">2</text><text x="570" y="180">3</text></g><g data-g9-stage-id="VIS-ISS29-MATH-TRANSFER-RESULT"><circle cx="436.67" cy="135" r="8" fill="#2563eb"/><text x="385" y="105">x = 8/3</text><text x="70" y="220">Check: 3(8/3 − 1) = 5. A truncation 2.66 gives 4.98.</text></g></svg>',encoding='utf-8',newline='\n')
    rep['rendered_asset_refs']=[asset.relative_to(ROOT).as_posix()]
    rep['correspondence']=[{'element':'Marked solution with its exact label','symbol':'8/3','in_words':'The exact rational satisfying 3(x−1)=5; not the earlier anchor value.'}]
    p['representations'].append(rep)
    transfer['representation_roles']={'initial_ref':None,'safe_ref':rep['id'],'bound_ref':rep['id'],'stage_refs':['VIS-ISS29-MATH-TRANSFER-DOMAIN']}
    p['extensions']['grade9v3:review_derivation']={'source_path':source.relative_to(ROOT).as_posix(),
       'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'canonical_unchanged':True,
       'quarantined_claims':quarantined,'independent_verification':'NOT_RUN'}
    save(directory/'package.v1.json',p)
    save(directory/'bank.v1.json',{'schema_version':'review-bank/v1','questions':questions})
    rel=lambda path:path.relative_to(ROOT).as_posix()
    m=product_manifest.derive(rel(directory/'package.v1.json'),[rel(directory/'bank.v1.json')],'PRODUCT-ISS29-MATH-REVIEW','index.html')
    m['selection']['microtopics']=[row['id'] for row in p['microtopics'][:3]]
    m['selection']['core2a']=['Q-MATH-LINEAR-01'];m['selection']['core2b']=['Q-MATH-LINEAR-2B-01']
    held=product_manifest.derivable([p],questions)
    m['coverage']={'omitted':{qid:'Outside the selected familiar-application/transfer compatibility pair; retained in the derived library.' for role in ('core2a','core2b') for qid in held[role] if qid not in m['selection'][role]}}
    m['output_roles']=list(render_core.RENDER)
    save(directory/'manifest.json',m)
    baseline={q['id']:q for q in original['questions']}
    for q in questions:
        for field in ('stem','original_identifier','options','conditions'):
            assert q[field]==baseline[q['id']][field],(q['id'],field)
        assert q['answer']['summary']==baseline[q['id']]['answer']['summary']
    save(directory/'derivation.json',{'source_path':rel(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'ten_question_ids':list(selected),'source_identity_and_answer_unchanged':True,'quarantined_claims':quarantined,
        'classification':'AUTHOR_ESTIMATE_REQUIRES_REVIEW','source_verification':'NOT_RUN',
        'claim':'Derived real-library compatibility specimens; no canonical promotion or independent educational acceptance.'})
    return directory/'manifest.json'

def build_physics():
    """The real ten-question friction product plus a declared nonphysical toy.

    The added example tests the optional model-scope operator independently of
    chemistry. Its formula is a given demonstration, not a friction or barrier
    model; the real source-question selection and original library stay intact.
    """
    manifest_path=ROOT/'products/physics/phy-nlm-friction.manifest.json'
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    source=ROOT/manifest['package_refs'][0]
    p=json.loads(source.read_text(encoding='utf-8'))
    calibration=json.loads((OUT.parent/'matrix/package.v1.json').read_text(encoding='utf-8'))
    qid='Q-ISS29-PHY-MODEL-SCOPE';mid='MIC-ISS29-PHY-MODEL-SCOPE';capid='CAP-ISS29-PHY-MODEL-SCOPE';repid='REP-ISS29-PHY-MODEL-SCOPE';famid='FAM-ISS29-PHY-MODEL-SCOPE';uid='CU-ISS29-PHY-MODEL-SCOPE'
    resource=copy.deepcopy(calibration['resources'][0]);p['resources'].append(resource)
    cap=copy.deepcopy(calibration['capabilities'][0]);cap.update(id=capid,action='Distinguish a given angular factor from a total depending on an independent contribution.',success_criterion='Hold theta fixed while changing c; identify changed total E without predicting a physical barrier.');p['capabilities'].append(cap)
    family=copy.deepcopy(calibration['question_families'][0]);family.update(id=famid,title='Given toy partial factor versus total',capability_refs=[capid],item_refs=[qid]);p['question_families'].append(family)
    q=copy.deepcopy(calibration['questions'][0]);q.update(id=qid,original_identifier=qid,stem='Given the dimensionless demonstration g=cos(theta), E=−g²+c, take theta=60 degrees. Compare c=0 and c=1. Does the same g determine a unique E? This is a chosen toy expression, not a physical energy law or barrier calculation.',primary_capability_ref=capid,family_ref=famid,figure_refs=[repid],exposure=[{'core':'CORE1A','role':'PLANNED_WORKED_ANCHOR','artifact_ref':None}],conditions=['The formula and arbitrary units are stipulated.','c is an independent contribution; theta is held fixed.','No real force, energy barrier, or friction prediction follows.'])
    moves=[('Hold theta at 60 degrees.','The requested comparison changes c alone.','g=cos(60 degrees)=1/2 in both cases.'),('Evaluate the explicitly given partial term.','Squaring is a chosen definition in this toy, not a universal physical law.','−g²=−1/4.'),('Add each independent contribution.','The total is defined as this partial term plus c.','At c=0, E=−1/4; at c=1, E=3/4.'),('Compare the outputs and the claim.','Two different totals with identical g refute uniqueness from g alone.','The same angular factor does not determine total E; no physical barrier was calculated.')]
    route=[{'id':qid+f'-MOVE-{n}','kind':'VERIFY' if n==4 else 'TRANSFORM','action':a,'why_valid':w,'inputs':[q['stem']] if n==1 else [moves[n-2][2]],'output':o} for n,(a,w,o) in enumerate(moves,1)]
    q['answer'].update(summary='At theta=60 degrees, both have g=1/2; E changes from −1/4 to 3/4 as c changes from 0 to 1.',reasoning=[a+' '+w+' '+o for a,w,o in moves],reasoning_route=route,crux_move_ref=route[2]['id'],check='At theta=90 degrees, g=0 and E=c, so c still changes the total without changing g.')
    q['extensions']={'grade9v3:authorship':{'kind':'AI_AUTHORED_CALIBRATION','owner_supplied':False}}
    q['difficulty']={'band':'D2','score':3,'components':dict(zip(KEYS,[1,0,1,0,1])),'basis':'Connect a chosen partial model term to an independent contribution, preserving the boundary between demonstration and physical prediction.'}
    q['hints']=[];q['hint_ladder']=[];q.pop('repair_ref',None);q['representation_roles']={};p['questions'].append(q)
    rep=copy.deepcopy(calibration['representations'][0]);rep.update(id=repid,purpose='Show the two independent inputs to a stipulated toy total.',relation_refs=[],correspondence=[{'element':'two inputs','symbol':'theta and c','in_words':'Theta determines g; the independent c also enters E.'}])
    stages=[{'id':'VIS-ISS29-PHY-TOY-1','label':'Two inputs','purpose':'Distinguish the angle input from the independent contribution.','visible_elements':['theta','c']},{'id':'VIS-ISS29-PHY-TOY-2','label':'Dependencies','purpose':'Show both dependencies entering the chosen total expression.','visible_elements':['theta','c','E']},{'id':'VIS-ISS29-PHY-TOY-3','label':'Boundary','purpose':'Make the nonphysical model boundary explicit before interpreting an output.','visible_elements':['theta','c','E','boundary']}];rep['reveal_stages']=stages
    asset=OUT/'physics/assets/model-scope.svg';asset.parent.mkdir(parents=True,exist_ok=True)
    asset.write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 620 180" role="img" aria-label="Toy total has two independent inputs" font-size="20"><title>Two inputs to a stipulated toy expression</title><desc>Angle theta determines g. An independent c also enters total E; no physical law is inferred.</desc><g data-g9-stage-id="VIS-ISS29-PHY-TOY-1"><text x="24" y="40">theta → given factor g = cos(theta)</text><text x="24" y="80">independent contribution c</text></g><g data-g9-stage-id="VIS-ISS29-PHY-TOY-2"><text x="24" y="125">g and c → chosen toy E = −g² + c</text></g><g data-g9-stage-id="VIS-ISS29-PHY-TOY-3"><text x="24" y="160">No physical barrier is computed.</text></g></svg>',encoding='utf-8')
    rep['rendered_asset_refs']=[asset.relative_to(ROOT).as_posix()];rep['support_stage_map']=[{'support_level':'low','visual_stage_ref':stages[0]['id']},{'support_level':'medium','visual_stage_ref':stages[1]['id']}];p['representations'].append(rep)
    m=copy.deepcopy(calibration['microtopics'][0]);m.update(id=mid,title='A bounded angular factor and an independent total contribution',bucket_id=p['microtopics'][0]['bucket_id'],primary_capability_ref=capid,representation_refs=[repid],question_family_refs=[famid],inferential_jump='A partial factor cannot fix a total that also depends on an independent input.',entry_assumptions=q['conditions'])
    m['teaching_path']=[{**{k:v for k,v in row.items() if k!='kind'},'role':'VERIFY' if row['kind']=='VERIFY' else 'TRANSFORM'} for row in route]
    unit=m['construction_units'][0];unit.update(id=uid,decision=m['inferential_jump'],step_refs=[row['id'] for row in route],representation_ref=repid,reveal_stage_refs=[s['id'] for s in stages],worked_anchor_ref=qid,independent_checks=[{'statement':q['answer']['check'],'role':'CHECK'},{'statement':'At theta=60 degrees and c=−1, the toy gives E=−5/4.','role':'APPLY'},{'statement':'Identify both independent inputs before treating a partial factor as a total.','role':'CONNECT'}])
    repair={'question_ref':qid,'label':'Toy model-scope example','construction_ref':uid,'microtopic_ref':mid,'interaction':'MODEL_SCOPE_PROBE','clarify':'Distinguish a partial angular factor from a total with an independent contribution.','connect':'Two independent variables can affect the same total.','way':'Hold theta fixed and change only c.','rule':m['inferential_jump'],'check':q['answer']['check'],'probe':'Hold theta at 90 degrees and compare c=−1 with c=1. Can g alone identify the total?','pattern':'Both have g=0; the totals are −1 and 1. Repeatedly treating g=0 as total E=0 suggests the omitted-contribution rule, rather than an isolated arithmetic slip.','transfer':'Use theta=60 degrees and c=−1: E=−5/4 in the stipulated toy.','wrong_idea':'A zero partial term forces every contribution to the total to be zero.'}
    repair['crux_move_ref']=q['answer']['crux_move_ref'];q['extensions']['grade9v3:learning_repair']=repair
    m['extensions']['grade9v3:question_repairs']=[repair]
    m['misconceptions']=[{'wrong_idea':repair['wrong_idea'],'diagnostic_prompt':repair['probe'],'repair':repair['pattern']+' '+repair['rule']}]
    m['exit_task']={'prompt':repair['probe'],'source_ref':'SRC-ISS29-SUPPLEMENT','answer':{'kind':'MODEL_RESPONSE','summary':repair['pattern'],'reasoning':[repair['rule']],'check':repair['transfer'],'acceptable_alternatives':[],'subpart_answers':[],'verification_status':'CHECKED_BY_AUTHOR'},'oracle':{'held_by':'ISS-ISS29-PHY-TOY-REVIEW'}}
    m['compact_anchor']={'prompt':q['stem'],'result':q['answer']['summary']};p['microtopics'].append(m)
    p['known_issues'].append({'id':'ISS-ISS29-PHY-TOY-REVIEW','affected_refs':[mid,qid],'classification':'SCIENTIFIC_REVIEW_REQUIRED','description':'The formula is a stipulated demonstration, not an accepted physical energy model.','next_action':'Review the exact optional probe and its boundaries.'})
    directory=OUT/'physics';save(directory/'package.v1.json',p)
    # Keep authentic question/custody fields, but correct this derived authored
    # support lane's collision between normal reaction and the source's N=10mu.
    source_ctx=render_core.context(manifest_path)
    bank_questions=[copy.deepcopy(q) for ref in manifest['bank_refs'] for q in json.loads((ROOT/ref).read_text())['questions']]
    source_questions=copy.deepcopy(bank_questions)
    for question in bank_questions:
        if question['id']=='PYQ-PHY-IITJEE-2011-P1-Q41':
            for scaffold in question.get('scaffolds',[]):
                scaffold['text']=scaffold['text'].replace('change N.','change R_perp.').replace('μN','μR_perp')
                if 'prompt' in scaffold:scaffold['prompt']=scaffold['prompt'].replace('What are N and','What are R_perp and')
            ans=question['answer']
            def normal_text(value):return value.replace('N=mg','R_perp=mg').replace('μN','μR_perp')
            ans['reasoning']=[normal_text(s) for s in ans['reasoning']]
            for row in ans['reasoning_route']:
                for key in ('action','why_valid','output'):row[key]=normal_text(row[key])
        if question['id']=='PYQ-PHY-JEEADV-2020-P1-Q13':
            question['extensions']['grade9v3:review_scope']='Advanced rigid-body torque/contact extension; outside the baseline friction-only teaching scope. Rendering does not establish its prerequisite exposure.'
    for original,derived in zip(source_questions,bank_questions):
        for field in ('id','stem','options','conditions','figure_refs','representation_roles','original_identifier'):assert original.get(field)==derived.get(field)
        assert original['extensions']['grade9v3:source_custody']==derived['extensions']['grade9v3:source_custody']
        assert original['answer']['summary']==derived['answer']['summary']
    save(directory/'bank.v1.json',{'schema_version':'review-bank/v1','questions':bank_questions})
    manifest['bank_refs']=[(directory/'bank.v1.json').relative_to(ROOT).as_posix()]
    manifest['package_refs']=[(directory/'package.v1.json').relative_to(ROOT).as_posix()];manifest['home_href']='index.html';manifest['question_bank_href']='index.html';manifest['selection']['microtopics'].append(mid)
    save(directory/'manifest.json',manifest)
    save(directory/'derivation.json',{'source_manifest':manifest_path.relative_to(ROOT).as_posix(),'source_package':source.relative_to(ROOT).as_posix(),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'source_questions_unchanged':True,'source_question_count':10,'added_authored_specimen':qid,'scope':'Nonchemistry optional model-scope demonstration with explicitly stipulated units and formula.'})
    return directory/'manifest.json'

if __name__=='__main__':
    print(build_math().relative_to(ROOT).as_posix())
    print(build_physics().relative_to(ROOT).as_posix())
