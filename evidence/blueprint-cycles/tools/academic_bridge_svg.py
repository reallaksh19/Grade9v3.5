"""Question-specific unfilled construction frameworks, never target answers.

Depth keys use a fictitious X centre to teach notation. Other diagrams expose
correspondences and blank ledgers; the original question's result stays unfilled.
"""
from html import escape

def text(x,y,s,size=20):
    return f'<text x="{x}" y="{y}" font-size="{size}">{escape(s)}</text>'

def table(headers,rows):
    width=740/len(headers); out=''
    for i,row in enumerate([headers]+rows):
        for j,s in enumerate(row):
            x=40+j*width;y=90+i*70
            out+=f'<rect x="{x}" y="{y}" width="{width}" height="70" fill="{"#dbeafe" if i==0 else "#fff"}" stroke="#64748b"/>'
            out+=text(x+10,y+40,s,18)
    return out+text(40,120+(len(rows)+1)*70,'Empty cells are learner work; no final model, count or label is supplied.',18)

def depth():
    return (text(40,100,'Notation key on fictitious centre X; this is not the target molecule.')+
        text(375,255,'X',28)+
        '<path d="M365 245L250 245 M395 245L510 245" stroke="#334155" stroke-width="3"/>'+
        '<path d="M380 235L350 135L410 135Z" fill="#334155"/>'+
        '<path d="M380 270L380 360" stroke="#334155" stroke-width="14" stroke-dasharray="2 9"/>'+
        text(200,220,'in page')+text(465,220,'in page')+text(430,150,'toward you')+
        text(430,355,'away from you')+text(40,435,'Use the key to construct your own target; preserve its given connections.'))

def plane():
    return (text(40,100,'Reference convention only; construct the target orbital correspondence.')+
        '<path d="M180 300L360 195L600 260L420 365Z" fill="#e0f2fe" stroke="#334155"/>'+
        '<path d="M390 390V130 M385 140L390 130L395 140" stroke="#2563eb" stroke-width="3"/>'+
        text(430,170,'normal to reference plane')+text(440,320,'reference plane')+
        text(40,435,'Target centres: [     ]     Direction correspondence: [                  ]'))

def axes():
    return (text(40,100,'Keep one reference fixed; fill the relative orientation in each frame.')+
        ''.join(f'<rect x="{x}" y="135" width="330" height="250" fill="#fff" stroke="#64748b"/>'+
            f'<path d="M{x+40} 330H{x+280} M{x+165} 350V175" stroke="#334155" stroke-width="3"/>'+
            text(x+20,420,label) for x,label in [(40,'Initial frame: [    ]'),(440,'Changed frame: [    ]')])+
        text(40,470,'Fixed axis: [             ]    Donor/terminal direction: [             ]'))

def pathway(names):
    out=text(40,100,'Map availability and adjacency without selecting a completed pathway.')
    step=740/len(names)
    for i,name in enumerate(names):
        x=40+i*step
        out+=f'<rect x="{x}" y="165" width="{step-15}" height="120" fill="#fff" stroke="#64748b"/>'
        out+=text(x+8,200,name,18)+text(x+8,245,'p: [     ]',18)
        if i<len(names)-1:out+=text(x+step-17,320,'↔',24)
    return out+text(40,390,'Link test: available direction? adjacent? aligned? Fill each link separately.')

