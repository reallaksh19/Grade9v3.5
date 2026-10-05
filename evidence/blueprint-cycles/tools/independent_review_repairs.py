"""Apply explicit R5 reviewer findings without changing frozen source questions."""
import copy,json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]; BASE=ROOT/'evidence/blueprint-cycles'
def save(p,obj):p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')

HINTS={
 0:'Compare the predicted bond properties of a permanently selected contributor with the supplied equivalent positions. Decide which description fits.',
 2:'Use an unfilled four-function carbon ledger. Allocate functions to the stated sigma jobs and leave the remaining direction entries for your construction.',
 8:'Mark each carbon with an unfilled p-availability entry. Test availability, adjacency and relative direction before deciding which links form the pathway.'}
for issue in (32,31,34,33,36,35,38,37):
 p=BASE/f'ISS{issue}/inputs/package.v1.json';b=BASE/f'ISS{issue}/inputs/owner.bank.json'
 package=json.loads(p.read_text());bank=json.loads(b.read_text())
 for n,q in enumerate(bank['questions']):
  repair=q['extensions']['grade9v3:learning_repair']
  if issue in (35,36):
   if n in HINTS:
    q['scaffolds'][1]['text']=repair['connect']=HINTS[n]
   # Concept/family titles can themselves settle the model choice. Neutral
   # attempt labels leave canonical ownership intact; detailed names are inert.
   q['extensions']['grade9v3:attempt_labels']={'question_ref':q['id'],
       'concept':'Atom-local bonding and model comparison',
       'family':'Construct or test the supplied bonding description'}
   if n==6:
    repair['probe']='Draw a second formal carbonate contributor by moving electron pairs on the same nuclear framework. Mark which electron entries change and which atoms stay fixed. Reconstruct the perpendicular p-function/electron ledger. Does moving the formal double-bond position assert a different measured C–O bond?'
    repair['pattern']='Contributor drawings move formal electron-pair assignments while retaining the C/O nuclear framework. In the supplied local bookkeeping each retains four participating p functions and six pi-space electrons. The given equivalent C–O bonds are not one permanent unequal single/double pattern. Formal averaged charge is bookkeeping, not measured partial charge.'
    repair['wrong_idea']='A formal contributor is a different nuclear structure with a permanently unequal bond and electron pattern.'
    repair['transfer']='Use a changed nitrate contributor to reconstruct the same nuclear-framework and perpendicular p/electron ledger; do not infer measured atomic charges from formal averages.'
  if issue in (37,38) and n==1:
   repair['probe']='In a blank frame look along the declared C–N axis. Fix a carbonyl p-direction reference and sketch the N donor direction first parallel to it, then at 45 degrees. Label the relative angle and what stays fixed. Use CH3NO valence/total sums only as an inventory check.'
   repair['pattern']='In this end-on reference the carbonyl direction stays fixed; the donor direction rotates by the declared 45 degrees while connectivity and 18 valence/24 total electrons stay fixed. A cosine alignment factor in a stipulated toy does not measure donation strength or a real barrier. A correct sum alone is not evidence of a correct orientation sketch.'
   repair['wrong_idea']='A correct electron inventory is enough to construct the relative donor/carbonyl orientation.'
   repair['check']='Check the labelled fixed axis and relative angle independently; then verify valence 4+3+5+6=18 and total 6+3+7+8=24. The inventory checks do not grade the geometric construction.'
   repair['rule']='Choose the C–N viewing axis and fixed carbonyl reference before rotating the donor direction; preserve atoms and electrons. Under the given localized alignment model a relative direction changes, not the inventory; geometry alone does not quantify a physical barrier.'
   q['extensions']['grade9v3:analysis']['stable_crux_move']='Construct two directions relative to one fixed C–N viewing axis; bound the alignment inference to the supplied localized model.'
   for s in q['scaffolds'][3:]:
    if 'Count valence' in s['text']:s['text']='Try the changed 45-degree orientation in the blank two-frame reference; use electron sums only as a separate inventory check.'
  for m in package['microtopics']:
   if ((issue in (31,32) and n==7) or (issue in (33,34) and n in (1,6,8))):
    rid=f'REP-ACADEMIC-ISS{issue}-Q{n+1}'
    for u in m.get('construction_units',[]):
     if u['id']==repair['construction_ref']:
      u['representation_ref']=rid;u['reveal_stage_refs']=[rid+'-GIVENS',rid+'-BRIDGE']
      if rid not in m['representation_refs']:m['representation_refs'].append(rid)
   copies=m.get('extensions',{}).get('grade9v3:question_repairs',[])
   for j,r in enumerate(copies):
    if r.get('question_ref')==q['id']:copies[j]=copy.deepcopy(repair)
  # Actual remedial teaching may explain the decisive move. The preattempt
  # scaffold remains the neutral framework, not a completed target solution.
 if issue in (35,36):
  items=package.get('extensions',{}).get('grade9v3:purpose_delivery',{}).get('COMPETITION',{}).get('items',[])
  for item in items:
   if item['id']=='CHEM-COMP-TRANSFER-ALLENE-CHIRALITY':
    item['answer']['summary']='Distinct substituents at both allene termini permit axial stereogenicity in the perpendicular terminal-substituent framework. An idealized coplanar terminal framework removes that axial stereogenicity; this is not a claim that all methyl hydrogen atoms lie in one plane.'
    item['answer']['reasoning'][-1]='In the counterfactual coplanar terminal-substituent/backbone framework, the axial stereogenic arrangement disappears. Methyl groups still have tetrahedral local geometry; no literal all-atom coplanarity is asserted.'
   if item['id']=='CHEM-COMP-TRANSFER-CONJUGATION-ENERGY':
    item['title']='Conjugation and the limits of a hydrogenation comparison'
    item['prompt']='In the introductory p-orbital model compare buta-1,3-diene with penta-1,4-diene. Identify the orbital-connected difference. A proposed hydrogenation experiment gives a less exothermic value for a conjugated reactant than an isolated-bond reference. What matching conditions and reference assumptions would be needed before using that difference as evidence about reactant stability? No numerical thermochemical values are supplied.'
    item['answer']['summary']='Contiguous available p directions support the introductory conjugated pathway in butadiene; the saturated spacer interrupts that pathway in pentadiene. A less exothermic hydrogenation may support a relative reactant-stability inference only with suitable products, phases, substitution and experimental/reference controls. It is not a unique measured resonance energy, and the spacer does not prove all quantum interactions vanish.'
    item['answer']['reasoning']=['Construct the atom-local availability and adjacency map before inferring the pathway.','A reaction-enthalpy comparison includes both reactant and product states; match or account for products, phases and substitution.','A chosen isolated-bond reference is a model. Do not identify its difference uniquely with resonance energy or infer zero interaction across a saturated spacer.']
    item['source_label']='Original qualitative model-boundary transfer; no authenticated thermochemical dataset or official exam question claimed.'
 save(p,package);save(b,bank)
print('R5 reviewer-specific hint, metadata, geometric diagnostic and ancillary claims repaired; source custody unchanged.')
