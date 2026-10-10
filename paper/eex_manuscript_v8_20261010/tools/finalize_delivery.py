"""Finish v8 delivery; no document rebuild or statistical estimation.
Visual statements below record the assistant's separate local inspection.
"""
from pathlib import Path
import hashlib, json, os, zipfile
import xml.etree.ElementTree as ET
ROOT = Path(__file__).resolve().parents[1]
TITLE = 'Bid and award dispersion in European carbon auctions'
DOC_HASHES = {
 'MANUSCRIPT_EN_v8.docx':'15180678628a21a511b6f2ff49c91b1eb5bd89168129b522585ad20cc2452ee6',
 'ONLINE_RESOURCE_1_v8.docx':'0b00a762b7b1b0ddf67d3711486c248a38a4005f4274b8366ff437e8591d66fe',
 'TITLE_PAGE_v8.docx':'7daf9d090939235805a0c88a8e135872717877050eb61e6aae6db82b5000c335',
 'ESM_1.pdf':'f9e97a30e50339f1b570e64f8375febe2487238e8d2b3ba5af9f616ce455fdd5'}
OLD_MD_BLOBS = {
 'MANUSCRIPT_EN.md':'99d81e2ac7164f3f0263a3063fff261d2259c177',
 'ONLINE_RESOURCE_1.md':'18c6b519ac8db8261d534067b4228cabe905ab0c',
 'TITLE_PAGE.md':'df4dbd0df6dc1a83db650d15535c1c0efd81ff53'}
