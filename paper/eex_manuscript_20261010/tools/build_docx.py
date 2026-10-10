"""Build an editable author-review Word document from manuscript sources; no statistical execution."""
from pathlib import Path
import subprocess, json, re
from docx import Document
from docx.shared import Pt, Inches, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
ROOT=Path(__file__).resolve().parents[1]
WORK=ROOT/'_build'
WORK.mkdir(exist_ok=True)
default_ref=WORK/'default_reference.docx'
default_ref.write_bytes(subprocess.check_output(['pandoc','--print-default-data-file','reference.docx']))
ref=Document(default_ref)
sec=ref.sections[0]
sec.page_width=Mm(210);sec.page_height=Mm(297)
sec.top_margin=Mm(22);sec.bottom_margin=Mm(22);sec.left_margin=Mm(23);sec.right_margin=Mm(23)
sec.header_distance=Mm(10);sec.footer_distance=Mm(10)
for st in ref.styles:
    if st.type in (1,2):
        st.font.name='Times New Roman';st.font.color.rgb=RGBColor(0,0,0)
        st.element.get_or_add_rPr().set(qn('w:lang'),'en-GB') if False else None
norm=ref.styles['Normal'];norm.font.size=Pt(11.5)
norm.paragraph_format.line_spacing=1.14;norm.paragraph_format.space_before=Pt(0);norm.paragraph_format.space_after=Pt(6)
for name,size in [('Title',20),('Subtitle',12),('Heading 1',15),('Heading 2',13),('Heading 3',11.5)]:
 st=next(st for st in ref.styles if st.name==name);st.font.name='Times New Roman';st.font.size=Pt(size);st.font.color.rgb=RGBColor(0,0,0)
 st.font.bold=name not in ['Subtitle']
 st.paragraph_format.space_before=Pt(12 if name.startswith('Heading') else 0)
 st.paragraph_format.space_after=Pt(6)
 st.paragraph_format.keep_with_next=True
 if name in ['Title','Subtitle']:st.paragraph_format.alignment=WD_ALIGN_PARAGRAPH.CENTER
ref.styles['Caption'].font.size=Pt(10)
ref.styles['Caption'].paragraph_format.space_after=Pt(5)
ref.save(WORK/'reference.docx')
text=(ROOT/'MANUSCRIPT_EN.md').read_text(encoding='utf-8')+'\n\n'+(ROOT/'SUPPLEMENT_EN.md').read_text(encoding='utf-8')
text=text.replace('figures/Fig1.svg','figures/Fig1.png').replace('figures/Fig2.svg','figures/Fig2.png')
(WORK/'combined.md').write_text(text)
out=ROOT/'MANUSCRIPT_EN.docx'
proc=subprocess.run(['pandoc',str(WORK/'combined.md'),'-o',str(out),'--reference-doc='+str(WORK/'reference.docx'),'--resource-path='+str(ROOT),'--from=markdown+tex_math_dollars'],capture_output=True,text=True)
if proc.returncode: raise RuntimeError(proc.stderr)
(WORK/'pandoc_log.txt').write_text(proc.stderr)
doc=Document(out)
sec=doc.sections[0]
# Compact, high-contrast manuscript header and consistent page numbers.
h=sec.header.paragraphs[0];h.alignment=WD_ALIGN_PARAGRAPH.RIGHT
r=h.add_run('EUA AUCTION QUANTITIES  |  AUTHOR-REVIEW REVISION 2');r.font.name='Times New Roman';r.font.size=Pt(8);r.font.color.rgb=RGBColor.from_string('555555')
f=sec.footer.paragraphs[0];f.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=f.add_run('');r.font.size=Pt(9)
field=OxmlElement('w:fldSimple');field.set(qn('w:instr'),'PAGE');f._p.append(field)
# Use readable styles for notes, links, captions, and formulas.
for nm in ['Body Text','First Paragraph']:
 if nm in doc.styles:
  st=doc.styles[nm];st.font.name='Times New Roman';st.font.size=Pt(11.5);st.paragraph_format.line_spacing=1.14;st.paragraph_format.space_before=Pt(0);st.paragraph_format.space_after=Pt(6)
if 'Hyperlink' in doc.styles:
 doc.styles['Hyperlink'].font.color.rgb=RGBColor(0,0,0)
 doc.styles['Hyperlink'].font.underline=False
