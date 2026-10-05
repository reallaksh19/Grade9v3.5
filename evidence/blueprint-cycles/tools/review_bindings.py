"""Bind the twelve semantic review questions to current authored/rendered evidence.

This prepares an exact review worksheet. It does not grade learning quality.
"""
import hashlib
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / 'evidence/blueprint-cycles'
templates = {t['template_id']: t for t in json.loads(
    (ROOT / 'Shared/quality/question-demand-templates.v1.json').read_text())['templates']}

def digest(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()

for issue in (32, 31, 34, 33, 36, 35, 38, 37):
    pack = BASE / f'ISS{issue}'
    bank = json.loads((pack / 'inputs/owner.bank.json').read_text())
    package = json.loads((pack / 'inputs/package.v1.json').read_text())
    units = {u['id']: u for m in package['microtopics'] for u in m['construction_units']}
    representations = {r['id']: r for r in package['representations']}
    rows = []
    for q in bank['questions']:
        repair = q['extensions']['grade9v3:learning_repair']
        template = templates[q['extensions']['grade9v3:qrt_template']['template_id']]
        unit = units[repair['construction_ref']]
        rep = representations.get(unit.get('representation_ref'))
        visual_review=q['extensions'].get('grade9v3:core2_visual_review',{})
        question_reps=[representations[ref] for ref in visual_review.get('authored_figure_refs',q.get('figure_refs',[])) if ref in representations]
        evidence = {
            'H1': q['scaffolds'][0], 'H2': q['scaffolds'][1], 'H3': q['scaffolds'][2],
            'S1': {'question_representations': question_reps, 'teaching_representation': rep, 'visual_review':visual_review, 'waivers': q['extensions'].get('grade9v3:component_waivers', {})},
            'S2': {'scaffold_visual_refs': [s.get('visual_ref') for s in q['scaffolds']], 'question_stages': [r.get('reveal_stages',[]) for r in question_reps]},
            'S3': {'third_stage_waiver':visual_review.get('third_stage_waiver'), 'teaching_reveal_stage_refs': unit.get('reveal_stage_refs', []), 'decisive_act': next(move for move in q['answer']['reasoning_route'] if move['id'] == q['answer']['crux_move_ref'])},
            'P1': {'conditions': q.get('conditions', []), 'scaffolds': q['scaffolds'], 'protected_work': template['band_policy']['protected_work'], 'browser_report': '../'+Path(os.environ.get('G9_REVIEW_DIR','closure-20261005')).name+'/interaction-closure.json'},
            'P2': {'construction_ref': unit['id'], 'construction': unit, 'repair_anchor': 'repair-' + q['id'], 'return_question_ref': q['id']},
            'P3': {'reasoning_route': q['answer']['reasoning_route'], 'crux_move_ref': q['answer']['crux_move_ref'], 'check': q['answer']['check']},
            'M1': {'wrong_idea': repair['wrong_idea'], 'probe': repair['probe']},
            'M2': {'probe': repair['probe'], 'pattern': repair['pattern']},
            'M3': {'rule': repair['rule'], 'check': repair['check'], 'transfer': repair['transfer']},
        }
        rows.append({
            'question_ref': q['id'], 'label': q['original_identifier'],
            'template_id': template['template_id'], 'band': template['band'],
            'construction_ref': unit['id'], 'repair_anchor': 'repair-' + q['id'],
            'exact_artifact_sha256': {name: digest(pack / name) for name in (
                'inputs/owner.bank.json', 'inputs/package.v1.json',
                'rendered/core1a.html', 'rendered/core2.html')},
            'facets': {facet: {
                'status': 'AUTHORED_REQUIRES_INDEPENDENT_SEMANTIC_REVIEW',
                'review_question': template['review'][facet]['question'],
                'objective': template['review'][facet]['objective'],
                'authored_evidence': value,
                'mechanical_render_binding': 'SEE_FINAL_ASSURANCE_NOT_A_SEMANTIC_VERDICT',
            } for facet, value in evidence.items()},
        })
    (pack / 'qrt-repair-ledger.json').write_text(
        json.dumps(rows, indent=2, ensure_ascii=False) + '\n', encoding='utf-8', newline='\n')
print('80 exact review rows / 960 facets prepared; independent semantic verdicts remain pending.')