def sha256(data): return hashlib.sha256(data).hexdigest()
def git_blob(data): return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def main():
 hashes={}
 for name,expected in DOC_HASHES.items():
  data=(ROOT/name).read_bytes()
  if sha256(data)!=expected: raise ValueError('Unreviewed document: '+name)
  hashes[name]={'sha256':expected,'git_blob':git_blob(data),'bytes':len(data)}
 md_changes={}
 for name,old_blob in OLD_MD_BLOBS.items():
  path=ROOT/name;raw=path.read_bytes()
  prefix=('# Online Resource 1\n\n' if name=='ONLINE_RESOURCE_1.md' else '# '+TITLE+'\n\n').encode()
  if git_blob(raw)==old_blob: updated=prefix+raw;path.write_bytes(updated)
  elif raw.startswith(prefix) and git_blob(raw[len(prefix):])==old_blob: updated=raw
  else: raise ValueError('Unexpected Markdown; refusing broad replacement: '+name)
  md_changes[name]={'original_git_blob':old_blob,'updated_git_blob':git_blob(updated),'change':'Restore title only; following original bytes retained'}
 ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main','m':'http://schemas.openxmlformats.org/officeDocument/2006/math'}
 structural={}
 for name in ('MANUSCRIPT_EN_v8.docx','ONLINE_RESOURCE_1_v8.docx','TITLE_PAGE_v8.docx'):
  with zipfile.ZipFile(ROOT/name) as z:
   if z.testzip() is not None: raise ValueError('DOCX CRC: '+name)
   doc=ET.fromstring(z.read('word/document.xml'))
  text=''.join(t.text or '' for t in doc.findall('.//w:t',ns))
  for token in ('Zhongfei Tian','Xiang Wang','15517837680@163.com'):
   if token not in text: raise ValueError('Missing author: '+name)
  if text.index('Zhongfei Tian')>text.index('Xiang Wang'): raise ValueError('Author order')
  structural[name]={'native_math_objects':len(doc.findall('.//m:oMath',ns)),'physical_table_objects':len(doc.findall('.//w:tbl',ns)),'drawings':len(doc.findall('.//w:drawing',ns))}
 receipt={
  'date':'2026-10-10','scope':'Finish interrupted v8 editorial delivery; no new market computation',
  'reviewed_branch_head':'d4b6ba3899a653b54cc036e58debbb860f1011d1','branch':'eex-editorial-v8-20261010',
  'finish_workflow_source_commit':os.environ.get('GITHUB_SHA','local_preflight'),
  'reviewed_document_workflow_run':38063279824,'reviewed_artifact_id':11673828486,
  'reviewed_artifact_sha256':'f39edd04c6b7996632c0107e69bda8496ac089df67e5ffc2491046bb378b6bc3','reviewed_artifact_CRC_passed':True,
  'documents':hashes,'structure_checks':structural,'markdown_changes':md_changes,
  'local_object_comparison_to_v7':{'all_original_math_XML_equal':True,'all_original_table_text_and_math_preserved':True,'all_original_embedded_media_preserved':True,'whole_word_inline_subscripts_preserved':True},
  'visual_review_record':{'inspected_by':'assistant locally, separately from this script','docx_render_pages':{'main':15,'supplement':10,'title_page':1},'all_docx_render_pages_opened':True,'remote_supplement_PDF_pages':10,'all_remote_supplement_PDF_pages_opened':True,'observed_clipping_or_overlap':False,'remote_PDF_pixel_identical_to_local_reconversion':False,'Microsoft_Word_or_WPS_native_test':False},
  'abstract_words':200,'keywords':6,'main_numbered_tables':5,'main_figures':3,'SI_numbered_tables':10,
  'funding':'No financial support, user-confirmed','Wang_preceding_review':'User-confirmed; not reset to unknown',
  'new_statistical_fits':0,'new_resamples':0,'new_market_descriptive_calculations':0,
  'E2_price_regressions':0,'E2_status':'No eligible per-auction reference acquired',
  'journal_submitted':False,'main_merged':False,'CAS_qualification_certified':False,'acceptance_probability_estimated':False,'submission_ready':False,
  'open_items':['actual author contributions','competing-interest declarations','final lawful data delivery','contribution judged by target journal']}
 (ROOT/'PUBLICATION_RECEIPT.json').write_text(json.dumps(receipt,indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
 (ROOT/'DELIVERY_SCOPE.md').write_text('''# 交付范围与完成状态

此目录是v8稿件和核验材料，不是新的市场实验。下载包对应本目录；包含三份Word、期刊用补充PDF、三张图的源文件、文本稿、编辑方案、构建程序及现有汇总/核验记录。不包含原始拍卖工作簿、外部论文全文、字体或本地渲染中间图。

原始市场统计复现仍须使用REPRODUCIBILITY.md指向的固定研究提交和合法原始输入。早期数值账本和未在此目录重复保存的汇总，须从其既有固定版本取得；此包不声称将全部旧实验文件再次打包。

本轮完成了GitHub文档下载回核对、三份Word逐页本地渲染、远端PDF另行逐页检查；文档二进制不再修改。Markdown导出原先漏掉的标题已恢复，正文其余字节保留。

无资金资助、王老师已审阅前稿为用户已确认信息，不再列为未知。新修订不等于代共同作者批准正式投稿。利益冲突、实际贡献和最终数据交付安排仍待真实确认；E2价格关联未估计。

视觉检查覆盖当前LibreOffice/PDF渲染，不包含用户本机Word/WPS实测。远端补充PDF与本地重新转换PDF的像素不同，因此两者分别检查，而不宣称完全同版。
''',encoding='utf-8')
 (ROOT/'START_HERE.md').write_text('''# EEX论文v8：优化完成与GitHub回读

v7→v8为编辑修订，不重新估计。当前稿件明确区分指标水平、条件关联、构成敏感性和2026年短时间轴证据。写作基线固定为35d8c63fc57173f67eb0bd8bb570eb289188324f。

## 稿件

- [英文正文Word](MANUSCRIPT_EN_v8.docx) / [在线正文](MANUSCRIPT_EN.md)
- [补充材料Word](ONLINE_RESOURCE_1_v8.docx) / [期刊用补充PDF](ESM_1.pdf)
- [独立题名页](TITLE_PAGE_v8.docx)
- [编辑审查与修改](EDITORIAL_REVIEW_ZH.md)
- [期刊要求检查](JOURNAL_CHECK_V8.md)
- [实际发布与回读收据](PUBLICATION_RECEIPT.json)
- [交付范围](DELIVERY_SCOPE.md) / [统计复现定位](REPRODUCIBILITY.md)

## 改动与证据边界

改写摘要与引言，明确加权残差相关的估计对象；新增SI表S10，将原主要Δβ97.5%、次要Δθ95%、加权Δθ97.5%、新时间诊断和未估计价格关系分开。原表图、系数、区间、公式和late/early整词下标保持。2026只支持短时间描述，不是冻结模型预测；E2缺数据不代表价格无效。

正文15页、3图、5张编号表；补充10页、10张编号表；独立题名页1页。主文与补充的原数学对象和表格数字已对v7核对，三份Word与已回下载的GitHub文件SHA-256相同。正文、补充、题名页逐页渲染核查，远端SI PDF另外检查10页。没有Microsoft Word/WPS本机实测，不作所有阅读器兼容保证。

## 作者与状态

田中斐 / Zhongfei Tian：第一及通讯作者；王翔 / Xiang Wang：第二作者。单位Zhengzhou University of Aeronautics；通讯15517837680@163.com。无资金资助、王老师已审阅前稿，均保留为用户已确认信息。

实际贡献、利益冲突及最终数据交付安排尚需如实填写。工作期刊为Empirical Economics；格式检查不认证CAS资格、全部费用、创新或中稿率。没有发送邮件、提交期刊或合并main。

下载包只包含此稿件目录，不重复发布原始拍卖数据或字体；更早冻结数值文件按REPRODUCIBILITY.md取用。本轮另修复在线Markdown导出漏题名的问题，未重新生成或改变已经检查的DOCX/PDF。
''',encoding='utf-8')
 for name,expected in DOC_HASHES.items():
  if sha256((ROOT/name).read_bytes())!=expected: raise ValueError('Reviewed document changed')
 print(json.dumps({'status':'passed','documents_unchanged':True,'new_fits':0,'markdown_titles_restored':list(md_changes)},ensure_ascii=False))
if __name__=='__main__': main()
