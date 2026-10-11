"""Targeted DOCX text edit. Preserve original math/media and every numeric table.
No regressions, data downloading, macro execution or automatic declarations.
"""
import argparse, copy, hashlib, json, re, zipfile
from pathlib import Path
from lxml import etree as E
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
W='{'+NS['w']+'}'

def text(p):return ''.join(p.xpath('.//w:t/text()',namespaces=NS))
def rewrite(p,old,new):
    if text(p)!=old:raise ValueError('Paragraph text does not match reviewed source')
    if p.xpath('.//m:oMath|.//w:drawing',namespaces=NS):raise ValueError('Refuse replacing math/drawing paragraph')
    prop=p.find('w:pPr',NS);style=p.find('w:r/w:rPr',NS)
    style=copy.deepcopy(style) if style is not None else None
    for c in list(p):
        if c is not prop:p.remove(c)
    # Newline-preserving plain text; new equations stay in separate protocol file.
    for i,line in enumerate(new.split('\n')):
        r=E.SubElement(p,W+'r')
        if style is not None:r.append(copy.deepcopy(style))
        if i:E.SubElement(r,W+'br')
        t=E.SubElement(r,W+'t');t.set('{http://www.w3.org/XML/1998/namespace}space','preserve');t.text=line

def signature(root):
    return {'math':[E.tostring(n,method='c14n') for n in root.xpath('//m:oMath',namespaces=NS)],
            'table_numbers':[re.findall(r'(?<![A-Za-z])[-−]?\d+(?:\.\d+)?',text(t)) for t in root.xpath('//w:tbl',namespaces=NS)],
            'drawings':[E.tostring(n,method='c14n') for n in root.xpath('//w:drawing',namespaces=NS)],
            'subscripts':[text(n) for n in root.xpath('//w:r[w:rPr/w:vertAlign[@w:val="subscript"]]',namespaces=NS)]}

def build(source_root,out,plan):
    out.mkdir(parents=True,exist_ok=True);logs=[]
    for d in plan['documents']:
        src=source_root/d['source'];raw=src.read_bytes()
        if hashlib.sha256(raw).hexdigest()!=d['source_sha256']:raise ValueError('Source SHA mismatch: '+src.name)
        z=zipfile.ZipFile(src);parts={n:z.read(n) for n in z.namelist()};root=E.fromstring(parts['word/document.xml']);before=signature(root)
        for change in d['changes']:
            ps=[p for p in root.xpath('//w:p',namespaces=NS) if text(p)==change['old']]
            if len(ps)!=1:raise ValueError('Text target not unique: '+change['old'][:55])
            rewrite(ps[0],change['old'],change['new'])
        after=signature(root)
        if before!=after:raise ValueError('Protected math/table numbers/drawings/subscripts changed')
        parts['word/document.xml']=E.tostring(root,xml_declaration=True,encoding='UTF-8',standalone=True)
        for n in parts:
            if n.startswith('word/header') and n.endswith('.xml'):
                hr=E.fromstring(parts[n])
                for t in hr.xpath('//w:t',namespaces=NS):
                    if t.text:t.text=re.sub(r'AUTHOR-REVIEW V8(?:\.1)?(?![\d.])','AUTHOR-REVIEW V8.2',t.text)
                parts[n]=E.tostring(hr,xml_declaration=True,encoding='UTF-8',standalone=True)
        dest=out/d['output']
        if dest.exists():raise FileExistsError(dest)
        with zipfile.ZipFile(dest,'w',zipfile.ZIP_DEFLATED) as oz:
            for n,body in parts.items():oz.writestr(n,body)
        logs.append({'file':dest.name,'sha256':hashlib.sha256(dest.read_bytes()).hexdigest(),
                     'source_sha256':d['source_sha256'],'paragraph_changes':len(d['changes']),
                     'native_math_objects':len(after['math']),'physical_tables':len(after['table_numbers']),
                     'drawings':len(after['drawings']),'protected_signature_unchanged':True,
                     'source_bytes_unchanged':hashlib.sha256(src.read_bytes()).hexdigest()==d['source_sha256']})
    (out/'DOCUMENT_QA.json').write_text(json.dumps({'files':logs,'new_market_estimates':0,'new_resamples':0},indent=2))
    return logs
if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--source-root',type=Path,required=True);a.add_argument('--out',type=Path,required=True);a.add_argument('--plan',type=Path,required=True);v=a.parse_args()
    print(json.dumps(build(v.source_root,v.out,json.loads(v.plan.read_text())),indent=2))
