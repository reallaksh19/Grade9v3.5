"""R4 authored support: question-local givens, protected metadata and diagnosis.

Frozen stems/conditions/figure references/custody stay unchanged. New visuals
are explicitly authored corrections, not fabricated authentic source figures.
"""
import copy, json, math
from html import escape as esc
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
BASE=ROOT/'evidence/blueprint-cycles'

def text(x,y,s,size=20): return f'<text x="{x}" y="{y}" font-size="{size}">{esc(s)}</text>'
def line(x,y,a,b,double=False):
    result=f'<line x1="{x}" y1="{y}" x2="{a}" y2="{b}" stroke="#334155" stroke-width="3"/>'
    if double:
        length=math.hypot(a-x,b-y);ox=-(b-y)*6/length;oy=(a-x)*6/length
        result+=f'<line x1="{x+ox}" y1="{y+oy}" x2="{a+ox}" y2="{b+oy}" stroke="#334155" stroke-width="3"/>'
    return result
def molecule(cx,cy,center,ends,lp=0,caption=''):
    result=text(cx-12,cy,center,24)
    positions=[(-100,0),(90,0),(0,-75),(0,75)]
    for (name,multiplicity),(dx,dy) in zip(ends,positions):
        result+=line(cx+(20 if dx>0 else -20 if dx<0 else 0),cy-8+(15 if dy>0 else -15 if dy<0 else 0),cx+dx-(20 if dx>0 else -20 if dx<0 else 0),cy+dy-8,multiplicity>=2)
        if multiplicity==3:result+=line(cx+(20 if dx>0 else -20 if dx<0 else 0),cy-15,cx+dx-(20 if dx>0 else -20 if dx<0 else 0),cy+dy-15)
        result+=text(cx+dx-12,cy+dy,name,24)
    if lp:result+=text(cx-10,cy+35,':'*lp,24)
    if caption:result+=text(cx-115,cy+110,caption)
    return result
def chain(cx,cy,names,orders,caption=''):
    result='';positions=[cx]
    for name in names[:-1]:positions.append(positions[-1]+max(125,len(name)*15+55))
    for i,name in enumerate(names):
        x=positions[i];result+=text(x,cy,name,24)
        if i<len(orders):result+=line(x+len(name)*15+8,cy-7,positions[i+1]-12,cy-7,orders[i]>=2)
        if i<len(orders) and orders[i]==3:result+=line(x+len(name)*15+8,cy-14,positions[i+1]-12,cy-14)
    if caption:result+=text(cx,cy+65,caption)
    return result
def contributors(center):
    result=''
    for i,cx in enumerate([130,380,630]):
        ends=[('O' if i==j else 'O−',2 if i==j else 1) for j in range(3)]
        result+=molecule(cx,180,'N+' if center=='N' else 'C',ends)
        for j,(dx,dy) in enumerate([(-100,0),(90,0),(0,-75)]):
            result+=text(cx+dx-26,180+dy+28,'·· ··' if i==j else '·· ·· ··',18)
        result+=text(cx-95,320,f'Contributor {i+1}')
    return result
def overlap():
    result=''
    for i,x in enumerate([65,425]):
        result+=text(x,90,'A: end-on' if i==0 else 'B: side-on')
        result+=f'<path d="M{x} 195H{x+265}" stroke="#64748b" stroke-dasharray="6 4" stroke-width="2"/>'
        for center in [x+70,x+185]:
            result+=f'<circle cx="{center}" cy="195" r="5" fill="#334155"/>'
            for d in [-1,1]:
                px=center+d*30 if i==0 else center;py=195 if i==0 else 195+d*38
                result+=f'<ellipse cx="{px}" cy="{py}" rx="{35 if i==0 else 20}" ry="{20 if i==0 else 35}" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>'
        result+=text(x,290,'Same nucleus-to-nucleus reference')
    return result

