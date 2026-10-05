"""Materialize the second D1 correction cycle; never change source stems or custody.

Routes contain the actual inventory, warrant and output. B is authored before A;
the resulting authored rule is shared, but neither sample is an independent review.
"""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[3]
def move(action, why, output): return (action,why,output)
ROUTES=[
 [move('Read the requested four equivalent domain directions.','The question supplies a tetrahedral four-direction introductory model.','Four model directions must be represented.'),move('Select one valence s and three valence p inputs.','For a second-period centre, these four independent basis functions can be recombined without changing the basis dimension.','2s + 2px + 2py + 2pz: four inputs.'),move('Name the recombined set and count its members.','The name sp3 records one s and three p inputs; the total number is 1+3.','sp3; four hybrid orbitals.'),move('Compare the count with an sp allocation.','One s plus one p has two outputs, so the superscript alone cannot be the set size.','sp has two outputs; the four-member sp3 inventory is consistent.')],
 [move('Make separate neighbour and shared-pair inventories for HCHO.','Two H atoms and one O are attached to C; a C=O double bond contains two shared pairs.','Three neighbours; two pairs in C=O.'),move('Count C-to-O as one local VSEPR domain.','A multiple bond connects one pair of nuclei and supplies one bonded-neighbour direction in local domain counting. Sigma and pi density have different spatial symmetry.','One C=O domain; this does not place pi density on the internuclear axis.'),move('Add the two C-H directions.','Each of the two distinct C-H connections adds one domain and C has no lone pair.','1+1+1 = three C-centred domains.'),move('Recount carbon directions in HCN.','H-C and C-N connect carbon to two neighbours although C-N has three shared pairs.','Two domains in HCN; shared-pair count and neighbour count are different.')],
 [move('Inventory CH4 at carbon.','The supplied Lewis connectivity has four C-H bonds and no C lone pair.','Four bonding domains; zero central lone pairs.'),move('Apply the explicitly supplied four-domain rule.','The task asks for the known introductory correspondence, rather than an experimental determination of orbital coefficients.','Tetrahedral domain geometry; introductory sp3 description.'),move('Check the orbital basis ledger.','One 2s plus three 2p inputs gives four hybrids, matching four model sigma directions.','Four inputs and four outputs; no residual p in this allocation.'),move('Change one substituent without adding a neighbour.','CH3Cl still has four carbon-neighbour connections; different bond properties do not constitute extra domains.','CH3Cl also has four C-centred domains; no exact bond-property claim follows.')],
 [move('Count exactly three N-H connections and one N lone pair.','The question supplies the inventory at nitrogen.','Four domains: three bonds and one lone pair.'),move('Project the four domain directions with a declared depth convention.','Two ordinary lines may denote in-plane directions; a solid wedge denotes toward and a hashed wedge away. The lone-pair slot must replace one bond slot.','N at centre; exactly three labelled H endpoints and one LP direction.'),move('Distinguish domain arrangement from nuclear shape.','Domain geometry counts all four slots; molecular shape counts the three bonded H nuclei.','Tetrahedral domain model; trigonal-pyramidal molecular shape, without an exact-angle inference.'),move('Compare with the four-bond NH4+ inventory.','Replacing the LP slot with a fourth N-H bond adds a bonded nucleus but no fifth domain.','NH3: three H + LP; NH4+: four H. The NH3 drawing must not contain a fourth H.')],
 [move('Specify the required output before choosing a model.','The task asks for qualitative domain arrangement and expressly excludes detailed orbital overlap.','Required output: qualitative three-dimensional domain geometry.'),move('Choose VSEPR for that output.','VSEPR uses the three bonding domains and central lone pair to describe their approximate spatial arrangement.','Four-domain, approximately tetrahedral arrangement; pyramidal bonded-nucleus shape.'),move('Declare unresolved quantities.','A qualitative domain model does not supply orbital wavefunctions, overlap amplitudes or exact measured angles.','No detailed orbital composition, exact angle or spectrum is determined.'),move('Change the required output to axial versus lateral overlap.','That question needs orbital orientation/symmetry information beyond a geometry-only model.','An orbital-overlap account is now required; familiarity alone cannot select the model.')],
 [move('Mark the line joining the nuclei in each sketch.','Sigma/pi labels refer to overlap relative to this internuclear axis, not to page orientation.','A common geometric reference is declared.'),move('Classify A from its stated end-on overlap.','The supplied overlap is axial; in the introductory sketch the sigma component is symmetric about the bond axis.','A is sigma overlap.'),move('Classify B from side-on p overlap.','The supplied parallel lateral lobes have a nodal plane containing the axis.','B is pi overlap.'),move('Rotate the whole picture, including its axis.','A rigid rotation preserves all relative orientation and symmetry relations.','Neither classification changes under whole-picture rotation.')],
 [move('Retain the four C-H connections from Lewis notation.','A Lewis cross records connectivity; its page angles do not measure molecular angles.','C at centre with four H endpoints; no bond is added or removed.'),move('Declare and use a wedge/dash convention.','A solid wedge points toward the viewer, a hashed wedge away; ordinary lines lie in the chosen page plane.','Two in-plane bonds, one toward bond and one away bond represent a tetrahedral model.'),move('Explain the physical and projected angles separately.','The ideal tetrahedral model has about 109.5-degree physical angles, while a projection distorts page angles.','The flat cross does not assert square-planar CH4; depth belongs to the 3D interpretation.'),move('Change viewpoint and recount endpoints.','A rotation or a different projection preserves connectivity and noncoplanar geometry.','Four C-H bonds remain; the drawing is a projection of the same tetrahedron.')],
 [move('Choose nitrogen as the counting centre.','The requested domains are centred on N, not on the entire NF3 molecule.','Three N-F bonding directions are included.'),move('Assign each lone pair to its own atom.','N has one lone pair; terminal F lone pairs belong to F-centred inventories.','One N lone pair included; terminal F lone pairs excluded from the N count.'),move('Add the local entries.','The N inventory has three bonded directions plus one central lone pair.','3+1 = four nitrogen-centred domains.'),move('Substitute H for F in the local comparison.','NH3 has the same three-bond/one-central-pair N inventory even though terminal atoms differ.','NH3 also has four N domains; terminal pairs were not required for that total.')],
 [move('Identify the faulty C=O line-counting entry.','Two drawn bond lines denote two bond components to one O neighbour.','The student counted one neighbour twice.'),move('Replace bond-line counting with local neighbour counting.','In VSEPR a multiple bond supplies one bonded-neighbour domain; pi density is lateral rather than an extra atom direction.','C=O contributes one domain, not two.'),move('Compute the corrected HCHO total.','There are two distinct H neighbours, one O neighbour and no C lone pair.','2+1+0 = three C-centred domains.'),move('Apply the operation to CO2.','Two C=O bonds connect C to two O neighbours; four drawn bond lines do not imply four local domains.','CO2 carbon has two domains in the introductory model.')],
 [move('Read the two supplied domain inventories.','The task supplies three B bonding domains and four C bonding domains, with no central lone pairs.','BF3: three; CH4: four.'),move('Match each inventory to a conserved valence-basis allocation.','One s plus two p yields three hybrids; one s plus three p yields four.','BF3: sp2, three hybrids; CH4: sp3, four hybrids.'),move('Match the ideal domain arrangement within this introductory model.','Three equivalent model directions are planar; four are tetrahedral. These labels are model descriptions.','BF3: trigonal planar; CH4: tetrahedral.'),move('Reconstruct an sp inventory as a third case.','One s plus one p provides two inputs and therefore two hybrid outputs.','The set-size sequence is sp=2, sp2=3, sp3=4, rather than the superscripts 1,2,3.')],
]

