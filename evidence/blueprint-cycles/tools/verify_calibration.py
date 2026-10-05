"""Alternate exact checks of the eight author-created calibration solutions.

Finite sampling is labelled as sampling. The D4 conclusion additionally uses
explicit exhaustive parameter branches and the rational-root argument below.
Neither this script nor a render establishes independent difficulty acceptance.
"""
import hashlib, json
from fractions import Fraction as F
import os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
OUT=ROOT/os.environ.get('G9_REVIEW_DIR','evidence/blueprint-cycles/closure-20261005')/'matrix'
checks=[]
def record(cell,method,detail):checks.append({'cell':cell,'status':'PASS','method':method,'detail':detail})

# RETRIEVE D2: an alternate substitution check, rather than replaying the route.
assert 3*F(1)-4==1-2*F(1)
assert 3*F(0)-4!=1-2*F(0)
record('QRT-RETRIEVE-D2','EXACT_SUBSTITUTION_AND_NONZERO_COEFFICIENT','Coefficient difference is 5, so there is one rational solution; 0 refutes all-solutions.')

parameters={F(n,d) for n in range(-12,13) for d in range(1,6)}
samples={F(n,d) for n in range(-8,9) for d in range(1,5)}
for k in parameters:
    for x in samples:
        assert (2*(x-3)==2*x+k)==(k==-6)
        assert ((k-2)*x==4-2*k)==(k==2 or x==-2)
record('QRT-RETRIEVE-D3','EXACT_BRANCH_REDUCTION_PLUS_RATIONAL_SAMPLING',f'{len(parameters)} rational parameter values × {len(samples)} rational unknown values; identities reduce to −6=k and (k−2)(x+2)=0.')

# D4, k=2: invalid denominator; k=1: original equations admit x=0.
assert (F(1)-1)*(F(1)-2)*F(0)==F(1)-1
assert (F(0)+1)/(F(0)-1)==F(1)/(F(1)-2)
for k in parameters-{F(1),F(2)}:
    candidate=1/(k-2)
    if candidate!=1:
        assert (candidate+1)/(candidate-1)!=k/(k-2)
# Outside {1,2}, compatibility gives the monic integer polynomial k²−3k+1.
# Any rational root of this monic polynomial must be an integer dividing 1,
# hence ±1; neither is a root. Irrational k makes 1/(k−2) irrational: a
# nonzero rational reciprocal would imply k=2+1/x rational, a contradiction.
assert all(k*k-3*k+1!=0 for k in (F(-1),F(1)))
record('QRT-SYNTHESIZE-D4','EXHAUSTIVE_DOMAIN_BRANCHES_AND_RATIONAL_ROOT_ARGUMENT','k=2 invalid; k=1 admits x=0; other rational k fail compatibility; irrational k cannot produce a rational candidate. Sampling is an additional check, not the universal proof. Independent review rejected RETRIEVE primary ownership; its cell remains open.')

# APPLY D3: collapse the forward graph into a single expression as an
# independent computation, then compare with the stepwise authored route.
x=F(13,3);collapsed=(3*x+9)/10
assert collapsed==F(22,10)
assert (((x-1)/2)*3+4+2)/5==F(11,5)
assert (3*F(11,3)+9)/10==2
record('QRT-APPLY-D3','COLLAPSED_FORWARD_GRAPH_AND_EXACT_UNIT_CONVERSION','C=(3X+9)/10 cm; 22 mm=11/5 cm; X=13/3 cm reproduces the original observation.')

for a,b in [(F(1),F(0)),(F(-2),F(3)),(F(7,3),F(-5,2))]:
    assert a*(b/a)==b
record('QRT-MODEL-D1','NONZERO_COEFFICIENT_INVERSE','Nonzero A permits the reversible rule x=B/A; the identity rule requires A=B=0.')
row={'x':2,'y':3};point=(row['x'],row['y'])
assert point==(2,3) and point!=(row['y'],row['x'])
record('QRT-REPRESENT-D1','MEANING_PRESERVING_ROUND_TRIP','Reading the ordered pair back preserves x=2,y=3; a swap changes coordinate roles.')
forward=lambda x:2*(x+3)
for start in [F(-4),F(2),F(7,3)]:assert forward(start)/2-3==start
assert (forward(F(2))-3)/2!=2
record('QRT-SYNTHESIZE-D1','INVERSE_COMPOSITION_AND_COUNTERORDER','Halve then subtract undoes the forward dependency; subtract then halve fails on a changed input.')
assert 2*F(4)==8
assert 0*F(1)==0*F(2) and F(1)!=F(2)
record('QRT-JUSTIFY-D1','INVERSE_WARRANT_AND_ZERO_MULTIPLIER_COUNTEREXAMPLE','Dividing by nonzero 2 is defined and reversible; an identical zero-multiplication can enlarge the solution set.')

package=OUT/'package.v1.json'
report={'schema':'issue29-alternate-calibration-checks/v1','package_sha256':hashlib.sha256(package.read_bytes()).hexdigest(),'checks':checks,
 'status':'PASS','independent_reviewer':False,'classification_acceptance':'AUTHOR_ESTIMATE_REQUIRES_INDEPENDENT_CALIBRATION',
 'claim':'Alternate exact solution checks by the same author. No independent pedagogical verdict or mastery claim.'}
(OUT/'solution-checks.json').write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8',newline='\n')
print('Eight alternate exact solution checks PASS; classifications remain calibration candidates.')
