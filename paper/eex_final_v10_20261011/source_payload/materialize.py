"""Materialize reviewed editorial text only; no market data or model execution."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
ROOT = Path.cwd()
TARGET = ROOT / 'paper/eex_final_v10_20261011'
encoded = ''.join((TARGET/'source_payload'/f'part{i}.txt').read_text(encoding='utf-8') for i in range(1,6))
if len(encoded) != 42560:
    raise ValueError('Wrong encoded length')
compressed = base64.b64decode(encoded, validate=True)
expected = '766aeae3e39086cbfd62013946164d6cc29b7bed21f2f76f217e45382d778764'
if len(compressed) != 31920 or hashlib.sha256(compressed).hexdigest() != expected:
    raise ValueError('Reviewed source archive differs')
payload = json.loads(lzma.decompress(compressed, memlimit=256*1024*1024))
if payload['target'] != 'paper/eex_final_v10_20261011' or len(payload['files']) != 14:
    raise ValueError('Unexpected output scope')
seen = set()
for item in payload['files']:
    rel = PurePosixPath(item['path'])
    if rel.is_absolute() or '..' in rel.parts or str(rel) in seen:
        raise ValueError('Unsafe or duplicate relative path')
    seen.add(str(rel))
    dest = TARGET / rel
    if dest.exists():
        raise FileExistsError(str(rel))
    body = item['text'].encode('utf-8')
    if hashlib.sha256(body).hexdigest() != item['sha256']:
        raise ValueError('Individual reviewed file differs: '+str(rel))
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(body)
for name in ('figures','support','tables'):
    (TARGET/name).mkdir(exist_ok=True)
receipt = {'scope':payload['scope'], 'compressed_sha256':expected, 'reviewed_text_files':14,
           'files':{r['path']:r['sha256'] for r in payload['files']}, 'new_market_fits':0}
(TARGET/'support/SOURCE_MATERIALIZATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('14 reviewed editorial source files materialized and hashed.')