in_references=False
in_supplement=False
for p in doc.paragraphs:
 p.paragraph_format.widow_control=True
 t=p.text
 if t=='Online Resource 1': in_supplement=True
 if in_supplement and not p.style.name.startswith('Heading') and t!='Online Resource 1':
  p.paragraph_format.line_spacing=1.08
  p.paragraph_format.space_after=Pt(5)
  for r in p.runs:r.font.size=Pt(11)
 if t=='References': in_references=True
 elif t=='Online Resource 1': in_references=False
 elif in_references:
  p.paragraph_format.line_spacing=1.05;p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(6)
  for r in p.runs:r.font.size=Pt(10.5)
 if t.startswith('1. Introduction'):
  p.paragraph_format.page_break_before=True
 if t=='Online Resource 1':
  p.paragraph_format.page_break_before=True
 if t=='References':
  p.paragraph_format.keep_with_next=True
 if t.startswith(('Table ', 'Panel ', 'Fig. ')):
  p.paragraph_format.keep_with_next=True;p.paragraph_format.space_after=Pt(4)
  for r in p.runs:r.font.size=Pt(10.5)
 if t.startswith('Note:'):
  for r in p.runs:r.font.size=Pt(10)
  p.paragraph_format.line_spacing=1.08;p.paragraph_format.space_after=Pt(7)
 if p._p.xpath('.//w:drawing'):
  p.paragraph_format.keep_with_next=True;p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 if p.style.name=='Image Caption':
  for r in p.runs:r.font.size=Pt(10)
  p.paragraph_format.keep_with_next=True
 if t.startswith('Author-review revision'):
  p.alignment=WD_ALIGN_PARAGRAPH.CENTER
  for r in p.runs:r.font.size=Pt(10)
 # inline code rendering, no giant monospace hashes
 for r in p.runs:
  if r.style and r.style.name in ['Verbatim Char','Source Code']:
   r.font.name='DejaVu Sans Mono';r.font.size=Pt(8)
# All tables use fixed geometry. Width=164mm (body width).
widths={
 0:[16,91,57], # labels
 1:[34,32,32,32,34],
 2:[26,20,44,22,52],
 3:[17,37,19,22,69],
 4:[49,39,76],
 5:[60,52,52],
 6:[18,26,20,50,50],
 7:[78,43,43],
 8:[18,24,20,27,75]
}
for ti,tbl in enumerate(doc.tables):
 tbl.alignment=WD_TABLE_ALIGNMENT.CENTER;tbl.autofit=False
 ws=widths.get(ti,[164/len(tbl.columns)]*len(tbl.columns))
 for j,w in enumerate(ws):
  tbl.columns[j].width=Mm(w)
 for ri,row in enumerate(tbl.rows):
  pr=row._tr.get_or_add_trPr()
  cant=OxmlElement('w:cantSplit');pr.append(cant)
  if ri==0:

   for old in pr.findall(qn('w:tblHeader')): pr.remove(old)
   repeat=OxmlElement('w:tblHeader');pr.append(repeat)
  for j,cell in enumerate(row.cells):
   cell.width=Mm(ws[j]);cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.CENTER
   cp=cell._tc.get_or_add_tcPr()
   margins=OxmlElement('w:tcMar')
   for side,num in [('top',65),('bottom',65),('left',80),('right',80)]:
    el=OxmlElement('w:'+side);el.set(qn('w:w'),str(num));el.set(qn('w:type'),'dxa');margins.append(el)
   cp.append(margins)
   for p in cell.paragraphs:
    p.paragraph_format.space_before=Pt(0);p.paragraph_format.space_after=Pt(0);p.paragraph_format.line_spacing=1.05
    p.paragraph_format.keep_with_next=(ri<len(tbl.rows)-1)
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9.5 if ti in [0,2,3,6,8] else 10)
    if ri==0:
     for r in p.runs:r.bold=True
   if ri==0:
    sh=OxmlElement('w:shd');sh.set(qn('w:fill'),'F0F0F0');cp.append(sh)
 # Minimal horizontal rules, no heavy full grid.
 tp=tbl._tbl.tblPr
 for old in tp.findall(qn('w:tblBorders')):tp.remove(old)
 borders=OxmlElement('w:tblBorders')
 for edge in ['top','bottom','insideH','left','right','insideV']:
  el=OxmlElement('w:'+edge);el.set(qn('w:val'),'single' if edge in ['top','bottom','insideH'] else 'nil');el.set(qn('w:sz'),'5' if edge in ['top','bottom'] else '3');el.set(qn('w:color'),'777777' if edge=='insideH' else '333333');borders.append(el)
 tp.append(borders)
# Explicit language and privacy-clean document properties.
props=doc.core_properties;props.author='';props.last_modified_by='';props.title='Bid and award dispersion in European carbon auctions';props.subject='Author-review manuscript; fixed results, no new estimation';props.keywords='EUA; primary auctions; quantity dispersion; measurement';props.comments='Generated from fixed manuscript sources. Authorship and declarations require author confirmation.'
# Attach alt texts to each figure.
for i,shape in enumerate(doc.inline_shapes):
 shape._inline.docPr.set('descr', 'Figure 1: pooled residual correlation and 95 percent exploratory block intervals for A and C.' if i==0 else 'Figure 2: early and late residual correlations and 95 percent exploratory block intervals; no causal break interpretation.')
doc.save(out)
print('DOCX',out,'tables',len(doc.tables),'figures',len(doc.inline_shapes))
