"""Independent final artifact checks for all eight correction candidates.

Parses exact saved HTML, including inert templates. Does not claim live browser QA.
"""
import hashlib,json,re,subprocess,sys
from collections import Counter
from pathlib import Path
from lxml import html,etree
ROOT=Path(__file__).resolve().parents[3]
results=[];coverage=Counter()
for n in (31,32,33,34,35,36,37,38):
    directory=ROOT/f'evidence/blueprint-cycles/ISS{n}'
    bank=json.loads((directory/'inputs/owner.bank.json').read_text())
    package=json.loads((directory/'inputs/package.v1.json').read_text())
    a=html.fromstring((directory/'rendered/core1a.html').read_text());b=html.fromstring((directory/'rendered/core2.html').read_text())
    aids=set(a.xpath('//@id'));bids=set(b.xpath('//@id'));failures=[]
    qs={q['id']:q for q in bank['questions']}
    receipt=json.loads((directory/'cycle-receipt.json').read_text())
    for name,expected in receipt['page_hashes'].items():
        if hashlib.sha256((directory/'rendered'/name).read_bytes()).hexdigest()!=expected:
            failures.append({'defect':'saved page bytes differ from receipt','path':name})
    for group in ('authority_sha256','canonical_input_sha256'):
        for path,expected in receipt['render_basis'][group].items():
            if hashlib.sha256((ROOT/path).read_bytes().replace(b'\r\n',b'\n')).hexdigest()!=expected:
                failures.append({'defect':'receipt does not cover current source','path':path})
    for q in bank['questions']:
        nodes=b.xpath('//article[@data-g9-unit=$id]',id=q['id']);assert len(nodes)==1
        node=nodes[0];r=q['extensions']['grade9v3:learning_repair']
        for link in node.xpath('.//a[@data-g9-concept-link or @data-g9-repair-link]/@href'):
            if link.split('#')[-1] not in aids:failures.append({'q':q['id'],'defect':'unresolved teaching/repair target'})
        if node.xpath('.//details[@data-requires-attempt and @open]'):failures.append({'q':q['id'],'defect':'solution initially open'})
        repair=node.xpath('.//*[@data-g9-learning-repair=$id]',id=q['id'])
        if len(repair)!=1 or not repair[0].xpath('.//*[@data-g9-probe-feedback and @hidden]'):failures.append({'q':q['id'],'defect':'diagnostic feedback not initially hidden'})
        if not repair[0].xpath('ancestor::template'):failures.append({'q':q['id'],'defect':'diagnostic leaked into pre-attempt DOM'})
        if len(node.xpath('.//a[@data-g9-repair-link]'))!=1:failures.append({'q':q['id'],'defect':'missing item-specific repair'})
        all_text=' '.join(node.itertext())
        for move in q['answer']['reasoning_route']:
            for field in ('action','why_valid','output'):
                if move[field] not in all_text:
                    failures.append({'q':q['id'],'defect':'current reasoning differs from rendered solution','move':move['id'],'field':field})
        for h in q['scaffolds']:
            if h['text'] not in all_text:failures.append({'q':q['id'],'defect':'authored hint differs from exact rendered support'})
        # Template text is checked as authored evidence, not assumed visible to a learner.
        if r['probe'] not in all_text or r['rule'] not in all_text:failures.append({'q':q['id'],'defect':'review text differs from rendered repair'})
        coverage[q['extensions']['grade9v3:qrt_template']['template_id']]+=1
    for m in package['microtopics']:
        for u in m['construction_units']:
            anchor=(m.get('extensions') or {}).get('grade9v3:lesson_anchors',{}).get(u['id'])
            if anchor is not None:
                target=qs.get(anchor.get('target_question_ref'))
                if not target or anchor.get('construction_ref')!=u['id'] or anchor.get('target_crux_move_ref')!=target['answer']['crux_move_ref'] or anchor.get('stem')==target['stem']:
                    failures.append({'defect':'novel anchor is not distinct and bound to its actual crux','unit':u['id']})
    if n in (37,38):
        probes=a.xpath('//*[@data-g9-alignment-probe and not(ancestor::details) and not(ancestor::template)]')
        if not probes:failures.append({'defect':'authored D4 construction probe is not on the visible teaching surface'})
    back=a.xpath('//a[@data-g9-repair-link]/@href')
    if len(back)!=10 or not all(x.split('#')[-1] in bids for x in back):failures.append({'defect':'Core1A return links do not resolve'})
    first=a.xpath('//details[@data-g9-secondary and @open]')
    if first:failures.append({'defect':'secondary help initially open'})
    for src in a.xpath('//script[@src]/@src')+a.xpath('//link[@rel="stylesheet"]/@href'):
        if not (directory/'rendered'/src).is_file():failures.append({'defect':'missing local shell dependency','path':src})
    for rep in package['representations']:
        for ref in rep.get('rendered_asset_refs',[]):
            tree=etree.parse(str(ROOT/ref));ids=tree.xpath('//@data-g9-stage-id')
            if set(ids)!=set(s['id'] for s in rep.get('reveal_stages',[])):failures.append({'defect':'stage record differs from actual SVG','representation':rep['id']})
    receipt=json.loads((directory/'cycle-receipt.json').read_text())
    if receipt['render_gaps'] or receipt['owner_bank_basic'] or receipt['owner_bank_reference_findings']:failures.append({'defect':'canonical/reference validation finding remains'})
    results.append({'issue':n,'checks':'PASS' if not failures else 'FAIL','failures':failures,'observed':'LOCAL_EXECUTION + ARTIFACT_INSPECTION','browser':'NOT_RUN','stems_and_custody':receipt['stems_and_custody_preserved'],'hashes':receipt['page_hashes']})
matrix=json.loads((ROOT/'Shared/quality/question-demand-templates.v1.json').read_text())
uncovered=[t['template_id'] for t in matrix['templates'] if not coverage[t['template_id']]]
report={'schema':'blueprint-final-cycle/v1','results':results,'actual_cell_coverage':dict(sorted(coverage.items())),'cells_with_no_question_specimen':uncovered,'registered_cells':len(matrix['templates']),'specimens':80,'distinct_owner_questions':40,'all_cells_learning_validated':False,'all_facets_certified':False,'golden':False}
(ROOT/'evidence/blueprint-cycles/final-cycle-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':'PASS' if all(r['checks']=='PASS' for r in results) else 'FAIL','issues':[{'issue':r['issue'],'findings':len(r['failures'])} for r in results],'observed_cells':len(coverage),'uncovered':uncovered}))
if any(r['failures'] for r in results):sys.exit(1)
