"""Create readable Markdown exports; never use them to rebuild repaired DOCX math."""
from pathlib import Path
import hashlib, json, re, subprocess, tempfile
r=Path('paper/eex_manuscript_v8_20261010')
expected={
'MANUSCRIPT_EN_v8.docx':'15180678628a21a511b6f2ff49c91b1eb5bd89168129b522585ad20cc2452ee6',
'ONLINE_RESOURCE_1_v8.docx':'0b00a762b7b1b0ddf67d3711486c248a38a4005f4274b8366ff437e8591d66fe',
'TITLE_PAGE_v8.docx':'7daf9d090939235805a0c88a8e135872717877050eb61e6aae6db82b5000c335'}
receipt={'scope':'document-only build and export','new_fits':0,'new_resamples':0,'docx':{}}
for name,digest in expected.items():
 f=r/name
 actual=hashlib.sha256(f.read_bytes()).hexdigest()
 if actual!=digest: raise ValueError('DOCX differs from locally reviewed final: '+name)
 with tempfile.TemporaryDirectory() as temp:
  dst=r/(name.replace('_v8','').replace('.docx','.md'))
  subprocess.run(['pandoc',str(f),'--to=markdown','--wrap=none','--extract-media='+temp,'-o',str(dst)],check=True)
  text=dst.read_text()
  for p in Path(temp).rglob('*'):
   if not p.is_file():continue
   matches=[q for q in (r/'figures').glob('*.png') if hashlib.sha256(q.read_bytes()).hexdigest()==hashlib.sha256(p.read_bytes()).hexdigest()]
   if len(matches)!=1: raise ValueError('Unexpected exported image')
   text=text.replace(str(p),'figures/'+matches[0].name)
  dst.write_text(text)
 receipt['docx'][name]=actual
(r/'support/CI_DOCUMENT_QA.json').write_text(json.dumps(receipt,indent=2))
print(json.dumps(receipt,indent=2))
