"""Publish already-computed reviewed results only. No estimation or data retrieval."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
root = Path(__file__).resolve().parents[1]
parts = root / 'delivery_payload'
compressed = base64.b64decode(''.join((parts/f'part{i}.txt').read_text() for i in range(1,5)), validate=True)
if hashlib.sha256(compressed).hexdigest() != '79f907f0efd6ea4a5ff7feb74c0efbe2c6a5722453349e922d89a6b8406182e4':
    raise ValueError('Reviewed delivery archive mismatch')
raw = lzma.decompress(compressed, memlimit=256*1024*1024)
if hashlib.sha256(raw).hexdigest() != '7235e66b03d2826f3ddcbd5f77156f7df27f32b59405563ea7dda8a8f2c323cc':
    raise ValueError('Decoded delivery hash mismatch')
files = json.loads(raw)
if len(files) != 25:
    raise ValueError('Unexpected delivery scope')
receipt = {'scope':'previously completed results and self-authored text/code; no source data', 'new_fits_this_publication':0, 'new_data_downloads_this_publication':0, 'files':{}}
for name,text in files.items():
    rel = PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts or rel.suffix not in {'.md','.json','.csv','.py','.txt'}:
        raise ValueError('Unsafe or unsupported publication path')
    dest = root/rel
    if dest.exists():
        raise FileExistsError(str(rel))
    data=text.encode('utf-8')
    dest.parent.mkdir(parents=True,exist_ok=True)
    dest.write_bytes(data)
    receipt['files'][name]=hashlib.sha256(data).hexdigest()
(root/'audit/PUBLICATION_SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print('Published 25 reviewed text/result files with full hash verification.')
