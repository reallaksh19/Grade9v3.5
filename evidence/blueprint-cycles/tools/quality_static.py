"""Write actual static gate verdicts for all correction pages; static cannot PASS."""
import argparse,json,sys
from pathlib import Path
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--repo',type=Path,default=Path(__file__).resolve().parents[3])
args=parser.parse_args();repo=args.repo.resolve();sys.path.insert(0,str(repo))
from Shared.tools import quality_gate
rows=[]
for issue in range(31,39):
    directory=repo/f'evidence/blueprint-cycles/ISS{issue}'
    manifest=json.loads((directory/'inputs/product.manifest.json').read_text())
    report=quality_gate.gate(directory/'rendered','Chemistry',manifest['product_id'],static=True)
    (directory/'quality-static.json').write_text(json.dumps(report,indent=2)+'\n')
    rows.append({'issue':issue,'verdict':report['verdict'],'findings':len(report['findings']),'continuity':len(report['continuity']),'fail_reasons':report['fail_reasons']})
(repo/'evidence/blueprint-cycles/static-quality-results.json').write_text(json.dumps(rows,indent=2)+'\n')
print(json.dumps(rows))