SPECS={
 'D1':[
  (['Input s','Input p','Outputs','Set name'],[['[   ]','[   ]','[   ]','[   ]']]),
  (['Centre','Neighbours','Shared pairs'],[['H–Cl example','one each','one shared pair'],['HCHO C','[   ]','[   ]']]),
  (['Centre','Bonded sites','Lone pairs','Model'],[['CH4 C','[   ]','[   ]','[   ]']]),
  'depth',
  (['Candidate','Requested output','Scope fit'],[['VSEPR','domain arrangement','[   ]'],['Overlap','domain arrangement','[   ]']]),
  (['Sketch','Axis reference','Orientation','Bond type'],[['A','nucleus ↔ nucleus','[   ]','[   ]'],['B','nucleus ↔ nucleus','[   ]','[   ]']]),
  'depth',
  (['Atom','Own neighbours','Own lone pairs','Local total'],[['N in NF3','[   ]','[   ]','[   ]'],['One F','[   ]','[   ]','[   ]']]),
  (['Operation','Lines/pairs','Neighbour count'],[['Given wrong tally','from the stem','[   ]'],['Centre C','[   ]','[   ]']]),
  (['Species','Directions','s/p inputs','Outputs'],[['BF3','[   ]','[   ]','[   ]'],['CH4','[   ]','[   ]','[   ]']])],
 'D2':[
  (['Centre','Bonded sites','Lone pairs','Total'],[['BF3 B','[   ]','[   ]','[   ]'],['NH3 N','[   ]','[   ]','[   ]']]),
  (['Input basis','Hybrid allocation','Residual p'],[['one s + three p','[           ]','[           ]']]),
  'plane',
  (['Job','Carbon function','Orientation'],[['Sigma job 1','[          ]','[          ]'],['Sigma job 2','[          ]','[          ]'],['Remaining p','[          ]','[          ]']]),
  (['Centre','Bonds','Central lone pair','Claim test'],[['BF3 B','[   ]','[   ]','[   ]'],['NH3 N','[   ]','[   ]','[   ]']]),
  (['Case','C neighbours','Bond property','Local total'],[['CH4','[   ]','[   ]','[   ]'],['CH3F','[   ]','[   ]','[   ]']]),
  (['Centre','Domains','Sigma/pi jobs','Own lone pair'],[['HCN C','[   ]','[   ]','[   ]'],['HCN N','[   ]','[   ]','[   ]']]),
  (['Centre','Bonded sites','Lone pairs','Atom shape'],[['C','[   ]','[   ]','[   ]'],['N','[   ]','[   ]','[   ]']]),
  (['Partition','Hybrid functions','Residual p','Total'],[['sp','[   ]','[   ]','[   ]'],['sp2','[   ]','[   ]','[   ]'],['sp3','[   ]','[   ]','[   ]']]),
  (['Species','Given domains','Atom vertices','Shape'],[['CH4','four','[   ]','[   ]'],['NH3','four','[   ]','[   ]'],['H2O','four','[   ]','[   ]']])],
 'D3':[
  (['Description','Bond prediction','Given equivalence'],[['Permanent one double','[          ]','compare stem'],['Contributor set','[          ]','compare stem']]),
  (['Centre','Sigma/LP ledger','Perpendicular p','Pi electrons'],[['N','[   ]','[   ]','[   ]'],['Each O','[   ]','[   ]','[   ]']]),
  (['Site','Sigma jobs','Basis allocation','Residual dirs'],[['Terminal 1','[   ]','[   ]','[   ]'],['Central C','[   ]','[   ]','[   ]'],['Terminal 2','[   ]','[   ]','[   ]']]),
  'axes',
  (['Claim','Given case','What follows','Limit'],[['Equivalence','CO2','[   ]','[   ]'],['Local domains','NH3','[   ]','[   ]']]),
  (['Bond/location','Shared pairs','Sigma','Pi'],[['Each C–H','[   ]','[   ]','[   ]'],['Each C–C','[   ]','[   ]','[   ]']]),
  (['Centre','Sigma/LP ledger','Perpendicular p','Pi electrons'],[['C','[   ]','[   ]','[   ]'],['Each O','[   ]','[   ]','[   ]']]),
  'axes',
  ['C1','C2','C3','C4','C5'],
  (['Species/site','Local inventory','Residual job','Boundary'],[['Allene sites','[   ]','[   ]','[   ]'],['Propyne sites','[   ]','[   ]','[   ]']])],
 'D4':[
  (['Account','Local count','Availability','Alignment'],[['Lewis N','[   ]','[   ]','[   ]'],['Adjacent C=O','[   ]','[   ]','[   ]']]),
  'axes','axes',
  (['Case','Availability','Adjacency','Alignment'],[['Direct amide','[   ]','[   ]','[   ]'],['Spacer amine','[   ]','[   ]','[   ]']]),
  (['Observation','Common label','Different output','Inference limit'],[['Given angles','from stem','[   ]','[   ]'],['Given amide','from stem','[   ]','[   ]']]),
  (['Site','Local rule','Conditions met?','Boundary'],[['Amide N','[   ]','[   ]','[   ]'],['Spacer N','[   ]','[   ]','[   ]']]),
  (['Species','Sigma ledger','Perpendicular occupancy'],[['CH3 radical','[   ]','[   ]'],['CH3 cation','[   ]','[   ]']]),
  (['Observation','Prediction A','Prediction B','What is limited'],[['Geometry','[   ]','[   ]','[   ]'],['Response to twist','[   ]','[   ]','[   ]']]),
  (['Theta','Given cos factor','Other contributions','Total claim'],[['0 degrees','[   ]','[   ]','[   ]'],['60 degrees','[   ]','[   ]','[   ]'],['90 degrees','[   ]','[   ]','[   ]']]),
  (['Case','Count','Occupancy/alignment','Qualified rule'],[['NH3 / allene','[   ]','[   ]','[   ]'],['Amide / spacer','[   ]','[   ]','[   ]']])]
}

def framework(band,index):
    s=SPECS[band][index]
    if s=='depth':return depth()
    if s=='plane':return plane()
    if s=='axes':return axes()
    if isinstance(s,list):return pathway(s)
    return table(*s)

def matrix_framework(demand,band):
    if (demand,band)==('RETRIEVE','D2'):
        return table(['Side','Variable term','Constant','Reduced A/B'],[['Left','3x','−4','[   ]'],['Right','−2x','+1','[   ]']])
    if (demand,band)==('RETRIEVE','D3'):
        return table(['Fixed k; vary x','Coefficient A','Constant B','A=0 / A≠0'],[['E1','[   ]','[   ]','[   ]'],['E2','[   ]','[   ]','[   ]']])
    if band=='D4':
        return table(['Requirement','Candidate set','Intersection'],[['Equation 1','[                ]','[                ]'],['Equation 2','[                ]','[                ]'],['x rational; x≠1','k≠2','[                ]']])
    if demand=='APPLY':
        return table(['Record','Value / unit','Process','Inverse input'],[['Observation C','22 mm','program uses cm','[   ]'],['Program','same-unit readings','X → A → B → C','[   ]'],['Unit reference','10 mm = 1 cm','same-unit stages','[   ]']])
    if demand=='MODEL':
        return table(['Generic branch','Operation condition','Select R1/R2'],[['A≠0','division reversible','[   ]'],['A=0','inspect constant','[   ]']])
    if demand=='REPRESENT':
        return (text(40,100,'Coordinate roles: horizontal x; vertical y. Place the requested point yourself.')+
           '<path d="M130 390H700 M160 450V145" stroke="#334155" stroke-width="3"/>'+
           text(705,395,'x')+text(165,140,'y')+text(300,470,'Ordered pair: (horizontal [   ], vertical [   ])'))
    if demand=='SYNTHESIZE':
        return table(['Dependency','Forward input','Forward output','Inverse order'],[['add 3','start','intermediate','[   ]'],['double','intermediate','final','[   ]']])
    return table(['Operation','Inverse/defined?','Solution set','Warrant'],[['Nonzero scale','[   ]','[   ]','[   ]'],['Zero multiplier','many values → 0','[   ]','[   ]']])
