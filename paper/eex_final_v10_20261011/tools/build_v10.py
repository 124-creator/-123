"""Build an editorial v10 from exact v9 DOCX objects and frozen public aggregates.
No raw price data, statistical fitting, network requests or model deserialization.
"""
from __future__ import annotations
import argparse, copy, csv, hashlib, json, re, shutil
from pathlib import Path
from collections import Counter
from lxml import etree
from docx import Document
from docx.shared import Pt, Inches, Mm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.style import WD_STYLE_TYPE
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.text.paragraph import Paragraph
from docx.table import Table
from docx.opc.constants import RELATIONSHIP_TYPE as RT

NS={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math','wp':'http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing'}
def xp(el,s):return etree.XPath(s,namespaces=NS)(el)
def rawtext(el):return ''.join(t.text or '' for t in xp(el,'.//w:t|.//m:t'))
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def mathstrings(doc):return [rawtext(e) for e in xp(doc.element,'.//m:oMath')]
def table_strings(doc):return [[rawtext(c) for c in xp(e,'.//w:tr/w:tc')] for e in xp(doc.element.body,'./w:tbl')]
TABLE_MAP={'3':'4','4':'6','5':'7','6':'5'}
def reftxt(s):
 s=re.sub(r'\bTable ([3456])(?!\d)',lambda m:'Table '+TABLE_MAP[m.group(1)],s)
 s=s.replace('Section 3.7','Section 4.2').replace('Section 3.4','Section 4.4')
 s=s.replace('Table 6 page locators','Table 4 page locators').replace('relevant Table 6 explanatory text','relevant Table 4 explanatory text')
 return s

def add_link(p,label,url):
 h=OxmlElement('w:hyperlink');h.set(qn('r:id'),p.part.relate_to(url,RT.HYPERLINK,is_external=True))
 r=OxmlElement('w:r');pr=OxmlElement('w:rPr');c=OxmlElement('w:color');c.set(qn('w:val'),'000000');pr.append(c)
 u=OxmlElement('w:u');u.set(qn('w:val'),'single');pr.append(u);r.append(pr);t=OxmlElement('w:t');t.text=label;r.append(t);h.append(r);p._p.append(h)

def create_p(doc,text,style='BodyText'):
 if style not in doc.styles:doc.styles.add_style(style,WD_STYLE_TYPE.PARAGRAPH)
 p=doc.add_paragraph(style=style);p.add_run(text);el=p._p;el.getparent().remove(el);return el

def create_pic(doc,path,descr):
 p=doc.add_paragraph();p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 r=p.add_run();sh=r.add_picture(str(path),width=Inches(6.4));sh._inline.docPr.set('descr',descr)
 p.paragraph_format.keep_with_next=True
 e=p._p;e.getparent().remove(e);return e

def set_text(el,text):
 # Only used on prose without math or drawings.
 if xp(el,'.//m:oMath|.//w:drawing'):raise ValueError('Refusing to flatten protected equation/image')
 ppr=el.find(qn('w:pPr'))
 for c in list(el):
  if c is not ppr:el.remove(c)
 r=OxmlElement('w:r');t=OxmlElement('w:t');t.set(qn('xml:space'),'preserve');t.text=text;r.append(t);el.append(r)

def math_style(doc):
 for r in xp(doc.element,'.//m:r'):
  ts=xp(r,'./m:t');s=''.join(t.text or '' for t in ts)
  if s not in {'Z','M','z','γ','λ','c','x','y'}:continue
  isvector=s in {'Z','M','z','γ','λ','c'}
  if s=='M':
   subs=[a for a in r.iterancestors() if a.tag in {qn('m:sSub'),qn('m:sSubSup')}]
   isvector=any('Z' in rawtext(a.find(qn('m:sub'))) for a in subs if a.find(qn('m:sub')) is not None)
  constructed_c = s=='c' and any(a.tag==qn('m:sup') for a in r.iterancestors())
  if constructed_c:isvector=False
  if s in {'x','y'}:
   subs=[e for e in r.iterancestors() if e.tag in {qn('m:sSub'),qn('m:sSubSup')}]
   # Indexed observations remain scalar; unindexed x/y in projection equations are vectors.
   indexed=any('t' in rawtext(e.find(qn('m:sub'))) for e in subs if e.find(qn('m:sub')) is not None)
   isvector=not indexed
  pr=r.find(qn('m:rPr'))
  if pr is None:pr=OxmlElement('m:rPr');r.insert(0,pr)
  for tag in ('m:sty','m:nor'):
   e=pr.find(qn(tag))
   if e is not None:pr.remove(e)
  sty=OxmlElement('m:sty');sty.set(qn('m:val'),'p' if constructed_c else ('b' if isvector else 'i'));pr.append(sty)

def style_inline_math(doc):
 # Single-letter mathematical tokens only. Preserve existing run properties and line breaks.
 pat=re.compile(r'(?<![A-Za-z0-9_])(?:[dxYκβθGnp]|c)(?![A-Za-z0-9_])|R(?=²)')
 for r in list(xp(doc.element.body,'.//w:r')):
  if any(a.tag.startswith('{'+NS['m']+'}') for a in r.iterancestors()):continue
  children=[e for e in r if e.tag!=qn('w:rPr')]
  if len(children)!=1 or children[0].tag!=qn('w:t'):continue
  ps=[a for a in r.iterancestors() if a.tag==qn('w:p')]
  if ps and Paragraph(ps[0],doc).style.name=='Reference':continue
  text=children[0].text or '';matches=list(pat.finditer(text))
  if not matches:continue
  pos=0;pieces=[]
  for m in matches:
   if m.start()>pos:pieces.append((text[pos:m.start()],False))
   pieces.append((m.group(),True));pos=m.end()
  if pos<len(text):pieces.append((text[pos:],False))
  parent=r.getparent();ix=parent.index(r)
  for txt,is_math in pieces:
   nr=copy.deepcopy(r);nt=nr.find(qn('w:t'));nt.text=txt;nt.set(qn('xml:space'),'preserve')
   if is_math:
    pr=nr.find(qn('w:rPr'))
    if pr is None:pr=OxmlElement('w:rPr');nr.insert(0,pr)
    for tag in ('w:i','w:iCs'):
     e=pr.find(qn(tag))
     if e is None:e=OxmlElement(tag);pr.append(e)
     e.set(qn('w:val'),'1')
    if txt=='c' and not any('superscript c' in rawtext(p) for p in ps):
     e=pr.find(qn('w:b'))
     if e is None:e=OxmlElement('w:b');pr.append(e)
     e.set(qn('w:val'),'1')
   parent.insert(ix,nr);ix+=1
  parent.remove(r)

def normalize(doc,kind):
 for name in ['BodyText','FirstParagraph','Caption','TableNote','FigureCaption','Reference']:
  if name not in doc.styles:doc.styles.add_style(name,WD_STYLE_TYPE.PARAGRAPH)
  st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(11.5);st.font.color.rgb=RGBColor(0,0,0)
  st.paragraph_format.space_after=Pt(6);st.paragraph_format.line_spacing=1.12
  st.paragraph_format.first_line_indent=Pt(0);st.paragraph_format.widow_control=True
 for name in ['Caption','FigureCaption']:
  doc.styles[name].font.size=Pt(10);doc.styles[name].paragraph_format.line_spacing=1.03
  doc.styles[name].paragraph_format.space_before=Pt(7);doc.styles[name].paragraph_format.space_after=Pt(4)
 for name in ['TableNote','Reference']:
  doc.styles[name].font.size=Pt(9.5 if name=='TableNote' else 10.5)
  doc.styles[name].paragraph_format.line_spacing=1.05
 for name,size in [('Heading1',12.5),('Heading2',11.5)]:
  st=doc.styles[name];st.font.name='Times New Roman';st.font.size=Pt(size);st.font.bold=True;st.font.color.rgb=RGBColor(0,0,0)
  st.paragraph_format.space_before=Pt(12);st.paragraph_format.space_after=Pt(5);st.paragraph_format.keep_with_next=True
  st.paragraph_format.page_break_before=False
 for sec in doc.sections:
  sec.page_width=Mm(210);sec.page_height=Mm(297);sec.top_margin=Mm(22);sec.bottom_margin=Mm(22);sec.left_margin=Mm(24);sec.right_margin=Mm(24)
  sec.header_distance=Mm(10);sec.footer_distance=Mm(11)
  for p in sec.header.paragraphs:
   p.text=('Quantity dispersion and reported price deviations' if kind=='main' else ('Online Resource 1' if kind=='si' else ''))
   p.alignment=WD_ALIGN_PARAGRAPH.RIGHT
   for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(8.5);r.font.color.rgb=RGBColor(0,0,0)
  for p in sec.footer.paragraphs:
   for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9)
 for p in doc.paragraphs:
  s=p.text;pr=p.paragraph_format
  pr.first_line_indent=Pt(0);pr.widow_control=True
  # Remove inherited page forcing; reapply only a controlled title-page boundary.
  pr.page_break_before=False
  if kind=='si' and (re.match(r'^S\d+ ',s) or s=='Additional references'):p.style='Heading1'
  if p.style.name not in ['Title','Subtitle','Heading 1','Heading 2']:
   if re.match(r'^Table S?\d+ (?:\(continued\) |[A-Z])',s):p.style='Caption';pr.keep_with_next=True
   elif re.match(r'^Fig\. S?\d+',s):p.style='FigureCaption';pr.keep_with_next=False
   elif s.startswith('Note:'):p.style='TableNote';pr.keep_with_next=False
   elif s.startswith('Panel '):p.style='Caption';pr.keep_with_next=True
   elif p.style.name not in ['Reference']:p.style='BodyText'
  for r in p.runs:
   r.font.name='Times New Roman';r.font.color.rgb=RGBColor(0,0,0)
   if p.style.name in ['BodyText','Body Text','FirstParagraph','First Paragraph']:r.font.size=Pt(11.5)
   elif p.style.name=='TableNote':r.font.size=Pt(9.5)
   elif p.style.name in ['Caption','FigureCaption']:r.font.size=Pt(10)
   elif p.style.name=='Reference':r.font.size=Pt(10.5)
  if p.style.name=='Caption':
   for r in p.runs:r.bold=True
  if p.style.name=='FigureCaption':
   # Preserve exact caption text, bold Fig. and numeral only.
   m=re.match(r'^(Fig\. S?\d+)\s+(.*)$',s)
   if m:
    p.clear();r=p.add_run(m.group(1));r.bold=True;p.add_run(' '+m.group(2).rstrip('.'))
    for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(10)
  if xp(p._p,'.//w:drawing'):pr.keep_with_next=True
  if xp(p._p,'.//m:oMathPara'):pr.keep_together=True
 for table in doc.tables:
  table.autofit=False
  for row in table.rows:
   trpr=row._tr.get_or_add_trPr();cs=trpr.find(qn('w:cantSplit'))
   if cs is None:trpr.append(OxmlElement('w:cantSplit'))
   for cell in row.cells:
    for p in cell.paragraphs:
     p.paragraph_format.space_after=Pt(3);p.paragraph_format.space_before=Pt(3);p.paragraph_format.line_spacing=1.03
     p.paragraph_format.keep_with_next=False;p.paragraph_format.keep_together=True
     for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(9.5);r.font.color.rgb=RGBColor(0,0,0)
  hp=table.rows[0]._tr.get_or_add_trPr()
  if hp.find(qn('w:tblHeader')) is None:hp.append(OxmlElement('w:tblHeader'))
  for c in table.rows[0].cells:
   for p in c.paragraphs:
    for r in p.runs:r.bold=True
 # Keep each numbered table with its panels and explanatory note, when the group fits on one page.
 active=False
 for el in doc.element.body:
  if el.tag==qn('w:p'):
   pp=Paragraph(el,doc);txt=pp.text
   if pp.style.name=='Caption' and re.match(r'^Table S?\d+ ',txt):active=True
   if active:
    if pp.style.name in {'Heading 1','Heading 2'}:active=False
    else:pp.paragraph_format.keep_with_next=not txt.startswith('Note:')
    if txt.startswith('Note:'):active=False
  elif el.tag==qn('w:tbl') and active:
   for pp_el in xp(el,'.//w:p'):Paragraph(pp_el,doc).paragraph_format.keep_with_next=True
 # Direct typography of the first title block.
 for i,p in enumerate(doc.paragraphs[:7]):
  if i==0:
   p.style='Title';p.paragraph_format.space_before=Pt(10);p.paragraph_format.space_after=Pt(7)
   for r in p.runs:r.font.name='Times New Roman';r.font.size=Pt(16);r.bold=True
  if i in range(0,5) and p.style.name not in {'Heading 1','Heading 2'}:p.alignment=WD_ALIGN_PARAGRAPH.CENTER
 for p in doc.paragraphs:
  if p.style.name in {'Heading 1','Heading 2'}:p.alignment=WD_ALIGN_PARAGRAPH.LEFT
 if kind=='main':
  for p in doc.paragraphs:
   if p.text=='1 Introduction':p.paragraph_format.page_break_before=True
 math_style(doc);style_inline_math(doc)
 # Remove old manuscript bookmarks; no REF fields depend on these exported anchors.
 for e in xp(doc.element.body,'.//w:bookmarkStart|.//w:bookmarkEnd'):e.getparent().remove(e)
 doc.core_properties.author='Zhongfei Tian; Xiang Wang';doc.core_properties.last_modified_by='Zhongfei Tian'
 doc.core_properties.title='Quantity dispersion and reported price deviations in European carbon auctions'
 doc.core_properties.subject='Empirical Economics submission manuscript';doc.core_properties.comments=''


