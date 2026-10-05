"""Reconcile measured checks without converting them into academic acceptance."""
import os
import hashlib
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from Shared.tools.render_core import pdf_publication_problems
from pypdf import PdfReader

BASE = ROOT / 'evidence/blueprint-cycles'
OUT = ROOT / os.environ.get('G9_REVIEW_DIR','evidence/blueprint-cycles/closure-20261005')
def read(p): return json.loads(p.read_text(encoding='utf-8-sig'))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

failures = []
interaction = read(OUT / 'interaction-closure.json')
supplements = read(OUT / 'supplement-browser.json')
artifact = read(BASE / 'final-cycle-results.json')
replay = read(OUT / 'replay.json')
pdfs = []
audits = []
facet_count = 0
for observation in interaction['results']:
    issue = observation['issue']
    pack = BASE / f'ISS{issue}'
    if observation['status'] != 'PASS': failures.append(f'ISS{issue}: interaction')
    for path, expected in observation['binding'].items():
        if sha(pack / path) != expected: failures.append(f'ISS{issue}: stale browser {path}')
    for name, expected in observation['pdfs'].items():
        if sha(pack / 'rendered' / name) != expected: failures.append(f'ISS{issue}: stale PDF {name}')
    for profile in ('strict', 'tablet'):
        data = read(OUT / f'ISS{issue}-{profile}.json')
        errors = [error for page in data.values() for error in page.get('errors', [])]
        if errors: failures.append(f'ISS{issue}: {profile} {errors}')
        audits.append({'issue': issue, 'profile': profile, 'pages': len(data),
                       'page_viewports': sum(len(page['viewports']) for page in data.values()),
                       'errors': errors})
    for row in read(pack / 'qrt-repair-ledger.json'):
        for path, expected in row['exact_artifact_sha256'].items():
            if sha(pack / path) != expected: failures.append(f'ISS{issue}: stale review row {row["question_ref"]}')
        facet_count += len(row['facets'])
    pdfs.append({'group': f'ISS{issue}', 'folder': str((pack / 'rendered').relative_to(ROOT)).replace('\\', '/'),
                 'problems': pdf_publication_problems(pack / 'rendered')})
for observation in supplements['results']:
    group = observation['group']
    folder = OUT / group / 'rendered'
    if observation['status'] != 'PASS': failures.append(f'{group}: browser')
    for name, expected in observation['binding'].items():
        if sha(folder / name) != expected: failures.append(f'{group}: stale page {name}')
    for row in observation['pdfs']:
        if row['page_digest'] != 'sha256:' + sha(folder / row['page']): failures.append(f'{group}: stale print page')
        if row['pdf_digest'] != 'sha256:' + sha(folder / row['pdf']): failures.append(f'{group}: stale print PDF')
        if row['protected_bodies_materialized'] != 0: failures.append(f'{group}: answer printed')
    pdfs.append({'group': group, 'folder': str(folder.relative_to(ROOT)).replace('\\', '/'),
                 'problems': pdf_publication_problems(folder)})
for row in pdfs:
    if row['problems']: failures.extend(row['problems'])
    folder = ROOT / row['folder']
    row['pdfs'] = [{'file': p.name, 'sha256': sha(p), 'pages': len(PdfReader(p).pages)}
                   for p in sorted(folder.glob('*.pdf'))]
    if any(p['pages'] < 1 for p in row['pdfs']): failures.append(f'{row["group"]}: empty PDF')
for row in artifact['results']:
    if row['checks'] != 'PASS': failures.append(f'ISS{row["issue"]}: artifact')
for row in replay['results']:
    if row['status'] != 'PASS': failures.append(f'ISS{row["issue"]}: replay')
