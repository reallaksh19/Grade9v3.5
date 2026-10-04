"""Render explicit diagnosis/repair records without grading or fabricating mastery.

Namespaced extensions carry authored pedagogy; canonical question wording is untouched.
"""
from html import escape

KEY = 'grade9v3:learning_repair'
FIELDS = ('clarify', 'connect', 'way', 'rule', 'check', 'probe', 'pattern', 'transfer', 'wrong_idea')

def problems(record, unit_ids):
    repair = (record.get('extensions') or {}).get(KEY)
    if not isinstance(repair, dict):
        return ['learning repair is absent']
    found = [f'{name} is absent' for name in FIELDS if not isinstance(repair.get(name), str) or not repair[name].strip()]
    if repair.get('construction_ref') not in unit_ids:
        found.append('construction_ref does not resolve to a construction unit')
    if not repair.get('question_ref') == record.get('id'):
        found.append('question_ref does not name the reviewed question')
    answer=record.get('answer') or {}
    moves={m.get('id') for m in answer.get('reasoning_route') or []}
    if repair.get('crux_move_ref') != answer.get('crux_move_ref') or repair.get('crux_move_ref') not in moves:
        found.append('crux_move_ref does not resolve to this question crux')
    if repair.get('interaction') not in (None,'MODEL_SCOPE_PROBE'):
        found.append('interaction is not supported')
    return found

def card(repair, question_id, role='CORE2'):
    e = lambda value: escape(str(value), quote=True)
    prefix = f'{role}-probe-{question_id}'
    href = ('core1a.html#repair-' + question_id) if role == 'CORE2' else ('core2.html#' + question_id)
    link = 'Open the exact repair' if role == 'CORE2' else 'Return to the question'
    return (
        f'<section data-g9-learning-repair="{e(question_id)}" class="g9-repair-probe">'
        '<h4>Test the rule on a changed case</h4>'
        f'<p>{e(repair["probe"])}</p>'
        f'<label for="{e(prefix)}">Your prediction and reason</label>'
        f'<textarea id="{e(prefix)}" data-g9-probe-response rows="3"></textarea>'
        '<button type="button" data-g9-probe-compare>Commit this reasoning and compare</button>'
        '<p data-g9-probe-message role="status" aria-live="polite"></p>'
        '<div data-g9-probe-feedback hidden>'
        f'<p><strong>Expected pattern:</strong> {e(repair["pattern"])}</p>'
        '<p>This pattern suggests a rule to revisit; it does not diagnose you or certify mastery.</p>'
        f'<p><strong>Replacement rule:</strong> {e(repair["rule"])}</p>'
        f'<p><strong>Fresh application:</strong> {e(repair["transfer"])}</p>'
        + (alignment_probe(prefix) if repair.get('interaction') == 'MODEL_SCOPE_PROBE' else '')
        +
        f'<a href="{e(href)}" data-g9-repair-link>{link}</a>'
        '</div></section>'
    )

def alignment_probe(prefix):
    """End-on projection: rotating a donor direction corresponds to rotation about C-N.

    The toy energy family demonstrates non-uniqueness; it is never a formamide calculation.
    """
    p=escape(prefix,quote=True)
    return (f'<section data-g9-alignment-probe><h4>Keep alignment separate from total energy</h4>'
      '<p>Look along the fixed C-N axis. The two centres project to the same origin. '
      'The solid donor direction turns relative to the dashed carbonyl direction. '
      'This is a direction diagram, not a measured orbital or overlap integral.</p>'
      f'<label for="{p}-theta">Relative angle θ (degrees)</label><input id="{p}-theta" data-g9-theta type="range" min="0" max="90" step="15" value="0">'
      f'<label for="{p}-other">Independent toy energy contribution c</label><input id="{p}-other" data-g9-other type="range" min="-2" max="2" step="0.5" value="0">'
      '<svg viewBox="0 0 360 360" role="img" aria-label="End-on relative p direction comparator">'
      '<title>Relative directions about a fixed C-N axis</title><desc>Dashed acceptor direction is fixed; solid donor direction rotates about the projected bond axis.</desc>'
      '<line x1="180" y1="55" x2="180" y2="305" stroke="currentColor" stroke-width="3" stroke-dasharray="8 6"/>'
      '<g data-g9-donor><line x1="180" y1="75" x2="180" y2="285" stroke="currentColor" stroke-width="7"/>'
      '<ellipse cx="180" cy="115" rx="25" ry="40" fill="none" stroke="currentColor" stroke-width="3"/>'
      '<ellipse cx="180" cy="245" rx="25" ry="40" fill="none" stroke="currentColor" stroke-width="3"/></g>'
      '<circle cx="180" cy="180" r="8" fill="currentColor"/><text x="15" y="340" font-size="18">Axis points towards/away from viewer.</text></svg>'
      '<p data-g9-alignment-output role="status" aria-live="polite">θ = 0°; given factor = 1; toy E = -1.</p>'
      '<p>Declared demonstration only: g = cos(θ); E = -g² + c in arbitrary toy units. '
      'The square is an explicitly chosen example, not a universal law. Hold θ fixed and vary c: '
      'the same g permits different E. Predict this before moving c. No physical barrier is computed.</p>'
      '<noscript>Static cases: θ=0°,60°,90° gives g=1,1/2,0. At θ=60°, c=0 gives E=-1/4; '
      'c=1 gives E=3/4. Same overlap factor, different toy total.</noscript></section>')

