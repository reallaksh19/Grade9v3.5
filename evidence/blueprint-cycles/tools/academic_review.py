"""Record bounded author judgements separately from independent facet acceptance."""
import hashlib,json,subprocess
from pathlib import Path
from fractions import Fraction as F
ROOT=Path(__file__).resolve().parents[3];BASE=ROOT/'evidence/blueprint-cycles';OUT=BASE/'closure-r4-20261005'
def read(p):return json.loads(p.read_text())
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def save(name,obj):(OUT/name).write_text(json.dumps(obj,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
# These are actual content judgements, not inferred from successful rendering.
# Advanced conclusions are bounded to the supplied introductory local models.
REASONS={
 'D1':[
  'The set has four functions from one valence s and three p inputs; the superscript counts p inputs, not all outputs.',
  'HCHO carbon has three neighbour directions; the C=O has one sigma and one pi component.',
  'Four CH4 neighbour domains support the introductory tetrahedral/sp3 account; the flat connectivity sketch does not measure shape.',
  'NH3 must retain three H atoms and one central lone pair when depth notation is added.',
  'The requested domain arrangement warrants VSEPR scope; orbital overlap is a different requested output.',
  'End-on and side-on orientations are relative to the internuclear axis, independent of whole-page rotation.',
  'A Lewis cross records connectivity; the learner must supply an explicit depth convention rather than infer page angles.',
  'NF3 nitrogen has three neighbour directions and its own lone pair. Fluorine lone pairs belong to fluorine.',
  'HCHO carbon has three neighbour directions; counting the double-bond lines as two neighbours repeats the wrong operation.',
  'BF3 and CH4 have three and four local directions and three and four hybrid functions in their introductory models.'
 ],
 'D2':[
  'BF3 and NH3 share three bonds but differ by the central lone pair: three versus four local domains.',
  'HCHO carbon allocates three sp2 hybrids and one residual p; the same p input cannot also remain unhybridized.',
  'Ethene needs parallel residual p directions perpendicular to each local sigma plane, rather than a privileged page orientation.',
  'CO2 carbon uses two axial hybrid functions and two residual p functions. This local basis count does not prove a unique terminal-oxygen physical basis.',
  'NH3 refutes three-sigma-implies-sp2 because the central lone pair changes the inventory.',
  'Replacing a bonded H by F does not add another carbon-centred direction beyond its bond.',
  'HCN has two domains at each selected centre; four shared pairs plus the N lone pair account for ten valence electrons.',
  'Methylamine requires separate C and N inventories; four total domains need not give the same nuclear shape.',
  'One s and three p inputs yield four basis functions in every partition; residual p counts for sp/sp2/sp3 are two/one/zero.',
  'CH4/NH3/H2O have four introductory domains but four/three/two bonded nuclei, yielding different atom-only shapes.'
 ],
 'D3':[
  'A permanent unique nitrate double-bond position conflicts with supplied equivalence; contributors are electron bookkeeping, not switching nuclear structures.',
  'The supplied nitrate contributors allocate four perpendicular p functions and six pi-space electrons, including terminal perpendicular lone-pair contributions.',
  'The declared allene local model retains two perpendicular central p directions, constraining perpendicular terminal sigma planes.',
  'The connected allene account is an alignment construction. Pauli limits state occupancy, not all multicentre use of a basis function; no universal zero integral is proved.',
  'CO2 and NH3 counterexamples separate bond equivalence from the local-domain criterion for a hybrid label.',
  'Propyne has six sigma and two pi components; multiple bond lines do not each contribute another sigma.',
  'Carbonate has four p functions/six pi-space electrons in this bookkeeping model. Formal charge averaging is not a measurement of atomic partial charge.',
  'Holding the central sigma axis fixed does not hold every neighbouring interaction fixed during a relative group rotation.',
  'Butadiene has a contiguous introductory p pathway; the saturated carbon in pentadiene interrupts that pathway. This does not assert every quantum interaction is zero.',
  'The procedure is atom-local; allene and propyne cannot each be assigned one whole-molecule hybrid label.'
 ],
 'D4':[
  'Formamide local Lewis counting must be reconciled with the supplied adjacent donation/alignment conditions rather than mechanically choosing a localized amine basis.',
  'CH3NO retains eighteen valence and twenty-four total electrons under torsion; only relative geometry changes.',
  'A hybrid label alone is not a mechanism for a donation or barrier trend; the supplied alignment trend needs explicit model limits.',
  'The saturated spacer changes orbital-connected adjacency; folding spatially closer does not remove the intervening saturated centre.',
  'The supplied methane/ammonia/water angle differences and amide case refute a unique label-to-angle or unique observed-geometry-to-basis inference.',
  'Retrieval of a local rule does not establish its applicability to supplied delocalisation conditions.',
  'Under the supplied planar model CH3 radical has one residual unpaired electron whereas CH3+ has none; three sigma bonds alone do not fix occupancy.',
  'Geometry can help discriminate descriptions but alone does not numerically measure donation strength or a rotational barrier.',
  'The given cosine factor is one variable, not a universal total-energy law. A specified two-level toy gives a different dependence and does not predict a real barrier.',
  'Local count is a useful first ledger; occupancy, residual directions, adjacency/alignment and the requested explanatory job remain separate checks.'
 ]}
rows=[]
for issue in (32,31,34,33,36,35,38,37):
    folder=BASE/f'ISS{issue}';bank=read(folder/'inputs/owner.bank.json');band=f'D{(issue-31)//2+1}'
    for n,q in enumerate(bank['questions']):
        rows.append({'question_ref':q['id'],'issue':issue,'source_item':q['original_identifier'],
         'scope':'AUTHOR_ANSWER_AND_SUPPORT_REVIEW_NOT_COMPLETE_INDEPENDENT_HSPM_VERDICTS',
         'answer_judgement':REASONS[band][n],
         'support_judgement':{'given_visual':q['extensions']['grade9v3:core2_visual_review'],
          'preserved_decision':q['scaffolds'][2]['text'] if 'text' in q['scaffolds'][2] else q['scaffolds'][2],
          'diagnostic_scope':'Probe and expected pattern read together against the named wrong idea; repeated pattern is suggestive, never a diagnosis from one response.'},
         'hashes':{name:sha(folder/name) for name in ('inputs/owner.bank.json','inputs/package.v1.json','rendered/core1a.html','rendered/core2.html')},
         'independent_acceptance':'NOT_RUN'})
save('academic-review.json',{'basis':subprocess.check_output(['git','rev-parse','HEAD'],text=True,cwd=ROOT).strip(),
 'rows':rows,'distinct_answer_judgements':40,'instance_bindings':80,'independent_facets_accepted':0,
 'limits':['These bounded author judgements do not constitute 960 independent facet verdicts.','Classification disagreements remain unresolved author estimates.','Supplied conditions and local-model deductions are not empirical proof of a unique orbital basis.']})
matrix=read(OUT/'matrix/calibration-ledger.json')
classification=[]
for specimen in matrix['specimens']:
    disputed=specimen['qrt_id']=='QRT-RETRIEVE-D4'
    classification.append({'id':specimen['id'],'cell':specimen['qrt_id'],'status':'AUTHOR_CONTESTED' if disputed else 'AUTHOR_PROVISIONAL',
     'reason':('The terminal requested output is a category, but the decisive compatibility proof coordinates rational-domain restrictions and newly derives a quadratic. Whether RETRIEVE should own this rather than SYNTHESIZE/JUSTIFY requires independent adjudication; its label does not close the cell.' if disputed else specimen['classification_rationale']),
     'five_components':specimen['five_components'],'independent_acceptance':'NOT_RUN'})
save('matrix-classification-review.json',{'specimens':classification,'candidate_identity_union':28,'independently_accepted_union':0,'contested':['QRT-RETRIEVE-D4']})
# Alternate counterexamples/branches for the repaired candidate mathematics rules.
assert 2*F('0.5')==1
assert 3*F('0.333')-1==F(-1,1000)
for y in (F(-2),F(0),F(7,3)):assert 1*F(2)+0*y-2==0
for x in (F(-2),F(0),F(7,3)):assert 0*x+1*F(3)-3==0
save('mathematics-proof-review.json',{'author_review':'NOT_INDEPENDENT_ACCEPTANCE',
 'claims':[
  {'claim':'A single zero coefficient still defines a real-plane line.','proof':'For b=0, a!=0: x=-c/a, y arbitrary. For b!=0: y=-(a/b)x-c/b, x arbitrary. Both zero gives an identity or contradiction, not a line.'},
  {'claim':'Decimal notation alone does not introduce a residual.','proof':'For a!=0 and exact solution s, residual at q is a(q-s). Thus q=s has zero residual even in terminating-decimal notation; 0.333 in 3x=1 gives -1/1000.'},
  {'claim':'Reversible operations preserve the declared domain solution set.','proof':'Adding/subtracting the same defined term has an inverse; multiplication/division by a nonzero constant has an inverse. Multiplication by zero lacks this property.'},
  {'claim':'An identity admits precisely the declared admissible domain.','proof':'After reversible reduction, the constant true equality holds for every admissible x; a false equality holds for none. Changing Q to R changes the domain, not the equality.'},
  {'claim':'The denominator-clearing rule here is bounded to nonzero constant integer denominators.','proof':'Their positive LCM is nonzero, so multiplication has an inverse; variable denominators require additional domain restrictions outside this rule.'}],
 'primary_reference':'https://openstax.org/books/elementary-algebra-2e/pages/4-1-use-the-rectangular-coordinate-system',
 'other_reference':'https://openstax.org/books/elementary-algebra-2e/pages/2-4-use-a-general-strategy-to-solve-linear-equations',
 'retrieval_limit':'NCERT PDF retrieval timed out. No new claim of authenticated NCERT wording, current board mapping, or source acceptance.'})
print('40 bounded answer judgements / 80 exact instance bindings; eight provisional/contested matrix reviews; five algebraic boundary proofs recorded. Independent 960-facet acceptance remains NOT_RUN.')
