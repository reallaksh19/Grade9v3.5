"""Complete the teaching side of each cumulative repair, including changed exits."""
import argparse,json
from pathlib import Path
from close_d1 import move,write
ROOT=Path(__file__).resolve().parents[3]
D1_STEPS={
'DOMAIN-COUNTING':[
move('Count distinct bonded neighbours at the chosen centre.','A multiple bond supplies one local VSEPR domain; sigma and pi density are not spatially identical.','HCHO carbon: two H neighbours and one O neighbour = three bonding domains.'),
move('Assign each lone pair to its atom before adding it.','Only a lone pair centred on the selected atom enters its local count.','NF3 nitrogen: three N-F directions + one N lone pair = four; F lone pairs are excluded.'),
move('Test neighbour counting against bond-component counting.','HCHO has a C=O sigma and pi component to one O; HCN has one sigma and two pi components to one N.','HCHO carbon has three domains; HCN carbon two. Shared-pair multiplicity does not add neighbours.')],
'HYBRID-ORBITAL-MAPPING':[
move('Allocate the local second-period valence basis.','One 2s and three 2p functions supply four independent inputs; an introductory basis change preserves dimension.','sp: two hybrids + two p; sp2: three hybrids + one p; sp3: four hybrids + zero p.'),
move('Match the supplied ideal local domain model without turning a label into proof.','CH4 has four C neighbours and no C lone pair; the known four-domain rule supplies a tetrahedral/sp3 description.','Four sigma-direction hybrids in the chosen model, without a uniquely measured orbital decomposition.'),
move('Separate sigma and pi jobs by the declared internuclear axis.','Axial overlap describes sigma; lateral p overlap with a nodal plane containing the axis describes pi.','Rigidly turning a drawing does not change its overlap class; relative orbital orientation matters.')],
'3D-REPRESENTATION-MODELS':[
move('Preserve connectivity and declare depth conventions.','A Lewis drawing records bonded atom pairs, not all physical page angles.','Four-domain CH4: four H endpoints; NH3: three H and one lone-pair domain.'),
move('Construct the domain directions and then name the bonded-nucleus shape.','A solid wedge denotes toward, a hashed wedge away and ordinary lines the page plane; lone pairs are domains without atomic vertices.','CH4 has tetrahedral nuclear shape; NH3 has tetrahedral domains and a pyramidal nuclear shape.'),
move('Choose the model by its requested output and limits.','VSEPR describes qualitative domain arrangement; detailed overlap orientation or wavefunctions require an orbital account.','Do not infer exact experimental angles or orbital coefficients from a qualitative domain sketch.')],
}
EXIT={
(34,'DOMAINS'):('Given OF2 with two O-F bonds and two O lone pairs, classify the domain arrangement and bonded-nucleus shape at O. Explain why terminal-F lone pairs are excluded.','Four O domains; introductory tetrahedral domain arrangement and bent nuclear shape. F lone pairs are F-centred.'),
(34,'MULTIPLE'):('For H-C≡C-H, inventory domains and residual p functions at each C, then count sigma and pi components in the entire molecule. Close the valence-electron ledger.','Each C has two directions: sp with two residual p functions. Whole molecule: three sigma plus two pi pairs, using 2*4+2=10 valence electrons.'),
(33,'DOMAIN-FIRST'):('Count C-centred domains in CH2Cl2 and separately count all attached atoms. State which bond properties this inventory cannot determine.','Four C-neighbour domains; no C lone pair. It determines neither equality of bond lengths nor exact angles.'),
(33,'ORBITAL-INVENTORY'):('For H-C≡C-H, account for each carbon valence basis and the whole-molecule sigma/pi inventory without reusing a p function.','At each C: two sp hybrids plus two residual p functions. Whole molecule: three sigma and two pi components; each local basis totals four.'),
(33,'DOMAIN-VS'):('Given OF2 with two O-F bonds and two O lone pairs, sketch the four domain directions and distinguish its atom-only shape from the domain arrangement.','Four domains, two bonded F nuclei: tetrahedral domain model and bent nuclear shape. Exactly two F endpoints.'),
(35,'DELOCALISATION'):('A hypothetical anion has two equivalent terminal bonds and two formal contributors sharing one atomic skeleton and total charge. Explain which quantities remain invariant and what extra information you need to count pi-space electrons.','Nuclei, connectivity and total charge/electron count remain invariant. Contributors are bookkeeping alternatives. The occupied participating orbitals/electron ledger must be supplied before assigning a pi-space electron total.'),
(35,'PI-ORIENTATION'):('Number carbons in CH3-CH=C=CH2. Assign local introductory models and relate the terminal sigma planes of its cumulated double-bond triad.','In written order: sp3, sp2, sp, sp2. The terminal sigma planes of C2=C3=C4 are perpendicular in this model because central C3 retains two perpendicular p functions.'),
(35,'LOCAL-PROCEDURE'):('Apply your atom-local procedure to approximately planar CH2=CH-CH=CH2. Account for the local carbon bases and identify the contiguous p pathway. State what this model alone cannot predict.','All four carbons have three sigma directions and sp2-like accounting, each retaining one p. Four contiguous aligned p sites support the ordinary delocalised pathway. Exact energies and unique physical hybrid coefficients remain undetermined.'),
(37,'MODEL-SCOPE'):('For the supplied g(theta)=cos(theta) toy factor, compute g(120 degrees). Does its negative value determine a negative total molecular energy or a unique energy change? Give a counterexample family.','g(120)=-1/2. No total energy follows from the factor. For the explicitly invented family E=-g^2+c, different values of c give different energies at the same angle; this is a counterexample, not a physical amide energy law.'),
}

