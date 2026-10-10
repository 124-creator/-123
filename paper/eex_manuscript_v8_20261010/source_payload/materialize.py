"""Verify and materialize only the reviewed v8 UTF-8 editorial sources."""
from pathlib import Path, PurePosixPath
import base64, hashlib, json, lzma, shutil
root=Path.cwd(); target=root/'paper/eex_manuscript_v8_20261010'
parts=target/'source_payload'
encoded=''.join((parts/f'part{i}.txt').read_text().strip() for i in (1,2,3))
packed=base64.b64decode(encoded,validate=True)
expected='23dc5b2c61957edbe9c007c3b260213664beb6fd9e07492856e47a556b1a8553'
if hashlib.sha256(packed).hexdigest()!=expected: raise ValueError('Reviewed source archive mismatch')
data=json.loads(lzma.decompress(packed,memlimit=128*1024*1024))
if data['target']!='paper/eex_manuscript_v8_20261010' or len(data['files'])!=12: raise ValueError('Unexpected output scope')
for item in data['files']:
 p=PurePosixPath(item['path'])
 if p.is_absolute() or '..' in p.parts: raise ValueError('Unsafe relative path')
 dst=target/p
 if dst.exists(): raise FileExistsError(str(p))
 raw=item['text'].encode('utf-8')
 if hashlib.sha256(raw).hexdigest()!=item['sha256']: raise ValueError('Source mismatch: '+str(p))
 dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(raw)
base=root/'paper/eex_manuscript_v7_20261010'
shutil.copytree(base/'figures',target/'figures')
shutil.copy2(base/'references.bib',target/'references.bib')
# Result support already published with v7; no raw market input is copied or run.
for name in ['NEW_TIME_RESULTS.json','strength_point_estimates.json','strength_intervals.csv','strength_distribution_balance.csv']:
 shutil.copy2(base/'support'/name,target/'support'/name)
shutil.copy2(base/'support/new_diagnostic/E3R_RESULTS.json',target/'support/E3R_RESULTS.json')
(target/'support/SOURCE_TRANSFER_QA.json').write_text(json.dumps({'packed_sha256':expected,'files':{i['path']:i['sha256'] for i in data['files']},'new_fits':0},indent=2))
print('12 reviewed UTF-8 files verified; frozen figures and aggregate sources copied.')
