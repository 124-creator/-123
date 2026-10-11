"""Materialize only reviewed v9 UTF-8 sources; no raw data or model execution."""
from pathlib import Path, PurePosixPath
import base64,hashlib,json,lzma
root=Path.cwd();folder=root/'paper/eex_price_integrated_v9_20261011/source_payload'
encoded=''.join((folder/f'part{i}.txt').read_text() for i in (1,2,3))
if len(encoded)!=40044:raise ValueError('Source payload length mismatch')
body=base64.b64decode(encoded,validate=True)
if hashlib.sha256(body).hexdigest()!='738913796aa7cc0704cdbf575dae88b268e06daffb51797063c736db6edec882':raise ValueError('Source payload digest mismatch')
obj=json.loads(lzma.decompress(body,memlimit=256*1024*1024))
if len(obj['files'])!=14:raise ValueError('Unexpected source file count')
seen=set()
for item in obj['files']:
    rel=PurePosixPath(item['path'])
    if rel.is_absolute() or '..' in rel.parts or not str(rel).startswith(('paper/eex_price_integrated_v9_20261011/','research/eex_aggregate_review_20261011/')):raise ValueError('Unsafe or out-of-scope path')
    if str(rel) in seen:raise ValueError('Duplicate source path')
    seen.add(str(rel));data=item['text'].encode('utf-8')
    if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Reviewed file digest mismatch: '+str(rel))
    p=root/rel
    if p.exists():raise FileExistsError(str(rel))
    p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
receipt={'scope':obj['scope'],'source_files':14,'compressed_sha256':hashlib.sha256(body).hexdigest(),'files':[{k:v for k,v in x.items() if k!='text'} for x in obj['files']]}
(root/'paper/eex_price_integrated_v9_20261011/support/SOURCE_TRANSFER.json').write_text(json.dumps(receipt,indent=2))
print('14 reviewed sources materialized and hash-verified')
