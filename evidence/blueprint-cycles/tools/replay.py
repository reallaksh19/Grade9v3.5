"""Replay all stored correction inputs through the production renderer.

Run from any cwd: python evidence/blueprint-cycles/tools/replay.py --repo .
Requires jsonschema. Does not certify browser or academic quality.
"""
import argparse, hashlib, json, sys
from pathlib import Path

parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
parser.add_argument('--out',type=Path)
args=parser.parse_args()
repo=args.repo.resolve();sys.path.insert(0,str(repo))
from jsonschema import Draft202012Validator, RefResolver
from Shared.tools import render_core,product_manifest,product_coverage,owner_bank,learning_repair,web_blueprint_contract

def load(path):return json.loads(path.read_text(encoding='utf-8'))
def validate(record,path):
    schema=load(path)
    Draft202012Validator(schema,resolver=RefResolver.from_schema(schema,store={'':schema})).validate(record)

validate(web_blueprint_contract.load_registry(),repo/'Shared/web/interactive-page-blueprint.schema.json')
results=[]
for issue in (32,31,34,33,36,35,38,37):
    directory=repo/f'evidence/blueprint-cycles/ISS{issue}'
    pkg=load(directory/'inputs/package.v1.json');bank=load(directory/'inputs/owner.bank.json');manifest=load(directory/'inputs/product.manifest.json')
    validate(pkg,render_core.PACKAGE_SCHEMA)
    problems=owner_bank.check(bank,complete=True)
    if problems:raise ValueError(problems)
    unit_ids={u['id'] for m in pkg['microtopics'] for u in m['construction_units']}
    for question in bank['questions']:
        problems=learning_repair.problems(question,unit_ids)
        if problems:raise ValueError((question['id'],problems))
    selection=product_manifest.validate_selection(manifest,[pkg],bank['questions'])
    product_coverage.validate(manifest,product_manifest.derivable([pkg],bank['questions']))
    ctx=render_core.Ctx(manifest,[pkg],bank['questions'],web_blueprint_contract.load_registry(),selection_rows=selection)
    pages={render_core.ROLE_FILE[role]:render_core.page(ctx,role,'PAGES',render_core.DIGEST_SLOT) for role in ('CORE1A','CORE2')}
    pages['index.html']=render_core.index_page(ctx,render_core.DIGEST_SLOT)
    digest=render_core._artifact_digest(pages)
    expected=load(directory/'cycle-receipt.json')
    hashes={name:hashlib.sha256(text.replace(render_core.DIGEST_SLOT,digest).encode()).hexdigest() for name,text in pages.items()}
    match=hashes==expected['page_hashes'] and digest==expected['render_digest']
    results.append({'issue':issue,'status':'PASS' if match and not ctx.gaps else 'FAIL','render_digest':digest,'page_hashes':hashes,'gaps':ctx.gaps,'oracle':'INDEPENDENT_REPLAY_OF_STORED_INPUTS_WITH_PRODUCTION_API','browser':'NOT_RUN','golden':False})
report={'schema':'blueprint-replay/v1','results':results,'golden':False}
if args.out:args.out.write_text(json.dumps(report,indent=2)+'\n',encoding='utf-8')
print(json.dumps({'replay':[{'issue':row['issue'],'status':row['status']} for row in results],'golden':False}))
if any(row['status']!='PASS' for row in results):sys.exit(1)
