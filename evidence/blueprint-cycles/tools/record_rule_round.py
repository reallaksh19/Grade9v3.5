"""Repeat B -> shared authoring rule -> A -> shared rule on actual R3 bytes.

These are new draft-authority checkpoints, not reconstructed historical releases.
Each snapshot is hashed and each subsequent render uses the production renderer.
"""
import copy,hashlib,json,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3];OUT=ROOT/'evidence/blueprint-cycles/closure-20261005'
RULES=[
('D1',32,31,'Keep neighbour/domain, bond-component and orbital-basis inventories distinct. A pi component is not axial density; VSEPR is qualitative. Each action needs its actual local warrant and output, rather than a generic assertion that the source/model permits it.','Teach construction and its selected visual before summarizing the insight. Every source question needs an exact construction bridge; an exit uses a changed case with a concrete expected result, not a repeated worked input.'),
('D2',34,33,'Close the valence-basis ledger: hybrid outputs plus residual functions equal the independent inputs, with no double use. Nuclear shape excludes lone-pair vertices. A geometry drawing does not uniquely measure an orbital basis.','Maintain a question-specific orbital allocation, conditions and independent changed check. Multiple questions may share a concept; a broad section label does not prove that each requested operation was constructed.'),
('D3',36,35,'Contributors are bookkeeping alternatives, not switching structures. Count the occupied delocalised pi space, not only a drawn double bond. Orthogonal p directions constrain allene terminal planes; Pauli is not a blanket one-bond-per-orbital ban.','Preserve atom-local roles and every relevant electron/charge invariant through representations. Separate a supplied equivalence observation from the model label and from a unique physical orbital/charge claim.'),
('D4',38,37,'Separate local counts, occupancy, adjacency, alignment and empirical evidence. A supplied overlap factor is not total energy. Preserve formal electron inventory under torsion; strength, barrier and unique basis require specified further evidence.','Use explicit model assumptions, a counterfactual or independently changed contribution, and an applicability stopping condition. Diagnosis compares a changed-case response with uncertain patterns; it does not assign mastery or a misconception from opening help.'),
]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(p,r):p.write_text(json.dumps(r,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
registry_path=ROOT/'Shared/web/interactive-page-blueprints.v1.json'
registry=json.loads(registry_path.read_text());registry['registry_version']='1.12.0'
core2=next(b for b in registry['blueprints'] if 'CORE2' in b['core_roles']);core2['version']='1.7.0'
solution=next(c for c in core2['components'] if c['id']=='SOLUTION_STEPS')
core1a=next(b for b in registry['blueprints'] if 'CORE1A' in b['core_roles'])
construction=next(c for c in core1a['components'] if c['id']=='CONSTRUCTION_STEPS')
steps=[]
for band,b,a,question_rule,teaching_rule in RULES:
    before=sha(registry_path)
    solution['authoring']['hint']+=' '+band+' repair: '+question_rule
    save(registry_path,registry)
    b_snapshot=OUT/(band.lower()+'-after-b-blueprint.json');save(b_snapshot,registry)
    subprocess.run([sys.executable,'evidence/blueprint-cycles/tools/refresh.py','--write','--issues',str(b),str(a),'--out',str(OUT/(band.lower()+'-b-to-a-render.json'))],cwd=ROOT,check=True)
    construction['authoring']['hint']+=' '+band+' repair: '+teaching_rule
    save(registry_path,registry)
    a_snapshot=OUT/(band.lower()+'-after-a-blueprint.json');save(a_snapshot,registry)
    subprocess.run([sys.executable,'evidence/blueprint-cycles/tools/refresh.py','--write','--issues',str(b),str(a),'--out',str(OUT/(band.lower()+'-a-feedback-render.json'))],cwd=ROOT,check=True)
    steps.append({'band':band,'order':[b,'SHARED_RULE',a,'SHARED_RULE','RENDER_BOTH'],
      'registry_before_sha256':before,'after_b':{'path':b_snapshot.name,'sha256':sha(b_snapshot)},
      'after_a':{'path':a_snapshot.name,'sha256':sha(a_snapshot)},
      'question_rule':question_rule,'teaching_rule':teaching_rule,'verdict':'IMPLEMENTED_REQUIRES_FINAL_ALL_EIGHT_REGRESSION'})
save(OUT/'cumulative-rule-round.json',{'schema':'issue29-cumulative-rule-round/v1','basis':'NEW_R3_DRAFT_AUTHORITY_EXECUTION','steps':steps,'claim':'Actual rule checkpoints and production regeneration; not eight published blueprint releases or independent educational certification.'})
subprocess.run([sys.executable,'Shared/tools/blueprint_spec.py','--write'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'Shared/tools/build_core_learning_data.py'],cwd=ROOT,check=True)
subprocess.run([sys.executable,'evidence/blueprint-cycles/tools/refresh.py','--write','--out',str(OUT/'all-render.json')],cwd=ROOT,check=True)
