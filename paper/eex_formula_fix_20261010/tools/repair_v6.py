"""Targeted OOXML repair; retains scientific text and image bytes. No experiments."""
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
import argparse, hashlib, json, re, shutil
from lxml import etree as E
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'; M='{'+NS['m']+'}'
BASE_SHA='8cc64c63803444334fc70c87e67965ca804f445d'
EXPECTED={'MANUSCRIPT_EN_v6.docx':'231c49e22b1a6a996fa59ab0d2bd6bc7f6ca3738c1e0b6da215126086a79d7be','ONLINE_RESOURCE_1_v6.docx':'2d61cf0f87df1c71bfb7236bc4c635696f41a40ed7e904915db77c9cdf8d4d07','TITLE_PAGE_v6.docx':'3b17a660c9ff2db42c31a3aa27a7cfb05addc59a46d52683354ebeedf7378c35'}
FUND='The authors received no financial support for this research.'
REVIEW='Xiang Wang has reviewed the manuscript. Remaining author declarations and the final data-access arrangement are recorded separately.'
SI_OLD='Funding, competing interests, actual contributions, AI-use disclosure and data permissions still require both authors’ confirmation before submission.'
SI_NEW='The corresponding author has confirmed that the research received no financial support and that Xiang Wang has reviewed the manuscript. Competing interests, actual contributions, AI-use disclosure and data permissions remain separate author declarations.'
REPLACEMENTS={
'Funding: [Author confirmation required for this study; no funding or absence of funding has been inferred.]':'Funding: '+FUND,
'[Author confirmation required. Add full funding-body names and grant identifiers where applicable; otherwise use an accurate statement confirmed for this study.]':FUND,
'Author-review status: Final declarations, data-access arrangements and approval by all authors are pending. This version is not for submission.':'Author-review status: '+REVIEW,
'[Both authors must approve the completed manuscript, references, declarations, AI-use disclosure and permissible data-access route before submission.]':REVIEW,
'Final approval':'Review status'}
def txt(el):
 return ''.join(el.xpath('.//w:t/text()|.//m:t/text()',namespaces=NS))
def wrun(text,sub=False,italic=False):
 r=E.Element(W+'r'); rp=E.SubElement(r,W+'rPr');fonts=E.SubElement(rp,W+'rFonts')
 for k in ('ascii','hAnsi','cs'):fonts.set(W+k,'Times New Roman')
 if italic:E.SubElement(rp,W+'i')
 E.SubElement(rp,W+'sz').set(W+'val','23')
 if sub:E.SubElement(rp,W+'vertAlign').set(W+'val','subscript')
 E.SubElement(rp,W+'lang').set(W+'val','en-GB')
 t=E.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=text
 return r
def mathematical_text(root):
 return re.sub(r'\s+','',''.join(root.xpath('//w:t/text()|//m:t/text()',namespaces=NS)))
