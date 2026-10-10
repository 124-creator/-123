"""Validate a reviewed writing snapshot; never recalculate market estimates."""
from pathlib import Path
import argparse, hashlib, json, zipfile
from lxml import etree
ROOT=Path(__file__).resolve().parents[1]
NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
def signature(path):
    with zipfile.ZipFile(path) as z:
        if z.testzip() is not None: raise ValueError('DOCX archive integrity failure')
        x=etree.fromstring(z.read('word/document.xml'))
    text='\n'.join(x.xpath('//w:t/text() | //m:t/text()',namespaces=NS))
    return {'semantic_sha256':hashlib.sha256(text.encode()).hexdigest(),'tables':len(x.xpath('//w:tbl',namespaces=NS)),'equation_objects':len(x.xpath('//m:oMath',namespaces=NS)),'drawings':len(x.xpath('//w:drawing',namespaces=NS))}
def main():
    ap=argparse.ArgumentParser(description=__doc__);ap.add_argument('--built',action='store_true');args=ap.parse_args()
    lock=json.loads((ROOT/'support/DISPLAY_LOCK.json').read_text())
    for item in lock['sources']:
        path=ROOT/item['path']
        if hashlib.sha256(path.read_bytes()).hexdigest()!=item['sha256']:raise ValueError('Reviewed source changed: '+item['path'])
    if args.built:
        for name,expected in lock['docx_signatures'].items():
            actual=signature(ROOT/name)
            if actual!=expected:raise ValueError('Rendered content signature differs: '+name+' '+str(actual))
    print(json.dumps({'passed':True,'scope':'reviewed text hashes and DOCX semantic structure, not market replication','sources':len(lock['sources']),'built_documents_checked':args.built,'new_fits':0}))
if __name__=='__main__':main()
