"""Reference-grounded candidate repairs; never upgrade question/source status."""
import copy, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def save(path,value):
    path.write_text(json.dumps(value,indent=2,ensure_ascii=False)+'\n',encoding='utf-8',newline='\n')
p=ROOT/'Mathematics/library/linear-equations.v1.json'
library=json.loads(p.read_text());g=ROOT/'Mathematics/gates/linear-equations.v1.json';registry=json.loads(g.read_text())
relations={r['id']:r for r in library['relations']}
prefix='REL-MAT-LEQ-'
changes={
 'REL-MATH-EXACTNESS':{
  'meaning':'For a nonzero linear coefficient, the residual is a times the error in the candidate value. An exact terminating decimal is an exact rational too; only a changed value introduces a nonzero residual.',
  'conditions':['The linear coefficient a is non-zero and all arithmetic is exact over the rationals.','The decimal approximation differs numerically from the exact solution.','Rounding is a presentation choice made after the mathematics, never during it.'],
  'checks':['For 2x = 1, x = 0.5 is exact and has zero residual; for 3x = 1, x = 0.333 has residual -0.001.'],
 },
 prefix+'03-REDUCTION':{
  'conditions':list(dict.fromkeys(relations[prefix+'03-REDUCTION']['conditions']+['Denominators are non-zero constant integers; the domain is declared before clearing them.'])),
 },
 prefix+'03-REDUCED-OUTCOMES':{
  'meaning':'After reversible reduction, a false constant equality has no admissible solutions; a true constant equality admits every value in the declared domain.',
  'conditions':list(dict.fromkeys(relations[prefix+'03-REDUCED-OUTCOMES']['conditions']+['Every reduction preserves the original admissible domain and solution set.'])),
  'limits':['An identity admits every value of the declared domain, which need not be all real numbers.'],
 },
 prefix+'04-TWO-VARIABLE-FORM':{
  'expression':'ax + by + c = 0, where a, b, c are real numbers and a and b are not both zero; a solution is a pair (x₀, y₀) with ax₀ + by₀ + c = 0',
  'conditions':['a and b are not both zero; either individual coefficient may be zero.','a, b and c are real numbers.','The graph claim uses the real Cartesian plane and ordered real pairs.'],
  'checks':['If b = 0 and a != 0, x = -c/a with arbitrary real y is a vertical line.','If a = 0 and b != 0, y = -c/b with arbitrary real x is a horizontal line.','If a = b = 0, the constant equality is either the entire plane or empty, not a line.'],
 },
 prefix+'04-STRAIGHT-LINE':{
  'meaning':'The form y = ax + b describes every nonvertical line in the real Cartesian plane, including horizontal lines with a = 0. A vertical line x = k has no slope in this form.',
  'conditions':['x and y are real coordinates in the Cartesian plane.','The line is nonvertical; the coefficient of y in the general form is non-zero.','The letters a and b here name slope and constant; they differ from the a and b of ax + by + c = 0.'],
 },
}
for rid,fields in changes.items():
    r=relations[rid];ext=r['extensions']
    ext.setdefault('grade9v3:academic_revision',{'previous':{key:copy.deepcopy(r.get(key)) for key in fields},'status':'AUTHOR_REVIEW_NOT_INDEPENDENT_ACCEPTANCE'})
    r.update(fields);r['version']='0.2.0'
    # The old evidence mapping must not silently certify corrected statements.
    old=ext.pop('grade9v3:citations',None)
    if old:ext['grade9v3:academic_revision']['previous_citations']=old
    ext['grade9v3:academic_revision']['basis']='OpenStax Elementary Algebra 2e sections 2.4 and 4.1, with the explicit algebraic counterexamples in the R4 review report.'