def main(source,out):
 out.mkdir(parents=True,exist_ok=True);plan=json.loads((out/'REVISION_PLAN.json').read_text());P=plan['paragraphs']
 expected={'MANUSCRIPT_EN_v9.docx':'ce6b68f22d88454d35a534a99b0b1561d0207a550dc31666f0f37e00c424e789','ONLINE_RESOURCE_1_v9.docx':'7e6de1b5e9045d3f0343c323f6e34ffb7209d0dc8fd9d9e64fcff22598a82830','TITLE_PAGE_v9.docx':'97a79285d4f88287f5e04e2fa88442e15372b1e89b9b88ef146e26b7561a0527'}
 for f,h in expected.items():
  if sha(source/f)!=h:raise ValueError('Unexpected v9 DOCX: '+f)
 doc=Document(source/'MANUSCRIPT_EN_v9.docx');orig_math=mathstrings(doc);orig_tables=table_strings(doc)
 old=list(doc.element.body);sect=copy.deepcopy(old[-1]);new=[]
 for step in plan['main_sequence']:
  if 'source' in step:
   el=copy.deepcopy(old[step['source']])
   for t in xp(el,'.//w:t'):t.text=reftxt(t.text or '')
   if step['source']==32:
    set_text(el,rawtext(el).replace('Otsubo (2026) studies intraday futures–ETF price discovery and a daily auction–futures–ETF comparison aligned to 16:00 UK time.', 'Otsubo (2026) studies intraday price discovery between futures and an exchange-traded fund (ETF), together with a daily auction–futures–ETF comparison aligned to 16:00 UK time.'))
   if step['source']==33:
    set_text(el,rawtext(el).replace('ESMA (2025)','ESMA (2025)'))
   if step['source']==96:set_text(el,rawtext(el).replace('quarter-clustered CR1 covariance','a finite-sample-corrected quarter-cluster covariance estimator (CR1)'))
   if step['source']==141:set_text(el,rawtext(el).replace('KS is the maximum empirical cumulative-distribution distance','KS denotes the Kolmogorov–Smirnov distance, the maximum difference between empirical cumulative distributions'))
   if step['source']==110:set_text(el,rawtext(el).replace('(Fig. 2)','(Online Resource 1, Fig. S1)'))
   new.append(el)
  elif 'heading' in step:new.append(create_p(doc,step['heading'],'Heading'+str(step['level'])))
  elif 'figure' in step:new.append(create_pic(doc,out/'figures'/step['figure'],'Observed-interquartile price contrasts with CR1-t intervals; absolute outcome is separated from signed outcomes.'))
  else:new.append(create_p(doc,P[step['text_key']] if 'text_key' in step else step['text'],step.get('style','BodyText')))
 for el in list(doc.element.body):doc.element.body.remove(el)
 for el in new:doc.element.body.append(el)
 doc.element.body.append(sect)
 # References have their own semantic style, not arbitrary source first-paragraph styling.
 inref=False
 for p in doc.paragraphs:
  if p.text=='References':inref=True;continue
  if inref:p.style='Reference'
 normalize(doc,'main')
 if Counter(mathstrings(doc))!=Counter(orig_math):raise ValueError('Mathematical text changed or original formula lost')
 if Counter(tuple(x) for x in table_strings(doc))!=Counter(tuple(x) for x in orig_tables):raise ValueError('Original numerical table cells changed')
 doc.save(out/'MANUSCRIPT_EN_v10.docx')
 # Supplement: retained scientific objects; remove editorial-review voice and update references.
 si=Document(source/'ONLINE_RESOURCE_1_v9.docx');si_orig_math=mathstrings(si)
 for el in si.element.body:
  for t in xp(el,'.//w:t'):t.text=reftxt(t.text or '').replace('Version: Integrated author-review v9, 11 October 2026','Version: 11 October 2026').replace(' (intended submission; not yet submitted)','').replace('they have not been re-estimated for v9.','they have not been re-estimated in this manuscript.')
 replacements={
 'S8 Descriptive context and direct correlation contrasts added to the presentation':'S8 Historical descriptions and direct correlation contrasts',
 'The first path contains the raw-workbook identifiers': 'The first path contains the raw-workbook identifiers, complete extraction, candidate sample, exclusions and cell traces. The other paths contain the analysis code, protocols, result summaries and computational records. Reproduction starts from the fixed input and rebuilds the eligibility rules rather than filtering until a particular sample size is reached. Source acquisition and redistribution remain subject to provider rights; the access route is described in Section S18.',
 'Version: Integrated author-review v9, 11 October 2026':'Version: 11 October 2026',
 'This resource keeps the historical quantity evidence': 'This resource documents the separate quantity and price analyses and their limits. Sections S1–S11 retain the historical quantity evidence and subsequent sensitivity checks. Sections S12–S17 cover the matched German price analysis, including sources, descriptions and uncertainty. Section S18 provides the data-access route. All numerical estimates are preserved from the versioned analyses; the present reorganization changes no model or sample.',
 'The numerical reimplementations use the same archives': 'The numerical reimplementations use the same archives and are not independent-market replications. Fitting counts record computation rather than observations. The study received no financial support. Zhongfei Tian coordinated manuscript preparation and the final revision. Xiang Wang reviewed and checked the manuscript, approved its scientific content, and authorized completion of the final editorial revision. All inferential limitations remain part of the published analysis.',
 'S9 Conditioning-set values accompanying Figure 2':'S9 Conditioning-set values and supplementary Figure S1',
 'The table and Figure 2 use the same frozen values.':'Table S6 and Figure S1 display the same estimates; their agreement is not an additional result. The full-control row reproduces the principal quantity estimate. Main Figure 1 shows quartile ranges, main Figure 2 shows price-model CR1-t intervals, and main Figure 3 shows the secondary historical correlation contrast. These statistical objects are not interchangeable.',
 'The earlier display ledgers remain available':'The numerical source ledger and aggregate audit are provided with the versioned manuscript package. They link displayed price values to fixed results and stored test statistics. The underlying source-input checks and estimation code are documented separately; an editorial ledger does not replace access to event-level inputs.',
 'The team reports 1,034 original estimation requests':'The price analysis used 1,034 estimation requests: eight baseline/extension fits, 999 restricted bootstrap fits, 21 quarter deletions and six year deletions. Four fixed extended models were also checked with a separate numerical implementation, which agreed on the focal coefficient, CR1 standard error and partial R². The recorded 26 artificial tests in each Python mode assess implementation behaviour rather than empirical validity. The 55 frozen source objects were unchanged. Public aggregate checks reproduce arithmetic from the outputs, but independent event-level refitting still requires the input rows.',
 'Note: Page numbers reproduce the targeted local definition record':'Note: Page numbers identify the methods-text locations in the fixed source record. Online Resource 2 and the machine-readable SOURCE_DEFINITION_CHECK.json give exact source URLs and SHA-256 values. Three quarters contribute no eligible reference observations; one additional source-date conflict is excluded in 2025Q1. The reports and event-level panels are not redistributed with this resource. These locators do not authenticate native tick data, quote age or a complete UTC deadline history.',
 'Data-access statement: the historical EEX quantity input':'Source identities and reporting coverage are listed in Online Resource 2. Section S18 gives the public and conditional-access routes; neither the catalogue nor a file hash grants permission to redistribute third-party material.',
 }
 for p in si.paragraphs:
  if xp(p._p,'.//m:oMath|.//w:drawing'):continue
  for start,value in replacements.items():
   if p.text.startswith(start):set_text(p._p,value);break
 # Source-object scope now distinguishes old figure numbering explicitly.
 for p in si.paragraphs:
  if p.text.startswith('The source file for prices contains'):
   set_text(p._p,p.text+' These are contemporaneous reported fields; the conditional comparison is not a pre-auction forecast.')
 # Insert the former main conditioning figure next to its numerical table, with an actual new SI image relationship.
 target=next(p for p in si.paragraphs if p.text.startswith('Table S6 and Figure S1'))
 pic=create_pic(si,out/'figures/FigS1.png','Residual quantity correlations under three control sets; frozen block intervals.')
 cap=create_p(si,'Fig. S1 Residual quantity correlations across conditioning sets; row labels identify the transformations. Bars are exploratory 95% three-month block intervals from Table S6. FE denotes reporting-series and year–month fixed effects; full controls add demand coverage and successful bidders to volume and total bidders. The full-control rows repeat the principal estimates','FigureCaption')
 target._p.addnext(pic);pic.addnext(cap)
 # Operational access section before additional references, using clickable named links.
 ar=next(p for p in si.paragraphs if p.text=='Additional references')
 access=[]
 access.append(create_p(si,'S18 Data and code access','Heading2'))
 access.append(create_p(si,P['si_access']))
 links=[('Historical quantity inputs (fixed snapshot)', '5745eb3ddca79602346053446583d794b0e09800','research/pro_review_20261010/full_data/README.md'),('German price model, protocol and aggregate results','fccd471de96548bd781c59aced4a59435aae08ac','research/eua_local_price_execution_20261011/START_HERE_ZH.txt'),('German price descriptions and source definitions','33707c164c80accd7acf9fcd3f0965088a8370f6','research/eua_price_description_followup_20261011/START_HERE_ZH.txt'),('Historical quantity and extension reproduction map','35f6b780561907b4914e61e68b0962645ace8e71','paper/eex_price_integrated_v9_20261011/REPRODUCIBILITY.md')]
 for label,rev,path in links:
  p=si.add_paragraph();add_link(p,label,'https://github.com/124-creator/-123/blob/'+rev+'/'+path);el=p._p;el.getparent().remove(el);access.append(el)
 access.append(create_p(si,'Online Resource 2 (ESM_2.csv) lists the official report quarter, source URL, definition-page locator, eligibility count and file hash, with article and corresponding-author metadata. It contains no event-level price rows. The unit of the price input is numeric percentage points; the analysis converts this field to basis points without reconstructing native reference prices.'))
 for el in access:ar._p.addprevious(el)
 normalize(si,'si')
 # Guarantee the long source catalogue has intelligible continued-page titles.
 for p in si.paragraphs:
  if p.text.startswith('Table S14 '):p.paragraph_format.page_break_before=True
 if Counter(mathstrings(si))!=Counter(si_orig_math):raise ValueError('Supplement mathematical text changed')
 si.save(out/'ONLINE_RESOURCE_1_v10.docx')
 # Standalone title page, with only information supplied or explicitly confirmed.
 title=Document(source/'TITLE_PAGE_v9.docx')
 root=title.element.body;sec=copy.deepcopy(root[-1])
 for e in list(root):root.remove(e)
 title_seq=[('Quantity dispersion and reported price deviations in European carbon auctions','Title'),('Conditional associations and historical scope','BodyText'),('Zhongfei Tian · Xiang Wang','BodyText'),('Zhengzhou University of Aeronautics, Zhengzhou, Henan, China','BodyText'),('Corresponding author: Zhongfei Tian\nE-mail: 15517837680@163.com','BodyText'),('Article type: Research article\nTarget journal: Empirical Economics','BodyText'),('Funding','Heading1'),(P['funding'],'BodyText'),('Author contributions','Heading1'),(P['contributions'],'BodyText'),('Competing interests','Heading1'),(P['interests'],'BodyText')]
 for text,style in title_seq:root.append(create_p(title,text,style))
 root.append(sec);normalize(title,'title');title.save(out/'TITLE_PAGE_v10.docx')
 # Preserve frozen evidence. No unlicensed raw material is introduced.
 for f in ['PRICE_RESULTS.json','PRICE_DESCRIPTIVES.json','FULL24_SOURCE_INDEX.json','SOURCE_DEFINITION_CHECK.json','AGGREGATE_AUDIT.json']:
  shutil.copy2(source/'support'/f,out/'support'/f)
 cat=json.loads((source/'support/FULL24_SOURCE_INDEX.json').read_text())['reports'];defs=json.loads((source/'support/SOURCE_DEFINITION_CHECK.json').read_text())['sources'];byhash={r['sha256']:r for r in defs}
 with (out/'ESM_2.csv').open('w',newline='',encoding='utf-8-sig') as f:
  columns=['article_title','journal','authors','affiliation','corresponding_email','quarter','source_url','definition_page_1based','reported_auctions','eligible_auctions','sha256','scope']
  w=csv.DictWriter(f,fieldnames=columns);w.writeheader()
  for r in cat:
   de=byhash[r['sha256']]
   w.writerow(dict(article_title=title_seq[0][0],journal='Empirical Economics',authors='Zhongfei Tian; Xiang Wang',affiliation='Zhengzhou University of Aeronautics, Zhengzhou, Henan, China',corresponding_email='15517837680@163.com',quarter=r['quarter_id'],source_url=r['source_url'],definition_page_1based=de['page_1based'],reported_auctions=r['event_rows'],eligible_auctions=r['strict_reference_date_rows'],sha256=r['sha256'],scope='Official reported comparison; no native quote or redistribution permission certification'))
 # Machine-readable content and QA inventory. Word is the source of editable mathematics.
 def export(d,path):
  outtext=[];tokens=[]
  for el in d.element.body:
   if el.tag==qn('w:p'):
    s=rawtext(el)
    if not s:continue
    p=Paragraph(el,d);sty=p.style.name
    prefix='# ' if sty=='Title' else '## ' if sty=='Heading 1' else '### ' if sty=='Heading 2' else ''
    # Export native equations through the exact readable linear OMML text, not an alternate build path.
    if xp(el,'.//m:oMathPara'):s='[Editable equation in DOCX] '+s
    outtext.append(prefix+s)
   elif el.tag==qn('w:tbl'):
    t=Table(el,d);grid=[[rawtext(c._tc).replace('|','/').replace('\n',' ') for c in row.cells] for row in t.rows]
    outtext.append('\n'.join(['| '+' | '.join(row)+' |' for row in grid[:1]]+['| '+' | '.join(['---']*len(grid[0]))+' |']+['| '+' | '.join(row)+' |' for row in grid[1:]]))
  path.write_text('\n\n'.join(outtext),encoding='utf-8')
 export(doc,out/'MANUSCRIPT_EN.md');export(si,out/'ONLINE_RESOURCE_1.md');export(title,out/'TITLE_PAGE.md')
 def words(d):
  text=' '.join(rawtext(e) for e in d.element.body if e.tag==qn('w:p'))
  return len(re.findall(r"\b[\w]+(?:[’'–-][\w]+)*\b",text))
 audit={'scope':'Editorial build, not statistical refit','date':'2026-10-11','source_sha256':expected,'original_math_objects_main':len(orig_math),'math_objects_main':len(mathstrings(doc)),'math_text_preserved':Counter(mathstrings(doc))==Counter(orig_math),'original_numerical_tables_all_cells_preserved':True,'SI_math_objects':len(mathstrings(si)),'SI_math_text_preserved':True,'main_figures':len(doc.inline_shapes),'SI_figures':len(si.inline_shapes),'main_physical_tables':len(doc.tables),'SI_physical_tables':len(si.tables),'main_numbered_tables':7,'SI_numbered_tables':14,'abstract_words':len(P['abstract'].split()),'main_paragraph_words_including_references':words(doc),'main_v9_paragraph_words_including_references':words(Document(source/'MANUSCRIPT_EN_v9.docx')),'SI_paragraph_words':words(si),'new_market_fits':0,'new_resampling_fits':0,'new_private_row_statistics':0,'visual_review':'pending','nonfinancial_interests_not_inferred':True,'data_redistribution_permission_not_inferred':True,'native_Word_WPS_test':False}
 (out/'support/BUILD_QA.json').write_text(json.dumps(audit,indent=2))
 print(json.dumps(audit,indent=2))

if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--source',type=Path,required=True);a.add_argument('--out',type=Path,required=True);args=a.parse_args();main(args.source,args.out)