def finish(issue):
    directory=ROOT/f'evidence/blueprint-cycles/ISS{issue}/inputs'
    b=json.loads((directory/'owner.bank.json').read_text());p=json.loads((directory/'package.v1.json').read_text());qs={q['id']:q for q in b['questions']}
    for m in p['microtopics']:
        if issue==32:
            spec=next(rows for key,rows in D1_STEPS.items() if key in m['id'])
            for row,step in zip(spec,m['teaching_path']):step.update(action=row[0],why_valid=row[1],output=row[2])
        for u in m['construction_units']:
            anchor=m['extensions'].get('grade9v3:lesson_anchors',{}).get(u['id'])
            if anchor:
                target=qs[anchor['target_question_ref']];r=target['extensions']['grade9v3:learning_repair']
                anchor['target_crux_move_ref']=target['answer']['crux_move_ref']
                result=r['pattern'].split(' Repeated')[0].split(' A repeated')[0].split(' Persistent')[0].split(' A recurring')[0]
                anchor['answer'].update(summary=result,reasoning=[r['connect'],result,r['rule']],check=r['check'])
        primary=qs[m['construction_units'][0]['bank_anchor_ref']]
        m['inferential_jump']=primary['extensions']['grade9v3:learning_repair']['rule']
        for (n,key),(prompt,answer) in EXIT.items():
            if n==issue and key in m['id']:
                m['exit_task']['prompt']=prompt
                m['exit_task']['answer'].update(summary=answer,reasoning=[answer],check='Rebuild the atom-local and electron/basis ledgers; separate model outputs from unprovided physical quantities.')
        # A retained exit already differs from the worked anchor only when it asks a changed case.
        for u in m['construction_units']:
            anchor=m['extensions'].get('grade9v3:lesson_anchors',{}).get(u['id'])
            if anchor and m['exit_task']['prompt']==anchor['stem']:raise ValueError('exit repeats worked prompt')
    write(directory/'package.v1.json',p)
    print(f'ISS{issue}: teaching bindings and fresh exits reconciled.')

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('issue',type=int,choices=range(31,39));finish(a.parse_args().issue)