matrix = read(OUT / 'matrix/calibration-ledger.json')
solutions = read(OUT / 'matrix/solution-checks.json')
if solutions['package_sha256'] != sha(OUT / 'matrix/package.v1.json'): failures.append('stale calibration solutions')
if solutions['status'] != 'PASS': failures.append('calibration solutions')
cells = sorted(set(artifact['actual_cell_coverage']) | {s['qrt_id'] for s in matrix['specimens']})
if len(cells) != 28: failures.append('candidate cell union is not 28')
seed = read(BASE / 'recovery-20261004/seed-full-suite.json')
full = read(OUT / 'closure-full-suite.json')
added = sorted(set(full['failures']) - set(seed['failures']))
if added: failures.append('introduced full-suite failure IDs')
focused = read(OUT / 'committed-contract-tests.json')
if focused['exit_code'] != 0: failures.append('final wording-delta focused tests')
frozen = read(OUT / 'frozen-submission-heads.json')
if any(r['status'] != 'UNCHANGED' for r in frozen['results']): failures.append('frozen submission drift')
academic_path=OUT/'academic-review.json'
academic=read(academic_path) if academic_path.exists() else None
if academic:
    for row in academic['rows']:
        folder=BASE/f'ISS{row["issue"]}'
        for name,expected in row['hashes'].items():
            if sha(folder/name)!=expected:failures.append('stale academic binding: '+row['question_ref']+' '+name)
report = {
    'schema': 'issue29-final-assurance/v1',
    'production_basis': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(),
    'mechanical_status': 'PASS' if not failures else 'FAIL', 'failures': failures,
    'registry': read(ROOT/'Shared/web/interactive-page-blueprints.v1.json')['registry_version'], 'core1a_blueprint': next(b['version'] for b in read(ROOT/'Shared/web/interactive-page-blueprints.v1.json')['blueprints'] if 'CORE1A' in b['core_roles']), 'core2_blueprint': next(b['version'] for b in read(ROOT/'Shared/web/interactive-page-blueprints.v1.json')['blueprints'] if 'CORE2' in b['core_roles']),
    'original_question_instances': 80, 'distinct_owner_questions': 40,
    'exact_review_facets': facet_count, 'independent_facets_accepted': 0,
    'original_instantiated_cells': 20, 'supplement_candidates': 8,
    'candidate_cell_union': cells, 'all_28_cells_independently_accepted': False,
    'browser': {'all_eight_interaction_statuses': [r['status'] for r in interaction['results']],
                'executed_source_question_states': sum(len(r['questionStates']) for r in interaction['results']),
                'audits': audits, 'supplements': [{'group': r['group'], 'status': r['status'], 'pages': len(r['pages'])} for r in supplements['results']]},
    'pdf_publication_checks': pdfs,
    'full_suite': {'verdict': 'FAIL', 'basis': full['basis_head'], 'summary': full['tests_summary'],
                   'seed_basis': seed['basis_head'], 'seed_summary': seed['tests_summary'],
                   'introduced_failure_ids': added,
                   'seed_failure_ids_absent': sorted(set(seed['failures']) - set(full['failures'])),
                   'note': 'The clean-checkout full suite covers '+full['basis_head']+'. Focused tests and hash-bound browser reports separately name their exact bases. Evidence/report helpers confer no academic acceptance. Absent failure IDs include reconciled contract/version expectations and are not all independent bug fixes.'},
    'author_academic_review': {'instance_bindings': len(academic['rows']) if academic else 0,
                               'distinct_answer_judgements': academic['distinct_answer_judgements'] if academic else 0,
                               'independent_facets_accepted': 0},
    'final_focused': {'basis': focused['basis_head'], 'summary': focused['tests_summary'], 'exit_code': focused['exit_code']},
    'frozen_submissions': 'ALL_EIGHT_UNCHANGED',
    'academic_verdict': 'REQUIRES_INDEPENDENT_REVIEW',
    'subject_limitations': ['Mathematics: six missing gate bindings and false author rule boundaries repaired; current authority check passes. Derived source records remain SOURCE_UNVERIFIED; original invalid publication/canonical claims are quarantined in the derived copy.',
                            'Physics: bounded toy scope probe demonstrates shared component behavior, not a law of friction or molecular energy.'],
    'static_gate_verdict': 'FAIL_RENDERED_RULES_NOT_MEASURED_UNCHANGED_NOT_REINTERPRETED',
    'golden': False, 'responsibility_complete': False,
}
(OUT / 'final-assurance.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'mechanical_status': report['mechanical_status'], 'failures': failures,
                 'pdfs': sum(len(r['pdfs']) for r in pdfs), 'facets_prepared': facet_count,
                 'candidate_cells': len(cells), 'full_suite': full['tests_summary'], 'new_failure_ids': len(added)}))
sys.exit(bool(failures))