def write(path, record): path.write_text(json.dumps(record,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
def fresh_exit(m, q):
    # Each prompt differs from the unit's worked paired cases; it stays authored lesson material.
    n=int(q['original_identifier'][1:])
    cases={
      1:('For a second-period centre allocated an sp set, inventory the hybrid outputs and unused p functions. Show that the valence basis is conserved.','Two sp hybrids plus two unused p functions: four outputs from one s plus three p inputs.'),
      2:('At carbon in CO2, count local domains and then separately count the shared pairs in both C=O bonds. Explain why the totals differ.','Two carbon-neighbour domains; four shared pairs. Each double bond connects one O neighbour.'),
      3:('Use the introductory local rule for carbon in CH2Cl2. Give the domain inventory and model geometry without claiming identical bond properties.','Four C-neighbour domains and no lone pair; tetrahedral domain model with introductory sp3 accounting. Bond identity does not fix lengths or exact angles.'),
      4:('Draw a depth-labelled domain model for H2O: two O-H bonds and two central lone pairs. Separate domain arrangement from bonded-nucleus shape.','Four O-centred domains: two bonds and two lone pairs. Introductory tetrahedral domain arrangement; bent molecular shape. Exactly two H endpoints.'),
      5:('A new task asks which orbital directions could produce the pi component in ethene and which plane contains its node. Choose the information needed and name one prediction a domain-count-only account cannot supply.','An orbital-overlap account is needed: perpendicular p functions overlap laterally with a node in the molecular plane. Domain counting alone does not supply this orbital symmetry.'),
      6:('An end-on sketch is rotated together with its internuclear axis by 45 degrees on the page. Classify the overlap and justify the invariant you used.','It remains sigma: relative axial overlap is unchanged by rigid rotation.'),
      7:('Project a tetrahedral four-bond CH3Cl model from a new viewing direction. Declare your depth convention and state what connectivity and angle information is invariant.','Exactly three H and one Cl stay attached to C. Toward/away/in-plane conventions preserve the tetrahedral model; page angles are projections, not measured molecular angles.'),
      8:('Count O-centred domains in OF2 given two O-F single bonds and two lone pairs on O. Explain how you treat the terminal-F lone pairs.','Four O-centred domains: two bonds plus two O lone pairs. F-centred lone pairs are excluded from the O count.'),
      9:('Audit a learner who counts all four bond lines in CO2 as four carbon-centred domains. Replace the operation and show the corrected inventory.','There are two O neighbours and no C lone pair, so carbon has two local domains. Counting bond components as neighbours was the error.'),
      10:('For a supplied two-domain second-period centre with no central lone pair, reconstruct the introductory hybrid set size and unused p inventory.','An sp allocation has two hybrids and two residual p functions; four valence-basis functions are accounted for.'),
    }
    prompt,answer=cases[n]
    m['exit_task']['prompt']=prompt
    m['exit_task']['answer'].update(summary=answer,reasoning=[answer],check='Verify the local inventory and the declared model conditions independently of page orientation.')

def materialize(issue):
    directory=ROOT/f'evidence/blueprint-cycles/ISS{issue}/inputs'
    b=json.loads((directory/'owner.bank.json').read_text()); p=json.loads((directory/'package.v1.json').read_text())
    for n,q in enumerate(b['questions']):
        old=q['answer']['reasoning_route']; route=[]
        for i,(action,why,output) in enumerate(ROUTES[n],1):
            route.append({'id':q['id']+f'-MOVE-{i}','kind':('DECIDE','CONNECT','TRANSFORM','VERIFY')[i-1], 'action':action,'why_valid':why,'inputs':[q['stem'] if i==1 else route[-1]['output']], 'output':output})
        q['answer']['reasoning_route']=route
        q['answer']['crux_move_ref']=route[1]['id']
        r=q['extensions']['grade9v3:learning_repair']
        q['answer']['summary']=r['rule'];q['answer']['check']=r['check']; r['crux_move_ref']=route[1]['id']
    qs={q['id']:q for q in b['questions']}
    for m in p['microtopics']:
        for u in m['construction_units']:
            target=qs[u['bank_anchor_ref']]
            rows=target['answer']['reasoning_route']
            selected=[s for s in m['teaching_path'] if s['id'] in u['step_refs']]
            for i,s in enumerate(selected):
                row=rows[min(i,len(rows)-1)]
                s.update(action=row['action'],why_valid=row['why_valid'],output=row['output'])
            anchors=m['extensions'].get('grade9v3:lesson_anchors',{})
            if u['id'] in anchors:
                anchor=anchors[u['id']]
                r=target['extensions']['grade9v3:learning_repair']
                answer=r['pattern'].split(' Repeated')[0].split(' A recurring')[0].split(' Persistent')[0]
                anchor['answer'].update(summary=answer,reasoning=[r['connect'],answer,r['rule']],check=r['check'])
            u['crux_step_ref']=u['step_refs'][min(1,len(u['step_refs'])-1)]
        primary=qs[m['construction_units'][0]['bank_anchor_ref']]
        fresh_exit(m,primary)
        m['extensions']['grade9v3:question_repairs']=[q['extensions']['grade9v3:learning_repair'] for q in b['questions'] if q['extensions']['grade9v3:learning_repair']['microtopic_ref']==m['id']]
        if issue==32 and 'DOMAIN-COUNTING' in m['id']:
            m['inferential_jump']='Count distinct bonded neighbours and central lone pairs. A multiple bond is one local VSEPR domain; this rule does not put its pi density on the internuclear axis.'
    write(directory/'owner.bank.json',b);write(directory/'package.v1.json',p)
    print(f'ISS{issue}: ten explicit routes, unit warrants and fresh exits; source payload unchanged.')

if __name__=='__main__':
    import argparse
    a=argparse.ArgumentParser();a.add_argument('issue',type=int,choices=[32,31]);args=a.parse_args();materialize(args.issue)
