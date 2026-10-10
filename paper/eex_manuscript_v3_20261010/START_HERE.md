# EEX论文v3：已构建并回读GitHub

日期：2026-10-10。最新远端写作基线：`16ab8ff415e51d69b750699f33d62f32c66e0ac4`。本版合并审阅了该提交与此前下载的v2，不覆盖两份历史稿或旧实验。

**[英文正文Word](MANUSCRIPT_EN_v3.docx)** · **[补充材料Word](ONLINE_RESOURCE_1_v3.docx)**

**[在线阅读正文](MANUSCRIPT_EN.md)** · **[在线阅读补充材料](ONLINE_RESOURCE_1.md)**

## 修订与交接

- [具体修订与编辑风险](EDITORIAL_REVIEW_ZH.md)
- [目标期刊检查](TARGET_JOURNAL_CHECK_V3.md)及[实际来源层级](SOURCE_LEDGER_V3.json)
- [待作者确认的正式提交项](AUTHOR_INFORMATION_AND_APPROVAL.md)
- [未发送投稿信草稿](COVER_LETTER_DRAFT_EN.md)
- [远端构建与下载核验记录](PUBLICATION_QA.json)

正文4张编号表、2图、4条可编辑编号公式；补充材料4表、4条编号公式。摘要200词、6关键词。所有统计结果冻结，本轮新增回归与重抽样均为0。

## 科学状态

当前稿件值得进入作者审阅，不是已经获得录用资格。重点为报告数量指标的条件共同变化和历史时期异质性，不是因果机制、潜变量识别或新的预测模型。最大的未决风险是编辑是否认为这条经验事实具有足够的增量价值。学校认可不作为研究阻断，但CAS资格和完整收费不能猜测。

输入commit：`5745eb3ddca79602346053446583d794b0e09800`。
主结果commit：`e25c1e02e1a58e0aec1084f7419066855e9565ec`。
扩展commit：`d4b26f1bbd8c1d7c036259e48e119c9c12f6c9a9`。

## 构建与发布范围

正文源提交`ee12dbcf92287395319ae507dbc9adb1cd42720a`；Word/图件构建提交`76d521e20af249727f08ba81751942b36c9a06ba`。工作流38040347923已成功，回下载的正文/公式/表格/样式/嵌入图与本地已审阅版本相同，区别仅Word核心元数据时间。主文12页、补充材料5页已逐页检查。此流程只构建文档，不执行市场实验。

`tools/build_manuscript.py`依赖pandoc、python-docx和lxml，只转换当前文本/图件。图源见`support/figure_data.json`；`tools/build_figures.py`只绘制冻结值。`tools/verify_display_lock.py`检查已审阅文本及DOCX内容结构，不冒充独立市场复算。

GitHub目录包含正文、补充、编辑说明、来源账本、构建器、图源和Word文件。会话完整ZIP另保留三份冻结结果JSON、237条数字来源账本及完整数字核验器；不声称每个历史实验大文件均重新推送。未修改main，没有提交期刊。作者最终确认前，不移除草稿声明或发送投稿信。
