"""Reconstruct only this revision's reviewed UTF-8 sources; no model/data execution."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
ROOT = Path.cwd()
TARGET = ROOT / 'paper/eex_manuscript_v6_20261010'
parts = TARGET / 'source_payload'
encoded = ''.join((parts / f'part{i}.txt').read_text() for i in range(1, 5))
compressed = base64.b64decode(encoded, validate=True)
expected = 'aed71f309e96ef2b7143a501e67a9a96fee9c1485a249706aeb0ae187fa27919'
if hashlib.sha256(compressed).hexdigest() != expected:
    raise ValueError('Reviewed source archive hash mismatch')
payload = json.loads(lzma.decompress(compressed, memlimit=256*1024*1024))
if payload['target'] != 'paper/eex_manuscript_v6_20261010' or len(payload['files']) != 19:
    raise ValueError('Unexpected scope')
for item in payload['files']:
    path = PurePosixPath(item['path'])
    if path.is_absolute() or '..' in path.parts:
        raise ValueError('Unsafe relative output path')
    destination = TARGET / path
    if destination.exists():
        raise FileExistsError(str(path))
    if 'text' in item:
        text = item['text']
    else:
        base = PurePosixPath(item['base'])
        if base.is_absolute() or '..' in base.parts or not str(base).startswith('paper/eex_manuscript_v3_20261010/'):
            raise ValueError('Unexpected base source')
        raw = (ROOT / base).read_bytes()
        if hashlib.sha256(raw).hexdigest() != item['base_sha256']:
            raise ValueError('Base source mismatch: ' + str(base))
        lines = raw.decode('utf-8').splitlines(keepends=True)
        for start, end, replacement in reversed(item['line_edits']):
            if not 0 <= start <= end <= len(lines):
                raise ValueError('Invalid source edit')
            lines[start:end] = [replacement]
        text = ''.join(lines)
    data = text.encode('utf-8')
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise ValueError('Reviewed source differs: ' + str(path))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
(TARGET/'figures').mkdir(exist_ok=True)
(TARGET/'support/source_materialization_receipt.json').write_text(json.dumps({
    'scope': payload['scope'], 'source_files': len(payload['files']),
    'compressed_sha256': expected, 'files': {x['path']:x['sha256'] for x in payload['files']},
    'new_statistical_fits': 0, 'new_resamples': 0
}, indent=2), encoding='utf-8')
print('19 reviewed source files reconstructed and SHA-256 verified.')