exact=relations['REL-MATH-EXACTNESS']
exact['derivation'][1].update(action='Substitute a decimal value different from the exact solution and subtract the two sides.',why_valid='The residual a*(approximation - exact solution) is nonzero when a and the difference are nonzero.',output='A non-zero difference only when the candidate value has changed.')
r=relations[prefix+'04-TWO-VARIABLE-FORM']
next(s for s in r['symbols'] if s['symbol']=='a, b')['unit_or_domain']='real numbers, not both zero'
r['derivation'][-1].update(action='Split the general claim by whether b is zero.',why_valid='For b != 0 solve y for each x; otherwise a != 0 fixes x and leaves y arbitrary.',output='A nonvertical or vertical straight line with infinitely many real pairs.')
for gate in registry['gates']:
    for row in gate['relations']:
        if row['relation_id']=='REL-EQ-EXACT-VERIFICATION':
            row.update(meaning=exact['meaning'],conditions=exact['conditions'])
            gate['canonical_concepts'][1]['statement']='A decimal approximation that changes the exact rational value is a different number; an exact terminating decimal is another notation for the same rational.'
            gate['reasoning_sequence'][-1].update(action='Compare an exact terminating decimal with a numerically changed approximation.',why_valid='Notation alone changes no value; a changed value has residual a times its error.')
            for item in gate['misconceptions']:
                # Existing exact-fraction teaching remains valid; narrow blanket claims.
                for key,value in item.items():
                    if isinstance(value,str):item[key]=value.replace('every truncated decimal','a decimal approximation that changes the exact value')
newgate=copy.deepcopy(registry['gates'][0])
newgate.update(gate_id='MATH-EQ-CANDIDATE-EXTENDED-RELATIONS',title='Declared-domain equality operations and real-plane line boundaries',
 canonical_concepts=[{'concept_id':'CON-EQ-DOMAIN-AND-LINE-BOUNDARIES','statement':'Reversible operations preserve the declared solution set; real-plane line equations include either single zero coefficient but exclude both zero.'}],
 relations=[{'relation_id':r['gate_relation_ref'],'expression':r['expression'],'meaning':r['meaning'],
             'symbols':[{'symbol':s['symbol'],'meaning':s['meaning'],'domain':s['unit_or_domain']} for s in r['symbols']],
             'conditions':r['conditions']} for r in library['relations'] if r['id'].startswith(prefix)],
 representations=[],transformations=[],
 misconceptions=[{'misconception_id':'MIS-EQ-SINGLE-ZERO-EXCLUDES-LINE','wrong_idea':'Either zero coefficient prevents a real-plane line.','counterexample':'x = 2 has a = 1, b = 0 and is a vertical line; y = 3 is horizontal.','repair':'Exclude both zero together, then divide by whichever coefficient is nonzero.'}],
 problem_families=[{'family_id':'FAM-EQ-DECLARED-DOMAIN-IDENTITY','title':'Distinguish the declared-domain identity from a contradiction','hidden_invariants':['Only reversible operations preserve all admissible solutions.']}],
 falsification_cases=[{'case_id':'FAL-EQ-EXTENDED-PRESCRIBED-NO-BINDING','mutation':'Change scope_class to PRESCRIBED with no curriculum binding.','expected_report':'held_insufficient_authority'}],
 validity_conditions=['Use each relation only under its own explicitly declared domain and conditions.'],
 reasoning_sequence=[{'step_id':'RS-EQ-CHECK-BOUNDARIES','sequence':1,'action':'Declare the domain, apply reversible operations, and check zero-coefficient branches.','why_valid':'Inverse operations preserve equality; the two line branches follow by division by whichever coefficient is nonzero.'}])
registry['gates']=[a for a in registry['gates'] if a['gate_id']!=newgate['gate_id']]+[newgate]
registry['provenance']['scope']='Candidate one-variable rational equality gates and explicitly real-plane two-variable relations. No independent acceptance or full Mathematics coverage.'
library['version']='0.2.0'
for m in library['microtopics']:
    for step in m.get('teaching_path',[]):
        if step.get('action')=='Write the equation in the form ax + by + c = 0 and check that a and b are both non-zero.':
            step.update(action='Write the equation in the form ax + by + c = 0 and check that a and b are not both zero.',why_valid='Either individual coefficient may be zero. Both zero would yield an entire-plane identity or empty contradiction rather than a line.')
    if m['id']=='MIC-MAT-LEQ-04-TWO-VARIABLES-LINE-OF-SOLUTIONS':
        m['research_contribution']='Authored line-boundary repair grounded in OpenStax Elementary Algebra 2e section 4.1: either single zero coefficient is allowed. Original source/evidence cards remain separately attributable; no board or source acceptance follows.'
save(p,library);save(g,registry)
print('Six missing candidate relation bindings repaired; zero-coefficient, domain, denominator and exact-decimal claims corrected. Source questions/statuses unchanged.')
