"""Materialize reviewed UTF-8 sources only; no download, fitting, or raw-data publication."""
from pathlib import Path, PurePosixPath
import base64,hashlib,json,lzma,shutil
ROOT=Path.cwd()
R=ROOT/'research/eex_reported_price_design_20261011'
P=ROOT/'paper/eex_reported_price_v8_2_20261011'
encoded=''.join((R/'source_payload'/f'part{i}.txt').read_text() for i in (1,2,3))
compressed=base64.b64decode(encoded,validate=True)
expected='07ae8b12046fadba18113f57531375d420a2dbaa522c0209bc9bdfc1a0deedd0'
if hashlib.sha256(compressed).hexdigest()!=expected:raise ValueError('Reviewed source hash mismatch')
obj=json.loads(lzma.decompress(compressed,memlimit=256*1024*1024))
if len(obj['files'])!=22 or len(obj['figures'])!=9:raise ValueError('Unexpected materialization scope')
def safe(name):
    rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or not str(rel).startswith(('research/eex_reported_price_design_20261011/','paper/eex_reported_price_v8_2_20261011/')):
        raise ValueError('Unsafe output path')
    dest=ROOT/rel
    if dest.exists():raise FileExistsError(dest)
    dest.parent.mkdir(parents=True,exist_ok=True)
    return dest
for item in obj['files']:
    b=item['text'].encode('utf8')
    if hashlib.sha256(b).hexdigest()!=item['sha256']:raise ValueError('Source text differs: '+item['path'])
    safe(item['path']).write_bytes(b)
for item in obj['figures']:
    src=PurePosixPath(item['source'])
    if src.is_absolute() or '..' in src.parts or not str(src).startswith('paper/eex_manuscript_v8_20261010/figures/'):
        raise ValueError('Unexpected figure source')
    b=(ROOT/src).read_bytes()
    if hashlib.sha256(b).hexdigest()!=item['sha256']:raise ValueError('Frozen figure differs')
    safe(item['target']).write_bytes(b)
(R/'results/SOURCE_MATERIALIZATION.json').write_text(json.dumps({'scope':obj['scope'],'source_files':22,'frozen_figures':9,'compressed_sha256':expected,'new_real_price_fits':0,'source_hashes':{x['path']:x['sha256'] for x in obj['files']}},indent=2))
print('Reviewed text sources and frozen figure hashes passed. No real price data accessed.')
