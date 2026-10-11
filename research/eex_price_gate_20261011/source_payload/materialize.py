"""Restore reviewed UTF-8 sources only. Contains no market observations or remote requests."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
ROOT = Path.cwd()
PARTS = ROOT / 'research/eex_price_gate_20261011/source_payload'
raw = base64.b64decode(''.join((PARTS/f'part{i}.txt').read_text().strip() for i in range(1,5)), validate=True)
expected = '8443191d9c78b74add1231cf268a20b082942b65a346c3c329b44eb3335ccdcd'
if hashlib.sha256(raw).hexdigest() != expected:
    raise ValueError('Reviewed source archive mismatch')
payload = json.loads(lzma.decompress(raw, memlimit=256*1024*1024))
if payload.get('date') != '2026-10-11' or len(payload.get('files', [])) != 24:
    raise ValueError('Unexpected source inventory')
allowed = ('research/eex_price_gate_20261011/', 'paper/eex_price_revision_20261011/')
seen = set()
for item in payload['files']:
    rel = PurePosixPath(item['path'])
    if rel.is_absolute() or '..' in rel.parts or not str(rel).startswith(allowed):
        raise ValueError('Unsafe output path')
    if str(rel) in seen:
        raise ValueError('Duplicate source')
    seen.add(str(rel))
    data = item['text'].encode('utf-8')
    if hashlib.sha256(data).hexdigest() != item['sha256']:
        raise ValueError('Source checksum mismatch: ' + str(rel))
    destination = ROOT / rel
    if destination.exists():
        raise FileExistsError(str(rel))
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_bytes(data)
receipt = {'source_files':len(seen), 'archive_sha256':expected,
           'files':{item['path']:item['sha256'] for item in payload['files']},
           'market_price_regressions':0, 'third_party_raw_republished':False}
(ROOT/'research/eex_price_gate_20261011/results/SOURCE_TRANSFER_QA.json').write_text(json.dumps(receipt, indent=2))
print('24 reviewed source files materialized and verified.')
