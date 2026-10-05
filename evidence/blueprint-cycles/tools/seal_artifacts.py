"""Seal/verify Git index bytes without rewriting browser-observed artifacts."""
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NAME = 'evidence/blueprint-cycles/ARTIFACT-MANIFEST.json'
parser = argparse.ArgumentParser()
parser.add_argument('--verify', action='store_true')
args = parser.parse_args()
def git(*args): return subprocess.check_output(['git', *args], cwd=ROOT)
def indexed_blobs(head=False):
    entries = git('ls-tree', '-rz', 'HEAD') if head else git('ls-files', '--stage', '-z')
    mapping = {}
    for entry in entries.split(b'\0'):
        if not entry: continue
        metadata, path = entry.split(b'\t', 1)
        fields = metadata.split()
        mapping[path.decode()] = fields[2 if head else 1].decode()
    return mapping
def contents(oids):
    unique = list(dict.fromkeys(oids))
    proc = subprocess.run(['git', 'cat-file', '--batch'], cwd=ROOT,
                          input=('\n'.join(unique) + '\n').encode(), capture_output=True, check=True)
    data = proc.stdout
    result = {}
    cursor = 0
    for oid in unique:
        end = data.index(b'\n', cursor)
        header = data[cursor:end].split()
        assert header[0].decode() == oid and header[1] == b'blob'
        length = int(header[2]); cursor = end + 1
        result[oid] = data[cursor:cursor + length]; cursor += length + 1
    return result
if args.verify:
    manifest = json.loads((ROOT / NAME).read_text())
    mapping = indexed_blobs(head=True)
    blobs = contents(mapping[row['path']] for row in manifest['files'])
    failures = []
    for row in manifest['files']:
        data = blobs[mapping[row['path']]]
        blob = hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest()
        if len(data) != row['bytes'] or hashlib.sha256(data).hexdigest() != row['sha256'] or blob != row['git_blob_sha']:
            failures.append(row['path'])
    print(json.dumps({'files': len(manifest['files']), 'status': 'PASS' if not failures else 'FAIL', 'failures': failures}))
    raise SystemExit(bool(failures))
previous = json.loads((ROOT / NAME).read_text())
names = {r['path'] for r in previous['files']}
names.update(git('diff', '--cached', '--name-only', 'e01c6365acfd6aec84c0a6e94f11b683bd961f6e').decode().splitlines())
names.update(git('ls-files', '--', 'evidence/blueprint-cycles').decode().splitlines())
names.discard(NAME)
mapping = indexed_blobs()
names.intersection_update(mapping)
blobs = contents(mapping[name] for name in sorted(names))
rows = []
for name in sorted(names):
    data = blobs[mapping[name]]
    rows.append({'path': name, 'bytes': len(data),
                 'git_blob_sha': hashlib.sha1(b'blob ' + str(len(data)).encode() + b'\0' + data).hexdigest(),
                 'sha256': hashlib.sha256(data).hexdigest()})
manifest = {'schema': 'correction-artifact-manifest/v1', 'excludes_self': True,
            'tested_basis': '6dd20aa33c65f48315175e8ff360c339b204da16',
            'full_suite_basis': '37e5e3ea3b0e8b68d59f18c5fa691f095fcf4936',
            'historical_basis': '46e91c9ec4285e14ca0db469eda281ff31df596a',
            'byte_policy': 'EXACT_PUBLISHED_GIT_BLOB_BYTES',
            'evidence_scope': 'See closure-20261005/final-assurance.json; mechanical checks are not academic acceptance.',
            'files': rows}
(ROOT / NAME).write_text(json.dumps(manifest, indent=2) + '\n', encoding='utf-8', newline='\n')
print(json.dumps({'sealed_index_files': len(rows), 'bytes': sum(r['bytes'] for r in rows), 'excludes_self': True}))
