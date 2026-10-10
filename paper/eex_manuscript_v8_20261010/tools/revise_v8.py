"""Apply a hash-checked editorial plan to v7, preserving all original math and tables.
No raw market data are read, and no statistical model is fitted.
"""
from pathlib import Path
from datetime import datetime, timezone
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED
from copy import deepcopy
import argparse, csv, hashlib, io, json, re, subprocess
from lxml import etree
from docx import Document
from docx.shared import Pt, Mm
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn


def sha(data):
    return hashlib.sha256(data).hexdigest()


def cx(el):
    return etree.tostring(el, method='c14n')


def table_sig(table):
    node=deepcopy(table._tbl)
    for el in node.xpath('.//w:pPr/w:keepNext'):
        el.getparent().remove(el)
    return sha(cx(node))


def invariant(doc):
    return {
        'math': [sha(cx(x)) for x in doc._element.xpath('.//m:oMath')],
        'tables': [table_sig(x) for x in doc.tables],
        'images': [sha(x._inline.xml.encode()) for x in doc.inline_shapes],
        'scripted_runs': [sha(cx(x)) for x in doc._element.xpath('.//w:r[w:rPr/w:vertAlign]')],
    }


def deterministic_zip(path):
    data = io.BytesIO()
    with ZipFile(path) as old, ZipFile(data, 'w', ZIP_DEFLATED, compresslevel=9) as out:
        for name in sorted(old.namelist()):
            info = ZipInfo(name, (2026, 10, 10, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            info.external_attr = 0o600 << 16
            out.writestr(info, old.read(name))
    path.write_bytes(data.getvalue())


def evidence_map(doc):
    """Add one method-status table before the SI references, not new empirical evidence."""
    refs = next(p for p in doc.paragraphs if p.text == 'Additional references')
    hstyle = next(p.style for p in doc.paragraphs if p.text.startswith('S12 '))
    h = refs.insert_paragraph_before('S13 Estimands and evidence status', style=hstyle)
    h.paragraph_format.page_break_before = True
    p = refs.insert_paragraph_before(
        'Table S10 records the role of each analysis in the research sequence. '
        'Different transformations, uncertainty levels and later checks are not interchangeable '
        'confirmations. The labels describe recorded analysis roles, not a prospectively registered design.')
    p.paragraph_format.keep_with_next = True
    cap = refs.insert_paragraph_before('Table S10 Evidence roles and limits')
    cap.paragraph_format.keep_with_next = True
    rows = [
        ['Historical pooled relation', 'Slope and residual correlation', 'Exploratory 95% month-block intervals', 'Within-sample conditional association'],
        ['Historical period contrast', 'Primary slope difference; secondary correlation difference', '97.5% slope intervals; 95% correlation intervals', 'Separate estimands; neither proves policy causality'],
        ['Composition sensitivity', 'Weighted correlation difference', 'Exploratory 97.5% intervals; 95% paired-change intervals', 'Selected-moment comparison; incomplete volume-distribution balance'],
        ['Additional 2026 period', 'Re-estimated slope and correlation', 'Nine-month diagnostics; finite percentile and deletion ranges', 'New-time description, not a frozen-model forecast'],
        ['External price relation', 'Not estimated', 'No eligible auction-level reference series', 'Missing validation, not a null result'],
    ]
    table = doc.add_table(rows=1, cols=4)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    for c, text in zip(table.rows[0].cells, ['Analysis', 'Estimand', 'Uncertainty display', 'Interpretation']):
        c.text = text
    for row in rows:
        for c, text in zip(table.add_row().cells, row):
            c.text = text
    widths = [32, 43, 45, 44]
    for j, width in enumerate(widths):
        table.columns[j].width = Mm(width)
    for ri, row in enumerate(table.rows):
        pr = row._tr.get_or_add_trPr()
        pr.append(OxmlElement('w:cantSplit'))
        if ri == 0:
            pr.append(OxmlElement('w:tblHeader'))
        for j, cell in enumerate(row.cells):
            cell.width = Mm(widths[j])
            cell.vertical_alignment = WD_CELL_VERTICAL_ALIGNMENT.CENTER
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.06
                p.paragraph_format.keep_with_next = ri < len(rows)
                for r in p.runs:
                    r.font.name = 'Times New Roman'
                    r.font.size = Pt(9.5)
                    r.bold = ri == 0
    borders = OxmlElement('w:tblBorders')
    for side in ('top','bottom','left','right','insideH','insideV'):
        b = OxmlElement('w:'+side)
        b.set(qn('w:val'), 'single' if side in ('top','bottom') else 'nil')
        b.set(qn('w:sz'),'6')
        b.set(qn('w:color'),'000000')
        borders.append(b)
    table._tbl.tblPr.append(borders)
    for cell in table.rows[0].cells:
        b = OxmlElement('w:tcBorders'); edge=OxmlElement('w:bottom')
        edge.set(qn('w:val'),'single'); edge.set(qn('w:sz'),'4'); b.append(edge)
        cell._tc.get_or_add_tcPr().append(b)
    refs._p.addprevious(table._tbl)
    note = refs.insert_paragraph_before(
        'Note: Each interval family is conditional on its approximation. No procedure adjusts '
        'the complete historical specification search, and exact enumeration does not give exact '
        'frequentist coverage. The price extension has no estimates. This table adds no statistical test.')
    for r in note.runs:
        r.font.size = Pt(9.5)
    note.paragraph_format.keep_together=True


def run(source, out, plan_path):
    source=Path(source); out=Path(out); out.mkdir(parents=True,exist_ok=True)
    plan=json.loads(Path(plan_path).read_text())
    checks={'base_commit':plan['base_commit'],'new_fits':0,'new_resamples':0,
            'scope':'document-object preservation, not independent market-data replication',
            'documents':{},'changed_paragraphs':0}
    inventory=[]; changes=[]
    for filename, entry in plan['documents'].items():
        path=source/filename
        if sha(path.read_bytes()) != entry['source_sha256']:
            raise ValueError('Source DOCX hash mismatch: '+filename)
        doc=Document(path); before=invariant(doc); pars=list(doc.paragraphs)
        for edit in entry['replacements']:
            p=pars[edit['index']]
            if sha(p.text.encode())!=edit['old_sha256']:
                raise ValueError('Paragraph mismatch '+filename+':'+str(edit['index']))
            if p._p.xpath('.//m:oMath | .//w:drawing | .//w:vertAlign'):
                raise ValueError('Refusing to rewrite a complex paragraph')
            runpr=deepcopy(p.runs[0]._r.rPr) if p.runs and p.runs[0]._r.rPr is not None else None
            old_text=p.text
            p.clear(); r=p.add_run(edit['new'])
            if runpr is not None: r._r.insert(0,runpr)
            if filename.startswith('ONLINE_') and edit['index']==3:
                r.bold=False
            changes.append({'file':filename,'paragraph':edit['index'],'before':old_text,'after':edit['new']})
        if filename.startswith('ONLINE_'):
            for idx in (7,8,9):
                if doc.paragraphs[idx].text != Document(path).paragraphs[idx].text:
                    raise ValueError('Reproduction path changed')
            if 'Author-review v8' not in doc.paragraphs[3].text:
                raise ValueError('SI version not updated')
            evidence_map(doc)
        for p in doc.paragraphs:
            if p.text.startswith(('Note:', 'Fig. ')):
                p.paragraph_format.keep_together=True
        if filename.startswith('MANUSCRIPT_'):
            for p in doc.paragraphs:
                if p.text=='3 Data and empirical design':
                    p.paragraph_format.page_break_before=True
        for t in doc.tables:
            following=t._tbl.getnext()
            if following is not None and ''.join(following.xpath('.//w:t/text()')).startswith(('Note:', 'Panel B:', 'Panel C:')):
                for c in t.rows[-1].cells:
                    for p in c.paragraphs:
                        p.paragraph_format.keep_with_next=True
        for section in doc.sections:
            for p in section.header.paragraphs:
                for r in p.runs: r.text=r.text.replace('AUTHOR-REVIEW V7','AUTHOR-REVIEW V8')
        doc.core_properties.subject='Author-review v8; frozen numerical evidence; no new estimation'
        doc.core_properties.comments='Funding absence and preceding Wang review recorded; unresolved declarations retained.'
        doc.core_properties.created=datetime(2026,10,10,tzinfo=timezone.utc)
        doc.core_properties.modified=datetime(2026,10,10,tzinfo=timezone.utc)
        dest=out/filename.replace('_v7','_v8')
        doc.save(dest); deterministic_zip(dest)
        after=invariant(Document(dest))
        for part in ('math','images','scripted_runs'):
            if after[part]!=before[part]: raise ValueError('Changed protected '+part)
        if after['tables'][:len(before['tables'])]!=before['tables']:
            raise ValueError('Original table changed')
        xml=ZipFile(dest).read('word/document.xml')
        # Native simple whole-word late/early subscripts must stay intact.
        text='\n'.join(''.join(p._p.xpath('.//w:t/text() | .//m:t/text()')) for p in doc.paragraphs)
        for term in ('Zhongfei Tian','Xiang Wang','15517837680@163.com'):
            if term not in text: raise ValueError('Missing author item '+term)
        if text.index('Zhongfei Tian')>text.index('Xiang Wang'): raise ValueError('Author order')
        if filename.startswith('MANUSCRIPT_') and 'The authors received no financial support' not in text:
            raise ValueError('Funding state lost')
        checks['documents'][dest.name]={
            'sha256':sha(dest.read_bytes()),'document_xml_sha256':sha(xml),
            'original_math_preserved':len(before['math']),
            'original_table_contents_preserved':len(before['tables']),
            'allowed_table_layout_change':'Keep last row with its following note',
            'tables_including_panels':len(after['tables']),
            'images_preserved':len(before['images']),
            'scripted_runs_preserved':len(before['scripted_runs']),
            'original_table_numbers_and_values_unchanged':True,
        }
        checks['changed_paragraphs']+=len(entry['replacements'])
        for ti,t in enumerate(doc.tables):
            for ri,row in enumerate(t.rows):
                for ci,cell in enumerate(row.cells):
                    tx=''.join(cell._tc.xpath('.//w:t/text() | .//m:t/text()'))
                    for token in re.findall(r'(?<![A-Za-z])[-−]?\d+(?:[,.]\d+)*(?:%|)?',tx):
                        inventory.append([dest.name,ti,ri,ci,token,tx])
    checks['abstract_words']=len(plan['documents']['MANUSCRIPT_EN_v7.docx']['replacements'][1]['new'].split())
    if not 150<=checks['abstract_words']<=250: raise ValueError('Abstract word count')
    (out/'support').mkdir(exist_ok=True); (out/'tables').mkdir(exist_ok=True)
    (out/'support/DOCUMENT_QA_V8.json').write_text(json.dumps(checks,indent=2))
    (out/'support/TEXT_CHANGELOG.json').write_text(json.dumps(changes,ensure_ascii=False,indent=2))
    with (out/'tables/DISPLAY_NUMERICS_V8.csv').open('w',newline='') as f:
        w=csv.writer(f);w.writerow(['file','table_object','row','column','display_token','cell_text']);w.writerows(inventory)
    print(json.dumps(checks,indent=2))
    return checks

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',required=True);p.add_argument('--out',required=True);p.add_argument('--plan',required=True)
    a=p.parse_args();run(a.source,a.out,a.plan)