def clinic(rows):
    out = []
    for row in rows:
        qid = row['question_ref']
        out.append(f'<section id="repair-{escape(qid, quote=True)}" data-g9-repair-target="{escape(qid, quote=True)}" tabindex="-1">'
                   f'<h4>Repair for {escape(row["label"])}</h4>' + card(row, qid, 'CORE1A') + '</section>')
    return ''.join(out)

def navigation_targets(text):
    """Only renderer-typed unit/repair landmarks join ordinary article navigation."""
    from html.parser import HTMLParser
    class Targets(HTMLParser):
        def __init__(self):super().__init__();self.ids=set()
        def handle_starttag(self,tag,attrs):
            data=dict(attrs);ident=data.get('id')
            if not ident:return
            if (tag=='article' and data.get('data-g9-unit')==ident) or (tag=='section' and data.get('data-g9-cu')==ident):self.ids.add(ident)
            if tag=='section' and ident=='repair-'+str(data.get('data-g9-repair-target')):self.ids.add(ident)
    parser=Targets();parser.feed(text);return parser.ids

JS = r'''document.addEventListener('click',event=>{
 const button=event.target.closest('[data-g9-probe-compare]');if(!button)return;
 const root=button.closest('[data-g9-learning-repair]');if(!root)return;
 const response=root.querySelector('[data-g9-probe-response]');
 const message=root.querySelector('[data-g9-probe-message]');
 if(!response.value.trim()){message.textContent='Write your prediction and reason first.';response.focus();return;}
 root.dataset.g9ProbeCommitted='true';root.querySelector('[data-g9-probe-feedback]').hidden=false;
 message.textContent='Compare your reasoning with the pattern below. Your response is not automatically graded.';
});
document.addEventListener('input',event=>{
 const root=event.target.closest('[data-g9-alignment-probe]');if(!root)return;
 const theta=Number(root.querySelector('[data-g9-theta]').value);
 const other=Number(root.querySelector('[data-g9-other]').value);
 const factor=Math.abs(theta-90)<1e-10?0:Math.cos(theta*Math.PI/180);
 root.querySelector('[data-g9-donor]').setAttribute('transform',`rotate(${theta} 180 180)`);
 root.querySelector('[data-g9-alignment-output]').textContent=`θ = ${theta}°; given factor = ${factor.toFixed(3)}; toy E = ${(-factor*factor+other).toFixed(3)}; c = ${other.toFixed(1)}.`;
});
const g9RepairHeader=document.querySelector('[data-g9-shell-header]');
if(g9RepairHeader&&window.ResizeObserver){new ResizeObserver(()=>{
 document.documentElement.style.setProperty('--g9-header-offset',Math.ceil(g9RepairHeader.getBoundingClientRect().height+16)+'px');
}).observe(g9RepairHeader);}
if(g9RepairHeader)document.documentElement.style.setProperty('--g9-header-offset',Math.ceil(g9RepairHeader.getBoundingClientRect().height+16)+'px');
function g9OpenRepairTarget(){
 let id;try{id=decodeURIComponent(location.hash.slice(1));}catch(_){return;}if(!id.startsWith('repair-'))return;
 const target=document.getElementById(id);if(!target)return;
 let parent=target.parentElement;while(parent){if(parent.tagName==='DETAILS')parent.open=true;parent=parent.parentElement;}
 target.focus({preventScroll:true});target.scrollIntoView({block:'start'});
}
window.addEventListener('hashchange',g9OpenRepairTarget);g9OpenRepairTarget();
'''

CSS = '''
article[id],section[id]{scroll-margin-top:var(--g9-header-offset,160px)}
.g9-repair-probe{padding:12px;border:1px solid var(--line);border-radius:12px;margin:12px 0}
.g9-repair-probe label,.g9-repair-probe textarea{display:block;width:100%;box-sizing:border-box}
.g9-repair-probe textarea{min-height:88px;font:inherit;margin:8px 0}
.g9-repair-probe button,.g9-repair-probe a{min-height:48px;display:inline-flex;align-items:center}
.g9-repair-probe [hidden]{display:none!important}
section[id]:focus{outline:3px solid var(--accent);outline-offset:3px}
'''
