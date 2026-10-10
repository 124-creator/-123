# v6.1 公式显示修复与作者确认更新

本版修复用户截图指出的行内Δβ、Δθ公式下标字母竖排/错位问题。旧v6文件保留，本文档目录为修正版入口。

- [修正后的正文Word](MANUSCRIPT_EN_v6.docx)
- [修正后的题名页](TITLE_PAGE_v6.docx)
- [修正后的补充Word](ONLINE_RESOURCE_1_v6.docx)
- [补充材料PDF](ESM_1.pdf)
- [修复和字段状态记录](support/REPAIR_RECEIPT.json)

## 事实更新

用户已明确：本研究没有资金资助；王翔老师已经审阅。资助声明现在为“The authors received no financial support for this research.”，不再要求重复确认这两项。作者排序和通讯邮箱不变。没有据此代填利益冲突或其他尚未提供的贡献细节，也没有把已审阅扩张成授权本工具发送投稿。

## 实际问题与处理

原Word在相关下标中分别存放l/a/t/e与e/a/r/l/y等逐字母OfficeMath片段。用户截图显示竖排。本轮用同一原件做LibreOffice本地转换时未复现竖排，故不能证明具体是哪个软件版本导致，也不能把先前渲染通过当成跨软件保证。旧“没有公式问题”的宽泛结论撤回。

两处简单行内公式改为普通Word可编辑数学符号+整词下标，每个late/early是一个文本对象，不再经过逐字母OfficeMath布局；公式(4)中的partial标签合并为一个正体文本标签。全部8条编号公式仍保留原生OfficeMath。其余公式结构、数值、表格、嵌入图、参考文献和样式保留。

修复前后对照了全部111个OfficeMath对象的上下标结构，并核对数学文本序列一致。两处行内表达转换为可编辑文本后，正文剩51个OfficeMath对象、SI58个；对象数量减少不代表删除公式。声明单独更新。

本地重新渲染并查看13页正文、7页SI、1页题名页。该检查仅覆盖LibreOffice输出；没有用户本机Word/WPS版本的实机验证，不作所有阅读器绝对兼容保证。此轮无新估计、重抽样、描述统计或期刊科学资格判定。

## 复建方法

从本分支根目录运行：

```bash
python paper/eex_formula_fix_20261010/tools/repair_v6.py --source paper/eex_manuscript_v6_20261010 --out paper/eex_formula_fix_20261010
```

脚本严格核对原v6的三个DOCX SHA-256，直接修复OOXML，并同步声明到Markdown。不要仅用旧Pandoc构建器重新生成交付，否则会重新引入逐字母标签。需要重新排版整篇时，应保留本次下标规范化和行内公式处理，并重新做视觉检查。

旧v6目录的资金/审阅待确认状态仅代表历史状态，本次用户确认覆盖这些旧状态；原实验结论不变。原件及所有冻结实验输出均未修改。
