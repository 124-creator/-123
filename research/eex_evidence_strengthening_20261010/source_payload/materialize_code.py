"""Restore only four reviewed self-authored source files; no source-data execution."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma
root = Path(__file__).resolve().parents[1]
compressed = base64.b64decode((root/'source_payload/reviewed_code.txt').read_text(),validate=True)
expected = '71d1705d4dc7432a6e687a10ed1d7f255f51d3a597c98797a479d463f1533738'
if hashlib.sha256(compressed).hexdigest()!=expected:
    raise ValueError('Code archive hash mismatch')
raw = lzma.decompress(compressed,memlimit=256*1024*1024)
if hashlib.sha256(raw).hexdigest()!='86388f652b9d5a3f96baec36ba9050b8fd490a80ab9f778693c0ab73319d8f40':
    raise ValueError('Decoded source hash mismatch')
files = json.loads(raw)
expected_files = {'code/run_strengthening.py','code/run_newtime_2026.py','code/test_strengthening.py','code/independent_crosscheck.py'}
if set(files)!=expected_files: raise ValueError('Unexpected source paths')
receipt = {'compressed_sha256':expected,'files':{},'raw_data_included':False}
for name,text in files.items():
    rel=PurePosixPath(name)
    if rel.is_absolute() or '..' in rel.parts: raise ValueError('Unsafe source path')
    dest=root/name
    if dest.exists(): raise FileExistsError(name)
    dest.parent.mkdir(parents=True,exist_ok=True)
    data=text.encode('utf-8');dest.write_bytes(data)
    receipt['files'][name]=hashlib.sha256(data).hexdigest()
(root/'audit').mkdir(exist_ok=True)
(root/'audit/REMOTE_SOURCE_RECEIPT.json').write_text(json.dumps(receipt,indent=2))
print('Restored four reviewed sources; no raw data included.')