# The drawings below contain supplied connectivity/conditions, never the
# requested hybrid labels, model choice, corrected count or electron totals.
CH4=lambda x,y:molecule(x,y,'C',[('H',1)]*4,caption='CH4 connectivity')
NH3=lambda x,y:molecule(x,y,'N',[('H',1)]*3,lp=1,caption='NH3 Lewis inventory')
BF3=lambda x,y:molecule(x,y,'B',[('F',1)]*3,caption='BF3 Lewis inventory')
HCHO=lambda x,y:molecule(x,y,'C',[('H',1),('O',2),('H',1)],caption='H2C=O connectivity')
CO2=lambda x,y:chain(x,y,['O','C','O'],[2,2],'CO2 connectivity')
HCN=lambda x,y:chain(x,y,['H','C','N:'],[1,3],'HCN connectivity; : is the N lone pair')
ALLENE=lambda x,y:chain(x,y,['H2C','C','CH2'],[2,2],'Allene connectivity')
PROPYNE=lambda x,y:chain(x,y,['CH3','C','CH'],[1,3],'Propyne connectivity')
ETHENE=lambda x,y:chain(x,y,['H2C','CH2'],[2],'Ethene connectivity')
AMIDE=lambda x,y:chain(x,y,['H-C(=O)','NH2:'],[1],'Formamide connectivity; : is the N lone pair')
SPACER=lambda x,y:chain(x,y,['H-C(=O)','CH2','NH2:'],[1,1],'Saturated spacer; no changed connectivity')
def pair(a,b):return a(170,180)+b(540,180)
def nf3():
    result=molecule(380,185,'N',[('F',1)]*3,lp=1,caption='NF3 Lewis inventory')
    for x,y in [(280,185),(470,185),(380,110)]:result+=text(x-24,y+28,'·· ·· ··',18)
    return result