def fix_docx(source,dest):
 digest=hashlib.sha256(source.read_bytes()).hexdigest()
 if digest!=EXPECTED[source.name]:raise ValueError('Different source snapshot: '+source.name)
 with ZipFile(source) as z:parts={i.filename:z.read(i.filename) for i in z.infolist()};infos=z.infolist()
 root=E.fromstring(parts['word/document.xml']);old_text=mathematical_text(root)
 math_before=len(root.xpath('//m:oMath',namespaces=NS));tables=len(root.xpath('//w:tbl',namespaces=NS));changes=[]
 for om in list(root.xpath('//m:oMath',namespaces=NS)):
  s=txt(om)
  for symbol in ('β','θ'):
   if s=='Δ'+symbol+'='+symbol+'late−'+symbol+'early':
    replacement=[wrun('Δ'+symbol+'\u00a0=\u00a0'+symbol,italic=True),wrun('late',sub=True),wrun('\u00a0−\u00a0'+symbol,italic=True),wrun('early',sub=True)]
    parent=om.getparent();idx=parent.index(om);parent.remove(om)
    for j,r in enumerate(replacement):parent.insert(idx+j,r)
    changes.append('inline-'+symbol+'-contrast-native-text-subscripts')
 for arg in root.xpath('//m:sub|//m:sup',namespaces=NS):
  children=list(arg)
  if len(children)<2 or not all(c.tag==M+'r' for c in children):continue
  label=''.join(c.findtext(M+'t','') for c in children)
  if not re.fullmatch('[A-Za-z]+',label):continue
  if not all(c.find(M+'rPr/'+M+'sty') is not None and c.find(M+'rPr/'+M+'sty').get(M+'val')=='p' for c in children):continue
  single=E.Element(M+'r');pr=E.SubElement(single,M+'rPr');E.SubElement(pr,M+'nor');E.SubElement(single,M+'t').text=label
  for c in children:arg.remove(c)
  arg.append(single);changes.append('atomic-upright-script-label:'+label)
 assert mathematical_text(root)==old_text,'Formula character sequence changed'
 declaration_changes=[]
 for p in root.xpath('//w:p',namespaces=NS):
  s=txt(p);new=REPLACEMENTS.get(s)
  if new is None and s.startswith('The numerical reimplementations use the same archive'):
   new=s.replace(SI_OLD,SI_NEW)
   new=new.replace('Final authorship, funding, conflicts, AI disclosure and data permissions must be verified by the authors before submission.','The corresponding author has confirmed that the research received no financial support and that Xiang Wang has reviewed the manuscript. Other author declarations and data permissions remain separate matters.')
  if new is not None and new!=s:
   if p.xpath('.//m:oMath',namespaces=NS):raise ValueError('Declaration includes math')
   for c in list(p):
    if c.tag!=W+'pPr':p.remove(c)
   p.append(wrun(new));declaration_changes.append({'old':s,'new':new})
 assert len(root.xpath('//w:tbl',namespaces=NS))==tables
 math_after=len(root.xpath('//m:oMath',namespaces=NS))
 if source.name.startswith('MANUSCRIPT'):
  assert math_before-math_after==2
  assert 'partial' in [txt(n) for n in root.xpath('//m:sub',namespaces=NS)]
  assert len(root.xpath('//w:vertAlign[@w:val="subscript"]',namespaces=NS))>=4
 else:assert math_before==math_after
 parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
 if 'docProps/core.xml' in parts:
  core=E.fromstring(parts['docProps/core.xml'])
  for n in core:
   if E.QName(n).localname in ('description','subject'):n.text='Formula-layout repair; no financial support confirmed; Xiang Wang review confirmed. Other declarations are not inferred.'
  parts['docProps/core.xml']=E.tostring(core,xml_declaration=True,encoding='UTF-8',standalone=True)
 dest.parent.mkdir(parents=True,exist_ok=True)
 with ZipFile(dest,'w',compression=ZIP_DEFLATED) as z:
  for info in infos:z.writestr(info,parts[info.filename])
 with ZipFile(source) as old,ZipFile(dest) as new:
  assert new.testzip() is None
  unchanged=[i for i in old.namelist() if i not in ('word/document.xml','docProps/core.xml')]
  assert all(old.read(i)==new.read(i) for i in unchanged)
 return {'source_sha256':digest,'output_sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),'math_objects_before':math_before,'math_objects_after':math_after,'inline_math_repaired':sum(x.startswith('inline') for x in changes),'formula_changes':changes,'declaration_changes':declaration_changes,'unmodified_other_zip_parts':len(unchanged),'mathematical_character_sequence_preserved':True,'images_tables_styles_unchanged':True}
def fix_markdown(s):
 s=s.replace(SI_OLD,SI_NEW)
 s=s.replace("Funding, competing interests, actual contributions, AI-use disclosure and data permissions still require both authors' confirmation before submission.","The corresponding author has confirmed no financial support and Xiang Wang's manuscript review. Other author declarations and data permissions remain separate matters.")
 for old,new in REPLACEMENTS.items():s=s.replace(old,new)
 s=s.replace('**Funding:** [Author confirmation required for this study; no funding or absence of funding has been inferred.]','**Funding:** '+FUND)
 s=s.replace('**Author-review status:** Final declarations, data-access arrangements and approval by all authors are pending. This version is not for submission.','**Author-review status:** '+REVIEW)
 s=s.replace('Final authorship, funding, conflicts, AI disclosure and data permissions must be verified by the authors before submission.',"The corresponding author has confirmed no financial support and Xiang Wang's manuscript review. Other author declarations and data permissions remain separate matters.")
 return s
def run(source_dir,out):
 out.mkdir(parents=True,exist_ok=True)
 report={'base_commit':BASE_SHA,'scope':'OOXML repair and user-confirmed declarations only','new_fits':0,'new_resamples':0,'new_statistics':0,'funding':'none; explicitly confirmed by user','xiang_wang_review':'reviewed; explicitly confirmed by user','final_submission_authorization':'not inferred from review','user_application_and_version':'unknown; Microsoft Word/WPS native testing not performed','documents':{}}
 for name in EXPECTED:report['documents'][name]=fix_docx(source_dir/name,out/name)
 for name in ('MANUSCRIPT_EN.md','ONLINE_RESOURCE_1.md','TITLE_PAGE.md'):
  p=source_dir/name
  if p.exists():(out/name).write_text(fix_markdown(p.read_text()),encoding='utf-8')
 if (source_dir/'figures').exists():shutil.copytree(source_dir/'figures',out/'figures',dirs_exist_ok=True)
 if (source_dir/'references.bib').exists():shutil.copy2(source_dir/'references.bib',out/'references.bib')
 (out/'support').mkdir(exist_ok=True)
 (out/'support/REPAIR_RECEIPT.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
 print(json.dumps(report,ensure_ascii=False,indent=2))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--source',type=Path,required=True);p.add_argument('--out',type=Path,required=True);a=p.parse_args();run(a.source,a.out)