JOBS={
 'D1':[
  ('Four supplied equivalent directions', ''.join(line(380,190,380+105*math.cos(t),190+105*math.sin(t)) for t in [0,math.pi/2,math.pi,3*math.pi/2])+text(350,195,'Atom'), 'Connect a direction inventory to a conserved orbital basis; choose the set name yourself.'),
  ('H2C=O supplied Lewis connectivity',HCHO(380,180),'Keep the neighbour ledger separate from the shared-pair ledger.'),
  ('CH4 supplied connectivity',CH4(380,180),'Count at the selected centre before matching the known introductory rule.'),
  ('NH3 supplied Lewis inventory',NH3(380,180),'Preserve the given connections and lone pair when constructing your own depth-coded drawing.'),
  ('Requested output: domain arrangement',text(90,140,'Candidate: VSEPR')+text(400,140,'Candidate: orbital overlap')+text(90,225,'Overall domain arrangement requested')+text(90,275,'Detailed overlap excluded'),'Match a model to the requested output; the choice is yours.'),
  ('Supplied overlap situations A and B',overlap(),'Use the shared internuclear reference; classify the two orientations yourself.'),
  ('CH4 connectivity to be translated',CH4(380,180),'A page layout records connectivity. You must declare the depth convention.'),
  ('NF3 atom-local inventory',nf3(),'Select the requested N centre. Distinguish each atom’s own lone pairs before counting.'),
  ('H2C=O counting operation to audit',HCHO(380,180),'Compare bond lines with bonded-neighbour directions; write your corrected count.'),
  ('Supplied BF3 and CH4 inventories',pair(BF3,CH4),'Match each given inventory to a set name, then check input/output conservation.')],
 'D2':[
  ('Supplied three-bond comparison',pair(BF3,NH3),'Track bonded neighbours and central lone pairs in separate columns.'),
  ('H2C=O connectivity',HCHO(380,180),'Allocate the same carbon valence basis to the requested sigma and pi jobs.'),
  ('Ethene Lewis connectivity',ETHENE(230,180),'Declare the molecular-plane reference before translating into orbital directions.'),
  ('CO2 Lewis connectivity',CO2(210,180),'Keep local domains, bond components and available basis functions as separate inventories.'),
  ('Supplied BF3 and NH3 counterexample candidates',pair(BF3,NH3),'Test the claimed sufficient condition without replacing the supplied observations.'),
  ('CH3F and CH4 connectivity',molecule(170,180,'C',[('H',1),('F',1),('H',1),('H',1)],caption='CH3F connectivity')+CH4(540,180),'Substituent identity and the number of neighbour directions are different quantities.'),
  ('Supplied HCN Lewis connectivity',HCN(210,180),'Make separate local inventories at C and N; bond multiplicity is a separate ledger.'),
  ('Supplied methylamine connectivity',chain(250,180,['CH3','NH2:'],[1],'Nitrogen lone pair is marked by :'),'Select one centre at a time before comparing bonded-atom arrangements.'),
  ('Supplied local carbon jobs',text(90,125,'Three sigma directions; no lone pair')+text(90,210,'One pi participation')+text(90,295,'Available valence basis: one 2s and three 2p'),'Allocate each basis function once. The completed orbital arrangement is your response.'),
  ('Supplied four-domain comparisons',CH4(155,175)+NH3(405,175)+molecule(650,175,'O',[('H',1),('H',1)],lp=2,caption='H2O Lewis inventory'),'Separate all domain slots from the positions occupied by bonded nuclei.')],
 'D3':[
  ('Supplied nitrate contributors',contributors('N'),'Compare a permanent unequal-bond interpretation with the supplied bond-equivalence observation.'),
  ('Nitrate contributors to be translated',contributors('N'),'Keep one nuclear framework while changing from formal contributors to orbital accounting.'),
  ('Supplied allene connectivity',ALLENE(210,180),'Select each carbon locally, then coordinate the required neighbouring overlaps.'),
  ('Ethene and allene connectivity',ETHENE(65,150)+ALLENE(385,220),'Use each declared plane and relative orbital direction, rather than copying page geometry.'),
  ('Supplied equivalence observations',text(90,120,'CO2: equivalent C-O; supplied linear shape')+text(90,195,'NO3−: equivalent N-O; supplied planar shape')+text(90,270,'NH3: equivalent N-H; supplied pyramidal shape'),'Bond equivalence and local domain inventory must be tested as distinct criteria.'),
  ('Supplied propyne connectivity',PROPYNE(210,180),'Count connected atom pairs for the sigma ledger and account separately for multiplicity.'),
  ('Supplied carbonate contributors',contributors('C'),'Distinguish formal-contributor bookkeeping from the requested complete pi-space model.'),
  ('Ethane and ethene connectivity',chain(65,150,['CH3','CH3'],[1],'Ethane')+ETHENE(435,220),'Hold the central axis fixed while distinguishing whole-picture from relative-group rotation.'),
  ('Supplied pathway comparison',chain(35,125,['CH2','CH','CH','CH2'],[2,1,2],'First connectivity')+chain(35,245,['CH2','CH','CH2','CH','CH2'],[2,1,1,2],'Second connectivity'),'Mark orbital availability and adjacency; draw the pathway you judge to be continuous.'),
  ('Supplied local-procedure tests',PROPYNE(45,140)+ALLENE(405,235),'Apply one local inventory procedure to each selected atom, then check neighbours.')],
 'D4':[
  ('Supplied formamide connectivity',AMIDE(240,180),'Separate local counting from the supplied donation/alignment conditions.'),
  ('Fixed connectivity for two arrangements',AMIDE(240,150)+text(90,285,'Construct reference and twisted arrangements yourself'),'Declare the C-N viewing axis. Preserve inventories while changing relative orientation.'),
  ('Supplied qualitative twist result',text(90,130,'Fixed atom connectivity')+text(90,215,'Given: twist toward 90° reduces alignment')+text(90,290,'Given: delocalisation contribution decreases'),'Connect the supplied trend to a bounded mechanism; tag assumptions and observations.'),
  ('Supplied direct/spacer comparison',AMIDE(35,140)+SPACER(350,240),'Test local count, orbital availability, adjacency and alignment separately.'),
  ('Supplied counterexample observations',text(90,110,'CH4: ~109.5°; NH3: ~107°; H2O: ~104.5°')+text(90,190,'Given: common introductory sp3 descriptions')+text(90,270,'Given: approximately planar amide N with donation'),'Test the uniqueness claim against the supplied data, then state a qualified replacement.'),
  ('The two supplied nitrogen sites',AMIDE(35,140)+SPACER(350,240),'Recall the local rule, then separately decide whether its conditions hold.'),
  ('Supplied methyl-radical model',text(90,130,'CH3· is supplied as approximately planar')+text(90,215,'Given: one unpaired electron in a perpendicular p-like orbital')+text(90,295,'Three C-H sigma directions'),'Translate occupancy as well as orientation. The empty-orbital generalisation remains your judgement.'),
  ('Two descriptions to discriminate',text(70,120,'A: localised pyramidal nitrogen lone pair')+text(70,210,'B: approximately planar N; possible carbonyl donation')+text(70,300,'Propose observations; no measured strength is given'),'For each proposed observation state competing predictions and an inference limit.'),
  ('Supplied cosine-factor model',text(90,125,'Given: g = cos(θ)')+text(90,210,'Compare θ = 0°, 60°, 90°')+text(90,295,'Assess a separate claim about total molecular energy'),'Keep the supplied factor and an energy model as distinct variables.'),
  ('Supplied universal-rule audit cases',text(90,125,'NH3; allene; formamide; saturated-spacer amine')+text(90,210,'Proposed rule: count → label → every shape/reactivity')+text(90,295,'Audit the rule and construct a qualified procedure'),'Use the different cases to test distinct boundaries; do not replace one universal slogan with another.')]
}

for issue in (32,31,34,33,36,35,38,37):
    directory=BASE/f'ISS{issue}'
    bank=json.loads((directory/'inputs/owner.bank.json').read_text())
    package=json.loads((directory/'inputs/package.v1.json').read_text())
    band=f'D{(issue-31)//2+1}'
    for index,q in enumerate(bank['questions']):
        title,drawing,bridge=JOBS[band][index]
        rid=f'REP-ACADEMIC-ISS{issue}-Q{index+1}'
        stage1=f'{rid}-GIVENS';stage2=f'{rid}-BRIDGE'
        asset=directory/'assets'/f'question-{index+1}-givens.svg'
        import textwrap
        bridge_lines=textwrap.wrap(bridge,width=78)
        bridge_svg=''.join(text(45,438+24*i,s,18) for i,s in enumerate(bridge_lines))
        svg=(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 510" role="img" aria-label="{esc(title)}">'
             f'<title>{esc(title)}</title><desc>Authored support for the supplied situation. No final classification or computed answer is shown.</desc>'
             '<style>text{font-family:Arial,sans-serif;fill:#0f172a;stroke:none}</style>'
             f'<g data-g9-stage-id="{stage1}">{text(35,45,title,22)}{drawing}'
             f'{text(35,385,"Connectivity layout only; page angles are not measured geometry.",18)}</g>'
             f'<g data-g9-stage-id="{stage2}">{text(35,45,title,22)}{drawing}'
             '<rect x="30" y="405" width="760" height="88" rx="10" fill="#eff6ff" stroke="#2563eb"/>'
             f'{bridge_svg}</g></svg>')
        asset.write_text(svg,encoding='utf-8',newline='\n')
        old=next((r for r in package['representations'] if r['id']==rid),None)
        if old is not None:package['representations'].remove(old)
        rep=copy.deepcopy(package['representations'][0]);rep.update(id=rid,kind='STRUCTURAL_FORMULA',purpose=bridge,
                rendered_asset_refs=[asset.relative_to(ROOT).as_posix()],scene_instances=[],
                required_elements=['Supplied situation','Question-local bridge'],read_order=[title,bridge],
                correspondence=[{'element':'labels and connectivity','symbol':'given situation','in_words':title}],
                misleading_alternatives=['Using a different species or printing the requested final decision before commitment.'],
                reveal_stages=[{'id':stage1,'label':'Supplied situation','purpose':title,'visible_elements':['Supplied situation']},
                               {'id':stage2,'label':'Question-local bridge','purpose':bridge,'visible_elements':['Question-local bridge']}])
        rep['extensions']={'grade9v3:stage_mode':'REPLACE','grade9v3:authored_question_ref':q['id']}
        package['representations'].append(rep)
        q['extensions']['grade9v3:core2_visual_review']={
            'question_ref':q['id'],'authored_figure_refs':[rid],
            'replaces_authored_figure_refs':q.get('figure_refs',[]),
            'rationale':'Use the actual supplied species/conditions; leave the requested classification, construction and computed result to the learner. Frozen authored refs remain in custody data.',
            'third_stage_waiver':'A third stage would repeat the route or perform the requested construction. The two authored stages support situation and bridge; the response remains learner work.',
            'review_status':'AUTHOR_REFERENCE_GROUNDED_REVIEW_NOT_INDEPENDENT_ACCEPTANCE'}
        q['scaffolds'][0].update(visual_ref=rid,visual_stage_ref=stage1)
        q['scaffolds'][1].update(visual_ref=rid,visual_stage_ref=stage2)
        if band=='D2' and index==3:
            repair=q['extensions']['grade9v3:learning_repair']
            repair.update(wrong_idea='Each multiple-bond component needs an extra carbon orbital beyond the available valence basis.',
                probe='Allocate the carbon basis in CO2 and HCN. For each, count axial hybrid functions and residual p functions. Does bond multiplicity create extra carbon basis functions?',
                pattern='Both local carbon ledgers have two sp hybrids plus two residual p functions, total four. Repeated larger totals or a third residual p function identify a double-counting rule rather than one addition slip.',
                transfer='Check the carbon orbital allocation in ethyne while retaining one 2s and three 2p inputs.')
        if band=='D3' and index==0:
            repair=q['extensions']['grade9v3:learning_repair']
            repair.update(probe='For nitrate, predict whether one permanently selected N=O position would have the same bond properties as both remaining N-O positions. Test the same interpretation against the supplied equivalent carbonate bonds. Do formal contributors mean the nuclei switch structures?',
                pattern='A permanently unequal single/double-bond interpretation conflicts with the supplied equivalence in both ions. Repeating that interpretation, or literal temporal switching, suggests a held model error; revising it on the second case after one notation slip does not establish that misconception.',
                transfer='Explain why a single permanent double-bond position cannot represent the supplied three equivalent carbonate bonds.')
        if band=='D3' and index==3:
            analysis=q['extensions']['grade9v3:analysis']
            analysis['difficulty']['basis']='Coordinate each local sigma framework with the residual p directions and neighbouring overlap requirements. The argument is an introductory localized construction, not a proof of a universal zero overlap integral.'
            analysis['stable_crux_move']='Allocate the central carbon basis, then match each terminal p direction to a different central p direction within the declared localized model.'
        # Keep the teaching-clinic copies bound to the same reviewed question.
        repair=q['extensions']['grade9v3:learning_repair']
        for m in package['microtopics']:
            copies=m.get('extensions',{}).get('grade9v3:question_repairs',[])
            for j,row in enumerate(copies):
                if row.get('question_ref')==q['id']:copies[j]=copy.deepcopy(repair)
            if band=='D3' and index==0:
                for misconception in m.get('misconceptions',[]):
                    if misconception['wrong_idea']==repair['wrong_idea']:
                        misconception.update(diagnostic_prompt=repair['probe'],repair=repair['rule']+' Changed check: '+repair['transfer'])
    for name,value in [('owner.bank.json',bank),('package.v1.json',package)]:
        (directory/'inputs'/name).write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
print('80 question-local authored supports saved; supplied stems/conditions/figure refs/custody preserved. Two misaligned diagnostic probes corrected.')
